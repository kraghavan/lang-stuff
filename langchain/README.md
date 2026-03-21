# LangChain Examples

Simple chains and basic patterns for real-world financial applications.

## When to Use LangChain (vs LangGraph)

Use LangChain when you need:
- ✅ **Linear workflows** - A → B → C, no backtracking
- ✅ **Prompt engineering** - Template-based prompts with variables
- ✅ **Output parsing** - Structured data from LLM responses
- ✅ **RAG pipelines** - Retrieve context, then generate answers
- ✅ **Simple chains** - Compose multiple steps without complex state

Use LangGraph instead when:
- ❌ You need loops or iteration
- ❌ You need conditional branching with shared state
- ❌ Multiple agents need to coordinate
- ❌ You need human-in-the-loop approval gates

## Examples in This Directory

### 1. 📈 Stock Summary Generator
**Pattern**: Prompt Template → LLM → Output Parser

```
User input (ticker) → Fetch stock data → Format prompt → Claude → Parse structured output
```

**Learn**: PromptTemplate, ChatAnthropic, StrOutputParser, LCEL (LangChain Expression Language)

[See full example →](./01-stock-summary)

---

### 2. 📰 Financial News Analyzer
**Pattern**: Sequential Chain (multi-step processing)

```
Fetch headlines → Summarize each → Analyze sentiment → Generate investment brief
```

**Learn**: Sequential chains, RunnableSequence, multiple prompts, sentiment analysis

[See full example →](./02-financial-news-analyzer)

---

### 3. 📄 SEC Filing Q&A
**Pattern**: RAG (Retrieval-Augmented Generation)

```
Load filing text → Chunk → Embed → Store in vector DB → Query → Generate answer
```

**Learn**: Document loaders, text splitters, embeddings, vector stores, retrieval chains

[See full example →](./03-sec-filing-qa)

---

### 4. 💼 Portfolio Report Generator
**Pattern**: Structured Output + Batch Processing

```
Portfolio CSV → Analyze each holding → Score & classify → Generate formatted report
```

**Learn**: Pydantic output schemas, batch processing, structured generation, report formatting

[See full example →](./04-portfolio-report-generator)

---

## Quick Start

```bash
# Choose an example
cd 01-stock-summary

# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Run it
python simple_version.py
```

## Common Patterns Across Examples

All examples demonstrate:
- **Prompt templates** - Reusable prompts with variable injection
- **LLM integration** - Using Claude via langchain-anthropic
- **Output parsing** - Converting raw LLM text into structured data
- **Error handling** - Graceful failures with informative messages
- **LCEL syntax** - Modern LangChain Expression Language (`chain = prompt | llm | parser`)

## Key LangChain Concepts

### Prompt Templates
Reusable prompts with variables:
```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a financial analyst."),
    ("human", "Analyze {company} stock based on: {data}")
])
```

### LLM (Chat Model)
Connects to Claude:
```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0)
```

### Output Parsers
Structure the LLM response:
```python
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

# Simple string output
chain = prompt | llm | StrOutputParser()

# Structured JSON output
chain = prompt | llm | JsonOutputParser()
```

### LCEL (LangChain Expression Language)
Compose chains with the pipe operator:
```python
# Linear chain
chain = prompt | llm | parser

# Invoke with variables
result = chain.invoke({"company": "AAPL", "data": metrics})
```

### Retrieval (RAG)
Combine retrieval with generation:
```python
from langchain_core.runnables import RunnablePassthrough

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | parser
)
```

## Progression Path

```
01-stock-summary          → Learn the basics (prompts, LLM, parsing)
        │
        ▼
02-financial-news-analyzer → Chain multiple steps together
        │
        ▼
03-sec-filing-qa          → Add retrieval (RAG) to the mix
        │
        ▼
04-portfolio-report-generator → Structured output + batch processing
        │
        ▼
Ready for LangGraph!       → When you need loops, branches, and state
```

## Tips for Learning LangChain

1. **Start with LCEL** - The `prompt | llm | parser` pattern is the foundation
2. **Understand the Runnable protocol** - Everything in LangChain is a "Runnable"
3. **Use `invoke()` for single inputs** - `batch()` for multiple
4. **Print intermediate results** - Debugging chains is easier step by step
5. **Read the prompts** - Most of the "intelligence" lives in the prompt template
6. **Check types** - LangChain is strongly typed; mismatched types cause confusing errors

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangChain Expression Language](https://python.langchain.com/docs/concepts/lcel/)
- [langchain-anthropic](https://python.langchain.com/docs/integrations/chat/anthropic/)
- [LangChain GitHub](https://github.com/langchain-ai/langchain)

---

**Ready to build? Start with the [Stock Summary Generator](./01-stock-summary) →**
