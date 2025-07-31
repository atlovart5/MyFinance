# 🚀 FinBot Quick Start Guide

Get FinBot running in 5 minutes!

## ⚡ Super Quick Setup

### 1. **One-Command Setup**
```bash
git clone <your-repo-url>
cd finbot_project
python setup.py
```

### 2. **Add Your API Key**
Edit `.env` file and add:
```
OPENAI_API_KEY=sk-your-openai-key-here
```

### 3. **Add Your Data**
Put your CSV files in:
- `data/raw/credito/` (credit card statements)
- `data/raw/debito/` (debit card statements)

### 4. **Run FinBot**
```bash
streamlit run app/app.py
```

## 📋 What You Need

- **Python 3.8+** (check with `python --version`)
- **OpenAI API Key** (get from [OpenAI Platform](https://platform.openai.com/))
- **CSV files** from your bank statements

## 🔧 Troubleshooting

### **"Module not found" errors**
```bash
pip install -r requirements.txt
```

### **"API key not found" error**
Make sure your `.env` file exists and contains:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### **"No data found" error**
- Check that your CSV files are in the correct folders
- Verify CSV format matches the examples in README.md

### **Tests failing**
```bash
python run_tests.py
```
This will show you exactly what's wrong.

## 🎯 Next Steps

1. **Explore the Dashboard** - See your spending patterns
2. **Try the AI Chat** - Ask questions like "What was my biggest expense in July?"
3. **Generate Reports** - Create PDF reports for your finances
4. **Customize Categories** - Add your own spending categories

## 📞 Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Run `python run_tests.py` to diagnose issues
- Look at the logs for error details

---

**That's it! You're ready to manage your finances with AI! 🤖💰** 