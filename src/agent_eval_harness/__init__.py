"""agent-eval-harness: evaluation harness for LLM agents.

Public API (Commit 1 = typed contracts only; logic lands in later commits):

  datasets  Task, Bucket, BUCKETS, Dataset, load_tasks
  runner    Runner, RunResult, Claim, ClaimLabel, RiskLevel
  metric    Metric, MetricScore
  judge     Judge, JudgeVerdict
"""

from __future__ import annotations

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
    "evaluate",
    "load_tasks",
    "validate_task",
    "write_csv",
]
