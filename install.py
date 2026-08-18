#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mem.py 一键安装（跨平台，纯标准库）。

自动适配任何用户：检测 DSH_HOME / 用户主目录，把 SKILL.md 模板渲染成真实路径
安装到 $DSH_HOME/skills/memory/SKILL.md。mem.py 本身零配置（记忆库按
MEMORY_HOME > $DSH_HOME/memories > mem.py 所在目录 自动定位）。

用法:  python install.py          # 安装 DSH 技能
       python install.py --path   # 额外把 mem.py 加入用户 PATH（Windows 提示）
"""
import argparse, os, sys
from pathlib import Path


def dsh_home() -> Path:
    return Path(os.environ.get("DSH_HOME") or Path.home() / ".dsh")


def render(mem_py: Path, memory_home: Path) -> str:
    tpl = (Path(__file__).resolve().parent / "SKILL.md.tpl").read_text(encoding="utf-8")
    return tpl.replace("{{MEM_PY}}", str(mem_py)).replace("{{MEMORY_HOME}}", str(memory_home))


def add_to_path(mem_py: Path) -> None:
    """把 mem.py 的 mem 命令加进 PATH（可选便利）。"""
    if sys.platform == "win32":
        bindir = Path.home() / ".local" / "bin"
        bindir.mkdir(parents=True, exist_ok=True)
        shim = bindir / ("mem.py" if sys.platform != "win32" else "mem.cmd")
        shim.write_text(f"@echo off\r\npython \"{mem_py}\" %*\r\n", encoding="utf-8")
        print(f"  提示: 把 {bindir} 加入 PATH 后可直接用 mem.py 命令")
    else:
        bindir = Path.home() / ".local" / "bin"
        bindir.mkdir(parents=True, exist_ok=True)
        link = bindir / "mem.py"
        link.write_text(f"#!/bin/sh\nexec python3 \"{mem_py}\" \"$@\"\n", encoding="utf-8")
        link.chmod(0o755)
        print(f"  ✓ {link} (加入 PATH 后可直接 mem.py)")


def main() -> int:
    ap = argparse.ArgumentParser(description="mem.py 一键安装")
    ap.add_argument("--path", action="store_true", help="同时把 mem 命令加入 PATH")
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    mem_py = here / "mem.py"
    if not mem_py.exists():
        print(f"错误: 找不到 {mem_py}（install.py 必须和 mem.py 同目录）", file=sys.stderr)
        return 1

    dh = dsh_home()
    memory_home = Path(os.environ.get("MEMORY_HOME") or (dh / "memories"))
    target = dh / "skills" / "memory" / "SKILL.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(mem_py, memory_home), encoding="utf-8")

    print(f"✓ DSH 技能: {target}")
    print(f"✓ 记忆库:   {memory_home}（首次使用自动创建；MEMORY_HOME 可覆盖）")
    print(f"✓ 入口:     {mem_py}（自动定位，不依赖工作目录）")
    if args.path:
        add_to_path(mem_py)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())