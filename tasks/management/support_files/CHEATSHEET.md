# CHEATSHEET

This kit contains a set of tasks designed to automate various operations on Python files. This Tasks are available:

1. [Format Python Task](#1-format-python-task)
1. [Automatic Prompt Task](#2-automatic-prompt-task)
1. [Restore File Task](#4-restore-file-task)
1. [Pylint Report Task](#3-pylint-report-task)
1. [Directory Runner Task](#5-directory-runner-task)
1. [Undo Directory Runner Task](#6-uno-directory-runner-task)
1. [Git Staging Task](#7-git-staging-task)
1. [Git Discard Task](#8-git-discard-task)



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
| RI            | Rearrange imports         |                    |
| RU            | Remove unused imports     |                    |
| BF            | Run Black formatting      |                    |
| FE            | Format exceptions         |                    |
| FD            | Format docstrings         |                    |
| FC            | Format comments           |                    |
| EN            | Ensure new line at EOF    | Needs to be forced |
| PL            | Execute Pylint            |                    |

**Usage from command line**:
```sh
python path/to/format_python_task.py <root_directory> [<macro_file_path> | --help | -h | --cancel | -c]
```

### 2. Automatic Prompt Task

**Description:**            
The `AutomaticPromptTask` is designed to create dynamic prompts based on macro statements provided either through the macro field or as a string argument. These prompts can serve various purposes, such as generating queries, automating tasks, or facilitating further processing. The generated prompts can be saved to a file, optionally copied to the clipboard (as configured in [configs.json](./profile/configs.json)), or sent directly to ChatGPT via macro.

Optional arguments should be provided as Python literals enclosed in parentheses, separated by commas (e.g., `(True, "string", 1, [1, 2, 3])`). If no arguments are specified, the task will use default values. Default values are either explicitly defined or empty for data types such as lists, tuples, or dictionaries.

**Available Reference Types**:
| Name                     | Description                                                                                       | Pattern                                                 | Optional Arguments                                                                                  |
|--------------------------|---------------------------------------------------------------------------------------------------|----------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| `begin_text`             | Place start text                                                                                  | `#B <begin_text>`                                        | –                                                                                                     |
| `end_text`               | Place end text                                                                                    | `#E <end_text>`                                          | –                                                                                                     |
| `title`                  | Title of the reference                                                                            | `#T <title>`                                             | `<level: int = 1>`                                                                                    |
| `normal_text`            | Normal text                                                                                       | `#N <normal_text>`                                       | –                                                                                                     |
| `paste_file`             | Paste file(s)                                                                                     | `#P <file_path>` or `<file_path_1, file_path_2>`         | `<line_ranges: List[List[int, int]]>`                                                                 |
| `paste_declaration_block`| Paste class or function                                                                           | `#PDB <file_path> <declaration_name>`                    | `<only_declaration_and_docstring: bool = False>`                                                      |
| `fill_text`              | Add a fill text ([see more](./costumizations/fill_texts/fill_text_template/template_4.txt))       | `#*<file_name_without_ext>`                              | –                                                                                                     |
| `meta_macros`            | Interpret predefined meta macros ([see more](./costumizations/meta_macros/template_1.py))         | `#<file_name_without_ext>_meta`                          | –                                                                                                     |
| `meta_macros_with_args`  | Meta macros with arguments ([see more](./costumizations/meta_macros_with_args/template_2.py))     | `#<file_name_without_ext>_meta+`                         | `<arg_1, arg_2, ...>`                                                                                 |
| `costum_function`        | Paste the output of custom function ([see more](./costumizations/functions/costum_function_template/template_3.py)) | `#<file_name_without_ext>_func+`       | `<arg_1, arg_2,>`                                                                                     |
| `run_pyscript`           | Run a Python script                                                                               | `#run <script_path>`                                     | –                                                                                                     |
| `run_bash_script`        | Run a bash script                                                                                 | `#runsh <script_path>`                                    | –                                                                                                     |
| `run_subprocess`         | Run subprocess command                                                                            | `#$ <command>`                                           | `<python_subprocess_kwargs: Dict>`                                                                    |
| `run_pylint`             | Run pylint on a Python script                                                                     | `#pylint <file_path>`                                    | –                                                                                                     |
| `run_unittest`           | Run unittests on a Python script                                                                  | `#unittest <file_path>`                                  | `<verbosity: int = 1>`                                                                                |
| `directory_tree`         | Get directory tree layout                                                                         | `#tree <directory_path>`                                 | `<max_depth: int = float("inf"), include_files: bool = False, ignore_list: List[str]>`                |
| `summarize_python_script`| Summarize a Python script                                                                         | `#summarize <script_path>`                               | `<include_definitions_without_docstrings: bool = False>`                                              |
| `summarize_folder`       | Summarize all Python scripts in a folder                                                          | `#summarize_folder <folder_path>`                        | `<include_definitions_without_docstrings: bool = False, excluded_dirs: List[str], excluded_files: List[str]>` |
| `send_prompt`            | Send a prompt from a temporary file                                                             | `#send`                                                | `<modify_inplace: bool = False, max_tokens: int = None>`                                              |

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
```

### 8. Git Discard Task

**Description:**  
The `GitDiscardTask` is designed to discard specified files or directories from a Git repository after backing them up. It ensures that the specified files or files in directories are not ignored and are modified before proceeding with the discard operation. The task makes use of Git commands to restore the files from the repository and utilizes a backup handler to save the original state of the files.

**Usage from command line**:  
```sh
python path/to/git_discard_task.py <root_directory> <reference_file> <paths_to_discard>
```
