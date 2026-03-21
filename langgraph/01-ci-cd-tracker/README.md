# 🔄 CI/CD Status Tracker

A deployment pipeline tracker that demonstrates basic LangGraph state management. **No LLM needed** — this is pure state + nodes + edges to learn the fundamentals.

## 🎯 What It Does

Simulates a CI/CD pipeline that tracks state through 5 stages:

```
START → Build → Test → Deploy Staging → Smoke Test → Deploy Prod → END
```

Each stage updates shared state, and later stages check previous results (e.g., skip tests if build failed).

## 🌟 Why LangGraph?

- ✅ **State management** — Shared `TypedDict` flows through all nodes
- ✅ **Node functions** — Each stage is a pure function that modifies state
- ✅ **Edges** — Linear connections between pipeline stages
- ✅ **No LLM needed** — Focus on graph concepts without API complexity

## 📁 Files

```
01-ci-cd-tracker/
├── README.md          # This file
├── main.py            # Complete pipeline implementation
└── test_tracker.py    # Test script (no API key needed)
```

## 🚀 Quick Start

```bash
cd langgraph/01-ci-cd-tracker
pip install -r ../requirements.txt
python main.py          # No API key needed!
```

### Example Output

```
═══════════════════════════════════════════════════════
  CI/CD PIPELINE
═══════════════════════════════════════════════════════
  Project:  payments-api
  Branch:   main
  Commit:   a1b2c3d

🔨 Building payments-api...
  ✓ Build succeeded (2.1s)

🧪 Running tests...
  ✓ 87/87 tests passed (5.3s)

🚀 Deploying to staging...
  ✓ Deployed to staging (8.7s)

🔥 Running smoke tests on staging...
  ✓ 8 endpoints healthy (3.2s)

🌐 Deploying to production...
  ✓ Deployed to production (14.5s)

═══════════════════════════════════════════════════════
  PIPELINE SUMMARY
═══════════════════════════════════════════════════════
  ✓ Build           success
  ✓ Tests           success
  ✓ Staging         success
  ✓ Smoke Tests     success
  ✓ Production      success

  Total Duration: 33.8s

  🎉 Pipeline SUCCEEDED — payments-api@a1b2c3d is live!
═══════════════════════════════════════════════════════
```

## 🏗️ Architecture

```
┌─────────┐     ┌─────────┐     ┌───────────┐     ┌───────────┐     ┌───────────┐
│  Build  │ ──► │  Test   │ ──► │  Deploy   │ ──► │  Smoke    │ ──► │  Deploy   │ ──► END
│         │     │         │     │  Staging  │     │  Test     │     │  Prod     │
└─────────┘     └─────────┘     └───────────┘     └───────────┘     └───────────┘
    │               │               │                 │                 │
    └───────────────┴───────────────┴─────────────────┴─────────────────┘
                        All nodes read/write shared CICDState
```

---

## 📖 Code Walkthrough

### State (`CICDState`)

The state is a `TypedDict` — a shared data structure passed through every node:

```python
class CICDState(TypedDict):
    project_name: str
    build_status: str       # "pending" → "success" or "failed"
    test_status: str
    staging_status: str
    smoke_status: str
    prod_status: str
    logs: List[str]
    errors: List[str]
    duration_seconds: float
```

**Key insight:** State is the *only* way nodes communicate. Node A doesn't call Node B — they both read/write the same state.

### Nodes

Each node is a function `(state) → state`:

```python
def run_build(state: CICDState) -> CICDState:
    state["build_status"] = "success"   # Update state
    state["logs"].append("Build OK")    # Add to logs
    return state                         # Always return state
```

Nodes check previous stages before running:
```python
def run_tests(state):
    if state["build_status"] != "success":
        state["test_status"] = "skipped"  # Skip if build failed
        return state
    # ... run tests ...
```

### Graph Construction

```python
workflow = StateGraph(CICDState)

workflow.add_node("build", run_build)
workflow.add_node("test", run_tests)
# ... add more nodes ...

workflow.set_entry_point("build")

workflow.add_edge("build", "test")       # build → test
workflow.add_edge("test", "deploy_staging")  # test → staging
# ... add more edges ...

workflow.add_edge("deploy_prod", END)    # last node → END

app = workflow.compile()
result = app.invoke(initial_state)
```

### Key Pattern: Linear Graph

This is the simplest graph pattern — every node connects to exactly one next node:

```python
workflow.add_edge("A", "B")   # A always goes to B
workflow.add_edge("B", "C")   # B always goes to C
workflow.add_edge("C", END)   # C always ends
```

In Example 02 (Fraud Detection), you'll learn **conditional edges** where the path depends on the data.

---

## 🧪 Testing

```bash
python test_tracker.py   # 4 tests, no API key needed
python main.py           # Full pipeline run
```

## 🎯 Challenges

1. **Add a stage** — Insert a "lint" step between build and test
2. **Add conditional logic** — If build fails, skip ALL remaining stages (instead of checking individually)
3. **Add retry logic** — If staging deploy fails, retry once before giving up
4. **Add timing** — Track how long each individual stage takes (not just total)
5. **Visualize the graph** — Use `app.get_graph().print_ascii()` to see the structure

## ✅ Completion Checklist

- [ ] Ran `python main.py` and saw the pipeline execute
- [ ] Ran `python test_tracker.py` — all 4 tests pass
- [ ] Understand how `TypedDict` defines shared state
- [ ] Understand that nodes are just `(state) → state` functions
- [ ] Understand `add_edge("A", "B")` creates linear flow
- [ ] Understand `set_entry_point()` and `END`

## 📚 Resources

- [LangGraph StateGraph](https://langchain-ai.github.io/langgraph/concepts/low_level/#stategraph)
- [LangGraph Quickstart](https://langchain-ai.github.io/langgraph/tutorials/introduction/)

---

**Next: [02 — Fraud Detection](../02-fraud-detection) — add conditional routing based on data →**
