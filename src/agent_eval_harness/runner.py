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

import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, get_args, runtime_checkable

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


# An architecture's raw invocation: (repo_url, query) -> a provider-specific
# mapping. Adapters normalize this into a `RunResult`. The live wiring (HTTP to a
# deployed Wayfinder, or a LangGraph `create_react_agent`) is injected by the
# caller and lands in Commit 8; tests inject a fake.
AgentInvoke = Callable[[str, str], Mapping[str, Any]]

# Keys an `AgentInvoke` mapping may carry (all optional, safe defaults applied):
#   answer:str  route:str  claims:list[dict]  cited_symbols:list[str]
#   tokens:int  cost_usd:float
# A `claims` dict entry: {text:str, label:ClaimLabel, risk_level:RiskLevel, test_id:str|None}

_VALID_LABELS: frozenset[str] = frozenset(get_args(ClaimLabel))
_VALID_RISK: frozenset[str] = frozenset(get_args(RiskLevel))


def _parse_claims(raw_claims: Any) -> list[Claim]:
    if not isinstance(raw_claims, list):
        return []
    claims: list[Claim] = []
    for item in raw_claims:
        if not isinstance(item, dict):
            continue
        label_raw = item.get("label", "unverified")
        label: ClaimLabel = label_raw if label_raw in _VALID_LABELS else "unverified"
        risk_raw = item.get("risk_level", "low")
        risk: RiskLevel = risk_raw if risk_raw in _VALID_RISK else "low"
        test_id = item.get("test_id")
        claims.append(
            Claim(
                text=str(item.get("text", "")),
                label=label,
                risk_level=risk,
                test_id=test_id if isinstance(test_id, str) else None,
            )
        )
    return claims


def _normalize(task: Task, arch: str, raw: Mapping[str, Any], latency_s: float) -> RunResult:
    """Map a raw agent invocation mapping into a normalized `RunResult`."""
    cited = raw.get("cited_symbols", [])
    cited_symbols = [str(s) for s in cited] if isinstance(cited, list) else []
    tokens = raw.get("tokens", 0)
    cost = raw.get("cost_usd", 0.0)
    return RunResult(
        task_id=task.id,
        arch=arch,
        answer=str(raw.get("answer", "")),
        route_taken=str(raw.get("route", "")),
        claims=_parse_claims(raw.get("claims")),
        cited_symbols=cited_symbols,
        tokens=int(tokens) if isinstance(tokens, (int, float)) else 0,
        cost_usd=float(cost) if isinstance(cost, (int, float)) else 0.0,
        latency_s=latency_s,
        raw=dict(raw),
    )


def _execute(task: Task, arch: str, invoke: AgentInvoke) -> RunResult:
    """Run `invoke`, timing it and capturing any failure as `RunResult.error`."""
    start = time.perf_counter()
    try:
        raw = invoke(task.repo_url, task.query)
    except Exception as exc:  # eval must not crash on a single failing task
        return RunResult(
            task_id=task.id,
            arch=arch,
            answer="",
            route_taken="",
            error=f"{type(exc).__name__}: {exc}",
            latency_s=time.perf_counter() - start,
        )
    return _normalize(task, arch, raw, time.perf_counter() - start)


class WayfinderSupervisorRunner:
    """Adapter for the Wayfinder Supervisor architecture (the system under test).

    Its invocation surfaces explicit routing, structured claims (with verifier
    labels), and cited symbols, so all four metrics have signal to score.
    """

    arch = "wayfinder_supervisor"

    def __init__(self, invoke: AgentInvoke) -> None:
        self._invoke = invoke

    def run(self, task: Task) -> RunResult:
        return _execute(task, self.arch, self._invoke)


class ReActBaselineRunner:
    """Adapter for the ReAct single-agent baseline (`create_react_agent`, same MCP tools).

    No supervisor and no structured verifier step, so it typically yields no
    `claims` — which is exactly why its verification_rate is expected to be low
    relative to the Supervisor.
    """

    arch = "react_baseline"

    def __init__(self, invoke: AgentInvoke) -> None:
        self._invoke = invoke

    def run(self, task: Task) -> RunResult:
        return _execute(task, self.arch, self._invoke)
