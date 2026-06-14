"""Metric layer — scoring a `(Task, RunResult)` pair.

Four metrics are planned (theme_design_v1.md §6.3):
  - routing_accuracy    — deterministic: route_taken vs Task.expected_route
  - citation_grounding  — deterministic: cited_symbols exist in the repo AST
  - verification_rate   — deterministic: share of claims labeled verified/contradicted
  - factual_correctness — LLM-judged (see judge.py)

`Metric` is the common contract for all four. Deterministic metrics implement it
directly; the LLM-judged one delegates to a `Judge` and is wrapped for
self-consistency. Concrete metrics land in Commit 3 (deterministic) / Commit 4
(judged).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from agent_eval_harness.datasets import Task
from agent_eval_harness.runner import RunResult


@dataclass(frozen=True, slots=True)
class MetricScore:
    """A single metric's score for one task, plus computation detail."""

    name: str
    value: float  # normalized to [0, 1]
    detail: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Metric(Protocol):
    """Maps a (task, result) pair to a normalized [0, 1] score."""

    name: str

    def score(self, task: Task, result: RunResult) -> MetricScore: ...
