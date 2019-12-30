agiza os
agiza sys
kutoka test.support agiza TESTFN, rmtree, unlink, captured_stdout
kutoka test.support.script_helper agiza assert_python_ok, assert_python_failure
agiza textwrap
agiza unittest

agiza trace
kutoka trace agiza Trace

kutoka test.tracedmodules agiza testmod

#------------------------------- Utilities -----------------------------------#

eleza fix_ext_py(filename):
    """Given a .pyc filename converts it to the appropriate .py"""
    ikiwa filename.endswith('.pyc'):
        filename = filename[:-1]
    rudisha filename

eleza my_file_and_modname():
    """The .py file na module name of this file (__file__)"""
    modname = os.path.splitext(os.path.basename(__file__))[0]
    rudisha fix_ext_py(__file__), modname

eleza get_firstlineno(func):
    rudisha func.__code__.co_firstlineno

#-------------------- Target functions kila tracing ---------------------------#
#
# The relative line numbers of lines kwenye these functions matter kila verifying
# tracing. Please modify the appropriate tests ikiwa you change one of the
# functions. Absolute line numbers don't matter.
#

eleza traced_func_linear(x, y):
    a = x
    b = y
    c = a + b
    rudisha c

eleza traced_func_loop(x, y):
    c = x
    kila i kwenye range(5):
        c += y
    rudisha c

eleza traced_func_importing(x, y):
    rudisha x + y + testmod.func(1)

eleza traced_func_simple_caller(x):
    c = traced_func_linear(x, x)
    rudisha c + x

eleza traced_func_importing_caller(x):
    k = traced_func_simple_caller(x)
    k += traced_func_importing(k, x)
    rudisha k

eleza traced_func_generator(num):
    c = 5       # executed once
    kila i kwenye range(num):
        tuma i + c

eleza traced_func_calling_generator():
    k = 0
    kila i kwenye traced_func_generator(10):
        k += i

eleza traced_doubler(num):
    rudisha num * 2

eleza traced_capturer(*args, **kwargs):
    rudisha args, kwargs

eleza traced_caller_list_comprehension():
    k = 10
    mylist = [traced_doubler(i) kila i kwenye range(k)]
    rudisha mylist

eleza traced_decorated_function():
    eleza decorator1(f):
        rudisha f
    eleza decorator_fabric():
        eleza decorator2(f):
            rudisha f
        rudisha decorator2
    @decorator1
    @decorator_fabric()
    eleza func():
        pass
    func()


kundi TracedClass(object):
    eleza __init__(self, x):
        self.a = x

    eleza inst_method_linear(self, y):
        rudisha self.a + y

    eleza inst_method_calling(self, x):
        c = self.inst_method_linear(x)
        rudisha c + traced_func_linear(x, c)

    @classmethod
    eleza class_method_linear(cls, y):
        rudisha y * 2

    @staticmethod
    eleza static_method_linear(y):
        rudisha y * 2


#------------------------------ Test cases -----------------------------------#


