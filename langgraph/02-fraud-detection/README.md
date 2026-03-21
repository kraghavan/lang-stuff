# 🚨 Fraud Detection System

A transaction fraud detector that demonstrates **conditional routing** in LangGraph. Transactions are scored and routed to different paths based on risk level. All code is **complete and ready to run**.

Supports two modes: **rule-based** (no API key) and **LLM-assisted** (uses Claude for medium-risk investigation).

## 🎯 What It Does

1. **Fetch** — Loads and validates the transaction
2. **Score** — Calculates suspicion score from 5 fraud indicators
3. **Route** — Conditional branching based on risk level:
   - Low risk → Instant approve
   - High risk → Instant block
   - Medium risk → Investigate (rule-based or LLM-powered)
4. **Finalize** — Log decision and recommendations

## 🌟 Why LangGraph?

- ✅ **Conditional edges** — Different paths based on computed data
- ✅ **Routing functions** — Return edge keys to control flow
- ✅ **Multi-path branching** — Three distinct processing paths
- ✅ **Loop potential** — Investigation could loop back for deeper analysis

**New concept vs Example 01:** `add_conditional_edges()` — the path through the graph depends on the data, not hardcoded.

## 📁 Files

```
02-fraud-detection/
├── README.md          # This file
├── main.py            # LangGraph fraud detection pipeline
├── fraud_data.py      # Transaction scoring engine (no LLM)
└── test_fraud.py      # Tests (no API key needed)
```

## 🚀 Quick Start

```bash
cd langgraph/02-fraud-detection
pip install -r ../requirements.txt

# Option 1: With LLM (medium-risk uses Claude)
export ANTHROPIC_API_KEY="your-key-here"
python main.py

# Option 2: Without LLM (pure rule-based)
python main.py --no-llm
```

### Example Output (--no-llm)

```
🔒 Fraud Detection System (rule-based only)

TEST 1: NORMAL TRANSACTION
═══════════════════════════════════════════════════════
  FRAUD DETECTION SYSTEM
═══════════════════════════════════════════════════════

📥 Processing transaction TX_20260320...
  Amount: $55.00
  Merchant: Gas Station (gas)
  Location: New York

📊 Analyzing transaction patterns...
  Suspicion Score: 0.000 (low)
  ✓ No suspicious factors detected
  → Routing: LOW risk → quick approve

✅ QUICK APPROVE
  Approved: $55.00

📝 Final: APPROVE (confidence: high)

═══════════════════════════════════════════════════════
  DECISION SUMMARY
═══════════════════════════════════════════════════════
  Transaction: $55.00 at Gas Station
  Suspicion:   0.000 (low)
  Action:      APPROVE
  Confidence:  high
═══════════════════════════════════════════════════════
```

## 🏗️ Architecture

```
                    ┌─────────────────┐
                    │ fetch_transaction│
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ extract_patterns│
                    └────────┬────────┘
                             │
                    [route_by_suspicion]
                    ┌────────┼────────┐
                    │        │        │
              low   │   medium│   high│
                    ▼        ▼        ▼
            ┌───────────┐ ┌─────────┐ ┌───────────┐
            │quick_     │ │invest-  │ │quick_     │
            │approve    │ │igate    │ │block      │
            └─────┬─────┘ └────┬────┘ └─────┬─────┘
                  │            │             │
                  └────────────┼─────────────┘
                               │
                      ┌────────▼────────┐
                      │    finalize     │
                      └────────┬────────┘
                               │
                              END
```

---

## 📖 Code Walkthrough

### The Key Concept: Conditional Edges

In Example 01, all edges were linear: `A → B → C`. Here, the path **depends on the data**:

```python
# Routing function — returns a STRING that maps to the next node
def route_by_suspicion(state) -> Literal["approve", "block", "investigate"]:
    if state["suspicion_category"] == "low":
        return "approve"
    elif state["suspicion_category"] == "high":
        return "block"
    else:
        return "investigate"

# Register conditional edges — maps return values to node names
workflow.add_conditional_edges(
    "extract_patterns",        # Source node
    route_by_suspicion,        # Routing function
    {
        "approve": "quick_approve",    # "approve" → quick_approve node
        "block": "quick_block",        # "block"   → quick_block node
        "investigate": "investigate",  # "investigate" → investigate node
    },
)
```

**How it works:**
1. `extract_patterns` finishes → LangGraph calls `route_by_suspicion(state)`
2. The function returns `"approve"`, `"block"`, or `"investigate"`
3. LangGraph looks up that key in the edge dictionary
4. Execution continues at the corresponding node

### Fraud Scoring (`fraud_data.py`)

Five weighted fraud indicators, each scored 0-1:

| Indicator | Weight | What it checks |
|-----------|--------|----------------|
| Velocity | 0.30 | >5 transactions in 1 hour |
| Amount anomaly | 0.25 | >3 std deviations from mean |
| Location | 0.20 | Location changed in <2 hours |
| Time | 0.10 | Transaction between 12am-6am |
| Merchant | 0.15 | Gambling, crypto, wire transfer |

### Dual Mode (LLM vs Rule-Based)

Medium-risk transactions can be investigated two ways:

- **With LLM** — Claude analyzes the transaction and recommends approve/block/flag
- **Without LLM** — Pure rule-based: score thresholds determine the decision

Both modes produce the same state shape — the graph doesn't care how the decision was made.

---

## 🧪 Testing

```bash
python test_fraud.py         # 5 tests, no API key needed
python fraud_data.py         # Test scoring engine alone
python main.py --no-llm      # Full pipeline without LLM
python main.py               # Full pipeline with Claude
```

## 🎯 Challenges

1. **Add a fraud indicator** — Add "card not present" as a 6th scoring factor
2. **Add a loop** — If investigation confidence is "low", loop back for a second pass
3. **Add more paths** — Split "medium" into "medium-low" (approve with monitoring) and "medium-high" (flag)
4. **Real data** — Replace sample transactions with a Kaggle fraud dataset
5. **Visualize paths** — Track which path each test case takes and print the route

## ✅ Completion Checklist

- [ ] Ran `python main.py --no-llm` — saw all 3 test cases
- [ ] Ran `python test_fraud.py` — all 5 tests pass
- [ ] Understand `add_conditional_edges(source, routing_fn, edge_map)`
- [ ] Understand that routing functions return STRING KEYS, not node references
- [ ] Understand the difference between linear edges and conditional edges
- [ ] Tried at least one challenge

## 📚 Resources

- [LangGraph Conditional Edges](https://langchain-ai.github.io/langgraph/how-tos/branching/)
- [LangGraph Routing](https://langchain-ai.github.io/langgraph/concepts/low_level/#conditional-edges)

---

**Next: [03 — DevOps Troubleshooting Agent](../03-devops-agent) — tool calling and the ReAct pattern →**
