"""
Initialize the awesome-aws-ai-apps repository.
Creates the repository structure and initial README.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.github.client import GitHubClient
from src.utils.logger import setup_logging, get_logger
import os

logger = get_logger(__name__)


def create_initial_readme() -> str:
    """Create the initial README content"""
    return """# 🚀 Awesome AWS AI Apps

A curated collection of AI and Machine Learning applications built with AWS services. This repository showcases practical, production-ready examples of AI agents, RAG systems, serverless ML apps, and more—all powered by AWS.

## 🌟 Overview

This repository contains unique, open-source AI applications that leverage AWS services like:
- 🧠 Amazon Bedrock (Foundation Models)
- 🤖 Amazon SageMaker (ML Training & Deployment)
- ⚡ AWS Lambda (Serverless Compute)
- 🔍 Amazon OpenSearch (Vector Search)
- 📦 Amazon S3 (Storage)
- 🔄 Amazon Kinesis (Real-time Streaming)
- And many more!

## 📂 Categories

### 🤖 Bedrock AI Agents
AI agents powered by Amazon Bedrock foundation models.

### ⚡ Serverless AI Apps
Serverless applications using AWS Lambda, API Gateway, and managed AI services.

### 📚 RAG on AWS
Retrieval-Augmented Generation applications with AWS vector databases and LLMs.

### 🧪 SageMaker ML Apps
Machine learning applications using Amazon SageMaker for training and deployment.

### 🌊 Real-time AI Streaming
Real-time AI applications using Amazon Kinesis and streaming analytics.

### 🎨 Multimodal AI
Applications that work with text, images, video, and audio using AWS AI services.

### ✍️ AI Content Generation
Content generation systems for text, images, and media.

### 💬 Conversational AI
Chatbots, voice assistants, and conversational AI on AWS.

## 🚀 Quick Start

Each application includes:
- Complete source code
- Detailed README with setup instructions
- AWS CloudFormation templates for infrastructure
- Requirements and dependencies
- Usage examples

Navigate to any category folder and choose an app to get started!

## 💡 Prerequisites

- AWS Account with appropriate permissions
- Python 3.10 or higher
- AWS CLI configured
- Basic knowledge of AWS services

## 📝 License

MIT License - see individual app directories for details.

## 🤝 Contributing

This repository is maintained by an automated agent that generates new applications daily. Each app is reviewed for quality and security before being added.

## ⚠️ Cost Warning

These applications use AWS services that may incur costs. Always review the pricing information for each AWS service before deploying. Most apps include cost estimates in their README files.

---

*This repository is automatically updated daily with new AI applications. Star ⭐ this repo to stay updated!*
"""


def create_gitignore() -> str:
    """Create .gitignore content"""
    return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo

# AWS
.aws/

# Logs
*.log

# OS
.DS_Store
Thumbs.db
"""


def main():
    """Main initialization function"""
    setup_logging()
    logger.info("Starting repository initialization...")

    try:
        # Load configuration
        config = Config()

        # Create GitHub client
        github_client = GitHubClient(config.github.token)

        # Get repository name
        repo_name = os.getenv('REPO_NAME', 'awesome-aws-ai-apps')
        repo_visibility = os.getenv('REPO_VISIBILITY', 'public')

        logger.info(f"Creating repository: {repo_name}")

        # Create repository
        repo = github_client.create_repository(
            name=repo_name,
            description="Curated collection of AI and ML applications built with AWS services",
            private=(repo_visibility == 'private'),
            auto_init=False
        )

        logger.info(f"Repository created: {repo.html_url}")

        # Create initial files
        logger.info("Creating initial README...")
        github_client.create_or_update_file(
            repo=repo,
            path="README.md",
            content=create_initial_readme(),
            message="Initial commit: Add README"
        )

        logger.info("Creating .gitignore...")
        github_client.create_or_update_file(
            repo=repo,
            path=".gitignore",
            content=create_gitignore(),
            message="Add .gitignore"
        )

        # Create category directories with READMEs
        for category in config.categories['categories']:
            category_name = category['name']
            category_desc = category['description']

            logger.info(f"Creating category: {category_name}")

            category_readme = f"""# {category_desc}

This directory contains {category_desc.lower()}.

## Applications

*Applications will be added here by the automated agent.*

---

*This category is automatically updated daily.*
"""

            github_client.create_or_update_file(
                repo=repo,
                path=f"{category_name}/README.md",
                content=category_readme,
                message=f"Add {category_name} category"
            )

        # Create initialization summary
        summary = f"""## Repository Initialization Complete ✅

- **Repository URL**: {repo.html_url}
- **Repository Name**: {repo_name}
- **Visibility**: {repo_visibility}
- **Categories Created**: {len(config.categories['categories'])}

### Next Steps

1. Set up GitHub Secrets for daily automation:
   - `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
   - `GITHUB_PAT` (Personal Access Token)
   - `TARGET_REPO_OWNER` (your GitHub username)

2. Enable GitHub Actions workflow for daily iterations

3. The agent will start generating applications automatically!

**Repository**: {repo.html_url}
"""

        # Save summary
        summary_file = config.project_root / 'data' / 'initialization_summary.md'
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        summary_file.write_text(summary)

        print(summary)
        logger.info("Repository initialization completed successfully!")

    except Exception as e:
        logger.error(f"Initialization failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
