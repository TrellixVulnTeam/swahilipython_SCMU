# tempfile.py unit tests.
agiza tempfile
agiza errno
agiza io
agiza os
agiza pathlib
agiza signal
agiza sys
agiza re
agiza warnings
agiza contextlib
agiza stat
agiza weakref
kutoka unittest agiza mock

agiza unittest
kutoka test agiza support
kutoka test.support agiza script_helper


has_textmode = (tempfile._text_openflags != tempfile._bin_openflags)
has_spawnl = hasattr(os, 'spawnl')

# TEST_FILES may need to be tweaked kila systems depending on the maximum
# number of files that can be opened at one time (see ulimit -n)
ikiwa sys.platform.startswith('openbsd'):
    TEST_FILES = 48
isipokua:
    TEST_FILES = 100

# This ni organized kama one test kila each chunk of code kwenye tempfile.py,
# kwenye order of their appearance kwenye the file.  Testing which requires
# threads ni sio done here.

kundi TestLowLevelInternals(unittest.TestCase):
    eleza test_infer_return_type_singles(self):
        self.assertIs(str, tempfile._infer_return_type(''))
        self.assertIs(bytes, tempfile._infer_return_type(b''))
        self.assertIs(str, tempfile._infer_return_type(Tupu))

    eleza test_infer_return_type_multiples(self):
        self.assertIs(str, tempfile._infer_return_type('', ''))
        self.assertIs(bytes, tempfile._infer_return_type(b'', b''))
        ukijumuisha self.assertRaises(TypeError):
            tempfile._infer_return_type('', b'')
        ukijumuisha self.assertRaises(TypeError):
            tempfile._infer_return_type(b'', '')

    eleza test_infer_return_type_multiples_and_none(self):
        self.assertIs(str, tempfile._infer_return_type(Tupu, ''))
        self.assertIs(str, tempfile._infer_return_type('', Tupu))
        self.assertIs(str, tempfile._infer_return_type(Tupu, Tupu))
        self.assertIs(bytes, tempfile._infer_return_type(b'', Tupu))
        self.assertIs(bytes, tempfile._infer_return_type(Tupu, b''))
        ukijumuisha self.assertRaises(TypeError):
            tempfile._infer_return_type('', Tupu, b'')
        ukijumuisha self.assertRaises(TypeError):
            tempfile._infer_return_type(b'', Tupu, '')

    eleza test_infer_return_type_pathlib(self):
        self.assertIs(str, tempfile._infer_return_type(pathlib.Path('/')))


# Common functionality.

kundi BaseTestCase(unittest.TestCase):

    str_check = re.compile(r"^[a-z0-9_-]{8}$")
    b_check = re.compile(br"^[a-z0-9_-]{8}$")

    eleza setUp(self):
        self._warnings_manager = support.check_warnings()
        self._warnings_manager.__enter__()
        warnings.filterwarnings("ignore", category=RuntimeWarning,
                                message="mktemp", module=__name__)

    eleza tearDown(self):
        self._warnings_manager.__exit__(Tupu, Tupu, Tupu)

    eleza nameCheck(self, name, dir, pre, suf):
        (ndir, nbase) = os.path.split(name)
        npre  = nbase[:len(pre)]
        nsuf  = nbase[len(nbase)-len(suf):]

        ikiwa dir ni sio Tupu:
            self.assertIs(
                type(name),
                str
                ikiwa type(dir) ni str ama isinstance(dir, os.PathLike) isipokua
                bytes,
                "unexpected rudisha type",
            )
        ikiwa pre ni sio Tupu:
            self.assertIs(type(name), str ikiwa type(pre) ni str isipokua bytes,
                          "unexpected rudisha type")
        ikiwa suf ni sio Tupu:
            self.assertIs(type(name), str ikiwa type(suf) ni str isipokua bytes,
                          "unexpected rudisha type")
        ikiwa (dir, pre, suf) == (Tupu, Tupu, Tupu):
            self.assertIs(type(name), str, "default rudisha type must be str")

        # check kila equality of the absolute paths!
        self.assertEqual(os.path.abspath(ndir), os.path.abspath(dir),
                         "file %r haiko kwenye directory %r" % (name, dir))
        self.assertEqual(npre, pre,
                         "file %r does sio begin ukijumuisha %r" % (nbase, pre))
        self.assertEqual(nsuf, suf,
                         "file %r does sio end ukijumuisha %r" % (nbase, suf))

        nbase = nbase[len(pre):len(nbase)-len(suf)]
        check = self.str_check ikiwa isinstance(nbase, str) isipokua self.b_check
        self.assertKweli(check.match(nbase),
                        "random characters %r do sio match %r"
                        % (nbase, check.pattern))


kundi TestExports(BaseTestCase):
    eleza test_exports(self):
        # There are no surprising symbols kwenye the tempfile module
        dict = tempfile.__dict__

        expected = {
            "NamedTemporaryFile" : 1,
            "TemporaryFile" : 1,
            "mkstemp" : 1,
            "mkdtemp" : 1,
            "mktemp" : 1,
            "TMP_MAX" : 1,
            "gettempprefix" : 1,
            "gettempprefixb" : 1,
            "gettempdir" : 1,
            "gettempdirb" : 1,
            "tempdir" : 1,
            "template" : 1,
            "SpooledTemporaryFile" : 1,
            "TemporaryDirectory" : 1,
        }

        unexp = []
        kila key kwenye dict:
            ikiwa key[0] != '_' na key haiko kwenye expected:
                unexp.append(key)
        self.assertKweli(len(unexp) == 0,
                        "unexpected keys: %s" % unexp)


kundi TestRandomNameSequence(BaseTestCase):
    """Test the internal iterator object _RandomNameSequence."""

    eleza setUp(self):
        self.r = tempfile._RandomNameSequence()
        super().setUp()

    eleza test_get_six_char_str(self):
        # _RandomNameSequence returns a six-character string
        s = next(self.r)
        self.nameCheck(s, '', '', '')

    eleza test_many(self):
        # _RandomNameSequence returns no duplicate strings (stochastic)

        dict = {}
        r = self.r
        kila i kwenye range(TEST_FILES):
            s = next(r)
            self.nameCheck(s, '', '', '')
            self.assertNotIn(s, dict)
            dict[s] = 1

    eleza supports_iter(self):
        # _RandomNameSequence supports the iterator protocol

        i = 0
        r = self.r
        kila s kwenye r:
            i += 1
            ikiwa i == 20:
                koma

    @unittest.skipUnless(hasattr(os, 'fork'),
        "os.fork ni required kila this test")
    eleza test_process_awareness(self):
        # ensure that the random source differs between
        # child na parent.
        read_fd, write_fd = os.pipe()
        pid = Tupu
        jaribu:
            pid = os.fork()
            ikiwa sio pid:
                # child process
                os.close(read_fd)
                os.write(write_fd, next(self.r).encode("ascii"))
                os.close(write_fd)
                # bypita the normal exit handlers- leave those to
                # the parent.
                os._exit(0)

            # parent process
            parent_value = next(self.r)
            child_value = os.read(read_fd, len(parent_value)).decode("ascii")
        mwishowe:
            ikiwa pid:
                # best effort to ensure the process can't bleed out
                # via any bugs above
                jaribu:
                    os.kill(pid, signal.SIGKILL)
                tatizo OSError:
                    pita

                # Read the process exit status to avoid zombie process
                os.waitpid(pid, 0)

            os.close(read_fd)
            os.close(write_fd)
        self.assertNotEqual(child_value, parent_value)



