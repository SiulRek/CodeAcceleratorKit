import re


def extract_python_code_strategy_1(text):
    """
    Extracts Python code from a given text. It extracts code from code blocks that are formatted as ```python ... ```.
    The code is expected to start with: python, import, from, def, class, if, for, while, 3 times double quotes or '''.

    Args:
        text (str): The text to extract Python code from.

    Returns:
        str: The extracted Python code.
    """
    pattern = r"```(.*?)```"

    matches = re.findall(pattern, text, re.DOTALL)

    python_code_blocks = [
        match
        for match in matches
        if match.strip().startswith(
            (
                "python",
                "import",
                "from",
                "def",
                "class",
                "if",
                "for",
                "while",
                '"""',
                "'''",
            )
        )
    ]

    for i, block in enumerate(python_code_blocks):
        if block.startswith("python"):
            python_code_blocks[i] = block[6:]
    python_code = "\n\n".join(python_code_blocks)
    python_code = python_code.replace("```", "").strip()
    if python_code.startswith("-"):
        python_code = python_code[python_code.find("\n") + 1 :]
    python_code = python_code.replace("`", "")
    return python_code


def extract_python_code_strategy_2(text):
    """
    Extracts Python code from a given text. It extracts code following a line starting with "---".

    Args:
        text (str): The text to extract Python code from.
    """
    lines = text.split("\n")
    python_code = ""
    in_code_block = False
    for line in lines:
        if in_code_block:
            if line.startswith("---") or line.startswith("***"):
                in_code_block = False
            else:
                python_code += line + "\n"
        elif line.startswith("---"):
            in_code_block = True
    return python_code.strip()


def extract_python_code(text):
    """
    Extracts Python code from a given text. Specifically designed for ChatGPT's response format.

    Args:
        text (str): The text to extract Python code from.
    """
    python_code = extract_python_code_strategy_1(text)
    if not python_code:
        python_code = extract_python_code_strategy_2(text)
    return python_code


if __name__ == "__main__":
    text = """
Here's an example of a Python function:

```python
def hello_world():
    print("Hello, world!")
#This function prints a greeting.```
Blablabla cool talking
```python
def bye_world():
    print("Bye, world!")
#This function prints a greeting.```
"""

    print(extract_python_code(text))
