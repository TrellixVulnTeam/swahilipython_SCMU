agiza unittest
kutoka weakref agiza WeakSet
agiza string
kutoka collections agiza UserString kama ustr
agiza gc
agiza contextlib


kundi Foo:
    pita

kundi RefCycle:
    eleza __init__(self):
        self.cycle = self


kundi TestWeakSet(unittest.TestCase):

    eleza setUp(self):
        # need to keep references to them
        self.items = [ustr(c) kila c kwenye ('a', 'b', 'c')]
        self.items2 = [ustr(c) kila c kwenye ('x', 'y', 'z')]
        self.ab_items = [ustr(c) kila c kwenye 'ab']
        self.abcde_items = [ustr(c) kila c kwenye 'abcde']
        self.def_items = [ustr(c) kila c kwenye 'def']
        self.ab_weakset = WeakSet(self.ab_items)
        self.abcde_weakset = WeakSet(self.abcde_items)
        self.def_weakset = WeakSet(self.def_items)
        self.letters = [ustr(c) kila c kwenye string.ascii_letters]
        self.s = WeakSet(self.items)
        self.d = dict.fromkeys(self.items)
        self.obj = ustr('F')
        self.fs = WeakSet([self.obj])

    eleza test_methods(self):
        weaksetmethods = dir(WeakSet)
        kila method kwenye dir(set):
            ikiwa method == 'test_c_api' ama method.startswith('_'):
                endelea
            self.assertIn(method, weaksetmethods,
                         "WeakSet missing method " + method)

    eleza test_new_or_init(self):
        self.assertRaises(TypeError, WeakSet, [], 2)

    eleza test_len(self):
        self.assertEqual(len(self.s), len(self.d))
        self.assertEqual(len(self.fs), 1)
        toa self.obj
        self.assertEqual(len(self.fs), 0)

    eleza test_contains(self):
        kila c kwenye self.letters:
            self.assertEqual(c kwenye self.s, c kwenye self.d)
        # 1 ni sio weakref'able, but that TypeError ni caught by __contains__
        self.assertNotIn(1, self.s)
        self.assertIn(self.obj, self.fs)
        toa self.obj
        self.assertNotIn(ustr('F'), self.fs)

    eleza test_union(self):
        u = self.s.union(self.items2)
        kila c kwenye self.letters:
            self.assertEqual(c kwenye u, c kwenye self.d ama c kwenye self.items2)
        self.assertEqual(self.s, WeakSet(self.items))
        self.assertEqual(type(u), WeakSet)
        self.assertRaises(TypeError, self.s.union, [[]])
        kila C kwenye set, frozenset, dict.fromkeys, list, tuple:
            x = WeakSet(self.items + self.items2)
            c = C(self.items2)
            self.assertEqual(self.s.union(c), x)
            toa c
        self.assertEqual(len(u), len(self.items) + len(self.items2))
        self.items2.pop()
        gc.collect()
        self.assertEqual(len(u), len(self.items) + len(self.items2))

    eleza test_or(self):
        i = self.s.union(self.items2)
        self.assertEqual(self.s | set(self.items2), i)
        self.assertEqual(self.s | frozenset(self.items2), i)

    eleza test_intersection(self):
        s = WeakSet(self.letters)
        i = s.intersection(self.items2)
        kila c kwenye self.letters:
            self.assertEqual(c kwenye i, c kwenye self.items2 na c kwenye self.letters)
        self.assertEqual(s, WeakSet(self.letters))
        self.assertEqual(type(i), WeakSet)
        kila C kwenye set, frozenset, dict.fromkeys, list, tuple:
            x = WeakSet([])
            self.assertEqual(i.intersection(C(self.items)), x)
        self.assertEqual(len(i), len(self.items2))
        self.items2.pop()
        gc.collect()
        self.assertEqual(len(i), len(self.items2))

    eleza test_isdisjoint(self):
        self.assertKweli(self.s.isdisjoint(WeakSet(self.items2)))
        self.assertKweli(sio self.s.isdisjoint(WeakSet(self.letters)))

    eleza test_and(self):
        i = self.s.intersection(self.items2)
        self.assertEqual(self.s & set(self.items2), i)
        self.assertEqual(self.s & frozenset(self.items2), i)

    eleza test_difference(self):
        i = self.s.difference(self.items2)
        kila c kwenye self.letters:
            self.assertEqual(c kwenye i, c kwenye self.d na c haiko kwenye self.items2)
        self.assertEqual(self.s, WeakSet(self.items))
        self.assertEqual(type(i), WeakSet)
        self.assertRaises(TypeError, self.s.difference, [[]])

    eleza test_sub(self):
        i = self.s.difference(self.items2)
        self.assertEqual(self.s - set(self.items2), i)
        self.assertEqual(self.s - frozenset(self.items2), i)

    eleza test_symmetric_difference(self):
        i = self.s.symmetric_difference(self.items2)
        kila c kwenye self.letters:
            self.assertEqual(c kwenye i, (c kwenye self.d) ^ (c kwenye self.items2))
        self.assertEqual(self.s, WeakSet(self.items))
        self.assertEqual(type(i), WeakSet)
        self.assertRaises(TypeError, self.s.symmetric_difference, [[]])
        self.assertEqual(len(i), len(self.items) + len(self.items2))
        self.items2.pop()
        gc.collect()
        self.assertEqual(len(i), len(self.items) + len(self.items2))

    eleza test_xor(self):
        i = self.s.symmetric_difference(self.items2)
        self.assertEqual(self.s ^ set(self.items2), i)
        self.assertEqual(self.s ^ frozenset(self.items2), i)

    eleza test_sub_and_super(self):
        self.assertKweli(self.ab_weakset <= self.abcde_weakset)
        self.assertKweli(self.abcde_weakset <= self.abcde_weakset)
        self.assertKweli(self.abcde_weakset >= self.ab_weakset)
        self.assertUongo(self.abcde_weakset <= self.def_weakset)
        self.assertUongo(self.abcde_weakset >= self.def_weakset)
        self.assertKweli(set('a').issubset('abc'))
        self.assertKweli(set('abc').issuperset('a'))
        self.assertUongo(set('a').issubset('cbs'))
        self.assertUongo(set('cbs').issuperset('a'))

    eleza test_lt(self):
        self.assertKweli(self.ab_weakset < self.abcde_weakset)
        self.assertUongo(self.abcde_weakset < self.def_weakset)
        self.assertUongo(self.ab_weakset < self.ab_weakset)
        self.assertUongo(WeakSet() < WeakSet())

    eleza test_gt(self):
        self.assertKweli(self.abcde_weakset > self.ab_weakset)
        self.assertUongo(self.abcde_weakset > self.def_weakset)
        self.assertUongo(self.ab_weakset > self.ab_weakset)
        self.assertUongo(WeakSet() > WeakSet())

    eleza test_gc(self):
        # Create a nest of cycles to exercise overall ref count check
        s = WeakSet(Foo() kila i kwenye range(1000))
        kila elem kwenye s:
            elem.cycle = s
            elem.sub = elem
            elem.set = WeakSet([elem])

    eleza test_subclass_with_custom_hash(self):
        # Bug #1257731
        kundi H(WeakSet):
            eleza __hash__(self):
                rudisha int(id(self) & 0x7fffffff)
        s=H()
        f=set()
        f.add(s)
        self.assertIn(s, f)
        f.remove(s)
        f.add(s)
        f.discard(s)

    eleza test_init(self):
        s = WeakSet()
        s.__init__(self.items)
        self.assertEqual(s, self.s)
        s.__init__(self.items2)
        self.assertEqual(s, WeakSet(self.items2))
        self.assertRaises(TypeError, s.__init__, s, 2);
        self.assertRaises(TypeError, s.__init__, 1);

    eleza test_constructor_identity(self):
        s = WeakSet(self.items)
        t = WeakSet(s)
        self.assertNotEqual(id(s), id(t))

    eleza test_hash(self):
        self.assertRaises(TypeError, hash, self.s)

    eleza test_clear(self):
        self.s.clear()
        self.assertEqual(self.s, WeakSet([]))
        self.assertEqual(len(self.s), 0)

    eleza test_copy(self):
        dup = self.s.copy()
        self.assertEqual(self.s, dup)
        self.assertNotEqual(id(self.s), id(dup))

    eleza test_add(self):
        x = ustr('Q')
        self.s.add(x)
        self.assertIn(x, self.s)
        dup = self.s.copy()
        self.s.add(x)
        self.assertEqual(self.s, dup)
        self.assertRaises(TypeError, self.s.add, [])
        self.fs.add(Foo())
        self.assertKweli(len(self.fs) == 1)
        self.fs.add(self.obj)
        self.assertKweli(len(self.fs) == 1)

    eleza test_remove(self):
        x = ustr('a')
        self.s.remove(x)
        self.assertNotIn(x, self.s)
        self.assertRaises(KeyError, self.s.remove, x)
        self.assertRaises(TypeError, self.s.remove, [])

    eleza test_discard(self):
        a, q = ustr('a'), ustr('Q')
        self.s.discard(a)
        self.assertNotIn(a, self.s)
        self.s.discard(q)
        self.assertRaises(TypeError, self.s.discard, [])

    eleza test_pop(self):
        kila i kwenye range(len(self.s)):
            elem = self.s.pop()
            self.assertNotIn(elem, self.s)
        self.assertRaises(KeyError, self.s.pop)

    eleza test_update(self):
        retval = self.s.update(self.items2)
        self.assertEqual(retval, Tupu)
        kila c kwenye (self.items + self.items2):
            self.assertIn(c, self.s)
        self.assertRaises(TypeError, self.s.update, [[]])

    eleza test_update_set(self):
        self.s.update(set(self.items2))
        kila c kwenye (self.items + self.items2):
            self.assertIn(c, self.s)

    eleza test_ior(self):
        self.s |= set(self.items2)
        kila c kwenye (self.items + self.items2):
            self.assertIn(c, self.s)

    eleza test_intersection_update(self):
        retval = self.s.intersection_update(self.items2)
        self.assertEqual(retval, Tupu)
        kila c kwenye (self.items + self.items2):
            ikiwa c kwenye self.items2 na c kwenye self.items:
                self.assertIn(c, self.s)
            isipokua:
                self.assertNotIn(c, self.s)
        self.assertRaises(TypeError, self.s.intersection_update, [[]])

    eleza test_iand(self):
        self.s &= set(self.items2)
        kila c kwenye (self.items + self.items2):
            ikiwa c kwenye self.items2 na c kwenye self.items:
                self.assertIn(c, self.s)
            isipokua:
                self.assertNotIn(c, self.s)

    eleza test_difference_update(self):
        retval = self.s.difference_update(self.items2)
        self.assertEqual(retval, Tupu)
        kila c kwenye (self.items + self.items2):
            ikiwa c kwenye self.items na c haiko kwenye self.items2:
                self.assertIn(c, self.s)
            isipokua:
                self.assertNotIn(c, self.s)
        self.assertRaises(TypeError, self.s.difference_update, [[]])
        self.assertRaises(TypeError, self.s.symmetric_difference_update, [[]])

    eleza test_isub(self):
        self.s -= set(self.items2)
        kila c kwenye (self.items + self.items2):
            ikiwa c kwenye self.items na c haiko kwenye self.items2:
                self.assertIn(c, self.s)
            isipokua:
                self.assertNotIn(c, self.s)

    eleza test_symmetric_difference_update(self):
        retval = self.s.symmetric_difference_update(self.items2)
        self.assertEqual(retval, Tupu)
        kila c kwenye (self.items + self.items2):
            ikiwa (c kwenye self.items) ^ (c kwenye self.items2):
                self.assertIn(c, self.s)
            isipokua:
                self.assertNotIn(c, self.s)
        self.assertRaises(TypeError, self.s.symmetric_difference_update, [[]])

    eleza test_ixor(self):
        self.s ^= set(self.items2)
        kila c kwenye (self.items + self.items2):
            ikiwa (c kwenye self.items) ^ (c kwenye self.items2):
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
        self.assertEqual(t, WeakSet())
        t = self.s.copy()
        t ^= t
        self.assertEqual(t, WeakSet())

    eleza test_eq(self):
        # issue 5964
        self.assertKweli(self.s == self.s)
        self.assertKweli(self.s == WeakSet(self.items))
        self.assertUongo(self.s == set(self.items))
        self.assertUongo(self.s == list(self.items))
        self.assertUongo(self.s == tuple(self.items))
        self.assertUongo(self.s == WeakSet([Foo]))
        self.assertUongo(self.s == 1)

    eleza test_ne(self):
        self.assertKweli(self.s != set(self.items))
        s1 = WeakSet()
        s2 = WeakSet()
        self.assertUongo(s1 != s2)

    eleza test_weak_destroy_while_iterating(self):
        # Issue #7105: iterators shouldn't crash when a key ni implicitly removed
        # Create new items to be sure no-one isipokua holds a reference
        items = [ustr(c) kila c kwenye ('a', 'b', 'c')]
        s = WeakSet(items)
        it = iter(s)
        next(it)             # Trigger internal iteration
        # Destroy an item
        toa items[-1]
        gc.collect()    # just kwenye case
        # We have removed either the first consumed items, ama another one
        self.assertIn(len(list(it)), [len(items), len(items) - 1])
        toa it
        # The removal has been committed
        self.assertEqual(len(s), len(items))

    eleza test_weak_destroy_and_mutate_while_iterating(self):
        # Issue #7105: iterators shouldn't crash when a key ni implicitly removed
        items = [ustr(c) kila c kwenye string.ascii_letters]
        s = WeakSet(items)
        @contextlib.contextmanager
        eleza testcontext():
            jaribu:
                it = iter(s)
                # Start iterator
                tumaed = ustr(str(next(it)))
                # Schedule an item kila removal na recreate it
                u = ustr(str(items.pop()))
                ikiwa tumaed == u:
                    # The iterator still has a reference to the removed item,
                    # advance it (issue #20006).
                    next(it)
                gc.collect()      # just kwenye case
                tuma u
            mwishowe:
                it = Tupu           # should commit all removals

        ukijumuisha testcontext() kama u:
            self.assertNotIn(u, s)
        ukijumuisha testcontext() kama u:
            self.assertRaises(KeyError, s.remove, u)
        self.assertNotIn(u, s)
        ukijumuisha testcontext() kama u:
            s.add(u)
        self.assertIn(u, s)
        t = s.copy()
        ukijumuisha testcontext() kama u:
            s.update(t)
        self.assertEqual(len(s), len(t))
        ukijumuisha testcontext() kama u:
            s.clear()
        self.assertEqual(len(s), 0)

    eleza test_len_cycles(self):
        N = 20
        items = [RefCycle() kila i kwenye range(N)]
        s = WeakSet(items)
        toa items
        it = iter(s)
        jaribu:
            next(it)
        tatizo StopIteration:
            pita
        gc.collect()
        n1 = len(s)
        toa it
        gc.collect()
        n2 = len(s)
        # one item may be kept alive inside the iterator
        self.assertIn(n1, (0, 1))
        self.assertEqual(n2, 0)

    eleza test_len_race(self):
        # Extended sanity checks kila len() kwenye the face of cyclic collection
        self.addCleanup(gc.set_threshold, *gc.get_threshold())
        kila th kwenye range(1, 100):
            N = 20
            gc.collect(0)
            gc.set_threshold(th, th, th)
            items = [RefCycle() kila i kwenye range(N)]
            s = WeakSet(items)
            toa items
            # All items will be collected at next garbage collection pita
            it = iter(s)
            jaribu:
                next(it)
            tatizo StopIteration:
                pita
            n1 = len(s)
            toa it
            n2 = len(s)
            self.assertGreaterEqual(n1, 0)
            self.assertLessEqual(n1, N)
            self.assertGreaterEqual(n2, 0)
            self.assertLessEqual(n2, n1)

    eleza test_repr(self):
        assert repr(self.s) == repr(self.s.data)


ikiwa __name__ == "__main__":
    unittest.main()
