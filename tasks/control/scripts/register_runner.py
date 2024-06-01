from tasks.management.task_manager import TaskManager

if __name__ == "__main__":
    task_manager = TaskManager()
    runner_root = "/path/to/runner"
    task_manager.register_runner(
        # runner_root=runner_root,
        # python_env="/path/to/runner/python_env",
        # storage_dir="/path/to/runner/storage",
        # cwd="/path/to/runner/cwd",
        # create_dirs=True
    )
    task_manager.load_support_files_to(
        runner_root=runner_root,
    )
    print("Runner registered successfully.")
