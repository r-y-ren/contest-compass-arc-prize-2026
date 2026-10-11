"""verify_package_layout 单测：完整包过/缺件清单化/入口语法错捕获/空目录。"""

from src.build_kaggle_package.verify_package_layout import verify_package_layout


def _make_package(tmp_path, entry_source='X = 1\n', with_src=True, with_req=True, with_freeze=True):
    root = tmp_path / "pkg"
    (root / "agent").mkdir(parents=True)
    (root / "agent" / "my_agent.py").write_text(entry_source, encoding="utf-8")
    if with_src:
        (root / "src").mkdir(exist_ok=True)
        (root / "src" / "__init__.py").write_text("", encoding="utf-8")
    if with_req:
        (root / "requirements.txt").write_text("arc-agi==0.9.9\n", encoding="utf-8")
    if with_freeze:
        (root / "freeze.json").write_text('{"commit": "abc"}\n', encoding="utf-8")
    return root


# ① 完整包：通过且无差异


def test_complete_package_passes(tmp_path):
    ok, issues = verify_package_layout(str(_make_package(tmp_path)))
    assert ok is True and issues == []


# ② 缺件：逐项差异、不抛异常


def test_missing_items_listed(tmp_path):
    root = _make_package(tmp_path, with_src=False, with_req=False, with_freeze=False)

    ok, issues = verify_package_layout(str(root))

    assert ok is False
    assert len(issues) == 3
    assert any("缺少 src" in i for i in issues)
    assert any("缺少 requirements.txt" in i for i in issues)
    assert any("缺少 freeze.json" in i for i in issues)


def test_missing_package_dir_listed(tmp_path):
    ok, issues = verify_package_layout(str(tmp_path / "nope"))

    assert ok is False
    assert len(issues) == 4  # 四必需项全缺
    assert all(i.startswith("缺少") for i in issues)


# ③ 入口编译检查：语法错被捕获并进差异清单


def test_broken_entry_compile_error_captured(tmp_path):
    root = _make_package(tmp_path, entry_source="def broken(:\n    pass\n")

    ok, issues = verify_package_layout(str(root))

    assert ok is False
    assert any("入口编译失败" in i for i in issues)
    assert len(issues) == 1  # 其余件齐全


def test_valid_class_entry_compiles(tmp_path):
    root = _make_package(tmp_path, entry_source="class MyAgent:\n    pass\n")

    ok, issues = verify_package_layout(str(root))

    assert ok is True and issues == []
