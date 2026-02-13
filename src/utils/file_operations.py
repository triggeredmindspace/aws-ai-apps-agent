"""
File system operations utilities.
"""

from pathlib import Path
from typing import Dict
from src.utils.logger import get_logger

logger = get_logger(__name__)


def write_files_to_disk(base_path: Path, files: Dict[str, str]) -> None:
    """
    Write multiple files to disk.

    Args:
        base_path: Base directory path
        files: Dict mapping relative file paths to their content
    """
    base_path.mkdir(parents=True, exist_ok=True)

    for file_path, content in files.items():
        full_path = base_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Written file: {full_path}")


def read_file(file_path: Path) -> str:
    """
    Read file content.

    Args:
        file_path: Path to file

    Returns:
        File content as string
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def ensure_directory(directory: Path) -> None:
    """
    Ensure directory exists, create if it doesn't.

    Args:
        directory: Directory path
    """
    directory.mkdir(parents=True, exist_ok=True)
