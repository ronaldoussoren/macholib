macholib can be used to analyze and edit Mach-O headers, the executable
format used by Mac OS X.

It's typically used as a dependency analysis tool, and also to rewrite dylib
references in Mach-O headers to be @executable_path relative.

Though this tool targets a platform specific file format, it is pure python
code that is platform and endian independent.

CI Status
---------

* .. image:: https://github.com/ronaldoussoren/macholib/workflows/Lint/badge.svg
* .. image:: https://github.com/ronaldoussoren/macholib/workflows/Test/badge.svg

Project links
-------------

* `Documentation <https://macholib.readthedocs.io/en/latest/>`_

* `Issue Tracker <https://github.com/ronaldoussoren/macholib>`_

* `Repository <https://github.com/ronaldoussoren/macholib/>`_
