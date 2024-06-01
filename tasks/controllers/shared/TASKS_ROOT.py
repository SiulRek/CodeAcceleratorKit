""" Stores the root directory of the tasks codebase considered as the main tasks
root. """

from tasks.configs.constants import TASKS_ROOT
from tasks.management.normalize_path import normalize_path

TASKS_ROOT = normalize_path(TASKS_ROOT)
