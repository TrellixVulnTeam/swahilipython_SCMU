agiza unittest
kutoka test agiza support
kutoka itertools agiza *
agiza weakref
kutoka decimal agiza Decimal
kutoka fractions agiza Fraction
agiza operator
agiza random
agiza copy
agiza pickle
kutoka functools agiza reduce
agiza sys
agiza struct
agiza threading
maxsize = support.MAX_Py_ssize_t
minsize = -maxsize-1

eleza lzip(*args):
    rudisha list(zip(*args))

eleza onearg(x):
    'Test function of one argument'
    rudisha 2*x

eleza errfunc(*args):
    'Test function that ashirias an error'
    ashiria ValueError

eleza gen3():
    'Non-restartable source sequence'
    kila i kwenye (0, 1, 2):
        tuma i

eleza isEven(x):
    'Test predicate'
    rudisha x%2==0

eleza isOdd(x):
    'Test predicate'
    rudisha x%2==1

eleza tupleize(*args):
    rudisha args

eleza irange(n):
    kila i kwenye range(n):
        tuma i

kundi StopNow:
    'Class emulating an empty iterable.'
    eleza __iter__(self):
        rudisha self
    eleza __next__(self):
        ashiria StopIteration

eleza take(n, seq):
    'Convenience function kila partially consuming a long of infinite iterable'
    rudisha list(islice(seq, n))

eleza prod(iterable):
    rudisha reduce(operator.mul, iterable, 1)

eleza fact(n):
    'Factorial'
    rudisha prod(range(1, n+1))

# root level methods kila pickling ability
eleza testR(r):
    rudisha r[0]

eleza testR2(r):
    rudisha r[2]

eleza underten(x):
    rudisha x<10

picklecopiers = [lambda s, proto=proto: pickle.loads(pickle.dumps(s, proto))
                 kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1)]

