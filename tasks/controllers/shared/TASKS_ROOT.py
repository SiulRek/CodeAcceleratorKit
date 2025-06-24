"""
Stores the root directory of the tasks codebase considered as the main tasks
root.
"""

from tasks.configs.constants import TASKS_ROOT
from tasks.management.standardize_path import standardize_path

TASKS_ROOT = standardize_path(TASKS_ROOT)
