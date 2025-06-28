import argparse

from tasks.controllers.shared.TASKS_ROOT import TASKS_ROOT
from tasks.controllers.shared.allocate_vscode_tasks_json import (
    allocate_vscode_tasks_json,
)
from tasks.management.task_manager import TaskManager
from tasks.utils.shared.library_utils import is_library_installed, install_library


def magic_register_runner(
    runner_root,
    python_env,
    storage_dir=None,
    overwrite=False,
    create_dirs=True,
    cwd=None,
):
    """
    A Magic runners registration function for lazy people like me. Not only
    registers the runner but also copies the templates files from the main
    tasks root to the target runner root and allocates the
    '.vscode/tasks.json'.

    Parameters
    ----------
    runner_root (str)
        The root directory of the runner.
    python_env (str)
        The path to the python environment directory.
    storage_dir (str)
        The path to the storage directory.
    overwrite (bool)
        Whether to overwrite the existing runner registration.
    create_dirs (bool)
        Whether to create the directories if they do not exist.
    cwd (str)
        The current working directory for the runner.
    """
    try:
        TaskManager.login_runner(TASKS_ROOT)
    except Exception as e:
        raise Exception("Probably main runner not registered") from e

    try:
        TaskManager.login_runner(runner_root)
        raise Exception(f"Runner '{runner_root}' already registered.")
    except Exception as e:
        pass
    
    storage_dir = storage_dir or f"{runner_root}/local/tasks_storage"
    allocate_vscode_tasks_json(runner_root)
    TaskManager.register_runner(
        runner_root,
        python_env=python_env,
        storage_dir=storage_dir,
        overwrite=overwrite,
        create_dirs=create_dirs,
        cwd=cwd,
    )
    TaskManager.copy_costumizations_files(
        source_runner=TASKS_ROOT,
        dest_runner=runner_root,
    )
    print(f"Runner '{runner_root}' registered successfully.")


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Register a runner with the main tasks root."
    )
    parser.add_argument(
        "runner_root",
        type=str,
        help="The root directory of the runner.",
    )
    parser.add_argument(
        "--python_env",
        type=str,
        default=None,
        help="The path to the python environment directory (optional).",
    )
    args = parser.parse_args()
    runner_root = args.runner_root
    python_env = args.python_env if args.python_env else f"{runner_root}/venv"

    return runner_root, python_env


if __name__ == "__main__":
    runner_root, runner_env = _parse_args()

    for lib in ["black", "pylint", "stdlib-list"]:
        if is_library_installed(lib, runner_env):
            continue
        if not install_library(lib, runner_env):
            msg = f"Library '{lib}' not installed in the specified virtual"
            msg += "environment."
            raise ValueError(msg)
    magic_register_runner(
        runner_root=runner_root,
        python_env=runner_env,
    )
