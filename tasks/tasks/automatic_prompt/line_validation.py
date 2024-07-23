import re

from tasks.configs.constants import AUTOMATIC_PROMPT_TAGS as TAGS
from tasks.configs.constants import CURRENT_FILE_TAG
from tasks.configs.defaults import DIRECTORY_TREE_DEFAULTS
from tasks.tasks.core.line_validation_utils import retrieve_arguments_in_round_brackets
from tasks.tasks.core.line_validation_utils import check_type

# PASTE_FILES_PATTERN
paste_files_tag = TAGS.PASTE_FILES.value
file_extensions = r"(?:py|txt|log|md|csv)"
file_pattern = rf"\S+\.{file_extensions}"
files_list_pattern = rf"(?:{file_pattern}\s*(?:,\s*{file_pattern}\s*)*)"
current_file_pattern = rf"{CURRENT_FILE_TAG}"
paste_files_pattern = (
    rf"{paste_files_tag}\s*({files_list_pattern}|{current_file_pattern})"
)
PASTE_FILES_PATTERN = re.compile(paste_files_pattern)

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

# RUN_SCRIPT_PATTERN
run_script_tag = TAGS.RUN_SCRIPT.value
run_script_pattern = rf"{run_script_tag}\s(\S+\.py|{CURRENT_FILE_TAG})"
RUN_SCRIPT_PATTERN = re.compile(run_script_pattern)

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

# CHECKSUM_PATTERN
checksum_tag = TAGS.CHECKSUM.value
checksum_pattern = rf"{checksum_tag}\s(\d+)"
CHECKSUM_PATTERN = re.compile(checksum_pattern)

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
        edit_content = False
        if args := retrieve_arguments_in_round_brackets(line, 1):
            edit_content = args[0]
            check_type(edit_content, bool, "for paste current file")
        return True, edit_content
    return None


def line_validation_for_paste_files(line):
    """ Validate if the line contains references to files. """
    if match := re.search(PASTE_FILES_PATTERN, line):
        file_names = match.group(1).split(",")
        file_names = [file_name.strip() for file_name in file_names]
        edit_content = False
        if args := retrieve_arguments_in_round_brackets(line, 1):
            edit_content = args[0]
            check_type(edit_content, bool, "for paste files")
        return file_names, edit_content
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