kundi TestBasicOps(unittest.TestCase):

    eleza pickletest(self, protocol, it, stop=4, take=1, compare=Tupu):
        """Test that an iterator ni the same after pickling, also when part-consumed"""
        eleza expand(it, i=0):
            # Recursively expand iterables, within sensible bounds
            ikiwa i > 10:
                ashiria RuntimeError("infinite recursion encountered")
            ikiwa isinstance(it, str):
                rudisha it
            jaribu:
                l = list(islice(it, stop))
            tatizo TypeError:
                rudisha it # can't expand it
            rudisha [expand(e, i+1) kila e kwenye l]

        # Test the initial copy against the original
        dump = pickle.dumps(it, protocol)
        i2 = pickle.loads(dump)
        self.assertEqual(type(it), type(i2))
        a, b = expand(it), expand(i2)
        self.assertEqual(a, b)
        ikiwa compare:
            c = expand(compare)
            self.assertEqual(a, c)

        # Take kutoka the copy, na create another copy na compare them.
        i3 = pickle.loads(dump)
        took = 0
        jaribu:
            kila i kwenye range(take):
                next(i3)
                took += 1
        tatizo StopIteration:
            pita #in case there ni less data than 'take'
        dump = pickle.dumps(i3, protocol)
        i4 = pickle.loads(dump)
        a, b = expand(i3), expand(i4)
        self.assertEqual(a, b)
        ikiwa compare:
            c = expand(compare[took:])
            self.assertEqual(a, c);

    eleza test_accumulate(self):
        self.assertEqual(list(accumulate(range(10))),               # one positional arg
                          [0, 1, 3, 6, 10, 15, 21, 28, 36, 45])
        self.assertEqual(list(accumulate(iterable=range(10))),      # kw arg
                          [0, 1, 3, 6, 10, 15, 21, 28, 36, 45])
        kila typ kwenye int, complex, Decimal, Fraction:                 # multiple types
            self.assertEqual(
                list(accumulate(map(typ, range(10)))),
                list(map(typ, [0, 1, 3, 6, 10, 15, 21, 28, 36, 45])))
        self.assertEqual(list(accumulate('abc')), ['a', 'ab', 'abc'])   # works ukijumuisha non-numeric
        self.assertEqual(list(accumulate([])), [])                  # empty iterable
        self.assertEqual(list(accumulate([7])), [7])                # iterable of length one
        self.assertRaises(TypeError, accumulate, range(10), 5, 6)   # too many args
        self.assertRaises(TypeError, accumulate)                    # too few args
        self.assertRaises(TypeError, accumulate, x=range(10))       # unexpected kwd arg
        self.assertRaises(TypeError, list, accumulate([1, []]))     # args that don't add

        s = [2, 8, 9, 5, 7, 0, 3, 4, 1, 6]
        self.assertEqual(list(accumulate(s, min)),
                         [2, 2, 2, 2, 2, 0, 0, 0, 0, 0])
        self.assertEqual(list(accumulate(s, max)),
                         [2, 8, 9, 9, 9, 9, 9, 9, 9, 9])
        self.assertEqual(list(accumulate(s, operator.mul)),
                         [2, 16, 144, 720, 5040, 0, 0, 0, 0, 0])
        ukijumuisha self.assertRaises(TypeError):
            list(accumulate(s, chr))                                # unary-operation
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            self.pickletest(proto, accumulate(range(10)))           # test pickling
            self.pickletest(proto, accumulate(range(10), initial=7))
        self.assertEqual(list(accumulate([10, 5, 1], initial=Tupu)), [10, 15, 16])
        self.assertEqual(list(accumulate([10, 5, 1], initial=100)), [100, 110, 115, 116])
        self.assertEqual(list(accumulate([], initial=100)), [100])
        ukijumuisha self.assertRaises(TypeError):
            list(accumulate([10, 20], 100))

    eleza test_chain(self):

        eleza chain2(*iterables):
            'Pure python version kwenye the docs'
            kila it kwenye iterables:
                kila element kwenye it:
                    tuma element

        kila c kwenye (chain, chain2):
            self.assertEqual(list(c('abc', 'def')), list('abcdef'))
            self.assertEqual(list(c('abc')), list('abc'))
            self.assertEqual(list(c('')), [])
            self.assertEqual(take(4, c('abc', 'def')), list('abcd'))
            self.assertRaises(TypeError, list,c(2, 3))

    eleza test_chain_from_iterable(self):
        self.assertEqual(list(chain.kutoka_iterable(['abc', 'def'])), list('abcdef'))
        self.assertEqual(list(chain.kutoka_iterable(['abc'])), list('abc'))
        self.assertEqual(list(chain.kutoka_iterable([''])), [])
        self.assertEqual(take(4, chain.kutoka_iterable(['abc', 'def'])), list('abcd'))
        self.assertRaises(TypeError, list, chain.kutoka_iterable([2, 3]))

    eleza test_chain_reducible(self):
        kila oper kwenye [copy.deepcopy] + picklecopiers:
            it = chain('abc', 'def')
            self.assertEqual(list(oper(it)), list('abcdef'))
            self.assertEqual(next(it), 'a')
            self.assertEqual(list(oper(it)), list('bcdef'))

            self.assertEqual(list(oper(chain(''))), [])
            self.assertEqual(take(4, oper(chain('abc', 'def'))), list('abcd'))
            self.assertRaises(TypeError, list, oper(chain(2, 3)))
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            self.pickletest(proto, chain('abc', 'def'), compare=list('abcdef'))

    eleza test_chain_setstate(self):
        self.assertRaises(TypeError, chain().__setstate__, ())
        self.assertRaises(TypeError, chain().__setstate__, [])
        self.assertRaises(TypeError, chain().__setstate__, 0)
        self.assertRaises(TypeError, chain().__setstate__, ([],))
        self.assertRaises(TypeError, chain().__setstate__, (iter([]), []))
        it = chain()
        it.__setstate__((iter(['abc', 'def']),))
        self.assertEqual(list(it), ['a', 'b', 'c', 'd', 'e', 'f'])
        it = chain()
        it.__setstate__((iter(['abc', 'def']), iter(['ghi'])))
        self.assertEqual(list(it), ['ghi', 'a', 'b', 'c', 'd', 'e', 'f'])

    eleza test_combinations(self):
        self.assertRaises(TypeError, combinations, 'abc')       # missing r argument
        self.assertRaises(TypeError, combinations, 'abc', 2, 1) # too many arguments
        self.assertRaises(TypeError, combinations, Tupu)        # pool ni sio iterable
        self.assertRaises(ValueError, combinations, 'abc', -2)  # r ni negative

        kila op kwenye [lambda a:a] + picklecopiers:
            self.assertEqual(list(op(combinations('abc', 32))), [])     # r > n

            self.assertEqual(list(op(combinations('ABCD', 2))),
                             [('A','B'), ('A','C'), ('A','D'), ('B','C'), ('B','D'), ('C','D')])
            testIntermediate = combinations('ABCD', 2)
            next(testIntermediate)
            self.assertEqual(list(op(testIntermediate)),
                             [('A','C'), ('A','D'), ('B','C'), ('B','D'), ('C','D')])

            self.assertEqual(list(op(combinations(range(4), 3))),
                             [(0,1,2), (0,1,3), (0,2,3), (1,2,3)])
            testIntermediate = combinations(range(4), 3)
            next(testIntermediate)
            self.assertEqual(list(op(testIntermediate)),
                             [(0,1,3), (0,2,3), (1,2,3)])


        eleza combinations1(iterable, r):
            'Pure python version shown kwenye the docs'
            pool = tuple(iterable)
            n = len(pool)
            ikiwa r > n:
                rudisha
            indices = list(range(r))
            tuma tuple(pool[i] kila i kwenye indices)
            wakati 1:
                kila i kwenye reversed(range(r)):
                    ikiwa indices[i] != i + n - r:
                        koma
                isipokua:
                    rudisha
                indices[i] += 1
                kila j kwenye range(i+1, r):
                    indices[j] = indices[j-1] + 1
                tuma tuple(pool[i] kila i kwenye indices)

        eleza combinations2(iterable, r):
            'Pure python version shown kwenye the docs'
            pool = tuple(iterable)
            n = len(pool)
            kila indices kwenye permutations(range(n), r):
                ikiwa sorted(indices) == list(indices):
                    tuma tuple(pool[i] kila i kwenye indices)

        eleza combinations3(iterable, r):
            'Pure python version kutoka cwr()'
            pool = tuple(iterable)
            n = len(pool)
            kila indices kwenye combinations_with_replacement(range(n), r):
                ikiwa len(set(indices)) == r:
                    tuma tuple(pool[i] kila i kwenye indices)

        kila n kwenye range(7):
            values = [5*x-12 kila x kwenye range(n)]
            kila r kwenye range(n+2):
                result = list(combinations(values, r))
                self.assertEqual(len(result), 0 ikiwa r>n isipokua fact(n) / fact(r) / fact(n-r)) # right number of combs
                self.assertEqual(len(result), len(set(result)))         # no repeats
                self.assertEqual(result, sorted(result))                # lexicographic order
                kila c kwenye result:
                    self.assertEqual(len(c), r)                         # r-length combinations
                    self.assertEqual(len(set(c)), r)                    # no duplicate elements
                    self.assertEqual(list(c), sorted(c))                # keep original ordering
                    self.assertKweli(all(e kwenye values kila e kwenye c))           # elements taken kutoka input iterable
                    self.assertEqual(list(c),
                                     [e kila e kwenye values ikiwa e kwenye c])      # comb ni a subsequence of the input iterable
                self.assertEqual(result, list(combinations1(values, r))) # matches first pure python version
                self.assertEqual(result, list(combinations2(values, r))) # matches second pure python version
                self.assertEqual(result, list(combinations3(values, r))) # matches second pure python version

                kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                    self.pickletest(proto, combinations(values, r))      # test pickling

    @support.bigaddrspacetest
    eleza test_combinations_overflow(self):
        ukijumuisha self.assertRaises((OverflowError, MemoryError)):
            combinations("AA", 2**29)

        # Test implementation detail:  tuple re-use
    @support.impl_detail("tuple reuse ni specific to CPython")
    eleza test_combinations_tuple_reuse(self):
        self.assertEqual(len(set(map(id, combinations('abcde', 3)))), 1)
        self.assertNotEqual(len(set(map(id, list(combinations('abcde', 3))))), 1)

    eleza test_combinations_with_replacement(self):
        cwr = combinations_with_replacement
        self.assertRaises(TypeError, cwr, 'abc')       # missing r argument
        self.assertRaises(TypeError, cwr, 'abc', 2, 1) # too many arguments
        self.assertRaises(TypeError, cwr, Tupu)        # pool ni sio iterable
        self.assertRaises(ValueError, cwr, 'abc', -2)  # r ni negative

        kila op kwenye [lambda a:a] + picklecopiers:
            self.assertEqual(list(op(cwr('ABC', 2))),
                             [('A','A'), ('A','B'), ('A','C'), ('B','B'), ('B','C'), ('C','C')])
            testIntermediate = cwr('ABC', 2)
            next(testIntermediate)
            self.assertEqual(list(op(testIntermediate)),
                             [('A','B'), ('A','C'), ('B','B'), ('B','C'), ('C','C')])


        eleza cwr1(iterable, r):
            'Pure python version shown kwenye the docs'
            # number items rudishaed:  (n+r-1)! / r! / (n-1)! when n>0
            pool = tuple(iterable)
            n = len(pool)
            ikiwa sio n na r:
                rudisha
            indices = [0] * r
            tuma tuple(pool[i] kila i kwenye indices)
            wakati 1:
                kila i kwenye reversed(range(r)):
                    ikiwa indices[i] != n - 1:
                        koma
                isipokua:
                    rudisha
                indices[i:] = [indices[i] + 1] * (r - i)
                tuma tuple(pool[i] kila i kwenye indices)

        eleza cwr2(iterable, r):
            'Pure python version shown kwenye the docs'
            pool = tuple(iterable)
            n = len(pool)
            kila indices kwenye product(range(n), repeat=r):
                ikiwa sorted(indices) == list(indices):
                    tuma tuple(pool[i] kila i kwenye indices)

        eleza numcombs(n, r):
            ikiwa sio n:
                rudisha 0 ikiwa r isipokua 1
            rudisha fact(n+r-1) / fact(r)/ fact(n-1)

        kila n kwenye range(7):
            values = [5*x-12 kila x kwenye range(n)]
            kila r kwenye range(n+2):
                result = list(cwr(values, r))

                self.assertEqual(len(result), numcombs(n, r))           # right number of combs
                self.assertEqual(len(result), len(set(result)))         # no repeats
                self.assertEqual(result, sorted(result))                # lexicographic order

                regular_combs = list(combinations(values, r))           # compare to combs without replacement
                ikiwa n == 0 ama r <= 1:
                    self.assertEqual(result, regular_combs)            # cases that should be identical
                isipokua:
                    self.assertKweli(set(result) >= set(regular_combs))     # rest should be supersets of regular combs

                kila c kwenye result:
                    self.assertEqual(len(c), r)                         # r-length combinations
                    noruns = [k kila k,v kwenye groupby(c)]                  # combo without consecutive repeats
                    self.assertEqual(len(noruns), len(set(noruns)))     # no repeats other than consecutive
                    self.assertEqual(list(c), sorted(c))                # keep original ordering
                    self.assertKweli(all(e kwenye values kila e kwenye c))           # elements taken kutoka input iterable
                    self.assertEqual(noruns,
                                     [e kila e kwenye values ikiwa e kwenye c])     # comb ni a subsequence of the input iterable
                self.assertEqual(result, list(cwr1(values, r)))         # matches first pure python version
                self.assertEqual(result, list(cwr2(values, r)))         # matches second pure python version

                kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                    self.pickletest(proto, cwr(values,r))               # test pickling

    @support.bigaddrspacetest
    eleza test_combinations_with_replacement_overflow(self):
        ukijumuisha self.assertRaises((OverflowError, MemoryError)):
            combinations_with_replacement("AA", 2**30)

        # Test implementation detail:  tuple re-use
    @support.impl_detail("tuple reuse ni specific to CPython")
    eleza test_combinations_with_replacement_tuple_reuse(self):
        cwr = combinations_with_replacement
        self.assertEqual(len(set(map(id, cwr('abcde', 3)))), 1)
        self.assertNotEqual(len(set(map(id, list(cwr('abcde', 3))))), 1)

    eleza test_permutations(self):
        self.assertRaises(TypeError, permutations)              # too few arguments
        self.assertRaises(TypeError, permutations, 'abc', 2, 1) # too many arguments
        self.assertRaises(TypeError, permutations, Tupu)        # pool ni sio iterable
        self.assertRaises(ValueError, permutations, 'abc', -2)  # r ni negative
        self.assertEqual(list(permutations('abc', 32)), [])     # r > n
        self.assertRaises(TypeError, permutations, 'abc', 's')  # r ni sio an int ama Tupu
        self.assertEqual(list(permutations(range(3), 2)),
                                           [(0,1), (0,2), (1,0), (1,2), (2,0), (2,1)])

        eleza permutations1(iterable, r=Tupu):
            'Pure python version shown kwenye the docs'
            pool = tuple(iterable)
            n = len(pool)
            r = n ikiwa r ni Tupu isipokua r
            ikiwa r > n:
                rudisha
            indices = list(range(n))
            cycles = list(range(n-r+1, n+1))[::-1]
            tuma tuple(pool[i] kila i kwenye indices[:r])
            wakati n:
                kila i kwenye reversed(range(r)):
                    cycles[i] -= 1
                    ikiwa cycles[i] == 0:
                        indices[i:] = indices[i+1:] + indices[i:i+1]
                        cycles[i] = n - i
                    isipokua:
                        j = cycles[i]
                        indices[i], indices[-j] = indices[-j], indices[i]
                        tuma tuple(pool[i] kila i kwenye indices[:r])
                        koma
                isipokua:
                    rudisha

        eleza permutations2(iterable, r=Tupu):
            'Pure python version shown kwenye the docs'
            pool = tuple(iterable)
            n = len(pool)
            r = n ikiwa r ni Tupu isipokua r
            kila indices kwenye product(range(n), repeat=r):
                ikiwa len(set(indices)) == r:
                    tuma tuple(pool[i] kila i kwenye indices)

        kila n kwenye range(7):
            values = [5*x-12 kila x kwenye range(n)]
            kila r kwenye range(n+2):
                result = list(permutations(values, r))
                self.assertEqual(len(result), 0 ikiwa r>n isipokua fact(n) / fact(n-r))      # right number of perms
                self.assertEqual(len(result), len(set(result)))         # no repeats
                self.assertEqual(result, sorted(result))                # lexicographic order
                kila p kwenye result:
                    self.assertEqual(len(p), r)                         # r-length permutations
                    self.assertEqual(len(set(p)), r)                    # no duplicate elements
                    self.assertKweli(all(e kwenye values kila e kwenye p))           # elements taken kutoka input iterable
                self.assertEqual(result, list(permutations1(values, r))) # matches first pure python version
                self.assertEqual(result, list(permutations2(values, r))) # matches second pure python version
                ikiwa r == n:
                    self.assertEqual(result, list(permutations(values, Tupu))) # test r kama Tupu
                    self.assertEqual(result, list(permutations(values)))       # test default r

                kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                    self.pickletest(proto, permutations(values, r))     # test pickling

    @support.bigaddrspacetest
    eleza test_permutations_overflow(self):
        ukijumuisha self.assertRaises((OverflowError, MemoryError)):
            permutations("A", 2**30)

    @support.impl_detail("tuple reuse ni specific to CPython")
    eleza test_permutations_tuple_reuse(self):
        self.assertEqual(len(set(map(id, permutations('abcde', 3)))), 1)
        self.assertNotEqual(len(set(map(id, list(permutations('abcde', 3))))), 1)

    eleza test_combinatorics(self):
        # Test relationships between product(), permutations(),
        # combinations() na combinations_with_replacement().

        kila n kwenye range(6):
            s = 'ABCDEFG'[:n]
            kila r kwenye range(8):
                prod = list(product(s, repeat=r))
                cwr = list(combinations_with_replacement(s, r))
                perm = list(permutations(s, r))
                comb = list(combinations(s, r))

                # Check size
                self.assertEqual(len(prod), n**r)
                self.assertEqual(len(cwr), (fact(n+r-1) / fact(r)/ fact(n-1)) ikiwa n isipokua (sio r))
                self.assertEqual(len(perm), 0 ikiwa r>n isipokua fact(n) / fact(n-r))
                self.assertEqual(len(comb), 0 ikiwa r>n isipokua fact(n) / fact(r) / fact(n-r))

                # Check lexicographic order without repeated tuples
                self.assertEqual(prod, sorted(set(prod)))
                self.assertEqual(cwr, sorted(set(cwr)))
                self.assertEqual(perm, sorted(set(perm)))
                self.assertEqual(comb, sorted(set(comb)))

                # Check interrelationships
                self.assertEqual(cwr, [t kila t kwenye prod ikiwa sorted(t)==list(t)]) # cwr: prods which are sorted
                self.assertEqual(perm, [t kila t kwenye prod ikiwa len(set(t))==r])    # perm: prods ukijumuisha no dups
                self.assertEqual(comb, [t kila t kwenye perm ikiwa sorted(t)==list(t)]) # comb: perms that are sorted
                self.assertEqual(comb, [t kila t kwenye cwr ikiwa len(set(t))==r])      # comb: cwrs without dups
                self.assertEqual(comb, list(filter(set(cwr).__contains__, perm)))     # comb: perm that ni a cwr
                self.assertEqual(comb, list(filter(set(perm).__contains__, cwr)))     # comb: cwr that ni a perm
                self.assertEqual(comb, sorted(set(cwr) & set(perm)))            # comb: both a cwr na a perm

    eleza test_compress(self):
        self.assertEqual(list(compress(data='ABCDEF', selectors=[1,0,1,0,1,1])), list('ACEF'))
        self.assertEqual(list(compress('ABCDEF', [1,0,1,0,1,1])), list('ACEF'))
        self.assertEqual(list(compress('ABCDEF', [0,0,0,0,0,0])), list(''))
        self.assertEqual(list(compress('ABCDEF', [1,1,1,1,1,1])), list('ABCDEF'))
        self.assertEqual(list(compress('ABCDEF', [1,0,1])), list('AC'))
        self.assertEqual(list(compress('ABC', [0,1,1,1,1,1])), list('BC'))
        n = 10000
        data = chain.kutoka_iterable(repeat(range(6), n))
        selectors = chain.kutoka_iterable(repeat((0, 1)))
        self.assertEqual(list(compress(data, selectors)), [1,3,5] * n)
        self.assertRaises(TypeError, compress, Tupu, range(6))      # 1st arg sio iterable
        self.assertRaises(TypeError, compress, range(6), Tupu)      # 2nd arg sio iterable
        self.assertRaises(TypeError, compress, range(6))            # too few args
        self.assertRaises(TypeError, compress, range(6), Tupu)      # too many args

        # check copy, deepcopy, pickle
        kila op kwenye [lambda a:copy.copy(a), lambda a:copy.deepcopy(a)] + picklecopiers:
            kila data, selectors, result1, result2 kwenye [
                ('ABCDEF', [1,0,1,0,1,1], 'ACEF', 'CEF'),
                ('ABCDEF', [0,0,0,0,0,0], '', ''),
                ('ABCDEF', [1,1,1,1,1,1], 'ABCDEF', 'BCDEF'),
                ('ABCDEF', [1,0,1], 'AC', 'C'),
                ('ABC', [0,1,1,1,1,1], 'BC', 'C'),
                ]:

                self.assertEqual(list(op(compress(data=data, selectors=selectors))), list(result1))
                self.assertEqual(list(op(compress(data, selectors))), list(result1))
                testIntermediate = compress(data, selectors)
                ikiwa result1:
                    next(testIntermediate)
                    self.assertEqual(list(op(testIntermediate)), list(result2))


    eleza test_count(self):
        self.assertEqual(lzip('abc',count()), [('a', 0), ('b', 1), ('c', 2)])
        self.assertEqual(lzip('abc',count(3)), [('a', 3), ('b', 4), ('c', 5)])
        self.assertEqual(take(2, lzip('abc',count(3))), [('a', 3), ('b', 4)])
        self.assertEqual(take(2, zip('abc',count(-1))), [('a', -1), ('b', 0)])
        self.assertEqual(take(2, zip('abc',count(-3))), [('a', -3), ('b', -2)])
        self.assertRaises(TypeError, count, 2, 3, 4)
        self.assertRaises(TypeError, count, 'a')
        self.assertEqual(take(10, count(maxsize-5)),
                         list(range(maxsize-5, maxsize+5)))
        self.assertEqual(take(10, count(-maxsize-5)),
                         list(range(-maxsize-5, -maxsize+5)))
        self.assertEqual(take(3, count(3.25)), [3.25, 4.25, 5.25])
        self.assertEqual(take(3, count(3.25-4j)), [3.25-4j, 4.25-4j, 5.25-4j])
        self.assertEqual(take(3, count(Decimal('1.1'))),
                         [Decimal('1.1'), Decimal('2.1'), Decimal('3.1')])
        self.assertEqual(take(3, count(Fraction(2, 3))),
                         [Fraction(2, 3), Fraction(5, 3), Fraction(8, 3)])
        BIGINT = 1<<1000
        self.assertEqual(take(3, count(BIGINT)), [BIGINT, BIGINT+1, BIGINT+2])
        c = count(3)
        self.assertEqual(repr(c), 'count(3)')
        next(c)
        self.assertEqual(repr(c), 'count(4)')
        c = count(-9)
        self.assertEqual(repr(c), 'count(-9)')
        next(c)
        self.assertEqual(next(c), -8)
        self.assertEqual(repr(count(10.25)), 'count(10.25)')
        self.assertEqual(repr(count(10.0)), 'count(10.0)')
        self.assertEqual(type(next(count(10.0))), float)
        kila i kwenye (-sys.maxsize-5, -sys.maxsize+5 ,-10, -1, 0, 10, sys.maxsize-5, sys.maxsize+5):
            # Test repr
            r1 = repr(count(i))
            r2 = 'count(%r)'.__mod__(i)
            self.assertEqual(r1, r2)

        # check copy, deepcopy, pickle
        kila value kwenye -3, 3, maxsize-5, maxsize+5:
            c = count(value)
            self.assertEqual(next(copy.copy(c)), value)
            self.assertEqual(next(copy.deepcopy(c)), value)
            kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                self.pickletest(proto, count(value))

        #check proper internal error handling kila large "step' sizes
        count(1, maxsize+5); sys.exc_info()

    eleza test_count_with_stride(self):
        self.assertEqual(lzip('abc',count(2,3)), [('a', 2), ('b', 5), ('c', 8)])
        self.assertEqual(lzip('abc',count(start=2,step=3)),
                         [('a', 2), ('b', 5), ('c', 8)])
        self.assertEqual(lzip('abc',count(step=-1)),
                         [('a', 0), ('b', -1), ('c', -2)])
        self.assertRaises(TypeError, count, 'a', 'b')
        self.assertEqual(lzip('abc',count(2,0)), [('a', 2), ('b', 2), ('c', 2)])
        self.assertEqual(lzip('abc',count(2,1)), [('a', 2), ('b', 3), ('c', 4)])
        self.assertEqual(lzip('abc',count(2,3)), [('a', 2), ('b', 5), ('c', 8)])
        self.assertEqual(take(20, count(maxsize-15, 3)), take(20, range(maxsize-15, maxsize+100, 3)))
        self.assertEqual(take(20, count(-maxsize-15, 3)), take(20, range(-maxsize-15,-maxsize+100, 3)))
        self.assertEqual(take(3, count(10, maxsize+5)),
                         list(range(10, 10+3*(maxsize+5), maxsize+5)))
        self.assertEqual(take(3, count(2, 1.25)), [2, 3.25, 4.5])
        self.assertEqual(take(3, count(2, 3.25-4j)), [2, 5.25-4j, 8.5-8j])
        self.assertEqual(take(3, count(Decimal('1.1'), Decimal('.1'))),
                         [Decimal('1.1'), Decimal('1.2'), Decimal('1.3')])
        self.assertEqual(take(3, count(Fraction(2,3), Fraction(1,7))),
                         [Fraction(2,3), Fraction(17,21), Fraction(20,21)])
        BIGINT = 1<<1000
        self.assertEqual(take(3, count(step=BIGINT)), [0, BIGINT, 2*BIGINT])
        self.assertEqual(repr(take(3, count(10, 2.5))), repr([10, 12.5, 15.0]))
        c = count(3, 5)
        self.assertEqual(repr(c), 'count(3, 5)')
        next(c)
        self.assertEqual(repr(c), 'count(8, 5)')
        c = count(-9, 0)
        self.assertEqual(repr(c), 'count(-9, 0)')
        next(c)
        self.assertEqual(repr(c), 'count(-9, 0)')
        c = count(-9, -3)
        self.assertEqual(repr(c), 'count(-9, -3)')
        next(c)
        self.assertEqual(repr(c), 'count(-12, -3)')
        self.assertEqual(repr(c), 'count(-12, -3)')
        self.assertEqual(repr(count(10.5, 1.25)), 'count(10.5, 1.25)')
        self.assertEqual(repr(count(10.5, 1)), 'count(10.5)')           # suppress step=1 when it's an int
        self.assertEqual(repr(count(10.5, 1.00)), 'count(10.5, 1.0)')   # do show float values lilke 1.0
        self.assertEqual(repr(count(10, 1.00)), 'count(10, 1.0)')
        c = count(10, 1.0)
        self.assertEqual(type(next(c)), int)
        self.assertEqual(type(next(c)), float)
        kila i kwenye (-sys.maxsize-5, -sys.maxsize+5 ,-10, -1, 0, 10, sys.maxsize-5, sys.maxsize+5):
            kila j kwenye  (-sys.maxsize-5, -sys.maxsize+5 ,-10, -1, 0, 1, 10, sys.maxsize-5, sys.maxsize+5):
                # Test repr
                r1 = repr(count(i, j))
                ikiwa j == 1:
                    r2 = ('count(%r)' % i)
                isipokua:
                    r2 = ('count(%r, %r)' % (i, j))
                self.assertEqual(r1, r2)
                kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                    self.pickletest(proto, count(i, j))

    eleza test_cycle(self):
        self.assertEqual(take(10, cycle('abc')), list('abcabcabca'))
        self.assertEqual(list(cycle('')), [])
        self.assertRaises(TypeError, cycle)
        self.assertRaises(TypeError, cycle, 5)
        self.assertEqual(list(islice(cycle(gen3()),10)), [0,1,2,0,1,2,0,1,2,0])

        # check copy, deepcopy, pickle
        c = cycle('abc')
        self.assertEqual(next(c), 'a')
        #simple copy currently sio supported, because __reduce__ rudishas
        #an internal iterator
        #self.assertEqual(take(10, copy.copy(c)), list('bcabcabcab'))
        self.assertEqual(take(10, copy.deepcopy(c)), list('bcabcabcab'))
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            self.assertEqual(take(10, pickle.loads(pickle.dumps(c, proto))),
                             list('bcabcabcab'))
            next(c)
            self.assertEqual(take(10, pickle.loads(pickle.dumps(c, proto))),
                             list('cabcabcabc'))
            next(c)
            next(c)
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            self.pickletest(proto, cycle('abc'))

        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            # test ukijumuisha partial consumed input iterable
            it = iter('abcde')
            c = cycle(it)
            _ = [next(c) kila i kwenye range(2)]      # consume 2 of 5 inputs
            p = pickle.dumps(c, proto)
            d = pickle.loads(p)                  # rebuild the cycle object
            self.assertEqual(take(20, d), list('cdeabcdeabcdeabcdeab'))

            # test ukijumuisha completely consumed input iterable
            it = iter('abcde')
            c = cycle(it)
            _ = [next(c) kila i kwenye range(7)]      # consume 7 of 5 inputs
            p = pickle.dumps(c, proto)
            d = pickle.loads(p)                  # rebuild the cycle object
            self.assertEqual(take(20, d), list('cdeabcdeabcdeabcdeab'))

    eleza test_cycle_setstate(self):
        # Verify both modes kila restoring state

        # Mode 0 ni efficient.  It uses an incompletely consumed input
        # iterator to build a cycle object na then pitaes kwenye state with
        # a list of previously consumed values.  There ni no data
        # overlap between the two.
        c = cycle('defg')
        c.__setstate__((list('abc'), 0))
        self.assertEqual(take(20, c), list('defgabcdefgabcdefgab'))

        # Mode 1 ni inefficient.  It starts ukijumuisha a cycle object built
        # kutoka an iterator over the remaining elements kwenye a partial
        # cycle na then pitaes kwenye state ukijumuisha all of the previously
        # seen values (this overlaps values included kwenye the iterator).
        c = cycle('defg')
        c.__setstate__((list('abcdefg'), 1))
        self.assertEqual(take(20, c), list('defgabcdefgabcdefgab'))

        # The first argument to setstate needs to be a tuple
        ukijumuisha self.assertRaises(TypeError):
            cycle('defg').__setstate__([list('abcdefg'), 0])

        # The first argument kwenye the setstate tuple must be a list
        ukijumuisha self.assertRaises(TypeError):
            c = cycle('defg')
            c.__setstate__((tuple('defg'), 0))
        take(20, c)

        # The second argument kwenye the setstate tuple must be an int
        ukijumuisha self.assertRaises(TypeError):
            cycle('defg').__setstate__((list('abcdefg'), 'x'))

        self.assertRaises(TypeError, cycle('').__setstate__, ())
        self.assertRaises(TypeError, cycle('').__setstate__, ([],))

    eleza test_groupby(self):
        # Check whether it accepts arguments correctly
        self.assertEqual([], list(groupby([])))
        self.assertEqual([], list(groupby([], key=id)))
        self.assertRaises(TypeError, list, groupby('abc', []))
        self.assertRaises(TypeError, groupby, Tupu)
        self.assertRaises(TypeError, groupby, 'abc', lambda x:x, 10)

        # Check normal input
        s = [(0, 10, 20), (0, 11,21), (0,12,21), (1,13,21), (1,14,22),
             (2,15,22), (3,16,23), (3,17,23)]
        dup = []
        kila k, g kwenye groupby(s, lambda r:r[0]):
            kila elem kwenye g:
                self.assertEqual(k, elem[0])
                dup.append(elem)
        self.assertEqual(s, dup)

        # Check normal pickled
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            dup = []
            kila k, g kwenye pickle.loads(pickle.dumps(groupby(s, testR), proto)):
                kila elem kwenye g:
                    self.assertEqual(k, elem[0])
                    dup.append(elem)
            self.assertEqual(s, dup)

        # Check nested case
        dup = []
        kila k, g kwenye groupby(s, testR):
            kila ik, ig kwenye groupby(g, testR2):
                kila elem kwenye ig:
                    self.assertEqual(k, elem[0])
                    self.assertEqual(ik, elem[2])
                    dup.append(elem)
        self.assertEqual(s, dup)

        # Check nested na pickled
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            dup = []
            kila k, g kwenye pickle.loads(pickle.dumps(groupby(s, testR), proto)):
                kila ik, ig kwenye pickle.loads(pickle.dumps(groupby(g, testR2), proto)):
                    kila elem kwenye ig:
                        self.assertEqual(k, elem[0])
                        self.assertEqual(ik, elem[2])
                        dup.append(elem)
            self.assertEqual(s, dup)


        # Check case where inner iterator ni sio used
        keys = [k kila k, g kwenye groupby(s, testR)]
        expectedkeys = set([r[0] kila r kwenye s])
        self.assertEqual(set(keys), expectedkeys)
        self.assertEqual(len(keys), len(expectedkeys))

        # Check case where inner iterator ni used after advancing the groupby
        # iterator
        s = list(zip('AABBBAAAA', range(9)))
        it = groupby(s, testR)
        _, g1 = next(it)
        _, g2 = next(it)
        _, g3 = next(it)
        self.assertEqual(list(g1), [])
        self.assertEqual(list(g2), [])
        self.assertEqual(next(g3), ('A', 5))
        list(it)  # exhaust the groupby iterator
        self.assertEqual(list(g3), [])

        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            it = groupby(s, testR)
            _, g = next(it)
            next(it)
            next(it)
            self.assertEqual(list(pickle.loads(pickle.dumps(g, proto))), [])

        # Exercise pipes na filters style
        s = 'abracadabra'
        # sort s | uniq
        r = [k kila k, g kwenye groupby(sorted(s))]
        self.assertEqual(r, ['a', 'b', 'c', 'd', 'r'])
        # sort s | uniq -d
        r = [k kila k, g kwenye groupby(sorted(s)) ikiwa list(islice(g,1,2))]
        self.assertEqual(r, ['a', 'b', 'r'])
        # sort s | uniq -c
        r = [(len(list(g)), k) kila k, g kwenye groupby(sorted(s))]
        self.assertEqual(r, [(5, 'a'), (2, 'b'), (1, 'c'), (1, 'd'), (2, 'r')])
        # sort s | uniq -c | sort -rn | head -3
        r = sorted([(len(list(g)) , k) kila k, g kwenye groupby(sorted(s))], reverse=Kweli)[:3]
        self.assertEqual(r, [(5, 'a'), (2, 'r'), (2, 'b')])

        # iter.__next__ failure
        kundi ExpectedError(Exception):
            pita
        eleza delayed_ashiria(n=0):
            kila i kwenye range(n):
                tuma 'yo'
            ashiria ExpectedError
        eleza gulp(iterable, keyp=Tupu, func=list):
            rudisha [func(g) kila k, g kwenye groupby(iterable, keyp)]

        # iter.__next__ failure on outer object
        self.assertRaises(ExpectedError, gulp, delayed_ashiria(0))
        # iter.__next__ failure on inner object
        self.assertRaises(ExpectedError, gulp, delayed_ashiria(1))

        # __eq__ failure
        kundi DummyCmp:
            eleza __eq__(self, dst):
                ashiria ExpectedError
        s = [DummyCmp(), DummyCmp(), Tupu]

        # __eq__ failure on outer object
        self.assertRaises(ExpectedError, gulp, s, func=id)
        # __eq__ failure on inner object
        self.assertRaises(ExpectedError, gulp, s)

        # keyfunc failure
        eleza keyfunc(obj):
            ikiwa keyfunc.skip > 0:
                keyfunc.skip -= 1
                rudisha obj
            isipokua:
                ashiria ExpectedError

        # keyfunc failure on outer object
        keyfunc.skip = 0
        self.assertRaises(ExpectedError, gulp, [Tupu], keyfunc)
        keyfunc.skip = 1
        self.assertRaises(ExpectedError, gulp, [Tupu, Tupu], keyfunc)

    eleza test_filter(self):
        self.assertEqual(list(filter(isEven, range(6))), [0,2,4])
        self.assertEqual(list(filter(Tupu, [0,1,0,2,0])), [1,2])
        self.assertEqual(list(filter(bool, [0,1,0,2,0])), [1,2])
        self.assertEqual(take(4, filter(isEven, count())), [0,2,4,6])
        self.assertRaises(TypeError, filter)
        self.assertRaises(TypeError, filter, lambda x:x)
        self.assertRaises(TypeError, filter, lambda x:x, range(6), 7)
        self.assertRaises(TypeError, filter, isEven, 3)
        self.assertRaises(TypeError, next, filter(range(6), range(6)))

        # check copy, deepcopy, pickle
        ans = [0,2,4]

        c = filter(isEven, range(6))
        self.assertEqual(list(copy.copy(c)), ans)
        c = filter(isEven, range(6))
        self.assertEqual(list(copy.deepcopy(c)), ans)
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            c = filter(isEven, range(6))
            self.assertEqual(list(pickle.loads(pickle.dumps(c, proto))), ans)
            next(c)
            self.assertEqual(list(pickle.loads(pickle.dumps(c, proto))), ans[1:])
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            c = filter(isEven, range(6))
            self.pickletest(proto, c)

    eleza test_filterfalse(self):
        self.assertEqual(list(filterfalse(isEven, range(6))), [1,3,5])
        self.assertEqual(list(filterfalse(Tupu, [0,1,0,2,0])), [0,0,0])
        self.assertEqual(list(filterfalse(bool, [0,1,0,2,0])), [0,0,0])
        self.assertEqual(take(4, filterfalse(isEven, count())), [1,3,5,7])
        self.assertRaises(TypeError, filterfalse)
        self.assertRaises(TypeError, filterfalse, lambda x:x)
        self.assertRaises(TypeError, filterfalse, lambda x:x, range(6), 7)
        self.assertRaises(TypeError, filterfalse, isEven, 3)
        self.assertRaises(TypeError, next, filterfalse(range(6), range(6)))
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            self.pickletest(proto, filterfalse(isEven, range(6)))

    eleza test_zip(self):
        # XXX This ni rather silly now that builtin zip() calls zip()...
        ans = [(x,y) kila x, y kwenye zip('abc',count())]
        self.assertEqual(ans, [('a', 0), ('b', 1), ('c', 2)])
        self.assertEqual(list(zip('abc', range(6))), lzip('abc', range(6)))
        self.assertEqual(list(zip('abcdef', range(3))), lzip('abcdef', range(3)))
        self.assertEqual(take(3,zip('abcdef', count())), lzip('abcdef', range(3)))
        self.assertEqual(list(zip('abcdef')), lzip('abcdef'))
        self.assertEqual(list(zip()), lzip())
        self.assertRaises(TypeError, zip, 3)
        self.assertRaises(TypeError, zip, range(3), 3)
        self.assertEqual([tuple(list(pair)) kila pair kwenye zip('abc', 'def')],
                         lzip('abc', 'def'))
        self.assertEqual([pair kila pair kwenye zip('abc', 'def')],
                         lzip('abc', 'def'))

    @support.impl_detail("tuple reuse ni specific to CPython")
    eleza test_zip_tuple_reuse(self):
        ids = list(map(id, zip('abc', 'def')))
        self.assertEqual(min(ids), max(ids))
        ids = list(map(id, list(zip('abc', 'def'))))
        self.assertEqual(len(dict.kutokakeys(ids)), len(ids))

        # check copy, deepcopy, pickle
        ans = [(x,y) kila x, y kwenye copy.copy(zip('abc',count()))]
        self.assertEqual(ans, [('a', 0), ('b', 1), ('c', 2)])

        ans = [(x,y) kila x, y kwenye copy.deepcopy(zip('abc',count()))]
        self.assertEqual(ans, [('a', 0), ('b', 1), ('c', 2)])

        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ans = [(x,y) kila x, y kwenye pickle.loads(pickle.dumps(zip('abc',count()), proto))]
            self.assertEqual(ans, [('a', 0), ('b', 1), ('c', 2)])

        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            testIntermediate = zip('abc',count())
            next(testIntermediate)
            ans = [(x,y) kila x, y kwenye pickle.loads(pickle.dumps(testIntermediate, proto))]
            self.assertEqual(ans, [('b', 1), ('c', 2)])

        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            self.pickletest(proto, zip('abc', count()))

    eleza test_ziplongest(self):
        kila args kwenye [
                ['abc', range(6)],
                [range(6), 'abc'],
                [range(1000), range(2000,2100), range(3000,3050)],
                [range(1000), range(0), range(3000,3050), range(1200), range(1500)],
                [range(1000), range(0), range(3000,3050), range(1200), range(1500), range(0)],
            ]:
            target = [tuple([arg[i] ikiwa i < len(arg) isipokua Tupu kila arg kwenye args])
                      kila i kwenye range(max(map(len, args)))]
            self.assertEqual(list(zip_longest(*args)), target)
            self.assertEqual(list(zip_longest(*args, **{})), target)
            target = [tuple((e ni Tupu na 'X' ama e) kila e kwenye t) kila t kwenye target]   # Replace Tupu fills ukijumuisha 'X'
            self.assertEqual(list(zip_longest(*args, **dict(fillvalue='X'))), target)

        self.assertEqual(take(3,zip_longest('abcdef', count())), list(zip('abcdef', range(3)))) # take 3 kutoka infinite input

        self.assertEqual(list(zip_longest()), list(zip()))
        self.assertEqual(list(zip_longest([])), list(zip([])))
        self.assertEqual(list(zip_longest('abcdef')), list(zip('abcdef')))

        self.assertEqual(list(zip_longest('abc', 'defg', **{})),
                         list(zip(list('abc')+[Tupu], 'defg'))) # empty keyword dict
        self.assertRaises(TypeError, zip_longest, 3)
        self.assertRaises(TypeError, zip_longest, range(3), 3)

        kila stmt kwenye [
            "zip_longest('abc', fv=1)",
            "zip_longest('abc', fillvalue=1, bogus_keyword=Tupu)",
        ]:
            jaribu:
                eval(stmt, globals(), locals())
            tatizo TypeError:
                pita
            isipokua:
                self.fail('Did sio ashiria Type in:  ' + stmt)

        self.assertEqual([tuple(list(pair)) kila pair kwenye zip_longest('abc', 'def')],
                         list(zip('abc', 'def')))
        self.assertEqual([pair kila pair kwenye zip_longest('abc', 'def')],
                         list(zip('abc', 'def')))

    @support.impl_detail("tuple reuse ni specific to CPython")
    eleza test_zip_longest_tuple_reuse(self):
        ids = list(map(id, zip_longest('abc', 'def')))
        self.assertEqual(min(ids), max(ids))
        ids = list(map(id, list(zip_longest('abc', 'def'))))
        self.assertEqual(len(dict.kutokakeys(ids)), len(ids))

    eleza test_zip_longest_pickling(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            self.pickletest(proto, zip_longest("abc", "def"))
            self.pickletest(proto, zip_longest("abc", "defgh"))
            self.pickletest(proto, zip_longest("abc", "defgh", fillvalue=1))
            self.pickletest(proto, zip_longest("", "defgh"))

    eleza test_zip_longest_bad_iterable(self):
        exception = TypeError()

        kundi BadIterable:
            eleza __iter__(self):
                ashiria exception

        ukijumuisha self.assertRaises(TypeError) kama cm:
            zip_longest(BadIterable())

        self.assertIs(cm.exception, exception)

    eleza test_bug_7244(self):

        kundi Repeater:
            # this kundi ni similar to itertools.repeat
            eleza __init__(self, o, t, e):
                self.o = o
                self.t = int(t)
                self.e = e
            eleza __iter__(self): # its iterator ni itself
                rudisha self
            eleza __next__(self):
                ikiwa self.t > 0:
                    self.t -= 1
                    rudisha self.o
                isipokua:
                    ashiria self.e

        # Formerly this code kwenye would fail kwenye debug mode
        # ukijumuisha Undetected Error na Stop Iteration
        r1 = Repeater(1, 3, StopIteration)
        r2 = Repeater(2, 4, StopIteration)
        eleza run(r1, r2):
            result = []
            kila i, j kwenye zip_longest(r1, r2, fillvalue=0):
                ukijumuisha support.captured_output('stdout'):
                    andika((i, j))
                result.append((i, j))
            rudisha result
        self.assertEqual(run(r1, r2), [(1,2), (1,2), (1,2), (0,2)])

        # Formerly, the RuntimeError would be lost
        # na StopIteration would stop kama expected
        r1 = Repeater(1, 3, RuntimeError)
        r2 = Repeater(2, 4, StopIteration)
        it = zip_longest(r1, r2, fillvalue=0)
        self.assertEqual(next(it), (1, 2))
        self.assertEqual(next(it), (1, 2))
        self.assertEqual(next(it), (1, 2))
        self.assertRaises(RuntimeError, next, it)

    eleza test_product(self):
        kila args, result kwenye [
            ([], [()]),                     # zero iterables
            (['ab'], [('a',), ('b',)]),     # one iterable
            ([range(2), range(3)], [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)]),     # two iterables
            ([range(0), range(2), range(3)], []),           # first iterable ukijumuisha zero length
            ([range(2), range(0), range(3)], []),           # middle iterable ukijumuisha zero length
            ([range(2), range(3), range(0)], []),           # last iterable ukijumuisha zero length
            ]:
            self.assertEqual(list(product(*args)), result)
            kila r kwenye range(4):
                self.assertEqual(list(product(*(args*r))),
                                 list(product(*args, **dict(repeat=r))))
        self.assertEqual(len(list(product(*[range(7)]*6))), 7**6)
        self.assertRaises(TypeError, product, range(6), Tupu)

        eleza product1(*args, **kwds):
            pools = list(map(tuple, args)) * kwds.get('repeat', 1)
            n = len(pools)
            ikiwa n == 0:
                tuma ()
                rudisha
            ikiwa any(len(pool) == 0 kila pool kwenye pools):
                rudisha
            indices = [0] * n
            tuma tuple(pool[i] kila pool, i kwenye zip(pools, indices))
            wakati 1:
                kila i kwenye reversed(range(n)):  # right to left
                    ikiwa indices[i] == len(pools[i]) - 1:
                        endelea
                    indices[i] += 1
                    kila j kwenye range(i+1, n):
                        indices[j] = 0
                    tuma tuple(pool[i] kila pool, i kwenye zip(pools, indices))
                    koma
                isipokua:
                    rudisha

        eleza product2(*args, **kwds):
            'Pure python version used kwenye docs'
            pools = list(map(tuple, args)) * kwds.get('repeat', 1)
            result = [[]]
            kila pool kwenye pools:
                result = [x+[y] kila x kwenye result kila y kwenye pool]
            kila prod kwenye result:
                tuma tuple(prod)

        argtypes = ['', 'abc', '', range(0), range(4), dict(a=1, b=2, c=3),
                    set('abcdefg'), range(11), tuple(range(13))]
        kila i kwenye range(100):
            args = [random.choice(argtypes) kila j kwenye range(random.randrange(5))]
            expected_len = prod(map(len, args))
            self.assertEqual(len(list(product(*args))), expected_len)
            self.assertEqual(list(product(*args)), list(product1(*args)))
            self.assertEqual(list(product(*args)), list(product2(*args)))
            args = map(iter, args)
            self.assertEqual(len(list(product(*args))), expected_len)

    @support.bigaddrspacetest
    eleza test_product_overflow(self):
        ukijumuisha self.assertRaises((OverflowError, MemoryError)):
            product(*(['ab']*2**5), repeat=2**25)

    @support.impl_detail("tuple reuse ni specific to CPython")
    eleza test_product_tuple_reuse(self):
        self.assertEqual(len(set(map(id, product('abc', 'def')))), 1)
        self.assertNotEqual(len(set(map(id, list(product('abc', 'def'))))), 1)

    eleza test_product_pickling(self):
        # check copy, deepcopy, pickle
        kila args, result kwenye [
            ([], [()]),                     # zero iterables
            (['ab'], [('a',), ('b',)]),     # one iterable
            ([range(2), range(3)], [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)]),     # two iterables
            ([range(0), range(2), range(3)], []),           # first iterable ukijumuisha zero length
            ([range(2), range(0), range(3)], []),           # middle iterable ukijumuisha zero length
            ([range(2), range(3), range(0)], []),           # last iterable ukijumuisha zero length
            ]:
            self.assertEqual(list(copy.copy(product(*args))), result)
            self.assertEqual(list(copy.deepcopy(product(*args))), result)
            kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                self.pickletest(proto, product(*args))

    eleza test_product_issue_25021(self):
        # test that indices are properly clamped to the length of the tuples
        p = product((1, 2),(3,))
        p.__setstate__((0, 0x1000))  # will access tuple element 1 ikiwa sio clamped
        self.assertEqual(next(p), (2, 3))
        # test that empty tuple kwenye the list will result kwenye an immediate StopIteration
        p = product((1, 2), (), (3,))
        p.__setstate__((0, 0, 0x1000))  # will access tuple element 1 ikiwa sio clamped
        self.assertRaises(StopIteration, next, p)

    eleza test_repeat(self):
        self.assertEqual(list(repeat(object='a', times=3)), ['a', 'a', 'a'])
        self.assertEqual(lzip(range(3),repeat('a')),
                         [(0, 'a'), (1, 'a'), (2, 'a')])
        self.assertEqual(list(repeat('a', 3)), ['a', 'a', 'a'])
        self.assertEqual(take(3, repeat('a')), ['a', 'a', 'a'])
        self.assertEqual(list(repeat('a', 0)), [])
        self.assertEqual(list(repeat('a', -3)), [])
        self.assertRaises(TypeError, repeat)
        self.assertRaises(TypeError, repeat, Tupu, 3, 4)
        self.assertRaises(TypeError, repeat, Tupu, 'a')
        r = repeat(1+0j)
        self.assertEqual(repr(r), 'repeat((1+0j))')
        r = repeat(1+0j, 5)
        self.assertEqual(repr(r), 'repeat((1+0j), 5)')
        list(r)
        self.assertEqual(repr(r), 'repeat((1+0j), 0)')

        # check copy, deepcopy, pickle
        c = repeat(object='a', times=10)
        self.assertEqual(next(c), 'a')
        self.assertEqual(take(2, copy.copy(c)), list('a' * 2))
        self.assertEqual(take(2, copy.deepcopy(c)), list('a' * 2))
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            self.pickletest(proto, repeat(object='a', times=10))

    eleza test_repeat_with_negative_times(self):
        self.assertEqual(repr(repeat('a', -1)), "repeat('a', 0)")
        self.assertEqual(repr(repeat('a', -2)), "repeat('a', 0)")
        self.assertEqual(repr(repeat('a', times=-1)), "repeat('a', 0)")
        self.assertEqual(repr(repeat('a', times=-2)), "repeat('a', 0)")

    eleza test_map(self):
        self.assertEqual(list(map(operator.pow, range(3), range(1,7))),
                         [0**1, 1**2, 2**3])
        self.assertEqual(list(map(tupleize, 'abc', range(5))),
                         [('a',0),('b',1),('c',2)])
        self.assertEqual(list(map(tupleize, 'abc', count())),
                         [('a',0),('b',1),('c',2)])
        self.assertEqual(take(2,map(tupleize, 'abc', count())),
                         [('a',0),('b',1)])
        self.assertEqual(list(map(operator.pow, [])), [])
        self.assertRaises(TypeError, map)
        self.assertRaises(TypeError, list, map(Tupu, range(3), range(3)))
        self.assertRaises(TypeError, map, operator.neg)
        self.assertRaises(TypeError, next, map(10, range(5)))
        self.assertRaises(ValueError, next, map(errfunc, [4], [5]))
        self.assertRaises(TypeError, next, map(onearg, [4], [5]))

        # check copy, deepcopy, pickle
        ans = [('a',0),('b',1),('c',2)]

        c = map(tupleize, 'abc', count())
        self.assertEqual(list(copy.copy(c)), ans)

        c = map(tupleize, 'abc', count())
        self.assertEqual(list(copy.deepcopy(c)), ans)

        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            c = map(tupleize, 'abc', count())
            self.pickletest(proto, c)

    eleza test_starmap(self):
        self.assertEqual(list(starmap(operator.pow, zip(range(3), range(1,7)))),
                         [0**1, 1**2, 2**3])
        self.assertEqual(take(3, starmap(operator.pow, zip(count(), count(1)))),
                         [0**1, 1**2, 2**3])
        self.assertEqual(list(starmap(operator.pow, [])), [])
        self.assertEqual(list(starmap(operator.pow, [iter([4,5])])), [4**5])
        self.assertRaises(TypeError, list, starmap(operator.pow, [Tupu]))
        self.assertRaises(TypeError, starmap)
        self.assertRaises(TypeError, starmap, operator.pow, [(4,5)], 'extra')
        self.assertRaises(TypeError, next, starmap(10, [(4,5)]))
        self.assertRaises(ValueError, next, starmap(errfunc, [(4,5)]))
        self.assertRaises(TypeError, next, starmap(onearg, [(4,5)]))

        # check copy, deepcopy, pickle
        ans = [0**1, 1**2, 2**3]

        c = starmap(operator.pow, zip(range(3), range(1,7)))
        self.assertEqual(list(copy.copy(c)), ans)

        c = starmap(operator.pow, zip(range(3), range(1,7)))
        self.assertEqual(list(copy.deepcopy(c)), ans)

        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            c = starmap(operator.pow, zip(range(3), range(1,7)))
            self.pickletest(proto, c)

    eleza test_islice(self):
        kila args kwenye [          # islice(args) should agree ukijumuisha range(args)
                (10, 20, 3),
                (10, 3, 20),
                (10, 20),
                (10, 10),
                (10, 3),
                (20,)
                ]:
            self.assertEqual(list(islice(range(100), *args)),
                             list(range(*args)))

        kila args, tgtargs kwenye [  # Stop when seqn ni exhausted
                ((10, 110, 3), ((10, 100, 3))),
                ((10, 110), ((10, 100))),
                ((110,), (100,))
                ]:
            self.assertEqual(list(islice(range(100), *args)),
                             list(range(*tgtargs)))

        # Test stop=Tupu
        self.assertEqual(list(islice(range(10), Tupu)), list(range(10)))
        self.assertEqual(list(islice(range(10), Tupu, Tupu)), list(range(10)))
        self.assertEqual(list(islice(range(10), Tupu, Tupu, Tupu)), list(range(10)))
        self.assertEqual(list(islice(range(10), 2, Tupu)), list(range(2, 10)))
        self.assertEqual(list(islice(range(10), 1, Tupu, 2)), list(range(1, 10, 2)))

        # Test number of items consumed     SF #1171417
        it = iter(range(10))
        self.assertEqual(list(islice(it, 3)), list(range(3)))
        self.assertEqual(list(it), list(range(3, 10)))

        it = iter(range(10))
        self.assertEqual(list(islice(it, 3, 3)), [])
        self.assertEqual(list(it), list(range(3, 10)))

        # Test invalid arguments
        ra = range(10)
        self.assertRaises(TypeError, islice, ra)
        self.assertRaises(TypeError, islice, ra, 1, 2, 3, 4)
        self.assertRaises(ValueError, islice, ra, -5, 10, 1)
        self.assertRaises(ValueError, islice, ra, 1, -5, -1)
        self.assertRaises(ValueError, islice, ra, 1, 10, -1)
        self.assertRaises(ValueError, islice, ra, 1, 10, 0)
        self.assertRaises(ValueError, islice, ra, 'a')
        self.assertRaises(ValueError, islice, ra, 'a', 1)
        self.assertRaises(ValueError, islice, ra, 1, 'a')
        self.assertRaises(ValueError, islice, ra, 'a', 1, 1)
        self.assertRaises(ValueError, islice, ra, 1, 'a', 1)
        self.assertEqual(len(list(islice(count(), 1, 10, maxsize))), 1)

        # Issue #10323:  Less islice kwenye a predictable state
        c = count()
        self.assertEqual(list(islice(c, 1, 3, 50)), [1])
        self.assertEqual(next(c), 3)

        # check copy, deepcopy, pickle
        kila args kwenye [          # islice(args) should agree ukijumuisha range(args)
                (10, 20, 3),
                (10, 3, 20),
                (10, 20),
                (10, 3),
                (20,)
                ]:
            self.assertEqual(list(copy.copy(islice(range(100), *args))),
                             list(range(*args)))
            self.assertEqual(list(copy.deepcopy(islice(range(100), *args))),
                             list(range(*args)))
            kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                self.pickletest(proto, islice(range(100), *args))

        # Issue #21321: check source iterator ni sio referenced
        # kutoka islice() after the latter has been exhausted
        it = (x kila x kwenye (1, 2))
        wr = weakref.ref(it)
        it = islice(it, 1)
        self.assertIsNotTupu(wr())
        list(it) # exhaust the iterator
        support.gc_collect()
        self.assertIsTupu(wr())

        # Issue #30537: islice can accept integer-like objects as
        # arguments
        kundi IntLike(object):
            eleza __init__(self, val):
                self.val = val
            eleza __index__(self):
                rudisha self.val
        self.assertEqual(list(islice(range(100), IntLike(10))), list(range(10)))
        self.assertEqual(list(islice(range(100), IntLike(10), IntLike(50))),
                         list(range(10, 50)))
        self.assertEqual(list(islice(range(100), IntLike(10), IntLike(50), IntLike(5))),
                         list(range(10,50,5)))

    eleza test_takewhile(self):
        data = [1, 3, 5, 20, 2, 4, 6, 8]
        self.assertEqual(list(takewhile(underten, data)), [1, 3, 5])
        self.assertEqual(list(takewhile(underten, [])), [])
        self.assertRaises(TypeError, takewhile)
        self.assertRaises(TypeError, takewhile, operator.pow)
        self.assertRaises(TypeError, takewhile, operator.pow, [(4,5)], 'extra')
        self.assertRaises(TypeError, next, takewhile(10, [(4,5)]))
        self.assertRaises(ValueError, next, takewhile(errfunc, [(4,5)]))
        t = takewhile(bool, [1, 1, 1, 0, 0, 0])
        self.assertEqual(list(t), [1, 1, 1])
        self.assertRaises(StopIteration, next, t)

        # check copy, deepcopy, pickle
        self.assertEqual(list(copy.copy(takewhile(underten, data))), [1, 3, 5])
        self.assertEqual(list(copy.deepcopy(takewhile(underten, data))),
                        [1, 3, 5])
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            self.pickletest(proto, takewhile(underten, data))

    eleza test_dropwhile(self):
        data = [1, 3, 5, 20, 2, 4, 6, 8]
        self.assertEqual(list(dropwhile(underten, data)), [20, 2, 4, 6, 8])
        self.assertEqual(list(dropwhile(underten, [])), [])
        self.assertRaises(TypeError, dropwhile)
        self.assertRaises(TypeError, dropwhile, operator.pow)
        self.assertRaises(TypeError, dropwhile, operator.pow, [(4,5)], 'extra')
        self.assertRaises(TypeError, next, dropwhile(10, [(4,5)]))
        self.assertRaises(ValueError, next, dropwhile(errfunc, [(4,5)]))

        # check copy, deepcopy, pickle
        self.assertEqual(list(copy.copy(dropwhile(underten, data))), [20, 2, 4, 6, 8])
        self.assertEqual(list(copy.deepcopy(dropwhile(underten, data))),
                        [20, 2, 4, 6, 8])
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            self.pickletest(proto, dropwhile(underten, data))

    eleza test_tee(self):
        n = 200

        a, b = tee([])        # test empty iterator
        self.assertEqual(list(a), [])
        self.assertEqual(list(b), [])

        a, b = tee(irange(n)) # test 100% interleaved
        self.assertEqual(lzip(a,b), lzip(range(n), range(n)))

        a, b = tee(irange(n)) # test 0% interleaved
        self.assertEqual(list(a), list(range(n)))
        self.assertEqual(list(b), list(range(n)))

        a, b = tee(irange(n)) # test dealloc of leading iterator
        kila i kwenye range(100):
            self.assertEqual(next(a), i)
        toa a
        self.assertEqual(list(b), list(range(n)))

        a, b = tee(irange(n)) # test dealloc of trailing iterator
        kila i kwenye range(100):
            self.assertEqual(next(a), i)
        toa b
        self.assertEqual(list(a), list(range(100, n)))

        kila j kwenye range(5):   # test randomly interleaved
            order = [0]*n + [1]*n
            random.shuffle(order)
            lists = ([], [])
            its = tee(irange(n))
            kila i kwenye order:
                value = next(its[i])
                lists[i].append(value)
            self.assertEqual(lists[0], list(range(n)))
            self.assertEqual(lists[1], list(range(n)))

        # test argument format checking
        self.assertRaises(TypeError, tee)
        self.assertRaises(TypeError, tee, 3)
        self.assertRaises(TypeError, tee, [1,2], 'x')
        self.assertRaises(TypeError, tee, [1,2], 3, 'x')

        # tee object should be instantiable
        a, b = tee('abc')
        c = type(a)('def')
        self.assertEqual(list(c), list('def'))

        # test long-lagged na multi-way split
        a, b, c = tee(range(2000), 3)
        kila i kwenye range(100):
            self.assertEqual(next(a), i)
        self.assertEqual(list(b), list(range(2000)))
        self.assertEqual([next(c), next(c)], list(range(2)))
        self.assertEqual(list(a), list(range(100,2000)))
        self.assertEqual(list(c), list(range(2,2000)))

        # test values of n
        self.assertRaises(TypeError, tee, 'abc', 'invalid')
        self.assertRaises(ValueError, tee, [], -1)
        kila n kwenye range(5):
            result = tee('abc', n)
            self.assertEqual(type(result), tuple)
            self.assertEqual(len(result), n)
            self.assertEqual([list(x) kila x kwenye result], [list('abc')]*n)

        # tee pita-through to copyable iterator
        a, b = tee('abc')
        c, d = tee(a)
        self.assertKweli(a ni c)

        # test tee_new
        t1, t2 = tee('abc')
        tnew = type(t1)
        self.assertRaises(TypeError, tnew)
        self.assertRaises(TypeError, tnew, 10)
        t3 = tnew(t1)
        self.assertKweli(list(t1) == list(t2) == list(t3) == list('abc'))

        # test that tee objects are weak referencable
        a, b = tee(range(10))
        p = weakref.proxy(a)
        self.assertEqual(getattr(p, '__class__'), type(b))
        toa a
        self.assertRaises(ReferenceError, getattr, p, '__class__')

        ans = list('abc')
        long_ans = list(range(10000))

        # check copy
        a, b = tee('abc')
        self.assertEqual(list(copy.copy(a)), ans)
        self.assertEqual(list(copy.copy(b)), ans)
        a, b = tee(list(range(10000)))
        self.assertEqual(list(copy.copy(a)), long_ans)
        self.assertEqual(list(copy.copy(b)), long_ans)

        # check partially consumed copy
        a, b = tee('abc')
        take(2, a)
        take(1, b)
        self.assertEqual(list(copy.copy(a)), ans[2:])
        self.assertEqual(list(copy.copy(b)), ans[1:])
        self.assertEqual(list(a), ans[2:])
        self.assertEqual(list(b), ans[1:])
        a, b = tee(range(10000))
        take(100, a)
        take(60, b)
        self.assertEqual(list(copy.copy(a)), long_ans[100:])
        self.assertEqual(list(copy.copy(b)), long_ans[60:])
        self.assertEqual(list(a), long_ans[100:])
        self.assertEqual(list(b), long_ans[60:])

        # check deepcopy
        a, b = tee('abc')
        self.assertEqual(list(copy.deepcopy(a)), ans)
        self.assertEqual(list(copy.deepcopy(b)), ans)
        self.assertEqual(list(a), ans)
        self.assertEqual(list(b), ans)
        a, b = tee(range(10000))
        self.assertEqual(list(copy.deepcopy(a)), long_ans)
        self.assertEqual(list(copy.deepcopy(b)), long_ans)
        self.assertEqual(list(a), long_ans)
        self.assertEqual(list(b), long_ans)

        # check partially consumed deepcopy
        a, b = tee('abc')
        take(2, a)
        take(1, b)
        self.assertEqual(list(copy.deepcopy(a)), ans[2:])
        self.assertEqual(list(copy.deepcopy(b)), ans[1:])
        self.assertEqual(list(a), ans[2:])
        self.assertEqual(list(b), ans[1:])
        a, b = tee(range(10000))
        take(100, a)
        take(60, b)
        self.assertEqual(list(copy.deepcopy(a)), long_ans[100:])
        self.assertEqual(list(copy.deepcopy(b)), long_ans[60:])
        self.assertEqual(list(a), long_ans[100:])
        self.assertEqual(list(b), long_ans[60:])

        # check pickle
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            self.pickletest(proto, iter(tee('abc')))
            a, b = tee('abc')
            self.pickletest(proto, a, compare=ans)
            self.pickletest(proto, b, compare=ans)

    # Issue 13454: Crash when deleting backward iterator kutoka tee()
    eleza test_tee_del_backward(self):
        forward, backward = tee(repeat(Tupu, 20000000))
        jaribu:
            any(forward)  # exhaust the iterator
            toa backward
        tatizo:
            toa forward, backward
            ashiria

    eleza test_tee_reenter(self):
        kundi I:
            first = Kweli
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                first = self.first
                self.first = Uongo
                ikiwa first:
                    rudisha next(b)

        a, b = tee(I())
        ukijumuisha self.assertRaisesRegex(RuntimeError, "tee"):
            next(a)

    eleza test_tee_concurrent(self):
        start = threading.Event()
        finish = threading.Event()
        kundi I:
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                start.set()
                finish.wait()

        a, b = tee(I())
        thread = threading.Thread(target=next, args=[a])
        thread.start()
        jaribu:
            start.wait()
            ukijumuisha self.assertRaisesRegex(RuntimeError, "tee"):
                next(b)
        mwishowe:
            finish.set()
            thread.join()

    eleza test_StopIteration(self):
        self.assertRaises(StopIteration, next, zip())

        kila f kwenye (chain, cycle, zip, groupby):
            self.assertRaises(StopIteration, next, f([]))
            self.assertRaises(StopIteration, next, f(StopNow()))

        self.assertRaises(StopIteration, next, islice([], Tupu))
        self.assertRaises(StopIteration, next, islice(StopNow(), Tupu))

        p, q = tee([])
        self.assertRaises(StopIteration, next, p)
        self.assertRaises(StopIteration, next, q)
        p, q = tee(StopNow())
        self.assertRaises(StopIteration, next, p)
        self.assertRaises(StopIteration, next, q)

        self.assertRaises(StopIteration, next, repeat(Tupu, 0))

        kila f kwenye (filter, filterfalse, map, takewhile, dropwhile, starmap):
            self.assertRaises(StopIteration, next, f(lambda x:x, []))
            self.assertRaises(StopIteration, next, f(lambda x:x, StopNow()))

