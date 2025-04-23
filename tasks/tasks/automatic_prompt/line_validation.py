import re

from tasks.configs.constants import AUTOMATIC_PROMPT_TAGS as TAGS
from tasks.configs.constants import CURRENT_FILE_TAG, MACRO_TAG
from tasks.configs.defaults import DIRECTORY_TREE_DEFAULTS
from tasks.tasks.core.line_validation_utils import retrieve_arguments_in_round_brackets
from tasks.tasks.core.line_validation_utils import check_type

MACRO_PATTERN = rf"^{MACRO_TAG}\*?[\w_+]+"

# TITLE_PATTERN
title_tag = TAGS.TITLE.value
title_pattern = rf"^{title_tag}\s*([^\n\(\["
title_pattern += r"\{]+)"
TITLE_PATTERN = re.compile(title_pattern)

# PASTE_FILE_PATTERN
paste_file_tag = TAGS.PASTE_FILE.value
file_extensions = r"(?:py|txt|log|md|csv|json|sh)"
file_pattern = rf"\S+\.{file_extensions}"
files_list_pattern = rf"(?:{file_pattern}\s*(?:,\s*{file_pattern}\s*)*)"
paste_file_pattern = rf"{paste_file_tag}\s*({files_list_pattern}|{CURRENT_FILE_TAG})"
PASTE_FILE_PATTERN = re.compile(paste_file_pattern)

# PASTE_DECLARATION_BLOCK_PATTERN
paste_declaration_block_tag = TAGS.PASTE_DECLARATION_BLOCK.value
file_pattern = rf"\S+\.py|{CURRENT_FILE_TAG}"
declaration_pattern = r"([a-zA-Z_][a-zA-Z0-9_]*)"
paste_declaration_block_pattern = (
    rf"{paste_declaration_block_tag}\s+({file_pattern})\s+({declaration_pattern})"
)

# FILL_TEXT_PATTERN
fill_text_tag = TAGS.FILL_TEXT.value
fill_text_pattern = rf"^{fill_text_tag}\s*(.*)"
FILL_TEXT_PATTERN = re.compile(fill_text_pattern)

# META_MACROS_PATTERN
meta_macros_start_tag = TAGS.META_MACROS_START.value
meta_macros_end_tag = TAGS.META_MACROS_END.value
meta_macros_pattern = rf"{meta_macros_start_tag}\s*(.*)\s*{meta_macros_end_tag}"
META_MACROS_PATTERN = re.compile(meta_macros_pattern)

# META_MACROS_WITH_ARGS_PATTERN
meta_macros_with_args_start_tag = TAGS.META_MACROS_WITH_ARGS_START.value
meta_macros_with_args_end_tag = TAGS.META_MACROS_WITH_ARGS_END.value
meta_macros_with_args_pattern = (
    rf"{meta_macros_with_args_start_tag}(.*?){meta_macros_with_args_end_tag}"
)
META_MACROS_WITH_ARGS_PATTERN = re.compile(meta_macros_with_args_pattern)

# COSTUM_FUNCTION_PATTERN
costum_function_start_tag = TAGS.COSTUM_FUNCTION_START.value
costum_function_end_tag = TAGS.COSTUM_FUNCTION_END.value
costum_function_pattern = rf"{costum_function_start_tag}(.*?){costum_function_end_tag}"
COSTUM_FUNCTION_PATTERN = re.compile(costum_function_pattern)

# RUN_PYSCRIPT_PATTERN
run_pyscript_tag = TAGS.RUN_PYSCRIPT.value
run_pyscript_pattern = rf"{run_pyscript_tag}\s(\S+\.py|{CURRENT_FILE_TAG})"
RUN_PYSCRIPT_PATTERN = re.compile(run_pyscript_pattern)

# RUN_BASH_SCRIPT_PATTERN
run_bash_script_tag = TAGS.RUN_BASH_SCRIPT.value
run_bash_script_pattern = rf"{run_bash_script_tag}\s(\S+\.sh|{CURRENT_FILE_TAG})"
RUN_BASH_SCRIPT_PATTERN = re.compile(run_bash_script_pattern)

# RUN_SUBPROCESS_PATTERN
run_subprocess_tag = TAGS.RUN_SUBROCESS.value
run_subprocess_pattern = rf"{run_subprocess_tag}\s*([^\n\(\["
run_subprocess_pattern += r"\{]+)"
RUN_SUBPROCESS_PATTERN = re.compile(run_subprocess_pattern)

# RUN_PYLINT_PATTERN
run_pylint_tag = TAGS.RUN_PYLINT.value
run_pylint_pattern = rf"{run_pylint_tag}\s(\S+\.py|{CURRENT_FILE_TAG})"
RUN_PYLINT_PATTERN = re.compile(run_pylint_pattern)

