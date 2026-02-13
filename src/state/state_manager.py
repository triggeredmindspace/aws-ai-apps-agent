"""
Manage persistent state for the automation system.
Tracks what has been generated, what needs fixing, etc.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class StateManager:
    """Manage automation state"""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load state from JSON file"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Failed to load state file, using default state")
                return self._default_state()
        return self._default_state()

    def _default_state(self) -> Dict[str, Any]:
        """Create default state structure"""
        return {
            'version': '1.0.0',
            'initialized_at': datetime.now().isoformat(),
            'last_iteration': None,
            'stats': {
                'total_apps_generated': 0,
                'total_bugs_fixed': 0,
                'total_improvements': 0,
                'total_doc_updates': 0
            },
            'pending_tasks': [],
            'completed_tasks': [],
            'categories': {}
        }

    def save(self):
        """Save state to file"""
        self.state['last_updated'] = datetime.now().isoformat()
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
        logger.debug(f"State saved to {self.state_file}")

    def add_task(self, task: Dict[str, Any]):
        """Add a pending task"""
        task['created_at'] = datetime.now().isoformat()
        task['status'] = 'pending'
        if 'id' not in task:
            task['id'] = f"task_{len(self.state['pending_tasks']) + 1}_{datetime.now().timestamp()}"
        self.state['pending_tasks'].append(task)
        self.save()

    def complete_task(self, task_id: str):
        """Mark a task as completed"""
        for task in self.state['pending_tasks']:
            if task.get('id') == task_id:
                task['status'] = 'completed'
                task['completed_at'] = datetime.now().isoformat()
                self.state['completed_tasks'].append(task)
                self.state['pending_tasks'].remove(task)
                self.save()
                break

    def get_pending_tasks(self, task_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get pending tasks, optionally filtered by type"""
        if task_type:
            return [t for t in self.state['pending_tasks'] if t.get('type') == task_type]
        return self.state['pending_tasks']

    def update_stats(self, stat_name: str, increment: int = 1):
        """Update statistics"""
        if stat_name in self.state['stats']:
            self.state['stats'][stat_name] += increment
        else:
            self.state['stats'][stat_name] = increment
        self.save()

    def record_iteration(self, iteration_data: Dict[str, Any]):
        """Record data from a daily iteration"""
        self.state['last_iteration'] = {
            'timestamp': datetime.now().isoformat(),
            **iteration_data
        }
        self.save()

    def get_category_state(self, category: str) -> Dict[str, Any]:
        """Get state for a specific category"""
        if category not in self.state['categories']:
            self.state['categories'][category] = {
                'apps_count': 0,
                'last_app_generated': None
            }
        return self.state['categories'][category]

    def update_category_state(self, category: str, data: Dict[str, Any]):
        """Update category state"""
        if category not in self.state['categories']:
            self.state['categories'][category] = {}
        self.state['categories'][category].update(data)
        self.save()
