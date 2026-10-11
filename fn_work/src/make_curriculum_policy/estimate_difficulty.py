"""经验源难度估计：历史局记录 → 标量难度信号（纯函数，无副作用）。

ActiveSaddler 思路的编排层降级件（责任文档 R3）：难度信号供
select_experience_source 做"先易后难"选择。公式钉死保证确定性：
    difficulty = (1 - success_rate) + 0.5 * min(avg_steps / 100, 1.0)
- success_rate = WIN 局数 / 总局数（无 WIN 记录按 0 计）；
- avg_steps = 各记录 steps 均值（缺 steps 按 0 计）；
- 取值域约 [0, 2]：全胜少步 → 0（最易），全败百步 → 2（最难）。
"""

from __future__ import annotations

# 空记录的默认难度（中性偏难：无信息时不敢假设容易）。
DEFAULT_DIFFICULTY = 1.0

# 步数归一上限：avg_steps 达到该值即取满 0.5 步数惩罚项。
_STEP_NORM_CAP = 100.0
_STEP_WEIGHT = 0.5


def estimate_difficulty(history: list) -> tuple:
    """从某经验源的历史局记录计算 (难度标量, 低置信 bool)。

    - 记录元素为 dict，识别键：outcome（"WIN" 记成功）、steps（数值，缺省 0）；
    - 空列表 → (DEFAULT_DIFFICULTY, True)——默认难度并标注低置信；
    - 纯函数：不修改输入，同输入同输出。
    """
    if not history:
        return DEFAULT_DIFFICULTY, True

    wins = sum(1 for r in history if isinstance(r, dict) and r.get("outcome") == "WIN")
    steps = [r.get("steps", 0) if isinstance(r, dict) else 0 for r in history]
    avg_steps = sum(steps) / len(steps)
    success_rate = wins / len(history)

    difficulty = (1.0 - success_rate) + _STEP_WEIGHT * min(avg_steps / _STEP_NORM_CAP, 1.0)
    return difficulty, False
