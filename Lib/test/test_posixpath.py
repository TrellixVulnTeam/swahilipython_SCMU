agiza os
agiza posixpath
agiza unittest
kutoka posixpath agiza realpath, abspath, dirname, basename
kutoka test agiza support, test_genericpath
kutoka test.support agiza FakePath
kutoka unittest agiza mock

jaribu:
    agiza posix
tatizo ImportError:
    posix = Tupu


# An absolute path to a temporary filename kila testing. We can't rely on TESTFN
# being an absolute path, so we need this.

ABSTFN = abspath(support.TESTFN)

eleza skip_if_ABSTFN_contains_backslash(test):
    """
    On Windows, posixpath.abspath still rudishas paths with backslashes
    instead of posix forward slashes. If this ni the case, several tests
    fail, so skip them.
    """
    found_backslash = '\\' kwenye ABSTFN
    msg = "ABSTFN ni sio a posix path - tests fail"
    rudisha [test, unittest.skip(msg)(test)][found_backslash]

eleza safe_rmdir(dirname):
    jaribu:
        os.rmdir(dirname)
    tatizo OSError:
        pita

kundi PosixPathTest(unittest.TestCase):

    eleza setUp(self):
        self.tearDown()

    eleza tearDown(self):
        kila suffix kwenye ["", "1", "2"]:
            support.unlink(support.TESTFN + suffix)
            safe_rmdir(support.TESTFN + suffix)

    eleza test_join(self):
        self.assertEqual(posixpath.join("/foo", "bar", "/bar", "baz"),
                         "/bar/baz")
        self.assertEqual(posixpath.join("/foo", "bar", "baz"), "/foo/bar/baz")
        self.assertEqual(posixpath.join("/foo/", "bar/", "baz/"),
                         "/foo/bar/baz/")

        self.assertEqual(posixpath.join(b"/foo", b"bar", b"/bar", b"baz"),
                         b"/bar/baz")
        self.assertEqual(posixpath.join(b"/foo", b"bar", b"baz"),
                         b"/foo/bar/baz")
        self.assertEqual(posixpath.join(b"/foo/", b"bar/", b"baz/"),
                         b"/foo/bar/baz/")

    eleza test_split(self):
        self.assertEqual(posixpath.split("/foo/bar"), ("/foo", "bar"))
        self.assertEqual(posixpath.split("/"), ("/", ""))
        self.assertEqual(posixpath.split("foo"), ("", "foo"))
        self.assertEqual(posixpath.split("////foo"), ("////", "foo"))
        self.assertEqual(posixpath.split("//foo//bar"), ("//foo", "bar"))

        self.assertEqual(posixpath.split(b"/foo/bar"), (b"/foo", b"bar"))
        self.assertEqual(posixpath.split(b"/"), (b"/", b""))
        self.assertEqual(posixpath.split(b"foo"), (b"", b"foo"))
        self.assertEqual(posixpath.split(b"////foo"), (b"////", b"foo"))
        self.assertEqual(posixpath.split(b"//foo//bar"), (b"//foo", b"bar"))

    eleza splitextTest(self, path, filename, ext):
        self.assertEqual(posixpath.splitext(path), (filename, ext))
        self.assertEqual(posixpath.splitext("/" + path), ("/" + filename, ext))
        self.assertEqual(posixpath.splitext("abc/" + path),
                         ("abc/" + filename, ext))
        self.assertEqual(posixpath.splitext("abc.def/" + path),
                         ("abc.def/" + filename, ext))
        self.assertEqual(posixpath.splitext("/abc.def/" + path),
                         ("/abc.def/" + filename, ext))
        self.assertEqual(posixpath.splitext(path + "/"),
                         (filename + ext + "/", ""))

        path = bytes(path, "ASCII")
        filename = bytes(filename, "ASCII")
        ext = bytes(ext, "ASCII")

        self.assertEqual(posixpath.splitext(path), (filename, ext))
        self.assertEqual(posixpath.splitext(b"/" + path),
                         (b"/" + filename, ext))
        self.assertEqual(posixpath.splitext(b"abc/" + path),
                         (b"abc/" + filename, ext))
        self.assertEqual(posixpath.splitext(b"abc.def/" + path),
                         (b"abc.def/" + filename, ext))
        self.assertEqual(posixpath.splitext(b"/abc.def/" + path),
                         (b"/abc.def/" + filename, ext))
        self.assertEqual(posixpath.splitext(path + b"/"),
                         (filename + ext + b"/", b""))

    eleza test_splitext(self):
        self.splitextTest("foo.bar", "foo", ".bar")
        self.splitextTest("foo.boo.bar", "foo.boo", ".bar")
        self.splitextTest("foo.boo.biff.bar", "foo.boo.biff", ".bar")
        self.splitextTest(".csh.rc", ".csh", ".rc")
        self.splitextTest("nodots", "nodots", "")
        self.splitextTest(".cshrc", ".cshrc", "")
        self.splitextTest("...manydots", "...manydots", "")
        self.splitextTest("...manydots.ext", "...manydots", ".ext")
        self.splitextTest(".", ".", "")
        self.splitextTest("..", "..", "")
        self.splitextTest("........", "........", "")
        self.splitextTest("", "", "")

    eleza test_isabs(self):
        self.assertIs(posixpath.isabs(""), Uongo)
        self.assertIs(posixpath.isabs("/"), Kweli)
        self.assertIs(posixpath.isabs("/foo"), Kweli)
        self.assertIs(posixpath.isabs("/foo/bar"), Kweli)
        self.assertIs(posixpath.isabs("foo/bar"), Uongo)

        self.assertIs(posixpath.isabs(b""), Uongo)
        self.assertIs(posixpath.isabs(b"/"), Kweli)
        self.assertIs(posixpath.isabs(b"/foo"), Kweli)
        self.assertIs(posixpath.isabs(b"/foo/bar"), Kweli)
        self.assertIs(posixpath.isabs(b"foo/bar"), Uongo)

    eleza test_basename(self):
        self.assertEqual(posixpath.basename("/foo/bar"), "bar")
        self.assertEqual(posixpath.basename("/"), "")
        self.assertEqual(posixpath.basename("foo"), "foo")
        self.assertEqual(posixpath.basename("////foo"), "foo")
        self.assertEqual(posixpath.basename("//foo//bar"), "bar")

        self.assertEqual(posixpath.basename(b"/foo/bar"), b"bar")
        self.assertEqual(posixpath.basename(b"/"), b"")
        self.assertEqual(posixpath.basename(b"foo"), b"foo")
        self.assertEqual(posixpath.basename(b"////foo"), b"foo")
        self.assertEqual(posixpath.basename(b"//foo//bar"), b"bar")

    eleza test_dirname(self):
        self.assertEqual(posixpath.dirname("/foo/bar"), "/foo")
        self.assertEqual(posixpath.dirname("/"), "/")
        self.assertEqual(posixpath.dirname("foo"), "")
        self.assertEqual(posixpath.dirname("////foo"), "////")
        self.assertEqual(posixpath.dirname("//foo//bar"), "//foo")

        self.assertEqual(posixpath.dirname(b"/foo/bar"), b"/foo")
        self.assertEqual(posixpath.dirname(b"/"), b"/")
        self.assertEqual(posixpath.dirname(b"foo"), b"")
        self.assertEqual(posixpath.dirname(b"////foo"), b"////")
        self.assertEqual(posixpath.dirname(b"//foo//bar"), b"//foo")

    eleza test_islink(self):
        self.assertIs(posixpath.islink(support.TESTFN + "1"), Uongo)
        self.assertIs(posixpath.lexists(support.TESTFN + "2"), Uongo)

        with open(support.TESTFN + "1", "wb") kama f:
            f.write(b"foo")
        self.assertIs(posixpath.islink(support.TESTFN + "1"), Uongo)

        ikiwa support.can_symlink():
            os.symlink(support.TESTFN + "1", support.TESTFN + "2")
            self.assertIs(posixpath.islink(support.TESTFN + "2"), Kweli)
            os.remove(support.TESTFN + "1")
            self.assertIs(posixpath.islink(support.TESTFN + "2"), Kweli)
            self.assertIs(posixpath.exists(support.TESTFN + "2"), Uongo)
            self.assertIs(posixpath.lexists(support.TESTFN + "2"), Kweli)

        self.assertIs(posixpath.islink(support.TESTFN + "\udfff"), Uongo)
        self.assertIs(posixpath.islink(os.fsencode(support.TESTFN) + b"\xff"), Uongo)
        self.assertIs(posixpath.islink(support.TESTFN + "\x00"), Uongo)
        self.assertIs(posixpath.islink(os.fsencode(support.TESTFN) + b"\x00"), Uongo)

    eleza test_ismount(self):
        self.assertIs(posixpath.ismount("/"), Kweli)
        self.assertIs(posixpath.ismount(b"/"), Kweli)

    eleza test_ismount_non_existent(self):
        # Non-existent mountpoint.
        self.assertIs(posixpath.ismount(ABSTFN), Uongo)
        jaribu:
            os.mkdir(ABSTFN)
            self.assertIs(posixpath.ismount(ABSTFN), Uongo)
        mwishowe:
            safe_rmdir(ABSTFN)

        self.assertIs(posixpath.ismount('/\udfff'), Uongo)
        self.assertIs(posixpath.ismount(b'/\xff'), Uongo)
        self.assertIs(posixpath.ismount('/\x00'), Uongo)
        self.assertIs(posixpath.ismount(b'/\x00'), Uongo)

    @unittest.skipUnless(support.can_symlink(),
                         "Test requires symlink support")
    eleza test_ismount_symlinks(self):
        # Symlinks are never mountpoints.
        jaribu:
            os.symlink("/", ABSTFN)
            self.assertIs(posixpath.ismount(ABSTFN), Uongo)
        mwishowe:
            os.unlink(ABSTFN)

    @unittest.skipIf(posix ni Tupu, "Test requires posix module")
    eleza test_ismount_different_device(self):
        # Simulate the path being on a different device kutoka its parent by
        # mocking out st_dev.
        save_lstat = os.lstat
        eleza fake_lstat(path):
            st_ino = 0
            st_dev = 0
            ikiwa path == ABSTFN:
                st_dev = 1
                st_ino = 1
            rudisha posix.stat_result((0, st_ino, st_dev, 0, 0, 0, 0, 0, 0, 0))
        jaribu:
            os.lstat = fake_lstat
            self.assertIs(posixpath.ismount(ABSTFN), Kweli)
        mwishowe:
            os.lstat = save_lstat

    @unittest.skipIf(posix ni Tupu, "Test requires posix module")
    eleza test_ismount_directory_not_readable(self):
        # issue #2466: Simulate ismount run on a directory that ni not
        # readable, which used to rudisha Uongo.
        save_lstat = os.lstat
        eleza fake_lstat(path):
            st_ino = 0
            st_dev = 0
            ikiwa path.startswith(ABSTFN) na path != ABSTFN:
                # ismount tries to read something inside the ABSTFN directory;
                # simulate this being forbidden (no read permission).
                ashiria OSError("Fake [Errno 13] Permission denied")
            ikiwa path == ABSTFN:
                st_dev = 1
                st_ino = 1
            rudisha posix.stat_result((0, st_ino, st_dev, 0, 0, 0, 0, 0, 0, 0))
        jaribu:
            os.lstat = fake_lstat
            self.assertIs(posixpath.ismount(ABSTFN), Kweli)
        mwishowe:
            os.lstat = save_lstat

    eleza test_expanduser(self):
        self.assertEqual(posixpath.expanduser("foo"), "foo")
        self.assertEqual(posixpath.expanduser(b"foo"), b"foo")

    eleza test_expanduser_home_envvar(self):
        with support.EnvironmentVarGuard() kama env:
            env['HOME'] = '/home/victor'
            self.assertEqual(posixpath.expanduser("~"), "/home/victor")

            # expanduser() strips trailing slash
            env['HOME'] = '/home/victor/'
            self.assertEqual(posixpath.expanduser("~"), "/home/victor")

            kila home kwenye '/', '', '//', '///':
                with self.subTest(home=home):
                    env['HOME'] = home
                    self.assertEqual(posixpath.expanduser("~"), "/")
                    self.assertEqual(posixpath.expanduser("~/"), "/")
                    self.assertEqual(posixpath.expanduser("~/foo"), "/foo")

    eleza test_expanduser_pwd(self):
        pwd = support.import_module('pwd')

        self.assertIsInstance(posixpath.expanduser("~/"), str)
        self.assertIsInstance(posixpath.expanduser(b"~/"), bytes)

        # ikiwa home directory == root directory, this test makes no sense
        ikiwa posixpath.expanduser("~") != '/':
            self.assertEqual(
                posixpath.expanduser("~") + "/",
                posixpath.expanduser("~/")
            )
            self.assertEqual(
                posixpath.expanduser(b"~") + b"/",
                posixpath.expanduser(b"~/")
            )
        self.assertIsInstance(posixpath.expanduser("~root/"), str)
        self.assertIsInstance(posixpath.expanduser("~foo/"), str)
        self.assertIsInstance(posixpath.expanduser(b"~root/"), bytes)
        self.assertIsInstance(posixpath.expanduser(b"~foo/"), bytes)

        with support.EnvironmentVarGuard() kama env:
            # expanduser should fall back to using the pitaword database
            toa env['HOME']

            home = pwd.getpwuid(os.getuid()).pw_dir
            # $HOME can end with a trailing /, so strip it (see #17809)
            home = home.rstrip("/") ama '/'
            self.assertEqual(posixpath.expanduser("~"), home)

            # bpo-10496: If the HOME environment variable ni sio set na the
            # user (current identifier ama name kwenye the path) doesn't exist in
            # the pitaword database (pwd.getuid() ama pwd.getpwnam() fail),
            # expanduser() must rudisha the path unchanged.
            with mock.patch.object(pwd, 'getpwuid', side_effect=KeyError), \
                 mock.patch.object(pwd, 'getpwnam', side_effect=KeyError):
                kila path kwenye ('~', '~/.local', '~vstinner/'):
                    self.assertEqual(posixpath.expanduser(path), path)

    eleza test_normpath(self):
        self.assertEqual(posixpath.normpath(""), ".")
        self.assertEqual(posixpath.normpath("/"), "/")
        self.assertEqual(posixpath.normpath("//"), "//")
        self.assertEqual(posixpath.normpath("///"), "/")
        self.assertEqual(posixpath.normpath("///foo/.//bar//"), "/foo/bar")
        self.assertEqual(posixpath.normpath("///foo/.//bar//.//..//.//baz"),
                         "/foo/baz")
        self.assertEqual(posixpath.normpath("///..//./foo/.//bar"), "/foo/bar")

        self.assertEqual(posixpath.normpath(b""), b".")
        self.assertEqual(posixpath.normpath(b"/"), b"/")
        self.assertEqual(posixpath.normpath(b"//"), b"//")
        self.assertEqual(posixpath.normpath(b"///"), b"/")
        self.assertEqual(posixpath.normpath(b"///foo/.//bar//"), b"/foo/bar")
        self.assertEqual(posixpath.normpath(b"///foo/.//bar//.//..//.//baz"),
                         b"/foo/baz")
        self.assertEqual(posixpath.normpath(b"///..//./foo/.//bar"),
                         b"/foo/bar")

    @skip_if_ABSTFN_contains_backslash
    eleza test_realpath_curdir(self):
        self.assertEqual(realpath('.'), os.getcwd())
        self.assertEqual(realpath('./.'), os.getcwd())
        self.assertEqual(realpath('/'.join(['.'] * 100)), os.getcwd())

        self.assertEqual(realpath(b'.'), os.getcwdb())
        self.assertEqual(realpath(b'./.'), os.getcwdb())
        self.assertEqual(realpath(b'/'.join([b'.'] * 100)), os.getcwdb())

    @skip_if_ABSTFN_contains_backslash
    eleza test_realpath_pardir(self):
        self.assertEqual(realpath('..'), dirname(os.getcwd()))
        self.assertEqual(realpath('../..'), dirname(dirname(os.getcwd())))
        self.assertEqual(realpath('/'.join(['..'] * 100)), '/')

        self.assertEqual(realpath(b'..'), dirname(os.getcwdb()))
        self.assertEqual(realpath(b'../..'), dirname(dirname(os.getcwdb())))
        self.assertEqual(realpath(b'/'.join([b'..'] * 100)), b'/')

    @unittest.skipUnless(hasattr(os, "symlink"),
                         "Missing symlink implementation")
    @skip_if_ABSTFN_contains_backslash
    eleza test_realpath_basic(self):
        # Basic operation.
        jaribu:
            os.symlink(ABSTFN+"1", ABSTFN)
            self.assertEqual(realpath(ABSTFN), ABSTFN+"1")
        mwishowe:
            support.unlink(ABSTFN)

    @unittest.skipUnless(hasattr(os, "symlink"),
                         "Missing symlink implementation")
    @skip_if_ABSTFN_contains_backslash
    eleza test_realpath_relative(self):
        jaribu:
            os.symlink(posixpath.relpath(ABSTFN+"1"), ABSTFN)
            self.assertEqual(realpath(ABSTFN), ABSTFN+"1")
        mwishowe:
            support.unlink(ABSTFN)

    @unittest.skipUnless(hasattr(os, "symlink"),
                         "Missing symlink implementation")
    @skip_if_ABSTFN_contains_backslash
    eleza test_realpath_symlink_loops(self):
        # Bug #930024, rudisha the path unchanged ikiwa we get into an infinite
        # symlink loop.
        jaribu:
            os.symlink(ABSTFN, ABSTFN)
            self.assertEqual(realpath(ABSTFN), ABSTFN)

            os.symlink(ABSTFN+"1", ABSTFN+"2")
            os.symlink(ABSTFN+"2", ABSTFN+"1")
            self.assertEqual(realpath(ABSTFN+"1"), ABSTFN+"1")
            self.assertEqual(realpath(ABSTFN+"2"), ABSTFN+"2")

            self.assertEqual(realpath(ABSTFN+"1/x"), ABSTFN+"1/x")
            self.assertEqual(realpath(ABSTFN+"1/.."), dirname(ABSTFN))
            self.assertEqual(realpath(ABSTFN+"1/../x"), dirname(ABSTFN) + "/x")
            os.symlink(ABSTFN+"x", ABSTFN+"y")
            self.assertEqual(realpath(ABSTFN+"1/../" + basename(ABSTFN) + "y"),
                             ABSTFN + "y")
            self.assertEqual(realpath(ABSTFN+"1/../" + basename(ABSTFN) + "1"),
                             ABSTFN + "1")

            os.symlink(basename(ABSTFN) + "a/b", ABSTFN+"a")
            self.assertEqual(realpath(ABSTFN+"a"), ABSTFN+"a/b")

            os.symlink("../" + basename(dirname(ABSTFN)) + "/" +
                       basename(ABSTFN) + "c", ABSTFN+"c")
            self.assertEqual(realpath(ABSTFN+"c"), ABSTFN+"c")

            # Test using relative path kama well.
            with support.change_cwd(dirname(ABSTFN)):
                self.assertEqual(realpath(basename(ABSTFN)), ABSTFN)
        mwishowe:
            support.unlink(ABSTFN)
            support.unlink(ABSTFN+"1")
            support.unlink(ABSTFN+"2")
            support.unlink(ABSTFN+"y")
            support.unlink(ABSTFN+"c")
            support.unlink(ABSTFN+"a")

    @unittest.skipUnless(hasattr(os, "symlink"),
                         "Missing symlink implementation")
    @skip_if_ABSTFN_contains_backslash
    eleza test_realpath_repeated_indirect_symlinks(self):
        # Issue #6975.
        jaribu:
            os.mkdir(ABSTFN)
            os.symlink('../' + basename(ABSTFN), ABSTFN + '/self')
            os.symlink('self/self/self', ABSTFN + '/link')
            self.assertEqual(realpath(ABSTFN + '/link'), ABSTFN)
        mwishowe:
            support.unlink(ABSTFN + '/self')
            support.unlink(ABSTFN + '/link')
            safe_rmdir(ABSTFN)

    @unittest.skipUnless(hasattr(os, "symlink"),
                         "Missing symlink implementation")
    @skip_if_ABSTFN_contains_backslash
    eleza test_realpath_deep_recursion(self):
        depth = 10
        jaribu:
            os.mkdir(ABSTFN)
            kila i kwenye range(depth):
                os.symlink('/'.join(['%d' % i] * 10), ABSTFN + '/%d' % (i + 1))
            os.symlink('.', ABSTFN + '/0')
            self.assertEqual(realpath(ABSTFN + '/%d' % depth), ABSTFN)

            # Test using relative path kama well.
            with support.change_cwd(ABSTFN):
                self.assertEqual(realpath('%d' % depth), ABSTFN)
        mwishowe:
            kila i kwenye range(depth + 1):
                support.unlink(ABSTFN + '/%d' % i)
            safe_rmdir(ABSTFN)

    @unittest.skipUnless(hasattr(os, "symlink"),
                         "Missing symlink implementation")
    @skip_if_ABSTFN_contains_backslash
    eleza test_realpath_resolve_parents(self):
        # We also need to resolve any symlinks kwenye the parents of a relative
        # path pitaed to realpath. E.g.: current working directory is
        # /usr/doc with 'doc' being a symlink to /usr/share/doc. We call
        # realpath("a"). This should rudisha /usr/share/doc/a/.
        jaribu:
            os.mkdir(ABSTFN)
            os.mkdir(ABSTFN + "/y")
            os.symlink(ABSTFN + "/y", ABSTFN + "/k")

            with support.change_cwd(ABSTFN + "/k"):
                self.assertEqual(realpath("a"), ABSTFN + "/y/a")
        mwishowe:
            support.unlink(ABSTFN + "/k")
            safe_rmdir(ABSTFN + "/y")
            safe_rmdir(ABSTFN)

    @unittest.skipUnless(hasattr(os, "symlink"),
                         "Missing symlink implementation")
    @skip_if_ABSTFN_contains_backslash
    eleza test_realpath_resolve_before_normalizing(self):
        # Bug #990669: Symbolic links should be resolved before we
        # normalize the path. E.g.: ikiwa we have directories 'a', 'k' na 'y'
        # kwenye the following hierarchy:
        # a/k/y
        #
        # na a symbolic link 'link-y' pointing to 'y' kwenye directory 'a',
        # then realpath("link-y/..") should rudisha 'k', sio 'a'.
        jaribu:
            os.mkdir(ABSTFN)
            os.mkdir(ABSTFN + "/k")
            os.mkdir(ABSTFN + "/k/y")
            os.symlink(ABSTFN + "/k/y", ABSTFN + "/link-y")

            # Absolute path.
            self.assertEqual(realpath(ABSTFN + "/link-y/.."), ABSTFN + "/k")
            # Relative path.
            with support.change_cwd(dirname(ABSTFN)):
                self.assertEqual(realpath(basename(ABSTFN) + "/link-y/.."),
                                 ABSTFN + "/k")
        mwishowe:
            support.unlink(ABSTFN + "/link-y")
            safe_rmdir(ABSTFN + "/k/y")
            safe_rmdir(ABSTFN + "/k")
            safe_rmdir(ABSTFN)

    @unittest.skipUnless(hasattr(os, "symlink"),
                         "Missing symlink implementation")
    @skip_if_ABSTFN_contains_backslash
    eleza test_realpath_resolve_first(self):
        # Bug #1213894: The first component of the path, ikiwa sio absolute,
        # must be resolved too.

        jaribu:
            os.mkdir(ABSTFN)
            os.mkdir(ABSTFN + "/k")
            os.symlink(ABSTFN, ABSTFN + "link")
            with support.change_cwd(dirname(ABSTFN)):
                base = basename(ABSTFN)
                self.assertEqual(realpath(base + "link"), ABSTFN)
                self.assertEqual(realpath(base + "link/k"), ABSTFN + "/k")
        mwishowe:
            support.unlink(ABSTFN + "link")
            safe_rmdir(ABSTFN + "/k")
            safe_rmdir(ABSTFN)

    eleza test_relpath(self):
        (real_getcwd, os.getcwd) = (os.getcwd, lambda: r"/home/user/bar")
        jaribu:
            curdir = os.path.split(os.getcwd())[-1]
            self.assertRaises(ValueError, posixpath.relpath, "")
            self.assertEqual(posixpath.relpath("a"), "a")
            self.assertEqual(posixpath.relpath(posixpath.abspath("a")), "a")
            self.assertEqual(posixpath.relpath("a/b"), "a/b")
            self.assertEqual(posixpath.relpath("../a/b"), "../a/b")
            self.assertEqual(posixpath.relpath("a", "../b"), "../"+curdir+"/a")
            self.assertEqual(posixpath.relpath("a/b", "../c"),
                             "../"+curdir+"/a/b")
            self.assertEqual(posixpath.relpath("a", "b/c"), "../../a")
            self.assertEqual(posixpath.relpath("a", "a"), ".")
            self.assertEqual(posixpath.relpath("/foo/bar/bat", "/x/y/z"), '../../../foo/bar/bat')
            self.assertEqual(posixpath.relpath("/foo/bar/bat", "/foo/bar"), 'bat')
            self.assertEqual(posixpath.relpath("/foo/bar/bat", "/"), 'foo/bar/bat')
            self.assertEqual(posixpath.relpath("/", "/foo/bar/bat"), '../../..')
            self.assertEqual(posixpath.relpath("/foo/bar/bat", "/x"), '../foo/bar/bat')
            self.assertEqual(posixpath.relpath("/x", "/foo/bar/bat"), '../../../x')
            self.assertEqual(posixpath.relpath("/", "/"), '.')
            self.assertEqual(posixpath.relpath("/a", "/a"), '.')
            self.assertEqual(posixpath.relpath("/a/b", "/a/b"), '.')
        mwishowe:
            os.getcwd = real_getcwd

    eleza test_relpath_bytes(self):
        (real_getcwdb, os.getcwdb) = (os.getcwdb, lambda: br"/home/user/bar")
        jaribu:
            curdir = os.path.split(os.getcwdb())[-1]
            self.assertRaises(ValueError, posixpath.relpath, b"")
            self.assertEqual(posixpath.relpath(b"a"), b"a")
            self.assertEqual(posixpath.relpath(posixpath.abspath(b"a")), b"a")
            self.assertEqual(posixpath.relpath(b"a/b"), b"a/b")
            self.assertEqual(posixpath.relpath(b"../a/b"), b"../a/b")
            self.assertEqual(posixpath.relpath(b"a", b"../b"),
                             b"../"+curdir+b"/a")
            self.assertEqual(posixpath.relpath(b"a/b", b"../c"),
                             b"../"+curdir+b"/a/b")
            self.assertEqual(posixpath.relpath(b"a", b"b/c"), b"../../a")
            self.assertEqual(posixpath.relpath(b"a", b"a"), b".")
            self.assertEqual(posixpath.relpath(b"/foo/bar/bat", b"/x/y/z"), b'../../../foo/bar/bat')
            self.assertEqual(posixpath.relpath(b"/foo/bar/bat", b"/foo/bar"), b'bat')
            self.assertEqual(posixpath.relpath(b"/foo/bar/bat", b"/"), b'foo/bar/bat')
            self.assertEqual(posixpath.relpath(b"/", b"/foo/bar/bat"), b'../../..')
            self.assertEqual(posixpath.relpath(b"/foo/bar/bat", b"/x"), b'../foo/bar/bat')
            self.assertEqual(posixpath.relpath(b"/x", b"/foo/bar/bat"), b'../../../x')
            self.assertEqual(posixpath.relpath(b"/", b"/"), b'.')
            self.assertEqual(posixpath.relpath(b"/a", b"/a"), b'.')
            self.assertEqual(posixpath.relpath(b"/a/b", b"/a/b"), b'.')

            self.assertRaises(TypeError, posixpath.relpath, b"bytes", "str")
            self.assertRaises(TypeError, posixpath.relpath, "str", b"bytes")
        mwishowe:
            os.getcwdb = real_getcwdb

    eleza test_commonpath(self):
        eleza check(paths, expected):
            self.assertEqual(posixpath.commonpath(paths), expected)
            self.assertEqual(posixpath.commonpath([os.fsencode(p) kila p kwenye paths]),
                             os.fsencode(expected))
        eleza check_error(exc, paths):
            self.assertRaises(exc, posixpath.commonpath, paths)
            self.assertRaises(exc, posixpath.commonpath,
                              [os.fsencode(p) kila p kwenye paths])

        self.assertRaises(ValueError, posixpath.commonpath, [])
        check_error(ValueError, ['/usr', 'usr'])
        check_error(ValueError, ['usr', '/usr'])

        check(['/usr/local'], '/usr/local')
        check(['/usr/local', '/usr/local'], '/usr/local')
        check(['/usr/local/', '/usr/local'], '/usr/local')
        check(['/usr/local/', '/usr/local/'], '/usr/local')
        check(['/usr//local', '//usr/local'], '/usr/local')
        check(['/usr/./local', '/./usr/local'], '/usr/local')
        check(['/', '/dev'], '/')
        check(['/usr', '/dev'], '/')
        check(['/usr/lib/', '/usr/lib/python3'], '/usr/lib')
        check(['/usr/lib/', '/usr/lib64/'], '/usr')

        check(['/usr/lib', '/usr/lib64'], '/usr')
        check(['/usr/lib/', '/usr/lib64'], '/usr')

        check(['spam'], 'spam')
        check(['spam', 'spam'], 'spam')
        check(['spam', 'alot'], '')
        check(['and/jam', 'and/spam'], 'and')
        check(['and//jam', 'and/spam//'], 'and')
        check(['and/./jam', './and/spam'], 'and')
        check(['and/jam', 'and/spam', 'alot'], '')
        check(['and/jam', 'and/spam', 'and'], 'and')

        check([''], '')
        check(['', 'spam/alot'], '')
        check_error(ValueError, ['', '/spam/alot'])

        self.assertRaises(TypeError, posixpath.commonpath,
                          [b'/usr/lib/', '/usr/lib/python3'])
        self.assertRaises(TypeError, posixpath.commonpath,
                          [b'/usr/lib/', 'usr/lib/python3'])
        self.assertRaises(TypeError, posixpath.commonpath,
                          [b'usr/lib/', '/usr/lib/python3'])
        self.assertRaises(TypeError, posixpath.commonpath,
                          ['/usr/lib/', b'/usr/lib/python3'])
        self.assertRaises(TypeError, posixpath.commonpath,
                          ['/usr/lib/', b'usr/lib/python3'])
        self.assertRaises(TypeError, posixpath.commonpath,
                          ['usr/lib/', b'/usr/lib/python3'])


