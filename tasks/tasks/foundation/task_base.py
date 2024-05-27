from abc import ABC, abstractmethod
import os
import shutil
import sys

from tasks.tasks.management.task_runner_profile import TaskRunnerProfile


class TaskBase(ABC):
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
        self.task_runner_root = None
        self.additional_args = None
        self.tasks_cache_dir = None
        self.default_root = default_root
        self.default_args = default_args
        self._force_defaults = False
        self.line_sep = "-" * 120 + "\n"

    def force_defaults(self):
        """Forces the task to use the default root and arguments."""
        self._force_defaults = True

    def _initialize_arguments(self):
        """Initializes the task arguments, setting the task_runner_root and
        additional_args based on the command line arguments. If no arguments are
        provided, uses the default root and arguments."""
        if len(sys.argv) < 2 or self._force_defaults:
            self.task_runner_root = self.default_root
            self.additional_args = self.default_args
            sys.path.append(self.task_runner_root)
        else:
            self.task_runner_root = sys.argv[1]
            self.additional_args = sys.argv[2:]

    def setup(self):
        """Sets up the task environment. Initializes the task profile and creates
        the tasks_cache directory."""
        self._initialize_arguments()
        self.profile = TaskRunnerProfile(self.task_runner_root)
        self.tasks_cache_dir = self.profile.tasks_cache
        self.runners_cache_dir = self.profile.runners_cache

        os.makedirs(self.tasks_cache_dir, exist_ok=True)
        os.makedirs(self.runners_cache_dir, exist_ok=True)

    @abstractmethod
    def execute(self):
        """Executes the task's main functionality. Must be implemented by
        subclasses."""

    def teardown(self):
        """Cleans up the task environment. Removes the tasks_cache directory if it
        exists."""
        if self.tasks_cache_dir and os.path.exists(self.tasks_cache_dir):
            shutil.rmtree(self.tasks_cache_dir)
        if self.runners_cache_dir and os.path.exists(self.runners_cache_dir):
            shutil.rmtree(self.runners_cache_dir)

    def _print_execution_start(self):
        """Prints the start message for task execution. Provides information about
        the task being started."""
        msg = f"{'='*55} TASK START {'='*53}\n"
        msg += f"Runned Task: {self.NAME}\n{self.line_sep}"
        msg += "Task Outputs:\n"
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
        """The main method to manage the flow of task execution. Executes the task
        by calling setup, execute, and teardown methods successively."""
        self._print_execution_start()
        self.setup()
        self.execute()
        self.teardown()
        self._print_execution_end()
