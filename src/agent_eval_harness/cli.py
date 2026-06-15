"""Command-line runner: `agent-eval run --dataset <f> --arch <a> --out <csv>`.

The CLI loads a dataset, runs an architecture over it, scores with the default
deterministic metrics, and writes a CSV. The architecture's live invocation
(HTTP to a deployed Wayfinder / a LangGraph ReAct agent) is wired in Commit 8;
until then `build_runner` raises with guidance. `run_eval` takes an injectable
`runner_factory` so the whole pipeline is testable offline with a fake runner.
"""

from __future__ import annotations

import argparse
import os
from collections.abc import Callable, Sequence
from pathlib import Path

from agent_eval_harness.datasets import load_tasks
from agent_eval_harness.evaluate import evaluate, write_csv
from agent_eval_harness.metric import Metric, RoutingAccuracy, VerificationRate
from agent_eval_harness.runner import (
    ReActBaselineRunner,
    Runner,
    WayfinderSupervisorRunner,
)

ARCHITECTURES = ("wayfinder_supervisor", "react_baseline")

RunnerFactory = Callable[[str], Runner]


def default_metrics() -> list[Metric]:
    """Metrics that need no external resolver/judge (routing + verification).

    citation_grounding (AST resolver) and factual_correctness (LLM judge) are
    added when the live runners are wired (Commit 8 / 14).
    """
    return [RoutingAccuracy(), VerificationRate()]


def build_runner(arch: str) -> Runner:
    """Construct a Runner with its live invocation.

    `wayfinder_supervisor` is wired over HTTP when `WAYFINDER_URL` is set (needs a
    running Wayfinder + the `[live]` extra). The ReAct baseline is wired in a
    follow-up; inject a `runner_factory` to run offline with a fake.
    """
    if arch not in ARCHITECTURES:
        raise ValueError(f"unknown arch {arch!r}; choose from {ARCHITECTURES}")
    if arch == "wayfinder_supervisor":
        base_url = os.environ.get("WAYFINDER_URL")
        if not base_url:
            raise RuntimeError(
                "set WAYFINDER_URL to a running Wayfinder (e.g. http://localhost:8000) "
                "to run the wayfinder_supervisor architecture"
            )
        from agent_eval_harness.live.wayfinder import wayfinder_invoke

        return WayfinderSupervisorRunner(
            wayfinder_invoke(base_url, auth_token=os.environ.get("WAYFINDER_TOKEN"))
        )
    mcp_urls = {
        "repo_mapper": os.environ.get("REACT_REPO_MAPPER_MCP_URL", "http://127.0.0.1:8101/mcp"),
        "ast_explorer": os.environ.get("REACT_AST_EXPLORER_MCP_URL", "http://127.0.0.1:8102/mcp"),
        "test_runner": os.environ.get("REACT_TEST_RUNNER_MCP_URL", "http://127.0.0.1:8103/mcp"),
    }
    from agent_eval_harness.live.react import react_invoke

    model = os.environ.get("REACT_OPENAI_MODEL", "gpt-5.5")
    return ReActBaselineRunner(react_invoke(mcp_urls, model=model))


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


def _build_live_metrics(
    resolution_root: Path, *, judge_model: str, judge_runs: int
) -> list[Metric]:
    """All four metrics wired live: routing + verification (deterministic),
    citation_grounding (repo-clone resolver), factual_correctness (self-consistent
    Claude judge)."""
    from agent_eval_harness.citations import RepoSymbolResolver
    from agent_eval_harness.judge import (
        AnthropicChatModel,
        FactualCorrectnessJudge,
        SelfConsistentJudge,
    )
    from agent_eval_harness.metric import CitationGrounding, JudgeMetric

    judge = SelfConsistentJudge(
        FactualCorrectnessJudge(AnthropicChatModel(judge_model)), runs=judge_runs
    )
    resolver = RepoSymbolResolver([resolution_root])
    return [
        RoutingAccuracy(),
        VerificationRate(),
        CitationGrounding(resolver),
        JudgeMetric(judge),
    ]


def run_benchmark_cmd(
    dataset: Path,
    out: Path,
    *,
    judge_model: str = "claude-sonnet-4-6",
    judge_runs: int = 3,
    price_per_1k_usd: float = 0.0,
    archs: Sequence[str] | None = None,
) -> dict[str, object]:
    """Benchmark architectures × all 4 metrics → CSVs + summary.json.

    `archs` restricts which architectures run (default: all); a single-arch run
    merges with any existing sibling CSVs in `out` when summarizing.
    """
    from agent_eval_harness.experiment import clone_repos_for_resolution, run_benchmark

    selected = list(archs) if archs else list(ARCHITECTURES)
    tasks = load_tasks(dataset)
    resolution_root = out / "repos"
    clone_repos_for_resolution(tasks, resolution_root)
    metrics = _build_live_metrics(resolution_root, judge_model=judge_model, judge_runs=judge_runs)
    runners = {arch: build_runner(arch) for arch in selected}
    run_benchmark(tasks, runners, metrics, out, price_per_1k_usd=price_per_1k_usd)
    from agent_eval_harness.experiment import summarize_csv_dir

    return summarize_csv_dir(out, price_per_1k_usd=price_per_1k_usd)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-eval", description="agent-eval-harness runner")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run an architecture over a dataset and write CSV")
    run.add_argument("--dataset", required=True, type=Path, help="path to a tasks.jsonl file")
    run.add_argument("--arch", required=True, choices=ARCHITECTURES, help="architecture to run")
    run.add_argument("--out", required=True, type=Path, help="output CSV path")

    bench = sub.add_parser("benchmark", help="run all architectures x 4 metrics -> CSVs + summary")
    bench.add_argument("--dataset", required=True, type=Path, help="path to a tasks.jsonl file")
    bench.add_argument("--out", required=True, type=Path, help="output directory")
    bench.add_argument("--judge-model", default="claude-sonnet-4-6", help="LLM-as-judge model")
    bench.add_argument("--runs", type=int, default=3, help="self-consistency judge runs")
    bench.add_argument(
        "--price-per-1k", type=float, default=0.0, help="USD per 1k tokens for cost column"
    )
    bench.add_argument(
        "--arch",
        action="append",
        choices=ARCHITECTURES,
        help="restrict to an architecture (repeatable); default runs all",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "run":
        count = run_eval(args.dataset, args.arch, args.out)
        print(f"wrote {count} rows to {args.out}")
        return 0
    if args.command == "benchmark":
        run_benchmark_cmd(
            args.dataset,
            args.out,
            judge_model=args.judge_model,
            judge_runs=args.runs,
            price_per_1k_usd=args.price_per_1k,
            archs=args.arch,
        )
        print(f"benchmark written to {args.out} (see summary.json)")
        return 0
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