kundi PosixCommonTest(test_genericpath.CommonTest, unittest.TestCase):
    pathmodule = posixpath
    attributes = ['relpath', 'samefile', 'sameopenfile', 'samestat']


kundi PathLikeTests(unittest.TestCase):

    path = posixpath

    eleza setUp(self):
        self.file_name = support.TESTFN.lower()
        self.file_path = FakePath(support.TESTFN)
        self.addCleanup(support.unlink, self.file_name)
        with open(self.file_name, 'xb', 0) kama file:
            file.write(b"test_posixpath.PathLikeTests")

    eleza assertPathEqual(self, func):
        self.assertEqual(func(self.file_path), func(self.file_name))

    eleza test_path_normcase(self):
        self.assertPathEqual(self.path.normcase)

    eleza test_path_isabs(self):
        self.assertPathEqual(self.path.isabs)

    eleza test_path_join(self):
        self.assertEqual(self.path.join('a', FakePath('b'), 'c'),
                         self.path.join('a', 'b', 'c'))

    eleza test_path_split(self):
        self.assertPathEqual(self.path.split)

    eleza test_path_splitext(self):
        self.assertPathEqual(self.path.splitext)

    eleza test_path_splitdrive(self):
        self.assertPathEqual(self.path.splitdrive)

    eleza test_path_basename(self):
        self.assertPathEqual(self.path.basename)

    eleza test_path_dirname(self):
        self.assertPathEqual(self.path.dirname)

    eleza test_path_islink(self):
        self.assertPathEqual(self.path.islink)

    eleza test_path_lexists(self):
        self.assertPathEqual(self.path.lexists)

    eleza test_path_ismount(self):
        self.assertPathEqual(self.path.ismount)

    eleza test_path_expanduser(self):
        self.assertPathEqual(self.path.expanduser)

    eleza test_path_expandvars(self):
        self.assertPathEqual(self.path.expandvars)

    eleza test_path_normpath(self):
        self.assertPathEqual(self.path.normpath)

    eleza test_path_abspath(self):
        self.assertPathEqual(self.path.abspath)

    eleza test_path_realpath(self):
        self.assertPathEqual(self.path.realpath)

    eleza test_path_relpath(self):
        self.assertPathEqual(self.path.relpath)

    eleza test_path_commonpath(self):
        common_path = self.path.commonpath([self.file_path, self.file_name])
        self.assertEqual(common_path, self.file_name)


ikiwa __name__=="__main__":
    unittest.main()
