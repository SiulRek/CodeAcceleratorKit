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


def render_to_markdown_code_block(text, language=None, extension=None):
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
    if language and extension:
        msg = "Only one of 'format' or 'extension' can be specified."
        raise ValueError(msg)

    if not language:
        extension = extension.split(".")[-1].lower()
        language = EXTENSION_TO_FORMAT.get(extension, None)
        if not language:
            msg = f"Could not determine the format for the extension '{extension}'."
            msg += "Text is not rendered."
            warnings.warn(msg)
            return text
    return f"```{language}\n{text}\n```"
