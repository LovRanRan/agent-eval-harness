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

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from agent_eval_harness.datasets import Task
from agent_eval_harness.judge import Judge
from agent_eval_harness.runner import RunResult

# Resolves whether a cited code symbol / file path actually exists in the task's
# repo. Task-aware so it can locate the right repo clone; in tests a fake is injected.
SymbolResolver = Callable[[Task, str], bool]


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


class RoutingAccuracy:
    """1.0 if the run's `route_taken` matches the task's `expected_route`, else 0.0."""

    name = "routing_accuracy"

    def score(self, task: Task, result: RunResult) -> MetricScore:
        correct = result.route_taken == task.expected_route
        return MetricScore(
            self.name,
            1.0 if correct else 0.0,
            {"expected": task.expected_route, "actual": result.route_taken},
        )


class CitationGrounding:
    """Fraction of cited symbols that actually exist in the repo (anti-hallucination).

    Symbols are de-duplicated before scoring. An answer that cites nothing scores
    1.0 (nothing ungrounded) but the detail records `total == 0` so a non-citing
    agent is still visible in the report.
    """

    name = "citation_grounding"

    def __init__(self, resolver: SymbolResolver) -> None:
        self._resolver = resolver

    def score(self, task: Task, result: RunResult) -> MetricScore:
        unique = dict.fromkeys(result.cited_symbols)  # preserves order, dedupes
        resolved = {symbol: self._resolver(task, symbol) for symbol in unique}
        total = len(resolved)
        grounded = [s for s, ok in resolved.items() if ok]
        ungrounded = [s for s, ok in resolved.items() if not ok]
        value = 1.0 if total == 0 else len(grounded) / total
        return MetricScore(
            self.name,
            value,
            {"total": total, "grounded": len(grounded), "ungrounded": ungrounded},
        )


class VerificationRate:
    """Share of claims with a definitive verdict (verified or contradicted).

    This is the metric that quantifies the verifier's value: a high rate means
    the agent's claims are being grounded against real test execution rather than
    left as unchecked assertions. Empty claim list scores 0.0.
    """

    name = "verification_rate"

    def score(self, task: Task, result: RunResult) -> MetricScore:
        claims = result.claims
        total = len(claims)
        verified = sum(1 for c in claims if c.label == "verified")
        contradicted = sum(1 for c in claims if c.label == "contradicted")
        unverified = sum(1 for c in claims if c.label == "unverified")
        value = 0.0 if total == 0 else (verified + contradicted) / total
        return MetricScore(
            self.name,
            value,
            {
                "total": total,
                "verified": verified,
                "contradicted": contradicted,
                "unverified": unverified,
            },
        )


class JudgeMetric:
    """Adapts a `Judge` into the `Metric` contract (the `factual_correctness` metric).

    Wrap a `SelfConsistentJudge` to fold self-consistency into the score; the
    verdict's reasoning, flagged hallucinations, and raw aggregation are carried
    through into `MetricScore.detail` for the report.
    """

    def __init__(self, judge: Judge, name: str = "factual_correctness") -> None:
        self.name = name
        self._judge = judge

    def score(self, task: Task, result: RunResult) -> MetricScore:
        verdict = self._judge.judge(task, result)
        return MetricScore(
            self.name,
            verdict.score,
            {
                "reasoning": verdict.reasoning,
                "flagged_hallucinations": verdict.flagged_hallucinations,
                "judge_raw": verdict.raw,
            },
        )
