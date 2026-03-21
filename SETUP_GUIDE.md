# Lang-Stuff Repository Setup Files

Welcome! This folder contains everything you need to set up your `lang-stuff` repository.

## 📦 What's Included

| File | Description | Where it goes |
|------|-------------|---------------|
| `setup_repo.sh` | Bash script to create directory structure | Repo root |
| `README.md` | Main repository README | Repo root |
| `langgraph_README.md` | LangGraph section README | `langgraph/` |
| `earnings_analyzer_README.md` | Earnings analyzer README | `langgraph/01-earnings-analyzer/` |
| `requirements.txt` | Python dependencies | `langgraph/01-earnings-analyzer/` |
| `.env.example` | Environment variables template | Repo root |
| `example_outputs.md` | Sample outputs | `langgraph/01-earnings-analyzer/examples/` |

## 🚀 Quick Setup Instructions

### Step 1: Clone Your Repo

```bash
git clone git@github.com:kraghavan/lang-stuff.git
cd lang-stuff
```

### Step 2: Run Setup Script

```bash
# Copy setup_repo.sh to repo root
cp /path/to/setup_repo.sh .

# Make it executable
chmod +x setup_repo.sh

# Run it
./setup_repo.sh
```

This will create all the directories you need:
```
lang-stuff/
├── langgraph/
│   ├── 01-earnings-analyzer/
│   ├── 02-loan-approval/
│   └── 03-fraud-detection/
├── langchain/
├── langsmith/
├── langflow/
└── shared/
```

### Step 3: Copy READMEs to Correct Locations

```bash
# Main README
cp README.md ./

# LangGraph README
cp langgraph_README.md ./langgraph/README.md

# Earnings Analyzer README
cp earnings_analyzer_README.md ./langgraph/01-earnings-analyzer/README.md

# Requirements
cp requirements.txt ./langgraph/01-earnings-analyzer/

# Env template
cp .env.example ./

# Example outputs
mkdir -p ./langgraph/01-earnings-analyzer/examples/
cp example_outputs.md ./langgraph/01-earnings-analyzer/examples/
```

### Step 4: Set Up Environment

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and add your Anthropic API key
nano .env  # or use your preferred editor
```

### Step 5: Commit Initial Structure

```bash
git add .
git commit -m "Initial repo structure - earnings analyzer setup"
git push origin main
```

## 🏗️ Manual File Placement (If Needed)

If you prefer to place files manually:

1. **Repo Root:**
   - `README.md`
   - `.env.example`
   - `.gitignore` (created by setup_repo.sh)

2. **langgraph/ directory:**
   - `README.md` (from langgraph_README.md)

3. **langgraph/01-earnings-analyzer/ directory:**
   - `README.md` (from earnings_analyzer_README.md)
   - `requirements.txt`
   - `examples/example_outputs.md`

## 📝 Next Steps After Setup

1. **Install dependencies:**
   ```bash
   cd langgraph/01-earnings-analyzer
   pip install -r requirements.txt
   ```

2. **Set up API key:**
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```

3. **Start building the analyzer:**
   - Create `simple_version.py`
   - Create `sec_api.py`
   - Follow the README in earnings-analyzer

## 🎯 File Summary

### setup_repo.sh
- Creates complete directory structure
- Generates placeholder READMEs for future sections
- Creates shared utility files
- Sets up .gitignore

### README.md (Main)
- Repository overview
- Learning roadmap
- Tech stack
- Quick start guide

### langgraph_README.md
- When to use LangGraph
- Common patterns
- All three examples overview
- Key concepts

### earnings_analyzer_README.md
- Complete guide for earnings analyzer
- Architecture diagrams
- API documentation
- Example usage

### requirements.txt
- All Python dependencies
- Versioned for stability

### .env.example
- Environment variable template
- API key placeholder
- Configuration options

### example_outputs.md
- Real output examples
- Different scenarios
- Error handling examples

## 💡 Tips

- Run `setup_repo.sh` first - it creates the structure
- Then copy READMEs to their destinations
- Start with earnings-analyzer
- Don't forget to add your API key!

## 🤔 Questions?

If something's unclear:
1. Check the main README.md
2. Check the specific example's README
3. Look at example_outputs.md for expected results

---

**Ready to build? Let's go! 🚀**

```bash
cd lang-stuff
./setup_repo.sh
# Then start building in langgraph/01-earnings-analyzer/
```
