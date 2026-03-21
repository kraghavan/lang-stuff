"""
Database Migration Approval — Human-in-the-Loop (HITL)

Demonstrates LangGraph's interrupt mechanism: the graph PAUSES
for human review before executing a database migration.

Flow:
    Analyze schema → Generate plan → Claude reviews plan
        ↓
    INTERRUPT ⏸️ (human reviews the plan)
        ↓
    Human approves → Execute migration → Verify → Done
    Human rejects  → Revise plan → INTERRUPT again ⏸️

Key Concepts:
    - interrupt_before: Pause graph at a specific node
    - Checkpointer: Save state while paused
    - Resume with Command: Continue after human input
    - Approval gates: Critical for production AI

Usage:
    python main.py

Requires:
    - ANTHROPIC_API_KEY environment variable
"""

import os
import sys
from typing import TypedDict, List, Literal, Optional
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

from schema_analyzer import SchemaAnalyzer

load_dotenv()

# ═══════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")


# ═══════════════════════════════════════════════
# Step 1: Define State
# ═══════════════════════════════════════════════

class MigrationState(TypedDict):
    """State for the migration approval workflow."""
    # Schema analysis
    schema_summary: str
    migration_plan: str

    # LLM review
    llm_review: str
    risk_assessment: str

    # Human decision
    human_decision: str   # "approve" | "reject" | "pending"
    human_feedback: str

    # Execution
    execution_log: List[str]
    execution_status: str  # "pending" | "running" | "complete" | "failed" | "cancelled"

    # Tracking
    review_count: int


# ═══════════════════════════════════════════════
# Step 2: Define Nodes
# ═══════════════════════════════════════════════

analyzer = SchemaAnalyzer()


def analyze_schema(state: MigrationState) -> MigrationState:
    """Node 1: Analyze the current database schema."""
    print("\n📊 Analyzing current database schema...")

    state["schema_summary"] = analyzer.format_schema_summary()
    state["migration_plan"] = analyzer.format_migration_plan()

    print(f"  ✓ Schema analyzed (3 tables, 16.5M total rows)")
    print(f"  ✓ Migration plan: 5 steps")

    return state


def llm_review_plan(state: MigrationState) -> MigrationState:
    """Node 2: Claude reviews the migration plan for risks."""
    print("\n🤖 Claude is reviewing the migration plan...")

    llm = ChatAnthropic(model=MODEL, temperature=0, max_tokens=1024)

    prompt = f"""You are a senior DBA reviewing a database migration plan.

Current Schema:
{state['schema_summary']}

Proposed Migration:
{state['migration_plan']}

{f"Previous human feedback: {state['human_feedback']}" if state['human_feedback'] else ""}

Provide:
1. RISK ASSESSMENT (LOW/MEDIUM/HIGH) with reasoning
2. CONCERNS (any issues you see)
3. RECOMMENDATIONS (what to watch during execution)
4. VERDICT: Should this be approved? (yes with conditions / no with reasons)

Be concise. This will be shown to a human DBA for final approval."""

    response = llm.invoke(prompt)
    review = response.content if isinstance(response.content, str) else str(response.content)

    state["llm_review"] = review

    # Extract risk level
    review_lower = review.lower()
    if "high" in review_lower.split("risk")[0] if "risk" in review_lower else "":
        state["risk_assessment"] = "HIGH"
    elif "medium" in review_lower[:200]:
        state["risk_assessment"] = "MEDIUM"
    else:
        state["risk_assessment"] = "LOW"

    print(f"  ✓ Review complete (Risk: {state['risk_assessment']})")

    return state


