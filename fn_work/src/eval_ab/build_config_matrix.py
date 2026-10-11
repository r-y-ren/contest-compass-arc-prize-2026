"""配置矩阵展开：配置声明 → 待跑配置列表（责任文档 R5）。

纯函数。策略组合四态（A/B 全因子）：
    baseline / curriculum / regularized / curriculum+regularized（全开）
组合语义（run_config_batch 按此构造）：curriculum+regularized =
课程包装(经验正则包装(裸基线))——编排层在外、记忆层在内。
场景标记恒为 experiment（R5 评测上下文；提交态走 build_kaggle_package 独立路径）。
"""

from __future__ import annotations

POLICY_KINDS = (
    "baseline",
    "curriculum",
    "regularized",
    "curriculum+regularized",
)

_PARAM_KEYS = ("baseline_config", "curriculum_config", "regularized_config")

# 默认四配置（A/B 对照标准阵：裸基线 / +R3 / +R4 / 全开）。
DEFAULT_DECLARATIONS = [
    {"name": "baseline", "policy": "baseline"},
    {"name": "plus_curriculum", "policy": "curriculum"},
    {"name": "plus_regularized", "policy": "regularized"},
    {"name": "full", "policy": "curriculum+regularized"},
]


class ConfigError(RuntimeError):
    """配置声明非法：非列表/项非映射/name 缺失·重复/policy 未知/参数段类型错。"""


def build_config_matrix(declarations: list = None) -> list:
    """由配置声明展开为待跑配置列表（名字→策略组合+场景标记 experiment）；纯函数。

    - declarations 为 None → 默认四配置；
    - 每项声明 {"name": str, "policy": POLICY_KINDS 之一, 可选三段参数 dict}；
    - 输出每项 {"name", "policy", "scene": "experiment", baseline_config,
      curriculum_config, regularized_config}——参数段缺省 {}（工厂各自套默认）。
    """
    if declarations is None:
        declarations = DEFAULT_DECLARATIONS
    if not isinstance(declarations, list):
        raise ConfigError(f"配置声明必须是列表，实际是 {type(declarations).__name__}")

    matrix, seen = [], set()
    for idx, declaration in enumerate(declarations):
        if not isinstance(declaration, dict):
            raise ConfigError(
                f"配置声明[{idx}] 必须是映射，实际是 {type(declaration).__name__}: {declaration!r}"
            )
        name = declaration.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ConfigError(f"配置声明[{idx}] 缺合法 name: {declaration!r}")
        if name in seen:
            raise ConfigError(f"配置名重复: {name}")
        seen.add(name)
        policy = declaration.get("policy")
        if policy not in POLICY_KINDS:
            raise ConfigError(
                f"配置 {name} 的 policy 必须是 {'/'.join(POLICY_KINDS)} 之一，实际是 {policy!r}"
            )
        entry = {"name": name, "policy": policy, "scene": "experiment"}
        for key in _PARAM_KEYS:
            value = declaration.get(key, {})
            if not isinstance(value, dict):
                raise ConfigError(f"配置 {name} 的 {key} 必须是 dict，实际是 {value!r}")
            entry[key] = dict(value)
        matrix.append(entry)
    return matrix
