# This is a template for writing meta macros with arguments
# The script is going to be executed as a subprocess by the macro interpreter
# Generally, the template is referenced like this:
# #<name_of_file_without_ext>_macros+ (argument_1, argument_2, ...)
# The reference to this module's template is:
# #template_2_macros+ (True, 5)

# 1. Import sys
import sys

# 2. Define the arguments with default values
argument_1 = False
argument_2 = 1

# 3. Allow the arguments to be passed as command line arguments
if len(sys.argv) > 1:
    argument_1 = sys.argv[1].lower() == 'true'  # Convert to boolean
if len(sys.argv) > 2:
    argument_2 = int(sys.argv[2])

# 4. Write the macros text based on the arguments
macros_text = (
    "#T This is the Start of the macros_with_args template\n"
    "#C Juhuuu\n"
    "#T Chapter dedicated to argument_1\n"
)

if argument_1:
    macros_text += f"#C argument_1 was set to {argument_1}\n"

macros_text += (
    "#T Chapter dedicated to argument_2\n"
    f"#C argument_2 was set to {argument_2}\n"
    "#C \n"
    "#C Iterations Start:\n"
)

for i in range(argument_2):
    macros_text += f"#C Iteration {i + 1}\n"

# 5. Print the macros text; stdout is used to return the text to the calling script
print(macros_text)
