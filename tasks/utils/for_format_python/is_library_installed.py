import subprocess


def is_library_installed(env_path, library_name):
    """
    Check if a specific library is installed in a given Python environment.

    Parameters:
        - env_path (str): Path to the Python environment.
        - library_name (str): Name of the library to check.

    Returns:
        - bool: True if the library is installed, False otherwise.
    """
    try:
        command = [env_path, "-m", "pip", "show", library_name]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

