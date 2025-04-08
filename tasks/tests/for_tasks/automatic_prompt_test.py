"""
TODO:
    1. Run the task Load File and References
    2. check the temporary file for the output.
"""
#cut_up
#REPLACE_ME
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
#cut_down

# ------------ MACROS TEXT START ------------------------------------

#B Start of Prompt
#B Merge begin text in multiple lines

#E End of prompt
#E Merge end text in multiple lines

#T Title of the chapter

#N The Normal text
#N Merge normal texts in multiple lines

#P reference_1.py, data\reference_2.py
#P reference_1.py, data\reference_2.py (True)

#P File
#P File (True)

#L

#*template_4

#template_1_meta

#template_2_meta+ (True, 5)

#template_3_func (True, 5)

#run data/example_script.py

#pylint data/example_script.py

#unittest File (2)

#tree . (2, False, ['temp', 'log'])

#summarize data/example_script_2.py (True)

#summarize_folder data (True, [], ['reference_1.py', 'reference_2.py', 'example_script_6.py'])

# send (False, 100)

# ------------ MACROS TEXT END ------------------------------------
