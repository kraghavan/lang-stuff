# 💼 Portfolio Report Generator

Analyzes an entire stock portfolio using Claude with structured Pydantic output and batch processing, then generates a professional report. All code is **complete and ready to run**.

## 🎯 What It Does

1. **Load** — Reads portfolio from CSV (ticker, shares, cost basis)
2. **Fetch** — Gets financial data for each holding (built-in sample data)
3. **Analyze** — Claude analyzes each holding with **structured output** (Pydantic models)
4. **Report** — Generates a formatted portfolio report with aggregated insights

## 🌟 Why LangChain (not LangGraph)?

- ✅ **Structured output** — Pydantic models enforce response schema
- ✅ **Batch processing** — `chain.batch()` analyzes multiple holdings concurrently
- ✅ **Typed objects** — LLM returns Python objects, not text
- ❌ No conditional branching — every holding gets the same analysis

## 📁 Files

```
04-portfolio-report-generator/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── simple_version.py      # Main implementation
├── portfolio_models.py    # Pydantic output schemas
├── data/
│   ├── sample_portfolio.csv  # 5-holding sample portfolio
│   └── README.md             # Data format docs
└── examples/
    └── EXAMPLE_OUTPUTS.md    # Sample report output
```

## 🚀 Quick Start

```bash
cd langchain/04-portfolio-report-generator
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"
python simple_version.py
```

### Example Output (abbreviated)

```
💼 Portfolio Report Generator
========================================
📂 Loading portfolio...
✓ Loaded 5 holdings: AAPL, MSFT, TSLA, NVDA, JPM

🤖 Analyzing 5 holdings (batch processing)...
✓ Analyzed 5/5 holdings

════════════════════════════════════════════════════════════
                    PORTFOLIO REPORT
════════════════════════════════════════════════════════════

📊 Portfolio Summary
  Total Holdings:  5
  Risk Breakdown:  3 LOW, 2 MEDIUM
  Avg Rating:      ⭐⭐⭐⭐ (4.4/5)

📈 Holdings Analysis

  AAPL — Apple Inc.
  ├─ Outlook: STABLE ⭐⭐⭐⭐
  ├─ Risk: LOW | Action: HOLD
  └─ Strong ecosystem moat, services growth at 13% YoY

  TSLA — Tesla Inc.
  ├─ Outlook: MIXED ⭐⭐⭐
  ├─ Risk: MEDIUM | Action: HOLD
  └─ Margin compression from 25.6% to 17.6%, but energy storage +75%

⚠️  Action Items
  • Maintain positions: AAPL, MSFT, TSLA, NVDA, JPM
════════════════════════════════════════════════════════════
```

## 🏗️ Architecture

```
┌──────────────┐     ┌───────────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Portfolio   │ ──► │  Enrich Data      │ ──► │  Analyze (Batch) │ ──► │  Generate    │
│  CSV File    │     │  (sample data)    │     │  Claude +        │     │  Report      │
│              │     │                   │     │  Pydantic Schema │     │              │
└──────────────┘     └───────────────────┘     └──────────────────┘     └──────────────┘
  pandas/csv          SAMPLE_FINANCIAL_DATA     chain.batch() with       Programmatic
                                                structured_output()      formatting
```

---

## 📖 Code Walkthrough

### `portfolio_models.py` — Pydantic Output Schemas

Defines the exact shape of Claude's response:

```python
class HoldingAnalysis(BaseModel):
    ticker: str
    outlook: Literal["POSITIVE", "STABLE", "MIXED", "NEGATIVE"]
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    star_rating: int = Field(ge=1, le=5)
    summary: str
    recommendation: Literal["BUY", "HOLD", "SELL", "TRIM"]
    key_strengths: list[str]
    key_risks: list[str]
```

- `Literal[...]` — Claude must pick from these exact values
- `Field(ge=1, le=5)` — Validates range
- `Field(description="...")` — Claude reads these to know what to generate

```bash
python portfolio_models.py  # See the JSON schema and test instance
```

### `simple_version.py` — Structured Output + Batch

**`create_analysis_chain()`** — The key difference from previous examples:

```python
# Before (returns string):
chain = prompt | llm | StrOutputParser()

# Now (returns typed Pydantic object):
structured_llm = llm.with_structured_output(HoldingAnalysis)
chain = prompt | structured_llm
```

`with_structured_output()` sends the Pydantic schema to Claude as a tool definition. Claude returns data matching the schema exactly. You get typed Python objects — no string parsing.

**`analyze_all_holdings(holdings)`** — Batch processing:

```python
# Slow: sequential
for h in holdings: chain.invoke(h)  # 5 API calls, one at a time

# Fast: batch with concurrency
results = chain.batch(holdings, config={"max_concurrency": 3})
```

**`generate_report(analyses)`** — Because analyses are Pydantic objects, report generation is pure Python:

```python
high_risk = [a for a in analyses if a.risk_level == "HIGH"]
avg_rating = sum(a.star_rating for a in analyses) / len(analyses)
sells = [a for a in analyses if a.recommendation in ("SELL", "TRIM")]
```

---

## 🛠️ Key LangChain Concepts

### Structured Output vs String Output

| | String Output (Examples 01-03) | Structured Output (This Example) |
|---|---|---|
| Returns | Raw text | Typed Pydantic object |
| Access fields | Regex/parsing | `result.risk_level` |
| Sort/filter | Difficult | `sorted(results, key=lambda r: r.star_rating)` |
| Validate | Manual | Automatic (Pydantic) |
| Export | String manipulation | `result.model_dump_json()` |

### `chain.batch()` — Concurrent Processing

Processes multiple inputs in parallel. LangChain handles concurrency — you just set `max_concurrency`:

```python
results = chain.batch(inputs, config={"max_concurrency": 3})
# Returns: [HoldingAnalysis(...), HoldingAnalysis(...), ...]
```

---

## 🧪 Testing

```bash
python portfolio_models.py   # Verify Pydantic schemas
python simple_version.py     # Full portfolio report
```

| Check | What to Verify |
|-------|---------------|
| Types | Each result is a `HoldingAnalysis` object |
| Risk ratings | TSLA should be higher risk than AAPL |
| Recommendations | Reasonable given the financial data |
| Report format | Consistent structure across all holdings |

---

## 🎯 Challenges

1. **Add a holding** — Edit `sample_portfolio.csv` to add `AMZN,20,120.00` and re-run
2. **Add a field** — Add `sector: str` to `HoldingAnalysis` — does Claude fill it?
3. **Sort the report** — Modify `generate_report()` to sort by star rating (best first)
4. **Export JSON** — Add `--json` flag that outputs `[a.model_dump() for a in analyses]`
5. **Time sequential vs batch** — Compare `chain.invoke()` in a loop vs `chain.batch()`

---

## ✅ Completion Checklist

- [ ] Ran `python simple_version.py` and saw the portfolio report
- [ ] Understand `with_structured_output(HoldingAnalysis)` — typed LLM responses
- [ ] Understand `chain.batch()` — concurrent processing
- [ ] Can access typed fields (`result.risk_level`, `result.star_rating`)
- [ ] Tried at least one challenge

## 📚 Resources

- [Structured Output Guide](https://python.langchain.com/docs/how_to/structured_output/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)
- [Batch Processing](https://python.langchain.com/docs/how_to/parallel/)

---

**Congratulations! You've completed all LangChain examples. Ready for [LangGraph](../../langgraph/) →**
