from abc import ABC, abstractmethod
import inspect

class MacroInterpreter(ABC):
    """
    A base class for extracting macros from files based on specified validation
    methods used in Tasks.

    This class stores the profile object of the running task and provides the
    foundational mechanisms to identify and extract macros from the current
    file types.

    Attributes
    ----------
    profile (object)
        The current profile object of the running task.

    Methods
    -------
    extract_macros
        Extract macros from a file and separate them from non-referenced
        content.
    post_process_macros
        Provide a hook for child classes to further process the extracted
        macros.
    """

    def __init__(self, profile):
        """
        Initializes the MacroInterpreter with the provided profile.

        Parameters
        ----------
        profile (object)
            The profile object of the running task.
        """
        self.profile = profile
        self.initialize_validation_methods()

    def initialize_validation_methods(self):
        """
        Initializes the validation methods for oextracting macros from the
        text.
        """
        source = inspect.getsource(self.__class__)

        # The order of the methods corresponds to the order of their occurrence in the source code.
        method_names = [
            line.split()[1].split('(')[0]
            for line in source.splitlines()
            if line.strip().startswith('def validate_')
        ]
        self.validation_methods = [
            getattr(self, method)
            for method in method_names
            if callable(getattr(self, method))
        ]


    def extract_macros_from_text(self, text, post_process=False):
        """
        Extracts macros and updated text from the input text based on
        validation methods.

        Parameters
        ----------
        text (str)
            The text to extract macros from.
        post_process (bool)
            Whether to post-process the extracted macros or not.

        
        Returns:
            - tuple: macros_data or the post-processed macros.
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

        if post_process:
            return self.post_process_macros(macros), updated_text
        return macros, updated_text

    def extract_macros_from_file(self, file_path):
        """
        Extracts macros from a specified file using validation methods, while
        maintaining the order of their occurrence.

        This method iterates through each line of the file, applying validation
        methods that start with 'validate_' to detect and extract specific
        content based on tags or patterns. The results may include a single
        item or an aggregated list of items, based on the complexity of the
        validation logic. The non-referenced text is updated to exclude the
        extracted content, enhancing clarity and separation.

        Parameters
        ----------
        file_path (str)
            The path to the file from which to extract content.

        Returns
        -------
        tuple
            A tuple where the first element is the result of post-processing
            the extracted macros, defined in child classes, and the second
            element is the updated text stripped of macros.
        """
        self.current_file = file_path

        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
            macros, updated_text = self.extract_macros_from_text(text)

        process_results = self.post_process_macros(macros)
        return process_results, updated_text

    @abstractmethod
    def post_process_macros(self, macros):
        """
        Processes the collected macros for final output.

        This method must be overridden by child classes to implement custom
        processing of the extracted macros, such as merging related items or
        filtering out specific results.

        Parameters
        ----------
        macros (list)
            The list of macros collected by the validation methods.

        Returns
        -------
        custom_type
            A custom type or list of macros after post-processing.
        """