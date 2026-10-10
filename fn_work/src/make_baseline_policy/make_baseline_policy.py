"""裸基线策略工厂：固定提示词 + 冻结 LLM，无记忆、无经验、无课程。

确定性根基（R2：同 seed 两跑一致）：默认采样 temperature=0 贪心解码，解析与回退
全部确定性（无随机）；动作协议见 references/arc_agi_3_sdk.md——obs.available_actions
是 0-7 整数编号（0=RESET，1..7=ACTION1..ACTION7），ACTION6 需 0-63 坐标。
"""

from __future__ import annotations

import logging
import re

from src.make_baseline_policy.build_baseline_prompt import build_baseline_prompt
from src.shared.llm_complete import llm_complete

_LOGGER = logging.getLogger(__name__)

# 默认采样参数：temperature=0 贪心解码。构造时记入日志（责任文档要求）。
BASELINE_SAMPLING = {"temperature": 0.0, "max_tokens": 64}

# 动作编号 → 名称（obs.available_actions 的整数编号映射；SDK 实核：0=RESET）。
ACTION_NAMES = (
    "RESET",
    "ACTION1",
    "ACTION2",
    "ACTION3",
    "ACTION4",
    "ACTION5",
    "ACTION6",
    "ACTION7",
)

# 动作解析（官方 safe_parse 模式，references/arc_agi_3_sdk.md 附节）：
# 取回复中第一个出现的动作名；ACTION6 再在其后找两个 0-63 整数坐标。
_ACTION_RE = re.compile(r"\b(RESET|ACTION[1-7])\b")
_COORDS_RE = re.compile(r"(\d{1,2})\D+(\d{1,2})")


class ConfigError(RuntimeError):
    """基线策略配置不合法：缺 scene / scene 取值非法 / 字段类型错。"""


def _fallback_action(obs: dict) -> dict:
    """确定性回退：available_actions 首个合法编号的动作；列表空/全非法时 RESET。"""
    for action_id in obs.get("available_actions") or []:
        if isinstance(action_id, int) and 0 <= action_id < len(ACTION_NAMES):
            return {"name": ACTION_NAMES[action_id]}
    return {"name": "RESET"}


class BaselinePolicy:
    """裸基线策略对象：act(obs) -> 动作 dict（{"name": str[, "x": int, "y": int]}）。"""

    name = "baseline"

    def __init__(self, scene: str, model: str, sampling: dict):
        self.scene = scene
        self.model = model
        self.sampling = dict(sampling)
        # token 用量累计：run_episode 局终汇总进 EpisodeResult（无此属性需求的策略可不含）。
        self.total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "calls": 0}
        _LOGGER.info(
            "baseline policy 构造: scene=%s model=%r sampling=%s", scene, model, self.sampling
        )

    def act(self, obs: dict) -> dict:
        """固定提示词 + 观测 → llm_complete → 解析动作；解析失败确定性回退。

        - build_baseline_prompt / llm_complete 异常原样透传（实验态失败即停哲学）；
        - 解析规则：首个 RESET|ACTION1-7 命中；ACTION6 需后随两个 0-63 坐标；
        - 命中动作不在 obs.available_actions 中、或解析不出 → 回退
          available_actions 首个合法编号动作（确定性，无随机）。
        """
        messages = build_baseline_prompt(obs)
        text, usage = llm_complete(messages, self.sampling, self.scene, model=self.model)
        self.total_usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
        self.total_usage["completion_tokens"] += usage.get("completion_tokens", 0)
        self.total_usage["calls"] += 1
        return self._parse_action(text, obs)

    @staticmethod
    def _parse_action(text: str, obs: dict) -> dict:
        match = _ACTION_RE.search(text or "")
        if match:
            name = match.group(1)
            available = obs.get("available_actions") or []
            action_id = ACTION_NAMES.index(name)
            if action_id in available:
                if name != "ACTION6":
                    return {"name": name}
                tail = text[match.end():]
                coords = _COORDS_RE.search(tail)
                if coords:
                    x, y = int(coords.group(1)), int(coords.group(2))
                    if 0 <= x <= 63 and 0 <= y <= 63:
                        return {"name": "ACTION6", "x": x, "y": y}
        return _fallback_action(obs)


def make_baseline_policy(config: dict) -> BaselinePolicy:
    """构造裸基线策略对象。

    config 键：
    - scene（必填）: "experiment" | "submit"——异常处置场景标记；
    - model（可选，默认 ""）: 模型名，空则用 llm_complete 端点默认（ARC_MODEL/内置默认）；
    - sampling（可选，默认 BASELINE_SAMPLING）：采样参数（默认 temperature=0 保证确定性）。

    配置缺 scene / scene 非法 / 类型不符 → ConfigError。
    """
    if not isinstance(config, dict):
        raise ConfigError(f"config 必须是 dict，实际是 {type(config).__name__}: {config!r}")
    if "scene" not in config:
        raise ConfigError(f"config 缺少 scene: {config!r}")
    scene = config["scene"]
    if scene not in ("experiment", "submit"):
        raise ConfigError(f"scene 必须是 experiment|submit，实际是 {scene!r}")
    model = config.get("model", "")
    if not isinstance(model, str):
        raise ConfigError(f"model 必须是字符串，实际是 {type(model).__name__}: {model!r}")
    sampling = config.get("sampling", BASELINE_SAMPLING)
    if not isinstance(sampling, dict):
        raise ConfigError(f"sampling 必须是 dict，实际是 {type(sampling).__name__}: {sampling!r}")
    return BaselinePolicy(scene=scene, model=model, sampling=sampling)
