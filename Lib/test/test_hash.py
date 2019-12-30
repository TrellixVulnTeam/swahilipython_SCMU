# test the invariant that
#   iff a==b then hash(a)==hash(b)
#
# Also test that hash implementations are inherited kama expected

agiza datetime
agiza os
agiza sys
agiza unittest
kutoka test.support.script_helper agiza assert_python_ok
kutoka collections.abc agiza Hashable

IS_64BIT = sys.maxsize > 2**32

eleza lcg(x, length=16):
    """Linear congruential generator"""
    ikiwa x == 0:
        rudisha bytes(length)
    out = bytearray(length)
    kila i kwenye range(length):
        x = (214013 * x + 2531011) & 0x7fffffff
        out[i] = (x >> 16) & 0xff
    rudisha bytes(out)

eleza pysiphash(uint64):
    """Convert SipHash24 output to Py_hash_t
    """
    assert 0 <= uint64 < (1 << 64)
    # simple unsigned to signed int64
    ikiwa uint64 > (1 << 63) - 1:
        int64 = uint64 - (1 << 64)
    isipokua:
        int64 = uint64
    # mangle uint64 to uint32
    uint32 = (uint64 ^ uint64 >> 32) & 0xffffffff
    # simple unsigned to signed int32
    ikiwa uint32 > (1 << 31) - 1:
        int32 = uint32 - (1 << 32)
    isipokua:
        int32 = uint32
    rudisha int32, int64

eleza skip_unless_internalhash(test):
    """Skip decorator kila tests that depend on SipHash24 ama FNV"""
    ok = sys.hash_info.algorithm kwenye {"fnv", "siphash24"}
    msg = "Requires SipHash24 ama FNV"
    rudisha test ikiwa ok isipokua unittest.skip(msg)(test)


kundi HashEqualityTestCase(unittest.TestCase):

    eleza same_hash(self, *objlist):
        # Hash each object given na fail if
        # the hash values are sio all the same.
        hashed = list(map(hash, objlist))
        kila h kwenye hashed[1:]:
            ikiwa h != hashed[0]:
                self.fail("hashed values differ: %r" % (objlist,))

    eleza test_numeric_literals(self):
        self.same_hash(1, 1, 1.0, 1.0+0.0j)
        self.same_hash(0, 0.0, 0.0+0.0j)
        self.same_hash(-1, -1.0, -1.0+0.0j)
        self.same_hash(-2, -2.0, -2.0+0.0j)

    eleza test_coerced_integers(self):
        self.same_hash(int(1), int(1), float(1), complex(1),
                       int('1'), float('1.0'))
        self.same_hash(int(-2**31), float(-2**31))
        self.same_hash(int(1-2**31), float(1-2**31))
        self.same_hash(int(2**31-1), float(2**31-1))
        # kila 64-bit platforms
        self.same_hash(int(2**31), float(2**31))
        self.same_hash(int(-2**63), float(-2**63))
        self.same_hash(int(2**63), float(2**63))

    eleza test_coerced_floats(self):
        self.same_hash(int(1.23e300), float(1.23e300))
        self.same_hash(float(0.5), complex(0.5, 0.0))

    eleza test_unaligned_buffers(self):
        # The hash function kila bytes-like objects shouldn't have
        # alignment-dependent results (example kwenye issue #16427).
        b = b"123456789abcdefghijklmnopqrstuvwxyz" * 128
        kila i kwenye range(16):
            kila j kwenye range(16):
                aligned = b[i:128+j]
                unaligned = memoryview(b)[i:128+j]
                self.assertEqual(hash(aligned), hash(unaligned))


_default_hash = object.__hash__
kundi DefaultHash(object): pita

_FIXED_HASH_VALUE = 42
kundi FixedHash(object):
    eleza __hash__(self):
        rudisha _FIXED_HASH_VALUE

kundi OnlyEquality(object):
    eleza __eq__(self, other):
        rudisha self ni other

kundi OnlyInequality(object):
    eleza __ne__(self, other):
        rudisha self ni sio other

kundi InheritedHashWithEquality(FixedHash, OnlyEquality): pita
kundi InheritedHashWithInequality(FixedHash, OnlyInequality): pita

kundi NoHash(object):
    __hash__ = Tupu

