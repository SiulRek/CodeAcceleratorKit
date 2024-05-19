from enum import Enum
import json
import os
import unittest
from unittest.mock import patch
import tempfile

from tasks.handling.executor_context import ExecutorContext
from tasks.handling.normalize_path import normalize_path


class AttrNamesMock(Enum):
    VAR1 = "VAR1"
    VAR2 = "VAR2"


class TestExecutorVariable(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.executor_root = normalize_path(os.path.join(self.temp_dir.name, "executor_root"))
        self.json_mock = normalize_path(os.path.join(self.temp_dir.name, "registered_variables.json"))

        registered_executors = {
            self.executor_root: normalize_path(os.path.join(self.temp_dir.name, "task_room"))
        }

        with open(self.json_mock, "w", encoding="utf-8") as f:
            json.dump(registered_executors, f, indent=4)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_attributes_1(self):
        with patch(
            "tasks.constants.configs.REGISTERED_EXECUTORS_JSON", self.json_mock
        ), patch(
            "tasks.handling.context_attribute_names.ContextAttrNames" , AttrNamesMock
        ):
            executor_context = ExecutorContext(
                self.executor_root, load_attributes_from_json=False
            )
            room_dir = os.path.dirname(executor_context.variable_json)
            os.makedirs(room_dir, exist_ok=True)
            with open(executor_context.variable_json, "w", encoding="utf-8") as f:
                json.dump({"VAR1": "value1", "VAR2": "value2"}, f, indent=4)
            executor_context.load_attributes()

            self.assertEqual(executor_context.VAR1, "value1")
            self.assertEqual(executor_context.VAR2, "value2")
    
    def test_load_attributes(self):
        with patch(
            "tasks.constants.configs.REGISTERED_EXECUTORS_JSON", self.json_mock
        ), patch(
            "tasks.handling.context_attribute_names.ContextAttrNames", AttrNamesMock
        ):
            variable_json = ExecutorContext(
                self.executor_root, load_attributes_from_json=False
            ).variable_json
            room_dir = os.path.dirname(variable_json)
            os.makedirs(room_dir, exist_ok=True)
            with open(variable_json, "w", encoding="utf-8") as f:
                json.dump({"VAR1": "value1", "VAR2": "value2"}, f, indent=4)
            executor_context = ExecutorContext(
                self.executor_root, load_attributes_from_json=True
            )

            self.assertEqual(executor_context.VAR1, "value1")
            self.assertEqual(executor_context.VAR2, "value2")
    
    def test_load_attributes_from_dict(self):
        with patch( "tasks.constants.configs.REGISTERED_EXECUTORS_JSON", self.json_mock), patch(
            "tasks.handling.context_attribute_names.ContextAttrNames", AttrNamesMock
        ):
            executor_context = ExecutorContext(
                self.executor_root, load_attributes_from_json=False
            )
            executor_context.load_attributes_from_dict({"VAR1": "value1", "VAR2": "value2"})


            self.assertEqual(executor_context.VAR1, "value1")
            self.assertEqual(executor_context.VAR2, "value2")

    def test_save_attributes(self):
        with patch(
            "tasks.constants.configs.REGISTERED_EXECUTORS_JSON", self.json_mock
        ), patch(
            "tasks.handling.context_attribute_names.ContextAttrNames", AttrNamesMock
        ):

            executor_context = ExecutorContext(
                self.executor_root, load_attributes_from_json=False
            )
            executor_context.VAR1 = "value1"
            executor_context.VAR2 = "value2"
            room_dir = os.path.dirname(executor_context.variable_json)
            os.makedirs(room_dir, exist_ok=True)
            executor_context.save_attributes()

            with open(executor_context.variable_json, "r", encoding="utf-8") as f:
                written_data = json.load(f)

            expected_data = {
                "VAR1": "value1",
                "VAR2": "value2",
            }
            self.assertEqual(written_data, expected_data)


if __name__ == "__main__":
    unittest.main()
