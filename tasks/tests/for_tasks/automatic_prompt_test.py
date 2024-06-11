"""
TODO:
    1. Run the task Load File and References
    2. check the temporary file for the output.
"""

class ExampleClassCar:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

    def __eq__(self, other):
        return self.brand == other.brand and self.model == other.model

    def __str__(self):
        return f"{self.brand} {self.model}"

    def get_car(self):
        return self.brand, self.model

# ------------ MACROS TEXT START ------------------------------------

# Begin Text Macro
#B Start of Prompt
#B Merge begin text in multiple lines

# End Text Macro
#E End of prompt
#E Merge end text in multiple lines

# Chapter title macro
#T Title of the chapter

# Normal text macro
#N The Normal text
#N Merge normal texts in multiple lines

# Paste files macro
# reference_1.py, data\reference_2.py

# Paste files macro with post editing
# reference_1.py, data\reference_2.py (True)

# Paste current file
# File

# Logged error macro
#L

# Fill text macro
#*template_4

# Meta macro
#template_1_meta

# Meta macro with arguments
#template_2_meta+ (True, 5)

# Costum unction macro
#template_3_func (True, 5)

# Run script macro
#run data/example_script.py

# Run pylint macro
#pylint data/example_script.py

# Run unittest macro
#unittest File (2)

# Create directory tree macro
#tree . (2, False, ['temp', 'log'])

# Summarize python script macro
#summarize data/example_script_2.py (True)

# Summarize folder macro
#summarize_folder data (True, [], ['reference_1.py', 'reference_2.py', 'example_script_6.py'])

# Send Prompt Macro (remove space in '# send')
# send (False, 100)

# Checksum Macro
#checksum 22

# Not a macro
#copy_output_fun

# ------------ MACROS TEXT END ------------------------------------
