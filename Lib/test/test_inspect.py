agiza builtins
agiza collections
agiza datetime
agiza functools
agiza importlib
agiza inspect
agiza io
agiza linecache
agiza os
kutoka os.path agiza normcase
agiza _pickle
agiza pickle
agiza shutil
agiza sys
agiza types
agiza textwrap
agiza unicodedata
agiza unittest
agiza unittest.mock
agiza warnings

jaribu:
    kutoka concurrent.futures agiza ThreadPoolExecutor
tatizo ImportError:
    ThreadPoolExecutor = Tupu

kutoka test.support agiza run_unittest, TESTFN, DirsOnSysPath, cpython_only
kutoka test.support agiza MISSING_C_DOCSTRINGS, cpython_only
kutoka test.support.script_helper agiza assert_python_ok, assert_python_failure
kutoka test agiza inspect_fodder kama mod
kutoka test agiza inspect_fodder2 kama mod2
kutoka test agiza support

kutoka test.test_agiza agiza _ready_to_import


# Functions tested kwenye this suite:
# ismodule, isclass, ismethod, isfunction, istraceback, isframe, iscode,
# isbuiltin, isroutine, isgenerator, isgeneratorfunction, getmembers,
# getdoc, getfile, getmodule, getsourcefile, getcomments, getsource,
# getclasstree, getargvalues, formatargspec, formatargvalues,
# currentframe, stack, trace, isdatadescriptor

# NOTE: There are some additional tests relating to interaction with
#       zipagiza kwenye the test_zipimport_support test module.

modfile = mod.__file__
ikiwa modfile.endswith(('c', 'o')):
    modfile = modfile[:-1]

# Normalize file names: on Windows, the case of file names of compiled
# modules depends on the path used to start the python executable.
modfile = normcase(modfile)

eleza revise(filename, *args):
    rudisha (normcase(filename),) + args

git = mod.StupidGit()


eleza signatures_with_lexicographic_keyword_only_parameters():
    """
    Yields a whole bunch of functions ukijumuisha only keyword-only parameters,
    where those parameters are always kwenye lexicographically sorted order.
    """
    parameters = ['a', 'bar', 'c', 'delta', 'ephraim', 'magical', 'yoyo', 'z']
    kila i kwenye range(1, 2**len(parameters)):
        p = []
        bit = 1
        kila j kwenye range(len(parameters)):
            ikiwa i & (bit << j):
                p.append(parameters[j])
        fn_text = "eleza foo(*, " + ", ".join(p) + "): pita"
        symbols = {}
        exec(fn_text, symbols, symbols)
        tuma symbols['foo']


eleza unsorted_keyword_only_parameters_fn(*, throw, out, the, baby, with_,
                                        the_, bathwater):
    pita

unsorted_keyword_only_parameters = 'throw out the baby with_ the_ bathwater'.split()

kundi IsTestBase(unittest.TestCase):
    predicates = set([inspect.isbuiltin, inspect.isclass, inspect.iscode,
                      inspect.isframe, inspect.isfunction, inspect.ismethod,
                      inspect.ismodule, inspect.istraceback,
                      inspect.isgenerator, inspect.isgeneratorfunction,
                      inspect.iscoroutine, inspect.iscoroutinefunction,
                      inspect.isasyncgen, inspect.isasyncgenfunction])

    eleza istest(self, predicate, exp):
        obj = eval(exp)
        self.assertKweli(predicate(obj), '%s(%s)' % (predicate.__name__, exp))

        kila other kwenye self.predicates - set([predicate]):
            ikiwa (predicate == inspect.isgeneratorfunction ama \
               predicate == inspect.isasyncgenfunction ama \
               predicate == inspect.iscoroutinefunction) na \
               other == inspect.isfunction:
                endelea
            self.assertUongo(other(obj), 'sio %s(%s)' % (other.__name__, exp))

eleza generator_function_example(self):
    kila i kwenye range(2):
        tuma i

async eleza async_generator_function_example(self):
    async kila i kwenye range(2):
        tuma i

async eleza coroutine_function_example(self):
    rudisha 'spam'

@types.coroutine
eleza gen_coroutine_function_example(self):
    tuma
    rudisha 'spam'

kundi EqualsToAll:
    eleza __eq__(self, other):
        rudisha Kweli

kundi TestPredicates(IsTestBase):

    eleza test_excluding_predicates(self):
        global tb
        self.istest(inspect.isbuiltin, 'sys.exit')
        self.istest(inspect.isbuiltin, '[].append')
        self.istest(inspect.iscode, 'mod.spam.__code__')
        jaribu:
            1/0
        tatizo:
            tb = sys.exc_info()[2]
            self.istest(inspect.isframe, 'tb.tb_frame')
            self.istest(inspect.istraceback, 'tb')
            ikiwa hasattr(types, 'GetSetDescriptorType'):
                self.istest(inspect.isgetsetdescriptor,
                            'type(tb.tb_frame).f_locals')
            isipokua:
                self.assertUongo(inspect.isgetsetdescriptor(type(tb.tb_frame).f_locals))
        mwishowe:
            # Clear traceback na all the frames na local variables hanging to it.
            tb = Tupu
        self.istest(inspect.isfunction, 'mod.spam')
        self.istest(inspect.isfunction, 'mod.StupidGit.abuse')
        self.istest(inspect.ismethod, 'git.argue')
        self.istest(inspect.ismethod, 'mod.custom_method')
        self.istest(inspect.ismodule, 'mod')
        self.istest(inspect.isdatadescriptor, 'collections.defaultdict.default_factory')
        self.istest(inspect.isgenerator, '(x kila x kwenye range(2))')
        self.istest(inspect.isgeneratorfunction, 'generator_function_example')
        self.istest(inspect.isasyncgen,
                    'async_generator_function_example(1)')
        self.istest(inspect.isasyncgenfunction,
                    'async_generator_function_example')

        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.istest(inspect.iscoroutine, 'coroutine_function_example(1)')
            self.istest(inspect.iscoroutinefunction, 'coroutine_function_example')

        ikiwa hasattr(types, 'MemberDescriptorType'):
            self.istest(inspect.ismemberdescriptor, 'datetime.timedelta.days')
        isipokua:
            self.assertUongo(inspect.ismemberdescriptor(datetime.timedelta.days))

    eleza test_iscoroutine(self):
        async_gen_coro = async_generator_function_example(1)
        gen_coro = gen_coroutine_function_example(1)
        coro = coroutine_function_example(1)

        self.assertUongo(
            inspect.iscoroutinefunction(gen_coroutine_function_example))
        self.assertUongo(
            inspect.iscoroutinefunction(
                functools.partial(functools.partial(
                    gen_coroutine_function_example))))
        self.assertUongo(inspect.iscoroutine(gen_coro))

        self.assertKweli(
            inspect.isgeneratorfunction(gen_coroutine_function_example))
        self.assertKweli(
            inspect.isgeneratorfunction(
                functools.partial(functools.partial(
                    gen_coroutine_function_example))))
        self.assertKweli(inspect.isgenerator(gen_coro))

        self.assertKweli(
            inspect.iscoroutinefunction(coroutine_function_example))
        self.assertKweli(
            inspect.iscoroutinefunction(
                functools.partial(functools.partial(
                    coroutine_function_example))))
        self.assertKweli(inspect.iscoroutine(coro))

        self.assertUongo(
            inspect.isgeneratorfunction(coroutine_function_example))
        self.assertUongo(
            inspect.isgeneratorfunction(
                functools.partial(functools.partial(
                    coroutine_function_example))))
        self.assertUongo(inspect.isgenerator(coro))

        self.assertKweli(
            inspect.isasyncgenfunction(async_generator_function_example))
        self.assertKweli(
            inspect.isasyncgenfunction(
                functools.partial(functools.partial(
                    async_generator_function_example))))
        self.assertKweli(inspect.isasyncgen(async_gen_coro))

        coro.close(); gen_coro.close(); # silence warnings

    eleza test_isawaitable(self):
        eleza gen(): tuma
        self.assertUongo(inspect.isawaitable(gen()))

        coro = coroutine_function_example(1)
        gen_coro = gen_coroutine_function_example(1)

        self.assertKweli(inspect.isawaitable(coro))
        self.assertKweli(inspect.isawaitable(gen_coro))

        kundi Future:
            eleza __await__():
                pita
        self.assertKweli(inspect.isawaitable(Future()))
        self.assertUongo(inspect.isawaitable(Future))

        kundi NotFuture: pita
        not_fut = NotFuture()
        not_fut.__await__ = lambda: Tupu
        self.assertUongo(inspect.isawaitable(not_fut))

        coro.close(); gen_coro.close() # silence warnings

    eleza test_isroutine(self):
        self.assertKweli(inspect.isroutine(mod.spam))
        self.assertKweli(inspect.isroutine([].count))

    eleza test_isclass(self):
        self.istest(inspect.isclass, 'mod.StupidGit')
        self.assertKweli(inspect.isclass(list))

        kundi CustomGetattr(object):
            eleza __getattr__(self, attr):
                rudisha Tupu
        self.assertUongo(inspect.isclass(CustomGetattr()))

    eleza test_get_slot_members(self):
        kundi C(object):
            __slots__ = ("a", "b")
        x = C()
        x.a = 42
        members = dict(inspect.getmembers(x))
        self.assertIn('a', members)
        self.assertNotIn('b', members)

    eleza test_isabstract(self):
        kutoka abc agiza ABCMeta, abstractmethod

        kundi AbstractClassExample(metaclass=ABCMeta):

            @abstractmethod
            eleza foo(self):
                pita

        kundi ClassExample(AbstractClassExample):
            eleza foo(self):
                pita

        a = ClassExample()

        # Test general behaviour.
        self.assertKweli(inspect.isabstract(AbstractClassExample))
        self.assertUongo(inspect.isabstract(ClassExample))
        self.assertUongo(inspect.isabstract(a))
        self.assertUongo(inspect.isabstract(int))
        self.assertUongo(inspect.isabstract(5))

    eleza test_isabstract_during_init_subclass(self):
        kutoka abc agiza ABCMeta, abstractmethod
        isabstract_checks = []
        kundi AbstractChecker(metaclass=ABCMeta):
            eleza __init_subclass__(cls):
                isabstract_checks.append(inspect.isabstract(cls))
        kundi AbstractClassExample(AbstractChecker):
            @abstractmethod
            eleza foo(self):
                pita
        kundi ClassExample(AbstractClassExample):
            eleza foo(self):
                pita
        self.assertEqual(isabstract_checks, [Kweli, Uongo])

        isabstract_checks.clear()
        kundi AbstractChild(AbstractClassExample):
            pita
        kundi AbstractGrandchild(AbstractChild):
            pita
        kundi ConcreteGrandchild(ClassExample):
            pita
        self.assertEqual(isabstract_checks, [Kweli, Kweli, Uongo])


kundi TestInterpreterStack(IsTestBase):
    eleza __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

        git.abuse(7, 8, 9)

    eleza test_abuse_done(self):
        self.istest(inspect.istraceback, 'git.ex[2]')
        self.istest(inspect.isframe, 'mod.fr')

    eleza test_stack(self):
        self.assertKweli(len(mod.st) >= 5)
        self.assertEqual(revise(*mod.st[0][1:]),
             (modfile, 16, 'eggs', ['    st = inspect.stack()\n'], 0))
        self.assertEqual(revise(*mod.st[1][1:]),
             (modfile, 9, 'spam', ['    eggs(b + d, c + f)\n'], 0))
        self.assertEqual(revise(*mod.st[2][1:]),
             (modfile, 43, 'argue', ['            spam(a, b, c)\n'], 0))
        self.assertEqual(revise(*mod.st[3][1:]),
             (modfile, 39, 'abuse', ['        self.argue(a, b, c)\n'], 0))
        # Test named tuple fields
        record = mod.st[0]
        self.assertIs(record.frame, mod.fr)
        self.assertEqual(record.lineno, 16)
        self.assertEqual(record.filename, mod.__file__)
        self.assertEqual(record.function, 'eggs')
        self.assertIn('inspect.stack()', record.code_context[0])
        self.assertEqual(record.index, 0)

    eleza test_trace(self):
        self.assertEqual(len(git.tr), 3)
        self.assertEqual(revise(*git.tr[0][1:]),
             (modfile, 43, 'argue', ['            spam(a, b, c)\n'], 0))
        self.assertEqual(revise(*git.tr[1][1:]),
             (modfile, 9, 'spam', ['    eggs(b + d, c + f)\n'], 0))
        self.assertEqual(revise(*git.tr[2][1:]),
             (modfile, 18, 'eggs', ['    q = y / 0\n'], 0))

    eleza test_frame(self):
        args, varargs, varkw, locals = inspect.getargvalues(mod.fr)
        self.assertEqual(args, ['x', 'y'])
        self.assertEqual(varargs, Tupu)
        self.assertEqual(varkw, Tupu)
        self.assertEqual(locals, {'x': 11, 'p': 11, 'y': 14})
        self.assertEqual(inspect.formatargvalues(args, varargs, varkw, locals),
                         '(x=11, y=14)')

    eleza test_previous_frame(self):
        args, varargs, varkw, locals = inspect.getargvalues(mod.fr.f_back)
        self.assertEqual(args, ['a', 'b', 'c', 'd', 'e', 'f'])
        self.assertEqual(varargs, 'g')
        self.assertEqual(varkw, 'h')
        self.assertEqual(inspect.formatargvalues(args, varargs, varkw, locals),
             '(a=7, b=8, c=9, d=3, e=4, f=5, *g=(), **h={})')

kundi GetSourceBase(unittest.TestCase):
    # Subclasses must override.
    fodderModule = Tupu

    eleza setUp(self):
        ukijumuisha open(inspect.getsourcefile(self.fodderModule)) kama fp:
            self.source = fp.read()

    eleza sourcerange(self, top, bottom):
        lines = self.source.split("\n")
        rudisha "\n".join(lines[top-1:bottom]) + ("\n" ikiwa bottom isipokua "")

    eleza assertSourceEqual(self, obj, top, bottom):
        self.assertEqual(inspect.getsource(obj),
                         self.sourcerange(top, bottom))

kundi SlotUser:
    'Docstrings kila __slots__'
    __slots__ = {'power': 'measured kwenye kilowatts',
                 'distance': 'measured kwenye kilometers'}

kundi TestRetrievingSourceCode(GetSourceBase):
    fodderModule = mod

    eleza test_getclasses(self):
        classes = inspect.getmembers(mod, inspect.isclass)
        self.assertEqual(classes,
                         [('FesteringGob', mod.FesteringGob),
                          ('MalodorousPervert', mod.MalodorousPervert),
                          ('ParrotDroppings', mod.ParrotDroppings),
                          ('StupidGit', mod.StupidGit),
                          ('Tit', mod.MalodorousPervert),
                         ])
        tree = inspect.getclasstree([cls[1] kila cls kwenye classes])
        self.assertEqual(tree,
                         [(object, ()),
                          [(mod.ParrotDroppings, (object,)),
                           [(mod.FesteringGob, (mod.MalodorousPervert,
                                                   mod.ParrotDroppings))
                            ],
                           (mod.StupidGit, (object,)),
                           [(mod.MalodorousPervert, (mod.StupidGit,)),
                            [(mod.FesteringGob, (mod.MalodorousPervert,
                                                    mod.ParrotDroppings))
                             ]
                            ]
                           ]
                          ])
        tree = inspect.getclasstree([cls[1] kila cls kwenye classes], Kweli)
        self.assertEqual(tree,
                         [(object, ()),
                          [(mod.ParrotDroppings, (object,)),
                           (mod.StupidGit, (object,)),
                           [(mod.MalodorousPervert, (mod.StupidGit,)),
                            [(mod.FesteringGob, (mod.MalodorousPervert,
                                                    mod.ParrotDroppings))
                             ]
                            ]
                           ]
                          ])

    eleza test_getfunctions(self):
        functions = inspect.getmembers(mod, inspect.isfunction)
        self.assertEqual(functions, [('eggs', mod.eggs),
                                     ('lobbest', mod.lobbest),
                                     ('spam', mod.spam)])

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    eleza test_getdoc(self):
        self.assertEqual(inspect.getdoc(mod), 'A module docstring.')
        self.assertEqual(inspect.getdoc(mod.StupidGit),
                         'A longer,\n\nindented\n\ndocstring.')
        self.assertEqual(inspect.getdoc(git.abuse),
                         'Another\n\ndocstring\n\ncontaining\n\ntabs')
        self.assertEqual(inspect.getdoc(SlotUser.power),
                         'measured kwenye kilowatts')
        self.assertEqual(inspect.getdoc(SlotUser.distance),
                         'measured kwenye kilometers')

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    eleza test_getdoc_inherited(self):
        self.assertEqual(inspect.getdoc(mod.FesteringGob),
                         'A longer,\n\nindented\n\ndocstring.')
        self.assertEqual(inspect.getdoc(mod.FesteringGob.abuse),
                         'Another\n\ndocstring\n\ncontaining\n\ntabs')
        self.assertEqual(inspect.getdoc(mod.FesteringGob().abuse),
                         'Another\n\ndocstring\n\ncontaining\n\ntabs')
        self.assertEqual(inspect.getdoc(mod.FesteringGob.contradiction),
                         'The automatic gainsaying.')

    @unittest.skipIf(MISSING_C_DOCSTRINGS, "test requires docstrings")
    eleza test_finddoc(self):
        finddoc = inspect._finddoc
        self.assertEqual(finddoc(int), int.__doc__)
        self.assertEqual(finddoc(int.to_bytes), int.to_bytes.__doc__)
        self.assertEqual(finddoc(int().to_bytes), int.to_bytes.__doc__)
        self.assertEqual(finddoc(int.from_bytes), int.from_bytes.__doc__)
        self.assertEqual(finddoc(int.real), int.real.__doc__)

    eleza test_cleandoc(self):
        self.assertEqual(inspect.cleandoc('An\n    indented\n    docstring.'),
                         'An\nindented\ndocstring.')

    eleza test_getcomments(self):
        self.assertEqual(inspect.getcomments(mod), '# line 1\n')
        self.assertEqual(inspect.getcomments(mod.StupidGit), '# line 20\n')
        # If the object source file ni sio available, rudisha Tupu.
        co = compile('x=1', '_non_existing_filename.py', 'exec')
        self.assertIsTupu(inspect.getcomments(co))
        # If the object has been defined kwenye C, rudisha Tupu.
        self.assertIsTupu(inspect.getcomments(list))

    eleza test_getmodule(self):
        # Check actual module
        self.assertEqual(inspect.getmodule(mod), mod)
        # Check kundi (uses __module__ attribute)
        self.assertEqual(inspect.getmodule(mod.StupidGit), mod)
        # Check a method (no __module__ attribute, falls back to filename)
        self.assertEqual(inspect.getmodule(mod.StupidGit.abuse), mod)
        # Do it again (check the caching isn't broken)
        self.assertEqual(inspect.getmodule(mod.StupidGit.abuse), mod)
        # Check a builtin
        self.assertEqual(inspect.getmodule(str), sys.modules["builtins"])
        # Check filename override
        self.assertEqual(inspect.getmodule(Tupu, modfile), mod)

    eleza test_getframeinfo_get_first_line(self):
        frame_info = inspect.getframeinfo(self.fodderModule.fr, 50)
        self.assertEqual(frame_info.code_context[0], "# line 1\n")
        self.assertEqual(frame_info.code_context[1], "'A module docstring.'\n")

    eleza test_getsource(self):
        self.assertSourceEqual(git.abuse, 29, 39)
        self.assertSourceEqual(mod.StupidGit, 21, 51)
        self.assertSourceEqual(mod.lobbest, 75, 76)

    eleza test_getsourcefile(self):
        self.assertEqual(normcase(inspect.getsourcefile(mod.spam)), modfile)
        self.assertEqual(normcase(inspect.getsourcefile(git.abuse)), modfile)
        fn = "_non_existing_filename_used_for_sourcefile_test.py"
        co = compile("x=1", fn, "exec")
        self.assertEqual(inspect.getsourcefile(co), Tupu)
        linecache.cache[co.co_filename] = (1, Tupu, "Tupu", co.co_filename)
        jaribu:
            self.assertEqual(normcase(inspect.getsourcefile(co)), fn)
        mwishowe:
            toa linecache.cache[co.co_filename]

    eleza test_getfile(self):
        self.assertEqual(inspect.getfile(mod.StupidGit), mod.__file__)

    eleza test_getfile_builtin_module(self):
        ukijumuisha self.assertRaises(TypeError) kama e:
            inspect.getfile(sys)
        self.assertKweli(str(e.exception).startswith('<module'))

    eleza test_getfile_builtin_class(self):
        ukijumuisha self.assertRaises(TypeError) kama e:
            inspect.getfile(int)
        self.assertKweli(str(e.exception).startswith('<class'))

    eleza test_getfile_builtin_function_or_method(self):
        ukijumuisha self.assertRaises(TypeError) kama e_abs:
            inspect.getfile(abs)
        self.assertIn('expected, got', str(e_abs.exception))
        ukijumuisha self.assertRaises(TypeError) kama e_append:
            inspect.getfile(list.append)
        self.assertIn('expected, got', str(e_append.exception))

    eleza test_getfile_class_without_module(self):
        kundi CM(type):
            @property
            eleza __module__(cls):
                ashiria AttributeError
        kundi C(metaclass=CM):
            pita
        ukijumuisha self.assertRaises(TypeError):
            inspect.getfile(C)

    eleza test_getfile_broken_repr(self):
        kundi ErrorRepr:
            eleza __repr__(self):
                ashiria Exception('xyz')
        er = ErrorRepr()
        ukijumuisha self.assertRaises(TypeError):
            inspect.getfile(er)

    eleza test_getmodule_recursion(self):
        kutoka types agiza ModuleType
        name = '__inspect_dummy'
        m = sys.modules[name] = ModuleType(name)
        m.__file__ = "<string>" # hopefully sio a real filename...
        m.__loader__ = "dummy"  # pretend the filename ni understood by a loader
        exec("eleza x(): pita", m.__dict__)
        self.assertEqual(inspect.getsourcefile(m.x.__code__), '<string>')
        toa sys.modules[name]
        inspect.getmodule(compile('a=10','','single'))

    eleza test_proceed_with_fake_filename(self):
        '''doctest monkeypatches linecache to enable inspection'''
        fn, source = '<test>', 'eleza x(): pita\n'
        getlines = linecache.getlines
        eleza monkey(filename, module_globals=Tupu):
            ikiwa filename == fn:
                rudisha source.splitlines(keepends=Kweli)
            isipokua:
                rudisha getlines(filename, module_globals)
        linecache.getlines = monkey
        jaribu:
            ns = {}
            exec(compile(source, fn, 'single'), ns)
            inspect.getsource(ns["x"])
        mwishowe:
            linecache.getlines = getlines

    eleza test_getsource_on_code_object(self):
        self.assertSourceEqual(mod.eggs.__code__, 12, 18)

