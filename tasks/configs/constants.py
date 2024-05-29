from enum import Enum
import os
import re

# ----------------- General Constants -----------------
TASKS_ROOT = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
TEST_RESULTS_FILE = "test_results.log"
FILE_TAG = "File"
REGISTERED_RUNNERS_JSON = os.path.join(TASKS_ROOT, "tasks", "configs", "registered_runners.json")
PROFILE_SUBFOLDER = "profile"
TASKS_PYTHON_ENV = os.path.join(TASKS_ROOT, "venv")
TASKS_CACHE = os.path.join(TASKS_ROOT, "tasks", "__taskscache__")
MAX_BACKUPS = 70

# ----------------- For Automatic Prompt -----------------
class AUTOMATIC_PROMPT_MACROS(Enum):
    BEGIN_TEXT = "begin_text",
    END_TEXT = "end_text",
    COMMENT = "comment"
    PASTE_FILE = "paste_file"
    LOGGED_ERROR = "error"
    CURRENT_FILE = "current_file"
    RUN_PYTHON_SCRIPT = "run_python_script"
    RUN_PYLINT = "run_pylint"
    RUN_UNITTEST = "run_unittest"
    DIRECTORY_TREE = "directory_tree"
    SUMMARIZE_PYTHON_SCRIPT = "summarize_python_script"
    SUMMARIZE_FOLDER = "summarize_folder" # Summarize all Python scripts in a folder
    FILL_TEXT = "fill_text"
    TITLE = "title"
    SEND_PROMPT = "send_prompt"


class AUTOMATIC_PROMPT_TAGS(Enum):
    BEGIN = "#B "
    END = "#E "
    RUN_PYLINT = "#pylint"
    RUN_SCRIPT = "#run"
    UNITTEST = "#unittest"
    DIRECTORY_TREE = "#tree"
    SUMMARIZE_PYTHON_SCRIPT = "#summarize"
    SUMMARIZE_FOLDER = "#summarize_folder"
    MACROS_TEMPLATE_START = "#"
    MACROS_TEMPLATE_END = "_macros"
    CHECKSUM = "#checksum"
    PASTE_FILES = "#"
    FILL_TEXT = r"#\*"
    ERROR = "#L"
    TITLE = "#T "
    COMMENT = "#C "
    CURRENT_FILE = f"#{FILE_TAG}"
    SEND_PROMPT = "#send"

TEST_RESULT_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - (ERROR|INFO) - .*)")

# ----------------- For Format Python -----------------
LINE_WIDTH = 80
INTEND = " " * 4
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
