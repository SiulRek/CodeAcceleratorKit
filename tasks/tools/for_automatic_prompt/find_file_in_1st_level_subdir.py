import os


def find_file_in_1st_level_subdir(file_name, directory, prettify=False):
    """
    Find a file by name in the given directory within its first-level subdirectories.

    Args:
        - file_name (str): The name of the file to search for (without extension).
        - directory (str): The directory to search within.
        - prettify (bool): If True, prettify the subdirectory name to use as a title.

    Returns:
        - tuple: A tuple containing the file path and the subdirectory name.
    """
    if not os.path.exists(directory):
        msg = f"Directory {directory} does not exist."
        raise NotADirectoryError(msg)
    
    for root, _, files in os.walk(directory):
        # Only 1. level subdirectories
        if os.path.dirname(root) != directory:
            continue
        files = [os.path.splitext(file) for file in files]
        for file in files:
            if file[0] == file_name:
                subdir_name = os.path.basename(root)
                if prettify:
                    title_parts = subdir_name.split("_")
                    subdir_name = " ".join([word.capitalize() for word in title_parts])
                file_path = os.path.join(root, f"{file[0]}{file[1]}")
                return file_path, subdir_name
    
    msg = f"File with name {file_name} not found."
    raise FileNotFoundError(msg)
