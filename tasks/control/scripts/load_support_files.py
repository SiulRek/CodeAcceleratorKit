from tasks.management.task_manager import TaskManager

if __name__ == "__main__":
    task_manager = TaskManager()

    task_manager.load_support_files_to(
        runner_root="/home/krakerlu/github/CodeAcceleratorKit",
    )
    print("Support files loaded successfully.")