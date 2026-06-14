# LEARNINGS — `agent-eval-harness`

> Append-only. One section per closed commit. Never rewrite past sections.
> Four fixed sub-blocks: 🧠 Concepts internalized · ⚠️ Gotchas debugged · 💼 Interview soundbites · 📚 Sources.

---

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
