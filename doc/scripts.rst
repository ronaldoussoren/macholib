Command-line tools
==================

macho_find
----------

Usage::

        $ macho_find dir...

Print the paths of all MachO binaries
in the specified directories.

macho_standalone
----------------

Usage::

        $ macho_standalone appbundle...

Convert one or more application bundles into 
standalone bundles. That is, copy all non-system
shared libraries and frameworks used by the bundle
into the bundle and rewrite load commands.

macho_dump
----------

Usage::
        
        $ macho_dump dir...

Print the MachO headers of all binaries in the
given directories.

