"""make_baseline_policy 单测：构造校验/act 全路径/解析与确定性回退/usage 累计/异常透传。

llm_complete 全程 monkeypatch 为假函数（不发网络），并核验收到的实参。
"""

import logging

import pytest

from src.make_baseline_policy import make_baseline_policy as mbp
from src.make_baseline_policy.make_baseline_policy import (
    BASELINE_SAMPLING,
    ConfigError,
    make_baseline_policy,
)
from src.shared.llm_complete import LLMServiceError


def _obs(available=(0, 1, 2)) -> dict:
    """合法 FrameData 形态观测。"""
    return {
        "game_id": "ls20-016295f7601e",
        "state": "NOT_FINISHED",
        "frame": [[[0, 1], [1, 0]]],
        "levels_completed": 0,
        "win_levels": 254,
        "available_actions": list(available),
    }


class _FakeLLM:
    """按序吐回复文本；记录每次收到的 (messages, sampling, scene, model)。"""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def __call__(self, messages, sampling, scene, model=""):
        self.calls.append({"messages": messages, "sampling": dict(sampling), "scene": scene, "model": model})
        item = self.replies.pop(0)
        if isinstance(item, Exception):
            raise item
        return item, {"prompt_tokens": 3, "completion_tokens": 2, "latency_ms": 1, "attempt": 1}


def _policy(monkeypatch, replies, config=None):
    fake = _FakeLLM(replies)
    monkeypatch.setattr(mbp, "llm_complete", fake)
    return make_baseline_policy(config or {"scene": "experiment"}), fake


# ① 构造校验


def test_config_missing_scene_raises():
    with pytest.raises(ConfigError, match="缺少 scene"):
        make_baseline_policy({})


def test_config_bad_scene_raises():
    with pytest.raises(ConfigError, match=r"experiment\|submit"):
        make_baseline_policy({"scene": "eval"})


def test_config_bad_model_type_raises():
    with pytest.raises(ConfigError, match="model 必须是字符串"):
        make_baseline_policy({"scene": "submit", "model": 27})


def test_ok_config_defaults_and_sampling_logged(monkeypatch, caplog):
    fake = _FakeLLM([])
    monkeypatch.setattr(mbp, "llm_complete", fake)

    with caplog.at_level(logging.INFO, logger=mbp._LOGGER.name):
        policy = make_baseline_policy({"scene": "experiment"})

    assert policy.scene == "experiment"
    assert policy.model == ""
    assert policy.sampling == BASELINE_SAMPLING
    assert BASELINE_SAMPLING["temperature"] == 0.0  # 确定性采样钉死
    assert policy.name == "baseline"
    assert any("sampling" in r.message for r in caplog.records)  # 采样参数记入日志


# ② act：正常解析路径


def test_act_simple_action_parsed(monkeypatch):
    policy, fake = _policy(monkeypatch, ["I'll go ACTION3"])

    action = policy.act(_obs(available=(0, 1, 2, 3, 4)))

    assert action == {"name": "ACTION3"}
    # llm 收到的实参：固定提示词 + 默认采样 + 场景 + 模型名
    call = fake.calls[0]
    assert [m["role"] for m in call["messages"]] == ["system", "user"]
    assert call["sampling"] == BASELINE_SAMPLING
    assert call["scene"] == "experiment"
    assert call["model"] == ""


def test_act_action6_with_coords_parsed(monkeypatch):
    policy, _ = _policy(monkeypatch, ["ACTION6 12 34"])

    assert policy.act(_obs(available=(6,))) == {"name": "ACTION6", "x": 12, "y": 34}


# ③ 解析失败/非法 → 确定性回退


def test_act_garbage_reply_falls_back_to_first_available(monkeypatch):
    policy, _ = _policy(monkeypatch, ["no idea what to do"])

    assert policy.act(_obs(available=(2, 3))) == {"name": "ACTION2"}


def test_act_action6_missing_coords_falls_back(monkeypatch):
    policy, _ = _policy(monkeypatch, ["ACTION6 somewhere"])

    # 坐标缺失 → 解析失败回退；available 首项=2，回退 ACTION2（非 ACTION6）
    assert policy.act(_obs(available=(2, 6))) == {"name": "ACTION2"}


def test_act_action_outside_available_falls_back(monkeypatch):
    policy, _ = _policy(monkeypatch, ["ACTION5 please"])

    assert policy.act(_obs(available=(0, 1))) == {"name": "RESET"}  # 首个可用=0→RESET


def test_act_empty_available_falls_back_to_reset(monkeypatch):
    policy, _ = _policy(monkeypatch, ["ACTION1"])

    assert policy.act(_obs(available=())) == {"name": "RESET"}


def test_act_same_reply_same_action_deterministic(monkeypatch):
    policy, _ = _policy(monkeypatch, ["ACTION6 63 0", "ACTION6 63 0"])

    a = policy.act(_obs(available=(6,)))
    b = policy.act(_obs(available=(6,)))

    assert a == b == {"name": "ACTION6", "x": 63, "y": 0}


# ④ usage 累计与异常透传


def test_act_accumulates_total_usage(monkeypatch):
    policy, _ = _policy(monkeypatch, ["ACTION1", "ACTION2"])

    policy.act(_obs())
    policy.act(_obs())

    assert policy.total_usage == {"prompt_tokens": 6, "completion_tokens": 4, "calls": 2}


def test_act_llm_experiment_error_propagates(monkeypatch):
    policy, _ = _policy(monkeypatch, [LLMServiceError("vLLM down")])

    with pytest.raises(LLMServiceError, match="vLLM down"):
        policy.act(_obs())


def test_model_config_forwarded_to_llm(monkeypatch):
    policy, fake = _policy(monkeypatch, ["ACTION1"], {"scene": "submit", "model": "qwen3-32b"})

    policy.act(_obs())

    assert fake.calls[0]["model"] == "qwen3-32b"
