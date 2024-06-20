import os

from tasks.configs.constants import AUTOMATIC_PROMPT_MACROS as MACROS
from tasks.tasks.automatic_prompt.line_validation import (
    line_validation_for_begin_text,
    line_validation_for_end_text,
    line_validation_for_title,
    line_validation_for_normal_text,
    line_validation_for_paste_files,
    line_validation_for_error,
    line_validation_for_fill_text,
    line_validation_for_meta_macros,
    line_validation_for_meta_macros_with_args,
    line_validation_for_costum_function,
    line_validation_for_run_python_script,
    line_validation_for_run_pylint,
    line_validation_for_run_unittest,
    line_validation_for_paste_current_file,
    line_validation_for_directory_tree,
    line_validation_for_summarize_python_script,
    line_validation_for_summarize_folder,
    line_validation_for_send_prompt,
)
from tasks.tasks.automatic_prompt.process_tagged_arguments import (
    process_tagged_arguments,
)
from tasks.tasks.core.macro_interpreter import MacroInterpreter
from tasks.utils.for_automatic_prompt.edit_text import edit_text
import tasks.utils.for_automatic_prompt.execute_unittests_from_file as execute_unittests_from_file
from tasks.utils.for_automatic_prompt.find_file_in_1st_level_subdir import (
    find_file_in_1st_level_subdir,
)
from tasks.utils.for_automatic_prompt.generate_directory_tree import (
    generate_directory_tree,
)
from tasks.utils.for_automatic_prompt.get_error_text import get_error_text
from tasks.utils.for_automatic_prompt.render_to_markdown import render_to_markdown
from tasks.utils.for_automatic_prompt.summarize_python_script import (
    summarize_python_file,
)
from tasks.utils.shared.execute_pylint import execute_pylint
from tasks.utils.shared.execute_python_module import execute_python_module
from tasks.utils.shared.find_dir_sloppy import find_dir_sloppy
from tasks.utils.shared.find_file_sloppy import find_file_sloppy
from tasks.utils.shared.format_identifiers_as_code import format_identifiers_as_code


