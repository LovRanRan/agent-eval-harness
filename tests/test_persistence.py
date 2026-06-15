"""Tests for run-result persistence + offline re-scoring (no agent re-runs)."""

from __future__ import annotations

import json
from pathlib import Path

from agent_eval_harness import (
    Claim,
    RoutingAccuracy,
    RunResult,
    Task,
    VerificationRate,
    read_run_results,
    rescore_from_runs,
    run_benchmark,
    runresult_from_dict,
    runresult_to_dict,
    write_run_results,
)


def _task(task_id: str = "t1") -> Task:
    return Task(
        id=task_id,
        bucket="architecture",
        repo_url="https://github.com/acme/x",
        repo_pin="p",
        query="q",
        expected_key_facts=["a", "b", "c"],
        expected_route="architecture",
    )


def test_runresult_roundtrip_preserves_fields_and_claims() -> None:
    result = RunResult(
        task_id="t1",
        arch="wayfinder_supervisor",
        answer="ans",
        route_taken="architecture",
        claims=[Claim(text="c", label="verified", risk_level="high", test_id="tests/test_x.py::t")],
        cited_symbols=["core.py", "Command.invoke"],
        tokens=123,
        cost_usd=0.5,
        latency_s=1.25,
        error=None,
    )
    restored = runresult_from_dict(runresult_to_dict(result))
    assert restored.task_id == "t1"
    assert restored.arch == "wayfinder_supervisor"
    assert restored.answer == "ans"
    assert restored.route_taken == "architecture"
    assert restored.cited_symbols == ["core.py", "Command.invoke"]
    assert restored.tokens == 123
    assert len(restored.claims) == 1
    assert restored.claims[0].label == "verified"
    assert restored.claims[0].test_id == "tests/test_x.py::t"


def test_runresult_from_dict_sanitizes_bad_enums() -> None:
    restored = runresult_from_dict(
        {
            "task_id": "t1",
            "arch": "a",
            "claims": [{"text": "c", "label": "bogus", "risk_level": "nope"}],
        }
    )
    assert restored.claims[0].label == "unverified"
    assert restored.claims[0].risk_level == "low"


def test_write_then_read_run_results(tmp_path: Path) -> None:
    results = [
        RunResult(task_id="t1", arch="a", answer="x", route_taken="architecture"),
        RunResult(task_id="t2", arch="a", answer="", route_taken="", error="boom"),
    ]
    path = tmp_path / "a.runs.jsonl"
    write_run_results(results, path)
    back = read_run_results(path)
    assert [r.task_id for r in back] == ["t1", "t2"]
    assert back[1].error == "boom"


class _FakeRunner:
    def __init__(self, arch: str, route: str) -> None:
        self.arch = arch
        self._route = route

    def run(self, task: Task) -> RunResult:
        return RunResult(task_id=task.id, arch=self.arch, answer="a", route_taken=self._route)


def test_rescore_from_runs_reproduces_without_runner(tmp_path: Path) -> None:
    tasks = [_task("t1"), _task("t2")]
    runners = {"supervisor": _FakeRunner("supervisor", "architecture")}
    metrics = [RoutingAccuracy(), VerificationRate()]
    run_benchmark(tasks, runners, metrics, tmp_path)

    # the sidecar was persisted
    assert (tmp_path / "supervisor.runs.jsonl").exists()

    # corrupt the CSV/summary, then rebuild purely from persisted runs (no runner)
    (tmp_path / "supervisor.csv").write_text("garbage", encoding="utf-8")
    summary = rescore_from_runs(tmp_path, tasks, [RoutingAccuracy()])
    assert summary["supervisor"]["metrics"]["routing_accuracy"] == 1.0
    assert summary["supervisor"]["tasks"] == 2


def test_persisted_jsonl_is_one_object_per_line(tmp_path: Path) -> None:
    write_run_results(
        [RunResult(task_id="t1", arch="a", answer="x", route_taken="r")],
        tmp_path / "a.runs.jsonl",
    )
    lines = (tmp_path / "a.runs.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["task_id"] == "t1"
