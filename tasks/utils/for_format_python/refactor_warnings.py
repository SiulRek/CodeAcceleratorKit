import re

from tasks.configs.constants import LINE_WIDTH
from tasks.utils.for_format_python.wrap_text import wrap_text


def add_quotes(string, quote):
    """
    Adds quotes to the provided string.

    Args:
        - string (str): The string to which quotes are to be added.
        - quote (str): The quote to be added.

    Returns:
        - str: The string with quotes added.
    """
    if "{" in string and "}" in string:
        string = f"f{quote}{string}{quote}"
    else:
        string = f"{quote}{string}{quote}"
    return string


def refactor_warnings(code):
    """
    Refactors warnings in the provided code. The refactored code will have the
    warning message stored in a variable before calling the warnings.warn()
    function.

    Args:
        - code (str): The code to be refactored.

    Returns:
        - str: The refactored code.
    """
    lines = code.splitlines()
    updated_lines = []
    for i, line in enumerate(lines):
        match = re.search(r"(\s*)warnings\.warn\((f?'.*'|f?\".*\")\)", line)
        if match:
            indent = match.group(1)
            msg_with_q = match.group(2)
            q = msg_with_q[-1]
            if msg_with_q.startswith("f"):
                msg = msg_with_q[2:-1]
            else:
                msg = msg_with_q[1:-1]

            msg = wrap_text(
                msg,
                LINE_WIDTH - len(indent) - 9,  # Adjust the length for proper wrapping
            )

            start = True
            for msg_line in msg.splitlines():
                if start:
                    start = False
                    updated_line = f"{indent}msg = {add_quotes(msg_line, q)}"
                    updated_lines.append(updated_line)
                else:
                    updated_line = f"{indent}msg += {add_quotes(msg_line, q)}"
                    updated_lines.append(updated_line)

            updated_line = f"{indent}warnings.warn(msg)"
            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)
    return "\n".join(updated_lines)


def refactor_warnings_from_file(file_path):
    """
    Refactors the warning code in the file.

    Args:
        - file_path (str): The path to the file to be refactored.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()
    updated_code = refactor_warnings(code)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_code)


if __name__ == "__main__":
    path = r"tasks/tests/data/example_script_4.py"
    refactor_warnings_from_file(path)
    print(f"Refactored warnings in {path}")
