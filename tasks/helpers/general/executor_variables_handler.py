""" Module for handling executor variables, including registration and
initialization. """

from enum import Enum
import os
import json

from tasks.constants.configs import REGISTERED_VARIABLES_JSON, VARIABLE_JSON_NAME


def normalize_path(path):
    """
    Normalizes a file path to use forward slashes.

    Args:
        - path (str): The file path to normalize.

    Returns:
        - str: The normalized file path.
    """
    path = os.path.normpath(path)
    path = path.replace(os.sep, "/")
    return path


class VariableNames(Enum):
    """Enumeration for variable names."""


class ExecutorVariable:
    """
    Handles executor variables, including loading and saving attributes.

    Args:
        - executor_root (str): The root directory of the executor.
        - load_attributes_from_json (bool): Whether to load attributes from
            JSON at initialization.
    """

    def __init__(self, executor_root, load_attributes_from_json=True):
        self._executor_root = normalize_path(executor_root)
        self._room_dir = self._get_room_dir(executor_root)
        self._variable_json = os.path.join(self.room_dir, VARIABLE_JSON_NAME)
        if load_attributes_from_json:
            self.load_attributes_from_json()

    @property
    def executor_root(self):
        """
        Returns the normalized executor root path.

        Returns:
            - str: The executor root path.
        """
        return self._executor_root

    @property
    def variable_json(self):
        """
        Returns the path to the variable JSON file.

        Returns:
            - str: The path to the variable JSON file.
        """
        return self._variable_json

    @property
    def room_dir(self):
        """
        Returns the room directory path.

        Returns:
            - str: The room directory path.
        """
        return self._variable_json

    def _get_room_dir(self, executor_root):
        """
        Determines the room directory based on the executor root.

        Args:
            - executor_root (str): The root directory of the executor.

        Returns:
            - str: The room directory path.

        Raises:
            - ValueError: If the executor root is not registered.
        """
        with open(REGISTERED_VARIABLES_JSON, "r", encoding="utf-8") as f:
            registered_variables = json.load(f)
        if executor_root not in registered_variables:
            msg = f"Executor root {executor_root} is not registered."
            raise ValueError(msg)
        return registered_variables[executor_root]

    def load_attributes_from_dict(self, attributes_dict):
        """
        Loads attributes from a dictionary.

        Args:
            - attributes_dict (dict): A dictionary containing the
                attributes to load.

        Raises:
            - KeyError: If a required key is missing.
        """
        for key in VariableNames:
            if key not in attributes_dict:
                msg = f"Missing key {key}"
                raise KeyError(msg)
            setattr(self, key, attributes_dict[key])

    def load_attributes_from_json(self):
        """Loads attributes from a JSON file."""
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
        for key in VariableNames:
            if not hasattr(self, key):
                msg = f"Missing attribute {key}"
                raise AttributeError(msg)
            attributes_dict[key] = getattr(self, key)
        with open(self.variable_json, "w", encoding="utf-8") as f:
            json.dump(attributes_dict, f, indent=4)


class ExecutorVariablesHandler:
    """Handles the registration and initialization of executor variables."""

    @classmethod
    def _register(cls, executor_root, room_dir):
        """
        Registers an executor root and its corresponding room directory.

        Args:
            - executor_root (str): The root directory of the executor.
            - room_dir (str): The room directory to register.

        Raises:
            - ValueError: If the executor root is already registered.
        """
        if not os.path.exists(REGISTERED_VARIABLES_JSON):
            with open(REGISTERED_VARIABLES_JSON, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)
                registered_variables = {}
        else:
            with open(REGISTERED_VARIABLES_JSON, "r", encoding="utf-8") as f:
                registered_variables = json.load(f)
        if executor_root in registered_variables:
            msg = f"Task executor root {executor_root} is already registered."
            msg += " Delete the existing registration to re-register."
            raise ValueError(msg)
        registered_variables[executor_root] = room_dir
        with open(REGISTERED_VARIABLES_JSON, "w", encoding="utf-8") as f:
            json.dump(registered_variables, f, indent=4)

    @classmethod
    def _initialize_attributes(cls, executor_root, room_dir):
        """
        Initializes attributes for the executor based on its root and room
        directory.

        Args:
            - executor_root (str): The root directory of the executor.
            - room_dir (str): The room directory.

        Returns:
            - dict: A dictionary of initialized attributes.
        """
        attributes = {}
        for key in VariableNames:
            init_func = getattr(cls, f"_initialize_{key}")
            attributes[key] = init_func(executor_root, room_dir)
        return attributes

    @classmethod
    def register(cls, executor_root, room_dir="local/task_room"):
        """
        Registers an executor and initializes attributes.

        Args:
            - executor_root (str): The root directory of the executor.
            - room_dir (str, optional): The room directory. Defaults to
                "local/task_room".
        """
        executor_root = normalize_path(executor_root)
        room_dir = normalize_path(room_dir)
        if not room_dir.startswith(executor_root):
            room_dir = os.path.join(executor_root, room_dir)
        cls._register(executor_root, room_dir)
        attributes = cls._initialize_attributes(executor_root, room_dir)
        variable = ExecutorVariable(executor_root, load_attributes_from_json=False)
        variable.load_attributes_from_dict(attributes)
        variable.save_attributes()
