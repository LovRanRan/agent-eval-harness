# agent-eval-harness

Open-source evaluation harness for LLM agents — claim verification, LLM-as-judge,
failure-mode taxonomy, and token/cost tracking — shipped with a **40-OSS-repo
Supervisor-vs-ReAct benchmark** for codebase-understanding agents.

> Status: pre-build (scaffold). See `progress.md` for the plan and roadmap.

## Why

Most agent projects have no rigorous eval data. `agent-eval-harness` provides a
reusable framework to score agents on four metrics — routing accuracy, factual
correctness, citation grounding, and **verification rate** — and a flagship
40-repo benchmark that evaluates the [`wayfinder`](https://github.com/LovRanRan/wayfinder)
multi-agent codebase-onboarding system against a ReAct baseline.

## Planned scope

- Datasets / runners / metrics / judges API
- 40 OSS repos (web frameworks · ML libs · CLI tools · distributed systems), each
  with a runnable test suite
- LLM-as-judge (Claude + GPT) + ground-truth comparison + self-consistency
- Failure-mode taxonomy (hallucination / tool misuse / retrieval / reasoning)
- CLI runner + `EVAL_REPORT.md` + SVG charts

## Status / roadmap

See [`progress.md`](./progress.md).
