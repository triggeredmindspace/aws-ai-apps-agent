"""
Generate complete application code including Python files, requirements, and configs.
"""

from typing import Dict, Any
from pathlib import Path
from src.llm.client import LLMClient
from src.llm.prompts import CodeGenerationPrompts
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CodeGenerator:
    """Generate application code from ideas"""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.prompts = CodeGenerationPrompts()

    def generate_app(
        self,
        idea: Dict[str, Any],
        category: str,
        output_path: Path
    ) -> Dict[str, str]:
        """
        Generate complete application code.

        Args:
            idea: Application idea with name, description, features, etc.
            category: Category directory (e.g., 'bedrock_ai_agents')
            output_path: Base path for the target repository

        Returns:
            Dict mapping file paths to their content
        """
        logger.info(f"Generating app: {idea['name']}")

        files = {}

        # 1. Main application file
        files['app.py'] = self._generate_main_app(idea)

        # 2. Requirements.txt
        files['requirements.txt'] = self._generate_requirements(idea)

        # 3. README.md
        files['README.md'] = self._generate_readme(idea)

        # 4. Configuration file
        files['config.yaml'] = self._generate_config(idea)

        # 5. Environment template
        files['.env.example'] = self._generate_env_example(idea)

        # 6. AWS CloudFormation template
        files['aws/cloudformation/template.yaml'] = self._generate_cloudformation(idea)

        # 7. Deployment script
        files['aws/deploy.sh'] = self._generate_deploy_script(idea)

        logger.info(f"Generated {len(files)} files for {idea['name']}")
        return files

    def _generate_main_app(self, idea: Dict[str, Any]) -> str:
        """Generate the main application Python file"""
        try:
            prompt = self.prompts.generate_app_code_prompt(idea)
            system_prompt = self.prompts.code_generation_system_prompt()

            code = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for more predictable code
                max_tokens=4096
            )

            # Clean and extract code
            code = self._extract_code_block(code)
            return code
        except Exception as e:
            logger.error(f"Error generating main app code: {e}")
            return self._generate_fallback_app_code(idea)

    def _generate_requirements(self, idea: Dict[str, Any]) -> str:
        """Generate requirements.txt based on app needs"""
        dependencies = set()

        # AWS SDK
        dependencies.add('boto3>=1.34.0')
        dependencies.add('botocore>=1.34.0')

        # LLM libraries
        if 'bedrock' in idea.get('aws_services', []):
            dependencies.add('anthropic>=0.18.0')

        # Framework dependencies
        frameworks = idea.get('frameworks', ['streamlit'])
        if 'streamlit' in frameworks:
            dependencies.add('streamlit>=1.31.0')
        if 'fastapi' in frameworks:
            dependencies.add('fastapi>=0.109.0')
            dependencies.add('uvicorn>=0.27.0')
        if 'langchain' in frameworks:
            dependencies.add('langchain>=0.1.0')
            dependencies.add('langchain-aws>=0.1.0')
        if 'flask' in frameworks:
            dependencies.add('flask>=3.0.0')

        # Common utilities
        dependencies.add('python-dotenv>=1.0.0')
        dependencies.add('pydantic>=2.6.0')
        dependencies.add('pyyaml>=6.0.1')

        return '\n'.join(sorted(dependencies)) + '\n'

    def _generate_readme(self, idea: Dict[str, Any]) -> str:
        """Generate comprehensive README"""
        try:
            prompt = self.prompts.generate_readme_prompt(idea)

            readme = self.llm.generate(
                prompt=prompt,
                temperature=0.5,
                max_tokens=2048
            )

            return readme
        except Exception as e:
            logger.error(f"Error generating README: {e}")
            return self._generate_fallback_readme(idea)

    def _generate_config(self, idea: Dict[str, Any]) -> str:
        """Generate YAML configuration file"""
        import yaml

        config = {
            'app_name': idea['name'],
            'aws_region': 'us-east-1',
            'aws_services': idea.get('aws_services', []),
            'llm_config': {
                'model': 'anthropic.claude-3-sonnet-20240229-v1:0',
                'max_tokens': 2048,
                'temperature': 0.7
            }
        }

        return yaml.dump(config, default_flow_style=False)

    def _generate_env_example(self, idea: Dict[str, Any]) -> str:
        """Generate .env.example file"""
        env_vars = [
            "# AWS Configuration",
            "AWS_ACCESS_KEY_ID=your_access_key_here",
            "AWS_SECRET_ACCESS_KEY=your_secret_key_here",
            "AWS_REGION=us-east-1",
            ""
        ]

        if 'bedrock' in idea.get('aws_services', []):
            env_vars.extend([
                "# AWS Bedrock Configuration",
                "BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0",
                ""
            ])

        env_vars.extend([
            "# Application Configuration",
            "LOG_LEVEL=INFO",
            ""
        ])

        return '\n'.join(env_vars)

    def _generate_cloudformation(self, idea: Dict[str, Any]) -> str:
        """Generate AWS CloudFormation template"""
        try:
            prompt = self.prompts.generate_cloudformation_prompt(idea)

            template = self.llm.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=4096
            )

            # Extract YAML if in code blocks
            template = self._extract_yaml_block(template)
            return template
        except Exception as e:
            logger.error(f"Error generating CloudFormation template: {e}")
            return self._generate_fallback_cloudformation(idea)

    def _generate_deploy_script(self, idea: Dict[str, Any]) -> str:
        """Generate AWS deployment script"""
        script = f"""#!/bin/bash
# Deployment script for {idea['name']}

set -e

echo "Deploying {idea['name']} to AWS..."

# Set AWS region
export AWS_REGION=${{AWS_REGION:-us-east-1}}

# Deploy CloudFormation stack
aws cloudformation deploy \\
    --template-file cloudformation/template.yaml \\
    --stack-name {self._slugify(idea['name'])} \\
    --capabilities CAPABILITY_IAM \\
    --region $AWS_REGION

echo "Deployment complete!"
"""
        return script

    def _extract_code_block(self, text: str) -> str:
        """Extract code from markdown code blocks"""
        text = text.strip()

        if '```python' in text:
            start = text.find('```python') + len('```python')
            end = text.find('```', start)
            if end != -1:
                return text[start:end].strip()
        elif '```' in text:
            start = text.find('```') + 3
            # Skip language identifier if present
            newline = text.find('\n', start)
            if newline != -1:
                start = newline + 1
            end = text.find('```', start)
            if end != -1:
                return text[start:end].strip()

        return text.strip()

    def _extract_yaml_block(self, text: str) -> str:
        """Extract YAML from markdown code blocks"""
        text = text.strip()

        if '```yaml' in text:
            start = text.find('```yaml') + len('```yaml')
            end = text.find('```', start)
            if end != -1:
                return text[start:end].strip()
        elif '```' in text:
            start = text.find('```') + 3
            newline = text.find('\n', start)
            if newline != -1:
                start = newline + 1
            end = text.find('```', start)
            if end != -1:
                return text[start:end].strip()

        return text.strip()

    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        return text.lower().replace(' ', '-').replace('_', '-')

    def _generate_fallback_app_code(self, idea: Dict[str, Any]) -> str:
        """Generate fallback application code"""
        return f"""\"\"\"
{idea['name']}

{idea['description']}
\"\"\"

import boto3
import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


class App:
    def __init__(self):
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.setup_aws_clients()

    def setup_aws_clients(self):
        \"\"\"Initialize AWS service clients\"\"\"
        # TODO: Initialize AWS clients for: {', '.join(idea.get('aws_services', []))}
        pass

    def run(self):
        \"\"\"Main application logic\"\"\"
        st.title("{idea['name']}")
        st.write("{idea['description']}")

        # TODO: Implement features:
        {chr(10).join(f'        # - {feature}' for feature in idea.get('features', []))}


if __name__ == "__main__":
    app = App()
    app.run()
"""

    def _generate_fallback_readme(self, idea: Dict[str, Any]) -> str:
        """Generate fallback README"""
        return f"""# {idea['name']}

{idea['description']}

## Features

{chr(10).join(f'- {feature}' for feature in idea.get('features', []))}

## AWS Services Used

{chr(10).join(f'- {service}' for service in idea.get('aws_services', []))}

## Prerequisites

- Python 3.10+
- AWS Account with appropriate permissions
- AWS CLI configured

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and fill in your AWS credentials:

```bash
cp .env.example .env
```

## Usage

```bash
streamlit run app.py
```

## AWS Deployment

Deploy the infrastructure using the provided CloudFormation template:

```bash
cd aws
chmod +x deploy.sh
./deploy.sh
```

## Use Case

{idea.get('use_case', '')}

## Difficulty Level

{idea.get('difficulty', 'intermediate').capitalize()}

## License

MIT
"""

    def _generate_fallback_cloudformation(self, idea: Dict[str, Any]) -> str:
        """Generate fallback CloudFormation template"""
        return f"""AWSTemplateFormatVersion: '2010-09-09'
Description: CloudFormation template for {idea['name']}

Parameters:
  Environment:
    Type: String
    Default: dev
    Description: Environment name

Resources:
  # TODO: Define AWS resources for: {', '.join(idea.get('aws_services', []))}

  AppLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub '/{idea['name'].lower().replace(' ', '-')}'
      RetentionInDays: 7

Outputs:
  LogGroupName:
    Description: CloudWatch Log Group
    Value: !Ref AppLogGroup
"""
