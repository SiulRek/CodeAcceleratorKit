import json
import os
import warnings

from tasks.control.TASK_ROOT import TASKS_ROOT

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
    if not os.path.exists(MAIN_VSCODE_TASKS_JSON):
        msg = f"The VSCODE tasks file '{MAIN_VSCODE_TASKS_JSON}' does not"
        msg += f"exist."
        raise FileNotFoundError(msg)
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
