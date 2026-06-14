"""Tests for the datasets layer (Commit 2): loading + validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_eval_harness import (
    BUCKETS,
    DatasetError,
    Task,
    load_tasks,
    validate_task,
)

FIXTURE = Path(__file__).parent / "fixtures" / "mini_tasks.jsonl"


def _valid_task(**overrides: object) -> Task:
    base: dict[str, object] = {
        "id": "t1",
        "bucket": "architecture",
        "repo_url": "https://example.com/repo",
        "repo_pin": "abc123",
        "query": "what does it do?",
        "expected_key_facts": ["a", "b", "c"],
        "expected_route": "architecture",
    }
    base.update(overrides)
    return Task(**base)  # type: ignore[arg-type]


def test_loads_mini_fixture_one_task_per_bucket() -> None:
    tasks = load_tasks(FIXTURE)
    assert len(tasks) == 4
    assert {t.bucket for t in tasks} == set(BUCKETS)
    assert all(len(t.expected_key_facts) >= 3 for t in tasks)
    claim = next(t for t in tasks if t.bucket == "claim_verification")
    assert claim.claim_under_test
    bug = next(t for t in tasks if t.bucket == "bug_localization")
    assert bug.bug_fix_files


def test_missing_file_raises() -> None:
    with pytest.raises(DatasetError, match="not found"):
        load_tasks(Path("does-not-exist.jsonl"))


def test_blank_and_comment_lines_are_skipped(tmp_path: Path) -> None:
    f = tmp_path / "d.jsonl"
    f.write_text(
        "# a comment\n\n"
        '{"id":"x","bucket":"architecture","repo_url":"u","repo_pin":"p",'
        '"query":"q","expected_key_facts":["a","b","c"],"expected_route":"architecture"}\n',
        encoding="utf-8",
    )
    assert len(load_tasks(f)) == 1


def test_malformed_json_reports_line_number(tmp_path: Path) -> None:
    f = tmp_path / "d.jsonl"
    f.write_text("{not json}\n", encoding="utf-8")
    with pytest.raises(DatasetError, match=r":1: invalid JSON"):
        load_tasks(f)


def test_duplicate_ids_raise(tmp_path: Path) -> None:
    line = (
        '{"id":"dup","bucket":"architecture","repo_url":"u","repo_pin":"p",'
        '"query":"q","expected_key_facts":["a","b","c"],"expected_route":"architecture"}'
    )
    f = tmp_path / "d.jsonl"
    f.write_text(line + "\n" + line + "\n", encoding="utf-8")
    with pytest.raises(DatasetError, match="duplicate task id"):
        load_tasks(f)


def test_missing_required_field_raises(tmp_path: Path) -> None:
    f = tmp_path / "d.jsonl"
    f.write_text('{"id":"x","bucket":"architecture"}\n', encoding="utf-8")
    with pytest.raises(DatasetError, match="missing required field"):
        load_tasks(f)


def test_validate_requires_three_key_facts() -> None:
    with pytest.raises(DatasetError, match="expected_key_facts"):
        validate_task(_valid_task(expected_key_facts=["only", "two"]))


def test_validate_claim_verification_requires_claim() -> None:
    with pytest.raises(DatasetError, match="claim_under_test"):
        validate_task(_valid_task(bucket="claim_verification"))


def test_validate_bug_localization_requires_fix_files() -> None:
    with pytest.raises(DatasetError, match="bug_fix_files"):
        validate_task(_valid_task(bucket="bug_localization"))


def test_wrong_type_for_key_facts_raises(tmp_path: Path) -> None:
    f = tmp_path / "d.jsonl"
    f.write_text(
        '{"id":"x","bucket":"architecture","repo_url":"u","repo_pin":"p",'
        '"query":"q","expected_key_facts":"notalist","expected_route":"architecture"}\n',
        encoding="utf-8",
    )
    with pytest.raises(DatasetError, match="list of strings"):
        load_tasks(f)
