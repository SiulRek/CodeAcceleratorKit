"""
This module defines the DirectoryRunnerTask, a task for running specific tasks on a directory of files.

The DirectoryRunnerTask class sets up the environment, reads configurations from a JSON file, and executes the specified task on each file within a directory. It supports resuming from the last stopped file and excludes specified files and directories.

Available tasks:
- FormatPythonTask: Formats Python files by removing or refactoring specific parts based on macros.
- AutomaticPromptTask: Generates automatic prompts based on macro statements.

The module includes the following key functionalities:
- Reading configuration from a JSON file.
- Initializing and setting up the task environment.
- Tracking the execution status of each file.
- Logging outputs to a specified file.
- Handling backups of files before modifications.
- Supporting resumption from the last stopped file in case of interruptions.

Usage example:
# Initialize the task with a root directory and a configuration JSON file.
DirectoryRunnerTask(root_directory, config_json).main()

TODO when adding new tasks:
1. Ensure the task class is imported and recognized in _get_task_class method.
2. Update the configuration JSON schema if new attributes are needed.
3. Implement necessary methods in the task class for integration.
"""
import json
import os

from tasks.tasks.format_python.format_python_task import FormatPythonTask
from tasks.tasks.automatic_prompt.automatic_prompt_task import AutomaticPromptTask
from tasks.tasks.core.task_base import TaskBase
from tasks.utils.for_directory_runner.file_execution_tracker import FileExecutionTracker
from tasks.utils.shared.backup_handler import BackupHandler
from tasks.utils.for_directory_runner.log_outputs_to_file import log_outputs_to_file


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
        if task_name == FormatPythonTask.NAME:
            return FormatPythonTask
        if task_name == AutomaticPromptTask.NAME:
            return AutomaticPromptTask
        msg = f"Task {task_name} is not supported."
        raise ValueError(msg)

    def setup(self):
        super().setup()
        self.current_file = self.additional_args[0]
        if not self.current_file.endswith(".json"):
            msg = "Directory Runner JSON is not json. Hint: Currently active"
            msg += "file must be the Directory Runner JSON."
            raise ValueError(msg)
        self._set_attributes_from_json(self.current_file)

    def execute(self):
        """ Executes the directory runner task, running the specified task on
        thefiles in the directory. """
        execution_tracks_dir = self.profile.execution_tracks_dir
        csv_name = (
            os.path.basename(self.current_file).split(".")[0]
            + "_execution_tracks.csv"
        )
        file_execution_csv = os.path.join(execution_tracks_dir, csv_name)
        output_log_name = csv_name.replace("_execution_tracks.csv", "_output.log")
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
                self.directory_path, 
                excluded_files=self.excluded_files,
                excluded_dirs=self.excluded_dirs,
                extensions=[".py"]
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
