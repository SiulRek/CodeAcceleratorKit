import os
import shutil
import sys
import tempfile
import unittest

from tasks.configs.constants import CURRENT_FILE_TAG
from tasks.utils.shared.find_closest_matching_file import find_closest_matching_file

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))


class TestFindClosestMatchingFile(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

        os.makedirs(os.path.join(self.temp_dir, "project1/module/data"))
        os.makedirs(os.path.join(self.temp_dir, "project1/module/test"))
        os.makedirs(os.path.join(self.temp_dir, "project2/module/data"))
        os.makedirs(os.path.join(self.temp_dir, "project2/module/test"))

        # Create test files
        self.file1 = os.path.join(self.temp_dir, "project1/module/data", "main.py")
        self.file2 = os.path.join(self.temp_dir, "project2/module/data", "main.py")
        self.test_file = os.path.join(self.temp_dir, "project1/module/test", "main_test.py")

        with open(self.file1, "w", encoding="utf-8") as f:
            f.write("print('file1')")

        with open(self.file2, "w", encoding="utf-8") as f:
            f.write("print('file2')")

        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("print('test_file')")

        self.root_dir = self.temp_dir

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_exact_name_single_match(self):
        reference = os.path.join(self.temp_dir, "project1/module")
        result = find_closest_matching_file("main_test.py", self.root_dir, reference)
        self.assertTrue(result.endswith("project1/module/test/main_test.py"))

    def test_exact_name_multiple_matches_choose_closest(self):
        reference = os.path.join(self.temp_dir, "project2/module")
        result = find_closest_matching_file("main.py", self.root_dir, reference)
        self.assertTrue(result.endswith("project2/module/data/main.py"))

    def test_exact_fragment_single_match(self):
        fragment = os.path.join("test", "main_test.py")
        reference = os.path.join(self.temp_dir, "project2/module")
        result = find_closest_matching_file(fragment, self.root_dir, reference)
        self.assertTrue(result.endswith("project1/module/test/main_test.py"))

    def test_fragment_multiple_matches_choose_closest(self):
        fragment = os.path.join("data", "main.py")
        reference = os.path.join(self.temp_dir, "project2/module")
        result = find_closest_matching_file(fragment, self.root_dir, reference)
        self.assertTrue(result.endswith("project2/module/data/main.py"))

    def test_current_file_tag_returns_reference(self):
        reference = os.path.join(self.temp_dir, "project1/module/data", "main.py")
        result = find_closest_matching_file(CURRENT_FILE_TAG, self.root_dir, reference)
        self.assertEqual(result, os.path.abspath(reference))

    def test_source_tag_resolves_to_source(self):
        test_path = os.path.join(self.temp_dir, "project1/module/test", "main_test.py")
        result = find_closest_matching_file(CURRENT_FILE_TAG + "S", self.root_dir, test_path)
        self.assertTrue(result.endswith("project1/module/data/main.py"))

    def test_test_tag_resolves_to_test(self):
        source_path = os.path.join(self.temp_dir, "project1/module/data", "main.py")
        result = find_closest_matching_file(CURRENT_FILE_TAG + "T", self.root_dir, source_path)
        self.assertTrue(result.endswith("project1/module/test/main_test.py"))

    def test_nonexistent_file_raises(self):
        reference = os.path.join(self.temp_dir, "project1/module")
        with self.assertRaises(FileNotFoundError):
            find_closest_matching_file("nonexistent.py", self.root_dir, reference)

    def test_nonexistent_fragment_raises(self):
        reference = os.path.join(self.temp_dir, "project1/module")
        with self.assertRaises(FileNotFoundError):
            find_closest_matching_file("no/fragment.py", self.root_dir, reference)

    def test_ambiguous_match_unresolvable(self):
        unrelated = os.path.join(self.temp_dir, "project3/unrelated")
        os.makedirs(unrelated)
        reference = os.path.join(unrelated, "somefile.txt")
        with open(reference, "w", encoding="utf-8") as f:
            f.write("ref")

        with self.assertRaises(ValueError):
            find_closest_matching_file("main.py", self.root_dir, reference)


if __name__ == "__main__":
    unittest.main()
