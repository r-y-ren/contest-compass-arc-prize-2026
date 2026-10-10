"""对远端 vLLM（OpenAI 兼容）服务的对话补全封装。

拼请求体（模型名/消息列表/采样参数）→ 发送 → 解析回复文本；失败按场景处置：
- experiment：失败即抛 LLMServiceError（含原因），不重试；
- submit：有限重试（≤3 次尝试、指数退避），耗尽后降级返回安全回退动作文本。
记录请求耗时与 token 用量，随回复文本一并返回。
"""

from __future__ import annotations

import logging
import os
import time

import httpx

_DEFAULT_BASE_URL = "localhost:8000/v1"
_DEFAULT_MODEL = "qwen-27b-fp8"

_MAX_ATTEMPTS = 3        # submit 场景总尝试次数上限（首次 + 2 次重试）
_RETRY_BACKOFF_S = 0.5   # 退避基数：第 n 次失败后睡 _RETRY_BACKOFF_S * 2**(n-1) 秒
_REQUEST_TIMEOUT_S = 60.0

_RESERVED_KEYS = ("model", "messages")  # 采样参数不得覆盖请求体保留字段

# submit 重试耗尽后的安全回退动作文本（空动作，由上层按无操作处理）。
SAFE_FALLBACK = ""

_LOGGER = logging.getLogger(__name__)


class LLMServiceError(RuntimeError):
    """vLLM 服务请求失败：网络异常 / 超时 / 4xx-5xx / 响应体不可解析。"""


def _load_endpoint() -> tuple:
    """从环境变量 ARC_VLLM_BASE_URL / ARC_MODEL 读取 (base_url, model)，缺省用默认值。

    base_url 归一化为带 scheme、无尾斜杠形式，如 http://localhost:8000/v1。
    """
    base_url = (os.environ.get("ARC_VLLM_BASE_URL") or _DEFAULT_BASE_URL).strip().rstrip("/")
    if not base_url:
        base_url = _DEFAULT_BASE_URL
    if not (base_url.startswith("http://") or base_url.startswith("https://")):
        base_url = "http://" + base_url
    model = (os.environ.get("ARC_MODEL") or _DEFAULT_MODEL).strip() or _DEFAULT_MODEL
    return base_url, model


def llm_complete(messages: list, sampling: dict, scene: str) -> tuple:
    """对远端 vLLM 服务发一次对话补全，返回 (回复文本, 用量统计 dict)。

    用量统计含 prompt_tokens / completion_tokens / latency_ms / attempt。
    scene=="experiment"：失败抛 LLMServiceError（含原因）；
    scene=="submit"：≤3 次尝试（指数退避），耗尽后返回 SAFE_FALLBACK 不抛。
    """
    if scene not in ("experiment", "submit"):
        raise ValueError(f"未知 scene: {scene!r}（仅支持 experiment/submit）")

    base_url, model = _load_endpoint()
    url = base_url + "/chat/completions"
    payload = {"model": model, "messages": list(messages)}
    payload.update({k: v for k, v in (sampling or {}).items() if k not in _RESERVED_KEYS})

    started = time.perf_counter()
    last_reason = "未发起任何请求"
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            with httpx.Client(timeout=_REQUEST_TIMEOUT_S) as client:
                resp = client.post(url, json=payload)
            if resp.status_code >= 400:
                raise LLMServiceError(f"vLLM 返回 {resp.status_code}（{url}）: {resp.text[:200]!r}")
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            if not isinstance(text, str):
                raise LLMServiceError(f"响应 content 非字符串: {text!r}")
            raw_usage = data.get("usage")
            usage = raw_usage if isinstance(raw_usage, dict) else {}
            latency_ms = int((time.perf_counter() - started) * 1000)
            return text, {
                "prompt_tokens": int(usage.get("prompt_tokens") or 0),
                "completion_tokens": int(usage.get("completion_tokens") or 0),
                "latency_ms": latency_ms,
                "attempt": attempt,
            }
        except LLMServiceError as exc:
            last_reason = str(exc)
        except (httpx.TimeoutException, httpx.RequestError) as exc:
            last_reason = f"{type(exc).__name__}: {exc}"
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            last_reason = f"响应体不可解析 {type(exc).__name__}: {exc}"

        _LOGGER.warning(
            "llm_complete[%s] 第 %d/%d 次尝试失败: %s", scene, attempt, _MAX_ATTEMPTS, last_reason
        )
        if scene == "experiment":
            raise LLMServiceError(f"llm_complete[experiment] 失败: {last_reason}")
        if attempt < _MAX_ATTEMPTS:
            time.sleep(_RETRY_BACKOFF_S * (2 ** (attempt - 1)))

    # submit 重试耗尽：降级返回安全回退动作，不抛（失败原因已逐次告警留痕）。
    latency_ms = int((time.perf_counter() - started) * 1000)
    return SAFE_FALLBACK, {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "latency_ms": latency_ms,
        "attempt": _MAX_ATTEMPTS,
    }