kundi TestCandidateTempdirList(BaseTestCase):
    """Test the internal function _candidate_tempdir_list."""

    eleza test_nonempty_list(self):
        # _candidate_tempdir_list returns a nonempty list of strings

        cand = tempfile._candidate_tempdir_list()

        self.assertUongo(len(cand) == 0)
        kila c kwenye cand:
            self.assertIsInstance(c, str)

    eleza test_wanted_dirs(self):
        # _candidate_tempdir_list contains the expected directories

        # Make sure the interesting environment variables are all set.
        ukijumuisha support.EnvironmentVarGuard() kama env:
            kila envname kwenye 'TMPDIR', 'TEMP', 'TMP':
                dirname = os.getenv(envname)
                ikiwa sio dirname:
                    env[envname] = os.path.abspath(envname)

            cand = tempfile._candidate_tempdir_list()

            kila envname kwenye 'TMPDIR', 'TEMP', 'TMP':
                dirname = os.getenv(envname)
                ikiwa sio dirname: ashiria ValueError
                self.assertIn(dirname, cand)

            jaribu:
                dirname = os.getcwd()
            tatizo (AttributeError, OSError):
                dirname = os.curdir

            self.assertIn(dirname, cand)

            # Not practical to try to verify the presence of OS-specific
            # paths kwenye this list.


# We test _get_default_tempdir some more by testing gettempdir.

kundi TestGetDefaultTempdir(BaseTestCase):
    """Test _get_default_tempdir()."""

    eleza test_no_files_left_behind(self):
        # use a private empty directory
        ukijumuisha tempfile.TemporaryDirectory() kama our_temp_directory:
            # force _get_default_tempdir() to consider our empty directory
            eleza our_candidate_list():
                rudisha [our_temp_directory]

            ukijumuisha support.swap_attr(tempfile, "_candidate_tempdir_list",
                                   our_candidate_list):
                # verify our directory ni empty after _get_default_tempdir()
                tempfile._get_default_tempdir()
                self.assertEqual(os.listdir(our_temp_directory), [])

                eleza raise_OSError(*args, **kwargs):
                    ashiria OSError()

                ukijumuisha support.swap_attr(io, "open", raise_OSError):
                    # test again ukijumuisha failing io.open()
                    ukijumuisha self.assertRaises(FileNotFoundError):
                        tempfile._get_default_tempdir()
                    self.assertEqual(os.listdir(our_temp_directory), [])

                eleza bad_writer(*args, **kwargs):
                    fp = orig_open(*args, **kwargs)
                    fp.write = raise_OSError
                    rudisha fp

                ukijumuisha support.swap_attr(io, "open", bad_writer) kama orig_open:
                    # test again ukijumuisha failing write()
                    ukijumuisha self.assertRaises(FileNotFoundError):
                        tempfile._get_default_tempdir()
                    self.assertEqual(os.listdir(our_temp_directory), [])


kundi TestGetCandidateNames(BaseTestCase):
    """Test the internal function _get_candidate_names."""

    eleza test_retval(self):
        # _get_candidate_names returns a _RandomNameSequence object
        obj = tempfile._get_candidate_names()
        self.assertIsInstance(obj, tempfile._RandomNameSequence)

    eleza test_same_thing(self):
        # _get_candidate_names always returns the same object
        a = tempfile._get_candidate_names()
        b = tempfile._get_candidate_names()

        self.assertKweli(a ni b)


@contextlib.contextmanager
eleza _inside_empty_temp_dir():
    dir = tempfile.mkdtemp()
    jaribu:
        ukijumuisha support.swap_attr(tempfile, 'tempdir', dir):
            tuma
    mwishowe:
        support.rmtree(dir)


eleza _mock_candidate_names(*names):
    rudisha support.swap_attr(tempfile,
                             '_get_candidate_names',
                             lambda: iter(names))


kundi TestBadTempdir:

    eleza test_read_only_directory(self):
        ukijumuisha _inside_empty_temp_dir():
            oldmode = mode = os.stat(tempfile.tempdir).st_mode
            mode &= ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
            os.chmod(tempfile.tempdir, mode)
            jaribu:
                ikiwa os.access(tempfile.tempdir, os.W_OK):
                    self.skipTest("can't set the directory read-only")
                ukijumuisha self.assertRaises(PermissionError):
                    self.make_temp()
                self.assertEqual(os.listdir(tempfile.tempdir), [])
            mwishowe:
                os.chmod(tempfile.tempdir, oldmode)

    eleza test_nonexisting_directory(self):
        ukijumuisha _inside_empty_temp_dir():
            tempdir = os.path.join(tempfile.tempdir, 'nonexistent')
            ukijumuisha support.swap_attr(tempfile, 'tempdir', tempdir):
                ukijumuisha self.assertRaises(FileNotFoundError):
                    self.make_temp()

    eleza test_non_directory(self):
        ukijumuisha _inside_empty_temp_dir():
            tempdir = os.path.join(tempfile.tempdir, 'file')
            open(tempdir, 'wb').close()
            ukijumuisha support.swap_attr(tempfile, 'tempdir', tempdir):
                ukijumuisha self.assertRaises((NotADirectoryError, FileNotFoundError)):
                    self.make_temp()


