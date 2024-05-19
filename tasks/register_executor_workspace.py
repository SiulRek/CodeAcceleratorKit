import tasks.constants.getters as getters


def register_executor_workspace(workspace_dir):

    # Initialize all the directories in the workspace
    getters.get_output_directory(workspace_dir)
    getters.get_checkpoint_directory(workspace_dir)
    getters.get_fill_text_directory(workspace_dir)
    getters.get_query_templates_directory(workspace_dir)
    getters.get_query_file_path(workspace_dir)
    getters.get_query_file_path(workspace_dir)
    getters.get_environment_path(workspace_dir)
    getters.get_temporary_script_path(workspace_dir)  
    getters.get_checkpoint_directory(workspace_dir)

    # Initialize the modules info
    getters.get_modules_info(workspace_dir)