kundi TestGettingSourceOfToplevelFrames(GetSourceBase):
    fodderModule = mod

    eleza test_range_toplevel_frame(self):
        self.maxDiff = Tupu
        self.assertSourceEqual(mod.currentframe, 1, Tupu)

    eleza test_range_traceback_toplevel_frame(self):
        self.assertSourceEqual(mod.tb, 1, Tupu)

kundi TestDecorators(GetSourceBase):
    fodderModule = mod2

    eleza test_wrapped_decorator(self):
        self.assertSourceEqual(mod2.wrapped, 14, 17)

    eleza test_replacing_decorator(self):
        self.assertSourceEqual(mod2.gone, 9, 10)

    eleza test_getsource_unwrap(self):
        self.assertSourceEqual(mod2.real, 130, 132)

    eleza test_decorator_with_lambda(self):
        self.assertSourceEqual(mod2.func114, 113, 115)

kundi TestOneliners(GetSourceBase):
    fodderModule = mod2
    eleza test_oneline_lambda(self):
        # Test inspect.getsource ukijumuisha a one-line lambda function.
        self.assertSourceEqual(mod2.oll, 25, 25)

    eleza test_threeline_lambda(self):
        # Test inspect.getsource ukijumuisha a three-line lambda function,
        # where the second na third lines are _not_ indented.
        self.assertSourceEqual(mod2.tll, 28, 30)

    eleza test_twoline_indented_lambda(self):
        # Test inspect.getsource ukijumuisha a two-line lambda function,
        # where the second line _is_ indented.
        self.assertSourceEqual(mod2.tlli, 33, 34)

    eleza test_onelinefunc(self):
        # Test inspect.getsource ukijumuisha a regular one-line function.
        self.assertSourceEqual(mod2.onelinefunc, 37, 37)

    eleza test_manyargs(self):
        # Test inspect.getsource ukijumuisha a regular function where
        # the arguments are on two lines na _not_ indented na
        # the body on the second line ukijumuisha the last arguments.
        self.assertSourceEqual(mod2.manyargs, 40, 41)

    eleza test_twolinefunc(self):
        # Test inspect.getsource ukijumuisha a regular function where
        # the body ni on two lines, following the argument list na
        # endelead on the next line by a \\.
        self.assertSourceEqual(mod2.twolinefunc, 44, 45)

    eleza test_lambda_in_list(self):
        # Test inspect.getsource ukijumuisha a one-line lambda function
        # defined kwenye a list, indented.
        self.assertSourceEqual(mod2.a[1], 49, 49)

    eleza test_anonymous(self):
        # Test inspect.getsource ukijumuisha a lambda function defined
        # kama argument to another function.
        self.assertSourceEqual(mod2.anonymous, 55, 55)

kundi TestBuggyCases(GetSourceBase):
    fodderModule = mod2

    eleza test_with_comment(self):
        self.assertSourceEqual(mod2.with_comment, 58, 59)

    eleza test_multiline_sig(self):
        self.assertSourceEqual(mod2.multiline_sig[0], 63, 64)

    eleza test_nested_class(self):
        self.assertSourceEqual(mod2.func69().func71, 71, 72)

    eleza test_one_liner_followed_by_non_name(self):
        self.assertSourceEqual(mod2.func77, 77, 77)

    eleza test_one_liner_dedent_non_name(self):
        self.assertSourceEqual(mod2.cls82.func83, 83, 83)

    eleza test_with_comment_instead_of_docstring(self):
        self.assertSourceEqual(mod2.func88, 88, 90)

    eleza test_method_in_dynamic_class(self):
        self.assertSourceEqual(mod2.method_in_dynamic_class, 95, 97)

    # This should sio skip kila CPython, but might on a repackaged python where
    # unicodedata ni sio an external module, ama on pypy.
    @unittest.skipIf(sio hasattr(unicodedata, '__file__') ama
                                 unicodedata.__file__.endswith('.py'),
                     "unicodedata ni sio an external binary module")
    eleza test_findsource_binary(self):
        self.assertRaises(OSError, inspect.getsource, unicodedata)
        self.assertRaises(OSError, inspect.findsource, unicodedata)

    eleza test_findsource_code_in_linecache(self):
        lines = ["x=1"]
        co = compile(lines[0], "_dynamically_created_file", "exec")
        self.assertRaises(OSError, inspect.findsource, co)
        self.assertRaises(OSError, inspect.getsource, co)
        linecache.cache[co.co_filename] = (1, Tupu, lines, co.co_filename)
        jaribu:
            self.assertEqual(inspect.findsource(co), (lines,0))
            self.assertEqual(inspect.getsource(co), lines[0])
        mwishowe:
            toa linecache.cache[co.co_filename]

    eleza test_findsource_without_filename(self):
        kila fname kwenye ['', '<string>']:
            co = compile('x=1', fname, "exec")
            self.assertRaises(IOError, inspect.findsource, co)
            self.assertRaises(IOError, inspect.getsource, co)

    eleza test_getsource_on_method(self):
        self.assertSourceEqual(mod2.ClassWithMethod.method, 118, 119)

    eleza test_nested_func(self):
        self.assertSourceEqual(mod2.cls135.func136, 136, 139)


kundi TestNoEOL(GetSourceBase):
    eleza setUp(self):
        self.tempdir = TESTFN + '_dir'
        os.mkdir(self.tempdir)
        ukijumuisha open(os.path.join(self.tempdir,
                               'inspect_fodder3%spy' % os.extsep), 'w') kama f:
            f.write("kundi X:\n    pita # No EOL")
        ukijumuisha DirsOnSysPath(self.tempdir):
            agiza inspect_fodder3 kama mod3
        self.fodderModule = mod3
        super().setUp()

    eleza tearDown(self):
        shutil.rmtree(self.tempdir)

    eleza test_class(self):
        self.assertSourceEqual(self.fodderModule.X, 1, 2)


kundi _BrokenDataDescriptor(object):
    """
    A broken data descriptor. See bug #1785.
    """
    eleza __get__(*args):
        ashiria AttributeError("broken data descriptor")

    eleza __set__(*args):
        ashiria RuntimeError

    eleza __getattr__(*args):
        ashiria AttributeError("broken data descriptor")


kundi _BrokenMethodDescriptor(object):
    """
    A broken method descriptor. See bug #1785.
    """
    eleza __get__(*args):
        ashiria AttributeError("broken method descriptor")

    eleza __getattr__(*args):
        ashiria AttributeError("broken method descriptor")


# Helper kila testing classify_class_attrs.
eleza attrs_wo_objs(cls):
    rudisha [t[:3] kila t kwenye inspect.classify_class_attrs(cls)]


