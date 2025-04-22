import os


def normalize_path(path):
    """
    Normalizes a file path to use forward slashes.

    Parameters
    ----------
    path (str)
        The file path to normalize.

    Returns
    -------
    str
        The normalized file path.
    """
    path = os.path.normpath(path)
    path = path.replace(os.sep, "/")
    return path
