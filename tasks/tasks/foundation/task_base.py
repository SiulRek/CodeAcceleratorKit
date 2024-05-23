from abc import ABC, abstractmethod
import os
import sys
import shutil

from tasks.tasks.management.task_session import TaskSession


class TaskBase(ABC):
    """
    Base class for task execution, providing setup and common utilities for all tasks.
    
    Attributes:
    - NAME (str): A class-level attribute that identifies the name of the task.
    """

    NAME = None

    def __init__(self, default_root, *default_args):
        """
        Initializes the task with default root and additional arguments.
        
        Args:
        - default_root (str): The default root directory for task execution.
        - default_args (tuple): Additional default arguments required by the task.
        """
        self.task_runner_root = None
        self.additional_args = None
        self.cache_dir = None
        self._initialize_arguments(default_root, default_args)
        self.line_sep = "-" * 120 + "\n"

    def _initialize_arguments(self, default_root, default_args):
        """
        Processes command line arguments and sets the task root and additional arguments.
        
        Args:
        - default_root (str): The default root directory if no command line argument is provided.
        - default_args (tuple): Default arguments to use if no additional command line arguments are provided.
        """
        if len(sys.argv) < 2:
            self.task_runner_root = default_root
            self.additional_args = default_args
            sys.path.append(self.task_runner_root)
        else:
            self.task_runner_root = sys.argv[1]
            self.additional_args = sys.argv[2:]

    def setup(self):
        """
        Sets up the task environment.
        Initializes the task session and creates the cache directory.
        """
        self.session = TaskSession(self.task_runner_root)
        self.cache_dir = self.session.cache
        os.makedirs(self.cache_dir, exist_ok=True)

    @abstractmethod
    def execute(self):
        """
        Executes the task's main functionality.
        Must be implemented by subclasses.
        """

    def teardown(self):
        """
        Cleans up the task environment.
        Removes the cache directory if it exists.
        """
        if self.cache_dir and os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)

    def _print_execution_start(self):
        """
        Prints the start message for task execution.
        Provides information about the task being started.
        """
        msg = f"{'='*55} TASK START {'='*53}\n"
        msg += f"Runned Task: {self.NAME}\n{self.line_sep}"
        msg += "Task Outputs:\n"
        print(msg)

    def _print_execution_end(self, additional_msg=""):
        """
        Prints the end message for task execution, indicating completion.
        
        Args:
        - additional_msg (str): Optional additional message to include in the completion printout.
        """
        msg = self.line_sep
        msg += "TASK EXECUTED SUCCESSFULLY\n"
        msg += f"{'='*55} TASK END {'='*55}"
        if additional_msg:
            msg += f"\n{additional_msg}"
        print(msg)

    def main(self):
        """
        The main method to manage the flow of task execution.
        Executes the task by calling setup, execute, and teardown methods successively.
        """
        self._print_execution_start()
        self.setup()
        self.execute()
        self.teardown()
        self._print_execution_end()
