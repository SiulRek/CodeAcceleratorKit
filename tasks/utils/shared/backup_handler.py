from copy import deepcopy
import csv
import os
import shutil


class BackupHandler:
    """
    A class for handling file backups in a specified directory.

    Attributes
    ----------
    backup_dir (str)
        The directory where backup files will be stored.
    max_backups (int)
        The maximum number of backup files to keep in the directory.

    Methods
    -------
    load_context()
        Load the backup context from a CSV file.
    save_context()
        Save the backup context to a CSV file.
    store_backup(file_path, comment=None)
        Store a backup of a file in the backup directory.
    recover_backup(previous_file_name)
        Recover a specific backup file to its original location.
    cleanup_storage()
        Clean up excess backup files based on the `max_backups` limit.
    get_backup_context(file_extension=None)
        Retrieve information about stored backup files.
    clear_storage()
        Removes the content of the backup directory.
    get_backup_path(previous_file_path)
        Get the backup path of a specific file.
    recover_last_backup()
        Recover the last backup file to its original location.

    Usage
    -----
    ```python
    backup_dir = 'path/to/backup/directory'
    max_backups = 10
    backup_handler = BackupHandler(backup_dir, max_backups)
    backup_handler.store_backup('file_path.txt', 'Backup comment')
    ```
    """

    CONTEXT_FILE_NAME = "backup_context.csv"

    def __init__(self, backup_dir, max_backups=None):
        """
        Initialize the BackupHandler instance.

        Parameters
        ----------
        backup_dir (str)
            The directory where backup files will be stored.
        max_backups (int, optional)
            The maximum number of backup files to keep. Default is None.
        """

        self.backup_dir = backup_dir
        if not os.path.exists(self.backup_dir):
            os.mkdir(self.backup_dir)
        self.context_file = os.path.join(backup_dir, BackupHandler.CONTEXT_FILE_NAME)
        self.load_context()
        self.max_backups = max_backups

    def load_context(self):
        """
        Load the backup context from a CSV file.

        Returns
        -------
        list
            context_data
        """

        self.context_data = []
        if os.path.exists(self.context_file):
            with open(self.context_file, "r", newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.context_data.append(row)

        return self.context_data

    def save_context(self):
        """
        Save the backup context to a CSV file.
        """

        with open(self.context_file, "w", newline="") as csvfile:
            fieldnames = ["previous_file_path", "backup_file_name", "comment"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.context_data)

    def store_backup(self, file_path, comment=None):
        """
        Store a backup of a file in the backup directory. Raises
        FileNotFoundError if the file does not exist.

        Parameters
        ----------
        file_path (str)
            The path to the file to be backed up.
        comment (str, optional)
            An optional comment to associate with the backup.
        """

        count = 1
        file_name, file_extension = os.path.splitext(os.path.basename(file_path))
        dest_file = os.path.join(
            self.backup_dir, f"{file_name}_{count}{file_extension}"
        )

        while os.path.exists(f"{dest_file}"):
            dest_file = os.path.join(
                self.backup_dir, f"{file_name}_{count}{file_extension}"
            )
            count += 1

        shutil.copy2(file_path, dest_file)

        context_entry = {
            "previous_file_path": os.path.normpath(file_path),
            "backup_file_name": os.path.basename(dest_file),
            "comment": comment,
        }
        self.load_context()
        self.context_data.append(context_entry)

        if self.max_backups is not None and len(self.context_data) > self.max_backups:
            oldest_backup = self.context_data.pop(0)
            oldest_backup_file = os.path.join(
                self.backup_dir, oldest_backup["backup_file_name"]
            )
            os.remove(oldest_backup_file)

        self.save_context()

    def recover_backup(self, previous_file_path):
        """
        Recover a specific backup file to its original location. If multiple
        backups exist for the same file, the most recent backup will be
        recovered.

        Parameters
        ----------
        previous_file_path (str)
            The path to the file that was backed up.
        """
        self.cleanup_storage()
        self.load_context()
        previous_file_path = os.path.normpath(previous_file_path)
        copy_context_data = deepcopy(self.context_data)
        copy_context_data.reverse()  # To get the last backup first
        for backup_file_context in copy_context_data:
            source_file_path = backup_file_context["previous_file_path"]
            if source_file_path == previous_file_path:
                backup_file = os.path.join(
                    self.backup_dir, backup_file_context["backup_file_name"]
                )
                if os.path.exists(backup_file):
                    shutil.move(backup_file, previous_file_path)
                    self.context_data.remove(backup_file_context)
                    self.save_context()
                break
        else:
            msg = f"No backup found for {previous_file_path}"
            raise FileNotFoundError(msg)

    def recover_last_backup(self):
        """
        Recover the last backupt file to its original location.

        Returns
        -------
        bool
            True if the recovery was successful, False if the no File is backed
            up.
        """

        self.cleanup_storage()

        if not self.context_data == []:
            backup_file_context = self.context_data[-1]
            source_file = os.path.join(
                self.backup_dir, backup_file_context["backup_file_name"]
            )
            dest_file = backup_file_context["previous_file_path"]
            if os.path.exists(source_file):
                shutil.move(source_file, dest_file)
                self.cleanup_storage()
                return True
            else:
                msg = f"Backup file {source_file} not found"
                raise FileNotFoundError(msg)
        msg = "No backup found"
        raise FileNotFoundError(msg)

    def get_backup_path(self, previous_file_path):
        """
        Get the backup path of a specific file.

        Parameters
        ----------
        previous_file_path (str)
            The path to the file that was backed up.

        Returns
        -------
        str
            The path to the backup file.
        """
        self.load_context()
        previous_file_path = os.path.normpath(previous_file_path)
        reversed_context_data = deepcopy(self.context_data)
        reversed_context_data.reverse()
        for backup_file_context in reversed_context_data:
            source_file_path = backup_file_context["previous_file_path"]
            if source_file_path == previous_file_path:
                return os.path.join(
                    self.backup_dir, backup_file_context["backup_file_name"]
                )
        else:
            msg = f"No backup found for {previous_file_path}"
            raise FileNotFoundError(msg)

    def cleanup_storage(self):
        """
        Clean up the backup storage by removing outdated backup files and
        associated records.

        This method removes backup files that are no longer associated with any
        records in the backup context. Additionally, if the number of backup
        files exceeds the maximum allowed, it removes the oldest backups to
        maintain the specified limit.

        Returns
        -------
        bool
            True if the cleanup was successful, False if the cleanup was not
            possible or no action was taken.
        """

        if not os.path.exists(self.context_file):
            self.clear_storage()
            return False

        self.load_context()
        stored_files = set(os.listdir(self.backup_dir))
        mentioned_files = set(entry["backup_file_name"] for entry in self.context_data)
        files_to_remove = (
            stored_files - mentioned_files - set([BackupHandler.CONTEXT_FILE_NAME])
        )

        for file_to_remove in files_to_remove:
            file_path = os.path.join(self.backup_dir, file_to_remove)
            os.remove(file_path)

        self.context_data = [
            entry
            for entry in self.context_data
            if entry["backup_file_name"] in stored_files
        ]

        while len(self.context_data) > self.max_backups:
            oldest_backup = self.context_data.pop(0)
            oldest_backup_file = os.path.join(
                self.backup_dir, oldest_backup["backup_file_name"]
            )
            os.remove(oldest_backup_file)

        self.save_context()

        return True

    def clear_storage(self):
        """
        Removes the content of the backup directory.
        """
        if os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)
            os.mkdir(self.backup_dir)

    def get_backup_context(self, file_extension=None):
        """
        Retrieve information about stored backup files.

        Parameters
        ----------
        file_extension (str, optional)
            Filter backups by file extension. Default is None.

        Returns
        -------
        list
            A list of tuples containing (previous_file_path, backup_file_name,
            comment).
        """

        if file_extension:
            filtered_context = [
                entry
                for entry in self.context_data
                if entry["previous_file_path"].endswith(file_extension)
            ]
        else:
            self.load_context()
            filtered_context = self.context_data
        return [
            (entry["previous_file_path"], entry["backup_file_name"], entry["comment"])
            for entry in filtered_context
        ]


if __name__ == "__main__":
    backup_dir = r"directory/to/store/backups"
    max_backups = 2

    backup_handler = BackupHandler(backup_dir, max_backups)
    backup_handler.store_backup(r"store_backup.py", "Backup comment")
