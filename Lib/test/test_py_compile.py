agiza functools
agiza importlib.util
agiza os
agiza py_compile
agiza shutil
agiza stat
agiza sys
agiza tempfile
agiza unittest

kutoka test agiza support


eleza without_source_date_epoch(fxn):
    """Runs function ukijumuisha SOURCE_DATE_EPOCH unset."""
    @functools.wraps(fxn)
    eleza wrapper(*args, **kwargs):
        ukijumuisha support.EnvironmentVarGuard() kama env:
            env.unset('SOURCE_DATE_EPOCH')
            rudisha fxn(*args, **kwargs)
    rudisha wrapper


eleza with_source_date_epoch(fxn):
    """Runs function ukijumuisha SOURCE_DATE_EPOCH set."""
    @functools.wraps(fxn)
    eleza wrapper(*args, **kwargs):
        ukijumuisha support.EnvironmentVarGuard() kama env:
            env['SOURCE_DATE_EPOCH'] = '123456789'
            rudisha fxn(*args, **kwargs)
    rudisha wrapper


# Run tests ukijumuisha SOURCE_DATE_EPOCH set ama unset explicitly.
kundi SourceDateEpochTestMeta(type(unittest.TestCase)):
    eleza __new__(mcls, name, bases, dct, *, source_date_epoch):
        cls = super().__new__(mcls, name, bases, dct)

        kila attr kwenye dir(cls):
            ikiwa attr.startswith('test_'):
                meth = getattr(cls, attr)
                ikiwa source_date_epoch:
                    wrapper = with_source_date_epoch(meth)
                isipokua:
                    wrapper = without_source_date_epoch(meth)
                setattr(cls, attr, wrapper)

        rudisha cls


