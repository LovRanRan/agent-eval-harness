"""Tests for the deterministic metrics (Commit 3)."""

from __future__ import annotations

from agent_eval_harness import (
    CitationGrounding,
    Claim,
    Metric,
    RoutingAccuracy,
    RunResult,
    Task,
    VerificationRate,
)
from agent_eval_harness.runner import ClaimLabel


def _task(expected_route: str = "architecture") -> Task:
    return Task(
        id="t",
        bucket="architecture",
        repo_url="u",
        repo_pin="p",
        query="q",
        expected_key_facts=["a", "b", "c"],
        expected_route=expected_route,
    )


def _result(**overrides: object) -> RunResult:
    base: dict[str, object] = {
        "task_id": "t",
        "arch": "wayfinder_supervisor",
        "answer": "...",
        "route_taken": "architecture",
    }
    base.update(overrides)
    return RunResult(**base)  # type: ignore[arg-type]


def _claim(label: ClaimLabel) -> Claim:
    return Claim(text="x does y", label=label, risk_level="high")


def test_all_three_satisfy_the_metric_protocol() -> None:
    assert isinstance(RoutingAccuracy(), Metric)
    assert isinstance(CitationGrounding(lambda _s: True), Metric)
    assert isinstance(VerificationRate(), Metric)


def test_routing_accuracy_match_and_mismatch() -> None:
    metric = RoutingAccuracy()
    assert metric.score(_task("architecture"), _result(route_taken="architecture")).value == 1.0
    miss = metric.score(_task("architecture"), _result(route_taken="debug"))
    assert miss.value == 0.0
    assert miss.detail == {"expected": "architecture", "actual": "debug"}


def test_verification_rate_counts_definitive_verdicts() -> None:
    result = _result(
        claims=[
            _claim("verified"),
            _claim("contradicted"),
            _claim("unverified"),
            _claim("unverified"),
        ]
    )
    score = VerificationRate().score(_task(), result)
    assert score.value == 0.5  # 2 of 4 are definitive
    assert score.detail == {"total": 4, "verified": 1, "contradicted": 1, "unverified": 2}


def test_verification_rate_empty_is_zero() -> None:
    score = VerificationRate().score(_task(), _result(claims=[]))
    assert score.value == 0.0
    assert score.detail["total"] == 0


def test_citation_grounding_fraction_and_ungrounded_list() -> None:
    real = {"pkg.mod.real_fn", "pkg.mod.also_real"}
    metric = CitationGrounding(lambda s: s in real)
    result = _result(cited_symbols=["pkg.mod.real_fn", "pkg.mod.hallucinated", "pkg.mod.also_real"])
    score = metric.score(_task(), result)
    assert score.value == 2 / 3
    assert score.detail["ungrounded"] == ["pkg.mod.hallucinated"]


def test_citation_grounding_dedupes_symbols() -> None:
    metric = CitationGrounding(lambda _s: True)
    result = _result(cited_symbols=["a", "a", "b"])
    score = metric.score(_task(), result)
    assert score.detail["total"] == 2  # de-duplicated
    assert score.value == 1.0


def test_citation_grounding_empty_scores_one_but_flags_total_zero() -> None:
    score = CitationGrounding(lambda _s: True).score(_task(), _result(cited_symbols=[]))
    assert score.value == 1.0
    assert score.detail["total"] == 0
