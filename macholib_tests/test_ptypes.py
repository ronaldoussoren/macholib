from macholib import ptypes
from macholib._compat import B

import unittest
import sys

try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO
import mmap


class TestPTypes (unittest.TestCase):
    def test_missing(self):
        self.fail("tests are missing")




class MyStructure (ptypes.Structure):
    _fields_ = (
        ('foo', ptypes.p_int),
        ('bar', ptypes.p_ubyte),
    )

class MyFunStructure (ptypes.Structure):
    _fields_ = (
        ('fun', ptypes.p_char),
        ('mystruct', MyStructure),
    )

class TestPTypesSimple (unittest.TestCase):
    # Quick port of tests that used to be part of 
    # the macholib.ptypes source code


    def testBasic(self):
        for endian in '><':
            kw = dict(_endian_=endian)
            MYSTRUCTURE = B('\x00\x11\x22\x33\xFF')
            for fn, args in [
                        ('from_str', (MYSTRUCTURE,)),
                        ('from_mmap', (MYSTRUCTURE, 0)),
                        ('from_fileobj', (BytesIO(MYSTRUCTURE),)),
                    ]:
                myStructure = getattr(MyStructure, fn)(*args, **kw)
                if endian == '>':
                    self.assertEqual(myStructure.foo, 0x00112233)
                else:
                    self.assertEqual( myStructure.foo, 0x33221100)
                self.assertEqual(myStructure.bar, 0xFF)
                self.assertEqual(myStructure.to_str(), MYSTRUCTURE)

            MYFUNSTRUCTURE = B('!') + MYSTRUCTURE
            for fn, args in [
                        ('from_str', (MYFUNSTRUCTURE,)),
                        ('from_mmap', (MYFUNSTRUCTURE, 0)),
                        ('from_fileobj', (BytesIO(MYFUNSTRUCTURE),)),
                    ]:
                myFunStructure = getattr(MyFunStructure, fn)(*args, **kw)
                self.assertEqual(myFunStructure.mystruct, myStructure)
                self.assertEqual(myFunStructure.fun, B('!'), (myFunStructure.fun, B('!')))
                self.assertEqual(myFunStructure.to_str(), MYFUNSTRUCTURE)

            sio = BytesIO()
            myFunStructure.to_fileobj(sio)
            self.assertEqual(sio.getvalue(), MYFUNSTRUCTURE)

            mm = mmap.mmap(-1, ptypes.sizeof(MyFunStructure) * 2) 
            mm[:] = B('\x00') * (ptypes.sizeof(MyFunStructure) * 2)
            myFunStructure.to_mmap(mm, 0)
            self.assertEqual(MyFunStructure.from_mmap(mm, 0, **kw), myFunStructure)
            self.assertEqual(mm[:ptypes.sizeof(MyFunStructure)], MYFUNSTRUCTURE)
            self.assertEqual(mm[ptypes.sizeof(MyFunStructure):], B('\x00') * ptypes.sizeof(MyFunStructure))
            myFunStructure.to_mmap(mm, ptypes.sizeof(MyFunStructure))
            self.assertEqual(mm[:], MYFUNSTRUCTURE + MYFUNSTRUCTURE)
            self.assertEqual(MyFunStructure.from_mmap(mm, ptypes.sizeof(MyFunStructure), **kw), myFunStructure)

if __name__ == "__main__":
    unittest.main()
