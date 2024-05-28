import os

from tasks.configs.constants import FILE_TAG


def find_nearest_file(file_name, root_dir, reference_file):
    root_dir = os.path.abspath(root_dir)
    reference_file = os.path.abspath(reference_file)
    closest_file = None
    min_distance = float("inf")

    if file_name == FILE_TAG:
        return reference_file
    for dirpath, _, filenames in os.walk(root_dir):
        if file_name in filenames:
            current_file = os.path.join(dirpath, file_name)
            current_relative_path = os.path.relpath(current_file, root_dir)
            reference_relative_path = os.path.relpath(reference_file, root_dir)

            current_path_parts = current_relative_path.split(os.sep)
            reference_path_parts = reference_relative_path.split(os.sep)

            distance = len(
                set(current_path_parts).symmetric_difference(set(reference_path_parts))
            )

            if distance < min_distance:
                min_distance = distance
                closest_file = current_file

    if not closest_file:
        msg = f"File '{file_name}' not found in '{root_dir}'"
        raise FileNotFoundError(msg)
    return closest_file


def find_file_from_path_fragment(path_fragment, root_dir):
    root_dir = os.path.abspath(root_dir)
    path_fragment = path_fragment.replace("\\", os.sep).replace("/", os.sep)

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename).lower()
            if path_fragment in full_path:
                return os.path.join(dirpath, filename)
    raise FileNotFoundError(
        f"File from Fragment '{path_fragment}' not found in '{root_dir}'"
    )


def find_file_sloppy(sloppy_string, root_dir, current_file_path):
    """
    Function to find the file from the string. If the string contains a path
    fragment, the function will search for the file from the path fragment. If
    the string contains only the file name, the function will search for the
    nearest file to the current file.

    Args:
        - file_name_fragment (str): The name or a fragment of the file name to search for.
        - root_dir (str): The root directory to start the search from.
        - current_file_path (str, optional): The current file path to assist in finding 
          the nearest file if not found directly under root_dir. Default is None.

    Returns:
        - file_path (str): The path to the file.
    """
    if "\\" in sloppy_string or "/" in sloppy_string:
        file = find_file_from_path_fragment(sloppy_string, root_dir)
    else:
        file = find_nearest_file(sloppy_string, root_dir, current_file_path)
    return os.path.normpath(file)