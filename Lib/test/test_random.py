agiza unittest
agiza unittest.mock
agiza random
agiza os
agiza time
agiza pickle
agiza warnings
kutoka functools agiza partial
kutoka math agiza log, exp, pi, fsum, sin, factorial
kutoka test agiza support
kutoka fractions agiza Fraction


kundi TestBasicOps:
    # Superkundi with tests common to all generators.
    # Subclasses must arrange kila self.gen to retrieve the Random instance
    # to be tested.

    eleza randomlist(self, n):
        """Helper function to make a list of random numbers"""
        rudisha [self.gen.random() kila i kwenye range(n)]

    eleza test_autoseed(self):
        self.gen.seed()
        state1 = self.gen.getstate()
        time.sleep(0.1)
        self.gen.seed()      # different seeds at different times
        state2 = self.gen.getstate()
        self.assertNotEqual(state1, state2)

    eleza test_saverestore(self):
        N = 1000
        self.gen.seed()
        state = self.gen.getstate()
        randseq = self.randomlist(N)
        self.gen.setstate(state)    # should regenerate the same sequence
        self.assertEqual(randseq, self.randomlist(N))

    eleza test_seedargs(self):
        # Seed value with a negative hash.
        kundi MySeed(object):
            eleza __hash__(self):
                rudisha -1729
        kila arg kwenye [Tupu, 0, 0, 1, 1, -1, -1, 10**20, -(10**20),
                    3.14, 1+2j, 'a', tuple('abc'), MySeed()]:
            self.gen.seed(arg)
        kila arg kwenye [list(range(3)), dict(one=1)]:
            self.assertRaises(TypeError, self.gen.seed, arg)
        self.assertRaises(TypeError, self.gen.seed, 1, 2, 3, 4)
        self.assertRaises(TypeError, type(self.gen), [])

    @unittest.mock.patch('random._urandom') # os.urandom
    eleza test_seed_when_randomness_source_not_found(self, urandom_mock):
        # Random.seed() uses time.time() when an operating system specific
        # randomness source ni sio found. To test this on machines where it
        # exists, run the above test, test_seedargs(), again after mocking
        # os.urandom() so that it ashirias the exception expected when the
        # randomness source ni sio available.
        urandom_mock.side_effect = NotImplementedError
        self.test_seedargs()

    eleza test_shuffle(self):
        shuffle = self.gen.shuffle
        lst = []
        shuffle(lst)
        self.assertEqual(lst, [])
        lst = [37]
        shuffle(lst)
        self.assertEqual(lst, [37])
        seqs = [list(range(n)) kila n kwenye range(10)]
        shuffled_seqs = [list(range(n)) kila n kwenye range(10)]
        kila shuffled_seq kwenye shuffled_seqs:
            shuffle(shuffled_seq)
        kila (seq, shuffled_seq) kwenye zip(seqs, shuffled_seqs):
            self.assertEqual(len(seq), len(shuffled_seq))
            self.assertEqual(set(seq), set(shuffled_seq))
        # The above tests all would pita ikiwa the shuffle was a
        # no-op. The following non-deterministic test covers that.  It
        # asserts that the shuffled sequence of 1000 distinct elements
        # must be different kutoka the original one. Although there is
        # mathematically a non-zero probability that this could
        # actually happen kwenye a genuinely random shuffle, it is
        # completely negligible, given that the number of possible
        # permutations of 1000 objects ni 1000! (factorial of 1000),
        # which ni considerably larger than the number of atoms kwenye the
        # universe...
        lst = list(range(1000))
        shuffled_lst = list(range(1000))
        shuffle(shuffled_lst)
        self.assertKweli(lst != shuffled_lst)
        shuffle(lst)
        self.assertKweli(lst != shuffled_lst)
        self.assertRaises(TypeError, shuffle, (1, 2, 3))

    eleza test_shuffle_random_argument(self):
        # Test random argument to shuffle.
        shuffle = self.gen.shuffle
        mock_random = unittest.mock.Mock(rudisha_value=0.5)
        seq = bytearray(b'abcdefghijk')
        shuffle(seq, mock_random)
        mock_random.assert_called_with()

    eleza test_choice(self):
        choice = self.gen.choice
        with self.assertRaises(IndexError):
            choice([])
        self.assertEqual(choice([50]), 50)
        self.assertIn(choice([25, 75]), [25, 75])

    eleza test_sample(self):
        # For the entire allowable range of 0 <= k <= N, validate that
        # the sample ni of the correct length na contains only unique items
        N = 100
        population = range(N)
        kila k kwenye range(N+1):
            s = self.gen.sample(population, k)
            self.assertEqual(len(s), k)
            uniq = set(s)
            self.assertEqual(len(uniq), k)
            self.assertKweli(uniq <= set(population))
        self.assertEqual(self.gen.sample([], 0), [])  # test edge case N==k==0
        # Exception ashiriad ikiwa size of sample exceeds that of population
        self.assertRaises(ValueError, self.gen.sample, population, N+1)
        self.assertRaises(ValueError, self.gen.sample, [], -1)

    eleza test_sample_distribution(self):
        # For the entire allowable range of 0 <= k <= N, validate that
        # sample generates all possible permutations
        n = 5
        pop = range(n)
        trials = 10000  # large num prevents false negatives without slowing normal case
        kila k kwenye range(n):
            expected = factorial(n) // factorial(n-k)
            perms = {}
            kila i kwenye range(trials):
                perms[tuple(self.gen.sample(pop, k))] = Tupu
                ikiwa len(perms) == expected:
                    koma
            isipokua:
                self.fail()

    eleza test_sample_inputs(self):
        # SF bug #801342 -- population can be any iterable defining __len__()
        self.gen.sample(set(range(20)), 2)
        self.gen.sample(range(20), 2)
        self.gen.sample(range(20), 2)
        self.gen.sample(str('abcdefghijklmnopqrst'), 2)
        self.gen.sample(tuple('abcdefghijklmnopqrst'), 2)

    eleza test_sample_on_dicts(self):
        self.assertRaises(TypeError, self.gen.sample, dict.kutokakeys('abcdef'), 2)

    eleza test_choices(self):
        choices = self.gen.choices
        data = ['red', 'green', 'blue', 'yellow']
        str_data = 'abcd'
        range_data = range(4)
        set_data = set(range(4))

        # basic functionality
        kila sample kwenye [
            choices(data, k=5),
            choices(data, range(4), k=5),
            choices(k=5, population=data, weights=range(4)),
            choices(k=5, population=data, cum_weights=range(4)),
        ]:
            self.assertEqual(len(sample), 5)
            self.assertEqual(type(sample), list)
            self.assertKweli(set(sample) <= set(data))

        # test argument handling
        with self.assertRaises(TypeError):                               # missing arguments
            choices(2)

        self.assertEqual(choices(data, k=0), [])                         # k == 0
        self.assertEqual(choices(data, k=-1), [])                        # negative k behaves like ``[0] * -1``
        with self.assertRaises(TypeError):
            choices(data, k=2.5)                                         # k ni a float

        self.assertKweli(set(choices(str_data, k=5)) <= set(str_data))    # population ni a string sequence
        self.assertKweli(set(choices(range_data, k=5)) <= set(range_data))  # population ni a range
        with self.assertRaises(TypeError):
            choices(set_data, k=2)                                       # population ni sio a sequence

        self.assertKweli(set(choices(data, Tupu, k=5)) <= set(data))      # weights ni Tupu
        self.assertKweli(set(choices(data, weights=Tupu, k=5)) <= set(data))
        with self.assertRaises(ValueError):
            choices(data, [1,2], k=5)                                    # len(weights) != len(population)
        with self.assertRaises(TypeError):
            choices(data, 10, k=5)                                       # non-iterable weights
        with self.assertRaises(TypeError):
            choices(data, [Tupu]*4, k=5)                                 # non-numeric weights
        kila weights kwenye [
                [15, 10, 25, 30],                                                 # integer weights
                [15.1, 10.2, 25.2, 30.3],                                         # float weights
                [Fraction(1, 3), Fraction(2, 6), Fraction(3, 6), Fraction(4, 6)], # fractional weights
                [Kweli, Uongo, Kweli, Uongo]                                        # booleans (include / exclude)
        ]:
            self.assertKweli(set(choices(data, weights, k=5)) <= set(data))

        with self.assertRaises(ValueError):
            choices(data, cum_weights=[1,2], k=5)                        # len(weights) != len(population)
        with self.assertRaises(TypeError):
            choices(data, cum_weights=10, k=5)                           # non-iterable cum_weights
        with self.assertRaises(TypeError):
            choices(data, cum_weights=[Tupu]*4, k=5)                     # non-numeric cum_weights
        with self.assertRaises(TypeError):
            choices(data, range(4), cum_weights=range(4), k=5)           # both weights na cum_weights
        kila weights kwenye [
                [15, 10, 25, 30],                                                 # integer cum_weights
                [15.1, 10.2, 25.2, 30.3],                                         # float cum_weights
                [Fraction(1, 3), Fraction(2, 6), Fraction(3, 6), Fraction(4, 6)], # fractional cum_weights
        ]:
            self.assertKweli(set(choices(data, cum_weights=weights, k=5)) <= set(data))

        # Test weight focused on a single element of the population
        self.assertEqual(choices('abcd', [1, 0, 0, 0]), ['a'])
        self.assertEqual(choices('abcd', [0, 1, 0, 0]), ['b'])
        self.assertEqual(choices('abcd', [0, 0, 1, 0]), ['c'])
        self.assertEqual(choices('abcd', [0, 0, 0, 1]), ['d'])

        # Test consistency with random.choice() kila empty population
        with self.assertRaises(IndexError):
            choices([], k=1)
        with self.assertRaises(IndexError):
            choices([], weights=[], k=1)
        with self.assertRaises(IndexError):
            choices([], cum_weights=[], k=5)

    eleza test_choices_subnormal(self):
        # Subnormal weights would occasionally trigger an IndexError
        # kwenye choices() when the value rudishaed by random() was large
        # enough to make `random() * total` round up to the total.
        # See https://bugs.python.org/msg275594 kila more detail.
        choices = self.gen.choices
        choices(population=[1, 2], weights=[1e-323, 1e-323], k=5000)

    eleza test_gauss(self):
        # Ensure that the seed() method initializes all the hidden state.  In
        # particular, through 2.2.1 it failed to reset a piece of state used
        # by (and only by) the .gauss() method.

        kila seed kwenye 1, 12, 123, 1234, 12345, 123456, 654321:
            self.gen.seed(seed)
            x1 = self.gen.random()
            y1 = self.gen.gauss(0, 1)

            self.gen.seed(seed)
            x2 = self.gen.random()
            y2 = self.gen.gauss(0, 1)

            self.assertEqual(x1, x2)
            self.assertEqual(y1, y2)

    eleza test_pickling(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            state = pickle.dumps(self.gen, proto)
            origseq = [self.gen.random() kila i kwenye range(10)]
            newgen = pickle.loads(state)
            restoredseq = [newgen.random() kila i kwenye range(10)]
            self.assertEqual(origseq, restoredseq)

    eleza test_bug_1727780(self):
        # verify that version-2-pickles can be loaded
        # fine, whether they are created on 32-bit ama 64-bit
        # platforms, na that version-3-pickles load fine.
        files = [("randv2_32.pck", 780),
                 ("randv2_64.pck", 866),
                 ("randv3.pck", 343)]
        kila file, value kwenye files:
            with open(support.findfile(file),"rb") kama f:
                r = pickle.load(f)
            self.assertEqual(int(r.random()*1000), value)

    eleza test_bug_9025(self):
        # Had problem with an uneven distribution kwenye int(n*random())
        # Verify the fix by checking that distributions fall within expectations.
        n = 100000
        randrange = self.gen.randrange
        k = sum(randrange(6755399441055744) % 3 == 2 kila i kwenye range(n))
        self.assertKweli(0.30 < k/n < .37, (k/n))

jaribu:
    random.SystemRandom().random()
tatizo NotImplementedError:
    SystemRandom_available = Uongo
isipokua:
    SystemRandom_available = Kweli

@unittest.skipUnless(SystemRandom_available, "random.SystemRandom sio available")
kundi SystemRandom_TestBasicOps(TestBasicOps, unittest.TestCase):
    gen = random.SystemRandom()

    eleza test_autoseed(self):
        # Doesn't need to do anything tatizo sio fail
        self.gen.seed()

    eleza test_saverestore(self):
        self.assertRaises(NotImplementedError, self.gen.getstate)
        self.assertRaises(NotImplementedError, self.gen.setstate, Tupu)

    eleza test_seedargs(self):
        # Doesn't need to do anything tatizo sio fail
        self.gen.seed(100)

    eleza test_gauss(self):
        self.gen.gauss_next = Tupu
        self.gen.seed(100)
        self.assertEqual(self.gen.gauss_next, Tupu)

    eleza test_pickling(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            self.assertRaises(NotImplementedError, pickle.dumps, self.gen, proto)

    eleza test_53_bits_per_float(self):
        # This should pita whenever a C double has 53 bit precision.
        span = 2 ** 53
        cum = 0
        kila i kwenye range(100):
            cum |= int(self.gen.random() * span)
        self.assertEqual(cum, span-1)

    eleza test_bigrand(self):
        # The randrange routine should build-up the required number of bits
        # kwenye stages so that all bit positions are active.
        span = 2 ** 500
        cum = 0
        kila i kwenye range(100):
            r = self.gen.randrange(span)
            self.assertKweli(0 <= r < span)
            cum |= r
        self.assertEqual(cum, span-1)

    eleza test_bigrand_ranges(self):
        kila i kwenye [40,80, 160, 200, 211, 250, 375, 512, 550]:
            start = self.gen.randrange(2 ** (i-2))
            stop = self.gen.randrange(2 ** i)
            ikiwa stop <= start:
                endelea
            self.assertKweli(start <= self.gen.randrange(start, stop) < stop)

    eleza test_rangelimits(self):
        kila start, stop kwenye [(-2,0), (-(2**60)-2,-(2**60)), (2**60,2**60+2)]:
            self.assertEqual(set(range(start,stop)),
                set([self.gen.randrange(start,stop) kila i kwenye range(100)]))

    eleza test_randrange_nonunit_step(self):
        rint = self.gen.randrange(0, 10, 2)
        self.assertIn(rint, (0, 2, 4, 6, 8))
        rint = self.gen.randrange(0, 2, 2)
        self.assertEqual(rint, 0)

    eleza test_randrange_errors(self):
        ashirias = partial(self.assertRaises, ValueError, self.gen.randrange)
        # Empty range
        ashirias(3, 3)
        ashirias(-721)
        ashirias(0, 100, -12)
        # Non-integer start/stop
        ashirias(3.14159)
        ashirias(0, 2.71828)
        # Zero na non-integer step
        ashirias(0, 42, 0)
        ashirias(0, 42, 3.14159)

    eleza test_genrandbits(self):
        # Verify ranges
        kila k kwenye range(1, 1000):
            self.assertKweli(0 <= self.gen.getrandbits(k) < 2**k)

        # Verify all bits active
        getbits = self.gen.getrandbits
        kila span kwenye [1, 2, 3, 4, 31, 32, 32, 52, 53, 54, 119, 127, 128, 129]:
            cum = 0
            kila i kwenye range(100):
                cum |= getbits(span)
            self.assertEqual(cum, 2**span-1)

        # Verify argument checking
        self.assertRaises(TypeError, self.gen.getrandbits)
        self.assertRaises(TypeError, self.gen.getrandbits, 1, 2)
        self.assertRaises(ValueError, self.gen.getrandbits, 0)
        self.assertRaises(ValueError, self.gen.getrandbits, -1)
        self.assertRaises(TypeError, self.gen.getrandbits, 10.1)

    eleza test_randbelow_logic(self, _log=log, int=int):
        # check bitcount transition points:  2**i na 2**(i+1)-1
        # show that: k = int(1.001 + _log(n, 2))
        # ni equal to ama one greater than the number of bits kwenye n
        kila i kwenye range(1, 1000):
            n = 1 << i # check an exact power of two
            numbits = i+1
            k = int(1.00001 + _log(n, 2))
            self.assertEqual(k, numbits)
            self.assertEqual(n, 2**(k-1))

            n += n - 1      # check 1 below the next power of two
            k = int(1.00001 + _log(n, 2))
            self.assertIn(k, [numbits, numbits+1])
            self.assertKweli(2**k > n > 2**(k-2))

            n -= n >> 15     # check a little farther below the next power of two
            k = int(1.00001 + _log(n, 2))
            self.assertEqual(k, numbits)        # note the stronger assertion
            self.assertKweli(2**k > n > 2**(k-1))   # note the stronger assertion


kundi MersenneTwister_TestBasicOps(TestBasicOps, unittest.TestCase):
    gen = random.Random()

    eleza test_guaranteed_stable(self):
        # These sequences are guaranteed to stay the same across versions of python
        self.gen.seed(3456147, version=1)
        self.assertEqual([self.gen.random().hex() kila i kwenye range(4)],
            ['0x1.ac362300d90d2p-1', '0x1.9d16f74365005p-1',
             '0x1.1ebb4352e4c4dp-1', '0x1.1a7422abf9c11p-1'])
        self.gen.seed("the quick brown fox", version=2)
        self.assertEqual([self.gen.random().hex() kila i kwenye range(4)],
            ['0x1.1239ddfb11b7cp-3', '0x1.b3cbb5c51b120p-4',
             '0x1.8c4f55116b60fp-1', '0x1.63eb525174a27p-1'])

    eleza test_bug_27706(self):
        # Verify that version 1 seeds are unaffected by hash randomization

        self.gen.seed('nofar', version=1)   # hash('nofar') == 5990528763808513177
        self.assertEqual([self.gen.random().hex() kila i kwenye range(4)],
            ['0x1.8645314505ad7p-1', '0x1.afb1f82e40a40p-5',
             '0x1.2a59d2285e971p-1', '0x1.56977142a7880p-6'])

        self.gen.seed('rachel', version=1)  # hash('rachel') == -9091735575445484789
        self.assertEqual([self.gen.random().hex() kila i kwenye range(4)],
            ['0x1.0b294cc856fcdp-1', '0x1.2ad22d79e77b8p-3',
             '0x1.3052b9c072678p-2', '0x1.578f332106574p-3'])

        self.gen.seed('', version=1)        # hash('') == 0
        self.assertEqual([self.gen.random().hex() kila i kwenye range(4)],
            ['0x1.b0580f98a7dbep-1', '0x1.84129978f9c1ap-1',
             '0x1.aeaa51052e978p-2', '0x1.092178fb945a6p-2'])

    eleza test_bug_31478(self):
        # There shouldn't be an assertion failure kwenye _random.Random.seed() in
        # case the argument has a bad __abs__() method.
        kundi BadInt(int):
            eleza __abs__(self):
                rudisha Tupu
        jaribu:
            self.gen.seed(BadInt())
        tatizo TypeError:
            pita

    eleza test_bug_31482(self):
        # Verify that version 1 seeds are unaffected by hash randomization
        # when the seeds are expressed kama bytes rather than strings.
        # The hash(b) values listed are the Python2.7 hash() values
        # which were used kila seeding.

        self.gen.seed(b'nofar', version=1)   # hash('nofar') == 5990528763808513177
        self.assertEqual([self.gen.random().hex() kila i kwenye range(4)],
            ['0x1.8645314505ad7p-1', '0x1.afb1f82e40a40p-5',
             '0x1.2a59d2285e971p-1', '0x1.56977142a7880p-6'])

        self.gen.seed(b'rachel', version=1)  # hash('rachel') == -9091735575445484789
        self.assertEqual([self.gen.random().hex() kila i kwenye range(4)],
            ['0x1.0b294cc856fcdp-1', '0x1.2ad22d79e77b8p-3',
             '0x1.3052b9c072678p-2', '0x1.578f332106574p-3'])

        self.gen.seed(b'', version=1)        # hash('') == 0
        self.assertEqual([self.gen.random().hex() kila i kwenye range(4)],
            ['0x1.b0580f98a7dbep-1', '0x1.84129978f9c1ap-1',
             '0x1.aeaa51052e978p-2', '0x1.092178fb945a6p-2'])

        b = b'\x00\x20\x40\x60\x80\xA0\xC0\xE0\xF0'
        self.gen.seed(b, version=1)         # hash(b) == 5015594239749365497
        self.assertEqual([self.gen.random().hex() kila i kwenye range(4)],
            ['0x1.52c2fde444d23p-1', '0x1.875174f0daea4p-2',
             '0x1.9e9b2c50e5cd2p-1', '0x1.fa57768bd321cp-2'])

    eleza test_setstate_first_arg(self):
        self.assertRaises(ValueError, self.gen.setstate, (1, Tupu, Tupu))

    eleza test_setstate_middle_arg(self):
        start_state = self.gen.getstate()
        # Wrong type, s/b tuple
        self.assertRaises(TypeError, self.gen.setstate, (2, Tupu, Tupu))
        # Wrong length, s/b 625
        self.assertRaises(ValueError, self.gen.setstate, (2, (1,2,3), Tupu))
        # Wrong type, s/b tuple of 625 ints
        self.assertRaises(TypeError, self.gen.setstate, (2, ('a',)*625, Tupu))
        # Last element s/b an int also
        self.assertRaises(TypeError, self.gen.setstate, (2, (0,)*624+('a',), Tupu))
        # Last element s/b between 0 na 624
        with self.assertRaises((ValueError, OverflowError)):
            self.gen.setstate((2, (1,)*624+(625,), Tupu))
        with self.assertRaises((ValueError, OverflowError)):
            self.gen.setstate((2, (1,)*624+(-1,), Tupu))
        # Failed calls to setstate() should sio have changed the state.
        bits100 = self.gen.getrandbits(100)
        self.gen.setstate(start_state)
        self.assertEqual(self.gen.getrandbits(100), bits100)

        # Little trick to make "tuple(x % (2**32) kila x kwenye internalstate)"
        # ashiria ValueError. I cannot think of a simple way to achieve this, so
        # I am opting kila using a generator kama the middle argument of setstate
        # which attempts to cast a NaN to integer.
        state_values = self.gen.getstate()[1]
        state_values = list(state_values)
        state_values[-1] = float('nan')
        state = (int(x) kila x kwenye state_values)
        self.assertRaises(TypeError, self.gen.setstate, (2, state, Tupu))

    eleza test_referenceImplementation(self):
        # Compare the python implementation with results kutoka the original
        # code.  Create 2000 53-bit precision random floats.  Compare only
        # the last ten entries to show that the independent implementations
        # are tracking.  Here ni the main() function needed to create the
        # list of expected random numbers:
        #    void main(void){
        #         int i;
        #         unsigned long init[4]={61731, 24903, 614, 42143}, length=4;
        #         init_by_array(init, length);
        #         kila (i=0; i<2000; i++) {
        #           printf("%.15f ", genrand_res53());
        #           ikiwa (i%5==4) printf("\n");
        #         }
        #     }
        expected = [0.45839803073713259,
                    0.86057815201978782,
                    0.92848331726782152,
                    0.35932681119782461,
                    0.081823493762449573,
                    0.14332226470169329,
                    0.084297823823520024,
                    0.53814864671831453,
                    0.089215024911993401,
                    0.78486196105372907]

        self.gen.seed(61731 + (24903<<32) + (614<<64) + (42143<<96))
        actual = self.randomlist(2000)[-10:]
        kila a, e kwenye zip(actual, expected):
            self.assertAlmostEqual(a,e,places=14)

    eleza test_strong_reference_implementation(self):
        # Like test_referenceImplementation, but checks kila exact bit-level
        # equality.  This should pita on any box where C double contains
        # at least 53 bits of precision (the underlying algorithm suffers
        # no rounding errors -- all results are exact).
        kutoka math agiza ldexp

        expected = [0x0eab3258d2231f,
                    0x1b89db315277a5,
                    0x1db622a5518016,
                    0x0b7f9af0d575bf,
                    0x029e4c4db82240,
                    0x04961892f5d673,
                    0x02b291598e4589,
                    0x11388382c15694,
                    0x02dad977c9e1fe,
                    0x191d96d4d334c6]
        self.gen.seed(61731 + (24903<<32) + (614<<64) + (42143<<96))
        actual = self.randomlist(2000)[-10:]
        kila a, e kwenye zip(actual, expected):
            self.assertEqual(int(ldexp(a, 53)), e)

    eleza test_long_seed(self):
        # This ni most interesting to run kwenye debug mode, just to make sure
        # nothing blows up.  Under the covers, a dynamically resized array
        # ni allocated, consuming space proportional to the number of bits
        # kwenye the seed.  Unfortunately, that's a quadratic-time algorithm,
        # so don't make this horribly big.
        seed = (1 << (10000 * 8)) - 1  # about 10K bytes
        self.gen.seed(seed)

    eleza test_53_bits_per_float(self):
        # This should pita whenever a C double has 53 bit precision.
        span = 2 ** 53
        cum = 0
        kila i kwenye range(100):
            cum |= int(self.gen.random() * span)
        self.assertEqual(cum, span-1)

    eleza test_bigrand(self):
        # The randrange routine should build-up the required number of bits
        # kwenye stages so that all bit positions are active.
        span = 2 ** 500
        cum = 0
        kila i kwenye range(100):
            r = self.gen.randrange(span)
            self.assertKweli(0 <= r < span)
            cum |= r
        self.assertEqual(cum, span-1)

    eleza test_bigrand_ranges(self):
        kila i kwenye [40,80, 160, 200, 211, 250, 375, 512, 550]:
            start = self.gen.randrange(2 ** (i-2))
            stop = self.gen.randrange(2 ** i)
            ikiwa stop <= start:
                endelea
            self.assertKweli(start <= self.gen.randrange(start, stop) < stop)

    eleza test_rangelimits(self):
        kila start, stop kwenye [(-2,0), (-(2**60)-2,-(2**60)), (2**60,2**60+2)]:
            self.assertEqual(set(range(start,stop)),
                set([self.gen.randrange(start,stop) kila i kwenye range(100)]))

    eleza test_genrandbits(self):
        # Verify cross-platform repeatability
        self.gen.seed(1234567)
        self.assertEqual(self.gen.getrandbits(100),
                         97904845777343510404718956115)
        # Verify ranges
        kila k kwenye range(1, 1000):
            self.assertKweli(0 <= self.gen.getrandbits(k) < 2**k)

        # Verify all bits active
        getbits = self.gen.getrandbits
        kila span kwenye [1, 2, 3, 4, 31, 32, 32, 52, 53, 54, 119, 127, 128, 129]:
            cum = 0
            kila i kwenye range(100):
                cum |= getbits(span)
            self.assertEqual(cum, 2**span-1)

        # Verify argument checking
        self.assertRaises(TypeError, self.gen.getrandbits)
        self.assertRaises(TypeError, self.gen.getrandbits, 'a')
        self.assertRaises(TypeError, self.gen.getrandbits, 1, 2)
        self.assertRaises(ValueError, self.gen.getrandbits, 0)
        self.assertRaises(ValueError, self.gen.getrandbits, -1)

    eleza test_randrange_uses_getrandbits(self):
        # Verify use of getrandbits by randrange
        # Use same seed kama kwenye the cross-platform repeatability test
        # kwenye test_genrandbits above.
        self.gen.seed(1234567)
        # If randrange uses getrandbits, it should pick getrandbits(100)
        # when called with a 100-bits stop argument.
        self.assertEqual(self.gen.randrange(2**99),
                         97904845777343510404718956115)

    eleza test_randbelow_logic(self, _log=log, int=int):
        # check bitcount transition points:  2**i na 2**(i+1)-1
        # show that: k = int(1.001 + _log(n, 2))
        # ni equal to ama one greater than the number of bits kwenye n
        kila i kwenye range(1, 1000):
            n = 1 << i # check an exact power of two
            numbits = i+1
            k = int(1.00001 + _log(n, 2))
            self.assertEqual(k, numbits)
            self.assertEqual(n, 2**(k-1))

            n += n - 1      # check 1 below the next power of two
            k = int(1.00001 + _log(n, 2))
            self.assertIn(k, [numbits, numbits+1])
            self.assertKweli(2**k > n > 2**(k-2))

            n -= n >> 15     # check a little farther below the next power of two
            k = int(1.00001 + _log(n, 2))
            self.assertEqual(k, numbits)        # note the stronger assertion
            self.assertKweli(2**k > n > 2**(k-1))   # note the stronger assertion

    eleza test_randbelow_without_getrandbits(self):
        # Random._randbelow() can only use random() when the built-in one
        # has been overridden but no new getrandbits() method was supplied.
        maxsize = 1<<random.BPF
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            # Population range too large (n >= maxsize)
            self.gen._randbelow_without_getrandbits(
                maxsize+1, maxsize=maxsize
            )
        self.gen._randbelow_without_getrandbits(5640, maxsize=maxsize)
        # issue 33203: test that _randbelow ashirias ValueError on
        # n == 0 also kwenye its getrandbits-independent branch.
        with self.assertRaises(ValueError):
            self.gen._randbelow_without_getrandbits(0, maxsize=maxsize)

        # This might be going too far to test a single line, but because of our
        # noble aim of achieving 100% test coverage we need to write a case in
        # which the following line kwenye Random._randbelow() gets executed:
        #
        # rem = maxsize % n
        # limit = (maxsize - rem) / maxsize
        # r = random()
        # wakati r >= limit:
        #     r = random() # <== *This line* <==<
        #
        # Therefore, to guarantee that the wakati loop ni executed at least
        # once, we need to mock random() so that it rudishas a number greater
        # than 'limit' the first time it gets called.

        n = 42
        epsilon = 0.01
        limit = (maxsize - (maxsize % n)) / maxsize
        with unittest.mock.patch.object(random.Random, 'random') kama random_mock:
            random_mock.side_effect = [limit + epsilon, limit - epsilon]
            self.gen._randbelow_without_getrandbits(n, maxsize=maxsize)
            self.assertEqual(random_mock.call_count, 2)

    eleza test_randrange_bug_1590891(self):
        start = 1000000000000
        stop = -100000000000000000000
        step = -200
        x = self.gen.randrange(start, stop, step)
        self.assertKweli(stop < x <= start)
        self.assertEqual((x+stop)%step, 0)

    eleza test_choices_algorithms(self):
        # The various ways of specifying weights should produce the same results
        choices = self.gen.choices
        n = 104729

        self.gen.seed(8675309)
        a = self.gen.choices(range(n), k=10000)

        self.gen.seed(8675309)
        b = self.gen.choices(range(n), [1]*n, k=10000)
        self.assertEqual(a, b)

        self.gen.seed(8675309)
        c = self.gen.choices(range(n), cum_weights=range(1, n+1), k=10000)
        self.assertEqual(a, c)

        # American Roulette
        population = ['Red', 'Black', 'Green']
        weights = [18, 18, 2]
        cum_weights = [18, 36, 38]
        expanded_population = ['Red'] * 18 + ['Black'] * 18 + ['Green'] * 2

        self.gen.seed(9035768)
        a = self.gen.choices(expanded_population, k=10000)

        self.gen.seed(9035768)
        b = self.gen.choices(population, weights, k=10000)
        self.assertEqual(a, b)

        self.gen.seed(9035768)
        c = self.gen.choices(population, cum_weights=cum_weights, k=10000)
        self.assertEqual(a, c)

eleza gamma(z, sqrt2pi=(2.0*pi)**0.5):
    # Reflection to right half of complex plane
    ikiwa z < 0.5:
        rudisha pi / sin(pi*z) / gamma(1.0-z)
    # Lanczos approximation with g=7
    az = z + (7.0 - 0.5)
    rudisha az ** (z-0.5) / exp(az) * sqrt2pi * fsum([
        0.9999999999995183,
        676.5203681218835 / z,
        -1259.139216722289 / (z+1.0),
        771.3234287757674 / (z+2.0),
        -176.6150291498386 / (z+3.0),
        12.50734324009056 / (z+4.0),
        -0.1385710331296526 / (z+5.0),
        0.9934937113930748e-05 / (z+6.0),
        0.1659470187408462e-06 / (z+7.0),
    ])

kundi TestDistributions(unittest.TestCase):
    eleza test_zeroinputs(self):
        # Verify that distributions can handle a series of zero inputs'
        g = random.Random()
        x = [g.random() kila i kwenye range(50)] + [0.0]*5
        g.random = x[:].pop; g.uniform(1,10)
        g.random = x[:].pop; g.paretovariate(1.0)
        g.random = x[:].pop; g.expovariate(1.0)
        g.random = x[:].pop; g.weibullvariate(1.0, 1.0)
        g.random = x[:].pop; g.vonmisesvariate(1.0, 1.0)
        g.random = x[:].pop; g.normalvariate(0.0, 1.0)
        g.random = x[:].pop; g.gauss(0.0, 1.0)
        g.random = x[:].pop; g.lognormvariate(0.0, 1.0)
        g.random = x[:].pop; g.vonmisesvariate(0.0, 1.0)
        g.random = x[:].pop; g.gammavariate(0.01, 1.0)
        g.random = x[:].pop; g.gammavariate(1.0, 1.0)
        g.random = x[:].pop; g.gammavariate(200.0, 1.0)
        g.random = x[:].pop; g.betavariate(3.0, 3.0)
        g.random = x[:].pop; g.triangular(0.0, 1.0, 1.0/3.0)

    eleza test_avg_std(self):
        # Use integration to test distribution average na standard deviation.
        # Only works kila distributions which do sio consume variates kwenye pairs
        g = random.Random()
        N = 5000
        x = [i/float(N) kila i kwenye range(1,N)]
        kila variate, args, mu, sigmasqrd kwenye [
                (g.uniform, (1.0,10.0), (10.0+1.0)/2, (10.0-1.0)**2/12),
                (g.triangular, (0.0, 1.0, 1.0/3.0), 4.0/9.0, 7.0/9.0/18.0),
                (g.expovariate, (1.5,), 1/1.5, 1/1.5**2),
                (g.vonmisesvariate, (1.23, 0), pi, pi**2/3),
                (g.paretovariate, (5.0,), 5.0/(5.0-1),
                                  5.0/((5.0-1)**2*(5.0-2))),
                (g.weibullvariate, (1.0, 3.0), gamma(1+1/3.0),
                                  gamma(1+2/3.0)-gamma(1+1/3.0)**2) ]:
            g.random = x[:].pop
            y = []
            kila i kwenye range(len(x)):
                jaribu:
                    y.append(variate(*args))
                tatizo IndexError:
                    pita
            s1 = s2 = 0
            kila e kwenye y:
                s1 += e
                s2 += (e - mu) ** 2
            N = len(y)
            self.assertAlmostEqual(s1/N, mu, places=2,
                                   msg='%s%r' % (variate.__name__, args))
            self.assertAlmostEqual(s2/(N-1), sigmasqrd, places=2,
                                   msg='%s%r' % (variate.__name__, args))

    eleza test_constant(self):
        g = random.Random()
        N = 100
        kila variate, args, expected kwenye [
                (g.uniform, (10.0, 10.0), 10.0),
                (g.triangular, (10.0, 10.0), 10.0),
                (g.triangular, (10.0, 10.0, 10.0), 10.0),
                (g.expovariate, (float('inf'),), 0.0),
                (g.vonmisesvariate, (3.0, float('inf')), 3.0),
                (g.gauss, (10.0, 0.0), 10.0),
                (g.lognormvariate, (0.0, 0.0), 1.0),
                (g.lognormvariate, (-float('inf'), 0.0), 0.0),
                (g.normalvariate, (10.0, 0.0), 10.0),
                (g.paretovariate, (float('inf'),), 1.0),
                (g.weibullvariate, (10.0, float('inf')), 10.0),
                (g.weibullvariate, (0.0, 10.0), 0.0),
            ]:
            kila i kwenye range(N):
                self.assertEqual(variate(*args), expected)

    eleza test_von_mises_range(self):
        # Issue 17149: von mises variates were sio consistently kwenye the
        # range [0, 2*PI].
        g = random.Random()
        N = 100
        kila mu kwenye 0.0, 0.1, 3.1, 6.2:
            kila kappa kwenye 0.0, 2.3, 500.0:
                kila _ kwenye range(N):
                    sample = g.vonmisesvariate(mu, kappa)
                    self.assertKweli(
                        0 <= sample <= random.TWOPI,
                        msg=("vonmisesvariate({}, {}) produced a result {} out"
                             " of range [0, 2*pi]").format(mu, kappa, sample))

    eleza test_von_mises_large_kappa(self):
        # Issue #17141: vonmisesvariate() was hang kila large kappas
        random.vonmisesvariate(0, 1e15)
        random.vonmisesvariate(0, 1e100)

    eleza test_gammavariate_errors(self):
        # Both alpha na beta must be > 0.0
        self.assertRaises(ValueError, random.gammavariate, -1, 3)
        self.assertRaises(ValueError, random.gammavariate, 0, 2)
        self.assertRaises(ValueError, random.gammavariate, 2, 0)
        self.assertRaises(ValueError, random.gammavariate, 1, -3)

    # There are three different possibilities kwenye the current implementation
    # of random.gammavariate(), depending on the value of 'alpha'. What we
    # are going to do here ni to fix the values rudishaed by random() to
    # generate test cases that provide 100% line coverage of the method.
    @unittest.mock.patch('random.Random.random')
    eleza test_gammavariate_alpha_greater_one(self, random_mock):

        # #1: alpha > 1.0.
        # We want the first random number to be outside the
        # [1e-7, .9999999] range, so that the endelea statement executes
        # once. The values of u1 na u2 will be 0.5 na 0.3, respectively.
        random_mock.side_effect = [1e-8, 0.5, 0.3]
        rudishaed_value = random.gammavariate(1.1, 2.3)
        self.assertAlmostEqual(rudishaed_value, 2.53)

    @unittest.mock.patch('random.Random.random')
    eleza test_gammavariate_alpha_equal_one(self, random_mock):

        # #2.a: alpha == 1.
        # The execution body of the wakati loop executes once.
        # Then random.random() rudishas 0.45,
        # which causes wakati to stop looping na the algorithm to terminate.
        random_mock.side_effect = [0.45]
        rudishaed_value = random.gammavariate(1.0, 3.14)
        self.assertAlmostEqual(rudishaed_value, 1.877208182372648)

    @unittest.mock.patch('random.Random.random')
    eleza test_gammavariate_alpha_equal_one_equals_expovariate(self, random_mock):

        # #2.b: alpha == 1.
        # It must be equivalent of calling expovariate(1.0 / beta).
        beta = 3.14
        random_mock.side_effect = [1e-8, 1e-8]
        gammavariate_rudishaed_value = random.gammavariate(1.0, beta)
        expovariate_rudishaed_value = random.expovariate(1.0 / beta)
        self.assertAlmostEqual(gammavariate_rudishaed_value, expovariate_rudishaed_value)

    @unittest.mock.patch('random.Random.random')
    eleza test_gammavariate_alpha_between_zero_and_one(self, random_mock):

        # #3: 0 < alpha < 1.
        # This ni the most complex region of code to cover,
        # kama there are multiple if-else statements. Let's take a look at the
        # source code, na determine the values that we need accordingly:
        #
        # wakati 1:
        #     u = random()
        #     b = (_e + alpha)/_e
        #     p = b*u
        #     ikiwa p <= 1.0: # <=== (A)
        #         x = p ** (1.0/alpha)
        #     isipokua: # <=== (B)
        #         x = -_log((b-p)/alpha)
        #     u1 = random()
        #     ikiwa p > 1.0: # <=== (C)
        #         ikiwa u1 <= x ** (alpha - 1.0): # <=== (D)
        #             koma
        #     elikiwa u1 <= _exp(-x): # <=== (E)
        #         koma
        # rudisha x * beta
        #
        # First, we want (A) to be Kweli. For that we need that:
        # b*random() <= 1.0
        # r1 = random() <= 1.0 / b
        #
        # We now get to the second if-else branch, na here, since p <= 1.0,
        # (C) ni Uongo na we take the elikiwa branch, (E). For it to be Kweli,
        # so that the koma ni executed, we need that:
        # r2 = random() <= _exp(-x)
        # r2 <= _exp(-(p ** (1.0/alpha)))
        # r2 <= _exp(-((b*r1) ** (1.0/alpha)))

        _e = random._e
        _exp = random._exp
        _log = random._log
        alpha = 0.35
        beta = 1.45
        b = (_e + alpha)/_e
        epsilon = 0.01

        r1 = 0.8859296441566 # 1.0 / b
        r2 = 0.3678794411714 # _exp(-((b*r1) ** (1.0/alpha)))

        # These four "random" values result kwenye the following trace:
        # (A) Kweli, (E) Uongo --> [next iteration of while]
        # (A) Kweli, (E) Kweli --> [wakati loop komas]
        random_mock.side_effect = [r1, r2 + epsilon, r1, r2]
        rudishaed_value = random.gammavariate(alpha, beta)
        self.assertAlmostEqual(rudishaed_value, 1.4499999999997544)

        # Let's now make (A) be Uongo. If this ni the case, when we get to the
        # second if-else 'p' ni greater than 1, so (C) evaluates to Kweli. We
        # now encounter a second ikiwa statement, (D), which kwenye order to execute
        # must satisfy the following condition:
        # r2 <= x ** (alpha - 1.0)
        # r2 <= (-_log((b-p)/alpha)) ** (alpha - 1.0)
        # r2 <= (-_log((b-(b*r1))/alpha)) ** (alpha - 1.0)
        r1 = 0.8959296441566 # (1.0 / b) + epsilon -- so that (A) ni Uongo
        r2 = 0.9445400408898141

        # And these four values result kwenye the following trace:
        # (B) na (C) Kweli, (D) Uongo --> [next iteration of while]
        # (B) na (C) Kweli, (D) Kweli [wakati loop komas]
        random_mock.side_effect = [r1, r2 + epsilon, r1, r2]
        rudishaed_value = random.gammavariate(alpha, beta)
        self.assertAlmostEqual(rudishaed_value, 1.5830349561760781)

    @unittest.mock.patch('random.Random.gammavariate')
    eleza test_betavariate_rudisha_zero(self, gammavariate_mock):
        # betavariate() rudishas zero when the Gamma distribution
        # that it uses internally rudishas this same value.
        gammavariate_mock.rudisha_value = 0.0
        self.assertEqual(0.0, random.betavariate(2.71828, 3.14159))


kundi TestRandomSubclassing(unittest.TestCase):
    eleza test_random_subclass_with_kwargs(self):
        # SF bug #1486663 -- this used to erroneously ashiria a TypeError
        kundi Subclass(random.Random):
            eleza __init__(self, newarg=Tupu):
                random.Random.__init__(self)
        Subclass(newarg=1)

    eleza test_subclasses_overriding_methods(self):
        # Subclasses with an overridden random, but only the original
        # getrandbits method should sio rely on getrandbits kwenye kila randrange,
        # but should use a getrandbits-independent implementation instead.

        # subkundi providing its own random **and** getrandbits methods
        # like random.SystemRandom does => keep relying on getrandbits for
        # randrange
        kundi SubClass1(random.Random):
            eleza random(self):
                called.add('SubClass1.random')
                rudisha random.Random.random(self)

            eleza getrandbits(self, n):
                called.add('SubClass1.getrandbits')
                rudisha random.Random.getrandbits(self, n)
        called = set()
        SubClass1().randrange(42)
        self.assertEqual(called, {'SubClass1.getrandbits'})

        # subkundi providing only random => can only use random kila randrange
        kundi SubClass2(random.Random):
            eleza random(self):
                called.add('SubClass2.random')
                rudisha random.Random.random(self)
        called = set()
        SubClass2().randrange(42)
        self.assertEqual(called, {'SubClass2.random'})

        # subkundi defining getrandbits to complement its inherited random
        # => can now rely on getrandbits kila randrange again
        kundi SubClass3(SubClass2):
            eleza getrandbits(self, n):
                called.add('SubClass3.getrandbits')
                rudisha random.Random.getrandbits(self, n)
        called = set()
        SubClass3().randrange(42)
        self.assertEqual(called, {'SubClass3.getrandbits'})

        # subkundi providing only random na inherited getrandbits
        # => random takes precedence
        kundi SubClass4(SubClass3):
            eleza random(self):
                called.add('SubClass4.random')
                rudisha random.Random.random(self)
        called = set()
        SubClass4().randrange(42)
        self.assertEqual(called, {'SubClass4.random'})

        # Following subclasses don't define random ama getrandbits directly,
        # but inherit them kutoka classes which are sio subclasses of Random
        kundi Mixin1:
            eleza random(self):
                called.add('Mixin1.random')
                rudisha random.Random.random(self)
        kundi Mixin2:
            eleza getrandbits(self, n):
                called.add('Mixin2.getrandbits')
                rudisha random.Random.getrandbits(self, n)

        kundi SubClass5(Mixin1, random.Random):
            pita
        called = set()
        SubClass5().randrange(42)
        self.assertEqual(called, {'Mixin1.random'})

        kundi SubClass6(Mixin2, random.Random):
            pita
        called = set()
        SubClass6().randrange(42)
        self.assertEqual(called, {'Mixin2.getrandbits'})

        kundi SubClass7(Mixin1, Mixin2, random.Random):
            pita
        called = set()
        SubClass7().randrange(42)
        self.assertEqual(called, {'Mixin1.random'})

        kundi SubClass8(Mixin2, Mixin1, random.Random):
            pita
        called = set()
        SubClass8().randrange(42)
        self.assertEqual(called, {'Mixin2.getrandbits'})


kundi TestModule(unittest.TestCase):
    eleza testMagicConstants(self):
        self.assertAlmostEqual(random.NV_MAGICCONST, 1.71552776992141)
        self.assertAlmostEqual(random.TWOPI, 6.28318530718)
        self.assertAlmostEqual(random.LOG4, 1.38629436111989)
        self.assertAlmostEqual(random.SG_MAGICCONST, 2.50407739677627)

    eleza test__all__(self):
        # tests validity but sio completeness of the __all__ list
        self.assertKweli(set(random.__all__) <= set(dir(random)))

    @unittest.skipUnless(hasattr(os, "fork"), "fork() required")
    eleza test_after_fork(self):
        # Test the global Random instance gets reseeded kwenye child
        r, w = os.pipe()
        pid = os.fork()
        ikiwa pid == 0:
            # child process
            jaribu:
                val = random.getrandbits(128)
                with open(w, "w") kama f:
                    f.write(str(val))
            mwishowe:
                os._exit(0)
        isipokua:
            # parent process
            os.close(w)
            val = random.getrandbits(128)
            with open(r, "r") kama f:
                child_val = eval(f.read())
            self.assertNotEqual(val, child_val)

            pid, status = os.waitpid(pid, 0)
            self.assertEqual(status, 0)


ikiwa __name__ == "__main__":
    unittest.main()
