# As format docstring previously supported another format, this script was
# created to convert the docstrings to the now supported Numpy format.

import re
import warnings

from tasks.configs.constants import DOC_QUOTE, INDENT_SPACES


# TODO: Handle the case of string with """ that is not a docstring
def _count_leading_spaces(line):
    return len(line) - len(line.lstrip())


def _get_docstrings(code):
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
                    msg = "Invalid docstring numpyify "
                    raise ValueError(msg)
                docstrings.append(docstring[:-1])

        except StopIteration:
            break
    return docstrings


def _clean_docstrings(docstrings):
    cleaned_docstrings = []
    for docstring in docstrings:
        cleaned_docstring = ""
        docstring_lines = docstring.splitlines()

        if len(docstring_lines) == 1:
            leading_spaces = " " * _count_leading_spaces(docstring_lines[0])
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
                leading_spaces = " " * _count_leading_spaces(parts[0])
                cleaned_docstring += leading_spaces + DOC_QUOTE + "\n"
                cleaned_docstring += leading_spaces + parts[1] + "\n"
            elif stripped_line.endswith(DOC_QUOTE) and not stripped_line.startswith(
                DOC_QUOTE
            ):
                parts = line.split(DOC_QUOTE)
                leading_spaces = " " * _count_leading_spaces(parts[0])
                cleaned_docstring += parts[0] + "\n"
                cleaned_docstring += leading_spaces + DOC_QUOTE
            else:
                cleaned_docstring += line + "\n"
        cleaned_docstrings.append(cleaned_docstring)
    return cleaned_docstrings


def _indent_text(text, intend_number):
    lines = text.splitlines()
    lines = [INDENT_SPACES * intend_number + line for line in lines]
    return "\n".join(lines)


def _check_new_item(line):
    pattern = r": [a-zA-Z]"
    match = re.search(pattern, line)
    return match is not None and line.strip().startswith("-")


def _startswith_enumaration_symbol(line, include_dashed=True):
    line = line.strip()
    numbered = line.split(".")[0].isdigit()
    bulleted = line.startswith("° ") or line.startswith("* ")
    if include_dashed:
        bulleted = bulleted or line.startswith("- ")
    return numbered or bulleted


def _check_freezing_required(text):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if _startswith_enumaration_symbol(line, include_dashed=i > 0):
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


def _numpyify_metadata_text(text):
    lines = text.splitlines()
    header = lines[0].strip()
    body = lines[1:]
    m_type = header.split(":")[0].strip().removeprefix("-").strip()
    additional_mtypes = [
        "Warnings",
        "Warning",
        "Methods",
        "Method",
        "Attributes",
        "Attribute",
        "Yields",
        "Yield",
        "Notes",
        "Note",
        "Examples",
        "Example",
        "Usage",
        "References",
        "Reference",
    ]
    if m_type in ["Args", "Arguments", "Parameters"]:
        header = "Parameters\n" + "-" * 10
    elif m_type in ["Returns", "Return"]:
        header = "Returns\n" + "-" * 7
    elif m_type in ["Raises", "Raise"]:
        header = "Raises\n" + "-" * 5
    elif m_type in additional_mtypes:
        header = m_type + "\n" + "-" * len(m_type)
    # else:
    #     raise ValueError(
    #         f"Unknown metadata type: {m_type}."
    #     )

    items = []
    for line in body:
        line = line.strip()
        if _check_new_item(line):
            items.append(line)
        elif items != []:
            items[-1] += "\n" + line
        else:
            items.append(line)

    udpated_items = []
    for item in items:
        if _check_freezing_required(item):
            # raise ValueError( "The metadata item contains an enumeration
            # symbol or " "undefined symbols, indicating that it should not be "
            # f"modified for numpyifyting. \nOffending Item:\n{item}" )
            warnings.warn(
                "The metadata item contains an enumeration symbol or "
                "undefined symbols, indicating that it should not be "
                f"modified for numpyifyting. \nOffending Item:\n{item}"
            )
            udpated_items.append(item)
            continue
        # Replace the first occurence of ": " with "\n"
        item = re.sub(r":\s+", "\n", item, count=1)
        lines = item.splitlines()
        first_line = lines[0].lstrip().removeprefix("-").lstrip()
        item = first_line + "\n" + _indent_text("\n".join(lines[1:]), 1)
        udpated_items.append(item)

    numpyifyted_text = header + "\n" + "\n".join(udpated_items)
    return numpyifyted_text


def _numpyify_docstring(docstring, leading_spaces):
    first_line = docstring.splitlines()[0]
    first_line = leading_spaces + first_line
    last_line = docstring.splitlines()[-1]
    last_line = leading_spaces + last_line
    content = "\n".join(docstring.splitlines()[1:-1])
    sections = content.split("\n\n")

    numpyifyted_sections = []

    def append_to_numpyifyted_sections(section):
        indent_number = len(leading_spaces) // len(INDENT_SPACES)
        section = _indent_text(section, indent_number)
        numpyifyted_sections.append(section)

    for section in sections:
        start = section.split("\n")[0]
        if start.strip().endswith(":"):
            numpyifyted_section = _numpyify_metadata_text(section)
            append_to_numpyifyted_sections(numpyifyted_section)
        else:
            # No modification required.
            append_to_numpyifyted_sections(section)
    numpyifyted_sections = "\n\n".join(numpyifyted_sections)

    numpyifyted_docstring = first_line + "\n" + numpyifyted_sections + "\n" + last_line
    return numpyifyted_docstring


def _numpyify_docstrings(docstrings):
    numpyifyted_docstrings = []
    for docstring in docstrings:
        leading_spaces = " " * _count_leading_spaces(docstring)
        lines = [
            line[len(leading_spaces) :] if line.startswith(leading_spaces) else line
            for line in docstring.splitlines()
        ]
        docstring = "\n".join(lines)
        numpyifyted_docstring = _numpyify_docstring(docstring, leading_spaces)
        numpyifyted_docstrings.append(numpyifyted_docstring)
    return numpyifyted_docstrings


def _numpyify_doctrings_from_code(code):
    docstrings = _get_docstrings(code)
    cleaned_docstrings = _clean_docstrings(docstrings)
    updated_code = code
    numpyifyted_docstrings = _numpyify_docstrings(cleaned_docstrings)
    for original, updated in zip(docstrings, numpyifyted_docstrings):
        updated_code = updated_code.replace(original, updated)

    return updated_code


def numpyify_docstrings_from_file(file_path):
    """
    Reformats the docstrings in a Python file to Numpy style.

    Parameters
    ----------
    file_path (str)
        The path to the file to be numpyifyted.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()
    updated_code = _numpyify_doctrings_from_code(code)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_code)


if __name__ == "__main__":
    path = r"temp.py"
    numpyify_docstrings_from_file(path)
    print(f"Docstrings numpyifyted of {path}")
