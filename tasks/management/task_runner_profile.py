#TODO Maybe its not good to load attributes twice, so make flag or so
from copy import deepcopy
import json
import os
import pickle
import warnings

import tasks.configs.constants as configs
from tasks.management.normalize_path import normalize_path
import tasks.configs.profile_attributes as Attributes


class TaskRunnerProfile:
    """
    Stores the TaskRunnerProfile, including loading and saving attributes.

    Parameters
    ----------
    runner_root (str)
        The root directory of the runner.
    load_attributes_from_storage (bool)
        Whether to load attributes from the storage directory.
    """

    def __init__(self, runner_root, load_attributes_from_storage=True):
        self._root = normalize_path(runner_root)
        self._storage_dir = self._get_storage_dir(self.root)
        self._profile_dir = os.path.join(self.storage_dir, configs.PROFILE_SUBFOLDER)
        self._all_attributes = {}
        if load_attributes_from_storage:
            self.load_attributes_from_storage()

    @property
    def root(self):
        """
        Returns the normalized runner root path.

        Returns
        -------
        str
            The runner root path.
        """
        return self._root

    @property
    def storage_dir(self):
        """
        Returns the storage directory path.

        Returns
        -------
        str
            The storage directory path.
        """
        return self._storage_dir

    @property
    def profile_dir(self):
        """
        Returns the directory path for storing configuration files inside the
        runner storage directory.

        Returns
        -------
        str
            The configuration directory path.
        """
        return self._profile_dir
    
    @property
    def attributes(self):
        """
        Returns the attributes dictionary.

        Returns
        -------
        dict
            The attributes dictionary.
        """
        return self._all_attributes

    def _get_storage_dir(self, runner_root):
        """
        Determines the storage directory based on the registration data of
        runner root.

        Parameters
        ----------
        runner_root (str)
            The root directory of the runner.

        Returns
        -------
        str
            The storage directory path.
        """
        with open(configs.REGISTERED_RUNNERS_JSON, "r", encoding="utf-8") as f:
            registered_variables = json.load(f)
        if runner_root not in registered_variables:
            msg = f"Runner root {runner_root} is not registered."
            raise ValueError(msg)
        return registered_variables[runner_root]
    
    def set_attribute(self, attribute_name, attribute_value):
        """
        Sets an attribute.

        Parameters
        ----------
        attribute_name (str)
            The name of the attribute.
        attribute_value (Any)
            The value of the attribute.
        """
        if attribute_name not in Attributes.ProfileAttrNames.__members__.keys():
            warnings.warn(f"Attribute {attribute_name} is not defined in the ProfileAttrNames.")
        setattr(self, attribute_name, attribute_value)
        self._all_attributes[attribute_name] = attribute_value
    
    def get_attribute_copy(self, attribute_name):
        """
        Returns a deep copy of the attribute.

        Parameters
        ----------
        attribute_name (str)
            The name of the attribute.

        Returns
        -------
        Any
            A deep copy of the attribute.
        """
        if attribute_name not in self._all_attributes:
            msg = f"Attribute {attribute_name} is not present in the attributes."
            raise AttributeError(msg)
        return deepcopy(self._all_attributes[attribute_name])
    
    def clear_attributes(self):
        """
        Clears all attributes.
        """
        for attr in self._all_attributes:
            delattr(self, attr)
        self._all_attributes = {}

    def load_attributes_from_dict(self, attributes_dict):
        """
        Loads attributes from a dictionary.

        Parameters
        ----------
        attributes_dict (dict)
            A dictionary containing the attributes to load.
        """
        for name, value in attributes_dict.items():
            self.set_attribute(name, value)

    def load_attributes_from_storage(self):
        """
        Loads attributes from the storage/configs directory.
        """
        if not os.path.isdir(self.profile_dir):
            msg = f"Directory {self.profile_dir} does not exist. Please register the runner properly."
            raise NotADirectoryError(msg)
        attributes_dict = {}
        for dir_ in os.listdir(self.profile_dir):
            if dir_.endswith(".json"):
                with open(
                    os.path.join(self.profile_dir, dir_), "r", encoding="utf-8"
                ) as f:
                    attributes_dict = json.load(f)
                self.load_attributes_from_dict(attributes_dict)
            elif dir_.endswith(".pkl"):
                with open(os.path.join(self.profile_dir, dir_), "rb") as f:
                    attributes_dict = pickle.load(f)
                self.load_attributes_from_dict(attributes_dict)
                
    def update_attributes(self, reinitialized_attrs):
        """
        Updates the attributes with the reinitialized attributes. The update
        depends on the UPDATE_MAPPING parameter.

        Parameters
        ----------
        reinitialized_attrs (dict)
            A dictionary containing the reinitialized attributes. It is
            expected that the keys corresponds to ProfileAttrNames.
        """
        updated_attrs = {}
        for reinit_name in reinitialized_attrs:
            if reinit_name not in Attributes.UPDATE_MAPPING:
                raise AttributeError(f"Attribute {reinit_name} is not in the update mapping.")
            old_name = Attributes.UPDATE_MAPPING[reinit_name]
            if old_name is None:
                updated_attrs[reinit_name] = reinitialized_attrs[reinit_name]
            else:
                updated_attrs[reinit_name] = self.get_attribute_copy(old_name)
        
        self.clear_attributes()
        self.load_attributes_from_dict(updated_attrs)
            
    def are_attributes_complete(self):
        """
        Checks if all attributes defined in ContextAttrNames are present in the

        Returns
        -------
        bool
            True if all attributes are present, False otherwise.
        """
        for attr in Attributes.ProfileAttrNames.__members__.keys():
            if not hasattr(self, attr):
                return False
        return True

    def save_attributes(self):
        """
        Saves attributes to a JSON or pickle file.

        Raises
        -----
        AttributeError
            If a required attribute is missing.
        """
        if not self.are_attributes_complete():
            msg = "Missing context attribute(s) to save."
            raise AttributeError(msg)
        os.makedirs(self.profile_dir, exist_ok=True)

        configs = {}
        for member in Attributes.ProfileAttrNames:
            attr = member.name
            _, file_name = member.value
            if file_name not in configs:
                configs[file_name] = {}
            configs[file_name][attr] = getattr(self, attr)
        file_names = []
        for file_name, attributes in configs.items():
            file_path = os.path.join(self.profile_dir, file_name)
            if file_name.endswith(".json"):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(attributes, f, indent=4)
            elif file_name.endswith(".pkl"):
                with open(file_path, "wb") as f:
                    pickle.dump(attributes, f)
            else:
                raise ValueError(f"File name {file_name} is not supported.")
            file_names.append(file_name)
        for name in os.listdir(self.profile_dir):
            if name not in file_names:
                warnings.warn(f"File {name} is unknown and will be ignored.")