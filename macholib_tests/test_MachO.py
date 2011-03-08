from macholib import MachO

import unittest


class TestMachO (unittest.TestCase):
    def test_missing(self):
        self.fail("tests are missing")

if __name__ == "__main__":
    unittest.main()
