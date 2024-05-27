import os

from tasks.configs.constants import MAKE_QUERY_MACROS as MACROS
from tasks.tasks.create_query.line_validation import (
    line_validation_for_begin_text,
    line_validation_for_end_text,
    line_validation_for_title,
    line_validation_for_comment,
    line_validation_for_files,
    line_validation_for_error,
    line_validation_for_fill_text,
    line_validation_for_run_python_script,
    line_validation_for_run_pylint,
    line_validation_for_run_unittest,
    line_validation_for_current_file_reference,
    line_validation_for_directory_tree,
    line_validation_for_summarize_python_script,
    line_validation_for_summarize_folder,
    line_validation_for_macros_template,
    line_validation_for_make_query,
)
from tasks.tasks.foundation.macro_interpreter import MacroInterpreter
from tasks.tools.for_create_query.get_error_text import get_error_text
from tasks.tools.for_create_query.get_fill_text import get_fill_text
from tasks.tools.for_create_query.get_macros_template import get_macros_template
from tasks.tools.for_create_query.summarize_python_script import summarize_python_file
from tasks.tools.general.execute_pylint import execute_pylint
from tasks.tools.general.execute_python_module import execute_python_module
import tasks.tools.general.execute_unittests_from_file as execute_unittests_from_file
from tasks.tools.general.find_dir import find_dir
from tasks.tools.general.find_file import find_file
from tasks.tools.general.generate_directory_tree import generate_directory_tree
from tasks.tools.general.get_temporary_script_path import get_temporary_script_path


class CreateQueryInterpreter(MacroInterpreter):
    """Interpreter for creating a query from macros within text lines."""

    def validate_begin_text_macro(self, line):
        if result := line_validation_for_begin_text(line):
            return (MACROS.BEGIN_TEXT, result, None)
        return None

    def validate_end_text_macro(self, line):
        if result := line_validation_for_end_text(line):
            return (MACROS.END_TEXT, result, None)
        return None

    def validate_title_macro(self, line):
        if result := line_validation_for_title(line):
            return (MACROS.TITLE, result, None)
        return None

    def validate_comment_macro(self, line):
        if result := line_validation_for_comment(line):
            default_title = "Comment"
            return (MACROS.COMMENT, default_title, result)
        return None

    def validate_files_macro(self, line):
        if result := line_validation_for_files(line):
            referenced_files = []
            for file_name in result:
                file_path = find_file(file_name, self.profile.root, self.file_path)
                with open(file_path, "r", encoding="utf-8") as file:
                    relative_path = os.path.relpath(file_path, self.profile.root)
                    default_title = f"File at {relative_path}"
                    referenced_file = (MACROS.FILE, default_title, file.read())
                    referenced_files.append(referenced_file)
            return referenced_files
        return None

    def validate_current_file_macro(self, line):
        if line_validation_for_current_file_reference(line):
            relative_path = os.path.relpath(self.file_path, self.profile.root)
            default_title = f"File at {relative_path}"
            return (MACROS.CURRENT_FILE, default_title, None)
        return None

    def validate_error_macro(self, line):
        if line_validation_for_error(line):
            error_text = get_error_text(self.profile.root, self.file_path)
            default_title = "Occured Errors"
            return (MACROS.LOGGED_ERROR, default_title, error_text)
        return None

    def validate_fill_text_macro(self, line):
        if result := line_validation_for_fill_text(line):
            fill_text, default_title = get_fill_text(result, self.profile.fill_text_dir)
            return (MACROS.FILL_TEXT, default_title, fill_text)
        return None

    def validate_run_python_script_macro(self, line):
        if result := line_validation_for_run_python_script(line):
            script_path = find_file(result, self.profile.root, self.file_path)
            environment_path = self.profile.runner_python_env
            script_output = execute_python_module(
                script_path, 
                environment_path,
                cwd=self.profile.cwd,
                )
            default_title = "Python Script Output"
            return (MACROS.RUN_PYTHON_SCRIPT, default_title, script_output)
        return None

    def validate_run_pylint_macro(self, line):
        if result := line_validation_for_run_pylint(line):
            script_path = find_file(result, self.profile.root, self.file_path)
            environment_path = self.profile.tasks_python_env
            pylint_output = execute_pylint(script_path, environment_path)
            default_title = "Pylint Output"
            return (MACROS.RUN_PYLINT, default_title, pylint_output)
        return None

    def validate_run_unittest_macro(self, line):
        if result := line_validation_for_run_unittest(line):
            name, verbosity = result
            script_path = find_file(name, self.profile.root, self.file_path)
            temp_script_path = get_temporary_script_path(self.profile.runners_cache)
            python_env = self.profile.runner_python_env
            cwd = self.profile.cwd
            unittest_output = execute_python_module(
                module=execute_unittests_from_file,
                args=[script_path, cwd, str(verbosity)],
                env_python_path=python_env,
                cwd=cwd,
                temp_script_path=temp_script_path,
            )
            default_title = "Unittest Output"
            return (MACROS.RUN_UNITTEST, default_title, unittest_output)
        return None

    def validate_directory_tree_macro(self, line):
        if result := line_validation_for_directory_tree(line):
            dir, max_depth, include_files, ignore_list = result
            dir = find_dir(dir, self.profile.root, self.file_path)
            directory_tree = generate_directory_tree(
                dir, max_depth, include_files, ignore_list
            )
            default_title = "Directory Tree"
            return (MACROS.DIRECTORY_TREE, default_title, directory_tree)
        return None

    def validate_summarize_python_script_macro(self, line):
        if result := line_validation_for_summarize_python_script(line):
            name, include_definitions_without_docstrings = result
            script_path = find_file(name, self.profile.root, self.file_path)
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
            folder_path = find_dir(folder_path, self.profile.root, self.file_path)
            excluded_dirs = [
                find_dir(dir, self.profile.root, self.file_path)
                for dir in excluded_dirs
            ]
            excluded_files = [
                find_file(file, self.profile.root, self.file_path)
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

    def validate_macros_template_macro(self, line):
        if result := line_validation_for_macros_template(line):
            macros_template = get_macros_template(
                result, self.profile.macros_templates_dir
            )
            macros_data, _ = self.extract_macros_from_text(macros_template)
            return macros_data
        return None

    def validate_make_query_macro(self, line):
        if results := line_validation_for_make_query(line):
            return (MACROS.MAKE_QUERY, results, None)
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
            if macro_data[0] == MACROS.COMMENT:
                start = macros_data.index(macro_data)
                index = start + 1
                while (
                    index < len(macros_data) and macros_data[index][0] == MACROS.COMMENT
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

        # Organize the make query reference
        updated_macros_data_2 = []
        make_query_kwargs = {}
        for macro_data in updated_macros_data_1:
            if macro_data[0] == MACROS.MAKE_QUERY:
                # if len(make_query_kwargs) > 0:
                #     msg = "Multiple make_query macros found in the query."
                #     raise ValueError(msg) # Last make_query macro will be used
                modify_inplace, max_tokens = macro_data[1]
                make_query_kwargs["modify_inplace"] = modify_inplace
                make_query_kwargs["max_tokens"] = max_tokens
            else:
                updated_macros_data_2.append(macro_data)
        make_query_kwargs = make_query_kwargs or None
        return (updated_macros_data_2, begin_text, end_text, make_query_kwargs)
