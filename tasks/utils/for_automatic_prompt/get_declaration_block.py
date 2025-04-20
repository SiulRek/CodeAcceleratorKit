import re
import warnings

INDENT_SIZE = 4


def _get_indent_level(line):
    indent_len = len(line) - len(line.lstrip())
    try:
        return int(indent_len / INDENT_SIZE)
    except ValueError:
        raise ValueError(
            f"Invalid indentation level: {indent_len}. Expected a multiple "
            f"of {INDENT_SIZE}."
        )


DECLARATION_PATTERN = r"^\s*(def|class)\s+([a-zA-Z_][a-zA-Z0-9_]*)"


def _move_dictionary_item(key, source, target):
    value = source.pop(key)
    target[key] = value


def _collect_declaration_infos(script):
    with open(script, "r", encoding="utf-8") as file:
        text = file.read()

    declarations = {}
    pending_declarations = {}
    cur_indent = 0

    lines = text.splitlines(True)

    for i, line in enumerate(lines):
        if not line.strip():
            continue
        cur_indent = _get_indent_level(line)

        # Use a snapshot of items to avoid modifying dict during iteration
        for key, value in list(pending_declarations.items()):
            if value["indent"] >= cur_indent:
                value.update({"stop": i})
                _move_dictionary_item(key, pending_declarations, declarations)

        if match := re.match(DECLARATION_PATTERN, line):
            kind = match.group(1)  # def or class
            name = match.group(2)  # name of the callable

            declaration_info = {
                "kind": kind,
                "start": i,
                "indent": cur_indent,
                "stop": None,
            }

            duplicate_count = 2
            updated_name = name
            while (updated_name in pending_declarations) or (
                updated_name in declarations
            ):
                updated_name = f"{name}_{duplicate_count}"
                duplicate_count += 1
            if updated_name != name:
                warnings.warn(
                    f"Duplicate declaration detected for '{name}' at line "
                    f"{i + 1}. Renaming to '{updated_name}' to ensure "
                    "unique identifiers in declaration infos."
                )
                name = updated_name

            pending_declarations[name] = declaration_info

    for key, value in list(pending_declarations.items()):
        value.update({"stop": len(lines)})
        _move_dictionary_item(key, pending_declarations, declarations)

    declarations = dict(sorted(declarations.items(), key=lambda item: item[1]["start"]))
    return declarations


def _extract_declaration_and_docstring(declaration_block):
    lines = declaration_block.rstrip().splitlines()
    non_blank_index = next((i for i, line in enumerate(lines) if line.strip()), None)
    if not lines or non_blank_index is None:
        raise ValueError(
            "Declaration block is empty or contains only blank lines."
        )

    declaration = lines[non_blank_index]
    if re.match(DECLARATION_PATTERN, declaration) == None:
        raise ValueError(
            f"Invalid declaration line: {declaration}"
        )
    remaining = "\n".join(lines[non_blank_index + 1 :])

    docstring_pattern = r'^([ \t]*[\'"]{3}.*?[\'"]{3})'
    match = re.search(docstring_pattern, remaining, re.DOTALL | re.MULTILINE)

    if match:
        docstring_block = match.group(1)
        return f"{declaration}\n{docstring_block}"
    return declaration


def get_declaration_block(name, script, only_declaration_and_docstring=False):
    declaration_infos = _collect_declaration_infos(script)
    if name not in declaration_infos:
        raise ValueError(
            f"Callable {name} not found in {script}"
        )

    declaration_info = declaration_infos[name]
    with open(script, "r", encoding="utf-8") as file:
        lines = file.readlines()
        code_snippet = "".join(
            lines[declaration_info["start"] : declaration_info["stop"]]
        ).rstrip()

    if only_declaration_and_docstring:
        code_snippet = _extract_declaration_and_docstring(code_snippet)

    return code_snippet


if __name__ == "__main__":
    script = "/home/siulrek/MY_ROOM/github/CodeAcceleratorKit/tasks/tasks/automatic_prompt/chat_manager.py"
    collect_infos = False

    if collect_infos:
        # _collect_declaration_infos
        declaration_infos = _collect_declaration_infos(script)
        print("Declaration Infos:")
        for name, info in declaration_infos.items():
            print(f"{name}: {info}")
    else:
        # get_declaration_block
        name = "store_prompt_2"
        code_snippet = get_declaration_block(name, script, False)
        print(f"Code snippet for {name}:\n{code_snippet}")