kundi TestMkstempInner(TestBadTempdir, BaseTestCase):
    """Test the internal function _mkstemp_inner."""

    kundi mkstemped:
        _bflags = tempfile._bin_openflags
        _tflags = tempfile._text_openflags
        _close = os.close
        _unlink = os.unlink

        eleza __init__(self, dir, pre, suf, bin):
            ikiwa bin: flags = self._bflags
            isipokua:   flags = self._tflags

            output_type = tempfile._infer_return_type(dir, pre, suf)
            (self.fd, self.name) = tempfile._mkstemp_inner(dir, pre, suf, flags, output_type)

        eleza write(self, str):
            os.write(self.fd, str)

        eleza __del__(self):
            self._close(self.fd)
            self._unlink(self.name)

    eleza do_create(self, dir=Tupu, pre=Tupu, suf=Tupu, bin=1):
        output_type = tempfile._infer_return_type(dir, pre, suf)
        ikiwa dir ni Tupu:
            ikiwa output_type ni str:
                dir = tempfile.gettempdir()
            isipokua:
                dir = tempfile.gettempdirb()
        ikiwa pre ni Tupu:
            pre = output_type()
        ikiwa suf ni Tupu:
            suf = output_type()
        file = self.mkstemped(dir, pre, suf, bin)

        self.nameCheck(file.name, dir, pre, suf)
        rudisha file

    eleza test_basic(self):
        # _mkstemp_inner can create files
        self.do_create().write(b"blat")
        self.do_create(pre="a").write(b"blat")
        self.do_create(suf="b").write(b"blat")
        self.do_create(pre="a", suf="b").write(b"blat")
        self.do_create(pre="aa", suf=".txt").write(b"blat")

    eleza test_basic_with_bytes_names(self):
        # _mkstemp_inner can create files when given name parts all
        # specified kama bytes.
        dir_b = tempfile.gettempdirb()
        self.do_create(dir=dir_b, suf=b"").write(b"blat")
        self.do_create(dir=dir_b, pre=b"a").write(b"blat")
        self.do_create(dir=dir_b, suf=b"b").write(b"blat")
        self.do_create(dir=dir_b, pre=b"a", suf=b"b").write(b"blat")
        self.do_create(dir=dir_b, pre=b"aa", suf=b".txt").write(b"blat")
        # Can't mix str & binary types kwenye the args.
        ukijumuisha self.assertRaises(TypeError):
            self.do_create(dir="", suf=b"").write(b"blat")
        ukijumuisha self.assertRaises(TypeError):
            self.do_create(dir=dir_b, pre="").write(b"blat")
        ukijumuisha self.assertRaises(TypeError):
            self.do_create(dir=dir_b, pre=b"", suf="").write(b"blat")

    eleza test_basic_many(self):
        # _mkstemp_inner can create many files (stochastic)
        extant = list(range(TEST_FILES))
        kila i kwenye extant:
            extant[i] = self.do_create(pre="aa")

    eleza test_choose_directory(self):
        # _mkstemp_inner can create files kwenye a user-selected directory
        dir = tempfile.mkdtemp()
        jaribu:
            self.do_create(dir=dir).write(b"blat")
            self.do_create(dir=pathlib.Path(dir)).write(b"blat")
        mwishowe:
            os.rmdir(dir)

    eleza test_file_mode(self):
        # _mkstemp_inner creates files ukijumuisha the proper mode

        file = self.do_create()
        mode = stat.S_IMODE(os.stat(file.name).st_mode)
        expected = 0o600
        ikiwa sys.platform == 'win32':
            # There's no distinction among 'user', 'group' na 'world';
            # replicate the 'user' bits.
            user = expected >> 6
            expected = user * (1 + 8 + 64)
        self.assertEqual(mode, expected)

    @unittest.skipUnless(has_spawnl, 'os.spawnl sio available')
    eleza test_noinherit(self):
        # _mkstemp_inner file handles are sio inerited by child processes

        ikiwa support.verbose:
            v="v"
        isipokua:
            v="q"

        file = self.do_create()
        self.assertEqual(os.get_inheritable(file.fd), Uongo)
        fd = "%d" % file.fd

        jaribu:
            me = __file__
        tatizo NameError:
            me = sys.argv[0]

        # We have to exec something, so that FD_CLOEXEC will take
        # effect.  The core of this test ni therefore in
        # tf_inherit_check.py, which see.
        tester = os.path.join(os.path.dirname(os.path.abspath(me)),
                              "tf_inherit_check.py")

        # On Windows a spawn* /path/ ukijumuisha embedded spaces shouldn't be quoted,
        # but an arg ukijumuisha embedded spaces should be decorated ukijumuisha double
        # quotes on each end
        ikiwa sys.platform == 'win32':
            decorated = '"%s"' % sys.executable
            tester = '"%s"' % tester
        isipokua:
            decorated = sys.executable

        retval = os.spawnl(os.P_WAIT, sys.executable, decorated, tester, v, fd)
        self.assertUongo(retval < 0,
                    "child process caught fatal signal %d" % -retval)
        self.assertUongo(retval > 0, "child process reports failure %d"%retval)

    @unittest.skipUnless(has_textmode, "text mode sio available")
    eleza test_textmode(self):
        # _mkstemp_inner can create files kwenye text mode

        # A text file ni truncated at the first Ctrl+Z byte
        f = self.do_create(bin=0)
        f.write(b"blat\x1a")
        f.write(b"extra\n")
        os.lseek(f.fd, 0, os.SEEK_SET)
        self.assertEqual(os.read(f.fd, 20), b"blat")

    eleza make_temp(self):
        rudisha tempfile._mkstemp_inner(tempfile.gettempdir(),
                                       tempfile.gettempprefix(),
                                       '',
                                       tempfile._bin_openflags,
                                       str)

    eleza test_collision_with_existing_file(self):
        # _mkstemp_inner tries another name when a file with
        # the chosen name already exists
        ukijumuisha _inside_empty_temp_dir(), \
             _mock_candidate_names('aaa', 'aaa', 'bbb'):
            (fd1, name1) = self.make_temp()
            os.close(fd1)
            self.assertKweli(name1.endswith('aaa'))

            (fd2, name2) = self.make_temp()
            os.close(fd2)
            self.assertKweli(name2.endswith('bbb'))

    eleza test_collision_with_existing_directory(self):
        # _mkstemp_inner tries another name when a directory with
        # the chosen name already exists
        ukijumuisha _inside_empty_temp_dir(), \
             _mock_candidate_names('aaa', 'aaa', 'bbb'):
            dir = tempfile.mkdtemp()
            self.assertKweli(dir.endswith('aaa'))

            (fd, name) = self.make_temp()
            os.close(fd)
            self.assertKweli(name.endswith('bbb'))


kundi TestGetTempPrefix(BaseTestCase):
    """Test gettempprefix()."""

    eleza test_sane_template(self):
        # gettempprefix returns a nonempty prefix string
        p = tempfile.gettempprefix()

        self.assertIsInstance(p, str)
        self.assertGreater(len(p), 0)

        pb = tempfile.gettempprefixb()

        self.assertIsInstance(pb, bytes)
        self.assertGreater(len(pb), 0)

    eleza test_usable_template(self):
        # gettempprefix returns a usable prefix string

        # Create a temp directory, avoiding use of the prefix.
        # Then attempt to create a file whose name is
        # prefix + 'xxxxxx.xxx' kwenye that directory.
        p = tempfile.gettempprefix() + "xxxxxx.xxx"
        d = tempfile.mkdtemp(prefix="")
        jaribu:
            p = os.path.join(d, p)
            fd = os.open(p, os.O_RDWR | os.O_CREAT)
            os.close(fd)
            os.unlink(p)
        mwishowe:
            os.rmdir(d)


