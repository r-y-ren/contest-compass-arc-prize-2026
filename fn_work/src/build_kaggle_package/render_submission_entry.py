"""提交入口渲染：最优配置 → agent/my_agent.py 内容（责任文档 R6）。

契约以赛站实核为准（references/arc_agi_3_sdk.md + ARC Prize 2026 官方文档
2026-10-11 实核）：code competition 提交 notebook，kit 只编辑 agent/my_agent.py，
MyAgent 继承 Agent，实现 is_done(frames, latest_frame) 与
choose_action(frames, latest_frame) -> GameAction。

本函数渲染的入口做协议适配：官方 Agent 接口 ↔ 我方策略协议
（normalize_obs → policy.act → GameAction 转换），策略按 BEST_CONFIG 组装、
scene=submit（llm_complete 有限重试耗尽降级 SAFE_FALLBACK → 策略确定性回退）。
"""

from __future__ import annotations

# 契约模板必填字段（缺一 → PackageError）。
REQUIRED_CONTRACT_FIELDS = ("entry_path", "agent_class", "base_import")

# 官方实核契约（B5 缺省模板：赛站 starter kit 的 agent 形态）。
DEFAULT_CONTRACT = {
    "entry_path": "agent/my_agent.py",
    "agent_class": "MyAgent",
    "base_import": "from agents.structs import Agent",
}

_ENTRY_TEMPLATE = '''"""ARC Prize 2026 提交入口——render_submission_entry 生成，勿手改。

策略：{config_name}（{policy_kind}，scene=submit）；生成时间：{generated_at}。
"""
from arcengine import GameAction

from src.make_baseline_policy.make_baseline_policy import make_baseline_policy
from src.make_curriculum_policy.make_curriculum_policy import make_curriculum_policy
from src.make_regularized_policy.make_regularized_policy import make_regularized_policy
from src.run_episode._frame import normalize_obs

BEST_CONFIG = {best_config!r}


def _build_policy():
    """按 BEST_CONFIG 组合策略（与 run_config_batch.build_policy 同构，scene=submit）。"""
    baseline = make_baseline_policy({{**BEST_CONFIG["baseline_config"], "scene": "submit"}})
    kind = BEST_CONFIG["policy"]
    if kind == "baseline":
        return baseline
    if kind == "curriculum":
        return make_curriculum_policy(baseline, BEST_CONFIG["curriculum_config"])
    if kind == "regularized":
        return make_regularized_policy(baseline, BEST_CONFIG["regularized_config"])
    inner = make_regularized_policy(baseline, BEST_CONFIG["regularized_config"])
    return make_curriculum_policy(inner, BEST_CONFIG["curriculum_config"])


class {agent_class}({base_class}):
    """官方 Agent 接口适配器：观测→我方策略→GameAction。"""

    def __init__(self):
        self._policy = _build_policy()

    def is_done(self, frames, latest_frame) -> bool:
        state = getattr(latest_frame, "state", None)
        name = getattr(state, "name", None) or str(state)
        return name in ("WIN", "GAME_OVER")

    def choose_action(self, frames, latest_frame) -> GameAction:
        obs = normalize_obs(latest_frame)
        action = self._policy.act(obs)
        game_action = GameAction.from_name(action["name"])
        if action["name"] == "ACTION6":
            game_action.set_data({{"x": action["x"], "y": action["y"]}})
        return game_action
'''


class PackageError(RuntimeError):
    """提交件契约不合法：模板缺字段/配置缺段。"""


def render_submission_entry(best_config, contract_template: dict = None) -> str:
    """按契约模板渲染入口文件内容，返回 my_agent.py 源码文本。

    - best_config：配置名 str（在 build_config_matrix 默认阵中按名解析；未知名
      → PackageError）或配置项 dict（含 name/policy/三参数段，直接使用）；
    - contract_template：{"entry_path", "agent_class", "base_import"}（缺省用
      DEFAULT_CONTRACT——赛站实核契约）；缺必填字段 → PackageError；
    - 生成文本含 BEST_CONFIG 常量与 MyAgent 适配器（scene=submit 降级回退由
      llm_complete/策略回退链承担）。
    """
    if contract_template is None:
        contract = dict(DEFAULT_CONTRACT)
    else:
        contract = dict(contract_template)  # 显式模板必须完整：缺字段即 PackageError
    missing = [field for field in REQUIRED_CONTRACT_FIELDS if not contract.get(field)]
    if missing:
        raise PackageError(f"契约模板缺字段: {missing}（需 {list(REQUIRED_CONTRACT_FIELDS)}）")

    from src.eval_ab.build_config_matrix import build_config_matrix

    if isinstance(best_config, str):
        resolved = next(
            (c for c in build_config_matrix() if c["name"] == best_config), None
        )
        if resolved is None:
            raise PackageError(
                f"未知配置名: {best_config!r}（默认阵: "
                f"{[c['name'] for c in build_config_matrix()]}）"
            )
        best_config = resolved
    if not isinstance(best_config, dict) or "name" not in best_config or "policy" not in best_config:
        raise PackageError(f"best_config 必须是配置名或含 name/policy 的配置项: {best_config!r}")

    from datetime import datetime, timezone

    return _ENTRY_TEMPLATE.format(
        config_name=best_config["name"],
        policy_kind=best_config["policy"],
        generated_at=datetime.now(timezone.utc).isoformat(),
        best_config=best_config,
        agent_class=contract["agent_class"],
        base_class=contract["base_import"].rsplit(" import ", 1)[-1],
    )
