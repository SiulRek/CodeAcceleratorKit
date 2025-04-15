"""
TODO:
    1. Run this file to copy macros text to clipboard
    2. Run the task
    3. Paste the text from clipboard to the 'Macros Field'
    4. Press Submit
    5. Compare the output with automatic_prompt_test_prompt.txt
"""
import os

import clipboard

MACROS_FILE = os.path.join("tasks", "tests", "data", "automatic_prompt_macros.txt")
with open(MACROS_FILE, "r") as file:
    text = file.read()

clipboard.copy(text)
