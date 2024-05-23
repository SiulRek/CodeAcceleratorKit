from abc import ABC, abstractmethod


class MacroEngine(ABC):
    """
    A base class for extracting macros from files based on specified validation methods used in Tasks.

    This class stores the session object of the running task and provides the foundational mechanisms 
    to identify and extract macros from the current file types.

    Attributes:
        session (object): The current session object of the running task.

    Methods:
        - extract_macros: Extract macros from a file and separates them from
            non-referenced content.
        - post_process_macros: Provide a hook for child classes to further
            process the extracted macros.
    """

    def __init__(self, session):
        """
        Initializes the MacroEngine with the provided session.

        Args:
            session (object): The session object of the running task.
        """
        self.session = session
        self.initialize_validation_methods()

    def initialize_validation_methods(self):
        """Initializes the validation methods for extracting macros from the text."""
        self.validation_methods = [
            getattr(self, method)
            for method in dir(self)
            if callable(getattr(self, method)) and method.startswith("validate_")
        ]

    def _extract_macros(self, text):
        """
        Extracts macros and updated text from the input text based on
        validation methods.

        Args:
            - text (str): The text to extract macros from.

        Returns:
            - tuple: A tuple containing a list of extracted macros and
                the updated text.
        """
        macros = []
        updated_text_lines = []

        for line in text.splitlines():
            result = None
            stripped_line = line.strip()
            for val in self.validation_methods:
                if result := val(stripped_line):
                    if isinstance(result, list):
                        macros.extend(result)
                    else:
                        macros.append(result)
                    break
            if not result:
                updated_text_lines.append(line)
        updated_text = "\n".join(updated_text_lines)
        return macros, updated_text

    def extract_macros(self, file_path):
        """
        Extracts macros from a specified file using validation methods, while maintaining the order of their occurrence.

        This method iterates through each line of the file, applying validation
        methods that start with 'validate_' to detect and extract specific
        content based on tags or patterns. The results may include a single item
        or an aggregated list of items, based on the complexity of the
        validation logic. The non-referenced text is updated to exclude the
        extracted content, enhancing clarity and separation.

        Args:
            - file_path (str): The path to the file from which to extract
                content.

        Returns:
            - tuple: A tuple where the first element is the result of
                post-processing the extracted macros, defined in child
                classes, and the second element is the updated text stripped of
                macros.
        """
        self.file_path = file_path

        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
            macros, updated_text = self._extract_macros(text)

        process_results = self.post_process_macros(macros)
        return process_results, updated_text

    @abstractmethod
    def post_process_macros(self, macros):
        """
        Processes the collected macros for final output.

        This method must be overridden by child classes to implement custom
        processing of the extracted macros, such as merging related items or
        filtering out specific results.

        Args:
            - macros (list): The list of macros collected by the validation
                methods.

        Returns:
            - custom_type: A custom type or list of macros after
                post-processing.
        """