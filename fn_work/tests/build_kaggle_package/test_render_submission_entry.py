"""render_submission_entry 单测：契约驱动渲染/配置解析/适配器协议/编译合法。"""

import ast

import pytest

from src.build_kaggle_package.render_submission_entry import (
    DEFAULT_CONTRACT,
    PackageError,
    render_submission_entry,
)


# ① 渲染产物：含 BEST_CONFIG 常量、适配器类、submit 场景


def test_renders_entry_with_constants_and_adapter():
    source = render_submission_entry("full")

    assert "BEST_CONFIG" in source
    assert "'policy': 'curriculum+regularized'" in source
    assert "class MyAgent" in source
    assert "scene': 'submit'" in source or '"scene": "submit"' in source
    assert "def is_done(self, frames, latest_frame)" in source
    assert "def choose_action(self, frames, latest_frame)" in source
    assert "GameAction.from_name" in source  # 动作转换
    assert "normalize_obs" in source  # 观测归一化桥


def test_rendered_source_parses_as_valid_python():
    source = render_submission_entry("baseline")
    tree = ast.parse(source)  # 语法合法
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    assert "MyAgent" in classes and "_build_policy" in functions


# ② 配置解析：名字→默认阵；dict 直用；未知名报错


def test_config_name_resolved_from_default_matrix():
    source = render_submission_entry("plus_curriculum")
    assert "'policy': 'curriculum'" in source


def test_config_dict_used_directly():
    config = {"name": "custom-x", "policy": "baseline", "scene": "experiment",
              "baseline_config": {"model": "qwen3-32b"}, "curriculum_config": {}, "regularized_config": {}}
    source = render_submission_entry(config)
    assert "'model': 'qwen3-32b'" in source


def test_unknown_config_name_raises():
    with pytest.raises(PackageError, match="未知配置名"):
        render_submission_entry("no-such-config")


def test_bad_config_object_raises():
    with pytest.raises(PackageError, match="配置名或含 name/policy"):
        render_submission_entry(42)


# ③ 契约模板：字段驱动；缺字段报错；缺省用赛站实核契约


def test_contract_overrides_class_and_import():
    source = render_submission_entry(
        "baseline",
        {"entry_path": "agent/custom.py", "agent_class": "CoolAgent", "base_import": "from mykit import Base"},
    )
    assert "class CoolAgent(Base)" in source
    assert "from mykit import Base" not in source  # 基类仅取符号名，import 由 kit 环境承担


def test_contract_missing_field_raises():
    with pytest.raises(PackageError, match="契约模板缺字段"):
        render_submission_entry("baseline", {"entry_path": "agent/my_agent.py"})


def test_default_contract_shape():
    assert DEFAULT_CONTRACT["entry_path"] == "agent/my_agent.py"
    assert DEFAULT_CONTRACT["agent_class"] == "MyAgent"


# ④ 确定性：同输入两次渲染，除时间戳外逐字节一致


def test_deterministic_modulo_timestamp():
    a = render_submission_entry("full")
    b = render_submission_entry("full")
    strip = lambda s: "\n".join(l for l in s.splitlines() if "生成时间" not in l)
    assert strip(a) == strip(b)
