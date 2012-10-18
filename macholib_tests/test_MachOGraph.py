from macholib import MachOGraph

import unittest

try:
    expectedFailure = unittest.expectedFailure
except AttributeError:
    def expectedFailure(function):
        def wrapper(self):
            try:
                function(self)
            except AssertionError:
                print ("ignore expected failure")
        return wrapper


class TestMachOGraph (unittest.TestCase):
    @expectedFailure
    def test_missing(self):
        self.fail("tests are missing")

if __name__ == "__main__":
    unittest.main()
