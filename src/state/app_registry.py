"""
Registry of all generated applications.
Tracks app metadata and provides query capabilities.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AppRegistry:
    """Registry of generated applications"""

    def __init__(self, registry_file: Path):
        self.registry_file = registry_file
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        """Load registry from JSON file"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Failed to load registry file, using empty registry")
                return self._default_registry()
        return self._default_registry()

    def _default_registry(self) -> Dict[str, Any]:
        """Create default registry structure"""
        return {
            'version': '1.0.0',
            'apps': []
        }

    def save(self):
        """Save registry to file"""
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
        logger.debug(f"Registry saved to {self.registry_file}")

    def register_app(self, app_data: Dict[str, Any]):
        """
        Register a new application.

        Args:
            app_data: App metadata (name, category, path, aws_services, etc.)
        """
        if 'created_at' not in app_data:
            app_data['created_at'] = datetime.now().isoformat()

        if 'id' not in app_data:
            app_data['id'] = f"app_{len(self.registry['apps']) + 1}"

        self.registry['apps'].append(app_data)
        self.save()
        logger.info(f"Registered app: {app_data.get('name', 'Unknown')}")

    def app_exists(self, app_name: str) -> bool:
        """Check if an app with the given name exists"""
        return any(app['name'] == app_name for app in self.registry['apps'])

    def get_app(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Get an app by name"""
        for app in self.registry['apps']:
            if app['name'] == app_name:
                return app
        return None

    def get_all_apps(self) -> List[Dict[str, Any]]:
        """Get all registered apps"""
        return self.registry['apps']

    def get_apps_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all apps in a specific category"""
        return [app for app in self.registry['apps'] if app.get('category') == category]

    def get_apps_by_aws_service(self, service: str) -> List[Dict[str, Any]]:
        """Get all apps using a specific AWS service"""
        return [
            app for app in self.registry['apps']
            if service in app.get('aws_services', [])
        ]

    def update_app(self, app_name: str, updates: Dict[str, Any]):
        """Update an existing app's metadata"""
        for app in self.registry['apps']:
            if app['name'] == app_name:
                app.update(updates)
                app['updated_at'] = datetime.now().isoformat()
                self.save()
                logger.info(f"Updated app: {app_name}")
                return
        logger.warning(f"App not found for update: {app_name}")

    def get_total_apps(self) -> int:
        """Get total number of registered apps"""
        return len(self.registry['apps'])
