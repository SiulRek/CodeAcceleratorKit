import re

from tasks.configs.constants import LINE_WIDTH, INDENT_SPACES
from tasks.utils.for_format_python.wrap_text import wrap_text


def _extract_prefix_quote_and_msg(raw_msg):
    pattern = r"""(?i)                  # case-insensitive
                  (r|u|ru|ur)?          # optional prefix
                  (['"])                # capturing the quote
                  (.*?)(?<!\\)          # the message, non-greedy, ignoring escaped quotes
                  \2                    # match same quote type
               """
    matches = re.findall(pattern, raw_msg, re.DOTALL | re.VERBOSE)
    if not matches:
        msg = f"Invalid exception message format: {raw_msg}."
        raise ValueError(msg)

    msg_cmp = []
    for prefix, q, msg in matches:
        msg_cmp.append(
            {
                "prefix": prefix.lower() if prefix else "",
                "quote": q,
                "message": msg.strip(),
            }
        )
    all_quotes_equal = all(cmp["quote"] == msg_cmp[0]["quote"] for cmp in msg_cmp)
    if not all_quotes_equal:
        msg = f"Inconsistent quotes in the exception message:\n{raw_msg}."
        raise ValueError(msg)
    all_prefixes_equal = all(cmp["prefix"] == msg_cmp[0]["prefix"] for cmp in msg_cmp)
    if not all_prefixes_equal:
        msg = f"Inconsistent prefixes in the exception message:\n{raw_msg}."
        raise ValueError(msg)

    prefix = msg_cmp[0]["prefix"]
    quote = msg_cmp[0]["quote"]
    message = " ".join(cmp["message"] for cmp in msg_cmp)
    return prefix, quote, message


def _extract_exception_informations(code):
    code_lines = code.splitlines()
    code_lines_no_comments = [re.sub(r"#.*", "", line) for line in code_lines]

    merged_lines = []
    current = ""
    open_parens = 0
    buffer = []
    for i, line in enumerate(code_lines_no_comments):
        rstripped = line.rstrip()
        if not rstripped.lstrip():
            continue

        open_parens += rstripped.count("(") - rstripped.count(")")
        buffer.append(rstripped.lstrip() if buffer else rstripped)
        if open_parens == 0:
            start, stop = i - len(buffer) + 1, i
            current = " ".join(buffer)
            merged_lines.append(((current), [start, stop]))
            buffer.clear()
    exception_infos = []
    for line, line_range in merged_lines:
        exc_code = "\n".join(code_lines[line_range[0] : line_range[1] + 1])
        match = re.search(
            r"^([ \t]*)(raise\s+\w+(Exception|Error|Warning)|warnings.warn)\s*\((.*?)\)(\s+from\s+\w+)?",
            line,
            re.DOTALL,
        )
        if not match:
            continue
        indent = match.group(1)
        exception_type = match.group(2).removeprefix("raise").strip()
        raw_msg = match.group(4).strip()
        from_clause = match.group(5).strip() if match.group(5) else ""

        try:
            prefix, q, msg = _extract_prefix_quote_and_msg(raw_msg)
        except ValueError as e:
            continue

        exception_infos.append(
            {
                "code": exc_code,
                "indent": indent,
                "exception_type": exception_type,
                "prefix": prefix,
                "quote": q,
                "message": msg,
                "from_clause": from_clause,
            }
        )

    return exception_infos


def _ensure_space_and_quote(string_, quote):
    if not string_.endswith(" "):
        string_ = string_ + " "
    if "{" in string_ and "}" in string_:
        string_ = f"f{quote}{string_}{quote}"
    else:
        string_ = f"{quote}{string_}{quote}"
    return string_


def _construct_formatted_exception_code(exception_info):
    indent = exception_info["indent"]
    exception_type = exception_info["exception_type"]
    prefix = exception_info["prefix"]
    q = exception_info["quote"]
    msg = exception_info["message"]
    from_clause = exception_info["from_clause"]

    msg = wrap_text(msg, LINE_WIDTH - len(indent) - 10)

    formatted_msg = []
    for msg_line in msg.splitlines():
        buffer = indent + INDENT_SPACES + prefix + _ensure_space_and_quote(msg_line, q)
        formatted_msg.append(buffer)
    if formatted_msg[-1].endswith(" \""):
        formatted_msg[-1] = formatted_msg[-1][:-2] + "\""
    formatted_msg = "\n".join(formatted_msg)

    raise_holder = (
        "raise "
        if "warnings.warn" != exception_type
        else ""
    )
    formatted_exception = f"{indent}{raise_holder}{exception_type}(\n"
    formatted_exception += f"{formatted_msg}\n{indent})"
    formatted_exception += f" {from_clause}" if from_clause else ""
    return formatted_exception


def refactor_exceptions(code):
    """
    Refactors the exception code in the provided code.

    Args:
        - code (str): The code to be refactored.

    Returns:
        - str: The refactored code.
    """
    exception_infos = _extract_exception_informations(code)
    for exception_info in exception_infos:
        formatted_exception = _construct_formatted_exception_code(exception_info)
        code = code.replace(exception_info["code"], formatted_exception)
    return code


def refactor_exception_from_file(file_path):
    """
    Refactors the exception code in the file.

    Args:
        - file_path (str): The path to the file to be refactored.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()
    updated_code = refactor_exceptions(code)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_code)


if __name__ == "__main__":
    path = r"tasks/tests/data/example_script_4.py"
    refactor_exception_from_file(path)
    print(f"Refactored exception code in {path}")
