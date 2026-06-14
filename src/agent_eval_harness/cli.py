"""Command-line runner: `agent-eval run --dataset <f> --arch <a> --out <csv>`.

The CLI loads a dataset, runs an architecture over it, scores with the default
deterministic metrics, and writes a CSV. The architecture's live invocation
(HTTP to a deployed Wayfinder / a LangGraph ReAct agent) is wired in Commit 8;
until then `build_runner` raises with guidance. `run_eval` takes an injectable
`runner_factory` so the whole pipeline is testable offline with a fake runner.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
from pathlib import Path

from agent_eval_harness.datasets import load_tasks
from agent_eval_harness.evaluate import evaluate, write_csv
from agent_eval_harness.metric import Metric, RoutingAccuracy, VerificationRate
from agent_eval_harness.runner import ReActBaselineRunner, Runner, WayfinderSupervisorRunner

ARCHITECTURES = ("wayfinder_supervisor", "react_baseline")

RunnerFactory = Callable[[str], Runner]


def default_metrics() -> list[Metric]:
    """Metrics that need no external resolver/judge (routing + verification).

    citation_grounding (AST resolver) and factual_correctness (LLM judge) are
    added when the live runners are wired (Commit 8 / 14).
    """
    return [RoutingAccuracy(), VerificationRate()]


def build_runner(arch: str) -> Runner:
    """Construct a Runner with its live invocation. Live wiring lands in Commit 8."""
    if arch not in ARCHITECTURES:
        raise ValueError(f"unknown arch {arch!r}; choose from {ARCHITECTURES}")
    cls = WayfinderSupervisorRunner if arch == "wayfinder_supervisor" else ReActBaselineRunner
    raise NotImplementedError(
        f"live invocation for {cls.__name__} is wired in Commit 8 "
        "(inject a runner_factory to run offline)"
    )


def run_eval(
    dataset: Path,
    arch: str,
    out: Path,
    *,
    runner_factory: RunnerFactory = build_runner,
    metrics: Sequence[Metric] | None = None,
) -> int:
    """Load → run → score → write CSV. Returns the number of rows written."""
    tasks = load_tasks(dataset)
    runner = runner_factory(arch)
    rows = evaluate(tasks, runner, list(metrics) if metrics is not None else default_metrics())
    write_csv(rows, out)
    return len(rows)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-eval", description="agent-eval-harness runner")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run an architecture over a dataset and write CSV")
    run.add_argument("--dataset", required=True, type=Path, help="path to a tasks.jsonl file")
    run.add_argument("--arch", required=True, choices=ARCHITECTURES, help="architecture to run")
    run.add_argument("--out", required=True, type=Path, help="output CSV path")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "run":
        count = run_eval(args.dataset, args.arch, args.out)
        print(f"wrote {count} rows to {args.out}")
        return 0
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
