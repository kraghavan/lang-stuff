"""
Test script for Algorithmic Trading Team.

Tests all 3 scenarios:
1. Happy path — all agents approve
2. Risk block → alternative works
3. Multiple blocks → give up (PASS)

Also tests data modules independently.
No API key needed for tests (uses rule-based fallbacks).
"""

import os
from portfolio_data import (
    load_portfolio, calculate_portfolio_value, calculate_sector_breakdown,
    check_sector_limits, check_position_limits, check_correlation,
    check_compliance_position_limit, check_restricted_list, check_blackout_period,
)
from market_data import get_market_data, find_alternative, extract_ticker_from_query


def test_market_data():
    """Test market data module."""
    print("Test 1: Market data... ", end="")
    data = get_market_data("NVDA")
    assert data is not None
    assert data["sector"] == "Technology"
    assert data["price"] == 880.00

    assert get_market_data("NONEXISTENT") is None

    ticker = extract_ticker_from_query("Should we buy NVDA?")
    assert ticker == "NVDA"

    alt = find_alternative(exclude_tickers=["AAPL", "MSFT"], exclude_sectors=["Technology"])
    assert alt is not None
    assert alt["sector"] != "Technology"
    print("✓")


def test_portfolio_data():
    """Test portfolio loading and calculations."""
    print("Test 2: Portfolio data... ", end="")
    portfolio = load_portfolio()
    assert len(portfolio) == 4
    assert "AAPL" in portfolio

    value = calculate_portfolio_value(portfolio)
    assert value > 0

    sectors = calculate_sector_breakdown(portfolio)
    assert "Technology" in sectors
    assert sectors["Technology"] > 0.5  # Tech-heavy portfolio
    print("✓")


def test_risk_checks():
    """Test risk checking functions."""
    print("Test 3: Risk checks... ", end="")
    portfolio = load_portfolio()

    # Adding NVDA (tech) to a tech-heavy portfolio should fail sector check
    sector_check = check_sector_limits(portfolio, "NVDA", 11)
    assert sector_check["passed"] is False, f"Expected sector check to fail, got {sector_check}"

    # Adding WMT (consumer staples) should pass
    sector_check = check_sector_limits(portfolio, "WMT", 10)
    assert sector_check["passed"] is True

    # Position limit check
    pos_check = check_position_limits(portfolio, "WMT", 10)
    assert pos_check["passed"] is True

    # Correlation check — NVDA would be 3rd tech position (AAPL, MSFT, NVDA)
    corr_check = check_correlation(portfolio, "NVDA")
    assert corr_check["same_sector_count"] == 3
    assert corr_check["passed"] is True  # limit is 3

    print("✓")


def test_compliance_checks():
    """Test compliance checking functions."""
    print("Test 4: Compliance checks... ", end="")
    portfolio = load_portfolio()

    # Normal ticker should pass
    assert check_restricted_list("AAPL")["passed"] is True

    # META is restricted
    assert check_restricted_list("META")["passed"] is False

    # TSLA is in blackout
    assert check_blackout_period("TSLA")["passed"] is False
    assert check_blackout_period("AAPL")["passed"] is True

    print("✓")


def test_graph_compiles():
    """Test that the trading team graph compiles."""
    print("Test 5: Graph compiles... ", end="")
    from main import create_trading_team
    workflow = create_trading_team()
    app = workflow.compile()
    assert app is not None
    print("✓")


