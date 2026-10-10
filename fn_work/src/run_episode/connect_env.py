"""官方 SDK 环境连接：episode spec → (环境句柄, 初始观测 dict)。

底座（references/arc_agi_3_sdk.md，2026-10-10 实核）：
arc_agi.Arcade() → arcade.make(game_id, seed=...) → 判空（SDK 失败返回 None 不抛
异常）→ env.reset() 取初始观测。Arcade 配置全走环境变量（ARC_API_KEY /
ARC_BASE_URL / OPERATION_MODE / ENVIRONMENTS_DIR / RECORDINGS_DIR），本函数不覆盖。
"""

from __future__ import annotations

from src.run_episode._frame import EnvError, normalize_obs

__all__ = ["EnvError", "connect_env"]


def connect_env(spec: dict) -> tuple:
    """按 episode spec 初始化官方 SDK 环境句柄，返回 (env 句柄, 初始观测 dict)。

    - spec: {"game_id": str（"ls20" 或 "ls20-<版本hash>"）, "seed": int（缺省 0）}；
    - make 失败返回 None / 初始 reset 返回 None / SDK 抛任何异常 → EnvError（消息带局 ID）；
    - 初始观测经 normalize_obs 归一化为纯 dict（frame 逐帧 tolist、枚举取值）。
    """
    game_id = spec.get("game_id")
    if not isinstance(game_id, str) or not game_id.strip():
        raise EnvError(f"episode spec 缺 game_id: {spec!r}")
    seed = spec.get("seed", 0)
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise EnvError(f"episode spec 的 seed 必须是整数，实际是 {seed!r}")

    try:
        import arc_agi  # 延迟导入：密闭测试经 sys.modules 注入假件，不触发真 SDK

        arcade = arc_agi.Arcade()
        env = arcade.make(game_id, seed=seed)
    except Exception as exc:  # SDK 层异常类型未文档化，统一包装
        raise EnvError(f"SDK 环境初始化失败（{game_id}）: {type(exc).__name__}: {exc}") from exc
    if env is None:
        raise EnvError(f"SDK make 返回 None：局不存在或不可用（{game_id}）")

    try:
        obs = env.reset()
    except Exception as exc:
        raise EnvError(f"SDK 初始 reset 失败（{game_id}）: {type(exc).__name__}: {exc}") from exc
    if obs is None:
        raise EnvError(f"SDK 初始 reset 返回 None（{game_id}）")

    return env, normalize_obs(obs)
