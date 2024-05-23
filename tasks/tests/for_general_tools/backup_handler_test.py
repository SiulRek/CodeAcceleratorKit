import csv
import os
import shutil
import unittest

from tasks.tools.general.backup_handler import BackupHandler

ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
OUTPUT_DIRECTORY = os.path.join(ROOT_DIR, "tasks", "tests", "outputs")
DATA_DIR = os.path.join(ROOT_DIR, "tasks", "tests", "data")

TEXT_FILE_1_PATH = os.path.join(DATA_DIR, "test_file_1.txt")
TEXT_FILE_2_PATH = os.path.join(DATA_DIR, "test_file_2.txt")

TEXT_FILE_3_PATH = os.path.join(DATA_DIR, "reference_1.py")
TEXT_FILE_3_PATH = os.path.join(DATA_DIR, "reference_2.py")


class TestBackupHandler(unittest.TestCase):

    def setUp(self):
        self.backup_dir = os.path.join(OUTPUT_DIRECTORY, "backup")

        if os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)

        self.max_backups = 3
        self.backup_handler = BackupHandler(self.backup_dir, self.max_backups)

    def tearDown(self):
        if os.path.exists(TEXT_FILE_1_PATH):
            os.remove(TEXT_FILE_1_PATH)
        if os.path.exists(TEXT_FILE_2_PATH):
            os.remove(TEXT_FILE_2_PATH)

        shutil.rmtree(self.backup_dir)

    def test_store_and_recover_backup(self):
        source_file = TEXT_FILE_1_PATH
        with open(source_file, "w", encoding="utf-8") as f:
            f.write("Sample content")

        self.backup_handler.store_backup(source_file, "Backup comment")
        os.remove(source_file)
        self.assertEqual(len(os.listdir(self.backup_dir)) - 1, 1)

        self.backup_handler.recover_backup(source_file)

        self.assertTrue(os.path.exists(source_file))

    def test_cleanup_storage_1(self):
        source_file_1 = TEXT_FILE_1_PATH
        source_file_2 = TEXT_FILE_2_PATH

        with open(source_file_1, "w", encoding="utf-8") as f:
            f.write("Sample content 1")
        with open(source_file_2, "w", encoding="utf-8") as f:
            f.write("Sample content 2")

        self.backup_handler.store_backup(source_file_1, "Backup comment 1")
        os.remove(source_file_1)

        self.backup_handler.store_backup(source_file_2, "Backup comment 2")
        os.remove(source_file_2)

        self.assertEqual(len(os.listdir(self.backup_dir)) - 1, 2)

        for file_name in os.listdir(self.backup_dir):
            if file_name.endswith(".txt"):
                os.remove(os.path.join(self.backup_dir, file_name))
                break

        self.backup_handler.cleanup_storage()

        self.assertEqual(len(os.listdir(self.backup_dir)) - 1, 1)

    def test_cleanup_storage_2(self):
        source_file_1 = TEXT_FILE_1_PATH
        source_file_2 = TEXT_FILE_2_PATH

        with open(source_file_1, "w", encoding="utf-8") as f:
            f.write("Sample content 1")
        with open(source_file_2, "w", encoding="utf-8") as f:
            f.write("Sample content 2")

        self.backup_handler.store_backup(source_file_1, "Backup comment 1")
        os.remove(source_file_1)

        self.backup_handler.store_backup(source_file_2, "Backup comment 2")
        os.remove(source_file_2)

        self.assertEqual(len(os.listdir(self.backup_dir)) - 1, 2)

        rows = []
        with open(
            self.backup_handler.context_file, "r", newline="", encoding="utf-8"
        ) as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)

        rows.pop()
        with open(
            self.backup_handler.context_file, "w", newline="", encoding="utf-8"
        ) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)

        self.backup_handler.cleanup_storage()

        self.assertEqual(len(os.listdir(self.backup_dir)) - 1, 1)

    def test_cleanup_storage_3(self):
        source_file_1 = TEXT_FILE_1_PATH
        source_file_2 = TEXT_FILE_2_PATH

        with open(source_file_1, "w", encoding="utf-8") as f:
            f.write("Sample content 1")
        with open(source_file_2, "w", encoding="utf-8") as f:
            f.write("Sample content 2")

        self.backup_handler.store_backup(source_file_1, "Backup comment 1")
        self.backup_handler.store_backup(source_file_2, "Backup comment 2")

        self.assertEqual(len(os.listdir(self.backup_dir)) - 1, 2)

        rows = []
        with open(
            self.backup_handler.context_file, "r", newline="", encoding="utf-8"
        ) as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)

        self.assertEqual(len(rows), 3)

        for file_name in os.listdir(self.backup_dir):
            if file_name.endswith(".txt"):
                os.remove(os.path.join(self.backup_dir, file_name))
                break

        self.backup_handler.cleanup_storage()

        rows = []
        with open(
            self.backup_handler.context_file, "r", newline="", encoding="utf-8"
        ) as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)

        self.assertEqual(len(rows), 2)

    def test_cleanup_storage_4(self):
        source_file_1 = TEXT_FILE_1_PATH
        source_file_2 = TEXT_FILE_2_PATH

        with open(source_file_1, "w", encoding="utf-8") as f:
            f.write("Sample content 1")
        with open(source_file_2, "w", encoding="utf-8") as f:
            f.write("Sample content 2")

        self.backup_handler.store_backup(source_file_1, "Backup comment 1")
        self.backup_handler.store_backup(source_file_2, "Backup comment 2")
        os.remove(self.backup_handler.context_file)

        self.backup_handler.cleanup_storage()

        self.assertEqual(len(os.listdir(self.backup_dir)), 0)

    def test_max_backups_limit(self):
        source_file = TEXT_FILE_1_PATH

        with open(source_file, "w", encoding="utf-8") as f:
            f.write("Sample content")

        for i in range(self.max_backups + 1):
            self.backup_handler.store_backup(source_file, f"Backup comment {i}")

        self.assertEqual(len(os.listdir(self.backup_dir)) - 1, self.max_backups)

    def test_recover_backup_success(self):
        original_file = TEXT_FILE_1_PATH
        backup_comment = "Backup comment"

        with open(original_file, "w", encoding="utf-8") as f:
            f.write("Sample content")

        self.backup_handler.store_backup(original_file, backup_comment)

        os.remove(original_file)

        self.backup_handler.recover_backup(original_file)

        self.assertTrue(os.path.exists(original_file))

    def test_recover_backup_failure_1(self):
        non_existent_file_name = "non_existent_backup.txt"
        with self.assertRaises(FileNotFoundError):
            self.backup_handler.recover_backup(non_existent_file_name)

    def test_recover_backup_failure_2(self):
        source_file_1 = TEXT_FILE_1_PATH

        with open(source_file_1, "w", encoding="utf-8") as f:
            f.write("Sample content 1")

        self.backup_handler.store_backup(source_file_1, "Backup comment 1")
        os.remove(source_file_1)

        self.assertEqual(len(os.listdir(self.backup_dir)) - 1, 1)

        for file_name in os.listdir(self.backup_dir):
            if file_name.endswith(".txt"):
                os.remove(os.path.join(self.backup_dir, file_name))
                with self.assertRaises(FileNotFoundError):
                    self.backup_handler.recover_backup(file_name)
                break

    def test_recover_last_backup_successful(self):
        with open(TEXT_FILE_1_PATH, "w", encoding="utf-8") as f:
            f.write("Original content")

        with open(TEXT_FILE_2_PATH, "w", encoding="utf-8") as f:
            f.write("Modified content")

        self.backup_handler.store_backup(TEXT_FILE_1_PATH, "Backup comment")
        os.remove(TEXT_FILE_1_PATH)
        self.backup_handler.store_backup(TEXT_FILE_2_PATH, "Modified comment")
        os.remove(TEXT_FILE_2_PATH)

        self.assertTrue(self.backup_handler.recover_last_backup())

        self.assertTrue(os.path.exists(TEXT_FILE_2_PATH))

    def test_recover_last_backup_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.backup_handler.recover_last_backup()

    def test_get_backup_context_with_extension(self):
        with open(TEXT_FILE_1_PATH, "w", encoding="utf-8") as f:
            f.write("Sample content")

        self.backup_handler.store_backup(TEXT_FILE_3_PATH, "Backup comment 1")
        self.backup_handler.store_backup(TEXT_FILE_1_PATH, "Backup comment 2")
        self.backup_handler.store_backup(TEXT_FILE_3_PATH, "Backup comment 3")

        pdf_backup_context = self.backup_handler.get_backup_context(
            file_extension=".py"
        )

        self.assertEqual(len(pdf_backup_context), 2)

        self.assertEqual(pdf_backup_context[0][0], TEXT_FILE_3_PATH)
        self.assertEqual(pdf_backup_context[0][2], "Backup comment 1")

        self.assertEqual(pdf_backup_context[1][0], TEXT_FILE_3_PATH)
        self.assertEqual(pdf_backup_context[1][2], "Backup comment 3")

    def test_max_backups_change(self):
        with open(TEXT_FILE_1_PATH, "w", encoding="utf-8") as f:
            f.write("Sample content")
        with open(TEXT_FILE_2_PATH, "w", encoding="utf-8") as f:
            f.write("Sample content")

        self.backup_handler.store_backup(TEXT_FILE_1_PATH, "Backup comment 1")
        self.backup_handler.store_backup(TEXT_FILE_2_PATH, "Backup comment 2")
        self.backup_handler.store_backup(TEXT_FILE_3_PATH, "Backup comment 3")

        self.assertEqual(len(self.backup_handler.get_backup_context()), 3)

        self.backup_handler.max_backups = 1

        self.backup_handler.cleanup_storage()

        self.assertEqual(len(self.backup_handler.get_backup_context()), 1)

    def test_get_backup_path(self):
        source_file = TEXT_FILE_1_PATH
        backup_comment = "Backup comment"

        with open(source_file, "w", encoding="utf-8") as f:
            f.write("Sample content")

        self.backup_handler.store_backup(source_file, backup_comment)

        backup_path = self.backup_handler.get_backup_path(source_file)
        self.assertTrue(os.path.exists(backup_path))
        self.assertTrue(backup_path.startswith(self.backup_dir))


if __name__ == "__main__":
    unittest.main()
