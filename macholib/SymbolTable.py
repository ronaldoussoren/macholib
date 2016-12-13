"""
Class to read the symbol table from a Mach-O header
"""
from __future__ import with_statement

from macholib.mach_o import *
import sys

__all__ = ['SymbolTable']

if sys.version_info[0] == 2:
    range = xrange

class SymbolTable(object):
    def __init__(self, macho, header=None, openfile=None):
        if openfile is None:
            openfile = open
        if header is None:
            header = macho.headers[0]
        self.macho_header = header
        with openfile(macho.filename, 'rb') as fh:
            self.symtab = header.getSymbolTableCommand()
            self.dysymtab = header.getDynamicSymbolTableCommand()
            try:
                if self.symtab is not None:
                    self.nlists = self.readSymbolTable(fh)

                if self.dysymtab is not None:
                    self.readDynamicSymbolTable(fh)
            except:
                raise

    def readSymbolTable(self, fh):
        cmd = self.symtab
        fh.seek(self.macho_header.offset + cmd.stroff)
        strtab = fh.read(cmd.strsize)
        fh.seek(self.macho_header.offset + cmd.symoff)
        nlists = []

        if self.macho_header.MH_MAGIC in [MH_MAGIC_64, MH_CIGAM_64]:
            cls = nlist_64
        else:
            cls = nlist

        for i in range(cmd.nsyms):
            cmd = cls.from_fileobj(fh, _endian_=self.macho_header.endian)
            if cmd.n_un == 0:
                nlists.append((cmd, ''))
            else:
                nlists.append((cmd, strtab[cmd.n_un:strtab.find(b'\x00', cmd.n_un)]))
        return nlists

    def readDynamicSymbolTable(self, fh):
        cmd = self.dysymtab
        nlists = self.nlists

        self.localsyms = nlists[cmd.ilocalsym:cmd.ilocalsym+cmd.nlocalsym]
        self.extdefsyms = nlists[cmd.iextdefsym:cmd.iextdefsym+cmd.nextdefsym]
        self.undefsyms = nlists[cmd.iundefsym:cmd.iundefsym+cmd.nundefsym]
        if cmd.tocoff == 0:
           self.toc = None
        else:
           self.toc = self.readtoc(fh, cmd.tocoff, cmd.ntoc)

        # if cmd.modtaboff == 0:
        #    self.modtab = None
        # else:
        #    self.modtab = self.readmodtab(fh, cmd.modtaboff, cmd.nmodtab)

        # if cmd.extrefsymoff == 0:
        #     self.extrefsym = None
        # else:
        #     self.extrefsym = self.readsym(fh, cmd.extrefsymoff, cmd.nextrefsyms)
        #if cmd.indirectsymoff == 0:
        #    self.indirectsym = None
        #else:
        #    self.indirectsym = self.readsym(fh, cmd.indirectsymoff, cmd.nindirectsyms)
        #if cmd.extreloff == 0:
        #    self.extrel = None
        #else:
        #    self.extrel = self.readrel(fh, cmd.extreloff, cmd.nextrel)
        #if cmd.locreloff == 0:
        #    self.locrel = None
        #else:
        #    self.locrel = self.readrel(fh, cmd.locreloff, cmd.nlocrel)

    def readtoc(self, fh, off, n):
        fh.seek(self.macho_header.offset + off)
        return [dylib_table_of_contents.from_fileobj(fh) for i in range(n)]

    def readmodtab(self, fh, off, n):
        fh.seek(self.macho_header.offset + off)
        return [dylib_module.from_fileobj(fh) for i in range(n)]

    def readsym(self, fh, off, n):
        fh.seek(self.macho_header.offset + off)
        refs = []
        for i in range(n):
            ref = dylib_reference.from_fileobj(fh)
            isym, flags = divmod(ref.isym_flags, 256)
            refs.append((self.nlists[isym], flags))
        return refs

    def readrel(self, fh, off, n):
        fh.seek(self.macho_header.offset + off)
        return [relocation_info.from_fileobj(fh) for i in range(n)]