class AutomaticPromptInterpreter(MacroInterpreter):
    """ Interpreter for creating a prompt from macros within text lines. """

    def _check_exists(self, file_path, usage_description):
        if not os.path.exists(file_path):
            msg = f"File for {usage_description} in {file_path} does not exist."
            raise FileNotFoundError(msg)

    def _read_file(self, file_path, usage_description):
        self._check_exists(file_path, usage_description)
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    def validate_begin_text_macro(self, line):
        if result := line_validation_for_begin_text(line):
            result = format_identifiers_as_code(result)
            return (MACROS.BEGIN_TEXT, result, None)
        return None

    def validate_end_text_macro(self, line):
        if result := line_validation_for_end_text(line):
            result = format_identifiers_as_code(result)
            return (MACROS.END_TEXT, result, None)
        return None

    def validate_title_macro(self, line):
        if result := line_validation_for_title(line):
            return (MACROS.TITLE, result, None)
        return None

    def validate_normal_text_macro(self, line):
        if result := line_validation_for_normal_text(line):
            default_title = "Normal Text"
            result = format_identifiers_as_code(result)
            return (MACROS.NORMAL_TEXT, default_title, result)
        return None

    def validate_paste_current_file_macro(self, line):
        # Special File paste case as the interest is in the file content
        # without macros in case there are any
        if result := line_validation_for_paste_current_file(line):
            current_content = self._read_file(
                self.current_file, "paste current file reference"
            )
            # Remove current line to avoid infinite loop in next step
            current_content = current_content.replace(line, "")
            # Remove any macros from the content
            _, current_content = self.extract_macros_from_text(current_content)
            if result[1]:  # Argument for editing the content
                current_content = edit_text(
                    current_content, self.profile.replace_mapping
                )
            current_content = render_to_markdown(
                current_content, extension=self.current_file.split(".")[-1]
            )
            relative_path = os.path.relpath(self.current_file, self.profile.root)
            default_title = f"File at {relative_path}"
            return (MACROS.PASTE_CURRENT_FILE, default_title, current_content)
        return None

    def validate_paste_files_macro(self, line):
        if result := line_validation_for_paste_files(line):
            file_names, edit_content = result
            referenced_files = []
            for file_name in file_names:
                file_path = find_file_sloppy(
                    file_name, self.profile.root, self.current_file
                )
                file_content = self._read_file(file_path, "paste files reference")
                if edit_content:
                    file_content = edit_text(file_content, self.profile.replace_mapping)
                file_content = render_to_markdown(
                    file_content, extension=file_path.split(".")[-1]
                )
                relative_path = os.path.relpath(file_path, self.profile.root)
                default_title = f"File at {relative_path}"
                referenced_file = (MACROS.PASTE_FILE, default_title, file_content)
                referenced_files.append(referenced_file)
            return referenced_files
        return None

    def validate_error_macro(self, line):
        # Tailored for specific test_results.log files
        if line_validation_for_error(line):
            error_text = get_error_text(self.profile.root, self.current_file)
            default_title = "Occured Errors"
            return (MACROS.LOGGED_ERROR, default_title, error_text)
        return None

    def validate_fill_text_macro(self, line):
        if result := line_validation_for_fill_text(line):
            file_path, subdir_name = find_file_in_1st_level_subdir(
                result, self.profile.fill_text_dir, prettify=True
            )
            fill_text = self._read_file(file_path, "fill text reference")
            return (MACROS.FILL_TEXT, subdir_name, fill_text)
        return None

    def validate_meta_macros_with_args(self, line):
        if result := line_validation_for_meta_macros_with_args(line):
            name, args = result
            if args:
                args = process_tagged_arguments(
                    args, self.profile.root, self.current_file
                )
                args = [str(arg) for arg in args]
            dir_ = self.profile.meta_macros_with_args_dir
            template_file = os.path.join(dir_, f"{name}.py")
            self._check_exists(template_file, "meta macros with args reference")
            macros_text = execute_python_module(
                module=template_file,
                args=args,
                env_python_path=self.profile.runner_python_env,
                cwd=self.profile.cwd,
            )
            macros_data, _ = self.extract_macros_from_text(macros_text)
            return macros_data
        return None

    def validate_meta_macros(self, line):
        if result := line_validation_for_meta_macros(line):
            name = result
            dir_ = self.profile.meta_macros_dir
            template_file = os.path.join(dir_, f"{name}.py")
            macros_text = self._read_file(template_file, "meta macros reference")
            macros_data, _ = self.extract_macros_from_text(macros_text)
            return macros_data
        return None

    def validate_costum_function_macro(self, line):
        if result := line_validation_for_costum_function(line):
            name, args = result
            if args:
                args = process_tagged_arguments(
                    args, self.profile.root, self.current_file
                )
                args = [str(arg) for arg in args]
            costum_functions_dir = self.profile.costum_functions_dir
            costum_file, subdir_name = find_file_in_1st_level_subdir(
                name, costum_functions_dir, prettify=True
            )
            output = execute_python_module(
                costum_file,
                args=args,
                env_python_path=self.profile.runner_python_env,
                cwd=self.profile.cwd,
            )
            return (MACROS.COSTUM_FUNCTION, subdir_name, output)
        return None

    def validate_run_python_script_macro(self, line):
        if result := line_validation_for_run_python_script(line):
            script_path = find_file_sloppy(result, self.profile.root, self.current_file)
            environment_path = self.profile.runner_python_env
            script_output = execute_python_module(
                script_path,
                environment_path,
                cwd=self.profile.cwd,
            )
            script_output = render_to_markdown(script_output, format="shell")
            default_title = "Python Script Output"
            return (MACROS.RUN_PYTHON_SCRIPT, default_title, script_output)
        return None

    def validate_run_pylint_macro(self, line):
        if result := line_validation_for_run_pylint(line):
            script_path = find_file_sloppy(result, self.profile.root, self.current_file)
            environment_path = self.profile.runner_python_env
            pylint_output = execute_pylint(script_path, environment_path)
            pylint_output = render_to_markdown(pylint_output, format="shell")
            default_title = "Pylint Output"
            return (MACROS.RUN_PYLINT, default_title, pylint_output)
        return None

    def validate_run_unittest_macro(self, line):
        if result := line_validation_for_run_unittest(line):
            name, verbosity = result
            script_path = find_file_sloppy(name, self.profile.root, self.current_file)
            python_env = self.profile.runner_python_env
            cwd = self.profile.cwd
            unittest_output = execute_python_module(
                module=execute_unittests_from_file,
                args=[script_path, cwd, str(verbosity)],
                env_python_path=python_env,
                cwd=cwd
            )
            unittest_output = render_to_markdown(unittest_output, format="shell")
            default_title = "Unittest Output"
            return (MACROS.RUN_UNITTEST, default_title, unittest_output)
        return None

    def validate_directory_tree_macro(self, line):
        if result := line_validation_for_directory_tree(line):
            dir_, max_depth, include_files, ignore_list = result
            dir_ = find_dir_sloppy(dir_, self.profile.root, self.current_file)
            directory_tree = generate_directory_tree(
                dir_, max_depth, include_files, ignore_list
            )
            default_title = "Directory Tree"
            return (MACROS.DIRECTORY_TREE, default_title, directory_tree)
        return None

    def validate_summarize_python_script_macro(self, line):
        if result := line_validation_for_summarize_python_script(line):
            name, include_definitions_without_docstrings = result
            script_path = find_file_sloppy(name, self.profile.root, self.current_file)
            script_summary = summarize_python_file(
                script_path, include_definitions_without_docstrings
            )
            default_title = f"Summarized Python Script {os.path.basename(script_path)}"
            return (
                MACROS.SUMMARIZE_PYTHON_SCRIPT,
                default_title,
                script_summary,
            )
        return None

    def validate_summarize_folder_macro(self, line):
        if result := line_validation_for_summarize_folder(line):
            (
                folder_path,
                include_definitions_without_docstrings,
                excluded_dirs,
                excluded_files,
            ) = result
            folder_path = find_dir_sloppy(
                folder_path, self.profile.root, self.current_file
            )
            excluded_dirs = [
                find_dir_sloppy(dir_, self.profile.root, self.current_file)
                for dir_ in excluded_dirs
            ]
            excluded_files = [
                find_file_sloppy(file, self.profile.root, self.current_file)
                for file in excluded_files
            ]
            macros_data = []
            for root, _, files in os.walk(folder_path):
                root = os.path.normpath(root)
                if any([excluded_folder in root for excluded_folder in excluded_dirs]):
                    continue
                for file in files:
                    file = os.path.join(root, file)
                    file = os.path.normpath(file)
                    if file in excluded_files or not file.endswith(".py"):
                        continue
                    if script_summary := summarize_python_file(
                        file, include_definitions_without_docstrings
                    ):
                        default_title = (
                            f"Summarized Python Script {os.path.basename(file)}"
                        )
                        macros_data.append(
                            (
                                MACROS.SUMMARIZE_PYTHON_SCRIPT,
                                default_title,
                                script_summary,
                            )
                        )
            return macros_data
        return None

    def validate_send_prompt_macro(self, line):
        if results := line_validation_for_send_prompt(line):
            return (MACROS.SEND_PROMPT, results, None)
        return None

    def post_process_macros(self, macros_data):
        """
        Post-processes the extracted macros to merge comments, begin_text, and
        end_text.

        Args:
            - macros_data (list): A list of tuples containing macro data,
                where each tuple is in the format (macro_type, title, content).

        Returns:
            - tuple: A tuple containing processed macro data, aggregated
                beginning text, aggregated ending text, and a dictionary of
                keyword arguments for the MAKE_QUERY macro.
        """
        # Merge comments in sequence to one comment
        for macro_data in macros_data:
            if macro_data[0] == MACROS.NORMAL_TEXT:
                start = macros_data.index(macro_data)
                index = start + 1
                while (
                    index < len(macros_data)
                    and macros_data[index][0] == MACROS.NORMAL_TEXT
                ):
                    merged_text = f"{macro_data[2].strip()}\n"
                    merged_text += f"{macros_data[index][2].strip()}"
                    macro_data = (
                        macro_data[0],
                        macro_data[1],
                        merged_text,
                    )
                    macros_data.pop(index)
                macros_data[start] = macro_data

        # Merge begin_text and end_text in the referenced contents
        begin_text = []
        end_text = []
        updated_macros_data_1 = []
        for macro_data in macros_data:
            if macro_data[0] == MACROS.BEGIN_TEXT:
                begin_text.append(macro_data[1])
            elif macro_data[0] == MACROS.END_TEXT:
                end_text.append(macro_data[1])
            else:
                updated_macros_data_1.append(macro_data)
        begin_text = "\n".join(begin_text) if begin_text else ""
        end_text = "\n".join(end_text) if end_text else ""

        # Manage the send prompt macro
        updated_macros_data_2 = []
        send_prompt_kwargs = {}
        for macro_data in updated_macros_data_1:
            if macro_data[0] == MACROS.SEND_PROMPT:
                # if len(send_prompt) > 0:
                #     msg = "Multiple send_prompt macros found in the prompt."
                #     raise ValueError(msg)
                # Last send_prompt macro will be used
                modify_inplace, max_tokens = macro_data[1]
                send_prompt_kwargs["modify_inplace"] = modify_inplace
                send_prompt_kwargs["max_tokens"] = max_tokens
            else:
                updated_macros_data_2.append(macro_data)
        send_prompt_kwargs = send_prompt_kwargs or None
        return (updated_macros_data_2, begin_text, end_text, send_prompt_kwargs)
