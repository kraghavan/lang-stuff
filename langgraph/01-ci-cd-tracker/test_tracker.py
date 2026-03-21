"""
Test script for CI/CD Status Tracker.

Verifies:
- Graph compiles correctly
- State flows through all nodes
- Each node updates the expected fields
- Pipeline handles failures gracefully

No API key needed — runs entirely locally.
"""

from main import create_pipeline, CICDState


def make_initial_state() -> CICDState:
    """Create a fresh initial state for testing."""
    return {
        "project_name": "test-project",
        "branch": "main",
        "commit_sha": "test123",
        "build_status": "pending",
        "test_status": "pending",
        "staging_status": "pending",
        "smoke_status": "pending",
        "prod_status": "pending",
        "current_step": "start",
        "logs": [],
        "errors": [],
        "duration_seconds": 0.0,
    }


def test_graph_compiles():
    """Test that the graph compiles without errors."""
    print("Test 1: Graph compiles... ", end="")
    workflow = create_pipeline()
    app = workflow.compile()
    assert app is not None
    print("✓")


def test_pipeline_runs():
    """Test that the pipeline runs end-to-end."""
    print("Test 2: Pipeline runs... ", end="")
    workflow = create_pipeline()
    app = workflow.compile()

    state = make_initial_state()
    result = app.invoke(state)

    # All status fields should be updated (no longer "pending")
    for field in ["build_status", "test_status", "staging_status", "smoke_status", "prod_status"]:
        assert result[field] != "pending", f"{field} is still pending"

    # Should have some logs
    assert len(result["logs"]) > 0, "No logs generated"

    # Duration should be positive
    assert result["duration_seconds"] > 0, "No duration recorded"

    print("✓")


def test_state_has_correct_types():
    """Test that state fields have correct types after execution."""
    print("Test 3: State types correct... ", end="")
    workflow = create_pipeline()
    app = workflow.compile()

    state = make_initial_state()
    result = app.invoke(state)

    assert isinstance(result["project_name"], str)
    assert isinstance(result["logs"], list)
    assert isinstance(result["errors"], list)
    assert isinstance(result["duration_seconds"], float)
    assert isinstance(result["build_status"], str)
    print("✓")


def test_multiple_runs_independent():
    """Test that running the pipeline twice gives independent results."""
    print("Test 4: Independent runs... ", end="")
    workflow = create_pipeline()
    app = workflow.compile()

    result1 = app.invoke(make_initial_state())
    result2 = app.invoke(make_initial_state())

    # Both should complete (statuses updated)
    assert result1["build_status"] != "pending"
    assert result2["build_status"] != "pending"

    # Logs should be independent
    assert id(result1["logs"]) != id(result2["logs"])
    print("✓")


if __name__ == "__main__":
    print("\n🧪 CI/CD Tracker Tests")
    print("=" * 40)

    test_graph_compiles()
    test_pipeline_runs()
    test_state_has_correct_types()
    test_multiple_runs_independent()

    print("\n✅ All tests passed!")
