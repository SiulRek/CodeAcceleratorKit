from tasks.management.task_manager import TaskManager

if __name__ == "__main__":
    task_manager = TaskManager()

    runners = task_manager.get_registered_runners()
    for runner in runners:
        print(f"Loading support files for {runner}...")
        task_manager.load_support_files_to(runner)
        print(f"Support files loaded successfully for {runner}.")
    print("All support files loaded successfully.")
