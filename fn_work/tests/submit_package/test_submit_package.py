"""submit_package 单测：真实组包+预检；CLI 与日志全打桩（不出网）。"""

import subprocess
from types import SimpleNamespace

import pytest

from src.build_kaggle_package.build_kaggle_package import build_kaggle_package
from src.submit_package import submit_package as sp
from src.submit_package.submit_package import SubmitError, submit_package


@pytest.fixture
def package(tmp_path):
    return build_kaggle_package("baseline", str(tmp_path / "pkg"))


@pytest.fixture
def logs(monkeypatch):
    captured = []
    monkeypatch.setattr(
        sp, "append_jsonl_log", lambda run_id, event, payload: captured.append((run_id, event, payload))
    )
    return captured


@pytest.fixture
def no_sleep(monkeypatch):
    monkeypatch.setattr(sp.time, "sleep", lambda s: None)


# ① 预检：坏包不出网即拒


def test_broken_package_rejected_before_cli(tmp_path, monkeypatch):
    def _no_cli(*a, **k):
        raise AssertionError("不应触 CLI")

    monkeypatch.setattr(sp.subprocess, "run", _no_cli)
    empty = tmp_path / "empty"
    empty.mkdir()

    with pytest.raises(SubmitError, match="包预检不过"):
        submit_package("arc-prize-2026-arc-agi-3", str(empty), dry_run=False)


def test_bad_competition_id_rejected(package):
    with pytest.raises(SubmitError, match="competition_id"):
        submit_package("", package)


# ② dry_run（默认）：不出网、回执完整、事件落日志


def test_dry_run_receipt_without_cli(package, monkeypatch, logs):
    monkeypatch.setattr(sp.subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(AssertionError("不应触 CLI")))

    receipt = submit_package("arc-prize-2026-arc-agi-3", package)

    assert receipt["status"] == "dry_run"
    assert receipt["verified"] is True
    assert receipt["competition"] == "arc-prize-2026-arc-agi-3"
    assert "make submit" in receipt["planned_handoff"]
    assert (logs[-1][0], logs[-1][1]) == ("submit-arc-prize-2026-arc-agi-3", "submit_dry_run")


# ③ 实跑模式（CLI 打桩）：成功回执 / 失败重试→耗尽 SubmitError 附原始输出


def test_real_submit_success_receipt(package, monkeypatch, logs, no_sleep):
    calls = []

    def _fake_run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout="Successfully submitted", stderr="")

    monkeypatch.setattr(sp.subprocess, "run", _fake_run)

    receipt = submit_package("arc-prize-2026-arc-agi-3", package, dry_run=False)

    assert receipt["status"] == "submitted"
    assert receipt["attempt"] == 1 and "Successfully submitted" in receipt["cli_output"]
    assert calls[0][:3] == ["kaggle", "competitions", "submit"]
    assert calls[0][3:] == ["-c", "arc-prize-2026-arc-agi-3", "-f", receipt["zip"]]
    assert (logs[-1][1]) == "submit_result"


def test_real_submit_retries_then_exhausts(package, monkeypatch, no_sleep):
    attempts = []

    def _fake_run(command, **kwargs):
        attempts.append(1)
        return SimpleNamespace(returncode=1, stdout="", stderr="403 - code competition rejects file submission")

    monkeypatch.setattr(sp.subprocess, "run", _fake_run)

    with pytest.raises(SubmitError, match="403 - code competition rejects"):
        submit_package("arc-prize-2026-arc-agi-3", package, dry_run=False)

    assert len(attempts) == 3  # 有限重试上限


def test_real_submit_recovers_on_third_attempt(package, monkeypatch, no_sleep):
    outcomes = iter([1, 1, 0])

    def _fake_run(command, **kwargs):
        return SimpleNamespace(returncode=next(outcomes), stdout="ok", stderr="")

    monkeypatch.setattr(sp.subprocess, "run", _fake_run)
    monkeypatch.setattr(sp, "append_jsonl_log", lambda *a: None)

    receipt = submit_package("arc-prize-2026-arc-agi-3", package, dry_run=False)

    assert receipt["attempt"] == 3 and receipt["status"] == "submitted"
