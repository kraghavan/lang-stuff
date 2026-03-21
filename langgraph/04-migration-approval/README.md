# 🗄️ Database Migration Approval

A database migration workflow with **human-in-the-loop (HITL)** — the graph pauses for human review before executing changes. All code is **complete and ready to run**.

## 🎯 What It Does

1. **Analyze** — Inspect current database schema (3 tables, 16.5M rows)
2. **Review** — Claude reviews the migration plan and assesses risks
3. **Interrupt** — Graph **PAUSES** for human DBA to review
4. **Decide** — Human approves → execute, or rejects → revise
5. **Execute** — Run migration steps (simulated)
6. **Verify** — Confirm changes applied correctly

## 🌟 Why This Is Critical for Production

**You cannot ship AI without human oversight for critical actions.**

- Legal/compliance often requires human approval for data changes
- Database migrations can cause downtime if done wrong
- AI should *propose* and *analyze*, but humans should *decide*
- This pattern applies to: deployments, financial transactions, security changes

## 📁 Files

```
04-migration-approval/
├── README.md              # This file
├── main.py                # HITL migration workflow
├── schema_analyzer.py     # Simulated schema analysis
└── test_migration.py      # Tests (3 offline, 3 need API key)
```

## 🚀 Quick Start

```bash
cd langgraph/04-migration-approval
pip install -r ../requirements.txt
export ANTHROPIC_API_KEY="your-key-here"

# Interactive mode (you'll be prompted to approve/reject)
python main.py

# Auto-approve (for testing)
python main.py --auto-approve

# Auto-reject (for testing)
python main.py --auto-reject
```

### Example Session

```
═══════════════════════════════════════════════════════
  DATABASE MIGRATION APPROVAL WORKFLOW
═══════════════════════════════════════════════════════

📊 Analyzing current database schema...
  ✓ Schema analyzed (3 tables, 16.5M total rows)
  ✓ Migration plan: 5 steps

🤖 Claude is reviewing the migration plan...
  ✓ Review complete (Risk: LOW)

═══════════════════════════════════════════════════════
  ⏸️  HUMAN REVIEW REQUIRED
═══════════════════════════════════════════════════════

📋 Migration Plan:
  Step 1: ADD_INDEX — users.email
  Step 2: ADD_INDEX — orders.user_id
  Step 3: ADD_INDEX — orders.status
  Step 4: CREATE_TABLE — audit_log
  Step 5: ADD_COLUMN — users.last_login_at

🤖 Claude's Review:
  RISK ASSESSMENT: LOW
  All indexes use CONCURRENTLY (no table locks).
  New column is nullable (no table rewrite on PG12+).
  Recommend monitoring replication lag during execution.

  Your decision (approve/reject): approve

🚀 Executing migration...
  ✓ ADD_INDEX completed: idx_users_email
  ✓ ADD_INDEX completed: idx_orders_user_id
  ✓ ADD_INDEX completed: idx_orders_status
  ✓ CREATE_TABLE completed: audit_log
  ✓ ADD_COLUMN completed: last_login_at

  ✓ All 5 steps completed successfully

🔍 Verifying migration...
  ✓ All changes verified successfully

═══════════════════════════════════════════════════════
  WORKFLOW COMPLETE
═══════════════════════════════════════════════════════
  Status: COMPLETE
  Reviews: 1
```

## 🏗️ Architecture

```
┌────────────────┐     ┌────────────┐     ┌──────────────┐
│ analyze_schema │ ──► │ llm_review │ ──► │ human_review │
└────────────────┘     └────────────┘     └──────┬───────┘
                              ↑                   │
                              │            [route_after_review]
                              │            ┌──────┼──────┐
                              │            │      │      │
                          "revise"    "approve" │  "cancel"
                              │            │      │      │
                              │            ▼      │      ▼
                              │     ┌──────────┐  │ ┌─────────┐
                              └─────│ execute  │  │ │ cancel  │
                                    └────┬─────┘  │ └────┬────┘
                                         │        │      │
                                    ┌────▼─────┐  │      │
                                    │ verify   │  │      │
                                    └────┬─────┘  │      │
                                         │        │      │
                                        END      END    END
```

---

## 📖 Code Walkthrough

### The Key Concept: `interrupt()`

LangGraph's `interrupt()` **pauses the graph** and returns control to the caller:

```python
from langgraph.types import interrupt

def human_review(state):
    # This PAUSES the graph execution
    human_input = interrupt({
        "prompt": "Approve this migration?",
        "plan": state["migration_plan"],
    })

    # When resumed, human_input contains the user's response
    state["human_decision"] = human_input["decision"]
    return state
```

### How HITL Works (3 Parts)

**1. Checkpointer** — Saves graph state while paused:
```python
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)
```

**2. Interrupt** — Pauses at a node:
```python
human_input = interrupt({"prompt": "Approve?"})
# Graph freezes here until resumed
```

**3. Resume with Command** — Continue after human input:
```python
from langgraph.types import Command
result = app.invoke(Command(resume={"decision": "approve"}), config=config)
```

### The Reject → Revise Loop

If the human rejects, the graph loops back to `llm_review`:

```python
def route_after_review(state):
    if state["human_decision"] == "approve":
        return "execute"
    elif state["review_count"] >= 3:
        return "cancel"   # Max 3 reviews
    else:
        return "revise"   # Loop back to LLM review
```

Claude sees the human's feedback and adjusts the review. This creates a conversation between the human and AI about the migration plan.

---

## 🧪 Testing

```bash
python schema_analyzer.py         # Test schema analysis
python test_migration.py          # 6 tests (3 offline, 3 need API key)
python main.py --auto-approve     # Full flow with auto-approval
python main.py --auto-reject      # Full flow with auto-rejection
python main.py                    # Interactive mode
```

## 🎯 Challenges

1. **Add a step** — Add a "backup database" step before execution
2. **Richer feedback** — Let the human edit specific migration steps
3. **Slack integration** — Send the approval request to a Slack channel
4. **Persistent checkpointer** — Use `SqliteSaver` instead of `MemorySaver` to survive restarts
5. **Multi-approver** — Require 2 approvals for HIGH risk migrations

## ✅ Completion Checklist

- [ ] Ran `python main.py --auto-approve` — migration executed
- [ ] Ran `python main.py --auto-reject` — migration cancelled
- [ ] Ran `python main.py` interactively — approved or rejected
- [ ] Understand `interrupt()` — pauses graph execution
- [ ] Understand `Command(resume=...)` — resumes with human input
- [ ] Understand `MemorySaver` — saves state between interrupt and resume
- [ ] Understand the reject → revise loop

## 📚 Resources

- [LangGraph Human-in-the-Loop](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/breakpoints/)
- [LangGraph Checkpointing](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
- [Interrupt API](https://langchain-ai.github.io/langgraph/reference/types/#langgraph.types.interrupt)

---

**Next: [05 — Algorithmic Trading Team](../05-trading-team) — multi-agent system with conflict resolution →**
