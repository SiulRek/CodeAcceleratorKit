import json
import os

import tasks.constants.configs as configs
from tasks.handling.normalize_path import normalize_path
import tasks.handling.context_attribute_names as Names


class ExecutorContext:
    """
    Handles executor context, including loading and saving attributes.

    Args:
        - executor_root (str): The root directory of the executor.
        - load_attributes_from_json (bool): Whether to load attributes from
            JSON at initialization.
    """

    def __init__(self, executor_root, load_attributes_from_json=True):
        self._executor_root = normalize_path(executor_root)
        self._room_dir = self._get_room_dir(executor_root)
        self._variable_json = os.path.join(self.room_dir, configs.VARIABLE_JSON_NAME)
        if load_attributes_from_json:
            self.load_attributes()

    @property
    def executor_root(self):
        """
        Returns the normalized executor root path.

        Returns:
            - str: The executor root path.
        """
        return self._executor_root

    @property
    def room_dir(self):
        """
        Returns the room directory path.

        Returns:
            - str: The room directory path.
        """
        return self._room_dir

    @property
    def variable_json(self):
        """
        Returns the path to the variable JSON file.

        Returns:
            - str: The path to the variable JSON file.
        """
        return self._variable_json

    def _get_room_dir(self, executor_root):
        """
        Determines the room directory based on the registration data of executor
        root.

        Args:
            - executor_root (str): The root directory of the executor.

        Returns:
            - str: The room directory path.

        Raises:
            - ValueError: If the executor root is not registered.
        """
        with open(configs.REGISTERED_EXECUTORS_JSON, "r", encoding="utf-8") as f:
            registered_variables = json.load(f)
        if executor_root not in registered_variables:
            msg = f"Executor root {executor_root} is not registered."
            raise ValueError(msg)
        return registered_variables[executor_root]

    def load_attributes_from_dict(self, attributes_dict):
        """
        Loads attributes from a dictionary.

        Args:
            - attributes_dict (dict): A dictionary containing the attributes
                to load.

        Raises:
            - KeyError: If a required key is missing.
        """
        for key in Names.ContextAttrNames.__members__.keys():
            if key not in attributes_dict:
                msg = f"Missing attribute {key} in attributes dictionary."
                raise KeyError(msg)
            setattr(self, key, attributes_dict[key])

    def load_attributes(self):
        """
        Loads attributes from the Variable JSON file.

        Raises:
            - FileNotFoundError: If the variable JSON file does not exist.
        """
        if not os.path.exists(self.variable_json):
            msg = f"Variable JSON file {self.variable_json} does not exist or has been deleted."
            raise FileNotFoundError(msg)
        with open(self.variable_json, "r", encoding="utf-8") as f:
            attributes_dict = json.load(f)
        self.load_attributes_from_dict(attributes_dict)

    def save_attributes(self):
        """
        Saves attributes to a JSON file.

        Raises:
            - AttributeError: If a required attribute is missing.
        """
        attributes_dict = {}
        for key in Names.ContextAttrNames.__members__.keys():
            if not hasattr(self, key):
                msg = f"Missing attribute {key}"
                raise AttributeError(msg)
            attributes_dict[key] = getattr(self, key)
        with open(self.variable_json, "w", encoding="utf-8") as f:
            json.dump(attributes_dict, f, indent=4)