kundi TestClassesAndFunctions(unittest.TestCase):
    eleza test_newstyle_mro(self):
        # The same w/ new-kundi MRO.
        kundi A(object):    pita
        kundi B(A): pita
        kundi C(A): pita
        kundi D(B, C): pita

        expected = (D, B, C, A, object)
        got = inspect.getmro(D)
        self.assertEqual(expected, got)

    eleza assertArgSpecEquals(self, routine, args_e, varargs_e=Tupu,
                            varkw_e=Tupu, defaults_e=Tupu, formatted=Tupu):
        ukijumuisha self.assertWarns(DeprecationWarning):
            args, varargs, varkw, defaults = inspect.getargspec(routine)
        self.assertEqual(args, args_e)
        self.assertEqual(varargs, varargs_e)
        self.assertEqual(varkw, varkw_e)
        self.assertEqual(defaults, defaults_e)
        ikiwa formatted ni sio Tupu:
            ukijumuisha self.assertWarns(DeprecationWarning):
                self.assertEqual(inspect.formatargspec(args, varargs, varkw, defaults),
                                 formatted)

    eleza assertFullArgSpecEquals(self, routine, args_e, varargs_e=Tupu,
                                    varkw_e=Tupu, defaults_e=Tupu,
                                    posonlyargs_e=[], kwonlyargs_e=[],
                                    kwonlydefaults_e=Tupu,
                                    ann_e={}, formatted=Tupu):
        args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, ann = \
            inspect.getfullargspec(routine)
        self.assertEqual(args, args_e)
        self.assertEqual(varargs, varargs_e)
        self.assertEqual(varkw, varkw_e)
        self.assertEqual(defaults, defaults_e)
        self.assertEqual(kwonlyargs, kwonlyargs_e)
        self.assertEqual(kwonlydefaults, kwonlydefaults_e)
        self.assertEqual(ann, ann_e)
        ikiwa formatted ni sio Tupu:
            ukijumuisha self.assertWarns(DeprecationWarning):
                self.assertEqual(inspect.formatargspec(args, varargs, varkw, defaults,
                                                       kwonlyargs, kwonlydefaults, ann),
                                 formatted)

    eleza test_getargspec(self):
        self.assertArgSpecEquals(mod.eggs, ['x', 'y'], formatted='(x, y)')

        self.assertArgSpecEquals(mod.spam,
                                 ['a', 'b', 'c', 'd', 'e', 'f'],
                                 'g', 'h', (3, 4, 5),
                                 '(a, b, c, d=3, e=4, f=5, *g, **h)')

        self.assertRaises(ValueError, self.assertArgSpecEquals,
                          mod2.keyworded, [])

        self.assertRaises(ValueError, self.assertArgSpecEquals,
                          mod2.annotated, [])
        self.assertRaises(ValueError, self.assertArgSpecEquals,
                          mod2.keyword_only_arg, [])


    eleza test_getfullargspec(self):
        self.assertFullArgSpecEquals(mod2.keyworded, [], varargs_e='arg1',
                                     kwonlyargs_e=['arg2'],
                                     kwonlydefaults_e={'arg2':1},
                                     formatted='(*arg1, arg2=1)')

        self.assertFullArgSpecEquals(mod2.annotated, ['arg1'],
                                     ann_e={'arg1' : list},
                                     formatted='(arg1: list)')
        self.assertFullArgSpecEquals(mod2.keyword_only_arg, [],
                                     kwonlyargs_e=['arg'],
                                     formatted='(*, arg)')

        self.assertFullArgSpecEquals(mod2.all_markers, ['a', 'b', 'c', 'd'],
                                     kwonlyargs_e=['e', 'f'],
                                     formatted='(a, b, c, d, *, e, f)')

        self.assertFullArgSpecEquals(mod2.all_markers_with_args_and_kwargs,
                                     ['a', 'b', 'c', 'd'],
                                     varargs_e='args',
                                     varkw_e='kwargs',
                                     kwonlyargs_e=['e', 'f'],
                                     formatted='(a, b, c, d, *args, e, f, **kwargs)')

        self.assertFullArgSpecEquals(mod2.all_markers_with_defaults, ['a', 'b', 'c', 'd'],
                                     defaults_e=(1,2,3),
                                     kwonlyargs_e=['e', 'f'],
                                     kwonlydefaults_e={'e': 4, 'f': 5},
                                     formatted='(a, b=1, c=2, d=3, *, e=4, f=5)')

    eleza test_argspec_api_ignores_wrapped(self):
        # Issue 20684: low level introspection API must ignore __wrapped__
        @functools.wraps(mod.spam)
        eleza ham(x, y):
            pita
        # Basic check
        self.assertArgSpecEquals(ham, ['x', 'y'], formatted='(x, y)')
        self.assertFullArgSpecEquals(ham, ['x', 'y'], formatted='(x, y)')
        self.assertFullArgSpecEquals(functools.partial(ham),
                                     ['x', 'y'], formatted='(x, y)')
        # Other variants
        eleza check_method(f):
            self.assertArgSpecEquals(f, ['self', 'x', 'y'],
                                        formatted='(self, x, y)')
        kundi C:
            @functools.wraps(mod.spam)
            eleza ham(self, x, y):
                pita
            pham = functools.partialmethod(ham)
            @functools.wraps(mod.spam)
            eleza __call__(self, x, y):
                pita
        check_method(C())
        check_method(C.ham)
        check_method(C().ham)
        check_method(C.pham)
        check_method(C().pham)

        kundi C_new:
            @functools.wraps(mod.spam)
            eleza __new__(self, x, y):
                pita
        check_method(C_new)

        kundi C_init:
            @functools.wraps(mod.spam)
            eleza __init__(self, x, y):
                pita
        check_method(C_init)

    eleza test_getfullargspec_signature_attr(self):
        eleza test():
            pita
        spam_param = inspect.Parameter('spam', inspect.Parameter.POSITIONAL_ONLY)
        test.__signature__ = inspect.Signature(parameters=(spam_param,))

        self.assertFullArgSpecEquals(test, ['spam'], formatted='(spam)')

    eleza test_getfullargspec_signature_annos(self):
        eleza test(a:'spam') -> 'ham': pita
        spec = inspect.getfullargspec(test)
        self.assertEqual(test.__annotations__, spec.annotations)

        eleza test(): pita
        spec = inspect.getfullargspec(test)
        self.assertEqual(test.__annotations__, spec.annotations)

    @unittest.skipIf(MISSING_C_DOCSTRINGS,
                     "Signature information kila builtins requires docstrings")
    eleza test_getfullargspec_builtin_methods(self):
        self.assertFullArgSpecEquals(_pickle.Pickler.dump, ['self', 'obj'],
                                     formatted='(self, obj)')

        self.assertFullArgSpecEquals(_pickle.Pickler(io.BytesIO()).dump, ['self', 'obj'],
                                     formatted='(self, obj)')

        self.assertFullArgSpecEquals(
             os.stat,
             args_e=['path'],
             kwonlyargs_e=['dir_fd', 'follow_symlinks'],
             kwonlydefaults_e={'dir_fd': Tupu, 'follow_symlinks': Kweli},
             formatted='(path, *, dir_fd=Tupu, follow_symlinks=Kweli)')

    @cpython_only
    @unittest.skipIf(MISSING_C_DOCSTRINGS,
                     "Signature information kila builtins requires docstrings")
    eleza test_getfullargspec_builtin_func(self):
        agiza _testcapi
        builtin = _testcapi.docstring_with_signature_with_defaults
        spec = inspect.getfullargspec(builtin)
        self.assertEqual(spec.defaults[0], 'avocado')

    @cpython_only
    @unittest.skipIf(MISSING_C_DOCSTRINGS,
                     "Signature information kila builtins requires docstrings")
    eleza test_getfullargspec_builtin_func_no_signature(self):
        agiza _testcapi
        builtin = _testcapi.docstring_no_signature
        ukijumuisha self.assertRaises(TypeError):
            inspect.getfullargspec(builtin)

    eleza test_getfullargspec_definition_order_preserved_on_kwonly(self):
        kila fn kwenye signatures_with_lexicographic_keyword_only_parameters():
            signature = inspect.getfullargspec(fn)
            l = list(signature.kwonlyargs)
            sorted_l = sorted(l)
            self.assertKweli(l)
            self.assertEqual(l, sorted_l)
        signature = inspect.getfullargspec(unsorted_keyword_only_parameters_fn)
        l = list(signature.kwonlyargs)
        self.assertEqual(l, unsorted_keyword_only_parameters)

    eleza test_getargspec_method(self):
        kundi A(object):
            eleza m(self):
                pita
        self.assertArgSpecEquals(A.m, ['self'])

    eleza test_classify_newstyle(self):
        kundi A(object):

            eleza s(): pita
            s = staticmethod(s)

            eleza c(cls): pita
            c = classmethod(c)

            eleza getp(self): pita
            p = property(getp)

            eleza m(self): pita

            eleza m1(self): pita

            datablob = '1'

            dd = _BrokenDataDescriptor()
            md = _BrokenMethodDescriptor()

        attrs = attrs_wo_objs(A)

        self.assertIn(('__new__', 'static method', object), attrs,
                      'missing __new__')
        self.assertIn(('__init__', 'method', object), attrs, 'missing __init__')

        self.assertIn(('s', 'static method', A), attrs, 'missing static method')
        self.assertIn(('c', 'kundi method', A), attrs, 'missing kundi method')
        self.assertIn(('p', 'property', A), attrs, 'missing property')
        self.assertIn(('m', 'method', A), attrs,
                      'missing plain method: %r' % attrs)
        self.assertIn(('m1', 'method', A), attrs, 'missing plain method')
        self.assertIn(('datablob', 'data', A), attrs, 'missing data')
        self.assertIn(('md', 'method', A), attrs, 'missing method descriptor')
        self.assertIn(('dd', 'data', A), attrs, 'missing data descriptor')

        kundi B(A):

            eleza m(self): pita

        attrs = attrs_wo_objs(B)
        self.assertIn(('s', 'static method', A), attrs, 'missing static method')
        self.assertIn(('c', 'kundi method', A), attrs, 'missing kundi method')
        self.assertIn(('p', 'property', A), attrs, 'missing property')
        self.assertIn(('m', 'method', B), attrs, 'missing plain method')
        self.assertIn(('m1', 'method', A), attrs, 'missing plain method')
        self.assertIn(('datablob', 'data', A), attrs, 'missing data')
        self.assertIn(('md', 'method', A), attrs, 'missing method descriptor')
        self.assertIn(('dd', 'data', A), attrs, 'missing data descriptor')


        kundi C(A):

            eleza m(self): pita
            eleza c(self): pita

        attrs = attrs_wo_objs(C)
        self.assertIn(('s', 'static method', A), attrs, 'missing static method')
        self.assertIn(('c', 'method', C), attrs, 'missing plain method')
        self.assertIn(('p', 'property', A), attrs, 'missing property')
        self.assertIn(('m', 'method', C), attrs, 'missing plain method')
        self.assertIn(('m1', 'method', A), attrs, 'missing plain method')
        self.assertIn(('datablob', 'data', A), attrs, 'missing data')
        self.assertIn(('md', 'method', A), attrs, 'missing method descriptor')
        self.assertIn(('dd', 'data', A), attrs, 'missing data descriptor')

        kundi D(B, C):

            eleza m1(self): pita

        attrs = attrs_wo_objs(D)
        self.assertIn(('s', 'static method', A), attrs, 'missing static method')
        self.assertIn(('c', 'method', C), attrs, 'missing plain method')
        self.assertIn(('p', 'property', A), attrs, 'missing property')
        self.assertIn(('m', 'method', B), attrs, 'missing plain method')
        self.assertIn(('m1', 'method', D), attrs, 'missing plain method')
        self.assertIn(('datablob', 'data', A), attrs, 'missing data')
        self.assertIn(('md', 'method', A), attrs, 'missing method descriptor')
        self.assertIn(('dd', 'data', A), attrs, 'missing data descriptor')

    eleza test_classify_builtin_types(self):
        # Simple sanity check that all built-in types can have their
        # attributes classified.
        kila name kwenye dir(__builtins__):
            builtin = getattr(__builtins__, name)
            ikiwa isinstance(builtin, type):
                inspect.classify_class_attrs(builtin)

        attrs = attrs_wo_objs(bool)
        self.assertIn(('__new__', 'static method', bool), attrs,
                      'missing __new__')
        self.assertIn(('from_bytes', 'kundi method', int), attrs,
                      'missing kundi method')
        self.assertIn(('to_bytes', 'method', int), attrs,
                      'missing plain method')
        self.assertIn(('__add__', 'method', int), attrs,
                      'missing plain method')
        self.assertIn(('__and__', 'method', bool), attrs,
                      'missing plain method')

    eleza test_classify_DynamicClassAttribute(self):
        kundi Meta(type):
            eleza __getattr__(self, name):
                ikiwa name == 'ham':
                    rudisha 'spam'
                rudisha super().__getattr__(name)
        kundi VA(metaclass=Meta):
            @types.DynamicClassAttribute
            eleza ham(self):
                rudisha 'eggs'
        should_find_dca = inspect.Attribute('ham', 'data', VA, VA.__dict__['ham'])
        self.assertIn(should_find_dca, inspect.classify_class_attrs(VA))
        should_find_ga = inspect.Attribute('ham', 'data', Meta, 'spam')
        self.assertIn(should_find_ga, inspect.classify_class_attrs(VA))

    eleza test_classify_overrides_bool(self):
        kundi NoBool(object):
            eleza __eq__(self, other):
                rudisha NoBool()

            eleza __bool__(self):
                ashiria NotImplementedError(
                    "This object does sio specify a boolean value")

        kundi HasNB(object):
            dd = NoBool()

        should_find_attr = inspect.Attribute('dd', 'data', HasNB, HasNB.dd)
        self.assertIn(should_find_attr, inspect.classify_class_attrs(HasNB))

    eleza test_classify_metaclass_class_attribute(self):
        kundi Meta(type):
            fish = 'slap'
            eleza __dir__(self):
                rudisha ['__class__', '__module__', '__name__', 'fish']
        kundi Class(metaclass=Meta):
            pita
        should_find = inspect.Attribute('fish', 'data', Meta, 'slap')
        self.assertIn(should_find, inspect.classify_class_attrs(Class))

    eleza test_classify_VirtualAttribute(self):
        kundi Meta(type):
            eleza __dir__(cls):
                rudisha ['__class__', '__module__', '__name__', 'BOOM']
            eleza __getattr__(self, name):
                ikiwa name =='BOOM':
                    rudisha 42
                rudisha super().__getattr(name)
        kundi Class(metaclass=Meta):
            pita
        should_find = inspect.Attribute('BOOM', 'data', Meta, 42)
        self.assertIn(should_find, inspect.classify_class_attrs(Class))

    eleza test_classify_VirtualAttribute_multi_classes(self):
        kundi Meta1(type):
            eleza __dir__(cls):
                rudisha ['__class__', '__module__', '__name__', 'one']
            eleza __getattr__(self, name):
                ikiwa name =='one':
                    rudisha 1
                rudisha super().__getattr__(name)
        kundi Meta2(type):
            eleza __dir__(cls):
                rudisha ['__class__', '__module__', '__name__', 'two']
            eleza __getattr__(self, name):
                ikiwa name =='two':
                    rudisha 2
                rudisha super().__getattr__(name)
        kundi Meta3(Meta1, Meta2):
            eleza __dir__(cls):
                rudisha list(sorted(set(['__class__', '__module__', '__name__', 'three'] +
                    Meta1.__dir__(cls) + Meta2.__dir__(cls))))
            eleza __getattr__(self, name):
                ikiwa name =='three':
                    rudisha 3
                rudisha super().__getattr__(name)
        kundi Class1(metaclass=Meta1):
            pita
        kundi Class2(Class1, metaclass=Meta3):
            pita

        should_find1 = inspect.Attribute('one', 'data', Meta1, 1)
        should_find2 = inspect.Attribute('two', 'data', Meta2, 2)
        should_find3 = inspect.Attribute('three', 'data', Meta3, 3)
        cca = inspect.classify_class_attrs(Class2)
        kila sf kwenye (should_find1, should_find2, should_find3):
            self.assertIn(sf, cca)

    eleza test_classify_class_attrs_with_buggy_dir(self):
        kundi M(type):
            eleza __dir__(cls):
                rudisha ['__class__', '__name__', 'missing']
        kundi C(metaclass=M):
            pita
        attrs = [a[0] kila a kwenye inspect.classify_class_attrs(C)]
        self.assertNotIn('missing', attrs)

    eleza test_getmembers_descriptors(self):
        kundi A(object):
            dd = _BrokenDataDescriptor()
            md = _BrokenMethodDescriptor()

        eleza pred_wrapper(pred):
            # A quick'n'dirty way to discard standard attributes of new-style
            # classes.
            kundi Empty(object):
                pita
            eleza wrapped(x):
                ikiwa '__name__' kwenye dir(x) na hasattr(Empty, x.__name__):
                    rudisha Uongo
                rudisha pred(x)
            rudisha wrapped

        ismethoddescriptor = pred_wrapper(inspect.ismethoddescriptor)
        isdatadescriptor = pred_wrapper(inspect.isdatadescriptor)

        self.assertEqual(inspect.getmembers(A, ismethoddescriptor),
            [('md', A.__dict__['md'])])
        self.assertEqual(inspect.getmembers(A, isdatadescriptor),
            [('dd', A.__dict__['dd'])])

        kundi B(A):
            pita

        self.assertEqual(inspect.getmembers(B, ismethoddescriptor),
            [('md', A.__dict__['md'])])
        self.assertEqual(inspect.getmembers(B, isdatadescriptor),
            [('dd', A.__dict__['dd'])])

    eleza test_getmembers_method(self):
        kundi B:
            eleza f(self):
                pita

        self.assertIn(('f', B.f), inspect.getmembers(B))
        self.assertNotIn(('f', B.f), inspect.getmembers(B, inspect.ismethod))
        b = B()
        self.assertIn(('f', b.f), inspect.getmembers(b))
        self.assertIn(('f', b.f), inspect.getmembers(b, inspect.ismethod))

    eleza test_getmembers_VirtualAttribute(self):
        kundi M(type):
            eleza __getattr__(cls, name):
                ikiwa name == 'eggs':
                    rudisha 'scrambled'
                rudisha super().__getattr__(name)
        kundi A(metaclass=M):
            @types.DynamicClassAttribute
            eleza eggs(self):
                rudisha 'spam'
        self.assertIn(('eggs', 'scrambled'), inspect.getmembers(A))
        self.assertIn(('eggs', 'spam'), inspect.getmembers(A()))

    eleza test_getmembers_with_buggy_dir(self):
        kundi M(type):
            eleza __dir__(cls):
                rudisha ['__class__', '__name__', 'missing']
        kundi C(metaclass=M):
            pita
        attrs = [a[0] kila a kwenye inspect.getmembers(C)]
        self.assertNotIn('missing', attrs)

kundi TestIsDataDescriptor(unittest.TestCase):

    eleza test_custom_descriptors(self):
        kundi NonDataDescriptor:
            eleza __get__(self, value, type=Tupu): pita
        kundi DataDescriptor0:
            eleza __set__(self, name, value): pita
        kundi DataDescriptor1:
            eleza __delete__(self, name): pita
        kundi DataDescriptor2:
            __set__ = Tupu
        self.assertUongo(inspect.isdatadescriptor(NonDataDescriptor()),
                         'kundi ukijumuisha only __get__ sio a data descriptor')
        self.assertKweli(inspect.isdatadescriptor(DataDescriptor0()),
                        'kundi ukijumuisha __set__ ni a data descriptor')
        self.assertKweli(inspect.isdatadescriptor(DataDescriptor1()),
                        'kundi ukijumuisha __delete__ ni a data descriptor')
        self.assertKweli(inspect.isdatadescriptor(DataDescriptor2()),
                        'kundi ukijumuisha __set__ = Tupu ni a data descriptor')

    eleza test_slot(self):
        kundi Slotted:
            __slots__ = 'foo',
        self.assertKweli(inspect.isdatadescriptor(Slotted.foo),
                        'a slot ni a data descriptor')

    eleza test_property(self):
        kundi Propertied:
            @property
            eleza a_property(self):
                pita
        self.assertKweli(inspect.isdatadescriptor(Propertied.a_property),
                        'a property ni a data descriptor')

    eleza test_functions(self):
        kundi Test(object):
            eleza instance_method(self): pita
            @classmethod
            eleza class_method(cls): pita
            @staticmethod
            eleza static_method(): pita
        eleza function():
            pita
        a_lambda = lambda: Tupu
        self.assertUongo(inspect.isdatadescriptor(Test().instance_method),
                         'a instance method ni sio a data descriptor')
        self.assertUongo(inspect.isdatadescriptor(Test().class_method),
                         'a kundi method ni sio a data descriptor')
        self.assertUongo(inspect.isdatadescriptor(Test().static_method),
                         'a static method ni sio a data descriptor')
        self.assertUongo(inspect.isdatadescriptor(function),
                         'a function ni sio a data descriptor')
        self.assertUongo(inspect.isdatadescriptor(a_lambda),
                         'a lambda ni sio a data descriptor')


_global_ref = object()
kundi TestGetClosureVars(unittest.TestCase):

    eleza test_name_resolution(self):
        # Basic test of the 4 different resolution mechanisms
        eleza f(nonlocal_ref):
            eleza g(local_ref):
                andika(local_ref, nonlocal_ref, _global_ref, unbound_ref)
            rudisha g
        _arg = object()
        nonlocal_vars = {"nonlocal_ref": _arg}
        global_vars = {"_global_ref": _global_ref}
        builtin_vars = {"print": print}
        unbound_names = {"unbound_ref"}
        expected = inspect.ClosureVars(nonlocal_vars, global_vars,
                                       builtin_vars, unbound_names)
        self.assertEqual(inspect.getclosurevars(f(_arg)), expected)

    eleza test_generator_closure(self):
        eleza f(nonlocal_ref):
            eleza g(local_ref):
                andika(local_ref, nonlocal_ref, _global_ref, unbound_ref)
                tuma
            rudisha g
        _arg = object()
        nonlocal_vars = {"nonlocal_ref": _arg}
        global_vars = {"_global_ref": _global_ref}
        builtin_vars = {"print": print}
        unbound_names = {"unbound_ref"}
        expected = inspect.ClosureVars(nonlocal_vars, global_vars,
                                       builtin_vars, unbound_names)
        self.assertEqual(inspect.getclosurevars(f(_arg)), expected)

    eleza test_method_closure(self):
        kundi C:
            eleza f(self, nonlocal_ref):
                eleza g(local_ref):
                    andika(local_ref, nonlocal_ref, _global_ref, unbound_ref)
                rudisha g
        _arg = object()
        nonlocal_vars = {"nonlocal_ref": _arg}
        global_vars = {"_global_ref": _global_ref}
        builtin_vars = {"print": print}
        unbound_names = {"unbound_ref"}
        expected = inspect.ClosureVars(nonlocal_vars, global_vars,
                                       builtin_vars, unbound_names)
        self.assertEqual(inspect.getclosurevars(C().f(_arg)), expected)

    eleza test_nonlocal_vars(self):
        # More complex tests of nonlocal resolution
        eleza _nonlocal_vars(f):
            rudisha inspect.getclosurevars(f).nonlocals

        eleza make_adder(x):
            eleza add(y):
                rudisha x + y
            rudisha add

        eleza curry(func, arg1):
            rudisha lambda arg2: func(arg1, arg2)

        eleza less_than(a, b):
            rudisha a < b

        # The infamous Y combinator.
        eleza Y(le):
            eleza g(f):
                rudisha le(lambda x: f(f)(x))
            Y.g_ref = g
            rudisha g(g)

        eleza check_y_combinator(func):
            self.assertEqual(_nonlocal_vars(func), {'f': Y.g_ref})

        inc = make_adder(1)
        add_two = make_adder(2)
        greater_than_five = curry(less_than, 5)

        self.assertEqual(_nonlocal_vars(inc), {'x': 1})
        self.assertEqual(_nonlocal_vars(add_two), {'x': 2})
        self.assertEqual(_nonlocal_vars(greater_than_five),
                         {'arg1': 5, 'func': less_than})
        self.assertEqual(_nonlocal_vars((lambda x: lambda y: x + y)(3)),
                         {'x': 3})
        Y(check_y_combinator)

    eleza test_getclosurevars_empty(self):
        eleza foo(): pita
        _empty = inspect.ClosureVars({}, {}, {}, set())
        self.assertEqual(inspect.getclosurevars(lambda: Kweli), _empty)
        self.assertEqual(inspect.getclosurevars(foo), _empty)

    eleza test_getclosurevars_error(self):
        kundi T: pita
        self.assertRaises(TypeError, inspect.getclosurevars, 1)
        self.assertRaises(TypeError, inspect.getclosurevars, list)
        self.assertRaises(TypeError, inspect.getclosurevars, {})

    eleza _private_globals(self):
        code = """eleza f(): andika(path)"""
        ns = {}
        exec(code, ns)
        rudisha ns["f"], ns

    eleza test_builtins_fallback(self):
        f, ns = self._private_globals()
        ns.pop("__builtins__", Tupu)
        expected = inspect.ClosureVars({}, {}, {"print":print}, {"path"})
        self.assertEqual(inspect.getclosurevars(f), expected)

    eleza test_builtins_as_dict(self):
        f, ns = self._private_globals()
        ns["__builtins__"] = {"path":1}
        expected = inspect.ClosureVars({}, {}, {"path":1}, {"print"})
        self.assertEqual(inspect.getclosurevars(f), expected)

    eleza test_builtins_as_module(self):
        f, ns = self._private_globals()
        ns["__builtins__"] = os
        expected = inspect.ClosureVars({}, {}, {"path":os.path}, {"print"})
        self.assertEqual(inspect.getclosurevars(f), expected)


