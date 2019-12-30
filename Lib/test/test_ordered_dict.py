agiza builtins
agiza contextlib
agiza copy
agiza gc
agiza pickle
kutoka random agiza randrange, shuffle
agiza struct
agiza sys
agiza unittest
agiza weakref
kutoka collections.abc agiza MutableMapping
kutoka test agiza mapping_tests, support


py_coll = support.import_fresh_module('collections', blocked=['_collections'])
c_coll = support.import_fresh_module('collections', fresh=['_collections'])


@contextlib.contextmanager
eleza replaced_module(name, replacement):
    original_module = sys.modules[name]
    sys.modules[name] = replacement
    jaribu:
        yield
    mwishowe:
        sys.modules[name] = original_module


kundi OrderedDictTests:

    eleza test_init(self):
        OrderedDict = self.OrderedDict
        ukijumuisha self.assertRaises(TypeError):
            OrderedDict([('a', 1), ('b', 2)], Tupu)                                 # too many args
        pairs = [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5)]
        self.assertEqual(sorted(OrderedDict(dict(pairs)).items()), pairs)           # dict input
        self.assertEqual(sorted(OrderedDict(**dict(pairs)).items()), pairs)         # kwds input
        self.assertEqual(list(OrderedDict(pairs).items()), pairs)                   # pairs input
        self.assertEqual(list(OrderedDict([('a', 1), ('b', 2), ('c', 9), ('d', 4)],
                                          c=3, e=5).items()), pairs)                # mixed input

        # make sure no positional args conflict ukijumuisha possible kwdargs
        self.assertEqual(list(OrderedDict(self=42).items()), [('self', 42)])
        self.assertEqual(list(OrderedDict(other=42).items()), [('other', 42)])
        self.assertRaises(TypeError, OrderedDict, 42)
        self.assertRaises(TypeError, OrderedDict, (), ())
        self.assertRaises(TypeError, OrderedDict.__init__)

        # Make sure that direct calls to __init__ do sio clear previous contents
        d = OrderedDict([('a', 1), ('b', 2), ('c', 3), ('d', 44), ('e', 55)])
        d.__init__([('e', 5), ('f', 6)], g=7, d=4)
        self.assertEqual(list(d.items()),
            [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5), ('f', 6), ('g', 7)])

    eleza test_468(self):
        OrderedDict = self.OrderedDict
        items = [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5), ('f', 6), ('g', 7)]
        shuffle(items)
        argdict = OrderedDict(items)
        d = OrderedDict(**argdict)
        self.assertEqual(list(d.items()), items)

    eleza test_update(self):
        OrderedDict = self.OrderedDict
        ukijumuisha self.assertRaises(TypeError):
            OrderedDict().update([('a', 1), ('b', 2)], Tupu)                        # too many args
        pairs = [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5)]
        od = OrderedDict()
        od.update(dict(pairs))
        self.assertEqual(sorted(od.items()), pairs)                                 # dict input
        od = OrderedDict()
        od.update(**dict(pairs))
        self.assertEqual(sorted(od.items()), pairs)                                 # kwds input
        od = OrderedDict()
        od.update(pairs)
        self.assertEqual(list(od.items()), pairs)                                   # pairs input
        od = OrderedDict()
        od.update([('a', 1), ('b', 2), ('c', 9), ('d', 4)], c=3, e=5)
        self.assertEqual(list(od.items()), pairs)                                   # mixed input

        # Issue 9137: Named argument called 'other' ama 'self'
        # shouldn't be treated specially.
        od = OrderedDict()
        od.update(self=23)
        self.assertEqual(list(od.items()), [('self', 23)])
        od = OrderedDict()
        od.update(other={})
        self.assertEqual(list(od.items()), [('other', {})])
        od = OrderedDict()
        od.update(red=5, blue=6, other=7, self=8)
        self.assertEqual(sorted(list(od.items())),
                         [('blue', 6), ('other', 7), ('red', 5), ('self', 8)])

        # Make sure that direct calls to update do sio clear previous contents
        # add that updates items are sio moved to the end
        d = OrderedDict([('a', 1), ('b', 2), ('c', 3), ('d', 44), ('e', 55)])
        d.update([('e', 5), ('f', 6)], g=7, d=4)
        self.assertEqual(list(d.items()),
            [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5), ('f', 6), ('g', 7)])

        self.assertRaises(TypeError, OrderedDict().update, 42)
        self.assertRaises(TypeError, OrderedDict().update, (), ())
        self.assertRaises(TypeError, OrderedDict.update)

        self.assertRaises(TypeError, OrderedDict().update, 42)
        self.assertRaises(TypeError, OrderedDict().update, (), ())
        self.assertRaises(TypeError, OrderedDict.update)

    eleza test_init_calls(self):
        calls = []
        kundi Spam:
            eleza keys(self):
                calls.append('keys')
                rudisha ()
            eleza items(self):
                calls.append('items')
                rudisha ()

        self.OrderedDict(Spam())
        self.assertEqual(calls, ['keys'])

    eleza test_fromkeys(self):
        OrderedDict = self.OrderedDict
        od = OrderedDict.fromkeys('abc')
        self.assertEqual(list(od.items()), [(c, Tupu) kila c kwenye 'abc'])
        od = OrderedDict.fromkeys('abc', value=Tupu)
        self.assertEqual(list(od.items()), [(c, Tupu) kila c kwenye 'abc'])
        od = OrderedDict.fromkeys('abc', value=0)
        self.assertEqual(list(od.items()), [(c, 0) kila c kwenye 'abc'])

    eleza test_abc(self):
        OrderedDict = self.OrderedDict
        self.assertIsInstance(OrderedDict(), MutableMapping)
        self.assertKweli(issubclass(OrderedDict, MutableMapping))

    eleza test_clear(self):
        OrderedDict = self.OrderedDict
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        self.assertEqual(len(od), len(pairs))
        od.clear()
        self.assertEqual(len(od), 0)

    eleza test_delitem(self):
        OrderedDict = self.OrderedDict
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        od = OrderedDict(pairs)
        toa od['a']
        self.assertNotIn('a', od)
        ukijumuisha self.assertRaises(KeyError):
            toa od['a']
        self.assertEqual(list(od.items()), pairs[:2] + pairs[3:])

    eleza test_setitem(self):
        OrderedDict = self.OrderedDict
        od = OrderedDict([('d', 1), ('b', 2), ('c', 3), ('a', 4), ('e', 5)])
        od['c'] = 10           # existing element
        od['f'] = 20           # new element
        self.assertEqual(list(od.items()),
                         [('d', 1), ('b', 2), ('c', 10), ('a', 4), ('e', 5), ('f', 20)])

    eleza test_iterators(self):
        OrderedDict = self.OrderedDict
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        self.assertEqual(list(od), [t[0] kila t kwenye pairs])
        self.assertEqual(list(od.keys()), [t[0] kila t kwenye pairs])
        self.assertEqual(list(od.values()), [t[1] kila t kwenye pairs])
        self.assertEqual(list(od.items()), pairs)
        self.assertEqual(list(reversed(od)),
                         [t[0] kila t kwenye reversed(pairs)])
        self.assertEqual(list(reversed(od.keys())),
                         [t[0] kila t kwenye reversed(pairs)])
        self.assertEqual(list(reversed(od.values())),
                         [t[1] kila t kwenye reversed(pairs)])
        self.assertEqual(list(reversed(od.items())), list(reversed(pairs)))

    eleza test_detect_deletion_during_iteration(self):
        OrderedDict = self.OrderedDict
        od = OrderedDict.fromkeys('abc')
        it = iter(od)
        key = next(it)
        toa od[key]
        ukijumuisha self.assertRaises(Exception):
            # Note, the exact exception raised ni sio guaranteed
            # The only guarantee that the next() will sio succeed
            next(it)

    eleza test_sorted_iterators(self):
        OrderedDict = self.OrderedDict
        ukijumuisha self.assertRaises(TypeError):
            OrderedDict([('a', 1), ('b', 2)], Tupu)
        pairs = [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5)]
        od = OrderedDict(pairs)
        self.assertEqual(sorted(od), [t[0] kila t kwenye pairs])
        self.assertEqual(sorted(od.keys()), [t[0] kila t kwenye pairs])
        self.assertEqual(sorted(od.values()), [t[1] kila t kwenye pairs])
        self.assertEqual(sorted(od.items()), pairs)
        self.assertEqual(sorted(reversed(od)),
                         sorted([t[0] kila t kwenye reversed(pairs)]))

    eleza test_iterators_empty(self):
        OrderedDict = self.OrderedDict
        od = OrderedDict()
        empty = []
        self.assertEqual(list(od), empty)
        self.assertEqual(list(od.keys()), empty)
        self.assertEqual(list(od.values()), empty)
        self.assertEqual(list(od.items()), empty)
        self.assertEqual(list(reversed(od)), empty)
        self.assertEqual(list(reversed(od.keys())), empty)
        self.assertEqual(list(reversed(od.values())), empty)
        self.assertEqual(list(reversed(od.items())), empty)

    eleza test_popitem(self):
        OrderedDict = self.OrderedDict
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        wakati pairs:
            self.assertEqual(od.popitem(), pairs.pop())
        ukijumuisha self.assertRaises(KeyError):
            od.popitem()
        self.assertEqual(len(od), 0)

    eleza test_popitem_last(self):
        OrderedDict = self.OrderedDict
        pairs = [(i, i) kila i kwenye range(30)]

        obj = OrderedDict(pairs)
        kila i kwenye range(8):
            obj.popitem(Kweli)
        obj.popitem(Kweli)
        obj.popitem(last=Kweli)
        self.assertEqual(len(obj), 20)

    eleza test_pop(self):
        OrderedDict = self.OrderedDict
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        shuffle(pairs)
        wakati pairs:
            k, v = pairs.pop()
            self.assertEqual(od.pop(k), v)
        ukijumuisha self.assertRaises(KeyError):
            od.pop('xyz')
        self.assertEqual(len(od), 0)
        self.assertEqual(od.pop(k, 12345), 12345)

        # make sure pop still works when __missing__ ni defined
        kundi Missing(OrderedDict):
            eleza __missing__(self, key):
                rudisha 0
        m = Missing(a=1)
        self.assertEqual(m.pop('b', 5), 5)
        self.assertEqual(m.pop('a', 6), 1)
        self.assertEqual(m.pop('a', 6), 6)
        self.assertEqual(m.pop('a', default=6), 6)
        ukijumuisha self.assertRaises(KeyError):
            m.pop('a')

    eleza test_equality(self):
        OrderedDict = self.OrderedDict
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od1 = OrderedDict(pairs)
        od2 = OrderedDict(pairs)
        self.assertEqual(od1, od2)          # same order implies equality
        pairs = pairs[2:] + pairs[:2]
        od2 = OrderedDict(pairs)
        self.assertNotEqual(od1, od2)       # different order implies inequality
        # comparison to regular dict ni sio order sensitive
        self.assertEqual(od1, dict(od2))
        self.assertEqual(dict(od2), od1)
        # different length implied inequality
        self.assertNotEqual(od1, OrderedDict(pairs[:-1]))

    eleza test_copying(self):
        OrderedDict = self.OrderedDict
        # Check that ordered dicts are copyable, deepcopyable, picklable,
        # na have a repr/eval round-trip
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        od = OrderedDict(pairs)
        eleza check(dup):
            msg = "\ncopy: %s\nod: %s" % (dup, od)
            self.assertIsNot(dup, od, msg)
            self.assertEqual(dup, od)
            self.assertEqual(list(dup.items()), list(od.items()))
            self.assertEqual(len(dup), len(od))
            self.assertEqual(type(dup), type(od))
        check(od.copy())
        check(copy.copy(od))
        check(copy.deepcopy(od))
        # pickle directly pulls the module, so we have to fake it
        ukijumuisha replaced_module('collections', self.module):
            kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                ukijumuisha self.subTest(proto=proto):
                    check(pickle.loads(pickle.dumps(od, proto)))
        check(eval(repr(od)))
        update_test = OrderedDict()
        update_test.update(od)
        check(update_test)
        check(OrderedDict(od))

    eleza test_yaml_linkage(self):
        OrderedDict = self.OrderedDict
        # Verify that __reduce__ ni setup kwenye a way that supports PyYAML's dump() feature.
        # In yaml, lists are native but tuples are not.
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        od = OrderedDict(pairs)
        # yaml.dump(od) -->
        # '!!python/object/apply:__main__.OrderedDict\n- - [a, 1]\n  - [b, 2]\n'
        self.assertKweli(all(type(pair)==list kila pair kwenye od.__reduce__()[1]))

    eleza test_reduce_not_too_fat(self):
        OrderedDict = self.OrderedDict
        # do sio save instance dictionary ikiwa sio needed
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        od = OrderedDict(pairs)
        self.assertIsInstance(od.__dict__, dict)
        self.assertIsTupu(od.__reduce__()[2])
        od.x = 10
        self.assertEqual(od.__dict__['x'], 10)
        self.assertEqual(od.__reduce__()[2], {'x': 10})

    eleza test_pickle_recursive(self):
        OrderedDict = self.OrderedDict
        od = OrderedDict()
        od[1] = od

        # pickle directly pulls the module, so we have to fake it
        ukijumuisha replaced_module('collections', self.module):
            kila proto kwenye range(-1, pickle.HIGHEST_PROTOCOL + 1):
                dup = pickle.loads(pickle.dumps(od, proto))
                self.assertIsNot(dup, od)
                self.assertEqual(list(dup.keys()), [1])
                self.assertIs(dup[1], dup)

    eleza test_repr(self):
        OrderedDict = self.OrderedDict
        od = OrderedDict([('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)])
        self.assertEqual(repr(od),
            "OrderedDict([('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)])")
        self.assertEqual(eval(repr(od)), od)
        self.assertEqual(repr(OrderedDict()), "OrderedDict()")

    eleza test_repr_recursive(self):
        OrderedDict = self.OrderedDict
        # See issue #9826
        od = OrderedDict.fromkeys('abc')
        od['x'] = od
        self.assertEqual(repr(od),
            "OrderedDict([('a', Tupu), ('b', Tupu), ('c', Tupu), ('x', ...)])")

    eleza test_repr_recursive_values(self):
        OrderedDict = self.OrderedDict
        od = OrderedDict()
        od[42] = od.values()
        r = repr(od)
        # Cannot perform a stronger test, as the contents of the repr
        # are implementation-dependent.  All we can say ni that we
        # want a str result, sio an exception of any sort.
        self.assertIsInstance(r, str)
        od[42] = od.items()
        r = repr(od)
        # Again.
        self.assertIsInstance(r, str)

    eleza test_setdefault(self):
        OrderedDict = self.OrderedDict
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        pair_order = list(od.items())
        self.assertEqual(od.setdefault('a', 10), 3)
        # make sure order didn't change
        self.assertEqual(list(od.items()), pair_order)
        self.assertEqual(od.setdefault('x', 10), 10)
        # make sure 'x' ni added to the end
        self.assertEqual(list(od.items())[-1], ('x', 10))
        self.assertEqual(od.setdefault('g', default=9), 9)

        # make sure setdefault still works when __missing__ ni defined
        kundi Missing(OrderedDict):
            eleza __missing__(self, key):
                rudisha 0
        self.assertEqual(Missing().setdefault(5, 9), 9)

    eleza test_reinsert(self):
        OrderedDict = self.OrderedDict
        # Given insert a, insert b, delete a, re-insert a,
        # verify that a ni now later than b.
        od = OrderedDict()
        od['a'] = 1
        od['b'] = 2
        toa od['a']
        self.assertEqual(list(od.items()), [('b', 2)])
        od['a'] = 1
        self.assertEqual(list(od.items()), [('b', 2), ('a', 1)])

    eleza test_move_to_end(self):
        OrderedDict = self.OrderedDict
        od = OrderedDict.fromkeys('abcde')
        self.assertEqual(list(od), list('abcde'))
        od.move_to_end('c')
        self.assertEqual(list(od), list('abdec'))
        od.move_to_end('c', 0)
        self.assertEqual(list(od), list('cabde'))
        od.move_to_end('c', 0)
        self.assertEqual(list(od), list('cabde'))
        od.move_to_end('e')
        self.assertEqual(list(od), list('cabde'))
        od.move_to_end('b', last=Uongo)
        self.assertEqual(list(od), list('bcade'))
        ukijumuisha self.assertRaises(KeyError):
            od.move_to_end('x')
        ukijumuisha self.assertRaises(KeyError):
            od.move_to_end('x', 0)

    eleza test_move_to_end_issue25406(self):
        OrderedDict = self.OrderedDict
        od = OrderedDict.fromkeys('abc')
        od.move_to_end('c', last=Uongo)
        self.assertEqual(list(od), list('cab'))
        od.move_to_end('a', last=Uongo)
        self.assertEqual(list(od), list('acb'))

        od = OrderedDict.fromkeys('abc')
        od.move_to_end('a')
        self.assertEqual(list(od), list('bca'))
        od.move_to_end('c')
        self.assertEqual(list(od), list('bac'))

    eleza test_sizeof(self):
        OrderedDict = self.OrderedDict
        # Wimpy test: Just verify the reported size ni larger than a regular dict
        d = dict(a=1)
        od = OrderedDict(**d)
        self.assertGreater(sys.getsizeof(od), sys.getsizeof(d))

    eleza test_views(self):
        OrderedDict = self.OrderedDict
        # See http://bugs.python.org/issue24286
        s = 'the quick brown fox jumped over a lazy dog yesterday before dawn'.split()
        od = OrderedDict.fromkeys(s)
        self.assertEqual(od.keys(), dict(od).keys())
        self.assertEqual(od.items(), dict(od).items())

    eleza test_override_update(self):
        OrderedDict = self.OrderedDict
        # Verify that subclasses can override update() without komaing __init__()
        kundi MyOD(OrderedDict):
            eleza update(self, *args, **kwds):
                 ashiria Exception()
        items = [('a', 1), ('c', 3), ('b', 2)]
        self.assertEqual(list(MyOD(items).items()), items)

    eleza test_highly_nested(self):
        # Issues 25395 na 35983: test that the trashcan mechanism works
        # correctly kila OrderedDict: deleting a highly nested OrderDict
        # should sio crash Python.
        OrderedDict = self.OrderedDict
        obj = Tupu
        kila _ kwenye range(1000):
            obj = OrderedDict([(Tupu, obj)])
        toa obj
        support.gc_collect()

    eleza test_highly_nested_subclass(self):
        # Issues 25395 na 35983: test that the trashcan mechanism works
        # correctly kila OrderedDict: deleting a highly nested OrderDict
        # should sio crash Python.
        OrderedDict = self.OrderedDict
        deleted = []
        kundi MyOD(OrderedDict):
            eleza __del__(self):
                deleted.append(self.i)
        obj = Tupu
        kila i kwenye range(100):
            obj = MyOD([(Tupu, obj)])
            obj.i = i
        toa obj
        support.gc_collect()
        self.assertEqual(deleted, list(reversed(range(100))))

    eleza test_delitem_hash_collision(self):
        OrderedDict = self.OrderedDict

        kundi Key:
            eleza __init__(self, hash):
                self._hash = hash
                self.value = str(id(self))
            eleza __hash__(self):
                rudisha self._hash
            eleza __eq__(self, other):
                jaribu:
                    rudisha self.value == other.value
                except AttributeError:
                    rudisha Uongo
            eleza __repr__(self):
                rudisha self.value

        eleza blocking_hash(hash):
            # See the collision-handling kwenye lookdict (in Objects/dictobject.c).
            MINSIZE = 8
            i = (hash & MINSIZE-1)
            rudisha (i << 2) + i + hash + 1

        COLLIDING = 1

        key = Key(COLLIDING)
        colliding = Key(COLLIDING)
        blocking = Key(blocking_hash(COLLIDING))

        od = OrderedDict()
        od[key] = ...
        od[blocking] = ...
        od[colliding] = ...
        od['after'] = ...

        toa od[blocking]
        toa od[colliding]
        self.assertEqual(list(od.items()), [(key, ...), ('after', ...)])

    eleza test_issue24347(self):
        OrderedDict = self.OrderedDict

        kundi Key:
            eleza __hash__(self):
                rudisha randrange(100000)

        od = OrderedDict()
        kila i kwenye range(100):
            key = Key()
            od[key] = i

        # These should sio crash.
        ukijumuisha self.assertRaises(KeyError):
            list(od.values())
        ukijumuisha self.assertRaises(KeyError):
            list(od.items())
        ukijumuisha self.assertRaises(KeyError):
            repr(od)
        ukijumuisha self.assertRaises(KeyError):
            od.copy()

    eleza test_issue24348(self):
        OrderedDict = self.OrderedDict

        kundi Key:
            eleza __hash__(self):
                rudisha 1

        od = OrderedDict()
        od[Key()] = 0
        # This should sio crash.
        od.popitem()

    eleza test_issue24667(self):
        """
        dict resizes after a certain number of insertion operations,
        whether ama sio there were deletions that freed up slots kwenye the
        hash table.  During fast node lookup, OrderedDict must correctly
        respond to all resizes, even ikiwa the current "size" ni the same
        as the old one.  We verify that here by forcing a dict resize
        on a sparse odict na then perform an operation that should
        trigger an odict resize (e.g. popitem).  One key aspect here is
        that we will keep the size of the odict the same at each popitem
        call.  This verifies that we handled the dict resize properly.
        """
        OrderedDict = self.OrderedDict

        od = OrderedDict()
        kila c0 kwenye '0123456789ABCDEF':
            kila c1 kwenye '0123456789ABCDEF':
                ikiwa len(od) == 4:
                    # This should sio  ashiria a KeyError.
                    od.popitem(last=Uongo)
                key = c0 + c1
                od[key] = key

    # Direct use of dict methods

    eleza test_dict_setitem(self):
        OrderedDict = self.OrderedDict
        od = OrderedDict()
        dict.__setitem__(od, 'spam', 1)
        self.assertNotIn('NULL', repr(od))

    eleza test_dict_delitem(self):
        OrderedDict = self.OrderedDict
        od = OrderedDict()
        od['spam'] = 1
        od['ham'] = 2
        dict.__delitem__(od, 'spam')
        ukijumuisha self.assertRaises(KeyError):
            repr(od)

    eleza test_dict_clear(self):
        OrderedDict = self.OrderedDict
        od = OrderedDict()
        od['spam'] = 1
        od['ham'] = 2
        dict.clear(od)
        self.assertNotIn('NULL', repr(od))

    eleza test_dict_pop(self):
        OrderedDict = self.OrderedDict
        od = OrderedDict()
        od['spam'] = 1
        od['ham'] = 2
        dict.pop(od, 'spam')
        ukijumuisha self.assertRaises(KeyError):
            repr(od)

    eleza test_dict_popitem(self):
        OrderedDict = self.OrderedDict
        od = OrderedDict()
        od['spam'] = 1
        od['ham'] = 2
        dict.popitem(od)
        ukijumuisha self.assertRaises(KeyError):
            repr(od)

    eleza test_dict_setdefault(self):
        OrderedDict = self.OrderedDict
        od = OrderedDict()
        dict.setdefault(od, 'spam', 1)
        self.assertNotIn('NULL', repr(od))

    eleza test_dict_update(self):
        OrderedDict = self.OrderedDict
        od = OrderedDict()
        dict.update(od, [('spam', 1)])
        self.assertNotIn('NULL', repr(od))

    eleza test_reference_loop(self):
        # Issue 25935
        OrderedDict = self.OrderedDict
        kundi A:
            od = OrderedDict()
        A.od[A] = Tupu
        r = weakref.ref(A)
        toa A
        gc.collect()
        self.assertIsTupu(r())

    eleza test_free_after_iterating(self):
        support.check_free_after_iterating(self, iter, self.OrderedDict)
        support.check_free_after_iterating(self, lambda d: iter(d.keys()), self.OrderedDict)
        support.check_free_after_iterating(self, lambda d: iter(d.values()), self.OrderedDict)
        support.check_free_after_iterating(self, lambda d: iter(d.items()), self.OrderedDict)


kundi PurePythonOrderedDictTests(OrderedDictTests, unittest.TestCase):

    module = py_coll
    OrderedDict = py_coll.OrderedDict


kundi CPythonBuiltinDictTests(unittest.TestCase):
    """Builtin dict preserves insertion order.

    Reuse some of tests kwenye OrderedDict selectively.
    """

    module = builtins
    OrderedDict = dict

kila method kwenye (
    "test_init test_update test_abc test_clear test_delitem " +
    "test_setitem test_detect_deletion_during_iteration " +
    "test_popitem test_reinsert test_override_update " +
    "test_highly_nested test_highly_nested_subkundi " +
    "test_delitem_hash_collision ").split():
    setattr(CPythonBuiltinDictTests, method, getattr(OrderedDictTests, method))
toa method


@unittest.skipUnless(c_coll, 'requires the C version of the collections module')
kundi CPythonOrderedDictTests(OrderedDictTests, unittest.TestCase):

    module = c_coll
    OrderedDict = c_coll.OrderedDict
    check_sizeof = support.check_sizeof

    @support.cpython_only
    eleza test_sizeof_exact(self):
        OrderedDict = self.OrderedDict
        calcsize = struct.calcsize
        size = support.calcobjsize
        check = self.check_sizeof

        basicsize = size('nQ2P' + '3PnPn2P') + calcsize('2nP2n')

        entrysize = calcsize('n2P')
        p = calcsize('P')
        nodesize = calcsize('Pn2P')

        od = OrderedDict()
        check(od, basicsize + 8 + 5*entrysize)  # 8byte indices + 8*2//3 * entry table
        od.x = 1
        check(od, basicsize + 8 + 5*entrysize)
        od.update([(i, i) kila i kwenye range(3)])
        check(od, basicsize + 8*p + 8 + 5*entrysize + 3*nodesize)
        od.update([(i, i) kila i kwenye range(3, 10)])
        check(od, basicsize + 16*p + 16 + 10*entrysize + 10*nodesize)

        check(od.keys(), size('P'))
        check(od.items(), size('P'))
        check(od.values(), size('P'))

        itersize = size('iP2n2P')
        check(iter(od), itersize)
        check(iter(od.keys()), itersize)
        check(iter(od.items()), itersize)
        check(iter(od.values()), itersize)

    eleza test_key_change_during_iteration(self):
        OrderedDict = self.OrderedDict

        od = OrderedDict.fromkeys('abcde')
        self.assertEqual(list(od), list('abcde'))
        ukijumuisha self.assertRaises(RuntimeError):
            kila i, k kwenye enumerate(od):
                od.move_to_end(k)
                self.assertLess(i, 5)
        ukijumuisha self.assertRaises(RuntimeError):
            kila k kwenye od:
                od['f'] = Tupu
        ukijumuisha self.assertRaises(RuntimeError):
            kila k kwenye od:
                toa od['c']
        self.assertEqual(list(od), list('bdeaf'))

    eleza test_iterators_pickling(self):
        OrderedDict = self.OrderedDict
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        od = OrderedDict(pairs)

        kila method_name kwenye ('keys', 'values', 'items'):
            meth = getattr(od, method_name)
            expected = list(meth())[1:]
            kila i kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                ukijumuisha self.subTest(method_name=method_name, protocol=i):
                    it = iter(meth())
                    next(it)
                    p = pickle.dumps(it, i)
                    unpickled = pickle.loads(p)
                    self.assertEqual(list(unpickled), expected)
                    self.assertEqual(list(it), expected)


kundi PurePythonOrderedDictSubclassTests(PurePythonOrderedDictTests):

    module = py_coll
    kundi OrderedDict(py_coll.OrderedDict):
        pass


kundi CPythonOrderedDictSubclassTests(CPythonOrderedDictTests):

    module = c_coll
    kundi OrderedDict(c_coll.OrderedDict):
        pass


kundi PurePythonGeneralMappingTests(mapping_tests.BasicTestMappingProtocol):

    @classmethod
    eleza setUpClass(cls):
        cls.type2test = py_coll.OrderedDict

    eleza test_popitem(self):
        d = self._empty_mapping()
        self.assertRaises(KeyError, d.popitem)


@unittest.skipUnless(c_coll, 'requires the C version of the collections module')
kundi CPythonGeneralMappingTests(mapping_tests.BasicTestMappingProtocol):

    @classmethod
    eleza setUpClass(cls):
        cls.type2test = c_coll.OrderedDict

    eleza test_popitem(self):
        d = self._empty_mapping()
        self.assertRaises(KeyError, d.popitem)


kundi PurePythonSubclassMappingTests(mapping_tests.BasicTestMappingProtocol):

    @classmethod
    eleza setUpClass(cls):
        kundi MyOrderedDict(py_coll.OrderedDict):
            pass
        cls.type2test = MyOrderedDict

    eleza test_popitem(self):
        d = self._empty_mapping()
        self.assertRaises(KeyError, d.popitem)


@unittest.skipUnless(c_coll, 'requires the C version of the collections module')
kundi CPythonSubclassMappingTests(mapping_tests.BasicTestMappingProtocol):

    @classmethod
    eleza setUpClass(cls):
        kundi MyOrderedDict(c_coll.OrderedDict):
            pass
        cls.type2test = MyOrderedDict

    eleza test_popitem(self):
        d = self._empty_mapping()
        self.assertRaises(KeyError, d.popitem)


ikiwa __name__ == "__main__":
    unittest.main()
