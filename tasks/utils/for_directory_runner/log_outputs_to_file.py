from contextlib import contextmanager
import sys


@contextmanager
def log_outputs_to_file(log_file_path, append=False):
    """
    Context manager to log stdout and stderr output to a file and suppress.

    Args:
        - log_file_path (str): Path to the log file where output should be
            written.
        - append (bool): If True, append to the log file. If False, overwrite
    """
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    mode = "a" if append else "w"
    with open(log_file_path, mode) as log_file:
        sys.stdout = log_file
        sys.stderr = log_file
        try:
            yield
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
