import os
import shutil
import sys
import tempfile
import unittest

from tasks.configs.constants import CURRENT_DIRECTORY_TAG
from tasks.utils.shared.find_closest_matching_dir import find_closest_matching_dir

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))


class TestFindClosestMatchingDir(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

        os.makedirs(os.path.join(self.temp_dir, "project1/module/data/logs"))
        os.makedirs(os.path.join(self.temp_dir, "project1/module/cache"))
        os.makedirs(os.path.join(self.temp_dir, "project2/module/data/logs"))
        os.makedirs(os.path.join(self.temp_dir, "project2/module/code/helpers"))

        self.root_dir = self.temp_dir

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_exact_name_single_match_1(self):
        name = "cache"
        reference_dir = os.path.join(self.root_dir, "project2/module")
        result = find_closest_matching_dir(name, self.root_dir, reference_dir)
        self.assertTrue(result.endswith("project1/module/cache"))

    def test_exact_name_single_match_2(self):
        name = "cache"
        reference_dir = os.path.join(self.root_dir, "project1")
        result = find_closest_matching_dir(name, self.root_dir, reference_dir)
        self.assertTrue(result.endswith("project1/module/cache"))

    def test_exact_name_single_match_3(self):
        name = "cache"
        reference_dir = os.path.join(self.root_dir, "project2/module")
        result = find_closest_matching_dir(name, self.root_dir, reference_dir)
        self.assertTrue(result.endswith("project1/module/cache"))

    def test_exact_fragment_single_match_1(self):
        fragment = "module/cache"
        reference_dir = os.path.join(self.temp_dir, "project2/module")
        result = find_closest_matching_dir(fragment, self.root_dir, reference_dir)
        self.assertTrue(result.endswith("module/cache"))

    def test_exact_fragment_single_match_2(self):
        fragment = "module/cache"
        reference_dir = os.path.join(self.root_dir, "project1/module")
        result = find_closest_matching_dir(fragment, self.root_dir, reference_dir)
        self.assertTrue(result.endswith("module/cache"))

    def test_name_multiple_matches_choose_closest_1(self):
        fragment = "logs"
        reference_dir = os.path.join(self.root_dir, "project2/module")
        result = find_closest_matching_dir(fragment, self.root_dir, reference_dir)
        self.assertTrue(result.endswith("project2/module/data/logs"))

    def test_name_multiple_matches_choose_closest_2(self):
        fragment = "logs"
        reference_dir = os.path.join(self.root_dir, "project1")
        result = find_closest_matching_dir(fragment, self.root_dir, reference_dir)
        self.assertTrue(result.endswith("project1/module/data/logs"))

    def test_fragment_multiple_matches_choose_closest_1(self):
        fragment = "data/logs"
        reference_dir = os.path.join(self.root_dir, "project2/module")
        result = find_closest_matching_dir(fragment, self.root_dir, reference_dir)
        self.assertTrue(result.endswith("project2/module/data/logs"))

    def test_fragment_multiple_matches_choose_closest_2(self):
        fragment = "data/logs"
        reference_dir = os.path.join(self.root_dir, "project1")
        result = find_closest_matching_dir(fragment, self.root_dir, reference_dir)
        self.assertTrue(result.endswith("project1/module/data/logs"))

    def test_reference_is_file(self):
        file_path = os.path.join(self.root_dir, "project1/module/cache/file.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("test")
        partial_path = "cache"
        result = find_closest_matching_dir(partial_path, self.root_dir, file_path)
        self.assertTrue(result.endswith("project1/module/cache"))

    def test_name_is_dot(self):
        name = "."
        reference_dir = os.path.join(self.root_dir, "project1/module")
        result = find_closest_matching_dir(name, self.root_dir, reference_dir)
        self.assertEqual(result, os.path.abspath(name))

    def test_name_is_dir_tag(self):
        name = CURRENT_DIRECTORY_TAG
        reference_dir = os.path.join(self.root_dir, "project1/module")
        result = find_closest_matching_dir(name, self.root_dir, reference_dir)
        self.assertEqual(result, os.path.abspath(reference_dir))

    def test_name_has_dir_tag(self):
        name = f"{CURRENT_DIRECTORY_TAG}/../project2"
        reference_dir = os.path.join(self.root_dir, "project1")
        result = find_closest_matching_dir(name, self.root_dir, reference_dir)
        expected_path = os.path.abspath(os.path.join(self.root_dir, "project2"))
        self.assertEqual(result, expected_path)

    def test_nonexistent_name_raises(self):
        with self.assertRaises(NotADirectoryError):
            find_closest_matching_dir("unknown", self.root_dir, self.root_dir)

    def test_nonexistent_fragment_raises(self):
        with self.assertRaises(NotADirectoryError):
            find_closest_matching_dir("unknown/fragment", self.root_dir, self.root_dir)

    def test_ambiguous_match_raises(self):
        reference_dir = os.path.join(self.root_dir, "other/unrelated")
        os.makedirs(reference_dir, exist_ok=True)
        with self.assertRaises(ValueError):
            find_closest_matching_dir("logs", self.root_dir, reference_dir)

    def test_match_not_in_root_dir_raises(self):
        with self.assertRaises(NotADirectoryError):
            find_closest_matching_dir("unknown", "/nonexistent/root", self.root_dir)


if __name__ == "__main__":
    unittest.main()