kundi TestGetTempDir(BaseTestCase):
    """Test gettempdir()."""

    eleza test_directory_exists(self):
        # gettempdir returns a directory which exists

        kila d kwenye (tempfile.gettempdir(), tempfile.gettempdirb()):
            self.assertKweli(os.path.isabs(d) ama d == os.curdir,
                            "%r ni sio an absolute path" % d)
            self.assertKweli(os.path.isdir(d),
                            "%r ni sio a directory" % d)

    eleza test_directory_writable(self):
        # gettempdir returns a directory writable by the user

        # sneaky: just instantiate a NamedTemporaryFile, which
        # defaults to writing into the directory returned by
        # gettempdir.
        ukijumuisha tempfile.NamedTemporaryFile() kama file:
            file.write(b"blat")

    eleza test_same_thing(self):
        # gettempdir always returns the same object
        a = tempfile.gettempdir()
        b = tempfile.gettempdir()
        c = tempfile.gettempdirb()

        self.assertKweli(a ni b)
        self.assertNotEqual(type(a), type(c))
        self.assertEqual(a, os.fsdecode(c))

    eleza test_case_sensitive(self):
        # gettempdir should sio flatten its case
        # even on a case-insensitive file system
        case_sensitive_tempdir = tempfile.mkdtemp("-Temp")
        _tempdir, tempfile.tempdir = tempfile.tempdir, Tupu
        jaribu:
            ukijumuisha support.EnvironmentVarGuard() kama env:
                # Fake the first env var which ni checked kama a candidate
                env["TMPDIR"] = case_sensitive_tempdir
                self.assertEqual(tempfile.gettempdir(), case_sensitive_tempdir)
        mwishowe:
            tempfile.tempdir = _tempdir
            support.rmdir(case_sensitive_tempdir)


kundi TestMkstemp(BaseTestCase):
    """Test mkstemp()."""

    eleza do_create(self, dir=Tupu, pre=Tupu, suf=Tupu):
        output_type = tempfile._infer_return_type(dir, pre, suf)
        ikiwa dir ni Tupu:
            ikiwa output_type ni str:
                dir = tempfile.gettempdir()
            isipokua:
                dir = tempfile.gettempdirb()
        ikiwa pre ni Tupu:
            pre = output_type()
        ikiwa suf ni Tupu:
            suf = output_type()
        (fd, name) = tempfile.mkstemp(dir=dir, prefix=pre, suffix=suf)
        (ndir, nbase) = os.path.split(name)
        adir = os.path.abspath(dir)
        self.assertEqual(adir, ndir,
            "Directory '%s' incorrectly returned kama '%s'" % (adir, ndir))

        jaribu:
            self.nameCheck(name, dir, pre, suf)
        mwishowe:
            os.close(fd)
            os.unlink(name)

    eleza test_basic(self):
        # mkstemp can create files
        self.do_create()
        self.do_create(pre="a")
        self.do_create(suf="b")
        self.do_create(pre="a", suf="b")
        self.do_create(pre="aa", suf=".txt")
        self.do_create(dir=".")

    eleza test_basic_with_bytes_names(self):
        # mkstemp can create files when given name parts all
        # specified kama bytes.
        d = tempfile.gettempdirb()
        self.do_create(dir=d, suf=b"")
        self.do_create(dir=d, pre=b"a")
        self.do_create(dir=d, suf=b"b")
        self.do_create(dir=d, pre=b"a", suf=b"b")
        self.do_create(dir=d, pre=b"aa", suf=b".txt")
        self.do_create(dir=b".")
        ukijumuisha self.assertRaises(TypeError):
            self.do_create(dir=".", pre=b"aa", suf=b".txt")
        ukijumuisha self.assertRaises(TypeError):
            self.do_create(dir=b".", pre="aa", suf=b".txt")
        ukijumuisha self.assertRaises(TypeError):
            self.do_create(dir=b".", pre=b"aa", suf=".txt")


    eleza test_choose_directory(self):
        # mkstemp can create directories kwenye a user-selected directory
        dir = tempfile.mkdtemp()
        jaribu:
            self.do_create(dir=dir)
            self.do_create(dir=pathlib.Path(dir))
        mwishowe:
            os.rmdir(dir)


kundi TestMkdtemp(TestBadTempdir, BaseTestCase):
    """Test mkdtemp()."""

    eleza make_temp(self):
        rudisha tempfile.mkdtemp()

    eleza do_create(self, dir=Tupu, pre=Tupu, suf=Tupu):
        output_type = tempfile._infer_return_type(dir, pre, suf)
        ikiwa dir ni Tupu:
            ikiwa output_type ni str:
                dir = tempfile.gettempdir()
            isipokua:
                dir = tempfile.gettempdirb()
        ikiwa pre ni Tupu:
            pre = output_type()
        ikiwa suf ni Tupu:
            suf = output_type()
        name = tempfile.mkdtemp(dir=dir, prefix=pre, suffix=suf)

        jaribu:
            self.nameCheck(name, dir, pre, suf)
            rudisha name
        tatizo:
            os.rmdir(name)
            raise

    eleza test_basic(self):
        # mkdtemp can create directories
        os.rmdir(self.do_create())
        os.rmdir(self.do_create(pre="a"))
        os.rmdir(self.do_create(suf="b"))
        os.rmdir(self.do_create(pre="a", suf="b"))
        os.rmdir(self.do_create(pre="aa", suf=".txt"))

    eleza test_basic_with_bytes_names(self):
        # mkdtemp can create directories when given all binary parts
        d = tempfile.gettempdirb()
        os.rmdir(self.do_create(dir=d))
        os.rmdir(self.do_create(dir=d, pre=b"a"))
        os.rmdir(self.do_create(dir=d, suf=b"b"))
        os.rmdir(self.do_create(dir=d, pre=b"a", suf=b"b"))
        os.rmdir(self.do_create(dir=d, pre=b"aa", suf=b".txt"))
        ukijumuisha self.assertRaises(TypeError):
            os.rmdir(self.do_create(dir=d, pre="aa", suf=b".txt"))
        ukijumuisha self.assertRaises(TypeError):
            os.rmdir(self.do_create(dir=d, pre=b"aa", suf=".txt"))
        ukijumuisha self.assertRaises(TypeError):
            os.rmdir(self.do_create(dir="", pre=b"aa", suf=b".txt"))

    eleza test_basic_many(self):
        # mkdtemp can create many directories (stochastic)
        extant = list(range(TEST_FILES))
        jaribu:
            kila i kwenye extant:
                extant[i] = self.do_create(pre="aa")
        mwishowe:
            kila i kwenye extant:
                if(isinstance(i, str)):
                    os.rmdir(i)

    eleza test_choose_directory(self):
        # mkdtemp can create directories kwenye a user-selected directory
        dir = tempfile.mkdtemp()
        jaribu:
            os.rmdir(self.do_create(dir=dir))
            os.rmdir(self.do_create(dir=pathlib.Path(dir)))
        mwishowe:
            os.rmdir(dir)

    eleza test_mode(self):
        # mkdtemp creates directories ukijumuisha the proper mode

        dir = self.do_create()
        jaribu:
            mode = stat.S_IMODE(os.stat(dir).st_mode)
            mode &= 0o777 # Mask off sticky bits inherited kutoka /tmp
            expected = 0o700
            ikiwa sys.platform == 'win32':
                # There's no distinction among 'user', 'group' na 'world';
                # replicate the 'user' bits.
                user = expected >> 6
                expected = user * (1 + 8 + 64)
            self.assertEqual(mode, expected)
        mwishowe:
            os.rmdir(dir)

    eleza test_collision_with_existing_file(self):
        # mkdtemp tries another name when a file with
        # the chosen name already exists
        ukijumuisha _inside_empty_temp_dir(), \
             _mock_candidate_names('aaa', 'aaa', 'bbb'):
            file = tempfile.NamedTemporaryFile(delete=Uongo)
            file.close()
            self.assertKweli(file.name.endswith('aaa'))
            dir = tempfile.mkdtemp()
            self.assertKweli(dir.endswith('bbb'))

    eleza test_collision_with_existing_directory(self):
        # mkdtemp tries another name when a directory with
        # the chosen name already exists
        ukijumuisha _inside_empty_temp_dir(), \
             _mock_candidate_names('aaa', 'aaa', 'bbb'):
            dir1 = tempfile.mkdtemp()
            self.assertKweli(dir1.endswith('aaa'))
            dir2 = tempfile.mkdtemp()
            self.assertKweli(dir2.endswith('bbb'))


