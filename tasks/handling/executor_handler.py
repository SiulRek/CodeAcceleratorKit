import json
import os
import warnings

from tasks.constants.configs import REGISTERED_EXECUTORS_JSON
from tasks.handling.normalize_path import normalize_path
import tasks.constants.session_attributes as Names
from tasks.handling.task_session import TaskSession


class ExecutorHandler:
    """Handles the registration and initialization of new task executors."""

    @classmethod
    def _register_executor(cls, executor_root, storage_dir, overwrite):
        """
        Registers an executor root and its corresponding storage directory.

        Args:
            - executor_root (str): The root directory of the executor.
            - storage_dir (str): The storage directory to register.
            - overwrite (bool): Whether to overwrite an existing
                registration.
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

        python_env = normalize_path(python_env)
        if cwd is None:
            cwd = executor_root
        if not os.path.exists(cwd):
            msg = f"Current working directory {cwd} does not exist."
            raise NotADirectoryError(msg)
        if not os.path.exists(python_env):
            msg = f"Python environment {python_env} does not exist."
            raise NotADirectoryError(msg)

        for attr in Names.SessionAttrNames.__members__.keys():
            if attr in "cwd":
                attributes[attr] = cwd
            elif attr in "python_env":
                attributes[attr] = python_env
            else:
                init_func = getattr(cls, f"_initialize_{attr}")
                attributes[attr] = init_func(executor_root, storage_dir)
        return attributes

    @classmethod
    def sync_directories(cls, session):
        """
        Synchronizes the directories of the executor session with the
        directories in the task storage.

        Args:
            - session (TaskSession): The executor session to synchronize.
        """
        created_dirs = []
        for attr in Names.SessionAttrNames.__members__.keys():
            if attr.endswith("_dir"):
                path = getattr(session, attr)
                os.makedirs(path, exist_ok=True)
                created_dirs.append(path)
        storage_dir = session.storage_dir
        dirs_in_storage = os.listdir(storage_dir)
        dirs_in_storage = [
            os.path.join(storage_dir, dir_)
            for dir_ in dirs_in_storage
            if os.path.isdir(dir_)
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
    def register_executor(
        cls,
        executor_root,
        python_env,
        storage_dir="local/task_storage",
        overwrite=False,
        create_dirs=True,
        cwd=None,
    ):
        """
        Registers an executor and initializes its attributes.

        Args:
            - executor_root (str): The root directory of the executor.
            - python_env (str): The Python environment to use.
            - storage_dir (str, optional): The storage directory. Defaults
                to "local/task_storage".
            - overwrite (bool, optional): Whether to overwrite an existing
                registration. Defaults to False.
            - create_dirs (bool, optional): Whether to create directories
                for the executor. Defaults to True.
            - cwd (str, optional): The current working directory of the
                executor.

        Returns:
            - TaskSession: The executor session generated from the
                registration.
        """
        executor_root = normalize_path(executor_root)
        storage_dir = normalize_path(storage_dir)
        if not storage_dir.startswith(executor_root):
            storage_dir = os.path.join(executor_root, storage_dir)
        cls._register_executor(executor_root, storage_dir, overwrite=overwrite)
        attributes = cls._init_executor_attributes(
            executor_root, storage_dir, python_env, cwd
        )
        variable = TaskSession(executor_root, load_attributes_from_storage=False)
        variable.load_attributes_from_dict(attributes)
        variable.save_attributes()
        if create_dirs:
            cls.sync_directories(variable)
        return variable

    @classmethod
    def login_executor(cls, executor_root, update_dirs=True):
        """
        Logs in to an executor and initializes its session.

        Args:
            - executor_root (str): The root directory of the executor.
            - update_dirs (bool, optional): Whether to update the
                directories of the executor session. Defaults to True.

        Returns:
            - TaskSession: The executor session after logging in.
        """
        executor_root = normalize_path(executor_root)
        session = TaskSession(executor_root)
        if update_dirs:
            cls.sync_directories(session)
        return session
