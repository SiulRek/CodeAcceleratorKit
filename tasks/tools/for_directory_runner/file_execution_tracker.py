import csv
import os


class FileExecutionTracker:
    """Class that tracks execution status of files."""

    def __init__(self, csv_path):
        self.csv_path = csv_path
        if not os.path.isfile(csv_path):
            with open(csv_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["File Path", "Status", "Comments"])

    def add_files(self, files):
        """
        Add files to the CSV file with status set to 'pending'.

        Args:
            - files (list): A list of file descriptions (strings).
        """
        with open(self.csv_path, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for file_path in files:
                writer.writerow([file_path, "pending", "-"])

    def add_files_from_directory(
        self, directory, excluded_dirs=None, excluded_files=None
    ):
        """
        Add all files from a directory to the CSV file with status set to
        'pending'.

        Args:
            - directory (str): The directory to write files from.
            - excluded_dirs (list): A list of directory names to exclude.
            - excluded_files (list): A list of file names to exclude.
        """
        if excluded_dirs is None:
            excluded_dirs = []
        if excluded_files is None:
            excluded_files = []

        excluded_dirs = [os.path.normpath(dir_path) for dir_path in excluded_dirs]
        excluded_dirs = [os.path.abspath(dir_path) for dir_path in excluded_dirs]

        files = []
        for root, _, filenames in os.walk(directory):
            root = os.path.normpath(root)
            root = os.path.abspath(root)
            for excluded_dir in excluded_dirs:
                if root.startswith(excluded_dir):
                    break
            else:
                filenames.sort()
                for filename in filenames:
                    if filename not in excluded_files:
                        files.append(os.path.join(root, filename))

        self.add_files(files)

    def verify_tracks(self):
        """Verifies the tracks in CSV file by checking if all files are either 'pending',
        'running', or 'completed'. Raises ValueError if any other status is found."""
        if not os.path.isfile(self.csv_path):
            raise FileNotFoundError(f"File '{self.csv_path}' does not exist.")
        with open(self.csv_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)

            running_exists = False
            for row in reader:
                if row[1] not in ["pending", "running", "completed", "failed"]:
                    msg = f"Invalid status '{row[1]}' in file '{row[0]}'"
                    raise ValueError(msg)
                if row[1] == "running":
                    if running_exists:
                        msg = "More than one file is marked as 'running'"
                        raise ValueError(msg)

    def take_next_pending(self):
        """
        Transforms the first 'pending' file to 'running' and the current
        'running' files to 'completed'. Returns the value of the first column
        (file description) of the newly marked 'running' file.

        Returns:
            - str: The description of the file now marked as 'running'.
        """
        rows = []
        next_pending_file = None

        with open(self.csv_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[1] == "pending" and next_pending_file is None:
                    row[1] = "running"
                    next_pending_file = row[0]
                rows.append(row)

        with open(self.csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(rows)

        return next_pending_file
    
    def mark_running_as_completed(self):
        """
        Transforms the 'running' file to 'completed'.
        """
        rows = []
        with open(self.csv_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[1] == "running":
                    row[1] = "completed"
                rows.append(row)

        with open(self.csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    def mark_running_as_failed(self, error_message):
        """
        Transforms the 'running' file to 'failed' and writes the error message
        in the third column.

        Args:
            - error_message (str): The error message to write in the
                comments column.
        """
        rows = []
        with open(self.csv_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[1] == "running":
                    row[1] = "failed"
                    row[2] = error_message
                rows.append(row)

        with open(self.csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(rows)
    
    def get_status_count(self):
        """
        Returns the number of files with each status.

        Returns:
            - dict: A dictionary with status as keys and the number of files
                with that status as values.
        """
        with open(self.csv_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)

            count_status = {"pending": 0, "running": 0, "completed": 0, "failed": 0}
            for row in reader:
                count_status[row[1]] += 1

        return count_status

    def clear_tracks(self):
        """Clears the CSV file."""
        with open(self.csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["File Path", "Status", "Comments"])
    
    def get_completed_files(self):
        """
        Returns the list of file paths marked as 'completed'.

        Returns:
            - list: A list of file paths.
        """
        completed_files = []
        with open(self.csv_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if row[1] == "completed":
                    completed_files.append(row[0])

        return completed_files
    
    def get_failed_files(self):
        """
        Returns the list of file paths marked as 'failed'.

        Returns:
            - list: A list of file paths.
        """
        failed_files = []
        with open(self.csv_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if row[1] == "failed":
                    failed_files.append(row[0])

        return failed_files