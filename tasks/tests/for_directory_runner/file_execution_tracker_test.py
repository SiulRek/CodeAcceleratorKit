import csv
import os
import tempfile
import unittest

from tasks.tools.for_directory_runner.file_execution_tracker import FileExecutionTracker


class TestFileExecutionTracker(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_csv_path = os.path.join(self.temp_dir.name, "test_files.csv")
        self.tracker = FileExecutionTracker(self.test_csv_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initialization(self):
        self.assertTrue(os.path.isfile(self.test_csv_path))
        with open(self.test_csv_path, "r", newline="") as file:
            reader = csv.reader(file)
            headers = next(reader)
            self.assertEqual(headers, ["File Path", "Status", "Comments"])

    def test_add_files(self):
        files = ["file_1", "file_2", "file_3"]
        self.tracker.add_files(files)
        with open(self.test_csv_path, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)

            rows = list(reader)
            self.assertEqual(len(rows), len(files))
            for i, row in enumerate(rows):
                self.assertEqual(row, [files[i], "pending", "-"])

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

        self.tracker.add_files_from_directory(
            self.temp_dir.name, excluded_files=["test_files.csv"]
        )
        with open(self.test_csv_path, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)

            rows = list(reader)
            self.assertEqual(len(rows), len(file_paths))
            for row, path in zip(rows, file_paths):
                self.assertEqual(row, [path, "pending", "-"])

    def test_verify_csv(self):
        files = ["file_1", "file_2", "file_3"]
        self.tracker.add_files(files)
        with open(self.test_csv_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["file_4", "invalid_status", "-"])

        with self.assertRaises(ValueError) as context:
            self.tracker.verify_tracks()
        self.assertIn("Invalid status 'invalid_status'", str(context.exception))

    def test_take_next_pending(self):
        files = ["file_1", "file_2", "file_3"]
        self.tracker.add_files(files)
        next_task = self.tracker.take_next_pending()
        self.assertEqual(next_task, "file_1")
        with open(self.test_csv_path, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)
            rows = list(reader)
            self.assertEqual(rows[0], ["file_1", "running", "-"])
            self.assertEqual(rows[1], ["file_2", "pending", "-"])
            self.assertEqual(rows[2], ["file_3", "pending", "-"])

        self.tracker.mark_running_as_completed()
        next_task = self.tracker.take_next_pending()
        self.assertEqual(next_task, "file_2")
        with open(self.test_csv_path, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)

            rows = list(reader)
            self.assertEqual(rows[0], ["file_1", "completed", "-"])
            self.assertEqual(rows[1], ["file_2", "running", "-"])
            self.assertEqual(rows[2], ["file_3", "pending", "-"])

        self.tracker.mark_running_as_completed()
        next_task = self.tracker.take_next_pending()
        self.assertEqual(next_task, "file_3")
        with open(self.test_csv_path, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)

            rows = list(reader)
            self.assertEqual(rows[0], ["file_1", "completed", "-"])
            self.assertEqual(rows[1], ["file_2", "completed", "-"])
            self.assertEqual(rows[2], ["file_3", "running", "-"])

        next_task = self.tracker.mark_running_as_completed()
        self.assertIsNone(next_task)
        with open(self.test_csv_path, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)

            rows = list(reader)
            self.assertEqual(rows[0], ["file_1", "completed", "-"])
            self.assertEqual(rows[1], ["file_2", "completed", "-"])
            self.assertEqual(rows[2], ["file_3", "completed", "-"])

    def test_mark_running_as_completed(self):
        files = ["file_1", "file_2", "file_3"]
        self.tracker.add_files(files)
        next_task = self.tracker.take_next_pending()
        self.assertEqual(next_task, "file_1")

        self.tracker.mark_running_as_completed()
        with open(self.test_csv_path, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)
            rows = list(reader)

            self.assertEqual(rows[0], ["file_1", "completed", "-"])
            self.assertEqual(rows[1], ["file_2", "pending", "-"])
            self.assertEqual(rows[2], ["file_3", "pending", "-"])

    def test_mark_running_as_failed(self):
        files = ["file_1", "file_2"]
        self.tracker.add_files(files)
        self.tracker.take_next_pending()

        self.tracker.mark_running_as_failed("Some error occurred")

        with open(self.test_csv_path, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)
            rows = list(reader)
            self.assertEqual(rows[0], ["file_1", "failed", "Some error occurred"])
            self.assertEqual(rows[1], ["file_2", "pending", "-"])

    def test_clear_tracks(self):
        files = ["file_1", "file_2"]
        self.tracker.add_files(files)
        self.tracker.clear_tracks()

        with open(self.test_csv_path, "r", newline="") as file:
            reader = csv.reader(file)
            headers = next(reader)

            self.assertEqual(headers, ["File Path", "Status", "Comments"])
            with self.assertRaises(StopIteration):
                next(reader)

    def test_get_status_count(self):
        files = ["file_1", "file_2", "file_3"]
        self.tracker.add_files(files)
        self.tracker.take_next_pending()

        self.tracker.mark_running_as_completed()

        self.tracker.take_next_pending()

        self.tracker.mark_running_as_failed("error")

        status_count = self.tracker.get_status_count()
        self.assertEqual(status_count["pending"], 1)
        self.assertEqual(status_count["running"], 0)
        self.assertEqual(status_count["completed"], 1)
        self.assertEqual(status_count["failed"], 1)

    def test_get_completed_files(self):
        files = ["file_1", "file_2", "file_3"]
        self.tracker.add_files(files)
        self.tracker.take_next_pending()

        self.tracker.mark_running_as_completed()

        self.tracker.take_next_pending()

        self.tracker.mark_running_as_completed()

        self.tracker.take_next_pending()
        self.tracker.mark_running_as_failed("error")

        completed_files = self.tracker.get_completed_files()
        self.assertEqual(completed_files, ["file_1", "file_2"])

    def test_get_failed_files(self):
        files = ["file_1", "file_2", "file_3"]
        self.tracker.add_files(files)
        self.tracker.take_next_pending()

        self.tracker.mark_running_as_failed("error")

        self.tracker.take_next_pending()

        self.tracker.mark_running_as_failed("error")

        self.tracker.take_next_pending()
        self.tracker.mark_running_as_completed()

        failed_files = self.tracker.get_failed_files()
        self.assertEqual(failed_files, ["file_1", "file_2"])


if __name__ == "__main__":
    unittest.main()
