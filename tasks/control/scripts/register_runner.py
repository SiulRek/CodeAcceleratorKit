from tasks.tasks.management.task_manager import TaskManager

if __name__ == "__main__":
    task_manager = TaskManager()

    task_manager.register_runner(
        # runner_root="/path/to/runner",
        # python_env="/path/to/runner/python_env",
        # # storage_dir="/path/to/runner/storage",
        # # cwd="/path/to/runner/cwd",
        # # overwrite=True
        # # create_dirs=True
    )