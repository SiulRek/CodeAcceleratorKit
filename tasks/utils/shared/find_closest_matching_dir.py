import os

from tasks.configs.constants import CURRENT_DIRECTORY_TAG
from tasks.utils.shared.sloppy_paths_utils import standardize_path


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


def _sanitize_partial_path(sloppy_string, reference_path):
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


def _get_closest_dir_from_list(dirs, reference_dir):
    scored_paths = [
        (_common_prefix_length(reference_dir, candidate), candidate)
        for candidate in dirs
    ]
    scored_paths.sort(reverse=True)
    best_score = scored_paths[0][0]
    best_matches = [path for score, path in scored_paths if score == best_score]
    if len(best_matches) == 1:
        return best_matches[0]
    if len(best_matches) > 1:
        msg = (
            "Multiple directories matching found with equal closeness to "
            f"reference '{reference_dir}':\n- "
            + "\n- ".join(best_matches)
            + "\nPlease refine the input for disambiguation."
        )
        raise ValueError(msg)
    raise NotADirectoryError(
        f"Directory not found near '{reference_dir}'"
    )


def _find_closest_dir_from_name(name, root_dir, reference_dir):
    if name == ".":
        return standardize_path(name)

    # Step 1: Collect all matching paths
    matching_dirs = [
        standardize_path(os.path.join(root_dir, d))
        for d, _, _ in os.walk(root_dir)
        if os.path.basename(d) == name
    ]
    if not matching_dirs:
        msg = f"No directory named '{name}' found under '{root_dir}'"
        raise NotADirectoryError(msg)
    if len(matching_dirs) == 1:
        return matching_dirs[0]

    # Step 2: Measure similarity by longest common prefix with reference_dir
    try:
        return _get_closest_dir_from_list(matching_dirs, reference_dir)
    except NotADirectoryError as e:
        raise NotADirectoryError(
            "Could not determine a single closest directory matching "
            f"'{name}' relative to '{reference_dir}'.\n"
        ) from e


def _find_closest_matching_dir_from_fragment(fragment, root_dir, reference_dir):
    # Step 1: Collect all matching paths
    matching_dirs = [
        standardize_path(os.path.join(root_dir, dirpath))
        for dirpath, _, _ in os.walk(root_dir)
        if dirpath.endswith(fragment)
    ]
    if not matching_dirs:
        msg = f"No directory ending with '{fragment}' found under '{root_dir}'"
        raise NotADirectoryError(msg)

    if len(matching_dirs) == 1:
        return matching_dirs[0]

    # Step 2: Measure similarity by longest common prefix with reference_dir
    try:
        return _get_closest_dir_from_list(matching_dirs, reference_dir)
    except NotADirectoryError as e:
        raise NotADirectoryError(
            "Could not determine a single closest directory matching "
            f"'{fragment}' relative to '{reference_dir}'.\n"
        ) from e


def find_closest_matching_dir(partial_path, root_dir, reference_dir):
    """
    Function to find the closest matching directory from a partial or
    incomplete path string. The function searches within the root directory and
    uses the reference directory to determine proximity or relevance. If the
    string contains a path fragment, the function will search for directories
    matching the fragment. If the string contains only a directory name, the
    function will search for the nearest directory to the reference directory.

    Parameters
    ----------
    partial_path (str)
        The string to be searched, which could be a path fragment or directory
        name.
    root_dir (str)
        The root directory of the project.
    reference_dir (str)
        The path to the reference directory, used to determine proximity when
        finding the nearest directory.

    Returns
    -------
    dir_path (str)
        The standardized path to the closest matching directory.
    """
    root_dir = standardize_path(root_dir)
    reference_dir = standardize_path(reference_dir)

    # Reference_dir to be file a file is allowed
    if os.path.isfile(reference_dir):
        reference_dir = os.path.dirname(reference_dir)

    partial_path = _sanitize_partial_path(partial_path, reference_dir)

    if "\\" in partial_path or "/" in partial_path:
        if os.path.isdir(partial_path):
            dir_ = partial_path
        else:
            dir_ = _find_closest_matching_dir_from_fragment(
                partial_path, root_dir, reference_dir
            )
    else:
        dir_ = _find_closest_dir_from_name(partial_path, root_dir, reference_dir)
    return standardize_path(dir_)
