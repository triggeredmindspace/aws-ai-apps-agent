"""
GitHub API client for repository operations.
Handles authentication, repo creation, file operations, and commits.
"""

from typing import Optional, Dict, Any, List
import base64
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GitHubClient:
    """GitHub API client wrapper"""

    def __init__(self, token: str):
        try:
            from github import Github
            self.client = Github(token)
            self.user = self.client.get_user()
        except ImportError:
            raise ImportError("PyGithub package not installed. Run: pip install PyGithub")

    def create_repository(
        self,
        name: str,
        description: str,
        private: bool = False,
        auto_init: bool = False
    ):
        """
        Create a new GitHub repository.

        Args:
            name: Repository name
            description: Repository description
            private: Whether the repo should be private
            auto_init: Whether to initialize with README

        Returns:
            Repository object
        """
        try:
            repo = self.user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=auto_init,
                has_issues=True,
                has_wiki=False,
                has_downloads=True
            )
            logger.info(f"Created repository: {repo.full_name}")
            return repo
        except Exception as e:
            if 'already exists' in str(e).lower():
                logger.info(f"Repository {name} already exists, fetching it")
                return self.user.get_repo(name)
            raise

    def get_repository(self, repo_name: str):
        """
        Get an existing repository.

        Args:
            repo_name: Repository name (owner/repo or just repo)

        Returns:
            Repository object
        """
        if '/' not in repo_name:
            # Assume it's owned by the authenticated user
            repo_name = f"{self.user.login}/{repo_name}"
        return self.client.get_repo(repo_name)

    def create_file(
        self,
        repo,
        path: str,
        content: str,
        message: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Create a new file in the repository.

        Args:
            repo: Repository object
            path: File path in the repo
            content: File content
            message: Commit message
            branch: Branch name

        Returns:
            Commit information
        """
        try:
            result = repo.create_file(
                path=path,
                message=message,
                content=content,
                branch=branch
            )
            logger.info(f"Created file: {path}")
            return result
        except Exception as e:
            logger.error(f"Failed to create file {path}: {e}")
            raise

    def update_file(
        self,
        repo,
        path: str,
        content: str,
        message: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Update an existing file in the repository.

        Args:
            repo: Repository object
            path: File path in the repo
            content: New file content
            message: Commit message
            branch: Branch name

        Returns:
            Commit information
        """
        try:
            file = repo.get_contents(path, ref=branch)
            result = repo.update_file(
                path=path,
                message=message,
                content=content,
                sha=file.sha,
                branch=branch
            )
            logger.info(f"Updated file: {path}")
            return result
        except Exception as e:
            logger.error(f"Failed to update file {path}: {e}")
            raise

    def file_exists(self, repo, path: str, branch: str = "main") -> bool:
        """
        Check if a file exists in the repository.

        Args:
            repo: Repository object
            path: File path
            branch: Branch name

        Returns:
            True if file exists, False otherwise
        """
        try:
            repo.get_contents(path, ref=branch)
            return True
        except:
            return False

    def get_file_content(
        self,
        repo,
        path: str,
        branch: str = "main"
    ) -> Optional[str]:
        """
        Get the content of a file from the repository.

        Args:
            repo: Repository object
            path: File path
            branch: Branch name

        Returns:
            File content as string or None if not found
        """
        try:
            file = repo.get_contents(path, ref=branch)
            if isinstance(file, list):
                return None
            return base64.b64decode(file.content).decode('utf-8')
        except:
            return None

    def list_directory(
        self,
        repo,
        path: str = "",
        branch: str = "main"
    ) -> List[str]:
        """
        List files and directories at a given path.

        Args:
            repo: Repository object
            path: Directory path
            branch: Branch name

        Returns:
            List of file/directory paths
        """
        try:
            contents = repo.get_contents(path, ref=branch)
            if isinstance(contents, list):
                return [item.path for item in contents]
            return [contents.path]
        except:
            return []

    def create_or_update_file(
        self,
        repo,
        path: str,
        content: str,
        message: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Create a file if it doesn't exist, update if it does.

        Args:
            repo: Repository object
            path: File path
            content: File content
            message: Commit message
            branch: Branch name

        Returns:
            Commit information
        """
        if self.file_exists(repo, path, branch):
            return self.update_file(repo, path, content, message, branch)
        else:
            return self.create_file(repo, path, content, message, branch)