# UNITTEST_PATTERN
unittest_tag = TAGS.UNITTEST.value
unittest_pattern = rf"{unittest_tag}\s(\S+\.py|{CURRENT_FILE_TAG})"
UNITTEST_PATTERN = re.compile(unittest_pattern)

# DIRECTORY_TREE_PATTERN
directory_tree_tag = TAGS.DIRECTORY_TREE.value
directory_tree_pattern = rf"{directory_tree_tag}\s(\S+)"
DIRECTORY_TREE_PATTERN = re.compile(directory_tree_pattern)

# SUMMARIZE_PYTHON_SCRIPT_PATTERN
summarize_python_script_tag = TAGS.SUMMARIZE_PYTHON_SCRIPT.value
summarize_python_script_pattern = (
    rf"{summarize_python_script_tag}\s(\S+\.py|{CURRENT_FILE_TAG})"
)
SUMMARIZE_PYTHON_SCRIPT_PATTERN = re.compile(summarize_python_script_pattern)

# SUMMARIZE_FOLDER_PATTERN
summarize_folder_tag = TAGS.SUMMARIZE_FOLDER.value
summarize_folder_pattern = rf"{summarize_folder_tag}\s(\S+)"
SUMMARIZE_FOLDER_PATTERN = re.compile(summarize_folder_pattern)

BEGIN_TAG = TAGS.BEGIN.value
END_TAG = TAGS.END.value
TITLE_TAG = TAGS.TITLE.value
NORMAL_TEXT_TAG = TAGS.NORMAL_TEXT.value
SEND_PROMPT_TAG = TAGS.SEND_PROMPT.value


def line_validation_for_begin_text(line):
    """
    Validate if the line is a start tag macro.
    """
    if BEGIN_TAG in line:
        return line.split(BEGIN_TAG, 1)[1].strip()
    return None


def line_validation_for_end_text(line):
    """
    Validate if the line is an end tag macro.
    """
    if END_TAG in line:
        return line.split(END_TAG, 1)[1].strip()
    return None


def line_validation_for_title(line):
    """
    Validate if the line is a title macro.
    """
    if match := TITLE_PATTERN.match(line):
        title = match.group(1).strip()
        level = 1
        if arguments := retrieve_arguments_in_round_brackets(line, 1):
            level = arguments[0]
            check_type(level, int, "for title level")
        return title, level
    return None


def line_validation_for_normal_text(line):
    """
    Validate if the line is a normal text macro.
    """
    if NORMAL_TEXT_TAG in line:
        return line.replace(NORMAL_TEXT_TAG, "").lstrip()
    if not re.match(MACRO_PATTERN, line):  # Check if it is not a macro
        return line
    return None


def line_validation_for_paste_file(line):
    """
    Validate if the line contains references to paste file macro.
    """
    if match := re.search(PASTE_FILE_PATTERN, line):
        file_names = match.group(1).split(",")
        file_names = [file_name.strip() for file_name in file_names]
        line_ranges = []
        updated_line_ranges = []
        if arguments := retrieve_arguments_in_round_brackets(line, 1):
            line_ranges = arguments[0]
            check_type(line_ranges, list, "for paste file line ranges")
            for elem in line_ranges:
                check_type(elem, list, "for paste file line ranges")
                assert (
                    len(elem) == 2
                ), f"for paste file line ranges, expected a list of two elements, but got {elem}"
                updated_line_ranges.append(tuple(elem))
        return file_names, updated_line_ranges
    return None


def line_validation_for_paste_declaration_block(line):
    if match := re.search(paste_declaration_block_pattern, line):
        file_name = match.group(1)
        declaration_name = match.group(2)
        only_declaration_and_docstring = False
        if arguments := retrieve_arguments_in_round_brackets(line, 1):
            only_declaration_and_docstring = arguments[0]
            check_type(
                only_declaration_and_docstring,
                bool,
                "for paste declaration block only declaration and docstring",
            )
        return file_name, declaration_name, only_declaration_and_docstring
    return None


def line_validation_for_fill_text(line):
    """
    Validate if the line is a fill text macro.
    """
    if match := FILL_TEXT_PATTERN.match(line):
        placeholder = match.group(1)
        return placeholder
    return None


def line_validation_for_meta_macros(line):
    """
    Validate if the line is a meta macros macro.
    """
    if result := META_MACROS_PATTERN.match(line):
        return result.group(1)
    return None


def line_validation_for_meta_macros_with_args(line):
    """
    Validate if the line is a meta macros with arguments macro.
    """
    if match := META_MACROS_WITH_ARGS_PATTERN.match(line):
        name = match.group(1)
        arguments = retrieve_arguments_in_round_brackets(line)
        return name, arguments
    return None


