"""
Code review functionality to identify bugs and issues in generated code.
"""

from typing import List, Dict, Any
from pathlib import Path
import json
from src.llm.client import LLMClient
from src.llm.prompts import CodeReviewPrompts
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CodeReviewer:
    """Review code for bugs and issues"""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.prompts = CodeReviewPrompts()

    def review_app(self, app_path: Path) -> List[Dict[str, Any]]:
        """
        Review an application for issues.

        Args:
            app_path: Path to the application directory

        Returns:
            List of issues found
        """
        issues = []

        # Review main app file
        app_file = app_path / 'app.py'
        if app_file.exists():
            file_issues = self.review_file(app_file)
            issues.extend(file_issues)

        return issues

    def review_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Review a single Python file.

        Args:
            file_path: Path to the Python file

        Returns:
            List of issues found in the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()

            prompt = self.prompts.review_code_prompt(code, str(file_path))
            system_prompt = self.prompts.code_review_system_prompt()

            response = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=2048
            )

            # Parse response
            issues = self._parse_review_response(response)
            logger.info(f"Reviewed {file_path}: found {len(issues)} issues")

            return issues
        except Exception as e:
            logger.error(f"Error reviewing file {file_path}: {e}")
            return []

    def _parse_review_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM review response"""
        try:
            # Clean response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()

            issues = json.loads(response)
            return issues if isinstance(issues, list) else []
        except json.JSONDecodeError:
            logger.warning("Failed to parse review response as JSON")
            return []
