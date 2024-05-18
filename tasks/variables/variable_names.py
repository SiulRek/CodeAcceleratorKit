from enum import Enum


class VariableNames(Enum):
    """Enumeration for variable names."""
    # Define first dirs, than subdirs, than files and then the rest
    # Dirs should end with _DIR, files with _FILE, the rest with _VAR
    ORIGINAL = "ORIGINAL"