import os
import subprocess


def is_library_installed(req, venv_path):
    """
    Check if the 'black' library is installed in the specified virtual
    environment.

    Parameters
    ----------
    req (str)
        The name of the library to check.
    venv_path (str)
        Path to the virtual environment.

    Returns
    -------
    bool
        True if 'black' is installed, False otherwise.
    """
    try:
        python_executable = os.path.join(
            venv_path, "Scripts" if os.name == "nt" else "bin", "python"
        )

        command = [python_executable, "-m", "pip", "show", req]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return result.returncode == 0
    except Exception as e:
        raise ValueError(f"Error checking if {req} is installed.") from e
    

def install_library(req, venv_path):
    """
    Install the 'black' library in the specified virtual environment.

    Parameters
    ----------
    req (str)
        The name of the library to install.
    venv_path (str)
        Path to the virtual environment.

    Returns
    -------
    bool
        True if 'black' is installed, False otherwise.
    """
    if not input(
        f"Library '{req}' is not installed. Do you want to install it? (y/n): "
    ).lower() == "y":
        return False
    try:
        python_executable = os.path.join(
            venv_path, "Scripts" if os.name == "nt" else "bin", "python"
        )

        command = [python_executable, "-m", "pip", "install", req]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return result.returncode == 0
    except Exception as e:
        raise ValueError(f"Error installing {req}.") from e
    