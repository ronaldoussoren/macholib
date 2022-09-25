"""
Shared setup file for simple python packages. Uses a setup.cfg that
is the same as the distutils2 project, unless noted otherwise.

It exists for two reasons:
1) This makes it easier to reuse setup.py code between my own
   projects

2) Easier migration to distutils2 when that catches on.

Additional functionality:

* Section metadata:
    requires-test:  Same as 'tests_require' option for setuptools.

"""

import os
import platform
import re
import sys
from distutils import log
from fnmatch import fnmatch

from setuptools import Command, setup
from setuptools.command import egg_info

if sys.version_info[0] == 2:
    from ConfigParser import NoOptionError, NoSectionError, RawConfigParser
else:
    from configparser import NoOptionError, NoSectionError, RawConfigParser

ROOTDIR = os.path.dirname(os.path.abspath(__file__))


#
#
#
# Parsing the setup.cfg and converting it to something that can be
# used by setuptools.setup()
#
#
#


def eval_marker(value):
    """
    Evaluate an distutils2 environment marker.

    This code is unsafe when used with hostile setup.cfg files,
    but that's not a problem for our own files.
    """
    value = value.strip()

    class M:
        def __init__(self, **kwds):
            for k, v in kwds.items():
                setattr(self, k, v)

    variables = {
        "python_version": "%d.%d" % (sys.version_info[0], sys.version_info[1]),
        "python_full_version": sys.version.split()[0],
        "os": M(name=os.name),
        "sys": M(platform=sys.platform),
        "platform": M(version=platform.version(), machine=platform.machine()),
    }

    return bool(eval(value, variables, variables))

    return True


def _opt_value(cfg, into, section, key, transform=None):
    try:
        v = cfg.get(section, key)
        if transform != _as_lines and ";" in v:
            v, marker = v.rsplit(";", 1)
            if not eval_marker(marker):
                return

            v = v.strip()

        if v:
            if transform:
                into[key] = transform(v.strip())
            else:
                into[key] = v.strip()

    except (NoOptionError, NoSectionError):
        pass


def _as_bool(value):
    if value.lower() in ("y", "yes", "on"):
        return True
    elif value.lower() in ("n", "no", "off"):
        return False
    elif value.isdigit():
        return bool(int(value))
    else:
        raise ValueError(value)


def _as_list(value):
    return value.split()


def _as_lines(value):
    result = []
    for v in value.splitlines():
        if ";" in v:
            v, marker = v.rsplit(";", 1)
            if not eval_marker(marker):
                continue

            v = v.strip()
            if v:
                result.append(v)
        else:
            result.append(v)
    return result


def _map_requirement(value):
    m = re.search(r"(\S+)\s*(?:\((.*)\))?", value)
    name = m.group(1)
    version = m.group(2)

    if version is None:
        return name

    else:
        mapped = []
        for v in version.split(","):
            v = v.strip()
            if v[0].isdigit():
                # Checks for a specific version prefix
                m = v.rsplit(".", 1)
                mapped.append(">=%s,<%s.%s" % (v, m[0], int(m[1]) + 1))

            else:
                mapped.append(v)
        return "%s %s" % (name, ",".join(mapped))


def _as_requires(value):
    requires = []
    for req in value.splitlines():
        if ";" in req:
            req, marker = req.rsplit(";", 1)
            if not eval_marker(marker):
                continue
            req = req.strip()

        if not req:
            continue
        requires.append(_map_requirement(req))
    return requires


