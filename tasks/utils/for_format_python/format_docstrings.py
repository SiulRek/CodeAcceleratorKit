import re
from textwrap import wrap as wrap_text

from tasks.configs.constants import DOC_QUOTE, LINE_WIDTH, INDENT_SPACES
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
                    msg = "Invalid docstring format "
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


def has_enumeration_symbol(text):
    for line in text.splitlines():
        line = line.strip()
        numbered = line.split(".")[0].isdigit()
        bulleted = line.startswith(("° ", "* ", "- "))
        if numbered or bulleted:
            return True
    return False


def has_docstring_keyword(line):
    keys = [
        "Args:",
        "Arguments:",
        "Parameters:",
        "Returns:",
        "Raises:",
        "Attributes:",
        "Methods:",
    ]
    return any([key in line for key in keys])


def has_undefined_symbols(text):
    undefined_symbols = [
        "<<<",
        ">>>",
        "```",
        "´´´´",
    ]
    if any([symbol in text for symbol in undefined_symbols]):
        return True


def is_freezing_needed(text):
    return (
        has_undefined_symbols(text)
        or has_docstring_keyword(text)
        or has_enumeration_symbol(text)
    )


def indent_text(text, intend_number):
    lines = text.splitlines()
    lines = [INDENT_SPACES * intend_number + line for line in lines]
    return "\n".join(lines)


def unindent_text(text, unindent_number):
    lines = text.splitlines()
    lines = [line[unindent_number:] for line in lines]
    return "\n".join(lines)


def wrap_text_with_indent(text, indent_length):
    text = unindent_text(text, indent_length)
    wrapped_text = wrap_text(
        text, width=LINE_WIDTH - indent_length * len(INDENT_SPACES)
    )
    wrapped_text = indent_text(wrapped_text, indent_length)
    return wrapped_text


def wrap_metadata_text(text):
    """
    Wraps metadata text that contains.

    Args:
        - text (str): The text to be wrapped.

    Returns:
        - str: The wrapped text.
    """

    root_indent_length = last_indent_length = count_leading_spaces(text) // len(
        INDENT_SPACES
    )
    wrapped_text = ""
    text_buffer = ""
    end_tag = "$$ENDTAG$$"
    lines = (text + "\n" + end_tag).splitlines()
    for i, line in enumerate(lines):
        if line == end_tag:
            if not is_freezing_needed(text_buffer):
                text_buffer = wrap_text_with_indent(text_buffer, last_indent_length)
            wrapped_text += "\n" + text_buffer if wrapped_text else text_buffer
            break
        cur_indent_length = count_leading_spaces(line) // len(INDENT_SPACES)
        if cur_indent_length == root_indent_length:
            if text_buffer:
                if not is_freezing_needed(text_buffer):
                    text_buffer = wrap_text_with_indent(text_buffer, last_indent_length)
                wrapped_text += "\n" + text_buffer if wrapped_text else text_buffer
                # Line with same indent length as root does not need to be
                # wrapped
                wrapped_text += "\n" + line if text_buffer else line
                text_buffer = ""
            else:
                wrapped_text += "\n" + line if wrapped_text else line
        elif cur_indent_length != last_indent_length and last_indent_length != root_indent_length:
            raise ValueError(
                "Inconsistent indentation detected in metadata. "
                "Lines with non-root indentation must maintain the same level as the previous line. "
                f"Mismatch found between lines:\n {lines[i-1]} and \n{lines[i]}."
            )
        else:
            text_buffer += "\n" + line if text_buffer else line
        last_indent_length = cur_indent_length

    return wrapped_text


def wrap_docstring(docstring):
    """
    Wraps the docstring to the specified width.

    Args:
        - docstring (str): The docstring to be wrapped.
            wrapped docstring.

    Returns:
        - str: The wrapped docstring.
    """
    leading_spaces = " " * count_leading_spaces(docstring)
    start_quote = leading_spaces + docstring.splitlines()[0].strip()
    end_quote = leading_spaces + docstring.splitlines()[-1].strip()
    docstring = "\n".join(docstring.splitlines()[1:-1])
    sections = docstring.split("\n\n")

    wrapped_sections = []
    for section in sections:
        section_lines = section.splitlines()
        if len(section_lines) >= 2:
            first_line = section_lines[0].strip()
            second_line = section_lines[1].strip()
            is_metadata = first_line in ["Parameters", "Returns", "Raises"]
            is_metadata = all([l == "-" for l in second_line]) and is_metadata
        else:
            is_metadata = False
        if is_metadata:
            # The section is identified as metadata.
            header = "\n".join(section_lines[:2])
            body = "\n".join(section_lines[2:])
            wrapped_body = wrap_metadata_text(body)
            wrapped_section = header + "\n" + wrapped_body
        elif is_freezing_needed(section):
            # No modification required.
            wrapped_section = section
        else:
            indent_length = len(leading_spaces) // len(INDENT_SPACES)
            wrapped_section = wrap_text_with_indent(section, indent_length)

        wrapped_sections.append(wrapped_section)
    wrapped_sections = "\n\n".join(wrapped_sections)
    wrapped_docstring = start_quote + "\n" + wrapped_sections + "\n" + end_quote
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
        wrapped_docstring = wrap_docstring(docstring)
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
    path = r"/home/siulrek/MY_ROOM/github/CodeAcceleratorKit/tasks/controllers/magic_scripts/magic_register_runner.py"
    format_docstrings_from_file(path)
    print(f"Docstrings formatted of {path}")
