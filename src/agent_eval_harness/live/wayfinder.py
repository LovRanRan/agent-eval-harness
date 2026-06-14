"""Live invocation of a running Wayfinder deployment.

Contract (from wayfinder/src/wayfinder/api): `POST /explain {repo_url, query}`
returns a `RunSummary` with a `job_id`; poll `GET /status/{job_id}` until the
`status` is terminal (`completed` / `failed`), then map the `RunSummary` into the
standard raw mapping consumed by `runner._normalize`.

What maps cleanly today:
  - `final_output`                       -> answer
  - verified/unverified/contradicted_count -> claims (labels drive verification_rate)
  - `trace_metadata`                     -> route / tokens / cost (best-effort)

`cited_symbols` is left empty for now — the `/status` payload exposes claim
*counts*, not individual cited symbols, so citation_grounding isn't meaningful
from this endpoint yet (revisit once a real RunSummary is in hand).
"""

from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any

from agent_eval_harness.citations import extract_cited_symbols
from agent_eval_harness.runner import AgentInvoke

_TERMINAL = frozenset({"completed", "failed"})


def map_run_summary(summary: Mapping[str, Any]) -> dict[str, Any]:
    """Map a Wayfinder `RunSummary` payload into the standard raw run mapping."""
    verified = _as_int(summary.get("verified_count"))
    unverified = _as_int(summary.get("unverified_count"))
    contradicted = _as_int(summary.get("contradicted_count"))
    claims = (
        [_claim("verified") for _ in range(verified)]
        + [_claim("unverified") for _ in range(unverified)]
        + [_claim("contradicted") for _ in range(contradicted)]
    )
    meta = summary.get("trace_metadata")
    meta = meta if isinstance(meta, dict) else {}
    # Prefer the top-level classified intent (wayfinder now surfaces it); fall back
    # to trace_metadata for older runs.
    route = str(summary.get("intent") or meta.get("intent") or meta.get("route") or "")
    answer = summary.get("final_output") or ""
    return {
        "answer": answer,
        "route": route,
        "claims": claims,
        "cited_symbols": extract_cited_symbols(answer),
        "tokens": _as_int(meta.get("tokens")),
        "cost_usd": _as_float(meta.get("cost_usd")),
    }


def wayfinder_invoke(
    base_url: str,
    *,
    poll_interval_s: float = 2.0,
    timeout_s: float = 300.0,
    auth_token: str | None = None,
    transport: Any = None,
) -> AgentInvoke:
    """Build an `AgentInvoke` that drives a running Wayfinder over HTTP.

    Needs the `[live]` extra (`pip install 'agent-eval-harness[live]'`). A failed
    Wayfinder run raises (captured as `RunResult.error` by the runner); a timeout
    raises `TimeoutError`. `transport` is an optional httpx transport (e.g.
    `httpx.MockTransport`) for tests.
    """

    def invoke(repo_url: str, query: str) -> Mapping[str, Any]:
        try:
            import httpx
        except ImportError as exc:  # pragma: no cover - depends on optional extra
            raise RuntimeError(
                "wayfinder_invoke needs httpx: pip install 'agent-eval-harness[live]'"
            ) from exc
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        deadline = time.monotonic() + timeout_s
        with httpx.Client(
            base_url=base_url, timeout=30.0, headers=headers, transport=transport
        ) as client:
            started = client.post("/explain", json={"repo_url": repo_url, "query": query})
            started.raise_for_status()
            job_id = started.json()["job_id"]
            while True:
                resp = client.get(f"/status/{job_id}")
                resp.raise_for_status()
                summary = resp.json()
                status = summary.get("status")
                if status == "completed":
                    return map_run_summary(summary)
                if status == "failed":
                    raise RuntimeError(f"wayfinder run failed: {summary.get('error')}")
                if time.monotonic() > deadline:
                    raise TimeoutError(f"wayfinder run {job_id} did not finish in {timeout_s}s")
                time.sleep(poll_interval_s)

    return invoke


def _claim(label: str) -> dict[str, str]:
    return {"text": f"({label} claim)", "label": label, "risk_level": "high"}


def _as_int(value: Any) -> int:
    return int(value) if isinstance(value, (int, float)) else 0


def _as_float(value: Any) -> float:
    return float(value) if isinstance(value, (int, float)) else 0.0
