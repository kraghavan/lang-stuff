"""
Market Data — Simulated Market Signals

Provides simulated market data (prices, signals, sectors) for the
trading team to analyze. No external API needed.

Each ticker has:
- Current price
- Sector classification
- Technical signals (RSI, momentum)
- A conviction level for BUY/SELL/HOLD

Usage:
    from market_data import get_market_data, find_alternative
"""

from typing import Dict, Optional, List


# ═══════════════════════════════════════════════
# Simulated market universe
# ═══════════════════════════════════════════════

MARKET_UNIVERSE: Dict[str, Dict] = {
    # Technology
    "AAPL": {"price": 185.00, "sector": "Technology", "rsi": 55, "momentum": "neutral", "signal": "HOLD", "conviction": "MEDIUM"},
    "MSFT": {"price": 420.00, "sector": "Technology", "rsi": 62, "momentum": "bullish", "signal": "BUY", "conviction": "MEDIUM"},
    "NVDA": {"price": 880.00, "sector": "Technology", "rsi": 72, "momentum": "strong_bullish", "signal": "BUY", "conviction": "HIGH"},
    "AMD": {"price": 165.00, "sector": "Technology", "rsi": 48, "momentum": "neutral", "signal": "BUY", "conviction": "MEDIUM"},
    "QCOM": {"price": 170.00, "sector": "Technology", "rsi": 42, "momentum": "neutral", "signal": "HOLD", "conviction": "LOW"},
    "GOOGL": {"price": 175.00, "sector": "Technology", "rsi": 58, "momentum": "bullish", "signal": "BUY", "conviction": "MEDIUM"},

    # Financials
    "JPM": {"price": 195.00, "sector": "Financials", "rsi": 60, "momentum": "bullish", "signal": "BUY", "conviction": "MEDIUM"},
    "GS": {"price": 470.00, "sector": "Financials", "rsi": 55, "momentum": "neutral", "signal": "HOLD", "conviction": "LOW"},
    "BAC": {"price": 38.00, "sector": "Financials", "rsi": 45, "momentum": "neutral", "signal": "BUY", "conviction": "LOW"},

    # Healthcare
    "JNJ": {"price": 160.00, "sector": "Healthcare", "rsi": 40, "momentum": "bearish", "signal": "HOLD", "conviction": "LOW"},
    "UNH": {"price": 520.00, "sector": "Healthcare", "rsi": 35, "momentum": "oversold", "signal": "BUY", "conviction": "HIGH"},
    "PFE": {"price": 28.00, "sector": "Healthcare", "rsi": 28, "momentum": "oversold", "signal": "BUY", "conviction": "MEDIUM"},

    # Consumer Staples
    "WMT": {"price": 215.00, "sector": "Consumer Staples", "rsi": 52, "momentum": "neutral", "signal": "BUY", "conviction": "MEDIUM"},
    "PG": {"price": 165.00, "sector": "Consumer Staples", "rsi": 50, "momentum": "neutral", "signal": "HOLD", "conviction": "LOW"},
    "KO": {"price": 62.00, "sector": "Consumer Staples", "rsi": 48, "momentum": "neutral", "signal": "BUY", "conviction": "LOW"},

    # Energy
    "XOM": {"price": 115.00, "sector": "Energy", "rsi": 58, "momentum": "bullish", "signal": "BUY", "conviction": "MEDIUM"},
    "CVX": {"price": 155.00, "sector": "Energy", "rsi": 53, "momentum": "neutral", "signal": "HOLD", "conviction": "LOW"},
}

