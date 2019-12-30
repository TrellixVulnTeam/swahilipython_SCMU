agiza abc
agiza builtins
agiza collections
agiza collections.abc
agiza copy
kutoka itertools agiza permutations
agiza pickle
kutoka random agiza choice
agiza sys
kutoka test agiza support
agiza threading
agiza time
agiza typing
agiza unittest
agiza unittest.mock
kutoka weakref agiza proxy
agiza contextlib

agiza functools

py_functools = support.import_fresh_module('functools', blocked=['_functools'])
c_functools = support.import_fresh_module('functools', fresh=['_functools'])

decimal = support.import_fresh_module('decimal', fresh=['_decimal'])

@contextlib.contextmanager
eleza replaced_module(name, replacement):
    original_module = sys.modules[name]
    sys.modules[name] = replacement
    jaribu:
        tuma
    mwishowe:
        sys.modules[name] = original_module

eleza capture(*args, **kw):
    """capture all positional na keyword arguments"""
    rudisha args, kw


eleza signature(part):
    """ rudisha the signature of a partial object """
    rudisha (part.func, part.args, part.keywords, part.__dict__)

kundi MyTuple(tuple):
    pita

kundi BadTuple(tuple):
    eleza __add__(self, other):
        rudisha list(self) + list(other)

kundi MyDict(dict):
    pita


kundi TestPartial:

    eleza test_basic_examples(self):
        p = self.partial(capture, 1, 2, a=10, b=20)
        self.assertKweli(callable(p))
        self.assertEqual(p(3, 4, b=30, c=40),
                         ((1, 2, 3, 4), dict(a=10, b=30, c=40)))
        p = self.partial(map, lambda x: x*10)
        self.assertEqual(list(p([1,2,3,4])), [10, 20, 30, 40])

    eleza test_attributes(self):
        p = self.partial(capture, 1, 2, a=10, b=20)
        # attributes should be readable
        self.assertEqual(p.func, capture)
        self.assertEqual(p.args, (1, 2))
        self.assertEqual(p.keywords, dict(a=10, b=20))

    eleza test_argument_checking(self):
        self.assertRaises(TypeError, self.partial)     # need at least a func arg
        jaribu:
            self.partial(2)()
        tatizo TypeError:
            pita
        isipokua:
            self.fail('First arg sio checked kila callability')

    eleza test_protection_of_callers_dict_argument(self):
        # a caller's dictionary should sio be altered by partial
        eleza func(a=10, b=20):
            rudisha a
        d = {'a':3}
        p = self.partial(func, a=5)
        self.assertEqual(p(**d), 3)
        self.assertEqual(d, {'a':3})
        p(b=7)
        self.assertEqual(d, {'a':3})

    eleza test_kwargs_copy(self):
        # Issue #29532: Altering a kwarg dictionary pitaed to a constructor
        # should sio affect a partial object after creation
        d = {'a': 3}
        p = self.partial(capture, **d)
        self.assertEqual(p(), ((), {'a': 3}))
        d['a'] = 5
        self.assertEqual(p(), ((), {'a': 3}))

    eleza test_arg_combinations(self):
        # exercise special code paths kila zero args kwenye either partial
        # object ama the caller
        p = self.partial(capture)
        self.assertEqual(p(), ((), {}))
        self.assertEqual(p(1,2), ((1,2), {}))
        p = self.partial(capture, 1, 2)
        self.assertEqual(p(), ((1,2), {}))
        self.assertEqual(p(3,4), ((1,2,3,4), {}))

    eleza test_kw_combinations(self):
        # exercise special code paths kila no keyword args in
        # either the partial object ama the caller
        p = self.partial(capture)
        self.assertEqual(p.keywords, {})
        self.assertEqual(p(), ((), {}))
        self.assertEqual(p(a=1), ((), {'a':1}))
        p = self.partial(capture, a=1)
        self.assertEqual(p.keywords, {'a':1})
        self.assertEqual(p(), ((), {'a':1}))
        self.assertEqual(p(b=2), ((), {'a':1, 'b':2}))
        # keyword args kwenye the call override those kwenye the partial object
        self.assertEqual(p(a=3, b=2), ((), {'a':3, 'b':2}))

    eleza test_positional(self):
        # make sure positional arguments are captured correctly
        kila args kwenye [(), (0,), (0,1), (0,1,2), (0,1,2,3)]:
            p = self.partial(capture, *args)
            expected = args + ('x',)
            got, empty = p('x')
            self.assertKweli(expected == got na empty == {})

    eleza test_keyword(self):
        # make sure keyword arguments are captured correctly
        kila a kwenye ['a', 0, Tupu, 3.5]:
            p = self.partial(capture, a=a)
            expected = {'a':a,'x':Tupu}
            empty, got = p(x=Tupu)
            self.assertKweli(expected == got na empty == ())

    eleza test_no_side_effects(self):
        # make sure there are no side effects that affect subsequent calls
        p = self.partial(capture, 0, a=1)
        args1, kw1 = p(1, b=2)
        self.assertKweli(args1 == (0,1) na kw1 == {'a':1,'b':2})
        args2, kw2 = p()
        self.assertKweli(args2 == (0,) na kw2 == {'a':1})

    eleza test_error_propagation(self):
        eleza f(x, y):
            x / y
        self.assertRaises(ZeroDivisionError, self.partial(f, 1, 0))
        self.assertRaises(ZeroDivisionError, self.partial(f, 1), 0)
        self.assertRaises(ZeroDivisionError, self.partial(f), 1, 0)
        self.assertRaises(ZeroDivisionError, self.partial(f, y=0), 1)

    eleza test_weakref(self):
        f = self.partial(int, base=16)
        p = proxy(f)
        self.assertEqual(f.func, p.func)
        f = Tupu
        self.assertRaises(ReferenceError, getattr, p, 'func')

    eleza test_with_bound_and_unbound_methods(self):
        data = list(map(str, range(10)))
        join = self.partial(str.join, '')
        self.assertEqual(join(data), '0123456789')
        join = self.partial(''.join)
        self.assertEqual(join(data), '0123456789')

    eleza test_nested_optimization(self):
        partial = self.partial
        inner = partial(signature, 'asdf')
        nested = partial(inner, bar=Kweli)
        flat = partial(signature, 'asdf', bar=Kweli)
        self.assertEqual(signature(nested), signature(flat))

    eleza test_nested_partial_with_attribute(self):
        # see issue 25137
        partial = self.partial

        eleza foo(bar):
            rudisha bar

        p = partial(foo, 'first')
        p2 = partial(p, 'second')
        p2.new_attr = 'spam'
        self.assertEqual(p2.new_attr, 'spam')

    eleza test_repr(self):
        args = (object(), object())
        args_repr = ', '.join(repr(a) kila a kwenye args)
        kwargs = {'a': object(), 'b': object()}
        kwargs_reprs = ['a={a!r}, b={b!r}'.format_map(kwargs),
                        'b={b!r}, a={a!r}'.format_map(kwargs)]
        ikiwa self.partial kwenye (c_functools.partial, py_functools.partial):
            name = 'functools.partial'
        isipokua:
            name = self.partial.__name__

        f = self.partial(capture)
        self.assertEqual(f'{name}({capture!r})', repr(f))

        f = self.partial(capture, *args)
        self.assertEqual(f'{name}({capture!r}, {args_repr})', repr(f))

        f = self.partial(capture, **kwargs)
        self.assertIn(repr(f),
                      [f'{name}({capture!r}, {kwargs_repr})'
                       kila kwargs_repr kwenye kwargs_reprs])

        f = self.partial(capture, *args, **kwargs)
        self.assertIn(repr(f),
                      [f'{name}({capture!r}, {args_repr}, {kwargs_repr})'
                       kila kwargs_repr kwenye kwargs_reprs])

    eleza test_recursive_repr(self):
        ikiwa self.partial kwenye (c_functools.partial, py_functools.partial):
            name = 'functools.partial'
        isipokua:
            name = self.partial.__name__

        f = self.partial(capture)
        f.__setstate__((f, (), {}, {}))
        jaribu:
            self.assertEqual(repr(f), '%s(...)' % (name,))
        mwishowe:
            f.__setstate__((capture, (), {}, {}))

        f = self.partial(capture)
        f.__setstate__((capture, (f,), {}, {}))
        jaribu:
            self.assertEqual(repr(f), '%s(%r, ...)' % (name, capture,))
        mwishowe:
            f.__setstate__((capture, (), {}, {}))

        f = self.partial(capture)
        f.__setstate__((capture, (), {'a': f}, {}))
        jaribu:
            self.assertEqual(repr(f), '%s(%r, a=...)' % (name, capture,))
        mwishowe:
            f.__setstate__((capture, (), {}, {}))

    eleza test_pickle(self):
        ukijumuisha self.AllowPickle():
            f = self.partial(signature, ['asdf'], bar=[Kweli])
            f.attr = []
            kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                f_copy = pickle.loads(pickle.dumps(f, proto))
                self.assertEqual(signature(f_copy), signature(f))

    eleza test_copy(self):
        f = self.partial(signature, ['asdf'], bar=[Kweli])
        f.attr = []
        f_copy = copy.copy(f)
        self.assertEqual(signature(f_copy), signature(f))
        self.assertIs(f_copy.attr, f.attr)
        self.assertIs(f_copy.args, f.args)
        self.assertIs(f_copy.keywords, f.keywords)

    eleza test_deepcopy(self):
        f = self.partial(signature, ['asdf'], bar=[Kweli])
        f.attr = []
        f_copy = copy.deepcopy(f)
        self.assertEqual(signature(f_copy), signature(f))
        self.assertIsNot(f_copy.attr, f.attr)
        self.assertIsNot(f_copy.args, f.args)
        self.assertIsNot(f_copy.args[0], f.args[0])
        self.assertIsNot(f_copy.keywords, f.keywords)
        self.assertIsNot(f_copy.keywords['bar'], f.keywords['bar'])

    eleza test_setstate(self):
        f = self.partial(signature)
        f.__setstate__((capture, (1,), dict(a=10), dict(attr=[])))

        self.assertEqual(signature(f),
                         (capture, (1,), dict(a=10), dict(attr=[])))
        self.assertEqual(f(2, b=20), ((1, 2), {'a': 10, 'b': 20}))

        f.__setstate__((capture, (1,), dict(a=10), Tupu))

        self.assertEqual(signature(f), (capture, (1,), dict(a=10), {}))
        self.assertEqual(f(2, b=20), ((1, 2), {'a': 10, 'b': 20}))

        f.__setstate__((capture, (1,), Tupu, Tupu))
        #self.assertEqual(signature(f), (capture, (1,), {}, {}))
        self.assertEqual(f(2, b=20), ((1, 2), {'b': 20}))
        self.assertEqual(f(2), ((1, 2), {}))
        self.assertEqual(f(), ((1,), {}))

        f.__setstate__((capture, (), {}, Tupu))
        self.assertEqual(signature(f), (capture, (), {}, {}))
        self.assertEqual(f(2, b=20), ((2,), {'b': 20}))
        self.assertEqual(f(2), ((2,), {}))
        self.assertEqual(f(), ((), {}))

    eleza test_setstate_errors(self):
        f = self.partial(signature)
        self.assertRaises(TypeError, f.__setstate__, (capture, (), {}))
        self.assertRaises(TypeError, f.__setstate__, (capture, (), {}, {}, Tupu))
        self.assertRaises(TypeError, f.__setstate__, [capture, (), {}, Tupu])
        self.assertRaises(TypeError, f.__setstate__, (Tupu, (), {}, Tupu))
        self.assertRaises(TypeError, f.__setstate__, (capture, Tupu, {}, Tupu))
        self.assertRaises(TypeError, f.__setstate__, (capture, [], {}, Tupu))
        self.assertRaises(TypeError, f.__setstate__, (capture, (), [], Tupu))

    eleza test_setstate_subclasses(self):
        f = self.partial(signature)
        f.__setstate__((capture, MyTuple((1,)), MyDict(a=10), Tupu))
        s = signature(f)
        self.assertEqual(s, (capture, (1,), dict(a=10), {}))
        self.assertIs(type(s[1]), tuple)
        self.assertIs(type(s[2]), dict)
        r = f()
        self.assertEqual(r, ((1,), {'a': 10}))
        self.assertIs(type(r[0]), tuple)
        self.assertIs(type(r[1]), dict)

        f.__setstate__((capture, BadTuple((1,)), {}, Tupu))
        s = signature(f)
        self.assertEqual(s, (capture, (1,), {}, {}))
        self.assertIs(type(s[1]), tuple)
        r = f(2)
        self.assertEqual(r, ((1, 2), {}))
        self.assertIs(type(r[0]), tuple)

    eleza test_recursive_pickle(self):
        ukijumuisha self.AllowPickle():
            f = self.partial(capture)
            f.__setstate__((f, (), {}, {}))
            jaribu:
                kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                    ukijumuisha self.assertRaises(RecursionError):
                        pickle.dumps(f, proto)
            mwishowe:
                f.__setstate__((capture, (), {}, {}))

            f = self.partial(capture)
            f.__setstate__((capture, (f,), {}, {}))
            jaribu:
                kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                    f_copy = pickle.loads(pickle.dumps(f, proto))
                    jaribu:
                        self.assertIs(f_copy.args[0], f_copy)
                    mwishowe:
                        f_copy.__setstate__((capture, (), {}, {}))
            mwishowe:
                f.__setstate__((capture, (), {}, {}))

            f = self.partial(capture)
            f.__setstate__((capture, (), {'a': f}, {}))
            jaribu:
                kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                    f_copy = pickle.loads(pickle.dumps(f, proto))
                    jaribu:
                        self.assertIs(f_copy.keywords['a'], f_copy)
                    mwishowe:
                        f_copy.__setstate__((capture, (), {}, {}))
            mwishowe:
                f.__setstate__((capture, (), {}, {}))

    # Issue 6083: Reference counting bug
    eleza test_setstate_refcount(self):
        kundi BadSequence:
            eleza __len__(self):
                rudisha 4
            eleza __getitem__(self, key):
                ikiwa key == 0:
                    rudisha max
                lasivyo key == 1:
                    rudisha tuple(range(1000000))
                lasivyo key kwenye (2, 3):
                    rudisha {}
                ashiria IndexError

        f = self.partial(object)
        self.assertRaises(TypeError, f.__setstate__, BadSequence())

