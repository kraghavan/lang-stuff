# 🎓 LangGraph Learning Guide

Complete this guide to build your first LangGraph application!

## 📚 What You're Building

An intelligent earnings analyzer that:
1. Fetches SEC data
2. Detects anomalies
3. **Investigates deeper if needed** (this is the LangGraph magic!)
4. Generates a report

## 🎯 Learning Objectives

By the end, you'll understand:
- ✅ How state flows through nodes
- ✅ How to build nodes (functions)
- ✅ How conditional routing works
- ✅ How loops enable iterative refinement
- ✅ When to use LangGraph vs LangChain

---

## 📝 TODO Checklist

### Phase 1: SEC API (sec_api.py)
- [ ] TODO 1: Implement `extract_revenue()`
- [ ] TODO 2: Implement `extract_net_income()`
- [ ] TODO 3: Complete `get_latest_metrics()`

### Phase 2: LangGraph Nodes (simple_version.py)
- [ ] TODO 4: Implement `extract_metrics()`
- [ ] TODO 5: Implement `compare_historical()`
- [ ] TODO 6: Complete `detect_anomalies()`
- [ ] TODO 7: Implement `investigate_anomaly()`
- [ ] TODO 8: Implement `generate_report()`

### Phase 3: Testing
- [ ] Run with a simple company (AAPL)
- [ ] Run with a volatile company (TSLA)
- [ ] Verify investigation loops work

---

## 🔧 Phase 1: SEC API

### TODO 1: Extract Revenue

**File**: `sec_api.py`  
**Function**: `extract_revenue()`

**What to do**:
Extract revenue data from the facts dictionary.

**Hints**:
```python
def extract_revenue(self, facts: Dict) -> List[Dict]:
    try:
        # Navigate to revenue data
        revenue_data = facts["facts"]["us-gaap"]["Revenues"]["units"]["USD"]
        
        # Filter to quarterly data
        quarterly = [
            item for item in revenue_data 
            if item.get("fp") in ["Q1", "Q2", "Q3", "Q4"]
        ]
        
        # Format nicely
        results = []
        for item in quarterly:
            results.append({
                "period": f"Q{item['fp'][1]} {item['fy']}",
                "value": item["val"],
                "date": item.get("filed", "")
            })
        
        # Sort by date (newest first)
        results.sort(key=lambda x: x["date"], reverse=True)
        
        return results
        
    except KeyError as e:
        print(f"Revenue data not found: {e}")
        return []
```

**Test it**:
```bash
python sec_api.py
```

---

### TODO 2: Extract Net Income

**File**: `sec_api.py`  
**Function**: `extract_net_income()`

**What to do**:
Similar to extract_revenue, but for net income.

**Hints**:
- Look for `"NetIncomeLoss"` instead of `"Revenues"`
- Same structure as revenue extraction
- Copy and modify the revenue function

**Code skeleton**:
```python
def extract_net_income(self, facts: Dict) -> List[Dict]:
    try:
        # Similar to revenue but use "NetIncomeLoss"
        income_data = facts["facts"]["us-gaap"]["NetIncomeLoss"]["units"]["USD"]
        
        # Rest is same as revenue extraction
        # ... copy logic from extract_revenue
        
    except KeyError as e:
        print(f"Net income data not found: {e}")
        return []
```

---

### TODO 3: Complete get_latest_metrics

**File**: `sec_api.py`  
**Function**: `get_latest_metrics()`

**What to do**:
Use your extraction functions to get the latest data.

**Code to complete**:
```python
def get_latest_metrics(self, ticker: str) -> Optional[Dict]:
    # ... (existing code above)
    
    # Extract metrics
    revenues = self.extract_revenue(facts)
    net_incomes = self.extract_net_income(facts)
    
    # Get most recent
    latest_revenue = revenues[0] if revenues else None
    latest_net_income = net_incomes[0] if net_incomes else None
    
    # Return structured data
    return {
        "ticker": ticker.upper(),
        "company_name": company_name,
        "cik": cik,
        "revenue": latest_revenue["value"] if latest_revenue else 0,
        "net_income": latest_net_income["value"] if latest_net_income else 0,
        "period": latest_revenue["period"] if latest_revenue else "Unknown",
        "filing_date": latest_revenue["date"] if latest_revenue else ""
    }
```

**Test Phase 1**:
```bash
python sec_api.py
# Should print Apple's latest metrics
```

---

## 🧩 Phase 2: LangGraph Nodes

### TODO 4: Extract Metrics

**File**: `simple_version.py`  
**Function**: `extract_metrics()`

**What to do**:
Pull metrics from state and format them.