def parse_setup_cfg():
    cfg = RawConfigParser()
    r = cfg.read([os.path.join(ROOTDIR, "setup.cfg")])
    if len(r) != 1:
        print("Cannot read 'setup.cfg'")
        sys.exit(1)

    metadata = {
        "name": cfg.get("x-metadata", "name"),
        "version": cfg.get("x-metadata", "version"),
        "description": cfg.get("x-metadata", "description"),
    }

    _opt_value(cfg, metadata, "x-metadata", "license")
    _opt_value(cfg, metadata, "x-metadata", "maintainer")
    _opt_value(cfg, metadata, "x-metadata", "maintainer_email")
    _opt_value(cfg, metadata, "x-metadata", "author")
    _opt_value(cfg, metadata, "x-metadata", "author_email")
    _opt_value(cfg, metadata, "x-metadata", "url")
    _opt_value(cfg, metadata, "x-metadata", "download_url")
    _opt_value(cfg, metadata, "x-metadata", "classifiers", _as_lines)
    _opt_value(cfg, metadata, "x-metadata", "platforms", _as_list)
    _opt_value(cfg, metadata, "x-metadata", "packages", _as_list)
    _opt_value(cfg, metadata, "x-metadata", "keywords", _as_list)

    try:
        v = cfg.get("x-metadata", "requires-dist")

    except (NoOptionError, NoSectionError):
        pass

    else:
        requires = _as_requires(v)
        if requires:
            metadata["install_requires"] = requires

    try:
        v = cfg.get("x-metadata", "requires-test")

    except (NoOptionError, NoSectionError):
        pass

    else:
        requires = _as_requires(v)
        if requires:
            metadata["tests_require"] = requires

    try:
        v = cfg.get("x-metadata", "long_description_file")
    except (NoOptionError, NoSectionError):
        pass

    else:
        parts = []
        for nm in v.split():
            fp = open(nm, "r")
            parts.append(fp.read())
            fp.close()

        metadata["long_description"] = "\n\n".join(parts)
        metadata["long_description_content_type"] = "text/x-rst; charset=UTF-8"

    try:
        v = cfg.get("x-metadata", "zip-safe")
    except (NoOptionError, NoSectionError):
        pass

    else:
        metadata["zip_safe"] = _as_bool(v)

    try:
        v = cfg.get("x-metadata", "console_scripts")
    except (NoOptionError, NoSectionError):
        pass

    else:
        if "entry_points" not in metadata:
            metadata["entry_points"] = {}

        metadata["entry_points"]["console_scripts"] = v.splitlines()

    if sys.version_info[:2] <= (2, 6):
        try:
            metadata["tests_require"] += ", unittest2"
        except KeyError:
            metadata["tests_require"] = "unittest2"

    return metadata


#
#
#
# Definitions of custom commands
#
#
#


def recursiveGlob(root, pathPattern):
    """
    Recursively look for files matching 'pathPattern'. Return a list
    of matching files/directories.
    """
    result = []

    for rootpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fnmatch(fn, pathPattern):
                result.append(os.path.join(rootpath, fn))
    return result


def importExternalTestCases(unittest, pathPattern="test_*.py", root=".", package=None):
    """
    Import all unittests in the PyObjC tree starting at 'root'
    """

    testFiles = recursiveGlob(root, pathPattern)
    testModules = [
        x[len(root) + 1 : -3].replace("/", ".") for x in testFiles  # noqa: E203
    ]  # noqa: E203
    if package is not None:
        testModules = [(package + "." + m) for m in testModules]

    suites = []

    for modName in testModules:
        try:
            module = __import__(modName)
        except ImportError:
            print("SKIP %s: %s" % (modName, sys.exc_info()[1]))
            continue

        if "." in modName:
            for elem in modName.split(".")[1:]:
                module = getattr(module, elem)

        s = unittest.defaultTestLoader.loadTestsFromModule(module)
        suites.append(s)

    return unittest.TestSuite(suites)