@unittest.skipUnless(c_functools, 'requires the C _functools module')
kundi TestPartialC(TestPartial, unittest.TestCase):
    ikiwa c_functools:
        partial = c_functools.partial

    kundi AllowPickle:
        eleza __enter__(self):
            rudisha self
        eleza __exit__(self, type, value, tb):
            rudisha Uongo

    eleza test_attributes_unwritable(self):
        # attributes should sio be writable
        p = self.partial(capture, 1, 2, a=10, b=20)
        self.assertRaises(AttributeError, setattr, p, 'func', map)
        self.assertRaises(AttributeError, setattr, p, 'args', (1, 2))
        self.assertRaises(AttributeError, setattr, p, 'keywords', dict(a=1, b=2))

        p = self.partial(hex)
        jaribu:
            toa p.__dict__
        tatizo TypeError:
            pita
        isipokua:
            self.fail('partial object allowed __dict__ to be deleted')

    eleza test_manually_adding_non_string_keyword(self):
        p = self.partial(capture)
        # Adding a non-string/unicode keyword to partial kwargs
        p.keywords[1234] = 'value'
        r = repr(p)
        self.assertIn('1234', r)
        self.assertIn("'value'", r)
        ukijumuisha self.assertRaises(TypeError):
            p()

    eleza test_keystr_replaces_value(self):
        p = self.partial(capture)

        kundi MutatesYourDict(object):
            eleza __str__(self):
                p.keywords[self] = ['sth2']
                rudisha 'astr'

        # Replacing the value during key formatting should keep the original
        # value alive (at least long enough).
        p.keywords[MutatesYourDict()] = ['sth']
        r = repr(p)
        self.assertIn('astr', r)
        self.assertIn("['sth']", r)


kundi TestPartialPy(TestPartial, unittest.TestCase):
    partial = py_functools.partial

    kundi AllowPickle:
        eleza __init__(self):
            self._cm = replaced_module("functools", py_functools)
        eleza __enter__(self):
            rudisha self._cm.__enter__()
        eleza __exit__(self, type, value, tb):
            rudisha self._cm.__exit__(type, value, tb)

ikiwa c_functools:
    kundi CPartialSubclass(c_functools.partial):
        pita

kundi PyPartialSubclass(py_functools.partial):
    pita

@unittest.skipUnless(c_functools, 'requires the C _functools module')
kundi TestPartialCSubclass(TestPartialC):
    ikiwa c_functools:
        partial = CPartialSubclass

    # partial subclasses are sio optimized kila nested calls
    test_nested_optimization = Tupu

kundi TestPartialPySubclass(TestPartialPy):
    partial = PyPartialSubclass

kundi TestPartialMethod(unittest.TestCase):

    kundi A(object):
        nothing = functools.partialmethod(capture)
        positional = functools.partialmethod(capture, 1)
        keywords = functools.partialmethod(capture, a=2)
        both = functools.partialmethod(capture, 3, b=4)
        spec_keywords = functools.partialmethod(capture, self=1, func=2)

        nested = functools.partialmethod(positional, 5)

        over_partial = functools.partialmethod(functools.partial(capture, c=6), 7)

        static = functools.partialmethod(staticmethod(capture), 8)
        cls = functools.partialmethod(classmethod(capture), d=9)

    a = A()

    eleza test_arg_combinations(self):
        self.assertEqual(self.a.nothing(), ((self.a,), {}))
        self.assertEqual(self.a.nothing(5), ((self.a, 5), {}))
        self.assertEqual(self.a.nothing(c=6), ((self.a,), {'c': 6}))
        self.assertEqual(self.a.nothing(5, c=6), ((self.a, 5), {'c': 6}))

        self.assertEqual(self.a.positional(), ((self.a, 1), {}))
        self.assertEqual(self.a.positional(5), ((self.a, 1, 5), {}))
        self.assertEqual(self.a.positional(c=6), ((self.a, 1), {'c': 6}))
        self.assertEqual(self.a.positional(5, c=6), ((self.a, 1, 5), {'c': 6}))

        self.assertEqual(self.a.keywords(), ((self.a,), {'a': 2}))
        self.assertEqual(self.a.keywords(5), ((self.a, 5), {'a': 2}))
        self.assertEqual(self.a.keywords(c=6), ((self.a,), {'a': 2, 'c': 6}))
        self.assertEqual(self.a.keywords(5, c=6), ((self.a, 5), {'a': 2, 'c': 6}))

        self.assertEqual(self.a.both(), ((self.a, 3), {'b': 4}))
        self.assertEqual(self.a.both(5), ((self.a, 3, 5), {'b': 4}))
        self.assertEqual(self.a.both(c=6), ((self.a, 3), {'b': 4, 'c': 6}))
        self.assertEqual(self.a.both(5, c=6), ((self.a, 3, 5), {'b': 4, 'c': 6}))

        self.assertEqual(self.A.both(self.a, 5, c=6), ((self.a, 3, 5), {'b': 4, 'c': 6}))

        self.assertEqual(self.a.spec_keywords(), ((self.a,), {'self': 1, 'func': 2}))

    eleza test_nested(self):
        self.assertEqual(self.a.nested(), ((self.a, 1, 5), {}))
        self.assertEqual(self.a.nested(6), ((self.a, 1, 5, 6), {}))
        self.assertEqual(self.a.nested(d=7), ((self.a, 1, 5), {'d': 7}))
        self.assertEqual(self.a.nested(6, d=7), ((self.a, 1, 5, 6), {'d': 7}))

        self.assertEqual(self.A.nested(self.a, 6, d=7), ((self.a, 1, 5, 6), {'d': 7}))

    eleza test_over_partial(self):
        self.assertEqual(self.a.over_partial(), ((self.a, 7), {'c': 6}))
        self.assertEqual(self.a.over_partial(5), ((self.a, 7, 5), {'c': 6}))
        self.assertEqual(self.a.over_partial(d=8), ((self.a, 7), {'c': 6, 'd': 8}))
        self.assertEqual(self.a.over_partial(5, d=8), ((self.a, 7, 5), {'c': 6, 'd': 8}))

        self.assertEqual(self.A.over_partial(self.a, 5, d=8), ((self.a, 7, 5), {'c': 6, 'd': 8}))

    eleza test_bound_method_introspection(self):
        obj = self.a
        self.assertIs(obj.both.__self__, obj)
        self.assertIs(obj.nested.__self__, obj)
        self.assertIs(obj.over_partial.__self__, obj)
        self.assertIs(obj.cls.__self__, self.A)
        self.assertIs(self.A.cls.__self__, self.A)

    eleza test_unbound_method_retrieval(self):
        obj = self.A
        self.assertUongo(hasattr(obj.both, "__self__"))
        self.assertUongo(hasattr(obj.nested, "__self__"))
        self.assertUongo(hasattr(obj.over_partial, "__self__"))
        self.assertUongo(hasattr(obj.static, "__self__"))
        self.assertUongo(hasattr(self.a.static, "__self__"))

    eleza test_descriptors(self):
        kila obj kwenye [self.A, self.a]:
            ukijumuisha self.subTest(obj=obj):
                self.assertEqual(obj.static(), ((8,), {}))
                self.assertEqual(obj.static(5), ((8, 5), {}))
                self.assertEqual(obj.static(d=8), ((8,), {'d': 8}))
                self.assertEqual(obj.static(5, d=8), ((8, 5), {'d': 8}))

                self.assertEqual(obj.cls(), ((self.A,), {'d': 9}))
                self.assertEqual(obj.cls(5), ((self.A, 5), {'d': 9}))
                self.assertEqual(obj.cls(c=8), ((self.A,), {'c': 8, 'd': 9}))
                self.assertEqual(obj.cls(5, c=8), ((self.A, 5), {'c': 8, 'd': 9}))

    eleza test_overriding_keywords(self):
        self.assertEqual(self.a.keywords(a=3), ((self.a,), {'a': 3}))
        self.assertEqual(self.A.keywords(self.a, a=3), ((self.a,), {'a': 3}))

    eleza test_invalid_args(self):
        ukijumuisha self.assertRaises(TypeError):
            kundi B(object):
                method = functools.partialmethod(Tupu, 1)
        ukijumuisha self.assertRaises(TypeError):
            kundi B:
                method = functools.partialmethod()
        ukijumuisha self.assertWarns(DeprecationWarning):
            kundi B:
                method = functools.partialmethod(func=capture, a=1)
        b = B()
        self.assertEqual(b.method(2, x=3), ((b, 2), {'a': 1, 'x': 3}))

    eleza test_repr(self):
        self.assertEqual(repr(vars(self.A)['both']),
                         'functools.partialmethod({}, 3, b=4)'.format(capture))

    eleza test_abstract(self):
        kundi Abstract(abc.ABCMeta):

            @abc.abstractmethod
            eleza add(self, x, y):
                pita

            add5 = functools.partialmethod(add, 5)

        self.assertKweli(Abstract.add.__isabstractmethod__)
        self.assertKweli(Abstract.add5.__isabstractmethod__)

        kila func kwenye [self.A.static, self.A.cls, self.A.over_partial, self.A.nested, self.A.both]:
            self.assertUongo(getattr(func, '__isabstractmethod__', Uongo))

    eleza test_positional_only(self):
        eleza f(a, b, /):
            rudisha a + b

        p = functools.partial(f, 1)
        self.assertEqual(p(2), f(1, 2))


