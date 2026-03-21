"""
Test script for Database Migration Approval.

Tests schema analyzer, graph compilation, and auto-approve/reject flows.
Full interactive test requires ANTHROPIC_API_KEY.
"""

import os
from schema_analyzer import SchemaAnalyzer


def test_schema_analyzer():
    """Test the schema analyzer."""
    print("Test 1: Schema analyzer... ", end="")
    analyzer = SchemaAnalyzer()

    schema = analyzer.get_current_schema()
    assert "tables" in schema
    assert "users" in schema["tables"]
    assert len(schema["tables"]) == 3

    summary = analyzer.format_schema_summary()
    assert "PostgreSQL" in summary
    assert "users" in summary

    plan = analyzer.format_migration_plan()
    assert "ADD_INDEX" in plan or "index" in plan.lower()

    print("✓")


def test_migration_plan():
    """Test migration plan details."""
    print("Test 2: Migration plan... ", end="")
    analyzer = SchemaAnalyzer()

    changes = analyzer.get_requested_changes()
    assert len(changes["changes"]) == 5

    # Each change should have required fields
    for change in changes["changes"]:
        assert "type" in change
        assert "sql" in change
        assert "risk" in change
        assert "rollback" in change

    print("✓")


def test_simulate_execution():
    """Test migration step simulation."""
    print("Test 3: Simulate execution... ", end="")
    analyzer = SchemaAnalyzer()

    result = analyzer.simulate_execution(0)
    assert result["success"] is True
    assert "step" in result

    # Invalid step
    result = analyzer.simulate_execution(99)
    assert result["success"] is False

    print("✓")


def test_graph_compiles():
    """Test that the HITL graph compiles."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Test 4: Graph compiles... ⏭ (no API key)")
        return

    print("Test 4: Graph compiles... ", end="")
    from main import create_migration_workflow
    from langgraph.checkpoint.memory import MemorySaver

    workflow = create_migration_workflow()
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)
    assert app is not None
    print("✓")


def test_auto_approve():
    """Test the auto-approve flow end-to-end."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Test 5: Auto-approve flow... ⏭ (no API key)")
        return

    print("Test 5: Auto-approve flow... ", end="")
    from main import run_migration_auto

    result = run_migration_auto(approve=True)
    assert result["execution_status"] == "complete"
    assert result["human_decision"] == "approve"
    assert len(result["execution_log"]) > 0
    print("✓")


def test_auto_reject():
    """Test the auto-reject flow end-to-end."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Test 6: Auto-reject flow... ⏭ (no API key)")
        return

    print("Test 6: Auto-reject flow... ", end="")
    from main import run_migration_auto

    result = run_migration_auto(approve=False)
    assert result["execution_status"] == "cancelled"
    assert result["human_decision"] == "reject"
    print("✓")


if __name__ == "__main__":
    print("\n🧪 Migration Approval Tests")
    print("=" * 40)

    test_schema_analyzer()
    test_migration_plan()
    test_simulate_execution()
    test_graph_compiles()
    test_auto_approve()
    test_auto_reject()

    print("\n✅ All tests passed!")
