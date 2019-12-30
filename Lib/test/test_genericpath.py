"""
Tests common to genericpath, ntpath na posixpath
"""

agiza genericpath
agiza os
agiza sys
agiza unittest
agiza warnings
kutoka test agiza support
kutoka test.support.script_helper agiza assert_python_ok
kutoka test.support agiza FakePath


eleza create_file(filename, data=b'foo'):
    ukijumuisha open(filename, 'xb', 0) kama fp:
        fp.write(data)


kundi GenericTest:
    common_attributes = ['commonprefix', 'getsize', 'getatime', 'getctime',
                         'getmtime', 'exists', 'isdir', 'isfile']
    attributes = []

    eleza test_no_argument(self):
        kila attr kwenye self.common_attributes + self.attributes:
            ukijumuisha self.assertRaises(TypeError):
                getattr(self.pathmodule, attr)()
                ashiria self.fail("{}.{}() did sio ashiria a TypeError"
                                .format(self.pathmodule.__name__, attr))

    eleza test_commonprefix(self):
        commonprefix = self.pathmodule.commonprefix
        self.assertEqual(
            commonprefix([]),
            ""
        )
        self.assertEqual(
            commonprefix(["/home/swenson/spam", "/home/swen/spam"]),
            "/home/swen"
        )
        self.assertEqual(
            commonprefix(["/home/swen/spam", "/home/swen/eggs"]),
            "/home/swen/"
        )
        self.assertEqual(
            commonprefix(["/home/swen/spam", "/home/swen/spam"]),
            "/home/swen/spam"
        )
        self.assertEqual(
            commonprefix(["home:swenson:spam", "home:swen:spam"]),
            "home:swen"
        )
        self.assertEqual(
            commonprefix([":home:swen:spam", ":home:swen:eggs"]),
            ":home:swen:"
        )
        self.assertEqual(
            commonprefix([":home:swen:spam", ":home:swen:spam"]),
            ":home:swen:spam"
        )

        self.assertEqual(
            commonprefix([b"/home/swenson/spam", b"/home/swen/spam"]),
            b"/home/swen"
        )
        self.assertEqual(
            commonprefix([b"/home/swen/spam", b"/home/swen/eggs"]),
            b"/home/swen/"
        )
        self.assertEqual(
            commonprefix([b"/home/swen/spam", b"/home/swen/spam"]),
            b"/home/swen/spam"
        )
        self.assertEqual(
            commonprefix([b"home:swenson:spam", b"home:swen:spam"]),
            b"home:swen"
        )
        self.assertEqual(
            commonprefix([b":home:swen:spam", b":home:swen:eggs"]),
            b":home:swen:"
        )
        self.assertEqual(
            commonprefix([b":home:swen:spam", b":home:swen:spam"]),
            b":home:swen:spam"
        )

        testlist = ['', 'abc', 'Xbcd', 'Xb', 'XY', 'abcd',
                    'aXc', 'abd', 'ab', 'aX', 'abcX']
        kila s1 kwenye testlist:
            kila s2 kwenye testlist:
                p = commonprefix([s1, s2])
                self.assertKweli(s1.startswith(p))
                self.assertKweli(s2.startswith(p))
                ikiwa s1 != s2:
                    n = len(p)
                    self.assertNotEqual(s1[n:n+1], s2[n:n+1])

    eleza test_getsize(self):
        filename = support.TESTFN
        self.addCleanup(support.unlink, filename)

        create_file(filename, b'Hello')
        self.assertEqual(self.pathmodule.getsize(filename), 5)
        os.remove(filename)

        create_file(filename, b'Hello World!')
        self.assertEqual(self.pathmodule.getsize(filename), 12)

    eleza test_filetime(self):
        filename = support.TESTFN
        self.addCleanup(support.unlink, filename)

        create_file(filename, b'foo')

        ukijumuisha open(filename, "ab", 0) kama f:
            f.write(b"bar")

        ukijumuisha open(filename, "rb", 0) kama f:
            data = f.read()
        self.assertEqual(data, b"foobar")

        self.assertLessEqual(
            self.pathmodule.getctime(filename),
            self.pathmodule.getmtime(filename)
        )

    eleza test_exists(self):
        filename = support.TESTFN
        bfilename = os.fsencode(filename)
        self.addCleanup(support.unlink, filename)

        self.assertIs(self.pathmodule.exists(filename), Uongo)
        self.assertIs(self.pathmodule.exists(bfilename), Uongo)

        create_file(filename)

        self.assertIs(self.pathmodule.exists(filename), Kweli)
        self.assertIs(self.pathmodule.exists(bfilename), Kweli)

        self.assertIs(self.pathmodule.exists(filename + '\udfff'), Uongo)
        self.assertIs(self.pathmodule.exists(bfilename + b'\xff'), Uongo)
        self.assertIs(self.pathmodule.exists(filename + '\x00'), Uongo)
        self.assertIs(self.pathmodule.exists(bfilename + b'\x00'), Uongo)

        ikiwa self.pathmodule ni sio genericpath:
            self.assertIs(self.pathmodule.lexists(filename), Kweli)
            self.assertIs(self.pathmodule.lexists(bfilename), Kweli)

            self.assertIs(self.pathmodule.lexists(filename + '\udfff'), Uongo)
            self.assertIs(self.pathmodule.lexists(bfilename + b'\xff'), Uongo)
            self.assertIs(self.pathmodule.lexists(filename + '\x00'), Uongo)
            self.assertIs(self.pathmodule.lexists(bfilename + b'\x00'), Uongo)

    @unittest.skipUnless(hasattr(os, "pipe"), "requires os.pipe()")
    eleza test_exists_fd(self):
        r, w = os.pipe()
        jaribu:
            self.assertKweli(self.pathmodule.exists(r))
        mwishowe:
            os.close(r)
            os.close(w)
        self.assertUongo(self.pathmodule.exists(r))

    eleza test_isdir(self):
        filename = support.TESTFN
        bfilename = os.fsencode(filename)
        self.assertIs(self.pathmodule.isdir(filename), Uongo)
        self.assertIs(self.pathmodule.isdir(bfilename), Uongo)

        self.assertIs(self.pathmodule.isdir(filename + '\udfff'), Uongo)
        self.assertIs(self.pathmodule.isdir(bfilename + b'\xff'), Uongo)
        self.assertIs(self.pathmodule.isdir(filename + '\x00'), Uongo)
        self.assertIs(self.pathmodule.isdir(bfilename + b'\x00'), Uongo)

        jaribu:
            create_file(filename)
            self.assertIs(self.pathmodule.isdir(filename), Uongo)
            self.assertIs(self.pathmodule.isdir(bfilename), Uongo)
        mwishowe:
            support.unlink(filename)

        jaribu:
            os.mkdir(filename)
            self.assertIs(self.pathmodule.isdir(filename), Kweli)
            self.assertIs(self.pathmodule.isdir(bfilename), Kweli)
        mwishowe:
            support.rmdir(filename)

    eleza test_isfile(self):
        filename = support.TESTFN
        bfilename = os.fsencode(filename)
        self.assertIs(self.pathmodule.isfile(filename), Uongo)
        self.assertIs(self.pathmodule.isfile(bfilename), Uongo)

        self.assertIs(self.pathmodule.isfile(filename + '\udfff'), Uongo)
        self.assertIs(self.pathmodule.isfile(bfilename + b'\xff'), Uongo)
        self.assertIs(self.pathmodule.isfile(filename + '\x00'), Uongo)
        self.assertIs(self.pathmodule.isfile(bfilename + b'\x00'), Uongo)

        jaribu:
            create_file(filename)
            self.assertIs(self.pathmodule.isfile(filename), Kweli)
            self.assertIs(self.pathmodule.isfile(bfilename), Kweli)
        mwishowe:
            support.unlink(filename)

        jaribu:
            os.mkdir(filename)
            self.assertIs(self.pathmodule.isfile(filename), Uongo)
            self.assertIs(self.pathmodule.isfile(bfilename), Uongo)
        mwishowe:
            support.rmdir(filename)

    eleza test_samefile(self):
        file1 = support.TESTFN
        file2 = support.TESTFN + "2"
        self.addCleanup(support.unlink, file1)
        self.addCleanup(support.unlink, file2)

        create_file(file1)
        self.assertKweli(self.pathmodule.samefile(file1, file1))

        create_file(file2)
        self.assertUongo(self.pathmodule.samefile(file1, file2))

        self.assertRaises(TypeError, self.pathmodule.samefile)

    eleza _test_samefile_on_link_func(self, func):
        test_fn1 = support.TESTFN
        test_fn2 = support.TESTFN + "2"
        self.addCleanup(support.unlink, test_fn1)
        self.addCleanup(support.unlink, test_fn2)

        create_file(test_fn1)

        func(test_fn1, test_fn2)
        self.assertKweli(self.pathmodule.samefile(test_fn1, test_fn2))
        os.remove(test_fn2)

        create_file(test_fn2)
        self.assertUongo(self.pathmodule.samefile(test_fn1, test_fn2))

    @support.skip_unless_symlink
    eleza test_samefile_on_symlink(self):
        self._test_samefile_on_link_func(os.symlink)

    eleza test_samefile_on_link(self):
        jaribu:
            self._test_samefile_on_link_func(os.link)
        tatizo PermissionError kama e:
            self.skipTest('os.link(): %s' % e)

    eleza test_samestat(self):
        test_fn1 = support.TESTFN
        test_fn2 = support.TESTFN + "2"
        self.addCleanup(support.unlink, test_fn1)
        self.addCleanup(support.unlink, test_fn2)

        create_file(test_fn1)
        stat1 = os.stat(test_fn1)
        self.assertKweli(self.pathmodule.samestat(stat1, os.stat(test_fn1)))

        create_file(test_fn2)
        stat2 = os.stat(test_fn2)
        self.assertUongo(self.pathmodule.samestat(stat1, stat2))

        self.assertRaises(TypeError, self.pathmodule.samestat)

    eleza _test_samestat_on_link_func(self, func):
        test_fn1 = support.TESTFN + "1"
        test_fn2 = support.TESTFN + "2"
        self.addCleanup(support.unlink, test_fn1)
        self.addCleanup(support.unlink, test_fn2)

        create_file(test_fn1)
        func(test_fn1, test_fn2)
        self.assertKweli(self.pathmodule.samestat(os.stat(test_fn1),
                                                 os.stat(test_fn2)))
        os.remove(test_fn2)

        create_file(test_fn2)
        self.assertUongo(self.pathmodule.samestat(os.stat(test_fn1),
                                                  os.stat(test_fn2)))

    @support.skip_unless_symlink
    eleza test_samestat_on_symlink(self):
        self._test_samestat_on_link_func(os.symlink)

    eleza test_samestat_on_link(self):
        jaribu:
            self._test_samestat_on_link_func(os.link)
        tatizo PermissionError kama e:
            self.skipTest('os.link(): %s' % e)

    eleza test_sameopenfile(self):
        filename = support.TESTFN
        self.addCleanup(support.unlink, filename)
        create_file(filename)

        ukijumuisha open(filename, "rb", 0) kama fp1:
            fd1 = fp1.fileno()
            ukijumuisha open(filename, "rb", 0) kama fp2:
                fd2 = fp2.fileno()
                self.assertKweli(self.pathmodule.sameopenfile(fd1, fd2))


