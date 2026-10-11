"""打包主流程：最优配置 → 可提交包目录（责任文档 R6）。

包结构（与 verify_package_layout 的契约清单一一对应）：
    <out_dir>/
      agent/my_agent.py   ← render_submission_entry（scene=submit 适配器）
      src/…               ← fn_work/src 拷贝（剔除 __pycache__）
      requirements.txt    ← fn_work/requirements.txt 派生（滤 pytest 注释）
      freeze.json         ← 冻结记录：git commit + 完整配置 + 生成时间
verify 自检不过 → PackageError（差异清单入消息）。
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from src.build_kaggle_package.render_submission_entry import (
    PackageError,
    render_submission_entry,
)
from src.build_kaggle_package.verify_package_layout import verify_package_layout
from src.eval_ab.build_config_matrix import build_config_matrix

# 本包源码根（fn_work/src）与 requirements 源头（fn_work/requirements.txt）。
_SRC_ROOT = Path(__file__).resolve().parents[1]
_REQUIREMENTS = Path(__file__).resolve().parents[2] / "requirements.txt"

# 打包排除：测试依赖与缓存不入提交件。
_REQUIREMENTS_EXCLUDE = {"pytest"}


def _git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True,
            cwd=str(_SRC_ROOT.parent),
        ).stdout.strip()
    except Exception:
        return "unknown"


def _package_requirements() -> str:
    lines = []
    for line in _REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.split("==")[0].split(">=")[0].strip() in _REQUIREMENTS_EXCLUDE:
            continue
        lines.append(stripped)
    return "\n".join(lines) + "\n"


def build_kaggle_package(best_config: str, out_dir: str) -> str:
    """打包主流程：选定最优配置→渲染入口→包结构自检→落成可提交包目录。

    - best_config：配置名（默认阵按名解析；未知 → PackageError）；
    - out_dir：包根目录（自动创建，已存在则覆盖同名文件）；
    - 返回包目录路径 str；verify 差异 → PackageError（消息含差异清单）。
    """
    config = next((c for c in build_config_matrix() if c["name"] == best_config), None)
    if config is None:
        raise PackageError(
            f"未知配置名: {best_config!r}（默认阵: {[c['name'] for c in build_config_matrix()]}）"
        )

    package = Path(out_dir)
    (package / "agent").mkdir(parents=True, exist_ok=True)
    (package / "agent" / "my_agent.py").write_text(
        render_submission_entry(config), encoding="utf-8"
    )

    shutil.copytree(
        _SRC_ROOT, package / "src",
        dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    (package / "requirements.txt").write_text(_package_requirements(), encoding="utf-8")
    freeze = {
        "commit": _git_commit(),
        "config": config,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sdk": "arc-agi==0.9.9",
    }
    (package / "freeze.json").write_text(
        json.dumps(freeze, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    ok, issues = verify_package_layout(str(package))
    if not ok:
        raise PackageError(f"包自检不过: {issues}")
    return str(package)
