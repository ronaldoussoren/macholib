.. macholib documentation master file, created by
   sphinx-quickstart on Tue Sep 28 22:23:35 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentation for macholib
==========================

macholib can be used to analyze and edit Mach-O headers, the executable
format used by Mac OS X.

It's typically used as a dependency analysis tool, and also to rewrite dylib
references in Mach-O headers to be @executable_path relative.

Though this tool targets a platform specific file format, it is pure python
code that is platform and endian independent.


Contents:

.. toctree::
   :maxdepth: 1

   changelog
   license
   scripts

Online Resources
================

* `Sourcecode repository on bitbucket <http://bitbucket.org/ronaldoussoren/macholib/>`_

* `The issue tracker <http://bitbucket.org/ronaldoussoren/macholib/issues>`_



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

