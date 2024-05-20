import os

from tasks.configs.getters import (
    get_checkpoint_directory,
    get_environment_path_of_tasks,
)
from tasks.tools.for_cleanup.cleanup_file import cleanup_file
from tasks.tools.for_cleanup.referenced_contents_extractor import (
    ReferencedContentExtractor,
)
from tasks.tasks.task_base import TaskBase


extract_referenced_contents = ReferencedContentExtractor().extract_referenced_contents


class CleanupTask(TaskBase):
    NAME = "Cleanup"

    def setup(self):
        super().setup()
        self.file_path = self.additional_args[0]

    def execute(self):
        root_dir = self.task_runner_root
        file_path = self.file_path
        checkpoint_dir = get_checkpoint_directory(root_dir)
        environment_path = get_environment_path_of_tasks()

        referenced_contents, updated_content = extract_referenced_contents(
            file_path, root_dir
        )
        select_only, select_not, checkpointing = referenced_contents

        if select_only != None and select_not != None:
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
    default_root = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", ".."
    )
    default_file_path = os.path.join(
        default_root,
        "tasks",
        "tests",
        "for_tasks",
        "cleanup_test.py",
    )
    task = CleanupTask(default_root, default_file_path)
    task.main()
