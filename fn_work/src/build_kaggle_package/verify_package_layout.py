"""包布局自检：契约清单逐项存在性 + 入口可编译（责任文档 R6）。

纯校验不改包：差异以清单返回（(ok, [差异 str, ...])），无异常路径
（目录不存在也以差异项表达）。
"""

from __future__ import annotations

import py_compile
from pathlib import Path

# 契约清单（赛站实核 + 本项目打包约定）：文件/目录 → 说明。
REQUIRED_ITEMS = (
    ("agent/my_agent.py", "提交入口（官方 Agent 契约）"),
    ("src", "策略源码树（入口经 src.* 导入）"),
    ("requirements.txt", "依赖清单"),
    ("freeze.json", "冻结记录（commit/配置/时间戳）"),
)


def verify_package_layout(package_dir: str) -> tuple:
    """对照契约清单逐项检查包内文件存在性与入口可编译，返回 (通过, 差异清单)。

    - 任一必需项缺失 → 差异项 "缺少 <path>（<说明>）"；
    - 入口存在但 py_compile 失败 → 差异项带编译错误摘要；
    - 全过 → (True, [])。
    """
    package = Path(package_dir)
    issues = []

    for rel_path, note in REQUIRED_ITEMS:
        if not (package / rel_path).exists():
            issues.append(f"缺少 {rel_path}（{note}）")
    if issues:
        return False, issues  # 入口都没有，编译检查无意义

    entry = package / "agent" / "my_agent.py"
    try:
        py_compile.compile(str(entry), doraise=True)
    except py_compile.PyCompileError as exc:
        issues.append(f"入口编译失败 agent/my_agent.py: {str(exc).splitlines()[-1]}")

    return (not issues), issues
