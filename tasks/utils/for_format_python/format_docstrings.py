import re
from textwrap import wrap as wrap_text

from tasks.configs.constants import DOC_QUOTE, LINE_WIDTH, INTEND
from tasks.utils.for_format_python.wrap_text import wrap_text


# TODO: Handle the case of string with """ that is not a docstring
def count_leading_spaces(line):
    return len(line) - len(line.lstrip())


def get_docstrings(code):
    """
    Extracts docstrings from the code and returns them as a list.

    Args:
        - code (str): The code from which the docstrings are to be
            extracted.

    Returns:
        - list: A list of docstrings extracted from the code.
    """
    code_lines = code.split("\n")
    lines_iter = iter(code_lines)
    docstrings = []
    updated_code = ""

    while True:
        try:
            line = next(lines_iter)
            stripped_line = line.strip()
            if not stripped_line.startswith(DOC_QUOTE):
                updated_code += line + "\n"
            else:
                docstring = line + "\n"
                stripped_line = stripped_line[3:]
                try:
                    while not stripped_line.endswith(DOC_QUOTE):
                        line = next(lines_iter)
                        docstring += line + "\n"
                        stripped_line = line.strip()
                except StopIteration:
                    msg += "Invalid docstring format "
                    raise ValueError(msg)
                docstrings.append(docstring[:-1])

        except StopIteration:
            break
    return docstrings


def clean_docstrings(docstrings):
    """
    Cleans the docstrings by ensuring that the triple quotes are on their own
    lines.

    Args:
        - docstrings (list): A list of docstrings to be cleaned.

    Returns:
        - list: A list of cleaned docstrings.
    """
    cleaned_docstrings = []
    for docstring in docstrings:
        cleaned_docstring = ""
        docstring_lines = docstring.splitlines()

        if len(docstring_lines) == 1:
            leading_spaces = " " * count_leading_spaces(docstring_lines[0])
            text = docstring_lines[0].replace(DOC_QUOTE, "").strip()
            cleaned_docstring += leading_spaces + DOC_QUOTE + "\n"
            cleaned_docstring += leading_spaces + text + "\n"
            cleaned_docstring += leading_spaces + DOC_QUOTE
            cleaned_docstrings.append(cleaned_docstring)
            continue

        for line in docstring_lines:
            stripped_line = line.strip()
            if stripped_line.startswith(DOC_QUOTE) and not stripped_line.endswith(
                DOC_QUOTE
            ):
                parts = line.split(DOC_QUOTE)
                leading_spaces = " " * count_leading_spaces(parts[0])
                cleaned_docstring += leading_spaces + DOC_QUOTE + "\n"
                cleaned_docstring += leading_spaces + parts[1] + "\n"
            elif stripped_line.endswith(DOC_QUOTE) and not stripped_line.startswith(
                DOC_QUOTE
            ):
                parts = line.split(DOC_QUOTE)
                leading_spaces = " " * count_leading_spaces(parts[0])
                cleaned_docstring += parts[0] + "\n"
                cleaned_docstring += leading_spaces + DOC_QUOTE
            else:
                cleaned_docstring += line + "\n"
        cleaned_docstrings.append(cleaned_docstring)
    return cleaned_docstrings


def check_new_item(line):
    pattern = r": [a-zA-Z]"
    match = re.search(pattern, line)
    return match is not None


def startswith_enumaration_symbol(line, include_dashed=True):
    line = line.strip()
    numbered = line.split(".")[0].isdigit()
    bulleted = line.startswith("° ") or line.startswith("* ")
    if include_dashed:
        bulleted = bulleted or line.startswith("- ")
    return numbered or bulleted


def check_freezing_required(text):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if startswith_enumaration_symbol(line, include_dashed=i > 0):
            # If the line has a enumaration symbol, we assume modification is
            # not wanted, so we freeze the text.
            return True
    undefined_symbols = [
        "<<<",
        ">>>",
        "```",
        "´´´´",
    ]
    return any([symbol in text for symbol in undefined_symbols])


def intend_text(text, intend_number):
    lines = text.splitlines()
    lines = [INTEND * intend_number + line for line in lines]
    return "\n".join(lines)


