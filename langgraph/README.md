# LangGraph Examples

Complex agentic workflows that require loops, branches, state management, and tool use. Designed for **software engineers** learning production AI patterns.

## When to Use LangGraph (vs LangChain)

Use LangGraph when you need:
- ✅ **Loops** - "Keep investigating until we find the answer"
- ✅ **Conditional routing** - "If risk is high, take path A, else path B"
- ✅ **Tool calling** - Agent decides which tools to use based on context
- ✅ **Shared state** - Multiple agents accessing/updating the same data
- ✅ **Multi-agent coordination** - Agents that interact with each other
- ✅ **Human-in-the-loop** - Pause for human approval/input
- ✅ **Self-correction** - Retry until output meets quality threshold

Use LangChain instead when:
- ❌ Simple linear flow: A → B → C
- ❌ Single-pass processing
- ❌ No need to revisit previous steps
- ❌ No conditional logic needed

## Examples in This Directory

We progress from simple state management to advanced multi-agent systems. Each example teaches a **fundamentally different LangGraph pattern** — no redundancy.

---

### 1. 🔄 CI/CD Status Tracker
**Level**: 🟢 BEGINNER  
**Pattern**: Basic state management with linear flow

```
Trigger build → Run tests → Deploy to staging → Run smoke tests → Deploy to prod
         ↓           ↓              ↓                  ↓                ↓
    (update state at each step)
```

**What you'll learn**:
- Basic `TypedDict` state definition
- Simple node functions that modify state
- Linear edges (no conditionals)
- Entry point and END
- How state flows through a graph

**Why this example**:
- Every SWE understands CI/CD
- Simple enough to grasp LangGraph basics
- Real-world relevant (deployment pipelines)
- No complex logic to distract from core concepts

**Use cases**:
- Build pipeline tracking
- Deployment status monitoring
- Sequential task execution
- Any linear workflow with state

[See full example →](./01-ci-cd-tracker)

---

### 2. 🚨 Fraud Detection System
**Level**: 🟡 INTERMEDIATE  
**Pattern**: Multi-path conditional routing

```
Transaction → Extract patterns → Calculate suspicion score
                                         ↓
                              ┌──────────┼──────────┐
                              ↓          ↓          ↓
                        (low risk)  (medium)   (high risk)
                              ↓          ↓          ↓
                          Approve   Investigate   Block
```

**What you'll learn**:
- Conditional edges (`add_conditional_edges`)
- Routing functions that return edge keys
- Multi-path branching based on computed values
- Pattern matching and risk scoring
- Different code paths for different scenarios

**Why this example**:
- Clear decision tree logic
- Multiple fraud indicators (velocity, location, amount)
- Real production pattern (every fintech uses this)
- Shows when LangGraph beats simple chains

**Use cases**:
- Risk-based routing (approvals, escalations)
- Triage systems (support tickets, bug reports)
- Content moderation (safe/review/block)
- Any workflow where different inputs need different handling

[See full example →](./02-fraud-detection)

---

### 3. 🛠️ DevOps Troubleshooting Agent (Deep Agent)
**Level**: 🟡 INTERMEDIATE  
**Pattern**: Tool-calling with ReAct (Reason + Act) loop

```
User: "Why is the API slow?"
    ↓
Agent: "I should check logs first"
    ↓ (calls check_logs tool)
Result: "High DB query times"
    ↓
Agent: "I should check database metrics"
    ↓ (calls query_database tool)
Result: "Missing index on users table"
    ↓
Agent: "Found issue! Missing index causing slow queries"
    ↓
END
```

**What you'll learn**:
- **Tool calling** - Agent has access to multiple tools
- **ReAct pattern** - Reason about what to do → Act (use tool) → Observe → Repeat
- **Agentic behavior** - Agent decides its own path, not hardcoded
- **Loop until solved** - Keep using tools until problem found
- **Tool observation** - Agent sees tool results and decides next action

**Why this example (CRITICAL)**:
- **This IS "deep agents"** - the foundation of agentic AI
- AutoGPT, Devin, most "AI agents" use this exact pattern
- Shows true autonomy (agent picks tools, not hardcoded)
- Production-critical (DevOps, debugging, investigation)