**Code**:
```python
def extract_metrics(state: EarningsState) -> EarningsState:
    print("\n📊 Extracting financial metrics...")
    
    # Pull from current_metrics
    metrics = state['current_metrics']
    
    # Store in state for easy access
    state['revenue'] = metrics.get('revenue', 0)
    state['net_income'] = metrics.get('net_income', 0)
    state['period'] = metrics.get('period', 'Unknown')
    
    print(f"✓ Revenue: ${state['revenue']:,.0f}")
    print(f"✓ Net Income: ${state['net_income']:,.0f}")
    
    return state
```

**Note**: You'll need to add these keys to the EarningsState TypedDict:
```python
class EarningsState(TypedDict):
    # ... existing fields
    revenue: float
    net_income: float
```

---

### TODO 5: Compare Historical

**File**: `simple_version.py`  
**Function**: `compare_historical()`

**What to do**:
Fetch previous quarters and calculate changes.

**Code**:
```python
def compare_historical(state: EarningsState) -> EarningsState:
    print("\n🔎 Comparing to historical data...")
    
    # Get historical data from SEC
    cik = state['cik']
    facts = sec_client.get_company_facts(cik)
    
    if not facts:
        print("✗ Could not fetch historical data")
        return state
    
    # Extract historical revenue
    revenues = sec_client.extract_revenue(facts)
    
    # Get previous quarter (second in list since first is current)
    if len(revenues) > 1:
        current = revenues[0]['value']
        previous = revenues[1]['value']
        
        # Calculate change
        change = ((current - previous) / previous) * 100
        
        state['revenue_change'] = change
        print(f"✓ Revenue change: {change:+.1f}%")
    
    # Do the same for net income
    incomes = sec_client.extract_net_income(facts)
    if len(incomes) > 1:
        current = incomes[0]['value']
        previous = incomes[1]['value']
        change = ((current - previous) / previous) * 100
        
        state['net_income_change'] = change
        print(f"✓ Net income change: {change:+.1f}%")
    
    print("✓ Historical comparison complete")
    return state
```

**Update state**:
```python
class EarningsState(TypedDict):
    # ... existing fields
    revenue_change: float
    net_income_change: float
```

---

### TODO 6: Detect Anomalies

**File**: `simple_version.py`  
**Function**: `detect_anomalies()`

**What to do**:
Check each metric and flag large changes.

**Code**:
```python
def detect_anomalies(state: EarningsState) -> EarningsState:
    print("\n⚠️  Detecting anomalies...")
    
    anomalies = []
    THRESHOLD = 25  # 25% change is significant
    
    # Check revenue
    revenue_change = state.get('revenue_change', 0)
    if abs(revenue_change) > THRESHOLD:
        anomalies.append({
            "metric": "revenue",
            "change": revenue_change,
            "severity": "high" if abs(revenue_change) > 50 else "medium",
            "explained": False
        })
    
    # Check net income
    net_income_change = state.get('net_income_change', 0)
    if abs(net_income_change) > THRESHOLD:
        anomalies.append({
            "metric": "net_income",
            "change": net_income_change,
            "severity": "high" if abs(net_income_change) > 50 else "medium",
            "explained": False
        })
    
    state['anomalies'] = anomalies
    
    if anomalies:
        print(f"⚠️  Found {len(anomalies)} anomalies")
        for a in anomalies:
            print(f"  - {a['metric']}: {a['change']:+.1f}%")
    else:
        print("✓ No significant anomalies detected")
    
    return state
```

---

### TODO 7: Investigate Anomaly

**File**: `simple_version.py`  
**Function**: `investigate_anomaly()`

**What to do**:
Use Claude to find explanations for anomalies.

**Code**:
```python
def investigate_anomaly(state: EarningsState) -> EarningsState:
    print("\n🕵️  Investigating anomalies...")
    
    state['investigation_depth'] += 1
    
    # Get unexplained anomalies
    unexplained = [a for a in state['anomalies'] if not a.get('explained')]
    
    if not unexplained:
        print("✓ All anomalies explained")
        return state
    
    # Investigate each
    for anomaly in unexplained:
        prompt = f"""
        {state['company_name']}'s {anomaly['metric']} changed by {anomaly['change']:+.1f}%.
        This is a {anomaly['severity']} severity change.
        
        Period: {state['period']}
        
        Provide a brief (2-3 sentence) explanation for why this might have happened.
        Consider: market conditions, company strategy, industry trends.
        """
        
        response = llm.invoke(prompt)
        explanation = response.content
        
        state['investigation_results'].append(f"{anomaly['metric']}: {explanation}")
        anomaly['explained'] = True
        
        print(f"  ✓ Explained {anomaly['metric']} anomaly")
    
    print(f"✓ Investigation round {state['investigation_depth']} complete")
    return state
```

