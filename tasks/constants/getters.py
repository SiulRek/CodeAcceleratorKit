import os
import json

from tasks.helpers.general.retrieve_modules import retrieve_modules

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_CODE_ROOT = os.path.join(FILE_DIR, "..", "..")


def get_task_cache_directory(name):
    dir = os.path.join(TASKS_CODE_ROOT, "tasks",  "__taskcache__", name)
    os.makedirs(dir, exist_ok=True)
    return os.path.normpath(dir)


def get_response_file_path(root_dir):
    dir = os.path.join(root_dir, "local", "tasks_room", "outputs")
    os.makedirs(dir, exist_ok=True)
    path = os.path.join(dir, "response.txt")
    return os.path.normpath(path)

#TODO change to query file path
def get_response_file_path(root_dir):
    dir = os.path.join(root_dir, "local", "tasks_room", "outputs")
    os.makedirs(dir, exist_ok=True)
    path = os.path.join(dir, "temporary_file.txt")
    return os.path.normpath(path)


def get_fill_text_directory(root_dir):
    dir = os.path.join(root_dir, "local", "tasks_room", "data", "fill_texts")
    os.makedirs(dir, exist_ok=True)
    return os.path.normpath(dir)


def get_query_templates_directory(root_dir):
    dir = os.path.join(root_dir, "local", "tasks_room", "data", "query_templates")
    os.makedirs(dir, exist_ok=True)
    return os.path.normpath(dir)


def get_temporary_script_path(root_dir):
    if not hasattr(get_temporary_script_path, "counter"):
        get_temporary_script_path.counter = 1
    else:
        get_temporary_script_path.counter += 1
    name = f"script_{get_temporary_script_path.counter}.py"
    dir = os.path.join(root_dir, "local", "tasks_room", "temp")
    os.makedirs(dir, exist_ok=True)
    path = os.path.join(dir, name)
    return os.path.normpath(path)


def get_output_directory(root_dir):
    dir = os.path.join(root_dir, "local", "tasks_room", "outputs")
    os.makedirs(dir, exist_ok=True)
    return os.path.normpath(dir)


def get_checkpoint_directory(root_dir):
    output_dir = get_output_directory(root_dir)
    dir = os.path.join(output_dir, "checkpoints")
    os.makedirs(dir, exist_ok=True)
    return os.path.normpath(dir)


# Allows to run subprocesses in the virtual environment of the external workspace
def get_environment_path(root_dir):
    path = os.path.join(root_dir, "venv")
    return os.path.normpath(path)


# Allows to run subprocesses in the virtual environment of this (the tasks) workspace.  
def get_environment_path_of_tasks():
    return get_environment_path(TASKS_CODE_ROOT)


def get_modules_info(root_dir):
    path = os.path.join(
        root_dir, "local", "tasks_room", "data", "modules_info.json"
    )
    if not os.path.exists(path):
        retrieve_modules(path)
    with open(path, "r") as file:
        modules_info = json.load(file)
    list_dirs = os.listdir(root_dir)
    modules_info["local"] = [dir for dir in list_dirs if os.path.isdir(dir)]
    return modules_info