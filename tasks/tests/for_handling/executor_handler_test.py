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
        self.room_subfolder = "task_room"
        self.room_dir = os.path.join(self.executor_root, self.room_subfolder)
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

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_register(self):
        Handler._initialize_VAR1_DIR = lambda x, y: "value1"
        Handler._initialize_VAR2_DIR = lambda x, y: "value2"
        executor_context = Handler.register_executor(
            self.executor_root, self.room_subfolder, create_dirs=False
        )

        with open(self.json_mock, "r", encoding="utf-8") as f:
            registered_executors = json.load(f)

        self.assertIn(self.executor_root, registered_executors)
        self.assertEqual(registered_executors[self.executor_root], self.room_dir)

        self.assertEqual(executor_context.VAR1_DIR, "value1")
        self.assertEqual(executor_context.VAR2_DIR, "value2")

    def test_initialize_attributes(self):
        Handler._initialize_VAR1_DIR = lambda x, y: "value1"
        Handler._initialize_VAR2_DIR = lambda x, y: "value2"
        attributes = Handler._init_executor_attributes(
            self.executor_root, self.room_subfolder
        )

        self.assertIn("VAR1_DIR", attributes)
        self.assertIn("VAR2_DIR", attributes)

    def test_create_directories(self):
        Handler._initialize_VAR1_DIR = lambda x, y: os.path.join(
            self.room_dir, "value1"
        )
        Handler._initialize_VAR2_DIR = lambda x, y: os.path.join(
            self.room_dir, "value2"
        )
        executor_context = Handler.register_executor(
            self.executor_root, self.room_subfolder, overwrite=True, create_dirs=True
        )

        self.assertTrue(os.path.exists(executor_context.VAR1_DIR))
        self.assertTrue(os.path.exists(executor_context.VAR2_DIR))

    def test_overwrite_registration(self):
        Handler._initialize_VAR1_DIR = lambda x, y: "value1"
        Handler._initialize_VAR2_DIR = lambda x, y: "value2"
        Handler.register_executor(
            self.executor_root, self.room_subfolder, overwrite=False, create_dirs=False
        )

        with self.assertRaises(ValueError):
            Handler.register_executor(self.executor_root, self.room_subfolder, overwrite=False)

        Handler.register_executor(
            self.executor_root, self.room_subfolder, overwrite=True, create_dirs=False
        )

        with open(self.json_mock, "r", encoding="utf-8") as f:
            registered_executors = json.load(f)

        self.assertIn(self.executor_root, registered_executors)
        self.assertEqual(registered_executors[self.executor_root], self.room_dir)


if __name__ == "__main__":
    unittest.main()
