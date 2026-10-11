"""select_experience_source 单测：先易后难/利用计数/平手决胜/理由串/池校验/确定性。"""

import pytest

from src.make_curriculum_policy.select_experience_source import (
    SELECTION_LAMBDA,
    CurriculumError,
    select_experience_source,
)


# ① 先易后难：无历史时选难度最低者


def test_picks_lowest_difficulty_without_history():
    source, reason = select_experience_source({"a": 0.8, "b": 0.2, "c": 1.5}, [])

    assert source == "b"
    assert "difficulty=0.200" in reason and "selected=0" in reason


# ② 利用计数：难度最低者被过度选择后让位


def test_exploitation_count_penalizes_overused_source():
    # a 难度 0.2 已被选 2 次 → score=0.2+1.0=1.2；b 难度 0.5 未选 → score=0.5
    source, _ = select_experience_source({"a": 0.2, "b": 0.5}, ["a", "a"])

    assert source == "b"


def test_lambda_boundary_exact_tie_by_count():
    # a: 0.4+0.5=0.9；b: 0.9+0=0.9 → 平手，比 (难度, 计数, id)：a 难度低者胜
    source, _ = select_experience_source({"b": 0.9, "a": 0.4}, ["a"])

    assert source == "a"


# ③ 平手决胜链：难度同 → 计数少者 → ID 字典序


def test_tie_break_by_count_then_id():
    same = {"x": 0.5, "y": 0.5}
    assert select_experience_source(same, [])[0] == "x"  # 计数同 → 字典序

    assert select_experience_source(same, ["x"])[0] == "y"  # x 已选 → y 让位


# ④ 理由串可解释：含三要素与规则说明


def test_reason_carries_rule_and_factors():
    _, reason = select_experience_source({"a": 0.3}, ["a", "a", "b"])

    assert f"min(difficulty+{SELECTION_LAMBDA}*selected)" in reason
    assert "pool=1" in reason


# ⑤ 池校验：空表/脏表 → CurriculumError；合法表里有脏值只跳过


def test_empty_pool_raises():
    with pytest.raises(CurriculumError, match="经验源池为空"):
        select_experience_source({}, [])


def test_all_invalid_entries_raises():
    with pytest.raises(CurriculumError):
        select_experience_source({"a": "hard", "b": None}, [])


def test_invalid_entries_skipped_valid_used():
    source, _ = select_experience_source({"a": "hard", "b": 0.7}, [])

    assert source == "b"


def test_bool_difficulty_rejected_as_invalid():
    # bool 是 int 子类，不得混入难度表当 0/1 用
    with pytest.raises(CurriculumError):
        select_experience_source({"a": True}, [])


# ⑥ 确定性：同输入同输出


def test_deterministic_same_output():
    table = {"a": 0.6, "b": 0.6, "c": 0.1}
    history = ["c", "a"]

    assert select_experience_source(table, history) == select_experience_source(table, history)
