# -*- coding: utf-8 -*-

agiza collections
agiza io
agiza itertools
agiza pprint
agiza random
agiza test.support
agiza test.test_set
agiza types
agiza unittest

# list, tuple na dict subclasses that do ama don't overwrite __repr__
kundi list2(list):
    pita

kundi list3(list):
    eleza __repr__(self):
        rudisha list.__repr__(self)

kundi tuple2(tuple):
    pita

kundi tuple3(tuple):
    eleza __repr__(self):
        rudisha tuple.__repr__(self)

kundi set2(set):
    pita

kundi set3(set):
    eleza __repr__(self):
        rudisha set.__repr__(self)

kundi frozenset2(frozenset):
    pita

kundi frozenset3(frozenset):
    eleza __repr__(self):
        rudisha frozenset.__repr__(self)

kundi dict2(dict):
    pita

kundi dict3(dict):
    eleza __repr__(self):
        rudisha dict.__repr__(self)

kundi Unorderable:
    eleza __repr__(self):
        rudisha str(id(self))

# Class Orderable ni orderable ukijumuisha any type
kundi Orderable:
    eleza __init__(self, hash):
        self._hash = hash
    eleza __lt__(self, other):
        rudisha Uongo
    eleza __gt__(self, other):
        rudisha self != other
    eleza __le__(self, other):
        rudisha self == other
    eleza __ge__(self, other):
        rudisha Kweli
    eleza __eq__(self, other):
        rudisha self ni other
    eleza __ne__(self, other):
        rudisha self ni sio other
    eleza __hash__(self):
        rudisha self._hash

