# tests common to dict and UserDict
agiza unittest
agiza collections
agiza sys


kundi BasicTestMappingProtocol(unittest.TestCase):
    # This base kundi can be used to check that an object conforms to the
    # mapping protocol

    # Functions that can be useful to override to adapt to dictionary
    # semantics
    type2test = None # which kundi is being tested (overwrite in subclasses)

    eleza _reference(self):
        """Return a dictionary of values which are invariant by storage
        in the object under test."""
        rudisha {"1": "2", "key1":"value1", "key2":(1,2,3)}
    eleza _empty_mapping(self):
        """Return an empty mapping object"""
        rudisha self.type2test()
    eleza _full_mapping(self, data):
        """Return a mapping object with the value contained in data
        dictionary"""
        x = self._empty_mapping()
        for key, value in data.items():
            x[key] = value
        rudisha x

    eleza __init__(self, *args, **kw):
        unittest.TestCase.__init__(self, *args, **kw)
        self.reference = self._reference().copy()

        # A (key, value) pair not in the mapping
        key, value = self.reference.popitem()
        self.other = {key:value}

        # A (key, value) pair in the mapping
        key, value = self.reference.popitem()
        self.inmapping = {key:value}
        self.reference[key] = value

    eleza test_read(self):
        # Test for read only operations on mapping
        p = self._empty_mapping()
        p1 = dict(p) #workaround for singleton objects
        d = self._full_mapping(self.reference)
        ikiwa d is p:
            p = p1
        #Indexing
        for key, value in self.reference.items():
            self.assertEqual(d[key], value)
        knownkey = list(self.other.keys())[0]
        self.assertRaises(KeyError, lambda:d[knownkey])
        #len
        self.assertEqual(len(p), 0)
        self.assertEqual(len(d), len(self.reference))
        #__contains__
        for k in self.reference:
            self.assertIn(k, d)
        for k in self.other:
            self.assertNotIn(k, d)
        #cmp
        self.assertEqual(p, p)
        self.assertEqual(d, d)
        self.assertNotEqual(p, d)
        self.assertNotEqual(d, p)
        #bool
        ikiwa p: self.fail("Empty mapping must compare to False")
        ikiwa not d: self.fail("Full mapping must compare to True")
        # keys(), items(), iterkeys() ...
        eleza check_iterandlist(iter, lst, ref):
            self.assertTrue(hasattr(iter, '__next__'))
            self.assertTrue(hasattr(iter, '__iter__'))
            x = list(iter)
            self.assertTrue(set(x)==set(lst)==set(ref))
        check_iterandlist(iter(d.keys()), list(d.keys()),
                          self.reference.keys())
        check_iterandlist(iter(d), list(d.keys()), self.reference.keys())
        check_iterandlist(iter(d.values()), list(d.values()),
                          self.reference.values())
        check_iterandlist(iter(d.items()), list(d.items()),
                          self.reference.items())
        #get
        key, value = next(iter(d.items()))
        knownkey, knownvalue = next(iter(self.other.items()))
        self.assertEqual(d.get(key, knownvalue), value)
        self.assertEqual(d.get(knownkey, knownvalue), knownvalue)
        self.assertNotIn(knownkey, d)

    eleza test_write(self):
        # Test for write operations on mapping
        p = self._empty_mapping()
        #Indexing
        for key, value in self.reference.items():
            p[key] = value
            self.assertEqual(p[key], value)
        for key in self.reference.keys():
            del p[key]
            self.assertRaises(KeyError, lambda:p[key])
        p = self._empty_mapping()
        #update
        p.update(self.reference)
        self.assertEqual(dict(p), self.reference)
        items = list(p.items())
        p = self._empty_mapping()
        p.update(items)
        self.assertEqual(dict(p), self.reference)
        d = self._full_mapping(self.reference)
        #setdefault
        key, value = next(iter(d.items()))
        knownkey, knownvalue = next(iter(self.other.items()))
        self.assertEqual(d.setdefault(key, knownvalue), value)
        self.assertEqual(d[key], value)
        self.assertEqual(d.setdefault(knownkey, knownvalue), knownvalue)
        self.assertEqual(d[knownkey], knownvalue)
        #pop
        self.assertEqual(d.pop(knownkey), knownvalue)
        self.assertNotIn(knownkey, d)
        self.assertRaises(KeyError, d.pop, knownkey)
        default = 909
        d[knownkey] = knownvalue
        self.assertEqual(d.pop(knownkey, default), knownvalue)
        self.assertNotIn(knownkey, d)
        self.assertEqual(d.pop(knownkey, default), default)
        #popitem
        key, value = d.popitem()
        self.assertNotIn(key, d)
        self.assertEqual(value, self.reference[key])
        p=self._empty_mapping()
        self.assertRaises(KeyError, p.popitem)

    eleza test_constructor(self):
        self.assertEqual(self._empty_mapping(), self._empty_mapping())

    eleza test_bool(self):
        self.assertTrue(not self._empty_mapping())
        self.assertTrue(self.reference)
        self.assertTrue(bool(self._empty_mapping()) is False)
        self.assertTrue(bool(self.reference) is True)

    eleza test_keys(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.keys()), [])
        d = self.reference
        self.assertIn(list(self.inmapping.keys())[0], d.keys())
        self.assertNotIn(list(self.other.keys())[0], d.keys())
        self.assertRaises(TypeError, d.keys, None)

    eleza test_values(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.values()), [])

        self.assertRaises(TypeError, d.values, None)

    eleza test_items(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.items()), [])

        self.assertRaises(TypeError, d.items, None)

    eleza test_len(self):
        d = self._empty_mapping()
        self.assertEqual(len(d), 0)

    eleza test_getitem(self):
        d = self.reference
        self.assertEqual(d[list(self.inmapping.keys())[0]],
                         list(self.inmapping.values())[0])

        self.assertRaises(TypeError, d.__getitem__)

    eleza test_update(self):
        # mapping argument
        d = self._empty_mapping()
        d.update(self.other)
        self.assertEqual(list(d.items()), list(self.other.items()))

        # No argument
        d = self._empty_mapping()
        d.update()
        self.assertEqual(d, self._empty_mapping())

        # item sequence
        d = self._empty_mapping()
        d.update(self.other.items())
        self.assertEqual(list(d.items()), list(self.other.items()))

        # Iterator
        d = self._empty_mapping()
        d.update(self.other.items())
        self.assertEqual(list(d.items()), list(self.other.items()))

        # FIXME: Doesn't work with UserDict
        # self.assertRaises((TypeError, AttributeError), d.update, None)
        self.assertRaises((TypeError, AttributeError), d.update, 42)

        outerself = self
        kundi SimpleUserDict:
            eleza __init__(self):
                self.d = outerself.reference
            eleza keys(self):
                rudisha self.d.keys()
            eleza __getitem__(self, i):
                rudisha self.d[i]
        d.clear()
        d.update(SimpleUserDict())
        i1 = sorted(d.items())
        i2 = sorted(self.reference.items())
        self.assertEqual(i1, i2)

        kundi Exc(Exception): pass

        d = self._empty_mapping()
        kundi FailingUserDict:
            eleza keys(self):
                raise Exc
        self.assertRaises(Exc, d.update, FailingUserDict())

        d.clear()

        kundi FailingUserDict:
            eleza keys(self):
                kundi BogonIter:
                    eleza __init__(self):
                        self.i = 1
                    eleza __iter__(self):
                        rudisha self
                    eleza __next__(self):
                        ikiwa self.i:
                            self.i = 0
                            rudisha 'a'
                        raise Exc
                rudisha BogonIter()
            eleza __getitem__(self, key):
                rudisha key
        self.assertRaises(Exc, d.update, FailingUserDict())

        kundi FailingUserDict:
            eleza keys(self):
                kundi BogonIter:
                    eleza __init__(self):
                        self.i = ord('a')
                    eleza __iter__(self):
                        rudisha self
                    eleza __next__(self):
                        ikiwa self.i <= ord('z'):
                            rtn = chr(self.i)
                            self.i += 1
                            rudisha rtn
                        raise StopIteration
                rudisha BogonIter()
            eleza __getitem__(self, key):
                raise Exc
        self.assertRaises(Exc, d.update, FailingUserDict())

        d = self._empty_mapping()
        kundi badseq(object):
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                raise Exc()

        self.assertRaises(Exc, d.update, badseq())

        self.assertRaises(ValueError, d.update, [(1, 2, 3)])

    # no test_kutokakeys or test_copy as both os.environ and selves don't support it

    eleza test_get(self):
        d = self._empty_mapping()
        self.assertTrue(d.get(list(self.other.keys())[0]) is None)
        self.assertEqual(d.get(list(self.other.keys())[0], 3), 3)
        d = self.reference
        self.assertTrue(d.get(list(self.other.keys())[0]) is None)
        self.assertEqual(d.get(list(self.other.keys())[0], 3), 3)
        self.assertEqual(d.get(list(self.inmapping.keys())[0]),
                         list(self.inmapping.values())[0])
        self.assertEqual(d.get(list(self.inmapping.keys())[0], 3),
                         list(self.inmapping.values())[0])
        self.assertRaises(TypeError, d.get)
        self.assertRaises(TypeError, d.get, None, None, None)

    eleza test_setdefault(self):
        d = self._empty_mapping()
        self.assertRaises(TypeError, d.setdefault)

    eleza test_popitem(self):
        d = self._empty_mapping()
        self.assertRaises(KeyError, d.popitem)
        self.assertRaises(TypeError, d.popitem, 42)

    eleza test_pop(self):
        d = self._empty_mapping()
        k, v = list(self.inmapping.items())[0]
        d[k] = v
        self.assertRaises(KeyError, d.pop, list(self.other.keys())[0])

        self.assertEqual(d.pop(k), v)
        self.assertEqual(len(d), 0)

        self.assertRaises(KeyError, d.pop, k)


