"""
Prompt templates for LLM-based code generation tasks.
"""

from typing import Dict, Any


class IdeaGenerationPrompts:
    """Prompts for AI application idea generation"""

    @staticmethod
    def idea_system_prompt() -> str:
        return """You are an expert AI/ML application architect specializing in AWS services.
Your task is to generate unique, practical, and innovative AI application ideas.

Key requirements:
- Ideas must be unique and not duplicate existing applications
- Must leverage AWS services effectively (Bedrock, SageMaker, Lambda, etc.)
- Must be practical and implementable
- Should solve real-world problems
- Return response in JSON format only, no additional text

JSON schema:
{
    "name": "Application name (concise, descriptive, 3-6 words)",
    "description": "2-3 sentence description of what the app does and its value",
    "features": ["feature1", "feature2", "feature3", ...],
    "aws_services": ["bedrock", "lambda", "s3", ...],
    "use_case": "Primary use case or target audience",
    "difficulty": "beginner|intermediate|advanced",
    "estimated_cost": "Low|Medium|High - brief explanation",
    "frameworks": ["streamlit", "fastapi", "langchain", ...]
}"""

    @staticmethod
    def generate_idea_prompt(context: Dict[str, Any]) -> str:
        existing_apps_str = ', '.join(context.get('existing_apps', [])[:10])
        if len(context.get('existing_apps', [])) > 10:
            existing_apps_str += f", and {len(context.get('existing_apps', [])) - 10} more..."

        return f"""Generate a unique AI application idea for the category: {context['category']}

Context:
- Preferred AWS services: {', '.join(context['preferred_aws_services'])}
- Existing apps in this category: {len(context.get('existing_apps', []))}
- Total apps in repository: {context['total_apps_count']}

Avoid duplicating these existing apps:
{existing_apps_str}

Generate a creative, unique idea that:
1. Uses AWS services in innovative ways (especially the preferred services)
2. Solves a practical, real-world problem
3. Is completely different from existing applications
4. Is implementable with modern AI/ML frameworks
5. Provides clear value to users

Return ONLY the JSON response, no markdown formatting or additional text."""


class CodeGenerationPrompts:
    """Prompts for code generation"""

    @staticmethod
    def code_generation_system_prompt() -> str:
        return """You are an expert Python developer specializing in AWS and AI/ML applications.
Your task is to generate clean, production-ready, well-documented Python code.

Requirements:
- Write Python 3.10+ code following PEP 8 style guidelines
- Include comprehensive error handling
- Add clear docstrings and comments
- Use type hints where appropriate
- Follow AWS best practices and security guidelines
- Make code modular and maintainable
- Include environment variable configuration
- Never hardcode credentials or secrets"""

    @staticmethod
    def generate_app_code_prompt(idea: Dict[str, Any]) -> str:
        return f"""Generate a complete Python application for: {idea['name']}

Description: {idea['description']}

Features to implement:
{chr(10).join(f"- {feature}" for feature in idea.get('features', []))}

AWS Services to use:
{chr(10).join(f"- {service}" for service in idea.get('aws_services', []))}

Requirements:
1. Create a main application file using {idea.get('frameworks', ['streamlit'])[0]} for the UI
2. Use boto3 for AWS service integration
3. Include proper error handling and logging
4. Add configuration management using environment variables
5. Make the code production-ready and secure
6. Include inline comments explaining key logic
7. Follow AWS SDK best practices

Return ONLY the Python code in a single code block, no markdown headers or explanations."""

    @staticmethod
    def generate_readme_prompt(idea: Dict[str, Any]) -> str:
        return f"""Generate a comprehensive README.md file for: {idea['name']}

Application details:
- Description: {idea['description']}
- AWS Services: {', '.join(idea.get('aws_services', []))}
- Use Case: {idea.get('use_case', '')}
- Difficulty: {idea.get('difficulty', 'intermediate')}

The README should include:
1. Title and brief description
2. Features list
3. Prerequisites (AWS account, Python version, etc.)
4. Installation instructions
5. Configuration (environment variables needed)
6. Usage instructions with examples
7. AWS Setup guide (what resources to create)
8. Cost considerations
9. Troubleshooting section
10. License (MIT)

Use clear markdown formatting with proper headings, code blocks, and emoji where appropriate.
Return the complete README content."""

    @staticmethod
    def generate_cloudformation_prompt(idea: Dict[str, Any]) -> str:
        return f"""Generate a CloudFormation template (YAML) for deploying: {idea['name']}

AWS Services to provision:
{chr(10).join(f"- {service}" for service in idea.get('aws_services', []))}

The template should:
1. Define all necessary AWS resources
2. Use parameters for configurable values
3. Include outputs for important resource identifiers
4. Follow CloudFormation best practices
5. Include IAM roles and policies with least privilege
6. Add resource tags for organization
7. Include descriptions for parameters and resources

Return ONLY the YAML CloudFormation template, no additional text."""


class DocumentationPrompts:
    """Prompts for documentation generation"""

    @staticmethod
    def generate_main_readme_prompt(apps_by_category: Dict[str, list]) -> str:
        total_apps = sum(len(apps) for apps in apps_by_category.values())

        return f"""Generate a comprehensive main README.md for the awesome-aws-ai-apps repository.

Current statistics:
- Total applications: {total_apps}
- Categories: {len(apps_by_category)}

Categories and apps:
{chr(10).join(f"- {cat}: {len(apps)} apps" for cat, apps in apps_by_category.items())}

The README should include:
1. Eye-catching title and description
2. Table of contents
3. Quick start guide
4. Categories with links to each category folder
5. Contributing guidelines
6. AWS prerequisites
7. Cost information and warnings
8. License
9. Star history badge and other relevant badges

Use engaging markdown formatting, emojis, and clear organization.
Make it similar in quality to the awesome-llm-apps repository but focused on AWS."""


class CodeReviewPrompts:
    """Prompts for code review and bug detection"""

    @staticmethod
    def code_review_system_prompt() -> str:
        return """You are an expert code reviewer specializing in Python, AWS, and security.
Analyze code for bugs, security issues, best practice violations, and potential improvements."""

    @staticmethod
    def review_code_prompt(code: str, file_path: str) -> str:
        return f"""Review this Python code from {file_path}:

```python
{code}
```

Analyze for:
1. Bugs and logic errors
2. Security vulnerabilities (hardcoded secrets, injection risks, etc.)
3. AWS best practices violations
4. Error handling issues
5. Performance problems
6. Code quality issues

Return a JSON array of issues found:
[
    {{
        "severity": "critical|high|medium|low",
        "type": "bug|security|performance|style",
        "line": line_number,
        "issue": "description of the issue",
        "suggestion": "how to fix it"
    }},
    ...
]

If no issues found, return an empty array: []"""


class BugFixPrompts:
    """Prompts for automated bug fixing"""

    @staticmethod
    def fix_bug_prompt(code: str, issue: Dict[str, Any]) -> str:
        return f"""Fix the following issue in this code:

Issue: {issue['issue']}
Severity: {issue['severity']}
Suggested fix: {issue['suggestion']}
Line: {issue.get('line', 'unknown')}

Original code:
```python
{code}
```

Return ONLY the corrected code, no explanations or markdown headers."""
