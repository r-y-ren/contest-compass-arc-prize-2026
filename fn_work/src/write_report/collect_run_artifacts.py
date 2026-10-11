"""运行产物索引：runs 目录扫描汇集（责任文档 R7）。

只读不改：产物索引 = {"runs_dir": 绝对路径, "runs": [run 条目, ...]}，
run 条目 {"run_id", "dir", "mtime", "files": [相对路径...], "table": {...}|None}——
"table" 在该 run 含 ab_table.csv 时解析出 {"rows": 行数, "configs": [配置名...]}。
目录不存在 → ReportDataError（宁停勿错）。
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path


class ReportDataError(RuntimeError):
    """报告数据不合法：runs 目录不存在/对照表与索引对不上。"""


def collect_run_artifacts(runs_dir: str) -> dict:
    """扫描 runs 目录汇集运行产物索引；只读，返回 {"runs_dir", "runs": [...]}。"""
    root = Path(runs_dir)
    if not root.is_dir():
        raise ReportDataError(f"runs 目录不存在: {root}")

    runs = []
    for run_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        files = sorted(str(f.relative_to(root)) for f in run_dir.rglob("*") if f.is_file())
        table = None
        csv_path = run_dir / "ab_table.csv"
        if csv_path.is_file():
            with open(csv_path, encoding="utf-8", newline="") as fh:
                rows = list(csv.DictReader(fh))
            table = {
                "csv": str(csv_path),
                "rows": len(rows),
                "configs": [row.get("name", "?") for row in rows],
            }
        runs.append(
            {
                "run_id": run_dir.name,
                "dir": str(run_dir),
                "mtime": datetime.fromtimestamp(
                    run_dir.stat().st_mtime, tz=timezone.utc
                ).isoformat(),
                "files": files,
                "table": table,
            }
        )
    return {"runs_dir": str(root.resolve()), "runs": runs}
