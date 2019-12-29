# Verify that gdb can pretty-print the various PyObject* types
#
# The code kila testing gdb was adapted kutoka similar work kwenye Unladen Swallow's
# Lib/test/test_jit_gdb.py

agiza os
agiza platform
agiza re
agiza subprocess
agiza sys
agiza sysconfig
agiza textwrap
agiza unittest

kutoka test agiza support
kutoka test.support agiza run_unittest, findfile, python_is_optimized

eleza get_gdb_version():
    jaribu:
        proc = subprocess.Popen(["gdb", "-nx", "--version"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=Kweli)
        ukijumuisha proc:
            version = proc.communicate()[0]
    tatizo OSError:
        # This ni what "no gdb" looks like.  There may, however, be other
        # errors that manifest this way too.
        ashiria unittest.SkipTest("Couldn't find gdb on the path")

    # Regex to parse:
    # 'GNU gdb (GDB; SUSE Linux Enterprise 12) 7.7\n' -> 7.7
    # 'GNU gdb (GDB) Fedora 7.9.1-17.fc22\n' -> 7.9
    # 'GNU gdb 6.1.1 [FreeBSD]\n' -> 6.1
    # 'GNU gdb (GDB) Fedora (7.5.1-37.fc18)\n' -> 7.5
    match = re.search(r"^GNU gdb.*?\b(\d+)\.(\d+)", version)
    ikiwa match ni Tupu:
        ashiria Exception("unable to parse GDB version: %r" % version)
    rudisha (version, int(match.group(1)), int(match.group(2)))

gdb_version, gdb_major_version, gdb_minor_version = get_gdb_version()
ikiwa gdb_major_version < 7:
    ashiria unittest.SkipTest("gdb versions before 7.0 didn't support python "
                            "embedding. Saw %s.%s:\n%s"
                            % (gdb_major_version, gdb_minor_version,
                               gdb_version))

ikiwa sio sysconfig.is_python_build():
    ashiria unittest.SkipTest("test_gdb only works on source builds at the moment.")

ikiwa 'Clang' kwenye platform.python_compiler() na sys.platform == 'darwin':
    ashiria unittest.SkipTest("test_gdb doesn't work correctly when python is"
                            " built ukijumuisha LLVM clang")

ikiwa ((sysconfig.get_config_var('PGO_PROF_USE_FLAG') ama 'xxx') in
    (sysconfig.get_config_var('PY_CORE_CFLAGS') ama '')):
    ashiria unittest.SkipTest("test_gdb ni sio reliable on PGO builds")

# Location of custom hooks file kwenye a repository checkout.
checkout_hook_path = os.path.join(os.path.dirname(sys.executable),
                                  'python-gdb.py')

PYTHONHASHSEED = '123'


eleza cet_protection():
    cflags = sysconfig.get_config_var('CFLAGS')
    ikiwa sio cflags:
        rudisha Uongo
    flags = cflags.split()
    # Kweli ikiwa "-mcet -fcf-protection" options are found, but false
    # ikiwa "-fcf-protection=none" ama "-fcf-protection=rudisha" ni found.
    rudisha (('-mcet' kwenye flags)
            na any((flag.startswith('-fcf-protection')
                     na sio flag.endswith(("=none", "=rudisha")))
                    kila flag kwenye flags))

# Control-flow enforcement technology
CET_PROTECTION = cet_protection()


eleza run_gdb(*args, **env_vars):
    """Runs gdb kwenye --batch mode ukijumuisha the additional arguments given by *args.

    Returns its (stdout, stderr) decoded kutoka utf-8 using the replace handler.
    """
    ikiwa env_vars:
        env = os.environ.copy()
        env.update(env_vars)
    isipokua:
        env = Tupu
    # -nx: Do sio execute commands kutoka any .gdbinit initialization files
    #      (issue #22188)
    base_cmd = ('gdb', '--batch', '-nx')
    ikiwa (gdb_major_version, gdb_minor_version) >= (7, 4):
        base_cmd += ('-iex', 'add-auto-load-safe-path ' + checkout_hook_path)
    proc = subprocess.Popen(base_cmd + args,
                            # Redirect stdin to prevent GDB kutoka messing with
                            # the terminal settings
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            env=env)
    ukijumuisha proc:
        out, err = proc.communicate()
    rudisha out.decode('utf-8', 'replace'), err.decode('utf-8', 'replace')

# Verify that "gdb" was built ukijumuisha the embedded python support enabled:
gdbpy_version, _ = run_gdb("--eval-command=python agiza sys; andika(sys.version_info)")
ikiwa sio gdbpy_version:
    ashiria unittest.SkipTest("gdb sio built ukijumuisha embedded python support")

# Verify that "gdb" can load our custom hooks, kama OS security settings may
# disallow this without a customized .gdbinit.
_, gdbpy_errors = run_gdb('--args', sys.executable)
ikiwa "auto-loading has been declined" kwenye gdbpy_errors:
    msg = "gdb security settings prevent use of custom hooks: "
    ashiria unittest.SkipTest(msg + gdbpy_errors.rstrip())

eleza gdb_has_frame_select():
    # Does this build of gdb have gdb.Frame.select ?
    stdout, _ = run_gdb("--eval-command=python andika(dir(gdb.Frame))")
    m = re.match(r'.*\[(.*)\].*', stdout)
    ikiwa sio m:
        ashiria unittest.SkipTest("Unable to parse output kutoka gdb.Frame.select test")
    gdb_frame_dir = m.group(1).split(', ')
    rudisha "'select'" kwenye gdb_frame_dir

HAS_PYUP_PYDOWN = gdb_has_frame_select()

BREAKPOINT_FN='builtin_id'

@unittest.skipIf(support.PGO, "not useful kila PGO")
kundi DebuggerTests(unittest.TestCase):

    """Test that the debugger can debug Python."""

    eleza get_stack_trace(self, source=Tupu, script=Tupu,
                        komapoint=BREAKPOINT_FN,
                        cmds_after_komapoint=Tupu,
                        import_site=Uongo):
        '''
        Run 'python -c SOURCE' under gdb ukijumuisha a komapoint.

        Support injecting commands after the komapoint ni reached

        Returns the stdout kutoka gdb

        cmds_after_komapoint: ikiwa provided, a list of strings: gdb commands
        '''
        # We use "set komapoint pending yes" to avoid blocking ukijumuisha a:
        #   Function "foo" sio defined.
        #   Make komapoint pending on future shared library load? (y ama [n])
        # error, which typically happens python ni dynamically linked (the
        # komapoints of interest are to be found kwenye the shared library)
        # When this happens, we still get:
        #   Function "textiowrapper_write" sio defined.
        # emitted to stderr each time, alas.

        # Initially I had "--eval-command=endelea" here, but removed it to
        # avoid repeated print komapoints when traversing hierarchical data
        # structures

        # Generate a list of commands kwenye gdb's language:
        commands = ['set komapoint pending yes',
                    'koma %s' % komapoint,

                    # The tests assume that the first frame of printed
                    #  backtrace will sio contain program counter,
                    #  that ni however sio guaranteed by gdb
                    #  therefore we need to use 'set print address off' to
                    #  make sure the counter ni sio there. For example:
                    # #0 kwenye PyObject_Print ...
                    #  ni assumed, but sometimes this can be e.g.
                    # #0 0x00003fffb7dd1798 kwenye PyObject_Print ...
                    'set print address off',

                    'run']

        # GDB kama of 7.4 onwards can distinguish between the
        # value of a variable at entry vs current value:
        #   http://sourceware.org/gdb/onlinedocs/gdb/Variables.html
        # which leads to the selftests failing ukijumuisha errors like this:
        #   AssertionError: 'v@entry=()' != '()'
        # Disable this:
        ikiwa (gdb_major_version, gdb_minor_version) >= (7, 4):
            commands += ['set print entry-values no']

        ikiwa cmds_after_komapoint:
            ikiwa CET_PROTECTION:
                # bpo-32962: When Python ni compiled ukijumuisha -mcet
                # -fcf-protection, function arguments are unusable before
                # running the first instruction of the function entry point.
                # The 'next' command makes the required first step.
                commands += ['next']
            commands += cmds_after_komapoint
        isipokua:
            commands += ['backtrace']

        # print commands

        # Use "commands" to generate the arguments ukijumuisha which to invoke "gdb":
        args = ['--eval-command=%s' % cmd kila cmd kwenye commands]
        args += ["--args",
                 sys.executable]
        args.extend(subprocess._args_kutoka_interpreter_flags())

        ikiwa sio import_site:
            # -S suppresses the default 'agiza site'
            args += ["-S"]

        ikiwa source:
            args += ["-c", source]
        lasivyo script:
            args += [script]

        # Use "args" to invoke gdb, capturing stdout, stderr:
        out, err = run_gdb(*args, PYTHONHASHSEED=PYTHONHASHSEED)

        kila line kwenye err.splitlines():
            andika(line, file=sys.stderr)

        # bpo-34007: Sometimes some versions of the shared libraries that
        # are part of the traceback are compiled kwenye optimised mode na the
        # Program Counter (PC) ni sio present, sio allowing gdb to walk the
        # frames back. When this happens, the Python bindings of gdb ashiria
        # an exception, making the test impossible to succeed.
        ikiwa "PC sio saved" kwenye err:
            ashiria unittest.SkipTest("gdb cannot walk the frame object"
                                    " because the Program Counter is"
                                    " sio present")

        rudisha out

    eleza get_gdb_repr(self, source,
                     cmds_after_komapoint=Tupu,
                     import_site=Uongo):
        # Given an input python source representation of data,
        # run "python -c'id(DATA)'" under gdb ukijumuisha a komapoint on
        # builtin_id na scrape out gdb's representation of the "op"
        # parameter, na verify that the gdb displays the same string
        #
        # Verify that the gdb displays the expected string
        #
        # For a nested structure, the first time we hit the komapoint will
        # give us the top-level structure

        # NOTE: avoid decoding too much of the traceback kama some
        # undecodable characters may lurk there kwenye optimized mode
        # (issue #19743).
        cmds_after_komapoint = cmds_after_komapoint ama ["backtrace 1"]
        gdb_output = self.get_stack_trace(source, komapoint=BREAKPOINT_FN,
                                          cmds_after_komapoint=cmds_after_komapoint,
                                          import_site=import_site)
        # gdb can insert additional '\n' na space characters kwenye various places
        # kwenye its output, depending on the width of the terminal it's connected
        # to (using its "wrap_here" function)
        m = re.search(
            # Match '#0 builtin_id(self=..., v=...)'
            r'#0\s+builtin_id\s+\(self\=.*,\s+v=\s*(.*?)?\)'
            # Match ' at Python/bltinmodule.c'.
            # bpo-38239: builtin_id() ni defined kwenye Python/bltinmodule.c,
            # but accept any "Directory\file.c" to support Link Time
            # Optimization (LTO).
            r'\s+at\s+\S*[A-Za-z]+/[A-Za-z0-9_-]+\.c',
            gdb_output, re.DOTALL)
        ikiwa sio m:
            self.fail('Unexpected gdb output: %r\n%s' % (gdb_output, gdb_output))
        rudisha m.group(1), gdb_output

    eleza assertEndsWith(self, actual, exp_end):
        '''Ensure that the given "actual" string ends ukijumuisha "exp_end"'''
        self.assertKweli(actual.endswith(exp_end),
                        msg='%r did sio end ukijumuisha %r' % (actual, exp_end))

    eleza assertMultilineMatches(self, actual, pattern):
        m = re.match(pattern, actual, re.DOTALL)
        ikiwa sio m:
            self.fail(msg='%r did sio match %r' % (actual, pattern))

    eleza get_sample_script(self):
        rudisha findfile('gdb_sample.py')

kundi PrettyPrintTests(DebuggerTests):
    eleza test_getting_backtrace(self):
        gdb_output = self.get_stack_trace('id(42)')
        self.assertKweli(BREAKPOINT_FN kwenye gdb_output)

    eleza assertGdbRepr(self, val, exp_repr=Tupu):
        # Ensure that gdb's rendering of the value kwenye a debugged process
        # matches repr(value) kwenye this process:
        gdb_repr, gdb_output = self.get_gdb_repr('id(' + ascii(val) + ')')
        ikiwa sio exp_repr:
            exp_repr = repr(val)
        self.assertEqual(gdb_repr, exp_repr,
                         ('%r did sio equal expected %r; full output was:\n%s'
                          % (gdb_repr, exp_repr, gdb_output)))

    eleza test_int(self):
        'Verify the pretty-printing of various int values'
        self.assertGdbRepr(42)
        self.assertGdbRepr(0)
        self.assertGdbRepr(-7)
        self.assertGdbRepr(1000000000000)
        self.assertGdbRepr(-1000000000000000)

    eleza test_singletons(self):
        'Verify the pretty-printing of Kweli, Uongo na Tupu'
        self.assertGdbRepr(Kweli)
        self.assertGdbRepr(Uongo)
        self.assertGdbRepr(Tupu)

    eleza test_dicts(self):
        'Verify the pretty-printing of dictionaries'
        self.assertGdbRepr({})
        self.assertGdbRepr({'foo': 'bar'}, "{'foo': 'bar'}")
        # Python preserves insertion order since 3.6
        self.assertGdbRepr({'foo': 'bar', 'douglas': 42}, "{'foo': 'bar', 'douglas': 42}")

    eleza test_lists(self):
        'Verify the pretty-printing of lists'
        self.assertGdbRepr([])
        self.assertGdbRepr(list(range(5)))

    eleza test_bytes(self):
        'Verify the pretty-printing of bytes'
        self.assertGdbRepr(b'')
        self.assertGdbRepr(b'And now kila something hopefully the same')
        self.assertGdbRepr(b'string ukijumuisha embedded NUL here \0 na then some more text')
        self.assertGdbRepr(b'this ni a tab:\t'
                           b' this ni a slash-N:\n'
                           b' this ni a slash-R:\r'
                           )

        self.assertGdbRepr(b'this ni byte 255:\xff na byte 128:\x80')

        self.assertGdbRepr(bytes([b kila b kwenye range(255)]))

    eleza test_strings(self):
        'Verify the pretty-printing of unicode strings'
        # We cannot simply call locale.getpreferredencoding() here,
        # kama GDB might have been linked against a different version
        # of Python ukijumuisha a different encoding na coercion policy
        # ukijumuisha respect to PEP 538 na PEP 540.
        out, err = run_gdb(
            '--eval-command',
            'python agiza locale; andika(locale.getpreferredencoding())')

        encoding = out.rstrip()
        ikiwa err ama sio encoding:
            ashiria RuntimeError(
                f'unable to determine the preferred encoding '
                f'of embedded Python kwenye GDB: {err}')

        eleza check_repr(text):
            jaribu:
                text.encode(encoding)
                printable = Kweli
            tatizo UnicodeEncodeError:
                self.assertGdbRepr(text, ascii(text))
            isipokua:
                self.assertGdbRepr(text)

        self.assertGdbRepr('')
        self.assertGdbRepr('And now kila something hopefully the same')
        self.assertGdbRepr('string ukijumuisha embedded NUL here \0 na then some more text')

        # Test printing a single character:
        #    U+2620 SKULL AND CROSSBONES
        check_repr('\u2620')

        # Test printing a Japanese unicode string
        # (I believe this reads "mojibake", using 3 characters kutoka the CJK
        # Unified Ideographs area, followed by U+3051 HIRAGANA LETTER KE)
        check_repr('\u6587\u5b57\u5316\u3051')

        # Test a character outside the BMP:
        #    U+1D121 MUSICAL SYMBOL C CLEF
        # This is:
        # UTF-8: 0xF0 0x9D 0x84 0xA1
        # UTF-16: 0xD834 0xDD21
        check_repr(chr(0x1D121))

    eleza test_tuples(self):
        'Verify the pretty-printing of tuples'
        self.assertGdbRepr(tuple(), '()')
        self.assertGdbRepr((1,), '(1,)')
        self.assertGdbRepr(('foo', 'bar', 'baz'))

    eleza test_sets(self):
        'Verify the pretty-printing of sets'
        ikiwa (gdb_major_version, gdb_minor_version) < (7, 3):
            self.skipTest("pretty-printing of sets needs gdb 7.3 ama later")
        self.assertGdbRepr(set(), "set()")
        self.assertGdbRepr(set(['a']), "{'a'}")
        # PYTHONHASHSEED ni need to get the exact frozenset item order
        ikiwa sio sys.flags.ignore_environment:
            self.assertGdbRepr(set(['a', 'b']), "{'a', 'b'}")
            self.assertGdbRepr(set([4, 5, 6]), "{4, 5, 6}")

        # Ensure that we handle sets containing the "dummy" key value,
        # which happens on deletion:
        gdb_repr, gdb_output = self.get_gdb_repr('''s = set(['a','b'])
s.remove('a')
id(s)''')
        self.assertEqual(gdb_repr, "{'b'}")

    eleza test_frozensets(self):
        'Verify the pretty-printing of frozensets'
        ikiwa (gdb_major_version, gdb_minor_version) < (7, 3):
            self.skipTest("pretty-printing of frozensets needs gdb 7.3 ama later")
        self.assertGdbRepr(frozenset(), "frozenset()")
        self.assertGdbRepr(frozenset(['a']), "frozenset({'a'})")
        # PYTHONHASHSEED ni need to get the exact frozenset item order
        ikiwa sio sys.flags.ignore_environment:
            self.assertGdbRepr(frozenset(['a', 'b']), "frozenset({'a', 'b'})")
            self.assertGdbRepr(frozenset([4, 5, 6]), "frozenset({4, 5, 6})")

    eleza test_exceptions(self):
        # Test a RuntimeError
        gdb_repr, gdb_output = self.get_gdb_repr('''
jaribu:
    ashiria RuntimeError("I am an error")
tatizo RuntimeError kama e:
    id(e)
''')
        self.assertEqual(gdb_repr,
                         "RuntimeError('I am an error',)")


        # Test division by zero:
        gdb_repr, gdb_output = self.get_gdb_repr('''
jaribu:
    a = 1 / 0
tatizo ZeroDivisionError kama e:
    id(e)
''')
        self.assertEqual(gdb_repr,
                         "ZeroDivisionError('division by zero',)")

    eleza test_modern_class(self):
        'Verify the pretty-printing of new-style kundi instances'
        gdb_repr, gdb_output = self.get_gdb_repr('''
kundi Foo:
    pita
foo = Foo()
foo.an_int = 42
id(foo)''')
        m = re.match(r'<Foo\(an_int=42\) at remote 0x-?[0-9a-f]+>', gdb_repr)
        self.assertKweli(m,
                        msg='Unexpected new-style kundi rendering %r' % gdb_repr)

    eleza test_subclassing_list(self):
        'Verify the pretty-printing of an instance of a list subclass'
        gdb_repr, gdb_output = self.get_gdb_repr('''
kundi Foo(list):
    pita
foo = Foo()
foo += [1, 2, 3]
foo.an_int = 42
id(foo)''')
        m = re.match(r'<Foo\(an_int=42\) at remote 0x-?[0-9a-f]+>', gdb_repr)

        self.assertKweli(m,
                        msg='Unexpected new-style kundi rendering %r' % gdb_repr)

    eleza test_subclassing_tuple(self):
        'Verify the pretty-printing of an instance of a tuple subclass'
        # This should exercise the negative tp_dictoffset code kwenye the
        # new-style kundi support
        gdb_repr, gdb_output = self.get_gdb_repr('''
kundi Foo(tuple):
    pita
foo = Foo((1, 2, 3))
foo.an_int = 42
id(foo)''')
        m = re.match(r'<Foo\(an_int=42\) at remote 0x-?[0-9a-f]+>', gdb_repr)

        self.assertKweli(m,
                        msg='Unexpected new-style kundi rendering %r' % gdb_repr)

    eleza assertSane(self, source, corruption, exprepr=Tupu):
        '''Run Python under gdb, corrupting variables kwenye the inferior process
        immediately before taking a backtrace.

        Verify that the variable's representation ni the expected failsafe
        representation'''
        ikiwa corruption:
            cmds_after_komapoint=[corruption, 'backtrace']
        isipokua:
            cmds_after_komapoint=['backtrace']

        gdb_repr, gdb_output = \
            self.get_gdb_repr(source,
                              cmds_after_komapoint=cmds_after_komapoint)
        ikiwa exprepr:
            ikiwa gdb_repr == exprepr:
                # gdb managed to print the value kwenye spite of the corruption;
                # this ni good (see http://bugs.python.org/issue8330)
                rudisha

        # Match anything kila the type name; 0xDEADBEEF could point to
        # something arbitrary (see  http://bugs.python.org/issue8330)
        pattern = '<.* at remote 0x-?[0-9a-f]+>'

        m = re.match(pattern, gdb_repr)
        ikiwa sio m:
            self.fail('Unexpected gdb representation: %r\n%s' % \
                          (gdb_repr, gdb_output))

    eleza test_NULL_ptr(self):
        'Ensure that a NULL PyObject* ni handled gracefully'
        gdb_repr, gdb_output = (
            self.get_gdb_repr('id(42)',
                              cmds_after_komapoint=['set variable v=0',
                                                     'backtrace'])
            )

        self.assertEqual(gdb_repr, '0x0')

    eleza test_NULL_ob_type(self):
        'Ensure that a PyObject* ukijumuisha NULL ob_type ni handled gracefully'
        self.assertSane('id(42)',
                        'set v->ob_type=0')

    eleza test_corrupt_ob_type(self):
        'Ensure that a PyObject* ukijumuisha a corrupt ob_type ni handled gracefully'
        self.assertSane('id(42)',
                        'set v->ob_type=0xDEADBEEF',
                        exprepr='42')

    eleza test_corrupt_tp_flags(self):
        'Ensure that a PyObject* ukijumuisha a type ukijumuisha corrupt tp_flags ni handled'
        self.assertSane('id(42)',
                        'set v->ob_type->tp_flags=0x0',
                        exprepr='42')

    eleza test_corrupt_tp_name(self):
        'Ensure that a PyObject* ukijumuisha a type ukijumuisha corrupt tp_name ni handled'
        self.assertSane('id(42)',
                        'set v->ob_type->tp_name=0xDEADBEEF',
                        exprepr='42')

    eleza test_builtins_help(self):
        'Ensure that the new-style kundi _Helper kwenye site.py can be handled'

        ikiwa sys.flags.no_site:
            self.skipTest("need site module, but -S option was used")

        # (this was the issue causing tracebacks in
        #  http://bugs.python.org/issue8032#msg100537 )
        gdb_repr, gdb_output = self.get_gdb_repr('id(__builtins__.help)', import_site=Kweli)

        m = re.match(r'<_Helper at remote 0x-?[0-9a-f]+>', gdb_repr)
        self.assertKweli(m,
                        msg='Unexpected rendering %r' % gdb_repr)

    eleza test_selfreferential_list(self):
        '''Ensure that a reference loop involving a list doesn't lead proxyval
        into an infinite loop:'''
        gdb_repr, gdb_output = \
            self.get_gdb_repr("a = [3, 4, 5] ; a.append(a) ; id(a)")
        self.assertEqual(gdb_repr, '[3, 4, 5, [...]]')

        gdb_repr, gdb_output = \
            self.get_gdb_repr("a = [3, 4, 5] ; b = [a] ; a.append(b) ; id(a)")
        self.assertEqual(gdb_repr, '[3, 4, 5, [[...]]]')

    eleza test_selfreferential_dict(self):
        '''Ensure that a reference loop involving a dict doesn't lead proxyval
        into an infinite loop:'''
        gdb_repr, gdb_output = \
            self.get_gdb_repr("a = {} ; b = {'bar':a} ; a['foo'] = b ; id(a)")

        self.assertEqual(gdb_repr, "{'foo': {'bar': {...}}}")

    eleza test_selfreferential_old_style_instance(self):
        gdb_repr, gdb_output = \
            self.get_gdb_repr('''
kundi Foo:
    pita
foo = Foo()
foo.an_attr = foo
id(foo)''')
        self.assertKweli(re.match(r'<Foo\(an_attr=<\.\.\.>\) at remote 0x-?[0-9a-f]+>',
                                 gdb_repr),
                        'Unexpected gdb representation: %r\n%s' % \
                            (gdb_repr, gdb_output))

    eleza test_selfreferential_new_style_instance(self):
        gdb_repr, gdb_output = \
            self.get_gdb_repr('''
kundi Foo(object):
    pita
foo = Foo()
foo.an_attr = foo
id(foo)''')
        self.assertKweli(re.match(r'<Foo\(an_attr=<\.\.\.>\) at remote 0x-?[0-9a-f]+>',
                                 gdb_repr),
                        'Unexpected gdb representation: %r\n%s' % \
                            (gdb_repr, gdb_output))

        gdb_repr, gdb_output = \
            self.get_gdb_repr('''
kundi Foo(object):
    pita
a = Foo()
b = Foo()
a.an_attr = b
b.an_attr = a
id(a)''')
        self.assertKweli(re.match(r'<Foo\(an_attr=<Foo\(an_attr=<\.\.\.>\) at remote 0x-?[0-9a-f]+>\) at remote 0x-?[0-9a-f]+>',
                                 gdb_repr),
                        'Unexpected gdb representation: %r\n%s' % \
                            (gdb_repr, gdb_output))

    eleza test_truncation(self):
        'Verify that very long output ni truncated'
        gdb_repr, gdb_output = self.get_gdb_repr('id(list(range(1000)))')
        self.assertEqual(gdb_repr,
                         "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, "
                         "14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, "
                         "27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, "
                         "40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, "
                         "53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, "
                         "66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, "
                         "79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, "
                         "92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, "
                         "104, 105, 106, 107, 108, 109, 110, 111, 112, 113, "
                         "114, 115, 116, 117, 118, 119, 120, 121, 122, 123, "
                         "124, 125, 126, 127, 128, 129, 130, 131, 132, 133, "
                         "134, 135, 136, 137, 138, 139, 140, 141, 142, 143, "
                         "144, 145, 146, 147, 148, 149, 150, 151, 152, 153, "
                         "154, 155, 156, 157, 158, 159, 160, 161, 162, 163, "
                         "164, 165, 166, 167, 168, 169, 170, 171, 172, 173, "
                         "174, 175, 176, 177, 178, 179, 180, 181, 182, 183, "
                         "184, 185, 186, 187, 188, 189, 190, 191, 192, 193, "
                         "194, 195, 196, 197, 198, 199, 200, 201, 202, 203, "
                         "204, 205, 206, 207, 208, 209, 210, 211, 212, 213, "
                         "214, 215, 216, 217, 218, 219, 220, 221, 222, 223, "
                         "224, 225, 226...(truncated)")
        self.assertEqual(len(gdb_repr),
                         1024 + len('...(truncated)'))

    eleza test_builtin_method(self):
        gdb_repr, gdb_output = self.get_gdb_repr('agiza sys; id(sys.stdout.readlines)')
        self.assertKweli(re.match(r'<built-in method readlines of _io.TextIOWrapper object at remote 0x-?[0-9a-f]+>',
                                 gdb_repr),
                        'Unexpected gdb representation: %r\n%s' % \
                            (gdb_repr, gdb_output))

    eleza test_frames(self):
        gdb_output = self.get_stack_trace('''
eleza foo(a, b, c):
    pita

foo(3, 4, 5)
id(foo.__code__)''',
                                          komapoint='builtin_id',
                                          cmds_after_komapoint=['print (PyFrameObject*)(((PyCodeObject*)v)->co_zombieframe)']
                                          )
        self.assertKweli(re.match(r'.*\s+\$1 =\s+Frame 0x-?[0-9a-f]+, kila file <string>, line 3, kwenye foo \(\)\s+.*',
                                 gdb_output,
                                 re.DOTALL),
                        'Unexpected gdb representation: %r\n%s' % (gdb_output, gdb_output))

@unittest.skipIf(python_is_optimized(),
                 "Python was compiled ukijumuisha optimizations")
kundi PyListTests(DebuggerTests):
    eleza assertListing(self, expected, actual):
        self.assertEndsWith(actual, expected)

    eleza test_basic_command(self):
        'Verify that the "py-list" command works'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_komapoint=['py-list'])

        self.assertListing('   5    \n'
                           '   6    eleza bar(a, b, c):\n'
                           '   7        baz(a, b, c)\n'
                           '   8    \n'
                           '   9    eleza baz(*args):\n'
                           ' >10        id(42)\n'
                           '  11    \n'
                           '  12    foo(1, 2, 3)\n',
                           bt)

    eleza test_one_abs_arg(self):
        'Verify the "py-list" command ukijumuisha one absolute argument'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_komapoint=['py-list 9'])

        self.assertListing('   9    eleza baz(*args):\n'
                           ' >10        id(42)\n'
                           '  11    \n'
                           '  12    foo(1, 2, 3)\n',
                           bt)

    eleza test_two_abs_args(self):
        'Verify the "py-list" command ukijumuisha two absolute arguments'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_komapoint=['py-list 1,3'])

        self.assertListing('   1    # Sample script kila use by test_gdb.py\n'
                           '   2    \n'
                           '   3    eleza foo(a, b, c):\n',
                           bt)

