"""Contract tests for the Commit 1 eval API skeleton.

These assert the typed contracts instantiate and connect — no logic is exercised
yet (loaders, metrics, judges, runners arrive in later commits).
"""

from __future__ import annotations

import agent_eval_harness as aeh
from agent_eval_harness import (
    BUCKETS,
    Claim,
    JudgeVerdict,
    MetricScore,
    Runner,
    RunResult,
    Task,
)


def test_public_api_is_exported() -> None:
    for name in aeh.__all__:
        assert hasattr(aeh, name), f"missing export: {name}"


def test_buckets_are_the_four_locked_buckets() -> None:
    assert BUCKETS == (
        "architecture",
        "function_tracing",
        "claim_verification",
        "bug_localization",
    )


def test_task_constructs_with_required_and_optional_fields() -> None:
    task = Task(
        id="t1",
        bucket="claim_verification",
        repo_url="https://github.com/tiangolo/fastapi",
        repo_pin="0.110.0",
        query="Does Depends() cache results within a request?",
        expected_key_facts=["caches per-request", "use_cache flag", "solve_dependencies"],
        expected_route="claim_verification",
        verifier_test_id="tests/test_dependency_cache.py::test_caches",
        claim_under_test="Depends() re-evaluates on every use",
    )
    assert task.bucket == "claim_verification"
    assert len(task.expected_key_facts) == 3
    assert task.bug_fix_files == []  # optional default


def test_runresult_and_claim_normalize_an_architecture_run() -> None:
    result = RunResult(
        task_id="t1",
        arch="wayfinder_supervisor",
        answer="Depends() caches per request.",
        route_taken="claim_verification",
        claims=[
            Claim(
                text="Depends() caches per request",
                label="verified",
                risk_level="high",
                test_id="tests/test_dependency_cache.py::test_caches",
            )
        ],
        cited_symbols=["fastapi.dependencies.utils.solve_dependencies"],
        tokens=1234,
        cost_usd=0.012,
        latency_s=4.2,
    )
    assert result.error is None
    assert result.claims[0].label == "verified"


def test_metricscore_and_judgeverdict_construct() -> None:
    score = MetricScore(name="verification_rate", value=1.0, detail={"verified": 1, "total": 1})
    verdict = JudgeVerdict(score=0.9, reasoning="all key facts present", flagged_hallucinations=[])
    assert 0.0 <= score.value <= 1.0
    assert 0.0 <= verdict.score <= 1.0


def test_runner_protocol_is_structurally_satisfied() -> None:
    class DummyRunner:
        arch = "dummy"

        def run(self, task: Task) -> RunResult:  # noqa: ARG002
            return RunResult(task_id=task.id, arch=self.arch, answer="", route_taken="")

    assert isinstance(DummyRunner(), Runner)
