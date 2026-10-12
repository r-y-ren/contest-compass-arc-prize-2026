"""run_config_batch 单测：run_episode/日志打桩（密闭）；四组合构造与指标数学。"""

import pytest

from src.eval_ab import run_config_batch as rcb
from src.eval_ab.run_config_batch import ExperimentAbortError, run_config_batch
from src.make_curriculum_policy.make_curriculum_policy import CurriculumPolicy
from src.make_regularized_policy.make_regularized_policy import RegularizedPolicy
from src.shared.llm_complete import LLMServiceError


def _config(policy="baseline", name="c1", **sections):
    return {"name": name, "policy": policy, "scene": "experiment",
            "baseline_config": {}, "curriculum_config": {}, "regularized_config": {}, **sections}


def _result(outcome, steps, tokens=(10, 4)):
    return {"episode_id": "g", "outcome": outcome, "steps": steps, "duration_s": 0.5,
            "levels_completed": 0, "win_levels": 1,
            "token_usage": {"prompt_tokens": tokens[0], "completion_tokens": tokens[1], "calls": 1}}


@pytest.fixture
def stub(monkeypatch):
    """打桩 run_episode（按序吐结果或异常）与 append_jsonl_log；记录调用。"""
    calls = {"episodes": [], "logs": []}

    def _fake_run_episode(spec, policy, run_id):
        calls["episodes"].append((spec, policy, run_id))
        item = calls["queue"].pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    monkeypatch.setattr(rcb, "run_episode", _fake_run_episode)
    monkeypatch.setattr(rcb, "append_jsonl_log", lambda run_id, event, payload: calls["logs"].append((event, payload)))
    return calls


def _queue(calls, items):
    calls["queue"] = list(items)


EPISODE_SET = {"name": "demo", "episode_ids": ["g1", "g2"], "seed": 7}


# ① 四组合构造：包装层序（课程外/正则内）与 scene 传递


def test_policy_kinds_wrap_in_order(stub):
    from src.make_baseline_policy.make_baseline_policy import BaselinePolicy

    cases = {
        "baseline": BaselinePolicy,
        "curriculum": CurriculumPolicy,
        "regularized": RegularizedPolicy,
        "curriculum+regularized": CurriculumPolicy,
    }
    for policy_kind, expected_type in cases.items():
        _queue(stub, [_result("GAME_OVER", 3), _result("GAME_OVER", 3)])
        run_config_batch(_config(policy=policy_kind, name=f"c-{policy_kind}"), EPISODE_SET, "r")
        wrapper = stub["episodes"][-1][1]
        assert isinstance(wrapper, expected_type), policy_kind

    # 全开组合：外层课程，其内层应为正则包装
    _queue(stub, [_result("GAME_OVER", 3), _result("GAME_OVER", 3)])
    run_config_batch(_config(policy="curriculum+regularized", name="full"), EPISODE_SET, "r")
    full_wrapper = stub["episodes"][-1][1]
    assert isinstance(full_wrapper.inner, RegularizedPolicy)
    assert isinstance(full_wrapper.inner.inner, BaselinePolicy)


def test_episode_specs_carry_set_seed(stub):
    _queue(stub, [_result("WIN", 2), _result("GAME_OVER", 6)])

    run_config_batch(_config(), EPISODE_SET, "run-1")

    assert [spec for spec, _, _ in stub["episodes"]] == [
        {"game_id": "g1", "seed": 7}, {"game_id": "g2", "seed": 7},
    ]
    assert all(run_id == "run-1" for _, _, run_id in stub["episodes"])


# ② 指标数学：成功率/平均步数/时长与 token 汇总


def test_metrics_math(stub):
    _queue(stub, [_result("WIN", 2, (10, 4)), _result("GAME_OVER", 6, (1, 1))])

    metrics = run_config_batch(_config(), EPISODE_SET, "run-2")

    assert metrics["name"] == "c1" and metrics["policy"] == "baseline"
    assert metrics["episodes"] == 2 and metrics["wins"] == 1
    assert metrics["success_rate"] == 0.5
    assert metrics["avg_steps"] == 4.0
    assert metrics["duration_s"] == 1.0
    assert metrics["token_usage"] == {"prompt_tokens": 11, "completion_tokens": 5, "calls": 2}
    assert len(metrics["episode_results"]) == 2
    events = [event for event, _ in stub["logs"]]
    assert events[0] == "config_batch_start" and events[-1] == "config_batch_end"


def test_empty_episode_set_zero_metrics(stub):
    _queue(stub, [])

    metrics = run_config_batch(_config(), {"episode_ids": [], "seed": 0}, "r")

    assert metrics["episodes"] == 0 and metrics["success_rate"] == 0.0 and metrics["avg_steps"] == 0.0


# ③ 实验态中止：任一局失败 → ExperimentAbortError 附局 ID；后续局不再跑


def test_episode_failure_aborts_with_episode_id(stub):
    _queue(stub, [_result("WIN", 2), LLMServiceError("vLLM down"), _result("WIN", 1)])

    with pytest.raises(ExperimentAbortError, match=r"第 2 局（g2）失败.*LLMServiceError.*vLLM down"):
        run_config_batch(_config(), {"episode_ids": ["g1", "g2", "g3"], "seed": 0}, "run-3")

    assert len(stub["episodes"]) == 2  # 第三局未跑


def test_policy_construction_failure_aborts(stub):
    bad = _config(policy="curriculum", curriculum_config={"sources": {"a": "not-a-list"}})

    with pytest.raises(ExperimentAbortError, match="策略构造失败"):
        run_config_batch(bad, EPISODE_SET, "run-4")


def test_unknown_policy_kind_aborts(stub):
    with pytest.raises(ExperimentAbortError, match="未知 policy 组合"):
        run_config_batch({"name": "x", "policy": "SGD", "scene": "experiment",
                          "baseline_config": {}, "curriculum_config": {}, "regularized_config": {}},
                         EPISODE_SET, "run-5")


def test_curriculum_sources_defaulted_from_episode_set(stub):
    """课程配置缺 sources 时按局集合成源池（Ruling 2026-10-12），不再第一局即 CurriculumError。"""
    from src.make_curriculum_policy.make_curriculum_policy import CurriculumPolicy

    _queue(stub, [_result("GAME_OVER", 3), _result("GAME_OVER", 3)])
    run_config_batch(_config(policy="curriculum", name="c-def"), EPISODE_SET, "run-def")

    wrapper = stub["episodes"][-1][1]
    assert isinstance(wrapper, CurriculumPolicy)
    assert set(wrapper._source_history) == {"g1", "g2"}


def test_explicit_sources_not_overridden(stub):
    _queue(stub, [_result("GAME_OVER", 3), _result("GAME_OVER", 3)])
    explicit = _config(policy="curriculum", name="c-exp")
    explicit["curriculum_config"] = {"sources": {"demo-src": []}}

    run_config_batch(explicit, EPISODE_SET, "run-exp")

    assert set(stub["episodes"][-1][1]._source_history) == {"demo-src"}
