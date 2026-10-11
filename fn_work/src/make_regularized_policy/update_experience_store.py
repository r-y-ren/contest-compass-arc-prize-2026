"""经验库更新：一局结局 + 关键步摘要入库（责任文档 R4，RRSI 思路记忆层降级件）。

经验库形态（规范化 dict）：
    {"capacity": int, "entries": [{"episode_id", "ts", "outcome", "steps",
                                    "key_steps": [...], "truncated": bool}, ...]}
- 只写不改旧条目：返回**新** store 对象，旧 entries 逐条不变（可回放审计）；
- key_steps 超过 MAX_KEY_STEPS → 截断并置 truncated=True（截断标志入库）；
- 超容量 → 从最旧端淘汰（entries 尾部最新）；
- 空 store {} → 以默认容量起库（容量由 make_regularized_policy 的记忆配置注入）。
"""

from __future__ import annotations

from datetime import datetime, timezone

DEFAULT_CAPACITY = 32

# 关键步摘要上限：超过即截断并记录截断标志。
MAX_KEY_STEPS = 20


def update_experience_store(result: dict, key_steps: list, store: dict) -> dict:
    """把一局结局与关键步摘要写入经验库，返回更新后的新经验库 dict。

    - result: EpisodeResult（识别 episode_id/outcome/steps）；
    - key_steps: 关键步摘要列表（元素任意可序列化对象）；
    - store: 经验库 dict（空 dict 允许，按默认容量起库）。
    """
    if not isinstance(store, dict):
        raise TypeError(f"store 必须是 dict，实际是 {type(store).__name__}: {store!r}")

    capacity = store.get("capacity", DEFAULT_CAPACITY)
    if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity < 1:
        raise ValueError(f"capacity 必须是正整数，实际是 {capacity!r}")

    steps = list(key_steps or [])
    truncated = len(steps) > MAX_KEY_STEPS
    if truncated:
        steps = steps[:MAX_KEY_STEPS]

    entry = {
        "episode_id": result.get("episode_id"),
        "ts": datetime.now(timezone.utc).isoformat(),
        "outcome": result.get("outcome"),
        "steps": result.get("steps", 0),
        "key_steps": steps,
        "truncated": truncated,
    }
    entries = list(store.get("entries", [])) + [entry]  # 旧条目零改动
    if len(entries) > capacity:
        entries = entries[-capacity:]  # 淘汰最旧（头部）
    return {"capacity": capacity, "entries": entries}
