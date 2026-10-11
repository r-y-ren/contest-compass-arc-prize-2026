"""estimate_difficulty 单测：公式分量/边界钳制/空记录低置信/纯函数/脏记录容错。"""

from src.make_curriculum_policy.estimate_difficulty import (
    DEFAULT_DIFFICULTY,
    estimate_difficulty,
)


def _rec(outcome="GAME_OVER", steps=10):
    return {"outcome": outcome, "steps": steps}


# ① 公式分量：成功率项 + 步数项


def test_all_win_few_steps_near_zero():
    d, low = estimate_difficulty([_rec("WIN", 0), _rec("WIN", 0)])
    assert d == 0.0 and not low


def test_all_lose_low_steps_one():
    d, low = estimate_difficulty([_rec("GAME_OVER", 0), _rec("STEP_LIMIT", 0)])
    assert d == 1.0 and not low


def test_half_win_average_steps_exact_formula():
    # success_rate=0.5, avg_steps=40 → 0.5 + 0.5*(40/100) = 0.7
    d, _ = estimate_difficulty([_rec("WIN", 10), _rec("GAME_OVER", 70)])
    assert d == 0.5 + 0.5 * (40 / 100)


def test_step_term_clamped_at_cap():
    # avg_steps=500 超上限 → 步数项钳到 0.5，难度 = 1.5
    d, _ = estimate_difficulty([_rec("GAME_OVER", 500)])
    assert d == 1.5


# ② 空记录 → 默认难度 + 低置信


def test_empty_history_default_low_confidence():
    assert estimate_difficulty([]) == (DEFAULT_DIFFICULTY, True)


# ③ 纯函数：不修改输入


def test_pure_function_does_not_mutate_input():
    records = [_rec("WIN", 5), _rec("GAME_OVER", 15)]
    snapshot = [dict(r) for r in records]

    first = estimate_difficulty(records)
    second = estimate_difficulty(records)

    assert first == second
    assert records == snapshot


# ④ 脏记录容错：非 dict 元素按零值计，缺 steps 按 0


def test_dirty_records_tolerated():
    d, low = estimate_difficulty(["junk", {"outcome": "WIN"}, None])

    # 仅第二条记 WIN：success_rate=1/3；steps 全 0
    assert abs(d - (1 - 1 / 3)) < 1e-9
    assert not low


def test_missing_steps_counts_as_zero():
    d, _ = estimate_difficulty([{"outcome": "WIN"}])
    assert d == 0.0  # 全胜 + 零步
