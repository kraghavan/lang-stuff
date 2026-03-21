"""
LangSmith Connection Test

Verifies that LangSmith is configured correctly before you
start tracing your LangGraph workflows.

Checks:
1. LANGCHAIN_API_KEY is set
2. LANGCHAIN_TRACING_V2 is enabled
3. API connection works

Usage:
    python test_connection.py

Requires:
    - LANGCHAIN_API_KEY (get from https://smith.langchain.com)
    - LANGCHAIN_TRACING_V2=true
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def test_langsmith_connection() -> bool:
    """Verify LangSmith configuration."""
    print("\n🔍 Testing LangSmith Connection...\n")

    api_key = os.getenv("LANGCHAIN_API_KEY")
    tracing = os.getenv("LANGCHAIN_TRACING_V2")
    project = os.getenv("LANGCHAIN_PROJECT", "default")

    issues = []

    # Check API key
    if not api_key:
        issues.append("LANGCHAIN_API_KEY not set")
        print("  ❌ LANGCHAIN_API_KEY not set")
        print("     Get key from: https://smith.langchain.com/settings")
        print("     Then: export LANGCHAIN_API_KEY='lsv2_pt_...'")
    else:
        masked = api_key[:8] + "..." + api_key[-4:]
        print(f"  ✅ LANGCHAIN_API_KEY is set ({masked})")

    # Check tracing enabled
    if tracing != "true":
        issues.append("LANGCHAIN_TRACING_V2 not enabled")
        print("  ⚠️  LANGCHAIN_TRACING_V2 not set to 'true'")
        print("     Run: export LANGCHAIN_TRACING_V2=true")
    else:
        print("  ✅ LANGCHAIN_TRACING_V2 is enabled")

    print(f"  ✅ Project: '{project}'")

    # If missing key, can't test API
    if not api_key:
        print(f"\n  ❌ Setup incomplete. Fix {len(issues)} issue(s) above.")
        return False

    # Test API connection
    try:
        from langsmith import Client

        client = Client()
        projects = list(client.list_projects(limit=1))
        print("  ✅ LangSmith API connection successful!")
        print(f"\n  🎉 Ready to trace your LangGraph workflows!")
        return True

    except ImportError:
        print("  ❌ langsmith package not installed")
        print("     Run: pip install langsmith")
        return False

    except Exception as e:
        print(f"  ❌ LangSmith API connection failed: {e}")
        print("     Check your API key is correct")
        return False


if __name__ == "__main__":
    success = test_langsmith_connection()
    sys.exit(0 if success else 1)
