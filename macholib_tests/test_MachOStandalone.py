from macholib import MachOStandalone

import unittest


class TestMachOStandalone (unittest.TestCase):
    def test_missing(self):
        self.fail("tests are missing")

if __name__ == "__main__":
    unittest.main()