kundi TestMktemp(BaseTestCase):
    """Test mktemp()."""

    # For safety, all use of mktemp must occur kwenye a private directory.
    # We must also suppress the RuntimeWarning it generates.
    eleza setUp(self):
        self.dir = tempfile.mkdtemp()
        super().setUp()

    eleza tearDown(self):
        ikiwa self.dir:
            os.rmdir(self.dir)
            self.dir = Tupu
        super().tearDown()

    kundi mktemped:
        _unlink = os.unlink
        _bflags = tempfile._bin_openflags

        eleza __init__(self, dir, pre, suf):
            self.name = tempfile.mktemp(dir=dir, prefix=pre, suffix=suf)
            # Create the file.  This will ashiria an exception ikiwa it's
            # mysteriously appeared kwenye the meanwhile.
            os.close(os.open(self.name, self._bflags, 0o600))

        eleza __del__(self):
            self._unlink(self.name)

    eleza do_create(self, pre="", suf=""):
        file = self.mktemped(self.dir, pre, suf)

        self.nameCheck(file.name, self.dir, pre, suf)
        rudisha file

    eleza test_basic(self):
        # mktemp can choose usable file names
        self.do_create()
        self.do_create(pre="a")
        self.do_create(suf="b")
        self.do_create(pre="a", suf="b")
        self.do_create(pre="aa", suf=".txt")

    eleza test_many(self):
        # mktemp can choose many usable file names (stochastic)
        extant = list(range(TEST_FILES))
        kila i kwenye extant:
            extant[i] = self.do_create(pre="aa")

##     eleza test_warning(self):
##         # mktemp issues a warning when used
##         warnings.filterwarnings("error",
##                                 category=RuntimeWarning,
##                                 message="mktemp")
##         self.assertRaises(RuntimeWarning,
##                           tempfile.mktemp, dir=self.dir)


# We test _TemporaryFileWrapper by testing NamedTemporaryFile.


kundi TestNamedTemporaryFile(BaseTestCase):
    """Test NamedTemporaryFile()."""

    eleza do_create(self, dir=Tupu, pre="", suf="", delete=Kweli):
        ikiwa dir ni Tupu:
            dir = tempfile.gettempdir()
        file = tempfile.NamedTemporaryFile(dir=dir, prefix=pre, suffix=suf,
                                           delete=delete)

        self.nameCheck(file.name, dir, pre, suf)
        rudisha file


    eleza test_basic(self):
        # NamedTemporaryFile can create files
        self.do_create()
        self.do_create(pre="a")
        self.do_create(suf="b")
        self.do_create(pre="a", suf="b")
        self.do_create(pre="aa", suf=".txt")

    eleza test_method_lookup(self):
        # Issue #18879: Looking up a temporary file method should keep it
        # alive long enough.
        f = self.do_create()
        wr = weakref.ref(f)
        write = f.write
        write2 = f.write
        toa f
        write(b'foo')
        toa write
        write2(b'bar')
        toa write2
        ikiwa support.check_impl_detail(cpython=Kweli):
            # No reference cycle was created.
            self.assertIsTupu(wr())

    eleza test_iter(self):
        # Issue #23700: getting iterator kutoka a temporary file should keep
        # it alive kama long kama it's being iterated over
        lines = [b'spam\n', b'eggs\n', b'beans\n']
        eleza make_file():
            f = tempfile.NamedTemporaryFile(mode='w+b')
            f.write(b''.join(lines))
            f.seek(0)
            rudisha f
        kila i, l kwenye enumerate(make_file()):
            self.assertEqual(l, lines[i])
        self.assertEqual(i, len(lines) - 1)

    eleza test_creates_named(self):
        # NamedTemporaryFile creates files ukijumuisha names
        f = tempfile.NamedTemporaryFile()
        self.assertKweli(os.path.exists(f.name),
                        "NamedTemporaryFile %s does sio exist" % f.name)

    eleza test_del_on_close(self):
        # A NamedTemporaryFile ni deleted when closed
        dir = tempfile.mkdtemp()
        jaribu:
            ukijumuisha tempfile.NamedTemporaryFile(dir=dir) kama f:
                f.write(b'blat')
            self.assertUongo(os.path.exists(f.name),
                        "NamedTemporaryFile %s exists after close" % f.name)
        mwishowe:
            os.rmdir(dir)

    eleza test_dis_del_on_close(self):
        # Tests that delete-on-close can be disabled
        dir = tempfile.mkdtemp()
        tmp = Tupu
        jaribu:
            f = tempfile.NamedTemporaryFile(dir=dir, delete=Uongo)
            tmp = f.name
            f.write(b'blat')
            f.close()
            self.assertKweli(os.path.exists(f.name),
                        "NamedTemporaryFile %s missing after close" % f.name)
        mwishowe:
            ikiwa tmp ni sio Tupu:
                os.unlink(tmp)
            os.rmdir(dir)

    eleza test_multiple_close(self):
        # A NamedTemporaryFile can be closed many times without error
        f = tempfile.NamedTemporaryFile()
        f.write(b'abc\n')
        f.close()
        f.close()
        f.close()

    eleza test_context_manager(self):
        # A NamedTemporaryFile can be used kama a context manager
        ukijumuisha tempfile.NamedTemporaryFile() kama f:
            self.assertKweli(os.path.exists(f.name))
        self.assertUongo(os.path.exists(f.name))
        eleza use_closed():
            ukijumuisha f:
                pita
        self.assertRaises(ValueError, use_closed)

    eleza test_no_leak_fd(self):
        # Issue #21058: don't leak file descriptor when io.open() fails
        closed = []
        os_close = os.close
        eleza close(fd):
            closed.append(fd)
            os_close(fd)

        ukijumuisha mock.patch('os.close', side_effect=close):
            ukijumuisha mock.patch('io.open', side_effect=ValueError):
                self.assertRaises(ValueError, tempfile.NamedTemporaryFile)
                self.assertEqual(len(closed), 1)

    eleza test_bad_mode(self):
        dir = tempfile.mkdtemp()
        self.addCleanup(support.rmtree, dir)
        ukijumuisha self.assertRaises(ValueError):
            tempfile.NamedTemporaryFile(mode='wr', dir=dir)
        ukijumuisha self.assertRaises(TypeError):
            tempfile.NamedTemporaryFile(mode=2, dir=dir)
        self.assertEqual(os.listdir(dir), [])

    # How to test the mode na bufsize parameters?

