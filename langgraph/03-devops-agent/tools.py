"""
DevOps Troubleshooting Tools — Simulated Infrastructure Tools

These simulate real DevOps tools (logs, databases, endpoints) so the
ReAct agent can investigate issues without needing actual infrastructure.

Each tool is decorated with @tool — this makes it callable by the LLM.
The LLM reads the docstring to decide WHEN to use each tool.

Usage:
    from tools import devops_tools
    # Pass to agent: llm.bind_tools(devops_tools)
"""

from langchain_core.tools import tool


# ═══════════════════════════════════════════════
# Simulated infrastructure state
# (In production, these would call real APIs)
# ═══════════════════════════════════════════════

_SIMULATED_LOGS = {
    "api-gateway": [
        "[ERROR] 2026-03-20 10:15:23 - Request timeout after 30s on /api/v2/users",
        "[WARN]  2026-03-20 10:15:20 - Upstream response time 28.5s from user-service",
        "[ERROR] 2026-03-20 10:14:55 - Request timeout after 30s on /api/v2/users/123",
        "[INFO]  2026-03-20 10:14:00 - Health check OK",
        "[WARN]  2026-03-20 10:13:45 - Connection pool exhausted, waiting for free connection",
    ],
    "user-service": [
        "[ERROR] 2026-03-20 10:15:22 - DB query took 25.3s: SELECT * FROM users WHERE id = ?",
        "[WARN]  2026-03-20 10:15:20 - Slow query detected: full table scan on users table",
        "[ERROR] 2026-03-20 10:14:50 - DB query took 28.1s: SELECT * FROM users JOIN orders ON ...",
        "[INFO]  2026-03-20 10:14:00 - Connected to postgres-primary:5432",
        "[WARN]  2026-03-20 10:13:30 - Query cache miss rate: 89%",
    ],
    "payment-service": [
        "[INFO]  2026-03-20 10:15:00 - Payment processed: $49.99 (txn_abc123)",
        "[INFO]  2026-03-20 10:14:30 - Health check OK",
        "[INFO]  2026-03-20 10:14:00 - Stripe webhook received",
    ],
    "auth-service": [
        "[INFO]  2026-03-20 10:15:10 - Token validated for user_456",
        "[INFO]  2026-03-20 10:14:45 - Login successful: user_789",
        "[INFO]  2026-03-20 10:14:00 - Health check OK",
    ],
}

_SIMULATED_METRICS = {
    "cpu": {"api-gateway": "45%", "user-service": "78%", "payment-service": "12%", "database": "92%"},
    "memory": {"api-gateway": "60%", "user-service": "55%", "payment-service": "30%", "database": "85%"},
    "disk": {"api-gateway": "20%", "user-service": "25%", "payment-service": "15%", "database": "88%"},
    "connections": {"database": "148/150 active connections"},
}

_SIMULATED_DB = {
    "slow_queries": [
        {"query": "SELECT * FROM users WHERE id = 123", "avg_time_ms": 25300, "calls_last_hour": 450},
        {"query": "SELECT * FROM users JOIN orders ON users.id = orders.user_id", "avg_time_ms": 28100, "calls_last_hour": 120},
    ],
    "missing_indexes": [
        {"table": "users", "column": "email", "recommendation": "CREATE INDEX idx_users_email ON users(email)"},
        {"table": "orders", "column": "user_id", "recommendation": "CREATE INDEX idx_orders_user_id ON orders(user_id)"},
    ],
    "table_stats": {
        "users": {"rows": 2_500_000, "size_mb": 1200, "last_vacuum": "2026-03-15", "dead_tuples": 450_000},
        "orders": {"rows": 8_000_000, "size_mb": 4500, "last_vacuum": "2026-03-10", "dead_tuples": 1_200_000},
    },
}

_SIMULATED_ENDPOINTS = {
    "https://api.example.com/health": {"status": 200, "response_time_ms": 45, "body": '{"status": "ok"}'},
    "https://api.example.com/api/v2/users": {"status": 504, "response_time_ms": 30000, "body": '{"error": "gateway timeout"}'},
    "https://api.example.com/api/v2/users/123": {"status": 504, "response_time_ms": 30000, "body": '{"error": "gateway timeout"}'},
    "https://api.example.com/api/v2/payments": {"status": 200, "response_time_ms": 120, "body": '{"status": "ok"}'},
}


# ═══════════════════════════════════════════════
# Tool Definitions
#
# Each @tool function:
# - Has a descriptive docstring (the LLM reads this!)
# - Takes typed parameters
# - Returns a string result
# - Simulates real infrastructure behavior
# ═══════════════════════════════════════════════

@tool
def check_logs(service: str, lines: int = 5) -> str:
    """Check recent logs for a service. Use this to find errors, warnings, and patterns.

    Args:
        service: Service name (e.g., 'api-gateway', 'user-service', 'payment-service', 'auth-service')
        lines: Number of recent log lines to return (default: 5)
    """
    service = service.lower().strip()
    if service not in _SIMULATED_LOGS:
        available = ", ".join(_SIMULATED_LOGS.keys())
        return f"Service '{service}' not found. Available services: {available}"

    logs = _SIMULATED_LOGS[service][:lines]
    return f"Last {len(logs)} log entries for {service}:\n" + "\n".join(logs)


