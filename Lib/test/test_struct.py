kutoka collections agiza abc
agiza array
agiza math
agiza operator
agiza unittest
agiza struct
agiza sys

kutoka test agiza support

ISBIGENDIAN = sys.byteorder == "big"

integer_codes = 'b', 'B', 'h', 'H', 'i', 'I', 'l', 'L', 'q', 'Q', 'n', 'N'
byteorders = '', '@', '=', '<', '>', '!'

eleza iter_integer_formats(byteorders=byteorders):
    kila code kwenye integer_codes:
        kila byteorder kwenye byteorders:
            ikiwa (byteorder haiko kwenye ('', '@') na code kwenye ('n', 'N')):
                endelea
            tuma code, byteorder

eleza string_reverse(s):
    rudisha s[::-1]

eleza bigendian_to_native(value):
    ikiwa ISBIGENDIAN:
        rudisha value
    isipokua:
        rudisha string_reverse(value)

kundi StructTest(unittest.TestCase):
    eleza test_isbigendian(self):
        self.assertEqual((struct.pack('=i', 1)[0] == 0), ISBIGENDIAN)

    eleza test_consistence(self):
        self.assertRaises(struct.error, struct.calcsize, 'Z')

        sz = struct.calcsize('i')
        self.assertEqual(sz * 3, struct.calcsize('iii'))

        fmt = 'cbxxxxxxhhhhiillffd?'
        fmt3 = '3c3b18x12h6i6l6f3d3?'
        sz = struct.calcsize(fmt)
        sz3 = struct.calcsize(fmt3)
        self.assertEqual(sz * 3, sz3)

        self.assertRaises(struct.error, struct.pack, 'iii', 3)
        self.assertRaises(struct.error, struct.pack, 'i', 3, 3, 3)
        self.assertRaises((TypeError, struct.error), struct.pack, 'i', 'foo')
        self.assertRaises((TypeError, struct.error), struct.pack, 'P', 'foo')
        self.assertRaises(struct.error, struct.unpack, 'd', b'flap')
        s = struct.pack('ii', 1, 2)
        self.assertRaises(struct.error, struct.unpack, 'iii', s)
        self.assertRaises(struct.error, struct.unpack, 'i', s)

    eleza test_transitiveness(self):
        c = b'a'
        b = 1
        h = 255
        i = 65535
        l = 65536
        f = 3.1415
        d = 3.1415
        t = Kweli

        kila prefix kwenye ('', '@', '<', '>', '=', '!'):
            kila format kwenye ('xcbhilfd?', 'xcBHILfd?'):
                format = prefix + format
                s = struct.pack(format, c, b, h, i, l, f, d, t)
                cp, bp, hp, ip, lp, fp, dp, tp = struct.unpack(format, s)
                self.assertEqual(cp, c)
                self.assertEqual(bp, b)
                self.assertEqual(hp, h)
                self.assertEqual(ip, i)
                self.assertEqual(lp, l)
                self.assertEqual(int(100 * fp), int(100 * f))
                self.assertEqual(int(100 * dp), int(100 * d))
                self.assertEqual(tp, t)

    eleza test_new_features(self):
        # Test some of the new features kwenye detail
        # (format, argument, big-endian result, little-endian result, asymmetric)
        tests = [
            ('c', b'a', b'a', b'a', 0),
            ('xc', b'a', b'\0a', b'\0a', 0),
            ('cx', b'a', b'a\0', b'a\0', 0),
            ('s', b'a', b'a', b'a', 0),
            ('0s', b'helloworld', b'', b'', 1),
            ('1s', b'helloworld', b'h', b'h', 1),
            ('9s', b'helloworld', b'helloworl', b'helloworl', 1),
            ('10s', b'helloworld', b'helloworld', b'helloworld', 0),
            ('11s', b'helloworld', b'helloworld\0', b'helloworld\0', 1),
            ('20s', b'helloworld', b'helloworld'+10*b'\0', b'helloworld'+10*b'\0', 1),
            ('b', 7, b'\7', b'\7', 0),
            ('b', -7, b'\371', b'\371', 0),
            ('B', 7, b'\7', b'\7', 0),
            ('B', 249, b'\371', b'\371', 0),
            ('h', 700, b'\002\274', b'\274\002', 0),
            ('h', -700, b'\375D', b'D\375', 0),
            ('H', 700, b'\002\274', b'\274\002', 0),
            ('H', 0x10000-700, b'\375D', b'D\375', 0),
            ('i', 70000000, b'\004,\035\200', b'\200\035,\004', 0),
            ('i', -70000000, b'\373\323\342\200', b'\200\342\323\373', 0),
            ('I', 70000000, b'\004,\035\200', b'\200\035,\004', 0),
            ('I', 0x100000000-70000000, b'\373\323\342\200', b'\200\342\323\373', 0),
            ('l', 70000000, b'\004,\035\200', b'\200\035,\004', 0),
            ('l', -70000000, b'\373\323\342\200', b'\200\342\323\373', 0),
            ('L', 70000000, b'\004,\035\200', b'\200\035,\004', 0),
            ('L', 0x100000000-70000000, b'\373\323\342\200', b'\200\342\323\373', 0),
            ('f', 2.0, b'@\000\000\000', b'\000\000\000@', 0),
            ('d', 2.0, b'@\000\000\000\000\000\000\000',
                       b'\000\000\000\000\000\000\000@', 0),
            ('f', -2.0, b'\300\000\000\000', b'\000\000\000\300', 0),
            ('d', -2.0, b'\300\000\000\000\000\000\000\000',
                        b'\000\000\000\000\000\000\000\300', 0),
            ('?', 0, b'\0', b'\0', 0),
            ('?', 3, b'\1', b'\1', 1),
            ('?', Kweli, b'\1', b'\1', 0),
            ('?', [], b'\0', b'\0', 1),
            ('?', (1,), b'\1', b'\1', 1),
        ]

        kila fmt, arg, big, lil, asy kwenye tests:
            kila (xfmt, exp) kwenye [('>'+fmt, big), ('!'+fmt, big), ('<'+fmt, lil),
                                ('='+fmt, ISBIGENDIAN na big ama lil)]:
                res = struct.pack(xfmt, arg)
                self.assertEqual(res, exp)
                self.assertEqual(struct.calcsize(xfmt), len(res))
                rev = struct.unpack(xfmt, res)[0]
                ikiwa rev != arg:
                    self.assertKweli(asy)

    eleza test_calcsize(self):
        expected_size = {
            'b': 1, 'B': 1,
            'h': 2, 'H': 2,
            'i': 4, 'I': 4,
            'l': 4, 'L': 4,
            'q': 8, 'Q': 8,
            }

        # standard integer sizes
        kila code, byteorder kwenye iter_integer_formats(('=', '<', '>', '!')):
            format = byteorder+code
            size = struct.calcsize(format)
            self.assertEqual(size, expected_size[code])

        # native integer sizes
        native_pairs = 'bB', 'hH', 'iI', 'lL', 'nN', 'qQ'
        kila format_pair kwenye native_pairs:
            kila byteorder kwenye '', '@':
                signed_size = struct.calcsize(byteorder + format_pair[0])
                unsigned_size = struct.calcsize(byteorder + format_pair[1])
                self.assertEqual(signed_size, unsigned_size)

        # bounds kila native integer sizes
        self.assertEqual(struct.calcsize('b'), 1)
        self.assertLessEqual(2, struct.calcsize('h'))
        self.assertLessEqual(4, struct.calcsize('l'))
        self.assertLessEqual(struct.calcsize('h'), struct.calcsize('i'))
        self.assertLessEqual(struct.calcsize('i'), struct.calcsize('l'))
        self.assertLessEqual(8, struct.calcsize('q'))
        self.assertLessEqual(struct.calcsize('l'), struct.calcsize('q'))
        self.assertGreaterEqual(struct.calcsize('n'), struct.calcsize('i'))
        self.assertGreaterEqual(struct.calcsize('n'), struct.calcsize('P'))

    eleza test_integers(self):
        # Integer tests (bBhHiIlLqQnN).
        agiza binascii

        kundi IntTester(unittest.TestCase):
            eleza __init__(self, format):
                super(IntTester, self).__init__(methodName='test_one')
                self.format = format
                self.code = format[-1]
                self.byteorder = format[:-1]
                ikiwa sio self.byteorder kwenye byteorders:
                    ashiria ValueError("unrecognized packing byteorder: %s" %
                                     self.byteorder)
                self.bytesize = struct.calcsize(format)
                self.bitsize = self.bytesize * 8
                ikiwa self.code kwenye tuple('bhilqn'):
                    self.signed = Kweli
                    self.min_value = -(2**(self.bitsize-1))
                    self.max_value = 2**(self.bitsize-1) - 1
                lasivyo self.code kwenye tuple('BHILQN'):
                    self.signed = Uongo
                    self.min_value = 0
                    self.max_value = 2**self.bitsize - 1
                isipokua:
                    ashiria ValueError("unrecognized format code: %s" %
                                     self.code)

            eleza test_one(self, x, pack=struct.pack,
                                  unpack=struct.unpack,
                                  unhexlify=binascii.unhexlify):

                format = self.format
                ikiwa self.min_value <= x <= self.max_value:
                    expected = x
                    ikiwa self.signed na x < 0:
                        expected += 1 << self.bitsize
                    self.assertGreaterEqual(expected, 0)
                    expected = '%x' % expected
                    ikiwa len(expected) & 1:
                        expected = "0" + expected
                    expected = expected.encode('ascii')
                    expected = unhexlify(expected)
                    expected = (b"\x00" * (self.bytesize - len(expected)) +
                                expected)
                    ikiwa (self.byteorder == '<' ama
                        self.byteorder kwenye ('', '@', '=') na sio ISBIGENDIAN):
                        expected = string_reverse(expected)
                    self.assertEqual(len(expected), self.bytesize)

                    # Pack work?
                    got = pack(format, x)
                    self.assertEqual(got, expected)

                    # Unpack work?
                    retrieved = unpack(format, got)[0]
                    self.assertEqual(x, retrieved)

                    # Adding any byte should cause a "too big" error.
                    self.assertRaises((struct.error, TypeError), unpack, format,
                                                                 b'\x01' + got)
                isipokua:
                    # x ni out of range -- verify pack realizes that.
                    self.assertRaises((OverflowError, ValueError, struct.error),
                                      pack, format, x)

            eleza run(self):
                kutoka random agiza randrange

                # Create all interesting powers of 2.
                values = []
                kila exp kwenye range(self.bitsize + 3):
                    values.append(1 << exp)

                # Add some random values.
                kila i kwenye range(self.bitsize):
                    val = 0
                    kila j kwenye range(self.bytesize):
                        val = (val << 8) | randrange(256)
                    values.append(val)

                # Values absorbed kutoka other tests
                values.extend([300, 700000, sys.maxsize*4])

                # Try all those, na their negations, na +-1 from
                # them.  Note that this tests all power-of-2
                # boundaries kwenye range, na a few out of range, plus
                # +-(2**n +- 1).
                kila base kwenye values:
                    kila val kwenye -base, base:
                        kila incr kwenye -1, 0, 1:
                            x = val + incr
                            self.test_one(x)

                # Some error cases.
                kundi NotAnInt:
                    eleza __int__(self):
                        rudisha 42

                # Objects ukijumuisha an '__index__' method should be allowed
                # to pack kama integers.  That ni assuming the implemented
                # '__index__' method returns an 'int'.
                kundi Indexable(object):
                    eleza __init__(self, value):
                        self._value = value

                    eleza __index__(self):
                        rudisha self._value

                # If the '__index__' method raises a type error, then
                # '__int__' should be used ukijumuisha a deprecation warning.
                kundi BadIndex(object):
                    eleza __index__(self):
                        ashiria TypeError

                    eleza __int__(self):
                        rudisha 42

                self.assertRaises((TypeError, struct.error),
                                  struct.pack, self.format,
                                  "a string")
                self.assertRaises((TypeError, struct.error),
                                  struct.pack, self.format,
                                  randrange)
                self.assertRaises((TypeError, struct.error),
                                  struct.pack, self.format,
                                  3+42j)
                self.assertRaises((TypeError, struct.error),
                                  struct.pack, self.format,
                                  NotAnInt())
                self.assertRaises((TypeError, struct.error),
                                  struct.pack, self.format,
                                  BadIndex())

                # Check kila legitimate values kutoka '__index__'.
                kila obj kwenye (Indexable(0), Indexable(10), Indexable(17),
                            Indexable(42), Indexable(100), Indexable(127)):
                    jaribu:
                        struct.pack(format, obj)
                    tatizo:
                        self.fail("integer code pack failed on object "
                                  "ukijumuisha '__index__' method")

                # Check kila bogus values kutoka '__index__'.
                kila obj kwenye (Indexable(b'a'), Indexable('b'), Indexable(Tupu),
                            Indexable({'a': 1}), Indexable([1, 2, 3])):
                    self.assertRaises((TypeError, struct.error),
                                      struct.pack, self.format,
                                      obj)

        kila code, byteorder kwenye iter_integer_formats():
            format = byteorder+code
            t = IntTester(format)
            t.run()

    eleza test_nN_code(self):
        # n na N don't exist kwenye standard sizes
        eleza assertStructError(func, *args, **kwargs):
            ukijumuisha self.assertRaises(struct.error) kama cm:
                func(*args, **kwargs)
            self.assertIn("bad char kwenye struct format", str(cm.exception))
        kila code kwenye 'nN':
            kila byteorder kwenye ('=', '<', '>', '!'):
                format = byteorder+code
                assertStructError(struct.calcsize, format)
                assertStructError(struct.pack, format, 0)
                assertStructError(struct.unpack, format, b"")

    eleza test_p_code(self):
        # Test p ("Pascal string") code.
        kila code, input, expected, expectedback kwenye [
                ('p',  b'abc', b'\x00',            b''),
                ('1p', b'abc', b'\x00',            b''),
                ('2p', b'abc', b'\x01a',           b'a'),
                ('3p', b'abc', b'\x02ab',          b'ab'),
                ('4p', b'abc', b'\x03abc',         b'abc'),
                ('5p', b'abc', b'\x03abc\x00',     b'abc'),
                ('6p', b'abc', b'\x03abc\x00\x00', b'abc'),
                ('1000p', b'x'*1000, b'\xff' + b'x'*999, b'x'*255)]:
            got = struct.pack(code, input)
            self.assertEqual(got, expected)
            (got,) = struct.unpack(code, got)
            self.assertEqual(got, expectedback)

    eleza test_705836(self):
        # SF bug 705836.  "<f" na ">f" had a severe rounding bug, where a carry
        # kutoka the low-order discarded bits could propagate into the exponent
        # field, causing the result to be wrong by a factor of 2.
        kila base kwenye range(1, 33):
            # smaller <- largest representable float less than base.
            delta = 0.5
            wakati base - delta / 2.0 != base:
                delta /= 2.0
            smaller = base - delta
            # Packing this rounds away a solid string of trailing 1 bits.
            packed = struct.pack("<f", smaller)
            unpacked = struct.unpack("<f", packed)[0]
            # This failed at base = 2, 4, na 32, ukijumuisha unpacked = 1, 2, na
            # 16, respectively.
            self.assertEqual(base, unpacked)
            bigpacked = struct.pack(">f", smaller)
            self.assertEqual(bigpacked, string_reverse(packed))
            unpacked = struct.unpack(">f", bigpacked)[0]
            self.assertEqual(base, unpacked)

        # Largest finite IEEE single.
        big = (1 << 24) - 1
        big = math.ldexp(big, 127 - 23)
        packed = struct.pack(">f", big)
        unpacked = struct.unpack(">f", packed)[0]
        self.assertEqual(big, unpacked)

        # The same, but tack on a 1 bit so it rounds up to infinity.
        big = (1 << 25) - 1
        big = math.ldexp(big, 127 - 24)
        self.assertRaises(OverflowError, struct.pack, ">f", big)

    eleza test_1530559(self):
        kila code, byteorder kwenye iter_integer_formats():
            format = byteorder + code
            self.assertRaises(struct.error, struct.pack, format, 1.0)
            self.assertRaises(struct.error, struct.pack, format, 1.5)
        self.assertRaises(struct.error, struct.pack, 'P', 1.0)
        self.assertRaises(struct.error, struct.pack, 'P', 1.5)

    eleza test_unpack_from(self):
        test_string = b'abcd01234'
        fmt = '4s'
        s = struct.Struct(fmt)
        kila cls kwenye (bytes, bytearray):
            data = cls(test_string)
            self.assertEqual(s.unpack_from(data), (b'abcd',))
            self.assertEqual(s.unpack_from(data, 2), (b'cd01',))
            self.assertEqual(s.unpack_from(data, 4), (b'0123',))
            kila i kwenye range(6):
                self.assertEqual(s.unpack_from(data, i), (data[i:i+4],))
            kila i kwenye range(6, len(test_string) + 1):
                self.assertRaises(struct.error, s.unpack_from, data, i)
        kila cls kwenye (bytes, bytearray):
            data = cls(test_string)
            self.assertEqual(struct.unpack_from(fmt, data), (b'abcd',))
            self.assertEqual(struct.unpack_from(fmt, data, 2), (b'cd01',))
            self.assertEqual(struct.unpack_from(fmt, data, 4), (b'0123',))
            kila i kwenye range(6):
                self.assertEqual(struct.unpack_from(fmt, data, i), (data[i:i+4],))
            kila i kwenye range(6, len(test_string) + 1):
                self.assertRaises(struct.error, struct.unpack_from, fmt, data, i)

        # keyword arguments
        self.assertEqual(s.unpack_from(buffer=test_string, offset=2),
                         (b'cd01',))

    eleza test_pack_into(self):
        test_string = b'Reykjavik rocks, eow!'
        writable_buf = array.array('b', b' '*100)
        fmt = '21s'
        s = struct.Struct(fmt)

        # Test without offset
        s.pack_into(writable_buf, 0, test_string)
        from_buf = writable_buf.tobytes()[:len(test_string)]
        self.assertEqual(from_buf, test_string)

        # Test ukijumuisha offset.
        s.pack_into(writable_buf, 10, test_string)
        from_buf = writable_buf.tobytes()[:len(test_string)+10]
        self.assertEqual(from_buf, test_string[:10] + test_string)

        # Go beyond boundaries.
        small_buf = array.array('b', b' '*10)
        self.assertRaises((ValueError, struct.error), s.pack_into, small_buf, 0,
                          test_string)
        self.assertRaises((ValueError, struct.error), s.pack_into, small_buf, 2,
                          test_string)

        # Test bogus offset (issue 3694)
        sb = small_buf
        self.assertRaises((TypeError, struct.error), struct.pack_into, b'', sb,
                          Tupu)

    eleza test_pack_into_fn(self):
        test_string = b'Reykjavik rocks, eow!'
        writable_buf = array.array('b', b' '*100)
        fmt = '21s'
        pack_into = lambda *args: struct.pack_into(fmt, *args)

        # Test without offset.
        pack_into(writable_buf, 0, test_string)
        from_buf = writable_buf.tobytes()[:len(test_string)]
        self.assertEqual(from_buf, test_string)

        # Test ukijumuisha offset.
        pack_into(writable_buf, 10, test_string)
        from_buf = writable_buf.tobytes()[:len(test_string)+10]
        self.assertEqual(from_buf, test_string[:10] + test_string)

        # Go beyond boundaries.
        small_buf = array.array('b', b' '*10)
        self.assertRaises((ValueError, struct.error), pack_into, small_buf, 0,
                          test_string)
        self.assertRaises((ValueError, struct.error), pack_into, small_buf, 2,
                          test_string)

    eleza test_unpack_with_buffer(self):
        # SF bug 1563759: struct.unpack doesn't support buffer protocol objects
        data1 = array.array('B', b'\x12\x34\x56\x78')
        data2 = memoryview(b'\x12\x34\x56\x78') # XXX b'......XXXX......', 6, 4
        kila data kwenye [data1, data2]:
            value, = struct.unpack('>I', data)
            self.assertEqual(value, 0x12345678)

    eleza test_bool(self):
        kundi ExplodingBool(object):
            eleza __bool__(self):
                ashiria OSError
        kila prefix kwenye tuple("<>!=")+('',):
            false = (), [], [], '', 0
            true = [1], 'test', 5, -1, 0xffffffff+1, 0xffffffff/2

            falseFormat = prefix + '?' * len(false)
            packedUongo = struct.pack(falseFormat, *false)
            unpackedUongo = struct.unpack(falseFormat, packedUongo)

            trueFormat = prefix + '?' * len(true)
            packedKweli = struct.pack(trueFormat, *true)
            unpackedKweli = struct.unpack(trueFormat, packedKweli)

            self.assertEqual(len(true), len(unpackedKweli))
            self.assertEqual(len(false), len(unpackedUongo))

            kila t kwenye unpackedUongo:
                self.assertUongo(t)
            kila t kwenye unpackedKweli:
                self.assertKweli(t)

            packed = struct.pack(prefix+'?', 1)

            self.assertEqual(len(packed), struct.calcsize(prefix+'?'))

            ikiwa len(packed) != 1:
                self.assertUongo(prefix, msg='encoded bool ni sio one byte: %r'
                                             %packed)

            jaribu:
                struct.pack(prefix + '?', ExplodingBool())
            tatizo OSError:
                pita
            isipokua:
                self.fail("Expected OSError: struct.pack(%r, "
                          "ExplodingBool())" % (prefix + '?'))

        kila c kwenye [b'\x01', b'\x7f', b'\xff', b'\x0f', b'\xf0']:
            self.assertKweli(struct.unpack('>?', c)[0])

    eleza test_count_overflow(self):
        hugecount = '{}b'.format(sys.maxsize+1)
        self.assertRaises(struct.error, struct.calcsize, hugecount)

        hugecount2 = '{}b{}H'.format(sys.maxsize//2, sys.maxsize//2)
        self.assertRaises(struct.error, struct.calcsize, hugecount2)

    eleza test_trailing_counter(self):
        store = array.array('b', b' '*100)

        # format lists containing only count spec should result kwenye an error
        self.assertRaises(struct.error, struct.pack, '12345')
        self.assertRaises(struct.error, struct.unpack, '12345', b'')
        self.assertRaises(struct.error, struct.pack_into, '12345', store, 0)
        self.assertRaises(struct.error, struct.unpack_from, '12345', store, 0)

        # Format lists ukijumuisha trailing count spec should result kwenye an error
        self.assertRaises(struct.error, struct.pack, 'c12345', 'x')
        self.assertRaises(struct.error, struct.unpack, 'c12345', b'x')
        self.assertRaises(struct.error, struct.pack_into, 'c12345', store, 0,
                           'x')
        self.assertRaises(struct.error, struct.unpack_from, 'c12345', store,
                           0)

        # Mixed format tests
        self.assertRaises(struct.error, struct.pack, '14s42', 'spam na eggs')
        self.assertRaises(struct.error, struct.unpack, '14s42',
                          b'spam na eggs')
        self.assertRaises(struct.error, struct.pack_into, '14s42', store, 0,
                          'spam na eggs')
        self.assertRaises(struct.error, struct.unpack_from, '14s42', store, 0)

    eleza test_Struct_reinitialization(self):
        # Issue 9422: there was a memory leak when reinitializing a
        # Struct instance.  This test can be used to detect the leak
        # when running ukijumuisha regrtest -L.
        s = struct.Struct('i')
        s.__init__('ii')

    eleza check_sizeof(self, format_str, number_of_codes):
        # The size of 'PyStructObject'
        totalsize = support.calcobjsize('2n3P')
        # The size taken up by the 'formatcode' dynamic array
        totalsize += struct.calcsize('P3n0P') * (number_of_codes + 1)
        support.check_sizeof(self, struct.Struct(format_str), totalsize)

    @support.cpython_only
    eleza test__sizeof__(self):
        kila code kwenye integer_codes:
            self.check_sizeof(code, 1)
        self.check_sizeof('BHILfdspP', 9)
        self.check_sizeof('B' * 1234, 1234)
        self.check_sizeof('fd', 2)
        self.check_sizeof('xxxxxxxxxxxxxx', 0)
        self.check_sizeof('100H', 1)
        self.check_sizeof('187s', 1)
        self.check_sizeof('20p', 1)
        self.check_sizeof('0s', 1)
        self.check_sizeof('0c', 0)

    eleza test_boundary_error_message(self):
        regex1 = (
            r'pack_into requires a buffer of at least 6 '
            r'bytes kila packing 1 bytes at offset 5 '
            r'\(actual buffer size ni 1\)'
        )
        ukijumuisha self.assertRaisesRegex(struct.error, regex1):
            struct.pack_into('b', bytearray(1), 5, 1)

        regex2 = (
            r'unpack_kutoka requires a buffer of at least 6 '
            r'bytes kila unpacking 1 bytes at offset 5 '
            r'\(actual buffer size ni 1\)'
        )
        ukijumuisha self.assertRaisesRegex(struct.error, regex2):
            struct.unpack_from('b', bytearray(1), 5)

    eleza test_boundary_error_message_with_negative_offset(self):
        byte_list = bytearray(10)
        ukijumuisha self.assertRaisesRegex(
                struct.error,
                r'no space to pack 4 bytes at offset -2'):
            struct.pack_into('<I', byte_list, -2, 123)

        ukijumuisha self.assertRaisesRegex(
                struct.error,
                'offset -11 out of range kila 10-byte buffer'):
            struct.pack_into('<B', byte_list, -11, 123)

        ukijumuisha self.assertRaisesRegex(
                struct.error,
                r'sio enough data to unpack 4 bytes at offset -2'):
            struct.unpack_from('<I', byte_list, -2)

        ukijumuisha self.assertRaisesRegex(
                struct.error,
                "offset -11 out of range kila 10-byte buffer"):
            struct.unpack_from('<B', byte_list, -11)

    eleza test_boundary_error_message_with_large_offset(self):
        # Test overflows cause by large offset na value size (issue 30245)
        regex1 = (
            r'pack_into requires a buffer of at least ' + str(sys.maxsize + 4) +
            r' bytes kila packing 4 bytes at offset ' + str(sys.maxsize) +
            r' \(actual buffer size ni 10\)'
        )
        ukijumuisha self.assertRaisesRegex(struct.error, regex1):
            struct.pack_into('<I', bytearray(10), sys.maxsize, 1)

        regex2 = (
            r'unpack_kutoka requires a buffer of at least ' + str(sys.maxsize + 4) +
            r' bytes kila unpacking 4 bytes at offset ' + str(sys.maxsize) +
            r' \(actual buffer size ni 10\)'
        )
        ukijumuisha self.assertRaisesRegex(struct.error, regex2):
            struct.unpack_from('<I', bytearray(10), sys.maxsize)

    eleza test_issue29802(self):
        # When the second argument of struct.unpack() was of wrong type
        # the Struct object was decrefed twice na the reference to
        # deallocated object was left kwenye a cache.
        ukijumuisha self.assertRaises(TypeError):
            struct.unpack('b', 0)
        # Shouldn't crash.
        self.assertEqual(struct.unpack('b', b'a'), (b'a'[0],))

    eleza test_format_attr(self):
        s = struct.Struct('=i2H')
        self.assertEqual(s.format, '=i2H')

        # use a bytes string
        s2 = struct.Struct(s.format.encode())
        self.assertEqual(s2.format, s.format)


kundi UnpackIteratorTest(unittest.TestCase):
    """
    Tests kila iterative unpacking (struct.Struct.iter_unpack).
    """

    eleza test_construct(self):
        eleza _check_iterator(it):
            self.assertIsInstance(it, abc.Iterator)
            self.assertIsInstance(it, abc.Iterable)
        s = struct.Struct('>ibcp')
        it = s.iter_unpack(b"")
        _check_iterator(it)
        it = s.iter_unpack(b"1234567")
        _check_iterator(it)
        # Wrong bytes length
        ukijumuisha self.assertRaises(struct.error):
            s.iter_unpack(b"123456")
        ukijumuisha self.assertRaises(struct.error):
            s.iter_unpack(b"12345678")
        # Zero-length struct
        s = struct.Struct('>')
        ukijumuisha self.assertRaises(struct.error):
            s.iter_unpack(b"")
        ukijumuisha self.assertRaises(struct.error):
            s.iter_unpack(b"12")

    eleza test_iterate(self):
        s = struct.Struct('>IB')
        b = bytes(range(1, 16))
        it = s.iter_unpack(b)
        self.assertEqual(next(it), (0x01020304, 5))
        self.assertEqual(next(it), (0x06070809, 10))
        self.assertEqual(next(it), (0x0b0c0d0e, 15))
        self.assertRaises(StopIteration, next, it)
        self.assertRaises(StopIteration, next, it)

    eleza test_arbitrary_buffer(self):
        s = struct.Struct('>IB')
        b = bytes(range(1, 11))
        it = s.iter_unpack(memoryview(b))
        self.assertEqual(next(it), (0x01020304, 5))
        self.assertEqual(next(it), (0x06070809, 10))
        self.assertRaises(StopIteration, next, it)
        self.assertRaises(StopIteration, next, it)

    eleza test_length_hint(self):
        lh = operator.length_hint
        s = struct.Struct('>IB')
        b = bytes(range(1, 16))
        it = s.iter_unpack(b)
        self.assertEqual(lh(it), 3)
        next(it)
        self.assertEqual(lh(it), 2)
        next(it)
        self.assertEqual(lh(it), 1)
        next(it)
        self.assertEqual(lh(it), 0)
        self.assertRaises(StopIteration, next, it)
        self.assertEqual(lh(it), 0)

    eleza test_module_func(self):
        # Sanity check kila the global struct.iter_unpack()
        it = struct.iter_unpack('>IB', bytes(range(1, 11)))
        self.assertEqual(next(it), (0x01020304, 5))
        self.assertEqual(next(it), (0x06070809, 10))
        self.assertRaises(StopIteration, next, it)
        self.assertRaises(StopIteration, next, it)

    eleza test_half_float(self):
        # Little-endian examples from:
        # http://en.wikipedia.org/wiki/Half_precision_floating-point_format
        format_bits_float__cleanRoundtrip_list = [
            (b'\x00\x3c', 1.0),
            (b'\x00\xc0', -2.0),
            (b'\xff\x7b', 65504.0), #  (max half precision)
            (b'\x00\x04', 2**-14), # ~= 6.10352 * 10**-5 (min pos normal)
            (b'\x01\x00', 2**-24), # ~= 5.96046 * 10**-8 (min pos subnormal)
            (b'\x00\x00', 0.0),
            (b'\x00\x80', -0.0),
            (b'\x00\x7c', float('+inf')),
            (b'\x00\xfc', float('-inf')),
            (b'\x55\x35', 0.333251953125), # ~= 1/3
        ]

        kila le_bits, f kwenye format_bits_float__cleanRoundtrip_list:
            be_bits = le_bits[::-1]
            self.assertEqual(f, struct.unpack('<e', le_bits)[0])
            self.assertEqual(le_bits, struct.pack('<e', f))
            self.assertEqual(f, struct.unpack('>e', be_bits)[0])
            self.assertEqual(be_bits, struct.pack('>e', f))
            ikiwa sys.byteorder == 'little':
                self.assertEqual(f, struct.unpack('e', le_bits)[0])
                self.assertEqual(le_bits, struct.pack('e', f))
            isipokua:
                self.assertEqual(f, struct.unpack('e', be_bits)[0])
                self.assertEqual(be_bits, struct.pack('e', f))

        # Check kila NaN handling:
        format_bits__nan_list = [
            ('<e', b'\x01\xfc'),
            ('<e', b'\x00\xfe'),
            ('<e', b'\xff\xff'),
            ('<e', b'\x01\x7c'),
            ('<e', b'\x00\x7e'),
            ('<e', b'\xff\x7f'),
        ]

        kila formatcode, bits kwenye format_bits__nan_list:
            self.assertKweli(math.isnan(struct.unpack('<e', bits)[0]))
            self.assertKweli(math.isnan(struct.unpack('>e', bits[::-1])[0]))

        # Check that packing produces a bit pattern representing a quiet NaN:
        # all exponent bits na the msb of the fraction should all be 1.
        packed = struct.pack('<e', math.nan)
        self.assertEqual(packed[1] & 0x7e, 0x7e)
        packed = struct.pack('<e', -math.nan)
        self.assertEqual(packed[1] & 0x7e, 0x7e)

        # Checks kila round-to-even behavior
        format_bits_float__rounding_list = [
            ('>e', b'\x00\x01', 2.0**-25 + 2.0**-35), # Rounds to minimum subnormal
            ('>e', b'\x00\x00', 2.0**-25), # Underflows to zero (nearest even mode)
            ('>e', b'\x00\x00', 2.0**-26), # Underflows to zero
            ('>e', b'\x03\xff', 2.0**-14 - 2.0**-24), # Largest subnormal.
            ('>e', b'\x03\xff', 2.0**-14 - 2.0**-25 - 2.0**-65),
            ('>e', b'\x04\x00', 2.0**-14 - 2.0**-25),
            ('>e', b'\x04\x00', 2.0**-14), # Smallest normal.
            ('>e', b'\x3c\x01', 1.0+2.0**-11 + 2.0**-16), # rounds to 1.0+2**(-10)
            ('>e', b'\x3c\x00', 1.0+2.0**-11), # rounds to 1.0 (nearest even mode)
            ('>e', b'\x3c\x00', 1.0+2.0**-12), # rounds to 1.0
            ('>e', b'\x7b\xff', 65504), # largest normal
            ('>e', b'\x7b\xff', 65519), # rounds to 65504
            ('>e', b'\x80\x01', -2.0**-25 - 2.0**-35), # Rounds to minimum subnormal
            ('>e', b'\x80\x00', -2.0**-25), # Underflows to zero (nearest even mode)
            ('>e', b'\x80\x00', -2.0**-26), # Underflows to zero
            ('>e', b'\xbc\x01', -1.0-2.0**-11 - 2.0**-16), # rounds to 1.0+2**(-10)
            ('>e', b'\xbc\x00', -1.0-2.0**-11), # rounds to 1.0 (nearest even mode)
            ('>e', b'\xbc\x00', -1.0-2.0**-12), # rounds to 1.0
            ('>e', b'\xfb\xff', -65519), # rounds to 65504
        ]

        kila formatcode, bits, f kwenye format_bits_float__rounding_list:
            self.assertEqual(bits, struct.pack(formatcode, f))

        # This overflows, na so raises an error
        format_bits_float__roundingError_list = [
            # Values that round to infinity.
            ('>e', 65520.0),
            ('>e', 65536.0),
            ('>e', 1e300),
            ('>e', -65520.0),
            ('>e', -65536.0),
            ('>e', -1e300),
            ('<e', 65520.0),
            ('<e', 65536.0),
            ('<e', 1e300),
            ('<e', -65520.0),
            ('<e', -65536.0),
            ('<e', -1e300),
        ]

        kila formatcode, f kwenye format_bits_float__roundingError_list:
            self.assertRaises(OverflowError, struct.pack, formatcode, f)

        # Double rounding
        format_bits_float__doubleRoundingError_list = [
            ('>e', b'\x67\xff', 0x1ffdffffff * 2**-26), # should be 2047, ikiwa double-rounded 64>32>16, becomes 2048
        ]

        kila formatcode, bits, f kwenye format_bits_float__doubleRoundingError_list:
            self.assertEqual(bits, struct.pack(formatcode, f))


ikiwa __name__ == '__main__':
    unittest.main()
