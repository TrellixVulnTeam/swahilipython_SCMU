"""Unit tests kila the bytes na bytearray types.

XXX This ni a mess.  Common tests should be unified ukijumuisha string_tests.py (and
the latter should be modernized).
"""

agiza array
agiza os
agiza re
agiza sys
agiza copy
agiza functools
agiza pickle
agiza tempfile
agiza unittest

agiza test.support
agiza test.string_tests
agiza test.list_tests
kutoka test.support agiza bigaddrspacetest, MAX_Py_ssize_t


ikiwa sys.flags.bytes_warning:
    eleza check_bytes_warnings(func):
        @functools.wraps(func)
        eleza wrapper(*args, **kw):
            ukijumuisha test.support.check_warnings(('', BytesWarning)):
                rudisha func(*args, **kw)
        rudisha wrapper
isipokua:
    # no-op
    eleza check_bytes_warnings(func):
        rudisha func


kundi Indexable:
    eleza __init__(self, value=0):
        self.value = value
    eleza __index__(self):
        rudisha self.value


kundi BaseBytesTest:

    eleza test_basics(self):
        b = self.type2test()
        self.assertEqual(type(b), self.type2test)
        self.assertEqual(b.__class__, self.type2test)

    eleza test_copy(self):
        a = self.type2test(b"abcd")
        kila copy_method kwenye (copy.copy, copy.deepcopy):
            b = copy_method(a)
            self.assertEqual(a, b)
            self.assertEqual(type(a), type(b))

    eleza test_empty_sequence(self):
        b = self.type2test()
        self.assertEqual(len(b), 0)
        self.assertRaises(IndexError, lambda: b[0])
        self.assertRaises(IndexError, lambda: b[1])
        self.assertRaises(IndexError, lambda: b[sys.maxsize])
        self.assertRaises(IndexError, lambda: b[sys.maxsize+1])
        self.assertRaises(IndexError, lambda: b[10**100])
        self.assertRaises(IndexError, lambda: b[-1])
        self.assertRaises(IndexError, lambda: b[-2])
        self.assertRaises(IndexError, lambda: b[-sys.maxsize])
        self.assertRaises(IndexError, lambda: b[-sys.maxsize-1])
        self.assertRaises(IndexError, lambda: b[-sys.maxsize-2])
        self.assertRaises(IndexError, lambda: b[-10**100])

    eleza test_from_iterable(self):
        b = self.type2test(range(256))
        self.assertEqual(len(b), 256)
        self.assertEqual(list(b), list(range(256)))

        # Non-sequence iterable.
        b = self.type2test({42})
        self.assertEqual(b, b"*")
        b = self.type2test({43, 45})
        self.assertIn(tuple(b), {(43, 45), (45, 43)})

        # Iterator that has a __length_hint__.
        b = self.type2test(iter(range(256)))
        self.assertEqual(len(b), 256)
        self.assertEqual(list(b), list(range(256)))

        # Iterator that doesn't have a __length_hint__.
        b = self.type2test(i kila i kwenye range(256) ikiwa i % 2)
        self.assertEqual(len(b), 128)
        self.assertEqual(list(b), list(range(256))[1::2])

        # Sequence without __iter__.
        kundi S:
            eleza __getitem__(self, i):
                rudisha (1, 2, 3)[i]
        b = self.type2test(S())
        self.assertEqual(b, b"\x01\x02\x03")

    eleza test_from_tuple(self):
        # There ni a special case kila tuples.
        b = self.type2test(tuple(range(256)))
        self.assertEqual(len(b), 256)
        self.assertEqual(list(b), list(range(256)))
        b = self.type2test((1, 2, 3))
        self.assertEqual(b, b"\x01\x02\x03")

    eleza test_from_list(self):
        # There ni a special case kila lists.
        b = self.type2test(list(range(256)))
        self.assertEqual(len(b), 256)
        self.assertEqual(list(b), list(range(256)))
        b = self.type2test([1, 2, 3])
        self.assertEqual(b, b"\x01\x02\x03")

    eleza test_from_mutating_list(self):
        # Issue #34973: Crash kwenye bytes constructor ukijumuisha mutating list.
        kundi X:
            eleza __index__(self):
                a.clear()
                rudisha 42
        a = [X(), X()]
        self.assertEqual(bytes(a), b'*')

        kundi Y:
            eleza __index__(self):
                ikiwa len(a) < 1000:
                    a.append(self)
                rudisha 42
        a = [Y()]
        self.assertEqual(bytes(a), b'*' * 1000)  # should sio crash

    eleza test_from_index(self):
        b = self.type2test([Indexable(), Indexable(1), Indexable(254),
                            Indexable(255)])
        self.assertEqual(list(b), [0, 1, 254, 255])
        self.assertRaises(ValueError, self.type2test, [Indexable(-1)])
        self.assertRaises(ValueError, self.type2test, [Indexable(256)])

    eleza test_from_buffer(self):
        a = self.type2test(array.array('B', [1, 2, 3]))
        self.assertEqual(a, b"\x01\x02\x03")
        a = self.type2test(b"\x01\x02\x03")
        self.assertEqual(a, b"\x01\x02\x03")

        # Issues #29159 na #34974.
        # Fallback when __index__ raises a TypeError
        kundi B(bytes):
            eleza __index__(self):
                ashiria TypeError

        self.assertEqual(self.type2test(B(b"foobar")), b"foobar")

    eleza test_from_ssize(self):
        self.assertEqual(self.type2test(0), b'')
        self.assertEqual(self.type2test(1), b'\x00')
        self.assertEqual(self.type2test(5), b'\x00\x00\x00\x00\x00')
        self.assertRaises(ValueError, self.type2test, -1)

        self.assertEqual(self.type2test('0', 'ascii'), b'0')
        self.assertEqual(self.type2test(b'0'), b'0')
        self.assertRaises(OverflowError, self.type2test, sys.maxsize + 1)

    eleza test_constructor_type_errors(self):
        self.assertRaises(TypeError, self.type2test, 0.0)
        kundi C:
            pita
        self.assertRaises(TypeError, self.type2test, ["0"])
        self.assertRaises(TypeError, self.type2test, [0.0])
        self.assertRaises(TypeError, self.type2test, [Tupu])
        self.assertRaises(TypeError, self.type2test, [C()])
        self.assertRaises(TypeError, self.type2test, encoding='ascii')
        self.assertRaises(TypeError, self.type2test, errors='ignore')
        self.assertRaises(TypeError, self.type2test, 0, 'ascii')
        self.assertRaises(TypeError, self.type2test, b'', 'ascii')
        self.assertRaises(TypeError, self.type2test, 0, errors='ignore')
        self.assertRaises(TypeError, self.type2test, b'', errors='ignore')
        self.assertRaises(TypeError, self.type2test, '')
        self.assertRaises(TypeError, self.type2test, '', errors='ignore')
        self.assertRaises(TypeError, self.type2test, '', b'ascii')
        self.assertRaises(TypeError, self.type2test, '', 'ascii', b'ignore')

    eleza test_constructor_value_errors(self):
        self.assertRaises(ValueError, self.type2test, [-1])
        self.assertRaises(ValueError, self.type2test, [-sys.maxsize])
        self.assertRaises(ValueError, self.type2test, [-sys.maxsize-1])
        self.assertRaises(ValueError, self.type2test, [-sys.maxsize-2])
        self.assertRaises(ValueError, self.type2test, [-10**100])
        self.assertRaises(ValueError, self.type2test, [256])
        self.assertRaises(ValueError, self.type2test, [257])
        self.assertRaises(ValueError, self.type2test, [sys.maxsize])
        self.assertRaises(ValueError, self.type2test, [sys.maxsize+1])
        self.assertRaises(ValueError, self.type2test, [10**100])

    @bigaddrspacetest
    eleza test_constructor_overflow(self):
        size = MAX_Py_ssize_t
        self.assertRaises((OverflowError, MemoryError), self.type2test, size)
        jaribu:
            # Should either pita ama ashiria an error (e.g. on debug builds with
            # additional malloc() overhead), but shouldn't crash.
            bytearray(size - 4)
        tatizo (OverflowError, MemoryError):
            pita

    eleza test_constructor_exceptions(self):
        # Issue #34974: bytes na bytearray constructors replace unexpected
        # exceptions.
        kundi BadInt:
            eleza __index__(self):
                1/0
        self.assertRaises(ZeroDivisionError, self.type2test, BadInt())
        self.assertRaises(ZeroDivisionError, self.type2test, [BadInt()])

        kundi BadIterable:
            eleza __iter__(self):
                1/0
        self.assertRaises(ZeroDivisionError, self.type2test, BadIterable())

    eleza test_compare(self):
        b1 = self.type2test([1, 2, 3])
        b2 = self.type2test([1, 2, 3])
        b3 = self.type2test([1, 3])

        self.assertEqual(b1, b2)
        self.assertKweli(b2 != b3)
        self.assertKweli(b1 <= b2)
        self.assertKweli(b1 <= b3)
        self.assertKweli(b1 <  b3)
        self.assertKweli(b1 >= b2)
        self.assertKweli(b3 >= b2)
        self.assertKweli(b3 >  b2)

        self.assertUongo(b1 != b2)
        self.assertUongo(b2 == b3)
        self.assertUongo(b1 >  b2)
        self.assertUongo(b1 >  b3)
        self.assertUongo(b1 >= b3)
        self.assertUongo(b1 <  b2)
        self.assertUongo(b3 <  b2)
        self.assertUongo(b3 <= b2)

    @check_bytes_warnings
    eleza test_compare_to_str(self):
        # Byte comparisons ukijumuisha unicode should always fail!
        # Test this kila all expected byte orders na Unicode character
        # sizes.
        self.assertEqual(self.type2test(b"\0a\0b\0c") == "abc", Uongo)
        self.assertEqual(self.type2test(b"\0\0\0a\0\0\0b\0\0\0c") == "abc",
                            Uongo)
        self.assertEqual(self.type2test(b"a\0b\0c\0") == "abc", Uongo)
        self.assertEqual(self.type2test(b"a\0\0\0b\0\0\0c\0\0\0") == "abc",
                            Uongo)
        self.assertEqual(self.type2test() == str(), Uongo)
        self.assertEqual(self.type2test() != str(), Kweli)

    eleza test_reversed(self):
        input = list(map(ord, "Hello"))
        b = self.type2test(input)
        output = list(reversed(b))
        input.reverse()
        self.assertEqual(output, input)

    eleza test_getslice(self):
        eleza by(s):
            rudisha self.type2test(map(ord, s))
        b = by("Hello, world")

        self.assertEqual(b[:5], by("Hello"))
        self.assertEqual(b[1:5], by("ello"))
        self.assertEqual(b[5:7], by(", "))
        self.assertEqual(b[7:], by("world"))
        self.assertEqual(b[7:12], by("world"))
        self.assertEqual(b[7:100], by("world"))

        self.assertEqual(b[:-7], by("Hello"))
        self.assertEqual(b[-11:-7], by("ello"))
        self.assertEqual(b[-7:-5], by(", "))
        self.assertEqual(b[-5:], by("world"))
        self.assertEqual(b[-5:12], by("world"))
        self.assertEqual(b[-5:100], by("world"))
        self.assertEqual(b[-100:5], by("Hello"))

    eleza test_extended_getslice(self):
        # Test extended slicing by comparing ukijumuisha list slicing.
        L = list(range(255))
        b = self.type2test(L)
        indices = (0, Tupu, 1, 3, 19, 100, sys.maxsize, -1, -2, -31, -100)
        kila start kwenye indices:
            kila stop kwenye indices:
                # Skip step 0 (invalid)
                kila step kwenye indices[1:]:
                    self.assertEqual(b[start:stop:step], self.type2test(L[start:stop:step]))

    eleza test_encoding(self):
        sample = "Hello world\n\u1234\u5678\u9abc"
        kila enc kwenye ("utf-8", "utf-16"):
            b = self.type2test(sample, enc)
            self.assertEqual(b, self.type2test(sample.encode(enc)))
        self.assertRaises(UnicodeEncodeError, self.type2test, sample, "latin-1")
        b = self.type2test(sample, "latin-1", "ignore")
        self.assertEqual(b, self.type2test(sample[:-3], "utf-8"))

    eleza test_decode(self):
        sample = "Hello world\n\u1234\u5678\u9abc"
        kila enc kwenye ("utf-8", "utf-16"):
            b = self.type2test(sample, enc)
            self.assertEqual(b.decode(enc), sample)
        sample = "Hello world\n\x80\x81\xfe\xff"
        b = self.type2test(sample, "latin-1")
        self.assertRaises(UnicodeDecodeError, b.decode, "utf-8")
        self.assertEqual(b.decode("utf-8", "ignore"), "Hello world\n")
        self.assertEqual(b.decode(errors="ignore", encoding="utf-8"),
                         "Hello world\n")
        # Default encoding ni utf-8
        self.assertEqual(self.type2test(b'\xe2\x98\x83').decode(), '\u2603')

    eleza test_from_int(self):
        b = self.type2test(0)
        self.assertEqual(b, self.type2test())
        b = self.type2test(10)
        self.assertEqual(b, self.type2test([0]*10))
        b = self.type2test(10000)
        self.assertEqual(b, self.type2test([0]*10000))

    eleza test_concat(self):
        b1 = self.type2test(b"abc")
        b2 = self.type2test(b"def")
        self.assertEqual(b1 + b2, b"abcdef")
        self.assertEqual(b1 + bytes(b"def"), b"abcdef")
        self.assertEqual(bytes(b"def") + b1, b"defabc")
        self.assertRaises(TypeError, lambda: b1 + "def")
        self.assertRaises(TypeError, lambda: "abc" + b2)

    eleza test_repeat(self):
        kila b kwenye b"abc", self.type2test(b"abc"):
            self.assertEqual(b * 3, b"abcabcabc")
            self.assertEqual(b * 0, b"")
            self.assertEqual(b * -1, b"")
            self.assertRaises(TypeError, lambda: b * 3.14)
            self.assertRaises(TypeError, lambda: 3.14 * b)
            # XXX Shouldn't bytes na bytearray agree on what to raise?
            ukijumuisha self.assertRaises((OverflowError, MemoryError)):
                c = b * sys.maxsize
            ukijumuisha self.assertRaises((OverflowError, MemoryError)):
                b *= sys.maxsize

    eleza test_repeat_1char(self):
        self.assertEqual(self.type2test(b'x')*100, self.type2test([ord('x')]*100))

    eleza test_contains(self):
        b = self.type2test(b"abc")
        self.assertIn(ord('a'), b)
        self.assertIn(int(ord('a')), b)
        self.assertNotIn(200, b)
        self.assertRaises(ValueError, lambda: 300 kwenye b)
        self.assertRaises(ValueError, lambda: -1 kwenye b)
        self.assertRaises(ValueError, lambda: sys.maxsize+1 kwenye b)
        self.assertRaises(TypeError, lambda: Tupu kwenye b)
        self.assertRaises(TypeError, lambda: float(ord('a')) kwenye b)
        self.assertRaises(TypeError, lambda: "a" kwenye b)
        kila f kwenye bytes, bytearray:
            self.assertIn(f(b""), b)
            self.assertIn(f(b"a"), b)
            self.assertIn(f(b"b"), b)
            self.assertIn(f(b"c"), b)
            self.assertIn(f(b"ab"), b)
            self.assertIn(f(b"bc"), b)
            self.assertIn(f(b"abc"), b)
            self.assertNotIn(f(b"ac"), b)
            self.assertNotIn(f(b"d"), b)
            self.assertNotIn(f(b"dab"), b)
            self.assertNotIn(f(b"abd"), b)

    eleza test_fromhex(self):
        self.assertRaises(TypeError, self.type2test.fromhex)
        self.assertRaises(TypeError, self.type2test.fromhex, 1)
        self.assertEqual(self.type2test.fromhex(''), self.type2test())
        b = bytearray([0x1a, 0x2b, 0x30])
        self.assertEqual(self.type2test.fromhex('1a2B30'), b)
        self.assertEqual(self.type2test.fromhex('  1A 2B  30   '), b)

        # check that ASCII whitespace ni ignored
        self.assertEqual(self.type2test.fromhex(' 1A\n2B\t30\v'), b)
        kila c kwenye "\x09\x0A\x0B\x0C\x0D\x20":
            self.assertEqual(self.type2test.fromhex(c), self.type2test())
        kila c kwenye "\x1C\x1D\x1E\x1F\x85\xa0\u2000\u2002\u2028":
            self.assertRaises(ValueError, self.type2test.fromhex, c)

        self.assertEqual(self.type2test.fromhex('0000'), b'\0\0')
        self.assertRaises(TypeError, self.type2test.fromhex, b'1B')
        self.assertRaises(ValueError, self.type2test.fromhex, 'a')
        self.assertRaises(ValueError, self.type2test.fromhex, 'rt')
        self.assertRaises(ValueError, self.type2test.fromhex, '1a b cd')
        self.assertRaises(ValueError, self.type2test.fromhex, '\x00')
        self.assertRaises(ValueError, self.type2test.fromhex, '12   \x00   34')

        kila data, pos kwenye (
            # invalid first hexadecimal character
            ('12 x4 56', 3),
            # invalid second hexadecimal character
            ('12 3x 56', 4),
            # two invalid hexadecimal characters
            ('12 xy 56', 3),
            # test non-ASCII string
            ('12 3\xff 56', 4),
        ):
            ukijumuisha self.assertRaises(ValueError) kama cm:
                self.type2test.fromhex(data)
            self.assertIn('at position %s' % pos, str(cm.exception))

    eleza test_hex(self):
        self.assertRaises(TypeError, self.type2test.hex)
        self.assertRaises(TypeError, self.type2test.hex, 1)
        self.assertEqual(self.type2test(b"").hex(), "")
        self.assertEqual(bytearray([0x1a, 0x2b, 0x30]).hex(), '1a2b30')
        self.assertEqual(self.type2test(b"\x1a\x2b\x30").hex(), '1a2b30')
        self.assertEqual(memoryview(b"\x1a\x2b\x30").hex(), '1a2b30')

    eleza test_hex_separator_basics(self):
        three_bytes = self.type2test(b'\xb9\x01\xef')
        self.assertEqual(three_bytes.hex(), 'b901ef')
        ukijumuisha self.assertRaises(ValueError):
            three_bytes.hex('')
        ukijumuisha self.assertRaises(ValueError):
            three_bytes.hex('xx')
        self.assertEqual(three_bytes.hex(':', 0), 'b901ef')
        ukijumuisha self.assertRaises(TypeError):
            three_bytes.hex(Tupu, 0)
        ukijumuisha self.assertRaises(ValueError):
            three_bytes.hex('\xff')
        ukijumuisha self.assertRaises(ValueError):
            three_bytes.hex(b'\xff')
        ukijumuisha self.assertRaises(ValueError):
            three_bytes.hex(b'\x80')
        ukijumuisha self.assertRaises(ValueError):
            three_bytes.hex(chr(0x100))
        self.assertEqual(three_bytes.hex(':', 0), 'b901ef')
        self.assertEqual(three_bytes.hex(b'\x00'), 'b9\x0001\x00ef')
        self.assertEqual(three_bytes.hex('\x00'), 'b9\x0001\x00ef')
        self.assertEqual(three_bytes.hex(b'\x7f'), 'b9\x7f01\x7fef')
        self.assertEqual(three_bytes.hex('\x7f'), 'b9\x7f01\x7fef')
        self.assertEqual(three_bytes.hex(':', 3), 'b901ef')
        self.assertEqual(three_bytes.hex(':', 4), 'b901ef')
        self.assertEqual(three_bytes.hex(':', -4), 'b901ef')
        self.assertEqual(three_bytes.hex(':'), 'b9:01:ef')
        self.assertEqual(three_bytes.hex(b'$'), 'b9$01$ef')
        self.assertEqual(three_bytes.hex(':', 1), 'b9:01:ef')
        self.assertEqual(three_bytes.hex(':', -1), 'b9:01:ef')
        self.assertEqual(three_bytes.hex(':', 2), 'b9:01ef')
        self.assertEqual(three_bytes.hex(':', 1), 'b9:01:ef')
        self.assertEqual(three_bytes.hex('*', -2), 'b901*ef')

        value = b'{s\005\000\000\000worldi\002\000\000\000s\005\000\000\000helloi\001\000\000\0000'
        self.assertEqual(value.hex('.', 8), '7b7305000000776f.726c646902000000.730500000068656c.6c6f690100000030')

    eleza test_hex_separator_five_bytes(self):
        five_bytes = self.type2test(range(90,95))
        self.assertEqual(five_bytes.hex(), '5a5b5c5d5e')

    eleza test_hex_separator_six_bytes(self):
        six_bytes = self.type2test(x*3 kila x kwenye range(1, 7))
        self.assertEqual(six_bytes.hex(), '0306090c0f12')
        self.assertEqual(six_bytes.hex('.', 1), '03.06.09.0c.0f.12')
        self.assertEqual(six_bytes.hex(' ', 2), '0306 090c 0f12')
        self.assertEqual(six_bytes.hex('-', 3), '030609-0c0f12')
        self.assertEqual(six_bytes.hex(':', 4), '0306:090c0f12')
        self.assertEqual(six_bytes.hex(':', 5), '03:06090c0f12')
        self.assertEqual(six_bytes.hex(':', 6), '0306090c0f12')
        self.assertEqual(six_bytes.hex(':', 95), '0306090c0f12')
        self.assertEqual(six_bytes.hex('_', -3), '030609_0c0f12')
        self.assertEqual(six_bytes.hex(':', -4), '0306090c:0f12')
        self.assertEqual(six_bytes.hex(b'@', -5), '0306090c0f@12')
        self.assertEqual(six_bytes.hex(':', -6), '0306090c0f12')
        self.assertEqual(six_bytes.hex(' ', -95), '0306090c0f12')

    eleza test_join(self):
        self.assertEqual(self.type2test(b"").join([]), b"")
        self.assertEqual(self.type2test(b"").join([b""]), b"")
        kila lst kwenye [[b"abc"], [b"a", b"bc"], [b"ab", b"c"], [b"a", b"b", b"c"]]:
            lst = list(map(self.type2test, lst))
            self.assertEqual(self.type2test(b"").join(lst), b"abc")
            self.assertEqual(self.type2test(b"").join(tuple(lst)), b"abc")
            self.assertEqual(self.type2test(b"").join(iter(lst)), b"abc")
        dot_join = self.type2test(b".:").join
        self.assertEqual(dot_join([b"ab", b"cd"]), b"ab.:cd")
        self.assertEqual(dot_join([memoryview(b"ab"), b"cd"]), b"ab.:cd")
        self.assertEqual(dot_join([b"ab", memoryview(b"cd")]), b"ab.:cd")
        self.assertEqual(dot_join([bytearray(b"ab"), b"cd"]), b"ab.:cd")
        self.assertEqual(dot_join([b"ab", bytearray(b"cd")]), b"ab.:cd")
        # Stress it ukijumuisha many items
        seq = [b"abc"] * 1000
        expected = b"abc" + b".:abc" * 999
        self.assertEqual(dot_join(seq), expected)
        self.assertRaises(TypeError, self.type2test(b" ").join, Tupu)
        # Error handling na cleanup when some item kwenye the middle of the
        # sequence has the wrong type.
        ukijumuisha self.assertRaises(TypeError):
            dot_join([bytearray(b"ab"), "cd", b"ef"])
        ukijumuisha self.assertRaises(TypeError):
            dot_join([memoryview(b"ab"), "cd", b"ef"])

    eleza test_count(self):
        b = self.type2test(b'mississippi')
        i = 105
        p = 112
        w = 119

        self.assertEqual(b.count(b'i'), 4)
        self.assertEqual(b.count(b'ss'), 2)
        self.assertEqual(b.count(b'w'), 0)

        self.assertEqual(b.count(i), 4)
        self.assertEqual(b.count(w), 0)

        self.assertEqual(b.count(b'i', 6), 2)
        self.assertEqual(b.count(b'p', 6), 2)
        self.assertEqual(b.count(b'i', 1, 3), 1)
        self.assertEqual(b.count(b'p', 7, 9), 1)

        self.assertEqual(b.count(i, 6), 2)
        self.assertEqual(b.count(p, 6), 2)
        self.assertEqual(b.count(i, 1, 3), 1)
        self.assertEqual(b.count(p, 7, 9), 1)

    eleza test_startswith(self):
        b = self.type2test(b'hello')
        self.assertUongo(self.type2test().startswith(b"anything"))
        self.assertKweli(b.startswith(b"hello"))
        self.assertKweli(b.startswith(b"hel"))
        self.assertKweli(b.startswith(b"h"))
        self.assertUongo(b.startswith(b"hellow"))
        self.assertUongo(b.startswith(b"ha"))
        ukijumuisha self.assertRaises(TypeError) kama cm:
            b.startswith([b'h'])
        exc = str(cm.exception)
        self.assertIn('bytes', exc)
        self.assertIn('tuple', exc)

    eleza test_endswith(self):
        b = self.type2test(b'hello')
        self.assertUongo(bytearray().endswith(b"anything"))
        self.assertKweli(b.endswith(b"hello"))
        self.assertKweli(b.endswith(b"llo"))
        self.assertKweli(b.endswith(b"o"))
        self.assertUongo(b.endswith(b"whello"))
        self.assertUongo(b.endswith(b"no"))
        ukijumuisha self.assertRaises(TypeError) kama cm:
            b.endswith([b'o'])
        exc = str(cm.exception)
        self.assertIn('bytes', exc)
        self.assertIn('tuple', exc)

    eleza test_find(self):
        b = self.type2test(b'mississippi')
        i = 105
        w = 119

        self.assertEqual(b.find(b'ss'), 2)
        self.assertEqual(b.find(b'w'), -1)
        self.assertEqual(b.find(b'mississippian'), -1)

        self.assertEqual(b.find(i), 1)
        self.assertEqual(b.find(w), -1)

        self.assertEqual(b.find(b'ss', 3), 5)
        self.assertEqual(b.find(b'ss', 1, 7), 2)
        self.assertEqual(b.find(b'ss', 1, 3), -1)

        self.assertEqual(b.find(i, 6), 7)
        self.assertEqual(b.find(i, 1, 3), 1)
        self.assertEqual(b.find(w, 1, 3), -1)

        kila index kwenye (-1, 256, sys.maxsize + 1):
            self.assertRaisesRegex(
                ValueError, r'byte must be kwenye range\(0, 256\)',
                b.find, index)

    eleza test_rfind(self):
        b = self.type2test(b'mississippi')
        i = 105
        w = 119

        self.assertEqual(b.rfind(b'ss'), 5)
        self.assertEqual(b.rfind(b'w'), -1)
        self.assertEqual(b.rfind(b'mississippian'), -1)

        self.assertEqual(b.rfind(i), 10)
        self.assertEqual(b.rfind(w), -1)

        self.assertEqual(b.rfind(b'ss', 3), 5)
        self.assertEqual(b.rfind(b'ss', 0, 6), 2)

        self.assertEqual(b.rfind(i, 1, 3), 1)
        self.assertEqual(b.rfind(i, 3, 9), 7)
        self.assertEqual(b.rfind(w, 1, 3), -1)

    eleza test_index(self):
        b = self.type2test(b'mississippi')
        i = 105
        w = 119

        self.assertEqual(b.index(b'ss'), 2)
        self.assertRaises(ValueError, b.index, b'w')
        self.assertRaises(ValueError, b.index, b'mississippian')

        self.assertEqual(b.index(i), 1)
        self.assertRaises(ValueError, b.index, w)

        self.assertEqual(b.index(b'ss', 3), 5)
        self.assertEqual(b.index(b'ss', 1, 7), 2)
        self.assertRaises(ValueError, b.index, b'ss', 1, 3)

        self.assertEqual(b.index(i, 6), 7)
        self.assertEqual(b.index(i, 1, 3), 1)
        self.assertRaises(ValueError, b.index, w, 1, 3)

    eleza test_rindex(self):
        b = self.type2test(b'mississippi')
        i = 105
        w = 119

        self.assertEqual(b.rindex(b'ss'), 5)
        self.assertRaises(ValueError, b.rindex, b'w')
        self.assertRaises(ValueError, b.rindex, b'mississippian')

        self.assertEqual(b.rindex(i), 10)
        self.assertRaises(ValueError, b.rindex, w)

        self.assertEqual(b.rindex(b'ss', 3), 5)
        self.assertEqual(b.rindex(b'ss', 0, 6), 2)

        self.assertEqual(b.rindex(i, 1, 3), 1)
        self.assertEqual(b.rindex(i, 3, 9), 7)
        self.assertRaises(ValueError, b.rindex, w, 1, 3)

    eleza test_mod(self):
        b = self.type2test(b'hello, %b!')
        orig = b
        b = b % b'world'
        self.assertEqual(b, b'hello, world!')
        self.assertEqual(orig, b'hello, %b!')
        self.assertUongo(b ni orig)
        b = self.type2test(b'%s / 100 = %d%%')
        a = b % (b'seventy-nine', 79)
        self.assertEqual(a, b'seventy-nine / 100 = 79%')
        self.assertIs(type(a), self.type2test)
        # issue 29714
        b = self.type2test(b'hello,\x00%b!')
        b = b % b'world'
        self.assertEqual(b, b'hello,\x00world!')
        self.assertIs(type(b), self.type2test)

    eleza test_imod(self):
        b = self.type2test(b'hello, %b!')
        orig = b
        b %= b'world'
        self.assertEqual(b, b'hello, world!')
        self.assertEqual(orig, b'hello, %b!')
        self.assertUongo(b ni orig)
        b = self.type2test(b'%s / 100 = %d%%')
        b %= (b'seventy-nine', 79)
        self.assertEqual(b, b'seventy-nine / 100 = 79%')
        self.assertIs(type(b), self.type2test)
        # issue 29714
        b = self.type2test(b'hello,\x00%b!')
        b %= b'world'
        self.assertEqual(b, b'hello,\x00world!')
        self.assertIs(type(b), self.type2test)

    eleza test_rmod(self):
        ukijumuisha self.assertRaises(TypeError):
            object() % self.type2test(b'abc')
        self.assertIs(self.type2test(b'abc').__rmod__('%r'), NotImplemented)

    eleza test_replace(self):
        b = self.type2test(b'mississippi')
        self.assertEqual(b.replace(b'i', b'a'), b'massassappa')
        self.assertEqual(b.replace(b'ss', b'x'), b'mixixippi')

    eleza test_replace_int_error(self):
        self.assertRaises(TypeError, self.type2test(b'a b').replace, 32, b'')

    eleza test_split_string_error(self):
        self.assertRaises(TypeError, self.type2test(b'a b').split, ' ')
        self.assertRaises(TypeError, self.type2test(b'a b').rsplit, ' ')

    eleza test_split_int_error(self):
        self.assertRaises(TypeError, self.type2test(b'a b').split, 32)
        self.assertRaises(TypeError, self.type2test(b'a b').rsplit, 32)

    eleza test_split_unicodewhitespace(self):
        kila b kwenye (b'a\x1Cb', b'a\x1Db', b'a\x1Eb', b'a\x1Fb'):
            b = self.type2test(b)
            self.assertEqual(b.split(), [b])
        b = self.type2test(b"\x09\x0A\x0B\x0C\x0D\x1C\x1D\x1E\x1F")
        self.assertEqual(b.split(), [b'\x1c\x1d\x1e\x1f'])

    eleza test_rsplit_unicodewhitespace(self):
        b = self.type2test(b"\x09\x0A\x0B\x0C\x0D\x1C\x1D\x1E\x1F")
        self.assertEqual(b.rsplit(), [b'\x1c\x1d\x1e\x1f'])

    eleza test_partition(self):
        b = self.type2test(b'mississippi')
        self.assertEqual(b.partition(b'ss'), (b'mi', b'ss', b'issippi'))
        self.assertEqual(b.partition(b'w'), (b'mississippi', b'', b''))

    eleza test_rpartition(self):
        b = self.type2test(b'mississippi')
        self.assertEqual(b.rpartition(b'ss'), (b'missi', b'ss', b'ippi'))
        self.assertEqual(b.rpartition(b'i'), (b'mississipp', b'i', b''))
        self.assertEqual(b.rpartition(b'w'), (b'', b'', b'mississippi'))

    eleza test_partition_string_error(self):
        self.assertRaises(TypeError, self.type2test(b'a b').partition, ' ')
        self.assertRaises(TypeError, self.type2test(b'a b').rpartition, ' ')

    eleza test_partition_int_error(self):
        self.assertRaises(TypeError, self.type2test(b'a b').partition, 32)
        self.assertRaises(TypeError, self.type2test(b'a b').rpartition, 32)

    eleza test_pickling(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            kila b kwenye b"", b"a", b"abc", b"\xffab\x80", b"\0\0\377\0\0":
                b = self.type2test(b)
                ps = pickle.dumps(b, proto)
                q = pickle.loads(ps)
                self.assertEqual(b, q)

    eleza test_iterator_pickling(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            kila b kwenye b"", b"a", b"abc", b"\xffab\x80", b"\0\0\377\0\0":
                it = itorg = iter(self.type2test(b))
                data = list(self.type2test(b))
                d = pickle.dumps(it, proto)
                it = pickle.loads(d)
                self.assertEqual(type(itorg), type(it))
                self.assertEqual(list(it), data)

                it = pickle.loads(d)
                ikiwa sio b:
                    endelea
                next(it)
                d = pickle.dumps(it, proto)
                it = pickle.loads(d)
                self.assertEqual(list(it), data[1:])

    eleza test_strip_bytearray(self):
        self.assertEqual(self.type2test(b'abc').strip(memoryview(b'ac')), b'b')
        self.assertEqual(self.type2test(b'abc').lstrip(memoryview(b'ac')), b'bc')
        self.assertEqual(self.type2test(b'abc').rstrip(memoryview(b'ac')), b'ab')

    eleza test_strip_string_error(self):
        self.assertRaises(TypeError, self.type2test(b'abc').strip, 'ac')
        self.assertRaises(TypeError, self.type2test(b'abc').lstrip, 'ac')
        self.assertRaises(TypeError, self.type2test(b'abc').rstrip, 'ac')

    eleza test_strip_int_error(self):
        self.assertRaises(TypeError, self.type2test(b' abc ').strip, 32)
        self.assertRaises(TypeError, self.type2test(b' abc ').lstrip, 32)
        self.assertRaises(TypeError, self.type2test(b' abc ').rstrip, 32)

    eleza test_center(self):
        # Fill character can be either bytes ama bytearray (issue 12380)
        b = self.type2test(b'abc')
        kila fill_type kwenye (bytes, bytearray):
            self.assertEqual(b.center(7, fill_type(b'-')),
                             self.type2test(b'--abc--'))

    eleza test_ljust(self):
        # Fill character can be either bytes ama bytearray (issue 12380)
        b = self.type2test(b'abc')
        kila fill_type kwenye (bytes, bytearray):
            self.assertEqual(b.ljust(7, fill_type(b'-')),
                             self.type2test(b'abc----'))

    eleza test_rjust(self):
        # Fill character can be either bytes ama bytearray (issue 12380)
        b = self.type2test(b'abc')
        kila fill_type kwenye (bytes, bytearray):
            self.assertEqual(b.rjust(7, fill_type(b'-')),
                             self.type2test(b'----abc'))

    eleza test_xjust_int_error(self):
        self.assertRaises(TypeError, self.type2test(b'abc').center, 7, 32)
        self.assertRaises(TypeError, self.type2test(b'abc').ljust, 7, 32)
        self.assertRaises(TypeError, self.type2test(b'abc').rjust, 7, 32)

    eleza test_ord(self):
        b = self.type2test(b'\0A\x7f\x80\xff')
        self.assertEqual([ord(b[i:i+1]) kila i kwenye range(len(b))],
                         [0, 65, 127, 128, 255])

    eleza test_maketrans(self):
        transtable = b'\000\001\002\003\004\005\006\007\010\011\012\013\014\015\016\017\020\021\022\023\024\025\026\027\030\031\032\033\034\035\036\037 !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`xyzdefghijklmnopqrstuvwxyz{|}~\177\200\201\202\203\204\205\206\207\210\211\212\213\214\215\216\217\220\221\222\223\224\225\226\227\230\231\232\233\234\235\236\237\240\241\242\243\244\245\246\247\250\251\252\253\254\255\256\257\260\261\262\263\264\265\266\267\270\271\272\273\274\275\276\277\300\301\302\303\304\305\306\307\310\311\312\313\314\315\316\317\320\321\322\323\324\325\326\327\330\331\332\333\334\335\336\337\340\341\342\343\344\345\346\347\350\351\352\353\354\355\356\357\360\361\362\363\364\365\366\367\370\371\372\373\374\375\376\377'
        self.assertEqual(self.type2test.maketrans(b'abc', b'xyz'), transtable)
        transtable = b'\000\001\002\003\004\005\006\007\010\011\012\013\014\015\016\017\020\021\022\023\024\025\026\027\030\031\032\033\034\035\036\037 !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\177\200\201\202\203\204\205\206\207\210\211\212\213\214\215\216\217\220\221\222\223\224\225\226\227\230\231\232\233\234\235\236\237\240\241\242\243\244\245\246\247\250\251\252\253\254\255\256\257\260\261\262\263\264\265\266\267\270\271\272\273\274\275\276\277\300\301\302\303\304\305\306\307\310\311\312\313\314\315\316\317\320\321\322\323\324\325\326\327\330\331\332\333\334\335\336\337\340\341\342\343\344\345\346\347\350\351\352\353\354\355\356\357\360\361\362\363\364\365\366\367\370\371\372\373\374xyz'
        self.assertEqual(self.type2test.maketrans(b'\375\376\377', b'xyz'), transtable)
        self.assertRaises(ValueError, self.type2test.maketrans, b'abc', b'xyzq')
        self.assertRaises(TypeError, self.type2test.maketrans, 'abc', 'def')

    eleza test_none_arguments(self):
        # issue 11828
        b = self.type2test(b'hello')
        l = self.type2test(b'l')
        h = self.type2test(b'h')
        x = self.type2test(b'x')
        o = self.type2test(b'o')

        self.assertEqual(2, b.find(l, Tupu))
        self.assertEqual(3, b.find(l, -2, Tupu))
        self.assertEqual(2, b.find(l, Tupu, -2))
        self.assertEqual(0, b.find(h, Tupu, Tupu))

        self.assertEqual(3, b.rfind(l, Tupu))
        self.assertEqual(3, b.rfind(l, -2, Tupu))
        self.assertEqual(2, b.rfind(l, Tupu, -2))
        self.assertEqual(0, b.rfind(h, Tupu, Tupu))

        self.assertEqual(2, b.index(l, Tupu))
        self.assertEqual(3, b.index(l, -2, Tupu))
        self.assertEqual(2, b.index(l, Tupu, -2))
        self.assertEqual(0, b.index(h, Tupu, Tupu))

        self.assertEqual(3, b.rindex(l, Tupu))
        self.assertEqual(3, b.rindex(l, -2, Tupu))
        self.assertEqual(2, b.rindex(l, Tupu, -2))
        self.assertEqual(0, b.rindex(h, Tupu, Tupu))

        self.assertEqual(2, b.count(l, Tupu))
        self.assertEqual(1, b.count(l, -2, Tupu))
        self.assertEqual(1, b.count(l, Tupu, -2))
        self.assertEqual(0, b.count(x, Tupu, Tupu))

        self.assertEqual(Kweli, b.endswith(o, Tupu))
        self.assertEqual(Kweli, b.endswith(o, -2, Tupu))
        self.assertEqual(Kweli, b.endswith(l, Tupu, -2))
        self.assertEqual(Uongo, b.endswith(x, Tupu, Tupu))

        self.assertEqual(Kweli, b.startswith(h, Tupu))
        self.assertEqual(Kweli, b.startswith(l, -2, Tupu))
        self.assertEqual(Kweli, b.startswith(h, Tupu, -2))
        self.assertEqual(Uongo, b.startswith(x, Tupu, Tupu))

    eleza test_integer_arguments_out_of_byte_range(self):
        b = self.type2test(b'hello')

        kila method kwenye (b.count, b.find, b.index, b.rfind, b.rindex):
            self.assertRaises(ValueError, method, -1)
            self.assertRaises(ValueError, method, 256)
            self.assertRaises(ValueError, method, 9999)

    eleza test_find_etc_raise_correct_error_messages(self):
        # issue 11828
        b = self.type2test(b'hello')
        x = self.type2test(b'x')
        self.assertRaisesRegex(TypeError, r'\bfind\b', b.find,
                                x, Tupu, Tupu, Tupu)
        self.assertRaisesRegex(TypeError, r'\brfind\b', b.rfind,
                                x, Tupu, Tupu, Tupu)
        self.assertRaisesRegex(TypeError, r'\bindex\b', b.index,
                                x, Tupu, Tupu, Tupu)
        self.assertRaisesRegex(TypeError, r'\brindex\b', b.rindex,
                                x, Tupu, Tupu, Tupu)
        self.assertRaisesRegex(TypeError, r'\bcount\b', b.count,
                                x, Tupu, Tupu, Tupu)
        self.assertRaisesRegex(TypeError, r'\bstartswith\b', b.startswith,
                                x, Tupu, Tupu, Tupu)
        self.assertRaisesRegex(TypeError, r'\bendswith\b', b.endswith,
                                x, Tupu, Tupu, Tupu)

    eleza test_free_after_iterating(self):
        test.support.check_free_after_iterating(self, iter, self.type2test)
        test.support.check_free_after_iterating(self, reversed, self.type2test)

    eleza test_translate(self):
        b = self.type2test(b'hello')
        rosetta = bytearray(range(256))
        rosetta[ord('o')] = ord('e')

        self.assertRaises(TypeError, b.translate)
        self.assertRaises(TypeError, b.translate, Tupu, Tupu)
        self.assertRaises(ValueError, b.translate, bytes(range(255)))

        c = b.translate(rosetta, b'hello')
        self.assertEqual(b, b'hello')
        self.assertIsInstance(c, self.type2test)

        c = b.translate(rosetta)
        d = b.translate(rosetta, b'')
        self.assertEqual(c, d)
        self.assertEqual(c, b'helle')

        c = b.translate(rosetta, b'l')
        self.assertEqual(c, b'hee')
        c = b.translate(Tupu, b'e')
        self.assertEqual(c, b'hllo')

        # test delete kama a keyword argument
        c = b.translate(rosetta, delete=b'')
        self.assertEqual(c, b'helle')
        c = b.translate(rosetta, delete=b'l')
        self.assertEqual(c, b'hee')
        c = b.translate(Tupu, delete=b'e')
        self.assertEqual(c, b'hllo')


kundi BytesTest(BaseBytesTest, unittest.TestCase):
    type2test = bytes

    eleza test_getitem_error(self):
        b = b'python'
        msg = "byte indices must be integers ama slices"
        ukijumuisha self.assertRaisesRegex(TypeError, msg):
            b['a']

    eleza test_buffer_is_readonly(self):
        fd = os.open(__file__, os.O_RDONLY)
        ukijumuisha open(fd, "rb", buffering=0) kama f:
            self.assertRaises(TypeError, f.readinto, b"")

    eleza test_custom(self):
        kundi A:
            eleza __bytes__(self):
                rudisha b'abc'
        self.assertEqual(bytes(A()), b'abc')
        kundi A: pita
        self.assertRaises(TypeError, bytes, A())
        kundi A:
            eleza __bytes__(self):
                rudisha Tupu
        self.assertRaises(TypeError, bytes, A())
        kundi A:
            eleza __bytes__(self):
                rudisha b'a'
            eleza __index__(self):
                rudisha 42
        self.assertEqual(bytes(A()), b'a')
        # Issue #25766
        kundi A(str):
            eleza __bytes__(self):
                rudisha b'abc'
        self.assertEqual(bytes(A('\u20ac')), b'abc')
        self.assertEqual(bytes(A('\u20ac'), 'iso8859-15'), b'\xa4')
        # Issue #24731
        kundi A:
            eleza __bytes__(self):
                rudisha OtherBytesSubclass(b'abc')
        self.assertEqual(bytes(A()), b'abc')
        self.assertIs(type(bytes(A())), OtherBytesSubclass)
        self.assertEqual(BytesSubclass(A()), b'abc')
        self.assertIs(type(BytesSubclass(A())), BytesSubclass)

    # Test PyBytes_FromFormat()
    eleza test_from_format(self):
        ctypes = test.support.import_module('ctypes')
        _testcapi = test.support.import_module('_testcapi')
        kutoka ctypes agiza pythonapi, py_object
        kutoka ctypes agiza (
            c_int, c_uint,
            c_long, c_ulong,
            c_size_t, c_ssize_t,
            c_char_p)

        PyBytes_FromFormat = pythonapi.PyBytes_FromFormat
        PyBytes_FromFormat.restype = py_object

        # basic tests
        self.assertEqual(PyBytes_FromFormat(b'format'),
                         b'format')
        self.assertEqual(PyBytes_FromFormat(b'Hello %s !', b'world'),
                         b'Hello world !')

        # test formatters
        self.assertEqual(PyBytes_FromFormat(b'c=%c', c_int(0)),
                         b'c=\0')
        self.assertEqual(PyBytes_FromFormat(b'c=%c', c_int(ord('@'))),
                         b'c=@')
        self.assertEqual(PyBytes_FromFormat(b'c=%c', c_int(255)),
                         b'c=\xff')
        self.assertEqual(PyBytes_FromFormat(b'd=%d ld=%ld zd=%zd',
                                            c_int(1), c_long(2),
                                            c_size_t(3)),
                         b'd=1 ld=2 zd=3')
        self.assertEqual(PyBytes_FromFormat(b'd=%d ld=%ld zd=%zd',
                                            c_int(-1), c_long(-2),
                                            c_size_t(-3)),
                         b'd=-1 ld=-2 zd=-3')
        self.assertEqual(PyBytes_FromFormat(b'u=%u lu=%lu zu=%zu',
                                            c_uint(123), c_ulong(456),
                                            c_size_t(789)),
                         b'u=123 lu=456 zu=789')
        self.assertEqual(PyBytes_FromFormat(b'i=%i', c_int(123)),
                         b'i=123')
        self.assertEqual(PyBytes_FromFormat(b'i=%i', c_int(-123)),
                         b'i=-123')
        self.assertEqual(PyBytes_FromFormat(b'x=%x', c_int(0xabc)),
                         b'x=abc')

        sizeof_ptr = ctypes.sizeof(c_char_p)

        ikiwa os.name == 'nt':
            # Windows (MSCRT)
            ptr_format = '0x%0{}X'.format(2 * sizeof_ptr)
            eleza ptr_formatter(ptr):
                rudisha (ptr_format % ptr)
        isipokua:
            # UNIX (glibc)
            eleza ptr_formatter(ptr):
                rudisha '%#x' % ptr

        ptr = 0xabcdef
        self.assertEqual(PyBytes_FromFormat(b'ptr=%p', c_char_p(ptr)),
                         ('ptr=' + ptr_formatter(ptr)).encode('ascii'))
        self.assertEqual(PyBytes_FromFormat(b's=%s', c_char_p(b'cstr')),
                         b's=cstr')

        # test minimum na maximum integer values
        size_max = c_size_t(-1).value
        kila formatstr, ctypes_type, value, py_formatter kwenye (
            (b'%d', c_int, _testcapi.INT_MIN, str),
            (b'%d', c_int, _testcapi.INT_MAX, str),
            (b'%ld', c_long, _testcapi.LONG_MIN, str),
            (b'%ld', c_long, _testcapi.LONG_MAX, str),
            (b'%lu', c_ulong, _testcapi.ULONG_MAX, str),
            (b'%zd', c_ssize_t, _testcapi.PY_SSIZE_T_MIN, str),
            (b'%zd', c_ssize_t, _testcapi.PY_SSIZE_T_MAX, str),
            (b'%zu', c_size_t, size_max, str),
            (b'%p', c_char_p, size_max, ptr_formatter),
        ):
            self.assertEqual(PyBytes_FromFormat(formatstr, ctypes_type(value)),
                             py_formatter(value).encode('ascii')),

        # width na precision (width ni currently ignored)
        self.assertEqual(PyBytes_FromFormat(b'%5s', b'a'),
                         b'a')
        self.assertEqual(PyBytes_FromFormat(b'%.3s', b'abcdef'),
                         b'abc')

        # '%%' formatter
        self.assertEqual(PyBytes_FromFormat(b'%%'),
                         b'%')
        self.assertEqual(PyBytes_FromFormat(b'[%%]'),
                         b'[%]')
        self.assertEqual(PyBytes_FromFormat(b'%%%c', c_int(ord('_'))),
                         b'%_')
        self.assertEqual(PyBytes_FromFormat(b'%%s'),
                         b'%s')

        # Invalid formats na partial formatting
        self.assertEqual(PyBytes_FromFormat(b'%'), b'%')
        self.assertEqual(PyBytes_FromFormat(b'x=%i y=%', c_int(2), c_int(3)),
                         b'x=2 y=%')

        # Issue #19969: %c must ashiria OverflowError kila values
        # haiko kwenye the range [0; 255]
        self.assertRaises(OverflowError,
                          PyBytes_FromFormat, b'%c', c_int(-1))
        self.assertRaises(OverflowError,
                          PyBytes_FromFormat, b'%c', c_int(256))

        # Issue #33817: empty strings
        self.assertEqual(PyBytes_FromFormat(b''),
                         b'')
        self.assertEqual(PyBytes_FromFormat(b'%s', b''),
                         b'')

    eleza test_bytes_blocking(self):
        kundi IterationBlocked(list):
            __bytes__ = Tupu
        i = [0, 1, 2, 3]
        self.assertEqual(bytes(i), b'\x00\x01\x02\x03')
        self.assertRaises(TypeError, bytes, IterationBlocked(i))

        # At least kwenye CPython, because bytes.__new__ na the C API
        # PyBytes_FromObject have different fallback rules, integer
        # fallback ni handled specially, so test separately.
        kundi IntBlocked(int):
            __bytes__ = Tupu
        self.assertEqual(bytes(3), b'\0\0\0')
        self.assertRaises(TypeError, bytes, IntBlocked(3))

        # While there ni no separately-defined rule kila handling bytes
        # subclasses differently kutoka other buffer-interface classes,
        # an implementation may well special-case them (as CPython 2.x
        # str did), so test them separately.
        kundi BytesSubclassBlocked(bytes):
            __bytes__ = Tupu
        self.assertEqual(bytes(b'ab'), b'ab')
        self.assertRaises(TypeError, bytes, BytesSubclassBlocked(b'ab'))

        kundi BufferBlocked(bytearray):
            __bytes__ = Tupu
        ba, bb = bytearray(b'ab'), BufferBlocked(b'ab')
        self.assertEqual(bytes(ba), b'ab')
        self.assertRaises(TypeError, bytes, bb)


kundi ByteArrayTest(BaseBytesTest, unittest.TestCase):
    type2test = bytearray

    eleza test_getitem_error(self):
        b = bytearray(b'python')
        msg = "bytearray indices must be integers ama slices"
        ukijumuisha self.assertRaisesRegex(TypeError, msg):
            b['a']

    eleza test_setitem_error(self):
        b = bytearray(b'python')
        msg = "bytearray indices must be integers ama slices"
        ukijumuisha self.assertRaisesRegex(TypeError, msg):
            b['a'] = "python"

    eleza test_nohash(self):
        self.assertRaises(TypeError, hash, bytearray())

    eleza test_bytearray_api(self):
        short_sample = b"Hello world\n"
        sample = short_sample + b"\0"*(20 - len(short_sample))
        tfn = tempfile.mktemp()
        jaribu:
            # Prepare
            ukijumuisha open(tfn, "wb") kama f:
                f.write(short_sample)
            # Test readinto
            ukijumuisha open(tfn, "rb") kama f:
                b = bytearray(20)
                n = f.readinto(b)
            self.assertEqual(n, len(short_sample))
            self.assertEqual(list(b), list(sample))
            # Test writing kwenye binary mode
            ukijumuisha open(tfn, "wb") kama f:
                f.write(b)
            ukijumuisha open(tfn, "rb") kama f:
                self.assertEqual(f.read(), sample)
            # Text mode ni ambiguous; don't test
        mwishowe:
            jaribu:
                os.remove(tfn)
            tatizo OSError:
                pita

    eleza test_reverse(self):
        b = bytearray(b'hello')
        self.assertEqual(b.reverse(), Tupu)
        self.assertEqual(b, b'olleh')
        b = bytearray(b'hello1') # test even number of items
        b.reverse()
        self.assertEqual(b, b'1olleh')
        b = bytearray()
        b.reverse()
        self.assertUongo(b)

    eleza test_clear(self):
        b = bytearray(b'python')
        b.clear()
        self.assertEqual(b, b'')

        b = bytearray(b'')
        b.clear()
        self.assertEqual(b, b'')

        b = bytearray(b'')
        b.append(ord('r'))
        b.clear()
        b.append(ord('p'))
        self.assertEqual(b, b'p')

    eleza test_copy(self):
        b = bytearray(b'abc')
        bb = b.copy()
        self.assertEqual(bb, b'abc')

        b = bytearray(b'')
        bb = b.copy()
        self.assertEqual(bb, b'')

        # test that it's indeed a copy na sio a reference
        b = bytearray(b'abc')
        bb = b.copy()
        self.assertEqual(b, bb)
        self.assertIsNot(b, bb)
        bb.append(ord('d'))
        self.assertEqual(bb, b'abcd')
        self.assertEqual(b, b'abc')

    eleza test_regexps(self):
        eleza by(s):
            rudisha bytearray(map(ord, s))
        b = by("Hello, world")
        self.assertEqual(re.findall(br"\w+", b), [by("Hello"), by("world")])

    eleza test_setitem(self):
        b = bytearray([1, 2, 3])
        b[1] = 100
        self.assertEqual(b, bytearray([1, 100, 3]))
        b[-1] = 200
        self.assertEqual(b, bytearray([1, 100, 200]))
        b[0] = Indexable(10)
        self.assertEqual(b, bytearray([10, 100, 200]))
        jaribu:
            b[3] = 0
            self.fail("Didn't ashiria IndexError")
        tatizo IndexError:
            pita
        jaribu:
            b[-10] = 0
            self.fail("Didn't ashiria IndexError")
        tatizo IndexError:
            pita
        jaribu:
            b[0] = 256
            self.fail("Didn't ashiria ValueError")
        tatizo ValueError:
            pita
        jaribu:
            b[0] = Indexable(-1)
            self.fail("Didn't ashiria ValueError")
        tatizo ValueError:
            pita
        jaribu:
            b[0] = Tupu
            self.fail("Didn't ashiria TypeError")
        tatizo TypeError:
            pita

    eleza test_delitem(self):
        b = bytearray(range(10))
        toa b[0]
        self.assertEqual(b, bytearray(range(1, 10)))
        toa b[-1]
        self.assertEqual(b, bytearray(range(1, 9)))
        toa b[4]
        self.assertEqual(b, bytearray([1, 2, 3, 4, 6, 7, 8]))

    eleza test_setslice(self):
        b = bytearray(range(10))
        self.assertEqual(list(b), list(range(10)))

        b[0:5] = bytearray([1, 1, 1, 1, 1])
        self.assertEqual(b, bytearray([1, 1, 1, 1, 1, 5, 6, 7, 8, 9]))

        toa b[0:-5]
        self.assertEqual(b, bytearray([5, 6, 7, 8, 9]))

        b[0:0] = bytearray([0, 1, 2, 3, 4])
        self.assertEqual(b, bytearray(range(10)))

        b[-7:-3] = bytearray([100, 101])
        self.assertEqual(b, bytearray([0, 1, 2, 100, 101, 7, 8, 9]))

        b[3:5] = [3, 4, 5, 6]
        self.assertEqual(b, bytearray(range(10)))

        b[3:0] = [42, 42, 42]
        self.assertEqual(b, bytearray([0, 1, 2, 42, 42, 42, 3, 4, 5, 6, 7, 8, 9]))

        b[3:] = b'foo'
        self.assertEqual(b, bytearray([0, 1, 2, 102, 111, 111]))

        b[:3] = memoryview(b'foo')
        self.assertEqual(b, bytearray([102, 111, 111, 102, 111, 111]))

        b[3:4] = []
        self.assertEqual(b, bytearray([102, 111, 111, 111, 111]))

        kila elem kwenye [5, -5, 0, int(10e20), 'str', 2.3,
                     ['a', 'b'], [b'a', b'b'], [[]]]:
            ukijumuisha self.assertRaises(TypeError):
                b[3:4] = elem

        kila elem kwenye [[254, 255, 256], [-256, 9000]]:
            ukijumuisha self.assertRaises(ValueError):
                b[3:4] = elem

    eleza test_setslice_extend(self):
        # Exercise the resizing logic (see issue #19087)
        b = bytearray(range(100))
        self.assertEqual(list(b), list(range(100)))
        toa b[:10]
        self.assertEqual(list(b), list(range(10, 100)))
        b.extend(range(100, 110))
        self.assertEqual(list(b), list(range(10, 110)))

    eleza test_fifo_overrun(self):
        # Test kila issue #23985, a buffer overrun when implementing a FIFO
        # Build Python kwenye pydebug mode kila best results.
        b = bytearray(10)
        b.pop()        # Defeat expanding buffer off-by-one quirk
        toa b[:1]      # Advance start pointer without reallocating
        b += bytes(2)  # Append exactly the number of deleted bytes
        toa b          # Free memory buffer, allowing pydebug verification

    eleza test_del_expand(self):
        # Reducing the size should sio expand the buffer (issue #23985)
        b = bytearray(10)
        size = sys.getsizeof(b)
        toa b[:1]
        self.assertLessEqual(sys.getsizeof(b), size)

    eleza test_extended_set_del_slice(self):
        indices = (0, Tupu, 1, 3, 19, 300, 1<<333, sys.maxsize,
            -1, -2, -31, -300)
        kila start kwenye indices:
            kila stop kwenye indices:
                # Skip invalid step 0
                kila step kwenye indices[1:]:
                    L = list(range(255))
                    b = bytearray(L)
                    # Make sure we have a slice of exactly the right length,
                    # but ukijumuisha different data.
                    data = L[start:stop:step]
                    data.reverse()
                    L[start:stop:step] = data
                    b[start:stop:step] = data
                    self.assertEqual(b, bytearray(L))

                    toa L[start:stop:step]
                    toa b[start:stop:step]
                    self.assertEqual(b, bytearray(L))

    eleza test_setslice_trap(self):
        # This test verifies that we correctly handle assigning self
        # to a slice of self (the old Lambert Meertens trap).
        b = bytearray(range(256))
        b[8:] = b
        self.assertEqual(b, bytearray(list(range(8)) + list(range(256))))

    eleza test_iconcat(self):
        b = bytearray(b"abc")
        b1 = b
        b += b"def"
        self.assertEqual(b, b"abcdef")
        self.assertEqual(b, b1)
        self.assertIs(b, b1)
        b += b"xyz"
        self.assertEqual(b, b"abcdefxyz")
        jaribu:
            b += ""
        tatizo TypeError:
            pita
        isipokua:
            self.fail("bytes += unicode didn't ashiria TypeError")

    eleza test_irepeat(self):
        b = bytearray(b"abc")
        b1 = b
        b *= 3
        self.assertEqual(b, b"abcabcabc")
        self.assertEqual(b, b1)
        self.assertIs(b, b1)

    eleza test_irepeat_1char(self):
        b = bytearray(b"x")
        b1 = b
        b *= 100
        self.assertEqual(b, b"x"*100)
        self.assertEqual(b, b1)
        self.assertIs(b, b1)

    eleza test_alloc(self):
        b = bytearray()
        alloc = b.__alloc__()
        self.assertGreaterEqual(alloc, 0)
        seq = [alloc]
        kila i kwenye range(100):
            b += b"x"
            alloc = b.__alloc__()
            self.assertGreater(alloc, len(b))  # including trailing null byte
            ikiwa alloc haiko kwenye seq:
                seq.append(alloc)

    eleza test_init_alloc(self):
        b = bytearray()
        eleza g():
            kila i kwenye range(1, 100):
                tuma i
                a = list(b)
                self.assertEqual(a, list(range(1, len(a)+1)))
                self.assertEqual(len(b), len(a))
                self.assertLessEqual(len(b), i)
                alloc = b.__alloc__()
                self.assertGreater(alloc, len(b))  # including trailing null byte
        b.__init__(g())
        self.assertEqual(list(b), list(range(1, 100)))
        self.assertEqual(len(b), 99)
        alloc = b.__alloc__()
        self.assertGreater(alloc, len(b))

    eleza test_extend(self):
        orig = b'hello'
        a = bytearray(orig)
        a.extend(a)
        self.assertEqual(a, orig + orig)
        self.assertEqual(a[5:], orig)
        a = bytearray(b'')
        # Test iterators that don't have a __length_hint__
        a.extend(map(int, orig * 25))
        a.extend(int(x) kila x kwenye orig * 25)
        self.assertEqual(a, orig * 50)
        self.assertEqual(a[-5:], orig)
        a = bytearray(b'')
        a.extend(iter(map(int, orig * 50)))
        self.assertEqual(a, orig * 50)
        self.assertEqual(a[-5:], orig)
        a = bytearray(b'')
        a.extend(list(map(int, orig * 50)))
        self.assertEqual(a, orig * 50)
        self.assertEqual(a[-5:], orig)
        a = bytearray(b'')
        self.assertRaises(ValueError, a.extend, [0, 1, 2, 256])
        self.assertRaises(ValueError, a.extend, [0, 1, 2, -1])
        self.assertEqual(len(a), 0)
        a = bytearray(b'')
        a.extend([Indexable(ord('a'))])
        self.assertEqual(a, b'a')

    eleza test_remove(self):
        b = bytearray(b'hello')
        b.remove(ord('l'))
        self.assertEqual(b, b'helo')
        b.remove(ord('l'))
        self.assertEqual(b, b'heo')
        self.assertRaises(ValueError, lambda: b.remove(ord('l')))
        self.assertRaises(ValueError, lambda: b.remove(400))
        self.assertRaises(TypeError, lambda: b.remove('e'))
        # remove first na last
        b.remove(ord('o'))
        b.remove(ord('h'))
        self.assertEqual(b, b'e')
        self.assertRaises(TypeError, lambda: b.remove(b'e'))
        b.remove(Indexable(ord('e')))
        self.assertEqual(b, b'')

        # test values outside of the ascii range: (0, 127)
        c = bytearray([126, 127, 128, 129])
        c.remove(127)
        self.assertEqual(c, bytes([126, 128, 129]))
        c.remove(129)
        self.assertEqual(c, bytes([126, 128]))

    eleza test_pop(self):
        b = bytearray(b'world')
        self.assertEqual(b.pop(), ord('d'))
        self.assertEqual(b.pop(0), ord('w'))
        self.assertEqual(b.pop(-2), ord('r'))
        self.assertRaises(IndexError, lambda: b.pop(10))
        self.assertRaises(IndexError, lambda: bytearray().pop())
        # test kila issue #6846
        self.assertEqual(bytearray(b'\xff').pop(), 0xff)

    eleza test_nosort(self):
        self.assertRaises(AttributeError, lambda: bytearray().sort())

    eleza test_append(self):
        b = bytearray(b'hell')
        b.append(ord('o'))
        self.assertEqual(b, b'hello')
        self.assertEqual(b.append(100), Tupu)
        b = bytearray()
        b.append(ord('A'))
        self.assertEqual(len(b), 1)
        self.assertRaises(TypeError, lambda: b.append(b'o'))
        b = bytearray()
        b.append(Indexable(ord('A')))
        self.assertEqual(b, b'A')

    eleza test_insert(self):
        b = bytearray(b'msssspp')
        b.insert(1, ord('i'))
        b.insert(4, ord('i'))
        b.insert(-2, ord('i'))
        b.insert(1000, ord('i'))
        self.assertEqual(b, b'mississippi')
        self.assertRaises(TypeError, lambda: b.insert(0, b'1'))
        b = bytearray()
        b.insert(0, Indexable(ord('A')))
        self.assertEqual(b, b'A')

    eleza test_copied(self):
        # Issue 4348.  Make sure that operations that don't mutate the array
        # copy the bytes.
        b = bytearray(b'abc')
        self.assertIsNot(b, b.replace(b'abc', b'cde', 0))

        t = bytearray([i kila i kwenye range(256)])
        x = bytearray(b'')
        self.assertIsNot(x, x.translate(t))

    eleza test_partition_bytearray_doesnt_share_nullstring(self):
        a, b, c = bytearray(b"x").partition(b"y")
        self.assertEqual(b, b"")
        self.assertEqual(c, b"")
        self.assertIsNot(b, c)
        b += b"!"
        self.assertEqual(c, b"")
        a, b, c = bytearray(b"x").partition(b"y")
        self.assertEqual(b, b"")
        self.assertEqual(c, b"")
        # Same kila rpartition
        b, c, a = bytearray(b"x").rpartition(b"y")
        self.assertEqual(b, b"")
        self.assertEqual(c, b"")
        self.assertIsNot(b, c)
        b += b"!"
        self.assertEqual(c, b"")
        c, b, a = bytearray(b"x").rpartition(b"y")
        self.assertEqual(b, b"")
        self.assertEqual(c, b"")

    eleza test_resize_forbidden(self):
        # #4509: can't resize a bytearray when there are buffer exports, even
        # ikiwa it wouldn't reallocate the underlying buffer.
        # Furthermore, no destructive changes to the buffer may be applied
        # before raising the error.
        b = bytearray(range(10))
        v = memoryview(b)
        eleza resize(n):
            b[1:-1] = range(n + 1, 2*n - 1)
        resize(10)
        orig = b[:]
        self.assertRaises(BufferError, resize, 11)
        self.assertEqual(b, orig)
        self.assertRaises(BufferError, resize, 9)
        self.assertEqual(b, orig)
        self.assertRaises(BufferError, resize, 0)
        self.assertEqual(b, orig)
        # Other operations implying resize
        self.assertRaises(BufferError, b.pop, 0)
        self.assertEqual(b, orig)
        self.assertRaises(BufferError, b.remove, b[1])
        self.assertEqual(b, orig)
        eleza delitem():
            toa b[1]
        self.assertRaises(BufferError, delitem)
        self.assertEqual(b, orig)
        # deleting a non-contiguous slice
        eleza delslice():
            b[1:-1:2] = b""
        self.assertRaises(BufferError, delslice)
        self.assertEqual(b, orig)

    @test.support.cpython_only
    eleza test_obsolete_write_lock(self):
        kutoka _testcapi agiza getbuffer_with_null_view
        self.assertRaises(BufferError, getbuffer_with_null_view, bytearray())

    eleza test_iterator_pickling2(self):
        orig = bytearray(b'abc')
        data = list(b'qwerty')
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            # initial iterator
            itorig = iter(orig)
            d = pickle.dumps((itorig, orig), proto)
            it, b = pickle.loads(d)
            b[:] = data
            self.assertEqual(type(it), type(itorig))
            self.assertEqual(list(it), data)

            # running iterator
            next(itorig)
            d = pickle.dumps((itorig, orig), proto)
            it, b = pickle.loads(d)
            b[:] = data
            self.assertEqual(type(it), type(itorig))
            self.assertEqual(list(it), data[1:])

            # empty iterator
            kila i kwenye range(1, len(orig)):
                next(itorig)
            d = pickle.dumps((itorig, orig), proto)
            it, b = pickle.loads(d)
            b[:] = data
            self.assertEqual(type(it), type(itorig))
            self.assertEqual(list(it), data[len(orig):])

            # exhausted iterator
            self.assertRaises(StopIteration, next, itorig)
            d = pickle.dumps((itorig, orig), proto)
            it, b = pickle.loads(d)
            b[:] = data
            self.assertEqual(list(it), [])

    test_exhausted_iterator = test.list_tests.CommonTest.test_exhausted_iterator

    eleza test_iterator_length_hint(self):
        # Issue 27443: __length_hint__ can rudisha negative integer
        ba = bytearray(b'ab')
        it = iter(ba)
        next(it)
        ba.clear()
        # Shouldn't ashiria an error
        self.assertEqual(list(it), [])


kundi AssortedBytesTest(unittest.TestCase):
    #
    # Test various combinations of bytes na bytearray
    #

    @check_bytes_warnings
    eleza test_repr_str(self):
        kila f kwenye str, repr:
            self.assertEqual(f(bytearray()), "bytearray(b'')")
            self.assertEqual(f(bytearray([0])), "bytearray(b'\\x00')")
            self.assertEqual(f(bytearray([0, 1, 254, 255])),
                             "bytearray(b'\\x00\\x01\\xfe\\xff')")
            self.assertEqual(f(b"abc"), "b'abc'")
            self.assertEqual(f(b"'"), '''b"'"''') # '''
            self.assertEqual(f(b"'\""), r"""b'\'"'""") # '

    @check_bytes_warnings
    eleza test_format(self):
        kila b kwenye b'abc', bytearray(b'abc'):
            self.assertEqual(format(b), str(b))
            self.assertEqual(format(b, ''), str(b))
            ukijumuisha self.assertRaisesRegex(TypeError,
                                        r'\b%s\b' % re.escape(type(b).__name__)):
                format(b, 's')

    eleza test_compare_bytes_to_bytearray(self):
        self.assertEqual(b"abc" == bytes(b"abc"), Kweli)
        self.assertEqual(b"ab" != bytes(b"abc"), Kweli)
        self.assertEqual(b"ab" <= bytes(b"abc"), Kweli)
        self.assertEqual(b"ab" < bytes(b"abc"), Kweli)
        self.assertEqual(b"abc" >= bytes(b"ab"), Kweli)
        self.assertEqual(b"abc" > bytes(b"ab"), Kweli)

        self.assertEqual(b"abc" != bytes(b"abc"), Uongo)
        self.assertEqual(b"ab" == bytes(b"abc"), Uongo)
        self.assertEqual(b"ab" > bytes(b"abc"), Uongo)
        self.assertEqual(b"ab" >= bytes(b"abc"), Uongo)
        self.assertEqual(b"abc" < bytes(b"ab"), Uongo)
        self.assertEqual(b"abc" <= bytes(b"ab"), Uongo)

        self.assertEqual(bytes(b"abc") == b"abc", Kweli)
        self.assertEqual(bytes(b"ab") != b"abc", Kweli)
        self.assertEqual(bytes(b"ab") <= b"abc", Kweli)
        self.assertEqual(bytes(b"ab") < b"abc", Kweli)
        self.assertEqual(bytes(b"abc") >= b"ab", Kweli)
        self.assertEqual(bytes(b"abc") > b"ab", Kweli)

        self.assertEqual(bytes(b"abc") != b"abc", Uongo)
        self.assertEqual(bytes(b"ab") == b"abc", Uongo)
        self.assertEqual(bytes(b"ab") > b"abc", Uongo)
        self.assertEqual(bytes(b"ab") >= b"abc", Uongo)
        self.assertEqual(bytes(b"abc") < b"ab", Uongo)
        self.assertEqual(bytes(b"abc") <= b"ab", Uongo)

    @test.support.requires_docstrings
    eleza test_doc(self):
        self.assertIsNotTupu(bytearray.__doc__)
        self.assertKweli(bytearray.__doc__.startswith("bytearray("), bytearray.__doc__)
        self.assertIsNotTupu(bytes.__doc__)
        self.assertKweli(bytes.__doc__.startswith("bytes("), bytes.__doc__)

    eleza test_from_bytearray(self):
        sample = bytes(b"Hello world\n\x80\x81\xfe\xff")
        buf = memoryview(sample)
        b = bytearray(buf)
        self.assertEqual(b, bytearray(sample))

    @check_bytes_warnings
    eleza test_to_str(self):
        self.assertEqual(str(b''), "b''")
        self.assertEqual(str(b'x'), "b'x'")
        self.assertEqual(str(b'\x80'), "b'\\x80'")
        self.assertEqual(str(bytearray(b'')), "bytearray(b'')")
        self.assertEqual(str(bytearray(b'x')), "bytearray(b'x')")
        self.assertEqual(str(bytearray(b'\x80')), "bytearray(b'\\x80')")

    eleza test_literal(self):
        tests =  [
            (b"Wonderful spam", "Wonderful spam"),
            (br"Wonderful spam too", "Wonderful spam too"),
            (b"\xaa\x00\000\200", "\xaa\x00\000\200"),
            (br"\xaa\x00\000\200", r"\xaa\x00\000\200"),
        ]
        kila b, s kwenye tests:
            self.assertEqual(b, bytearray(s, 'latin-1'))
        kila c kwenye range(128, 256):
            self.assertRaises(SyntaxError, eval,
                              'b"%s"' % chr(c))

    eleza test_split_bytearray(self):
        self.assertEqual(b'a b'.split(memoryview(b' ')), [b'a', b'b'])

    eleza test_rsplit_bytearray(self):
        self.assertEqual(b'a b'.rsplit(memoryview(b' ')), [b'a', b'b'])

    eleza test_return_self(self):
        # bytearray.replace must always rudisha a new bytearray
        b = bytearray()
        self.assertIsNot(b.replace(b'', b''), b)

    @unittest.skipUnless(sys.flags.bytes_warning,
                         "BytesWarning ni needed kila this test: use -bb option")
    eleza test_compare(self):
        eleza bytes_warning():
            rudisha test.support.check_warnings(('', BytesWarning))
        ukijumuisha bytes_warning():
            b'' == ''
        ukijumuisha bytes_warning():
            '' == b''
        ukijumuisha bytes_warning():
            b'' != ''
        ukijumuisha bytes_warning():
            '' != b''
        ukijumuisha bytes_warning():
            bytearray(b'') == ''
        ukijumuisha bytes_warning():
            '' == bytearray(b'')
        ukijumuisha bytes_warning():
            bytearray(b'') != ''
        ukijumuisha bytes_warning():
            '' != bytearray(b'')
        ukijumuisha bytes_warning():
            b'\0' == 0
        ukijumuisha bytes_warning():
            0 == b'\0'
        ukijumuisha bytes_warning():
            b'\0' != 0
        ukijumuisha bytes_warning():
            0 != b'\0'

    # Optimizations:
    # __iter__? (optimization)
    # __reversed__? (optimization)

    # XXX More string methods?  (Those that don't use character properties)

    # There are tests kwenye string_tests.py that are more
    # comprehensive kila things like partition, etc.
    # Unfortunately they are all bundled ukijumuisha tests that
    # are sio appropriate kila bytes

    # I've started porting some of those into bytearray_tests.py, we should port
    # the rest that make sense (the code can be cleaned up to use modern
    # unittest methods at the same time).

kundi BytearrayPEP3137Test(unittest.TestCase):
    eleza marshal(self, x):
        rudisha bytearray(x)

    eleza test_returns_new_copy(self):
        val = self.marshal(b'1234')
        # On immutable types these MAY rudisha a reference to themselves
        # but on mutable types like bytearray they MUST rudisha a new copy.
        kila methname kwenye ('zfill', 'rjust', 'ljust', 'center'):
            method = getattr(val, methname)
            newval = method(3)
            self.assertEqual(val, newval)
            self.assertIsNot(val, newval,
                            methname+' returned self on a mutable object')
        kila expr kwenye ('val.split()[0]', 'val.rsplit()[0]',
                     'val.partition(b".")[0]', 'val.rpartition(b".")[2]',
                     'val.splitlines()[0]', 'val.replace(b"", b"")'):
            newval = eval(expr)
            self.assertEqual(val, newval)
            self.assertIsNot(val, newval,
                            expr+' returned val on a mutable object')
        sep = self.marshal(b'')
        newval = sep.join([val])
        self.assertEqual(val, newval)
        self.assertIsNot(val, newval)


kundi FixedStringTest(test.string_tests.BaseTest):
    eleza fixtype(self, obj):
        ikiwa isinstance(obj, str):
            rudisha self.type2test(obj.encode("utf-8"))
        rudisha super().fixtype(obj)

    contains_bytes = Kweli

kundi ByteArrayAsStringTest(FixedStringTest, unittest.TestCase):
    type2test = bytearray

kundi BytesAsStringTest(FixedStringTest, unittest.TestCase):
    type2test = bytes


kundi SubclassTest:

    eleza test_basic(self):
        self.assertKweli(issubclass(self.type2test, self.basetype))
        self.assertIsInstance(self.type2test(), self.basetype)

        a, b = b"abcd", b"efgh"
        _a, _b = self.type2test(a), self.type2test(b)

        # test comparison operators ukijumuisha subkundi instances
        self.assertKweli(_a == _a)
        self.assertKweli(_a != _b)
        self.assertKweli(_a < _b)
        self.assertKweli(_a <= _b)
        self.assertKweli(_b >= _a)
        self.assertKweli(_b > _a)
        self.assertIsNot(_a, a)

        # test concat of subkundi instances
        self.assertEqual(a + b, _a + _b)
        self.assertEqual(a + b, a + _b)
        self.assertEqual(a + b, _a + b)

        # test repeat
        self.assertKweli(a*5 == _a*5)

    eleza test_join(self):
        # Make sure join returns a NEW object kila single item sequences
        # involving a subclass.
        # Make sure that it ni of the appropriate type.
        s1 = self.type2test(b"abcd")
        s2 = self.basetype().join([s1])
        self.assertIsNot(s1, s2)
        self.assertIs(type(s2), self.basetype, type(s2))

        # Test reverse, calling join on subclass
        s3 = s1.join([b"abcd"])
        self.assertIs(type(s3), self.basetype)

    eleza test_pickle(self):
        a = self.type2test(b"abcd")
        a.x = 10
        a.y = self.type2test(b"efgh")
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            b = pickle.loads(pickle.dumps(a, proto))
            self.assertNotEqual(id(a), id(b))
            self.assertEqual(a, b)
            self.assertEqual(a.x, b.x)
            self.assertEqual(a.y, b.y)
            self.assertEqual(type(a), type(b))
            self.assertEqual(type(a.y), type(b.y))

    eleza test_copy(self):
        a = self.type2test(b"abcd")
        a.x = 10
        a.y = self.type2test(b"efgh")
        kila copy_method kwenye (copy.copy, copy.deepcopy):
            b = copy_method(a)
            self.assertNotEqual(id(a), id(b))
            self.assertEqual(a, b)
            self.assertEqual(a.x, b.x)
            self.assertEqual(a.y, b.y)
            self.assertEqual(type(a), type(b))
            self.assertEqual(type(a.y), type(b.y))

    eleza test_fromhex(self):
        b = self.type2test.fromhex('1a2B30')
        self.assertEqual(b, b'\x1a\x2b\x30')
        self.assertIs(type(b), self.type2test)

        kundi B1(self.basetype):
            eleza __new__(cls, value):
                me = self.basetype.__new__(cls, value)
                me.foo = 'bar'
                rudisha me

        b = B1.fromhex('1a2B30')
        self.assertEqual(b, b'\x1a\x2b\x30')
        self.assertIs(type(b), B1)
        self.assertEqual(b.foo, 'bar')

        kundi B2(self.basetype):
            eleza __init__(me, *args, **kwargs):
                ikiwa self.basetype ni sio bytes:
                    self.basetype.__init__(me, *args, **kwargs)
                me.foo = 'bar'

        b = B2.fromhex('1a2B30')
        self.assertEqual(b, b'\x1a\x2b\x30')
        self.assertIs(type(b), B2)
        self.assertEqual(b.foo, 'bar')


kundi ByteArraySubclass(bytearray):
    pita

kundi BytesSubclass(bytes):
    pita

kundi OtherBytesSubclass(bytes):
    pita

kundi ByteArraySubclassTest(SubclassTest, unittest.TestCase):
    basetype = bytearray
    type2test = ByteArraySubclass

    eleza test_init_override(self):
        kundi subclass(bytearray):
            eleza __init__(me, newarg=1, *args, **kwargs):
                bytearray.__init__(me, *args, **kwargs)
        x = subclass(4, b"abcd")
        x = subclass(4, source=b"abcd")
        self.assertEqual(x, b"abcd")
        x = subclass(newarg=4, source=b"abcd")
        self.assertEqual(x, b"abcd")


kundi BytesSubclassTest(SubclassTest, unittest.TestCase):
    basetype = bytes
    type2test = BytesSubclass


ikiwa __name__ == "__main__":
    unittest.main()
