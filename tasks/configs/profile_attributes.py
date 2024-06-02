from enum import Enum
import json
import os

from tasks.configs.constants import (
    PROFILE_SUBFOLDER,
    TASKS_PYTHON_ENV,
    TASKS_CACHE,
    MAX_BACKUPS,
)
from tasks.management.normalize_path import normalize_path
from tasks.utils.shared.execute_python_module import execute_python_module
import tasks.utils.shared.retrieve_modules as retrieve_modules


class ProfileAttrNames(Enum):
    """
    Enumerated constants that define attribute names for a profile's
    configuration file. The attribute name is associated with a unique
    identifier. The associated file is where the value of the attribute might be
    found.
    """

    cwd = (1, "configs.json")
    runner_python_env = (2, "configs.json")
    tasks_cache = (3, "configs.json")
    runners_cache = (4, "configs.json")
    data_dir = (5, "configs.json")
    execution_tracks_dir = (6, "configs.json")
    costumizations_dir = (7, "configs.json")
    fill_text_dir = (8, "configs.json")
    meta_macros_dir = (9, "configs.json")
    meta_macros_with_args_dir = (10, "configs.json")
    costum_functions_dir = (11, "configs.json")
    output_dir = (12, "configs.json")
    log_dir = (13, "configs.json")
    backup_dir = (14, "configs.json")
    checkpoint_dir = (15, "configs.json")
    chats_dir = (16, "configs.json")
    tasks_python_env = (17, "configs.json")
    max_backups = (18, "configs.json")
    modules_info = (19, "modules_info.json")
    directory_runner_config = (20, "directory_runner_template.json")


UPDATE_MAPPING = {
    # New Name: Old Name
    # Old Name None is accepted
    "cwd": "cwd",
    "runner_python_env": "runner_python_env",
    "tasks_cache": "tasks_cache",
    "runners_cache": "runners_cache",
    "data_dir": "data_dir",
    "execution_tracks_dir": "execution_tracks_dir",
    "costumizations_dir": "costumizations_dir",
    "fill_text_dir": "fill_text_dir",
    "costum_functions_dir": "costum_functions_dir",
    "meta_macros_dir": "meta_macros_dir",
    "meta_macros_with_args_dir": "meta_macros_with_args_dir",
    "output_dir": "output_dir",
    "log_dir": "log_dir",
    "backup_dir": "backup_dir",
    "checkpoint_dir": "checkpoint_dir",
    "chats_dir": "chats_dir",
    "tasks_python_env": "tasks_python_env",
    "max_backups": "max_backups",
    "modules_info": None,  # Forces update of modules_info
    "directory_runner_config": "directory_runner_config",
}


