import os
import subprocess

import clipboard

from tasks.configs.constants import AUTOMATIC_PROMPT_MACROS as MACROS
from tasks.tasks.automatic_prompt.line_validation import (
    line_validation_for_begin_text,
    line_validation_for_end_text,
    line_validation_for_title,
    line_validation_for_normal_text,
    line_validation_for_paste_file,
    line_validation_for_paste_folder_files,
    line_validation_for_paste_declaration_block,
    line_validation_for_paste_clipboard,
    line_validation_for_fill_text,
    line_validation_for_meta_macros,
    line_validation_for_meta_macros_with_args,
    line_validation_for_costum_function,
    line_validation_for_run_pyscript,
    line_validation_for_run_bash_script,
    line_validation_for_run_subprocess,
    line_validation_for_run_pylint,
    line_validation_for_run_unittest,
    line_validation_for_directory_tree,
    line_validation_for_summarize_python_script,
    line_validation_for_summarize_folder,
    line_validation_for_send_prompt,
)
from tasks.tasks.automatic_prompt.process_tagged_arguments import (
    process_tagged_arguments,
)
from tasks.tasks.core.macro_interpreter import MacroInterpreter
import tasks.utils.for_automatic_prompt.execute_unittests_from_file as execute_unittests_from_file
from tasks.utils.for_automatic_prompt.find_file_in_1st_level_subdir import (
    find_file_in_1st_level_subdir,
)
from tasks.utils.for_automatic_prompt.generate_directory_tree import (
    generate_directory_tree,
)
from tasks.utils.for_automatic_prompt.get_declaration_block import get_declaration_block
from tasks.utils.for_automatic_prompt.render_to_markdown_code_block import (
    render_to_markdown_code_block,
)
from tasks.utils.for_automatic_prompt.summarize_python_script import (
    summarize_python_file,
)
from tasks.utils.shared.execute_pylint import execute_pylint
from tasks.utils.shared.execute_python_module import execute_python_module
from tasks.utils.shared.find_closest_matching_dir import find_closest_matching_dir
from tasks.utils.shared.find_closest_matching_file import find_closest_matching_file
from tasks.utils.shared.format_identifiers_as_code import format_identifiers_as_code
from tasks.utils.shared.path_helpers import standardize_path


