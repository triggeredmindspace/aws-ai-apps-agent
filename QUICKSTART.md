# 🚀 Quick Start Guide

Get your AWS AI Apps automation agent running in 5 minutes!

## ⚡ Quick Setup

### Step 1: Install Dependencies (1 min)

```bash
pip install -r requirements.txt
```

### Step 2: Configure API Keys (2 min)

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
ANTHROPIC_API_KEY=sk-ant-xxxxx  # Get from console.anthropic.com
GITHUB_TOKEN=ghp_xxxxx          # Get from github.com/settings/tokens
```

### Step 3: Initialize the Repository (1 min)

```bash
export GITHUB_TOKEN=your_token_here
export ANTHROPIC_API_KEY=your_key_here
python scripts/initialize_repo.py
```

This creates the `awesome-aws-ai-apps` repository in your GitHub account!

### Step 4: Generate Your First App (1 min)

```bash
export TARGET_REPO_PATH=../awesome-aws-ai-apps  # Clone the created repo here first
python scripts/daily_iteration.py
```

Watch as the agent:
- ✨ Generates a unique AI application idea
- 💻 Creates complete Python code
- 📝 Writes comprehensive documentation
- ☁️ Generates AWS CloudFormation templates
- 🚀 Commits everything to your repository

## 🎯 What You'll Get

After running the daily iteration, you'll have a new AI application with:

- **app.py** - Complete working application code
- **README.md** - Detailed setup and usage guide
- **requirements.txt** - All Python dependencies
- **config.yaml** - Application configuration
- **.env.example** - Environment variable template
- **aws/cloudformation/template.yaml** - AWS infrastructure
- **aws/deploy.sh** - Deployment script

## 🤖 Enable Daily Automation

### Option 1: GitHub Actions (Recommended)

1. Push this code to your GitHub repository
2. Add secrets in Settings → Secrets and variables → Actions:
   - `ANTHROPIC_API_KEY`
   - `GITHUB_TOKEN`
3. The workflow runs automatically at 6 AM UTC daily!

### Option 2: Local Cron Job

```bash
# Add to crontab
0 6 * * * cd /path/to/GitHub-Agent && python scripts/daily_iteration.py
```

## 📊 Monitor Progress

Check the generated files in `data/`:
- `state.json` - Automation state and statistics
- `app_registry.json` - All generated applications
- `last_commit_message.txt` - Latest commit message

## 🎨 Customize

### Change App Categories

Edit `config/categories.yaml`:
```yaml
categories:
  - name: my_custom_category
    description: My custom AI apps
    priority: 1
```

### Adjust Generation Rate

In `.env`:
```env
NEW_APPS_PER_DAY=2  # Generate 2 apps per day
BUG_FIXES_PER_DAY=3
```

### Use Different LLM

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
```

## 🆘 Need Help?

- Check [README.md](README.md) for full documentation
- Review logs in `automation.log`
- Check GitHub Actions logs in your repository

## 🎉 Success Indicators

You'll know it's working when you see:
- ✅ New applications in your target repository
- ✅ Daily commits with descriptive messages
- ✅ Growing app count in `app_registry.json`
- ✅ CloudFormation templates for AWS deployment

---

**Ready to go?** Run the commands above and watch your AI application collection grow automatically! 🚀
