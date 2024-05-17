import sys
import os

from tasks.constants.getters import get_task_cache_directory


class TaskBase:
    """
    Base class for task execution, providing setup and common utilities for all
    tasks.

    Attributes:
        - NAME (str): A class-level attribute that identifies the name of
            the task.
    """

    NAME = None

    def __init__(self, default_root, *default_args):
        """
        Initializes the task with default root and additional arguments.

        Args:
            - default_root (str): The default root directory for task
                execution.
            - default_args (tuple): Additional default arguments required by
                the task.
        """
        self.task_executor_root = None
        self.additional_args = None
        self.cache_dir = None
        self._initialize_arguments(default_root, default_args)
        self.line_sep = "-" * 120 + "\n"

    def _initialize_arguments(self, default_root, default_args):
        """
        Processes command line arguments and sets the task root and additional
        arguments.

        Args:
            - default_root (str): The default root directory if no command
                line argument is provided.
            - default_args (tuple): Default arguments to use if no
                additional command line arguments are provided.
        """
        if len(sys.argv) < 2:
            self.task_executor_root = default_root
            self.additional_args = default_args
            sys.path.append(self.task_executor_root)
        else:
            self.task_executor_root = sys.argv[1]
            self.additional_args = sys.argv[2:]

    def setup(self):
        """Placeholder for task-specific setup. Can be extended by subclasses."""
        self.cache_dir = get_task_cache_directory(self.NAME)

    def execute(self):
        """Executes the task's main functionality. Must be implemented by
        subclasses."""
        msg = "Subclasses should implement this method."
        raise NotImplementedError(msg)

    def teardown(self):
        """Placeholder for task-specific teardown. can be extended by
        subclasses."""
        if self.cache_dir and os.path.exists(self.cache_dir):
            os.rmdir(self.cache_dir)

    def _print_execution_start(self):
        """Prints the start message for task execution."""
        msg = f"{'='*55} TASK START {'='*53}\n"
        msg += f"Runned Task: {self.NAME}\n{self.line_sep}"
        msg += "Task Ouputs:\n"
        print(msg)

    def _print_execution_end(self, additional_msg=""):
        """
        Prints the end message for task execution, indicating completion.

        Args:
            - additional_msg (str): Optional additional message to include
                in the completion printout.
        """
        msg = self.line_sep
        msg += "TASK EXECUTED SUCCESSFULLY\n"
        msg += f"{'='*55} TASK END {'='*55}"
        if additional_msg:
            msg += f"\n{additional_msg}"
        print(msg)

    def main(self):
        """The main method to manage the flow of task execution."""
        self._print_execution_start()
        self.setup()
        self.execute()
        self.teardown()
        self._print_execution_end()