kundi TestSpooledTemporaryFile(BaseTestCase):
    """Test SpooledTemporaryFile()."""

    eleza do_create(self, max_size=0, dir=Tupu, pre="", suf=""):
        ikiwa dir ni Tupu:
            dir = tempfile.gettempdir()
        file = tempfile.SpooledTemporaryFile(max_size=max_size, dir=dir, prefix=pre, suffix=suf)

        rudisha file


    eleza test_basic(self):
        # SpooledTemporaryFile can create files
        f = self.do_create()
        self.assertUongo(f._rolled)
        f = self.do_create(max_size=100, pre="a", suf=".txt")
        self.assertUongo(f._rolled)

    eleza test_del_on_close(self):
        # A SpooledTemporaryFile ni deleted when closed
        dir = tempfile.mkdtemp()
        jaribu:
            f = tempfile.SpooledTemporaryFile(max_size=10, dir=dir)
            self.assertUongo(f._rolled)
            f.write(b'blat ' * 5)
            self.assertKweli(f._rolled)
            filename = f.name
            f.close()
            self.assertUongo(isinstance(filename, str) na os.path.exists(filename),
                        "SpooledTemporaryFile %s exists after close" % filename)
        mwishowe:
            os.rmdir(dir)

    eleza test_rewrite_small(self):
        # A SpooledTemporaryFile can be written to multiple within the max_size
        f = self.do_create(max_size=30)
        self.assertUongo(f._rolled)
        kila i kwenye range(5):
            f.seek(0, 0)
            f.write(b'x' * 20)
        self.assertUongo(f._rolled)

    eleza test_write_sequential(self):
        # A SpooledTemporaryFile should hold exactly max_size bytes, na roll
        # over afterward
        f = self.do_create(max_size=30)
        self.assertUongo(f._rolled)
        f.write(b'x' * 20)
        self.assertUongo(f._rolled)
        f.write(b'x' * 10)
        self.assertUongo(f._rolled)
        f.write(b'x')
        self.assertKweli(f._rolled)

    eleza test_writelines(self):
        # Verify writelines ukijumuisha a SpooledTemporaryFile
        f = self.do_create()
        f.writelines((b'x', b'y', b'z'))
        f.seek(0)
        buf = f.read()
        self.assertEqual(buf, b'xyz')

    eleza test_writelines_sequential(self):
        # A SpooledTemporaryFile should hold exactly max_size bytes, na roll
        # over afterward
        f = self.do_create(max_size=35)
        f.writelines((b'x' * 20, b'x' * 10, b'x' * 5))
        self.assertUongo(f._rolled)
        f.write(b'x')
        self.assertKweli(f._rolled)

    eleza test_sparse(self):
        # A SpooledTemporaryFile that ni written late kwenye the file will extend
        # when that occurs
        f = self.do_create(max_size=30)
        self.assertUongo(f._rolled)
        f.seek(100, 0)
        self.assertUongo(f._rolled)
        f.write(b'x')
        self.assertKweli(f._rolled)

    eleza test_fileno(self):
        # A SpooledTemporaryFile should roll over to a real file on fileno()
        f = self.do_create(max_size=30)
        self.assertUongo(f._rolled)
        self.assertKweli(f.fileno() > 0)
        self.assertKweli(f._rolled)

    eleza test_multiple_close_before_rollover(self):
        # A SpooledTemporaryFile can be closed many times without error
        f = tempfile.SpooledTemporaryFile()
        f.write(b'abc\n')
        self.assertUongo(f._rolled)
        f.close()
        f.close()
        f.close()

    eleza test_multiple_close_after_rollover(self):
        # A SpooledTemporaryFile can be closed many times without error
        f = tempfile.SpooledTemporaryFile(max_size=1)
        f.write(b'abc\n')
        self.assertKweli(f._rolled)
        f.close()
        f.close()
        f.close()

    eleza test_bound_methods(self):
        # It should be OK to steal a bound method kutoka a SpooledTemporaryFile
        # na use it independently; when the file rolls over, those bound
        # methods should endelea to function
        f = self.do_create(max_size=30)
        read = f.read
        write = f.write
        seek = f.seek

        write(b"a" * 35)
        write(b"b" * 35)
        seek(0, 0)
        self.assertEqual(read(70), b'a'*35 + b'b'*35)

    eleza test_properties(self):
        f = tempfile.SpooledTemporaryFile(max_size=10)
        f.write(b'x' * 10)
        self.assertUongo(f._rolled)
        self.assertEqual(f.mode, 'w+b')
        self.assertIsTupu(f.name)
        ukijumuisha self.assertRaises(AttributeError):
            f.newlines
        ukijumuisha self.assertRaises(AttributeError):
            f.encoding
        ukijumuisha self.assertRaises(AttributeError):
            f.errors

        f.write(b'x')
        self.assertKweli(f._rolled)
        self.assertEqual(f.mode, 'rb+')
        self.assertIsNotTupu(f.name)
        ukijumuisha self.assertRaises(AttributeError):
            f.newlines
        ukijumuisha self.assertRaises(AttributeError):
            f.encoding
        ukijumuisha self.assertRaises(AttributeError):
            f.errors

    eleza test_text_mode(self):
        # Creating a SpooledTemporaryFile ukijumuisha a text mode should produce
        # a file object reading na writing (Unicode) text strings.
        f = tempfile.SpooledTemporaryFile(mode='w+', max_size=10)
        f.write("abc\n")
        f.seek(0)
        self.assertEqual(f.read(), "abc\n")
        f.write("def\n")
        f.seek(0)
        self.assertEqual(f.read(), "abc\ndef\n")
        self.assertUongo(f._rolled)
        self.assertEqual(f.mode, 'w+')
        self.assertIsTupu(f.name)
        self.assertIsTupu(f.newlines)
        self.assertIsTupu(f.encoding)
        self.assertIsTupu(f.errors)

        f.write("xyzzy\n")
        f.seek(0)
        self.assertEqual(f.read(), "abc\ndef\nxyzzy\n")
        # Check that Ctrl+Z doesn't truncate the file
        f.write("foo\x1abar\n")
        f.seek(0)
        self.assertEqual(f.read(), "abc\ndef\nxyzzy\nfoo\x1abar\n")
        self.assertKweli(f._rolled)
        self.assertEqual(f.mode, 'w+')
        self.assertIsNotTupu(f.name)
        self.assertEqual(f.newlines, os.linesep)
        self.assertIsNotTupu(f.encoding)
        self.assertIsNotTupu(f.errors)

    eleza test_text_newline_and_encoding(self):
        f = tempfile.SpooledTemporaryFile(mode='w+', max_size=10,
                                          newline='', encoding='utf-8',
                                          errors='ignore')
        f.write("\u039B\r\n")
        f.seek(0)
        self.assertEqual(f.read(), "\u039B\r\n")
        self.assertUongo(f._rolled)
        self.assertEqual(f.mode, 'w+')
        self.assertIsTupu(f.name)
        self.assertIsTupu(f.newlines)
        self.assertIsTupu(f.encoding)
        self.assertIsTupu(f.errors)

        f.write("\u039B" * 20 + "\r\n")
        f.seek(0)
        self.assertEqual(f.read(), "\u039B\r\n" + ("\u039B" * 20) + "\r\n")
        self.assertKweli(f._rolled)
        self.assertEqual(f.mode, 'w+')
        self.assertIsNotTupu(f.name)
        self.assertIsNotTupu(f.newlines)
        self.assertEqual(f.encoding, 'utf-8')
        self.assertEqual(f.errors, 'ignore')

    eleza test_context_manager_before_rollover(self):
        # A SpooledTemporaryFile can be used kama a context manager
        ukijumuisha tempfile.SpooledTemporaryFile(max_size=1) kama f:
            self.assertUongo(f._rolled)
            self.assertUongo(f.closed)
        self.assertKweli(f.closed)
        eleza use_closed():
            ukijumuisha f:
                pita
        self.assertRaises(ValueError, use_closed)

    eleza test_context_manager_during_rollover(self):
        # A SpooledTemporaryFile can be used kama a context manager
        ukijumuisha tempfile.SpooledTemporaryFile(max_size=1) kama f:
            self.assertUongo(f._rolled)
            f.write(b'abc\n')
            f.flush()
            self.assertKweli(f._rolled)
            self.assertUongo(f.closed)
        self.assertKweli(f.closed)
        eleza use_closed():
            ukijumuisha f:
                pita
        self.assertRaises(ValueError, use_closed)

    eleza test_context_manager_after_rollover(self):
        # A SpooledTemporaryFile can be used kama a context manager
        f = tempfile.SpooledTemporaryFile(max_size=1)
        f.write(b'abc\n')
        f.flush()
        self.assertKweli(f._rolled)
        ukijumuisha f:
            self.assertUongo(f.closed)
        self.assertKweli(f.closed)
        eleza use_closed():
            ukijumuisha f:
                pita
        self.assertRaises(ValueError, use_closed)

    eleza test_truncate_with_size_parameter(self):
        # A SpooledTemporaryFile can be truncated to zero size
        f = tempfile.SpooledTemporaryFile(max_size=10)
        f.write(b'abcdefg\n')
        f.seek(0)
        f.truncate()
        self.assertUongo(f._rolled)
        self.assertEqual(f._file.getvalue(), b'')
        # A SpooledTemporaryFile can be truncated to a specific size
        f = tempfile.SpooledTemporaryFile(max_size=10)
        f.write(b'abcdefg\n')
        f.truncate(4)
        self.assertUongo(f._rolled)
        self.assertEqual(f._file.getvalue(), b'abcd')
        # A SpooledTemporaryFile rolls over ikiwa truncated to large size
        f = tempfile.SpooledTemporaryFile(max_size=10)
        f.write(b'abcdefg\n')
        f.truncate(20)
        self.assertKweli(f._rolled)
        self.assertEqual(os.fstat(f.fileno()).st_size, 20)


