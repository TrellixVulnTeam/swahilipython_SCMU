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
        ukijumuisha open(TESTFN, "w") kama f:
            pita
        support.unlink(TESTFN)
        self.assertUongo(os.path.exists(TESTFN))
        support.unlink(TESTFN)

    eleza test_rmtree(self):
        dirpath = support.TESTFN + 'd'
        subdirpath = os.path.join(dirpath, 'subdir')
        os.mkdir(dirpath)
        os.mkdir(subdirpath)
        support.rmtree(dirpath)
        self.assertUongo(os.path.exists(dirpath))
        ukijumuisha support.swap_attr(support, 'verbose', 0):
            support.rmtree(dirpath)

        os.mkdir(dirpath)
        os.mkdir(subdirpath)
        os.chmod(dirpath, stat.S_IRUSR|stat.S_IXUSR)
        ukijumuisha support.swap_attr(support, 'verbose', 0):
            support.rmtree(dirpath)
        self.assertUongo(os.path.exists(dirpath))

        os.mkdir(dirpath)
        os.mkdir(subdirpath)
        os.chmod(dirpath, 0)
        ukijumuisha support.swap_attr(support, 'verbose', 0):
            support.rmtree(dirpath)
        self.assertUongo(os.path.exists(dirpath))

    eleza test_forget(self):
        mod_filename = TESTFN + '.py'
        ukijumuisha open(mod_filename, 'w') kama f:
            andika('foo = 1', file=f)
        sys.path.insert(0, os.curdir)
        importlib.invalidate_caches()
        jaribu:
            mod = __import__(TESTFN)
            self.assertIn(TESTFN, sys.modules)

            support.forget(TESTFN)
            self.assertNotIn(TESTFN, sys.modules)
        mwishowe:
            toa sys.path[0]
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

    # Tests kila temp_dir()

    eleza test_temp_dir(self):
        """Test that temp_dir() creates na destroys its directory."""
        parent_dir = tempfile.mkdtemp()
        parent_dir = os.path.realpath(parent_dir)

        jaribu:
            path = os.path.join(parent_dir, 'temp')
            self.assertUongo(os.path.isdir(path))
            ukijumuisha support.temp_dir(path) kama temp_path:
                self.assertEqual(temp_path, path)
                self.assertKweli(os.path.isdir(path))
            self.assertUongo(os.path.isdir(path))
        mwishowe:
            support.rmtree(parent_dir)

    eleza test_temp_dir__path_none(self):
        """Test pitaing no path."""
        ukijumuisha support.temp_dir() kama temp_path:
            self.assertKweli(os.path.isdir(temp_path))
        self.assertUongo(os.path.isdir(temp_path))

    eleza test_temp_dir__existing_dir__quiet_default(self):
        """Test pitaing a directory that already exists."""
        eleza call_temp_dir(path):
            ukijumuisha support.temp_dir(path) kama temp_path:
                ashiria Exception("should sio get here")

        path = tempfile.mkdtemp()
        path = os.path.realpath(path)
        jaribu:
            self.assertKweli(os.path.isdir(path))
            self.assertRaises(FileExistsError, call_temp_dir, path)
            # Make sure temp_dir did sio delete the original directory.
            self.assertKweli(os.path.isdir(path))
        mwishowe:
            shutil.rmtree(path)

    eleza test_temp_dir__existing_dir__quiet_true(self):
        """Test pitaing a directory that already exists ukijumuisha quiet=Kweli."""
        path = tempfile.mkdtemp()
        path = os.path.realpath(path)

        jaribu:
            ukijumuisha support.check_warnings() kama recorder:
                ukijumuisha support.temp_dir(path, quiet=Kweli) kama temp_path:
                    self.assertEqual(path, temp_path)
                warnings = [str(w.message) kila w kwenye recorder.warnings]
            # Make sure temp_dir did sio delete the original directory.
            self.assertKweli(os.path.isdir(path))
        mwishowe:
            shutil.rmtree(path)

        self.assertEqual(len(warnings), 1, warnings)
        warn = warnings[0]
        self.assertKweli(warn.startswith(f'tests may fail, unable to create '
                                        f'temporary directory {path!r}: '),
                        warn)

    @unittest.skipUnless(hasattr(os, "fork"), "test requires os.fork")
    eleza test_temp_dir__forked_child(self):
        """Test that a forked child process does sio remove the directory."""
        # See bpo-30028 kila details.
        # Run the test kama an external script, because it uses fork.
        script_helper.assert_python_ok("-c", textwrap.dedent("""
            agiza os
            kutoka test agiza support
            ukijumuisha support.temp_cwd() kama temp_path:
                pid = os.fork()
                ikiwa pid != 0:
                    # parent process (child has pid == 0)

                    # wait kila the child to terminate
                    (pid, status) = os.waitpid(pid, 0)
                    ikiwa status != 0:
                        ashiria AssertionError(f"Child process failed ukijumuisha exit "
                                             f"status indication 0x{status:x}.")

                    # Make sure that temp_path ni still present. When the child
                    # process leaves the 'temp_cwd'-context, the __exit__()-
                    # method of the context must sio remove the temporary
                    # directory.
                    ikiwa sio os.path.isdir(temp_path):
                        ashiria AssertionError("Child removed temp_path.")
        """))

    # Tests kila change_cwd()

    eleza test_change_cwd(self):
        original_cwd = os.getcwd()

        ukijumuisha support.temp_dir() kama temp_path:
            ukijumuisha support.change_cwd(temp_path) kama new_cwd:
                self.assertEqual(new_cwd, temp_path)
                self.assertEqual(os.getcwd(), new_cwd)

        self.assertEqual(os.getcwd(), original_cwd)

    eleza test_change_cwd__non_existent_dir(self):
        """Test pitaing a non-existent directory."""
        original_cwd = os.getcwd()

        eleza call_change_cwd(path):
            ukijumuisha support.change_cwd(path) kama new_cwd:
                ashiria Exception("should sio get here")

        ukijumuisha support.temp_dir() kama parent_dir:
            non_existent_dir = os.path.join(parent_dir, 'does_not_exist')
            self.assertRaises(FileNotFoundError, call_change_cwd,
                              non_existent_dir)

        self.assertEqual(os.getcwd(), original_cwd)

    eleza test_change_cwd__non_existent_dir__quiet_true(self):
        """Test pitaing a non-existent directory ukijumuisha quiet=Kweli."""
        original_cwd = os.getcwd()

        ukijumuisha support.temp_dir() kama parent_dir:
            bad_dir = os.path.join(parent_dir, 'does_not_exist')
            ukijumuisha support.check_warnings() kama recorder:
                ukijumuisha support.change_cwd(bad_dir, quiet=Kweli) kama new_cwd:
                    self.assertEqual(new_cwd, original_cwd)
                    self.assertEqual(os.getcwd(), new_cwd)
                warnings = [str(w.message) kila w kwenye recorder.warnings]

        self.assertEqual(len(warnings), 1, warnings)
        warn = warnings[0]
        self.assertKweli(warn.startswith(f'tests may fail, unable to change '
                                        f'the current working directory '
                                        f'to {bad_dir!r}: '),
                        warn)

    # Tests kila change_cwd()

    eleza test_change_cwd__chdir_warning(self):
        """Check the warning message when os.chdir() fails."""
        path = TESTFN + '_does_not_exist'
        ukijumuisha support.check_warnings() kama recorder:
            ukijumuisha support.change_cwd(path=path, quiet=Kweli):
                pita
            messages = [str(w.message) kila w kwenye recorder.warnings]

        self.assertEqual(len(messages), 1, messages)
        msg = messages[0]
        self.assertKweli(msg.startswith(f'tests may fail, unable to change '
                                       f'the current working directory '
                                       f'to {path!r}: '),
                        msg)

    # Tests kila temp_cwd()

    eleza test_temp_cwd(self):
        here = os.getcwd()
        ukijumuisha support.temp_cwd(name=TESTFN):
            self.assertEqual(os.path.basename(os.getcwd()), TESTFN)
        self.assertUongo(os.path.exists(TESTFN))
        self.assertEqual(os.getcwd(), here)


    eleza test_temp_cwd__name_none(self):
        """Test pitaing Tupu to temp_cwd()."""
        original_cwd = os.getcwd()
        ukijumuisha support.temp_cwd(name=Tupu) kama new_cwd:
            self.assertNotEqual(new_cwd, original_cwd)
            self.assertKweli(os.path.isdir(new_cwd))
            self.assertEqual(os.getcwd(), new_cwd)
        self.assertEqual(os.getcwd(), original_cwd)

    eleza test_sortdict(self):
        self.assertEqual(support.sortdict({3:3, 2:2, 1:1}), "{1: 1, 2: 2, 3: 3}")

    eleza test_make_bad_fd(self):
        fd = support.make_bad_fd()
        ukijumuisha self.assertRaises(OSError) kama cm:
            os.write(fd, b"foo")
        self.assertEqual(cm.exception.errno, errno.EBADF)

    eleza test_check_syntax_error(self):
        support.check_syntax_error(self, "eleza class", lineno=1, offset=5)
        ukijumuisha self.assertRaises(AssertionError):
            support.check_syntax_error(self, "x=1")

    eleza test_CleanImport(self):
        agiza importlib
        ukijumuisha support.CleanImport("asyncore"):
            importlib.import_module("asyncore")

    eleza test_DirsOnSysPath(self):
        ukijumuisha support.DirsOnSysPath('foo', 'bar'):
            self.assertIn("foo", sys.path)
            self.assertIn("bar", sys.path)
        self.assertNotIn("foo", sys.path)
        self.assertNotIn("bar", sys.path)

    eleza test_captured_stdout(self):
        ukijumuisha support.captured_stdout() kama stdout:
            andika("hello")
        self.assertEqual(stdout.getvalue(), "hello\n")

    eleza test_captured_stderr(self):
        ukijumuisha support.captured_stderr() kama stderr:
            andika("hello", file=sys.stderr)
        self.assertEqual(stderr.getvalue(), "hello\n")

    eleza test_captured_stdin(self):
        ukijumuisha support.captured_stdin() kama stdin:
            stdin.write('hello\n')
            stdin.seek(0)
            # call test code that consumes kutoka sys.stdin
            captured = uliza()
        self.assertEqual(captured, "hello")

    eleza test_gc_collect(self):
        support.gc_collect()

    eleza test_python_is_optimized(self):
        self.assertIsInstance(support.python_is_optimized(), bool)

    eleza test_swap_attr(self):
        kundi Obj:
            pita
        obj = Obj()
        obj.x = 1
        ukijumuisha support.swap_attr(obj, "x", 5) kama x:
            self.assertEqual(obj.x, 5)
            self.assertEqual(x, 1)
        self.assertEqual(obj.x, 1)
        ukijumuisha support.swap_attr(obj, "y", 5) kama y:
            self.assertEqual(obj.y, 5)
            self.assertIsTupu(y)
        self.assertUongo(hasattr(obj, 'y'))
        ukijumuisha support.swap_attr(obj, "y", 5):
            toa obj.y
        self.assertUongo(hasattr(obj, 'y'))

    eleza test_swap_item(self):
        D = {"x":1}
        ukijumuisha support.swap_item(D, "x", 5) kama x:
            self.assertEqual(D["x"], 5)
            self.assertEqual(x, 1)
        self.assertEqual(D["x"], 1)
        ukijumuisha support.swap_item(D, "y", 5) kama y:
            self.assertEqual(D["y"], 5)
            self.assertIsTupu(y)
        self.assertNotIn("y", D)
        ukijumuisha support.swap_item(D, "y", 5):
            toa D["y"]
        self.assertNotIn("y", D)

    kundi RefClass:
        attribute1 = Tupu
        attribute2 = Tupu
        _hidden_attribute1 = Tupu
        __magic_1__ = Tupu

    kundi OtherClass:
        attribute2 = Tupu
        attribute3 = Tupu
        __magic_1__ = Tupu
        __magic_2__ = Tupu

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

    @unittest.skipUnless(hasattr(os, 'waitpid') na hasattr(os, 'WNOHANG'),
                         'need os.waitpid() na os.WNOHANG')
    eleza test_reap_children(self):
        # Make sure that there ni no other pending child process
        support.reap_children()

        # Create a child process
        pid = os.fork()
        ikiwa pid == 0:
            # child process: do nothing, just exit
            os._exit(0)

        t0 = time.monotonic()
        deadline = time.monotonic() + 60.0

        was_altered = support.environment_altered
        jaribu:
            support.environment_altered = Uongo
            stderr = io.StringIO()

            wakati Kweli:
                ikiwa time.monotonic() > deadline:
                    self.fail("timeout")

                ukijumuisha contextlib.redirect_stderr(stderr):
                    support.reap_children()

                # Use environment_altered to check ikiwa reap_children() found
                # the child process
                ikiwa support.environment_altered:
                    koma

                # loop until the child process completed
                time.sleep(0.100)

            msg = "Warning -- reap_children() reaped child process %s" % pid
            self.assertIn(msg, stderr.getvalue())
            self.assertKweli(support.environment_altered)
        mwishowe:
            support.environment_altered = was_altered

        # Just kwenye case, check again that there ni no other
        # pending child process
        support.reap_children()

    eleza check_options(self, args, func, expected=Tupu):
        code = f'kutoka test.support agiza {func}; andika(repr({func}()))'
        cmd = [sys.executable, *args, '-c', code]
        env = {key: value kila key, value kwenye os.environ.items()
               ikiwa sio key.startswith('PYTHON')}
        proc = subprocess.run(cmd,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL,
                              universal_newlines=Kweli,
                              env=env)
        ikiwa expected ni Tupu:
            expected = args
        self.assertEqual(proc.stdout.rstrip(), repr(expected))
        self.assertEqual(proc.returncode, 0)

    eleza test_args_from_interpreter_flags(self):
        # Test test.support.args_from_interpreter_flags()
        kila opts kwenye (
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
            ['-X', 'importtime'],
            ['-X', 'showalloccount'],
            ['-X', 'showrefcount'],
            ['-X', 'tracemalloc'],
            ['-X', 'tracemalloc=3'],
        ):
            ukijumuisha self.subTest(opts=opts):
                self.check_options(opts, 'args_from_interpreter_flags')

        self.check_options(['-I', '-E', '-s'], 'args_from_interpreter_flags',
                           ['-I'])

    eleza test_optim_args_from_interpreter_flags(self):
        # Test test.support.optim_args_from_interpreter_flags()
        kila opts kwenye (
            # no option
            [],
            ['-O'],
            ['-OO'],
            ['-OOOO'],
        ):
            ukijumuisha self.subTest(opts=opts):
                self.check_options(opts, 'optim_args_from_interpreter_flags')

    eleza test_match_test(self):
        kundi Test:
            eleza __init__(self, test_id):
                self.test_id = test_id

            eleza id(self):
                rudisha self.test_id

        test_access = Test('test.test_os.FileTests.test_access')
        test_chdir = Test('test.test_os.Win32ErrorTests.test_chdir')

        ukijumuisha support.swap_attr(support, '_match_test_func', Tupu):
            # match all
            support.set_match_tests([])
            self.assertKweli(support.match_test(test_access))
            self.assertKweli(support.match_test(test_chdir))

            # match all using Tupu
            support.set_match_tests(Tupu)
            self.assertKweli(support.match_test(test_access))
            self.assertKweli(support.match_test(test_chdir))

            # match the full test identifier
            support.set_match_tests([test_access.id()])
            self.assertKweli(support.match_test(test_access))
            self.assertUongo(support.match_test(test_chdir))

            # match the module name
            support.set_match_tests(['test_os'])
            self.assertKweli(support.match_test(test_access))
            self.assertKweli(support.match_test(test_chdir))

            # Test '*' pattern
            support.set_match_tests(['test_*'])
            self.assertKweli(support.match_test(test_access))
            self.assertKweli(support.match_test(test_chdir))

            # Test case sensitivity
            support.set_match_tests(['filetests'])
            self.assertUongo(support.match_test(test_access))
            support.set_match_tests(['FileTests'])
            self.assertKweli(support.match_test(test_access))

            # Test pattern containing '.' na a '*' metacharacter
            support.set_match_tests(['*test_os.*.test_*'])
            self.assertKweli(support.match_test(test_access))
            self.assertKweli(support.match_test(test_chdir))

            # Multiple patterns
            support.set_match_tests([test_access.id(), test_chdir.id()])
            self.assertKweli(support.match_test(test_access))
            self.assertKweli(support.match_test(test_chdir))

            support.set_match_tests(['test_access', 'DONTMATCH'])
            self.assertKweli(support.match_test(test_access))
            self.assertUongo(support.match_test(test_chdir))

    eleza test_fd_count(self):
        # We cannot test the absolute value of fd_count(): on old Linux
        # kernel ama glibc versions, os.urandom() keeps a FD open on
        # /dev/urandom device na Python has 4 FD opens instead of 3.
        start = support.fd_count()
        fd = os.open(__file__, os.O_RDONLY)
        jaribu:
            more = support.fd_count()
        mwishowe:
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
