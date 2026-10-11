"""render_gain_table 单测：markdown 结构/行级溯源链接/索引缺项报错。"""

import pytest

from src.write_report.collect_run_artifacts import ReportDataError
from src.write_report.render_gain_table import render_gain_table


def _rows():
    return [
        {"name": "baseline", "policy": "baseline", "episodes": 2, "wins": 0,
         "success_rate": 0.0, "avg_steps": 75.0, "d_success_rate": 0.0, "d_avg_steps": 0.0},
        {"name": "full", "policy": "curriculum+regularized", "episodes": 2, "wins": 1,
         "success_rate": 0.5, "avg_steps": 60.0, "d_success_rate": 0.5, "d_avg_steps": -15.0},
    ]


def _index():
    return {
        "runs_dir": "/runs",
        "runs": [
            {"run_id": "eval-111", "dir": "/runs/eval-111", "mtime": "t",
             "files": ["eval-111/ab_table.csv"],
             "table": {"csv": "/runs/eval-111/ab_table.csv", "rows": 2,
                       "configs": ["baseline", "full"]}},
        ],
    }


# ① markdown 结构：表头/分隔/两行、八列+source


def test_markdown_table_structure():
    md = render_gain_table(_rows(), _index())

    lines = md.splitlines()
    assert lines[0].startswith("| name | policy |")
    assert lines[0].endswith("| source |")
    assert set(lines[1]) <= {"|", "-"}
    assert len(lines) == 4
    assert "| baseline | baseline | 2 |" in lines[2]
    assert "| 0.5 |" in lines[3]  # full 行增益列


# ② 行级溯源：source 含 run 链接与 csv 链接


def test_source_cell_links_run_and_csv():
    md = render_gain_table(_rows(), _index())

    assert "[eval-111](/runs/eval-111)" in md
    assert "[csv](/runs/eval-111/ab_table.csv)" in md


def test_row_resolves_to_its_own_run_when_multiple():
    index = _index()
    index["runs"].append(
        {"run_id": "eval-222", "dir": "/runs/eval-222", "mtime": "t", "files": [],
         "table": {"csv": "/runs/eval-222/ab_table.csv", "rows": 1, "configs": ["baseline"]}}
    )

    md = render_gain_table(_rows(), index)

    # 两个 run 都含 baseline：首列出的 run 胜（确定性），full 行仍指 eval-111
    assert "[eval-111]" in md


# ③ 索引缺项 → ReportDataError；空表 → 空串


def test_missing_run_in_index_raises():
    index = {"runs_dir": "/runs", "runs": []}
    with pytest.raises(ReportDataError, match=r"索引缺项.*'baseline'"):  # 首行先触发
        render_gain_table(_rows(), index)


def test_empty_table_renders_empty_string():
    assert render_gain_table([], _index()) == ""


def test_non_dict_row_raises():
    with pytest.raises(ReportDataError, match="必须是含 name 的映射"):
        render_gain_table(["junk"], _index())