@tool
def check_metrics(metric_type: str) -> str:
    """Check infrastructure metrics (CPU, memory, disk, connections).

    Args:
        metric_type: Type of metric - 'cpu', 'memory', 'disk', or 'connections'
    """
    metric_type = metric_type.lower().strip()
    if metric_type not in _SIMULATED_METRICS:
        return f"Unknown metric type '{metric_type}'. Available: cpu, memory, disk, connections"

    data = _SIMULATED_METRICS[metric_type]
    lines = [f"  {svc}: {val}" for svc, val in data.items()]
    return f"{metric_type.upper()} metrics:\n" + "\n".join(lines)


@tool
def query_database(check_type: str) -> str:
    """Query database for performance issues. Use this when logs suggest DB problems.

    Args:
        check_type: What to check - 'slow_queries', 'missing_indexes', or 'table_stats'
    """
    check_type = check_type.lower().strip()
    if check_type not in _SIMULATED_DB:
        return f"Unknown check type '{check_type}'. Available: slow_queries, missing_indexes, table_stats"

    data = _SIMULATED_DB[check_type]

    if check_type == "slow_queries":
        lines = []
        for q in data:
            lines.append(f"  Query: {q['query']}")
            lines.append(f"  Avg time: {q['avg_time_ms']}ms | Calls/hour: {q['calls_last_hour']}")
            lines.append("")
        return "Slow queries (last hour):\n" + "\n".join(lines)

    elif check_type == "missing_indexes":
        lines = []
        for idx in data:
            lines.append(f"  Table: {idx['table']}.{idx['column']}")
            lines.append(f"  Fix: {idx['recommendation']}")
            lines.append("")
        return "Missing indexes detected:\n" + "\n".join(lines)

    else:  # table_stats
        lines = []
        for table, stats in data.items():
            lines.append(f"  {table}: {stats['rows']:,} rows, {stats['size_mb']}MB, "
                         f"dead_tuples={stats['dead_tuples']:,}, last_vacuum={stats['last_vacuum']}")
        return "Table statistics:\n" + "\n".join(lines)


@tool
def test_endpoint(url: str) -> str:
    """Test an API endpoint and check its response. Use this to verify if endpoints are working.

    Args:
        url: The URL to test (e.g., 'https://api.example.com/health')
    """
    url = url.strip()
    if url not in _SIMULATED_ENDPOINTS:
        available = ", ".join(_SIMULATED_ENDPOINTS.keys())
        return f"Unknown endpoint '{url}'. Available: {available}"

    ep = _SIMULATED_ENDPOINTS[url]
    status_text = "OK" if ep["status"] == 200 else "ERROR"
    return (
        f"Endpoint: {url}\n"
        f"  Status: {ep['status']} ({status_text})\n"
        f"  Response time: {ep['response_time_ms']}ms\n"
        f"  Body: {ep['body']}"
    )


@tool
def run_remediation(action: str) -> str:
    """Execute a remediation action. Use this ONLY after you've identified the root cause.

    Args:
        action: The remediation to run. Options:
            - 'create_index users email' — Create missing index
            - 'create_index orders user_id' — Create missing index
            - 'vacuum users' — Run VACUUM on users table
            - 'vacuum orders' — Run VACUUM on orders table
            - 'restart user-service' — Restart the user service
            - 'scale user-service' — Scale up user service replicas
    """
    action = action.strip().lower()

    remediations = {
        "create_index users email": "✓ Index idx_users_email created on users(email). Expected query improvement: 10-50x.",
        "create_index orders user_id": "✓ Index idx_orders_user_id created on orders(user_id). Expected query improvement: 5-20x.",
        "vacuum users": "✓ VACUUM ANALYZE completed on users table. Reclaimed 450,000 dead tuples.",
        "vacuum orders": "✓ VACUUM ANALYZE completed on orders table. Reclaimed 1,200,000 dead tuples.",
        "restart user-service": "✓ user-service restarted. 3 pods rolling restart in progress.",
        "scale user-service": "✓ user-service scaled from 3 to 5 replicas.",
    }

    if action in remediations:
        return remediations[action]

    available = "\n  ".join(remediations.keys())
    return f"Unknown action '{action}'. Available actions:\n  {available}"


# Collect all tools for the agent
devops_tools = [check_logs, check_metrics, query_database, test_endpoint, run_remediation]


# ═══════════════════════════════════════════════
# Test
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    print("🛠️ Testing DevOps Tools\n")

    print("--- check_logs ---")
    print(check_logs.invoke({"service": "api-gateway", "lines": 3}))

    print("\n--- check_metrics ---")
    print(check_metrics.invoke({"metric_type": "cpu"}))

    print("\n--- query_database ---")
    print(query_database.invoke({"check_type": "slow_queries"}))

    print("\n--- test_endpoint ---")
    print(test_endpoint.invoke({"url": "https://api.example.com/api/v2/users"}))

    print("\n--- run_remediation ---")
    print(run_remediation.invoke({"action": "create_index users email"}))

    print("\n✅ All tools working!")
