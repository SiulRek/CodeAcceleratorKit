# The costum_function should return a string.
def costum_function(argument_1, argument_2):
    output_text = (
        "This is the Start of the costum_function output text\n",
        "text\n",
        f"This is argument_1: {argument_1}\n"
        f"This is argument_2: {argument_2}\n"
        "The End of the costum_function output text\n"
    )
    return ''.join(output_text)