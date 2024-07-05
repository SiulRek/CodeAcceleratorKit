"""
This module defines the GitStagingTask, a task for adding files or directories
to the Git staging area.

The GitStagingTask class sets up the environment, initializes the paths to be
added from additional arguments, and uses Git commands to add the specified
files or directories to the staging area.

Usage example:
    - GitStagingTask(root_directory, reference_file, paths_to_add).main()
"""

import os
import subprocess

from tasks.tasks.core.task_base import TaskBase
from tasks.utils.shared.find_dir_sloppy import find_dir_sloppy
from tasks.utils.shared.find_file_sloppy import find_file_sloppy


class GitStagingTask(TaskBase):
    """ A task for adding files or directories to the Git staging area. """

    NAME = "Git Staging"

    def setup(self):
        """ Sets up the GitStagingTask by initializing the paths to be added from
        additional arguments. """
        super().setup()
        self.current_file = self.additional_args[0]
        paths_to_add = self.additional_args[1].split(",")
        self.paths_to_add = self._process_paths_to_add(paths_to_add)

    def _process_paths_to_add(self, paths_to_add):
        if paths_to_add == [""]:
            return []

        paths = []
        for path in paths_to_add:
            path = path.strip()
            try:
                file_path = find_file_sloppy(path, self.profile.root, self.current_file)
                paths.append(file_path)
            except FileNotFoundError:
                try:
                    dir_path = find_dir_sloppy(
                        path, self.profile.root, os.path.dirname(self.current_file)
                    )
                    paths.append(dir_path)
                except FileNotFoundError as e:
                    msg = f"Failed to find {path}."
                    raise ValueError(msg) from e
        return paths

    def execute(self):
        """
        Executes the add to staging task, adding the specified files or
        directories to the Git staging area.

        Raises:
            - FileNotFoundError: If a specified file or directory cannot be
                found.
        """
        subprocess.run(["git", "reset"], check=True, cwd=self.profile.root)
        print()
        for path in self.paths_to_add:
            subprocess.run(["git", "add", path], check=True, cwd=self.profile.root)
            print(f"Added {path} to staging area.")


if __name__ == "__main__":
    default_root = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."
    )
    default_path = "path/to/reference/file"
    default_paths_to_add = "path/to/file1, path/to/file2, path/to/dir1"
    task = GitStagingTask(default_root, default_path, default_paths_to_add)
    task.main()
# tasks.json