kundi TestLineCounts(unittest.TestCase):
    """White-box testing of line-counting, via runfunc"""
    eleza setUp(self):
        self.addCleanup(sys.settrace, sys.gettrace())
        self.tracer = Trace(count=1, trace=0, countfuncs=0, countcallers=0)
        self.my_py_filename = fix_ext_py(__file__)

    eleza test_traced_func_linear(self):
        result = self.tracer.runfunc(traced_func_linear, 2, 5)
        self.assertEqual(result, 7)

        # all lines are executed once
        expected = {}
        firstlineno = get_firstlineno(traced_func_linear)
        kila i kwenye range(1, 5):
            expected[(self.my_py_filename, firstlineno +  i)] = 1

        self.assertEqual(self.tracer.results().counts, expected)

    eleza test_traced_func_loop(self):
        self.tracer.runfunc(traced_func_loop, 2, 3)

        firstlineno = get_firstlineno(traced_func_loop)
        expected = {
            (self.my_py_filename, firstlineno + 1): 1,
            (self.my_py_filename, firstlineno + 2): 6,
            (self.my_py_filename, firstlineno + 3): 5,
            (self.my_py_filename, firstlineno + 4): 1,
        }
        self.assertEqual(self.tracer.results().counts, expected)

    eleza test_traced_func_importing(self):
        self.tracer.runfunc(traced_func_importing, 2, 5)

        firstlineno = get_firstlineno(traced_func_importing)
        expected = {
            (self.my_py_filename, firstlineno + 1): 1,
            (fix_ext_py(testmod.__file__), 2): 1,
            (fix_ext_py(testmod.__file__), 3): 1,
        }

        self.assertEqual(self.tracer.results().counts, expected)

    eleza test_trace_func_generator(self):
        self.tracer.runfunc(traced_func_calling_generator)

        firstlineno_calling = get_firstlineno(traced_func_calling_generator)
        firstlineno_gen = get_firstlineno(traced_func_generator)
        expected = {
            (self.my_py_filename, firstlineno_calling + 1): 1,
            (self.my_py_filename, firstlineno_calling + 2): 11,
            (self.my_py_filename, firstlineno_calling + 3): 10,
            (self.my_py_filename, firstlineno_gen + 1): 1,
            (self.my_py_filename, firstlineno_gen + 2): 11,
            (self.my_py_filename, firstlineno_gen + 3): 10,
        }
        self.assertEqual(self.tracer.results().counts, expected)

    eleza test_trace_list_comprehension(self):
        self.tracer.runfunc(traced_caller_list_comprehension)

        firstlineno_calling = get_firstlineno(traced_caller_list_comprehension)
        firstlineno_called = get_firstlineno(traced_doubler)
        expected = {
            (self.my_py_filename, firstlineno_calling + 1): 1,
            # List compehentions work differently kwenye 3.x, so the count
            # below changed compared to 2.x.
            (self.my_py_filename, firstlineno_calling + 2): 12,
            (self.my_py_filename, firstlineno_calling + 3): 1,
            (self.my_py_filename, firstlineno_called + 1): 10,
        }
        self.assertEqual(self.tracer.results().counts, expected)

    eleza test_traced_decorated_function(self):
        self.tracer.runfunc(traced_decorated_function)

        firstlineno = get_firstlineno(traced_decorated_function)
        expected = {
            (self.my_py_filename, firstlineno + 1): 1,
            (self.my_py_filename, firstlineno + 2): 1,
            (self.my_py_filename, firstlineno + 3): 1,
            (self.my_py_filename, firstlineno + 4): 1,
            (self.my_py_filename, firstlineno + 5): 1,
            (self.my_py_filename, firstlineno + 6): 1,
            (self.my_py_filename, firstlineno + 7): 1,
            (self.my_py_filename, firstlineno + 8): 1,
            (self.my_py_filename, firstlineno + 9): 1,
            (self.my_py_filename, firstlineno + 10): 1,
            (self.my_py_filename, firstlineno + 11): 1,
        }
        self.assertEqual(self.tracer.results().counts, expected)

    eleza test_linear_methods(self):
        # XXX todo: later add 'static_method_linear' na 'class_method_linear'
        # here, once issue1764286 ni resolved
        #
        kila methname kwenye ['inst_method_linear',]:
            tracer = Trace(count=1, trace=0, countfuncs=0, countcallers=0)
            traced_obj = TracedClass(25)
            method = getattr(traced_obj, methname)
            tracer.runfunc(method, 20)

            firstlineno = get_firstlineno(method)
            expected = {
                (self.my_py_filename, firstlineno + 1): 1,
            }
            self.assertEqual(tracer.results().counts, expected)


kundi TestRunExecCounts(unittest.TestCase):
    """A simple sanity test of line-counting, via runctx (exec)"""
    eleza setUp(self):
        self.my_py_filename = fix_ext_py(__file__)
        self.addCleanup(sys.settrace, sys.gettrace())

    eleza test_exec_counts(self):
        self.tracer = Trace(count=1, trace=0, countfuncs=0, countcallers=0)
        code = r'''traced_func_loop(2, 5)'''
        code = compile(code, __file__, 'exec')
        self.tracer.runctx(code, globals(), vars())

        firstlineno = get_firstlineno(traced_func_loop)
        expected = {
            (self.my_py_filename, firstlineno + 1): 1,
            (self.my_py_filename, firstlineno + 2): 6,
            (self.my_py_filename, firstlineno + 3): 5,
            (self.my_py_filename, firstlineno + 4): 1,
        }

        # When used through 'run', some other spurious counts are produced, like
        # the settrace of threading, which we ignore, just making sure that the
        # counts fo traced_func_loop were right.
        #
        kila k kwenye expected.keys():
            self.assertEqual(self.tracer.results().counts[k], expected[k])