kundi TestGetcallargsFunctions(unittest.TestCase):

    eleza assertEqualCallArgs(self, func, call_params_string, locs=Tupu):
        locs = dict(locs ama {}, func=func)
        r1 = eval('func(%s)' % call_params_string, Tupu, locs)
        r2 = eval('inspect.getcallargs(func, %s)' % call_params_string, Tupu,
                  locs)
        self.assertEqual(r1, r2)

    eleza assertEqualException(self, func, call_param_string, locs=Tupu):
        locs = dict(locs ama {}, func=func)
        jaribu:
            eval('func(%s)' % call_param_string, Tupu, locs)
        tatizo Exception kama e:
            ex1 = e
        isipokua:
            self.fail('Exception sio raised')
        jaribu:
            eval('inspect.getcallargs(func, %s)' % call_param_string, Tupu,
                 locs)
        tatizo Exception kama e:
            ex2 = e
        isipokua:
            self.fail('Exception sio raised')
        self.assertIs(type(ex1), type(ex2))
        self.assertEqual(str(ex1), str(ex2))
        toa ex1, ex2

    eleza makeCallable(self, signature):
        """Create a function that returns its locals()"""
        code = "lambda %s: locals()"
        rudisha eval(code % signature)

    eleza test_plain(self):
        f = self.makeCallable('a, b=1')
        self.assertEqualCallArgs(f, '2')
        self.assertEqualCallArgs(f, '2, 3')
        self.assertEqualCallArgs(f, 'a=2')
        self.assertEqualCallArgs(f, 'b=3, a=2')
        self.assertEqualCallArgs(f, '2, b=3')
        # expand *iterable / **mapping
        self.assertEqualCallArgs(f, '*(2,)')
        self.assertEqualCallArgs(f, '*[2]')
        self.assertEqualCallArgs(f, '*(2, 3)')
        self.assertEqualCallArgs(f, '*[2, 3]')
        self.assertEqualCallArgs(f, '**{"a":2}')
        self.assertEqualCallArgs(f, 'b=3, **{"a":2}')
        self.assertEqualCallArgs(f, '2, **{"b":3}')
        self.assertEqualCallArgs(f, '**{"b":3, "a":2}')
        # expand UserList / UserDict
        self.assertEqualCallArgs(f, '*collections.UserList([2])')
        self.assertEqualCallArgs(f, '*collections.UserList([2, 3])')
        self.assertEqualCallArgs(f, '**collections.UserDict(a=2)')
        self.assertEqualCallArgs(f, '2, **collections.UserDict(b=3)')
        self.assertEqualCallArgs(f, 'b=2, **collections.UserDict(a=3)')

    eleza test_varargs(self):
        f = self.makeCallable('a, b=1, *c')
        self.assertEqualCallArgs(f, '2')
        self.assertEqualCallArgs(f, '2, 3')
        self.assertEqualCallArgs(f, '2, 3, 4')
        self.assertEqualCallArgs(f, '*(2,3,4)')
        self.assertEqualCallArgs(f, '2, *[3,4]')
        self.assertEqualCallArgs(f, '2, 3, *collections.UserList([4])')

    eleza test_varkw(self):
        f = self.makeCallable('a, b=1, **c')
        self.assertEqualCallArgs(f, 'a=2')
        self.assertEqualCallArgs(f, '2, b=3, c=4')
        self.assertEqualCallArgs(f, 'b=3, a=2, c=4')
        self.assertEqualCallArgs(f, 'c=4, **{"a":2, "b":3}')
        self.assertEqualCallArgs(f, '2, c=4, **{"b":3}')
        self.assertEqualCallArgs(f, 'b=2, **{"a":3, "c":4}')
        self.assertEqualCallArgs(f, '**collections.UserDict(a=2, b=3, c=4)')
        self.assertEqualCallArgs(f, '2, c=4, **collections.UserDict(b=3)')
        self.assertEqualCallArgs(f, 'b=2, **collections.UserDict(a=3, c=4)')

    eleza test_varkw_only(self):
        # issue11256:
        f = self.makeCallable('**c')
        self.assertEqualCallArgs(f, '')
        self.assertEqualCallArgs(f, 'a=1')
        self.assertEqualCallArgs(f, 'a=1, b=2')
        self.assertEqualCallArgs(f, 'c=3, **{"a": 1, "b": 2}')
        self.assertEqualCallArgs(f, '**collections.UserDict(a=1, b=2)')
        self.assertEqualCallArgs(f, 'c=3, **collections.UserDict(a=1, b=2)')

    eleza test_keyword_only(self):
        f = self.makeCallable('a=3, *, c, d=2')
        self.assertEqualCallArgs(f, 'c=3')
        self.assertEqualCallArgs(f, 'c=3, a=3')
        self.assertEqualCallArgs(f, 'a=2, c=4')
        self.assertEqualCallArgs(f, '4, c=4')
        self.assertEqualException(f, '')
        self.assertEqualException(f, '3')
        self.assertEqualException(f, 'a=3')
        self.assertEqualException(f, 'd=4')

        f = self.makeCallable('*, c, d=2')
        self.assertEqualCallArgs(f, 'c=3')
        self.assertEqualCallArgs(f, 'c=3, d=4')
        self.assertEqualCallArgs(f, 'd=4, c=3')

    eleza test_multiple_features(self):
        f = self.makeCallable('a, b=2, *f, **g')
        self.assertEqualCallArgs(f, '2, 3, 7')
        self.assertEqualCallArgs(f, '2, 3, x=8')
        self.assertEqualCallArgs(f, '2, 3, x=8, *[(4,[5,6]), 7]')
        self.assertEqualCallArgs(f, '2, x=8, *[3, (4,[5,6]), 7], y=9')
        self.assertEqualCallArgs(f, 'x=8, *[2, 3, (4,[5,6])], y=9')
        self.assertEqualCallArgs(f, 'x=8, *collections.UserList('
                                 '[2, 3, (4,[5,6])]), **{"y":9, "z":10}')
        self.assertEqualCallArgs(f, '2, x=8, *collections.UserList([3, '
                                 '(4,[5,6])]), **collections.UserDict('
                                 'y=9, z=10)')

        f = self.makeCallable('a, b=2, *f, x, y=99, **g')
        self.assertEqualCallArgs(f, '2, 3, x=8')
        self.assertEqualCallArgs(f, '2, 3, x=8, *[(4,[5,6]), 7]')
        self.assertEqualCallArgs(f, '2, x=8, *[3, (4,[5,6]), 7], y=9, z=10')
        self.assertEqualCallArgs(f, 'x=8, *[2, 3, (4,[5,6])], y=9, z=10')
        self.assertEqualCallArgs(f, 'x=8, *collections.UserList('
                                 '[2, 3, (4,[5,6])]), q=0, **{"y":9, "z":10}')
        self.assertEqualCallArgs(f, '2, x=8, *collections.UserList([3, '
                                 '(4,[5,6])]), q=0, **collections.UserDict('
                                 'y=9, z=10)')

    eleza test_errors(self):
        f0 = self.makeCallable('')
        f1 = self.makeCallable('a, b')
        f2 = self.makeCallable('a, b=1')
        # f0 takes no arguments
        self.assertEqualException(f0, '1')
        self.assertEqualException(f0, 'x=1')
        self.assertEqualException(f0, '1,x=1')
        # f1 takes exactly 2 arguments
        self.assertEqualException(f1, '')
        self.assertEqualException(f1, '1')
        self.assertEqualException(f1, 'a=2')
        self.assertEqualException(f1, 'b=3')
        # f2 takes at least 1 argument
        self.assertEqualException(f2, '')
        self.assertEqualException(f2, 'b=3')
        kila f kwenye f1, f2:
            # f1/f2 takes exactly/at most 2 arguments
            self.assertEqualException(f, '2, 3, 4')
            self.assertEqualException(f, '1, 2, 3, a=1')
            self.assertEqualException(f, '2, 3, 4, c=5')
            # XXX: success of this one depends on dict order
            ## self.assertEqualException(f, '2, 3, 4, a=1, c=5')
            # f got an unexpected keyword argument
            self.assertEqualException(f, 'c=2')
            self.assertEqualException(f, '2, c=3')
            self.assertEqualException(f, '2, 3, c=4')
            self.assertEqualException(f, '2, c=4, b=3')
            self.assertEqualException(f, '**{u"\u03c0\u03b9": 4}')
            # f got multiple values kila keyword argument
            self.assertEqualException(f, '1, a=2')
            self.assertEqualException(f, '1, **{"a":2}')
            self.assertEqualException(f, '1, 2, b=3')
            # XXX: Python inconsistency
            # - kila functions na bound methods: unexpected keyword 'c'
            # - kila unbound methods: multiple values kila keyword 'a'
            #self.assertEqualException(f, '1, c=3, a=2')
        # issue11256:
        f3 = self.makeCallable('**c')
        self.assertEqualException(f3, '1, 2')
        self.assertEqualException(f3, '1, 2, a=1, b=2')
        f4 = self.makeCallable('*, a, b=0')
        self.assertEqualException(f3, '1, 2')
        self.assertEqualException(f3, '1, 2, a=1, b=2')

        # issue #20816: getcallargs() fails to iterate over non-existent
        # kwonlydefaults na raises a wrong TypeError
        eleza f5(*, a): pita
        ukijumuisha self.assertRaisesRegex(TypeError,
                                    'missing 1 required keyword-only'):
            inspect.getcallargs(f5)


        # issue20817:
        eleza f6(a, b, c):
            pita
        ukijumuisha self.assertRaisesRegex(TypeError, "'a', 'b' na 'c'"):
            inspect.getcallargs(f6)

        # bpo-33197
        ukijumuisha self.assertRaisesRegex(ValueError,
                                    'variadic keyword parameters cannot'
                                    ' have default values'):
            inspect.Parameter("foo", kind=inspect.Parameter.VAR_KEYWORD,
                              default=42)
        ukijumuisha self.assertRaisesRegex(ValueError,
                                    "value 5 ni sio a valid Parameter.kind"):
            inspect.Parameter("bar", kind=5, default=42)

        ukijumuisha self.assertRaisesRegex(TypeError,
                                   'name must be a str, sio a int'):
            inspect.Parameter(123, kind=4)

kundi TestGetcallargsMethods(TestGetcallargsFunctions):

    eleza setUp(self):
        kundi Foo(object):
            pita
        self.cls = Foo
        self.inst = Foo()

    eleza makeCallable(self, signature):
        assert 'self' haiko kwenye signature
        mk = super(TestGetcallargsMethods, self).makeCallable
        self.cls.method = mk('self, ' + signature)
        rudisha self.inst.method

kundi TestGetcallargsUnboundMethods(TestGetcallargsMethods):

    eleza makeCallable(self, signature):
        super(TestGetcallargsUnboundMethods, self).makeCallable(signature)
        rudisha self.cls.method

    eleza assertEqualCallArgs(self, func, call_params_string, locs=Tupu):
        rudisha super(TestGetcallargsUnboundMethods, self).assertEqualCallArgs(
            *self._getAssertEqualParams(func, call_params_string, locs))

    eleza assertEqualException(self, func, call_params_string, locs=Tupu):
        rudisha super(TestGetcallargsUnboundMethods, self).assertEqualException(
            *self._getAssertEqualParams(func, call_params_string, locs))

    eleza _getAssertEqualParams(self, func, call_params_string, locs=Tupu):
        assert 'inst' haiko kwenye call_params_string
        locs = dict(locs ama {}, inst=self.inst)
        rudisha (func, 'inst,' + call_params_string, locs)


kundi TestGetattrStatic(unittest.TestCase):

    eleza test_basic(self):
        kundi Thing(object):
            x = object()

        thing = Thing()
        self.assertEqual(inspect.getattr_static(thing, 'x'), Thing.x)
        self.assertEqual(inspect.getattr_static(thing, 'x', Tupu), Thing.x)
        ukijumuisha self.assertRaises(AttributeError):
            inspect.getattr_static(thing, 'y')

        self.assertEqual(inspect.getattr_static(thing, 'y', 3), 3)

    eleza test_inherited(self):
        kundi Thing(object):
            x = object()
        kundi OtherThing(Thing):
            pita

        something = OtherThing()
        self.assertEqual(inspect.getattr_static(something, 'x'), Thing.x)

    eleza test_instance_attr(self):
        kundi Thing(object):
            x = 2
            eleza __init__(self, x):
                self.x = x
        thing = Thing(3)
        self.assertEqual(inspect.getattr_static(thing, 'x'), 3)
        toa thing.x
        self.assertEqual(inspect.getattr_static(thing, 'x'), 2)

    eleza test_property(self):
        kundi Thing(object):
            @property
            eleza x(self):
                ashiria AttributeError("I'm pretending sio to exist")
        thing = Thing()
        self.assertEqual(inspect.getattr_static(thing, 'x'), Thing.x)

    eleza test_descriptor_raises_AttributeError(self):
        kundi descriptor(object):
            eleza __get__(*_):
                ashiria AttributeError("I'm pretending sio to exist")
        desc = descriptor()
        kundi Thing(object):
            x = desc
        thing = Thing()
        self.assertEqual(inspect.getattr_static(thing, 'x'), desc)

    eleza test_classAttribute(self):
        kundi Thing(object):
            x = object()

        self.assertEqual(inspect.getattr_static(Thing, 'x'), Thing.x)

    eleza test_classVirtualAttribute(self):
        kundi Thing(object):
            @types.DynamicClassAttribute
            eleza x(self):
                rudisha self._x
            _x = object()

        self.assertEqual(inspect.getattr_static(Thing, 'x'), Thing.__dict__['x'])

    eleza test_inherited_classattribute(self):
        kundi Thing(object):
            x = object()
        kundi OtherThing(Thing):
            pita

        self.assertEqual(inspect.getattr_static(OtherThing, 'x'), Thing.x)

    eleza test_slots(self):
        kundi Thing(object):
            y = 'bar'
            __slots__ = ['x']
            eleza __init__(self):
                self.x = 'foo'
        thing = Thing()
        self.assertEqual(inspect.getattr_static(thing, 'x'), Thing.x)
        self.assertEqual(inspect.getattr_static(thing, 'y'), 'bar')

        toa thing.x
        self.assertEqual(inspect.getattr_static(thing, 'x'), Thing.x)

    eleza test_metaclass(self):
        kundi meta(type):
            attr = 'foo'
        kundi Thing(object, metaclass=meta):
            pita
        self.assertEqual(inspect.getattr_static(Thing, 'attr'), 'foo')

        kundi sub(meta):
            pita
        kundi OtherThing(object, metaclass=sub):
            x = 3
        self.assertEqual(inspect.getattr_static(OtherThing, 'attr'), 'foo')

        kundi OtherOtherThing(OtherThing):
            pita
        # this test ni odd, but it was added kama it exposed a bug
        self.assertEqual(inspect.getattr_static(OtherOtherThing, 'x'), 3)

    eleza test_no_dict_no_slots(self):
        self.assertEqual(inspect.getattr_static(1, 'foo', Tupu), Tupu)
        self.assertNotEqual(inspect.getattr_static('foo', 'lower'), Tupu)

    eleza test_no_dict_no_slots_instance_member(self):
        # returns descriptor
        ukijumuisha open(__file__) kama handle:
            self.assertEqual(inspect.getattr_static(handle, 'name'), type(handle).name)

    eleza test_inherited_slots(self):
        # returns descriptor
        kundi Thing(object):
            __slots__ = ['x']
            eleza __init__(self):
                self.x = 'foo'

        kundi OtherThing(Thing):
            pita
        # it would be nice ikiwa this worked...
        # we get the descriptor instead of the instance attribute
        self.assertEqual(inspect.getattr_static(OtherThing(), 'x'), Thing.x)

    eleza test_descriptor(self):
        kundi descriptor(object):
            eleza __get__(self, instance, owner):
                rudisha 3
        kundi Foo(object):
            d = descriptor()

        foo = Foo()

        # kila a non data descriptor we rudisha the instance attribute
        foo.__dict__['d'] = 1
        self.assertEqual(inspect.getattr_static(foo, 'd'), 1)

        # ikiwa the descriptor ni a data-descriptor we should rudisha the
        # descriptor
        descriptor.__set__ = lambda s, i, v: Tupu
        self.assertEqual(inspect.getattr_static(foo, 'd'), Foo.__dict__['d'])


    eleza test_metaclass_with_descriptor(self):
        kundi descriptor(object):
            eleza __get__(self, instance, owner):
                rudisha 3
        kundi meta(type):
            d = descriptor()
        kundi Thing(object, metaclass=meta):
            pita
        self.assertEqual(inspect.getattr_static(Thing, 'd'), meta.__dict__['d'])


    eleza test_class_as_property(self):
        kundi Base(object):
            foo = 3

        kundi Something(Base):
            executed = Uongo
            @property
            eleza __class__(self):
                self.executed = Kweli
                rudisha object

        instance = Something()
        self.assertEqual(inspect.getattr_static(instance, 'foo'), 3)
        self.assertUongo(instance.executed)
        self.assertEqual(inspect.getattr_static(Something, 'foo'), 3)

    eleza test_mro_as_property(self):
        kundi Meta(type):
            @property
            eleza __mro__(self):
                rudisha (object,)

        kundi Base(object):
            foo = 3

        kundi Something(Base, metaclass=Meta):
            pita

        self.assertEqual(inspect.getattr_static(Something(), 'foo'), 3)
        self.assertEqual(inspect.getattr_static(Something, 'foo'), 3)

    eleza test_dict_as_property(self):
        test = self
        test.called = Uongo

        kundi Foo(dict):
            a = 3
            @property
            eleza __dict__(self):
                test.called = Kweli
                rudisha {}

        foo = Foo()
        foo.a = 4
        self.assertEqual(inspect.getattr_static(foo, 'a'), 3)
        self.assertUongo(test.called)

    eleza test_custom_object_dict(self):
        test = self
        test.called = Uongo

        kundi Custom(dict):
            eleza get(self, key, default=Tupu):
                test.called = Kweli
                super().get(key, default)

        kundi Foo(object):
            a = 3
        foo = Foo()
        foo.__dict__ = Custom()
        self.assertEqual(inspect.getattr_static(foo, 'a'), 3)
        self.assertUongo(test.called)

    eleza test_metaclass_dict_as_property(self):
        kundi Meta(type):
            @property
            eleza __dict__(self):
                self.executed = Kweli

        kundi Thing(metaclass=Meta):
            executed = Uongo

            eleza __init__(self):
                self.spam = 42

        instance = Thing()
        self.assertEqual(inspect.getattr_static(instance, "spam"), 42)
        self.assertUongo(Thing.executed)

    eleza test_module(self):
        sentinel = object()
        self.assertIsNot(inspect.getattr_static(sys, "version", sentinel),
                         sentinel)

    eleza test_metaclass_with_metaclass_with_dict_as_property(self):
        kundi MetaMeta(type):
            @property
            eleza __dict__(self):
                self.executed = Kweli
                rudisha dict(spam=42)

        kundi Meta(type, metaclass=MetaMeta):
            executed = Uongo

        kundi Thing(metaclass=Meta):
            pita

        ukijumuisha self.assertRaises(AttributeError):
            inspect.getattr_static(Thing, "spam")
        self.assertUongo(Thing.executed)

kundi TestGetGeneratorState(unittest.TestCase):

    eleza setUp(self):
        eleza number_generator():
            kila number kwenye range(5):
                tuma number
        self.generator = number_generator()

    eleza _generatorstate(self):
        rudisha inspect.getgeneratorstate(self.generator)

    eleza test_created(self):
        self.assertEqual(self._generatorstate(), inspect.GEN_CREATED)

    eleza test_suspended(self):
        next(self.generator)
        self.assertEqual(self._generatorstate(), inspect.GEN_SUSPENDED)

    eleza test_closed_after_exhaustion(self):
        kila i kwenye self.generator:
            pita
        self.assertEqual(self._generatorstate(), inspect.GEN_CLOSED)

    eleza test_closed_after_immediate_exception(self):
        ukijumuisha self.assertRaises(RuntimeError):
            self.generator.throw(RuntimeError)
        self.assertEqual(self._generatorstate(), inspect.GEN_CLOSED)

    eleza test_running(self):
        # As mentioned on issue #10220, checking kila the RUNNING state only
        # makes sense inside the generator itself.
        # The following generator checks kila this by using the closure's
        # reference to self na the generator state checking helper method
        eleza running_check_generator():
            kila number kwenye range(5):
                self.assertEqual(self._generatorstate(), inspect.GEN_RUNNING)
                tuma number
                self.assertEqual(self._generatorstate(), inspect.GEN_RUNNING)
        self.generator = running_check_generator()
        # Running up to the first tuma
        next(self.generator)
        # Running after the first tuma
        next(self.generator)

    eleza test_easy_debugging(self):
        # repr() na str() of a generator state should contain the state name
        names = 'GEN_CREATED GEN_RUNNING GEN_SUSPENDED GEN_CLOSED'.split()
        kila name kwenye names:
            state = getattr(inspect, name)
            self.assertIn(name, repr(state))
            self.assertIn(name, str(state))

    eleza test_getgeneratorlocals(self):
        eleza each(lst, a=Tupu):
            b=(1, 2, 3)
            kila v kwenye lst:
                ikiwa v == 3:
                    c = 12
                tuma v

        numbers = each([1, 2, 3])
        self.assertEqual(inspect.getgeneratorlocals(numbers),
                         {'a': Tupu, 'lst': [1, 2, 3]})
        next(numbers)
        self.assertEqual(inspect.getgeneratorlocals(numbers),
                         {'a': Tupu, 'lst': [1, 2, 3], 'v': 1,
                          'b': (1, 2, 3)})
        next(numbers)
        self.assertEqual(inspect.getgeneratorlocals(numbers),
                         {'a': Tupu, 'lst': [1, 2, 3], 'v': 2,
                          'b': (1, 2, 3)})
        next(numbers)
        self.assertEqual(inspect.getgeneratorlocals(numbers),
                         {'a': Tupu, 'lst': [1, 2, 3], 'v': 3,
                          'b': (1, 2, 3), 'c': 12})
        jaribu:
            next(numbers)
        tatizo StopIteration:
            pita
        self.assertEqual(inspect.getgeneratorlocals(numbers), {})

    eleza test_getgeneratorlocals_empty(self):
        eleza tuma_one():
            tuma 1
        one = tuma_one()
        self.assertEqual(inspect.getgeneratorlocals(one), {})
        jaribu:
            next(one)
        tatizo StopIteration:
            pita
        self.assertEqual(inspect.getgeneratorlocals(one), {})

    eleza test_getgeneratorlocals_error(self):
        self.assertRaises(TypeError, inspect.getgeneratorlocals, 1)
        self.assertRaises(TypeError, inspect.getgeneratorlocals, lambda x: Kweli)
        self.assertRaises(TypeError, inspect.getgeneratorlocals, set)
        self.assertRaises(TypeError, inspect.getgeneratorlocals, (2,3))


