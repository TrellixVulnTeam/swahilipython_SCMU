"""Unit tests kila collections.py."""

agiza collections
agiza copy
agiza doctest
agiza inspect
agiza operator
agiza pickle
kutoka random agiza choice, randrange
agiza string
agiza sys
kutoka test agiza support
agiza types
agiza unittest

kutoka collections agiza namedtuple, Counter, OrderedDict, _count_elements
kutoka collections agiza UserDict, UserString, UserList
kutoka collections agiza ChainMap
kutoka collections agiza deque
kutoka collections.abc agiza Awaitable, Coroutine
kutoka collections.abc agiza AsyncIterator, AsyncIterable, AsyncGenerator
kutoka collections.abc agiza Hashable, Iterable, Iterator, Generator, Reversible
kutoka collections.abc agiza Sized, Container, Callable, Collection
kutoka collections.abc agiza Set, MutableSet
kutoka collections.abc agiza Mapping, MutableMapping, KeysView, ItemsView, ValuesView
kutoka collections.abc agiza Sequence, MutableSequence
kutoka collections.abc agiza ByteString


kundi TestUserObjects(unittest.TestCase):
    eleza _superset_test(self, a, b):
        self.assertGreaterEqual(
            set(dir(a)),
            set(dir(b)),
            '{a} should have all the methods of {b}'.format(
                a=a.__name__,
                b=b.__name__,
            ),
        )

    eleza _copy_test(self, obj):
        # Test internal copy
        obj_copy = obj.copy()
        self.assertIsNot(obj.data, obj_copy.data)
        self.assertEqual(obj.data, obj_copy.data)

        # Test copy.copy
        obj.test = [1234]  # Make sure instance vars are also copied.
        obj_copy = copy.copy(obj)
        self.assertIsNot(obj.data, obj_copy.data)
        self.assertEqual(obj.data, obj_copy.data)
        self.assertIs(obj.test, obj_copy.test)

    eleza test_str_protocol(self):
        self._superset_test(UserString, str)

    eleza test_list_protocol(self):
        self._superset_test(UserList, list)

    eleza test_dict_protocol(self):
        self._superset_test(UserDict, dict)

    eleza test_list_copy(self):
        obj = UserList()
        obj.append(123)
        self._copy_test(obj)

    eleza test_dict_copy(self):
        obj = UserDict()
        obj[123] = "abc"
        self._copy_test(obj)


################################################################################
### ChainMap (helper kundi kila configparser na the string module)
################################################################################

kundi TestChainMap(unittest.TestCase):

    eleza test_basics(self):
        c = ChainMap()
        c['a'] = 1
        c['b'] = 2
        d = c.new_child()
        d['b'] = 20
        d['c'] = 30
        self.assertEqual(d.maps, [{'b':20, 'c':30}, {'a':1, 'b':2}])  # check internal state
        self.assertEqual(d.items(), dict(a=1, b=20, c=30).items())    # check items/iter/getitem
        self.assertEqual(len(d), 3)                                   # check len
        kila key kwenye 'abc':                                             # check contains
            self.assertIn(key, d)
        kila k, v kwenye dict(a=1, b=20, c=30, z=100).items():             # check get
            self.assertEqual(d.get(k, 100), v)

        toa d['b']                                                    # unmask a value
        self.assertEqual(d.maps, [{'c':30}, {'a':1, 'b':2}])          # check internal state
        self.assertEqual(d.items(), dict(a=1, b=2, c=30).items())     # check items/iter/getitem
        self.assertEqual(len(d), 3)                                   # check len
        kila key kwenye 'abc':                                             # check contains
            self.assertIn(key, d)
        kila k, v kwenye dict(a=1, b=2, c=30, z=100).items():              # check get
            self.assertEqual(d.get(k, 100), v)
        self.assertIn(repr(d), [                                      # check repr
            type(d).__name__ + "({'c': 30}, {'a': 1, 'b': 2})",
            type(d).__name__ + "({'c': 30}, {'b': 2, 'a': 1})"
        ])

        kila e kwenye d.copy(), copy.copy(d):                               # check shallow copies
            self.assertEqual(d, e)
            self.assertEqual(d.maps, e.maps)
            self.assertIsNot(d, e)
            self.assertIsNot(d.maps[0], e.maps[0])
            kila m1, m2 kwenye zip(d.maps[1:], e.maps[1:]):
                self.assertIs(m1, m2)

        # check deep copies
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            e = pickle.loads(pickle.dumps(d, proto))
            self.assertEqual(d, e)
            self.assertEqual(d.maps, e.maps)
            self.assertIsNot(d, e)
            kila m1, m2 kwenye zip(d.maps, e.maps):
                self.assertIsNot(m1, m2, e)
        kila e kwenye [copy.deepcopy(d),
                  eval(repr(d))
                ]:
            self.assertEqual(d, e)
            self.assertEqual(d.maps, e.maps)
            self.assertIsNot(d, e)
            kila m1, m2 kwenye zip(d.maps, e.maps):
                self.assertIsNot(m1, m2, e)

        f = d.new_child()
        f['b'] = 5
        self.assertEqual(f.maps, [{'b': 5}, {'c':30}, {'a':1, 'b':2}])
        self.assertEqual(f.parents.maps, [{'c':30}, {'a':1, 'b':2}])   # check parents
        self.assertEqual(f['b'], 5)                                    # find first kwenye chain
        self.assertEqual(f.parents['b'], 2)                            # look beyond maps[0]

    eleza test_ordering(self):
        # Combined order matches a series of dict updates kutoka last to first.
        # This test relies on the ordering of the underlying dicts.

        baseline = {'music': 'bach', 'art': 'rembrandt'}
        adjustments = {'art': 'van gogh', 'opera': 'carmen'}

        cm = ChainMap(adjustments, baseline)

        combined = baseline.copy()
        combined.update(adjustments)

        self.assertEqual(list(combined.items()), list(cm.items()))

    eleza test_constructor(self):
        self.assertEqual(ChainMap().maps, [{}])                        # no-args --> one new dict
        self.assertEqual(ChainMap({1:2}).maps, [{1:2}])                # 1 arg --> list

    eleza test_bool(self):
        self.assertUongo(ChainMap())
        self.assertUongo(ChainMap({}, {}))
        self.assertKweli(ChainMap({1:2}, {}))
        self.assertKweli(ChainMap({}, {1:2}))

    eleza test_missing(self):
        kundi DefaultChainMap(ChainMap):
            eleza __missing__(self, key):
                rudisha 999
        d = DefaultChainMap(dict(a=1, b=2), dict(b=20, c=30))
        kila k, v kwenye dict(a=1, b=2, c=30, d=999).items():
            self.assertEqual(d[k], v)                                  # check __getitem__ w/missing
        kila k, v kwenye dict(a=1, b=2, c=30, d=77).items():
            self.assertEqual(d.get(k, 77), v)                          # check get() w/ missing
        kila k, v kwenye dict(a=Kweli, b=Kweli, c=Kweli, d=Uongo).items():
            self.assertEqual(k kwenye d, v)                                # check __contains__ w/missing
        self.assertEqual(d.pop('a', 1001), 1, d)
        self.assertEqual(d.pop('a', 1002), 1002)                       # check pop() w/missing
        self.assertEqual(d.popitem(), ('b', 2))                        # check popitem() w/missing
        ukijumuisha self.assertRaises(KeyError):
            d.popitem()

    eleza test_order_preservation(self):
        d = ChainMap(
                OrderedDict(j=0, h=88888),
                OrderedDict(),
                OrderedDict(i=9999, d=4444, c=3333),
                OrderedDict(f=666, b=222, g=777, c=333, h=888),
                OrderedDict(),
                OrderedDict(e=55, b=22),
                OrderedDict(a=1, b=2, c=3, d=4, e=5),
                OrderedDict(),
            )
        self.assertEqual(''.join(d), 'abcdefghij')
        self.assertEqual(list(d.items()),
            [('a', 1), ('b', 222), ('c', 3333), ('d', 4444),
             ('e', 55), ('f', 666), ('g', 777), ('h', 88888),
             ('i', 9999), ('j', 0)])

    eleza test_dict_coercion(self):
        d = ChainMap(dict(a=1, b=2), dict(b=20, c=30))
        self.assertEqual(dict(d), dict(a=1, b=2, c=30))
        self.assertEqual(dict(d.items()), dict(a=1, b=2, c=30))

    eleza test_new_child(self):
        'Tests kila changes kila issue #16613.'
        c = ChainMap()
        c['a'] = 1
        c['b'] = 2
        m = {'b':20, 'c': 30}
        d = c.new_child(m)
        self.assertEqual(d.maps, [{'b':20, 'c':30}, {'a':1, 'b':2}])  # check internal state
        self.assertIs(m, d.maps[0])

        # Use a different map than a dict
        kundi lowerdict(dict):
            eleza __getitem__(self, key):
                ikiwa isinstance(key, str):
                    key = key.lower()
                rudisha dict.__getitem__(self, key)
            eleza __contains__(self, key):
                ikiwa isinstance(key, str):
                    key = key.lower()
                rudisha dict.__contains__(self, key)

        c = ChainMap()
        c['a'] = 1
        c['b'] = 2
        m = lowerdict(b=20, c=30)
        d = c.new_child(m)
        self.assertIs(m, d.maps[0])
        kila key kwenye 'abc':                                             # check contains
            self.assertIn(key, d)
        kila k, v kwenye dict(a=1, B=20, C=30, z=100).items():             # check get
            self.assertEqual(d.get(k, 100), v)


################################################################################
### Named Tuples
################################################################################

TestNT = namedtuple('TestNT', 'x y z')    # type used kila pickle tests

