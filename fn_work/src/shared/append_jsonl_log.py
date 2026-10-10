def append_jsonl_log(run_id: str, event: str, payload: dict) -> None:
    """向当日 JSONL 日志原子追加结构化记录并镜像控制台；磁盘失败不吞异常。"""
    raise NotImplementedError("unimplemented:fn:append_jsonl_log")
