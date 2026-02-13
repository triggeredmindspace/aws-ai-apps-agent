# 🤖 AWS AI Apps Automation Agent

An automated GitHub agent that creates and maintains a curated collection of AI applications built with AWS services. This system generates new applications daily, reviews and fixes bugs in existing apps, and keeps documentation up-to-date—all automatically.

## 🌟 Overview

This project creates and maintains the [awesome-aws-ai-apps](https://github.com/YOUR_USERNAME/awesome-aws-ai-apps) repository, which contains unique AI/ML applications leveraging AWS services like:

- 🧠 **Amazon Bedrock** - Foundation models and AI agents
- 🤖 **Amazon SageMaker** - ML training and deployment
- ⚡ **AWS Lambda** - Serverless compute
- 🔍 **Amazon OpenSearch** - Vector search for RAG
- 📦 **Amazon S3** - Storage and data lakes
- 🔄 **Amazon Kinesis** - Real-time data streaming

## 🚀 Features

- **Daily App Generation**: Automatically generates 1 new AI application per day
- **Bug Fixing**: Reviews and fixes bugs in existing applications
- **Documentation**: Auto-generates comprehensive READMEs and setup guides
- **AWS Infrastructure**: Creates CloudFormation templates for each app
- **Quality Control**: LLM-powered code review and validation
- **GitHub Actions**: Fully automated with GitHub Actions workflows

## 📋 Prerequisites

- Python 3.10 or higher
- GitHub account
- Anthropic API key (for Claude) or OpenAI API key
- Git

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/GitHub-Agent.git
cd GitHub-Agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# LLM Provider (choose one)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_api_key_here

# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token
TARGET_REPO=awesome-aws-ai-apps
```

#### Getting API Keys:

**Anthropic API Key:**
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an account or sign in
3. Navigate to API Keys
4. Create a new API key

**GitHub Personal Access Token:**
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Name it "AWS AI Apps Agent"
4. Select scopes: `repo`, `workflow`
5. Generate and save the token

### 4. Configure GitHub Secrets

For GitHub Actions to work, add these secrets to your repository:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `ANTHROPIC_API_KEY` - Your Anthropic API key
   - `GITHUB_TOKEN` - Your GitHub Personal Access Token (with repo and workflow permissions)

### 5. Initialize the Target Repository

Run the initialization script to create the `awesome-aws-ai-apps` repository:

**Option A: Using GitHub Actions (Recommended)**
1. Go to Actions tab in your repository
2. Select "Initialize awesome-aws-ai-apps Repository" workflow
3. Click "Run workflow"
4. Wait for completion

**Option B: Run Locally**
```bash
export GITHUB_TOKEN=your_github_token
export ANTHROPIC_API_KEY=your_api_key
python scripts/initialize_repo.py
```

This will create the target repository with:
- Initial README
- Category directories
- Basic structure

### 6. Enable Daily Automation

The GitHub Actions workflow is already configured to run daily at 6 AM UTC. To test it manually:

1. Go to Actions tab
2. Select "Daily AWS AI Apps Iteration"
3. Click "Run workflow"

## 📁 Project Structure

```
.
├── .github/
│   └── workflows/
│       ├── daily-iteration.yml          # Daily automation workflow
│       └── repo-initialization.yml      # One-time repo setup
├── src/
│   ├── config.py                        # Configuration management
│   ├── github/
│   │   └── client.py                    # GitHub API client
│   ├── llm/
│   │   ├── client.py                    # LLM client abstraction
│   │   └── prompts.py                   # Prompt templates
│   ├── generators/
│   │   ├── idea_generator.py            # Generate app ideas
│   │   └── code_generator.py            # Generate app code
│   ├── quality/
│   │   ├── code_reviewer.py             # Review code for bugs
│   │   └── bug_fixer.py                 # Automated bug fixing
│   ├── state/
│   │   ├── state_manager.py             # Track automation state
│   │   └── app_registry.py              # Registry of all apps
│   └── utils/
│       ├── logger.py                    # Logging utilities
│       └── file_operations.py           # File system helpers
├── scripts/
│   ├── initialize_repo.py               # Initialize target repo
│   └── daily_iteration.py               # Daily automation logic
├── config/
│   ├── categories.yaml                  # App categories
│   └── aws_services.yaml                # AWS services config
├── data/                                # State and registry files
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

## 🔧 Configuration

### Customize Categories

Edit [config/categories.yaml](config/categories.yaml) to add or modify app categories:

```yaml
categories:
  - name: your_category_name
    description: Description of the category
    priority: 1  # 1-3, higher = more apps generated
    target_count: 20
```

### Customize AWS Services

Edit [config/aws_services.yaml](config/aws_services.yaml) to configure which AWS services to use:

```yaml
services:
  your_service:
    name: AWS Service Name
    use_cases:
      - Use case 1
      - Use case 2
    priority: 1  # 1-3, higher = more frequently used
```

### Adjust Generation Rates

In your `.env` file, customize how many items are generated daily:

```env
NEW_APPS_PER_DAY=1
BUG_FIXES_PER_DAY=2
IMPROVEMENTS_PER_DAY=1
DOC_UPDATES_PER_DAY=1
```

## 🏃 Running Locally

### Generate a Single App

```bash
python scripts/daily_iteration.py
```

### Test the Initialization

```bash
python scripts/initialize_repo.py
```

## 🔍 How It Works

### Daily Iteration Process

1. **Idea Generation**
   - LLM generates unique AI application ideas
   - Ideas are validated for uniqueness
   - AWS services are selected based on priorities

2. **Code Generation**
   - Complete Python application is generated
   - AWS CloudFormation templates created
   - Documentation and setup guides written

3. **Quality Assurance**
   - Existing apps are reviewed for bugs
   - Issues are identified and automatically fixed
   - Code quality is validated

4. **Commit & Push**
   - Changes are committed to the target repository
   - Descriptive commit messages are generated
   - GitHub Actions pushes the changes

### Application Categories

The system generates applications across multiple categories:

- **Bedrock AI Agents** - AI agents using AWS Bedrock models
- **Serverless AI Apps** - Lambda-based AI applications
- **RAG on AWS** - Retrieval-augmented generation systems
- **SageMaker ML Apps** - ML applications with SageMaker
- **Real-time AI Streaming** - Streaming AI with Kinesis
- **Multimodal AI** - Text, image, and video AI
- **AI Content Generation** - Content creation tools
- **Conversational AI** - Chatbots and voice assistants

## 📊 Monitoring

### View Automation Logs

1. Go to Actions tab in your repository
2. Click on the latest "Daily AWS AI Apps Iteration" run
3. View logs and summary

### Check State

State is tracked in `data/state.json`:

```json
{
  "stats": {
    "total_apps_generated": 25,
    "total_bugs_fixed": 15
  },
  "last_iteration": {
    "timestamp": "2026-02-13T12:00:00Z",
    "new_apps": ["App Name"]
  }
}
```

## 🐛 Troubleshooting

### Issue: "API key not found"

**Solution:** Ensure you've set up the environment variables correctly:
```bash
export ANTHROPIC_API_KEY=your_key
# or
export OPENAI_API_KEY=your_key
```

### Issue: "Repository already exists"

**Solution:** The initialization script handles this automatically and will use the existing repository.

### Issue: "Permission denied" when pushing

**Solution:** Check that your GitHub token has the `repo` and `workflow` scopes.

### Issue: "Import errors"

**Solution:** Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

## 🔐 Security

- **Never commit** `.env` files or API keys
- Use GitHub Secrets for sensitive data in Actions
- The `.gitignore` is configured to exclude sensitive files
- Review generated code before deploying to production

## 📝 License

MIT License - feel free to use this project for your own automated repositories.

## 🤝 Contributing

This is an automated system, but contributions to improve the automation logic are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📚 Resources

- [Anthropic API Documentation](https://docs.anthropic.com)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock)
- [GitHub Actions Documentation](https://docs.github.com/actions)

## 🎯 Roadmap

- [ ] Support for more LLM providers
- [ ] Advanced quality metrics
- [ ] Community voting on app ideas
- [ ] Automated AWS deployment testing
- [ ] Multi-repository support
- [ ] Cost optimization analysis

---

**Made with ❤️ and 🤖 AI**

*This automation agent was designed to create high-quality, unique AWS AI applications daily. Star ⭐ this repo to follow the development!*
