import os

from tasks.controllers.shared.TASKS_ROOT import TASKS_ROOT
from tasks.controllers.magic_scripts.magic_register_runner import allocate_vscode_tasks_json
from tasks.management.task_manager import TaskManager


def magic_update_all_runners():
    """
    A Magic function that not only updates all the registered runners but also
    copies the templates files from the main tasks root to the target runner
    root and allocates the '.vscode/tasks.json'.
    """
    TaskManager.update_registered_runners()

    runners = TaskManager.get_registered_runners()

    for runner in runners:
        runner_root = runner if isinstance(runner, str) else runner.root
        if runner_root == TASKS_ROOT:
            continue
        TaskManager.copy_costumizations_files(TASKS_ROOT, runner)
        allocate_vscode_tasks_json(runner)
        print(f"Runner {os.path.basename(runner_root)} updated successfully.")


if __name__ == "__main__":
    magic_update_all_runners()
    print("All runners updated successfully.")
