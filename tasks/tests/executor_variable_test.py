from enum import Enum
import json
import os
import unittest
from unittest.mock import patch
import tempfile

from tasks.variables.executor_variable import ExecutorVariable
from tasks.variables.normalize_path import normalize_path


class VariableNamesMock(Enum):
    VAR1 = "VAR1"
    VAR2 = "VAR2"


class TestExecutorVariable(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.executor_root = normalize_path(os.path.join(self.temp_dir.name, "executor_root"))
        self.json_mock = normalize_path(os.path.join(self.temp_dir.name, "registered_variables.json"))

        registered_variables = {
            self.executor_root: normalize_path(os.path.join(self.temp_dir.name, "task_room"))
        }

        with open(self.json_mock, "w", encoding="utf-8") as f:
            json.dump(registered_variables, f, indent=4)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_attributes_from_json_1(self):
        with patch(
            "tasks.constants.configs.REGISTERED_VARIABLES_JSON", self.json_mock
        ), patch(
            "tasks.variables.variable_names.VariableNames", VariableNamesMock
        ):
            executor_variable = ExecutorVariable(
                self.executor_root, load_attributes_from_json=False
            )
            room_dir = os.path.dirname(executor_variable.variable_json)
            os.makedirs(room_dir, exist_ok=True)
            with open(executor_variable.variable_json, "w", encoding="utf-8") as f:
                json.dump({"VAR1": "value1", "VAR2": "value2"}, f, indent=4)
            executor_variable.load_attributes_from_json()

            self.assertEqual(executor_variable.VAR1, "value1")
            self.assertEqual(executor_variable.VAR2, "value2")
    
    def test_load_attributes_from_json_2(self):
        with patch(
            "tasks.constants.configs.REGISTERED_VARIABLES_JSON", self.json_mock
        ), patch(
            "tasks.variables.variable_names.VariableNames", VariableNamesMock
        ):
            variable_json = ExecutorVariable(
                self.executor_root, load_attributes_from_json=False
            ).variable_json
            room_dir = os.path.dirname(variable_json)
            os.makedirs(room_dir, exist_ok=True)
            with open(variable_json, "w", encoding="utf-8") as f:
                json.dump({"VAR1": "value1", "VAR2": "value2"}, f, indent=4)
            executor_variable = ExecutorVariable(
                self.executor_root, load_attributes_from_json=True
            )

            self.assertEqual(executor_variable.VAR1, "value1")
            self.assertEqual(executor_variable.VAR2, "value2")
    
    def test_load_attributes_from_dict(self):
        with patch( "tasks.constants.configs.REGISTERED_VARIABLES_JSON", self.json_mock), patch(
            "tasks.variables.variable_names.VariableNames", VariableNamesMock
        ):
            executor_variable = ExecutorVariable(
                self.executor_root, load_attributes_from_json=False
            )
            executor_variable.load_attributes_from_dict({"VAR1": "value1", "VAR2": "value2"})


            self.assertEqual(executor_variable.VAR1, "value1")
            self.assertEqual(executor_variable.VAR2, "value2")

    def test_save_attributes(self):
        with patch(
            "tasks.constants.configs.REGISTERED_VARIABLES_JSON", self.json_mock
        ), patch(
            "tasks.variables.variable_names.VariableNames", VariableNamesMock
        ):

            executor_variable = ExecutorVariable(
                self.executor_root, load_attributes_from_json=False
            )
            executor_variable.VAR1 = "value1"
            executor_variable.VAR2 = "value2"
            room_dir = os.path.dirname(executor_variable.variable_json)
            os.makedirs(room_dir, exist_ok=True)
            executor_variable.save_attributes()

            with open(executor_variable.variable_json, "r", encoding="utf-8") as f:
                written_data = json.load(f)

            expected_data = {
                "VAR1": "value1",
                "VAR2": "value2",
            }
            self.assertEqual(written_data, expected_data)


if __name__ == "__main__":
    unittest.main()
