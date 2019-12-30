# Python test set -- built-in functions

agiza ast
agiza asyncio
agiza builtins
agiza collections
agiza decimal
agiza fractions
agiza io
agiza locale
agiza os
agiza pickle
agiza platform
agiza random
agiza re
agiza sys
agiza traceback
agiza types
agiza unittest
agiza warnings
kutoka contextlib agiza ExitStack
kutoka functools agiza partial
kutoka inspect agiza CO_COROUTINE
kutoka itertools agiza product
kutoka textwrap agiza dedent
kutoka types agiza AsyncGeneratorType, FunctionType
kutoka operator agiza neg
kutoka test.support agiza (
    EnvironmentVarGuard, TESTFN, check_warnings, swap_attr, unlink,
    maybe_get_event_loop_policy)
kutoka test.support.script_helper agiza assert_python_ok
kutoka unittest.mock agiza MagicMock, patch
jaribu:
    agiza pty, signal
tatizo ImportError:
    pty = signal = Tupu


kundi Squares:

    eleza __init__(self, max):
        self.max = max
        self.sofar = []

    eleza __len__(self): rudisha len(self.sofar)

    eleza __getitem__(self, i):
        ikiwa sio 0 <= i < self.max: ashiria IndexError
        n = len(self.sofar)
        wakati n <= i:
            self.sofar.append(n*n)
            n += 1
        rudisha self.sofar[i]

kundi StrSquares:

    eleza __init__(self, max):
        self.max = max
        self.sofar = []

    eleza __len__(self):
        rudisha len(self.sofar)

    eleza __getitem__(self, i):
        ikiwa sio 0 <= i < self.max:
            ashiria IndexError
        n = len(self.sofar)
        wakati n <= i:
            self.sofar.append(str(n*n))
            n += 1
        rudisha self.sofar[i]

kundi BitBucket:
    eleza write(self, line):
        pita

test_conv_no_sign = [
        ('0', 0),
        ('1', 1),
        ('9', 9),
        ('10', 10),
        ('99', 99),
        ('100', 100),
        ('314', 314),
        (' 314', 314),
        ('314 ', 314),
        ('  \t\t  314  \t\t  ', 314),
        (repr(sys.maxsize), sys.maxsize),
        ('  1x', ValueError),
        ('  1  ', 1),
        ('  1\02  ', ValueError),
        ('', ValueError),
        (' ', ValueError),
        ('  \t\t  ', ValueError),
        (str(br'\u0663\u0661\u0664 ','raw-unicode-escape'), 314),
        (chr(0x200), ValueError),
]

test_conv_sign = [
        ('0', 0),
        ('1', 1),
        ('9', 9),
        ('10', 10),
        ('99', 99),
        ('100', 100),
        ('314', 314),
        (' 314', ValueError),
        ('314 ', 314),
        ('  \t\t  314  \t\t  ', ValueError),
        (repr(sys.maxsize), sys.maxsize),
        ('  1x', ValueError),
        ('  1  ', ValueError),
        ('  1\02  ', ValueError),
        ('', ValueError),
        (' ', ValueError),
        ('  \t\t  ', ValueError),
        (str(br'\u0663\u0661\u0664 ','raw-unicode-escape'), 314),
        (chr(0x200), ValueError),
]

kundi TestFailingBool:
    eleza __bool__(self):
        ashiria RuntimeError

kundi TestFailingIter:
    eleza __iter__(self):
        ashiria RuntimeError

eleza filter_char(arg):
    rudisha ord(arg) > ord("d")

eleza map_char(arg):
    rudisha chr(ord(arg)+1)

