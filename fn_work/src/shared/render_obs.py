"""把 SDK 观测对象转为提示词用文本视图。

评测可复现的根基：同输入必产生逐字节相同输出——
- 序列化用 json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=False)，
  键序递归排序、无多余空格、中文原样保留，全部确定；
- 结果按字符预算 budget 截断：不超预算原样返回；超预算时保留头部内容、截去尾部，
  并以尾标 "…[truncated]" 结尾。budget 是硬上限（len(结果) <= budget 恒成立），
  且预算 >= 尾标长度时截断结果恰为 budget 字符。
"""

from __future__ import annotations

import json

# 截断尾标（长度 12：省略号 1 字符 + "[truncated]" 11 字符）。
TRUNCATION_SUFFIX = "…[truncated]"

# 观测对象必填字段集合。来源：ARC-AGI-3 SDK FrameDataRaw / REST FrameResponse 九字段
# （references/arc_agi_3_sdk.md，2026-10-10 实核）中的策略相关六字段；
# guid / action_input / full_reset 为会话回显字段，不计必填。缺失即抛 ObsFormatError。
REQUIRED_FIELDS: tuple = (
    "game_id",
    "state",
    "frame",
    "levels_completed",
    "win_levels",
    "available_actions",
)


class ObsFormatError(ValueError):
    """观测对象非法：不是 dict，或缺 REQUIRED_FIELDS 中的必填字段（消息带字段名）。"""


def render_obs(obs: dict, budget: int) -> str:
    """把 SDK 观测对象转为提示词用文本视图（序列化+可选截断），格式稳定可复现。"""
    if not isinstance(obs, dict):
        raise ObsFormatError(f"obs 必须是 dict，实际是 {type(obs).__name__}: {obs!r}")
    for field in REQUIRED_FIELDS:
        if field not in obs:
            raise ObsFormatError(f"obs 缺必填字段: {field!r}")
    if budget <= 0:
        raise ValueError(f"budget 必须为正整数，实际是 {budget!r}")

    text = json.dumps(obs, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if len(text) <= budget:
        return text
    keep = budget - len(TRUNCATION_SUFFIX)
    if keep < 0:
        # 退化情形：预算装不下完整尾标，返回尾标前缀，budget 仍是硬上限。
        return TRUNCATION_SUFFIX[:budget]
    return text[:keep] + TRUNCATION_SUFFIX
