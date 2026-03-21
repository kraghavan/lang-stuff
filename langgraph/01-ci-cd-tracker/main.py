"""
CI/CD Status Tracker — LangGraph Beginner Example

A deployment pipeline tracker that demonstrates basic LangGraph state management.
No LLM needed — this is pure state + nodes + edges to learn the fundamentals.

Architecture:
    START → build → test → deploy_staging → smoke_test → deploy_prod → END

Key Concepts:
    - TypedDict state definition
    - Node functions that modify state
    - Linear edges (no conditionals)
    - Entry point and END
    - How state flows through a graph

Usage:
    python main.py

No API key required — this example runs entirely locally.
"""

import time
import random
from typing import TypedDict, List
from langgraph.graph import StateGraph, END


# ═══════════════════════════════════════════════
# Step 1: Define State
#
# State is a TypedDict — a shared data structure that flows
# through every node in the graph. Each node can read and
# modify any field.
#
# Think of it as a "deployment ticket" that gets updated
# at each stage of the pipeline.
# ═══════════════════════════════════════════════

class CICDState(TypedDict):
    """Shared state for the CI/CD pipeline."""
    # Pipeline metadata
    project_name: str
    branch: str
    commit_sha: str

    # Status tracking (updated at each stage)
    build_status: str       # "pending" | "success" | "failed"
    test_status: str        # "pending" | "success" | "failed"
    staging_status: str     # "pending" | "success" | "failed"
    smoke_status: str       # "pending" | "success" | "failed"
    prod_status: str        # "pending" | "success" | "failed"

    # Current pipeline state
    current_step: str
    logs: List[str]
    errors: List[str]
    duration_seconds: float


# ═══════════════════════════════════════════════
# Step 2: Define Nodes
#
# Each node is a function that:
#   1. Receives the current state
#   2. Does some work (simulated here)
#   3. Updates state fields
#   4. Returns the modified state
#
# Nodes are pure functions — they only interact
# with the outside world through state.
# ═══════════════════════════════════════════════

def run_build(state: CICDState) -> CICDState:
    """Node 1: Compile and build the project."""
    print(f"\n🔨 Building {state['project_name']}...")
    state["current_step"] = "build"

    # Simulate build time
    build_time = round(random.uniform(1.0, 3.0), 1)
    time.sleep(0.3)  # Brief pause for realism

    # Simulate build result (95% success rate)
    if random.random() < 0.95:
        state["build_status"] = "success"
        state["logs"].append(f"Build completed in {build_time}s")
        print(f"  ✓ Build succeeded ({build_time}s)")
    else:
        state["build_status"] = "failed"
        state["errors"].append("Compilation error in src/main.py:42")
        state["logs"].append(f"Build FAILED after {build_time}s")
        print(f"  ✗ Build failed ({build_time}s)")

    state["duration_seconds"] += build_time
    return state


def run_tests(state: CICDState) -> CICDState:
    """Node 2: Run the test suite."""
    print(f"\n🧪 Running tests...")
    state["current_step"] = "test"

    # Skip if build failed
    if state["build_status"] != "success":
        state["test_status"] = "skipped"
        state["logs"].append("Tests skipped: build failed")
        print("  ⏭ Tests skipped (build failed)")
        return state

    # Simulate test execution
    total_tests = random.randint(45, 120)
    test_time = round(random.uniform(3.0, 8.0), 1)
    time.sleep(0.3)

    # 90% pass rate
    if random.random() < 0.90:
        state["test_status"] = "success"
        state["logs"].append(f"{total_tests}/{total_tests} tests passed in {test_time}s")
        print(f"  ✓ {total_tests}/{total_tests} tests passed ({test_time}s)")
    else:
        failed = random.randint(1, 5)
        state["test_status"] = "failed"
        state["errors"].append(f"{failed} test(s) failed: test_auth, test_payments")
        state["logs"].append(f"{total_tests - failed}/{total_tests} tests passed, {failed} failed")
        print(f"  ✗ {failed}/{total_tests} tests failed ({test_time}s)")

    state["duration_seconds"] += test_time
    return state


def deploy_staging(state: CICDState) -> CICDState:
    """Node 3: Deploy to the staging environment."""
    print(f"\n🚀 Deploying to staging...")
    state["current_step"] = "deploy_staging"

    # Skip if tests failed
    if state["test_status"] != "success":
        state["staging_status"] = "skipped"
        state["logs"].append("Staging deploy skipped: tests failed")
        print("  ⏭ Staging skipped (tests failed)")
        return state

    deploy_time = round(random.uniform(5.0, 15.0), 1)
    time.sleep(0.3)

    # 98% success rate for staging
    if random.random() < 0.98:
        state["staging_status"] = "success"
        state["logs"].append(f"Deployed to staging in {deploy_time}s")
        print(f"  ✓ Deployed to staging ({deploy_time}s)")
    else:
        state["staging_status"] = "failed"
        state["errors"].append("Staging deploy failed: health check timeout")
        state["logs"].append(f"Staging deploy FAILED after {deploy_time}s")
        print(f"  ✗ Staging deploy failed ({deploy_time}s)")

    state["duration_seconds"] += deploy_time
    return state


