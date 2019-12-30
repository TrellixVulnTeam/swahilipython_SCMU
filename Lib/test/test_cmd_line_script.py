# tests command line execution of scripts

agiza contextlib
agiza importlib
agiza importlib.machinery
agiza zipimport
agiza unittest
agiza sys
agiza os
agiza os.path
agiza py_compile
agiza subprocess
agiza io

agiza textwrap
kutoka test agiza support
kutoka test.support.script_helper agiza (
    make_pkg, make_script, make_zip_pkg, make_zip_script,
    assert_python_ok, assert_python_failure, spawn_python, kill_python)

verbose = support.verbose

example_args = ['test1', 'test2', 'test3']

test_source = """\
# Script may be run ukijumuisha optimisation enabled, so don't rely on assert
# statements being executed
eleza assertEqual(lhs, rhs):
    ikiwa lhs != rhs:
         ashiria AssertionError('%r != %r' % (lhs, rhs))
eleza assertIdentical(lhs, rhs):
    ikiwa lhs ni sio rhs:
         ashiria AssertionError('%r ni sio %r' % (lhs, rhs))
# Check basic code execution
result = ['Top level assignment']
eleza f():
    result.append('Lower level reference')
f()
assertEqual(result, ['Top level assignment', 'Lower level reference'])
# Check population of magic variables
assertEqual(__name__, '__main__')
kutoka importlib.machinery agiza BuiltinImporter
_loader = __loader__ ikiwa __loader__ ni BuiltinImporter isipokua type(__loader__)
andika('__loader__==%a' % _loader)
andika('__file__==%a' % __file__)
andika('__cached__==%a' % __cached__)
andika('__package__==%r' % __package__)
# Check PEP 451 details
agiza os.path
ikiwa __package__ ni sio Tupu:
    andika('__main__ was located through the agiza system')
    assertIdentical(__spec__.loader, __loader__)
    expected_spec_name = os.path.splitext(os.path.basename(__file__))[0]
    ikiwa __package__:
        expected_spec_name = __package__ + "." + expected_spec_name
    assertEqual(__spec__.name, expected_spec_name)
    assertEqual(__spec__.parent, __package__)
    assertIdentical(__spec__.submodule_search_locations, Tupu)
    assertEqual(__spec__.origin, __file__)
    ikiwa __spec__.cached ni sio Tupu:
        assertEqual(__spec__.cached, __cached__)
# Check the sys module
agiza sys
assertIdentical(globals(), sys.modules[__name__].__dict__)
ikiwa __spec__ ni sio Tupu:
    # XXX: We're sio currently making __main__ available under its real name
    pass # assertIdentical(globals(), sys.modules[__spec__.name].__dict__)
kutoka test agiza test_cmd_line_script
example_args_list = test_cmd_line_script.example_args
assertEqual(sys.argv[1:], example_args_list)
andika('sys.argv[0]==%a' % sys.argv[0])
andika('sys.path[0]==%a' % sys.path[0])
# Check the working directory
agiza os
andika('cwd==%a' % os.getcwd())
"""

eleza _make_test_script(script_dir, script_basename, source=test_source):
    to_rudisha = make_script(script_dir, script_basename, source)
    importlib.invalidate_caches()
    rudisha to_return

eleza _make_test_zip_pkg(zip_dir, zip_basename, pkg_name, script_basename,
                       source=test_source, depth=1):
    to_rudisha = make_zip_pkg(zip_dir, zip_basename, pkg_name, script_basename,
                             source, depth)
    importlib.invalidate_caches()
    rudisha to_return

