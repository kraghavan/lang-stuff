# Example Outputs — Portfolio Report Generator

These are examples of what the completed application produces.

---

## Full Report (5-Holding Portfolio)

```
💼 Portfolio Report Generator
========================================

📂 Loading portfolio from data/sample_portfolio.csv...
✓ Loaded 5 holdings: AAPL, MSFT, TSLA, NVDA, JPM

📥 Fetching financial data...
  ✓ AAPL: Apple Inc.
  ✓ MSFT: Microsoft Corporation
  ✓ TSLA: Tesla Inc.
  ✓ NVDA: NVIDIA Corporation
  ✓ JPM: JPMorgan Chase & Co.

🤖 Analyzing 5 holdings (batch processing)...
✓ Analyzed 5/5 holdings


════════════════════════════════════════════════════════════════
                    PORTFOLIO REPORT
════════════════════════════════════════════════════════════════

📊 Portfolio Summary
────────────────────────────────────────
  Total Holdings:  5
  Risk Breakdown:  3 LOW, 1 MEDIUM, 1 HIGH
  Avg Rating:      ⭐⭐⭐⭐ (3.8/5)

📈 Holdings Analysis
────────────────────────────────────────

  AAPL — Apple Inc.
  ├─ Outlook: STABLE ⭐⭐⭐⭐
  ├─ Risk: LOW
  ├─ Action: HOLD
  ├─ Strengths: Services growth at 13% YoY, Industry-leading 46.2% gross margin
  ├─ Risks: Slowing hardware revenue growth
  └─ Apple maintains its dominant ecosystem position with
     improving margins driven by the high-margin Services
     segment. Revenue growth is modest but the quality of
     earnings continues to improve.

  MSFT — Microsoft Corporation
  ├─ Outlook: POSITIVE ⭐⭐⭐⭐⭐
  ├─ Risk: LOW
  ├─ Action: HOLD
  ├─ Strengths: Azure growth at 29%, Diversified revenue streams, AI leadership via Copilot
  ├─ Risks: Enterprise spending sensitivity to macro conditions
  └─ Microsoft is executing exceptionally across cloud, AI,
     and productivity. Azure growth remains strong and the
     Copilot suite is driving incremental revenue. Best-
     positioned large-cap for the AI transition.

  TSLA — Tesla Inc.
  ├─ Outlook: MIXED ⭐⭐⭐
  ├─ Risk: HIGH
  ├─ Action: TRIM
  ├─ Strengths: Energy storage growing 75% YoY, Delivery volume still growing
  ├─ Risks: Gross margin compression from 25.6% to 17.6%, Intense EV competition
  └─ Tesla faces margin headwinds from aggressive pricing
     while competition intensifies. The energy storage
     business is a bright spot but can't offset automotive
     margin pressure. Position is underwater relative to
     cost basis.

  NVDA — NVIDIA Corporation
  ├─ Outlook: POSITIVE ⭐⭐⭐⭐⭐
  ├─ Risk: MEDIUM
  ├─ Action: HOLD
  ├─ Strengths: Data center revenue +154% YoY, 73% gross margin, AI infrastructure monopoly
  ├─ Risks: Elevated valuation, China export restrictions
  └─ NVIDIA is the clearest AI beneficiary with explosive
     growth and exceptional profitability. The position has
     nearly doubled from cost basis. Risk is primarily
     valuation — any growth deceleration could cause a
     significant pullback.

  JPM — JPMorgan Chase & Co.
  ├─ Outlook: STABLE ⭐⭐⭐⭐
  ├─ Risk: LOW
  ├─ Action: HOLD
  ├─ Strengths: Strong 17% ROE, Diversified banking franchise, Scale advantages
  ├─ Risks: Potential NII headwind if rates decline
  └─ JPMorgan continues to outperform peers with best-in-
     class execution. The higher rate environment has been
     a tailwind for net interest income. Provides valuable
     sector diversification away from the tech-heavy
     portfolio.

⚠️  Action Items
────────────────────────────────────────
  • Review high-risk: TSLA
  • Consider action: TSLA (TRIM — underwater position with margin pressure)
  • NVDA has nearly doubled — consider taking partial profits
  • Portfolio is 80% Technology — add Healthcare or Consumer Staples
  • JPM provides good diversification — maintain position

════════════════════════════════════════════════════════════════
```

---

## What to Notice

1. **Structured data** — Every holding has the same fields (outlook, risk, rating, etc.)
2. **Typed enums** — Risk is always LOW/MEDIUM/HIGH, outlook is always POSITIVE/STABLE/MIXED/NEGATIVE
3. **Batch processing** — All 5 holdings analyzed in one batch call
4. **Programmatic aggregation** — Risk breakdown and avg rating are computed from Pydantic objects
5. **Actionable recommendations** — Specific, tailored to each position's performance
6. **Report formatting** — Structured data enables consistent, professional formatting

## Structured Output Examples

Each `HoldingAnalysis` object looks like this as Python:

```python
HoldingAnalysis(
    ticker="AAPL",
    company_name="Apple Inc.",
    outlook="STABLE",
    risk_level="LOW",
    star_rating=4,
    summary="Apple maintains its dominant ecosystem position...",
    recommendation="HOLD",
    key_strengths=["Services growth at 13% YoY", "Industry-leading 46.2% gross margin"],
    key_risks=["Slowing hardware revenue growth"]
)
```

And as JSON:

```json
{
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "outlook": "STABLE",
    "risk_level": "LOW",
    "star_rating": 4,
    "summary": "Apple maintains its dominant ecosystem position...",
    "recommendation": "HOLD",
    "key_strengths": ["Services growth at 13% YoY", "Industry-leading 46.2% gross margin"],
    "key_risks": ["Slowing hardware revenue growth"]
}
```

This makes it trivial to:
- Filter: `[a for a in analyses if a.risk_level == "HIGH"]`
- Sort: `sorted(analyses, key=lambda a: a.star_rating, reverse=True)`
- Export: `[a.model_dump() for a in analyses]` → JSON-ready
- Validate: Pydantic enforces types and constraints automatically
