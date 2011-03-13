Release history
===============

macholib 1.4
-------------

macholib 1.4 is a feature release

Features:

- Documentation is now generated using `sphinx <http://pypi.python.org/pypi/sphinx>`_
  and can be viewed at <http://packages.python.org/macholib>.

- The repository has moved to bitbucket

- There now is a testsuite

- Private functionality inside modules was renamed to
  a name starting with an underscore. 

  .. note:: if this change affects your code you are relying on undefined
     implementation features, please stop using private functions.

- The basic packable types in ``macholib.ptypes`` were renamed to better
  represent the corresponding C type. The table below lists the old
  an new names (the old names are still available, but are deprecated and
  will be removed in a future release).

  +--------------+--------------+
  | **Old name** | **New name** |
  +==============+==============+
  | p_byte       | p_int8       |
  +--------------+--------------+
  | p_ubyte      | p_uint8      |
  +--------------+--------------+
  | p_short      | p_int16      |
  +--------------+--------------+
  | p_ushort     | p_uint16     |
  +--------------+--------------+
  | p_int        | p_int32      |
  +--------------+--------------+
  | p_uint       | p_uint32     |
  +--------------+--------------+
  | p_long       | p_int32      |
  +--------------+--------------+
  | p_ulong      | p_uint32     |
  +--------------+--------------+
  | p_longlong   | p_int64      |
  +--------------+--------------+
  | p_ulonglong  | p_uint64     |
  +--------------+--------------+

  ``Macholib.ptypes.p_ptr`` is no longer present as it had an unclear 
  definition and isn't actually used in the codebase.


Bug fixes:

- The semantics of ``dyld.dyld_default_search`` were changed a bit,
  it now first searches the framework path (if appropriate) and then
  the linker path, irrespective of the value of the ``DYLD_FALLBACK*``
  environment variables.
  
  Previous versions would change the search order when those variables
  was set, which is odd and doesn't correspond with the documented
  behaviour of the system dyld.

- It is once again possible to install using python2.5

- The source distribution includes all files, this was broken
  due to the switch to mercurial (which confused setuptools)

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
