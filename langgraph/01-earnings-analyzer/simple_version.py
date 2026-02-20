"""
Earnings Analyzer - LangGraph Implementation

This is your first LangGraph application! It demonstrates:
- State management (shared data across nodes)
- Conditional routing (different paths based on data)
- Iterative loops (keep investigating until condition met)

Key LangGraph concepts:
- State: TypedDict that all nodes can access/modify
- Nodes: Functions that process state
- Edges: Connections between nodes (simple or conditional)
- Graph: The compiled workflow
"""

import os
from typing import TypedDict, Literal, List, Dict, Optional
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic

from sec_api import SECClient


# ==============================================================================
# STEP 1: Define State
# ==============================================================================

class EarningsState(TypedDict):
    """
    State that flows through all nodes in the graph.
    
    Think of this as a shared whiteboard that all nodes can read and write to.
    Each node receives the current state, processes it, and returns updated state.
    """
    
    # Input from user
    ticker: str
    period: str  # e.g., "Q4 2024"
    
    # Data fetched from SEC
    cik: Optional[str]
    company_name: Optional[str]
    current_metrics: Dict
    historical_metrics: List[Dict]
    
    # Analysis results
    anomalies: List[Dict]
    investigation_results: List[str]
    
    # Control flow
    investigation_depth: int
    max_depth: int
    
    # Output
    final_report: str


# ==============================================================================
# STEP 2: Initialize Tools
# ==============================================================================

# SEC API client for fetching data
sec_client = SECClient()

