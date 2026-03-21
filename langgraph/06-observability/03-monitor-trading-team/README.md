# 03 — Monitor Trading Team (Multi-Agent)

Add LangSmith tracing to the Trading Team (Example 05) and monitor agent negotiations.

## What You'll See

LangSmith reveals the multi-agent negotiation — which agents blocked, what alternatives were tried, and cost per agent:

```
Trading Team Trace - "Buy NVDA" (8.4s, $0.0156)
├─ Portfolio Manager (0.1s, $0) → Route to Market
├─ Market Agent (1.8s, $0.0068) → BUY NVDA, HIGH conviction
├─ Portfolio Manager (0.1s, $0) → Route to Risk
├─ Risk Agent (0.7s, $0) → BLOCKED (tech 81% > 40% limit)
├─ Portfolio Manager (0.2s, $0) → Back to Market (round 1)
├─ Market Agent (1.6s, $0.0061) → Alternative: BUY UNH
├─ Risk Agent (0.6s, $0) → APPROVED
├─ Compliance Agent (0.4s, $0) → APPROVED
└─ Portfolio Manager (0.3s, $0.0027) → EXECUTE UNH trade
```

## Quick Start

```bash
export LANGCHAIN_TRACING_V2=true
python add_tracing.py                   # Default: "Should we buy NVDA?"
python add_tracing.py --all             # Run 3 scenarios
python ../trace_helper.py               # View latest trace
```
