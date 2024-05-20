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
    var1_dir = (1, "configs.pkl")
    var2_dir = (2, "configs.pkl")
    cwd = (3, "configs.json")
    python_env = (4, "configs.json")


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
            "tasks.constants.session_attributes.SessionAttrNames", AttrNamesMock
        )
        self.addCleanup(patcher3.stop)
        self.mock_variable_names = patcher3.start()

        Handler._initialize_var1_dir = lambda x, y: "value1"
        Handler._initialize_var2_dir = lambda x, y: "value2"
        Handler._initialize_cwd = lambda x, y: self.executor_root
        Handler._initialize_python_env = lambda x, y: os.path.join(
            self.executor_root, "python_env"
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_register(self):
        python_env_path = os.path.join(self.executor_root, "python_env")
        os.makedirs(python_env_path)

        session = Handler.register_executor(
            self.executor_root,
            python_env_path,
            storage_dir=self.storage_subfolder,
            overwrite=False,
            create_dirs=False,
        )

        with open(self.json_mock, "r", encoding="utf-8") as f:
            registered_executors = json.load(f)

        self.assertIn(self.executor_root, registered_executors)
        self.assertEqual(registered_executors[self.executor_root], self.storage_dir)

        self.assertEqual(session.var1_dir, "value1")
        self.assertEqual(session.var2_dir, "value2")
        self.assertEqual(session.cwd, self.executor_root)
        self.assertEqual(session.python_env, normalize_path(python_env_path))

    def test_initialize_attributes(self):
        python_env_path = os.path.join(self.executor_root, "python_env")
        os.makedirs(python_env_path)

        attributes = Handler._init_executor_attributes(
            self.executor_root,
            self.storage_subfolder,
            python_env_path,
            self.executor_root,
        )

        self.assertIn("var1_dir", attributes)
        self.assertIn("var2_dir", attributes)
        self.assertEqual(attributes["cwd"], self.executor_root)
        self.assertEqual(attributes["python_env"], normalize_path(python_env_path))

    def test_create_directories(self):
        Handler._initialize_var1_dir = lambda x, y: os.path.join(
            self.storage_dir, "value1"
        )
        Handler._initialize_var2_dir = lambda x, y: os.path.join(
            self.storage_dir, "value2"
        )
        python_env_path = os.path.join(self.executor_root, "python_env")
        os.makedirs(python_env_path)

        session = Handler.register_executor(
            self.executor_root,
            python_env_path,
            storage_dir=self.storage_subfolder,
            overwrite=False,
            create_dirs=True,
        )

        self.assertTrue(os.path.exists(session.var1_dir))
        self.assertTrue(os.path.exists(session.var2_dir))
        self.assertTrue(os.path.exists(session.cwd))
        self.assertTrue(os.path.exists(session.python_env))

    def test_overwrite_registration(self):
        python_env_path = os.path.join(self.executor_root, "python_env")
        os.makedirs(python_env_path)

        Handler.register_executor(
            self.executor_root,
            python_env_path,
            storage_dir=self.storage_subfolder,
            overwrite=False,
            create_dirs=False,
        )

        with self.assertRaises(ValueError):
            Handler.register_executor(
                self.executor_root,
                python_env_path,
                storage_dir=self.storage_subfolder,
                overwrite=False,
            )

        Handler.register_executor(
            self.executor_root,
            python_env_path,
            storage_dir=self.storage_subfolder,
            overwrite=True,
            create_dirs=False,
        )

        with open(self.json_mock, "r", encoding="utf-8") as f:
            registered_executors = json.load(f)

        self.assertIn(self.executor_root, registered_executors)
        self.assertEqual(registered_executors[self.executor_root], self.storage_dir)

    def test_login_executor(self):
        python_env_path = os.path.join(self.executor_root, "python_env")
        os.makedirs(python_env_path)

        Handler.register_executor(
            self.executor_root,
            python_env_path,
            storage_dir=self.storage_subfolder,
            overwrite=True,
            create_dirs=False,
        )

        session = Handler.login_executor(
            self.executor_root, update_dirs=False
        )

        self.assertEqual(session.executor_root, self.executor_root)
        self.assertEqual(session.storage_dir, self.storage_dir)
        self.assertEqual(
            session.configs_dir, os.path.join(self.storage_dir, "configs")
        )
        self.assertEqual(session.var1_dir, "value1")
        self.assertEqual(session.var2_dir, "value2")
        self.assertEqual(session.cwd, self.executor_root)
        self.assertEqual(session.python_env, normalize_path(python_env_path))


if __name__ == "__main__":
    unittest.main()
