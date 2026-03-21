"""
Test script for DevOps Troubleshooting Agent.

Tests tools work correctly and agent compiles.
Full agent test requires ANTHROPIC_API_KEY.
"""

import os
from tools import (
    check_logs, check_metrics, query_database,
    test_endpoint, run_remediation, devops_tools,
)


def test_check_logs():
    """Test log checking tool."""
    print("Test 1: check_logs... ", end="")
    result = check_logs.invoke({"service": "api-gateway", "lines": 3})
    assert "api-gateway" in result
    assert "ERROR" in result or "WARN" in result or "INFO" in result

    # Test invalid service
    result = check_logs.invoke({"service": "nonexistent"})
    assert "not found" in result.lower()
    print("✓")


def test_check_metrics():
    """Test metrics tool."""
    print("Test 2: check_metrics... ", end="")
    result = check_metrics.invoke({"metric_type": "cpu"})
    assert "CPU" in result
    assert "api-gateway" in result

    result = check_metrics.invoke({"metric_type": "connections"})
    assert "connections" in result.lower() or "database" in result
    print("✓")


def test_query_database():
    """Test database query tool."""
    print("Test 3: query_database... ", end="")
    result = query_database.invoke({"check_type": "slow_queries"})
    assert "slow" in result.lower() or "query" in result.lower()

    result = query_database.invoke({"check_type": "missing_indexes"})
    assert "index" in result.lower()

    result = query_database.invoke({"check_type": "table_stats"})
    assert "users" in result
    print("✓")


def test_endpoint_tool():
    """Test endpoint testing tool."""
    print("Test 4: test_endpoint... ", end="")
    result = test_endpoint.invoke({"url": "https://api.example.com/health"})
    assert "200" in result

    result = test_endpoint.invoke({"url": "https://api.example.com/api/v2/users"})
    assert "504" in result or "timeout" in result.lower()
    print("✓")


def test_remediation():
    """Test remediation tool."""
    print("Test 5: run_remediation... ", end="")
    result = run_remediation.invoke({"action": "create_index users email"})
    assert "idx_users_email" in result

    result = run_remediation.invoke({"action": "unknown_action"})
    assert "unknown" in result.lower() or "available" in result.lower()
    print("✓")


def test_tools_collection():
    """Test that all tools are collected."""
    print("Test 6: Tools collection... ", end="")
    assert len(devops_tools) == 5
    names = [t.name for t in devops_tools]
    assert "check_logs" in names
    assert "check_metrics" in names
    assert "query_database" in names
    assert "test_endpoint" in names
    assert "run_remediation" in names
    print("✓")


def test_agent_compiles():
    """Test that the agent graph compiles (requires API key)."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Test 7: Agent compiles... ⏭ (no API key)")
        return

    print("Test 7: Agent compiles... ", end="")
    from main import create_devops_agent
    agent = create_devops_agent()
    assert agent is not None
    print("✓")


if __name__ == "__main__":
    print("\n🧪 DevOps Agent Tests")
    print("=" * 40)

    test_check_logs()
    test_check_metrics()
    test_query_database()
    test_endpoint_tool()
    test_remediation()
    test_tools_collection()
    test_agent_compiles()

    print("\n✅ All tests passed!")
