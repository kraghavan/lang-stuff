"""
LangSmith Prometheus Exporter

Polls LangSmith API every 60s, exposes metrics at http://localhost:8001/metrics
for Prometheus to scrape.

Metrics exported:
  - langsmith_run_cost_usd          (Counter) — Cumulative cost
  - langsmith_requests_total        (Counter) — Request count by status
  - langsmith_latency_seconds       (Histogram) — Latency distribution
  - langsmith_llm_calls_total       (Counter) — LLM calls by model
  - langsmith_tokens_total          (Counter) — Token usage
  - langsmith_agent_calls_total     (Counter) — Agent-specific calls
  - langsmith_negotiation_rounds    (Histogram) — Trading Team rounds
  - langsmith_errors_total          (Counter) — Error count

Requirements:
  pip install prometheus-client langsmith

Usage:
  python prometheus_exporter.py

Environment:
  LANGCHAIN_API_KEY=lsv2_pt_...
  LANGCHAIN_PROJECT=langgraph-learning  (optional)
  POLL_INTERVAL=60                      (optional, seconds)
  EXPORTER_PORT=8001                    (optional)
"""

import os
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

from prometheus_client import start_http_server, Counter, Histogram, Gauge
from langsmith import Client

load_dotenv()

# ═══════════════════════════════════════════════
# Prometheus Metric Definitions
# ═══════════════════════════════════════════════

langsmith_run_cost = Counter(
    "langsmith_run_cost_usd",
    "Cumulative cost in USD across all runs",
    ["project", "example"],
)

langsmith_request_count = Counter(
    "langsmith_requests_total",
    "Total number of LangSmith runs",
    ["project", "example", "status"],
)

langsmith_latency = Histogram(
    "langsmith_latency_seconds",
    "Run latency in seconds",
    ["project", "example"],
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, float("inf")),
)

langsmith_llm_calls = Counter(
    "langsmith_llm_calls_total",
    "Total LLM calls made",
    ["project", "example", "model"],
)

langsmith_tokens = Counter(
    "langsmith_tokens_total",
    "Total tokens used",
    ["project", "example", "type"],  # type: input or output
)

langsmith_agent_calls = Counter(
    "langsmith_agent_calls_total",
    "Agent-specific call counts",
    ["project", "example", "agent"],
)

langsmith_negotiation_rounds = Histogram(
    "langsmith_negotiation_rounds",
    "Number of negotiation rounds (Trading Team)",
    ["project", "example"],
    buckets=(0, 1, 2, 3, 4, 5, float("inf")),
)

langsmith_errors = Counter(
    "langsmith_errors_total",
    "Total errors encountered",
    ["project", "example"],
)

langsmith_last_poll = Gauge(
    "langsmith_last_poll_timestamp",
    "Timestamp of last successful poll",
    ["project"],
)


# ═══════════════════════════════════════════════
# Exporter
# ═══════════════════════════════════════════════

