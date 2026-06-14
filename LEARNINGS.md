# LEARNINGS — `agent-eval-harness`

> Append-only. One section per closed commit. Never rewrite past sections.
> Four fixed sub-blocks: 🧠 Concepts internalized · ⚠️ Gotchas debugged · 💼 Interview soundbites · 📚 Sources.

---

## Commit 5 — runner + architecture adapters (2026-06-14)

### 🧠 Concepts internalized

- The fairness of a Supervisor-vs-ReAct comparison is enforced in one function: `_normalize` maps each architecture's raw output into the same `RunResult`, so the difference between architectures shows up as *data* (ReAct yields no claims → low verification_rate) rather than as special-casing in the scorer.
- Adapters take an injected `AgentInvoke = Callable[[repo, query], Mapping]`. The harness never imports Wayfinder or LangGraph — it only depends on a callable — so the framework stays importable, testable, and decoupled from the systems it grades.
- `_execute` times the call and converts any exception into `RunResult.error`. Errors-as-data is the difference between "one task failed" and "the whole 240-run sweep aborted".
- Defensive normalization of untrusted agent output: coerce unknown claim labels/risk to safe defaults, skip non-dict claim entries, and default malformed numeric fields to 0 — a noisy agent can't produce a `RunResult` that crashes a metric.

### ⚠️ Gotchas debugged

- Narrowing `Any` from a raw dict into a `Literal` (ClaimLabel/RiskLevel): because `item.get(...)` is `Any`, assigning the membership-checked value to a `Literal`-typed variable type-checks without a `cast` — the `Any` branch dominates the conditional's type. (Had this needed a non-Any source, a `cast` would be required.)

### 💼 Interview soundbites

- "Architecture-blindness is structural: each adapter normalizes into one `RunResult`, so when ReAct scores lower on verification_rate it's because it genuinely produced no grounded claims, not because I scored it differently."
- "The harness depends on an injected `(repo, query) -> result` callable, never on the agent frameworks themselves, so it's decoupled from — and can grade — any of them."

### 📚 Sources

- `time.perf_counter` for latency — https://docs.python.org/3/library/time.html#time.perf_counter

## Commit 4 — LLM-as-judge + self-consistency (2026-06-14)

### 🧠 Concepts internalized

- An LLM-as-judge is only trustworthy if it's (a) structured — force JSON output with a fixed schema — and (b) self-consistent — run it N times and reject the score when variance is high. `SelfConsistentJudge` wraps any `Judge` and is itself a `Judge`, so composition is free.
- The judge depends on a tiny `ChatModel` protocol (`complete(prompt) -> str`), not on the Anthropic SDK directly. That keeps the judge logic unit-testable with a fake and makes the LLM provider swappable.
- Graceful degradation matters at eval scale: `_parse_verdict` tolerates markdown fences/prose (extract first `{` … last `}`), clamps the score to [0,1], and on unparseable output returns a score-0 verdict with the raw text in `raw` — one flaky judge call can't crash a 240-run sweep.
- A judged metric is just an adapter: `JudgeMetric` turns a `Judge` into the `Metric` contract so factual_correctness sits alongside the deterministic metrics in one scoring loop.

### ⚠️ Gotchas debugged

- **Optional dep + mypy --strict**: a lazy `import anthropic` (only installed via the `[llm]` extra) makes strict mypy fail with "cannot find module" in CI. Fix: `[[tool.mypy.overrides]] module=["anthropic.*"], ignore_missing_imports=true`.
- **ruff-format version skew**: formatting with a locally pip-installed ruff produced different wrapping than CI's uv-pinned ruff (0.15.17), so `ruff format --check` kept failing in CI even after I "formatted" it. Lesson: always format with the same ruff the gate uses — run it through `uv run` against the synced env, not a stray global ruff.

### 💼 Interview soundbites

- "My LLM judge is structured + self-consistent: it must return a fixed JSON schema, and I run it three times and drop the score if variance exceeds a threshold — so factual_correctness isn't one noisy model call."
- "Judging degrades gracefully — unparseable judge output becomes a flagged score-0 verdict, never an exception, so one bad call can't sink a benchmark sweep."

### 📚 Sources

- Self-consistency (CoT-SC) — https://arxiv.org/abs/2203.11171
- LLM-as-judge bias / MT-Bench — https://arxiv.org/abs/2306.05685

## Commit 3 — deterministic metrics (2026-06-14)

### 🧠 Concepts internalized

- Three of the four metrics are deterministic (no LLM): routing_accuracy is exact-match, verification_rate is a ratio over claim labels, citation_grounding is a ratio over resolvable symbols. Keeping them LLM-free makes them cheap, reproducible, and immune to judge variance.
- **Dependency injection over hard-coding**: `CitationGrounding` takes a `SymbolResolver = Callable[[str], bool]`. In production it wraps mcp-ast-explorer; in tests a lambda. The metric stays a pure, fast unit — the expensive/IO part is the injected collaborator.
- Edge cases are design decisions worth recording in `detail`: empty citations → 1.0 (nothing is hallucinated) but `total == 0` is surfaced so a non-citing agent can't hide; empty claims → verification_rate 0.0.
- `MetricScore.detail` carries the breakdown (counts, the ungrounded symbols) so the eventual EVAL_REPORT can explain *why* a score is what it is, not just the number.

### ⚠️ Gotchas debugged

- De-dup cited symbols with `dict.fromkeys(...)` before scoring — it preserves order and avoids letting a repeated citation skew the grounding ratio; it also calls the (potentially expensive) resolver once per unique symbol.

### 💼 Interview soundbites

