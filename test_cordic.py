import math
import unittest

from CORDIC import (
    HyperbolicFunction,
    MathFunctions,
    TrigonometricFunction,
    eval_expression,
)


class ExpressionEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.trig = TrigonometricFunction()
        self.hyperbolic = HyperbolicFunction()
        self.math_functions = MathFunctions()

    def evaluate(self, expression, mode="none"):
        return eval_expression(
            expression,
            mode,
            self.trig,
            self.hyperbolic,
            self.math_functions,
        )

    def test_arithmetic_and_constants(self):
        self.assertAlmostEqual(self.evaluate("2^3 + pi"), 8 + math.pi, places=8)

    def test_degree_mode_and_parenthesis_shortcut(self):
        self.assertAlmostEqual(self.evaluate("sin30 + cos60", "deg"), 1.0, places=6)

    def test_logarithm(self):
        self.assertAlmostEqual(self.evaluate("logtaban(8, 2)"), 3.0, places=6)

    def test_measurement_style_numeric_expression(self):
        self.assertEqual(self.evaluate("4.5 + 3 * 2"), 10.5)

    def test_rejects_code_execution_and_attribute_access(self):
        rejected = (
            "__import__('os').system('echo unsafe')",
            "(1).__class__",
            "[1, 2][0]",
            "(lambda: 1)()",
        )
        for expression in rejected:
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    self.evaluate(expression)

    def test_rejects_resource_exhaustion_expression(self):
        with self.assertRaises(ValueError):
            self.evaluate("10^1000")

    def test_rejects_invalid_logarithm_base(self):
        with self.assertRaises(ValueError):
            self.evaluate("logtaban(8, 1)")


if __name__ == "__main__":
    unittest.main()
