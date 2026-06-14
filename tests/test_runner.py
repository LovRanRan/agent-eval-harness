"""Tests for the runner + architecture adapters (Commit 5)."""

from __future__ import annotations

from typing import Any

from agent_eval_harness import (
    ReActBaselineRunner,
    Runner,
    Task,
    WayfinderSupervisorRunner,
)


def _task() -> Task:
    return Task(
        id="t1",
        bucket="claim_verification",
        repo_url="https://example.com/repo",
        repo_pin="abc",
        query="does X cache?",
        expected_key_facts=["a", "b", "c"],
        expected_route="claim_verification",
        claim_under_test="X caches",
    )


def _wayfinder_raw(_repo: str, _query: str) -> dict[str, Any]:
    return {
        "answer": "X caches per request.",
        "route": "claim_verification",
        "claims": [
            {"text": "X caches", "label": "verified", "risk_level": "high", "test_id": "t::a"},
            {"text": "junk", "label": "bogus", "risk_level": "nope"},  # coerced to defaults
            "not-a-dict",  # skipped
        ],
        "cited_symbols": ["pkg.mod.fn", "pkg.mod.fn"],
        "tokens": 1500,
        "cost_usd": 0.02,
    }


def test_both_runners_satisfy_protocol() -> None:
    assert isinstance(WayfinderSupervisorRunner(_wayfinder_raw), Runner)
    assert isinstance(ReActBaselineRunner(lambda _r, _q: {"answer": "hi"}), Runner)


def test_wayfinder_runner_normalizes_full_result() -> None:
    result = WayfinderSupervisorRunner(_wayfinder_raw).run(_task())
    assert result.arch == "wayfinder_supervisor"
    assert result.task_id == "t1"
    assert result.answer == "X caches per request."
    assert result.route_taken == "claim_verification"
    assert result.tokens == 1500
    assert result.cost_usd == 0.02
    assert result.error is None
    assert result.latency_s >= 0.0
    # claims: valid one parsed, bad labels coerced, non-dict skipped
    assert len(result.claims) == 2
    assert result.claims[0].label == "verified"
    assert result.claims[1].label == "unverified"  # coerced default
    assert result.claims[1].risk_level == "low"  # coerced default
    assert result.cited_symbols == ["pkg.mod.fn", "pkg.mod.fn"]


def test_react_runner_with_answer_only_has_no_claims() -> None:
    result = ReActBaselineRunner(lambda _r, _q: {"answer": "some answer"}).run(_task())
    assert result.arch == "react_baseline"
    assert result.answer == "some answer"
    assert result.claims == []
    assert result.cited_symbols == []


def test_runner_captures_failure_as_error_not_exception() -> None:
    def boom(_repo: str, _query: str) -> dict[str, Any]:
        raise RuntimeError("agent exploded")

    result = WayfinderSupervisorRunner(boom).run(_task())
    assert result.error is not None
    assert "agent exploded" in result.error
    assert result.answer == ""
    assert result.latency_s >= 0.0


def test_malformed_numeric_fields_default_safely() -> None:
    result = ReActBaselineRunner(
        lambda _r, _q: {"answer": "a", "tokens": "lots", "cost_usd": None}
    ).run(_task())
    assert result.tokens == 0
    assert result.cost_usd == 0.0
