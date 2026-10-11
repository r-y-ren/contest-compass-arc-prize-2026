"""增益表渲染：对照表行 → 报告用 markdown 表（责任文档 R7）。

纯函数。行级溯源：每行按配置名在产物索引中定位含该配置对照表的 run，
source 列内联挂该 run 目录与 CSV 链接——该行每个数字的产物路径由此可溯
（R7 验收：审阅者按路径能找到产物且数字一致）。
"""

from __future__ import annotations

from src.write_report.collect_run_artifacts import ReportDataError

_COLUMNS = (
    "name", "policy", "episodes", "wins", "success_rate", "avg_steps",
    "d_success_rate", "d_avg_steps",
)


def _source_cell(row_name: str, artifact_index: dict) -> str:
    """按配置名定位源 run，返回 markdown 链接；索引缺项 → ReportDataError。"""
    for run in artifact_index.get("runs", []):
        table = run.get("table") or {}
        if row_name in table.get("configs", []):
            return f"[{run['run_id']}]({run['dir']}) · [csv]({table['csv']})"
    raise ReportDataError(
        f"索引缺项：产物索引中无含配置 {row_name!r} 对照表的 run（数字无法溯源）"
    )


def render_gain_table(table_data, artifact_index: dict) -> str:
    """把对照表行渲染为 markdown 增益表（含 source 溯源列）；纯函数。

    - table_data：行 dict 列表（aggregate_results 的行结构，列名同 _COLUMNS）；
    - artifact_index：collect_run_artifacts 输出；
    - 空表 → 空字符串；非 dict 行 → ReportDataError。
    """
    if not table_data:
        return ""
    if not isinstance(artifact_index, dict):
        raise ReportDataError(f"artifact_index 必须是 dict: {artifact_index!r}")

    header = "| " + " | ".join(_COLUMNS) + " | source |"
    separator = "|" + "|".join(["---"] * (len(_COLUMNS) + 1)) + "|"
    lines = [header, separator]
    for row in table_data:
        if not isinstance(row, dict) or "name" not in row:
            raise ReportDataError(f"对照表行必须是含 name 的映射: {row!r}")
        cells = " | ".join(str(row.get(col, "")) for col in _COLUMNS)
        lines.append(f"| {cells} | {_source_cell(row['name'], artifact_index)} |")
    return "\n".join(lines)
