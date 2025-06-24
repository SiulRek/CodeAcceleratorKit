from tasks.management.task_manager import TaskManager
from tasks.utils.shared.library_utils import is_library_installed

if __name__ == "__main__":
    #TODO: Assign runner paths.
    runner_root = "/home/siulrek/MY_ROOM/github/CodeAcceleratorKit"
    runner_env = "/home/siulrek/MY_ROOM/github/CodeAcceleratorKit/venv"

    for lib in ["black", "pylint", "stdlib-list"]:
        if not is_library_installed(lib, runner_env):
            msg = f"Library '{lib}' not installed in the specified virtual"
            msg += "environment."
            raise ValueError(msg)

    task_manager = TaskManager()
    task_manager.register_runner(
        runner_root=runner_root,
        python_env=runner_env,
    )
    task_manager.load_support_files_to(
        runner=runner_root,
    )
    print("Runner registered successfully.")
