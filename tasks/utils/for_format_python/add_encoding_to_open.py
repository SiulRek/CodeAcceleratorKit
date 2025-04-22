import re


def add_encoding_to_open(code):
    """
    Checks for 'with open(<arguments>)' patterns in the given code and ensures
    'encoding="utf-8"' is provided. If not, it adds the encoding parameter.

    Parameters
    ----------
    code (str)
        The code to be checked and updated.

    Returns
    -------
    str
        The updated code with encoding added to 'open' functions.
    """
    pattern = re.compile(r"with open\(([^)]*)\)")
    lines = code.splitlines()
    updated_lines = []

    for line in lines:
        match = pattern.search(line)
        if match:
            params = match.group(1)
            if "encoding" not in params:
                if params.endswith(","):
                    new_params = f'{params} encoding="utf-8"'
                else:
                    new_params = f'{params}, encoding="utf-8"'
                updated_line = line.replace(params, new_params)
                updated_lines.append(updated_line)
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)

    return "\n".join(updated_lines) + "\n"


def add_encoding_to_open_from_file(file_path):
    """
    Checks for 'with open(...)' patterns in the file and ensures
    'encoding="utf-8"' is provided. If not, it adds the encoding parameter.

    Parameters
    ----------
    file_path (str)
        The path to the file to be checked and updated.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()
    updated_code = add_encoding_to_open(code)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_code)


if __name__ == "__main__":
    path = r"./tasks/tests/data/example_script_2.py"
    add_encoding_to_open_from_file(path)
    print(f"Added encoding to open functions in {path}")
