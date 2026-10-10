"""单局主循环：连接环境 → obs → 策略 act → 提交 → 步日志 → 终局汇总 EpisodeResult。

退出条件（references/arc_agi_3_sdk.md 实核 e/h）：
- obs.state ∈ {WIN, GAME_OVER} 为终局；SDK 无墙钟时限，故本地 MAX_STEPS 护栏防死循环，
  触顶 outcome=STEP_LIMIT；
- submit 场景 step 失败返回 STEP_FAILED 哨兵（非终局）：保持上一观测继续（提交态降级哲学），
  实验场景的失败已在 submit_action 内抛 EnvError（失败即停）。
策略协议：policy.act(obs) -> 动作 dict；可选属性 scene（缺省 experiment）与
total_usage（缺省零用量）。
策略抛出的实验态异常不捕获（失败即停哲学由上层场景决定）。
"""

from __future__ import annotations

import time

from src.run_episode.connect_env import connect_env
from src.run_episode.submit_action import STEP_FAILED_STATE, submit_action
from src.shared.append_jsonl_log import append_jsonl_log

# 终局状态（GameState 取值，见 _frame.normalize_obs：枚举已转字符串）。
_TERMINAL_STATES = ("WIN", "GAME_OVER")

# 步数护栏：官方文档未载明每局时限（实核 h），防策略与环境无限循环。
MAX_STEPS = 1024


def run_episode(spec: dict, policy, run_id: str) -> dict:
    """执行一局完整交互，返回 EpisodeResult dict。

    - 每步写 JSONL 步日志（event="step"：game_id/step/action/state/levels_completed/
      latency_ms），局终写 event="episode_end"（完整 EpisodeResult）；
    - EpisodeResult：{"episode_id": 解析后局 ID, "outcome": WIN|GAME_OVER|STEP_LIMIT,
      "steps": 提交步数, "duration_s": 总耗时秒, "levels_completed": ..., "win_levels": ...,
      "token_usage": 策略 total_usage（无此属性则零用量快照）}；
    - connect_env 的 EnvError 与策略异常原样透传。
    """
    scene = getattr(policy, "scene", "experiment")
    env, obs = connect_env(spec)
    game_id = obs.get("game_id") or spec.get("game_id")

    started = time.perf_counter()
    steps = 0
    while obs.get("state") not in _TERMINAL_STATES and steps < MAX_STEPS:
        step_started = time.perf_counter()
        action = policy.act(obs)
        next_obs = submit_action(env, action, scene)
        steps += 1
        append_jsonl_log(
            run_id,
            "step",
            {
                "game_id": game_id,
                "step": steps,
                "action": action,
                "state": next_obs.get("state"),
                "levels_completed": next_obs.get("levels_completed"),
                "latency_ms": int((time.perf_counter() - step_started) * 1000),
            },
        )
        if next_obs.get("state") != STEP_FAILED_STATE:
            obs = next_obs

    state = obs.get("state")
    outcome = state if state in _TERMINAL_STATES else "STEP_LIMIT"
    token_usage = dict(getattr(policy, "total_usage", None) or {
        "prompt_tokens": 0, "completion_tokens": 0, "calls": 0
    })
    result = {
        "episode_id": game_id,
        "outcome": outcome,
        "steps": steps,
        "duration_s": round(time.perf_counter() - started, 3),
        "levels_completed": obs.get("levels_completed"),
        "win_levels": obs.get("win_levels"),
        "token_usage": token_usage,
    }
    append_jsonl_log(run_id, "episode_end", result)
    return result
