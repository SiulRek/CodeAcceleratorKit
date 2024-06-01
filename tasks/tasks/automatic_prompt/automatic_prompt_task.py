"""
This module generates an automatic prompt based on macro statements that are retrieved from either a file or a string passed as an argument. The prompt, typically a query, is then finalized and saved in a file.

Available reference types:
| Name                    | Description                           | Pattern                                          | Arguments                                                                                |
|-------------------------|---------------------------------------|--------------------------------------------------|------------------------------------------------------------------------------------------|
| begin_text              | Place start text                      | #B <begin_text>                                  | -                                                                                        |
| end_text                | Place end text                        | #E <end_text>                                    | -                                                                                        |
| title                   | Title of the reference                | #T <title>                                       | -                                                                                        |
| normal_text             | Normal text                           | #N <normal_text>                                 | -                                                                                        |
| paste_files             | Paste file/s                          | # <file_path> or <file_path_1, file_path_2>      | -                                                                                        |
| paste_current_file      | Paste Current file                    | # File                                           | -                                                                                        |
| error                   | Get logged errors                     | #L                                               | -                                                                                        |
| fill_text               | Add a fill text                       | #*<file_name_without_ext>                        | -                                                                                        |
| meta_macros             | Interprete predifined meta macros     | #<file_name_without_ext>_meta                    | -                                                                                        |
| meta_macros_with_args   | "" meta macros with args              | #<file_name_without_ext>_meta+                   | <arg_1, arg_2, ...>                                                                      |
| costum_function         | Paste the output of costum function   | #<file_name_without_ext>_func+                   | <arg_1, arg_2, ...>                                                                      |
| run_python_script       | Run a Python script                   | #run <script_path>                               | -                                                                                        |
| run_pylint              | Run pylint on a file                  | #run_pylint <file_path>                          | -                                                                                        |
| run_unittest            | Run unittest on a file                | #run_unittest <file_path>                        | <verbosity>                                                                              |
| directory_tree          | Get directory tree                    | #tree <directory_path>                           | <max_depth, include_files, ignore_list (semicolon-separated list)>                       |
| summarize_python_script | Summarize a Python script             | #summarize <script_path>                         | <include_definitions_with_docstrings>                                                    |
| summarize_folder        | Summarize Python scripts in a folder  | #summarize_folder <folder_path>                  | <include_definitions_with_docstrings, excluded_dirs, excluded_files>                     |
| send_prompt             | Send a prompt from a temporary file   | #send                                            | <create_python_script, max_tokens>                                                       |
| checksum                | Check if provided checksum corresponds| #checksum <number_of_references>                 | -                                                                                        |

Usage Example:
macros_text = (
    "#T This is the Start of the prompt\n"
    "#C Some text\n"
    "#T New Chapter\n"
    "#run example_script.py\n"
    "#E Now that we paste the output of example_script.py we come to the end of prompt\n"#
)
AutomaticPromptTask(default_root, default_file_path, "".join(macros_text)).main()

TODO when adding new macros:
1. Make line validation function in line_validation.py.
2. Add the MACRO to AUTOMATIC_PROMPT_MACROS.
3. Add a new validation method for the new macro in AutomaticPromptInterpreter.
"""

import os

from tasks.configs.constants import AUTOMATIC_PROMPT_MACROS as MACROS
from tasks.tasks.automatic_prompt.automatic_prompt_interpreter import AutomaticPromptInterpreter
from tasks.tasks.automatic_prompt.finalizer import Finalizer
from tasks.tasks.core.task_base import TaskBase
from tasks.utils.for_automatic_prompt.add_text_tags import add_text_tags
from tasks.utils.shared.backup_handler import BackupHandler


class ChapterTitleManager:
    """
    Manages the title of the chapter for prompt formatting.

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
    Formats a prompt string from macros_data and updated content.

    Args:
        - macros_data (list): A list of tuples detailing macros (type, title, data).
        - updated_content (str): The updated content of the current file. It is
            used for the current file macro.

    Returns:
        - str: Formatted prompt based on file macros.
    """
    prompt = ""
    title_manager = ChapterTitleManager()
    for macros_data in macros_data:
        content_type, default_title, text = macros_data
        current_title = title_manager.get()
        title = current_title if current_title else default_title

        if content_type == MACROS.TITLE:
            title_manager.set(default_title)
        elif content_type == MACROS.PASTE_CURRENT_FILE:
            prompt += f"\n\n--- {title} ---\n{updated_content}"
        elif content_type in MACROS:
            prompt += f"\n\n--- {title} ---\n{text}"
        else:
            msg = f"Unknown content type: {content_type}"
            raise ValueError(msg)

    return prompt


class AutomaticPromptTask(TaskBase):
    """
    Task to create an automatic prompt based on macros.

    Attributes:
        - NAME (str): The name of the task.
    """

    NAME = "Automatic Prompt"

    def setup(self):
        """Sets up the AutomaticPrompt task by initializing the file path."""
        super().setup()
        self.file_path = self.additional_args[0]
        self.macros_text = None
        if len(self.additional_args) > 1:
            self.macros_text = self.additional_args[1]

    def execute(self):
        """Executes the AutomaticPrompt task to format and finalize the prompt."""
        interpreter = AutomaticPromptInterpreter(self.profile)
        backup_handler = BackupHandler(
            self.profile.backup_dir, self.profile.max_backups
        )

        if self.macros_text:
            interpreter.file_path = self.file_path  # Allows for paste current file macro
            macros_data, _ = interpreter.extract_macros_from_text(
                self.macros_text, post_process=True
            )
            with open(self.file_path, "r") as file:
                updated_content = file.read()
        else:
            macros_data, updated_content = interpreter.extract_macros_from_file(
                self.file_path
            )
        macros_data, begin_text, end_text, send_prompt_kwargs = macros_data

        prompt = format_text_from_macros(macros_data, updated_content)

        prompt = add_text_tags(begin_text, end_text, prompt)

        finalizer = Finalizer()
        finalizer.set_directories(
            self.file_path,
            self.profile.chats_dir,
        )
        finalizer.set_backup_handler(backup_handler)
        finalizer.validate_contents(updated_content)
        finalizer.finalize(prompt, send_prompt_kwargs)


if __name__ == "__main__":
    """Entry point for the module. Initializes and runs the AutomaticPrompt task."""
    default_root = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."
    )
    default_file_path = os.path.join(
        default_root, "tasks", "tests", "for_tasks", "automatic_prompt_test.py"
    )
    AutomaticPromptTask(default_root, default_file_path).main()
