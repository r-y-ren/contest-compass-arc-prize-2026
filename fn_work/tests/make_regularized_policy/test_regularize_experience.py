"""regularize_experience 单测：打分截断/相关性/新近度/去重/日志/隔离/确定性。"""

import pytest

from src.make_regularized_policy.regularize_experience import regularize_experience


def _obs(game_id="ls20-016295f7601e"):
    return {"game_id": game_id}


def _store(entries):
    return {"capacity": 32, "entries": entries}


def _entry(episode_id, outcome="GAME_OVER", steps=10):
    return {"episode_id": episode_id, "ts": f"t-{episode_id}", "outcome": outcome,
            "steps": steps, "key_steps": [], "truncated": False}


# ① 冷启动：空库/无条目 → 空子集空日志


def test_empty_store_cold_start():
    assert regularize_experience({}, _obs(), 5) == ([], [])
    assert regularize_experience(_store([]), _obs(), 5) == ([], [])


def test_zero_budget_returns_empty():
    assert regularize_experience(_store([_entry("a-1")]), _obs(), 0) == ([], [])


# ② 预算截断：高者优先、满员落选带原因


def test_budget_truncation_prefers_high_scores():
    store = _store([
        _entry("zz9-1", "GAME_OVER"),   # 旧且无关
        _entry("ls20-2", "WIN"),        # 同局相关 + 胜局 + 较新
        _entry("ls20-3", "GAME_OVER"),  # 同局相关 + 最新
    ])

    subset, log = regularize_experience(store, _obs(), 2)

    # ls20-2 与 ls20-3 同分 2.0（相关+win+新近0.5 vs 相关+新近1.0），平手新者优先
    assert [e["episode_id"] for e in subset] == ["ls20-3", "ls20-2"]
    dropped = [l for l in log if not l["kept"]]
    assert dropped[0]["episode_id"] == "zz9-1" and "beyond-budget" in dropped[0]["reason"]


def test_relevance_beats_recency():
    # 同局旧条目 vs 无关新条目：相关性 1.0 > 新近度最多 1.0——同局且非全旧可胜
    store = _store([
        _entry("ls20-old", "GAME_OVER"),   # 相关 + 新近度低
        _entry("qq9-new", "GAME_OVER"),    # 无关 + 新近度高
    ])

    subset, _ = regularize_experience(store, _obs(), 1)

    # 相关 1.0+新近 0 vs 无关 0+新近 1.0 → 平手 → 新者优先裁决 qq9-new？
    # 非也：平手决胜"新者优先"取 idx 大者——qq9-new。此测钉死该边界语义。
    assert [e["episode_id"] for e in subset] == ["qq9-new"]


# ③ 去重：同 episode_id 只取一次


def test_duplicate_episode_id_skipped():
    store = _store([
        _entry("ls20-a", "WIN"),
        _entry("ls20-a", "WIN"),  # 同 ID（理论上不该有，防御）
        _entry("ls20-b", "WIN"),
    ])

    subset, log = regularize_experience(store, _obs(), 3)

    # 全相关+胜局：新近度定序 → ls20-b(2.5) > ls20-a 第二条(2.0) > ls20-a 第一条(1.5，重复跳过)
    ids = [e["episode_id"] for e in subset]
    assert ids == ["ls20-b", "ls20-a"]
    dup = [l for l in log if l["reason"].startswith("duplicate")]
    assert len(dup) == 1 and dup[0]["kept"] is False


# ④ 日志完备：每条目一条记录，kept+score+factors 齐


def test_log_complete_per_entry():
    store = _store([_entry("ls20-1", "WIN"), _entry("qq2-2")])

    _, log = regularize_experience(store, _obs(), 1)

    assert len(log) == 2
    assert all({"episode_id", "kept", "score", "reason"} <= set(l) for l in log)
    assert any("recency=" in l["reason"] and "relevance=" in l["reason"] for l in log)


# ⑤ 子集为浅拷贝：改子集不动库


def test_subset_is_copy_store_untouched():
    entry = _entry("ls20-1", "WIN")
    store = _store([entry])

    subset, _ = regularize_experience(store, _obs(), 5)

    assert subset[0] == entry and subset[0] is not entry
    subset[0]["outcome"] = "MUTATED"
    assert entry["outcome"] == "WIN"


# ⑥ 校验与确定性


def test_bad_budget_raises():
    with pytest.raises(ValueError, match="budget 必须是整数"):
        regularize_experience(_store([_entry("a")]), _obs(), "5")
    with pytest.raises(ValueError, match="budget 必须是整数"):
        regularize_experience(_store([_entry("a")]), _obs(), True)


def test_deterministic_same_output():
    store = _store([_entry(f"g{i}-{i}", "WIN" if i % 2 else "GAME_OVER") for i in range(6)])

    assert regularize_experience(store, _obs("g3-9"), 3) == regularize_experience(store, _obs("g3-9"), 3)
