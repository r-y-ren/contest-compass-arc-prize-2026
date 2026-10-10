"""build_baseline_prompt 单测：结构/模板常量/视图一致性/确定性/异常透传/预算接线。"""

import pytest

from src.make_baseline_policy.build_baseline_prompt import (
    BASELINE_SYSTEM_PROMPT,
    OBS_BUDGET,
    build_baseline_prompt,
)
from src.shared.render_obs import ObsFormatError, render_obs


def _frame_obs(pad: int = 0) -> dict:
    """合法 FrameData 形态观测（六必填字段），pad 控制序列化长度。"""
    return {
        "game_id": "ls20-016295f7601e",
        "state": "NOT_FINISHED",
        "frame": [[[0, 1], [1, 0]]],
        "levels_completed": 0,
        "win_levels": 254,
        "available_actions": [0, 1, 2],
        "k": "x" * pad,
    }


# ① 结构：恰两条消息，system 在前 user 在后


def test_two_messages_system_then_user():
    messages = build_baseline_prompt(_frame_obs())

    assert [m["role"] for m in messages] == ["system", "user"]
    assert len(messages) == 2


# ② 模板常量：system 恒为 BASELINE_SYSTEM_PROMPT，不含观测内容


def test_system_content_is_constant_template():
    obs = _frame_obs()
    messages = build_baseline_prompt(obs)

    assert messages[0]["content"] == BASELINE_SYSTEM_PROMPT
    assert "ls20" not in messages[0]["content"]  # 观测不泄漏进模板


# ③ 视图一致性：user 内容恰为 render_obs(obs, OBS_BUDGET)


def test_user_view_matches_render_obs_with_module_budget():
    obs = _frame_obs()

    messages = build_baseline_prompt(obs)

    assert messages[1]["content"] == render_obs(obs, OBS_BUDGET)


# ④ 确定性：同输入两次调用逐字节相同


def test_deterministic_same_input_same_output():
    obs = _frame_obs()

    assert build_baseline_prompt(obs) == build_baseline_prompt(obs)


# ⑤ render_obs 异常透传：非 dict / 缺必填字段原样抛出


def test_render_obs_errors_propagate():
    with pytest.raises(ObsFormatError):
        build_baseline_prompt({"game_id": "x"})  # 缺其余必填字段

    with pytest.raises(ObsFormatError):
        build_baseline_prompt("not a dict")


# ⑥ 预算接线：超大观测触发截断，user 内容恰为 OBS_BUDGET 字符


def test_budget_wired_truncation_engages_for_huge_obs():
    obs = _frame_obs(pad=50_000)

    messages = build_baseline_prompt(obs)

    assert len(messages[1]["content"]) == OBS_BUDGET
    assert messages[1]["content"].endswith("…[truncated]")


# ⑦ 模板动作协议守卫：模板必须含动作协议关键词（防模板漂移破坏下游解析）


def test_template_mentions_action_protocol():
    for keyword in ("RESET", "ACTION1", "ACTION5", "ACTION6", "ACTION7", "available_actions"):
        assert keyword in BASELINE_SYSTEM_PROMPT