kundi TestUpdateWrapper(unittest.TestCase):

    eleza check_wrapper(self, wrapper, wrapped,
                      assigned=functools.WRAPPER_ASSIGNMENTS,
                      updated=functools.WRAPPER_UPDATES):
        # Check attributes were assigned
        kila name kwenye assigned:
            self.assertIs(getattr(wrapper, name), getattr(wrapped, name))
        # Check attributes were updated
        kila name kwenye updated:
            wrapper_attr = getattr(wrapper, name)
            wrapped_attr = getattr(wrapped, name)
            kila key kwenye wrapped_attr:
                ikiwa name == "__dict__" na key == "__wrapped__":
                    # __wrapped__ ni overwritten by the update code
                    endelea
                self.assertIs(wrapped_attr[key], wrapper_attr[key])
        # Check __wrapped__
        self.assertIs(wrapper.__wrapped__, wrapped)


    eleza _default_update(self):
        eleza f(a:'This ni a new annotation'):
            """This ni a test"""
            pita
        f.attr = 'This ni also a test'
        f.__wrapped__ = "This ni a bald faced lie"
        eleza wrapper(b:'This ni the prior annotation'):
            pita
        functools.update_wrapper(wrapper, f)
        rudisha wrapper, f

    eleza test_default_update(self):
        wrapper, f = self._default_update()
        self.check_wrapper(wrapper, f)
        self.assertIs(wrapper.__wrapped__, f)
        self.assertEqual(wrapper.__name__, 'f')
        self.assertEqual(wrapper.__qualname__, f.__qualname__)
        self.assertEqual(wrapper.attr, 'This ni also a test')
        self.assertEqual(wrapper.__annotations__['a'], 'This ni a new annotation')
        self.assertNotIn('b', wrapper.__annotations__)

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    eleza test_default_update_doc(self):
        wrapper, f = self._default_update()
        self.assertEqual(wrapper.__doc__, 'This ni a test')

    eleza test_no_update(self):
        eleza f():
            """This ni a test"""
            pita
        f.attr = 'This ni also a test'
        eleza wrapper():
            pita
        functools.update_wrapper(wrapper, f, (), ())
        self.check_wrapper(wrapper, f, (), ())
        self.assertEqual(wrapper.__name__, 'wrapper')
        self.assertNotEqual(wrapper.__qualname__, f.__qualname__)
        self.assertEqual(wrapper.__doc__, Tupu)
        self.assertEqual(wrapper.__annotations__, {})
        self.assertUongo(hasattr(wrapper, 'attr'))

    eleza test_selective_update(self):
        eleza f():
            pita
        f.attr = 'This ni a different test'
        f.dict_attr = dict(a=1, b=2, c=3)
        eleza wrapper():
            pita
        wrapper.dict_attr = {}
        assign = ('attr',)
        update = ('dict_attr',)
        functools.update_wrapper(wrapper, f, assign, update)
        self.check_wrapper(wrapper, f, assign, update)
        self.assertEqual(wrapper.__name__, 'wrapper')
        self.assertNotEqual(wrapper.__qualname__, f.__qualname__)
        self.assertEqual(wrapper.__doc__, Tupu)
        self.assertEqual(wrapper.attr, 'This ni a different test')
        self.assertEqual(wrapper.dict_attr, f.dict_attr)

    eleza test_missing_attributes(self):
        eleza f():
            pita
        eleza wrapper():
            pita
        wrapper.dict_attr = {}
        assign = ('attr',)
        update = ('dict_attr',)
        # Missing attributes on wrapped object are ignored
        functools.update_wrapper(wrapper, f, assign, update)
        self.assertNotIn('attr', wrapper.__dict__)
        self.assertEqual(wrapper.dict_attr, {})
        # Wrapper must have expected attributes kila updating
        toa wrapper.dict_attr
        ukijumuisha self.assertRaises(AttributeError):
            functools.update_wrapper(wrapper, f, assign, update)
        wrapper.dict_attr = 1
        ukijumuisha self.assertRaises(AttributeError):
            functools.update_wrapper(wrapper, f, assign, update)

    @support.requires_docstrings
    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    eleza test_builtin_update(self):
        # Test kila bug #1576241
        eleza wrapper():
            pita
        functools.update_wrapper(wrapper, max)
        self.assertEqual(wrapper.__name__, 'max')
        self.assertKweli(wrapper.__doc__.startswith('max('))
        self.assertEqual(wrapper.__annotations__, {})


kundi TestWraps(TestUpdateWrapper):

    eleza _default_update(self):
        eleza f():
            """This ni a test"""
            pita
        f.attr = 'This ni also a test'
        f.__wrapped__ = "This ni still a bald faced lie"
        @functools.wraps(f)
        eleza wrapper():
            pita
        rudisha wrapper, f

    eleza test_default_update(self):
        wrapper, f = self._default_update()
        self.check_wrapper(wrapper, f)
        self.assertEqual(wrapper.__name__, 'f')
        self.assertEqual(wrapper.__qualname__, f.__qualname__)
        self.assertEqual(wrapper.attr, 'This ni also a test')

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    eleza test_default_update_doc(self):
        wrapper, _ = self._default_update()
        self.assertEqual(wrapper.__doc__, 'This ni a test')

    eleza test_no_update(self):
        eleza f():
            """This ni a test"""
            pita
        f.attr = 'This ni also a test'
        @functools.wraps(f, (), ())
        eleza wrapper():
            pita
        self.check_wrapper(wrapper, f, (), ())
        self.assertEqual(wrapper.__name__, 'wrapper')
        self.assertNotEqual(wrapper.__qualname__, f.__qualname__)
        self.assertEqual(wrapper.__doc__, Tupu)
        self.assertUongo(hasattr(wrapper, 'attr'))

    eleza test_selective_update(self):
        eleza f():
            pita
        f.attr = 'This ni a different test'
        f.dict_attr = dict(a=1, b=2, c=3)
        eleza add_dict_attr(f):
            f.dict_attr = {}
            rudisha f
        assign = ('attr',)
        update = ('dict_attr',)
        @functools.wraps(f, assign, update)
        @add_dict_attr
        eleza wrapper():
            pita
        self.check_wrapper(wrapper, f, assign, update)
        self.assertEqual(wrapper.__name__, 'wrapper')
        self.assertNotEqual(wrapper.__qualname__, f.__qualname__)
        self.assertEqual(wrapper.__doc__, Tupu)
        self.assertEqual(wrapper.attr, 'This ni a different test')
        self.assertEqual(wrapper.dict_attr, f.dict_attr)


kundi TestReduce:
    eleza test_reduce(self):
        kundi Squares:
            eleza __init__(self, max):
                self.max = max
                self.sofar = []

            eleza __len__(self):
                rudisha len(self.sofar)

            eleza __getitem__(self, i):
                ikiwa sio 0 <= i < self.max: ashiria IndexError
                n = len(self.sofar)
                wakati n <= i:
                    self.sofar.append(n*n)
                    n += 1
                rudisha self.sofar[i]
        eleza add(x, y):
            rudisha x + y
        self.assertEqual(self.reduce(add, ['a', 'b', 'c'], ''), 'abc')
        self.assertEqual(
            self.reduce(add, [['a', 'c'], [], ['d', 'w']], []),
            ['a','c','d','w']
        )
        self.assertEqual(self.reduce(lambda x, y: x*y, range(2,8), 1), 5040)
        self.assertEqual(
            self.reduce(lambda x, y: x*y, range(2,21), 1),
            2432902008176640000
        )
        self.assertEqual(self.reduce(add, Squares(10)), 285)
        self.assertEqual(self.reduce(add, Squares(10), 0), 285)
        self.assertEqual(self.reduce(add, Squares(0), 0), 0)
        self.assertRaises(TypeError, self.reduce)
        self.assertRaises(TypeError, self.reduce, 42, 42)
        self.assertRaises(TypeError, self.reduce, 42, 42, 42)
        self.assertEqual(self.reduce(42, "1"), "1") # func ni never called ukijumuisha one item
        self.assertEqual(self.reduce(42, "", "1"), "1") # func ni never called ukijumuisha one item
        self.assertRaises(TypeError, self.reduce, 42, (42, 42))
        self.assertRaises(TypeError, self.reduce, add, []) # arg 2 must sio be empty sequence ukijumuisha no initial value
        self.assertRaises(TypeError, self.reduce, add, "")
        self.assertRaises(TypeError, self.reduce, add, ())
        self.assertRaises(TypeError, self.reduce, add, object())

        kundi TestFailingIter:
            eleza __iter__(self):
                ashiria RuntimeError
        self.assertRaises(RuntimeError, self.reduce, add, TestFailingIter())

        self.assertEqual(self.reduce(add, [], Tupu), Tupu)
        self.assertEqual(self.reduce(add, [], 42), 42)

        kundi BadSeq:
            eleza __getitem__(self, index):
                ashiria ValueError
        self.assertRaises(ValueError, self.reduce, 42, BadSeq())

    # Test reduce()'s use of iterators.
    eleza test_iterator_usage(self):
        kundi SequenceClass:
            eleza __init__(self, n):
                self.n = n
            eleza __getitem__(self, i):
                ikiwa 0 <= i < self.n:
                    rudisha i
                isipokua:
                    ashiria IndexError

        kutoka operator agiza add
        self.assertEqual(self.reduce(add, SequenceClass(5)), 10)
        self.assertEqual(self.reduce(add, SequenceClass(5), 42), 52)
        self.assertRaises(TypeError, self.reduce, add, SequenceClass(0))
        self.assertEqual(self.reduce(add, SequenceClass(0), 42), 42)
        self.assertEqual(self.reduce(add, SequenceClass(1)), 0)
        self.assertEqual(self.reduce(add, SequenceClass(1), 42), 42)

        d = {"one": 1, "two": 2, "three": 3}
        self.assertEqual(self.reduce(add, d), "".join(d.keys()))


@unittest.skipUnless(c_functools, 'requires the C _functools module')
kundi TestReduceC(TestReduce, unittest.TestCase):
    ikiwa c_functools:
        reduce = c_functools.reduce


kundi TestReducePy(TestReduce, unittest.TestCase):
    reduce = staticmethod(py_functools.reduce)