kundi TestExamples(unittest.TestCase):

    eleza test_accumulate(self):
        self.assertEqual(list(accumulate([1,2,3,4,5])), [1, 3, 6, 10, 15])

    eleza test_accumulate_reducible(self):
        # check copy, deepcopy, pickle
        data = [1, 2, 3, 4, 5]
        accumulated = [1, 3, 6, 10, 15]

        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            it = accumulate(data)
            self.assertEqual(list(pickle.loads(pickle.dumps(it, proto))), accumulated[:])
            self.assertEqual(next(it), 1)
            self.assertEqual(list(pickle.loads(pickle.dumps(it, proto))), accumulated[1:])
        it = accumulate(data)
        self.assertEqual(next(it), 1)
        self.assertEqual(list(copy.deepcopy(it)), accumulated[1:])
        self.assertEqual(list(copy.copy(it)), accumulated[1:])

    eleza test_accumulate_reducible_none(self):
        # Issue #25718: total ni Tupu
        it = accumulate([Tupu, Tupu, Tupu], operator.is_)
        self.assertEqual(next(it), Tupu)
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            it_copy = pickle.loads(pickle.dumps(it, proto))
            self.assertEqual(list(it_copy), [Kweli, Uongo])
        self.assertEqual(list(copy.deepcopy(it)), [Kweli, Uongo])
        self.assertEqual(list(copy.copy(it)), [Kweli, Uongo])

    eleza test_chain(self):
        self.assertEqual(''.join(chain('ABC', 'DEF')), 'ABCDEF')

    eleza test_chain_from_iterable(self):
        self.assertEqual(''.join(chain.kutoka_iterable(['ABC', 'DEF'])), 'ABCDEF')

    eleza test_combinations(self):
        self.assertEqual(list(combinations('ABCD', 2)),
                         [('A','B'), ('A','C'), ('A','D'), ('B','C'), ('B','D'), ('C','D')])
        self.assertEqual(list(combinations(range(4), 3)),
                         [(0,1,2), (0,1,3), (0,2,3), (1,2,3)])

    eleza test_combinations_with_replacement(self):
        self.assertEqual(list(combinations_with_replacement('ABC', 2)),
                         [('A','A'), ('A','B'), ('A','C'), ('B','B'), ('B','C'), ('C','C')])

    eleza test_compress(self):
        self.assertEqual(list(compress('ABCDEF', [1,0,1,0,1,1])), list('ACEF'))

    eleza test_count(self):
        self.assertEqual(list(islice(count(10), 5)), [10, 11, 12, 13, 14])

    eleza test_cycle(self):
        self.assertEqual(list(islice(cycle('ABCD'), 12)), list('ABCDABCDABCD'))

    eleza test_dropwhile(self):
        self.assertEqual(list(dropwhile(lambda x: x<5, [1,4,6,4,1])), [6,4,1])

    eleza test_groupby(self):
        self.assertEqual([k kila k, g kwenye groupby('AAAABBBCCDAABBB')],
                         list('ABCDAB'))
        self.assertEqual([(list(g)) kila k, g kwenye groupby('AAAABBBCCD')],
                         [list('AAAA'), list('BBB'), list('CC'), list('D')])

    eleza test_filter(self):
        self.assertEqual(list(filter(lambda x: x%2, range(10))), [1,3,5,7,9])

    eleza test_filterfalse(self):
        self.assertEqual(list(filterfalse(lambda x: x%2, range(10))), [0,2,4,6,8])

    eleza test_map(self):
        self.assertEqual(list(map(pow, (2,3,10), (5,2,3))), [32, 9, 1000])

    eleza test_islice(self):
        self.assertEqual(list(islice('ABCDEFG', 2)), list('AB'))
        self.assertEqual(list(islice('ABCDEFG', 2, 4)), list('CD'))
        self.assertEqual(list(islice('ABCDEFG', 2, Tupu)), list('CDEFG'))
        self.assertEqual(list(islice('ABCDEFG', 0, Tupu, 2)), list('ACEG'))

    eleza test_zip(self):
        self.assertEqual(list(zip('ABCD', 'xy')), [('A', 'x'), ('B', 'y')])

    eleza test_zip_longest(self):
        self.assertEqual(list(zip_longest('ABCD', 'xy', fillvalue='-')),
                         [('A', 'x'), ('B', 'y'), ('C', '-'), ('D', '-')])

    eleza test_permutations(self):
        self.assertEqual(list(permutations('ABCD', 2)),
                         list(map(tuple, 'AB AC AD BA BC BD CA CB CD DA DB DC'.split())))
        self.assertEqual(list(permutations(range(3))),
                         [(0,1,2), (0,2,1), (1,0,2), (1,2,0), (2,0,1), (2,1,0)])

    eleza test_product(self):
        self.assertEqual(list(product('ABCD', 'xy')),
                         list(map(tuple, 'Ax Ay Bx By Cx Cy Dx Dy'.split())))
        self.assertEqual(list(product(range(2), repeat=3)),
                        [(0,0,0), (0,0,1), (0,1,0), (0,1,1),
                         (1,0,0), (1,0,1), (1,1,0), (1,1,1)])

    eleza test_repeat(self):
        self.assertEqual(list(repeat(10, 3)), [10, 10, 10])

    eleza test_stapmap(self):
        self.assertEqual(list(starmap(pow, [(2,5), (3,2), (10,3)])),
                         [32, 9, 1000])

    eleza test_takewhile(self):
        self.assertEqual(list(takewhile(lambda x: x<5, [1,4,6,4,1])), [1,4])


