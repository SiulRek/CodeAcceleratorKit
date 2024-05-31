# CodeAcceleratorKit

The CodeAcceleratorKit is designed to support and speed up Python code development. It includes two main sections:
- **[my_utils](./my_utils/)**: This folder contains helper tools I've created for my own use. They might not be interesting you, but you're welcome to explore them.
- **[tasks](./tasks/)**: This section features scripts that automate tasks related to Python file management, such as formatting, prompt generation, and file restoration.

This README will give you a brief overview about the tasks of CodeAcceleratorKit and how to set them up in a new workspace.

## Table of Contents
1. [Setup](#setup)
2. [Conventions](#conventions)
3. [Tasks Overview](#tasks-overview)

## Setup

In order to setup the tasks on a new local workspace, you will need to register the runner using our provided script `register_runner.py`. This will create the appropriate directories and initialize its attributes. Link to the script can be found [here](./tasks/control/scripts/register_runner.py). After registering the runner, you can start using the tasks by running the corresponding task scripts with the required arguments. Note, the Kit organizes both python environments of CodeAcceleratorKit and the workspace runner environments carefully to avoid conflicts.

## Conventions

In CodeAccelerationKit, we use various definitions:

- **Macro**: A statement that we use to configure our tasks. For example, `#only`, `#not`, `#force`, and `#checkpointing`.
- **Interpreter**: In this context, interpreter refers to the system that interprets macro statements in our tasks.
- **Runner**: A registered environment where tasks are executed, usually an external workspace.
- **tasks_storage**: A storage directory that contains all runner data including profiles, backups, and status of running tasks. It is located in the root directory of the runner.
- **Profile**: Contains meta information about a runner.
- **Prefix TASKS_**: A convention in our codebase to denote constants related to tasks management.

## Tasks Overview

- [Format Python Task](#1-format-python-task)
- [Automatic Prompt Task](#2-automatic-prompt-task)
- [Restore File Task](#3-restore-file-task)
- [Directory Runner Task](#4-directory-runner-task)
- [Undo Directory Runner Task](#5-uno-directory-runner-task)

Refer to the above links for detailed information about each Task.


### 1. Format Python Task

**Description**:            
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
| RT            | Remove trailing parts     |                    |
| RL            | Remove line comments      | Needs to be forced |
| RE            | Refactor exception        |                    |
| RI            | Rearrange imports         |                    |
| RU            | Remove unused imports     |                    |
| BF            | Run Black formatting      |                    |
| FD            | Format docstrings         |                    |
| PL            | Execute Pylint            |                    |

**Usage from command line**:
```sh
python path/to/format_python_task.py <root_directory> <macro_file_path>
```


### 2. Automatic Prompt Task

**Description**:            
The `AutomaticPromptTask` generates an automatic prompt based on macro statements retrieved from either a file or a string passed as an argument. The prompt is typically a query, which is then finalized and saved in a file.

**Available Reference Types**:
| Name                    | Description                           | Pattern                                          | Arguments                            |
|-------------------------|---------------------------------------|--------------------------------------------------|--------------------------------------|
| begin_text              | Place start text                      | #B `<begin_text>`                                | -                                    |
| end_text                | Place end text                        | #E `<end_text>`                                  | -                                    |
| title                   | Title of the text                     | #T `<title>`                                     | -                                    |
| comment                 | Comment text                          | #C `<comment>`                                   | -                                    |
| paste_files             | Paste file/s                          | # `<file_path>` or `<file_path_1, file_path_2>`  | -                                    |
| paste_current_file      | Paste Current file                    | # File                                           | -                                    |
| error                   | Get logged errors                     | #L                                               | -                                    |
| fill_text               | Add a fill text  ([see more](./costumizations/fill_texts/fill_text_template/template_4.txt)) | #*`<file_name_without_ext>`  | -                                    |
| meta_macros             | Interprete predefined meta macros ([see more](./costumizations/meta_macros/template_1.py)) | #`<file_name_without_ext>`_meta | -                                    |
| meta_macros_with_args   | Meta macros with args  ([see more](./costumizations/meta_macros_with_args/template_2.py)) | #`<file_name_without_ext>`_meta+ | `<arg_1, arg_2, ...>`                |
| costum_function         | Paste the output of custom function  ([see more](./costumizations/functions/costum_function_template/template_3.py))   | #`<file_name_without_ext>`_func+                 | `<arg_1, arg_2, ...>`                |
| run_python_script       | Run a Python script                   | #run `<script_path>`                             | -                                    |
| run_pylint              | Run pylint on a file                  | #pylint `<file_path>`                            | -                                    |
| run_unittest            | Run unittest on a file                | #unittest `<file_path>`                          | `<verbosity>`                        |
| directory_tree          | Get directory tree                    | #tree `<directory_path>`                         | `<max_depth, include_files, ignore_list (semicolon-separated list)>` |
| summarize_python_script | Summarize a Python script             | #summarize `<script_path>`                       | `<include_definitions_with_docstrings>` |
| summarize_folder        | Summarize Python scripts in a folder  | #summarize_folder `<folder_path>`                | `<include_definitions_with_docstrings, excluded_dirs, excluded_files>` |
| send_prompt             | Send a prompt from a temporary file   | #send                                            | `<create_python_script, max_tokens>` |
| checksum                | Check if provided checksum corresponds| #checksum `<number_of_references>`               | -                                    |

**Usage from command line**:  
```sh
python path/to/automatic_prompt_task.py <root_directory> <macro_file_path>
```

### 3. Restore File Task

**Description**:            
The `RestoreFileTask` is designed to restore a backup file to its original location.

**Usage from command line**:
```sh
python path/to/restore_file_task.py <root_directory> <backup_file_path>
```

### 4. Directory Runner Task

**Description**:            
The `DirectoryRunnerTask` runs specific tasks on a directory of files. It sets up the environment, reads configurations from a JSON file, and executes the specified task on each file within a directory. It supports resuming from the last stopped file and excludes specified files and directories.

**Available Tasks**:
- FormatPythonTask: Formats Python files by removing or refactoring specific parts based on macros.
- AutomaticPromptTask: Generates automatic prompts based on macro statements.

**Usage from command line**:
python path/to/directory_runner_task.py <root_directory> <config_file_path>

### 5. Undo Directory Runner Task

**Description**:            
The `UndoDirectoryRunnerTask` undoes the effects of a previously executed directory runner task. It sets up the environment, reads configurations from a JSON file, and uses the FileExecutionTracker and BackupHandler to revert changes made by the directory runner task.

**Usage from command line**:
```sh
python path/to/undo_directory_runner_task.py <root_directory> <config_file_path>
```	