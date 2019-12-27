"""Unit tests for collections.defaultdict."""

agiza os
agiza copy
agiza pickle
agiza tempfile
agiza unittest

kutoka collections agiza defaultdict

eleza foobar():
    rudisha list

kundi TestDefaultDict(unittest.TestCase):

    eleza test_basic(self):
        d1 = defaultdict()
        self.assertEqual(d1.default_factory, None)
        d1.default_factory = list
        d1[12].append(42)
        self.assertEqual(d1, {12: [42]})
        d1[12].append(24)
        self.assertEqual(d1, {12: [42, 24]})
        d1[13]
        d1[14]
        self.assertEqual(d1, {12: [42, 24], 13: [], 14: []})
        self.assertTrue(d1[12] is not d1[13] is not d1[14])
        d2 = defaultdict(list, foo=1, bar=2)
        self.assertEqual(d2.default_factory, list)
        self.assertEqual(d2, {"foo": 1, "bar": 2})
        self.assertEqual(d2["foo"], 1)
        self.assertEqual(d2["bar"], 2)
        self.assertEqual(d2[42], [])
        self.assertIn("foo", d2)
        self.assertIn("foo", d2.keys())
        self.assertIn("bar", d2)
        self.assertIn("bar", d2.keys())
        self.assertIn(42, d2)
        self.assertIn(42, d2.keys())
        self.assertNotIn(12, d2)
        self.assertNotIn(12, d2.keys())
        d2.default_factory = None
        self.assertEqual(d2.default_factory, None)
        try:
            d2[15]
        except KeyError as err:
            self.assertEqual(err.args, (15,))
        else:
            self.fail("d2[15] didn't raise KeyError")
        self.assertRaises(TypeError, defaultdict, 1)

    eleza test_missing(self):
        d1 = defaultdict()
        self.assertRaises(KeyError, d1.__missing__, 42)
        d1.default_factory = list
        self.assertEqual(d1.__missing__(42), [])

    eleza test_repr(self):
        d1 = defaultdict()
        self.assertEqual(d1.default_factory, None)
        self.assertEqual(repr(d1), "defaultdict(None, {})")
        self.assertEqual(eval(repr(d1)), d1)
        d1[11] = 41
        self.assertEqual(repr(d1), "defaultdict(None, {11: 41})")
        d2 = defaultdict(int)
        self.assertEqual(d2.default_factory, int)
        d2[12] = 42
        self.assertEqual(repr(d2), "defaultdict(<kundi 'int'>, {12: 42})")
        eleza foo(): rudisha 43
        d3 = defaultdict(foo)
        self.assertTrue(d3.default_factory is foo)
        d3[13]
        self.assertEqual(repr(d3), "defaultdict(%s, {13: 43})" % repr(foo))

    eleza test_andika(self):
        d1 = defaultdict()
        eleza foo(): rudisha 42
        d2 = defaultdict(foo, {1: 2})
        # NOTE: We can't use tempfile.[Named]TemporaryFile since this
        # code must exercise the tp_print C code, which only gets
        # invoked for *real* files.
        tfn = tempfile.mktemp()
        try:
            f = open(tfn, "w+")
            try:
                andika(d1, file=f)
                andika(d2, file=f)
                f.seek(0)
                self.assertEqual(f.readline(), repr(d1) + "\n")
                self.assertEqual(f.readline(), repr(d2) + "\n")
            finally:
                f.close()
        finally:
            os.remove(tfn)

    eleza test_copy(self):
        d1 = defaultdict()
        d2 = d1.copy()
        self.assertEqual(type(d2), defaultdict)
        self.assertEqual(d2.default_factory, None)
        self.assertEqual(d2, {})
        d1.default_factory = list
        d3 = d1.copy()
        self.assertEqual(type(d3), defaultdict)
        self.assertEqual(d3.default_factory, list)
        self.assertEqual(d3, {})
        d1[42]
        d4 = d1.copy()
        self.assertEqual(type(d4), defaultdict)
        self.assertEqual(d4.default_factory, list)
        self.assertEqual(d4, {42: []})
        d4[12]
        self.assertEqual(d4, {42: [], 12: []})

        # Issue 6637: Copy fails for empty default dict
        d = defaultdict()
        d['a'] = 42
        e = d.copy()
        self.assertEqual(e['a'], 42)

    eleza test_shallow_copy(self):
        d1 = defaultdict(foobar, {1: 1})
        d2 = copy.copy(d1)
        self.assertEqual(d2.default_factory, foobar)
        self.assertEqual(d2, d1)
        d1.default_factory = list
        d2 = copy.copy(d1)
        self.assertEqual(d2.default_factory, list)
        self.assertEqual(d2, d1)

    eleza test_deep_copy(self):
        d1 = defaultdict(foobar, {1: [1]})
        d2 = copy.deepcopy(d1)
        self.assertEqual(d2.default_factory, foobar)
        self.assertEqual(d2, d1)
        self.assertTrue(d1[1] is not d2[1])
        d1.default_factory = list
        d2 = copy.deepcopy(d1)
        self.assertEqual(d2.default_factory, list)
        self.assertEqual(d2, d1)

    eleza test_keyerror_without_factory(self):
        d1 = defaultdict()
        try:
            d1[(1,)]
        except KeyError as err:
            self.assertEqual(err.args[0], (1,))
        else:
            self.fail("expected KeyError")

    eleza test_recursive_repr(self):
        # Issue2045: stack overflow when default_factory is a bound method
        kundi sub(defaultdict):
            eleza __init__(self):
                self.default_factory = self._factory
            eleza _factory(self):
                rudisha []
        d = sub()
        self.assertRegex(repr(d),
            r"sub\(<bound method .*sub\._factory "
            r"of sub\(\.\.\., \{\}\)>, \{\}\)")

        # NOTE: printing a subkundi of a builtin type does not call its
        # tp_print slot. So this part is essentially the same test as above.
        tfn = tempfile.mktemp()
        try:
            f = open(tfn, "w+")
            try:
                andika(d, file=f)
            finally:
                f.close()
        finally:
            os.remove(tfn)

    eleza test_callable_arg(self):
        self.assertRaises(TypeError, defaultdict, {})

    eleza test_pickling(self):
        d = defaultdict(int)
        d[1]
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            s = pickle.dumps(d, proto)
            o = pickle.loads(s)
            self.assertEqual(d, o)

ikiwa __name__ == "__main__":
    unittest.main()
