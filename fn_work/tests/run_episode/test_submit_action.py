"""submit_action 单测：假 env 队列（密闭），真 GameAction 枚举转换。"""

import pytest
from arcengine import GameAction

from src.make_baseline_policy.make_baseline_policy import ACTION_NAMES
from src.run_episode._frame import EnvError
from src.run_episode.submit_action import (
    LEGAL_ACTION_NAMES,
    STEP_FAILED_STATE,
    IllegalActionError,
    submit_action,
)


def _obs(state="NOT_FINISHED"):
    return {
        "game_id": "ls20-016295f7601e",
        "state": state,
        "frame": [[[0, 1]]],
        "levels_completed": 0,
        "win_levels": 254,
        "available_actions": [1, 2],
    }


class _FakeEnv:
    """按序吐 step 结果（dict / None / Exception）；记录每次收到的 (action, data)。"""

    def __init__(self, results):
        self.results = list(results)
        self.calls = []

    def step(self, action, data=None):
        self.calls.append((action, data))
        item = self.results.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


# ① 正常提交：simple / 大小写不敏感 / ACTION6 坐标


def test_simple_action_converted_to_enum_and_passed():
    env = _FakeEnv([_obs()])

    out = submit_action(env, {"name": "ACTION3"}, "experiment")

    assert env.calls == [(GameAction.ACTION3, None)]
    assert out["state"] == "NOT_FINISHED"


def test_lowercase_name_normalized():
    env = _FakeEnv([_obs()])

    submit_action(env, {"name": "reset"}, "experiment")

    assert env.calls[0][0] is GameAction.RESET


def test_action6_coords_passed_as_data():
    env = _FakeEnv([_obs()])

    submit_action(env, {"name": "ACTION6", "x": 12, "y": 34}, "experiment")

    assert env.calls == [(GameAction.ACTION6, {"x": 12, "y": 34})]


def test_boundary_coords_0_and_63_accepted():
    env = _FakeEnv([_obs(), _obs()])

    submit_action(env, {"name": "ACTION6", "x": 0, "y": 63}, "experiment")
    submit_action(env, {"name": "ACTION6", "x": 63, "y": 0}, "experiment")

    assert len(env.calls) == 2


# ② 结构校验 → IllegalActionError 带错误码


def test_missing_name_raises_invalid_action():
    with pytest.raises(IllegalActionError) as excinfo:
        submit_action(_FakeEnv([]), {"x": 1}, "experiment")
    assert excinfo.value.code == "INVALID_ACTION"


def test_unknown_name_raises_invalid_action():
    with pytest.raises(IllegalActionError) as excinfo:
        submit_action(_FakeEnv([]), {"name": "ACTION9"}, "experiment")
    assert excinfo.value.code == "INVALID_ACTION"


def test_action6_missing_coords_raises():
    with pytest.raises(IllegalActionError) as excinfo:
        submit_action(_FakeEnv([]), {"name": "ACTION6"}, "experiment")
    assert excinfo.value.code == "INVALID_COORDS"


def test_action6_bool_or_nonint_coords_raises():
    with pytest.raises(IllegalActionError) as excinfo:
        submit_action(_FakeEnv([]), {"name": "ACTION6", "x": True, "y": 0}, "experiment")
    assert excinfo.value.code == "INVALID_COORDS"


def test_action6_out_of_range_coords_raises():
    with pytest.raises(IllegalActionError) as excinfo:
        submit_action(_FakeEnv([]), {"name": "ACTION6", "x": 64, "y": 0}, "experiment")
    assert excinfo.value.code == "COORDS_OUT_OF_RANGE"


# ③ step 失败归一：experiment 抛 / submit 哨兵；异常包装；未知 scene


def test_step_none_experiment_raises_env_error():
    env = _FakeEnv([None])

    with pytest.raises(EnvError, match="实验态失败即停"):
        submit_action(env, {"name": "ACTION1"}, "experiment")


def test_step_none_submit_returns_sentinel_not_raise():
    env = _FakeEnv([None])

    out = submit_action(env, {"name": "ACTION1"}, "submit")

    assert out == {"state": STEP_FAILED_STATE}


def test_step_raises_wrapped_env_error():
    env = _FakeEnv([RuntimeError("transport boom")])

    with pytest.raises(EnvError, match="transport boom"):
        submit_action(env, {"name": "ACTION1"}, "submit")  # 两场景包装一致，不吞


def test_unknown_scene_rejected():
    with pytest.raises(ValueError, match="未知 scene"):
        submit_action(_FakeEnv([]), {"name": "ACTION1"}, "eval")


# ④ 跨模块一致性守卫：动作名集合与 make_baseline_policy 的编号表不漂移


def test_legal_names_match_baseline_action_names_table():
    assert LEGAL_ACTION_NAMES == set(ACTION_NAMES)
