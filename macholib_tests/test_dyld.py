from macholib import dyld

import unittest
import sys
import os

try:
    expectedFailure = unittest.expectedFailure
except AttributeError:
    expectedFailure = lambda function: function


class TestDyld (unittest.TestCase):
    @expectedFailure
    def test_missing(self):
        self.fail("tests are missing")

    if sys.version_info[0] == 2:
        def test_ensure_utf8(self):
            self.assertEqual(dyld._ensure_utf8("hello"), "hello")
            self.assertEqual(dyld._ensure_utf8("hello".decode('utf-8')), "hello")
            self.assertEqual(dyld._ensure_utf8(None), None)

    else:
        def test_ensure_utf8(self):
            self.assertEqual(dyld._ensure_utf8("hello"), "hello")
            self.assertEqual(dyld._ensure_utf8(None), None)
            self.assertRaises(ValueError, dyld._ensure_utf8, B("hello"))

    def test__dyld_env(self):
        _env = os.environ
        new = os.environ = dict([(k, _env[k]) for k in _env if 'DYLD' not in k])

        try:
            self.assertEqual(dyld._dyld_env(None, 'DYLD_FOO'), [])
            self.assertEqual(dyld._dyld_env({'DYLD_FOO':'bar'}, 'DYLD_FOO'), ['bar'])
            self.assertEqual(dyld._dyld_env({'DYLD_FOO':'bar:baz'}, 'DYLD_FOO'), ['bar', 'baz'])
            self.assertEqual(dyld._dyld_env({}, 'DYLD_FOO'), [])
            os.environ['DYLD_FOO'] = 'foobar'
            self.assertEqual(dyld._dyld_env(None, 'DYLD_FOO'), ['foobar'])
            os.environ['DYLD_FOO'] = 'foobar:nowhere'
            self.assertEqual(dyld._dyld_env(None, 'DYLD_FOO'), ['foobar', 'nowhere'])
            self.assertEqual(dyld._dyld_env({'DYLD_FOO':'bar'}, 'DYLD_FOO'), ['bar'])
            self.assertEqual(dyld._dyld_env({}, 'DYLD_FOO'), [])


            self.assertEqual(dyld.dyld_image_suffix(), None)
            self.assertEqual(dyld.dyld_image_suffix(None), None)
            self.assertEqual(dyld.dyld_image_suffix({'DYLD_IMAGE_SUFFIX':'bar'}), 'bar')
            os.environ['DYLD_IMAGE_SUFFIX'] = 'foobar'
            self.assertEqual(dyld.dyld_image_suffix(), 'foobar')
            self.assertEqual(dyld.dyld_image_suffix(None), 'foobar')

        finally:
            os.environ = _env

    def test_dyld_helpers(self):
        record = []
        def fake__dyld_env(env, key):
            record.append((env, key))
            return ['hello']

        orig_env = dyld._dyld_env
        dyld._dyld_env = fake__dyld_env
        try:
            self.assertEqual(dyld.dyld_framework_path(), ['hello'])
            self.assertEqual(dyld.dyld_framework_path({}), ['hello'])

            self.assertEqual(dyld.dyld_library_path(), ['hello'])
            self.assertEqual(dyld.dyld_library_path({}), ['hello'])

            self.assertEqual(dyld.dyld_fallback_framework_path(), ['hello'])
            self.assertEqual(dyld.dyld_fallback_framework_path({}), ['hello'])

            self.assertEqual(dyld.dyld_fallback_library_path(), ['hello'])
            self.assertEqual(dyld.dyld_fallback_library_path({}), ['hello'])

        finally:
            dyld._dyld_env = orig_env

        self.assertEqual(record, [
            (None, 'DYLD_FRAMEWORK_PATH'),
            ({}, 'DYLD_FRAMEWORK_PATH'),
            (None, 'DYLD_LIBRARY_PATH'),
            ({}, 'DYLD_LIBRARY_PATH'),
            (None, 'DYLD_FALLBACK_FRAMEWORK_PATH'),
            ({}, 'DYLD_FALLBACK_FRAMEWORK_PATH'),
            (None, 'DYLD_FALLBACK_LIBRARY_PATH'),
            ({}, 'DYLD_FALLBACK_LIBRARY_PATH'),
        ])

    def test_dyld_suffix_search(self):
        orig_suffix = dyld.dyld_image_suffix
        try:
            envs = [object()]
            def fake_suffix(env):
                envs[0] = env
                return None
            dyld.dyld_image_suffix = fake_suffix

            iterator = [
                '/usr/lib/foo',
                '/usr/lib/foo.dylib',
            ]
            result = dyld.dyld_image_suffix_search(iter(iterator))
            self.assertEqual(list(result), iterator)
            self.assertEqual(envs[0], None)

            result = dyld.dyld_image_suffix_search(iter(iterator), {})
            self.assertEqual(list(result), iterator)
            self.assertEqual(envs[0], {})

            envs = [object()]
            def fake_suffix(env):
                envs[0] = env
                return '_profile'
            dyld.dyld_image_suffix = fake_suffix

            iterator = [
                '/usr/lib/foo',
                '/usr/lib/foo.dylib',
            ]
            result = dyld.dyld_image_suffix_search(iter(iterator))
            self.assertEqual(list(result), [
                    '/usr/lib/foo_profile',
                    '/usr/lib/foo',
                    '/usr/lib/foo_profile.dylib',
                    '/usr/lib/foo.dylib',
                ])
            self.assertEqual(envs[0], None)

            result = dyld.dyld_image_suffix_search(iter(iterator), {})
            self.assertEqual(list(result), [
                    '/usr/lib/foo_profile',
                    '/usr/lib/foo',
                    '/usr/lib/foo_profile.dylib',
                    '/usr/lib/foo.dylib',
                ])
            self.assertEqual(envs[0], {})

        finally:
            dyld.dyld_image_suffix = orig_suffix



class TestTrivialDyld (unittest.TestCase):
    # Tests ported from the implementation file
    def testBasic(self):
        self.assertEqual(dyld.dyld_find('libSystem.dylib'), '/usr/lib/libSystem.dylib')
        self.assertEqual(dyld.dyld_find('System.framework/System'), '/System/Library/Frameworks/System.framework/System')

if __name__ == "__main__":
    unittest.main()
