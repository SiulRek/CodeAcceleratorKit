import json
import os
import shutil
import warnings

from tasks.configs.constants import REGISTERED_RUNNERS_JSON, TASKS_ROOT
import tasks.configs.profile_attributes as Attributes
from tasks.management.normalize_path import normalize_path
from tasks.management.task_runner_profile import TaskRunnerProfile

SUPPORT_FILES_DIR = os.path.join(TASKS_ROOT, "tasks", "management", "support_files")


class TaskManager(Attributes.AttributesInitializer):
    """
    Manages the registration and initialization of new task runners.
    """

    @classmethod
    def _register_runner(cls, runner_root, storage_dir, overwrite):
        """
        Registers an runner root and its corresponding storage directory.

        Parameters
        ----------
        runner_root (str)
            The root directory of the runner.
        storage_dir (str)
            The storage directory to register.
        overwrite (bool)
            Whether to overwrite an existing registration.
        """
        if not os.path.exists(REGISTERED_RUNNERS_JSON):
            registered_runners = {}
        else:
            with open(REGISTERED_RUNNERS_JSON, "r", encoding="utf-8") as f:
                registered_runners = json.load(f)
        if runner_root in registered_runners and not overwrite:
            msg = f"Task runner root {runner_root} is already registered."
            msg += " Use the overwrite flag to overwrite the registration."
            raise ValueError(msg)
        os.makedirs(storage_dir, exist_ok=True)
        registered_runners[runner_root] = storage_dir
        with open(REGISTERED_RUNNERS_JSON, "w", encoding="utf-8") as f:
            json.dump(registered_runners, f, indent=4)

    @classmethod
    def _init_runner_attributes(cls, runner_root, storage_dir, python_env, cwd):
        """
        Initializes attributes for the runner based on its root and storage
        directory.

        Parameters
        ----------
        runner_root (str)
            The root directory of the runner.
        storage_dir (str)
            The storage directory.
        python_env (str)
            The Python environment to use.
        cwd (str)
            The current working directory of the runner.

        Returns
        -------
        dict
            A dictionary of initialized attributes.
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
        for attr in Attributes.ProfileAttrNames.__members__:
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

        Parameters
        ----------
        runner_root (str)
            The root directory of the runner.
        """
        profile = TaskRunnerProfile(runner_root)
        created_dirs = []
        for attr in Attributes.ProfileAttrNames.__members__:
            if attr.endswith("_dir"):
                path = getattr(profile, attr)
                os.makedirs(path, exist_ok=True)
                created_dirs.append(path)
        storage_dir = profile.storage_dir
        dirs_in_storage = os.listdir(storage_dir)
        dirs_in_storage = [os.path.join(storage_dir, dir_) for dir_ in dirs_in_storage]
        dirs_in_storage = [dir_ for dir_ in dirs_in_storage if os.path.isdir(dir_)]
        dirs_in_storage = [normalize_path(dir_) for dir_ in dirs_in_storage]
        unknown_dirs = []
        for dir_in_storage in dirs_in_storage:
            for created_dir in created_dirs:
                if dir_in_storage in created_dir or dir_in_storage.endswith("profile"):
                    break
            else:
                unknown_dirs.append(dir_in_storage)

        for unknown_dir in unknown_dirs:
            msg = f"Unknown directory {unknown_dir} from tasks storage."
            warnings.warn(msg)

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

        Parameters
        ----------
        runner_root (str)
            The root directory of the runner.
        python_env (str)
            The Python environment to use.
        storage_dir (str, optional)
            The storage directory. Defaults to "local/task_storage".
        overwrite (bool, optional)
            Whether to overwrite an existing registration. Defaults to False.
        create_dirs (bool, optional)
            Whether to create directories for the runner. Defaults to True.
        cwd (str, optional)
            The current working directory of the runner.

        Returns
        -------
        TaskRunnerProfile
            The runner profile generated from the registration.
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
        profile = TaskRunnerProfile(runner_root, load_attributes_from_storage=False)
        profile.load_attributes_from_dict(attributes)
        profile.save_attributes()
        if create_dirs:
            cls.sync_directories_of(runner_root)
        return profile

    @classmethod
    def get_registered_runners(cls):
        """
        Gets the registered runners.

        Returns
        -------
        list
            A list of registered runner roots.
        """
        with open(REGISTERED_RUNNERS_JSON, "r", encoding="utf-8") as f:
            registered_runners = json.load(f)
        return registered_runners.keys()

    @classmethod
    def is_runner_registered(cls, runner_root, raise_error=False):
        """
        Checks if a runner is registered.

        Parameters
        ----------
        runner_root (str)
            The root directory of the runner.
        raise_error (bool, optional)
            Whether to raise an error if the

        Returns
        -------
        bool
            True if the runner is registered, False otherwise.
        """
        runner_root = normalize_path(runner_root)
        with open(REGISTERED_RUNNERS_JSON, "r", encoding="utf-8") as f:
            registered_runners = json.load(f)
        if runner_root in registered_runners:
            return True
        if raise_error:
            msg = f"Runner root {runner_root} is not registered."
            raise ValueError(msg)
        return False

    @classmethod
    def login_runner(cls, runner_root, update_dirs=True):
        """
        Logs in to an runner and initializes its profile.

        Parameters
        ----------
        runner_root (str)
            The root directory of the runner.
        update_dirs (bool, optional)
            Whether to update the directories of the runner profile. Defaults
            to True.

        Returns
        -------
        TaskRunnerProfile
            The runner profile after logging in.
        """
        runner_root = normalize_path(runner_root)
        cls.is_runner_registered(runner_root, raise_error=True)
        if update_dirs:
            cls.sync_directories_of(runner_root)
        profile = TaskRunnerProfile(runner_root)
        return profile

    @classmethod
    def update_runner(cls, runner_root):
        """
        Updates the runner profile with the latest attributes. The update
        depends on UPDATE_MAPPING in profile_attributes.py.

        Parameters
        ----------
        runner_root (str)
            The root directory of the runner.
        """
        cls.is_runner_registered(runner_root, raise_error=True)

        profile = TaskRunnerProfile(runner_root)
        modules_info_file = os.path.join(profile.profile_dir, "modules_info.json")
        if os.path.exists(modules_info_file):
            os.remove(modules_info_file)  # Is going to be regenereted in the next step
        reinit_attrs = cls._init_runner_attributes(
            runner_root,
            profile.storage_dir,
            profile.runner_python_env,
            profile.cwd,
        )
        profile.update_attributes(reinit_attrs)
        profile.save_attributes()
        TaskManager.sync_directories_of(runner_root)

    @classmethod
    def update_registered_runners(cls):
        """
        Updates the attributes of all registered runners.
        """
        with open(REGISTERED_RUNNERS_JSON, "r", encoding="utf-8") as f:
            registered_runners = json.load(f)
        for runner_root in registered_runners:
            runner_name = os.path.basename(runner_root)
            print(f"Updating runner {runner_name}...")
            cls.update_runner(runner_root)
            print(f"Runner {runner_name} updated.")
            print()

    @classmethod
    def delete_runner(cls, runner_root):
        """
        Deletes a runner registration.

        Parameters
        ----------
        runner_root (str)
            The root directory of the runner.
        """
        cls.is_runner_registered(runner_root, raise_error=True)
        with open(REGISTERED_RUNNERS_JSON, "r", encoding="utf-8") as f:
            registered_runners = json.load(f)
        if runner_root not in registered_runners:
            msg = f"Runner root {runner_root} is not registered."
            raise ValueError(msg)
        storage_dir = registered_runners[runner_root]
        if os.path.exists(storage_dir):
            shutil.rmtree(storage_dir)
        del registered_runners[runner_root]
        with open(REGISTERED_RUNNERS_JSON, "w", encoding="utf-8") as f:
            json.dump(registered_runners, f, indent=4)

    @classmethod
    def copy_costumizations_files(
        cls, source_runner_dir, dest_runner_dir, overwrite=False
    ):
        """
        Copies costumizations files from the source runner to the destination
        runner.

        Parameters
        ----------
        source_runner_dir (str)
            The source runner directory.
        dest_runner_dir (str)
            The destination runner directory.
        overwrite (bool, optional)
            Whether to overwrite existing files.
        """
        if not cls.is_runner_registered(source_runner_dir):
            msg = f"Source runner {source_runner_dir} is not registered."
            raise ValueError(msg)
        if not cls.is_runner_registered(dest_runner_dir):
            msg = f"Destination runner {dest_runner_dir} is not registered."
            raise ValueError(msg)

        source_profile = TaskRunnerProfile(source_runner_dir)
        dest_profile = TaskRunnerProfile(dest_runner_dir)
        source_costumizations_dir = source_profile.costumizations_dir
        dest_costumizations_dir = dest_profile.costumizations_dir

        for root, _, files in os.walk(source_costumizations_dir):
            if "__pycache__" in root:
                continue
            for file in files:
                file_abs_path = os.path.join(root, file)
                file_rel_path = os.path.relpath(
                    file_abs_path, source_costumizations_dir
                )
                dest_file = os.path.join(dest_costumizations_dir, file_rel_path)
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                if os.path.exists(dest_file):
                    if not overwrite:
                        msg = f"File {dest_file} already exists, skipping."
                        warnings.warn(msg)
                        continue
                    msg = f"Overwriting file {dest_file}."
                    warnings.warn(msg)
                shutil.copy2(file_abs_path, dest_file)
                with open(dest_file, "r+", encoding="utf-8") as f:
                    content = f.read()
                    source_runner_dir = normalize_path(source_runner_dir)
                    dest_runner_dir = normalize_path(dest_runner_dir)
                    content = content.replace(source_runner_dir, dest_runner_dir)
                    f.seek(0)
                    f.write(content)
                    f.truncate()

    @classmethod
    def load_support_files_to(cls, runner_root):
        """
        Loads support files to the runner.

        Parameters
        ----------
        runner_root (str)
            The root directory of the runner.
        """
        profile = TaskRunnerProfile(runner_root)
        cheatsheet = os.path.join(SUPPORT_FILES_DIR, "CHEATSHEET.md")
        template_1 = os.path.join(SUPPORT_FILES_DIR, "template_1.py")
        template_2 = os.path.join(SUPPORT_FILES_DIR, "template_2.py")
        template_3 = os.path.join(
            SUPPORT_FILES_DIR, "costum_function_template", "template_3.py"
        )
        costum_function_example = os.path.join(
            SUPPORT_FILES_DIR, "costum_function_template", "costum_function_example.py"
        )
        template_4 = os.path.join(
            SUPPORT_FILES_DIR, "fill_text_template", "template_4.txt"
        )

        load_mapping = [
            # (source_file, dest_dir, subdir_to_create)
            (cheatsheet, profile.storage_dir, None),
            (template_1, profile.meta_macros_dir, None),
            (template_2, profile.meta_macros_with_args_dir, None),
            (template_3, profile.costum_functions_dir, "costum_function_template"),
            (
                costum_function_example,
                profile.costum_functions_dir,
                "costum_function_template",
            ),
            (template_4, profile.fill_text_dir, "fill_text_template"),
        ]

        for source_file, dest_dir, subdir in load_mapping:
            if subdir is not None:
                dest_dir = os.path.join(dest_dir, subdir)
                os.makedirs(dest_dir, exist_ok=True)
            dest_file = os.path.join(dest_dir, os.path.basename(source_file))
            shutil.copy2(source_file, dest_file)