kundi QueryTestCase(unittest.TestCase):

    eleza setUp(self):
        self.a = list(range(100))
        self.b = list(range(200))
        self.a[-12] = self.b

    eleza test_init(self):
        pp = pprint.PrettyPrinter()
        pp = pprint.PrettyPrinter(indent=4, width=40, depth=5,
                                  stream=io.StringIO(), compact=Kweli)
        pp = pprint.PrettyPrinter(4, 40, 5, io.StringIO())
        pp = pprint.PrettyPrinter(sort_dicts=Uongo)
        ukijumuisha self.assertRaises(TypeError):
            pp = pprint.PrettyPrinter(4, 40, 5, io.StringIO(), Kweli)
        self.assertRaises(ValueError, pprint.PrettyPrinter, indent=-1)
        self.assertRaises(ValueError, pprint.PrettyPrinter, depth=0)
        self.assertRaises(ValueError, pprint.PrettyPrinter, depth=-1)
        self.assertRaises(ValueError, pprint.PrettyPrinter, width=0)

    eleza test_basic(self):
        # Verify .isrecursive() na .isreadable() w/o recursion
        pp = pprint.PrettyPrinter()
        kila safe kwenye (2, 2.0, 2j, "abc", [3], (2,2), {3: 3}, b"def",
                     bytearray(b"ghi"), Kweli, Uongo, Tupu, ...,
                     self.a, self.b):
            # module-level convenience functions
            self.assertUongo(pprint.isrecursive(safe),
                             "expected sio isrecursive kila %r" % (safe,))
            self.assertKweli(pprint.isreadable(safe),
                            "expected isreadable kila %r" % (safe,))
            # PrettyPrinter methods
            self.assertUongo(pp.isrecursive(safe),
                             "expected sio isrecursive kila %r" % (safe,))
            self.assertKweli(pp.isreadable(safe),
                            "expected isreadable kila %r" % (safe,))

    eleza test_knotted(self):
        # Verify .isrecursive() na .isreadable() w/ recursion
        # Tie a knot.
        self.b[67] = self.a
        # Messy dict.
        self.d = {}
        self.d[0] = self.d[1] = self.d[2] = self.d

        pp = pprint.PrettyPrinter()

        kila icky kwenye self.a, self.b, self.d, (self.d, self.d):
            self.assertKweli(pprint.isrecursive(icky), "expected isrecursive")
            self.assertUongo(pprint.isreadable(icky), "expected sio isreadable")
            self.assertKweli(pp.isrecursive(icky), "expected isrecursive")
            self.assertUongo(pp.isreadable(icky), "expected sio isreadable")

        # Break the cycles.
        self.d.clear()
        toa self.a[:]
        toa self.b[:]

        kila safe kwenye self.a, self.b, self.d, (self.d, self.d):
            # module-level convenience functions
            self.assertUongo(pprint.isrecursive(safe),
                             "expected sio isrecursive kila %r" % (safe,))
            self.assertKweli(pprint.isreadable(safe),
                            "expected isreadable kila %r" % (safe,))
            # PrettyPrinter methods
            self.assertUongo(pp.isrecursive(safe),
                             "expected sio isrecursive kila %r" % (safe,))
            self.assertKweli(pp.isreadable(safe),
                            "expected isreadable kila %r" % (safe,))

    eleza test_unreadable(self):
        # Not recursive but sio readable anyway
        pp = pprint.PrettyPrinter()
        kila unreadable kwenye type(3), pprint, pprint.isrecursive:
            # module-level convenience functions
            self.assertUongo(pprint.isrecursive(unreadable),
                             "expected sio isrecursive kila %r" % (unreadable,))
            self.assertUongo(pprint.isreadable(unreadable),
                             "expected sio isreadable kila %r" % (unreadable,))
            # PrettyPrinter methods
            self.assertUongo(pp.isrecursive(unreadable),
                             "expected sio isrecursive kila %r" % (unreadable,))
            self.assertUongo(pp.isreadable(unreadable),
                             "expected sio isreadable kila %r" % (unreadable,))

    eleza test_same_as_repr(self):
        # Simple objects, small containers na classes that overwrite __repr__
        # For those the result should be the same kama repr().
        # Ahem.  The docs don't say anything about that -- this appears to
        # be testing an implementation quirk.  Starting kwenye Python 2.5, it's
        # sio true kila dicts:  pprint always sorts dicts by key now; before,
        # it sorted a dict display ikiwa na only ikiwa the display required
        # multiple lines.  For that reason, dicts ukijumuisha more than one element
        # aren't tested here.
        kila simple kwenye (0, 0, 0+0j, 0.0, "", b"", bytearray(),
                       (), tuple2(), tuple3(),
                       [], list2(), list3(),
                       set(), set2(), set3(),
                       frozenset(), frozenset2(), frozenset3(),
                       {}, dict2(), dict3(),
                       self.assertKweli, pprint,
                       -6, -6, -6-6j, -1.5, "x", b"x", bytearray(b"x"),
                       (3,), [3], {3: 6},
                       (1,2), [3,4], {5: 6},
                       tuple2((1,2)), tuple3((1,2)), tuple3(range(100)),
                       [3,4], list2([3,4]), list3([3,4]), list3(range(100)),
                       set({7}), set2({7}), set3({7}),
                       frozenset({8}), frozenset2({8}), frozenset3({8}),
                       dict2({5: 6}), dict3({5: 6}),
                       range(10, -11, -1),
                       Kweli, Uongo, Tupu, ...,
                      ):
            native = repr(simple)
            self.assertEqual(pprint.pformat(simple), native)
            self.assertEqual(pprint.pformat(simple, width=1, indent=0)
                             .replace('\n', ' '), native)
            self.assertEqual(pprint.saferepr(simple), native)

    eleza test_basic_line_wrap(self):
        # verify basic line-wrapping operation
        o = {'RPM_cal': 0,
             'RPM_cal2': 48059,
             'Speed_cal': 0,
             'controldesk_runtime_us': 0,
             'main_code_runtime_us': 0,
             'read_io_runtime_us': 0,
             'write_io_runtime_us': 43690}
        exp = """\
{'RPM_cal': 0,
 'RPM_cal2': 48059,
 'Speed_cal': 0,
 'controldesk_runtime_us': 0,
 'main_code_runtime_us': 0,
 'read_io_runtime_us': 0,
 'write_io_runtime_us': 43690}"""
        kila type kwenye [dict, dict2]:
            self.assertEqual(pprint.pformat(type(o)), exp)

        o = range(100)
        exp = '[%s]' % ',\n '.join(map(str, o))
        kila type kwenye [list, list2]:
            self.assertEqual(pprint.pformat(type(o)), exp)

        o = tuple(range(100))
        exp = '(%s)' % ',\n '.join(map(str, o))
        kila type kwenye [tuple, tuple2]:
            self.assertEqual(pprint.pformat(type(o)), exp)

        # indent parameter
        o = range(100)
        exp = '[   %s]' % ',\n    '.join(map(str, o))
        kila type kwenye [list, list2]:
            self.assertEqual(pprint.pformat(type(o), indent=4), exp)

    eleza test_nested_indentations(self):
        o1 = list(range(10))
        o2 = dict(first=1, second=2, third=3)
        o = [o1, o2]
        expected = """\
[   [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    {'first': 1, 'second': 2, 'third': 3}]"""
        self.assertEqual(pprint.pformat(o, indent=4, width=42), expected)
        expected = """\
[   [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    {   'first': 1,
        'second': 2,
        'third': 3}]"""
        self.assertEqual(pprint.pformat(o, indent=4, width=41), expected)

    eleza test_width(self):
        expected = """\
[[[[[[1, 2, 3],
     '1 2']]]],
 {1: [1, 2, 3],
  2: [12, 34]},
 'abc eleza ghi',
 ('ab cd ef',),
 set2({1, 23}),
 [[[[[1, 2, 3],
     '1 2']]]]]"""
        o = eval(expected)
        self.assertEqual(pprint.pformat(o, width=15), expected)
        self.assertEqual(pprint.pformat(o, width=16), expected)
        self.assertEqual(pprint.pformat(o, width=25), expected)
        self.assertEqual(pprint.pformat(o, width=14), """\
[[[[[[1,
      2,
      3],
     '1 '
     '2']]]],
 {1: [1,
      2,
      3],
  2: [12,
      34]},
 'abc eleza '
 'ghi',
 ('ab cd '
  'ef',),
 set2({1,
       23}),
 [[[[[1,
      2,
      3],
     '1 '
     '2']]]]]""")

    eleza test_sorted_dict(self):
        # Starting kwenye Python 2.5, pprint sorts dict displays by key regardless
        # of how small the dictionary may be.
        # Before the change, on 32-bit Windows pformat() gave order
        # 'a', 'c', 'b' here, so this test failed.
        d = {'a': 1, 'b': 1, 'c': 1}
        self.assertEqual(pprint.pformat(d), "{'a': 1, 'b': 1, 'c': 1}")
        self.assertEqual(pprint.pformat([d, d]),
            "[{'a': 1, 'b': 1, 'c': 1}, {'a': 1, 'b': 1, 'c': 1}]")

        # The next one ni kind of goofy.  The sorted order depends on the
        # alphabetic order of type names:  "int" < "str" < "tuple".  Before
        # Python 2.5, this was kwenye the test_same_as_repr() test.  It's worth
        # keeping around kila now because it's one of few tests of pprint
        # against a crazy mix of types.
        self.assertEqual(pprint.pformat({"xy\tab\n": (3,), 5: [[]], (): {}}),
            r"{5: [[]], 'xy\tab\n': (3,), (): {}}")

    eleza test_sort_dict(self):
        d = dict.fromkeys('cba')
        self.assertEqual(pprint.pformat(d, sort_dicts=Uongo), "{'c': Tupu, 'b': Tupu, 'a': Tupu}")
        self.assertEqual(pprint.pformat([d, d], sort_dicts=Uongo),
            "[{'c': Tupu, 'b': Tupu, 'a': Tupu}, {'c': Tupu, 'b': Tupu, 'a': Tupu}]")

    eleza test_ordered_dict(self):
        d = collections.OrderedDict()
        self.assertEqual(pprint.pformat(d, width=1), 'OrderedDict()')
        d = collections.OrderedDict([])
        self.assertEqual(pprint.pformat(d, width=1), 'OrderedDict()')
        words = 'the quick brown fox jumped over a lazy dog'.split()
        d = collections.OrderedDict(zip(words, itertools.count()))
        self.assertEqual(pprint.pformat(d),
"""\
OrderedDict([('the', 0),
             ('quick', 1),
             ('brown', 2),
             ('fox', 3),
             ('jumped', 4),
             ('over', 5),
             ('a', 6),
             ('lazy', 7),
             ('dog', 8)])""")

    eleza test_mapping_proxy(self):
        words = 'the quick brown fox jumped over a lazy dog'.split()
        d = dict(zip(words, itertools.count()))
        m = types.MappingProxyType(d)
        self.assertEqual(pprint.pformat(m), """\
mappingproxy({'a': 6,
              'brown': 2,
              'dog': 8,
              'fox': 3,
              'jumped': 4,
              'lazy': 7,
              'over': 5,
              'quick': 1,
              'the': 0})""")
        d = collections.OrderedDict(zip(words, itertools.count()))
        m = types.MappingProxyType(d)
        self.assertEqual(pprint.pformat(m), """\
mappingproxy(OrderedDict([('the', 0),
                          ('quick', 1),
                          ('brown', 2),
                          ('fox', 3),
                          ('jumped', 4),
                          ('over', 5),
                          ('a', 6),
                          ('lazy', 7),
                          ('dog', 8)]))""")

    eleza test_subclassing(self):
        o = {'names ukijumuisha spaces': 'should be presented using repr()',
             'others.should.not.be': 'like.this'}
        exp = """\
{'names ukijumuisha spaces': 'should be presented using repr()',
 others.should.not.be: like.this}"""
        self.assertEqual(DottedPrettyPrinter().pformat(o), exp)

    eleza test_set_reprs(self):
        self.assertEqual(pprint.pformat(set()), 'set()')
        self.assertEqual(pprint.pformat(set(range(3))), '{0, 1, 2}')
        self.assertEqual(pprint.pformat(set(range(7)), width=20), '''\
{0,
 1,
 2,
 3,
 4,
 5,
 6}''')
        self.assertEqual(pprint.pformat(set2(range(7)), width=20), '''\
set2({0,
      1,
      2,
      3,
      4,
      5,
      6})''')
        self.assertEqual(pprint.pformat(set3(range(7)), width=20),
                         'set3({0, 1, 2, 3, 4, 5, 6})')

        self.assertEqual(pprint.pformat(frozenset()), 'frozenset()')
        self.assertEqual(pprint.pformat(frozenset(range(3))),
                         'frozenset({0, 1, 2})')
        self.assertEqual(pprint.pformat(frozenset(range(7)), width=20), '''\
frozenset({0,
           1,
           2,
           3,
           4,
           5,
           6})''')
        self.assertEqual(pprint.pformat(frozenset2(range(7)), width=20), '''\
frozenset2({0,
            1,
            2,
            3,
            4,
            5,
            6})''')
        self.assertEqual(pprint.pformat(frozenset3(range(7)), width=20),
                         'frozenset3({0, 1, 2, 3, 4, 5, 6})')

    @unittest.expectedFailure
    #See http://bugs.python.org/issue13907
    @test.support.cpython_only
    eleza test_set_of_sets_reprs(self):
        # This test creates a complex arrangement of frozensets na
        # compares the pretty-printed repr against a string hard-coded in
        # the test.  The hard-coded repr depends on the sort order of
        # frozensets.
        #
        # However, kama the docs point out: "Since sets only define
        # partial ordering (subset relationships), the output of the
        # list.sort() method ni undefined kila lists of sets."
        #
        # In a nutshell, the test assumes frozenset({0}) will always
        # sort before frozenset({1}), but:
        #
        # >>> frozenset({0}) < frozenset({1})
        # Uongo
        # >>> frozenset({1}) < frozenset({0})
        # Uongo
        #
        # Consequently, this test ni fragile na
        # implementation-dependent.  Small changes to Python's sort
        # algorithm cause the test to fail when it should pita.
        # XXX Or changes to the dictionary implmentation...

        cube_repr_tgt = """\
{frozenset(): frozenset({frozenset({2}), frozenset({0}), frozenset({1})}),
 frozenset({0}): frozenset({frozenset(),
                            frozenset({0, 2}),
                            frozenset({0, 1})}),
 frozenset({1}): frozenset({frozenset(),
                            frozenset({1, 2}),
                            frozenset({0, 1})}),
 frozenset({2}): frozenset({frozenset(),
                            frozenset({1, 2}),
                            frozenset({0, 2})}),
 frozenset({1, 2}): frozenset({frozenset({2}),
                               frozenset({1}),
                               frozenset({0, 1, 2})}),
 frozenset({0, 2}): frozenset({frozenset({2}),
                               frozenset({0}),
                               frozenset({0, 1, 2})}),
 frozenset({0, 1}): frozenset({frozenset({0}),
                               frozenset({1}),
                               frozenset({0, 1, 2})}),
 frozenset({0, 1, 2}): frozenset({frozenset({1, 2}),
                                  frozenset({0, 2}),
                                  frozenset({0, 1})})}"""
        cube = test.test_set.cube(3)
        self.assertEqual(pprint.pformat(cube), cube_repr_tgt)
        cubo_repr_tgt = """\
{frozenset({frozenset({0, 2}), frozenset({0})}): frozenset({frozenset({frozenset({0,
                                                                                  2}),
                                                                       frozenset({0,
                                                                                  1,
                                                                                  2})}),
                                                            frozenset({frozenset({0}),
                                                                       frozenset({0,
                                                                                  1})}),
                                                            frozenset({frozenset(),
                                                                       frozenset({0})}),
                                                            frozenset({frozenset({2}),
                                                                       frozenset({0,
                                                                                  2})})}),
 frozenset({frozenset({0, 1}), frozenset({1})}): frozenset({frozenset({frozenset({0,
                                                                                  1}),
                                                                       frozenset({0,
                                                                                  1,
                                                                                  2})}),
                                                            frozenset({frozenset({0}),
                                                                       frozenset({0,
                                                                                  1})}),
                                                            frozenset({frozenset({1}),
                                                                       frozenset({1,
                                                                                  2})}),
                                                            frozenset({frozenset(),
                                                                       frozenset({1})})}),
 frozenset({frozenset({1, 2}), frozenset({1})}): frozenset({frozenset({frozenset({1,
                                                                                  2}),
                                                                       frozenset({0,
                                                                                  1,
                                                                                  2})}),
                                                            frozenset({frozenset({2}),
                                                                       frozenset({1,
                                                                                  2})}),
                                                            frozenset({frozenset(),
                                                                       frozenset({1})}),
                                                            frozenset({frozenset({1}),
                                                                       frozenset({0,
                                                                                  1})})}),
 frozenset({frozenset({1, 2}), frozenset({2})}): frozenset({frozenset({frozenset({1,
                                                                                  2}),
                                                                       frozenset({0,
                                                                                  1,
                                                                                  2})}),
                                                            frozenset({frozenset({1}),
                                                                       frozenset({1,
                                                                                  2})}),
                                                            frozenset({frozenset({2}),
                                                                       frozenset({0,
                                                                                  2})}),
                                                            frozenset({frozenset(),
                                                                       frozenset({2})})}),
 frozenset({frozenset(), frozenset({0})}): frozenset({frozenset({frozenset({0}),
                                                                 frozenset({0,
                                                                            1})}),
                                                      frozenset({frozenset({0}),
                                                                 frozenset({0,
                                                                            2})}),
                                                      frozenset({frozenset(),
                                                                 frozenset({1})}),
                                                      frozenset({frozenset(),
                                                                 frozenset({2})})}),
 frozenset({frozenset(), frozenset({1})}): frozenset({frozenset({frozenset(),
                                                                 frozenset({0})}),
                                                      frozenset({frozenset({1}),
                                                                 frozenset({1,
                                                                            2})}),
                                                      frozenset({frozenset(),
                                                                 frozenset({2})}),
                                                      frozenset({frozenset({1}),
                                                                 frozenset({0,
                                                                            1})})}),
 frozenset({frozenset({2}), frozenset()}): frozenset({frozenset({frozenset({2}),
                                                                 frozenset({1,
                                                                            2})}),
                                                      frozenset({frozenset(),
                                                                 frozenset({0})}),
                                                      frozenset({frozenset(),
                                                                 frozenset({1})}),
                                                      frozenset({frozenset({2}),
                                                                 frozenset({0,
                                                                            2})})}),
 frozenset({frozenset({0, 1, 2}), frozenset({0, 1})}): frozenset({frozenset({frozenset({1,
                                                                                        2}),
                                                                             frozenset({0,
                                                                                        1,
                                                                                        2})}),
                                                                  frozenset({frozenset({0,
                                                                                        2}),
                                                                             frozenset({0,
                                                                                        1,
                                                                                        2})}),
                                                                  frozenset({frozenset({0}),
                                                                             frozenset({0,
                                                                                        1})}),
                                                                  frozenset({frozenset({1}),
                                                                             frozenset({0,
                                                                                        1})})}),
 frozenset({frozenset({0}), frozenset({0, 1})}): frozenset({frozenset({frozenset(),
                                                                       frozenset({0})}),
                                                            frozenset({frozenset({0,
                                                                                  1}),
                                                                       frozenset({0,
                                                                                  1,
                                                                                  2})}),
                                                            frozenset({frozenset({0}),
                                                                       frozenset({0,
                                                                                  2})}),
                                                            frozenset({frozenset({1}),
                                                                       frozenset({0,
                                                                                  1})})}),
 frozenset({frozenset({2}), frozenset({0, 2})}): frozenset({frozenset({frozenset({0,
                                                                                  2}),
                                                                       frozenset({0,
                                                                                  1,
                                                                                  2})}),
                                                            frozenset({frozenset({2}),
                                                                       frozenset({1,
                                                                                  2})}),
                                                            frozenset({frozenset({0}),
                                                                       frozenset({0,
                                                                                  2})}),
                                                            frozenset({frozenset(),
                                                                       frozenset({2})})}),
 frozenset({frozenset({0, 1, 2}), frozenset({0, 2})}): frozenset({frozenset({frozenset({1,
                                                                                        2}),
                                                                             frozenset({0,
                                                                                        1,
                                                                                        2})}),
                                                                  frozenset({frozenset({0,
                                                                                        1}),
                                                                             frozenset({0,
                                                                                        1,
                                                                                        2})}),
                                                                  frozenset({frozenset({0}),
                                                                             frozenset({0,
                                                                                        2})}),
                                                                  frozenset({frozenset({2}),
                                                                             frozenset({0,
                                                                                        2})})}),
 frozenset({frozenset({1, 2}), frozenset({0, 1, 2})}): frozenset({frozenset({frozenset({0,
                                                                                        2}),
                                                                             frozenset({0,
                                                                                        1,
                                                                                        2})}),
                                                                  frozenset({frozenset({0,
                                                                                        1}),
                                                                             frozenset({0,
                                                                                        1,
                                                                                        2})}),
                                                                  frozenset({frozenset({2}),
                                                                             frozenset({1,
                                                                                        2})}),
                                                                  frozenset({frozenset({1}),
                                                                             frozenset({1,
                                                                                        2})})})}"""

        cubo = test.test_set.linegraph(cube)
        self.assertEqual(pprint.pformat(cubo), cubo_repr_tgt)

    eleza test_depth(self):
        nested_tuple = (1, (2, (3, (4, (5, 6)))))
        nested_dict = {1: {2: {3: {4: {5: {6: 6}}}}}}
        nested_list = [1, [2, [3, [4, [5, [6, []]]]]]]
        self.assertEqual(pprint.pformat(nested_tuple), repr(nested_tuple))
        self.assertEqual(pprint.pformat(nested_dict), repr(nested_dict))
        self.assertEqual(pprint.pformat(nested_list), repr(nested_list))

        lv1_tuple = '(1, (...))'
        lv1_dict = '{1: {...}}'
        lv1_list = '[1, [...]]'
        self.assertEqual(pprint.pformat(nested_tuple, depth=1), lv1_tuple)
        self.assertEqual(pprint.pformat(nested_dict, depth=1), lv1_dict)
        self.assertEqual(pprint.pformat(nested_list, depth=1), lv1_list)

    eleza test_sort_unorderable_values(self):
        # Issue 3976:  sorted pprints fail kila unorderable values.
        n = 20
        keys = [Unorderable() kila i kwenye range(n)]
        random.shuffle(keys)
        skeys = sorted(keys, key=id)
        clean = lambda s: s.replace(' ', '').replace('\n','')

        self.assertEqual(clean(pprint.pformat(set(keys))),
            '{' + ','.join(map(repr, skeys)) + '}')
        self.assertEqual(clean(pprint.pformat(frozenset(keys))),
            'frozenset({' + ','.join(map(repr, skeys)) + '})')
        self.assertEqual(clean(pprint.pformat(dict.fromkeys(keys))),
            '{' + ','.join('%r:Tupu' % k kila k kwenye skeys) + '}')

        # Issue 10017: TypeError on user-defined types kama dict keys.
        self.assertEqual(pprint.pformat({Unorderable: 0, 1: 0}),
                         '{1: 0, ' + repr(Unorderable) +': 0}')

        # Issue 14998: TypeError on tuples ukijumuisha TupuTypes kama dict keys.
        keys = [(1,), (Tupu,)]
        self.assertEqual(pprint.pformat(dict.fromkeys(keys, 0)),
                         '{%r: 0, %r: 0}' % tuple(sorted(keys, key=id)))

    eleza test_sort_orderable_and_unorderable_values(self):
        # Issue 22721:  sorted pprints ni sio stable
        a = Unorderable()
        b = Orderable(hash(a))  # should have the same hash value
        # self-test
        self.assertLess(a, b)
        self.assertLess(str(type(b)), str(type(a)))
        self.assertEqual(sorted([b, a]), [a, b])
        self.assertEqual(sorted([a, b]), [a, b])
        # set
        self.assertEqual(pprint.pformat(set([b, a]), width=1),
                         '{%r,\n %r}' % (a, b))
        self.assertEqual(pprint.pformat(set([a, b]), width=1),
                         '{%r,\n %r}' % (a, b))
        # dict
        self.assertEqual(pprint.pformat(dict.fromkeys([b, a]), width=1),
                         '{%r: Tupu,\n %r: Tupu}' % (a, b))
        self.assertEqual(pprint.pformat(dict.fromkeys([a, b]), width=1),
                         '{%r: Tupu,\n %r: Tupu}' % (a, b))

    eleza test_str_wrap(self):
        # pprint tries to wrap strings intelligently
        fox = 'the quick brown fox jumped over a lazy dog'
        self.assertEqual(pprint.pformat(fox, width=19), """\
('the quick brown '
 'fox jumped over '
 'a lazy dog')""")
        self.assertEqual(pprint.pformat({'a': 1, 'b': fox, 'c': 2},
                                        width=25), """\
{'a': 1,
 'b': 'the quick brown '
      'fox jumped over '
      'a lazy dog',
 'c': 2}""")
        # With some special characters
        # - \n always triggers a new line kwenye the pprint
        # - \t na \n are escaped
        # - non-ASCII ni allowed
        # - an apostrophe doesn't disrupt the pprint
        special = "Portons dix bons \"whiskys\"\nà l'avocat goujat\t qui fumait au zoo"
        self.assertEqual(pprint.pformat(special, width=68), repr(special))
        self.assertEqual(pprint.pformat(special, width=31), """\
('Portons dix bons "whiskys"\\n'
 "à l'avocat goujat\\t qui "
 'fumait au zoo')""")
        self.assertEqual(pprint.pformat(special, width=20), """\
('Portons dix bons '
 '"whiskys"\\n'
 "à l'avocat "
 'goujat\\t qui '
 'fumait au zoo')""")
        self.assertEqual(pprint.pformat([[[[[special]]]]], width=35), """\
[[[[['Portons dix bons "whiskys"\\n'
     "à l'avocat goujat\\t qui "
     'fumait au zoo']]]]]""")
        self.assertEqual(pprint.pformat([[[[[special]]]]], width=25), """\
[[[[['Portons dix bons '
     '"whiskys"\\n'
     "à l'avocat "
     'goujat\\t qui '
     'fumait au zoo']]]]]""")
        self.assertEqual(pprint.pformat([[[[[special]]]]], width=23), """\
[[[[['Portons dix '
     'bons "whiskys"\\n'
     "à l'avocat "
     'goujat\\t qui '
     'fumait au '
     'zoo']]]]]""")
        # An unwrappable string ni formatted kama its repr
        unwrappable = "x" * 100
        self.assertEqual(pprint.pformat(unwrappable, width=80), repr(unwrappable))
        self.assertEqual(pprint.pformat(''), "''")
        # Check that the pprint ni a usable repr
        special *= 10
        kila width kwenye range(3, 40):
            formatted = pprint.pformat(special, width=width)
            self.assertEqual(eval(formatted), special)
            formatted = pprint.pformat([special] * 2, width=width)
            self.assertEqual(eval(formatted), [special] * 2)

    eleza test_compact(self):
        o = ([list(range(i * i)) kila i kwenye range(5)] +
             [list(range(i)) kila i kwenye range(6)])
        expected = """\
[[], [0], [0, 1, 2, 3],
 [0, 1, 2, 3, 4, 5, 6, 7, 8],
 [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
  14, 15],
 [], [0], [0, 1], [0, 1, 2], [0, 1, 2, 3],
 [0, 1, 2, 3, 4]]"""
        self.assertEqual(pprint.pformat(o, width=47, compact=Kweli), expected)

    eleza test_compact_width(self):
        levels = 20
        number = 10
        o = [0] * number
        kila i kwenye range(levels - 1):
            o = [o]
        kila w kwenye range(levels * 2 + 1, levels + 3 * number - 1):
            lines = pprint.pformat(o, width=w, compact=Kweli).splitlines()
            maxwidth = max(map(len, lines))
            self.assertLessEqual(maxwidth, w)
            self.assertGreater(maxwidth, w - 3)

    eleza test_bytes_wrap(self):
        self.assertEqual(pprint.pformat(b'', width=1), "b''")
        self.assertEqual(pprint.pformat(b'abcd', width=1), "b'abcd'")
        letters = b'abcdefghijklmnopqrstuvwxyz'
        self.assertEqual(pprint.pformat(letters, width=29), repr(letters))
        self.assertEqual(pprint.pformat(letters, width=19), """\
(b'abcdefghijkl'
 b'mnopqrstuvwxyz')""")
        self.assertEqual(pprint.pformat(letters, width=18), """\
(b'abcdefghijkl'
 b'mnopqrstuvwx'
 b'yz')""")
        self.assertEqual(pprint.pformat(letters, width=16), """\
(b'abcdefghijkl'
 b'mnopqrstuvwx'
 b'yz')""")
        special = bytes(range(16))
        self.assertEqual(pprint.pformat(special, width=61), repr(special))
        self.assertEqual(pprint.pformat(special, width=48), """\
(b'\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\t\\n\\x0b'
 b'\\x0c\\r\\x0e\\x0f')""")
        self.assertEqual(pprint.pformat(special, width=32), """\
(b'\\x00\\x01\\x02\\x03'
 b'\\x04\\x05\\x06\\x07\\x08\\t\\n\\x0b'
 b'\\x0c\\r\\x0e\\x0f')""")
        self.assertEqual(pprint.pformat(special, width=1), """\
(b'\\x00\\x01\\x02\\x03'
 b'\\x04\\x05\\x06\\x07'
 b'\\x08\\t\\n\\x0b'
 b'\\x0c\\r\\x0e\\x0f')""")
        self.assertEqual(pprint.pformat({'a': 1, 'b': letters, 'c': 2},
                                        width=21), """\
{'a': 1,
 'b': b'abcdefghijkl'
      b'mnopqrstuvwx'
      b'yz',
 'c': 2}""")
        self.assertEqual(pprint.pformat({'a': 1, 'b': letters, 'c': 2},
                                        width=20), """\
{'a': 1,
 'b': b'abcdefgh'
      b'ijklmnop'
      b'qrstuvwxyz',
 'c': 2}""")
        self.assertEqual(pprint.pformat([[[[[[letters]]]]]], width=25), """\
[[[[[[b'abcdefghijklmnop'
      b'qrstuvwxyz']]]]]]""")
        self.assertEqual(pprint.pformat([[[[[[special]]]]]], width=41), """\
[[[[[[b'\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07'
      b'\\x08\\t\\n\\x0b\\x0c\\r\\x0e\\x0f']]]]]]""")
        # Check that the pprint ni a usable repr
        kila width kwenye range(1, 64):
            formatted = pprint.pformat(special, width=width)
            self.assertEqual(eval(formatted), special)
            formatted = pprint.pformat([special] * 2, width=width)
            self.assertEqual(eval(formatted), [special] * 2)

    eleza test_bytearray_wrap(self):
        self.assertEqual(pprint.pformat(bytearray(), width=1), "bytearray(b'')")
        letters = bytearray(b'abcdefghijklmnopqrstuvwxyz')
        self.assertEqual(pprint.pformat(letters, width=40), repr(letters))
        self.assertEqual(pprint.pformat(letters, width=28), """\
bytearray(b'abcdefghijkl'
          b'mnopqrstuvwxyz')""")
        self.assertEqual(pprint.pformat(letters, width=27), """\
bytearray(b'abcdefghijkl'
          b'mnopqrstuvwx'
          b'yz')""")
        self.assertEqual(pprint.pformat(letters, width=25), """\
bytearray(b'abcdefghijkl'
          b'mnopqrstuvwx'
          b'yz')""")
        special = bytearray(range(16))
        self.assertEqual(pprint.pformat(special, width=72), repr(special))
        self.assertEqual(pprint.pformat(special, width=57), """\
bytearray(b'\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\t\\n\\x0b'
          b'\\x0c\\r\\x0e\\x0f')""")
        self.assertEqual(pprint.pformat(special, width=41), """\
bytearray(b'\\x00\\x01\\x02\\x03'
          b'\\x04\\x05\\x06\\x07\\x08\\t\\n\\x0b'
          b'\\x0c\\r\\x0e\\x0f')""")
        self.assertEqual(pprint.pformat(special, width=1), """\
bytearray(b'\\x00\\x01\\x02\\x03'
          b'\\x04\\x05\\x06\\x07'
          b'\\x08\\t\\n\\x0b'
          b'\\x0c\\r\\x0e\\x0f')""")
        self.assertEqual(pprint.pformat({'a': 1, 'b': letters, 'c': 2},
                                        width=31), """\
{'a': 1,
 'b': bytearray(b'abcdefghijkl'
                b'mnopqrstuvwx'
                b'yz'),
 'c': 2}""")
        self.assertEqual(pprint.pformat([[[[[letters]]]]], width=37), """\
[[[[[bytearray(b'abcdefghijklmnop'
               b'qrstuvwxyz')]]]]]""")
        self.assertEqual(pprint.pformat([[[[[special]]]]], width=50), """\
[[[[[bytearray(b'\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07'
               b'\\x08\\t\\n\\x0b\\x0c\\r\\x0e\\x0f')]]]]]""")

    eleza test_default_dict(self):
        d = collections.defaultdict(int)
        self.assertEqual(pprint.pformat(d, width=1), "defaultdict(<kundi 'int'>, {})")
        words = 'the quick brown fox jumped over a lazy dog'.split()
        d = collections.defaultdict(int, zip(words, itertools.count()))
        self.assertEqual(pprint.pformat(d),
"""\
defaultdict(<kundi 'int'>,
            {'a': 6,
             'brown': 2,
             'dog': 8,
             'fox': 3,
             'jumped': 4,
             'lazy': 7,
             'over': 5,
             'quick': 1,
             'the': 0})""")

    eleza test_counter(self):
        d = collections.Counter()
        self.assertEqual(pprint.pformat(d, width=1), "Counter()")
        d = collections.Counter('senselessness')
        self.assertEqual(pprint.pformat(d, width=40),
"""\
Counter({'s': 6,
         'e': 4,
         'n': 2,
         'l': 1})""")

    eleza test_chainmap(self):
        d = collections.ChainMap()
        self.assertEqual(pprint.pformat(d, width=1), "ChainMap({})")
        words = 'the quick brown fox jumped over a lazy dog'.split()
        items = list(zip(words, itertools.count()))
        d = collections.ChainMap(dict(items))
        self.assertEqual(pprint.pformat(d),
"""\
ChainMap({'a': 6,
          'brown': 2,
          'dog': 8,
          'fox': 3,
          'jumped': 4,
          'lazy': 7,
          'over': 5,
          'quick': 1,
          'the': 0})""")
        d = collections.ChainMap(dict(items), collections.OrderedDict(items))
        self.assertEqual(pprint.pformat(d),
"""\
ChainMap({'a': 6,
          'brown': 2,
          'dog': 8,
          'fox': 3,
          'jumped': 4,
          'lazy': 7,
          'over': 5,
          'quick': 1,
          'the': 0},
         OrderedDict([('the', 0),
                      ('quick', 1),
                      ('brown', 2),
                      ('fox', 3),
                      ('jumped', 4),
                      ('over', 5),
                      ('a', 6),
                      ('lazy', 7),
                      ('dog', 8)]))""")

    eleza test_deque(self):
        d = collections.deque()
        self.assertEqual(pprint.pformat(d, width=1), "deque([])")
        d = collections.deque(maxlen=7)
        self.assertEqual(pprint.pformat(d, width=1), "deque([], maxlen=7)")
        words = 'the quick brown fox jumped over a lazy dog'.split()
        d = collections.deque(zip(words, itertools.count()))
        self.assertEqual(pprint.pformat(d),
"""\
deque([('the', 0),
       ('quick', 1),
       ('brown', 2),
       ('fox', 3),
       ('jumped', 4),
       ('over', 5),
       ('a', 6),
       ('lazy', 7),
       ('dog', 8)])""")
        d = collections.deque(zip(words, itertools.count()), maxlen=7)
        self.assertEqual(pprint.pformat(d),
"""\
deque([('brown', 2),
       ('fox', 3),
       ('jumped', 4),
       ('over', 5),
       ('a', 6),
       ('lazy', 7),
       ('dog', 8)],
      maxlen=7)""")

    eleza test_user_dict(self):
        d = collections.UserDict()
        self.assertEqual(pprint.pformat(d, width=1), "{}")
        words = 'the quick brown fox jumped over a lazy dog'.split()
        d = collections.UserDict(zip(words, itertools.count()))
        self.assertEqual(pprint.pformat(d),
"""\
{'a': 6,
 'brown': 2,
 'dog': 8,
 'fox': 3,
 'jumped': 4,
 'lazy': 7,
 'over': 5,
 'quick': 1,
 'the': 0}""")

    eleza test_user_list(self):
        d = collections.UserList()
        self.assertEqual(pprint.pformat(d, width=1), "[]")
        words = 'the quick brown fox jumped over a lazy dog'.split()
        d = collections.UserList(zip(words, itertools.count()))
        self.assertEqual(pprint.pformat(d),
"""\
[('the', 0),
 ('quick', 1),
 ('brown', 2),
 ('fox', 3),
 ('jumped', 4),
 ('over', 5),
 ('a', 6),
 ('lazy', 7),
 ('dog', 8)]""")

    eleza test_user_string(self):
        d = collections.UserString('')
        self.assertEqual(pprint.pformat(d, width=1), "''")
        d = collections.UserString('the quick brown fox jumped over a lazy dog')
        self.assertEqual(pprint.pformat(d, width=20),
"""\
('the quick brown '
 'fox jumped over '
 'a lazy dog')""")
        self.assertEqual(pprint.pformat({1: d}, width=20),
"""\
{1: 'the quick '
    'brown fox '
    'jumped over a '
    'lazy dog'}""")


kundi DottedPrettyPrinter(pprint.PrettyPrinter):

    eleza format(self, object, context, maxlevels, level):
        ikiwa isinstance(object, str):
            ikiwa ' ' kwenye object:
                rudisha repr(object), 1, 0
            isipokua:
                rudisha object, 0, 0
        isipokua:
            rudisha pprint.PrettyPrinter.format(
                self, object, context, maxlevels, level)


ikiwa __name__ == "__main__":
    unittest.main()
