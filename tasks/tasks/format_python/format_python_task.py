"""
This module defines the FormatPythonTask, a task for formatting Python files by removing or refactoring specific parts based on strategies
that can be configured by macros.

The FormatPythonTask class sets up the environment, extracts macros from the given Python files, and applies the specified formatting.

The specific macros and their interpretation are defined in the FormatPythonInterpreter.

Available macros:
| Name                     | Description                                            | Macro                  | Arguments                          |
|--------------------------|--------------------------------------------------------|------------------------|------------------------------------|
| select_only              | Selects only the specified strategies                  | #only                  | <List of strategies abbreviations> |
| select_not               | Excludes the specified strategies                      | #not                   | <List of strategies abbreviations> |
| force_select_of          | Forces selection of the specified strategies           | #force                 | <List of strategies abbreviations> |
| checkpoints              | Marks the points in the code for checkpoints           | #checkpointing         | -                                  |

Available strategies:
| Abbreviation | Description                        | Comments                           |
|--------------|------------------------------------|------------------------------------|
| RL           | Remove line comments               | Needs to be forced                 |
| RT           | Remove trailing parts              |                                    |
| AE           | Add encoding to open               |                                    |
| RUE          | Remove unnecessary else            |                                    |
| RF           | Remove f from empty fstrings       |                                    |
| RI           | Rearrang imports                   |                                    |
| RU           | Remove unused imports              |                                    |
| BF           | Run Black formatting               |                                    |
| FE           | Refactor exception                 |                                    |
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

from rich.console import Console
from rich.table import Table
from tasks.tasks.core.task_base import TaskBase
from tasks.tasks.format_python.format_python_interpreter import FormatPythonInterpreter
from tasks.utils.for_format_python.format_python_file import format_python_file
from tasks.utils.shared.backup_handler import BackupHandler

requirements = ["black", "pylint"]


def print_help():
    console = Console()

    # Macros Table
    macros_table = Table(title="Macros")
    macros_table.add_column("Macro", style="cyan", justify="center")
    macros_table.add_column("Purpose", style="green")
    macros_table.add_column("Args", style="magenta")
    macros_table.add_row("#only", "Include only strategies", "<List of abbreviations>")
    macros_table.add_row("#not", "Exclude strategies", "<List of abbreviations>")
    macros_table.add_row(
        "#force", "Force include strategies", "<List of abbreviations>"
    )
    macros_table.add_row("#checkpointing", "Insert checkpoints", "-")

    # Strategies Table
    strategies_table = Table(title="Strategies")
    strategies_table.add_column("Abbr", style="cyan", justify="center")
    strategies_table.add_column("Description", style="green")
    strategies_table.add_column("Notes", style="magenta")
    strategies_table.add_row("RL", "Remove line comments", "Must be forced")
    strategies_table.add_row("RT", "Remove trailing parts", "")
    strategies_table.add_row("AE", "Add encoding to open", "")
    strategies_table.add_row("RUE", "Remove unnecessary else", "")
    strategies_table.add_row("RF", "Remove 'f' from empty fstrings", "")
    strategies_table.add_row("RI", "Rearrange imports", "")
    strategies_table.add_row("RU", "Remove unused imports", "")
    strategies_table.add_row("BF", "Apply Black formatting", "")
    strategies_table.add_row("FE", "Refactor exception blocks", "")
    strategies_table.add_row("FD", "Format docstrings", "")
    strategies_table.add_row("EN", "Ensure newline at EOF", "Must be forced")
    strategies_table.add_row("PL", "Run Pylint", "")

    # Print tables
    console.print(macros_table)
    console.print(strategies_table)


class FormatPythonTask(TaskBase):
    """A task for formatting python files by removing or refactoring specific parts based on
    macros."""

    NAME = "Format Python"

    def _handle_options_if_present(self, text):
        stripped = text.strip()
        if stripped == "--help" or stripped == "-h":
            print_help()
            exit(0)
        if stripped == "--cancel" or stripped == "-c":
            print("Cancelled by user.")
            exit(0)

    def setup(self):
        """Sets up the FormatPythonTask by initializing the file path from additional
        arguments."""
        super().setup()
        self.current_file = self.additional_args[0]
        self.macros_text = None
        if len(self.additional_args) > 1:
            text = self.additional_args[1]
            # Both --help and --cancel options terminate the program
            self._handle_options_if_present(text)
            self.macros_text = text

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
            macros_data, updated_text = interpreter.extract_macros_from_text(
                self.macros_text, post_process=True
            )
            if updated_text:
                raise ValueError(
                    "Not able to process the following macros:\n" + updated_text
                )

            with open(current_file, "r", encoding="utf-8") as file:
                updated_content = file.read()
        else:
            macros_data, updated_content = interpreter.extract_macros_from_file(
                current_file
            )
        select_only, select_not, force_select_of, checkpointing = macros_data

        if select_only is not None and select_not is not None:
            msg = "Cannot have both select_only and select_not options specified."
            raise ValueError(msg)
        if not checkpointing:
            checkpoint_dir = None

        backup_handler.store_backup(
            current_file, "Before modification from format python task."
        )
        with open(current_file, "w", encoding="utf-8") as file:
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
    default_root = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."
    )
    default_file_path = os.path.join(
        default_root,
        "tasks",
        "tests",
        "for_tasks",
        "format_python_test.py",
    )
    task = FormatPythonTask(default_root, default_file_path)
    task.main()
