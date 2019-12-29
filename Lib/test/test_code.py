"""This module includes tests of the code object representation.

>>> eleza f(x):
...     eleza g(y):
...         rudisha x + y
...     rudisha g
...

>>> dump(f.__code__)
name: f
argcount: 1
posonlyargcount: 0
kwonlyargcount: 0
names: ()
varnames: ('x', 'g')
cellvars: ('x',)
freevars: ()
nlocals: 2
flags: 3
consts: ('Tupu', '<code object g>', "'f.<locals>.g'")

>>> dump(f(4).__code__)
name: g
argcount: 1
posonlyargcount: 0
kwonlyargcount: 0
names: ()
varnames: ('y',)
cellvars: ()
freevars: ('x',)
nlocals: 1
flags: 19
consts: ('Tupu',)

>>> eleza h(x, y):
...     a = x + y
...     b = x - y
...     c = a * b
...     rudisha c
...

>>> dump(h.__code__)
name: h
argcount: 2
posonlyargcount: 0
kwonlyargcount: 0
names: ()
varnames: ('x', 'y', 'a', 'b', 'c')
cellvars: ()
freevars: ()
nlocals: 5
flags: 67
consts: ('Tupu',)

>>> eleza attrs(obj):
...     andika(obj.attr1)
...     andika(obj.attr2)
...     andika(obj.attr3)

>>> dump(attrs.__code__)
name: attrs
argcount: 1
posonlyargcount: 0
kwonlyargcount: 0
names: ('print', 'attr1', 'attr2', 'attr3')
varnames: ('obj',)
cellvars: ()
freevars: ()
nlocals: 1
flags: 67
consts: ('Tupu',)

>>> eleza optimize_away():
...     'doc string'
...     'not a docstring'
...     53
...     0x53

>>> dump(optimize_away.__code__)
name: optimize_away
argcount: 0
posonlyargcount: 0
kwonlyargcount: 0
names: ()
varnames: ()
cellvars: ()
freevars: ()
nlocals: 0
flags: 67
consts: ("'doc string'", 'Tupu')

>>> eleza keywordonly_args(a,b,*,k1):
...     rudisha a,b,k1
...

>>> dump(keywordonly_args.__code__)
name: keywordonly_args
argcount: 2
posonlyargcount: 0
kwonlyargcount: 1
names: ()
varnames: ('a', 'b', 'k1')
cellvars: ()
freevars: ()
nlocals: 3
flags: 67
consts: ('Tupu',)

>>> eleza posonly_args(a,b,/,c):
...     rudisha a,b,c
...

>>> dump(posonly_args.__code__)
name: posonly_args
argcount: 3
posonlyargcount: 2
kwonlyargcount: 0
names: ()
varnames: ('a', 'b', 'c')
cellvars: ()
freevars: ()
nlocals: 3
flags: 67
consts: ('Tupu',)

"""

agiza inspect
agiza sys
agiza threading
agiza unittest
agiza weakref
agiza opcode
jaribu:
    agiza ctypes
tatizo ImportError:
    ctypes = Tupu
kutoka test.support agiza (run_doctest, run_unittest, cpython_only,
                          check_impl_detail)


eleza consts(t):
    """Yield a doctest-safe sequence of object reprs."""
    kila elt kwenye t:
        r = repr(elt)
        ikiwa r.startswith("<code object"):
            tuma "<code object %s>" % elt.co_name
        isipokua:
            tuma r

eleza dump(co):
    """Print out a text representation of a code object."""
    kila attr kwenye ["name", "argcount", "posonlyargcount",
                 "kwonlyargcount", "names", "varnames",
                 "cellvars", "freevars", "nlocals", "flags"]:
        andika("%s: %s" % (attr, getattr(co, "co_" + attr)))
    andika("consts:", tuple(consts(co.co_consts)))

# Needed kila test_closure_injection below
# Defined at global scope to avoid implicitly closing over __class__
eleza external_getitem(self, i):
    rudisha f"Foreign getitem: {super().__getitem__(i)}"