kundi TestGetCoroutineState(unittest.TestCase):

    eleza setUp(self):
        @types.coroutine
        eleza number_coroutine():
            kila number kwenye range(5):
                tuma number
        async eleza coroutine():
            await number_coroutine()
        self.coroutine = coroutine()

    eleza tearDown(self):
        self.coroutine.close()

    eleza _coroutinestate(self):
        rudisha inspect.getcoroutinestate(self.coroutine)

    eleza test_created(self):
        self.assertEqual(self._coroutinestate(), inspect.CORO_CREATED)

    eleza test_suspended(self):
        self.coroutine.send(Tupu)
        self.assertEqual(self._coroutinestate(), inspect.CORO_SUSPENDED)

    eleza test_closed_after_exhaustion(self):
        wakati Kweli:
            jaribu:
                self.coroutine.send(Tupu)
            tatizo StopIteration:
                koma

        self.assertEqual(self._coroutinestate(), inspect.CORO_CLOSED)

    eleza test_closed_after_immediate_exception(self):
        ukijumuisha self.assertRaises(RuntimeError):
            self.coroutine.throw(RuntimeError)
        self.assertEqual(self._coroutinestate(), inspect.CORO_CLOSED)

    eleza test_easy_debugging(self):
        # repr() na str() of a coroutine state should contain the state name
        names = 'CORO_CREATED CORO_RUNNING CORO_SUSPENDED CORO_CLOSED'.split()
        kila name kwenye names:
            state = getattr(inspect, name)
            self.assertIn(name, repr(state))
            self.assertIn(name, str(state))

    eleza test_getcoroutinelocals(self):
        @types.coroutine
        eleza gencoro():
            tuma

        gencoro = gencoro()
        async eleza func(a=Tupu):
            b = 'spam'
            await gencoro

        coro = func()
        self.assertEqual(inspect.getcoroutinelocals(coro),
                         {'a': Tupu, 'gencoro': gencoro})
        coro.send(Tupu)
        self.assertEqual(inspect.getcoroutinelocals(coro),
                         {'a': Tupu, 'gencoro': gencoro, 'b': 'spam'})


kundi MySignature(inspect.Signature):
    # Top-level to make it picklable;
    # used kwenye test_signature_object_pickle
    pita

kundi MyParameter(inspect.Parameter):
    # Top-level to make it picklable;
    # used kwenye test_signature_object_pickle
    pita



