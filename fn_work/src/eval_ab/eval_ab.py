"""A/B 评测主流程（责任文档 R5，CLI 入口 eval_ab.py）。

    python eval_ab.py --episodes N --seed S [--configs baseline full ...]

流程：load_episode_set 载局集（含 SDK 局索引存在性校验——B2 债务①的注入点）
→ build_config_matrix 展开配置（--configs 按名筛选默认四配置）
→ 逐配置 run_config_batch（实验态：任一失败 ExperimentAbortError 透传，非零退出）
→ aggregate_results 对照表（CSV 落 runs 目录 + 控制台表）。
runs 根目录 ARC_RUNS_DIR（缺省 fn_work/runs）；局集路径 ARC_EPISODE_SET
（缺省 fn_work/episode_sets/default.yaml）。
"""

from __future__ import annotations

import os
import time

from src.eval_ab.aggregate_results import aggregate_results
from src.eval_ab.build_config_matrix import DEFAULT_DECLARATIONS, build_config_matrix
from src.eval_ab.run_config_batch import run_config_batch
from src.shared.append_jsonl_log import append_jsonl_log
from src.shared.load_episode_set import load_episode_set


def _sdk_episode_ids():
    """官方 SDK 局索引（get_environments 的 game_id 列表）；SDK 不可达时 None（跳过校验）。"""
    try:
        import arc_agi

        return [env.game_id for env in arc_agi.Arcade().get_environments()]
    except Exception:  # 密闭/离线环境：不阻断评测，存在性校验退化为结构校验
        return None


def eval_ab(episodes: int, seed: int, configs: list = None) -> dict:
    """A/B 评测主流程：载局集→展开配置→逐配置跑批→出对照表，返回 run 摘要 dict。

    - episodes：截取局集前 N 局（正整数）；
    - configs：配置名列表（筛选默认四配置）；None = 全部；
    - 任一配置失败 → ExperimentAbortError 透传（CLI 非零退出）；
    - 返回 {"run_id", "csv_path", "table", "metrics"}；run 级起止事件落 JSONL。
    """
    if isinstance(episodes, bool) or not isinstance(episodes, int) or episodes < 1:
        raise ValueError(f"episodes 必须是正整数，实际是 {episodes!r}")

    run_id = f"eval-{int(time.time())}-s{seed}"
    episode_set_path = os.environ.get("ARC_EPISODE_SET", "fn_work/episode_sets/default.yaml")
    episode_set = load_episode_set(episode_set_path, known_episode_ids=_sdk_episode_ids())
    episode_set["episode_ids"] = episode_set["episode_ids"][:episodes]
    episode_set["seed"] = seed

    if configs is None:
        declarations = None
    else:
        by_name = {d["name"]: d for d in DEFAULT_DECLARATIONS}
        unknown = [name for name in configs if name not in by_name]
        if unknown:
            raise ValueError(f"未知配置名: {unknown}（可选: {sorted(by_name)}）")
        declarations = [by_name[name] for name in configs]
    matrix = build_config_matrix(declarations)

    runs_root = os.environ.get("ARC_RUNS_DIR", "fn_work/runs")
    out_dir = os.path.join(runs_root, run_id)
    append_jsonl_log(
        run_id, "eval_ab_start",
        {"episodes": episodes, "seed": seed, "configs": [c["name"] for c in matrix],
         "episode_ids": episode_set["episode_ids"], "out_dir": out_dir},
    )

    metrics = [run_config_batch(config, episode_set, run_id) for config in matrix]
    csv_path, table = aggregate_results(metrics, out_dir)
    print(table)

    append_jsonl_log(
        run_id, "eval_ab_end",
        {"csv_path": csv_path,
         "wins": {m["name"]: m["wins"] for m in metrics},
         "success_rate": {m["name"]: m["success_rate"] for m in metrics}},
    )
    return {"run_id": run_id, "csv_path": csv_path, "table": table, "metrics": metrics}
