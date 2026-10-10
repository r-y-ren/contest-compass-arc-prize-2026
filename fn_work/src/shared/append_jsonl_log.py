"""当日 JSONL 结构化日志：原子追加 + 控制台镜像。"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

_DEFAULT_LOG_DIR = "fn_work/logs"


class LogWriteError(RuntimeError):
    """日志写盘失败（OSError 的包装），供调用方感知磁盘故障。"""


def _log_dir() -> Path:
    """解析日志根目录：ARC_LOG_DIR 环境变量（默认 fn_work/logs），相对路径基于 cwd。"""
    raw = os.environ.get("ARC_LOG_DIR") or _DEFAULT_LOG_DIR
    path = Path(raw)
    return path if path.is_absolute() else Path.cwd() / path


def append_jsonl_log(run_id: str, event: str, payload: dict) -> None:
    """向当日 JSONL 日志原子追加一条结构化记录，并镜像一行到 stdout。

    - 记录形如 {"ts": ISO8601, "run_id": str, "event": str, "payload": dict}；
    - 文件名 f"{当天YYYYMMDD}.jsonl"，以 "a"（O_APPEND）打开，整行（含换行）
      单次 write 调用落盘后 flush+fsync，同文件多进程/多句柄追加不丢行；
    - 目录不存在则 mkdir(parents=True) 自动创建；
    - 磁盘失败（OSError）包装为 LogWriteError 抛出，不吞异常、不镜像控制台。
    """
    now = datetime.now().astimezone()
    record = {"ts": now.isoformat(), "run_id": run_id, "event": event, "payload": payload}
    line = json.dumps(record, ensure_ascii=False) + "\n"
    path = _log_dir() / f"{now:%Y%m%d}.jsonl"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line)
            fh.flush()
            os.fsync(fh.fileno())
    except OSError as exc:
        raise LogWriteError(f"日志写盘失败 {path}: {exc}") from exc
    sys.stdout.write(line)
    sys.stdout.flush()
