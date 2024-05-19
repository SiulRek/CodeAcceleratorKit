from enum import Enum


class ContextAttrNames(Enum):
    """Enumeration for context attribute names."""
    # All directory path attributes should end with "_dir"
    # The dirs should be placed first in the enumeration
    cwd = "cwd"
    python_env = "python_env"