**What is a "Deep Agent"?**:
A "deep agent" is an AI that:
1. Has access to multiple tools (search, APIs, databases, shell commands)
2. **Decides which tool to use** based on context (not hardcoded)
3. Observes tool results
4. **Iteratively chooses next tool** until task complete
5. Can fail, backtrack, and try different approaches

This is opposed to "shallow agents" (hardcoded tool sequences) or simple chains (no tool choice).

**Use cases**:
- Debugging assistants (check logs → query DB → test endpoint)
- DevOps automation (diagnose → remediate → verify)
- Research assistants (search → read → extract → search more)
- API integration testing (call endpoint → parse → retry with different params)
- Any task requiring multi-step investigation with tool use

[See full example →](./03-devops-agent)

---

### 4. 🗄️ Database Migration Approval
**Level**: 🟠 ADVANCED  
**Pattern**: Human-in-the-loop (HITL) with interrupts

```
Analyze schema → Generate migration plan
    ↓
    INTERRUPT ⏸️ (pause for human review)
    ↓
Human reviews plan:
    ├─ Approve → Execute migration → Verify → END
    └─ Reject → Revise plan → INTERRUPT again ⏸️
```

**What you'll learn**:
- **Interrupt nodes** - Pause graph execution
- **State persistence** - Save state while waiting
- **Resume from checkpoint** - Continue after human input
- **Approval gates** - Critical for production AI
- **Feedback loops** - Human can reject and request changes

**Why this example (CRITICAL FOR PRODUCTION)**:
- **You cannot ship AI without human oversight** for critical actions
- Legal/compliance often requires human approval
- Shows responsible AI deployment
- Production requirement for high-stakes decisions

**Use cases**:
- Code deployment (AI generates → human approves → deploy)
- Database changes (AI plans → DBA reviews → execute)
- Financial transactions (AI suggests → manager approves)
- Security patches (AI detects → engineer approves fix)
- Any high-stakes action requiring human judgment

[See full example →](./04-migration-approval)

---

### 5. 💼 Algorithmic Trading Team
**Level**: 🔴 MOST ADVANCED
**Pattern**: Multi-agent system with conflict resolution and veto power

```
                    Portfolio Manager
                    (Supervisor Agent)
                           |
            ┌──────────────┼──────────────┐
            ↓              ↓              ↓
     Market Analysis   Risk Management  Compliance
     Agent             Agent             Agent
     "Find             "Assess           "Verify
      opportunities"    portfolio risk"   regulatory limits"
            ↓              ↓              ↓
            └──────────────┼──────────────┘
                           ↓
                    Portfolio Manager
                 (negotiate or execute)
```

**What you'll learn**:
- **Multiple specialized agents** with competing objectives
- **Supervisor pattern** - Portfolio Manager delegates to specialists
- **Veto power** - Risk and Compliance agents can block trades
- **Negotiation loops** - If blocked, try alternatives until consensus
- **Shared state** - All agents read/write the same TradingState
- **Conflict resolution** - Agents disagree, supervisor mediates

**Why this example**:
- Most complex LangGraph pattern
- Agents **disagree** with each other (not just sequential)
- Real production pattern (hedge fund trading desks work this way)
- Combines EVERY pattern from examples 01-04

**Use cases**:
- Trading desks (market + risk + compliance must agree)
- Incident response (triage + investigation + communication agents)
- Hiring pipelines (recruiter + technical + culture fit agents)
- Content moderation (safety + quality + policy agents)
- Any task requiring multiple specialized perspectives with veto power

[See full example →](./05-trading-team)

---

## 📊 Pattern Comparison

| Pattern | Example | When to Use | Complexity |
|---------|---------|-------------|------------|
| **Linear State** | CI/CD Tracker | Sequential tasks, no branching | ⭐ |
| **Conditional Routing** | Fraud Detection | Different paths based on data | ⭐⭐ |
| **Tool Calling (ReAct)** | DevOps Agent | Agent picks tools iteratively | ⭐⭐⭐ |
| **Human-in-Loop** | Migration Approval | Need human judgment | ⭐⭐⭐⭐ |
| **Multi-Agent** | Trading Team | Multiple agents with veto + negotiation | ⭐⭐⭐⭐⭐ |

---

