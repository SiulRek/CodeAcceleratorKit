import unittest
from enum import Enum
import json
import os
import pickle
import tempfile
import warnings
from unittest.mock import patch

from tasks.management.task_runner_profile import TaskRunnerProfile
from tasks.management.standardize_path import standardize_path
from tasks.utils.for_testing.test_result_logger import TestResultLogger

ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
OUTPUT_DIR = os.path.join(ROOT_DIR, "tasks", "tests", "outputs")
LOG_FILE = os.path.join(OUTPUT_DIR, "test_results.log")


class AttrNamesMock(Enum):
    cwd = (1, "configs.json")
    python_env = (2, "configs.json")


class AttrNamesMockExtended(Enum):
    cwd = (1, "configs.json")
    python_env = (2, "configs.json")
    attr_3 = (3, "other_configs.json")
    attr_4 = (4, "other_configs.json")
    attr_5 = (5, "other_configs.pkl")
    attr_6 = (6, "other_configs.pkl")

class TestTaskRunnerProfile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        cls.logger = TestResultLogger(LOG_FILE)
        cls.logger.log_title("Runner Variable Test")

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.runner_root = standardize_path(
            os.path.join(self.temp_dir.name, "runner_root")
        )
        self.json_mock = standardize_path(
            os.path.join(self.temp_dir.name, "registered_variables.json")
        )

        registered_runners = {
            self.runner_root: standardize_path(
                os.path.join(self.temp_dir.name, "task_storage")
            )
        }

        with open(self.json_mock, "w", encoding="utf-8") as f:
            json.dump(registered_runners, f, indent=4)

        self.profile_dir = os.path.join(self.temp_dir.name, "task_storage", "profile")
        os.makedirs(self.profile_dir, exist_ok=True)

    def tearDown(self):
        self.logger.log_test_outcome(self._outcome.result, self._testMethodName)
        self.temp_dir.cleanup()

    def test_load_attributes_1(self):
        with patch(
            "tasks.configs.constants.REGISTERED_RUNNERS_JSON", self.json_mock
        ), patch(
            "tasks.configs.profile_attributes.ProfileAttrNames", AttrNamesMock
        ):
            profile = TaskRunnerProfile(
                self.runner_root, load_attributes_from_storage=False
            )
            with open(
                os.path.join(self.profile_dir, "configs.json"), "w", encoding="utf-8"
            ) as f:
                json.dump({"cwd": "test_dir", "python_env": "test_env"}, f, indent=4)

            profile.load_attributes_from_storage()

            self.assertEqual(profile.cwd, "test_dir")
            self.assertEqual(profile.python_env, "test_env")

    def test_load_attributes(self):
        with patch(
            "tasks.configs.constants.REGISTERED_RUNNERS_JSON", self.json_mock
        ), patch(
            "tasks.configs.profile_attributes.ProfileAttrNames", AttrNamesMock
        ):
            variable_json = TaskRunnerProfile(
                self.runner_root, load_attributes_from_storage=False
            ).profile_dir
            with open(
                os.path.join(variable_json, "configs.json"), "w", encoding="utf-8"
            ) as f:
                json.dump({"cwd": "test_dir", "python_env": "test_env"}, f, indent=4)

            profile = TaskRunnerProfile(
                self.runner_root, load_attributes_from_storage=True
            )

            self.assertEqual(profile.cwd, "test_dir")
            self.assertEqual(profile.python_env, "test_env")

    def test_load_attributes_from_dict(self):
        with patch(
            "tasks.configs.constants.REGISTERED_RUNNERS_JSON", self.json_mock
        ), patch(
            "tasks.configs.profile_attributes.ProfileAttrNames",
            AttrNamesMockExtended,
        ):
            profile = TaskRunnerProfile(
                self.runner_root, load_attributes_from_storage=False
            )
            profile.load_attributes_from_dict(
                {
                    "cwd": "test_dir",
                    "python_env": "test_env",
                    "attr_3": "value3",
                    "attr_4": "value4",
                    "attr_5": "value5",
                    "attr_6": "value6",
                }
            )

            self.assertEqual(profile.cwd, "test_dir")
            self.assertEqual(profile.python_env, "test_env")
            self.assertEqual(profile.attr_3, "value3")
            self.assertEqual(profile.attr_4, "value4")
            self.assertEqual(profile.attr_5, "value5")
            self.assertEqual(profile.attr_6, "value6")


    def test_load_attributes_from_storage_with_pickle(self):
        with patch(
            "tasks.configs.constants.REGISTERED_RUNNERS_JSON", self.json_mock
        ), patch(
            "tasks.configs.profile_attributes.ProfileAttrNames",
            AttrNamesMockExtended,
        ):
            profile = TaskRunnerProfile(
                self.runner_root, load_attributes_from_storage=False
            )

            with open(os.path.join(self.profile_dir, "other_configs.pkl"), "wb") as f:
                pickle.dump({"attr_5": "value5", "attr_6": "value6"}, f)

            profile.load_attributes_from_storage()
            self.assertEqual(profile.attr_5, "value5")
            self.assertEqual(profile.attr_6, "value6")
            
    def test_are_attributes_complete_true(self):
        with patch(
            "tasks.configs.constants.REGISTERED_RUNNERS_JSON", self.json_mock
        ), patch(
            "tasks.configs.profile_attributes.ProfileAttrNames", AttrNamesMock
        ):
            profile = TaskRunnerProfile(
                self.runner_root, load_attributes_from_storage=False
            )
            profile.load_attributes_from_dict(
                {"cwd": "test_dir", "python_env": "test_env"}
            )

            self.assertTrue(profile.are_attributes_complete())

    def test_are_attributes_complete_false(self):
        with patch(
            "tasks.configs.constants.REGISTERED_RUNNERS_JSON", self.json_mock
        ), patch(
            "tasks.configs.profile_attributes.ProfileAttrNames", AttrNamesMock
        ):
            profile = TaskRunnerProfile(
                self.runner_root, load_attributes_from_storage=False
            )
            profile.load_attributes_from_dict({"cwd": "test_dir"})

            self.assertFalse(profile.are_attributes_complete())

    def test_save_attributes(self):
        with patch(
            "tasks.configs.constants.REGISTERED_RUNNERS_JSON", self.json_mock
        ), patch(
            "tasks.configs.profile_attributes.ProfileAttrNames",
            AttrNamesMockExtended,
        ):
            profile = TaskRunnerProfile(
                self.runner_root, load_attributes_from_storage=False
            )
            profile.load_attributes_from_dict(
                {
                    "cwd": "test_dir",
                    "python_env": "test_env",
                    "attr_3": "value3",
                    "attr_4": "value4",
                    "attr_5": "value5",
                    "attr_6": "value6",
                }
            )
            profile.save_attributes()

            with open(
                os.path.join(self.profile_dir, "configs.json"), "r", encoding="utf-8"
            ) as f:
                written_cofings_json = json.load(f)

            with open(
                os.path.join(self.profile_dir, "other_configs.json"),
                "r",
                encoding="utf-8",
            ) as f:
                written_other_configs_json = json.load(f)

            with open(os.path.join(self.profile_dir, "other_configs.pkl"), "rb") as f:
                written_other_configs_pickle = pickle.load(f)

            expected_configs_json = {"cwd": "test_dir", "python_env": "test_env"}
            expected_other_configs_json = {"attr_3": "value3", "attr_4": "value4"}
            expected_other_configs_pickle = {"attr_5": "value5", "attr_6": "value6"}

            self.assertEqual(written_cofings_json, expected_configs_json)
            self.assertEqual(written_other_configs_json, expected_other_configs_json)
            self.assertEqual(
                written_other_configs_pickle, expected_other_configs_pickle
            )

    def test_save_attributes_with_unknown_file(self):
        with patch(
            "tasks.configs.constants.REGISTERED_RUNNERS_JSON", self.json_mock
        ), patch(
            "tasks.configs.profile_attributes.ProfileAttrNames",
            AttrNamesMockExtended,
        ):
            profile = TaskRunnerProfile(
                self.runner_root, load_attributes_from_storage=False
            )
            profile.load_attributes_from_dict(
                {
                    "cwd": "test_dir",
                    "python_env": "test_env",
                    "attr_3": "value3",
                    "attr_4": "value4",
                    "attr_5": "value5",
                    "attr_6": "value6",
                }
            )

            unknown_file_path = os.path.join(self.profile_dir, "unknown_file.txt")
            with open(unknown_file_path, "w", encoding="utf-8") as f:
                f.write("This is an unknown file.")

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                profile.save_attributes()

                self.assertTrue(any(item.category == UserWarning for item in w))
                self.assertTrue(
                    any("unknown_file.txt" in str(item.message) for item in w)
                )

            self.assertTrue(os.path.exists(unknown_file_path))

    def test_get_attribute_copy(self):
        with patch(
            "tasks.configs.constants.REGISTERED_RUNNERS_JSON", self.json_mock
        ), patch(
            "tasks.configs.profile_attributes.ProfileAttrNames", AttrNamesMock
        ):
            profile = TaskRunnerProfile(
                self.runner_root, load_attributes_from_storage=False
            )
            profile.set_attribute("cwd", ["list", "of", "values"])
            copied_value = profile.get_attribute_copy("cwd")
            copied_value[1] = "changed"
            self.assertNotEqual(copied_value, profile.cwd)

    def test_clear_attributes(self):
        with patch(
            "tasks.configs.constants.REGISTERED_RUNNERS_JSON", self.json_mock
        ), patch(
            "tasks.configs.profile_attributes.ProfileAttrNames", AttrNamesMock
        ):
            profile = TaskRunnerProfile(
                self.runner_root, load_attributes_from_storage=False
            )
            profile.set_attribute("cwd", "test_dir")
            profile.set_attribute("python_env", "test_env")
            self.assertTrue(hasattr(profile, "cwd"))
            self.assertTrue(hasattr(profile, "python_env"))
            self.assertEqual(profile._all_attributes, {"cwd": "test_dir", "python_env": "test_env"})

            profile.clear_attributes()

            self.assertFalse(hasattr(profile, "cwd"))
            self.assertFalse(hasattr(profile, "python_env"))
            self.assertEqual(profile._all_attributes, {})

    def test_update_attributes(self):
        UpdateMappingMock = {
            "cwd": "old_cwd",
            "python_env": "old_python_env",
            "attr_3": "old_attr_3",
            "attr_4": None,
        }
        with patch(
            "tasks.configs.constants.REGISTERED_RUNNERS_JSON", self.json_mock
        ), patch(
            "tasks.configs.profile_attributes.ProfileAttrNames", AttrNamesMockExtended
        ), patch(
            "tasks.configs.profile_attributes.UPDATE_MAPPING", UpdateMappingMock
        ):
            profile = TaskRunnerProfile(
                self.runner_root, load_attributes_from_storage=False
            )
            profile.load_attributes_from_dict(
                {
                    "old_cwd": "test_dir",
                    "old_python_env": "test_env",
                    "old_attr_3": "value3",
                }
            )

            reinitialized_attrs = {
                "cwd": "new_test_dir",
                "python_env": "new_test_env",
                "attr_3": "new_value3",
                "attr_4": "new_value4",
            }

            # Test with prioritize_old_values=True
            profile.update_attributes(reinitialized_attrs)
            self.assertFalse(hasattr(profile, "old_cwd"))
            self.assertFalse(hasattr(profile, "old_python_env"))
            self.assertFalse(hasattr(profile, "old_attr_3"))
            self.assertEqual(profile.cwd, "test_dir")
            self.assertEqual(profile.python_env, "test_env")
            self.assertEqual(profile.attr_3, "value3")
            self.assertEqual(profile.attr_4, "new_value4")


if __name__ == "__main__":
    unittest.main()
