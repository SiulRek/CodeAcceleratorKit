import os

from tasks.constants.getters import (
    get_checkpoint_directory,
    get_environment_path_of_tasks,
)
from tasks.tools.for_cleanup.format_docstrings import (
    format_docstrings,
)
from tasks.tools.for_cleanup.rearrange_imports import (
    rearrange_imports,
)
from tasks.tools.for_cleanup.refactore_exception import (
    refactor_exception,
)
from tasks.tools.for_cleanup.remove_line_comments import (
    remove_line_comments,
)
from tasks.tools.for_cleanup.remove_trailing_parts import (
    remove_trailing_parts,
)
from tasks.tools.for_cleanup.remove_unused_imports import (
    remove_unused_imports,
)
from tasks.tools.for_cleanup.run_black_formatting import (
    format_with_black,
)
from tasks.tools.general.execute_pylint import execute_pylint

STRATEGIES = {
    "RT": (remove_trailing_parts, "Remove trailing parts", False),
    "RL": (remove_line_comments, "Remove line comments", False),
    "RE": (refactor_exception, "Refactor exception", False),
    "RI": (rearrange_imports, "Rearrange imports", False),
    "RU": (remove_unused_imports, "Remove unused imports", False),
    "FM": (format_docstrings, "Format docstrings", False),
    "BF": (format_with_black, "Run Black formatting", True),
    "PL": (execute_pylint, "Execute Pylint", True),
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
    with open(checkpoint_path, "w") as file:
        file.write(updated_code)
    print(f"--------> Checkpoint created at {checkpoint_path}")


def cleanup_file(
    file_path,
    select_only=None,
    select_not=None,
    checkpointing=False,
    checkpoint_dir=None,
    python_env_path=None,
):
    """
    Apply cleanup strategies to a python file. The strategies are applied in the
    order they are defined in the STRATEGIES dictionary.

    Args:
        - file_path (str): Path to the file to clean.
        - select_only (list): List of strategies to apply. Default to None.
        - select_not (list): List of strategies to exclude. Default to None.
        - checkpointing (bool): Whether to create checkpoints.
            DefaulttoFalse.
        - checkpoint_dir (str): Directory to save the checkpointsin.Required
            if checkpointing is True.
        - python_env_path (str): Path to the python environment to
            useforsubprocess cleaning. Required for subprocess cleaning.
    """
    if not file_path.endswith(".py"):
        msg = f"File {file_path} is not a python file"
        raise ValueError(msg)
    if not os.path.exists(file_path):
        msg = f"File {file_path} not found"
        raise FileNotFoundError(msg)
    with open(file_path, "r") as file:
        code = file.read()
    if checkpointing and not checkpoint_dir:
        msg = "Output directory is required for checkpointing"
        raise ValueError(msg)
    os.makedirs(checkpoint_dir, exist_ok=True)

    if select_only and select_not:
        msg = "Cannot have both select_only and select_not options specified."
        raise ValueError(msg)

    if select_only:
        strategies = {key: STRATEGIES[key] for key in select_only}
    elif select_not:
        strategies = {
            key: STRATEGIES[key] for key in STRATEGIES if key not in select_not
        }
    else:
        strategies = STRATEGIES

    updated_code = code
    for _, (function, description, cleaning_with_subprocess) in strategies.items():
        if cleaning_with_subprocess:
            if not python_env_path:
                raise ValueError(
                    "Python environment path is required for cleaning with subprocess."
                )
            if not updated_code == code:
                with open(file_path, "w") as file:
                    file.write(updated_code)
            if result := function(file_path, python_env_path):
                print(result)
            with open(file_path, "r") as file:
                updated_code = file.read()
        else:
            updated_code = function(updated_code)
        file_name = os.path.basename(file_path)
        print(f"--------> {description} applied to {file_name}")
        if checkpointing:
            make_checkpoint(file_path, updated_code, description, checkpoint_dir)


if __name__ == "__main__":
    path = r"tasks/tests/cleanup_test.py"
    root_dir = os.path.abspath(os.path.join(path, "..", "..", ".."))
    cleanup_file(
        path,
        checkpointing=True,
        checkpoint_dir=get_checkpoint_directory(root_dir),
        python_env_path=get_environment_path_of_tasks(),
    )
    print(f"File cleaned of {path}")