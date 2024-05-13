import os
import sys
import shutil
import subprocess


def execute_python_script(script, env_python_path, cwd=None, temp_script_path=None, args=None):
    """
    Executes a specified Python script using a designated Python interpreter from a virtual environment,
    potentially in a different working directory or a temporary location. This function supports passing 
    additional arguments to the script. It captures and returns the script's standard output. If an error 
    occurs during the script's execution, it captures and returns the error output.

    Args:
        - script (str): The path to or the module of the Python script to run.
        - env_python_path (str): The path to the Python interpreter in the
            virtual environment.
        - cwd (str): The current working directory for the script execution.
            Default is None.
        - temp_script_path (str): The path to copy the script to before. Useful
            when the script is located in a different workspace. Default is None.
        - args (list): The list of arguments to pass to the script. Default is None.

    Returns:
        - str: The output from the script execution or an error message if
            execution fails.
    """
    if hasattr(script, "__file__"):
        script = script.__file__
    
    if temp_script_path:
        shutil.copy(script, temp_script_path)
        script = temp_script_path
        
    if sys.platform == "win32":
        python_path = os.path.join(env_python_path, "Scripts", "python")
    else:
        python_path = os.path.join(env_python_path, "bin", "python")

    try:
        command = [python_path, "-u", script]
        if args:
            command.extend(args)
        if cwd:
            completed_process = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True,
            )
        else:
            completed_process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
        )
        return completed_process.stdout
    except subprocess.CalledProcessError as e:
        return (
            f"Error running script: {e}\nOutput: {e.output}\nError Output: {e.stderr}"
        )


if __name__ == "__main__":
    script_path = "/path/to/python/script.py"
    env_python_path = "path/to/python/interpreter"
    script_output = execute_python_script(script_path, env_python_path)
    with open("output.txt", "w") as output_file:
        output_file.write(script_output)
