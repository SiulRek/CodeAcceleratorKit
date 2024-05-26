from enum import Enum
import json
import os

from tasks.configs.constants import CONFIGS_SUBFOLDER, TASKS_PYTHON_ENV, TASKS_CACHE, MAX_BACKUPS
from tasks.tasks.management.normalize_path import normalize_path
from tasks.tools.general.retrieve_modules import retrieve_modules


class SessionAttrNames(Enum):
    """
    Enumeration for context attribute names, representing different
    configurable attributes for a session, each associated with a unique
    identifier and a file where its value might be found.
    """
    cwd = (1, "configs.json")
    runner_python_env = (2, "configs.json")
    tasks_cache = (3, "configs.json")
    runners_cache = (4, "configs.json")
    templates_dir = (5, "configs.json")
    fill_text_dir = (6, "configs.json")
    macros_templates_dir = (7, "configs.json")
    output_dir = (8, "configs.json")
    backup_dir = (9, "configs.json")
    checkpoint_dir = (10, "configs.json")
    chats_dir = (11, "configs.json")
    tasks_python_env = (12, "configs.json")
    max_backups = (13, "configs.json")
    modules_info = (14, "modules_info.json")


UPDATE_MAPPING = {
    # New name: old name 
    # New Name should cover all names from SessionAttrNames
    # Old name None is accepted
    "cwd": "cwd",
    "runner_python_env": "runner_python_env",
    "tasks_cache": "tasks_cache",
    "runners_cache": "runners_cache",
    "templates_dir": "templates_dir",
    "fill_text_dir": "fill_text_dir",
    "macros_templates_dir": "macros_templates_dir",
    "output_dir": "output_dir",
    "backup_dir": "backup_dir",
    "checkpoint_dir": "checkpoint_dir",
    "chats_dir": None,
    "tasks_python_env": "tasks_python_env",
    "max_backups": "max_backups",
    "modules_info": "modules_info"
}


class AttributesInitializer:
    """Class responsible for initializing various session attributes. It is used during registration of new task runners with the TaskManager class."""

    @classmethod
    def _initialize_tasks_cache(cls, primary_attrs):
        """Initializes the tasks_cache directory path."""
        dir = normalize_path(TASKS_CACHE)
        return dir
    
    @classmethod
    def _initialize_runners_cache(cls, primary_attrs):
        """Initializes the runners_cache directory path."""
        dir_ = normalize_path(primary_attrs.get("storage_dir"))
        dir_ = os.path.join(dir_, "__taskscache__")
        return dir_

    @classmethod
    def _initialize_templates_dir(cls, primary_attrs):
        """Initializes the templates directory path based on the storage_dir in primary
        attributes."""
        storage_dir = primary_attrs.get("storage_dir")
        dir_ = os.path.join(storage_dir, "templates")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_fill_text_dir(cls, primary_attrs):
        """Initializes the fill text directory path based on the templates directory."""
        templates_dir = cls._initialize_templates_dir(primary_attrs)
        dir_ = os.path.join(templates_dir, "fill_texts")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_macros_templates_dir(cls, primary_attrs):
        """Initializes the query templates directory path based on the templates
        directory."""
        templates_dir = cls._initialize_templates_dir(primary_attrs)
        dir_ = os.path.join(templates_dir, "macros_templates")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_output_dir(cls, primary_attrs):
        """Initializes the output directory path based on the storage_dir in
        primary attributes."""
        storage_dir = primary_attrs.get("storage_dir")
        dir_ = os.path.join(storage_dir, "outputs")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_backup_dir(cls, primary_attrs):
        """Initializes the backup directory path based on the output directory."""
        output_dir = cls._initialize_output_dir(primary_attrs)
        dir_ = os.path.join(output_dir, "backups")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_checkpoint_dir(cls, primary_attrs):
        """Initializes the checkpoint directory path based on the output directory."""
        output_dir = cls._initialize_output_dir(primary_attrs)
        dir_ = os.path.join(output_dir, "checkpoints")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_chats_dir(cls, primary_attrs):
        """Initializes the chats directory path based on the output directory."""
        output_dir = cls._initialize_output_dir(primary_attrs)
        dir_ = os.path.join(output_dir, "chats")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_tasks_python_env(cls, _):
        """Initializes the tasks Python environment variable."""
        return TASKS_PYTHON_ENV

    @classmethod
    def _initialize_max_backups(cls, _):
        """Initializes the maximum number of backups to keep."""
        return MAX_BACKUPS
     
    @classmethod
    def _initialize_modules_info(cls, primary_attrs):
        """Initializes the modules information by retrieving and loading the
        modules_info.json file."""
        storage_dir = primary_attrs.get("storage_dir")
        config_dir = os.path.join(storage_dir, CONFIGS_SUBFOLDER)
        name = SessionAttrNames.modules_info.value[1]
        module_info_json = os.path.join(config_dir, name)

        if not os.path.exists(module_info_json):
            cwd = primary_attrs.get("cwd")
            retrieve_modules(cwd, module_info_json, mkdir=True)

        with open(module_info_json, "r") as f:
            modules_info = json.load(f)

        return modules_info["modules_info"]