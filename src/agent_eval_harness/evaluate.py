"""Evaluation orchestration — run an architecture over a dataset and score it.

`evaluate` is the core loop: for each task, run the architecture, then score the
`RunResult` with each metric (skipping scoring when the run errored). `write_csv`
flattens the rows to CSV for the report. Both are pure/IO-light and unit-testable
with a fake runner.
"""

from __future__ import annotations

import csv
import os
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from agent_eval_harness.datasets import Bucket, Task
from agent_eval_harness.metric import Metric
from agent_eval_harness.runner import Runner


def _progress_enabled() -> bool:
    """Per-task progress goes to stderr only when AGENT_EVAL_PROGRESS is truthy.

    Off by default so unit tests stay silent; the CLI/benchmark turn it on.
    """
    return os.environ.get("AGENT_EVAL_PROGRESS", "").strip().lower() in {"1", "true", "yes", "on"}


_BASE_FIELDS = ("task_id", "bucket", "arch")
_TAIL_FIELDS = ("tokens", "cost_usd", "latency_s", "error")


@dataclass(frozen=True, slots=True)
class EvalRow:
    """One task's evaluation outcome under one architecture."""

    task_id: str
    bucket: Bucket
    arch: str
    metrics: dict[str, float]  # metric name -> value (empty if the run errored)
    tokens: int
    cost_usd: float
    latency_s: float
    error: str | None


def evaluate(tasks: Sequence[Task], runner: Runner, metrics: Sequence[Metric]) -> list[EvalRow]:
    """Run `runner` over `tasks`, scoring each successful result with `metrics`."""
    rows: list[EvalRow] = []
    total = len(tasks)
    show_progress = _progress_enabled()
    started = time.monotonic()
    for index, task in enumerate(tasks, start=1):
        result = runner.run(task)
        scores = (
            {}
            if result.error is not None
            else {m.name: m.score(task, result).value for m in metrics}
        )
        if show_progress:
            status = "ERR" if result.error is not None else "ok"
            elapsed = time.monotonic() - started
            print(
                f"[{index}/{total}] {runner.arch} · {task.id} · {task.bucket} · "
                f"{status} · {result.tokens} tok · {result.latency_s:.1f}s "
                f"(elapsed {elapsed:.0f}s)",
                file=sys.stderr,
                flush=True,
            )
        rows.append(
            EvalRow(
                task_id=task.id,
                bucket=task.bucket,
                arch=runner.arch,
                metrics=scores,
                tokens=result.tokens,
                cost_usd=result.cost_usd,
                latency_s=result.latency_s,
                error=result.error,
            )
        )
    return rows


def write_csv(rows: Sequence[EvalRow], path: Path) -> None:
    """Write evaluation rows to CSV, one metric per column (union across rows)."""
    metric_names = sorted({name for row in rows for name in row.metrics})
    fieldnames = [*_BASE_FIELDS, *metric_names, *_TAIL_FIELDS]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            record: dict[str, object] = {
                "task_id": row.task_id,
                "bucket": row.bucket,
                "arch": row.arch,
                "tokens": row.tokens,
                "cost_usd": row.cost_usd,
                "latency_s": round(row.latency_s, 4),
                "error": row.error or "",
            }
            for name in metric_names:
                value = row.metrics.get(name)
                record[name] = "" if value is None else value
            writer.writerow(record)
