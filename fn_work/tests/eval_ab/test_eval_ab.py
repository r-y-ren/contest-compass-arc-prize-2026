"""eval_ab 单测：load_episode_set/run_config_batch 打桩；矩阵/汇总走真件。"""

import csv
import os

import pytest

from src.eval_ab import eval_ab as ea
from src.eval_ab.eval_ab import eval_ab
from src.shared.load_episode_set import ConfigError


def _write_set(tmp_path, ids):
    path = tmp_path / "set.yaml"
    path.write_text("name: t\nepisode_ids:\n" + "".join(f"  - {i}\n" for i in ids), encoding="utf-8")
    return str(path)


@pytest.fixture
def env(tmp_path, monkeypatch):
    """隔离环境变量：局集指向临时 YAML、runs 落临时目录、SDK 索引返回固定表。"""
    monkeypatch.setenv("ARC_EPISODE_SET", _write_set(tmp_path, ["g1", "g2", "g3"]))
    monkeypatch.setenv("ARC_RUNS_DIR", str(tmp_path / "runs"))
    monkeypatch.setattr(ea, "_sdk_episode_ids", lambda: ["g1", "g2", "g3", "g4"])
    return tmp_path


@pytest.fixture
def batch(monkeypatch):
    """打桩 run_config_batch：按 policy 产出可区分指标；记录收到的局集与 run_id。"""
    seen = []

    def _fake(config, episode_set, run_id):
        seen.append({"config": config["name"], "ids": list(episode_set["episode_ids"]),
                     "seed": episode_set["seed"], "run_id": run_id})
        return {
            "name": config["name"], "policy": config["policy"],
            "episodes": len(episode_set["episode_ids"]),
            "wins": 1 if config["policy"] != "baseline" else 0,
            "success_rate": (1 if config["policy"] != "baseline" else 0) / len(episode_set["episode_ids"]),
            "avg_steps": 5.0, "duration_s": 0.1,
            "token_usage": {"prompt_tokens": 1, "completion_tokens": 1, "calls": 1},
            "episode_results": [],
        }

    monkeypatch.setattr(ea, "run_config_batch", _fake)
    return seen


# ① 编排：局集截取、四配置顺序、起止事件、CSV 落 run 目录


def test_orchestrates_four_configs_with_truncated_set(env, batch, capsys, monkeypatch):
    logs = []
    monkeypatch.setattr(ea, "append_jsonl_log", lambda run_id, event, payload: logs.append((run_id, event)))

    summary = eval_ab(2, 42)

    assert [s["config"] for s in batch] == ["baseline", "plus_curriculum", "plus_regularized", "full"]
    assert all(s["ids"] == ["g1", "g2"] and s["seed"] == 42 for s in batch)  # 截前 2 + seed 注入
    assert all(s["run_id"] == summary["run_id"] for s in batch)
    assert [e for _, e in logs] == ["eval_ab_start", "eval_ab_end"]
    out = capsys.readouterr().out
    assert "d_success_rate" in out and "baseline" in out  # 控制台对照表
    with open(summary["csv_path"], encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 4 and rows[0]["name"] == "baseline"


def test_configs_filter_by_name(env, batch, monkeypatch):
    monkeypatch.setattr(ea, "append_jsonl_log", lambda *a: None)

    eval_ab(3, 0, configs=["baseline", "full"])

    assert [s["config"] for s in batch] == ["baseline", "full"]


def test_unknown_config_name_raises(env, batch):
    with pytest.raises(ValueError, match="未知配置名"):
        eval_ab(1, 0, configs=["baseline", "sgd"])


# ② SDK 索引：注入校验生效（未知局 ID 报 ConfigError）；SDK 不可达降级跳过


def test_sdk_listing_validates_episode_ids(env, batch, monkeypatch):
    monkeypatch.setattr(ea, "_sdk_episode_ids", lambda: ["only-known"])
    monkeypatch.setattr(ea, "append_jsonl_log", lambda *a: None)

    with pytest.raises(ConfigError, match="局 ID 不在官方 SDK 局索引中: g1"):
        eval_ab(2, 0)


def test_sdk_unreachable_degrades_to_structural_validation(env, batch, monkeypatch):
    monkeypatch.setattr(ea, "_sdk_episode_ids", lambda: None)
    monkeypatch.setattr(ea, "append_jsonl_log", lambda *a: None)

    summary = eval_ab(1, 0)  # 局集结构合法 → 照跑

    assert summary["metrics"][0]["episodes"] == 1


# ③ 参数校验与失败透传


@pytest.mark.parametrize("bad", [0, -1, "3", True, 1.5])
def test_bad_episodes_rejected(env, bad):
    with pytest.raises(ValueError, match="episodes 必须是正整数"):
        eval_ab(bad, 0)


def test_batch_failure_propagates(env, monkeypatch):
    from src.eval_ab.run_config_batch import ExperimentAbortError

    def _boom(config, episode_set, run_id):
        raise ExperimentAbortError(f"配置 {config['name']} 第 1 局（g1）失败: LLMServiceError")

    monkeypatch.setattr(ea, "run_config_batch", _boom)
    monkeypatch.setattr(ea, "append_jsonl_log", lambda *a: None)

    with pytest.raises(ExperimentAbortError, match="g1"):
        eval_ab(2, 0)
