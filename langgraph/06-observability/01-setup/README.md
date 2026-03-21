# 01 — LangSmith Setup

## Quick Start

```bash
# 1. Get API key from https://smith.langchain.com (free: 5,000 traces/month)
# 2. Set environment variables:
export LANGCHAIN_API_KEY="lsv2_pt_..."
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_PROJECT="langgraph-learning"

# 3. Install
pip install langsmith

# 4. Test
python test_connection.py
```

Once you see `🎉 Ready to trace!`, move on to [02-trace-devops-agent](../02-trace-devops-agent).
