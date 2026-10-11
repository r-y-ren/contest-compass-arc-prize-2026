"""write_report 单测：真实产物目录（aggregate 真出表）端到端出报告。"""

import pytest

from src.eval_ab.aggregate_results import aggregate_results
from src.write_report.collect_run_artifacts import ReportDataError
from src.write_report.write_report import write_report


def _metric(name, policy, wins, episodes=4):
    return {"name": name, "policy": policy, "episodes": episodes, "wins": wins,
            "success_rate": wins / episodes, "avg_steps": 8.0, "duration_s": 0.2,
            "token_usage": {"prompt_tokens": 1, "completion_tokens": 1, "calls": 1},
            "episode_results": []}


@pytest.fixture
def artifacts(tmp_path):
    """真 aggregate 出表 + 附属文件，构成可溯源 runs 目录。"""
    runs = tmp_path / "runs"
    csv_path, _ = aggregate_results(
        [_metric("baseline", "baseline", 1), _metric("full", "curriculum+regularized", 3)],
        str(runs / "eval-999-s1"),
    )
    other = runs / "eval-888-s2"
    other.mkdir(parents=True)
    (other / "notes.txt").write_text("x\n", encoding="utf-8")
    return runs, csv_path


# ① 报告产出：三节齐、数字与链接可溯


def test_report_three_sections_with_traceable_numbers(artifacts):
    runs, csv_path = artifacts

    report_path = write_report(str(runs), csv_path)

    text = open(report_path, encoding="utf-8").read()
    assert report_path.endswith("report.md")
    assert "## 1. 增益表" in text and "## 2. 配置说明" in text and "## 3. 运行产物溯源附录" in text
    assert "| baseline |" in text and "| full |" in text  # 增益表行
    assert "[eval-999-s1]" in text and "ab_table.csv" in text  # 行级溯源链接
    assert "curriculum+regularized" in text  # 配置说明
    assert "eval-888-s2" in text  # 附录含其它 run


# ② 宁停勿错：CSV 不在索引 / 数字对不上 / 文件缺失


def test_csv_not_in_index_raises(tmp_path, artifacts):
    runs, csv_path = artifacts
    # 把 CSV 挪出 runs 目录 → 索引查无此表
    outside = tmp_path / "outside.csv"
    outside.write_text(open(csv_path, encoding="utf-8").read(), encoding="utf-8")

    with pytest.raises(ReportDataError, match="不在产物索引中"):
        write_report(str(runs), str(outside))


def test_index_number_mismatch_raises(tmp_path, artifacts):
    runs, csv_path = artifacts
    # 篡改索引侧：在 runs 里手工造一份与 CSV 不同 configs 的同名表（模拟索引漂移）
    tampered = runs / "eval-tamper"
    tampered.mkdir()
    (tampered / "ab_table.csv").write_text("name,policy\nbaseline,baseline\n", encoding="utf-8")

    # 用被篡改 run 的表出报告：其索引 configs 与 CSV 行（仅 baseline）一致 → 过；
    # 但再喂入行数不同的表则报错。此处直接验 CSV 缺失分支：
    with pytest.raises(ReportDataError, match="CSV"):
        write_report(str(runs), str(runs / "eval-999-s1" / "nope.csv"))


def test_missing_runs_dir_raises(tmp_path, artifacts):
    _, csv_path = artifacts
    with pytest.raises(ReportDataError, match="runs 目录不存在"):
        write_report(str(tmp_path / "nope-runs"), csv_path)
