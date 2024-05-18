from enum import Enum
import json
import os
import shutil
import unittest
from unittest.mock import patch

from tasks.variables.executor_variable import ExecutorVariable
from tasks.variables.normalize_path import normalize_path


class VariableNamesMock(Enum):
    VAR1 = "VAR1"
    VAR2 = "VAR2"


EXECUTOR_ROOT = normalize_path(os.path.join("tasks", "tests", "temp", "executor_root"))
JSON_MOCK = normalize_path(
    os.path.join("tasks", "tests", "temp", "registered_variables.json")
)


class TestExecutorVariable(unittest.TestCase):

    def setUp(self):
        json_dir = os.path.dirname(JSON_MOCK)
        os.makedirs(json_dir, exist_ok=True)
        registered_variables = {
            EXECUTOR_ROOT: normalize_path(os.path.join(json_dir, "task_room"))
        }
        with open(JSON_MOCK, "w", encoding="utf-8") as f:
            json.dump(registered_variables, f, indent=4)

    def tearDown(self):
        json_dir = os.path.dirname(JSON_MOCK)
        if os.path.exists(json_dir):
            shutil.rmtree(json_dir)

    def test_save_attributes(self):
        with patch(
            "tasks.constants.configs.REGISTERED_VARIABLES_JSON", JSON_MOCK
        ), patch(
            "tasks.variables.variable_names.VariableNames", VariableNamesMock
        ), patch(
            "os.path.exists", return_value=True
        ):

            executor_variable = ExecutorVariable(
                EXECUTOR_ROOT, load_attributes_from_json=False
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
