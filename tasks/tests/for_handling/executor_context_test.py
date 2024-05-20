import os
import json
import pickle
import tempfile
import unittest
from unittest.mock import patch
from enum import Enum

from tasks.handling.executor_context import ExecutorContext
from tasks.handling.normalize_path import normalize_path
from tasks.tools.for_testing.test_result_logger import TestResultLogger

ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
OUTPUT_DIR = os.path.join(ROOT_DIR, "tasks", "tests", "outputs")
LOG_FILE = os.path.join(OUTPUT_DIR, "test_results.log")


class AttrNamesMock(Enum):
    cwd = (1, "configs.json")
    python_env = (2, "configs.json")


class TestExecutorVariable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        cls.logger = TestResultLogger(LOG_FILE)
        cls.logger.log_title("Executor Variable Test")

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.executor_root = normalize_path(
            os.path.join(self.temp_dir.name, "executor_root")
        )
        self.json_mock = normalize_path(
            os.path.join(self.temp_dir.name, "registered_variables.json")
        )

        registered_executors = {
            self.executor_root: normalize_path(
                os.path.join(self.temp_dir.name, "task_storage")
            )
        }

        with open(self.json_mock, "w", encoding="utf-8") as f:
            json.dump(registered_executors, f, indent=4)

        self.configs_dir = os.path.join(self.temp_dir.name, "task_storage", "configs")
        os.makedirs(self.configs_dir, exist_ok=True)

    def tearDown(self):
        self.logger.log_test_outcome(self._outcome.result, self._testMethodName)
        self.temp_dir.cleanup()

    def test_load_attributes_1(self):
        with patch(
            "tasks.constants.configs.REGISTERED_EXECUTORS_JSON", self.json_mock
        ), patch(
            "tasks.handling.context_attribute_names.ContextAttrNames", AttrNamesMock
        ):
            executor_context = ExecutorContext(
                self.executor_root, load_attributes_from_storage=False
            )
            with open(
                os.path.join(self.configs_dir, "configs.json"), "w", encoding="utf-8"
            ) as f:
                json.dump({"cwd": "test_dir", "python_env": "test_env"}, f, indent=4)

            executor_context.load_attributes_from_storage()

            self.assertEqual(executor_context.cwd, "test_dir")
            self.assertEqual(executor_context.python_env, "test_env")

    def test_load_attributes(self):
        with patch(
            "tasks.constants.configs.REGISTERED_EXECUTORS_JSON", self.json_mock
        ), patch(
            "tasks.handling.context_attribute_names.ContextAttrNames", AttrNamesMock
        ):
            variable_json = ExecutorContext(
                self.executor_root, load_attributes_from_storage=False
            ).configs_dir
            with open(
                os.path.join(variable_json, "configs.json"), "w", encoding="utf-8"
            ) as f:
                json.dump({"cwd": "test_dir", "python_env": "test_env"}, f, indent=4)

            executor_context = ExecutorContext(
                self.executor_root, load_attributes_from_storage=True
            )

            self.assertEqual(executor_context.cwd, "test_dir")
            self.assertEqual(executor_context.python_env, "test_env")

    def test_load_attributes_from_dict(self):
        with patch(
            "tasks.constants.configs.REGISTERED_EXECUTORS_JSON", self.json_mock
        ), patch(
            "tasks.handling.context_attribute_names.ContextAttrNames", AttrNamesMock
        ):
            executor_context = ExecutorContext(
                self.executor_root, load_attributes_from_storage=False
            )
            executor_context.load_attributes_from_dict(
                {"cwd": "test_dir", "python_env": "test_env"}
            )

            self.assertEqual(executor_context.cwd, "test_dir")
            self.assertEqual(executor_context.python_env, "test_env")

    def test_load_attributes_from_storage_with_pickle(self):
        with patch(
            "tasks.constants.configs.REGISTERED_EXECUTORS_JSON", self.json_mock
        ), patch(
            "tasks.handling.context_attribute_names.ContextAttrNames", AttrNamesMock
        ):
            executor_context = ExecutorContext(
                self.executor_root, load_attributes_from_storage=False
            )

            data = {"cwd": "test_dir_pickle"}
            with open(os.path.join(self.configs_dir, "cwd.pickle"), "wb") as f:
                pickle.dump(data["cwd"], f)

            executor_context.load_attributes_from_storage()
            self.assertEqual(executor_context.cwd, "test_dir_pickle")

    def test_save_attributes(self):
        with patch(
            "tasks.constants.configs.REGISTERED_EXECUTORS_JSON", self.json_mock
        ), patch(
            "tasks.handling.context_attribute_names.ContextAttrNames", AttrNamesMock
        ):
            executor_context = ExecutorContext(
                self.executor_root, load_attributes_from_storage=False
            )
            executor_context.load_attributes_from_dict(
                {"cwd": "test_dir", "python_env": "test_env"}
            )
            executor_context.save_attributes()

            with open(
                os.path.join(self.configs_dir, "configs.json"), "r", encoding="utf-8"
            ) as f:
                written_data = json.load(f)

            expected_data = {"cwd": "test_dir", "python_env": "test_env"}
            self.assertEqual(written_data, expected_data)


if __name__ == "__main__":
    unittest.main()