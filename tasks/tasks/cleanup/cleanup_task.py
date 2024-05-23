import os

from tasks.tasks.cleanup.cleanup_interpreter import CleanupInterpreter
from tasks.tasks.foundation.task_base import TaskBase
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
        self.macros_text = None
        if len(self.additional_args) > 1:
            self.macros_text = self.additional_args[1]

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
        environment_path = self.session.tasks_python_env

        interpreter = CleanupInterpreter(self.session)
        if self.macros_text:
            macros_data, _ = interpreter.extract_macros_from_text(self.macros_text, post_process=True)
            with open(file_path, "r") as file:
                updated_content = file.read()
        else:
            macros_data, updated_content = interpreter.extract_macros_from_file(file_path)
        select_only, select_not, checkpointing = macros_data

        if select_only is not None and select_not is not None:
            msg = "Cannot have both select_only and select_not options specified."
            raise ValueError(msg)
        if not checkpointing:
            checkpoint_dir = None
            

        with open(file_path, "w") as file:
            file.write(updated_content)

        cleanup_file(
            file_path=file_path,
            select_only=select_only,
            select_not=select_not,
            checkpoint_dir=checkpoint_dir,
            python_env_path=environment_path,
            modules_info=self.session.modules_info,
        )


if __name__ == "__main__":
    default_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
    default_file_path = os.path.join(
        default_root,
        "tasks",
        "tests",
        "for_tasks",
        "cleanup_test.py",
    )
    task = CleanupTask(default_root, default_file_path)
    task.main()
