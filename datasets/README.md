# datasets

Benchmark task sets for the harness (`load_tasks` consumes the `.jsonl` files).

## `small_v1.jsonl` — 12-task small benchmark

Four buckets × 3 tasks, over five well-known Python repos that ship pytest suites
(a prerequisite for the test-execution verifier):

| bucket | tasks | repos |
|---|---|---|
| architecture | 3 | click, flask, requests |
| function_tracing | 3 | flask (`dispatch_request`), requests (`rebuild_auth`), click (`Command.invoke`) |
| claim_verification | 3 | requests (auth-strip · fragment · cookie-on-redirect) |
| bug_localization | 3 | requests (sessions), flask (sessions), click (core) |

**Provenance / honesty.** Ground truth was authored by cloning each repo at the
pinned commit (`repo_pin`) and reading the source/tests — not from memory. Each
`verifier_test_id` is a real pytest node ID confirmed in the pinned tree, and each
`bug_fix_files` path was confirmed to exist. `expected_route` uses Wayfinder's
intent taxonomy (`architectural` / `behavioral` / `debug`).

> ⚠️ **Pending Haichuan truthfulness review** before any number from this set is
> published (per project rule: resume numbers must be vetted). Review focus:
> the three `claim_verification` expected verdicts and the `bug_localization`
> suspect modules.