kundi TestCmpToKey:

    eleza test_cmp_to_key(self):
        eleza cmp1(x, y):
            rudisha (x > y) - (x < y)
        key = self.cmp_to_key(cmp1)
        self.assertEqual(key(3), key(3))
        self.assertGreater(key(3), key(1))
        self.assertGreaterEqual(key(3), key(3))

        eleza cmp2(x, y):
            rudisha int(x) - int(y)
        key = self.cmp_to_key(cmp2)
        self.assertEqual(key(4.0), key('4'))
        self.assertLess(key(2), key('35'))
        self.assertLessEqual(key(2), key('35'))
        self.assertNotEqual(key(2), key('35'))

    eleza test_cmp_to_key_arguments(self):
        eleza cmp1(x, y):
            rudisha (x > y) - (x < y)
        key = self.cmp_to_key(mycmp=cmp1)
        self.assertEqual(key(obj=3), key(obj=3))
        self.assertGreater(key(obj=3), key(obj=1))
        ukijumuisha self.assertRaises((TypeError, AttributeError)):
            key(3) > 1    # rhs ni sio a K object
        ukijumuisha self.assertRaises((TypeError, AttributeError)):
            1 < key(3)    # lhs ni sio a K object
        ukijumuisha self.assertRaises(TypeError):
            key = self.cmp_to_key()             # too few args
        ukijumuisha self.assertRaises(TypeError):
            key = self.cmp_to_key(cmp1, Tupu)   # too many args
        key = self.cmp_to_key(cmp1)
        ukijumuisha self.assertRaises(TypeError):
            key()                                    # too few args
        ukijumuisha self.assertRaises(TypeError):
            key(Tupu, Tupu)                          # too many args

    eleza test_bad_cmp(self):
        eleza cmp1(x, y):
            ashiria ZeroDivisionError
        key = self.cmp_to_key(cmp1)
        ukijumuisha self.assertRaises(ZeroDivisionError):
            key(3) > key(1)

        kundi BadCmp:
            eleza __lt__(self, other):
                ashiria ZeroDivisionError
        eleza cmp1(x, y):
            rudisha BadCmp()
        ukijumuisha self.assertRaises(ZeroDivisionError):
            key(3) > key(1)

    eleza test_obj_field(self):
        eleza cmp1(x, y):
            rudisha (x > y) - (x < y)
        key = self.cmp_to_key(mycmp=cmp1)
        self.assertEqual(key(50).obj, 50)

    eleza test_sort_int(self):
        eleza mycmp(x, y):
            rudisha y - x
        self.assertEqual(sorted(range(5), key=self.cmp_to_key(mycmp)),
                         [4, 3, 2, 1, 0])

    eleza test_sort_int_str(self):
        eleza mycmp(x, y):
            x, y = int(x), int(y)
            rudisha (x > y) - (x < y)
        values = [5, '3', 7, 2, '0', '1', 4, '10', 1]
        values = sorted(values, key=self.cmp_to_key(mycmp))
        self.assertEqual([int(value) kila value kwenye values],
                         [0, 1, 1, 2, 3, 4, 5, 7, 10])

    eleza test_hash(self):
        eleza mycmp(x, y):
            rudisha y - x
        key = self.cmp_to_key(mycmp)
        k = key(10)
        self.assertRaises(TypeError, hash, k)
        self.assertNotIsInstance(k, collections.abc.Hashable)


@unittest.skipUnless(c_functools, 'requires the C _functools module')
kundi TestCmpToKeyC(TestCmpToKey, unittest.TestCase):
    ikiwa c_functools:
        cmp_to_key = c_functools.cmp_to_key


kundi TestCmpToKeyPy(TestCmpToKey, unittest.TestCase):
    cmp_to_key = staticmethod(py_functools.cmp_to_key)


