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
    def _register_executor(cls, executor_root, storage_dir, overwrite):
        """
        Registers an executor root and its corresponding storage directory.

        Args:
            - executor_root (str): The root directory of the executor.
            - storage_dir (str): The storage directory to register.
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
        os.makedirs(storage_dir, exist_ok=True)
        registered_variables[executor_root] = storage_dir
        with open(REGISTERED_EXECUTORS_JSON, "w", encoding="utf-8") as f:
            json.dump(registered_variables, f, indent=4)

    @classmethod
    def _init_executor_attributes(cls, executor_root, storage_dir, python_env, cwd):
        """
        Initializes attributes for the executor based on its root and storage
        directory.

        Args:
            - executor_root (str): The root directory of the executor.
            - storage_dir (str): The storage directory.
            - python_env (str): The Python environment to use.
            - cwd (str): The current working directory of the executor.

        Returns:
            - dict: A dictionary of initialized attributes.
        """
        attributes = {}

        # Add cwd and python_env attributes
        python_env = normalize_path(python_env)
        if cwd is None:
            cwd = executor_root
        if not os.path.exists(cwd):
            raise NotADirectoryError(f"Current working directory {cwd} does not exist.")
        if not os.path.exists(python_env):
            raise NotADirectoryError(f"Python environment {python_env} does not exist.")
        attributes[Names.ContextAttrNames.cwd.value] = normalize_path(cwd)
        attributes[Names.ContextAttrNames.python_env.value] = python_env

        # Add other attributes
        for key in Names.ContextAttrNames.__members__.keys():
            init_func = getattr(cls, f"_initialize_{key}")
            attributes[key] = init_func(executor_root, storage_dir)
        return attributes

    @classmethod
    def sync_directories(cls, context):
        """
        Synchronizes the directories of the executor context with the directories
        in the task storage.

        Args:
            - context (ExecutorContext): The executor context to synchronize.
        """
        created_dirs = []
        for key in Names.ContextAttrNames.__members__.keys():
            if key.endswith("_DIR"):
                path = getattr(context, key)
                os.makedirs(path, exist_ok=True)
                created_dirs.append(path)
        storage_dir = context.storage_dir
        dirs_in_storage = os.listdir(storage_dir)
        dirs_in_storage = [
            os.path.join(storage_dir, dir_) for dir_ in dirs_in_storage if os.path.isdir(dir_)
        ]
        dirs_in_storage = [normalize_path(dir_) for dir_ in dirs_in_storage]
        unknown_dirs = []
        for dir_in_storage in dirs_in_storage:
            for created_dir in created_dirs:
                if dir_in_storage in created_dir:
                    break
            else:
                unknown_dirs.append(dir_in_storage)

        for unknown_dir in unknown_dirs:
            for unknown_dir in unknown_dirs:
                warnings.warn(f"Unknown directory {unknown_dir} from task storage.")
                
    @classmethod
    def register_executor(cls, executor_root, python_env, storage_dir="local/task_storage", overwrite=False, create_dirs=True, cwd=None):
        """
        Registers an executor: records in registered_executors.json, initializes executor 
        attributes creates directories, and saves the attributes to the variable JSON file. 
        Returns the executor variable of the registration.

        Args:
            - executor_root (str): The root directory of the executor.
            - python_env (str): The Python environment to use.
            - storage_dir (str, optional): The storage directory. Defaults to "local/task_storage".
            - overwrite (bool, optional): Whether to overwrite an existing
            - create_dirs (bool, optional): Whether to create directories for the executor.
            - cwd (str, optional): The current working directory of the executor.

        Returns:
            - ExecutorVariable: The executor variable generated from the registration.
        """
        executor_root = normalize_path(executor_root)
        storage_dir = normalize_path(storage_dir)
        if not storage_dir.startswith(executor_root):
            storage_dir = os.path.join(executor_root, storage_dir)
        cls._register_executor(executor_root, storage_dir, overwrite=overwrite)
        attributes = cls._init_executor_attributes(executor_root, storage_dir, python_env, cwd)
        variable = ExecutorContext(executor_root, load_attributes_from_json=False)
        variable.load_attributes_from_dict(attributes)
        variable.save_attributes()
        if create_dirs:
            cls.sync_directories(variable)
        return variable

    @classmethod
    def login_executor(cls, executor_root, update_dirs=True):
        """
        Logs in to an executor: loads the executor attributes from the variable JSON file,
        creates directories, and returns the executor context.

        Args:
            - executor_root (str): The root directory of the executor.
            - update_dirs (bool, optional): Whether to update the directories of the executor context.
        
        Returns:
            
        """
        executor_root = normalize_path(executor_root)
        context = ExecutorContext(executor_root)
        if update_dirs:
            cls.sync_directories(context)
        return context