import os

from tasks.configs.constants import CURRENT_DIRECTORY_TAG


def _replace_current_directory_tag(path_fragment, reference_path):
    ref_is_dir = os.path.isdir(reference_path)
    reference_path = reference_path if ref_is_dir else os.path.dirname(reference_path)
    if path_fragment.startswith(CURRENT_DIRECTORY_TAG + os.sep):
        path_fragment = path_fragment[len(CURRENT_DIRECTORY_TAG) :]
        path_fragment = reference_path + path_fragment
        path_fragment = os.path.normpath(path_fragment)
    elif path_fragment == CURRENT_DIRECTORY_TAG and ref_is_dir:
        path_fragment = reference_path
    return path_fragment


def sanitize_sloppy_path_string(sloppy_string, reference_path):
    """
    Sanitizes a sloppy string by removing leading/trailing whitespaces,
    replacing backslashes and forward slashes with the appropriate operating
    system separator, and replacing the current directory tag with the
    reference path.

    Parameters
    ----------
    sloppy_string (str)
        The sloppy string to be sanitized. reference_path (str): The reference
        path used to replace the current directory tag.

    Returns
    -------
    str
        The sanitized string.
    """
    sloppy_string = sloppy_string.strip()
    sloppy_string = sloppy_string.replace("\\", os.sep).replace("/", os.sep)
    sloppy_string = _replace_current_directory_tag(sloppy_string, reference_path)
    return sloppy_string
