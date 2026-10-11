"""run_episode 单测：monkeypatch connect_env 与日志（密闭），真 submit_action 走假 env。"""

import pytest

from src.run_episode import run_episode as re_mod
from src.run_episode.run_episode import run_episode
from src.shared.llm_complete import LLMServiceError


def _obs(state="NOT_FINISHED", levels=0):
    return {
        "game_id": "ls20-016295f7601e",
        "state": state,
        "frame": [[[0, 1]]],
        "levels_completed": levels,
        "win_levels": 254,
        "available_actions": [0, 1, 2],
    }


class _FakeEnv:
    """step 按序吐结果（dict / None）。"""

    def __init__(self, results):
        self.results = list(results)

    def step(self, action, data=None):
        item = self.results.pop(0)
        return item


class _FakePolicy:
    """act 按序吐动作并记录收到的观测；带 scene/total_usage 协议属性。"""

    def __init__(self, actions, scene="experiment"):
        self.actions = list(actions)
        self.seen_obs = []
        self.scene = scene
        self.total_usage = {"prompt_tokens": 100, "completion_tokens": 50, "calls": 4}

    def act(self, obs):
        self.seen_obs.append(dict(obs))
        return self.actions.pop(0)


class _BarePolicy:
    """无 scene/total_usage 属性的最小策略。"""

    def act(self, obs):
        return {"name": "ACTION1"}


def _install(monkeypatch, env_results, initial_obs=None):
    """monkeypatch connect_env 返回假 env；捕获日志调用。返回 (env, logs, policy_holder)。"""
    env = _FakeEnv(env_results)
    logs = []

    def _fake_connect(spec):
        return env, initial_obs if initial_obs is not None else _obs()

    monkeypatch.setattr(re_mod, "connect_env", _fake_connect)
    monkeypatch.setattr(
        re_mod, "append_jsonl_log", lambda run_id, event, payload: logs.append((event, payload))
    )
    return env, logs


# ① 两步到 WIN：结果字段 + 步日志 + 局终日志


def test_two_step_win_result_and_logs(monkeypatch):
    _, logs = _install(monkeypatch, [_obs(levels=1), _obs("WIN", levels=2)])
    policy = _FakePolicy([{"name": "ACTION1"}, {"name": "ACTION2"}])

    result = run_episode({"game_id": "ls20"}, policy, "run-1")

    assert result["episode_id"] == "ls20-016295f7601e"  # 解析后局 ID
    assert result["outcome"] == "WIN"
    assert result["steps"] == 2
    assert result["levels_completed"] == 2
    assert result["win_levels"] == 254
    assert result["token_usage"] == {"prompt_tokens": 100, "completion_tokens": 50, "calls": 4}
    assert isinstance(result["duration_s"], float) and result["duration_s"] >= 0

    step_logs = [p for event, p in logs if event == "step"]
    assert [p["step"] for p in step_logs] == [1, 2]
    assert step_logs[0]["action"] == {"name": "ACTION1"}
    assert step_logs[0]["state"] == "NOT_FINISHED"
    assert isinstance(step_logs[0]["latency_ms"], int)
    end_logs = [p for event, p in logs if event == "episode_end"]
    assert len(end_logs) == 1 and end_logs[0]["outcome"] == "WIN"


def test_game_over_outcome(monkeypatch):
    _install(monkeypatch, [_obs("GAME_OVER")])
    policy = _FakePolicy([{"name": "ACTION1"}])

    result = run_episode({"game_id": "ls20"}, policy, "run-2")

    assert result["outcome"] == "GAME_OVER"
    assert result["steps"] == 1


# ② STEP_LIMIT 护栏：环境永非终局 → 触顶停（SDK 无时限，本地护栏）


def test_step_limit_guard(monkeypatch):
    monkeypatch.setattr(re_mod, "MAX_STEPS", 3)
    _install(monkeypatch, [_obs(), _obs(), _obs()])
    policy = _FakePolicy([{"name": "ACTION1"}] * 3)

    result = run_episode({"game_id": "ls20"}, policy, "run-3")

    assert result["outcome"] == "STEP_LIMIT"
    assert result["steps"] == 3


