agiza builtins
agiza copyreg
agiza gc
agiza itertools
agiza math
agiza pickle
agiza sys
agiza types
agiza unittest
agiza warnings
agiza weakref

kutoka copy agiza deepcopy
kutoka test agiza support

jaribu:
    agiza _testcapi
except ImportError:
    _testcapi = Tupu


kundi OperatorsTest(unittest.TestCase):

    eleza __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.binops = {
            'add': '+',
            'sub': '-',
            'mul': '*',
            'matmul': '@',
            'truediv': '/',
            'floordiv': '//',
            'divmod': 'divmod',
            'pow': '**',
            'lshift': '<<',
            'rshift': '>>',
            'and': '&',
            'xor': '^',
            'or': '|',
            'cmp': 'cmp',
            'lt': '<',
            'le': '<=',
            'eq': '==',
            'ne': '!=',
            'gt': '>',
            'ge': '>=',
        }

        kila name, expr kwenye list(self.binops.items()):
            ikiwa expr.islower():
                expr = expr + "(a, b)"
            isipokua:
                expr = 'a %s b' % expr
            self.binops[name] = expr

        self.unops = {
            'pos': '+',
            'neg': '-',
            'abs': 'abs',
            'invert': '~',
            'int': 'int',
            'float': 'float',
        }

        kila name, expr kwenye list(self.unops.items()):
            ikiwa expr.islower():
                expr = expr + "(a)"
            isipokua:
                expr = '%s a' % expr
            self.unops[name] = expr

    eleza unop_test(self, a, res, expr="len(a)", meth="__len__"):
        d = {'a': a}
        self.assertEqual(eval(expr, d), res)
        t = type(a)
        m = getattr(t, meth)

        # Find method kwenye parent class
        wakati meth sio kwenye t.__dict__:
            t = t.__bases__[0]
        # kwenye some implementations (e.g. PyPy), 'm' can be a regular unbound
        # method object; the getattr() below obtains its underlying function.
        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
        self.assertEqual(m(a), res)
        bm = getattr(a, meth)
        self.assertEqual(bm(), res)

    eleza binop_test(self, a, b, res, expr="a+b", meth="__add__"):
        d = {'a': a, 'b': b}

        self.assertEqual(eval(expr, d), res)
        t = type(a)
        m = getattr(t, meth)
        wakati meth sio kwenye t.__dict__:
            t = t.__bases__[0]
        # kwenye some implementations (e.g. PyPy), 'm' can be a regular unbound
        # method object; the getattr() below obtains its underlying function.
        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
        self.assertEqual(m(a, b), res)
        bm = getattr(a, meth)
        self.assertEqual(bm(b), res)

    eleza sliceop_test(self, a, b, c, res, expr="a[b:c]", meth="__getitem__"):
        d = {'a': a, 'b': b, 'c': c}
        self.assertEqual(eval(expr, d), res)
        t = type(a)
        m = getattr(t, meth)
        wakati meth sio kwenye t.__dict__:
            t = t.__bases__[0]
        # kwenye some implementations (e.g. PyPy), 'm' can be a regular unbound
        # method object; the getattr() below obtains its underlying function.
        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
        self.assertEqual(m(a, slice(b, c)), res)
        bm = getattr(a, meth)
        self.assertEqual(bm(slice(b, c)), res)

    eleza setop_test(self, a, b, res, stmt="a+=b", meth="__iadd__"):
        d = {'a': deepcopy(a), 'b': b}
        exec(stmt, d)
        self.assertEqual(d['a'], res)
        t = type(a)
        m = getattr(t, meth)
        wakati meth sio kwenye t.__dict__:
            t = t.__bases__[0]
        # kwenye some implementations (e.g. PyPy), 'm' can be a regular unbound
        # method object; the getattr() below obtains its underlying function.
        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
        d['a'] = deepcopy(a)
        m(d['a'], b)
        self.assertEqual(d['a'], res)
        d['a'] = deepcopy(a)
        bm = getattr(d['a'], meth)
        bm(b)
        self.assertEqual(d['a'], res)

    eleza set2op_test(self, a, b, c, res, stmt="a[b]=c", meth="__setitem__"):
        d = {'a': deepcopy(a), 'b': b, 'c': c}
        exec(stmt, d)
        self.assertEqual(d['a'], res)
        t = type(a)
        m = getattr(t, meth)
        wakati meth sio kwenye t.__dict__:
            t = t.__bases__[0]
        # kwenye some implementations (e.g. PyPy), 'm' can be a regular unbound
        # method object; the getattr() below obtains its underlying function.
        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
        d['a'] = deepcopy(a)
        m(d['a'], b, c)
        self.assertEqual(d['a'], res)
        d['a'] = deepcopy(a)
        bm = getattr(d['a'], meth)
        bm(b, c)
        self.assertEqual(d['a'], res)

    eleza setsliceop_test(self, a, b, c, d, res, stmt="a[b:c]=d", meth="__setitem__"):
        dictionary = {'a': deepcopy(a), 'b': b, 'c': c, 'd': d}
        exec(stmt, dictionary)
        self.assertEqual(dictionary['a'], res)
        t = type(a)
        wakati meth sio kwenye t.__dict__:
            t = t.__bases__[0]
        m = getattr(t, meth)
        # kwenye some implementations (e.g. PyPy), 'm' can be a regular unbound
        # method object; the getattr() below obtains its underlying function.
        self.assertEqual(getattr(m, 'im_func', m), t.__dict__[meth])
        dictionary['a'] = deepcopy(a)
        m(dictionary['a'], slice(b, c), d)
        self.assertEqual(dictionary['a'], res)
        dictionary['a'] = deepcopy(a)
        bm = getattr(dictionary['a'], meth)
        bm(slice(b, c), d)
        self.assertEqual(dictionary['a'], res)

    eleza test_lists(self):
        # Testing list operations...
        # Asserts are within individual test methods
        self.binop_test([1], [2], [1,2], "a+b", "__add__")
        self.binop_test([1,2,3], 2, 1, "b kwenye a", "__contains__")
        self.binop_test([1,2,3], 4, 0, "b kwenye a", "__contains__")
        self.binop_test([1,2,3], 1, 2, "a[b]", "__getitem__")
        self.sliceop_test([1,2,3], 0, 2, [1,2], "a[b:c]", "__getitem__")
        self.setop_test([1], [2], [1,2], "a+=b", "__iadd__")
        self.setop_test([1,2], 3, [1,2,1,2,1,2], "a*=b", "__imul__")
        self.unop_test([1,2,3], 3, "len(a)", "__len__")
        self.binop_test([1,2], 3, [1,2,1,2,1,2], "a*b", "__mul__")
        self.binop_test([1,2], 3, [1,2,1,2,1,2], "b*a", "__rmul__")
        self.set2op_test([1,2], 1, 3, [1,3], "a[b]=c", "__setitem__")
        self.setsliceop_test([1,2,3,4], 1, 3, [5,6], [1,5,6,4], "a[b:c]=d",
                        "__setitem__")

    eleza test_dicts(self):
        # Testing dict operations...
        self.binop_test({1:2,3:4}, 1, 1, "b kwenye a", "__contains__")
        self.binop_test({1:2,3:4}, 2, 0, "b kwenye a", "__contains__")
        self.binop_test({1:2,3:4}, 1, 2, "a[b]", "__getitem__")

        d = {1:2, 3:4}
        l1 = []
        kila i kwenye list(d.keys()):
            l1.append(i)
        l = []
        kila i kwenye iter(d):
            l.append(i)
        self.assertEqual(l, l1)
        l = []
        kila i kwenye d.__iter__():
            l.append(i)
        self.assertEqual(l, l1)
        l = []
        kila i kwenye dict.__iter__(d):
            l.append(i)
        self.assertEqual(l, l1)
        d = {1:2, 3:4}
        self.unop_test(d, 2, "len(a)", "__len__")
        self.assertEqual(eval(repr(d), {}), d)
        self.assertEqual(eval(d.__repr__(), {}), d)
        self.set2op_test({1:2,3:4}, 2, 3, {1:2,2:3,3:4}, "a[b]=c",
                        "__setitem__")

    # Tests kila unary na binary operators
    eleza number_operators(self, a, b, skip=[]):
        dict = {'a': a, 'b': b}

        kila name, expr kwenye self.binops.items():
            ikiwa name sio kwenye skip:
                name = "__%s__" % name
                ikiwa hasattr(a, name):
                    res = eval(expr, dict)
                    self.binop_test(a, b, res, expr, name)

        kila name, expr kwenye list(self.unops.items()):
            ikiwa name sio kwenye skip:
                name = "__%s__" % name
                ikiwa hasattr(a, name):
                    res = eval(expr, dict)
                    self.unop_test(a, res, expr, name)

    eleza test_ints(self):
        # Testing int operations...
        self.number_operators(100, 3)
        # The following crashes kwenye Python 2.2
        self.assertEqual((1).__bool__(), 1)
        self.assertEqual((0).__bool__(), 0)
        # This returns 'NotImplemented' kwenye Python 2.2
        kundi C(int):
            eleza __add__(self, other):
                rudisha NotImplemented
        self.assertEqual(C(5), 5)
        jaribu:
            C() + ""
        except TypeError:
            pass
        isipokua:
            self.fail("NotImplemented should have caused TypeError")

    eleza test_floats(self):
        # Testing float operations...
        self.number_operators(100.0, 3.0)

    eleza test_complexes(self):
        # Testing complex operations...
        self.number_operators(100.0j, 3.0j, skip=['lt', 'le', 'gt', 'ge',
                                                  'int', 'float',
                                                  'floordiv', 'divmod', 'mod'])

        kundi Number(complex):
            __slots__ = ['prec']
            eleza __new__(cls, *args, **kwds):
                result = complex.__new__(cls, *args)
                result.prec = kwds.get('prec', 12)
                rudisha result
            eleza __repr__(self):
                prec = self.prec
                ikiwa self.imag == 0.0:
                    rudisha "%.*g" % (prec, self.real)
                ikiwa self.real == 0.0:
                    rudisha "%.*gj" % (prec, self.imag)
                rudisha "(%.*g+%.*gj)" % (prec, self.real, prec, self.imag)
            __str__ = __repr__

        a = Number(3.14, prec=6)
        self.assertEqual(repr(a), "3.14")
        self.assertEqual(a.prec, 6)

        a = Number(a, prec=2)
        self.assertEqual(repr(a), "3.1")
        self.assertEqual(a.prec, 2)

        a = Number(234.5)
        self.assertEqual(repr(a), "234.5")
        self.assertEqual(a.prec, 12)

    eleza test_explicit_reverse_methods(self):
        # see issue 9930
        self.assertEqual(complex.__radd__(3j, 4.0), complex(4.0, 3.0))
        self.assertEqual(float.__rsub__(3.0, 1), -2.0)

    @support.impl_detail("the module 'xxsubtype' ni internal")
    eleza test_spam_lists(self):
        # Testing spamlist operations...
        agiza copy, xxsubtype as spam

        eleza spamlist(l, memo=Tupu):
            agiza xxsubtype as spam
            rudisha spam.spamlist(l)

        # This ni an ugly hack:
        copy._deepcopy_dispatch[spam.spamlist] = spamlist

        self.binop_test(spamlist([1]), spamlist([2]), spamlist([1,2]), "a+b",
                       "__add__")
        self.binop_test(spamlist([1,2,3]), 2, 1, "b kwenye a", "__contains__")
        self.binop_test(spamlist([1,2,3]), 4, 0, "b kwenye a", "__contains__")
        self.binop_test(spamlist([1,2,3]), 1, 2, "a[b]", "__getitem__")
        self.sliceop_test(spamlist([1,2,3]), 0, 2, spamlist([1,2]), "a[b:c]",
                          "__getitem__")
        self.setop_test(spamlist([1]), spamlist([2]), spamlist([1,2]), "a+=b",
                        "__iadd__")
        self.setop_test(spamlist([1,2]), 3, spamlist([1,2,1,2,1,2]), "a*=b",
                        "__imul__")
        self.unop_test(spamlist([1,2,3]), 3, "len(a)", "__len__")
        self.binop_test(spamlist([1,2]), 3, spamlist([1,2,1,2,1,2]), "a*b",
                        "__mul__")
        self.binop_test(spamlist([1,2]), 3, spamlist([1,2,1,2,1,2]), "b*a",
                        "__rmul__")
        self.set2op_test(spamlist([1,2]), 1, 3, spamlist([1,3]), "a[b]=c",
                         "__setitem__")
        self.setsliceop_test(spamlist([1,2,3,4]), 1, 3, spamlist([5,6]),
                             spamlist([1,5,6,4]), "a[b:c]=d", "__setitem__")
        # Test subclassing
        kundi C(spam.spamlist):
            eleza foo(self): rudisha 1
        a = C()
        self.assertEqual(a, [])
        self.assertEqual(a.foo(), 1)
        a.append(100)
        self.assertEqual(a, [100])
        self.assertEqual(a.getstate(), 0)
        a.setstate(42)
        self.assertEqual(a.getstate(), 42)

    @support.impl_detail("the module 'xxsubtype' ni internal")
    eleza test_spam_dicts(self):
        # Testing spamdict operations...
        agiza copy, xxsubtype as spam
        eleza spamdict(d, memo=Tupu):
            agiza xxsubtype as spam
            sd = spam.spamdict()
            kila k, v kwenye list(d.items()):
                sd[k] = v
            rudisha sd
        # This ni an ugly hack:
        copy._deepcopy_dispatch[spam.spamdict] = spamdict

        self.binop_test(spamdict({1:2,3:4}), 1, 1, "b kwenye a", "__contains__")
        self.binop_test(spamdict({1:2,3:4}), 2, 0, "b kwenye a", "__contains__")
        self.binop_test(spamdict({1:2,3:4}), 1, 2, "a[b]", "__getitem__")
        d = spamdict({1:2,3:4})
        l1 = []
        kila i kwenye list(d.keys()):
            l1.append(i)
        l = []
        kila i kwenye iter(d):
            l.append(i)
        self.assertEqual(l, l1)
        l = []
        kila i kwenye d.__iter__():
            l.append(i)
        self.assertEqual(l, l1)
        l = []
        kila i kwenye type(spamdict({})).__iter__(d):
            l.append(i)
        self.assertEqual(l, l1)
        straightd = {1:2, 3:4}
        spamd = spamdict(straightd)
        self.unop_test(spamd, 2, "len(a)", "__len__")
        self.unop_test(spamd, repr(straightd), "repr(a)", "__repr__")
        self.set2op_test(spamdict({1:2,3:4}), 2, 3, spamdict({1:2,2:3,3:4}),
                   "a[b]=c", "__setitem__")
        # Test subclassing
        kundi C(spam.spamdict):
            eleza foo(self): rudisha 1
        a = C()
        self.assertEqual(list(a.items()), [])
        self.assertEqual(a.foo(), 1)
        a['foo'] = 'bar'
        self.assertEqual(list(a.items()), [('foo', 'bar')])
        self.assertEqual(a.getstate(), 0)
        a.setstate(100)
        self.assertEqual(a.getstate(), 100)

    eleza test_wrap_lenfunc_bad_cast(self):
        self.assertEqual(range(sys.maxsize).__len__(), sys.maxsize)


