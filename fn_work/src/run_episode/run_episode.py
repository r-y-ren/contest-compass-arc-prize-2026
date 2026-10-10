def run_episode(spec: dict, policy, run_id: str) -> dict:
    """执行一局完整交互：连接环境→步循环（取观测/调策略/提交动作/写日志）→返回 EpisodeResult。"""
    raise NotImplementedError("unimplemented:fn:run_episode")
