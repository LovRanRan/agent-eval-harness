"""Dataset layer — the unit of evaluation (`Task`), loading, and validation.

Disk format: a single `tasks.jsonl`, one task per line, each carrying a `bucket`
field. Rationale: one file diffs cleanly in PRs and keeps the four buckets in one
place; bucket-specific fields are optional on a single `Task` dataclass and
enforced per-bucket by `validate_task`.

Blank lines and lines beginning with `#` are ignored, so datasets can carry
comments.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, cast, get_args

# The four evaluation task buckets (locked in theme_design_v1.md §6).
Bucket = Literal[
    "architecture",  # "What does this project do? Top-3 modules?"
    "function_tracing",  # "What does function X do and what calls it?"
    "claim_verification",  # verify an LLM-generated claim via test execution
    "bug_localization",  # "Which module/function is most suspect?"
]

BUCKETS: tuple[Bucket, ...] = get_args(Bucket)

MIN_KEY_FACTS = 3


class DatasetError(ValueError):
    """Raised when a dataset file is malformed or a task fails validation."""


@dataclass(frozen=True, slots=True)
class Task:
    """One evaluation task: a query against a pinned repo + its ground truth.

    Bucket-specific fields are optional; `validate_task` enforces the per-bucket
    requirements:
      - claim_verification → `claim_under_test` (and usually `verifier_test_id`)
      - bug_localization   → `bug_fix_files` (non-empty)
      - all buckets        → at least `MIN_KEY_FACTS` `expected_key_facts`
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


def validate_task(task: Task, *, where: str = "") -> None:
    """Validate one task against shared + bucket-specific rules.

    Raises `DatasetError` with an optional `where` prefix (e.g. file:line).
    """
    loc = f"{where}: " if where else ""
    if task.bucket not in BUCKETS:
        raise DatasetError(f"{loc}unknown bucket {task.bucket!r} (expected one of {BUCKETS})")
    if not task.id:
        raise DatasetError(f"{loc}task id must be non-empty")
    if len(task.expected_key_facts) < MIN_KEY_FACTS:
        raise DatasetError(
            f"{loc}task {task.id!r}: need >= {MIN_KEY_FACTS} expected_key_facts, "
            f"got {len(task.expected_key_facts)}"
        )
    if task.bucket == "claim_verification" and not task.claim_under_test:
        raise DatasetError(f"{loc}task {task.id!r}: claim_verification requires claim_under_test")
    if task.bucket == "bug_localization" and not task.bug_fix_files:
        raise DatasetError(f"{loc}task {task.id!r}: bug_localization requires bug_fix_files")


def load_tasks(path: Path) -> list[Task]:
    """Load and validate tasks from a JSONL file.

    Raises `DatasetError` on a missing file, malformed JSON, a bad task, or a
    duplicate task id.
    """
    if not path.exists():
        raise DatasetError(f"dataset file not found: {path}")

    tasks: list[Task] = []
    seen_ids: set[str] = set()
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        where = f"{path}:{lineno}"
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise DatasetError(f"{where}: invalid JSON: {exc}") from exc
        if not isinstance(obj, dict):
            raise DatasetError(f"{where}: expected a JSON object, got {type(obj).__name__}")

        task = _task_from_dict(cast("dict[str, Any]", obj), where=where)
        validate_task(task, where=where)
        if task.id in seen_ids:
            raise DatasetError(f"{where}: duplicate task id {task.id!r}")
        seen_ids.add(task.id)
        tasks.append(task)
    return tasks


def _task_from_dict(obj: dict[str, Any], *, where: str) -> Task:
    """Build a `Task` from a parsed JSON object, checking field types."""
    bucket_raw = _req_str(obj, "bucket", where)
    if bucket_raw not in BUCKETS:
        raise DatasetError(f"{where}: unknown bucket {bucket_raw!r} (expected one of {BUCKETS})")
    return Task(
        id=_req_str(obj, "id", where),
        bucket=bucket_raw,
        repo_url=_req_str(obj, "repo_url", where),
        repo_pin=_req_str(obj, "repo_pin", where),
        query=_req_str(obj, "query", where),
        expected_key_facts=_req_str_list(obj, "expected_key_facts", where),
        expected_route=_req_str(obj, "expected_route", where),
        verifier_test_id=_opt_str(obj, "verifier_test_id", where),
        claim_under_test=_opt_str(obj, "claim_under_test", where),
        bug_fix_files=_opt_str_list(obj, "bug_fix_files", where),
        metadata=_opt_dict(obj, "metadata", where),
    )


def _req_str(obj: dict[str, Any], key: str, where: str) -> str:
    if key not in obj:
        raise DatasetError(f"{where}: missing required field {key!r}")
    value = obj[key]
    if not isinstance(value, str):
        raise DatasetError(f"{where}: field {key!r} must be a string, got {type(value).__name__}")
    return value


def _opt_str(obj: dict[str, Any], key: str, where: str) -> str | None:
    if key not in obj or obj[key] is None:
        return None
    return _req_str(obj, key, where)


def _req_str_list(obj: dict[str, Any], key: str, where: str) -> list[str]:
    if key not in obj:
        raise DatasetError(f"{where}: missing required field {key!r}")
    return _as_str_list(obj[key], key, where)


def _opt_str_list(obj: dict[str, Any], key: str, where: str) -> list[str]:
    if key not in obj or obj[key] is None:
        return []
    return _as_str_list(obj[key], key, where)


def _as_str_list(value: Any, key: str, where: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise DatasetError(f"{where}: field {key!r} must be a list of strings")
    return list(value)


def _opt_dict(obj: dict[str, Any], key: str, where: str) -> dict[str, Any]:
    if key not in obj or obj[key] is None:
        return {}
    value = obj[key]
    if not isinstance(value, dict):
        raise DatasetError(f"{where}: field {key!r} must be an object")
    return cast("dict[str, Any]", value)
