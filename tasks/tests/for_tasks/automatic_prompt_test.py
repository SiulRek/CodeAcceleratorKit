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

# End Text Macro

# Chapter title macro

# Normal text macro

# Paste files macro

# Paste current file

# Logged error macro

# Fill text macro

# Meta macro

# Meta macro with arguments

# Costum unction macro

# Run script macro

# Run pylint macro

# Run unittest macro

# Create directory tree macro

# Summarize python script macro

# Summarize folder macro

# Send Prompt Macro (remove space in '# send')
# send (False, 100)

# Checksum Macro

# Not a macro

# ------------ MACROS TEXT END ------------------------------------