class my_egg_info(egg_info.egg_info):
    def run(self):
        egg_info.egg_info.run(self)

        path = os.path.join(self.egg_info, "PKG-INFO")

        with open(path, "r") as fp:
            contents = fp.read()

        try:
            before, after = contents.split("\n\n", 1)
        except ValueError:
            before = contents
            after = "\n\n"

        with open(path, "w") as fp:
            fp.write(before)
            fp.write(
                "\nProject-URL: Documentation, https://macholib.readthedocs.io/en/latest/\n"  # noqa: B950
            )
            fp.write(
                "Project-URL: Issue tracker, https://github.com/ronaldoussoren/macholib/issues\n"  # noqa: B950
            )
            fp.write(
                "Project-URL: Repository, https://github.com/ronaldoussoren/macholib\n\n"  # noqa: B950
            )
            fp.write(after)


class my_test(Command):
    description = "run test suite"
    user_options = [("verbosity=", None, "print what tests are run")]

    def initialize_options(self):
        self.verbosity = "1"

    def finalize_options(self):
        if isinstance(self.verbosity, str):
            self.verbosity = int(self.verbosity)

    def cleanup_environment(self):
        ei_cmd = self.get_finalized_command("egg_info")
        egg_name = ei_cmd.egg_name.replace("-", "_")

        to_remove = []
        for dirname in sys.path:
            bn = os.path.basename(dirname)
            if bn.startswith(egg_name + "-"):
                to_remove.append(dirname)

        for dirname in to_remove:
            log.info("removing installed %r from sys.path before testing" % (dirname,))
            sys.path.remove(dirname)

    def add_project_to_sys_path(self):
        from pkg_resources import (
            add_activation_listener,
            normalize_path,
            require,
            working_set,
        )

        self.reinitialize_command("egg_info")
        self.run_command("egg_info")
        self.reinitialize_command("build_ext", inplace=1)
        self.run_command("build_ext")

        # Check if this distribution is already on sys.path
        # and remove that version, this ensures that the right
        # copy of the package gets tested.

        self.__old_path = sys.path[:]
        self.__old_modules = sys.modules.copy()

        ei_cmd = self.get_finalized_command("egg_info")
        sys.path.insert(0, normalize_path(ei_cmd.egg_base))
        sys.path.insert(1, os.path.dirname(__file__))

        # Strip the namespace packages defined in this distribution
        # from sys.modules, needed to reset the search path for
        # those modules.

        nspkgs = getattr(self.distribution, "namespace_packages", None)
        if nspkgs is not None:
            for nm in nspkgs:
                del sys.modules[nm]

        # Reset pkg_resources state:
        add_activation_listener(lambda dist: dist.activate())
        working_set.__init__()
        require("%s==%s" % (ei_cmd.egg_name, ei_cmd.egg_version))

    def remove_from_sys_path(self):
        from pkg_resources import working_set

        sys.path[:] = self.__old_path
        sys.modules.clear()
        sys.modules.update(self.__old_modules)
        working_set.__init__()

    def run(self):
        import unittest

        # Ensure that build directory is on sys.path (py3k)

        self.cleanup_environment()
        self.add_project_to_sys_path()

        try:
            meta = self.distribution.metadata
            name = meta.get_name()
            test_pkg = name + "_tests"
            suite = importExternalTestCases(unittest, "test_*.py", test_pkg, test_pkg)

            runner = unittest.TextTestRunner(verbosity=self.verbosity)
            result = runner.run(suite)

            # Print out summary. This is a structured format that
            # should make it easy to use this information in scripts.
            summary = {
                "count": result.testsRun,
                "fails": len(result.failures),
                "errors": len(result.errors),
                "xfails": len(getattr(result, "expectedFailures", [])),
                "xpass": len(getattr(result, "expectedSuccesses", [])),
                "skip": len(getattr(result, "skipped", [])),
            }
            print("SUMMARY: %s" % (summary,))
            if summary["fails"] or summary["errors"]:
                sys.exit(1)

        finally:
            self.remove_from_sys_path()


#
#
#
#  And finally run the setuptools main entry point.
#
#
#

metadata = parse_setup_cfg()

setup(cmdclass={"test": my_test, "egg_info": my_egg_info}, **metadata)
