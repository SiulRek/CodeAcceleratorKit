import json
import os
import warnings

from tasks.constants.configs import REGISTERED_VARIABLES_JSON
from tasks.variables.executor_variable import ExecutorVariable
from tasks.variables.normalize_path import normalize_path
from tasks.variables.variable_names import VariableNames


class ExecutorHandler:
    """Handles the registration and initialization of executor variables."""

    @classmethod
    def _register(cls, executor_root, room_dir, overwrite):
        """
        Registers an executor root and its corresponding room directory.

        Args:
            - executor_root (str): The root directory of the executor.
            - room_dir (str): The room directory to register.
            - overwrite (bool): Whether to overwrite anexistingregistration.

        Raises:
            - ValueError: If the executor root is already registered.
        """
        if not os.path.exists(REGISTERED_VARIABLES_JSON):
            with open(REGISTERED_VARIABLES_JSON, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)
                registered_variables = {}
        else:
            with open(REGISTERED_VARIABLES_JSON, "r", encoding="utf-8") as f:
                registered_variables = json.load(f)
        if executor_root in registered_variables and not overwrite:
            msg = f"Task executor root {executor_root} is already registered."
            msg += " Use the overwrite flag to overwrite the registration."
            raise ValueError(msg)
        registered_variables[executor_root] = room_dir
        with open(REGISTERED_VARIABLES_JSON, "w", encoding="utf-8") as f:
            json.dump(registered_variables, f, indent=4)

    @classmethod
    def _initialize_attributes(cls, executor_root, room_dir):
        """
        Initializes attributes for the executor based on its root and room
        directory.

        Args:
            - executor_root (str): The root directory of the executor.
            - room_dir (str): The room directory.

        Returns:
            - dict: A dictionary of initialized attributes.
        """
        attributes = {}
        for key in VariableNames:
            init_func = getattr(cls, f"_initialize_{key}")
            attributes[key] = init_func(executor_root, room_dir)
        return attributes

    @classmethod
    def register(cls, executor_root, room_dir="local/task_room", overwrite=False):
        """
        Registers an executor and initializes attributes.

        Args:
            - executor_root (str): The root directory of the executor.
            - room_dir (str, optional): The room directory. Defaults to "local/task_room".
            - overwrite (bool, optional): Whether to overwrite an existing
        """
        executor_root = normalize_path(executor_root)
        room_dir = normalize_path(room_dir)
        if not room_dir.startswith(executor_root):
            room_dir = os.path.join(executor_root, room_dir)
        cls._register(executor_root, room_dir, overwrite=overwrite)
        attributes = cls._initialize_attributes(executor_root, room_dir)
        variable = ExecutorVariable(executor_root, load_attributes_from_json=False)
        variable.load_attributes_from_dict(attributes)
        variable.save_attributes()

    def create_directories(self, variable):
        """
        Creates directories for the executor.

        Args:
            - variable (ExecutorVariable): The executor variable.
        """
        created_dirs = []
        for key in VariableNames:
            if key.name.endswith("_DIR"):
                path = getattr(variable, key)
                os.makedirs(path, exist_ok=True)
                created_dirs.append(path)
        room_dir = variable.room_dir
        dirs_in_room = os.listdir(room_dir)
        dirs_in_room = [
            os.path.join(room_dir, dir_) for dir_ in dirs_in_room if os.path.isdir(dir_)
        ]
        dirs_in_room = [normalize_path(dir_) for dir_ in dirs_in_room]
        unknown_dirs = []
        for dir_in_room in dirs_in_room:
            for created_dir in created_dirs:
                if dir_in_room in created_dir:
                    break
            else:
                unknown_dirs.append(dir_in_room)

        for unknown_dir in unknown_dirs:
            for unknown_dir in unknown_dirs:
                warnings.warn(f"Unknown directory found: {unknown_dir}")
