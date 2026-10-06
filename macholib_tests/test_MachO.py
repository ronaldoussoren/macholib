import contextlib
import io
import os
import struct
import sys
import tempfile
import uuid

from macholib import MachO, mach_o

if sys.version_info[:2] <= (2, 6):
    import unittest2 as unittest
else:
    import unittest


@contextlib.contextmanager
def temporary_macho_file(load_commands, endian=">"):
    struct_mach_header_64_format = endian + "IIIIIIII"
    cpu_type_arm64 = 0x100000C
    cpu_subtype_arm_all = 0x0
    mh_filetype_execute = 0x2
    ncmds = len(load_commands)
    sizeofcmds = sum([len(lc) for lc in load_commands])
    mach_header = struct.pack(
        struct_mach_header_64_format,
        mach_o.MH_MAGIC_64,
        cpu_type_arm64,
        cpu_subtype_arm_all,
        mh_filetype_execute,
        ncmds,
        sizeofcmds,
        0,
        0,
    )
    with tempfile.NamedTemporaryFile(delete=False) as macho_file:
        macho_file.write(mach_header)
        for lc in load_commands:
            macho_file.write(lc)
        # Close the file so it can be re-opened on Windows.
        macho_file.close()
        yield macho_file.name
        os.unlink(macho_file.name)


def lc_uuid(macho_uuid):
    lc_uuid_format = ">II16s"
    lc_uuid_size = struct.calcsize(lc_uuid_format)
    return struct.pack(lc_uuid_format, mach_o.LC_UUID, lc_uuid_size, macho_uuid.bytes)


def lc_unknown():
    lc_unknown_format = ">III"
    lc_unknown = 0x707A11ED  # Made-up load command. Hopefully never used.
    lc_unknown_size = struct.calcsize(lc_unknown_format)
    lc_unknown_value = 42  # Random value
    return struct.pack(lc_unknown_format, lc_unknown, lc_unknown_size, lc_unknown_value)


class TestMachO(unittest.TestCase):
    def test_known_load_command_should_succeed(self):
        macho_uuid = uuid.UUID("6894C0AE-C8B7-4E0B-A529-30BBEBA3703B")
        with temporary_macho_file([lc_uuid(macho_uuid)]) as macho_filename:
            macho = MachO.MachO(macho_filename, allow_unknown_load_commands=True)
            self.assertEqual(len(macho.headers), 1)
            self.assertEqual(len(macho.headers[0].commands), 1)
            load_command, command, _ = macho.headers[0].commands[0]
            self.assertEqual(load_command.cmd, mach_o.LC_UUID)
            self.assertEqual(uuid.UUID(bytes=command.uuid), macho_uuid)

    def test_modern_linkedit_load_commands(self):
        commands = (
            (0x36, "LC_ATOM_INFO"),
            (0x37, "LC_FUNCTION_VARIANTS"),
            (0x38, "LC_FUNCTION_VARIANT_FIXUPS"),
            (0x3A, "LC_LAZY_LOAD_DYLIB_INFO"),
        )
        for endian in (">", "<"):
            for value, name in commands:
                raw = struct.pack(endian + "IIII", value, 16, 0x1234, 0x5678)
                with temporary_macho_file([raw], endian) as filename:
                    command_info = MachO.MachO(filename).headers[0].commands[0]
                    load_command, command, data = command_info
                    self.assertEqual(getattr(mach_o, name), value)
                    self.assertEqual(mach_o.LC_NAMES[value], name)
                    self.assertIsInstance(command, mach_o.linkedit_data_command)
                    self.assertEqual(command.dataoff, 0x1234)
                    self.assertEqual(command.datasize, 0x5678)
                    self.assertEqual(data, b"")
                    output = io.BytesIO()
                    load_command.to_fileobj(output)
                    command.to_fileobj(output)
                    self.assertEqual(output.getvalue(), raw)

    def test_target_triple_load_command(self):
        triple = b"arm64e-apple-macosx15.0.0"
        for endian in (">", "<"):
            for offset in (12, 20):
                payload = b"x" * (offset - 12) + triple + b"\x00"
                payload += b"\x00" * (-(12 + len(payload)) % 8)
                raw = (
                    struct.pack(endian + "III", 0x39, 12 + len(payload), offset)
                    + payload
                )
                with temporary_macho_file([raw], endian) as filename:
                    command_info = MachO.MachO(filename).headers[0].commands[0]
                    load_command, command, data = command_info
                    self.assertEqual(mach_o.LC_TARGET_TRIPLE, 0x39)
                    self.assertEqual(mach_o.LC_NAMES[0x39], "LC_TARGET_TRIPLE")
                    self.assertIsInstance(command, mach_o.target_triple_command)
                    self.assertEqual(command.triple, offset)
                    self.assertEqual(
                        MachO.lc_str_value(command.triple, command_info), triple
                    )
                    self.assertEqual(command.describe(), {})
                    output = io.BytesIO()
                    load_command.to_fileobj(output)
                    command.to_fileobj(output)
                    output.write(data)
                    self.assertEqual(output.getvalue(), raw)

    def test_unknown_load_command_should_fail(self):
        with temporary_macho_file([lc_unknown()]) as macho_filename:
            with self.assertRaises(ValueError) as assert_context:
                MachO.MachO(macho_filename)

    def test_unknown_load_command_should_succeed_with_flag(self):
        with temporary_macho_file([lc_unknown()]) as macho_filename:
            macho = MachO.MachO(macho_filename, allow_unknown_load_commands=True)
            self.assertEqual(len(macho.headers), 1)
            self.assertEqual(len(macho.headers[0].commands), 1)
            load_command, command, data = macho.headers[0].commands[0]
            self.assertEqual(load_command.cmd, 0x707A11ED)
            self.assertIsInstance(command, mach_o.load_command)
            self.assertEqual(struct.unpack(">I", data), (42,))

    def test_mix_of_known_and_unknown_load_commands_should_allow_unknown_with_flag(
        self,
    ):
        macho_uuid = uuid.UUID("6894C0AE-C8B7-4E0B-A529-30BBEBA3703B")
        with temporary_macho_file(
            [lc_unknown(), lc_uuid(macho_uuid)]
        ) as macho_filename:
            macho = MachO.MachO(macho_filename, allow_unknown_load_commands=True)
            self.assertEqual(len(macho.headers), 1)
            self.assertEqual(len(macho.headers[0].commands), 2)
            load_command, command, data = macho.headers[0].commands[0]
            self.assertEqual(load_command.cmd, 0x707A11ED)
            self.assertIsInstance(command, mach_o.load_command)
            self.assertEqual(struct.unpack(">I", data), (42,))
            load_command, command, _ = macho.headers[0].commands[1]
            self.assertEqual(load_command.cmd, mach_o.LC_UUID)
            self.assertEqual(uuid.UUID(bytes=command.uuid), macho_uuid)


if __name__ == "__main__":
    unittest.main()