- "verification_rate is the metric that justifies the verifier: it's the share of an agent's claims that got a definitive verified/contradicted verdict from real test execution, so I can show whether grounding actually happened rather than asserting it did."
- "I inject the AST symbol resolver into the citation-grounding metric, so the anti-hallucination check is a pure, unit-testable function and the expensive AST lookup is swappable."

### 📚 Sources

- `dict.fromkeys` for order-preserving dedupe — https://docs.python.org/3/library/stdtypes.html#dict.fromkeys

## Commit 2 — datasets layer (2026-06-14)

### 🧠 Concepts internalized

- A JSONL loader for an eval set needs three things beyond `json.loads`: skip blank/comment lines, report errors with `file:line` so a bad dataset is debuggable, and enforce uniqueness of task ids (a duplicate id silently double-counts in metrics).
- Validation splits into shared rules (≥3 key facts for every task) and bucket-specific rules (claim_verification needs a claim; bug_localization needs fix files). Keeping `validate_task` separate from `load_tasks` means it can also guard hand-authored `Task` objects in tests.
- Type-checking untrusted JSON: `json.loads` returns `Any`, so each field goes through a typed helper (`_req_str`, `_as_str_list`, ...) that raises `DatasetError` on a type mismatch — the dataclass then only ever sees correctly-typed values.

### ⚠️ Gotchas debugged

- mypy `redundant-cast`: after `if bucket_raw not in BUCKETS: raise`, mypy already narrows `str` → the `Bucket` Literal via the tuple-membership check, so an explicit `cast("Bucket", ...)` is flagged. Lesson: try removing a cast before adding `# type: ignore`; modern mypy narrows more than you expect.
- When a later commit implements a stub, its Commit-1 "raises NotImplementedError" placeholder test must be deleted/replaced, and any now-unused imports (`pytest`, `load_tasks`) pruned or ruff F401 fails.

### 💼 Interview soundbites

- "The dataset loader fails loud and located — malformed JSON, missing fields, wrong types, and duplicate ids all raise a `DatasetError` with the file:line — because a silently-malformed eval set produces confidently wrong benchmark numbers."

### 📚 Sources

- Python `json` — https://docs.python.org/3/library/json.html
- mypy type narrowing — https://mypy.readthedocs.io/en/stable/type_narrowing.html

## Commit 1 — core eval API skeleton (2026-06-14)

### 🧠 Concepts internalized

- An eval harness is four composable abstractions: **Dataset (`Task`) → Runner (`RunResult`) → Metric (`MetricScore`) / Judge (`JudgeVerdict`)**. Nailing the *types* first (Protocols + dataclasses, no logic) forces the data flow to be correct before any implementation exists.
- **Architecture-blind scoring**: the comparison "Wayfinder Supervisor vs ReAct" is only fair if metrics/judge can't tell which arch produced an answer. The way to guarantee that in code is a normalized `RunResult` — adapter-specific detail lives in `raw`, and scoring reads only the typed fields.
- `Protocol` (structural typing) lets a runner/metric/judge satisfy the contract without inheriting a base class — adapters just need the right shape. `@runtime_checkable` enables `isinstance` checks in tests.
- Errors as data, not exceptions: `RunResult.error` instead of raising means one failing task never aborts a 240-run sweep.

### ⚠️ Gotchas debugged

- ruff `E501` (line >100) fired on inline `# comment` after a dataclass field; ruff-format won't shorten comments, so the fix is to move the comment to its own line above the field. Lint (E501) and format are separate gates — passing one doesn't pass the other.
- CI's `uv run mypy src` checks only `src`, not `tests`, so test-only type slips won't fail CI — but `pytest` still runs the tests, so contract tests still guard behaviour.

### 💼 Interview soundbites

- "I designed the eval API as four typed contracts — Dataset, Runner, Metric, Judge — with an architecture-blind `RunResult` so the Supervisor-vs-ReAct comparison can't leak which system produced an answer into the score."
- "Failures are data (`RunResult.error`), not exceptions, so a single broken task can't sink a full benchmark sweep."

### 📚 Sources

- Anthropic — Building Effective Agents — https://www.anthropic.com/research/building-effective-agents
- Hamel Husain — Your AI Product Needs Evals — https://hamel.dev/blog/posts/evals/

## Commit 0.b — CI + lint/type/test scaffold (2026-06-14)

### 🧠 Concepts internalized

- A repo's "gate" is the contract for what *green* means before any feature code lands: `ruff check` (lint) + `ruff format --check` (style) + `mypy --strict` (types) + `pytest` (behaviour). Wiring it on Commit 0 means every later commit inherits a passing baseline instead of bolting quality on at the end.
- CI matrix (`3.11` × `3.12`) catches version-specific breakage early; `fail-fast: false` so one Python version failing still reports the other.
- The `Makefile gate` target mirrors CI exactly, so "passes locally" and "passes in CI" mean the same thing.

### ⚠️ Gotchas debugged

- `mypy` crashed with `INTERNAL ERROR` when run against the repo via the Cowork mount — root cause was a **locked `.mypy_cache/*.db` sqlite file**, not the code. Running mypy on a clean copy → `Success: no issues found`. Takeaway: `.mypy_cache/` is gitignored and CI uses a fresh runner, so this is a local-mount artifact only, not a real type error.

### 💼 Interview soundbites

- "I gate the eval harness on `ruff` + `mypy --strict` + `pytest` across a 3.11/3.12 matrix from the first commit, so the eval *framework* meets the same rigor bar I use to judge the agents it scores."

### 📚 Sources

- GitHub Actions for Python — https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python
- (Pre-build, pending) LangSmith experiments — https://docs.smith.langchain.com/evaluation
