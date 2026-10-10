"""render_obs 单测：稳定序列化、中文/嵌套、截断边界与错误分支。

夹具为 ARC-AGI-3 FrameDataRaw 归一化后的真形态 dict（六必填字段齐备，
见 references/arc_agi_3_sdk.md；guid/action_input/full_reset 可选不入）。
"""

import json

import pytest

from src.shared import render_obs as ro
from src.shared.render_obs import ObsFormatError, render_obs

SUFFIX = "…[truncated]"  # 与规格钉死的尾标字面量一致（长度 12）


def _dumps(obs):
    """规格要求的参考序列化格式，独立重算以钉死输出格式。"""
    return json.dumps(obs, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _frame_obs(pad: int = 0, **extra) -> dict:
    """构造合法观测 dict：六必填字段 + 长度可控的填充键 "k"（截断测试用）。"""
    obs = {
        "game_id": "ls20-016295f7601e",
        "state": "NOT_FINISHED",
        "frame": [[[0, 1], [1, 0]]],
        "levels_completed": 0,
        "win_levels": 254,
        "available_actions": [0, 1, 2],
        "k": "x" * pad,
    }
    obs.update(extra)
    return obs


def _obs_of_len(n):
    """构造序列化后恰好 n 字符的合法观测 dict（pad 定长可控）。"""
    return _frame_obs(pad=n - len(_dumps(_frame_obs(pad=0))))


# ① 稳定序列化：键序无关、两次调用逐字节相同


def test_key_order_independent_byte_identical():
    a = _frame_obs()
    b = {k: a[k] for k in reversed(list(a))}  # 同内容、不同插入序
    b["frame"] = [[[1, 0], [0, 1]]]
    a2 = _frame_obs(frame=[[[1, 0], [0, 1]]])

    out_a = render_obs(a2, 10_000)
    out_b = render_obs(b, 10_000)

    assert out_a == out_b
    assert out_a == _dumps(a2)  # 键递归排序 + 紧凑分隔符的确切格式
    assert render_obs(a2, 10_000) == out_a  # 同输入两次调用逐字节相同


# ② 中文与嵌套结构（可选字段/自定键可携带中文，原样保留）


def test_chinese_and_nested_preserved():
    obs = _frame_obs(备注="左移", 网格注={"提示": "「中文」✓", "meta": {"t": None}})
    out = render_obs(obs, 10_000)

    assert out == _dumps(obs)
    assert "左移" in out
    assert "\\" not in out  # ensure_ascii=False：无 \u 转义；紧凑分隔符：无转义引号


# ③ 截断边界：恰好=预算 / 超 1 / 远超 / 预算装不下尾标


def test_truncation_exact_fit_returns_full_text():
    text = _dumps(_obs_of_len(500))
    assert len(text) == 500

    out = render_obs(_obs_of_len(500), 500)

    assert out == text
    assert len(out) == 500
    assert not out.endswith(SUFFIX)


def test_truncation_over_by_one_suffix_at_exact_budget():
    obs = _obs_of_len(501)
    text = _dumps(obs)

    out = render_obs(obs, 500)

    assert len(out) == 500
    assert out.endswith(SUFFIX)
    assert out[: 500 - len(SUFFIX)] == text[: 500 - len(SUFFIX)]  # 头部保留


def test_truncation_far_over_suffix_at_exact_budget():
    obs = _obs_of_len(2000)

    out = render_obs(obs, 120)

    assert len(out) == 120
    assert out.endswith(SUFFIX)
    assert out[: 120 - len(SUFFIX)] == _dumps(obs)[: 120 - len(SUFFIX)]


def test_truncation_budget_below_suffix_length_still_hard_capped():
    out = render_obs(_obs_of_len(600), 5)  # 预算 5 < 尾标 12

    assert len(out) == 5  # budget 恒为硬上限
    assert out == SUFFIX[:5]


# ④ 非 dict 输入 → ObsFormatError


@pytest.mark.parametrize("bad", [None, 42, "obs", [1, 2], [("a", 1)]])
def test_non_dict_raises_obs_format_error(bad):
    with pytest.raises(ObsFormatError):
        render_obs(bad, 1000)


# ⑤ REQUIRED_FIELDS：实核回填值；逐字段缺失 → ObsFormatError 带字段名


def test_required_fields_backfilled_to_frame_shape():
    assert ro.REQUIRED_FIELDS == (
        "game_id",
        "state",
        "frame",
        "levels_completed",
        "win_levels",
        "available_actions",
    )
    assert render_obs(_frame_obs(), 10_000) == _dumps(_frame_obs())


def test_empty_or_partial_dict_rejected():
    with pytest.raises(ObsFormatError):
        render_obs({}, 1000)


@pytest.mark.parametrize("field", ro.REQUIRED_FIELDS)
def test_missing_each_required_field_raises_with_field_name(field):
    obs = _frame_obs()
    del obs[field]

    with pytest.raises(ObsFormatError) as excinfo:
        render_obs(obs, 10_000)

    assert field in str(excinfo.value)


# ⑥ budget <= 0 → ValueError（参数错误，非观测格式错误）


@pytest.mark.parametrize("budget", [0, -1, -100])
def test_nonpositive_budget_raises_plain_value_error(budget):
    with pytest.raises(ValueError) as excinfo:
        render_obs(_frame_obs(), budget)

    assert not isinstance(excinfo.value, ObsFormatError)  # 参数错误，非观测格式错误
