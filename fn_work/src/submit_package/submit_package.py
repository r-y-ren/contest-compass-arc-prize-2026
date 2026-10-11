"""提交包到赛站：预检→（dry-run 回执 | CLI 提交有限重试）（责任文档 R6）。

契约备注（2026-10-11 实核，tracker Ruling）：ARC Prize 2026 为 code competition，
官方路径 = starter kit notebook 组装（make submit → kaggle kernels push）+ 网页
"Submit to Competition"；`kaggle competitions submit -f <包>` 为计划期假定的命令
形态（R6 验收原文）。本函数的实跑模式按计划形态执行（zip 包 + competitions
submit），被赛站拒绝时 SubmitError 附 CLI 原始输出原样暴露；真实提交是外部
动作，默认 dry_run=True 只做预检回执。
"""

from __future__ import annotations

import subprocess
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from src.build_kaggle_package.verify_package_layout import verify_package_layout
from src.shared.append_jsonl_log import append_jsonl_log

_MAX_ATTEMPTS = 3
_RETRY_BACKOFF_S = 2.0


class SubmitError(RuntimeError):
    """提交失败：包预检不过 / CLI 重试耗尽（消息附原始输出）。"""


def _zip_package(package_path: str) -> str:
    package = Path(package_path)
    zip_path = package.parent / f"{package.name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(package.rglob("*")):
            if file.is_file():
                zf.write(file, file.relative_to(package.parent))
    return str(zip_path)


def submit_package(competition_id: str, package_path: str, dry_run: bool = True) -> dict:
    """提交包到赛站，返回回执 dict（接收状态+时间戳）。

    - 预检：verify_package_layout 不过 → SubmitError（未触任何 CLI）；
    - dry_run=True（默认）：不出网，回执 {"status": "dry_run", ...} 含计划路径说明；
    - dry_run=False：zip 包 → `kaggle competitions submit <id> -f <zip>`，
      失败按指数退避重试 ≤3 次，耗尽 → SubmitError（附 CLI 原始输出）；
    - 两种模式均写 JSONL 事件（submit_dry_run / submit_result）。
    """
    if not competition_id or not isinstance(competition_id, str):
        raise SubmitError(f"competition_id 必须是非空字符串: {competition_id!r}")

    ok, issues = verify_package_layout(package_path)
    if not ok:
        raise SubmitError(f"包预检不过，未提交: {issues}")
    run_id = f"submit-{competition_id}"
    ts = datetime.now(timezone.utc).isoformat()

    if dry_run:
        receipt = {
            "status": "dry_run",
            "competition": competition_id,
            "package": str(package_path),
            "verified": True,
            "ts": ts,
            "planned_handoff": (
                "官方契约：starter kit notebook 组装（make submit → kaggle kernels push）"
                "+ 网页 Submit to Competition；本包 agent/my_agent.py 为交付物"
            ),
        }
        append_jsonl_log(run_id, "submit_dry_run", receipt)
        return receipt

    zip_path = _zip_package(package_path)
    command = ["kaggle", "competitions", "submit", "-c", competition_id, "-f", zip_path]
    last_output = ""
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        proc = subprocess.run(command, capture_output=True, text=True)
        last_output = (proc.stdout + proc.stderr).strip()
        if proc.returncode == 0:
            receipt = {
                "status": "submitted",
                "competition": competition_id,
                "package": str(package_path),
                "zip": zip_path,
                "verified": True,
                "attempt": attempt,
                "cli_output": last_output,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            append_jsonl_log(run_id, "submit_result", receipt)
            return receipt
        if attempt < _MAX_ATTEMPTS:
            time.sleep(_RETRY_BACKOFF_S * (2 ** (attempt - 1)))

    raise SubmitError(
        f"提交重试耗尽（{_MAX_ATTEMPTS} 次，赛站 {competition_id}）CLI 原始输出:\n{last_output}"
    )
