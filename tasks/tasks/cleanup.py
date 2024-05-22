import os

from tasks.tasks.engines.for_cleanup.cleanup_engine import CleanupEngine
from tasks.tasks.task_base import TaskBase
from tasks.tools.for_cleanup.cleanup_file import cleanup_file


class CleanupTask(TaskBase):
    """A task for cleaning up files by removing or keeping specific parts based on
    macros."""

    NAME = "Cleanup"

    def setup(self):
        """Sets up the CleanupTask by initializing the file path from additional
        arguments."""
        super().setup()
        self.file_path = self.additional_args[0]

    def execute(self):
        """
        Executes the cleanup task, extracting macros from the file and
        performing the cleanup.

        Raises:
            - ValueError: If both select_only and select_not options are
                specified.
        """
        file_path = self.file_path
        checkpoint_dir = self.session.checkpoint_dir
        environment_path = self.session.runner_python_env

        engine = CleanupEngine(self.session)
        macros_data, updated_content = engine.extract_macros(file_path)
        select_only, select_not, checkpointing = macros_data

        if select_only is not None and select_not is not None:
            msg = "Cannot have both select_only and select_not options specified."
            raise ValueError(msg)

        with open(file_path, "w") as file:
            file.write(updated_content)

        cleanup_file(
            file_path=file_path,
            select_only=select_only,
            select_not=select_not,
            checkpointing=checkpointing,
            python_env_path=environment_path,
            checkpoint_dir=checkpoint_dir,
        )


if __name__ == "__main__":
    default_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    default_file_path = os.path.join(
        default_root,
        "tasks",
        "tests",
        "for_tasks",
        "cleanup_test.py",
    )
    task = CleanupTask(default_root, default_file_path)
    task.main()