kundi CodeTest(unittest.TestCase):

    @cpython_only
    eleza test_newempty(self):
        agiza _testcapi
        co = _testcapi.code_newempty("filename", "funcname", 15)
        self.assertEqual(co.co_filename, "filename")
        self.assertEqual(co.co_name, "funcname")
        self.assertEqual(co.co_firstlineno, 15)

    @cpython_only
    eleza test_closure_injection(self):
        # From https://bugs.python.org/issue32176
        kutoka types agiza FunctionType

        eleza create_closure(__class__):
            rudisha (lambda: __class__).__closure__

        eleza new_code(c):
            '''A new code object ukijumuisha a __class__ cell added to freevars'''
            rudisha c.replace(co_freevars=c.co_freevars + ('__class__',))

        eleza add_foreign_method(cls, name, f):
            code = new_code(f.__code__)
            assert sio f.__closure__
            closure = create_closure(cls)
            defaults = f.__defaults__
            setattr(cls, name, FunctionType(code, globals(), name, defaults, closure))

        kundi List(list):
            pita

        add_foreign_method(List, "__getitem__", external_getitem)

        # Ensure the closure injection actually worked
        function = List.__getitem__
        class_ref = function.__closure__[0].cell_contents
        self.assertIs(class_ref, List)

        # Ensure the code correctly indicates it accesses a free variable
        self.assertUongo(function.__code__.co_flags & inspect.CO_NOFREE,
                         hex(function.__code__.co_flags))

        # Ensure the zero-arg super() call kwenye the injected method works
        obj = List([1, 2, 3])
        self.assertEqual(obj[0], "Foreign getitem: 1")

    eleza test_constructor(self):
        eleza func(): pita
        co = func.__code__
        CodeType = type(co)

        # test code constructor
        rudisha CodeType(co.co_argcount,
                        co.co_posonlyargcount,
                        co.co_kwonlyargcount,
                        co.co_nlocals,
                        co.co_stacksize,
                        co.co_flags,
                        co.co_code,
                        co.co_consts,
                        co.co_names,
                        co.co_varnames,
                        co.co_filename,
                        co.co_name,
                        co.co_firstlineno,
                        co.co_lnotab,
                        co.co_freevars,
                        co.co_cellvars)

    eleza test_replace(self):
        eleza func():
            x = 1
            rudisha x
        code = func.__code__

        # different co_name, co_varnames, co_consts
        eleza func2():
            y = 2
            rudisha y
        code2 = func.__code__

        kila attr, value kwenye (
            ("co_argcount", 0),
            ("co_posonlyargcount", 0),
            ("co_kwonlyargcount", 0),
            ("co_nlocals", 0),
            ("co_stacksize", 0),
            ("co_flags", code.co_flags | inspect.CO_COROUTINE),
            ("co_firstlineno", 100),
            ("co_code", code2.co_code),
            ("co_consts", code2.co_consts),
            ("co_names", ("myname",)),
            ("co_varnames", code2.co_varnames),
            ("co_freevars", ("freevar",)),
            ("co_cellvars", ("cellvar",)),
            ("co_filename", "newfilename"),
            ("co_name", "newname"),
            ("co_lnotab", code2.co_lnotab),
        ):
            ukijumuisha self.subTest(attr=attr, value=value):
                new_code = code.replace(**{attr: value})
                self.assertEqual(getattr(new_code, attr), value)


eleza isinterned(s):
    rudisha s ni sys.intern(('_' + s + '_')[1:-1])

kundi CodeConstsTest(unittest.TestCase):

    eleza find_const(self, consts, value):
        kila v kwenye consts:
            ikiwa v == value:
                rudisha v
        self.assertIn(value, consts)  # ashirias an exception
        self.fail('Should never be reached')

    eleza assertIsInterned(self, s):
        ikiwa sio isinterned(s):
            self.fail('String %r ni sio interned' % (s,))

    eleza assertIsNotInterned(self, s):
        ikiwa isinterned(s):
            self.fail('String %r ni interned' % (s,))

    @cpython_only
    eleza test_interned_string(self):
        co = compile('res = "str_value"', '?', 'exec')
        v = self.find_const(co.co_consts, 'str_value')
        self.assertIsInterned(v)

    @cpython_only
    eleza test_interned_string_in_tuple(self):
        co = compile('res = ("str_value",)', '?', 'exec')
        v = self.find_const(co.co_consts, ('str_value',))
        self.assertIsInterned(v[0])

    @cpython_only
    eleza test_interned_string_in_frozenset(self):
        co = compile('res = a kwenye {"str_value"}', '?', 'exec')
        v = self.find_const(co.co_consts, frozenset(('str_value',)))
        self.assertIsInterned(tuple(v)[0])

    @cpython_only
    eleza test_interned_string_default(self):
        eleza f(a='str_value'):
            rudisha a
        self.assertIsInterned(f())

    @cpython_only
    eleza test_interned_string_with_null(self):
        co = compile(r'res = "str\0value!"', '?', 'exec')
        v = self.find_const(co.co_consts, 'str\0value!')
        self.assertIsNotInterned(v)


kundi CodeWeakRefTest(unittest.TestCase):

    eleza test_basic(self):
        # Create a code object kwenye a clean environment so that we know we have
        # the only reference to it left.
        namespace = {}
        exec("eleza f(): pita", globals(), namespace)
        f = namespace["f"]
        toa namespace

        self.called = Uongo
        eleza callback(code):
            self.called = Kweli

        # f ni now the last reference to the function, na through it, the code
        # object.  While we hold it, check that we can create a weakref and
        # deref it.  Then delete it, na check that the callback gets called and
        # the reference dies.
        coderef = weakref.ref(f.__code__, callback)
        self.assertKweli(bool(coderef()))
        toa f
        self.assertUongo(bool(coderef()))
        self.assertKweli(self.called)


