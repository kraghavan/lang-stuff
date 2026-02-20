# LangGraph Examples

Complex agentic workflows that require loops, branches, and state management.

## When to Use LangGraph (vs LangChain)

Use LangGraph when you need:
- ✅ **Loops** - "Keep investigating until we find the answer"
- ✅ **Conditional routing** - "If risk is high, take path A, else path B"
- ✅ **Shared state** - Multiple agents accessing/updating the same data
- ✅ **Multi-agent coordination** - Agents that interact with each other
- ✅ **Human-in-the-loop** - Pause for human approval/input

Use LangChain when:
- ❌ Simple linear flow: A → B → C
- ❌ Single-pass processing
- ❌ No need to revisit previous steps

## Examples in This Directory

### 1. 📊 Earnings Analyzer
**Pattern**: Iterative investigation with adaptive depth

```
User query → Fetch filing → Extract metrics → Detect anomalies
    ↓ (if anomaly found)
    └→ Investigate → Fetch context → Re-analyze → (loop until explained)
```

**Learn**: State management, conditional loops, stopping criteria

[See full example →](./01-earnings-analyzer)

---

### 2. 💰 Loan Approval
**Pattern**: Multi-stage gates with conditional routing

```
Application → Credit check → 
    ├─ (Score < 600) → Reject
    ├─ (600-700) → Additional verification → Manual review
    └─ (> 700) → Income check → Auto-approve
```

**Learn**: Conditional edges, multi-path routing, human-in-the-loop

[See full example →](./02-loan-approval)

---

### 3. 🚨 Fraud Detection  
**Pattern**: Risk-adaptive investigation

```
Transaction → Rule check →
    ├─ (Low risk) → Approve
    ├─ (Medium risk) → Pattern analysis → Decision
    └─ (High risk) → Deep investigation → Alert
```

**Learn**: Dynamic depth, risk-based routing, escalation patterns

[See full example →](./03-fraud-detection)

---

## Quick Start

```bash
# Choose an example
cd 01-earnings-analyzer

# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Run it
python simple_version.py
```

## Common Patterns Across Examples

All examples demonstrate:
- **State management** - Shared data structure across nodes
- **Conditional routing** - Dynamic path selection based on data
- **Iterative refinement** - Loops until condition met
- **Explainability** - Clear reasoning for decisions
- **Error handling** - Graceful failures and retries

## Key LangGraph Concepts

### State
Shared data structure passed between all nodes:
```python
from typing import TypedDict

class AnalysisState(TypedDict):
    company: str
    metrics: dict
    anomalies: list
    explanation: str
```

### Nodes
Functions that process and modify state:
```python
def extract_metrics(state: AnalysisState) -> AnalysisState:
    # Process state
    state["metrics"] = {...}
    return state
```

### Edges
Connections between nodes:
```python
# Simple edge: always go to next node
workflow.add_edge("extract_metrics", "detect_anomalies")

# Conditional edge: route based on state
workflow.add_conditional_edges(
    "detect_anomalies",
    route_based_on_anomalies,
    {
        "investigate": "deep_dive",
        "finish": END
    }
)
```

### Compilation
Turn graph into runnable application:
```python
app = workflow.compile()
result = app.invoke(initial_state)
```

## Tips for Building LangGraph Applications

1. **Start simple** - Build linear flow first, add complexity later
2. **Design state carefully** - All nodes need access to shared data
3. **Use conditional edges** - For branching logic
4. **Add loops judiciously** - Always have exit conditions
5. **Test incrementally** - Test each node independently first
6. **Visualize your graph** - Use `mermaid` to draw the flow

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)
- [LangGraph Tutorials](https://langchain-ai.github.io/langgraph/tutorials/)

---

**Ready to build? Start with the [Earnings Analyzer](./01-earnings-analyzer) →**