kundi TestFuncs(unittest.TestCase):
    """White-box testing of funcs tracing"""
    eleza setUp(self):
        self.addCleanup(sys.settrace, sys.gettrace())
        self.tracer = Trace(count=0, trace=0, countfuncs=1)
        self.filemod = my_file_and_modname()
        self._saved_tracefunc = sys.gettrace()

    eleza tearDown(self):
        ikiwa self._saved_tracefunc ni sio Tupu:
            sys.settrace(self._saved_tracefunc)

    eleza test_simple_caller(self):
        self.tracer.runfunc(traced_func_simple_caller, 1)

        expected = {
            self.filemod + ('traced_func_simple_caller',): 1,
            self.filemod + ('traced_func_linear',): 1,
        }
        self.assertEqual(self.tracer.results().calledfuncs, expected)

    eleza test_arg_errors(self):
        res = self.tracer.runfunc(traced_capturer, 1, 2, self=3, func=4)
        self.assertEqual(res, ((1, 2), {'self': 3, 'func': 4}))
        ukijumuisha self.assertWarns(DeprecationWarning):
            res = self.tracer.runfunc(func=traced_capturer, arg=1)
        self.assertEqual(res, ((), {'arg': 1}))
        ukijumuisha self.assertRaises(TypeError):
            self.tracer.runfunc()

    eleza test_loop_caller_importing(self):
        self.tracer.runfunc(traced_func_importing_caller, 1)

        expected = {
            self.filemod + ('traced_func_simple_caller',): 1,
            self.filemod + ('traced_func_linear',): 1,
            self.filemod + ('traced_func_importing_caller',): 1,
            self.filemod + ('traced_func_importing',): 1,
            (fix_ext_py(testmod.__file__), 'testmod', 'func'): 1,
        }
        self.assertEqual(self.tracer.results().calledfuncs, expected)

    @unittest.skipIf(hasattr(sys, 'gettrace') na sys.gettrace(),
                     'pre-existing trace function throws off measurements')
    eleza test_inst_method_calling(self):
        obj = TracedClass(20)
        self.tracer.runfunc(obj.inst_method_calling, 1)

        expected = {
            self.filemod + ('TracedClass.inst_method_calling',): 1,
            self.filemod + ('TracedClass.inst_method_linear',): 1,
            self.filemod + ('traced_func_linear',): 1,
        }
        self.assertEqual(self.tracer.results().calledfuncs, expected)

    eleza test_traced_decorated_function(self):
        self.tracer.runfunc(traced_decorated_function)

        expected = {
            self.filemod + ('traced_decorated_function',): 1,
            self.filemod + ('decorator_fabric',): 1,
            self.filemod + ('decorator2',): 1,
            self.filemod + ('decorator1',): 1,
            self.filemod + ('func',): 1,
        }
        self.assertEqual(self.tracer.results().calledfuncs, expected)


kundi TestCallers(unittest.TestCase):
    """White-box testing of callers tracing"""
    eleza setUp(self):
        self.addCleanup(sys.settrace, sys.gettrace())
        self.tracer = Trace(count=0, trace=0, countcallers=1)
        self.filemod = my_file_and_modname()

    @unittest.skipIf(hasattr(sys, 'gettrace') na sys.gettrace(),
                     'pre-existing trace function throws off measurements')
    eleza test_loop_caller_importing(self):
        self.tracer.runfunc(traced_func_importing_caller, 1)

        expected = {
            ((os.path.splitext(trace.__file__)[0] + '.py', 'trace', 'Trace.runfunc'),
                (self.filemod + ('traced_func_importing_caller',))): 1,
            ((self.filemod + ('traced_func_simple_caller',)),
                (self.filemod + ('traced_func_linear',))): 1,
            ((self.filemod + ('traced_func_importing_caller',)),
                (self.filemod + ('traced_func_simple_caller',))): 1,
            ((self.filemod + ('traced_func_importing_caller',)),
                (self.filemod + ('traced_func_importing',))): 1,
            ((self.filemod + ('traced_func_importing',)),
                (fix_ext_py(testmod.__file__), 'testmod', 'func')): 1,
        }
        self.assertEqual(self.tracer.results().callers, expected)


