import re


def remove_trailing_lines(text):
    """
    Removes trailing lines from the given text.

    Parameters
    ----------
    text (str)
        The text content.

    Returns
    -------
    str
        The cleaned content of the text.
    """
    lines = text.splitlines()
    while lines and lines[-1].strip() == "":
        lines.pop()
    updated_contents = "\n".join(lines)
    return updated_contents


def remove_trailing_spaces(text):
    """
    Removes trailing spaces from the given text.

    Parameters
    ----------
    text (str)
        The text content.

    Returns
    -------
    str
        The cleaned text with trailing spaces removed from each line.
    """
    lines = text.splitlines()
    cleaned_lines = [re.sub(r"[ \t]+$", "", line) for line in lines]
    return "\n".join(cleaned_lines)


def remove_trailing_parts(text):
    """
    Removes trailing spaces and lines from the given text.

    Parameters
    ----------
    text (str)
        The text content.

    Returns
    -------
    str
        The cleaned content of the text.
    """
    text = remove_trailing_spaces(text)
    updated_text = remove_trailing_lines(text)
    # if text ends not with new line, add it
    if not updated_text.endswith("\n"):
        updated_text += "\n"
    return updated_text


def remove_trailing_parts_from_file(file_path):
    """
    Removes trailing spaces and lines from the given file.

    Parameters
    ----------
    file_path (str)
        The path to the file.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    updated_text = remove_trailing_parts(text)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_text)


if __name__ == "__main__":
    remove_trailing_parts_from_file(r"tasks/utils/for_format_python/remove_unnecessary_else.py")
