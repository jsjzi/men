# mem.py — 树状双层记忆系统

一个零依赖、纯 Python 标准库实现的个人记忆系统：把每次对话提炼成结构化摘要，按时间和内容双重索引，需要时一句话召回。设计理念来自对 Hermes Agent、DSH（DeepSeek Harness）、豆包长期记忆的对比研究。

## 特性

- **三层结构**：常驻层（MEMORY.md，≤2200 字符，会话开始注入）＋ 存档层（notes/年/月 时间树）＋ 检索层（SQLite FTS5 trigram 中文全文搜索）
- **双通道检索**：语义向量（bge-small-zh 512 维，换种说法也能搜到）＋ FTS5 关键词，先摘要层后全文层；Top-K 注入，单次 ≤2k token
- **零 token 存储与检索**：只有注入才花钱，与记忆总量无关
- **删除安全网**：软删除进回收站可恢复，段落级编辑删除
- **原子写入**：临时文件 + 改名，写一半崩溃不损坏
- **月度聚合**：rollup 自动生成月度摘要，防摘要过期
- **全局记忆库**：默认 $DSH_HOME/memories，跨所有工作区共享

## 安装（自动适配任何用户，零硬编码）

```bash
# 1. 克隆本项目
git clone <你的仓库地址> && cd mem-py

# 2. 一键安装：自动检测 $DSH_HOME，把技能装好（路径自动适配本机）
python install.py

# 3. 初始化记忆库（默认 $DSH_HOME/memories；可用 MEMORY_HOME 覆盖）
python mem.py init
```

`install.py` 会渲染 `SKILL.md.tpl` 模板中的 `{{MEM_PY}}`/`{{MEMORY_HOME}}` 为你的真实路径，写入 `$DSH_HOME/skills/memory/SKILL.md`——任何机器克隆后跑一次即用，不需要改任何代码。

**可选：语义检索**（换种说法也能搜到，如「不爱吃辣」→「饮食偏好」）：

```bash
pip install fastembed   # 首次会联网下载 bge-small-zh 模型（约 100MB），之后离线
```

未安装 fastembed 时自动退回纯关键词检索（零依赖底线不变）。

要求：Python 3.10+（SQLite 自带 FTS5 trigram 分词）。

## 用法

```bash
python mem.py add "标题" -t "标签1,标签2" -s "结论:..; 决定:..; 待办:.." --content "正文"  # 记录对话
python mem.py search "关键词" -k 3          # 两阶段检索（摘要层→全文层）
python mem.py inject "关键词" -k 3          # 生成可直接注入上下文的 Top-K 块
python mem.py get "notes/YYYY/MM/DD-标题.md" # 读取完整记忆
python mem.py list [YYYY-MM]                # 按时间列出
python mem.py mem add "高频事实"             # 写常驻层 MEMORY.md
python mem.py rm "路径"                      # 软删除（回收站可恢复）
python mem.py rm "路径" --hard              # 永久删除
python mem.py trash / restore <文件名>      # 回收站管理
python mem.py index                         # 手工改文件后重建索引
python mem.py rollup [YYYY-MM]              # 月度聚合
```

## 存储结构

```
memories/
├── MEMORY.md          # 常驻层：高频事实（≤2200 字符）
├── index.sqlite       # 检索层：SQLite FTS5（trigram 中文分词）
├── notes/             # 存档层：时间树
│   ├── 2026/
│   │   └── 08/
│   │       ├── 15-对话标题.md   # frontmatter 含 date/title/tags/summary
│   │       └── _index.md        # 自动生成的月度索引
│   └── rollup/
│       └── 2026-08.md           # 月度聚合
└── .trash/            # 软删除回收站
```

## 设计哲学

- **记忆是检索系统，不是上下文转储系统**：存储和检索都在模型外完成，模型只看到注入的那一小部分。
- **物理结构只能是一棵树**：时间轴做目录（追加写入、天然有序），内容靠 FTS5 检索层（交叉引用）。
- **摘要优先、全文兜底**：90% 的查询在摘要层结束，永远不用打开大文件。
- **常驻层要有硬上限**：MEMORY.md 满了就合并删旧（借鉴 Hermes 的 MEMORY.md/USER.md 设计）。
- **删除要可反悔**：软删除 + 回收站，确认后再 purge。

## 与同类方案对比

| 维度 | mem.py | Hermes Agent | DSH | 豆包 |
|---|---|---|---|---|
| 结构 | 时间树 + FTS5 | MEMORY.md + SQLite | workspace→session | 事实抽取 + 向量库 |
| 检索 | 关键词 FTS5 | FTS5 + 语义(提供商) | FTS5(默认关) | 向量语义检索 |
| 摘要 | 结构化 frontmatter | agent 维护条目 | LLM 会话标题 | LLM 抽取事实 |
| 常驻 | MEMORY.md ≤2200 字符 | MEMORY.md/USER.md | 会话标题 | 记忆条目 |
| token | 注入有上限 | ~1300 固定 | compaction 自动压缩 | Top-K 召回注入 |

## 隐私

记忆库默认包含你的真实对话摘要，**不要提交到公开仓库**（本项目 .gitignore 已排除 memories/）。发布示例请使用 `--content` 自行构造演示数据。

## License

MIT