"""
Cost & Performance Tracker — Production Monitoring

Queries LangSmith for traces and summarizes cost, latency,
and error rates across all LangGraph examples.

Usage:
    python cost_tracker.py              # Last 7 days
    python cost_tracker.py 30           # Last 30 days

Requires:
    - LANGCHAIN_API_KEY
    - Traces to have been captured (run examples with LANGCHAIN_TRACING_V2=true)
"""

import os
import sys
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DEFAULT_PROJECT = os.getenv("LANGCHAIN_PROJECT", "langgraph-learning")


def get_daily_costs(days: int = 7, project_name: str = DEFAULT_PROJECT):
    """
    Get cost and performance summary for the last N days.

    Groups traces by name and shows:
    - Total cost per example
    - Average cost per run
    - Average time per run
    - Error rate
    """
    from langsmith import Client

    client = Client()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    print(f"\n📊 Fetching traces from last {days} days...")

    try:
        runs = list(client.list_runs(
            project_name=project_name,
            start_time=start_date,
            end_time=end_date,
            is_root=True,
        ))
    except Exception as e:
        print(f"❌ Error fetching traces: {e}")
        return

    if not runs:
        print("⚠️  No traces found. Run some examples with LANGCHAIN_TRACING_V2=true first.")
        return

    # Group by trace name
    groups = {}
    for run in runs:
        name = (run.name or "unnamed").split(" - ")[0].strip()

        if name not in groups:
            groups[name] = {
                "runs": 0,
                "total_cost": 0.0,
                "total_time": 0.0,
                "errors": 0,
            }

        groups[name]["runs"] += 1
        groups[name]["total_cost"] += run.total_cost or 0
        groups[name]["total_time"] += run.total_time or 0
        if run.status == "error":
            groups[name]["errors"] += 1

    # Print report
    print(f"\n{'═' * 75}")
    print(f"  COST & PERFORMANCE REPORT — Last {days} Days")
    print(f"  Project: {project_name}")
    print(f"  Total traces: {len(runs)}")
    print(f"{'═' * 75}\n")

    print(f"  {'Example':<28} {'Runs':<6} {'Total Cost':<12} {'Avg Cost':<12} {'Avg Time':<9} {'Errors':<6}")
    print("  " + "─" * 73)

    total_cost = 0
    total_runs = 0

    for name, stats in sorted(groups.items(), key=lambda x: x[1]["total_cost"], reverse=True):
        avg_cost = stats["total_cost"] / stats["runs"] if stats["runs"] > 0 else 0
        avg_time = stats["total_time"] / stats["runs"] if stats["runs"] > 0 else 0
        error_str = str(stats["errors"]) if stats["errors"] > 0 else "—"

        print(
            f"  {name:<28} {stats['runs']:<6} "
            f"${stats['total_cost']:<11.4f} "
            f"${avg_cost:<11.6f} "
            f"{avg_time:<8.2f}s "
            f"{error_str:<6}"
        )

        total_cost += stats["total_cost"]
        total_runs += stats["runs"]

    print("  " + "─" * 73)
    print(f"  {'TOTAL':<28} {total_runs:<6} ${total_cost:<11.4f}")

    # Export to CSV
    csv_path = "costs_report.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Example", "Runs", "Total Cost", "Avg Cost", "Avg Time", "Errors"])
        for name, stats in groups.items():
            writer.writerow([
                name,
                stats["runs"],
                f"${stats['total_cost']:.4f}",
                f"${stats['total_cost'] / max(stats['runs'], 1):.6f}",
                f"{stats['total_time'] / max(stats['runs'], 1):.2f}s",
                stats["errors"],
            ])

    print(f"\n  ✅ Report saved to {csv_path}")
    print(f"{'═' * 75}")


if __name__ == "__main__":
    if not os.getenv("LANGCHAIN_API_KEY"):
        print("❌ LANGCHAIN_API_KEY not set. Run 01-setup/test_connection.py first.")
        sys.exit(1)

    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    get_daily_costs(days=days)
