from tasks.controllers.shared.TASKS_ROOT import TASKS_ROOT
from tasks.controllers.shared.allocate_vscode_tasks_json import (
    allocate_vscode_tasks_json,
)
from tasks.management.task_manager import TaskManager
from tasks.management.task_manager import TaskManager
from tasks.utils.shared.is_library_installed import is_library_installed


def magic_register_runner(
    runner_root,
    python_env,
    storage_dir="local/tasks_storage",
    overwrite=False,
    create_dirs=True,
    cwd=None,
):
    """
    A Magic runners registration function for lazy people like me. Not only
    registers the runner but also copies the templates files from the main tasks
    root to the target runner root and allocates the '.vscode/tasks.json'.

    Args:
        - runner_root (str): The root directory of the runner.
        - python_env (str): The path to the python environment directory.
        - storage_dir (str): The path to the storage directory.
        - overwrite (bool): Whether to overwrite the existing runner
            registration.
        - create_dirs (bool): Whether to create the directories if they do
            not exist.
        - cwd (str): The current working directory for the runner.
    """
    try:
        TaskManager.login_runner(TASKS_ROOT)
    except Exception as e:
        raise Exception(f"Probably main runner not registered") from e

    try:
        TaskManager.login_runner(runner_root)
        raise Exception(f"Runner '{runner_root}' already registered.")
    except Exception as e:
        pass

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
        source_runner_dir=TASKS_ROOT,
        dest_runner_dir=runner_root,
    )
    print(f"Runner '{runner_root}' registered successfully.")


if __name__ == "__main__":
    #TODO: Assign runner paths.
    runner_root = "/path/to/runner"
    runner_env = "/path/to/venv"

    for lib in ["black", "pylint", "stdlib-list"]:
        if not is_library_installed(lib, runner_env):
            msg = f"Library '{lib}' not installed in the specified virtual"
            msg += "environment."
            raise ValueError(msg)
    magic_register_runner(
        runner_root=runner_root,
        python_env=runner_env,
    )