kundi TestGenericTest(GenericTest, unittest.TestCase):
    # Issue 16852: GenericTest can't inherit kutoka unittest.TestCase
    # kila test discovery purposes; CommonTest inherits kutoka GenericTest
    # na ni only meant to be inherited by others.
    pathmodule = genericpath

    eleza test_invalid_paths(self):
        kila attr kwenye GenericTest.common_attributes:
            # os.path.commonprefix doesn't ashiria ValueError
            ikiwa attr == 'commonprefix':
                endelea
            func = getattr(self.pathmodule, attr)
            ukijumuisha self.subTest(attr=attr):
                ikiwa attr kwenye ('exists', 'isdir', 'isfile'):
                    func('/tmp\udfffabcds')
                    func(b'/tmp\xffabcds')
                    func('/tmp\x00abcds')
                    func(b'/tmp\x00abcds')
                isipokua:
                    ukijumuisha self.assertRaises((OSError, UnicodeEncodeError)):
                        func('/tmp\udfffabcds')
                    ukijumuisha self.assertRaises((OSError, UnicodeDecodeError)):
                        func(b'/tmp\xffabcds')
                    ukijumuisha self.assertRaisesRegex(ValueError, 'embedded null'):
                        func('/tmp\x00abcds')
                    ukijumuisha self.assertRaisesRegex(ValueError, 'embedded null'):
                        func(b'/tmp\x00abcds')

