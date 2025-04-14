# Automatic Prompt Task

**Description:**            
The `AutomaticPromptTask` generates an automatic prompt based on macro statements retrieved from the macro field or a string passed as an argument. The prompt is typically a query that is saved in a file, optionally copied to the clipboard, and optionally sent to ChatGPT.

Optional arguments should be provided as Python literals enclosed in round brackets, separated by commas (e.g., `(True, "string", 1, [1, 2, 3])`).

**Available Reference Types**:
| Name                    | Description                                                                                  | Pattern                                                  | Optional Arguments                                             |
|-------------------------|----------------------------------------------------------------------------------------------|-----------------------------------------------------------|----------------------------------------------------------------|
| `begin_text`            | Place start text                                                                             | `#B <begin_text>`                                         | –                                                              |
| `end_text`              | Place end text                                                                               | `#E <end_text>`                                           | –                                                              |
| `title`                 | Title of the reference                                                                       | `#T <title>`                                              | `<level>`                                                      |
| `normal_text`           | Normal text                                                                                  | `#N <normal_text>`                                        | –                                                              |
| `paste_file`            | Paste file(s)                                                                                | `#P <file_path>` or `<file_path_1, file_path_2>`         | –                                                              |
| `fill_text`             | Add a fill text ([see more](./costumizations/fill_texts/fill_text_template/template_4.txt)) | `#*<file_name_without_ext>`                              | –                                                              |
| `meta_macros`           | Interpret predefined meta macros ([see more](./costumizations/meta_macros/template_1.py))   | `#<file_name_without_ext>_meta`                          | –                                                              |
| `meta_macros_with_args` | Meta macros with arguments ([see more](./costumizations/meta_macros_with_args/template_2.py)) | `#<file_name_without_ext>_meta+`                         | `<arg_1, arg_2, ...>`                                          |
| `costum_function`       | Paste the output of custom function ([see more](./costumizations/functions/costum_function_template/template_3.py)) | `#<file_name_without_ext>_func+`                         | `<arg_1, arg_2, ...>`                                          |
| `run_python_script`     | Run a Python script                                                                          | `#run <script_path>`                                     | –                                                              |
| `run_subprocess`        | Run subprocess command                                                                       | `#$ <command>`                                            | `<python_subprocess_kwargs>`                                   |
| `run_pylint`            | Run pylint on a file                                                                         | `#pylint <file_path>`                                     | –                                                              |
| `run_unittest`          | Run unittests on a file                                                                      | `#unittest <file_path>`                                   | `<verbosity>`                                                  |
| `directory_tree`        | Get directory tree layout                                                                    | `#tree <directory_path>`                                  | `<max_depth, include_files, ignore_list>`                      |
| `summarize_python_script` | Summarize a Python script                                                                  | `#summarize <script_path>`                                | `<include_definitions_without_docstrings>`                        |
| `summarize_folder`      | Summarize all Python scripts in a folder                                                     | `#summarize_folder <folder_path>`                         | `<include_definitions_without_docstrings, excluded_dirs, excluded_files>` |
