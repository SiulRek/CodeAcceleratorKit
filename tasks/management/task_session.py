import json
import os
import pickle
import warnings

import tasks.configs.constants as configs
from tasks.management.normalize_path import normalize_path
import tasks.configs.session_attributes as Names


class TaskSession:
    """
    Stores the TaskSession, including loading and saving attributes.

    Args:
        - runner_root (str): The root directory of the runner.
        - load_attributes_from_storage (bool): Whether to load attributes
            from the storage directory.
    """

    def __init__(self, runner_root, load_attributes_from_storage=True):
        self._runner_root = normalize_path(runner_root)
        self._storage_dir = self._get_storage_dir(runner_root)
        self._configs_dir = os.path.join(self.storage_dir, configs.CONFIGS_SUBFOLDER)
        if load_attributes_from_storage:
            self.load_attributes_from_storage()

    @property
    def runner_root(self):
        """
        Returns the normalized runner root path.

        Returns:
            - str: The runner root path.
        """
        return self._runner_root

    @property
    def storage_dir(self):
        """
        Returns the storage directory path.

        Returns:
            - str: The storage directory path.
        """
        return self._storage_dir

    @property
    def configs_dir(self):
        """
        Returns the directory path for storing configuration files inside the
        runner storage directory.

        Returns:
            - str: The configuration directory path.
        """
        return self._configs_dir

    def _get_storage_dir(self, runner_root):
        """
        Determines the storage directory based on the registration data of
        runner root.

        Args:
            - runner_root (str): The root directory of the runner.

        Returns:
            - str: The storage directory path.
        """
        with open(configs.REGISTERED_RUNNERS_JSON, "r", encoding="utf-8") as f:
            registered_variables = json.load(f)
        if runner_root not in registered_variables:
            msg = f"Runner root {runner_root} is not registered."
            raise ValueError(msg)
        return registered_variables[runner_root]

    def load_attributes_from_dict(self, attributes_dict):
        """
        Loads attributes from a dictionary.

        Args:
            - attributes_dict (dict): A dictionary containing the attributes
                to load.
        """
        for attr in Names.SessionAttrNames.__members__.keys():
            if attr not in attributes_dict:
                continue
            setattr(self, attr, attributes_dict[attr])
        for attr in attributes_dict.keys():
            if attr not in Names.SessionAttrNames.__members__.keys():
                warnings.warn(
                    f"Attribute {attr} is not an attribute defined in ContextAttrNames."
                )
                setattr(self, attr, attributes_dict[attr])

    def load_attributes_from_storage(self):
        """Loads attributes from the storage/configs directory."""
        if not os.path.isdir(self.configs_dir):
            msg = f"Directory {self.configs_dir} does not exist. Please register the runner properly."
            raise NotADirectoryError(msg)
        attributes_dict = {}
        for dir_ in os.listdir(self.configs_dir):
            if dir_.endswith(".json"):
                with open(
                    os.path.join(self.configs_dir, dir_), "r", encoding="utf-8"
                ) as f:
                    attributes_dict = json.load(f)
                self.load_attributes_from_dict(attributes_dict)
            elif dir_.endswith(".pkl"):
                with open(os.path.join(self.configs_dir, dir_), "rb") as f:
                    attributes_dict = pickle.load(f)
                self.load_attributes_from_dict(attributes_dict)

    def are_attributes_complete(self):
        """
        Checks if all attributes defined in ContextAttrNames are present in the
        instance.

        Returns:
            - bool: True if all attributes are present, False otherwise.
        """
        for attr in Names.SessionAttrNames.__members__.keys():
            if not hasattr(self, attr):
                return False
        return True

    def save_attributes(self):
        """
        Saves attributes to a JSON or pickle file.

        Raises:
            - AttributeError: If a required attribute is missing.
        """
        if not self.are_attributes_complete():
            msg = "Missing context attribute(s) to save."
            raise AttributeError(msg)
        os.makedirs(self.configs_dir, exist_ok=True)

        configs = {}
        for member in Names.SessionAttrNames:
            attr = member.name
            _, file_name = member.value
            if file_name not in configs:
                configs[file_name] = {}
            configs[file_name][attr] = getattr(self, attr)
        for file_name, attributes in configs.items():
            file_path = os.path.join(self.configs_dir, file_name)
            if file_name.endswith(".json"):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(attributes, f, indent=4)
            elif file_name.endswith(".pkl"):
                with open(file_path, "wb") as f:
                    pickle.dump(attributes, f)