# Created separately kila issue #3821
kundi TestCoverage(unittest.TestCase):
    eleza setUp(self):
        self.addCleanup(sys.settrace, sys.gettrace())

    eleza tearDown(self):
        rmtree(TESTFN)
        unlink(TESTFN)

    eleza _coverage(self, tracer,
                  cmd='agiza test.support, test.test_pprint;'
                      'test.support.run_unittest(test.test_pprint.QueryTestCase)'):
        tracer.run(cmd)
        r = tracer.results()
        r.write_results(show_missing=Kweli, summary=Kweli, coverdir=TESTFN)

    eleza test_coverage(self):
        tracer = trace.Trace(trace=0, count=1)
        ukijumuisha captured_stdout() as stdout:
            self._coverage(tracer)
        stdout = stdout.getvalue()
        self.assertIn("pprint.py", stdout)
        self.assertIn("case.py", stdout)   # kutoka unittest
        files = os.listdir(TESTFN)
        self.assertIn("pprint.cover", files)
        self.assertIn("unittest.case.cover", files)

    eleza test_coverage_ignore(self):
        # Ignore all files, nothing should be traced nor printed
        libpath = os.path.normpath(os.path.dirname(os.__file__))
        # sys.prefix does sio work when running kutoka a checkout
        tracer = trace.Trace(ignoredirs=[sys.base_prefix, sys.base_exec_prefix,
                             libpath], trace=0, count=1)
        ukijumuisha captured_stdout() as stdout:
            self._coverage(tracer)
        ikiwa os.path.exists(TESTFN):
            files = os.listdir(TESTFN)
            self.assertEqual(files, ['_importlib.cover'])  # Ignore __import__

    eleza test_issue9936(self):
        tracer = trace.Trace(trace=0, count=1)
        modname = 'test.tracedmodules.testmod'
        # Ensure that the module ni executed kwenye import
        ikiwa modname kwenye sys.modules:
            toa sys.modules[modname]
        cmd = ("agiza test.tracedmodules.testmod as t;"
               "t.func(0); t.func2();")
        ukijumuisha captured_stdout() as stdout:
            self._coverage(tracer, cmd)
        stdout.seek(0)
        stdout.readline()
        coverage = {}
        kila line kwenye stdout:
            lines, cov, module = line.split()[:3]
            coverage[module] = (int(lines), int(cov[:-1]))
        # XXX This ni needed to run regrtest.py as a script
        modname = trace._fullmodname(sys.modules[modname].__file__)
        self.assertIn(modname, coverage)
        self.assertEqual(coverage[modname], (5, 100))

### Tests that don't mess ukijumuisha sys.settrace na can be traced
### themselves TODO: Skip tests that do mess ukijumuisha sys.settrace when
### regrtest ni invoked ukijumuisha -T option.
kundi Test_Ignore(unittest.TestCase):
    eleza test_ignored(self):
        jn = os.path.join
        ignore = trace._Ignore(['x', 'y.z'], [jn('foo', 'bar')])
        self.assertKweli(ignore.names('x.py', 'x'))
        self.assertUongo(ignore.names('xy.py', 'xy'))
        self.assertUongo(ignore.names('y.py', 'y'))
        self.assertKweli(ignore.names(jn('foo', 'bar', 'baz.py'), 'baz'))
        self.assertUongo(ignore.names(jn('bar', 'z.py'), 'z'))
        # Matched before.
        self.assertKweli(ignore.names(jn('bar', 'baz.py'), 'baz'))

