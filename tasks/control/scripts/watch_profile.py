from tasks.tasks.management.task_manager import TaskManager

if __name__ == "__main__":
    task_manager = TaskManager()

    profile = task_manager.login_runner(
        # runner_root="/path/to/runner",
    )
    pass # Set a breakpoint here to inspect the profile object
