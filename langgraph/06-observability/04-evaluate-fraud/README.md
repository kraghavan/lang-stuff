# 04 — Evaluate Fraud Detection (Accuracy Testing)

Test the Fraud Detection system (Example 02) on a dataset and measure accuracy.

## What You'll See

Run 20 transactions (10 legit, 10 fraud) and measure:
- **Accuracy** — How many decisions were correct?
- **False Positives** — Legit transactions incorrectly blocked
- **False Negatives** — Fraud transactions incorrectly approved

```
Evaluation Results: 17/20 correct (85%)

False Positives (2):
  ✗ $800 grocery (traveling) — BLOCKED (should approve)
  ✗ $350 gas station (unusual amount) — BLOCKED (should approve)

False Negatives (1):
  ✗ $2000 crypto at 5pm — APPROVED (should block, score 0.38 < 0.40 threshold)
```

## Quick Start

```bash
# Run locally (no LangSmith needed for basic eval)
python run_evaluation.py

# With LangSmith (traces each evaluation)
export LANGCHAIN_TRACING_V2=true
python run_evaluation.py
```
