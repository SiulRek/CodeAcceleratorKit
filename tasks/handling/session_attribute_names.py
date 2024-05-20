from enum import Enum


class SessionAttrNames(Enum):
    """Enumeration for context attribute names."""
    # All directory path attributes should end with "_dir"
    # The dirs should be placed first in the enumeration
    cwd = (1, "configs.json")
    python_env = (2, "configs.json")
