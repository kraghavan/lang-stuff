# 📈 Learning Guide: Stock Summary Generator

A walkthrough of your first LangChain application. All code is **complete and ready to run** — this guide explains how each piece works and gives you challenges to deepen your understanding.

## Prerequisites

- Python 3.10+ installed
- `ANTHROPIC_API_KEY` environment variable set
- Basic Python knowledge (functions, dictionaries, f-strings)
- No LangChain experience needed!

## How to Use This Guide

1. **Run the code first** — `python simple_version.py`, enter `AAPL`
2. **Read each section below** — understand what each function does and why
3. **Try the challenges** at the end of each section
4. **Check the completion checklist** at the bottom

---

## Phase 1: Data Layer (`stock_data.py`)

Open `stock_data.py` and follow along.

### Step 1: `get_company_cik()` — Ticker to CIK Lookup

The SEC identifies companies by CIK (Central Index Key), not ticker symbols. This function converts "AAPL" → "0000320193".

**How it works:**
1. Makes a GET request to `https://www.sec.gov/files/company_tickers.json`
2. The response is a JSON dict of all public companies
3. Loops through values, finds matching ticker (case-insensitive)
4. Returns the CIK zero-padded to 10 digits: `str(cik).zfill(10)`

**Key detail:** SEC requires a `User-Agent` header on all requests. Without it, you get a 403 error.

**Test it:**
```bash
python -c "from stock_data import get_company_cik; print(get_company_cik('AAPL'))"
# Expected: 0000320193
```

**Challenge:** Try looking up `TSLA`, `MSFT`, and `GOOGL`. What CIK does each return?

---

### Step 2: `get_financial_facts()` — Fetch Raw SEC Data

This function fetches ALL financial data a company has ever reported in XBRL format.

**How it works:**
1. Builds URL: `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json`
2. Makes GET request with the required `User-Agent` header
3. Returns the full JSON response (can be very large!)

**Key detail:** The response structure is deeply nested:
```
facts → "facts" → "us-gaap" → concept_name → "units" → "USD" → [list of filings]
```

**Challenge:** Run this and explore the keys — what financial concepts does Apple report?
```python
python -c "
from stock_data import get_company_cik, get_financial_facts
facts = get_financial_facts(get_company_cik('AAPL'))
concepts = list(facts['facts']['us-gaap'].keys())
print(f'{len(concepts)} concepts. First 10: {concepts[:10]}')
"
```

---

### Step 3: `extract_metric()` — Parse Specific Metrics

This is the trickiest function — it navigates the nested SEC data to find the most recent value for a specific metric.

**How it works:**
1. Tries each concept name in order (e.g., "Revenues" first, then the longer alternative)
2. Navigates to `facts["facts"]["us-gaap"][concept]["units"]["USD"]`
3. Filters for 10-K or 10-Q filings only
4. Sorts by end date (most recent first)
5. Returns the latest entry as a clean dict

**Why try multiple concept names?** Companies use different XBRL names. Apple uses `"Revenues"` but others might use `"RevenueFromContractWithCustomerExcludingAssessedTax"`.

**Challenge:** Add a new metric! Try extracting `"EarningsPerShareDiluted"` by adding it to `METRICS_TO_EXTRACT`.

---

### Step 4: `get_stock_data()` — The Main Entry Point

This convenience function ties everything together: CIK lookup → fetch facts → extract each metric → format numbers.

**Test the complete flow:**
```bash
python stock_data.py
# Should print AAPL's financial metrics with formatted numbers
```

---

## Phase 2: LangChain Chain (`simple_version.py`)

Open `simple_version.py` and follow along. This is where LangChain comes in.

### Step 5: `create_analysis_prompt()` — PromptTemplate

**Concept: ChatPromptTemplate**

