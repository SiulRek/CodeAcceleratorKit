import unittest

from tasks.utils.for_automatic_prompt.format_identifiers_as_code import (
    format_identifiers_as_code,
    is_maybe_identifier,
    is_camel_case,
    is_snake_case,
)


class TestFormatLiteralsAsCode(unittest.TestCase):

    def test_is_maybe_identifier(self):
        self.assertTrue(is_maybe_identifier("hello_world"))
        self.assertTrue(is_maybe_identifier("hello"))
        self.assertFalse(is_maybe_identifier("hello!"))

    def test_is_camel_case(self):
        self.assertTrue(is_camel_case("helloWorld"))
        self.assertFalse(is_camel_case("helloworld"))
        self.assertFalse(is_camel_case("hello_world"))

    def test_is_snake_case(self):
        self.assertTrue(is_snake_case("hello_world"))
        self.assertFalse(is_snake_case("helloWorld"))
        self.assertFalse(is_snake_case("helloworld"))

    def test_format_identifiers_as_code_no_literals(self):
        self.assertEqual(format_identifiers_as_code("Hello world"), "Hello world")

    def test_format_identifiers_as_code_special_characters(self):
        self.assertEqual(format_identifiers_as_code("Hello, world!"), "Hello, world!")

    def test_format_identifiers_as_code_snake_case(self):
        self.assertEqual(format_identifiers_as_code("hello_world"), "`hello_world`")

    def test_format_identifiers_as_code_camel_case(self):
        self.assertEqual(format_identifiers_as_code("helloWorld"), "`helloWorld`")

    def test_format_identifiers_as_code_mixed(self):
        self.assertEqual(
            format_identifiers_as_code(
                "hello world! This_isATest for_snakeCase, andCamelCase."
            ),
            "hello world! `This_isATest` `for_snakeCase`, `andCamelCase`.",
        )

    def test_format_identifiers_as_code_special_case(self):
        self.assertEqual(format_identifiers_as_code("supertest__"), "`supertest`")

    def test_format_identifiers_as_code_combined(self):
        text = "Hello, this is a test_case and a CamelCaseExample and a var__."
        expected = "Hello, this is a `test_case` and a `CamelCaseExample` and a `var`."
        self.assertEqual(format_identifiers_as_code(text), expected)


if __name__ == "__main__":
    unittest.main()
