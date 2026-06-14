"""agent-eval-harness: evaluation harness for LLM agents.

Public API (Commit 1 = typed contracts only; logic lands in later commits):

  datasets  Task, Bucket, BUCKETS, Dataset, load_tasks
  runner    Runner, RunResult, Claim, ClaimLabel, RiskLevel
  metric    Metric, MetricScore
  judge     Judge, JudgeVerdict
"""

from __future__ import annotations

from agent_eval_harness.citations import (
    RepoSymbolResolver,
    default_repo_slug,
    extract_cited_symbols,
)
from agent_eval_harness.datasets import (
    BUCKETS,
    Bucket,
    Dataset,
    DatasetError,
    Task,
    load_tasks,
    validate_task,
)
from agent_eval_harness.evaluate import EvalRow, evaluate, write_csv
from agent_eval_harness.experiment import (
    clone_repos_for_resolution,
    run_benchmark,
    summarize,
)
from agent_eval_harness.judge import (
    AnthropicChatModel,
    ChatModel,
    FactualCorrectnessJudge,
    Judge,
    JudgeVerdict,
    SelfConsistentJudge,
)
from agent_eval_harness.metric import (
    CitationGrounding,
    JudgeMetric,
    Metric,
    MetricScore,
    RoutingAccuracy,
    SymbolResolver,
    VerificationRate,
)
from agent_eval_harness.runner import (
    AgentInvoke,
    Claim,
    ClaimLabel,
    ReActBaselineRunner,
    RiskLevel,
    Runner,
    RunResult,
    WayfinderSupervisorRunner,
)

__version__ = "0.0.1"

__all__ = [
    "BUCKETS",
    "AgentInvoke",
    "AnthropicChatModel",
    "Bucket",
    "ChatModel",
    "CitationGrounding",
    "Claim",
    "ClaimLabel",
    "Dataset",
    "DatasetError",
    "EvalRow",
    "FactualCorrectnessJudge",
    "Judge",
    "JudgeMetric",
    "JudgeVerdict",
    "Metric",
    "MetricScore",
    "ReActBaselineRunner",
    "RepoSymbolResolver",
    "RiskLevel",
    "RoutingAccuracy",
    "RunResult",
    "Runner",
    "SelfConsistentJudge",
    "SymbolResolver",
    "Task",
    "VerificationRate",
    "WayfinderSupervisorRunner",
    "__version__",
    "clone_repos_for_resolution",
    "default_repo_slug",
    "evaluate",
    "extract_cited_symbols",
    "load_tasks",
    "run_benchmark",
    "summarize",
    "validate_task",
    "write_csv",
]
