def submit_action(env, action: dict, scene: str) -> dict:
    """向环境提交一步动作，返回下一观测或终局信号；非法动作按 SDK 错误码处置。"""
    raise NotImplementedError("unimplemented:fn:submit_action")