class AutomaticPromptInterpreter(MacroInterpreter):
    """
    Interpreter for creating a prompt from macros within text lines.
    """

    def _check_exists(self, file_path, usage_description):
        if not os.path.exists(file_path):
            msg = f"File for {usage_description} in {file_path} does not exist."
            raise FileNotFoundError(msg)

    def _read_file(self, file_path, usage_description):
        self._check_exists(file_path, usage_description)
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except UnicodeDecodeError as e:
            msg = f"Cannot read file {file_path} for {usage_description}. "
            raise UnicodeDecodeError(msg) from e

    def validate_begin_text_macro(self, line):
        if result := line_validation_for_begin_text(line):
            result = format_identifiers_as_code(result)
            macro_data = {"type": MACROS.BEGIN_TEXT, "text": result}
            return macro_data
        return None

    def validate_end_text_macro(self, line):
        if result := line_validation_for_end_text(line):
            result = format_identifiers_as_code(result)
            macro_data = {"type": MACROS.END_TEXT, "text": result}
            return macro_data
        return None

    def validate_title_macro(self, line):
        if result := line_validation_for_title(line):
            title, level = result
            title = "#" * level + " " + title
            title += "\n" + "-" * 10
            macro_data = {"type": MACROS.TITLE, "text": title}
            return macro_data
        return None

    def validate_normal_text_macro(self, line):
        if result := line_validation_for_normal_text(line):
            result = format_identifiers_as_code(result)
            macro_data = {"type": MACROS.NORMAL_TEXT, "text": result}
            return macro_data
        return None

    def _extract_line_ranges(self, text, line_ranges):
        text_chunks = []
        lines = text.splitlines(True)
        length = len(lines)
        for start, stop in line_ranges:
            start -= 1
            stop -= 1
            assert start >= 0, "Line number must be greater than 0"
            assert stop < length, "Line number must be less than the number of lines"
            if start == stop:
                text_chunks.append(lines[start])
            else:
                text_chunks.append("".join(lines[start:stop]))

        return "\n".join(text_chunks).strip()

    def validate_paste_file_macro(self, line):
        if result := line_validation_for_paste_file(line):
            file_names, line_ranges = result
            macro_data_list = []
            for file_name in file_names:
                file_path = find_closest_matching_file(
                    file_name, self.profile.root, self.current_file
                )
                file_content = self._read_file(file_path, "paste files reference")
                if line_ranges and file_path.lower().endswith(".py"):
                    file_content = self._extract_line_ranges(file_content, line_ranges)
                    # Enables merging of consecutive line ranges and declaration
                    # blocks into a single code snippet
                    macro_type = MACROS.PASTE_DECLARATION_BLOCK
                else:
                    macro_type = MACROS.PASTE_FILE
                    file_content = render_to_markdown_code_block(
                        file_content, extension=file_path.split(".")[-1]
                    )
                macro_data = {"type": macro_type, "text": file_content}
                macro_data_list.append(macro_data)
            return macro_data_list
        return None

    def validate_paste_folder_files_macro(self, line):
        if result := line_validation_for_paste_folder_files(line):
            folder_name, title_level, excluded_dirs, excluded_files = result
            folder_path = find_closest_matching_dir(
                folder_name, self.profile.root, self.current_file
            )
            excluded_dirs = [
                find_closest_matching_dir(dir_, self.profile.root, self.current_file)
                for dir_ in excluded_dirs
            ]
            excluded_files = [
                find_closest_matching_file(file, self.profile.root, self.current_file)
                for file in excluded_files
            ]
            macros_data = []
            for root, _, files in os.walk(folder_path):
                root = standardize_path(root)
                if root in excluded_dirs:
                    continue
                for file in files:
                    file = os.path.join(root, file)
                    file = standardize_path(file)
                    if file in excluded_files:
                        continue
                    rel_file = os.path.relpath(file, folder_path)
                    file_content = self._read_file(file, "paste folder files reference")
                    file_content = render_to_markdown_code_block(
                        file_content, extension=file.split(".")[-1]
                    )
                    macros_data.append(
                        {
                            "type": MACROS.TITLE,
                            "text": "#" * title_level + " " + rel_file,
                        }
                    )
                    macros_data.append(
                        {"type": MACROS.PASTE_FILE, "text": file_content}
                    )
            return macros_data
        return None

    def validate_paste_declaration_block_macro(self, line):
        if result := line_validation_for_paste_declaration_block(line):
            file_name, declaration_name, only_declaration_and_docstring = result
            file_path = find_closest_matching_file(
                file_name, self.profile.root, self.current_file
            )

            declaration_block = get_declaration_block(
                name=declaration_name,
                script=file_path,
                only_declaration_and_docstring=only_declaration_and_docstring,
            )
            macro_data = {
                "type": MACROS.PASTE_DECLARATION_BLOCK,
                "text": declaration_block,
            }
            return macro_data
        return None

    def validate_paste_clipboard_macro(self, line):
        if result := line_validation_for_paste_clipboard(line):
            _, code_language = result
            content = clipboard.paste()
            if not content:
                raise ValueError("Clipboard is empty.")
            if code_language:
                content = render_to_markdown_code_block(content, language=code_language)
            macro_data = {"type": MACROS.PASTE_CLIPBOARD, "text": content}
            return macro_data
        return None

    def validate_fill_text_macro(self, line):
        if result := line_validation_for_fill_text(line):
            file_path = find_file_in_1st_level_subdir(
                result, self.profile.fill_text_dir, prettify=True
            )
            fill_text = self._read_file(file_path, "fill text reference")
            macro_data = {"type": MACROS.FILL_TEXT, "text": fill_text}
            return macro_data
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
            costum_file = find_file_in_1st_level_subdir(
                name, costum_functions_dir, prettify=True
            )
            output = execute_python_module(
                costum_file,
                args=args,
                env_python_path=self.profile.runner_python_env,
                cwd=self.profile.cwd,
            )
            macro_data = {"type": MACROS.COSTUM_FUNCTION, "text": output}
            return macro_data
        return None

    def validate_run_pyscript_macro(self, line):
        if result := line_validation_for_run_pyscript(line):
            script_path = find_closest_matching_file(result, self.profile.root, self.current_file)
            environment_path = self.profile.runner_python_env
            script_output = execute_python_module(
                script_path,
                environment_path,
                cwd=self.profile.cwd,
            )
            script_output = render_to_markdown_code_block(
                script_output, language="shell"
            )
            macro_data = {"type": MACROS.RUN_PYSCRIPT, "text": script_output}
            return macro_data
        return None

    def validate_run_bash_script_macro(self, line):
        if result := line_validation_for_run_bash_script(line):
            script_path = find_closest_matching_file(result, self.profile.root, self.current_file)
            output = subprocess.run(
                [script_path],
                shell=True,
                capture_output=True,
                text=True,
            )
            output = output.stderr if output.returncode != 0 else output.stdout
            output = render_to_markdown_code_block(output, language="shell")
            macro_data = {"type": MACROS.RUN_BASH_SCRIPT, "text": output}
            return macro_data
        return None

    def validate_run_subprocess_macro(self, line):
        if result := line_validation_for_run_subprocess(line):
            command, kwargs = result
            kwargs.setdefault("shell", True)
            # Force 'capture_output' and 'text' kwargs to True
            kwargs["capture_output"] = True
            kwargs["text"] = True
            output = subprocess.run(command, **kwargs)
            output = output.stderr if output.returncode != 0 else output.stdout
            text = "$ " + command + "\n" + output
            macro_data = {"type": MACROS.RUN_SUBPROCESS, "text": text}
            return macro_data
        return None

    def validate_run_pylint_macro(self, line):
        if result := line_validation_for_run_pylint(line):
            script_path = find_closest_matching_file(result, self.profile.root, self.current_file)
            environment_path = self.profile.runner_python_env
            pylint_output = execute_pylint(script_path, environment_path)
            pylint_output = render_to_markdown_code_block(
                pylint_output, language="shell"
            )
            macro_data = {"type": MACROS.RUN_PYLINT, "text": pylint_output}
            return macro_data
        return None

    def validate_run_unittest_macro(self, line):
        if result := line_validation_for_run_unittest(line):
            name, verbosity = result
            script_path = find_closest_matching_file(name, self.profile.root, self.current_file)
            python_env = self.profile.runner_python_env
            cwd = self.profile.cwd
            unittest_output = execute_python_module(
                module=execute_unittests_from_file,
                args=[script_path, cwd, str(verbosity)],
                env_python_path=python_env,
                cwd=cwd,
            )
            unittest_output = render_to_markdown_code_block(
                unittest_output, language="shell"
            )
            macro_data = {"type": MACROS.RUN_UNITTEST, "text": unittest_output}
            return macro_data
        return None

    def validate_directory_tree_macro(self, line):
        if result := line_validation_for_directory_tree(line):
            dir_, max_depth, include_files, ignore_list = result
            dir_ = find_closest_matching_dir(dir_, self.profile.root, self.current_file)
            directory_tree = generate_directory_tree(
                dir_, max_depth, include_files, ignore_list
            )
            directory_tree = render_to_markdown_code_block(
                directory_tree, language="shell"
            )
            macro_data = {"type": MACROS.DIRECTORY_TREE, "text": directory_tree}
            return macro_data
        return None

    def validate_summarize_python_script_macro(self, line):
        if result := line_validation_for_summarize_python_script(line):
            name, include_definitions_without_docstrings = result
            script_path = find_closest_matching_file(name, self.profile.root, self.current_file)
            script_summary = summarize_python_file(
                script_path, include_definitions_without_docstrings
            )
            macro_data = {
                "type": MACROS.SUMMARIZE_PYTHON_SCRIPT,
                "text": script_summary,
            }
            return macro_data
        return None

    def validate_summarize_folder_macro(self, line):
        if result := line_validation_for_summarize_folder(line):
            (
                folder_path,
                include_definitions_without_docstrings,
                title_level,
                excluded_dirs,
                excluded_files,
            ) = result
            folder_path = find_closest_matching_dir(
                folder_path, self.profile.root, self.current_file
            )
            excluded_dirs = [
                find_closest_matching_dir(dir_, self.profile.root, self.current_file)
                for dir_ in excluded_dirs
            ]
            excluded_files = [
                find_closest_matching_file(file, self.profile.root, self.current_file)
                for file in excluded_files
            ]
            macros_data = []
            for root, _, files in os.walk(folder_path):
                root = standardize_path(root)
                if root in excluded_dirs:
                    continue
                for file in files:
                    file = os.path.join(root, file)
                    file = standardize_path(file)
                    if file in excluded_files or not file.endswith(".py"):
                        continue
                    if script_summary := summarize_python_file(
                        file, include_definitions_without_docstrings
                    ):  
                        rel_file = os.path.relpath(file, folder_path)
                        title = "#" * title_level + " " + rel_file
                        macros_data.append({
                            "type": MACROS.TITLE,
                            "text": title,
                        })
                        script_summary = render_to_markdown_code_block(
                            script_summary, language="python"
                        )
                        macro_data = {
                            "type": MACROS.SUMMARIZE_PYTHON_SCRIPT,
                            "text": script_summary,
                        }
                        macros_data.append(macro_data)
            return macros_data
        return None

    def validate_send_prompt_macro(self, line):
        if results := line_validation_for_send_prompt(line):
            kwargs = {"modify_inplace": results[0], "max_tokens": results[1]}
            macro_data = {"type": MACROS.SEND_PROMPT, "kwargs": kwargs}
            return macro_data
        return None

    def post_process_macros(self, macros_data):
        """
        Post-processes the extracted macros to merge normal text, begin_text,
        end_text and declaration blocks.
        """
        merged_data = []
        begin_text_list = []
        end_text_list = []

        i = 0
        while i < len(macros_data):
            macro = macros_data[i]
            m_type = macro["type"]

            # Merge consecutive NORMAL_TEXT blocks
            if m_type == MACROS.NORMAL_TEXT:
                text_blocks = [macro["text"].strip()]
                i += 1
                while (
                    i < len(macros_data)
                    and macros_data[i]["type"] == MACROS.NORMAL_TEXT
                ):
                    text_blocks.append(macros_data[i]["text"].strip())
                    i += 1
                merged_data.append(
                    {"type": MACROS.NORMAL_TEXT, "text": "\n".join(text_blocks)}
                )

            # Merge consecutive PASTE_DECLARATION_BLOCK blocks
            elif m_type == MACROS.PASTE_DECLARATION_BLOCK:
                code_blocks = [macro["text"]]
                i += 1
                while (
                    i < len(macros_data)
                    and macros_data[i]["type"] == MACROS.PASTE_DECLARATION_BLOCK
                ):
                    code_blocks.append(macros_data[i]["text"])
                    i += 1
                merged_code = render_to_markdown_code_block(
                    "\n\n\n".join(code_blocks), language="python"
                )
                merged_data.append(
                    {"type": MACROS.PASTE_DECLARATION_BLOCK, "text": merged_code}
                )

            # Collect BEGIN_TEXT
            elif m_type == MACROS.BEGIN_TEXT:
                begin_text_list.append(macro["text"])
                i += 1

            # Collect END_TEXT
            elif m_type == MACROS.END_TEXT:
                end_text_list.append(macro["text"])
                i += 1

            # Other types stay as is
            else:
                merged_data.append(macro)
                i += 1

        # Prepend BEGIN_TEXT if any
        if begin_text_list:
            merged_data.insert(
                0,
                {
                    "type": MACROS.BEGIN_TEXT,
                    "text": "\n".join(begin_text_list) + "\n" + ("*" * 10),
                },
            )

        # Append END_TEXT if any
        if end_text_list:
            merged_data.append(
                {
                    "type": MACROS.END_TEXT,
                    "text": ("*" * 10) + "\n" + "\n".join(end_text_list),
                }
            )

        return merged_data
