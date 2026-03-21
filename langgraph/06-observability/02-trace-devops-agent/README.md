# 02 — Trace DevOps Agent (Tool Calling)

Add LangSmith tracing to the DevOps Agent (Example 03) and debug tool-calling issues.

## What You'll See

LangSmith shows the full ReAct loop — every LLM decision and tool call with timing and cost:

```
DevOps Agent Trace (3.2s, $0.0042)
├─ Agent Decision (1.1s, $0.0042)
│   └─ LLM: "I should check logs first"
├─ Tool: check_logs("api-gateway") (0.8s, $0)
├─ Agent Decision (1.0s, $0.0038)
│   └─ LLM: "DB timeouts. Check database metrics"
├─ Tool: query_database("slow_queries") (0.3s, $0)
└─ Final: "Missing index on users.email"
```

## Quick Start

```bash
# Make sure LangSmith is configured (run 01-setup first)
export LANGCHAIN_TRACING_V2=true

# Run the traced agent
python add_tracing.py

# View trace
python ../trace_helper.py
# Or visit: https://smith.langchain.com
```