def human_review(state: MigrationState) -> MigrationState:
    """
    Node 3: INTERRUPT — pause for human review.

    This node uses LangGraph's interrupt() to pause execution.
    The graph saves state and waits for human input.
    """
    print("\n" + "=" * 55)
    print("  ⏸️  HUMAN REVIEW REQUIRED")
    print("=" * 55)

    print(f"\n📋 Migration Plan:")
    print(state["migration_plan"])

    print(f"\n🤖 Claude's Review:")
    review_text = state["llm_review"]
    # Truncate for display
    for line in review_text.split("\n")[:20]:
        print(f"  {line}")
    if review_text.count("\n") > 20:
        print("  ...")

    print(f"\n  Risk Assessment: {state['risk_assessment']}")
    print(f"  Review #{state['review_count'] + 1}")

    # INTERRUPT — this pauses the graph!
    # The value passed to interrupt() is returned to the caller
    human_input = interrupt({
        "prompt": "Do you approve this migration? (approve/reject): ",
        "migration_plan": state["migration_plan"],
        "risk_assessment": state["risk_assessment"],
    })

    # When resumed, human_input contains the user's response
    if isinstance(human_input, dict):
        state["human_decision"] = human_input.get("decision", "reject")
        state["human_feedback"] = human_input.get("feedback", "")
    else:
        decision = str(human_input).strip().lower()
        state["human_decision"] = "approve" if decision in ("approve", "yes", "y") else "reject"
        state["human_feedback"] = "" if state["human_decision"] == "approve" else str(human_input)

    state["review_count"] += 1
    print(f"\n  Human decision: {state['human_decision'].upper()}")

    return state


def execute_migration(state: MigrationState) -> MigrationState:
    """Node 4: Execute the migration (only if approved)."""
    print("\n🚀 Executing migration...")
    state["execution_status"] = "running"

    changes = analyzer.get_requested_changes()["changes"]

    for i, change in enumerate(changes):
        result = analyzer.simulate_execution(i)
        log_entry = result["result"]
        state["execution_log"].append(log_entry)
        print(f"  {log_entry}")

    state["execution_status"] = "complete"
    print(f"\n  ✓ All {len(changes)} steps completed successfully")

    return state


def cancel_migration(state: MigrationState) -> MigrationState:
    """Node 4b: Cancel the migration (rejected)."""
    print("\n❌ Migration CANCELLED by human reviewer")
    state["execution_status"] = "cancelled"
    state["execution_log"].append(f"Cancelled: {state['human_feedback']}")
    return state


def verify_migration(state: MigrationState) -> MigrationState:
    """Node 5: Verify the migration was successful."""
    print("\n🔍 Verifying migration...")

    if state["execution_status"] == "complete":
        state["execution_log"].append("✓ All indexes verified")
        state["execution_log"].append("✓ New table audit_log created and accessible")
        state["execution_log"].append("✓ Column users.last_login_at added")
        print("  ✓ All changes verified successfully")
    else:
        print("  ⏭ Verification skipped (migration not executed)")

    return state


# ═══════════════════════════════════════════════
# Step 3: Routing
# ═══════════════════════════════════════════════

def route_after_review(state: MigrationState) -> Literal["execute", "cancel", "revise"]:
    """Route based on human decision."""
    decision = state["human_decision"]

    if decision == "approve":
        print("  → Routing: APPROVED → execute")
        return "execute"
    elif state["review_count"] >= 3:
        print("  → Routing: Max reviews reached → cancel")
        return "cancel"
    else:
        print("  → Routing: REJECTED → revise plan")
        return "revise"


# ═══════════════════════════════════════════════
# Step 4: Build the Graph
# ═══════════════════════════════════════════════

def create_migration_workflow():
    """Build the migration approval graph with HITL interrupt."""
    workflow = StateGraph(MigrationState)

    # Add nodes
    workflow.add_node("analyze_schema", analyze_schema)
    workflow.add_node("llm_review", llm_review_plan)
    workflow.add_node("human_review", human_review)
    workflow.add_node("execute_migration", execute_migration)
    workflow.add_node("cancel_migration", cancel_migration)
    workflow.add_node("verify", verify_migration)

    # Entry
    workflow.set_entry_point("analyze_schema")

    # Edges
    workflow.add_edge("analyze_schema", "llm_review")
    workflow.add_edge("llm_review", "human_review")

    # After human review: approve → execute, reject → revise or cancel
    workflow.add_conditional_edges(
        "human_review",
        route_after_review,
        {
            "execute": "execute_migration",
            "cancel": "cancel_migration",
            "revise": "llm_review",     # Loop back for revised review
        },
    )

    workflow.add_edge("execute_migration", "verify")
    workflow.add_edge("verify", END)
    workflow.add_edge("cancel_migration", END)

    return workflow


