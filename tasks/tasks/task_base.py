import sys

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
        self.cache_dir = get_task_cache_directory
        self._initialize_arguments(default_root, default_args)

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
        """Placeholder for task-specific setup. Should be implemented by
        subclasses."""
        pass

    def execute(self):
        """Executes the task's main functionality. Must be implemented by
        subclasses."""
        msg = "Subclasses should implement this method."
        raise NotImplementedError(msg)

    def _print_execution_start(self):
        """Prints the start message for task execution."""
        msg = f"{'-'*100}\nRunned Task: {self.NAME}\n{'-'*100}"
        print(msg)

    def _print_execution_end(self, additional_msg=""):
        """
        Prints the end message for task execution, indicating completion.

        Args:
            - additional_msg (str): Optional additional message to include
                in the completion printout.
        """
        msg = f"{'='*50} TASK EXECUTED SUCCESSFULLY {'='*50}"
        if additional_msg:
            msg += f"\n{additional_msg}"
        print(msg)

    def main(self):
        """The main method to manage the flow of task execution."""
        self._print_execution_start()
        self.setup()
        self.execute()
        self._print_execution_end()
