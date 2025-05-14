"""
This module defines the GitStagingTask, a task for adding or removing files or
directories from the Git staging area.

The GitStagingTask class sets up the environment, initializes the paths to be
added or removed from additional arguments, and uses Git commands to manage the
staging area.

Usage example:
```python
GitStagingTask(root_directory, reference_file, paths_to_manage).main()
```
"""


import os
import subprocess

from tasks.tasks.core.task_base import TaskBase
from tasks.utils.shared.find_closest_matching_dir import find_closest_matching_dir
from tasks.utils.shared.find_closest_matching_file import find_closest_matching_file


class GitStagingTask(TaskBase):
    """
    A task for adding or removing files or directories from the Git staging
    area.
    """

    NAME = "Git Staging"

    def setup(self):
        """
        Sets up the GitStagingTask by initializing the paths to be managed from
        additional arguments.
        """
        super().setup()
        self.current_file = self.additional_args[0]
        paths = self.additional_args[1].split(",")
        paths = [path.strip() for path in paths]
        paths_to_remove = [path[1:] for path in paths if path.startswith("-")]
        paths_to_add = [path for path in paths if not path.startswith("-")]
        self.paths_to_add = self._process_paths(paths_to_add)
        self.paths_to_remove = self._process_paths(paths_to_remove)

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
                    processed_paths.append(dir_path)
                except FileNotFoundError as e:
                    msg = f"Failed to find {path}."
                    raise ValueError(msg) from e
        return processed_paths

    def execute(self):
        """
        Executes the task, adding or removing the specified files or
        directories from the Git staging area.

        Raises
        -----
        FileNotFoundError
            If a specified file or directory cannot be found.
        """
        subprocess.run(["git", "reset"], check=True, cwd=self.profile.root)
        print()
        for path in self.paths_to_add:
            subprocess.run(["git", "add", path], check=True, cwd=self.profile.root)
            print(f"Added {path} to staging area.")

        for path in self.paths_to_remove:
            subprocess.run(["git", "reset", path], check=True, cwd=self.profile.root)
            print(f"Removed {path} from staging area.")


if __name__ == "__main__":
    default_root = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."
    )
    default_reference_file = "path/to/reference/file"
    default_paths_to_manage = "path/to/file1, path/to/file2, path/to/dir1"
    task = GitStagingTask(default_root, default_reference_file, default_paths_to_manage)
    task.main()