# 🛠️ DevOps Troubleshooting Agent

A "deep agent" that autonomously investigates infrastructure issues using the **ReAct pattern** (Reason + Act). The agent chooses which tools to use, observes results, and iteratively solves problems. All code is **complete and ready to run**.

## 🎯 What It Does

Given a problem like *"The /api/v2/users endpoint is timing out"*, the agent:

1. **Thinks** — "I should check the API gateway logs first"
2. **Acts** — Calls `check_logs("api-gateway")`
3. **Observes** — Sees timeout errors, slow upstream responses
4. **Thinks** — "The user-service is slow. Let me check its logs"
5. **Acts** — Calls `check_logs("user-service")`
6. **Observes** — Sees slow database queries (25s+)
7. **Thinks** — "Database issue. Let me check for missing indexes"
8. **Acts** — Calls `query_database("missing_indexes")`
9. **Observes** — Missing index on `users.email`
10. **Concludes** — "Root cause: missing index. Recommending fix."

This is **true agentic behavior** — the agent decides its own investigation path.

## 🌟 Why This Is "Deep Agents"

A "deep agent" (agentic AI) is an AI that:
1. Has access to **multiple tools** (logs, metrics, DB, endpoints, remediation)
2. **Decides which tool to use** based on context (not hardcoded)
3. **Observes tool results** and reasons about them
4. **Iteratively chooses next actions** until the task is complete
5. Can **fail, backtrack, and try different approaches**

This is the same pattern behind AutoGPT, Devin, and most production AI agents.

**Contrast with "shallow" approaches:**
- Simple chain: hardcoded sequence, no adaptation
- Single LLM call: no tool use, no iteration
- Rule-based: predefined paths, no reasoning

## 📁 Files

```
03-devops-agent/
├── README.md          # This file
├── main.py            # ReAct agent implementation
├── tools.py           # 5 simulated DevOps tools
└── test_agent.py      # Tests (tools work offline, agent needs API key)
```

## 🚀 Quick Start

```bash
cd langgraph/03-devops-agent
pip install -r ../requirements.txt
export ANTHROPIC_API_KEY="your-key-here"

python main.py                                              # Default issue
python main.py "The payments endpoint is returning errors"   # Custom issue
```

## 🏗️ Architecture: The ReAct Loop

```
START → Agent (LLM thinks) → [has tool call?]
              ↑                     │
              │               yes   │   no
              │                ↓    │    ↓
              │            Tools    │   END
              │          (execute)  │
              └────────────────────┘
                    (loop back)
```

`create_react_agent()` builds this entire graph for you:

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model=llm,           # Claude decides what to do
    tools=devops_tools,  # 5 tools the agent can call
    prompt=system_prompt, # Instructions for the agent
)

result = agent.invoke({"messages": [("human", "Why is the API slow?")]})
```

## 🛠️ Available Tools

| Tool | What It Does | When Agent Uses It |
|------|-------------|-------------------|
| `check_logs` | View recent logs for any service | First step — find errors/warnings |
| `check_metrics` | CPU, memory, disk, connections | When logs suggest resource issues |
| `query_database` | Slow queries, missing indexes, table stats | When logs show DB problems |
| `test_endpoint` | Test API endpoints | Confirm which endpoints are affected |
| `run_remediation` | Create indexes, vacuum tables, restart services | After identifying root cause |

Each tool has a **docstring that Claude reads** to decide when to use it:

```python
@tool
def check_logs(service: str, lines: int = 5) -> str:
    """Check recent logs for a service. Use this to find errors, warnings, and patterns."""
```

---

## 📖 Code Walkthrough

### `tools.py` — Tool Definitions

Each tool is a `@tool`-decorated function with:
- **Typed parameters** — Claude sees the types and descriptions
- **Docstring** — Claude reads this to decide WHEN to use the tool
- **Simulated responses** — Returns realistic data without real infrastructure

The tools use `_SIMULATED_LOGS`, `_SIMULATED_METRICS`, etc. — dictionaries that mimic real infrastructure. In production, these would call actual APIs.

### `main.py` — The Agent

**`create_devops_agent()`** — Uses `create_react_agent()` which builds:
1. An "agent" node where Claude reasons and decides tool calls
2. A "tools" node that executes the selected tool
3. A conditional edge: if Claude made a tool call → loop; if not → END

**`SYSTEM_PROMPT`** — Critical for agent behavior. Tells Claude:
- What tools are available and when to use each
- Investigation methodology (logs first, then metrics, then DB)
- To state reasoning before each tool call
- To suggest remediation only after finding root cause

### Key Concept: `create_react_agent`

This is LangGraph's built-in ReAct implementation. Under the hood, it creates:

```python
# Simplified — create_react_agent does this for you:
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)      # LLM reasons
workflow.add_node("tools", execute_tools)   # Run tool

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {"continue": "tools", "end": END}
)
workflow.add_edge("tools", "agent")  # Always loop back
```

The loop continues until Claude responds WITHOUT a tool call (meaning it's done investigating).

---

## 🧪 Testing

```bash
python tools.py          # Test all 5 tools individually
python test_agent.py     # 7 tests (6 offline, 1 needs API key)
python main.py           # Full investigation (needs API key)
```

## 🎯 Challenges

1. **Add a tool** — Create a `check_alerts` tool that returns recent PagerDuty-style alerts
2. **Custom issue** — Run `python main.py "Memory usage is spiking on the database server"`
3. **Limit iterations** — Add `max_iterations` to prevent infinite loops
4. **Add memory** — Let the agent remember findings from previous investigations
5. **Build your own** — Replace simulated tools with real `subprocess.run()` calls to `kubectl`, `docker`, etc.

## ✅ Completion Checklist

- [ ] Ran `python tools.py` and saw all 5 tools work
- [ ] Ran `python test_agent.py` — all tests pass
- [ ] Ran `python main.py` and watched the agent investigate autonomously
- [ ] Understand the ReAct loop: Think → Act → Observe → Think → ...
- [ ] Understand that `@tool` docstrings guide Claude's tool selection
- [ ] Understand `create_react_agent()` builds the full loop graph

## 📚 Resources

- [LangGraph Tool Calling](https://langchain-ai.github.io/langgraph/how-tos/tool-calling/)
- [ReAct Pattern Paper](https://react-lm.github.io/)
- [create_react_agent API](https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent)

---

**Next: [04 — Database Migration Approval](../04-migration-approval) — human-in-the-loop with interrupts →**
