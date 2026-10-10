"""append_jsonl_log 实测：原子追加/同日累计/中文嵌套保真/stdout 镜像/自动建目录/失败透出。"""

import json
from datetime import datetime

import pytest

from src.shared.append_jsonl_log import LogWriteError, append_jsonl_log


def _day_file(root):
    return root / f"{datetime.now():%Y%m%d}.jsonl"


@pytest.fixture
def log_root(tmp_path, monkeypatch):
    monkeypatch.setenv("ARC_LOG_DIR", str(tmp_path))
    return tmp_path


def test_two_appends_roundtrip_ts_parseable(log_root):
    append_jsonl_log("run-1", "episode_start", {"step": 0})
    append_jsonl_log("run-1", "episode_end", {"step": 9})

    lines = _day_file(log_root).read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    records = [json.loads(line) for line in lines]
    for rec in records:
        assert set(rec) == {"ts", "run_id", "event", "payload"}
        datetime.fromisoformat(rec["ts"])  # ts 为可解析的 ISO8601
    assert (records[0]["run_id"], records[0]["event"]) == ("run-1", "episode_start")
    assert (records[1]["run_id"], records[1]["event"]) == ("run-1", "episode_end")


def test_same_day_accumulates_in_order(log_root):
    events = [f"e{i}" for i in range(5)]
    for ev in events:
        append_jsonl_log("run-2", ev, {"i": ev})

    records = [
        json.loads(line)
        for line in _day_file(log_root).read_text(encoding="utf-8").splitlines()
    ]
    assert [r["event"] for r in records] == events  # 同日累计，行序即写入序


def test_payload_chinese_and_nested_fidelity(log_root):
    payload = {"信息": "中文内容✓", "嵌套": {"层": [1, {"深": "值"}]}, "none": None}
    append_jsonl_log("run-3", "payload_check", payload)

    raw = _day_file(log_root).read_text(encoding="utf-8")
    assert "中文内容✓" in raw  # 原文保真，未被 \\u 转义
    rec = json.loads(raw.splitlines()[0])
    assert rec["payload"] == payload


def test_stdout_mirror(log_root, capsys):
    append_jsonl_log("run-4", "mirror", {"m": 1})

    out = capsys.readouterr().out
    disk = _day_file(log_root).read_text(encoding="utf-8")
    assert out.strip() == disk.strip()  # 镜像行与磁盘行一致


def test_creates_missing_dirs(tmp_path, monkeypatch):
    deep = tmp_path / "a" / "b" / "c"
    monkeypatch.setenv("ARC_LOG_DIR", str(deep))

    append_jsonl_log("run-5", "mkdir", {})

    assert (deep / f"{datetime.now():%Y%m%d}.jsonl").is_file()


def test_disk_failure_raises_logwriteerror_no_partial(log_root, monkeypatch, capsys):
    def _boom(*args, **kwargs):
        raise OSError("disk failure")

    monkeypatch.setattr("builtins.open", _boom)
    with pytest.raises(LogWriteError) as excinfo:
        append_jsonl_log("run-6", "will_fail", {"x": 1})

    assert isinstance(excinfo.value.__cause__, OSError)  # wrap OSError 且不吞
    monkeypatch.undo()
    assert not _day_file(log_root).exists()  # 不部分写
    assert "run-6" not in capsys.readouterr().out  # 失败不镜像