kundi TestPurePythonRoughEquivalents(unittest.TestCase):

    @staticmethod
    eleza islice(iterable, *args):
        s = slice(*args)
        start, stop, step = s.start ama 0, s.stop ama sys.maxsize, s.step ama 1
        it = iter(range(start, stop, step))
        jaribu:
            nexti = next(it)
        tatizo StopIteration:
            # Consume *iterable* up to the *start* position.
            kila i, element kwenye zip(range(start), iterable):
                pita
            rudisha
        jaribu:
            kila i, element kwenye enumerate(iterable):
                ikiwa i == nexti:
                    tuma element
                    nexti = next(it)
        tatizo StopIteration:
            # Consume to *stop*.
            kila i, element kwenye zip(range(i + 1, stop), iterable):
                pita

    eleza test_islice_recipe(self):
        self.assertEqual(list(self.islice('ABCDEFG', 2)), list('AB'))
        self.assertEqual(list(self.islice('ABCDEFG', 2, 4)), list('CD'))
        self.assertEqual(list(self.islice('ABCDEFG', 2, Tupu)), list('CDEFG'))
        self.assertEqual(list(self.islice('ABCDEFG', 0, Tupu, 2)), list('ACEG'))
        # Test items consumed.
        it = iter(range(10))
        self.assertEqual(list(self.islice(it, 3)), list(range(3)))
        self.assertEqual(list(it), list(range(3, 10)))
        it = iter(range(10))
        self.assertEqual(list(self.islice(it, 3, 3)), [])
        self.assertEqual(list(it), list(range(3, 10)))
        # Test that slice finishes kwenye predictable state.
        c = count()
        self.assertEqual(list(self.islice(c, 1, 3, 50)), [1])
        self.assertEqual(next(c), 3)


