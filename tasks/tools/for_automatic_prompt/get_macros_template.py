import os


def get_macros_template(name, macros_template_dir):
    """
    Get a prompt template by name.

    Args:
        - name (str): The name of the prompt template.
        - macros_template_dir (str): The directory containing the prompt templates.

    Returns:
        - str: The prompt template.
    """
    for file in os.listdir(macros_template_dir):
        base, _ = os.path.splitext(file)
        if base == name:
            file_path = os.path.join(macros_template_dir, file)
            with open(file_path, "r", encoding="utf-8") as macros_template_file:
                macros_template = macros_template_file.read()
            return macros_template
    msg = f"Query template with name {name} not found."
    raise FileNotFoundError(msg)
