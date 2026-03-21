#!/bin/bash
#
# Smoke Test Runner for LangChain Examples
#
# Runs each example end-to-end and checks for clean execution.
# Catches: import errors, missing files, API issues, broken chains.
#
# Usage:
#   cd langchain/
#   ./smoke_test.sh           # Run all tests
#   ./smoke_test.sh 01        # Run only example 01
#   ./smoke_test.sh 01 03     # Run examples 01 and 03
#
# Requirements:
#   - ANTHROPIC_API_KEY set
#   - venv/ with dependencies installed
#   - Internet connection (for SEC EDGAR + Claude API)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SCRIPT_DIR/venv/bin/activate"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m'

PASSED=0
FAILED=0
SKIPPED=0
FAILURES=()

# ═══════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════

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

    local output
    local exit_code

    # Use perl for timeout (works on macOS without coreutils)
    output=$(cd "$SCRIPT_DIR/$dir" && source "$VENV" && perl -e "alarm $timeout_secs; exec @ARGV" bash -c "$cmd" 2>&1) || exit_code=$?
    exit_code=${exit_code:-0}

    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ FAILED${NC} (exit code $exit_code)"
        FAILURES+=("$name")
        FAILED=$((FAILED + 1))
        # Show last 10 lines of output for debugging
        echo -e "${YELLOW}    Last 10 lines:${NC}"
        echo "$output" | tail -10 | sed 's/^/    /'
    fi
}

should_run() {
    local example_num="$1"
    # Run all if no args, or if this example was specified
    if [ ${#FILTER[@]} -eq 0 ]; then
        return 0
    fi
    for f in "${FILTER[@]}"; do
        if [[ "$example_num" == "$f" ]]; then
            return 0
        fi
    done
    return 1
}

# ═══════════════════════════════════════════════
# Pre-flight checks
# ═══════════════════════════════════════════════

print_header "LangChain Smoke Tests"

# Collect filter args
FILTER=("$@")
if [ ${#FILTER[@]} -gt 0 ]; then
    echo -e "  Running: examples ${FILTER[*]}"
else
    echo -e "  Running: all examples"
fi

# Check API key
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo -e "\n${RED}❌ ANTHROPIC_API_KEY not set. Export it and retry.${NC}"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} ANTHROPIC_API_KEY is set"

# Check venv
if [ ! -f "$VENV" ]; then
    echo -e "\n${RED}❌ venv not found at $SCRIPT_DIR/venv${NC}"
    echo "  Create it: python3 -m venv venv && source venv/bin/activate && pip install -r 01-stock-summary/requirements.txt"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} venv found"

# Check imports
IMPORT_CHECK=$(cd "$SCRIPT_DIR" && source "$VENV" && python -c "import langchain_core, langchain_anthropic; print('ok')" 2>&1) || true
if [ "$IMPORT_CHECK" != "ok" ]; then
    echo -e "\n${RED}❌ LangChain dependencies not installed in venv${NC}"
    echo "  Run: source venv/bin/activate && pip install langchain langchain-anthropic langchain-core"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} LangChain imports OK"

# ═══════════════════════════════════════════════
# Example 01: Stock Summary Generator
# ═══════════════════════════════════════════════

if should_run "01"; then
    print_header "01 — Stock Summary Generator"

    run_test \
        "stock_data.py (SEC EDGAR fetch)" \
        "01-stock-summary" \
        "python stock_data.py" \
        30

    run_test \
        "simple_version.py (full chain with Claude)" \
        "01-stock-summary" \
        "echo 'AAPL' | python simple_version.py" \
        60
fi

# ═══════════════════════════════════════════════
# Example 02: Financial News Analyzer
# ═══════════════════════════════════════════════

if should_run "02"; then
    print_header "02 — Financial News Analyzer"

    run_test \
        "news_data.py (sample data)" \
        "02-financial-news-analyzer" \
        "python news_data.py" \
        10

    run_test \
        "simple_version.py (3-step pipeline)" \
        "02-financial-news-analyzer" \
        "echo 'NVDA' | python simple_version.py" \
        90
fi

# ═══════════════════════════════════════════════
# Example 03: SEC Filing Q&A (RAG)
# ═══════════════════════════════════════════════

if should_run "03"; then
    print_header "03 — SEC Filing Q&A (RAG)"

    run_test \
        "filing_loader.py (chunking)" \
        "03-sec-filing-qa" \
        "python filing_loader.py" \
        30

    run_test \
        "simple_version.py (RAG Q&A)" \
        "03-sec-filing-qa" \
        "printf 'What was Apple total revenue?\nquit\n' | python simple_version.py" \
        120
fi

# ═══════════════════════════════════════════════
# Example 04: Portfolio Report Generator
# ═══════════════════════════════════════════════

if should_run "04"; then
    print_header "04 — Portfolio Report Generator"

    run_test \
        "portfolio_models.py (Pydantic schemas)" \
        "04-portfolio-report-generator" \
        "python portfolio_models.py" \
        10

    run_test \
        "simple_version.py (batch analysis + report)" \
        "04-portfolio-report-generator" \
        "python simple_version.py" \
        180
fi

# ═══════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════

print_header "Results"

TOTAL=$((PASSED + FAILED + SKIPPED))
echo -e "  Total:   $TOTAL"
echo -e "  ${GREEN}Passed:  $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "  ${RED}Failed:  $FAILED${NC}"
    echo ""
    echo -e "  ${RED}Failures:${NC}"
    for f in "${FAILURES[@]}"; do
        echo -e "    ${RED}✗${NC} $f"
    done
fi
if [ $SKIPPED -gt 0 ]; then
    echo -e "  ${YELLOW}Skipped: $SKIPPED${NC}"
fi

echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}${BOLD}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}${BOLD}$FAILED test(s) failed.${NC}"
    exit 1
fi
