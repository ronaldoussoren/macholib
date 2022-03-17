:mod:`macholib.MachO` --- Utilities for reading and writing Mach-O headers
==========================================================================

.. module:: macholib.MachO
   :synopsis: Utilities for reading and writing Mach-O headers

This module defines a class :class:`Macho`, which enables reading
and writing the Mach-O header of an executable file or dynamic
library on MacOS X.

.. function:: lc_str_value(offset, cmd_info)

   Returns the bytes for an ``lc_str`` value, given the *offset*
   of type ``lc_str`` and the ``cmd_info`` that contains the
   structure that contains the ``lc_str`` value. ``cmd_info`` is
   and item in the ``commands`` attribute of a MachOHeader instance.


.. class:: MachO(filename, allow_unknown_load_commands=False)

   Creates a MachO object by reading the Mach-O headers from
   *filename*.

   The *filename* should refer to an existing file in Mach-O
   format, and can refer to fat (universal) binaries.

   When *allow_unknown_load_commands* is false the instance will
   raise an error when the specified file contains unknown
   load commands.

   .. versionchanged: 1.16

      Added the *allow_unknown_load_commands* argument.

.. note:: more information will be added later