class LangSmithExporter:
    """Polls LangSmith API and updates Prometheus metrics."""

    def __init__(self, project_name: str = None, poll_interval: int = 60):
        self.client = Client()
        self.project_name = project_name or os.getenv("LANGCHAIN_PROJECT", "default")
        self.poll_interval = poll_interval
        self.last_check = datetime.now() - timedelta(hours=1)

    def extract_example_name(self, run_name: str) -> str:
        """'DevOps Agent - Issue 123' → 'DevOps Agent'"""
        if not run_name:
            return "unknown"
        return run_name.split(" - ")[0].strip()

    def collect_metrics(self):
        """Fetch new runs from LangSmith and update Prometheus metrics."""
        try:
            print(f"⏱️  Polling LangSmith ({self.project_name})...", end=" ")

            runs = list(self.client.list_runs(
                project_name=self.project_name,
                start_time=self.last_check,
                is_root=True,
            ))

            if not runs:
                print(f"no new runs since {self.last_check.strftime('%H:%M:%S')}")
                self.last_check = datetime.now()
                langsmith_last_poll.labels(project=self.project_name).set_to_current_time()
                return

            print(f"{len(runs)} new runs")

            for run in runs:
                example = self.extract_example_name(run.name)
                status = run.status or "unknown"

                # Cost (cumulative counter)
                if run.total_cost and run.total_cost > 0:
                    langsmith_run_cost.labels(
                        project=self.project_name, example=example
                    ).inc(run.total_cost)

                # Request count
                langsmith_request_count.labels(
                    project=self.project_name, example=example, status=status
                ).inc()

                # Latency
                if run.total_time and run.total_time > 0:
                    langsmith_latency.labels(
                        project=self.project_name, example=example
                    ).observe(run.total_time)

                # Errors
                if run.error:
                    langsmith_errors.labels(
                        project=self.project_name, example=example
                    ).inc()

                # Token usage — prefer actual counts, fall back to estimation
                self._collect_token_metrics(run, example)

                # Child runs for agent-level detail
                try:
                    children = list(self.client.list_runs(
                        trace_id=run.id, is_root=False
                    ))
                    self._process_children(children, example)
                except Exception:
                    pass

                # State-specific: negotiation rounds
                self._extract_state_metrics(run, example)

            self.last_check = datetime.now()
            langsmith_last_poll.labels(project=self.project_name).set_to_current_time()
            print(f"  ✅ Metrics updated at {self.last_check.strftime('%H:%M:%S')}")

        except Exception as e:
            print(f"❌ Error: {e}")

    def _collect_token_metrics(self, run, example: str):
        """Collect token metrics from a run."""
        # LangSmith provides prompt_tokens/completion_tokens on some runs
        prompt_tokens = getattr(run, "prompt_tokens", None)
        completion_tokens = getattr(run, "completion_tokens", None)

        if prompt_tokens:
            langsmith_tokens.labels(
                project=self.project_name, example=example, type="input"
            ).inc(prompt_tokens)
        if completion_tokens:
            langsmith_tokens.labels(
                project=self.project_name, example=example, type="output"
            ).inc(completion_tokens)

    def _process_children(self, children: list, example: str):
        """Process child runs for LLM and agent metrics."""
        for child in children:
            name = (child.name or "").lower()

            # LLM calls
            if any(kw in name for kw in ("llm", "claude", "chatanthropic", "chatmodel")):
                model = "unknown"
                if child.extra and isinstance(child.extra, dict):
                    model = child.extra.get("metadata", {}).get("ls_model_name", "unknown")

                langsmith_llm_calls.labels(
                    project=self.project_name, example=example, model=model
                ).inc()

                # Token counts from child
                pt = getattr(child, "prompt_tokens", None)
                ct = getattr(child, "completion_tokens", None)
                if pt:
                    langsmith_tokens.labels(
                        project=self.project_name, example=example, type="input"
                    ).inc(pt)
                if ct:
                    langsmith_tokens.labels(
                        project=self.project_name, example=example, type="output"
                    ).inc(ct)

            # Agent calls
            if "agent" in name or "manager" in name:
                agent_name = name.split()[0] if " " in name else name
                langsmith_agent_calls.labels(
                    project=self.project_name, example=example, agent=agent_name
                ).inc()

    def _extract_state_metrics(self, run, example: str):
        """Extract state-specific metrics (e.g., negotiation rounds)."""
        if "trading" in example.lower():
            if run.outputs and isinstance(run.outputs, dict):
                rounds = run.outputs.get("negotiation_round", 0)
                langsmith_negotiation_rounds.labels(
                    project=self.project_name, example=example
                ).observe(rounds)

    def run(self):
        """Run the exporter daemon."""
        port = int(os.getenv("EXPORTER_PORT", "8001"))

        print("═" * 60)
        print("  🚀 LangSmith Prometheus Exporter")
        print("═" * 60)
        print(f"  Project:       {self.project_name}")
        print(f"  Poll interval: {self.poll_interval}s")
        print(f"  Metrics URL:   http://localhost:{port}/metrics")
        print("═" * 60)

        # Verify connection
        try:
            list(self.client.list_projects(limit=1))
            print("  ✅ LangSmith connection verified")
        except Exception as e:
            print(f"  ❌ LangSmith connection failed: {e}")
            sys.exit(1)

        # Start HTTP server
        start_http_server(port)
        print(f"  ✅ HTTP server started on port {port}\n")

        # Main loop
        while True:
            self.collect_metrics()
            time.sleep(self.poll_interval)


if __name__ == "__main__":
    project = os.getenv("LANGCHAIN_PROJECT")
    interval = int(os.getenv("POLL_INTERVAL", "60"))

    exporter = LangSmithExporter(project_name=project, poll_interval=interval)

    try:
        exporter.run()
    except KeyboardInterrupt:
        print("\n⏹️  Exporter stopped.")
        sys.exit(0)
