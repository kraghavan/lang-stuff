# 05 — Production Monitoring (Cost & Performance)

Track costs, latency, and errors across all LangGraph examples.

## What You'll See

```
📊 Costs (Last 7 days)

Example                   Runs     Total Cost   Avg Cost     Avg Time
─────────────────────────────────────────────────────────────────────
Trading Team              42       $0.6552      $0.015600    8.42s
DevOps Agent              28       $0.2156      $0.007700    3.21s
Fraud Detection           15       $0.0465      $0.003100    1.87s
Migration Approval        8        $0.0312      $0.003900    5.63s
```

## Quick Start

```bash
export LANGCHAIN_TRACING_V2=true
python cost_tracker.py           # Cost report
python ../trace_helper.py list 10  # List recent traces
```
