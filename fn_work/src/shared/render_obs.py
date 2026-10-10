"""把 SDK 观测对象转为提示词用文本视图。

评测可复现的根基：同输入必产生逐字节相同输出——
- 序列化用 json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=False)，
  键序递归排序、无多余空格、中文原样保留，全部确定；
- 结果按字符预算 budget 截断：不超预算原样返回；超预算时截去头部内容并以
  尾标 "…[truncated]" 结尾。budget 是硬上限（len(结果) <= budget 恒成立），
  且预算 >= 尾标长度时截断结果恰为 budget 字符。
"""

from __future__ import annotations

import json

# 截断尾标（长度 12：省略号 1 字符 + "[truncated]" 11 字符）。
TRUNCATION_SUFFIX = "…[truncated]"

# 观测对象必填字段集合。约定：当前为空 tuple——官方 SDK 观测形态 B2 实核后回填；
# 回填为非空后 render_obs 将逐项校验，缺失即抛 ObsFormatError（消息带字段名）。
REQUIRED_FIELDS: tuple = ()


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
