Start of Prompt
Merge begin text in multiple lines
**********

# Test: Title of the chapter
----------

## Test: Normal Text
----------

The Normal text
Merge normal texts in multiple lines

## Test: Paste File
----------

```python
# This is the reference 1 file.
# Here is the reference 1 file finished.
# In Post-editing: REPLACE_ME == I_HAVE_BEEN_REPLACED
```

```python
# This is the reference 2 file.
#cut_up
# This line the only line that appears in post-editing
#cut_down
# Here is the reference 2 file finished.
```

## Test: Paste Current File
----------

```python
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

```

## Test: Paste Folder Files
----------

### test_results.log

2024-05-11 18:10:41,841 - INFO - -------------- This is a Title -------------------------------
2024-05-11 18:10:41,841 - ERROR - Test raised exc: test_example_error
Message: Traceback (most recent call last):
  File "/home/no_name/github/pcb-defect-detection/source/utils/testing/test_result_logger.py", line 146, in test_example_error
    raise ValueError()
ValueError

2024-05-11 18:10:41,841 - ERROR - Test failure: test_example_fail
Message: Traceback (most recent call last):
  File "/home/no_name/github/pcb-defect-detection/source/utils/testing/test_result_logger.py", line 143, in test_example_fail
    self.assertEqual(1, 2)
AssertionError: 1 != 2

2024-05-11 18:10:41,841 - INFO - Test passed: test_example_pass


### reference_3.txt

```text
Here is the reference 3 file.
Here is the reference 3 file finished.
```

## Test: Paste File's Lines, TODO list for test
----------

```python
"""
TODO:
    1. Run this file to copy macros text to clipboard
    2. Run the task
    3. Paste the text from clipboard to the 'Macros Field'
    4. Press Submit
    5. Compare the output with automatic_prompt_test_prompt.txt
```

## Test: Paste Declaration Block
----------

```python
class FileManager:
    """
    Class to handle file management operations.
    """


    def delete_file(self, filename):
        """
        Delete a file with the given name from the directory.
        """
        import os
        os.remove(f"{self.directory}/{filename}")
        print("File deleted successfully.")
```

## Test: Paste Clipboard Entry
----------

#B Start of Prompt
#B Merge begin text in multiple lines

#E End of prompt
#E Merge end text in multiple lines

#T Test: Title of the chapter

#T Test: Normal Text (2)
#N The Normal text
#N Merge normal texts in multiple lines

#T Test: Paste File (2)
#P reference_1.py, data\reference_2.py

#T Test: Paste Current File (2)
#P File

#T Test: Paste Folder Files (2)
#PF tasks/tests/data (3, ["tasks/tests/data/__pycache__"] , ["example_script.py", "example_script_2.py", "example_script_3.py", "example_script_4.py", "example_script_5.py", "example_script_6.py", "reference_1.py", "reference_2.py", "automatic_prompt_macros.txt"])

#T Test: Paste File's Lines, TODO list for test (2)
#P File ([[1, 8]])

#T Test: Paste Declaration Block (2)
#PDB example_script_2.py FileManager (True)
#PDB example_script_2.py delete_file

#T Test: Paste Clipboard Entry (2)
#PC 
#PC ("shell")

#T Test: Fill Text (2)
#*template_4

#T Test: Meta Macros (2)
#template_1_meta

#T Test: Meta Macros with Args (2)
#template_2_meta+ (True, 5)

#T Test: Custom Function (2)
#template_3_func (True, 5)

#T Test: Run Python Script (2)
#run data/example_script.py

#T Test: Run Pylint (2)
#pylint data/example_script.py

#T Test: Run Unittest (2)
#unittest example_script_6.py (2)

#T Test: Directory Tree (2)
#tree . (2, False, ['temp', 'log'])

#T Test: Summarize Python Script (2)
#summarize data/example_script_2.py (True)

#T Test: Summarize Folder (2)
#summarize_folder data (True, 3, [], ['reference_1.py', 'reference_2.py', 'example_script_6.py'])


```shell
#B Start of Prompt
#B Merge begin text in multiple lines

#E End of prompt
#E Merge end text in multiple lines

#T Test: Title of the chapter

#T Test: Normal Text (2)
#N The Normal text
#N Merge normal texts in multiple lines

#T Test: Paste File (2)
#P reference_1.py, data\reference_2.py

#T Test: Paste Current File (2)
#P File

#T Test: Paste Folder Files (2)
#PF tasks/tests/data (3, ["tasks/tests/data/__pycache__"] , ["example_script.py", "example_script_2.py", "example_script_3.py", "example_script_4.py", "example_script_5.py", "example_script_6.py", "reference_1.py", "reference_2.py", "automatic_prompt_macros.txt"])

#T Test: Paste File's Lines, TODO list for test (2)
#P File ([[1, 8]])

#T Test: Paste Declaration Block (2)
#PDB example_script_2.py FileManager (True)
#PDB example_script_2.py delete_file

#T Test: Paste Clipboard Entry (2)
#PC 
#PC ("shell")

#T Test: Fill Text (2)
#*template_4

#T Test: Meta Macros (2)
#template_1_meta

#T Test: Meta Macros with Args (2)
#template_2_meta+ (True, 5)

#T Test: Custom Function (2)
#template_3_func (True, 5)

#T Test: Run Python Script (2)
#run data/example_script.py

#T Test: Run Pylint (2)
#pylint data/example_script.py

#T Test: Run Unittest (2)
#unittest example_script_6.py (2)

#T Test: Directory Tree (2)
#tree . (2, False, ['temp', 'log'])

#T Test: Summarize Python Script (2)
#summarize data/example_script_2.py (True)

#T Test: Summarize Folder (2)
#summarize_folder data (True, 3, [], ['reference_1.py', 'reference_2.py', 'example_script_6.py'])

```

