import json
import os
import shutil
import warnings

from tasks.configs.constants import REGISTERED_RUNNERS_JSON
import tasks.configs.session_attributes as Attributes
from tasks.tasks.management.normalize_path import normalize_path
from tasks.tasks.management.task_session import TaskSession


class TaskManager(Attributes.AttributesInitializer):
    """Manages the registration and initialization of new task runners."""

    @classmethod
    def _register_runner(cls, runner_root, storage_dir, overwrite):
        """
        Registers an runner root and its corresponding storage directory.

        Args:
            - runner_root (str): The root directory of the runner.
            - storage_dir (str): The storage directory to register.
            - overwrite (bool): Whether to overwrite an existing
                registration.
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

        primary_attrs = {
            "runner_root": runner_root,
            "storage_dir": storage_dir,
            "cwd": cwd,
            "runner_python_env": python_env,
        }
        for attr in Attributes.SessionAttrNames.__members__.keys():
            if attr in "cwd":
                attributes[attr] = cwd if cwd is not None else runner_root
            elif attr in "runner_python_env":
                attributes[attr] = python_env
            else:
                init_func = getattr(cls, f"_initialize_{attr}")
                attributes[attr] = init_func(primary_attrs)
        return attributes

    @classmethod
    def sync_directories_of(cls, runner_root):
        """
        Synchronizes the directories of a runner to the storage directory.

        Args:
            - runner_root (str): The root directory of the runner.
        """
        session = TaskSession(runner_root)
        created_dirs = []
        for attr in Attributes.SessionAttrNames.__members__.keys():
            if attr.endswith("_dir"):
                path = getattr(session, attr)
                os.makedirs(path, exist_ok=True)
                created_dirs.append(path)
        storage_dir = session.storage_dir
        dirs_in_storage = os.listdir(storage_dir)
        dirs_in_storage = [os.path.join(storage_dir, dir_) for dir_ in dirs_in_storage]
        dirs_in_storage = [dir_ for dir_ in dirs_in_storage if os.path.isdir(dir_)]
        dirs_in_storage = [normalize_path(dir_) for dir_ in dirs_in_storage]
        unknown_dirs = []
        for dir_in_storage in dirs_in_storage:
            for created_dir in created_dirs:
                if dir_in_storage in created_dir or dir_in_storage.endswith("configs"):
                    break
            else:
                unknown_dirs.append(dir_in_storage)

        for unknown_dir in unknown_dirs:
            for unknown_dir in unknown_dirs:
                warnings.warn(f"Unknown directory {unknown_dir} from tasks storage.")

    @classmethod
    def register_runner(
        cls,
        runner_root,
        python_env,
        storage_dir="local/tasks_storage",
        overwrite=False,
        create_dirs=True,
        cwd=None,
    ):
        """
        Registers an runner and initializes its attributes.

        Args:
            - runner_root (str): The root directory of the runner.
            - python_env (str): The Python environment to use.
            - storage_dir (str, optional): The storage directory. Defaults
                to "local/task_storage".
            - overwrite (bool, optional): Whether to overwrite an existing
                registration. Defaults to False.
            - create_dirs (bool, optional): Whether to create directories
                for the runner. Defaults to True.
            - cwd (str, optional): The current working directory of the
                runner.

        Returns:
            - TaskSession: The runner session generated from the
                registration.
        """
        if not os.path.exists(runner_root):
            msg = f"Runner root {runner_root} does not exist."
            raise NotADirectoryError(msg)
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
            cls.sync_directories_of(runner_root)
        return session

    @classmethod
    def login_runner(cls, runner_root, update_dirs=True):
        """
        Logs in to an runner and initializes its session.

        Args:
            - runner_root (str): The root directory of the runner.
            - update_dirs (bool, optional): Whether to update the
                directories of the runner session. Defaults to True.

        Returns:
            - TaskSession: The runner session after logging in.
        """
        runner_root = normalize_path(runner_root)
        if update_dirs:
            cls.sync_directories_of(runner_root)
        session = TaskSession(runner_root)
        return session

    @classmethod
    def delete_runner(cls, runner_root):
        """
        Deletes a runner registration.

        Args:
            - runner_root (str): The root directory of the runner.
        """
        runner_root = normalize_path(runner_root)
        if not os.path.exists(runner_root):
            msg = f"Runner root {runner_root} does not exist."
            raise NotADirectoryError(msg)
        with open(REGISTERED_RUNNERS_JSON, "r", encoding="utf-8") as f:
            registered_variables = json.load(f)
        if runner_root not in registered_variables:
            msg = f"Runner root {runner_root} is not registered."
            raise ValueError(msg)
        storage_dir = registered_variables[runner_root]
        shutil.rmtree(storage_dir)
        del registered_variables[runner_root]
        with open(REGISTERED_RUNNERS_JSON, "w", encoding="utf-8") as f:
            json.dump(registered_variables, f, indent=4)
            
    def copy_data_files(self, source_runner_dir, dest_runner_dir):
        """
        Copies data files from the source runner to the destination runner.

        Args:
            - source_runner_dir (str): The source runner directory.
            - dest_runner_dir (str): The destination runner directory.
        """
        source_session = TaskSession(source_runner_dir)
        dest_session = TaskSession(dest_runner_dir)
        source_data_dir = source_session.data_dir

        for attr in Attributes.SessionAttrNames.__members__.keys():
            if attr.endswith("_dir"):
                source_dir = getattr(source_session, attr)
                dest_dir = getattr(dest_session, attr)
                if source_dir.startswith(source_data_dir):
                    for name in os.listdir(source_dir):
                        source_path = os.path.join(source_dir, name)
                        if os.path.isfile(source_path):
                            dest_path = os.path.join(dest_dir, name)
                            shutil.copy(source_path, dest_path)


if __name__ == "__main__":
    TaskManager.register_runner(
        runner_root=r"/home/krakerlu/github/CodeAcceleratorKit",
        python_env=r"/home/krakerlu/github/CodeAcceleratorKit/venv",
        overwrite=True,
    )