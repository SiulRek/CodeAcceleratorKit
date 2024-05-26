"""
Stores the root directory of the tasks codebase considered as the main tasks root.
"""
import os
from tasks.tasks.management.normalize_path import normalize_path

TASKS_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
TASKS_ROOT = normalize_path(TASKS_ROOT)