kundi TestMappingProtocol(BasicTestMappingProtocol):
    eleza test_constructor(self):
        BasicTestMappingProtocol.test_constructor(self)
        self.assertTrue(self._empty_mapping() is not self._empty_mapping())
        self.assertEqual(self.type2test(x=1, y=2), {"x": 1, "y": 2})

    eleza test_bool(self):
        BasicTestMappingProtocol.test_bool(self)
        self.assertTrue(not self._empty_mapping())
        self.assertTrue(self._full_mapping({"x": "y"}))
        self.assertTrue(bool(self._empty_mapping()) is False)
        self.assertTrue(bool(self._full_mapping({"x": "y"})) is True)

    eleza test_keys(self):
        BasicTestMappingProtocol.test_keys(self)
        d = self._empty_mapping()
        self.assertEqual(list(d.keys()), [])
        d = self._full_mapping({'a': 1, 'b': 2})
        k = d.keys()
        self.assertIn('a', k)
        self.assertIn('b', k)
        self.assertNotIn('c', k)

    eleza test_values(self):
        BasicTestMappingProtocol.test_values(self)
        d = self._full_mapping({1:2})
        self.assertEqual(list(d.values()), [2])

    eleza test_items(self):
        BasicTestMappingProtocol.test_items(self)

        d = self._full_mapping({1:2})
        self.assertEqual(list(d.items()), [(1, 2)])

    eleza test_contains(self):
        d = self._empty_mapping()
        self.assertNotIn('a', d)
        self.assertTrue(not ('a' in d))
        self.assertTrue('a' not in d)
        d = self._full_mapping({'a': 1, 'b': 2})
        self.assertIn('a', d)
        self.assertIn('b', d)
        self.assertNotIn('c', d)

        self.assertRaises(TypeError, d.__contains__)

    eleza test_len(self):
        BasicTestMappingProtocol.test_len(self)
        d = self._full_mapping({'a': 1, 'b': 2})
        self.assertEqual(len(d), 2)

    eleza test_getitem(self):
        BasicTestMappingProtocol.test_getitem(self)
        d = self._full_mapping({'a': 1, 'b': 2})
        self.assertEqual(d['a'], 1)
        self.assertEqual(d['b'], 2)
        d['c'] = 3
        d['a'] = 4
        self.assertEqual(d['c'], 3)
        self.assertEqual(d['a'], 4)
        del d['b']
        self.assertEqual(d, {'a': 4, 'c': 3})

        self.assertRaises(TypeError, d.__getitem__)

    eleza test_clear(self):
        d = self._full_mapping({1:1, 2:2, 3:3})
        d.clear()
        self.assertEqual(d, {})

        self.assertRaises(TypeError, d.clear, None)

    eleza test_update(self):
        BasicTestMappingProtocol.test_update(self)
        # mapping argument
        d = self._empty_mapping()
        d.update({1:100})
        d.update({2:20})
        d.update({1:1, 2:2, 3:3})
        self.assertEqual(d, {1:1, 2:2, 3:3})

        # no argument
        d.update()
        self.assertEqual(d, {1:1, 2:2, 3:3})

        # keyword arguments
        d = self._empty_mapping()
        d.update(x=100)
        d.update(y=20)
        d.update(x=1, y=2, z=3)
        self.assertEqual(d, {"x":1, "y":2, "z":3})

        # item sequence
        d = self._empty_mapping()
        d.update([("x", 100), ("y", 20)])
        self.assertEqual(d, {"x":100, "y":20})

        # Both item sequence and keyword arguments
        d = self._empty_mapping()
        d.update([("x", 100), ("y", 20)], x=1, y=2)
        self.assertEqual(d, {"x":1, "y":2})

        # iterator
        d = self._full_mapping({1:3, 2:4})
        d.update(self._full_mapping({1:2, 3:4, 5:6}).items())
        self.assertEqual(d, {1:2, 2:4, 3:4, 5:6})

        kundi SimpleUserDict:
            eleza __init__(self):
                self.d = {1:1, 2:2, 3:3}
            eleza keys(self):
                rudisha self.d.keys()
            eleza __getitem__(self, i):
                rudisha self.d[i]
        d.clear()
        d.update(SimpleUserDict())
        self.assertEqual(d, {1:1, 2:2, 3:3})

    eleza test_kutokakeys(self):
        self.assertEqual(self.type2test.kutokakeys('abc'), {'a':None, 'b':None, 'c':None})
        d = self._empty_mapping()
        self.assertTrue(not(d.kutokakeys('abc') is d))
        self.assertEqual(d.kutokakeys('abc'), {'a':None, 'b':None, 'c':None})
        self.assertEqual(d.kutokakeys((4,5),0), {4:0, 5:0})
        self.assertEqual(d.kutokakeys([]), {})
        eleza g():
            yield 1
        self.assertEqual(d.kutokakeys(g()), {1:None})
        self.assertRaises(TypeError, {}.kutokakeys, 3)
        kundi dictlike(self.type2test): pass
        self.assertEqual(dictlike.kutokakeys('a'), {'a':None})
        self.assertEqual(dictlike().kutokakeys('a'), {'a':None})
        self.assertTrue(dictlike.kutokakeys('a').__class__ is dictlike)
        self.assertTrue(dictlike().kutokakeys('a').__class__ is dictlike)
        self.assertTrue(type(dictlike.kutokakeys('a')) is dictlike)
        kundi mydict(self.type2test):
            eleza __new__(cls):
                rudisha collections.UserDict()
        ud = mydict.kutokakeys('ab')
        self.assertEqual(ud, {'a':None, 'b':None})
        self.assertIsInstance(ud, collections.UserDict)
        self.assertRaises(TypeError, dict.kutokakeys)

        kundi Exc(Exception): pass

        kundi baddict1(self.type2test):
            eleza __init__(self):
                raise Exc()

        self.assertRaises(Exc, baddict1.kutokakeys, [1])

        kundi BadSeq(object):
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                raise Exc()

        self.assertRaises(Exc, self.type2test.kutokakeys, BadSeq())

        kundi baddict2(self.type2test):
            eleza __setitem__(self, key, value):
                raise Exc()

        self.assertRaises(Exc, baddict2.kutokakeys, [1])

    eleza test_copy(self):
        d = self._full_mapping({1:1, 2:2, 3:3})
        self.assertEqual(d.copy(), {1:1, 2:2, 3:3})
        d = self._empty_mapping()
        self.assertEqual(d.copy(), d)
        self.assertIsInstance(d.copy(), d.__class__)
        self.assertRaises(TypeError, d.copy, None)

    eleza test_get(self):
        BasicTestMappingProtocol.test_get(self)
        d = self._empty_mapping()
        self.assertTrue(d.get('c') is None)
        self.assertEqual(d.get('c', 3), 3)
        d = self._full_mapping({'a' : 1, 'b' : 2})
        self.assertTrue(d.get('c') is None)
        self.assertEqual(d.get('c', 3), 3)
        self.assertEqual(d.get('a'), 1)
        self.assertEqual(d.get('a', 3), 1)

    eleza test_setdefault(self):
        BasicTestMappingProtocol.test_setdefault(self)
        d = self._empty_mapping()
        self.assertTrue(d.setdefault('key0') is None)
        d.setdefault('key0', [])
        self.assertTrue(d.setdefault('key0') is None)
        d.setdefault('key', []).append(3)
        self.assertEqual(d['key'][0], 3)
        d.setdefault('key', []).append(4)
        self.assertEqual(len(d['key']), 2)

    eleza test_popitem(self):
        BasicTestMappingProtocol.test_popitem(self)
        for copymode in -1, +1:
            # -1: b has same structure as a
            # +1: b is a.copy()
            for log2size in range(12):
                size = 2**log2size
                a = self._empty_mapping()
                b = self._empty_mapping()
                for i in range(size):
                    a[repr(i)] = i
                    ikiwa copymode < 0:
                        b[repr(i)] = i
                ikiwa copymode > 0:
                    b = a.copy()
                for i in range(size):
                    ka, va = ta = a.popitem()
                    self.assertEqual(va, int(ka))
                    kb, vb = tb = b.popitem()
                    self.assertEqual(vb, int(kb))
                    self.assertTrue(not(copymode < 0 and ta != tb))
                self.assertTrue(not a)
                self.assertTrue(not b)

    eleza test_pop(self):
        BasicTestMappingProtocol.test_pop(self)

        # Tests for pop with specified key
        d = self._empty_mapping()
        k, v = 'abc', 'def'

        self.assertEqual(d.pop(k, v), v)
        d[k] = v
        self.assertEqual(d.pop(k, 1), v)