ikiwa check_impl_detail(cpython=Kweli) na ctypes ni sio Tupu:
    py = ctypes.pythonapi
    freefunc = ctypes.CFUNCTYPE(Tupu,ctypes.c_voidp)

    RequestCodeExtraIndex = py._PyEval_RequestCodeExtraIndex
    RequestCodeExtraIndex.argtypes = (freefunc,)
    RequestCodeExtraIndex.restype = ctypes.c_ssize_t

    SetExtra = py._PyCode_SetExtra
    SetExtra.argtypes = (ctypes.py_object, ctypes.c_ssize_t, ctypes.c_voidp)
    SetExtra.restype = ctypes.c_int

    GetExtra = py._PyCode_GetExtra
    GetExtra.argtypes = (ctypes.py_object, ctypes.c_ssize_t,
                         ctypes.POINTER(ctypes.c_voidp))
    GetExtra.restype = ctypes.c_int

    LAST_FREED = Tupu
    eleza myfree(ptr):
        global LAST_FREED
        LAST_FREED = ptr

    FREE_FUNC = freefunc(myfree)
    FREE_INDEX = RequestCodeExtraIndex(FREE_FUNC)

    kundi CoExtra(unittest.TestCase):
        eleza get_func(self):
            # Defining a function causes the containing function to have a
            # reference to the code object.  We need the code objects to go
            # away, so we eval a lambda.
            rudisha eval('lambda:42')

        eleza test_get_non_code(self):
            f = self.get_func()

            self.assertRaises(SystemError, SetExtra, 42, FREE_INDEX,
                              ctypes.c_voidp(100))
            self.assertRaises(SystemError, GetExtra, 42, FREE_INDEX,
                              ctypes.c_voidp(100))

        eleza test_bad_index(self):
            f = self.get_func()
            self.assertRaises(SystemError, SetExtra, f.__code__,
                              FREE_INDEX+100, ctypes.c_voidp(100))
            self.assertEqual(GetExtra(f.__code__, FREE_INDEX+100,
                              ctypes.c_voidp(100)), 0)

        eleza test_free_called(self):
            # Verify that the provided free function gets invoked
            # when the code object ni cleaned up.
            f = self.get_func()

            SetExtra(f.__code__, FREE_INDEX, ctypes.c_voidp(100))
            toa f
            self.assertEqual(LAST_FREED, 100)

        eleza test_get_set(self):
            # Test basic get/set round tripping.
            f = self.get_func()

            extra = ctypes.c_voidp()

            SetExtra(f.__code__, FREE_INDEX, ctypes.c_voidp(200))
            # reset should free...
            SetExtra(f.__code__, FREE_INDEX, ctypes.c_voidp(300))
            self.assertEqual(LAST_FREED, 200)

            extra = ctypes.c_voidp()
            GetExtra(f.__code__, FREE_INDEX, extra)
            self.assertEqual(extra.value, 300)
            toa f

        eleza test_free_different_thread(self):
            # Freeing a code object on a different thread then
            # where the co_extra was set should be safe.
            f = self.get_func()
            kundi ThreadTest(threading.Thread):
                eleza __init__(self, f, test):
                    super().__init__()
                    self.f = f
                    self.test = test
                eleza run(self):
                    toa self.f
                    self.test.assertEqual(LAST_FREED, 500)

            SetExtra(f.__code__, FREE_INDEX, ctypes.c_voidp(500))
            tt = ThreadTest(f, self)
            toa f
            tt.start()
            tt.join()
            self.assertEqual(LAST_FREED, 500)

        @cpython_only
        eleza test_clean_stack_on_rudisha(self):

            eleza f(x):
                rudisha x

            code = f.__code__
            ct = type(f.__code__)

            # Insert an extra LOAD_FAST, this duplicates the value of
            # 'x' kwenye the stack, leaking it ikiwa the frame ni sio properly
            # cleaned up upon exit.

            bytecode = list(code.co_code)
            bytecode.insert(-2, opcode.opmap['LOAD_FAST'])
            bytecode.insert(-2, 0)

            c = ct(code.co_argcount, code.co_posonlyargcount,
                   code.co_kwonlyargcount, code.co_nlocals, code.co_stacksize+1,
                   code.co_flags, bytes(bytecode),
                   code.co_consts, code.co_names, code.co_varnames,
                   code.co_filename, code.co_name, code.co_firstlineno,
                   code.co_lnotab, code.co_freevars, code.co_cellvars)
            new_function = type(f)(c, f.__globals__, 'nf', f.__defaults__, f.__closure__)

            kundi Var:
                pita
            the_object = Var()
            var = weakref.ref(the_object)

            new_function(the_object)

            # Check ikiwa the_object ni leaked
            toa the_object
            assert var() ni Tupu


eleza test_main(verbose=Tupu):
    kutoka test agiza test_code
    run_doctest(test_code, verbose)
    tests = [CodeTest, CodeConstsTest, CodeWeakRefTest]
    ikiwa check_impl_detail(cpython=Kweli) na ctypes ni sio Tupu:
        tests.append(CoExtra)
    run_unittest(*tests)

ikiwa __name__ == "__main__":
    test_main()
