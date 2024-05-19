from enum import Enum
import json
import os
import tempfile
import unittest
from unittest.mock import patch

import tasks
from tasks.handling.executor_handler import ExecutorHandler as Handler
from tasks.handling.normalize_path import normalize_path


class AttrNamesMock(Enum):
    VAR1_DIR = "value1"
    VAR2_DIR = "value2"


class TestExecutorHandler(unittest.TestCase):
 
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.executor_root = normalize_path(
            os.path.join(self.temp_dir.name, "executor_root")
        )
        self.storage_subfolder = "task_storage"
        self.storage_dir = os.path.join(self.executor_root, self.storage_subfolder)
        self.json_mock = normalize_path(
            os.path.join(self.temp_dir.name, "registered_variables.json")
        )
        patcher1 = patch.object(
            tasks.handling.executor_handler,
            "REGISTERED_EXECUTORS_JSON",
            self.json_mock,
        )
        self.addCleanup(patcher1.stop)
        self.mock_REGISTERED_EXECUTORS_JSON = patcher1.start()

        patcher2 = patch(
            "tasks.constants.configs.REGISTERED_EXECUTORS_JSON", self.json_mock
        )
        self.addCleanup(patcher2.stop)
        self.mock_REGISTERED_EXECUTORS_JSON = patcher2.start()

        patcher3 = patch(
            "tasks.handling.context_attribute_names.ContextAttrNames", AttrNamesMock
        )
        self.addCleanup(patcher3.stop)
        self.mock_variable_names = patcher3.start()

        Handler._initialize_VAR1_DIR = lambda x, y: "value1"
        Handler._initialize_VAR2_DIR = lambda x, y: "value2"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_register(self):
        executor_context = Handler.register_executor(
            self.executor_root, self.storage_subfolder, create_dirs=False
        )

        with open(self.json_mock, "r", encoding="utf-8") as f:
            registered_executors = json.load(f)

        self.assertIn(self.executor_root, registered_executors)
        self.assertEqual(registered_executors[self.executor_root], self.storage_dir)

        self.assertEqual(executor_context.VAR1_DIR, "value1")
        self.assertEqual(executor_context.VAR2_DIR, "value2")

    def test_initialize_attributes(self):
        attributes = Handler._init_executor_attributes(
            self.executor_root, self.storage_subfolder
        )

        self.assertIn("VAR1_DIR", attributes)
        self.assertIn("VAR2_DIR", attributes)

    def test_sync_directories(self):
        Handler._initialize_VAR1_DIR = lambda x, y: os.path.join(
            self.storage_dir, "value1"
        )
        Handler._initialize_VAR2_DIR = lambda x, y: os.path.join(
            self.storage_dir, "value2"
        )
        executor_context = Handler.register_executor(
            self.executor_root, self.storage_subfolder, overwrite=True, create_dirs=True
        )

        self.assertTrue(os.path.exists(executor_context.VAR1_DIR))
        self.assertTrue(os.path.exists(executor_context.VAR2_DIR))

    def test_overwrite_registration(self):
        Handler.register_executor(
            self.executor_root,
            self.storage_subfolder,
            overwrite=False,
            create_dirs=False,
        )

        with self.assertRaises(ValueError):
            Handler.register_executor(
                self.executor_root, self.storage_subfolder, overwrite=False
            )

        Handler.register_executor(
            self.executor_root,
            self.storage_subfolder,
            overwrite=True,
            create_dirs=False,
        )

        with open(self.json_mock, "r", encoding="utf-8") as f:
            registered_executors = json.load(f)

        self.assertIn(self.executor_root, registered_executors)
        self.assertEqual(registered_executors[self.executor_root], self.storage_dir)

    def test_login_executor(self):
        Handler.register_executor(
            self.executor_root, self.storage_subfolder, overwrite=True, create_dirs=False
        )

        logged_in_context = Handler.login_executor(self.executor_root, update_dirs=False)

        self.assertEqual(logged_in_context.executor_root, self.executor_root)
        self.assertEqual(logged_in_context.storage_dir, self.storage_dir)
        self.assertEqual(logged_in_context.variable_json, os.path.join(self.storage_dir, "variable.json"))
        self.assertEqual(logged_in_context.VAR1_DIR, "value1")
        self.assertEqual(logged_in_context.VAR2_DIR, "value2")

        self.assertTrue(os.path.exists(logged_in_context.VAR1_DIR))
        self.assertTrue(os.path.exists(logged_in_context.VAR2_DIR))


if __name__ == "__main__":
    unittest.main()