kundi TestHashMappingProtocol(TestMappingProtocol):

    eleza test_getitem(self):
        TestMappingProtocol.test_getitem(self)
        kundi Exc(Exception): pass

        kundi BadEq(object):
            eleza __eq__(self, other):
                raise Exc()
            eleza __hash__(self):
                rudisha 24

        d = self._empty_mapping()
        d[BadEq()] = 42
        self.assertRaises(KeyError, d.__getitem__, 23)

        kundi BadHash(object):
            fail = False
            eleza __hash__(self):
                ikiwa self.fail:
                    raise Exc()
                else:
                    rudisha 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.__getitem__, x)

    eleza test_kutokakeys(self):
        TestMappingProtocol.test_kutokakeys(self)
        kundi mydict(self.type2test):
            eleza __new__(cls):
                rudisha collections.UserDict()
        ud = mydict.kutokakeys('ab')
        self.assertEqual(ud, {'a':None, 'b':None})
        self.assertIsInstance(ud, collections.UserDict)

    eleza test_pop(self):
        TestMappingProtocol.test_pop(self)

        kundi Exc(Exception): pass

        kundi BadHash(object):
            fail = False
            eleza __hash__(self):
                ikiwa self.fail:
                    raise Exc()
                else:
                    rudisha 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.pop, x)

    eleza test_mutatingiteration(self):
        d = self._empty_mapping()
        d[1] = 1
        try:
            for i in d:
                d[i+1] = 1
        except RuntimeError:
            pass
        else:
            self.fail("changing dict size during iteration doesn't raise Error")

    eleza test_repr(self):
        d = self._empty_mapping()
        self.assertEqual(repr(d), '{}')
        d[1] = 2
        self.assertEqual(repr(d), '{1: 2}')
        d = self._empty_mapping()
        d[1] = d
        self.assertEqual(repr(d), '{1: {...}}')

        kundi Exc(Exception): pass

        kundi BadRepr(object):
            eleza __repr__(self):
                raise Exc()

        d = self._full_mapping({1: BadRepr()})
        self.assertRaises(Exc, repr, d)

    eleza test_repr_deep(self):
        d = self._empty_mapping()
        for i in range(sys.getrecursionlimit() + 100):
            d0 = d
            d = self._empty_mapping()
            d[1] = d0
        self.assertRaises(RecursionError, repr, d)

    eleza test_eq(self):
        self.assertEqual(self._empty_mapping(), self._empty_mapping())
        self.assertEqual(self._full_mapping({1: 2}),
                         self._full_mapping({1: 2}))

        kundi Exc(Exception): pass

        kundi BadCmp(object):
            eleza __eq__(self, other):
                raise Exc()
            eleza __hash__(self):
                rudisha 1

        d1 = self._full_mapping({BadCmp(): 1})
        d2 = self._full_mapping({1: 1})
        self.assertRaises(Exc, lambda: BadCmp()==1)
        self.assertRaises(Exc, lambda: d1==d2)

    eleza test_setdefault(self):
        TestMappingProtocol.test_setdefault(self)

        kundi Exc(Exception): pass

        kundi BadHash(object):
            fail = False
            eleza __hash__(self):
                ikiwa self.fail:
                    raise Exc()
                else:
                    rudisha 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.setdefault, x, [])
