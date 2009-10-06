#!/usr/bin/env python

import os
import sys

from macholib.util import is_platform_file
from macholib.MachO import MachO
from mach_o import *

ARCH_MAP={
    ('<', '64-bit'): 'x86_64',
    ('<', '32-bit'): 'i386',
    ('>', '64-bit'): 'pp64',
    ('>', '32-bit'): 'ppc',
}

def dump_file(path):
    print path
    m = MachO(path)
    for header in m.headers:
        seen = set()
        if header.MH_MAGIC == MH_MAGIC_64:
            sz = '64-bit'
        else:
            sz = '32-bit'
        print '    [%s endian=%r size=%r arch=%r]' % (header.__class__.__name__, header.endian, sz, ARCH_MAP[(header.endian, sz)])
        for idx, name, other in header.walkRelocatables():
            if other not in seen:
                seen.add(other)
                print '\t' + other


def check_file(path):
    if not os.path.exists(path):
        print >>sys.stderr, '%s: %s: No such file or directory' % (sys.argv[0], path)
        return 1
    try:
        is_plat = is_platform_file(path)
    except IOError:
        print >>sys.stderr, '%s: %s: Permission denied' % (sys.argv[0], path)
        return 1
    else:
        if is_plat:
            dump_file(path)
    return 0

def main():
    args = sys.argv[1:]
    name = os.path.basename(sys.argv[0])
    err = 0
    if not args:
        raise SystemExit("usage: %s filename" % (name,))
    for base in args:
        if os.path.isdir(base):
            for root, dirs, files in os.walk(base):
                for fn in files:
                    err |= check_file(os.path.join(root, fn))
        else:
            err |= check_file(base)
    if err:
        raise SystemExit, 1

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