## 🎓 Learning Path

```
Step 1: CI/CD Tracker
├─ Learn state basics
├─ Understand nodes and edges
└─ Build first graph

Step 2: Fraud Detection
├─ Add conditional routing
├─ Learn routing functions
└─ Handle multiple paths

Step 3: DevOps Agent ⭐ (This is "Deep Agents")
├─ Add tool calling
├─ Learn ReAct pattern
├─ Agent autonomy
└─ Iterative problem solving

Step 4: Migration Approval
├─ Add human oversight
├─ Learn interrupts
├─ State persistence
└─ Approval workflows

Step 5: Trading Team
├─ Multiple agents with veto power
├─ Supervisor coordination
├─ Negotiation loops (block → alternative → re-check)
└─ Conflict resolution + complex state

✅ You now understand production LangGraph patterns
```

---

## 🚀 Quick Start

```bash
# Choose an example (start with 01)
cd 01-ci-cd-tracker

# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Run it
python main.py
```

---

## 🔑 Key LangGraph Concepts

### State
Shared data structure passed between all nodes:
```python
from typing import TypedDict, Annotated
from langgraph.graph import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # Conversation history
    current_step: str                        # What we're doing
    tools_used: list[str]                    # Which tools called
    result: dict                             # Final output
```

### Nodes
Functions that process and modify state:
```python
def analyze_issue(state: AgentState) -> AgentState:
    """Node that processes state and returns updated state."""
    issue = state["current_issue"]
    analysis = llm.invoke(f"Analyze: {issue}")
    
    state["analysis_result"] = analysis
    state["current_step"] = "analysis_complete"
    
    return state
```

### Edges
Connections between nodes:
```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)

# Simple edge: always go to next node
workflow.add_edge("analyze", "report")

# Conditional edge: route based on state
workflow.add_conditional_edges(
    "analyze",
    should_continue,  # Function that returns edge key
    {
        "continue": "investigate",
        "finish": END
    }
)
```

### Tools (for Tool-Calling Agents)
Functions the agent can call:
```python
from langchain_core.tools import tool

@tool
def check_logs(service: str, hours: int = 1) -> str:
    """Check logs for a service in the last N hours."""
    # Implementation here
    return f"Logs for {service}: ..."

@tool  
def query_database(query: str) -> str:
    """Execute a SQL query and return results."""
    # Implementation here
    return "Results: ..."

tools = [check_logs, query_database]
```

### Compilation
Turn graph into runnable application:
```python
# Compile the graph
app = workflow.compile()

# Run it
initial_state = {
    "messages": [],
    "current_step": "start"
}

result = app.invoke(initial_state)
```

### Interrupts (for Human-in-the-Loop)
Pause execution for human input:
```python
# When compiling, specify interrupt points
app = workflow.compile(interrupt_before=["human_review"])

# Run until interrupt
result = app.invoke(initial_state)

# Human reviews and provides input
approved = input("Approve? (yes/no): ")

# Resume from checkpoint
if approved == "yes":
    final_result = app.invoke(None)  # Resumes from last state
```

---

## 💡 Common Patterns Across Examples

All examples demonstrate:
- **State management** - Shared data structure across nodes
- **Node design** - Pure functions that transform state
- **Edge logic** - When to move to next node
- **Error handling** - Graceful failures and retries
- **Logging** - Track what the graph is doing
- **Testing** - How to test nodes independently

---

## 🎯 When to Use Each Pattern

### Use Linear State (Example 1) when:
- ✅ Tasks happen in fixed sequence
- ✅ No branching needed
- ✅ Simple status tracking
- ✅ Learning LangGraph basics

### Use Conditional Routing (Example 2) when:
- ✅ Different inputs need different handling
- ✅ Risk-based decision making
- ✅ Triage workflows
- ✅ Multiple possible outcomes

### Use Tool Calling (Example 3) when:
- ✅ Agent needs to choose actions dynamically
- ✅ Multiple tools available
- ✅ Iterative problem solving
- ✅ Investigation/debugging workflows
- ✅ **Building "deep agents" / autonomous agents**

### Use Human-in-Loop (Example 4) when:
- ✅ High-stakes decisions require approval
- ✅ Legal/compliance requires human oversight
- ✅ AI needs human expertise for edge cases
- ✅ Production deployment workflows

