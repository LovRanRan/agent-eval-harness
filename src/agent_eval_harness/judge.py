"""Judge layer — the LLM-as-judge behind non-deterministic metrics.

Used by `factual_correctness`: an LLM compares a `RunResult.answer` against the
task's ground truth and returns a structured verdict. Judge bias is controlled
explicitly — the verdict carries `reasoning` and any `flagged_hallucinations` so
scores are auditable rather than opaque, and self-consistency (3 runs, variance
< 0.1) is applied on top (Commit 4).

Commit 1 defines the contract only; the Claude-backed judge lands in Commit 4.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from agent_eval_harness.datasets import Task
from agent_eval_harness.runner import RunResult


@dataclass(frozen=True, slots=True)
class JudgeVerdict:
    """Structured output of one LLM-as-judge evaluation."""

    score: float  # normalized to [0, 1]
    reasoning: str  # why the judge scored it this way (auditability)
    flagged_hallucinations: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)  # raw model response, for debugging


@runtime_checkable
class Judge(Protocol):
    """Scores an answer against ground truth, returning a structured verdict."""

    def judge(self, task: Task, result: RunResult) -> JudgeVerdict: ...