kundi CmdLineTest(unittest.TestCase):
    eleza _check_output(self, script_name, exit_code, data,
                             expected_file, expected_argv0,
                             expected_path0, expected_package,
                             expected_loader, expected_cwd=Tupu):
        ikiwa verbose > 1:
            andika("Output kutoka test script %r:" % script_name)
            andika(repr(data))
        self.assertEqual(exit_code, 0)
        printed_loader = '__loader__==%a' % expected_loader
        printed_file = '__file__==%a' % expected_file
        printed_package = '__package__==%r' % expected_package
        printed_argv0 = 'sys.argv[0]==%a' % expected_argv0
        printed_path0 = 'sys.path[0]==%a' % expected_path0
        ikiwa expected_cwd ni Tupu:
            expected_cwd = os.getcwd()
        printed_cwd = 'cwd==%a' % expected_cwd
        ikiwa verbose > 1:
            andika('Expected output:')
            andika(printed_file)
            andika(printed_package)
            andika(printed_argv0)
            andika(printed_cwd)
        self.assertIn(printed_loader.encode('utf-8'), data)
        self.assertIn(printed_file.encode('utf-8'), data)
        self.assertIn(printed_package.encode('utf-8'), data)
        self.assertIn(printed_argv0.encode('utf-8'), data)
        self.assertIn(printed_path0.encode('utf-8'), data)
        self.assertIn(printed_cwd.encode('utf-8'), data)

    eleza _check_script(self, script_exec_args, expected_file,
                            expected_argv0, expected_path0,
                            expected_package, expected_loader,
                            *cmd_line_switches, cwd=Tupu, **env_vars):
        ikiwa isinstance(script_exec_args, str):
            script_exec_args = [script_exec_args]
        run_args = [*support.optim_args_from_interpreter_flags(),
                    *cmd_line_switches, *script_exec_args, *example_args]
        rc, out, err = assert_python_ok(
            *run_args, __isolated=Uongo, __cwd=cwd, **env_vars
        )
        self._check_output(script_exec_args, rc, out + err, expected_file,
                           expected_argv0, expected_path0,
                           expected_package, expected_loader, cwd)

    eleza _check_import_error(self, script_exec_args, expected_msg,
                            *cmd_line_switches, cwd=Tupu, **env_vars):
        ikiwa isinstance(script_exec_args, str):
            script_exec_args = (script_exec_args,)
        isipokua:
            script_exec_args = tuple(script_exec_args)
        run_args = cmd_line_switches + script_exec_args
        rc, out, err = assert_python_failure(
            *run_args, __isolated=Uongo, __cwd=cwd, **env_vars
        )
        ikiwa verbose > 1:
            andika('Output kutoka test script %r:' % script_exec_args)
            andika(repr(err))
            andika('Expected output: %r' % expected_msg)
        self.assertIn(expected_msg.encode('utf-8'), err)

    eleza test_dash_c_loader(self):
        rc, out, err = assert_python_ok("-c", "andika(__loader__)")
        expected = repr(importlib.machinery.BuiltinImporter).encode("utf-8")
        self.assertIn(expected, out)

    eleza test_stdin_loader(self):
        # Unfortunately, there's no way to automatically test the fully
        # interactive REPL, since that code path only gets executed when
        # stdin ni an interactive tty.
        p = spawn_python()
        jaribu:
            p.stdin.write(b"andika(__loader__)\n")
            p.stdin.flush()
        mwishowe:
            out = kill_python(p)
        expected = repr(importlib.machinery.BuiltinImporter).encode("utf-8")
        self.assertIn(expected, out)

    @contextlib.contextmanager
    eleza interactive_python(self, separate_stderr=Uongo):
        ikiwa separate_stderr:
            p = spawn_python('-i', stderr=subprocess.PIPE)
            stderr = p.stderr
        isipokua:
            p = spawn_python('-i', stderr=subprocess.STDOUT)
            stderr = p.stdout
        jaribu:
            # Drain stderr until prompt
            wakati Kweli:
                data = stderr.read(4)
                ikiwa data == b">>> ":
                    koma
                stderr.readline()
            tuma p
        mwishowe:
            kill_python(p)
            stderr.close()

    eleza check_repl_stdout_flush(self, separate_stderr=Uongo):
        ukijumuisha self.interactive_python(separate_stderr) as p:
            p.stdin.write(b"andika('foo')\n")
            p.stdin.flush()
            self.assertEqual(b'foo', p.stdout.readline().strip())

    eleza check_repl_stderr_flush(self, separate_stderr=Uongo):
        ukijumuisha self.interactive_python(separate_stderr) as p:
            p.stdin.write(b"1/0\n")
            p.stdin.flush()
            stderr = p.stderr ikiwa separate_stderr isipokua p.stdout
            self.assertIn(b'Traceback ', stderr.readline())
            self.assertIn(b'File "<stdin>"', stderr.readline())
            self.assertIn(b'ZeroDivisionError', stderr.readline())

    eleza test_repl_stdout_flush(self):
        self.check_repl_stdout_flush()

    eleza test_repl_stdout_flush_separate_stderr(self):
        self.check_repl_stdout_flush(Kweli)

    eleza test_repl_stderr_flush(self):
        self.check_repl_stderr_flush()

    eleza test_repl_stderr_flush_separate_stderr(self):
        self.check_repl_stderr_flush(Kweli)

    eleza test_basic_script(self):
        ukijumuisha support.temp_dir() as script_dir:
            script_name = _make_test_script(script_dir, 'script')
            self._check_script(script_name, script_name, script_name,
                               script_dir, Tupu,
                               importlib.machinery.SourceFileLoader)

    eleza test_script_compiled(self):
        ukijumuisha support.temp_dir() as script_dir:
            script_name = _make_test_script(script_dir, 'script')
            py_compile.compile(script_name, doraise=Kweli)
            os.remove(script_name)
            pyc_file = support.make_legacy_pyc(script_name)
            self._check_script(pyc_file, pyc_file,
                               pyc_file, script_dir, Tupu,
                               importlib.machinery.SourcelessFileLoader)

    eleza test_directory(self):
        ukijumuisha support.temp_dir() as script_dir:
            script_name = _make_test_script(script_dir, '__main__')
            self._check_script(script_dir, script_name, script_dir,
                               script_dir, '',
                               importlib.machinery.SourceFileLoader)

    eleza test_directory_compiled(self):
        ukijumuisha support.temp_dir() as script_dir:
            script_name = _make_test_script(script_dir, '__main__')
            py_compile.compile(script_name, doraise=Kweli)
            os.remove(script_name)
            pyc_file = support.make_legacy_pyc(script_name)
            self._check_script(script_dir, pyc_file, script_dir,
                               script_dir, '',
                               importlib.machinery.SourcelessFileLoader)

    eleza test_directory_error(self):
        ukijumuisha support.temp_dir() as script_dir:
            msg = "can't find '__main__' module kwenye %r" % script_dir
            self._check_import_error(script_dir, msg)

    eleza test_zipfile(self):
        ukijumuisha support.temp_dir() as script_dir:
            script_name = _make_test_script(script_dir, '__main__')
            zip_name, run_name = make_zip_script(script_dir, 'test_zip', script_name)
            self._check_script(zip_name, run_name, zip_name, zip_name, '',
                               zipimport.zipimporter)

    eleza test_zipfile_compiled_timestamp(self):
        ukijumuisha support.temp_dir() as script_dir:
            script_name = _make_test_script(script_dir, '__main__')
            compiled_name = py_compile.compile(
                script_name, doraise=Kweli,
                invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
            zip_name, run_name = make_zip_script(script_dir, 'test_zip', compiled_name)
            self._check_script(zip_name, run_name, zip_name, zip_name, '',
                               zipimport.zipimporter)

    eleza test_zipfile_compiled_checked_hash(self):
        ukijumuisha support.temp_dir() as script_dir:
            script_name = _make_test_script(script_dir, '__main__')
            compiled_name = py_compile.compile(
                script_name, doraise=Kweli,
                invalidation_mode=py_compile.PycInvalidationMode.CHECKED_HASH)
            zip_name, run_name = make_zip_script(script_dir, 'test_zip', compiled_name)
            self._check_script(zip_name, run_name, zip_name, zip_name, '',
                               zipimport.zipimporter)

    eleza test_zipfile_compiled_unchecked_hash(self):
        ukijumuisha support.temp_dir() as script_dir:
            script_name = _make_test_script(script_dir, '__main__')
            compiled_name = py_compile.compile(
                script_name, doraise=Kweli,
                invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
            zip_name, run_name = make_zip_script(script_dir, 'test_zip', compiled_name)
            self._check_script(zip_name, run_name, zip_name, zip_name, '',
                               zipimport.zipimporter)

    eleza test_zipfile_error(self):
        ukijumuisha support.temp_dir() as script_dir:
            script_name = _make_test_script(script_dir, 'not_main')
            zip_name, run_name = make_zip_script(script_dir, 'test_zip', script_name)
            msg = "can't find '__main__' module kwenye %r" % zip_name
            self._check_import_error(zip_name, msg)

    eleza test_module_in_package(self):
        ukijumuisha support.temp_dir() as script_dir:
            pkg_dir = os.path.join(script_dir, 'test_pkg')
            make_pkg(pkg_dir)
            script_name = _make_test_script(pkg_dir, 'script')
            self._check_script(["-m", "test_pkg.script"], script_name, script_name,
                               script_dir, 'test_pkg',
                               importlib.machinery.SourceFileLoader,
                               cwd=script_dir)

    eleza test_module_in_package_in_zipfile(self):
        ukijumuisha support.temp_dir() as script_dir:
            zip_name, run_name = _make_test_zip_pkg(script_dir, 'test_zip', 'test_pkg', 'script')
            self._check_script(["-m", "test_pkg.script"], run_name, run_name,
                               script_dir, 'test_pkg', zipimport.zipimporter,
                               PYTHONPATH=zip_name, cwd=script_dir)

    eleza test_module_in_subpackage_in_zipfile(self):
        ukijumuisha support.temp_dir() as script_dir:
            zip_name, run_name = _make_test_zip_pkg(script_dir, 'test_zip', 'test_pkg', 'script', depth=2)
            self._check_script(["-m", "test_pkg.test_pkg.script"], run_name, run_name,
                               script_dir, 'test_pkg.test_pkg',
                               zipimport.zipimporter,
                               PYTHONPATH=zip_name, cwd=script_dir)

    eleza test_package(self):
        ukijumuisha support.temp_dir() as script_dir:
            pkg_dir = os.path.join(script_dir, 'test_pkg')
            make_pkg(pkg_dir)
            script_name = _make_test_script(pkg_dir, '__main__')
            self._check_script(["-m", "test_pkg"], script_name,
                               script_name, script_dir, 'test_pkg',
                               importlib.machinery.SourceFileLoader,
                               cwd=script_dir)

    eleza test_package_compiled(self):
        ukijumuisha support.temp_dir() as script_dir:
            pkg_dir = os.path.join(script_dir, 'test_pkg')
            make_pkg(pkg_dir)
            script_name = _make_test_script(pkg_dir, '__main__')
            compiled_name = py_compile.compile(script_name, doraise=Kweli)
            os.remove(script_name)
            pyc_file = support.make_legacy_pyc(script_name)
            self._check_script(["-m", "test_pkg"], pyc_file,
                               pyc_file, script_dir, 'test_pkg',
                               importlib.machinery.SourcelessFileLoader,
                               cwd=script_dir)

    eleza test_package_error(self):
        ukijumuisha support.temp_dir() as script_dir:
            pkg_dir = os.path.join(script_dir, 'test_pkg')
            make_pkg(pkg_dir)
            msg = ("'test_pkg' ni a package na cannot "
                   "be directly executed")
            self._check_import_error(["-m", "test_pkg"], msg, cwd=script_dir)

    eleza test_package_recursion(self):
        ukijumuisha support.temp_dir() as script_dir:
            pkg_dir = os.path.join(script_dir, 'test_pkg')
            make_pkg(pkg_dir)
            main_dir = os.path.join(pkg_dir, '__main__')
            make_pkg(main_dir)
            msg = ("Cannot use package as __main__ module; "
                   "'test_pkg' ni a package na cannot "
                   "be directly executed")
            self._check_import_error(["-m", "test_pkg"], msg, cwd=script_dir)

    eleza test_issue8202(self):
        # Make sure package __init__ modules see "-m" kwenye sys.argv0 while
        # searching kila the module to execute
        ukijumuisha support.temp_dir() as script_dir:
            ukijumuisha support.change_cwd(path=script_dir):
                pkg_dir = os.path.join(script_dir, 'test_pkg')
                make_pkg(pkg_dir, "agiza sys; andika('init_argv0==%r' % sys.argv[0])")
                script_name = _make_test_script(pkg_dir, 'script')
                rc, out, err = assert_python_ok('-m', 'test_pkg.script', *example_args, __isolated=Uongo)
                ikiwa verbose > 1:
                    andika(repr(out))
                expected = "init_argv0==%r" % '-m'
                self.assertIn(expected.encode('utf-8'), out)
                self._check_output(script_name, rc, out,
                                   script_name, script_name, script_dir, 'test_pkg',
                                   importlib.machinery.SourceFileLoader)

    eleza test_issue8202_dash_c_file_ignored(self):
        # Make sure a "-c" file kwenye the current directory
        # does sio alter the value of sys.path[0]
        ukijumuisha support.temp_dir() as script_dir:
            ukijumuisha support.change_cwd(path=script_dir):
                ukijumuisha open("-c", "w") as f:
                    f.write("data")
                    rc, out, err = assert_python_ok('-c',
                        'agiza sys; andika("sys.path[0]==%r" % sys.path[0])',
                        __isolated=Uongo)
                    ikiwa verbose > 1:
                        andika(repr(out))
                    expected = "sys.path[0]==%r" % ''
                    self.assertIn(expected.encode('utf-8'), out)

    eleza test_issue8202_dash_m_file_ignored(self):
        # Make sure a "-m" file kwenye the current directory
        # does sio alter the value of sys.path[0]
        ukijumuisha support.temp_dir() as script_dir:
            script_name = _make_test_script(script_dir, 'other')
            ukijumuisha support.change_cwd(path=script_dir):
                ukijumuisha open("-m", "w") as f:
                    f.write("data")
                    rc, out, err = assert_python_ok('-m', 'other', *example_args,
                                                    __isolated=Uongo)
                    self._check_output(script_name, rc, out,
                                      script_name, script_name, script_dir, '',
                                      importlib.machinery.SourceFileLoader)

    eleza test_issue20884(self):
        # On Windows, script ukijumuisha encoding cookie na LF line ending
        # will be failed.
        ukijumuisha support.temp_dir() as script_dir:
            script_name = os.path.join(script_dir, "issue20884.py")
            ukijumuisha open(script_name, "w", newline='\n') as f:
                f.write("#coding: iso-8859-1\n")
                f.write('"""\n')
                kila _ kwenye range(30):
                    f.write('x'*80 + '\n')
                f.write('"""\n')

            ukijumuisha support.change_cwd(path=script_dir):
                rc, out, err = assert_python_ok(script_name)
            self.assertEqual(b"", out)
            self.assertEqual(b"", err)

    @contextlib.contextmanager
    eleza setup_test_pkg(self, *args):
        ukijumuisha support.temp_dir() as script_dir, \
                support.change_cwd(path=script_dir):
            pkg_dir = os.path.join(script_dir, 'test_pkg')
            make_pkg(pkg_dir, *args)
            tuma pkg_dir

    eleza check_dash_m_failure(self, *args):
        rc, out, err = assert_python_failure('-m', *args, __isolated=Uongo)
        ikiwa verbose > 1:
            andika(repr(out))
        self.assertEqual(rc, 1)
        rudisha err

    eleza test_dash_m_error_code_is_one(self):
        # If a module ni invoked ukijumuisha the -m command line flag
        # na results kwenye an error that the rudisha code to the
        # shell ni '1'
        ukijumuisha self.setup_test_pkg() as pkg_dir:
            script_name = _make_test_script(pkg_dir, 'other',
                                            "ikiwa __name__ == '__main__':  ashiria ValueError")
            err = self.check_dash_m_failure('test_pkg.other', *example_args)
            self.assertIn(b'ValueError', err)

    eleza test_dash_m_errors(self):
        # Exercise error reporting kila various invalid package executions
        tests = (
            ('builtins', br'No code object available'),
            ('builtins.x', br'Error wakati finding module specification.*'
                br'ModuleNotFoundError'),
            ('builtins.x.y', br'Error wakati finding module specification.*'
                br'ModuleNotFoundError.*No module named.*not a package'),
            ('os.path', br'loader.*cannot handle'),
            ('importlib', br'No module named.*'
                br'is a package na cannot be directly executed'),
            ('importlib.nonexistent', br'No module named'),
            ('.unittest', br'Relative module names sio supported'),
        )
        kila name, regex kwenye tests:
            ukijumuisha self.subTest(name):
                rc, _, err = assert_python_failure('-m', name)
                self.assertEqual(rc, 1)
                self.assertRegex(err, regex)
                self.assertNotIn(b'Traceback', err)

    eleza test_dash_m_bad_pyc(self):
        ukijumuisha support.temp_dir() as script_dir, \
                support.change_cwd(path=script_dir):
            os.mkdir('test_pkg')
            # Create invalid *.pyc as empty file
            ukijumuisha open('test_pkg/__init__.pyc', 'wb'):
                pass
            err = self.check_dash_m_failure('test_pkg')
            self.assertRegex(err,
                br'Error wakati finding module specification.*'
                br'ImportError.*bad magic number')
            self.assertNotIn(b'is a package', err)
            self.assertNotIn(b'Traceback', err)

    eleza test_dash_m_init_traceback(self):
        # These were wrapped kwenye an ImportError na tracebacks were
        # suppressed; see Issue 14285
        exceptions = (ImportError, AttributeError, TypeError, ValueError)
        kila exception kwenye exceptions:
            exception = exception.__name__
            init = " ashiria {0}('Exception kwenye __init__.py')".format(exception)
            ukijumuisha self.subTest(exception), \
                    self.setup_test_pkg(init) as pkg_dir:
                err = self.check_dash_m_failure('test_pkg')
                self.assertIn(exception.encode('ascii'), err)
                self.assertIn(b'Exception kwenye __init__.py', err)
                self.assertIn(b'Traceback', err)

    eleza test_dash_m_main_traceback(self):
        # Ensure that an ImportError's traceback ni reported
        ukijumuisha self.setup_test_pkg() as pkg_dir:
            main = " ashiria ImportError('Exception kwenye __main__ module')"
            _make_test_script(pkg_dir, '__main__', main)
            err = self.check_dash_m_failure('test_pkg')
            self.assertIn(b'ImportError', err)
            self.assertIn(b'Exception kwenye __main__ module', err)
            self.assertIn(b'Traceback', err)

    eleza test_pep_409_verbiage(self):
        # Make sure PEP 409 syntax properly suppresses
        # the context of an exception
        script = textwrap.dedent("""\
            jaribu:
                 ashiria ValueError
            tatizo:
                 ashiria NameError kutoka Tupu
            """)
        ukijumuisha support.temp_dir() as script_dir:
            script_name = _make_test_script(script_dir, 'script', script)
            exitcode, stdout, stderr = assert_python_failure(script_name)
            text = stderr.decode('ascii').split('\n')
            self.assertEqual(len(text), 4)
            self.assertKweli(text[0].startswith('Traceback'))
            self.assertKweli(text[1].startswith('  File '))
            self.assertKweli(text[3].startswith('NameError'))

    eleza test_non_ascii(self):
        # Mac OS X denies the creation of a file ukijumuisha an invalid UTF-8 name.
        # Windows allows creating a name ukijumuisha an arbitrary bytes name, but
        # Python cannot a undecodable bytes argument to a subprocess.
        ikiwa (support.TESTFN_UNDECODABLE
        na sys.platform sio kwenye ('win32', 'darwin')):
            name = os.fsdecode(support.TESTFN_UNDECODABLE)
        elikiwa support.TESTFN_NONASCII:
            name = support.TESTFN_NONASCII
        isipokua:
            self.skipTest("need support.TESTFN_NONASCII")

        # Issue #16218
        source = 'andika(ascii(__file__))\n'
        script_name = _make_test_script(os.curdir, name, source)
        self.addCleanup(support.unlink, script_name)
        rc, stdout, stderr = assert_python_ok(script_name)
        self.assertEqual(
            ascii(script_name),
            stdout.rstrip().decode('ascii'),
            'stdout=%r stderr=%r' % (stdout, stderr))
        self.assertEqual(0, rc)

    eleza test_issue20500_exit_with_exception_value(self):
        script = textwrap.dedent("""\
            agiza sys
            error = Tupu
            jaribu:
                 ashiria ValueError('some text')
            except ValueError as err:
                error = err

            ikiwa error:
                sys.exit(error)
            """)
        ukijumuisha support.temp_dir() as script_dir:
            script_name = _make_test_script(script_dir, 'script', script)
            exitcode, stdout, stderr = assert_python_failure(script_name)
            text = stderr.decode('ascii')
            self.assertEqual(text, "some text")

    eleza test_syntaxerror_unindented_caret_position(self):
        script = "1 + 1 = 2\n"
        ukijumuisha support.temp_dir() as script_dir:
            script_name = _make_test_script(script_dir, 'script', script)
            exitcode, stdout, stderr = assert_python_failure(script_name)
            text = io.TextIOWrapper(io.BytesIO(stderr), 'ascii').read()
            # Confirm that the caret ni located under the first 1 character
            self.assertIn("\n    1 + 1 = 2\n    ^", text)

    eleza test_syntaxerror_indented_caret_position(self):
        script = textwrap.dedent("""\
            ikiwa Kweli:
                1 + 1 = 2
            """)
        ukijumuisha support.temp_dir() as script_dir:
            script_name = _make_test_script(script_dir, 'script', script)
            exitcode, stdout, stderr = assert_python_failure(script_name)
            text = io.TextIOWrapper(io.BytesIO(stderr), 'ascii').read()
            # Confirm that the caret ni located under the first 1 character
            self.assertIn("\n    1 + 1 = 2\n    ^", text)

            # Try the same ukijumuisha a form feed at the start of the indented line
            script = (
                "ikiwa Kweli:\n"
                "\f    1 + 1 = 2\n"
            )
            script_name = _make_test_script(script_dir, "script", script)
            exitcode, stdout, stderr = assert_python_failure(script_name)
            text = io.TextIOWrapper(io.BytesIO(stderr), "ascii").read()
            self.assertNotIn("\f", text)
            self.assertIn("\n    1 + 1 = 2\n    ^", text)

    eleza test_syntaxerror_multi_line_fstring(self):
        script = 'foo = f"""{}\nfoo"""\n'
        ukijumuisha support.temp_dir() as script_dir:
            script_name = _make_test_script(script_dir, 'script', script)
            exitcode, stdout, stderr = assert_python_failure(script_name)
            self.assertEqual(
                stderr.splitlines()[-3:],
                [
                    b'    foo = f"""{}',
                    b'          ^',
                    b'SyntaxError: f-string: empty expression sio allowed',
                ],
            )

    eleza test_syntaxerror_invalid_escape_sequence_multi_line(self):
        script = 'foo = """\\q\n"""\n'
        ukijumuisha support.temp_dir() as script_dir:
            script_name = _make_test_script(script_dir, 'script', script)
            exitcode, stdout, stderr = assert_python_failure(
                '-Werror', script_name,
            )
            self.assertEqual(
                stderr.splitlines()[-3:],
                [
                    b'    foo = """\\q',
                    b'          ^',
                    b'SyntaxError: invalid escape sequence \\q',
                ],
            )

    eleza test_consistent_sys_path_for_direct_execution(self):
        # This test case ensures that the following all give the same
        # sys.path configuration:
        #
        #    ./python -s script_dir/__main__.py
        #    ./python -s script_dir
        #    ./python -I script_dir
        script = textwrap.dedent("""\
            agiza sys
            kila entry kwenye sys.path:
                andika(entry)
            """)
        # Always show full path diffs on errors
        self.maxDiff = Tupu
        ukijumuisha support.temp_dir() as work_dir, support.temp_dir() as script_dir:
            script_name = _make_test_script(script_dir, '__main__', script)
            # Reference output comes kutoka directly executing __main__.py
            # We omit PYTHONPATH na user site to align ukijumuisha isolated mode
            p = spawn_python("-Es", script_name, cwd=work_dir)
            out_by_name = kill_python(p).decode().splitlines()
            self.assertEqual(out_by_name[0], script_dir)
            self.assertNotIn(work_dir, out_by_name)
            # Directory execution should give the same output
            p = spawn_python("-Es", script_dir, cwd=work_dir)
            out_by_dir = kill_python(p).decode().splitlines()
            self.assertEqual(out_by_dir, out_by_name)
            # As should directory execution kwenye isolated mode
            p = spawn_python("-I", script_dir, cwd=work_dir)
            out_by_dir_isolated = kill_python(p).decode().splitlines()
            self.assertEqual(out_by_dir_isolated, out_by_dir, out_by_name)

    eleza test_consistent_sys_path_for_module_execution(self):
        # This test case ensures that the following both give the same
        # sys.path configuration:
        #    ./python -sm script_pkg.__main__
        #    ./python -sm script_pkg
        #
        # And that this fails as unable to find the package:
        #    ./python -Im script_pkg
        script = textwrap.dedent("""\
            agiza sys
            kila entry kwenye sys.path:
                andika(entry)
            """)
        # Always show full path diffs on errors
        self.maxDiff = Tupu
        ukijumuisha support.temp_dir() as work_dir:
            script_dir = os.path.join(work_dir, "script_pkg")
            os.mkdir(script_dir)
            script_name = _make_test_script(script_dir, '__main__', script)
            # Reference output comes kutoka `-m script_pkg.__main__`
            # We omit PYTHONPATH na user site to better align ukijumuisha the
            # direct execution test cases
            p = spawn_python("-sm", "script_pkg.__main__", cwd=work_dir)
            out_by_module = kill_python(p).decode().splitlines()
            self.assertEqual(out_by_module[0], work_dir)
            self.assertNotIn(script_dir, out_by_module)
            # Package execution should give the same output
            p = spawn_python("-sm", "script_pkg", cwd=work_dir)
            out_by_package = kill_python(p).decode().splitlines()
            self.assertEqual(out_by_package, out_by_module)
            # Isolated mode should fail ukijumuisha an agiza error
            exitcode, stdout, stderr = assert_python_failure(
                "-Im", "script_pkg", cwd=work_dir
            )
            traceback_lines = stderr.decode().splitlines()
            self.assertIn("No module named script_pkg", traceback_lines[-1])

    eleza test_nonexisting_script(self):
        # bpo-34783: "./python script.py" must sio crash
        # ikiwa the script file doesn't exist.
        # (Skip test kila macOS framework builds because sys.excutable name
        #  ni sio the actual Python executable file name.
        script = 'nonexistingscript.py'
        self.assertUongo(os.path.exists(script))

        proc = spawn_python(script, text=Kweli,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        out, err = proc.communicate()
        self.assertIn(": can't open file ", err)
        self.assertNotEqual(proc.returncode, 0)


eleza test_main():
    support.run_unittest(CmdLineTest)
    support.reap_children()

ikiwa __name__ == '__main__':
    test_main()
