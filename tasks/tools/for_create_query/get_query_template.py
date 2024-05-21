import os


def get_query_template(name, query_template_dir):
    """
    Get a query template by name.

    Args:
        - name (str): The name of the query template.
        - query_template_dir (str): The directory containing the query templates.

    Returns:
        - str: The query template.
    """
    for file in os.listdir(query_template_dir):
        base, _ = os.path.splitext(file)
        if base == name:
            file_path = os.path.join(query_template_dir, file)
            with open(file_path, "r", encoding="utf-8") as query_template_file:
                query_template = query_template_file.read()
            return query_template
    msg = f"Query template with name {name} not found."
    raise FileNotFoundError(msg)
