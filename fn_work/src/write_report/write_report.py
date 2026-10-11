"""复现报告主流程（责任文档 R7）：索引→核对→组装→写出 markdown。

报告三节：增益表（render_gain_table，行级溯源）/ 配置说明（默认阵语义）/
溯源附录（全部 run 的产物清单）。验收口径：报告中每个数字携带其 run 产物
路径；产物索引与对照表数字对不上 → ReportDataError（宁停勿错）。
"""

from __future__ import annotations

import csv
from pathlib import Path

from src.eval_ab.build_config_matrix import build_config_matrix
from src.write_report.collect_run_artifacts import ReportDataError, collect_run_artifacts
from src.write_report.render_gain_table import render_gain_table

# 配置组合的固定语义说明（与责任文档 R2-R4 对应）。
_POLICY_NOTES = {
    "baseline": "裸基线：固定提示词 + 冻结 LLM（对照起点）",
    "curriculum": "课程调度（R3/ActiveSaddler 降级）：先易后难编排经验源，包装 baseline",
    "regularized": "经验正则（R4/RRSI 降级）：筛选正则化历史经验入提示，包装 baseline",
    "curriculum+regularized": "全开：课程调度 ∘ 经验正则 ∘ 裸基线（编排层在外、记忆层在内）",
}


def _read_rows(table_csv: str) -> list:
    path = Path(table_csv)
    if not path.is_file():
        raise ReportDataError(f"对照表 CSV 不存在: {path}")
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ReportDataError(f"对照表 CSV 无数据行: {path}")
    return rows


def _cross_check(rows: list, artifact_index: dict, table_csv: str) -> None:
    """对照表配置名与索引中该 run 的解析结果一致（数字对不上宁停勿错）。"""
    csv_names = [row["name"] for row in rows]
    resolved = str(Path(table_csv).resolve())
    for run in artifact_index.get("runs", []):
        table = run.get("table") or {}
        if table.get("csv") and str(Path(table["csv"]).resolve()) == resolved:
            if table.get("configs") != csv_names:
                raise ReportDataError(
                    f"产物索引与对照表数字对不上: run {run['run_id']} 索引 configs="
                    f"{table.get('configs')} != CSV {csv_names}"
                )
            return
    raise ReportDataError(f"对照表 {resolved} 不在产物索引中（数字无法溯源）")


def _config_section(rows: list) -> str:
    matrix = {c["name"]: c for c in build_config_matrix()}
    lines = ["| 配置 | 组合 | 说明 |", "|---|---|---|"]
    for row in rows:
        config = matrix.get(row["name"])
        policy = config["policy"] if config else row.get("policy", "?")
        lines.append(f"| {row['name']} | {policy} | {_POLICY_NOTES.get(policy, '')} |")
    return "\n".join(lines)


def _appendix(artifact_index: dict) -> str:
    lines = ["| run_id | 修改时间 | 文件数 | 对照表 |", "|---|---|---|---|"]
    for run in artifact_index.get("runs", []):
        table = run.get("table")
        table_cell = f"[ab_table.csv]({table['csv']})（{table['rows']} 行）" if table else "—"
        lines.append(f"| {run['run_id']} | {run['mtime']} | {len(run['files'])} | {table_cell} |")
    return "\n".join(lines)


def write_report(runs_dir: str, table_csv: str) -> str:
    """报告主流程：建运行产物索引→组装增益表/配置说明/溯源附录→写出 markdown。

    - 返回报告路径（写在 table_csv 同目录的 report.md）；
    - rows 与索引对不上 / CSV 缺失或空 → ReportDataError。
    """
    artifact_index = collect_run_artifacts(runs_dir)
    rows = _read_rows(table_csv)
    _cross_check(rows, artifact_index, table_csv)

    gain_md = render_gain_table(rows, artifact_index)
    report = "\n".join(
        [
            "# ARC-AGI-3 自进化智能体复现报告",
            "",
            f"- runs 目录：`{artifact_index['runs_dir']}`",
            f"- 对照表：`{table_csv}`",
            "",
            "## 1. 增益表",
            "",
            gain_md,
            "",
            "## 2. 配置说明",
            "",
            _config_section(rows),
            "",
            "## 3. 运行产物溯源附录",
            "",
            _appendix(artifact_index),
            "",
        ]
    )
    report_path = Path(table_csv).parent / "report.md"
    report_path.write_text(report, encoding="utf-8")
    return str(report_path)
