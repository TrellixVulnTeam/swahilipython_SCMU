agiza ntpath
agiza os
agiza sys
agiza unittest
agiza warnings
kutoka test.support agiza TestFailed, FakePath
kutoka test agiza support, test_genericpath
kutoka tempfile agiza TemporaryFile


jaribu:
    agiza nt
tatizo ImportError:
    # Most tests can complete without the nt module,
    # but kila those that require it we agiza here.
    nt = Tupu

jaribu:
    ntpath._getfinalpathname
tatizo AttributeError:
    HAVE_GETFINALPATHNAME = Uongo
isipokua:
    HAVE_GETFINALPATHNAME = Kweli


eleza _norm(path):
    ikiwa isinstance(path, (bytes, str, os.PathLike)):
        rudisha ntpath.normcase(os.fsdecode(path))
    lasivyo hasattr(path, "__iter__"):
        rudisha tuple(ntpath.normcase(os.fsdecode(p)) kila p kwenye path)
    rudisha path


eleza tester(fn, wantResult):
    fn = fn.replace("\\", "\\\\")
    gotResult = eval(fn)
    ikiwa wantResult != gotResult na _norm(wantResult) != _norm(gotResult):
        ashiria TestFailed("%s should return: %s but returned: %s" \
              %(str(fn), str(wantResult), str(gotResult)))

    # then ukijumuisha bytes
    fn = fn.replace("('", "(b'")
    fn = fn.replace('("', '(b"')
    fn = fn.replace("['", "[b'")
    fn = fn.replace('["', '[b"')
    fn = fn.replace(", '", ", b'")
    fn = fn.replace(', "', ', b"')
    fn = os.fsencode(fn).decode('latin1')
    fn = fn.encode('ascii', 'backslashreplace').decode('ascii')
    ukijumuisha warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        gotResult = eval(fn)
    ikiwa _norm(wantResult) != _norm(gotResult):
        ashiria TestFailed("%s should return: %s but returned: %s" \
              %(str(fn), str(wantResult), repr(gotResult)))


kundi NtpathTestCase(unittest.TestCase):
    eleza assertPathEqual(self, path1, path2):
        ikiwa path1 == path2 ama _norm(path1) == _norm(path2):
            rudisha
        self.assertEqual(path1, path2)

    eleza assertPathIn(self, path, pathset):
        self.assertIn(_norm(path), _norm(pathset))