kundi StackNavigationTests(DebuggerTests):
    @unittest.skipUnless(HAS_PYUP_PYDOWN, "test requires py-up/py-down commands")
    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled ukijumuisha optimizations")
    eleza test_pyup_command(self):
        'Verify that the "py-up" command works'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_komapoint=['py-up', 'py-up'])
        self.assertMultilineMatches(bt,
                                    r'''^.*
#[0-9]+ Frame 0x-?[0-9a-f]+, kila file .*gdb_sample.py, line 7, kwenye bar \(a=1, b=2, c=3\)
    baz\(a, b, c\)
$''')

    @unittest.skipUnless(HAS_PYUP_PYDOWN, "test requires py-up/py-down commands")
    eleza test_down_at_bottom(self):
        'Verify handling of "py-down" at the bottom of the stack'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_komapoint=['py-down'])
        self.assertEndsWith(bt,
                            'Unable to find a newer python frame\n')

    @unittest.skipUnless(HAS_PYUP_PYDOWN, "test requires py-up/py-down commands")
    eleza test_up_at_top(self):
        'Verify handling of "py-up" at the top of the stack'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_komapoint=['py-up'] * 5)
        self.assertEndsWith(bt,
                            'Unable to find an older python frame\n')

    @unittest.skipUnless(HAS_PYUP_PYDOWN, "test requires py-up/py-down commands")
    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled ukijumuisha optimizations")
    eleza test_up_then_down(self):
        'Verify "py-up" followed by "py-down"'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_komapoint=['py-up', 'py-up', 'py-down'])
        self.assertMultilineMatches(bt,
                                    r'''^.*
#[0-9]+ Frame 0x-?[0-9a-f]+, kila file .*gdb_sample.py, line 7, kwenye bar \(a=1, b=2, c=3\)
    baz\(a, b, c\)
#[0-9]+ Frame 0x-?[0-9a-f]+, kila file .*gdb_sample.py, line 10, kwenye baz \(args=\(1, 2, 3\)\)
    id\(42\)
$''')

