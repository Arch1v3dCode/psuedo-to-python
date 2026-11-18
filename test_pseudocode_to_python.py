import unittest

from pseudocode_to_python import ConversionError, convert


class ConvertTests(unittest.TestCase):
    def test_if_else_and_operators(self):
        result = convert('IF score >= 10 AND ready = TRUE THEN\nOUTPUT "AND stays text"\nELSE\nOUTPUT score MOD 2\nENDIF')
        self.assertIn("if score >= 10 and ready = True:", result)
        self.assertIn('print("AND stays text")', result)
        self.assertIn("print(score % 2)", result)

    def test_for_range_includes_end_and_step(self):
        result = convert("FOR i FROM 1 TO 5 STEP 2\nOUTPUT i\nENDFOR")
        self.assertIn("_inclusive_range(1, 5, 2)", result)
        namespace = {}
        exec(result, namespace)
        self.assertEqual(list(namespace["_inclusive_range"](1, 5, 2)), [1, 3, 5])
        self.assertEqual(list(namespace["_inclusive_range"](5, 1, -2)), [5, 3, 1])

    def test_repeat_until(self):
        result = convert("REPEAT\nx <- x + 1\nUNTIL x >= 3")
        namespace = {"x": 0}
        exec(result, namespace)
        self.assertEqual(namespace["x"], 3)

    def test_unmatched_block_is_reported(self):
        with self.assertRaises(ConversionError):
            convert("ELSE")


if __name__ == "__main__":
    unittest.main()
