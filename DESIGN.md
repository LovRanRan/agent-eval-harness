# DESIGN — Commit 1: core eval API skeleton

> **Ownership (rules 13–16):** Haichuan leads this design. Decide the schemas and
> contracts here *before* any production code. Codex only fills local TODOs after
> the design is locked. Each decision below uses the four-step frame:
> **input → output → rules → failure cases → tests → interview explanation.**
>
> How to use: read the prompts, fill each `> ⬜ 你来定:` line, then we write the
> minimal skeleton (dataclasses / Protocols only, no logic). Don't pre-write logic.

---

## 0. Scope of Commit 1

The goal is a **typed skeleton** of the eval API — the four core abstractions and
how they connect — with zero real implementation. Concretely: `datasets`,
`runner`, `metric`, `judge` as Protocols/dataclasses + a `tests/` contract.
The 40-repo data, the Wayfinder/ReAct adapters, and the LLM judges come later
(Commits 2–5).

**Locked from `final_checklist.md` / theme_design (do not re-litigate):**

- 4 task buckets: Architecture Understanding · Function Tracing · Claim Verification · Bug Localization
- 4 metrics: routing_accuracy · factual_correctness · citation_grounding · verification_rate
- 2 architectures compared: Wayfinder Supervisor vs ReAct (Swarm cut)
- Self-consistency on judge: 3 runs, variance < 0.1

---

## 1. `Task` / dataset schema

What is the unit of evaluation? A task pairs a query against a repo with the
ground truth needed to score it.

Prompts to answer:

- What fields does one `Task` carry? (candidate: `id`, `bucket`, `repo_url`,
  `repo_pin` (commit SHA), `query`, `expected_key_facts: list[str]` (≥3),
  `expected_route`, `verifier_test_id: str | None`, `bug_fix_files: list[str] | None`)
- How is a dataset stored on disk? (candidate: one JSONL file per bucket, or one
  `tasks.jsonl` with a `bucket` field — which is easier to diff in PRs?)
- How do bucket-specific fields stay type-safe? (one `Task` with optional fields,
  vs a `Task` base + 4 subtypes?)

> ⬜ 你来定 (input/output): `Task` 的字段 + 磁盘格式 + bucket 多态策略
> ⬜ 你来定 (failure cases): repo pin 失效 / ground truth 缺失 / 套件破损时怎么标
> ⬜ 你来定 (interview): 一句话解释为什么这样建 dataset schema

---

## 2. `Runner` / architecture adapter

A runner executes one architecture against one task and returns a normalized
trace — so Wayfinder Supervisor and ReAct produce *the same* output shape for the
judge.

Prompts to answer:

- What does a `Runner` return? (candidate `RunResult`: `task_id`, `arch`, `answer`,
  `route_taken`, `claims: list[Claim]`, `cited_symbols: list[str]`,
  `tokens`, `cost_usd`, `latency_s`, `error: str | None`)
- What is the `Runner` interface? (candidate `Protocol`: `def run(task: Task) -> RunResult`)
- Where does the Wayfinder-vs-ReAct difference live — inside the adapter, fully
  hidden behind `RunResult`? (it should: the judge must not know which arch ran)

> ⬜ 你来定 (input/output): `RunResult` 字段 + `Runner` Protocol 签名
> ⬜ 你来定 (rules): 归一化边界 —— judge 绝不能看到 arch 特定字段
> ⬜ 你来定 (failure cases): 超时 / quota / crash 如何进 `RunResult.error` 而非抛出
> ⬜ 你来定 (interview): 为什么用 adapter 归一化而不是各 arch 各写 judge

---

## 3. `Metric`

A metric maps `(Task, RunResult)` (or a list, for judge-based ones) to a score.

Prompts to answer:

- Common signature? (candidate `Protocol`: `def score(task: Task, result: RunResult) -> MetricScore`
  where `MetricScore` has `name`, `value: float`, `detail: dict`)
- Which of the 4 metrics are deterministic (routing_accuracy, citation_grounding
  via AST lookup) vs LLM-judged (factual_correctness)? verification_rate — derived
  from `RunResult.claims` labels, no LLM needed?