# Simulated sector correlations (simplified)
SECTOR_CORRELATIONS = {
    ("Technology", "Technology"): 0.85,
    ("Technology", "Financials"): 0.45,
    ("Technology", "Healthcare"): 0.30,
    ("Technology", "Consumer Staples"): 0.15,
    ("Technology", "Energy"): 0.20,
    ("Financials", "Financials"): 0.80,
    ("Financials", "Healthcare"): 0.35,
    ("Financials", "Consumer Staples"): 0.25,
    ("Financials", "Energy"): 0.40,
    ("Healthcare", "Healthcare"): 0.75,
    ("Healthcare", "Consumer Staples"): 0.30,
    ("Healthcare", "Energy"): 0.15,
    ("Consumer Staples", "Consumer Staples"): 0.70,
    ("Consumer Staples", "Energy"): 0.20,
    ("Energy", "Energy"): 0.80,
}


def get_market_data(ticker: str) -> Optional[Dict]:
    """Get market data for a ticker."""
    ticker = ticker.upper()
    if ticker not in MARKET_UNIVERSE:
        return None
    data = MARKET_UNIVERSE[ticker].copy()
    data["ticker"] = ticker
    return data


def get_sector(ticker: str) -> str:
    """Get the sector for a ticker."""
    data = MARKET_UNIVERSE.get(ticker.upper(), {})
    return data.get("sector", "Unknown")


def get_price(ticker: str) -> float:
    """Get the current price for a ticker."""
    data = MARKET_UNIVERSE.get(ticker.upper(), {})
    return data.get("price", 0.0)


def get_correlation(sector1: str, sector2: str) -> float:
    """Get correlation between two sectors."""
    key = (sector1, sector2)
    rev_key = (sector2, sector1)
    return SECTOR_CORRELATIONS.get(key, SECTOR_CORRELATIONS.get(rev_key, 0.5))


def find_alternative(
    exclude_tickers: List[str],
    exclude_sectors: List[str],
    min_conviction: str = "LOW",
) -> Optional[Dict]:
    """
    Find an alternative ticker from a different sector.

    Prioritizes by conviction level (HIGH > MEDIUM > LOW) and
    BUY signal over HOLD.

    Args:
        exclude_tickers: Tickers to skip
        exclude_sectors: Sectors to skip
        min_conviction: Minimum conviction level

    Returns:
        Market data dict for the best alternative, or None
    """
    exclude_tickers = [t.upper() for t in exclude_tickers]
    exclude_sectors = [s.strip() for s in exclude_sectors]

    conviction_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    min_conv_val = conviction_order.get(min_conviction, 0)

    candidates = []
    for ticker, data in MARKET_UNIVERSE.items():
        if ticker in exclude_tickers:
            continue
        if data["sector"] in exclude_sectors:
            continue
        if data["signal"] == "SELL":
            continue
        if conviction_order.get(data["conviction"], 0) < min_conv_val:
            continue
        candidates.append((ticker, data))

    if not candidates:
        return None

    # Sort: BUY before HOLD, then by conviction (HIGH first)
    candidates.sort(
        key=lambda x: (
            0 if x[1]["signal"] == "BUY" else 1,
            -conviction_order.get(x[1]["conviction"], 0),
        )
    )

    best_ticker, best_data = candidates[0]
    result = best_data.copy()
    result["ticker"] = best_ticker
    return result


def extract_ticker_from_query(query: str) -> Optional[str]:
    """Try to extract a stock ticker from a user query."""
    query_upper = query.upper()
    for ticker in MARKET_UNIVERSE:
        if ticker in query_upper:
            return ticker
    return None


# ═══════════════════════════════════════════════
if __name__ == "__main__":
    print("📈 Market Data Universe\n")
    for ticker, data in MARKET_UNIVERSE.items():
        print(f"  {ticker:5s} ${data['price']:>8.2f}  {data['sector']:20s}  RSI:{data['rsi']:3d}  {data['signal']:4s}  {data['conviction']}")

    print(f"\n  Total tickers: {len(MARKET_UNIVERSE)}")

    print("\n--- Find alternative (exclude tech) ---")
    alt = find_alternative(exclude_tickers=["AAPL", "MSFT"], exclude_sectors=["Technology"])
    if alt:
        print(f"  Best alternative: {alt['ticker']} ({alt['sector']}) - {alt['signal']} ({alt['conviction']})")