kundi TestGC(unittest.TestCase):

    eleza makecycle(self, iterator, container):
        container.append(iterator)
        next(iterator)
        toa container, iterator

    eleza test_accumulate(self):
        a = []
        self.makecycle(accumulate([1,2,a,3]), a)

    eleza test_chain(self):
        a = []
        self.makecycle(chain(a), a)

    eleza test_chain_from_iterable(self):
        a = []
        self.makecycle(chain.kutoka_iterable([a]), a)

    eleza test_combinations(self):
        a = []
        self.makecycle(combinations([1,2,a,3], 3), a)

    eleza test_combinations_with_replacement(self):
        a = []
        self.makecycle(combinations_with_replacement([1,2,a,3], 3), a)

    eleza test_compress(self):
        a = []
        self.makecycle(compress('ABCDEF', [1,0,1,0,1,0]), a)

    eleza test_count(self):
        a = []
        Int = type('Int', (int,), dict(x=a))
        self.makecycle(count(Int(0), Int(1)), a)

    eleza test_cycle(self):
        a = []
        self.makecycle(cycle([a]*2), a)

    eleza test_dropwhile(self):
        a = []
        self.makecycle(dropwhile(bool, [0, a, a]), a)

    eleza test_groupby(self):
        a = []
        self.makecycle(groupby([a]*2, lambda x:x), a)

    eleza test_issue2246(self):
        # Issue 2246 -- the _grouper iterator was sio included kwenye GC
        n = 10
        keyfunc = lambda x: x
        kila i, j kwenye groupby(range(n), key=keyfunc):
            keyfunc.__dict__.setdefault('x',[]).append(j)

    eleza test_filter(self):
        a = []
        self.makecycle(filter(lambda x:Kweli, [a]*2), a)

    eleza test_filterfalse(self):
        a = []
        self.makecycle(filterfalse(lambda x:Uongo, a), a)

    eleza test_zip(self):
        a = []
        self.makecycle(zip([a]*2, [a]*3), a)

    eleza test_zip_longest(self):
        a = []
        self.makecycle(zip_longest([a]*2, [a]*3), a)
        b = [a, Tupu]
        self.makecycle(zip_longest([a]*2, [a]*3, fillvalue=b), a)

    eleza test_map(self):
        a = []
        self.makecycle(map(lambda x:x, [a]*2), a)

    eleza test_islice(self):
        a = []
        self.makecycle(islice([a]*2, Tupu), a)

    eleza test_permutations(self):
        a = []
        self.makecycle(permutations([1,2,a,3], 3), a)

    eleza test_product(self):
        a = []
        self.makecycle(product([1,2,a,3], repeat=3), a)

    eleza test_repeat(self):
        a = []
        self.makecycle(repeat(a), a)

    eleza test_starmap(self):
        a = []
        self.makecycle(starmap(lambda *t: t, [(a,a)]*2), a)

    eleza test_takewhile(self):
        a = []
        self.makecycle(takewhile(bool, [1, 0, a, a]), a)

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
        ikiwa self.i >= len(self.seqn): ashiria StopIteration
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
        ikiwa self.i >= len(self.seqn): ashiria StopIteration
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
        pita
    eleza __iter__(self):
        rudisha self
    eleza __next__(self):
        ashiria StopIteration

