import os

from tasks.configs.constants import (
    MAKE_QUERY_MACROS as MACROS,
)
from tasks.configs.getters import get_environment_path, get_environment_path_of_tasks, get_temporary_script_path
from tasks.tools.for_create_query.get_error_text import (
    get_error_text,
)
from tasks.tools.for_create_query.get_fill_text import get_fill_text
from tasks.tools.for_create_query.get_query_template import (
    get_query_template,
)
from tasks.tasks.engines.for_create_query.line_validation import (
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
    line_validation_for_query_template,
    line_validation_for_make_query,
)
from tasks.tools.for_create_query.summarize_python_script import (
    summarize_python_file,
)
from tasks.tools.general.execute_pylint import execute_pylint
from tasks.tools.general.execute_python_module import (
    execute_python_module,
)
import tasks.tools.general.execute_unittests_from_file as execute_unittests_from_file
from tasks.tasks.engines.macro_engine import MacroEngine
from tasks.tools.general.find_dir import find_dir
from tasks.tools.general.find_file import find_file
from tasks.tools.general.generate_directory_tree import (
    generate_directory_tree,
)


class CreateQueryEngine(MacroEngine):

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
                file_path = find_file(file_name, self.runner_root, self.file_path)
                with open(file_path, "r", encoding="utf-8") as file:
                    relative_path = os.path.relpath(file_path, self.runner_root)
                    default_title = f"File at {relative_path}"
                    referenced_file = (MACROS.FILE, default_title, file.read())
                    referenced_files.append(referenced_file)
            return referenced_files
        return None

    def validate_current_file_macro(self, line):
        if line_validation_for_current_file_reference(line):
            relative_path = os.path.relpath(self.file_path, self.runner_root)
            default_title = f"File at {relative_path}"
            return (MACROS.CURRENT_FILE, default_title, None)
        return None

    def validate_error_macro(self, line):
        if line_validation_for_error(line):
            error_text = get_error_text(self.runner_root, self.file_path)
            default_title = "Occured Errors"
            return (MACROS.LOGGED_ERROR, default_title, error_text)
        return None

    def validate_fill_text_macro(self, line):
        if result := line_validation_for_fill_text(line):
            fill_text, default_title = get_fill_text(result, self.runner_root)
            return (MACROS.FILL_TEXT, default_title, fill_text)
        return None

    def validate_run_python_script_macro(self, line):
        if result := line_validation_for_run_python_script(line):
            script_path = find_file(result, self.runner_root, self.file_path)
            environment_path = get_environment_path(self.runner_root)
            script_output = execute_python_module(script_path, environment_path)
            default_title = "Python Script Output"
            return (MACROS.RUN_PYTHON_SCRIPT, default_title, script_output)
        return None

    def validate_run_pylint_macro(self, line):
        if result := line_validation_for_run_pylint(line):
            script_path = find_file(result, self.runner_root, self.file_path)
            environment_path = get_environment_path_of_tasks()
            pylint_output = execute_pylint(script_path, environment_path)
            default_title = "Pylint Output"
            return (MACROS.RUN_PYLINT, default_title, pylint_output)
        return None

    def validate_run_unittest_macro(self, line):
        if result := line_validation_for_run_unittest(line):
            name, verbosity = result
            script_path = find_file(name, self.runner_root, self.file_path)
            temp_script_path = get_temporary_script_path(self.runner_root)
            unittest_output = execute_python_module(
                module=execute_unittests_from_file,
                args=[script_path, str(verbosity)],
                env_python_path=get_environment_path(self.runner_root),
                cwd=self.runner_root,
                temp_script_path=temp_script_path,
            )
            default_title = "Unittest Output"
            return (MACROS.RUN_UNITTEST, default_title, unittest_output)
        return None

    def validate_directory_tree_macro(self, line):
        if result := line_validation_for_directory_tree(line):
            dir, max_depth, include_files, ignore_list = result
            dir = find_dir(dir, self.runner_root, self.file_path)
            directory_tree = generate_directory_tree(
                dir, max_depth, include_files, ignore_list
            )
            default_title = "Directory Tree"
            return (MACROS.DIRECTORY_TREE, default_title, directory_tree)
        return None

    def validate_summarize_python_script_macro(self, line):
        if result := line_validation_for_summarize_python_script(line):
            name, include_definitions_without_docstrings = result
            script_path = find_file(name, self.runner_root, self.file_path)
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
            folder_path = find_dir(folder_path, self.runner_root, self.file_path)
            excluded_dirs = [
                find_dir(dir, self.runner_root, self.file_path) for dir in excluded_dirs
            ]
            excluded_files = [
                find_file(file, self.runner_root, self.file_path)
                for file in excluded_files
            ]
            referenced_contents = []
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
                        referenced_contents.append(
                            (
                                MACROS.SUMMARIZE_PYTHON_SCRIPT,
                                default_title,
                                script_summary,
                            )
                        )
            return referenced_contents
        return None

    def validate_query_template_macro(self, line):
        if result := line_validation_for_query_template(line):
            query_template = get_query_template(result, self.runner_root)
            referenced_contents, _ = self._extract_macros(query_template)
            return referenced_contents
        return None

    def validate_make_query_macro(self, line):
        if results := line_validation_for_make_query(line):
            return (MACROS.MAKE_QUERY, results, None)
        return None

    def post_process_macros(self, referenced_contents):
        # Merge comments in sequence to one comment
        for referenced_content in referenced_contents:
            if referenced_content[0] == MACROS.COMMENT:
                start = referenced_contents.index(referenced_content)
                index = start + 1
                while (
                    index < len(referenced_contents)
                    and referenced_contents[index][0] == MACROS.COMMENT
                ):
                    merged_text = f"{referenced_content[2].strip()}\n"
                    merged_text += f"{referenced_contents[index][2].strip()}"
                    referenced_content = (
                        referenced_content[0],
                        referenced_content[1],
                        merged_text,
                    )
                    referenced_contents.pop(index)
                referenced_contents[start] = referenced_content

        # Merge begin_text and end_text in the referenced contents
        begin_text = ""
        end_text = ""
        for referenced_content in referenced_contents:
            if referenced_content[0] == MACROS.BEGIN_TEXT:
                begin_text += referenced_content[1]
                referenced_contents.remove(referenced_content)
            elif referenced_content[0] == MACROS.END_TEXT:
                end_text += referenced_content[1]
                referenced_contents.remove(referenced_content)

        # Organize the make query reference
        make_query_kwargs = {}
        for referenced_content in referenced_contents:
            if referenced_content[0] == MACROS.MAKE_QUERY:
                if len(make_query_kwargs) > 0:
                    msg = "Multiple make_query macros found in the query."
                    raise ValueError(msg)
                create_python_script, max_tokens = referenced_content[1]
                make_query_kwargs["create_python_script"] = create_python_script
                make_query_kwargs["max_tokens"] = max_tokens
        make_query_kwargs = make_query_kwargs or None
        return (referenced_contents, begin_text, end_text, make_query_kwargs)