"""run_episode 包内私有件：SDK 帧对象归一化与环境错误基类。

不在责任文档函数树内（实现细节，非新顶层函数）：
- normalize_obs: FrameDataRaw（pydantic + numpy frame 私有属性）→ 纯 JSON dict，
  使观测可进 render_obs / append_jsonl_log（二者都要求可 JSON 序列化）；
- EnvError: SDK 环境交互错误基类（connect_env 包装 SDK 异常、submit_action 失败归一化共用）。
"""

from __future__ import annotations


class EnvError(RuntimeError):
    """官方 SDK 环境交互失败：初始化/连接/步进请求失败（消息带局 ID）。"""


def normalize_obs(frame) -> dict:
    """把 SDK 观测对象归一化为纯 JSON dict。

    - FrameDataRaw（有 model_dump）：model_dump(mode="json") 取九字段
      （枚举→值、guid/full_reset 原样），frame 为 PrivateAttr 不进 dump，
      从 .frame 属性逐帧 tolist()（numpy 数组不可 JSON 序列化）；
    - 已是 dict：原样浅拷贝（假环境/测试夹具走此分支）；
    - action_input 只保留 id/data 两个键（reasoning 为调用方回显大对象，不进日志与提示）。
    """
    if hasattr(frame, "model_dump"):
        data = frame.model_dump(mode="json")
        raw_frames = getattr(frame, "frame", None) or []
        data["frame"] = [f.tolist() if hasattr(f, "tolist") else f for f in raw_frames]
    elif isinstance(frame, dict):
        data = dict(frame)
    else:
        raise EnvError(f"观测对象既非 FrameDataRaw 也非 dict: {type(frame).__name__}: {frame!r}")

    action_input = data.get("action_input")
    if isinstance(action_input, dict):
        # 只保留 id/data：reasoning 是调用方回显的可选大对象（≤16KB），不进日志与提示。
        data["action_input"] = {"id": action_input.get("id"), "data": action_input.get("data", {})}
    elif action_input is not None:
        # 上游塞了非 dict 对象：降级保留可取字段。
        data["action_input"] = {"id": getattr(action_input, "id", None), "data": {}}
    return data
