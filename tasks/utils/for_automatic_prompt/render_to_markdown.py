import warnings

EXTENSION_TO_FORMAT = {
    "py": "python",
    "json": "json",
    "yaml": "yaml",
    "yml": "yaml",
    "sh": "bash",
    "bash": "bash",
    "sql": "sql",
    "java": "java",
    "js": "javascript",
    "html": "html",
    "css": "css",
    "xml": "xml",
    "md": "markdown",
    "markdown": "markdown",
    "txt": "text",
}


def render_to_markdown(text, format=None, extension=None):
    """
    Renders the given text to a markdown code block with the specified format
    or extension of the file from which the text was extracted.

    Parameters
    ----------
    text (str)
        The text to be rendered.
    format (str, Optional)
        The format of the code block (e.g., 'python', 'json').
    extension (str, Optional)
        The extension of the file from which the text

    Returns
    -------
    str
        The markdown formatted code block.
    """
    if format and extension:
        msg = "Only one of 'format' or 'extension' can be specified."
        raise ValueError(msg)

    if not format:
        extension = extension.split(".")[-1].lower()
        format = EXTENSION_TO_FORMAT.get(extension, None)
        if not format:
            msg = f"Could not determine the format for the extension '{extension}'."
            msg += "Text is not rendered."
            warnings.warn(msg)
            return text
    return f"```{format}\n{text}\n```"
