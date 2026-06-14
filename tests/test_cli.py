"""Tests for the CLI runner (Commit 6)."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from agent_eval_harness import RunResult, Task
from agent_eval_harness.cli import build_runner, default_metrics, run_eval

FIXTURE = Path(__file__).parent / "fixtures" / "mini_tasks.jsonl"


class FakeRunner:
    arch = "wayfinder_supervisor"

    def run(self, task: Task) -> RunResult:
        # echo the expected route so routing_accuracy scores 1.0
        return RunResult(
            task_id=task.id, arch=self.arch, answer="a", route_taken=task.expected_route
        )


def test_default_metrics_are_offline_safe() -> None:
    names = {m.name for m in default_metrics()}
    assert names == {"routing_accuracy", "verification_rate"}


def test_run_eval_writes_csv_with_injected_runner(tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    count = run_eval(
        FIXTURE,
        "wayfinder_supervisor",
        out,
        runner_factory=lambda _arch: FakeRunner(),
    )
    assert count == 4  # mini fixture has 4 tasks
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert len(rows) == 4
    assert all(r["routing_accuracy"] == "1.0" for r in rows)


def test_build_runner_wayfinder_needs_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WAYFINDER_URL", raising=False)
    with pytest.raises(RuntimeError, match="WAYFINDER_URL"):
        build_runner("wayfinder_supervisor")


def test_build_runner_wayfinder_wired_when_url_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WAYFINDER_URL", "http://localhost:8000")
    runner = build_runner("wayfinder_supervisor")
    assert runner.arch == "wayfinder_supervisor"


def test_build_runner_wires_react_baseline() -> None:
    runner = build_runner("react_baseline")
    assert runner.arch == "react_baseline"


def test_build_runner_rejects_unknown_arch() -> None:
    with pytest.raises(ValueError, match="unknown arch"):
        build_runner("nope")


def test_benchmark_subcommand_parses() -> None:
    from agent_eval_harness.cli import _build_parser

    args = _build_parser().parse_args(
        ["benchmark", "--dataset", "d.jsonl", "--out", "o", "--runs", "5", "--price-per-1k", "3.0"]
    )
    assert args.command == "benchmark"
    assert args.runs == 5
    assert args.price_per_1k == 3.0
