import re

from tasks.configs.constants import AUTOMATIC_PROMPT_TAGS as TAGS
from tasks.configs.constants import CURRENT_FILE_TAG
from tasks.configs.defaults import DIRECTORY_TREE_DEFAULTS
from tasks.tasks.core.line_validation_utils import (
    retrieve_arguments_in_round_brackets,
)
from tasks.tasks.core.line_validation_utils import check_type

PASTE_FILES_PATTERN = re.compile(
    rf"{TAGS.PASTE_FILES.value}\s*((?:\S+\.(?:py|txt|log|md|csv))\s*(?:,\s*\S+\.(?:py|txt|log|md|csv)\s*)*|{CURRENT_FILE_TAG})"
)
FILL_TEXT_PATTERN = re.compile(rf"^{TAGS.FILL_TEXT.value}\s*(.*)")
META_MACROS_PATTERN = re.compile(
    rf"{TAGS.META_MACROS_START.value}(.*?){TAGS.META_MACROS_END.value}"
)
META_MACROS_WITH_ARGS_PATTERN = re.compile(
    rf"{TAGS.META_MACROS_WITH_ARGS_START.value}(.*?){TAGS.META_MACROS_WITH_ARGS_END.value}"
)
COSTUM_FUNCTION_PATTERN = re.compile(
    rf"{TAGS.COSTUM_FUNCTION_START.value}(.*?){TAGS.COSTUM_FUNCTION_END.value}"
)
RUN_SCRIPT_PATTERN = re.compile(
    rf"{TAGS.RUN_SCRIPT.value}\s(\S+\.py|{CURRENT_FILE_TAG})"
)
RUN_PYLINT_PATTERN = re.compile(
    rf"{TAGS.RUN_PYLINT.value}\s(\S+\.py|{CURRENT_FILE_TAG})"
)
UNITTEST_PATTERN = re.compile(rf"{TAGS.UNITTEST.value}\s(\S+\.py|{CURRENT_FILE_TAG})")
DIRECTORY_TREE_PATTERN = re.compile(rf"{TAGS.DIRECTORY_TREE.value}\s(\S+)")
SUMMARIZE_PYTHON_SCRIPT_PATTERN = re.compile(
    rf"{TAGS.SUMMARIZE_PYTHON_SCRIPT.value}\s(\S+\.py|{CURRENT_FILE_TAG})"
)
SUMMARIZE_FOLDER_PATTERN = re.compile(rf"{TAGS.SUMMARIZE_FOLDER.value}\s(\S+)")
CHECKSUM_PATTERN = re.compile(rf"{TAGS.CHECKSUM.value}\s(\S+)")

BEGIN_TAG = TAGS.BEGIN.value
END_TAG = TAGS.END.value
TITLE_TAG = TAGS.TITLE.value
NORMAL_TEXT_TAG = TAGS.NORMAL_TEXT.value
PASTE_CURRENT_FILE_TAG = TAGS.PASTE_CURRENT_FILE.value
ERROR_TAG = TAGS.ERROR.value
SEND_PROMPT_TAG = TAGS.SEND_PROMPT.value


def line_validation_for_begin_text(line):
    """ Validate if the line is a start tag. """
    if BEGIN_TAG in line:
        return line.split(BEGIN_TAG, 1)[1].strip()
    return None


def line_validation_for_end_text(line):
    """ Validate if the line is an end tag. """
    if END_TAG in line:
        return line.split(END_TAG, 1)[1].strip()
    return None


def line_validation_for_title(line):
    """ Validate if the line is a title. """
    if TITLE_TAG in line:
        return line.replace(TITLE_TAG, "").strip()
    return None


def line_validation_for_normal_text(line):
    """ Validate if the line is a normal text. """
    if NORMAL_TEXT_TAG in line:
        return line.replace(NORMAL_TEXT_TAG, "").strip()
    return None


def line_validation_for_paste_current_file(line):
    """ Validate if the line is a current file reference. """
    if PASTE_CURRENT_FILE_TAG in line:
        return True
    return None


def line_validation_for_paste_files(line):
    """ Validate if the line contains references to files. """
    if match := re.search(PASTE_FILES_PATTERN, line):
        file_names = match.group(1).split(",")
        file_names = [file_name.strip() for file_name in file_names]
        arguments = retrieve_arguments_in_round_brackets(line)
        return file_names, arguments
    return None


def line_validation_for_error(line):
    """ Validate if the line is an error. """
    if ERROR_TAG in line:
        return True
    return None


def line_validation_for_fill_text(line):
    """ Validate if the line is a fill text. """
    if match := FILL_TEXT_PATTERN.match(line):
        placeholder = match.group(1)
        return placeholder
    return None


def line_validation_for_meta_macros(line):
    """ Validate if the line is a meta macros. """
    if result := META_MACROS_PATTERN.match(line):
        return result.group(1)
    return None


def line_validation_for_meta_macros_with_args(line):
    """ Validate if the line is a meta macros with arguments. """
    if match := META_MACROS_WITH_ARGS_PATTERN.match(line):
        name = match.group(1)
        arguments = retrieve_arguments_in_round_brackets(line)
        return name, arguments
    return None


def line_validation_for_costum_function(line):
    """ Validate if the line is a costum function. """
    if match := COSTUM_FUNCTION_PATTERN.match(line):
        name = match.group(1)
        arguments = retrieve_arguments_in_round_brackets(line)
        return name, arguments
    return None


def line_validation_for_run_python_script(line):
    """ Validate if the line is a run python script. """
    if match := RUN_SCRIPT_PATTERN.match(line):
        return match.group(1)
    return None


def line_validation_for_run_pylint(line):
    """ Validate if the line is a run pylint. """
    if match := RUN_PYLINT_PATTERN.match(line):
        return match.group(1)
    return None


def line_validation_for_run_unittest(line):
    """ Validate if the line is a run unittest. """
    if match := re.search(UNITTEST_PATTERN, line):
        verbosity = 1
        if arguments := retrieve_arguments_in_round_brackets(line, 1):
            verbosity = arguments[0]
            check_type(verbosity, int, "for unittest verbosity")
        return match.group(1), verbosity
    return None


def line_validation_for_directory_tree(line):
    """ Validate if the line is a directory tree. """
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
    """ Validate if the line is a summarize python script. """
    if match := SUMMARIZE_PYTHON_SCRIPT_PATTERN.match(line):
        include_definitions_without_docstrings = False
        if arguments := retrieve_arguments_in_round_brackets(line, 1):
            bool_ = arguments[0]
            check_type(bool_, bool, "for summarize python script")
            include_definitions_without_docstrings = bool_
        return match.group(1), include_definitions_without_docstrings
    return None


def line_validation_for_summarize_folder(line):
    """ Validate if the line is a summarize folder. """
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
    """ Validate the line to check if it is a valid line to make a prompt. """
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


def line_validation_for_checksum(line):
    """ Validate the line to check if it is a valid line to add checksum. """
    if result := CHECKSUM_PATTERN.match(line):
        try:
            checksum = int(result.group(1).strip())
            return checksum
        except ValueError as e:
            msg = "Invalid checksum line. Must be in the format: #checksum <int>"
            raise ValueError(msg) from e
    return None
