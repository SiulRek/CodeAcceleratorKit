import os

from tasks.utils.shared.path_helpers import (
    standardize_path,
    sanitize_partial_path,
    get_closest_path_from_list,
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
        return get_closest_path_from_list(matching_dirs, reference_dir)
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
        return get_closest_path_from_list(matching_dirs, reference_dir)
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

    partial_path = sanitize_partial_path(partial_path, reference_dir)

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
