import json
import os
import warnings

from tasks.controllers.shared.TASKS_ROOT import TASKS_ROOT
from tasks.management.task_runner_profile import TaskRunnerProfile

MAIN_VSCODE_TASKS_JSON = os.path.join(TASKS_ROOT, ".vscode", "tasks.json")


def allocate_vscode_tasks_json(runner_root):
    """
    Allocates the '.vscode/tasks.json' file from the main tasks root to the
    target runner root. If the file already exists in the target runner root,
    the tasks are appended to the existing file. The file is created if it does
    not exist.

    Parameters
    ----------
    runner_root : str or TaskRunnerProfile
        The root directory of the runner or a TaskRunnerProfile instance.
        If a TaskRunnerProfile instance is provided, its `root` attribute will
        be used as the runner root.
    """
    if isinstance(runner_root, TaskRunnerProfile):
        runner_root = runner_root.root

    if not os.path.exists(MAIN_VSCODE_TASKS_JSON):
        msg = f"The VSCODE tasks file '{MAIN_VSCODE_TASKS_JSON}' does not"
        msg += "exist."
        raise FileNotFoundError(msg)

    with open(MAIN_VSCODE_TASKS_JSON, "r", encoding="utf-8") as f:
        main_vscode_tasks = json.load(f)

    runner_vscode_tasks_json = os.path.join(runner_root, ".vscode", "tasks.json")
    os.makedirs(os.path.dirname(runner_vscode_tasks_json), exist_ok=True)

    if os.path.exists(runner_vscode_tasks_json):
        with open(runner_vscode_tasks_json, "r", encoding="utf-8") as f:
            runner_vscode_tasks = json.load(f)
        runner_tasks_label = [
            task["label"] for task in runner_vscode_tasks.get("tasks", [])
        ]
        runner_inputs_id = [
            input["id"] for input in runner_vscode_tasks.get("inputs", [])
        ]

        for task in main_vscode_tasks["tasks"]:
            task_label = task["label"]
            if task_label in runner_tasks_label:
                msg = f"Task '{task_label}' already present in"
                msg += f"'{runner_vscode_tasks_json}', will be replaced."
                warnings.warn(msg)
                runner_vscode_tasks["tasks"] = [
                    t if t["label"] != task_label else task
                    for t in runner_vscode_tasks["tasks"]
                ]
            else:
                runner_vscode_tasks["tasks"] = runner_vscode_tasks.get("tasks", [])
                runner_vscode_tasks["tasks"].append(task)

        for input in main_vscode_tasks["inputs"]:
            input_id = input["id"]
            if input_id in runner_inputs_id:
                msg = f"Input '{input_id}' already present in"
                msg += f"'{runner_vscode_tasks_json}', will be replaced."
                warnings.warn(msg)
                runner_vscode_tasks["inputs"] = [
                    t if t["id"] != input_id else input
                    for t in runner_vscode_tasks["inputs"]
                ]
            else:
                runner_vscode_tasks["inputs"] = runner_vscode_tasks.get("inputs", [])
                runner_vscode_tasks["inputs"].append(input)
    else:
        runner_vscode_tasks = main_vscode_tasks

    with open(runner_vscode_tasks_json, "w", encoding="utf-8") as f:
        json.dump(runner_vscode_tasks, f, indent=4)
