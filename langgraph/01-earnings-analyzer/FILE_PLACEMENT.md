# 📍 File Placement Guide

Where to put each file in your lang-stuff repo.

## 📁 Directory: `langgraph/01-earnings-analyzer/`

Copy these files into this directory:

```
langgraph/01-earnings-analyzer/
├── sec_api.py              ← Copy from downloads
├── simple_version.py       ← Copy from downloads
└── LEARNING_GUIDE.md       ← Copy from downloads
```

## 🚀 Quick Setup

```bash
# Navigate to your repo
cd lang-stuff/langgraph/01-earnings-analyzer/

# Copy the files (adjust path as needed)
cp ~/Downloads/sec_api.py .
cp ~/Downloads/simple_version.py .
cp ~/Downloads/LEARNING_GUIDE.md .

# Verify files are in place
ls -la
# Should see: sec_api.py, simple_version.py, LEARNING_GUIDE.md

# Make sure you have requirements.txt (already created earlier)
ls ../requirements.txt
```

## ✅ Verification

Your directory should look like:

```
langgraph/01-earnings-analyzer/
├── README.md               (already there from setup)
├── requirements.txt        (already there from setup)
├── sec_api.py             (NEW - you just copied)
├── simple_version.py      (NEW - you just copied)
├── LEARNING_GUIDE.md      (NEW - you just copied)
├── examples/
│   └── example_outputs.md (already there from setup)
└── data/
    └── (empty - SEC data fetched in real-time)
```

## 🔧 First Run

```bash
# 1. Install dependencies (if not done already)
pip install -r requirements.txt

# 2. Set API key
export ANTHROPIC_API_KEY="your-key-here"

# 3. Test SEC API
python sec_api.py
# Should fetch Apple's data

# 4. Start implementing TODOs
# Open LEARNING_GUIDE.md and follow along!
```

## 📝 Git Workflow

```bash
# After copying files
git add sec_api.py simple_version.py LEARNING_GUIDE.md
git commit -m "Add earnings analyzer starter code"
git push origin main
```

## 🎯 What's Next?

1. **Read LEARNING_GUIDE.md** - Step-by-step instructions
2. **Complete TODO 1** in sec_api.py
3. **Test after each TODO**
4. **Move to simple_version.py** once SEC API works
5. **Test the full workflow**

---

**Files ready? Open LEARNING_GUIDE.md and let's build! 🚀**