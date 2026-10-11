"""经验正则化：经验库 → 本步入提示的经验子集（责任文档 R4，RRSI 思路记忆层降级件）。

确定性打分（同输入同输出，可解释）：
    score = 新近度 + 相关性 + 胜局加成
- 新近度 = 条目位次 / max(库长-1, 1) ∈ [0,1]（尾部最新）；
- 相关性 = 1.0（条目局 ID 与当前观测 game_id 同基础名——同游戏经验更相关）否则 0；
- 胜局加成 = 0.5（outcome==WIN 的经验对通关更有用）否则 0。
按 score 降序贪心取 ≤budget 条；episode_id 重复者跳过（去重）；
平手按（新者优先，局 ID 字典序）全序确定。
取舍日志逐条给出得分构成与去留原因（kept/落选名次/重复跳过）。
"""

from __future__ import annotations

_RELEVANCE_BONUS = 1.0
_WIN_BONUS = 0.5


def _base(game_id) -> str:
    """局 ID 基础名：'-' 前部分（'ls20-abc' → 'ls20'；非字符串原样返回）。"""
    if not isinstance(game_id, str):
        return game_id
    return game_id.split("-", 1)[0]


def regularize_experience(store: dict, obs: dict, budget: int) -> tuple:
    """从经验库生成本步入提示子集，返回 (经验子集, 取舍日志)。

    - store: update_experience_store 维护的经验库 dict；
    - obs: 当前观测（game_id 作相关性锚点）；
    - budget: 入提示最大条数（<=0 → 空子集）；
    - 库空 / 无条目 → ([], [])（首局冷启动）；
    - 子集元素为入库条目的浅拷贝（调用方可安全注入提示）。
    """
    if not isinstance(budget, int) or isinstance(budget, bool):
        raise ValueError(f"budget 必须是整数，实际是 {budget!r}")
    entries = list((store or {}).get("entries", []))
    if not entries or budget <= 0:
        return [], []

    obs_base = _base(obs.get("game_id"))
    denom = max(len(entries) - 1, 1)
    ranked = []
    for idx, entry in enumerate(entries):
        recency = idx / denom
        relevant = _base(entry.get("episode_id")) == obs_base
        won = entry.get("outcome") == "WIN"
        score = recency + (_RELEVANCE_BONUS if relevant else 0.0) + (_WIN_BONUS if won else 0.0)
        # 平手决胜：分同 → 新者优先（位次大）→ 局 ID 字典序。
        ranked.append((-score, -idx, entry.get("episode_id") or "", idx, entry, recency, relevant, won))
    ranked.sort()

    subset, log = [], []
    picked_ids = set()
    for rank, item in enumerate(ranked):
        _, _, _, idx, entry, recency, relevant, won = item
        episode_id = entry.get("episode_id")
        factors = f"recency={recency:.3f} relevance={_RELEVANCE_BONUS if relevant else 0.0} win={_WIN_BONUS if won else 0.0}"
        if episode_id in picked_ids:
            log.append({"episode_id": episode_id, "kept": False, "score": -item[0], "reason": f"duplicate（同局 ID 已取）| {factors}"})
            continue
        if len(subset) < budget:
            picked_ids.add(episode_id)
            subset.append(dict(entry))
            log.append({"episode_id": episode_id, "kept": True, "rank": rank, "score": -item[0], "reason": f"kept（第 {rank + 1} 优先）| {factors}"})
        else:
            log.append({"episode_id": episode_id, "kept": False, "score": -item[0], "reason": f"beyond-budget（预算 {budget} 已满）| {factors}"})
    return subset, log
