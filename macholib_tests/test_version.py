import macholib

import sys
import os

if sys.version_info[:2] <= (2,6):
    import unittest2 as unittest
else:
    import unittest

class TestVersion (unittest.TestCase):
    def test_version(self):
        fn = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'setup.cfg')
        with open(fn) as fp:
            for ln in fp:
                if ln.startswith('version'):
                    setup_version = ln.split('=')[-1].strip()
                    break
            else:
                self.fail("Cannot determine wheel version")
        self.assertEqual(setup_version, macholib.__version__)

if __name__ == "__main__":
    unittest.main()
