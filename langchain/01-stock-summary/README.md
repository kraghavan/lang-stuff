# 📈 Stock Summary Generator

A LangChain-powered tool that fetches real stock data and generates professional analyst-style summaries using Claude. All code is **complete and ready to run**.

## 🎯 What It Does

1. Fetches real company financial data from SEC EDGAR (free, no API key)
2. Formats the data into a prompt template
3. Sends to Claude for intelligent analysis
4. Parses the response into a clean, structured summary

## 🌟 Why LangChain (not LangGraph)?

- ✅ **Linear flow** — Fetch → Format → Analyze → Output (no loops needed)
- ✅ **Prompt templates** — Reusable prompt with variable injection
- ✅ **Output parsing** — Convert Claude's response into structured data
- ❌ No conditional branching, loops, or multi-agent coordination needed

## 📁 Files

```
01-stock-summary/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── simple_version.py      # Main LangChain implementation
├── stock_data.py          # SEC EDGAR API client
└── examples/
    └── EXAMPLE_OUTPUTS.md # Sample outputs for reference
```

## 🚀 Quick Start

```bash
cd langchain/01-stock-summary
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"
python simple_version.py
# Enter: AAPL
```

### Example Output

```
📈 Stock Summary Generator
========================================
Enter a stock ticker (e.g., AAPL, MSFT, TSLA): AAPL

📥 Fetching data for AAPL from SEC EDGAR...
✓ Company: APPLE INC (CIK: 0000320193)
✓ Retrieved financial data

🤖 Generating analysis with Claude...
✓ Analysis complete

════════════════════════════════════════════════════════
               AAPL — STOCK SUMMARY
════════════════════════════════════════════════════════
📊 Key Metrics:
  Revenue (TTM):        $391.0B
  Net Income (TTM):     $101.2B
  Profit Margin:        25.9%

📈 Performance:
  Revenue Growth (YoY): +5.2%
  Income Growth (YoY):  +8.1%

💡 Outlook: Stable
  Apple's massive cash position and ecosystem lock-in
  provide strong defensive characteristics.
════════════════════════════════════════════════════════
```

## 🏗️ Architecture

```
┌──────────────┐     ┌───────────────┐     ┌─────────────┐     ┌──────────────┐
│  Fetch Data  │ ──► │ Prompt        │ ──► │   Claude     │ ──► │ Output       │
│  (SEC EDGAR) │     │ Template      │     │   (LLM)      │     │ Parser       │
└──────────────┘     └───────────────┘     └─────────────┘     └──────────────┘
    stock_data.py        PromptTemplate       ChatAnthropic       StrOutputParser
```

In LCEL: `chain = prompt | llm | parser`

---

## 📖 Code Walkthrough

Run the code first (`python simple_version.py`), then read along below.

### `stock_data.py` — Data Layer

**`get_company_cik(ticker)`** — Converts "AAPL" → SEC CIK number "0000320193". SEC identifies companies by CIK, not ticker. Makes a GET request to `https://www.sec.gov/files/company_tickers.json` and searches for the matching ticker.

**`get_financial_facts(cik)`** — Fetches ALL financial data from SEC EDGAR XBRL API. Response is deeply nested: `facts → "facts" → "us-gaap" → concept_name → "units" → "USD" → [entries]`.

**`extract_metric(facts, concept_names)`** — Navigates the nested SEC data to find the most recent value for a metric. Tries multiple XBRL concept names (companies use different names — Apple uses `"Revenues"` but others use `"RevenueFromContractWithCustomerExcludingAssessedTax"`).

**`get_stock_data(ticker)`** — Convenience wrapper: CIK lookup → fetch facts → extract all metrics → format numbers.

```bash
# Test the data layer alone
python stock_data.py
```

### `simple_version.py` — LangChain Chain

**`create_analysis_prompt()`** — Creates a `ChatPromptTemplate` with `{ticker}`, `{company_name}`, `{financial_data}` placeholders. The system message sets Claude as a financial analyst; the human message provides data and asks for structured output.

**`create_llm()`** — Initializes `ChatAnthropic` with `temperature=0` (deterministic for financial analysis) and `max_tokens=1024`.

**`create_summary_chain()`** — The core LCEL chain:
```python
chain = prompt | llm | parser
```
The pipe operator composes components: prompt formats input → LLM generates response → parser extracts text string.

**`analyze_stock(ticker)`** — Ties it together: fetch data → format for prompt → invoke chain → return result.

---

## 🛠️ Key LangChain Concepts

### PromptTemplate
Templates separate instructions from data. Same template works for any ticker:
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a senior financial analyst..."),
    ("human", "Analyze {ticker} based on: {financial_data}")
])
```

### ChatAnthropic
Connects LangChain to Claude. `temperature=0` = factual, consistent output:
```python
llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0)
```

### LCEL (LangChain Expression Language)
Compose chains with `|` — like Unix pipes:
```python
chain = prompt | llm | StrOutputParser()
result = chain.invoke({"ticker": "AAPL", "financial_data": "..."})
```
LCEL chains automatically support `.stream()`, `.batch()`, and `.ainvoke()` for free.

---

## 🧪 Testing

| Ticker | Why | Expected |
|--------|-----|----------|
| AAPL | Stable large-cap | Clean summary, all metrics |
| TSLA | Volatile growth | Interesting analysis |
| JPM | Financial sector | Different metric focus |
| INVALID | Error case | Graceful failure |

```bash
# Test data layer
python stock_data.py

# Test full chain
echo "AAPL" | python simple_version.py
```

---

## 🎯 Challenges

1. **Modify the prompt** — Change the system message to "risk-focused analyst". How does output change?
2. **Try `temperature=0.7`** — Compare creative vs deterministic output
3. **Add a metric** — Add `"EarningsPerShareDiluted"` to `METRICS_TO_EXTRACT` in `stock_data.py`
4. **Remove the parser** — What does raw LLM output look like? (Hint: `AIMessage` object)
5. **Add streaming** — Change `chain.invoke()` to `chain.stream()` and print tokens as they arrive

---

## ✅ Completion Checklist

- [ ] Ran `python simple_version.py` with AAPL
- [ ] Ran `python stock_data.py` and saw real financial data
- [ ] Understand `prompt | llm | parser` (LCEL)
- [ ] Understand what `temperature=0` does
- [ ] Tried at least one challenge

---

## 📚 Resources

- [LangChain PromptTemplate Docs](https://python.langchain.com/docs/concepts/prompt_templates/)
- [ChatAnthropic Integration](https://python.langchain.com/docs/integrations/chat/anthropic/)
- [LCEL Guide](https://python.langchain.com/docs/concepts/lcel/)
- [SEC EDGAR API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)

---

**Next: [02 — Financial News Analyzer](../02-financial-news-analyzer) — chain multiple LLM calls together →**