Templates separate your instructions from your data. The same template works for any ticker — you just swap the variables.

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a senior financial analyst..."),
    ("human", "Analyze {ticker} ({company_name}) based on: {financial_data}")
])
```

**How it works:**
- `("system", "...")` — Sets Claude's role and behavior
- `("human", "...")` — The actual request with `{placeholders}`
- Placeholders like `{ticker}` are filled when you call `chain.invoke({"ticker": "AAPL", ...})`

**Challenge:** Modify the system prompt to make Claude respond as a "risk-focused analyst" instead. How does the output change?

---

### Step 6: `create_llm()` — ChatAnthropic

**Concept: LLM Connection**

`ChatAnthropic` connects LangChain to Claude:

```python
llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0, max_tokens=1024)
```

- **`temperature=0`** — Deterministic output. Same input = same output. Good for financial analysis.
- **`max_tokens=1024`** — Caps response length. Prevents runaway responses.

**Challenge:** Try `temperature=0.7` — how does the output change? (More creative but less consistent.)

---

### Step 7: `create_summary_chain()` — LCEL (The Pipe Operator)

**Concept: LangChain Expression Language (LCEL)**

This is the core pattern of LangChain:

```python
chain = prompt | llm | parser
```

The `|` operator composes components:
1. **prompt** formats input dict → list of messages
2. **llm** sends messages to Claude → AIMessage response
3. **parser** extracts AIMessage.content → plain string

It's like Unix pipes: each component transforms data and passes it to the next.

**Why this matters:** LCEL chains automatically support streaming (`chain.stream()`), batching (`chain.batch()`), and async (`await chain.ainvoke()`) — for free.

**Challenge:** Remove the `StrOutputParser` and run the chain. What does the raw LLM output look like? (Hint: it's an `AIMessage` object, not a string.)

---

### Step 8: `analyze_stock()` — Putting It Together

This function:
1. Fetches data from SEC EDGAR
2. Formats metrics into a readable string
3. Creates the chain and invokes it with the data
4. Returns the analysis

**Challenge:** Add a timer to measure how long each step takes:
```python
import time
start = time.time()
# ... step ...
print(f"Step took {time.time() - start:.1f}s")
```

---

## Phase 3: Testing & Exploration

### Test 1: Simple Company
```bash
python simple_version.py  # Enter: AAPL
```

### Test 2: Volatile Company
```bash
python simple_version.py  # Enter: TSLA
```

### Test 3: Error Handling
```bash
python simple_version.py  # Enter: INVALIDTICKER
```

### Test 4: Explore the Chain Internals
Add debug prints to see what happens at each step:

```python
# In create_summary_chain(), try:
prompt = create_analysis_prompt()
messages = prompt.format_messages(ticker="AAPL", company_name="Apple", financial_data="Revenue: $391B")
print("Messages:", messages)
```

---

## Understanding LCEL

### What Is It?

LangChain Expression Language is the modern way to compose chains. Instead of the old `LLMChain` class, you use `|`:

```python
# Old way (deprecated)
chain = LLMChain(llm=llm, prompt=prompt, output_parser=parser)

# New way (LCEL) ✅
chain = prompt | llm | parser
```

### How the Pipe Works

Each component is a "Runnable" with `.invoke()`, `.batch()`, and `.stream()` methods:

```
Input dict ──► prompt.invoke() ──► Messages ──► llm.invoke() ──► AIMessage ──► parser.invoke() ──► str
```

---

## Bonus Challenges

1. **Add a new metric**: Edit `METRICS_TO_EXTRACT` in `stock_data.py` to include `EarningsPerShareDiluted`
2. **Change the output format**: Modify the prompt to ask for JSON output instead of prose
3. **Use JsonOutputParser**: Replace `StrOutputParser` with `JsonOutputParser` and ask Claude to return structured JSON
4. **Add streaming**: Change `chain.invoke()` to `chain.stream()` and print tokens as they arrive
5. **Compare companies**: Modify `main()` to accept two tickers and generate a comparison

---

## Completion Checklist

- [ ] Ran `python simple_version.py` with AAPL successfully
- [ ] Ran `python stock_data.py` and saw real financial data
- [ ] Understand how `ChatPromptTemplate` uses placeholders
- [ ] Understand what `temperature=0` means for output consistency
- [ ] Understand the LCEL chain: `prompt | llm | parser`
- [ ] Understand how `chain.invoke({"key": "value"})` fills placeholders
- [ ] Tried at least one bonus challenge

## What's Next?

**[02 - Financial News Analyzer](../02-financial-news-analyzer)** — Learn to chain multiple LLM calls together, where the output of one step feeds into the next.

---

**Concepts Learned:**
- ✅ PromptTemplate
- ✅ ChatAnthropic
- ✅ StrOutputParser
- ✅ LCEL (pipe operator)
- ✅ chain.invoke()
