"""
This module defines the GitDiscardTask, a task for discarding files or
directories from a Git repository after backing them up.

The GitDiscardTask class sets up the environment, initializes the paths to be
discarded from additional arguments, backs up the specified files or files in
directories, and uses Git commands to restore them from the repository.

Usage
----
```python
# Define the root directory of the repository root_directory =
"/path/to/repository/root"

# Define the reference file (usually the script itself or a related file)
reference_file = "/path/to/reference/file"

# Define the paths to discard (comma-separated string of files or directories)
paths_to_discard = "file1.txt, dir1, file2.txt"

# Create and execute the task task = GitDiscardTask(root_directory,
reference_file, paths_to_discard) task.main()
```
"""

from contextlib import contextmanager
import os
import subprocess

from tasks.utils.shared.backup_handler import BackupHandler
from tasks.tasks.core.task_base import TaskBase
from tasks.utils.shared.find_closest_matching_dir import find_closest_matching_dir
from tasks.utils.shared.find_closest_matching_file import find_closest_matching_file


@contextmanager
def _suppress_output():
    """
    Context Manager to suppress output.
    """
    with open(os.devnull, "w", encoding="utf-8") as devnull:
        old_stdout = os.dup(1)
        os.dup2(devnull.fileno(), 1)
        yield
        os.dup2(old_stdout, 1)


class GitDiscardTask(TaskBase):
    """
    A task for discarding files or directories from a Git repository after
    backing them up.
    """

    NAME = "Git Discard"

    def setup(self):
        """
        Sets up the GitDiscardTask by initializing the paths to be discarded
        from additional arguments.
        """
        super().setup()
        self.current_file = self.additional_args[0]
        paths = self.additional_args[1].split(",")
        paths = [path.strip() for path in paths]
        self.paths_to_discard = self._process_paths(paths)

    def _is_not_ignored_and_modified(self, path):
        try:
            with _suppress_output():
                ignored = (
                    subprocess.run(
                        ["git", "check-ignore", path], cwd=self.profile.root
                    ).returncode
                    == 0
                )
        except subprocess.CalledProcessError as e:
            raise subprocess.CalledProcessError(
                f"Failed to check if {path} is ignored."
            ) from e
        try:
            with _suppress_output():
                modified = subprocess.run(
                    ["git", "status", "--porcelain", path],
                    cwd=self.profile.root,
                    capture_output=True,
                ).stdout
        except subprocess.CalledProcessError as e:
            raise subprocess.CalledProcessError(
                f"Failed to check if {path} is modified."
            ) from e
        return not ignored and modified

    def _get_not_ignored_and_modified_files(self, directory):
        valid_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                file = os.path.relpath(os.path.join(root, file), self.profile.root)
                if self._is_not_ignored_and_modified(file):
                    valid_files.append(file)
        return valid_files

    def _process_paths(self, paths):
        if paths == [""]:
            return []

        processed_paths = []
        for path in paths:
            path = path.strip()
            try:
                file_path = find_closest_matching_file(path, self.profile.root, self.current_file)
                processed_paths.append(file_path)
            except FileNotFoundError:
                try:
                    dir_path = find_closest_matching_dir(
                        path, self.profile.root, os.path.dirname(self.current_file)
                    )
                    processed_paths.extend(
                        self._get_not_ignored_and_modified_files(dir_path)
                    )
                except FileNotFoundError as e:
                    msg = f"Failed to find {path}."
                    raise ValueError(msg) from e
        return processed_paths

    def execute(self):
        """
        Executes the task, backing up and then discarding the specified files
        or directories from the Git repository.

        Raises
        -----
        FileNotFoundError
            If a specified file or directory cannot be found.
        """
        backup_handler = BackupHandler(
            self.profile.backup_dir,
            self.profile.max_backups,
        )

        for path in self.paths_to_discard:
            backup_handler.store_backup(path, "Before discarding from git repository.")
            backup_path = backup_handler.get_backup_path(path)
            # Git discard changes
            subprocess.run(
                ["git", "restore", "--source=HEAD", path],
                check=True,
                cwd=self.profile.root,
            )
            print(f"Discarded {path} from repository.")
            print(f"Backed up to {backup_path}.\n")


if __name__ == "__main__":
    default_root = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."
    )
    default_reference_file = "path/to/reference/file"
    default_paths_to_discard = "path/to/file1, path/to/file2, path/to/dir1"
    default_reference_file = "/home/krakerlu/github/CodeAcceleratorKit/tasks/tasks/git_discard/git_discard_task.py"
    default_paths_to_discard = "tasks/tests/data"
    task = GitDiscardTask(
        default_root, default_reference_file, default_paths_to_discard
    )
    task.main()
