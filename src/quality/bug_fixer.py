"""
Automated bug fixing using LLM.
"""

from typing import List, Dict, Any
from pathlib import Path
from src.llm.client import LLMClient
from src.llm.prompts import BugFixPrompts
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BugFixer:
    """Fix bugs in code automatically"""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.prompts = BugFixPrompts()

    def fix_issues(
        self,
        app_path: Path,
        issues: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Fix issues in an application.

        Args:
            app_path: Path to the application directory
            issues: List of issues to fix

        Returns:
            List of fixed files
        """
        fixed_files = []

        # Group issues by file
        issues_by_file = {}
        for issue in issues:
            if issue.get('severity') in ['critical', 'high']:
                file_path = str(app_path / 'app.py')  # Simplified: assume app.py
                if file_path not in issues_by_file:
                    issues_by_file[file_path] = []
                issues_by_file[file_path].append(issue)

        # Fix each file
        for file_path, file_issues in issues_by_file.items():
            if self._fix_file(Path(file_path), file_issues):
                fixed_files.append(file_path)

        return fixed_files

    def _fix_file(self, file_path: Path, issues: List[Dict[str, Any]]) -> bool:
        """Fix issues in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()

            code = original_code

            # Fix each issue
            for issue in issues:
                prompt = self.prompts.fix_bug_prompt(code, issue)

                fixed_code = self.llm.generate(
                    prompt=prompt,
                    temperature=0.2,
                    max_tokens=4096
                )

                # Extract code from response
                fixed_code = self._extract_code(fixed_code)
                code = fixed_code

            # Write fixed code back
            if code != original_code:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                logger.info(f"Fixed {len(issues)} issues in {file_path}")
                return True

            return False
        except Exception as e:
            logger.error(f"Error fixing file {file_path}: {e}")
            return False

    def _extract_code(self, text: str) -> str:
        """Extract code from markdown blocks"""
        text = text.strip()
        if '```python' in text:
            start = text.find('```python') + 9
            end = text.find('```', start)
            if end != -1:
                return text[start:end].strip()
        elif '```' in text:
            start = text.find('```') + 3
            end = text.find('```', start)
            if end != -1:
                return text[start:end].strip()
        return text