kundi HashInheritanceTestCase(unittest.TestCase):
    default_expected = [object(),
                        DefaultHash(),
                        OnlyInequality(),
                       ]
    fixed_expected = [FixedHash(),
                      InheritedHashWithEquality(),
                      InheritedHashWithInequality(),
                      ]
    error_expected = [NoHash(),
                      OnlyEquality(),
                      ]

    eleza test_default_hash(self):
        kila obj kwenye self.default_expected:
            self.assertEqual(hash(obj), _default_hash(obj))

    eleza test_fixed_hash(self):
        kila obj kwenye self.fixed_expected:
            self.assertEqual(hash(obj), _FIXED_HASH_VALUE)

    eleza test_error_hash(self):
        kila obj kwenye self.error_expected:
            self.assertRaises(TypeError, hash, obj)

    eleza test_hashable(self):
        objects = (self.default_expected +
                   self.fixed_expected)
        kila obj kwenye objects:
            self.assertIsInstance(obj, Hashable)

    eleza test_not_hashable(self):
        kila obj kwenye self.error_expected:
            self.assertNotIsInstance(obj, Hashable)


# Issue #4701: Check that some builtin types are correctly hashable
kundi DefaultIterSeq(object):
    seq = range(10)
    eleza __len__(self):
        rudisha len(self.seq)
    eleza __getitem__(self, index):
        rudisha self.seq[index]

kundi HashBuiltinsTestCase(unittest.TestCase):
    hashes_to_check = [enumerate(range(10)),
                       iter(DefaultIterSeq()),
                       iter(lambda: 0, 0),
                      ]

    eleza test_hashes(self):
        _default_hash = object.__hash__
        kila obj kwenye self.hashes_to_check:
            self.assertEqual(hash(obj), _default_hash(obj))

kundi HashRandomizationTests:

    # Each subkundi should define a field "repr_", containing the repr() of
    # an object to be tested

    eleza get_hash_command(self, repr_):
        rudisha 'andika(hash(eval(%a)))' % repr_

    eleza get_hash(self, repr_, seed=Tupu):
        env = os.environ.copy()
        env['__cleanenv'] = Kweli  # signal to assert_python sio to do a copy
                                  # of os.environ on its own
        ikiwa seed ni sio Tupu:
            env['PYTHONHASHSEED'] = str(seed)
        isipokua:
            env.pop('PYTHONHASHSEED', Tupu)
        out = assert_python_ok(
            '-c', self.get_hash_command(repr_),
            **env)
        stdout = out[1].strip()
        rudisha int(stdout)

    eleza test_randomized_hash(self):
        # two runs should rudisha different hashes
        run1 = self.get_hash(self.repr_, seed='random')
        run2 = self.get_hash(self.repr_, seed='random')
        self.assertNotEqual(run1, run2)

kundi StringlikeHashRandomizationTests(HashRandomizationTests):
    repr_ = Tupu
    repr_long = Tupu

    # 32bit little, 64bit little, 32bit big, 64bit big
    known_hashes = {
        'djba33x': [ # only used kila small strings
            # seed 0, 'abc'
            [193485960, 193485960,  193485960, 193485960],
            # seed 42, 'abc'
            [-678966196, 573763426263223372, -820489388, -4282905804826039665],
            ],
        'siphash24': [
            # NOTE: PyUCS2 layout depends on endianness
            # seed 0, 'abc'
            [1198583518, 4596069200710135518, 1198583518, 4596069200710135518],
            # seed 42, 'abc'
            [273876886, -4501618152524544106, 273876886, -4501618152524544106],
            # seed 42, 'abcdefghijk'
            [-1745215313, 4436719588892876975, -1745215313, 4436719588892876975],
            # seed 0, 'äú∑ℇ'
            [493570806, 5749986484189612790, -1006381564, -5915111450199468540],
            # seed 42, 'äú∑ℇ'
            [-1677110816, -2947981342227738144, -1860207793, -4296699217652516017],
        ],
        'fnv': [
            # seed 0, 'abc'
            [-1600925533, 1453079729188098211, -1600925533,
             1453079729188098211],
            # seed 42, 'abc'
            [-206076799, -4410911502303878509, -1024014457,
             -3570150969479994130],
            # seed 42, 'abcdefghijk'
            [811136751, -5046230049376118746, -77208053 ,
             -4779029615281019666],
            # seed 0, 'äú∑ℇ'
            [44402817, 8998297579845987431, -1956240331,
             -782697888614047887],
            # seed 42, 'äú∑ℇ'
            [-283066365, -4576729883824601543, -271871407,
             -3927695501187247084],
        ]
    }

    eleza get_expected_hash(self, position, length):
        ikiwa length < sys.hash_info.cutoff:
            algorithm = "djba33x"
        isipokua:
            algorithm = sys.hash_info.algorithm
        ikiwa sys.byteorder == 'little':
            platform = 1 ikiwa IS_64BIT isipokua 0
        isipokua:
            assert(sys.byteorder == 'big')
            platform = 3 ikiwa IS_64BIT isipokua 2
        rudisha self.known_hashes[algorithm][position][platform]

    eleza test_null_hash(self):
        # PYTHONHASHSEED=0 disables the randomized hash
        known_hash_of_obj = self.get_expected_hash(0, 3)

        # Randomization ni enabled by default:
        self.assertNotEqual(self.get_hash(self.repr_), known_hash_of_obj)

        # It can also be disabled by setting the seed to 0:
        self.assertEqual(self.get_hash(self.repr_, seed=0), known_hash_of_obj)

    @skip_unless_internalhash
    eleza test_fixed_hash(self):
        # test a fixed seed kila the randomized hash
        # Note that all types share the same values:
        h = self.get_expected_hash(1, 3)
        self.assertEqual(self.get_hash(self.repr_, seed=42), h)

    @skip_unless_internalhash
    eleza test_long_fixed_hash(self):
        ikiwa self.repr_long ni Tupu:
            rudisha
        h = self.get_expected_hash(2, 11)
        self.assertEqual(self.get_hash(self.repr_long, seed=42), h)


