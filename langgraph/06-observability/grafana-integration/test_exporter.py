"""
Test the LangSmith Prometheus Exporter.

Run this AFTER starting prometheus_exporter.py in another terminal.

Usage:
    python test_exporter.py
"""

import os
import sys
import requests


def test_exporter():
    """Test that the exporter is running and producing metrics."""
    print("\n🧪 Testing LangSmith Prometheus Exporter\n")

    # Check env
    if not os.getenv("LANGCHAIN_API_KEY"):
        print("  ❌ LANGCHAIN_API_KEY not set")
        return False
    print("  ✅ LANGCHAIN_API_KEY is set")

    # Check exporter
    port = int(os.getenv("EXPORTER_PORT", "8001"))
    url = f"http://localhost:{port}/metrics"

    try:
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            print(f"  ❌ Exporter returned status {response.status_code}")
            return False

        print(f"  ✅ Exporter running on port {port}")

        # Check for expected metric names
        text = response.text
        expected = [
            "langsmith_run_cost_usd",
            "langsmith_requests_total",
            "langsmith_latency_seconds",
        ]

        for metric in expected:
            if metric in text:
                print(f"  ✅ Found metric: {metric}")
            else:
                print(f"  ⚠️  Missing: {metric} (OK if no runs yet)")

        # Show sample lines
        lines = [l for l in text.split("\n") if l and not l.startswith("#")]
        if lines:
            print(f"\n  Sample metrics ({len(lines)} total):")
            for line in lines[:10]:
                print(f"    {line}")

        print("\n  ✅ Exporter test passed!")
        return True

    except requests.exceptions.ConnectionError:
        print(f"  ❌ Cannot connect to exporter on port {port}")
        print(f"     Start it first: python prometheus_exporter.py")
        return False

    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_exporter()
    sys.exit(0 if success else 1)
