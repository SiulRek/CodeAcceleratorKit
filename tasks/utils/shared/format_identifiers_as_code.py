special_characters = [
    "'",
    '"',
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    ":",
    ",",
    ".",
    "!",
    "?",
    ";",
    "#",
    "@",
    "$",
    "%",
    "^",
    "&",
    "*",
    "+",
    "-",
    "=",
    "<",
    ">",
    "|",
    "\\",
    "/",
    "~",
    "`",
]


def is_maybe_identifier(word):
    """
    Check if the word is a identifier.

    Parameters
    ----------
    word (str)
        The word to check.

    Returns
    -------
    bool
        True if the word is a identifier, False otherwise.
    """
    for sign in special_characters:
        if sign in word:
            return False
    return True


def is_camel_case(word):
    """
    Check if the word is in camel case.

    Parameters
    ----------
    word (str)
        The word to check.

    Returns
    -------
    bool
        True if the word is in camel case, False otherwise.
    """
    if "_" in word:
        return False
    isupper_list = [x.isupper() for x in word][1:]  # First letter is not considered
    if isupper_list.count(True) > 0 and not all(isupper_list):
        return True
    return False


def is_snake_case(word):
    """
    Check if the word is in snake case.

    Parameters
    ----------
    word (str)
        The word to check.

    Returns
    -------
    bool
        True if the word is in snake case, False otherwise.
    """
    return "_" in word


def extract_punctuation(word):
    """
    Extracts the punctuation from the word.

    Parameters
    ----------
    word (str)
        The word to remove the punctuation from.

    Returns
    -------
    tuple
        The word without the punctuation and the punctuation.
    """
    punctuation_signs = [".", ",", ":", ";", "!", "?"]
    for sign in punctuation_signs:
        if word.endswith(sign):
            return word[:-1], sign
    return word, ""


def format_identifiers_as_code(text):
    """
    Format the identifiers in the text as code. Words wit underscores or in
    CamelCase are considered identifiers, when they are not surrounded by
    special characters.

    Parameters
    ----------
    text (str)
        The text to format the identifiers in.

    Returns
    -------
    list
        The text with the identifiers formatted as code.

    Examples;
        >>> format_identifiers_as_code("Hello, this is a test_case and a CamelCaseExample.")
        "Hello, this is a `test_case` and a `CamelCaseExample`."
    """
    words = text.split()
    formatted_text = []
    for word in words:
        word, punctuation = extract_punctuation(word)
        if not is_maybe_identifier(word):
            formatted_text.append(word)
            continue
        if is_snake_case(word) or is_camel_case(word):

            if len(word.split("_")) == 3 and word.endswith(
                "__"
            ):  # Case intentionally added to force formatting
                word = word[:-2]
            word = "`" + word + "`"  # Format the word as code
        formatted_text.append(word + punctuation)
    return " ".join(formatted_text)
