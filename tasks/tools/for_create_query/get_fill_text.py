import os

from tasks.configs.getters import get_fill_text_directory


def get_fill_text(placeholder, fill_text_dir):
    """
    Get fill text from a file with a placeholder.

    Args:
        - placeholder (str): The placeholder to search for.
        - fill_text_dir (str): The directory containing the fill text files.

    Returns:
        - tuple: A tuple containing the fill text and the title of the fill
            text.
    """
    if not os.path.exists(fill_text_dir):
        msg = f"Fill text directory {fill_text_dir} does not exist."
        raise NotADirectoryError(msg)
    
    for root, _, files in os.walk(fill_text_dir):
        files = [os.path.splitext(file) for file in files]
        for file in files:
            if file[0] == placeholder:
                title_parts = os.path.basename(root).split("_")
                title = " ".join([word.capitalize() for word in title_parts])
                file_path = os.path.join(root, f"{file[0]}{file[1]}")
                with open(file_path, "r", encoding="utf-8") as fill_text_file:
                    fill_text = fill_text_file.read()
                return fill_text, title
    msg = f"Fill text with placeholder {placeholder} not found."
    raise FileNotFoundError(msg)
