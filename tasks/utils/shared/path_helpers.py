import os

from tasks.configs.constants import CURRENT_DIRECTORY_TAG

class PathNotFoundError(Exception):
    pass

def standardize_path(path):
    path = os.path.abspath(path)
    path = os.path.normpath(path)
    return path


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


def sanitize_partial_path(sloppy_string, reference_path):
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


def _common_prefix_length(p1, p2):
    parts1 = p1.split(os.sep)
    parts2 = p2.split(os.sep)
    length = 0
    for a, b in zip(parts1, parts2):
        if a != b:
            break
        length += 1
    return length


def get_closest_path_from_list(path, reference_path):
    scored_paths = [
        (_common_prefix_length(reference_path, candidate), candidate)
        for candidate in path
    ]
    scored_paths.sort(reverse=True)
    best_score = scored_paths[0][0]
    best_matches = [path for score, path in scored_paths if score == best_score]
    if len(best_matches) == 1:
        return best_matches[0]
    msg = (
        "Multiple directories matching found with equal closeness to "
        f"reference '{reference_path}':\n- "
        + "\n- ".join(best_matches)
        + "\nPlease refine the input for disambiguation."
    )
    raise ValueError(msg)
        
