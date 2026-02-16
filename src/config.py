"""
Central configuration management for the AWS AI Apps automation system.
Loads from environment variables and config files.
"""

from dataclasses import dataclass, field
from typing import Optional
import os
from pathlib import Path
import yaml


@dataclass
class LLMConfig:
    """LLM provider configuration"""
    provider: str  # 'anthropic' or 'openai'
    api_key: str
    model: str
    max_tokens: int = 4096
    temperature: float = 0.7


@dataclass
class GitHubConfig:
    """GitHub API configuration"""
    token: str
    target_repo: str  # Format: owner/repo or just repo name
    target_repo_path: Optional[Path] = None


@dataclass
class GenerationConfig:
    """Generation behavior configuration"""
    new_apps_per_week: int = 1
    new_app_day: int = 1  # Monday (0=Mon, 6=Sun)
    bug_fixes_per_day: int = 1
    improvements_per_day: int = 1
    doc_updates_per_day: int = 0
    preferred_frameworks: list = field(default_factory=list)
    preferred_aws_services: list = field(default_factory=list)


class Config:
    """Main configuration class"""

    def __init__(self):
        self.llm = self._load_llm_config()
        self.github = self._load_github_config()
        self.generation = self._load_generation_config()
        self.project_root = Path(__file__).parent.parent
        self.categories = self._load_categories()
        self.aws_services = self._load_aws_services()

    def _load_llm_config(self) -> LLMConfig:
        provider = os.getenv('LLM_PROVIDER', 'anthropic')

        if provider == 'anthropic':
            return LLMConfig(
                provider='anthropic',
                api_key=os.getenv('ANTHROPIC_API_KEY', ''),
                model=os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-5-20250929'),
                max_tokens=int(os.getenv('LLM_MAX_TOKENS', '8192')),
                temperature=float(os.getenv('LLM_TEMPERATURE', '0.7'))
            )
        else:
            return LLMConfig(
                provider='openai',
                api_key=os.getenv('OPENAI_API_KEY', ''),
                model=os.getenv('OPENAI_MODEL', 'gpt-4-turbo'),
                max_tokens=int(os.getenv('LLM_MAX_TOKENS', '4096')),
                temperature=float(os.getenv('LLM_TEMPERATURE', '0.7'))
            )

    def _load_github_config(self) -> GitHubConfig:
        target_repo_path = os.getenv('TARGET_REPO_PATH')
        return GitHubConfig(
            token=os.getenv('GITHUB_TOKEN', ''),
            target_repo=os.getenv('TARGET_REPO', 'awesome-aws-ai-apps'),
            target_repo_path=Path(target_repo_path) if target_repo_path else None
        )

    def _load_generation_config(self) -> GenerationConfig:
        return GenerationConfig(
            new_apps_per_week=int(os.getenv('NEW_APPS_PER_WEEK', '1')),
            new_app_day=int(os.getenv('NEW_APP_DAY', '0')),  # 0=Monday
            bug_fixes_per_day=int(os.getenv('BUG_FIXES_PER_DAY', '1')),
            improvements_per_day=int(os.getenv('IMPROVEMENTS_PER_DAY', '1')),
            doc_updates_per_day=int(os.getenv('DOC_UPDATES_PER_DAY', '0'))
        )

    def _load_categories(self) -> dict:
        config_file = self.project_root / 'config' / 'categories.yaml'
        if config_file.exists():
            with open(config_file) as f:
                return yaml.safe_load(f)
        return self._default_categories()

    def _load_aws_services(self) -> dict:
        config_file = self.project_root / 'config' / 'aws_services.yaml'
        if config_file.exists():
            with open(config_file) as f:
                return yaml.safe_load(f)
        return self._default_aws_services()

    @staticmethod
    def _default_categories() -> dict:
        return {
            'categories': [
                {
                    'name': 'bedrock_ai_agents',
                    'description': 'AI agents using AWS Bedrock foundation models',
                    'priority': 1
                },
                {
                    'name': 'serverless_ai_apps',
                    'description': 'Serverless AI applications using Lambda and API Gateway',
                    'priority': 2
                },
                {
                    'name': 'rag_on_aws',
                    'description': 'RAG applications with AWS services (Bedrock, OpenSearch, S3)',
                    'priority': 1
                },
                {
                    'name': 'sagemaker_ml_apps',
                    'description': 'ML applications using Amazon SageMaker',
                    'priority': 2
                },
                {
                    'name': 'realtime_ai_streaming',
                    'description': 'Real-time AI with Kinesis and Lambda',
                    'priority': 3
                },
                {
                    'name': 'multimodal_ai',
                    'description': 'Multimodal AI with Bedrock (text, image, video)',
                    'priority': 2
                }
            ]
        }

    @staticmethod
    def _default_aws_services() -> dict:
        return {
            'services': {
                'bedrock': {
                    'name': 'Amazon Bedrock',
                    'use_cases': ['LLM inference', 'RAG', 'Agents'],
                    'priority': 1
                },
                'lambda': {
                    'name': 'AWS Lambda',
                    'use_cases': ['Serverless compute', 'API backends'],
                    'priority': 1
                },
                'sagemaker': {
                    'name': 'Amazon SageMaker',
                    'use_cases': ['Model training', 'Model deployment', 'Endpoints'],
                    'priority': 2
                },
                's3': {
                    'name': 'Amazon S3',
                    'use_cases': ['Document storage', 'Model artifacts', 'Data lake'],
                    'priority': 1
                },
                'dynamodb': {
                    'name': 'Amazon DynamoDB',
                    'use_cases': ['Session storage', 'Vector DB', 'Metadata'],
                    'priority': 2
                },
                'opensearch': {
                    'name': 'Amazon OpenSearch',
                    'use_cases': ['Vector search', 'RAG', 'Semantic search'],
                    'priority': 2
                },
                'api_gateway': {
                    'name': 'Amazon API Gateway',
                    'use_cases': ['REST APIs', 'WebSocket APIs'],
                    'priority': 2
                },
                'eventbridge': {
                    'name': 'Amazon EventBridge',
                    'use_cases': ['Event-driven architecture', 'Scheduling'],
                    'priority': 3
                },
                'kinesis': {
                    'name': 'Amazon Kinesis',
                    'use_cases': ['Real-time streaming', 'Data pipelines'],
                    'priority': 3
                }
            }
        }
