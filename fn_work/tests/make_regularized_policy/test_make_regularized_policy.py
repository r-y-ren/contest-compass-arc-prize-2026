"""make_regularized_policy 单测：包装协议/经验注入/两版入库（JSONL 打桩）。"""

import pytest

from src.make_regularized_policy import make_regularized_policy as mrp
from src.make_regularized_policy.make_regularized_policy import (
    PolicyWrapError,
    make_regularized_policy,
)


class _Inner:
    def __init__(self, scene="experiment"):
        self.scene = scene
        self.total_usage = {"prompt_tokens": 7, "completion_tokens": 3, "calls": 1}
        self.seen = []

    def act(self, obs):
        self.seen.append(obs)
        return {"name": "ACTION1"}


@pytest.fixture
def logs(monkeypatch):
    captured = []
    monkeypatch.setattr(
        mrp, "append_jsonl_log", lambda run_id, event, payload: captured.append((run_id, event, payload))
    )
    return captured


def _obs(game_id="ls20-016295f7601e"):
    return {"game_id": game_id, "state": "NOT_FINISHED", "frame": [], "levels_completed": 0,
            "win_levels": 1, "available_actions": [1]}


# ① 构造校验


def test_inner_without_act_raises():
    with pytest.raises(PolicyWrapError, match="缺可调用 act"):
        make_regularized_policy(object(), {})


def test_bad_config_values_raise():
    with pytest.raises(PolicyWrapError, match="capacity 必须是正整数"):
        make_regularized_policy(_Inner(), {"capacity": 0})
    with pytest.raises(PolicyWrapError, match="budget 必须是正整数"):
        make_regularized_policy(_Inner(), {"budget": "3"})


def test_defaults_capacity_budget():
    policy = make_regularized_policy(_Inner(), {})
    assert policy._store["capacity"] == 32 and policy._budget == 3


# ② 冷启动：空库 act 不注入 experience，原样转发


def test_cold_start_act_forwards_plain(logs):
    inner = _Inner()
    policy = make_regularized_policy(inner, {})

    policy.act(_obs())

    assert "experience" not in inner.seen[0]
    assert inner.seen[0] == _obs()


# ③ 有经验时：子集注入 obs.experience，决策缓冲；scene/usage 转发


def test_act_injects_experience_subset(logs):
    inner = _Inner(scene="submit")
    policy = make_regularized_policy(inner, {"budget": 1})
    # 预填经验库：直接往内部 store 放两条同局经验
    policy._store["entries"] = [
        {"episode_id": "ls20-a", "outcome": "WIN", "steps": 4, "key_steps": [], "truncated": False},
        {"episode_id": "ls20-b", "outcome": "GAME_OVER", "steps": 9, "key_steps": [], "truncated": False},
    ]

    policy.act(_obs())

    injected = inner.seen[0]["experience"]
    # ls20-b（最新）=1.0新近+1.0相关=2.0 > ls20-a（WIN 但最旧）=0+1.0+0.5=1.5，budget=1 取 b
    assert [e["episode_id"] for e in injected] == ["ls20-b"]
    assert policy.scene == "submit"
    assert policy.total_usage == {"prompt_tokens": 7, "completion_tokens": 3, "calls": 1}


# ④ 局终两版入库：原始关键步进库 + 正则决策日志刷 JSONL；缓冲复位


def test_episode_end_stores_raw_and_flushes_regularized(logs):
    policy = make_regularized_policy(_Inner(), {})
    policy.on_episode_start({"game_id": "ls20"}, "run-1")
    policy.act(_obs())   # 第 1 步
    policy.act(_obs())   # 第 2 步

    policy.on_episode_end({"episode_id": "ls20-x", "outcome": "WIN", "steps": 2}, "run-1")

    # 原始版：库内新条目含两步关键动作
    (entry,) = policy._store["entries"]
    assert entry["key_steps"] == [
        {"step": 1, "action": {"name": "ACTION1"}},
        {"step": 2, "action": {"name": "ACTION1"}},
    ]
    assert entry["outcome"] == "WIN"
    # 正则版：JSONL 事件含逐步决策与库快照
    run_id, event, payload = logs[-1]
    assert (run_id, event) == ("run-1", "regularized_episode")
    assert [d["step"] for d in payload["decisions"]] == [1, 2]
    assert payload["store_size"] == 1 and payload["capacity"] == 32
    # 缓冲复位
    assert policy._episode_actions == [] and policy._episode_decisions == []


def test_episode_start_resets_buffers(logs):
    policy = make_regularized_policy(_Inner(), {})
    policy.act(_obs())
    assert policy._episode_actions

    policy.on_episode_start({"game_id": "ls20"}, "run-2")

    assert policy._episode_actions == [] and policy._episode_decisions == []


# ⑤ 经验跨局累积与容量约束


def test_experience_accumulates_across_episodes(logs):
    policy = make_regularized_policy(_Inner(), {"capacity": 2})
    for i in range(3):
        policy.on_episode_start({"game_id": "ls20"}, f"run-{i}")
        policy.act(_obs())
        policy.on_episode_end({"episode_id": f"ls20-{i}", "outcome": "GAME_OVER", "steps": 1}, f"run-{i}")

    assert len(policy._store["entries"]) == 2  # 容量 2，最旧被淘汰
    assert [e["episode_id"] for e in policy._store["entries"]] == ["ls20-1", "ls20-2"]


def test_end_to_end_injection_after_first_episode(logs):
    inner = _Inner()
    policy = make_regularized_policy(inner, {"budget": 2})
    policy.on_episode_start({"game_id": "ls20"}, "run-1")
    policy.act(_obs())
    policy.on_episode_end({"episode_id": "ls20-0", "outcome": "WIN", "steps": 1}, "run-1")

    policy.on_episode_start({"game_id": "ls20"}, "run-2")
    policy.act(_obs())  # 第二局：上局经验应被注入

    assert [e["episode_id"] for e in inner.seen[-1]["experience"]] == ["ls20-0"]
