# agent-eval-harness

Open-source evaluation harness for LLM agents — claim verification, LLM-as-judge,
failure-mode taxonomy, and token/cost tracking — shipped with a **40-OSS-repo
Supervisor-vs-ReAct benchmark** for codebase-understanding agents.

> Status: building — core API (datasets / runner / metrics / judge / CLI) in place,
> green under `ruff` + `mypy --strict` + `pytest`. See `progress.md` for the roadmap.

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

## Usage (framework core)

```python
from pathlib import Path
from agent_eval_harness import (
    load_tasks, evaluate, write_csv,
    RoutingAccuracy, VerificationRate,
)

tasks = load_tasks(Path("tasks.jsonl"))
rows = evaluate(tasks, my_runner, [RoutingAccuracy(), VerificationRate()])
write_csv(rows, Path("results.csv"))
```

CLI:

```bash
agent-eval run --dataset tasks.jsonl --arch wayfinder_supervisor --out results.csv
```

(Live architecture invocations are wired in a later commit; until then inject a
`runner_factory` into `run_eval`, or pass your own runner to `evaluate`.)

## Status / roadmap

See [`progress.md`](./progress.md).
