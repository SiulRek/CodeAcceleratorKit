import os
import shutil

from tasks.controllers.shared.TASKS_ROOT import TASKS_ROOT
from tasks.management.standardize_path import standardize_path
from tasks.management.task_manager import TaskManager
from tasks.management.task_runner_profile import TaskRunnerProfile


def copy_file_to_registered_runners(source_file):
    """
    A Magic function to copy a file from the main tasks storage root to all
    registered runners' storage directories.

    Parameters
    ----------
    file (str)
        The path to the file to be copied.
    """
    source_file = standardize_path(source_file)

    if not source_file.startswith(TASKS_ROOT):
        raise ValueError(
            f"File '{source_file}' must be within the main tasks root "
            f"directory '{TASKS_ROOT}'."
        )

    task_manager = TaskManager()
    runners = task_manager.get_registered_runners()
    runners = [
        TaskRunnerProfile(runner) 
        for runner in runners
        if runner != TASKS_ROOT
    ]
    root_runner = TaskRunnerProfile(TASKS_ROOT)
    root_storage_dir = root_runner.storage_dir

    assert source_file.startswith(
        root_storage_dir
    ), f"File '{source_file}' must be within the root storage directory '{root_storage_dir}'."
    assert os.path.isfile(source_file), f"File '{source_file}' does not exist."

    rel_path = os.path.relpath(source_file, root_storage_dir)
    for runner in runners:
        target_file = os.path.join(runner.storage_dir, rel_path)
        target_dir = os.path.dirname(target_file)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
        shutil.copy2(source_file, target_file)
        print(f"Copied '{source_file}' to '{target_file}'.")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        raise ValueError("Please provide the source file path as an argument.")

    source_file = sys.argv[1]
    copy_file_to_registered_runners(source_file)