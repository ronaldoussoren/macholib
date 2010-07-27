#!/usr/bin/env python

try:
    import setuptools
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()

from setuptools import setup, Extension
import sys

VERSION = '1.3'
DESCRIPTION = "Mach-O header analysis and editing"
LONG_DESCRIPTION = """
macholib can be used to analyze and edit Mach-O headers, the executable
format used by Mac OS X.

It's typically used as a dependency analysis tool, and also to rewrite dylib
references in Mach-O headers to be @executable_path relative.

Though this tool targets a platform specific file format, it is pure python
code that is platform and endian independent.

NEWS
====

macholib 1.3
------------

macholib 1.3 is a feature release.

Features:

- Experimental Python 3.x support

  This version contains lightly tested support for Python 3.

macholib 1.2.2
--------------

macholib 1.2.2 is a bugfix release.

Bug fixes:

- Macholib should work better with 64-bit code
  (patch by Marc-Antoine Parent)
"""

CLASSIFIERS = filter(None, map(str.strip,
"""                 
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 3
Operating System :: MacOS :: MacOS X
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Software Development :: Build Tools
""".splitlines()))

if sys.version_info[0] == 3:
    extra_args = dict(use_2to3=True)
else:
    extra_args = dict()

setup(
    name="macholib",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    author="Bob Ippolito",
    author_email="bob@redivi.com",
    maintainer="Ronald Oussoren",
    maintainer_email="ronaldoussoren@mac.com",
    url="http://undefined.org/python/#macholib",
    license="MIT License",
    packages=['macholib'],
    platforms=['any'],
    install_requires=["altgraph>=0.7"],
    zip_safe=True,
    entry_points=dict(
        console_scripts=[
            'macho_find = macholib.macho_find:main',
            'macho_standalone = macholib.macho_standalone:main',
            'macho_dump = macholib.macho_dump:main',
        ],
    ),
    **extra_args
)