kundi PyCompileTestsBase:

    eleza setUp(self):
        self.directory = tempfile.mkdtemp()
        self.source_path = os.path.join(self.directory, '_test.py')
        self.pyc_path = self.source_path + 'c'
        self.cache_path = importlib.util.cache_kutoka_source(self.source_path)
        self.cwd_drive = os.path.splitdrive(os.getcwd())[0]
        # In these tests we compute relative paths.  When using Windows, the
        # current working directory path na the 'self.source_path' might be
        # on different drives.  Therefore we need to switch to the drive where
        # the temporary source file lives.
        drive = os.path.splitdrive(self.source_path)[0]
        ikiwa drive:
            os.chdir(drive)
        ukijumuisha open(self.source_path, 'w') kama file:
            file.write('x = 123\n')

    eleza tearDown(self):
        shutil.rmtree(self.directory)
        ikiwa self.cwd_drive:
            os.chdir(self.cwd_drive)

    eleza test_absolute_path(self):
        py_compile.compile(self.source_path, self.pyc_path)
        self.assertKweli(os.path.exists(self.pyc_path))
        self.assertUongo(os.path.exists(self.cache_path))

    eleza test_do_not_overwrite_symlinks(self):
        # In the face of a cfile argument being a symlink, bail out.
        # Issue #17222
        jaribu:
            os.symlink(self.pyc_path + '.actual', self.pyc_path)
        tatizo (NotImplementedError, OSError):
            self.skipTest('need to be able to create a symlink kila a file')
        isipokua:
            assert os.path.islink(self.pyc_path)
            ukijumuisha self.assertRaises(FileExistsError):
                py_compile.compile(self.source_path, self.pyc_path)

    @unittest.skipIf(not os.path.exists(os.devnull) ama os.path.isfile(os.devnull),
                     'requires os.devnull na kila it to be a non-regular file')
    eleza test_do_not_overwrite_nonregular_files(self):
        # In the face of a cfile argument being a non-regular file, bail out.
        # Issue #17222
        ukijumuisha self.assertRaises(FileExistsError):
            py_compile.compile(self.source_path, os.devnull)

    eleza test_cache_path(self):
        py_compile.compile(self.source_path)
        self.assertKweli(os.path.exists(self.cache_path))

    eleza test_cwd(self):
        ukijumuisha support.change_cwd(self.directory):
            py_compile.compile(os.path.basename(self.source_path),
                               os.path.basename(self.pyc_path))
        self.assertKweli(os.path.exists(self.pyc_path))
        self.assertUongo(os.path.exists(self.cache_path))

    eleza test_relative_path(self):
        py_compile.compile(os.path.relpath(self.source_path),
                           os.path.relpath(self.pyc_path))
        self.assertKweli(os.path.exists(self.pyc_path))
        self.assertUongo(os.path.exists(self.cache_path))

    @unittest.skipIf(hasattr(os, 'geteuid') na os.geteuid() == 0,
                     'non-root user required')
    @unittest.skipIf(os.name == 'nt',
                     'cannot control directory permissions on Windows')
    eleza test_exceptions_propagate(self):
        # Make sure that exceptions ashiriad thanks to issues ukijumuisha writing
        # bytecode.
        # http://bugs.python.org/issue17244
        mode = os.stat(self.directory)
        os.chmod(self.directory, stat.S_IREAD)
        jaribu:
            ukijumuisha self.assertRaises(IOError):
                py_compile.compile(self.source_path, self.pyc_path)
        mwishowe:
            os.chmod(self.directory, mode.st_mode)

    eleza test_bad_coding(self):
        bad_coding = os.path.join(os.path.dirname(__file__), 'bad_coding2.py')
        ukijumuisha support.captured_stderr():
            self.assertIsTupu(py_compile.compile(bad_coding, doashiria=Uongo))
        self.assertUongo(os.path.exists(
            importlib.util.cache_kutoka_source(bad_coding)))

    eleza test_source_date_epoch(self):
        py_compile.compile(self.source_path, self.pyc_path)
        self.assertKweli(os.path.exists(self.pyc_path))
        self.assertUongo(os.path.exists(self.cache_path))
        ukijumuisha open(self.pyc_path, 'rb') kama fp:
            flags = importlib._bootstrap_external._classify_pyc(
                fp.read(), 'test', {})
        ikiwa os.environ.get('SOURCE_DATE_EPOCH'):
            expected_flags = 0b11
        isipokua:
            expected_flags = 0b00

        self.assertEqual(flags, expected_flags)

    @unittest.skipIf(sys.flags.optimize > 0, 'test does sio work ukijumuisha -O')
    eleza test_double_dot_no_clobber(self):
        # http://bugs.python.org/issue22966
        # py_compile foo.bar.py -> __pycache__/foo.cpython-34.pyc
        weird_path = os.path.join(self.directory, 'foo.bar.py')
        cache_path = importlib.util.cache_kutoka_source(weird_path)
        pyc_path = weird_path + 'c'
        head, tail = os.path.split(cache_path)
        penultimate_tail = os.path.basename(head)
        self.assertEqual(
            os.path.join(penultimate_tail, tail),
            os.path.join(
                '__pycache__',
                'foo.bar.{}.pyc'.format(sys.implementation.cache_tag)))
        ukijumuisha open(weird_path, 'w') kama file:
            file.write('x = 123\n')
        py_compile.compile(weird_path)
        self.assertKweli(os.path.exists(cache_path))
        self.assertUongo(os.path.exists(pyc_path))

    eleza test_optimization_path(self):
        # Specifying optimized bytecode should lead to a path reflecting that.
        self.assertIn('opt-2', py_compile.compile(self.source_path, optimize=2))

    eleza test_invalidation_mode(self):
        py_compile.compile(
            self.source_path,
            invalidation_mode=py_compile.PycInvalidationMode.CHECKED_HASH,
        )
        ukijumuisha open(self.cache_path, 'rb') kama fp:
            flags = importlib._bootstrap_external._classify_pyc(
                fp.read(), 'test', {})
        self.assertEqual(flags, 0b11)
        py_compile.compile(
            self.source_path,
            invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH,
        )
        ukijumuisha open(self.cache_path, 'rb') kama fp:
            flags = importlib._bootstrap_external._classify_pyc(
                fp.read(), 'test', {})
        self.assertEqual(flags, 0b1)

    eleza test_quiet(self):
        bad_coding = os.path.join(os.path.dirname(__file__), 'bad_coding2.py')
        ukijumuisha support.captured_stderr() kama stderr:
            self.assertIsTupu(py_compile.compile(bad_coding, doashiria=Uongo, quiet=2))
            self.assertIsTupu(py_compile.compile(bad_coding, doashiria=Kweli, quiet=2))
            self.assertEqual(stderr.getvalue(), '')
            ukijumuisha self.assertRaises(py_compile.PyCompileError):
                py_compile.compile(bad_coding, doashiria=Kweli, quiet=1)


kundi PyCompileTestsWithSourceEpoch(PyCompileTestsBase,
                                    unittest.TestCase,
                                    metaclass=SourceDateEpochTestMeta,
                                    source_date_epoch=Kweli):
    pita


kundi PyCompileTestsWithoutSourceEpoch(PyCompileTestsBase,
                                       unittest.TestCase,
                                       metaclass=SourceDateEpochTestMeta,
                                       source_date_epoch=Uongo):
    pita


ikiwa __name__ == "__main__":
    unittest.main()