kundi TestNtpath(NtpathTestCase):
    eleza test_splitext(self):
        tester('ntpath.splitext("foo.ext")', ('foo', '.ext'))
        tester('ntpath.splitext("/foo/foo.ext")', ('/foo/foo', '.ext'))
        tester('ntpath.splitext(".ext")', ('.ext', ''))
        tester('ntpath.splitext("\\foo.ext\\foo")', ('\\foo.ext\\foo', ''))
        tester('ntpath.splitext("foo.ext\\")', ('foo.ext\\', ''))
        tester('ntpath.splitext("")', ('', ''))
        tester('ntpath.splitext("foo.bar.ext")', ('foo.bar', '.ext'))
        tester('ntpath.splitext("xx/foo.bar.ext")', ('xx/foo.bar', '.ext'))
        tester('ntpath.splitext("xx\\foo.bar.ext")', ('xx\\foo.bar', '.ext'))
        tester('ntpath.splitext("c:a/b\\c.d")', ('c:a/b\\c', '.d'))

    eleza test_splitdrive(self):
        tester('ntpath.splitdrive("c:\\foo\\bar")',
               ('c:', '\\foo\\bar'))
        tester('ntpath.splitdrive("c:/foo/bar")',
               ('c:', '/foo/bar'))
        tester('ntpath.splitdrive("\\\\conky\\mountpoint\\foo\\bar")',
               ('\\\\conky\\mountpoint', '\\foo\\bar'))
        tester('ntpath.splitdrive("//conky/mountpoint/foo/bar")',
               ('//conky/mountpoint', '/foo/bar'))
        tester('ntpath.splitdrive("\\\\\\conky\\mountpoint\\foo\\bar")',
            ('', '\\\\\\conky\\mountpoint\\foo\\bar'))
        tester('ntpath.splitdrive("///conky/mountpoint/foo/bar")',
            ('', '///conky/mountpoint/foo/bar'))
        tester('ntpath.splitdrive("\\\\conky\\\\mountpoint\\foo\\bar")',
               ('', '\\\\conky\\\\mountpoint\\foo\\bar'))
        tester('ntpath.splitdrive("//conky//mountpoint/foo/bar")',
               ('', '//conky//mountpoint/foo/bar'))
        # Issue #19911: UNC part containing U+0130
        self.assertEqual(ntpath.splitdrive('//conky/MOUNTPOİNT/foo/bar'),
                         ('//conky/MOUNTPOİNT', '/foo/bar'))

    eleza test_split(self):
        tester('ntpath.split("c:\\foo\\bar")', ('c:\\foo', 'bar'))
        tester('ntpath.split("\\\\conky\\mountpoint\\foo\\bar")',
               ('\\\\conky\\mountpoint\\foo', 'bar'))

        tester('ntpath.split("c:\\")', ('c:\\', ''))
        tester('ntpath.split("\\\\conky\\mountpoint\\")',
               ('\\\\conky\\mountpoint\\', ''))

        tester('ntpath.split("c:/")', ('c:/', ''))
        tester('ntpath.split("//conky/mountpoint/")', ('//conky/mountpoint/', ''))

    eleza test_isabs(self):
        tester('ntpath.isabs("c:\\")', 1)
        tester('ntpath.isabs("\\\\conky\\mountpoint\\")', 1)
        tester('ntpath.isabs("\\foo")', 1)
        tester('ntpath.isabs("\\foo\\bar")', 1)

    eleza test_commonprefix(self):
        tester('ntpath.commonprefix(["/home/swenson/spam", "/home/swen/spam"])',
               "/home/swen")
        tester('ntpath.commonprefix(["\\home\\swen\\spam", "\\home\\swen\\eggs"])',
               "\\home\\swen\\")
        tester('ntpath.commonprefix(["/home/swen/spam", "/home/swen/spam"])',
               "/home/swen/spam")

    eleza test_join(self):
        tester('ntpath.join("")', '')
        tester('ntpath.join("", "", "")', '')
        tester('ntpath.join("a")', 'a')
        tester('ntpath.join("/a")', '/a')
        tester('ntpath.join("\\a")', '\\a')
        tester('ntpath.join("a:")', 'a:')
        tester('ntpath.join("a:", "\\b")', 'a:\\b')
        tester('ntpath.join("a", "\\b")', '\\b')
        tester('ntpath.join("a", "b", "c")', 'a\\b\\c')
        tester('ntpath.join("a\\", "b", "c")', 'a\\b\\c')
        tester('ntpath.join("a", "b\\", "c")', 'a\\b\\c')
        tester('ntpath.join("a", "b", "\\c")', '\\c')
        tester('ntpath.join("d:\\", "\\pleep")', 'd:\\pleep')
        tester('ntpath.join("d:\\", "a", "b")', 'd:\\a\\b')

        tester("ntpath.join('', 'a')", 'a')
        tester("ntpath.join('', '', '', '', 'a')", 'a')
        tester("ntpath.join('a', '')", 'a\\')
        tester("ntpath.join('a', '', '', '', '')", 'a\\')
        tester("ntpath.join('a\\', '')", 'a\\')
        tester("ntpath.join('a\\', '', '', '', '')", 'a\\')
        tester("ntpath.join('a/', '')", 'a/')

        tester("ntpath.join('a/b', 'x/y')", 'a/b\\x/y')
        tester("ntpath.join('/a/b', 'x/y')", '/a/b\\x/y')
        tester("ntpath.join('/a/b/', 'x/y')", '/a/b/x/y')
        tester("ntpath.join('c:', 'x/y')", 'c:x/y')
        tester("ntpath.join('c:a/b', 'x/y')", 'c:a/b\\x/y')
        tester("ntpath.join('c:a/b/', 'x/y')", 'c:a/b/x/y')
        tester("ntpath.join('c:/', 'x/y')", 'c:/x/y')
        tester("ntpath.join('c:/a/b', 'x/y')", 'c:/a/b\\x/y')
        tester("ntpath.join('c:/a/b/', 'x/y')", 'c:/a/b/x/y')
        tester("ntpath.join('//computer/share', 'x/y')", '//computer/share\\x/y')
        tester("ntpath.join('//computer/share/', 'x/y')", '//computer/share/x/y')
        tester("ntpath.join('//computer/share/a/b', 'x/y')", '//computer/share/a/b\\x/y')

        tester("ntpath.join('a/b', '/x/y')", '/x/y')
        tester("ntpath.join('/a/b', '/x/y')", '/x/y')
        tester("ntpath.join('c:', '/x/y')", 'c:/x/y')
        tester("ntpath.join('c:a/b', '/x/y')", 'c:/x/y')
        tester("ntpath.join('c:/', '/x/y')", 'c:/x/y')
        tester("ntpath.join('c:/a/b', '/x/y')", 'c:/x/y')
        tester("ntpath.join('//computer/share', '/x/y')", '//computer/share/x/y')
        tester("ntpath.join('//computer/share/', '/x/y')", '//computer/share/x/y')
        tester("ntpath.join('//computer/share/a', '/x/y')", '//computer/share/x/y')

        tester("ntpath.join('c:', 'C:x/y')", 'C:x/y')
        tester("ntpath.join('c:a/b', 'C:x/y')", 'C:a/b\\x/y')
        tester("ntpath.join('c:/', 'C:x/y')", 'C:/x/y')
        tester("ntpath.join('c:/a/b', 'C:x/y')", 'C:/a/b\\x/y')

        kila x kwenye ('', 'a/b', '/a/b', 'c:', 'c:a/b', 'c:/', 'c:/a/b',
                  '//computer/share', '//computer/share/', '//computer/share/a/b'):
            kila y kwenye ('d:', 'd:x/y', 'd:/', 'd:/x/y',
                      '//machine/common', '//machine/common/', '//machine/common/x/y'):
                tester("ntpath.join(%r, %r)" % (x, y), y)

        tester("ntpath.join('\\\\computer\\share\\', 'a', 'b')", '\\\\computer\\share\\a\\b')
        tester("ntpath.join('\\\\computer\\share', 'a', 'b')", '\\\\computer\\share\\a\\b')
        tester("ntpath.join('\\\\computer\\share', 'a\\b')", '\\\\computer\\share\\a\\b')
        tester("ntpath.join('//computer/share/', 'a', 'b')", '//computer/share/a\\b')
        tester("ntpath.join('//computer/share', 'a', 'b')", '//computer/share\\a\\b')
        tester("ntpath.join('//computer/share', 'a/b')", '//computer/share\\a/b')

    eleza test_normpath(self):
        tester("ntpath.normpath('A//////././//.//B')", r'A\B')
        tester("ntpath.normpath('A/./B')", r'A\B')
        tester("ntpath.normpath('A/foo/../B')", r'A\B')
        tester("ntpath.normpath('C:A//B')", r'C:A\B')
        tester("ntpath.normpath('D:A/./B')", r'D:A\B')
        tester("ntpath.normpath('e:A/foo/../B')", r'e:A\B')

        tester("ntpath.normpath('C:///A//B')", r'C:\A\B')
        tester("ntpath.normpath('D:///A/./B')", r'D:\A\B')
        tester("ntpath.normpath('e:///A/foo/../B')", r'e:\A\B')

        tester("ntpath.normpath('..')", r'..')
        tester("ntpath.normpath('.')", r'.')
        tester("ntpath.normpath('')", r'.')
        tester("ntpath.normpath('/')", '\\')
        tester("ntpath.normpath('c:/')", 'c:\\')
        tester("ntpath.normpath('/../.././..')", '\\')
        tester("ntpath.normpath('c:/../../..')", 'c:\\')
        tester("ntpath.normpath('../.././..')", r'..\..\..')
        tester("ntpath.normpath('K:../.././..')", r'K:..\..\..')
        tester("ntpath.normpath('C:////a/b')", r'C:\a\b')
        tester("ntpath.normpath('//machine/share//a/b')", r'\\machine\share\a\b')

        tester("ntpath.normpath('\\\\.\\NUL')", r'\\.\NUL')
        tester("ntpath.normpath('\\\\?\\D:/XY\\Z')", r'\\?\D:/XY\Z')

    eleza test_realpath_curdir(self):
        expected = ntpath.normpath(os.getcwd())
        tester("ntpath.realpath('.')", expected)
        tester("ntpath.realpath('./.')", expected)
        tester("ntpath.realpath('/'.join(['.'] * 100))", expected)
        tester("ntpath.realpath('.\\.')", expected)
        tester("ntpath.realpath('\\'.join(['.'] * 100))", expected)

    eleza test_realpath_pardir(self):
        expected = ntpath.normpath(os.getcwd())
        tester("ntpath.realpath('..')", ntpath.dirname(expected))
        tester("ntpath.realpath('../..')",
               ntpath.dirname(ntpath.dirname(expected)))
        tester("ntpath.realpath('/'.join(['..'] * 50))",
               ntpath.splitdrive(expected)[0] + '\\')
        tester("ntpath.realpath('..\\..')",
               ntpath.dirname(ntpath.dirname(expected)))
        tester("ntpath.realpath('\\'.join(['..'] * 50))",
               ntpath.splitdrive(expected)[0] + '\\')

    @support.skip_unless_symlink
    @unittest.skipUnless(HAVE_GETFINALPATHNAME, 'need _getfinalpathname')
    eleza test_realpath_basic(self):
        ABSTFN = ntpath.abspath(support.TESTFN)
        open(ABSTFN, "wb").close()
        self.addCleanup(support.unlink, ABSTFN)
        self.addCleanup(support.unlink, ABSTFN + "1")

        os.symlink(ABSTFN, ABSTFN + "1")
        self.assertPathEqual(ntpath.realpath(ABSTFN + "1"), ABSTFN)
        self.assertPathEqual(ntpath.realpath(os.fsencode(ABSTFN + "1")),
                         os.fsencode(ABSTFN))

    @support.skip_unless_symlink
    @unittest.skipUnless(HAVE_GETFINALPATHNAME, 'need _getfinalpathname')
    eleza test_realpath_relative(self):
        ABSTFN = ntpath.abspath(support.TESTFN)
        open(ABSTFN, "wb").close()
        self.addCleanup(support.unlink, ABSTFN)
        self.addCleanup(support.unlink, ABSTFN + "1")

        os.symlink(ABSTFN, ntpath.relpath(ABSTFN + "1"))
        self.assertPathEqual(ntpath.realpath(ABSTFN + "1"), ABSTFN)

    @support.skip_unless_symlink
    @unittest.skipUnless(HAVE_GETFINALPATHNAME, 'need _getfinalpathname')
    eleza test_realpath_broken_symlinks(self):
        ABSTFN = ntpath.abspath(support.TESTFN)
        os.mkdir(ABSTFN)
        self.addCleanup(support.rmtree, ABSTFN)

        ukijumuisha support.change_cwd(ABSTFN):
            os.mkdir("subdir")
            os.chdir("subdir")
            os.symlink(".", "recursive")
            os.symlink("..", "parent")
            os.chdir("..")
            os.symlink(".", "self")
            os.symlink("missing", "broken")
            os.symlink(r"broken\bar", "broken1")
            os.symlink(r"self\self\broken", "broken2")
            os.symlink(r"subdir\parent\subdir\parent\broken", "broken3")
            os.symlink(ABSTFN + r"\broken", "broken4")
            os.symlink(r"recursive\..\broken", "broken5")

            self.assertPathEqual(ntpath.realpath("broken"),
                                 ABSTFN + r"\missing")
            self.assertPathEqual(ntpath.realpath(r"broken\foo"),
                                 ABSTFN + r"\missing\foo")
            self.assertPathEqual(ntpath.realpath(r"broken1"),
                                 ABSTFN + r"\missing\bar")
            self.assertPathEqual(ntpath.realpath(r"broken1\baz"),
                                 ABSTFN + r"\missing\bar\baz")
            self.assertPathEqual(ntpath.realpath("broken2"),
                                 ABSTFN + r"\missing")
            self.assertPathEqual(ntpath.realpath("broken3"),
                                 ABSTFN + r"\missing")
            self.assertPathEqual(ntpath.realpath("broken4"),
                                 ABSTFN + r"\missing")
            self.assertPathEqual(ntpath.realpath("broken5"),
                                 ABSTFN + r"\missing")

            self.assertPathEqual(ntpath.realpath(b"broken"),
                                 os.fsencode(ABSTFN + r"\missing"))
            self.assertPathEqual(ntpath.realpath(rb"broken\foo"),
                                 os.fsencode(ABSTFN + r"\missing\foo"))
            self.assertPathEqual(ntpath.realpath(rb"broken1"),
                                 os.fsencode(ABSTFN + r"\missing\bar"))
            self.assertPathEqual(ntpath.realpath(rb"broken1\baz"),
                                 os.fsencode(ABSTFN + r"\missing\bar\baz"))
            self.assertPathEqual(ntpath.realpath(b"broken2"),
                                 os.fsencode(ABSTFN + r"\missing"))
            self.assertPathEqual(ntpath.realpath(rb"broken3"),
                                 os.fsencode(ABSTFN + r"\missing"))
            self.assertPathEqual(ntpath.realpath(b"broken4"),
                                 os.fsencode(ABSTFN + r"\missing"))
            self.assertPathEqual(ntpath.realpath(b"broken5"),
                                 os.fsencode(ABSTFN + r"\missing"))

    @support.skip_unless_symlink
    @unittest.skipUnless(HAVE_GETFINALPATHNAME, 'need _getfinalpathname')
    eleza test_realpath_symlink_loops(self):
        # Bug #930024, rudisha the path unchanged ikiwa we get into an infinite
        # symlink loop.
        ABSTFN = ntpath.abspath(support.TESTFN)
        self.addCleanup(support.unlink, ABSTFN)
        self.addCleanup(support.unlink, ABSTFN + "1")
        self.addCleanup(support.unlink, ABSTFN + "2")
        self.addCleanup(support.unlink, ABSTFN + "y")
        self.addCleanup(support.unlink, ABSTFN + "c")
        self.addCleanup(support.unlink, ABSTFN + "a")

        os.symlink(ABSTFN, ABSTFN)
        self.assertPathEqual(ntpath.realpath(ABSTFN), ABSTFN)

        # cycles are non-deterministic kama to which path ni returned, but
        # it will always be the fully resolved path of one member of the cycle
        os.symlink(ABSTFN + "1", ABSTFN + "2")
        os.symlink(ABSTFN + "2", ABSTFN + "1")
        expected = (ABSTFN + "1", ABSTFN + "2")
        self.assertPathIn(ntpath.realpath(ABSTFN + "1"), expected)
        self.assertPathIn(ntpath.realpath(ABSTFN + "2"), expected)

        self.assertPathIn(ntpath.realpath(ABSTFN + "1\\x"),
                          (ntpath.join(r, "x") kila r kwenye expected))
        self.assertPathEqual(ntpath.realpath(ABSTFN + "1\\.."),
                             ntpath.dirname(ABSTFN))
        self.assertPathEqual(ntpath.realpath(ABSTFN + "1\\..\\x"),
                             ntpath.dirname(ABSTFN) + "\\x")
        os.symlink(ABSTFN + "x", ABSTFN + "y")
        self.assertPathEqual(ntpath.realpath(ABSTFN + "1\\..\\"
                                             + ntpath.basename(ABSTFN) + "y"),
                             ABSTFN + "x")
        self.assertPathIn(ntpath.realpath(ABSTFN + "1\\..\\"
                                          + ntpath.basename(ABSTFN) + "1"),
                          expected)

        os.symlink(ntpath.basename(ABSTFN) + "a\\b", ABSTFN + "a")
        self.assertPathEqual(ntpath.realpath(ABSTFN + "a"), ABSTFN + "a")

        os.symlink("..\\" + ntpath.basename(ntpath.dirname(ABSTFN))
                   + "\\" + ntpath.basename(ABSTFN) + "c", ABSTFN + "c")
        self.assertPathEqual(ntpath.realpath(ABSTFN + "c"), ABSTFN + "c")

        # Test using relative path kama well.
        self.assertPathEqual(ntpath.realpath(ntpath.basename(ABSTFN)), ABSTFN)

    @support.skip_unless_symlink
    @unittest.skipUnless(HAVE_GETFINALPATHNAME, 'need _getfinalpathname')
    eleza test_realpath_symlink_prefix(self):
        ABSTFN = ntpath.abspath(support.TESTFN)
        self.addCleanup(support.unlink, ABSTFN + "3")
        self.addCleanup(support.unlink, "\\\\?\\" + ABSTFN + "3.")
        self.addCleanup(support.unlink, ABSTFN + "3link")
        self.addCleanup(support.unlink, ABSTFN + "3.link")

        ukijumuisha open(ABSTFN + "3", "wb") kama f:
            f.write(b'0')
        os.symlink(ABSTFN + "3", ABSTFN + "3link")

        ukijumuisha open("\\\\?\\" + ABSTFN + "3.", "wb") kama f:
            f.write(b'1')
        os.symlink("\\\\?\\" + ABSTFN + "3.", ABSTFN + "3.link")

        self.assertPathEqual(ntpath.realpath(ABSTFN + "3link"),
                             ABSTFN + "3")
        self.assertPathEqual(ntpath.realpath(ABSTFN + "3.link"),
                             "\\\\?\\" + ABSTFN + "3.")

        # Resolved paths should be usable to open target files
        ukijumuisha open(ntpath.realpath(ABSTFN + "3link"), "rb") kama f:
            self.assertEqual(f.read(), b'0')
        ukijumuisha open(ntpath.realpath(ABSTFN + "3.link"), "rb") kama f:
            self.assertEqual(f.read(), b'1')

        # When the prefix ni included, it ni sio stripped
        self.assertPathEqual(ntpath.realpath("\\\\?\\" + ABSTFN + "3link"),
                             "\\\\?\\" + ABSTFN + "3")
        self.assertPathEqual(ntpath.realpath("\\\\?\\" + ABSTFN + "3.link"),
                             "\\\\?\\" + ABSTFN + "3.")

    @unittest.skipUnless(HAVE_GETFINALPATHNAME, 'need _getfinalpathname')
    eleza test_realpath_nul(self):
        tester("ntpath.realpath('NUL')", r'\\.\NUL')

    eleza test_expandvars(self):
        ukijumuisha support.EnvironmentVarGuard() kama env:
            env.clear()
            env["foo"] = "bar"
            env["{foo"] = "baz1"
            env["{foo}"] = "baz2"
            tester('ntpath.expandvars("foo")', "foo")
            tester('ntpath.expandvars("$foo bar")', "bar bar")
            tester('ntpath.expandvars("${foo}bar")', "barbar")
            tester('ntpath.expandvars("$[foo]bar")', "$[foo]bar")
            tester('ntpath.expandvars("$bar bar")', "$bar bar")
            tester('ntpath.expandvars("$?bar")', "$?bar")
            tester('ntpath.expandvars("$foo}bar")', "bar}bar")
            tester('ntpath.expandvars("${foo")', "${foo")
            tester('ntpath.expandvars("${{foo}}")', "baz1}")
            tester('ntpath.expandvars("$foo$foo")', "barbar")
            tester('ntpath.expandvars("$bar$bar")', "$bar$bar")
            tester('ntpath.expandvars("%foo% bar")', "bar bar")
            tester('ntpath.expandvars("%foo%bar")', "barbar")
            tester('ntpath.expandvars("%foo%%foo%")', "barbar")
            tester('ntpath.expandvars("%%foo%%foo%foo%")', "%foo%foobar")
            tester('ntpath.expandvars("%?bar%")', "%?bar%")
            tester('ntpath.expandvars("%foo%%bar")', "bar%bar")
            tester('ntpath.expandvars("\'%foo%\'%bar")', "\'%foo%\'%bar")
            tester('ntpath.expandvars("bar\'%foo%")', "bar\'%foo%")

    @unittest.skipUnless(support.FS_NONASCII, 'need support.FS_NONASCII')
    eleza test_expandvars_nonascii(self):
        eleza check(value, expected):
            tester('ntpath.expandvars(%r)' % value, expected)
        ukijumuisha support.EnvironmentVarGuard() kama env:
            env.clear()
            nonascii = support.FS_NONASCII
            env['spam'] = nonascii
            env[nonascii] = 'ham' + nonascii
            check('$spam bar', '%s bar' % nonascii)
            check('$%s bar' % nonascii, '$%s bar' % nonascii)
            check('${spam}bar', '%sbar' % nonascii)
            check('${%s}bar' % nonascii, 'ham%sbar' % nonascii)
            check('$spam}bar', '%s}bar' % nonascii)
            check('$%s}bar' % nonascii, '$%s}bar' % nonascii)
            check('%spam% bar', '%s bar' % nonascii)
            check('%{}% bar'.format(nonascii), 'ham%s bar' % nonascii)
            check('%spam%bar', '%sbar' % nonascii)
            check('%{}%bar'.format(nonascii), 'ham%sbar' % nonascii)

    eleza test_expanduser(self):
        tester('ntpath.expanduser("test")', 'test')

        ukijumuisha support.EnvironmentVarGuard() kama env:
            env.clear()
            tester('ntpath.expanduser("~test")', '~test')

            env['HOMEPATH'] = 'eric\\idle'
            env['HOMEDRIVE'] = 'C:\\'
            tester('ntpath.expanduser("~test")', 'C:\\eric\\test')
            tester('ntpath.expanduser("~")', 'C:\\eric\\idle')

            toa env['HOMEDRIVE']
            tester('ntpath.expanduser("~test")', 'eric\\test')
            tester('ntpath.expanduser("~")', 'eric\\idle')

            env.clear()
            env['USERPROFILE'] = 'C:\\eric\\idle'
            tester('ntpath.expanduser("~test")', 'C:\\eric\\test')
            tester('ntpath.expanduser("~")', 'C:\\eric\\idle')
            tester('ntpath.expanduser("~test\\foo\\bar")',
                   'C:\\eric\\test\\foo\\bar')
            tester('ntpath.expanduser("~test/foo/bar")',
                   'C:\\eric\\test/foo/bar')
            tester('ntpath.expanduser("~\\foo\\bar")',
                   'C:\\eric\\idle\\foo\\bar')
            tester('ntpath.expanduser("~/foo/bar")',
                   'C:\\eric\\idle/foo/bar')

            # bpo-36264: ignore `HOME` when set on windows
            env.clear()
            env['HOME'] = 'F:\\'
            env['USERPROFILE'] = 'C:\\eric\\idle'
            tester('ntpath.expanduser("~test")', 'C:\\eric\\test')
            tester('ntpath.expanduser("~")', 'C:\\eric\\idle')

    @unittest.skipUnless(nt, "abspath requires 'nt' module")
    eleza test_abspath(self):
        tester('ntpath.abspath("C:\\")', "C:\\")
        ukijumuisha support.temp_cwd(support.TESTFN) kama cwd_dir: # bpo-31047
            tester('ntpath.abspath("")', cwd_dir)
            tester('ntpath.abspath(" ")', cwd_dir + "\\ ")
            tester('ntpath.abspath("?")', cwd_dir + "\\?")
            drive, _ = ntpath.splitdrive(cwd_dir)
            tester('ntpath.abspath("/abc/")', drive + "\\abc")

    eleza test_relpath(self):
        tester('ntpath.relpath("a")', 'a')
        tester('ntpath.relpath(ntpath.abspath("a"))', 'a')
        tester('ntpath.relpath("a/b")', 'a\\b')
        tester('ntpath.relpath("../a/b")', '..\\a\\b')
        ukijumuisha support.temp_cwd(support.TESTFN) kama cwd_dir:
            currentdir = ntpath.basename(cwd_dir)
            tester('ntpath.relpath("a", "../b")', '..\\'+currentdir+'\\a')
            tester('ntpath.relpath("a/b", "../c")', '..\\'+currentdir+'\\a\\b')
        tester('ntpath.relpath("a", "b/c")', '..\\..\\a')
        tester('ntpath.relpath("c:/foo/bar/bat", "c:/x/y")', '..\\..\\foo\\bar\\bat')
        tester('ntpath.relpath("//conky/mountpoint/a", "//conky/mountpoint/b/c")', '..\\..\\a')
        tester('ntpath.relpath("a", "a")', '.')
        tester('ntpath.relpath("/foo/bar/bat", "/x/y/z")', '..\\..\\..\\foo\\bar\\bat')
        tester('ntpath.relpath("/foo/bar/bat", "/foo/bar")', 'bat')
        tester('ntpath.relpath("/foo/bar/bat", "/")', 'foo\\bar\\bat')
        tester('ntpath.relpath("/", "/foo/bar/bat")', '..\\..\\..')
        tester('ntpath.relpath("/foo/bar/bat", "/x")', '..\\foo\\bar\\bat')
        tester('ntpath.relpath("/x", "/foo/bar/bat")', '..\\..\\..\\x')
        tester('ntpath.relpath("/", "/")', '.')
        tester('ntpath.relpath("/a", "/a")', '.')
        tester('ntpath.relpath("/a/b", "/a/b")', '.')
        tester('ntpath.relpath("c:/foo", "C:/FOO")', '.')

    eleza test_commonpath(self):
        eleza check(paths, expected):
            tester(('ntpath.commonpath(%r)' % paths).replace('\\\\', '\\'),
                   expected)
        eleza check_error(exc, paths):
            self.assertRaises(exc, ntpath.commonpath, paths)
            self.assertRaises(exc, ntpath.commonpath,
                              [os.fsencode(p) kila p kwenye paths])

        self.assertRaises(ValueError, ntpath.commonpath, [])
        check_error(ValueError, ['C:\\Program Files', 'Program Files'])
        check_error(ValueError, ['C:\\Program Files', 'C:Program Files'])
        check_error(ValueError, ['\\Program Files', 'Program Files'])
        check_error(ValueError, ['Program Files', 'C:\\Program Files'])
        check(['C:\\Program Files'], 'C:\\Program Files')
        check(['C:\\Program Files', 'C:\\Program Files'], 'C:\\Program Files')
        check(['C:\\Program Files\\', 'C:\\Program Files'],
              'C:\\Program Files')
        check(['C:\\Program Files\\', 'C:\\Program Files\\'],
              'C:\\Program Files')
        check(['C:\\\\Program Files', 'C:\\Program Files\\\\'],
              'C:\\Program Files')
        check(['C:\\.\\Program Files', 'C:\\Program Files\\.'],
              'C:\\Program Files')
        check(['C:\\', 'C:\\bin'], 'C:\\')
        check(['C:\\Program Files', 'C:\\bin'], 'C:\\')
        check(['C:\\Program Files', 'C:\\Program Files\\Bar'],
              'C:\\Program Files')
        check(['C:\\Program Files\\Foo', 'C:\\Program Files\\Bar'],
              'C:\\Program Files')
        check(['C:\\Program Files', 'C:\\Projects'], 'C:\\')
        check(['C:\\Program Files\\', 'C:\\Projects'], 'C:\\')

        check(['C:\\Program Files\\Foo', 'C:/Program Files/Bar'],
              'C:\\Program Files')
        check(['C:\\Program Files\\Foo', 'c:/program files/bar'],
              'C:\\Program Files')
        check(['c:/program files/bar', 'C:\\Program Files\\Foo'],
              'c:\\program files')

        check_error(ValueError, ['C:\\Program Files', 'D:\\Program Files'])

        check(['spam'], 'spam')
        check(['spam', 'spam'], 'spam')
        check(['spam', 'alot'], '')
        check(['and\\jam', 'and\\spam'], 'and')
        check(['and\\\\jam', 'and\\spam\\\\'], 'and')
        check(['and\\.\\jam', '.\\and\\spam'], 'and')
        check(['and\\jam', 'and\\spam', 'alot'], '')
        check(['and\\jam', 'and\\spam', 'and'], 'and')
        check(['C:and\\jam', 'C:and\\spam'], 'C:and')

        check([''], '')
        check(['', 'spam\\alot'], '')
        check_error(ValueError, ['', '\\spam\\alot'])

        self.assertRaises(TypeError, ntpath.commonpath,
                          [b'C:\\Program Files', 'C:\\Program Files\\Foo'])
        self.assertRaises(TypeError, ntpath.commonpath,
                          [b'C:\\Program Files', 'Program Files\\Foo'])
        self.assertRaises(TypeError, ntpath.commonpath,
                          [b'Program Files', 'C:\\Program Files\\Foo'])
        self.assertRaises(TypeError, ntpath.commonpath,
                          ['C:\\Program Files', b'C:\\Program Files\\Foo'])
        self.assertRaises(TypeError, ntpath.commonpath,
                          ['C:\\Program Files', b'Program Files\\Foo'])
        self.assertRaises(TypeError, ntpath.commonpath,
                          ['Program Files', b'C:\\Program Files\\Foo'])

    eleza test_sameopenfile(self):
        ukijumuisha TemporaryFile() kama tf1, TemporaryFile() kama tf2:
            # Make sure the same file ni really the same
            self.assertKweli(ntpath.sameopenfile(tf1.fileno(), tf1.fileno()))
            # Make sure different files are really different
            self.assertUongo(ntpath.sameopenfile(tf1.fileno(), tf2.fileno()))
            # Make sure invalid values don't cause issues on win32
            ikiwa sys.platform == "win32":
                ukijumuisha self.assertRaises(OSError):
                    # Invalid file descriptors shouldn't display assert
                    # dialogs (#4804)
                    ntpath.sameopenfile(-1, -1)

    eleza test_ismount(self):
        self.assertKweli(ntpath.ismount("c:\\"))
        self.assertKweli(ntpath.ismount("C:\\"))
        self.assertKweli(ntpath.ismount("c:/"))
        self.assertKweli(ntpath.ismount("C:/"))
        self.assertKweli(ntpath.ismount("\\\\.\\c:\\"))
        self.assertKweli(ntpath.ismount("\\\\.\\C:\\"))

        self.assertKweli(ntpath.ismount(b"c:\\"))
        self.assertKweli(ntpath.ismount(b"C:\\"))
        self.assertKweli(ntpath.ismount(b"c:/"))
        self.assertKweli(ntpath.ismount(b"C:/"))
        self.assertKweli(ntpath.ismount(b"\\\\.\\c:\\"))
        self.assertKweli(ntpath.ismount(b"\\\\.\\C:\\"))

        ukijumuisha support.temp_dir() kama d:
            self.assertUongo(ntpath.ismount(d))

        ikiwa sys.platform == "win32":
            #
            # Make sure the current folder isn't the root folder
            # (or any other volume root). The drive-relative
            # locations below cannot then refer to mount points
            #
            drive, path = ntpath.splitdrive(sys.executable)
            ukijumuisha support.change_cwd(ntpath.dirname(sys.executable)):
                self.assertUongo(ntpath.ismount(drive.lower()))
                self.assertUongo(ntpath.ismount(drive.upper()))

            self.assertKweli(ntpath.ismount("\\\\localhost\\c$"))
            self.assertKweli(ntpath.ismount("\\\\localhost\\c$\\"))

            self.assertKweli(ntpath.ismount(b"\\\\localhost\\c$"))
            self.assertKweli(ntpath.ismount(b"\\\\localhost\\c$\\"))

    eleza assertEqualCI(self, s1, s2):
        """Assert that two strings are equal ignoring case differences."""
        self.assertEqual(s1.lower(), s2.lower())

    @unittest.skipUnless(nt, "OS helpers require 'nt' module")
    eleza test_nt_helpers(self):
        # Trivial validation that the helpers do sio koma, na support both
        # unicode na bytes (UTF-8) paths

        executable = nt._getfinalpathname(sys.executable)

        kila path kwenye executable, os.fsencode(executable):
            volume_path = nt._getvolumepathname(path)
            path_drive = ntpath.splitdrive(path)[0]
            volume_path_drive = ntpath.splitdrive(volume_path)[0]
            self.assertEqualCI(path_drive, volume_path_drive)

        cap, free = nt._getdiskusage(sys.exec_prefix)
        self.assertGreater(cap, 0)
        self.assertGreater(free, 0)
        b_cap, b_free = nt._getdiskusage(sys.exec_prefix.encode())
        # Free space may change, so only test the capacity ni equal
        self.assertEqual(b_cap, cap)
        self.assertGreater(b_free, 0)

        kila path kwenye [sys.prefix, sys.executable]:
            final_path = nt._getfinalpathname(path)
            self.assertIsInstance(final_path, str)
            self.assertGreater(len(final_path), 0)

            b_final_path = nt._getfinalpathname(path.encode())
            self.assertIsInstance(b_final_path, bytes)
            self.assertGreater(len(b_final_path), 0)

