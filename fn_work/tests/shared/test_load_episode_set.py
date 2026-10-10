"""load_episode_set 实测：正常读入/缺省与显式 seed/缺文件/坏 YAML/空·重复·非字符串 ID/非整数 seed。"""

import pytest

from src.shared.load_episode_set import ConfigError, load_episode_set


def _write_cfg(tmp_path, content, filename="episodes.yaml"):
    path = tmp_path / filename
    path.write_text(content, encoding="utf-8")
    return str(path)


def test_ok_defaults_seed_zero(tmp_path):
    """① 正常读入：name + episode_ids，缺省 seed=0，ID 保持文件顺序。"""
    path = _write_cfg(tmp_path, 'name: demo\nepisode_ids:\n  - "00762c0b"\n  - "1e0a9b12"\n')

    result = load_episode_set(path)

    assert result == {"name": "demo", "episode_ids": ["00762c0b", "1e0a9b12"], "seed": 0}


def test_explicit_seed(tmp_path):
    """② 显式 seed：原样透传为 int。"""
    path = _write_cfg(tmp_path, "name: demo\nepisode_ids:\n  - aabb\nseed: 42\n")

    result = load_episode_set(path)

    assert result["seed"] == 42 and isinstance(result["seed"], int)


def test_missing_file_raises(tmp_path):
    """③ 文件不存在 → ConfigError。"""
    with pytest.raises(ConfigError, match="不存在"):
        load_episode_set(str(tmp_path / "nope.yaml"))


def test_bad_yaml_raises(tmp_path):
    """④ 坏 YAML（流序列未闭合）→ ConfigError。"""
    path = _write_cfg(tmp_path, 'name: bad\nepisode_ids: ["a", "b"\n')

    with pytest.raises(ConfigError, match="不是合法 YAML"):
        load_episode_set(path)


def test_empty_episode_ids_raises(tmp_path):
    """⑤ 空 episode_ids → ConfigError。"""
    path = _write_cfg(tmp_path, "name: demo\nepisode_ids: []\nseed: 1\n")

    with pytest.raises(ConfigError, match="episode_ids 为空列表"):
        load_episode_set(path)


def test_duplicate_ids_raises(tmp_path):
    """⑥ 重复局 ID → ConfigError，消息指明重复项。"""
    path = _write_cfg(tmp_path, "name: demo\nepisode_ids:\n  - a\n  - b\n  - a\n")

    with pytest.raises(ConfigError, match="重复局 ID: a"):
        load_episode_set(path)


def test_non_string_id_raises(tmp_path):
    """⑦ 非字符串局 ID → ConfigError，消息指明问题项。"""
    path = _write_cfg(tmp_path, "name: demo\nepisode_ids:\n  - a\n  - 7\n")

    with pytest.raises(ConfigError, match=r"episode_ids\[1\] 必须是字符串.*7"):
        load_episode_set(path)


def test_non_integer_seed_raises(tmp_path):
    """⑧ seed 非整数（字符串）→ ConfigError。"""
    path = _write_cfg(tmp_path, "name: demo\nepisode_ids:\n  - a\nseed: forty-two\n")

    with pytest.raises(ConfigError, match="seed 必须是整数"):
        load_episode_set(path)


def test_bool_seed_raises(tmp_path):
    """补充：YAML 的 true/false 解析为 bool，不算整数（bool 是 int 子类，须显式排除）。"""
    path = _write_cfg(tmp_path, "name: demo\nepisode_ids:\n  - a\nseed: true\n")

    with pytest.raises(ConfigError, match="seed 必须是整数"):
        load_episode_set(path)


def test_blank_id_and_missing_key_and_non_mapping(tmp_path):
    """补充：空白局 ID / 缺 episode_ids 键 / 顶层非映射 → ConfigError。"""
    blank = _write_cfg(tmp_path, "name: demo\nepisode_ids:\n  - '  '\n", "blank.yaml")
    with pytest.raises(ConfigError, match=r"episode_ids\[0\] 为空局 ID"):
        load_episode_set(blank)

    missing = _write_cfg(tmp_path, "name: demo\nseed: 3\n", "missing.yaml")
    with pytest.raises(ConfigError, match="缺少 episode_ids"):
        load_episode_set(missing)

    non_map = _write_cfg(tmp_path, "- just\n- a list\n", "nonmap.yaml")
    with pytest.raises(ConfigError, match="顶层必须是映射"):
        load_episode_set(non_map)
