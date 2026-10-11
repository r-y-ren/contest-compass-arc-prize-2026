"""经验源选择：难度表 + 已选历史 → (下一经验源 ID, 理由字符串)。

ActiveSaddler 思路的编排层降级（责任文档 R3）：先易后难 + 利用计数。
规则钉死（确定性、可解释）：
    score = difficulty + SELECTION_LAMBDA * selected_count
- 取 score 最小者（难度低优先；被选次数多者受惩罚，保证探索覆盖）；
- 平手依次比 (难度, 已选次数, ID 字典序)，全序确定——同输入同输出；
- 理由字符串携带三要素与得分，逐次可查。
"""

from __future__ import annotations

from collections import Counter

# 利用计数惩罚系数：每被选一次，等效难度加 λ。
SELECTION_LAMBDA = 0.5


class CurriculumError(RuntimeError):
    """经验源池为空（难度表空或无有效项），无法选择。"""


def select_experience_source(difficulty_table: dict, chosen_history: list) -> tuple:
    """依据难度表与已选历史选出下一经验源，返回 (经验源 ID, 理由字符串)。

    - difficulty_table: {source_id: 难度标量}（数值；来自 estimate_difficulty）；
    - chosen_history: 已选 source_id 列表（计数用，顺序无关）；
    - 池空（空 dict / 全非数值项）→ CurriculumError。
    """
    counts = Counter(chosen_history)
    scored = []
    for source_id, difficulty in (difficulty_table or {}).items():
        if isinstance(difficulty, (int, float)) and not isinstance(difficulty, bool):
            difficulty = float(difficulty)
            selected = counts.get(source_id, 0)
            score = difficulty + SELECTION_LAMBDA * selected
            scored.append((score, difficulty, selected, source_id))
    if not scored:
        raise CurriculumError(f"经验源池为空或无有效难度项: {difficulty_table!r}")

    score, difficulty, selected, source_id = min(scored)
    reason = (
        f"source={source_id} difficulty={difficulty:.3f} selected={selected} "
        f"score={score:.3f} (rule=min(difficulty+{SELECTION_LAMBDA}*selected); "
        f"pool={len(scored)})"
    )
    return source_id, reason
