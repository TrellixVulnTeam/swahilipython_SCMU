agiza collections
agiza collections.abc
agiza gc
agiza pickle
agiza random
agiza string
agiza sys
agiza unittest
agiza weakref
kutoka test agiza support


kundi DictTest(unittest.TestCase):

    eleza test_invalid_keyword_arguments(self):
        kundi Custom(dict):
            pita
        kila invalid kwenye {1 : 2}, Custom({1 : 2}):
            ukijumuisha self.assertRaises(TypeError):
                dict(**invalid)
            ukijumuisha self.assertRaises(TypeError):
                {}.update(**invalid)

    eleza test_constructor(self):
        # calling built-in types without argument must rudisha empty
        self.assertEqual(dict(), {})
        self.assertIsNot(dict(), {})

    eleza test_literal_constructor(self):
        # check literal constructor kila different sized dicts
        # (to exercise the BUILD_MAP oparg).
        kila n kwenye (0, 1, 6, 256, 400):
            items = [(''.join(random.sample(string.ascii_letters, 8)), i)
                     kila i kwenye range(n)]
            random.shuffle(items)
            formatted_items = ('{!r}: {:d}'.format(k, v) kila k, v kwenye items)
            dictliteral = '{' + ', '.join(formatted_items) + '}'
            self.assertEqual(eval(dictliteral), dict(items))

    eleza test_bool(self):
        self.assertIs(sio {}, Kweli)
        self.assertKweli({1: 2})
        self.assertIs(bool({}), Uongo)
        self.assertIs(bool({1: 2}), Kweli)

    eleza test_keys(self):
        d = {}
        self.assertEqual(set(d.keys()), set())
        d = {'a': 1, 'b': 2}
        k = d.keys()
        self.assertEqual(set(k), {'a', 'b'})
        self.assertIn('a', k)
        self.assertIn('b', k)
        self.assertIn('a', d)
        self.assertIn('b', d)
        self.assertRaises(TypeError, d.keys, Tupu)
        self.assertEqual(repr(dict(a=1).keys()), "dict_keys(['a'])")

    eleza test_values(self):
        d = {}
        self.assertEqual(set(d.values()), set())
        d = {1:2}
        self.assertEqual(set(d.values()), {2})
        self.assertRaises(TypeError, d.values, Tupu)
        self.assertEqual(repr(dict(a=1).values()), "dict_values([1])")

    eleza test_items(self):
        d = {}
        self.assertEqual(set(d.items()), set())

        d = {1:2}
        self.assertEqual(set(d.items()), {(1, 2)})
        self.assertRaises(TypeError, d.items, Tupu)
        self.assertEqual(repr(dict(a=1).items()), "dict_items([('a', 1)])")

    eleza test_contains(self):
        d = {}
        self.assertNotIn('a', d)
        self.assertUongo('a' kwenye d)
        self.assertKweli('a' haiko kwenye d)
        d = {'a': 1, 'b': 2}
        self.assertIn('a', d)
        self.assertIn('b', d)
        self.assertNotIn('c', d)

        self.assertRaises(TypeError, d.__contains__)

    eleza test_len(self):
        d = {}
        self.assertEqual(len(d), 0)
        d = {'a': 1, 'b': 2}
        self.assertEqual(len(d), 2)

    eleza test_getitem(self):
        d = {'a': 1, 'b': 2}
        self.assertEqual(d['a'], 1)
        self.assertEqual(d['b'], 2)
        d['c'] = 3
        d['a'] = 4
        self.assertEqual(d['c'], 3)
        self.assertEqual(d['a'], 4)
        toa d['b']
        self.assertEqual(d, {'a': 4, 'c': 3})

        self.assertRaises(TypeError, d.__getitem__)

        kundi BadEq(object):
            eleza __eq__(self, other):
                ashiria Exc()
            eleza __hash__(self):
                rudisha 24

        d = {}
        d[BadEq()] = 42
        self.assertRaises(KeyError, d.__getitem__, 23)

        kundi Exc(Exception): pita

        kundi BadHash(object):
            fail = Uongo
            eleza __hash__(self):
                ikiwa self.fail:
                    ashiria Exc()
                isipokua:
                    rudisha 42

        x = BadHash()
        d[x] = 42
        x.fail = Kweli
        self.assertRaises(Exc, d.__getitem__, x)

    eleza test_clear(self):
        d = {1:1, 2:2, 3:3}
        d.clear()
        self.assertEqual(d, {})

        self.assertRaises(TypeError, d.clear, Tupu)

    eleza test_update(self):
        d = {}
        d.update({1:100})
        d.update({2:20})
        d.update({1:1, 2:2, 3:3})
        self.assertEqual(d, {1:1, 2:2, 3:3})

        d.update()
        self.assertEqual(d, {1:1, 2:2, 3:3})

        self.assertRaises((TypeError, AttributeError), d.update, Tupu)

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

        kundi Exc(Exception): pita

        d.clear()
        kundi FailingUserDict:
            eleza keys(self):
                ashiria Exc
        self.assertRaises(Exc, d.update, FailingUserDict())

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

        kundi badseq(object):
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                ashiria Exc()

        self.assertRaises(Exc, {}.update, badseq())

        self.assertRaises(ValueError, {}.update, [(1, 2, 3)])

    eleza test_kutokakeys(self):
        self.assertEqual(dict.kutokakeys('abc'), {'a':Tupu, 'b':Tupu, 'c':Tupu})
        d = {}
        self.assertIsNot(d.kutokakeys('abc'), d)
        self.assertEqual(d.kutokakeys('abc'), {'a':Tupu, 'b':Tupu, 'c':Tupu})
        self.assertEqual(d.kutokakeys((4,5),0), {4:0, 5:0})
        self.assertEqual(d.kutokakeys([]), {})
        eleza g():
            tuma 1
        self.assertEqual(d.kutokakeys(g()), {1:Tupu})
        self.assertRaises(TypeError, {}.kutokakeys, 3)
        kundi dictlike(dict): pita
        self.assertEqual(dictlike.kutokakeys('a'), {'a':Tupu})
        self.assertEqual(dictlike().kutokakeys('a'), {'a':Tupu})
        self.assertIsInstance(dictlike.kutokakeys('a'), dictlike)
        self.assertIsInstance(dictlike().kutokakeys('a'), dictlike)
        kundi mydict(dict):
            eleza __new__(cls):
                rudisha collections.UserDict()
        ud = mydict.kutokakeys('ab')
        self.assertEqual(ud, {'a':Tupu, 'b':Tupu})
        self.assertIsInstance(ud, collections.UserDict)
        self.assertRaises(TypeError, dict.kutokakeys)

        kundi Exc(Exception): pita

        kundi baddict1(dict):
            eleza __init__(self):
                ashiria Exc()

        self.assertRaises(Exc, baddict1.kutokakeys, [1])

        kundi BadSeq(object):
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                ashiria Exc()

        self.assertRaises(Exc, dict.kutokakeys, BadSeq())

        kundi baddict2(dict):
            eleza __setitem__(self, key, value):
                ashiria Exc()

        self.assertRaises(Exc, baddict2.kutokakeys, [1])

        # test fast path kila dictionary inputs
        d = dict(zip(range(6), range(6)))
        self.assertEqual(dict.kutokakeys(d, 0), dict(zip(range(6), [0]*6)))

        kundi baddict3(dict):
            eleza __new__(cls):
                rudisha d
        d = {i : i kila i kwenye range(10)}
        res = d.copy()
        res.update(a=Tupu, b=Tupu, c=Tupu)
        self.assertEqual(baddict3.kutokakeys({"a", "b", "c"}), res)

    eleza test_copy(self):
        d = {1: 1, 2: 2, 3: 3}
        self.assertIsNot(d.copy(), d)
        self.assertEqual(d.copy(), d)
        self.assertEqual(d.copy(), {1: 1, 2: 2, 3: 3})

        copy = d.copy()
        d[4] = 4
        self.assertNotEqual(copy, d)

        self.assertEqual({}.copy(), {})
        self.assertRaises(TypeError, d.copy, Tupu)

    eleza test_copy_fuzz(self):
        kila dict_size kwenye [10, 100, 1000, 10000, 100000]:
            dict_size = random.randrange(
                dict_size // 2, dict_size + dict_size // 2)
            ukijumuisha self.subTest(dict_size=dict_size):
                d = {}
                kila i kwenye range(dict_size):
                    d[i] = i

                d2 = d.copy()
                self.assertIsNot(d2, d)
                self.assertEqual(d, d2)
                d2['key'] = 'value'
                self.assertNotEqual(d, d2)
                self.assertEqual(len(d2), len(d) + 1)

    eleza test_copy_maintains_tracking(self):
        kundi A:
            pita

        key = A()

        kila d kwenye ({}, {'a': 1}, {key: 'val'}):
            d2 = d.copy()
            self.assertEqual(gc.is_tracked(d), gc.is_tracked(d2))

    eleza test_copy_noncompact(self):
        # Dicts don't compact themselves on del/pop operations.
        # Copy will use a slow merging strategy that produces
        # a compacted copy when roughly 33% of dict ni a non-used
        # keys-space (to optimize memory footprint).
        # In this test we want to hit the slow/compacting
        # branch of dict.copy() na make sure it works OK.
        d = {k: k kila k kwenye range(1000)}
        kila k kwenye range(950):
            toa d[k]
        d2 = d.copy()
        self.assertEqual(d2, d)

    eleza test_get(self):
        d = {}
        self.assertIs(d.get('c'), Tupu)
        self.assertEqual(d.get('c', 3), 3)
        d = {'a': 1, 'b': 2}
        self.assertIs(d.get('c'), Tupu)
        self.assertEqual(d.get('c', 3), 3)
        self.assertEqual(d.get('a'), 1)
        self.assertEqual(d.get('a', 3), 1)
        self.assertRaises(TypeError, d.get)
        self.assertRaises(TypeError, d.get, Tupu, Tupu, Tupu)

    eleza test_setdefault(self):
        # dict.setdefault()
        d = {}
        self.assertIs(d.setdefault('key0'), Tupu)
        d.setdefault('key0', [])
        self.assertIs(d.setdefault('key0'), Tupu)
        d.setdefault('key', []).append(3)
        self.assertEqual(d['key'][0], 3)
        d.setdefault('key', []).append(4)
        self.assertEqual(len(d['key']), 2)
        self.assertRaises(TypeError, d.setdefault)

        kundi Exc(Exception): pita

        kundi BadHash(object):
            fail = Uongo
            eleza __hash__(self):
                ikiwa self.fail:
                    ashiria Exc()
                isipokua:
                    rudisha 42

        x = BadHash()
        d[x] = 42
        x.fail = Kweli
        self.assertRaises(Exc, d.setdefault, x, [])

    eleza test_setdefault_atomic(self):
        # Issue #13521: setdefault() calls __hash__ na __eq__ only once.
        kundi Hashed(object):
            eleza __init__(self):
                self.hash_count = 0
                self.eq_count = 0
            eleza __hash__(self):
                self.hash_count += 1
                rudisha 42
            eleza __eq__(self, other):
                self.eq_count += 1
                rudisha id(self) == id(other)
        hashed1 = Hashed()
        y = {hashed1: 5}
        hashed2 = Hashed()
        y.setdefault(hashed2, [])
        self.assertEqual(hashed1.hash_count, 1)
        self.assertEqual(hashed2.hash_count, 1)
        self.assertEqual(hashed1.eq_count + hashed2.eq_count, 1)

    eleza test_setitem_atomic_at_resize(self):
        kundi Hashed(object):
            eleza __init__(self):
                self.hash_count = 0
                self.eq_count = 0
            eleza __hash__(self):
                self.hash_count += 1
                rudisha 42
            eleza __eq__(self, other):
                self.eq_count += 1
                rudisha id(self) == id(other)
        hashed1 = Hashed()
        # 5 items
        y = {hashed1: 5, 0: 0, 1: 1, 2: 2, 3: 3}
        hashed2 = Hashed()
        # 6th item forces a resize
        y[hashed2] = []
        self.assertEqual(hashed1.hash_count, 1)
        self.assertEqual(hashed2.hash_count, 1)
        self.assertEqual(hashed1.eq_count + hashed2.eq_count, 1)

    eleza test_popitem(self):
        # dict.popitem()
        kila copymode kwenye -1, +1:
            # -1: b has same structure kama a
            # +1: b ni a.copy()
            kila log2size kwenye range(12):
                size = 2**log2size
                a = {}
                b = {}
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
                    self.assertUongo(copymode < 0 na ta != tb)
                self.assertUongo(a)
                self.assertUongo(b)

        d = {}
        self.assertRaises(KeyError, d.popitem)

    eleza test_pop(self):
        # Tests kila pop ukijumuisha specified key
        d = {}
        k, v = 'abc', 'def'
        d[k] = v
        self.assertRaises(KeyError, d.pop, 'ghi')

        self.assertEqual(d.pop(k), v)
        self.assertEqual(len(d), 0)

        self.assertRaises(KeyError, d.pop, k)

        self.assertEqual(d.pop(k, v), v)
        d[k] = v
        self.assertEqual(d.pop(k, 1), v)

        self.assertRaises(TypeError, d.pop)

        kundi Exc(Exception): pita

        kundi BadHash(object):
            fail = Uongo
            eleza __hash__(self):
                ikiwa self.fail:
                    ashiria Exc()
                isipokua:
                    rudisha 42

        x = BadHash()
        d[x] = 42
        x.fail = Kweli
        self.assertRaises(Exc, d.pop, x)

    eleza test_mutating_iteration(self):
        # changing dict size during iteration
        d = {}
        d[1] = 1
        ukijumuisha self.assertRaises(RuntimeError):
            kila i kwenye d:
                d[i+1] = 1

    eleza test_mutating_iteration_delete(self):
        # change dict content during iteration
        d = {}
        d[0] = 0
        ukijumuisha self.assertRaises(RuntimeError):
            kila i kwenye d:
                toa d[0]
                d[0] = 0

    eleza test_mutating_iteration_delete_over_values(self):
        # change dict content during iteration
        d = {}
        d[0] = 0
        ukijumuisha self.assertRaises(RuntimeError):
            kila i kwenye d.values():
                toa d[0]
                d[0] = 0

    eleza test_mutating_iteration_delete_over_items(self):
        # change dict content during iteration
        d = {}
        d[0] = 0
        ukijumuisha self.assertRaises(RuntimeError):
            kila i kwenye d.items():
                toa d[0]
                d[0] = 0

    eleza test_mutating_lookup(self):
        # changing dict during a lookup (issue #14417)
        kundi NastyKey:
            mutate_dict = Tupu

            eleza __init__(self, value):
                self.value = value

            eleza __hash__(self):
                # hash collision!
                rudisha 1

            eleza __eq__(self, other):
                ikiwa NastyKey.mutate_dict:
                    mydict, key = NastyKey.mutate_dict
                    NastyKey.mutate_dict = Tupu
                    toa mydict[key]
                rudisha self.value == other.value

        key1 = NastyKey(1)
        key2 = NastyKey(2)
        d = {key1: 1}
        NastyKey.mutate_dict = (d, key1)
        d[key2] = 2
        self.assertEqual(d, {key2: 2})

    eleza test_repr(self):
        d = {}
        self.assertEqual(repr(d), '{}')
        d[1] = 2
        self.assertEqual(repr(d), '{1: 2}')
        d = {}
        d[1] = d
        self.assertEqual(repr(d), '{1: {...}}')

        kundi Exc(Exception): pita

        kundi BadRepr(object):
            eleza __repr__(self):
                ashiria Exc()

        d = {1: BadRepr()}
        self.assertRaises(Exc, repr, d)

    eleza test_repr_deep(self):
        d = {}
        kila i kwenye range(sys.getrecursionlimit() + 100):
            d = {1: d}
        self.assertRaises(RecursionError, repr, d)

    eleza test_eq(self):
        self.assertEqual({}, {})
        self.assertEqual({1: 2}, {1: 2})

        kundi Exc(Exception): pita

        kundi BadCmp(object):
            eleza __eq__(self, other):
                ashiria Exc()
            eleza __hash__(self):
                rudisha 1

        d1 = {BadCmp(): 1}
        d2 = {1: 1}

        ukijumuisha self.assertRaises(Exc):
            d1 == d2

    eleza test_keys_contained(self):
        self.helper_keys_contained(lambda x: x.keys())
        self.helper_keys_contained(lambda x: x.items())

    eleza helper_keys_contained(self, fn):
        # Test rich comparisons against dict key views, which should behave the
        # same kama sets.
        empty = fn(dict())
        empty2 = fn(dict())
        smaller = fn({1:1, 2:2})
        larger = fn({1:1, 2:2, 3:3})
        larger2 = fn({1:1, 2:2, 3:3})
        larger3 = fn({4:1, 2:2, 3:3})

        self.assertKweli(smaller <  larger)
        self.assertKweli(smaller <= larger)
        self.assertKweli(larger >  smaller)
        self.assertKweli(larger >= smaller)

        self.assertUongo(smaller >= larger)
        self.assertUongo(smaller >  larger)
        self.assertUongo(larger  <= smaller)
        self.assertUongo(larger  <  smaller)

        self.assertUongo(smaller <  larger3)
        self.assertUongo(smaller <= larger3)
        self.assertUongo(larger3 >  smaller)
        self.assertUongo(larger3 >= smaller)

        # Inequality strictness
        self.assertKweli(larger2 >= larger)
        self.assertKweli(larger2 <= larger)
        self.assertUongo(larger2 > larger)
        self.assertUongo(larger2 < larger)

        self.assertKweli(larger == larger2)
        self.assertKweli(smaller != larger)

        # There ni an optimization on the zero-element case.
        self.assertKweli(empty == empty2)
        self.assertUongo(empty != empty2)
        self.assertUongo(empty == smaller)
        self.assertKweli(empty != smaller)

        # With the same size, an elementwise compare happens
        self.assertKweli(larger != larger3)
        self.assertUongo(larger == larger3)

    eleza test_errors_in_view_containment_check(self):
        kundi C:
            eleza __eq__(self, other):
                ashiria RuntimeError

        d1 = {1: C()}
        d2 = {1: C()}
        ukijumuisha self.assertRaises(RuntimeError):
            d1.items() == d2.items()
        ukijumuisha self.assertRaises(RuntimeError):
            d1.items() != d2.items()
        ukijumuisha self.assertRaises(RuntimeError):
            d1.items() <= d2.items()
        ukijumuisha self.assertRaises(RuntimeError):
            d1.items() >= d2.items()

        d3 = {1: C(), 2: C()}
        ukijumuisha self.assertRaises(RuntimeError):
            d2.items() < d3.items()
        ukijumuisha self.assertRaises(RuntimeError):
            d3.items() > d2.items()

    eleza test_dictview_set_operations_on_keys(self):
        k1 = {1:1, 2:2}.keys()
        k2 = {1:1, 2:2, 3:3}.keys()
        k3 = {4:4}.keys()

        self.assertEqual(k1 - k2, set())
        self.assertEqual(k1 - k3, {1,2})
        self.assertEqual(k2 - k1, {3})
        self.assertEqual(k3 - k1, {4})
        self.assertEqual(k1 & k2, {1,2})
        self.assertEqual(k1 & k3, set())
        self.assertEqual(k1 | k2, {1,2,3})
        self.assertEqual(k1 ^ k2, {3})
        self.assertEqual(k1 ^ k3, {1,2,4})

    eleza test_dictview_set_operations_on_items(self):
        k1 = {1:1, 2:2}.items()
        k2 = {1:1, 2:2, 3:3}.items()
        k3 = {4:4}.items()

        self.assertEqual(k1 - k2, set())
        self.assertEqual(k1 - k3, {(1,1), (2,2)})
        self.assertEqual(k2 - k1, {(3,3)})
        self.assertEqual(k3 - k1, {(4,4)})
        self.assertEqual(k1 & k2, {(1,1), (2,2)})
        self.assertEqual(k1 & k3, set())
        self.assertEqual(k1 | k2, {(1,1), (2,2), (3,3)})
        self.assertEqual(k1 ^ k2, {(3,3)})
        self.assertEqual(k1 ^ k3, {(1,1), (2,2), (4,4)})

    eleza test_dictview_mixed_set_operations(self):
        # Just a few kila .keys()
        self.assertKweli({1:1}.keys() == {1})
        self.assertKweli({1} == {1:1}.keys())
        self.assertEqual({1:1}.keys() | {2}, {1, 2})
        self.assertEqual({2} | {1:1}.keys(), {1, 2})
        # And a few kila .items()
        self.assertKweli({1:1}.items() == {(1,1)})
        self.assertKweli({(1,1)} == {1:1}.items())
        self.assertEqual({1:1}.items() | {2}, {(1,1), 2})
        self.assertEqual({2} | {1:1}.items(), {(1,1), 2})

    eleza test_missing(self):
        # Make sure dict doesn't have a __missing__ method
        self.assertUongo(hasattr(dict, "__missing__"))
        self.assertUongo(hasattr({}, "__missing__"))
        # Test several cases:
        # (D) subkundi defines __missing__ method rudishaing a value
        # (E) subkundi defines __missing__ method raising RuntimeError
        # (F) subkundi sets __missing__ instance variable (no effect)
        # (G) subkundi doesn't define __missing__ at all
        kundi D(dict):
            eleza __missing__(self, key):
                rudisha 42
        d = D({1: 2, 3: 4})
        self.assertEqual(d[1], 2)
        self.assertEqual(d[3], 4)
        self.assertNotIn(2, d)
        self.assertNotIn(2, d.keys())
        self.assertEqual(d[2], 42)

        kundi E(dict):
            eleza __missing__(self, key):
                ashiria RuntimeError(key)
        e = E()
        ukijumuisha self.assertRaises(RuntimeError) kama c:
            e[42]
        self.assertEqual(c.exception.args, (42,))

        kundi F(dict):
            eleza __init__(self):
                # An instance variable __missing__ should have no effect
                self.__missing__ = lambda key: Tupu
        f = F()
        ukijumuisha self.assertRaises(KeyError) kama c:
            f[42]
        self.assertEqual(c.exception.args, (42,))

        kundi G(dict):
            pita
        g = G()
        ukijumuisha self.assertRaises(KeyError) kama c:
            g[42]
        self.assertEqual(c.exception.args, (42,))

    eleza test_tuple_keyerror(self):
        # SF #1576657
        d = {}
        ukijumuisha self.assertRaises(KeyError) kama c:
            d[(1,)]
        self.assertEqual(c.exception.args, ((1,),))

    eleza test_bad_key(self):
        # Dictionary lookups should fail ikiwa __eq__() ashirias an exception.
        kundi CustomException(Exception):
            pita

        kundi BadDictKey:
            eleza __hash__(self):
                rudisha hash(self.__class__)

            eleza __eq__(self, other):
                ikiwa isinstance(other, self.__class__):
                    ashiria CustomException
                rudisha other

        d = {}
        x1 = BadDictKey()
        x2 = BadDictKey()
        d[x1] = 1
        kila stmt kwenye ['d[x2] = 2',
                     'z = d[x2]',
                     'x2 kwenye d',
                     'd.get(x2)',
                     'd.setdefault(x2, 42)',
                     'd.pop(x2)',
                     'd.update({x2: 2})']:
            ukijumuisha self.assertRaises(CustomException):
                exec(stmt, locals())

    eleza test_resize1(self):
        # Dict resizing bug, found by Jack Jansen kwenye 2.2 CVS development.
        # This version got an assert failure kwenye debug build, infinite loop in
        # release build.  Unfortunately, provoking this kind of stuff requires
        # a mix of inserts na deletes hitting exactly the right hash codes in
        # exactly the right order, na I can't think of a randomized approach
        # that would be *likely* to hit a failing case kwenye reasonable time.

        d = {}
        kila i kwenye range(5):
            d[i] = i
        kila i kwenye range(5):
            toa d[i]
        kila i kwenye range(5, 9):  # i==8 was the problem
            d[i] = i

    eleza test_resize2(self):
        # Another dict resizing bug (SF bug #1456209).
        # This caused Segmentation faults ama Illegal instructions.

        kundi X(object):
            eleza __hash__(self):
                rudisha 5
            eleza __eq__(self, other):
                ikiwa resizing:
                    d.clear()
                rudisha Uongo
        d = {}
        resizing = Uongo
        d[X()] = 1
        d[X()] = 2
        d[X()] = 3
        d[X()] = 4
        d[X()] = 5
        # now trigger a resize
        resizing = Kweli
        d[9] = 6

    eleza test_empty_presized_dict_in_freelist(self):
        # Bug #3537: ikiwa an empty but presized dict ukijumuisha a size larger
        # than 7 was kwenye the freelist, it triggered an assertion failure
        ukijumuisha self.assertRaises(ZeroDivisionError):
            d = {'a': 1 // 0, 'b': Tupu, 'c': Tupu, 'd': Tupu, 'e': Tupu,
                 'f': Tupu, 'g': Tupu, 'h': Tupu}
        d = {}

    eleza test_container_iterator(self):
        # Bug #3680: tp_traverse was sio implemented kila dictiter na
        # dictview objects.
        kundi C(object):
            pita
        views = (dict.items, dict.values, dict.keys)
        kila v kwenye views:
            obj = C()
            ref = weakref.ref(obj)
            container = {obj: 1}
            obj.v = v(container)
            obj.x = iter(obj.v)
            toa obj, container
            gc.collect()
            self.assertIs(ref(), Tupu, "Cycle was sio collected")

    eleza _not_tracked(self, t):
        # Nested containers can take several collections to untrack
        gc.collect()
        gc.collect()
        self.assertUongo(gc.is_tracked(t), t)

    eleza _tracked(self, t):
        self.assertKweli(gc.is_tracked(t), t)
        gc.collect()
        gc.collect()
        self.assertKweli(gc.is_tracked(t), t)

    @support.cpython_only
    eleza test_track_literals(self):
        # Test GC-optimization of dict literals
        x, y, z, w = 1.5, "a", (1, Tupu), []

        self._not_tracked({})
        self._not_tracked({x:(), y:x, z:1})
        self._not_tracked({1: "a", "b": 2})
        self._not_tracked({1: 2, (Tupu, Kweli, Uongo, ()): int})
        self._not_tracked({1: object()})

        # Dicts ukijumuisha mutable elements are always tracked, even ikiwa those
        # elements are sio tracked right now.
        self._tracked({1: []})
        self._tracked({1: ([],)})
        self._tracked({1: {}})
        self._tracked({1: set()})

    @support.cpython_only
    eleza test_track_dynamic(self):
        # Test GC-optimization of dynamically-created dicts
        kundi MyObject(object):
            pita
        x, y, z, w, o = 1.5, "a", (1, object()), [], MyObject()

        d = dict()
        self._not_tracked(d)
        d[1] = "a"
        self._not_tracked(d)
        d[y] = 2
        self._not_tracked(d)
        d[z] = 3
        self._not_tracked(d)
        self._not_tracked(d.copy())
        d[4] = w
        self._tracked(d)
        self._tracked(d.copy())
        d[4] = Tupu
        self._not_tracked(d)
        self._not_tracked(d.copy())

        # dd isn't tracked right now, but it may mutate na therefore d
        # which contains it must be tracked.
        d = dict()
        dd = dict()
        d[1] = dd
        self._not_tracked(dd)
        self._tracked(d)
        dd[1] = d
        self._tracked(dd)

        d = dict.kutokakeys([x, y, z])
        self._not_tracked(d)
        dd = dict()
        dd.update(d)
        self._not_tracked(dd)
        d = dict.kutokakeys([x, y, z, o])
        self._tracked(d)
        dd = dict()
        dd.update(d)
        self._tracked(dd)

        d = dict(x=x, y=y, z=z)
        self._not_tracked(d)
        d = dict(x=x, y=y, z=z, w=w)
        self._tracked(d)
        d = dict()
        d.update(x=x, y=y, z=z)
        self._not_tracked(d)
        d.update(w=w)
        self._tracked(d)

        d = dict([(x, y), (z, 1)])
        self._not_tracked(d)
        d = dict([(x, y), (z, w)])
        self._tracked(d)
        d = dict()
        d.update([(x, y), (z, 1)])
        self._not_tracked(d)
        d.update([(x, y), (z, w)])
        self._tracked(d)

    @support.cpython_only
    eleza test_track_subtypes(self):
        # Dict subtypes are always tracked
        kundi MyDict(dict):
            pita
        self._tracked(MyDict())

    eleza make_shared_key_dict(self, n):
        kundi C:
            pita

        dicts = []
        kila i kwenye range(n):
            a = C()
            a.x, a.y, a.z = 1, 2, 3
            dicts.append(a.__dict__)

        rudisha dicts

    @support.cpython_only
    eleza test_splittable_setdefault(self):
        """split table must be combined when setdefault()
        komas insertion order"""
        a, b = self.make_shared_key_dict(2)

        a['a'] = 1
        size_a = sys.getsizeof(a)
        a['b'] = 2
        b.setdefault('b', 2)
        size_b = sys.getsizeof(b)
        b['a'] = 1

        self.assertGreater(size_b, size_a)
        self.assertEqual(list(a), ['x', 'y', 'z', 'a', 'b'])
        self.assertEqual(list(b), ['x', 'y', 'z', 'b', 'a'])

    @support.cpython_only
    eleza test_splittable_del(self):
        """split table must be combined when toa d[k]"""
        a, b = self.make_shared_key_dict(2)

        orig_size = sys.getsizeof(a)

        toa a['y']  # split table ni combined
        ukijumuisha self.assertRaises(KeyError):
            toa a['y']

        self.assertGreater(sys.getsizeof(a), orig_size)
        self.assertEqual(list(a), ['x', 'z'])
        self.assertEqual(list(b), ['x', 'y', 'z'])

        # Two dicts have different insertion order.
        a['y'] = 42
        self.assertEqual(list(a), ['x', 'z', 'y'])
        self.assertEqual(list(b), ['x', 'y', 'z'])

    @support.cpython_only
    eleza test_splittable_pop(self):
        """split table must be combined when d.pop(k)"""
        a, b = self.make_shared_key_dict(2)

        orig_size = sys.getsizeof(a)

        a.pop('y')  # split table ni combined
        ukijumuisha self.assertRaises(KeyError):
            a.pop('y')

        self.assertGreater(sys.getsizeof(a), orig_size)
        self.assertEqual(list(a), ['x', 'z'])
        self.assertEqual(list(b), ['x', 'y', 'z'])

        # Two dicts have different insertion order.
        a['y'] = 42
        self.assertEqual(list(a), ['x', 'z', 'y'])
        self.assertEqual(list(b), ['x', 'y', 'z'])

    @support.cpython_only
    eleza test_splittable_pop_pending(self):
        """pop a pending key kwenye a splitted table should sio crash"""
        a, b = self.make_shared_key_dict(2)

        a['a'] = 4
        ukijumuisha self.assertRaises(KeyError):
            b.pop('a')

    @support.cpython_only
    eleza test_splittable_popitem(self):
        """split table must be combined when d.popitem()"""
        a, b = self.make_shared_key_dict(2)

        orig_size = sys.getsizeof(a)

        item = a.popitem()  # split table ni combined
        self.assertEqual(item, ('z', 3))
        ukijumuisha self.assertRaises(KeyError):
            toa a['z']

        self.assertGreater(sys.getsizeof(a), orig_size)
        self.assertEqual(list(a), ['x', 'y'])
        self.assertEqual(list(b), ['x', 'y', 'z'])

    @support.cpython_only
    eleza test_splittable_setattr_after_pop(self):
        """setattr() must sio convert combined table into split table."""
        # Issue 28147
        agiza _testcapi

        kundi C:
            pita
        a = C()

        a.a = 1
        self.assertKweli(_testcapi.dict_hassplittable(a.__dict__))

        # dict.pop() convert it to combined table
        a.__dict__.pop('a')
        self.assertUongo(_testcapi.dict_hassplittable(a.__dict__))

        # But C should sio convert a.__dict__ to split table again.
        a.a = 1
        self.assertUongo(_testcapi.dict_hassplittable(a.__dict__))

        # Same kila popitem()
        a = C()
        a.a = 2
        self.assertKweli(_testcapi.dict_hassplittable(a.__dict__))
        a.__dict__.popitem()
        self.assertUongo(_testcapi.dict_hassplittable(a.__dict__))
        a.a = 3
        self.assertUongo(_testcapi.dict_hassplittable(a.__dict__))

    eleza test_iterator_pickling(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            data = {1:"a", 2:"b", 3:"c"}
            it = iter(data)
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            self.assertEqual(list(it), list(data))

            it = pickle.loads(d)
            jaribu:
                drop = next(it)
            tatizo StopIteration:
                endelea
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            toa data[drop]
            self.assertEqual(list(it), list(data))

    eleza test_itemiterator_pickling(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            data = {1:"a", 2:"b", 3:"c"}
            # dictviews aren't picklable, only their iterators
            itorg = iter(data.items())
            d = pickle.dumps(itorg, proto)
            it = pickle.loads(d)
            # note that the type of the unpickled iterator
            # ni sio necessarily the same kama the original.  It is
            # merely an object supporting the iterator protocol, tumaing
            # the same objects kama the original one.
            # self.assertEqual(type(itorg), type(it))
            self.assertIsInstance(it, collections.abc.Iterator)
            self.assertEqual(dict(it), data)

            it = pickle.loads(d)
            drop = next(it)
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            toa data[drop[0]]
            self.assertEqual(dict(it), data)

    eleza test_valuesiterator_pickling(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            data = {1:"a", 2:"b", 3:"c"}
            # data.values() isn't picklable, only its iterator
            it = iter(data.values())
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            self.assertEqual(list(it), list(data.values()))

            it = pickle.loads(d)
            drop = next(it)
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            values = list(it) + [drop]
            self.assertEqual(sorted(values), sorted(list(data.values())))

    eleza test_reverseiterator_pickling(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            data = {1:"a", 2:"b", 3:"c"}
            it = reversed(data)
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            self.assertEqual(list(it), list(reversed(data)))

            it = pickle.loads(d)
            jaribu:
                drop = next(it)
            tatizo StopIteration:
                endelea
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            toa data[drop]
            self.assertEqual(list(it), list(reversed(data)))

    eleza test_reverseitemiterator_pickling(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            data = {1:"a", 2:"b", 3:"c"}
            # dictviews aren't picklable, only their iterators
            itorg = reversed(data.items())
            d = pickle.dumps(itorg, proto)
            it = pickle.loads(d)
            # note that the type of the unpickled iterator
            # ni sio necessarily the same kama the original.  It is
            # merely an object supporting the iterator protocol, tumaing
            # the same objects kama the original one.
            # self.assertEqual(type(itorg), type(it))
            self.assertIsInstance(it, collections.abc.Iterator)
            self.assertEqual(dict(it), data)

            it = pickle.loads(d)
            drop = next(it)
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            toa data[drop[0]]
            self.assertEqual(dict(it), data)

    eleza test_reversevaluesiterator_pickling(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            data = {1:"a", 2:"b", 3:"c"}
            # data.values() isn't picklable, only its iterator
            it = reversed(data.values())
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            self.assertEqual(list(it), list(reversed(data.values())))

            it = pickle.loads(d)
            drop = next(it)
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            values = list(it) + [drop]
            self.assertEqual(sorted(values), sorted(data.values()))

    eleza test_instance_dict_getattr_str_subclass(self):
        kundi Foo:
            eleza __init__(self, msg):
                self.msg = msg
        f = Foo('123')
        kundi _str(str):
            pita
        self.assertEqual(f.msg, getattr(f, _str('msg')))
        self.assertEqual(f.msg, f.__dict__[_str('msg')])

    eleza test_object_set_item_single_instance_non_str_key(self):
        kundi Foo: pita
        f = Foo()
        f.__dict__[1] = 1
        f.a = 'a'
        self.assertEqual(f.__dict__, {1:1, 'a':'a'})

    eleza check_reentrant_insertion(self, mutate):
        # This object will trigger mutation of the dict when replaced
        # by another value.  Note this relies on refcounting: the test
        # won't achieve its purpose on fully-GCed Python implementations.
        kundi Mutating:
            eleza __del__(self):
                mutate(d)

        d = {k: Mutating() kila k kwenye 'abcdefghijklmnopqr'}
        kila k kwenye list(d):
            d[k] = k

    eleza test_reentrant_insertion(self):
        # Reentrant insertion shouldn't crash (see issue #22653)
        eleza mutate(d):
            d['b'] = 5
        self.check_reentrant_insertion(mutate)

        eleza mutate(d):
            d.update(self.__dict__)
            d.clear()
        self.check_reentrant_insertion(mutate)

        eleza mutate(d):
            wakati d:
                d.popitem()
        self.check_reentrant_insertion(mutate)

    eleza test_merge_and_mutate(self):
        kundi X:
            eleza __hash__(self):
                rudisha 0

            eleza __eq__(self, o):
                other.clear()
                rudisha Uongo

        l = [(i,0) kila i kwenye range(1, 1337)]
        other = dict(l)
        other[X()] = 0
        d = {X(): 0, 1: 1}
        self.assertRaises(RuntimeError, d.update, other)

    eleza test_free_after_iterating(self):
        support.check_free_after_iterating(self, iter, dict)
        support.check_free_after_iterating(self, lambda d: iter(d.keys()), dict)
        support.check_free_after_iterating(self, lambda d: iter(d.values()), dict)
        support.check_free_after_iterating(self, lambda d: iter(d.items()), dict)

    eleza test_equal_operator_modifying_operand(self):
        # test fix kila seg fault reported kwenye issue 27945 part 3.
        kundi X():
            eleza __del__(self):
                dict_b.clear()

            eleza __eq__(self, other):
                dict_a.clear()
                rudisha Kweli

            eleza __hash__(self):
                rudisha 13

        dict_a = {X(): 0}
        dict_b = {X(): X()}
        self.assertKweli(dict_a == dict_b)

    eleza test_kutokakeys_operator_modifying_dict_operand(self):
        # test fix kila seg fault reported kwenye issue 27945 part 4a.
        kundi X(int):
            eleza __hash__(self):
                rudisha 13

            eleza __eq__(self, other):
                ikiwa len(d) > 1:
                    d.clear()
                rudisha Uongo

        d = {}  # this ni required to exist so that d can be constructed!
        d = {X(1): 1, X(2): 2}
        jaribu:
            dict.kutokakeys(d)  # shouldn't crash
        tatizo RuntimeError:  # implementation defined
            pita

    eleza test_kutokakeys_operator_modifying_set_operand(self):
        # test fix kila seg fault reported kwenye issue 27945 part 4b.
        kundi X(int):
            eleza __hash__(self):
                rudisha 13

            eleza __eq__(self, other):
                ikiwa len(d) > 1:
                    d.clear()
                rudisha Uongo

        d = {}  # this ni required to exist so that d can be constructed!
        d = {X(1), X(2)}
        jaribu:
            dict.kutokakeys(d)  # shouldn't crash
        tatizo RuntimeError:  # implementation defined
            pita

    eleza test_dictitems_contains_use_after_free(self):
        kundi X:
            eleza __eq__(self, other):
                d.clear()
                rudisha NotImplemented

        d = {0: set()}
        (0, X()) kwenye d.items()

    eleza test_init_use_after_free(self):
        kundi X:
            eleza __hash__(self):
                pair[:] = []
                rudisha 13

        pair = [X(), 123]
        dict([pair])

    eleza test_oob_indexing_dictiter_iternextitem(self):
        kundi X(int):
            eleza __del__(self):
                d.clear()

        d = {i: X(i) kila i kwenye range(8)}

        eleza iter_and_mutate():
            kila result kwenye d.items():
                ikiwa result[0] == 2:
                    d[2] = Tupu # free d[2] --> X(2).__del__ was called

        self.assertRaises(RuntimeError, iter_and_mutate)

    eleza test_reversed(self):
        d = {"a": 1, "b": 2, "foo": 0, "c": 3, "d": 4}
        toa d["foo"]
        r = reversed(d)
        self.assertEqual(list(r), list('dcba'))
        self.assertRaises(StopIteration, next, r)

    eleza test_dict_copy_order(self):
        # bpo-34320
        od = collections.OrderedDict([('a', 1), ('b', 2)])
        od.move_to_end('a')
        expected = list(od.items())

        copy = dict(od)
        self.assertEqual(list(copy.items()), expected)

        # dict subkundi doesn't override __iter__
        kundi CustomDict(dict):
            pita

        pairs = [('a', 1), ('b', 2), ('c', 3)]

        d = CustomDict(pairs)
        self.assertEqual(pairs, list(dict(d).items()))

        kundi CustomReversedDict(dict):
            eleza keys(self):
                rudisha reversed(list(dict.keys(self)))

            __iter__ = keys

            eleza items(self):
                rudisha reversed(dict.items(self))

        d = CustomReversedDict(pairs)
        self.assertEqual(pairs[::-1], list(dict(d).items()))


kundi CAPITest(unittest.TestCase):

    # Test _PyDict_GetItem_KnownHash()
    @support.cpython_only
    eleza test_getitem_knownhash(self):
        kutoka _testcapi agiza dict_getitem_knownhash

        d = {'x': 1, 'y': 2, 'z': 3}
        self.assertEqual(dict_getitem_knownhash(d, 'x', hash('x')), 1)
        self.assertEqual(dict_getitem_knownhash(d, 'y', hash('y')), 2)
        self.assertEqual(dict_getitem_knownhash(d, 'z', hash('z')), 3)

        # sio a dict
        self.assertRaises(SystemError, dict_getitem_knownhash, [], 1, hash(1))
        # key does sio exist
        self.assertRaises(KeyError, dict_getitem_knownhash, {}, 1, hash(1))

        kundi Exc(Exception): pita
        kundi BadEq:
            eleza __eq__(self, other):
                ashiria Exc
            eleza __hash__(self):
                rudisha 7

        k1, k2 = BadEq(), BadEq()
        d = {k1: 1}
        self.assertEqual(dict_getitem_knownhash(d, k1, hash(k1)), 1)
        self.assertRaises(Exc, dict_getitem_knownhash, d, k2, hash(k2))


kutoka test agiza mapping_tests

kundi GeneralMappingTests(mapping_tests.BasicTestMappingProtocol):
    type2test = dict

kundi Dict(dict):
    pita

kundi SubclassMappingTests(mapping_tests.BasicTestMappingProtocol):
    type2test = Dict


ikiwa __name__ == "__main__":
    unittest.main()