class AttributesInitializer:
    """ Class that initializes various profile attributes. It is used during
    registration of new task runners with the TaskManager class. """

    @classmethod
    def _initialize_tasks_cache(cls, _):
        """ Initializes the tasks_cache directory path. """
        dir_ = normalize_path(TASKS_CACHE)
        return dir_

    @classmethod
    def _initialize_runners_cache(cls, primary_attrs):
        """ Initializes the runners_cache directory path. """
        dir_ = normalize_path(primary_attrs.get("storage_dir"))
        dir_ = os.path.join(dir_, "__taskscache__")
        return dir_

    @classmethod
    def _initialize_data_dir(cls, primary_attrs):
        """ Initializes the data directory path based on the storage_dir
        inprimaryattributes. """
        storage_dir = primary_attrs.get("storage_dir")
        dir_ = os.path.join(storage_dir, "data")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_execution_tracks_dir(cls, primary_attrs):
        """ Initializes the execution track directory path based on the storage_dir
        inprimaryattributes. """
        data_dir = cls._initialize_data_dir(primary_attrs)
        dir_ = os.path.join(data_dir, "execution_tracks")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_costumizations_dir(cls, primary_attrs):
        """ Initializes the templates directory path based on the storage_dir
        inprimaryattributes. """
        storage_dir = primary_attrs.get("storage_dir")
        dir_ = os.path.join(storage_dir, "costumizations")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_fill_text_dir(cls, primary_attrs):
        """ Initializes the fill text directory path based on the
        templatesdirectory. """
        templates_dir = cls._initialize_costumizations_dir(primary_attrs)
        dir_ = os.path.join(templates_dir, "fill_texts")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_meta_macros_dir(cls, primary_attrs):
        """ Initializes the prompt templates directory path based on the templates
        directory. """
        templates_dir = cls._initialize_costumizations_dir(primary_attrs)
        dir_ = os.path.join(templates_dir, "meta_macros")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_meta_macros_with_args_dir(cls, primary_attrs):
        """ Initializes the templates with arguments directory path based on the
        templates directory. """
        templates_dir = cls._initialize_costumizations_dir(primary_attrs)
        dir_ = os.path.join(templates_dir, "meta_macros_with_args")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_costum_functions_dir(cls, primary_attrs):
        """ Initializes the costum functions directory path based on the
        templatesdirectory. """
        templates_dir = cls._initialize_costumizations_dir(primary_attrs)
        dir_ = os.path.join(templates_dir, "functions")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_output_dir(cls, primary_attrs):
        """ Initializes the output directory path based on the storage_dir
        inprimaryattributes. """
        storage_dir = primary_attrs.get("storage_dir")
        dir_ = os.path.join(storage_dir, "outputs")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_log_dir(cls, primary_attrs):
        """ Initializes the log directory path based on the output directory. """
        output_dir = cls._initialize_output_dir(primary_attrs)
        dir_ = os.path.join(output_dir, "logs")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_backup_dir(cls, primary_attrs):
        """ Initializes the backup directory path based on the output directory. """
        output_dir = cls._initialize_output_dir(primary_attrs)
        dir_ = os.path.join(output_dir, "backups")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_checkpoint_dir(cls, primary_attrs):
        """ Initializes the checkpoint directory path based on the output directory. """
        output_dir = cls._initialize_output_dir(primary_attrs)
        dir_ = os.path.join(output_dir, "checkpoints")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_chats_dir(cls, primary_attrs):
        """ Initializes the chats directory path based on the output directory. """
        output_dir = cls._initialize_output_dir(primary_attrs)
        dir_ = os.path.join(output_dir, "chats")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_tasks_python_env(cls, _):
        """ Initializes the tasks Python environment variable. """
        return TASKS_PYTHON_ENV

    @classmethod
    def _initialize_max_backups(cls, _):
        """ Initializes the maximum number of backups to keep. """
        return MAX_BACKUPS

    @classmethod
    def _initialize_modules_info(cls, primary_attrs):
        """ Initializes the modules information by retrieving and loading the
        modules_info.json file. """
        storage_dir = primary_attrs.get("storage_dir")
        cwd = primary_attrs.get("cwd")
        runner_python_env = primary_attrs.get("runner_python_env")
        profile_dir = os.path.join(storage_dir, PROFILE_SUBFOLDER)
        os.makedirs(profile_dir, exist_ok=True)
        name = ProfileAttrNames.modules_info.value[1]
        module_info_json = os.path.join(profile_dir, name)
        temp_script_path = os.path.join(profile_dir, "retrieve_modules.py")
        execute_python_module(
            module=retrieve_modules,
            args=[cwd, module_info_json],
            env_python_path=runner_python_env,
            cwd=cwd,
            temp_script_path=temp_script_path,
        )

        with open(module_info_json, "r") as f:
            modules_info = json.load(f)

        return modules_info["modules_info"]

    @classmethod
    def _initialize_directory_runner_config(cls, _):
        """ Initializes the directory runner configuration file. """
        config = {
            "task_name": "Task Name",
            "directory_path": "/path/to/directory",
            "macros_text": ["sample macros text", "as list of lines"],
            "resume_from_last_stopped": False,
            "excluded_files": ["only_py_file_name.py"],
            "excluded_dirs": ["/must/be/absolute"],
            "clear_backup_storage": True,
        }
        return config
