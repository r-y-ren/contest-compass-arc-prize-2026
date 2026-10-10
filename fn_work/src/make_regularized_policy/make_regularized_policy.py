def make_regularized_policy(inner_policy, memory_config: dict):
    """构造经验正则包装策略：维护经验库，act 时并入正则化经验子集，局终入库。"""
    raise NotImplementedError("unimplemented:fn:make_regularized_policy")