## Test: Fill Text
----------

Write some text here.
Generally, you can call the fill text:
#*<file_name_without_ext>
For instance this module is called with:
#*template_4
Note the file must be in a subdir of fill_text_dir, the subdir name is going to 
be the macro title of the text here.

## Test: Meta Macros
----------

### How to make Meta Macros
----------

List every macro you want here
Generally you can call this meta macro with:
#<name_of_file_without_ext>_macros
Specifically call this template with:
#template_1_macros
And all the macros you defined here are going to be processed
Lets try it out, I hope you have an example_script.py somewhere

```shell
Prime numbers up to 100: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

```

```shell
************* Module example_script
tasks/tests/data/example_script.py:12:0: C0304: Final newline missing (missing-final-newline)
tasks/tests/data/example_script.py:1:0: C0114: Missing module docstring (missing-module-docstring)
tasks/tests/data/example_script.py:4:4: C0103: Constant name "isPrime" doesn't conform to UPPER_CASE naming style (invalid-name)
tasks/tests/data/example_script.py:7:12: C0103: Constant name "isPrime" doesn't conform to UPPER_CASE naming style (invalid-name)

------------------------------------------------------------------
Your code has been rated at 6.00/10 (previous run: 6.00/10, +0.00)


```

Now call me

## Test: Meta Macros with Args
----------

### This is the Start of the macros_with_args template
----------

text

### Chapter dedicated to argument_1
----------

`argument_1` was set to True

### Chapter dedicated to argument_2
----------

`argument_2` was set to 5
Iterations Start:
Iteration 1
Iteration 2
Iteration 3
Iteration 4
Iteration 5

## Test: Custom Function
----------

This is the Start of the costum_function output text
text
This is argument_1: True
This is argument_2: 5
The End of the costum_function output text



## Test: Run Python Script
----------

```shell
Prime numbers up to 100: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

```

## Test: Run Pylint
----------

```shell
************* Module example_script
tasks/tests/data/example_script.py:12:0: C0304: Final newline missing (missing-final-newline)
tasks/tests/data/example_script.py:1:0: C0114: Missing module docstring (missing-module-docstring)
tasks/tests/data/example_script.py:4:4: C0103: Constant name "isPrime" doesn't conform to UPPER_CASE naming style (invalid-name)
tasks/tests/data/example_script.py:7:12: C0103: Constant name "isPrime" doesn't conform to UPPER_CASE naming style (invalid-name)

------------------------------------------------------------------
Your code has been rated at 6.00/10 (previous run: 6.00/10, +0.00)


```

## Test: Run Unittest
----------

```shell
test_invalid_script_name_no_py (example_script_6.TestScriptNamePattern) ... ok
test_valid_script_name (example_script_6.TestScriptNamePattern) ... ok
test_valid_script_name_with_path (example_script_6.TestScriptNamePattern) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK


```

## Test: Directory Tree
----------

```shell
CodeAcceleratorKit/
├── __pycache__/
├── _local/
│   ├── management/
│   ├── private/
│   ├── tasks_storage/
│   └── waste/
├── local/
│   ├── private/
│   └── tasks_storage/
├── my_utils/
│   ├── create_repo_cheatsheet/
│   └── vscode_shortcuts/
├── tasks/
│   ├── __taskscache__/
│   ├── configs/
│   ├── controllers/
│   ├── deprecated/
│   ├── management/
│   ├── tasks/
│   ├── tests/
│   └── utils/
└── venv/
    ├── bin/
    ├── include/
    ├── lib/
    ├── lib64/
```

## Test: Summarize Python Script
----------

class FileManager:
    """
    Class to handle file management operations.
    """
    def __init__(self, directory):

    def create_file(self, filename, content):
        """
        Create a file with the given name and content in the directory.
        """
    def delete_file(self, filename):
        """
        Delete a file with the given name from the directory.
        """
class Calculator:
    """
    Simple calculator class to perform basic arithmetic operations.
    """
    def __init__(self):

    def add(a, b):
        """
        Return the sum of two numbers.
        """
    def subtract(a, b):
        """
        Return the difference of two numbers.
        """
def main():
    """
    Main function to execute some operations.
    """

## Test: Summarize Folder
----------

### example_script_6.py

```python
class TestScriptNamePattern:

    def test_valid_script_name(self):

    def test_invalid_script_name_no_py(self):

    def test_valid_script_name_with_path(self):

```

### example_script_4.py

```python
def check_age_raising_exception(age):

def check_age_sending_warnings(age):

```

### example_script_5.py

```python
def parse_url(url):

def calculate_square_root(number):

def generate_random_number():

```

### example_script_3.py

```python
def function():

```

### example_script_2.py

```python
class FileManager:
    """
    Class to handle file management operations.
    """
    def __init__(self, directory):

    def create_file(self, filename, content):
        """
        Create a file with the given name and content in the directory.
        """
    def delete_file(self, filename):
        """
        Delete a file with the given name from the directory.
        """
class Calculator:
    """
    Simple calculator class to perform basic arithmetic operations.
    """
    def __init__(self):

    def add(a, b):
        """
        Return the sum of two numbers.
        """
    def subtract(a, b):
        """
        Return the difference of two numbers.
        """
def main():
    """
    Main function to execute some operations.
    """
```

**********
End of prompt
Merge end text in multiple lines
