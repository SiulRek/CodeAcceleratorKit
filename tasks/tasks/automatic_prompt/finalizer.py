import os
import warnings

from tasks.tasks.automatic_prompt.line_validation import line_validation_for_checksum
from tasks.utils.for_automatic_prompt.extract_python_code import extract_python_code
from tasks.utils.for_automatic_prompt.send_prompt import send_prompt


def write_to_file(file_path, content):
    """
    Writes specified content to the provided file.

    Args:
        - file_path (str): The path to the file to write to.
        - content (str): The content to be written in the file.
    """
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


class Finalizer:
    """Processes final stages of Automatic Prompt task. Includes validation, checksum verification, sending prompt, and processing response."""

    def __init__(self):
        """Initializes Finalizer with predefined paths and content states."""
        self.file_path = None
        self.prompt_path = None
        self.response_path = None
        self.checksum = None
        self.updated_contents = None
        self.final_lines = []
        self.prompt = None

    def set_directories(self, file_path, chats_dir):
        """
        Sets file, prompt and response paths using provided base directory and
        file path.

        Args:
            - file_path (str): Path of the target file.
            - chats_dir (str): Base directory to save the prompt and
                response.
        """
        self.file_path = file_path
        self.file_name = os.path.basename(self.file_path).split(".")[0]
        self.file_ext = os.path.splitext(self.file_path)[1]
        self.chats_dir = chats_dir

    def set_backup_handler(self, backup_handler):
        """
        Attaches the provided backup handler to the finalizer.

        Args:
            - backup_handler (BackupHandler): Instance of a BackupHandler to
                be attached.
        """
        self.backup_handler = backup_handler

    def _validate_lines(self):
        """Verifies each line of the updated contents for validation checksums.
        Extra lines are added to the content map for final lines."""
        for line in self.updated_contents.splitlines():
            if result := line_validation_for_checksum(line.strip()):
                self.checksum = result
            else:
                self.final_lines.append(line)

    def _verify_checksum(self):
        """
        Validates that the difference in length of original and final lines
        matches the validated checksum. Raises an error if the checksum does not
        match.
        """
        if self.checksum:
            with open(self.file_path, "r", encoding="utf-8") as file:
                file_contents = file.read().splitlines()
                diff = len(file_contents) - len(self.final_lines)
                if diff != self.checksum:
                    msg = f"Checksum mismatch: {diff} != {self.checksum}"
                    raise ValueError(msg)

    def validate_contents(self, updated_contents):
        """
        Verifies that the checksum of the updated contents matches the verified
        one.

        Args:
            - updated_contents (str): Updated content to be verified.
        """
        self.updated_contents = updated_contents
        self._validate_lines()
        self._verify_checksum()

    def _store_prompt(self, prompt):
        """
        Writes the prompt to the prompt path.

        Args:
            - prompt (str): Prompt to be written.
        """
        prompt_name = self.file_name + "_prompt.txt"
        prompt_path = os.path.join(self.chats_dir, prompt_name)
        write_to_file(prompt_path, prompt)
        print(f"Prompt saved to {prompt_path}")

    def _send_prompt(self, prompt, max_tokens):
        """
        Prepares a prompt based on provided parameters and executes it. Writes
        the response of the prompt to prompt_path.

        Args:
            - prompt (str): Prompt to be executed.
            - max_tokens (int): Maximum number of tokens to be generated by
                model.
        """
        self._store_prompt(prompt)
        print("Sending prompt...")
        response = send_prompt(prompt, max_tokens) if max_tokens else send_prompt(prompt)
        return response

    def _process_response(self, response, modify_inplace):
        """
        Writes the response obtained from a prompt.

        Args:
            - response (str): The response of the prompt.
            - modify_inplace (bool): Whether to save the response back in
                the original file.
        """
        python_code = extract_python_code(response)

        response_name = self.file_name + "_response.txt"
        response_path = os.path.join(self.chats_dir, response_name)
        write_to_file(response_path, response)
        print(f"Response saved to {response_path}")
        if python_code:
            code_name = self.file_name + "_code.py"
            code_path = os.path.join(self.chats_dir, code_name)
            write_to_file(code_path, python_code)
            print(f"Python code saved to {code_path}")
        if modify_inplace:
            if not python_code:
                warnings.warn("No Python code found in response.")
            else:
                self.backup_handler.store_backup(
                    self.file_path, "Before modification from automatic prompt task."
                )
                backuped_path = self.backup_handler.get_backup_path(self.file_path)
                print(f"Backup saved to {backuped_path}")
                write_to_file(self.file_path, python_code)

    def finalize(self, prompt, send_prompt_kwargs):
        """
        Carries out the final stages of content processing including validation,
        checksum verification, sending prompt, and processing response.

        Args:
            - prompt (str): Prompt to be executed.
            - send_prompt_kwargs (dict): Parameters including
                'modify_inplace' and 'max_tokens' for the prompt.
        """
        self.prompt = prompt
        final_text = "\n".join(self.final_lines)
        write_to_file(self.file_path, final_text)
        if send_prompt_kwargs:
            max_tokens = send_prompt_kwargs.get("max_tokens")
            modify_inplace = send_prompt_kwargs.get("modify_inplace")
            response = self._send_prompt(prompt, max_tokens)
            self._process_response(response, modify_inplace)
        else:
            self._store_prompt(prompt)
