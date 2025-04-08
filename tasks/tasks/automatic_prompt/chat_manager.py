import os

import pyperclip
from tasks.utils.for_automatic_prompt.send_prompt import send_prompt
from tasks.utils.for_automatic_prompt.extract_python_code import extract_python_code


class ChatManager:
    """
    Manages the chat interactions for the Automatic Prompt task.

    Args:
        - file_path (str): Path to the file being processed.
        - chats_dir (str): Directory for chat files.
        - backup_handler (BackupHandler): Instance of BackupHandler for
            managing backups.
    """

    def __init__(self, file_path, chats_dir, backup_handler):
        """
        Initializes the ChatManager with file path and chat directory.

        Args:
            - file_path (str): Path to the file being processed.
            - chats_dir (str): Directory for chat files.
            - backup_handler (BackupHandler): Instance of BackupHandler for
                managing backups.
        """
        self.file_path = None
        self.file_name = None
        self.file_ext = None
        self.chats_dir = None
        self.backup_handler = backup_handler
        self.prompt_path = None
        self.response_path = None
        self.checksum = None
        self.updated_contents = None
        self.final_lines = []
        self.prompt = None

        self._set_directories(file_path, chats_dir)

    def _set_directories(self, file_path, chats_dir):
        self.file_path = os.path.normpath(file_path)
        self.file_name = os.path.basename(self.file_path).split(".")[0]
        self.file_ext = os.path.splitext(self.file_path)[1]
        self.chats_dir = chats_dir

        # Special case that allows to have macro_text.txt, generated_prompt.md
        # and generated_response.md in the same directory
        if self.file_path.endswith("automatic_prompt" + os.sep + "macros_text.txt"):
            self.file_name = "generated"
            self.chats_dir = os.path.dirname(self.file_path)

    def store_prompt(self, prompt, copy_prompt):
        """
        Saves the prompt to a file and optionally copies it to the clipboard.

        Args:
            - prompt (str): The prompt to be sent.
            - copy_prompt (bool): Whether to copy the prompt to clipboard.
        """
        self.prompt = prompt
        self.prompt_path = os.path.join(self.chats_dir, f"{self.file_name}_prompt.md")

        with open(self.prompt_path, "w", encoding="utf-8") as file:
            file.write(prompt)

        if copy_prompt:
            pyperclip.copy(self.prompt)
            print("Prompt copied to clipboard.")


    def send_prompt(self, **kwargs):
        """
        Sends the prompt to the chat manager.

        Args:
            - prompt (str): The prompt to be sent.
            - copy_prompt (bool): Whether to copy the prompt to clipboard.
        """
        modify_inplace = kwargs["modify_inplace"]
        max_tokens = kwargs["max_tokens"]
        response = (
            send_prompt(self.prompt, max_tokens) if max_tokens else send_prompt(self.prompt)
        )
        response_path = os.path.join(
            self.chats_dir, f"{self.file_name}_response.md"
        )
        with open(response_path, "w", encoding="utf-8") as file:
            file.write(response)
        print("Response saved to:", response_path)
        if modify_inplace:
            self.backup_handler.backup_file(self.file_path)
            python_code = extract_python_code(response)
            with open(self.file_path, "w", encoding="utf-8") as file:
                file.write(python_code)
            print("File modified in place.")