kundi PyBtTests(DebuggerTests):
    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled ukijumuisha optimizations")
    eleza test_bt(self):
        'Verify that the "py-bt" command works'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_komapoint=['py-bt'])
        self.assertMultilineMatches(bt,
                                    r'''^.*
Traceback \(most recent call first\):
  <built-in method id of module object .*>
  File ".*gdb_sample.py", line 10, kwenye baz
    id\(42\)
  File ".*gdb_sample.py", line 7, kwenye bar
    baz\(a, b, c\)
  File ".*gdb_sample.py", line 4, kwenye foo
    bar\(a, b, c\)
  File ".*gdb_sample.py", line 12, kwenye <module>
    foo\(1, 2, 3\)
''')

    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled ukijumuisha optimizations")
    eleza test_bt_full(self):
        'Verify that the "py-bt-full" command works'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_komapoint=['py-bt-full'])
        self.assertMultilineMatches(bt,
                                    r'''^.*
#[0-9]+ Frame 0x-?[0-9a-f]+, kila file .*gdb_sample.py, line 7, kwenye bar \(a=1, b=2, c=3\)
    baz\(a, b, c\)
#[0-9]+ Frame 0x-?[0-9a-f]+, kila file .*gdb_sample.py, line 4, kwenye foo \(a=1, b=2, c=3\)
    bar\(a, b, c\)
#[0-9]+ Frame 0x-?[0-9a-f]+, kila file .*gdb_sample.py, line 12, kwenye <module> \(\)
    foo\(1, 2, 3\)
''')

    eleza test_threads(self):
        'Verify that "py-bt" indicates threads that are waiting kila the GIL'
        cmd = '''
kutoka threading agiza Thread

kundi TestThread(Thread):
    # These threads would run forever, but we'll interrupt things ukijumuisha the
    # debugger
    eleza run(self):
        i = 0
        wakati 1:
             i += 1

t = {}
kila i kwenye range(4):
   t[i] = TestThread()
   t[i].start()

# Trigger a komapoint on the main thread
id(42)

'''
        # Verify ukijumuisha "py-bt":
        gdb_output = self.get_stack_trace(cmd,
                                          cmds_after_komapoint=['thread apply all py-bt'])
        self.assertIn('Waiting kila the GIL', gdb_output)

        # Verify ukijumuisha "py-bt-full":
        gdb_output = self.get_stack_trace(cmd,
                                          cmds_after_komapoint=['thread apply all py-bt-full'])
        self.assertIn('Waiting kila the GIL', gdb_output)

    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled ukijumuisha optimizations")
    # Some older versions of gdb will fail with
    #  "Cannot find new threads: generic error"
    # unless we add LD_PRELOAD=PATH-TO-libpthread.so.1 kama a workaround
    eleza test_gc(self):
        'Verify that "py-bt" indicates ikiwa a thread ni garbage-collecting'
        cmd = ('kutoka gc agiza collect\n'
               'id(42)\n'
               'eleza foo():\n'
               '    collect()\n'
               'eleza bar():\n'
               '    foo()\n'
               'bar()\n')
        # Verify ukijumuisha "py-bt":
        gdb_output = self.get_stack_trace(cmd,
                                          cmds_after_komapoint=['koma update_refs', 'endelea', 'py-bt'],
                                          )
        self.assertIn('Garbage-collecting', gdb_output)

        # Verify ukijumuisha "py-bt-full":
        gdb_output = self.get_stack_trace(cmd,
                                          cmds_after_komapoint=['koma update_refs', 'endelea', 'py-bt-full'],
                                          )
        self.assertIn('Garbage-collecting', gdb_output)

    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled ukijumuisha optimizations")
    # Some older versions of gdb will fail with
    #  "Cannot find new threads: generic error"
    # unless we add LD_PRELOAD=PATH-TO-libpthread.so.1 kama a workaround
    eleza test_pycfunction(self):
        'Verify that "py-bt" displays invocations of PyCFunction instances'
        # Various optimizations multiply the code paths by which these are
        # called, so test a variety of calling conventions.
        kila py_name, py_args, c_name, expected_frame_number kwenye (
            ('gmtime', '', 'time_gmtime', 1),  # METH_VARARGS
            ('len', '[]', 'builtin_len', 1),  # METH_O
            ('locals', '', 'builtin_locals', 1),  # METH_NOARGS
            ('iter', '[]', 'builtin_iter', 1),  # METH_FASTCALL
            ('sorted', '[]', 'builtin_sorted', 1),  # METH_FASTCALL|METH_KEYWORDS
        ):
            ukijumuisha self.subTest(c_name):
                cmd = ('kutoka time agiza gmtime\n'  # (not always needed)
                    'eleza foo():\n'
                    f'    {py_name}({py_args})\n'
                    'eleza bar():\n'
                    '    foo()\n'
                    'bar()\n')
                # Verify ukijumuisha "py-bt":
                gdb_output = self.get_stack_trace(
                    cmd,
                    komapoint=c_name,
                    cmds_after_komapoint=['bt', 'py-bt'],
                )
                self.assertIn(f'<built-in method {py_name}', gdb_output)

                # Verify ukijumuisha "py-bt-full":
                gdb_output = self.get_stack_trace(
                    cmd,
                    komapoint=c_name,
                    cmds_after_komapoint=['py-bt-full'],
                )
                self.assertIn(
                    f'#{expected_frame_number} <built-in method {py_name}',
                    gdb_output,
                )

    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled ukijumuisha optimizations")
    eleza test_wrapper_call(self):
        cmd = textwrap.dedent('''
            kundi MyList(list):
                eleza __init__(self):
                    super().__init__()   # wrapper_call()

            id("first koma point")
            l = MyList()
        ''')
        cmds_after_komapoint = ['koma wrapper_call', 'endelea']
        ikiwa CET_PROTECTION:
            # bpo-32962: same case kama kwenye get_stack_trace():
            # we need an additional 'next' command kwenye order to read
            # arguments of the innermost function of the call stack.
            cmds_after_komapoint.append('next')
        cmds_after_komapoint.append('py-bt')

        # Verify ukijumuisha "py-bt":
        gdb_output = self.get_stack_trace(cmd,
                                          cmds_after_komapoint=cmds_after_komapoint)
        self.assertRegex(gdb_output,
                         r"<method-wrapper u?'__init__' of MyList object at ")


