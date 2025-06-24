from enum import Enum
import json
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import warnings

import tasks
from tasks.management.standardize_path import standardize_path
from tasks.management.task_manager import TaskManager as Manager
from tasks.management.task_runner_profile import TaskRunnerProfile

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
        self.runner_root = standardize_path(
            os.path.join(self.temp_dir.name, "runner_root")
        )
        self.storage_dir = os.path.join(self.runner_root, "task_storage")
        self.json_mock = standardize_path(
            os.path.join(self.temp_dir.name, "registered_variables.json")
        )
        patcher1 = patch.object(
            tasks.management.task_manager,
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
            "tasks.configs.profile_attributes.ProfileAttrNames", AttrNamesMock
        )
        self.addCleanup(patcher3.stop)
        self.mock_variable_names = patcher3.start()

        patcher4 = patch(
            "tasks.management.task_manager.Attributes.AttributesInitializer",
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

        profile = Manager.register_runner(
            self.runner_root,
            python_env_path,
            storage_dir=self.storage_dir,
            overwrite=False,
            create_dirs=False,
        )

        with open(self.json_mock, "r", encoding="utf-8") as f:
            registered_runners = json.load(f)

        self.assertIn(self.runner_root, registered_runners)
        self.assertEqual(registered_runners[self.runner_root], self.storage_dir)

        self.assertEqual(profile.var1_dir, os.path.join(self.storage_dir, "value1"))
        self.assertEqual(profile.var2_dir, os.path.join(self.storage_dir, "value2"))
        self.assertEqual(profile.cwd, self.runner_root)
        self.assertEqual(profile.runner_python_env, standardize_path(python_env_path))

    def test_initialize_attributes(self):
        python_env_path = os.path.join(self.runner_root, "runner_python_env")
        os.makedirs(python_env_path)

        attributes = Manager._init_runner_attributes(
            self.runner_root,
            self.storage_dir,
            python_env_path,
            self.runner_root,
        )

        self.assertIn("var1_dir", attributes)
        self.assertIn("var2_dir", attributes)
        self.assertEqual(attributes["cwd"], self.runner_root)
        self.assertEqual(
            attributes["runner_python_env"], standardize_path(python_env_path)
        )

    def test_create_directories(self):
        python_env_path = os.path.join(self.runner_root, "runner_python_env")
        os.makedirs(python_env_path)

        profile = Manager.register_runner(
            self.runner_root,
            python_env_path,
            storage_dir=self.storage_dir,
            overwrite=False,
            create_dirs=True,
        )

        self.assertTrue(os.path.exists(profile.var1_dir))
        self.assertTrue(os.path.exists(profile.var2_dir))
        self.assertTrue(os.path.exists(profile.cwd))
        self.assertTrue(os.path.exists(profile.runner_python_env))

    def test_sync_directories_of(self):
        with patch.object(Manager, "sync_directories_of") as mock_sync:
            python_env_path = os.path.join(self.runner_root, "runner_python_env")
            os.makedirs(python_env_path)

            Manager.register_runner(
                self.runner_root,
                python_env_path,
                storage_dir=self.storage_dir,
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
            storage_dir=self.storage_dir,
            overwrite=False,
            create_dirs=False,
        )
        with patch("warnings.warn") as mock_warn:
            Manager.sync_directories_of(self.runner_root)
            mock_warn.assert_called_with(
                f"Unknown directory {standardize_path(unknown_dir)} from tasks storage."
            )

    def test_overwrite_registration(self):
        python_env_path = os.path.join(self.runner_root, "runner_python_env")
        os.makedirs(python_env_path)

        Manager.register_runner(
            self.runner_root,
            python_env_path,
            storage_dir=self.storage_dir,
            overwrite=False,
            create_dirs=False,
        )

        with self.assertRaises(ValueError):
            Manager.register_runner(
                self.runner_root,
                python_env_path,
                storage_dir=self.storage_dir,
                overwrite=False,
            )

        Manager.register_runner(
            self.runner_root,
            python_env_path,
            storage_dir=self.storage_dir,
            overwrite=True,
            create_dirs=False,
        )

        with open(self.json_mock, "r", encoding="utf-8") as f:
            registered_runners = json.load(f)

        self.assertIn(self.runner_root, registered_runners)
        self.assertEqual(registered_runners[self.runner_root], self.storage_dir)

    def test_is_runner_registered(self):
        with open(self.json_mock, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)

        self.assertFalse(Manager.is_runner_registered(self.runner_root))

        python_env_path = os.path.join(self.runner_root, "runner_python_env")
        os.makedirs(python_env_path)

        Manager.register_runner(
            self.runner_root,
            python_env_path,
            storage_dir=self.storage_dir,
            overwrite=False,
            create_dirs=False,
        )

        self.assertTrue(Manager.is_runner_registered(self.runner_root))

    def test_is_runner_registered_with_error(self):
        with open(self.json_mock, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)
        with self.assertRaises(ValueError):
            Manager.is_runner_registered(self.runner_root, raise_error=True)

    def test_login_runner(self):
        python_env_path = os.path.join(self.runner_root, "runner_python_env")
        os.makedirs(python_env_path)

        Manager.register_runner(
            self.runner_root,
            python_env_path,
            storage_dir=self.storage_dir,
            overwrite=True,
            create_dirs=False,
        )

        profile = Manager.login_runner(self.runner_root, update_dirs=False)

        self.assertEqual(profile.root, self.runner_root)
        self.assertEqual(profile.storage_dir, self.storage_dir)
        self.assertEqual(profile.profile_dir, os.path.join(self.storage_dir, "profile"))
        self.assertEqual(profile.var1_dir, os.path.join(self.storage_dir, "value1"))
        self.assertEqual(profile.var2_dir, os.path.join(self.storage_dir, "value2"))
        self.assertEqual(profile.cwd, self.runner_root)
        self.assertEqual(profile.runner_python_env, standardize_path(python_env_path))

    def test_delete_runner(self):
        python_env_path = os.path.join(self.runner_root, "runner_python_env")
        os.makedirs(python_env_path)

        Manager.register_runner(
            self.runner_root,
            python_env_path,
            storage_dir=self.storage_dir,
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

    def test_copy_costumizations_files(self):
        source_runner_dir = os.path.join(self.temp_dir.name, "source_runner")
        os.makedirs(source_runner_dir)

        dest_runner_dir = os.path.join(self.temp_dir.name, "dest_runner")
        os.makedirs(dest_runner_dir)

        source_costumizations_dir = os.path.join(source_runner_dir, "costumizations")
        os.makedirs(source_costumizations_dir)
        source_file_path = os.path.join(source_costumizations_dir, "example_dir", "example_file.txt")
        os.makedirs(os.path.dirname(source_file_path))
        with open(source_file_path, "w") as file:
            file.write("Sample costumizations")

        dest_costumizations_dir = os.path.join(dest_runner_dir, "costumizations")
        os.makedirs(dest_costumizations_dir)

        with patch("tasks.management.task_manager.TaskRunnerProfile") as MockProfile, patch.object(Manager, 'is_runner_registered', return_value=True):
            mock_source_profile = MagicMock()
            mock_source_profile.costumizations_dir = source_costumizations_dir
            mock_source_profile.root = source_runner_dir
            mock_source_profile.var1_dir = source_costumizations_dir
            mock_source_profile.var2_dir = source_costumizations_dir

            mock_dest_profile = MagicMock()
            mock_dest_profile.costumizations_dir = dest_costumizations_dir
            mock_dest_profile.root = dest_runner_dir
            mock_dest_profile.var1_dir = dest_costumizations_dir
            mock_dest_profile.var2_dir = dest_costumizations_dir

            MockProfile.side_effect = [mock_source_profile, mock_dest_profile]

            Manager().copy_costumizations_files(source_runner_dir, dest_runner_dir)

        dest_file_path = os.path.join(dest_costumizations_dir, "example_dir", "example_file.txt")
        self.assertTrue(os.path.isfile(dest_file_path))
        with open(dest_file_path, "r") as file:
            content = file.read()
            self.assertEqual(content, "Sample costumizations")

    def test_update_runner(self):
        with patch(
            "tasks.configs.constants.REGISTERED_RUNNERS_JSON", self.json_mock
        ):
            python_env_path = os.path.join(self.runner_root, "runner_python_env")
            os.makedirs(python_env_path)

            Manager.register_runner(
                self.runner_root,
                python_env_path,
                storage_dir=self.storage_dir,
                overwrite=False,
                create_dirs=False,
            )

            with patch(
                "tasks.configs.profile_attributes.ProfileAttrNames", AttrNamesMockOld
            ):
                profile = TaskRunnerProfile(self.runner_root, load_attributes_from_storage=False)
                old_value1 = os.path.join(self.storage_dir, "old_value1")
                profile.load_attributes_from_dict(
                    {
                        "old_var1_dir": old_value1,
                        "old_var2_dir": "old_value2",
                        "cwd": "old_cwd",
                        "runner_python_env": "old_python_env",
                    }
                )
                profile.save_attributes()

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
            "tasks.configs.profile_attributes.UPDATE_MAPPING", update_mapping
            ), patch("tasks.configs.profile_attributes.ProfileAttrNames", AttrNamesMock):
                Manager().update_runner(self.runner_root)
                updated_profile = TaskRunnerProfile(self.runner_root, load_attributes_from_storage=True)
                self.assertEqual(updated_profile.var1_dir, old_value1)
                self.assertEqual(updated_profile.var2_dir, new_value2)
                self.assertEqual(updated_profile.cwd, "old_cwd")
                self.assertEqual(updated_profile.runner_python_env, "old_python_env")
                self.assertFalse(hasattr(updated_profile, "old_var1_dir"))
                self.assertFalse(hasattr(updated_profile, "old_var2_dir"))
                self.assertTrue(os.path.exists(old_value1))
                self.assertTrue(os.path.exists(new_value2))


if __name__ == "__main__":
    unittest.main()
