import ast
import re

ROUND_BRACKET_PATTERN = re.compile(r"\((.*?)\)")

def check_type(value, expected_type, additional_error_message=""):
    """Check if the value is of the expected type."""
    if not isinstance(value, expected_type):
        msg = f"Expected {expected_type}, but got {type(value)}"
        msg += f"{additional_error_message}"
        raise ValueError(msg)

def retrieve_arguments_in_round_brackets(string, max_args=float("inf")):
    """
    Retrieve the arguments in round brackets.

    Args:
        - string (str): The string to retrieve the arguments from.
        - max_args (int): The maximum number of arguments expected.
            Otherwise, an error is raised.

    Returns:
        - tuple: The arguments in the round brackets or None if there are no arguments.
    """
    match = re.search(ROUND_BRACKET_PATTERN, string)
    if match:
        try:
            literal = match.group(0).replace(")", ",)")
            result = ast.literal_eval(literal)
            if len(result) > max_args:
                msg = f"Expected at most {max_args} arguments, but got {len(result)}"
                raise ValueError(msg)
            return result
        except (ValueError, SyntaxError) as e:
            msg = f"Evaluation of the arguments in round brackets failed: {str(e)}"
            raise ValueError(msg)
    else:
        return None
    
