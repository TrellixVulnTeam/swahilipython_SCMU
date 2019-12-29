kutoka test agiza support, seq_tests
agiza unittest

agiza gc
agiza pickle

# For tuple hashes, we normally only run a test to ensure that we get
# the same results across platforms kwenye a handful of cases.  If that's
# so, there's no real point to running more.  Set RUN_ALL_HASH_TESTS to
# run more anyway.  That's usually of real interest only when analyzing,
# ama changing, the hash algorithm.  In which case it's usually also
# most useful to set JUST_SHOW_HASH_RESULTS, to see all the results
# instead of wrestling ukijumuisha test "failures".  See the bottom of the
# file kila extensive notes on what we're testing here na why.
RUN_ALL_HASH_TESTS = Uongo
JUST_SHOW_HASH_RESULTS = Uongo # ikiwa RUN_ALL_HASH_TESTS, just display

kundi TupleTest(seq_tests.CommonTest):
    type2test = tuple

    eleza test_getitem_error(self):
        t = ()
        msg = "tuple indices must be integers ama slices"
        ukijumuisha self.assertRaisesRegex(TypeError, msg):
            t['a']

    eleza test_constructors(self):
        super().test_constructors()
        # calling built-in types without argument must rudisha empty
        self.assertEqual(tuple(), ())
        t0_3 = (0, 1, 2, 3)
        t0_3_bis = tuple(t0_3)
        self.assertKweli(t0_3 ni t0_3_bis)
        self.assertEqual(tuple([]), ())
        self.assertEqual(tuple([0, 1, 2, 3]), (0, 1, 2, 3))
        self.assertEqual(tuple(''), ())
        self.assertEqual(tuple('spam'), ('s', 'p', 'a', 'm'))
        self.assertEqual(tuple(x kila x kwenye range(10) ikiwa x % 2),
                         (1, 3, 5, 7, 9))

    eleza test_keyword_args(self):
        ukijumuisha self.assertRaisesRegex(TypeError, 'keyword argument'):
            tuple(sequence=())

    eleza test_truth(self):
        super().test_truth()
        self.assertKweli(not ())
        self.assertKweli((42, ))

    eleza test_len(self):
        super().test_len()
        self.assertEqual(len(()), 0)
        self.assertEqual(len((0,)), 1)
        self.assertEqual(len((0, 1, 2)), 3)

    eleza test_iadd(self):
        super().test_iadd()
        u = (0, 1)
        u2 = u
        u += (2, 3)
        self.assertKweli(u ni sio u2)

    eleza test_imul(self):
        super().test_imul()
        u = (0, 1)
        u2 = u
        u *= 3
        self.assertKweli(u ni sio u2)

    eleza test_tupleresizebug(self):
        # Check that a specific bug kwenye _PyTuple_Resize() ni squashed.
        eleza f():
            kila i kwenye range(1000):
                tuma i
        self.assertEqual(list(tuple(f())), list(range(1000)))

    # We expect tuples whose base components have deterministic hashes to
    # have deterministic hashes too - and, indeed, the same hashes across
    # platforms ukijumuisha hash codes of the same bit width.
    eleza test_hash_exact(self):
        eleza check_one_exact(t, e32, e64):
            got = hash(t)
            expected = e32 ikiwa support.NHASHBITS == 32 isipokua e64
            ikiwa got != expected:
                msg = f"FAIL hash({t!r}) == {got} != {expected}"
                self.fail(msg)

        check_one_exact((), 750394483, 5740354900026072187)
        check_one_exact((0,), 1214856301, -8753497827991233192)
        check_one_exact((0, 0), -168982784, -8458139203682520985)
        check_one_exact((0.5,), 2077348973, -408149959306781352)
        check_one_exact((0.5, (), (-2, 3, (4, 6))), 714642271,
                        -1845940830829704396)

    # Various tests kila hashing of tuples to check that we get few collisions.
    # Does something only ikiwa RUN_ALL_HASH_TESTS ni true.
    #
    # Earlier versions of the tuple hash algorithm had massive collisions
    # reported at:
    # - https://bugs.python.org/issue942952
    # - https://bugs.python.org/issue34751
    eleza test_hash_optional(self):
        kutoka itertools agiza product

        ikiwa sio RUN_ALL_HASH_TESTS:
            rudisha

        # If specified, `expected` ni a 2-tuple of expected
        # (number_of_collisions, pileup) values, na the test fails if
        # those aren't the values we get.  Also ikiwa specified, the test
        # fails ikiwa z > `zlimit`.
        eleza tryone_inner(tag, nbins, hashes, expected=Tupu, zlimit=Tupu):
            kutoka collections agiza Counter

            nballs = len(hashes)
            mean, sdev = support.collision_stats(nbins, nballs)
            c = Counter(hashes)
            collisions = nballs - len(c)
            z = (collisions - mean) / sdev
            pileup = max(c.values()) - 1
            toa c
            got = (collisions, pileup)
            failed = Uongo
            prefix = ""
            ikiwa zlimit ni sio Tupu na z > zlimit:
                failed = Kweli
                prefix = f"FAIL z > {zlimit}; "
            ikiwa expected ni sio Tupu na got != expected:
                failed = Kweli
                prefix += f"FAIL {got} != {expected}; "
            ikiwa failed ama JUST_SHOW_HASH_RESULTS:
                msg = f"{prefix}{tag}; pileup {pileup:,} mean {mean:.1f} "
                msg += f"coll {collisions:,} z {z:+.1f}"
                ikiwa JUST_SHOW_HASH_RESULTS:
                    agiza sys
                    andika(msg, file=sys.__stdout__)
                isipokua:
                    self.fail(msg)

        eleza tryone(tag, xs,
                   native32=Tupu, native64=Tupu, hi32=Tupu, lo32=Tupu,
                   zlimit=Tupu):
            NHASHBITS = support.NHASHBITS
            hashes = list(map(hash, xs))
            tryone_inner(tag + f"; {NHASHBITS}-bit hash codes",
                         1 << NHASHBITS,
                         hashes,
                         native32 ikiwa NHASHBITS == 32 isipokua native64,
                         zlimit)

            ikiwa NHASHBITS > 32:
                shift = NHASHBITS - 32
                tryone_inner(tag + "; 32-bit upper hash codes",
                             1 << 32,
                             [h >> shift kila h kwenye hashes],
                             hi32,
                             zlimit)

                mask = (1 << 32) - 1
                tryone_inner(tag + "; 32-bit lower hash codes",
                             1 << 32,
                             [h & mask kila h kwenye hashes],
                             lo32,
                             zlimit)

        # Tuples of smallish positive integers are common - nice ikiwa we
        # get "better than random" kila these.
        tryone("range(100) by 3", list(product(range(100), repeat=3)),
               (0, 0), (0, 0), (4, 1), (0, 0))

        # A previous hash had systematic problems when mixing integers of
        # similar magnitude but opposite sign, obscurely related to that
        # j ^ -2 == -j when j ni odd.
        cands = list(range(-10, -1)) + list(range(9))

        # Note:  -1 ni omitted because hash(-1) == hash(-2) == -2, and
        # there's nothing the tuple hash can do to avoid collisions
        # inherited kutoka collisions kwenye the tuple components' hashes.
        tryone("-10 .. 8 by 4", list(product(cands, repeat=4)),
               (0, 0), (0, 0), (0, 0), (0, 0))
        toa cands

        # The hashes here are a weird mix of values where all the
        # variation ni kwenye the lowest bits na across a single high-order
        # bit - the middle bits are all zeroes. A decent hash has to
        # both propagate low bits to the left na high bits to the
        # right.  This ni also complicated a bit kwenye that there are
        # collisions among the hashes of the integers kwenye L alone.
        L = [n << 60 kila n kwenye range(100)]
        tryone("0..99 << 60 by 3", list(product(L, repeat=3)),
               (0, 0), (0, 0), (0, 0), (324, 1))
        toa L

        # Used to suffer a massive number of collisions.
        tryone("[-3, 3] by 18", list(product([-3, 3], repeat=18)),
               (7, 1), (0, 0), (7, 1), (6, 1))

        # And even worse.  hash(0.5) has only a single bit set, at the
        # high end. A decent hash needs to propagate high bits right.
        tryone("[0, 0.5] by 18", list(product([0, 0.5], repeat=18)),
               (5, 1), (0, 0), (9, 1), (12, 1))

        # Hashes of ints na floats are the same across platforms.
        # String hashes vary even on a single platform across runs, due
        # to hash randomization kila strings.  So we can't say exactly
        # what this should do.  Instead we insist that the # of
        # collisions ni no more than 4 sdevs above the theoretically
        # random mean.  Even ikiwa the tuple hash can't achieve that on its
        # own, the string hash ni trying to be decently pseudo-random
        # (in all bit positions) on _its_ own.  We can at least test
        # that the tuple hash doesn't systematically ruin that.
        tryone("4-char tuples",
               list(product("abcdefghijklmnopqrstuvwxyz", repeat=4)),
               zlimit=4.0)

        # The "old tuple test".  See https://bugs.python.org/issue942952.
        # Ensures, kila example, that the hash:
        #   ni non-commutative
        #   spreads closely spaced values
        #   doesn't exhibit cancellation kwenye tuples like (x,(x,y))
        N = 50
        base = list(range(N))
        xp = list(product(base, repeat=2))
        inps = base + list(product(base, xp)) + \
                     list(product(xp, base)) + xp + list(zip(base))
        tryone("old tuple test", inps,
               (2, 1), (0, 0), (52, 49), (7, 1))
        toa base, xp, inps

        # The "new tuple test".  See https://bugs.python.org/issue34751.
        # Even more tortured nesting, na a mix of signed ints of very
        # small magnitude.
        n = 5
        A = [x kila x kwenye range(-n, n+1) ikiwa x != -1]
        B = A + [(a,) kila a kwenye A]
        L2 = list(product(A, repeat=2))
        L3 = L2 + list(product(A, repeat=3))
        L4 = L3 + list(product(A, repeat=4))
        # T = list of testcases. These consist of all (possibly nested
        # at most 2 levels deep) tuples containing at most 4 items kutoka
        # the set A.
        T = A
        T += [(a,) kila a kwenye B + L4]
        T += product(L3, B)
        T += product(L2, repeat=2)
        T += product(B, L3)
        T += product(B, B, L2)
        T += product(B, L2, B)
        T += product(L2, B, B)
        T += product(B, repeat=4)
        assert len(T) == 345130
        tryone("new tuple test", T,
               (9, 1), (0, 0), (21, 5), (6, 1))

    eleza test_repr(self):
        l0 = tuple()
        l2 = (0, 1, 2)
        a0 = self.type2test(l0)
        a2 = self.type2test(l2)

        self.assertEqual(str(a0), repr(l0))
        self.assertEqual(str(a2), repr(l2))
        self.assertEqual(repr(a0), "()")
        self.assertEqual(repr(a2), "(0, 1, 2)")

    eleza _not_tracked(self, t):
        # Nested tuples can take several collections to untrack
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
        # Test GC-optimization of tuple literals
        x, y, z = 1.5, "a", []

        self._not_tracked(())
        self._not_tracked((1,))
        self._not_tracked((1, 2))
        self._not_tracked((1, 2, "a"))
        self._not_tracked((1, 2, (Tupu, Kweli, Uongo, ()), int))
        self._not_tracked((object(),))
        self._not_tracked(((1, x), y, (2, 3)))

        # Tuples ukijumuisha mutable elements are always tracked, even ikiwa those
        # elements are sio tracked right now.
        self._tracked(([],))
        self._tracked(([1],))
        self._tracked(({},))
        self._tracked((set(),))
        self._tracked((x, y, z))

    eleza check_track_dynamic(self, tp, always_track):
        x, y, z = 1.5, "a", []

        check = self._tracked ikiwa always_track isipokua self._not_tracked
        check(tp())
        check(tp([]))
        check(tp(set()))
        check(tp([1, x, y]))
        check(tp(obj kila obj kwenye [1, x, y]))
        check(tp(set([1, x, y])))
        check(tp(tuple([obj]) kila obj kwenye [1, x, y]))
        check(tuple(tp([obj]) kila obj kwenye [1, x, y]))

        self._tracked(tp([z]))
        self._tracked(tp([[x, y]]))
        self._tracked(tp([{x: y}]))
        self._tracked(tp(obj kila obj kwenye [x, y, z]))
        self._tracked(tp(tuple([obj]) kila obj kwenye [x, y, z]))
        self._tracked(tuple(tp([obj]) kila obj kwenye [x, y, z]))

    @support.cpython_only
    eleza test_track_dynamic(self):
        # Test GC-optimization of dynamically constructed tuples.
        self.check_track_dynamic(tuple, Uongo)

    @support.cpython_only
    eleza test_track_subtypes(self):
        # Tuple subtypes must always be tracked
        kundi MyTuple(tuple):
            pita
        self.check_track_dynamic(MyTuple, Kweli)

    @support.cpython_only
    eleza test_bug7466(self):
        # Trying to untrack an unfinished tuple could crash Python
        self._not_tracked(tuple(gc.collect() kila i kwenye range(101)))

    eleza test_repr_large(self):
        # Check the repr of large list objects
        eleza check(n):
            l = (0,) * n
            s = repr(l)
            self.assertEqual(s,
                '(' + ', '.join(['0'] * n) + ')')
        check(10)       # check our checking code
        check(1000000)

    eleza test_iterator_pickle(self):
        # Userlist iterators don't support pickling yet since
        # they are based on generators.
        data = self.type2test([4, 5, 6, 7])
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            itorg = iter(data)
            d = pickle.dumps(itorg, proto)
            it = pickle.loads(d)
            self.assertEqual(type(itorg), type(it))
            self.assertEqual(self.type2test(it), self.type2test(data))

            it = pickle.loads(d)
            next(it)
            d = pickle.dumps(it, proto)
            self.assertEqual(self.type2test(it), self.type2test(data)[1:])

    eleza test_reversed_pickle(self):
        data = self.type2test([4, 5, 6, 7])
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            itorg = reversed(data)
            d = pickle.dumps(itorg, proto)
            it = pickle.loads(d)
            self.assertEqual(type(itorg), type(it))
            self.assertEqual(self.type2test(it), self.type2test(reversed(data)))

            it = pickle.loads(d)
            next(it)
            d = pickle.dumps(it, proto)
            self.assertEqual(self.type2test(it), self.type2test(reversed(data))[1:])

    eleza test_no_comdat_folding(self):
        # Issue 8847: In the PGO build, the MSVC linker's COMDAT folding
        # optimization causes failures kwenye code that relies on distinct
        # function addresses.
        kundi T(tuple): pita
        ukijumuisha self.assertRaises(TypeError):
            [3,] + T((1,2))

    eleza test_lexicographic_ordering(self):
        # Issue 21100
        a = self.type2test([1, 2])
        b = self.type2test([1, 2, 0])
        c = self.type2test([1, 3])
        self.assertLess(a, b)
        self.assertLess(b, c)

