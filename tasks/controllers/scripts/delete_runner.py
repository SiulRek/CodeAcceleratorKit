from tasks.management.task_manager import TaskManager

if __name__ == "__main__":
    task_manager = TaskManager()

    task_manager.delete_runner(
        runner_root="/home/krakerlu/github/CodeAcceleratorKitTest",
    )
    pass