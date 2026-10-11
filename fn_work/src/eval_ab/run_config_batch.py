"""单配置批跑：config × 局集 → 配置指标（责任文档 R5）。

策略组合构造（与 build_config_matrix 的 POLICY_KINDS 对应）：
    baseline            → make_baseline_policy(baseline_config)
    curriculum          → 课程(基线)
    regularized         → 正则(基线)
    curriculum+regularized → 课程(正则(基线))——编排层在外、记忆层在内
实验态哲学：任一局失败（EnvError/LLM 服务/策略异常）立即抛 ExperimentAbortError
（附局 ID），整跑由 eval_ab 终止——失败数字不进对照表。
"""

from __future__ import annotations

from src.make_baseline_policy.make_baseline_policy import make_baseline_policy
from src.make_curriculum_policy.make_curriculum_policy import make_curriculum_policy
from src.make_regularized_policy.make_regularized_policy import make_regularized_policy
from src.run_episode.run_episode import run_episode
from src.shared.append_jsonl_log import append_jsonl_log


class ExperimentAbortError(RuntimeError):
    """实验中止：配置构造失败或某局失败（消息附配置名/局 ID 与原因）。"""


def build_policy(config: dict):
    """按配置的策略组合构造策略对象（scene 恒 experiment，工厂各自套参数默认）。"""
    scene = config.get("scene", "experiment")
    baseline = make_baseline_policy({**config.get("baseline_config", {}), "scene": scene})
    policy_kind = config.get("policy")
    if policy_kind == "baseline":
        return baseline
    if policy_kind == "curriculum":
        return make_curriculum_policy(baseline, config.get("curriculum_config", {}))
    if policy_kind == "regularized":
        return make_regularized_policy(baseline, config.get("regularized_config", {}))
    if policy_kind == "curriculum+regularized":
        inner = make_regularized_policy(baseline, config.get("regularized_config", {}))
        return make_curriculum_policy(inner, config.get("curriculum_config", {}))
    raise ExperimentAbortError(f"未知 policy 组合: {policy_kind!r}")


def run_config_batch(config: dict, episode_set: dict, run_id: str) -> dict:
    """单配置跑完整个局集，返回该配置指标 dict（含逐局结果列表）。

    - 逐局 spec = {"game_id": episode_id, "seed": episode_set.seed}；
    - 指标：episodes/wins/success_rate/avg_steps/duration_s（各局之和）/
      token_usage（各局汇总）+ episode_results 原样列表；
    - 批级起止事件落 JSONL（config_batch_start / config_batch_end）。
    """
    name = config.get("name", "<unnamed>")
    try:
        policy = build_policy(config)
    except Exception as exc:
        raise ExperimentAbortError(f"配置 {name} 策略构造失败: {type(exc).__name__}: {exc}") from exc

    episode_ids = episode_set.get("episode_ids", [])
    seed = episode_set.get("seed", 0)
    append_jsonl_log(
        run_id, "config_batch_start",
        {"config": name, "policy": config.get("policy"), "episodes": len(episode_ids), "seed": seed},
    )

    results = []
    for index, episode_id in enumerate(episode_ids):
        try:
            results.append(run_episode({"game_id": episode_id, "seed": seed}, policy, run_id))
        except Exception as exc:
            raise ExperimentAbortError(
                f"配置 {name} 第 {index + 1} 局（{episode_id}）失败: {type(exc).__name__}: {exc}"
            ) from exc

    episodes_n = len(results)
    wins = sum(1 for r in results if r.get("outcome") == "WIN")
    token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "calls": 0}
    for r in results:
        for key in token_usage:
            token_usage[key] += (r.get("token_usage") or {}).get(key, 0)
    metrics = {
        "name": name,
        "policy": config.get("policy"),
        "episodes": episodes_n,
        "wins": wins,
        "success_rate": (wins / episodes_n) if episodes_n else 0.0,
        "avg_steps": (sum(r.get("steps", 0) for r in results) / episodes_n) if episodes_n else 0.0,
        "duration_s": round(sum(r.get("duration_s", 0.0) for r in results), 3),
        "token_usage": token_usage,
        "episode_results": results,
    }
    append_jsonl_log(run_id, "config_batch_end", {k: v for k, v in metrics.items() if k != "episode_results"})
    return metrics
