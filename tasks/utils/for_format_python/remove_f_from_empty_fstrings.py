import re

def remove_f_from_empty_fstrings(code):
    """
    Removes the 'f' from f-strings that do not contain any interpolated variables.

    Args:
        - code (str): The code to be checked and updated.

    Returns:
        - str: The updated code with 'f' removed from empty f-strings.
    """
    pattern = re.compile(r'f"([^{}]*)"')
    lines = code.splitlines()
    updated_lines = []

    for line in lines:
        match = pattern.search(line)
        if match:
            content = match.group(1)
            updated_line = line.replace(f'f"{content}"', f'"{content}"')
            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)

    return "\n".join(updated_lines)


def remove_f_from_empty_fstrings_from_file(file_path):
    """
    Removes the 'f' from f-strings in the file if they do not contain any interpolated variables.

    Args:
        - file_path (str): The path to the file to be checked and updated.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()
    updated_code = remove_f_from_empty_fstrings(code)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_code)


if __name__ == "__main__":
    path = r"./tasks/tests/data/example_script_2.py"
    remove_f_from_empty_fstrings_from_file(path)
    print(f"Removed 'f' from empty f-strings in {path}")