# LEARNINGS — `agent-eval-harness`

> Append-only. One section per closed commit. Never rewrite past sections.
> Four fixed sub-blocks: 🧠 Concepts internalized · ⚠️ Gotchas debugged · 💼 Interview soundbites · 📚 Sources.

---

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
