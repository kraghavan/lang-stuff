# Claude Code Instructions for lang-stuff

## Project Overview

**lang-stuff** is an educational repository for learning the LangChain ecosystem (LangChain, LangGraph, LangSmith, LangFlow) through real-world financial applications.

- **Purpose**: Hands-on learning, not production code
- **Target Audience**: Engineers learning agentic workflows and LangGraph patterns
- **Primary LLM**: Anthropic Claude (via langchain-anthropic)
- **Data Source**: SEC EDGAR API (free, no API key needed)

## Directory Structure

```
lang-stuff/
├── langgraph/                 # ✅ ACTIVE - Complex agentic workflows
│   ├── 01-earnings-analyzer/  # ✅ In Progress - SEC filing analyzer
│   │   ├── sec_api.py         # SEC EDGAR API client
│   │   ├── simple_version.py  # Main LangGraph implementation (has TODOs)
│   │   ├── LEARNING_GUIDE.md  # Step-by-step tutorial
│   │   └── examples/          # Example outputs and documentation
│   ├── 02-loan-approval/      # 📋 Planned - Multi-stage decision pipeline
│   └── 03-fraud-detection/    # 📋 Planned - Risk-adaptive investigation
├── langchain/                 # 📋 Planned - Simple chains
├── langsmith/                 # 📋 Planned - Observability & debugging
├── langflow/                  # 📋 Planned - Visual workflow builder
├── shared/                    # ✅ Shared utilities
│   ├── utils.py               # Currency formatting, percentage calculations
│   └── data_loaders.py        # CSV loading with error handling
├── .env.example               # Environment variable template
└── setup_repo.sh              # Initial setup script
```

## Current Status

### Implemented
- ✅ SEC API client (`sec_api.py`) - Complete and functional
- ✅ Repository structure and documentation
- ✅ Shared utilities
- ⚠️ Earnings analyzer (`simple_version.py`) - Partially complete with TODOs for learning

### Not Implemented
- ❌ LangChain examples
- ❌ LangSmith examples
- ❌ LangFlow examples
- ❌ Loan Approval workflow
- ❌ Fraud Detection workflow

## Key Conventions

### Code Style
- **Python 3.10+** required
- Use **type hints** everywhere (`TypedDict`, `Optional`, `List`, `Dict`)
- **Docstrings** for all functions (Google style preferred)
- Descriptive variable names over comments
- Keep functions focused (single responsibility)

### LangGraph Patterns
```python
# State: TypedDict shared across all nodes
class MyState(TypedDict):
    input: str
    data: dict
    results: list

# Nodes: Functions that transform state
def my_node(state: MyState) -> MyState:
    # Process and return modified state
    return state

# Routing: Functions that return edge names
def route_logic(state: MyState) -> Literal["path_a", "path_b"]:
    if condition:
        return "path_a"
    return "path_b"
```

### File Organization
- **API clients** in separate files (e.g., `sec_api.py`)
- **LangGraph workflows** in `*_version.py` files
- **Utilities** in `/shared` for cross-example reuse
- **Documentation** alongside code (README.md per example)
- **Examples** in `/examples` subdirectories

### Environment Variables
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929  # Default model
SEC_API_USER_AGENT=Your Name <your@email.com>

# LangSmith (future)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=...
```

## Working with This Repository

### When Adding New Code

1. **Read existing code first** - Understand patterns before adding
2. **Follow the LangGraph structure** - State → Nodes → Edges → Routing
3. **Add docstrings** - Explain what, why, and how
4. **Test incrementally** - Don't build everything at once
5. **Update LEARNING_GUIDE.md** if adding TODOs

### When Completing TODOs

TODOs in this repo are **intentional learning exercises**, not bugs:
- Preserve the TODO structure (don't remove all TODOs)
- Add comments explaining the solution
- Test each TODO independently before moving to the next
- Reference the LEARNING_GUIDE.md for hints

### When Updating Dependencies

Current versions (may be outdated):
```
langchain==0.1.0
langchain-anthropic==0.1.1
langgraph==0.0.20
```

If updating:
1. Test all examples after upgrade
2. Check for breaking API changes
3. Update requirements.txt
4. Document any code changes needed

## Testing

### Manual Testing Approach
```bash
# Test SEC API
cd langgraph/01-earnings-analyzer
python sec_api.py