# Claude for analysis and report generation
llm = ChatAnthropic(
    model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


# ==============================================================================
# STEP 3: Define Nodes (Functions that process state)
# ==============================================================================

def fetch_company_data(state: EarningsState) -> EarningsState:
    """
    Node 1: Fetch company data from SEC.
    
    This node:
    1. Gets CIK from ticker
    2. Fetches latest metrics
    3. Updates state with results
    
    This is COMPLETE - you can use it as reference for other nodes.
    """
    print(f"\n📥 Fetching data for {state['ticker']}...")
    
    # Get CIK
    cik = sec_client.get_company_cik(state['ticker'])
    if not cik:
        raise ValueError(f"Could not find company {state['ticker']}")
    
    state['cik'] = cik
    
    # Get latest metrics
    metrics = sec_client.get_latest_metrics(state['ticker'])
    if metrics:
        state['company_name'] = metrics.get('company_name', 'Unknown')
        state['current_metrics'] = metrics
        print(f"✓ Found data for {state['company_name']}")
    else:
        print("✗ Could not fetch metrics")
    
    return state


def extract_metrics(state: EarningsState) -> EarningsState:
    """
    Node 2: Extract and structure financial metrics.
    
    TODO: Implement this node!
    
    Tasks:
    1. Get revenue, net income, expenses from state['current_metrics']
    2. Format them nicely
    3. Update state with structured data
    
    Hints:
    - Access data with state['current_metrics']
    - Create new keys in state like state['revenue'], state['net_income']
    - Print progress so user knows what's happening
    """
    print("\n📊 Extracting financial metrics...")
    
    # TODO: Extract metrics from state['current_metrics']
    # Example structure:
    # state['revenue'] = state['current_metrics'].get('revenue', 0)
    # state['net_income'] = state['current_metrics'].get('net_income', 0)
    
    print("✓ Metrics extracted")
    return state


def compare_historical(state: EarningsState) -> EarningsState:
    """
    Node 3: Compare current metrics to historical data.
    
    TODO: Implement this node!
    
    Tasks:
    1. Get historical data (previous quarters)
    2. Calculate percentage changes
    3. Identify which metrics changed significantly
    
    Hints:
    - Use sec_client to fetch historical data
    - Calculate: ((current - previous) / previous) * 100
    - Store results in state['historical_metrics']
    """
    print("\n🔎 Comparing to historical data...")
    
    # TODO: Fetch historical data
    # TODO: Calculate changes
    # TODO: Update state
    
    print("✓ Historical comparison complete")
    return state


def detect_anomalies(state: EarningsState) -> EarningsState:
    """
    Node 4: Detect unusual changes in metrics.
    
    This is PARTIALLY COMPLETE - finish the TODO sections.
    
    An anomaly is a metric that changed more than expected.
    For example: revenue dropped 30% or expenses increased 50%.
    """
    print("\n⚠️  Detecting anomalies...")
    
    anomalies = []
    
    # Define threshold for what counts as anomaly
    THRESHOLD = 25  # percent change
    
    # TODO: Check each metric for unusual changes
    # Example structure:
    # if abs(revenue_change) > THRESHOLD:
    #     anomalies.append({
    #         "metric": "revenue",
    #         "change": revenue_change,
    #         "severity": "high" if abs(revenue_change) > 50 else "medium"
    #     })
    
    state['anomalies'] = anomalies
    
    if anomalies:
        print(f"⚠️  Found {len(anomalies)} anomalies")
        for a in anomalies:
            print(f"  - {a['metric']}: {a['change']:+.1f}%")
    else:
        print("✓ No significant anomalies detected")
    
    return state


def investigate_anomaly(state: EarningsState) -> EarningsState:
    """
    Node 5: Investigate anomalies to find explanations.
    
    This uses Claude to search for context and explanations.
    
    TODO: Implement the investigation logic!
    
    Tasks:
    1. For each unexplained anomaly
    2. Use Claude to search for context (earnings calls, news, filings)
    3. Store explanations in state['investigation_results']
    """
    print("\n🕵️  Investigating anomalies...")
    
    state['investigation_depth'] += 1
    
    # Get unexplained anomalies
    unexplained = [a for a in state['anomalies'] if not a.get('explained')]
    
    if not unexplained:
        print("✓ All anomalies explained")
        return state
    
    # TODO: Use Claude to investigate each anomaly
    # Example:
    # for anomaly in unexplained:
    #     prompt = f"Explain why {state['company_name']}'s {anomaly['metric']} changed by {anomaly['change']}%"
    #     explanation = llm.invoke(prompt)
    #     state['investigation_results'].append(explanation)
    #     anomaly['explained'] = True
    
    print(f"✓ Investigation round {state['investigation_depth']} complete")
    return state


def generate_report(state: EarningsState) -> EarningsState:
    """
    Node 6: Generate final analysis report.
    
    TODO: Implement report generation using Claude!
    
    Tasks:
    1. Create a prompt with all the data
    2. Ask Claude to write a comprehensive report
    3. Store in state['final_report']
    
    Report should include:
    - Key metrics
    - Anomalies found
    - Explanations
    - Overall assessment
    """
    print("\n📝 Generating report...")
    
    # TODO: Build prompt with all state data
    # TODO: Call Claude to generate report
    # TODO: Store in state['final_report']
    
    # Example structure:
    # prompt = f"""
    # Analyze {state['company_name']}'s earnings:
    # 
    # Metrics: {state['current_metrics']}
    # Anomalies: {state['anomalies']}
    # Investigations: {state['investigation_results']}
    # 
    # Write a concise executive summary.
    # """
    
    state['final_report'] = "Report generation not yet implemented"
    
    print("✓ Report generated")
    return state


# ==============================================================================
# STEP 4: Define Routing Logic
# ==============================================================================

def should_investigate(state: EarningsState) -> Literal["investigate", "report"]:
    """
    Conditional routing: Decide whether to investigate further.
    
    This is COMPLETE - study how it works!
    
    This function determines which node to go to next:
    - If anomalies need investigation → go to "investigate" node
    - If done investigating → go to "report" node
    
    Returns:
        "investigate" or "report" (must match edge keys in graph)
    """
    
    # Check if we've hit max depth
    if state['investigation_depth'] >= state['max_depth']:
        print(f"→ Max investigation depth ({state['max_depth']}) reached, generating report")
        return "report"
    
    # Check if there are unexplained anomalies
    unexplained = [a for a in state['anomalies'] if not a.get('explained')]
    
    if unexplained:
        print(f"→ {len(unexplained)} unexplained anomalies, continuing investigation")
        return "investigate"
    else:
        print("→ All anomalies explained, generating report")
        return "report"


# ==============================================================================
# STEP 5: Build the Graph
# ==============================================================================

def create_earnings_analyzer() -> StateGraph:
    """
    Build the LangGraph workflow.
    
    This is PARTIALLY COMPLETE - study the structure!
    
    The graph looks like this:
    
    START
      ↓
    fetch_data
      ↓
    extract_metrics
      ↓
    compare_historical
      ↓
    detect_anomalies
      ↓
    (decision: investigate?)
      ├─ yes → investigate_anomaly → (loop back to decision)
      └─ no → generate_report → END
    """
    
    # Create graph with our state type
    workflow = StateGraph(EarningsState)
    
    # Add all nodes
    workflow.add_node("fetch_data", fetch_company_data)
    workflow.add_node("extract_metrics", extract_metrics)
    workflow.add_node("compare_historical", compare_historical)
    workflow.add_node("detect_anomalies", detect_anomalies)
    workflow.add_node("investigate", investigate_anomaly)
    workflow.add_node("generate_report", generate_report)
    
    # Set entry point
    workflow.set_entry_point("fetch_data")
    
    # Add simple edges (always go to next node)
    workflow.add_edge("fetch_data", "extract_metrics")
    workflow.add_edge("extract_metrics", "compare_historical")
    workflow.add_edge("compare_historical", "detect_anomalies")
    
    # Add conditional edge (routing based on state)
    workflow.add_conditional_edges(
        "detect_anomalies",  # From this node
        should_investigate,   # Use this function to decide
        {
            "investigate": "investigate",  # If returns "investigate", go here
            "report": "generate_report"    # If returns "report", go here
        }
    )
    
    # After investigation, check again if we should continue
    workflow.add_conditional_edges(
        "investigate",
        should_investigate,
        {
            "investigate": "investigate",  # Loop back if more investigation needed
            "report": "generate_report"
        }
    )
    
    # Final node goes to END
    workflow.add_edge("generate_report", END)
    
    return workflow


# ==============================================================================
# STEP 6: Main Function
# ==============================================================================

def analyze_earnings(ticker: str, period: str = "Q4 2024", max_depth: int = 2):
    """
    Run the earnings analysis workflow.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL", "TSLA")
        period: Period to analyze (e.g., "Q4 2024")
        max_depth: Maximum investigation loops
    """
    
    print("="*60)
    print("🔍 SEC EARNINGS ANALYZER")
    print("="*60)
    
    # Create the workflow
    workflow = create_earnings_analyzer()
    
    # Compile it into a runnable app
    app = workflow.compile()
    
    # Create initial state
    initial_state: EarningsState = {
        "ticker": ticker,
        "period": period,
        "cik": None,
        "company_name": None,
        "current_metrics": {},
        "historical_metrics": [],
        "anomalies": [],
        "investigation_results": [],
        "investigation_depth": 0,
        "max_depth": max_depth,
        "final_report": ""
    }
    
    # Run the workflow
    try:
        print(f"\nAnalyzing {ticker} for {period}...")
        final_state = app.invoke(initial_state)
        
        # Print results
        print("\n" + "="*60)
        print("📊 ANALYSIS COMPLETE")
        print("="*60)
        print(f"\nCompany: {final_state['company_name']}")
        print(f"Investigation Depth: {final_state['investigation_depth']}")
        print(f"\n{final_state['final_report']}")
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


# ==============================================================================
# STEP 7: Run It!
# ==============================================================================

if __name__ == "__main__":
    """
    Test the analyzer.
    
    TODO: Once you've implemented the missing functions, uncomment and run!
    """
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)
    
    # Run analysis
    # Uncomment this when you're ready to test:
    # analyze_earnings("AAPL", "Q4 2024", max_depth=2)
    
    # For now, just test the structure
    print("✓ Code structure is valid")
    print("\nTODO: Implement the missing functions:")
    print("  1. extract_metrics()")
    print("  2. compare_historical()")
    print("  3. detect_anomalies() - finish implementation")
    print("  4. investigate_anomaly()")
    print("  5. generate_report()")
    print("\nThen uncomment the analyze_earnings() call above and run!")


# ==============================================================================
# LEARNING CHECKPOINTS
# ==============================================================================

"""
🎓 What you should understand after completing this:

1. STATE MANAGEMENT
   - State is a TypedDict shared across all nodes
   - Each node receives state, modifies it, returns it
   - State flows through the graph like water through pipes

2. NODES
   - Nodes are just Python functions
   - They take state as input, return state as output
   - Do one thing and do it well

3. EDGES
   - Simple edges: always go to next node
   - Conditional edges: use a function to decide where to go
   - Can create loops by routing back to earlier nodes

4. ROUTING
   - Routing functions return strings that match edge keys
   - Enable different paths through the graph based on data
   - Critical for adaptive/intelligent workflows

5. WHY LANGGRAPH?
   - LangChain: A → B → C (fixed path)
   - LangGraph: A → B → (is it good? → C : back to B) (adaptive)

Next steps:
- Implement the TODOs
- Test with different companies
- Add more metrics to analyze
- Visualize the graph with Mermaid
"""