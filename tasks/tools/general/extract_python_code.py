import re


def extract_python_code(text):
    """
    Extracts Python code from a given text. Specifically, it extracts code from code blocks that are formatted as ```python ... ```.
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
        if match.strip().startswith(("python", "import", "from", "def", "class", "if", "for", "while",'"""', "'''"))
    ]
    
    for i, block in enumerate(python_code_blocks):
        if block.startswith("python"):
            python_code_blocks[i] = block[6:]
    python_code = "\n\n".join(python_code_blocks)
    python_code = python_code.replace("```", "").strip()
    if python_code.startswith("-"):
        python_code = python_code[python_code.find("\n") + 1:]
    python_code = python_code.replace("`", "")
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