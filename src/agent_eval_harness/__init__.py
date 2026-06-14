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
    Task,
    load_tasks,
)
from agent_eval_harness.judge import Judge, JudgeVerdict
from agent_eval_harness.metric import Metric, MetricScore
from agent_eval_harness.runner import (
    Claim,
    ClaimLabel,
    RiskLevel,
    Runner,
    RunResult,
)

__version__ = "0.0.1"

__all__ = [
    "BUCKETS",
    "Bucket",
    "Claim",
    "ClaimLabel",
    "Dataset",
    "Judge",
    "JudgeVerdict",
    "Metric",
    "MetricScore",
    "RiskLevel",
    "RunResult",
    "Runner",
    "Task",
    "__version__",
    "load_tasks",
]
