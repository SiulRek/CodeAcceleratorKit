import unittest

from tasks.utils.for_format_python._refactor_exception import (
    _extract_prefix_quote_and_msg,
    _extract_exception_informations,
)

valid_cases = [
    # (raw_msg, (prefix, quote, msg))
    ("'This is a message'", ("", "'", "This is a message")),
    ('r"This is raw"', ("r", '"', "This is raw")),
    ("'Part one' 'Part two'", ("", "'", "Part one Part two")),
    ('r"Part one" r"Part two"', ("r", '"', "Part one Part two")),
    ('u"Part one" u"Part two"', ("u", '"', "Part one Part two")),
    ('ru"Part one" ru"Part two"', ("ru", '"', "Part one Part two")),
]

invalid_cases = [
    # (raw_msg, Exception)
    ("'Part one' \"Part two\"", ValueError),
    ("r'Part one' u'Part two'", ValueError),
    ("Not a string at all", ValueError),
]


class TestExtractPrefixQuoteAndMsg(unittest.TestCase):
    def test_valid_string(self):
        for i, (raw_msg, expected) in enumerate(valid_cases):
            with self.subTest(raw_msg=f"Test case {i+1}"):
                prefix, quote, msg = _extract_prefix_quote_and_msg(raw_msg)
                self.assertEqual(prefix, expected[0])
                self.assertEqual(quote, expected[1])
                self.assertEqual(msg, expected[2])

    def test_invalid_string(self):
        for raw_msg, expected_exception in invalid_cases:
            with self.subTest(raw_msg=raw_msg):
                with self.assertRaises(expected_exception):
                    _extract_prefix_quote_and_msg(raw_msg)


class TestExtractExceptionInformations(unittest.TestCase):
    def test_extract_single_exception(self):
        code = "    raise ValueError(r'Something went wrong') from exc"
        result = _extract_exception_informations(code)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["code"], code)
        self.assertEqual(result[0]["indent"], "    ")
        self.assertEqual(result[0]["exception_type"], "ValueError")
        self.assertEqual(result[0]["prefix"], "r")
        self.assertEqual(result[0]["quote"], "'")
        self.assertEqual(result[0]["message"], "Something went wrong")
        self.assertEqual(result[0]["from_clause"], "from exc")

    def test_multiline_exception(self):
        code = """
raise TypeError(
    "Invalid type"
    " for the operation"
    f" with {value}"
) from some_variable
        """
        result = _extract_exception_informations(code)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["exception_type"], "TypeError")
        self.assertEqual(
            result[0]["message"], "Invalid type for the operation with {value}"
        )
        self.assertEqual(result[0]["from_clause"], "from some_variable")
        self.assertEqual(result[0]["code"], code.strip())

    def test_ignores_non_string_exception_message(self):
        code = "raise RuntimeError(some_variable)"
        result = _extract_exception_informations(code)
        self.assertEqual(result, [])

    def test_multiple_exceptions(self):
        code = """
    raise ValueError("One Error")
    if True:
        not_an_exception()'
        raise KeyError("Another Error")
        """
        result = _extract_exception_informations(code)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["exception_type"], "ValueError")
        self.assertEqual(result[1]["exception_type"], "KeyError")


if __name__ == "__main__":
    unittest.main()
