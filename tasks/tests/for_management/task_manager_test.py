from enum import Enum
import json
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import warnings

import tasks
from tasks.tasks.management.normalize_path import normalize_path
from tasks.tasks.management.task_manager import TaskManager as Manager
from tasks.tasks.management.task_session import TaskSession

class AttrNamesMock(Enum):
    var1_dir = (1, "configs.pkl")
    var2_dir = (2, "configs.pkl")
    cwd = (3, "configs.json")
    runner_python_env = (4, "configs.json")

class AttrNamesMockOld(Enum):
    old_var1_dir = (1, "configs.pkl")
    old_var2_dir = (2, "configs.pkl")
    cwd = (3, "configs.json")
    runner_python_env = (4, "configs.json")


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.runner_root = normalize_path(
            os.path.join(self.temp_dir.name, "runner_root")
        )
        self.storage_subfolder = "task_storage"
        self.storage_dir = os.path.join(self.runner_root, self.storage_subfolder)
        self.json_mock = normalize_path(
            os.path.join(self.temp_dir.name, "registered_variables.json")
        )
        patcher1 = patch.object(
            tasks.tasks.management.task_manager,
            "REGISTERED_RUNNERS_JSON",
            self.json_mock,
        )
        self.addCleanup(patcher1.stop)
        self.mock_REGISTERED_RUNNERS_JSON = patcher1.start()

        patcher2 = patch(
            "tasks.configs.constants.REGISTERED_RUNNERS_JSON", self.json_mock
        )
        self.addCleanup(patcher2.stop)
        self.mock_REGISTERED_RUNNERS_JSON = patcher2.start()

        patcher3 = patch(
            "tasks.configs.session_attributes.SessionAttrNames", AttrNamesMock
        )
        self.addCleanup(patcher3.stop)
        self.mock_variable_names = patcher3.start()

        patcher4 = patch(
            "tasks.tasks.management.task_manager.Attributes.AttributesInitializer",
            new_callable=MagicMock,
        )
        self.addCleanup(patcher4.stop)
        self.mock_attributes_initializer = patcher4.start()

        Manager._initialize_var1_dir = lambda primary_attrs: os.path.join(
            primary_attrs["storage_dir"], "value1"
        )
        Manager._initialize_var2_dir = lambda primary_attrs: os.path.join(
            primary_attrs["storage_dir"], "value2"
        )
        Manager._initialize_cwd = lambda primary_attrs: primary_attrs["runner_root"]
        Manager._initialize_runner_python_env = lambda primary_attrs: primary_attrs[
            "runner_python_env"
        ]

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_register(self):
        python_env_path = os.path.join(self.runner_root, "runner_python_env")
        os.makedirs(python_env_path)

        session = Manager.register_runner(
            self.runner_root,
            python_env_path,
            storage_dir=self.storage_subfolder,
            overwrite=False,
            create_dirs=False,
        )

        with open(self.json_mock, "r", encoding="utf-8") as f:
            registered_runners = json.load(f)

        self.assertIn(self.runner_root, registered_runners)
        self.assertEqual(registered_runners[self.runner_root], self.storage_dir)

        self.assertEqual(session.var1_dir, os.path.join(self.storage_dir, "value1"))
        self.assertEqual(session.var2_dir, os.path.join(self.storage_dir, "value2"))
        self.assertEqual(session.cwd, self.runner_root)
        self.assertEqual(session.runner_python_env, normalize_path(python_env_path))

    def test_initialize_attributes(self):
        python_env_path = os.path.join(self.runner_root, "runner_python_env")
        os.makedirs(python_env_path)

        attributes = Manager._init_runner_attributes(
            self.runner_root,
            self.storage_subfolder,
            python_env_path,
            self.runner_root,
        )

        self.assertIn("var1_dir", attributes)
        self.assertIn("var2_dir", attributes)
        self.assertEqual(attributes["cwd"], self.runner_root)
        self.assertEqual(
            attributes["runner_python_env"], normalize_path(python_env_path)
        )

    def test_create_directories(self):
        python_env_path = os.path.join(self.runner_root, "runner_python_env")
        os.makedirs(python_env_path)

        session = Manager.register_runner(
            self.runner_root,
            python_env_path,
            storage_dir=self.storage_subfolder,
            overwrite=False,
            create_dirs=True,
        )

        self.assertTrue(os.path.exists(session.var1_dir))
        self.assertTrue(os.path.exists(session.var2_dir))
        self.assertTrue(os.path.exists(session.cwd))
        self.assertTrue(os.path.exists(session.runner_python_env))

    def test_sync_directories_of(self):
        with patch.object(Manager, "sync_directories_of") as mock_sync:
            python_env_path = os.path.join(self.runner_root, "runner_python_env")
            os.makedirs(python_env_path)

            Manager.register_runner(
                self.runner_root,
                python_env_path,
                storage_dir=self.storage_subfolder,
                overwrite=False,
                create_dirs=True,
            )

            mock_sync.assert_called_once_with(self.runner_root)

    def test_detect_unknown_directories(self):
        python_env_path = os.path.join(self.runner_root, "runner_python_env")
        os.makedirs(python_env_path)
        os.makedirs(self.storage_dir)

        unknown_dir = os.path.join(self.storage_dir, "unknown_dir")
        os.makedirs(unknown_dir)

        Manager._initialize_var1_dir = lambda primary_attrs: os.path.join(
            primary_attrs["storage_dir"], "value1"
        )
        Manager._initialize_var2_dir = lambda primary_attrs: os.path.join(
            primary_attrs["storage_dir"], "value2"
        )
        Manager.register_runner(
            self.runner_root,
            python_env_path,
            storage_dir=self.storage_subfolder,
            overwrite=False,
            create_dirs=False,
        )
        with patch("warnings.warn") as mock_warn:
            Manager.sync_directories_of(self.runner_root)
            mock_warn.assert_called_with(
                f"Unknown directory {normalize_path(unknown_dir)} from tasks storage."
            )

    def test_overwrite_registration(self):
        python_env_path = os.path.join(self.runner_root, "runner_python_env")
        os.makedirs(python_env_path)

        Manager.register_runner(
            self.runner_root,
            python_env_path,
            storage_dir=self.storage_subfolder,
            overwrite=False,
            create_dirs=False,
        )

        with self.assertRaises(ValueError):
            Manager.register_runner(
                self.runner_root,
                python_env_path,
                storage_dir=self.storage_subfolder,
                overwrite=False,
            )

        Manager.register_runner(
            self.runner_root,
            python_env_path,
            storage_dir=self.storage_subfolder,
            overwrite=True,
            create_dirs=False,
        )

        with open(self.json_mock, "r", encoding="utf-8") as f:
            registered_runners = json.load(f)

        self.assertIn(self.runner_root, registered_runners)
        self.assertEqual(registered_runners[self.runner_root], self.storage_dir)

    def test_login_runner(self):
        python_env_path = os.path.join(self.runner_root, "runner_python_env")
        os.makedirs(python_env_path)

        Manager.register_runner(
            self.runner_root,
            python_env_path,
            storage_dir=self.storage_subfolder,
            overwrite=True,
            create_dirs=False,
        )

        session = Manager.login_runner(self.runner_root, update_dirs=False)

        self.assertEqual(session.root, self.runner_root)
        self.assertEqual(session.storage_dir, self.storage_dir)
        self.assertEqual(session.configs_dir, os.path.join(self.storage_dir, "configs"))
        self.assertEqual(session.var1_dir, os.path.join(self.storage_dir, "value1"))
        self.assertEqual(session.var2_dir, os.path.join(self.storage_dir, "value2"))
        self.assertEqual(session.cwd, self.runner_root)
        self.assertEqual(session.runner_python_env, normalize_path(python_env_path))

    def test_delete_runner(self):
        python_env_path = os.path.join(self.runner_root, "runner_python_env")
        os.makedirs(python_env_path)

        Manager.register_runner(
            self.runner_root,
            python_env_path,
            storage_dir=self.storage_subfolder,
            overwrite=False,
            create_dirs=True,
        )

        with open(self.json_mock, "r", encoding="utf-8") as f:
            registered_runners = json.load(f)
        self.assertIn(self.runner_root, registered_runners)

        self.assertTrue(os.path.exists(self.storage_dir))

        Manager.delete_runner(self.runner_root)

        with open(self.json_mock, "r", encoding="utf-8") as f:
            registered_runners = json.load(f)
        self.assertNotIn(self.runner_root, registered_runners)

        self.assertFalse(os.path.exists(self.storage_dir))

    def test_copy_data_files(self):
        source_runner_dir = os.path.join(self.temp_dir.name, "source_runner")
        os.makedirs(source_runner_dir)

        dest_runner_dir = os.path.join(self.temp_dir.name, "dest_runner")
        os.makedirs(dest_runner_dir)

        source_data_dir = os.path.join(source_runner_dir, "data")
        os.makedirs(source_data_dir)
        source_file_path = os.path.join(source_data_dir, "example_file.txt")
        with open(source_file_path, "w") as file:
            file.write("Sample data")

        dest_data_dir = os.path.join(dest_runner_dir, "data")
        os.makedirs(dest_data_dir)

        with patch("tasks.tasks.management.task_manager.TaskSession") as MockSession:
            mock_source_session = MagicMock()
            mock_source_session.data_dir = source_data_dir
            mock_source_session.var1_dir = source_data_dir
            mock_source_session.var2_dir = source_data_dir

            mock_dest_session = MagicMock()
            mock_dest_session.var1_dir = dest_data_dir
            mock_dest_session.var2_dir = dest_data_dir

            MockSession.side_effect = [mock_source_session, mock_dest_session]

            Manager().copy_data_files(source_runner_dir, dest_runner_dir)

        dest_file_path = os.path.join(dest_data_dir, "example_file.txt")
        self.assertTrue(os.path.isfile(dest_file_path))
        with open(dest_file_path, "r") as file:
            content = file.read()
            self.assertEqual(content, "Sample data")

    def test_update_runner(self):
        with patch(
            "tasks.configs.constants.REGISTERED_RUNNERS_JSON", self.json_mock
        ):
            python_env_path = os.path.join(self.runner_root, "runner_python_env")
            os.makedirs(python_env_path)

            Manager.register_runner(
                self.runner_root,
                python_env_path,
                storage_dir=self.storage_subfolder,
                overwrite=False,
                create_dirs=False,
            )

            with patch(
                "tasks.configs.session_attributes.SessionAttrNames", AttrNamesMockOld
            ):
                session = TaskSession(self.runner_root, load_attributes_from_storage=False)
                old_value1 = os.path.join(self.storage_dir, "old_value1")
                session.load_attributes_from_dict(
                    {
                        "old_var1_dir": old_value1,
                        "old_var2_dir": "old_value2",
                        "cwd": "old_cwd",
                        "runner_python_env": "old_python_env",
                    }
                )
                session.save_attributes()

            new_value2 = os.path.join(self.storage_dir, "new_value2")
            reinit_attrs = {
                "var1_dir": "new_value1",
                "var2_dir": new_value2,
                "cwd": self.runner_root,
                "runner_python_env": python_env_path,
            }
            new_value2 = os.path.join(self.storage_dir, "new_value2")
            update_mapping = {
                "var1_dir": "old_var1_dir",
                "var2_dir": None,
                "cwd": "cwd",
                "runner_python_env": "runner_python_env",
            }
            with patch.object(Manager, "_init_runner_attributes", return_value=reinit_attrs), patch(
            "tasks.configs.session_attributes.UPDATE_MAPPING", update_mapping
            ), patch("tasks.configs.session_attributes.SessionAttrNames", AttrNamesMock):
                Manager().update_runner(self.runner_root)
                updated_session = TaskSession(self.runner_root, load_attributes_from_storage=True)
                self.assertEqual(updated_session.var1_dir, old_value1)
                self.assertEqual(updated_session.var2_dir, new_value2)
                self.assertEqual(updated_session.cwd, "old_cwd")
                self.assertEqual(updated_session.runner_python_env, "old_python_env")
                self.assertFalse(hasattr(updated_session, "old_var1_dir"))
                self.assertFalse(hasattr(updated_session, "old_var2_dir"))
                self.assertTrue(os.path.exists(old_value1))
                self.assertTrue(os.path.exists(new_value2))


if __name__ == "__main__":
    unittest.main()