kundi StrHashRandomizationTests(StringlikeHashRandomizationTests,
                                unittest.TestCase):
    repr_ = repr('abc')
    repr_long = repr('abcdefghijk')
    repr_ucs2 = repr('äú∑ℇ')

    @skip_unless_internalhash
    eleza test_empty_string(self):
        self.assertEqual(hash(""), 0)

    @skip_unless_internalhash
    eleza test_ucs2_string(self):
        h = self.get_expected_hash(3, 6)
        self.assertEqual(self.get_hash(self.repr_ucs2, seed=0), h)
        h = self.get_expected_hash(4, 6)
        self.assertEqual(self.get_hash(self.repr_ucs2, seed=42), h)

kundi BytesHashRandomizationTests(StringlikeHashRandomizationTests,
                                  unittest.TestCase):
    repr_ = repr(b'abc')
    repr_long = repr(b'abcdefghijk')

    @skip_unless_internalhash
    eleza test_empty_string(self):
        self.assertEqual(hash(b""), 0)

kundi MemoryviewHashRandomizationTests(StringlikeHashRandomizationTests,
                                       unittest.TestCase):
    repr_ = "memoryview(b'abc')"
    repr_long = "memoryview(b'abcdefghijk')"

    @skip_unless_internalhash
    eleza test_empty_string(self):
        self.assertEqual(hash(memoryview(b"")), 0)

kundi DatetimeTests(HashRandomizationTests):
    eleza get_hash_command(self, repr_):
        rudisha 'agiza datetime; andika(hash(%s))' % repr_

kundi DatetimeDateTests(DatetimeTests, unittest.TestCase):
    repr_ = repr(datetime.date(1066, 10, 14))

kundi DatetimeDatetimeTests(DatetimeTests, unittest.TestCase):
    repr_ = repr(datetime.datetime(1, 2, 3, 4, 5, 6, 7))

kundi DatetimeTimeTests(DatetimeTests, unittest.TestCase):
    repr_ = repr(datetime.time(0))


kundi HashDistributionTestCase(unittest.TestCase):

    eleza test_hash_distribution(self):
        # check kila hash collision
        base = "abcdefghabcdefg"
        kila i kwenye range(1, len(base)):
            prefix = base[:i]
            ukijumuisha self.subTest(prefix=prefix):
                s15 = set()
                s255 = set()
                kila c kwenye range(256):
                    h = hash(prefix + chr(c))
                    s15.add(h & 0xf)
                    s255.add(h & 0xff)
                # SipHash24 distribution depends on key, usually > 60%
                self.assertGreater(len(s15), 8, prefix)
                self.assertGreater(len(s255), 128, prefix)

ikiwa __name__ == "__main__":
    unittest.main()