kundi TestTotalOrdering(unittest.TestCase):

    eleza test_total_ordering_lt(self):
        @functools.total_ordering
        kundi A:
            eleza __init__(self, value):
                self.value = value
            eleza __lt__(self, other):
                rudisha self.value < other.value
            eleza __eq__(self, other):
                rudisha self.value == other.value
        self.assertKweli(A(1) < A(2))
        self.assertKweli(A(2) > A(1))
        self.assertKweli(A(1) <= A(2))
        self.assertKweli(A(2) >= A(1))
        self.assertKweli(A(2) <= A(2))
        self.assertKweli(A(2) >= A(2))
        self.assertUongo(A(1) > A(2))

    eleza test_total_ordering_le(self):
        @functools.total_ordering
        kundi A:
            eleza __init__(self, value):
                self.value = value
            eleza __le__(self, other):
                rudisha self.value <= other.value
            eleza __eq__(self, other):
                rudisha self.value == other.value
        self.assertKweli(A(1) < A(2))
        self.assertKweli(A(2) > A(1))
        self.assertKweli(A(1) <= A(2))
        self.assertKweli(A(2) >= A(1))
        self.assertKweli(A(2) <= A(2))
        self.assertKweli(A(2) >= A(2))
        self.assertUongo(A(1) >= A(2))

    eleza test_total_ordering_gt(self):
        @functools.total_ordering
        kundi A:
            eleza __init__(self, value):
                self.value = value
            eleza __gt__(self, other):
                rudisha self.value > other.value
            eleza __eq__(self, other):
                rudisha self.value == other.value
        self.assertKweli(A(1) < A(2))
        self.assertKweli(A(2) > A(1))
        self.assertKweli(A(1) <= A(2))
        self.assertKweli(A(2) >= A(1))
        self.assertKweli(A(2) <= A(2))
        self.assertKweli(A(2) >= A(2))
        self.assertUongo(A(2) < A(1))

    eleza test_total_ordering_ge(self):
        @functools.total_ordering
        kundi A:
            eleza __init__(self, value):
                self.value = value
            eleza __ge__(self, other):
                rudisha self.value >= other.value
            eleza __eq__(self, other):
                rudisha self.value == other.value
        self.assertKweli(A(1) < A(2))
        self.assertKweli(A(2) > A(1))
        self.assertKweli(A(1) <= A(2))
        self.assertKweli(A(2) >= A(1))
        self.assertKweli(A(2) <= A(2))
        self.assertKweli(A(2) >= A(2))
        self.assertUongo(A(2) <= A(1))

    eleza test_total_ordering_no_overwrite(self):
        # new methods should sio overwrite existing
        @functools.total_ordering
        kundi A(int):
            pita
        self.assertKweli(A(1) < A(2))
        self.assertKweli(A(2) > A(1))
        self.assertKweli(A(1) <= A(2))
        self.assertKweli(A(2) >= A(1))
        self.assertKweli(A(2) <= A(2))
        self.assertKweli(A(2) >= A(2))

    eleza test_no_operations_defined(self):
        ukijumuisha self.assertRaises(ValueError):
            @functools.total_ordering
            kundi A:
                pita

    eleza test_type_error_when_not_implemented(self):
        # bug 10042; ensure stack overflow does sio occur
        # when decorated types rudisha NotImplemented
        @functools.total_ordering
        kundi ImplementsLessThan:
            eleza __init__(self, value):
                self.value = value
            eleza __eq__(self, other):
                ikiwa isinstance(other, ImplementsLessThan):
                    rudisha self.value == other.value
                rudisha Uongo
            eleza __lt__(self, other):
                ikiwa isinstance(other, ImplementsLessThan):
                    rudisha self.value < other.value
                rudisha NotImplemented

        @functools.total_ordering
        kundi ImplementsGreaterThan:
            eleza __init__(self, value):
                self.value = value
            eleza __eq__(self, other):
                ikiwa isinstance(other, ImplementsGreaterThan):
                    rudisha self.value == other.value
                rudisha Uongo
            eleza __gt__(self, other):
                ikiwa isinstance(other, ImplementsGreaterThan):
                    rudisha self.value > other.value
                rudisha NotImplemented

        @functools.total_ordering
        kundi ImplementsLessThanEqualTo:
            eleza __init__(self, value):
                self.value = value
            eleza __eq__(self, other):
                ikiwa isinstance(other, ImplementsLessThanEqualTo):
                    rudisha self.value == other.value
                rudisha Uongo
            eleza __le__(self, other):
                ikiwa isinstance(other, ImplementsLessThanEqualTo):
                    rudisha self.value <= other.value
                rudisha NotImplemented

        @functools.total_ordering
        kundi ImplementsGreaterThanEqualTo:
            eleza __init__(self, value):
                self.value = value
            eleza __eq__(self, other):
                ikiwa isinstance(other, ImplementsGreaterThanEqualTo):
                    rudisha self.value == other.value
                rudisha Uongo
            eleza __ge__(self, other):
                ikiwa isinstance(other, ImplementsGreaterThanEqualTo):
                    rudisha self.value >= other.value
                rudisha NotImplemented

        @functools.total_ordering
        kundi ComparatorNotImplemented:
            eleza __init__(self, value):
                self.value = value
            eleza __eq__(self, other):
                ikiwa isinstance(other, ComparatorNotImplemented):
                    rudisha self.value == other.value
                rudisha Uongo
            eleza __lt__(self, other):
                rudisha NotImplemented

        ukijumuisha self.subTest("LT < 1"), self.assertRaises(TypeError):
            ImplementsLessThan(-1) < 1

        ukijumuisha self.subTest("LT < LE"), self.assertRaises(TypeError):
            ImplementsLessThan(0) < ImplementsLessThanEqualTo(0)

        ukijumuisha self.subTest("LT < GT"), self.assertRaises(TypeError):
            ImplementsLessThan(1) < ImplementsGreaterThan(1)

        ukijumuisha self.subTest("LE <= LT"), self.assertRaises(TypeError):
            ImplementsLessThanEqualTo(2) <= ImplementsLessThan(2)

        ukijumuisha self.subTest("LE <= GE"), self.assertRaises(TypeError):
            ImplementsLessThanEqualTo(3) <= ImplementsGreaterThanEqualTo(3)

        ukijumuisha self.subTest("GT > GE"), self.assertRaises(TypeError):
            ImplementsGreaterThan(4) > ImplementsGreaterThanEqualTo(4)

        ukijumuisha self.subTest("GT > LT"), self.assertRaises(TypeError):
            ImplementsGreaterThan(5) > ImplementsLessThan(5)

        ukijumuisha self.subTest("GE >= GT"), self.assertRaises(TypeError):
            ImplementsGreaterThanEqualTo(6) >= ImplementsGreaterThan(6)

        ukijumuisha self.subTest("GE >= LE"), self.assertRaises(TypeError):
            ImplementsGreaterThanEqualTo(7) >= ImplementsLessThanEqualTo(7)

        ukijumuisha self.subTest("GE when equal"):
            a = ComparatorNotImplemented(8)
            b = ComparatorNotImplemented(8)
            self.assertEqual(a, b)
            ukijumuisha self.assertRaises(TypeError):
                a >= b

        ukijumuisha self.subTest("LE when equal"):
            a = ComparatorNotImplemented(9)
            b = ComparatorNotImplemented(9)
            self.assertEqual(a, b)
            ukijumuisha self.assertRaises(TypeError):
                a <= b

    eleza test_pickle(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            kila name kwenye '__lt__', '__gt__', '__le__', '__ge__':
                ukijumuisha self.subTest(method=name, proto=proto):
                    method = getattr(Orderable_LT, name)
                    method_copy = pickle.loads(pickle.dumps(method, proto))
                    self.assertIs(method_copy, method)

@functools.total_ordering
kundi Orderable_LT:
    eleza __init__(self, value):
        self.value = value
    eleza __lt__(self, other):
        rudisha self.value < other.value
    eleza __eq__(self, other):
        rudisha self.value == other.value


kundi TestLRU:

    eleza test_lru(self):
        eleza orig(x, y):
            rudisha 3 * x + y
        f = self.module.lru_cache(maxsize=20)(orig)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(maxsize, 20)
        self.assertEqual(currsize, 0)
        self.assertEqual(hits, 0)
        self.assertEqual(misses, 0)

        domain = range(5)
        kila i kwenye range(1000):
            x, y = choice(domain), choice(domain)
            actual = f(x, y)
            expected = orig(x, y)
            self.assertEqual(actual, expected)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertKweli(hits > misses)
        self.assertEqual(hits + misses, 1000)
        self.assertEqual(currsize, 20)

        f.cache_clear()   # test clearing
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 0)
        self.assertEqual(misses, 0)
        self.assertEqual(currsize, 0)
        f(x, y)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 0)
        self.assertEqual(misses, 1)
        self.assertEqual(currsize, 1)

        # Test bypitaing the cache
        self.assertIs(f.__wrapped__, orig)
        f.__wrapped__(x, y)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 0)
        self.assertEqual(misses, 1)
        self.assertEqual(currsize, 1)

        # test size zero (which means "never-cache")
        @self.module.lru_cache(0)
        eleza f():
            nonlocal f_cnt
            f_cnt += 1
            rudisha 20
        self.assertEqual(f.cache_info().maxsize, 0)
        f_cnt = 0
        kila i kwenye range(5):
            self.assertEqual(f(), 20)
        self.assertEqual(f_cnt, 5)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 0)
        self.assertEqual(misses, 5)
        self.assertEqual(currsize, 0)

        # test size one
        @self.module.lru_cache(1)
        eleza f():
            nonlocal f_cnt
            f_cnt += 1
            rudisha 20
        self.assertEqual(f.cache_info().maxsize, 1)
        f_cnt = 0
        kila i kwenye range(5):
            self.assertEqual(f(), 20)
        self.assertEqual(f_cnt, 1)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 4)
        self.assertEqual(misses, 1)
        self.assertEqual(currsize, 1)

        # test size two
        @self.module.lru_cache(2)
        eleza f(x):
            nonlocal f_cnt
            f_cnt += 1
            rudisha x*10
        self.assertEqual(f.cache_info().maxsize, 2)
        f_cnt = 0
        kila x kwenye 7, 9, 7, 9, 7, 9, 8, 8, 8, 9, 9, 9, 8, 8, 8, 7:
            #    *  *              *                          *
            self.assertEqual(f(x), x*10)
        self.assertEqual(f_cnt, 4)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(hits, 12)
        self.assertEqual(misses, 4)
        self.assertEqual(currsize, 2)

    eleza test_lru_no_args(self):
        @self.module.lru_cache
        eleza square(x):
            rudisha x ** 2

        self.assertEqual(list(map(square, [10, 20, 10])),
                         [100, 400, 100])
        self.assertEqual(square.cache_info().hits, 1)
        self.assertEqual(square.cache_info().misses, 2)
        self.assertEqual(square.cache_info().maxsize, 128)
        self.assertEqual(square.cache_info().currsize, 2)

    eleza test_lru_bug_35780(self):
        # C version of the lru_cache was sio checking to see if
        # the user function call has already modified the cache
        # (this arises kwenye recursive calls na kwenye multi-threading).
        # This cause the cache to have orphan links sio referenced
        # by the cache dictionary.

        once = Kweli                 # Modified by f(x) below

        @self.module.lru_cache(maxsize=10)
        eleza f(x):
            nonlocal once
            rv = f'.{x}.'
            ikiwa x == 20 na once:
                once = Uongo
                rv = f(x)
            rudisha rv

        # Fill the cache
        kila x kwenye range(15):
            self.assertEqual(f(x), f'.{x}.')
        self.assertEqual(f.cache_info().currsize, 10)

        # Make a recursive call na make sure the cache remains full
        self.assertEqual(f(20), '.20.')
        self.assertEqual(f.cache_info().currsize, 10)

    eleza test_lru_bug_36650(self):
        # C version of lru_cache was treating a call ukijumuisha an empty **kwargs
        # dictionary kama being distinct kutoka a call ukijumuisha no keywords at all.
        # This did sio result kwenye an incorrect answer, but it did trigger
        # an unexpected cache miss.

        @self.module.lru_cache()
        eleza f(x):
            pita

        f(0)
        f(0, **{})
        self.assertEqual(f.cache_info().hits, 1)

    eleza test_lru_hash_only_once(self):
        # To protect against weird reentrancy bugs na to improve
        # efficiency when faced ukijumuisha slow __hash__ methods, the
        # LRU cache guarantees that it will only call __hash__
        # only once per use kama an argument to the cached function.

        @self.module.lru_cache(maxsize=1)
        eleza f(x, y):
            rudisha x * 3 + y

        # Simulate the integer 5
        mock_int = unittest.mock.Mock()
        mock_int.__mul__ = unittest.mock.Mock(return_value=15)
        mock_int.__hash__ = unittest.mock.Mock(return_value=999)

        # Add to cache:  One use kama an argument gives one call
        self.assertEqual(f(mock_int, 1), 16)
        self.assertEqual(mock_int.__hash__.call_count, 1)
        self.assertEqual(f.cache_info(), (0, 1, 1, 1))

        # Cache hit: One use kama an argument gives one additional call
        self.assertEqual(f(mock_int, 1), 16)
        self.assertEqual(mock_int.__hash__.call_count, 2)
        self.assertEqual(f.cache_info(), (1, 1, 1, 1))

        # Cache eviction: No use kama an argument gives no additional call
        self.assertEqual(f(6, 2), 20)
        self.assertEqual(mock_int.__hash__.call_count, 2)
        self.assertEqual(f.cache_info(), (1, 2, 1, 1))

        # Cache miss: One use kama an argument gives one additional call
        self.assertEqual(f(mock_int, 1), 16)
        self.assertEqual(mock_int.__hash__.call_count, 3)
        self.assertEqual(f.cache_info(), (1, 3, 1, 1))

    eleza test_lru_reentrancy_with_len(self):
        # Test to make sure the LRU cache code isn't thrown-off by
        # caching the built-in len() function.  Since len() can be
        # cached, we shouldn't use it inside the lru code itself.
        old_len = builtins.len
        jaribu:
            builtins.len = self.module.lru_cache(4)(len)
            kila i kwenye [0, 0, 1, 2, 3, 3, 4, 5, 6, 1, 7, 2, 1]:
                self.assertEqual(len('abcdefghijklmn'[:i]), i)
        mwishowe:
            builtins.len = old_len

    eleza test_lru_star_arg_handling(self):
        # Test regression that arose kwenye ea064ff3c10f
        @functools.lru_cache()
        eleza f(*args):
            rudisha args

        self.assertEqual(f(1, 2), (1, 2))
        self.assertEqual(f((1, 2)), ((1, 2),))

    eleza test_lru_type_error(self):
        # Regression test kila issue #28653.
        # lru_cache was leaking when one of the arguments
        # wasn't cacheable.

        @functools.lru_cache(maxsize=Tupu)
        eleza infinite_cache(o):
            pita

        @functools.lru_cache(maxsize=10)
        eleza limited_cache(o):
            pita

        ukijumuisha self.assertRaises(TypeError):
            infinite_cache([])

        ukijumuisha self.assertRaises(TypeError):
            limited_cache([])

    eleza test_lru_with_maxsize_none(self):
        @self.module.lru_cache(maxsize=Tupu)
        eleza fib(n):
            ikiwa n < 2:
                rudisha n
            rudisha fib(n-1) + fib(n-2)
        self.assertEqual([fib(n) kila n kwenye range(16)],
            [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610])
        self.assertEqual(fib.cache_info(),
            self.module._CacheInfo(hits=28, misses=16, maxsize=Tupu, currsize=16))
        fib.cache_clear()
        self.assertEqual(fib.cache_info(),
            self.module._CacheInfo(hits=0, misses=0, maxsize=Tupu, currsize=0))

    eleza test_lru_with_maxsize_negative(self):
        @self.module.lru_cache(maxsize=-10)
        eleza eq(n):
            rudisha n
        kila i kwenye (0, 1):
            self.assertEqual([eq(n) kila n kwenye range(150)], list(range(150)))
        self.assertEqual(eq.cache_info(),
            self.module._CacheInfo(hits=0, misses=300, maxsize=0, currsize=0))

    eleza test_lru_with_exceptions(self):
        # Verify that user_function exceptions get pitaed through without
        # creating a hard-to-read chained exception.
        # http://bugs.python.org/issue13177
        kila maxsize kwenye (Tupu, 128):
            @self.module.lru_cache(maxsize)
            eleza func(i):
                rudisha 'abc'[i]
            self.assertEqual(func(0), 'a')
            ukijumuisha self.assertRaises(IndexError) kama cm:
                func(15)
            self.assertIsTupu(cm.exception.__context__)
            # Verify that the previous exception did sio result kwenye a cached entry
            ukijumuisha self.assertRaises(IndexError):
                func(15)

    eleza test_lru_with_types(self):
        kila maxsize kwenye (Tupu, 128):
            @self.module.lru_cache(maxsize=maxsize, typed=Kweli)
            eleza square(x):
                rudisha x * x
            self.assertEqual(square(3), 9)
            self.assertEqual(type(square(3)), type(9))
            self.assertEqual(square(3.0), 9.0)
            self.assertEqual(type(square(3.0)), type(9.0))
            self.assertEqual(square(x=3), 9)
            self.assertEqual(type(square(x=3)), type(9))
            self.assertEqual(square(x=3.0), 9.0)
            self.assertEqual(type(square(x=3.0)), type(9.0))
            self.assertEqual(square.cache_info().hits, 4)
            self.assertEqual(square.cache_info().misses, 4)

    eleza test_lru_with_keyword_args(self):
        @self.module.lru_cache()
        eleza fib(n):
            ikiwa n < 2:
                rudisha n
            rudisha fib(n=n-1) + fib(n=n-2)
        self.assertEqual(
            [fib(n=number) kila number kwenye range(16)],
            [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
        )
        self.assertEqual(fib.cache_info(),
            self.module._CacheInfo(hits=28, misses=16, maxsize=128, currsize=16))
        fib.cache_clear()
        self.assertEqual(fib.cache_info(),
            self.module._CacheInfo(hits=0, misses=0, maxsize=128, currsize=0))

    eleza test_lru_with_keyword_args_maxsize_none(self):
        @self.module.lru_cache(maxsize=Tupu)
        eleza fib(n):
            ikiwa n < 2:
                rudisha n
            rudisha fib(n=n-1) + fib(n=n-2)
        self.assertEqual([fib(n=number) kila number kwenye range(16)],
            [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610])
        self.assertEqual(fib.cache_info(),
            self.module._CacheInfo(hits=28, misses=16, maxsize=Tupu, currsize=16))
        fib.cache_clear()
        self.assertEqual(fib.cache_info(),
            self.module._CacheInfo(hits=0, misses=0, maxsize=Tupu, currsize=0))

    eleza test_kwargs_order(self):
        # PEP 468: Preserving Keyword Argument Order
        @self.module.lru_cache(maxsize=10)
        eleza f(**kwargs):
            rudisha list(kwargs.items())
        self.assertEqual(f(a=1, b=2), [('a', 1), ('b', 2)])
        self.assertEqual(f(b=2, a=1), [('b', 2), ('a', 1)])
        self.assertEqual(f.cache_info(),
            self.module._CacheInfo(hits=0, misses=2, maxsize=10, currsize=2))

    eleza test_lru_cache_decoration(self):
        eleza f(zomg: 'zomg_annotation'):
            """f doc string"""
            rudisha 42
        g = self.module.lru_cache()(f)
        kila attr kwenye self.module.WRAPPER_ASSIGNMENTS:
            self.assertEqual(getattr(g, attr), getattr(f, attr))

    eleza test_lru_cache_threaded(self):
        n, m = 5, 11
        eleza orig(x, y):
            rudisha 3 * x + y
        f = self.module.lru_cache(maxsize=n*m)(orig)
        hits, misses, maxsize, currsize = f.cache_info()
        self.assertEqual(currsize, 0)

        start = threading.Event()
        eleza full(k):
            start.wait(10)
            kila _ kwenye range(m):
                self.assertEqual(f(k, 0), orig(k, 0))

        eleza clear():
            start.wait(10)
            kila _ kwenye range(2*m):
                f.cache_clear()

        orig_si = sys.getswitchinterval()
        support.setswitchinterval(1e-6)
        jaribu:
            # create n threads kwenye order to fill cache
            threads = [threading.Thread(target=full, args=[k])
                       kila k kwenye range(n)]
            ukijumuisha support.start_threads(threads):
                start.set()

            hits, misses, maxsize, currsize = f.cache_info()
            ikiwa self.module ni py_functools:
                # XXX: Why can be sio equal?
                self.assertLessEqual(misses, n)
                self.assertLessEqual(hits, m*n - misses)
            isipokua:
                self.assertEqual(misses, n)
                self.assertEqual(hits, m*n - misses)
            self.assertEqual(currsize, n)

            # create n threads kwenye order to fill cache na 1 to clear it
            threads = [threading.Thread(target=clear)]
            threads += [threading.Thread(target=full, args=[k])
                        kila k kwenye range(n)]
            start.clear()
            ukijumuisha support.start_threads(threads):
                start.set()
        mwishowe:
            sys.setswitchinterval(orig_si)

    eleza test_lru_cache_threaded2(self):
        # Simultaneous call ukijumuisha the same arguments
        n, m = 5, 7
        start = threading.Barrier(n+1)
        pause = threading.Barrier(n+1)
        stop = threading.Barrier(n+1)
        @self.module.lru_cache(maxsize=m*n)
        eleza f(x):
            pause.wait(10)
            rudisha 3 * x
        self.assertEqual(f.cache_info(), (0, 0, m*n, 0))
        eleza test():
            kila i kwenye range(m):
                start.wait(10)
                self.assertEqual(f(i), 3 * i)
                stop.wait(10)
        threads = [threading.Thread(target=test) kila k kwenye range(n)]
        ukijumuisha support.start_threads(threads):
            kila i kwenye range(m):
                start.wait(10)
                stop.reset()
                pause.wait(10)
                start.reset()
                stop.wait(10)
                pause.reset()
                self.assertEqual(f.cache_info(), (0, (i+1)*n, m*n, i+1))

    eleza test_lru_cache_threaded3(self):
        @self.module.lru_cache(maxsize=2)
        eleza f(x):
            time.sleep(.01)
            rudisha 3 * x
        eleza test(i, x):
            ukijumuisha self.subTest(thread=i):
                self.assertEqual(f(x), 3 * x, i)
        threads = [threading.Thread(target=test, args=(i, v))
                   kila i, v kwenye enumerate([1, 2, 2, 3, 2])]
        ukijumuisha support.start_threads(threads):
            pita

    eleza test_need_for_rlock(self):
        # This will deadlock on an LRU cache that uses a regular lock

        @self.module.lru_cache(maxsize=10)
        eleza test_func(x):
            'Used to demonstrate a reentrant lru_cache call within a single thread'
            rudisha x

        kundi DoubleEq:
            'Demonstrate a reentrant lru_cache call within a single thread'
            eleza __init__(self, x):
                self.x = x
            eleza __hash__(self):
                rudisha self.x
            eleza __eq__(self, other):
                ikiwa self.x == 2:
                    test_func(DoubleEq(1))
                rudisha self.x == other.x

        test_func(DoubleEq(1))                      # Load the cache
        test_func(DoubleEq(2))                      # Load the cache
        self.assertEqual(test_func(DoubleEq(2)),    # Trigger a re-entrant __eq__ call
                         DoubleEq(2))               # Verify the correct rudisha value

    eleza test_lru_method(self):
        kundi X(int):
            f_cnt = 0
            @self.module.lru_cache(2)
            eleza f(self, x):
                self.f_cnt += 1
                rudisha x*10+self
        a = X(5)
        b = X(5)
        c = X(7)
        self.assertEqual(X.f.cache_info(), (0, 0, 2, 0))

        kila x kwenye 1, 2, 2, 3, 1, 1, 1, 2, 3, 3:
            self.assertEqual(a.f(x), x*10 + 5)
        self.assertEqual((a.f_cnt, b.f_cnt, c.f_cnt), (6, 0, 0))
        self.assertEqual(X.f.cache_info(), (4, 6, 2, 2))

        kila x kwenye 1, 2, 1, 1, 1, 1, 3, 2, 2, 2:
            self.assertEqual(b.f(x), x*10 + 5)
        self.assertEqual((a.f_cnt, b.f_cnt, c.f_cnt), (6, 4, 0))
        self.assertEqual(X.f.cache_info(), (10, 10, 2, 2))

        kila x kwenye 2, 1, 1, 1, 1, 2, 1, 3, 2, 1:
            self.assertEqual(c.f(x), x*10 + 7)
        self.assertEqual((a.f_cnt, b.f_cnt, c.f_cnt), (6, 4, 5))
        self.assertEqual(X.f.cache_info(), (15, 15, 2, 2))

        self.assertEqual(a.f.cache_info(), X.f.cache_info())
        self.assertEqual(b.f.cache_info(), X.f.cache_info())
        self.assertEqual(c.f.cache_info(), X.f.cache_info())

    eleza test_pickle(self):
        cls = self.__class__
        kila f kwenye cls.cached_func[0], cls.cached_meth, cls.cached_staticmeth:
            kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                ukijumuisha self.subTest(proto=proto, func=f):
                    f_copy = pickle.loads(pickle.dumps(f, proto))
                    self.assertIs(f_copy, f)

    eleza test_copy(self):
        cls = self.__class__
        eleza orig(x, y):
            rudisha 3 * x + y
        part = self.module.partial(orig, 2)
        funcs = (cls.cached_func[0], cls.cached_meth, cls.cached_staticmeth,
                 self.module.lru_cache(2)(part))
        kila f kwenye funcs:
            ukijumuisha self.subTest(func=f):
                f_copy = copy.copy(f)
                self.assertIs(f_copy, f)

    eleza test_deepcopy(self):
        cls = self.__class__
        eleza orig(x, y):
            rudisha 3 * x + y
        part = self.module.partial(orig, 2)
        funcs = (cls.cached_func[0], cls.cached_meth, cls.cached_staticmeth,
                 self.module.lru_cache(2)(part))
        kila f kwenye funcs:
            ukijumuisha self.subTest(func=f):
                f_copy = copy.deepcopy(f)
                self.assertIs(f_copy, f)


@py_functools.lru_cache()
eleza py_cached_func(x, y):
    rudisha 3 * x + y

@c_functools.lru_cache()
eleza c_cached_func(x, y):
    rudisha 3 * x + y


kundi TestLRUPy(TestLRU, unittest.TestCase):
    module = py_functools
    cached_func = py_cached_func,

    @module.lru_cache()
    eleza cached_meth(self, x, y):
        rudisha 3 * x + y

    @staticmethod
    @module.lru_cache()
    eleza cached_staticmeth(x, y):
        rudisha 3 * x + y


kundi TestLRUC(TestLRU, unittest.TestCase):
    module = c_functools
    cached_func = c_cached_func,

    @module.lru_cache()
    eleza cached_meth(self, x, y):
        rudisha 3 * x + y

    @staticmethod
    @module.lru_cache()
    eleza cached_staticmeth(x, y):
        rudisha 3 * x + y


kundi TestSingleDispatch(unittest.TestCase):
    eleza test_simple_overloads(self):
        @functools.singledispatch
        eleza g(obj):
            rudisha "base"
        eleza g_int(i):
            rudisha "integer"
        g.register(int, g_int)
        self.assertEqual(g("str"), "base")
        self.assertEqual(g(1), "integer")
        self.assertEqual(g([1,2,3]), "base")

    eleza test_mro(self):
        @functools.singledispatch
        eleza g(obj):
            rudisha "base"
        kundi A:
            pita
        kundi C(A):
            pita
        kundi B(A):
            pita
        kundi D(C, B):
            pita
        eleza g_A(a):
            rudisha "A"
        eleza g_B(b):
            rudisha "B"
        g.register(A, g_A)
        g.register(B, g_B)
        self.assertEqual(g(A()), "A")
        self.assertEqual(g(B()), "B")
        self.assertEqual(g(C()), "A")
        self.assertEqual(g(D()), "B")

    eleza test_register_decorator(self):
        @functools.singledispatch
        eleza g(obj):
            rudisha "base"
        @g.register(int)
        eleza g_int(i):
            rudisha "int %s" % (i,)
        self.assertEqual(g(""), "base")
        self.assertEqual(g(12), "int 12")
        self.assertIs(g.dispatch(int), g_int)
        self.assertIs(g.dispatch(object), g.dispatch(str))
        # Note: kwenye the assert above this ni sio g.
        # @singledispatch returns the wrapper.

    eleza test_wrapping_attributes(self):
        @functools.singledispatch
        eleza g(obj):
            "Simple test"
            rudisha "Test"
        self.assertEqual(g.__name__, "g")
        ikiwa sys.flags.optimize < 2:
            self.assertEqual(g.__doc__, "Simple test")

    @unittest.skipUnless(decimal, 'requires _decimal')
    @support.cpython_only
    eleza test_c_classes(self):
        @functools.singledispatch
        eleza g(obj):
            rudisha "base"
        @g.register(decimal.DecimalException)
        eleza _(obj):
            rudisha obj.args
        subn = decimal.Subnormal("Exponent < Emin")
        rnd = decimal.Rounded("Number got rounded")
        self.assertEqual(g(subn), ("Exponent < Emin",))
        self.assertEqual(g(rnd), ("Number got rounded",))
        @g.register(decimal.Subnormal)
        eleza _(obj):
            rudisha "Too small to care."
        self.assertEqual(g(subn), "Too small to care.")
        self.assertEqual(g(rnd), ("Number got rounded",))

    eleza test_compose_mro(self):
        # Tupu of the examples kwenye this test depend on haystack ordering.
        c = collections.abc
        mro = functools._compose_mro
        bases = [c.Sequence, c.MutableMapping, c.Mapping, c.Set]
        kila haystack kwenye permutations(bases):
            m = mro(dict, haystack)
            self.assertEqual(m, [dict, c.MutableMapping, c.Mapping,
                                 c.Collection, c.Sized, c.Iterable,
                                 c.Container, object])
        bases = [c.Container, c.Mapping, c.MutableMapping, collections.OrderedDict]
        kila haystack kwenye permutations(bases):
            m = mro(collections.ChainMap, haystack)
            self.assertEqual(m, [collections.ChainMap, c.MutableMapping, c.Mapping,
                                 c.Collection, c.Sized, c.Iterable,
                                 c.Container, object])

        # If there's a generic function ukijumuisha implementations registered for
        # both Sized na Container, pitaing a defaultdict to it results kwenye an
        # ambiguous dispatch which will cause a RuntimeError (see
        # test_mro_conflicts).
        bases = [c.Container, c.Sized, str]
        kila haystack kwenye permutations(bases):
            m = mro(collections.defaultdict, [c.Sized, c.Container, str])
            self.assertEqual(m, [collections.defaultdict, dict, c.Sized,
                                 c.Container, object])

        # MutableSequence below ni registered directly on D. In other words, it
        # precedes MutableMapping which means single dispatch will always
        # choose MutableSequence here.
        kundi D(collections.defaultdict):
            pita
        c.MutableSequence.register(D)
        bases = [c.MutableSequence, c.MutableMapping]
        kila haystack kwenye permutations(bases):
            m = mro(D, bases)
            self.assertEqual(m, [D, c.MutableSequence, c.Sequence, c.Reversible,
                                 collections.defaultdict, dict, c.MutableMapping, c.Mapping,
                                 c.Collection, c.Sized, c.Iterable, c.Container,
                                 object])

        # Container na Callable are registered on different base classes na
        # a generic function supporting both should always pick the Callable
        # implementation ikiwa a C instance ni pitaed.
        kundi C(collections.defaultdict):
            eleza __call__(self):
                pita
        bases = [c.Sized, c.Callable, c.Container, c.Mapping]
        kila haystack kwenye permutations(bases):
            m = mro(C, haystack)
            self.assertEqual(m, [C, c.Callable, collections.defaultdict, dict, c.Mapping,
                                 c.Collection, c.Sized, c.Iterable,
                                 c.Container, object])

    eleza test_register_abc(self):
        c = collections.abc
        d = {"a": "b"}
        l = [1, 2, 3]
        s = {object(), Tupu}
        f = frozenset(s)
        t = (1, 2, 3)
        @functools.singledispatch
        eleza g(obj):
            rudisha "base"
        self.assertEqual(g(d), "base")
        self.assertEqual(g(l), "base")
        self.assertEqual(g(s), "base")
        self.assertEqual(g(f), "base")
        self.assertEqual(g(t), "base")
        g.register(c.Sized, lambda obj: "sized")
        self.assertEqual(g(d), "sized")
        self.assertEqual(g(l), "sized")
        self.assertEqual(g(s), "sized")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")
        g.register(c.MutableMapping, lambda obj: "mutablemapping")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "sized")
        self.assertEqual(g(s), "sized")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")
        g.register(collections.ChainMap, lambda obj: "chainmap")
        self.assertEqual(g(d), "mutablemapping")  # irrelevant ABCs registered
        self.assertEqual(g(l), "sized")
        self.assertEqual(g(s), "sized")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")
        g.register(c.MutableSequence, lambda obj: "mutablesequence")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "sized")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")
        g.register(c.MutableSet, lambda obj: "mutableset")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")
        g.register(c.Mapping, lambda obj: "mapping")
        self.assertEqual(g(d), "mutablemapping")  # sio specific enough
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")
        g.register(c.Sequence, lambda obj: "sequence")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sequence")
        g.register(c.Set, lambda obj: "set")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "set")
        self.assertEqual(g(t), "sequence")
        g.register(dict, lambda obj: "dict")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "set")
        self.assertEqual(g(t), "sequence")
        g.register(list, lambda obj: "list")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "list")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "set")
        self.assertEqual(g(t), "sequence")
        g.register(set, lambda obj: "concrete-set")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "list")
        self.assertEqual(g(s), "concrete-set")
        self.assertEqual(g(f), "set")
        self.assertEqual(g(t), "sequence")
        g.register(frozenset, lambda obj: "frozen-set")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "list")
        self.assertEqual(g(s), "concrete-set")
        self.assertEqual(g(f), "frozen-set")
        self.assertEqual(g(t), "sequence")
        g.register(tuple, lambda obj: "tuple")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "list")
        self.assertEqual(g(s), "concrete-set")
        self.assertEqual(g(f), "frozen-set")
        self.assertEqual(g(t), "tuple")

    eleza test_c3_abc(self):
        c = collections.abc
        mro = functools._c3_mro
        kundi A(object):
            pita
        kundi B(A):
            eleza __len__(self):
                rudisha 0   # implies Sized
        @c.Container.register
        kundi C(object):
            pita
        kundi D(object):
            pita   # unrelated
        kundi X(D, C, B):
            eleza __call__(self):
                pita   # implies Callable
        expected = [X, c.Callable, D, C, c.Container, B, c.Sized, A, object]
        kila abcs kwenye permutations([c.Sized, c.Callable, c.Container]):
            self.assertEqual(mro(X, abcs=abcs), expected)
        # unrelated ABCs don't appear kwenye the resulting MRO
        many_abcs = [c.Mapping, c.Sized, c.Callable, c.Container, c.Iterable]
        self.assertEqual(mro(X, abcs=many_abcs), expected)

    eleza test_false_meta(self):
        # see issue23572
        kundi MetaA(type):
            eleza __len__(self):
                rudisha 0
        kundi A(metaclass=MetaA):
            pita
        kundi AA(A):
            pita
        @functools.singledispatch
        eleza fun(a):
            rudisha 'base A'
        @fun.register(A)
        eleza _(a):
            rudisha 'fun A'
        aa = AA()
        self.assertEqual(fun(aa), 'fun A')

    eleza test_mro_conflicts(self):
        c = collections.abc
        @functools.singledispatch
        eleza g(arg):
            rudisha "base"
        kundi O(c.Sized):
            eleza __len__(self):
                rudisha 0
        o = O()
        self.assertEqual(g(o), "base")
        g.register(c.Iterable, lambda arg: "iterable")
        g.register(c.Container, lambda arg: "container")
        g.register(c.Sized, lambda arg: "sized")
        g.register(c.Set, lambda arg: "set")
        self.assertEqual(g(o), "sized")
        c.Iterable.register(O)
        self.assertEqual(g(o), "sized")   # because it's explicitly kwenye __mro__
        c.Container.register(O)
        self.assertEqual(g(o), "sized")   # see above: Sized ni kwenye __mro__
        c.Set.register(O)
        self.assertEqual(g(o), "set")     # because c.Set ni a subkundi of
                                          # c.Sized na c.Container
        kundi P:
            pita
        p = P()
        self.assertEqual(g(p), "base")
        c.Iterable.register(P)
        self.assertEqual(g(p), "iterable")
        c.Container.register(P)
        ukijumuisha self.assertRaises(RuntimeError) kama re_one:
            g(p)
        self.assertIn(
            str(re_one.exception),
            (("Ambiguous dispatch: <kundi 'collections.abc.Container'> "
              "or <kundi 'collections.abc.Iterable'>"),
             ("Ambiguous dispatch: <kundi 'collections.abc.Iterable'> "
              "or <kundi 'collections.abc.Container'>")),
        )
        kundi Q(c.Sized):
            eleza __len__(self):
                rudisha 0
        q = Q()
        self.assertEqual(g(q), "sized")
        c.Iterable.register(Q)
        self.assertEqual(g(q), "sized")   # because it's explicitly kwenye __mro__
        c.Set.register(Q)
        self.assertEqual(g(q), "set")     # because c.Set ni a subkundi of
                                          # c.Sized na c.Iterable
        @functools.singledispatch
        eleza h(arg):
            rudisha "base"
        @h.register(c.Sized)
        eleza _(arg):
            rudisha "sized"
        @h.register(c.Container)
        eleza _(arg):
            rudisha "container"
        # Even though Sized na Container are explicit bases of MutableMapping,
        # this ABC ni implicitly registered on defaultdict which makes all of
        # MutableMapping's bases implicit kama well kutoka defaultdict's
        # perspective.
        ukijumuisha self.assertRaises(RuntimeError) kama re_two:
            h(collections.defaultdict(lambda: 0))
        self.assertIn(
            str(re_two.exception),
            (("Ambiguous dispatch: <kundi 'collections.abc.Container'> "
              "or <kundi 'collections.abc.Sized'>"),
             ("Ambiguous dispatch: <kundi 'collections.abc.Sized'> "
              "or <kundi 'collections.abc.Container'>")),
        )
        kundi R(collections.defaultdict):
            pita
        c.MutableSequence.register(R)
        @functools.singledispatch
        eleza i(arg):
            rudisha "base"
        @i.register(c.MutableMapping)
        eleza _(arg):
            rudisha "mapping"
        @i.register(c.MutableSequence)
        eleza _(arg):
            rudisha "sequence"
        r = R()
        self.assertEqual(i(r), "sequence")
        kundi S:
            pita
        kundi T(S, c.Sized):
            eleza __len__(self):
                rudisha 0
        t = T()
        self.assertEqual(h(t), "sized")
        c.Container.register(T)
        self.assertEqual(h(t), "sized")   # because it's explicitly kwenye the MRO
        kundi U:
            eleza __len__(self):
                rudisha 0
        u = U()
        self.assertEqual(h(u), "sized")   # implicit Sized subkundi inferred
                                          # kutoka the existence of __len__()
        c.Container.register(U)
        # There ni no preference kila registered versus inferred ABCs.
        ukijumuisha self.assertRaises(RuntimeError) kama re_three:
            h(u)
        self.assertIn(
            str(re_three.exception),
            (("Ambiguous dispatch: <kundi 'collections.abc.Container'> "
              "or <kundi 'collections.abc.Sized'>"),
             ("Ambiguous dispatch: <kundi 'collections.abc.Sized'> "
              "or <kundi 'collections.abc.Container'>")),
        )
        kundi V(c.Sized, S):
            eleza __len__(self):
                rudisha 0
        @functools.singledispatch
        eleza j(arg):
            rudisha "base"
        @j.register(S)
        eleza _(arg):
            rudisha "s"
        @j.register(c.Container)
        eleza _(arg):
            rudisha "container"
        v = V()
        self.assertEqual(j(v), "s")
        c.Container.register(V)
        self.assertEqual(j(v), "container")   # because it ends up right after
                                              # Sized kwenye the MRO

    eleza test_cache_invalidation(self):
        kutoka collections agiza UserDict
        agiza weakref

        kundi TracingDict(UserDict):
            eleza __init__(self, *args, **kwargs):
                super(TracingDict, self).__init__(*args, **kwargs)
                self.set_ops = []
                self.get_ops = []
            eleza __getitem__(self, key):
                result = self.data[key]
                self.get_ops.append(key)
                rudisha result
            eleza __setitem__(self, key, value):
                self.set_ops.append(key)
                self.data[key] = value
            eleza clear(self):
                self.data.clear()

        td = TracingDict()
        ukijumuisha support.swap_attr(weakref, "WeakKeyDictionary", lambda: td):
            c = collections.abc
            @functools.singledispatch
            eleza g(arg):
                rudisha "base"
            d = {}
            l = []
            self.assertEqual(len(td), 0)
            self.assertEqual(g(d), "base")
            self.assertEqual(len(td), 1)
            self.assertEqual(td.get_ops, [])
            self.assertEqual(td.set_ops, [dict])
            self.assertEqual(td.data[dict], g.registry[object])
            self.assertEqual(g(l), "base")
            self.assertEqual(len(td), 2)
            self.assertEqual(td.get_ops, [])
            self.assertEqual(td.set_ops, [dict, list])
            self.assertEqual(td.data[dict], g.registry[object])
            self.assertEqual(td.data[list], g.registry[object])
            self.assertEqual(td.data[dict], td.data[list])
            self.assertEqual(g(l), "base")
            self.assertEqual(g(d), "base")
            self.assertEqual(td.get_ops, [list, dict])
            self.assertEqual(td.set_ops, [dict, list])
            g.register(list, lambda arg: "list")
            self.assertEqual(td.get_ops, [list, dict])
            self.assertEqual(len(td), 0)
            self.assertEqual(g(d), "base")
            self.assertEqual(len(td), 1)
            self.assertEqual(td.get_ops, [list, dict])
            self.assertEqual(td.set_ops, [dict, list, dict])
            self.assertEqual(td.data[dict],
                             functools._find_impl(dict, g.registry))
            self.assertEqual(g(l), "list")
            self.assertEqual(len(td), 2)
            self.assertEqual(td.get_ops, [list, dict])
            self.assertEqual(td.set_ops, [dict, list, dict, list])
            self.assertEqual(td.data[list],
                             functools._find_impl(list, g.registry))
            kundi X:
                pita
            c.MutableMapping.register(X)   # Will sio inalidate the cache,
                                           # sio using ABCs yet.
            self.assertEqual(g(d), "base")
            self.assertEqual(g(l), "list")
            self.assertEqual(td.get_ops, [list, dict, dict, list])
            self.assertEqual(td.set_ops, [dict, list, dict, list])
            g.register(c.Sized, lambda arg: "sized")
            self.assertEqual(len(td), 0)
            self.assertEqual(g(d), "sized")
            self.assertEqual(len(td), 1)
            self.assertEqual(td.get_ops, [list, dict, dict, list])
            self.assertEqual(td.set_ops, [dict, list, dict, list, dict])
            self.assertEqual(g(l), "list")
            self.assertEqual(len(td), 2)
            self.assertEqual(td.get_ops, [list, dict, dict, list])
            self.assertEqual(td.set_ops, [dict, list, dict, list, dict, list])
            self.assertEqual(g(l), "list")
            self.assertEqual(g(d), "sized")
            self.assertEqual(td.get_ops, [list, dict, dict, list, list, dict])
            self.assertEqual(td.set_ops, [dict, list, dict, list, dict, list])
            g.dispatch(list)
            g.dispatch(dict)
            self.assertEqual(td.get_ops, [list, dict, dict, list, list, dict,
                                          list, dict])
            self.assertEqual(td.set_ops, [dict, list, dict, list, dict, list])
            c.MutableSet.register(X)       # Will invalidate the cache.
            self.assertEqual(len(td), 2)   # Stale cache.
            self.assertEqual(g(l), "list")
            self.assertEqual(len(td), 1)
            g.register(c.MutableMapping, lambda arg: "mutablemapping")
            self.assertEqual(len(td), 0)
            self.assertEqual(g(d), "mutablemapping")
            self.assertEqual(len(td), 1)
            self.assertEqual(g(l), "list")
            self.assertEqual(len(td), 2)
            g.register(dict, lambda arg: "dict")
            self.assertEqual(g(d), "dict")
            self.assertEqual(g(l), "list")
            g._clear_cache()
            self.assertEqual(len(td), 0)

    eleza test_annotations(self):
        @functools.singledispatch
        eleza i(arg):
            rudisha "base"
        @i.register
        eleza _(arg: collections.abc.Mapping):
            rudisha "mapping"
        @i.register
        eleza _(arg: "collections.abc.Sequence"):
            rudisha "sequence"
        self.assertEqual(i(Tupu), "base")
        self.assertEqual(i({"a": 1}), "mapping")
        self.assertEqual(i([1, 2, 3]), "sequence")
        self.assertEqual(i((1, 2, 3)), "sequence")
        self.assertEqual(i("str"), "sequence")

        # Registering classes kama callables doesn't work ukijumuisha annotations,
        # you need to pita the type explicitly.
        @i.register(str)
        kundi _:
            eleza __init__(self, arg):
                self.arg = arg

            eleza __eq__(self, other):
                rudisha self.arg == other
        self.assertEqual(i("str"), "str")

    eleza test_method_register(self):
        kundi A:
            @functools.singledispatchmethod
            eleza t(self, arg):
                self.arg = "base"
            @t.register(int)
            eleza _(self, arg):
                self.arg = "int"
            @t.register(str)
            eleza _(self, arg):
                self.arg = "str"
        a = A()

        a.t(0)
        self.assertEqual(a.arg, "int")
        aa = A()
        self.assertUongo(hasattr(aa, 'arg'))
        a.t('')
        self.assertEqual(a.arg, "str")
        aa = A()
        self.assertUongo(hasattr(aa, 'arg'))
        a.t(0.0)
        self.assertEqual(a.arg, "base")
        aa = A()
        self.assertUongo(hasattr(aa, 'arg'))

    eleza test_staticmethod_register(self):
        kundi A:
            @functools.singledispatchmethod
            @staticmethod
            eleza t(arg):
                rudisha arg
            @t.register(int)
            @staticmethod
            eleza _(arg):
                rudisha isinstance(arg, int)
            @t.register(str)
            @staticmethod
            eleza _(arg):
                rudisha isinstance(arg, str)
        a = A()

        self.assertKweli(A.t(0))
        self.assertKweli(A.t(''))
        self.assertEqual(A.t(0.0), 0.0)

    eleza test_classmethod_register(self):
        kundi A:
            eleza __init__(self, arg):
                self.arg = arg

            @functools.singledispatchmethod
            @classmethod
            eleza t(cls, arg):
                rudisha cls("base")
            @t.register(int)
            @classmethod
            eleza _(cls, arg):
                rudisha cls("int")
            @t.register(str)
            @classmethod
            eleza _(cls, arg):
                rudisha cls("str")

        self.assertEqual(A.t(0).arg, "int")
        self.assertEqual(A.t('').arg, "str")
        self.assertEqual(A.t(0.0).arg, "base")

    eleza test_callable_register(self):
        kundi A:
            eleza __init__(self, arg):
                self.arg = arg

            @functools.singledispatchmethod
            @classmethod
            eleza t(cls, arg):
                rudisha cls("base")

        @A.t.register(int)
        @classmethod
        eleza _(cls, arg):
            rudisha cls("int")
        @A.t.register(str)
        @classmethod
        eleza _(cls, arg):
            rudisha cls("str")

        self.assertEqual(A.t(0).arg, "int")
        self.assertEqual(A.t('').arg, "str")
        self.assertEqual(A.t(0.0).arg, "base")

    eleza test_abstractmethod_register(self):
        kundi Abstract(abc.ABCMeta):

            @functools.singledispatchmethod
            @abc.abstractmethod
            eleza add(self, x, y):
                pita

        self.assertKweli(Abstract.add.__isabstractmethod__)

    eleza test_type_ann_register(self):
        kundi A:
            @functools.singledispatchmethod
            eleza t(self, arg):
                rudisha "base"
            @t.register
            eleza _(self, arg: int):
                rudisha "int"
            @t.register
            eleza _(self, arg: str):
                rudisha "str"
        a = A()

        self.assertEqual(a.t(0), "int")
        self.assertEqual(a.t(''), "str")
        self.assertEqual(a.t(0.0), "base")

    eleza test_invalid_registrations(self):
        msg_prefix = "Invalid first argument to `register()`: "
        msg_suffix = (
            ". Use either `@register(some_class)` ama plain `@register` on an "
            "annotated function."
        )
        @functools.singledispatch
        eleza i(arg):
            rudisha "base"
        ukijumuisha self.assertRaises(TypeError) kama exc:
            @i.register(42)
            eleza _(arg):
                rudisha "I annotated ukijumuisha a non-type"
        self.assertKweli(str(exc.exception).startswith(msg_prefix + "42"))
        self.assertKweli(str(exc.exception).endswith(msg_suffix))
        ukijumuisha self.assertRaises(TypeError) kama exc:
            @i.register
            eleza _(arg):
                rudisha "I forgot to annotate"
        self.assertKweli(str(exc.exception).startswith(msg_prefix +
            "<function TestSingleDispatch.test_invalid_registrations.<locals>._"
        ))
        self.assertKweli(str(exc.exception).endswith(msg_suffix))

        ukijumuisha self.assertRaises(TypeError) kama exc:
            @i.register
            eleza _(arg: typing.Iterable[str]):
                # At runtime, dispatching on generics ni impossible.
                # When registering implementations ukijumuisha singledispatch, avoid
                # types kutoka `typing`. Instead, annotate ukijumuisha regular types
                # ama ABCs.
                rudisha "I annotated ukijumuisha a generic collection"
        self.assertKweli(str(exc.exception).startswith(
            "Invalid annotation kila 'arg'."
        ))
        self.assertKweli(str(exc.exception).endswith(
            'typing.Iterable[str] ni sio a class.'
        ))

    eleza test_invalid_positional_argument(self):
        @functools.singledispatch
        eleza f(*args):
            pita
        msg = 'f requires at least 1 positional argument'
        ukijumuisha self.assertRaisesRegex(TypeError, msg):
            f()


