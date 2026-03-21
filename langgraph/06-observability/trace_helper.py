"""
Trace Helper — Terminal-Based LangSmith Utilities

View and export traces without the web UI.
Useful for debugging in the terminal or CI/CD.

Usage:
    python trace_helper.py                  # Print latest trace
    python trace_helper.py export           # Export to JSON
    python trace_helper.py list 5           # List last 5 traces
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

DEFAULT_PROJECT = os.getenv("LANGCHAIN_PROJECT", "langgraph-learning")


def get_client():
    """Get LangSmith client."""
    from langsmith import Client
    return Client()


def print_latest_trace(project_name: str = DEFAULT_PROJECT):
    """Print the most recent trace summary to console."""
    client = get_client()

    try:
        traces = list(client.list_runs(
            project_name=project_name,
            limit=1,
            is_root=True,
        ))

        if not traces:
            print("⚠️  No traces found. Run a LangGraph example with LANGCHAIN_TRACING_V2=true first.")
            return

        trace = traces[0]

        print("\n" + "═" * 65)
        print(f"  📊 LATEST TRACE: {trace.name}")
        print("═" * 65)
        print(f"  Status:   {trace.status}")
        print(f"  Duration: {trace.total_time:.2f}s" if trace.total_time else "  Duration: N/A")

        if trace.total_cost:
            print(f"  Cost:     ${trace.total_cost:.6f}")

        if trace.error:
            print(f"  Error:    {trace.error}")

        # Get child runs (steps within the trace)
        child_runs = list(client.list_runs(
            trace_id=trace.id,
            is_root=False,
        ))

        if child_runs:
            print(f"\n  Steps ({len(child_runs)}):")
            for i, child in enumerate(child_runs, 1):
                icon = "✅" if child.status == "success" else "❌"
                time_str = f"{child.total_time:.2f}s" if child.total_time else "N/A"
                cost_str = f" (${child.total_cost:.4f})" if child.total_cost else ""
                print(f"    {i}. {icon} {child.name} ({time_str}{cost_str})")

                if child.error:
                    print(f"       ⚠️  {child.error[:80]}")

        if hasattr(trace, "url") and trace.url:
            print(f"\n  Full trace: {trace.url}")

        print("═" * 65)

    except Exception as e:
        print(f"❌ Error: {e}")


def list_traces(project_name: str = DEFAULT_PROJECT, limit: int = 5):
    """List recent traces."""
    client = get_client()

    try:
        traces = list(client.list_runs(
            project_name=project_name,
            limit=limit,
            is_root=True,
        ))

        if not traces:
            print("⚠️  No traces found.")
            return

        print(f"\n📊 Last {len(traces)} Traces ({project_name})\n")
        print(f"  {'#':<4} {'Name':<35} {'Status':<10} {'Time':<8} {'Cost':<10}")
        print("  " + "─" * 70)

        for i, trace in enumerate(traces, 1):
            time_str = f"{trace.total_time:.1f}s" if trace.total_time else "N/A"
            cost_str = f"${trace.total_cost:.4f}" if trace.total_cost else "—"
            print(f"  {i:<4} {(trace.name or 'unnamed')[:35]:<35} {trace.status:<10} {time_str:<8} {cost_str:<10}")

    except Exception as e:
        print(f"❌ Error: {e}")


def export_trace_to_json(
    project_name: str = DEFAULT_PROJECT,
    filename: str = "latest_trace.json",
):
    """Export the latest trace to JSON for offline analysis."""
    client = get_client()

    try:
        traces = list(client.list_runs(
            project_name=project_name,
            limit=1,
            is_root=True,
        ))

        if not traces:
            print("No traces found")
            return

        trace = traces[0]

        child_runs = list(client.list_runs(
            trace_id=trace.id,
            is_root=False,
        ))

        trace_data = {
            "name": trace.name,
            "status": trace.status,
            "duration_seconds": trace.total_time,
            "cost_usd": trace.total_cost,
            "error": trace.error if trace.error else None,
            "steps": [
                {
                    "name": child.name,
                    "duration_seconds": child.total_time,
                    "cost_usd": child.total_cost,
                    "status": child.status,
                    "error": child.error if child.error else None,
                }
                for child in child_runs
            ],
        }

        with open(filename, "w") as f:
            json.dump(trace_data, f, indent=2, default=str)

        print(f"✅ Trace exported to {filename}")

    except Exception as e:
        print(f"❌ Export failed: {e}")


if __name__ == "__main__":
    if not os.getenv("LANGCHAIN_API_KEY"):
        print("❌ LANGCHAIN_API_KEY not set. Run 01-setup/test_connection.py first.")
        sys.exit(1)

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "export":
            export_trace_to_json()
        elif cmd == "list":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            list_traces(limit=limit)
        else:
            print(f"Unknown command: {cmd}. Use: export, list")
    else:
        print_latest_trace()
