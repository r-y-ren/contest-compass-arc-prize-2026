"""make_curriculum_policy 单测：包装协议/选源落日志/obs 注入/局终回填（JSONL 打桩）。"""

import pytest

from src.make_curriculum_policy import make_curriculum_policy as mcp
from src.make_curriculum_policy.make_curriculum_policy import (
    PolicyWrapError,
    make_curriculum_policy,
)


class _Inner:
    """内层假策略：记录收到的观测；可选 scene/total_usage。"""

    def __init__(self, scene="experiment", with_usage=True):
        self.scene = scene
        if with_usage:
            self.total_usage = {"prompt_tokens": 9, "completion_tokens": 4, "calls": 1}
        self.seen = []

    def act(self, obs):
        self.seen.append(obs)
        return {"name": "ACTION1"}


@pytest.fixture
def logs(monkeypatch):
    captured = []
    monkeypatch.setattr(
        mcp, "append_jsonl_log", lambda run_id, event, payload: captured.append((run_id, event, payload))
    )
    return captured


CFG = {"sources": {"easy": [{"outcome": "WIN", "steps": 3}], "hard": [{"outcome": "GAME_OVER", "steps": 90}]}}


# ① 构造校验


def test_inner_without_act_raises():
    with pytest.raises(PolicyWrapError, match="缺可调用 act"):
        make_curriculum_policy(object(), CFG)


def test_bad_sources_structure_raises():
    with pytest.raises(PolicyWrapError, match="sources 必须是"):
        make_curriculum_policy(_Inner(), {"sources": {"easy": "not-a-list"}})


def test_non_dict_config_raises():
    with pytest.raises(PolicyWrapError, match="必须是 dict"):
        make_curriculum_policy(_Inner(), ["sources"])


# ② 局开始：选最易源、写 curriculum_select 日志（含难度表与理由）


def test_episode_start_selects_easiest_and_logs(logs):
    policy = make_curriculum_policy(_Inner(), CFG)

    policy.on_episode_start({"game_id": "ls20"}, "run-1")

    source, event, payload = logs[-1]
    assert (source, event) == ("run-1", "curriculum_select")
    assert payload["source"] == "easy"  # 成率高步数少 → 难度低
    assert payload["difficulty_table"]["easy"] < payload["difficulty_table"]["hard"]
    assert "score=" in payload["reason"]


# ③ 局内：所选源注入 obs.experience_source 后转发；scene/usage 转发


def test_act_injects_source_into_obs_and_forwards(logs):
    inner = _Inner(scene="submit")
    policy = make_curriculum_policy(inner, CFG)
    policy.on_episode_start({"game_id": "ls20"}, "run-1")

    obs = {"game_id": "ls20", "state": "NOT_FINISHED", "frame": [], "levels_completed": 0,
           "win_levels": 1, "available_actions": [1]}
    action = policy.act(obs)

    assert action == {"name": "ACTION1"}
    assert inner.seen[0]["experience_source"]["id"] == "easy"
    assert "reason" in inner.seen[0]["experience_source"]
    assert obs.get("experience_source") is None  # 原观测不被改写（浅拷贝注入）
    assert policy.scene == "submit"
    assert policy.total_usage == {"prompt_tokens": 9, "completion_tokens": 4, "calls": 1}


def test_act_before_start_forwards_plain_obs(logs):
    inner = _Inner()
    policy = make_curriculum_policy(inner, CFG)
    obs = {"available_actions": [1]}

    policy.act(obs)

    assert inner.seen[0] == obs  # 未选源时不注入


# ④ 局终：结局记回所选源、难度更新落日志、利用计数推进


def test_episode_end_records_back_and_updates_difficulty(logs):
    policy = make_curriculum_policy(_Inner(), CFG)
    policy.on_episode_start({"game_id": "ls20"}, "run-1")

    policy.on_episode_end(
        {"episode_id": "ls20-x", "outcome": "WIN", "steps": 5}, "run-1"
    )

    source, event, payload = logs[-1]
    assert (source, event) == ("run-1", "curriculum_update")
    assert payload["record"] == {"outcome": "WIN", "steps": 5, "ts": payload["record"]["ts"]}
    assert payload["new_difficulty"] < 0.05  # easy 源两连胜少步 → 难度近 0
    assert payload["low_confidence"] is False


def test_exploitation_count_rotates_sources_across_episodes(logs):
    # 两源难度相近（easy 稍低），反复开局使利用计数让位
    cfg = {"sources": {"a": [{"outcome": "WIN", "steps": 5}], "b": [{"outcome": "WIN", "steps": 6}]}}
    policy = make_curriculum_policy(_Inner(), cfg)
    picks = []
    for i in range(3):
        policy.on_episode_start({"game_id": "g"}, f"run-{i}")
        picks.append(logs[-1][2]["source"])

    assert picks[0] == "a"  # 难度最低
    assert picks[1] == "b"  # a 已选 1 次：0.056+0.5 > b 的 0.06+0
    assert picks[2] == "a"  # 轮回


def test_episode_end_without_start_is_noop(logs):
    policy = make_curriculum_policy(_Inner(), CFG)

    policy.on_episode_end({"outcome": "WIN", "steps": 1}, "run-x")

    assert logs == []


# ⑤ 确定性：同配置同事件序列 → 同选择序列


def test_deterministic_selection_sequence(logs):
    def run():
        policy = make_curriculum_policy(_Inner(), CFG)
        seq = []
        for i in range(4):
            policy.on_episode_start({"game_id": "g"}, "r")
            seq.append((policy._current_source, policy._current_reason))
            policy.on_episode_end({"outcome": "GAME_OVER", "steps": 40}, "r")
        return seq

    assert run() == run()