kundi TestSignatureObject(unittest.TestCase):
    @staticmethod
    eleza signature(func, **kw):
        sig = inspect.signature(func, **kw)
        rudisha (tuple((param.name,
                       (... ikiwa param.default ni param.empty isipokua param.default),
                       (... ikiwa param.annotation ni param.empty
                                                        isipokua param.annotation),
                       str(param.kind).lower())
                                    kila param kwenye sig.parameters.values()),
                (... ikiwa sig.return_annotation ni sig.empty
                                            isipokua sig.return_annotation))

    eleza test_signature_object(self):
        S = inspect.Signature
        P = inspect.Parameter

        self.assertEqual(str(S()), '()')

        eleza test(po, pk, pod=42, pkd=100, *args, ko, **kwargs):
            pita
        sig = inspect.signature(test)
        po = sig.parameters['po'].replace(kind=P.POSITIONAL_ONLY)
        pod = sig.parameters['pod'].replace(kind=P.POSITIONAL_ONLY)
        pk = sig.parameters['pk']
        pkd = sig.parameters['pkd']
        args = sig.parameters['args']
        ko = sig.parameters['ko']
        kwargs = sig.parameters['kwargs']

        S((po, pk, args, ko, kwargs))

        ukijumuisha self.assertRaisesRegex(ValueError, 'wrong parameter order'):
            S((pk, po, args, ko, kwargs))

        ukijumuisha self.assertRaisesRegex(ValueError, 'wrong parameter order'):
            S((po, args, pk, ko, kwargs))

        ukijumuisha self.assertRaisesRegex(ValueError, 'wrong parameter order'):
            S((args, po, pk, ko, kwargs))

        ukijumuisha self.assertRaisesRegex(ValueError, 'wrong parameter order'):
            S((po, pk, args, kwargs, ko))

        kwargs2 = kwargs.replace(name='args')
        ukijumuisha self.assertRaisesRegex(ValueError, 'duplicate parameter name'):
            S((po, pk, args, kwargs2, ko))

        ukijumuisha self.assertRaisesRegex(ValueError, 'follows default argument'):
            S((pod, po))

        ukijumuisha self.assertRaisesRegex(ValueError, 'follows default argument'):
            S((po, pkd, pk))

        ukijumuisha self.assertRaisesRegex(ValueError, 'follows default argument'):
            S((pkd, pk))

        self.assertKweli(repr(sig).startswith('<Signature'))
        self.assertKweli('(po, pk' kwenye repr(sig))

    eleza test_signature_object_pickle(self):
        eleza foo(a, b, *, c:1={}, **kw) -> {42:'ham'}: pita
        foo_partial = functools.partial(foo, a=1)

        sig = inspect.signature(foo_partial)

        kila ver kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.subTest(pickle_ver=ver, subclass=Uongo):
                sig_pickled = pickle.loads(pickle.dumps(sig, ver))
                self.assertEqual(sig, sig_pickled)

        # Test that basic sub-classing works
        sig = inspect.signature(foo)
        myparam = MyParameter(name='z', kind=inspect.Parameter.POSITIONAL_ONLY)
        myparams = collections.OrderedDict(sig.parameters, a=myparam)
        mysig = MySignature().replace(parameters=myparams.values(),
                                      return_annotation=sig.return_annotation)
        self.assertKweli(isinstance(mysig, MySignature))
        self.assertKweli(isinstance(mysig.parameters['z'], MyParameter))

        kila ver kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.subTest(pickle_ver=ver, subclass=Kweli):
                sig_pickled = pickle.loads(pickle.dumps(mysig, ver))
                self.assertEqual(mysig, sig_pickled)
                self.assertKweli(isinstance(sig_pickled, MySignature))
                self.assertKweli(isinstance(sig_pickled.parameters['z'],
                                           MyParameter))

    eleza test_signature_immutability(self):
        eleza test(a):
            pita
        sig = inspect.signature(test)

        ukijumuisha self.assertRaises(AttributeError):
            sig.foo = 'bar'

        ukijumuisha self.assertRaises(TypeError):
            sig.parameters['a'] = Tupu

    eleza test_signature_on_noarg(self):
        eleza test():
            pita
        self.assertEqual(self.signature(test), ((), ...))

    eleza test_signature_on_wargs(self):
        eleza test(a, b:'foo') -> 123:
            pita
        self.assertEqual(self.signature(test),
                         ((('a', ..., ..., "positional_or_keyword"),
                           ('b', ..., 'foo', "positional_or_keyword")),
                          123))

    eleza test_signature_on_wkwonly(self):
        eleza test(*, a:float, b:str) -> int:
            pita
        self.assertEqual(self.signature(test),
                         ((('a', ..., float, "keyword_only"),
                           ('b', ..., str, "keyword_only")),
                           int))

    eleza test_signature_on_complex_args(self):
        eleza test(a, b:'foo'=10, *args:'bar', spam:'baz', ham=123, **kwargs:int):
            pita
        self.assertEqual(self.signature(test),
                         ((('a', ..., ..., "positional_or_keyword"),
                           ('b', 10, 'foo', "positional_or_keyword"),
                           ('args', ..., 'bar', "var_positional"),
                           ('spam', ..., 'baz', "keyword_only"),
                           ('ham', 123, ..., "keyword_only"),
                           ('kwargs', ..., int, "var_keyword")),
                          ...))

    eleza test_signature_without_self(self):
        eleza test_args_only(*args):  # NOQA
            pita

        eleza test_args_kwargs_only(*args, **kwargs):  # NOQA
            pita

        kundi A:
            @classmethod
            eleza test_classmethod(*args):  # NOQA
                pita

            @staticmethod
            eleza test_staticmethod(*args):  # NOQA
                pita

            f1 = functools.partialmethod((test_classmethod), 1)
            f2 = functools.partialmethod((test_args_only), 1)
            f3 = functools.partialmethod((test_staticmethod), 1)
            f4 = functools.partialmethod((test_args_kwargs_only),1)

        self.assertEqual(self.signature(test_args_only),
                         ((('args', ..., ..., 'var_positional'),), ...))
        self.assertEqual(self.signature(test_args_kwargs_only),
                         ((('args', ..., ..., 'var_positional'),
                           ('kwargs', ..., ..., 'var_keyword')), ...))
        self.assertEqual(self.signature(A.f1),
                         ((('args', ..., ..., 'var_positional'),), ...))
        self.assertEqual(self.signature(A.f2),
                         ((('args', ..., ..., 'var_positional'),), ...))
        self.assertEqual(self.signature(A.f3),
                         ((('args', ..., ..., 'var_positional'),), ...))
        self.assertEqual(self.signature(A.f4),
                         ((('args', ..., ..., 'var_positional'),
                            ('kwargs', ..., ..., 'var_keyword')), ...))
    @cpython_only
    @unittest.skipIf(MISSING_C_DOCSTRINGS,
                     "Signature information kila builtins requires docstrings")
    eleza test_signature_on_builtins(self):
        agiza _testcapi

        eleza test_unbound_method(o):
            """Use this to test unbound methods (things that should have a self)"""
            signature = inspect.signature(o)
            self.assertKweli(isinstance(signature, inspect.Signature))
            self.assertEqual(list(signature.parameters.values())[0].name, 'self')
            rudisha signature

        eleza test_callable(o):
            """Use this to test bound methods ama normal callables (things that don't expect self)"""
            signature = inspect.signature(o)
            self.assertKweli(isinstance(signature, inspect.Signature))
            ikiwa signature.parameters:
                self.assertNotEqual(list(signature.parameters.values())[0].name, 'self')
            rudisha signature

        signature = test_callable(_testcapi.docstring_with_signature_with_defaults)
        eleza p(name): rudisha signature.parameters[name].default
        self.assertEqual(p('s'), 'avocado')
        self.assertEqual(p('b'), b'bytes')
        self.assertEqual(p('d'), 3.14)
        self.assertEqual(p('i'), 35)
        self.assertEqual(p('n'), Tupu)
        self.assertEqual(p('t'), Kweli)
        self.assertEqual(p('f'), Uongo)
        self.assertEqual(p('local'), 3)
        self.assertEqual(p('sys'), sys.maxsize)
        self.assertNotIn('exp', signature.parameters)

        test_callable(object)

        # normal method
        # (PyMethodDescr_Type, "method_descriptor")
        test_unbound_method(_pickle.Pickler.dump)
        d = _pickle.Pickler(io.StringIO())
        test_callable(d.dump)

        # static method
        test_callable(bytes.maketrans)
        test_callable(b'abc'.maketrans)

        # kundi method
        test_callable(dict.fromkeys)
        test_callable({}.fromkeys)

        # wrapper around slot (PyWrapperDescr_Type, "wrapper_descriptor")
        test_unbound_method(type.__call__)
        test_unbound_method(int.__add__)
        test_callable((3).__add__)

        # _PyMethodWrapper_Type
        # support kila 'method-wrapper'
        test_callable(min.__call__)

        # This doesn't work now.
        # (We don't have a valid signature kila "type" kwenye 3.4)
        ukijumuisha self.assertRaisesRegex(ValueError, "no signature found"):
            kundi ThisWorksNow:
                __call__ = type
            test_callable(ThisWorksNow())

        # Regression test kila issue #20786
        test_unbound_method(dict.__delitem__)
        test_unbound_method(property.__delete__)

        # Regression test kila issue #20586
        test_callable(_testcapi.docstring_with_signature_but_no_doc)

    @cpython_only
    @unittest.skipIf(MISSING_C_DOCSTRINGS,
                     "Signature information kila builtins requires docstrings")
    eleza test_signature_on_decorated_builtins(self):
        agiza _testcapi
        func = _testcapi.docstring_with_signature_with_defaults

        eleza decorator(func):
            @functools.wraps(func)
            eleza wrapper(*args, **kwargs) -> int:
                rudisha func(*args, **kwargs)
            rudisha wrapper

        decorated_func = decorator(func)

        self.assertEqual(inspect.signature(func),
                         inspect.signature(decorated_func))

        eleza wrapper_like(*args, **kwargs) -> int: pita
        self.assertEqual(inspect.signature(decorated_func,
                                           follow_wrapped=Uongo),
                         inspect.signature(wrapper_like))

    @cpython_only
    eleza test_signature_on_builtins_no_signature(self):
        agiza _testcapi
        ukijumuisha self.assertRaisesRegex(ValueError,
                                    'no signature found kila builtin'):
            inspect.signature(_testcapi.docstring_no_signature)

        ukijumuisha self.assertRaisesRegex(ValueError,
                                    'no signature found kila builtin'):
            inspect.signature(str)

    eleza test_signature_on_non_function(self):
        ukijumuisha self.assertRaisesRegex(TypeError, 'is sio a callable object'):
            inspect.signature(42)

    eleza test_signature_from_functionlike_object(self):
        eleza func(a,b, *args, kwonly=Kweli, kwonlyreq, **kwargs):
            pita

        kundi funclike:
            # Has to be callable, na have correct
            # __code__, __annotations__, __defaults__, __name__,
            # na __kwdefaults__ attributes

            eleza __init__(self, func):
                self.__name__ = func.__name__
                self.__code__ = func.__code__
                self.__annotations__ = func.__annotations__
                self.__defaults__ = func.__defaults__
                self.__kwdefaults__ = func.__kwdefaults__
                self.func = func

            eleza __call__(self, *args, **kwargs):
                rudisha self.func(*args, **kwargs)

        sig_func = inspect.Signature.from_callable(func)

        sig_funclike = inspect.Signature.from_callable(funclike(func))
        self.assertEqual(sig_funclike, sig_func)

        sig_funclike = inspect.signature(funclike(func))
        self.assertEqual(sig_funclike, sig_func)

        # If object ni sio a duck type of function, then
        # signature will try to get a signature kila its '__call__'
        # method
        fl = funclike(func)
        toa fl.__defaults__
        self.assertEqual(self.signature(fl),
                         ((('args', ..., ..., "var_positional"),
                           ('kwargs', ..., ..., "var_keyword")),
                           ...))

        # Test ukijumuisha cython-like builtins:
        _orig_isdesc = inspect.ismethoddescriptor
        eleza _isdesc(obj):
            ikiwa hasattr(obj, '_builtinmock'):
                rudisha Kweli
            rudisha _orig_isdesc(obj)

        ukijumuisha unittest.mock.patch('inspect.ismethoddescriptor', _isdesc):
            builtin_func = funclike(func)
            # Make sure that our mock setup ni working
            self.assertUongo(inspect.ismethoddescriptor(builtin_func))
            builtin_func._builtinmock = Kweli
            self.assertKweli(inspect.ismethoddescriptor(builtin_func))
            self.assertEqual(inspect.signature(builtin_func), sig_func)

    eleza test_signature_functionlike_class(self):
        # We only want to duck type function-like objects,
        # sio classes.

        eleza func(a,b, *args, kwonly=Kweli, kwonlyreq, **kwargs):
            pita

        kundi funclike:
            eleza __init__(self, marker):
                pita

            __name__ = func.__name__
            __code__ = func.__code__
            __annotations__ = func.__annotations__
            __defaults__ = func.__defaults__
            __kwdefaults__ = func.__kwdefaults__

        self.assertEqual(str(inspect.signature(funclike)), '(marker)')

    eleza test_signature_on_method(self):
        kundi Test:
            eleza __init__(*args):
                pita
            eleza m1(self, arg1, arg2=1) -> int:
                pita
            eleza m2(*args):
                pita
            eleza __call__(*, a):
                pita

        self.assertEqual(self.signature(Test().m1),
                         ((('arg1', ..., ..., "positional_or_keyword"),
                           ('arg2', 1, ..., "positional_or_keyword")),
                          int))

        self.assertEqual(self.signature(Test().m2),
                         ((('args', ..., ..., "var_positional"),),
                          ...))

        self.assertEqual(self.signature(Test),
                         ((('args', ..., ..., "var_positional"),),
                          ...))

        ukijumuisha self.assertRaisesRegex(ValueError, 'invalid method signature'):
            self.signature(Test())

    eleza test_signature_wrapped_bound_method(self):
        # Issue 24298
        kundi Test:
            eleza m1(self, arg1, arg2=1) -> int:
                pita
        @functools.wraps(Test().m1)
        eleza m1d(*args, **kwargs):
            pita
        self.assertEqual(self.signature(m1d),
                         ((('arg1', ..., ..., "positional_or_keyword"),
                           ('arg2', 1, ..., "positional_or_keyword")),
                          int))

    eleza test_signature_on_classmethod(self):
        kundi Test:
            @classmethod
            eleza foo(cls, arg1, *, arg2=1):
                pita

        meth = Test().foo
        self.assertEqual(self.signature(meth),
                         ((('arg1', ..., ..., "positional_or_keyword"),
                           ('arg2', 1, ..., "keyword_only")),
                          ...))

        meth = Test.foo
        self.assertEqual(self.signature(meth),
                         ((('arg1', ..., ..., "positional_or_keyword"),
                           ('arg2', 1, ..., "keyword_only")),
                          ...))

    eleza test_signature_on_staticmethod(self):
        kundi Test:
            @staticmethod
            eleza foo(cls, *, arg):
                pita

        meth = Test().foo
        self.assertEqual(self.signature(meth),
                         ((('cls', ..., ..., "positional_or_keyword"),
                           ('arg', ..., ..., "keyword_only")),
                          ...))

        meth = Test.foo
        self.assertEqual(self.signature(meth),
                         ((('cls', ..., ..., "positional_or_keyword"),
                           ('arg', ..., ..., "keyword_only")),
                          ...))

    eleza test_signature_on_partial(self):
        kutoka functools agiza partial

        Parameter = inspect.Parameter

        eleza test():
            pita

        self.assertEqual(self.signature(partial(test)), ((), ...))

        ukijumuisha self.assertRaisesRegex(ValueError, "has incorrect arguments"):
            inspect.signature(partial(test, 1))

        ukijumuisha self.assertRaisesRegex(ValueError, "has incorrect arguments"):
            inspect.signature(partial(test, a=1))

        eleza test(a, b, *, c, d):
            pita

        self.assertEqual(self.signature(partial(test)),
                         ((('a', ..., ..., "positional_or_keyword"),
                           ('b', ..., ..., "positional_or_keyword"),
                           ('c', ..., ..., "keyword_only"),
                           ('d', ..., ..., "keyword_only")),
                          ...))

        self.assertEqual(self.signature(partial(test, 1)),
                         ((('b', ..., ..., "positional_or_keyword"),
                           ('c', ..., ..., "keyword_only"),
                           ('d', ..., ..., "keyword_only")),
                          ...))

        self.assertEqual(self.signature(partial(test, 1, c=2)),
                         ((('b', ..., ..., "positional_or_keyword"),
                           ('c', 2, ..., "keyword_only"),
                           ('d', ..., ..., "keyword_only")),
                          ...))

        self.assertEqual(self.signature(partial(test, b=1, c=2)),
                         ((('a', ..., ..., "positional_or_keyword"),
                           ('b', 1, ..., "keyword_only"),
                           ('c', 2, ..., "keyword_only"),
                           ('d', ..., ..., "keyword_only")),
                          ...))

        self.assertEqual(self.signature(partial(test, 0, b=1, c=2)),
                         ((('b', 1, ..., "keyword_only"),
                           ('c', 2, ..., "keyword_only"),
                           ('d', ..., ..., "keyword_only")),
                          ...))

        self.assertEqual(self.signature(partial(test, a=1)),
                         ((('a', 1, ..., "keyword_only"),
                           ('b', ..., ..., "keyword_only"),
                           ('c', ..., ..., "keyword_only"),
                           ('d', ..., ..., "keyword_only")),
                          ...))

        eleza test(a, *args, b, **kwargs):
            pita

        self.assertEqual(self.signature(partial(test, 1)),
                         ((('args', ..., ..., "var_positional"),
                           ('b', ..., ..., "keyword_only"),
                           ('kwargs', ..., ..., "var_keyword")),
                          ...))

        self.assertEqual(self.signature(partial(test, a=1)),
                         ((('a', 1, ..., "keyword_only"),
                           ('b', ..., ..., "keyword_only"),
                           ('kwargs', ..., ..., "var_keyword")),
                          ...))

        self.assertEqual(self.signature(partial(test, 1, 2, 3)),
                         ((('args', ..., ..., "var_positional"),
                           ('b', ..., ..., "keyword_only"),
                           ('kwargs', ..., ..., "var_keyword")),
                          ...))

        self.assertEqual(self.signature(partial(test, 1, 2, 3, test=Kweli)),
                         ((('args', ..., ..., "var_positional"),
                           ('b', ..., ..., "keyword_only"),
                           ('kwargs', ..., ..., "var_keyword")),
                          ...))

        self.assertEqual(self.signature(partial(test, 1, 2, 3, test=1, b=0)),
                         ((('args', ..., ..., "var_positional"),
                           ('b', 0, ..., "keyword_only"),
                           ('kwargs', ..., ..., "var_keyword")),
                          ...))

        self.assertEqual(self.signature(partial(test, b=0)),
                         ((('a', ..., ..., "positional_or_keyword"),
                           ('args', ..., ..., "var_positional"),
                           ('b', 0, ..., "keyword_only"),
                           ('kwargs', ..., ..., "var_keyword")),
                          ...))

        self.assertEqual(self.signature(partial(test, b=0, test=1)),
                         ((('a', ..., ..., "positional_or_keyword"),
                           ('args', ..., ..., "var_positional"),
                           ('b', 0, ..., "keyword_only"),
                           ('kwargs', ..., ..., "var_keyword")),
                          ...))

        eleza test(a, b, c:int) -> 42:
            pita

        sig = test.__signature__ = inspect.signature(test)

        self.assertEqual(self.signature(partial(partial(test, 1))),
                         ((('b', ..., ..., "positional_or_keyword"),
                           ('c', ..., int, "positional_or_keyword")),
                          42))

        self.assertEqual(self.signature(partial(partial(test, 1), 2)),
                         ((('c', ..., int, "positional_or_keyword"),),
                          42))

        psig = inspect.signature(partial(partial(test, 1), 2))

        eleza foo(a):
            rudisha a
        _foo = partial(partial(foo, a=10), a=20)
        self.assertEqual(self.signature(_foo),
                         ((('a', 20, ..., "keyword_only"),),
                          ...))
        # check that we don't have any side-effects kwenye signature(),
        # na the partial object ni still functioning
        self.assertEqual(_foo(), 20)

        eleza foo(a, b, c):
            rudisha a, b, c
        _foo = partial(partial(foo, 1, b=20), b=30)

        self.assertEqual(self.signature(_foo),
                         ((('b', 30, ..., "keyword_only"),
                           ('c', ..., ..., "keyword_only")),
                          ...))
        self.assertEqual(_foo(c=10), (1, 30, 10))

        eleza foo(a, b, c, *, d):
            rudisha a, b, c, d
        _foo = partial(partial(foo, d=20, c=20), b=10, d=30)
        self.assertEqual(self.signature(_foo),
                         ((('a', ..., ..., "positional_or_keyword"),
                           ('b', 10, ..., "keyword_only"),
                           ('c', 20, ..., "keyword_only"),
                           ('d', 30, ..., "keyword_only"),
                           ),
                          ...))
        ba = inspect.signature(_foo).bind(a=200, b=11)
        self.assertEqual(_foo(*ba.args, **ba.kwargs), (200, 11, 20, 30))

        eleza foo(a=1, b=2, c=3):
            rudisha a, b, c
        _foo = partial(foo, c=13) # (a=1, b=2, *, c=13)

        ba = inspect.signature(_foo).bind(a=11)
        self.assertEqual(_foo(*ba.args, **ba.kwargs), (11, 2, 13))

        ba = inspect.signature(_foo).bind(11, 12)
        self.assertEqual(_foo(*ba.args, **ba.kwargs), (11, 12, 13))

        ba = inspect.signature(_foo).bind(11, b=12)
        self.assertEqual(_foo(*ba.args, **ba.kwargs), (11, 12, 13))

        ba = inspect.signature(_foo).bind(b=12)
        self.assertEqual(_foo(*ba.args, **ba.kwargs), (1, 12, 13))

        _foo = partial(_foo, b=10, c=20)
        ba = inspect.signature(_foo).bind(12)
        self.assertEqual(_foo(*ba.args, **ba.kwargs), (12, 10, 20))


        eleza foo(a, b, c, d, **kwargs):
            pita
        sig = inspect.signature(foo)
        params = sig.parameters.copy()
        params['a'] = params['a'].replace(kind=Parameter.POSITIONAL_ONLY)
        params['b'] = params['b'].replace(kind=Parameter.POSITIONAL_ONLY)
        foo.__signature__ = inspect.Signature(params.values())
        sig = inspect.signature(foo)
        self.assertEqual(str(sig), '(a, b, /, c, d, **kwargs)')

        self.assertEqual(self.signature(partial(foo, 1)),
                         ((('b', ..., ..., 'positional_only'),
                           ('c', ..., ..., 'positional_or_keyword'),
                           ('d', ..., ..., 'positional_or_keyword'),
                           ('kwargs', ..., ..., 'var_keyword')),
                         ...))

        self.assertEqual(self.signature(partial(foo, 1, 2)),
                         ((('c', ..., ..., 'positional_or_keyword'),
                           ('d', ..., ..., 'positional_or_keyword'),
                           ('kwargs', ..., ..., 'var_keyword')),
                         ...))

        self.assertEqual(self.signature(partial(foo, 1, 2, 3)),
                         ((('d', ..., ..., 'positional_or_keyword'),
                           ('kwargs', ..., ..., 'var_keyword')),
                         ...))

        self.assertEqual(self.signature(partial(foo, 1, 2, c=3)),
                         ((('c', 3, ..., 'keyword_only'),
                           ('d', ..., ..., 'keyword_only'),
                           ('kwargs', ..., ..., 'var_keyword')),
                         ...))

        self.assertEqual(self.signature(partial(foo, 1, c=3)),
                         ((('b', ..., ..., 'positional_only'),
                           ('c', 3, ..., 'keyword_only'),
                           ('d', ..., ..., 'keyword_only'),
                           ('kwargs', ..., ..., 'var_keyword')),
                         ...))

    eleza test_signature_on_partialmethod(self):
        kutoka functools agiza partialmethod

        kundi Spam:
            eleza test():
                pita
            ham = partialmethod(test)

        ukijumuisha self.assertRaisesRegex(ValueError, "has incorrect arguments"):
            inspect.signature(Spam.ham)

        kundi Spam:
            eleza test(it, a, *, c) -> 'spam':
                pita
            ham = partialmethod(test, c=1)

        self.assertEqual(self.signature(Spam.ham),
                         ((('it', ..., ..., 'positional_or_keyword'),
                           ('a', ..., ..., 'positional_or_keyword'),
                           ('c', 1, ..., 'keyword_only')),
                          'spam'))

        self.assertEqual(self.signature(Spam().ham),
                         ((('a', ..., ..., 'positional_or_keyword'),
                           ('c', 1, ..., 'keyword_only')),
                          'spam'))

        kundi Spam:
            eleza test(self: 'anno', x):
                pita

            g = partialmethod(test, 1)

        self.assertEqual(self.signature(Spam.g),
                         ((('self', ..., 'anno', 'positional_or_keyword'),),
                          ...))

    eleza test_signature_on_fake_partialmethod(self):
        eleza foo(a): pita
        foo._partialmethod = 'spam'
        self.assertEqual(str(inspect.signature(foo)), '(a)')

    eleza test_signature_on_decorated(self):
        agiza functools

        eleza decorator(func):
            @functools.wraps(func)
            eleza wrapper(*args, **kwargs) -> int:
                rudisha func(*args, **kwargs)
            rudisha wrapper

        kundi Foo:
            @decorator
            eleza bar(self, a, b):
                pita

        self.assertEqual(self.signature(Foo.bar),
                         ((('self', ..., ..., "positional_or_keyword"),
                           ('a', ..., ..., "positional_or_keyword"),
                           ('b', ..., ..., "positional_or_keyword")),
                          ...))

        self.assertEqual(self.signature(Foo().bar),
                         ((('a', ..., ..., "positional_or_keyword"),
                           ('b', ..., ..., "positional_or_keyword")),
                          ...))

        self.assertEqual(self.signature(Foo.bar, follow_wrapped=Uongo),
                         ((('args', ..., ..., "var_positional"),
                           ('kwargs', ..., ..., "var_keyword")),
                          ...)) # functools.wraps will copy __annotations__
                                # kutoka "func" to "wrapper", hence no
                                # return_annotation

        # Test that we handle method wrappers correctly
        eleza decorator(func):
            @functools.wraps(func)
            eleza wrapper(*args, **kwargs) -> int:
                rudisha func(42, *args, **kwargs)
            sig = inspect.signature(func)
            new_params = tuple(sig.parameters.values())[1:]
            wrapper.__signature__ = sig.replace(parameters=new_params)
            rudisha wrapper

        kundi Foo:
            @decorator
            eleza __call__(self, a, b):
                pita

        self.assertEqual(self.signature(Foo.__call__),
                         ((('a', ..., ..., "positional_or_keyword"),
                           ('b', ..., ..., "positional_or_keyword")),
                          ...))

        self.assertEqual(self.signature(Foo().__call__),
                         ((('b', ..., ..., "positional_or_keyword"),),
                          ...))

        # Test we handle __signature__ partway down the wrapper stack
        eleza wrapped_foo_call():
            pita
        wrapped_foo_call.__wrapped__ = Foo.__call__

        self.assertEqual(self.signature(wrapped_foo_call),
                         ((('a', ..., ..., "positional_or_keyword"),
                           ('b', ..., ..., "positional_or_keyword")),
                          ...))


    eleza test_signature_on_class(self):
        kundi C:
            eleza __init__(self, a):
                pita

        self.assertEqual(self.signature(C),
                         ((('a', ..., ..., "positional_or_keyword"),),
                          ...))

        kundi CM(type):
            eleza __call__(cls, a):
                pita
        kundi C(metaclass=CM):
            eleza __init__(self, b):
                pita

        self.assertEqual(self.signature(C),
                         ((('a', ..., ..., "positional_or_keyword"),),
                          ...))

        kundi CM(type):
            eleza __new__(mcls, name, bases, dct, *, foo=1):
                rudisha super().__new__(mcls, name, bases, dct)
        kundi C(metaclass=CM):
            eleza __init__(self, b):
                pita

        self.assertEqual(self.signature(C),
                         ((('b', ..., ..., "positional_or_keyword"),),
                          ...))

        self.assertEqual(self.signature(CM),
                         ((('name', ..., ..., "positional_or_keyword"),
                           ('bases', ..., ..., "positional_or_keyword"),
                           ('dct', ..., ..., "positional_or_keyword"),
                           ('foo', 1, ..., "keyword_only")),
                          ...))

        kundi CMM(type):
            eleza __new__(mcls, name, bases, dct, *, foo=1):
                rudisha super().__new__(mcls, name, bases, dct)
            eleza __call__(cls, nm, bs, dt):
                rudisha type(nm, bs, dt)
        kundi CM(type, metaclass=CMM):
            eleza __new__(mcls, name, bases, dct, *, bar=2):
                rudisha super().__new__(mcls, name, bases, dct)
        kundi C(metaclass=CM):
            eleza __init__(self, b):
                pita

        self.assertEqual(self.signature(CMM),
                         ((('name', ..., ..., "positional_or_keyword"),
                           ('bases', ..., ..., "positional_or_keyword"),
                           ('dct', ..., ..., "positional_or_keyword"),
                           ('foo', 1, ..., "keyword_only")),
                          ...))

        self.assertEqual(self.signature(CM),
                         ((('nm', ..., ..., "positional_or_keyword"),
                           ('bs', ..., ..., "positional_or_keyword"),
                           ('dt', ..., ..., "positional_or_keyword")),
                          ...))

        self.assertEqual(self.signature(C),
                         ((('b', ..., ..., "positional_or_keyword"),),
                          ...))

        kundi CM(type):
            eleza __init__(cls, name, bases, dct, *, bar=2):
                rudisha super().__init__(name, bases, dct)
        kundi C(metaclass=CM):
            eleza __init__(self, b):
                pita

        self.assertEqual(self.signature(CM),
                         ((('name', ..., ..., "positional_or_keyword"),
                           ('bases', ..., ..., "positional_or_keyword"),
                           ('dct', ..., ..., "positional_or_keyword"),
                           ('bar', 2, ..., "keyword_only")),
                          ...))

    @unittest.skipIf(MISSING_C_DOCSTRINGS,
                     "Signature information kila builtins requires docstrings")
    eleza test_signature_on_class_without_init(self):
        # Test classes without user-defined __init__ ama __new__
        kundi C: pita
        self.assertEqual(str(inspect.signature(C)), '()')
        kundi D(C): pita
        self.assertEqual(str(inspect.signature(D)), '()')

        # Test meta-classes without user-defined __init__ ama __new__
        kundi C(type): pita
        kundi D(C): pita
        ukijumuisha self.assertRaisesRegex(ValueError, "callable.*is sio supported"):
            self.assertEqual(inspect.signature(C), Tupu)
        ukijumuisha self.assertRaisesRegex(ValueError, "callable.*is sio supported"):
            self.assertEqual(inspect.signature(D), Tupu)

    @unittest.skipIf(MISSING_C_DOCSTRINGS,
                     "Signature information kila builtins requires docstrings")
    eleza test_signature_on_builtin_class(self):
        expected = ('(file, protocol=Tupu, fix_imports=Kweli, '
                    'buffer_callback=Tupu)')
        self.assertEqual(str(inspect.signature(_pickle.Pickler)), expected)

        kundi P(_pickle.Pickler): pita
        kundi EmptyTrait: pita
        kundi P2(EmptyTrait, P): pita
        self.assertEqual(str(inspect.signature(P)), expected)
        self.assertEqual(str(inspect.signature(P2)), expected)

        kundi P3(P2):
            eleza __init__(self, spam):
                pita
        self.assertEqual(str(inspect.signature(P3)), '(spam)')

        kundi MetaP(type):
            eleza __call__(cls, foo, bar):
                pita
        kundi P4(P2, metaclass=MetaP):
            pita
        self.assertEqual(str(inspect.signature(P4)), '(foo, bar)')

    eleza test_signature_on_callable_objects(self):
        kundi Foo:
            eleza __call__(self, a):
                pita

        self.assertEqual(self.signature(Foo()),
                         ((('a', ..., ..., "positional_or_keyword"),),
                          ...))

        kundi Spam:
            pita
        ukijumuisha self.assertRaisesRegex(TypeError, "is sio a callable object"):
            inspect.signature(Spam())

        kundi Bar(Spam, Foo):
            pita

        self.assertEqual(self.signature(Bar()),
                         ((('a', ..., ..., "positional_or_keyword"),),
                          ...))

        kundi Wrapped:
            pita
        Wrapped.__wrapped__ = lambda a: Tupu
        self.assertEqual(self.signature(Wrapped),
                         ((('a', ..., ..., "positional_or_keyword"),),
                          ...))
        # wrapper loop:
        Wrapped.__wrapped__ = Wrapped
        ukijumuisha self.assertRaisesRegex(ValueError, 'wrapper loop'):
            self.signature(Wrapped)

    eleza test_signature_on_lambdas(self):
        self.assertEqual(self.signature((lambda a=10: a)),
                         ((('a', 10, ..., "positional_or_keyword"),),
                          ...))

    eleza test_signature_equality(self):
        eleza foo(a, *, b:int) -> float: pita
        self.assertUongo(inspect.signature(foo) == 42)
        self.assertKweli(inspect.signature(foo) != 42)
        self.assertKweli(inspect.signature(foo) == EqualsToAll())
        self.assertUongo(inspect.signature(foo) != EqualsToAll())

        eleza bar(a, *, b:int) -> float: pita
        self.assertKweli(inspect.signature(foo) == inspect.signature(bar))
        self.assertUongo(inspect.signature(foo) != inspect.signature(bar))
        self.assertEqual(
            hash(inspect.signature(foo)), hash(inspect.signature(bar)))

        eleza bar(a, *, b:int) -> int: pita
        self.assertUongo(inspect.signature(foo) == inspect.signature(bar))
        self.assertKweli(inspect.signature(foo) != inspect.signature(bar))
        self.assertNotEqual(
            hash(inspect.signature(foo)), hash(inspect.signature(bar)))

        eleza bar(a, *, b:int): pita
        self.assertUongo(inspect.signature(foo) == inspect.signature(bar))
        self.assertKweli(inspect.signature(foo) != inspect.signature(bar))
        self.assertNotEqual(
            hash(inspect.signature(foo)), hash(inspect.signature(bar)))

        eleza bar(a, *, b:int=42) -> float: pita
        self.assertUongo(inspect.signature(foo) == inspect.signature(bar))
        self.assertKweli(inspect.signature(foo) != inspect.signature(bar))
        self.assertNotEqual(
            hash(inspect.signature(foo)), hash(inspect.signature(bar)))

        eleza bar(a, *, c) -> float: pita
        self.assertUongo(inspect.signature(foo) == inspect.signature(bar))
        self.assertKweli(inspect.signature(foo) != inspect.signature(bar))
        self.assertNotEqual(
            hash(inspect.signature(foo)), hash(inspect.signature(bar)))

        eleza bar(a, b:int) -> float: pita
        self.assertUongo(inspect.signature(foo) == inspect.signature(bar))
        self.assertKweli(inspect.signature(foo) != inspect.signature(bar))
        self.assertNotEqual(
            hash(inspect.signature(foo)), hash(inspect.signature(bar)))
        eleza spam(b:int, a) -> float: pita
        self.assertUongo(inspect.signature(spam) == inspect.signature(bar))
        self.assertKweli(inspect.signature(spam) != inspect.signature(bar))
        self.assertNotEqual(
            hash(inspect.signature(spam)), hash(inspect.signature(bar)))

        eleza foo(*, a, b, c): pita
        eleza bar(*, c, b, a): pita
        self.assertKweli(inspect.signature(foo) == inspect.signature(bar))
        self.assertUongo(inspect.signature(foo) != inspect.signature(bar))
        self.assertEqual(
            hash(inspect.signature(foo)), hash(inspect.signature(bar)))

        eleza foo(*, a=1, b, c): pita
        eleza bar(*, c, b, a=1): pita
        self.assertKweli(inspect.signature(foo) == inspect.signature(bar))
        self.assertUongo(inspect.signature(foo) != inspect.signature(bar))
        self.assertEqual(
            hash(inspect.signature(foo)), hash(inspect.signature(bar)))

        eleza foo(pos, *, a=1, b, c): pita
        eleza bar(pos, *, c, b, a=1): pita
        self.assertKweli(inspect.signature(foo) == inspect.signature(bar))
        self.assertUongo(inspect.signature(foo) != inspect.signature(bar))
        self.assertEqual(
            hash(inspect.signature(foo)), hash(inspect.signature(bar)))

        eleza foo(pos, *, a, b, c): pita
        eleza bar(pos, *, c, b, a=1): pita
        self.assertUongo(inspect.signature(foo) == inspect.signature(bar))
        self.assertKweli(inspect.signature(foo) != inspect.signature(bar))
        self.assertNotEqual(
            hash(inspect.signature(foo)), hash(inspect.signature(bar)))

        eleza foo(pos, *args, a=42, b, c, **kwargs:int): pita
        eleza bar(pos, *args, c, b, a=42, **kwargs:int): pita
        self.assertKweli(inspect.signature(foo) == inspect.signature(bar))
        self.assertUongo(inspect.signature(foo) != inspect.signature(bar))
        self.assertEqual(
            hash(inspect.signature(foo)), hash(inspect.signature(bar)))

    eleza test_signature_hashable(self):
        S = inspect.Signature
        P = inspect.Parameter

        eleza foo(a): pita
        foo_sig = inspect.signature(foo)

        manual_sig = S(parameters=[P('a', P.POSITIONAL_OR_KEYWORD)])

        self.assertEqual(hash(foo_sig), hash(manual_sig))
        self.assertNotEqual(hash(foo_sig),
                            hash(manual_sig.replace(return_annotation='spam')))

        eleza bar(a) -> 1: pita
        self.assertNotEqual(hash(foo_sig), hash(inspect.signature(bar)))

        eleza foo(a={}): pita
        ukijumuisha self.assertRaisesRegex(TypeError, 'unhashable type'):
            hash(inspect.signature(foo))

        eleza foo(a) -> {}: pita
        ukijumuisha self.assertRaisesRegex(TypeError, 'unhashable type'):
            hash(inspect.signature(foo))

    eleza test_signature_str(self):
        eleza foo(a:int=1, *, b, c=Tupu, **kwargs) -> 42:
            pita
        self.assertEqual(str(inspect.signature(foo)),
                         '(a: int = 1, *, b, c=Tupu, **kwargs) -> 42')

        eleza foo(a:int=1, *args, b, c=Tupu, **kwargs) -> 42:
            pita
        self.assertEqual(str(inspect.signature(foo)),
                         '(a: int = 1, *args, b, c=Tupu, **kwargs) -> 42')

        eleza foo():
            pita
        self.assertEqual(str(inspect.signature(foo)), '()')

    eleza test_signature_str_positional_only(self):
        P = inspect.Parameter
        S = inspect.Signature

        eleza test(a_po, *, b, **kwargs):
            rudisha a_po, kwargs

        sig = inspect.signature(test)
        new_params = list(sig.parameters.values())
        new_params[0] = new_params[0].replace(kind=P.POSITIONAL_ONLY)
        test.__signature__ = sig.replace(parameters=new_params)

        self.assertEqual(str(inspect.signature(test)),
                         '(a_po, /, *, b, **kwargs)')

        self.assertEqual(str(S(parameters=[P('foo', P.POSITIONAL_ONLY)])),
                         '(foo, /)')

        self.assertEqual(str(S(parameters=[
                                P('foo', P.POSITIONAL_ONLY),
                                P('bar', P.VAR_KEYWORD)])),
                         '(foo, /, **bar)')

        self.assertEqual(str(S(parameters=[
                                P('foo', P.POSITIONAL_ONLY),
                                P('bar', P.VAR_POSITIONAL)])),
                         '(foo, /, *bar)')

    eleza test_signature_replace_anno(self):
        eleza test() -> 42:
            pita

        sig = inspect.signature(test)
        sig = sig.replace(return_annotation=Tupu)
        self.assertIs(sig.return_annotation, Tupu)
        sig = sig.replace(return_annotation=sig.empty)
        self.assertIs(sig.return_annotation, sig.empty)
        sig = sig.replace(return_annotation=42)
        self.assertEqual(sig.return_annotation, 42)
        self.assertEqual(sig, inspect.signature(test))

    eleza test_signature_on_mangled_parameters(self):
        kundi Spam:
            eleza foo(self, __p1:1=2, *, __p2:2=3):
                pita
        kundi Ham(Spam):
            pita

        self.assertEqual(self.signature(Spam.foo),
                         ((('self', ..., ..., "positional_or_keyword"),
                           ('_Spam__p1', 2, 1, "positional_or_keyword"),
                           ('_Spam__p2', 3, 2, "keyword_only")),
                          ...))

        self.assertEqual(self.signature(Spam.foo),
                         self.signature(Ham.foo))

    eleza test_signature_from_callable_python_obj(self):
        kundi MySignature(inspect.Signature): pita
        eleza foo(a, *, b:1): pita
        foo_sig = MySignature.from_callable(foo)
        self.assertIsInstance(foo_sig, MySignature)

    eleza test_signature_from_callable_class(self):
        # A regression test kila a kundi inheriting its signature kutoka `object`.
        kundi MySignature(inspect.Signature): pita
        kundi foo: pita
        foo_sig = MySignature.from_callable(foo)
        self.assertIsInstance(foo_sig, MySignature)

    @unittest.skipIf(MISSING_C_DOCSTRINGS,
                     "Signature information kila builtins requires docstrings")
    eleza test_signature_from_callable_builtin_obj(self):
        kundi MySignature(inspect.Signature): pita
        sig = MySignature.from_callable(_pickle.Pickler)
        self.assertIsInstance(sig, MySignature)

    eleza test_signature_definition_order_preserved_on_kwonly(self):
        kila fn kwenye signatures_with_lexicographic_keyword_only_parameters():
            signature = inspect.signature(fn)
            l = list(signature.parameters)
            sorted_l = sorted(l)
            self.assertKweli(l)
            self.assertEqual(l, sorted_l)
        signature = inspect.signature(unsorted_keyword_only_parameters_fn)
        l = list(signature.parameters)
        self.assertEqual(l, unsorted_keyword_only_parameters)


