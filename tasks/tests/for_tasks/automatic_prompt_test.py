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

#T Test: Title of the chapter

#T Test: Normal Text (2)
#N The Normal text
#N Merge normal texts in multiple lines

#T Test: Paste File (2)
#P reference_1.py, data\reference_2.py

#T Test: Paste Current File (2)
#P File

#T Test: Paste File's Lines (2)
#P File ([[[23, 80] 

#T Test: Fill Text (2)
#*template_4

#T Test: Meta Macros (2)
#template_1_meta

#T Test: Meta Macros with Args (2)
#template_2_meta+ (True, 5)

#T Test: Custom Function (2)
#template_3_func (True, 5)

#T Test: Run Python Script (2)
#run data/example_script.py

#T Test: Run Pylint (2)
#pylint data/example_script.py

#T Test: Run Unittest (2)
#unittest File (2)

#T Test: Directory Tree (2)
#tree . (2, False, ['temp', 'log'])

#T Test: Summarize Python Script (2)
#summarize data/example_script_2.py (True)

#T Test: Summarize Folder (2)
#summarize_folder data (True, [], ['reference_1.py', 'reference_2.py', 'example_script_6.py'])

# send (False, 100)

# ------------ MACROS TEXT END ------------------------------------