kundi CachedCostItem:
    _cost = 1

    eleza __init__(self):
        self.lock = py_functools.RLock()

    @py_functools.cached_property
    eleza cost(self):
        """The cost of the item."""
        ukijumuisha self.lock:
            self._cost += 1
        rudisha self._cost


kundi OptionallyCachedCostItem:
    _cost = 1

    eleza get_cost(self):
        """The cost of the item."""
        self._cost += 1
        rudisha self._cost

    cached_cost = py_functools.cached_property(get_cost)


kundi CachedCostItemWait:

    eleza __init__(self, event):
        self._cost = 1
        self.lock = py_functools.RLock()
        self.event = event

    @py_functools.cached_property
    eleza cost(self):
        self.event.wait(1)
        ukijumuisha self.lock:
            self._cost += 1
        rudisha self._cost


kundi CachedCostItemWithSlots:
    __slots__ = ('_cost')

    eleza __init__(self):
        self._cost = 1

    @py_functools.cached_property
    eleza cost(self):
        ashiria RuntimeError('never called, slots sio supported')


kundi TestCachedProperty(unittest.TestCase):
    eleza test_cached(self):
        item = CachedCostItem()
        self.assertEqual(item.cost, 2)
        self.assertEqual(item.cost, 2) # sio 3

    eleza test_cached_attribute_name_differs_from_func_name(self):
        item = OptionallyCachedCostItem()
        self.assertEqual(item.get_cost(), 2)
        self.assertEqual(item.cached_cost, 3)
        self.assertEqual(item.get_cost(), 4)
        self.assertEqual(item.cached_cost, 3)

    eleza test_threaded(self):
        go = threading.Event()
        item = CachedCostItemWait(go)

        num_threads = 3

        orig_si = sys.getswitchinterval()
        sys.setswitchinterval(1e-6)
        jaribu:
            threads = [
                threading.Thread(target=lambda: item.cost)
                kila k kwenye range(num_threads)
            ]
            ukijumuisha support.start_threads(threads):
                go.set()
        mwishowe:
            sys.setswitchinterval(orig_si)

        self.assertEqual(item.cost, 2)

    eleza test_object_with_slots(self):
        item = CachedCostItemWithSlots()
        ukijumuisha self.assertRaisesRegex(
                TypeError,
                "No '__dict__' attribute on 'CachedCostItemWithSlots' instance to cache 'cost' property.",
        ):
            item.cost

    eleza test_immutable_dict(self):
        kundi MyMeta(type):
            @py_functools.cached_property
            eleza prop(self):
                rudisha Kweli

        kundi MyClass(metaclass=MyMeta):
            pita

        ukijumuisha self.assertRaisesRegex(
            TypeError,
            "The '__dict__' attribute on 'MyMeta' instance does sio support item assignment kila caching 'prop' property.",
        ):
            MyClass.prop

    eleza test_reuse_different_names(self):
        """Disallow this case because decorated function a would sio be cached."""
        ukijumuisha self.assertRaises(RuntimeError) kama ctx:
            kundi ReusedCachedProperty:
                @py_functools.cached_property
                eleza a(self):
                    pita

                b = a

        self.assertEqual(
            str(ctx.exception.__context__),
            str(TypeError("Cannot assign the same cached_property to two different names ('a' na 'b')."))
        )

    eleza test_reuse_same_name(self):
        """Reusing a cached_property on different classes under the same name ni OK."""
        counter = 0

        @py_functools.cached_property
        eleza _cp(_self):
            nonlocal counter
            counter += 1
            rudisha counter

        kundi A:
            cp = _cp

        kundi B:
            cp = _cp

        a = A()
        b = B()

        self.assertEqual(a.cp, 1)
        self.assertEqual(b.cp, 2)
        self.assertEqual(a.cp, 1)

    eleza test_set_name_not_called(self):
        cp = py_functools.cached_property(lambda s: Tupu)
        kundi Foo:
            pita

        Foo.cp = cp

        ukijumuisha self.assertRaisesRegex(
                TypeError,
                "Cannot use cached_property instance without calling __set_name__ on it.",
        ):
            Foo().cp

    eleza test_access_from_class(self):
        self.assertIsInstance(CachedCostItem.cost, py_functools.cached_property)

    eleza test_doc(self):
        self.assertEqual(CachedCostItem.cost.__doc__, "The cost of the item.")


ikiwa __name__ == '__main__':
    unittest.main()
