"""
This module creates a query from the file and referenced contents in the file.

Available reference types:
| Name                    | Description                           | Pattern                                          | Arguments                                            |
|-------------------------|---------------------------------------|--------------------------------------------------|-----------------------------------------------------|
| start tag               | Place start text                      | #S <start_text>                                  | -                                                   |
| end tag                 | Place end text                        | #E <end_text>                                    | -                                                   |
| title                   | Title of the reference                | #T <title>                                       | -                                                   |
| comment                 | Comment text                          | #C <comment>                                     | -                                                   |
| file reference          | Reference to file/s                   | #File <file_path> or <file_path_1, file_path_2>  | -                                                   |
| current_file_reference  | Current file content                  | #File                                            | -                                                   |
| error                   | Get logged errors                     | #L                                               | -                                                   |
| fill_text               | Add a fill text                       | #*<fill_text_name>                               | -                                                   |
| run_python_script       | Run a Python script                   | #run <script_path>                 | -                                                   |
| run_pylint              | Run pylint on a file                  | #run_pylint <file_path>                          | -                                                   |
| run_unittest            | Run unittest on a file                | #run_unittest <file_path>                        | <verbosity> -                                                   |
| directory_tree          | Get directory tree                    | #tree <directory_path>                 | <max_depth, include_files, ignore_list (semicolon-separated list)> |
| summarize_python_script | Summarize a Python script             | #summarize <script_path>           | <include_definitions_without_docstrings>               |
| summarize_folder       | Summarize Python scripts in a folder  | #summarize_folder <folder_path>     | <include_definitions_without_docstrings, excluded_dirs, excluded_files> |
| make_query              | Make a query from a temporary file    | #makequery                                       | <create_python_script, max_tokens>                  |
| checksum                | Check if provided checksum corresponds | #checksum <number_of_references>                 | -                                                   |

Note: Replace angled brackets and their contents with appropriate values when using patterns.

TODO when adding new reference:
1. Make line validation function in line_validation.py.
2. Add the reference type to REFERENCE_TYPE.
3. Add a new handler function with the reference functionality in extract_referenced_contents.py.
4. Add the handler function to the reference_handlers dictionary.
"""
import os

from tasks.constants.configs import MAKE_QUERY_REFERENCE_TYPES as REFERENCE_TYPES
from tasks.constants.getters import get_query_file_path, get_response_file_path
from tasks.tools.for_create_query.add_text_tags import add_text_tags
from tasks.tools.for_create_query.finalizer import Finalizer
from tasks.tools.for_create_query.referenced_contents_extractor import (
    ReferencedContentExtractor,
)
from tasks.tasks.task_base import TaskBase

extract_referenced_contents = ReferencedContentExtractor().extract_referenced_contents


class ReferenceTitleManager:

    def __init__(self):
        self.title = None

    def set(self, title):
        self.title = title

    def get(self):
        title, self.title = self.title, None
        return title


def format_text_from_references(referenced_contents, updated_content):
    """
    Formats a query string from file references and updated content.

    Args:
        - referenced_contents (list): A list of tuples detailing
            references(type, data).
        - file_path (str): The path to the current file.
        - updated_content (str): The updated content of the current file.
        - root_dir (str): The root directory of the project.

    Returns:
        - str: Formatted query based on file references.
    """
    query = ""
    title_manager = ReferenceTitleManager()
    for referenced_content in referenced_contents:
        content_type, default_title, text = referenced_content
        current_title = title_manager.get()
        title = current_title if current_title else default_title

        if content_type == REFERENCE_TYPES.TITLE:
            title_manager.set(default_title)
        elif content_type == REFERENCE_TYPES.CURRENT_FILE:
            query += f"\n\n--- {title} ---\n{updated_content}"
        elif content_type in REFERENCE_TYPES:
            query += f"\n\n--- {title} ---\n{text}"
        else:
            msg = f"Unknown content type: {content_type}"
            raise ValueError(msg)

    return query


def create_query(file_path, root_dir, query_path, response_path):
    """
    Create a query from the file and referenced contents in the file.

    Args:
        - file_path (str): The path to the file to be processed.
        - root_dir (str): The root directory of the project.
        - query_path (str): The path to the query file.
        - response_path (str): The path to the response file.
    """
    extracted_contents, updated_content = extract_referenced_contents(
        file_path, root_dir
    )
    referenced_contents, begin_text, end_text, make_query_kwargs = extracted_contents

    query = format_text_from_references(referenced_contents, updated_content)

    query = add_text_tags(begin_text, end_text, query)

    finalizer = Finalizer()
    finalizer.set_paths(file_path, query_path, response_path)
    finalizer.finalize(updated_content, query, make_query_kwargs)


class CreateQuery(TaskBase):
    NAME = "Create Query"

    def setup(self):
        super().setup()
        self.file_path = self.additional_args[0]
        self.query_path = get_query_file_path(self.task_executor_root)
        self.response_path = get_response_file_path(self.task_executor_root)

    def execute(self):
        root_dir = self.task_executor_root
        create_query(self.file_path, root_dir, self.query_path, self.response_path)


if __name__ == "__main__":
    default_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    default_file_path = os.path.join(
        default_root, "tasks", "tests", "for_tasks", "create_query_test.py"
    )
    CreateQuery(default_root, default_file_path).main()
