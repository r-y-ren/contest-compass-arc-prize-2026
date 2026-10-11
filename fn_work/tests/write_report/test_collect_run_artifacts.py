"""collect_run_artifacts 单测：真实目录扫描（临时目录造产物）；只读性验证。"""

import pytest

from src.write_report.collect_run_artifacts import ReportDataError, collect_run_artifacts


@pytest.fixture
def runs(tmp_path):
    run1 = tmp_path / "runs" / "eval-111-s42"
    run1.mkdir(parents=True)
    (run1 / "ab_table.csv").write_text(
        "name,policy,episodes,wins\nbaseline,baseline,2,0\nfull,curriculum+regularized,2,1\n",
        encoding="utf-8",
    )
    run2 = tmp_path / "runs" / "eval-222-s7"
    run2.mkdir()
    (run2 / "notes.txt").write_text("no table here\n", encoding="utf-8")
    return tmp_path / "runs"


# ① 扫描：条目齐、表解析、无表 run 的 table=None


def test_scans_runs_with_table_details(runs):
    index = collect_run_artifacts(str(runs))

    assert index["runs_dir"].endswith("runs")
    by_id = {r["run_id"]: r for r in index["runs"]}
    assert set(by_id) == {"eval-111-s42", "eval-222-s7"}

    with_table = by_id["eval-111-s42"]
    assert with_table["table"]["rows"] == 2
    assert with_table["table"]["configs"] == ["baseline", "full"]
    assert "eval-111-s42/ab_table.csv" in with_table["files"]  # 相对 runs 根的全前缀
    assert by_id["eval-222-s7"]["table"] is None
    assert by_id["eval-222-s7"]["files"] == ["eval-222-s7/notes.txt"]


# ② 只读：扫描后目录内容不变


def test_read_only_scan(runs):
    before = sorted(str(p) for p in runs.rglob("*"))
    collect_run_artifacts(str(runs))
    after = sorted(str(p) for p in runs.rglob("*"))
    assert before == after


# ③ 空目录合法；目录缺失报错


def test_empty_runs_dir_ok(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    index = collect_run_artifacts(str(empty))
    assert index["runs"] == []


def test_missing_dir_raises(tmp_path):
    with pytest.raises(ReportDataError, match="runs 目录不存在"):
        collect_run_artifacts(str(tmp_path / "nope"))
