agiza collections.abc
agiza copy
agiza pickle
agiza sys
agiza unittest

kundi DictSetTest(unittest.TestCase):

    eleza test_constructors_not_callable(self):
        kt = type({}.keys())
        self.assertRaises(TypeError, kt, {})
        self.assertRaises(TypeError, kt)
        it = type({}.items())
        self.assertRaises(TypeError, it, {})
        self.assertRaises(TypeError, it)
        vt = type({}.values())
        self.assertRaises(TypeError, vt, {})
        self.assertRaises(TypeError, vt)

    eleza test_dict_keys(self):
        d = {1: 10, "a": "ABC"}
        keys = d.keys()
        self.assertEqual(len(keys), 2)
        self.assertEqual(set(keys), {1, "a"})
        self.assertEqual(keys, {1, "a"})
        self.assertNotEqual(keys, {1, "a", "b"})
        self.assertNotEqual(keys, {1, "b"})
        self.assertNotEqual(keys, {1})
        self.assertNotEqual(keys, 42)
        self.assertIn(1, keys)
        self.assertIn("a", keys)
        self.assertNotIn(10, keys)
        self.assertNotIn("Z", keys)
        self.assertEqual(d.keys(), d.keys())
        e = {1: 11, "a": "def"}
        self.assertEqual(d.keys(), e.keys())
        toa e["a"]
        self.assertNotEqual(d.keys(), e.keys())

    eleza test_dict_items(self):
        d = {1: 10, "a": "ABC"}
        items = d.items()
        self.assertEqual(len(items), 2)
        self.assertEqual(set(items), {(1, 10), ("a", "ABC")})
        self.assertEqual(items, {(1, 10), ("a", "ABC")})
        self.assertNotEqual(items, {(1, 10), ("a", "ABC"), "junk"})
        self.assertNotEqual(items, {(1, 10), ("a", "def")})
        self.assertNotEqual(items, {(1, 10)})
        self.assertNotEqual(items, 42)
        self.assertIn((1, 10), items)
        self.assertIn(("a", "ABC"), items)
        self.assertNotIn((1, 11), items)
        self.assertNotIn(1, items)
        self.assertNotIn((), items)
        self.assertNotIn((1,), items)
        self.assertNotIn((1, 2, 3), items)
        self.assertEqual(d.items(), d.items())
        e = d.copy()
        self.assertEqual(d.items(), e.items())
        e["a"] = "def"
        self.assertNotEqual(d.items(), e.items())

    eleza test_dict_mixed_keys_items(self):
        d = {(1, 1): 11, (2, 2): 22}
        e = {1: 1, 2: 2}
        self.assertEqual(d.keys(), e.items())
        self.assertNotEqual(d.items(), e.keys())

    eleza test_dict_values(self):
        d = {1: 10, "a": "ABC"}
        values = d.values()
        self.assertEqual(set(values), {10, "ABC"})
        self.assertEqual(len(values), 2)

    eleza test_dict_repr(self):
        d = {1: 10, "a": "ABC"}
        self.assertIsInstance(repr(d), str)
        r = repr(d.items())
        self.assertIsInstance(r, str)
        self.assertKweli(r == "dict_items([('a', 'ABC'), (1, 10)])" or
                        r == "dict_items([(1, 10), ('a', 'ABC')])")
        r = repr(d.keys())
        self.assertIsInstance(r, str)
        self.assertKweli(r == "dict_keys(['a', 1])" or
                        r == "dict_keys([1, 'a'])")
        r = repr(d.values())
        self.assertIsInstance(r, str)
        self.assertKweli(r == "dict_values(['ABC', 10])" or
                        r == "dict_values([10, 'ABC'])")

    eleza test_keys_set_operations(self):
        d1 = {'a': 1, 'b': 2}
        d2 = {'b': 3, 'c': 2}
        d3 = {'d': 4, 'e': 5}
        self.assertEqual(d1.keys() & d1.keys(), {'a', 'b'})
        self.assertEqual(d1.keys() & d2.keys(), {'b'})
        self.assertEqual(d1.keys() & d3.keys(), set())
        self.assertEqual(d1.keys() & set(d1.keys()), {'a', 'b'})
        self.assertEqual(d1.keys() & set(d2.keys()), {'b'})
        self.assertEqual(d1.keys() & set(d3.keys()), set())
        self.assertEqual(d1.keys() & tuple(d1.keys()), {'a', 'b'})

        self.assertEqual(d1.keys() | d1.keys(), {'a', 'b'})
        self.assertEqual(d1.keys() | d2.keys(), {'a', 'b', 'c'})
        self.assertEqual(d1.keys() | d3.keys(), {'a', 'b', 'd', 'e'})
        self.assertEqual(d1.keys() | set(d1.keys()), {'a', 'b'})
        self.assertEqual(d1.keys() | set(d2.keys()), {'a', 'b', 'c'})
        self.assertEqual(d1.keys() | set(d3.keys()),
                         {'a', 'b', 'd', 'e'})
        self.assertEqual(d1.keys() | (1, 2), {'a', 'b', 1, 2})

        self.assertEqual(d1.keys() ^ d1.keys(), set())
        self.assertEqual(d1.keys() ^ d2.keys(), {'a', 'c'})
        self.assertEqual(d1.keys() ^ d3.keys(), {'a', 'b', 'd', 'e'})
        self.assertEqual(d1.keys() ^ set(d1.keys()), set())
        self.assertEqual(d1.keys() ^ set(d2.keys()), {'a', 'c'})
        self.assertEqual(d1.keys() ^ set(d3.keys()),
                         {'a', 'b', 'd', 'e'})
        self.assertEqual(d1.keys() ^ tuple(d2.keys()), {'a', 'c'})

        self.assertEqual(d1.keys() - d1.keys(), set())
        self.assertEqual(d1.keys() - d2.keys(), {'a'})
        self.assertEqual(d1.keys() - d3.keys(), {'a', 'b'})
        self.assertEqual(d1.keys() - set(d1.keys()), set())
        self.assertEqual(d1.keys() - set(d2.keys()), {'a'})
        self.assertEqual(d1.keys() - set(d3.keys()), {'a', 'b'})
        self.assertEqual(d1.keys() - (0, 1), {'a', 'b'})

        self.assertUongo(d1.keys().isdisjoint(d1.keys()))
        self.assertUongo(d1.keys().isdisjoint(d2.keys()))
        self.assertUongo(d1.keys().isdisjoint(list(d2.keys())))
        self.assertUongo(d1.keys().isdisjoint(set(d2.keys())))
        self.assertKweli(d1.keys().isdisjoint({'x', 'y', 'z'}))
        self.assertKweli(d1.keys().isdisjoint(['x', 'y', 'z']))
        self.assertKweli(d1.keys().isdisjoint(set(['x', 'y', 'z'])))
        self.assertKweli(d1.keys().isdisjoint(set(['x', 'y'])))
        self.assertKweli(d1.keys().isdisjoint(['x', 'y']))
        self.assertKweli(d1.keys().isdisjoint({}))
        self.assertKweli(d1.keys().isdisjoint(d3.keys()))

        de = {}
        self.assertKweli(de.keys().isdisjoint(set()))
        self.assertKweli(de.keys().isdisjoint([]))
        self.assertKweli(de.keys().isdisjoint(de.keys()))
        self.assertKweli(de.keys().isdisjoint([1]))

    eleza test_items_set_operations(self):
        d1 = {'a': 1, 'b': 2}
        d2 = {'a': 2, 'b': 2}
        d3 = {'d': 4, 'e': 5}
        self.assertEqual(
            d1.items() & d1.items(), {('a', 1), ('b', 2)})
        self.assertEqual(d1.items() & d2.items(), {('b', 2)})
        self.assertEqual(d1.items() & d3.items(), set())
        self.assertEqual(d1.items() & set(d1.items()),
                         {('a', 1), ('b', 2)})
        self.assertEqual(d1.items() & set(d2.items()), {('b', 2)})
        self.assertEqual(d1.items() & set(d3.items()), set())

        self.assertEqual(d1.items() | d1.items(),
                         {('a', 1), ('b', 2)})
        self.assertEqual(d1.items() | d2.items(),
                         {('a', 1), ('a', 2), ('b', 2)})
        self.assertEqual(d1.items() | d3.items(),
                         {('a', 1), ('b', 2), ('d', 4), ('e', 5)})
        self.assertEqual(d1.items() | set(d1.items()),
                         {('a', 1), ('b', 2)})
        self.assertEqual(d1.items() | set(d2.items()),
                         {('a', 1), ('a', 2), ('b', 2)})
        self.assertEqual(d1.items() | set(d3.items()),
                         {('a', 1), ('b', 2), ('d', 4), ('e', 5)})

        self.assertEqual(d1.items() ^ d1.items(), set())
        self.assertEqual(d1.items() ^ d2.items(),
                         {('a', 1), ('a', 2)})
        self.assertEqual(d1.items() ^ d3.items(),
                         {('a', 1), ('b', 2), ('d', 4), ('e', 5)})

        self.assertEqual(d1.items() - d1.items(), set())
        self.assertEqual(d1.items() - d2.items(), {('a', 1)})
        self.assertEqual(d1.items() - d3.items(), {('a', 1), ('b', 2)})
        self.assertEqual(d1.items() - set(d1.items()), set())
        self.assertEqual(d1.items() - set(d2.items()), {('a', 1)})
        self.assertEqual(d1.items() - set(d3.items()), {('a', 1), ('b', 2)})

        self.assertUongo(d1.items().isdisjoint(d1.items()))
        self.assertUongo(d1.items().isdisjoint(d2.items()))
        self.assertUongo(d1.items().isdisjoint(list(d2.items())))
        self.assertUongo(d1.items().isdisjoint(set(d2.items())))
        self.assertKweli(d1.items().isdisjoint({'x', 'y', 'z'}))
        self.assertKweli(d1.items().isdisjoint(['x', 'y', 'z']))
        self.assertKweli(d1.items().isdisjoint(set(['x', 'y', 'z'])))
        self.assertKweli(d1.items().isdisjoint(set(['x', 'y'])))
        self.assertKweli(d1.items().isdisjoint({}))
        self.assertKweli(d1.items().isdisjoint(d3.items()))

        de = {}
        self.assertKweli(de.items().isdisjoint(set()))
        self.assertKweli(de.items().isdisjoint([]))
        self.assertKweli(de.items().isdisjoint(de.items()))
        self.assertKweli(de.items().isdisjoint([1]))

    eleza test_recursive_repr(self):
        d = {}
        d[42] = d.values()
        r = repr(d)
        # Cannot perform a stronger test, kama the contents of the repr
        # are implementation-dependent.  All we can say ni that we
        # want a str result, sio an exception of any sort.
        self.assertIsInstance(r, str)
        d[42] = d.items()
        r = repr(d)
        # Again.
        self.assertIsInstance(r, str)

    eleza test_deeply_nested_repr(self):
        d = {}
        kila i kwenye range(sys.getrecursionlimit() + 100):
            d = {42: d.values()}
        self.assertRaises(RecursionError, repr, d)

    eleza test_copy(self):
        d = {1: 10, "a": "ABC"}
        self.assertRaises(TypeError, copy.copy, d.keys())
        self.assertRaises(TypeError, copy.copy, d.values())
        self.assertRaises(TypeError, copy.copy, d.items())

    eleza test_compare_error(self):
        kundi Exc(Exception):
            pita

        kundi BadEq:
            eleza __hash__(self):
                rudisha 7
            eleza __eq__(self, other):
                ashiria Exc

        k1, k2 = BadEq(), BadEq()
        v1, v2 = BadEq(), BadEq()
        d = {k1: v1}

        self.assertIn(k1, d)
        self.assertIn(k1, d.keys())
        self.assertIn(v1, d.values())
        self.assertIn((k1, v1), d.items())

        self.assertRaises(Exc, d.__contains__, k2)
        self.assertRaises(Exc, d.keys().__contains__, k2)
        self.assertRaises(Exc, d.items().__contains__, (k2, v1))
        self.assertRaises(Exc, d.items().__contains__, (k1, v2))
        with self.assertRaises(Exc):
            v2 kwenye d.values()

    eleza test_pickle(self):
        d = {1: 10, "a": "ABC"}
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            self.assertRaises((TypeError, pickle.PicklingError),
                pickle.dumps, d.keys(), proto)
            self.assertRaises((TypeError, pickle.PicklingError),
                pickle.dumps, d.values(), proto)
            self.assertRaises((TypeError, pickle.PicklingError),
                pickle.dumps, d.items(), proto)

    eleza test_abc_registry(self):
        d = dict(a=1)

        self.assertIsInstance(d.keys(), collections.abc.KeysView)
        self.assertIsInstance(d.keys(), collections.abc.MappingView)
        self.assertIsInstance(d.keys(), collections.abc.Set)
        self.assertIsInstance(d.keys(), collections.abc.Sized)
        self.assertIsInstance(d.keys(), collections.abc.Iterable)
        self.assertIsInstance(d.keys(), collections.abc.Container)

        self.assertIsInstance(d.values(), collections.abc.ValuesView)
        self.assertIsInstance(d.values(), collections.abc.MappingView)
        self.assertIsInstance(d.values(), collections.abc.Sized)

        self.assertIsInstance(d.items(), collections.abc.ItemsView)
        self.assertIsInstance(d.items(), collections.abc.MappingView)
        self.assertIsInstance(d.items(), collections.abc.Set)
        self.assertIsInstance(d.items(), collections.abc.Sized)
        self.assertIsInstance(d.items(), collections.abc.Iterable)
        self.assertIsInstance(d.items(), collections.abc.Container)


ikiwa __name__ == "__main__":
    unittest.main()
