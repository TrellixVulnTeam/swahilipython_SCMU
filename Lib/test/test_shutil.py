# Copyright (C) 2003 Python Software Foundation

agiza unittest
agiza unittest.mock
agiza shutil
agiza tempfile
agiza sys
agiza stat
agiza os
agiza os.path
agiza errno
agiza functools
agiza pathlib
agiza subprocess
agiza random
agiza string
agiza contextlib
agiza io
kutoka shutil agiza (make_archive,
                    register_archive_format, unregister_archive_format,
                    get_archive_formats, Error, unpack_archive,
                    register_unpack_format, RegistryError,
                    unregister_unpack_format, get_unpack_formats,
                    SameFileError, _GiveupOnFastCopy)
agiza tarfile
agiza zipfile
jaribu:
    agiza posix
tatizo ImportError:
    posix = Tupu

kutoka test agiza support
kutoka test.support agiza TESTFN, FakePath

TESTFN2 = TESTFN + "2"
MACOS = sys.platform.startswith("darwin")
AIX = sys.platform[:3] == 'aix'
jaribu:
    agiza grp
    agiza pwd
    UID_GID_SUPPORT = Kweli
tatizo ImportError:
    UID_GID_SUPPORT = Uongo

jaribu:
    agiza _winapi
tatizo ImportError:
    _winapi = Tupu

eleza _fake_rename(*args, **kwargs):
    # Pretend the destination path ni on a different filesystem.
    ashiria OSError(getattr(errno, 'EXDEV', 18), "Invalid cross-device link")

eleza mock_rename(func):
    @functools.wraps(func)
    eleza wrap(*args, **kwargs):
        jaribu:
            builtin_rename = os.rename
            os.rename = _fake_rename
            rudisha func(*args, **kwargs)
        mwishowe:
            os.rename = builtin_rename
    rudisha wrap

eleza write_file(path, content, binary=Uongo):
    """Write *content* to a file located at *path*.

    If *path* ni a tuple instead of a string, os.path.join will be used to
    make a path.  If *binary* ni true, the file will be opened kwenye binary
    mode.
    """
    ikiwa isinstance(path, tuple):
        path = os.path.join(*path)
    ukijumuisha open(path, 'wb' ikiwa binary isipokua 'w') kama fp:
        fp.write(content)

eleza write_test_file(path, size):
    """Create a test file ukijumuisha an arbitrary size na random text content."""
    eleza chunks(total, step):
        assert total >= step
        wakati total > step:
            tuma step
            total -= step
        ikiwa total:
            tuma total

    bufsize = min(size, 8192)
    chunk = b"".join([random.choice(string.ascii_letters).encode()
                      kila i kwenye range(bufsize)])
    ukijumuisha open(path, 'wb') kama f:
        kila csize kwenye chunks(size, bufsize):
            f.write(chunk)
    assert os.path.getsize(path) == size

eleza read_file(path, binary=Uongo):
    """Return contents kutoka a file located at *path*.

    If *path* ni a tuple instead of a string, os.path.join will be used to
    make a path.  If *binary* ni true, the file will be opened kwenye binary
    mode.
    """
    ikiwa isinstance(path, tuple):
        path = os.path.join(*path)
    ukijumuisha open(path, 'rb' ikiwa binary isipokua 'r') kama fp:
        rudisha fp.read()

eleza rlistdir(path):
    res = []
    kila name kwenye sorted(os.listdir(path)):
        p = os.path.join(path, name)
        ikiwa os.path.isdir(p) na sio os.path.islink(p):
            res.append(name + '/')
            kila n kwenye rlistdir(p):
                res.append(name + '/' + n)
        isipokua:
            res.append(name)
    rudisha res

eleza supports_file2file_sendfile():
    # ...apparently Linux na Solaris are the only ones
    ikiwa sio hasattr(os, "sendfile"):
        rudisha Uongo
    srcname = Tupu
    dstname = Tupu
    jaribu:
        ukijumuisha tempfile.NamedTemporaryFile("wb", delete=Uongo) kama f:
            srcname = f.name
            f.write(b"0123456789")

        ukijumuisha open(srcname, "rb") kama src:
            ukijumuisha tempfile.NamedTemporaryFile("wb", delete=Uongo) kama dst:
                dstname = dst.name
                infd = src.fileno()
                outfd = dst.fileno()
                jaribu:
                    os.sendfile(outfd, infd, 0, 2)
                tatizo OSError:
                    rudisha Uongo
                isipokua:
                    rudisha Kweli
    mwishowe:
        ikiwa srcname ni sio Tupu:
            support.unlink(srcname)
        ikiwa dstname ni sio Tupu:
            support.unlink(dstname)


SUPPORTS_SENDFILE = supports_file2file_sendfile()

# AIX 32-bit mode, by default, lacks enough memory kila the xz/lzma compiler test
# The AIX command 'dump -o program' gives XCOFF header information
# The second word of the last line kwenye the maxdata value
# when 32-bit maxdata must be greater than 0x1000000 kila the xz test to succeed
eleza _maxdataOK():
    ikiwa AIX na sys.maxsize == 2147483647:
        hdrs=subprocess.getoutput("/usr/bin/dump -o %s" % sys.executable)
        maxdata=hdrs.split("\n")[-1].split()[1]
        rudisha int(maxdata,16) >= 0x20000000
    isipokua:
        rudisha Kweli

