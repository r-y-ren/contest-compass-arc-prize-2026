"""向环境提交一步动作：action dict → SDK GameAction → env.step → 归一化返回。

错误归一化（references/arc_agi_3_sdk.md 实核 f：SDK 层失败一律返回 None 不抛异常，
REST 错误码被 SDK 吞进日志，调用方拿不到）：
- 动作 dict 结构非法（未知动作名/ACTION6 缺坐标/坐标越界）→ IllegalActionError（带 code）；
- env.step 返回 None（传输/服务端失败，含 REST 400/429/500 语义）：
  experiment → EnvError（失败即停）；submit → 返回 {"state": "STEP_FAILED"} 哨兵，
  由 run_episode 主循环按提交态哲学降级（保上一观测继续/走安全回退），不在这里重试。
"""

from __future__ import annotations

import logging

from src.run_episode._frame import EnvError, normalize_obs

__all__ = ["EnvError", "IllegalActionError", "submit_action"]

_LOGGER = logging.getLogger(__name__)

# 合法动作名集合（SDK 实核：RESET + ACTION1-7；0-63 坐标仅 ACTION6）。
LEGAL_ACTION_NAMES = frozenset(["RESET"] + [f"ACTION{i}" for i in range(1, 8)])

# submit 场景 step 失败的哨兵观测（非终局态；主循环见此态保持上一观测继续）。
STEP_FAILED_STATE = "STEP_FAILED"


class IllegalActionError(EnvError):
    """非法动作：结构校验不过（未知动作名/ACTION6 缺坐标/坐标越界），带错误码。"""

    def __init__(self, message: str, code: str):
        super().__init__(f"{message} [code={code}]")
        self.code = code


def _validate_action(action: dict) -> tuple:
    """校验动作 dict，返回 (name, data)；非法 → IllegalActionError。"""
    if not isinstance(action, dict) or "name" not in action:
        raise IllegalActionError(f"action 必须是含 name 键的 dict: {action!r}", "INVALID_ACTION")
    name = action["name"]
    if not isinstance(name, str) or name.upper() not in LEGAL_ACTION_NAMES:
        raise IllegalActionError(f"未知动作名: {name!r}", "INVALID_ACTION")
    name = name.upper()
    data = None
    if name == "ACTION6":
        x, y = action.get("x"), action.get("y")
        for coord in (x, y):
            if isinstance(coord, bool) or not isinstance(coord, int):
                raise IllegalActionError(
                    f"ACTION6 需要 0-63 整数坐标 x/y，实际 x={x!r} y={y!r}", "INVALID_COORDS"
                )
        if not (0 <= x <= 63 and 0 <= y <= 63):
            raise IllegalActionError(
                f"ACTION6 坐标越界（0-63），实际 x={x} y={y}", "COORDS_OUT_OF_RANGE"
            )
        data = {"x": x, "y": y}
    return name, data


def submit_action(env, action: dict, scene: str) -> dict:
    """向环境提交一步动作，返回归一化的下一观测 dict（或终局观测 dict）。

    - 动作结构非法 → IllegalActionError（code=INVALID_ACTION/INVALID_COORDS/COORDS_OUT_OF_RANGE）；
    - env.step 返回 None：experiment → EnvError；submit → {"state": "STEP_FAILED"}（不抛）；
    - 其余异常（SDK 未文档化抛出）→ EnvError 包装。
    """
    if scene not in ("experiment", "submit"):
        raise ValueError(f"未知 scene: {scene!r}（仅支持 experiment/submit）")

    name, data = _validate_action(action)

    try:
        from arcengine import GameAction  # 延迟导入：密闭测试注入假 env + 假枚举表

        game_action = GameAction.from_name(name)
    except ImportError:  # 无 SDK 环境：动作名已过白名单校验，直接透传字符串（假环境自解析）
        game_action = name
    except ValueError as exc:
        raise IllegalActionError(f"SDK 拒绝动作名 {name}: {exc}", "INVALID_ACTION") from exc

    try:
        obs = env.step(game_action, data)
    except Exception as exc:
        raise EnvError(f"env.step 抛异常（{name}）: {type(exc).__name__}: {exc}") from exc
    if obs is None:
        _LOGGER.warning("submit_action[%s] step 返回 None（动作 %s）", scene, action)
        if scene == "experiment":
            raise EnvError(f"step 请求失败（动作 {action}）——实验态失败即停")
        return {"state": STEP_FAILED_STATE}

    return normalize_obs(obs)