- How does self-consistency (3 runs, var < 0.1) wrap a metric — a decorator, or
  built into the judge metric only?

> ⬜ 你来定 (input/output): `Metric` Protocol + `MetricScore` 字段
> ⬜ 你来定 (rules): 哪些 metric 确定性 / 哪些走 judge / self-consistency 包在哪层
> ⬜ 你来定 (failure cases): metric 无法计算(无 AST / 无 ground truth)时返回什么
> ⬜ 你来定 (interview): verification_rate 为什么是本框架最强差异化指标

---

## 4. `Judge`

The LLM-as-judge for non-deterministic metrics (factual_correctness).

Prompts to answer:

- Interface? (candidate `Protocol`: `def judge(task, result) -> JudgeVerdict`
  with structured output: `score`, `reasoning`, `flagged_hallucinations`)
- Which provider(s)? theme_design says Claude + GPT; cost note says Sonnet for
  judge. Single judge or dual-judge agreement?
- How is judge bias controlled / disclosed (rule: judge bias must be explicit)?

> ⬜ 你来定 (input/output): `Judge` Protocol + `JudgeVerdict` 字段
> ⬜ 你来定 (rules): provider 选择 + 单/双 judge + bias 披露策略
> ⬜ 你来定 (failure cases): judge 输出非结构化 / 拒答 / 超 variance 阈值
> ⬜ 你来定 (interview): 怎么向面试官证明 judge 数字可信

---

## 5. How the four connect (the one diagram that matters)

```
Dataset(tasks.jsonl) ──> Runner[arch] ──> RunResult ──┐
                                                       ├─> Metric[] ──> MetricScore[]
                              (ground truth in Task) ──┘        │
                                                        Judge (for LLM metrics)
                                                                │
                                                          EVAL_REPORT.md + CSV
```

> ⬜ 你来定: 这张图对不对?有没有遗漏的边(例如 cost tracking / failure-mode taxonomy 挂在哪)?

---

## 6. Decision log (fill as you lock each section)

| # | Decision | Locked value | Date |
|---|---|---|---|
| 1 | Task schema + disk format | Single frozen `Task` dataclass with optional bucket-specific fields (`verifier_test_id`, `claim_under_test`, `bug_fix_files`); one `tasks.jsonl`, one task/line with a `bucket` field. `Dataset = list[Task]`. Per-bucket required-field validation deferred to `validate_task` (Commit 2). | 2026-06-14 |
| 2 | RunResult + Runner Protocol | `RunResult` is architecture-blind (judge/metrics read only typed fields; adapter trace hidden in `raw`). Errors via `RunResult.error`, never raised. `Claim` carries `label` (verified/unverified/contradicted) + `risk_level` + `test_id`. `Runner` = `Protocol` with `arch: str` + `run(task) -> RunResult`. | 2026-06-14 |
| 3 | Metric + MetricScore | `Metric` = `Protocol` with `name` + `score(task, result) -> MetricScore`; `MetricScore.value` normalized to [0,1] + `detail` dict. Deterministic metrics implement directly; judged metric delegates to `Judge` + self-consistency wrapper (Commit 4). | 2026-06-14 |
| 4 | Judge + JudgeVerdict | `Judge` = `Protocol` with `judge(task, result) -> JudgeVerdict`; verdict carries `score` + `reasoning` + `flagged_hallucinations` for auditability (explicit bias control). Self-consistency (3 runs, var<0.1) applied on top in Commit 4. | 2026-06-14 |
| 5 | Module/file layout under `src/agent_eval_harness/` | `datasets.py` / `runner.py` / `metric.py` / `judge.py`; deps flow `metric,judge → datasets,runner` and `runner → datasets` (no cycles). `__init__.py` re-exports the public API. | 2026-06-14 |

> **Status (2026-06-14):** Commit 1 schema locked + skeleton shipped (Protocols + frozen/slots dataclasses, zero logic). Open `⬜ 你来定` prompts above are kept as design rationale; concrete logic lands per-commit (loaders C2 · deterministic metrics C3 · judge C4 · runners C5).
