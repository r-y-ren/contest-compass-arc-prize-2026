"""build_kaggle_package 单测：真实组包（临时目录），结构与冻结记录逐项验。"""

import json

import pytest

from src.build_kaggle_package.build_kaggle_package import build_kaggle_package
from src.build_kaggle_package.render_submission_entry import PackageError
from src.build_kaggle_package.verify_package_layout import verify_package_layout


# ① 组包成功：四必需项齐、入口含配置、src 树在、verify 复核过


def test_build_produces_complete_package(tmp_path):
    package = build_kaggle_package("full", str(tmp_path / "pkg"))

    ok, issues = verify_package_layout(package)
    assert ok is True and issues == []

    entry = (tmp_path / "pkg" / "agent" / "my_agent.py").read_text(encoding="utf-8")
    assert "curriculum+regularized" in entry  # 选定配置进了入口
    assert (tmp_path / "pkg" / "src" / "run_episode" / "run_episode.py").exists()
    assert not (tmp_path / "pkg" / "src" / "run_episode" / "__pycache__").exists()  # 缓存剔除


# ② 冻结记录：commit/配置/时间戳齐


def test_freeze_record_complete(tmp_path):
    build_kaggle_package("baseline", str(tmp_path / "pkg"))

    freeze = json.loads((tmp_path / "pkg" / "freeze.json").read_text(encoding="utf-8"))
    assert freeze["config"]["name"] == "baseline"
    assert freeze["config"]["policy"] == "baseline"
    assert freeze["sdk"] == "arc-agi==0.9.9"
    assert "T" in freeze["generated_at"]
    assert freeze["commit"]  # unknown 或 hash，但字段在


# ③ requirements 派生：注释与 pytest 滤除、核心依赖保留


def test_requirements_derived_without_test_deps(tmp_path):
    build_kaggle_package("baseline", str(tmp_path / "pkg"))

    req = (tmp_path / "pkg" / "requirements.txt").read_text(encoding="utf-8")
    assert "arc-agi==0.9.9" in req and "httpx" in req and "pyyaml" in req
    assert "pytest" not in req
    assert "#" not in req


# ④ 未知配置名 → PackageError


def test_unknown_config_raises(tmp_path):
    with pytest.raises(PackageError, match="未知配置名"):
        build_kaggle_package("no-such", str(tmp_path / "pkg"))


# ⑤ 幂等重建：同目标二次组包不炸（覆盖同名）


def test_rebuild_same_dir_idempotent(tmp_path):
    build_kaggle_package("baseline", str(tmp_path / "pkg"))
    package = build_kaggle_package("full", str(tmp_path / "pkg"))

    entry = (tmp_path / "pkg" / "agent" / "my_agent.py").read_text(encoding="utf-8")
    assert "curriculum+regularized" in entry  # 新配置生效
    ok, _ = verify_package_layout(package)
    assert ok
