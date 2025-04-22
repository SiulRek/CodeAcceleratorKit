from tasks.configs.constants import INDENT_SPACES

INTEND_LEN = len(INDENT_SPACES)


def remove_unnecessary_else(code):
    """
    Removes unnecessary 'else' statements that follow 'raise' or 'return'
    statements.

    Parameters
    ----------
    code (str)
        The code to be checked and updated.

    Returns
    -------
    str
        The updated code with unnecessary 'else' statements removed.
    """
    lines = code.splitlines()
    updated_lines = []
    # The indentation level of the 'raise' or 'return' statement if found in previous line, else None
    i = 0
    indentation_recorded = None

    while i < len(lines):
        line = lines[i]
        lstripped_line = line.strip()
        current_indentation = len(line) - len(lstripped_line)

        if indentation_recorded:
            if lstripped_line.startswith("else:"):
                else_indentation = current_indentation
                # Only remove 'else' if its block is one level higher than the 'raise' or 'return' statement
                if (
                    indentation_recorded is not None
                    and else_indentation == indentation_recorded - INTEND_LEN
                ):
                    i += 1
                    while (
                        i < len(lines)
                        and (len(lines[i]) - len(lines[i].lstrip())) > else_indentation
                    ):
                        updated_lines.append(lines[i][4:])
                        i += 1
                    indentation_recorded = None
                    continue
            if lstripped_line.startswith("elif"):
                elif_indentation = current_indentation
                # Only replace 'elif' with 'if' if its block is one level higher than the 'raise' or 'return' statement
                if (
                    indentation_recorded is not None
                    and elif_indentation == indentation_recorded - INTEND_LEN
                ):
                    line = line.replace("elif", "if")
                    updated_lines.append(line)
                    i += 1
                    indentation_recorded = None
                    continue

        if lstripped_line.startswith("raise") or lstripped_line.startswith("return"):
            indentation_recorded = current_indentation
        else:
            indentation_recorded = None

        updated_lines.append(line)
        i += 1

    return "\n".join(updated_lines)


def remove_unnecessary_else_from_file(file_path):
    """
    Removes unnecessary 'else' statements from the file if they follow 'raise'
    or 'return' statements.

    Parameters
    ----------
    file_path (str)
        The path to the file to be checked and updated.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()
    updated_code = remove_unnecessary_else(code)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_code)


if __name__ == "__main__":
    path = r"./tasks/tests/data/example_script_2.py"
    remove_unnecessary_else_from_file(path)
    print(f"Removed unnecessary 'else' statements in {path}")
