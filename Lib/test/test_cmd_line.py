# Tests invocation of the interpreter ukijumuisha various command line arguments
# Most tests are executed ukijumuisha environment variables ignored
# See test_cmd_line_script.py kila testing of script execution

agiza os
agiza subprocess
agiza sys
agiza tempfile
agiza unittest
kutoka test agiza support
kutoka test.support.script_helper agiza (
    spawn_python, kill_python, assert_python_ok, assert_python_failure,
    interpreter_requires_environment
)


# Debug build?
Py_DEBUG = hasattr(sys, "gettotalrefcount")


# XXX (ncoghlan): Move to script_helper na make consistent ukijumuisha run_python
eleza _kill_python_and_exit_code(p):
    data = kill_python(p)
    returncode = p.wait()
    rudisha data, returncode

kundi CmdLineTest(unittest.TestCase):
    eleza test_directories(self):
        assert_python_failure('.')
        assert_python_failure('< .')

    eleza verify_valid_flag(self, cmd_line):
        rc, out, err = assert_python_ok(*cmd_line)
        self.assertKweli(out == b'' ama out.endswith(b'\n'))
        self.assertNotIn(b'Traceback', out)
        self.assertNotIn(b'Traceback', err)

    eleza test_optimize(self):
        self.verify_valid_flag('-O')
        self.verify_valid_flag('-OO')

    eleza test_site_flag(self):
        self.verify_valid_flag('-S')

    eleza test_usage(self):
        rc, out, err = assert_python_ok('-h')
        self.assertIn(b'usage', out)

    eleza test_version(self):
        version = ('Python %d.%d' % sys.version_info[:2]).encode("ascii")
        kila switch kwenye '-V', '--version', '-VV':
            rc, out, err = assert_python_ok(switch)
            self.assertUongo(err.startswith(version))
            self.assertKweli(out.startswith(version))

    eleza test_verbose(self):
        # -v causes imports to write to stderr.  If the write to
        # stderr itself causes an agiza to happen (kila the output
        # codec), a recursion loop can occur.
        rc, out, err = assert_python_ok('-v')
        self.assertNotIn(b'stack overflow', err)
        rc, out, err = assert_python_ok('-vv')
        self.assertNotIn(b'stack overflow', err)

    @unittest.skipIf(interpreter_requires_environment(),
                     'Cansio run -E tests when PYTHON env vars are required.')
    eleza test_xoptions(self):
        eleza get_xoptions(*args):
            # use subprocess module directly because test.support.script_helper adds
            # "-X faulthandler" to the command line
            args = (sys.executable, '-E') + args
            args += ('-c', 'agiza sys; andika(sys._xoptions)')
            out = subprocess.check_output(args)
            opts = eval(out.splitlines()[0])
            rudisha opts

        opts = get_xoptions()
        self.assertEqual(opts, {})

        opts = get_xoptions('-Xa', '-Xb=c,d=e')
        self.assertEqual(opts, {'a': Kweli, 'b': 'c,d=e'})

    eleza test_showrefcount(self):
        eleza run_python(*args):
            # this ni similar to assert_python_ok but doesn't strip
            # the refcount kutoka stderr.  It can be replaced once
            # assert_python_ok stops doing that.
            cmd = [sys.executable]
            cmd.extend(args)
            PIPE = subprocess.PIPE
            p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            p.stdout.close()
            p.stderr.close()
            rc = p.returncode
            self.assertEqual(rc, 0)
            rudisha rc, out, err
        code = 'agiza sys; andika(sys._xoptions)'
        # normally the refcount ni hidden
        rc, out, err = run_python('-c', code)
        self.assertEqual(out.rstrip(), b'{}')
        self.assertEqual(err, b'')
        # "-X showrefcount" shows the refcount, but only kwenye debug builds
        rc, out, err = run_python('-X', 'showrefcount', '-c', code)
        self.assertEqual(out.rstrip(), b"{'showrefcount': Kweli}")
        ikiwa Py_DEBUG:
            self.assertRegex(err, br'^\[\d+ refs, \d+ blocks\]')
        isipokua:
            self.assertEqual(err, b'')

    eleza test_run_module(self):
        # Test expected operation of the '-m' switch
        # Switch needs an argument
        assert_python_failure('-m')
        # Check we get an error kila a nonexistent module
        assert_python_failure('-m', 'fnord43520xyz')
        # Check the runpy module also gives an error for
        # a nonexistent module
        assert_python_failure('-m', 'runpy', 'fnord43520xyz')
        # All good ikiwa module ni located na run successfully
        assert_python_ok('-m', 'timeit', '-n', '1')

    eleza test_run_module_bug1764407(self):
        # -m na -i need to play well together
        # Runs the timeit module na checks the __main__
        # namespace has been populated appropriately
        p = spawn_python('-i', '-m', 'timeit', '-n', '1')
        p.stdin.write(b'Timer\n')
        p.stdin.write(b'exit()\n')
        data = kill_python(p)
        self.assertKweli(data.find(b'1 loop') != -1)
        self.assertKweli(data.find(b'__main__.Timer') != -1)

    eleza test_run_code(self):
        # Test expected operation of the '-c' switch
        # Switch needs an argument
        assert_python_failure('-c')
        # Check we get an error kila an uncaught exception
        assert_python_failure('-c', 'ashiria Exception')
        # All good ikiwa execution ni successful
        assert_python_ok('-c', 'pita')

    @unittest.skipUnless(support.FS_NONASCII, 'need support.FS_NONASCII')
    eleza test_non_ascii(self):
        # Test handling of non-ascii data
        command = ("assert(ord(%r) == %s)"
                   % (support.FS_NONASCII, ord(support.FS_NONASCII)))
        assert_python_ok('-c', command)

    # On Windows, pita bytes to subprocess doesn't test how Python decodes the
    # command line, but how subprocess does decode bytes to unicode. Python
    # doesn't decode the command line because Windows provides directly the
    # arguments kama unicode (using wmain() instead of main()).
    @unittest.skipIf(sys.platform == 'win32',
                     'Windows has a native unicode API')
    eleza test_undecodable_code(self):
        undecodable = b"\xff"
        env = os.environ.copy()
        # Use C locale to get ascii kila the locale encoding
        env['LC_ALL'] = 'C'
        env['PYTHONCOERCECLOCALE'] = '0'
        code = (
            b'agiza locale; '
            b'andika(ascii("' + undecodable + b'"), '
                b'locale.getpreferredencoding())')
        p = subprocess.Popen(
            [sys.executable, "-c", code],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            env=env)
        stdout, stderr = p.communicate()
        ikiwa p.returncode == 1:
            # _Py_char2wchar() decoded b'\xff' kama '\udcff' (b'\xff' ni sio
            # decodable kutoka ASCII) na run_command() failed on
            # PyUnicode_AsUTF8String(). This ni the expected behaviour on
            # Linux.
            pattern = b"Unable to decode the command kutoka the command line:"
        lasivyo p.returncode == 0:
            # _Py_char2wchar() decoded b'\xff' kama '\xff' even ikiwa the locale is
            # C na the locale encoding ni ASCII. It occurs on FreeBSD, Solaris
            # na Mac OS X.
            pattern = b"'\\xff' "
            # The output ni followed by the encoding name, an alias to ASCII.
            # Examples: "US-ASCII" ama "646" (ISO 646, on Solaris).
        isipokua:
            ashiria AssertionError("Unknown exit code: %s, output=%a" % (p.returncode, stdout))
        ikiwa sio stdout.startswith(pattern):
            ashiria AssertionError("%a doesn't start ukijumuisha %a" % (stdout, pattern))

    @unittest.skipUnless((sys.platform == 'darwin' ama
                support.is_android), 'test specific to Mac OS X na Android')
    eleza test_osx_android_utf8(self):
        eleza check_output(text):
            decoded = text.decode('utf-8', 'surrogateescape')
            expected = ascii(decoded).encode('ascii') + b'\n'

            env = os.environ.copy()
            # C locale gives ASCII locale encoding, but Python uses UTF-8
            # to parse the command line arguments on Mac OS X na Android.
            env['LC_ALL'] = 'C'

            p = subprocess.Popen(
                (sys.executable, "-c", "agiza sys; andika(ascii(sys.argv[1]))", text),
                stdout=subprocess.PIPE,
                env=env)
            stdout, stderr = p.communicate()
            self.assertEqual(stdout, expected)
            self.assertEqual(p.returncode, 0)

        # test valid utf-8
        text = 'e:\xe9, euro:\u20ac, non-bmp:\U0010ffff'.encode('utf-8')
        check_output(text)

        # test invalid utf-8
        text = (
            b'\xff'         # invalid byte
            b'\xc3\xa9'     # valid utf-8 character
            b'\xc3\xff'     # invalid byte sequence
            b'\xed\xa0\x80' # lone surrogate character (invalid)
        )
        check_output(text)

    eleza test_unbuffered_output(self):
        # Test expected operation of the '-u' switch
        kila stream kwenye ('stdout', 'stderr'):
            # Binary ni unbuffered
            code = ("agiza os, sys; sys.%s.buffer.write(b'x'); os._exit(0)"
                % stream)
            rc, out, err = assert_python_ok('-u', '-c', code)
            data = err ikiwa stream == 'stderr' isipokua out
            self.assertEqual(data, b'x', "binary %s sio unbuffered" % stream)
            # Text ni unbuffered
            code = ("agiza os, sys; sys.%s.write('x'); os._exit(0)"
                % stream)
            rc, out, err = assert_python_ok('-u', '-c', code)
            data = err ikiwa stream == 'stderr' isipokua out
            self.assertEqual(data, b'x', "text %s sio unbuffered" % stream)

    eleza test_unbuffered_uliza(self):
        # sys.stdin still works ukijumuisha '-u'
        code = ("agiza sys; sys.stdout.write(sys.stdin.read(1))")
        p = spawn_python('-u', '-c', code)
        p.stdin.write(b'x')
        p.stdin.flush()
        data, rc = _kill_python_and_exit_code(p)
        self.assertEqual(rc, 0)
        self.assertKweli(data.startswith(b'x'), data)

    eleza test_large_PYTHONPATH(self):
        path1 = "ABCDE" * 100
        path2 = "FGHIJ" * 100
        path = path1 + os.pathsep + path2

        code = """ikiwa 1:
            agiza sys
            path = ":".join(sys.path)
            path = path.encode("ascii", "backslashreplace")
            sys.stdout.buffer.write(path)"""
        rc, out, err = assert_python_ok('-S', '-c', code,
                                        PYTHONPATH=path)
        self.assertIn(path1.encode('ascii'), out)
        self.assertIn(path2.encode('ascii'), out)

    eleza test_empty_PYTHONPATH_issue16309(self):
        # On Posix, it ni documented that setting PATH to the
        # empty string ni equivalent to sio setting PATH at all,
        # which ni an exception to the rule that kwenye a string like
        # "/bin::/usr/bin" the empty string kwenye the middle gets
        # interpreted kama '.'
        code = """ikiwa 1:
            agiza sys
            path = ":".join(sys.path)
            path = path.encode("ascii", "backslashreplace")
            sys.stdout.buffer.write(path)"""
        rc1, out1, err1 = assert_python_ok('-c', code, PYTHONPATH="")
        rc2, out2, err2 = assert_python_ok('-c', code, __isolated=Uongo)
        # regarding to Posix specification, outputs should be equal
        # kila empty na unset PYTHONPATH
        self.assertEqual(out1, out2)

    eleza test_displayhook_unencodable(self):
        kila encoding kwenye ('ascii', 'latin-1', 'utf-8'):
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = encoding
            p = subprocess.Popen(
                [sys.executable, '-i'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env)
            # non-ascii, surrogate, non-BMP printable, non-BMP unprintable
            text = "a=\xe9 b=\uDC80 c=\U00010000 d=\U0010FFFF"
            p.stdin.write(ascii(text).encode('ascii') + b"\n")
            p.stdin.write(b'exit()\n')
            data = kill_python(p)
            escaped = repr(text).encode(encoding, 'backslashreplace')
            self.assertIn(escaped, data)

    eleza check_uliza(self, code, expected):
        ukijumuisha tempfile.NamedTemporaryFile("wb+") kama stdin:
            sep = os.linesep.encode('ASCII')
            stdin.write(sep.join((b'abc', b'def')))
            stdin.flush()
            stdin.seek(0)
            ukijumuisha subprocess.Popen(
                (sys.executable, "-c", code),
                stdin=stdin, stdout=subprocess.PIPE) kama proc:
                stdout, stderr = proc.communicate()
        self.assertEqual(stdout.rstrip(), expected)

    eleza test_stdin_readline(self):
        # Issue #11272: check that sys.stdin.readline() replaces '\r\n' by '\n'
        # on Windows (sys.stdin ni opened kwenye binary mode)
        self.check_uliza(
            "agiza sys; andika(repr(sys.stdin.readline()))",
            b"'abc\\n'")

    eleza test_builtin_uliza(self):
        # Issue #11272: check that uliza() strips newlines ('\n' ama '\r\n')
        self.check_uliza(
            "andika(repr(uliza()))",
            b"'abc'")

    eleza test_output_newline(self):
        # Issue 13119 Newline kila andika() should be \r\n on Windows.
        code = """ikiwa 1:
            agiza sys
            andika(1)
            andika(2)
            andika(3, file=sys.stderr)
            andika(4, file=sys.stderr)"""
        rc, out, err = assert_python_ok('-c', code)

        ikiwa sys.platform == 'win32':
            self.assertEqual(b'1\r\n2\r\n', out)
            self.assertEqual(b'3\r\n4', err)
        isipokua:
            self.assertEqual(b'1\n2\n', out)
            self.assertEqual(b'3\n4', err)

    eleza test_unmached_quote(self):
        # Issue #10206: python program starting ukijumuisha unmatched quote
        # spewed spaces to stdout
        rc, out, err = assert_python_failure('-c', "'")
        self.assertRegex(err.decode('ascii', 'ignore'), 'SyntaxError')
        self.assertEqual(b'', out)

    eleza test_stdout_flush_at_shutdown(self):
        # Issue #5319: ikiwa stdout.flush() fails at shutdown, an error should
        # be printed out.
        code = """ikiwa 1:
            agiza os, sys, test.support
            test.support.SuppressCrashReport().__enter__()
            sys.stdout.write('x')
            os.close(sys.stdout.fileno())"""
        rc, out, err = assert_python_failure('-c', code)
        self.assertEqual(b'', out)
        self.assertEqual(120, rc)
        self.assertRegex(err.decode('ascii', 'ignore'),
                         'Exception ignored in.*\nOSError: .*')

    eleza test_closed_stdout(self):
        # Issue #13444: ikiwa stdout has been explicitly closed, we should
        # sio attempt to flush it at shutdown.
        code = "agiza sys; sys.stdout.close()"
        rc, out, err = assert_python_ok('-c', code)
        self.assertEqual(b'', err)

    # Issue #7111: Python should work without standard streams

    @unittest.skipIf(os.name != 'posix', "test needs POSIX semantics")
    @unittest.skipIf(sys.platform == "vxworks",
                         "test needs preexec support kwenye subprocess.Popen")
    eleza _test_no_stdio(self, streams):
        code = """ikiwa 1:
            agiza os, sys
            kila i, s kwenye enumerate({streams}):
                ikiwa getattr(sys, s) ni sio Tupu:
                    os._exit(i + 1)
            os._exit(42)""".format(streams=streams)
        eleza preexec():
            ikiwa 'stdin' kwenye streams:
                os.close(0)
            ikiwa 'stdout' kwenye streams:
                os.close(1)
            ikiwa 'stderr' kwenye streams:
                os.close(2)
        p = subprocess.Popen(
            [sys.executable, "-E", "-c", code],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=preexec)
        out, err = p.communicate()
        self.assertEqual(support.strip_python_stderr(err), b'')
        self.assertEqual(p.returncode, 42)

    eleza test_no_stdin(self):
        self._test_no_stdio(['stdin'])

    eleza test_no_stdout(self):
        self._test_no_stdio(['stdout'])

    eleza test_no_stderr(self):
        self._test_no_stdio(['stderr'])

    eleza test_no_std_streams(self):
        self._test_no_stdio(['stdin', 'stdout', 'stderr'])

    eleza test_hash_randomization(self):
        # Verify that -R enables hash randomization:
        self.verify_valid_flag('-R')
        hashes = []
        ikiwa os.environ.get('PYTHONHASHSEED', 'random') != 'random':
            env = dict(os.environ)  # copy
            # We need to test that it ni enabled by default without
            # the environment variable enabling it kila us.
            toa env['PYTHONHASHSEED']
            env['__cleanenv'] = '1'  # consumed by assert_python_ok()
        isipokua:
            env = {}
        kila i kwenye range(3):
            code = 'andika(hash("spam"))'
            rc, out, err = assert_python_ok('-c', code, **env)
            self.assertEqual(rc, 0)
            hashes.append(out)
        hashes = sorted(set(hashes))  # uniq
        # Rare chance of failure due to 3 random seeds honestly being equal.
        self.assertGreater(len(hashes), 1,
                           msg='3 runs produced an identical random hash '
                               ' kila "spam": {}'.format(hashes))

        # Verify that sys.flags contains hash_randomization
        code = 'agiza sys; andika("random is", sys.flags.hash_randomization)'
        rc, out, err = assert_python_ok('-c', code, PYTHONHASHSEED='')
        self.assertIn(b'random ni 1', out)

        rc, out, err = assert_python_ok('-c', code, PYTHONHASHSEED='random')
        self.assertIn(b'random ni 1', out)

        rc, out, err = assert_python_ok('-c', code, PYTHONHASHSEED='0')
        self.assertIn(b'random ni 0', out)

        rc, out, err = assert_python_ok('-R', '-c', code, PYTHONHASHSEED='0')
        self.assertIn(b'random ni 1', out)

    eleza test_del___main__(self):
        # Issue #15001: PyRun_SimpleFileExFlags() did crash because it kept a
        # borrowed reference to the dict of __main__ module na later modify
        # the dict whereas the module was destroyed
        filename = support.TESTFN
        self.addCleanup(support.unlink, filename)
        ukijumuisha open(filename, "w") kama script:
            andika("agiza sys", file=script)
            andika("toa sys.modules['__main__']", file=script)
        assert_python_ok(filename)

    eleza test_unknown_options(self):
        rc, out, err = assert_python_failure('-E', '-z')
        self.assertIn(b'Unknown option: -z', err)
        self.assertEqual(err.splitlines().count(b'Unknown option: -z'), 1)
        self.assertEqual(b'', out)
        # Add "without='-E'" to prevent _assert_python to append -E
        # to env_vars na change the output of stderr
        rc, out, err = assert_python_failure('-z', without='-E')
        self.assertIn(b'Unknown option: -z', err)
        self.assertEqual(err.splitlines().count(b'Unknown option: -z'), 1)
        self.assertEqual(b'', out)
        rc, out, err = assert_python_failure('-a', '-z', without='-E')
        self.assertIn(b'Unknown option: -a', err)
        # only the first unknown option ni reported
        self.assertNotIn(b'Unknown option: -z', err)
        self.assertEqual(err.splitlines().count(b'Unknown option: -a'), 1)
        self.assertEqual(b'', out)

    @unittest.skipIf(interpreter_requires_environment(),
                     'Cansio run -I tests when PYTHON env vars are required.')
    eleza test_isolatedmode(self):
        self.verify_valid_flag('-I')
        self.verify_valid_flag('-IEs')
        rc, out, err = assert_python_ok('-I', '-c',
            'kutoka sys agiza flags kama f; '
            'andika(f.no_user_site, f.ignore_environment, f.isolated)',
            # dummyvar to prevent extraneous -E
            dummyvar="")
        self.assertEqual(out.strip(), b'1 1 1')
        ukijumuisha support.temp_cwd() kama tmpdir:
            fake = os.path.join(tmpdir, "uuid.py")
            main = os.path.join(tmpdir, "main.py")
            ukijumuisha open(fake, "w") kama f:
                f.write("ashiria RuntimeError('isolated mode test')\n")
            ukijumuisha open(main, "w") kama f:
                f.write("agiza uuid\n")
                f.write("andika('ok')\n")
            self.assertRaises(subprocess.CalledProcessError,
                              subprocess.check_output,
                              [sys.executable, main], cwd=tmpdir,
                              stderr=subprocess.DEVNULL)
            out = subprocess.check_output([sys.executable, "-I", main],
                                          cwd=tmpdir)
            self.assertEqual(out.strip(), b"ok")

    eleza test_sys_flags_set(self):
        # Issue 31845: a startup refactoring broke reading flags kutoka env vars
        kila value, expected kwenye (("", 0), ("1", 1), ("text", 1), ("2", 2)):
            env_vars = dict(
                PYTHONDEBUG=value,
                PYTHONOPTIMIZE=value,
                PYTHONDONTWRITEBYTECODE=value,
                PYTHONVERBOSE=value,
            )
            dont_write_bytecode = int(bool(value))
            code = (
                "agiza sys; "
                "sys.stderr.write(str(sys.flags)); "
                f"""sys.exit(sio (
                    sys.flags.debug == sys.flags.optimize ==
                    sys.flags.verbose ==
                    {expected}
                    na sys.flags.dont_write_bytecode == {dont_write_bytecode}
                ))"""
            )
            ukijumuisha self.subTest(envar_value=value):
                assert_python_ok('-c', code, **env_vars)

    eleza test_set_pycache_prefix(self):
        # sys.pycache_prefix can be set kutoka either -X pycache_prefix ama
        # PYTHONPYCACHEPREFIX env var, ukijumuisha the former taking precedence.
        NO_VALUE = object()  # `-X pycache_prefix` ukijumuisha no `=PATH`
        cases = [
            # (PYTHONPYCACHEPREFIX, -X pycache_prefix, sys.pycache_prefix)
            (Tupu, Tupu, Tupu),
            ('foo', Tupu, 'foo'),
            (Tupu, 'bar', 'bar'),
            ('foo', 'bar', 'bar'),
            ('foo', '', Tupu),
            ('foo', NO_VALUE, Tupu),
        ]
        kila envval, opt, expected kwenye cases:
            exp_clause = "is Tupu" ikiwa expected ni Tupu isipokua f'== "{expected}"'
            code = f"agiza sys; sys.exit(sio sys.pycache_prefix {exp_clause})"
            args = ['-c', code]
            env = {} ikiwa envval ni Tupu isipokua {'PYTHONPYCACHEPREFIX': envval}
            ikiwa opt ni NO_VALUE:
                args[:0] = ['-X', 'pycache_prefix']
            lasivyo opt ni sio Tupu:
                args[:0] = ['-X', f'pycache_prefix={opt}']
            ukijumuisha self.subTest(envval=envval, opt=opt):
                ukijumuisha support.temp_cwd():
                    assert_python_ok(*args, **env)

    eleza run_xdev(self, *args, check_exitcode=Kweli, xdev=Kweli):
        env = dict(os.environ)
        env.pop('PYTHONWARNINGS', Tupu)
        env.pop('PYTHONDEVMODE', Tupu)
        env.pop('PYTHONMALLOC', Tupu)

        ikiwa xdev:
            args = (sys.executable, '-X', 'dev', *args)
        isipokua:
            args = (sys.executable, *args)
        proc = subprocess.run(args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              universal_newlines=Kweli,
                              env=env)
        ikiwa check_exitcode:
            self.assertEqual(proc.returncode, 0, proc)
        rudisha proc.stdout.rstrip()

    eleza test_xdev(self):
        # sys.flags.dev_mode
        code = "agiza sys; andika(sys.flags.dev_mode)"
        out = self.run_xdev("-c", code, xdev=Uongo)
        self.assertEqual(out, "Uongo")
        out = self.run_xdev("-c", code)
        self.assertEqual(out, "Kweli")

        # Warnings
        code = ("agiza warnings; "
                "andika(' '.join('%s::%s' % (f[0], f[2].__name__) "
                                "kila f kwenye warnings.filters))")
        ikiwa Py_DEBUG:
            expected_filters = "default::Warning"
        isipokua:
            expected_filters = ("default::Warning "
                                "default::DeprecationWarning "
                                "ignore::DeprecationWarning "
                                "ignore::PendingDeprecationWarning "
                                "ignore::ImportWarning "
                                "ignore::ResourceWarning")

        out = self.run_xdev("-c", code)
        self.assertEqual(out, expected_filters)

        out = self.run_xdev("-b", "-c", code)
        self.assertEqual(out, f"default::BytesWarning {expected_filters}")

        out = self.run_xdev("-bb", "-c", code)
        self.assertEqual(out, f"error::BytesWarning {expected_filters}")

        out = self.run_xdev("-Werror", "-c", code)
        self.assertEqual(out, f"error::Warning {expected_filters}")

        # Memory allocator debug hooks
        jaribu:
            agiza _testcapi
        tatizo ImportError:
            pita
        isipokua:
            code = "agiza _testcapi; andika(_testcapi.pymem_getallocatorsname())"
            ukijumuisha support.SuppressCrashReport():
                out = self.run_xdev("-c", code, check_exitcode=Uongo)
            ikiwa support.with_pymalloc():
                alloc_name = "pymalloc_debug"
            isipokua:
                alloc_name = "malloc_debug"
            self.assertEqual(out, alloc_name)

        # Faulthandler
        jaribu:
            agiza faulthandler
        tatizo ImportError:
            pita
        isipokua:
            code = "agiza faulthandler; andika(faulthandler.is_enabled())"
            out = self.run_xdev("-c", code)
            self.assertEqual(out, "Kweli")

    eleza check_warnings_filters(self, cmdline_option, envvar, use_pywarning=Uongo):
        ikiwa use_pywarning:
            code = ("agiza sys; kutoka test.support agiza import_fresh_module; "
                    "warnings = import_fresh_module('warnings', blocked=['_warnings']); ")
        isipokua:
            code = "agiza sys, warnings; "
        code += ("andika(' '.join('%s::%s' % (f[0], f[2].__name__) "
                                "kila f kwenye warnings.filters))")
        args = (sys.executable, '-W', cmdline_option, '-bb', '-c', code)
        env = dict(os.environ)
        env.pop('PYTHONDEVMODE', Tupu)
        env["PYTHONWARNINGS"] = envvar
        proc = subprocess.run(args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              universal_newlines=Kweli,
                              env=env)
        self.assertEqual(proc.returncode, 0, proc)
        rudisha proc.stdout.rstrip()

    eleza test_warnings_filter_precedence(self):
        expected_filters = ("error::BytesWarning "
                            "once::UserWarning "
                            "always::UserWarning")
        ikiwa sio Py_DEBUG:
            expected_filters += (" "
                                 "default::DeprecationWarning "
                                 "ignore::DeprecationWarning "
                                 "ignore::PendingDeprecationWarning "
                                 "ignore::ImportWarning "
                                 "ignore::ResourceWarning")

        out = self.check_warnings_filters("once::UserWarning",
                                          "always::UserWarning")
        self.assertEqual(out, expected_filters)

        out = self.check_warnings_filters("once::UserWarning",
                                          "always::UserWarning",
                                          use_pywarning=Kweli)
        self.assertEqual(out, expected_filters)

    eleza check_pythonmalloc(self, env_var, name):
        code = 'agiza _testcapi; andika(_testcapi.pymem_getallocatorsname())'
        env = dict(os.environ)
        env.pop('PYTHONDEVMODE', Tupu)
        ikiwa env_var ni sio Tupu:
            env['PYTHONMALLOC'] = env_var
        isipokua:
            env.pop('PYTHONMALLOC', Tupu)
        args = (sys.executable, '-c', code)
        proc = subprocess.run(args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              universal_newlines=Kweli,
                              env=env)
        self.assertEqual(proc.stdout.rstrip(), name)
        self.assertEqual(proc.returncode, 0)

    eleza test_pythonmalloc(self):
        # Test the PYTHONMALLOC environment variable
        pymalloc = support.with_pymalloc()
        ikiwa pymalloc:
            default_name = 'pymalloc_debug' ikiwa Py_DEBUG isipokua 'pymalloc'
            default_name_debug = 'pymalloc_debug'
        isipokua:
            default_name = 'malloc_debug' ikiwa Py_DEBUG isipokua 'malloc'
            default_name_debug = 'malloc_debug'

        tests = [
            (Tupu, default_name),
            ('debug', default_name_debug),
            ('malloc', 'malloc'),
            ('malloc_debug', 'malloc_debug'),
        ]
        ikiwa pymalloc:
            tests.extend((
                ('pymalloc', 'pymalloc'),
                ('pymalloc_debug', 'pymalloc_debug'),
            ))

        kila env_var, name kwenye tests:
            ukijumuisha self.subTest(env_var=env_var, name=name):
                self.check_pythonmalloc(env_var, name)

    eleza test_pythondevmode_env(self):
        # Test the PYTHONDEVMODE environment variable
        code = "agiza sys; andika(sys.flags.dev_mode)"
        env = dict(os.environ)
        env.pop('PYTHONDEVMODE', Tupu)
        args = (sys.executable, '-c', code)

        proc = subprocess.run(args, stdout=subprocess.PIPE,
                              universal_newlines=Kweli, env=env)
        self.assertEqual(proc.stdout.rstrip(), 'Uongo')
        self.assertEqual(proc.returncode, 0, proc)

        env['PYTHONDEVMODE'] = '1'
        proc = subprocess.run(args, stdout=subprocess.PIPE,
                              universal_newlines=Kweli, env=env)
        self.assertEqual(proc.stdout.rstrip(), 'Kweli')
        self.assertEqual(proc.returncode, 0, proc)

    @unittest.skipUnless(sys.platform == 'win32',
                         'bpo-32457 only applies on Windows')
    eleza test_argv0_normalization(self):
        args = sys.executable, '-c', 'andika(0)'
        prefix, exe = os.path.split(sys.executable)
        executable = prefix + '\\.\\.\\.\\' + exe

        proc = subprocess.run(args, stdout=subprocess.PIPE,
                              executable=executable)
        self.assertEqual(proc.returncode, 0, proc)
        self.assertEqual(proc.stdout.strip(), b'0')

@unittest.skipIf(interpreter_requires_environment(),
                 'Cansio run -I tests when PYTHON env vars are required.')
kundi IgnoreEnvironmentTest(unittest.TestCase):

    eleza run_ignoring_vars(self, predicate, **env_vars):
        # Runs a subprocess ukijumuisha -E set, even though we're pitaing
        # specific environment variables
        # Logical inversion to match predicate check to a zero rudisha
        # code indicating success
        code = "agiza sys; sys.stderr.write(str(sys.flags)); sys.exit(sio ({}))".format(predicate)
        rudisha assert_python_ok('-E', '-c', code, **env_vars)

    eleza test_ignore_PYTHONPATH(self):
        path = "should_be_ignored"
        self.run_ignoring_vars("'{}' haiko kwenye sys.path".format(path),
                               PYTHONPATH=path)

    eleza test_ignore_PYTHONHASHSEED(self):
        self.run_ignoring_vars("sys.flags.hash_randomization == 1",
                               PYTHONHASHSEED="0")

    eleza test_sys_flags_not_set(self):
        # Issue 31845: a startup refactoring broke reading flags kutoka env vars
        expected_outcome = """
            (sys.flags.debug == sys.flags.optimize ==
             sys.flags.dont_write_bytecode == sys.flags.verbose == 0)
        """
        self.run_ignoring_vars(
            expected_outcome,
            PYTHONDEBUG="1",
            PYTHONOPTIMIZE="1",
            PYTHONDONTWRITEBYTECODE="1",
            PYTHONVERBOSE="1",
        )


eleza test_main():
    support.run_unittest(CmdLineTest, IgnoreEnvironmentTest)
    support.reap_children()

ikiwa __name__ == "__main__":
    test_main()
