from textwrap import wrap as wrap_text

LINE_WIDTH = 80
INTEND = "    "


def count_leading_spaces(line):
    return len(line) - len(line.lstrip())


def extract_comments(code):
    """
    Extracts comments from the code and returns them as a list.

    Args:
        - code (str): The code from which the comments are to be extracted.

    Returns:
        - list: A list of comments extracted from the code.
    """
    code_lines = code.split("\n")
    lines_iter = iter(code_lines)
    comments = []

    while True:
        try:
            line = next(lines_iter)
            stripped_line = line.strip()
            if stripped_line.startswith("#"):
                comment = line + "\n"
                while stripped_line.startswith("#"):
                    line = next(lines_iter)
                    stripped_line = line.strip()
                    if stripped_line.startswith("#"):
                        comment += line + "\n"
                    else:
                        break
                comments.append(comment.rstrip())
        except StopIteration:
            break

    return comments


def wrap_comment(comment, leading_spaces):
    """
    Wraps the comment to the specified width.

    Args:
        - comment (str): The comment to be wrapped.
        - leading_spaces (str): The leading spaces to be added to the
            wrapped comment.

    Returns:
        - str: The wrapped comment.
    """
    comment_lines = comment.splitlines()
    concatenated_comment = " ".join(line.strip("# ").strip() for line in comment_lines)
    wrapped_lines = wrap_text(
        concatenated_comment, width=LINE_WIDTH - len(leading_spaces) - 2
    )
    wrapped_comment = "\n".join(f"{leading_spaces}# {line}" for line in wrapped_lines)
    return wrapped_comment

def enumaration_symbol_detected(text):
    for line in text.splitlines():
        line = line.strip().removeprefix("#").strip()
        numbered = line.split(".")[0].isdigit()
        dashed = line.startswith("- ") or line.startswith("* ")
        if numbered or dashed:
            return True
    return False

def refactor_comments(comments):
    """
    Refactors the comments by wrapping them to the specified width.

    Args:
        - comments (list): A list of comments to be refactored.

    Returns:
        - list: A list of refactored comments.
    """
    refactored_comments = []
    for comment in comments:
        first_line = comment.splitlines()[0]
        leading_spaces = " " * count_leading_spaces(first_line)
        if not enumaration_symbol_detected(comment):
            comment = wrap_comment(comment, leading_spaces)
        refactored_comments.append(comment)
    return refactored_comments


def format_comments(code):
    """
    Formats the comments in the code.

    Args:
        - code (str): The code to be formatted.

    Returns:
        - str: The code with the formatted comments.
    """
    comments = extract_comments(code)
    refactored_comments = refactor_comments(comments)
    for original, updated in zip(comments, refactored_comments):
        code = code.replace(original, updated)
    return code


def format_comments_from_file(file_path):
    """
    Formats the comments in the file.

    Args:
        - file_path (str): The path to the file to be formatted.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()
    updated_code = format_comments(code)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_code)


if __name__ == "__main__":
    path = r"tasks/tests/for_tasks/format_python_test.py"
    format_comments_from_file(path)
    print(f"Comments formatted in {path}")