# ③ 异常透传：策略异常不吞、connect EnvError 直抛


def test_policy_exception_propagates_without_end_log(monkeypatch):
    _, logs = _install(monkeypatch, [_obs()])

    class _Boom(_FakePolicy):
        def act(self, obs):
            raise LLMServiceError("experiment abort")

    with pytest.raises(LLMServiceError, match="experiment abort"):
        run_episode({"game_id": "ls20"}, _Boom([]), "run-4")
    assert not any(event == "episode_end" for event, _ in logs)


def test_connect_env_error_propagates(monkeypatch):
    from src.run_episode._frame import EnvError

    monkeypatch.setattr(re_mod, "append_jsonl_log", lambda *a: None)

    def _boom(spec):
        raise EnvError("SDK make 返回 None：局不存在或不可用（ls20）")

    monkeypatch.setattr(re_mod, "connect_env", _boom)

    with pytest.raises(EnvError, match="make 返回 None"):
        run_episode({"game_id": "ls20"}, _BarePolicy(), "run-5")


# ④ submit 场景 STEP_FAILED 降级：失败步保持上一观测继续


def test_submit_scene_step_failed_keeps_previous_obs(monkeypatch):
    _, logs = _install(monkeypatch, [None, _obs("WIN")])
    policy = _FakePolicy([{"name": "ACTION1"}, {"name": "ACTION2"}], scene="submit")

    result = run_episode({"game_id": "ls20"}, policy, "run-6")

    assert result["outcome"] == "WIN"
    assert result["steps"] == 2
    # 第一步失败（STEP_FAILED 哨兵）后，第二步策略看到的仍是初始观测（未推进）
    assert policy.seen_obs[0] == policy.seen_obs[1]
    step_states = [p["state"] for event, p in logs if event == "step"]
    assert step_states == ["STEP_FAILED", "WIN"]


# ⑤ 最小策略协议：无 scene/total_usage → 缺省 experiment + 零用量快照


def test_bare_policy_defaults_scene_and_zero_usage(monkeypatch):
    env, _ = _install(monkeypatch, [_obs("WIN")])

    result = run_episode({"game_id": "ls20"}, _BarePolicy(), "run-7")

    assert result["outcome"] == "WIN"
    assert result["token_usage"] == {"prompt_tokens": 0, "completion_tokens": 0, "calls": 0}
    # scene 缺省 experiment：假 env 的 step 正常返回（submit_action 未因 scene 拒绝）
    assert env.results == []


# ⑥ 策略协议钩子：on_episode_start/on_episode_end 检测到即调用；异常透传


def test_hooks_called_with_spec_result_and_run_id(monkeypatch):
    _, logs = _install(monkeypatch, [_obs("WIN")])
    calls = []

    class _Hooked:
        scene = "experiment"
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "calls": 0}

        def on_episode_start(self, spec, run_id):
            calls.append(("start", spec, run_id))

        def act(self, obs):
            return {"name": "ACTION1"}

        def on_episode_end(self, result, run_id):
            calls.append(("end", result, run_id))

    result = run_episode({"game_id": "ls20"}, _Hooked(), "run-hooks")

    assert calls[0] == ("start", {"game_id": "ls20"}, "run-hooks")
    assert calls[1][0] == "end" and calls[1][1] is result and calls[1][2] == "run-hooks"


def test_hook_exception_propagates(monkeypatch):
    _install(monkeypatch, [_obs("WIN")])

    class _Boom:
        scene = "experiment"

        def on_episode_start(self, spec, run_id):
            raise RuntimeError("hook boom")

        def act(self, obs):
            return {"name": "ACTION1"}

    with pytest.raises(RuntimeError, match="hook boom"):
        run_episode({"game_id": "ls20"}, _Boom(), "run-boom")
