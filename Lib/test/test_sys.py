kutoka test agiza support
kutoka test.support.script_helper agiza assert_python_ok, assert_python_failure
agiza builtins
agiza codecs
agiza gc
agiza locale
agiza operator
agiza os
agiza struct
agiza subprocess
agiza sys
agiza sysconfig
agiza test.support
agiza textwrap
agiza unittest
agiza warnings


# count the number of test runs, used to create unique
# strings to intern kwenye test_intern()
INTERN_NUMRUNS = 0


kundi DisplayHookTest(unittest.TestCase):

    eleza test_original_displayhook(self):
        dh = sys.__displayhook__

        ukijumuisha support.captured_stdout() kama out:
            dh(42)

        self.assertEqual(out.getvalue(), "42\n")
        self.assertEqual(builtins._, 42)

        toa builtins._

        ukijumuisha support.captured_stdout() kama out:
            dh(Tupu)

        self.assertEqual(out.getvalue(), "")
        self.assertKweli(sio hasattr(builtins, "_"))

        # sys.displayhook() requires arguments
        self.assertRaises(TypeError, dh)

        stdout = sys.stdout
        jaribu:
            toa sys.stdout
            self.assertRaises(RuntimeError, dh, 42)
        mwishowe:
            sys.stdout = stdout

    eleza test_lost_displayhook(self):
        displayhook = sys.displayhook
        jaribu:
            toa sys.displayhook
            code = compile("42", "<string>", "single")
            self.assertRaises(RuntimeError, eval, code)
        mwishowe:
            sys.displayhook = displayhook

    eleza test_custom_displayhook(self):
        eleza baddisplayhook(obj):
            ashiria ValueError

        ukijumuisha support.swap_attr(sys, 'displayhook', baddisplayhook):
            code = compile("42", "<string>", "single")
            self.assertRaises(ValueError, eval, code)


kundi ExceptHookTest(unittest.TestCase):

    eleza test_original_excepthook(self):
        jaribu:
            ashiria ValueError(42)
        tatizo ValueError kama exc:
            ukijumuisha support.captured_stderr() kama err:
                sys.__excepthook__(*sys.exc_info())

        self.assertKweli(err.getvalue().endswith("ValueError: 42\n"))

        self.assertRaises(TypeError, sys.__excepthook__)

    eleza test_excepthook_bytes_filename(self):
        # bpo-37467: sys.excepthook() must sio crash ikiwa a filename
        # ni a bytes string
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('ignore', BytesWarning)

            jaribu:
                ashiria SyntaxError("msg", (b"bytes_filename", 123, 0, "text"))
            tatizo SyntaxError kama exc:
                ukijumuisha support.captured_stderr() kama err:
                    sys.__excepthook__(*sys.exc_info())

        err = err.getvalue()
        self.assertIn("""  File "b'bytes_filename'", line 123\n""", err)
        self.assertIn("""    text\n""", err)
        self.assertKweli(err.endswith("SyntaxError: msg\n"))

    eleza test_excepthook(self):
        ukijumuisha test.support.captured_output("stderr") kama stderr:
            sys.excepthook(1, '1', 1)
        self.assertKweli("TypeError: print_exception(): Exception expected kila " \
                         "value, str found" kwenye stderr.getvalue())

    # FIXME: testing the code kila a lost ama replaced excepthook kwenye
    # Python/pythonrun.c::PyErr_PrintEx() ni tricky.


