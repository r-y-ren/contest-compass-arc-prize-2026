"""update_experience_store 单测：入库字段/截断/容量淘汰/不可变性/空库/校验。"""

import pytest

from src.make_regularized_policy.update_experience_store import (
    DEFAULT_CAPACITY,
    MAX_KEY_STEPS,
    update_experience_store,
)


def _result(episode_id="ls20-x", outcome="WIN", steps=5):
    return {"episode_id": episode_id, "outcome": outcome, "steps": steps}


# ① 入库：字段齐全（时间戳/局 ID/结局/步数/关键步）


def test_entry_fields_complete():
    store = update_experience_store(_result(), [{"step": 1, "a": "ACTION1"}], {})

    assert store["capacity"] == DEFAULT_CAPACITY
    (entry,) = store["entries"]
    assert entry["episode_id"] == "ls20-x"
    assert entry["outcome"] == "WIN"
    assert entry["steps"] == 5
    assert entry["key_steps"] == [{"step": 1, "a": "ACTION1"}]
    assert entry["truncated"] is False
    assert "T" in entry["ts"]  # ISO8601


# ② 关键步超限 → 截断 + 标志


def test_key_steps_truncated_with_flag():
    many = [{"i": i} for i in range(MAX_KEY_STEPS + 7)]

    store = update_experience_store(_result(), many, {})

    (entry,) = store["entries"]
    assert len(entry["key_steps"]) == MAX_KEY_STEPS
    assert entry["truncated"] is True
    assert entry["key_steps"][0] == {"i": 0}  # 保头部


def test_key_steps_at_limit_not_truncated():
    exact = [{"i": i} for i in range(MAX_KEY_STEPS)]

    store = update_experience_store(_result(), exact, {})

    assert store["entries"][0]["truncated"] is False


# ③ 容量淘汰：超容量从最旧端淘汰


def test_capacity_evicts_oldest():
    store = {"capacity": 2, "entries": [
        {"episode_id": "old-1"}, {"episode_id": "old-2"},
    ]}

    updated = update_experience_store(_result("new-3"), [], store)

    assert [e["episode_id"] for e in updated["entries"]] == ["old-2", "new-3"]


# ④ 只写不改旧条目：返回新对象，旧库逐字节不变


def test_returns_new_object_old_untouched():
    old_entry = {"episode_id": "keep", "key_steps": [{"x": 1}], "truncated": False}
    store = {"capacity": 8, "entries": [old_entry]}

    updated = update_experience_store(_result("new"), [], store)

    assert updated is not store
    assert updated["entries"][0] is old_entry  # 旧条目对象原样复用，零改动
    assert store["entries"] == [old_entry]


# ⑤ 空库起库 / 脏 store 校验


def test_empty_store_defaults():
    store = update_experience_store(_result(), [], {})
    assert store["capacity"] == DEFAULT_CAPACITY and len(store["entries"]) == 1


def test_none_key_steps_tolerated():
    store = update_experience_store(_result(), None, {})
    assert store["entries"][0]["key_steps"] == []


def test_bad_capacity_raises():
    with pytest.raises(ValueError, match="capacity 必须是正整数"):
        update_experience_store(_result(), [], {"capacity": 0})


def test_non_dict_store_raises():
    with pytest.raises(TypeError, match="store 必须是 dict"):
        update_experience_store(_result(), [], ["not", "a", "dict"])
