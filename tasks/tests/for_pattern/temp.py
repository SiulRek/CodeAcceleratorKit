import unittest
import re

# Improved regex pattern to capture all items after "#only"
SELECT_ONLY_PATTERN = re.compile(r"#only\s*((?:\S+)\s*(?:,\s*\S+\s*)*)")

class TestSelectOnlyPattern(unittest.TestCase):
    def test_valid_input_1(self):
        # Test with a single item using search
        match = SELECT_ONLY_PATTERN.search("#only item1")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "item1")

    def test_valid_input_2(self):
        # Test with multiple items separated by commas and spaces using search
        match = SELECT_ONLY_PATTERN.search("#only item1, item2, item3")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "item1, item2, item3")

    def test_invalid_input(self):
        # Test with invalid input where the pattern should not match (missing "#only") using search
        match = SELECT_ONLY_PATTERN.search("only item1, item2")
        self.assertIsNone(match)

    def test_edge_case_input(self):
        # Test with no spaces after commas using search
        match = SELECT_ONLY_PATTERN.search("#only item1,item2,item3")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "item1,item2,item3")

if __name__ == "__main__":
    unittest.main()
