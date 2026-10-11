"""对照表汇总：各配置指标 → CSV 文件 + 对齐文本表（责任文档 R5）。

- 行序与输入 metrics 一致；列：name/policy/episodes/wins/success_rate/avg_steps/
  duration_s/prompt_tokens/completion_tokens + 相对 baseline 的增益列
  （d_success_rate 百分点、d_avg_steps 步）；
- baseline 行 = policy=="baseline" 的首行；无 baseline 或指标缺列 → ReportDataError
  （宁停勿错——对照表数字必须可比）；
- CSV 落盘 out_dir（可选参数，签名微调 2026-10-11：eval_ab 以 run 级目录注入，
  缺省 fn_work/runs；文件名固定 ab_table.csv，同 run 重跑覆盖）。
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

_COLUMNS = (
    "name", "policy", "episodes", "wins", "success_rate", "avg_steps",
    "duration_s", "prompt_tokens", "completion_tokens", "d_success_rate", "d_avg_steps",
)
_REQUIRED_KEYS = ("name", "policy", "episodes", "wins", "success_rate", "avg_steps")


class ReportDataError(RuntimeError):
    """对照表数据不合法：非列表/指标缺列/无 baseline 行（增益列无法计算）。"""


def _row(metric: dict, baseline_rate: float, baseline_steps: float) -> dict:
    tokens = metric.get("token_usage") or {}
    rate = metric["success_rate"]
    steps = metric["avg_steps"]
    return {
        "name": metric["name"],
        "policy": metric["policy"],
        "episodes": metric["episodes"],
        "wins": metric["wins"],
        "success_rate": round(rate, 4),
        "avg_steps": round(steps, 3),
        "duration_s": metric.get("duration_s", 0.0),
        "prompt_tokens": tokens.get("prompt_tokens", 0),
        "completion_tokens": tokens.get("completion_tokens", 0),
        "d_success_rate": round(rate - baseline_rate, 4),
        "d_avg_steps": round(steps - baseline_steps, 3),
    }


def aggregate_results(metrics: list, out_dir: str = "fn_work/runs") -> tuple:
    """把各配置指标汇成对照表，返回 (CSV 路径, 文本表)。

    - metrics：run_config_batch 返回的指标 dict 列表（至少含 baseline 行）；
    - CSV 写入 out_dir/ab_table.csv（目录自动创建）；
    - 文本表列对齐，可直接打印控制台。
    """
    if not isinstance(metrics, list) or not metrics:
        raise ReportDataError(f"metrics 必须是非空列表，实际是: {metrics!r}")
    for index, metric in enumerate(metrics):
        if not isinstance(metric, dict):
            raise ReportDataError(f"metrics[{index}] 必须是映射: {metric!r}")
        missing = [key for key in _REQUIRED_KEYS if key not in metric]
        if missing:
            raise ReportDataError(f"metrics[{index}]（{metric.get('name', '?')}）缺列: {missing}")

    baseline = next((m for m in metrics if m.get("policy") == "baseline"), None)
    if baseline is None:
        raise ReportDataError("metrics 无 policy=baseline 的行，增益列无法计算")

    rows = [_row(m, baseline["success_rate"], baseline["avg_steps"]) for m in metrics]

    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    csv_path = target / "ab_table.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)

    widths = {col: max(len(col), *(len(str(row[col])) for row in rows)) for col in _COLUMNS}
    header = " | ".join(col.ljust(widths[col]) for col in _COLUMNS)
    separator = "-+-".join("-" * widths[col] for col in _COLUMNS)
    body = "\n".join(
        " | ".join(str(row[col]).ljust(widths[col]) for col in _COLUMNS) for row in rows
    )
    text_table = "\n".join([header, separator, body])
    return str(csv_path), text_table