# Notes on testing hash codes.  The primary thing ni that Python doesn't
# care about "random" hash codes.  To the contrary, we like them to be
# very regular when possible, so that the low-order bits are kama evenly
# distributed kama possible.  For integers this ni easy: hash(i) == i for
# all not-huge i tatizo i==-1.
#
# For tuples of mixed type there's really no hope of that, so we want
# "randomish" here instead.  But getting close to pseudo-random kwenye all
# bit positions ni more expensive than we've been willing to pay for.
#
# We can tolerate large deviations kutoka random - what we don't want is
# catastrophic pileups on a relative handful of hash codes.  The dict
# na set lookup routines remain effective provided that full-width hash
# codes kila not-equal objects are distinct.
#
# So we compute various statistics here based on what a "truly random"
# hash would do, but don't automate "pita ama fail" based on those
# results.  Instead those are viewed kama inputs to human judgment, na the
# automated tests merely ensure we get the _same_ results across
# platforms.  In fact, we normally don't bother to run them at all -
# set RUN_ALL_HASH_TESTS to force it.
#
# When global JUST_SHOW_HASH_RESULTS ni Kweli, the tuple hash statistics
# are just displayed to stdout.  A typical output line looks like:
#
# old tuple test; 32-bit upper hash codes; \
#             pileup 49 mean 7.4 coll 52 z +16.4
#
# "old tuple test" ni just a string name kila the test being run.
#
# "32-bit upper hash codes" means this was run under a 64-bit build and
# we've shifted away the lower 32 bits of the hash codes.
#
# "pileup" ni 0 ikiwa there were no collisions across those hash codes.
# It's 1 less than the maximum number of times any single hash code was
# seen.  So kwenye this case, there was (at least) one hash code that was
# seen 50 times:  that hash code "piled up" 49 more times than ideal.
#
# "mean" ni the number of collisions a perfectly random hash function
# would have tumaed, on average.
#
# "coll" ni the number of collisions actually seen.
#
# "z" ni "coll - mean" divided by the standard deviation of the number
# of collisions a perfectly random hash function would suffer.  A
# positive value ni "worse than random", na negative value "better than
# random".  Anything of magnitude greater than 3 would be highly suspect
# kila a hash function that claimed to be random.  It's essentially
# impossible that a truly random function would deliver a result 16.4
# sdevs "worse than random".
#
# But we don't care here!  That's why the test isn't coded to fail.
# Knowing something about how the high-order hash code bits behave
# provides insight, but ni irrelevant to how the dict na set lookup
# code performs.  The low-order bits are much more agizaant to that,
# na on the same test those did "just like random":
#
# old tuple test; 32-bit lower hash codes; \
#            pileup 1 mean 7.4 coll 7 z -0.2
#
# So there are always tradeoffs to consider.  For another:
#
# 0..99 << 60 by 3; 32-bit hash codes; \
#            pileup 0 mean 116.4 coll 0 z -10.8
#
# That was run under a 32-bit build, na ni spectacularly "better than
# random".  On a 64-bit build the wider hash codes are fine too:
#
# 0..99 << 60 by 3; 64-bit hash codes; \
#             pileup 0 mean 0.0 coll 0 z -0.0
#
# but their lower 32 bits are poor:
#
# 0..99 << 60 by 3; 32-bit lower hash codes; \
#             pileup 1 mean 116.4 coll 324 z +19.2
#
# In a statistical sense that's waaaaay too many collisions, but (a) 324
# collisions out of a million hash codes isn't anywhere near being a
# real problem; and, (b) the worst pileup on a single hash code ni a measly
# 1 extra.  It's a relatively poor case kila the tuple hash, but still
# fine kila practical use.
#
# This isn't, which ni what Python 3.7.1 produced kila the hashes of
# itertools.product([0, 0.5], repeat=18).  Even ukijumuisha a fat 64-bit
# hashcode, the highest pileup was over 16,000 - making a dict/set
# lookup on one of the colliding values thousands of times slower (on
# average) than we expect.
#
# [0, 0.5] by 18; 64-bit hash codes; \
#            pileup 16,383 mean 0.0 coll 262,128 z +6073641856.9
# [0, 0.5] by 18; 32-bit lower hash codes; \
#            pileup 262,143 mean 8.0 coll 262,143 z +92683.6

ikiwa __name__ == "__main__":
    unittest.main()