def wrap_metadata_text(text, leading_spaces):
    """
    Wraps metadata text that contains colons or dashes.

    Args:
        - text (str): The text to be wrapped.
        - leading_spaces (str): The leading spaces to be added to the
            wrapped text.

    Returns:
        - str: The wrapped text.
    """
    first_line = text.splitlines()[0].strip()
    first_line = wrap_text(first_line, width=LINE_WIDTH - len(leading_spaces))

    body = text.splitlines()[1:]
    items_intendation = leading_spaces + INTEND
    items = []
    for line in body:
        line = line.strip()
        if check_new_item(line):
            items.append(line)
        elif items != []:
            items[-1] += "\n" + line
        else:
            items.append(line)

    if len(items) == 0:
        return first_line

    # if len(items) == 1: return first_line + "\n" + items[0]

    updated_items = []
    for item in items:
        if check_freezing_required(item):
            frozen = intend_text(item, 1)
            updated_items.append(frozen)
            continue
        prefix = "- " if not item.startswith("-") else ""
        item = prefix + item
        max_intend_length = len(items_intendation) + len(
            INTEND
        )  ## Following line of item intend more than first
        item = wrap_text(item, width=LINE_WIDTH - max_intend_length)
        item = intend_text(item, 2)
        item = item.removeprefix(INTEND)
        updated_items.append(item)

    wrapped_text = first_line + "\n" + "\n".join(updated_items)
    return wrapped_text


def wrap_docstring(docstring, leading_spaces):
    """
    Wraps the docstring to the specified width.

    Args:
        - docstring (str): The docstring to be wrapped.
        - leading_spaces (str): The leading spaces to be added to the
            wrapped docstring.

    Returns:
        - str: The wrapped docstring.
    """
    first_line = docstring.splitlines()[0]
    first_line = leading_spaces + first_line
    last_line = docstring.splitlines()[-1]
    last_line = leading_spaces + last_line
    docstring = "\n".join(docstring.splitlines()[1:-1])
    sections = docstring.split("\n\n")

    wrapped_sections = []

    def append_to_wrapped_sections(section):
        intend_number = len(leading_spaces) // len(INTEND)
        section = intend_text(section, intend_number)
        wrapped_sections.append(section)

    for section in sections:
        start = section.split("\n")[0]
        if start.strip().endswith(":"):
            wrapped_section = wrap_metadata_text(section, leading_spaces)
            append_to_wrapped_sections(wrapped_section)
        elif check_freezing_required(section):
            # No modification required.
            append_to_wrapped_sections(section)
        else:
            wrapped_section = wrap_text(section, width=LINE_WIDTH - len(leading_spaces))
            append_to_wrapped_sections(wrapped_section)
    wrapped_sections = "\n\n".join(wrapped_sections)

    if len(wrapped_sections.splitlines()) > 2:
        sep = "\n"
    else:
        wrapped_sections = wrapped_sections[len(leading_spaces) :]
        last_line = last_line.replace(leading_spaces, "")
        sep = " "
    wrapped_docstring = first_line + sep + wrapped_sections + sep + last_line
    return wrapped_docstring


def wrap_docstrings(docstrings):
    """
    Wraps the docstrings to the specified width.

    Args:
        - docstrings (list): A list of docstrings to be wrapped.

    Returns:
        - list: A list of wrapped docstrings.
    """
    wrapped_docstrings = []
    for docstring in docstrings:
        first_line = docstring.splitlines()[0]
        leading_spaces = " " * count_leading_spaces(first_line)
        docstring = docstring.replace(leading_spaces, "")
        wrapped_docstring = wrap_docstring(docstring, leading_spaces)
        wrapped_docstrings.append(wrapped_docstring)
    return wrapped_docstrings


def format_docstrings(code):
    """
    Formats the docstrings in the code.

    Args:
        - code (str): The code to be formatted.

    Returns:
        - str: The code with the formatted docstrings.
    """
    docstrings = get_docstrings(code)
    cleaned_docstrings = clean_docstrings(docstrings)
    updated_code = code
    wrapped_docstrings = wrap_docstrings(cleaned_docstrings)
    for original, updated in zip(docstrings, wrapped_docstrings):
        updated_code = updated_code.replace(original, updated)

    return updated_code


def format_docstrings_from_file(file_path):
    """
    Formats the docstrings in the file.

    Args:
        - file_path (str): The path to the file to be formatted.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()
    updated_code = format_docstrings(code)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_code)


if __name__ == "__main__":
    path = r"tasks/tests/for_tasks/format_python_test.py"
    format_docstrings_from_file(path)
    print(f"Docstrings formatted of {path}")