eleza L(seqn):
    'Test multiple tiers of iterators'
    rudisha chain(map(lambda x:x, R(Ig(G(seqn)))))


kundi TestVariousIteratorArgs(unittest.TestCase):

    eleza test_accumulate(self):
        s = [1,2,3,4,5]
        r = [1,3,6,10,15]
        n = len(s)
        kila g kwenye (G, I, Ig, L, R):
            self.assertEqual(list(accumulate(g(s))), r)
        self.assertEqual(list(accumulate(S(s))), [])
        self.assertRaises(TypeError, accumulate, X(s))
        self.assertRaises(TypeError, accumulate, N(s))
        self.assertRaises(ZeroDivisionError, list, accumulate(E(s)))

    eleza test_chain(self):
        kila s kwenye ("123", "", range(1000), ('do', 1.2), range(2000,2200,5)):
            kila g kwenye (G, I, Ig, S, L, R):
                self.assertEqual(list(chain(g(s))), list(g(s)))
                self.assertEqual(list(chain(g(s), g(s))), list(g(s))+list(g(s)))
            self.assertRaises(TypeError, list, chain(X(s)))
            self.assertRaises(TypeError, list, chain(N(s)))
            self.assertRaises(ZeroDivisionError, list, chain(E(s)))

    eleza test_compress(self):
        kila s kwenye ("123", "", range(1000), ('do', 1.2), range(2000,2200,5)):
            n = len(s)
            kila g kwenye (G, I, Ig, S, L, R):
                self.assertEqual(list(compress(g(s), repeat(1))), list(g(s)))
            self.assertRaises(TypeError, compress, X(s), repeat(1))
            self.assertRaises(TypeError, compress, N(s), repeat(1))
            self.assertRaises(ZeroDivisionError, list, compress(E(s), repeat(1)))

    eleza test_product(self):
        kila s kwenye ("123", "", range(1000), ('do', 1.2), range(2000,2200,5)):
            self.assertRaises(TypeError, product, X(s))
            self.assertRaises(TypeError, product, N(s))
            self.assertRaises(ZeroDivisionError, product, E(s))

    eleza test_cycle(self):
        kila s kwenye ("123", "", range(1000), ('do', 1.2), range(2000,2200,5)):
            kila g kwenye (G, I, Ig, S, L, R):
                tgtlen = len(s) * 3
                expected = list(g(s))*3
                actual = list(islice(cycle(g(s)), tgtlen))
                self.assertEqual(actual, expected)
            self.assertRaises(TypeError, cycle, X(s))
            self.assertRaises(TypeError, cycle, N(s))
            self.assertRaises(ZeroDivisionError, list, cycle(E(s)))

    eleza test_groupby(self):
        kila s kwenye (range(10), range(0), range(1000), (7,11), range(2000,2200,5)):
            kila g kwenye (G, I, Ig, S, L, R):
                self.assertEqual([k kila k, sb kwenye groupby(g(s))], list(g(s)))
            self.assertRaises(TypeError, groupby, X(s))
            self.assertRaises(TypeError, groupby, N(s))
            self.assertRaises(ZeroDivisionError, list, groupby(E(s)))

    eleza test_filter(self):
        kila s kwenye (range(10), range(0), range(1000), (7,11), range(2000,2200,5)):
            kila g kwenye (G, I, Ig, S, L, R):
                self.assertEqual(list(filter(isEven, g(s))),
                                 [x kila x kwenye g(s) ikiwa isEven(x)])
            self.assertRaises(TypeError, filter, isEven, X(s))
            self.assertRaises(TypeError, filter, isEven, N(s))
            self.assertRaises(ZeroDivisionError, list, filter(isEven, E(s)))

    eleza test_filterfalse(self):
        kila s kwenye (range(10), range(0), range(1000), (7,11), range(2000,2200,5)):
            kila g kwenye (G, I, Ig, S, L, R):
                self.assertEqual(list(filterfalse(isEven, g(s))),
                                 [x kila x kwenye g(s) ikiwa isOdd(x)])
            self.assertRaises(TypeError, filterfalse, isEven, X(s))
            self.assertRaises(TypeError, filterfalse, isEven, N(s))
            self.assertRaises(ZeroDivisionError, list, filterfalse(isEven, E(s)))

    eleza test_zip(self):
        kila s kwenye ("123", "", range(1000), ('do', 1.2), range(2000,2200,5)):
            kila g kwenye (G, I, Ig, S, L, R):
                self.assertEqual(list(zip(g(s))), lzip(g(s)))
                self.assertEqual(list(zip(g(s), g(s))), lzip(g(s), g(s)))
            self.assertRaises(TypeError, zip, X(s))
            self.assertRaises(TypeError, zip, N(s))
            self.assertRaises(ZeroDivisionError, list, zip(E(s)))

    eleza test_ziplongest(self):
        kila s kwenye ("123", "", range(1000), ('do', 1.2), range(2000,2200,5)):
            kila g kwenye (G, I, Ig, S, L, R):
                self.assertEqual(list(zip_longest(g(s))), list(zip(g(s))))
                self.assertEqual(list(zip_longest(g(s), g(s))), list(zip(g(s), g(s))))
            self.assertRaises(TypeError, zip_longest, X(s))
            self.assertRaises(TypeError, zip_longest, N(s))
            self.assertRaises(ZeroDivisionError, list, zip_longest(E(s)))

    eleza test_map(self):
        kila s kwenye (range(10), range(0), range(100), (7,11), range(20,50,5)):
            kila g kwenye (G, I, Ig, S, L, R):
                self.assertEqual(list(map(onearg, g(s))),
                                 [onearg(x) kila x kwenye g(s)])
                self.assertEqual(list(map(operator.pow, g(s), g(s))),
                                 [x**x kila x kwenye g(s)])
            self.assertRaises(TypeError, map, onearg, X(s))
            self.assertRaises(TypeError, map, onearg, N(s))
            self.assertRaises(ZeroDivisionError, list, map(onearg, E(s)))

    eleza test_islice(self):
        kila s kwenye ("12345", "", range(1000), ('do', 1.2), range(2000,2200,5)):
            kila g kwenye (G, I, Ig, S, L, R):
                self.assertEqual(list(islice(g(s),1,Tupu,2)), list(g(s))[1::2])
            self.assertRaises(TypeError, islice, X(s), 10)
            self.assertRaises(TypeError, islice, N(s), 10)
            self.assertRaises(ZeroDivisionError, list, islice(E(s), 10))

    eleza test_starmap(self):
        kila s kwenye (range(10), range(0), range(100), (7,11), range(20,50,5)):
            kila g kwenye (G, I, Ig, S, L, R):
                ss = lzip(s, s)
                self.assertEqual(list(starmap(operator.pow, g(ss))),
                                 [x**x kila x kwenye g(s)])
            self.assertRaises(TypeError, starmap, operator.pow, X(ss))
            self.assertRaises(TypeError, starmap, operator.pow, N(ss))
            self.assertRaises(ZeroDivisionError, list, starmap(operator.pow, E(ss)))

    eleza test_takewhile(self):
        kila s kwenye (range(10), range(0), range(1000), (7,11), range(2000,2200,5)):
            kila g kwenye (G, I, Ig, S, L, R):
                tgt = []
                kila elem kwenye g(s):
                    ikiwa sio isEven(elem): koma
                    tgt.append(elem)
                self.assertEqual(list(takewhile(isEven, g(s))), tgt)
            self.assertRaises(TypeError, takewhile, isEven, X(s))
            self.assertRaises(TypeError, takewhile, isEven, N(s))
            self.assertRaises(ZeroDivisionError, list, takewhile(isEven, E(s)))

    eleza test_dropwhile(self):
        kila s kwenye (range(10), range(0), range(1000), (7,11), range(2000,2200,5)):
            kila g kwenye (G, I, Ig, S, L, R):
                tgt = []
                kila elem kwenye g(s):
                    ikiwa sio tgt na isOdd(elem): endelea
                    tgt.append(elem)
                self.assertEqual(list(dropwhile(isOdd, g(s))), tgt)
            self.assertRaises(TypeError, dropwhile, isOdd, X(s))
            self.assertRaises(TypeError, dropwhile, isOdd, N(s))
            self.assertRaises(ZeroDivisionError, list, dropwhile(isOdd, E(s)))

    eleza test_tee(self):
        kila s kwenye ("123", "", range(1000), ('do', 1.2), range(2000,2200,5)):
            kila g kwenye (G, I, Ig, S, L, R):
                it1, it2 = tee(g(s))
                self.assertEqual(list(it1), list(g(s)))
                self.assertEqual(list(it2), list(g(s)))
            self.assertRaises(TypeError, tee, X(s))
            self.assertRaises(TypeError, tee, N(s))
            self.assertRaises(ZeroDivisionError, list, tee(E(s))[0])

