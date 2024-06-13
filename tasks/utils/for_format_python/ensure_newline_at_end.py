import re

def ensure_newline_at_end(text):
    """
    Ensures that there is a newline at the end of the given text. Adds a newline if there isn't one.

    Args:
        - text (str): The text content.

    Returns:
        - str: The updated text with a newline at the end.
    """
    if not text.endswith("\n"):
        text += "\n"
    return text


def ensure_newline_at_end_from_file(file_path):
    """
    Ensures that there is a newline at the end of the given file content. Adds a newline if there isn't one.

    Args:
        - file_path (str): The path to the file.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    updated_text = ensure_newline_at_end(text)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_text)


if __name__ == "__main__":
    ensure_newline_at_end_from_file(r"/path/to/your/file")
