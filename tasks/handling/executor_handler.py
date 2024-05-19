import json
import os
import warnings

from tasks.constants.configs import REGISTERED_EXECUTORS_JSON
from tasks.handling.executor_context import ExecutorContext
from tasks.handling.normalize_path import normalize_path
import tasks.handling.context_attribute_names as Names

class ExecutorHandler:
    """Handles the registration and initialization of new task executors."""

    @classmethod
    def _register_executor(cls, executor_root, room_dir, overwrite):
        """
        Registers an executor root and its corresponding room directory.

        Args:
            - executor_root (str): The root directory of the executor.
            - room_dir (str): The room directory to register.
            - overwrite (bool): Whether to overwrite anexistingregistration.
        """
        if not os.path.exists(REGISTERED_EXECUTORS_JSON):
                registered_variables = {}
        else:
            with open(REGISTERED_EXECUTORS_JSON, "r", encoding="utf-8") as f:
                registered_variables = json.load(f)
        if executor_root in registered_variables and not overwrite:
            msg = f"Task executor root {executor_root} is already registered."
            msg += " Use the overwrite flag to overwrite the registration."
            raise ValueError(msg)
        os.makedirs(room_dir, exist_ok=True)
        registered_variables[executor_root] = room_dir
        with open(REGISTERED_EXECUTORS_JSON, "w", encoding="utf-8") as f:
            json.dump(registered_variables, f, indent=4)

    @classmethod
    def _init_executor_attributes(cls, executor_root, room_dir):
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
        for key in Names.ContextAttrNames.__members__.keys():
            init_func = getattr(cls, f"_initialize_{key}")
            attributes[key] = init_func(executor_root, room_dir)
        return attributes

    @classmethod
    def register_executor(cls, executor_root, room_dir="local/task_room", overwrite=False, create_dirs=True):
        """
        Registers an executor: records in registered_executors.json, initializes executor 
        attributes creates directories, and saves the attributes to the variable JSON file. 
        Returns the executor variable of the registration.

        Args:
            - executor_root (str): The root directory of the executor.
            - room_dir (str, optional): The room directory. Defaults to "local/task_room".
            - overwrite (bool, optional): Whether to overwrite an existing
            - create_dirs (bool, optional): Whether to create directories for the executor.

        Returns:
            - ExecutorVariable: The executor variable generated from the registration.
        """
        executor_root = normalize_path(executor_root)
        room_dir = normalize_path(room_dir)
        if not room_dir.startswith(executor_root):
            room_dir = os.path.join(executor_root, room_dir)
        cls._register_executor(executor_root, room_dir, overwrite=overwrite)
        attributes = cls._init_executor_attributes(executor_root, room_dir)
        variable = ExecutorContext(executor_root, load_attributes_from_json=False)
        variable.load_attributes_from_dict(attributes)
        variable.save_attributes()
        if create_dirs:
            cls.create_directories(variable)
        return variable

    @classmethod
    def create_directories(cls, variable):
        """
        Creates directories for the executor.

        Args:
            - variable (ExecutorVariable): The executor variable.
        """
        created_dirs = []
        for key in Names.ContextAttrNames.__members__.keys():
            if key.endswith("_DIR"):
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
                warnings.warn(f"Unknown directory {unknown_dir} from task room.")
                