kundi NtCommonTest(test_genericpath.CommonTest, unittest.TestCase):
    pathmodule = ntpath
    attributes = ['relpath']


kundi PathLikeTests(NtpathTestCase):

    path = ntpath

    eleza setUp(self):
        self.file_name = support.TESTFN.lower()
        self.file_path = FakePath(support.TESTFN)
        self.addCleanup(support.unlink, self.file_name)
        ukijumuisha open(self.file_name, 'xb', 0) kama file:
            file.write(b"test_ntpath.PathLikeTests")

    eleza _check_function(self, func):
        self.assertPathEqual(func(self.file_path), func(self.file_name))

    eleza test_path_normcase(self):
        self._check_function(self.path.normcase)

    eleza test_path_isabs(self):
        self._check_function(self.path.isabs)

    eleza test_path_join(self):
        self.assertEqual(self.path.join('a', FakePath('b'), 'c'),
                         self.path.join('a', 'b', 'c'))

    eleza test_path_split(self):
        self._check_function(self.path.split)

    eleza test_path_splitext(self):
        self._check_function(self.path.splitext)

    eleza test_path_splitdrive(self):
        self._check_function(self.path.splitdrive)

    eleza test_path_basename(self):
        self._check_function(self.path.basename)

    eleza test_path_dirname(self):
        self._check_function(self.path.dirname)

    eleza test_path_islink(self):
        self._check_function(self.path.islink)

    eleza test_path_lexists(self):
        self._check_function(self.path.lexists)

    eleza test_path_ismount(self):
        self._check_function(self.path.ismount)

    eleza test_path_expanduser(self):
        self._check_function(self.path.expanduser)

    eleza test_path_expandvars(self):
        self._check_function(self.path.expandvars)

    eleza test_path_normpath(self):
        self._check_function(self.path.normpath)

    eleza test_path_abspath(self):
        self._check_function(self.path.abspath)

    eleza test_path_realpath(self):
        self._check_function(self.path.realpath)

    eleza test_path_relpath(self):
        self._check_function(self.path.relpath)

    eleza test_path_commonpath(self):
        common_path = self.path.commonpath([self.file_path, self.file_name])
        self.assertPathEqual(common_path, self.file_name)

    eleza test_path_isdir(self):
        self._check_function(self.path.isdir)


ikiwa __name__ == "__main__":
    unittest.main()
