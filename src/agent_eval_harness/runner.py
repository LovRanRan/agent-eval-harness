"""Runner layer — architecture adapters and their normalized output.

A `Runner` executes one architecture (Wayfinder Supervisor, ReAct baseline, ...)
against one `Task` and returns a `RunResult`. The whole point of `RunResult` is
normalization: the judge and metrics must NOT be able to tell which architecture
produced an answer, so every adapter maps its own trace into this one shape.

Errors are reported via `RunResult.error` (not raised), so a single failing task
never aborts a whole eval sweep.

Commit 1 defines the contract only; concrete adapters land in Commit 5.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable

from agent_eval_harness.datasets import Task

# Outcome of grounding a single claim against real test execution.
ClaimLabel = Literal["verified", "unverified", "contradicted"]

# How strongly a claim asserts something (function names / numbers / behaviour
# assertions = high). Only high/medium-risk claims are routed to the verifier.
RiskLevel = Literal["low", "medium", "high"]


@dataclass(frozen=True, slots=True)
class Claim:
    """A factual assertion an agent made about the repo, plus its verification."""

    text: str
    label: ClaimLabel
    risk_level: RiskLevel
    test_id: str | None = None  # the test used to verify/contradict, if any


@dataclass(frozen=True, slots=True)
class RunResult:
    """Normalized output of one architecture on one task.

    Adapter-specific details go in `raw`; everything the judge/metrics read must
    be one of the typed fields below so scoring is architecture-blind.
    """

    task_id: str
    arch: str  # architecture identifier, e.g. "wayfinder_supervisor" / "react_baseline"
    answer: str  # final natural-language answer
    route_taken: str  # the route/intent the run actually followed
    claims: list[Claim] = field(default_factory=list)
    cited_symbols: list[str] = field(default_factory=list)  # code symbols / file paths cited
    tokens: int = 0
    cost_usd: float = 0.0
    latency_s: float = 0.0
    error: str | None = None  # populated instead of raising on failure
    raw: dict[str, Any] = field(default_factory=dict)  # adapter trace, for debugging only


@runtime_checkable
class Runner(Protocol):
    """Executes one architecture against a task, returning a normalized result."""

    arch: str

    def run(self, task: Task) -> RunResult: ...