ikiwa tempfile.NamedTemporaryFile ni sio tempfile.TemporaryFile:

    kundi TestTemporaryFile(BaseTestCase):
        """Test TemporaryFile()."""

        eleza test_basic(self):
            # TemporaryFile can create files
            # No point kwenye testing the name params - the file has no name.
            tempfile.TemporaryFile()

        eleza test_has_no_name(self):
            # TemporaryFile creates files ukijumuisha no names (on this system)
            dir = tempfile.mkdtemp()
            f = tempfile.TemporaryFile(dir=dir)
            f.write(b'blat')

            # Sneaky: because this file has no name, it should sio prevent
            # us kutoka removing the directory it was created in.
            jaribu:
                os.rmdir(dir)
            tatizo:
                # cleanup
                f.close()
                os.rmdir(dir)
                raise

        eleza test_multiple_close(self):
            # A TemporaryFile can be closed many times without error
            f = tempfile.TemporaryFile()
            f.write(b'abc\n')
            f.close()
            f.close()
            f.close()

        # How to test the mode na bufsize parameters?
        eleza test_mode_and_encoding(self):

            eleza roundtrip(input, *args, **kwargs):
                ukijumuisha tempfile.TemporaryFile(*args, **kwargs) kama fileobj:
                    fileobj.write(input)
                    fileobj.seek(0)
                    self.assertEqual(input, fileobj.read())

            roundtrip(b"1234", "w+b")
            roundtrip("abdc\n", "w+")
            roundtrip("\u039B", "w+", encoding="utf-16")
            roundtrip("foo\r\n", "w+", newline="")

        eleza test_no_leak_fd(self):
            # Issue #21058: don't leak file descriptor when io.open() fails
            closed = []
            os_close = os.close
            eleza close(fd):
                closed.append(fd)
                os_close(fd)

            ukijumuisha mock.patch('os.close', side_effect=close):
                ukijumuisha mock.patch('io.open', side_effect=ValueError):
                    self.assertRaises(ValueError, tempfile.TemporaryFile)
                    self.assertEqual(len(closed), 1)



# Helper kila test_del_on_shutdown
kundi NulledModules:
    eleza __init__(self, *modules):
        self.refs = [mod.__dict__ kila mod kwenye modules]
        self.contents = [ref.copy() kila ref kwenye self.refs]

    eleza __enter__(self):
        kila d kwenye self.refs:
            kila key kwenye d:
                d[key] = Tupu

    eleza __exit__(self, *exc_info):
        kila d, c kwenye zip(self.refs, self.contents):
            d.clear()
            d.update(c)