kundi TestParameterObject(unittest.TestCase):
    eleza test_signature_parameter_kinds(self):
        P = inspect.Parameter
        self.assertKweli(P.POSITIONAL_ONLY < P.POSITIONAL_OR_KEYWORD < \
                        P.VAR_POSITIONAL < P.KEYWORD_ONLY < P.VAR_KEYWORD)

        self.assertEqual(str(P.POSITIONAL_ONLY), 'POSITIONAL_ONLY')
        self.assertKweli('POSITIONAL_ONLY' kwenye repr(P.POSITIONAL_ONLY))

    eleza test_signature_parameter_object(self):
        p = inspect.Parameter('foo', default=10,
                              kind=inspect.Parameter.POSITIONAL_ONLY)
        self.assertEqual(p.name, 'foo')
        self.assertEqual(p.default, 10)
        self.assertIs(p.annotation, p.empty)
        self.assertEqual(p.kind, inspect.Parameter.POSITIONAL_ONLY)

        ukijumuisha self.assertRaisesRegex(ValueError, "value '123' ni "
                                    "sio a valid Parameter.kind"):
            inspect.Parameter('foo', default=10, kind='123')

        ukijumuisha self.assertRaisesRegex(ValueError, 'sio a valid parameter name'):
            inspect.Parameter('1', kind=inspect.Parameter.VAR_KEYWORD)

        ukijumuisha self.assertRaisesRegex(TypeError, 'name must be a str'):
            inspect.Parameter(Tupu, kind=inspect.Parameter.VAR_KEYWORD)

        ukijumuisha self.assertRaisesRegex(ValueError,
                                    'is sio a valid parameter name'):
            inspect.Parameter('$', kind=inspect.Parameter.VAR_KEYWORD)

        ukijumuisha self.assertRaisesRegex(ValueError,
                                    'is sio a valid parameter name'):
            inspect.Parameter('.a', kind=inspect.Parameter.VAR_KEYWORD)

        ukijumuisha self.assertRaisesRegex(ValueError, 'cannot have default values'):
            inspect.Parameter('a', default=42,
                              kind=inspect.Parameter.VAR_KEYWORD)

        ukijumuisha self.assertRaisesRegex(ValueError, 'cannot have default values'):
            inspect.Parameter('a', default=42,
                              kind=inspect.Parameter.VAR_POSITIONAL)

        p = inspect.Parameter('a', default=42,
                              kind=inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ukijumuisha self.assertRaisesRegex(ValueError, 'cannot have default values'):
            p.replace(kind=inspect.Parameter.VAR_POSITIONAL)

        self.assertKweli(repr(p).startswith('<Parameter'))
        self.assertKweli('"a=42"' kwenye repr(p))

    eleza test_signature_parameter_hashable(self):
        P = inspect.Parameter
        foo = P('foo', kind=P.POSITIONAL_ONLY)
        self.assertEqual(hash(foo), hash(P('foo', kind=P.POSITIONAL_ONLY)))
        self.assertNotEqual(hash(foo), hash(P('foo', kind=P.POSITIONAL_ONLY,
                                              default=42)))
        self.assertNotEqual(hash(foo),
                            hash(foo.replace(kind=P.VAR_POSITIONAL)))

    eleza test_signature_parameter_equality(self):
        P = inspect.Parameter
        p = P('foo', default=42, kind=inspect.Parameter.KEYWORD_ONLY)

        self.assertKweli(p == p)
        self.assertUongo(p != p)
        self.assertUongo(p == 42)
        self.assertKweli(p != 42)
        self.assertKweli(p == EqualsToAll())
        self.assertUongo(p != EqualsToAll())

        self.assertKweli(p == P('foo', default=42,
                               kind=inspect.Parameter.KEYWORD_ONLY))
        self.assertUongo(p != P('foo', default=42,
                                kind=inspect.Parameter.KEYWORD_ONLY))

    eleza test_signature_parameter_replace(self):
        p = inspect.Parameter('foo', default=42,
                              kind=inspect.Parameter.KEYWORD_ONLY)

        self.assertIsNot(p, p.replace())
        self.assertEqual(p, p.replace())

        p2 = p.replace(annotation=1)
        self.assertEqual(p2.annotation, 1)
        p2 = p2.replace(annotation=p2.empty)
        self.assertEqual(p, p2)

        p2 = p2.replace(name='bar')
        self.assertEqual(p2.name, 'bar')
        self.assertNotEqual(p2, p)

        ukijumuisha self.assertRaisesRegex(ValueError,
                                    'name ni a required attribute'):
            p2 = p2.replace(name=p2.empty)

        p2 = p2.replace(name='foo', default=Tupu)
        self.assertIs(p2.default, Tupu)
        self.assertNotEqual(p2, p)

        p2 = p2.replace(name='foo', default=p2.empty)
        self.assertIs(p2.default, p2.empty)


        p2 = p2.replace(default=42, kind=p2.POSITIONAL_OR_KEYWORD)
        self.assertEqual(p2.kind, p2.POSITIONAL_OR_KEYWORD)
        self.assertNotEqual(p2, p)

        ukijumuisha self.assertRaisesRegex(ValueError,
                                    "value <kundi 'inspect._empty'> "
                                    "is sio a valid Parameter.kind"):
            p2 = p2.replace(kind=p2.empty)

        p2 = p2.replace(kind=p2.KEYWORD_ONLY)
        self.assertEqual(p2, p)

    eleza test_signature_parameter_positional_only(self):
        ukijumuisha self.assertRaisesRegex(TypeError, 'name must be a str'):
            inspect.Parameter(Tupu, kind=inspect.Parameter.POSITIONAL_ONLY)

    @cpython_only
    eleza test_signature_parameter_implicit(self):
        ukijumuisha self.assertRaisesRegex(ValueError,
                                    'implicit arguments must be pitaed kama '
                                    'positional ama keyword arguments, '
                                    'sio positional-only'):
            inspect.Parameter('.0', kind=inspect.Parameter.POSITIONAL_ONLY)

        param = inspect.Parameter(
            '.0', kind=inspect.Parameter.POSITIONAL_OR_KEYWORD)
        self.assertEqual(param.kind, inspect.Parameter.POSITIONAL_ONLY)
        self.assertEqual(param.name, 'implicit0')

    eleza test_signature_parameter_immutability(self):
        p = inspect.Parameter('spam', kind=inspect.Parameter.KEYWORD_ONLY)

        ukijumuisha self.assertRaises(AttributeError):
            p.foo = 'bar'

        ukijumuisha self.assertRaises(AttributeError):
            p.kind = 123


kundi TestSignatureBind(unittest.TestCase):
    @staticmethod
    eleza call(func, *args, **kwargs):
        sig = inspect.signature(func)
        ba = sig.bind(*args, **kwargs)
        rudisha func(*ba.args, **ba.kwargs)

    eleza test_signature_bind_empty(self):
        eleza test():
            rudisha 42

        self.assertEqual(self.call(test), 42)
        ukijumuisha self.assertRaisesRegex(TypeError, 'too many positional arguments'):
            self.call(test, 1)
        ukijumuisha self.assertRaisesRegex(TypeError, 'too many positional arguments'):
            self.call(test, 1, spam=10)
        ukijumuisha self.assertRaisesRegex(
            TypeError, "got an unexpected keyword argument 'spam'"):

            self.call(test, spam=1)

    eleza test_signature_bind_var(self):
        eleza test(*args, **kwargs):
            rudisha args, kwargs

        self.assertEqual(self.call(test), ((), {}))
        self.assertEqual(self.call(test, 1), ((1,), {}))
        self.assertEqual(self.call(test, 1, 2), ((1, 2), {}))
        self.assertEqual(self.call(test, foo='bar'), ((), {'foo': 'bar'}))
        self.assertEqual(self.call(test, 1, foo='bar'), ((1,), {'foo': 'bar'}))
        self.assertEqual(self.call(test, args=10), ((), {'args': 10}))
        self.assertEqual(self.call(test, 1, 2, foo='bar'),
                         ((1, 2), {'foo': 'bar'}))

    eleza test_signature_bind_just_args(self):
        eleza test(a, b, c):
            rudisha a, b, c

        self.assertEqual(self.call(test, 1, 2, 3), (1, 2, 3))

        ukijumuisha self.assertRaisesRegex(TypeError, 'too many positional arguments'):
            self.call(test, 1, 2, 3, 4)

        ukijumuisha self.assertRaisesRegex(TypeError,
                                    "missing a required argument: 'b'"):
            self.call(test, 1)

        ukijumuisha self.assertRaisesRegex(TypeError,
                                    "missing a required argument: 'a'"):
            self.call(test)

        eleza test(a, b, c=10):
            rudisha a, b, c
        self.assertEqual(self.call(test, 1, 2, 3), (1, 2, 3))
        self.assertEqual(self.call(test, 1, 2), (1, 2, 10))

        eleza test(a=1, b=2, c=3):
            rudisha a, b, c
        self.assertEqual(self.call(test, a=10, c=13), (10, 2, 13))
        self.assertEqual(self.call(test, a=10), (10, 2, 3))
        self.assertEqual(self.call(test, b=10), (1, 10, 3))

    eleza test_signature_bind_varargs_order(self):
        eleza test(*args):
            rudisha args

        self.assertEqual(self.call(test), ())
        self.assertEqual(self.call(test, 1, 2, 3), (1, 2, 3))

    eleza test_signature_bind_args_and_varargs(self):
        eleza test(a, b, c=3, *args):
            rudisha a, b, c, args

        self.assertEqual(self.call(test, 1, 2, 3, 4, 5), (1, 2, 3, (4, 5)))
        self.assertEqual(self.call(test, 1, 2), (1, 2, 3, ()))
        self.assertEqual(self.call(test, b=1, a=2), (2, 1, 3, ()))
        self.assertEqual(self.call(test, 1, b=2), (1, 2, 3, ()))

        ukijumuisha self.assertRaisesRegex(TypeError,
                                     "multiple values kila argument 'c'"):
            self.call(test, 1, 2, 3, c=4)

    eleza test_signature_bind_just_kwargs(self):
        eleza test(**kwargs):
            rudisha kwargs

        self.assertEqual(self.call(test), {})
        self.assertEqual(self.call(test, foo='bar', spam='ham'),
                         {'foo': 'bar', 'spam': 'ham'})

    eleza test_signature_bind_args_and_kwargs(self):
        eleza test(a, b, c=3, **kwargs):
            rudisha a, b, c, kwargs

        self.assertEqual(self.call(test, 1, 2), (1, 2, 3, {}))
        self.assertEqual(self.call(test, 1, 2, foo='bar', spam='ham'),
                         (1, 2, 3, {'foo': 'bar', 'spam': 'ham'}))
        self.assertEqual(self.call(test, b=2, a=1, foo='bar', spam='ham'),
                         (1, 2, 3, {'foo': 'bar', 'spam': 'ham'}))
        self.assertEqual(self.call(test, a=1, b=2, foo='bar', spam='ham'),
                         (1, 2, 3, {'foo': 'bar', 'spam': 'ham'}))
        self.assertEqual(self.call(test, 1, b=2, foo='bar', spam='ham'),
                         (1, 2, 3, {'foo': 'bar', 'spam': 'ham'}))
        self.assertEqual(self.call(test, 1, b=2, c=4, foo='bar', spam='ham'),
                         (1, 2, 4, {'foo': 'bar', 'spam': 'ham'}))
        self.assertEqual(self.call(test, 1, 2, 4, foo='bar'),
                         (1, 2, 4, {'foo': 'bar'}))
        self.assertEqual(self.call(test, c=5, a=4, b=3),
                         (4, 3, 5, {}))

    eleza test_signature_bind_kwonly(self):
        eleza test(*, foo):
            rudisha foo
        ukijumuisha self.assertRaisesRegex(TypeError,
                                     'too many positional arguments'):
            self.call(test, 1)
        self.assertEqual(self.call(test, foo=1), 1)

        eleza test(a, *, foo=1, bar):
            rudisha foo
        ukijumuisha self.assertRaisesRegex(TypeError,
                                     "missing a required argument: 'bar'"):
            self.call(test, 1)

        eleza test(foo, *, bar):
            rudisha foo, bar
        self.assertEqual(self.call(test, 1, bar=2), (1, 2))
        self.assertEqual(self.call(test, bar=2, foo=1), (1, 2))

        ukijumuisha self.assertRaisesRegex(
            TypeError, "got an unexpected keyword argument 'spam'"):

            self.call(test, bar=2, foo=1, spam=10)

        ukijumuisha self.assertRaisesRegex(TypeError,
                                     'too many positional arguments'):
            self.call(test, 1, 2)

        ukijumuisha self.assertRaisesRegex(TypeError,
                                     'too many positional arguments'):
            self.call(test, 1, 2, bar=2)

        ukijumuisha self.assertRaisesRegex(
            TypeError, "got an unexpected keyword argument 'spam'"):

            self.call(test, 1, bar=2, spam='ham')

        ukijumuisha self.assertRaisesRegex(TypeError,
                                     "missing a required argument: 'bar'"):
            self.call(test, 1)

        eleza test(foo, *, bar, **bin):
            rudisha foo, bar, bin
        self.assertEqual(self.call(test, 1, bar=2), (1, 2, {}))
        self.assertEqual(self.call(test, foo=1, bar=2), (1, 2, {}))
        self.assertEqual(self.call(test, 1, bar=2, spam='ham'),
                         (1, 2, {'spam': 'ham'}))
        self.assertEqual(self.call(test, spam='ham', foo=1, bar=2),
                         (1, 2, {'spam': 'ham'}))
        ukijumuisha self.assertRaisesRegex(TypeError,
                                    "missing a required argument: 'foo'"):
            self.call(test, spam='ham', bar=2)
        self.assertEqual(self.call(test, 1, bar=2, bin=1, spam=10),
                         (1, 2, {'bin': 1, 'spam': 10}))

    eleza test_signature_bind_arguments(self):
        eleza test(a, *args, b, z=100, **kwargs):
            pita
        sig = inspect.signature(test)
        ba = sig.bind(10, 20, b=30, c=40, args=50, kwargs=60)
        # we won't have 'z' argument kwenye the bound arguments object, kama we didn't
        # pita it to the 'bind'
        self.assertEqual(tuple(ba.arguments.items()),
                         (('a', 10), ('args', (20,)), ('b', 30),
                          ('kwargs', {'c': 40, 'args': 50, 'kwargs': 60})))
        self.assertEqual(ba.kwargs,
                         {'b': 30, 'c': 40, 'args': 50, 'kwargs': 60})
        self.assertEqual(ba.args, (10, 20))

    eleza test_signature_bind_positional_only(self):
        P = inspect.Parameter

        eleza test(a_po, b_po, c_po=3, foo=42, *, bar=50, **kwargs):
            rudisha a_po, b_po, c_po, foo, bar, kwargs

        sig = inspect.signature(test)
        new_params = collections.OrderedDict(tuple(sig.parameters.items()))
        kila name kwenye ('a_po', 'b_po', 'c_po'):
            new_params[name] = new_params[name].replace(kind=P.POSITIONAL_ONLY)
        new_sig = sig.replace(parameters=new_params.values())
        test.__signature__ = new_sig

        self.assertEqual(self.call(test, 1, 2, 4, 5, bar=6),
                         (1, 2, 4, 5, 6, {}))

        self.assertEqual(self.call(test, 1, 2),
                         (1, 2, 3, 42, 50, {}))

        self.assertEqual(self.call(test, 1, 2, foo=4, bar=5),
                         (1, 2, 3, 4, 5, {}))

        ukijumuisha self.assertRaisesRegex(TypeError, "but was pitaed kama a keyword"):
            self.call(test, 1, 2, foo=4, bar=5, c_po=10)

        ukijumuisha self.assertRaisesRegex(TypeError, "parameter ni positional only"):
            self.call(test, 1, 2, c_po=4)

        ukijumuisha self.assertRaisesRegex(TypeError, "parameter ni positional only"):
            self.call(test, a_po=1, b_po=2)

    eleza test_signature_bind_with_self_arg(self):
        # Issue #17071: one of the parameters ni named "self
        eleza test(a, self, b):
            pita
        sig = inspect.signature(test)
        ba = sig.bind(1, 2, 3)
        self.assertEqual(ba.args, (1, 2, 3))
        ba = sig.bind(1, self=2, b=3)
        self.assertEqual(ba.args, (1, 2, 3))

    eleza test_signature_bind_vararg_name(self):
        eleza test(a, *args):
            rudisha a, args
        sig = inspect.signature(test)

        ukijumuisha self.assertRaisesRegex(
            TypeError, "got an unexpected keyword argument 'args'"):

            sig.bind(a=0, args=1)

        eleza test(*args, **kwargs):
            rudisha args, kwargs
        self.assertEqual(self.call(test, args=1), ((), {'args': 1}))

        sig = inspect.signature(test)
        ba = sig.bind(args=1)
        self.assertEqual(ba.arguments, {'kwargs': {'args': 1}})

    @cpython_only
    eleza test_signature_bind_implicit_arg(self):
        # Issue #19611: getcallargs should work ukijumuisha set comprehensions
        eleza make_set():
            rudisha {z * z kila z kwenye range(5)}
        setcomp_code = make_set.__code__.co_consts[1]
        setcomp_func = types.FunctionType(setcomp_code, {})

        iterator = iter(range(5))
        self.assertEqual(self.call(setcomp_func, iterator), {0, 1, 4, 9, 16})


kundi TestBoundArguments(unittest.TestCase):
    eleza test_signature_bound_arguments_unhashable(self):
        eleza foo(a): pita
        ba = inspect.signature(foo).bind(1)

        ukijumuisha self.assertRaisesRegex(TypeError, 'unhashable type'):
            hash(ba)

    eleza test_signature_bound_arguments_equality(self):
        eleza foo(a): pita
        ba = inspect.signature(foo).bind(1)
        self.assertKweli(ba == ba)
        self.assertUongo(ba != ba)
        self.assertKweli(ba == EqualsToAll())
        self.assertUongo(ba != EqualsToAll())

        ba2 = inspect.signature(foo).bind(1)
        self.assertKweli(ba == ba2)
        self.assertUongo(ba != ba2)

        ba3 = inspect.signature(foo).bind(2)
        self.assertUongo(ba == ba3)
        self.assertKweli(ba != ba3)
        ba3.arguments['a'] = 1
        self.assertKweli(ba == ba3)
        self.assertUongo(ba != ba3)

        eleza bar(b): pita
        ba4 = inspect.signature(bar).bind(1)
        self.assertUongo(ba == ba4)
        self.assertKweli(ba != ba4)

        eleza foo(*, a, b): pita
        sig = inspect.signature(foo)
        ba1 = sig.bind(a=1, b=2)
        ba2 = sig.bind(b=2, a=1)
        self.assertKweli(ba1 == ba2)
        self.assertUongo(ba1 != ba2)

    eleza test_signature_bound_arguments_pickle(self):
        eleza foo(a, b, *, c:1={}, **kw) -> {42:'ham'}: pita
        sig = inspect.signature(foo)
        ba = sig.bind(20, 30, z={})

        kila ver kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.subTest(pickle_ver=ver):
                ba_pickled = pickle.loads(pickle.dumps(ba, ver))
                self.assertEqual(ba, ba_pickled)

    eleza test_signature_bound_arguments_repr(self):
        eleza foo(a, b, *, c:1={}, **kw) -> {42:'ham'}: pita
        sig = inspect.signature(foo)
        ba = sig.bind(20, 30, z={})
        self.assertRegex(repr(ba), r'<BoundArguments \(a=20,.*\}\}\)>')

    eleza test_signature_bound_arguments_apply_defaults(self):
        eleza foo(a, b=1, *args, c:1={}, **kw): pita
        sig = inspect.signature(foo)

        ba = sig.bind(20)
        ba.apply_defaults()
        self.assertEqual(
            list(ba.arguments.items()),
            [('a', 20), ('b', 1), ('args', ()), ('c', {}), ('kw', {})])

        # Make sure that we preserve the order:
        # i.e. 'c' should be *before* 'kw'.
        ba = sig.bind(10, 20, 30, d=1)
        ba.apply_defaults()
        self.assertEqual(
            list(ba.arguments.items()),
            [('a', 10), ('b', 20), ('args', (30,)), ('c', {}), ('kw', {'d':1})])

        # Make sure that BoundArguments produced by bind_partial()
        # are supported.
        eleza foo(a, b): pita
        sig = inspect.signature(foo)
        ba = sig.bind_partial(20)
        ba.apply_defaults()
        self.assertEqual(
            list(ba.arguments.items()),
            [('a', 20)])

        # Test no args
        eleza foo(): pita
        sig = inspect.signature(foo)
        ba = sig.bind()
        ba.apply_defaults()
        self.assertEqual(list(ba.arguments.items()), [])

        # Make sure a no-args binding still acquires proper defaults.
        eleza foo(a='spam'): pita
        sig = inspect.signature(foo)
        ba = sig.bind()
        ba.apply_defaults()
        self.assertEqual(list(ba.arguments.items()), [('a', 'spam')])


kundi TestSignaturePrivateHelpers(unittest.TestCase):
    eleza test_signature_get_bound_param(self):
        getter = inspect._signature_get_bound_param

        self.assertEqual(getter('($self)'), 'self')
        self.assertEqual(getter('($self, obj)'), 'self')
        self.assertEqual(getter('($cls, /, obj)'), 'cls')

    eleza _strip_non_python_syntax(self, input,
        clean_signature, self_parameter, last_positional_only):
        computed_clean_signature, \
            computed_self_parameter, \
            computed_last_positional_only = \
            inspect._signature_strip_non_python_syntax(input)
        self.assertEqual(computed_clean_signature, clean_signature)
        self.assertEqual(computed_self_parameter, self_parameter)
        self.assertEqual(computed_last_positional_only, last_positional_only)

    eleza test_signature_strip_non_python_syntax(self):
        self._strip_non_python_syntax(
            "($module, /, path, mode, *, dir_fd=Tupu, " +
                "effective_ids=Uongo,\n       follow_symlinks=Kweli)",
            "(module, path, mode, *, dir_fd=Tupu, " +
                "effective_ids=Uongo, follow_symlinks=Kweli)",
            0,
            0)

        self._strip_non_python_syntax(
            "($module, word, salt, /)",
            "(module, word, salt)",
            0,
            2)

        self._strip_non_python_syntax(
            "(x, y=Tupu, z=Tupu, /)",
            "(x, y=Tupu, z=Tupu)",
            Tupu,
            2)

        self._strip_non_python_syntax(
            "(x, y=Tupu, z=Tupu)",
            "(x, y=Tupu, z=Tupu)",
            Tupu,
            Tupu)

        self._strip_non_python_syntax(
            "(x,\n    y=Tupu,\n      z = Tupu  )",
            "(x, y=Tupu, z=Tupu)",
            Tupu,
            Tupu)

        self._strip_non_python_syntax(
            "",
            "",
            Tupu,
            Tupu)

        self._strip_non_python_syntax(
            Tupu,
            Tupu,
            Tupu,
            Tupu)

kundi TestSignatureDefinitions(unittest.TestCase):
    # This test case provides a home kila checking that particular APIs
    # have signatures available kila introspection

    @cpython_only
    @unittest.skipIf(MISSING_C_DOCSTRINGS,
                     "Signature information kila builtins requires docstrings")
    eleza test_builtins_have_signatures(self):
        # This checks all builtin callables kwenye CPython have signatures
        # A few have signatures Signature can't yet handle, so we skip those
        # since they will have to wait until PEP 457 adds the required
        # introspection support to the inspect module
        # Some others also haven't been converted yet kila various other
        # reasons, so we also skip those kila the time being, but design
        # the test to fail kwenye order to indicate when it needs to be
        # updated.
        no_signature = set()
        # These need PEP 457 groups
        needs_groups = {"range", "slice", "dir", "getattr",
                        "next", "iter", "vars"}
        no_signature |= needs_groups
        # These need PEP 457 groups ama a signature change to accept Tupu
        needs_semantic_update = {"round"}
        no_signature |= needs_semantic_update
        # These need *args support kwenye Argument Clinic
        needs_varargs = {"komapoint", "min", "max", "print",
                         "__build_class__"}
        no_signature |= needs_varargs
        # These simply weren't covered kwenye the initial AC conversion
        # kila builtin callables
        not_converted_yet = {"open", "__import__"}
        no_signature |= not_converted_yet
        # These builtin types are expected to provide introspection info
        types_with_signatures = set()
        # Check the signatures we expect to be there
        ns = vars(builtins)
        kila name, obj kwenye sorted(ns.items()):
            ikiwa sio callable(obj):
                endelea
            # The builtin types haven't been converted to AC yet
            ikiwa isinstance(obj, type) na (name haiko kwenye types_with_signatures):
                # Note that this also skips all the exception types
                no_signature.add(name)
            ikiwa (name kwenye no_signature):
                # Not yet converted
                endelea
            ukijumuisha self.subTest(builtin=name):
                self.assertIsNotTupu(inspect.signature(obj))
        # Check callables that haven't been converted don't claim a signature
        # This ensures this test will start failing kama more signatures are
        # added, so the affected items can be moved into the scope of the
        # regression test above
        kila name kwenye no_signature:
            ukijumuisha self.subTest(builtin=name):
                self.assertIsTupu(obj.__text_signature__)

    eleza test_python_function_override_signature(self):
        eleza func(*args, **kwargs):
            pita
        func.__text_signature__ = '($self, a, b=1, *args, c, d=2, **kwargs)'
        sig = inspect.signature(func)
        self.assertIsNotTupu(sig)
        self.assertEqual(str(sig), '(self, /, a, b=1, *args, c, d=2, **kwargs)')
        func.__text_signature__ = '($self, a, b=1, /, *args, c, d=2, **kwargs)'
        sig = inspect.signature(func)
        self.assertEqual(str(sig), '(self, a, b=1, /, *args, c, d=2, **kwargs)')


kundi NTimesUnwrappable:
    eleza __init__(self, n):
        self.n = n
        self._next = Tupu

    @property
    eleza __wrapped__(self):
        ikiwa self.n <= 0:
            ashiria Exception("Unwrapped too many times")
        ikiwa self._next ni Tupu:
            self._next = NTimesUnwrappable(self.n - 1)
        rudisha self._next

kundi TestUnwrap(unittest.TestCase):

    eleza test_unwrap_one(self):
        eleza func(a, b):
            rudisha a + b
        wrapper = functools.lru_cache(maxsize=20)(func)
        self.assertIs(inspect.unwrap(wrapper), func)

    eleza test_unwrap_several(self):
        eleza func(a, b):
            rudisha a + b
        wrapper = func
        kila __ kwenye range(10):
            @functools.wraps(wrapper)
            eleza wrapper():
                pita
        self.assertIsNot(wrapper.__wrapped__, func)
        self.assertIs(inspect.unwrap(wrapper), func)

    eleza test_stop(self):
        eleza func1(a, b):
            rudisha a + b
        @functools.wraps(func1)
        eleza func2():
            pita
        @functools.wraps(func2)
        eleza wrapper():
            pita
        func2.stop_here = 1
        unwrapped = inspect.unwrap(wrapper,
                                   stop=(lambda f: hasattr(f, "stop_here")))
        self.assertIs(unwrapped, func2)

    eleza test_cycle(self):
        eleza func1(): pita
        func1.__wrapped__ = func1
        ukijumuisha self.assertRaisesRegex(ValueError, 'wrapper loop'):
            inspect.unwrap(func1)

        eleza func2(): pita
        func2.__wrapped__ = func1
        func1.__wrapped__ = func2
        ukijumuisha self.assertRaisesRegex(ValueError, 'wrapper loop'):
            inspect.unwrap(func1)
        ukijumuisha self.assertRaisesRegex(ValueError, 'wrapper loop'):
            inspect.unwrap(func2)

    eleza test_unhashable(self):
        eleza func(): pita
        func.__wrapped__ = Tupu
        kundi C:
            __hash__ = Tupu
            __wrapped__ = func
        self.assertIsTupu(inspect.unwrap(C()))

    eleza test_recursion_limit(self):
        obj = NTimesUnwrappable(sys.getrecursionlimit() + 1)
        ukijumuisha self.assertRaisesRegex(ValueError, 'wrapper loop'):
            inspect.unwrap(obj)

kundi TestMain(unittest.TestCase):
    eleza test_only_source(self):
        module = importlib.import_module('unittest')
        rc, out, err = assert_python_ok('-m', 'inspect',
                                        'unittest')
        lines = out.decode().splitlines()
        # ignore the final newline
        self.assertEqual(lines[:-1], inspect.getsource(module).splitlines())
        self.assertEqual(err, b'')

    eleza test_custom_getattr(self):
        eleza foo():
            pita
        foo.__signature__ = 42
        ukijumuisha self.assertRaises(TypeError):
            inspect.signature(foo)

    @unittest.skipIf(ThreadPoolExecutor ni Tupu,
            'threads required to test __qualname__ kila source files')
    eleza test_qualname_source(self):
        rc, out, err = assert_python_ok('-m', 'inspect',
                                     'concurrent.futures:ThreadPoolExecutor')
        lines = out.decode().splitlines()
        # ignore the final newline
        self.assertEqual(lines[:-1],
                         inspect.getsource(ThreadPoolExecutor).splitlines())
        self.assertEqual(err, b'')

    eleza test_builtins(self):
        module = importlib.import_module('unittest')
        _, out, err = assert_python_failure('-m', 'inspect',
                                            'sys')
        lines = err.decode().splitlines()
        self.assertEqual(lines, ["Can't get info kila builtin modules."])

    eleza test_details(self):
        module = importlib.import_module('unittest')
        args = support.optim_args_from_interpreter_flags()
        rc, out, err = assert_python_ok(*args, '-m', 'inspect',
                                        'unittest', '--details')
        output = out.decode()
        # Just a quick sanity check on the output
        self.assertIn(module.__name__, output)
        self.assertIn(module.__file__, output)
        self.assertIn(module.__cached__, output)
        self.assertEqual(err, b'')


kundi TestReload(unittest.TestCase):

    src_before = textwrap.dedent("""\
eleza foo():
    andika("Bla")
    """)

    src_after = textwrap.dedent("""\
eleza foo():
    andika("Oh no!")
    """)

    eleza assertInspectEqual(self, path, source):
        inspected_src = inspect.getsource(source)
        ukijumuisha open(path) kama src:
            self.assertEqual(
                src.read().splitlines(Kweli),
                inspected_src.splitlines(Kweli)
            )

    eleza test_getsource_reload(self):
        # see issue 1218234
        ukijumuisha _ready_to_import('reload_bug', self.src_before) kama (name, path):
            module = importlib.import_module(name)
            self.assertInspectEqual(path, module)
            ukijumuisha open(path, 'w') kama src:
                src.write(self.src_after)
            self.assertInspectEqual(path, module)


eleza test_main():
    run_unittest(
        TestDecorators, TestRetrievingSourceCode, TestOneliners, TestBuggyCases,
        TestInterpreterStack, TestClassesAndFunctions, TestPredicates,
        TestGetcallargsFunctions, TestGetcallargsMethods,
        TestGetcallargsUnboundMethods, TestGetattrStatic, TestGetGeneratorState,
        TestNoEOL, TestSignatureObject, TestSignatureBind, TestParameterObject,
        TestBoundArguments, TestSignaturePrivateHelpers,
        TestSignatureDefinitions, TestIsDataDescriptor,
        TestGetClosureVars, TestUnwrap, TestMain, TestReload,
        TestGetCoroutineState, TestGettingSourceOfToplevelFrames
    )

ikiwa __name__ == "__main__":
    test_main()