### Use Multi-Agent (Example 5) when:
- ✅ Task requires multiple specialized skills
- ✅ Different perspectives needed
- ✅ Complex coordination required
- ✅ Scaling beyond single-agent capabilities

---

## 🔬 What Are "Deep Agents"?

**"Deep agents"** (also called **agentic AI** or **autonomous agents**) refers to AI systems that:

1. **Have agency** - Make their own decisions about what to do next
2. **Use tools** - Can call functions, APIs, databases, etc.
3. **Reason iteratively** - Think → Act → Observe → Think → Act (ReAct loop)
4. **Adapt to results** - Change strategy based on what tools return
5. **Solve complex tasks** - Chain together multiple tool uses

**This is Example 3 (DevOps Agent)** - the ReAct pattern with tool calling.

**Contrast with "shallow" approaches**:
- ❌ Hardcoded tool sequences (not adaptive)
- ❌ Single LLM call (no iteration)
- ❌ Pre-defined workflows (no agency)

**Famous examples of deep agents**:
- AutoGPT (research → code → debug loop)
- Devin (software engineer agent)
- Browser automation agents
- DevOps agents

**Key insight**: Deep agents are just **LangGraph with tool calling and loops**. Example 3 teaches this pattern.

---

## 🛠️ Tips for Building LangGraph Applications

### Design
1. **Start with state** - What data do you need to track?
2. **Map the flow** - Draw boxes (nodes) and arrows (edges) on paper
3. **Identify conditionals** - Where do you branch? What decides the path?
4. **Plan loops** - What's the exit condition? How do you avoid infinite loops?
5. **Consider HITL** - What decisions need human judgment?

### Development
1. **Build incrementally** - Start with 2 nodes, add complexity
2. **Test nodes alone** - Each node should work independently
3. **Print state liberally** - Watch how state changes through the graph
4. **Use type hints** - TypedDict makes debugging easier
5. **Handle errors** - Nodes should catch exceptions and update state

### Debugging
1. **Visualize the graph** - Use `mermaid` to draw it
2. **Log each transition** - Print which edge was taken and why
3. **Inspect state at each node** - Use `print(state)` generously
4. **Test routing functions** - Make sure conditionals route correctly
5. **Check for infinite loops** - Always have exit conditions

### Production
1. **Add checkpointing** - Save state for long-running workflows
2. **Implement retries** - Handle transient failures
3. **Add monitoring** - Track which paths are taken
4. **Version your graphs** - Graph structure is code, version it
5. **Test edge cases** - What happens if a tool fails?

---

## 📚 Resources

**Official Documentation**:
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)
- [LangGraph Tutorials](https://langchain-ai.github.io/langgraph/tutorials/)

**Key Concepts**:
- [StateGraph](https://langchain-ai.github.io/langgraph/concepts/low_level/#stategraph)
- [Conditional Edges](https://langchain-ai.github.io/langgraph/how-tos/branching/)
- [Human-in-the-Loop](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/breakpoints/)
- [Tool Calling](https://langchain-ai.github.io/langgraph/how-tos/tool-calling/)
- [Multi-Agent Systems](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)

**Patterns**:
- [ReAct Pattern](https://react-lm.github.io/)
- [Plan-and-Execute](https://langchain-ai.github.io/langgraph/tutorials/plan-and-execute/)
- [Agent Supervisor](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/)

---

## 🎯 Next Steps

1. **Start with Example 1** (CI/CD Tracker) - Get comfortable with basics
2. **Build Example 2** (Fraud Detection) - Add conditional logic
3. **Master Example 3** (DevOps Agent) - This is "deep agents" / true agentic AI ⭐
4. **Add Example 4** (Migration Approval) - Critical for production
5. **Cap with Example 5** (Trading Team) - Show off your skills

After completing all 5, you'll understand:
- ✅ All core LangGraph patterns
- ✅ When to use LangGraph vs LangChain
- ✅ How to build production-ready agentic systems
- ✅ Deep agents (ReAct + tool calling)
- ✅ Multi-agent architectures

---

**Ready to build? Start with [CI/CD Status Tracker](./01-ci-cd-tracker) →**
