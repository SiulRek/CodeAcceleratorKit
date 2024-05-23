"""
This module creates a query from the file and referenced contents in the file.

Available reference types:
    - | Name | Description | Pattern | Arguments |
        |-----------------------|-----------------------------|-------------------------------------------------|-----------------------------------------------------------------------------------------------|
        | start tag | Place start text | #S <start_text> | - | | fill_text | Add
        a fill text | #*<fill_text_name> | - | | run_python_script | Run a
        Python script | #run <script_path> | - | | run_pylint | Run pylint on a
        file | #run_pylint <file_path> | - | | run_unittest | Run unittest on a
        file | #run_unittest <file_path> | <verbosity> | | directory_tree | Get
        directory tree | #tree <directory_path> | <max_depth, include_files,
        ignore_list (semicolon-separated list)> | | summarize_python_script |
        Summarize a Python script | #summarize <script_path> |
        <include_definitions_without_docstrings> | | summarize_folder |
        Summarize Python scripts in a folder | #summarize_folder <folder_path> |
        <include_definitions_without_docstrings, excluded_dirs, excluded_files>
        | | checksum | Check if provided checksum corresponds | #checksum
        <number_of_macros> | - |

Note: Replace angled brackets and their contents with appropriate values when
using patterns.

TODO when adding new reference:
    - 1. Make line validation function in `line_validation.py`. 2. Add the
        reference type to `REFERENCE_TYPE`. 3. Add a new handler function with
        the reference functionality in `extract_referenced_contents.py`. 4. Add
        the handler function to the `reference_handlers` dictionary.
"""

import os

from tasks.configs.constants import MAKE_QUERY_MACROS as MACROS
from tasks.tasks.create_query.create_query_engine import CreateQueryEngine
from tasks.tasks.create_query.finalizer import Finalizer
from tasks.tasks.foundation.task_base import TaskBase
from tasks.tools.for_create_query.add_text_tags import add_text_tags
from tasks.tools.general.backup_handler import BackupHandler


class ChapterTitleManager:
    """
    Manages the title of the chapter for query formatting.

    Attributes:
        - title (str): The current title of the chapter.
    """

    def __init__(self):
        """Initializes ChapterTitleManager with no title."""
        self.title = None

    def set(self, title):
        """
        Sets the chapter title.

        Args:
            - title (str): The title to be set.
        """
        self.title = title

    def get(self):
        """
        Gets the current chapter title and resets it to None.

        Returns:
            - str: The current title.
        """
        title, self.title = self.title, None
        return title


def format_text_from_macros(macros_data, updated_content):
    """
    Formats a query string from file references and updated content.

    Args:
        - macros_data (list): A list of tuples detailing macros (type,
            data).
        - updated_content (str): The updated content of the current file.

    Returns:
        - str: Formatted query based on file macros.
    """
    query = ""
    title_manager = ChapterTitleManager()
    for macros_data in macros_data:
        content_type, default_title, text = macros_data
        current_title = title_manager.get()
        title = current_title if current_title else default_title

        if content_type == MACROS.TITLE:
            title_manager.set(default_title)
        elif content_type == MACROS.CURRENT_FILE:
            query += f"\n\n--- {title} ---\n{updated_content}"
        elif content_type in MACROS:
            query += f"\n\n--- {title} ---\n{text}"
        else:
            msg = f"Unknown content type: {content_type}"
            raise ValueError(msg)

    return query


class CreateQueryTask(TaskBase):
    """
    Task to create a query based on formatted content and macros.

    Attributes:
        - NAME (str): The name of the task.
    """

    NAME = "Create Query"

    def setup(self):
        """Sets up the CreateQuery task by initializing the file path."""
        super().setup()
        self.file_path = self.additional_args[0]
        self.macros_text = None
        if len(self.additional_args) > 1:
            self.macros_text = self.additional_args[1]

    def execute(self):
        """Executes the CreateQuery task to format and finalize the query."""
        engine = CreateQueryEngine(self.session)

        if self.macros_text:
            engine.file_path = self.file_path  # Allows for current file macros
            macros_data, _ = engine.extract_macros_from_text(
                self.macros_text, post_process=True
            )
            with open(self.file_path, "r") as file:
                updated_content = file.read()
        else:
            macros_data, updated_content = engine.extract_macros_from_file(
                self.file_path
            )
        macros_data, begin_text, end_text, make_query_kwargs = macros_data

        query = format_text_from_macros(macros_data, updated_content)

        query = add_text_tags(begin_text, end_text, query)

        finalizer = Finalizer()
        finalizer.set_directories(
            self.file_path,
            self.session.output_dir,
        )
        backup_handler = BackupHandler(
            self.session.backup_dir, self.session.max_backups
        )
        finalizer.finalize(updated_content, query, make_query_kwargs, backup_handler)


if __name__ == "__main__":
    """Entry point for the module. Initializes and runs the CreateQuery task."""
    default_root = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."
    )
    default_file_path = os.path.join(
        default_root, "tasks", "tests", "for_tasks", "create_query.py"
    )
    CreateQueryTask(default_root, default_file_path).main()
