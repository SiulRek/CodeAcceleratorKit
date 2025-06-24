import os


def standardize_path(path):
    """
    Standardizes a file path to an absolute, normalized path using forward slashes.

    Parameters
    ----------
    path : str
        The file path to standardize.

    Returns
    -------
    str
        The standardized file path.
    """
    path = os.path.abspath(path)
    path = os.path.normpath(path)
    path = path.replace(os.sep, "/")
    return path
