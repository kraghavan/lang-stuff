# 💼 Portfolio Report Generator

A LangChain application that analyzes an entire stock portfolio using structured Pydantic output models and batch processing, then generates a professional report.

## 🎯 What It Does

Takes a portfolio of stock holdings and produces a comprehensive analysis:

1. **Load** — Reads portfolio from a CSV file (ticker, shares, cost basis)
2. **Fetch** — Gets current financial data for each holding (SEC EDGAR)
3. **Analyze** — Claude analyzes each holding with **structured output** (Pydantic models)
4. **Score** — Assigns risk scores, outlook ratings, and classifications
5. **Report** — Generates a formatted portfolio report with aggregated insights

## 🌟 Why LangChain?

This example showcases LangChain's most advanced simple-chain features:

- ✅ **Structured output** — Pydantic models enforce response schema
- ✅ **Batch processing** — Analyze multiple holdings efficiently with `chain.batch()`
- ✅ **Output schemas** — LLM returns typed Python objects, not just text
- ✅ **Data transformation** — Convert between formats at each pipeline stage

**Why NOT LangGraph?**
- ❌ No conditional branching — every holding gets the same analysis
- ❌ No loops — process once per holding
- ❌ No inter-agent communication — single analyzer for all

**When WOULD you use LangGraph?**
- If different asset types need different analysis paths (stocks vs bonds vs crypto)
- If you need iterative deep-dives on flagged holdings
- If you need human approval before generating the final report

## 📁 Files in This Example

```
04-portfolio-report-generator/
├── README.md                 # This file
├── LEARNING_GUIDE.md         # Step-by-step TODO tutorial
├── requirements.txt          # Python dependencies
├── simple_version.py         # Main implementation (has TODOs)
├── portfolio_models.py       # Pydantic output schemas
├── data/
│   ├── sample_portfolio.csv  # Sample portfolio for testing
│   └── README.md             # Data format documentation
└── examples/
    └── EXAMPLE_OUTPUTS.md    # Sample report outputs
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd langchain/04-portfolio-report-generator
pip install -r requirements.txt
```

### 2. Set Up API Key

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### 3. Run It

```bash
python simple_version.py
```

### Example Output

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

🤖 Analyzing holdings (batch processing)...
  ✓ Analyzed 5/5 holdings

═══════════════════════════════════════════════════════════════
                    PORTFOLIO REPORT
═══════════════════════════════════════════════════════════════

📊 Portfolio Summary
─────────────────────────────────────────
  Total Holdings:        5
  Total Market Value:    $487,250
  Total Cost Basis:      $392,100
  Unrealized Gain/Loss:  +$95,150 (+24.3%)

📈 Holdings Analysis
─────────────────────────────────────────

  AAPL — Apple Inc.
  ├─ Shares: 100 @ $150.00 → Current: ~$185.00
  ├─ Outlook: STABLE ⭐⭐⭐⭐
  ├─ Risk: LOW
  └─ Note: Strong ecosystem moat, services growth

  MSFT — Microsoft Corporation
  ├─ Shares: 50 @ $280.00 → Current: ~$420.00
  ├─ Outlook: POSITIVE ⭐⭐⭐⭐⭐
  ├─ Risk: LOW
  └─ Note: Cloud + AI leadership, diversified revenue

  TSLA — Tesla Inc.
  ├─ Shares: 30 @ $200.00 → Current: ~$175.00
  ├─ Outlook: MIXED ⭐⭐⭐
  ├─ Risk: HIGH
  └─ Note: Margin compression, but FSD optionality

  NVDA — NVIDIA Corporation
  ├─ Shares: 25 @ $450.00 → Current: ~$880.00
  ├─ Outlook: POSITIVE ⭐⭐⭐⭐⭐
  ├─ Risk: MEDIUM
  └─ Note: AI demand strong, valuation stretched

  JPM — JPMorgan Chase & Co.
  ├─ Shares: 40 @ $140.00 → Current: ~$195.00
  ├─ Outlook: STABLE ⭐⭐⭐⭐
  ├─ Risk: LOW
  └─ Note: Rate environment favorable, credit quality solid

🏷️  Sector Breakdown
─────────────────────────────────────────
  Technology:    80% (AAPL, MSFT, TSLA, NVDA)
  Financials:    20% (JPM)

⚠️  Recommendations
─────────────────────────────────────────
  • Portfolio is heavily concentrated in Technology
  • Consider adding Healthcare or Consumer Staples
  • TSLA position is underwater — review thesis
  • NVDA has outsized gains — consider trimming

═══════════════════════════════════════════════════════════════
```

## 🏗️ Architecture

### Batch Analysis Pipeline

```
┌──────────────┐     ┌───────────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Portfolio   │ ──► │  Fetch Data       │ ──► │  Analyze (Batch) │ ──► │  Generate    │
│  CSV File    │     │  (SEC EDGAR)      │     │  Claude +        │     │  Report      │
│              │     │  per holding      │     │  Pydantic Schema │     │              │
└──────────────┘     └───────────────────┘     └──────────────────┘     └──────────────┘
  pandas              stock_data module         chain.batch()            Format + print
                      (from example 01)         with_structured_output()
```

### Structured Output Flow

```
For each holding:

Financial Data (dict)
    │
    ▼
