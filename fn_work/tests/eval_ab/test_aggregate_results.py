"""aggregate_results 单测：增益列/CSV 落盘/文本表对齐/缺列与无 baseline 报错。"""

import csv

import pytest

from src.eval_ab.aggregate_results import ReportDataError, aggregate_results


def _metric(name, policy, wins=0, episodes=4, steps=10.0, tokens=(100, 40)):
    return {
        "name": name, "policy": policy, "episodes": episodes, "wins": wins,
        "success_rate": wins / episodes, "avg_steps": steps, "duration_s": 1.5,
        "token_usage": {"prompt_tokens": tokens[0], "completion_tokens": tokens[1], "calls": 9},
        "episode_results": [],
    }


METRICS = [
    _metric("baseline", "baseline", wins=1, steps=10.0),
    _metric("plus_curriculum", "curriculum", wins=3, steps=8.0, tokens=(120, 50)),
    _metric("full", "curriculum+regularized", wins=2, steps=9.5, tokens=(130, 60)),
]


# ① 增益列：相对 baseline 的成功率/步数差


def test_gain_columns_relative_to_baseline(tmp_path):
    csv_path, table = aggregate_results(METRICS, str(tmp_path))

    with open(csv_path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))

    assert len(rows) == 3
    by_name = {r["name"]: r for r in rows}
    assert by_name["baseline"]["d_success_rate"] == "0.0"
    assert float(by_name["plus_curriculum"]["d_success_rate"]) == pytest.approx(0.5)
    assert float(by_name["full"]["d_avg_steps"]) == pytest.approx(-0.5)
    assert by_name["baseline"]["prompt_tokens"] == "100"


def test_baseline_row_can_be_anywhere(tmp_path):
    reordered = [METRICS[1], METRICS[0], METRICS[2]]

    csv_path, _ = aggregate_results(reordered, str(tmp_path))

    with open(csv_path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert [r["name"] for r in rows] == ["plus_curriculum", "baseline", "full"]  # 行序保持
    assert float(rows[0]["d_success_rate"]) == pytest.approx(0.5)  # 增益仍对 baseline 算


# ② 文本表：三行对齐、含表头分隔线


def test_text_table_aligned_with_header(tmp_path):
    _, table = aggregate_results(METRICS, str(tmp_path))

    lines = table.splitlines()
    assert len(lines) == 5  # 表头 + 分隔线 + 三行
    assert all(" | " in line for line in [lines[0], *lines[2:]])  # 数据行含列分隔
    assert lines[1].startswith("---") and "+-" in lines[1]  # 分隔线风格
    assert "d_success_rate" in lines[0] and "full" in lines[4]
    cols = [len(line) for line in lines]
    assert cols[0] == cols[2] == cols[3] == cols[4]  # 等宽对齐


def test_csv_written_under_out_dir(tmp_path):
    csv_path, _ = aggregate_results(METRICS, str(tmp_path / "runs" / "run-42"))

    assert csv_path.endswith("run-42/ab_table.csv") or csv_path.endswith("run-42\\ab_table.csv")


# ③ 数据校验 → ReportDataError


def test_empty_metrics_raise():
    with pytest.raises(ReportDataError, match="非空列表"):
        aggregate_results([])


def test_missing_column_raises(tmp_path):
    broken = _metric("baseline", "baseline")
    del broken["success_rate"]

    with pytest.raises(ReportDataError, match="缺列.*success_rate"):
        aggregate_results([broken], str(tmp_path))


def test_no_baseline_row_raises(tmp_path):
    with pytest.raises(ReportDataError, match="无 policy=baseline"):
        aggregate_results([_metric("only_curriculum", "curriculum")], str(tmp_path))


def test_non_dict_entry_raises(tmp_path):
    with pytest.raises(ReportDataError, match=r"\[1\] 必须是映射"):
        aggregate_results([_metric("baseline", "baseline"), "junk"], str(tmp_path))
