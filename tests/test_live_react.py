"""Tests for the ReAct baseline adapter's pure mapping (Commit: ReAct baseline).

The live agent run (LangGraph + OpenAI + MCP) needs the `react` extra and a live
stack, so it's validated separately; here we test the message→raw mapping with
duck-typed fake messages.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent_eval_harness.live.react import (
    _extract_answer_and_tokens,
    _map_react_result,
    _slug,
)


@dataclass
class _FakeMsg:
    type: str
    content: str
    usage_metadata: dict[str, Any] | None = None


def test_slug_is_filesystem_safe() -> None:
    assert _slug("https://github.com/pallets/click.git") == "github_com_pallets_click"


def test_extract_takes_last_ai_message_and_sums_tokens() -> None:
    messages = [
        _FakeMsg("human", "q"),
        _FakeMsg("ai", "thinking", {"total_tokens": 10}),
        _FakeMsg("tool", "tool output", None),
        _FakeMsg("ai", "final answer", {"total_tokens": 25}),
    ]
    answer, tokens = _extract_answer_and_tokens(messages)
    assert answer == "final answer"
    assert tokens == 35


def test_extract_handles_missing_usage() -> None:
    answer, tokens = _extract_answer_and_tokens([_FakeMsg("ai", "hi")])
    assert answer == "hi"
    assert tokens == 0


def test_map_react_result_has_no_claims_and_react_route() -> None:
    raw = _map_react_result("an answer", 2000, cost_per_1k=0.01)
    assert raw["route"] == "react"
    assert raw["claims"] == []
    assert raw["cited_symbols"] == []
    assert raw["tokens"] == 2000
    assert raw["cost_usd"] == 0.02
