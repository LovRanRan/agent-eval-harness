"""Tests for the live Wayfinder adapter (Commit 8 wiring).

The HTTP loop is exercised with httpx.MockTransport — no network, no real Wayfinder.
"""

from __future__ import annotations

import httpx

from agent_eval_harness.live.wayfinder import map_run_summary, wayfinder_invoke


def test_map_run_summary_builds_claims_from_counts() -> None:
    raw = map_run_summary(
        {
            "final_output": "Flask is a WSGI framework.",
            "verified_count": 2,
            "unverified_count": 1,
            "contradicted_count": 1,
            "trace_metadata": {"intent": "architecture", "tokens": 1200, "cost_usd": 0.03},
        }
    )
    assert raw["answer"] == "Flask is a WSGI framework."
    assert raw["route"] == "architecture"
    assert raw["tokens"] == 1200
    assert raw["cost_usd"] == 0.03
    labels = [c["label"] for c in raw["claims"]]
    assert labels.count("verified") == 2
    assert labels.count("unverified") == 1
    assert labels.count("contradicted") == 1


def test_map_run_summary_tolerates_missing_fields() -> None:
    raw = map_run_summary({})
    assert raw["answer"] == ""
    assert raw["route"] == ""
    assert raw["claims"] == []
    assert raw["tokens"] == 0
    assert raw["cost_usd"] == 0.0


def _transport(status_sequence: list[str]) -> httpx.MockTransport:
    """MockTransport: /explain returns a job, /status walks the given status sequence."""
    state = {"i": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/explain":
            return httpx.Response(202, json={"job_id": "job-1", "status": "queued"})
        if request.url.path == "/status/job-1":
            status = status_sequence[min(state["i"], len(status_sequence) - 1)]
            state["i"] += 1
            body = {"job_id": "job-1", "status": status}
            if status == "completed":
                body |= {"final_output": "done", "verified_count": 1}
            if status == "failed":
                body |= {"error": "boom"}
            return httpx.Response(200, json=body)
        return httpx.Response(404)

    return httpx.MockTransport(handler)


def test_invoke_polls_until_completed() -> None:
    invoke = wayfinder_invoke(
        "http://test", poll_interval_s=0.0, transport=_transport(["running", "completed"])
    )
    raw = invoke("https://github.com/pallets/flask", "what does it do?")
    assert raw["answer"] == "done"
    assert len(raw["claims"]) == 1


def test_invoke_raises_on_failed_run() -> None:
    invoke = wayfinder_invoke("http://test", poll_interval_s=0.0, transport=_transport(["failed"]))
    try:
        invoke("https://github.com/pallets/flask", "q")
    except RuntimeError as exc:
        assert "boom" in str(exc)
    else:
        raise AssertionError("expected RuntimeError on failed run")