kundi ClassPropertiesAndMethods(unittest.TestCase):

    eleza assertHasAttr(self, obj, name):
        self.assertKweli(hasattr(obj, name),
                        '%r has no attribute %r' % (obj, name))

    eleza assertNotHasAttr(self, obj, name):
        self.assertUongo(hasattr(obj, name),
                         '%r has unexpected attribute %r' % (obj, name))

    eleza test_python_dicts(self):
        # Testing Python subkundi of dict...
        self.assertKweli(issubclass(dict, dict))
        self.assertIsInstance({}, dict)
        d = dict()
        self.assertEqual(d, {})
        self.assertIs(d.__class__, dict)
        self.assertIsInstance(d, dict)
        kundi C(dict):
            state = -1
            eleza __init__(self_local, *a, **kw):
                ikiwa a:
                    self.assertEqual(len(a), 1)
                    self_local.state = a[0]
                ikiwa kw:
                    kila k, v kwenye list(kw.items()):
                        self_local[v] = k
            eleza __getitem__(self, key):
                rudisha self.get(key, 0)
            eleza __setitem__(self_local, key, value):
                self.assertIsInstance(key, type(0))
                dict.__setitem__(self_local, key, value)
            eleza setstate(self, state):
                self.state = state
            eleza getstate(self):
                rudisha self.state
        self.assertKweli(issubclass(C, dict))
        a1 = C(12)
        self.assertEqual(a1.state, 12)
        a2 = C(foo=1, bar=2)
        self.assertEqual(a2[1] == 'foo' na a2[2], 'bar')
        a = C()
        self.assertEqual(a.state, -1)
        self.assertEqual(a.getstate(), -1)
        a.setstate(0)
        self.assertEqual(a.state, 0)
        self.assertEqual(a.getstate(), 0)
        a.setstate(10)
        self.assertEqual(a.state, 10)
        self.assertEqual(a.getstate(), 10)
        self.assertEqual(a[42], 0)
        a[42] = 24
        self.assertEqual(a[42], 24)
        N = 50
        kila i kwenye range(N):
            a[i] = C()
            kila j kwenye range(N):
                a[i][j] = i*j
        kila i kwenye range(N):
            kila j kwenye range(N):
                self.assertEqual(a[i][j], i*j)

    eleza test_python_lists(self):
        # Testing Python subkundi of list...
        kundi C(list):
            eleza __getitem__(self, i):
                ikiwa isinstance(i, slice):
                    rudisha i.start, i.stop
                rudisha list.__getitem__(self, i) + 100
        a = C()
        a.extend([0,1,2])
        self.assertEqual(a[0], 100)
        self.assertEqual(a[1], 101)
        self.assertEqual(a[2], 102)
        self.assertEqual(a[100:200], (100,200))

    eleza test_metaclass(self):
        # Testing metaclasses...
        kundi C(metaclass=type):
            eleza __init__(self):
                self.__state = 0
            eleza getstate(self):
                rudisha self.__state
            eleza setstate(self, state):
                self.__state = state
        a = C()
        self.assertEqual(a.getstate(), 0)
        a.setstate(10)
        self.assertEqual(a.getstate(), 10)
        kundi _metaclass(type):
            eleza myself(cls): rudisha cls
        kundi D(metaclass=_metaclass):
            pass
        self.assertEqual(D.myself(), D)
        d = D()
        self.assertEqual(d.__class__, D)
        kundi M1(type):
            eleza __new__(cls, name, bases, dict):
                dict['__spam__'] = 1
                rudisha type.__new__(cls, name, bases, dict)
        kundi C(metaclass=M1):
            pass
        self.assertEqual(C.__spam__, 1)
        c = C()
        self.assertEqual(c.__spam__, 1)

        kundi _instance(object):
            pass
        kundi M2(object):
            @staticmethod
            eleza __new__(cls, name, bases, dict):
                self = object.__new__(cls)
                self.name = name
                self.bases = bases
                self.dict = dict
                rudisha self
            eleza __call__(self):
                it = _instance()
                # Early binding of methods
                kila key kwenye self.dict:
                    ikiwa key.startswith("__"):
                        endelea
                    setattr(it, key, self.dict[key].__get__(it, self))
                rudisha it
        kundi C(metaclass=M2):
            eleza spam(self):
                rudisha 42
        self.assertEqual(C.name, 'C')
        self.assertEqual(C.bases, ())
        self.assertIn('spam', C.dict)
        c = C()
        self.assertEqual(c.spam(), 42)

        # More metakundi examples

        kundi autosuper(type):
            # Automatically add __super to the class
            # This trick only works kila dynamic classes
            eleza __new__(metaclass, name, bases, dict):
                cls = super(autosuper, metaclass).__new__(metaclass,
                                                          name, bases, dict)
                # Name mangling kila __super removes leading underscores
                wakati name[:1] == "_":
                    name = name[1:]
                ikiwa name:
                    name = "_%s__super" % name
                isipokua:
                    name = "__super"
                setattr(cls, name, super(cls))
                rudisha cls
        kundi A(metaclass=autosuper):
            eleza meth(self):
                rudisha "A"
        kundi B(A):
            eleza meth(self):
                rudisha "B" + self.__super.meth()
        kundi C(A):
            eleza meth(self):
                rudisha "C" + self.__super.meth()
        kundi D(C, B):
            eleza meth(self):
                rudisha "D" + self.__super.meth()
        self.assertEqual(D().meth(), "DCBA")
        kundi E(B, C):
            eleza meth(self):
                rudisha "E" + self.__super.meth()
        self.assertEqual(E().meth(), "EBCA")

        kundi autoproperty(type):
            # Automatically create property attributes when methods
            # named _get_x and/or _set_x are found
            eleza __new__(metaclass, name, bases, dict):
                hits = {}
                kila key, val kwenye dict.items():
                    ikiwa key.startswith("_get_"):
                        key = key[5:]
                        get, set = hits.get(key, (Tupu, Tupu))
                        get = val
                        hits[key] = get, set
                    elikiwa key.startswith("_set_"):
                        key = key[5:]
                        get, set = hits.get(key, (Tupu, Tupu))
                        set = val
                        hits[key] = get, set
                kila key, (get, set) kwenye hits.items():
                    dict[key] = property(get, set)
                rudisha super(autoproperty, metaclass).__new__(metaclass,
                                                            name, bases, dict)
        kundi A(metaclass=autoproperty):
            eleza _get_x(self):
                rudisha -self.__x
            eleza _set_x(self, x):
                self.__x = -x
        a = A()
        self.assertNotHasAttr(a, "x")
        a.x = 12
        self.assertEqual(a.x, 12)
        self.assertEqual(a._A__x, -12)

        kundi multimetaclass(autoproperty, autosuper):
            # Merge of multiple cooperating metaclasses
            pass
        kundi A(metaclass=multimetaclass):
            eleza _get_x(self):
                rudisha "A"
        kundi B(A):
            eleza _get_x(self):
                rudisha "B" + self.__super._get_x()
        kundi C(A):
            eleza _get_x(self):
                rudisha "C" + self.__super._get_x()
        kundi D(C, B):
            eleza _get_x(self):
                rudisha "D" + self.__super._get_x()
        self.assertEqual(D().x, "DCBA")

        # Make sure type(x) doesn't call x.__class__.__init__
        kundi T(type):
            counter = 0
            eleza __init__(self, *args):
                T.counter += 1
        kundi C(metaclass=T):
            pass
        self.assertEqual(T.counter, 1)
        a = C()
        self.assertEqual(type(a), C)
        self.assertEqual(T.counter, 1)

        kundi C(object): pass
        c = C()
        jaribu: c()
        except TypeError: pass
        isipokua: self.fail("calling object w/o call method should  ashiria "
                        "TypeError")

        # Testing code to find most derived baseclass
        kundi A(type):
            eleza __new__(*args, **kwargs):
                rudisha type.__new__(*args, **kwargs)

        kundi B(object):
            pass

        kundi C(object, metaclass=A):
            pass

        # The most derived metakundi of D ni A rather than type.
        kundi D(B, C):
            pass
        self.assertIs(A, type(D))

        # issue1294232: correct metakundi calculation
        new_calls = []  # to check the order of __new__ calls
        kundi AMeta(type):
            @staticmethod
            eleza __new__(mcls, name, bases, ns):
                new_calls.append('AMeta')
                rudisha super().__new__(mcls, name, bases, ns)
            @classmethod
            eleza __prepare__(mcls, name, bases):
                rudisha {}

        kundi BMeta(AMeta):
            @staticmethod
            eleza __new__(mcls, name, bases, ns):
                new_calls.append('BMeta')
                rudisha super().__new__(mcls, name, bases, ns)
            @classmethod
            eleza __prepare__(mcls, name, bases):
                ns = super().__prepare__(name, bases)
                ns['BMeta_was_here'] = Kweli
                rudisha ns

        kundi A(metaclass=AMeta):
            pass
        self.assertEqual(['AMeta'], new_calls)
        new_calls.clear()

        kundi B(metaclass=BMeta):
            pass
        # BMeta.__new__ calls AMeta.__new__ ukijumuisha super:
        self.assertEqual(['BMeta', 'AMeta'], new_calls)
        new_calls.clear()

        kundi C(A, B):
            pass
        # The most derived metakundi ni BMeta:
        self.assertEqual(['BMeta', 'AMeta'], new_calls)
        new_calls.clear()
        # BMeta.__prepare__ should've been called:
        self.assertIn('BMeta_was_here', C.__dict__)

        # The order of the bases shouldn't matter:
        kundi C2(B, A):
            pass
        self.assertEqual(['BMeta', 'AMeta'], new_calls)
        new_calls.clear()
        self.assertIn('BMeta_was_here', C2.__dict__)

        # Check correct metakundi calculation when a metakundi ni declared:
        kundi D(C, metaclass=type):
            pass
        self.assertEqual(['BMeta', 'AMeta'], new_calls)
        new_calls.clear()
        self.assertIn('BMeta_was_here', D.__dict__)

        kundi E(C, metaclass=AMeta):
            pass
        self.assertEqual(['BMeta', 'AMeta'], new_calls)
        new_calls.clear()
        self.assertIn('BMeta_was_here', E.__dict__)

        # Special case: the given metakundi isn't a class,
        # so there ni no metakundi calculation.
        marker = object()
        eleza func(*args, **kwargs):
            rudisha marker
        kundi X(metaclass=func):
            pass
        kundi Y(object, metaclass=func):
            pass
        kundi Z(D, metaclass=func):
            pass
        self.assertIs(marker, X)
        self.assertIs(marker, Y)
        self.assertIs(marker, Z)

        # The given metakundi ni a class,
        # but sio a descendant of type.
        prepare_calls = []  # to track __prepare__ calls
        kundi ANotMeta:
            eleza __new__(mcls, *args, **kwargs):
                new_calls.append('ANotMeta')
                rudisha super().__new__(mcls)
            @classmethod
            eleza __prepare__(mcls, name, bases):
                prepare_calls.append('ANotMeta')
                rudisha {}
        kundi BNotMeta(ANotMeta):
            eleza __new__(mcls, *args, **kwargs):
                new_calls.append('BNotMeta')
                rudisha super().__new__(mcls)
            @classmethod
            eleza __prepare__(mcls, name, bases):
                prepare_calls.append('BNotMeta')
                rudisha super().__prepare__(name, bases)

        kundi A(metaclass=ANotMeta):
            pass
        self.assertIs(ANotMeta, type(A))
        self.assertEqual(['ANotMeta'], prepare_calls)
        prepare_calls.clear()
        self.assertEqual(['ANotMeta'], new_calls)
        new_calls.clear()

        kundi B(metaclass=BNotMeta):
            pass
        self.assertIs(BNotMeta, type(B))
        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
        prepare_calls.clear()
        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
        new_calls.clear()

        kundi C(A, B):
            pass
        self.assertIs(BNotMeta, type(C))
        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
        new_calls.clear()
        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
        prepare_calls.clear()

        kundi C2(B, A):
            pass
        self.assertIs(BNotMeta, type(C2))
        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
        new_calls.clear()
        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
        prepare_calls.clear()

        # This ni a TypeError, because of a metakundi conflict:
        # BNotMeta ni neither a subclass, nor a superkundi of type
        ukijumuisha self.assertRaises(TypeError):
            kundi D(C, metaclass=type):
                pass

        kundi E(C, metaclass=ANotMeta):
            pass
        self.assertIs(BNotMeta, type(E))
        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
        new_calls.clear()
        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
        prepare_calls.clear()

        kundi F(object(), C):
            pass
        self.assertIs(BNotMeta, type(F))
        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
        new_calls.clear()
        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
        prepare_calls.clear()

        kundi F2(C, object()):
            pass
        self.assertIs(BNotMeta, type(F2))
        self.assertEqual(['BNotMeta', 'ANotMeta'], new_calls)
        new_calls.clear()
        self.assertEqual(['BNotMeta', 'ANotMeta'], prepare_calls)
        prepare_calls.clear()

        # TypeError: BNotMeta ni neither a
        # subclass, nor a superkundi of int
        ukijumuisha self.assertRaises(TypeError):
            kundi X(C, int()):
                pass
        ukijumuisha self.assertRaises(TypeError):
            kundi X(int(), C):
                pass

    eleza test_module_subclasses(self):
        # Testing Python subkundi of module...
        log = []
        MT = type(sys)
        kundi MM(MT):
            eleza __init__(self, name):
                MT.__init__(self, name)
            eleza __getattribute__(self, name):
                log.append(("getattr", name))
                rudisha MT.__getattribute__(self, name)
            eleza __setattr__(self, name, value):
                log.append(("setattr", name, value))
                MT.__setattr__(self, name, value)
            eleza __delattr__(self, name):
                log.append(("delattr", name))
                MT.__delattr__(self, name)
        a = MM("a")
        a.foo = 12
        x = a.foo
        toa a.foo
        self.assertEqual(log, [("setattr", "foo", 12),
                               ("getattr", "foo"),
                               ("delattr", "foo")])

        # http://python.org/sf/1174712
        jaribu:
            kundi Module(types.ModuleType, str):
                pass
        except TypeError:
            pass
        isipokua:
            self.fail("inheriting kutoka ModuleType na str at the same time "
                      "should fail")

    eleza test_multiple_inheritance(self):
        # Testing multiple inheritance...
        kundi C(object):
            eleza __init__(self):
                self.__state = 0
            eleza getstate(self):
                rudisha self.__state
            eleza setstate(self, state):
                self.__state = state
        a = C()
        self.assertEqual(a.getstate(), 0)
        a.setstate(10)
        self.assertEqual(a.getstate(), 10)
        kundi D(dict, C):
            eleza __init__(self):
                type({}).__init__(self)
                C.__init__(self)
        d = D()
        self.assertEqual(list(d.keys()), [])
        d["hello"] = "world"
        self.assertEqual(list(d.items()), [("hello", "world")])
        self.assertEqual(d["hello"], "world")
        self.assertEqual(d.getstate(), 0)
        d.setstate(10)
        self.assertEqual(d.getstate(), 10)
        self.assertEqual(D.__mro__, (D, dict, C, object))

        # SF bug #442833
        kundi Node(object):
            eleza __int__(self):
                rudisha int(self.foo())
            eleza foo(self):
                rudisha "23"
        kundi Frag(Node, list):
            eleza foo(self):
                rudisha "42"
        self.assertEqual(Node().__int__(), 23)
        self.assertEqual(int(Node()), 23)
        self.assertEqual(Frag().__int__(), 42)
        self.assertEqual(int(Frag()), 42)

    eleza test_diamond_inheritance(self):
        # Testing multiple inheritance special cases...
        kundi A(object):
            eleza spam(self): rudisha "A"
        self.assertEqual(A().spam(), "A")
        kundi B(A):
            eleza boo(self): rudisha "B"
            eleza spam(self): rudisha "B"
        self.assertEqual(B().spam(), "B")
        self.assertEqual(B().boo(), "B")
        kundi C(A):
            eleza boo(self): rudisha "C"
        self.assertEqual(C().spam(), "A")
        self.assertEqual(C().boo(), "C")
        kundi D(B, C): pass
        self.assertEqual(D().spam(), "B")
        self.assertEqual(D().boo(), "B")
        self.assertEqual(D.__mro__, (D, B, C, A, object))
        kundi E(C, B): pass
        self.assertEqual(E().spam(), "B")
        self.assertEqual(E().boo(), "C")
        self.assertEqual(E.__mro__, (E, C, B, A, object))
        # MRO order disagreement
        jaribu:
            kundi F(D, E): pass
        except TypeError:
            pass
        isipokua:
            self.fail("expected MRO order disagreement (F)")
        jaribu:
            kundi G(E, D): pass
        except TypeError:
            pass
        isipokua:
            self.fail("expected MRO order disagreement (G)")

    # see thread python-dev/2002-October/029035.html
    eleza test_ex5_from_c3_switch(self):
        # Testing ex5 kutoka C3 switch discussion...
        kundi A(object): pass
        kundi B(object): pass
        kundi C(object): pass
        kundi X(A): pass
        kundi Y(A): pass
        kundi Z(X,B,Y,C): pass
        self.assertEqual(Z.__mro__, (Z, X, B, Y, A, C, object))

    # see "A Monotonic Superkundi Linearization kila Dylan",
    # by Kim Barrett et al. (OOPSLA 1996)
    eleza test_monotonicity(self):
        # Testing MRO monotonicity...
        kundi Boat(object): pass
        kundi DayBoat(Boat): pass
        kundi WheelBoat(Boat): pass
        kundi EngineLess(DayBoat): pass
        kundi SmallMultihull(DayBoat): pass
        kundi PedalWheelBoat(EngineLess,WheelBoat): pass
        kundi SmallCatamaran(SmallMultihull): pass
        kundi Pedalo(PedalWheelBoat,SmallCatamaran): pass

        self.assertEqual(PedalWheelBoat.__mro__,
              (PedalWheelBoat, EngineLess, DayBoat, WheelBoat, Boat, object))
        self.assertEqual(SmallCatamaran.__mro__,
              (SmallCatamaran, SmallMultihull, DayBoat, Boat, object))
        self.assertEqual(Pedalo.__mro__,
              (Pedalo, PedalWheelBoat, EngineLess, SmallCatamaran,
               SmallMultihull, DayBoat, WheelBoat, Boat, object))

    # see "A Monotonic Superkundi Linearization kila Dylan",
    # by Kim Barrett et al. (OOPSLA 1996)
    eleza test_consistency_with_epg(self):
        # Testing consistency ukijumuisha EPG...
        kundi Pane(object): pass
        kundi ScrollingMixin(object): pass
        kundi EditingMixin(object): pass
        kundi ScrollablePane(Pane,ScrollingMixin): pass
        kundi EditablePane(Pane,EditingMixin): pass
        kundi EditableScrollablePane(ScrollablePane,EditablePane): pass

        self.assertEqual(EditableScrollablePane.__mro__,
              (EditableScrollablePane, ScrollablePane, EditablePane, Pane,
                ScrollingMixin, EditingMixin, object))

    eleza test_mro_disagreement(self):
        # Testing error messages kila MRO disagreement...
        mro_err_msg = """Cannot create a consistent method resolution
order (MRO) kila bases """

        eleza raises(exc, expected, callable, *args):
            jaribu:
                callable(*args)
            except exc as msg:
                # the exact msg ni generally considered an impl detail
                ikiwa support.check_impl_detail():
                    ikiwa sio str(msg).startswith(expected):
                        self.fail("Message %r, expected %r" %
                                  (str(msg), expected))
            isipokua:
                self.fail("Expected %s" % exc)

        kundi A(object): pass
        kundi B(A): pass
        kundi C(object): pass

        # Test some very simple errors
        raises(TypeError, "duplicate base kundi A",
               type, "X", (A, A), {})
        raises(TypeError, mro_err_msg,
               type, "X", (A, B), {})
        raises(TypeError, mro_err_msg,
               type, "X", (A, C, B), {})
        # Test a slightly more complex error
        kundi GridLayout(object): pass
        kundi HorizontalGrid(GridLayout): pass
        kundi VerticalGrid(GridLayout): pass
        kundi HVGrid(HorizontalGrid, VerticalGrid): pass
        kundi VHGrid(VerticalGrid, HorizontalGrid): pass
        raises(TypeError, mro_err_msg,
               type, "ConfusedGrid", (HVGrid, VHGrid), {})

    eleza test_object_class(self):
        # Testing object class...
        a = object()
        self.assertEqual(a.__class__, object)
        self.assertEqual(type(a), object)
        b = object()
        self.assertNotEqual(a, b)
        self.assertNotHasAttr(a, "foo")
        jaribu:
            a.foo = 12
        except (AttributeError, TypeError):
            pass
        isipokua:
            self.fail("object() should sio allow setting a foo attribute")
        self.assertNotHasAttr(object(), "__dict__")

        kundi Cdict(object):
            pass
        x = Cdict()
        self.assertEqual(x.__dict__, {})
        x.foo = 1
        self.assertEqual(x.foo, 1)
        self.assertEqual(x.__dict__, {'foo': 1})

    eleza test_object_class_assignment_between_heaptypes_and_nonheaptypes(self):
        kundi SubType(types.ModuleType):
            a = 1

        m = types.ModuleType("m")
        self.assertKweli(m.__class__ ni types.ModuleType)
        self.assertUongo(hasattr(m, "a"))

        m.__class__ = SubType
        self.assertKweli(m.__class__ ni SubType)
        self.assertKweli(hasattr(m, "a"))

        m.__class__ = types.ModuleType
        self.assertKweli(m.__class__ ni types.ModuleType)
        self.assertUongo(hasattr(m, "a"))

        # Make sure that builtin immutable objects don't support __class__
        # assignment, because the object instances may be interned.
        # We set __slots__ = () to ensure that the subclasses are
        # memory-layout compatible, na thus otherwise reasonable candidates
        # kila __class__ assignment.

        # The following types have immutable instances, but are not
        # subclassable na thus don't need to be checked:
        #   TupuType, bool

        kundi MyInt(int):
            __slots__ = ()
        ukijumuisha self.assertRaises(TypeError):
            (1).__class__ = MyInt

        kundi MyFloat(float):
            __slots__ = ()
        ukijumuisha self.assertRaises(TypeError):
            (1.0).__class__ = MyFloat

        kundi MyComplex(complex):
            __slots__ = ()
        ukijumuisha self.assertRaises(TypeError):
            (1 + 2j).__class__ = MyComplex

        kundi MyStr(str):
            __slots__ = ()
        ukijumuisha self.assertRaises(TypeError):
            "a".__class__ = MyStr

        kundi MyBytes(bytes):
            __slots__ = ()
        ukijumuisha self.assertRaises(TypeError):
            b"a".__class__ = MyBytes

        kundi MyTuple(tuple):
            __slots__ = ()
        ukijumuisha self.assertRaises(TypeError):
            ().__class__ = MyTuple

        kundi MyFrozenSet(frozenset):
            __slots__ = ()
        ukijumuisha self.assertRaises(TypeError):
            frozenset().__class__ = MyFrozenSet

    eleza test_slots(self):
        # Testing __slots__...
        kundi C0(object):
            __slots__ = []
        x = C0()
        self.assertNotHasAttr(x, "__dict__")
        self.assertNotHasAttr(x, "foo")

        kundi C1(object):
            __slots__ = ['a']
        x = C1()
        self.assertNotHasAttr(x, "__dict__")
        self.assertNotHasAttr(x, "a")
        x.a = 1
        self.assertEqual(x.a, 1)
        x.a = Tupu
        self.assertEqual(x.a, Tupu)
        toa x.a
        self.assertNotHasAttr(x, "a")

        kundi C3(object):
            __slots__ = ['a', 'b', 'c']
        x = C3()
        self.assertNotHasAttr(x, "__dict__")
        self.assertNotHasAttr(x, 'a')
        self.assertNotHasAttr(x, 'b')
        self.assertNotHasAttr(x, 'c')
        x.a = 1
        x.b = 2
        x.c = 3
        self.assertEqual(x.a, 1)
        self.assertEqual(x.b, 2)
        self.assertEqual(x.c, 3)

        kundi C4(object):
            """Validate name mangling"""
            __slots__ = ['__a']
            eleza __init__(self, value):
                self.__a = value
            eleza get(self):
                rudisha self.__a
        x = C4(5)
        self.assertNotHasAttr(x, '__dict__')
        self.assertNotHasAttr(x, '__a')
        self.assertEqual(x.get(), 5)
        jaribu:
            x.__a = 6
        except AttributeError:
            pass
        isipokua:
            self.fail("Double underscored names sio mangled")

        # Make sure slot names are proper identifiers
        jaribu:
            kundi C(object):
                __slots__ = [Tupu]
        except TypeError:
            pass
        isipokua:
            self.fail("[Tupu] slots sio caught")
        jaribu:
            kundi C(object):
                __slots__ = ["foo bar"]
        except TypeError:
            pass
        isipokua:
            self.fail("['foo bar'] slots sio caught")
        jaribu:
            kundi C(object):
                __slots__ = ["foo\0bar"]
        except TypeError:
            pass
        isipokua:
            self.fail("['foo\\0bar'] slots sio caught")
        jaribu:
            kundi C(object):
                __slots__ = ["1"]
        except TypeError:
            pass
        isipokua:
            self.fail("['1'] slots sio caught")
        jaribu:
            kundi C(object):
                __slots__ = [""]
        except TypeError:
            pass
        isipokua:
            self.fail("[''] slots sio caught")
        kundi C(object):
            __slots__ = ["a", "a_b", "_a", "A0123456789Z"]
        # XXX(nnorwitz): was there supposed to be something tested
        # kutoka the kundi above?

        # Test a single string ni sio expanded as a sequence.
        kundi C(object):
            __slots__ = "abc"
        c = C()
        c.abc = 5
        self.assertEqual(c.abc, 5)

        # Test unicode slot names
        # Test a single unicode string ni sio expanded as a sequence.
        kundi C(object):
            __slots__ = "abc"
        c = C()
        c.abc = 5
        self.assertEqual(c.abc, 5)

        # _unicode_to_string used to modify slots kwenye certain circumstances
        slots = ("foo", "bar")
        kundi C(object):
            __slots__ = slots
        x = C()
        x.foo = 5
        self.assertEqual(x.foo, 5)
        self.assertIs(type(slots[0]), str)
        # this used to leak references
        jaribu:
            kundi C(object):
                __slots__ = [chr(128)]
        except (TypeError, UnicodeEncodeError):
            pass
        isipokua:
            self.fail("[chr(128)] slots sio caught")

        # Test leaks
        kundi Counted(object):
            counter = 0    # counts the number of instances alive
            eleza __init__(self):
                Counted.counter += 1
            eleza __del__(self):
                Counted.counter -= 1
        kundi C(object):
            __slots__ = ['a', 'b', 'c']
        x = C()
        x.a = Counted()
        x.b = Counted()
        x.c = Counted()
        self.assertEqual(Counted.counter, 3)
        toa x
        support.gc_collect()
        self.assertEqual(Counted.counter, 0)
        kundi D(C):
            pass
        x = D()
        x.a = Counted()
        x.z = Counted()
        self.assertEqual(Counted.counter, 2)
        toa x
        support.gc_collect()
        self.assertEqual(Counted.counter, 0)
        kundi E(D):
            __slots__ = ['e']
        x = E()
        x.a = Counted()
        x.z = Counted()
        x.e = Counted()
        self.assertEqual(Counted.counter, 3)
        toa x
        support.gc_collect()
        self.assertEqual(Counted.counter, 0)

        # Test cyclical leaks [SF bug 519621]
        kundi F(object):
            __slots__ = ['a', 'b']
        s = F()
        s.a = [Counted(), s]
        self.assertEqual(Counted.counter, 1)
        s = Tupu
        support.gc_collect()
        self.assertEqual(Counted.counter, 0)

        # Test lookup leaks [SF bug 572567]
        ikiwa hasattr(gc, 'get_objects'):
            kundi G(object):
                eleza __eq__(self, other):
                    rudisha Uongo
            g = G()
            orig_objects = len(gc.get_objects())
            kila i kwenye range(10):
                g==g
            new_objects = len(gc.get_objects())
            self.assertEqual(orig_objects, new_objects)

        kundi H(object):
            __slots__ = ['a', 'b']
            eleza __init__(self):
                self.a = 1
                self.b = 2
            eleza __del__(self_):
                self.assertEqual(self_.a, 1)
                self.assertEqual(self_.b, 2)
        ukijumuisha support.captured_output('stderr') as s:
            h = H()
            toa h
        self.assertEqual(s.getvalue(), '')

        kundi X(object):
            __slots__ = "a"
        ukijumuisha self.assertRaises(AttributeError):
            toa X().a

    eleza test_slots_special(self):
        # Testing __dict__ na __weakref__ kwenye __slots__...
        kundi D(object):
            __slots__ = ["__dict__"]
        a = D()
        self.assertHasAttr(a, "__dict__")
        self.assertNotHasAttr(a, "__weakref__")
        a.foo = 42
        self.assertEqual(a.__dict__, {"foo": 42})

        kundi W(object):
            __slots__ = ["__weakref__"]
        a = W()
        self.assertHasAttr(a, "__weakref__")
        self.assertNotHasAttr(a, "__dict__")
        jaribu:
            a.foo = 42
        except AttributeError:
            pass
        isipokua:
            self.fail("shouldn't be allowed to set a.foo")

        kundi C1(W, D):
            __slots__ = []
        a = C1()
        self.assertHasAttr(a, "__dict__")
        self.assertHasAttr(a, "__weakref__")
        a.foo = 42
        self.assertEqual(a.__dict__, {"foo": 42})

        kundi C2(D, W):
            __slots__ = []
        a = C2()
        self.assertHasAttr(a, "__dict__")
        self.assertHasAttr(a, "__weakref__")
        a.foo = 42
        self.assertEqual(a.__dict__, {"foo": 42})

    eleza test_slots_special2(self):
        # Testing __qualname__ na __classcell__ kwenye __slots__
        kundi Meta(type):
            eleza __new__(cls, name, bases, namespace, attr):
                self.assertIn(attr, namespace)
                rudisha super().__new__(cls, name, bases, namespace)

        kundi C1:
            eleza __init__(self):
                self.b = 42
        kundi C2(C1, metaclass=Meta, attr="__classcell__"):
            __slots__ = ["__classcell__"]
            eleza __init__(self):
                super().__init__()
        self.assertIsInstance(C2.__dict__["__classcell__"],
                              types.MemberDescriptorType)
        c = C2()
        self.assertEqual(c.b, 42)
        self.assertNotHasAttr(c, "__classcell__")
        c.__classcell__ = 42
        self.assertEqual(c.__classcell__, 42)
        ukijumuisha self.assertRaises(TypeError):
            kundi C3:
                __classcell__ = 42
                __slots__ = ["__classcell__"]

        kundi Q1(metaclass=Meta, attr="__qualname__"):
            __slots__ = ["__qualname__"]
        self.assertEqual(Q1.__qualname__, C1.__qualname__[:-2] + "Q1")
        self.assertIsInstance(Q1.__dict__["__qualname__"],
                              types.MemberDescriptorType)
        q = Q1()
        self.assertNotHasAttr(q, "__qualname__")
        q.__qualname__ = "q"
        self.assertEqual(q.__qualname__, "q")
        ukijumuisha self.assertRaises(TypeError):
            kundi Q2:
                __qualname__ = object()
                __slots__ = ["__qualname__"]

    eleza test_slots_descriptor(self):
        # Issue2115: slot descriptors did sio correctly check
        # the type of the given object
        agiza abc
        kundi MyABC(metaclass=abc.ABCMeta):
            __slots__ = "a"

        kundi Unrelated(object):
            pass
        MyABC.register(Unrelated)

        u = Unrelated()
        self.assertIsInstance(u, MyABC)

        # This used to crash
        self.assertRaises(TypeError, MyABC.a.__set__, u, 3)

    eleza test_dynamics(self):
        # Testing kundi attribute propagation...
        kundi D(object):
            pass
        kundi E(D):
            pass
        kundi F(D):
            pass
        D.foo = 1
        self.assertEqual(D.foo, 1)
        # Test that dynamic attributes are inherited
        self.assertEqual(E.foo, 1)
        self.assertEqual(F.foo, 1)
        # Test dynamic instances
        kundi C(object):
            pass
        a = C()
        self.assertNotHasAttr(a, "foobar")
        C.foobar = 2
        self.assertEqual(a.foobar, 2)
        C.method = lambda self: 42
        self.assertEqual(a.method(), 42)
        C.__repr__ = lambda self: "C()"
        self.assertEqual(repr(a), "C()")
        C.__int__ = lambda self: 100
        self.assertEqual(int(a), 100)
        self.assertEqual(a.foobar, 2)
        self.assertNotHasAttr(a, "spam")
        eleza mygetattr(self, name):
            ikiwa name == "spam":
                rudisha "spam"
             ashiria AttributeError
        C.__getattr__ = mygetattr
        self.assertEqual(a.spam, "spam")
        a.new = 12
        self.assertEqual(a.new, 12)
        eleza mysetattr(self, name, value):
            ikiwa name == "spam":
                 ashiria AttributeError
            rudisha object.__setattr__(self, name, value)
        C.__setattr__ = mysetattr
        jaribu:
            a.spam = "not spam"
        except AttributeError:
            pass
        isipokua:
            self.fail("expected AttributeError")
        self.assertEqual(a.spam, "spam")
        kundi D(C):
            pass
        d = D()
        d.foo = 1
        self.assertEqual(d.foo, 1)

        # Test handling of int*seq na seq*int
        kundi I(int):
            pass
        self.assertEqual("a"*I(2), "aa")
        self.assertEqual(I(2)*"a", "aa")
        self.assertEqual(2*I(3), 6)
        self.assertEqual(I(3)*2, 6)
        self.assertEqual(I(3)*I(2), 6)

        # Test comparison of classes ukijumuisha dynamic metaclasses
        kundi dynamicmetaclass(type):
            pass
        kundi someclass(metaclass=dynamicmetaclass):
            pass
        self.assertNotEqual(someclass, object)

    eleza test_errors(self):
        # Testing errors...
        jaribu:
            kundi C(list, dict):
                pass
        except TypeError:
            pass
        isipokua:
            self.fail("inheritance kutoka both list na dict should be illegal")

        jaribu:
            kundi C(object, Tupu):
                pass
        except TypeError:
            pass
        isipokua:
            self.fail("inheritance kutoka non-type should be illegal")
        kundi Classic:
            pass

        jaribu:
            kundi C(type(len)):
                pass
        except TypeError:
            pass
        isipokua:
            self.fail("inheritance kutoka CFunction should be illegal")

        jaribu:
            kundi C(object):
                __slots__ = 1
        except TypeError:
            pass
        isipokua:
            self.fail("__slots__ = 1 should be illegal")

        jaribu:
            kundi C(object):
                __slots__ = [1]
        except TypeError:
            pass
        isipokua:
            self.fail("__slots__ = [1] should be illegal")

        kundi M1(type):
            pass
        kundi M2(type):
            pass
        kundi A1(object, metaclass=M1):
            pass
        kundi A2(object, metaclass=M2):
            pass
        jaribu:
            kundi B(A1, A2):
                pass
        except TypeError:
            pass
        isipokua:
            self.fail("finding the most derived metakundi should have failed")

    eleza test_classmethods(self):
        # Testing kundi methods...
        kundi C(object):
            eleza foo(*a): rudisha a
            goo = classmethod(foo)
        c = C()
        self.assertEqual(C.goo(1), (C, 1))
        self.assertEqual(c.goo(1), (C, 1))
        self.assertEqual(c.foo(1), (c, 1))
        kundi D(C):
            pass
        d = D()
        self.assertEqual(D.goo(1), (D, 1))
        self.assertEqual(d.goo(1), (D, 1))
        self.assertEqual(d.foo(1), (d, 1))
        self.assertEqual(D.foo(d, 1), (d, 1))
        # Test kila a specific crash (SF bug 528132)
        eleza f(cls, arg): rudisha (cls, arg)
        ff = classmethod(f)
        self.assertEqual(ff.__get__(0, int)(42), (int, 42))
        self.assertEqual(ff.__get__(0)(42), (int, 42))

        # Test super() ukijumuisha classmethods (SF bug 535444)
        self.assertEqual(C.goo.__self__, C)
        self.assertEqual(D.goo.__self__, D)
        self.assertEqual(super(D,D).goo.__self__, D)
        self.assertEqual(super(D,d).goo.__self__, D)
        self.assertEqual(super(D,D).goo(), (D,))
        self.assertEqual(super(D,d).goo(), (D,))

        # Verify that a non-callable will raise
        meth = classmethod(1).__get__(1)
        self.assertRaises(TypeError, meth)

        # Verify that classmethod() doesn't allow keyword args
        jaribu:
            classmethod(f, kw=1)
        except TypeError:
            pass
        isipokua:
            self.fail("classmethod shouldn't accept keyword args")

        cm = classmethod(f)
        self.assertEqual(cm.__dict__, {})
        cm.x = 42
        self.assertEqual(cm.x, 42)
        self.assertEqual(cm.__dict__, {"x" : 42})
        toa cm.x
        self.assertNotHasAttr(cm, "x")

    @support.refcount_test
    eleza test_refleaks_in_classmethod___init__(self):
        gettotalrefcount = support.get_attribute(sys, 'gettotalrefcount')
        cm = classmethod(Tupu)
        refs_before = gettotalrefcount()
        kila i kwenye range(100):
            cm.__init__(Tupu)
        self.assertAlmostEqual(gettotalrefcount() - refs_before, 0, delta=10)

    @support.impl_detail("the module 'xxsubtype' ni internal")
    eleza test_classmethods_in_c(self):
        # Testing C-based kundi methods...
        agiza xxsubtype as spam
        a = (1, 2, 3)
        d = {'abc': 123}
        x, a1, d1 = spam.spamlist.classmeth(*a, **d)
        self.assertEqual(x, spam.spamlist)
        self.assertEqual(a, a1)
        self.assertEqual(d, d1)
        x, a1, d1 = spam.spamlist().classmeth(*a, **d)
        self.assertEqual(x, spam.spamlist)
        self.assertEqual(a, a1)
        self.assertEqual(d, d1)
        spam_cm = spam.spamlist.__dict__['classmeth']
        x2, a2, d2 = spam_cm(spam.spamlist, *a, **d)
        self.assertEqual(x2, spam.spamlist)
        self.assertEqual(a2, a1)
        self.assertEqual(d2, d1)
        kundi SubSpam(spam.spamlist): pass
        x2, a2, d2 = spam_cm(SubSpam, *a, **d)
        self.assertEqual(x2, SubSpam)
        self.assertEqual(a2, a1)
        self.assertEqual(d2, d1)

        ukijumuisha self.assertRaises(TypeError) as cm:
            spam_cm()
        self.assertEqual(
            str(cm.exception),
            "descriptor 'classmeth' of 'xxsubtype.spamlist' "
            "object needs an argument")

        ukijumuisha self.assertRaises(TypeError) as cm:
            spam_cm(spam.spamlist())
        self.assertEqual(
            str(cm.exception),
            "descriptor 'classmeth' requires a type "
            "but received a 'xxsubtype.spamlist' instance")

        ukijumuisha self.assertRaises(TypeError) as cm:
            spam_cm(list)
        expected_errmsg = (
            "descriptor 'classmeth' requires a subtype of 'xxsubtype.spamlist' "
            "but received 'list'")
        self.assertEqual(str(cm.exception), expected_errmsg)

        ukijumuisha self.assertRaises(TypeError) as cm:
            spam_cm.__get__(Tupu, list)
        self.assertEqual(str(cm.exception), expected_errmsg)

    eleza test_staticmethods(self):
        # Testing static methods...
        kundi C(object):
            eleza foo(*a): rudisha a
            goo = staticmethod(foo)
        c = C()
        self.assertEqual(C.goo(1), (1,))
        self.assertEqual(c.goo(1), (1,))
        self.assertEqual(c.foo(1), (c, 1,))
        kundi D(C):
            pass
        d = D()
        self.assertEqual(D.goo(1), (1,))
        self.assertEqual(d.goo(1), (1,))
        self.assertEqual(d.foo(1), (d, 1))
        self.assertEqual(D.foo(d, 1), (d, 1))
        sm = staticmethod(Tupu)
        self.assertEqual(sm.__dict__, {})
        sm.x = 42
        self.assertEqual(sm.x, 42)
        self.assertEqual(sm.__dict__, {"x" : 42})
        toa sm.x
        self.assertNotHasAttr(sm, "x")

    @support.refcount_test
    eleza test_refleaks_in_staticmethod___init__(self):
        gettotalrefcount = support.get_attribute(sys, 'gettotalrefcount')
        sm = staticmethod(Tupu)
        refs_before = gettotalrefcount()
        kila i kwenye range(100):
            sm.__init__(Tupu)
        self.assertAlmostEqual(gettotalrefcount() - refs_before, 0, delta=10)

    @support.impl_detail("the module 'xxsubtype' ni internal")
    eleza test_staticmethods_in_c(self):
        # Testing C-based static methods...
        agiza xxsubtype as spam
        a = (1, 2, 3)
        d = {"abc": 123}
        x, a1, d1 = spam.spamlist.staticmeth(*a, **d)
        self.assertEqual(x, Tupu)
        self.assertEqual(a, a1)
        self.assertEqual(d, d1)
        x, a1, d2 = spam.spamlist().staticmeth(*a, **d)
        self.assertEqual(x, Tupu)
        self.assertEqual(a, a1)
        self.assertEqual(d, d1)

    eleza test_classic(self):
        # Testing classic classes...
        kundi C:
            eleza foo(*a): rudisha a
            goo = classmethod(foo)
        c = C()
        self.assertEqual(C.goo(1), (C, 1))
        self.assertEqual(c.goo(1), (C, 1))
        self.assertEqual(c.foo(1), (c, 1))
        kundi D(C):
            pass
        d = D()
        self.assertEqual(D.goo(1), (D, 1))
        self.assertEqual(d.goo(1), (D, 1))
        self.assertEqual(d.foo(1), (d, 1))
        self.assertEqual(D.foo(d, 1), (d, 1))
        kundi E: # *not* subclassing kutoka C
            foo = C.foo
        self.assertEqual(E().foo.__func__, C.foo) # i.e., unbound
        self.assertKweli(repr(C.foo.__get__(C())).startswith("<bound method "))

    eleza test_compattr(self):
        # Testing computed attributes...
        kundi C(object):
            kundi computed_attribute(object):
                eleza __init__(self, get, set=Tupu, delete=Tupu):
                    self.__get = get
                    self.__set = set
                    self.__delete = delete
                eleza __get__(self, obj, type=Tupu):
                    rudisha self.__get(obj)
                eleza __set__(self, obj, value):
                    rudisha self.__set(obj, value)
                eleza __delete__(self, obj):
                    rudisha self.__delete(obj)
            eleza __init__(self):
                self.__x = 0
            eleza __get_x(self):
                x = self.__x
                self.__x = x+1
                rudisha x
            eleza __set_x(self, x):
                self.__x = x
            eleza __delete_x(self):
                toa self.__x
            x = computed_attribute(__get_x, __set_x, __delete_x)
        a = C()
        self.assertEqual(a.x, 0)
        self.assertEqual(a.x, 1)
        a.x = 10
        self.assertEqual(a.x, 10)
        self.assertEqual(a.x, 11)
        toa a.x
        self.assertNotHasAttr(a, 'x')

    eleza test_newslots(self):
        # Testing __new__ slot override...
        kundi C(list):
            eleza __new__(cls):
                self = list.__new__(cls)
                self.foo = 1
                rudisha self
            eleza __init__(self):
                self.foo = self.foo + 2
        a = C()
        self.assertEqual(a.foo, 3)
        self.assertEqual(a.__class__, C)
        kundi D(C):
            pass
        b = D()
        self.assertEqual(b.foo, 3)
        self.assertEqual(b.__class__, D)

    @unittest.expectedFailure
    eleza test_bad_new(self):
        self.assertRaises(TypeError, object.__new__)
        self.assertRaises(TypeError, object.__new__, '')
        self.assertRaises(TypeError, list.__new__, object)
        self.assertRaises(TypeError, object.__new__, list)
        kundi C(object):
            __new__ = list.__new__
        self.assertRaises(TypeError, C)
        kundi C(list):
            __new__ = object.__new__
        self.assertRaises(TypeError, C)

    eleza test_object_new(self):
        kundi A(object):
            pass
        object.__new__(A)
        self.assertRaises(TypeError, object.__new__, A, 5)
        object.__init__(A())
        self.assertRaises(TypeError, object.__init__, A(), 5)

        kundi A(object):
            eleza __init__(self, foo):
                self.foo = foo
        object.__new__(A)
        object.__new__(A, 5)
        object.__init__(A(3))
        self.assertRaises(TypeError, object.__init__, A(3), 5)

        kundi A(object):
            eleza __new__(cls, foo):
                rudisha object.__new__(cls)
        object.__new__(A)
        self.assertRaises(TypeError, object.__new__, A, 5)
        object.__init__(A(3))
        object.__init__(A(3), 5)

        kundi A(object):
            eleza __new__(cls, foo):
                rudisha object.__new__(cls)
            eleza __init__(self, foo):
                self.foo = foo
        object.__new__(A)
        self.assertRaises(TypeError, object.__new__, A, 5)
        object.__init__(A(3))
        self.assertRaises(TypeError, object.__init__, A(3), 5)

    @unittest.expectedFailure
    eleza test_restored_object_new(self):
        kundi A(object):
            eleza __new__(cls, *args, **kwargs):
                 ashiria AssertionError
        self.assertRaises(AssertionError, A)
        kundi B(A):
            __new__ = object.__new__
            eleza __init__(self, foo):
                self.foo = foo
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('error', DeprecationWarning)
            b = B(3)
        self.assertEqual(b.foo, 3)
        self.assertEqual(b.__class__, B)
        toa B.__new__
        self.assertRaises(AssertionError, B)
        toa A.__new__
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('error', DeprecationWarning)
            b = B(3)
        self.assertEqual(b.foo, 3)
        self.assertEqual(b.__class__, B)

    eleza test_altmro(self):
        # Testing mro() na overriding it...
        kundi A(object):
            eleza f(self): rudisha "A"
        kundi B(A):
            pass
        kundi C(A):
            eleza f(self): rudisha "C"
        kundi D(B, C):
            pass
        self.assertEqual(A.mro(), [A, object])
        self.assertEqual(A.__mro__, (A, object))
        self.assertEqual(B.mro(), [B, A, object])
        self.assertEqual(B.__mro__, (B, A, object))
        self.assertEqual(C.mro(), [C, A, object])
        self.assertEqual(C.__mro__, (C, A, object))
        self.assertEqual(D.mro(), [D, B, C, A, object])
        self.assertEqual(D.__mro__, (D, B, C, A, object))
        self.assertEqual(D().f(), "C")

        kundi PerverseMetaType(type):
            eleza mro(cls):
                L = type.mro(cls)
                L.reverse()
                rudisha L
        kundi X(D,B,C,A, metaclass=PerverseMetaType):
            pass
        self.assertEqual(X.__mro__, (object, A, C, B, D, X))
        self.assertEqual(X().f(), "A")

        jaribu:
            kundi _metaclass(type):
                eleza mro(self):
                    rudisha [self, dict, object]
            kundi X(object, metaclass=_metaclass):
                pass
            # In CPython, the kundi creation above already raises
            # TypeError, as a protection against the fact that
            # instances of X would segfault it.  In other Python
            # implementations it would be ok to let the kundi X
            # be created, but instead get a clean TypeError on the
            # __setitem__ below.
            x = object.__new__(X)
            x[5] = 6
        except TypeError:
            pass
        isipokua:
            self.fail("devious mro() rudisha sio caught")

        jaribu:
            kundi _metaclass(type):
                eleza mro(self):
                    rudisha [1]
            kundi X(object, metaclass=_metaclass):
                pass
        except TypeError:
            pass
        isipokua:
            self.fail("non-kundi mro() rudisha sio caught")

        jaribu:
            kundi _metaclass(type):
                eleza mro(self):
                    rudisha 1
            kundi X(object, metaclass=_metaclass):
                pass
        except TypeError:
            pass
        isipokua:
            self.fail("non-sequence mro() rudisha sio caught")

    eleza test_overloading(self):
        # Testing operator overloading...

        kundi B(object):
            "Intermediate kundi because object doesn't have a __setattr__"

        kundi C(B):
            eleza __getattr__(self, name):
                ikiwa name == "foo":
                    rudisha ("getattr", name)
                isipokua:
                     ashiria AttributeError
            eleza __setattr__(self, name, value):
                ikiwa name == "foo":
                    self.setattr = (name, value)
                isipokua:
                    rudisha B.__setattr__(self, name, value)
            eleza __delattr__(self, name):
                ikiwa name == "foo":
                    self.delattr = name
                isipokua:
                    rudisha B.__delattr__(self, name)

            eleza __getitem__(self, key):
                rudisha ("getitem", key)
            eleza __setitem__(self, key, value):
                self.setitem = (key, value)
            eleza __delitem__(self, key):
                self.delitem = key

        a = C()
        self.assertEqual(a.foo, ("getattr", "foo"))
        a.foo = 12
        self.assertEqual(a.setattr, ("foo", 12))
        toa a.foo
        self.assertEqual(a.delattr, "foo")

        self.assertEqual(a[12], ("getitem", 12))
        a[12] = 21
        self.assertEqual(a.setitem, (12, 21))
        toa a[12]
        self.assertEqual(a.delitem, 12)

        self.assertEqual(a[0:10], ("getitem", slice(0, 10)))
        a[0:10] = "foo"
        self.assertEqual(a.setitem, (slice(0, 10), "foo"))
        toa a[0:10]
        self.assertEqual(a.delitem, (slice(0, 10)))

    eleza test_methods(self):
        # Testing methods...
        kundi C(object):
            eleza __init__(self, x):
                self.x = x
            eleza foo(self):
                rudisha self.x
        c1 = C(1)
        self.assertEqual(c1.foo(), 1)
        kundi D(C):
            boo = C.foo
            goo = c1.foo
        d2 = D(2)
        self.assertEqual(d2.foo(), 2)
        self.assertEqual(d2.boo(), 2)
        self.assertEqual(d2.goo(), 1)
        kundi E(object):
            foo = C.foo
        self.assertEqual(E().foo.__func__, C.foo) # i.e., unbound
        self.assertKweli(repr(C.foo.__get__(C(1))).startswith("<bound method "))

    @support.impl_detail("testing error message kutoka implementation")
    eleza test_methods_in_c(self):
        # This test checks error messages kwenye builtin method descriptor.
        # It ni allowed that other Python implementations use
        # different error messages.
        set_add = set.add

        expected_errmsg = "descriptor 'add' of 'set' object needs an argument"

        ukijumuisha self.assertRaises(TypeError) as cm:
            set_add()
        self.assertEqual(cm.exception.args[0], expected_errmsg)

        expected_errmsg = "descriptor 'add' kila 'set' objects doesn't apply to a 'int' object"

        ukijumuisha self.assertRaises(TypeError) as cm:
            set_add(0)
        self.assertEqual(cm.exception.args[0], expected_errmsg)

        ukijumuisha self.assertRaises(TypeError) as cm:
            set_add.__get__(0)
        self.assertEqual(cm.exception.args[0], expected_errmsg)

    eleza test_special_method_lookup(self):
        # The lookup of special methods bypasses __getattr__ and
        # __getattribute__, but they still can be descriptors.

        eleza run_context(manager):
            ukijumuisha manager:
                pass
        eleza iden(self):
            rudisha self
        eleza hello(self):
            rudisha b"hello"
        eleza empty_seq(self):
            rudisha []
        eleza zero(self):
            rudisha 0
        eleza complex_num(self):
            rudisha 1j
        eleza stop(self):
             ashiria StopIteration
        eleza return_true(self, thing=Tupu):
            rudisha Kweli
        eleza do_isinstance(obj):
            rudisha isinstance(int, obj)
        eleza do_issubclass(obj):
            rudisha issubclass(int, obj)
        eleza do_dict_missing(checker):
            kundi DictSub(checker.__class__, dict):
                pass
            self.assertEqual(DictSub()["hi"], 4)
        eleza some_number(self_, key):
            self.assertEqual(key, "hi")
            rudisha 4
        eleza swallow(*args): pass
        eleza format_impl(self, spec):
            rudisha "hello"

        # It would be nice to have every special method tested here, but I'm
        # only listing the ones I can remember outside of typeobject.c, since it
        # does it right.
        specials = [
            ("__bytes__", bytes, hello, set(), {}),
            ("__reversed__", reversed, empty_seq, set(), {}),
            ("__length_hint__", list, zero, set(),
             {"__iter__" : iden, "__next__" : stop}),
            ("__sizeof__", sys.getsizeof, zero, set(), {}),
            ("__instancecheck__", do_isinstance, return_true, set(), {}),
            ("__missing__", do_dict_missing, some_number,
             set(("__class__",)), {}),
            ("__subclasscheck__", do_issubclass, return_true,
             set(("__bases__",)), {}),
            ("__enter__", run_context, iden, set(), {"__exit__" : swallow}),
            ("__exit__", run_context, swallow, set(), {"__enter__" : iden}),
            ("__complex__", complex, complex_num, set(), {}),
            ("__format__", format, format_impl, set(), {}),
            ("__floor__", math.floor, zero, set(), {}),
            ("__trunc__", math.trunc, zero, set(), {}),
            ("__trunc__", int, zero, set(), {}),
            ("__ceil__", math.ceil, zero, set(), {}),
            ("__dir__", dir, empty_seq, set(), {}),
            ("__round__", round, zero, set(), {}),
            ]

        kundi Checker(object):
            eleza __getattr__(self, attr, test=self):
                test.fail("__getattr__ called ukijumuisha {0}".format(attr))
            eleza __getattribute__(self, attr, test=self):
                ikiwa attr sio kwenye ok:
                    test.fail("__getattribute__ called ukijumuisha {0}".format(attr))
                rudisha object.__getattribute__(self, attr)
        kundi SpecialDescr(object):
            eleza __init__(self, impl):
                self.impl = impl
            eleza __get__(self, obj, owner):
                record.append(1)
                rudisha self.impl.__get__(obj, owner)
        kundi MyException(Exception):
            pass
        kundi ErrDescr(object):
            eleza __get__(self, obj, owner):
                 ashiria MyException

        kila name, runner, meth_impl, ok, env kwenye specials:
            kundi X(Checker):
                pass
            kila attr, obj kwenye env.items():
                setattr(X, attr, obj)
            setattr(X, name, meth_impl)
            runner(X())

            record = []
            kundi X(Checker):
                pass
            kila attr, obj kwenye env.items():
                setattr(X, attr, obj)
            setattr(X, name, SpecialDescr(meth_impl))
            runner(X())
            self.assertEqual(record, [1], name)

            kundi X(Checker):
                pass
            kila attr, obj kwenye env.items():
                setattr(X, attr, obj)
            setattr(X, name, ErrDescr())
            self.assertRaises(MyException, runner, X())

    eleza test_specials(self):
        # Testing special operators...
        # Test operators like __hash__ kila which a built-in default exists

        # Test the default behavior kila static classes
        kundi C(object):
            eleza __getitem__(self, i):
                ikiwa 0 <= i < 10: rudisha i
                 ashiria IndexError
        c1 = C()
        c2 = C()
        self.assertUongo(not c1)
        self.assertNotEqual(id(c1), id(c2))
        hash(c1)
        hash(c2)
        self.assertEqual(c1, c1)
        self.assertKweli(c1 != c2)
        self.assertUongo(c1 != c1)
        self.assertUongo(c1 == c2)
        # Note that the module name appears kwenye str/repr, na that varies
        # depending on whether this test ni run standalone ama kutoka a framework.
        self.assertGreaterEqual(str(c1).find('C object at '), 0)
        self.assertEqual(str(c1), repr(c1))
        self.assertNotIn(-1, c1)
        kila i kwenye range(10):
            self.assertIn(i, c1)
        self.assertNotIn(10, c1)
        # Test the default behavior kila dynamic classes
        kundi D(object):
            eleza __getitem__(self, i):
                ikiwa 0 <= i < 10: rudisha i
                 ashiria IndexError
        d1 = D()
        d2 = D()
        self.assertUongo(not d1)
        self.assertNotEqual(id(d1), id(d2))
        hash(d1)
        hash(d2)
        self.assertEqual(d1, d1)
        self.assertNotEqual(d1, d2)
        self.assertUongo(d1 != d1)
        self.assertUongo(d1 == d2)
        # Note that the module name appears kwenye str/repr, na that varies
        # depending on whether this test ni run standalone ama kutoka a framework.
        self.assertGreaterEqual(str(d1).find('D object at '), 0)
        self.assertEqual(str(d1), repr(d1))
        self.assertNotIn(-1, d1)
        kila i kwenye range(10):
            self.assertIn(i, d1)
        self.assertNotIn(10, d1)
        # Test overridden behavior
        kundi Proxy(object):
            eleza __init__(self, x):
                self.x = x
            eleza __bool__(self):
                rudisha sio sio self.x
            eleza __hash__(self):
                rudisha hash(self.x)
            eleza __eq__(self, other):
                rudisha self.x == other
            eleza __ne__(self, other):
                rudisha self.x != other
            eleza __ge__(self, other):
                rudisha self.x >= other
            eleza __gt__(self, other):
                rudisha self.x > other
            eleza __le__(self, other):
                rudisha self.x <= other
            eleza __lt__(self, other):
                rudisha self.x < other
            eleza __str__(self):
                rudisha "Proxy:%s" % self.x
            eleza __repr__(self):
                rudisha "Proxy(%r)" % self.x
            eleza __contains__(self, value):
                rudisha value kwenye self.x
        p0 = Proxy(0)
        p1 = Proxy(1)
        p_1 = Proxy(-1)
        self.assertUongo(p0)
        self.assertUongo(not p1)
        self.assertEqual(hash(p0), hash(0))
        self.assertEqual(p0, p0)
        self.assertNotEqual(p0, p1)
        self.assertUongo(p0 != p0)
        self.assertEqual(not p0, p1)
        self.assertKweli(p0 < p1)
        self.assertKweli(p0 <= p1)
        self.assertKweli(p1 > p0)
        self.assertKweli(p1 >= p0)
        self.assertEqual(str(p0), "Proxy:0")
        self.assertEqual(repr(p0), "Proxy(0)")
        p10 = Proxy(range(10))
        self.assertNotIn(-1, p10)
        kila i kwenye range(10):
            self.assertIn(i, p10)
        self.assertNotIn(10, p10)

    eleza test_weakrefs(self):
        # Testing weak references...
        agiza weakref
        kundi C(object):
            pass
        c = C()
        r = weakref.ref(c)
        self.assertEqual(r(), c)
        toa c
        support.gc_collect()
        self.assertEqual(r(), Tupu)
        toa r
        kundi NoWeak(object):
            __slots__ = ['foo']
        no = NoWeak()
        jaribu:
            weakref.ref(no)
        except TypeError as msg:
            self.assertIn("weak reference", str(msg))
        isipokua:
            self.fail("weakref.ref(no) should be illegal")
        kundi Weak(object):
            __slots__ = ['foo', '__weakref__']
        yes = Weak()
        r = weakref.ref(yes)
        self.assertEqual(r(), yes)
        toa yes
        support.gc_collect()
        self.assertEqual(r(), Tupu)
        toa r

    eleza test_properties(self):
        # Testing property...
        kundi C(object):
            eleza getx(self):
                rudisha self.__x
            eleza setx(self, value):
                self.__x = value
            eleza delx(self):
                toa self.__x
            x = property(getx, setx, delx, doc="I'm the x property.")
        a = C()
        self.assertNotHasAttr(a, "x")
        a.x = 42
        self.assertEqual(a._C__x, 42)
        self.assertEqual(a.x, 42)
        toa a.x
        self.assertNotHasAttr(a, "x")
        self.assertNotHasAttr(a, "_C__x")
        C.x.__set__(a, 100)
        self.assertEqual(C.x.__get__(a), 100)
        C.x.__delete__(a)
        self.assertNotHasAttr(a, "x")

        raw = C.__dict__['x']
        self.assertIsInstance(raw, property)

        attrs = dir(raw)
        self.assertIn("__doc__", attrs)
        self.assertIn("fget", attrs)
        self.assertIn("fset", attrs)
        self.assertIn("fdel", attrs)

        self.assertEqual(raw.__doc__, "I'm the x property.")
        self.assertIs(raw.fget, C.__dict__['getx'])
        self.assertIs(raw.fset, C.__dict__['setx'])
        self.assertIs(raw.fdel, C.__dict__['delx'])

        kila attr kwenye "fget", "fset", "fdel":
            jaribu:
                setattr(raw, attr, 42)
            except AttributeError as msg:
                ikiwa str(msg).find('readonly') < 0:
                    self.fail("when setting readonly attr %r on a property, "
                              "got unexpected AttributeError msg %r" % (attr, str(msg)))
            isipokua:
                self.fail("expected AttributeError kutoka trying to set readonly %r "
                          "attr on a property" % attr)

        raw.__doc__ = 42
        self.assertEqual(raw.__doc__, 42)

        kundi D(object):
            __getitem__ = property(lambda s: 1/0)

        d = D()
        jaribu:
            kila i kwenye d:
                str(i)
        except ZeroDivisionError:
            pass
        isipokua:
            self.fail("expected ZeroDivisionError kutoka bad property")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    eleza test_properties_doc_attrib(self):
        kundi E(object):
            eleza getter(self):
                "getter method"
                rudisha 0
            eleza setter(self_, value):
                "setter method"
                pass
            prop = property(getter)
            self.assertEqual(prop.__doc__, "getter method")
            prop2 = property(fset=setter)
            self.assertEqual(prop2.__doc__, Tupu)

    @support.cpython_only
    eleza test_testcapi_no_segfault(self):
        # this segfaulted kwenye 2.5b2
        jaribu:
            agiza _testcapi
        except ImportError:
            pass
        isipokua:
            kundi X(object):
                p = property(_testcapi.test_with_docstring)

    eleza test_properties_plus(self):
        kundi C(object):
            foo = property(doc="hello")
            @foo.getter
            eleza foo(self):
                rudisha self._foo
            @foo.setter
            eleza foo(self, value):
                self._foo = abs(value)
            @foo.deleter
            eleza foo(self):
                toa self._foo
        c = C()
        self.assertEqual(C.foo.__doc__, "hello")
        self.assertNotHasAttr(c, "foo")
        c.foo = -42
        self.assertHasAttr(c, '_foo')
        self.assertEqual(c._foo, 42)
        self.assertEqual(c.foo, 42)
        toa c.foo
        self.assertNotHasAttr(c, '_foo')
        self.assertNotHasAttr(c, "foo")

        kundi D(C):
            @C.foo.deleter
            eleza foo(self):
                jaribu:
                    toa self._foo
                except AttributeError:
                    pass
        d = D()
        d.foo = 24
        self.assertEqual(d.foo, 24)
        toa d.foo
        toa d.foo

        kundi E(object):
            @property
            eleza foo(self):
                rudisha self._foo
            @foo.setter
            eleza foo(self, value):
                 ashiria RuntimeError
            @foo.setter
            eleza foo(self, value):
                self._foo = abs(value)
            @foo.deleter
            eleza foo(self, value=Tupu):
                toa self._foo

        e = E()
        e.foo = -42
        self.assertEqual(e.foo, 42)
        toa e.foo

        kundi F(E):
            @E.foo.deleter
            eleza foo(self):
                toa self._foo
            @foo.setter
            eleza foo(self, value):
                self._foo = max(0, value)
        f = F()
        f.foo = -10
        self.assertEqual(f.foo, 0)
        toa f.foo

    eleza test_dict_constructors(self):
        # Testing dict constructor ...
        d = dict()
        self.assertEqual(d, {})
        d = dict({})
        self.assertEqual(d, {})
        d = dict({1: 2, 'a': 'b'})
        self.assertEqual(d, {1: 2, 'a': 'b'})
        self.assertEqual(d, dict(list(d.items())))
        self.assertEqual(d, dict(iter(d.items())))
        d = dict({'one':1, 'two':2})
        self.assertEqual(d, dict(one=1, two=2))
        self.assertEqual(d, dict(**d))
        self.assertEqual(d, dict({"one": 1}, two=2))
        self.assertEqual(d, dict([("two", 2)], one=1))
        self.assertEqual(d, dict([("one", 100), ("two", 200)], **d))
        self.assertEqual(d, dict(**d))

        kila badarg kwenye 0, 0, 0j, "0", [0], (0,):
            jaribu:
                dict(badarg)
            except TypeError:
                pass
            except ValueError:
                ikiwa badarg == "0":
                    # It's a sequence, na its elements are also sequences (gotta
                    # love strings <wink>), but they aren't of length 2, so this
                    # one seemed better as a ValueError than a TypeError.
                    pass
                isipokua:
                    self.fail("no TypeError kutoka dict(%r)" % badarg)
            isipokua:
                self.fail("no TypeError kutoka dict(%r)" % badarg)

        jaribu:
            dict({}, {})
        except TypeError:
            pass
        isipokua:
            self.fail("no TypeError kutoka dict({}, {})")

        kundi Mapping:
            # Lacks a .keys() method; will be added later.
            dict = {1:2, 3:4, 'a':1j}

        jaribu:
            dict(Mapping())
        except TypeError:
            pass
        isipokua:
            self.fail("no TypeError kutoka dict(incomplete mapping)")

        Mapping.keys = lambda self: list(self.dict.keys())
        Mapping.__getitem__ = lambda self, i: self.dict[i]
        d = dict(Mapping())
        self.assertEqual(d, Mapping.dict)

        # Init kutoka sequence of iterable objects, each producing a 2-sequence.
        kundi AddressBookEnjaribu:
            eleza __init__(self, first, last):
                self.first = first
                self.last = last
            eleza __iter__(self):
                rudisha iter([self.first, self.last])

        d = dict([AddressBookEntry('Tim', 'Warsaw'),
                  AddressBookEntry('Barry', 'Peters'),
                  AddressBookEntry('Tim', 'Peters'),
                  AddressBookEntry('Barry', 'Warsaw')])
        self.assertEqual(d, {'Barry': 'Warsaw', 'Tim': 'Peters'})

        d = dict(zip(range(4), range(1, 5)))
        self.assertEqual(d, dict([(i, i+1) kila i kwenye range(4)]))

        # Bad sequence lengths.
        kila bad kwenye [('tooshort',)], [('too', 'long', 'by 1')]:
            jaribu:
                dict(bad)
            except ValueError:
                pass
            isipokua:
                self.fail("no ValueError kutoka dict(%r)" % bad)

    eleza test_dir(self):
        # Testing dir() ...
        junk = 12
        self.assertEqual(dir(), ['junk', 'self'])
        toa junk

        # Just make sure these don't blow up!
        kila arg kwenye 2, 2, 2j, 2e0, [2], "2", b"2", (2,), {2:2}, type, self.test_dir:
            dir(arg)

        # Test dir on new-style classes.  Since these have object as a
        # base class, a lot more gets sucked in.
        eleza interesting(strings):
            rudisha [s kila s kwenye strings ikiwa sio s.startswith('_')]

        kundi C(object):
            Cdata = 1
            eleza Cmethod(self): pass

        cstuff = ['Cdata', 'Cmethod']
        self.assertEqual(interesting(dir(C)), cstuff)

        c = C()
        self.assertEqual(interesting(dir(c)), cstuff)
        ## self.assertIn('__self__', dir(C.Cmethod))

        c.cdata = 2
        c.cmethod = lambda self: 0
        self.assertEqual(interesting(dir(c)), cstuff + ['cdata', 'cmethod'])
        ## self.assertIn('__self__', dir(c.Cmethod))

        kundi A(C):
            Adata = 1
            eleza Amethod(self): pass

        astuff = ['Adata', 'Amethod'] + cstuff
        self.assertEqual(interesting(dir(A)), astuff)
        ## self.assertIn('__self__', dir(A.Amethod))
        a = A()
        self.assertEqual(interesting(dir(a)), astuff)
        a.adata = 42
        a.amethod = lambda self: 3
        self.assertEqual(interesting(dir(a)), astuff + ['adata', 'amethod'])
        ## self.assertIn('__self__', dir(a.Amethod))

        # Try a module subclass.
        kundi M(type(sys)):
            pass
        minstance = M("m")
        minstance.b = 2
        minstance.a = 1
        default_attributes = ['__name__', '__doc__', '__package__',
                              '__loader__', '__spec__']
        names = [x kila x kwenye dir(minstance) ikiwa x sio kwenye default_attributes]
        self.assertEqual(names, ['a', 'b'])

        kundi M2(M):
            eleza getdict(self):
                rudisha "Not a dict!"
            __dict__ = property(getdict)

        m2instance = M2("m2")
        m2instance.b = 2
        m2instance.a = 1
        self.assertEqual(m2instance.__dict__, "Not a dict!")
        jaribu:
            dir(m2instance)
        except TypeError:
            pass

        # Two essentially featureless objects, just inheriting stuff from
        # object.
        self.assertEqual(dir(NotImplemented), dir(Ellipsis))

        # Nasty test case kila proxied objects
        kundi Wrapper(object):
            eleza __init__(self, obj):
                self.__obj = obj
            eleza __repr__(self):
                rudisha "Wrapper(%s)" % repr(self.__obj)
            eleza __getitem__(self, key):
                rudisha Wrapper(self.__obj[key])
            eleza __len__(self):
                rudisha len(self.__obj)
            eleza __getattr__(self, name):
                rudisha Wrapper(getattr(self.__obj, name))

        kundi C(object):
            eleza __getclass(self):
                rudisha Wrapper(type(self))
            __class__ = property(__getclass)

        dir(C()) # This used to segfault

    eleza test_supers(self):
        # Testing super...

        kundi A(object):
            eleza meth(self, a):
                rudisha "A(%r)" % a

        self.assertEqual(A().meth(1), "A(1)")

        kundi B(A):
            eleza __init__(self):
                self.__super = super(B, self)
            eleza meth(self, a):
                rudisha "B(%r)" % a + self.__super.meth(a)

        self.assertEqual(B().meth(2), "B(2)A(2)")

        kundi C(A):
            eleza meth(self, a):
                rudisha "C(%r)" % a + self.__super.meth(a)
        C._C__super = super(C)

        self.assertEqual(C().meth(3), "C(3)A(3)")

        kundi D(C, B):
            eleza meth(self, a):
                rudisha "D(%r)" % a + super(D, self).meth(a)

        self.assertEqual(D().meth(4), "D(4)C(4)B(4)A(4)")

        # Test kila subclassing super

        kundi mysuper(super):
            eleza __init__(self, *args):
                rudisha super(mysuper, self).__init__(*args)

        kundi E(D):
            eleza meth(self, a):
                rudisha "E(%r)" % a + mysuper(E, self).meth(a)

        self.assertEqual(E().meth(5), "E(5)D(5)C(5)B(5)A(5)")

        kundi F(E):
            eleza meth(self, a):
                s = self.__super # == mysuper(F, self)
                rudisha "F(%r)[%s]" % (a, s.__class__.__name__) + s.meth(a)
        F._F__super = mysuper(F)

        self.assertEqual(F().meth(6), "F(6)[mysuper]E(6)D(6)C(6)B(6)A(6)")

        # Make sure certain errors are raised

        jaribu:
            super(D, 42)
        except TypeError:
            pass
        isipokua:
            self.fail("shouldn't allow super(D, 42)")

        jaribu:
            super(D, C())
        except TypeError:
            pass
        isipokua:
            self.fail("shouldn't allow super(D, C())")

        jaribu:
            super(D).__get__(12)
        except TypeError:
            pass
        isipokua:
            self.fail("shouldn't allow super(D).__get__(12)")

        jaribu:
            super(D).__get__(C())
        except TypeError:
            pass
        isipokua:
            self.fail("shouldn't allow super(D).__get__(C())")

        # Make sure data descriptors can be overridden na accessed via super
        # (new feature kwenye Python 2.3)

        kundi DDbase(object):
            eleza getx(self): rudisha 42
            x = property(getx)

        kundi DDsub(DDbase):
            eleza getx(self): rudisha "hello"
            x = property(getx)

        dd = DDsub()
        self.assertEqual(dd.x, "hello")
        self.assertEqual(super(DDsub, dd).x, 42)

        # Ensure that super() lookup of descriptor kutoka classmethod
        # works (SF ID# 743627)

        kundi Base(object):
            aProp = property(lambda self: "foo")

        kundi Sub(Base):
            @classmethod
            eleza test(klass):
                rudisha super(Sub,klass).aProp

        self.assertEqual(Sub.test(), Base.aProp)

        # Verify that super() doesn't allow keyword args
        ukijumuisha self.assertRaises(TypeError):
            super(Base, kw=1)

    eleza test_basic_inheritance(self):
        # Testing inheritance kutoka basic types...

        kundi hexint(int):
            eleza __repr__(self):
                rudisha hex(self)
            eleza __add__(self, other):
                rudisha hexint(int.__add__(self, other))
            # (Note that overriding __radd__ doesn't work,
            # because the int type gets first dibs.)
        self.assertEqual(repr(hexint(7) + 9), "0x10")
        self.assertEqual(repr(hexint(1000) + 7), "0x3ef")
        a = hexint(12345)
        self.assertEqual(a, 12345)
        self.assertEqual(int(a), 12345)
        self.assertIs(int(a).__class__, int)
        self.assertEqual(hash(a), hash(12345))
        self.assertIs((+a).__class__, int)
        self.assertIs((a >> 0).__class__, int)
        self.assertIs((a << 0).__class__, int)
        self.assertIs((hexint(0) << 12).__class__, int)
        self.assertIs((hexint(0) >> 12).__class__, int)

        kundi octlong(int):
            __slots__ = []
            eleza __str__(self):
                rudisha oct(self)
            eleza __add__(self, other):
                rudisha self.__class__(super(octlong, self).__add__(other))
            __radd__ = __add__
        self.assertEqual(str(octlong(3) + 5), "0o10")
        # (Note that overriding __radd__ here only seems to work
        # because the example uses a short int left argument.)
        self.assertEqual(str(5 + octlong(3000)), "0o5675")
        a = octlong(12345)
        self.assertEqual(a, 12345)
        self.assertEqual(int(a), 12345)
        self.assertEqual(hash(a), hash(12345))
        self.assertIs(int(a).__class__, int)
        self.assertIs((+a).__class__, int)
        self.assertIs((-a).__class__, int)
        self.assertIs((-octlong(0)).__class__, int)
        self.assertIs((a >> 0).__class__, int)
        self.assertIs((a << 0).__class__, int)
        self.assertIs((a - 0).__class__, int)
        self.assertIs((a * 1).__class__, int)
        self.assertIs((a ** 1).__class__, int)
        self.assertIs((a // 1).__class__, int)
        self.assertIs((1 * a).__class__, int)
        self.assertIs((a | 0).__class__, int)
        self.assertIs((a ^ 0).__class__, int)
        self.assertIs((a & -1).__class__, int)
        self.assertIs((octlong(0) << 12).__class__, int)
        self.assertIs((octlong(0) >> 12).__class__, int)
        self.assertIs(abs(octlong(0)).__class__, int)

        # Because octlong overrides __add__, we can't check the absence of +0
        # optimizations using octlong.
        kundi longclone(int):
            pass
        a = longclone(1)
        self.assertIs((a + 0).__class__, int)
        self.assertIs((0 + a).__class__, int)

        # Check that negative clones don't segfault
        a = longclone(-1)
        self.assertEqual(a.__dict__, {})
        self.assertEqual(int(a), -1)  # self.assertKweli PyNumber_Long() copies the sign bit

        kundi precfloat(float):
            __slots__ = ['prec']
            eleza __init__(self, value=0.0, prec=12):
                self.prec = int(prec)
            eleza __repr__(self):
                rudisha "%.*g" % (self.prec, self)
        self.assertEqual(repr(precfloat(1.1)), "1.1")
        a = precfloat(12345)
        self.assertEqual(a, 12345.0)
        self.assertEqual(float(a), 12345.0)
        self.assertIs(float(a).__class__, float)
        self.assertEqual(hash(a), hash(12345.0))
        self.assertIs((+a).__class__, float)

        kundi madcomplex(complex):
            eleza __repr__(self):
                rudisha "%.17gj%+.17g" % (self.imag, self.real)
        a = madcomplex(-3, 4)
        self.assertEqual(repr(a), "4j-3")
        base = complex(-3, 4)
        self.assertEqual(base.__class__, complex)
        self.assertEqual(a, base)
        self.assertEqual(complex(a), base)
        self.assertEqual(complex(a).__class__, complex)
        a = madcomplex(a)  # just trying another form of the constructor
        self.assertEqual(repr(a), "4j-3")
        self.assertEqual(a, base)
        self.assertEqual(complex(a), base)
        self.assertEqual(complex(a).__class__, complex)
        self.assertEqual(hash(a), hash(base))
        self.assertEqual((+a).__class__, complex)
        self.assertEqual((a + 0).__class__, complex)
        self.assertEqual(a + 0, base)
        self.assertEqual((a - 0).__class__, complex)
        self.assertEqual(a - 0, base)
        self.assertEqual((a * 1).__class__, complex)
        self.assertEqual(a * 1, base)
        self.assertEqual((a / 1).__class__, complex)
        self.assertEqual(a / 1, base)

        kundi madtuple(tuple):
            _rev = Tupu
            eleza rev(self):
                ikiwa self._rev ni sio Tupu:
                    rudisha self._rev
                L = list(self)
                L.reverse()
                self._rev = self.__class__(L)
                rudisha self._rev
        a = madtuple((1,2,3,4,5,6,7,8,9,0))
        self.assertEqual(a, (1,2,3,4,5,6,7,8,9,0))
        self.assertEqual(a.rev(), madtuple((0,9,8,7,6,5,4,3,2,1)))
        self.assertEqual(a.rev().rev(), madtuple((1,2,3,4,5,6,7,8,9,0)))
        kila i kwenye range(512):
            t = madtuple(range(i))
            u = t.rev()
            v = u.rev()
            self.assertEqual(v, t)
        a = madtuple((1,2,3,4,5))
        self.assertEqual(tuple(a), (1,2,3,4,5))
        self.assertIs(tuple(a).__class__, tuple)
        self.assertEqual(hash(a), hash((1,2,3,4,5)))
        self.assertIs(a[:].__class__, tuple)
        self.assertIs((a * 1).__class__, tuple)
        self.assertIs((a * 0).__class__, tuple)
        self.assertIs((a + ()).__class__, tuple)
        a = madtuple(())
        self.assertEqual(tuple(a), ())
        self.assertIs(tuple(a).__class__, tuple)
        self.assertIs((a + a).__class__, tuple)
        self.assertIs((a * 0).__class__, tuple)
        self.assertIs((a * 1).__class__, tuple)
        self.assertIs((a * 2).__class__, tuple)
        self.assertIs(a[:].__class__, tuple)

        kundi madstring(str):
            _rev = Tupu
            eleza rev(self):
                ikiwa self._rev ni sio Tupu:
                    rudisha self._rev
                L = list(self)
                L.reverse()
                self._rev = self.__class__("".join(L))
                rudisha self._rev
        s = madstring("abcdefghijklmnopqrstuvwxyz")
        self.assertEqual(s, "abcdefghijklmnopqrstuvwxyz")
        self.assertEqual(s.rev(), madstring("zyxwvutsrqponmlkjihgfedcba"))
        self.assertEqual(s.rev().rev(), madstring("abcdefghijklmnopqrstuvwxyz"))
        kila i kwenye range(256):
            s = madstring("".join(map(chr, range(i))))
            t = s.rev()
            u = t.rev()
            self.assertEqual(u, s)
        s = madstring("12345")
        self.assertEqual(str(s), "12345")
        self.assertIs(str(s).__class__, str)

        base = "\x00" * 5
        s = madstring(base)
        self.assertEqual(s, base)
        self.assertEqual(str(s), base)
        self.assertIs(str(s).__class__, str)
        self.assertEqual(hash(s), hash(base))
        self.assertEqual({s: 1}[base], 1)
        self.assertEqual({base: 1}[s], 1)
        self.assertIs((s + "").__class__, str)
        self.assertEqual(s + "", base)
        self.assertIs(("" + s).__class__, str)
        self.assertEqual("" + s, base)
        self.assertIs((s * 0).__class__, str)
        self.assertEqual(s * 0, "")
        self.assertIs((s * 1).__class__, str)
        self.assertEqual(s * 1, base)
        self.assertIs((s * 2).__class__, str)
        self.assertEqual(s * 2, base + base)
        self.assertIs(s[:].__class__, str)
        self.assertEqual(s[:], base)
        self.assertIs(s[0:0].__class__, str)
        self.assertEqual(s[0:0], "")
        self.assertIs(s.strip().__class__, str)
        self.assertEqual(s.strip(), base)
        self.assertIs(s.lstrip().__class__, str)
        self.assertEqual(s.lstrip(), base)
        self.assertIs(s.rstrip().__class__, str)
        self.assertEqual(s.rstrip(), base)
        identitytab = {}
        self.assertIs(s.translate(identitytab).__class__, str)
        self.assertEqual(s.translate(identitytab), base)
        self.assertIs(s.replace("x", "x").__class__, str)
        self.assertEqual(s.replace("x", "x"), base)
        self.assertIs(s.ljust(len(s)).__class__, str)
        self.assertEqual(s.ljust(len(s)), base)
        self.assertIs(s.rjust(len(s)).__class__, str)
        self.assertEqual(s.rjust(len(s)), base)
        self.assertIs(s.center(len(s)).__class__, str)
        self.assertEqual(s.center(len(s)), base)
        self.assertIs(s.lower().__class__, str)
        self.assertEqual(s.lower(), base)

        kundi madunicode(str):
            _rev = Tupu
            eleza rev(self):
                ikiwa self._rev ni sio Tupu:
                    rudisha self._rev
                L = list(self)
                L.reverse()
                self._rev = self.__class__("".join(L))
                rudisha self._rev
        u = madunicode("ABCDEF")
        self.assertEqual(u, "ABCDEF")
        self.assertEqual(u.rev(), madunicode("FEDCBA"))
        self.assertEqual(u.rev().rev(), madunicode("ABCDEF"))
        base = "12345"
        u = madunicode(base)
        self.assertEqual(str(u), base)
        self.assertIs(str(u).__class__, str)
        self.assertEqual(hash(u), hash(base))
        self.assertEqual({u: 1}[base], 1)
        self.assertEqual({base: 1}[u], 1)
        self.assertIs(u.strip().__class__, str)
        self.assertEqual(u.strip(), base)
        self.assertIs(u.lstrip().__class__, str)
        self.assertEqual(u.lstrip(), base)
        self.assertIs(u.rstrip().__class__, str)
        self.assertEqual(u.rstrip(), base)
        self.assertIs(u.replace("x", "x").__class__, str)
        self.assertEqual(u.replace("x", "x"), base)
        self.assertIs(u.replace("xy", "xy").__class__, str)
        self.assertEqual(u.replace("xy", "xy"), base)
        self.assertIs(u.center(len(u)).__class__, str)
        self.assertEqual(u.center(len(u)), base)
        self.assertIs(u.ljust(len(u)).__class__, str)
        self.assertEqual(u.ljust(len(u)), base)
        self.assertIs(u.rjust(len(u)).__class__, str)
        self.assertEqual(u.rjust(len(u)), base)
        self.assertIs(u.lower().__class__, str)
        self.assertEqual(u.lower(), base)
        self.assertIs(u.upper().__class__, str)
        self.assertEqual(u.upper(), base)
        self.assertIs(u.capitalize().__class__, str)
        self.assertEqual(u.capitalize(), base)
        self.assertIs(u.title().__class__, str)
        self.assertEqual(u.title(), base)
        self.assertIs((u + "").__class__, str)
        self.assertEqual(u + "", base)
        self.assertIs(("" + u).__class__, str)
        self.assertEqual("" + u, base)
        self.assertIs((u * 0).__class__, str)
        self.assertEqual(u * 0, "")
        self.assertIs((u * 1).__class__, str)
        self.assertEqual(u * 1, base)
        self.assertIs((u * 2).__class__, str)
        self.assertEqual(u * 2, base + base)
        self.assertIs(u[:].__class__, str)
        self.assertEqual(u[:], base)
        self.assertIs(u[0:0].__class__, str)
        self.assertEqual(u[0:0], "")

        kundi sublist(list):
            pass
        a = sublist(range(5))
        self.assertEqual(a, list(range(5)))
        a.append("hello")
        self.assertEqual(a, list(range(5)) + ["hello"])
        a[5] = 5
        self.assertEqual(a, list(range(6)))
        a.extend(range(6, 20))
        self.assertEqual(a, list(range(20)))
        a[-5:] = []
        self.assertEqual(a, list(range(15)))
        toa a[10:15]
        self.assertEqual(len(a), 10)
        self.assertEqual(a, list(range(10)))
        self.assertEqual(list(a), list(range(10)))
        self.assertEqual(a[0], 0)
        self.assertEqual(a[9], 9)
        self.assertEqual(a[-10], 0)
        self.assertEqual(a[-1], 9)
        self.assertEqual(a[:5], list(range(5)))

        ## kundi CountedInput(file):
        ##    """Counts lines read by self.readline().
        ##
        ##     self.lineno ni the 0-based ordinal of the last line read, up to
        ##     a maximum of one greater than the number of lines kwenye the file.
        ##
        ##     self.ateof ni true ikiwa na only ikiwa the final "" line has been read,
        ##     at which point self.lineno stops incrementing, na further calls
        ##     to readline() endelea to rudisha "".
        ##     """
        ##
        ##     lineno = 0
        ##     ateof = 0
        ##     eleza readline(self):
        ##         ikiwa self.ateof:
        ##             rudisha ""
        ##         s = file.readline(self)
        ##         # Next line works too.
        ##         # s = super(CountedInput, self).readline()
        ##         self.lineno += 1
        ##         ikiwa s == "":
        ##             self.ateof = 1
        ##        rudisha s
        ##
        ## f = file(name=support.TESTFN, mode='w')
        ## lines = ['a\n', 'b\n', 'c\n']
        ## jaribu:
        ##     f.writelines(lines)
        ##     f.close()
        ##     f = CountedInput(support.TESTFN)
        ##     kila (i, expected) kwenye zip(range(1, 5) + [4], lines + 2 * [""]):
        ##         got = f.readline()
        ##         self.assertEqual(expected, got)
        ##         self.assertEqual(f.lineno, i)
        ##         self.assertEqual(f.ateof, (i > len(lines)))
        ##     f.close()
        ## mwishowe:
        ##     jaribu:
        ##         f.close()
        ##     tatizo:
        ##         pass
        ##     support.unlink(support.TESTFN)

    eleza test_keywords(self):
        # Testing keyword args to basic type constructors ...
        ukijumuisha self.assertRaisesRegex(TypeError, 'keyword argument'):
            int(x=1)
        ukijumuisha self.assertRaisesRegex(TypeError, 'keyword argument'):
            float(x=2)
        ukijumuisha self.assertRaisesRegex(TypeError, 'keyword argument'):
            bool(x=2)
        self.assertEqual(complex(imag=42, real=666), complex(666, 42))
        self.assertEqual(str(object=500), '500')
        self.assertEqual(str(object=b'abc', errors='strict'), 'abc')
        ukijumuisha self.assertRaisesRegex(TypeError, 'keyword argument'):
            tuple(sequence=range(3))
        ukijumuisha self.assertRaisesRegex(TypeError, 'keyword argument'):
            list(sequence=(0, 1, 2))
        # note: as of Python 2.3, dict() no longer has an "items" keyword arg

        kila constructor kwenye (int, float, int, complex, str, str,
                            tuple, list):
            jaribu:
                constructor(bogus_keyword_arg=1)
            except TypeError:
                pass
            isipokua:
                self.fail("expected TypeError kutoka bogus keyword argument to %r"
                            % constructor)

    eleza test_str_subclass_as_dict_key(self):
        # Testing a str subkundi used as dict key ..

        kundi cistr(str):
            """Subkundi of str that computes __eq__ case-insensitively.

            Also computes a hash code of the string kwenye canonical form.
            """

            eleza __init__(self, value):
                self.canonical = value.lower()
                self.hashcode = hash(self.canonical)

            eleza __eq__(self, other):
                ikiwa sio isinstance(other, cistr):
                    other = cistr(other)
                rudisha self.canonical == other.canonical

            eleza __hash__(self):
                rudisha self.hashcode

        self.assertEqual(cistr('ABC'), 'abc')
        self.assertEqual('aBc', cistr('ABC'))
        self.assertEqual(str(cistr('ABC')), 'ABC')

        d = {cistr('one'): 1, cistr('two'): 2, cistr('tHree'): 3}
        self.assertEqual(d[cistr('one')], 1)
        self.assertEqual(d[cistr('tWo')], 2)
        self.assertEqual(d[cistr('THrEE')], 3)
        self.assertIn(cistr('ONe'), d)
        self.assertEqual(d.get(cistr('thrEE')), 3)

    eleza test_classic_comparisons(self):
        # Testing classic comparisons...
        kundi classic:
            pass

        kila base kwenye (classic, int, object):
            kundi C(base):
                eleza __init__(self, value):
                    self.value = int(value)
                eleza __eq__(self, other):
                    ikiwa isinstance(other, C):
                        rudisha self.value == other.value
                    ikiwa isinstance(other, int) ama isinstance(other, int):
                        rudisha self.value == other
                    rudisha NotImplemented
                eleza __ne__(self, other):
                    ikiwa isinstance(other, C):
                        rudisha self.value != other.value
                    ikiwa isinstance(other, int) ama isinstance(other, int):
                        rudisha self.value != other
                    rudisha NotImplemented
                eleza __lt__(self, other):
                    ikiwa isinstance(other, C):
                        rudisha self.value < other.value
                    ikiwa isinstance(other, int) ama isinstance(other, int):
                        rudisha self.value < other
                    rudisha NotImplemented
                eleza __le__(self, other):
                    ikiwa isinstance(other, C):
                        rudisha self.value <= other.value
                    ikiwa isinstance(other, int) ama isinstance(other, int):
                        rudisha self.value <= other
                    rudisha NotImplemented
                eleza __gt__(self, other):
                    ikiwa isinstance(other, C):
                        rudisha self.value > other.value
                    ikiwa isinstance(other, int) ama isinstance(other, int):
                        rudisha self.value > other
                    rudisha NotImplemented
                eleza __ge__(self, other):
                    ikiwa isinstance(other, C):
                        rudisha self.value >= other.value
                    ikiwa isinstance(other, int) ama isinstance(other, int):
                        rudisha self.value >= other
                    rudisha NotImplemented

            c1 = C(1)
            c2 = C(2)
            c3 = C(3)
            self.assertEqual(c1, 1)
            c = {1: c1, 2: c2, 3: c3}
            kila x kwenye 1, 2, 3:
                kila y kwenye 1, 2, 3:
                    kila op kwenye "<", "<=", "==", "!=", ">", ">=":
                        self.assertEqual(eval("c[x] %s c[y]" % op),
                                     eval("x %s y" % op),
                                     "x=%d, y=%d" % (x, y))
                        self.assertEqual(eval("c[x] %s y" % op),
                                     eval("x %s y" % op),
                                     "x=%d, y=%d" % (x, y))
                        self.assertEqual(eval("x %s c[y]" % op),
                                     eval("x %s y" % op),
                                     "x=%d, y=%d" % (x, y))

    eleza test_rich_comparisons(self):
        # Testing rich comparisons...
        kundi Z(complex):
            pass
        z = Z(1)
        self.assertEqual(z, 1+0j)
        self.assertEqual(1+0j, z)
        kundi ZZ(complex):
            eleza __eq__(self, other):
                jaribu:
                    rudisha abs(self - other) <= 1e-6
                tatizo:
                    rudisha NotImplemented
        zz = ZZ(1.0000003)
        self.assertEqual(zz, 1+0j)
        self.assertEqual(1+0j, zz)

        kundi classic:
            pass
        kila base kwenye (classic, int, object, list):
            kundi C(base):
                eleza __init__(self, value):
                    self.value = int(value)
                eleza __cmp__(self_, other):
                    self.fail("shouldn't call __cmp__")
                eleza __eq__(self, other):
                    ikiwa isinstance(other, C):
                        rudisha self.value == other.value
                    ikiwa isinstance(other, int) ama isinstance(other, int):
                        rudisha self.value == other
                    rudisha NotImplemented
                eleza __ne__(self, other):
                    ikiwa isinstance(other, C):
                        rudisha self.value != other.value
                    ikiwa isinstance(other, int) ama isinstance(other, int):
                        rudisha self.value != other
                    rudisha NotImplemented
                eleza __lt__(self, other):
                    ikiwa isinstance(other, C):
                        rudisha self.value < other.value
                    ikiwa isinstance(other, int) ama isinstance(other, int):
                        rudisha self.value < other
                    rudisha NotImplemented
                eleza __le__(self, other):
                    ikiwa isinstance(other, C):
                        rudisha self.value <= other.value
                    ikiwa isinstance(other, int) ama isinstance(other, int):
                        rudisha self.value <= other
                    rudisha NotImplemented
                eleza __gt__(self, other):
                    ikiwa isinstance(other, C):
                        rudisha self.value > other.value
                    ikiwa isinstance(other, int) ama isinstance(other, int):
                        rudisha self.value > other
                    rudisha NotImplemented
                eleza __ge__(self, other):
                    ikiwa isinstance(other, C):
                        rudisha self.value >= other.value
                    ikiwa isinstance(other, int) ama isinstance(other, int):
                        rudisha self.value >= other
                    rudisha NotImplemented
            c1 = C(1)
            c2 = C(2)
            c3 = C(3)
            self.assertEqual(c1, 1)
            c = {1: c1, 2: c2, 3: c3}
            kila x kwenye 1, 2, 3:
                kila y kwenye 1, 2, 3:
                    kila op kwenye "<", "<=", "==", "!=", ">", ">=":
                        self.assertEqual(eval("c[x] %s c[y]" % op),
                                         eval("x %s y" % op),
                                         "x=%d, y=%d" % (x, y))
                        self.assertEqual(eval("c[x] %s y" % op),
                                         eval("x %s y" % op),
                                         "x=%d, y=%d" % (x, y))
                        self.assertEqual(eval("x %s c[y]" % op),
                                         eval("x %s y" % op),
                                         "x=%d, y=%d" % (x, y))

    eleza test_descrdoc(self):
        # Testing descriptor doc strings...
        kutoka _io agiza FileIO
        eleza check(descr, what):
            self.assertEqual(descr.__doc__, what)
        check(FileIO.closed, "Kweli ikiwa the file ni closed") # getset descriptor
        check(complex.real, "the real part of a complex number") # member descriptor

    eleza test_doc_descriptor(self):
        # Testing __doc__ descriptor...
        # SF bug 542984
        kundi DocDescr(object):
            eleza __get__(self, object, otype):
                ikiwa object:
                    object = object.__class__.__name__ + ' instance'
                ikiwa otype:
                    otype = otype.__name__
                rudisha 'object=%s; type=%s' % (object, otype)
        kundi OldClass:
            __doc__ = DocDescr()
        kundi NewClass(object):
            __doc__ = DocDescr()
        self.assertEqual(OldClass.__doc__, 'object=Tupu; type=OldClass')
        self.assertEqual(OldClass().__doc__, 'object=OldClass instance; type=OldClass')
        self.assertEqual(NewClass.__doc__, 'object=Tupu; type=NewClass')
        self.assertEqual(NewClass().__doc__, 'object=NewClass instance; type=NewClass')

    eleza test_set_class(self):
        # Testing __class__ assignment...
        kundi C(object): pass
        kundi D(object): pass
        kundi E(object): pass
        kundi F(D, E): pass
        kila cls kwenye C, D, E, F:
            kila cls2 kwenye C, D, E, F:
                x = cls()
                x.__class__ = cls2
                self.assertIs(x.__class__, cls2)
                x.__class__ = cls
                self.assertIs(x.__class__, cls)
        eleza cant(x, C):
            jaribu:
                x.__class__ = C
            except TypeError:
                pass
            isipokua:
                self.fail("shouldn't allow %r.__class__ = %r" % (x, C))
            jaribu:
                delattr(x, "__class__")
            except (TypeError, AttributeError):
                pass
            isipokua:
                self.fail("shouldn't allow toa %r.__class__" % x)
        cant(C(), list)
        cant(list(), C)
        cant(C(), 1)
        cant(C(), object)
        cant(object(), list)
        cant(list(), object)
        kundi Int(int): __slots__ = []
        cant(Kweli, int)
        cant(2, bool)
        o = object()
        cant(o, type(1))
        cant(o, type(Tupu))
        toa o
        kundi G(object):
            __slots__ = ["a", "b"]
        kundi H(object):
            __slots__ = ["b", "a"]
        kundi I(object):
            __slots__ = ["a", "b"]
        kundi J(object):
            __slots__ = ["c", "b"]
        kundi K(object):
            __slots__ = ["a", "b", "d"]
        kundi L(H):
            __slots__ = ["e"]
        kundi M(I):
            __slots__ = ["e"]
        kundi N(J):
            __slots__ = ["__weakref__"]
        kundi P(J):
            __slots__ = ["__dict__"]
        kundi Q(J):
            pass
        kundi R(J):
            __slots__ = ["__dict__", "__weakref__"]

        kila cls, cls2 kwenye ((G, H), (G, I), (I, H), (Q, R), (R, Q)):
            x = cls()
            x.a = 1
            x.__class__ = cls2
            self.assertIs(x.__class__, cls2,
                   "assigning %r as __class__ kila %r silently failed" % (cls2, x))
            self.assertEqual(x.a, 1)
            x.__class__ = cls
            self.assertIs(x.__class__, cls,
                   "assigning %r as __class__ kila %r silently failed" % (cls, x))
            self.assertEqual(x.a, 1)
        kila cls kwenye G, J, K, L, M, N, P, R, list, Int:
            kila cls2 kwenye G, J, K, L, M, N, P, R, list, Int:
                ikiwa cls ni cls2:
                    endelea
                cant(cls(), cls2)

        # Issue5283: when __class__ changes kwenye __del__, the wrong
        # type gets DECREF'd.
        kundi O(object):
            pass
        kundi A(object):
            eleza __del__(self):
                self.__class__ = O
        l = [A() kila x kwenye range(100)]
        toa l

    eleza test_set_dict(self):
        # Testing __dict__ assignment...
        kundi C(object): pass
        a = C()
        a.__dict__ = {'b': 1}
        self.assertEqual(a.b, 1)
        eleza cant(x, dict):
            jaribu:
                x.__dict__ = dict
            except (AttributeError, TypeError):
                pass
            isipokua:
                self.fail("shouldn't allow %r.__dict__ = %r" % (x, dict))
        cant(a, Tupu)
        cant(a, [])
        cant(a, 1)
        toa a.__dict__ # Deleting __dict__ ni allowed

        kundi Base(object):
            pass
        eleza verify_dict_readonly(x):
            """
            x has to be an instance of a kundi inheriting kutoka Base.
            """
            cant(x, {})
            jaribu:
                toa x.__dict__
            except (AttributeError, TypeError):
                pass
            isipokua:
                self.fail("shouldn't allow toa %r.__dict__" % x)
            dict_descr = Base.__dict__["__dict__"]
            jaribu:
                dict_descr.__set__(x, {})
            except (AttributeError, TypeError):
                pass
            isipokua:
                self.fail("dict_descr allowed access to %r's dict" % x)

        # Classes don't allow __dict__ assignment na have readonly dicts
        kundi Meta1(type, Base):
            pass
        kundi Meta2(Base, type):
            pass
        kundi D(object, metaclass=Meta1):
            pass
        kundi E(object, metaclass=Meta2):
            pass
        kila cls kwenye C, D, E:
            verify_dict_readonly(cls)
            class_dict = cls.__dict__
            jaribu:
                class_dict["spam"] = "eggs"
            except TypeError:
                pass
            isipokua:
                self.fail("%r's __dict__ can be modified" % cls)

        # Modules also disallow __dict__ assignment
        kundi Module1(types.ModuleType, Base):
            pass
        kundi Module2(Base, types.ModuleType):
            pass
        kila ModuleType kwenye Module1, Module2:
            mod = ModuleType("spam")
            verify_dict_readonly(mod)
            mod.__dict__["spam"] = "eggs"

        # Exception's __dict__ can be replaced, but sio deleted
        # (at least sio any more than regular exception's __dict__ can
        # be deleted; on CPython it ni sio the case, whereas on PyPy they
        # can, just like any other new-style instance's __dict__.)
        eleza can_delete_dict(e):
            jaribu:
                toa e.__dict__
            except (TypeError, AttributeError):
                rudisha Uongo
            isipokua:
                rudisha Kweli
        kundi Exception1(Exception, Base):
            pass
        kundi Exception2(Base, Exception):
            pass
        kila ExceptionType kwenye Exception, Exception1, Exception2:
            e = ExceptionType()
            e.__dict__ = {"a": 1}
            self.assertEqual(e.a, 1)
            self.assertEqual(can_delete_dict(e), can_delete_dict(ValueError()))

    eleza test_binary_operator_override(self):
        # Testing overrides of binary operations...
        kundi I(int):
            eleza __repr__(self):
                rudisha "I(%r)" % int(self)
            eleza __add__(self, other):
                rudisha I(int(self) + int(other))
            __radd__ = __add__
            eleza __pow__(self, other, mod=Tupu):
                ikiwa mod ni Tupu:
                    rudisha I(pow(int(self), int(other)))
                isipokua:
                    rudisha I(pow(int(self), int(other), int(mod)))
            eleza __rpow__(self, other, mod=Tupu):
                ikiwa mod ni Tupu:
                    rudisha I(pow(int(other), int(self), mod))
                isipokua:
                    rudisha I(pow(int(other), int(self), int(mod)))

        self.assertEqual(repr(I(1) + I(2)), "I(3)")
        self.assertEqual(repr(I(1) + 2), "I(3)")
        self.assertEqual(repr(1 + I(2)), "I(3)")
        self.assertEqual(repr(I(2) ** I(3)), "I(8)")
        self.assertEqual(repr(2 ** I(3)), "I(8)")
        self.assertEqual(repr(I(2) ** 3), "I(8)")
        self.assertEqual(repr(pow(I(2), I(3), I(5))), "I(3)")
        kundi S(str):
            eleza __eq__(self, other):
                rudisha self.lower() == other.lower()

    eleza test_subclass_propagation(self):
        # Testing propagation of slot functions to subclasses...
        kundi A(object):
            pass
        kundi B(A):
            pass
        kundi C(A):
            pass
        kundi D(B, C):
            pass
        d = D()
        orig_hash = hash(d) # related to id(d) kwenye platform-dependent ways
        A.__hash__ = lambda self: 42
        self.assertEqual(hash(d), 42)
        C.__hash__ = lambda self: 314
        self.assertEqual(hash(d), 314)
        B.__hash__ = lambda self: 144
        self.assertEqual(hash(d), 144)
        D.__hash__ = lambda self: 100
        self.assertEqual(hash(d), 100)
        D.__hash__ = Tupu
        self.assertRaises(TypeError, hash, d)
        toa D.__hash__
        self.assertEqual(hash(d), 144)
        B.__hash__ = Tupu
        self.assertRaises(TypeError, hash, d)
        toa B.__hash__
        self.assertEqual(hash(d), 314)
        C.__hash__ = Tupu
        self.assertRaises(TypeError, hash, d)
        toa C.__hash__
        self.assertEqual(hash(d), 42)
        A.__hash__ = Tupu
        self.assertRaises(TypeError, hash, d)
        toa A.__hash__
        self.assertEqual(hash(d), orig_hash)
        d.foo = 42
        d.bar = 42
        self.assertEqual(d.foo, 42)
        self.assertEqual(d.bar, 42)
        eleza __getattribute__(self, name):
            ikiwa name == "foo":
                rudisha 24
            rudisha object.__getattribute__(self, name)
        A.__getattribute__ = __getattribute__
        self.assertEqual(d.foo, 24)
        self.assertEqual(d.bar, 42)
        eleza __getattr__(self, name):
            ikiwa name kwenye ("spam", "foo", "bar"):
                rudisha "hello"
             ashiria AttributeError(name)
        B.__getattr__ = __getattr__
        self.assertEqual(d.spam, "hello")
        self.assertEqual(d.foo, 24)
        self.assertEqual(d.bar, 42)
        toa A.__getattribute__
        self.assertEqual(d.foo, 42)
        toa d.foo
        self.assertEqual(d.foo, "hello")
        self.assertEqual(d.bar, 42)
        toa B.__getattr__
        jaribu:
            d.foo
        except AttributeError:
            pass
        isipokua:
            self.fail("d.foo should be undefined now")

        # Test a nasty bug kwenye recurse_down_subclasses()
        kundi A(object):
            pass
        kundi B(A):
            pass
        toa B
        support.gc_collect()
        A.__setitem__ = lambda *a: Tupu # crash

    eleza test_buffer_inheritance(self):
        # Testing that buffer interface ni inherited ...

        agiza binascii
        # SF bug [#470040] ParseTuple t# vs subclasses.

        kundi MyBytes(bytes):
            pass
        base = b'abc'
        m = MyBytes(base)
        # b2a_hex uses the buffer interface to get its argument's value, via
        # PyArg_ParseTuple 't#' code.
        self.assertEqual(binascii.b2a_hex(m), binascii.b2a_hex(base))

        kundi MyInt(int):
            pass
        m = MyInt(42)
        jaribu:
            binascii.b2a_hex(m)
            self.fail('subkundi of int should sio have a buffer interface')
        except TypeError:
            pass

    eleza test_str_of_str_subclass(self):
        # Testing __str__ defined kwenye subkundi of str ...
        agiza binascii
        agiza io

        kundi octetstring(str):
            eleza __str__(self):
                rudisha binascii.b2a_hex(self.encode('ascii')).decode("ascii")
            eleza __repr__(self):
                rudisha self + " repr"

        o = octetstring('A')
        self.assertEqual(type(o), octetstring)
        self.assertEqual(type(str(o)), str)
        self.assertEqual(type(repr(o)), str)
        self.assertEqual(ord(o), 0x41)
        self.assertEqual(str(o), '41')
        self.assertEqual(repr(o), 'A repr')
        self.assertEqual(o.__str__(), '41')
        self.assertEqual(o.__repr__(), 'A repr')

        capture = io.StringIO()
        # Calling str() ama sio exercises different internal paths.
        andika(o, file=capture)
        andika(str(o), file=capture)
        self.assertEqual(capture.getvalue(), '41\n41\n')
        capture.close()

    eleza test_keyword_arguments(self):
        # Testing keyword arguments to __init__, __call__...
        eleza f(a): rudisha a
        self.assertEqual(f.__call__(a=42), 42)
        ba = bytearray()
        bytearray.__init__(ba, 'abc\xbd\u20ac',
                           encoding='latin1', errors='replace')
        self.assertEqual(ba, b'abc\xbd?')

    eleza test_recursive_call(self):
        # Testing recursive __call__() by setting to instance of class...
        kundi A(object):
            pass

        A.__call__ = A()
        jaribu:
            A()()
        except RecursionError:
            pass
        isipokua:
            self.fail("Recursion limit should have been reached kila __call__()")

    eleza test_delete_hook(self):
        # Testing __del__ hook...
        log = []
        kundi C(object):
            eleza __del__(self):
                log.append(1)
        c = C()
        self.assertEqual(log, [])
        toa c
        support.gc_collect()
        self.assertEqual(log, [1])

        kundi D(object): pass
        d = D()
        jaribu: toa d[0]
        except TypeError: pass
        isipokua: self.fail("invalid del() didn't  ashiria TypeError")

    eleza test_hash_inheritance(self):
        # Testing hash of mutable subclasses...

        kundi mydict(dict):
            pass
        d = mydict()
        jaribu:
            hash(d)
        except TypeError:
            pass
        isipokua:
            self.fail("hash() of dict subkundi should fail")

        kundi mylist(list):
            pass
        d = mylist()
        jaribu:
            hash(d)
        except TypeError:
            pass
        isipokua:
            self.fail("hash() of list subkundi should fail")

    eleza test_str_operations(self):
        jaribu: 'a' + 5
        except TypeError: pass
        isipokua: self.fail("'' + 5 doesn't  ashiria TypeError")

        jaribu: ''.split('')
        except ValueError: pass
        isipokua: self.fail("''.split('') doesn't  ashiria ValueError")

        jaribu: ''.join([0])
        except TypeError: pass
        isipokua: self.fail("''.join([0]) doesn't  ashiria TypeError")

        jaribu: ''.rindex('5')
        except ValueError: pass
        isipokua: self.fail("''.rindex('5') doesn't  ashiria ValueError")

        jaribu: '%(n)s' % Tupu
        except TypeError: pass
        isipokua: self.fail("'%(n)s' % Tupu doesn't  ashiria TypeError")

        jaribu: '%(n' % {}
        except ValueError: pass
        isipokua: self.fail("'%(n' % {} '' doesn't  ashiria ValueError")

        jaribu: '%*s' % ('abc')
        except TypeError: pass
        isipokua: self.fail("'%*s' % ('abc') doesn't  ashiria TypeError")

        jaribu: '%*.*s' % ('abc', 5)
        except TypeError: pass
        isipokua: self.fail("'%*.*s' % ('abc', 5) doesn't  ashiria TypeError")

        jaribu: '%s' % (1, 2)
        except TypeError: pass
        isipokua: self.fail("'%s' % (1, 2) doesn't  ashiria TypeError")

        jaribu: '%' % Tupu
        except ValueError: pass
        isipokua: self.fail("'%' % Tupu doesn't  ashiria ValueError")

        self.assertEqual('534253'.isdigit(), 1)
        self.assertEqual('534253x'.isdigit(), 0)
        self.assertEqual('%c' % 5, '\x05')
        self.assertEqual('%c' % '5', '5')

    eleza test_deepcopy_recursive(self):
        # Testing deepcopy of recursive objects...
        kundi Node:
            pass
        a = Node()
        b = Node()
        a.b = b
        b.a = a
        z = deepcopy(a) # This blew up before

    eleza test_uninitialized_modules(self):
        # Testing uninitialized module objects...
        kutoka types agiza ModuleType as M
        m = M.__new__(M)
        str(m)
        self.assertNotHasAttr(m, "__name__")
        self.assertNotHasAttr(m, "__file__")
        self.assertNotHasAttr(m, "foo")
        self.assertUongo(m.__dict__)   # Tupu ama {} are both reasonable answers
        m.foo = 1
        self.assertEqual(m.__dict__, {"foo": 1})

    eleza test_funny_new(self):
        # Testing __new__ returning something unexpected...
        kundi C(object):
            eleza __new__(cls, arg):
                ikiwa isinstance(arg, str): rudisha [1, 2, 3]
                elikiwa isinstance(arg, int): rudisha object.__new__(D)
                isipokua: rudisha object.__new__(cls)
        kundi D(C):
            eleza __init__(self, arg):
                self.foo = arg
        self.assertEqual(C("1"), [1, 2, 3])
        self.assertEqual(D("1"), [1, 2, 3])
        d = D(Tupu)
        self.assertEqual(d.foo, Tupu)
        d = C(1)
        self.assertIsInstance(d, D)
        self.assertEqual(d.foo, 1)
        d = D(1)
        self.assertIsInstance(d, D)
        self.assertEqual(d.foo, 1)

        kundi C(object):
            @staticmethod
            eleza __new__(*args):
                rudisha args
        self.assertEqual(C(1, 2), (C, 1, 2))
        kundi D(C):
            pass
        self.assertEqual(D(1, 2), (D, 1, 2))

        kundi C(object):
            @classmethod
            eleza __new__(*args):
                rudisha args
        self.assertEqual(C(1, 2), (C, C, 1, 2))
        kundi D(C):
            pass
        self.assertEqual(D(1, 2), (D, D, 1, 2))

    eleza test_imul_bug(self):
        # Testing kila __imul__ problems...
        # SF bug 544647
        kundi C(object):
            eleza __imul__(self, other):
                rudisha (self, other)
        x = C()
        y = x
        y *= 1.0
        self.assertEqual(y, (x, 1.0))
        y = x
        y *= 2
        self.assertEqual(y, (x, 2))
        y = x
        y *= 3
        self.assertEqual(y, (x, 3))
        y = x
        y *= 1<<100
        self.assertEqual(y, (x, 1<<100))
        y = x
        y *= Tupu
        self.assertEqual(y, (x, Tupu))
        y = x
        y *= "foo"
        self.assertEqual(y, (x, "foo"))

    eleza test_copy_setstate(self):
        # Testing that copy.*copy() correctly uses __setstate__...
        agiza copy
        kundi C(object):
            eleza __init__(self, foo=Tupu):
                self.foo = foo
                self.__foo = foo
            eleza setfoo(self, foo=Tupu):
                self.foo = foo
            eleza getfoo(self):
                rudisha self.__foo
            eleza __getstate__(self):
                rudisha [self.foo]
            eleza __setstate__(self_, lst):
                self.assertEqual(len(lst), 1)
                self_.__foo = self_.foo = lst[0]
        a = C(42)
        a.setfoo(24)
        self.assertEqual(a.foo, 24)
        self.assertEqual(a.getfoo(), 42)
        b = copy.copy(a)
        self.assertEqual(b.foo, 24)
        self.assertEqual(b.getfoo(), 24)
        b = copy.deepcopy(a)
        self.assertEqual(b.foo, 24)
        self.assertEqual(b.getfoo(), 24)

    eleza test_slices(self):
        # Testing cases ukijumuisha slices na overridden __getitem__ ...

        # Strings
        self.assertEqual("hello"[:4], "hell")
        self.assertEqual("hello"[slice(4)], "hell")
        self.assertEqual(str.__getitem__("hello", slice(4)), "hell")
        kundi S(str):
            eleza __getitem__(self, x):
                rudisha str.__getitem__(self, x)
        self.assertEqual(S("hello")[:4], "hell")
        self.assertEqual(S("hello")[slice(4)], "hell")
        self.assertEqual(S("hello").__getitem__(slice(4)), "hell")
        # Tuples
        self.assertEqual((1,2,3)[:2], (1,2))
        self.assertEqual((1,2,3)[slice(2)], (1,2))
        self.assertEqual(tuple.__getitem__((1,2,3), slice(2)), (1,2))
        kundi T(tuple):
            eleza __getitem__(self, x):
                rudisha tuple.__getitem__(self, x)
        self.assertEqual(T((1,2,3))[:2], (1,2))
        self.assertEqual(T((1,2,3))[slice(2)], (1,2))
        self.assertEqual(T((1,2,3)).__getitem__(slice(2)), (1,2))
        # Lists
        self.assertEqual([1,2,3][:2], [1,2])
        self.assertEqual([1,2,3][slice(2)], [1,2])
        self.assertEqual(list.__getitem__([1,2,3], slice(2)), [1,2])
        kundi L(list):
            eleza __getitem__(self, x):
                rudisha list.__getitem__(self, x)
        self.assertEqual(L([1,2,3])[:2], [1,2])
        self.assertEqual(L([1,2,3])[slice(2)], [1,2])
        self.assertEqual(L([1,2,3]).__getitem__(slice(2)), [1,2])
        # Now do lists na __setitem__
        a = L([1,2,3])
        a[slice(1, 3)] = [3,2]
        self.assertEqual(a, [1,3,2])
        a[slice(0, 2, 1)] = [3,1]
        self.assertEqual(a, [3,1,2])
        a.__setitem__(slice(1, 3), [2,1])
        self.assertEqual(a, [3,2,1])
        a.__setitem__(slice(0, 2, 1), [2,3])
        self.assertEqual(a, [2,3,1])

    eleza test_subtype_resurrection(self):
        # Testing resurrection of new-style instance...

        kundi C(object):
            container = []

            eleza __del__(self):
                # resurrect the instance
                C.container.append(self)

        c = C()
        c.attr = 42

        # The most interesting thing here ni whether this blows up, due to
        # flawed GC tracking logic kwenye typeobject.c's call_finalizer() (a 2.2.1
        # bug).
        toa c

        support.gc_collect()
        self.assertEqual(len(C.container), 1)

        # Make c mortal again, so that the test framework ukijumuisha -l doesn't report
        # it as a leak.
        toa C.__del__

    eleza test_slots_trash(self):
        # Testing slot trash...
        # Deallocating deeply nested slotted trash caused stack overflows
        kundi trash(object):
            __slots__ = ['x']
            eleza __init__(self, x):
                self.x = x
        o = Tupu
        kila i kwenye range(50000):
            o = trash(o)
        toa o

    eleza test_slots_multiple_inheritance(self):
        # SF bug 575229, multiple inheritance w/ slots dumps core
        kundi A(object):
            __slots__=()
        kundi B(object):
            pass
        kundi C(A,B) :
            __slots__=()
        ikiwa support.check_impl_detail():
            self.assertEqual(C.__basicsize__, B.__basicsize__)
        self.assertHasAttr(C, '__dict__')
        self.assertHasAttr(C, '__weakref__')
        C().x = 2

    eleza test_rmul(self):
        # Testing correct invocation of __rmul__...
        # SF patch 592646
        kundi C(object):
            eleza __mul__(self, other):
                rudisha "mul"
            eleza __rmul__(self, other):
                rudisha "rmul"
        a = C()
        self.assertEqual(a*2, "mul")
        self.assertEqual(a*2.2, "mul")
        self.assertEqual(2*a, "rmul")
        self.assertEqual(2.2*a, "rmul")

    eleza test_ipow(self):
        # Testing correct invocation of __ipow__...
        # [SF bug 620179]
        kundi C(object):
            eleza __ipow__(self, other):
                pass
        a = C()
        a **= 2

    eleza test_mutable_bases(self):
        # Testing mutable bases...

        # stuff that should work:
        kundi C(object):
            pass
        kundi C2(object):
            eleza __getattribute__(self, attr):
                ikiwa attr == 'a':
                    rudisha 2
                isipokua:
                    rudisha super(C2, self).__getattribute__(attr)
            eleza meth(self):
                rudisha 1
        kundi D(C):
            pass
        kundi E(D):
            pass
        d = D()
        e = E()
        D.__bases__ = (C,)
        D.__bases__ = (C2,)
        self.assertEqual(d.meth(), 1)
        self.assertEqual(e.meth(), 1)
        self.assertEqual(d.a, 2)
        self.assertEqual(e.a, 2)
        self.assertEqual(C2.__subclasses__(), [D])

        jaribu:
            toa D.__bases__
        except (TypeError, AttributeError):
            pass
        isipokua:
            self.fail("shouldn't be able to delete .__bases__")

        jaribu:
            D.__bases__ = ()
        except TypeError as msg:
            ikiwa str(msg) == "a new-style kundi can't have only classic bases":
                self.fail("wrong error message kila .__bases__ = ()")
        isipokua:
            self.fail("shouldn't be able to set .__bases__ to ()")

        jaribu:
            D.__bases__ = (D,)
        except TypeError:
            pass
        isipokua:
            # actually, we'll have crashed by here...
            self.fail("shouldn't be able to create inheritance cycles")

        jaribu:
            D.__bases__ = (C, C)
        except TypeError:
            pass
        isipokua:
            self.fail("didn't detect repeated base classes")

        jaribu:
            D.__bases__ = (E,)
        except TypeError:
            pass
        isipokua:
            self.fail("shouldn't be able to create inheritance cycles")

    eleza test_builtin_bases(self):
        # Make sure all the builtin types can have their base queried without
        # segfaulting. See issue #5787.
        builtin_types = [tp kila tp kwenye builtins.__dict__.values()
                         ikiwa isinstance(tp, type)]
        kila tp kwenye builtin_types:
            object.__getattribute__(tp, "__bases__")
            ikiwa tp ni sio object:
                self.assertEqual(len(tp.__bases__), 1, tp)

        kundi L(list):
            pass

        kundi C(object):
            pass

        kundi D(C):
            pass

        jaribu:
            L.__bases__ = (dict,)
        except TypeError:
            pass
        isipokua:
            self.fail("shouldn't turn list subkundi into dict subclass")

        jaribu:
            list.__bases__ = (dict,)
        except TypeError:
            pass
        isipokua:
            self.fail("shouldn't be able to assign to list.__bases__")

        jaribu:
            D.__bases__ = (C, list)
        except TypeError:
            pass
        isipokua:
            assert 0, "best_base calculation found wanting"

    eleza test_unsubclassable_types(self):
        ukijumuisha self.assertRaises(TypeError):
            kundi X(type(Tupu)):
                pass
        ukijumuisha self.assertRaises(TypeError):
            kundi X(object, type(Tupu)):
                pass
        ukijumuisha self.assertRaises(TypeError):
            kundi X(type(Tupu), object):
                pass
        kundi O(object):
            pass
        ukijumuisha self.assertRaises(TypeError):
            kundi X(O, type(Tupu)):
                pass
        ukijumuisha self.assertRaises(TypeError):
            kundi X(type(Tupu), O):
                pass

        kundi X(object):
            pass
        ukijumuisha self.assertRaises(TypeError):
            X.__bases__ = type(Tupu),
        ukijumuisha self.assertRaises(TypeError):
            X.__bases__ = object, type(Tupu)
        ukijumuisha self.assertRaises(TypeError):
            X.__bases__ = type(Tupu), object
        ukijumuisha self.assertRaises(TypeError):
            X.__bases__ = O, type(Tupu)
        ukijumuisha self.assertRaises(TypeError):
            X.__bases__ = type(Tupu), O

    eleza test_mutable_bases_with_failing_mro(self):
        # Testing mutable bases ukijumuisha failing mro...
        kundi WorkOnce(type):
            eleza __new__(self, name, bases, ns):
                self.flag = 0
                rudisha super(WorkOnce, self).__new__(WorkOnce, name, bases, ns)
            eleza mro(self):
                ikiwa self.flag > 0:
                     ashiria RuntimeError("bozo")
                isipokua:
                    self.flag += 1
                    rudisha type.mro(self)

        kundi WorkAlways(type):
            eleza mro(self):
                # this ni here to make sure that .mro()s aren't called
                # ukijumuisha an exception set (which was possible at one point).
                # An error message will be printed kwenye a debug build.
                # What's a good way to test kila this?
                rudisha type.mro(self)

        kundi C(object):
            pass

        kundi C2(object):
            pass

        kundi D(C):
            pass

        kundi E(D):
            pass

        kundi F(D, metaclass=WorkOnce):
            pass

        kundi G(D, metaclass=WorkAlways):
            pass

        # Immediate subclasses have their mro's adjusted kwenye alphabetical
        # order, so E's will get adjusted before adjusting F's fails.  We
        # check here that E's gets restored.

        E_mro_before = E.__mro__
        D_mro_before = D.__mro__

        jaribu:
            D.__bases__ = (C2,)
        except RuntimeError:
            self.assertEqual(E.__mro__, E_mro_before)
            self.assertEqual(D.__mro__, D_mro_before)
        isipokua:
            self.fail("exception sio propagated")

    eleza test_mutable_bases_catch_mro_conflict(self):
        # Testing mutable bases catch mro conflict...
        kundi A(object):
            pass

        kundi B(object):
            pass

        kundi C(A, B):
            pass

        kundi D(A, B):
            pass

        kundi E(C, D):
            pass

        jaribu:
            C.__bases__ = (B, A)
        except TypeError:
            pass
        isipokua:
            self.fail("didn't catch MRO conflict")

    eleza test_mutable_names(self):
        # Testing mutable names...
        kundi C(object):
            pass

        # C.__module__ could be 'test_descr' ama '__main__'
        mod = C.__module__

        C.__name__ = 'D'
        self.assertEqual((C.__module__, C.__name__), (mod, 'D'))

        C.__name__ = 'D.E'
        self.assertEqual((C.__module__, C.__name__), (mod, 'D.E'))

    eleza test_evil_type_name(self):
        # A badly placed Py_DECREF kwenye type_set_name led to arbitrary code
        # execution wakati the type structure was sio kwenye a sane state, na a
        # possible segmentation fault as a result.  See bug #16447.
        kundi Nasty(str):
            eleza __del__(self):
                C.__name__ = "other"

        kundi C:
            pass

        C.__name__ = Nasty("abc")
        C.__name__ = "normal"

    eleza test_subclass_right_op(self):
        # Testing correct dispatch of subkundi overloading __r<op>__...

        # This code tests various cases where right-dispatch of a subclass
        # should be preferred over left-dispatch of a base class.

        # Case 1: subkundi of int; this tests code kwenye abstract.c::binary_op1()

        kundi B(int):
            eleza __floordiv__(self, other):
                rudisha "B.__floordiv__"
            eleza __rfloordiv__(self, other):
                rudisha "B.__rfloordiv__"

        self.assertEqual(B(1) // 1, "B.__floordiv__")
        self.assertEqual(1 // B(1), "B.__rfloordiv__")

        # Case 2: subkundi of object; this ni just the baseline kila case 3

        kundi C(object):
            eleza __floordiv__(self, other):
                rudisha "C.__floordiv__"
            eleza __rfloordiv__(self, other):
                rudisha "C.__rfloordiv__"

        self.assertEqual(C() // 1, "C.__floordiv__")
        self.assertEqual(1 // C(), "C.__rfloordiv__")

        # Case 3: subkundi of new-style class; here it gets interesting

        kundi D(C):
            eleza __floordiv__(self, other):
                rudisha "D.__floordiv__"
            eleza __rfloordiv__(self, other):
                rudisha "D.__rfloordiv__"

        self.assertEqual(D() // C(), "D.__floordiv__")
        self.assertEqual(C() // D(), "D.__rfloordiv__")

        # Case 4: this didn't work right kwenye 2.2.2 na 2.3a1

        kundi E(C):
            pass

        self.assertEqual(E.__rfloordiv__, C.__rfloordiv__)

        self.assertEqual(E() // 1, "C.__floordiv__")
        self.assertEqual(1 // E(), "C.__rfloordiv__")
        self.assertEqual(E() // C(), "C.__floordiv__")
        self.assertEqual(C() // E(), "C.__floordiv__") # This one would fail

    @support.impl_detail("testing an internal kind of method object")
    eleza test_meth_class_get(self):
        # Testing __get__ method of METH_CLASS C methods...
        # Full coverage of descrobject.c::classmethod_get()

        # Baseline
        arg = [1, 2, 3]
        res = {1: Tupu, 2: Tupu, 3: Tupu}
        self.assertEqual(dict.fromkeys(arg), res)
        self.assertEqual({}.fromkeys(arg), res)

        # Now get the descriptor
        descr = dict.__dict__["fromkeys"]

        # More baseline using the descriptor directly
        self.assertEqual(descr.__get__(Tupu, dict)(arg), res)
        self.assertEqual(descr.__get__({})(arg), res)

        # Now check various error cases
        jaribu:
            descr.__get__(Tupu, Tupu)
        except TypeError:
            pass
        isipokua:
            self.fail("shouldn't have allowed descr.__get__(Tupu, Tupu)")
        jaribu:
            descr.__get__(42)
        except TypeError:
            pass
        isipokua:
            self.fail("shouldn't have allowed descr.__get__(42)")
        jaribu:
            descr.__get__(Tupu, 42)
        except TypeError:
            pass
        isipokua:
            self.fail("shouldn't have allowed descr.__get__(Tupu, 42)")
        jaribu:
            descr.__get__(Tupu, int)
        except TypeError:
            pass
        isipokua:
            self.fail("shouldn't have allowed descr.__get__(Tupu, int)")

    eleza test_isinst_isclass(self):
        # Testing proxy isinstance() na isclass()...
        kundi Proxy(object):
            eleza __init__(self, obj):
                self.__obj = obj
            eleza __getattribute__(self, name):
                ikiwa name.startswith("_Proxy__"):
                    rudisha object.__getattribute__(self, name)
                isipokua:
                    rudisha getattr(self.__obj, name)
        # Test ukijumuisha a classic class
        kundi C:
            pass
        a = C()
        pa = Proxy(a)
        self.assertIsInstance(a, C)  # Baseline
        self.assertIsInstance(pa, C) # Test
        # Test ukijumuisha a classic subclass
        kundi D(C):
            pass
        a = D()
        pa = Proxy(a)
        self.assertIsInstance(a, C)  # Baseline
        self.assertIsInstance(pa, C) # Test
        # Test ukijumuisha a new-style class
        kundi C(object):
            pass
        a = C()
        pa = Proxy(a)
        self.assertIsInstance(a, C)  # Baseline
        self.assertIsInstance(pa, C) # Test
        # Test ukijumuisha a new-style subclass
        kundi D(C):
            pass
        a = D()
        pa = Proxy(a)
        self.assertIsInstance(a, C)  # Baseline
        self.assertIsInstance(pa, C) # Test

    eleza test_proxy_super(self):
        # Testing super() kila a proxy object...
        kundi Proxy(object):
            eleza __init__(self, obj):
                self.__obj = obj
            eleza __getattribute__(self, name):
                ikiwa name.startswith("_Proxy__"):
                    rudisha object.__getattribute__(self, name)
                isipokua:
                    rudisha getattr(self.__obj, name)

        kundi B(object):
            eleza f(self):
                rudisha "B.f"

        kundi C(B):
            eleza f(self):
                rudisha super(C, self).f() + "->C.f"

        obj = C()
        p = Proxy(obj)
        self.assertEqual(C.__dict__["f"](p), "B.f->C.f")

    eleza test_carloverre(self):
        # Testing prohibition of Carlo Verre's hack...
        jaribu:
            object.__setattr__(str, "foo", 42)
        except TypeError:
            pass
        isipokua:
            self.fail("Carlo Verre __setattr__ succeeded!")
        jaribu:
            object.__delattr__(str, "lower")
        except TypeError:
            pass
        isipokua:
            self.fail("Carlo Verre __delattr__ succeeded!")

    eleza test_weakref_segfault(self):
        # Testing weakref segfault...
        # SF 742911
        agiza weakref

        kundi Provoker:
            eleza __init__(self, referrent):
                self.ref = weakref.ref(referrent)

            eleza __del__(self):
                x = self.ref()

        kundi Oops(object):
            pass

        o = Oops()
        o.whatever = Provoker(o)
        toa o

    eleza test_wrapper_segfault(self):
        # SF 927248: deeply nested wrappers could cause stack overflow
        f = lambda:Tupu
        kila i kwenye range(1000000):
            f = f.__call__
        f = Tupu

    eleza test_file_fault(self):
        # Testing sys.stdout ni changed kwenye getattr...
        test_stdout = sys.stdout
        kundi StdoutGuard:
            eleza __getattr__(self, attr):
                sys.stdout = sys.__stdout__
                 ashiria RuntimeError("Premature access to sys.stdout.%s" % attr)
        sys.stdout = StdoutGuard()
        jaribu:
            andika("Oops!")
        except RuntimeError:
            pass
        mwishowe:
            sys.stdout = test_stdout

    eleza test_vicious_descriptor_nonsense(self):
        # Testing vicious_descriptor_nonsense...

        # A potential segfault spotted by Thomas Wouters kwenye mail to
        # python-dev 2003-04-17, turned into an example & fixed by Michael
        # Hudson just less than four months later...

        kundi Evil(object):
            eleza __hash__(self):
                rudisha hash('attr')
            eleza __eq__(self, other):
                jaribu:
                    toa C.attr
                except AttributeError:
                    # possible race condition
                    pass
                rudisha 0

        kundi Descr(object):
            eleza __get__(self, ob, type=Tupu):
                rudisha 1

        kundi C(object):
            attr = Descr()

        c = C()
        c.__dict__[Evil()] = 0

        self.assertEqual(c.attr, 1)
        # this makes a crash more likely:
        support.gc_collect()
        self.assertNotHasAttr(c, 'attr')

    eleza test_init(self):
        # SF 1155938
        kundi Foo(object):
            eleza __init__(self):
                rudisha 10
        jaribu:
            Foo()
        except TypeError:
            pass
        isipokua:
            self.fail("did sio test __init__() kila Tupu return")

    eleza assertNotOrderable(self, a, b):
        ukijumuisha self.assertRaises(TypeError):
            a < b
        ukijumuisha self.assertRaises(TypeError):
            a > b
        ukijumuisha self.assertRaises(TypeError):
            a <= b
        ukijumuisha self.assertRaises(TypeError):
            a >= b

    eleza test_method_wrapper(self):
        # Testing method-wrapper objects...
        # <type 'method-wrapper'> did sio support any reflection before 2.5
        l = []
        self.assertKweli(l.__add__ == l.__add__)
        self.assertUongo(l.__add__ != l.__add__)
        self.assertUongo(l.__add__ == [].__add__)
        self.assertKweli(l.__add__ != [].__add__)
        self.assertUongo(l.__add__ == l.__mul__)
        self.assertKweli(l.__add__ != l.__mul__)
        self.assertNotOrderable(l.__add__, l.__add__)
        self.assertEqual(l.__add__.__name__, '__add__')
        self.assertIs(l.__add__.__self__, l)
        self.assertIs(l.__add__.__objclass__, list)
        self.assertEqual(l.__add__.__doc__, list.__add__.__doc__)
        # hash([].__add__) should sio be based on hash([])
        hash(l.__add__)

    eleza test_builtin_function_or_method(self):
        # Not really belonging to test_descr, but introspection and
        # comparison on <type 'builtin_function_or_method'> seems not
        # to be tested elsewhere
        l = []
        self.assertKweli(l.append == l.append)
        self.assertUongo(l.append != l.append)
        self.assertUongo(l.append == [].append)
        self.assertKweli(l.append != [].append)
        self.assertUongo(l.append == l.pop)
        self.assertKweli(l.append != l.pop)
        self.assertNotOrderable(l.append, l.append)
        self.assertEqual(l.append.__name__, 'append')
        self.assertIs(l.append.__self__, l)
        # self.assertIs(l.append.__objclass__, list) --- could be added?
        self.assertEqual(l.append.__doc__, list.append.__doc__)
        # hash([].append) should sio be based on hash([])
        hash(l.append)

    eleza test_special_unbound_method_types(self):
        # Testing objects of <type 'wrapper_descriptor'>...
        self.assertKweli(list.__add__ == list.__add__)
        self.assertUongo(list.__add__ != list.__add__)
        self.assertUongo(list.__add__ == list.__mul__)
        self.assertKweli(list.__add__ != list.__mul__)
        self.assertNotOrderable(list.__add__, list.__add__)
        self.assertEqual(list.__add__.__name__, '__add__')
        self.assertIs(list.__add__.__objclass__, list)

        # Testing objects of <type 'method_descriptor'>...
        self.assertKweli(list.append == list.append)
        self.assertUongo(list.append != list.append)
        self.assertUongo(list.append == list.pop)
        self.assertKweli(list.append != list.pop)
        self.assertNotOrderable(list.append, list.append)
        self.assertEqual(list.append.__name__, 'append')
        self.assertIs(list.append.__objclass__, list)

    eleza test_not_implemented(self):
        # Testing NotImplemented...
        # all binary methods should be able to rudisha a NotImplemented
        agiza operator

        eleza specialmethod(self, other):
            rudisha NotImplemented

        eleza check(expr, x, y):
            jaribu:
                exec(expr, {'x': x, 'y': y, 'operator': operator})
            except TypeError:
                pass
            isipokua:
                self.fail("no TypeError kutoka %r" % (expr,))

        N1 = sys.maxsize + 1    # might trigger OverflowErrors instead of
                                # TypeErrors
        N2 = sys.maxsize         # ikiwa sizeof(int) < sizeof(long), might trigger
                                #   ValueErrors instead of TypeErrors
        kila name, expr, iexpr kwenye [
                ('__add__',      'x + y',                   'x += y'),
                ('__sub__',      'x - y',                   'x -= y'),
                ('__mul__',      'x * y',                   'x *= y'),
                ('__matmul__',   'x @ y',                   'x @= y'),
                ('__truediv__',  'x / y',                   'x /= y'),
                ('__floordiv__', 'x // y',                  'x //= y'),
                ('__mod__',      'x % y',                   'x %= y'),
                ('__divmod__',   'divmod(x, y)',            Tupu),
                ('__pow__',      'x ** y',                  'x **= y'),
                ('__lshift__',   'x << y',                  'x <<= y'),
                ('__rshift__',   'x >> y',                  'x >>= y'),
                ('__and__',      'x & y',                   'x &= y'),
                ('__or__',       'x | y',                   'x |= y'),
                ('__xor__',      'x ^ y',                   'x ^= y')]:
            rname = '__r' + name[2:]
            A = type('A', (), {name: specialmethod})
            a = A()
            check(expr, a, a)
            check(expr, a, N1)
            check(expr, a, N2)
            ikiwa iexpr:
                check(iexpr, a, a)
                check(iexpr, a, N1)
                check(iexpr, a, N2)
                iname = '__i' + name[2:]
                C = type('C', (), {iname: specialmethod})
                c = C()
                check(iexpr, c, a)
                check(iexpr, c, N1)
                check(iexpr, c, N2)

    eleza test_assign_slice(self):
        # ceval.c's assign_slice used to check for
        # tp->tp_as_sequence->sq_slice instead of
        # tp->tp_as_sequence->sq_ass_slice

        kundi C(object):
            eleza __setitem__(self, idx, value):
                self.value = value

        c = C()
        c[1:2] = 3
        self.assertEqual(c.value, 3)

    eleza test_set_and_no_get(self):
        # See
        # http://mail.python.org/pipermail/python-dev/2010-January/095637.html
        kundi Descr(object):

            eleza __init__(self, name):
                self.name = name

            eleza __set__(self, obj, value):
                obj.__dict__[self.name] = value
        descr = Descr("a")

        kundi X(object):
            a = descr

        x = X()
        self.assertIs(x.a, descr)
        x.a = 42
        self.assertEqual(x.a, 42)

        # Also check type_getattro kila correctness.
        kundi Meta(type):
            pass
        kundi X(metaclass=Meta):
            pass
        X.a = 42
        Meta.a = Descr("a")
        self.assertEqual(X.a, 42)

    eleza test_getattr_hooks(self):
        # issue 4230

        kundi Descriptor(object):
            counter = 0
            eleza __get__(self, obj, objtype=Tupu):
                eleza getter(name):
                    self.counter += 1
                     ashiria AttributeError(name)
                rudisha getter

        descr = Descriptor()
        kundi A(object):
            __getattribute__ = descr
        kundi B(object):
            __getattr__ = descr
        kundi C(object):
            __getattribute__ = descr
            __getattr__ = descr

        self.assertRaises(AttributeError, getattr, A(), "attr")
        self.assertEqual(descr.counter, 1)
        self.assertRaises(AttributeError, getattr, B(), "attr")
        self.assertEqual(descr.counter, 2)
        self.assertRaises(AttributeError, getattr, C(), "attr")
        self.assertEqual(descr.counter, 4)

        kundi EvilGetattribute(object):
            # This used to segfault
            eleza __getattr__(self, name):
                 ashiria AttributeError(name)
            eleza __getattribute__(self, name):
                toa EvilGetattribute.__getattr__
                kila i kwenye range(5):
                    gc.collect()
                 ashiria AttributeError(name)

        self.assertRaises(AttributeError, getattr, EvilGetattribute(), "attr")

    eleza test_type___getattribute__(self):
        self.assertRaises(TypeError, type.__getattribute__, list, type)

    eleza test_abstractmethods(self):
        # type pretends sio to have __abstractmethods__.
        self.assertRaises(AttributeError, getattr, type, "__abstractmethods__")
        kundi meta(type):
            pass
        self.assertRaises(AttributeError, getattr, meta, "__abstractmethods__")
        kundi X(object):
            pass
        ukijumuisha self.assertRaises(AttributeError):
            toa X.__abstractmethods__

    eleza test_proxy_call(self):
        kundi FakeStr:
            __class__ = str

        fake_str = FakeStr()
        # isinstance() reads __class__
        self.assertIsInstance(fake_str, str)

        # call a method descriptor
        ukijumuisha self.assertRaises(TypeError):
            str.split(fake_str)

        # call a slot wrapper descriptor
        ukijumuisha self.assertRaises(TypeError):
            str.__add__(fake_str, "abc")

    eleza test_repr_as_str(self):
        # Issue #11603: crash ama infinite loop when rebinding __str__ as
        # __repr__.
        kundi Foo:
            pass
        Foo.__repr__ = Foo.__str__
        foo = Foo()
        self.assertRaises(RecursionError, str, foo)
        self.assertRaises(RecursionError, repr, foo)

    eleza test_mixing_slot_wrappers(self):
        kundi X(dict):
            __setattr__ = dict.__setitem__
            __neg__ = dict.copy
        x = X()
        x.y = 42
        self.assertEqual(x["y"], 42)
        self.assertEqual(x, -x)

    eleza test_wrong_class_slot_wrapper(self):
        # Check bpo-37619: a wrapper descriptor taken kutoka the wrong class
        # should  ashiria an exception instead of silently being ignored
        kundi A(int):
            __eq__ = str.__eq__
            __add__ = str.__add__
        a = A()
        ukijumuisha self.assertRaises(TypeError):
            a == a
        ukijumuisha self.assertRaises(TypeError):
            a + a

    eleza test_slot_shadows_class_variable(self):
        ukijumuisha self.assertRaises(ValueError) as cm:
            kundi X:
                __slots__ = ["foo"]
                foo = Tupu
        m = str(cm.exception)
        self.assertEqual("'foo' kwenye __slots__ conflicts ukijumuisha kundi variable", m)

    eleza test_set_doc(self):
        kundi X:
            "elephant"
        X.__doc__ = "banana"
        self.assertEqual(X.__doc__, "banana")
        ukijumuisha self.assertRaises(TypeError) as cm:
            type(list).__dict__["__doc__"].__set__(list, "blah")
        self.assertIn("can't set list.__doc__", str(cm.exception))
        ukijumuisha self.assertRaises(TypeError) as cm:
            type(X).__dict__["__doc__"].__delete__(X)
        self.assertIn("can't delete X.__doc__", str(cm.exception))
        self.assertEqual(X.__doc__, "banana")

    eleza test_qualname(self):
        descriptors = [str.lower, complex.real, float.real, int.__add__]
        types = ['method', 'member', 'getset', 'wrapper']

        # make sure we have an example of each type of descriptor
        kila d, n kwenye zip(descriptors, types):
            self.assertEqual(type(d).__name__, n + '_descriptor')

        kila d kwenye descriptors:
            qualname = d.__objclass__.__qualname__ + '.' + d.__name__
            self.assertEqual(d.__qualname__, qualname)

        self.assertEqual(str.lower.__qualname__, 'str.lower')
        self.assertEqual(complex.real.__qualname__, 'complex.real')
        self.assertEqual(float.real.__qualname__, 'float.real')
        self.assertEqual(int.__add__.__qualname__, 'int.__add__')

        kundi X:
            pass
        ukijumuisha self.assertRaises(TypeError):
            toa X.__qualname__

        self.assertRaises(TypeError, type.__dict__['__qualname__'].__set__,
                          str, 'Oink')

        global Y
        kundi Y:
            kundi Inside:
                pass
        self.assertEqual(Y.__qualname__, 'Y')
        self.assertEqual(Y.Inside.__qualname__, 'Y.Inside')

    eleza test_qualname_dict(self):
        ns = {'__qualname__': 'some.name'}
        tp = type('Foo', (), ns)
        self.assertEqual(tp.__qualname__, 'some.name')
        self.assertNotIn('__qualname__', tp.__dict__)
        self.assertEqual(ns, {'__qualname__': 'some.name'})

        ns = {'__qualname__': 1}
        self.assertRaises(TypeError, type, 'Foo', (), ns)

    eleza test_cycle_through_dict(self):
        # See bug #1469629
        kundi X(dict):
            eleza __init__(self):
                dict.__init__(self)
                self.__dict__ = self
        x = X()
        x.attr = 42
        wr = weakref.ref(x)
        toa x
        support.gc_collect()
        self.assertIsTupu(wr())
        kila o kwenye gc.get_objects():
            self.assertIsNot(type(o), X)

    eleza test_object_new_and_init_with_parameters(self):
        # See issue #1683368
        kundi OverrideNeither:
            pass
        self.assertRaises(TypeError, OverrideNeither, 1)
        self.assertRaises(TypeError, OverrideNeither, kw=1)
        kundi OverrideNew:
            eleza __new__(cls, foo, kw=0, *args, **kwds):
                rudisha object.__new__(cls, *args, **kwds)
        kundi OverrideInit:
            eleza __init__(self, foo, kw=0, *args, **kwargs):
                rudisha object.__init__(self, *args, **kwargs)
        kundi OverrideBoth(OverrideNew, OverrideInit):
            pass
        kila case kwenye OverrideNew, OverrideInit, OverrideBoth:
            case(1)
            case(1, kw=2)
            self.assertRaises(TypeError, case, 1, 2, 3)
            self.assertRaises(TypeError, case, 1, 2, foo=3)

    eleza test_subclassing_does_not_duplicate_dict_descriptors(self):
        kundi Base:
            pass
        kundi Sub(Base):
            pass
        self.assertIn("__dict__", Base.__dict__)
        self.assertNotIn("__dict__", Sub.__dict__)

    eleza test_bound_method_repr(self):
        kundi Foo:
            eleza method(self):
                pass
        self.assertRegex(repr(Foo().method),
            r"<bound method .*Foo\.method of <.*Foo object at .*>>")


        kundi Base:
            eleza method(self):
                pass
        kundi Derived1(Base):
            pass
        kundi Derived2(Base):
            eleza method(self):
                pass
        base = Base()
        derived1 = Derived1()
        derived2 = Derived2()
        super_d2 = super(Derived2, derived2)
        self.assertRegex(repr(base.method),
            r"<bound method .*Base\.method of <.*Base object at .*>>")
        self.assertRegex(repr(derived1.method),
            r"<bound method .*Base\.method of <.*Derived1 object at .*>>")
        self.assertRegex(repr(derived2.method),
            r"<bound method .*Derived2\.method of <.*Derived2 object at .*>>")
        self.assertRegex(repr(super_d2.method),
            r"<bound method .*Base\.method of <.*Derived2 object at .*>>")

        kundi Foo:
            @classmethod
            eleza method(cls):
                pass
        foo = Foo()
        self.assertRegex(repr(foo.method), # access via instance
            r"<bound method .*Foo\.method of <kundi '.*Foo'>>")
        self.assertRegex(repr(Foo.method), # access via the class
            r"<bound method .*Foo\.method of <kundi '.*Foo'>>")


        kundi MyCallable:
            eleza __call__(self, arg):
                pass
        func = MyCallable() # func has no __name__ ama __qualname__ attributes
        instance = object()
        method = types.MethodType(func, instance)
        self.assertRegex(repr(method),
            r"<bound method \? of <object object at .*>>")
        func.__name__ = "name"
        self.assertRegex(repr(method),
            r"<bound method name of <object object at .*>>")
        func.__qualname__ = "qualname"
        self.assertRegex(repr(method),
            r"<bound method qualname of <object object at .*>>")

    @unittest.skipIf(_testcapi ni Tupu, 'need the _testcapi module')
    eleza test_bpo25750(self):
        # bpo-25750: calling a descriptor (implemented as built-in
        # function ukijumuisha METH_FASTCALL) should sio crash CPython ikiwa the
        # descriptor deletes itself kutoka the class.
        kundi Descr:
            __get__ = _testcapi.bad_get

        kundi X:
            descr = Descr()
            eleza __new__(cls):
                cls.descr = Tupu
                # Create this large list to corrupt some unused memory
                cls.lst = [2**i kila i kwenye range(10000)]
        X.descr


kundi DictProxyTests(unittest.TestCase):
    eleza setUp(self):
        kundi C(object):
            eleza meth(self):
                pass
        self.C = C

    @unittest.skipIf(hasattr(sys, 'gettrace') na sys.gettrace(),
                        'trace function introduces __local__')
    eleza test_iter_keys(self):
        # Testing dict-proxy keys...
        it = self.C.__dict__.keys()
        self.assertNotIsInstance(it, list)
        keys = list(it)
        keys.sort()
        self.assertEqual(keys, ['__dict__', '__doc__', '__module__',
                                '__weakref__', 'meth'])

    @unittest.skipIf(hasattr(sys, 'gettrace') na sys.gettrace(),
                        'trace function introduces __local__')
    eleza test_iter_values(self):
        # Testing dict-proxy values...
        it = self.C.__dict__.values()
        self.assertNotIsInstance(it, list)
        values = list(it)
        self.assertEqual(len(values), 5)

    @unittest.skipIf(hasattr(sys, 'gettrace') na sys.gettrace(),
                        'trace function introduces __local__')
    eleza test_iter_items(self):
        # Testing dict-proxy iteritems...
        it = self.C.__dict__.items()
        self.assertNotIsInstance(it, list)
        keys = [item[0] kila item kwenye it]
        keys.sort()
        self.assertEqual(keys, ['__dict__', '__doc__', '__module__',
                                '__weakref__', 'meth'])

    eleza test_dict_type_with_metaclass(self):
        # Testing type of __dict__ when metakundi set...
        kundi B(object):
            pass
        kundi M(type):
            pass
        kundi C(metaclass=M):
            # In 2.3a1, C.__dict__ was a real dict rather than a dict proxy
            pass
        self.assertEqual(type(C.__dict__), type(B.__dict__))

    eleza test_repr(self):
        # Testing mappingproxy.__repr__.
        # We can't blindly compare ukijumuisha the repr of another dict as ordering
        # of keys na values ni arbitrary na may differ.
        r = repr(self.C.__dict__)
        self.assertKweli(r.startswith('mappingproxy('), r)
        self.assertKweli(r.endswith(')'), r)
        kila k, v kwenye self.C.__dict__.items():
            self.assertIn('{!r}: {!r}'.format(k, v), r)


kundi PTypesLongInitTest(unittest.TestCase):
    # This ni kwenye its own TestCase so that it can be run before any other tests.
    eleza test_pytype_long_ready(self):
        # Testing SF bug 551412 ...

        # This dumps core when SF bug 551412 isn't fixed --
        # but only when test_descr.py ni run separately.
        # (That can't be helped -- as soon as PyType_Ready()
        # ni called kila PyLong_Type, the bug ni gone.)
        kundi UserLong(object):
            eleza __pow__(self, *args):
                pass
        jaribu:
            pow(0, UserLong(), 0)
        tatizo:
            pass

        # Another segfault only when run early
        # (before PyType_Ready(tuple) ni called)
        type.mro(tuple)


kundi MiscTests(unittest.TestCase):
    eleza test_type_lookup_mro_reference(self):
        # Issue #14199: _PyType_Lookup() has to keep a strong reference to
        # the type MRO because it may be modified during the lookup, if
        # __bases__ ni set during the lookup kila example.
        kundi MyKey(object):
            eleza __hash__(self):
                rudisha hash('mykey')

            eleza __eq__(self, other):
                X.__bases__ = (Base2,)

        kundi Base(object):
            mykey = 'kutoka Base'
            mykey2 = 'kutoka Base'

        kundi Base2(object):
            mykey = 'kutoka Base2'
            mykey2 = 'kutoka Base2'

        X = type('X', (Base,), {MyKey(): 5})
        # mykey ni read kutoka Base
        self.assertEqual(X.mykey, 'kutoka Base')
        # mykey2 ni read kutoka Base2 because MyKey.__eq__ has set __bases__
        self.assertEqual(X.mykey2, 'kutoka Base2')


kundi PicklingTests(unittest.TestCase):

    eleza _check_reduce(self, proto, obj, args=(), kwargs={}, state=Tupu,
                      listitems=Tupu, dictitems=Tupu):
        ikiwa proto >= 2:
            reduce_value = obj.__reduce_ex__(proto)
            ikiwa kwargs:
                self.assertEqual(reduce_value[0], copyreg.__newobj_ex__)
                self.assertEqual(reduce_value[1], (type(obj), args, kwargs))
            isipokua:
                self.assertEqual(reduce_value[0], copyreg.__newobj__)
                self.assertEqual(reduce_value[1], (type(obj),) + args)
            self.assertEqual(reduce_value[2], state)
            ikiwa listitems ni sio Tupu:
                self.assertListEqual(list(reduce_value[3]), listitems)
            isipokua:
                self.assertIsTupu(reduce_value[3])
            ikiwa dictitems ni sio Tupu:
                self.assertDictEqual(dict(reduce_value[4]), dictitems)
            isipokua:
                self.assertIsTupu(reduce_value[4])
        isipokua:
            base_type = type(obj).__base__
            reduce_value = (copyreg._reconstructor,
                            (type(obj),
                             base_type,
                             Tupu ikiwa base_type ni object isipokua base_type(obj)))
            ikiwa state ni sio Tupu:
                reduce_value += (state,)
            self.assertEqual(obj.__reduce_ex__(proto), reduce_value)
            self.assertEqual(obj.__reduce__(), reduce_value)

    eleza test_reduce(self):
        protocols = range(pickle.HIGHEST_PROTOCOL + 1)
        args = (-101, "spam")
        kwargs = {'bacon': -201, 'fish': -301}
        state = {'cheese': -401}

        kundi C1:
            eleza __getnewargs__(self):
                rudisha args
        obj = C1()
        kila proto kwenye protocols:
            self._check_reduce(proto, obj, args)

        kila name, value kwenye state.items():
            setattr(obj, name, value)
        kila proto kwenye protocols:
            self._check_reduce(proto, obj, args, state=state)

        kundi C2:
            eleza __getnewargs__(self):
                rudisha "bad args"
        obj = C2()
        kila proto kwenye protocols:
            ikiwa proto >= 2:
                ukijumuisha self.assertRaises(TypeError):
                    obj.__reduce_ex__(proto)

        kundi C3:
            eleza __getnewargs_ex__(self):
                rudisha (args, kwargs)
        obj = C3()
        kila proto kwenye protocols:
            ikiwa proto >= 2:
                self._check_reduce(proto, obj, args, kwargs)

        kundi C4:
            eleza __getnewargs_ex__(self):
                rudisha (args, "bad dict")
        kundi C5:
            eleza __getnewargs_ex__(self):
                rudisha ("bad tuple", kwargs)
        kundi C6:
            eleza __getnewargs_ex__(self):
                rudisha ()
        kundi C7:
            eleza __getnewargs_ex__(self):
                rudisha "bad args"
        kila proto kwenye protocols:
            kila cls kwenye C4, C5, C6, C7:
                obj = cls()
                ikiwa proto >= 2:
                    ukijumuisha self.assertRaises((TypeError, ValueError)):
                        obj.__reduce_ex__(proto)

        kundi C9:
            eleza __getnewargs_ex__(self):
                rudisha (args, {})
        obj = C9()
        kila proto kwenye protocols:
            self._check_reduce(proto, obj, args)

        kundi C10:
            eleza __getnewargs_ex__(self):
                 ashiria IndexError
        obj = C10()
        kila proto kwenye protocols:
            ikiwa proto >= 2:
                ukijumuisha self.assertRaises(IndexError):
                    obj.__reduce_ex__(proto)

        kundi C11:
            eleza __getstate__(self):
                rudisha state
        obj = C11()
        kila proto kwenye protocols:
            self._check_reduce(proto, obj, state=state)

        kundi C12:
            eleza __getstate__(self):
                rudisha "not dict"
        obj = C12()
        kila proto kwenye protocols:
            self._check_reduce(proto, obj, state="not dict")

        kundi C13:
            eleza __getstate__(self):
                 ashiria IndexError
        obj = C13()
        kila proto kwenye protocols:
            ukijumuisha self.assertRaises(IndexError):
                obj.__reduce_ex__(proto)
            ikiwa proto < 2:
                ukijumuisha self.assertRaises(IndexError):
                    obj.__reduce__()

        kundi C14:
            __slots__ = tuple(state)
            eleza __init__(self):
                kila name, value kwenye state.items():
                    setattr(self, name, value)

        obj = C14()
        kila proto kwenye protocols:
            ikiwa proto >= 2:
                self._check_reduce(proto, obj, state=(Tupu, state))
            isipokua:
                ukijumuisha self.assertRaises(TypeError):
                    obj.__reduce_ex__(proto)
                ukijumuisha self.assertRaises(TypeError):
                    obj.__reduce__()

        kundi C15(dict):
            pass
        obj = C15({"quebec": -601})
        kila proto kwenye protocols:
            self._check_reduce(proto, obj, dictitems=dict(obj))

        kundi C16(list):
            pass
        obj = C16(["yukon"])
        kila proto kwenye protocols:
            self._check_reduce(proto, obj, listitems=list(obj))

    eleza test_special_method_lookup(self):
        protocols = range(pickle.HIGHEST_PROTOCOL + 1)
        kundi Picky:
            eleza __getstate__(self):
                rudisha {}

            eleza __getattr__(self, attr):
                ikiwa attr kwenye ("__getnewargs__", "__getnewargs_ex__"):
                     ashiria AssertionError(attr)
                rudisha Tupu
        kila protocol kwenye protocols:
            state = {} ikiwa protocol >= 2 isipokua Tupu
            self._check_reduce(protocol, Picky(), state=state)

    eleza _assert_is_copy(self, obj, objcopy, msg=Tupu):
        """Utility method to verify ikiwa two objects are copies of each others.
        """
        ikiwa msg ni Tupu:
            msg = "{!r} ni sio a copy of {!r}".format(obj, objcopy)
        ikiwa type(obj).__repr__ ni object.__repr__:
            # We have this limitation kila now because we use the object's repr
            # to help us verify that the two objects are copies. This allows
            # us to delegate the non-generic verification logic to the objects
            # themselves.
             ashiria ValueError("object passed to _assert_is_copy must " +
                             "override the __repr__ method.")
        self.assertIsNot(obj, objcopy, msg=msg)
        self.assertIs(type(obj), type(objcopy), msg=msg)
        ikiwa hasattr(obj, '__dict__'):
            self.assertDictEqual(obj.__dict__, objcopy.__dict__, msg=msg)
            self.assertIsNot(obj.__dict__, objcopy.__dict__, msg=msg)
        ikiwa hasattr(obj, '__slots__'):
            self.assertListEqual(obj.__slots__, objcopy.__slots__, msg=msg)
            kila slot kwenye obj.__slots__:
                self.assertEqual(
                    hasattr(obj, slot), hasattr(objcopy, slot), msg=msg)
                self.assertEqual(getattr(obj, slot, Tupu),
                                 getattr(objcopy, slot, Tupu), msg=msg)
        self.assertEqual(repr(obj), repr(objcopy), msg=msg)

    @staticmethod
    eleza _generate_pickle_copiers():
        """Utility method to generate the many possible pickle configurations.
        """
        kundi PickleCopier:
            "This kundi copies object using pickle."
            eleza __init__(self, proto, dumps, loads):
                self.proto = proto
                self.dumps = dumps
                self.loads = loads
            eleza copy(self, obj):
                rudisha self.loads(self.dumps(obj, self.proto))
            eleza __repr__(self):
                # We try to be as descriptive as possible here since this is
                # the string which we will allow us to tell the pickle
                # configuration we are using during debugging.
                rudisha ("PickleCopier(proto={}, dumps={}.{}, loads={}.{})"
                        .format(self.proto,
                                self.dumps.__module__, self.dumps.__qualname__,
                                self.loads.__module__, self.loads.__qualname__))
        rudisha (PickleCopier(*args) kila args in
                   itertools.product(range(pickle.HIGHEST_PROTOCOL + 1),
                                     {pickle.dumps, pickle._dumps},
                                     {pickle.loads, pickle._loads}))

    eleza test_pickle_slots(self):
        # Tests pickling of classes ukijumuisha __slots__.

        # Pickling of classes ukijumuisha __slots__ but without __getstate__ should
        # fail (ikiwa using protocol 0 ama 1)
        global C
        kundi C:
            __slots__ = ['a']
        ukijumuisha self.assertRaises(TypeError):
            pickle.dumps(C(), 0)

        global D
        kundi D(C):
            pass
        ukijumuisha self.assertRaises(TypeError):
            pickle.dumps(D(), 0)

        kundi C:
            "A kundi ukijumuisha __getstate__ na __setstate__ implemented."
            __slots__ = ['a']
            eleza __getstate__(self):
                state = getattr(self, '__dict__', {}).copy()
                kila cls kwenye type(self).__mro__:
                    kila slot kwenye cls.__dict__.get('__slots__', ()):
                        jaribu:
                            state[slot] = getattr(self, slot)
                        except AttributeError:
                            pass
                rudisha state
            eleza __setstate__(self, state):
                kila k, v kwenye state.items():
                    setattr(self, k, v)
            eleza __repr__(self):
                rudisha "%s()<%r>" % (type(self).__name__, self.__getstate__())

        kundi D(C):
            "A subkundi of a kundi ukijumuisha slots."
            pass

        global E
        kundi E(C):
            "A subkundi ukijumuisha an extra slot."
            __slots__ = ['b']

        # Now it should work
        kila pickle_copier kwenye self._generate_pickle_copiers():
            ukijumuisha self.subTest(pickle_copier=pickle_copier):
                x = C()
                y = pickle_copier.copy(x)
                self._assert_is_copy(x, y)

                x.a = 42
                y = pickle_copier.copy(x)
                self._assert_is_copy(x, y)

                x = D()
                x.a = 42
                x.b = 100
                y = pickle_copier.copy(x)
                self._assert_is_copy(x, y)

                x = E()
                x.a = 42
                x.b = "foo"
                y = pickle_copier.copy(x)
                self._assert_is_copy(x, y)

    eleza test_reduce_copying(self):
        # Tests pickling na copying new-style classes na objects.
        global C1
        kundi C1:
            "The state of this kundi ni copyable via its instance dict."
            ARGS = (1, 2)
            NEED_DICT_COPYING = Kweli
            eleza __init__(self, a, b):
                super().__init__()
                self.a = a
                self.b = b
            eleza __repr__(self):
                rudisha "C1(%r, %r)" % (self.a, self.b)

        global C2
        kundi C2(list):
            "A list subkundi copyable via __getnewargs__."
            ARGS = (1, 2)
            NEED_DICT_COPYING = Uongo
            eleza __new__(cls, a, b):
                self = super().__new__(cls)
                self.a = a
                self.b = b
                rudisha self
            eleza __init__(self, *args):
                super().__init__()
                # This helps testing that __init__ ni sio called during the
                # unpickling process, which would cause extra appends.
                self.append("cheese")
            @classmethod
            eleza __getnewargs__(cls):
                rudisha cls.ARGS
            eleza __repr__(self):
                rudisha "C2(%r, %r)<%r>" % (self.a, self.b, list(self))

        global C3
        kundi C3(list):
            "A list subkundi copyable via __getstate__."
            ARGS = (1, 2)
            NEED_DICT_COPYING = Uongo
            eleza __init__(self, a, b):
                self.a = a
                self.b = b
                # This helps testing that __init__ ni sio called during the
                # unpickling process, which would cause extra appends.
                self.append("cheese")
            @classmethod
            eleza __getstate__(cls):
                rudisha cls.ARGS
            eleza __setstate__(self, state):
                a, b = state
                self.a = a
                self.b = b
            eleza __repr__(self):
                rudisha "C3(%r, %r)<%r>" % (self.a, self.b, list(self))

        global C4
        kundi C4(int):
            "An int subkundi copyable via __getnewargs__."
            ARGS = ("hello", "world", 1)
            NEED_DICT_COPYING = Uongo
            eleza __new__(cls, a, b, value):
                self = super().__new__(cls, value)
                self.a = a
                self.b = b
                rudisha self
            @classmethod
            eleza __getnewargs__(cls):
                rudisha cls.ARGS
            eleza __repr__(self):
                rudisha "C4(%r, %r)<%r>" % (self.a, self.b, int(self))

        global C5
        kundi C5(int):
            "An int subkundi copyable via __getnewargs_ex__."
            ARGS = (1, 2)
            KWARGS = {'value': 3}
            NEED_DICT_COPYING = Uongo
            eleza __new__(cls, a, b, *, value=0):
                self = super().__new__(cls, value)
                self.a = a
                self.b = b
                rudisha self
            @classmethod
            eleza __getnewargs_ex__(cls):
                rudisha (cls.ARGS, cls.KWARGS)
            eleza __repr__(self):
                rudisha "C5(%r, %r)<%r>" % (self.a, self.b, int(self))

        test_classes = (C1, C2, C3, C4, C5)
        # Testing copying through pickle
        pickle_copiers = self._generate_pickle_copiers()
        kila cls, pickle_copier kwenye itertools.product(test_classes, pickle_copiers):
            ukijumuisha self.subTest(cls=cls, pickle_copier=pickle_copier):
                kwargs = getattr(cls, 'KWARGS', {})
                obj = cls(*cls.ARGS, **kwargs)
                proto = pickle_copier.proto
                objcopy = pickle_copier.copy(obj)
                self._assert_is_copy(obj, objcopy)
                # For test classes that supports this, make sure we didn't go
                # around the reduce protocol by simply copying the attribute
                # dictionary. We clear attributes using the previous copy to
                # sio mutate the original argument.
                ikiwa proto >= 2 na sio cls.NEED_DICT_COPYING:
                    objcopy.__dict__.clear()
                    objcopy2 = pickle_copier.copy(objcopy)
                    self._assert_is_copy(obj, objcopy2)

        # Testing copying through copy.deepcopy()
        kila cls kwenye test_classes:
            ukijumuisha self.subTest(cls=cls):
                kwargs = getattr(cls, 'KWARGS', {})
                obj = cls(*cls.ARGS, **kwargs)
                objcopy = deepcopy(obj)
                self._assert_is_copy(obj, objcopy)
                # For test classes that supports this, make sure we didn't go
                # around the reduce protocol by simply copying the attribute
                # dictionary. We clear attributes using the previous copy to
                # sio mutate the original argument.
                ikiwa sio cls.NEED_DICT_COPYING:
                    objcopy.__dict__.clear()
                    objcopy2 = deepcopy(objcopy)
                    self._assert_is_copy(obj, objcopy2)

    eleza test_issue24097(self):
        # Slot name ni freed inside __getattr__ na ni later used.
        kundi S(str):  # Not interned
            pass
        kundi A:
            __slotnames__ = [S('spam')]
            eleza __getattr__(self, attr):
                ikiwa attr == 'spam':
                    A.__slotnames__[:] = [S('spam')]
                    rudisha 42
                isipokua:
                     ashiria AttributeError

        agiza copyreg
        expected = (copyreg.__newobj__, (A,), (Tupu, {'spam': 42}), Tupu, Tupu)
        self.assertEqual(A().__reduce_ex__(2), expected)  # Shouldn't crash

    eleza test_object_reduce(self):
        # Issue #29914
        # __reduce__() takes no arguments
        object().__reduce__()
        ukijumuisha self.assertRaises(TypeError):
            object().__reduce__(0)
        # __reduce_ex__() takes one integer argument
        object().__reduce_ex__(0)
        ukijumuisha self.assertRaises(TypeError):
            object().__reduce_ex__()
        ukijumuisha self.assertRaises(TypeError):
            object().__reduce_ex__(Tupu)


kundi SharedKeyTests(unittest.TestCase):

    @support.cpython_only
    eleza test_subclasses(self):
        # Verify that subclasses can share keys (per PEP 412)
        kundi A:
            pass
        kundi B(A):
            pass

        a, b = A(), B()
        self.assertEqual(sys.getsizeof(vars(a)), sys.getsizeof(vars(b)))
        self.assertLess(sys.getsizeof(vars(a)), sys.getsizeof({"a":1}))
        # Initial hash table can contain at most 5 elements.
        # Set 6 attributes to cause internal resizing.
        a.x, a.y, a.z, a.w, a.v, a.u = range(6)
        self.assertNotEqual(sys.getsizeof(vars(a)), sys.getsizeof(vars(b)))
        a2 = A()
        self.assertEqual(sys.getsizeof(vars(a)), sys.getsizeof(vars(a2)))
        self.assertLess(sys.getsizeof(vars(a)), sys.getsizeof({"a":1}))
        b.u, b.v, b.w, b.t, b.s, b.r = range(6)
        self.assertLess(sys.getsizeof(vars(b)), sys.getsizeof({"a":1}))


kundi DebugHelperMeta(type):
    """
    Sets default __doc__ na simplifies repr() output.
    """
    eleza __new__(mcls, name, bases, attrs):
        ikiwa attrs.get('__doc__') ni Tupu:
            attrs['__doc__'] = name  # helps when debugging ukijumuisha gdb
        rudisha type.__new__(mcls, name, bases, attrs)
    eleza __repr__(cls):
        rudisha repr(cls.__name__)


kundi MroTest(unittest.TestCase):
    """
    Regressions kila some bugs revealed through
    mcsl.mro() customization (typeobject.c: mro_internal()) and
    cls.__bases__ assignment (typeobject.c: type_set_bases()).
    """

    eleza setUp(self):
        self.step = 0
        self.ready = Uongo

    eleza step_until(self, limit):
        ret = (self.step < limit)
        ikiwa ret:
            self.step += 1
        rudisha ret

    eleza test_incomplete_set_bases_on_self(self):
        """
        type_set_bases must be aware that type->tp_mro can be NULL.
        """
        kundi M(DebugHelperMeta):
            eleza mro(cls):
                ikiwa self.step_until(1):
                    assert cls.__mro__ ni Tupu
                    cls.__bases__ += ()

                rudisha type.mro(cls)

        kundi A(metaclass=M):
            pass

    eleza test_reent_set_bases_on_base(self):
        """
        Deep reentrancy must sio over-decref old_mro.
        """
        kundi M(DebugHelperMeta):
            eleza mro(cls):
                ikiwa cls.__mro__ ni sio Tupu na cls.__name__ == 'B':
                    # 4-5 steps are usually enough to make it crash somewhere
                    ikiwa self.step_until(10):
                        A.__bases__ += ()

                rudisha type.mro(cls)

        kundi A(metaclass=M):
            pass
        kundi B(A):
            pass
        B.__bases__ += ()

    eleza test_reent_set_bases_on_direct_base(self):
        """
        Similar to test_reent_set_bases_on_base, but may crash differently.
        """
        kundi M(DebugHelperMeta):
            eleza mro(cls):
                base = cls.__bases__[0]
                ikiwa base ni sio object:
                    ikiwa self.step_until(5):
                        base.__bases__ += ()

                rudisha type.mro(cls)

        kundi A(metaclass=M):
            pass
        kundi B(A):
            pass
        kundi C(B):
            pass

    eleza test_reent_set_bases_tp_base_cycle(self):
        """
        type_set_bases must check kila an inheritance cycle sio only through
        MRO of the type, which may be sio yet updated kwenye case of reentrance,
        but also through tp_base chain, which ni assigned before diving into
        inner calls to mro().

        Otherwise, the following snippet can loop forever:
            do {
                // ...
                type = type->tp_base;
            } wakati (type != NULL);

        Functions that rely on tp_base (like solid_base na PyType_IsSubtype)
        would sio be happy kwenye that case, causing a stack overflow.
        """
        kundi M(DebugHelperMeta):
            eleza mro(cls):
                ikiwa self.ready:
                    ikiwa cls.__name__ == 'B1':
                        B2.__bases__ = (B1,)
                    ikiwa cls.__name__ == 'B2':
                        B1.__bases__ = (B2,)
                rudisha type.mro(cls)

        kundi A(metaclass=M):
            pass
        kundi B1(A):
            pass
        kundi B2(A):
            pass

        self.ready = Kweli
        ukijumuisha self.assertRaises(TypeError):
            B1.__bases__ += ()

    eleza test_tp_subclasses_cycle_in_update_slots(self):
        """
        type_set_bases must check kila reentrancy upon finishing its job
        by updating tp_subclasses of old/new bases of the type.
        Otherwise, an implicit inheritance cycle through tp_subclasses
        can koma functions that recurse on elements of that field
        (like recurse_down_subclasses na mro_hierarchy) eventually
        leading to a stack overflow.
        """
        kundi M(DebugHelperMeta):
            eleza mro(cls):
                ikiwa self.ready na cls.__name__ == 'C':
                    self.ready = Uongo
                    C.__bases__ = (B2,)
                rudisha type.mro(cls)

        kundi A(metaclass=M):
            pass
        kundi B1(A):
            pass
        kundi B2(A):
            pass
        kundi C(A):
            pass

        self.ready = Kweli
        C.__bases__ = (B1,)
        B1.__bases__ = (C,)

        self.assertEqual(C.__bases__, (B2,))
        self.assertEqual(B2.__subclasses__(), [C])
        self.assertEqual(B1.__subclasses__(), [])

        self.assertEqual(B1.__bases__, (C,))
        self.assertEqual(C.__subclasses__(), [B1])

    eleza test_tp_subclasses_cycle_error_return_path(self):
        """
        The same as test_tp_subclasses_cycle_in_update_slots, but tests
        a code path executed on error (goto bail).
        """
        kundi E(Exception):
            pass
        kundi M(DebugHelperMeta):
            eleza mro(cls):
                ikiwa self.ready na cls.__name__ == 'C':
                    ikiwa C.__bases__ == (B2,):
                        self.ready = Uongo
                    isipokua:
                        C.__bases__ = (B2,)
                         ashiria E
                rudisha type.mro(cls)

        kundi A(metaclass=M):
            pass
        kundi B1(A):
            pass
        kundi B2(A):
            pass
        kundi C(A):
            pass

        self.ready = Kweli
        ukijumuisha self.assertRaises(E):
            C.__bases__ = (B1,)
        B1.__bases__ = (C,)

        self.assertEqual(C.__bases__, (B2,))
        self.assertEqual(C.__mro__, tuple(type.mro(C)))

    eleza test_incomplete_extend(self):
        """
        Extending an unitialized type ukijumuisha type->tp_mro == NULL must
        throw a reasonable TypeError exception, instead of failing
        ukijumuisha PyErr_BadInternalCall.
        """
        kundi M(DebugHelperMeta):
            eleza mro(cls):
                ikiwa cls.__mro__ ni Tupu na cls.__name__ != 'X':
                    ukijumuisha self.assertRaises(TypeError):
                        kundi X(cls):
                            pass

                rudisha type.mro(cls)

        kundi A(metaclass=M):
            pass

    eleza test_incomplete_super(self):
        """
        Attrubute lookup on a super object must be aware that
        its target type can be uninitialized (type->tp_mro == NULL).
        """
        kundi M(DebugHelperMeta):
            eleza mro(cls):
                ikiwa cls.__mro__ ni Tupu:
                    ukijumuisha self.assertRaises(AttributeError):
                        super(cls, cls).xxx

                rudisha type.mro(cls)

        kundi A(metaclass=M):
            pass


eleza test_main():
    # Run all local test cases, ukijumuisha PTypesLongInitTest first.
    support.run_unittest(PTypesLongInitTest, OperatorsTest,
                         ClassPropertiesAndMethods, DictProxyTests,
                         MiscTests, PicklingTests, SharedKeyTests,
                         MroTest)

ikiwa __name__ == "__main__":
    test_main()
