import os
import sys
import shutil
import subprocess

def execute_python_module(module, env_python_path, cwd=None, temp_script_path=None, args=None):
    """
    Executes a specified Python module using a designated Python interpreter
    from a virtual environment, potentially in a different working directory or
    a temporary location. This function supports passing additional arguments
    to the script. It captures and returns the script's standard output. If an
    error occurs during the script's execution, it captures and returns the
    error output.

    Parameters
    ----------
    script (str)
        The path to or the module of the Python script to run.
    env_python_path (str)
        The path to the Python interpreter in the virtual environment.
    cwd (str)
        The current working directory for the script execution. Default is
        None.
    temp_script_path (str)
        The path to copy the script to before. Useful when the script is
        located in a different workspace. Default is None.
    args (list)
        The list of arguments to pass to the script. Default is None.

    Returns
    -------
    str
        The output from the script execution or an error message if execution
        fails.
    """
    if hasattr(module, "__file__"):
        module = module.__file__
    
    if temp_script_path:
        shutil.copy(module, temp_script_path)
        module = temp_script_path
        
    if sys.platform == "win32" or sys.platform == "win64":
        python_path = os.path.join(env_python_path, "Scripts", "python")
    else:
        python_path = os.path.join(env_python_path, "bin", "python")

    try:
        command = [python_path, "-u", module]
        if args:
            command.extend(args)
        
        env = os.environ.copy()
        if cwd:
            env['PYTHONPATH'] = cwd + os.pathsep + env.get('PYTHONPATH', '')

        completed_process = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            env=env
        )
        
        return completed_process.stdout
    except subprocess.CalledProcessError as e:
        return (
            f"Error running script: {e}\nOutput: {e.output}\nError Output: {e.stderr}"
        )
    finally:
        if temp_script_path:
            os.remove(temp_script_path)

if __name__ == "__main__":
    script_path = "/path/to/script.py"
    env_python_path = "path/to/python/env"
    cwd = "/path/to/cwd"
    script_output = execute_python_module(script_path, env_python_path, cwd=cwd)
    print(script_output)
