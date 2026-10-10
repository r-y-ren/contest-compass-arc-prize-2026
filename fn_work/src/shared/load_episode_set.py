"""局集配置加载：YAML 读入 + 结构校验 + 规范化。

局集配置形如：

    name: demo            # 可选 str，缺省 ""
    episode_ids:          # 必填，非空字符串列表、不得重复、各项非空
      - 00762c0b
      - 1e0a9b12
    seed: 42              # 可选 int，缺省 0

局 ID 存在性校验（B2 债务①，2026-10-10 清）：调用方把官方 SDK 局索引
（arc.get_environments() 的 game_id 列表）经 known_episode_ids 注入则逐一核对，
不注入则跳过（密闭测试/未接 SDK 场景）——校验逻辑在本函数内，网络边界在调用方。
"""

from pathlib import Path
from typing import Iterable, Optional

import yaml

_DEFAULT_SEED = 0
_DEFAULT_NAME = ""


class ConfigError(RuntimeError):
    """局集配置不合法：文件缺失/坏 YAML/结构缺陷（缺键、空列表、非字符串 ID、重复 ID、seed 非整数）/局 ID 不在已知索引中。"""


def _base_id(episode_id: str) -> str:
    """取局 ID 的基础名：'-' 前部分（'ls20-016295f7601e' → 'ls20'；无 '-' 原样）。"""
    return episode_id.split("-", 1)[0]


def load_episode_set(config_path: str, known_episode_ids: Optional[Iterable[str]] = None) -> dict:
    """读取局集配置（YAML）并校验结构，返回规范化局集 dict。

    返回形如 {"name": str, "episode_ids": [str, ...], "seed": int}：
    - name 缺省 ""；seed 缺省 0；episode_ids 校验通过后按文件顺序原样返回；
    - 文件不存在 / 坏 YAML / 顶层非映射 → ConfigError；
    - 缺 episode_ids / 非列表 / 空列表 / 含非字符串或空 ID / 重复 → ConfigError（消息指明问题项）；
    - seed 存在但非整数（bool 亦不算）→ ConfigError；
    - known_episode_ids 给定时逐局核对存在性：精确命中，或配置 ID 的基础名
      与某已知 ID 的基础名一致（'ls20' 匹配 'ls20-016295f7601e'，短名取最新版，
      与 SDK make() 的解析规则一致）；未命中 → ConfigError（消息带该局 ID 与已知局数）。
    """
    path = Path(config_path)
    if not path.is_file():
        raise ConfigError(f"局集配置文件不存在: {path}")

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        raise ConfigError(f"局集配置不是合法 YAML: {path} ({exc})") from exc
    except OSError as exc:
        raise ConfigError(f"局集配置读取失败: {path} ({exc})") from exc

    if not isinstance(raw, dict):
        raise ConfigError(f"局集配置顶层必须是映射(dict)，实际是 {type(raw).__name__}: {path}")

    name = raw.get("name", _DEFAULT_NAME)
    if not isinstance(name, str):
        raise ConfigError(f"name 必须是字符串，实际是 {type(name).__name__}: {name!r}")

    if "episode_ids" not in raw:
        raise ConfigError(f"局集配置缺少 episode_ids: {path}")
    episode_ids = raw["episode_ids"]
    if not isinstance(episode_ids, list):
        raise ConfigError(
            f"episode_ids 必须是列表，实际是 {type(episode_ids).__name__}: {episode_ids!r}"
        )
    if not episode_ids:
        raise ConfigError(f"episode_ids 为空列表，至少需要一个局 ID: {path}")

    seen = set()
    for idx, episode_id in enumerate(episode_ids):
        if not isinstance(episode_id, str):
            raise ConfigError(
                f"episode_ids[{idx}] 必须是字符串，实际是 {type(episode_id).__name__}: {episode_id!r}"
            )
        if not episode_id.strip():
            raise ConfigError(f"episode_ids[{idx}] 为空局 ID: {episode_id!r}")
        if episode_id in seen:
            raise ConfigError(f"episode_ids 存在重复局 ID: {episode_id}（第 {idx} 项）")
        seen.add(episode_id)

    if known_episode_ids is not None:
        known = list(known_episode_ids)
        known_exact = set(known)
        known_bases = {_base_id(k) for k in known}
        for idx, episode_id in enumerate(episode_ids):
            if episode_id in known_exact or _base_id(episode_id) in known_bases:
                continue
            raise ConfigError(
                f"episode_ids[{idx}] 局 ID 不在官方 SDK 局索引中: {episode_id}"
                f"（已知局 {len(known)} 个；短名按基础名匹配，如 ls20 匹配 ls20-<版本>）"
            )

    seed = raw.get("seed", _DEFAULT_SEED)
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ConfigError(f"seed 必须是整数，实际是 {type(seed).__name__}: {seed!r}")

    return {"name": name, "episode_ids": list(episode_ids), "seed": seed}