# Following TestCase ni sio supposed to be run kutoka test_genericpath.
# It ni inherited by other test modules (ntpath, posixpath).

kundi CommonTest(GenericTest):
    common_attributes = GenericTest.common_attributes + [
        # Properties
        'curdir', 'pardir', 'extsep', 'sep',
        'pathsep', 'defpath', 'altsep', 'devnull',
        # Methods
        'normcase', 'splitdrive', 'expandvars', 'normpath', 'abspath',
        'join', 'split', 'splitext', 'isabs', 'basename', 'dirname',
        'lexists', 'islink', 'ismount', 'expanduser', 'normpath', 'realpath',
    ]

    eleza test_normcase(self):
        normcase = self.pathmodule.normcase
        # check that normcase() ni idempotent
        kila p kwenye ["FoO/./BaR", b"FoO/./BaR"]:
            p = normcase(p)
            self.assertEqual(p, normcase(p))

        self.assertEqual(normcase(''), '')
        self.assertEqual(normcase(b''), b'')

        # check that normcase raises a TypeError kila invalid types
        kila path kwenye (Tupu, Kweli, 0, 2.5, [], bytearray(b''), {'o','o'}):
            self.assertRaises(TypeError, normcase, path)

    eleza test_splitdrive(self):
        # splitdrive kila non-NT paths
        splitdrive = self.pathmodule.splitdrive
        self.assertEqual(splitdrive("/foo/bar"), ("", "/foo/bar"))
        self.assertEqual(splitdrive("foo:bar"), ("", "foo:bar"))
        self.assertEqual(splitdrive(":foo:bar"), ("", ":foo:bar"))

        self.assertEqual(splitdrive(b"/foo/bar"), (b"", b"/foo/bar"))
        self.assertEqual(splitdrive(b"foo:bar"), (b"", b"foo:bar"))
        self.assertEqual(splitdrive(b":foo:bar"), (b"", b":foo:bar"))

    eleza test_expandvars(self):
        expandvars = self.pathmodule.expandvars
        ukijumuisha support.EnvironmentVarGuard() kama env:
            env.clear()
            env["foo"] = "bar"
            env["{foo"] = "baz1"
            env["{foo}"] = "baz2"
            self.assertEqual(expandvars("foo"), "foo")
            self.assertEqual(expandvars("$foo bar"), "bar bar")
            self.assertEqual(expandvars("${foo}bar"), "barbar")
            self.assertEqual(expandvars("$[foo]bar"), "$[foo]bar")
            self.assertEqual(expandvars("$bar bar"), "$bar bar")
            self.assertEqual(expandvars("$?bar"), "$?bar")
            self.assertEqual(expandvars("$foo}bar"), "bar}bar")
            self.assertEqual(expandvars("${foo"), "${foo")
            self.assertEqual(expandvars("${{foo}}"), "baz1}")
            self.assertEqual(expandvars("$foo$foo"), "barbar")
            self.assertEqual(expandvars("$bar$bar"), "$bar$bar")

            self.assertEqual(expandvars(b"foo"), b"foo")
            self.assertEqual(expandvars(b"$foo bar"), b"bar bar")
            self.assertEqual(expandvars(b"${foo}bar"), b"barbar")
            self.assertEqual(expandvars(b"$[foo]bar"), b"$[foo]bar")
            self.assertEqual(expandvars(b"$bar bar"), b"$bar bar")
            self.assertEqual(expandvars(b"$?bar"), b"$?bar")
            self.assertEqual(expandvars(b"$foo}bar"), b"bar}bar")
            self.assertEqual(expandvars(b"${foo"), b"${foo")
            self.assertEqual(expandvars(b"${{foo}}"), b"baz1}")
            self.assertEqual(expandvars(b"$foo$foo"), b"barbar")
            self.assertEqual(expandvars(b"$bar$bar"), b"$bar$bar")

    @unittest.skipUnless(support.FS_NONASCII, 'need support.FS_NONASCII')
    eleza test_expandvars_nonascii(self):
        expandvars = self.pathmodule.expandvars
        eleza check(value, expected):
            self.assertEqual(expandvars(value), expected)
        ukijumuisha support.EnvironmentVarGuard() kama env:
            env.clear()
            nonascii = support.FS_NONASCII
            env['spam'] = nonascii
            env[nonascii] = 'ham' + nonascii
            check(nonascii, nonascii)
            check('$spam bar', '%s bar' % nonascii)
            check('${spam}bar', '%sbar' % nonascii)
            check('${%s}bar' % nonascii, 'ham%sbar' % nonascii)
            check('$bar%s bar' % nonascii, '$bar%s bar' % nonascii)
            check('$spam}bar', '%s}bar' % nonascii)

            check(os.fsencode(nonascii), os.fsencode(nonascii))
            check(b'$spam bar', os.fsencode('%s bar' % nonascii))
            check(b'${spam}bar', os.fsencode('%sbar' % nonascii))
            check(os.fsencode('${%s}bar' % nonascii),
                  os.fsencode('ham%sbar' % nonascii))
            check(os.fsencode('$bar%s bar' % nonascii),
                  os.fsencode('$bar%s bar' % nonascii))
            check(b'$spam}bar', os.fsencode('%s}bar' % nonascii))

    eleza test_abspath(self):
        self.assertIn("foo", self.pathmodule.abspath("foo"))
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.assertIn(b"foo", self.pathmodule.abspath(b"foo"))

        # avoid UnicodeDecodeError on Windows
        undecodable_path = b'' ikiwa sys.platform == 'win32' isipokua b'f\xf2\xf2'

        # Abspath returns bytes when the arg ni bytes
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            kila path kwenye (b'', b'foo', undecodable_path, b'/foo', b'C:\\'):
                self.assertIsInstance(self.pathmodule.abspath(path), bytes)

    eleza test_realpath(self):
        self.assertIn("foo", self.pathmodule.realpath("foo"))
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.assertIn(b"foo", self.pathmodule.realpath(b"foo"))

    eleza test_normpath_issue5827(self):
        # Make sure normpath preserves unicode
        kila path kwenye ('', '.', '/', '\\', '///foo/.//bar//'):
            self.assertIsInstance(self.pathmodule.normpath(path), str)

    eleza test_abspath_issue3426(self):
        # Check that abspath returns unicode when the arg ni unicode
        # ukijumuisha both ASCII na non-ASCII cwds.
        abspath = self.pathmodule.abspath
        kila path kwenye ('', 'fuu', 'f\xf9\xf9', '/fuu', 'U:\\'):
            self.assertIsInstance(abspath(path), str)

        unicwd = '\xe7w\xf0'
        jaribu:
            os.fsencode(unicwd)
        tatizo (AttributeError, UnicodeEncodeError):
            # FS encoding ni probably ASCII
            pita
        isipokua:
            ukijumuisha support.temp_cwd(unicwd):
                kila path kwenye ('', 'fuu', 'f\xf9\xf9', '/fuu', 'U:\\'):
                    self.assertIsInstance(abspath(path), str)

    eleza test_nonascii_abspath(self):
        ikiwa (support.TESTFN_UNDECODABLE
        # Mac OS X denies the creation of a directory ukijumuisha an invalid
        # UTF-8 name. Windows allows creating a directory ukijumuisha an
        # arbitrary bytes name, but fails to enter this directory
        # (when the bytes name ni used).
        na sys.platform haiko kwenye ('win32', 'darwin')):
            name = support.TESTFN_UNDECODABLE
        lasivyo support.TESTFN_NONASCII:
            name = support.TESTFN_NONASCII
        isipokua:
            self.skipTest("need support.TESTFN_NONASCII")

        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            ukijumuisha support.temp_cwd(name):
                self.test_abspath()

    eleza test_join_errors(self):
        # Check join() raises friendly TypeErrors.
        ukijumuisha support.check_warnings(('', BytesWarning), quiet=Kweli):
            errmsg = "Can't mix strings na bytes kwenye path components"
            ukijumuisha self.assertRaisesRegex(TypeError, errmsg):
                self.pathmodule.join(b'bytes', 'str')
            ukijumuisha self.assertRaisesRegex(TypeError, errmsg):
                self.pathmodule.join('str', b'bytes')
            # regression, see #15377
            ukijumuisha self.assertRaisesRegex(TypeError, 'int'):
                self.pathmodule.join(42, 'str')
            ukijumuisha self.assertRaisesRegex(TypeError, 'int'):
                self.pathmodule.join('str', 42)
            ukijumuisha self.assertRaisesRegex(TypeError, 'int'):
                self.pathmodule.join(42)
            ukijumuisha self.assertRaisesRegex(TypeError, 'list'):
                self.pathmodule.join([])
            ukijumuisha self.assertRaisesRegex(TypeError, 'bytearray'):
                self.pathmodule.join(bytearray(b'foo'), bytearray(b'bar'))

    eleza test_relpath_errors(self):
        # Check relpath() raises friendly TypeErrors.
        ukijumuisha support.check_warnings(('', (BytesWarning, DeprecationWarning)),
                                    quiet=Kweli):
            errmsg = "Can't mix strings na bytes kwenye path components"
            ukijumuisha self.assertRaisesRegex(TypeError, errmsg):
                self.pathmodule.relpath(b'bytes', 'str')
            ukijumuisha self.assertRaisesRegex(TypeError, errmsg):
                self.pathmodule.relpath('str', b'bytes')
            ukijumuisha self.assertRaisesRegex(TypeError, 'int'):
                self.pathmodule.relpath(42, 'str')
            ukijumuisha self.assertRaisesRegex(TypeError, 'int'):
                self.pathmodule.relpath('str', 42)
            ukijumuisha self.assertRaisesRegex(TypeError, 'bytearray'):
                self.pathmodule.relpath(bytearray(b'foo'), bytearray(b'bar'))

    eleza test_import(self):
        assert_python_ok('-S', '-c', 'agiza ' + self.pathmodule.__name__)


kundi PathLikeTests(unittest.TestCase):

    eleza setUp(self):
        self.file_name = support.TESTFN.lower()
        self.file_path = FakePath(support.TESTFN)
        self.addCleanup(support.unlink, self.file_name)
        create_file(self.file_name, b"test_genericpath.PathLikeTests")

    eleza assertPathEqual(self, func):
        self.assertEqual(func(self.file_path), func(self.file_name))

    eleza test_path_exists(self):
        self.assertPathEqual(os.path.exists)

    eleza test_path_isfile(self):
        self.assertPathEqual(os.path.isfile)

    eleza test_path_isdir(self):
        self.assertPathEqual(os.path.isdir)

    eleza test_path_commonprefix(self):
        self.assertEqual(os.path.commonprefix([self.file_path, self.file_name]),
                         self.file_name)

    eleza test_path_getsize(self):
        self.assertPathEqual(os.path.getsize)

    eleza test_path_getmtime(self):
        self.assertPathEqual(os.path.getatime)

    eleza test_path_getctime(self):
        self.assertPathEqual(os.path.getctime)

    eleza test_path_samefile(self):
        self.assertKweli(os.path.samefile(self.file_path, self.file_name))


ikiwa __name__ == "__main__":
    unittest.main()
