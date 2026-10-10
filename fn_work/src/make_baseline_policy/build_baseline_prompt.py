"""裸基线提示词拼装：固定系统模板 + render_obs 观测视图。

模板文本为常量 BASELINE_SYSTEM_PROMPT（动作协议与字段语义以 SDK 实核为准，
见 references/arc_agi_3_sdk.md）——改动须记 requirements 变更。
"""

from src.shared.render_obs import render_obs

# 观测视图字符预算：64×64×多帧网格序列化后可达数万字符，预算内截断保头（保住网格
# 开头比保尾对局面理解更重要，且截断行为确定性可复现）。
OBS_BUDGET = 4000

BASELINE_SYSTEM_PROMPT = (
    "You are an agent playing an ARC-AGI-3 interactive game.\n"
    "\n"
    "The user message each turn is a JSON view of the current observation:\n"
    '- "frame": one or more grids (up to 64x64) of integers 0-15 describing the game\n'
    "screen (0 is usually the background);\n"
    '- "state": NOT_PLAYED / NOT_FINISHED / WIN / GAME_OVER;\n'
    '- "available_actions": integer ids of the actions currently legal\n'
    "(0=RESET, 1..7=ACTION1..ACTION7);\n"
    '- "levels_completed" / "win_levels": levels already done and the threshold to win.\n'
    "\n"
    "Each turn you must answer with exactly one action, on a single line:\n"
    '- a simple action: "RESET" or "ACTION1" ... "ACTION5", "ACTION7";\n'
    '- the complex action: "ACTION6 x y" with integer coordinates 0 <= x,y <= 63.\n'
    "\n"
    "Only choose among the actions listed in available_actions. Study what the grids\n"
    "mean, then output the action line and nothing else."
)


def build_baseline_prompt(obs: dict) -> list:
    """拼装固定系统提示词 + render_obs 观测视图为 messages 列表。

    - 返回 [{"role": "system", "content": BASELINE_SYSTEM_PROMPT},
            {"role": "user", "content": render_obs(obs, OBS_BUDGET)}]；
    - 模板为常量、观测视图确定性序列化——同输入两次调用逐字节相同；
    - render_obs 异常（非 dict / 缺必填字段 / 非法预算）原样透传。
    """
    user_view = render_obs(obs, OBS_BUDGET)
    return [
        {"role": "system", "content": BASELINE_SYSTEM_PROMPT},
        {"role": "user", "content": user_view},
    ]