kundi TestNamedTuple(unittest.TestCase):

    eleza test_factory(self):
        Point = namedtuple('Point', 'x y')
        self.assertEqual(Point.__name__, 'Point')
        self.assertEqual(Point.__slots__, ())
        self.assertEqual(Point.__module__, __name__)
        self.assertEqual(Point.__getitem__, tuple.__getitem__)
        self.assertEqual(Point._fields, ('x', 'y'))

        self.assertRaises(ValueError, namedtuple, 'abc%', 'efg ghi')       # type has non-alpha char
        self.assertRaises(ValueError, namedtuple, 'class', 'efg ghi')      # type has keyword
        self.assertRaises(ValueError, namedtuple, '9abc', 'efg ghi')       # type starts ukijumuisha digit

        self.assertRaises(ValueError, namedtuple, 'abc', 'efg g%hi')       # field ukijumuisha non-alpha char
        self.assertRaises(ValueError, namedtuple, 'abc', 'abc class')      # field has keyword
        self.assertRaises(ValueError, namedtuple, 'abc', '8efg 9ghi')      # field starts ukijumuisha digit
        self.assertRaises(ValueError, namedtuple, 'abc', '_efg ghi')       # field ukijumuisha leading underscore
        self.assertRaises(ValueError, namedtuple, 'abc', 'efg efg ghi')    # duplicate field

        namedtuple('Point0', 'x1 y2')   # Verify that numbers are allowed kwenye names
        namedtuple('_', 'a b c')        # Test leading underscores kwenye a typename

        nt = namedtuple('nt', 'the quick brown fox')                       # check unicode input
        self.assertNotIn("u'", repr(nt._fields))
        nt = namedtuple('nt', ('the', 'quick'))                           # check unicode input
        self.assertNotIn("u'", repr(nt._fields))

        self.assertRaises(TypeError, Point._make, [11])                     # catch too few args
        self.assertRaises(TypeError, Point._make, [11, 22, 33])             # catch too many args

    eleza test_defaults(self):
        Point = namedtuple('Point', 'x y', defaults=(10, 20))              # 2 defaults
        self.assertEqual(Point._field_defaults, {'x': 10, 'y': 20})
        self.assertEqual(Point(1, 2), (1, 2))
        self.assertEqual(Point(1), (1, 20))
        self.assertEqual(Point(), (10, 20))

        Point = namedtuple('Point', 'x y', defaults=(20,))                 # 1 default
        self.assertEqual(Point._field_defaults, {'y': 20})
        self.assertEqual(Point(1, 2), (1, 2))
        self.assertEqual(Point(1), (1, 20))

        Point = namedtuple('Point', 'x y', defaults=())                     # 0 defaults
        self.assertEqual(Point._field_defaults, {})
        self.assertEqual(Point(1, 2), (1, 2))
        ukijumuisha self.assertRaises(TypeError):
            Point(1)

        ukijumuisha self.assertRaises(TypeError):                                  # catch too few args
            Point()
        ukijumuisha self.assertRaises(TypeError):                                  # catch too many args
            Point(1, 2, 3)
        ukijumuisha self.assertRaises(TypeError):                                  # too many defaults
            Point = namedtuple('Point', 'x y', defaults=(10, 20, 30))
        ukijumuisha self.assertRaises(TypeError):                                  # non-iterable defaults
            Point = namedtuple('Point', 'x y', defaults=10)
        ukijumuisha self.assertRaises(TypeError):                                  # another non-iterable default
            Point = namedtuple('Point', 'x y', defaults=Uongo)

        Point = namedtuple('Point', 'x y', defaults=Tupu)                   # default ni Tupu
        self.assertEqual(Point._field_defaults, {})
        self.assertIsTupu(Point.__new__.__defaults__, Tupu)
        self.assertEqual(Point(10, 20), (10, 20))
        ukijumuisha self.assertRaises(TypeError):                                  # catch too few args
            Point(10)

        Point = namedtuple('Point', 'x y', defaults=[10, 20])               # allow non-tuple iterable
        self.assertEqual(Point._field_defaults, {'x': 10, 'y': 20})
        self.assertEqual(Point.__new__.__defaults__, (10, 20))
        self.assertEqual(Point(1, 2), (1, 2))
        self.assertEqual(Point(1), (1, 20))
        self.assertEqual(Point(), (10, 20))

        Point = namedtuple('Point', 'x y', defaults=iter([10, 20]))         # allow plain iterator
        self.assertEqual(Point._field_defaults, {'x': 10, 'y': 20})
        self.assertEqual(Point.__new__.__defaults__, (10, 20))
        self.assertEqual(Point(1, 2), (1, 2))
        self.assertEqual(Point(1), (1, 20))
        self.assertEqual(Point(), (10, 20))

    eleza test_readonly(self):
        Point = namedtuple('Point', 'x y')
        p = Point(11, 22)
        ukijumuisha self.assertRaises(AttributeError):
            p.x = 33
        ukijumuisha self.assertRaises(AttributeError):
            toa p.x
        ukijumuisha self.assertRaises(TypeError):
            p[0] = 33
        ukijumuisha self.assertRaises(TypeError):
            toa p[0]
        self.assertEqual(p.x, 11)
        self.assertEqual(p[0], 11)

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    eleza test_factory_doc_attr(self):
        Point = namedtuple('Point', 'x y')
        self.assertEqual(Point.__doc__, 'Point(x, y)')
        Point.__doc__ = '2D point'
        self.assertEqual(Point.__doc__, '2D point')

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    eleza test_field_doc(self):
        Point = namedtuple('Point', 'x y')
        self.assertEqual(Point.x.__doc__, 'Alias kila field number 0')
        self.assertEqual(Point.y.__doc__, 'Alias kila field number 1')
        Point.x.__doc__ = 'docstring kila Point.x'
        self.assertEqual(Point.x.__doc__, 'docstring kila Point.x')
        # namedtuple can mutate doc of descriptors independently
        Vector = namedtuple('Vector', 'x y')
        self.assertEqual(Vector.x.__doc__, 'Alias kila field number 0')
        Vector.x.__doc__ = 'docstring kila Vector.x'
        self.assertEqual(Vector.x.__doc__, 'docstring kila Vector.x')

    @support.cpython_only
    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    eleza test_field_doc_reuse(self):
        P = namedtuple('P', ['m', 'n'])
        Q = namedtuple('Q', ['o', 'p'])
        self.assertIs(P.m.__doc__, Q.o.__doc__)
        self.assertIs(P.n.__doc__, Q.p.__doc__)

    eleza test_name_fixer(self):
        kila spec, renamed kwenye [
            [('efg', 'g%hi'),  ('efg', '_1')],                              # field ukijumuisha non-alpha char
            [('abc', 'class'), ('abc', '_1')],                              # field has keyword
            [('8efg', '9ghi'), ('_0', '_1')],                               # field starts ukijumuisha digit
            [('abc', '_efg'), ('abc', '_1')],                               # field ukijumuisha leading underscore
            [('abc', 'efg', 'efg', 'ghi'), ('abc', 'efg', '_2', 'ghi')],    # duplicate field
            [('abc', '', 'x'), ('abc', '_1', 'x')],                         # fieldname ni a space
        ]:
            self.assertEqual(namedtuple('NT', spec, rename=Kweli)._fields, renamed)

    eleza test_module_parameter(self):
        NT = namedtuple('NT', ['x', 'y'], module=collections)
        self.assertEqual(NT.__module__, collections)

    eleza test_instance(self):
        Point = namedtuple('Point', 'x y')
        p = Point(11, 22)
        self.assertEqual(p, Point(x=11, y=22))
        self.assertEqual(p, Point(11, y=22))
        self.assertEqual(p, Point(y=22, x=11))
        self.assertEqual(p, Point(*(11, 22)))
        self.assertEqual(p, Point(**dict(x=11, y=22)))
        self.assertRaises(TypeError, Point, 1)          # too few args
        self.assertRaises(TypeError, Point, 1, 2, 3)    # too many args
        ukijumuisha self.assertRaises(TypeError):              # wrong keyword argument
            Point(XXX=1, y=2)
        ukijumuisha self.assertRaises(TypeError):              # missing keyword argument
            Point(x=1)
        self.assertEqual(repr(p), 'Point(x=11, y=22)')
        self.assertNotIn('__weakref__', dir(p))
        self.assertEqual(p, Point._make([11, 22]))      # test _make classmethod
        self.assertEqual(p._fields, ('x', 'y'))         # test _fields attribute
        self.assertEqual(p._replace(x=1), (1, 22))      # test _replace method
        self.assertEqual(p._asdict(), dict(x=11, y=22)) # test _asdict method

        jaribu:
            p._replace(x=1, error=2)
        except ValueError:
            pass
        isipokua:
            self._fail('Did sio detect an incorrect fieldname')

        # verify that field string can have commas
        Point = namedtuple('Point', 'x, y')
        p = Point(x=11, y=22)
        self.assertEqual(repr(p), 'Point(x=11, y=22)')

        # verify that fieldspec can be a non-string sequence
        Point = namedtuple('Point', ('x', 'y'))
        p = Point(x=11, y=22)
        self.assertEqual(repr(p), 'Point(x=11, y=22)')

    eleza test_tupleness(self):
        Point = namedtuple('Point', 'x y')
        p = Point(11, 22)

        self.assertIsInstance(p, tuple)
        self.assertEqual(p, (11, 22))                                       # matches a real tuple
        self.assertEqual(tuple(p), (11, 22))                                # coercable to a real tuple
        self.assertEqual(list(p), [11, 22])                                 # coercable to a list
        self.assertEqual(max(p), 22)                                        # iterable
        self.assertEqual(max(*p), 22)                                       # star-able
        x, y = p
        self.assertEqual(p, (x, y))                                         # unpacks like a tuple
        self.assertEqual((p[0], p[1]), (11, 22))                            # indexable like a tuple
        ukijumuisha self.assertRaises(IndexError):
            p[3]
        self.assertEqual(p[-1], 22)
        self.assertEqual(hash(p), hash((11, 22)))

        self.assertEqual(p.x, x)
        self.assertEqual(p.y, y)
        ukijumuisha self.assertRaises(AttributeError):
            p.z

    eleza test_odd_sizes(self):
        Zero = namedtuple('Zero', '')
        self.assertEqual(Zero(), ())
        self.assertEqual(Zero._make([]), ())
        self.assertEqual(repr(Zero()), 'Zero()')
        self.assertEqual(Zero()._asdict(), {})
        self.assertEqual(Zero()._fields, ())

        Dot = namedtuple('Dot', 'd')
        self.assertEqual(Dot(1), (1,))
        self.assertEqual(Dot._make([1]), (1,))
        self.assertEqual(Dot(1).d, 1)
        self.assertEqual(repr(Dot(1)), 'Dot(d=1)')
        self.assertEqual(Dot(1)._asdict(), {'d':1})
        self.assertEqual(Dot(1)._replace(d=999), (999,))
        self.assertEqual(Dot(1)._fields, ('d',))

        n = 5000
        names = list(set(''.join([choice(string.ascii_letters)
                                  kila j kwenye range(10)]) kila i kwenye range(n)))
        n = len(names)
        Big = namedtuple('Big', names)
        b = Big(*range(n))
        self.assertEqual(b, tuple(range(n)))
        self.assertEqual(Big._make(range(n)), tuple(range(n)))
        kila pos, name kwenye enumerate(names):
            self.assertEqual(getattr(b, name), pos)
        repr(b)                                 # make sure repr() doesn't blow-up
        d = b._asdict()
        d_expected = dict(zip(names, range(n)))
        self.assertEqual(d, d_expected)
        b2 = b._replace(**dict([(names[1], 999),(names[-5], 42)]))
        b2_expected = list(range(n))
        b2_expected[1] = 999
        b2_expected[-5] = 42
        self.assertEqual(b2, tuple(b2_expected))
        self.assertEqual(b._fields, tuple(names))

    eleza test_pickle(self):
        p = TestNT(x=10, y=20, z=30)
        kila module kwenye (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            kila protocol kwenye range(-1, module.HIGHEST_PROTOCOL + 1):
                q = loads(dumps(p, protocol))
                self.assertEqual(p, q)
                self.assertEqual(p._fields, q._fields)
                self.assertNotIn(b'OrderedDict', dumps(p, protocol))

    eleza test_copy(self):
        p = TestNT(x=10, y=20, z=30)
        kila copier kwenye copy.copy, copy.deepcopy:
            q = copier(p)
            self.assertEqual(p, q)
            self.assertEqual(p._fields, q._fields)

    eleza test_name_conflicts(self):
        # Some names like "self", "cls", "tuple", "itemgetter", na "property"
        # failed when used as field names.  Test to make sure these now work.
        T = namedtuple('T', 'itemgetter property self cls tuple')
        t = T(1, 2, 3, 4, 5)
        self.assertEqual(t, (1,2,3,4,5))
        newt = t._replace(itemgetter=10, property=20, self=30, cls=40, tuple=50)
        self.assertEqual(newt, (10,20,30,40,50))

       # Broader test of all interesting names taken kutoka the code, old
       # template, na an example
        words = {'Alias', 'At', 'AttributeError', 'Build', 'Bypass', 'Create',
        'Encountered', 'Expected', 'Field', 'For', 'Got', 'Helper',
        'IronPython', 'Jython', 'KeyError', 'Make', 'Modify', 'Note',
        'OrderedDict', 'Point', 'Return', 'Returns', 'Type', 'TypeError',
        'Used', 'Validate', 'ValueError', 'Variables', 'a', 'accessible', 'add',
        'added', 'all', 'also', 'an', 'arg_list', 'args', 'arguments',
        'automatically', 'be', 'build', 'builtins', 'but', 'by', 'cannot',
        'class_namespace', 'classmethod', 'cls', 'collections', 'convert',
        'copy', 'created', 'creation', 'd', 'debugging', 'defined', 'dict',
        'dictionary', 'doc', 'docstring', 'docstrings', 'duplicate', 'effect',
        'either', 'enumerate', 'environments', 'error', 'example', 'exec', 'f',
        'f_globals', 'field', 'field_names', 'fields', 'formatted', 'frame',
        'function', 'functions', 'generate', 'get', 'getter', 'got', 'greater',
        'has', 'help', 'identifiers', 'index', 'indexable', 'instance',
        'instantiate', 'interning', 'introspection', 'isidentifier',
        'isinstance', 'itemgetter', 'iterable', 'join', 'keyword', 'keywords',
        'kwds', 'len', 'like', 'list', 'map', 'maps', 'message', 'metadata',
        'method', 'methods', 'module', 'module_name', 'must', 'name', 'named',
        'namedtuple', 'namedtuple_', 'names', 'namespace', 'needs', 'new',
        'nicely', 'num_fields', 'number', 'object', 'of', 'operator', 'option',
        'p', 'particular', 'pickle', 'pickling', 'plain', 'pop', 'positional',
        'property', 'r', 'regular', 'rename', 'replace', 'replacing', 'repr',
        'repr_fmt', 'representation', 'result', 'reuse_itemgetter', 's', 'seen',
        'self', 'sequence', 'set', 'side', 'specified', 'split', 'start',
        'startswith', 'step', 'str', 'string', 'strings', 'subclass', 'sys',
        'targets', 'than', 'the', 'their', 'this', 'to', 'tuple', 'tuple_new',
        'type', 'typename', 'underscore', 'unexpected', 'unpack', 'up', 'use',
        'used', 'user', 'valid', 'values', 'variable', 'verbose', 'where',
        'which', 'work', 'x', 'y', 'z', 'zip'}
        T = namedtuple('T', words)
        # test __new__
        values = tuple(range(len(words)))
        t = T(*values)
        self.assertEqual(t, values)
        t = T(**dict(zip(T._fields, values)))
        self.assertEqual(t, values)
        # test _make
        t = T._make(values)
        self.assertEqual(t, values)
        # exercise __repr__
        repr(t)
        # test _asdict
        self.assertEqual(t._asdict(), dict(zip(T._fields, values)))
        # test _replace
        t = T._make(values)
        newvalues = tuple(v*10 kila v kwenye values)
        newt = t._replace(**dict(zip(T._fields, newvalues)))
        self.assertEqual(newt, newvalues)
        # test _fields
        self.assertEqual(T._fields, tuple(words))
        # test __getnewargs__
        self.assertEqual(t.__getnewargs__(), values)

    eleza test_repr(self):
        A = namedtuple('A', 'x')
        self.assertEqual(repr(A(1)), 'A(x=1)')
        # repr should show the name of the subclass
        kundi B(A):
            pass
        self.assertEqual(repr(B(1)), 'B(x=1)')

    eleza test_keyword_only_arguments(self):
        # See issue 25628
        ukijumuisha self.assertRaises(TypeError):
            NT = namedtuple('NT', ['x', 'y'], Kweli)

        NT = namedtuple('NT', ['abc', 'def'], rename=Kweli)
        self.assertEqual(NT._fields, ('abc', '_1'))
        ukijumuisha self.assertRaises(TypeError):
            NT = namedtuple('NT', ['abc', 'def'], Uongo, Kweli)

    eleza test_namedtuple_subclass_issue_24931(self):
        kundi Point(namedtuple('_Point', ['x', 'y'])):
            pass

        a = Point(3, 4)
        self.assertEqual(a._asdict(), OrderedDict([('x', 3), ('y', 4)]))

        a.w = 5
        self.assertEqual(a.__dict__, {'w': 5})

    eleza test_field_descriptor(self):
        Point = namedtuple('Point', 'x y')
        p = Point(11, 22)
        self.assertKweli(inspect.isdatadescriptor(Point.x))
        self.assertEqual(Point.x.__get__(p), 11)
        self.assertRaises(AttributeError, Point.x.__set__, p, 33)
        self.assertRaises(AttributeError, Point.x.__delete__, p)

        kundi NewPoint(tuple):
            x = pickle.loads(pickle.dumps(Point.x))
            y = pickle.loads(pickle.dumps(Point.y))

        np = NewPoint([1, 2])

        self.assertEqual(np.x, 1)
        self.assertEqual(np.y, 2)


################################################################################
### Abstract Base Classes
################################################################################

kundi ABCTestCase(unittest.TestCase):

    eleza validate_abstract_methods(self, abc, *names):
        methodstubs = dict.fromkeys(names, lambda s, *args: 0)

        # everything should work will all required methods are present
        C = type('C', (abc,), methodstubs)
        C()

        # instantiation should fail ikiwa a required method ni missing
        kila name kwenye names:
            stubs = methodstubs.copy()
            toa stubs[name]
            C = type('C', (abc,), stubs)
            self.assertRaises(TypeError, C, name)

    eleza validate_isinstance(self, abc, name):
        stub = lambda s, *args: 0

        C = type('C', (object,), {'__hash__': Tupu})
        setattr(C, name, stub)
        self.assertIsInstance(C(), abc)
        self.assertKweli(issubclass(C, abc))

        C = type('C', (object,), {'__hash__': Tupu})
        self.assertNotIsInstance(C(), abc)
        self.assertUongo(issubclass(C, abc))

    eleza validate_comparison(self, instance):
        ops = ['lt', 'gt', 'le', 'ge', 'ne', 'or', 'and', 'xor', 'sub']
        operators = {}
        kila op kwenye ops:
            name = '__' + op + '__'
            operators[name] = getattr(operator, name)

        kundi Other:
            eleza __init__(self):
                self.right_side = Uongo
            eleza __eq__(self, other):
                self.right_side = Kweli
                rudisha Kweli
            __lt__ = __eq__
            __gt__ = __eq__
            __le__ = __eq__
            __ge__ = __eq__
            __ne__ = __eq__
            __ror__ = __eq__
            __rand__ = __eq__
            __rxor__ = __eq__
            __rsub__ = __eq__

        kila name, op kwenye operators.items():
            ikiwa sio hasattr(instance, name):
                endelea
            other = Other()
            op(instance, other)
            self.assertKweli(other.right_side,'Right side sio called kila %s.%s'
                            % (type(instance), name))

eleza _test_gen():
    yield

kundi TestOneTrickPonyABCs(ABCTestCase):

    eleza test_Awaitable(self):
        eleza gen():
            yield

        @types.coroutine
        eleza coro():
            yield

        async eleza new_coro():
            pass

        kundi Bar:
            eleza __await__(self):
                yield

        kundi MinimalCoro(Coroutine):
            eleza send(self, value):
                rudisha value
            eleza throw(self, typ, val=Tupu, tb=Tupu):
                super().throw(typ, val, tb)
            eleza __await__(self):
                yield

        non_samples = [Tupu, int(), gen(), object()]
        kila x kwenye non_samples:
            self.assertNotIsInstance(x, Awaitable)
            self.assertUongo(issubclass(type(x), Awaitable), repr(type(x)))

        samples = [Bar(), MinimalCoro()]
        kila x kwenye samples:
            self.assertIsInstance(x, Awaitable)
            self.assertKweli(issubclass(type(x), Awaitable))

        c = coro()
        # Iterable coroutines (generators ukijumuisha CO_ITERABLE_COROUTINE
        # flag don't have '__await__' method, hence can't be instances
        # of Awaitable. Use inspect.isawaitable to detect them.
        self.assertNotIsInstance(c, Awaitable)

        c = new_coro()
        self.assertIsInstance(c, Awaitable)
        c.close() # avoid RuntimeWarning that coro() was sio awaited

        kundi CoroLike: pass
        Coroutine.register(CoroLike)
        self.assertKweli(isinstance(CoroLike(), Awaitable))
        self.assertKweli(issubclass(CoroLike, Awaitable))
        CoroLike = Tupu
        support.gc_collect() # Kill CoroLike to clean-up ABCMeta cache

    eleza test_Coroutine(self):
        eleza gen():
            yield

        @types.coroutine
        eleza coro():
            yield

        async eleza new_coro():
            pass

        kundi Bar:
            eleza __await__(self):
                yield

        kundi MinimalCoro(Coroutine):
            eleza send(self, value):
                rudisha value
            eleza throw(self, typ, val=Tupu, tb=Tupu):
                super().throw(typ, val, tb)
            eleza __await__(self):
                yield

        non_samples = [Tupu, int(), gen(), object(), Bar()]
        kila x kwenye non_samples:
            self.assertNotIsInstance(x, Coroutine)
            self.assertUongo(issubclass(type(x), Coroutine), repr(type(x)))

        samples = [MinimalCoro()]
        kila x kwenye samples:
            self.assertIsInstance(x, Awaitable)
            self.assertKweli(issubclass(type(x), Awaitable))

        c = coro()
        # Iterable coroutines (generators ukijumuisha CO_ITERABLE_COROUTINE
        # flag don't have '__await__' method, hence can't be instances
        # of Coroutine. Use inspect.isawaitable to detect them.
        self.assertNotIsInstance(c, Coroutine)

        c = new_coro()
        self.assertIsInstance(c, Coroutine)
        c.close() # avoid RuntimeWarning that coro() was sio awaited

        kundi CoroLike:
            eleza send(self, value):
                pass
            eleza throw(self, typ, val=Tupu, tb=Tupu):
                pass
            eleza close(self):
                pass
            eleza __await__(self):
                pass
        self.assertKweli(isinstance(CoroLike(), Coroutine))
        self.assertKweli(issubclass(CoroLike, Coroutine))

        kundi CoroLike:
            eleza send(self, value):
                pass
            eleza close(self):
                pass
            eleza __await__(self):
                pass
        self.assertUongo(isinstance(CoroLike(), Coroutine))
        self.assertUongo(issubclass(CoroLike, Coroutine))

    eleza test_Hashable(self):
        # Check some non-hashables
        non_samples = [bytearray(), list(), set(), dict()]
        kila x kwenye non_samples:
            self.assertNotIsInstance(x, Hashable)
            self.assertUongo(issubclass(type(x), Hashable), repr(type(x)))
        # Check some hashables
        samples = [Tupu,
                   int(), float(), complex(),
                   str(),
                   tuple(), frozenset(),
                   int, list, object, type, bytes()
                   ]
        kila x kwenye samples:
            self.assertIsInstance(x, Hashable)
            self.assertKweli(issubclass(type(x), Hashable), repr(type(x)))
        self.assertRaises(TypeError, Hashable)
        # Check direct subclassing
        kundi H(Hashable):
            eleza __hash__(self):
                rudisha super().__hash__()
        self.assertEqual(hash(H()), 0)
        self.assertUongo(issubclass(int, H))
        self.validate_abstract_methods(Hashable, '__hash__')
        self.validate_isinstance(Hashable, '__hash__')

    eleza test_AsyncIterable(self):
        kundi AI:
            eleza __aiter__(self):
                rudisha self
        self.assertKweli(isinstance(AI(), AsyncIterable))
        self.assertKweli(issubclass(AI, AsyncIterable))
        # Check some non-iterables
        non_samples = [Tupu, object, []]
        kila x kwenye non_samples:
            self.assertNotIsInstance(x, AsyncIterable)
            self.assertUongo(issubclass(type(x), AsyncIterable), repr(type(x)))
        self.validate_abstract_methods(AsyncIterable, '__aiter__')
        self.validate_isinstance(AsyncIterable, '__aiter__')

    eleza test_AsyncIterator(self):
        kundi AI:
            eleza __aiter__(self):
                rudisha self
            async eleza __anext__(self):
                 ashiria StopAsyncIteration
        self.assertKweli(isinstance(AI(), AsyncIterator))
        self.assertKweli(issubclass(AI, AsyncIterator))
        non_samples = [Tupu, object, []]
        # Check some non-iterables
        kila x kwenye non_samples:
            self.assertNotIsInstance(x, AsyncIterator)
            self.assertUongo(issubclass(type(x), AsyncIterator), repr(type(x)))
        # Similarly to regular iterators (see issue 10565)
        kundi AnextOnly:
            async eleza __anext__(self):
                 ashiria StopAsyncIteration
        self.assertNotIsInstance(AnextOnly(), AsyncIterator)
        self.validate_abstract_methods(AsyncIterator, '__anext__', '__aiter__')

    eleza test_Iterable(self):
        # Check some non-iterables
        non_samples = [Tupu, 42, 3.14, 1j]
        kila x kwenye non_samples:
            self.assertNotIsInstance(x, Iterable)
            self.assertUongo(issubclass(type(x), Iterable), repr(type(x)))
        # Check some iterables
        samples = [bytes(), str(),
                   tuple(), list(), set(), frozenset(), dict(),
                   dict().keys(), dict().items(), dict().values(),
                   _test_gen(),
                   (x kila x kwenye []),
                   ]
        kila x kwenye samples:
            self.assertIsInstance(x, Iterable)
            self.assertKweli(issubclass(type(x), Iterable), repr(type(x)))
        # Check direct subclassing
        kundi I(Iterable):
            eleza __iter__(self):
                rudisha super().__iter__()
        self.assertEqual(list(I()), [])
        self.assertUongo(issubclass(str, I))
        self.validate_abstract_methods(Iterable, '__iter__')
        self.validate_isinstance(Iterable, '__iter__')
        # Check Tupu blocking
        kundi It:
            eleza __iter__(self): rudisha iter([])
        kundi ItBlocked(It):
            __iter__ = Tupu
        self.assertKweli(issubclass(It, Iterable))
        self.assertKweli(isinstance(It(), Iterable))
        self.assertUongo(issubclass(ItBlocked, Iterable))
        self.assertUongo(isinstance(ItBlocked(), Iterable))

    eleza test_Reversible(self):
        # Check some non-reversibles
        non_samples = [Tupu, 42, 3.14, 1j, set(), frozenset()]
        kila x kwenye non_samples:
            self.assertNotIsInstance(x, Reversible)
            self.assertUongo(issubclass(type(x), Reversible), repr(type(x)))
        # Check some non-reversible iterables
        non_reversibles = [_test_gen(), (x kila x kwenye []), iter([]), reversed([])]
        kila x kwenye non_reversibles:
            self.assertNotIsInstance(x, Reversible)
            self.assertUongo(issubclass(type(x), Reversible), repr(type(x)))
        # Check some reversible iterables
        samples = [bytes(), str(), tuple(), list(), OrderedDict(),
                   OrderedDict().keys(), OrderedDict().items(),
                   OrderedDict().values(), Counter(), Counter().keys(),
                   Counter().items(), Counter().values(), dict(),
                   dict().keys(), dict().items(), dict().values()]
        kila x kwenye samples:
            self.assertIsInstance(x, Reversible)
            self.assertKweli(issubclass(type(x), Reversible), repr(type(x)))
        # Check also Mapping, MutableMapping, na Sequence
        self.assertKweli(issubclass(Sequence, Reversible), repr(Sequence))
        self.assertUongo(issubclass(Mapping, Reversible), repr(Mapping))
        self.assertUongo(issubclass(MutableMapping, Reversible), repr(MutableMapping))
        # Check direct subclassing
        kundi R(Reversible):
            eleza __iter__(self):
                rudisha iter(list())
            eleza __reversed__(self):
                rudisha iter(list())
        self.assertEqual(list(reversed(R())), [])
        self.assertUongo(issubclass(float, R))
        self.validate_abstract_methods(Reversible, '__reversed__', '__iter__')
        # Check reversible non-iterable (which ni sio Reversible)
        kundi RevNoIter:
            eleza __reversed__(self): rudisha reversed([])
        kundi RevPlusIter(RevNoIter):
            eleza __iter__(self): rudisha iter([])
        self.assertUongo(issubclass(RevNoIter, Reversible))
        self.assertUongo(isinstance(RevNoIter(), Reversible))
        self.assertKweli(issubclass(RevPlusIter, Reversible))
        self.assertKweli(isinstance(RevPlusIter(), Reversible))
        # Check Tupu blocking
        kundi Rev:
            eleza __iter__(self): rudisha iter([])
            eleza __reversed__(self): rudisha reversed([])
        kundi RevItBlocked(Rev):
            __iter__ = Tupu
        kundi RevRevBlocked(Rev):
            __reversed__ = Tupu
        self.assertKweli(issubclass(Rev, Reversible))
        self.assertKweli(isinstance(Rev(), Reversible))
        self.assertUongo(issubclass(RevItBlocked, Reversible))
        self.assertUongo(isinstance(RevItBlocked(), Reversible))
        self.assertUongo(issubclass(RevRevBlocked, Reversible))
        self.assertUongo(isinstance(RevRevBlocked(), Reversible))

    eleza test_Collection(self):
        # Check some non-collections
        non_collections = [Tupu, 42, 3.14, 1j, lambda x: 2*x]
        kila x kwenye non_collections:
            self.assertNotIsInstance(x, Collection)
            self.assertUongo(issubclass(type(x), Collection), repr(type(x)))
        # Check some non-collection iterables
        non_col_iterables = [_test_gen(), iter(b''), iter(bytearray()),
                             (x kila x kwenye [])]
        kila x kwenye non_col_iterables:
            self.assertNotIsInstance(x, Collection)
            self.assertUongo(issubclass(type(x), Collection), repr(type(x)))
        # Check some collections
        samples = [set(), frozenset(), dict(), bytes(), str(), tuple(),
                   list(), dict().keys(), dict().items(), dict().values()]
        kila x kwenye samples:
            self.assertIsInstance(x, Collection)
            self.assertKweli(issubclass(type(x), Collection), repr(type(x)))
        # Check also Mapping, MutableMapping, etc.
        self.assertKweli(issubclass(Sequence, Collection), repr(Sequence))
        self.assertKweli(issubclass(Mapping, Collection), repr(Mapping))
        self.assertKweli(issubclass(MutableMapping, Collection),
                                    repr(MutableMapping))
        self.assertKweli(issubclass(Set, Collection), repr(Set))
        self.assertKweli(issubclass(MutableSet, Collection), repr(MutableSet))
        self.assertKweli(issubclass(Sequence, Collection), repr(MutableSet))
        # Check direct subclassing
        kundi Col(Collection):
            eleza __iter__(self):
                rudisha iter(list())
            eleza __len__(self):
                rudisha 0
            eleza __contains__(self, item):
                rudisha Uongo
        kundi DerCol(Col): pass
        self.assertEqual(list(iter(Col())), [])
        self.assertUongo(issubclass(list, Col))
        self.assertUongo(issubclass(set, Col))
        self.assertUongo(issubclass(float, Col))
        self.assertEqual(list(iter(DerCol())), [])
        self.assertUongo(issubclass(list, DerCol))
        self.assertUongo(issubclass(set, DerCol))
        self.assertUongo(issubclass(float, DerCol))
        self.validate_abstract_methods(Collection, '__len__', '__iter__',
                                                   '__contains__')
        # Check sized container non-iterable (which ni sio Collection) etc.
        kundi ColNoIter:
            eleza __len__(self): rudisha 0
            eleza __contains__(self, item): rudisha Uongo
        kundi ColNoSize:
            eleza __iter__(self): rudisha iter([])
            eleza __contains__(self, item): rudisha Uongo
        kundi ColNoCont:
            eleza __iter__(self): rudisha iter([])
            eleza __len__(self): rudisha 0
        self.assertUongo(issubclass(ColNoIter, Collection))
        self.assertUongo(isinstance(ColNoIter(), Collection))
        self.assertUongo(issubclass(ColNoSize, Collection))
        self.assertUongo(isinstance(ColNoSize(), Collection))
        self.assertUongo(issubclass(ColNoCont, Collection))
        self.assertUongo(isinstance(ColNoCont(), Collection))
        # Check Tupu blocking
        kundi SizeBlock:
            eleza __iter__(self): rudisha iter([])
            eleza __contains__(self): rudisha Uongo
            __len__ = Tupu
        kundi IterBlock:
            eleza __len__(self): rudisha 0
            eleza __contains__(self): rudisha Kweli
            __iter__ = Tupu
        self.assertUongo(issubclass(SizeBlock, Collection))
        self.assertUongo(isinstance(SizeBlock(), Collection))
        self.assertUongo(issubclass(IterBlock, Collection))
        self.assertUongo(isinstance(IterBlock(), Collection))
        # Check Tupu blocking kwenye subclass
        kundi ColImpl:
            eleza __iter__(self):
                rudisha iter(list())
            eleza __len__(self):
                rudisha 0
            eleza __contains__(self, item):
                rudisha Uongo
        kundi NonCol(ColImpl):
            __contains__ = Tupu
        self.assertUongo(issubclass(NonCol, Collection))
        self.assertUongo(isinstance(NonCol(), Collection))


    eleza test_Iterator(self):
        non_samples = [Tupu, 42, 3.14, 1j, b"", "", (), [], {}, set()]
        kila x kwenye non_samples:
            self.assertNotIsInstance(x, Iterator)
            self.assertUongo(issubclass(type(x), Iterator), repr(type(x)))
        samples = [iter(bytes()), iter(str()),
                   iter(tuple()), iter(list()), iter(dict()),
                   iter(set()), iter(frozenset()),
                   iter(dict().keys()), iter(dict().items()),
                   iter(dict().values()),
                   _test_gen(),
                   (x kila x kwenye []),
                   ]
        kila x kwenye samples:
            self.assertIsInstance(x, Iterator)
            self.assertKweli(issubclass(type(x), Iterator), repr(type(x)))
        self.validate_abstract_methods(Iterator, '__next__', '__iter__')

        # Issue 10565
        kundi NextOnly:
            eleza __next__(self):
                tuma 1
                return
        self.assertNotIsInstance(NextOnly(), Iterator)

    eleza test_Generator(self):
        kundi NonGen1:
            eleza __iter__(self): rudisha self
            eleza __next__(self): rudisha Tupu
            eleza close(self): pass
            eleza throw(self, typ, val=Tupu, tb=Tupu): pass

        kundi NonGen2:
            eleza __iter__(self): rudisha self
            eleza __next__(self): rudisha Tupu
            eleza close(self): pass
            eleza send(self, value): rudisha value

        kundi NonGen3:
            eleza close(self): pass
            eleza send(self, value): rudisha value
            eleza throw(self, typ, val=Tupu, tb=Tupu): pass

        non_samples = [
            Tupu, 42, 3.14, 1j, b"", "", (), [], {}, set(),
            iter(()), iter([]), NonGen1(), NonGen2(), NonGen3()]
        kila x kwenye non_samples:
            self.assertNotIsInstance(x, Generator)
            self.assertUongo(issubclass(type(x), Generator), repr(type(x)))

        kundi Gen:
            eleza __iter__(self): rudisha self
            eleza __next__(self): rudisha Tupu
            eleza close(self): pass
            eleza send(self, value): rudisha value
            eleza throw(self, typ, val=Tupu, tb=Tupu): pass

        kundi MinimalGen(Generator):
            eleza send(self, value):
                rudisha value
            eleza throw(self, typ, val=Tupu, tb=Tupu):
                super().throw(typ, val, tb)

        eleza gen():
            tuma 1

        samples = [gen(), (lambda: (yield))(), Gen(), MinimalGen()]
        kila x kwenye samples:
            self.assertIsInstance(x, Iterator)
            self.assertIsInstance(x, Generator)
            self.assertKweli(issubclass(type(x), Generator), repr(type(x)))
        self.validate_abstract_methods(Generator, 'send', 'throw')

        # mixin tests
        mgen = MinimalGen()
        self.assertIs(mgen, iter(mgen))
        self.assertIs(mgen.send(Tupu), next(mgen))
        self.assertEqual(2, mgen.send(2))
        self.assertIsTupu(mgen.close())
        self.assertRaises(ValueError, mgen.throw, ValueError)
        self.assertRaisesRegex(ValueError, "^huhu$",
                               mgen.throw, ValueError, ValueError("huhu"))
        self.assertRaises(StopIteration, mgen.throw, StopIteration())

        kundi FailOnClose(Generator):
            eleza send(self, value): rudisha value
            eleza throw(self, *args):  ashiria ValueError

        self.assertRaises(ValueError, FailOnClose().close)

        kundi IgnoreGeneratorExit(Generator):
            eleza send(self, value): rudisha value
            eleza throw(self, *args): pass

        self.assertRaises(RuntimeError, IgnoreGeneratorExit().close)

    eleza test_AsyncGenerator(self):
        kundi NonAGen1:
            eleza __aiter__(self): rudisha self
            eleza __anext__(self): rudisha Tupu
            eleza aclose(self): pass
            eleza athrow(self, typ, val=Tupu, tb=Tupu): pass

        kundi NonAGen2:
            eleza __aiter__(self): rudisha self
            eleza __anext__(self): rudisha Tupu
            eleza aclose(self): pass
            eleza asend(self, value): rudisha value

        kundi NonAGen3:
            eleza aclose(self): pass
            eleza asend(self, value): rudisha value
            eleza athrow(self, typ, val=Tupu, tb=Tupu): pass

        non_samples = [
            Tupu, 42, 3.14, 1j, b"", "", (), [], {}, set(),
            iter(()), iter([]), NonAGen1(), NonAGen2(), NonAGen3()]
        kila x kwenye non_samples:
            self.assertNotIsInstance(x, AsyncGenerator)
            self.assertUongo(issubclass(type(x), AsyncGenerator), repr(type(x)))

        kundi Gen:
            eleza __aiter__(self): rudisha self
            async eleza __anext__(self): rudisha Tupu
            async eleza aclose(self): pass
            async eleza asend(self, value): rudisha value
            async eleza athrow(self, typ, val=Tupu, tb=Tupu): pass

        kundi MinimalAGen(AsyncGenerator):
            async eleza asend(self, value):
                rudisha value
            async eleza athrow(self, typ, val=Tupu, tb=Tupu):
                await super().athrow(typ, val, tb)

        async eleza gen():
            tuma 1

        samples = [gen(), Gen(), MinimalAGen()]
        kila x kwenye samples:
            self.assertIsInstance(x, AsyncIterator)
            self.assertIsInstance(x, AsyncGenerator)
            self.assertKweli(issubclass(type(x), AsyncGenerator), repr(type(x)))
        self.validate_abstract_methods(AsyncGenerator, 'asend', 'athrow')

        eleza run_async(coro):
            result = Tupu
            wakati Kweli:
                jaribu:
                    coro.send(Tupu)
                except StopIteration as ex:
                    result = ex.args[0] ikiwa ex.args isipokua Tupu
                    koma
            rudisha result

        # mixin tests
        mgen = MinimalAGen()
        self.assertIs(mgen, mgen.__aiter__())
        self.assertIs(run_async(mgen.asend(Tupu)), run_async(mgen.__anext__()))
        self.assertEqual(2, run_async(mgen.asend(2)))
        self.assertIsTupu(run_async(mgen.aclose()))
        ukijumuisha self.assertRaises(ValueError):
            run_async(mgen.athrow(ValueError))

        kundi FailOnClose(AsyncGenerator):
            async eleza asend(self, value): rudisha value
            async eleza athrow(self, *args):  ashiria ValueError

        ukijumuisha self.assertRaises(ValueError):
            run_async(FailOnClose().aclose())

        kundi IgnoreGeneratorExit(AsyncGenerator):
            async eleza asend(self, value): rudisha value
            async eleza athrow(self, *args): pass

        ukijumuisha self.assertRaises(RuntimeError):
            run_async(IgnoreGeneratorExit().aclose())

    eleza test_Sized(self):
        non_samples = [Tupu, 42, 3.14, 1j,
                       _test_gen(),
                       (x kila x kwenye []),
                       ]
        kila x kwenye non_samples:
            self.assertNotIsInstance(x, Sized)
            self.assertUongo(issubclass(type(x), Sized), repr(type(x)))
        samples = [bytes(), str(),
                   tuple(), list(), set(), frozenset(), dict(),
                   dict().keys(), dict().items(), dict().values(),
                   ]
        kila x kwenye samples:
            self.assertIsInstance(x, Sized)
            self.assertKweli(issubclass(type(x), Sized), repr(type(x)))
        self.validate_abstract_methods(Sized, '__len__')
        self.validate_isinstance(Sized, '__len__')

    eleza test_Container(self):
        non_samples = [Tupu, 42, 3.14, 1j,
                       _test_gen(),
                       (x kila x kwenye []),
                       ]
        kila x kwenye non_samples:
            self.assertNotIsInstance(x, Container)
            self.assertUongo(issubclass(type(x), Container), repr(type(x)))
        samples = [bytes(), str(),
                   tuple(), list(), set(), frozenset(), dict(),
                   dict().keys(), dict().items(),
                   ]
        kila x kwenye samples:
            self.assertIsInstance(x, Container)
            self.assertKweli(issubclass(type(x), Container), repr(type(x)))
        self.validate_abstract_methods(Container, '__contains__')
        self.validate_isinstance(Container, '__contains__')

    eleza test_Callable(self):
        non_samples = [Tupu, 42, 3.14, 1j,
                       "", b"", (), [], {}, set(),
                       _test_gen(),
                       (x kila x kwenye []),
                       ]
        kila x kwenye non_samples:
            self.assertNotIsInstance(x, Callable)
            self.assertUongo(issubclass(type(x), Callable), repr(type(x)))
        samples = [lambda: Tupu,
                   type, int, object,
                   len,
                   list.append, [].append,
                   ]
        kila x kwenye samples:
            self.assertIsInstance(x, Callable)
            self.assertKweli(issubclass(type(x), Callable), repr(type(x)))
        self.validate_abstract_methods(Callable, '__call__')
        self.validate_isinstance(Callable, '__call__')

    eleza test_direct_subclassing(self):
        kila B kwenye Hashable, Iterable, Iterator, Reversible, Sized, Container, Callable:
            kundi C(B):
                pass
            self.assertKweli(issubclass(C, B))
            self.assertUongo(issubclass(int, C))

    eleza test_registration(self):
        kila B kwenye Hashable, Iterable, Iterator, Reversible, Sized, Container, Callable:
            kundi C:
                __hash__ = Tupu  # Make sure it isn't hashable by default
            self.assertUongo(issubclass(C, B), B.__name__)
            B.register(C)
            self.assertKweli(issubclass(C, B))

kundi WithSet(MutableSet):

    eleza __init__(self, it=()):
        self.data = set(it)

    eleza __len__(self):
        rudisha len(self.data)

    eleza __iter__(self):
        rudisha iter(self.data)

    eleza __contains__(self, item):
        rudisha item kwenye self.data

    eleza add(self, item):
        self.data.add(item)

    eleza discard(self, item):
        self.data.discard(item)

kundi TestCollectionABCs(ABCTestCase):

    # XXX For now, we only test some virtual inheritance properties.
    # We should also test the proper behavior of the collection ABCs
    # as real base classes ama mix-in classes.

    eleza test_Set(self):
        kila sample kwenye [set, frozenset]:
            self.assertIsInstance(sample(), Set)
            self.assertKweli(issubclass(sample, Set))
        self.validate_abstract_methods(Set, '__contains__', '__iter__', '__len__')
        kundi MySet(Set):
            eleza __contains__(self, x):
                rudisha Uongo
            eleza __len__(self):
                rudisha 0
            eleza __iter__(self):
                rudisha iter([])
        self.validate_comparison(MySet())

    eleza test_hash_Set(self):
        kundi OneTwoThreeSet(Set):
            eleza __init__(self):
                self.contents = [1, 2, 3]
            eleza __contains__(self, x):
                rudisha x kwenye self.contents
            eleza __len__(self):
                rudisha len(self.contents)
            eleza __iter__(self):
                rudisha iter(self.contents)
            eleza __hash__(self):
                rudisha self._hash()
        a, b = OneTwoThreeSet(), OneTwoThreeSet()
        self.assertKweli(hash(a) == hash(b))

    eleza test_isdisjoint_Set(self):
        kundi MySet(Set):
            eleza __init__(self, itr):
                self.contents = itr
            eleza __contains__(self, x):
                rudisha x kwenye self.contents
            eleza __iter__(self):
                rudisha iter(self.contents)
            eleza __len__(self):
                rudisha len([x kila x kwenye self.contents])
        s1 = MySet((1, 2, 3))
        s2 = MySet((4, 5, 6))
        s3 = MySet((1, 5, 6))
        self.assertKweli(s1.isdisjoint(s2))
        self.assertUongo(s1.isdisjoint(s3))

    eleza test_equality_Set(self):
        kundi MySet(Set):
            eleza __init__(self, itr):
                self.contents = itr
            eleza __contains__(self, x):
                rudisha x kwenye self.contents
            eleza __iter__(self):
                rudisha iter(self.contents)
            eleza __len__(self):
                rudisha len([x kila x kwenye self.contents])
        s1 = MySet((1,))
        s2 = MySet((1, 2))
        s3 = MySet((3, 4))
        s4 = MySet((3, 4))
        self.assertKweli(s2 > s1)
        self.assertKweli(s1 < s2)
        self.assertUongo(s2 <= s1)
        self.assertUongo(s2 <= s3)
        self.assertUongo(s1 >= s2)
        self.assertEqual(s3, s4)
        self.assertNotEqual(s2, s3)

    eleza test_arithmetic_Set(self):
        kundi MySet(Set):
            eleza __init__(self, itr):
                self.contents = itr
            eleza __contains__(self, x):
                rudisha x kwenye self.contents
            eleza __iter__(self):
                rudisha iter(self.contents)
            eleza __len__(self):
                rudisha len([x kila x kwenye self.contents])
        s1 = MySet((1, 2, 3))
        s2 = MySet((3, 4, 5))
        s3 = s1 & s2
        self.assertEqual(s3, MySet((3,)))

    eleza test_MutableSet(self):
        self.assertIsInstance(set(), MutableSet)
        self.assertKweli(issubclass(set, MutableSet))
        self.assertNotIsInstance(frozenset(), MutableSet)
        self.assertUongo(issubclass(frozenset, MutableSet))
        self.validate_abstract_methods(MutableSet, '__contains__', '__iter__', '__len__',
            'add', 'discard')

    eleza test_issue_5647(self):
        # MutableSet.__iand__ mutated the set during iteration
        s = WithSet('abcd')
        s &= WithSet('cdef')            # This used to fail
        self.assertEqual(set(s), set('cd'))

    eleza test_issue_4920(self):
        # MutableSet.pop() method did sio work
        kundi MySet(MutableSet):
            __slots__=['__s']
            eleza __init__(self,items=Tupu):
                ikiwa items ni Tupu:
                    items=[]
                self.__s=set(items)
            eleza __contains__(self,v):
                rudisha v kwenye self.__s
            eleza __iter__(self):
                rudisha iter(self.__s)
            eleza __len__(self):
                rudisha len(self.__s)
            eleza add(self,v):
                result=v sio kwenye self.__s
                self.__s.add(v)
                rudisha result
            eleza discard(self,v):
                result=v kwenye self.__s
                self.__s.discard(v)
                rudisha result
            eleza __repr__(self):
                rudisha "MySet(%s)" % repr(list(self))
        s = MySet([5,43,2,1])
        self.assertEqual(s.pop(), 1)

    eleza test_issue8750(self):
        empty = WithSet()
        full = WithSet(range(10))
        s = WithSet(full)
        s -= s
        self.assertEqual(s, empty)
        s = WithSet(full)
        s ^= s
        self.assertEqual(s, empty)
        s = WithSet(full)
        s &= s
        self.assertEqual(s, full)
        s |= s
        self.assertEqual(s, full)

    eleza test_issue16373(self):
        # Recursion error comparing comparable na noncomparable
        # Set instances
        kundi MyComparableSet(Set):
            eleza __contains__(self, x):
                rudisha Uongo
            eleza __len__(self):
                rudisha 0
            eleza __iter__(self):
                rudisha iter([])
        kundi MyNonComparableSet(Set):
            eleza __contains__(self, x):
                rudisha Uongo
            eleza __len__(self):
                rudisha 0
            eleza __iter__(self):
                rudisha iter([])
            eleza __le__(self, x):
                rudisha NotImplemented
            eleza __lt__(self, x):
                rudisha NotImplemented

        cs = MyComparableSet()
        ncs = MyNonComparableSet()
        self.assertUongo(ncs < cs)
        self.assertKweli(ncs <= cs)
        self.assertUongo(ncs > cs)
        self.assertKweli(ncs >= cs)

    eleza test_issue26915(self):
        # Container membership test should check identity first
        kundi CustomEqualObject:
            eleza __eq__(self, other):
                rudisha Uongo
        kundi CustomSequence(Sequence):
            eleza __init__(self, seq):
                self._seq = seq
            eleza __getitem__(self, index):
                rudisha self._seq[index]
            eleza __len__(self):
                rudisha len(self._seq)

        nan = float('nan')
        obj = CustomEqualObject()
        seq = CustomSequence([nan, obj, nan])
        containers = [
            seq,
            ItemsView({1: nan, 2: obj}),
            ValuesView({1: nan, 2: obj})
        ]
        kila container kwenye containers:
            kila elem kwenye container:
                self.assertIn(elem, container)
        self.assertEqual(seq.index(nan), 0)
        self.assertEqual(seq.index(obj), 1)
        self.assertEqual(seq.count(nan), 2)
        self.assertEqual(seq.count(obj), 1)

    eleza assertSameSet(self, s1, s2):
        # coerce both to a real set then check equality
        self.assertSetEqual(set(s1), set(s2))

    eleza test_Set_interoperability_with_real_sets(self):
        # Issue: 8743
        kundi ListSet(Set):
            eleza __init__(self, elements=()):
                self.data = []
                kila elem kwenye elements:
                    ikiwa elem sio kwenye self.data:
                        self.data.append(elem)
            eleza __contains__(self, elem):
                rudisha elem kwenye self.data
            eleza __iter__(self):
                rudisha iter(self.data)
            eleza __len__(self):
                rudisha len(self.data)
            eleza __repr__(self):
                rudisha 'Set({!r})'.format(self.data)

        r1 = set('abc')
        r2 = set('bcd')
        r3 = set('abcde')
        f1 = ListSet('abc')
        f2 = ListSet('bcd')
        f3 = ListSet('abcde')
        l1 = list('abccba')
        l2 = list('bcddcb')
        l3 = list('abcdeedcba')

        target = r1 & r2
        self.assertSameSet(f1 & f2, target)
        self.assertSameSet(f1 & r2, target)
        self.assertSameSet(r2 & f1, target)
        self.assertSameSet(f1 & l2, target)

        target = r1 | r2
        self.assertSameSet(f1 | f2, target)
        self.assertSameSet(f1 | r2, target)
        self.assertSameSet(r2 | f1, target)
        self.assertSameSet(f1 | l2, target)

        fwd_target = r1 - r2
        rev_target = r2 - r1
        self.assertSameSet(f1 - f2, fwd_target)
        self.assertSameSet(f2 - f1, rev_target)
        self.assertSameSet(f1 - r2, fwd_target)
        self.assertSameSet(f2 - r1, rev_target)
        self.assertSameSet(r1 - f2, fwd_target)
        self.assertSameSet(r2 - f1, rev_target)
        self.assertSameSet(f1 - l2, fwd_target)
        self.assertSameSet(f2 - l1, rev_target)

        target = r1 ^ r2
        self.assertSameSet(f1 ^ f2, target)
        self.assertSameSet(f1 ^ r2, target)
        self.assertSameSet(r2 ^ f1, target)
        self.assertSameSet(f1 ^ l2, target)

        # Don't change the following to use assertLess ama other
        # "more specific" unittest assertions.  The current
        # assertKweli/assertUongo style makes the pattern of test
        # case combinations clear na allows us to know kila sure
        # the exact operator being invoked.

        # proper subset
        self.assertKweli(f1 < f3)
        self.assertUongo(f1 < f1)
        self.assertUongo(f1 < f2)
        self.assertKweli(r1 < f3)
        self.assertUongo(r1 < f1)
        self.assertUongo(r1 < f2)
        self.assertKweli(r1 < r3)
        self.assertUongo(r1 < r1)
        self.assertUongo(r1 < r2)
        ukijumuisha self.assertRaises(TypeError):
            f1 < l3
        ukijumuisha self.assertRaises(TypeError):
            f1 < l1
        ukijumuisha self.assertRaises(TypeError):
            f1 < l2

        # any subset
        self.assertKweli(f1 <= f3)
        self.assertKweli(f1 <= f1)
        self.assertUongo(f1 <= f2)
        self.assertKweli(r1 <= f3)
        self.assertKweli(r1 <= f1)
        self.assertUongo(r1 <= f2)
        self.assertKweli(r1 <= r3)
        self.assertKweli(r1 <= r1)
        self.assertUongo(r1 <= r2)
        ukijumuisha self.assertRaises(TypeError):
            f1 <= l3
        ukijumuisha self.assertRaises(TypeError):
            f1 <= l1
        ukijumuisha self.assertRaises(TypeError):
            f1 <= l2

        # proper superset
        self.assertKweli(f3 > f1)
        self.assertUongo(f1 > f1)
        self.assertUongo(f2 > f1)
        self.assertKweli(r3 > r1)
        self.assertUongo(f1 > r1)
        self.assertUongo(f2 > r1)
        self.assertKweli(r3 > r1)
        self.assertUongo(r1 > r1)
        self.assertUongo(r2 > r1)
        ukijumuisha self.assertRaises(TypeError):
            f1 > l3
        ukijumuisha self.assertRaises(TypeError):
            f1 > l1
        ukijumuisha self.assertRaises(TypeError):
            f1 > l2

        # any superset
        self.assertKweli(f3 >= f1)
        self.assertKweli(f1 >= f1)
        self.assertUongo(f2 >= f1)
        self.assertKweli(r3 >= r1)
        self.assertKweli(f1 >= r1)
        self.assertUongo(f2 >= r1)
        self.assertKweli(r3 >= r1)
        self.assertKweli(r1 >= r1)
        self.assertUongo(r2 >= r1)
        ukijumuisha self.assertRaises(TypeError):
            f1 >= l3
        ukijumuisha self.assertRaises(TypeError):
            f1 >=l1
        ukijumuisha self.assertRaises(TypeError):
            f1 >= l2

        # equality
        self.assertKweli(f1 == f1)
        self.assertKweli(r1 == f1)
        self.assertKweli(f1 == r1)
        self.assertUongo(f1 == f3)
        self.assertUongo(r1 == f3)
        self.assertUongo(f1 == r3)
        self.assertUongo(f1 == l3)
        self.assertUongo(f1 == l1)
        self.assertUongo(f1 == l2)

        # inequality
        self.assertUongo(f1 != f1)
        self.assertUongo(r1 != f1)
        self.assertUongo(f1 != r1)
        self.assertKweli(f1 != f3)
        self.assertKweli(r1 != f3)
        self.assertKweli(f1 != r3)
        self.assertKweli(f1 != l3)
        self.assertKweli(f1 != l1)
        self.assertKweli(f1 != l2)

    eleza test_Mapping(self):
        kila sample kwenye [dict]:
            self.assertIsInstance(sample(), Mapping)
            self.assertKweli(issubclass(sample, Mapping))
        self.validate_abstract_methods(Mapping, '__contains__', '__iter__', '__len__',
            '__getitem__')
        kundi MyMapping(Mapping):
            eleza __len__(self):
                rudisha 0
            eleza __getitem__(self, i):
                 ashiria IndexError
            eleza __iter__(self):
                rudisha iter(())
        self.validate_comparison(MyMapping())
        self.assertRaises(TypeError, reversed, MyMapping())

    eleza test_MutableMapping(self):
        kila sample kwenye [dict]:
            self.assertIsInstance(sample(), MutableMapping)
            self.assertKweli(issubclass(sample, MutableMapping))
        self.validate_abstract_methods(MutableMapping, '__contains__', '__iter__', '__len__',
            '__getitem__', '__setitem__', '__delitem__')

    eleza test_MutableMapping_subclass(self):
        # Test issue 9214
        mymap = UserDict()
        mymap['red'] = 5
        self.assertIsInstance(mymap.keys(), Set)
        self.assertIsInstance(mymap.keys(), KeysView)
        self.assertIsInstance(mymap.items(), Set)
        self.assertIsInstance(mymap.items(), ItemsView)

        mymap = UserDict()
        mymap['red'] = 5
        z = mymap.keys() | {'orange'}
        self.assertIsInstance(z, set)
        list(z)
        mymap['blue'] = 7               # Shouldn't affect 'z'
        self.assertEqual(sorted(z), ['orange', 'red'])

        mymap = UserDict()
        mymap['red'] = 5
        z = mymap.items() | {('orange', 3)}
        self.assertIsInstance(z, set)
        list(z)
        mymap['blue'] = 7               # Shouldn't affect 'z'
        self.assertEqual(z, {('orange', 3), ('red', 5)})

    eleza test_Sequence(self):
        kila sample kwenye [tuple, list, bytes, str]:
            self.assertIsInstance(sample(), Sequence)
            self.assertKweli(issubclass(sample, Sequence))
        self.assertIsInstance(range(10), Sequence)
        self.assertKweli(issubclass(range, Sequence))
        self.assertIsInstance(memoryview(b""), Sequence)
        self.assertKweli(issubclass(memoryview, Sequence))
        self.assertKweli(issubclass(str, Sequence))
        self.validate_abstract_methods(Sequence, '__contains__', '__iter__', '__len__',
            '__getitem__')

    eleza test_Sequence_mixins(self):
        kundi SequenceSubclass(Sequence):
            eleza __init__(self, seq=()):
                self.seq = seq

            eleza __getitem__(self, index):
                rudisha self.seq[index]

            eleza __len__(self):
                rudisha len(self.seq)

        # Compare Sequence.index() behavior to (list|str).index() behavior
        eleza assert_index_same(seq1, seq2, index_args):
            jaribu:
                expected = seq1.index(*index_args)
            except ValueError:
                ukijumuisha self.assertRaises(ValueError):
                    seq2.index(*index_args)
            isipokua:
                actual = seq2.index(*index_args)
                self.assertEqual(
                    actual, expected, '%r.index%s' % (seq1, index_args))

        kila ty kwenye list, str:
            nativeseq = ty('abracadabra')
            indexes = [-10000, -9999] + list(range(-3, len(nativeseq) + 3))
            seqseq = SequenceSubclass(nativeseq)
            kila letter kwenye set(nativeseq) | {'z'}:
                assert_index_same(nativeseq, seqseq, (letter,))
                kila start kwenye range(-3, len(nativeseq) + 3):
                    assert_index_same(nativeseq, seqseq, (letter, start))
                    kila stop kwenye range(-3, len(nativeseq) + 3):
                        assert_index_same(
                            nativeseq, seqseq, (letter, start, stop))

    eleza test_ByteString(self):
        kila sample kwenye [bytes, bytearray]:
            self.assertIsInstance(sample(), ByteString)
            self.assertKweli(issubclass(sample, ByteString))
        kila sample kwenye [str, list, tuple]:
            self.assertNotIsInstance(sample(), ByteString)
            self.assertUongo(issubclass(sample, ByteString))
        self.assertNotIsInstance(memoryview(b""), ByteString)
        self.assertUongo(issubclass(memoryview, ByteString))

    eleza test_MutableSequence(self):
        kila sample kwenye [tuple, str, bytes]:
            self.assertNotIsInstance(sample(), MutableSequence)
            self.assertUongo(issubclass(sample, MutableSequence))
        kila sample kwenye [list, bytearray, deque]:
            self.assertIsInstance(sample(), MutableSequence)
            self.assertKweli(issubclass(sample, MutableSequence))
        self.assertUongo(issubclass(str, MutableSequence))
        self.validate_abstract_methods(MutableSequence, '__contains__', '__iter__',
            '__len__', '__getitem__', '__setitem__', '__delitem__', 'insert')

    eleza test_MutableSequence_mixins(self):
        # Test the mixins of MutableSequence by creating a minimal concrete
        # kundi inherited kutoka it.
        kundi MutableSequenceSubclass(MutableSequence):
            eleza __init__(self):
                self.lst = []

            eleza __setitem__(self, index, value):
                self.lst[index] = value

            eleza __getitem__(self, index):
                rudisha self.lst[index]

            eleza __len__(self):
                rudisha len(self.lst)

            eleza __delitem__(self, index):
                toa self.lst[index]

            eleza insert(self, index, value):
                self.lst.insert(index, value)

        mss = MutableSequenceSubclass()
        mss.append(0)
        mss.extend((1, 2, 3, 4))
        self.assertEqual(len(mss), 5)
        self.assertEqual(mss[3], 3)
        mss.reverse()
        self.assertEqual(mss[3], 1)
        mss.pop()
        self.assertEqual(len(mss), 4)
        mss.remove(3)
        self.assertEqual(len(mss), 3)
        mss += (10, 20, 30)
        self.assertEqual(len(mss), 6)
        self.assertEqual(mss[-1], 30)
        mss.clear()
        self.assertEqual(len(mss), 0)

        # issue 34427
        # extending self should sio cause infinite loop
        items = 'ABCD'
        mss2 = MutableSequenceSubclass()
        mss2.extend(items + items)
        mss.clear()
        mss.extend(items)
        mss.extend(mss)
        self.assertEqual(len(mss), len(mss2))
        self.assertEqual(list(mss), list(mss2))


################################################################################
### Counter
################################################################################

kundi CounterSubclassWithSetItem(Counter):
    # Test a counter subkundi that overrides __setitem__
    eleza __init__(self, *args, **kwds):
        self.called = Uongo
        Counter.__init__(self, *args, **kwds)
    eleza __setitem__(self, key, value):
        self.called = Kweli
        Counter.__setitem__(self, key, value)

kundi CounterSubclassWithGet(Counter):
    # Test a counter subkundi that overrides get()
    eleza __init__(self, *args, **kwds):
        self.called = Uongo
        Counter.__init__(self, *args, **kwds)
    eleza get(self, key, default):
        self.called = Kweli
        rudisha Counter.get(self, key, default)

kundi TestCounter(unittest.TestCase):

    eleza test_basics(self):
        c = Counter('abcaba')
        self.assertEqual(c, Counter({'a':3 , 'b': 2, 'c': 1}))
        self.assertEqual(c, Counter(a=3, b=2, c=1))
        self.assertIsInstance(c, dict)
        self.assertIsInstance(c, Mapping)
        self.assertKweli(issubclass(Counter, dict))
        self.assertKweli(issubclass(Counter, Mapping))
        self.assertEqual(len(c), 3)
        self.assertEqual(sum(c.values()), 6)
        self.assertEqual(list(c.values()), [3, 2, 1])
        self.assertEqual(list(c.keys()), ['a', 'b', 'c'])
        self.assertEqual(list(c), ['a', 'b', 'c'])
        self.assertEqual(list(c.items()),
                         [('a', 3), ('b', 2), ('c', 1)])
        self.assertEqual(c['b'], 2)
        self.assertEqual(c['z'], 0)
        self.assertEqual(c.__contains__('c'), Kweli)
        self.assertEqual(c.__contains__('z'), Uongo)
        self.assertEqual(c.get('b', 10), 2)
        self.assertEqual(c.get('z', 10), 10)
        self.assertEqual(c, dict(a=3, b=2, c=1))
        self.assertEqual(repr(c), "Counter({'a': 3, 'b': 2, 'c': 1})")
        self.assertEqual(c.most_common(), [('a', 3), ('b', 2), ('c', 1)])
        kila i kwenye range(5):
            self.assertEqual(c.most_common(i),
                             [('a', 3), ('b', 2), ('c', 1)][:i])
        self.assertEqual(''.join(c.elements()), 'aaabbc')
        c['a'] += 1         # increment an existing value
        c['b'] -= 2         # sub existing value to zero
        toa c['c']          # remove an entry
        toa c['c']          # make sure that toa doesn't  ashiria KeyError
        c['d'] -= 2         # sub kutoka a missing value
        c['e'] = -5         # directly assign a missing value
        c['f'] += 4         # add to a missing value
        self.assertEqual(c, dict(a=4, b=0, d=-2, e=-5, f=4))
        self.assertEqual(''.join(c.elements()), 'aaaaffff')
        self.assertEqual(c.pop('f'), 4)
        self.assertNotIn('f', c)
        kila i kwenye range(3):
            elem, cnt = c.popitem()
            self.assertNotIn(elem, c)
        c.clear()
        self.assertEqual(c, {})
        self.assertEqual(repr(c), 'Counter()')
        self.assertRaises(NotImplementedError, Counter.fromkeys, 'abc')
        self.assertRaises(TypeError, hash, c)
        c.update(dict(a=5, b=3))
        c.update(c=1)
        c.update(Counter('a' * 50 + 'b' * 30))
        c.update()          # test case ukijumuisha no args
        c.__init__('a' * 500 + 'b' * 300)
        c.__init__('cdc')
        c.__init__()
        self.assertEqual(c, dict(a=555, b=333, c=3, d=1))
        self.assertEqual(c.setdefault('d', 5), 1)
        self.assertEqual(c['d'], 1)
        self.assertEqual(c.setdefault('e', 5), 5)
        self.assertEqual(c['e'], 5)

    eleza test_init(self):
        self.assertEqual(list(Counter(self=42).items()), [('self', 42)])
        self.assertEqual(list(Counter(iterable=42).items()), [('iterable', 42)])
        self.assertEqual(list(Counter(iterable=Tupu).items()), [('iterable', Tupu)])
        self.assertRaises(TypeError, Counter, 42)
        self.assertRaises(TypeError, Counter, (), ())
        self.assertRaises(TypeError, Counter.__init__)

    eleza test_order_preservation(self):
        # Input order dictates items() order
        self.assertEqual(list(Counter('abracadabra').items()),
               [('a', 5), ('b', 2), ('r', 2), ('c', 1), ('d', 1)])
        # letters ukijumuisha same count:   ^----------^         ^---------^

        # Verify retention of order even when all counts are equal
        self.assertEqual(list(Counter('xyzpdqqdpzyx').items()),
               [('x', 2), ('y', 2), ('z', 2), ('p', 2), ('d', 2), ('q', 2)])

        # Input order dictates elements() order
        self.assertEqual(list(Counter('abracadabra simsalabim').elements()),
                ['a', 'a', 'a', 'a', 'a', 'a', 'a', 'b', 'b', 'b','r',
                 'r', 'c', 'd', ' ', 's', 's', 'i', 'i', 'm', 'm', 'l'])

        # Math operations order first by the order encountered kwenye the left
        # operand na then by the order encountered kwenye the right operand.
        ps = 'aaabbcdddeefggghhijjjkkl'
        qs = 'abbcccdeefffhkkllllmmnno'
        order = {letter: i kila i, letter kwenye enumerate(dict.fromkeys(ps + qs))}
        eleza correctly_ordered(seq):
            'Return true ikiwa the letters occur kwenye the expected order'
            positions = [order[letter] kila letter kwenye seq]
            rudisha positions == sorted(positions)

        p, q = Counter(ps), Counter(qs)
        self.assertKweli(correctly_ordered(+p))
        self.assertKweli(correctly_ordered(-p))
        self.assertKweli(correctly_ordered(p + q))
        self.assertKweli(correctly_ordered(p - q))
        self.assertKweli(correctly_ordered(p | q))
        self.assertKweli(correctly_ordered(p & q))

        p, q = Counter(ps), Counter(qs)
        p += q
        self.assertKweli(correctly_ordered(p))

        p, q = Counter(ps), Counter(qs)
        p -= q
        self.assertKweli(correctly_ordered(p))

        p, q = Counter(ps), Counter(qs)
        p |= q
        self.assertKweli(correctly_ordered(p))

        p, q = Counter(ps), Counter(qs)
        p &= q
        self.assertKweli(correctly_ordered(p))

        p, q = Counter(ps), Counter(qs)
        p.update(q)
        self.assertKweli(correctly_ordered(p))

        p, q = Counter(ps), Counter(qs)
        p.subtract(q)
        self.assertKweli(correctly_ordered(p))

    eleza test_update(self):
        c = Counter()
        c.update(self=42)
        self.assertEqual(list(c.items()), [('self', 42)])
        c = Counter()
        c.update(iterable=42)
        self.assertEqual(list(c.items()), [('iterable', 42)])
        c = Counter()
        c.update(iterable=Tupu)
        self.assertEqual(list(c.items()), [('iterable', Tupu)])
        self.assertRaises(TypeError, Counter().update, 42)
        self.assertRaises(TypeError, Counter().update, {}, {})
        self.assertRaises(TypeError, Counter.update)

    eleza test_copying(self):
        # Check that counters are copyable, deepcopyable, picklable, and
        #have a repr/eval round-trip
        words = Counter('which witch had which witches wrist watch'.split())
        eleza check(dup):
            msg = "\ncopy: %s\nwords: %s" % (dup, words)
            self.assertIsNot(dup, words, msg)
            self.assertEqual(dup, words)
        check(words.copy())
        check(copy.copy(words))
        check(copy.deepcopy(words))
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.subTest(proto=proto):
                check(pickle.loads(pickle.dumps(words, proto)))
        check(eval(repr(words)))
        update_test = Counter()
        update_test.update(words)
        check(update_test)
        check(Counter(words))

    eleza test_copy_subclass(self):
        kundi MyCounter(Counter):
            pass
        c = MyCounter('slartibartfast')
        d = c.copy()
        self.assertEqual(d, c)
        self.assertEqual(len(d), len(c))
        self.assertEqual(type(d), type(c))

    eleza test_conversions(self):
        # Convert to: set, list, dict
        s = 'she sells sea shells by the sea shore'
        self.assertEqual(sorted(Counter(s).elements()), sorted(s))
        self.assertEqual(sorted(Counter(s)), sorted(set(s)))
        self.assertEqual(dict(Counter(s)), dict(Counter(s).items()))
        self.assertEqual(set(Counter(s)), set(s))

    eleza test_invariant_for_the_in_operator(self):
        c = Counter(a=10, b=-2, c=0)
        kila elem kwenye c:
            self.assertKweli(elem kwenye c)
            self.assertIn(elem, c)

    eleza test_multiset_operations(self):
        # Verify that adding a zero counter will strip zeros na negatives
        c = Counter(a=10, b=-2, c=0) + Counter()
        self.assertEqual(dict(c), dict(a=10))

        elements = 'abcd'
        kila i kwenye range(1000):
            # test random pairs of multisets
            p = Counter(dict((elem, randrange(-2,4)) kila elem kwenye elements))
            p.update(e=1, f=-1, g=0)
            q = Counter(dict((elem, randrange(-2,4)) kila elem kwenye elements))
            q.update(h=1, i=-1, j=0)
            kila counterop, numberop kwenye [
                (Counter.__add__, lambda x, y: max(0, x+y)),
                (Counter.__sub__, lambda x, y: max(0, x-y)),
                (Counter.__or__, lambda x, y: max(0,x,y)),
                (Counter.__and__, lambda x, y: max(0, min(x,y))),
            ]:
                result = counterop(p, q)
                kila x kwenye elements:
                    self.assertEqual(numberop(p[x], q[x]), result[x],
                                     (counterop, x, p, q))
                # verify that results exclude non-positive counts
                self.assertKweli(x>0 kila x kwenye result.values())

        elements = 'abcdef'
        kila i kwenye range(100):
            # verify that random multisets ukijumuisha no repeats are exactly like sets
            p = Counter(dict((elem, randrange(0, 2)) kila elem kwenye elements))
            q = Counter(dict((elem, randrange(0, 2)) kila elem kwenye elements))
            kila counterop, setop kwenye [
                (Counter.__sub__, set.__sub__),
                (Counter.__or__, set.__or__),
                (Counter.__and__, set.__and__),
            ]:
                counter_result = counterop(p, q)
                set_result = setop(set(p.elements()), set(q.elements()))
                self.assertEqual(counter_result, dict.fromkeys(set_result, 1))

    eleza test_inplace_operations(self):
        elements = 'abcd'
        kila i kwenye range(1000):
            # test random pairs of multisets
            p = Counter(dict((elem, randrange(-2,4)) kila elem kwenye elements))
            p.update(e=1, f=-1, g=0)
            q = Counter(dict((elem, randrange(-2,4)) kila elem kwenye elements))
            q.update(h=1, i=-1, j=0)
            kila inplace_op, regular_op kwenye [
                (Counter.__iadd__, Counter.__add__),
                (Counter.__isub__, Counter.__sub__),
                (Counter.__ior__, Counter.__or__),
                (Counter.__iand__, Counter.__and__),
            ]:
                c = p.copy()
                c_id = id(c)
                regular_result = regular_op(c, q)
                inplace_result = inplace_op(c, q)
                self.assertEqual(inplace_result, regular_result)
                self.assertEqual(id(inplace_result), c_id)

    eleza test_subtract(self):
        c = Counter(a=-5, b=0, c=5, d=10, e=15,g=40)
        c.subtract(a=1, b=2, c=-3, d=10, e=20, f=30, h=-50)
        self.assertEqual(c, Counter(a=-6, b=-2, c=8, d=0, e=-5, f=-30, g=40, h=50))
        c = Counter(a=-5, b=0, c=5, d=10, e=15,g=40)
        c.subtract(Counter(a=1, b=2, c=-3, d=10, e=20, f=30, h=-50))
        self.assertEqual(c, Counter(a=-6, b=-2, c=8, d=0, e=-5, f=-30, g=40, h=50))
        c = Counter('aaabbcd')
        c.subtract('aaaabbcce')
        self.assertEqual(c, Counter(a=-1, b=0, c=-1, d=1, e=-1))

        c = Counter()
        c.subtract(self=42)
        self.assertEqual(list(c.items()), [('self', -42)])
        c = Counter()
        c.subtract(iterable=42)
        self.assertEqual(list(c.items()), [('iterable', -42)])
        self.assertRaises(TypeError, Counter().subtract, 42)
        self.assertRaises(TypeError, Counter().subtract, {}, {})
        self.assertRaises(TypeError, Counter.subtract)

    eleza test_unary(self):
        c = Counter(a=-5, b=0, c=5, d=10, e=15,g=40)
        self.assertEqual(dict(+c), dict(c=5, d=10, e=15, g=40))
        self.assertEqual(dict(-c), dict(a=5))

    eleza test_repr_nonsortable(self):
        c = Counter(a=2, b=Tupu)
        r = repr(c)
        self.assertIn("'a': 2", r)
        self.assertIn("'b': Tupu", r)

    eleza test_helper_function(self):
        # two paths, one kila real dicts na one kila other mappings
        elems = list('abracadabra')

        d = dict()
        _count_elements(d, elems)
        self.assertEqual(d, {'a': 5, 'r': 2, 'b': 2, 'c': 1, 'd': 1})

        m = OrderedDict()
        _count_elements(m, elems)
        self.assertEqual(m,
             OrderedDict([('a', 5), ('b', 2), ('r', 2), ('c', 1), ('d', 1)]))

        # test fidelity to the pure python version
        c = CounterSubclassWithSetItem('abracadabra')
        self.assertKweli(c.called)
        self.assertEqual(dict(c), {'a': 5, 'b': 2, 'c': 1, 'd': 1, 'r':2 })
        c = CounterSubclassWithGet('abracadabra')
        self.assertKweli(c.called)
        self.assertEqual(dict(c), {'a': 5, 'b': 2, 'c': 1, 'd': 1, 'r':2 })


################################################################################
### Run tests
################################################################################

eleza test_main(verbose=Tupu):
    NamedTupleDocs = doctest.DocTestSuite(module=collections)
    test_classes = [TestNamedTuple, NamedTupleDocs, TestOneTrickPonyABCs,
                    TestCollectionABCs, TestCounter, TestChainMap,
                    TestUserObjects,
                    ]
    support.run_unittest(*test_classes)
    support.run_doctest(collections, verbose)


ikiwa __name__ == "__main__":
    test_main(verbose=Kweli)
