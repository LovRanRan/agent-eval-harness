"""Judge layer — the LLM-as-judge behind the `factual_correctness` metric.

An LLM compares a `RunResult.answer` against the task's ground-truth key facts and
returns a structured `JudgeVerdict` (score + reasoning + flagged hallucinations).
Judge bias is controlled explicitly: every verdict carries its reasoning so scores
are auditable, and `SelfConsistentJudge` runs the judge N times and only treats a
score as trustworthy when its variance is below a threshold (CoT self-consistency).

The judge talks to any `ChatModel`; `AnthropicChatModel` is the production
implementation (lazy-imports the `anthropic` SDK), and tests inject a fake.
"""

from __future__ import annotations

import json
import statistics
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


@runtime_checkable
class ChatModel(Protocol):
    """Minimal text-in/text-out LLM interface the judge depends on."""

    def complete(self, prompt: str) -> str: ...


_PROMPT_TEMPLATE = """You are grading whether an AI agent's answer about a code \
repository is factually correct, using the provided ground-truth key facts.

Repository: {repo_url}
Question: {query}

Ground-truth key facts the answer should reflect:
{facts}

Agent's answer:
{answer}

Score how factually correct and complete the answer is against the key facts.
Respond with ONLY a JSON object, no prose, in exactly this shape:
{{"score": <float 0.0-1.0>, "reasoning": "<one or two sentences>", \
"hallucinations": ["<claim in the answer contradicted by or absent from the facts>"]}}"""


class FactualCorrectnessJudge:
    """Grades factual correctness of an answer against `Task.expected_key_facts`."""

    def __init__(self, model: ChatModel) -> None:
        self._model = model

    def judge(self, task: Task, result: RunResult) -> JudgeVerdict:
        prompt = _PROMPT_TEMPLATE.format(
            repo_url=task.repo_url,
            query=task.query,
            facts="\n".join(f"- {fact}" for fact in task.expected_key_facts),
            answer=result.answer,
        )
        raw_text = self._model.complete(prompt)
        return _parse_verdict(raw_text)


class SelfConsistentJudge:
    """Wraps a judge, runs it `runs` times, and aggregates by mean score.

    The verdict is flagged untrustworthy (`raw["consistent"] == False`) when the
    score variance exceeds `variance_threshold` (default 0.1) — the report should
    drop or caveat such scores.
    """

    def __init__(self, inner: Judge, runs: int = 3, variance_threshold: float = 0.1) -> None:
        if runs < 1:
            raise ValueError("runs must be >= 1")
        self._inner = inner
        self._runs = runs
        self._threshold = variance_threshold

    def judge(self, task: Task, result: RunResult) -> JudgeVerdict:
        verdicts = [self._inner.judge(task, result) for _ in range(self._runs)]
        scores = [v.score for v in verdicts]
        mean = statistics.fmean(scores)
        variance = statistics.pvariance(scores) if len(scores) > 1 else 0.0
        consistent = variance < self._threshold
        hallucinations = sorted({h for v in verdicts for h in v.flagged_hallucinations})
        reasoning = (
            f"self-consistency over {self._runs} runs: "
            f"mean={mean:.3f}, variance={variance:.4f}, consistent={consistent}"
        )
        return JudgeVerdict(
            score=mean,
            reasoning=reasoning,
            flagged_hallucinations=hallucinations,
            raw={
                "scores": scores,
                "variance": variance,
                "consistent": consistent,
                "runs": self._runs,
                "threshold": self._threshold,
            },
        )


class AnthropicChatModel:
    """Production `ChatModel` backed by the Anthropic API (lazy SDK import).

    Install via the `llm` extra: `pip install 'agent-eval-harness[llm]'`.
    """

    def __init__(self, model: str = "claude-sonnet-4-6", *, max_tokens: int = 1024) -> None:
        self._model = model
        self._max_tokens = max_tokens

    def complete(self, prompt: str) -> str:
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover - depends on optional extra
            raise RuntimeError(
                "AnthropicChatModel needs the 'anthropic' package: "
                "pip install 'agent-eval-harness[llm]'"
            ) from exc
        client = anthropic.Anthropic()
        message = client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        # Only text blocks carry `.text`; getattr keeps mypy happy across the SDK's
        # block union (tool-use/thinking/etc. blocks have no text attribute).
        parts = [
            t for block in message.content if isinstance(t := getattr(block, "text", None), str)
        ]
        return "".join(parts)


def _parse_verdict(raw_text: str) -> JudgeVerdict:
    """Parse a model response into a `JudgeVerdict`, tolerating fences/prose.

    A response that can't be parsed yields a score-0.0 verdict flagged in `raw`,
    so a single bad judge call degrades gracefully instead of aborting a sweep.
    """
    snippet = _extract_json_object(raw_text)
    if snippet is None:
        return JudgeVerdict(0.0, "could not locate JSON in judge response", raw={"raw": raw_text})
    try:
        obj = json.loads(snippet)
    except json.JSONDecodeError as exc:
        return JudgeVerdict(0.0, f"unparseable judge JSON: {exc}", raw={"raw": raw_text})
    if not isinstance(obj, dict):
        return JudgeVerdict(0.0, "judge JSON was not an object", raw={"raw": raw_text})

    score = obj.get("score", 0.0)
    score = float(score) if isinstance(score, (int, float)) else 0.0
    score = max(0.0, min(1.0, score))  # clamp to [0, 1]
    reasoning = obj.get("reasoning", "")
    reasoning = reasoning if isinstance(reasoning, str) else ""
    raw_halluc = obj.get("hallucinations", [])
    hallucinations = [str(h) for h in raw_halluc] if isinstance(raw_halluc, list) else []
    return JudgeVerdict(score, reasoning, hallucinations, raw={"raw": raw_text})


def _extract_json_object(text: str) -> str | None:
    """Return the substring from the first `{` to the last `}`, or None."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    return text[start : end + 1]