kundi PyPrintTests(DebuggerTests):
    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled ukijumuisha optimizations")
    eleza test_basic_command(self):
        'Verify that the "py-print" command works'
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_komapoint=['py-up', 'py-print args'])
        self.assertMultilineMatches(bt,
                                    r".*\nlocal 'args' = \(1, 2, 3\)\n.*")

    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled ukijumuisha optimizations")
    @unittest.skipUnless(HAS_PYUP_PYDOWN, "test requires py-up/py-down commands")
    eleza test_print_after_up(self):
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_komapoint=['py-up', 'py-up', 'py-print c', 'py-print b', 'py-print a'])
        self.assertMultilineMatches(bt,
                                    r".*\nlocal 'c' = 3\nlocal 'b' = 2\nlocal 'a' = 1\n.*")

    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled ukijumuisha optimizations")
    eleza test_printing_global(self):
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_komapoint=['py-up', 'py-print __name__'])
        self.assertMultilineMatches(bt,
                                    r".*\nglobal '__name__' = '__main__'\n.*")

    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled ukijumuisha optimizations")
    eleza test_printing_builtin(self):
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_komapoint=['py-up', 'py-print len'])
        self.assertMultilineMatches(bt,
                                    r".*\nbuiltin 'len' = <built-in method len of module object at remote 0x-?[0-9a-f]+>\n.*")