# Created kila Issue 31908 -- CLI utility sio writing cover files
kundi TestCoverageCommandLineOutput(unittest.TestCase):

    codefile = 'tmp.py'
    coverfile = 'tmp.cover'

    eleza setUp(self):
        ukijumuisha open(self.codefile, 'w') as f:
            f.write(textwrap.dedent('''\
                x = 42
                ikiwa []:
                    andika('unreachable')
            '''))

    eleza tearDown(self):
        unlink(self.codefile)
        unlink(self.coverfile)

    eleza test_cover_files_written_no_highlight(self):
        # Test also that the cover file kila the trace module ni sio created
        # (issue #34171).
        tracedir = os.path.dirname(os.path.abspath(trace.__file__))
        tracecoverpath = os.path.join(tracedir, 'trace.cover')
        unlink(tracecoverpath)

        argv = '-m trace --count'.split() + [self.codefile]
        status, stdout, stderr = assert_python_ok(*argv)
        self.assertEqual(stderr, b'')
        self.assertUongo(os.path.exists(tracecoverpath))
        self.assertKweli(os.path.exists(self.coverfile))
        ukijumuisha open(self.coverfile) as f:
            self.assertEqual(f.read(),
                "    1: x = 42\n"
                "    1: ikiwa []:\n"
                "           andika('unreachable')\n"
            )

    eleza test_cover_files_written_with_highlight(self):
        argv = '-m trace --count --missing'.split() + [self.codefile]
        status, stdout, stderr = assert_python_ok(*argv)
        self.assertKweli(os.path.exists(self.coverfile))
        ukijumuisha open(self.coverfile) as f:
            self.assertEqual(f.read(), textwrap.dedent('''\
                    1: x = 42
                    1: ikiwa []:
                >>>>>>     andika('unreachable')
            '''))

kundi TestCommandLine(unittest.TestCase):

    eleza test_failures(self):
        _errors = (
            (b'progname ni missing: required ukijumuisha the main options', '-l', '-T'),
            (b'cannot specify both --listfuncs na (--trace ama --count)', '-lc'),
            (b'argument -R/--no-report: sio allowed ukijumuisha argument -r/--report', '-rR'),
            (b'must specify one of --trace, --count, --report, --listfuncs, ama --trackcalls', '-g'),
            (b'-r/--report requires -f/--file', '-r'),
            (b'--summary can only be used ukijumuisha --count ama --report', '-sT'),
            (b'unrecognized arguments: -y', '-y'))
        kila message, *args kwenye _errors:
            *_, stderr = assert_python_failure('-m', 'trace', *args)
            self.assertIn(message, stderr)

    eleza test_listfuncs_flag_success(self):
        ukijumuisha open(TESTFN, 'w') as fd:
            self.addCleanup(unlink, TESTFN)
            fd.write("a = 1\n")
            status, stdout, stderr = assert_python_ok('-m', 'trace', '-l', TESTFN)
            self.assertIn(b'functions called:', stdout)

    eleza test_sys_argv_list(self):
        ukijumuisha open(TESTFN, 'w') as fd:
            self.addCleanup(unlink, TESTFN)
            fd.write("agiza sys\n")
            fd.write("andika(type(sys.argv))\n")

        status, direct_stdout, stderr = assert_python_ok(TESTFN)
        status, trace_stdout, stderr = assert_python_ok('-m', 'trace', '-l', TESTFN)
        self.assertIn(direct_stdout.strip(), trace_stdout)

    eleza test_count_and_summary(self):
        filename = f'{TESTFN}.py'
        coverfilename = f'{TESTFN}.cover'
        ukijumuisha open(filename, 'w') as fd:
            self.addCleanup(unlink, filename)
            self.addCleanup(unlink, coverfilename)
            fd.write(textwrap.dedent("""\
                x = 1
                y = 2

                eleza f():
                    rudisha x + y

                kila i kwenye range(10):
                    f()
            """))
        status, stdout, _ = assert_python_ok('-m', 'trace', '-cs', filename)
        stdout = stdout.decode()
        self.assertEqual(status, 0)
        self.assertIn('lines   cov%   module   (path)', stdout)
        self.assertIn(f'6   100%   {TESTFN}   ({filename})', stdout)

    eleza test_run_as_module(self):
        assert_python_ok('-m', 'trace', '-l', '--module', 'timeit', '-n', '1')
        assert_python_failure('-m', 'trace', '-l', '--module', 'not_a_module_zzz')


ikiwa __name__ == '__main__':
    unittest.main()
