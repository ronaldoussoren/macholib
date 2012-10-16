from macholib import SymbolTable

import unittest

try:
    expectedFailure = unittest.expectedFailure
except AttributeError:
    from macholib_tests.test_MachOGraph import expectedFailure


class TestSymbolTable (unittest.TestCase):
    @expectedFailure
    def test_missing(self):
        self.fail("tests are missing")

if __name__ == "__main__":
    unittest.main()