kundi TestShutil(unittest.TestCase):

    eleza setUp(self):
        super(TestShutil, self).setUp()
        self.tempdirs = []

    eleza tearDown(self):
        super(TestShutil, self).tearDown()
        wakati self.tempdirs:
            d = self.tempdirs.pop()
            shutil.rmtree(d, os.name kwenye ('nt', 'cygwin'))


    eleza mkdtemp(self):
        """Create a temporary directory that will be cleaned up.

        Returns the path of the directory.
        """
        d = tempfile.mkdtemp()
        self.tempdirs.append(d)
        rudisha d

    eleza test_rmtree_works_on_bytes(self):
        tmp = self.mkdtemp()
        victim = os.path.join(tmp, 'killme')
        os.mkdir(victim)
        write_file(os.path.join(victim, 'somefile'), 'foo')
        victim = os.fsencode(victim)
        self.assertIsInstance(victim, bytes)
        shutil.rmtree(victim)

    @support.skip_unless_symlink
    eleza test_rmtree_fails_on_symlink(self):
        tmp = self.mkdtemp()
        dir_ = os.path.join(tmp, 'dir')
        os.mkdir(dir_)
        link = os.path.join(tmp, 'link')
        os.symlink(dir_, link)
        self.assertRaises(OSError, shutil.rmtree, link)
        self.assertKweli(os.path.exists(dir_))
        self.assertKweli(os.path.lexists(link))
        errors = []
        eleza onerror(*args):
            errors.append(args)
        shutil.rmtree(link, onerror=onerror)
        self.assertEqual(len(errors), 1)
        self.assertIs(errors[0][0], os.path.islink)
        self.assertEqual(errors[0][1], link)
        self.assertIsInstance(errors[0][2][1], OSError)

    @support.skip_unless_symlink
    eleza test_rmtree_works_on_symlinks(self):
        tmp = self.mkdtemp()
        dir1 = os.path.join(tmp, 'dir1')
        dir2 = os.path.join(dir1, 'dir2')
        dir3 = os.path.join(tmp, 'dir3')
        kila d kwenye dir1, dir2, dir3:
            os.mkdir(d)
        file1 = os.path.join(tmp, 'file1')
        write_file(file1, 'foo')
        link1 = os.path.join(dir1, 'link1')
        os.symlink(dir2, link1)
        link2 = os.path.join(dir1, 'link2')
        os.symlink(dir3, link2)
        link3 = os.path.join(dir1, 'link3')
        os.symlink(file1, link3)
        # make sure symlinks are removed but sio followed
        shutil.rmtree(dir1)
        self.assertUongo(os.path.exists(dir1))
        self.assertKweli(os.path.exists(dir3))
        self.assertKweli(os.path.exists(file1))

    @unittest.skipUnless(_winapi, 'only relevant on Windows')
    eleza test_rmtree_fails_on_junctions(self):
        tmp = self.mkdtemp()
        dir_ = os.path.join(tmp, 'dir')
        os.mkdir(dir_)
        link = os.path.join(tmp, 'link')
        _winapi.CreateJunction(dir_, link)
        self.assertRaises(OSError, shutil.rmtree, link)
        self.assertKweli(os.path.exists(dir_))
        self.assertKweli(os.path.lexists(link))
        errors = []
        eleza onerror(*args):
            errors.append(args)
        shutil.rmtree(link, onerror=onerror)
        self.assertEqual(len(errors), 1)
        self.assertIs(errors[0][0], os.path.islink)
        self.assertEqual(errors[0][1], link)
        self.assertIsInstance(errors[0][2][1], OSError)

    @unittest.skipUnless(_winapi, 'only relevant on Windows')
    eleza test_rmtree_works_on_junctions(self):
        tmp = self.mkdtemp()
        dir1 = os.path.join(tmp, 'dir1')
        dir2 = os.path.join(dir1, 'dir2')
        dir3 = os.path.join(tmp, 'dir3')
        kila d kwenye dir1, dir2, dir3:
            os.mkdir(d)
        file1 = os.path.join(tmp, 'file1')
        write_file(file1, 'foo')
        link1 = os.path.join(dir1, 'link1')
        _winapi.CreateJunction(dir2, link1)
        link2 = os.path.join(dir1, 'link2')
        _winapi.CreateJunction(dir3, link2)
        link3 = os.path.join(dir1, 'link3')
        _winapi.CreateJunction(file1, link3)
        # make sure junctions are removed but sio followed
        shutil.rmtree(dir1)
        self.assertUongo(os.path.exists(dir1))
        self.assertKweli(os.path.exists(dir3))
        self.assertKweli(os.path.exists(file1))

    eleza test_rmtree_errors(self):
        # filename ni guaranteed sio to exist
        filename = tempfile.mktemp()
        self.assertRaises(FileNotFoundError, shutil.rmtree, filename)
        # test that ignore_errors option ni honored
        shutil.rmtree(filename, ignore_errors=Kweli)

        # existing file
        tmpdir = self.mkdtemp()
        write_file((tmpdir, "tstfile"), "")
        filename = os.path.join(tmpdir, "tstfile")
        ukijumuisha self.assertRaises(NotADirectoryError) kama cm:
            shutil.rmtree(filename)
        # The reason kila this rather odd construct ni that Windows sprinkles
        # a \*.* at the end of file names. But only sometimes on some buildbots
        possible_args = [filename, os.path.join(filename, '*.*')]
        self.assertIn(cm.exception.filename, possible_args)
        self.assertKweli(os.path.exists(filename))
        # test that ignore_errors option ni honored
        shutil.rmtree(filename, ignore_errors=Kweli)
        self.assertKweli(os.path.exists(filename))
        errors = []
        eleza onerror(*args):
            errors.append(args)
        shutil.rmtree(filename, onerror=onerror)
        self.assertEqual(len(errors), 2)
        self.assertIs(errors[0][0], os.scandir)
        self.assertEqual(errors[0][1], filename)
        self.assertIsInstance(errors[0][2][1], NotADirectoryError)
        self.assertIn(errors[0][2][1].filename, possible_args)
        self.assertIs(errors[1][0], os.rmdir)
        self.assertEqual(errors[1][1], filename)
        self.assertIsInstance(errors[1][2][1], NotADirectoryError)
        self.assertIn(errors[1][2][1].filename, possible_args)


    @unittest.skipIf(sys.platform[:6] == 'cygwin',
                     "This test can't be run on Cygwin (issue #1071513).")
    @unittest.skipIf(hasattr(os, 'geteuid') na os.geteuid() == 0,
                     "This test can't be run reliably kama root (issue #1076467).")
    eleza test_on_error(self):
        self.errorState = 0
        os.mkdir(TESTFN)
        self.addCleanup(shutil.rmtree, TESTFN)

        self.child_file_path = os.path.join(TESTFN, 'a')
        self.child_dir_path = os.path.join(TESTFN, 'b')
        support.create_empty_file(self.child_file_path)
        os.mkdir(self.child_dir_path)
        old_dir_mode = os.stat(TESTFN).st_mode
        old_child_file_mode = os.stat(self.child_file_path).st_mode
        old_child_dir_mode = os.stat(self.child_dir_path).st_mode
        # Make unwritable.
        new_mode = stat.S_IREAD|stat.S_IEXEC
        os.chmod(self.child_file_path, new_mode)
        os.chmod(self.child_dir_path, new_mode)
        os.chmod(TESTFN, new_mode)

        self.addCleanup(os.chmod, TESTFN, old_dir_mode)
        self.addCleanup(os.chmod, self.child_file_path, old_child_file_mode)
        self.addCleanup(os.chmod, self.child_dir_path, old_child_dir_mode)

        shutil.rmtree(TESTFN, onerror=self.check_args_to_onerror)
        # Test whether onerror has actually been called.
        self.assertEqual(self.errorState, 3,
                         "Expected call to onerror function did sio happen.")

    eleza check_args_to_onerror(self, func, arg, exc):
        # test_rmtree_errors deliberately runs rmtree
        # on a directory that ni chmod 500, which will fail.
        # This function ni run when shutil.rmtree fails.
        # 99.9% of the time it initially fails to remove
        # a file kwenye the directory, so the first time through
        # func ni os.remove.
        # However, some Linux machines running ZFS on
        # FUSE experienced a failure earlier kwenye the process
        # at os.listdir.  The first failure may legally
        # be either.
        ikiwa self.errorState < 2:
            ikiwa func ni os.unlink:
                self.assertEqual(arg, self.child_file_path)
            lasivyo func ni os.rmdir:
                self.assertEqual(arg, self.child_dir_path)
            isipokua:
                self.assertIs(func, os.listdir)
                self.assertIn(arg, [TESTFN, self.child_dir_path])
            self.assertKweli(issubclass(exc[0], OSError))
            self.errorState += 1
        isipokua:
            self.assertEqual(func, os.rmdir)
            self.assertEqual(arg, TESTFN)
            self.assertKweli(issubclass(exc[0], OSError))
            self.errorState = 3

    eleza test_rmtree_does_not_choke_on_failing_lstat(self):
        jaribu:
            orig_lstat = os.lstat
            eleza ashiriar(fn, *args, **kwargs):
                ikiwa fn != TESTFN:
                    ashiria OSError()
                isipokua:
                    rudisha orig_lstat(fn)
            os.lstat = ashiriar

            os.mkdir(TESTFN)
            write_file((TESTFN, 'foo'), 'foo')
            shutil.rmtree(TESTFN)
        mwishowe:
            os.lstat = orig_lstat

    @support.skip_unless_symlink
    eleza test_copymode_follow_symlinks(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        dst = os.path.join(tmp_dir, 'bar')
        src_link = os.path.join(tmp_dir, 'baz')
        dst_link = os.path.join(tmp_dir, 'quux')
        write_file(src, 'foo')
        write_file(dst, 'foo')
        os.symlink(src, src_link)
        os.symlink(dst, dst_link)
        os.chmod(src, stat.S_IRWXU|stat.S_IRWXG)
        # file to file
        os.chmod(dst, stat.S_IRWXO)
        self.assertNotEqual(os.stat(src).st_mode, os.stat(dst).st_mode)
        shutil.copymode(src, dst)
        self.assertEqual(os.stat(src).st_mode, os.stat(dst).st_mode)
        # On Windows, os.chmod does sio follow symlinks (issue #15411)
        ikiwa os.name != 'nt':
            # follow src link
            os.chmod(dst, stat.S_IRWXO)
            shutil.copymode(src_link, dst)
            self.assertEqual(os.stat(src).st_mode, os.stat(dst).st_mode)
            # follow dst link
            os.chmod(dst, stat.S_IRWXO)
            shutil.copymode(src, dst_link)
            self.assertEqual(os.stat(src).st_mode, os.stat(dst).st_mode)
            # follow both links
            os.chmod(dst, stat.S_IRWXO)
            shutil.copymode(src_link, dst_link)
            self.assertEqual(os.stat(src).st_mode, os.stat(dst).st_mode)

    @unittest.skipUnless(hasattr(os, 'lchmod'), 'requires os.lchmod')
    @support.skip_unless_symlink
    eleza test_copymode_symlink_to_symlink(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        dst = os.path.join(tmp_dir, 'bar')
        src_link = os.path.join(tmp_dir, 'baz')
        dst_link = os.path.join(tmp_dir, 'quux')
        write_file(src, 'foo')
        write_file(dst, 'foo')
        os.symlink(src, src_link)
        os.symlink(dst, dst_link)
        os.chmod(src, stat.S_IRWXU|stat.S_IRWXG)
        os.chmod(dst, stat.S_IRWXU)
        os.lchmod(src_link, stat.S_IRWXO|stat.S_IRWXG)
        # link to link
        os.lchmod(dst_link, stat.S_IRWXO)
        shutil.copymode(src_link, dst_link, follow_symlinks=Uongo)
        self.assertEqual(os.lstat(src_link).st_mode,
                         os.lstat(dst_link).st_mode)
        self.assertNotEqual(os.stat(src).st_mode, os.stat(dst).st_mode)
        # src link - use chmod
        os.lchmod(dst_link, stat.S_IRWXO)
        shutil.copymode(src_link, dst, follow_symlinks=Uongo)
        self.assertEqual(os.stat(src).st_mode, os.stat(dst).st_mode)
        # dst link - use chmod
        os.lchmod(dst_link, stat.S_IRWXO)
        shutil.copymode(src, dst_link, follow_symlinks=Uongo)
        self.assertEqual(os.stat(src).st_mode, os.stat(dst).st_mode)

    @unittest.skipIf(hasattr(os, 'lchmod'), 'requires os.lchmod to be missing')
    @support.skip_unless_symlink
    eleza test_copymode_symlink_to_symlink_wo_lchmod(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        dst = os.path.join(tmp_dir, 'bar')
        src_link = os.path.join(tmp_dir, 'baz')
        dst_link = os.path.join(tmp_dir, 'quux')
        write_file(src, 'foo')
        write_file(dst, 'foo')
        os.symlink(src, src_link)
        os.symlink(dst, dst_link)
        shutil.copymode(src_link, dst_link, follow_symlinks=Uongo)  # silent fail

    @support.skip_unless_symlink
    eleza test_copystat_symlinks(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        dst = os.path.join(tmp_dir, 'bar')
        src_link = os.path.join(tmp_dir, 'baz')
        dst_link = os.path.join(tmp_dir, 'qux')
        write_file(src, 'foo')
        src_stat = os.stat(src)
        os.utime(src, (src_stat.st_atime,
                       src_stat.st_mtime - 42.0))  # ensure different mtimes
        write_file(dst, 'bar')
        self.assertNotEqual(os.stat(src).st_mtime, os.stat(dst).st_mtime)
        os.symlink(src, src_link)
        os.symlink(dst, dst_link)
        ikiwa hasattr(os, 'lchmod'):
            os.lchmod(src_link, stat.S_IRWXO)
        ikiwa hasattr(os, 'lchflags') na hasattr(stat, 'UF_NODUMP'):
            os.lchflags(src_link, stat.UF_NODUMP)
        src_link_stat = os.lstat(src_link)
        # follow
        ikiwa hasattr(os, 'lchmod'):
            shutil.copystat(src_link, dst_link, follow_symlinks=Kweli)
            self.assertNotEqual(src_link_stat.st_mode, os.stat(dst).st_mode)
        # don't follow
        shutil.copystat(src_link, dst_link, follow_symlinks=Uongo)
        dst_link_stat = os.lstat(dst_link)
        ikiwa os.utime kwenye os.supports_follow_symlinks:
            kila attr kwenye 'st_atime', 'st_mtime':
                # The modification times may be truncated kwenye the new file.
                self.assertLessEqual(getattr(src_link_stat, attr),
                                     getattr(dst_link_stat, attr) + 1)
        ikiwa hasattr(os, 'lchmod'):
            self.assertEqual(src_link_stat.st_mode, dst_link_stat.st_mode)
        ikiwa hasattr(os, 'lchflags') na hasattr(src_link_stat, 'st_flags'):
            self.assertEqual(src_link_stat.st_flags, dst_link_stat.st_flags)
        # tell to follow but dst ni sio a link
        shutil.copystat(src_link, dst, follow_symlinks=Uongo)
        self.assertKweli(abs(os.stat(src).st_mtime - os.stat(dst).st_mtime) <
                        00000.1)

    @unittest.skipUnless(hasattr(os, 'chflags') na
                         hasattr(errno, 'EOPNOTSUPP') na
                         hasattr(errno, 'ENOTSUP'),
                         "requires os.chflags, EOPNOTSUPP & ENOTSUP")
    eleza test_copystat_handles_harmless_chflags_errors(self):
        tmpdir = self.mkdtemp()
        file1 = os.path.join(tmpdir, 'file1')
        file2 = os.path.join(tmpdir, 'file2')
        write_file(file1, 'xxx')
        write_file(file2, 'xxx')

        eleza make_chflags_ashiriar(err):
            ex = OSError()

            eleza _chflags_ashiriar(path, flags, *, follow_symlinks=Kweli):
                ex.errno = err
                ashiria ex
            rudisha _chflags_ashiriar
        old_chflags = os.chflags
        jaribu:
            kila err kwenye errno.EOPNOTSUPP, errno.ENOTSUP:
                os.chflags = make_chflags_ashiriar(err)
                shutil.copystat(file1, file2)
            # assert others errors koma it
            os.chflags = make_chflags_ashiriar(errno.EOPNOTSUPP + errno.ENOTSUP)
            self.assertRaises(OSError, shutil.copystat, file1, file2)
        mwishowe:
            os.chflags = old_chflags

    @support.skip_unless_xattr
    eleza test_copyxattr(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        write_file(src, 'foo')
        dst = os.path.join(tmp_dir, 'bar')
        write_file(dst, 'bar')

        # no xattr == no problem
        shutil._copyxattr(src, dst)
        # common case
        os.setxattr(src, 'user.foo', b'42')
        os.setxattr(src, 'user.bar', b'43')
        shutil._copyxattr(src, dst)
        self.assertEqual(sorted(os.listxattr(src)), sorted(os.listxattr(dst)))
        self.assertEqual(
                os.getxattr(src, 'user.foo'),
                os.getxattr(dst, 'user.foo'))
        # check errors don't affect other attrs
        os.remove(dst)
        write_file(dst, 'bar')
        os_error = OSError(errno.EPERM, 'EPERM')

        eleza _ashiria_on_user_foo(fname, attr, val, **kwargs):
            ikiwa attr == 'user.foo':
                ashiria os_error
            isipokua:
                orig_setxattr(fname, attr, val, **kwargs)
        jaribu:
            orig_setxattr = os.setxattr
            os.setxattr = _ashiria_on_user_foo
            shutil._copyxattr(src, dst)
            self.assertIn('user.bar', os.listxattr(dst))
        mwishowe:
            os.setxattr = orig_setxattr
        # the source filesystem sio supporting xattrs should be ok, too.
        eleza _ashiria_on_src(fname, *, follow_symlinks=Kweli):
            ikiwa fname == src:
                ashiria OSError(errno.ENOTSUP, 'Operation sio supported')
            rudisha orig_listxattr(fname, follow_symlinks=follow_symlinks)
        jaribu:
            orig_listxattr = os.listxattr
            os.listxattr = _ashiria_on_src
            shutil._copyxattr(src, dst)
        mwishowe:
            os.listxattr = orig_listxattr

        # test that shutil.copystat copies xattrs
        src = os.path.join(tmp_dir, 'the_original')
        srcro = os.path.join(tmp_dir, 'the_original_ro')
        write_file(src, src)
        write_file(srcro, srcro)
        os.setxattr(src, 'user.the_value', b'fiddly')
        os.setxattr(srcro, 'user.the_value', b'fiddly')
        os.chmod(srcro, 0o444)
        dst = os.path.join(tmp_dir, 'the_copy')
        dstro = os.path.join(tmp_dir, 'the_copy_ro')
        write_file(dst, dst)
        write_file(dstro, dstro)
        shutil.copystat(src, dst)
        shutil.copystat(srcro, dstro)
        self.assertEqual(os.getxattr(dst, 'user.the_value'), b'fiddly')
        self.assertEqual(os.getxattr(dstro, 'user.the_value'), b'fiddly')

    @support.skip_unless_symlink
    @support.skip_unless_xattr
    @unittest.skipUnless(hasattr(os, 'geteuid') na os.geteuid() == 0,
                         'root privileges required')
    eleza test_copyxattr_symlinks(self):
        # On Linux, it's only possible to access non-user xattr kila symlinks;
        # which kwenye turn require root privileges. This test should be expanded
        # kama soon kama other platforms gain support kila extended attributes.
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        src_link = os.path.join(tmp_dir, 'baz')
        write_file(src, 'foo')
        os.symlink(src, src_link)
        os.setxattr(src, 'trusted.foo', b'42')
        os.setxattr(src_link, 'trusted.foo', b'43', follow_symlinks=Uongo)
        dst = os.path.join(tmp_dir, 'bar')
        dst_link = os.path.join(tmp_dir, 'qux')
        write_file(dst, 'bar')
        os.symlink(dst, dst_link)
        shutil._copyxattr(src_link, dst_link, follow_symlinks=Uongo)
        self.assertEqual(os.getxattr(dst_link, 'trusted.foo', follow_symlinks=Uongo), b'43')
        self.assertRaises(OSError, os.getxattr, dst, 'trusted.foo')
        shutil._copyxattr(src_link, dst, follow_symlinks=Uongo)
        self.assertEqual(os.getxattr(dst, 'trusted.foo'), b'43')

    @support.skip_unless_symlink
    eleza test_copy_symlinks(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        dst = os.path.join(tmp_dir, 'bar')
        src_link = os.path.join(tmp_dir, 'baz')
        write_file(src, 'foo')
        os.symlink(src, src_link)
        ikiwa hasattr(os, 'lchmod'):
            os.lchmod(src_link, stat.S_IRWXU | stat.S_IRWXO)
        # don't follow
        shutil.copy(src_link, dst, follow_symlinks=Kweli)
        self.assertUongo(os.path.islink(dst))
        self.assertEqual(read_file(src), read_file(dst))
        os.remove(dst)
        # follow
        shutil.copy(src_link, dst, follow_symlinks=Uongo)
        self.assertKweli(os.path.islink(dst))
        self.assertEqual(os.readlink(dst), os.readlink(src_link))
        ikiwa hasattr(os, 'lchmod'):
            self.assertEqual(os.lstat(src_link).st_mode,
                             os.lstat(dst).st_mode)

    @support.skip_unless_symlink
    eleza test_copy2_symlinks(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        dst = os.path.join(tmp_dir, 'bar')
        src_link = os.path.join(tmp_dir, 'baz')
        write_file(src, 'foo')
        os.symlink(src, src_link)
        ikiwa hasattr(os, 'lchmod'):
            os.lchmod(src_link, stat.S_IRWXU | stat.S_IRWXO)
        ikiwa hasattr(os, 'lchflags') na hasattr(stat, 'UF_NODUMP'):
            os.lchflags(src_link, stat.UF_NODUMP)
        src_stat = os.stat(src)
        src_link_stat = os.lstat(src_link)
        # follow
        shutil.copy2(src_link, dst, follow_symlinks=Kweli)
        self.assertUongo(os.path.islink(dst))
        self.assertEqual(read_file(src), read_file(dst))
        os.remove(dst)
        # don't follow
        shutil.copy2(src_link, dst, follow_symlinks=Uongo)
        self.assertKweli(os.path.islink(dst))
        self.assertEqual(os.readlink(dst), os.readlink(src_link))
        dst_stat = os.lstat(dst)
        ikiwa os.utime kwenye os.supports_follow_symlinks:
            kila attr kwenye 'st_atime', 'st_mtime':
                # The modification times may be truncated kwenye the new file.
                self.assertLessEqual(getattr(src_link_stat, attr),
                                     getattr(dst_stat, attr) + 1)
        ikiwa hasattr(os, 'lchmod'):
            self.assertEqual(src_link_stat.st_mode, dst_stat.st_mode)
            self.assertNotEqual(src_stat.st_mode, dst_stat.st_mode)
        ikiwa hasattr(os, 'lchflags') na hasattr(src_link_stat, 'st_flags'):
            self.assertEqual(src_link_stat.st_flags, dst_stat.st_flags)

    @support.skip_unless_xattr
    eleza test_copy2_xattr(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'foo')
        dst = os.path.join(tmp_dir, 'bar')
        write_file(src, 'foo')
        os.setxattr(src, 'user.foo', b'42')
        shutil.copy2(src, dst)
        self.assertEqual(
                os.getxattr(src, 'user.foo'),
                os.getxattr(dst, 'user.foo'))
        os.remove(dst)

    @support.skip_unless_symlink
    eleza test_copyfile_symlinks(self):
        tmp_dir = self.mkdtemp()
        src = os.path.join(tmp_dir, 'src')
        dst = os.path.join(tmp_dir, 'dst')
        dst_link = os.path.join(tmp_dir, 'dst_link')
        link = os.path.join(tmp_dir, 'link')
        write_file(src, 'foo')
        os.symlink(src, link)
        # don't follow
        shutil.copyfile(link, dst_link, follow_symlinks=Uongo)
        self.assertKweli(os.path.islink(dst_link))
        self.assertEqual(os.readlink(link), os.readlink(dst_link))
        # follow
        shutil.copyfile(link, dst)
        self.assertUongo(os.path.islink(dst))

    eleza test_rmtree_uses_safe_fd_version_if_available(self):
        _use_fd_functions = ({os.open, os.stat, os.unlink, os.rmdir} <=
                             os.supports_dir_fd na
                             os.listdir kwenye os.supports_fd na
                             os.stat kwenye os.supports_follow_symlinks)
        ikiwa _use_fd_functions:
            self.assertKweli(shutil._use_fd_functions)
            self.assertKweli(shutil.rmtree.avoids_symlink_attacks)
            tmp_dir = self.mkdtemp()
            d = os.path.join(tmp_dir, 'a')
            os.mkdir(d)
            jaribu:
                real_rmtree = shutil._rmtree_safe_fd
                kundi Called(Exception): pita
                eleza _ashiriar(*args, **kwargs):
                    ashiria Called
                shutil._rmtree_safe_fd = _ashiriar
                self.assertRaises(Called, shutil.rmtree, d)
            mwishowe:
                shutil._rmtree_safe_fd = real_rmtree
        isipokua:
            self.assertUongo(shutil._use_fd_functions)
            self.assertUongo(shutil.rmtree.avoids_symlink_attacks)

    eleza test_rmtree_dont_delete_file(self):
        # When called on a file instead of a directory, don't delete it.
        handle, path = tempfile.mkstemp()
        os.close(handle)
        self.assertRaises(NotADirectoryError, shutil.rmtree, path)
        os.remove(path)

    eleza test_copytree_simple(self):
        src_dir = tempfile.mkdtemp()
        dst_dir = os.path.join(tempfile.mkdtemp(), 'destination')
        self.addCleanup(shutil.rmtree, src_dir)
        self.addCleanup(shutil.rmtree, os.path.dirname(dst_dir))
        write_file((src_dir, 'test.txt'), '123')
        os.mkdir(os.path.join(src_dir, 'test_dir'))
        write_file((src_dir, 'test_dir', 'test.txt'), '456')

        shutil.copytree(src_dir, dst_dir)
        self.assertKweli(os.path.isfile(os.path.join(dst_dir, 'test.txt')))
        self.assertKweli(os.path.isdir(os.path.join(dst_dir, 'test_dir')))
        self.assertKweli(os.path.isfile(os.path.join(dst_dir, 'test_dir',
                                                    'test.txt')))
        actual = read_file((dst_dir, 'test.txt'))
        self.assertEqual(actual, '123')
        actual = read_file((dst_dir, 'test_dir', 'test.txt'))
        self.assertEqual(actual, '456')

    eleza test_copytree_dirs_exist_ok(self):
        src_dir = tempfile.mkdtemp()
        dst_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, src_dir)
        self.addCleanup(shutil.rmtree, dst_dir)

        write_file((src_dir, 'nonexisting.txt'), '123')
        os.mkdir(os.path.join(src_dir, 'existing_dir'))
        os.mkdir(os.path.join(dst_dir, 'existing_dir'))
        write_file((dst_dir, 'existing_dir', 'existing.txt'), 'will be replaced')
        write_file((src_dir, 'existing_dir', 'existing.txt'), 'has been replaced')

        shutil.copytree(src_dir, dst_dir, dirs_exist_ok=Kweli)
        self.assertKweli(os.path.isfile(os.path.join(dst_dir, 'nonexisting.txt')))
        self.assertKweli(os.path.isdir(os.path.join(dst_dir, 'existing_dir')))
        self.assertKweli(os.path.isfile(os.path.join(dst_dir, 'existing_dir',
                                                    'existing.txt')))
        actual = read_file((dst_dir, 'nonexisting.txt'))
        self.assertEqual(actual, '123')
        actual = read_file((dst_dir, 'existing_dir', 'existing.txt'))
        self.assertEqual(actual, 'has been replaced')

        ukijumuisha self.assertRaises(FileExistsError):
            shutil.copytree(src_dir, dst_dir, dirs_exist_ok=Uongo)

    @support.skip_unless_symlink
    eleza test_copytree_symlinks(self):
        tmp_dir = self.mkdtemp()
        src_dir = os.path.join(tmp_dir, 'src')
        dst_dir = os.path.join(tmp_dir, 'dst')
        sub_dir = os.path.join(src_dir, 'sub')
        os.mkdir(src_dir)
        os.mkdir(sub_dir)
        write_file((src_dir, 'file.txt'), 'foo')
        src_link = os.path.join(sub_dir, 'link')
        dst_link = os.path.join(dst_dir, 'sub/link')
        os.symlink(os.path.join(src_dir, 'file.txt'),
                   src_link)
        ikiwa hasattr(os, 'lchmod'):
            os.lchmod(src_link, stat.S_IRWXU | stat.S_IRWXO)
        ikiwa hasattr(os, 'lchflags') na hasattr(stat, 'UF_NODUMP'):
            os.lchflags(src_link, stat.UF_NODUMP)
        src_stat = os.lstat(src_link)
        shutil.copytree(src_dir, dst_dir, symlinks=Kweli)
        self.assertKweli(os.path.islink(os.path.join(dst_dir, 'sub', 'link')))
        actual = os.readlink(os.path.join(dst_dir, 'sub', 'link'))
        # Bad practice to blindly strip the prefix kama it may be required to
        # correctly refer to the file, but we're only comparing paths here.
        ikiwa os.name == 'nt' na actual.startswith('\\\\?\\'):
            actual = actual[4:]
        self.assertEqual(actual, os.path.join(src_dir, 'file.txt'))
        dst_stat = os.lstat(dst_link)
        ikiwa hasattr(os, 'lchmod'):
            self.assertEqual(dst_stat.st_mode, src_stat.st_mode)
        ikiwa hasattr(os, 'lchflags'):
            self.assertEqual(dst_stat.st_flags, src_stat.st_flags)

    eleza test_copytree_with_exclude(self):
        # creating data
        join = os.path.join
        exists = os.path.exists
        src_dir = tempfile.mkdtemp()
        jaribu:
            dst_dir = join(tempfile.mkdtemp(), 'destination')
            write_file((src_dir, 'test.txt'), '123')
            write_file((src_dir, 'test.tmp'), '123')
            os.mkdir(join(src_dir, 'test_dir'))
            write_file((src_dir, 'test_dir', 'test.txt'), '456')
            os.mkdir(join(src_dir, 'test_dir2'))
            write_file((src_dir, 'test_dir2', 'test.txt'), '456')
            os.mkdir(join(src_dir, 'test_dir2', 'subdir'))
            os.mkdir(join(src_dir, 'test_dir2', 'subdir2'))
            write_file((src_dir, 'test_dir2', 'subdir', 'test.txt'), '456')
            write_file((src_dir, 'test_dir2', 'subdir2', 'test.py'), '456')

            # testing glob-like patterns
            jaribu:
                patterns = shutil.ignore_patterns('*.tmp', 'test_dir2')
                shutil.copytree(src_dir, dst_dir, ignore=patterns)
                # checking the result: some elements should sio be copied
                self.assertKweli(exists(join(dst_dir, 'test.txt')))
                self.assertUongo(exists(join(dst_dir, 'test.tmp')))
                self.assertUongo(exists(join(dst_dir, 'test_dir2')))
            mwishowe:
                shutil.rmtree(dst_dir)
            jaribu:
                patterns = shutil.ignore_patterns('*.tmp', 'subdir*')
                shutil.copytree(src_dir, dst_dir, ignore=patterns)
                # checking the result: some elements should sio be copied
                self.assertUongo(exists(join(dst_dir, 'test.tmp')))
                self.assertUongo(exists(join(dst_dir, 'test_dir2', 'subdir2')))
                self.assertUongo(exists(join(dst_dir, 'test_dir2', 'subdir')))
            mwishowe:
                shutil.rmtree(dst_dir)

            # testing callable-style
            jaribu:
                eleza _filter(src, names):
                    res = []
                    kila name kwenye names:
                        path = os.path.join(src, name)

                        ikiwa (os.path.isdir(path) na
                            path.split()[-1] == 'subdir'):
                            res.append(name)
                        lasivyo os.path.splitext(path)[-1] kwenye ('.py'):
                            res.append(name)
                    rudisha res

                shutil.copytree(src_dir, dst_dir, ignore=_filter)

                # checking the result: some elements should sio be copied
                self.assertUongo(exists(join(dst_dir, 'test_dir2', 'subdir2',
                                             'test.py')))
                self.assertUongo(exists(join(dst_dir, 'test_dir2', 'subdir')))

            mwishowe:
                shutil.rmtree(dst_dir)
        mwishowe:
            shutil.rmtree(src_dir)
            shutil.rmtree(os.path.dirname(dst_dir))

    eleza test_copytree_retains_permissions(self):
        tmp_dir = tempfile.mkdtemp()
        src_dir = os.path.join(tmp_dir, 'source')
        os.mkdir(src_dir)
        dst_dir = os.path.join(tmp_dir, 'destination')
        self.addCleanup(shutil.rmtree, tmp_dir)

        os.chmod(src_dir, 0o777)
        write_file((src_dir, 'permissive.txt'), '123')
        os.chmod(os.path.join(src_dir, 'permissive.txt'), 0o777)
        write_file((src_dir, 'restrictive.txt'), '456')
        os.chmod(os.path.join(src_dir, 'restrictive.txt'), 0o600)
        restrictive_subdir = tempfile.mkdtemp(dir=src_dir)
        os.chmod(restrictive_subdir, 0o600)

        shutil.copytree(src_dir, dst_dir)
        self.assertEqual(os.stat(src_dir).st_mode, os.stat(dst_dir).st_mode)
        self.assertEqual(os.stat(os.path.join(src_dir, 'permissive.txt')).st_mode,
                          os.stat(os.path.join(dst_dir, 'permissive.txt')).st_mode)
        self.assertEqual(os.stat(os.path.join(src_dir, 'restrictive.txt')).st_mode,
                          os.stat(os.path.join(dst_dir, 'restrictive.txt')).st_mode)
        restrictive_subdir_dst = os.path.join(dst_dir,
                                              os.path.split(restrictive_subdir)[1])
        self.assertEqual(os.stat(restrictive_subdir).st_mode,
                          os.stat(restrictive_subdir_dst).st_mode)

    @unittest.mock.patch('os.chmod')
    eleza test_copytree_winerror(self, mock_patch):
        # When copying to VFAT, copystat() ashirias OSError. On Windows, the
        # exception object has a meaningful 'winerror' attribute, but not
        # on other operating systems. Do sio assume 'winerror' ni set.
        src_dir = tempfile.mkdtemp()
        dst_dir = os.path.join(tempfile.mkdtemp(), 'destination')
        self.addCleanup(shutil.rmtree, src_dir)
        self.addCleanup(shutil.rmtree, os.path.dirname(dst_dir))

        mock_patch.side_effect = PermissionError('ka-boom')
        ukijumuisha self.assertRaises(shutil.Error):
            shutil.copytree(src_dir, dst_dir)

    eleza test_copytree_custom_copy_function(self):
        # See: https://bugs.python.org/issue35648
        eleza custom_cpfun(a, b):
            flag.append(Tupu)
            self.assertIsInstance(a, str)
            self.assertIsInstance(b, str)
            self.assertEqual(a, os.path.join(src, 'foo'))
            self.assertEqual(b, os.path.join(dst, 'foo'))

        flag = []
        src = tempfile.mkdtemp()
        self.addCleanup(support.rmtree, src)
        dst = tempfile.mktemp()
        self.addCleanup(support.rmtree, dst)
        ukijumuisha open(os.path.join(src, 'foo'), 'w') kama f:
            f.close()
        shutil.copytree(src, dst, copy_function=custom_cpfun)
        self.assertEqual(len(flag), 1)

    @unittest.skipUnless(hasattr(os, 'link'), 'requires os.link')
    eleza test_dont_copy_file_onto_link_to_itself(self):
        # bug 851123.
        os.mkdir(TESTFN)
        src = os.path.join(TESTFN, 'cheese')
        dst = os.path.join(TESTFN, 'shop')
        jaribu:
            ukijumuisha open(src, 'w') kama f:
                f.write('cheddar')
            jaribu:
                os.link(src, dst)
            tatizo PermissionError kama e:
                self.skipTest('os.link(): %s' % e)
            self.assertRaises(shutil.SameFileError, shutil.copyfile, src, dst)
            ukijumuisha open(src, 'r') kama f:
                self.assertEqual(f.read(), 'cheddar')
            os.remove(dst)
        mwishowe:
            shutil.rmtree(TESTFN, ignore_errors=Kweli)

    @support.skip_unless_symlink
    eleza test_dont_copy_file_onto_symlink_to_itself(self):
        # bug 851123.
        os.mkdir(TESTFN)
        src = os.path.join(TESTFN, 'cheese')
        dst = os.path.join(TESTFN, 'shop')
        jaribu:
            ukijumuisha open(src, 'w') kama f:
                f.write('cheddar')
            # Using `src` here would mean we end up ukijumuisha a symlink pointing
            # to TESTFN/TESTFN/cheese, wakati it should point at
            # TESTFN/cheese.
            os.symlink('cheese', dst)
            self.assertRaises(shutil.SameFileError, shutil.copyfile, src, dst)
            ukijumuisha open(src, 'r') kama f:
                self.assertEqual(f.read(), 'cheddar')
            os.remove(dst)
        mwishowe:
            shutil.rmtree(TESTFN, ignore_errors=Kweli)

    @support.skip_unless_symlink
    eleza test_rmtree_on_symlink(self):
        # bug 1669.
        os.mkdir(TESTFN)
        jaribu:
            src = os.path.join(TESTFN, 'cheese')
            dst = os.path.join(TESTFN, 'shop')
            os.mkdir(src)
            os.symlink(src, dst)
            self.assertRaises(OSError, shutil.rmtree, dst)
            shutil.rmtree(dst, ignore_errors=Kweli)
        mwishowe:
            shutil.rmtree(TESTFN, ignore_errors=Kweli)

    @unittest.skipUnless(_winapi, 'only relevant on Windows')
    eleza test_rmtree_on_junction(self):
        os.mkdir(TESTFN)
        jaribu:
            src = os.path.join(TESTFN, 'cheese')
            dst = os.path.join(TESTFN, 'shop')
            os.mkdir(src)
            open(os.path.join(src, 'spam'), 'wb').close()
            _winapi.CreateJunction(src, dst)
            self.assertRaises(OSError, shutil.rmtree, dst)
            shutil.rmtree(dst, ignore_errors=Kweli)
        mwishowe:
            shutil.rmtree(TESTFN, ignore_errors=Kweli)

    # Issue #3002: copyfile na copytree block indefinitely on named pipes
    @unittest.skipUnless(hasattr(os, "mkfifo"), 'requires os.mkfifo()')
    eleza test_copyfile_named_pipe(self):
        jaribu:
            os.mkfifo(TESTFN)
        tatizo PermissionError kama e:
            self.skipTest('os.mkfifo(): %s' % e)
        jaribu:
            self.assertRaises(shutil.SpecialFileError,
                                shutil.copyfile, TESTFN, TESTFN2)
            self.assertRaises(shutil.SpecialFileError,
                                shutil.copyfile, __file__, TESTFN)
        mwishowe:
            os.remove(TESTFN)

    @unittest.skipUnless(hasattr(os, "mkfifo"), 'requires os.mkfifo()')
    @support.skip_unless_symlink
    eleza test_copytree_named_pipe(self):
        os.mkdir(TESTFN)
        jaribu:
            subdir = os.path.join(TESTFN, "subdir")
            os.mkdir(subdir)
            pipe = os.path.join(subdir, "mypipe")
            jaribu:
                os.mkfifo(pipe)
            tatizo PermissionError kama e:
                self.skipTest('os.mkfifo(): %s' % e)
            jaribu:
                shutil.copytree(TESTFN, TESTFN2)
            tatizo shutil.Error kama e:
                errors = e.args[0]
                self.assertEqual(len(errors), 1)
                src, dst, error_msg = errors[0]
                self.assertEqual("`%s` ni a named pipe" % pipe, error_msg)
            isipokua:
                self.fail("shutil.Error should have been ashiriad")
        mwishowe:
            shutil.rmtree(TESTFN, ignore_errors=Kweli)
            shutil.rmtree(TESTFN2, ignore_errors=Kweli)

    eleza test_copytree_special_func(self):

        src_dir = self.mkdtemp()
        dst_dir = os.path.join(self.mkdtemp(), 'destination')
        write_file((src_dir, 'test.txt'), '123')
        os.mkdir(os.path.join(src_dir, 'test_dir'))
        write_file((src_dir, 'test_dir', 'test.txt'), '456')

        copied = []
        eleza _copy(src, dst):
            copied.append((src, dst))

        shutil.copytree(src_dir, dst_dir, copy_function=_copy)
        self.assertEqual(len(copied), 2)

    @support.skip_unless_symlink
    eleza test_copytree_dangling_symlinks(self):

        # a dangling symlink ashirias an error at the end
        src_dir = self.mkdtemp()
        dst_dir = os.path.join(self.mkdtemp(), 'destination')
        os.symlink('IDONTEXIST', os.path.join(src_dir, 'test.txt'))
        os.mkdir(os.path.join(src_dir, 'test_dir'))
        write_file((src_dir, 'test_dir', 'test.txt'), '456')
        self.assertRaises(Error, shutil.copytree, src_dir, dst_dir)

        # a dangling symlink ni ignored ukijumuisha the proper flag
        dst_dir = os.path.join(self.mkdtemp(), 'destination2')
        shutil.copytree(src_dir, dst_dir, ignore_dangling_symlinks=Kweli)
        self.assertNotIn('test.txt', os.listdir(dst_dir))

        # a dangling symlink ni copied ikiwa symlinks=Kweli
        dst_dir = os.path.join(self.mkdtemp(), 'destination3')
        shutil.copytree(src_dir, dst_dir, symlinks=Kweli)
        self.assertIn('test.txt', os.listdir(dst_dir))

    @support.skip_unless_symlink
    eleza test_copytree_symlink_dir(self):
        src_dir = self.mkdtemp()
        dst_dir = os.path.join(self.mkdtemp(), 'destination')
        os.mkdir(os.path.join(src_dir, 'real_dir'))
        ukijumuisha open(os.path.join(src_dir, 'real_dir', 'test.txt'), 'w'):
            pita
        os.symlink(os.path.join(src_dir, 'real_dir'),
                   os.path.join(src_dir, 'link_to_dir'),
                   target_is_directory=Kweli)

        shutil.copytree(src_dir, dst_dir, symlinks=Uongo)
        self.assertUongo(os.path.islink(os.path.join(dst_dir, 'link_to_dir')))
        self.assertIn('test.txt', os.listdir(os.path.join(dst_dir, 'link_to_dir')))

        dst_dir = os.path.join(self.mkdtemp(), 'destination2')
        shutil.copytree(src_dir, dst_dir, symlinks=Kweli)
        self.assertKweli(os.path.islink(os.path.join(dst_dir, 'link_to_dir')))
        self.assertIn('test.txt', os.listdir(os.path.join(dst_dir, 'link_to_dir')))

    eleza _copy_file(self, method):
        fname = 'test.txt'
        tmpdir = self.mkdtemp()
        write_file((tmpdir, fname), 'xxx')
        file1 = os.path.join(tmpdir, fname)
        tmpdir2 = self.mkdtemp()
        method(file1, tmpdir2)
        file2 = os.path.join(tmpdir2, fname)
        rudisha (file1, file2)

    eleza test_copy(self):
        # Ensure that the copied file exists na has the same mode bits.
        file1, file2 = self._copy_file(shutil.copy)
        self.assertKweli(os.path.exists(file2))
        self.assertEqual(os.stat(file1).st_mode, os.stat(file2).st_mode)

    @unittest.skipUnless(hasattr(os, 'utime'), 'requires os.utime')
    eleza test_copy2(self):
        # Ensure that the copied file exists na has the same mode na
        # modification time bits.
        file1, file2 = self._copy_file(shutil.copy2)
        self.assertKweli(os.path.exists(file2))
        file1_stat = os.stat(file1)
        file2_stat = os.stat(file2)
        self.assertEqual(file1_stat.st_mode, file2_stat.st_mode)
        kila attr kwenye 'st_atime', 'st_mtime':
            # The modification times may be truncated kwenye the new file.
            self.assertLessEqual(getattr(file1_stat, attr),
                                 getattr(file2_stat, attr) + 1)
        ikiwa hasattr(os, 'chflags') na hasattr(file1_stat, 'st_flags'):
            self.assertEqual(getattr(file1_stat, 'st_flags'),
                             getattr(file2_stat, 'st_flags'))

    @support.requires_zlib
    eleza test_make_tarball(self):
        # creating something to tar
        root_dir, base_dir = self._create_files('')

        tmpdir2 = self.mkdtemp()
        # force shutil to create the directory
        os.rmdir(tmpdir2)
        # working ukijumuisha relative paths
        work_dir = os.path.dirname(tmpdir2)
        rel_base_name = os.path.join(os.path.basename(tmpdir2), 'archive')

        ukijumuisha support.change_cwd(work_dir):
            base_name = os.path.abspath(rel_base_name)
            tarball = make_archive(rel_base_name, 'gztar', root_dir, '.')

        # check ikiwa the compressed tarball was created
        self.assertEqual(tarball, base_name + '.tar.gz')
        self.assertKweli(os.path.isfile(tarball))
        self.assertKweli(tarfile.is_tarfile(tarball))
        ukijumuisha tarfile.open(tarball, 'r:gz') kama tf:
            self.assertCountEqual(tf.getnames(),
                                  ['.', './sub', './sub2',
                                   './file1', './file2', './sub/file3'])

        # trying an uncompressed one
        ukijumuisha support.change_cwd(work_dir):
            tarball = make_archive(rel_base_name, 'tar', root_dir, '.')
        self.assertEqual(tarball, base_name + '.tar')
        self.assertKweli(os.path.isfile(tarball))
        self.assertKweli(tarfile.is_tarfile(tarball))
        ukijumuisha tarfile.open(tarball, 'r') kama tf:
            self.assertCountEqual(tf.getnames(),
                                  ['.', './sub', './sub2',
                                  './file1', './file2', './sub/file3'])

    eleza _tarinfo(self, path):
        ukijumuisha tarfile.open(path) kama tar:
            names = tar.getnames()
            names.sort()
            rudisha tuple(names)

    eleza _create_files(self, base_dir='dist'):
        # creating something to tar
        root_dir = self.mkdtemp()
        dist = os.path.join(root_dir, base_dir)
        os.makedirs(dist, exist_ok=Kweli)
        write_file((dist, 'file1'), 'xxx')
        write_file((dist, 'file2'), 'xxx')
        os.mkdir(os.path.join(dist, 'sub'))
        write_file((dist, 'sub', 'file3'), 'xxx')
        os.mkdir(os.path.join(dist, 'sub2'))
        ikiwa base_dir:
            write_file((root_dir, 'outer'), 'xxx')
        rudisha root_dir, base_dir

    @support.requires_zlib
    @unittest.skipUnless(shutil.which('tar'),
                         'Need the tar command to run')
    eleza test_tarfile_vs_tar(self):
        root_dir, base_dir = self._create_files()
        base_name = os.path.join(self.mkdtemp(), 'archive')
        tarball = make_archive(base_name, 'gztar', root_dir, base_dir)

        # check ikiwa the compressed tarball was created
        self.assertEqual(tarball, base_name + '.tar.gz')
        self.assertKweli(os.path.isfile(tarball))

        # now create another tarball using `tar`
        tarball2 = os.path.join(root_dir, 'archive2.tar')
        tar_cmd = ['tar', '-cf', 'archive2.tar', base_dir]
        subprocess.check_call(tar_cmd, cwd=root_dir,
                              stdout=subprocess.DEVNULL)

        self.assertKweli(os.path.isfile(tarball2))
        # let's compare both tarballs
        self.assertEqual(self._tarinfo(tarball), self._tarinfo(tarball2))

        # trying an uncompressed one
        tarball = make_archive(base_name, 'tar', root_dir, base_dir)
        self.assertEqual(tarball, base_name + '.tar')
        self.assertKweli(os.path.isfile(tarball))

        # now kila a dry_run
        tarball = make_archive(base_name, 'tar', root_dir, base_dir,
                               dry_run=Kweli)
        self.assertEqual(tarball, base_name + '.tar')
        self.assertKweli(os.path.isfile(tarball))

    @support.requires_zlib
    eleza test_make_zipfile(self):
        # creating something to zip
        root_dir, base_dir = self._create_files()

        tmpdir2 = self.mkdtemp()
        # force shutil to create the directory
        os.rmdir(tmpdir2)
        # working ukijumuisha relative paths
        work_dir = os.path.dirname(tmpdir2)
        rel_base_name = os.path.join(os.path.basename(tmpdir2), 'archive')

        ukijumuisha support.change_cwd(work_dir):
            base_name = os.path.abspath(rel_base_name)
            res = make_archive(rel_base_name, 'zip', root_dir)

        self.assertEqual(res, base_name + '.zip')
        self.assertKweli(os.path.isfile(res))
        self.assertKweli(zipfile.is_zipfile(res))
        ukijumuisha zipfile.ZipFile(res) kama zf:
            self.assertCountEqual(zf.namelist(),
                    ['dist/', 'dist/sub/', 'dist/sub2/',
                     'dist/file1', 'dist/file2', 'dist/sub/file3',
                     'outer'])

        ukijumuisha support.change_cwd(work_dir):
            base_name = os.path.abspath(rel_base_name)
            res = make_archive(rel_base_name, 'zip', root_dir, base_dir)

        self.assertEqual(res, base_name + '.zip')
        self.assertKweli(os.path.isfile(res))
        self.assertKweli(zipfile.is_zipfile(res))
        ukijumuisha zipfile.ZipFile(res) kama zf:
            self.assertCountEqual(zf.namelist(),
                    ['dist/', 'dist/sub/', 'dist/sub2/',
                     'dist/file1', 'dist/file2', 'dist/sub/file3'])

    @support.requires_zlib
    @unittest.skipUnless(shutil.which('zip'),
                         'Need the zip command to run')
    eleza test_zipfile_vs_zip(self):
        root_dir, base_dir = self._create_files()
        base_name = os.path.join(self.mkdtemp(), 'archive')
        archive = make_archive(base_name, 'zip', root_dir, base_dir)

        # check ikiwa ZIP file  was created
        self.assertEqual(archive, base_name + '.zip')
        self.assertKweli(os.path.isfile(archive))

        # now create another ZIP file using `zip`
        archive2 = os.path.join(root_dir, 'archive2.zip')
        zip_cmd = ['zip', '-q', '-r', 'archive2.zip', base_dir]
        subprocess.check_call(zip_cmd, cwd=root_dir,
                              stdout=subprocess.DEVNULL)

        self.assertKweli(os.path.isfile(archive2))
        # let's compare both ZIP files
        ukijumuisha zipfile.ZipFile(archive) kama zf:
            names = zf.namelist()
        ukijumuisha zipfile.ZipFile(archive2) kama zf:
            names2 = zf.namelist()
        self.assertEqual(sorted(names), sorted(names2))

    @support.requires_zlib
    @unittest.skipUnless(shutil.which('unzip'),
                         'Need the unzip command to run')
    eleza test_unzip_zipfile(self):
        root_dir, base_dir = self._create_files()
        base_name = os.path.join(self.mkdtemp(), 'archive')
        archive = make_archive(base_name, 'zip', root_dir, base_dir)

        # check ikiwa ZIP file  was created
        self.assertEqual(archive, base_name + '.zip')
        self.assertKweli(os.path.isfile(archive))

        # now check the ZIP file using `unzip -t`
        zip_cmd = ['unzip', '-t', archive]
        ukijumuisha support.change_cwd(root_dir):
            jaribu:
                subprocess.check_output(zip_cmd, stderr=subprocess.STDOUT)
            tatizo subprocess.CalledProcessError kama exc:
                details = exc.output.decode(errors="replace")
                ikiwa 'unrecognized option: t' kwenye details:
                    self.skipTest("unzip doesn't support -t")
                msg = "{}\n\n**Unzip Output**\n{}"
                self.fail(msg.format(exc, details))

    eleza test_make_archive(self):
        tmpdir = self.mkdtemp()
        base_name = os.path.join(tmpdir, 'archive')
        self.assertRaises(ValueError, make_archive, base_name, 'xxx')

    @support.requires_zlib
    eleza test_make_archive_owner_group(self):
        # testing make_archive ukijumuisha owner na group, ukijumuisha various combinations
        # this works even ikiwa there's sio gid/uid support
        ikiwa UID_GID_SUPPORT:
            group = grp.getgrgid(0)[0]
            owner = pwd.getpwuid(0)[0]
        isipokua:
            group = owner = 'root'

        root_dir, base_dir = self._create_files()
        base_name = os.path.join(self.mkdtemp(), 'archive')
        res = make_archive(base_name, 'zip', root_dir, base_dir, owner=owner,
                           group=group)
        self.assertKweli(os.path.isfile(res))

        res = make_archive(base_name, 'zip', root_dir, base_dir)
        self.assertKweli(os.path.isfile(res))

        res = make_archive(base_name, 'tar', root_dir, base_dir,
                           owner=owner, group=group)
        self.assertKweli(os.path.isfile(res))

        res = make_archive(base_name, 'tar', root_dir, base_dir,
                           owner='kjhkjhkjg', group='oihohoh')
        self.assertKweli(os.path.isfile(res))


    @support.requires_zlib
    @unittest.skipUnless(UID_GID_SUPPORT, "Requires grp na pwd support")
    eleza test_tarfile_root_owner(self):
        root_dir, base_dir = self._create_files()
        base_name = os.path.join(self.mkdtemp(), 'archive')
        group = grp.getgrgid(0)[0]
        owner = pwd.getpwuid(0)[0]
        ukijumuisha support.change_cwd(root_dir):
            archive_name = make_archive(base_name, 'gztar', root_dir, 'dist',
                                        owner=owner, group=group)

        # check ikiwa the compressed tarball was created
        self.assertKweli(os.path.isfile(archive_name))

        # now checks the rights
        archive = tarfile.open(archive_name)
        jaribu:
            kila member kwenye archive.getmembers():
                self.assertEqual(member.uid, 0)
                self.assertEqual(member.gid, 0)
        mwishowe:
            archive.close()

    eleza test_make_archive_cwd(self):
        current_dir = os.getcwd()
        eleza _komas(*args, **kw):
            ashiria RuntimeError()

        register_archive_format('xxx', _komas, [], 'xxx file')
        jaribu:
            jaribu:
                make_archive('xxx', 'xxx', root_dir=self.mkdtemp())
            tatizo Exception:
                pita
            self.assertEqual(os.getcwd(), current_dir)
        mwishowe:
            unregister_archive_format('xxx')

    eleza test_make_tarfile_in_curdir(self):
        # Issue #21280
        root_dir = self.mkdtemp()
        ukijumuisha support.change_cwd(root_dir):
            self.assertEqual(make_archive('test', 'tar'), 'test.tar')
            self.assertKweli(os.path.isfile('test.tar'))

    @support.requires_zlib
    eleza test_make_zipfile_in_curdir(self):
        # Issue #21280
        root_dir = self.mkdtemp()
        ukijumuisha support.change_cwd(root_dir):
            self.assertEqual(make_archive('test', 'zip'), 'test.zip')
            self.assertKweli(os.path.isfile('test.zip'))

    eleza test_register_archive_format(self):

        self.assertRaises(TypeError, register_archive_format, 'xxx', 1)
        self.assertRaises(TypeError, register_archive_format, 'xxx', lambda: x,
                          1)
        self.assertRaises(TypeError, register_archive_format, 'xxx', lambda: x,
                          [(1, 2), (1, 2, 3)])

        register_archive_format('xxx', lambda: x, [(1, 2)], 'xxx file')
        formats = [name kila name, params kwenye get_archive_formats()]
        self.assertIn('xxx', formats)

        unregister_archive_format('xxx')
        formats = [name kila name, params kwenye get_archive_formats()]
        self.assertNotIn('xxx', formats)

    eleza check_unpack_archive(self, format):
        self.check_unpack_archive_with_converter(format, lambda path: path)
        self.check_unpack_archive_with_converter(format, pathlib.Path)
        self.check_unpack_archive_with_converter(format, FakePath)

    eleza check_unpack_archive_with_converter(self, format, converter):
        root_dir, base_dir = self._create_files()
        expected = rlistdir(root_dir)
        expected.remove('outer')

        base_name = os.path.join(self.mkdtemp(), 'archive')
        filename = make_archive(base_name, format, root_dir, base_dir)

        # let's try to unpack it now
        tmpdir2 = self.mkdtemp()
        unpack_archive(converter(filename), converter(tmpdir2))
        self.assertEqual(rlistdir(tmpdir2), expected)

        # na again, this time ukijumuisha the format specified
        tmpdir3 = self.mkdtemp()
        unpack_archive(converter(filename), converter(tmpdir3), format=format)
        self.assertEqual(rlistdir(tmpdir3), expected)

        self.assertRaises(shutil.ReadError, unpack_archive, converter(TESTFN))
        self.assertRaises(ValueError, unpack_archive, converter(TESTFN), format='xxx')

    eleza test_unpack_archive_tar(self):
        self.check_unpack_archive('tar')

    @support.requires_zlib
    eleza test_unpack_archive_gztar(self):
        self.check_unpack_archive('gztar')

    @support.requires_bz2
    eleza test_unpack_archive_bztar(self):
        self.check_unpack_archive('bztar')

    @support.requires_lzma
    @unittest.skipIf(AIX na sio _maxdataOK(), "AIX MAXDATA must be 0x20000000 ama larger")
    eleza test_unpack_archive_xztar(self):
        self.check_unpack_archive('xztar')

    @support.requires_zlib
    eleza test_unpack_archive_zip(self):
        self.check_unpack_archive('zip')

    eleza test_unpack_registry(self):

        formats = get_unpack_formats()

        eleza _boo(filename, extract_dir, extra):
            self.assertEqual(extra, 1)
            self.assertEqual(filename, 'stuff.boo')
            self.assertEqual(extract_dir, 'xx')

        register_unpack_format('Boo', ['.boo', '.b2'], _boo, [('extra', 1)])
        unpack_archive('stuff.boo', 'xx')

        # trying to register a .boo unpacker again
        self.assertRaises(RegistryError, register_unpack_format, 'Boo2',
                          ['.boo'], _boo)

        # should work now
        unregister_unpack_format('Boo')
        register_unpack_format('Boo2', ['.boo'], _boo)
        self.assertIn(('Boo2', ['.boo'], ''), get_unpack_formats())
        self.assertNotIn(('Boo', ['.boo'], ''), get_unpack_formats())

        # let's leave a clean state
        unregister_unpack_format('Boo2')
        self.assertEqual(get_unpack_formats(), formats)

    @unittest.skipUnless(hasattr(shutil, 'disk_usage'),
                         "disk_usage sio available on this platform")
    eleza test_disk_usage(self):
        usage = shutil.disk_usage(os.path.dirname(__file__))
        kila attr kwenye ('total', 'used', 'free'):
            self.assertIsInstance(getattr(usage, attr), int)
        self.assertGreater(usage.total, 0)
        self.assertGreater(usage.used, 0)
        self.assertGreaterEqual(usage.free, 0)
        self.assertGreaterEqual(usage.total, usage.used)
        self.assertGreater(usage.total, usage.free)

        # bpo-32557: Check that disk_usage() also accepts a filename
        shutil.disk_usage(__file__)

    @unittest.skipUnless(UID_GID_SUPPORT, "Requires grp na pwd support")
    @unittest.skipUnless(hasattr(os, 'chown'), 'requires os.chown')
    eleza test_chown(self):

        # cleaned-up automatically by TestShutil.tearDown method
        dirname = self.mkdtemp()
        filename = tempfile.mktemp(dir=dirname)
        write_file(filename, 'testing chown function')

        ukijumuisha self.assertRaises(ValueError):
            shutil.chown(filename)

        ukijumuisha self.assertRaises(LookupError):
            shutil.chown(filename, user='non-existing username')

        ukijumuisha self.assertRaises(LookupError):
            shutil.chown(filename, group='non-existing groupname')

        ukijumuisha self.assertRaises(TypeError):
            shutil.chown(filename, b'spam')

        ukijumuisha self.assertRaises(TypeError):
            shutil.chown(filename, 3.14)

        uid = os.getuid()
        gid = os.getgid()

        eleza check_chown(path, uid=Tupu, gid=Tupu):
            s = os.stat(filename)
            ikiwa uid ni sio Tupu:
                self.assertEqual(uid, s.st_uid)
            ikiwa gid ni sio Tupu:
                self.assertEqual(gid, s.st_gid)

        shutil.chown(filename, uid, gid)
        check_chown(filename, uid, gid)
        shutil.chown(filename, uid)
        check_chown(filename, uid)
        shutil.chown(filename, user=uid)
        check_chown(filename, uid)
        shutil.chown(filename, group=gid)
        check_chown(filename, gid=gid)

        shutil.chown(dirname, uid, gid)
        check_chown(dirname, uid, gid)
        shutil.chown(dirname, uid)
        check_chown(dirname, uid)
        shutil.chown(dirname, user=uid)
        check_chown(dirname, uid)
        shutil.chown(dirname, group=gid)
        check_chown(dirname, gid=gid)

        user = pwd.getpwuid(uid)[0]
        group = grp.getgrgid(gid)[0]
        shutil.chown(filename, user, group)
        check_chown(filename, uid, gid)
        shutil.chown(dirname, user, group)
        check_chown(dirname, uid, gid)

    eleza test_copy_rudisha_value(self):
        # copy na copy2 both rudisha their destination path.
        kila fn kwenye (shutil.copy, shutil.copy2):
            src_dir = self.mkdtemp()
            dst_dir = self.mkdtemp()
            src = os.path.join(src_dir, 'foo')
            write_file(src, 'foo')
            rv = fn(src, dst_dir)
            self.assertEqual(rv, os.path.join(dst_dir, 'foo'))
            rv = fn(src, os.path.join(dst_dir, 'bar'))
            self.assertEqual(rv, os.path.join(dst_dir, 'bar'))

    eleza test_copyfile_rudisha_value(self):
        # copytree rudishas its destination path.
        src_dir = self.mkdtemp()
        dst_dir = self.mkdtemp()
        dst_file = os.path.join(dst_dir, 'bar')
        src_file = os.path.join(src_dir, 'foo')
        write_file(src_file, 'foo')
        rv = shutil.copyfile(src_file, dst_file)
        self.assertKweli(os.path.exists(rv))
        self.assertEqual(read_file(src_file), read_file(dst_file))

    eleza test_copyfile_same_file(self):
        # copyfile() should ashiria SameFileError ikiwa the source na destination
        # are the same.
        src_dir = self.mkdtemp()
        src_file = os.path.join(src_dir, 'foo')
        write_file(src_file, 'foo')
        self.assertRaises(SameFileError, shutil.copyfile, src_file, src_file)
        # But Error should work too, to stay backward compatible.
        self.assertRaises(Error, shutil.copyfile, src_file, src_file)
        # Make sure file ni sio corrupted.
        self.assertEqual(read_file(src_file), 'foo')

    eleza test_copytree_rudisha_value(self):
        # copytree rudishas its destination path.
        src_dir = self.mkdtemp()
        dst_dir = src_dir + "dest"
        self.addCleanup(shutil.rmtree, dst_dir, Kweli)
        src = os.path.join(src_dir, 'foo')
        write_file(src, 'foo')
        rv = shutil.copytree(src_dir, dst_dir)
        self.assertEqual(['foo'], os.listdir(rv))


kundi TestWhich(unittest.TestCase):

    eleza setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="Tmp")
        self.addCleanup(shutil.rmtree, self.temp_dir, Kweli)
        # Give the temp_file an ".exe" suffix kila all.
        # It's needed on Windows na sio harmful on other platforms.
        self.temp_file = tempfile.NamedTemporaryFile(dir=self.temp_dir,
                                                     prefix="Tmp",
                                                     suffix=".Exe")
        os.chmod(self.temp_file.name, stat.S_IXUSR)
        self.addCleanup(self.temp_file.close)
        self.dir, self.file = os.path.split(self.temp_file.name)
        self.env_path = self.dir
        self.curdir = os.curdir
        self.ext = ".EXE"

    eleza test_basic(self):
        # Given an EXE kwenye a directory, it should be rudishaed.
        rv = shutil.which(self.file, path=self.dir)
        self.assertEqual(rv, self.temp_file.name)

    eleza test_absolute_cmd(self):
        # When given the fully qualified path to an executable that exists,
        # it should be rudishaed.
        rv = shutil.which(self.temp_file.name, path=self.temp_dir)
        self.assertEqual(rv, self.temp_file.name)

    eleza test_relative_cmd(self):
        # When given the relative path ukijumuisha a directory part to an executable
        # that exists, it should be rudishaed.
        base_dir, tail_dir = os.path.split(self.dir)
        relpath = os.path.join(tail_dir, self.file)
        ukijumuisha support.change_cwd(path=base_dir):
            rv = shutil.which(relpath, path=self.temp_dir)
            self.assertEqual(rv, relpath)
        # But it shouldn't be searched kwenye PATH directories (issue #16957).
        ukijumuisha support.change_cwd(path=self.dir):
            rv = shutil.which(relpath, path=base_dir)
            self.assertIsTupu(rv)

    eleza test_cwd(self):
        # Issue #16957
        base_dir = os.path.dirname(self.dir)
        ukijumuisha support.change_cwd(path=self.dir):
            rv = shutil.which(self.file, path=base_dir)
            ikiwa sys.platform == "win32":
                # Windows: current directory implicitly on PATH
                self.assertEqual(rv, os.path.join(self.curdir, self.file))
            isipokua:
                # Other platforms: shouldn't match kwenye the current directory.
                self.assertIsTupu(rv)

    @unittest.skipIf(hasattr(os, 'geteuid') na os.geteuid() == 0,
                     'non-root user required')
    eleza test_non_matching_mode(self):
        # Set the file read-only na ask kila writeable files.
        os.chmod(self.temp_file.name, stat.S_IREAD)
        ikiwa os.access(self.temp_file.name, os.W_OK):
            self.skipTest("can't set the file read-only")
        rv = shutil.which(self.file, path=self.dir, mode=os.W_OK)
        self.assertIsTupu(rv)

    eleza test_relative_path(self):
        base_dir, tail_dir = os.path.split(self.dir)
        ukijumuisha support.change_cwd(path=base_dir):
            rv = shutil.which(self.file, path=tail_dir)
            self.assertEqual(rv, os.path.join(tail_dir, self.file))

    eleza test_nonexistent_file(self):
        # Return Tupu when no matching executable file ni found on the path.
        rv = shutil.which("foo.exe", path=self.dir)
        self.assertIsTupu(rv)

    @unittest.skipUnless(sys.platform == "win32",
                         "pathext check ni Windows-only")
    eleza test_pathext_checking(self):
        # Ask kila the file without the ".exe" extension, then ensure that
        # it gets found properly ukijumuisha the extension.
        rv = shutil.which(self.file[:-4], path=self.dir)
        self.assertEqual(rv, self.temp_file.name[:-4] + self.ext)

    eleza test_environ_path(self):
        ukijumuisha support.EnvironmentVarGuard() kama env:
            env['PATH'] = self.env_path
            rv = shutil.which(self.file)
            self.assertEqual(rv, self.temp_file.name)

    eleza test_environ_path_empty(self):
        # PATH='': no match
        ukijumuisha support.EnvironmentVarGuard() kama env:
            env['PATH'] = ''
            ukijumuisha unittest.mock.patch('os.confstr', rudisha_value=self.dir, \
                                     create=Kweli), \
                 support.swap_attr(os, 'defpath', self.dir), \
                 support.change_cwd(self.dir):
                rv = shutil.which(self.file)
                self.assertIsTupu(rv)

    eleza test_environ_path_cwd(self):
        expected_cwd = os.path.basename(self.temp_file.name)
        ikiwa sys.platform == "win32":
            curdir = os.curdir
            ikiwa isinstance(expected_cwd, bytes):
                curdir = os.fsencode(curdir)
            expected_cwd = os.path.join(curdir, expected_cwd)

        # PATH=':': explicitly looks kwenye the current directory
        ukijumuisha support.EnvironmentVarGuard() kama env:
            env['PATH'] = os.pathsep
            ukijumuisha unittest.mock.patch('os.confstr', rudisha_value=self.dir, \
                                     create=Kweli), \
                 support.swap_attr(os, 'defpath', self.dir):
                rv = shutil.which(self.file)
                self.assertIsTupu(rv)

                # look kwenye current directory
                ukijumuisha support.change_cwd(self.dir):
                    rv = shutil.which(self.file)
                    self.assertEqual(rv, expected_cwd)

    eleza test_environ_path_missing(self):
        ukijumuisha support.EnvironmentVarGuard() kama env:
            env.pop('PATH', Tupu)

            # without confstr
            ukijumuisha unittest.mock.patch('os.confstr', side_effect=ValueError, \
                                     create=Kweli), \
                 support.swap_attr(os, 'defpath', self.dir):
                rv = shutil.which(self.file)
            self.assertEqual(rv, self.temp_file.name)

            # ukijumuisha confstr
            ukijumuisha unittest.mock.patch('os.confstr', rudisha_value=self.dir, \
                                     create=Kweli), \
                 support.swap_attr(os, 'defpath', ''):
                rv = shutil.which(self.file)
            self.assertEqual(rv, self.temp_file.name)

    eleza test_empty_path(self):
        base_dir = os.path.dirname(self.dir)
        ukijumuisha support.change_cwd(path=self.dir), \
             support.EnvironmentVarGuard() kama env:
            env['PATH'] = self.env_path
            rv = shutil.which(self.file, path='')
            self.assertIsTupu(rv)

    eleza test_empty_path_no_PATH(self):
        ukijumuisha support.EnvironmentVarGuard() kama env:
            env.pop('PATH', Tupu)
            rv = shutil.which(self.file)
            self.assertIsTupu(rv)

    @unittest.skipUnless(sys.platform == "win32", 'test specific to Windows')
    eleza test_pathext(self):
        ext = ".xyz"
        temp_filexyz = tempfile.NamedTemporaryFile(dir=self.temp_dir,
                                                   prefix="Tmp2", suffix=ext)
        os.chmod(temp_filexyz.name, stat.S_IXUSR)
        self.addCleanup(temp_filexyz.close)

        # strip path na extension
        program = os.path.basename(temp_filexyz.name)
        program = os.path.splitext(program)[0]

        ukijumuisha support.EnvironmentVarGuard() kama env:
            env['PATHEXT'] = ext
            rv = shutil.which(program, path=self.temp_dir)
            self.assertEqual(rv, temp_filexyz.name)


kundi TestWhichBytes(TestWhich):
    eleza setUp(self):
        TestWhich.setUp(self)
        self.dir = os.fsencode(self.dir)
        self.file = os.fsencode(self.file)
        self.temp_file.name = os.fsencode(self.temp_file.name)
        self.curdir = os.fsencode(self.curdir)
        self.ext = os.fsencode(self.ext)


kundi TestMove(unittest.TestCase):

    eleza setUp(self):
        filename = "foo"
        self.src_dir = tempfile.mkdtemp()
        self.dst_dir = tempfile.mkdtemp()
        self.src_file = os.path.join(self.src_dir, filename)
        self.dst_file = os.path.join(self.dst_dir, filename)
        ukijumuisha open(self.src_file, "wb") kama f:
            f.write(b"spam")

    eleza tearDown(self):
        kila d kwenye (self.src_dir, self.dst_dir):
            jaribu:
                ikiwa d:
                    shutil.rmtree(d)
            tatizo:
                pita

    eleza _check_move_file(self, src, dst, real_dst):
        ukijumuisha open(src, "rb") kama f:
            contents = f.read()
        shutil.move(src, dst)
        ukijumuisha open(real_dst, "rb") kama f:
            self.assertEqual(contents, f.read())
        self.assertUongo(os.path.exists(src))

    eleza _check_move_dir(self, src, dst, real_dst):
        contents = sorted(os.listdir(src))
        shutil.move(src, dst)
        self.assertEqual(contents, sorted(os.listdir(real_dst)))
        self.assertUongo(os.path.exists(src))

    eleza test_move_file(self):
        # Move a file to another location on the same filesystem.
        self._check_move_file(self.src_file, self.dst_file, self.dst_file)

    eleza test_move_file_to_dir(self):
        # Move a file inside an existing dir on the same filesystem.
        self._check_move_file(self.src_file, self.dst_dir, self.dst_file)

    @mock_rename
    eleza test_move_file_other_fs(self):
        # Move a file to an existing dir on another filesystem.
        self.test_move_file()

    @mock_rename
    eleza test_move_file_to_dir_other_fs(self):
        # Move a file to another location on another filesystem.
        self.test_move_file_to_dir()

    eleza test_move_dir(self):
        # Move a dir to another location on the same filesystem.
        dst_dir = tempfile.mktemp()
        jaribu:
            self._check_move_dir(self.src_dir, dst_dir, dst_dir)
        mwishowe:
            jaribu:
                shutil.rmtree(dst_dir)
            tatizo:
                pita

    @mock_rename
    eleza test_move_dir_other_fs(self):
        # Move a dir to another location on another filesystem.
        self.test_move_dir()

    eleza test_move_dir_to_dir(self):
        # Move a dir inside an existing dir on the same filesystem.
        self._check_move_dir(self.src_dir, self.dst_dir,
            os.path.join(self.dst_dir, os.path.basename(self.src_dir)))

    @mock_rename
    eleza test_move_dir_to_dir_other_fs(self):
        # Move a dir inside an existing dir on another filesystem.
        self.test_move_dir_to_dir()

    eleza test_move_dir_sep_to_dir(self):
        self._check_move_dir(self.src_dir + os.path.sep, self.dst_dir,
            os.path.join(self.dst_dir, os.path.basename(self.src_dir)))

    @unittest.skipUnless(os.path.altsep, 'requires os.path.altsep')
    eleza test_move_dir_altsep_to_dir(self):
        self._check_move_dir(self.src_dir + os.path.altsep, self.dst_dir,
            os.path.join(self.dst_dir, os.path.basename(self.src_dir)))

    eleza test_existing_file_inside_dest_dir(self):
        # A file ukijumuisha the same name inside the destination dir already exists.
        ukijumuisha open(self.dst_file, "wb"):
            pita
        self.assertRaises(shutil.Error, shutil.move, self.src_file, self.dst_dir)

    eleza test_dont_move_dir_in_itself(self):
        # Moving a dir inside itself ashirias an Error.
        dst = os.path.join(self.src_dir, "bar")
        self.assertRaises(shutil.Error, shutil.move, self.src_dir, dst)

    eleza test_destinsrc_false_negative(self):
        os.mkdir(TESTFN)
        jaribu:
            kila src, dst kwenye [('srcdir', 'srcdir/dest')]:
                src = os.path.join(TESTFN, src)
                dst = os.path.join(TESTFN, dst)
                self.assertKweli(shutil._destinsrc(src, dst),
                             msg='_destinsrc() wrongly concluded that '
                             'dst (%s) ni haiko kwenye src (%s)' % (dst, src))
        mwishowe:
            shutil.rmtree(TESTFN, ignore_errors=Kweli)

    eleza test_destinsrc_false_positive(self):
        os.mkdir(TESTFN)
        jaribu:
            kila src, dst kwenye [('srcdir', 'src/dest'), ('srcdir', 'srcdir.new')]:
                src = os.path.join(TESTFN, src)
                dst = os.path.join(TESTFN, dst)
                self.assertUongo(shutil._destinsrc(src, dst),
                            msg='_destinsrc() wrongly concluded that '
                            'dst (%s) ni kwenye src (%s)' % (dst, src))
        mwishowe:
            shutil.rmtree(TESTFN, ignore_errors=Kweli)

    @support.skip_unless_symlink
    @mock_rename
    eleza test_move_file_symlink(self):
        dst = os.path.join(self.src_dir, 'bar')
        os.symlink(self.src_file, dst)
        shutil.move(dst, self.dst_file)
        self.assertKweli(os.path.islink(self.dst_file))
        self.assertKweli(os.path.samefile(self.src_file, self.dst_file))

    @support.skip_unless_symlink
    @mock_rename
    eleza test_move_file_symlink_to_dir(self):
        filename = "bar"
        dst = os.path.join(self.src_dir, filename)
        os.symlink(self.src_file, dst)
        shutil.move(dst, self.dst_dir)
        final_link = os.path.join(self.dst_dir, filename)
        self.assertKweli(os.path.islink(final_link))
        self.assertKweli(os.path.samefile(self.src_file, final_link))

    @support.skip_unless_symlink
    @mock_rename
    eleza test_move_dangling_symlink(self):
        src = os.path.join(self.src_dir, 'baz')
        dst = os.path.join(self.src_dir, 'bar')
        os.symlink(src, dst)
        dst_link = os.path.join(self.dst_dir, 'quux')
        shutil.move(dst, dst_link)
        self.assertKweli(os.path.islink(dst_link))
        self.assertEqual(os.path.realpath(src), os.path.realpath(dst_link))

    @support.skip_unless_symlink
    @mock_rename
    eleza test_move_dir_symlink(self):
        src = os.path.join(self.src_dir, 'baz')
        dst = os.path.join(self.src_dir, 'bar')
        os.mkdir(src)
        os.symlink(src, dst)
        dst_link = os.path.join(self.dst_dir, 'quux')
        shutil.move(dst, dst_link)
        self.assertKweli(os.path.islink(dst_link))
        self.assertKweli(os.path.samefile(src, dst_link))

    eleza test_move_rudisha_value(self):
        rv = shutil.move(self.src_file, self.dst_dir)
        self.assertEqual(rv,
                os.path.join(self.dst_dir, os.path.basename(self.src_file)))

    eleza test_move_as_rename_rudisha_value(self):
        rv = shutil.move(self.src_file, os.path.join(self.dst_dir, 'bar'))
        self.assertEqual(rv, os.path.join(self.dst_dir, 'bar'))

    @mock_rename
    eleza test_move_file_special_function(self):
        moved = []
        eleza _copy(src, dst):
            moved.append((src, dst))
        shutil.move(self.src_file, self.dst_dir, copy_function=_copy)
        self.assertEqual(len(moved), 1)

    @mock_rename
    eleza test_move_dir_special_function(self):
        moved = []
        eleza _copy(src, dst):
            moved.append((src, dst))
        support.create_empty_file(os.path.join(self.src_dir, 'child'))
        support.create_empty_file(os.path.join(self.src_dir, 'child1'))
        shutil.move(self.src_dir, self.dst_dir, copy_function=_copy)
        self.assertEqual(len(moved), 3)


kundi TestCopyFile(unittest.TestCase):

    _delete = Uongo

    kundi Faux(object):
        _entered = Uongo
        _exited_ukijumuisha = Tupu
        _ashiriad = Uongo
        eleza __init__(self, ashiria_in_exit=Uongo, suppress_at_exit=Kweli):
            self._ashiria_in_exit = ashiria_in_exit
            self._suppress_at_exit = suppress_at_exit
        eleza read(self, *args):
            rudisha ''
        eleza __enter__(self):
            self._entered = Kweli
        eleza __exit__(self, exc_type, exc_val, exc_tb):
            self._exited_ukijumuisha = exc_type, exc_val, exc_tb
            ikiwa self._ashiria_in_exit:
                self._ashiriad = Kweli
                ashiria OSError("Cannot close")
            rudisha self._suppress_at_exit

    eleza tearDown(self):
        ikiwa self._delete:
            toa shutil.open

    eleza _set_shutil_open(self, func):
        shutil.open = func
        self._delete = Kweli

    eleza test_w_source_open_fails(self):
        eleza _open(filename, mode='r'):
            ikiwa filename == 'srcfile':
                ashiria OSError('Cannot open "srcfile"')
            assert 0  # shouldn't reach here.

        self._set_shutil_open(_open)

        self.assertRaises(OSError, shutil.copyfile, 'srcfile', 'destfile')

    @unittest.skipIf(MACOS, "skipped on macOS")
    eleza test_w_dest_open_fails(self):

        srcfile = self.Faux()

        eleza _open(filename, mode='r'):
            ikiwa filename == 'srcfile':
                rudisha srcfile
            ikiwa filename == 'destfile':
                ashiria OSError('Cannot open "destfile"')
            assert 0  # shouldn't reach here.

        self._set_shutil_open(_open)

        shutil.copyfile('srcfile', 'destfile')
        self.assertKweli(srcfile._entered)
        self.assertKweli(srcfile._exited_with[0] ni OSError)
        self.assertEqual(srcfile._exited_with[1].args,
                         ('Cannot open "destfile"',))

    @unittest.skipIf(MACOS, "skipped on macOS")
    eleza test_w_dest_close_fails(self):

        srcfile = self.Faux()
        destfile = self.Faux(Kweli)

        eleza _open(filename, mode='r'):
            ikiwa filename == 'srcfile':
                rudisha srcfile
            ikiwa filename == 'destfile':
                rudisha destfile
            assert 0  # shouldn't reach here.

        self._set_shutil_open(_open)

        shutil.copyfile('srcfile', 'destfile')
        self.assertKweli(srcfile._entered)
        self.assertKweli(destfile._entered)
        self.assertKweli(destfile._ashiriad)
        self.assertKweli(srcfile._exited_with[0] ni OSError)
        self.assertEqual(srcfile._exited_with[1].args,
                         ('Cannot close',))

    @unittest.skipIf(MACOS, "skipped on macOS")
    eleza test_w_source_close_fails(self):

        srcfile = self.Faux(Kweli)
        destfile = self.Faux()

        eleza _open(filename, mode='r'):
            ikiwa filename == 'srcfile':
                rudisha srcfile
            ikiwa filename == 'destfile':
                rudisha destfile
            assert 0  # shouldn't reach here.

        self._set_shutil_open(_open)

        self.assertRaises(OSError,
                          shutil.copyfile, 'srcfile', 'destfile')
        self.assertKweli(srcfile._entered)
        self.assertKweli(destfile._entered)
        self.assertUongo(destfile._ashiriad)
        self.assertKweli(srcfile._exited_with[0] ni Tupu)
        self.assertKweli(srcfile._ashiriad)

    eleza test_move_dir_caseinsensitive(self):
        # Renames a folder to the same name
        # but a different case.

        self.src_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.src_dir, Kweli)
        dst_dir = os.path.join(
                os.path.dirname(self.src_dir),
                os.path.basename(self.src_dir).upper())
        self.assertNotEqual(self.src_dir, dst_dir)

        jaribu:
            shutil.move(self.src_dir, dst_dir)
            self.assertKweli(os.path.isdir(dst_dir))
        mwishowe:
            os.rmdir(dst_dir)


kundi TestCopyFileObj(unittest.TestCase):
    FILESIZE = 2 * 1024 * 1024

    @classmethod
    eleza setUpClass(cls):
        write_test_file(TESTFN, cls.FILESIZE)

    @classmethod
    eleza tearDownClass(cls):
        support.unlink(TESTFN)
        support.unlink(TESTFN2)

    eleza tearDown(self):
        support.unlink(TESTFN2)

    @contextlib.contextmanager
    eleza get_files(self):
        ukijumuisha open(TESTFN, "rb") kama src:
            ukijumuisha open(TESTFN2, "wb") kama dst:
                tuma (src, dst)

    eleza assert_files_eq(self, src, dst):
        ukijumuisha open(src, 'rb') kama fsrc:
            ukijumuisha open(dst, 'rb') kama fdst:
                self.assertEqual(fsrc.read(), fdst.read())

    eleza test_content(self):
        ukijumuisha self.get_files() kama (src, dst):
            shutil.copyfileobj(src, dst)
        self.assert_files_eq(TESTFN, TESTFN2)

    eleza test_file_not_closed(self):
        ukijumuisha self.get_files() kama (src, dst):
            shutil.copyfileobj(src, dst)
            assert sio src.closed
            assert sio dst.closed

    eleza test_file_offset(self):
        ukijumuisha self.get_files() kama (src, dst):
            shutil.copyfileobj(src, dst)
            self.assertEqual(src.tell(), self.FILESIZE)
            self.assertEqual(dst.tell(), self.FILESIZE)

    @unittest.skipIf(os.name != 'nt', "Windows only")
    eleza test_win_impl(self):
        # Make sure alternate Windows implementation ni called.
        ukijumuisha unittest.mock.patch("shutil._copyfileobj_readinto") kama m:
            shutil.copyfile(TESTFN, TESTFN2)
        assert m.called

        # File size ni 2 MiB but max buf size should be 1 MiB.
        self.assertEqual(m.call_args[0][2], 1 * 1024 * 1024)

        # If file size < 1 MiB memoryview() length must be equal to
        # the actual file size.
        ukijumuisha tempfile.NamedTemporaryFile(delete=Uongo) kama f:
            f.write(b'foo')
        fname = f.name
        self.addCleanup(support.unlink, fname)
        ukijumuisha unittest.mock.patch("shutil._copyfileobj_readinto") kama m:
            shutil.copyfile(fname, TESTFN2)
        self.assertEqual(m.call_args[0][2], 3)

        # Empty files should sio rely on readinto() variant.
        ukijumuisha tempfile.NamedTemporaryFile(delete=Uongo) kama f:
            pita
        fname = f.name
        self.addCleanup(support.unlink, fname)
        ukijumuisha unittest.mock.patch("shutil._copyfileobj_readinto") kama m:
            shutil.copyfile(fname, TESTFN2)
        assert sio m.called
        self.assert_files_eq(fname, TESTFN2)


kundi _ZeroCopyFileTest(object):
    """Tests common to all zero-copy APIs."""
    FILESIZE = (10 * 1024 * 1024)  # 10 MiB
    FILEDATA = b""
    PATCHPOINT = ""

    @classmethod
    eleza setUpClass(cls):
        write_test_file(TESTFN, cls.FILESIZE)
        ukijumuisha open(TESTFN, 'rb') kama f:
            cls.FILEDATA = f.read()
            assert len(cls.FILEDATA) == cls.FILESIZE

    @classmethod
    eleza tearDownClass(cls):
        support.unlink(TESTFN)

    eleza tearDown(self):
        support.unlink(TESTFN2)

    @contextlib.contextmanager
    eleza get_files(self):
        ukijumuisha open(TESTFN, "rb") kama src:
            ukijumuisha open(TESTFN2, "wb") kama dst:
                tuma (src, dst)

    eleza zerocopy_fun(self, *args, **kwargs):
        ashiria NotImplementedError("must be implemented kwenye subclass")

    eleza reset(self):
        self.tearDown()
        self.tearDownClass()
        self.setUpClass()
        self.setUp()

    # ---

    eleza test_regular_copy(self):
        ukijumuisha self.get_files() kama (src, dst):
            self.zerocopy_fun(src, dst)
        self.assertEqual(read_file(TESTFN2, binary=Kweli), self.FILEDATA)
        # Make sure the fallback function ni sio called.
        ukijumuisha self.get_files() kama (src, dst):
            ukijumuisha unittest.mock.patch('shutil.copyfileobj') kama m:
                shutil.copyfile(TESTFN, TESTFN2)
            assert sio m.called

    eleza test_same_file(self):
        self.addCleanup(self.reset)
        ukijumuisha self.get_files() kama (src, dst):
            ukijumuisha self.assertRaises(Exception):
                self.zerocopy_fun(src, src)
        # Make sure src file ni sio corrupted.
        self.assertEqual(read_file(TESTFN, binary=Kweli), self.FILEDATA)

    eleza test_non_existent_src(self):
        name = tempfile.mktemp()
        ukijumuisha self.assertRaises(FileNotFoundError) kama cm:
            shutil.copyfile(name, "new")
        self.assertEqual(cm.exception.filename, name)

    eleza test_empty_file(self):
        srcname = TESTFN + 'src'
        dstname = TESTFN + 'dst'
        self.addCleanup(lambda: support.unlink(srcname))
        self.addCleanup(lambda: support.unlink(dstname))
        ukijumuisha open(srcname, "wb"):
            pita

        ukijumuisha open(srcname, "rb") kama src:
            ukijumuisha open(dstname, "wb") kama dst:
                self.zerocopy_fun(src, dst)

        self.assertEqual(read_file(dstname, binary=Kweli), b"")

    eleza test_unhandled_exception(self):
        ukijumuisha unittest.mock.patch(self.PATCHPOINT,
                                 side_effect=ZeroDivisionError):
            self.assertRaises(ZeroDivisionError,
                              shutil.copyfile, TESTFN, TESTFN2)

    eleza test_exception_on_first_call(self):
        # Emulate a case where the first call to the zero-copy
        # function ashirias an exception kwenye which case the function is
        # supposed to give up immediately.
        ukijumuisha unittest.mock.patch(self.PATCHPOINT,
                                 side_effect=OSError(errno.EINVAL, "yo")):
            ukijumuisha self.get_files() kama (src, dst):
                ukijumuisha self.assertRaises(_GiveupOnFastCopy):
                    self.zerocopy_fun(src, dst)

    eleza test_filesystem_full(self):
        # Emulate a case where filesystem ni full na sendfile() fails
        # on first call.
        ukijumuisha unittest.mock.patch(self.PATCHPOINT,
                                 side_effect=OSError(errno.ENOSPC, "yo")):
            ukijumuisha self.get_files() kama (src, dst):
                self.assertRaises(OSError, self.zerocopy_fun, src, dst)


@unittest.skipIf(sio SUPPORTS_SENDFILE, 'os.sendfile() sio supported')
kundi TestZeroCopySendfile(_ZeroCopyFileTest, unittest.TestCase):
    PATCHPOINT = "os.sendfile"

    eleza zerocopy_fun(self, fsrc, fdst):
        rudisha shutil._fastcopy_sendfile(fsrc, fdst)

    eleza test_non_regular_file_src(self):
        ukijumuisha io.BytesIO(self.FILEDATA) kama src:
            ukijumuisha open(TESTFN2, "wb") kama dst:
                ukijumuisha self.assertRaises(_GiveupOnFastCopy):
                    self.zerocopy_fun(src, dst)
                shutil.copyfileobj(src, dst)

        self.assertEqual(read_file(TESTFN2, binary=Kweli), self.FILEDATA)

    eleza test_non_regular_file_dst(self):
        ukijumuisha open(TESTFN, "rb") kama src:
            ukijumuisha io.BytesIO() kama dst:
                ukijumuisha self.assertRaises(_GiveupOnFastCopy):
                    self.zerocopy_fun(src, dst)
                shutil.copyfileobj(src, dst)
                dst.seek(0)
                self.assertEqual(dst.read(), self.FILEDATA)

    eleza test_exception_on_second_call(self):
        eleza sendfile(*args, **kwargs):
            ikiwa sio flag:
                flag.append(Tupu)
                rudisha orig_sendfile(*args, **kwargs)
            isipokua:
                ashiria OSError(errno.EBADF, "yo")

        flag = []
        orig_sendfile = os.sendfile
        ukijumuisha unittest.mock.patch('os.sendfile', create=Kweli,
                                 side_effect=sendfile):
            ukijumuisha self.get_files() kama (src, dst):
                ukijumuisha self.assertRaises(OSError) kama cm:
                    shutil._fastcopy_sendfile(src, dst)
        assert flag
        self.assertEqual(cm.exception.errno, errno.EBADF)

    eleza test_cant_get_size(self):
        # Emulate a case where src file size cannot be determined.
        # Internally bufsize will be set to a small value na
        # sendfile() will be called repeatedly.
        ukijumuisha unittest.mock.patch('os.fstat', side_effect=OSError) kama m:
            ukijumuisha self.get_files() kama (src, dst):
                shutil._fastcopy_sendfile(src, dst)
                assert m.called
        self.assertEqual(read_file(TESTFN2, binary=Kweli), self.FILEDATA)

    eleza test_small_chunks(self):
        # Force internal file size detection to be smaller than the
        # actual file size. We want to force sendfile() to be called
        # multiple times, also kwenye order to emulate a src fd which gets
        # bigger wakati it ni being copied.
        mock = unittest.mock.Mock()
        mock.st_size = 65536 + 1
        ukijumuisha unittest.mock.patch('os.fstat', rudisha_value=mock) kama m:
            ukijumuisha self.get_files() kama (src, dst):
                shutil._fastcopy_sendfile(src, dst)
                assert m.called
        self.assertEqual(read_file(TESTFN2, binary=Kweli), self.FILEDATA)

    eleza test_big_chunk(self):
        # Force internal file size detection to be +100MB bigger than
        # the actual file size. Make sure sendfile() does sio rely on
        # file size value tatizo kila (maybe) a better throughput /
        # performance.
        mock = unittest.mock.Mock()
        mock.st_size = self.FILESIZE + (100 * 1024 * 1024)
        ukijumuisha unittest.mock.patch('os.fstat', rudisha_value=mock) kama m:
            ukijumuisha self.get_files() kama (src, dst):
                shutil._fastcopy_sendfile(src, dst)
                assert m.called
        self.assertEqual(read_file(TESTFN2, binary=Kweli), self.FILEDATA)

    eleza test_blocksize_arg(self):
        ukijumuisha unittest.mock.patch('os.sendfile',
                                 side_effect=ZeroDivisionError) kama m:
            self.assertRaises(ZeroDivisionError,
                              shutil.copyfile, TESTFN, TESTFN2)
            blocksize = m.call_args[0][3]
            # Make sure file size na the block size arg pitaed to
            # sendfile() are the same.
            self.assertEqual(blocksize, os.path.getsize(TESTFN))
            # ...unless we're dealing ukijumuisha a small file.
            support.unlink(TESTFN2)
            write_file(TESTFN2, b"hello", binary=Kweli)
            self.addCleanup(support.unlink, TESTFN2 + '3')
            self.assertRaises(ZeroDivisionError,
                              shutil.copyfile, TESTFN2, TESTFN2 + '3')
            blocksize = m.call_args[0][3]
            self.assertEqual(blocksize, 2 ** 23)

    eleza test_file2file_not_supported(self):
        # Emulate a case where sendfile() only support file->socket
        # fds. In such a case copyfile() ni supposed to skip the
        # fast-copy attempt kutoka then on.
        assert shutil._USE_CP_SENDFILE
        jaribu:
            ukijumuisha unittest.mock.patch(
                    self.PATCHPOINT,
                    side_effect=OSError(errno.ENOTSOCK, "yo")) kama m:
                ukijumuisha self.get_files() kama (src, dst):
                    ukijumuisha self.assertRaises(_GiveupOnFastCopy):
                        shutil._fastcopy_sendfile(src, dst)
                assert m.called
            assert sio shutil._USE_CP_SENDFILE

            ukijumuisha unittest.mock.patch(self.PATCHPOINT) kama m:
                shutil.copyfile(TESTFN, TESTFN2)
                assert sio m.called
        mwishowe:
            shutil._USE_CP_SENDFILE = Kweli


@unittest.skipIf(sio MACOS, 'macOS only')
kundi TestZeroCopyMACOS(_ZeroCopyFileTest, unittest.TestCase):
    PATCHPOINT = "posix._fcopyfile"

    eleza zerocopy_fun(self, src, dst):
        rudisha shutil._fastcopy_fcopyfile(src, dst, posix._COPYFILE_DATA)


kundi TermsizeTests(unittest.TestCase):
    eleza test_does_not_crash(self):
        """Check ikiwa get_terminal_size() rudishas a meaningful value.

        There's no easy portable way to actually check the size of the
        terminal, so let's check ikiwa it rudishas something sensible instead.
        """
        size = shutil.get_terminal_size()
        self.assertGreaterEqual(size.columns, 0)
        self.assertGreaterEqual(size.lines, 0)

    eleza test_os_environ_first(self):
        "Check ikiwa environment variables have precedence"

        ukijumuisha support.EnvironmentVarGuard() kama env:
            env['COLUMNS'] = '777'
            toa env['LINES']
            size = shutil.get_terminal_size()
        self.assertEqual(size.columns, 777)

        ukijumuisha support.EnvironmentVarGuard() kama env:
            toa env['COLUMNS']
            env['LINES'] = '888'
            size = shutil.get_terminal_size()
        self.assertEqual(size.lines, 888)

    eleza test_bad_environ(self):
        ukijumuisha support.EnvironmentVarGuard() kama env:
            env['COLUMNS'] = 'xxx'
            env['LINES'] = 'yyy'
            size = shutil.get_terminal_size()
        self.assertGreaterEqual(size.columns, 0)
        self.assertGreaterEqual(size.lines, 0)

    @unittest.skipUnless(os.isatty(sys.__stdout__.fileno()), "not on tty")
    @unittest.skipUnless(hasattr(os, 'get_terminal_size'),
                         'need os.get_terminal_size()')
    eleza test_stty_match(self):
        """Check ikiwa stty rudishas the same results ignoring env

        This test will fail ikiwa stdin na stdout are connected to
        different terminals ukijumuisha different sizes. Nevertheless, such
        situations should be pretty rare.
        """
        jaribu:
            size = subprocess.check_output(['stty', 'size']).decode().split()
        tatizo (FileNotFoundError, PermissionError,
                subprocess.CalledProcessError):
            self.skipTest("stty invocation failed")
        expected = (int(size[1]), int(size[0])) # reversed order

        ukijumuisha support.EnvironmentVarGuard() kama env:
            toa env['LINES']
            toa env['COLUMNS']
            actual = shutil.get_terminal_size()

        self.assertEqual(expected, actual)

    eleza test_fallback(self):
        ukijumuisha support.EnvironmentVarGuard() kama env:
            toa env['LINES']
            toa env['COLUMNS']

            # sys.__stdout__ has no fileno()
            ukijumuisha support.swap_attr(sys, '__stdout__', Tupu):
                size = shutil.get_terminal_size(fallback=(10, 20))
            self.assertEqual(size.columns, 10)
            self.assertEqual(size.lines, 20)

            # sys.__stdout__ ni sio a terminal on Unix
            # ama fileno() haiko kwenye (0, 1, 2) on Windows
            ukijumuisha open(os.devnull, 'w') kama f, \
                 support.swap_attr(sys, '__stdout__', f):
                size = shutil.get_terminal_size(fallback=(30, 40))
            self.assertEqual(size.columns, 30)
            self.assertEqual(size.lines, 40)


kundi PublicAPITests(unittest.TestCase):
    """Ensures that the correct values are exposed kwenye the public API."""

    eleza test_module_all_attribute(self):
        self.assertKweli(hasattr(shutil, '__all__'))
        target_api = ['copyfileobj', 'copyfile', 'copymode', 'copystat',
                      'copy', 'copy2', 'copytree', 'move', 'rmtree', 'Error',
                      'SpecialFileError', 'ExecError', 'make_archive',
                      'get_archive_formats', 'register_archive_format',
                      'unregister_archive_format', 'get_unpack_formats',
                      'register_unpack_format', 'unregister_unpack_format',
                      'unpack_archive', 'ignore_patterns', 'chown', 'which',
                      'get_terminal_size', 'SameFileError']
        ikiwa hasattr(os, 'statvfs') ama os.name == 'nt':
            target_api.append('disk_usage')
        self.assertEqual(set(shutil.__all__), set(target_api))


ikiwa __name__ == '__main__':
    unittest.main()
