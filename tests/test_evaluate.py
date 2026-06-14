"""Tests for the evaluation orchestration + CSV writer (Commit 6)."""

from __future__ import annotations

import csv
from pathlib import Path

from agent_eval_harness import (
    EvalRow,
    RoutingAccuracy,
    RunResult,
    Task,
    VerificationRate,
    evaluate,
    write_csv,
)


class FakeRunner:
    arch = "wayfinder_supervisor"

    def __init__(self, result: RunResult) -> None:
        self._result = result

    def run(self, task: Task) -> RunResult:  # noqa: ARG002
        return self._result


def _task(route: str = "architecture") -> Task:
    return Task(
        id="t1",
        bucket="architecture",
        repo_url="u",
        repo_pin="p",
        query="q",
        expected_key_facts=["a", "b", "c"],
        expected_route=route,
    )


def test_evaluate_scores_successful_run() -> None:
    result = RunResult(
        task_id="t1", arch="wayfinder_supervisor", answer="a", route_taken="architecture"
    )
    rows = evaluate([_task()], FakeRunner(result), [RoutingAccuracy(), VerificationRate()])
    assert len(rows) == 1
    assert rows[0].metrics["routing_accuracy"] == 1.0
    assert rows[0].metrics["verification_rate"] == 0.0
    assert rows[0].error is None


def test_evaluate_skips_scoring_on_error() -> None:
    result = RunResult(task_id="t1", arch="x", answer="", route_taken="", error="boom")
    rows = evaluate([_task()], FakeRunner(result), [RoutingAccuracy()])
    assert rows[0].metrics == {}
    assert rows[0].error == "boom"


def test_write_csv_roundtrip(tmp_path: Path) -> None:
    rows = [
        EvalRow(
            "t1",
            "architecture",
            "wayfinder_supervisor",
            {"routing_accuracy": 1.0},
            100,
            0.01,
            1.5,
            None,
        ),
        EvalRow("t2", "function_tracing", "wayfinder_supervisor", {}, 0, 0.0, 0.2, "timeout"),
    ]
    out = tmp_path / "results.csv"
    write_csv(rows, out)
    parsed = list(csv.DictReader(out.open(encoding="utf-8")))
    assert parsed[0]["task_id"] == "t1"
    assert parsed[0]["routing_accuracy"] == "1.0"
    assert parsed[1]["error"] == "timeout"
    assert parsed[1]["routing_accuracy"] == ""  # missing metric -> blank
