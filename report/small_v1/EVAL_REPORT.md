# EVAL_REPORT — small_v1 (Wayfinder Supervisor vs ReAct baseline)

**Run:** 2026-06-15 (fair re-score: both arms scored under the fixed citation
resolver; wayfinder runs committed code, no experimental prompt) · **Dataset:**
`datasets/small_v1.jsonl` (12 tasks, 4 buckets × 3, over click / flask / requests) ·
**Agent model:** OpenAI gpt-5.5 (both architectures) · **Judge:** Claude
(claude-sonnet-4-6), self-consistency = 3 runs.

## Conclusion (headline)

On this 12-task OSS codebase-understanding benchmark, the **Wayfinder Supervisor
answered at modestly lower raw quality than a ReAct single-agent baseline
(factual 0.59 vs 0.71, citation 0.80 vs 0.94) while using ~14.6× fewer tokens
(78k vs 1.14M), with zero errors (ReAct had one), and was the only system to route
by intent and to verify claims through real test execution** (verification_rate
0.19 vs 0.00). The cost gap is the decisive, apples-to-apples result; the quality
gaps are real but small.

## Results (both arms scored under the fixed resolver)

| metric | wayfinder_supervisor | react_baseline |
|---|---|---|
| factual_correctness | 0.594 | **0.711** |
| citation_grounding | 0.801 | **0.937** |
| verification_rate | **0.188** | 0.000 |
| routing_accuracy | **0.500** | 0.000 |
| total tokens | **78,256** | 1,144,468 |
| tasks (errors) | 12 (**0**) | 12 (1) |

Charts (this dir): `routing_accuracy.svg`, `factual_correctness_boxplot.svg`,
`cost_scatter.svg`, `verification_rate.svg`. Per-task: `*.csv`; aggregates:
`summary.json`.

## The citation metric was fixed mid-analysis (important)

An earlier version of this report showed citation_grounding 0.37 (wayfinder) vs
0.75 (ReAct) — a damning-looking gap. Investigating it surfaced a bug in **our own
metric**, not the agent: the `RepoSymbolResolver` only credited top-level
`def`/`class` names, so real attribute/method references like `self.callback` or
`ctx.params` were scored as ungrounded — i.e. counted as hallucinations. The
resolver was fixed to also credit a dotted reference when the attribute `.<name>`
actually occurs in the repo (anti-hallucination preserved: an invented attribute
never appears). Re-scoring **both** arms under the fixed resolver:

| citation_grounding | wayfinder | react | gap |
|---|---|---|---|
| old (strict) resolver | 0.37 | 0.75 | 0.38 |
| fixed (fair) resolver | 0.80 | 0.94 | 0.14 |

Most of the apparent gap (0.24 of 0.38) was a measurement artifact. Wayfinder is
not hallucinating — under fair scoring 80% of its cited symbols resolve to real
code. ReAct still cites slightly more grounded symbols by exploring exhaustively.

## Methodology

Each task pairs a query against a pinned OSS repo with ground truth authored by
reading that repo (≥3 key facts; for claim/bug buckets, a real pytest node id /
fix-file path). Both architectures run over the identical task set with the same
five project5 MCP tools (repo-mapper / ast-explorer / test-runner) and the same
agent model (gpt-5.5), so the comparison isolates orchestration, not tools or
model. Each `RunResult` is normalized so scoring is architecture-blind, then scored
on four metrics: **routing_accuracy** (classified intent vs expected),
**factual_correctness** (self-consistent LLM-as-judge against key facts),
**citation_grounding** (share of cited symbols that exist in the repo —
anti-hallucination), and **verification_rate** (share of claims given a definitive
verified/contradicted verdict by real test execution).

## Trade-off analysis

**Cost is the decisive win.** The Supervisor reached within ~0.12 of ReAct's
factual accuracy for **~7% of the tokens** (78k vs 1.14M, a 14.6× gap). ReAct's
open-ended loop explores broadly — hammering the AST tool hundreds of times — which
buys it higher citation and factual scores at an order-of-magnitude token cost. For
batch or cost-sensitive use, that gap dominates the sub-0.15 quality differences.

**Verification + routing are the Supervisor's unique, architectural capabilities.**
Only the Supervisor classifies intent (routing 0.50) and converts tool results into
test-execution-backed verdicts (verification 0.19). ReAct has the identical pytest
tool yet scores 0 on both — it has no router and no structured verifier/claim loop,
so these are abilities ReAct lacks by construction, not a fair head-to-head.

**Reliability.** The Supervisor completed all 12 tasks; the ReAct baseline errored
on one (its open loop is more prone to wandering or hitting limits).

## What this benchmark actually compares (fairness note)

The genuinely apples-to-apples axes are **factual_correctness**,
**citation_grounding**, and **token cost** — same model, same tools, both arms
scored under the same fixed resolver. On those, ReAct wins raw answer quality by a
modest margin (factual +0.12, citation +0.14) while spending ~14.6× the tokens; the
Supervisor wins cost decisively and reliability. `routing_accuracy` and
`verification_rate` are structurally one-sided (ReAct has no router/verifier), so
they demonstrate Supervisor capabilities rather than a fair contest. Honest pitch:
"comparable answer quality, an order of magnitude cheaper, plus intent routing and
test-backed verification" — not "beats ReAct on everything".

## Caveats / limitations (honest)

- **Single-seed agent runs** (one agent run per task; self-consistency applies to
  the *judge*, not the agents). Treat numbers as directional.
- **Ground truth pending Haichuan truthfulness review** (see `datasets/README.md`);
  no number here is resume-publishable until vetted.
- **factual_correctness favors ReAct** (0.71 vs 0.59): brute-force exploration
  produces more complete answers per the judge. This is the Supervisor's real weak
  axis, not cost or verification.
- **1 ReAct task errored** (excluded from its metric means; counted in token total).
- **cost in USD not computed** (`cost_usd = 0`); the token column is **agent-only**
  (gpt-5.5) and is the comparable. The two arms' agent spend is the OpenAI side
  (~US$1.5 for all runs). The **LLM-as-judge (Claude) is evaluation overhead, not
  either system's runtime cost** — and with `self-consistency = 3` it grades every
  task three times, so across all the runs in this experiment it is the dominant
  line item (it accounts for most of the month's Anthropic budget). Crucially it is
  identical per task for both arms, so it **cancels out of the wayfinder-vs-ReAct
  comparison**: the ~14.6× token ratio is agent-side and unaffected by judge cost.

## Reproduce

```bash
# live stack: wayfinder :8000 (WAYFINDER_-prefixed env, ENABLE_GITHUB_INGESTION=1),
# MCP :8101/:8102/:8103
agent-eval benchmark --dataset datasets/small_v1.jsonl --out runs/small_v1 \
  --judge-model claude-sonnet-4-6 --runs 3
python scripts/make_charts.py runs/small_v1 report/small_v1
```