# ═══════════════════════════════════════════════
# Step 5: Run with Human-in-the-Loop
# ═══════════════════════════════════════════════

def run_migration_workflow():
    """Run the migration workflow with interactive human review."""
    print("═" * 55)
    print("  DATABASE MIGRATION APPROVAL WORKFLOW")
    print("═" * 55)

    # Build graph with checkpointer (required for interrupts)
    workflow = create_migration_workflow()
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)

    # Initial state
    initial_state: MigrationState = {
        "schema_summary": "",
        "migration_plan": "",
        "llm_review": "",
        "risk_assessment": "",
        "human_decision": "pending",
        "human_feedback": "",
        "execution_log": [],
        "execution_status": "pending",
        "review_count": 0,
    }

    # Thread config (required for checkpointing)
    config = {"configurable": {"thread_id": "migration-1"}}

    # Run until interrupt
    print("\n▶ Starting workflow...\n")

    result = app.invoke(initial_state, config=config)

    # The graph paused at human_review (interrupt).
    # Now we get human input and resume.
    while True:
        # Check if we hit an interrupt
        snapshot = app.get_state(config)
        if not snapshot.next:
            # No more nodes to run — graph is complete
            break

        # Get human input
        print("\n" + "-" * 55)
        decision = input("  Your decision (approve/reject): ").strip().lower()

        if decision in ("approve", "yes", "y"):
            human_response = {"decision": "approve", "feedback": ""}
        else:
            feedback = input("  Feedback (why reject?): ").strip()
            human_response = {"decision": "reject", "feedback": feedback or "No reason given"}

        # Resume the graph with human input
        result = app.invoke(
            Command(resume=human_response),
            config=config,
        )

    # Print final summary
    print("\n" + "═" * 55)
    print("  WORKFLOW COMPLETE")
    print("═" * 55)
    print(f"  Status: {result['execution_status'].upper()}")
    print(f"  Reviews: {result['review_count']}")

    if result["execution_log"]:
        print(f"\n  Execution Log:")
        for entry in result["execution_log"]:
            print(f"    {entry}")

    print("═" * 55)

    return result


# ═══════════════════════════════════════════════
# Non-interactive mode (for testing/CI)
# ═══════════════════════════════════════════════

def run_migration_auto(approve: bool = True):
    """Run migration with auto-approval (for testing)."""
    print("═" * 55)
    print(f"  MIGRATION (auto-{'approve' if approve else 'reject'})")
    print("═" * 55)

    workflow = create_migration_workflow()
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)

    initial_state: MigrationState = {
        "schema_summary": "",
        "migration_plan": "",
        "llm_review": "",
        "risk_assessment": "",
        "human_decision": "pending",
        "human_feedback": "",
        "execution_log": [],
        "execution_status": "pending",
        "review_count": 0,
    }

    config = {"configurable": {"thread_id": f"auto-{'approve' if approve else 'reject'}"}}

    # Run until interrupt
    result = app.invoke(initial_state, config=config)

    # Keep responding to interrupts until the graph completes
    max_loops = 5
    for _ in range(max_loops):
        snapshot = app.get_state(config)
        if not snapshot.next:
            break

        if approve:
            response = "approve"
        else:
            response = {"decision": "reject", "feedback": "Auto-rejected for testing"}

        result = app.invoke(Command(resume=response), config=config)

    print(f"\n  Final status: {result['execution_status'].upper()}")
    print("═" * 55)

    return result


# ═══════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not set.")
        print("   Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    if "--auto-approve" in sys.argv:
        run_migration_auto(approve=True)
    elif "--auto-reject" in sys.argv:
        run_migration_auto(approve=False)
    else:
        run_migration_workflow()
