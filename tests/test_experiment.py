"""Tests for the benchmark driver (orchestration only, fake runners/metrics)."""

from __future__ import annotations

import json
from pathlib import Path

from agent_eval_harness import (
    RoutingAccuracy,
    RunResult,
    Task,
    VerificationRate,
    run_benchmark,
    summarize,
)
from agent_eval_harness.evaluate import EvalRow


class _FakeRunner:
    def __init__(self, arch: str, route: str, tokens: int) -> None:
        self.arch = arch
        self._route = route
        self._tokens = tokens

    def run(self, task: Task) -> RunResult:
        return RunResult(
            task_id=task.id,
            arch=self.arch,
            answer="a",
            route_taken=self._route,
            tokens=self._tokens,
        )


def _tasks() -> list[Task]:
    return [
        Task(
            id=f"t{i}",
            bucket="architecture",
            repo_url="https://github.com/acme/x",
            repo_pin="p",
            query="q",
            expected_key_facts=["a", "b", "c"],
            expected_route="architecture",
        )
        for i in range(2)
    ]


def test_run_benchmark_writes_csvs_and_summary(tmp_path: Path) -> None:
    runners = {
        "supervisor": _FakeRunner("supervisor", "architecture", 1000),
        "react": _FakeRunner("react", "debug", 500),
    }
    metrics = [RoutingAccuracy(), VerificationRate()]
    rows_by_arch = run_benchmark(_tasks(), runners, metrics, tmp_path)

    assert (tmp_path / "supervisor.csv").exists()
    assert (tmp_path / "react.csv").exists()
    summary = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    # supervisor routed correctly on both tasks; react never did
    assert summary["supervisor"]["metrics"]["routing_accuracy"] == 1.0
    assert summary["react"]["metrics"]["routing_accuracy"] == 0.0
    assert summary["supervisor"]["total_tokens"] == 2000
    assert len(rows_by_arch["supervisor"]) == 2


def test_summarize_means_costs_and_errors() -> None:
    rows = {
        "a": [
            EvalRow("t1", "architecture", "a", {"routing_accuracy": 1.0}, 100, 0.0, 1.0, None),
            EvalRow("t2", "architecture", "a", {"routing_accuracy": 0.0}, 200, 0.0, 1.0, None),
            EvalRow("t3", "architecture", "a", {}, 0, 0.0, 0.0, "boom"),
        ],
    }
    summary = summarize(rows, price_per_1k_usd=2.0)
    assert summary["a"]["metrics"]["routing_accuracy"] == 0.5  # over scored rows only
    assert summary["a"]["errors"] == 1
    assert summary["a"]["total_tokens"] == 300
    assert summary["a"]["cost_usd"] == 0.6  # 300/1000 * 2.0