kundi LengthTransparency(unittest.TestCase):

    eleza test_repeat(self):
        self.assertEqual(operator.length_hint(repeat(Tupu, 50)), 50)
        self.assertEqual(operator.length_hint(repeat(Tupu, 0)), 0)
        self.assertEqual(operator.length_hint(repeat(Tupu), 12), 12)

    eleza test_repeat_with_negative_times(self):
        self.assertEqual(operator.length_hint(repeat(Tupu, -1)), 0)
        self.assertEqual(operator.length_hint(repeat(Tupu, -2)), 0)
        self.assertEqual(operator.length_hint(repeat(Tupu, times=-1)), 0)
        self.assertEqual(operator.length_hint(repeat(Tupu, times=-2)), 0)

kundi RegressionTests(unittest.TestCase):

    eleza test_sf_793826(self):
        # Fix Armin Rigo's successful efforts to wreak havoc

        eleza mutatingtuple(tuple1, f, tuple2):
            # this builds a tuple t which ni a copy of tuple1,
            # then calls f(t), then mutates t to be equal to tuple2
            # (needs len(tuple1) == len(tuple2)).
            eleza g(value, first=[1]):
                ikiwa first:
                    toa first[:]
                    f(next(z))
                rudisha value
            items = list(tuple2)
            items[1:1] = list(tuple1)
            gen = map(g, items)
            z = zip(*[gen]*len(tuple1))
            next(z)

        eleza f(t):
            global T
            T = t
            first[:] = list(T)

        first = []
        mutatingtuple((1,2,3), f, (4,5,6))
        second = list(T)
        self.assertEqual(first, second)


    eleza test_sf_950057(self):
        # Make sure that chain() na cycle() catch exceptions immediately
        # rather than when shifting between input sources

        eleza gen1():
            hist.append(0)
            tuma 1
            hist.append(1)
            ashiria AssertionError
            hist.append(2)

        eleza gen2(x):
            hist.append(3)
            tuma 2
            hist.append(4)

        hist = []
        self.assertRaises(AssertionError, list, chain(gen1(), gen2(Uongo)))
        self.assertEqual(hist, [0,1])

        hist = []
        self.assertRaises(AssertionError, list, chain(gen1(), gen2(Kweli)))
        self.assertEqual(hist, [0,1])

        hist = []
        self.assertRaises(AssertionError, list, cycle(gen1()))
        self.assertEqual(hist, [0,1])

    @support.skip_if_pgo_task
    eleza test_long_chain_of_empty_iterables(self):
        # Make sure itertools.chain doesn't run into recursion limits when
        # dealing ukijumuisha long chains of empty iterables. Even ukijumuisha a high
        # number this would probably only fail kwenye Py_DEBUG mode.
        it = chain.kutoka_iterable(() kila unused kwenye range(10000000))
        ukijumuisha self.assertRaises(StopIteration):
            next(it)

    eleza test_issue30347_1(self):
        eleza f(n):
            ikiwa n == 5:
                list(b)
            rudisha n != 6
        kila (k, b) kwenye groupby(range(10), f):
            list(b)  # shouldn't crash

    eleza test_issue30347_2(self):
        kundi K:
            eleza __init__(self, v):
                pita
            eleza __eq__(self, other):
                nonlocal i
                i += 1
                ikiwa i == 1:
                    next(g, Tupu)
                rudisha Kweli
        i = 0
        g = next(groupby(range(10), K))[1]
        kila j kwenye range(2):
            next(g, Tupu)  # shouldn't crash


kundi SubclassWithKwargsTest(unittest.TestCase):
    eleza test_keywords_in_subclass(self):
        # count ni sio subclassable...
        kila cls kwenye (repeat, zip, filter, filterfalse, chain, map,
                    starmap, islice, takewhile, dropwhile, cycle, compress):
            kundi Subclass(cls):
                eleza __init__(self, newarg=Tupu, *args):
                    cls.__init__(self, *args)
            jaribu:
                Subclass(newarg=1)
            tatizo TypeError kama err:
                # we expect type errors because of wrong argument count
                self.assertNotIn("keyword arguments", err.args[0])

