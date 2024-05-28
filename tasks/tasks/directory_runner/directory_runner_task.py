import json
import os

from tasks.tasks.cleanup.cleanup_task import CleanupTask
from tasks.tasks.create_query.create_query_task import CreateQueryTask
from tasks.tasks.foundation.task_base import TaskBase
from tasks.tools.for_directory_runner.file_execution_tracker import FileExecutionTracker
from tasks.tools.general.backup_handler import BackupHandler
from tasks.tools.general.log_outputs_to_file import log_outputs_to_file


class DirectoryRunnerTask(TaskBase):
    """ A task for running tasks on a directory of files. """

    NAME = "Directory Runner"

    def _set_attributes_from_json(self, directory_runner_json):
        with open(directory_runner_json, "r", encoding="utf-8") as f:
            content = json.load(f)
            directory_runner_args = content["directory_runner_config"]
        keys = [
            "task_name",
            "directory_path",
            "macros_text",
            "resume_from_last_stopped",
            "excluded_files",
            "excluded_dirs",
            "clear_backup_storage",
        ]
        for key in keys:
            if key not in directory_runner_args:
                msg = f"Key {key} is missing in directory runner JSON file."
                raise ValueError(msg)
            if key == "macros_text":
                text = directory_runner_args[key]
                if isinstance(text, list):
                    text = "\n".join(text)
                setattr(self, key, text)
            else:
                setattr(self, key, directory_runner_args[key])

    def _get_task_class(self, task_name):
        if task_name == CleanupTask.NAME:
            return CleanupTask
        if task_name == CreateQueryTask.NAME:
            return CreateQueryTask
        msg = f"Task {task_name} is not supported."
        raise ValueError(msg)

    def setup(self):
        super().setup()
        self.directory_runner_json = self.additional_args[0]
        if not self.directory_runner_json.endswith(".json"):
            msg = "Directory Runner JSON is not json. Hint: Currently active"
            msg += "file must be the Directory Runner JSON."
            raise ValueError(msg)
        self._set_attributes_from_json(self.directory_runner_json)

    def execute(self):
        """ Executes the directory runner task, running the specified task on
        thefiles in the directory. """
        execution_tracks_dir = self.profile.execution_tracks_dir
        csv_name = (
            os.path.basename(self.directory_path).split(".")[0]
            + "_execution_tracks.csv"
        )
        file_execution_csv = os.path.join(execution_tracks_dir, csv_name)
        output_log_name = csv_name.replace("_execution_tracks.csv", "_output.txt")
        output_log_file = os.path.join(self.profile.log_dir, output_log_name)

        backup_handler = BackupHandler(
            self.profile.backup_dir, self.profile.max_backups
        )
        if self.clear_backup_storage:
            backup_handler.clear_storage()

        if not os.path.isdir(self.directory_path):
            msg = f"Directory path {self.directory_path} does not exist."
            raise ValueError(msg)

        execution_tracker = FileExecutionTracker(file_execution_csv)
        if self.resume_from_last_stopped:
            execution_tracker.verify_tracks()
        else:
            execution_tracker.clear_tracks()
            execution_tracker.add_files_from_directory(
                self.directory_path, self.excluded_dirs, self.excluded_files
            )

        print(f"\nExecution Tracker initialized: {file_execution_csv}")
        print(f"Output log file: {output_log_file}\n")
        count_status = execution_tracker.get_status_count()
        pendings_at_start = count_status.get("pending")
        print(f"Number of files pending at start: {pendings_at_start}\n")

        completed_files = 0
        failed_files = 0
        append = False
        while True:
            file_path = execution_tracker.take_next_pending()
            if file_path is None:
                break

            subtask_class = self._get_task_class(self.task_name)
            subtask = subtask_class(self.task_runner_root, file_path, self.macros_text)
            subtask.force_defaults()  # Prevents the task from using the command line arguments
            try:
                with log_outputs_to_file(output_log_file, append=append):
                    append = True
                    subtask.main()
                    print(f"\n\n")
                execution_tracker.mark_running_as_completed()
                completed_files += 1
            except Exception as e:
                execution_tracker.mark_running_as_failed(e)
                failed_files += 1

            print(f"Task '{self.task_name}' completed for file: {file_path}")
            print(f"Completed: {completed_files} / {pendings_at_start}")
            print(f"Failed: {failed_files} / {pendings_at_start}")
            print("-" * 40)

        print("\nExecution Summary")
        print("=" * 40)
        print(f"Total files processed: {completed_files + failed_files}")
        print(f"Successfully completed: {completed_files}")
        print(f"Failed: {failed_files}")
        print("=" * 40)


if __name__ == "__main__":
    default_root = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."
    )
    default_json = os.path.join(
        default_root, "local", "tasks_storage", "profile", "directory_runner_test.json"
    )
    DirectoryRunnerTask(default_root, default_json).main()
