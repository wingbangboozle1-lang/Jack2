"""Runs the browser calculator's Node test (canonical/tests/calculator_test.js) when Node is available."""
import os
import shutil
import subprocess
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


class CalculatorTests(unittest.TestCase):
    def test_calculator_arithmetic(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not installed")
        result = subprocess.run([node, os.path.join(HERE, "calculator_test.js")],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr[-800:])
        self.assertIn("all assertions passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
