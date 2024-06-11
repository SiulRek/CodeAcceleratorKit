from tasks.configs.constants import EDIT_TEXT_FLAGS as FLAGS


def edit_text(text, replace_mapping):
    """
    Edits the text based on the following edit strategies:
        1. Cutting the text up and down based on the flags. 
        2. Replacing the text based on the replace_dict.

    Args:
        - text (str): The text to be edited.
        - replace_mapping (dict): A dictionary of strings to replace. The key
            is the string to be replaced and the value is the string to replace.

    Returns:
        - str: The edited text.
    """

    # Edit strategy 1
    text_chunk = ""
    chunks_list = [
        # (text_chunk, cut_flag)
    ]
    text_len = len(text.splitlines())
    for line_number, line in enumerate(text.splitlines()):
        stripped_line = line.strip()
        if stripped_line == FLAGS.CUT_UP.value:
            chunks_list.append((text_chunk, FLAGS.CUT_UP))
            text_chunk = ""
        elif stripped_line == FLAGS.CUT_DOWN.value:
            chunks_list.append((text_chunk, FLAGS.CUT_DOWN))
            text_chunk = ""
        elif text_len == line_number + 1:
            text_chunk += line + "\n"
            chunks_list.append((text_chunk, FLAGS.END_OF_TEXT))
        else:
            text_chunk += line + "\n"

    updated_text = ""
    previous_cut_flag = None
    for text_chunk, cut_flag in chunks_list:
        if previous_cut_flag == FLAGS.CUT_DOWN:
            previous_cut_flag = cut_flag
            continue
        if cut_flag in [FLAGS.END_OF_TEXT, FLAGS.CUT_DOWN]:
            updated_text += text_chunk
        previous_cut_flag = cut_flag

    # Edit strategy 2
    for key, value in replace_mapping.items():
        updated_text = updated_text.replace(key, value)

    return updated_text


if __name__ == "__main__":
    text = """
    Here is some text that we want to edit.
    #cut_up
    This is the first chunk of text.
    #cut_down
    This is the second chunk of text.
    #cut_up
    This is the third chunk of text.
    #cut_down
    This is the end of the text.
    """
    replace_dict = {"first": "1st", "second": "2nd", "third": "3rd"}
    updated_text = edit_text(text, replace_dict)
    print(updated_text)
    # Expected output:
    # This is the 1st chunk of text.
    # This is the 2nd chunk of text.
    # This is the 3rd chunk of text.
