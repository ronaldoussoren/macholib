import unittest
import sys
from macholib import _compat

try:
    bytes
except NameError:
    bytes = str

class TestCompat (unittest.TestCase):
    def test_B(self):
        v = _compat.B("hello")
        self.assertTrue(isinstance(v, bytes))

        if sys.version_info[0] == 3:
            self.assertEqual(str(v), "b'hello'")
        else:
            self.assertEqual(str(v), "hello")

if __name__ == "__main__":
    unittest.main()
