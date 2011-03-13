from macholib import itergraphreport

import unittest

try:
    expectedFailure = unittest.expectedFailure
except AttributeError:
    expectedFailure = lambda function: function


class TestIterGraphReport (unittest.TestCase):
    @expectedFailure
    def test_missing(self):
        self.fail("tests are missing")

if __name__ == "__main__":
    unittest.main()
