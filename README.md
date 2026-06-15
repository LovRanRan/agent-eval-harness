# agent-eval-harness

Open-source evaluation harness for LLM agents — routing accuracy, factual
correctness (LLM-as-judge with self-consistency), citation grounding, and
test-execution **verification rate** — shipped with a **Supervisor-vs-ReAct
benchmark** for codebase-understanding agents.

> **Status: v0.5.** Framework complete and green under `ruff` + `mypy --strict` +
> `pytest` (73 tests). Flagship benchmark runs over **40 tasks across 10 Python OSS
> repos** (4 task buckets), both architectures scored under the same metrics. The
> full 40-repos-across-4-domains dataset and an OSS v1.0 (mkdocs site, more
> examples) are the roadmap to v1.0 — see [Scope & roadmap](#scope--roadmap).

## Why

Most agent projects ship with no rigorous eval data. `agent-eval-harness` is a
reusable framework to score agents on four metrics, plus a benchmark that pits the
[`wayfinder`](https://github.com/LovRanRan/wayfinder) multi-agent
codebase-onboarding system against a ReAct single-agent baseline using the *same*
model (gpt-5.5) and the *same* five MCP tools — so the comparison isolates
**orchestration**, not tools or model.

## Headline result (full_v1, 40 tasks, ground truth reviewed & approved)

On a 40-task benchmark over 10 OSS repos, the Wayfinder Supervisor used **~12×
fewer tokens (396k vs 4.8M) and completed every task, while the ReAct baseline
failed 6/40 (15%) by running its loop past the recursion limit.** ReAct produced
higher raw answer quality on the tasks it finished (factual 0.70 vs 0.48, citation
0.88 vs 0.78) — at ~12× the cost and with that reliability gap. The Supervisor is
also the only arm that routes by intent and verifies claims via real test
execution.

| metric | wayfinder_supervisor | react_baseline |
|---|---|---|
| factual_correctness | 0.482 | **0.702** |
| citation_grounding | 0.776 | **0.884** |
| verification_rate | **0.094** | 0.000 |
| routing_accuracy | **0.475** | 0.000 |
| total tokens | **396,223** | 4,812,463 |
| tasks (errors) | 40 (**0**) | 40 (**6**) |

Full write-ups: [`report/full_v1/EVAL_REPORT.md`](./report/full_v1/EVAL_REPORT.md)
(40 tasks) and [`report/small_v1/EVAL_REPORT.md`](./report/small_v1/EVAL_REPORT.md)
(12-task dev set), each with four SVG charts. `routing_accuracy` and
`verification_rate` are structurally one-sided (ReAct has no router/verifier), so
the apples-to-apples axes are factual, citation, and cost.

## Metrics

- **routing_accuracy** — classified intent vs the task's expected route.
- **factual_correctness** — LLM-as-judge (Claude) against ground-truth key facts,
  wrapped in self-consistency (N runs, variance-gated).
- **citation_grounding** — share of cited code symbols that actually exist in the
  repo (anti-hallucination). The resolver credits real attribute/method references
  (`self.callback`, `ctx.params`), not only top-level `def`/`class` names.
- **verification_rate** — share of claims given a definitive verified/contradicted
  verdict by real `pytest` execution.

## Install

```bash
uv sync --extra dev          # core + dev tooling
uv sync --extra dev --extra llm --extra live --extra react   # + judge/live runners
```

## Usage

Python API — run an architecture, then score (decoupled so you can re-score later):

```python
from pathlib import Path
from agent_eval_harness import (
    load_tasks, run_architecture, score_results, write_csv,
    RoutingAccuracy, VerificationRate,
)

tasks = load_tasks(Path("datasets/small_v1.jsonl"))
results = run_architecture(tasks, my_runner)            # the expensive part
rows = score_results(results, tasks, [RoutingAccuracy(), VerificationRate()])
write_csv(rows, Path("results.csv"))
```

CLI:

```bash
# run both architectures × 4 metrics -> per-arch CSVs + summary.json + persisted runs
agent-eval benchmark --dataset datasets/full_v1.jsonl --out runs/full_v1 \
  --judge-model claude-sonnet-4-6 --runs 3

# re-score persisted runs after a metric/resolver change WITHOUT re-running agents
# (deterministic metrics are free; --with-judge re-runs only the LLM judge)
agent-eval rescore --runs-dir runs/full_v1 --dataset datasets/full_v1.jsonl

# charts
python scripts/make_charts.py runs/full_v1 report/full_v1
```

Set `AGENT_EVAL_PROGRESS=1` for a live per-task progress line on stderr during long
runs. Live architecture invocation needs a running Wayfinder (`WAYFINDER_URL`) and
the project5 MCP servers; inject your own `runner` to run fully offline.

## Design notes

- **Architecture-blind scoring.** Every adapter normalizes its trace into one
  `RunResult`; the judge and metrics only read typed fields, so they can't tell
  which architecture produced an answer.
- **Run/score split + persisted runs.** Agent runs (the costly part — a ReAct loop
  burns ~10× the tokens) are persisted to `<arch>.runs.jsonl`, so a metric fix can
  be re-scored offline for free instead of paying to re-run the agents. This was
  built after a resolver bug was found mid-analysis: the citation resolver had been
  scoring real attribute references as hallucinations; fixing it and re-scoring
  raised wayfinder's citation 0.37 → ~0.80 without re-running anything.
- **Judge bias controlled explicitly.** Every verdict carries its reasoning;
  `SelfConsistentJudge` runs N times and flags scores whose variance exceeds a
  threshold.

## Scope & roadmap

- **Now (v0.5):** framework (datasets / runners / metrics / judge / CLI / rescore),
  40 tasks × 4 buckets over 10 Python OSS repos (click, flask, requests, httpx,
  rich, jinja, werkzeug, starlette, itsdangerous, gunicorn), both arms scored, GT
  reviewed and approved.
- **Toward v1.0:** expand to 40 distinct repos across four domains (web frameworks
  · ML libraries · CLI tools · distributed systems); a post-deploy cloud re-run;
  mkdocs site + more integration examples (LangGraph / bare LangChain adapters).

## Status / roadmap

See [`progress.md`](./progress.md).
