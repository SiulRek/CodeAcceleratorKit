# This is a template for writing costum functions to include in the prompt
# The script is going to be executed as a subprocess by the prompt interpreter
# Generally, the template is called like this:
# #<name_of_file_without_ext>_costum (argument_1, argument_2, ...)
# The call for this module's template is:
# #template_3_costum (True, 5)
# Moreover the module has to be located in a subfolder of the costum_functions folder, the subfolder name is used as the macro title in the prompt

# 1. Import sys and the costum function
import sys

from local.tasks_storage.costumizations.functions.costum_function_template.costum_function_example import (
    costum_function,
)

# 2. Define the arguments with default values
argument_1 = False
argument_2 = 1

# 3. Allow the arguments to be passed as command line arguments
if len(sys.argv) > 1:
    argument_1 = sys.argv[1].lower() == "true"  # Convert to boolean
if len(sys.argv) > 2:
    argument_2 = int(sys.argv[2])

# 4. Call the costum function with the arguments
output_text = costum_function(argument_1, argument_2)

# 5. Print the output text; stdout is used to return the text to the calling script
print(output_text)
