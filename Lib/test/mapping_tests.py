# tests common to dict na UserDict
agiza unittest
agiza collections
agiza sys


kundi BasicTestMappingProtocol(unittest.TestCase):
    # This base kundi can be used to check that an object conforms to the
    # mapping protocol

    # Functions that can be useful to override to adapt to dictionary
    # semantics
    type2test = Tupu # which kundi ni being tested (overwrite kwenye subclasses)

    eleza _reference(self):
        """Return a dictionary of values which are invariant by storage
        kwenye the object under test."""
        rudisha {"1": "2", "key1":"value1", "key2":(1,2,3)}
    eleza _empty_mapping(self):
        """Return an empty mapping object"""
        rudisha self.type2test()
    eleza _full_mapping(self, data):
        """Return a mapping object ukijumuisha the value contained kwenye data
        dictionary"""
        x = self._empty_mapping()
        kila key, value kwenye data.items():
            x[key] = value
        rudisha x

    eleza __init__(self, *args, **kw):
        unittest.TestCase.__init__(self, *args, **kw)
        self.reference = self._reference().copy()

        # A (key, value) pair sio kwenye the mapping
        key, value = self.reference.popitem()
        self.other = {key:value}

        # A (key, value) pair kwenye the mapping
        key, value = self.reference.popitem()
        self.inmapping = {key:value}
        self.reference[key] = value

    eleza test_read(self):
        # Test kila read only operations on mapping
        p = self._empty_mapping()
        p1 = dict(p) #workaround kila singleton objects
        d = self._full_mapping(self.reference)
        ikiwa d ni p:
            p = p1
        #Indexing
        kila key, value kwenye self.reference.items():
            self.assertEqual(d[key], value)
        knownkey = list(self.other.keys())[0]
        self.assertRaises(KeyError, lambda:d[knownkey])
        #len
        self.assertEqual(len(p), 0)
        self.assertEqual(len(d), len(self.reference))
        #__contains__
        kila k kwenye self.reference:
            self.assertIn(k, d)
        kila k kwenye self.other:
            self.assertNotIn(k, d)
        #cmp
        self.assertEqual(p, p)
        self.assertEqual(d, d)
        self.assertNotEqual(p, d)
        self.assertNotEqual(d, p)
        #bool
        ikiwa p: self.fail("Empty mapping must compare to Uongo")
        ikiwa sio d: self.fail("Full mapping must compare to Kweli")
        # keys(), items(), iterkeys() ...
        eleza check_iterandlist(iter, lst, ref):
            self.assertKweli(hasattr(iter, '__next__'))
            self.assertKweli(hasattr(iter, '__iter__'))
            x = list(iter)
            self.assertKweli(set(x)==set(lst)==set(ref))
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
        # Test kila write operations on mapping
        p = self._empty_mapping()
        #Indexing
        kila key, value kwenye self.reference.items():
            p[key] = value
            self.assertEqual(p[key], value)
        kila key kwenye self.reference.keys():
            toa p[key]
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
        self.assertKweli(not self._empty_mapping())
        self.assertKweli(self.reference)
        self.assertKweli(bool(self._empty_mapping()) ni Uongo)
        self.assertKweli(bool(self.reference) ni Kweli)

    eleza test_keys(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.keys()), [])
        d = self.reference
        self.assertIn(list(self.inmapping.keys())[0], d.keys())
        self.assertNotIn(list(self.other.keys())[0], d.keys())
        self.assertRaises(TypeError, d.keys, Tupu)

    eleza test_values(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.values()), [])

        self.assertRaises(TypeError, d.values, Tupu)

    eleza test_items(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.items()), [])

        self.assertRaises(TypeError, d.items, Tupu)

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

        # FIXME: Doesn't work ukijumuisha UserDict
        # self.assertRaises((TypeError, AttributeError), d.update, Tupu)
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
                 ashiria Exc
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
                         ashiria Exc
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
                         ashiria StopIteration
                rudisha BogonIter()
            eleza __getitem__(self, key):
                 ashiria Exc
        self.assertRaises(Exc, d.update, FailingUserDict())

        d = self._empty_mapping()
        kundi badseq(object):
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                 ashiria Exc()

        self.assertRaises(Exc, d.update, badseq())

        self.assertRaises(ValueError, d.update, [(1, 2, 3)])

    # no test_fromkeys ama test_copy as both os.environ na selves don't support it

    eleza test_get(self):
        d = self._empty_mapping()
        self.assertKweli(d.get(list(self.other.keys())[0]) ni Tupu)
        self.assertEqual(d.get(list(self.other.keys())[0], 3), 3)
        d = self.reference
        self.assertKweli(d.get(list(self.other.keys())[0]) ni Tupu)
        self.assertEqual(d.get(list(self.other.keys())[0], 3), 3)
        self.assertEqual(d.get(list(self.inmapping.keys())[0]),
                         list(self.inmapping.values())[0])
        self.assertEqual(d.get(list(self.inmapping.keys())[0], 3),
                         list(self.inmapping.values())[0])
        self.assertRaises(TypeError, d.get)
        self.assertRaises(TypeError, d.get, Tupu, Tupu, Tupu)

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
        self.assertKweli(self._empty_mapping() ni sio self._empty_mapping())
        self.assertEqual(self.type2test(x=1, y=2), {"x": 1, "y": 2})

    eleza test_bool(self):
        BasicTestMappingProtocol.test_bool(self)
        self.assertKweli(not self._empty_mapping())
        self.assertKweli(self._full_mapping({"x": "y"}))
        self.assertKweli(bool(self._empty_mapping()) ni Uongo)
        self.assertKweli(bool(self._full_mapping({"x": "y"})) ni Kweli)

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
        self.assertKweli(not ('a' kwenye d))
        self.assertKweli('a' sio kwenye d)
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
        toa d['b']
        self.assertEqual(d, {'a': 4, 'c': 3})

        self.assertRaises(TypeError, d.__getitem__)

    eleza test_clear(self):
        d = self._full_mapping({1:1, 2:2, 3:3})
        d.clear()
        self.assertEqual(d, {})

        self.assertRaises(TypeError, d.clear, Tupu)

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

        # Both item sequence na keyword arguments
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

    eleza test_fromkeys(self):
        self.assertEqual(self.type2test.fromkeys('abc'), {'a':Tupu, 'b':Tupu, 'c':Tupu})
        d = self._empty_mapping()
        self.assertKweli(not(d.fromkeys('abc') ni d))
        self.assertEqual(d.fromkeys('abc'), {'a':Tupu, 'b':Tupu, 'c':Tupu})
        self.assertEqual(d.fromkeys((4,5),0), {4:0, 5:0})
        self.assertEqual(d.fromkeys([]), {})
        eleza g():
            tuma 1
        self.assertEqual(d.fromkeys(g()), {1:Tupu})
        self.assertRaises(TypeError, {}.fromkeys, 3)
        kundi dictlike(self.type2test): pass
        self.assertEqual(dictlike.fromkeys('a'), {'a':Tupu})
        self.assertEqual(dictlike().fromkeys('a'), {'a':Tupu})
        self.assertKweli(dictlike.fromkeys('a').__class__ ni dictlike)
        self.assertKweli(dictlike().fromkeys('a').__class__ ni dictlike)
        self.assertKweli(type(dictlike.fromkeys('a')) ni dictlike)
        kundi mydict(self.type2test):
            eleza __new__(cls):
                rudisha collections.UserDict()
        ud = mydict.fromkeys('ab')
        self.assertEqual(ud, {'a':Tupu, 'b':Tupu})
        self.assertIsInstance(ud, collections.UserDict)
        self.assertRaises(TypeError, dict.fromkeys)

        kundi Exc(Exception): pass

        kundi baddict1(self.type2test):
            eleza __init__(self):
                 ashiria Exc()

        self.assertRaises(Exc, baddict1.fromkeys, [1])

        kundi BadSeq(object):
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                 ashiria Exc()

        self.assertRaises(Exc, self.type2test.fromkeys, BadSeq())

        kundi baddict2(self.type2test):
            eleza __setitem__(self, key, value):
                 ashiria Exc()

        self.assertRaises(Exc, baddict2.fromkeys, [1])

    eleza test_copy(self):
        d = self._full_mapping({1:1, 2:2, 3:3})
        self.assertEqual(d.copy(), {1:1, 2:2, 3:3})
        d = self._empty_mapping()
        self.assertEqual(d.copy(), d)
        self.assertIsInstance(d.copy(), d.__class__)
        self.assertRaises(TypeError, d.copy, Tupu)

    eleza test_get(self):
        BasicTestMappingProtocol.test_get(self)
        d = self._empty_mapping()
        self.assertKweli(d.get('c') ni Tupu)
        self.assertEqual(d.get('c', 3), 3)
        d = self._full_mapping({'a' : 1, 'b' : 2})
        self.assertKweli(d.get('c') ni Tupu)
        self.assertEqual(d.get('c', 3), 3)
        self.assertEqual(d.get('a'), 1)
        self.assertEqual(d.get('a', 3), 1)

    eleza test_setdefault(self):
        BasicTestMappingProtocol.test_setdefault(self)
        d = self._empty_mapping()
        self.assertKweli(d.setdefault('key0') ni Tupu)
        d.setdefault('key0', [])
        self.assertKweli(d.setdefault('key0') ni Tupu)
        d.setdefault('key', []).append(3)
        self.assertEqual(d['key'][0], 3)
        d.setdefault('key', []).append(4)
        self.assertEqual(len(d['key']), 2)

    eleza test_popitem(self):
        BasicTestMappingProtocol.test_popitem(self)
        kila copymode kwenye -1, +1:
            # -1: b has same structure as a
            # +1: b ni a.copy()
            kila log2size kwenye range(12):
                size = 2**log2size
                a = self._empty_mapping()
                b = self._empty_mapping()
                kila i kwenye range(size):
                    a[repr(i)] = i
                    ikiwa copymode < 0:
                        b[repr(i)] = i
                ikiwa copymode > 0:
                    b = a.copy()
                kila i kwenye range(size):
                    ka, va = ta = a.popitem()
                    self.assertEqual(va, int(ka))
                    kb, vb = tb = b.popitem()
                    self.assertEqual(vb, int(kb))
                    self.assertKweli(not(copymode < 0 na ta != tb))
                self.assertKweli(not a)
                self.assertKweli(not b)

    eleza test_pop(self):
        BasicTestMappingProtocol.test_pop(self)

        # Tests kila pop ukijumuisha specified key
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
                 ashiria Exc()
            eleza __hash__(self):
                rudisha 24

        d = self._empty_mapping()
        d[BadEq()] = 42
        self.assertRaises(KeyError, d.__getitem__, 23)

        kundi BadHash(object):
            fail = Uongo
            eleza __hash__(self):
                ikiwa self.fail:
                     ashiria Exc()
                isipokua:
                    rudisha 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = Kweli
        self.assertRaises(Exc, d.__getitem__, x)

    eleza test_fromkeys(self):
        TestMappingProtocol.test_fromkeys(self)
        kundi mydict(self.type2test):
            eleza __new__(cls):
                rudisha collections.UserDict()
        ud = mydict.fromkeys('ab')
        self.assertEqual(ud, {'a':Tupu, 'b':Tupu})
        self.assertIsInstance(ud, collections.UserDict)

    eleza test_pop(self):
        TestMappingProtocol.test_pop(self)

        kundi Exc(Exception): pass

        kundi BadHash(object):
            fail = Uongo
            eleza __hash__(self):
                ikiwa self.fail:
                     ashiria Exc()
                isipokua:
                    rudisha 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = Kweli
        self.assertRaises(Exc, d.pop, x)

    eleza test_mutatingiteration(self):
        d = self._empty_mapping()
        d[1] = 1
        jaribu:
            kila i kwenye d:
                d[i+1] = 1
        except RuntimeError:
            pass
        isipokua:
            self.fail("changing dict size during iteration doesn't  ashiria Error")

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
                 ashiria Exc()

        d = self._full_mapping({1: BadRepr()})
        self.assertRaises(Exc, repr, d)

    eleza test_repr_deep(self):
        d = self._empty_mapping()
        kila i kwenye range(sys.getrecursionlimit() + 100):
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
                 ashiria Exc()
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
            fail = Uongo
            eleza __hash__(self):
                ikiwa self.fail:
                     ashiria Exc()
                isipokua:
                    rudisha 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = Kweli
        self.assertRaises(Exc, d.setdefault, x, [])
