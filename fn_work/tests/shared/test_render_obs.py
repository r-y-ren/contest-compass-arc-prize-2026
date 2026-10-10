"""render_obs 单测：稳定序列化、中文/嵌套、截断边界与错误分支。"""

import json

import pytest

from src.shared import render_obs as ro
from src.shared.render_obs import ObsFormatError, render_obs

SUFFIX = "…[truncated]"  # 与规格钉死的尾标字面量一致（长度 12）


def _dumps(obs):
    """规格要求的参考序列化格式，独立重算以钉死输出格式。"""
    return json.dumps(obs, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _obs_of_len(n):
    """构造序列化后恰好 n 字符的观测 dict（{"k":"x"*m} 定长可控）。"""
    return {"k": "x" * (n - len(_dumps({"k": ""})))}


# ① 稳定序列化：键序无关、两次调用逐字节相同


def test_key_order_independent_byte_identical():
    a = {"b": 2, "a": 1, "c": {"z": [3, 2, 1], "y": None}}
    b = {"c": {"y": None, "z": [3, 2, 1]}, "a": 1, "b": 2}  # 同内容、不同插入序

    out_a = render_obs(a, 1000)
    out_b = render_obs(b, 1000)

    assert out_a == out_b
    assert out_a == _dumps(a)  # 键递归排序 + 紧凑分隔符的确切格式
    assert render_obs(a, 1000) == out_a  # 同输入两次调用逐字节相同


# ② 中文与嵌套结构


def test_chinese_and_nested_preserved():
    obs = {
        "动作": "左移",
        "网格": [[0, 1], [1, 0]],
        "嵌套": {"提示": "「中文」✓", "meta": {"t": None}},
    }
    out = render_obs(obs, 10_000)

    assert out == _dumps(obs)
    assert "左移" in out
    assert "\\" not in out  # ensure_ascii=False：无 \u 转义；紧凑分隔符：无转义引号


# ③ 截断边界：恰好=预算 / 超 1 / 远超 / 预算装不下尾标


def test_truncation_exact_fit_returns_full_text():
    text = _dumps(_obs_of_len(50))
    assert len(text) == 50

    out = render_obs(_obs_of_len(50), 50)

    assert out == text
    assert len(out) == 50
    assert not out.endswith(SUFFIX)


def test_truncation_over_by_one_suffix_at_exact_budget():
    obs = _obs_of_len(51)
    text = _dumps(obs)

    out = render_obs(obs, 50)

    assert len(out) == 50
    assert out.endswith(SUFFIX)
    assert out[: 50 - len(SUFFIX)] == text[: 50 - len(SUFFIX)]  # 前缀保留


def test_truncation_far_over_suffix_at_exact_budget():
    obs = _obs_of_len(1000)

    out = render_obs(obs, 80)

    assert len(out) == 80
    assert out.endswith(SUFFIX)
    assert out[: 80 - len(SUFFIX)] == _dumps(obs)[: 80 - len(SUFFIX)]


def test_truncation_budget_below_suffix_length_still_hard_capped():
    out = render_obs(_obs_of_len(100), 5)  # 预算 5 < 尾标 12

    assert len(out) == 5  # budget 恒为硬上限
    assert out == SUFFIX[:5]


# ④ 非 dict 输入 → ObsFormatError


@pytest.mark.parametrize("bad", [None, 42, "obs", [1, 2], [("a", 1)]])
def test_non_dict_raises_obs_format_error(bad):
    with pytest.raises(ObsFormatError):
        render_obs(bad, 100)


# ⑤ REQUIRED_FIELDS：注入后缺字段 → ObsFormatError 带字段名；默认空集合放行


def test_default_required_fields_empty_and_accepts_any_dict():
    assert ro.REQUIRED_FIELDS == ()
    assert render_obs({}, 100) == "{}"


def test_missing_required_field_raises_with_field_name(monkeypatch):
    monkeypatch.setattr(ro, "REQUIRED_FIELDS", ("grid", "step"))

    with pytest.raises(ObsFormatError) as excinfo:
        render_obs({"grid": [[0]], "other": 1}, 100)

    assert "step" in str(excinfo.value)


def test_required_fields_all_present_passes(monkeypatch):
    monkeypatch.setattr(ro, "REQUIRED_FIELDS", ("grid", "step"))

    obs = {"step": 7, "grid": [1], "z": 0}
    assert render_obs(obs, 100) == _dumps(obs)


# ⑥ budget <= 0 → ValueError


@pytest.mark.parametrize("budget", [0, -1, -100])
def test_nonpositive_budget_raises_plain_value_error(budget):
    with pytest.raises(ValueError) as excinfo:
        render_obs({"a": 1}, budget)

    assert not isinstance(excinfo.value, ObsFormatError)  # 参数错误，非观测格式错误
