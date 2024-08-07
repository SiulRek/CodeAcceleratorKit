"""
This module defines the FormatPythonTask, a task for formatting Python files by removing or refactoring specific parts based on strategies
that can be configured by macros.

The FormatPythonTask class sets up the environment, extracts macros from the given Python files, and applies the specified formatting.

The specific macros and their interpretation are defined in the FormatPythonInterpreter.

Available macros:
| Name                     | Description                                            | Macro                  | Arguments                          |
|--------------------------|--------------------------------------------------------|------------------------|------------------------------------|
| select_only              | Selects only the specified sections                    | #only                  | <List of strategies abbreviations> |
| select_not               | Excludes the specified sections                        | #not                   | <List of strategies abbreviations> |
| force_select_of          | Forces selection of the specified sections             | #force                 | <List of strategies abbreviations> |
| checkpoints              | Marks the points in the code for checkpoints           | #checkpointing         | -                                  |

Available strategies:
| Abbreviation | Description                        | Comments                           |
|--------------|------------------------------------|------------------------------------|
| RL           | Remove line comments               | Needs to be forced                 |
| RT           | Remove trailing parts              |                                    |
| AE           | Add encoding to open               |                                    |
| RUE          | Remove unnecessary else            |                                    |
| RF           | Remove f from empty fstrings       |                                    |
| RE           | Refactor exception                 |                                    |
| RW           | Refactor warnings                  |                                    |
| RI           | Rearrang imports                   |                                    |
| RU           | Remove unused imports              |                                    |
| BF           | Run Black formatting               |                                    |
| FD           | Format docstrings                  |                                    |
| EN           | Ensure newline at end              | Needs to be forced                 |
| PL           | Execute Pylint                     |                                    |

Usage example:
macros_text = "#only RL, FD\n#checkpointing"
FormatPythonTask(root_directory, file_path, macros_text).main()

TODO when adding new macros:
1. Add the validation function in line_validation.py.
2. Add the macro to FORMAT_PYTHON_MACROS in constants.py.
3. Add a new validation method for the macro in FormatPythonInterpreter.
"""

import os

from tasks.tasks.format_python.format_python_interpreter import FormatPythonInterpreter
from tasks.utils.shared.backup_handler import BackupHandler
from tasks.tasks.core.task_base import TaskBase
from tasks.utils.for_format_python.format_python_file import format_python_file
from tasks.utils.shared.is_library_installed import is_library_installed

requirements = ["black", "pylint"]


class FormatPythonTask(TaskBase):
    """A task for formatting python files by removing or refactoring specific parts based on
    macros."""

    NAME = "Format Python"

    def setup(self):
        """Sets up the FormatPythonTask by initializing the file path from additional
        arguments."""
        super().setup()
        self.current_file = self.additional_args[0]
        self.macros_text = None
        if len(self.additional_args) > 1:
            self.macros_text = self.additional_args[1]

    def execute(self):
        """
        Executes the format python task, extracting macros from the file and
        performing the python formatting.

        Raises:
            - ValueError: If both select_only and select_not options are
                specified.
        """
        current_file = self.current_file
        checkpoint_dir = self.profile.checkpoint_dir
        environment_path = self.profile.runner_python_env

        backup_handler = BackupHandler(
            self.profile.backup_dir,
            self.profile.max_backups,
        )
        interpreter = FormatPythonInterpreter(self.profile)

        if self.macros_text:
            macros_data, _ = interpreter.extract_macros_from_text(self.macros_text, post_process=True)
            with open(current_file, "r") as file:
                updated_content = file.read()
        else:
            macros_data, updated_content = interpreter.extract_macros_from_file(current_file)
        select_only, select_not, force_select_of, checkpointing = macros_data

        if select_only is not None and select_not is not None:
            msg = "Cannot have both select_only and select_not options specified."
            raise ValueError(msg)
        if not checkpointing:
            checkpoint_dir = None
            
        backup_handler.store_backup(current_file, "Before modification from format python task.")
        with open(current_file, "w") as file:
            file.write(updated_content)

        format_python_file(
            file_path=current_file,
            select_only=select_only,
            select_not=select_not,
            force_select_of=force_select_of,
            checkpoint_dir=checkpoint_dir,
            python_env_path=environment_path,
            modules_info=self.profile.modules_info,
        )


if __name__ == "__main__":
    default_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
    default_file_path = os.path.join(
        default_root,
        "tasks",
        "tests",
        "for_tasks",
        "format_python_test.py",
    )
    task = FormatPythonTask(default_root, default_file_path)
    task.main()