@support.cpython_only
kundi SizeofTest(unittest.TestCase):
    eleza setUp(self):
        self.ssize_t = struct.calcsize('n')

    check_sizeof = support.check_sizeof

    eleza test_product_sizeof(self):
        basesize = support.calcobjsize('3Pi')
        check = self.check_sizeof
        check(product('ab', '12'), basesize + 2 * self.ssize_t)
        check(product(*(('abc',) * 10)), basesize + 10 * self.ssize_t)

    eleza test_combinations_sizeof(self):
        basesize = support.calcobjsize('3Pni')
        check = self.check_sizeof
        check(combinations('abcd', 3), basesize + 3 * self.ssize_t)
        check(combinations(range(10), 4), basesize + 4 * self.ssize_t)

    eleza test_combinations_with_replacement_sizeof(self):
        cwr = combinations_with_replacement
        basesize = support.calcobjsize('3Pni')
        check = self.check_sizeof
        check(cwr('abcd', 3), basesize + 3 * self.ssize_t)
        check(cwr(range(10), 4), basesize + 4 * self.ssize_t)

    eleza test_permutations_sizeof(self):
        basesize = support.calcobjsize('4Pni')
        check = self.check_sizeof
        check(permutations('abcd'),
              basesize + 4 * self.ssize_t + 4 * self.ssize_t)
        check(permutations('abcd', 3),
              basesize + 4 * self.ssize_t + 3 * self.ssize_t)
        check(permutations('abcde', 3),
              basesize + 5 * self.ssize_t + 3 * self.ssize_t)
        check(permutations(range(10), 4),
              basesize + 10 * self.ssize_t + 4 * self.ssize_t)


libreftest = """ Doctest kila examples kwenye the library reference: libitertools.tex


>>> amounts = [120.15, 764.05, 823.14]
>>> kila checknum, amount kwenye zip(count(1200), amounts):
...     andika('Check %d ni kila $%.2f' % (checknum, amount))
...
Check 1200 ni kila $120.15
Check 1201 ni kila $764.05
Check 1202 ni kila $823.14

>>> agiza operator
>>> kila cube kwenye map(operator.pow, range(1,4), repeat(3)):
...    andika(cube)
...
1
8
27

>>> reportlines = ['EuroPython', 'Roster', '', 'alex', '', 'laura', '', 'martin', '', 'walter', '', 'samuele']
>>> kila name kwenye islice(reportlines, 3, Tupu, 2):
...    andika(name.title())
...
Alex
Laura
Martin
Walter
Samuele

>>> kutoka operator agiza itemgetter
>>> d = dict(a=1, b=2, c=1, d=2, e=1, f=2, g=3)
>>> di = sorted(sorted(d.items()), key=itemgetter(1))
>>> kila k, g kwenye groupby(di, itemgetter(1)):
...     andika(k, list(map(itemgetter(0), g)))
...
1 ['a', 'c', 'e']
2 ['b', 'd', 'f']
3 ['g']

# Find runs of consecutive numbers using groupby.  The key to the solution
# ni differencing ukijumuisha a range so that consecutive numbers all appear in
# same group.
>>> data = [ 1,  4,5,6, 10, 15,16,17,18, 22, 25,26,27,28]
>>> kila k, g kwenye groupby(enumerate(data), lambda t:t[0]-t[1]):
...     andika(list(map(operator.itemgetter(1), g)))
...
[1]
[4, 5, 6]
[10]
[15, 16, 17, 18]
[22]
[25, 26, 27, 28]

>>> eleza take(n, iterable):
...     "Return first n items of the iterable kama a list"
...     rudisha list(islice(iterable, n))

>>> eleza prepend(value, iterator):
...     "Prepend a single value kwenye front of an iterator"
...     # prepend(1, [2, 3, 4]) -> 1 2 3 4
...     rudisha chain([value], iterator)

>>> eleza enumerate(iterable, start=0):
...     rudisha zip(count(start), iterable)

>>> eleza tabulate(function, start=0):
...     "Return function(0), function(1), ..."
...     rudisha map(function, count(start))

>>> agiza collections
>>> eleza consume(iterator, n=Tupu):
...     "Advance the iterator n-steps ahead. If n ni Tupu, consume entirely."
...     # Use functions that consume iterators at C speed.
...     ikiwa n ni Tupu:
...         # feed the entire iterator into a zero-length deque
...         collections.deque(iterator, maxlen=0)
...     isipokua:
...         # advance to the empty slice starting at position n
...         next(islice(iterator, n, n), Tupu)

>>> eleza nth(iterable, n, default=Tupu):
...     "Returns the nth item ama a default value"
...     rudisha next(islice(iterable, n, Tupu), default)

>>> eleza all_equal(iterable):
...     "Returns Kweli ikiwa all the elements are equal to each other"
...     g = groupby(iterable)
...     rudisha next(g, Kweli) na sio next(g, Uongo)

>>> eleza quantify(iterable, pred=bool):
...     "Count how many times the predicate ni true"
...     rudisha sum(map(pred, iterable))

>>> eleza padnone(iterable):
...     "Returns the sequence elements na then rudishas Tupu indefinitely"
...     rudisha chain(iterable, repeat(Tupu))

>>> eleza ncycles(iterable, n):
...     "Returns the sequence elements n times"
...     rudisha chain(*repeat(iterable, n))

>>> eleza dotproduct(vec1, vec2):
...     rudisha sum(map(operator.mul, vec1, vec2))

>>> eleza flatten(listOfLists):
...     rudisha list(chain.kutoka_iterable(listOfLists))

>>> eleza repeatfunc(func, times=Tupu, *args):
...     "Repeat calls to func ukijumuisha specified arguments."
...     "   Example:  repeatfunc(random.random)"
...     ikiwa times ni Tupu:
...         rudisha starmap(func, repeat(args))
...     isipokua:
...         rudisha starmap(func, repeat(args, times))

>>> eleza pairwise(iterable):
...     "s -> (s0,s1), (s1,s2), (s2, s3), ..."
...     a, b = tee(iterable)
...     jaribu:
...         next(b)
...     tatizo StopIteration:
...         pita
...     rudisha zip(a, b)

>>> eleza grouper(n, iterable, fillvalue=Tupu):
...     "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
...     args = [iter(iterable)] * n
...     rudisha zip_longest(*args, fillvalue=fillvalue)

>>> eleza roundrobin(*iterables):
...     "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
...     # Recipe credited to George Sakkis
...     pending = len(iterables)
...     nexts = cycle(iter(it).__next__ kila it kwenye iterables)
...     wakati pending:
...         jaribu:
...             kila next kwenye nexts:
...                 tuma next()
...         tatizo StopIteration:
...             pending -= 1
...             nexts = cycle(islice(nexts, pending))

>>> eleza powerset(iterable):
...     "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
...     s = list(iterable)
...     rudisha chain.kutoka_iterable(combinations(s, r) kila r kwenye range(len(s)+1))

>>> eleza unique_everseen(iterable, key=Tupu):
...     "List unique elements, preserving order. Remember all elements ever seen."
...     # unique_everseen('AAAABBBCCDAABBB') --> A B C D
...     # unique_everseen('ABBCcAD', str.lower) --> A B C D
...     seen = set()
...     seen_add = seen.add
...     ikiwa key ni Tupu:
...         kila element kwenye iterable:
...             ikiwa element haiko kwenye seen:
...                 seen_add(element)
...                 tuma element
...     isipokua:
...         kila element kwenye iterable:
...             k = key(element)
...             ikiwa k haiko kwenye seen:
...                 seen_add(k)
...                 tuma element

>>> eleza unique_justseen(iterable, key=Tupu):
...     "List unique elements, preserving order. Remember only the element just seen."
...     # unique_justseen('AAAABBBCCDAABBB') --> A B C D A B
...     # unique_justseen('ABBCcAD', str.lower) --> A B C A D
...     rudisha map(next, map(itemgetter(1), groupby(iterable, key)))

>>> eleza first_true(iterable, default=Uongo, pred=Tupu):
...     '''Returns the first true value kwenye the iterable.
...
...     If no true value ni found, rudishas *default*
...
...     If *pred* ni sio Tupu, rudishas the first item
...     kila which pred(item) ni true.
...
...     '''
...     # first_true([a,b,c], x) --> a ama b ama c ama x
...     # first_true([a,b], x, f) --> a ikiwa f(a) isipokua b ikiwa f(b) isipokua x
...     rudisha next(filter(pred, iterable), default)

>>> eleza nth_combination(iterable, r, index):
...     'Equivalent to list(combinations(iterable, r))[index]'
...     pool = tuple(iterable)
...     n = len(pool)
...     ikiwa r < 0 ama r > n:
...         ashiria ValueError
...     c = 1
...     k = min(r, n-r)
...     kila i kwenye range(1, k+1):
...         c = c * (n - k + i) // i
...     ikiwa index < 0:
...         index += c
...     ikiwa index < 0 ama index >= c:
...         ashiria IndexError
...     result = []
...     wakati r:
...         c, n, r = c*r//n, n-1, r-1
...         wakati index >= c:
...             index -= c
...             c, n = c*(n-r)//n, n-1
...         result.append(pool[-1-n])
...     rudisha tuple(result)


This ni sio part of the examples but it tests to make sure the definitions
perform kama purported.

>>> take(10, count())
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

>>> list(prepend(1, [2, 3, 4]))
[1, 2, 3, 4]

>>> list(enumerate('abc'))
[(0, 'a'), (1, 'b'), (2, 'c')]

>>> list(islice(tabulate(lambda x: 2*x), 4))
[0, 2, 4, 6]

>>> it = iter(range(10))
>>> consume(it, 3)
>>> next(it)
3
>>> consume(it)
>>> next(it, 'Done')
'Done'

>>> nth('abcde', 3)
'd'

>>> nth('abcde', 9) ni Tupu
Kweli

>>> [all_equal(s) kila s kwenye ('', 'A', 'AAAA', 'AAAB', 'AAABA')]
[Kweli, Kweli, Kweli, Uongo, Uongo]

>>> quantify(range(99), lambda x: x%2==0)
50

>>> a = [[1, 2, 3], [4, 5, 6]]
>>> flatten(a)
[1, 2, 3, 4, 5, 6]

>>> list(repeatfunc(pow, 5, 2, 3))
[8, 8, 8, 8, 8]

>>> agiza random
>>> take(5, map(int, repeatfunc(random.random)))
[0, 0, 0, 0, 0]

>>> list(pairwise('abcd'))
[('a', 'b'), ('b', 'c'), ('c', 'd')]

>>> list(pairwise([]))
[]

>>> list(pairwise('a'))
[]

>>> list(islice(padnone('abc'), 0, 6))
['a', 'b', 'c', Tupu, Tupu, Tupu]

>>> list(ncycles('abc', 3))
['a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c']

>>> dotproduct([1,2,3], [4,5,6])
32

>>> list(grouper(3, 'abcdefg', 'x'))
[('a', 'b', 'c'), ('d', 'e', 'f'), ('g', 'x', 'x')]

>>> list(roundrobin('abc', 'd', 'ef'))
['a', 'd', 'e', 'b', 'f', 'c']

>>> list(powerset([1,2,3]))
[(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]

>>> all(len(list(powerset(range(n)))) == 2**n kila n kwenye range(18))
Kweli

>>> list(powerset('abcde')) == sorted(sorted(set(powerset('abcde'))), key=len)
Kweli

>>> list(unique_everseen('AAAABBBCCDAABBB'))
['A', 'B', 'C', 'D']

>>> list(unique_everseen('ABBCcAD', str.lower))
['A', 'B', 'C', 'D']

>>> list(unique_justseen('AAAABBBCCDAABBB'))
['A', 'B', 'C', 'D', 'A', 'B']

>>> list(unique_justseen('ABBCcAD', str.lower))
['A', 'B', 'C', 'A', 'D']

>>> first_true('ABC0DEF1', '9', str.isdigit)
'0'

>>> population = 'ABCDEFGH'
>>> kila r kwenye range(len(population) + 1):
...     seq = list(combinations(population, r))
...     kila i kwenye range(len(seq)):
...         assert nth_combination(population, r, i) == seq[i]
...     kila i kwenye range(-len(seq), 0):
...         assert nth_combination(population, r, i) == seq[i]


"""

__test__ = {'libreftest' : libreftest}

eleza test_main(verbose=Tupu):
    test_classes = (TestBasicOps, TestVariousIteratorArgs, TestGC,
                    RegressionTests, LengthTransparency,
                    SubclassWithKwargsTest, TestExamples,
                    TestPurePythonRoughEquivalents,
                    SizeofTest)
    support.run_unittest(*test_classes)

    # verify reference counting
    ikiwa verbose na hasattr(sys, "gettotalrefcount"):
        agiza gc
        counts = [Tupu] * 5
        kila i kwenye range(len(counts)):
            support.run_unittest(*test_classes)
            gc.collect()
            counts[i] = sys.gettotalrefcount()
        andika(counts)

    # doctest the examples kwenye the library reference
    support.run_doctest(sys.modules[__name__], verbose)

ikiwa __name__ == "__main__":
    test_main(verbose=Kweli)
