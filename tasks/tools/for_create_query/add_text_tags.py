def add_text_tags(begin_text, end_text, text):
    """
    Adds the specified begin and end text tags to the given text.

    Args:
        - begin_text (str): The begin text tag.
        - end_text (str): The end text tag.
        - text (str): The text to which the tags should be added.

    Returns:
        - str: The text with the start and end text tags.
    """
    stop_sep = "\n\n" + "*" * 10 + "\n\n"
    start_sep = "\n\n" + "*" * 10 + "\n\n"
    begin_text = f"{begin_text}{start_sep}" if begin_text else ""
    end_text = f"{end_text}{stop_sep}" if end_text else ""
    text = f"{begin_text}{text}{end_text}"
    return text
