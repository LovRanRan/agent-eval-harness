"""Dataset layer — the unit of evaluation (`Task`) and how tasks are stored.

Commit 1 defines the typed contract only. The JSONL loader / validation logic
lands in Commit 2 (`load_tasks` raises `NotImplementedError` for now).

Disk format decision: a single `tasks.jsonl`, one task per line, each carrying a
`bucket` field. Rationale: one file diffs cleanly in PRs and keeps the four
buckets in one place; bucket-specific fields are optional on a single `Task`
dataclass (validated by bucket at load time) rather than four subtypes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

# The four evaluation task buckets (locked in theme_design_v1.md §6).
Bucket = Literal[
    "architecture",  # "What does this project do? Top-3 modules?"
    "function_tracing",  # "What does function X do and what calls it?"
    "claim_verification",  # verify an LLM-generated claim via test execution
    "bug_localization",  # "Which module/function is most suspect?"
]

BUCKETS: tuple[Bucket, ...] = (
    "architecture",
    "function_tracing",
    "claim_verification",
    "bug_localization",
)


@dataclass(frozen=True, slots=True)
class Task:
    """One evaluation task: a query against a pinned repo + its ground truth.

    Bucket-specific fields are optional; `validate_task` (Commit 2) enforces the
    per-bucket requirements:
      - claim_verification → `claim_under_test` (and usually `verifier_test_id`)
      - bug_localization   → `bug_fix_files` (non-empty)
      - all buckets        → at least 3 `expected_key_facts`
    """

    id: str
    bucket: Bucket
    repo_url: str
    repo_pin: str  # commit SHA the repo is checked out at, for reproducibility
    query: str
    expected_key_facts: list[str]  # ground-truth facts the answer should contain (>=3)
    expected_route: str  # the routing path/intent a correct run should take
    # claim_verification: test that ground-truths the claim being checked
    verifier_test_id: str | None = None
    claim_under_test: str | None = None
    # bug_localization: files the fix PR touched
    bug_fix_files: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# A dataset is just an ordered collection of tasks; kept as a type alias so the
# rest of the API speaks in `list[Task]` without a wrapper class.
Dataset = list[Task]


def load_tasks(path: Path) -> list[Task]:
    """Load tasks from a JSONL file. Implemented in Commit 2."""
    raise NotImplementedError("load_tasks lands in Commit 2 (datasets layer)")
