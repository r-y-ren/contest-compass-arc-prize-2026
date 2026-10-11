"""build_config_matrix 单测：默认四配置/规范化/参数缺省/声明校验。"""

import pytest

from src.eval_ab.build_config_matrix import (
    DEFAULT_DECLARATIONS,
    POLICY_KINDS,
    ConfigError,
    build_config_matrix,
)


# ① 默认阵：四配置全因子、scene 恒 experiment


def test_default_matrix_four_configs():
    matrix = build_config_matrix()

    assert [c["name"] for c in matrix] == ["baseline", "plus_curriculum", "plus_regularized", "full"]
    assert [c["policy"] for c in matrix] == list(POLICY_KINDS)
    assert all(c["scene"] == "experiment" for c in matrix)


def test_default_params_empty_dicts():
    matrix = build_config_matrix()

    for config in matrix:
        assert config["baseline_config"] == {}
        assert config["curriculum_config"] == {}
        assert config["regularized_config"] == {}


# ② 自定义声明：规范化与参数透传


def test_custom_declaration_normalized_with_params():
    matrix = build_config_matrix([
        {"name": "my-base", "policy": "baseline",
         "baseline_config": {"model": "qwen3-32b", "sampling": {"temperature": 0}}},
    ])

    (config,) = matrix
    assert config == {
        "name": "my-base", "policy": "baseline", "scene": "experiment",
        "baseline_config": {"model": "qwen3-32b", "sampling": {"temperature": 0}},
        "curriculum_config": {}, "regularized_config": {},
    }


def test_empty_declaration_list_gives_empty_matrix():
    assert build_config_matrix([]) == []


def test_pure_function_input_not_mutated():
    declaration = [{"name": "x", "policy": "baseline", "baseline_config": {"scene": "experiment"}}]
    snapshot = [dict(d) for d in declaration]

    matrix = build_config_matrix(declaration)

    assert declaration == snapshot
    assert matrix[0]["baseline_config"] == {"scene": "experiment"}  # 浅拷贝隔离


# ③ 声明校验 → ConfigError


def test_non_list_declaration_raises():
    with pytest.raises(ConfigError, match="必须是列表"):
        build_config_matrix({"name": "x"})


def test_non_dict_entry_raises():
    with pytest.raises(ConfigError, match=r"\[0\] 必须是映射"):
        build_config_matrix(["baseline"])


@pytest.mark.parametrize("bad_name", [None, "", "  ", 42])
def test_bad_name_raises(bad_name):
    with pytest.raises(ConfigError, match="缺合法 name"):
        build_config_matrix([{"name": bad_name, "policy": "baseline"}])


def test_duplicate_names_raise():
    with pytest.raises(ConfigError, match="配置名重复"):
        build_config_matrix([
            {"name": "a", "policy": "baseline"},
            {"name": "a", "policy": "curriculum"},
        ])


def test_unknown_policy_raises():
    with pytest.raises(ConfigError, match="policy 必须是"):
        build_config_matrix([{"name": "a", "policy": "SGD"}])


def test_bad_param_section_raises():
    with pytest.raises(ConfigError, match="baseline_config 必须是 dict"):
        build_config_matrix([{"name": "a", "policy": "baseline", "baseline_config": "fast"}])
