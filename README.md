# CodeAcceleratorKit

The CodeAcceleratorKit is designed to support and speed up Python code development. It includes two main sections:
- **[my_utils](./my_utils/)**: This folder contains helper tools I've created for my own use. They might not be interesting you, but you're welcome to explore them.
- **[tasks](./tasks/)**: This section features scripts that automate tasks related to Python file management, such as formatting, prompt generation, and file restoration.

This README will give you a brief overview about the tasks of CodeAcceleratorKit and how to set them up in a new workspace.

## Table of Contents
1. [Setup](#setup)
2. [Conventions](#conventions)
3. [Tasks Overview](#tasks-overview)
4. [Special Chapter for VSCode Users](#special-chapter-for-vscode-users)

## Setup

To set up the tasks in a new local workspace, it is recommended to install the following three libraries in your runner workspace environment to utilize the full capabilities of the Tasks. You can find the requirements file for runner [here](./tasks/management/support_files/requirements_runner.txt). 

Next, you will need to register the runner using our provided script `register_runner.py`. This script will create the necessary directories and initialize their attributes. You can find the script [here](./tasks/controllers/scripts/register_runner.py). 

After registering the runner, you can start using the tasks by running the corresponding task scripts with the required arguments. Please note that the Kit carefully organizes both the Python environments of the CodeAcceleratorKit and the workspace runner environments to avoid conflicts.

Additionally, if you want to send prompts to OpenAI's API, you will need to set up an API key and import it in [send_prompt.py](./tasks/tools/for_automatic_prompt/send_prompt.py).


## Conventions

In CodeAcceleratorKit, various key definitions are used:

- **Macro**: A statement that configures our tasks. For example, `#only`, `#not`, `#force`, and `#checkpointing`.
- **Interpreter**: In this context, an interpreter refers to the system that interprets macro statements in our tasks.
- **Runner**: A registered environment where tasks are executed, usually an external workspace.
- **tasks_storage**: A storage directory that contains all runner data including profiles, backups, and status of running tasks. It is located in the root directory of the runner.
- **Profile**: Contains meta information about a runner.
- **Prefix TASKS_**: A convention in our codebase to denote constants related to tasks management.


## Tasks Overview

1. [Format Python Task](#1-format-python-task)
1. [Automatic Prompt Task](#2-automatic-prompt-task)
1. [Restore File Task](#4-restore-file-task)
1. [Pylint Report Task](#3-pylint-report-task)
1. [Directory Runner Task](#5-directory-runner-task)
1. [Undo Directory Runner Task](#6-uno-directory-runner-task)
1. [Git Staging Task](#7-git-staging-task)

Refer to the above links for detailed information about each Task.


### 1. Format Python Task

**Description:**            
The `FormatPythonTask` is designed to format Python files by removing or refactoring specific parts based on strategies configured by macros.

**Available Macros**:
| Name            | Description                                  | Macro          | Arguments                            |
|-----------------|----------------------------------------------|----------------|--------------------------------------|
| select_only     | Selects only the specified strategy          | #only          | `<List of strategies abbreviations>` |
| select_not      | Excludes the specified strategy              | #not           | `<List of strategies abbreviations>` |
| force_select_of | Forces selection of the specified strategy   | #force         | `<List of strategies abbreviations>` |
| checkpoints     | Marks the points in the code for checkpoints | #checkpointing | -                                    |

**Available Strategies**:
| Abbreviation  | Description               | Comments           |
|---------------|---------------------------|--------------------|
| RL            | Remove line comments      | Needs to be forced |
| RT            | Remove trailing parts     |                    |
| AE            | Add encoding to open      |                    |
| RUE           | Remove unused imports     |                    |
| RF            | Remove f from empty fstrings |                 |
| RE            | Refactor exceptions       |                    |
| RE            | Refactor warnings         |                    |
| RI            | Rearrange imports         |                    |
| RU            | Remove unused imports     |                    |
| BF            | Run Black formatting      |                    |
| FD            | Format docstrings         |                    |
| EN            | Ensure new line at EOF    | Needs to be forced |
| PL            | Execute Pylint            |                    |

**Usage from command line**:
```sh
python path/to/format_python_task.py <root_directory> <macro_file_path>
```


### 2. Automatic Prompt Task

**Description:**            
The `AutomaticPromptTask` generates an automatic prompt based on macro statements retrieved from either a file or a string passed as an argument. The prompt is typically a query, which is then finalized and saved in a file.

**Available Reference Types**:
| Name                    | Description                           | Pattern                                          | Optional Arguments                   |
|-------------------------|---------------------------------------|--------------------------------------------------|--------------------------------------|
| paste_files             | Paste file/s                          | # `<file_path>` or `<file_path_1, file_path_2>`  | <edit_content>                       |
| fill_text               | Add a fill text   | #*`<file_name_without_ext>`  | -                                    |
| meta_macros             | Interprete predefined meta macros  | #`<file_name_without_ext>`_meta | -                                    |
| meta_macros_with_args   | Meta macros with args  | #`<file_name_without_ext>`_meta+ | `<arg_1, arg_2, ...>`                |
| costum_function         | Paste the output of custom function   | #`<file_name_without_ext>`_func+                 | `<arg_1, arg_2, ...>`                |
| run_python_script       | Run a Python script                   | #run `<script_path>`                             | -                                    |
| run_pylint              | Run pylint on a file                  | #pylint `<file_path>`                            | -                                    |
| run_unittest            | Run unittest on a file                | #unittest `<file_path>`                          | `<verbosity>`                        |
| directory_tree          | Get directory tree                    | #tree `<directory_path>`                         | `<max_depth, include_files, ignore_list >` |
| summarize_python_script | Summarize a Python script             | #summarize `<script_path>`                       | `<include_definitions_with_docstrings>` |
| summarize_folder        | Summarize Python scripts in a folder  | #summarize_folder `<folder_path>`                | `<include_definitions_with_docstrings, excluded_dirs, excluded_files>` |
| checksum                | Check if provided checksum corresponds| #checksum `<number_of_references>`               | -                                    |


**Usage from command line**:  
```sh
python path/to/automatic_prompt_task.py <root_directory> <macro_file_path>
```
### 3. Pylint Report Task
**Description:**  
The `PylintReportTask` is designed to generate a Pylint report for python files in a directory or a single python file. It uses the Pylint library to analyze the file and generate a report in .txt format.

**Usage from command line**:  
```sh
% For a single file
python path/to/pylint_report_task.py <root_directory> <file_path>
% For a directory
python path/to/pylint_report_task.py <root_directory> None <directory_path>
``` 

**Note:**
The directory path is optional. If you provide a directory path, the task will generate a report for all python files in the directory. If not provided, the task will generate a report for the specified file.


### 4. Restore File Task

**Description:**            
The `RestoreFileTask` is designed to restore a backup file to its original location.

**Usage from command line**:  
```sh
python path/to/restore_file_task.py <root_directory> <backup_file_path>
```

### 5. Directory Runner Task

**Description:**            
The `DirectoryRunnerTask` runs specific tasks on a directory of files. It sets up the environment, reads configurations from a JSON file, and executes the specified task on each file within a directory. It supports resuming from the last stopped file and excludes specified files and directories.

**Available Tasks**:
- FormatPythonTask: Formats Python files by removing or refactoring specific parts based on macros.
- AutomaticPromptTask: Generates automatic prompts based on macro statements.

**Usage from command line**:
python path/to/directory_runner_task.py <root_directory> <config_file_path>

### 6. Undo Directory Runner Task

**Description:**            
The `UndoDirectoryRunnerTask` undoes the effects of a previously executed directory runner task. It sets up the environment, reads configurations from a JSON file, and uses the FileExecutionTracker and BackupHandler to revert changes made by the directory runner task.

**Usage from command line**:
```sh
python path/to/undo_directory_runner_task.py <root_directory> <config_file_path>
```	


## Special Chapter for VSCode Users

To utilize the CodeAcceleratorKit within VSCode, you need to create a `tasks.json` file in the `.vscode` folder of your project. Here you find a configuration example that sets up tasks: [windows](./tasks/management/support_files/windows/tasks.json) and [linux](./tasks/management/support_files/linux/tasks.json). Ensure the paths are correctly set according to your environment. After setting up the tasks, you can run them by pressing `Ctrt+Shift+P`, move to `Run Task`, and select the desired task.

**Note:**
Use the `${workspaceFolder}` and `${file}` placeholders to refer to your project folder and currently opened file, respectively. When you run a task, `workspaceFolder` will correspond to `root` and `file` to `current_file` in the related task class.

### 7. Git Staging Task

**Description:**  
The `GitStagingTask` is designed to manage the Git staging area by adding or removing specified files or directories. It uses `find_file_sloppy` and `find_dir_sloppy` to locate the files or directories, ensuring they exist before performing the specified action. Files or directories prefixed with a - are removed from the staging area, while others are added.

**Usage from command line**:  
```sh
python path/to/git_staging_task.py <root_directory> <reference_file> <paths_to_manage>
