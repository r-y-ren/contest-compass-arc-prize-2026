def llm_complete(messages: list, sampling: dict, scene: str) -> tuple:
    """对远端 vLLM 服务发一次对话补全：请求/解析/重试（实验态停/提交态降级）/记录用量。"""
    raise NotImplementedError("unimplemented:fn:llm_complete")