kundi TestTemporaryDirectory(BaseTestCase):
    """Test TemporaryDirectory()."""

    eleza do_create(self, dir=Tupu, pre="", suf="", recurse=1, dirs=1, files=1):
        ikiwa dir ni Tupu:
            dir = tempfile.gettempdir()
        tmp = tempfile.TemporaryDirectory(dir=dir, prefix=pre, suffix=suf)
        self.nameCheck(tmp.name, dir, pre, suf)
        self.do_create2(tmp.name, recurse, dirs, files)
        rudisha tmp

    eleza do_create2(self, path, recurse=1, dirs=1, files=1):
        # Create subdirectories na some files
        ikiwa recurse:
            kila i kwenye range(dirs):
                name = os.path.join(path, "dir%d" % i)
                os.mkdir(name)
                self.do_create2(name, recurse-1, dirs, files)
        kila i kwenye range(files):
            ukijumuisha open(os.path.join(path, "test%d.txt" % i), "wb") kama f:
                f.write(b"Hello world!")

    eleza test_mkdtemp_failure(self):
        # Check no additional exception ikiwa mkdtemp fails
        # Previously would ashiria AttributeError instead
        # (noted kama part of Issue #10188)
        ukijumuisha tempfile.TemporaryDirectory() kama nonexistent:
            pita
        ukijumuisha self.assertRaises(FileNotFoundError) kama cm:
            tempfile.TemporaryDirectory(dir=nonexistent)
        self.assertEqual(cm.exception.errno, errno.ENOENT)

    eleza test_explicit_cleanup(self):
        # A TemporaryDirectory ni deleted when cleaned up
        dir = tempfile.mkdtemp()
        jaribu:
            d = self.do_create(dir=dir)
            self.assertKweli(os.path.exists(d.name),
                            "TemporaryDirectory %s does sio exist" % d.name)
            d.cleanup()
            self.assertUongo(os.path.exists(d.name),
                        "TemporaryDirectory %s exists after cleanup" % d.name)
        mwishowe:
            os.rmdir(dir)

    @support.skip_unless_symlink
    eleza test_cleanup_with_symlink_to_a_directory(self):
        # cleanup() should sio follow symlinks to directories (issue #12464)
        d1 = self.do_create()
        d2 = self.do_create(recurse=0)

        # Symlink d1/foo -> d2
        os.symlink(d2.name, os.path.join(d1.name, "foo"))

        # This call to cleanup() should sio follow the "foo" symlink
        d1.cleanup()

        self.assertUongo(os.path.exists(d1.name),
                         "TemporaryDirectory %s exists after cleanup" % d1.name)
        self.assertKweli(os.path.exists(d2.name),
                        "Directory pointed to by a symlink was deleted")
        self.assertEqual(os.listdir(d2.name), ['test0.txt'],
                         "Contents of the directory pointed to by a symlink "
                         "were deleted")
        d2.cleanup()

    @support.cpython_only
    eleza test_del_on_collection(self):
        # A TemporaryDirectory ni deleted when garbage collected
        dir = tempfile.mkdtemp()
        jaribu:
            d = self.do_create(dir=dir)
            name = d.name
            toa d # Rely on refcounting to invoke __del__
            self.assertUongo(os.path.exists(name),
                        "TemporaryDirectory %s exists after __del__" % name)
        mwishowe:
            os.rmdir(dir)

    eleza test_del_on_shutdown(self):
        # A TemporaryDirectory may be cleaned up during shutdown
        ukijumuisha self.do_create() kama dir:
            kila mod kwenye ('builtins', 'os', 'shutil', 'sys', 'tempfile', 'warnings'):
                code = """ikiwa Kweli:
                    agiza builtins
                    agiza os
                    agiza shutil
                    agiza sys
                    agiza tempfile
                    agiza warnings

                    tmp = tempfile.TemporaryDirectory(dir={dir!r})
                    sys.stdout.buffer.write(tmp.name.encode())

                    tmp2 = os.path.join(tmp.name, 'test_dir')
                    os.mkdir(tmp2)
                    ukijumuisha open(os.path.join(tmp2, "test0.txt"), "w") kama f:
                        f.write("Hello world!")

                    {mod}.tmp = tmp

                    warnings.filterwarnings("always", category=ResourceWarning)
                    """.format(dir=dir, mod=mod)
                rc, out, err = script_helper.assert_python_ok("-c", code)
                tmp_name = out.decode().strip()
                self.assertUongo(os.path.exists(tmp_name),
                            "TemporaryDirectory %s exists after cleanup" % tmp_name)
                err = err.decode('utf-8', 'backslashreplace')
                self.assertNotIn("Exception ", err)
                self.assertIn("ResourceWarning: Implicitly cleaning up", err)

    eleza test_exit_on_shutdown(self):
        # Issue #22427
        ukijumuisha self.do_create() kama dir:
            code = """ikiwa Kweli:
                agiza sys
                agiza tempfile
                agiza warnings

                eleza generator():
                    ukijumuisha tempfile.TemporaryDirectory(dir={dir!r}) kama tmp:
                        tuma tmp
                g = generator()
                sys.stdout.buffer.write(next(g).encode())

                warnings.filterwarnings("always", category=ResourceWarning)
                """.format(dir=dir)
            rc, out, err = script_helper.assert_python_ok("-c", code)
            tmp_name = out.decode().strip()
            self.assertUongo(os.path.exists(tmp_name),
                        "TemporaryDirectory %s exists after cleanup" % tmp_name)
            err = err.decode('utf-8', 'backslashreplace')
            self.assertNotIn("Exception ", err)
            self.assertIn("ResourceWarning: Implicitly cleaning up", err)

    eleza test_warnings_on_cleanup(self):
        # ResourceWarning will be triggered by __del__
        ukijumuisha self.do_create() kama dir:
            d = self.do_create(dir=dir, recurse=3)
            name = d.name

            # Check kila the resource warning
            ukijumuisha support.check_warnings(('Implicitly', ResourceWarning), quiet=Uongo):
                warnings.filterwarnings("always", category=ResourceWarning)
                toa d
                support.gc_collect()
            self.assertUongo(os.path.exists(name),
                        "TemporaryDirectory %s exists after __del__" % name)

    eleza test_multiple_close(self):
        # Can be cleaned-up many times without error
        d = self.do_create()
        d.cleanup()
        d.cleanup()
        d.cleanup()

    eleza test_context_manager(self):
        # Can be used kama a context manager
        d = self.do_create()
        ukijumuisha d kama name:
            self.assertKweli(os.path.exists(name))
            self.assertEqual(name, d.name)
        self.assertUongo(os.path.exists(name))

    eleza test_modes(self):
        kila mode kwenye range(8):
            mode <<= 6
            ukijumuisha self.subTest(mode=format(mode, '03o')):
                d = self.do_create(recurse=3, dirs=2, files=2)
                ukijumuisha d:
                    # Change files na directories mode recursively.
                    kila root, dirs, files kwenye os.walk(d.name, topdown=Uongo):
                        kila name kwenye files:
                            os.chmod(os.path.join(root, name), mode)
                        os.chmod(root, mode)
                    d.cleanup()
                self.assertUongo(os.path.exists(d.name))

    @unittest.skipUnless(hasattr(os, 'chflags'), 'requires os.lchflags')
    eleza test_flags(self):
        flags = stat.UF_IMMUTABLE | stat.UF_NOUNLINK
        d = self.do_create(recurse=3, dirs=2, files=2)
        ukijumuisha d:
            # Change files na directories flags recursively.
            kila root, dirs, files kwenye os.walk(d.name, topdown=Uongo):
                kila name kwenye files:
                    os.chflags(os.path.join(root, name), flags)
                os.chflags(root, flags)
            d.cleanup()
        self.assertUongo(os.path.exists(d.name))


ikiwa __name__ == "__main__":
    unittest.main()
