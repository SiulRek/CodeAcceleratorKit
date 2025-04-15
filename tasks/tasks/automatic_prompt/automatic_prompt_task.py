"""
This module generates an automatic prompt based on macro statements that are
retrieved from the macro field or a string passed as an argument. The prompt,
typically a query, is then finalized and saved in a file.

Available reference types:
| Name                     | Description                             | Pattern                                              | Optional Arguments                                                                            |
|--------------------------|-----------------------------------------|------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| begin_text               | Place start text                        | #B <begin_text>                                      | –                                                                                             |
| end_text                 | Place end text                          | #E <end_text>                                        | –                                                                                             |
| title                    | Title of the reference                  | #T <title>                                           | <level: int>                                                                                  |
| normal_text              | Normal text                             | #N <normal_text>                                     | –                                                                                             |
| paste_file               | Paste file/s                            | #P <file_path> or <file_path_1, file_path_2>         | <line_ranges: List[List[int, int]]>                                                           |
| fill_text                | Add a fill text                         | #<file_name_without_ext>                             | –                                                                                             |
| meta_macros              | Interpret predefined meta macros        | #<file_name_without_ext>_meta                        | –                                                                                             |
| meta_macros_with_args    | Meta macros with args                   | #<file_name_without_ext>_meta+                       | <arg_1, arg_2, ...>                                                                           |
| costum_function          | Paste the output of custom function     | #<file_name_without_ext>_func+                       | <arg_1, arg_2, ...>                                                                           |
| run_python_script        | Run a Python script                     | #run <script_path>                                   | –                                                                                             |
| run_command              | Run Command                             | #$ <command>                                         | <subprocess kwargs: Dict>                                                                     |
| run_pylint               | Run pylint on a file                    | #run_pylint <file_path>                              | –                                                                                             |
| run_unittest             | Run unittest on a file                  | #run_unittest <file_path>                            | <verbosity: int>                                                                              |
| directory_tree           | Get directory tree                      | #tree <directory_path>                               | <max_depth: int, include_files: List[str], ignore_list: List[str]>                            |
| summarize_python_script  | Summarize a Python script               | #summarize <script_path>                             | <include_definitions_with_docstring: bool>                                                    |
| summarize_folder         | Summarize Python scripts in a folder    | #summarize_folder <folder_path>                      | <include_definitions_with_docstrings: bool, excluded_dirs: List[str], excluded_files: List[str]> |
| send_prompt              | Send a prompt from a temporary file     | #send                                                | <create_python_script: bool, max_tokens: int>                                                 |

Usage Example: macros_text = ( "#T This is the Start of the prompt\n", "#C Some
text\n", "#T New Chapter\n", "#run example_script.py\n", "#E Now that we paste
the output of example_script.py we come to the end of prompt\n", "#send (True)"
) AutomaticPromptTask(default_root, default_file_path,
"".join(macros_text)).main()

TODO when adding new macros:
1. Make line validation function in line_validation.py.
2. Add the MACRO to AUTOMATIC_PROMPT_MACROS.
3. Add a new validation method for the new macro in AutomaticPromptInterpreter.
"""

import os

from tasks.configs.constants import AUTOMATIC_PROMPT_MACROS as MACROS
from tasks.tasks.automatic_prompt.ask_user_for_macros import ask_user_for_macros
from tasks.tasks.automatic_prompt.automatic_prompt_interpreter import (
    AutomaticPromptInterpreter,
)
from tasks.tasks.automatic_prompt.chat_manager import ChatManager
from tasks.tasks.core.task_base import TaskBase
from tasks.utils.shared.backup_handler import BackupHandler


class AutomaticPromptTask(TaskBase):
    """
    Task to create an automatic prompt based on macros.

    Attributes:
        - NAME (str): The name of the task.
    """

    NAME = "Automatic Prompt"

    def setup(self):
        """
        Sets up the AutomaticPrompt task by initializing the file path.
        """
        super().setup()
        self.current_file = self.additional_args[0]
        if len(self.additional_args) > 1:
            self.macros_text = self.additional_args[1]
        else:
            self.macros_text = self._get_user_specified_macros()
        lines = self.macros_text.split("\n")
        self.macros_text = "\n".join(line for line in lines if line.strip())

    def _get_user_specified_macros(self):
        macros_text = ask_user_for_macros()
        macros_text = "\n".join(
            line for line in macros_text.split("\n") if line.strip()
        )
        return macros_text

    def _format_text_from_macros(self, macros_data):
        """
        Formats a prompt string from macros_data and updated content.

        Args:
            - macros_data (list): A list of tuples detailing macros (type, title, data).

        Returns:
            - str: Formatted prompt based on file macros.
        """
        prompt = ""
        for macros_data in macros_data:
            macro_type = macros_data["type"]
            text = macros_data["text"] if "text" in macros_data else None

            if macro_type in MACROS:
                if text:
                    prompt += f"\n{text}\n" if prompt else f"{text}\n"
                elif not macro_type in [MACROS.SEND_PROMPT]:
                    msg = f"Macro {macro_type} is missing text."
                    raise ValueError(msg)
            else:
                msg = f"Unknown macro type: {macro_type}"
                raise ValueError(msg)

        return prompt

    def _extract_send_prompt_parameters(self, macros_data):
        macro_types = [macro["type"] for macro in macros_data]
        send_prompt_count = macro_types.count(MACROS.SEND_PROMPT)
        send_prompt_kwargs = None
        if send_prompt_count > 1:
            raise ValueError(
                "Only one SEND_PROMPT macro is allowed in the macros text."
            )
        elif send_prompt_count == 1:
            send_prompt_macro = macros_data.pop(macro_types.index(MACROS.SEND_PROMPT))
            send_prompt_kwargs = send_prompt_macro["kwargs"]

        reminder_prompt = self._format_text_from_macros(macros_data)
        return send_prompt_kwargs, reminder_prompt

    def execute(self):
        """
        Executes the AutomaticPrompt task to format the prompt and interact
        with AI.
        """
        interpreter = AutomaticPromptInterpreter(self.profile)
        backup_handler = BackupHandler(
            self.profile.backup_dir, self.profile.max_backups
        )

        interpreter.current_file = (
            self.current_file
        )  # Allows for paste current file macro
        macros_data, reminder_text = interpreter.extract_macros_from_text(
            self.macros_text, post_process=True
        )
        if reminder_text != "":
            raise ValueError(
                "Not able to process the following macros:\n"
                f"{reminder_text}"
            )

        send_prompt_kwargs, prompt = self._extract_send_prompt_parameters(macros_data)

        cm = ChatManager(
            self.current_file,
            self.profile.chats_dir,
            backup_handler,
        )
        cm.store_prompt(prompt, self.profile.copy_prompt)
        if send_prompt_kwargs:
            cm.send_prompt(send_prompt_kwargs)


if __name__ == "__main__":
    """
    Entry point for the module. Initializes and runs the AutomaticPrompt task.
    """
    default_root = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."
    )
    default_file_path = os.path.join(
        default_root, "tasks", "tests", "for_tasks", "automatic_prompt_test.py"
    )
    AutomaticPromptTask(default_root, default_file_path).main()
