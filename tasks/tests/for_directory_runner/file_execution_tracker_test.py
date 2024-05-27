import csv
import os
import tempfile
import unittest

from tasks.tools.for_directory_runner.file_execution_tracker import FileExecutionTracker


class TestFileExecutionTracker(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_csv_path = os.path.join(self.temp_dir.name, "test_files.csv")
        self.manager = FileExecutionTracker(self.test_csv_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initialization(self):
        self.assertTrue(os.path.isfile(self.test_csv_path))
        with open(self.test_csv_path, "r", newline="") as file:
            reader = csv.reader(file)
            headers = next(reader)
            self.assertEqual(headers, ["File Path", "Status"])

    def test_add_files(self):
        files = ["file_1", "file_2", "file_3"]
        self.manager.add_files(files)
        with open(self.test_csv_path, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)

            rows = list(reader)
            self.assertEqual(len(rows), len(files))
            for i, row in enumerate(rows):
                self.assertEqual(row, [files[i], "pending"])

    def test_write_files_from_directory(self):
        os.makedirs(os.path.join(self.temp_dir.name, "subdir"), exist_ok=True)
        file_paths = [
            os.path.join(self.temp_dir.name, "file1.txt"),
            os.path.join(self.temp_dir.name, "file2.txt"),
            os.path.join(self.temp_dir.name, "subdir", "file3.txt"),
        ]
        for path in file_paths:
            with open(path, "w") as f:
                f.write("Test")

        self.manager.add_files_from_directory(
            self.temp_dir.name, excluded_files=["test_files.csv"]
        )
        with open(self.test_csv_path, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)

            rows = list(reader)
            self.assertEqual(len(rows), len(file_paths))
            for row, path in zip(rows, file_paths):
                self.assertEqual(row, [path, "pending"])

    def test_verify_csv(self):
        files = ["file_1", "file_2", "file_3"]
        self.manager.add_files(files)
        with open(self.test_csv_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["File 4", "invalid_status"])

        with self.assertRaises(ValueError) as context:
            self.manager.verify_csv()
        self.assertIn("Invalid status 'invalid_status'", str(context.exception))

    def test_take_next_pending(self):
        files = ["file_1", "file_2", "file_3"]
        self.manager.add_files(files)
        next_task = self.manager.take_next_pending()
        self.assertEqual(next_task, "file_1")
        with open(self.test_csv_path, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)
            rows = list(reader)
            self.assertEqual(rows[0], ["file_1", "running"])
            self.assertEqual(rows[1], ["file_2", "pending"])
            self.assertEqual(rows[2], ["file_3", "pending"])

        next_task = self.manager.take_next_pending()
        self.assertEqual(next_task, "file_2")
        with open(self.test_csv_path, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)

            rows = list(reader)
            self.assertEqual(rows[0], ["file_1", "completed"])
            self.assertEqual(rows[1], ["file_2", "running"])
            self.assertEqual(rows[2], ["file_3", "pending"])

        next_task = self.manager.take_next_pending()
        self.assertEqual(next_task, "file_3")
        with open(self.test_csv_path, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)

            rows = list(reader)
            self.assertEqual(rows[0], ["file_1", "completed"])
            self.assertEqual(rows[1], ["file_2", "completed"])
            self.assertEqual(rows[2], ["file_3", "running"])

        next_task = self.manager.take_next_pending()
        self.assertIsNone(next_task)
        with open(self.test_csv_path, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)

            rows = list(reader)
            self.assertEqual(rows[0], ["file_1", "completed"])
            self.assertEqual(rows[1], ["file_2", "completed"])
            self.assertEqual(rows[2], ["file_3", "completed"])


if __name__ == "__main__":
    unittest.main()
