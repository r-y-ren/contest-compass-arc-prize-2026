"""课程调度包装策略（ActiveSaddler 思路编排层降级，责任文档 R3）。

跨局维护各经验源的历史局记录：每局开始前用 estimate_difficulty 重算难度表、
select_experience_source 选定本局经验源（先易后难+利用计数），选择与理由写入
JSONL 日志；局内把所选源描述注入 obs["experience_source"]（经 render_obs 序列化
进入提示词——示例局选择通道），其余行为转发内层策略。局终把本局结局记回所选源
并落难度更新日志。

策略协议（与 run_episode 约定）：
- act(obs) -> 动作 dict（转发内层，观测注入 experience_source 后）；
- on_episode_start(spec, run_id) / on_episode_end(result, run_id) 可选钩子
  （run_episode 检测到即调用——本包装依赖，协议扩展见 tracker Ruling）；
- scene / total_usage 转发内层。
"""

from __future__ import annotations

from datetime import datetime, timezone

from src.make_curriculum_policy.estimate_difficulty import estimate_difficulty
from src.make_curriculum_policy.select_experience_source import select_experience_source
from src.shared.append_jsonl_log import append_jsonl_log


class PolicyWrapError(RuntimeError):
    """内层策略接口不符（缺可调用 act）或课程配置结构非法。"""


class CurriculumPolicy:
    """课程调度包装策略对象。"""

    name = "curriculum"

    def __init__(self, inner, sources: dict):
        if not callable(getattr(inner, "act", None)):
            raise PolicyWrapError(f"内层策略缺可调用 act: {inner!r}")
        if not isinstance(sources, dict) or not all(
            isinstance(records, list) for records in sources.values()
        ):
            raise PolicyWrapError(
                f"课程配置 sources 必须是 {{源ID: 历史记录列表}} 映射: {sources!r}"
            )
        self.inner = inner
        self._source_history = {sid: list(records) for sid, records in sources.items()}
        self._chosen_history = []          # 已选源 ID 序列（select 的利用计数输入）
        self._current_source = None
        self._current_reason = ""

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
        """重算难度表并选定本局经验源，选择与理由写 JSONL。"""
        difficulty_table = {
            sid: estimate_difficulty(records)[0]
            for sid, records in self._source_history.items()
        }
        source_id, reason = select_experience_source(difficulty_table, self._chosen_history)
        self._current_source = source_id
        self._current_reason = reason
        self._chosen_history.append(source_id)
        append_jsonl_log(
            run_id,
            "curriculum_select",
            {
                "game_id": spec.get("game_id"),
                "source": source_id,
                "reason": reason,
                "difficulty_table": difficulty_table,
            },
        )

    def on_episode_end(self, result: dict, run_id: str) -> None:
        """本局结局记回所选源历史并落难度更新日志。"""
        if self._current_source is None:
            return  # 局未开始（start 钩子未被调用）：无可归档
        record = {
            "outcome": result.get("outcome"),
            "steps": result.get("steps", 0),
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        self._source_history[self._current_source].append(record)
        new_difficulty, low_confidence = estimate_difficulty(
            self._source_history[self._current_source]
        )
        append_jsonl_log(
            run_id,
            "curriculum_update",
            {
                "episode_id": result.get("episode_id"),
                "source": self._current_source,
                "record": record,
                "new_difficulty": new_difficulty,
                "low_confidence": low_confidence,
            },
        )

    # ---- 局内行为 ----

    def act(self, obs: dict) -> dict:
        """把所选经验源描述注入观测后转发内层策略（注入项进提示词视图）。"""
        if self._current_source is None:
            return self.inner.act(obs)  # 局开始前直接转发（钩子未走的裸用形态）
        enriched = dict(obs)
        enriched["experience_source"] = {
            "id": self._current_source,
            "reason": self._current_reason,
        }
        return self.inner.act(enriched)


def make_curriculum_policy(inner_policy, curriculum_config: dict) -> CurriculumPolicy:
    """构造课程调度包装策略（默认由配置矩阵包装 baseline 作内层）。

    curriculum_config 键：
    - sources（必填）: {源ID: [历史局记录, ...]}——各经验源初始记录
      （记录元素 {"outcome": "WIN"|..., "steps": int}，供难度估计）。
    内层缺 act / sources 结构非法 → PolicyWrapError。
    """
    if not isinstance(curriculum_config, dict):
        raise PolicyWrapError(
            f"curriculum_config 必须是 dict，实际是 {type(curriculum_config).__name__}"
        )
    sources = curriculum_config.get("sources", {})
    return CurriculumPolicy(inner_policy, sources)
