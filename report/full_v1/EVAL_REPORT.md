# EVAL_REPORT — full_v1 (Wayfinder Supervisor vs ReAct baseline)

**Run:** 2026-06-15 (fair: both arms scored under the fixed citation resolver;
wayfinder runs committed code, no experimental prompt) · **Dataset:**
`datasets/full_v1.jsonl` (40 tasks, 4 buckets × 10, over click / flask / requests /
httpx / rich / jinja / werkzeug / starlette / itsdangerous / gunicorn) · **Agent
model:** OpenAI gpt-5.5 (both architectures) · **Judge:** Claude
(claude-sonnet-4-6), self-consistency = 3 runs.

## Conclusion (headline)

On this 40-task OSS codebase-understanding benchmark, the **Wayfinder Supervisor
used ~12× fewer tokens (396k vs 4.8M) and completed every task, while a ReAct
single-agent baseline failed 6 of 40 (15%) by running its loop past the recursion
limit**. ReAct produced higher raw answer quality on the tasks it finished
(factual 0.70 vs 0.48, citation 0.88 vs 0.78), but at ~12× the cost and with a
material reliability gap. The Supervisor is also the only system that routes by
intent and verifies claims through real test execution.

## Results (both arms scored under the fixed resolver)

| metric | wayfinder_supervisor | react_baseline |
|---|---|---|
| factual_correctness | 0.482 | **0.702** |
| citation_grounding | 0.776 | **0.884** |
| verification_rate | **0.094** | 0.000 |
| routing_accuracy | **0.475** | 0.000 |
| total tokens | **396,223** | 4,812,463 |
| tasks (errors) | 40 (**0**) | 40 (**6**) |

Charts (this dir): `routing_accuracy.svg`, `factual_correctness_boxplot.svg`,
`cost_scatter.svg`, `verification_rate.svg`. Per-task: `*.csv`; aggregates:
`summary.json`.

## Reliability: ReAct's loop runs away at scale

All 6 ReAct failures were `GraphRecursionError` — its open-ended think→act loop did
not terminate within the step limit on the harder repos. The Supervisor's bounded,
planned graph (router → sub-agents → verifier → synthesizer) completed all 40. A
15% non-termination rate is a real architectural liability of the single-agent loop
that the metric table alone understates, since errored tasks are excluded from
ReAct's quality means — i.e. ReAct's 0.70 factual is computed over only the 34
tasks it actually finished.

## The citation metric was fixed before this run (so the comparison is fair)

An earlier version scored citation_grounding with a resolver that only credited
top-level `def`/`class` names, marking real attribute references (`self.callback`,
`ctx.params`) as ungrounded — which made wayfinder look like it was hallucinating
(0.37 vs ReAct 0.75). The resolver was fixed to also credit a dotted reference when
the attribute actually occurs in the repo. **Both arms here are scored under the
fixed resolver**, so the citation row is now a fair comparison: 0.78 vs 0.88 — a
small gap, with neither system materially hallucinating.

## Methodology

Each task pairs a query against a pinned OSS repo with ground truth authored by
reading that repo (≥3 key facts; for claim/bug buckets, a real pytest node id /
fix-file path). Both architectures run over the identical task set with the same
five project5 MCP tools (repo-mapper / ast-explorer / test-runner) and the same
agent model (gpt-5.5), so the comparison isolates orchestration, not tools or
model. Each `RunResult` is normalized so scoring is architecture-blind, then scored
on four metrics: **routing_accuracy**, **factual_correctness** (self-consistent
LLM-as-judge), **citation_grounding** (share of cited symbols that exist in the
repo), and **verification_rate** (share of claims given a definitive verdict by
real test execution).

## Trade-off analysis

**Cost + reliability are the Supervisor's wins.** ~12× fewer tokens and zero
failures vs ReAct's 6. ReAct's open loop explores exhaustively (hammering the AST
tool thousands of times across the run), which buys higher factual/citation on the
tasks it finishes but costs an order of magnitude more and runs away on 15%.

**Quality favors ReAct on the apples-to-apples axes**, by a real margin on factual
(0.70 vs 0.48 — wider on this harder 40-repo set than on small_v1's 0.59) and a
small margin on citation (0.88 vs 0.78). factual is the Supervisor's genuine weak
spot: brute-force exploration produces more complete answers per the judge.

**Routing + verification are structurally one-sided** (ReAct has no router/verifier,
scores 0 by construction) — they demonstrate Supervisor capabilities, not a fair
contest.

## Cost (real spend, honestly)

`cost_usd` is not auto-computed; the token column is **agent-only** (gpt-5.5).
Empirically the OpenAI agent spend dominated this project's bill (real money via
auto-recharge, not free credits) and was driven almost entirely by the **ReAct
arm** — its ~4.8M-token loop (and re-running it) is what cost the money, while the
Supervisor's 396k-token runs were ~an order of magnitude cheaper. The Claude judge
is comparatively cheap and, being identical per task for both arms, cancels out of
the comparison. The ~12× token ratio is the headline.

## Caveats / limitations (honest)

- **Single-seed agent runs**; self-consistency applies to the judge, not the agents.
- **Ground truth pending Haichuan truthfulness review** (see `datasets/README.md`) —
  especially the function-tracing "what calls it" claims for the 7 newer repos. No
  number is resume-publishable until vetted.
- **factual_correctness favors ReAct** (0.70 vs 0.48) — the Supervisor's real weak
  axis, and the gap widened on this harder set.
- **ReAct's 0.70 factual / 0.88 citation are over the 34 tasks it finished**; its 6
  recursion failures are excluded from those means but counted in tokens and errors.
- **cost in USD not computed**; tokens are the comparable, ~12× is the headline.

## Reproduce

```bash
# live stack: wayfinder :8000 (WAYFINDER_-prefixed env, ENABLE_GITHUB_INGESTION=1),
# MCP :8101/:8102/:8103
agent-eval benchmark --dataset datasets/full_v1.jsonl --out runs/full_v1 \
  --judge-model claude-sonnet-4-6 --runs 3
python scripts/make_charts.py runs/full_v1 report/full_v1
```
