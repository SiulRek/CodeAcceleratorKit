import os
import warnings

from tasks.management.task_runner_profile import TaskRunnerProfile
from tasks.utils.for_format_python.add_encoding_to_open import add_encoding_to_open
from tasks.utils.for_format_python.ensure_newline_at_end import ensure_newline_at_end
from tasks.utils.for_format_python.format_comments import format_comments
from tasks.utils.for_format_python.format_docstrings import format_docstrings
from tasks.utils.for_format_python.rearrange_imports import rearrange_imports
from tasks.utils.for_format_python.format_exceptions import format_exceptions
from tasks.utils.for_format_python.refactor_warnings import refactor_warnings
from tasks.utils.for_format_python.remove_f_from_empty_fstrings import (
    remove_f_from_empty_fstrings,
)
from tasks.utils.for_format_python.remove_line_comments import remove_line_comments
from tasks.utils.for_format_python.remove_trailing_parts import remove_trailing_parts
from tasks.utils.for_format_python.remove_unnecessary_else import (
    remove_unnecessary_else,
)
from tasks.utils.for_format_python.remove_unused_imports import remove_unused_imports
from tasks.utils.for_format_python.run_black_formatting import format_with_black
from tasks.utils.shared.execute_pylint import execute_pylint

STRATEGIES = {
    # Abbreviation: (function, description, format_with_subprocess,
    # forcing_required)
    "RL": (remove_line_comments, "Remove line comments", False, True),
    "RT": (remove_trailing_parts, "Remove trailing parts", False, False),
    "AE": (add_encoding_to_open, "Add encoding to open", False, False),
    "RUE": (remove_unnecessary_else, "Remove unnecessary else", False, False),
    "RF": (remove_f_from_empty_fstrings, "Remove f from empty fstrings", False, False),
    "RW": (refactor_warnings, "Refactor warnings", False, False),
    "RI": (rearrange_imports, "Rearrange imports", False, False),
    "RU": (remove_unused_imports, "Remove unused imports", False, False),
    "BF": (format_with_black, "Run Black formatting", True, False),
    "FE": (format_exceptions, "Format exceptions", False, False),
    "FD": (format_docstrings, "Format docstrings", False, False),
    "FC": (format_comments, "Format comments", False, False),
    "EN": (ensure_newline_at_end, "Ensure newline at end", False, True),
    "PL": (execute_pylint, "Execute Pylint", True, False),
}


def make_checkpoint(file_path, updated_code, description, checkpoint_dir):
    """
    Create a checkpoint of the file at the current state.

    Args:
        - file_path (str): Path to the file to create a checkpoint of.
        - updated_code (str): Updated code to save in the checkpoint.
        - description (str): Description of the changes made to the code.
        - checkpoint_dir (str): Directory to save the checkpoint in.
    """
    if hasattr(make_checkpoint, "counter"):
        make_checkpoint.counter += 1
        counter = str(make_checkpoint.counter).zfill(3)
    else:
        make_checkpoint.counter = 1
        counter = str(make_checkpoint.counter).zfill(3)
    if hasattr(make_checkpoint, "checkpoint_dir"):
        checkpoint_dir = make_checkpoint.checkpoint_dir
    else:
        file_name = os.path.basename(file_path).split(".")[0]
        id = "000"
        dir_name = id + "_" + file_name
        while os.path.exists(os.path.join(checkpoint_dir, dir_name)):
            id = str(int(id) + 1).zfill(3)
            dir_name = id + "_" + file_name
        checkpoint_dir = os.path.join(checkpoint_dir, dir_name)
        os.makedirs(checkpoint_dir)
        make_checkpoint.checkpoint_dir = checkpoint_dir
    description = description.lower().replace(" ", "_")
    checkpoint_path = os.path.join(checkpoint_dir, f"step_{counter}_{description}.py")
    with open(checkpoint_path, "w", encoding="utf-8") as file:
        file.write(updated_code)
    print(f"--------> Checkpoint created at {checkpoint_path}")


def format_python_file(
    file_path,
    select_only=[],
    select_not=[],
    force_select_of=[],
    checkpoint_dir=None,
    python_env_path=None,
    modules_info=None,
):
    """
    Apply formatting strategies to a python file. The strategies are applied in
    the order they are defined in the STRATEGIES dictionary.

    Args:
        - file_path (str): Path to the file to format.
        - select_only (list): List of strategy abbreviations to apply. If
            specified, only the strategies in the list are applied. Default is
            [].
        - select_not (list): List of strategy abbreviations to exclude. If
            specified, all strategies except the ones in the list are applied.
            Default is [].
        - force_select_of (list): List of strategy abbreviations to force
            apply, as some are not applied by default. Default is [].
        - checkpoint_dir (str): Directory to save the checkpoints in. If
            specified, checkpointing is enabled.
        - python_env_path (str): Path to the python environment to use for
            subprocess formatting. Required for strategies using subprocesses.
        - modules_info (dict): A dictionary containing information about the
            loaded modules. Keys are 'standard_library', 'third_party', and
            'local'. Used for rearranging imports. If None skips rearranging
            imports.
    """
    selected_to_force = force_select_of

    if not file_path.endswith(".py"):
        msg = f"File {file_path} is not a python file"
        raise ValueError(msg)
    if not os.path.exists(file_path):
        msg = f"File {file_path} not found"
        raise FileNotFoundError(msg)

    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()

    checkpointing = bool(checkpoint_dir)
    if checkpointing:
        os.makedirs(checkpoint_dir, exist_ok=True)

    if select_only and select_not:
        msg = "Cannot have both select_only and select_not options specified."
        raise ValueError(msg)

    is_forcable = {key: STRATEGIES[key][3] for key in STRATEGIES}
    strategies = {}
    if select_only:
        # Also forcable strategies can be included in select_only
        strategies = {key: STRATEGIES[key] for key in select_only}
    elif select_not:
        strategies = {
            key: STRATEGIES[key]
            for key in STRATEGIES
            if key not in select_not and not is_forcable[key]
        }
    else:
        strategies = {
            key: value for key, value in STRATEGIES.items() if not is_forcable[key]
        }

    if selected_to_force:
        for key in selected_to_force:
            strategies[key] = STRATEGIES[key]

    updated_code = code
    for _, (function, description, format_with_subprocess, _) in strategies.items():
        if format_with_subprocess:
            if not python_env_path:
                raise ValueError(
                    "Python environment path is required for format with subprocess."
                )
            if updated_code != code:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(updated_code)

            if message := function(file_path, python_env_path):
                print(message)
            with open(file_path, "r", encoding="utf-8") as file:
                updated_code = file.read()
        elif function == rearrange_imports:
            if not modules_info:
                warnings.warn(
                    "Modules info not provided. Skipping rearranging imports."
                )
                continue
            updated_code = function(updated_code, modules_info)
        else:
            updated_code = function(updated_code)
        file_name = os.path.basename(file_path)
        print(f"--------> {description} applied to {file_name}")
        if checkpointing:
            make_checkpoint(file_path, updated_code, description, checkpoint_dir)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_code)


if __name__ == "__main__":
    path = r"tasks/tests/for_tasks/format_python_test.py"

    root_dir = os.path.abspath(os.path.join(path, "..", "..", "..", ".."))
    profile = TaskRunnerProfile(root_dir)
    format_python_file(
        path,
        checkpoint_dir=profile.checkpoint_dir,
        python_env_path=profile.runner_python_env,
        # select_only=["FD"]
    )
    print(f"File Formatted at {path}")
