"""
This module defines the RestoreFileTask, a task for restoring a backup file to its original location.

The RestoreFileTask class sets up the environment, initializes the file path from additional arguments, and uses the BackupHandler to recover the specified backup file.

Usage example:
RestoreFileTask(root_directory, backup_file_path).main()
"""

import os

from tasks.tasks.core.task_base import TaskBase
from tasks.utils.shared.backup_handler import BackupHandler


class RestoreFileTask(TaskBase):
    """A task for restoring a backup file to its original location."""

    NAME = "Restore Backup"

    def setup(self):
        """Sets up the RestoreFileTask by initializing the file path from
        additional arguments."""
        super().setup()
        self.current_file = self.additional_args[0]

    def execute(self):
        """
        Executes the restore backup task, restoring the specified backup file to
        its original location.

        Raises:
            - FileNotFoundError: If the specified backup file does not
                exist.
        """
        file_path = self.current_file

        backup_handler = BackupHandler(
            self.profile.backup_dir,
            self.profile.max_backups,
        )

        try:
            backup_handler.recover_backup(file_path)
            print(f"Backup for {file_path} has been successfully restored.")
        except FileNotFoundError as e:
            print(f"Restore backup failed. Error: {e}")


if __name__ == "__main__":
    default_root = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."
    )
    default_file_path = os.path.join(
        default_root,
        "path",
        "to",
        "your",
        "backup_file.txt",
    )
    task = RestoreFileTask(default_root, default_file_path)
    task.main()
