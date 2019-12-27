agiza contextlib
agiza errno
agiza importlib
agiza io
agiza os
agiza shutil
agiza socket
agiza stat
agiza subprocess
agiza sys
agiza tempfile
agiza textwrap
agiza time
agiza unittest
kutoka test agiza support
kutoka test.support agiza script_helper

TESTFN = support.TESTFN


kundi TestSupport(unittest.TestCase):

    eleza test_import_module(self):
        support.import_module("ftplib")
        self.assertRaises(unittest.SkipTest, support.import_module, "foo")

    eleza test_import_fresh_module(self):
        support.import_fresh_module("ftplib")

    eleza test_get_attribute(self):
        self.assertEqual(support.get_attribute(self, "test_get_attribute"),
                        self.test_get_attribute)
        self.assertRaises(unittest.SkipTest, support.get_attribute, self, "foo")

    @unittest.skip("failing buildbots")
    eleza test_get_original_stdout(self):
        self.assertEqual(support.get_original_stdout(), sys.stdout)

    eleza test_unload(self):
        agiza sched
        self.assertIn("sched", sys.modules)
        support.unload("sched")
        self.assertNotIn("sched", sys.modules)

    eleza test_unlink(self):
        with open(TESTFN, "w") as f:
            pass
        support.unlink(TESTFN)
        self.assertFalse(os.path.exists(TESTFN))
        support.unlink(TESTFN)

    eleza test_rmtree(self):
        dirpath = support.TESTFN + 'd'
        subdirpath = os.path.join(dirpath, 'subdir')
        os.mkdir(dirpath)
        os.mkdir(subdirpath)
        support.rmtree(dirpath)
        self.assertFalse(os.path.exists(dirpath))
        with support.swap_attr(support, 'verbose', 0):
            support.rmtree(dirpath)

        os.mkdir(dirpath)
        os.mkdir(subdirpath)
        os.chmod(dirpath, stat.S_IRUSR|stat.S_IXUSR)
        with support.swap_attr(support, 'verbose', 0):
            support.rmtree(dirpath)
        self.assertFalse(os.path.exists(dirpath))

        os.mkdir(dirpath)
        os.mkdir(subdirpath)
        os.chmod(dirpath, 0)
        with support.swap_attr(support, 'verbose', 0):
            support.rmtree(dirpath)
        self.assertFalse(os.path.exists(dirpath))

    eleza test_forget(self):
        mod_filename = TESTFN + '.py'
        with open(mod_filename, 'w') as f:
            andika('foo = 1', file=f)
        sys.path.insert(0, os.curdir)
        importlib.invalidate_caches()
        try:
            mod = __import__(TESTFN)
            self.assertIn(TESTFN, sys.modules)

            support.forget(TESTFN)
            self.assertNotIn(TESTFN, sys.modules)
        finally:
            del sys.path[0]
            support.unlink(mod_filename)
            support.rmtree('__pycache__')

    eleza test_HOST(self):
        s = socket.create_server((support.HOST, 0))
        s.close()

    eleza test_find_unused_port(self):
        port = support.find_unused_port()
        s = socket.create_server((support.HOST, port))
        s.close()

    eleza test_bind_port(self):
        s = socket.socket()
        support.bind_port(s)
        s.listen()
        s.close()

    # Tests for temp_dir()

    eleza test_temp_dir(self):
        """Test that temp_dir() creates and destroys its directory."""
        parent_dir = tempfile.mkdtemp()
        parent_dir = os.path.realpath(parent_dir)

        try:
            path = os.path.join(parent_dir, 'temp')
            self.assertFalse(os.path.isdir(path))
            with support.temp_dir(path) as temp_path:
                self.assertEqual(temp_path, path)
                self.assertTrue(os.path.isdir(path))
            self.assertFalse(os.path.isdir(path))
        finally:
            support.rmtree(parent_dir)

    eleza test_temp_dir__path_none(self):
        """Test passing no path."""
        with support.temp_dir() as temp_path:
            self.assertTrue(os.path.isdir(temp_path))
        self.assertFalse(os.path.isdir(temp_path))

    eleza test_temp_dir__existing_dir__quiet_default(self):
        """Test passing a directory that already exists."""
        eleza call_temp_dir(path):
            with support.temp_dir(path) as temp_path:
                raise Exception("should not get here")

        path = tempfile.mkdtemp()
        path = os.path.realpath(path)
        try:
            self.assertTrue(os.path.isdir(path))
            self.assertRaises(FileExistsError, call_temp_dir, path)
            # Make sure temp_dir did not delete the original directory.
            self.assertTrue(os.path.isdir(path))
        finally:
            shutil.rmtree(path)

    eleza test_temp_dir__existing_dir__quiet_true(self):
        """Test passing a directory that already exists with quiet=True."""
        path = tempfile.mkdtemp()
        path = os.path.realpath(path)

        try:
            with support.check_warnings() as recorder:
                with support.temp_dir(path, quiet=True) as temp_path:
                    self.assertEqual(path, temp_path)
                warnings = [str(w.message) for w in recorder.warnings]
            # Make sure temp_dir did not delete the original directory.
            self.assertTrue(os.path.isdir(path))
        finally:
            shutil.rmtree(path)

        self.assertEqual(len(warnings), 1, warnings)
        warn = warnings[0]
        self.assertTrue(warn.startswith(f'tests may fail, unable to create '
                                        f'temporary directory {path!r}: '),
                        warn)

    @unittest.skipUnless(hasattr(os, "fork"), "test requires os.fork")
    eleza test_temp_dir__forked_child(self):
        """Test that a forked child process does not remove the directory."""
        # See bpo-30028 for details.
        # Run the test as an external script, because it uses fork.
        script_helper.assert_python_ok("-c", textwrap.dedent("""
            agiza os
            kutoka test agiza support
            with support.temp_cwd() as temp_path:
                pid = os.fork()
                ikiwa pid != 0:
                    # parent process (child has pid == 0)

                    # wait for the child to terminate
                    (pid, status) = os.waitpid(pid, 0)
                    ikiwa status != 0:
                        raise AssertionError(f"Child process failed with exit "
                                             f"status indication 0x{status:x}.")

                    # Make sure that temp_path is still present. When the child
                    # process leaves the 'temp_cwd'-context, the __exit__()-
                    # method of the context must not remove the temporary
                    # directory.
                    ikiwa not os.path.isdir(temp_path):
                        raise AssertionError("Child removed temp_path.")
        """))

    # Tests for change_cwd()

    eleza test_change_cwd(self):
        original_cwd = os.getcwd()

        with support.temp_dir() as temp_path:
            with support.change_cwd(temp_path) as new_cwd:
                self.assertEqual(new_cwd, temp_path)
                self.assertEqual(os.getcwd(), new_cwd)

        self.assertEqual(os.getcwd(), original_cwd)

    eleza test_change_cwd__non_existent_dir(self):
        """Test passing a non-existent directory."""
        original_cwd = os.getcwd()

        eleza call_change_cwd(path):
            with support.change_cwd(path) as new_cwd:
                raise Exception("should not get here")

        with support.temp_dir() as parent_dir:
            non_existent_dir = os.path.join(parent_dir, 'does_not_exist')
            self.assertRaises(FileNotFoundError, call_change_cwd,
                              non_existent_dir)

        self.assertEqual(os.getcwd(), original_cwd)

    eleza test_change_cwd__non_existent_dir__quiet_true(self):
        """Test passing a non-existent directory with quiet=True."""
        original_cwd = os.getcwd()

        with support.temp_dir() as parent_dir:
            bad_dir = os.path.join(parent_dir, 'does_not_exist')
            with support.check_warnings() as recorder:
                with support.change_cwd(bad_dir, quiet=True) as new_cwd:
                    self.assertEqual(new_cwd, original_cwd)
                    self.assertEqual(os.getcwd(), new_cwd)
                warnings = [str(w.message) for w in recorder.warnings]

        self.assertEqual(len(warnings), 1, warnings)
        warn = warnings[0]
        self.assertTrue(warn.startswith(f'tests may fail, unable to change '
                                        f'the current working directory '
                                        f'to {bad_dir!r}: '),
                        warn)

    # Tests for change_cwd()

    eleza test_change_cwd__chdir_warning(self):
        """Check the warning message when os.chdir() fails."""
        path = TESTFN + '_does_not_exist'
        with support.check_warnings() as recorder:
            with support.change_cwd(path=path, quiet=True):
                pass
            messages = [str(w.message) for w in recorder.warnings]

        self.assertEqual(len(messages), 1, messages)
        msg = messages[0]
        self.assertTrue(msg.startswith(f'tests may fail, unable to change '
                                       f'the current working directory '
                                       f'to {path!r}: '),
                        msg)

    # Tests for temp_cwd()

    eleza test_temp_cwd(self):
        here = os.getcwd()
        with support.temp_cwd(name=TESTFN):
            self.assertEqual(os.path.basename(os.getcwd()), TESTFN)
        self.assertFalse(os.path.exists(TESTFN))
        self.assertEqual(os.getcwd(), here)


    eleza test_temp_cwd__name_none(self):
        """Test passing None to temp_cwd()."""
        original_cwd = os.getcwd()
        with support.temp_cwd(name=None) as new_cwd:
            self.assertNotEqual(new_cwd, original_cwd)
            self.assertTrue(os.path.isdir(new_cwd))
            self.assertEqual(os.getcwd(), new_cwd)
        self.assertEqual(os.getcwd(), original_cwd)

    eleza test_sortdict(self):
        self.assertEqual(support.sortdict({3:3, 2:2, 1:1}), "{1: 1, 2: 2, 3: 3}")

    eleza test_make_bad_fd(self):
        fd = support.make_bad_fd()
        with self.assertRaises(OSError) as cm:
            os.write(fd, b"foo")
        self.assertEqual(cm.exception.errno, errno.EBADF)

    eleza test_check_syntax_error(self):
        support.check_syntax_error(self, "eleza class", lineno=1, offset=5)
        with self.assertRaises(AssertionError):
            support.check_syntax_error(self, "x=1")

    eleza test_CleanImport(self):
        agiza importlib
        with support.CleanImport("asyncore"):
            importlib.import_module("asyncore")

    eleza test_DirsOnSysPath(self):
        with support.DirsOnSysPath('foo', 'bar'):
            self.assertIn("foo", sys.path)
            self.assertIn("bar", sys.path)
        self.assertNotIn("foo", sys.path)
        self.assertNotIn("bar", sys.path)

    eleza test_captured_stdout(self):
        with support.captured_stdout() as stdout:
            andika("hello")
        self.assertEqual(stdout.getvalue(), "hello\n")

    eleza test_captured_stderr(self):
        with support.captured_stderr() as stderr:
            andika("hello", file=sys.stderr)
        self.assertEqual(stderr.getvalue(), "hello\n")

    eleza test_captured_stdin(self):
        with support.captured_stdin() as stdin:
            stdin.write('hello\n')
            stdin.seek(0)
            # call test code that consumes kutoka sys.stdin
            captured = input()
        self.assertEqual(captured, "hello")

    eleza test_gc_collect(self):
        support.gc_collect()

    eleza test_python_is_optimized(self):
        self.assertIsInstance(support.python_is_optimized(), bool)

    eleza test_swap_attr(self):
        kundi Obj:
            pass
        obj = Obj()
        obj.x = 1
        with support.swap_attr(obj, "x", 5) as x:
            self.assertEqual(obj.x, 5)
            self.assertEqual(x, 1)
        self.assertEqual(obj.x, 1)
        with support.swap_attr(obj, "y", 5) as y:
            self.assertEqual(obj.y, 5)
            self.assertIsNone(y)
        self.assertFalse(hasattr(obj, 'y'))
        with support.swap_attr(obj, "y", 5):
            del obj.y
        self.assertFalse(hasattr(obj, 'y'))

    eleza test_swap_item(self):
        D = {"x":1}
        with support.swap_item(D, "x", 5) as x:
            self.assertEqual(D["x"], 5)
            self.assertEqual(x, 1)
        self.assertEqual(D["x"], 1)
        with support.swap_item(D, "y", 5) as y:
            self.assertEqual(D["y"], 5)
            self.assertIsNone(y)
        self.assertNotIn("y", D)
        with support.swap_item(D, "y", 5):
            del D["y"]
        self.assertNotIn("y", D)

    kundi RefClass:
        attribute1 = None
        attribute2 = None
        _hidden_attribute1 = None
        __magic_1__ = None

    kundi OtherClass:
        attribute2 = None
        attribute3 = None
        __magic_1__ = None
        __magic_2__ = None

    eleza test_detect_api_mismatch(self):
        missing_items = support.detect_api_mismatch(self.RefClass,
                                                    self.OtherClass)
        self.assertEqual({'attribute1'}, missing_items)

        missing_items = support.detect_api_mismatch(self.OtherClass,
                                                    self.RefClass)
        self.assertEqual({'attribute3', '__magic_2__'}, missing_items)

    eleza test_detect_api_mismatch__ignore(self):
        ignore = ['attribute1', 'attribute3', '__magic_2__', 'not_in_either']

        missing_items = support.detect_api_mismatch(
                self.RefClass, self.OtherClass, ignore=ignore)
        self.assertEqual(set(), missing_items)

        missing_items = support.detect_api_mismatch(
                self.OtherClass, self.RefClass, ignore=ignore)
        self.assertEqual(set(), missing_items)

    eleza test_check__all__(self):
        extra = {'tempdir'}
        blacklist = {'template'}
        support.check__all__(self,
                             tempfile,
                             extra=extra,
                             blacklist=blacklist)

        extra = {'TextTestResult', 'installHandler'}
        blacklist = {'load_tests', "TestProgram", "BaseTestSuite"}

        support.check__all__(self,
                             unittest,
                             ("unittest.result", "unittest.case",
                              "unittest.suite", "unittest.loader",
                              "unittest.main", "unittest.runner",
                              "unittest.signals", "unittest.async_case"),
                             extra=extra,
                             blacklist=blacklist)

        self.assertRaises(AssertionError, support.check__all__, self, unittest)

    @unittest.skipUnless(hasattr(os, 'waitpid') and hasattr(os, 'WNOHANG'),
                         'need os.waitpid() and os.WNOHANG')
    eleza test_reap_children(self):
        # Make sure that there is no other pending child process
        support.reap_children()

        # Create a child process
        pid = os.fork()
        ikiwa pid == 0:
            # child process: do nothing, just exit
            os._exit(0)

        t0 = time.monotonic()
        deadline = time.monotonic() + 60.0

        was_altered = support.environment_altered
        try:
            support.environment_altered = False
            stderr = io.StringIO()

            while True:
                ikiwa time.monotonic() > deadline:
                    self.fail("timeout")

                with contextlib.redirect_stderr(stderr):
                    support.reap_children()

                # Use environment_altered to check ikiwa reap_children() found
                # the child process
                ikiwa support.environment_altered:
                    break

                # loop until the child process completed
                time.sleep(0.100)

            msg = "Warning -- reap_children() reaped child process %s" % pid
            self.assertIn(msg, stderr.getvalue())
            self.assertTrue(support.environment_altered)
        finally:
            support.environment_altered = was_altered

        # Just in case, check again that there is no other
        # pending child process
        support.reap_children()

    eleza check_options(self, args, func, expected=None):
        code = f'kutoka test.support agiza {func}; andika(repr({func}()))'
        cmd = [sys.executable, *args, '-c', code]
        env = {key: value for key, value in os.environ.items()
               ikiwa not key.startswith('PYTHON')}
        proc = subprocess.run(cmd,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL,
                              universal_newlines=True,
                              env=env)
        ikiwa expected is None:
            expected = args
        self.assertEqual(proc.stdout.rstrip(), repr(expected))
        self.assertEqual(proc.returncode, 0)

    eleza test_args_kutoka_interpreter_flags(self):
        # Test test.support.args_kutoka_interpreter_flags()
        for opts in (
            # no option
            [],
            # single option
            ['-B'],
            ['-s'],
            ['-S'],
            ['-E'],
            ['-v'],
            ['-b'],
            ['-q'],
            ['-I'],
            # same option multiple times
            ['-bb'],
            ['-vvv'],
            # -W options
            ['-Wignore'],
            # -X options
            ['-X', 'dev'],
            ['-Wignore', '-X', 'dev'],
            ['-X', 'faulthandler'],
            ['-X', 'agizatime'],
            ['-X', 'showalloccount'],
            ['-X', 'showrefcount'],
            ['-X', 'tracemalloc'],
            ['-X', 'tracemalloc=3'],
        ):
            with self.subTest(opts=opts):
                self.check_options(opts, 'args_kutoka_interpreter_flags')

        self.check_options(['-I', '-E', '-s'], 'args_kutoka_interpreter_flags',
                           ['-I'])

    eleza test_optim_args_kutoka_interpreter_flags(self):
        # Test test.support.optim_args_kutoka_interpreter_flags()
        for opts in (
            # no option
            [],
            ['-O'],
            ['-OO'],
            ['-OOOO'],
        ):
            with self.subTest(opts=opts):
                self.check_options(opts, 'optim_args_kutoka_interpreter_flags')

    eleza test_match_test(self):
        kundi Test:
            eleza __init__(self, test_id):
                self.test_id = test_id

            eleza id(self):
                rudisha self.test_id

        test_access = Test('test.test_os.FileTests.test_access')
        test_chdir = Test('test.test_os.Win32ErrorTests.test_chdir')

        with support.swap_attr(support, '_match_test_func', None):
            # match all
            support.set_match_tests([])
            self.assertTrue(support.match_test(test_access))
            self.assertTrue(support.match_test(test_chdir))

            # match all using None
            support.set_match_tests(None)
            self.assertTrue(support.match_test(test_access))
            self.assertTrue(support.match_test(test_chdir))

            # match the full test identifier
            support.set_match_tests([test_access.id()])
            self.assertTrue(support.match_test(test_access))
            self.assertFalse(support.match_test(test_chdir))

            # match the module name
            support.set_match_tests(['test_os'])
            self.assertTrue(support.match_test(test_access))
            self.assertTrue(support.match_test(test_chdir))

            # Test '*' pattern
            support.set_match_tests(['test_*'])
            self.assertTrue(support.match_test(test_access))
            self.assertTrue(support.match_test(test_chdir))

            # Test case sensitivity
            support.set_match_tests(['filetests'])
            self.assertFalse(support.match_test(test_access))
            support.set_match_tests(['FileTests'])
            self.assertTrue(support.match_test(test_access))

            # Test pattern containing '.' and a '*' metacharacter
            support.set_match_tests(['*test_os.*.test_*'])
            self.assertTrue(support.match_test(test_access))
            self.assertTrue(support.match_test(test_chdir))

            # Multiple patterns
            support.set_match_tests([test_access.id(), test_chdir.id()])
            self.assertTrue(support.match_test(test_access))
            self.assertTrue(support.match_test(test_chdir))

            support.set_match_tests(['test_access', 'DONTMATCH'])
            self.assertTrue(support.match_test(test_access))
            self.assertFalse(support.match_test(test_chdir))

    eleza test_fd_count(self):
        # We cannot test the absolute value of fd_count(): on old Linux
        # kernel or glibc versions, os.urandom() keeps a FD open on
        # /dev/urandom device and Python has 4 FD opens instead of 3.
        start = support.fd_count()
        fd = os.open(__file__, os.O_RDONLY)
        try:
            more = support.fd_count()
        finally:
            os.close(fd)
        self.assertEqual(more - start, 1)

    # XXX -follows a list of untested API
    # make_legacy_pyc
    # is_resource_enabled
    # requires
    # fcmp
    # umaks
    # findfile
    # check_warnings
    # EnvironmentVarGuard
    # TransientResource
    # transient_internet
    # run_with_locale
    # set_memlimit
    # bigmemtest
    # precisionbigmemtest
    # bigaddrspacetest
    # requires_resource
    # run_doctest
    # threading_cleanup
    # reap_threads
    # strip_python_stderr
    # can_symlink
    # skip_unless_symlink
    # SuppressCrashReport


eleza test_main():
    tests = [TestSupport]
    support.run_unittest(*tests)

ikiwa __name__ == '__main__':
    test_main()