def run_smoke_tests(state: CICDState) -> CICDState:
    """Node 4: Run smoke tests against the staging environment."""
    print(f"\n🔥 Running smoke tests on staging...")
    state["current_step"] = "smoke_test"

    if state["staging_status"] != "success":
        state["smoke_status"] = "skipped"
        state["logs"].append("Smoke tests skipped: staging deploy failed")
        print("  ⏭ Smoke tests skipped (staging not deployed)")
        return state

    smoke_time = round(random.uniform(2.0, 5.0), 1)
    time.sleep(0.3)

    endpoints_checked = random.randint(5, 12)

    if random.random() < 0.92:
        state["smoke_status"] = "success"
        state["logs"].append(f"Smoke tests passed: {endpoints_checked} endpoints OK ({smoke_time}s)")
        print(f"  ✓ {endpoints_checked} endpoints healthy ({smoke_time}s)")
    else:
        state["smoke_status"] = "failed"
        state["errors"].append("Smoke test failed: /api/health returned 503")
        state["logs"].append(f"Smoke tests FAILED ({smoke_time}s)")
        print(f"  ✗ Smoke tests failed ({smoke_time}s)")

    state["duration_seconds"] += smoke_time
    return state


def deploy_prod(state: CICDState) -> CICDState:
    """Node 5: Deploy to production."""
    print(f"\n🌐 Deploying to production...")
    state["current_step"] = "deploy_prod"

    if state["smoke_status"] != "success":
        state["prod_status"] = "skipped"
        state["logs"].append("Prod deploy skipped: smoke tests failed")
        print("  ⏭ Prod deploy skipped (smoke tests failed)")
        return state

    deploy_time = round(random.uniform(10.0, 25.0), 1)
    time.sleep(0.3)

    if random.random() < 0.99:
        state["prod_status"] = "success"
        state["logs"].append(f"Deployed to production in {deploy_time}s")
        print(f"  ✓ Deployed to production ({deploy_time}s)")
    else:
        state["prod_status"] = "failed"
        state["errors"].append("Prod deploy failed: rolling update timeout")
        state["logs"].append(f"Prod deploy FAILED after {deploy_time}s")
        print(f"  ✗ Prod deploy failed ({deploy_time}s)")

    state["duration_seconds"] += deploy_time
    return state


# ═══════════════════════════════════════════════
# Step 3: Build the Graph
#
# StateGraph is the core LangGraph class. You:
#   1. Create it with your state type
#   2. Add nodes (name → function)
#   3. Add edges (from → to)
#   4. Set the entry point
#   5. Compile into a runnable app
#
# This graph is LINEAR — no conditionals.
# Every run follows the same path:
#   build → test → staging → smoke → prod
# ═══════════════════════════════════════════════

def create_pipeline() -> StateGraph:
    """Build the CI/CD pipeline graph."""
    workflow = StateGraph(CICDState)

    # Add nodes
    workflow.add_node("build", run_build)
    workflow.add_node("test", run_tests)
    workflow.add_node("deploy_staging", deploy_staging)
    workflow.add_node("smoke_test", run_smoke_tests)
    workflow.add_node("deploy_prod", deploy_prod)

    # Set entry point
    workflow.set_entry_point("build")

    # Add linear edges: each step leads to the next
    workflow.add_edge("build", "test")
    workflow.add_edge("test", "deploy_staging")
    workflow.add_edge("deploy_staging", "smoke_test")
    workflow.add_edge("smoke_test", "deploy_prod")
    workflow.add_edge("deploy_prod", END)

    return workflow


# ═══════════════════════════════════════════════
# Step 4: Run the Pipeline
# ═══════════════════════════════════════════════

def run_pipeline(project_name: str = "my-api", branch: str = "main", commit_sha: str = "abc123f"):
    """
    Run the full CI/CD pipeline.

    Args:
        project_name: Name of the project
        branch: Git branch being deployed
        commit_sha: Short commit hash
    """
    print("═" * 55)
    print("  CI/CD PIPELINE")
    print("═" * 55)
    print(f"  Project:  {project_name}")
    print(f"  Branch:   {branch}")
    print(f"  Commit:   {commit_sha}")
    print("═" * 55)

    # Build and compile the graph
    workflow = create_pipeline()
    app = workflow.compile()

    # Create initial state
    initial_state: CICDState = {
        "project_name": project_name,
        "branch": branch,
        "commit_sha": commit_sha,
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

    # Run the graph
    final_state = app.invoke(initial_state)

    # Print summary
    print("\n" + "═" * 55)
    print("  PIPELINE SUMMARY")
    print("═" * 55)

    stages = [
        ("Build", final_state["build_status"]),
        ("Tests", final_state["test_status"]),
        ("Staging", final_state["staging_status"]),
        ("Smoke Tests", final_state["smoke_status"]),
        ("Production", final_state["prod_status"]),
    ]

    all_success = True
    for name, status in stages:
        icon = "✓" if status == "success" else "✗" if status == "failed" else "⏭"
        print(f"  {icon} {name:15s} {status}")
        if status != "success":
            all_success = False

    print(f"\n  Total Duration: {final_state['duration_seconds']:.1f}s")

    if final_state["errors"]:
        print(f"\n  Errors ({len(final_state['errors'])}):")
        for err in final_state["errors"]:
            print(f"    ✗ {err}")

    if all_success:
        print(f"\n  🎉 Pipeline SUCCEEDED — {project_name}@{commit_sha} is live!")
    else:
        print(f"\n  ❌ Pipeline FAILED — check errors above")

    print("═" * 55)
    return final_state


# ═══════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    # Run the pipeline (no API key needed!)
    run_pipeline(
        project_name="payments-api",
        branch="main",
        commit_sha="a1b2c3d"
    )
