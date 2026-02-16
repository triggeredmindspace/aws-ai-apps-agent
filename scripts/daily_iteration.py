"""
Main entry point for daily automated iterations.
Orchestrates the generation, improvement, and documentation of apps.
"""

import sys
from pathlib import Path
import random
from typing import List
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.llm.client import create_llm_client
from src.github.client import GitHubClient
from src.generators.idea_generator import IdeaGenerator
from src.generators.code_generator import CodeGenerator
from src.quality.code_reviewer import CodeReviewer
from src.quality.bug_fixer import BugFixer
from src.state.state_manager import StateManager
from src.state.app_registry import AppRegistry
from src.utils.logger import get_logger, setup_logging
from src.utils.file_operations import write_files_to_disk

logger = get_logger(__name__)


class DailyIterator:
    """Orchestrates daily iteration of the repository"""

    def __init__(self):
        setup_logging()
        self.config = Config()
        self.llm = create_llm_client(
            self.config.llm.provider,
            self.config.llm.api_key,
            self.config.llm.model
        )
        self.state = StateManager(self.config.project_root / 'data' / 'state.json')
        self.registry = AppRegistry(self.config.project_root / 'data' / 'app_registry.json')

        # Initialize generators
        self.idea_gen = IdeaGenerator(self.llm, self.registry)
        self.code_gen = CodeGenerator(self.llm)

        # Initialize quality tools
        self.code_reviewer = CodeReviewer(self.llm)
        self.bug_fixer = BugFixer(self.llm)

    def run(self):
        """Run a daily iteration"""
        logger.info("Starting daily iteration")

        iteration_summary = {
            'new_apps': [],
            'bugs_fixed': [],
            'improvements': [],
            'docs_updated': []
        }

        try:
            # 1. Generate new applications (only on designated day, e.g. Monday)
            today = datetime.now().weekday()  # 0=Monday, 6=Sunday
            if today == self.config.generation.new_app_day:
                logger.info("It's new app day! Generating new applications...")
                new_apps = self._generate_new_apps()
                iteration_summary['new_apps'] = new_apps
            else:
                logger.info(f"Skipping new app generation (runs on day {self.config.generation.new_app_day}, today is {today})")

            # 2. Fix bugs in existing apps (if any exist)
            if self.registry.get_total_apps() > 0 and self.config.generation.bug_fixes_per_day > 0:
                logger.info("Reviewing and fixing bugs...")
                bugs_fixed = self._fix_bugs()
                iteration_summary['bugs_fixed'] = bugs_fixed
            else:
                logger.info("No existing apps to review yet")

            # 3. Record iteration
            self.state.record_iteration(iteration_summary)

            # 4. Generate commit message
            commit_msg = self._generate_commit_message(iteration_summary)
            self._save_commit_message(commit_msg)

            logger.info("Daily iteration completed successfully")
            self._generate_summary_report(iteration_summary)

        except Exception as e:
            logger.error(f"Daily iteration failed: {e}", exc_info=True)
            raise

    def _generate_new_apps(self) -> List[str]:
        """Generate new applications"""
        new_apps = []
        target_path = self.config.github.target_repo_path

        if not target_path:
            logger.error("TARGET_REPO_PATH not set in environment")
            return new_apps

        for _ in range(self.config.generation.new_apps_per_week):
            try:
                # Select category
                category = self._select_category()

                # Select AWS services
                aws_services = self._select_aws_services()

                # Generate idea
                logger.info(f"Generating idea for category: {category}")
                idea = self.idea_gen.generate_idea(category, aws_services)

                # Generate code
                logger.info(f"Generating code for: {idea['name']}")
                files = self.code_gen.generate_app(idea, category, target_path)

                # Write files to disk
                app_path = target_path / category / self._slugify(idea['name'])
                write_files_to_disk(app_path, files)

                # Register app
                self.registry.register_app({
                    'name': idea['name'],
                    'category': category,
                    'path': str(app_path.relative_to(target_path)),
                    'aws_services': idea['aws_services'],
                    'created_at': datetime.now().isoformat()
                })

                # Update stats
                self.state.update_stats('total_apps_generated')

                new_apps.append(idea['name'])
                logger.info(f"✅ Generated app: {idea['name']}")

            except Exception as e:
                logger.error(f"Failed to generate app: {e}")

        return new_apps

    def _fix_bugs(self) -> List[str]:
        """Fix bugs in existing applications"""
        bugs_fixed = []
        target_path = self.config.github.target_repo_path

        if not target_path:
            return bugs_fixed

        # Get random apps to review
        apps = self.registry.get_all_apps()
        if not apps:
            return bugs_fixed

        apps_to_review = random.sample(
            apps,
            min(self.config.generation.bug_fixes_per_day, len(apps))
        )

        for app in apps_to_review:
            try:
                app_path = target_path / app['path']

                # Review code
                issues = self.code_reviewer.review_app(app_path)

                if issues:
                    # Fix issues
                    fixes = self.bug_fixer.fix_issues(app_path, issues)

                    if fixes:
                        bugs_fixed.append(f"{app['name']}: {len(fixes)} bugs fixed")
                        self.state.update_stats('total_bugs_fixed', len(fixes))
                        logger.info(f"✅ Fixed {len(fixes)} bugs in {app['name']}")
            except Exception as e:
                logger.error(f"Failed to review/fix {app.get('name', 'unknown')}: {e}")

        return bugs_fixed

    def _select_category(self) -> str:
        """Select a category based on priority and balance"""
        categories = self.config.categories['categories']

        # Weight by priority and inverse of current app count
        weights = []
        for cat in categories:
            cat_state = self.state.get_category_state(cat['name'])
            app_count = cat_state.get('apps_count', 0)
            priority = cat['priority']

            # Higher priority and fewer apps = higher weight
            weight = priority * (1.0 / (app_count + 1))
            weights.append(weight)

        # Random selection based on weights
        selected = random.choices(categories, weights=weights)[0]

        # Update category state
        self.state.update_category_state(
            selected['name'],
            {'apps_count': self.state.get_category_state(selected['name']).get('apps_count', 0) + 1}
        )

        return selected['name']

    def _select_aws_services(self) -> List[str]:
        """Select AWS services to use in the app"""
        services = self.config.aws_services['services']

        # Select 2-4 services weighted by priority
        service_list = list(services.keys())
        weights = [services[s]['priority'] for s in service_list]

        num_services = random.randint(2, 4)
        selected = random.choices(service_list, weights=weights, k=num_services)

        return selected

    def _generate_commit_message(self, summary: dict) -> str:
        """Generate a descriptive commit message"""
        parts = []

        if summary['new_apps']:
            parts.append(f"add {len(summary['new_apps'])} new app(s)")
        if summary['bugs_fixed']:
            parts.append(f"fix {len(summary['bugs_fixed'])} bug(s)")
        if summary['improvements']:
            parts.append(f"improve {len(summary['improvements'])} app(s)")
        if summary['docs_updated']:
            parts.append(f"update {len(summary['docs_updated'])} doc(s)")

        if not parts:
            return "chore: daily repository maintenance"

        message = "feat: " + ", ".join(parts)

        # Add detailed body
        body_parts = []
        if summary['new_apps']:
            body_parts.append("\nNew applications:")
            for app in summary['new_apps']:
                body_parts.append(f"- {app}")

        if body_parts:
            message += "\n" + "\n".join(body_parts)

        message += "\n\nCo-Authored-By: AWS AI Apps Bot <bot@awesome-aws-ai-apps.dev>"

        return message

    def _save_commit_message(self, message: str):
        """Save commit message for GitHub Actions"""
        msg_file = self.config.project_root / 'data' / 'last_commit_message.txt'
        msg_file.parent.mkdir(parents=True, exist_ok=True)
        msg_file.write_text(message)

    def _generate_summary_report(self, summary: dict):
        """Generate summary report for GitHub Actions"""
        report = f"""# Daily Iteration Summary

## New Applications ({len(summary['new_apps'])})
{self._format_list(summary['new_apps'])}

## Bugs Fixed ({len(summary['bugs_fixed'])})
{self._format_list(summary['bugs_fixed'])}

## Improvements ({len(summary['improvements'])})
{self._format_list(summary['improvements'])}

## Documentation Updates ({len(summary['docs_updated'])})
{self._format_list(summary['docs_updated'])}

---
*Generated at {datetime.now().isoformat()}*
"""

        print(report)

        # Save to file for GitHub Actions summary
        summary_file = self.config.project_root / 'data' / 'iteration_summary.md'
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        summary_file.write_text(report)

    def _format_list(self, items: List[str]) -> str:
        """Format list for markdown"""
        if not items:
            return "*None*"
        return '\n'.join(f"- {item}" for item in items)

    def _slugify(self, text: str) -> str:
        """Convert text to slug"""
        return text.lower().replace(' ', '-').replace('_', '-')


if __name__ == '__main__':
    iterator = DailyIterator()
    iterator.run()
