"""ReAct single-agent baseline (the comparison arm vs the Wayfinder Supervisor).

A single LangGraph `create_react_agent` on gpt-5.5, given the *same* project5 MCP
tools (repo-mapper / ast-explorer / test-runner) over streamable-http — but with
no supervisor and no structured verifier. It answers the query by free-form tool
use; we map its final message into the standard raw run mapping.

By design it emits no structured `claims`, so its verification_rate is expected to
be ~0 relative to the Supervisor — that contrast is the point of the benchmark.

Needs the `react` extra: `pip install 'agent-eval-harness[react]'`, plus
`OPENAI_API_KEY` in the environment and the project5 MCP servers reachable.
"""

from __future__ import annotations

import asyncio
import re
import subprocess
from pathlib import Path
from typing import Any

from agent_eval_harness.citations import extract_cited_symbols
from agent_eval_harness.runner import AgentInvoke

_PROMPT = """You are exploring an unfamiliar code repository to answer a question.

The repository is checked out locally at: {path}
Question: {query}

Use the available tools (repository structure, AST/symbol lookup, and test
execution) to ground your answer in the actual code. When the question is about
runtime behaviour, run the relevant test(s) before asserting it. Then give a
concise, specific answer."""


def _slug(repo_url: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", repo_url.removeprefix("https://").removesuffix(".git"))


def _clone_repo(repo_url: str, clone_root: Path) -> Path:
    """Shallow-clone the repo into `clone_root` (idempotent); return its path."""
    clone_root.mkdir(parents=True, exist_ok=True)
    path = clone_root / _slug(repo_url)
    if not path.exists():
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(path)],
            check=True,
            capture_output=True,
            timeout=180,
        )
    return path


def _extract_answer_and_tokens(messages: list[Any]) -> tuple[str, int]:
    """Pull the final AI answer text and summed token usage from agent messages."""
    answer = ""
    tokens = 0
    for message in messages:
        usage = getattr(message, "usage_metadata", None)
        if isinstance(usage, dict):
            tokens += int(usage.get("total_tokens", 0) or 0)
        content = getattr(message, "content", None)
        if getattr(message, "type", None) == "ai" and isinstance(content, str) and content.strip():
            answer = content
    return answer, tokens


def _map_react_result(answer: str, tokens: int, *, cost_per_1k: float = 0.0) -> dict[str, Any]:
    """Map a ReAct run into the standard raw run mapping (no structured claims)."""
    return {
        "answer": answer,
        "route": "react",
        "claims": [],
        "cited_symbols": extract_cited_symbols(answer),
        "tokens": tokens,
        "cost_usd": round(tokens / 1000.0 * cost_per_1k, 6),
    }


def react_invoke(
    mcp_urls: dict[str, str],
    *,
    model: str = "gpt-5.5",
    clone_root: str = "/tmp/agent-eval-harness/repos",
    cost_per_1k: float = 0.0,
    recursion_limit: int = 25,
    request_timeout_s: float = 120.0,
) -> AgentInvoke:
    """Build an `AgentInvoke` for the ReAct baseline.

    `mcp_urls` maps a server name to its streamable-http `/mcp` URL, e.g.
    `{"repo_mapper": "http://127.0.0.1:8101/mcp", ...}`.
    """

    async def _run(path: Path, query: str) -> dict[str, Any]:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        from langchain_openai import ChatOpenAI
        from langgraph.prebuilt import create_react_agent

        client = MultiServerMCPClient(
            {name: {"transport": "streamable_http", "url": url} for name, url in mcp_urls.items()}
        )
        tools = await client.get_tools()
        agent = create_react_agent(ChatOpenAI(model=model, timeout=request_timeout_s), tools)
        result = await agent.ainvoke(
            {"messages": [("user", _PROMPT.format(path=path, query=query))]},
            config={"recursion_limit": recursion_limit},
        )
        answer, tokens = _extract_answer_and_tokens(result["messages"])
        return _map_react_result(answer, tokens, cost_per_1k=cost_per_1k)

    def invoke(repo_url: str, query: str) -> dict[str, Any]:
        try:
            import langchain_mcp_adapters  # noqa: F401
            import langchain_openai  # noqa: F401
            import langgraph  # noqa: F401
        except ImportError as exc:  # pragma: no cover - depends on optional extra
            raise RuntimeError(
                "react_invoke needs the 'react' extra: pip install 'agent-eval-harness[react]'"
            ) from exc
        path = _clone_repo(repo_url, Path(clone_root))
        return asyncio.run(_run(path, query))

    return invoke
