#!/bin/bash
#
# Smoke Test Runner for LangGraph Examples
#
# Usage:
#   cd langgraph/
#   ./smoke_test.sh           # Run all tests
#   ./smoke_test.sh 01        # Run only example 01
#   ./smoke_test.sh 01 03     # Run examples 01 and 03
#
# Examples 01-02 tests run fully offline.
# Examples 03-04 tool/schema tests run offline; agent tests need ANTHROPIC_API_KEY.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SCRIPT_DIR/venv/bin/activate"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m'

PASSED=0
FAILED=0
FAILURES=()

print_header() {
    echo ""
    echo -e "${BOLD}═══════════════════════════════════════════════${NC}"
    echo -e "${BOLD}  $1${NC}"
    echo -e "${BOLD}═══════════════════════════════════════════════${NC}"
}

run_test() {
    local name="$1"
    local dir="$2"
    local cmd="$3"
    local timeout_secs="${4:-120}"

    echo -ne "  ${name}... "

    local output exit_code
    output=$(cd "$SCRIPT_DIR/$dir" && source "$VENV" && perl -e "alarm $timeout_secs; exec @ARGV" bash -c "$cmd" 2>&1) || exit_code=$?
    exit_code=${exit_code:-0}

    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ FAILED${NC} (exit code $exit_code)"
        FAILURES+=("$name")
        FAILED=$((FAILED + 1))
        echo -e "${YELLOW}    Last 10 lines:${NC}"
        echo "$output" | tail -10 | sed 's/^/    /'
    fi
}

should_run() {
    local num="$1"
    if [ ${#FILTER[@]} -eq 0 ]; then return 0; fi
    for f in "${FILTER[@]}"; do
        if [[ "$num" == "$f" ]]; then return 0; fi
    done
    return 1
}

# ═══════════════════════════════════════════════
# Pre-flight
# ═══════════════════════════════════════════════

print_header "LangGraph Smoke Tests"

FILTER=("$@")
if [ ${#FILTER[@]} -gt 0 ]; then
    echo -e "  Running: examples ${FILTER[*]}"
else
    echo -e "  Running: all examples"
fi

if [ ! -f "$VENV" ]; then
    echo -e "\n${RED}❌ venv not found at $SCRIPT_DIR/venv${NC}"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} venv found"

HAS_API_KEY=false
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    HAS_API_KEY=true
    echo -e "  ${GREEN}✓${NC} ANTHROPIC_API_KEY set"
else
    echo -e "  ${YELLOW}⚠${NC} ANTHROPIC_API_KEY not set (LLM tests will be skipped)"
fi

# ═══════════════════════════════════════════════
# 01: CI/CD Tracker (no API key needed)
# ═══════════════════════════════════════════════

if should_run "01"; then
    print_header "01 — CI/CD Tracker"

    run_test "test_tracker.py" "01-ci-cd-tracker" "python test_tracker.py" 30
fi

# ═══════════════════════════════════════════════
# 02: Fraud Detection (no API key for --no-llm)
# ═══════════════════════════════════════════════

if should_run "02"; then
    print_header "02 — Fraud Detection"

    run_test "test_fraud.py" "02-fraud-detection" "python test_fraud.py" 30
    run_test "main.py --no-llm" "02-fraud-detection" "python main.py --no-llm" 30
fi

# ═══════════════════════════════════════════════
# 03: DevOps Agent
# ═══════════════════════════════════════════════

if should_run "03"; then
    print_header "03 — DevOps Agent"

    run_test "test_agent.py (tools)" "03-devops-agent" "python test_agent.py" 30

    if [ "$HAS_API_KEY" = true ]; then
        run_test "main.py (full agent)" "03-devops-agent" "python main.py" 120
    else
        echo -e "  main.py (full agent)... ${YELLOW}⏭ SKIPPED (no API key)${NC}"
    fi
fi

# ═══════════════════════════════════════════════
# 04: Migration Approval
# ═══════════════════════════════════════════════

if should_run "04"; then
    print_header "04 — Migration Approval"

    run_test "schema_analyzer.py" "04-migration-approval" "python schema_analyzer.py" 10

    if [ "$HAS_API_KEY" = true ]; then
        run_test "main.py --auto-approve" "04-migration-approval" "python main.py --auto-approve" 120
        run_test "main.py --auto-reject" "04-migration-approval" "python main.py --auto-reject" 180
    else
        echo -e "  main.py (HITL flows)... ${YELLOW}⏭ SKIPPED (no API key)${NC}"
    fi
fi

# ═══════════════════════════════════════════════
# 05: Trading Team
# ═══════════════════════════════════════════════

if should_run "05"; then
    print_header "05 — Trading Team"

    run_test "test_trading.py" "05-trading-team" "python test_trading.py" 60

    if [ "$HAS_API_KEY" = true ]; then
        run_test "main.py (full team)" "05-trading-team" "python main.py \"Should we buy UNH?\"" 120
    else
        echo -e "  main.py (full team)... ${YELLOW}⏭ SKIPPED (no API key)${NC}"
    fi
fi

# ═══════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════

print_header "Results"

TOTAL=$((PASSED + FAILED))
echo -e "  Total:   $TOTAL"
echo -e "  ${GREEN}Passed:  $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "  ${RED}Failed:  $FAILED${NC}"
    echo ""
    for f in "${FAILURES[@]}"; do echo -e "    ${RED}✗${NC} $f"; done
fi

echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}${BOLD}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}${BOLD}$FAILED test(s) failed.${NC}"
    exit 1
fi
