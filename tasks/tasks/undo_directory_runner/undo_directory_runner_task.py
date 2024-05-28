import os

from tasks.tasks.foundation.task_base import TaskBase
from tasks.tools.for_directory_runner.file_execution_tracker import FileExecutionTracker
from tasks.tools.general.backup_handler import BackupHandler


class UndoDirectoryRunnerTask(TaskBase):
    """ A task for undoing the effects of a directory runner task. """

    NAME = "Undo Directory Runner"

    def setup(self):
        super().setup()
        self.directory_runner_json = self.additional_args[0]
        if not self.directory_runner_json.endswith(".json"):
            msg = "Directory Runner JSON is not json. Hint: Currently active"
            msg += "file must be the Directory Runner JSON from which to undo."
            raise ValueError(msg)

    def execute(self):
        """ Executes the directory runner task, running the specified task onthe
        files in the directory. """
        execution_tracks_dir = self.profile.execution_tracks_dir
        csv_name = (
            os.path.basename(self.directory_runner_json).split(".")[0]
            + "_execution_tracks.csv"
        ) # Same as the one in directory_runner_task.py
        file_execution_csv = os.path.join(execution_tracks_dir, csv_name)
        execution_tracker = FileExecutionTracker(file_execution_csv)
        backup_handler = BackupHandler(
            self.profile.backup_dir, self.profile.max_backups
        )

        completed_files = execution_tracker.get_completed_files()
        completed_count = len(completed_files)

        if completed_count == 0:
            print("\nNo files to undo.\n")
            return

        print(f"Undoing {completed_count} completed file(s):")

        for file in completed_files:
            print(f"Undoing file: {file}")
            execution_tracker.remove_file(file)
            try:
                backup_handler.recover_backup(file)  # Assumes the last backup is the correct one
            except FileNotFoundError:
                print(f"Backup not found for file: {file}")

        print("\nUndo process completed.\n")


if __name__ == "__main__":
    default_root = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."
    )
    default_json = os.path.join(
        default_root, "local", "tasks_storage", "profile", "directory_runner_test.json"
    )
    UndoDirectoryRunnerTask(default_root, default_json).main()
