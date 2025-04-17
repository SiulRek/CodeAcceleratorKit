from enum import Enum
import os
import re

# ----------------- General Constants -----------------
TASKS_ROOT = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
TEST_RESULTS_FILE = "test_results.log"
CURRENT_FILE_TAG = "File"
CURRENT_DIRECTORY_TAG = "Dir"
REGISTERED_RUNNERS_JSON = os.path.join(TASKS_ROOT, "tasks", "configs", "registered_runners.json")
PROFILE_SUBFOLDER = "profile"
TASKS_PYTHON_ENV = os.path.join(TASKS_ROOT, "venv")
TASKS_CACHE = os.path.join(TASKS_ROOT, "tasks", "__taskscache__")
MAX_BACKUPS = 70
MACRO_TAG = "#"

# ----------------- For Automatic Prompt -----------------
class AUTOMATIC_PROMPT_MACROS(Enum):
    BEGIN_TEXT = "begin_text",
    END_TEXT = "end_text",
    TITLE = "title"
    NORMAL_TEXT = "normal_text"
    PASTE_FILE = "paste_file"
    FILL_TEXT = "fill_text"
    COSTUM_FUNCTION = "costum_function"
    RUN_PYTHON_SCRIPT = "run_python_script"
    RUN_SUBPROCESS = "run_subprocess"
    RUN_PYLINT = "run_pylint"
    RUN_UNITTEST = "run_unittest"
    DIRECTORY_TREE = "directory_tree"
    SUMMARIZE_PYTHON_SCRIPT = "summarize_python_script"
    SUMMARIZE_FOLDER = "summarize_folder" # Summarize all Python scripts in a folder
    SEND_PROMPT = "send_prompt"


class AUTOMATIC_PROMPT_TAGS(Enum):
    BEGIN = MACRO_TAG + "B "
    END = MACRO_TAG + "E "
    TITLE = MACRO_TAG + "T "
    NORMAL_TEXT = MACRO_TAG + "N "
    PASTE_FILE = MACRO_TAG + "P "
    META_MACROS_START = MACRO_TAG
    META_MACROS_END = "_meta"
    META_MACROS_WITH_ARGS_START = MACRO_TAG
    META_MACROS_WITH_ARGS_END = r"_meta\+"
    COSTUM_FUNCTION_START = MACRO_TAG
    COSTUM_FUNCTION_END = "_func"
    FILL_TEXT = MACRO_TAG + r"\*"
    RUN_SCRIPT = MACRO_TAG + "run"
    RUN_PYLINT = MACRO_TAG + "pylint"
    RUN_SUBROCESS = MACRO_TAG + r"\$"
    UNITTEST = MACRO_TAG + "unittest"
    DIRECTORY_TREE = MACRO_TAG + "tree"
    SUMMARIZE_PYTHON_SCRIPT = MACRO_TAG + "summarize"
    SUMMARIZE_FOLDER = MACRO_TAG + "summarize_folder"
    SEND_PROMPT = MACRO_TAG + "send"


# ----------------- For Format Python -----------------
LINE_WIDTH = 79
INDENT_SPACES = " " * 4
DOC_QUOTE = '"""'

class FORMAT_PYTHON_MACROS(Enum):
    SELECT_ONLY = "select_only"
    SELECT_NOT = "select_not"
    FORCE_SELECT_OF = "force_select_of"
    CHECKPOINTING = "checkpointing"

class FORMAT_PYTHON_TAGS(Enum):
    SELECT_ONLY = "#only"
    SELECT_NOT = "#not"
    FORCE_SELECT_OF = "#force"
    CHECKPOINTS = "#checkpointing"
