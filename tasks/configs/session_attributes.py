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
    data_dir = (4, "configs.json")
    fill_text_dir = (5, "configs.json")
    query_templates_dir = (6, "configs.json")
    output_dir = (7, "configs.json")
    backup_dir = (8, "configs.json")
    checkpoint_dir = (9, "configs.json")
    query_file = (10, "configs.json")
    response_file = (11, "configs.json")
    tasks_python_env = (12, "configs.json")
    max_backups = (13, "configs.json")
    modules_info = (14, "modules_info.json")

# Format of dict: "new name": "old name"
UPDATE_MAPPING = None


class AttributesInitializer:
    """Class responsible for initializing various session attributes. It is used during registration of new task runners with the TaskManager class."""

    @classmethod
    def _initialize_tasks_cache(cls, primary_attrs):
        """Initializes the tasks_cache directory path."""
        dir = normalize_path(TASKS_CACHE)
        return dir

    @classmethod
    def _initialize_data_dir(cls, primary_attrs):
        """Initializes the data directory path based on the storage_dir in primary
        attributes."""
        storage_dir = primary_attrs.get("storage_dir")
        dir_ = os.path.join(storage_dir, "data")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_fill_text_dir(cls, primary_attrs):
        """Initializes the fill text directory path based on the data directory."""
        data_dir = cls._initialize_data_dir(primary_attrs)
        dir_ = os.path.join(data_dir, "fill_texts")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_query_templates_dir(cls, primary_attrs):
        """Initializes the query templates directory path based on the data
        directory."""
        data_dir = cls._initialize_data_dir(primary_attrs)
        dir_ = os.path.join(data_dir, "query_templates")
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
    def _initialize_query_file(cls, primary_attrs):
        """Initializes the query file path based on the output directory."""
        output_dir = cls._initialize_output_dir(primary_attrs)
        path = os.path.join(output_dir, "query.txt")
        path = normalize_path(path)
        return path

    @classmethod
    def _initialize_response_file(cls, primary_attrs):
        """Initializes the response file path based on the output directory."""
        output_dir = cls._initialize_output_dir(primary_attrs)
        path = os.path.join(output_dir, "response_file.txt")
        path = normalize_path(path)
        return path

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