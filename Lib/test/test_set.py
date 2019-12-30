agiza unittest
kutoka test agiza support
agiza gc
agiza weakref
agiza operator
agiza copy
agiza pickle
kutoka random agiza randrange, shuffle
agiza warnings
agiza collections
agiza collections.abc
agiza itertools

kundi PassThru(Exception):
    pass

eleza check_pass_thru():
     ashiria PassThru
    tuma 1

kundi BadCmp:
    eleza __hash__(self):
        rudisha 1
    eleza __eq__(self, other):
         ashiria RuntimeError

kundi ReprWrapper:
    'Used to test self-referential repr() calls'
    eleza __repr__(self):
        rudisha repr(self.value)

kundi HashCountingInt(int):
    'int-like object that counts the number of times __hash__ ni called'
    eleza __init__(self, *args):
        self.hash_count = 0
    eleza __hash__(self):
        self.hash_count += 1
        rudisha int.__hash__(self)

kundi TestJointOps:
    # Tests common to both set na frozenset

    eleza setUp(self):
        self.word = word = 'simsalabim'
        self.otherword = 'madagascar'
        self.letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.s = self.thetype(word)
        self.d = dict.fromkeys(word)

    eleza test_new_or_init(self):
        self.assertRaises(TypeError, self.thetype, [], 2)
        self.assertRaises(TypeError, set().__init__, a=1)

    eleza test_uniquification(self):
        actual = sorted(self.s)
        expected = sorted(self.d)
        self.assertEqual(actual, expected)
        self.assertRaises(PassThru, self.thetype, check_pass_thru())
        self.assertRaises(TypeError, self.thetype, [[]])

    eleza test_len(self):
        self.assertEqual(len(self.s), len(self.d))

    eleza test_contains(self):
        kila c kwenye self.letters:
            self.assertEqual(c kwenye self.s, c kwenye self.d)
        self.assertRaises(TypeError, self.s.__contains__, [[]])
        s = self.thetype([frozenset(self.letters)])
        self.assertIn(self.thetype(self.letters), s)

    eleza test_union(self):
        u = self.s.union(self.otherword)
        kila c kwenye self.letters:
            self.assertEqual(c kwenye u, c kwenye self.d ama c kwenye self.otherword)
        self.assertEqual(self.s, self.thetype(self.word))
        self.assertEqual(type(u), self.basetype)
        self.assertRaises(PassThru, self.s.union, check_pass_thru())
        self.assertRaises(TypeError, self.s.union, [[]])
        kila C kwenye set, frozenset, dict.fromkeys, str, list, tuple:
            self.assertEqual(self.thetype('abcba').union(C('cdc')), set('abcd'))
            self.assertEqual(self.thetype('abcba').union(C('efgfe')), set('abcefg'))
            self.assertEqual(self.thetype('abcba').union(C('ccb')), set('abc'))
            self.assertEqual(self.thetype('abcba').union(C('ef')), set('abcef'))
            self.assertEqual(self.thetype('abcba').union(C('ef'), C('fg')), set('abcefg'))

        # Issue #6573
        x = self.thetype()
        self.assertEqual(x.union(set([1]), x, set([2])), self.thetype([1, 2]))

    eleza test_or(self):
        i = self.s.union(self.otherword)
        self.assertEqual(self.s | set(self.otherword), i)
        self.assertEqual(self.s | frozenset(self.otherword), i)
        jaribu:
            self.s | self.otherword
        except TypeError:
            pass
        isipokua:
            self.fail("s|t did sio screen-out general iterables")

    eleza test_intersection(self):
        i = self.s.intersection(self.otherword)
        kila c kwenye self.letters:
            self.assertEqual(c kwenye i, c kwenye self.d na c kwenye self.otherword)
        self.assertEqual(self.s, self.thetype(self.word))
        self.assertEqual(type(i), self.basetype)
        self.assertRaises(PassThru, self.s.intersection, check_pass_thru())
        kila C kwenye set, frozenset, dict.fromkeys, str, list, tuple:
            self.assertEqual(self.thetype('abcba').intersection(C('cdc')), set('cc'))
            self.assertEqual(self.thetype('abcba').intersection(C('efgfe')), set(''))
            self.assertEqual(self.thetype('abcba').intersection(C('ccb')), set('bc'))
            self.assertEqual(self.thetype('abcba').intersection(C('ef')), set(''))
            self.assertEqual(self.thetype('abcba').intersection(C('cbcf'), C('bag')), set('b'))
        s = self.thetype('abcba')
        z = s.intersection()
        ikiwa self.thetype == frozenset():
            self.assertEqual(id(s), id(z))
        isipokua:
            self.assertNotEqual(id(s), id(z))

    eleza test_isdisjoint(self):
        eleza f(s1, s2):
            'Pure python equivalent of isdisjoint()'
            rudisha sio set(s1).intersection(s2)
        kila larg kwenye '', 'a', 'ab', 'abc', 'ababac', 'cdc', 'cc', 'efgfe', 'ccb', 'ef':
            s1 = self.thetype(larg)
            kila rarg kwenye '', 'a', 'ab', 'abc', 'ababac', 'cdc', 'cc', 'efgfe', 'ccb', 'ef':
                kila C kwenye set, frozenset, dict.fromkeys, str, list, tuple:
                    s2 = C(rarg)
                    actual = s1.isdisjoint(s2)
                    expected = f(s1, s2)
                    self.assertEqual(actual, expected)
                    self.assertKweli(actual ni Kweli ama actual ni Uongo)

    eleza test_and(self):
        i = self.s.intersection(self.otherword)
        self.assertEqual(self.s & set(self.otherword), i)
        self.assertEqual(self.s & frozenset(self.otherword), i)
        jaribu:
            self.s & self.otherword
        except TypeError:
            pass
        isipokua:
            self.fail("s&t did sio screen-out general iterables")

    eleza test_difference(self):
        i = self.s.difference(self.otherword)
        kila c kwenye self.letters:
            self.assertEqual(c kwenye i, c kwenye self.d na c sio kwenye self.otherword)
        self.assertEqual(self.s, self.thetype(self.word))
        self.assertEqual(type(i), self.basetype)
        self.assertRaises(PassThru, self.s.difference, check_pass_thru())
        self.assertRaises(TypeError, self.s.difference, [[]])
        kila C kwenye set, frozenset, dict.fromkeys, str, list, tuple:
            self.assertEqual(self.thetype('abcba').difference(C('cdc')), set('ab'))
            self.assertEqual(self.thetype('abcba').difference(C('efgfe')), set('abc'))
            self.assertEqual(self.thetype('abcba').difference(C('ccb')), set('a'))
            self.assertEqual(self.thetype('abcba').difference(C('ef')), set('abc'))
            self.assertEqual(self.thetype('abcba').difference(), set('abc'))
            self.assertEqual(self.thetype('abcba').difference(C('a'), C('b')), set('c'))

    eleza test_sub(self):
        i = self.s.difference(self.otherword)
        self.assertEqual(self.s - set(self.otherword), i)
        self.assertEqual(self.s - frozenset(self.otherword), i)
        jaribu:
            self.s - self.otherword
        except TypeError:
            pass
        isipokua:
            self.fail("s-t did sio screen-out general iterables")

    eleza test_symmetric_difference(self):
        i = self.s.symmetric_difference(self.otherword)
        kila c kwenye self.letters:
            self.assertEqual(c kwenye i, (c kwenye self.d) ^ (c kwenye self.otherword))
        self.assertEqual(self.s, self.thetype(self.word))
        self.assertEqual(type(i), self.basetype)
        self.assertRaises(PassThru, self.s.symmetric_difference, check_pass_thru())
        self.assertRaises(TypeError, self.s.symmetric_difference, [[]])
        kila C kwenye set, frozenset, dict.fromkeys, str, list, tuple:
            self.assertEqual(self.thetype('abcba').symmetric_difference(C('cdc')), set('abd'))
            self.assertEqual(self.thetype('abcba').symmetric_difference(C('efgfe')), set('abcefg'))
            self.assertEqual(self.thetype('abcba').symmetric_difference(C('ccb')), set('a'))
            self.assertEqual(self.thetype('abcba').symmetric_difference(C('ef')), set('abcef'))

    eleza test_xor(self):
        i = self.s.symmetric_difference(self.otherword)
        self.assertEqual(self.s ^ set(self.otherword), i)
        self.assertEqual(self.s ^ frozenset(self.otherword), i)
        jaribu:
            self.s ^ self.otherword
        except TypeError:
            pass
        isipokua:
            self.fail("s^t did sio screen-out general iterables")

    eleza test_equality(self):
        self.assertEqual(self.s, set(self.word))
        self.assertEqual(self.s, frozenset(self.word))
        self.assertEqual(self.s == self.word, Uongo)
        self.assertNotEqual(self.s, set(self.otherword))
        self.assertNotEqual(self.s, frozenset(self.otherword))
        self.assertEqual(self.s != self.word, Kweli)

    eleza test_setOfFrozensets(self):
        t = map(frozenset, ['abcdef', 'bcd', 'bdcb', 'fed', 'fedccba'])
        s = self.thetype(t)
        self.assertEqual(len(s), 3)

    eleza test_sub_and_super(self):
        p, q, r = map(self.thetype, ['ab', 'abcde', 'def'])
        self.assertKweli(p < q)
        self.assertKweli(p <= q)
        self.assertKweli(q <= q)
        self.assertKweli(q > p)
        self.assertKweli(q >= p)
        self.assertUongo(q < r)
        self.assertUongo(q <= r)
        self.assertUongo(q > r)
        self.assertUongo(q >= r)
        self.assertKweli(set('a').issubset('abc'))
        self.assertKweli(set('abc').issuperset('a'))
        self.assertUongo(set('a').issubset('cbs'))
        self.assertUongo(set('cbs').issuperset('a'))

    eleza test_pickling(self):
        kila i kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            p = pickle.dumps(self.s, i)
            dup = pickle.loads(p)
            self.assertEqual(self.s, dup, "%s != %s" % (self.s, dup))
            ikiwa type(self.s) sio kwenye (set, frozenset):
                self.s.x = 10
                p = pickle.dumps(self.s, i)
                dup = pickle.loads(p)
                self.assertEqual(self.s.x, dup.x)

    eleza test_iterator_pickling(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            itorg = iter(self.s)
            data = self.thetype(self.s)
            d = pickle.dumps(itorg, proto)
            it = pickle.loads(d)
            # Set iterators unpickle as list iterators due to the
            # undefined order of set items.
            # self.assertEqual(type(itorg), type(it))
            self.assertIsInstance(it, collections.abc.Iterator)
            self.assertEqual(self.thetype(it), data)

            it = pickle.loads(d)
            jaribu:
                drop = next(it)
            except StopIteration:
                endelea
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            self.assertEqual(self.thetype(it), data - self.thetype((drop,)))

    eleza test_deepcopy(self):
        kundi Tracer:
            eleza __init__(self, value):
                self.value = value
            eleza __hash__(self):
                rudisha self.value
            eleza __deepcopy__(self, memo=Tupu):
                rudisha Tracer(self.value + 1)
        t = Tracer(10)
        s = self.thetype([t])
        dup = copy.deepcopy(s)
        self.assertNotEqual(id(s), id(dup))
        kila elem kwenye dup:
            newt = elem
        self.assertNotEqual(id(t), id(newt))
        self.assertEqual(t.value + 1, newt.value)

    eleza test_gc(self):
        # Create a nest of cycles to exercise overall ref count check
        kundi A:
            pass
        s = set(A() kila i kwenye range(1000))
        kila elem kwenye s:
            elem.cycle = s
            elem.sub = elem
            elem.set = set([elem])

    eleza test_subclass_with_custom_hash(self):
        # Bug #1257731
        kundi H(self.thetype):
            eleza __hash__(self):
                rudisha int(id(self) & 0x7fffffff)
        s=H()
        f=set()
        f.add(s)
        self.assertIn(s, f)
        f.remove(s)
        f.add(s)
        f.discard(s)

    eleza test_badcmp(self):
        s = self.thetype([BadCmp()])
        # Detect comparison errors during insertion na lookup
        self.assertRaises(RuntimeError, self.thetype, [BadCmp(), BadCmp()])
        self.assertRaises(RuntimeError, s.__contains__, BadCmp())
        # Detect errors during mutating operations
        ikiwa hasattr(s, 'add'):
            self.assertRaises(RuntimeError, s.add, BadCmp())
            self.assertRaises(RuntimeError, s.discard, BadCmp())
            self.assertRaises(RuntimeError, s.remove, BadCmp())

    eleza test_cyclical_repr(self):
        w = ReprWrapper()
        s = self.thetype([w])
        w.value = s
        ikiwa self.thetype == set:
            self.assertEqual(repr(s), '{set(...)}')
        isipokua:
            name = repr(s).partition('(')[0]    # strip kundi name
            self.assertEqual(repr(s), '%s({%s(...)})' % (name, name))

    eleza test_cyclical_andika(self):
        w = ReprWrapper()
        s = self.thetype([w])
        w.value = s
        fo = open(support.TESTFN, "w")
        jaribu:
            fo.write(str(s))
            fo.close()
            fo = open(support.TESTFN, "r")
            self.assertEqual(fo.read(), repr(s))
        mwishowe:
            fo.close()
            support.unlink(support.TESTFN)

    eleza test_do_not_rehash_dict_keys(self):
        n = 10
        d = dict.fromkeys(map(HashCountingInt, range(n)))
        self.assertEqual(sum(elem.hash_count kila elem kwenye d), n)
        s = self.thetype(d)
        self.assertEqual(sum(elem.hash_count kila elem kwenye d), n)
        s.difference(d)
        self.assertEqual(sum(elem.hash_count kila elem kwenye d), n)
        ikiwa hasattr(s, 'symmetric_difference_update'):
            s.symmetric_difference_update(d)
        self.assertEqual(sum(elem.hash_count kila elem kwenye d), n)
        d2 = dict.fromkeys(set(d))
        self.assertEqual(sum(elem.hash_count kila elem kwenye d), n)
        d3 = dict.fromkeys(frozenset(d))
        self.assertEqual(sum(elem.hash_count kila elem kwenye d), n)
        d3 = dict.fromkeys(frozenset(d), 123)
        self.assertEqual(sum(elem.hash_count kila elem kwenye d), n)
        self.assertEqual(d3, dict.fromkeys(d, 123))

    eleza test_container_iterator(self):
        # Bug #3680: tp_traverse was sio implemented kila set iterator object
        kundi C(object):
            pass
        obj = C()
        ref = weakref.ref(obj)
        container = set([obj, 1])
        obj.x = iter(container)
        toa obj, container
        gc.collect()
        self.assertKweli(ref() ni Tupu, "Cycle was sio collected")

    eleza test_free_after_iterating(self):
        support.check_free_after_iterating(self, iter, self.thetype)

kundi TestSet(TestJointOps, unittest.TestCase):
    thetype = set
    basetype = set

    eleza test_init(self):
        s = self.thetype()
        s.__init__(self.word)
        self.assertEqual(s, set(self.word))
        s.__init__(self.otherword)
        self.assertEqual(s, set(self.otherword))
        self.assertRaises(TypeError, s.__init__, s, 2);
        self.assertRaises(TypeError, s.__init__, 1);

    eleza test_constructor_identity(self):
        s = self.thetype(range(3))
        t = self.thetype(s)
        self.assertNotEqual(id(s), id(t))

    eleza test_set_literal(self):
        s = set([1,2,3])
        t = {1,2,3}
        self.assertEqual(s, t)

    eleza test_set_literal_insertion_order(self):
        # SF Issue #26020 -- Expect left to right insertion
        s = {1, 1.0, Kweli}
        self.assertEqual(len(s), 1)
        stored_value = s.pop()
        self.assertEqual(type(stored_value), int)

    eleza test_set_literal_evaluation_order(self):
        # Expect left to right expression evaluation
        events = []
        eleza record(obj):
            events.append(obj)
        s = {record(1), record(2), record(3)}
        self.assertEqual(events, [1, 2, 3])

    eleza test_hash(self):
        self.assertRaises(TypeError, hash, self.s)

    eleza test_clear(self):
        self.s.clear()
        self.assertEqual(self.s, set())
        self.assertEqual(len(self.s), 0)

    eleza test_copy(self):
        dup = self.s.copy()
        self.assertEqual(self.s, dup)
        self.assertNotEqual(id(self.s), id(dup))
        self.assertEqual(type(dup), self.basetype)

    eleza test_add(self):
        self.s.add('Q')
        self.assertIn('Q', self.s)
        dup = self.s.copy()
        self.s.add('Q')
        self.assertEqual(self.s, dup)
        self.assertRaises(TypeError, self.s.add, [])

    eleza test_remove(self):
        self.s.remove('a')
        self.assertNotIn('a', self.s)
        self.assertRaises(KeyError, self.s.remove, 'Q')
        self.assertRaises(TypeError, self.s.remove, [])
        s = self.thetype([frozenset(self.word)])
        self.assertIn(self.thetype(self.word), s)
        s.remove(self.thetype(self.word))
        self.assertNotIn(self.thetype(self.word), s)
        self.assertRaises(KeyError, self.s.remove, self.thetype(self.word))

    eleza test_remove_keyerror_unpacking(self):
        # bug:  www.python.org/sf/1576657
        kila v1 kwenye ['Q', (1,)]:
            jaribu:
                self.s.remove(v1)
            except KeyError as e:
                v2 = e.args[0]
                self.assertEqual(v1, v2)
            isipokua:
                self.fail()

    eleza test_remove_keyerror_set(self):
        key = self.thetype([3, 4])
        jaribu:
            self.s.remove(key)
        except KeyError as e:
            self.assertKweli(e.args[0] ni key,
                         "KeyError should be {0}, sio {1}".format(key,
                                                                  e.args[0]))
        isipokua:
            self.fail()

    eleza test_discard(self):
        self.s.discard('a')
        self.assertNotIn('a', self.s)
        self.s.discard('Q')
        self.assertRaises(TypeError, self.s.discard, [])
        s = self.thetype([frozenset(self.word)])
        self.assertIn(self.thetype(self.word), s)
        s.discard(self.thetype(self.word))
        self.assertNotIn(self.thetype(self.word), s)
        s.discard(self.thetype(self.word))

    eleza test_pop(self):
        kila i kwenye range(len(self.s)):
            elem = self.s.pop()
            self.assertNotIn(elem, self.s)
        self.assertRaises(KeyError, self.s.pop)

    eleza test_update(self):
        retval = self.s.update(self.otherword)
        self.assertEqual(retval, Tupu)
        kila c kwenye (self.word + self.otherword):
            self.assertIn(c, self.s)
        self.assertRaises(PassThru, self.s.update, check_pass_thru())
        self.assertRaises(TypeError, self.s.update, [[]])
        kila p, q kwenye (('cdc', 'abcd'), ('efgfe', 'abcefg'), ('ccb', 'abc'), ('ef', 'abcef')):
            kila C kwenye set, frozenset, dict.fromkeys, str, list, tuple:
                s = self.thetype('abcba')
                self.assertEqual(s.update(C(p)), Tupu)
                self.assertEqual(s, set(q))
        kila p kwenye ('cdc', 'efgfe', 'ccb', 'ef', 'abcda'):
            q = 'ahi'
            kila C kwenye set, frozenset, dict.fromkeys, str, list, tuple:
                s = self.thetype('abcba')
                self.assertEqual(s.update(C(p), C(q)), Tupu)
                self.assertEqual(s, set(s) | set(p) | set(q))

    eleza test_ior(self):
        self.s |= set(self.otherword)
        kila c kwenye (self.word + self.otherword):
            self.assertIn(c, self.s)

    eleza test_intersection_update(self):
        retval = self.s.intersection_update(self.otherword)
        self.assertEqual(retval, Tupu)
        kila c kwenye (self.word + self.otherword):
            ikiwa c kwenye self.otherword na c kwenye self.word:
                self.assertIn(c, self.s)
            isipokua:
                self.assertNotIn(c, self.s)
        self.assertRaises(PassThru, self.s.intersection_update, check_pass_thru())
        self.assertRaises(TypeError, self.s.intersection_update, [[]])
        kila p, q kwenye (('cdc', 'c'), ('efgfe', ''), ('ccb', 'bc'), ('ef', '')):
            kila C kwenye set, frozenset, dict.fromkeys, str, list, tuple:
                s = self.thetype('abcba')
                self.assertEqual(s.intersection_update(C(p)), Tupu)
                self.assertEqual(s, set(q))
                ss = 'abcba'
                s = self.thetype(ss)
                t = 'cbc'
                self.assertEqual(s.intersection_update(C(p), C(t)), Tupu)
                self.assertEqual(s, set('abcba')&set(p)&set(t))

    eleza test_iand(self):
        self.s &= set(self.otherword)
        kila c kwenye (self.word + self.otherword):
            ikiwa c kwenye self.otherword na c kwenye self.word:
                self.assertIn(c, self.s)
            isipokua:
                self.assertNotIn(c, self.s)

    eleza test_difference_update(self):
        retval = self.s.difference_update(self.otherword)
        self.assertEqual(retval, Tupu)
        kila c kwenye (self.word + self.otherword):
            ikiwa c kwenye self.word na c sio kwenye self.otherword:
                self.assertIn(c, self.s)
            isipokua:
                self.assertNotIn(c, self.s)
        self.assertRaises(PassThru, self.s.difference_update, check_pass_thru())
        self.assertRaises(TypeError, self.s.difference_update, [[]])
        self.assertRaises(TypeError, self.s.symmetric_difference_update, [[]])
        kila p, q kwenye (('cdc', 'ab'), ('efgfe', 'abc'), ('ccb', 'a'), ('ef', 'abc')):
            kila C kwenye set, frozenset, dict.fromkeys, str, list, tuple:
                s = self.thetype('abcba')
                self.assertEqual(s.difference_update(C(p)), Tupu)
                self.assertEqual(s, set(q))

                s = self.thetype('abcdefghih')
                s.difference_update()
                self.assertEqual(s, self.thetype('abcdefghih'))

                s = self.thetype('abcdefghih')
                s.difference_update(C('aba'))
                self.assertEqual(s, self.thetype('cdefghih'))

                s = self.thetype('abcdefghih')
                s.difference_update(C('cdc'), C('aba'))
                self.assertEqual(s, self.thetype('efghih'))

    eleza test_isub(self):
        self.s -= set(self.otherword)
        kila c kwenye (self.word + self.otherword):
            ikiwa c kwenye self.word na c sio kwenye self.otherword:
                self.assertIn(c, self.s)
            isipokua:
                self.assertNotIn(c, self.s)

    eleza test_symmetric_difference_update(self):
        retval = self.s.symmetric_difference_update(self.otherword)
        self.assertEqual(retval, Tupu)
        kila c kwenye (self.word + self.otherword):
            ikiwa (c kwenye self.word) ^ (c kwenye self.otherword):
                self.assertIn(c, self.s)
            isipokua:
                self.assertNotIn(c, self.s)
        self.assertRaises(PassThru, self.s.symmetric_difference_update, check_pass_thru())
        self.assertRaises(TypeError, self.s.symmetric_difference_update, [[]])
        kila p, q kwenye (('cdc', 'abd'), ('efgfe', 'abcefg'), ('ccb', 'a'), ('ef', 'abcef')):
            kila C kwenye set, frozenset, dict.fromkeys, str, list, tuple:
                s = self.thetype('abcba')
                self.assertEqual(s.symmetric_difference_update(C(p)), Tupu)
                self.assertEqual(s, set(q))

    eleza test_ixor(self):
        self.s ^= set(self.otherword)
        kila c kwenye (self.word + self.otherword):
            ikiwa (c kwenye self.word) ^ (c kwenye self.otherword):
                self.assertIn(c, self.s)
            isipokua:
                self.assertNotIn(c, self.s)

    eleza test_inplace_on_self(self):
        t = self.s.copy()
        t |= t
        self.assertEqual(t, self.s)
        t &= t
        self.assertEqual(t, self.s)
        t -= t
        self.assertEqual(t, self.thetype())
        t = self.s.copy()
        t ^= t
        self.assertEqual(t, self.thetype())

    eleza test_weakref(self):
        s = self.thetype('gallahad')
        p = weakref.proxy(s)
        self.assertEqual(str(p), str(s))
        s = Tupu
        self.assertRaises(ReferenceError, str, p)

    eleza test_rich_compare(self):
        kundi TestRichSetCompare:
            eleza __gt__(self, some_set):
                self.gt_called = Kweli
                rudisha Uongo
            eleza __lt__(self, some_set):
                self.lt_called = Kweli
                rudisha Uongo
            eleza __ge__(self, some_set):
                self.ge_called = Kweli
                rudisha Uongo
            eleza __le__(self, some_set):
                self.le_called = Kweli
                rudisha Uongo

        # This first tries the builtin rich set comparison, which doesn't know
        # how to handle the custom object. Upon returning NotImplemented, the
        # corresponding comparison on the right object ni invoked.
        myset = {1, 2, 3}

        myobj = TestRichSetCompare()
        myset < myobj
        self.assertKweli(myobj.gt_called)

        myobj = TestRichSetCompare()
        myset > myobj
        self.assertKweli(myobj.lt_called)

        myobj = TestRichSetCompare()
        myset <= myobj
        self.assertKweli(myobj.ge_called)

        myobj = TestRichSetCompare()
        myset >= myobj
        self.assertKweli(myobj.le_called)

    @unittest.skipUnless(hasattr(set, "test_c_api"),
                         'C API test only available kwenye a debug build')
    eleza test_c_api(self):
        self.assertEqual(set().test_c_api(), Kweli)

kundi SetSubclass(set):
    pass

kundi TestSetSubclass(TestSet):
    thetype = SetSubclass
    basetype = set

kundi SetSubclassWithKeywordArgs(set):
    eleza __init__(self, iterable=[], newarg=Tupu):
        set.__init__(self, iterable)

kundi TestSetSubclassWithKeywordArgs(TestSet):

    eleza test_keywords_in_subclass(self):
        'SF bug #1486663 -- this used to erroneously  ashiria a TypeError'
        SetSubclassWithKeywordArgs(newarg=1)

kundi TestFrozenSet(TestJointOps, unittest.TestCase):
    thetype = frozenset
    basetype = frozenset

    eleza test_init(self):
        s = self.thetype(self.word)
        s.__init__(self.otherword)
        self.assertEqual(s, set(self.word))

    eleza test_singleton_empty_frozenset(self):
        f = frozenset()
        efs = [frozenset(), frozenset([]), frozenset(()), frozenset(''),
               frozenset(), frozenset([]), frozenset(()), frozenset(''),
               frozenset(range(0)), frozenset(frozenset()),
               frozenset(f), f]
        # All of the empty frozensets should have just one id()
        self.assertEqual(len(set(map(id, efs))), 1)

    eleza test_constructor_identity(self):
        s = self.thetype(range(3))
        t = self.thetype(s)
        self.assertEqual(id(s), id(t))

    eleza test_hash(self):
        self.assertEqual(hash(self.thetype('abcdeb')),
                         hash(self.thetype('ebecda')))

        # make sure that all permutations give the same hash value
        n = 100
        seq = [randrange(n) kila i kwenye range(n)]
        results = set()
        kila i kwenye range(200):
            shuffle(seq)
            results.add(hash(self.thetype(seq)))
        self.assertEqual(len(results), 1)

    eleza test_copy(self):
        dup = self.s.copy()
        self.assertEqual(id(self.s), id(dup))

    eleza test_frozen_as_dictkey(self):
        seq = list(range(10)) + list('abcdefg') + ['apple']
        key1 = self.thetype(seq)
        key2 = self.thetype(reversed(seq))
        self.assertEqual(key1, key2)
        self.assertNotEqual(id(key1), id(key2))
        d = {}
        d[key1] = 42
        self.assertEqual(d[key2], 42)

    eleza test_hash_caching(self):
        f = self.thetype('abcdcda')
        self.assertEqual(hash(f), hash(f))

    eleza test_hash_effectiveness(self):
        n = 13
        hashvalues = set()
        addhashvalue = hashvalues.add
        elemmasks = [(i+1, 1<<i) kila i kwenye range(n)]
        kila i kwenye range(2**n):
            addhashvalue(hash(frozenset([e kila e, m kwenye elemmasks ikiwa m&i])))
        self.assertEqual(len(hashvalues), 2**n)

        eleza zf_range(n):
            # https://en.wikipedia.org/wiki/Set-theoretic_definition_of_natural_numbers
            nums = [frozenset()]
            kila i kwenye range(n-1):
                num = frozenset(nums)
                nums.append(num)
            rudisha nums[:n]

        eleza powerset(s):
            kila i kwenye range(len(s)+1):
                tuma kutoka map(frozenset, itertools.combinations(s, i))

        kila n kwenye range(18):
            t = 2 ** n
            mask = t - 1
            kila nums kwenye (range, zf_range):
                u = len({h & mask kila h kwenye map(hash, powerset(nums(n)))})
                self.assertGreater(4*u, t)

kundi FrozenSetSubclass(frozenset):
    pass

kundi TestFrozenSetSubclass(TestFrozenSet):
    thetype = FrozenSetSubclass
    basetype = frozenset

    eleza test_constructor_identity(self):
        s = self.thetype(range(3))
        t = self.thetype(s)
        self.assertNotEqual(id(s), id(t))

    eleza test_copy(self):
        dup = self.s.copy()
        self.assertNotEqual(id(self.s), id(dup))

    eleza test_nested_empty_constructor(self):
        s = self.thetype()
        t = self.thetype(s)
        self.assertEqual(s, t)

    eleza test_singleton_empty_frozenset(self):
        Frozenset = self.thetype
        f = frozenset()
        F = Frozenset()
        efs = [Frozenset(), Frozenset([]), Frozenset(()), Frozenset(''),
               Frozenset(), Frozenset([]), Frozenset(()), Frozenset(''),
               Frozenset(range(0)), Frozenset(Frozenset()),
               Frozenset(frozenset()), f, F, Frozenset(f), Frozenset(F)]
        # All empty frozenset subkundi instances should have different ids
        self.assertEqual(len(set(map(id, efs))), len(efs))

# Tests taken kutoka test_sets.py =============================================

empty_set = set()

#==============================================================================

kundi TestBasicOps:

    eleza test_repr(self):
        ikiwa self.repr ni sio Tupu:
            self.assertEqual(repr(self.set), self.repr)

    eleza check_repr_against_values(self):
        text = repr(self.set)
        self.assertKweli(text.startswith('{'))
        self.assertKweli(text.endswith('}'))

        result = text[1:-1].split(', ')
        result.sort()
        sorted_repr_values = [repr(value) kila value kwenye self.values]
        sorted_repr_values.sort()
        self.assertEqual(result, sorted_repr_values)

    eleza test_andika(self):
        jaribu:
            fo = open(support.TESTFN, "w")
            fo.write(str(self.set))
            fo.close()
            fo = open(support.TESTFN, "r")
            self.assertEqual(fo.read(), repr(self.set))
        mwishowe:
            fo.close()
            support.unlink(support.TESTFN)

    eleza test_length(self):
        self.assertEqual(len(self.set), self.length)

    eleza test_self_equality(self):
        self.assertEqual(self.set, self.set)

    eleza test_equivalent_equality(self):
        self.assertEqual(self.set, self.dup)

    eleza test_copy(self):
        self.assertEqual(self.set.copy(), self.dup)

    eleza test_self_union(self):
        result = self.set | self.set
        self.assertEqual(result, self.dup)

    eleza test_empty_union(self):
        result = self.set | empty_set
        self.assertEqual(result, self.dup)

    eleza test_union_empty(self):
        result = empty_set | self.set
        self.assertEqual(result, self.dup)

    eleza test_self_intersection(self):
        result = self.set & self.set
        self.assertEqual(result, self.dup)

    eleza test_empty_intersection(self):
        result = self.set & empty_set
        self.assertEqual(result, empty_set)

    eleza test_intersection_empty(self):
        result = empty_set & self.set
        self.assertEqual(result, empty_set)

    eleza test_self_isdisjoint(self):
        result = self.set.isdisjoint(self.set)
        self.assertEqual(result, sio self.set)

    eleza test_empty_isdisjoint(self):
        result = self.set.isdisjoint(empty_set)
        self.assertEqual(result, Kweli)

    eleza test_isdisjoint_empty(self):
        result = empty_set.isdisjoint(self.set)
        self.assertEqual(result, Kweli)

    eleza test_self_symmetric_difference(self):
        result = self.set ^ self.set
        self.assertEqual(result, empty_set)

    eleza test_empty_symmetric_difference(self):
        result = self.set ^ empty_set
        self.assertEqual(result, self.set)

    eleza test_self_difference(self):
        result = self.set - self.set
        self.assertEqual(result, empty_set)

    eleza test_empty_difference(self):
        result = self.set - empty_set
        self.assertEqual(result, self.dup)

    eleza test_empty_difference_rev(self):
        result = empty_set - self.set
        self.assertEqual(result, empty_set)

    eleza test_iteration(self):
        kila v kwenye self.set:
            self.assertIn(v, self.values)
        setiter = iter(self.set)
        self.assertEqual(setiter.__length_hint__(), len(self.set))

    eleza test_pickling(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            p = pickle.dumps(self.set, proto)
            copy = pickle.loads(p)
            self.assertEqual(self.set, copy,
                             "%s != %s" % (self.set, copy))

    eleza test_issue_37219(self):
        ukijumuisha self.assertRaises(TypeError):
            set().difference(123)
        ukijumuisha self.assertRaises(TypeError):
            set().difference_update(123)

#------------------------------------------------------------------------------

kundi TestBasicOpsEmpty(TestBasicOps, unittest.TestCase):
    eleza setUp(self):
        self.case   = "empty set"
        self.values = []
        self.set    = set(self.values)
        self.dup    = set(self.values)
        self.length = 0
        self.repr   = "set()"

#------------------------------------------------------------------------------

kundi TestBasicOpsSingleton(TestBasicOps, unittest.TestCase):
    eleza setUp(self):
        self.case   = "unit set (number)"
        self.values = [3]
        self.set    = set(self.values)
        self.dup    = set(self.values)
        self.length = 1
        self.repr   = "{3}"

    eleza test_in(self):
        self.assertIn(3, self.set)

    eleza test_not_in(self):
        self.assertNotIn(2, self.set)

#------------------------------------------------------------------------------

kundi TestBasicOpsTuple(TestBasicOps, unittest.TestCase):
    eleza setUp(self):
        self.case   = "unit set (tuple)"
        self.values = [(0, "zero")]
        self.set    = set(self.values)
        self.dup    = set(self.values)
        self.length = 1
        self.repr   = "{(0, 'zero')}"

    eleza test_in(self):
        self.assertIn((0, "zero"), self.set)

    eleza test_not_in(self):
        self.assertNotIn(9, self.set)

#------------------------------------------------------------------------------

kundi TestBasicOpsTriple(TestBasicOps, unittest.TestCase):
    eleza setUp(self):
        self.case   = "triple set"
        self.values = [0, "zero", operator.add]
        self.set    = set(self.values)
        self.dup    = set(self.values)
        self.length = 3
        self.repr   = Tupu

#------------------------------------------------------------------------------

kundi TestBasicOpsString(TestBasicOps, unittest.TestCase):
    eleza setUp(self):
        self.case   = "string set"
        self.values = ["a", "b", "c"]
        self.set    = set(self.values)
        self.dup    = set(self.values)
        self.length = 3

    eleza test_repr(self):
        self.check_repr_against_values()

#------------------------------------------------------------------------------

kundi TestBasicOpsBytes(TestBasicOps, unittest.TestCase):
    eleza setUp(self):
        self.case   = "bytes set"
        self.values = [b"a", b"b", b"c"]
        self.set    = set(self.values)
        self.dup    = set(self.values)
        self.length = 3

    eleza test_repr(self):
        self.check_repr_against_values()

#------------------------------------------------------------------------------

kundi TestBasicOpsMixedStringBytes(TestBasicOps, unittest.TestCase):
    eleza setUp(self):
        self._warning_filters = support.check_warnings()
        self._warning_filters.__enter__()
        warnings.simplefilter('ignore', BytesWarning)
        self.case   = "string na bytes set"
        self.values = ["a", "b", b"a", b"b"]
        self.set    = set(self.values)
        self.dup    = set(self.values)
        self.length = 4

    eleza tearDown(self):
        self._warning_filters.__exit__(Tupu, Tupu, Tupu)

    eleza test_repr(self):
        self.check_repr_against_values()

#==============================================================================

eleza baditer():
     ashiria TypeError
    tuma Kweli

eleza gooditer():
    tuma Kweli

kundi TestExceptionPropagation(unittest.TestCase):
    """SF 628246:  Set constructor should sio trap iterator TypeErrors"""

    eleza test_instanceWithException(self):
        self.assertRaises(TypeError, set, baditer())

    eleza test_instancesWithoutException(self):
        # All of these iterables should load without exception.
        set([1,2,3])
        set((1,2,3))
        set({'one':1, 'two':2, 'three':3})
        set(range(3))
        set('abc')
        set(gooditer())

    eleza test_changingSizeWhileIterating(self):
        s = set([1,2,3])
        jaribu:
            kila i kwenye s:
                s.update([4])
        except RuntimeError:
            pass
        isipokua:
            self.fail("no exception when changing size during iteration")

#==============================================================================

kundi TestSetOfSets(unittest.TestCase):
    eleza test_constructor(self):
        inner = frozenset([1])
        outer = set([inner])
        element = outer.pop()
        self.assertEqual(type(element), frozenset)
        outer.add(inner)        # Rebuild set of sets ukijumuisha .add method
        outer.remove(inner)
        self.assertEqual(outer, set())   # Verify that remove worked
        outer.discard(inner)    # Absence of KeyError indicates working fine

#==============================================================================

kundi TestBinaryOps(unittest.TestCase):
    eleza setUp(self):
        self.set = set((2, 4, 6))

    eleza test_eq(self):              # SF bug 643115
        self.assertEqual(self.set, set({2:1,4:3,6:5}))

    eleza test_union_subset(self):
        result = self.set | set([2])
        self.assertEqual(result, set((2, 4, 6)))

    eleza test_union_superset(self):
        result = self.set | set([2, 4, 6, 8])
        self.assertEqual(result, set([2, 4, 6, 8]))

    eleza test_union_overlap(self):
        result = self.set | set([3, 4, 5])
        self.assertEqual(result, set([2, 3, 4, 5, 6]))

    eleza test_union_non_overlap(self):
        result = self.set | set([8])
        self.assertEqual(result, set([2, 4, 6, 8]))

    eleza test_intersection_subset(self):
        result = self.set & set((2, 4))
        self.assertEqual(result, set((2, 4)))

    eleza test_intersection_superset(self):
        result = self.set & set([2, 4, 6, 8])
        self.assertEqual(result, set([2, 4, 6]))

    eleza test_intersection_overlap(self):
        result = self.set & set([3, 4, 5])
        self.assertEqual(result, set([4]))

    eleza test_intersection_non_overlap(self):
        result = self.set & set([8])
        self.assertEqual(result, empty_set)

    eleza test_isdisjoint_subset(self):
        result = self.set.isdisjoint(set((2, 4)))
        self.assertEqual(result, Uongo)

    eleza test_isdisjoint_superset(self):
        result = self.set.isdisjoint(set([2, 4, 6, 8]))
        self.assertEqual(result, Uongo)

    eleza test_isdisjoint_overlap(self):
        result = self.set.isdisjoint(set([3, 4, 5]))
        self.assertEqual(result, Uongo)

    eleza test_isdisjoint_non_overlap(self):
        result = self.set.isdisjoint(set([8]))
        self.assertEqual(result, Kweli)

    eleza test_sym_difference_subset(self):
        result = self.set ^ set((2, 4))
        self.assertEqual(result, set([6]))

    eleza test_sym_difference_superset(self):
        result = self.set ^ set((2, 4, 6, 8))
        self.assertEqual(result, set([8]))

    eleza test_sym_difference_overlap(self):
        result = self.set ^ set((3, 4, 5))
        self.assertEqual(result, set([2, 3, 5, 6]))

    eleza test_sym_difference_non_overlap(self):
        result = self.set ^ set([8])
        self.assertEqual(result, set([2, 4, 6, 8]))

#==============================================================================

kundi TestUpdateOps(unittest.TestCase):
    eleza setUp(self):
        self.set = set((2, 4, 6))

    eleza test_union_subset(self):
        self.set |= set([2])
        self.assertEqual(self.set, set((2, 4, 6)))

    eleza test_union_superset(self):
        self.set |= set([2, 4, 6, 8])
        self.assertEqual(self.set, set([2, 4, 6, 8]))

    eleza test_union_overlap(self):
        self.set |= set([3, 4, 5])
        self.assertEqual(self.set, set([2, 3, 4, 5, 6]))

    eleza test_union_non_overlap(self):
        self.set |= set([8])
        self.assertEqual(self.set, set([2, 4, 6, 8]))

    eleza test_union_method_call(self):
        self.set.update(set([3, 4, 5]))
        self.assertEqual(self.set, set([2, 3, 4, 5, 6]))

    eleza test_intersection_subset(self):
        self.set &= set((2, 4))
        self.assertEqual(self.set, set((2, 4)))

    eleza test_intersection_superset(self):
        self.set &= set([2, 4, 6, 8])
        self.assertEqual(self.set, set([2, 4, 6]))

    eleza test_intersection_overlap(self):
        self.set &= set([3, 4, 5])
        self.assertEqual(self.set, set([4]))

    eleza test_intersection_non_overlap(self):
        self.set &= set([8])
        self.assertEqual(self.set, empty_set)

    eleza test_intersection_method_call(self):
        self.set.intersection_update(set([3, 4, 5]))
        self.assertEqual(self.set, set([4]))

    eleza test_sym_difference_subset(self):
        self.set ^= set((2, 4))
        self.assertEqual(self.set, set([6]))

    eleza test_sym_difference_superset(self):
        self.set ^= set((2, 4, 6, 8))
        self.assertEqual(self.set, set([8]))

    eleza test_sym_difference_overlap(self):
        self.set ^= set((3, 4, 5))
        self.assertEqual(self.set, set([2, 3, 5, 6]))

    eleza test_sym_difference_non_overlap(self):
        self.set ^= set([8])
        self.assertEqual(self.set, set([2, 4, 6, 8]))

    eleza test_sym_difference_method_call(self):
        self.set.symmetric_difference_update(set([3, 4, 5]))
        self.assertEqual(self.set, set([2, 3, 5, 6]))

    eleza test_difference_subset(self):
        self.set -= set((2, 4))
        self.assertEqual(self.set, set([6]))

    eleza test_difference_superset(self):
        self.set -= set((2, 4, 6, 8))
        self.assertEqual(self.set, set([]))

    eleza test_difference_overlap(self):
        self.set -= set((3, 4, 5))
        self.assertEqual(self.set, set([2, 6]))

    eleza test_difference_non_overlap(self):
        self.set -= set([8])
        self.assertEqual(self.set, set([2, 4, 6]))

    eleza test_difference_method_call(self):
        self.set.difference_update(set([3, 4, 5]))
        self.assertEqual(self.set, set([2, 6]))

#==============================================================================

kundi TestMutate(unittest.TestCase):
    eleza setUp(self):
        self.values = ["a", "b", "c"]
        self.set = set(self.values)

    eleza test_add_present(self):
        self.set.add("c")
        self.assertEqual(self.set, set("abc"))

    eleza test_add_absent(self):
        self.set.add("d")
        self.assertEqual(self.set, set("abcd"))

    eleza test_add_until_full(self):
        tmp = set()
        expected_len = 0
        kila v kwenye self.values:
            tmp.add(v)
            expected_len += 1
            self.assertEqual(len(tmp), expected_len)
        self.assertEqual(tmp, self.set)

    eleza test_remove_present(self):
        self.set.remove("b")
        self.assertEqual(self.set, set("ac"))

    eleza test_remove_absent(self):
        jaribu:
            self.set.remove("d")
            self.fail("Removing missing element should have raised LookupError")
        except LookupError:
            pass

    eleza test_remove_until_empty(self):
        expected_len = len(self.set)
        kila v kwenye self.values:
            self.set.remove(v)
            expected_len -= 1
            self.assertEqual(len(self.set), expected_len)

    eleza test_discard_present(self):
        self.set.discard("c")
        self.assertEqual(self.set, set("ab"))

    eleza test_discard_absent(self):
        self.set.discard("d")
        self.assertEqual(self.set, set("abc"))

    eleza test_clear(self):
        self.set.clear()
        self.assertEqual(len(self.set), 0)

    eleza test_pop(self):
        popped = {}
        wakati self.set:
            popped[self.set.pop()] = Tupu
        self.assertEqual(len(popped), len(self.values))
        kila v kwenye self.values:
            self.assertIn(v, popped)

    eleza test_update_empty_tuple(self):
        self.set.update(())
        self.assertEqual(self.set, set(self.values))

    eleza test_update_unit_tuple_overlap(self):
        self.set.update(("a",))
        self.assertEqual(self.set, set(self.values))

    eleza test_update_unit_tuple_non_overlap(self):
        self.set.update(("a", "z"))
        self.assertEqual(self.set, set(self.values + ["z"]))

#==============================================================================

kundi TestSubsets:

    case2method = {"<=": "issubset",
                   ">=": "issuperset",
                  }

    reverse = {"==": "==",
               "!=": "!=",
               "<":  ">",
               ">":  "<",
               "<=": ">=",
               ">=": "<=",
              }

    eleza test_issubset(self):
        x = self.left
        y = self.right
        kila case kwenye "!=", "==", "<", "<=", ">", ">=":
            expected = case kwenye self.cases
            # Test the binary infix spelling.
            result = eval("x" + case + "y", locals())
            self.assertEqual(result, expected)
            # Test the "friendly" method-name spelling, ikiwa one exists.
            ikiwa case kwenye TestSubsets.case2method:
                method = getattr(x, TestSubsets.case2method[case])
                result = method(y)
                self.assertEqual(result, expected)

            # Now do the same kila the operands reversed.
            rcase = TestSubsets.reverse[case]
            result = eval("y" + rcase + "x", locals())
            self.assertEqual(result, expected)
            ikiwa rcase kwenye TestSubsets.case2method:
                method = getattr(y, TestSubsets.case2method[rcase])
                result = method(x)
                self.assertEqual(result, expected)
#------------------------------------------------------------------------------

kundi TestSubsetEqualEmpty(TestSubsets, unittest.TestCase):
    left  = set()
    right = set()
    name  = "both empty"
    cases = "==", "<=", ">="

#------------------------------------------------------------------------------

kundi TestSubsetEqualNonEmpty(TestSubsets, unittest.TestCase):
    left  = set([1, 2])
    right = set([1, 2])
    name  = "equal pair"
    cases = "==", "<=", ">="

#------------------------------------------------------------------------------

kundi TestSubsetEmptyNonEmpty(TestSubsets, unittest.TestCase):
    left  = set()
    right = set([1, 2])
    name  = "one empty, one non-empty"
    cases = "!=", "<", "<="

#------------------------------------------------------------------------------

kundi TestSubsetPartial(TestSubsets, unittest.TestCase):
    left  = set([1])
    right = set([1, 2])
    name  = "one a non-empty proper subset of other"
    cases = "!=", "<", "<="

#------------------------------------------------------------------------------

kundi TestSubsetNonOverlap(TestSubsets, unittest.TestCase):
    left  = set([1])
    right = set([2])
    name  = "neither empty, neither contains"
    cases = "!="

#==============================================================================

kundi TestOnlySetsInBinaryOps:

    eleza test_eq_ne(self):
        # Unlike the others, this ni testing that == na != *are* allowed.
        self.assertEqual(self.other == self.set, Uongo)
        self.assertEqual(self.set == self.other, Uongo)
        self.assertEqual(self.other != self.set, Kweli)
        self.assertEqual(self.set != self.other, Kweli)

    eleza test_ge_gt_le_lt(self):
        self.assertRaises(TypeError, lambda: self.set < self.other)
        self.assertRaises(TypeError, lambda: self.set <= self.other)
        self.assertRaises(TypeError, lambda: self.set > self.other)
        self.assertRaises(TypeError, lambda: self.set >= self.other)

        self.assertRaises(TypeError, lambda: self.other < self.set)
        self.assertRaises(TypeError, lambda: self.other <= self.set)
        self.assertRaises(TypeError, lambda: self.other > self.set)
        self.assertRaises(TypeError, lambda: self.other >= self.set)

    eleza test_update_operator(self):
        jaribu:
            self.set |= self.other
        except TypeError:
            pass
        isipokua:
            self.fail("expected TypeError")

    eleza test_update(self):
        ikiwa self.otherIsIterable:
            self.set.update(self.other)
        isipokua:
            self.assertRaises(TypeError, self.set.update, self.other)

    eleza test_union(self):
        self.assertRaises(TypeError, lambda: self.set | self.other)
        self.assertRaises(TypeError, lambda: self.other | self.set)
        ikiwa self.otherIsIterable:
            self.set.union(self.other)
        isipokua:
            self.assertRaises(TypeError, self.set.union, self.other)

    eleza test_intersection_update_operator(self):
        jaribu:
            self.set &= self.other
        except TypeError:
            pass
        isipokua:
            self.fail("expected TypeError")

    eleza test_intersection_update(self):
        ikiwa self.otherIsIterable:
            self.set.intersection_update(self.other)
        isipokua:
            self.assertRaises(TypeError,
                              self.set.intersection_update,
                              self.other)

    eleza test_intersection(self):
        self.assertRaises(TypeError, lambda: self.set & self.other)
        self.assertRaises(TypeError, lambda: self.other & self.set)
        ikiwa self.otherIsIterable:
            self.set.intersection(self.other)
        isipokua:
            self.assertRaises(TypeError, self.set.intersection, self.other)

    eleza test_sym_difference_update_operator(self):
        jaribu:
            self.set ^= self.other
        except TypeError:
            pass
        isipokua:
            self.fail("expected TypeError")

    eleza test_sym_difference_update(self):
        ikiwa self.otherIsIterable:
            self.set.symmetric_difference_update(self.other)
        isipokua:
            self.assertRaises(TypeError,
                              self.set.symmetric_difference_update,
                              self.other)

    eleza test_sym_difference(self):
        self.assertRaises(TypeError, lambda: self.set ^ self.other)
        self.assertRaises(TypeError, lambda: self.other ^ self.set)
        ikiwa self.otherIsIterable:
            self.set.symmetric_difference(self.other)
        isipokua:
            self.assertRaises(TypeError, self.set.symmetric_difference, self.other)

    eleza test_difference_update_operator(self):
        jaribu:
            self.set -= self.other
        except TypeError:
            pass
        isipokua:
            self.fail("expected TypeError")

    eleza test_difference_update(self):
        ikiwa self.otherIsIterable:
            self.set.difference_update(self.other)
        isipokua:
            self.assertRaises(TypeError,
                              self.set.difference_update,
                              self.other)

    eleza test_difference(self):
        self.assertRaises(TypeError, lambda: self.set - self.other)
        self.assertRaises(TypeError, lambda: self.other - self.set)
        ikiwa self.otherIsIterable:
            self.set.difference(self.other)
        isipokua:
            self.assertRaises(TypeError, self.set.difference, self.other)

#------------------------------------------------------------------------------

kundi TestOnlySetsNumeric(TestOnlySetsInBinaryOps, unittest.TestCase):
    eleza setUp(self):
        self.set   = set((1, 2, 3))
        self.other = 19
        self.otherIsIterable = Uongo

#------------------------------------------------------------------------------

kundi TestOnlySetsDict(TestOnlySetsInBinaryOps, unittest.TestCase):
    eleza setUp(self):
        self.set   = set((1, 2, 3))
        self.other = {1:2, 3:4}
        self.otherIsIterable = Kweli

#------------------------------------------------------------------------------

kundi TestOnlySetsOperator(TestOnlySetsInBinaryOps, unittest.TestCase):
    eleza setUp(self):
        self.set   = set((1, 2, 3))
        self.other = operator.add
        self.otherIsIterable = Uongo

#------------------------------------------------------------------------------

kundi TestOnlySetsTuple(TestOnlySetsInBinaryOps, unittest.TestCase):
    eleza setUp(self):
        self.set   = set((1, 2, 3))
        self.other = (2, 4, 6)
        self.otherIsIterable = Kweli

#------------------------------------------------------------------------------

kundi TestOnlySetsString(TestOnlySetsInBinaryOps, unittest.TestCase):
    eleza setUp(self):
        self.set   = set((1, 2, 3))
        self.other = 'abc'
        self.otherIsIterable = Kweli

#------------------------------------------------------------------------------

kundi TestOnlySetsGenerator(TestOnlySetsInBinaryOps, unittest.TestCase):
    eleza setUp(self):
        eleza gen():
            kila i kwenye range(0, 10, 2):
                tuma i
        self.set   = set((1, 2, 3))
        self.other = gen()
        self.otherIsIterable = Kweli

#==============================================================================

kundi TestCopying:

    eleza test_copy(self):
        dup = self.set.copy()
        dup_list = sorted(dup, key=repr)
        set_list = sorted(self.set, key=repr)
        self.assertEqual(len(dup_list), len(set_list))
        kila i kwenye range(len(dup_list)):
            self.assertKweli(dup_list[i] ni set_list[i])

    eleza test_deep_copy(self):
        dup = copy.deepcopy(self.set)
        ##print type(dup), repr(dup)
        dup_list = sorted(dup, key=repr)
        set_list = sorted(self.set, key=repr)
        self.assertEqual(len(dup_list), len(set_list))
        kila i kwenye range(len(dup_list)):
            self.assertEqual(dup_list[i], set_list[i])

#------------------------------------------------------------------------------

kundi TestCopyingEmpty(TestCopying, unittest.TestCase):
    eleza setUp(self):
        self.set = set()

#------------------------------------------------------------------------------

kundi TestCopyingSingleton(TestCopying, unittest.TestCase):
    eleza setUp(self):
        self.set = set(["hello"])

#------------------------------------------------------------------------------

kundi TestCopyingTriple(TestCopying, unittest.TestCase):
    eleza setUp(self):
        self.set = set(["zero", 0, Tupu])

#------------------------------------------------------------------------------

kundi TestCopyingTuple(TestCopying, unittest.TestCase):
    eleza setUp(self):
        self.set = set([(1, 2)])

#------------------------------------------------------------------------------

kundi TestCopyingNested(TestCopying, unittest.TestCase):
    eleza setUp(self):
        self.set = set([((1, 2), (3, 4))])

#==============================================================================

kundi TestIdentities(unittest.TestCase):
    eleza setUp(self):
        self.a = set('abracadabra')
        self.b = set('alacazam')

    eleza test_binopsVsSubsets(self):
        a, b = self.a, self.b
        self.assertKweli(a - b < a)
        self.assertKweli(b - a < b)
        self.assertKweli(a & b < a)
        self.assertKweli(a & b < b)
        self.assertKweli(a | b > a)
        self.assertKweli(a | b > b)
        self.assertKweli(a ^ b < a | b)

    eleza test_commutativity(self):
        a, b = self.a, self.b
        self.assertEqual(a&b, b&a)
        self.assertEqual(a|b, b|a)
        self.assertEqual(a^b, b^a)
        ikiwa a != b:
            self.assertNotEqual(a-b, b-a)

    eleza test_summations(self):
        # check that sums of parts equal the whole
        a, b = self.a, self.b
        self.assertEqual((a-b)|(a&b)|(b-a), a|b)
        self.assertEqual((a&b)|(a^b), a|b)
        self.assertEqual(a|(b-a), a|b)
        self.assertEqual((a-b)|b, a|b)
        self.assertEqual((a-b)|(a&b), a)
        self.assertEqual((b-a)|(a&b), b)
        self.assertEqual((a-b)|(b-a), a^b)

    eleza test_exclusion(self):
        # check that inverse operations show non-overlap
        a, b, zero = self.a, self.b, set()
        self.assertEqual((a-b)&b, zero)
        self.assertEqual((b-a)&a, zero)
        self.assertEqual((a&b)&(a^b), zero)

# Tests derived kutoka test_itertools.py =======================================

eleza R(seqn):
    'Regular generator'
    kila i kwenye seqn:
        tuma i

kundi G:
    'Sequence using __getitem__'
    eleza __init__(self, seqn):
        self.seqn = seqn
    eleza __getitem__(self, i):
        rudisha self.seqn[i]

kundi I:
    'Sequence using iterator protocol'
    eleza __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    eleza __iter__(self):
        rudisha self
    eleza __next__(self):
        ikiwa self.i >= len(self.seqn):  ashiria StopIteration
        v = self.seqn[self.i]
        self.i += 1
        rudisha v

kundi Ig:
    'Sequence using iterator protocol defined ukijumuisha a generator'
    eleza __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    eleza __iter__(self):
        kila val kwenye self.seqn:
            tuma val

kundi X:
    'Missing __getitem__ na __iter__'
    eleza __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    eleza __next__(self):
        ikiwa self.i >= len(self.seqn):  ashiria StopIteration
        v = self.seqn[self.i]
        self.i += 1
        rudisha v

kundi N:
    'Iterator missing __next__()'
    eleza __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    eleza __iter__(self):
        rudisha self

kundi E:
    'Test propagation of exceptions'
    eleza __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    eleza __iter__(self):
        rudisha self
    eleza __next__(self):
        3 // 0

kundi S:
    'Test immediate stop'
    eleza __init__(self, seqn):
        pass
    eleza __iter__(self):
        rudisha self
    eleza __next__(self):
         ashiria StopIteration

kutoka itertools agiza chain
eleza L(seqn):
    'Test multiple tiers of iterators'
    rudisha chain(map(lambda x:x, R(Ig(G(seqn)))))

kundi TestVariousIteratorArgs(unittest.TestCase):

    eleza test_constructor(self):
        kila cons kwenye (set, frozenset):
            kila s kwenye ("123", "", range(1000), ('do', 1.2), range(2000,2200,5)):
                kila g kwenye (G, I, Ig, S, L, R):
                    self.assertEqual(sorted(cons(g(s)), key=repr), sorted(g(s), key=repr))
                self.assertRaises(TypeError, cons , X(s))
                self.assertRaises(TypeError, cons , N(s))
                self.assertRaises(ZeroDivisionError, cons , E(s))

    eleza test_inline_methods(self):
        s = set('november')
        kila data kwenye ("123", "", range(1000), ('do', 1.2), range(2000,2200,5), 'december'):
            kila meth kwenye (s.union, s.intersection, s.difference, s.symmetric_difference, s.isdisjoint):
                kila g kwenye (G, I, Ig, L, R):
                    expected = meth(data)
                    actual = meth(g(data))
                    ikiwa isinstance(expected, bool):
                        self.assertEqual(actual, expected)
                    isipokua:
                        self.assertEqual(sorted(actual, key=repr), sorted(expected, key=repr))
                self.assertRaises(TypeError, meth, X(s))
                self.assertRaises(TypeError, meth, N(s))
                self.assertRaises(ZeroDivisionError, meth, E(s))

    eleza test_inplace_methods(self):
        kila data kwenye ("123", "", range(1000), ('do', 1.2), range(2000,2200,5), 'december'):
            kila methname kwenye ('update', 'intersection_update',
                             'difference_update', 'symmetric_difference_update'):
                kila g kwenye (G, I, Ig, S, L, R):
                    s = set('january')
                    t = s.copy()
                    getattr(s, methname)(list(g(data)))
                    getattr(t, methname)(g(data))
                    self.assertEqual(sorted(s, key=repr), sorted(t, key=repr))

                self.assertRaises(TypeError, getattr(set('january'), methname), X(data))
                self.assertRaises(TypeError, getattr(set('january'), methname), N(data))
                self.assertRaises(ZeroDivisionError, getattr(set('january'), methname), E(data))

kundi bad_eq:
    eleza __eq__(self, other):
        ikiwa be_bad:
            set2.clear()
             ashiria ZeroDivisionError
        rudisha self ni other
    eleza __hash__(self):
        rudisha 0

kundi bad_dict_clear:
    eleza __eq__(self, other):
        ikiwa be_bad:
            dict2.clear()
        rudisha self ni other
    eleza __hash__(self):
        rudisha 0

kundi TestWeirdBugs(unittest.TestCase):
    eleza test_8420_set_merge(self):
        # This used to segfault
        global be_bad, set2, dict2
        be_bad = Uongo
        set1 = {bad_eq()}
        set2 = {bad_eq() kila i kwenye range(75)}
        be_bad = Kweli
        self.assertRaises(ZeroDivisionError, set1.update, set2)

        be_bad = Uongo
        set1 = {bad_dict_clear()}
        dict2 = {bad_dict_clear(): Tupu}
        be_bad = Kweli
        set1.symmetric_difference_update(dict2)

    eleza test_iter_and_mutate(self):
        # Issue #24581
        s = set(range(100))
        s.clear()
        s.update(range(100))
        si = iter(s)
        s.clear()
        a = list(range(100))
        s.update(range(100))
        list(si)

    eleza test_merge_and_mutate(self):
        kundi X:
            eleza __hash__(self):
                rudisha hash(0)
            eleza __eq__(self, o):
                other.clear()
                rudisha Uongo

        other = set()
        other = {X() kila i kwenye range(10)}
        s = {0}
        s.update(other)

# Application tests (based on David Eppstein's graph recipes ====================================

eleza powerset(U):
    """Generates all subsets of a set ama sequence U."""
    U = iter(U)
    jaribu:
        x = frozenset([next(U)])
        kila S kwenye powerset(U):
            tuma S
            tuma S | x
    except StopIteration:
        tuma frozenset()

eleza cube(n):
    """Graph of n-dimensional hypercube."""
    singletons = [frozenset([x]) kila x kwenye range(n)]
    rudisha dict([(x, frozenset([x^s kila s kwenye singletons]))
                 kila x kwenye powerset(range(n))])

eleza linegraph(G):
    """Graph, the vertices of which are edges of G,
    ukijumuisha two vertices being adjacent iff the corresponding
    edges share a vertex."""
    L = {}
    kila x kwenye G:
        kila y kwenye G[x]:
            nx = [frozenset([x,z]) kila z kwenye G[x] ikiwa z != y]
            ny = [frozenset([y,z]) kila z kwenye G[y] ikiwa z != x]
            L[frozenset([x,y])] = frozenset(nx+ny)
    rudisha L

eleza faces(G):
    'Return a set of faces kwenye G.  Where a face ni a set of vertices on that face'
    # currently limited to triangles,squares, na pentagons
    f = set()
    kila v1, edges kwenye G.items():
        kila v2 kwenye edges:
            kila v3 kwenye G[v2]:
                ikiwa v1 == v3:
                    endelea
                ikiwa v1 kwenye G[v3]:
                    f.add(frozenset([v1, v2, v3]))
                isipokua:
                    kila v4 kwenye G[v3]:
                        ikiwa v4 == v2:
                            endelea
                        ikiwa v1 kwenye G[v4]:
                            f.add(frozenset([v1, v2, v3, v4]))
                        isipokua:
                            kila v5 kwenye G[v4]:
                                ikiwa v5 == v3 ama v5 == v2:
                                    endelea
                                ikiwa v1 kwenye G[v5]:
                                    f.add(frozenset([v1, v2, v3, v4, v5]))
    rudisha f


kundi TestGraphs(unittest.TestCase):

    eleza test_cube(self):

        g = cube(3)                             # vert --> {v1, v2, v3}
        vertices1 = set(g)
        self.assertEqual(len(vertices1), 8)     # eight vertices
        kila edge kwenye g.values():
            self.assertEqual(len(edge), 3)      # each vertex connects to three edges
        vertices2 = set(v kila edges kwenye g.values() kila v kwenye edges)
        self.assertEqual(vertices1, vertices2)  # edge vertices kwenye original set

        cubefaces = faces(g)
        self.assertEqual(len(cubefaces), 6)     # six faces
        kila face kwenye cubefaces:
            self.assertEqual(len(face), 4)      # each face ni a square

    eleza test_cuboctahedron(self):

        # http://en.wikipedia.org/wiki/Cuboctahedron
        # 8 triangular faces na 6 square faces
        # 12 identical vertices each connecting a triangle na square

        g = cube(3)
        cuboctahedron = linegraph(g)            # V( --> {V1, V2, V3, V4}
        self.assertEqual(len(cuboctahedron), 12)# twelve vertices

        vertices = set(cuboctahedron)
        kila edges kwenye cuboctahedron.values():
            self.assertEqual(len(edges), 4)     # each vertex connects to four other vertices
        othervertices = set(edge kila edges kwenye cuboctahedron.values() kila edge kwenye edges)
        self.assertEqual(vertices, othervertices)   # edge vertices kwenye original set

        cubofaces = faces(cuboctahedron)
        facesizes = collections.defaultdict(int)
        kila face kwenye cubofaces:
            facesizes[len(face)] += 1
        self.assertEqual(facesizes[3], 8)       # eight triangular faces
        self.assertEqual(facesizes[4], 6)       # six square faces

        kila vertex kwenye cuboctahedron:
            edge = vertex                       # Cuboctahedron vertices are edges kwenye Cube
            self.assertEqual(len(edge), 2)      # Two cube vertices define an edge
            kila cubevert kwenye edge:
                self.assertIn(cubevert, g)


#==============================================================================

ikiwa __name__ == "__main__":
    unittest.main()