┌─────────────────────────────────────────────┐
│ Prompt Template                             │
│                                             │
│ "Analyze {ticker} with data: {metrics}      │
│  Return structured analysis."               │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ Claude with Structured Output               │
│                                             │
│ llm.with_structured_output(HoldingAnalysis) │
│                                             │
│ Returns a Pydantic object, NOT raw text:    │
│ HoldingAnalysis(                            │
│     ticker="AAPL",                          │
│     company_name="Apple Inc.",              │
│     outlook="STABLE",                       │
│     risk_level="LOW",                       │
│     star_rating=4,                          │
│     summary="Strong ecosystem moat...",     │
│     key_metrics={...},                      │
│     recommendation="HOLD"                   │
│ )                                           │
└─────────────────────────────────────────────┘
```

### Batch Processing

Instead of analyzing one holding at a time:

```python
# Slow: one at a time
for holding in portfolio:
    result = chain.invoke(holding)  # 5 sequential API calls

# Fast: batch processing
results = chain.batch(portfolio)  # LangChain handles concurrency
```

## 🛠️ Key LangChain Concepts You'll Learn

### 1. Pydantic Output Models

Define the exact shape of Claude's response:

```python
from pydantic import BaseModel, Field
from typing import Literal

class HoldingAnalysis(BaseModel):
    """Structured analysis of a single portfolio holding."""
    ticker: str = Field(description="Stock ticker symbol")
    outlook: Literal["POSITIVE", "STABLE", "MIXED", "NEGATIVE"] = Field(
        description="Forward-looking outlook"
    )
    risk_level: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        description="Current risk assessment"
    )
    star_rating: int = Field(ge=1, le=5, description="1-5 star rating")
    summary: str = Field(description="2-3 sentence analysis")
    recommendation: Literal["BUY", "HOLD", "SELL", "TRIM"] = Field(
        description="Action recommendation"
    )
```

**Why this matters**: Instead of parsing free-text, you get **typed Python objects** with guaranteed structure. No regex needed.

### 2. `with_structured_output()`

Tell Claude to return a specific schema:

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0)

# This returns HoldingAnalysis objects, not strings
structured_llm = llm.with_structured_output(HoldingAnalysis)

result = structured_llm.invoke("Analyze AAPL...")
print(result.outlook)       # "STABLE"
print(result.risk_level)    # "LOW"
print(result.star_rating)   # 4
```

### 3. Batch Processing

Process multiple inputs efficiently:

```python
chain = prompt | structured_llm

# Prepare inputs for all holdings
inputs = [
    {"ticker": "AAPL", "metrics": "..."},
    {"ticker": "MSFT", "metrics": "..."},
    {"ticker": "TSLA", "metrics": "..."},
]

# Process all at once (LangChain handles concurrency)
results = chain.batch(inputs)
# Returns: [HoldingAnalysis(...), HoldingAnalysis(...), HoldingAnalysis(...)]
```

### 4. CSV Data Loading

Read portfolio from a simple CSV:

```python
import csv

# data/sample_portfolio.csv:
# ticker,shares,cost_basis
# AAPL,100,150.00
# MSFT,50,280.00
# TSLA,30,200.00
```

## 🧪 Testing

### Test Cases

| Scenario | What to Check |
|----------|---------------|
| Run with sample_portfolio.csv | All 5 holdings analyzed |
| Check structured output | Each result is a HoldingAnalysis object |
| Verify risk ratings | TSLA should be higher risk than AAPL |
| Check recommendations | Loss positions might get SELL/TRIM |
| Test with 1 holding | Batch processing still works |

### Testing Incrementally

```bash
# Step 1: Test Pydantic models
python -c "from portfolio_models import HoldingAnalysis; print(HoldingAnalysis.model_json_schema())"

# Step 2: Test single holding analysis
python simple_version.py
# Should analyze all holdings and generate report

# Step 3: Modify sample_portfolio.csv and re-run
```

## 🔧 Configuration

```python
# Analysis parameters
MODEL = "claude-sonnet-4-5-20250929"
TEMPERATURE = 0

# Portfolio file
PORTFOLIO_PATH = "data/sample_portfolio.csv"

# Batch processing
MAX_CONCURRENCY = 3  # Don't overwhelm the API
```

## 💡 Learning Outcomes

After completing this example, you'll understand:

- ✅ **Pydantic models** for structured LLM output
- ✅ **`with_structured_output()`** to enforce response schemas
- ✅ **`chain.batch()`** for processing multiple inputs
- ✅ **CSV data loading** and portfolio data handling
- ✅ **Report generation** from structured analysis results
- ✅ **Type safety** — working with Python objects instead of raw text

## 🔗 Comparison: Full Learning Progression

| Feature | 01 Stock Summary | 02 News Analyzer | 03 Filing Q&A | 04 Portfolio Report |
|---------|-----------------|------------------|---------------|-------------------|
| Chains | 1 (basic) | 3 (sequential) | 2 (RAG) | 1 per holding (batch) |
| Output | String | String | String | **Pydantic objects** |
| Input | Single ticker | Single ticker | Questions | **CSV portfolio** |
| Processing | Single | Sequential | Retrieve+Generate | **Batch** |
| Key concept | LCEL basics | RunnablePassthrough | RAG | **Structured output** |

## 🚧 Future Enhancements

- [ ] Real-time price data (Alpha Vantage or Yahoo Finance API)
- [ ] PDF report export (ReportLab or WeasyPrint)
- [ ] Historical tracking (compare reports over time)
- [ ] Sector allocation visualization (matplotlib charts)
- [ ] Rebalancing recommendations based on target allocation
- [ ] Tax-loss harvesting suggestions
- [ ] Email delivery of morning reports

## 📚 Resources

- [Structured Output Guide](https://python.langchain.com/docs/how_to/structured_output/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)
- [Batch Processing](https://python.langchain.com/docs/how_to/parallel/)
- [ChatAnthropic Structured Output](https://python.langchain.com/docs/integrations/chat/anthropic/)

---

**Congratulations! You've completed all LangChain examples. Ready for [LangGraph](../../langgraph/) →**