# Test full workflow (when complete)
python simple_version.py
# Enter: AAPL
# Enter: Q4 2024
```

### Good Test Cases
- **Simple**: AAPL, MSFT, GOOGL (stable, predictable)
- **Complex**: TSLA, NVDA (volatile, anomalies likely)
- **Edge**: Newly public companies, recent acquisitions

### No Formal Test Suite Yet
- This is a learning repo, not production
- Tests would be beneficial but not critical
- Focus on working examples over test coverage

## Important Notes

### SEC EDGAR API
- **No API key needed** - Completely free
- **Rate limits**: 10 requests/second (be respectful)
- **User-Agent required**: Set SEC_API_USER_AGENT env var
- **Data format**: XBRL (XML-based financial reporting)
- **CIK**: Central Index Key (SEC's company identifier)

### LangGraph Key Concepts
- **State**: Shared data structure (TypedDict) passed between nodes
- **Nodes**: Functions that receive state, modify it, return it
- **Edges**: Connections between nodes (simple or conditional)
- **Routing**: Conditional logic that decides which node to visit next
- **Loops**: Created by routing back to earlier nodes
- **END**: Special marker for workflow termination

### When to Use LangGraph vs LangChain
**Use LangGraph when:**
- ✅ Need loops/iteration ("keep investigating until...")
- ✅ Conditional branching ("if X then A else B")
- ✅ Multi-agent coordination
- ✅ Human-in-the-loop
- ✅ Shared state across multiple steps

**Use LangChain when:**
- Simple A → B → C flow
- Single-pass processing
- No need to revisit previous steps

## Development Workflow

### Starting a New Example

1. Create directory: `langgraph/0X-example-name/`
2. Add README.md with:
   - What it does
   - Why it needs LangGraph
   - Architecture diagram
   - Quick start instructions
3. Create main file: `simple_version.py`
4. Create API client if needed: `*_api.py`
5. Add to main langgraph/README.md

### Iterative Development
```bash
# 1. Build data layer first
python sec_api.py  # Test API access

# 2. Define state structure
# Write TypedDict with all fields

# 3. Implement nodes one at a time
# Test each node independently

# 4. Add edges (simple first)
# Create linear flow

# 5. Add conditional routing
# Introduce branching logic

# 6. Test end-to-end
# Run complete workflow
```

## AI Assistant Guidelines

### When I Ask You to Code
- **Preserve learning structure** - Don't remove TODOs unless explicitly asked
- **Match existing style** - Follow patterns in current code
- **Explain decisions** - Why this approach over alternatives
- **Test incrementally** - Don't write large blocks without testing
- **Reference docs** - Link to LangGraph/LangChain docs when relevant

### When I Ask for Help
- **Show, don't just tell** - Provide code examples
- **Explain concepts** - Assume I'm learning LangGraph
- **Reference existing code** - Point to patterns already in the repo
- **Be practical** - Focus on making progress, not perfect code

### What NOT to Do
- ❌ Don't suggest production-grade features (this is for learning)
- ❌ Don't over-engineer (keep it simple)
- ❌ Don't remove educational TODOs without permission
- ❌ Don't add dependencies without discussing first
- ❌ Don't assume I know LangGraph concepts (explain them)

## Common Patterns

### Error Handling
```python
try:
    result = api_call()
    if not result:
        print("✗ API call returned empty")
        return None
    return result
except Exception as e:
    print(f"❌ Error: {e}")
    return None
```

### User Feedback
```python
print("\n📊 Processing data...")  # Start
print("✓ Data processed")         # Success
print("✗ Processing failed")      # Failure
print("⚠️  Warning: ...")          # Warning
```

### State Updates
```python
def my_node(state: MyState) -> MyState:
    # Get data from state
    data = state['input_field']

    # Process
    result = process(data)

    # Update state
    state['output_field'] = result

    # Always return state
    return state
```

## Resources

### Official Docs
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangChain Docs](https://python.langchain.com/)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [SEC EDGAR API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)

### Learning Resources
- LEARNING_GUIDE.md (in this repo)
- Example outputs (in examples/ directories)
- LangGraph tutorials (official site)

## Project Philosophy

**This is a learning journey, not a destination.**

- TODOs are teaching tools, not technical debt
- Incomplete is intentional (learning by doing)
- Real data makes learning engaging
- Focus on understanding over completion
- Iterate and experiment freely

---

**Last Updated**: 2026-03-20
**Primary Maintainer**: Karthika Raghavan
**AI Assistant**: Claude (Sonnet 4.5)