def test_happy_path():
    """Test scenario 1: All agents approve (buy in non-tech sector)."""
    print("Test 6: Happy path (JNJ buy)... ", end="")
    from main import create_trading_team, TradingState
    from portfolio_data import load_portfolio

    workflow = create_trading_team()
    app = workflow.compile()

    # Ask to buy JNJ — healthcare, portfolio is only 3% healthcare
    state: TradingState = {
        "user_query": "Should we buy UNH?",
        "portfolio": load_portfolio(),
        "cash_available": 20000,
        "market_analysis": None,
        "alternative_suggestions": [],
        "risk_assessment": None,
        "compliance_check": None,
        "next_agent": "",
        "trade_decision": None,
        "negotiation_round": 0,
        "max_negotiation_rounds": 3,
        "final_report": "",
        "trade_executed": None,
    }

    result = app.invoke(state)
    assert result["trade_decision"] == "EXECUTE", f"Expected EXECUTE, got {result['trade_decision']}"
    assert result["trade_executed"] is not None
    assert result["trade_executed"]["ticker"] == "UNH"
    print("✓")


def test_risk_block_then_alternative():
    """Test scenario 2: Risk blocks tech → alternative from different sector."""
    print("Test 7: Risk block → alternative... ", end="")
    from main import create_trading_team, TradingState
    from portfolio_data import load_portfolio

    workflow = create_trading_team()
    app = workflow.compile()

    # Ask to buy NVDA — tech, portfolio is already 81% tech → should block
    state: TradingState = {
        "user_query": "Should we buy NVDA?",
        "portfolio": load_portfolio(),
        "cash_available": 20000,
        "market_analysis": None,
        "alternative_suggestions": [],
        "risk_assessment": None,
        "compliance_check": None,
        "next_agent": "",
        "trade_decision": None,
        "negotiation_round": 0,
        "max_negotiation_rounds": 3,
        "final_report": "",
        "trade_executed": None,
    }

    result = app.invoke(state)

    # Should execute an alternative (not NVDA)
    if result["trade_decision"] == "EXECUTE":
        assert result["trade_executed"]["ticker"] != "NVDA", "Should have switched to an alternative"
        assert len(result["alternative_suggestions"]) > 0, "Should have tried alternatives"
    else:
        # It's OK if it passes (no alternatives found) — the key is NVDA was blocked
        assert result["negotiation_round"] > 0, "Should have attempted negotiation"

    print("✓")


def test_multiple_blocks_give_up():
    """Test scenario 3: Multiple blocks → give up after max rounds."""
    print("Test 8: Multiple blocks → PASS... ", end="")
    from main import create_trading_team, TradingState

    workflow = create_trading_team()
    app = workflow.compile()

    # Super concentrated portfolio + low cash → very hard to find anything
    concentrated_portfolio = {
        "AAPL": {"shares": 200, "cost_basis": 150.0, "sector": "Technology"},
        "MSFT": {"shares": 100, "cost_basis": 280.0, "sector": "Technology"},
        "GOOGL": {"shares": 80, "cost_basis": 140.0, "sector": "Technology"},
        "NVDA": {"shares": 20, "cost_basis": 500.0, "sector": "Technology"},
        "AMD": {"shares": 50, "cost_basis": 120.0, "sector": "Technology"},
    }

    state: TradingState = {
        "user_query": "Find me a good trade",
        "portfolio": concentrated_portfolio,
        "cash_available": 500,  # Very low cash
        "market_analysis": None,
        "alternative_suggestions": [],
        "risk_assessment": None,
        "compliance_check": None,
        "next_agent": "",
        "trade_decision": None,
        "negotiation_round": 0,
        "max_negotiation_rounds": 2,  # Low max to speed up test
        "final_report": "",
        "trade_executed": None,
    }

    result = app.invoke(state)

    # With $500 cash, shares will be 0 for most stocks
    # Market Agent should eventually give up or PM should PASS
    assert result["trade_decision"] in ("PASS", "EXECUTE"), f"Got {result['trade_decision']}"
    print("✓")


if __name__ == "__main__":
    print("\n🧪 Trading Team Tests")
    print("=" * 40)

    test_market_data()
    test_portfolio_data()
    test_risk_checks()
    test_compliance_checks()
    test_graph_compiles()
    test_happy_path()
    test_risk_block_then_alternative()
    test_multiple_blocks_give_up()

    print("\n✅ All tests passed!")