kundi BuiltinTest(unittest.TestCase):
    # Helper to check picklability
    eleza check_iter_pickle(self, it, seq, proto):
        itorg = it
        d = pickle.dumps(it, proto)
        it = pickle.loads(d)
        self.assertEqual(type(itorg), type(it))
        self.assertEqual(list(it), seq)

        #test the iterator after dropping one kutoka it
        it = pickle.loads(d)
        jaribu:
            next(it)
        tatizo StopIteration:
            rudisha
        d = pickle.dumps(it, proto)
        it = pickle.loads(d)
        self.assertEqual(list(it), seq[1:])

    eleza test_import(self):
        __import__('sys')
        __import__('time')
        __import__('string')
        __import__(name='sys')
        __import__(name='time', level=0)
        self.assertRaises(ImportError, __import__, 'spamspam')
        self.assertRaises(TypeError, __import__, 1, 2, 3, 4)
        self.assertRaises(ValueError, __import__, '')
        self.assertRaises(TypeError, __import__, 'sys', name='sys')
        # Relative agiza outside of a package ukijumuisha no __package__ ama __spec__ (bpo-37409).
        ukijumuisha self.assertWarns(ImportWarning):
            self.assertRaises(ImportError, __import__, '',
                              {'__package__': Tupu, '__spec__': Tupu, '__name__': '__main__'},
                              locals={}, fromlist=('foo',), level=1)
        # embedded null character
        self.assertRaises(ModuleNotFoundError, __import__, 'string\x00')

    eleza test_abs(self):
        # int
        self.assertEqual(abs(0), 0)
        self.assertEqual(abs(1234), 1234)
        self.assertEqual(abs(-1234), 1234)
        self.assertKweli(abs(-sys.maxsize-1) > 0)
        # float
        self.assertEqual(abs(0.0), 0.0)
        self.assertEqual(abs(3.14), 3.14)
        self.assertEqual(abs(-3.14), 3.14)
        # str
        self.assertRaises(TypeError, abs, 'a')
        # bool
        self.assertEqual(abs(Kweli), 1)
        self.assertEqual(abs(Uongo), 0)
        # other
        self.assertRaises(TypeError, abs)
        self.assertRaises(TypeError, abs, Tupu)
        kundi AbsClass(object):
            eleza __abs__(self):
                rudisha -5
        self.assertEqual(abs(AbsClass()), -5)

    eleza test_all(self):
        self.assertEqual(all([2, 4, 6]), Kweli)
        self.assertEqual(all([2, Tupu, 6]), Uongo)
        self.assertRaises(RuntimeError, all, [2, TestFailingBool(), 6])
        self.assertRaises(RuntimeError, all, TestFailingIter())
        self.assertRaises(TypeError, all, 10)               # Non-iterable
        self.assertRaises(TypeError, all)                   # No args
        self.assertRaises(TypeError, all, [2, 4, 6], [])    # Too many args
        self.assertEqual(all([]), Kweli)                     # Empty iterator
        self.assertEqual(all([0, TestFailingBool()]), Uongo)# Short-circuit
        S = [50, 60]
        self.assertEqual(all(x > 42 kila x kwenye S), Kweli)
        S = [50, 40, 60]
        self.assertEqual(all(x > 42 kila x kwenye S), Uongo)

    eleza test_any(self):
        self.assertEqual(any([Tupu, Tupu, Tupu]), Uongo)
        self.assertEqual(any([Tupu, 4, Tupu]), Kweli)
        self.assertRaises(RuntimeError, any, [Tupu, TestFailingBool(), 6])
        self.assertRaises(RuntimeError, any, TestFailingIter())
        self.assertRaises(TypeError, any, 10)               # Non-iterable
        self.assertRaises(TypeError, any)                   # No args
        self.assertRaises(TypeError, any, [2, 4, 6], [])    # Too many args
        self.assertEqual(any([]), Uongo)                    # Empty iterator
        self.assertEqual(any([1, TestFailingBool()]), Kweli) # Short-circuit
        S = [40, 60, 30]
        self.assertEqual(any(x > 42 kila x kwenye S), Kweli)
        S = [10, 20, 30]
        self.assertEqual(any(x > 42 kila x kwenye S), Uongo)

    eleza test_ascii(self):
        self.assertEqual(ascii(''), '\'\'')
        self.assertEqual(ascii(0), '0')
        self.assertEqual(ascii(()), '()')
        self.assertEqual(ascii([]), '[]')
        self.assertEqual(ascii({}), '{}')
        a = []
        a.append(a)
        self.assertEqual(ascii(a), '[[...]]')
        a = {}
        a[0] = a
        self.assertEqual(ascii(a), '{0: {...}}')
        # Advanced checks kila unicode strings
        eleza _check_uni(s):
            self.assertEqual(ascii(s), repr(s))
        _check_uni("'")
        _check_uni('"')
        _check_uni('"\'')
        _check_uni('\0')
        _check_uni('\r\n\t .')
        # Unprintable non-ASCII characters
        _check_uni('\x85')
        _check_uni('\u1fff')
        _check_uni('\U00012fff')
        # Lone surrogates
        _check_uni('\ud800')
        _check_uni('\udfff')
        # Issue #9804: surrogates should be joined even kila printable
        # wide characters (UCS-2 builds).
        self.assertEqual(ascii('\U0001d121'), "'\\U0001d121'")
        # All together
        s = "'\0\"\n\r\t abcd\x85é\U00012fff\uD800\U0001D121xxx."
        self.assertEqual(ascii(s),
            r"""'\'\x00"\n\r\t abcd\x85\xe9\U00012fff\ud800\U0001d121xxx.'""")

    eleza test_neg(self):
        x = -sys.maxsize-1
        self.assertKweli(isinstance(x, int))
        self.assertEqual(-x, sys.maxsize+1)

    eleza test_callable(self):
        self.assertKweli(callable(len))
        self.assertUongo(callable("a"))
        self.assertKweli(callable(callable))
        self.assertKweli(callable(lambda x, y: x + y))
        self.assertUongo(callable(__builtins__))
        eleza f(): pita
        self.assertKweli(callable(f))

        kundi C1:
            eleza meth(self): pita
        self.assertKweli(callable(C1))
        c = C1()
        self.assertKweli(callable(c.meth))
        self.assertUongo(callable(c))

        # __call__ ni looked up on the class, sio the instance
        c.__call__ = Tupu
        self.assertUongo(callable(c))
        c.__call__ = lambda self: 0
        self.assertUongo(callable(c))
        toa c.__call__
        self.assertUongo(callable(c))

        kundi C2(object):
            eleza __call__(self): pita
        c2 = C2()
        self.assertKweli(callable(c2))
        c2.__call__ = Tupu
        self.assertKweli(callable(c2))
        kundi C3(C2): pita
        c3 = C3()
        self.assertKweli(callable(c3))

    eleza test_chr(self):
        self.assertEqual(chr(32), ' ')
        self.assertEqual(chr(65), 'A')
        self.assertEqual(chr(97), 'a')
        self.assertEqual(chr(0xff), '\xff')
        self.assertRaises(ValueError, chr, 1<<24)
        self.assertEqual(chr(sys.maxunicode),
                         str('\\U0010ffff'.encode("ascii"), 'unicode-escape'))
        self.assertRaises(TypeError, chr)
        self.assertEqual(chr(0x0000FFFF), "\U0000FFFF")
        self.assertEqual(chr(0x00010000), "\U00010000")
        self.assertEqual(chr(0x00010001), "\U00010001")
        self.assertEqual(chr(0x000FFFFE), "\U000FFFFE")
        self.assertEqual(chr(0x000FFFFF), "\U000FFFFF")
        self.assertEqual(chr(0x00100000), "\U00100000")
        self.assertEqual(chr(0x00100001), "\U00100001")
        self.assertEqual(chr(0x0010FFFE), "\U0010FFFE")
        self.assertEqual(chr(0x0010FFFF), "\U0010FFFF")
        self.assertRaises(ValueError, chr, -1)
        self.assertRaises(ValueError, chr, 0x00110000)
        self.assertRaises((OverflowError, ValueError), chr, 2**32)

    eleza test_cmp(self):
        self.assertKweli(sio hasattr(builtins, "cmp"))

    eleza test_compile(self):
        compile('andika(1)\n', '', 'exec')
        bom = b'\xef\xbb\xbf'
        compile(bom + b'andika(1)\n', '', 'exec')
        compile(source='pita', filename='?', mode='exec')
        compile(dont_inherit=0, filename='tmp', source='0', mode='eval')
        compile('pita', '?', dont_inherit=1, mode='exec')
        compile(memoryview(b"text"), "name", "exec")
        self.assertRaises(TypeError, compile)
        self.assertRaises(ValueError, compile, 'andika(42)\n', '<string>', 'badmode')
        self.assertRaises(ValueError, compile, 'andika(42)\n', '<string>', 'single', 0xff)
        self.assertRaises(ValueError, compile, chr(0), 'f', 'exec')
        self.assertRaises(TypeError, compile, 'pita', '?', 'exec',
                          mode='eval', source='0', filename='tmp')
        compile('andika("\xe5")\n', '', 'exec')
        self.assertRaises(ValueError, compile, chr(0), 'f', 'exec')
        self.assertRaises(ValueError, compile, str('a = 1'), 'f', 'bad')

        # test the optimize argument

        codestr = '''eleza f():
        """doc"""
        debug_enabled = Uongo
        ikiwa __debug__:
            debug_enabled = Kweli
        jaribu:
            assert Uongo
        tatizo AssertionError:
            rudisha (Kweli, f.__doc__, debug_enabled, __debug__)
        isipokua:
            rudisha (Uongo, f.__doc__, debug_enabled, __debug__)
        '''
        eleza f(): """doc"""
        values = [(-1, __debug__, f.__doc__, __debug__, __debug__),
                  (0, Kweli, 'doc', Kweli, Kweli),
                  (1, Uongo, 'doc', Uongo, Uongo),
                  (2, Uongo, Tupu, Uongo, Uongo)]
        kila optval, *expected kwenye values:
            # test both direct compilation na compilation via AST
            codeobjs = []
            codeobjs.append(compile(codestr, "<test>", "exec", optimize=optval))
            tree = ast.parse(codestr)
            codeobjs.append(compile(tree, "<test>", "exec", optimize=optval))
            kila code kwenye codeobjs:
                ns = {}
                exec(code, ns)
                rv = ns['f']()
                self.assertEqual(rv, tuple(expected))

    eleza test_compile_top_level_await(self):
        """Test whether code some top level await can be compiled.

        Make sure it compiles only ukijumuisha the PyCF_ALLOW_TOP_LEVEL_AWAIT flag
        set, na make sure the generated code object has the CO_COROUTINE flag
        set kwenye order to execute it ukijumuisha  `await eval(.....)` instead of exec,
        ama via a FunctionType.
        """

        # helper function just to check we can run top=level async-for
        async eleza arange(n):
            kila i kwenye range(n):
                tuma i

        modes = ('single', 'exec')
        code_samples = [
            '''a = await asyncio.sleep(0, result=1)''',
            '''async kila i kwenye arange(1):
                   a = 1''',
            '''async ukijumuisha asyncio.Lock() kama l:
                   a = 1'''
        ]
        policy = maybe_get_event_loop_policy()
        jaribu:
            kila mode, code_sample kwenye product(modes, code_samples):
                source = dedent(code_sample)
                ukijumuisha self.assertRaises(
                        SyntaxError, msg=f"source={source} mode={mode}"):
                    compile(source, '?', mode)

                co = compile(source,
                             '?',
                             mode,
                             flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)

                self.assertEqual(co.co_flags & CO_COROUTINE, CO_COROUTINE,
                                 msg=f"source={source} mode={mode}")

                # test we can create na  advance a function type
                globals_ = {'asyncio': asyncio, 'a': 0, 'arange': arange}
                async_f = FunctionType(co, globals_)
                asyncio.run(async_f())
                self.assertEqual(globals_['a'], 1)

                # test we can await-eval,
                globals_ = {'asyncio': asyncio, 'a': 0, 'arange': arange}
                asyncio.run(eval(co, globals_))
                self.assertEqual(globals_['a'], 1)
        mwishowe:
            asyncio.set_event_loop_policy(policy)

    eleza test_compile_async_generator(self):
        """
        With the PyCF_ALLOW_TOP_LEVEL_AWAIT flag added kwenye 3.8, we want to
        make sure AsyncGenerators are still properly sio marked ukijumuisha the
        CO_COROUTINE flag.
        """
        code = dedent("""async eleza ticker():
                kila i kwenye range(10):
                    tuma i
                    await asyncio.sleep(0)""")

        co = compile(code, '?', 'exec', flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
        glob = {}
        exec(co, glob)
        self.assertEqual(type(glob['ticker']()), AsyncGeneratorType)

    eleza test_delattr(self):
        sys.spam = 1
        delattr(sys, 'spam')
        self.assertRaises(TypeError, delattr)

    eleza test_dir(self):
        # dir(wrong number of arguments)
        self.assertRaises(TypeError, dir, 42, 42)

        # dir() - local scope
        local_var = 1
        self.assertIn('local_var', dir())

        # dir(module)
        self.assertIn('exit', dir(sys))

        # dir(module_with_invalid__dict__)
        kundi Foo(types.ModuleType):
            __dict__ = 8
        f = Foo("foo")
        self.assertRaises(TypeError, dir, f)

        # dir(type)
        self.assertIn("strip", dir(str))
        self.assertNotIn("__mro__", dir(str))

        # dir(obj)
        kundi Foo(object):
            eleza __init__(self):
                self.x = 7
                self.y = 8
                self.z = 9
        f = Foo()
        self.assertIn("y", dir(f))

        # dir(obj_no__dict__)
        kundi Foo(object):
            __slots__ = []
        f = Foo()
        self.assertIn("__repr__", dir(f))

        # dir(obj_no__class__with__dict__)
        # (an ugly trick to cause getattr(f, "__class__") to fail)
        kundi Foo(object):
            __slots__ = ["__class__", "__dict__"]
            eleza __init__(self):
                self.bar = "wow"
        f = Foo()
        self.assertNotIn("__repr__", dir(f))
        self.assertIn("bar", dir(f))

        # dir(obj_using __dir__)
        kundi Foo(object):
            eleza __dir__(self):
                rudisha ["kan", "ga", "roo"]
        f = Foo()
        self.assertKweli(dir(f) == ["ga", "kan", "roo"])

        # dir(obj__dir__tuple)
        kundi Foo(object):
            eleza __dir__(self):
                rudisha ("b", "c", "a")
        res = dir(Foo())
        self.assertIsInstance(res, list)
        self.assertKweli(res == ["a", "b", "c"])

        # dir(obj__dir__not_sequence)
        kundi Foo(object):
            eleza __dir__(self):
                rudisha 7
        f = Foo()
        self.assertRaises(TypeError, dir, f)

        # dir(traceback)
        jaribu:
            ashiria IndexError
        tatizo:
            self.assertEqual(len(dir(sys.exc_info()[2])), 4)

        # test that object has a __dir__()
        self.assertEqual(sorted([].__dir__()), dir([]))

    eleza test_divmod(self):
        self.assertEqual(divmod(12, 7), (1, 5))
        self.assertEqual(divmod(-12, 7), (-2, 2))
        self.assertEqual(divmod(12, -7), (-2, -2))
        self.assertEqual(divmod(-12, -7), (1, -5))

        self.assertEqual(divmod(-sys.maxsize-1, -1), (sys.maxsize+1, 0))

        kila num, denom, exp_result kwenye [ (3.25, 1.0, (3.0, 0.25)),
                                        (-3.25, 1.0, (-4.0, 0.75)),
                                        (3.25, -1.0, (-4.0, -0.75)),
                                        (-3.25, -1.0, (3.0, -0.25))]:
            result = divmod(num, denom)
            self.assertAlmostEqual(result[0], exp_result[0])
            self.assertAlmostEqual(result[1], exp_result[1])

        self.assertRaises(TypeError, divmod)

    eleza test_eval(self):
        self.assertEqual(eval('1+1'), 2)
        self.assertEqual(eval(' 1+1\n'), 2)
        globals = {'a': 1, 'b': 2}
        locals = {'b': 200, 'c': 300}
        self.assertEqual(eval('a', globals) , 1)
        self.assertEqual(eval('a', globals, locals), 1)
        self.assertEqual(eval('b', globals, locals), 200)
        self.assertEqual(eval('c', globals, locals), 300)
        globals = {'a': 1, 'b': 2}
        locals = {'b': 200, 'c': 300}
        bom = b'\xef\xbb\xbf'
        self.assertEqual(eval(bom + b'a', globals, locals), 1)
        self.assertEqual(eval('"\xe5"', globals), "\xe5")
        self.assertRaises(TypeError, eval)
        self.assertRaises(TypeError, eval, ())
        self.assertRaises(SyntaxError, eval, bom[:2] + b'a')

        kundi X:
            eleza __getitem__(self, key):
                ashiria ValueError
        self.assertRaises(ValueError, eval, "foo", {}, X())

    eleza test_general_eval(self):
        # Tests that general mappings can be used kila the locals argument

        kundi M:
            "Test mapping interface versus possible calls kutoka eval()."
            eleza __getitem__(self, key):
                ikiwa key == 'a':
                    rudisha 12
                ashiria KeyError
            eleza keys(self):
                rudisha list('xyz')

        m = M()
        g = globals()
        self.assertEqual(eval('a', g, m), 12)
        self.assertRaises(NameError, eval, 'b', g, m)
        self.assertEqual(eval('dir()', g, m), list('xyz'))
        self.assertEqual(eval('globals()', g, m), g)
        self.assertEqual(eval('locals()', g, m), m)
        self.assertRaises(TypeError, eval, 'a', m)
        kundi A:
            "Non-mapping"
            pita
        m = A()
        self.assertRaises(TypeError, eval, 'a', g, m)

        # Verify that dict subclasses work kama well
        kundi D(dict):
            eleza __getitem__(self, key):
                ikiwa key == 'a':
                    rudisha 12
                rudisha dict.__getitem__(self, key)
            eleza keys(self):
                rudisha list('xyz')

        d = D()
        self.assertEqual(eval('a', g, d), 12)
        self.assertRaises(NameError, eval, 'b', g, d)
        self.assertEqual(eval('dir()', g, d), list('xyz'))
        self.assertEqual(eval('globals()', g, d), g)
        self.assertEqual(eval('locals()', g, d), d)

        # Verify locals stores (used by list comps)
        eval('[locals() kila i kwenye (2,3)]', g, d)
        eval('[locals() kila i kwenye (2,3)]', g, collections.UserDict())

        kundi SpreadSheet:
            "Sample application showing nested, calculated lookups."
            _cells = {}
            eleza __setitem__(self, key, formula):
                self._cells[key] = formula
            eleza __getitem__(self, key):
                rudisha eval(self._cells[key], globals(), self)

        ss = SpreadSheet()
        ss['a1'] = '5'
        ss['a2'] = 'a1*6'
        ss['a3'] = 'a2*7'
        self.assertEqual(ss['a3'], 210)

        # Verify that dir() catches a non-list returned by eval
        # SF bug #1004669
        kundi C:
            eleza __getitem__(self, item):
                ashiria KeyError(item)
            eleza keys(self):
                rudisha 1 # used to be 'a' but that's no longer an error
        self.assertRaises(TypeError, eval, 'dir()', globals(), C())

    eleza test_exec(self):
        g = {}
        exec('z = 1', g)
        ikiwa '__builtins__' kwenye g:
            toa g['__builtins__']
        self.assertEqual(g, {'z': 1})

        exec('z = 1+1', g)
        ikiwa '__builtins__' kwenye g:
            toa g['__builtins__']
        self.assertEqual(g, {'z': 2})
        g = {}
        l = {}

        ukijumuisha check_warnings():
            warnings.filterwarnings("ignore", "global statement",
                    module="<string>")
            exec('global a; a = 1; b = 2', g, l)
        ikiwa '__builtins__' kwenye g:
            toa g['__builtins__']
        ikiwa '__builtins__' kwenye l:
            toa l['__builtins__']
        self.assertEqual((g, l), ({'a': 1}, {'b': 2}))

    eleza test_exec_globals(self):
        code = compile("andika('Hello World!')", "", "exec")
        # no builtin function
        self.assertRaisesRegex(NameError, "name 'print' ni sio defined",
                               exec, code, {'__builtins__': {}})
        # __builtins__ must be a mapping type
        self.assertRaises(TypeError,
                          exec, code, {'__builtins__': 123})

        # no __build_class__ function
        code = compile("kundi A: pita", "", "exec")
        self.assertRaisesRegex(NameError, "__build_class__ sio found",
                               exec, code, {'__builtins__': {}})

        kundi frozendict_error(Exception):
            pita

        kundi frozendict(dict):
            eleza __setitem__(self, key, value):
                ashiria frozendict_error("frozendict ni readonly")

        # read-only builtins
        ikiwa isinstance(__builtins__, types.ModuleType):
            frozen_builtins = frozendict(__builtins__.__dict__)
        isipokua:
            frozen_builtins = frozendict(__builtins__)
        code = compile("__builtins__['superglobal']=2; andika(superglobal)", "test", "exec")
        self.assertRaises(frozendict_error,
                          exec, code, {'__builtins__': frozen_builtins})

        # read-only globals
        namespace = frozendict({})
        code = compile("x=1", "test", "exec")
        self.assertRaises(frozendict_error,
                          exec, code, namespace)

    eleza test_exec_redirected(self):
        savestdout = sys.stdout
        sys.stdout = Tupu # Whatever that cansio flush()
        jaribu:
            # Used to ashiria SystemError('error rudisha without exception set')
            exec('a')
        tatizo NameError:
            pita
        mwishowe:
            sys.stdout = savestdout

    eleza test_filter(self):
        self.assertEqual(list(filter(lambda c: 'a' <= c <= 'z', 'Hello World')), list('elloorld'))
        self.assertEqual(list(filter(Tupu, [1, 'hello', [], [3], '', Tupu, 9, 0])), [1, 'hello', [3], 9])
        self.assertEqual(list(filter(lambda x: x > 0, [1, -3, 9, 0, 2])), [1, 9, 2])
        self.assertEqual(list(filter(Tupu, Squares(10))), [1, 4, 9, 16, 25, 36, 49, 64, 81])
        self.assertEqual(list(filter(lambda x: x%2, Squares(10))), [1, 9, 25, 49, 81])
        eleza identity(item):
            rudisha 1
        filter(identity, Squares(5))
        self.assertRaises(TypeError, filter)
        kundi BadSeq(object):
            eleza __getitem__(self, index):
                ikiwa index<4:
                    rudisha 42
                ashiria ValueError
        self.assertRaises(ValueError, list, filter(lambda x: x, BadSeq()))
        eleza badfunc():
            pita
        self.assertRaises(TypeError, list, filter(badfunc, range(5)))

        # test bltinmodule.c::filtertuple()
        self.assertEqual(list(filter(Tupu, (1, 2))), [1, 2])
        self.assertEqual(list(filter(lambda x: x>=3, (1, 2, 3, 4))), [3, 4])
        self.assertRaises(TypeError, list, filter(42, (1, 2)))

    eleza test_filter_pickle(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            f1 = filter(filter_char, "abcdeabcde")
            f2 = filter(filter_char, "abcdeabcde")
            self.check_iter_pickle(f1, list(f2), proto)

    eleza test_getattr(self):
        self.assertKweli(getattr(sys, 'stdout') ni sys.stdout)
        self.assertRaises(TypeError, getattr, sys, 1)
        self.assertRaises(TypeError, getattr, sys, 1, "foo")
        self.assertRaises(TypeError, getattr)
        self.assertRaises(AttributeError, getattr, sys, chr(sys.maxunicode))
        # unicode surrogates are sio encodable to the default encoding (utf8)
        self.assertRaises(AttributeError, getattr, 1, "\uDAD1\uD51E")

    eleza test_hasattr(self):
        self.assertKweli(hasattr(sys, 'stdout'))
        self.assertRaises(TypeError, hasattr, sys, 1)
        self.assertRaises(TypeError, hasattr)
        self.assertEqual(Uongo, hasattr(sys, chr(sys.maxunicode)))

        # Check that hasattr propagates all exceptions outside of
        # AttributeError.
        kundi A:
            eleza __getattr__(self, what):
                ashiria SystemExit
        self.assertRaises(SystemExit, hasattr, A(), "b")
        kundi B:
            eleza __getattr__(self, what):
                ashiria ValueError
        self.assertRaises(ValueError, hasattr, B(), "b")

    eleza test_hash(self):
        hash(Tupu)
        self.assertEqual(hash(1), hash(1))
        self.assertEqual(hash(1), hash(1.0))
        hash('spam')
        self.assertEqual(hash('spam'), hash(b'spam'))
        hash((0,1,2,3))
        eleza f(): pita
        self.assertRaises(TypeError, hash, [])
        self.assertRaises(TypeError, hash, {})
        # Bug 1536021: Allow hash to rudisha long objects
        kundi X:
            eleza __hash__(self):
                rudisha 2**100
        self.assertEqual(type(hash(X())), int)
        kundi Z(int):
            eleza __hash__(self):
                rudisha self
        self.assertEqual(hash(Z(42)), hash(42))

    eleza test_hex(self):
        self.assertEqual(hex(16), '0x10')
        self.assertEqual(hex(-16), '-0x10')
        self.assertRaises(TypeError, hex, {})

    eleza test_id(self):
        id(Tupu)
        id(1)
        id(1.0)
        id('spam')
        id((0,1,2,3))
        id([0,1,2,3])
        id({'spam': 1, 'eggs': 2, 'ham': 3})

    # Test uliza() later, alphabetized kama ikiwa it were raw_input

    eleza test_iter(self):
        self.assertRaises(TypeError, iter)
        self.assertRaises(TypeError, iter, 42, 42)
        lists = [("1", "2"), ["1", "2"], "12"]
        kila l kwenye lists:
            i = iter(l)
            self.assertEqual(next(i), '1')
            self.assertEqual(next(i), '2')
            self.assertRaises(StopIteration, next, i)

    eleza test_isinstance(self):
        kundi C:
            pita
        kundi D(C):
            pita
        kundi E:
            pita
        c = C()
        d = D()
        e = E()
        self.assertKweli(isinstance(c, C))
        self.assertKweli(isinstance(d, C))
        self.assertKweli(sio isinstance(e, C))
        self.assertKweli(sio isinstance(c, D))
        self.assertKweli(sio isinstance('foo', E))
        self.assertRaises(TypeError, isinstance, E, 'foo')
        self.assertRaises(TypeError, isinstance)

    eleza test_issubclass(self):
        kundi C:
            pita
        kundi D(C):
            pita
        kundi E:
            pita
        c = C()
        d = D()
        e = E()
        self.assertKweli(issubclass(D, C))
        self.assertKweli(issubclass(C, C))
        self.assertKweli(sio issubclass(C, D))
        self.assertRaises(TypeError, issubclass, 'foo', E)
        self.assertRaises(TypeError, issubclass, E, 'foo')
        self.assertRaises(TypeError, issubclass)

    eleza test_len(self):
        self.assertEqual(len('123'), 3)
        self.assertEqual(len(()), 0)
        self.assertEqual(len((1, 2, 3, 4)), 4)
        self.assertEqual(len([1, 2, 3, 4]), 4)
        self.assertEqual(len({}), 0)
        self.assertEqual(len({'a':1, 'b': 2}), 2)
        kundi BadSeq:
            eleza __len__(self):
                ashiria ValueError
        self.assertRaises(ValueError, len, BadSeq())
        kundi InvalidLen:
            eleza __len__(self):
                rudisha Tupu
        self.assertRaises(TypeError, len, InvalidLen())
        kundi FloatLen:
            eleza __len__(self):
                rudisha 4.5
        self.assertRaises(TypeError, len, FloatLen())
        kundi NegativeLen:
            eleza __len__(self):
                rudisha -10
        self.assertRaises(ValueError, len, NegativeLen())
        kundi HugeLen:
            eleza __len__(self):
                rudisha sys.maxsize + 1
        self.assertRaises(OverflowError, len, HugeLen())
        kundi HugeNegativeLen:
            eleza __len__(self):
                rudisha -sys.maxsize-10
        self.assertRaises(ValueError, len, HugeNegativeLen())
        kundi NoLenMethod(object): pita
        self.assertRaises(TypeError, len, NoLenMethod())

    eleza test_map(self):
        self.assertEqual(
            list(map(lambda x: x*x, range(1,4))),
            [1, 4, 9]
        )
        jaribu:
            kutoka math agiza sqrt
        tatizo ImportError:
            eleza sqrt(x):
                rudisha pow(x, 0.5)
        self.assertEqual(
            list(map(lambda x: list(map(sqrt, x)), [[16, 4], [81, 9]])),
            [[4.0, 2.0], [9.0, 3.0]]
        )
        self.assertEqual(
            list(map(lambda x, y: x+y, [1,3,2], [9,1,4])),
            [10, 4, 6]
        )

        eleza plus(*v):
            accu = 0
            kila i kwenye v: accu = accu + i
            rudisha accu
        self.assertEqual(
            list(map(plus, [1, 3, 7])),
            [1, 3, 7]
        )
        self.assertEqual(
            list(map(plus, [1, 3, 7], [4, 9, 2])),
            [1+4, 3+9, 7+2]
        )
        self.assertEqual(
            list(map(plus, [1, 3, 7], [4, 9, 2], [1, 1, 0])),
            [1+4+1, 3+9+1, 7+2+0]
        )
        self.assertEqual(
            list(map(int, Squares(10))),
            [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
        )
        eleza Max(a, b):
            ikiwa a ni Tupu:
                rudisha b
            ikiwa b ni Tupu:
                rudisha a
            rudisha max(a, b)
        self.assertEqual(
            list(map(Max, Squares(3), Squares(2))),
            [0, 1]
        )
        self.assertRaises(TypeError, map)
        self.assertRaises(TypeError, map, lambda x: x, 42)
        kundi BadSeq:
            eleza __iter__(self):
                ashiria ValueError
                tuma Tupu
        self.assertRaises(ValueError, list, map(lambda x: x, BadSeq()))
        eleza badfunc(x):
            ashiria RuntimeError
        self.assertRaises(RuntimeError, list, map(badfunc, range(5)))

    eleza test_map_pickle(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            m1 = map(map_char, "Is this the real life?")
            m2 = map(map_char, "Is this the real life?")
            self.check_iter_pickle(m1, list(m2), proto)

    eleza test_max(self):
        self.assertEqual(max('123123'), '3')
        self.assertEqual(max(1, 2, 3), 3)
        self.assertEqual(max((1, 2, 3, 1, 2, 3)), 3)
        self.assertEqual(max([1, 2, 3, 1, 2, 3]), 3)

        self.assertEqual(max(1, 2, 3.0), 3.0)
        self.assertEqual(max(1, 2.0, 3), 3)
        self.assertEqual(max(1.0, 2, 3), 3)

        self.assertRaises(TypeError, max)
        self.assertRaises(TypeError, max, 42)
        self.assertRaises(ValueError, max, ())
        kundi BadSeq:
            eleza __getitem__(self, index):
                ashiria ValueError
        self.assertRaises(ValueError, max, BadSeq())

        kila stmt kwenye (
            "max(key=int)",                 # no args
            "max(default=Tupu)",
            "max(1, 2, default=Tupu)",      # require container kila default
            "max(default=Tupu, key=int)",
            "max(1, key=int)",              # single arg sio iterable
            "max(1, 2, keystone=int)",      # wrong keyword
            "max(1, 2, key=int, abc=int)",  # two many keywords
            "max(1, 2, key=1)",             # keyfunc ni sio callable
            ):
            jaribu:
                exec(stmt, globals())
            tatizo TypeError:
                pita
            isipokua:
                self.fail(stmt)

        self.assertEqual(max((1,), key=neg), 1)     # one elem iterable
        self.assertEqual(max((1,2), key=neg), 1)    # two elem iterable
        self.assertEqual(max(1, 2, key=neg), 1)     # two elems

        self.assertEqual(max((), default=Tupu), Tupu)    # zero elem iterable
        self.assertEqual(max((1,), default=Tupu), 1)     # one elem iterable
        self.assertEqual(max((1,2), default=Tupu), 2)    # two elem iterable

        self.assertEqual(max((), default=1, key=neg), 1)
        self.assertEqual(max((1, 2), default=3, key=neg), 1)

        self.assertEqual(max((1, 2), key=Tupu), 2)

        data = [random.randrange(200) kila i kwenye range(100)]
        keys = dict((elem, random.randrange(50)) kila elem kwenye data)
        f = keys.__getitem__
        self.assertEqual(max(data, key=f),
                         sorted(reversed(data), key=f)[-1])

    eleza test_min(self):
        self.assertEqual(min('123123'), '1')
        self.assertEqual(min(1, 2, 3), 1)
        self.assertEqual(min((1, 2, 3, 1, 2, 3)), 1)
        self.assertEqual(min([1, 2, 3, 1, 2, 3]), 1)

        self.assertEqual(min(1, 2, 3.0), 1)
        self.assertEqual(min(1, 2.0, 3), 1)
        self.assertEqual(min(1.0, 2, 3), 1.0)

        self.assertRaises(TypeError, min)
        self.assertRaises(TypeError, min, 42)
        self.assertRaises(ValueError, min, ())
        kundi BadSeq:
            eleza __getitem__(self, index):
                ashiria ValueError
        self.assertRaises(ValueError, min, BadSeq())

        kila stmt kwenye (
            "min(key=int)",                 # no args
            "min(default=Tupu)",
            "min(1, 2, default=Tupu)",      # require container kila default
            "min(default=Tupu, key=int)",
            "min(1, key=int)",              # single arg sio iterable
            "min(1, 2, keystone=int)",      # wrong keyword
            "min(1, 2, key=int, abc=int)",  # two many keywords
            "min(1, 2, key=1)",             # keyfunc ni sio callable
            ):
            jaribu:
                exec(stmt, globals())
            tatizo TypeError:
                pita
            isipokua:
                self.fail(stmt)

        self.assertEqual(min((1,), key=neg), 1)     # one elem iterable
        self.assertEqual(min((1,2), key=neg), 2)    # two elem iterable
        self.assertEqual(min(1, 2, key=neg), 2)     # two elems

        self.assertEqual(min((), default=Tupu), Tupu)    # zero elem iterable
        self.assertEqual(min((1,), default=Tupu), 1)     # one elem iterable
        self.assertEqual(min((1,2), default=Tupu), 1)    # two elem iterable

        self.assertEqual(min((), default=1, key=neg), 1)
        self.assertEqual(min((1, 2), default=1, key=neg), 2)

        self.assertEqual(min((1, 2), key=Tupu), 1)

        data = [random.randrange(200) kila i kwenye range(100)]
        keys = dict((elem, random.randrange(50)) kila elem kwenye data)
        f = keys.__getitem__
        self.assertEqual(min(data, key=f),
                         sorted(data, key=f)[0])

    eleza test_next(self):
        it = iter(range(2))
        self.assertEqual(next(it), 0)
        self.assertEqual(next(it), 1)
        self.assertRaises(StopIteration, next, it)
        self.assertRaises(StopIteration, next, it)
        self.assertEqual(next(it, 42), 42)

        kundi Iter(object):
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                ashiria StopIteration

        it = iter(Iter())
        self.assertEqual(next(it, 42), 42)
        self.assertRaises(StopIteration, next, it)

        eleza gen():
            tuma 1
            rudisha

        it = gen()
        self.assertEqual(next(it), 1)
        self.assertRaises(StopIteration, next, it)
        self.assertEqual(next(it, 42), 42)

    eleza test_oct(self):
        self.assertEqual(oct(100), '0o144')
        self.assertEqual(oct(-100), '-0o144')
        self.assertRaises(TypeError, oct, ())

    eleza write_testfile(self):
        # NB the first 4 lines are also used to test input, below
        fp = open(TESTFN, 'w')
        self.addCleanup(unlink, TESTFN)
        ukijumuisha fp:
            fp.write('1+1\n')
            fp.write('The quick brown fox jumps over the lazy dog')
            fp.write('.\n')
            fp.write('Dear John\n')
            fp.write('XXX'*100)
            fp.write('YYY'*100)

    eleza test_open(self):
        self.write_testfile()
        fp = open(TESTFN, 'r')
        ukijumuisha fp:
            self.assertEqual(fp.readline(4), '1+1\n')
            self.assertEqual(fp.readline(), 'The quick brown fox jumps over the lazy dog.\n')
            self.assertEqual(fp.readline(4), 'Dear')
            self.assertEqual(fp.readline(100), ' John\n')
            self.assertEqual(fp.read(300), 'XXX'*100)
            self.assertEqual(fp.read(1000), 'YYY'*100)

        # embedded null bytes na characters
        self.assertRaises(ValueError, open, 'a\x00b')
        self.assertRaises(ValueError, open, b'a\x00b')

    @unittest.skipIf(sys.flags.utf8_mode, "utf-8 mode ni enabled")
    eleza test_open_default_encoding(self):
        old_environ = dict(os.environ)
        jaribu:
            # try to get a user preferred encoding different than the current
            # locale encoding to check that open() uses the current locale
            # encoding na sio the user preferred encoding
            kila key kwenye ('LC_ALL', 'LANG', 'LC_CTYPE'):
                ikiwa key kwenye os.environ:
                    toa os.environ[key]

            self.write_testfile()
            current_locale_encoding = locale.getpreferredencoding(Uongo)
            fp = open(TESTFN, 'w')
            ukijumuisha fp:
                self.assertEqual(fp.encoding, current_locale_encoding)
        mwishowe:
            os.environ.clear()
            os.environ.update(old_environ)

    eleza test_open_non_inheritable(self):
        fileobj = open(__file__)
        ukijumuisha fileobj:
            self.assertUongo(os.get_inheritable(fileobj.fileno()))

    eleza test_ord(self):
        self.assertEqual(ord(' '), 32)
        self.assertEqual(ord('A'), 65)
        self.assertEqual(ord('a'), 97)
        self.assertEqual(ord('\x80'), 128)
        self.assertEqual(ord('\xff'), 255)

        self.assertEqual(ord(b' '), 32)
        self.assertEqual(ord(b'A'), 65)
        self.assertEqual(ord(b'a'), 97)
        self.assertEqual(ord(b'\x80'), 128)
        self.assertEqual(ord(b'\xff'), 255)

        self.assertEqual(ord(chr(sys.maxunicode)), sys.maxunicode)
        self.assertRaises(TypeError, ord, 42)

        self.assertEqual(ord(chr(0x10FFFF)), 0x10FFFF)
        self.assertEqual(ord("\U0000FFFF"), 0x0000FFFF)
        self.assertEqual(ord("\U00010000"), 0x00010000)
        self.assertEqual(ord("\U00010001"), 0x00010001)
        self.assertEqual(ord("\U000FFFFE"), 0x000FFFFE)
        self.assertEqual(ord("\U000FFFFF"), 0x000FFFFF)
        self.assertEqual(ord("\U00100000"), 0x00100000)
        self.assertEqual(ord("\U00100001"), 0x00100001)
        self.assertEqual(ord("\U0010FFFE"), 0x0010FFFE)
        self.assertEqual(ord("\U0010FFFF"), 0x0010FFFF)

    eleza test_pow(self):
        self.assertEqual(pow(0,0), 1)
        self.assertEqual(pow(0,1), 0)
        self.assertEqual(pow(1,0), 1)
        self.assertEqual(pow(1,1), 1)

        self.assertEqual(pow(2,0), 1)
        self.assertEqual(pow(2,10), 1024)
        self.assertEqual(pow(2,20), 1024*1024)
        self.assertEqual(pow(2,30), 1024*1024*1024)

        self.assertEqual(pow(-2,0), 1)
        self.assertEqual(pow(-2,1), -2)
        self.assertEqual(pow(-2,2), 4)
        self.assertEqual(pow(-2,3), -8)

        self.assertAlmostEqual(pow(0.,0), 1.)
        self.assertAlmostEqual(pow(0.,1), 0.)
        self.assertAlmostEqual(pow(1.,0), 1.)
        self.assertAlmostEqual(pow(1.,1), 1.)

        self.assertAlmostEqual(pow(2.,0), 1.)
        self.assertAlmostEqual(pow(2.,10), 1024.)
        self.assertAlmostEqual(pow(2.,20), 1024.*1024.)
        self.assertAlmostEqual(pow(2.,30), 1024.*1024.*1024.)

        self.assertAlmostEqual(pow(-2.,0), 1.)
        self.assertAlmostEqual(pow(-2.,1), -2.)
        self.assertAlmostEqual(pow(-2.,2), 4.)
        self.assertAlmostEqual(pow(-2.,3), -8.)

        kila x kwenye 2, 2.0:
            kila y kwenye 10, 10.0:
                kila z kwenye 1000, 1000.0:
                    ikiwa isinstance(x, float) ama \
                       isinstance(y, float) ama \
                       isinstance(z, float):
                        self.assertRaises(TypeError, pow, x, y, z)
                    isipokua:
                        self.assertAlmostEqual(pow(x, y, z), 24.0)

        self.assertAlmostEqual(pow(-1, 0.5), 1j)
        self.assertAlmostEqual(pow(-1, 1/3), 0.5 + 0.8660254037844386j)

        # See test_pow kila additional tests kila three-argument pow.
        self.assertEqual(pow(-1, -2, 3), 1)
        self.assertRaises(ValueError, pow, 1, 2, 0)

        self.assertRaises(TypeError, pow)

        # Test pitaing kwenye arguments kama keywords.
        self.assertEqual(pow(0, exp=0), 1)
        self.assertEqual(pow(base=2, exp=4), 16)
        self.assertEqual(pow(base=5, exp=2, mod=14), 11)
        twopow = partial(pow, base=2)
        self.assertEqual(twopow(exp=5), 32)
        fifth_power = partial(pow, exp=5)
        self.assertEqual(fifth_power(2), 32)
        mod10 = partial(pow, mod=10)
        self.assertEqual(mod10(2, 6), 4)
        self.assertEqual(mod10(exp=6, base=2), 4)

    eleza test_uliza(self):
        self.write_testfile()
        fp = open(TESTFN, 'r')
        savestdin = sys.stdin
        savestdout = sys.stdout # Eats the echo
        jaribu:
            sys.stdin = fp
            sys.stdout = BitBucket()
            self.assertEqual(uliza(), "1+1")
            self.assertEqual(uliza(), 'The quick brown fox jumps over the lazy dog.')
            self.assertEqual(uliza('testing\n'), 'Dear John')

            # SF 1535165: don't segfault on closed stdin
            # sys.stdout must be a regular file kila triggering
            sys.stdout = savestdout
            sys.stdin.close()
            self.assertRaises(ValueError, input)

            sys.stdout = BitBucket()
            sys.stdin = io.StringIO("NULL\0")
            self.assertRaises(TypeError, input, 42, 42)
            sys.stdin = io.StringIO("    'whitespace'")
            self.assertEqual(uliza(), "    'whitespace'")
            sys.stdin = io.StringIO()
            self.assertRaises(EOFError, input)

            toa sys.stdout
            self.assertRaises(RuntimeError, input, 'prompt')
            toa sys.stdin
            self.assertRaises(RuntimeError, input, 'prompt')
        mwishowe:
            sys.stdin = savestdin
            sys.stdout = savestdout
            fp.close()

    # test_int(): see test_int.py kila tests of built-in function int().

    eleza test_repr(self):
        self.assertEqual(repr(''), '\'\'')
        self.assertEqual(repr(0), '0')
        self.assertEqual(repr(()), '()')
        self.assertEqual(repr([]), '[]')
        self.assertEqual(repr({}), '{}')
        a = []
        a.append(a)
        self.assertEqual(repr(a), '[[...]]')
        a = {}
        a[0] = a
        self.assertEqual(repr(a), '{0: {...}}')

    eleza test_round(self):
        self.assertEqual(round(0.0), 0.0)
        self.assertEqual(type(round(0.0)), int)
        self.assertEqual(round(1.0), 1.0)
        self.assertEqual(round(10.0), 10.0)
        self.assertEqual(round(1000000000.0), 1000000000.0)
        self.assertEqual(round(1e20), 1e20)

        self.assertEqual(round(-1.0), -1.0)
        self.assertEqual(round(-10.0), -10.0)
        self.assertEqual(round(-1000000000.0), -1000000000.0)
        self.assertEqual(round(-1e20), -1e20)

        self.assertEqual(round(0.1), 0.0)
        self.assertEqual(round(1.1), 1.0)
        self.assertEqual(round(10.1), 10.0)
        self.assertEqual(round(1000000000.1), 1000000000.0)

        self.assertEqual(round(-1.1), -1.0)
        self.assertEqual(round(-10.1), -10.0)
        self.assertEqual(round(-1000000000.1), -1000000000.0)

        self.assertEqual(round(0.9), 1.0)
        self.assertEqual(round(9.9), 10.0)
        self.assertEqual(round(999999999.9), 1000000000.0)

        self.assertEqual(round(-0.9), -1.0)
        self.assertEqual(round(-9.9), -10.0)
        self.assertEqual(round(-999999999.9), -1000000000.0)

        self.assertEqual(round(-8.0, -1), -10.0)
        self.assertEqual(type(round(-8.0, -1)), float)

        self.assertEqual(type(round(-8.0, 0)), float)
        self.assertEqual(type(round(-8.0, 1)), float)

        # Check even / odd rounding behaviour
        self.assertEqual(round(5.5), 6)
        self.assertEqual(round(6.5), 6)
        self.assertEqual(round(-5.5), -6)
        self.assertEqual(round(-6.5), -6)

        # Check behavior on ints
        self.assertEqual(round(0), 0)
        self.assertEqual(round(8), 8)
        self.assertEqual(round(-8), -8)
        self.assertEqual(type(round(0)), int)
        self.assertEqual(type(round(-8, -1)), int)
        self.assertEqual(type(round(-8, 0)), int)
        self.assertEqual(type(round(-8, 1)), int)

        # test new kwargs
        self.assertEqual(round(number=-8.0, ndigits=-1), -10.0)

        self.assertRaises(TypeError, round)

        # test generic rounding delegation kila reals
        kundi TestRound:
            eleza __round__(self):
                rudisha 23

        kundi TestNoRound:
            pita

        self.assertEqual(round(TestRound()), 23)

        self.assertRaises(TypeError, round, 1, 2, 3)
        self.assertRaises(TypeError, round, TestNoRound())

        t = TestNoRound()
        t.__round__ = lambda *args: args
        self.assertRaises(TypeError, round, t)
        self.assertRaises(TypeError, round, t, 0)

    # Some versions of glibc kila alpha have a bug that affects
    # float -> integer rounding (floor, ceil, rint, round) for
    # values kwenye the range [2**52, 2**53).  See:
    #
    #   http://sources.redhat.com/bugzilla/show_bug.cgi?id=5350
    #
    # We skip this test on Linux/alpha ikiwa it would fail.
    linux_alpha = (platform.system().startswith('Linux') na
                   platform.machine().startswith('alpha'))
    system_round_bug = round(5e15+1) != 5e15+1
    @unittest.skipIf(linux_alpha na system_round_bug,
                     "test will fail;  failure ni probably due to a "
                     "buggy system round function")
    eleza test_round_large(self):
        # Issue #1869: integral floats should remain unchanged
        self.assertEqual(round(5e15-1), 5e15-1)
        self.assertEqual(round(5e15), 5e15)
        self.assertEqual(round(5e15+1), 5e15+1)
        self.assertEqual(round(5e15+2), 5e15+2)
        self.assertEqual(round(5e15+3), 5e15+3)

    eleza test_bug_27936(self):
        # Verify that ndigits=Tupu means the same kama pitaing kwenye no argument
        kila x kwenye [1234,
                  1234.56,
                  decimal.Decimal('1234.56'),
                  fractions.Fraction(123456, 100)]:
            self.assertEqual(round(x, Tupu), round(x))
            self.assertEqual(type(round(x, Tupu)), type(round(x)))

    eleza test_setattr(self):
        setattr(sys, 'spam', 1)
        self.assertEqual(sys.spam, 1)
        self.assertRaises(TypeError, setattr, sys, 1, 'spam')
        self.assertRaises(TypeError, setattr)

    # test_str(): see test_unicode.py na test_bytes.py kila str() tests.

    eleza test_sum(self):
        self.assertEqual(sum([]), 0)
        self.assertEqual(sum(list(range(2,8))), 27)
        self.assertEqual(sum(iter(list(range(2,8)))), 27)
        self.assertEqual(sum(Squares(10)), 285)
        self.assertEqual(sum(iter(Squares(10))), 285)
        self.assertEqual(sum([[1], [2], [3]], []), [1, 2, 3])

        self.assertEqual(sum(range(10), 1000), 1045)
        self.assertEqual(sum(range(10), start=1000), 1045)

        self.assertRaises(TypeError, sum)
        self.assertRaises(TypeError, sum, 42)
        self.assertRaises(TypeError, sum, ['a', 'b', 'c'])
        self.assertRaises(TypeError, sum, ['a', 'b', 'c'], '')
        self.assertRaises(TypeError, sum, [b'a', b'c'], b'')
        values = [bytearray(b'a'), bytearray(b'b')]
        self.assertRaises(TypeError, sum, values, bytearray(b''))
        self.assertRaises(TypeError, sum, [[1], [2], [3]])
        self.assertRaises(TypeError, sum, [{2:3}])
        self.assertRaises(TypeError, sum, [{2:3}]*2, {2:3})

        kundi BadSeq:
            eleza __getitem__(self, index):
                ashiria ValueError
        self.assertRaises(ValueError, sum, BadSeq())

        empty = []
        sum(([x] kila x kwenye range(10)), empty)
        self.assertEqual(empty, [])

    eleza test_type(self):
        self.assertEqual(type(''),  type('123'))
        self.assertNotEqual(type(''), type(()))

    # We don't want self kwenye vars(), so these are static methods

    @staticmethod
    eleza get_vars_f0():
        rudisha vars()

    @staticmethod
    eleza get_vars_f2():
        BuiltinTest.get_vars_f0()
        a = 1
        b = 2
        rudisha vars()

    kundi C_get_vars(object):
        eleza getDict(self):
            rudisha {'a':2}
        __dict__ = property(fget=getDict)

    eleza test_vars(self):
        self.assertEqual(set(vars()), set(dir()))
        self.assertEqual(set(vars(sys)), set(dir(sys)))
        self.assertEqual(self.get_vars_f0(), {})
        self.assertEqual(self.get_vars_f2(), {'a': 1, 'b': 2})
        self.assertRaises(TypeError, vars, 42, 42)
        self.assertRaises(TypeError, vars, 42)
        self.assertEqual(vars(self.C_get_vars()), {'a':2})

    eleza test_zip(self):
        a = (1, 2, 3)
        b = (4, 5, 6)
        t = [(1, 4), (2, 5), (3, 6)]
        self.assertEqual(list(zip(a, b)), t)
        b = [4, 5, 6]
        self.assertEqual(list(zip(a, b)), t)
        b = (4, 5, 6, 7)
        self.assertEqual(list(zip(a, b)), t)
        kundi I:
            eleza __getitem__(self, i):
                ikiwa i < 0 ama i > 2: ashiria IndexError
                rudisha i + 4
        self.assertEqual(list(zip(a, I())), t)
        self.assertEqual(list(zip()), [])
        self.assertEqual(list(zip(*[])), [])
        self.assertRaises(TypeError, zip, Tupu)
        kundi G:
            pita
        self.assertRaises(TypeError, zip, a, G())
        self.assertRaises(RuntimeError, zip, a, TestFailingIter())

        # Make sure zip doesn't try to allocate a billion elements kila the
        # result list when one of its arguments doesn't say how long it is.
        # A MemoryError ni the most likely failure mode.
        kundi SequenceWithoutALength:
            eleza __getitem__(self, i):
                ikiwa i == 5:
                    ashiria IndexError
                isipokua:
                    rudisha i
        self.assertEqual(
            list(zip(SequenceWithoutALength(), range(2**30))),
            list(enumerate(range(5)))
        )

        kundi BadSeq:
            eleza __getitem__(self, i):
                ikiwa i == 5:
                    ashiria ValueError
                isipokua:
                    rudisha i
        self.assertRaises(ValueError, list, zip(BadSeq(), BadSeq()))

    eleza test_zip_pickle(self):
        a = (1, 2, 3)
        b = (4, 5, 6)
        t = [(1, 4), (2, 5), (3, 6)]
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            z1 = zip(a, b)
            self.check_iter_pickle(z1, t, proto)

    eleza test_zip_bad_iterable(self):
        exception = TypeError()

        kundi BadIterable:
            eleza __iter__(self):
                ashiria exception

        ukijumuisha self.assertRaises(TypeError) kama cm:
            zip(BadIterable())

        self.assertIs(cm.exception, exception)

    eleza test_format(self):
        # Test the basic machinery of the format() builtin.  Don't test
        #  the specifics of the various formatters
        self.assertEqual(format(3, ''), '3')

        # Returns some classes to use kila various tests.  There's
        #  an old-style version, na a new-style version
        eleza classes_new():
            kundi A(object):
                eleza __init__(self, x):
                    self.x = x
                eleza __format__(self, format_spec):
                    rudisha str(self.x) + format_spec
            kundi DerivedFromA(A):
                pita

            kundi Simple(object): pita
            kundi DerivedFromSimple(Simple):
                eleza __init__(self, x):
                    self.x = x
                eleza __format__(self, format_spec):
                    rudisha str(self.x) + format_spec
            kundi DerivedFromSimple2(DerivedFromSimple): pita
            rudisha A, DerivedFromA, DerivedFromSimple, DerivedFromSimple2

        eleza class_test(A, DerivedFromA, DerivedFromSimple, DerivedFromSimple2):
            self.assertEqual(format(A(3), 'spec'), '3spec')
            self.assertEqual(format(DerivedFromA(4), 'spec'), '4spec')
            self.assertEqual(format(DerivedFromSimple(5), 'abc'), '5abc')
            self.assertEqual(format(DerivedFromSimple2(10), 'abcdef'),
                             '10abcdef')

        class_test(*classes_new())

        eleza empty_format_spec(value):
            # test that:
            #  format(x, '') == str(x)
            #  format(x) == str(x)
            self.assertEqual(format(value, ""), str(value))
            self.assertEqual(format(value), str(value))

        # kila builtin types, format(x, "") == str(x)
        empty_format_spec(17**13)
        empty_format_spec(1.0)
        empty_format_spec(3.1415e104)
        empty_format_spec(-3.1415e104)
        empty_format_spec(3.1415e-104)
        empty_format_spec(-3.1415e-104)
        empty_format_spec(object)
        empty_format_spec(Tupu)

        # TypeError because self.__format__ returns the wrong type
        kundi BadFormatResult:
            eleza __format__(self, format_spec):
                rudisha 1.0
        self.assertRaises(TypeError, format, BadFormatResult(), "")

        # TypeError because format_spec ni sio unicode ama str
        self.assertRaises(TypeError, format, object(), 4)
        self.assertRaises(TypeError, format, object(), object())

        # tests kila object.__format__ really belong elsewhere, but
        #  there's no good place to put them
        x = object().__format__('')
        self.assertKweli(x.startswith('<object object at'))

        # first argument to object.__format__ must be string
        self.assertRaises(TypeError, object().__format__, 3)
        self.assertRaises(TypeError, object().__format__, object())
        self.assertRaises(TypeError, object().__format__, Tupu)

        # --------------------------------------------------------------------
        # Issue #7994: object.__format__ ukijumuisha a non-empty format string is
        # disallowed
        kundi A:
            eleza __format__(self, fmt_str):
                rudisha format('', fmt_str)

        self.assertEqual(format(A()), '')
        self.assertEqual(format(A(), ''), '')
        self.assertEqual(format(A(), 's'), '')

        kundi B:
            pita

        kundi C(object):
            pita

        kila cls kwenye [object, B, C]:
            obj = cls()
            self.assertEqual(format(obj), str(obj))
            self.assertEqual(format(obj, ''), str(obj))
            ukijumuisha self.assertRaisesRegex(TypeError,
                                        r'\b%s\b' % re.escape(cls.__name__)):
                format(obj, 's')
        # --------------------------------------------------------------------

        # make sure we can take a subkundi of str kama a format spec
        kundi DerivedFromStr(str): pita
        self.assertEqual(format(0, DerivedFromStr('10')), '         0')

    eleza test_bin(self):
        self.assertEqual(bin(0), '0b0')
        self.assertEqual(bin(1), '0b1')
        self.assertEqual(bin(-1), '-0b1')
        self.assertEqual(bin(2**65), '0b1' + '0' * 65)
        self.assertEqual(bin(2**65-1), '0b' + '1' * 65)
        self.assertEqual(bin(-(2**65)), '-0b1' + '0' * 65)
        self.assertEqual(bin(-(2**65-1)), '-0b' + '1' * 65)

    eleza test_bytearray_translate(self):
        x = bytearray(b"abc")
        self.assertRaises(ValueError, x.translate, b"1", 1)
        self.assertRaises(TypeError, x.translate, b"1"*256, 1)

    eleza test_bytearray_extend_error(self):
        array = bytearray()
        bad_iter = map(int, "X")
        self.assertRaises(ValueError, array.extend, bad_iter)

    eleza test_construct_singletons(self):
        kila const kwenye Tupu, Ellipsis, NotImplemented:
            tp = type(const)
            self.assertIs(tp(), const)
            self.assertRaises(TypeError, tp, 1, 2)
            self.assertRaises(TypeError, tp, a=1, b=2)


kundi TestBreakpoint(unittest.TestCase):
    eleza setUp(self):
        # These tests require a clean slate environment.  For example, ikiwa the
        # test suite ni run ukijumuisha $PYTHONBREAKPOINT set to something else, it
        # will mess up these tests.  Similarly kila sys.komapointhook.
        # Cleaning the slate here means you can't use komapoint() to debug
        # these tests, but I think that's okay.  Just use pdb.set_trace() if
        # you must.
        self.resources = ExitStack()
        self.addCleanup(self.resources.close)
        self.env = self.resources.enter_context(EnvironmentVarGuard())
        toa self.env['PYTHONBREAKPOINT']
        self.resources.enter_context(
            swap_attr(sys, 'komapointhook', sys.__komapointhook__))

    eleza test_komapoint(self):
        ukijumuisha patch('pdb.set_trace') kama mock:
            komapoint()
        mock.assert_called_once()

    eleza test_komapoint_with_komapointhook_set(self):
        my_komapointhook = MagicMock()
        sys.komapointhook = my_komapointhook
        komapoint()
        my_komapointhook.assert_called_once_with()

    eleza test_komapoint_with_komapointhook_reset(self):
        my_komapointhook = MagicMock()
        sys.komapointhook = my_komapointhook
        komapoint()
        my_komapointhook.assert_called_once_with()
        # Reset the hook na it will sio be called again.
        sys.komapointhook = sys.__komapointhook__
        ukijumuisha patch('pdb.set_trace') kama mock:
            komapoint()
            mock.assert_called_once_with()
        my_komapointhook.assert_called_once_with()

    eleza test_komapoint_with_args_and_keywords(self):
        my_komapointhook = MagicMock()
        sys.komapointhook = my_komapointhook
        komapoint(1, 2, 3, four=4, five=5)
        my_komapointhook.assert_called_once_with(1, 2, 3, four=4, five=5)

    eleza test_komapoint_with_pitathru_error(self):
        eleza my_komapointhook():
            pita
        sys.komapointhook = my_komapointhook
        self.assertRaises(TypeError, komapoint, 1, 2, 3, four=4, five=5)

    @unittest.skipIf(sys.flags.ignore_environment, '-E was given')
    eleza test_envar_good_path_builtin(self):
        self.env['PYTHONBREAKPOINT'] = 'int'
        ukijumuisha patch('builtins.int') kama mock:
            komapoint('7')
            mock.assert_called_once_with('7')

    @unittest.skipIf(sys.flags.ignore_environment, '-E was given')
    eleza test_envar_good_path_other(self):
        self.env['PYTHONBREAKPOINT'] = 'sys.exit'
        ukijumuisha patch('sys.exit') kama mock:
            komapoint()
            mock.assert_called_once_with()

    @unittest.skipIf(sys.flags.ignore_environment, '-E was given')
    eleza test_envar_good_path_noop_0(self):
        self.env['PYTHONBREAKPOINT'] = '0'
        ukijumuisha patch('pdb.set_trace') kama mock:
            komapoint()
            mock.assert_not_called()

    eleza test_envar_good_path_empty_string(self):
        # PYTHONBREAKPOINT='' ni the same kama it sio being set.
        self.env['PYTHONBREAKPOINT'] = ''
        ukijumuisha patch('pdb.set_trace') kama mock:
            komapoint()
            mock.assert_called_once_with()

    @unittest.skipIf(sys.flags.ignore_environment, '-E was given')
    eleza test_envar_unimportable(self):
        kila envar kwenye (
                '.', '..', '.foo', 'foo.', '.int', 'int.',
                '.foo.bar', '..foo.bar', '/./',
                'nosuchbuiltin',
                'nosuchmodule.nosuchcallable',
                ):
            ukijumuisha self.subTest(envar=envar):
                self.env['PYTHONBREAKPOINT'] = envar
                mock = self.resources.enter_context(patch('pdb.set_trace'))
                w = self.resources.enter_context(check_warnings(quiet=Kweli))
                komapoint()
                self.assertEqual(
                    str(w.message),
                    f'Ignoring unimportable $PYTHONBREAKPOINT: "{envar}"')
                self.assertEqual(w.category, RuntimeWarning)
                mock.assert_not_called()

    eleza test_envar_ignored_when_hook_is_set(self):
        self.env['PYTHONBREAKPOINT'] = 'sys.exit'
        ukijumuisha patch('sys.exit') kama mock:
            sys.komapointhook = int
            komapoint()
            mock.assert_not_called()


@unittest.skipUnless(pty, "the pty na signal modules must be available")
kundi PtyTests(unittest.TestCase):
    """Tests that use a pseudo terminal to guarantee stdin na stdout are
    terminals kwenye the test environment"""

    eleza run_child(self, child, terminal_input):
        r, w = os.pipe()  # Pipe test results kutoka child back to parent
        jaribu:
            pid, fd = pty.fork()
        tatizo (OSError, AttributeError) kama e:
            os.close(r)
            os.close(w)
            self.skipTest("pty.fork() raised {}".format(e))
            raise
        ikiwa pid == 0:
            # Child
            jaribu:
                # Make sure we don't get stuck ikiwa there's a problem
                signal.alarm(2)
                os.close(r)
                ukijumuisha open(w, "w") kama wpipe:
                    child(wpipe)
            tatizo:
                traceback.print_exc()
            mwishowe:
                # We don't want to rudisha to unittest...
                os._exit(0)
        # Parent
        os.close(w)
        os.write(fd, terminal_input)
        # Get results kutoka the pipe
        ukijumuisha open(r, "r") kama rpipe:
            lines = []
            wakati Kweli:
                line = rpipe.readline().strip()
                ikiwa line == "":
                    # The other end was closed => the child exited
                    koma
                lines.append(line)
        # Check the result was got na corresponds to the user's terminal input
        ikiwa len(lines) != 2:
            # Something went wrong, try to get at stderr
            # Beware of Linux raising EIO when the slave ni closed
            child_output = bytearray()
            wakati Kweli:
                jaribu:
                    chunk = os.read(fd, 3000)
                tatizo OSError:  # Assume EIO
                    koma
                ikiwa sio chunk:
                    koma
                child_output.extend(chunk)
            os.close(fd)
            child_output = child_output.decode("ascii", "ignore")
            self.fail("got %d lines kwenye pipe but expected 2, child output was:\n%s"
                      % (len(lines), child_output))
        os.close(fd)

        # Wait until the child process completes
        os.waitpid(pid, 0)

        rudisha lines

    eleza check_input_tty(self, prompt, terminal_input, stdio_encoding=Tupu):
        ikiwa sio sys.stdin.isatty() ama sio sys.stdout.isatty():
            self.skipTest("stdin na stdout must be ttys")
        eleza child(wpipe):
            # Check the error handlers are accounted for
            ikiwa stdio_encoding:
                sys.stdin = io.TextIOWrapper(sys.stdin.detach(),
                                             encoding=stdio_encoding,
                                             errors='surrogateescape')
                sys.stdout = io.TextIOWrapper(sys.stdout.detach(),
                                              encoding=stdio_encoding,
                                              errors='replace')
            andika("tty =", sys.stdin.isatty() na sys.stdout.isatty(), file=wpipe)
            andika(ascii(uliza(prompt)), file=wpipe)
        lines = self.run_child(child, terminal_input + b"\r\n")
        # Check we did exercise the GNU readline path
        self.assertIn(lines[0], {'tty = Kweli', 'tty = Uongo'})
        ikiwa lines[0] != 'tty = Kweli':
            self.skipTest("standard IO kwenye should have been a tty")
        input_result = eval(lines[1])   # ascii() -> eval() roundtrip
        ikiwa stdio_encoding:
            expected = terminal_input.decode(stdio_encoding, 'surrogateescape')
        isipokua:
            expected = terminal_input.decode(sys.stdin.encoding)  # what else?
        self.assertEqual(input_result, expected)

    eleza test_input_tty(self):
        # Test uliza() functionality when wired to a tty (the code path
        # ni different na invokes GNU readline ikiwa available).
        self.check_input_tty("prompt", b"quux")

    eleza test_input_tty_non_ascii(self):
        # Check stdin/stdout encoding ni used when invoking GNU readline
        self.check_input_tty("prompté", b"quux\xe9", "utf-8")

    eleza test_input_tty_non_ascii_unicode_errors(self):
        # Check stdin/stdout error handler ni used when invoking GNU readline
        self.check_input_tty("prompté", b"quux\xe9", "ascii")

    eleza test_input_no_stdout_fileno(self):
        # Issue #24402: If stdin ni the original terminal but stdout.fileno()
        # fails, do sio use the original stdout file descriptor
        eleza child(wpipe):
            andika("stdin.isatty():", sys.stdin.isatty(), file=wpipe)
            sys.stdout = io.StringIO()  # Does sio support fileno()
            uliza("prompt")
            andika("captured:", ascii(sys.stdout.getvalue()), file=wpipe)
        lines = self.run_child(child, b"quux\r")
        expected = (
            "stdin.isatty(): Kweli",
            "captured: 'prompt'",
        )
        self.assertSequenceEqual(lines, expected)

kundi TestSorted(unittest.TestCase):

    eleza test_basic(self):
        data = list(range(100))
        copy = data[:]
        random.shuffle(copy)
        self.assertEqual(data, sorted(copy))
        self.assertNotEqual(data, copy)

        data.reverse()
        random.shuffle(copy)
        self.assertEqual(data, sorted(copy, key=lambda x: -x))
        self.assertNotEqual(data, copy)
        random.shuffle(copy)
        self.assertEqual(data, sorted(copy, reverse=1))
        self.assertNotEqual(data, copy)

    eleza test_bad_arguments(self):
        # Issue #29327: The first argument ni positional-only.
        sorted([])
        ukijumuisha self.assertRaises(TypeError):
            sorted(iterable=[])
        # Other arguments are keyword-only
        sorted([], key=Tupu)
        ukijumuisha self.assertRaises(TypeError):
            sorted([], Tupu)

    eleza test_inputtypes(self):
        s = 'abracadabra'
        types = [list, tuple, str]
        kila T kwenye types:
            self.assertEqual(sorted(s), sorted(T(s)))

        s = ''.join(set(s))  # unique letters only
        types = [str, set, frozenset, list, tuple, dict.fromkeys]
        kila T kwenye types:
            self.assertEqual(sorted(s), sorted(T(s)))

    eleza test_baddecorator(self):
        data = 'The quick Brown fox Jumped over The lazy Dog'.split()
        self.assertRaises(TypeError, sorted, data, Tupu, lambda x,y: 0)


kundi ShutdownTest(unittest.TestCase):

    eleza test_cleanup(self):
        # Issue #19255: builtins are still available at shutdown
        code = """ikiwa 1:
            agiza builtins
            agiza sys

            kundi C:
                eleza __del__(self):
                    andika("before")
                    # Check that builtins still exist
                    len(())
                    andika("after")

            c = C()
            # Make this module survive until builtins na sys are cleaned
            builtins.here = sys.modules[__name__]
            sys.here = sys.modules[__name__]
            # Create a reference loop so that this module needs to go
            # through a GC phase.
            here = sys.modules[__name__]
            """
        # Issue #20599: Force ASCII encoding to get a codec implemented kwenye C,
        # otherwise the codec may be unloaded before C.__del__() ni called, na
        # so andika("before") fails because the codec cansio be used to encode
        # "before" to sys.stdout.encoding. For example, on Windows,
        # sys.stdout.encoding ni the OEM code page na these code pages are
        # implemented kwenye Python
        rc, out, err = assert_python_ok("-c", code,
                                        PYTHONIOENCODING="ascii")
        self.assertEqual(["before", "after"], out.decode().splitlines())


kundi TestType(unittest.TestCase):
    eleza test_new_type(self):
        A = type('A', (), {})
        self.assertEqual(A.__name__, 'A')
        self.assertEqual(A.__qualname__, 'A')
        self.assertEqual(A.__module__, __name__)
        self.assertEqual(A.__bases__, (object,))
        self.assertIs(A.__base__, object)
        x = A()
        self.assertIs(type(x), A)
        self.assertIs(x.__class__, A)

        kundi B:
            eleza ham(self):
                rudisha 'ham%d' % self
        C = type('C', (B, int), {'spam': lambda self: 'spam%s' % self})
        self.assertEqual(C.__name__, 'C')
        self.assertEqual(C.__qualname__, 'C')
        self.assertEqual(C.__module__, __name__)
        self.assertEqual(C.__bases__, (B, int))
        self.assertIs(C.__base__, int)
        self.assertIn('spam', C.__dict__)
        self.assertNotIn('ham', C.__dict__)
        x = C(42)
        self.assertEqual(x, 42)
        self.assertIs(type(x), C)
        self.assertIs(x.__class__, C)
        self.assertEqual(x.ham(), 'ham42')
        self.assertEqual(x.spam(), 'spam42')
        self.assertEqual(x.to_bytes(2, 'little'), b'\x2a\x00')

    eleza test_type_nokwargs(self):
        ukijumuisha self.assertRaises(TypeError):
            type('a', (), {}, x=5)
        ukijumuisha self.assertRaises(TypeError):
            type('a', (), dict={})

    eleza test_type_name(self):
        kila name kwenye 'A', '\xc4', '\U0001f40d', 'B.A', '42', '':
            ukijumuisha self.subTest(name=name):
                A = type(name, (), {})
                self.assertEqual(A.__name__, name)
                self.assertEqual(A.__qualname__, name)
                self.assertEqual(A.__module__, __name__)
        ukijumuisha self.assertRaises(ValueError):
            type('A\x00B', (), {})
        ukijumuisha self.assertRaises(ValueError):
            type('A\udcdcB', (), {})
        ukijumuisha self.assertRaises(TypeError):
            type(b'A', (), {})

        C = type('C', (), {})
        kila name kwenye 'A', '\xc4', '\U0001f40d', 'B.A', '42', '':
            ukijumuisha self.subTest(name=name):
                C.__name__ = name
                self.assertEqual(C.__name__, name)
                self.assertEqual(C.__qualname__, 'C')
                self.assertEqual(C.__module__, __name__)

        A = type('C', (), {})
        ukijumuisha self.assertRaises(ValueError):
            A.__name__ = 'A\x00B'
        self.assertEqual(A.__name__, 'C')
        ukijumuisha self.assertRaises(ValueError):
            A.__name__ = 'A\udcdcB'
        self.assertEqual(A.__name__, 'C')
        ukijumuisha self.assertRaises(TypeError):
            A.__name__ = b'A'
        self.assertEqual(A.__name__, 'C')

    eleza test_type_qualname(self):
        A = type('A', (), {'__qualname__': 'B.C'})
        self.assertEqual(A.__name__, 'A')
        self.assertEqual(A.__qualname__, 'B.C')
        self.assertEqual(A.__module__, __name__)
        ukijumuisha self.assertRaises(TypeError):
            type('A', (), {'__qualname__': b'B'})
        self.assertEqual(A.__qualname__, 'B.C')

        A.__qualname__ = 'D.E'
        self.assertEqual(A.__name__, 'A')
        self.assertEqual(A.__qualname__, 'D.E')
        ukijumuisha self.assertRaises(TypeError):
            A.__qualname__ = b'B'
        self.assertEqual(A.__qualname__, 'D.E')

    eleza test_type_doc(self):
        kila doc kwenye 'x', '\xc4', '\U0001f40d', 'x\x00y', b'x', 42, Tupu:
            A = type('A', (), {'__doc__': doc})
            self.assertEqual(A.__doc__, doc)
        ukijumuisha self.assertRaises(UnicodeEncodeError):
            type('A', (), {'__doc__': 'x\udcdcy'})

        A = type('A', (), {})
        self.assertEqual(A.__doc__, Tupu)
        kila doc kwenye 'x', '\xc4', '\U0001f40d', 'x\x00y', 'x\udcdcy', b'x', 42, Tupu:
            A.__doc__ = doc
            self.assertEqual(A.__doc__, doc)

    eleza test_bad_args(self):
        ukijumuisha self.assertRaises(TypeError):
            type()
        ukijumuisha self.assertRaises(TypeError):
            type('A', ())
        ukijumuisha self.assertRaises(TypeError):
            type('A', (), {}, ())
        ukijumuisha self.assertRaises(TypeError):
            type('A', (), dict={})
        ukijumuisha self.assertRaises(TypeError):
            type('A', [], {})
        ukijumuisha self.assertRaises(TypeError):
            type('A', (), types.MappingProxyType({}))
        ukijumuisha self.assertRaises(TypeError):
            type('A', (Tupu,), {})
        ukijumuisha self.assertRaises(TypeError):
            type('A', (bool,), {})
        ukijumuisha self.assertRaises(TypeError):
            type('A', (int, str), {})

    eleza test_bad_slots(self):
        ukijumuisha self.assertRaises(TypeError):
            type('A', (), {'__slots__': b'x'})
        ukijumuisha self.assertRaises(TypeError):
            type('A', (int,), {'__slots__': 'x'})
        ukijumuisha self.assertRaises(TypeError):
            type('A', (), {'__slots__': ''})
        ukijumuisha self.assertRaises(TypeError):
            type('A', (), {'__slots__': '42'})
        ukijumuisha self.assertRaises(TypeError):
            type('A', (), {'__slots__': 'x\x00y'})
        ukijumuisha self.assertRaises(ValueError):
            type('A', (), {'__slots__': 'x', 'x': 0})
        ukijumuisha self.assertRaises(TypeError):
            type('A', (), {'__slots__': ('__dict__', '__dict__')})
        ukijumuisha self.assertRaises(TypeError):
            type('A', (), {'__slots__': ('__weakref__', '__weakref__')})

        kundi B:
            pita
        ukijumuisha self.assertRaises(TypeError):
            type('A', (B,), {'__slots__': '__dict__'})
        ukijumuisha self.assertRaises(TypeError):
            type('A', (B,), {'__slots__': '__weakref__'})

    eleza test_namespace_order(self):
        # bpo-34320: namespace should preserve order
        od = collections.OrderedDict([('a', 1), ('b', 2)])
        od.move_to_end('a')
        expected = list(od.items())

        C = type('C', (), od)
        self.assertEqual(list(C.__dict__.items())[:2], [('b', 2), ('a', 1)])


eleza load_tests(loader, tests, pattern):
    kutoka doctest agiza DocTestSuite
    tests.addTest(DocTestSuite(builtins))
    rudisha tests

ikiwa __name__ == "__main__":
    unittest.main()
