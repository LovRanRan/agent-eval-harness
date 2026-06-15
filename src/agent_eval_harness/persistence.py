"""Persist and reload raw `RunResult`s so a sweep can be re-scored offline.

Agent runs (especially a token-hungry ReAct loop) are the expensive part of a
benchmark; metric scoring is cheap (and free for non-LLM metrics). Writing each
run's normalized `RunResult` to a JSONL sidecar means a later metric/resolver
change can be re-scored against the stored answers without paying to re-run the
agents again. The adapter-specific `raw` trace is intentionally dropped — metrics
only read the typed fields.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast, get_args

from agent_eval_harness.runner import Claim, ClaimLabel, RiskLevel, RunResult

_VALID_LABELS: frozenset[str] = frozenset(get_args(ClaimLabel))
_VALID_RISK: frozenset[str] = frozenset(get_args(RiskLevel))


def runresult_to_dict(result: RunResult) -> dict[str, Any]:
    """Serialize the scoreable fields of a `RunResult` (drops the debug `raw`)."""
    return {
        "task_id": result.task_id,
        "arch": result.arch,
        "answer": result.answer,
        "route_taken": result.route_taken,
        "claims": [
            {
                "text": claim.text,
                "label": claim.label,
                "risk_level": claim.risk_level,
                "test_id": claim.test_id,
            }
            for claim in result.claims
        ],
        "cited_symbols": list(result.cited_symbols),
        "tokens": result.tokens,
        "cost_usd": result.cost_usd,
        "latency_s": result.latency_s,
        "error": result.error,
    }


def runresult_from_dict(data: dict[str, Any]) -> RunResult:
    """Reconstruct a `RunResult` from its serialized form, re-validating enums."""
    claims: list[Claim] = []
    for item in data.get("claims", []):
        if not isinstance(item, dict):
            continue
        label = item.get("label", "unverified")
        risk = item.get("risk_level", "low")
        test_id = item.get("test_id")
        claims.append(
            Claim(
                text=str(item.get("text", "")),
                label=cast(ClaimLabel, label if label in _VALID_LABELS else "unverified"),
                risk_level=cast(RiskLevel, risk if risk in _VALID_RISK else "low"),
                test_id=test_id if isinstance(test_id, str) else None,
            )
        )
    cited = data.get("cited_symbols", [])
    error = data.get("error")
    return RunResult(
        task_id=str(data["task_id"]),
        arch=str(data["arch"]),
        answer=str(data.get("answer", "")),
        route_taken=str(data.get("route_taken", "")),
        claims=claims,
        cited_symbols=[str(s) for s in cited] if isinstance(cited, list) else [],
        tokens=int(data.get("tokens", 0)),
        cost_usd=float(data.get("cost_usd", 0.0)),
        latency_s=float(data.get("latency_s", 0.0)),
        error=str(error) if isinstance(error, str) else None,
    )


def write_run_results(results: Sequence[RunResult], path: Path) -> None:
    """Write run results as JSONL (one result per line)."""
    with path.open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(runresult_to_dict(result)) + "\n")


def read_run_results(path: Path) -> list[RunResult]:
    """Read run results back from a JSONL sidecar."""
    results: list[RunResult] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                results.append(runresult_from_dict(json.loads(line)))
    return results
