import unittest
from config_parser import ConfigParser

class TestConfigParser(unittest.TestCase):
    def setUp(self):
        self.parser = ConfigParser()

    def test_numbers(self):
        text = "42"
        self.parser.tokenize(text)
        result = self.parser.parse()
        self.assertEqual(result, 42)

    def test_arrays(self):
        text = "(1, 2, 3)"
        self.parser.tokenize(text)
        result = self.parser.parse()
        self.assertEqual(result, [1, 2, 3])

    def test_nested_arrays(self):
        text = "(1, (2, 3), 4)"
        self.parser.tokenize(text)
        result = self.parser.parse()
        self.assertEqual(result, [1, [2, 3], 4])

    def test_dictionaries(self):
        text = "{ A = 1 B = 2 }"
        self.parser.tokenize(text)
        result = self.parser.parse()
        self.assertEqual(result, {'A': 1, 'B': 2})

    def test_nested_dictionaries(self):
        text = "{ A = { B = 2 } C = 3 }"
        self.parser.tokenize(text)
        result = self.parser.parse()
        self.assertEqual(result, {'A': {'B': 2}, 'C': 3})

    def test_variables(self):
        text = "var X := 10;"
        self.parser.tokenize(text)
        result = self.parser.parse()
        self.assertIsNone(result)
        self.assertEqual(self.parser.constants['X'], 10)

    def test_variable_evaluation(self):
        text = "var X := 10; |X|"
        self.parser.tokenize(text)
        result = self.parser.parse()
        self.assertEqual(result, 10)

    def test_variable_in_structure(self):
        text = "var X := 10; { A = |X| }"
        self.parser.tokenize(text)
        result = self.parser.parse()
        self.assertEqual(result, {'A': 10})

    def test_comments(self):
        text = "% This is a comment\n42"
        self.parser.tokenize(text)
        result = self.parser.parse()
        self.assertEqual(result, 42)

    def test_multiline_comments(self):
        text = "--[[ This is a\nmultiline comment ]]\n42"
        self.parser.tokenize(text)
        result = self.parser.parse()
        self.assertEqual(result, 42)

    def test_syntax_error(self):
        text = "var X := 10"
        self.parser.tokenize(text)
        with self.assertRaises(SyntaxError):
            self.parser.parse()

    def test_complex_structure(self):
        text = """
        var X := (1, 2, 3);
        {
            A = |X|
            B = { C = 4 D = (5, 6) }
            E = --[[ comment ]] 7
        }
        """
        self.parser.tokenize(text)
        result = self.parser.parse()
        expected = {
            'A': [1, 2, 3],
            'B': {'C': 4, 'D': [5, 6]},
            'E': 7
        }
        self.assertEqual(result, expected)

    def test_undefined_variable(self):
        text = "|Y|"
        self.parser.tokenize(text)
        with self.assertRaises(SyntaxError):
            self.parser.parse()

    def test_multiple_assignments(self):
        text = """
        A = 1
        B = 2
        C = 3
        """
        self.parser.tokenize(text)
        result = self.parser.parse()
        expected = [{'A': 1}, {'B': 2}, {'C': 3}]
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
