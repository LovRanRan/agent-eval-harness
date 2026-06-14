"""Benchmark driver — run multiple architectures over a dataset and summarize.

Ties the pieces together: for each architecture, run every task and score it with
the four metrics, write a per-architecture CSV, then aggregate per-metric means
and token/cost totals into a summary. Orchestration is pure and unit-testable
with fake runners/metrics; the live judge/resolver/runners are wired separately.
"""

from __future__ import annotations

import json
import statistics
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from agent_eval_harness.citations import default_repo_slug
from agent_eval_harness.datasets import Task
from agent_eval_harness.evaluate import EvalRow, evaluate, write_csv
from agent_eval_harness.metric import Metric
from agent_eval_harness.runner import Runner


def clone_repos_for_resolution(tasks: Sequence[Task], root: Path) -> Path:
    """Shallow-clone each unique repo under `root` (named by default_repo_slug).

    Gives the citation `RepoSymbolResolver` a clone to check symbols against,
    independent of how the live agents name their own clones.
    """
    root.mkdir(parents=True, exist_ok=True)
    for repo_url in sorted({task.repo_url for task in tasks}):
        path = root / default_repo_slug(repo_url)
        if not path.exists():
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(path)],
                check=True,
                capture_output=True,
                timeout=180,
            )
    return root


def summarize(
    rows_by_arch: Mapping[str, Sequence[EvalRow]],
    *,
    price_per_1k_usd: float = 0.0,
) -> dict[str, Any]:
    """Per-architecture per-metric means + token/cost totals + error counts."""
    summary: dict[str, Any] = {}
    for arch, rows in rows_by_arch.items():
        scored = [row for row in rows if row.error is None]
        metric_names = sorted({name for row in scored for name in row.metrics})
        means = {
            name: round(
                statistics.fmean([row.metrics[name] for row in scored if name in row.metrics]),
                4,
            )
            for name in metric_names
            if any(name in row.metrics for row in scored)
        }
        total_tokens = sum(row.tokens for row in rows)
        cost = (
            round(total_tokens / 1000.0 * price_per_1k_usd, 4)
            if price_per_1k_usd
            else round(sum(row.cost_usd for row in rows), 4)
        )
        summary[arch] = {
            "tasks": len(rows),
            "errors": sum(1 for row in rows if row.error is not None),
            "metrics": means,
            "total_tokens": total_tokens,
            "cost_usd": cost,
        }
    return summary


def run_benchmark(
    tasks: Sequence[Task],
    runners: Mapping[str, Runner],
    metrics: Sequence[Metric],
    out_dir: Path,
    *,
    price_per_1k_usd: float = 0.0,
) -> dict[str, list[EvalRow]]:
    """Run every architecture over `tasks`, write per-arch CSVs + summary.json."""
    out_dir.mkdir(parents=True, exist_ok=True)
    rows_by_arch: dict[str, list[EvalRow]] = {}
    for arch, runner in runners.items():
        rows = evaluate(tasks, runner, metrics)
        write_csv(rows, out_dir / f"{arch}.csv")
        rows_by_arch[arch] = rows
    summary = summarize(rows_by_arch, price_per_1k_usd=price_per_1k_usd)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return rows_by_arch