kundi PyLocalsTests(DebuggerTests):
    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled ukijumuisha optimizations")
    eleza test_basic_command(self):
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_komapoint=['py-up', 'py-locals'])
        self.assertMultilineMatches(bt,
                                    r".*\nargs = \(1, 2, 3\)\n.*")

    @unittest.skipUnless(HAS_PYUP_PYDOWN, "test requires py-up/py-down commands")
    @unittest.skipIf(python_is_optimized(),
                     "Python was compiled ukijumuisha optimizations")
    eleza test_locals_after_up(self):
        bt = self.get_stack_trace(script=self.get_sample_script(),
                                  cmds_after_komapoint=['py-up', 'py-up', 'py-locals'])
        self.assertMultilineMatches(bt,
                                    r".*\na = 1\nb = 2\nc = 3\n.*")

eleza test_main():
    ikiwa support.verbose:
        andika("GDB version %s.%s:" % (gdb_major_version, gdb_minor_version))
        kila line kwenye gdb_version.splitlines():
            andika(" " * 4 + line)
    run_unittest(PrettyPrintTests,
                 PyListTests,
                 StackNavigationTests,
                 PyBtTests,
                 PyPrintTests,
                 PyLocalsTests
                 )

ikiwa __name__ == "__main__":
    test_main()
