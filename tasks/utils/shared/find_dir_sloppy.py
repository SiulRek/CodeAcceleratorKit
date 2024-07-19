import os

from tasks.utils.shared.sloppy_paths_utils import (
    _replace_current_directory_tag,
    sanitize_sloppy_path_string,
)


def find_nearest_dir(dir_name, root_dir, reference_dir):
    def compute_distance(path1_parts, path2_parts):
        matching_parts = 0
        for part1, part2 in zip(path1_parts, path2_parts):
            if part1 == part2:
                matching_parts += 1
            else:
                break
        return matching_parts

    root_dir = os.path.abspath(root_dir)
    reference_dir = os.path.abspath(reference_dir)
    closest_dir = None
    max_matching_parts = -1

    if dir_name == ".":
        return root_dir

    reference_relative_path = os.path.relpath(reference_dir, root_dir).split(os.sep)

    for dirpath, dirnames, _ in os.walk(root_dir):
        if dir_name in dirnames:
            current_dir = os.path.join(dirpath, dir_name)
            current_relative_path = os.path.relpath(current_dir, root_dir).split(os.sep)

            matching_parts = compute_distance(
                current_relative_path, reference_relative_path
            )

            if matching_parts > max_matching_parts:
                max_matching_parts = matching_parts
                closest_dir = current_dir

    if not closest_dir:
        msg = f"Directory '{dir_name}' not found near '{reference_dir}'"
        raise NotADirectoryError(msg)

    return closest_dir


def find_dir_from_path_fragment(path_fragment, root_dir, reference_dir):
    for dirpath, _, _ in os.walk(root_dir):
        if dirpath.endswith(path_fragment):
            return dirpath

    msg = f"Directory from fragment '{path_fragment}' not found in '{root_dir}'"
    raise NotADirectoryError(msg)


def find_dir_sloppy(sloppy_string, root_dir, reference_dir):
    """
    Function to find the directory from a "sloppy" (partial or incomplete path)
    written string. The function expects the directory to be found in the root
    directory. If the string contains a path fragment, the function will search
    for the directory from the path fragment. If the string contains only the
    directory name, the function will search for the nearest directory to the
    reference directory.

    Args:
        - string (str): The string to be searched, which could be a path
            fragment or directory name.
        - root_dir (str): The root directory of the project.
        - reference_dir (str): The path to the reference directory, used
            when finding the nearest directory.

    Returns:
        - dir_path (str): The path to the directory.
    """
    root_dir = os.path.abspath(root_dir)
    reference_dir = os.path.abspath(reference_dir)
    root_dir = os.path.normpath(root_dir)
    reference_dir = os.path.normpath(reference_dir)

    # Reference_dir to be file should not be allowed, but
    # as it is often more convenient to use the file path
    # as reference, it is allowed here.
    if os.path.isfile(reference_dir):
        reference_dir = os.path.dirname(reference_dir)

    sloppy_string = sanitize_sloppy_path_string(sloppy_string, reference_dir)
    if os.path.isdir(sloppy_string):
        return sloppy_string

    if "\\" in sloppy_string or "/" in sloppy_string:
        dir_ = find_dir_from_path_fragment(sloppy_string, root_dir, reference_dir)
    else:
        dir_ = find_nearest_dir(sloppy_string, root_dir, reference_dir)
    return os.path.normpath(dir_)
