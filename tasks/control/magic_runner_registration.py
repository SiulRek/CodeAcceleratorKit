import json
import os
import warnings

from tasks.configs.constants import REGISTERED_RUNNERS_JSON
from tasks.tasks.management.task_manager import TaskManager
from tasks.tasks.management.normalize_path import normalize_path

TASKS_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
TASKS_ROOT = normalize_path(TASKS_ROOT)
MAIN_VSCODE_TASKS_JSON = os.path.join(TASKS_ROOT, ".vscode", "tasks.json")


def allocate_vscode_tasks_json(runner_root):
    """
    Allocates the '.vscode/tasks.json' file from the main tasks root to the
    target runner root. If the file already exists in the target runner root,
    the tasks are appended to the existing file. The file is created if it does
    not exist.

    Args:
        - runner_root (str): The root directory of the runner.
    """
    with open(MAIN_VSCODE_TASKS_JSON, "r", encoding="utf-8") as f:
        main_vscode_tasks = json.load(f)

    runner_vscode_tasks_json = os.path.join(runner_root, ".vscode", "tasks.json")
    os.makedirs(os.path.dirname(runner_vscode_tasks_json), exist_ok=True)
    if os.path.exists(runner_vscode_tasks_json):
        with open(runner_vscode_tasks_json, "r", encoding="utf-8") as f:
            runner_vscode_tasks = json.load(f)
        runner_labels = [task["label"] for task in runner_vscode_tasks["tasks"]]
        for task in main_vscode_tasks["tasks"]:
            task_label = task["label"]
            if task_label in runner_labels:
                warnings.warn(
                    f"Task '{task_label}' already present in '{runner_vscode_tasks_json}, will be replaced.'"
                )
                runner_vscode_tasks["tasks"] = [
                    t if t["label"] != task_label else task
                    for t in runner_vscode_tasks["tasks"]
                ]
            else:
                runner_vscode_tasks["tasks"].append(task)
    else:
        runner_vscode_tasks = main_vscode_tasks

    with open(runner_vscode_tasks_json, "w", encoding="utf-8") as f:
        json.dump(runner_vscode_tasks, f, indent=4)


def magic_runner_registration(
    runner_root,
    python_env,
    storage_dir="local/tasks_storage",
    overwrite=False,
    create_dirs=True,
    cwd=None,
):
    """
    A Magic runners registration function for lazy people like me.
    Not only registers the runner but also copies the data files from the main
    tasks root to the target runner root and allocates the '.vscode/tasks.json'.

    Args:
        - runner_root (str): The root directory of the runner.
        - python_env (str): The path to the python environment directory.
        - storage_dir (str): The path to the storage directory.
        - overwrite (bool): Whether to overwrite the existing runner registration.
        - create_dirs (bool): Whether to create the directories if they do not exist.
        - cwd (str): The current working directory for the runner.
    """
    TaskManager.register_runner(
        runner_root,
        python_env=python_env,
        storage_dir=storage_dir,
        overwrite=overwrite,
        create_dirs=create_dirs,
        cwd=cwd,
    )
    with open(REGISTERED_RUNNERS_JSON, "r", encoding="utf-8") as f:
        registered_runners = json.load(f)
    if not TASKS_ROOT in registered_runners:
        warnings.warn("Main Runner 'TASKS_ROOT' not registered")
    else:
        TaskManager.copy_data_files(
            source_runner_dir=TASKS_ROOT,
            dest_runner_dir=runner_root,
        )
    allocate_vscode_tasks_json(runner_root)
    print(f"Runner '{runner_root}' registered successfully.")


if __name__ == "__main__":
    magic_runner_registration(
        runner_root="/home/krakerlu/github/CodeAcceleratorKitTest",
        python_env="/home/krakerlu/github/CodeAcceleratorKitTest/venv",
        # storage_dir="/path/to/runner/storage",
        # cwd="/path/to/runner/cwd",
        # overwrite=True
        # create_dirs=True
    )