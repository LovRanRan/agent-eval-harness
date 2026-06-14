"""Tests for the judge layer (Commit 4): LLM-as-judge + self-consistency."""

from __future__ import annotations

import pytest

from agent_eval_harness import (
    ChatModel,
    FactualCorrectnessJudge,
    Judge,
    JudgeMetric,
    JudgeVerdict,
    RunResult,
    SelfConsistentJudge,
    Task,
)


class FakeChatModel:
    """Returns queued responses (last one repeats once exhausted)."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = responses
        self._i = 0

    def complete(self, prompt: str) -> str:  # noqa: ARG002
        resp = self._responses[min(self._i, len(self._responses) - 1)]
        self._i += 1
        return resp


class StubJudge:
    """Returns verdicts with a queued sequence of scores."""

    def __init__(self, scores: list[float]) -> None:
        self._scores = scores
        self._i = 0

    def judge(self, task: Task, result: RunResult) -> JudgeVerdict:  # noqa: ARG002
        score = self._scores[min(self._i, len(self._scores) - 1)]
        self._i += 1
        return JudgeVerdict(score, "stub", ["h"] if score < 0.5 else [])


def _task() -> Task:
    return Task(
        id="t",
        bucket="architecture",
        repo_url="u",
        repo_pin="p",
        query="q",
        expected_key_facts=["a", "b", "c"],
        expected_route="architecture",
    )


def _result() -> RunResult:
    return RunResult(task_id="t", arch="x", answer="some answer", route_taken="architecture")


def test_protocols_are_satisfied() -> None:
    assert isinstance(FakeChatModel(["{}"]), ChatModel)
    assert isinstance(FactualCorrectnessJudge(FakeChatModel(["{}"])), Judge)
    assert isinstance(StubJudge([1.0]), Judge)


def test_judge_parses_valid_json() -> None:
    model = FakeChatModel(['{"score": 0.8, "reasoning": "good", "hallucinations": ["x"]}'])
    verdict = FactualCorrectnessJudge(model).judge(_task(), _result())
    assert verdict.score == 0.8
    assert verdict.reasoning == "good"
    assert verdict.flagged_hallucinations == ["x"]


def test_judge_tolerates_fences_and_prose() -> None:
    model = FakeChatModel(['Here is my verdict:\n```json\n{"score": 1.0}\n```\nThanks!'])
    verdict = FactualCorrectnessJudge(model).judge(_task(), _result())
    assert verdict.score == 1.0


def test_judge_clamps_score_to_unit_interval() -> None:
    model = FakeChatModel(['{"score": 1.7}'])
    assert FactualCorrectnessJudge(model).judge(_task(), _result()).score == 1.0


def test_judge_unparseable_degrades_to_zero() -> None:
    model = FakeChatModel(["not json at all"])
    verdict = FactualCorrectnessJudge(model).judge(_task(), _result())
    assert verdict.score == 0.0
    assert verdict.raw["raw"] == "not json at all"


def test_self_consistency_means_scores_and_marks_consistent() -> None:
    judge = SelfConsistentJudge(StubJudge([0.8, 0.82, 0.78]), runs=3)
    verdict = judge.judge(_task(), _result())
    assert verdict.score == pytest.approx(0.8, abs=0.01)
    assert verdict.raw["consistent"] is True
    assert verdict.raw["runs"] == 3


def test_self_consistency_flags_high_variance() -> None:
    judge = SelfConsistentJudge(StubJudge([0.1, 0.9, 0.5]), runs=3, variance_threshold=0.1)
    verdict = judge.judge(_task(), _result())
    assert verdict.raw["consistent"] is False


def test_self_consistency_rejects_zero_runs() -> None:
    with pytest.raises(ValueError, match="runs must be"):
        SelfConsistentJudge(StubJudge([1.0]), runs=0)


def test_judge_metric_adapts_verdict_to_metricscore() -> None:
    metric = JudgeMetric(StubJudge([0.9]))
    score = metric.score(_task(), _result())
    assert metric.name == "factual_correctness"
    assert score.value == 0.9
    assert score.detail["reasoning"] == "stub"