def line_validation_for_costum_function(line):
    """
    Validate if the line is a costum function macro.
    """
    if match := COSTUM_FUNCTION_PATTERN.match(line):
        name = match.group(1)
        arguments = retrieve_arguments_in_round_brackets(line)
        return name, arguments
    return None


def line_validation_for_run_pyscript(line):
    """
    Validate if the line is a run python script macro.
    """
    if match := RUN_PYSCRIPT_PATTERN.match(line):
        return match.group(1)
    return None


def line_validation_for_run_bash_script(line):
    """
    Validate if the line is a run bash script macro.
    """
    if match := RUN_BASH_SCRIPT_PATTERN.match(line):
        return match.group(1)
    return None


def line_validation_for_run_subprocess(line):
    """
    Validate if the line is a run subprocess macro.
    """
    if match := RUN_SUBPROCESS_PATTERN.match(line):
        kwargs = {}
        if arguments := retrieve_arguments_in_round_brackets(line, 1):
            kwargs = arguments[0]
            check_type(kwargs, dict, "for run subprocess")
        command = match.group(1)
        return command, kwargs
    return None


def line_validation_for_run_pylint(line):
    """
    Validate if the line is a run pylint macro.
    """
    if match := RUN_PYLINT_PATTERN.match(line):
        return match.group(1)
    return None


def line_validation_for_run_unittest(line):
    """
    Validate if the line is a run unittest macro.
    """
    if match := re.search(UNITTEST_PATTERN, line):
        verbosity = 1
        if arguments := retrieve_arguments_in_round_brackets(line, 1):
            verbosity = arguments[0]
            check_type(verbosity, int, "for unittest verbosity")
        return match.group(1), verbosity
    return None


def line_validation_for_directory_tree(line):
    """
    Validate if the line is a directory tree macro.
    """
    if match := DIRECTORY_TREE_PATTERN.match(line):
        dir = match.group(1)
        max_depth = DIRECTORY_TREE_DEFAULTS.MAX_DEPTH.value
        include_files = DIRECTORY_TREE_DEFAULTS.INCLUDE_FILES.value
        ignore_list = DIRECTORY_TREE_DEFAULTS.IGNORE_LIST.value
        if arguments := retrieve_arguments_in_round_brackets(line, 3):
            if len(arguments) >= 1:
                max_depth = arguments[0]
                check_type(max_depth, int, "for directory tree max depth")
            if len(arguments) >= 2:
                include_files = arguments[1]
                check_type(include_files, bool, "for directory tree include files")
            if len(arguments) == 3:
                ignore_list = arguments[2]
                check_type(ignore_list, list, "for directory tree ignore list")
        return (dir, max_depth, include_files, ignore_list)
    return None


def line_validation_for_summarize_python_script(line):
    """
    Validate if the line is a summarize python script macro.
    """
    if match := SUMMARIZE_PYTHON_SCRIPT_PATTERN.match(line):
        include_definitions_without_docstrings = False
        if arguments := retrieve_arguments_in_round_brackets(line, 1):
            bool_ = arguments[0]
            check_type(bool_, bool, "for summarize python script")
            include_definitions_without_docstrings = bool_
        return match.group(1), include_definitions_without_docstrings
    return None


def line_validation_for_summarize_folder(line):
    """
    Validate if the line is a summarize folder macro.
    """
    if match := SUMMARIZE_FOLDER_PATTERN.match(line):
        dir = match.group(1)
        include_definitions_without_docstrings = False
        excluded_dirs = []
        excluded_files = []
        if arguments := retrieve_arguments_in_round_brackets(line, 3):
            include_definitions_without_docstrings = arguments[0]
            if len(arguments) > 1:
                excluded_dirs = arguments[1]
                check_type(excluded_dirs, list, "for summarize folder excluded dirs")
            if len(arguments) > 2:
                excluded_files = arguments[2]
                check_type(excluded_files, list, "for summarize folder excluded files")
        return (
            dir,
            include_definitions_without_docstrings,
            excluded_dirs,
            excluded_files,
        )


def line_validation_for_send_prompt(line):
    """
    Validate the line to check if it is a valid line to make a prompt macro.
    """
    if SEND_PROMPT_TAG in line:
        modify_inplace = False
        max_tokens = None
        if arguments := retrieve_arguments_in_round_brackets(line, 2):
            modify_inplace = arguments[0]
            check_type(modify_inplace, bool, "for send prompt modify inplace")
            if len(arguments) > 1:
                max_tokens = arguments[1]
                check_type(max_tokens, int, "for send prompt max tokens")
        return modify_inplace, max_tokens
    return None
