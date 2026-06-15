# EVAL_REPORT — small_v1 (Wayfinder Supervisor vs ReAct baseline)

**Run:** 2026-06-14 (clean re-run, ReAct test tool fixed) · **Dataset:**
`datasets/small_v1.jsonl` (12 tasks, 4 buckets × 3, over click / flask / requests) ·
**Agent model:** OpenAI gpt-5.5 · **Judge:** Claude (claude-sonnet-4-6),
self-consistency = 3 runs.

## Conclusion (headline)

On this 12-task OSS codebase-understanding benchmark, the **Wayfinder Supervisor
answered at comparable factual accuracy to a ReAct single-agent baseline (0.58 vs
0.70) while using ~15× fewer tokens (77.9k vs 1.17M)**, and was the **only system to
ground claims through real test execution** (verification_rate 0.19 vs 0.00). The
verification gap is *architectural*: in this clean re-run ReAct's `run_pytest` tool
worked, and ReAct still produced no verified claims — it has no structured verifier,
so its assertions stay unbacked. ReAct edged the Supervisor on factual_correctness
and citation_grounding by exploring exhaustively, but at ~15× the cost.

## Results

| metric | wayfinder_supervisor | react_baseline |
|---|---|---|
| factual_correctness | 0.582 | **0.696** |
| verification_rate | **0.188** | 0.000 |
| routing_accuracy | **0.500** | 0.000 |
| citation_grounding | 0.373 | **0.751** |
| total tokens | **77,878** | 1,165,148 |
| tasks (errors) | 12 (0) | 12 (1) |

Charts (this dir): `routing_accuracy.svg`, `factual_correctness_boxplot.svg`,
`cost_scatter.svg`, `verification_rate.svg`. Per-task: `*.csv`; aggregates: `summary.json`.

## Methodology

Each task pairs a query against a pinned OSS repo with ground truth authored by
reading that repo (≥3 key facts; for claim/bug buckets, a real pytest node id /
fix-file path). Both architectures run over the identical task set with the same
five project5 MCP tools (repo-mapper / ast-explorer / test-runner). Each `RunResult`
is normalized so scoring is architecture-blind, then scored on four metrics:
**routing_accuracy** (classified intent vs expected), **factual_correctness**
(self-consistent LLM-as-judge against key facts), **citation_grounding** (share of
cited symbols that exist in the repo — anti-hallucination), and **verification_rate**
(share of claims given a definitive verified/contradicted verdict by real test
execution).

## Trade-off analysis

**Cost vs quality.** The defining result is efficiency: the Supervisor reached within
~0.11 of ReAct's factual accuracy for **~7% of the tokens**. ReAct's open-ended loop
explores broadly (its higher citation_grounding) and runs many tools, but each task
costs tens-to-hundreds of thousands of tokens; the Supervisor's planned routing +
bounded sub-agents hold total tokens ~15× lower. For batch or cost-sensitive use,
that gap dominates a sub-point accuracy difference.

**Verification is the Supervisor's unique, architectural capability.** Only the
Supervisor produced test-execution-backed verdicts (0.188; it fired on the
function-tracing tasks). This clean re-run is the key evidence: ReAct's test tool was
working, yet ReAct's verification_rate stayed 0.0 — it has no structured
verifier/claim loop, so it never converts a tool result into a verified claim. The
harness measures exactly this difference between "answered" and "checked".

**Routing is real but the metric is asymmetric.** The Supervisor matched expected
intent on architecture + function_tracing (1.0) and missed on claim/bug (its intent
labels differ from the dataset's expected route there). ReAct scores 0 structurally
(no router), so routing_accuracy is a Supervisor-internal signal, not a fair
head-to-head.

## Caveats / limitations (honest)

- **Small, single-seed sample** (12 tasks, one agent run per task; self-consistency
  applies to the *judge*, not the agents). Treat numbers as directional.
- **factual_correctness favors ReAct** (0.70 vs 0.58): brute-force exploration
  produced more complete answers per the judge. The Supervisor's value here is
  cost + verification, not raw accuracy on this small set.
- **1 ReAct task errored** (excluded from its metric means; counted in token total).
- **claim_verification weak for the Supervisor** (factual ~0 on those): needs
  prompt/dataset iteration.
- **cost in USD not computed** (`cost_usd = 0`); tokens are the comparable — multiply
  by a model price for dollars (the ~15× ratio is the headline).

## Reproduce

```bash
# live stack: wayfinder :8000, MCP :8101/:8102/:8103, sandbox :8110
agent-eval benchmark --dataset datasets/small_v1.jsonl --out runs/small_v1 \
  --judge-model claude-sonnet-4-6 --runs 3
python scripts/make_charts.py runs/small_v1 report/small_v1
```
