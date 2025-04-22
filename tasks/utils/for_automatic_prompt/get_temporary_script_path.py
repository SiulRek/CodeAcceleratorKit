import os
def get_temporary_script_path(temporary_dir):
    """
    Get unique temporary script path.

    Parameters
    ----------
    temporary_dir (str)
        The directory to save the temporary script.

    Returns
    -------
    str
        The path to the temporary script.
    """
    if not os.path.exists(temporary_dir):
        raise NotADirectoryError(f"Temporary directory {temporary_dir} does not exist.")
    
    script_name = "temp_script.py"
    counter = 1
    while True:
        script_path = os.path.join(temporary_dir, script_name)
        if not os.path.exists(script_path):
            return script_path
        script_name = f"{script_name}_{counter}"
        counter += 1