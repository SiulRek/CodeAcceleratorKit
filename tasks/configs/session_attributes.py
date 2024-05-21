from enum import Enum
import json
import os

from tasks.configs.constants import CONFIGS_SUBFOLDER
from tasks.management.normalize_path import normalize_path
from tasks.tools.general.retrieve_modules import retrieve_modules


class SessionAttrNames(Enum):
    """Enumeration for context attribute names."""

    cwd = (1, "configs.json")
    python_env = (2, "configs.json")
    cache_dir = (3, "configs.json")
    data_dir = (4, "configs.json")
    fill_text_dir = (5, "configs.json")
    query_templates_dir = (6, "configs.json")
    output_dir = (7, "configs.json")
    checkpoint_dir = (8, "configs.json")
    query_file = (9, "configs.json")
    response_file = (10, "configs.json")
    temporary_script = (11, "configs.json")
    modules_info = (12, "modules_info.json")


class AttributesInitializer:

    @classmethod
    def _initialize_cache_dir(cls, primary_attrs):
        storage_dir = primary_attrs.get("storage_dir")
        dir_ = os.path.join(storage_dir, "__taskcache__")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_data_dir(cls, primary_attrs):
        storage_dir = primary_attrs.get("storage_dir")
        dir_ = os.path.join(storage_dir, "data")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_fill_text_dir(cls, primary_attrs):
        storage_dir = primary_attrs.get("storage_dir")
        data_dir = cls._initialize_data_dir(primary_attrs)
        dir_ = os.path.join(data_dir, "fill_texts")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_query_templates_dir(cls, primary_attrs):
        storage_dir = primary_attrs.get("storage_dir")
        data_dir = cls._initialize_data_dir(primary_attrs)
        dir_ = os.path.join(data_dir, "query_templates")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_output_dir(cls, primary_attrs):
        storage_dir = primary_attrs.get("storage_dir")
        dir_ = os.path.join(storage_dir, "outputs")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_checkpoint_dir(cls, primary_attrs):
        storage_dir = primary_attrs.get("storage_dir")
        output_dir = cls._initialize_output_dir(primary_attrs)
        dir_ = os.path.join(output_dir, "checkpoints")
        dir_ = normalize_path(dir_)
        return dir_

    @classmethod
    def _initialize_query_file(cls, primary_attrs):
        output_dir = cls._initialize_output_dir(primary_attrs)
        path = os.path.join(output_dir, "query.txt")
        path = normalize_path(path)
        return path

    @classmethod
    def _initialize_response_file(cls, primary_attrs):
        output_dir = cls._initialize_output_dir(primary_attrs)
        path = os.path.join(output_dir, "response_file.txt")
        path = normalize_path(path)
        return path

    @classmethod
    def _initialize_temporary_script(cls, primary_attrs):
        cache_dir = cls._initialize_cache_dir(primary_attrs)
        cache_dir = normalize_path(cache_dir)

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        if not hasattr(cls, "_temp_script_counter"):
            cls._temp_script_counter = 1
        else:
            cls._temp_script_counter += 1

        name = f"script_{cls._temp_script_counter}.py"
        path = os.path.join(cache_dir, name)
        path = normalize_path(path)

        return path

    @classmethod
    def _initialize_modules_info(cls, primary_attrs):
        storage_dir = primary_attrs.get("storage_dir")
        config_dir = os.path.join(storage_dir, CONFIGS_SUBFOLDER)
        name = SessionAttrNames.modules_info.value[1]
        module_info_json = os.path.join(config_dir, name)

        if not os.path.exists(module_info_json):
            cwd = primary_attrs.get("cwd")
            retrieve_modules(cwd, module_info_json, 
                             mkdir=True)

        with open(module_info_json, "r") as f:
            modules_info = json.load(f)

        return modules_info["modules_info"]