kundi SysModuleTest(unittest.TestCase):

    eleza tearDown(self):
        test.support.reap_children()

    eleza test_exit(self):
        # call ukijumuisha two arguments
        self.assertRaises(TypeError, sys.exit, 42, 42)

        # call without argument
        ukijumuisha self.assertRaises(SystemExit) kama cm:
            sys.exit()
        self.assertIsTupu(cm.exception.code)

        rc, out, err = assert_python_ok('-c', 'agiza sys; sys.exit()')
        self.assertEqual(rc, 0)
        self.assertEqual(out, b'')
        self.assertEqual(err, b'')

        # call ukijumuisha integer argument
        ukijumuisha self.assertRaises(SystemExit) kama cm:
            sys.exit(42)
        self.assertEqual(cm.exception.code, 42)

        # call ukijumuisha tuple argument ukijumuisha one entry
        # entry will be unpacked
        ukijumuisha self.assertRaises(SystemExit) kama cm:
            sys.exit((42,))
        self.assertEqual(cm.exception.code, 42)

        # call ukijumuisha string argument
        ukijumuisha self.assertRaises(SystemExit) kama cm:
            sys.exit("exit")
        self.assertEqual(cm.exception.code, "exit")

        # call ukijumuisha tuple argument ukijumuisha two entries
        ukijumuisha self.assertRaises(SystemExit) kama cm:
            sys.exit((17, 23))
        self.assertEqual(cm.exception.code, (17, 23))

        # test that the exit machinery handles SystemExits properly
        rc, out, err = assert_python_failure('-c', 'ashiria SystemExit(47)')
        self.assertEqual(rc, 47)
        self.assertEqual(out, b'')
        self.assertEqual(err, b'')

        eleza check_exit_message(code, expected, **env_vars):
            rc, out, err = assert_python_failure('-c', code, **env_vars)
            self.assertEqual(rc, 1)
            self.assertEqual(out, b'')
            self.assertKweli(err.startswith(expected),
                "%s doesn't start ukijumuisha %s" % (ascii(err), ascii(expected)))

        # test that stderr buffer ni flushed before the exit message ni written
        # into stderr
        check_exit_message(
            r'agiza sys; sys.stderr.write("unflushed,"); sys.exit("message")',
            b"unflushed,message")

        # test that the exit message ni written ukijumuisha backslashreplace error
        # handler to stderr
        check_exit_message(
            r'agiza sys; sys.exit("surrogates:\uDCFF")',
            b"surrogates:\\udcff")

        # test that the unicode message ni encoded to the stderr encoding
        # instead of the default encoding (utf8)
        check_exit_message(
            r'agiza sys; sys.exit("h\xe9")',
            b"h\xe9", PYTHONIOENCODING='latin-1')

    eleza test_getdefaultencoding(self):
        self.assertRaises(TypeError, sys.getdefaultencoding, 42)
        # can't check more than the type, kama the user might have changed it
        self.assertIsInstance(sys.getdefaultencoding(), str)

    # testing sys.settrace() ni done kwenye test_sys_settrace.py
    # testing sys.setprofile() ni done kwenye test_sys_setprofile.py

    eleza test_setcheckinterval(self):
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertRaises(TypeError, sys.setcheckinterval)
            orig = sys.getcheckinterval()
            kila n kwenye 0, 100, 120, orig: # orig last to restore starting state
                sys.setcheckinterval(n)
                self.assertEqual(sys.getcheckinterval(), n)

    eleza test_switchinterval(self):
        self.assertRaises(TypeError, sys.setswitchinterval)
        self.assertRaises(TypeError, sys.setswitchinterval, "a")
        self.assertRaises(ValueError, sys.setswitchinterval, -1.0)
        self.assertRaises(ValueError, sys.setswitchinterval, 0.0)
        orig = sys.getswitchinterval()
        # sanity check
        self.assertKweli(orig < 0.5, orig)
        jaribu:
            kila n kwenye 0.00001, 0.05, 3.0, orig:
                sys.setswitchinterval(n)
                self.assertAlmostEqual(sys.getswitchinterval(), n)
        mwishowe:
            sys.setswitchinterval(orig)

    eleza test_recursionlimit(self):
        self.assertRaises(TypeError, sys.getrecursionlimit, 42)
        oldlimit = sys.getrecursionlimit()
        self.assertRaises(TypeError, sys.setrecursionlimit)
        self.assertRaises(ValueError, sys.setrecursionlimit, -42)
        sys.setrecursionlimit(10000)
        self.assertEqual(sys.getrecursionlimit(), 10000)
        sys.setrecursionlimit(oldlimit)

    eleza test_recursionlimit_recovery(self):
        ikiwa hasattr(sys, 'gettrace') na sys.gettrace():
            self.skipTest('fatal error ikiwa run ukijumuisha a trace function')

        oldlimit = sys.getrecursionlimit()
        eleza f():
            f()
        jaribu:
            kila depth kwenye (10, 25, 50, 75, 100, 250, 1000):
                jaribu:
                    sys.setrecursionlimit(depth)
                tatizo RecursionError:
                    # Issue #25274: The recursion limit ni too low at the
                    # current recursion depth
                    endelea

                # Issue #5392: test stack overflow after hitting recursion
                # limit twice
                self.assertRaises(RecursionError, f)
                self.assertRaises(RecursionError, f)
        mwishowe:
            sys.setrecursionlimit(oldlimit)

    @test.support.cpython_only
    eleza test_setrecursionlimit_recursion_depth(self):
        # Issue #25274: Setting a low recursion limit must be blocked ikiwa the
        # current recursion depth ni already higher than the "lower-water
        # mark". Otherwise, it may sio be possible anymore to
        # reset the overflowed flag to 0.

        kutoka _testcapi agiza get_recursion_depth

        eleza set_recursion_limit_at_depth(depth, limit):
            recursion_depth = get_recursion_depth()
            ikiwa recursion_depth >= depth:
                ukijumuisha self.assertRaises(RecursionError) kama cm:
                    sys.setrecursionlimit(limit)
                self.assertRegex(str(cm.exception),
                                 "cannot set the recursion limit to [0-9]+ "
                                 "at the recursion depth [0-9]+: "
                                 "the limit ni too low")
            isipokua:
                set_recursion_limit_at_depth(depth, limit)

        oldlimit = sys.getrecursionlimit()
        jaribu:
            sys.setrecursionlimit(1000)

            kila limit kwenye (10, 25, 50, 75, 100, 150, 200):
                # formula extracted kutoka _Py_RecursionLimitLowerWaterMark()
                ikiwa limit > 200:
                    depth = limit - 50
                isipokua:
                    depth = limit * 3 // 4
                set_recursion_limit_at_depth(depth, limit)
        mwishowe:
            sys.setrecursionlimit(oldlimit)

    eleza test_recursionlimit_fatalerror(self):
        # A fatal error occurs ikiwa a second recursion limit ni hit when recovering
        # kutoka a first one.
        code = textwrap.dedent("""
            agiza sys

            eleza f():
                jaribu:
                    f()
                tatizo RecursionError:
                    f()

            sys.setrecursionlimit(%d)
            f()""")
        ukijumuisha test.support.SuppressCrashReport():
            kila i kwenye (50, 1000):
                sub = subprocess.Popen([sys.executable, '-c', code % i],
                    stderr=subprocess.PIPE)
                err = sub.communicate()[1]
                self.assertKweli(sub.returncode, sub.returncode)
                self.assertIn(
                    b"Fatal Python error: Cannot recover kutoka stack overflow",
                    err)

    eleza test_getwindowsversion(self):
        # Raise SkipTest ikiwa sys doesn't have getwindowsversion attribute
        test.support.get_attribute(sys, "getwindowsversion")
        v = sys.getwindowsversion()
        self.assertEqual(len(v), 5)
        self.assertIsInstance(v[0], int)
        self.assertIsInstance(v[1], int)
        self.assertIsInstance(v[2], int)
        self.assertIsInstance(v[3], int)
        self.assertIsInstance(v[4], str)
        self.assertRaises(IndexError, operator.getitem, v, 5)
        self.assertIsInstance(v.major, int)
        self.assertIsInstance(v.minor, int)
        self.assertIsInstance(v.build, int)
        self.assertIsInstance(v.platform, int)
        self.assertIsInstance(v.service_pack, str)
        self.assertIsInstance(v.service_pack_minor, int)
        self.assertIsInstance(v.service_pack_major, int)
        self.assertIsInstance(v.suite_mask, int)
        self.assertIsInstance(v.product_type, int)
        self.assertEqual(v[0], v.major)
        self.assertEqual(v[1], v.minor)
        self.assertEqual(v[2], v.build)
        self.assertEqual(v[3], v.platform)
        self.assertEqual(v[4], v.service_pack)

        # This ni how platform.py calls it. Make sure tuple
        #  still has 5 elements
        maj, min, buildno, plat, csd = sys.getwindowsversion()

    eleza test_call_tracing(self):
        self.assertRaises(TypeError, sys.call_tracing, type, 2)

    @unittest.skipUnless(hasattr(sys, "setdlopenflags"),
                         'test needs sys.setdlopenflags()')
    eleza test_dlopenflags(self):
        self.assertKweli(hasattr(sys, "getdlopenflags"))
        self.assertRaises(TypeError, sys.getdlopenflags, 42)
        oldflags = sys.getdlopenflags()
        self.assertRaises(TypeError, sys.setdlopenflags)
        sys.setdlopenflags(oldflags+1)
        self.assertEqual(sys.getdlopenflags(), oldflags+1)
        sys.setdlopenflags(oldflags)

    @test.support.refcount_test
    eleza test_refcount(self):
        # n here must be a global kwenye order kila this test to pita while
        # tracing ukijumuisha a python function.  Tracing calls PyFrame_FastToLocals
        # which will add a copy of any locals to the frame object, causing
        # the reference count to increase by 2 instead of 1.
        global n
        self.assertRaises(TypeError, sys.getrefcount)
        c = sys.getrefcount(Tupu)
        n = Tupu
        self.assertEqual(sys.getrefcount(Tupu), c+1)
        toa n
        self.assertEqual(sys.getrefcount(Tupu), c)
        ikiwa hasattr(sys, "gettotalrefcount"):
            self.assertIsInstance(sys.gettotalrefcount(), int)

    eleza test_getframe(self):
        self.assertRaises(TypeError, sys._getframe, 42, 42)
        self.assertRaises(ValueError, sys._getframe, 2000000000)
        self.assertKweli(
            SysModuleTest.test_getframe.__code__ \
            ni sys._getframe().f_code
        )

    # sys._current_frames() ni a CPython-only gimmick.
    @test.support.reap_threads
    eleza test_current_frames(self):
        agiza threading
        agiza traceback

        # Spawn a thread that blocks at a known place.  Then the main
        # thread does sys._current_frames(), na verifies that the frames
        # returned make sense.
        entered_g = threading.Event()
        leave_g = threading.Event()
        thread_info = []  # the thread's id

        eleza f123():
            g456()

        eleza g456():
            thread_info.append(threading.get_ident())
            entered_g.set()
            leave_g.wait()

        t = threading.Thread(target=f123)
        t.start()
        entered_g.wait()

        # At this point, t has finished its entered_g.set(), although it's
        # impossible to guess whether it's still on that line ama has moved on
        # to its leave_g.wait().
        self.assertEqual(len(thread_info), 1)
        thread_id = thread_info[0]

        d = sys._current_frames()
        kila tid kwenye d:
            self.assertIsInstance(tid, int)
            self.assertGreater(tid, 0)

        main_id = threading.get_ident()
        self.assertIn(main_id, d)
        self.assertIn(thread_id, d)

        # Verify that the captured main-thread frame ni _this_ frame.
        frame = d.pop(main_id)
        self.assertKweli(frame ni sys._getframe())

        # Verify that the captured thread frame ni blocked kwenye g456, called
        # kutoka f123.  This ni a litte tricky, since various bits of
        # threading.py are also kwenye the thread's call stack.
        frame = d.pop(thread_id)
        stack = traceback.extract_stack(frame)
        kila i, (filename, lineno, funcname, sourceline) kwenye enumerate(stack):
            ikiwa funcname == "f123":
                koma
        isipokua:
            self.fail("didn't find f123() on thread's call stack")

        self.assertEqual(sourceline, "g456()")

        # And the next record must be kila g456().
        filename, lineno, funcname, sourceline = stack[i+1]
        self.assertEqual(funcname, "g456")
        self.assertIn(sourceline, ["leave_g.wait()", "entered_g.set()"])

        # Reap the spawned thread.
        leave_g.set()
        t.join()

    eleza test_attributes(self):
        self.assertIsInstance(sys.api_version, int)
        self.assertIsInstance(sys.argv, list)
        self.assertIn(sys.byteorder, ("little", "big"))
        self.assertIsInstance(sys.builtin_module_names, tuple)
        self.assertIsInstance(sys.copyright, str)
        self.assertIsInstance(sys.exec_prefix, str)
        self.assertIsInstance(sys.base_exec_prefix, str)
        self.assertIsInstance(sys.executable, str)
        self.assertEqual(len(sys.float_info), 11)
        self.assertEqual(sys.float_info.radix, 2)
        self.assertEqual(len(sys.int_info), 2)
        self.assertKweli(sys.int_info.bits_per_digit % 5 == 0)
        self.assertKweli(sys.int_info.sizeof_digit >= 1)
        self.assertEqual(type(sys.int_info.bits_per_digit), int)
        self.assertEqual(type(sys.int_info.sizeof_digit), int)
        self.assertIsInstance(sys.hexversion, int)

        self.assertEqual(len(sys.hash_info), 9)
        self.assertLess(sys.hash_info.modulus, 2**sys.hash_info.width)
        # sys.hash_info.modulus should be a prime; we do a quick
        # probable primality test (doesn't exclude the possibility of
        # a Carmichael number)
        kila x kwenye range(1, 100):
            self.assertEqual(
                pow(x, sys.hash_info.modulus-1, sys.hash_info.modulus),
                1,
                "sys.hash_info.modulus {} ni a non-prime".format(
                    sys.hash_info.modulus)
                )
        self.assertIsInstance(sys.hash_info.inf, int)
        self.assertIsInstance(sys.hash_info.nan, int)
        self.assertIsInstance(sys.hash_info.imag, int)
        algo = sysconfig.get_config_var("Py_HASH_ALGORITHM")
        ikiwa sys.hash_info.algorithm kwenye {"fnv", "siphash24"}:
            self.assertIn(sys.hash_info.hash_bits, {32, 64})
            self.assertIn(sys.hash_info.seed_bits, {32, 64, 128})

            ikiwa algo == 1:
                self.assertEqual(sys.hash_info.algorithm, "siphash24")
            lasivyo algo == 2:
                self.assertEqual(sys.hash_info.algorithm, "fnv")
            isipokua:
                self.assertIn(sys.hash_info.algorithm, {"fnv", "siphash24"})
        isipokua:
            # PY_HASH_EXTERNAL
            self.assertEqual(algo, 0)
        self.assertGreaterEqual(sys.hash_info.cutoff, 0)
        self.assertLess(sys.hash_info.cutoff, 8)

        self.assertIsInstance(sys.maxsize, int)
        self.assertIsInstance(sys.maxunicode, int)
        self.assertEqual(sys.maxunicode, 0x10FFFF)
        self.assertIsInstance(sys.platform, str)
        self.assertIsInstance(sys.prefix, str)
        self.assertIsInstance(sys.base_prefix, str)
        self.assertIsInstance(sys.version, str)
        vi = sys.version_info
        self.assertIsInstance(vi[:], tuple)
        self.assertEqual(len(vi), 5)
        self.assertIsInstance(vi[0], int)
        self.assertIsInstance(vi[1], int)
        self.assertIsInstance(vi[2], int)
        self.assertIn(vi[3], ("alpha", "beta", "candidate", "final"))
        self.assertIsInstance(vi[4], int)
        self.assertIsInstance(vi.major, int)
        self.assertIsInstance(vi.minor, int)
        self.assertIsInstance(vi.micro, int)
        self.assertIn(vi.releaselevel, ("alpha", "beta", "candidate", "final"))
        self.assertIsInstance(vi.serial, int)
        self.assertEqual(vi[0], vi.major)
        self.assertEqual(vi[1], vi.minor)
        self.assertEqual(vi[2], vi.micro)
        self.assertEqual(vi[3], vi.releaselevel)
        self.assertEqual(vi[4], vi.serial)
        self.assertKweli(vi > (1,0,0))
        self.assertIsInstance(sys.float_repr_style, str)
        self.assertIn(sys.float_repr_style, ('short', 'legacy'))
        ikiwa sio sys.platform.startswith('win'):
            self.assertIsInstance(sys.abiflags, str)

    eleza test_thread_info(self):
        info = sys.thread_info
        self.assertEqual(len(info), 3)
        self.assertIn(info.name, ('nt', 'pthread', 'solaris', Tupu))
        self.assertIn(info.lock, ('semaphore', 'mutex+cond', Tupu))

    eleza test_43581(self):
        # Can't use sys.stdout, kama this ni a StringIO object when
        # the test runs under regrtest.
        self.assertEqual(sys.__stdout__.encoding, sys.__stderr__.encoding)

    eleza test_intern(self):
        global INTERN_NUMRUNS
        INTERN_NUMRUNS += 1
        self.assertRaises(TypeError, sys.intern)
        s = "never interned before" + str(INTERN_NUMRUNS)
        self.assertKweli(sys.intern(s) ni s)
        s2 = s.swapcase().swapcase()
        self.assertKweli(sys.intern(s2) ni s)

        # Subclasses of string can't be interned, because they
        # provide too much opportunity kila insane things to happen.
        # We don't want them kwenye the interned dict na ikiwa they aren't
        # actually interned, we don't want to create the appearance
        # that they are by allowing intern() to succeed.
        kundi S(str):
            eleza __hash__(self):
                rudisha 123

        self.assertRaises(TypeError, sys.intern, S("abc"))

    eleza test_sys_flags(self):
        self.assertKweli(sys.flags)
        attrs = ("debug",
                 "inspect", "interactive", "optimize", "dont_write_bytecode",
                 "no_user_site", "no_site", "ignore_environment", "verbose",
                 "bytes_warning", "quiet", "hash_randomization", "isolated",
                 "dev_mode", "utf8_mode")
        kila attr kwenye attrs:
            self.assertKweli(hasattr(sys.flags, attr), attr)
            attr_type = bool ikiwa attr == "dev_mode" isipokua int
            self.assertEqual(type(getattr(sys.flags, attr)), attr_type, attr)
        self.assertKweli(repr(sys.flags))
        self.assertEqual(len(sys.flags), len(attrs))

        self.assertIn(sys.flags.utf8_mode, {0, 1, 2})

    eleza assert_raise_on_new_sys_type(self, sys_attr):
        # Users are intentionally prevented kutoka creating new instances of
        # sys.flags, sys.version_info, na sys.getwindowsversion.
        attr_type = type(sys_attr)
        ukijumuisha self.assertRaises(TypeError):
            attr_type()
        ukijumuisha self.assertRaises(TypeError):
            attr_type.__new__(attr_type)

    eleza test_sys_flags_no_instantiation(self):
        self.assert_raise_on_new_sys_type(sys.flags)

    eleza test_sys_version_info_no_instantiation(self):
        self.assert_raise_on_new_sys_type(sys.version_info)

    eleza test_sys_getwindowsversion_no_instantiation(self):
        # Skip ikiwa sio being run on Windows.
        test.support.get_attribute(sys, "getwindowsversion")
        self.assert_raise_on_new_sys_type(sys.getwindowsversion())

    @test.support.cpython_only
    eleza test_clear_type_cache(self):
        sys._clear_type_cache()

    eleza test_ioencoding(self):
        env = dict(os.environ)

        # Test character: cent sign, encoded kama 0x4A (ASCII J) kwenye CP424,
        # sio representable kwenye ASCII.

        env["PYTHONIOENCODING"] = "cp424"
        p = subprocess.Popen([sys.executable, "-c", 'andika(chr(0xa2))'],
                             stdout = subprocess.PIPE, env=env)
        out = p.communicate()[0].strip()
        expected = ("\xa2" + os.linesep).encode("cp424")
        self.assertEqual(out, expected)

        env["PYTHONIOENCODING"] = "ascii:replace"
        p = subprocess.Popen([sys.executable, "-c", 'andika(chr(0xa2))'],
                             stdout = subprocess.PIPE, env=env)
        out = p.communicate()[0].strip()
        self.assertEqual(out, b'?')

        env["PYTHONIOENCODING"] = "ascii"
        p = subprocess.Popen([sys.executable, "-c", 'andika(chr(0xa2))'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=env)
        out, err = p.communicate()
        self.assertEqual(out, b'')
        self.assertIn(b'UnicodeEncodeError:', err)
        self.assertIn(rb"'\xa2'", err)

        env["PYTHONIOENCODING"] = "ascii:"
        p = subprocess.Popen([sys.executable, "-c", 'andika(chr(0xa2))'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=env)
        out, err = p.communicate()
        self.assertEqual(out, b'')
        self.assertIn(b'UnicodeEncodeError:', err)
        self.assertIn(rb"'\xa2'", err)

        env["PYTHONIOENCODING"] = ":surrogateescape"
        p = subprocess.Popen([sys.executable, "-c", 'andika(chr(0xdcbd))'],
                             stdout=subprocess.PIPE, env=env)
        out = p.communicate()[0].strip()
        self.assertEqual(out, b'\xbd')

    @unittest.skipUnless(test.support.FS_NONASCII,
                         'requires OS support of non-ASCII encodings')
    @unittest.skipUnless(sys.getfilesystemencoding() == locale.getpreferredencoding(Uongo),
                         'requires FS encoding to match locale')
    eleza test_ioencoding_nonascii(self):
        env = dict(os.environ)

        env["PYTHONIOENCODING"] = ""
        p = subprocess.Popen([sys.executable, "-c",
                                'andika(%a)' % test.support.FS_NONASCII],
                                stdout=subprocess.PIPE, env=env)
        out = p.communicate()[0].strip()
        self.assertEqual(out, os.fsencode(test.support.FS_NONASCII))

    @unittest.skipIf(sys.base_prefix != sys.prefix,
                     'Test ni sio venv-compatible')
    eleza test_executable(self):
        # sys.executable should be absolute
        self.assertEqual(os.path.abspath(sys.executable), sys.executable)

        # Issue #7774: Ensure that sys.executable ni an empty string ikiwa argv[0]
        # has been set to a non existent program name na Python ni unable to
        # retrieve the real program name

        # For a normal installation, it should work without 'cwd'
        # argument. For test runs kwenye the build directory, see #7774.
        python_dir = os.path.dirname(os.path.realpath(sys.executable))
        p = subprocess.Popen(
            ["nonexistent", "-c",
             'agiza sys; andika(sys.executable.encode("ascii", "backslashreplace"))'],
            executable=sys.executable, stdout=subprocess.PIPE, cwd=python_dir)
        stdout = p.communicate()[0]
        executable = stdout.strip().decode("ASCII")
        p.wait()
        self.assertIn(executable, ["b''", repr(sys.executable.encode("ascii", "backslashreplace"))])

    eleza check_fsencoding(self, fs_encoding, expected=Tupu):
        self.assertIsNotTupu(fs_encoding)
        codecs.lookup(fs_encoding)
        ikiwa expected:
            self.assertEqual(fs_encoding, expected)

    eleza test_getfilesystemencoding(self):
        fs_encoding = sys.getfilesystemencoding()
        ikiwa sys.platform == 'darwin':
            expected = 'utf-8'
        isipokua:
            expected = Tupu
        self.check_fsencoding(fs_encoding, expected)

    eleza c_locale_get_error_handler(self, locale, isolated=Uongo, encoding=Tupu):
        # Force the POSIX locale
        env = os.environ.copy()
        env["LC_ALL"] = locale
        env["PYTHONCOERCECLOCALE"] = "0"
        code = '\n'.join((
            'agiza sys',
            'eleza dump(name):',
            '    std = getattr(sys, name)',
            '    andika("%s: %s" % (name, std.errors))',
            'dump("stdin")',
            'dump("stdout")',
            'dump("stderr")',
        ))
        args = [sys.executable, "-X", "utf8=0", "-c", code]
        ikiwa isolated:
            args.append("-I")
        ikiwa encoding ni sio Tupu:
            env['PYTHONIOENCODING'] = encoding
        isipokua:
            env.pop('PYTHONIOENCODING', Tupu)
        p = subprocess.Popen(args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              env=env,
                              universal_newlines=Kweli)
        stdout, stderr = p.communicate()
        rudisha stdout

    eleza check_locale_surrogateescape(self, locale):
        out = self.c_locale_get_error_handler(locale, isolated=Kweli)
        self.assertEqual(out,
                         'stdin: surrogateescape\n'
                         'stdout: surrogateescape\n'
                         'stderr: backslashreplace\n')

        # replace the default error handler
        out = self.c_locale_get_error_handler(locale, encoding=':ignore')
        self.assertEqual(out,
                         'stdin: ignore\n'
                         'stdout: ignore\n'
                         'stderr: backslashreplace\n')

        # force the encoding
        out = self.c_locale_get_error_handler(locale, encoding='iso8859-1')
        self.assertEqual(out,
                         'stdin: strict\n'
                         'stdout: strict\n'
                         'stderr: backslashreplace\n')
        out = self.c_locale_get_error_handler(locale, encoding='iso8859-1:')
        self.assertEqual(out,
                         'stdin: strict\n'
                         'stdout: strict\n'
                         'stderr: backslashreplace\n')

        # have no any effect
        out = self.c_locale_get_error_handler(locale, encoding=':')
        self.assertEqual(out,
                         'stdin: surrogateescape\n'
                         'stdout: surrogateescape\n'
                         'stderr: backslashreplace\n')
        out = self.c_locale_get_error_handler(locale, encoding='')
        self.assertEqual(out,
                         'stdin: surrogateescape\n'
                         'stdout: surrogateescape\n'
                         'stderr: backslashreplace\n')

    eleza test_c_locale_surrogateescape(self):
        self.check_locale_surrogateescape('C')

    eleza test_posix_locale_surrogateescape(self):
        self.check_locale_surrogateescape('POSIX')

    eleza test_implementation(self):
        # This test applies to all implementations equally.

        levels = {'alpha': 0xA, 'beta': 0xB, 'candidate': 0xC, 'final': 0xF}

        self.assertKweli(hasattr(sys.implementation, 'name'))
        self.assertKweli(hasattr(sys.implementation, 'version'))
        self.assertKweli(hasattr(sys.implementation, 'hexversion'))
        self.assertKweli(hasattr(sys.implementation, 'cache_tag'))

        version = sys.implementation.version
        self.assertEqual(version[:2], (version.major, version.minor))

        hexversion = (version.major << 24 | version.minor << 16 |
                      version.micro << 8 | levels[version.releaselevel] << 4 |
                      version.serial << 0)
        self.assertEqual(sys.implementation.hexversion, hexversion)

        # PEP 421 requires that .name be lower case.
        self.assertEqual(sys.implementation.name,
                         sys.implementation.name.lower())

    @test.support.cpython_only
    eleza test_debugmallocstats(self):
        # Test sys._debugmallocstats()
        kutoka test.support.script_helper agiza assert_python_ok
        args = ['-c', 'agiza sys; sys._debugmallocstats()']
        ret, out, err = assert_python_ok(*args)
        self.assertIn(b"free PyDictObjects", err)

        # The function has no parameter
        self.assertRaises(TypeError, sys._debugmallocstats, Kweli)

    @unittest.skipUnless(hasattr(sys, "getallocatedblocks"),
                         "sys.getallocatedblocks unavailable on this build")
    eleza test_getallocatedblocks(self):
        jaribu:
            agiza _testcapi
        tatizo ImportError:
            with_pymalloc = support.with_pymalloc()
        isipokua:
            jaribu:
                alloc_name = _testcapi.pymem_getallocatorsname()
            tatizo RuntimeError kama exc:
                # "cannot get allocators name" (ex: tracemalloc ni used)
                with_pymalloc = Kweli
            isipokua:
                with_pymalloc = (alloc_name kwenye ('pymalloc', 'pymalloc_debug'))

        # Some sanity checks
        a = sys.getallocatedblocks()
        self.assertIs(type(a), int)
        ikiwa with_pymalloc:
            self.assertGreater(a, 0)
        isipokua:
            # When WITH_PYMALLOC isn't available, we don't know anything
            # about the underlying implementation: the function might
            # rudisha 0 ama something greater.
            self.assertGreaterEqual(a, 0)
        jaribu:
            # While we could imagine a Python session where the number of
            # multiple buffer objects would exceed the sharing of references,
            # it ni unlikely to happen kwenye a normal test run.
            self.assertLess(a, sys.gettotalrefcount())
        tatizo AttributeError:
            # gettotalrefcount() sio available
            pita
        gc.collect()
        b = sys.getallocatedblocks()
        self.assertLessEqual(b, a)
        gc.collect()
        c = sys.getallocatedblocks()
        self.assertIn(c, range(b - 50, b + 50))

    @test.support.requires_type_collecting
    eleza test_is_finalizing(self):
        self.assertIs(sys.is_finalizing(), Uongo)
        # Don't use the atexit module because _Py_Finalizing ni only set
        # after calling atexit callbacks
        code = """ikiwa 1:
            agiza sys

            kundi AtExit:
                is_finalizing = sys.is_finalizing
                andika = andika

                eleza __del__(self):
                    self.andika(self.is_finalizing(), flush=Kweli)

            # Keep a reference kwenye the __main__ module namespace, so the
            # AtExit destructor will be called at Python exit
            ref = AtExit()
        """
        rc, stdout, stderr = assert_python_ok('-c', code)
        self.assertEqual(stdout.rstrip(), b'Kweli')

    @test.support.requires_type_collecting
    eleza test_issue20602(self):
        # sys.flags na sys.float_info were wiped during shutdown.
        code = """ikiwa 1:
            agiza sys
            kundi A:
                eleza __del__(self, sys=sys):
                    andika(sys.flags)
                    andika(sys.float_info)
            a = A()
            """
        rc, out, err = assert_python_ok('-c', code)
        out = out.splitlines()
        self.assertIn(b'sys.flags', out[0])
        self.assertIn(b'sys.float_info', out[1])

    @unittest.skipUnless(hasattr(sys, 'getandroidapilevel'),
                         'need sys.getandroidapilevel()')
    eleza test_getandroidapilevel(self):
        level = sys.getandroidapilevel()
        self.assertIsInstance(level, int)
        self.assertGreater(level, 0)

    eleza test_sys_tracebacklimit(self):
        code = """ikiwa 1:
            agiza sys
            eleza f1():
                1 / 0
            eleza f2():
                f1()
            sys.tracebacklimit = %r
            f2()
        """
        eleza check(tracebacklimit, expected):
            p = subprocess.Popen([sys.executable, '-c', code % tracebacklimit],
                                 stderr=subprocess.PIPE)
            out = p.communicate()[1]
            self.assertEqual(out.splitlines(), expected)

        traceback = [
            b'Traceback (most recent call last):',
            b'  File "<string>", line 8, kwenye <module>',
            b'  File "<string>", line 6, kwenye f2',
            b'  File "<string>", line 4, kwenye f1',
            b'ZeroDivisionError: division by zero'
        ]
        check(10, traceback)
        check(3, traceback)
        check(2, traceback[:1] + traceback[2:])
        check(1, traceback[:1] + traceback[3:])
        check(0, [traceback[-1]])
        check(-1, [traceback[-1]])
        check(1<<1000, traceback)
        check(-1<<1000, [traceback[-1]])
        check(Tupu, traceback)

    eleza test_no_duplicates_in_meta_path(self):
        self.assertEqual(len(sys.meta_path), len(set(sys.meta_path)))

    @unittest.skipUnless(hasattr(sys, "_enablelegacywindowsfsencoding"),
                         'needs sys._enablelegacywindowsfsencoding()')
    eleza test__enablelegacywindowsfsencoding(self):
        code = ('agiza sys',
                'sys._enablelegacywindowsfsencoding()',
                'andika(sys.getfilesystemencoding(), sys.getfilesystemencodeerrors())')
        rc, out, err = assert_python_ok('-c', '; '.join(code))
        out = out.decode('ascii', 'replace').rstrip()
        self.assertEqual(out, 'mbcs replace')


@test.support.cpython_only
kundi UnraisableHookTest(unittest.TestCase):
    eleza write_unraisable_exc(self, exc, err_msg, obj):
        agiza _testcapi
        agiza types
        err_msg2 = f"Exception ignored {err_msg}"
        jaribu:
            _testcapi.write_unraisable_exc(exc, err_msg, obj)
            rudisha types.SimpleNamespace(exc_type=type(exc),
                                         exc_value=exc,
                                         exc_traceback=exc.__traceback__,
                                         err_msg=err_msg2,
                                         object=obj)
        mwishowe:
            # Explicitly koma any reference cycle
            exc = Tupu

    eleza test_original_unraisablehook(self):
        kila err_msg kwenye (Tupu, "original hook"):
            ukijumuisha self.subTest(err_msg=err_msg):
                obj = "an object"

                ukijumuisha test.support.captured_output("stderr") kama stderr:
                    ukijumuisha test.support.swap_attr(sys, 'unraisablehook',
                                                sys.__unraisablehook__):
                        self.write_unraisable_exc(ValueError(42), err_msg, obj)

                err = stderr.getvalue()
                ikiwa err_msg ni sio Tupu:
                    self.assertIn(f'Exception ignored {err_msg}: {obj!r}\n', err)
                isipokua:
                    self.assertIn(f'Exception ignored in: {obj!r}\n', err)
                self.assertIn('Traceback (most recent call last):\n', err)
                self.assertIn('ValueError: 42\n', err)

    eleza test_original_unraisablehook_err(self):
        # bpo-22836: PyErr_WriteUnraisable() should give sensible reports
        kundi BrokenDel:
            eleza __del__(self):
                exc = ValueError("toa ni broken")
                # The following line ni included kwenye the traceback report:
                ashiria exc

        kundi BrokenStrException(Exception):
            eleza __str__(self):
                ashiria Exception("str() ni broken")

        kundi BrokenExceptionDel:
            eleza __del__(self):
                exc = BrokenStrException()
                # The following line ni included kwenye the traceback report:
                ashiria exc

        kila test_class kwenye (BrokenDel, BrokenExceptionDel):
            ukijumuisha self.subTest(test_class):
                obj = test_class()
                ukijumuisha test.support.captured_stderr() kama stderr, \
                     test.support.swap_attr(sys, 'unraisablehook',
                                            sys.__unraisablehook__):
                    # Trigger obj.__del__()
                    toa obj

                report = stderr.getvalue()
                self.assertIn("Exception ignored", report)
                self.assertIn(test_class.__del__.__qualname__, report)
                self.assertIn("test_sys.py", report)
                self.assertIn("ashiria exc", report)
                ikiwa test_class ni BrokenExceptionDel:
                    self.assertIn("BrokenStrException", report)
                    self.assertIn("<exception str() failed>", report)
                isipokua:
                    self.assertIn("ValueError", report)
                    self.assertIn("toa ni broken", report)
                self.assertKweli(report.endswith("\n"))


    eleza test_original_unraisablehook_wrong_type(self):
        exc = ValueError(42)
        ukijumuisha test.support.swap_attr(sys, 'unraisablehook',
                                    sys.__unraisablehook__):
            ukijumuisha self.assertRaises(TypeError):
                sys.unraisablehook(exc)

    eleza test_custom_unraisablehook(self):
        hook_args = Tupu

        eleza hook_func(args):
            nonlocal hook_args
            hook_args = args

        obj = object()
        jaribu:
            ukijumuisha test.support.swap_attr(sys, 'unraisablehook', hook_func):
                expected = self.write_unraisable_exc(ValueError(42),
                                                     "custom hook", obj)
                kila attr kwenye "exc_type exc_value exc_traceback err_msg object".split():
                    self.assertEqual(getattr(hook_args, attr),
                                     getattr(expected, attr),
                                     (hook_args, expected))
        mwishowe:
            # expected na hook_args contain an exception: koma reference cycle
            expected = Tupu
            hook_args = Tupu

    eleza test_custom_unraisablehook_fail(self):
        eleza hook_func(*args):
            ashiria Exception("hook_func failed")

        ukijumuisha test.support.captured_output("stderr") kama stderr:
            ukijumuisha test.support.swap_attr(sys, 'unraisablehook', hook_func):
                self.write_unraisable_exc(ValueError(42),
                                          "custom hook fail", Tupu)

        err = stderr.getvalue()
        self.assertIn(f'Exception ignored kwenye sys.unraisablehook: '
                      f'{hook_func!r}\n',
                      err)
        self.assertIn('Traceback (most recent call last):\n', err)
        self.assertIn('Exception: hook_func failed\n', err)


@test.support.cpython_only
kundi SizeofTest(unittest.TestCase):

    eleza setUp(self):
        self.P = struct.calcsize('P')
        self.longdigit = sys.int_info.sizeof_digit
        agiza _testcapi
        self.gc_headsize = _testcapi.SIZEOF_PYGC_HEAD

    check_sizeof = test.support.check_sizeof

    eleza test_gc_head_size(self):
        # Check that the gc header size ni added to objects tracked by the gc.
        vsize = test.support.calcvobjsize
        gc_header_size = self.gc_headsize
        # bool objects are sio gc tracked
        self.assertEqual(sys.getsizeof(Kweli), vsize('') + self.longdigit)
        # but lists are
        self.assertEqual(sys.getsizeof([]), vsize('Pn') + gc_header_size)

    eleza test_errors(self):
        kundi BadSizeof:
            eleza __sizeof__(self):
                ashiria ValueError
        self.assertRaises(ValueError, sys.getsizeof, BadSizeof())

        kundi InvalidSizeof:
            eleza __sizeof__(self):
                rudisha Tupu
        self.assertRaises(TypeError, sys.getsizeof, InvalidSizeof())
        sentinel = ["sentinel"]
        self.assertIs(sys.getsizeof(InvalidSizeof(), sentinel), sentinel)

        kundi FloatSizeof:
            eleza __sizeof__(self):
                rudisha 4.5
        self.assertRaises(TypeError, sys.getsizeof, FloatSizeof())
        self.assertIs(sys.getsizeof(FloatSizeof(), sentinel), sentinel)

        kundi OverflowSizeof(int):
            eleza __sizeof__(self):
                rudisha int(self)
        self.assertEqual(sys.getsizeof(OverflowSizeof(sys.maxsize)),
                         sys.maxsize + self.gc_headsize)
        ukijumuisha self.assertRaises(OverflowError):
            sys.getsizeof(OverflowSizeof(sys.maxsize + 1))
        ukijumuisha self.assertRaises(ValueError):
            sys.getsizeof(OverflowSizeof(-1))
        ukijumuisha self.assertRaises((ValueError, OverflowError)):
            sys.getsizeof(OverflowSizeof(-sys.maxsize - 1))

    eleza test_default(self):
        size = test.support.calcvobjsize
        self.assertEqual(sys.getsizeof(Kweli), size('') + self.longdigit)
        self.assertEqual(sys.getsizeof(Kweli, -1), size('') + self.longdigit)

    eleza test_objecttypes(self):
        # check all types defined kwenye Objects/
        calcsize = struct.calcsize
        size = test.support.calcobjsize
        vsize = test.support.calcvobjsize
        check = self.check_sizeof
        # bool
        check(Kweli, vsize('') + self.longdigit)
        # buffer
        # XXX
        # builtin_function_or_method
        check(len, size('5P'))
        # bytearray
        samples = [b'', b'u'*100000]
        kila sample kwenye samples:
            x = bytearray(sample)
            check(x, vsize('n2Pi') + x.__alloc__())
        # bytearray_iterator
        check(iter(bytearray()), size('nP'))
        # bytes
        check(b'', vsize('n') + 1)
        check(b'x' * 10, vsize('n') + 11)
        # cell
        eleza get_cell():
            x = 42
            eleza inner():
                rudisha x
            rudisha inner
        check(get_cell().__closure__[0], size('P'))
        # code
        eleza check_code_size(a, expected_size):
            self.assertGreaterEqual(sys.getsizeof(a), expected_size)
        check_code_size(get_cell().__code__, size('6i13P'))
        check_code_size(get_cell.__code__, size('6i13P'))
        eleza get_cell2(x):
            eleza inner():
                rudisha x
            rudisha inner
        check_code_size(get_cell2.__code__, size('6i13P') + calcsize('n'))
        # complex
        check(complex(0,1), size('2d'))
        # method_descriptor (descriptor object)
        check(str.lower, size('3PPP'))
        # classmethod_descriptor (descriptor object)
        # XXX
        # member_descriptor (descriptor object)
        agiza datetime
        check(datetime.timedelta.days, size('3PP'))
        # getset_descriptor (descriptor object)
        agiza collections
        check(collections.defaultdict.default_factory, size('3PP'))
        # wrapper_descriptor (descriptor object)
        check(int.__add__, size('3P2P'))
        # method-wrapper (descriptor object)
        check({}.__iter__, size('2P'))
        # empty dict
        check({}, size('nQ2P'))
        # dict
        check({"a": 1}, size('nQ2P') + calcsize('2nP2n') + 8 + (8*2//3)*calcsize('n2P'))
        longdict = {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8}
        check(longdict, size('nQ2P') + calcsize('2nP2n') + 16 + (16*2//3)*calcsize('n2P'))
        # dictionary-keyview
        check({}.keys(), size('P'))
        # dictionary-valueview
        check({}.values(), size('P'))
        # dictionary-itemview
        check({}.items(), size('P'))
        # dictionary iterator
        check(iter({}), size('P2nPn'))
        # dictionary-keyiterator
        check(iter({}.keys()), size('P2nPn'))
        # dictionary-valueiterator
        check(iter({}.values()), size('P2nPn'))
        # dictionary-itemiterator
        check(iter({}.items()), size('P2nPn'))
        # dictproxy
        kundi C(object): pita
        check(C.__dict__, size('P'))
        # BaseException
        check(BaseException(), size('5Pb'))
        # UnicodeEncodeError
        check(UnicodeEncodeError("", "", 0, 0, ""), size('5Pb 2P2nP'))
        # UnicodeDecodeError
        check(UnicodeDecodeError("", b"", 0, 0, ""), size('5Pb 2P2nP'))
        # UnicodeTranslateError
        check(UnicodeTranslateError("", 0, 1, ""), size('5Pb 2P2nP'))
        # ellipses
        check(Ellipsis, size(''))
        # EncodingMap
        agiza codecs, encodings.iso8859_3
        x = codecs.charmap_build(encodings.iso8859_3.decoding_table)
        check(x, size('32B2iB'))
        # enumerate
        check(enumerate([]), size('n3P'))
        # reverse
        check(reversed(''), size('nP'))
        # float
        check(float(0), size('d'))
        # sys.floatinfo
        check(sys.float_info, vsize('') + self.P * len(sys.float_info))
        # frame
        agiza inspect
        CO_MAXBLOCKS = 20
        x = inspect.currentframe()
        ncells = len(x.f_code.co_cellvars)
        nfrees = len(x.f_code.co_freevars)
        extras = x.f_code.co_stacksize + x.f_code.co_nlocals +\
                  ncells + nfrees - 1
        check(x, vsize('5P2c4P3ic' + CO_MAXBLOCKS*'3i' + 'P' + extras*'P'))
        # function
        eleza func(): pita
        check(func, size('13P'))
        kundi c():
            @staticmethod
            eleza foo():
                pita
            @classmethod
            eleza bar(cls):
                pita
            # staticmethod
            check(foo, size('PP'))
            # classmethod
            check(bar, size('PP'))
        # generator
        eleza get_gen(): tuma 1
        check(get_gen(), size('Pb2PPP4P'))
        # iterator
        check(iter('abc'), size('lP'))
        # callable-iterator
        agiza re
        check(re.finditer('',''), size('2P'))
        # list
        samples = [[], [1,2,3], ['1', '2', '3']]
        kila sample kwenye samples:
            check(sample, vsize('Pn') + len(sample)*self.P)
        # sortwrapper (list)
        # XXX
        # cmpwrapper (list)
        # XXX
        # listiterator (list)
        check(iter([]), size('lP'))
        # listreverseiterator (list)
        check(reversed([]), size('nP'))
        # int
        check(0, vsize(''))
        check(1, vsize('') + self.longdigit)
        check(-1, vsize('') + self.longdigit)
        PyLong_BASE = 2**sys.int_info.bits_per_digit
        check(int(PyLong_BASE), vsize('') + 2*self.longdigit)
        check(int(PyLong_BASE**2-1), vsize('') + 2*self.longdigit)
        check(int(PyLong_BASE**2), vsize('') + 3*self.longdigit)
        # module
        check(unittest, size('PnPPP'))
        # Tupu
        check(Tupu, size(''))
        # NotImplementedType
        check(NotImplemented, size(''))
        # object
        check(object(), size(''))
        # property (descriptor object)
        kundi C(object):
            eleza getx(self): rudisha self.__x
            eleza setx(self, value): self.__x = value
            eleza delx(self): toa self.__x
            x = property(getx, setx, delx, "")
            check(x, size('4Pi'))
        # PyCapsule
        # XXX
        # rangeiterator
        check(iter(range(1)), size('4l'))
        # reverse
        check(reversed(''), size('nP'))
        # range
        check(range(1), size('4P'))
        check(range(66000), size('4P'))
        # set
        # frozenset
        PySet_MINSIZE = 8
        samples = [[], range(10), range(50)]
        s = size('3nP' + PySet_MINSIZE*'nP' + '2nP')
        kila sample kwenye samples:
            minused = len(sample)
            ikiwa minused == 0: tmp = 1
            # the computation of minused ni actually a bit more complicated
            # but this suffices kila the sizeof test
            minused = minused*2
            newsize = PySet_MINSIZE
            wakati newsize <= minused:
                newsize = newsize << 1
            ikiwa newsize <= 8:
                check(set(sample), s)
                check(frozenset(sample), s)
            isipokua:
                check(set(sample), s + newsize*calcsize('nP'))
                check(frozenset(sample), s + newsize*calcsize('nP'))
        # setiterator
        check(iter(set()), size('P3n'))
        # slice
        check(slice(0), size('3P'))
        # super
        check(super(int), size('3P'))
        # tuple
        check((), vsize(''))
        check((1,2,3), vsize('') + 3*self.P)
        # type
        # static type: PyTypeObject
        fmt = 'P2nPI13Pl4Pn9Pn11PIPPP'
        ikiwa hasattr(sys, 'getcounts'):
            fmt += '3n2P'
        s = vsize(fmt)
        check(int, s)
        # class
        s = vsize(fmt +                 # PyTypeObject
                  '3P'                  # PyAsyncMethods
                  '36P'                 # PyNumberMethods
                  '3P'                  # PyMappingMethods
                  '10P'                 # PySequenceMethods
                  '2P'                  # PyBufferProcs
                  '4P')
        kundi newstyleclass(object): pita
        # Separate block kila PyDictKeysObject ukijumuisha 8 keys na 5 entries
        check(newstyleclass, s + calcsize("2nP2n0P") + 8 + 5*calcsize("n2P"))
        # dict ukijumuisha shared keys
        check(newstyleclass().__dict__, size('nQ2P') + 5*self.P)
        o = newstyleclass()
        o.a = o.b = o.c = o.d = o.e = o.f = o.g = o.h = 1
        # Separate block kila PyDictKeysObject ukijumuisha 16 keys na 10 entries
        check(newstyleclass, s + calcsize("2nP2n0P") + 16 + 10*calcsize("n2P"))
        # dict ukijumuisha shared keys
        check(newstyleclass().__dict__, size('nQ2P') + 10*self.P)
        # unicode
        # each tuple contains a string na its expected character size
        # don't put any static strings here, kama they may contain
        # wchar_t ama UTF-8 representations
        samples = ['1'*100, '\xff'*50,
                   '\u0100'*40, '\uffff'*100,
                   '\U00010000'*30, '\U0010ffff'*100]
        asciifields = "nnbP"
        compactfields = asciifields + "nPn"
        unicodefields = compactfields + "P"
        kila s kwenye samples:
            maxchar = ord(max(s))
            ikiwa maxchar < 128:
                L = size(asciifields) + len(s) + 1
            lasivyo maxchar < 256:
                L = size(compactfields) + len(s) + 1
            lasivyo maxchar < 65536:
                L = size(compactfields) + 2*(len(s) + 1)
            isipokua:
                L = size(compactfields) + 4*(len(s) + 1)
            check(s, L)
        # verify that the UTF-8 size ni accounted for
        s = chr(0x4000)   # 4 bytes canonical representation
        check(s, size(compactfields) + 4)
        # compile() will trigger the generation of the UTF-8
        # representation kama a side effect
        compile(s, "<stdin>", "eval")
        check(s, size(compactfields) + 4 + 4)
        # TODO: add check that forces the presence of wchar_t representation
        # TODO: add check that forces layout of unicodefields
        # weakref
        agiza weakref
        check(weakref.ref(int), size('2Pn2P'))
        # weakproxy
        # XXX
        # weakcallableproxy
        check(weakref.proxy(int), size('2Pn2P'))

    eleza check_slots(self, obj, base, extra):
        expected = sys.getsizeof(base) + struct.calcsize(extra)
        ikiwa gc.is_tracked(obj) na sio gc.is_tracked(base):
            expected += self.gc_headsize
        self.assertEqual(sys.getsizeof(obj), expected)

    eleza test_slots(self):
        # check all subclassable types defined kwenye Objects/ that allow
        # non-empty __slots__
        check = self.check_slots
        kundi BA(bytearray):
            __slots__ = 'a', 'b', 'c'
        check(BA(), bytearray(), '3P')
        kundi D(dict):
            __slots__ = 'a', 'b', 'c'
        check(D(x=[]), {'x': []}, '3P')
        kundi L(list):
            __slots__ = 'a', 'b', 'c'
        check(L(), [], '3P')
        kundi S(set):
            __slots__ = 'a', 'b', 'c'
        check(S(), set(), '3P')
        kundi FS(frozenset):
            __slots__ = 'a', 'b', 'c'
        check(FS(), frozenset(), '3P')
        kutoka collections agiza OrderedDict
        kundi OD(OrderedDict):
            __slots__ = 'a', 'b', 'c'
        check(OD(x=[]), OrderedDict(x=[]), '3P')

    eleza test_pythontypes(self):
        # check all types defined kwenye Python/
        size = test.support.calcobjsize
        vsize = test.support.calcvobjsize
        check = self.check_sizeof
        # _ast.AST
        agiza _ast
        check(_ast.AST(), size('P'))
        jaribu:
            ashiria TypeError
        tatizo TypeError:
            tb = sys.exc_info()[2]
            # traceback
            ikiwa tb ni sio Tupu:
                check(tb, size('2P2i'))
        # symtable entry
        # XXX
        # sys.flags
        check(sys.flags, vsize('') + self.P * len(sys.flags))

    eleza test_asyncgen_hooks(self):
        old = sys.get_asyncgen_hooks()
        self.assertIsTupu(old.firstiter)
        self.assertIsTupu(old.finalizer)

        firstiter = lambda *a: Tupu
        sys.set_asyncgen_hooks(firstiter=firstiter)
        hooks = sys.get_asyncgen_hooks()
        self.assertIs(hooks.firstiter, firstiter)
        self.assertIs(hooks[0], firstiter)
        self.assertIs(hooks.finalizer, Tupu)
        self.assertIs(hooks[1], Tupu)

        finalizer = lambda *a: Tupu
        sys.set_asyncgen_hooks(finalizer=finalizer)
        hooks = sys.get_asyncgen_hooks()
        self.assertIs(hooks.firstiter, firstiter)
        self.assertIs(hooks[0], firstiter)
        self.assertIs(hooks.finalizer, finalizer)
        self.assertIs(hooks[1], finalizer)

        sys.set_asyncgen_hooks(*old)
        cur = sys.get_asyncgen_hooks()
        self.assertIsTupu(cur.firstiter)
        self.assertIsTupu(cur.finalizer)


ikiwa __name__ == "__main__":
    unittest.main()
