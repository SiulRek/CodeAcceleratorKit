from tasks.tasks.management.task_manager import TaskManager

if __name__ == "__main__":
    task_manager = TaskManager()

    task_manager.update_registered_runners()
    # Do not forget to to update UPDATE_MAPPING in tasks/configs/profile_attributes.py
