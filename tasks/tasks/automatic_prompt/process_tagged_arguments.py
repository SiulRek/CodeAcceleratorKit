from tasks.configs.constants import CURRENT_FILE_TAG, CURRENT_DIRECTORY_TAG
from tasks.utils.shared.find_dir_sloppy import find_dir_sloppy
from tasks.utils.shared.find_file_sloppy import find_file_sloppy


def process_tagged_arguments(arguments, root_dir, reference_file):
    """
    Process arguments that include special tags for files or directories.

    Parameters
    ----------
    arguments (tuple)
        The tuple of arguments to process.
    root_dir (str)
        The root directory to use for finding files and directories.
    reference_file (str)
        The reference file to use for finding files

    Returns
    -------
    tuple
        Processed arguments where special tags have been replaced with actual
        paths.
    """
    updated_arguments = []
    for arg in arguments:
        if not isinstance(arg, str):
            updated_arguments.append(arg)
            continue
        if arg.startswith(f"{CURRENT_FILE_TAG}="):
            arg = arg.replace(f"{CURRENT_FILE_TAG}=", "")
            arg = find_file_sloppy(arg.strip(), root_dir, reference_file)
        elif arg.startswith(f"{CURRENT_DIRECTORY_TAG}="):
            arg = arg.replace(f"{CURRENT_DIRECTORY_TAG}=", "")
            arg = find_dir_sloppy(arg.strip(), root_dir, reference_file)
        updated_arguments.append(arg)
    return tuple(updated_arguments)
