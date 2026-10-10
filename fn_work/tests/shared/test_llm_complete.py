"""llm_complete 单测：全量 mock httpx.Client，不发真网络。"""

import httpx
import pytest

from src.shared import llm_complete as llm_mod
from src.shared.llm_complete import SAFE_FALLBACK, LLMServiceError, _load_endpoint

MSGS = [{"role": "user", "content": "2+2=?"}]
SAMPLING = {"temperature": 0.2, "max_tokens": 128}


def _ok(text="ok", prompt_tokens=10, completion_tokens=5):
    body = {
        "id": "chatcmpl-test",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens},
    }
    return httpx.Response(200, json=body)


def _server_error():
    return httpx.Response(500, text="upstream panic")


def _install(monkeypatch, outcomes):
    """把 httpx.Client 换成按序吐 outcomes 的假客户端；返回请求捕获列表。"""
    captured = []

    class FakeClient:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def post(self, url, json=None):
            captured.append((url, json))
            item = outcomes.pop(0)
            if isinstance(item, Exception):
                raise item
            return item

    monkeypatch.setattr(llm_mod.httpx, "Client", FakeClient)
    monkeypatch.setattr(llm_mod, "_RETRY_BACKOFF_S", 0)  # 测试不真睡
    monkeypatch.delenv("ARC_VLLM_BASE_URL", raising=False)
    monkeypatch.delenv("ARC_MODEL", raising=False)
    return captured


def test_normal_return_parses_text_and_usage(monkeypatch):
    captured = _install(monkeypatch, [_ok("final answer", 11, 7)])

    text, usage = llm_mod.llm_complete(MSGS, SAMPLING, "experiment")

    assert text == "final answer"
    assert usage["prompt_tokens"] == 11
    assert usage["completion_tokens"] == 7
    assert usage["attempt"] == 1
    assert isinstance(usage["latency_ms"], int) and usage["latency_ms"] >= 0

    assert len(captured) == 1
    url, payload = captured[0]
    assert url == "http://localhost:8000/v1/chat/completions"
    assert payload["model"] == "qwen-27b-fp8"
    assert payload["messages"] == MSGS
    assert payload["temperature"] == 0.2
    assert payload["max_tokens"] == 128


def test_experiment_5xx_raises_without_retry(monkeypatch):
    captured = _install(monkeypatch, [_server_error()])

    with pytest.raises(LLMServiceError) as excinfo:
        llm_mod.llm_complete(MSGS, SAMPLING, "experiment")

    assert "500" in str(excinfo.value)
    assert len(captured) == 1  # experiment 失败即抛，不重试


def test_submit_retries_then_succeeds_on_third(monkeypatch):
    captured = _install(monkeypatch, [_server_error(), _server_error(), _ok("third try")])

    text, usage = llm_mod.llm_complete(MSGS, SAMPLING, "submit")

    assert text == "third try"
    assert usage["attempt"] == 3
    assert usage["prompt_tokens"] == 10
    assert usage["completion_tokens"] == 5
    assert len(captured) == 3


def test_submit_exhausted_retries_returns_safe_fallback(monkeypatch):
    captured = _install(monkeypatch, [_server_error(), _server_error(), _server_error()])

    text, usage = llm_mod.llm_complete(MSGS, SAMPLING, "submit")  # 不抛

    assert text == SAFE_FALLBACK
    assert usage["attempt"] == 3
    assert usage["prompt_tokens"] == 0
    assert usage["completion_tokens"] == 0
    assert isinstance(usage["latency_ms"], int) and usage["latency_ms"] >= 0
    assert len(captured) == 3


def test_experiment_timeout_raises_like_5xx(monkeypatch):
    _install(monkeypatch, [httpx.ReadTimeout("read timed out")])

    with pytest.raises(LLMServiceError) as excinfo:
        llm_mod.llm_complete(MSGS, SAMPLING, "experiment")

    assert "ReadTimeout" in str(excinfo.value)


def test_submit_timeout_exhausted_returns_safe_fallback(monkeypatch):
    captured = _install(monkeypatch, [httpx.ConnectTimeout("connect timed out")] * 3)

    text, usage = llm_mod.llm_complete(MSGS, SAMPLING, "submit")

    assert text == SAFE_FALLBACK
    assert usage["attempt"] == 3
    assert len(captured) == 3


def test_malformed_200_body_is_service_error(monkeypatch):
    _install(monkeypatch, [httpx.Response(200, json={"unexpected": "shape"})])

    with pytest.raises(LLMServiceError):
        llm_mod.llm_complete(MSGS, SAMPLING, "experiment")


def test_unknown_scene_rejected(monkeypatch):
    _install(monkeypatch, [_ok()])
    with pytest.raises(ValueError):
        llm_mod.llm_complete(MSGS, SAMPLING, "eval")


def test_load_endpoint_default_and_env(monkeypatch):
    monkeypatch.delenv("ARC_VLLM_BASE_URL", raising=False)
    monkeypatch.delenv("ARC_MODEL", raising=False)
    assert _load_endpoint() == ("http://localhost:8000/v1", "qwen-27b-fp8")

    monkeypatch.setenv("ARC_VLLM_BASE_URL", "https://gpu.box:9999/v1/")
    monkeypatch.setenv("ARC_MODEL", "deepseek-r1")
    assert _load_endpoint() == ("https://gpu.box:9999/v1", "deepseek-r1")

    monkeypatch.setenv("ARC_VLLM_BASE_URL", "gpu.box:8000/v1")  # 无 scheme 自动补 http://
    assert _load_endpoint()[0] == "http://gpu.box:8000/v1"
