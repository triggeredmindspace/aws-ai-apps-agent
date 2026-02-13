"""
Generate unique AI application ideas using LLM.
Ensures ideas are novel and leverage AWS services effectively.
"""

from typing import List, Dict, Any, Optional
import json
from src.llm.client import LLMClient
from src.llm.prompts import IdeaGenerationPrompts
from src.state.app_registry import AppRegistry
from src.utils.logger import get_logger

logger = get_logger(__name__)


class IdeaGenerator:
    """Generate unique AI application ideas"""

    def __init__(self, llm_client: LLMClient, app_registry: AppRegistry):
        self.llm = llm_client
        self.registry = app_registry
        self.prompts = IdeaGenerationPrompts()

    def generate_idea(
        self,
        category: str,
        aws_services: List[str],
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Generate a unique application idea.

        Args:
            category: Target category (e.g., 'bedrock_ai_agents')
            aws_services: Preferred AWS services to use
            max_retries: Maximum number of generation attempts

        Returns:
            Dict with idea details: name, description, features, aws_services, etc.
        """
        # Get existing apps in this category
        existing_apps = self.registry.get_apps_by_category(category)

        # Build context
        context = {
            'category': category,
            'preferred_aws_services': aws_services,
            'existing_apps': [app['name'] for app in existing_apps],
            'total_apps_count': self.registry.get_total_apps()
        }

        for attempt in range(max_retries):
            try:
                # Generate idea using LLM
                prompt = self.prompts.generate_idea_prompt(context)
                system_prompt = self.prompts.idea_system_prompt()

                response = self.llm.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.8,  # Higher temperature for creativity
                    max_tokens=2048
                )

                # Parse response
                idea = self._parse_idea_response(response)

                # Validate uniqueness
                if self._is_unique(idea):
                    logger.info(f"Generated unique idea: {idea['name']}")
                    return idea
                else:
                    logger.warning(f"Generated idea '{idea['name']}' is not unique (attempt {attempt + 1}/{max_retries})")

            except Exception as e:
                logger.error(f"Error generating idea (attempt {attempt + 1}/{max_retries}): {e}")

        # If all retries failed, return a fallback idea
        logger.warning("Failed to generate unique idea after retries, using fallback")
        return self._create_fallback_idea(category, aws_services)

    def _parse_idea_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured idea"""
        try:
            # Clean response if it has markdown code blocks
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()

            # Parse JSON
            idea = json.loads(response)

            # Validate required fields
            required_fields = ['name', 'description', 'features', 'aws_services', 'use_case']
            for field in required_fields:
                if field not in idea:
                    raise ValueError(f"Missing required field: {field}")

            return idea
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Response was: {response[:200]}")
            raise

    def _is_unique(self, idea: Dict[str, Any]) -> bool:
        """Check if the idea is sufficiently unique"""
        # Check if name already exists
        if self.registry.app_exists(idea['name']):
            return False

        # Check for very similar names
        existing_apps = self.registry.get_all_apps()
        idea_name_lower = idea['name'].lower()

        for app in existing_apps:
            existing_name_lower = app['name'].lower()
            # Check if names are too similar
            if idea_name_lower == existing_name_lower:
                return False
            # Check for substring matches (too similar)
            if len(idea_name_lower) > 5 and len(existing_name_lower) > 5:
                if idea_name_lower in existing_name_lower or existing_name_lower in idea_name_lower:
                    return False

        return True

    def _create_fallback_idea(self, category: str, aws_services: List[str]) -> Dict[str, Any]:
        """Create a fallback idea when generation fails"""
        import random

        fallback_ideas = {
            'bedrock_ai_agents': [
                {
                    'name': 'AWS Bedrock Content Moderator',
                    'description': 'AI-powered content moderation system using AWS Bedrock for analyzing and filtering user-generated content in real-time.',
                    'features': ['Real-time content analysis', 'Multi-language support', 'Custom moderation rules', 'API integration'],
                    'use_case': 'Social media platforms and community forums',
                    'difficulty': 'intermediate'
                }
            ],
            'rag_on_aws': [
                {
                    'name': 'AWS Legal Document RAG Assistant',
                    'description': 'Retrieval-augmented generation system for legal document analysis using AWS Bedrock and OpenSearch.',
                    'features': ['Document ingestion', 'Semantic search', 'Citation tracking', 'Multi-document queries'],
                    'use_case': 'Law firms and legal research',
                    'difficulty': 'advanced'
                }
            ]
        }

        ideas = fallback_ideas.get(category, fallback_ideas['bedrock_ai_agents'])
        fallback = random.choice(ideas).copy()
        fallback['aws_services'] = aws_services
        fallback['frameworks'] = ['streamlit', 'langchain']
        fallback['estimated_cost'] = 'Medium - based on API usage'

        return fallback
