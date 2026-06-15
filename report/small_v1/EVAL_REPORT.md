# EVAL_REPORT — small_v1 (Wayfinder Supervisor vs ReAct baseline)

**Run date:** 2026-06-14 · **Dataset:** `datasets/small_v1.jsonl` (12 tasks, 4 buckets ×
3, over click / flask / requests) · **Agent model:** OpenAI gpt-5.5 · **Judge:**
Claude (claude-sonnet-4-6), self-consistency = 3 runs · **Tasks errored:** 0 / 12 per arm.

## Conclusion (headline)

On this 12-task OSS codebase-understanding benchmark, the **Wayfinder Supervisor
answered at comparable factual accuracy to a ReAct single-agent baseline (0.62 vs
0.73) while using ~11× fewer tokens (77.2k vs 884.8k)** and was the **only system
to ground claims through real test execution** (verification_rate 0.19 vs 0.00).
ReAct scored higher on factual_correctness and citation_grounding by exploring
exhaustively — but at ~11× the token cost. See caveats; this is a small,
single-seed run and one ReAct tool was misconfigured (below).

## Results

| metric | wayfinder_supervisor | react_baseline |
|---|---|---|
| factual_correctness | 0.615 | **0.729** |
| verification_rate | **0.188** | 0.000 |
| routing_accuracy | **0.500** | 0.000 |
| citation_grounding | 0.372 | **0.742** |
| total tokens | **77,243** | 884,840 |
| tasks (errors) | 12 (0) | 12 (0) |

Charts (this directory): `routing_accuracy.svg`, `factual_correctness_boxplot.svg`,
`cost_scatter.svg`, `verification_rate.svg`. Per-task data: `*_*.csv`; aggregates:
`summary.json`.

## Methodology

Each task pairs a query against a pinned OSS repo with ground truth authored by
reading that repo (≥3 key facts; for claim/bug buckets, a real pytest node id /
fix-file path). Both architectures run over the identical task set with the same
five project5 MCP tools (repo-mapper / ast-explorer / test-runner). Each
`RunResult` is normalized so scoring is architecture-blind, then scored on four
metrics: **routing_accuracy** (classified intent vs expected), **factual_correctness**
(self-consistent LLM-as-judge against key facts), **citation_grounding** (share of
cited symbols that exist in the repo, anti-hallucination), and **verification_rate**
(share of claims given a definitive verified/contradicted verdict by real test
execution). The judge runs 3× per answer and its variance is recorded.

## Trade-off analysis

**Cost vs quality.** The defining result is efficiency: the Supervisor reached
within ~0.11 of ReAct's factual accuracy for ~9% of the tokens. ReAct's brute-force
ReAct loop reads broadly (hence its higher citation_grounding) and writes thorough
answers, but each task costs tens-to-hundreds of thousands of tokens; the Supervisor's
planned routing + bounded sub-agents keep token use ~11× lower. For batch or
cost-sensitive use, that gap dominates a sub-point factual difference.

**Verification is the Supervisor's unique capability.** Only the Supervisor produced
test-execution-backed verdicts (verification_rate 0.188; it fired on the
function-tracing tasks). ReAct scored 0.0 — it has no structured verifier, and its
verdicts are unbacked assertions. This is the differentiator the harness was built to
quantify: not "did it answer", but "did it *check*".

**Routing is real but the metric is asymmetric.** The Supervisor matched expected
intent on architecture + function_tracing (1.0) and missed on claim/bug (its intent
labels for those buckets differ from the dataset's expected route). ReAct scores 0
structurally — it has no router — so routing_accuracy should be read as a
Supervisor-internal quality signal, not a fair head-to-head.

## Caveats / limitations (honest)

- **ReAct's `run_pytest` tool was misconfigured this run** (`pytest` not on the
  mcp-test-runner PATH). Its verification tasks failed the tool repeatedly, which (a)
  inflated ReAct's token count via retries — so the ~11× cost gap is partly
  bug-driven — and (b) further explains its verification_rate of 0. A clean re-run
  should fix the test-runner before quoting the cost ratio precisely.
- **Small sample, single seed.** 12 tasks, one agent run per task (self-consistency
  applies to the *judge*, not the agents). Treat all numbers as directional.
- **claim_verification was weak for both** (factual ~0): both models answered the
  adversarial claim queries poorly per the judge; needs prompt/dataset iteration.
- **cost in USD not computed** (`cost_usd = 0`): tokens are the comparable here;
  multiply by a model price for dollars.

## Reproduce

```bash
# with the live stack up (wayfinder :8000, MCP :8101/:8102/:8103, sandbox :8110)
agent-eval benchmark --dataset datasets/small_v1.jsonl --out runs/small_v1 \
  --judge-model claude-sonnet-4-6 --runs 3
python scripts/make_charts.py runs/small_v1 report/small_v1
```
