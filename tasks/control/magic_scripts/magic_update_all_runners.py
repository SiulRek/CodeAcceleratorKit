import os

from tasks.control.shared.TASKS_ROOT import TASKS_ROOT
from tasks.control.magic_scripts.magic_register_runner import allocate_vscode_tasks_json
from tasks.tasks.management.task_manager import TaskManager


def magic_update_all_runners():
    """
    A Magic function that not only updates all the registered runners but also
    copies the templates files from the main tasks root to the target runner root and
    allocates the '.vscode/tasks.json'.
    """
    TaskManager.update_registered_runners()

    runner_roots = TaskManager.get_registered_runners()

    for runner_root in runner_roots:
        if runner_root == TASKS_ROOT:
            continue
        TaskManager.copy_templates_files(TASKS_ROOT, runner_root)
        allocate_vscode_tasks_json(runner_root)
        print(f"Runner {os.path.basename(runner_root)} updated successfully.")


if __name__ == "__main__":
    magic_update_all_runners()
    print("All runners updated successfully.")
