"""connect_env 单测：sys.modules 注入假 arc_agi（密闭，不触网），含真 FrameDataRaw 归一化。"""

import json
import sys
import types

import numpy as np
import pytest
from arcengine import GameState, FrameDataRaw

from src.run_episode._frame import EnvError, normalize_obs
from src.run_episode.connect_env import connect_env


class _FakeEnv:
    def __init__(self, reset_result):
        self._reset_result = reset_result
        self.reset_called = 0

    def reset(self):
        self.reset_called += 1
        item = self._reset_result
        if isinstance(item, Exception):
            raise item
        return item


class _FakeArcade:
    """记录 make 实参；make_result 为 _FakeEnv / None / Exception。"""

    instances = []

    def __init__(self, *args, **kwargs):
        self.make_calls = []
        _FakeArcade.instances.append(self)

    def make(self, game_id, seed=0, **kwargs):
        self.make_calls.append({"game_id": game_id, "seed": seed})
        result = self.make_result
        if isinstance(result, Exception):
            raise result
        return result


def _install_fake_arcade(monkeypatch, reset_result, make_returns_env=True):
    """注入假 arc_agi 模块；make 恒返回同一 env（或 None），reset 吐 reset_result。"""
    _FakeArcade.instances = []
    env = _FakeEnv(reset_result)
    _FakeArcade.make_result = env if make_returns_env else None

    fake_mod = types.ModuleType("arc_agi")
    fake_mod.Arcade = _FakeArcade
    monkeypatch.setitem(sys.modules, "arc_agi", fake_mod)
    return _FakeArcade, env


def _frame_raw(state=GameState.NOT_FINISHED, available=(0, 1)):
    raw = FrameDataRaw(
        game_id="ls20-016295f7601e",
        state=state,
        levels_completed=3,
        win_levels=254,
        available_actions=list(available),
    )
    raw.frame = [np.array([[0, 15], [7, 8]], dtype=int)]
    return raw


# ① 正常路径：make + reset 成功，返回 (env, 归一化观测)


def test_ok_returns_env_and_normalized_obs(monkeypatch):
    _, env = _install_fake_arcade(monkeypatch, _frame_raw())

    handle, obs = connect_env({"game_id": "ls20", "seed": 42})

    assert handle is env
    assert env.reset_called == 1
    assert obs["game_id"] == "ls20-016295f7601e"
    assert obs["state"] == "NOT_FINISHED"  # 枚举已取值
    assert obs["levels_completed"] == 3
    assert obs["win_levels"] == 254
    assert obs["available_actions"] == [0, 1]
    assert obs["frame"] == [[[0, 15], [7, 8]]]  # numpy → list
    json.dumps(obs)  # 归一化结果必须可 JSON 序列化


def test_ok_seed_forwarded_and_defaults(monkeypatch):
    arcade_cls, _ = _install_fake_arcade(monkeypatch, _frame_raw())

    connect_env({"game_id": "ls20"})

    assert arcade_cls.instances[-1].make_calls == [{"game_id": "ls20", "seed": 0}]


# ② spec 校验


def test_spec_missing_game_id_raises(monkeypatch):
    _install_fake_arcade(monkeypatch, _frame_raw())

    with pytest.raises(EnvError, match="缺 game_id"):
        connect_env({"seed": 1})


def test_spec_non_int_seed_raises(monkeypatch):
    _install_fake_arcade(monkeypatch, _frame_raw())

    with pytest.raises(EnvError, match="seed 必须是整数"):
        connect_env({"game_id": "ls20", "seed": "7"})


# ③ SDK 失败三态：make None / reset None / SDK 抛异常 → EnvError 带局 ID


def test_make_returns_none_raises_with_game_id(monkeypatch):
    _install_fake_arcade(monkeypatch, _frame_raw(), make_returns_env=False)

    with pytest.raises(EnvError, match=r"make 返回 None.*ls20"):
        connect_env({"game_id": "ls20"})


def test_reset_returns_none_raises(monkeypatch):
    _install_fake_arcade(monkeypatch, None)

    with pytest.raises(EnvError, match="reset 返回 None"):
        connect_env({"game_id": "ls20"})


def test_sdk_exception_wrapped_with_game_id(monkeypatch):
    _FakeArcade.instances = []

    class _BoomArcade(_FakeArcade):
        def __init__(self, *a, **k):
            raise RuntimeError("arcade down")

    fake_mod = types.ModuleType("arc_agi")
    fake_mod.Arcade = _BoomArcade
    monkeypatch.setitem(sys.modules, "arc_agi", fake_mod)

    with pytest.raises(EnvError, match=r"SDK 环境初始化失败（ls20-abc）.*RuntimeError"):
        connect_env({"game_id": "ls20-abc"})


# ④ normalize_obs 补充：dict 透传 / 非法类型 / action_input 裁剪


def test_normalize_obs_passthrough_dict():
    obs = {"game_id": "g", "state": "WIN", "frame": [], "levels_completed": 1,
           "win_levels": 2, "available_actions": []}
    assert normalize_obs(obs) == obs


def test_normalize_obs_rejects_unknown_type():
    with pytest.raises(EnvError, match="既非 FrameDataRaw 也非 dict"):
        normalize_obs("junk")


def test_normalize_obs_strips_reasoning(monkeypatch):
    raw = _frame_raw()
    raw.action_input.reasoning = {"big": "blob"}

    obs = normalize_obs(raw)

    assert set(obs["action_input"].keys()) == {"id", "data"}
