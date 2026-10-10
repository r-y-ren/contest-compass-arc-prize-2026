def regularize_experience(store: dict, obs: dict, budget: int) -> tuple:
    """从经验库生成本步入提示子集：相关性/新近度/去重正则打分截断，返回 (子集, 取舍日志)。"""
    raise NotImplementedError("unimplemented:fn:regularize_experience")
