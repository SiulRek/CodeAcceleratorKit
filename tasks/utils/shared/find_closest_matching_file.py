import os

from tasks.configs.constants import CURRENT_FILE_TAG
from tasks.utils.shared.path_helpers import (
    sanitize_partial_path,
    standardize_path,
    get_closest_path_from_list,
    PathNotFoundError,
)

def _find_closest_file_from_name(file_name, root_dir, reference_path):
    matching_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        if file_name in filenames:
            matching_files.append(os.path.join(dirpath, file_name))

    if not matching_files:
        raise FileNotFoundError(f"No file named '{file_name}' found under '{root_dir}'")

    if len(matching_files) == 1:
        return standardize_path(matching_files[0])

    return get_closest_path_from_list([standardize_path(p) for p in matching_files], reference_path)
    
def _find_closest_file_from_fragment(fragment, root_dir, reference_path):
    matching_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if full_path.endswith(fragment):
                matching_files.append(full_path)

    if not matching_files:
        raise FileNotFoundError(f"No file ending with '{fragment}' found under '{root_dir}'")

    if len(matching_files) == 1:
        return standardize_path(matching_files[0])

    return get_closest_path_from_list([standardize_path(p) for p in matching_files], reference_path)

def find_closest_matching_file(sloppy_string, root_dir, reference_file_path):
    """
    Finds the closest matching file from a partial or incomplete string.

    Parameters
    ----------
    sloppy_string : str
        A file name or fragment of a path.
    root_dir : str
        The root directory under which to search.
    reference_file_path : str
        Path used to determine proximity when resolving ambiguous matches.

    Returns
    -------
    str
        Standardized path to the closest matching file.
    """
    root_dir = standardize_path(root_dir)
    reference_file_path = standardize_path(reference_file_path)
    sloppy_string = sanitize_partial_path(sloppy_string, reference_file_path)

    if sloppy_string == CURRENT_FILE_TAG:
        return reference_file_path

    for mode, tag in [("test", CURRENT_FILE_TAG + "T"), ("source", CURRENT_FILE_TAG + "S")]:
        if sloppy_string == tag:
            ref_file_name = os.path.basename(reference_file_path)
            base, ext = os.path.splitext(ref_file_name)
            if mode == "source":
                sloppy_string = base.replace("_test", "") + ext
            else:
                sloppy_string = base + "_test" + ext

    if os.sep in sloppy_string:
        return _find_closest_file_from_fragment(sloppy_string, root_dir, reference_file_path)
    else:
        return _find_closest_file_from_name(sloppy_string, root_dir, reference_file_path)
