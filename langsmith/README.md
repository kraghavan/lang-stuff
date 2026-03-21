# 🔍 LangSmith — Observability & Debugging

LangSmith observability has been integrated into the LangGraph module as **production monitoring** for the workflows you build there.

**See: [langgraph/06-observability/](../langgraph/06-observability/)**

## What's There

| Example | What It Does |
|---------|-------------|
| 01-setup | Configure LangSmith, verify connection |
| 02-trace-devops-agent | Trace the ReAct agent's tool-calling loop |
| 03-monitor-trading-team | Trace multi-agent negotiations and costs |
| 04-evaluate-fraud | Test fraud detection accuracy on 20 transactions |
| 05-production-monitoring | Cost & latency reporting across all examples |

## Why It's in LangGraph

LangSmith instruments **existing LangGraph workflows** — it doesn't create new ones. Keeping it nested inside `langgraph/` makes the connection obvious: build the agent (examples 01-05), then observe it (example 06).

## Quick Start

```bash
cd langgraph/06-observability
cat README.md
```
