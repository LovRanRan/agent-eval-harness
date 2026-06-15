"""Generate the 4 EVAL_REPORT SVG charts from a benchmark run.

Usage: python scripts/make_charts.py [runs_dir] [out_dir]
Reads <runs_dir>/<arch>.csv + summary.json; writes 4 .svg into out_dir.
Needs matplotlib (`pip install matplotlib`).
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BUCKETS = ["architecture", "function_tracing", "claim_verification", "bug_localization"]


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    runs_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("runs/small_v1")
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("report/small_v1")
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = json.loads((runs_dir / "summary.json").read_text(encoding="utf-8"))
    archs = list(summary.keys())
    rows_by_arch = {arch: _read_rows(runs_dir / f"{arch}.csv") for arch in archs}
    colors = {archs[0]: "#2563eb", archs[1]: "#dc2626"} if len(archs) == 2 else {}

    # 1) routing accuracy: grouped bars per bucket x arch
    fig, ax = plt.subplots(figsize=(8, 4.5))
    width = 0.38
    xs = range(len(BUCKETS))
    for i, arch in enumerate(archs):
        per_bucket = defaultdict(list)
        for row in rows_by_arch[arch]:
            if row["routing_accuracy"]:
                per_bucket[row["bucket"]].append(float(row["routing_accuracy"]))
        vals = [sum(per_bucket[b]) / len(per_bucket[b]) if per_bucket[b] else 0.0 for b in BUCKETS]
        ax.bar([x + i * width for x in xs], vals, width, label=arch, color=colors.get(arch))
    ax.set_xticks([x + width / 2 for x in xs])
    ax.set_xticklabels([b.replace("_", "\n") for b in BUCKETS], fontsize=8)
    ax.set_ylabel("routing accuracy")
    ax.set_title("Routing accuracy by task bucket")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "routing_accuracy.svg")
    plt.close(fig)

    # 2) factual correctness boxplot per arch
    fig, ax = plt.subplots(figsize=(6, 4.5))
    data = [
        [float(r["factual_correctness"]) for r in rows_by_arch[a] if r["factual_correctness"]]
        for a in archs
    ]
    ax.boxplot(data, showmeans=True)
    ax.set_xticks(range(1, len(archs) + 1))
    ax.set_xticklabels(archs)
    ax.set_ylabel("factual_correctness")
    ax.set_title("Factual correctness distribution")
    fig.tight_layout()
    fig.savefig(out_dir / "factual_correctness_boxplot.svg")
    plt.close(fig)

    # 3) cost scatter: factual_correctness vs tokens (log y), colored by arch
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for arch in archs:
        xs2 = [float(r["factual_correctness"] or 0) for r in rows_by_arch[arch]]
        ys2 = [int(r["tokens"] or 0) for r in rows_by_arch[arch]]
        ax.scatter(xs2, ys2, label=arch, color=colors.get(arch), alpha=0.7, s=40)
    ax.set_yscale("log")
    ax.set_xlabel("factual_correctness (per task)")
    ax.set_ylabel("tokens (log)")
    ax.set_title("Cost vs quality per task")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "cost_scatter.svg")
    plt.close(fig)

    # 4) verification_rate per arch (overall mean) + total tokens annotation
    fig, ax = plt.subplots(figsize=(6, 4.5))
    vrs = [summary[a]["metrics"].get("verification_rate", 0.0) for a in archs]
    bars = ax.bar(archs, vrs, color=[colors.get(a) for a in archs])
    for bar, arch in zip(bars, archs, strict=False):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{summary[arch]['total_tokens']:,} tok",
            ha="center",
            fontsize=8,
        )
    ax.set_ylabel("verification_rate")
    ax.set_title("Verification rate per architecture")
    fig.tight_layout()
    fig.savefig(out_dir / "verification_rate.svg")
    plt.close(fig)

    print(f"wrote 4 charts to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