---

### TODO 8: Generate Report

**File**: `simple_version.py`  
**Function**: `generate_report()`

**What to do**:
Create a comprehensive report with Claude.

**Code**:
```python
def generate_report(state: EarningsState) -> EarningsState:
    print("\n📝 Generating report...")
    
    # Build context for Claude
    prompt = f"""
    Create a concise earnings analysis report for {state['company_name']} ({state['ticker']}).
    
    Period: {state['period']}
    
    Financial Metrics:
    - Revenue: ${state['revenue']:,.0f} ({state.get('revenue_change', 0):+.1f}% change)
    - Net Income: ${state['net_income']:,.0f} ({state.get('net_income_change', 0):+.1f}% change)
    
    Anomalies Detected: {len(state['anomalies'])}
    {chr(10).join([f"- {a['metric']}: {a['change']:+.1f}%" for a in state['anomalies']])}
    
    Investigations Conducted: {state['investigation_depth']}
    Findings:
    {chr(10).join([f"- {r}" for r in state['investigation_results']])}
    
    Write a 3-paragraph executive summary:
    1. Key metrics and performance
    2. Anomalies and explanations
    3. Overall assessment
    
    Be direct and data-driven. No preamble.
    """
    
    response = llm.invoke(prompt)
    state['final_report'] = response.content
    
    print("✓ Report generated")
    return state
```

---

## 🧪 Phase 3: Testing

### Test 1: Simple Company (No Anomalies)

```bash
python simple_version.py
```

Uncomment in `simple_version.py`:
```python
if __name__ == "__main__":
    analyze_earnings("AAPL", "Q4 2024", max_depth=2)
```

**Expected**: Should complete without deep investigation.

---

### Test 2: Volatile Company (With Anomalies)

```python
analyze_earnings("TSLA", "Q4 2024", max_depth=3)
```

**Expected**: Should detect anomalies and investigate them.

---

### Test 3: Verify Loops

**Check**: Does the graph loop back to investigate when needed?

**How to verify**:
- Look for `investigation_depth` increasing
- Should see "→ continuing investigation" messages
- Eventually should say "→ generating report"

---

## 🎓 Understanding LangGraph

### State Flow

```
Initial State → Node 1 → Modified State → Node 2 → More Modified → ...
```

Each node:
1. Receives current state
2. Does something
3. Returns modified state

### Routing Magic

```python
def should_investigate(state):
    if state['anomalies']:
        return "investigate"  # Go to investigate node
    else:
        return "report"  # Go to report node
```

This is what makes LangGraph powerful - **dynamic routing based on data**.

### Why Not LangChain?

LangChain: `fetch → analyze → report` (fixed path)

LangGraph: `fetch → analyze → need more info? → (yes: investigate → re-analyze) → report`

The ability to **loop back** and **branch conditionally** is the key difference!

---

## 🐛 Common Issues

**Issue**: "Module not found: langgraph"
**Fix**: `pip install -r requirements.txt`

**Issue**: "ANTHROPIC_API_KEY not set"
**Fix**: `export ANTHROPIC_API_KEY="your-key"`

**Issue**: "Ticker not found"
**Fix**: Use valid ticker (AAPL, MSFT, TSLA, etc.)

**Issue**: Node returns None
**Fix**: All nodes must `return state`

---

## ✅ Completion Checklist

You're done when:
- [ ] All TODOs are implemented
- [ ] Tests pass for AAPL
- [ ] Tests pass for TSLA
- [ ] You can explain how state flows
- [ ] You can explain why we use conditional edges
- [ ] You understand when to use LangGraph vs LangChain

---

## 🚀 Next Steps

After completing this:

1. **Add more metrics** - Operating expenses, margins, etc.
2. **Improve investigation** - Use web search for news context
3. **Add visualization** - Chart the metrics
4. **Build comparative version** - Compare two companies
5. **Move to loan approval** - Apply what you learned

---

## 💡 Key Takeaways

**LangGraph = State + Nodes + Conditional Routing + Loops**

- **State**: Shared data structure
- **Nodes**: Functions that process state
- **Edges**: Connections (simple or conditional)
- **Loops**: Enable iterative refinement

**When to use LangGraph**:
- ✅ Need to loop/iterate
- ✅ Different paths based on data
- ✅ Multiple agents coordinating
- ✅ Human-in-the-loop

**When to use LangChain**:
- Simple A → B → C flow
- Single-pass processing
- No branching needed

---

**Ready? Start with TODO 1 and work your way through! 🎯**

Questions? Issues? Check the example_outputs.md for expected results.