from macholib import mach_o

import sys
if sys.version_info[:2] <= (2,6):
    import unittest2 as unittest
else:
    import unittest


class TestMachO (unittest.TestCase):
    # This module is just a set of struct definitions,
    # not sure how to test those without replicating
    # the code.
    #
    # The definitions will get exercised by the
    # other tests, therefore testing is ignored
    # for now.

    def test_consistency(self):
        self.assertEqual(
            mach_o.MH_FLAGS_DESCRIPTIONS.keys(),
            mach_o.MH_FLAGS_NAMES.keys()
        )
        for k in dir (mach_o):
            if not k.startswith('MH_'): continue
            v = getattr(mach_o, k)
            if isinstance(v, int) and any(v == 1 << x for x in range(31)):
                self.assertTrue(v in mach_o.MH_FLAGS_NAMES, "No NAME and DESCRIPTION for %s"%(k,))


if __name__ == "__main__":
    unittest.main()
