"""经验正则包装策略（RRSI 思路记忆层降级，责任文档 R4）。

维护经验库（update_experience_store 形态）：每步 act 取 regularize_experience 的
经验子集注入 obs["experience"]（经 render_obs 序列化进入提示词）后转发内层策略；
局终以本局各步动作作关键步摘要调 update_experience_store 入库（原始版），并把
逐步正则决策日志与库快照刷入 JSONL（正则版）——"保留原始与正则两版"。

策略协议（与 run_episode 约定，同 CurriculumPolicy）：
act(obs) / on_episode_start(spec, run_id) / on_episode_end(result, run_id) /
scene / total_usage（后四者转发或缓冲）。
"""

from __future__ import annotations

from src.make_regularized_policy.regularize_experience import regularize_experience
from src.make_regularized_policy.update_experience_store import (
    DEFAULT_CAPACITY,
    update_experience_store,
)
from src.shared.append_jsonl_log import append_jsonl_log

# 默认入提示经验条数预算（正则参数）。
DEFAULT_BUDGET = 3


class PolicyWrapError(RuntimeError):
    """内层策略接口不符（缺可调用 act）或记忆配置结构非法。"""


class RegularizedPolicy:
    """经验正则包装策略对象。"""

    name = "regularized"

    def __init__(self, inner, capacity: int, budget: int):
        if not callable(getattr(inner, "act", None)):
            raise PolicyWrapError(f"内层策略缺可调用 act: {inner!r}")
        self.inner = inner
        self._store = {"capacity": capacity, "entries": []}
        self._budget = budget
        self._episode_actions = []    # 本局关键步缓冲：[(步号, 动作 dict)]
        self._episode_decisions = []  # 本局正则决策缓冲：逐步取舍日志

    # ---- 协议转发 ----

    @property
    def scene(self) -> str:
        return getattr(self.inner, "scene", "experiment")

    @property
    def total_usage(self) -> dict:
        return getattr(self.inner, "total_usage", None) or {
            "prompt_tokens": 0, "completion_tokens": 0, "calls": 0
        }

    # ---- 局边界钩子 ----

    def on_episode_start(self, spec: dict, run_id: str) -> None:
        """清空本局缓冲（经验库跨局保留）。"""
        self._episode_actions = []
        self._episode_decisions = []

    def on_episode_end(self, result: dict, run_id: str) -> None:
        """本局经验入库（原始版=全量关键步）并刷决策日志（正则版）到 JSONL。"""
        key_steps = [{"step": n, "action": action} for n, action in self._episode_actions]
        self._store = update_experience_store(result, key_steps, self._store)
        append_jsonl_log(
            run_id,
            "regularized_episode",
            {
                "episode_id": result.get("episode_id"),
                "outcome": result.get("outcome"),
                "steps": result.get("steps", 0),
                "decisions": self._episode_decisions,   # 正则版：逐步入提示取舍
                "store_size": len(self._store["entries"]),
                "capacity": self._store["capacity"],
            },
        )
        self._episode_actions = []
        self._episode_decisions = []

    # ---- 局内行为 ----

    def act(self, obs: dict) -> dict:
        """正则化经验子集注入观测后转发内层策略；缓冲本步动作与决策。"""
        subset, log = regularize_experience(self._store, obs, self._budget)
        self._episode_decisions.append(
            {"step": len(self._episode_actions) + 1, "kept": [e.get("episode_id") for e in subset], "log": log}
        )
        enriched = dict(obs)
        if subset:
            enriched["experience"] = subset
        action = self.inner.act(enriched)
        self._episode_actions.append((len(self._episode_actions) + 1, action))
        return action


def make_regularized_policy(inner_policy, memory_config: dict) -> RegularizedPolicy:
    """构造经验正则包装策略（默认由配置矩阵包装 baseline 作内层）。

    memory_config 键（均可选，记忆配置=容量/正则参数）：
    - capacity: 经验库容量（缺省 32）；
    - budget: 每步入提示经验条数上限（缺省 3）。
    内层缺 act / 配置类型非法 → PolicyWrapError。
    """
    if not isinstance(memory_config, dict):
        raise PolicyWrapError(
            f"memory_config 必须是 dict，实际是 {type(memory_config).__name__}"
        )
    capacity = memory_config.get("capacity", DEFAULT_CAPACITY)
    budget = memory_config.get("budget", DEFAULT_BUDGET)
    for name, value in (("capacity", capacity), ("budget", budget)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise PolicyWrapError(f"{name} 必须是正整数，实际是 {value!r}")
    return RegularizedPolicy(inner_policy, capacity, budget)
