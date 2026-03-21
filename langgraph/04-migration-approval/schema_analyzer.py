"""
Schema Analyzer — Simulated Database Schema Analysis

Provides schema inspection, migration plan generation, and
execution simulation for the HITL example.

No real database needed — all data is simulated.

Usage:
    from schema_analyzer import SchemaAnalyzer
    analyzer = SchemaAnalyzer()
    schema = analyzer.get_current_schema()
"""

from typing import Dict, List


# ═══════════════════════════════════════════════
# Simulated database schema
# ═══════════════════════════════════════════════

CURRENT_SCHEMA = {
    "tables": {
        "users": {
            "columns": [
                {"name": "id", "type": "SERIAL PRIMARY KEY"},
                {"name": "email", "type": "VARCHAR(255)"},
                {"name": "name", "type": "VARCHAR(255)"},
                {"name": "created_at", "type": "TIMESTAMP"},
                {"name": "updated_at", "type": "TIMESTAMP"},
            ],
            "indexes": ["PRIMARY KEY (id)"],
            "row_count": 2_500_000,
            "size_mb": 1200,
        },
        "orders": {
            "columns": [
                {"name": "id", "type": "SERIAL PRIMARY KEY"},
                {"name": "user_id", "type": "INTEGER"},
                {"name": "total", "type": "DECIMAL(10,2)"},
                {"name": "status", "type": "VARCHAR(50)"},
                {"name": "created_at", "type": "TIMESTAMP"},
            ],
            "indexes": ["PRIMARY KEY (id)"],
            "row_count": 8_000_000,
            "size_mb": 4500,
        },
        "payments": {
            "columns": [
                {"name": "id", "type": "SERIAL PRIMARY KEY"},
                {"name": "order_id", "type": "INTEGER"},
                {"name": "amount", "type": "DECIMAL(10,2)"},
                {"name": "method", "type": "VARCHAR(50)"},
                {"name": "status", "type": "VARCHAR(50)"},
                {"name": "processed_at", "type": "TIMESTAMP"},
            ],
            "indexes": ["PRIMARY KEY (id)"],
            "row_count": 6_000_000,
            "size_mb": 2800,
        },
    },
    "version": "2024.3.1",
    "engine": "PostgreSQL 15.4",
}

REQUESTED_CHANGES = {
    "description": "Add performance indexes and a new audit_log table",
    "changes": [
        {
            "type": "ADD_INDEX",
            "table": "users",
            "column": "email",
            "index_name": "idx_users_email",
            "sql": "CREATE INDEX CONCURRENTLY idx_users_email ON users(email);",
            "risk": "low",
            "estimated_time": "2-5 minutes (concurrent, no lock)",
            "rollback": "DROP INDEX idx_users_email;",
        },
        {
            "type": "ADD_INDEX",
            "table": "orders",
            "column": "user_id",
            "index_name": "idx_orders_user_id",
            "sql": "CREATE INDEX CONCURRENTLY idx_orders_user_id ON orders(user_id);",
            "risk": "low",
            "estimated_time": "5-10 minutes (concurrent, large table)",
            "rollback": "DROP INDEX idx_orders_user_id;",
        },
        {
            "type": "ADD_INDEX",
            "table": "orders",
            "column": "status",
            "index_name": "idx_orders_status",
            "sql": "CREATE INDEX CONCURRENTLY idx_orders_status ON orders(status);",
            "risk": "low",
            "estimated_time": "5-10 minutes (concurrent, large table)",
            "rollback": "DROP INDEX idx_orders_status;",
        },
        {
            "type": "CREATE_TABLE",
            "table": "audit_log",
            "sql": (
                "CREATE TABLE audit_log (\n"
                "  id BIGSERIAL PRIMARY KEY,\n"
                "  table_name VARCHAR(100) NOT NULL,\n"
                "  record_id INTEGER NOT NULL,\n"
                "  action VARCHAR(20) NOT NULL,\n"
                "  changed_by INTEGER REFERENCES users(id),\n"
                "  changed_at TIMESTAMP DEFAULT NOW(),\n"
                "  old_values JSONB,\n"
                "  new_values JSONB\n"
                ");"
            ),
            "risk": "low",
            "estimated_time": "< 1 second (empty table)",
            "rollback": "DROP TABLE audit_log;",
        },
        {
            "type": "ADD_COLUMN",
            "table": "users",
            "column": "last_login_at",
            "sql": "ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP;",
            "risk": "medium",
            "estimated_time": "1-2 minutes (nullable column, no rewrite on PG12+)",
            "rollback": "ALTER TABLE users DROP COLUMN last_login_at;",
        },
    ],
}


class SchemaAnalyzer:
    """Analyzes database schema and generates migration plans."""

    def get_current_schema(self) -> Dict:
        """Get the current database schema."""
        return CURRENT_SCHEMA

    def get_requested_changes(self) -> Dict:
        """Get the requested migration changes."""
        return REQUESTED_CHANGES

    def format_schema_summary(self) -> str:
        """Format schema into a readable summary."""
        lines = [f"Database: {CURRENT_SCHEMA['engine']} (v{CURRENT_SCHEMA['version']})\n"]
        for table_name, info in CURRENT_SCHEMA["tables"].items():
            cols = ", ".join(c["name"] for c in info["columns"])
            lines.append(f"  {table_name} ({info['row_count']:,} rows, {info['size_mb']}MB)")
            lines.append(f"    Columns: {cols}")
            lines.append(f"    Indexes: {', '.join(info['indexes'])}")
        return "\n".join(lines)

    def format_migration_plan(self) -> str:
        """Format migration changes into a readable plan."""
        changes = REQUESTED_CHANGES["changes"]
        lines = [f"Migration: {REQUESTED_CHANGES['description']}", f"Steps: {len(changes)}\n"]

        for i, change in enumerate(changes, 1):
            lines.append(f"  Step {i}: {change['type']} — {change.get('table', '')}.{change.get('column', change.get('table', ''))}")
            lines.append(f"    SQL: {change['sql'].split(chr(10))[0]}...")
            lines.append(f"    Risk: {change['risk']} | Time: {change['estimated_time']}")
            lines.append(f"    Rollback: {change['rollback']}")
            lines.append("")

        return "\n".join(lines)

    def simulate_execution(self, step_index: int) -> Dict:
        """Simulate executing a migration step."""
        changes = REQUESTED_CHANGES["changes"]
        if step_index >= len(changes):
            return {"success": False, "error": f"Invalid step index: {step_index}"}

        change = changes[step_index]
        return {
            "success": True,
            "step": step_index + 1,
            "type": change["type"],
            "sql": change["sql"],
            "result": f"✓ {change['type']} completed: {change.get('index_name', change.get('table', ''))}",
        }


if __name__ == "__main__":
    print("🗄️ Testing Schema Analyzer\n")
    analyzer = SchemaAnalyzer()

    print("--- Current Schema ---")
    print(analyzer.format_schema_summary())

    print("\n--- Migration Plan ---")
    print(analyzer.format_migration_plan())

    print("--- Simulate Step 1 ---")
    result = analyzer.simulate_execution(0)
    print(f"  {result['result']}")

    print("\n✅ Schema analyzer working!")
