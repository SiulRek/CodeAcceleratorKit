import json
import os
import warnings

from tasks.configs.constants import REGISTERED_RUNNERS_JSON
import tasks.configs.session_attributes as Names
from tasks.management.normalize_path import normalize_path
from tasks.management.task_session import TaskSession


class TaskManager:
    """Manages the registration and initialization of new task runners."""

    @classmethod
    def _register_runner(cls, runner_root, storage_dir, overwrite):
        """
        Registers an runner root and its corresponding storage directory.

        Args:
            - runner_root (str): The root directory of the runner.
            - storage_dir (str): The storage directory to register.
            - overwrite (bool): Whether to overwrite anexistingregistration.
        """
        if not os.path.exists(REGISTERED_RUNNERS_JSON):
            registered_variables = {}
        else:
            with open(REGISTERED_RUNNERS_JSON, "r", encoding="utf-8") as f:
                registered_variables = json.load(f)
        if runner_root in registered_variables and not overwrite:
            msg = f"Task runner root {runner_root} is already registered."
            msg += " Use the overwrite flag to overwrite the registration."
            raise ValueError(msg)
        os.makedirs(storage_dir, exist_ok=True)
        registered_variables[runner_root] = storage_dir
        with open(REGISTERED_RUNNERS_JSON, "w", encoding="utf-8") as f:
            json.dump(registered_variables, f, indent=4)

    @classmethod
    def _init_runner_attributes(cls, runner_root, storage_dir, python_env, cwd):
        """
        Initializes attributes for the runner based on its root and storage
        directory.

        Args:
            - runner_root (str): The root directory of the runner.
            - storage_dir (str): The storage directory.
            - python_env (str): The Python environment to use.
            - cwd (str): The current working directory of the runner.

        Returns:
            - dict: A dictionary of initialized attributes.
        """
        attributes = {}

        python_env = normalize_path(python_env)
        if cwd is None:
            cwd = runner_root
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
                attributes[attr] = init_func(runner_root, storage_dir)
        return attributes

    @classmethod
    def sync_directories_to(cls, runner_root):
        """
        Synchronizes the directories of a runner to the storage directory.

        Args:
            - runner_root (str): The root directory of the runner.
        """
        session = TaskSession(runner_root)
        created_dirs = []
        for attr in Names.SessionAttrNames.__members__.keys():
            if attr.endswith("_dir"):
                path = getattr(session, attr)
                os.makedirs(path, exist_ok=True)
                created_dirs.append(path)
        storage_dir = session.storage_dir
        dirs_in_storage = os.listdir(storage_dir)
        dirs_in_storage = [os.path.join(storage_dir, dir_) for dir_ in dirs_in_storage]
        dirs_in_storage = [
            dir_ for dir_ in dirs_in_storage
            if os.path.isdir(dir_)
        ]
        dirs_in_storage = [normalize_path(dir_) for dir_ in dirs_in_storage]
        unknown_dirs = []
        for dir_in_storage in dirs_in_storage:
            for created_dir in created_dirs:
                if dir_in_storage in created_dir or dir_in_storage.endswith('configs'):
                    break
            else:
                unknown_dirs.append(dir_in_storage)

        for unknown_dir in unknown_dirs:
            for unknown_dir in unknown_dirs:
                warnings.warn(f"Unknown directory {unknown_dir} from task storage.")

    @classmethod
    def register_runner(
        cls,
        runner_root,
        python_env,
        storage_dir="local/task_storage",
        overwrite=False,
        create_dirs=True,
        cwd=None,
    ):
        """
        Registers an runner and initializes its attributes.

        Args:
            - runner_root (str): The root directory of the runner.
            - python_env (str): The Python environment to use.
            - storage_dir (str, optional): The storage directory.
                Defaultsto"local/task_storage".
            - overwrite (bool, optional): Whether to overwrite
                anexistingregistration. Defaults to False.
            - create_dirs (bool, optional): Whether to create
                directoriesforthe runner. Defaults to True.
            - cwd (str, optional): The current working directory
                oftherunner.

        Returns:
            - TaskSession: The runner session generated fromtheregistration.
        """
        runner_root = normalize_path(runner_root)
        storage_dir = normalize_path(storage_dir)
        if not storage_dir.startswith(runner_root):
            storage_dir = os.path.join(runner_root, storage_dir)
        cls._register_runner(runner_root, storage_dir, overwrite=overwrite)
        attributes = cls._init_runner_attributes(
            runner_root, storage_dir, python_env, cwd
        )
        session = TaskSession(runner_root, load_attributes_from_storage=False)
        session.load_attributes_from_dict(attributes)
        session.save_attributes()
        if create_dirs:
            cls.sync_directories_to(runner_root)
        return session

    @classmethod
    def login_runner(cls, runner_root, update_dirs=True):
        """
        Logs in to an runner and initializes its session.

        Args:
            - runner_root (str): The root directory of the runner.
            - update_dirs (bool, optional): Whether to update
                thedirectoriesof the runner session. Defaults to True.

        Returns:
            - TaskSession: The runner session after logging in.
        """
        runner_root = normalize_path(runner_root)
        if update_dirs:
            cls.sync_directories_to(runner_root)
        session = TaskSession(runner_root)
        return session
