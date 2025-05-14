"""
This module defines the PylintReportTask, a task for generating a pylint report
for specified Python files within a directory.

The PylintReportTask class extends the base task functionality to find and
analyze Python files using pylint, collecting quality scores and forming a
comprehensive report. The task supports specifying files and directories as
input through command line arguments and handles dynamic discovery of files
within directories.

Usage example:
```python
PylintReportTask(root_directory, reference_dir,
directory_for_report).main()
```

Note
----
If no directory is specified, reference_dir is used as the
directory_for_report. directory_for_report can be defined with 'sloppy' string
(see

Highlights:
- Dynamically finds Python files in a given directory.
- Executes pylint on each file and extracts scoring information.
- Writes the pylint report to a file, organizing entries by score (worst
to best).
"""

from datetime import datetime
import os

from tasks.tasks.core.task_base import TaskBase
from tasks.utils.shared.execute_pylint import execute_pylint
from tasks.utils.shared.find_closest_matching_dir import find_closest_matching_dir


class PylintReportTask(TaskBase):
    """
    A task for generating a pylint report.
    """

    NAME = "Pylint Report"

    def setup(self):
        """
        Sets up the PylintReportTask by initializing the file path from
        additional arguments.
        """
        super().setup()
        self.current_file = self.additional_args[0]
        if len(self.additional_args) > 1 and self.additional_args[1]:
            self.dir_for_report = self.additional_args[1]

    def _get_python_files(self, directory):
        """
        Gets all python files in the specified directory.
        """
        python_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        return python_files

    def _process_pylint_output(self, file, output):
        """
        Processes the pylint output and prettifies it.
        """
        file = os.path.abspath(file)
        file = os.path.normpath(file)
        header = "*" * 50 + f"\n Module: {file}\n"

        lines = output.split("\n")
        prettified_output = [header]
        for line in lines[1:]:
            if line.strip():  # Ignore empty lines
                prettified_output.append("    " + line.strip())
        prettified_output.append("*" * 50)
        prettified_output = "\n".join(prettified_output) + "\n\n"

        try:
            score = output.split("Your code has been rated at ")[1].split("/10")[0]
        except IndexError:
            score = "0.0"
        return prettified_output, score

    def _execute_pylint(self, file):
        """
        Runs pylint on the specified file.
        """
        python_env = self.profile.runner_python_env
        print(f"Running pylint on {file}")
        output = execute_pylint(file, python_env)
        print("Output: \n", output)
        print()
        return self._process_pylint_output(file, output)

    def _write_report(self, logs):
        """
        Writes the pylint report to a file.
        """
        reports_dir = self.profile.reports_dir
        root_dir = self.profile.root
        report_name = os.path.basename(self.dir_for_report).split(".")[0]
        report_path = os.path.join(reports_dir, f"{report_name}_pylint_report.txt")

        with open(report_path, "w", encoding="utf-8") as report_file:
            report_file.write(f"Pylint Report for {self.dir_for_report}\n")
            report_file.write(
                f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            report_file.write("\nSummary:\n")
            report_file.write(f"{'Module':<50} {'Score':>5}\n")
            report_file.write(f"{'-'*46}\n")
            for file, score in [(log[0], log[2]) for log in logs]:
                file = os.path.relpath(file, root_dir)
                if len(file) > 50:
                    file = file[-50:]
                report_file.write(f"{file:<50} {score:>5}\n")
            report_file.write("\nDetailed Report:\n")
            report_file.write(f"{'='*50}\n")

            for log in logs:
                report_file.write(log[1])

        print(f"Report written to {report_path}")

    def execute(self):
        """
        Executes the pylint report task, generating a pylint report for the
        specified file.
        """
        logs = []

        if hasattr(self, "dir_for_report"):
            if os.path.exists(self.current_file):
                self.dir_for_report = find_closest_matching_dir(
                    partial_path=self.dir_for_report,
                    root_dir=self.task_runner_root,
                    reference_dir=os.path.dirname(self.current_file),
                )
            python_files = self._get_python_files(self.dir_for_report)
            for file in python_files:
                output, score = self._execute_pylint(file)
                logs.append((file, output, float(score)))

        else:
            self.dir_for_report = self.current_file
            output, score = self._execute_pylint(self.dir_for_report)
            logs.append((file, output, score))

        # Sort from worst score to best score
        logs = sorted(logs, key=lambda x: x[2], reverse=False)
        self._write_report(logs)


if __name__ == "__main__":
    default_root = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."
    )
    default_file_path = os.path.curdir
    default_dir_for_report = "tasks/core"
    task = PylintReportTask(default_root, default_file_path, default_dir_for_report)
    task.main()
