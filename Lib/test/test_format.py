kutoka test.support agiza verbose, TestFailed
agiza locale
agiza sys
agiza test.support kama support
agiza unittest

maxsize = support.MAX_Py_ssize_t

# test string formatting operator (I am sio sure ikiwa this ni being tested
# elsewhere but, surely, some of the given cases are *not* tested because
# they crash python)
# test on bytes object kama well

eleza testformat(formatstr, args, output=Tupu, limit=Tupu, overflowok=Uongo):
    ikiwa verbose:
        ikiwa output:
            andika("{!a} % {!a} =? {!a} ...".format(formatstr, args, output),
                  end=' ')
        isipokua:
            andika("{!a} % {!a} works? ...".format(formatstr, args), end=' ')
    jaribu:
        result = formatstr % args
    tatizo OverflowError:
        ikiwa sio overflowok:
            ashiria
        ikiwa verbose:
            andika('overflow (this ni fine)')
    isipokua:
        ikiwa output na limit ni Tupu na result != output:
            ikiwa verbose:
                andika('no')
            ashiria AssertionError("%r %% %r == %r != %r" %
                                (formatstr, args, result, output))
        # when 'limit' ni specified, it determines how many characters
        # must match exactly; lengths must always match.
        # ex: limit=5, '12345678' matches '12345___'
        # (mainly kila floating point format tests kila which an exact match
        # can't be guaranteed due to rounding na representation errors)
        lasivyo output na limit ni sio Tupu na (
                len(result)!=len(output) ama result[:limit]!=output[:limit]):
            ikiwa verbose:
                andika('no')
            andika("%s %% %s == %s != %s" % \
                  (repr(formatstr), repr(args), repr(result), repr(output)))
        isipokua:
            ikiwa verbose:
                andika('yes')

eleza testcommon(formatstr, args, output=Tupu, limit=Tupu, overflowok=Uongo):
    # ikiwa formatstr ni a str, test str, bytes, na bytearray;
    # otherwise, test bytes na bytearray
    ikiwa isinstance(formatstr, str):
        testformat(formatstr, args, output, limit, overflowok)
        b_format = formatstr.encode('ascii')
    isipokua:
        b_format = formatstr
    ba_format = bytearray(b_format)
    b_args = []
    ikiwa sio isinstance(args, tuple):
        args = (args, )
    b_args = tuple(args)
    ikiwa output ni Tupu:
        b_output = ba_output = Tupu
    isipokua:
        ikiwa isinstance(output, str):
            b_output = output.encode('ascii')
        isipokua:
            b_output = output
        ba_output = bytearray(b_output)
    testformat(b_format, b_args, b_output, limit, overflowok)
    testformat(ba_format, b_args, ba_output, limit, overflowok)

eleza test_exc(formatstr, args, exception, excmsg):
    jaribu:
        testformat(formatstr, args)
    tatizo exception kama exc:
        ikiwa str(exc) == excmsg:
            ikiwa verbose:
                andika("yes")
        isipokua:
            ikiwa verbose: andika('no')
            andika('Unexpected ', exception, ':', repr(str(exc)))
    except:
        ikiwa verbose: andika('no')
        andika('Unexpected exception')
        ashiria
    isipokua:
        ashiria TestFailed('did sio get expected exception: %s' % excmsg)

eleza test_exc_common(formatstr, args, exception, excmsg):
    # test str na bytes
    test_exc(formatstr, args, exception, excmsg)
    test_exc(formatstr.encode('ascii'), args, exception, excmsg)

kundi FormatTest(unittest.TestCase):

    eleza test_common_format(self):
        # test the format identifiers that work the same across
        # str, bytes, na bytearrays (integer, float, oct, hex)
        testcommon("%%", (), "%")
        testcommon("%.1d", (1,), "1")
        testcommon("%.*d", (sys.maxsize,1), overflowok=Kweli)  # expect overflow
        testcommon("%.100d", (1,), '00000000000000000000000000000000000000'
                 '000000000000000000000000000000000000000000000000000000'
                 '00000001', overflowok=Kweli)
        testcommon("%#.117x", (1,), '0x00000000000000000000000000000000000'
                 '000000000000000000000000000000000000000000000000000000'
                 '0000000000000000000000000001',
                 overflowok=Kweli)
        testcommon("%#.118x", (1,), '0x00000000000000000000000000000000000'
                 '000000000000000000000000000000000000000000000000000000'
                 '00000000000000000000000000001',
                 overflowok=Kweli)

        testcommon("%f", (1.0,), "1.000000")
        # these are trying to test the limits of the internal magic-number-length
        # formatting buffer, ikiwa that number changes then these tests are less
        # effective
        testcommon("%#.*g", (109, -1.e+49/3.))
        testcommon("%#.*g", (110, -1.e+49/3.))
        testcommon("%#.*g", (110, -1.e+100/3.))
        # test some ridiculously large precision, expect overflow
        testcommon('%12.*f', (123456, 1.0))

        # check kila internal overflow validation on length of precision
        # these tests should no longer cause overflow kwenye Python
        # 2.7/3.1 na later.
        testcommon("%#.*g", (110, -1.e+100/3.))
        testcommon("%#.*G", (110, -1.e+100/3.))
        testcommon("%#.*f", (110, -1.e+100/3.))
        testcommon("%#.*F", (110, -1.e+100/3.))
        # Formatting of integers. Overflow ni sio ok
        testcommon("%x", 10, "a")
        testcommon("%x", 100000000000, "174876e800")
        testcommon("%o", 10, "12")
        testcommon("%o", 100000000000, "1351035564000")
        testcommon("%d", 10, "10")
        testcommon("%d", 100000000000, "100000000000")

        big = 123456789012345678901234567890
        testcommon("%d", big, "123456789012345678901234567890")
        testcommon("%d", -big, "-123456789012345678901234567890")
        testcommon("%5d", -big, "-123456789012345678901234567890")
        testcommon("%31d", -big, "-123456789012345678901234567890")
        testcommon("%32d", -big, " -123456789012345678901234567890")
        testcommon("%-32d", -big, "-123456789012345678901234567890 ")
        testcommon("%032d", -big, "-0123456789012345678901234567890")
        testcommon("%-032d", -big, "-123456789012345678901234567890 ")
        testcommon("%034d", -big, "-000123456789012345678901234567890")
        testcommon("%034d", big, "0000123456789012345678901234567890")
        testcommon("%0+34d", big, "+000123456789012345678901234567890")
        testcommon("%+34d", big, "   +123456789012345678901234567890")
        testcommon("%34d", big, "    123456789012345678901234567890")
        testcommon("%.2d", big, "123456789012345678901234567890")
        testcommon("%.30d", big, "123456789012345678901234567890")
        testcommon("%.31d", big, "0123456789012345678901234567890")
        testcommon("%32.31d", big, " 0123456789012345678901234567890")
        testcommon("%d", float(big), "123456________________________", 6)

        big = 0x1234567890abcdef12345  # 21 hex digits
        testcommon("%x", big, "1234567890abcdef12345")
        testcommon("%x", -big, "-1234567890abcdef12345")
        testcommon("%5x", -big, "-1234567890abcdef12345")
        testcommon("%22x", -big, "-1234567890abcdef12345")
        testcommon("%23x", -big, " -1234567890abcdef12345")
        testcommon("%-23x", -big, "-1234567890abcdef12345 ")
        testcommon("%023x", -big, "-01234567890abcdef12345")
        testcommon("%-023x", -big, "-1234567890abcdef12345 ")
        testcommon("%025x", -big, "-0001234567890abcdef12345")
        testcommon("%025x", big, "00001234567890abcdef12345")
        testcommon("%0+25x", big, "+0001234567890abcdef12345")
        testcommon("%+25x", big, "   +1234567890abcdef12345")
        testcommon("%25x", big, "    1234567890abcdef12345")
        testcommon("%.2x", big, "1234567890abcdef12345")
        testcommon("%.21x", big, "1234567890abcdef12345")
        testcommon("%.22x", big, "01234567890abcdef12345")
        testcommon("%23.22x", big, " 01234567890abcdef12345")
        testcommon("%-23.22x", big, "01234567890abcdef12345 ")
        testcommon("%X", big, "1234567890ABCDEF12345")
        testcommon("%#X", big, "0X1234567890ABCDEF12345")
        testcommon("%#x", big, "0x1234567890abcdef12345")
        testcommon("%#x", -big, "-0x1234567890abcdef12345")
        testcommon("%#27x", big, "    0x1234567890abcdef12345")
        testcommon("%#-27x", big, "0x1234567890abcdef12345    ")
        testcommon("%#027x", big, "0x00001234567890abcdef12345")
        testcommon("%#.23x", big, "0x001234567890abcdef12345")
        testcommon("%#.23x", -big, "-0x001234567890abcdef12345")
        testcommon("%#27.23x", big, "  0x001234567890abcdef12345")
        testcommon("%#-27.23x", big, "0x001234567890abcdef12345  ")
        testcommon("%#027.23x", big, "0x00001234567890abcdef12345")
        testcommon("%#+.23x", big, "+0x001234567890abcdef12345")
        testcommon("%# .23x", big, " 0x001234567890abcdef12345")
        testcommon("%#+.23X", big, "+0X001234567890ABCDEF12345")
        # next one gets two leading zeroes kutoka precision, na another kutoka the
        # 0 flag na the width
        testcommon("%#+027.23X", big, "+0X0001234567890ABCDEF12345")
        testcommon("%# 027.23X", big, " 0X0001234567890ABCDEF12345")
        # same, tatizo no 0 flag
        testcommon("%#+27.23X", big, " +0X001234567890ABCDEF12345")
        testcommon("%#-+27.23x", big, "+0x001234567890abcdef12345 ")
        testcommon("%#- 27.23x", big, " 0x001234567890abcdef12345 ")

        big = 0o12345670123456701234567012345670  # 32 octal digits
        testcommon("%o", big, "12345670123456701234567012345670")
        testcommon("%o", -big, "-12345670123456701234567012345670")
        testcommon("%5o", -big, "-12345670123456701234567012345670")
        testcommon("%33o", -big, "-12345670123456701234567012345670")
        testcommon("%34o", -big, " -12345670123456701234567012345670")
        testcommon("%-34o", -big, "-12345670123456701234567012345670 ")
        testcommon("%034o", -big, "-012345670123456701234567012345670")
        testcommon("%-034o", -big, "-12345670123456701234567012345670 ")
        testcommon("%036o", -big, "-00012345670123456701234567012345670")
        testcommon("%036o", big, "000012345670123456701234567012345670")
        testcommon("%0+36o", big, "+00012345670123456701234567012345670")
        testcommon("%+36o", big, "   +12345670123456701234567012345670")
        testcommon("%36o", big, "    12345670123456701234567012345670")
        testcommon("%.2o", big, "12345670123456701234567012345670")
        testcommon("%.32o", big, "12345670123456701234567012345670")
        testcommon("%.33o", big, "012345670123456701234567012345670")
        testcommon("%34.33o", big, " 012345670123456701234567012345670")
        testcommon("%-34.33o", big, "012345670123456701234567012345670 ")
        testcommon("%o", big, "12345670123456701234567012345670")
        testcommon("%#o", big, "0o12345670123456701234567012345670")
        testcommon("%#o", -big, "-0o12345670123456701234567012345670")
        testcommon("%#38o", big, "    0o12345670123456701234567012345670")
        testcommon("%#-38o", big, "0o12345670123456701234567012345670    ")
        testcommon("%#038o", big, "0o000012345670123456701234567012345670")
        testcommon("%#.34o", big, "0o0012345670123456701234567012345670")
        testcommon("%#.34o", -big, "-0o0012345670123456701234567012345670")
        testcommon("%#38.34o", big, "  0o0012345670123456701234567012345670")
        testcommon("%#-38.34o", big, "0o0012345670123456701234567012345670  ")
        testcommon("%#038.34o", big, "0o000012345670123456701234567012345670")
        testcommon("%#+.34o", big, "+0o0012345670123456701234567012345670")
        testcommon("%# .34o", big, " 0o0012345670123456701234567012345670")
        testcommon("%#+38.34o", big, " +0o0012345670123456701234567012345670")
        testcommon("%#-+38.34o", big, "+0o0012345670123456701234567012345670 ")
        testcommon("%#- 38.34o", big, " 0o0012345670123456701234567012345670 ")
        testcommon("%#+038.34o", big, "+0o00012345670123456701234567012345670")
        testcommon("%# 038.34o", big, " 0o00012345670123456701234567012345670")
        # next one gets one leading zero kutoka precision
        testcommon("%.33o", big, "012345670123456701234567012345670")
        # base marker added kwenye spite of leading zero (different to Python 2)
        testcommon("%#.33o", big, "0o012345670123456701234567012345670")
        # reduce precision, na base marker ni always added
        testcommon("%#.32o", big, "0o12345670123456701234567012345670")
        # one leading zero kutoka precision, plus two kutoka "0" flag & width
        testcommon("%035.33o", big, "00012345670123456701234567012345670")
        # base marker shouldn't change the size
        testcommon("%0#35.33o", big, "0o012345670123456701234567012345670")

        # Some small ints, kwenye both Python int na flavors).
        testcommon("%d", 42, "42")
        testcommon("%d", -42, "-42")
        testcommon("%d", 42.0, "42")
        testcommon("%#x", 1, "0x1")
        testcommon("%#X", 1, "0X1")
        testcommon("%#o", 1, "0o1")
        testcommon("%#o", 0, "0o0")
        testcommon("%o", 0, "0")
        testcommon("%d", 0, "0")
        testcommon("%#x", 0, "0x0")
        testcommon("%#X", 0, "0X0")
        testcommon("%x", 0x42, "42")
        testcommon("%x", -0x42, "-42")
        testcommon("%o", 0o42, "42")
        testcommon("%o", -0o42, "-42")
        # alternate float formatting
        testcommon('%g', 1.1, '1.1')
        testcommon('%#g', 1.1, '1.10000')

        ikiwa verbose:
            andika('Testing exceptions')
        test_exc_common('%', (), ValueError, "incomplete format")
        test_exc_common('% %s', 1, ValueError,
                        "unsupported format character '%' (0x25) at index 2")
        test_exc_common('%d', '1', TypeError,
                        "%d format: a number ni required, sio str")
        test_exc_common('%d', b'1', TypeError,
                        "%d format: a number ni required, sio bytes")
        test_exc_common('%x', '1', TypeError,
                        "%x format: an integer ni required, sio str")
        test_exc_common('%x', 3.14, TypeError,
                        "%x format: an integer ni required, sio float")

    eleza test_str_format(self):
        testformat("%r", "\u0378", "'\\u0378'")  # non printable
        testformat("%a", "\u0378", "'\\u0378'")  # non printable
        testformat("%r", "\u0374", "'\u0374'")   # printable
        testformat("%a", "\u0374", "'\\u0374'")  # printable

        # Test exception kila unknown format characters, etc.
        ikiwa verbose:
            andika('Testing exceptions')
        test_exc('abc %b', 1, ValueError,
                 "unsupported format character 'b' (0x62) at index 5")
        #test_exc(unicode('abc %\u3000','raw-unicode-escape'), 1, ValueError,
        #         "unsupported format character '?' (0x3000) at index 5")
        test_exc('%g', '1', TypeError, "must be real number, sio str")
        test_exc('no format', '1', TypeError,
                 "not all arguments converted during string formatting")
        test_exc('%c', -1, OverflowError, "%c arg haiko kwenye range(0x110000)")
        test_exc('%c', sys.maxunicode+1, OverflowError,
                 "%c arg haiko kwenye range(0x110000)")
        #test_exc('%c', 2**128, OverflowError, "%c arg haiko kwenye range(0x110000)")
        test_exc('%c', 3.14, TypeError, "%c requires int ama char")
        test_exc('%c', 'ab', TypeError, "%c requires int ama char")
        test_exc('%c', b'x', TypeError, "%c requires int ama char")

        ikiwa maxsize == 2**31-1:
            # crashes 2.2.1 na earlier:
            jaribu:
                "%*d"%(maxsize, -127)
            tatizo MemoryError:
                pita
            isipokua:
                ashiria TestFailed('"%*d"%(maxsize, -127) should fail')

    eleza test_bytes_and_bytearray_format(self):
        # %c will insert a single byte, either kutoka an int kwenye range(256), or
        # kutoka a bytes argument of length 1, sio kutoka a str.
        testcommon(b"%c", 7, b"\x07")
        testcommon(b"%c", b"Z", b"Z")
        testcommon(b"%c", bytearray(b"Z"), b"Z")
        testcommon(b"%5c", 65, b"    A")
        testcommon(b"%-5c", 65, b"A    ")
        # %b will insert a series of bytes, either kutoka a type that supports
        # the Py_buffer protocol, ama something that has a __bytes__ method
        kundi FakeBytes(object):
            eleza __bytes__(self):
                rudisha b'123'
        fb = FakeBytes()
        testcommon(b"%b", b"abc", b"abc")
        testcommon(b"%b", bytearray(b"def"), b"def")
        testcommon(b"%b", fb, b"123")
        testcommon(b"%b", memoryview(b"abc"), b"abc")
        # # %s ni an alias kila %b -- should only be used kila Py2/3 code
        testcommon(b"%s", b"abc", b"abc")
        testcommon(b"%s", bytearray(b"def"), b"def")
        testcommon(b"%s", fb, b"123")
        testcommon(b"%s", memoryview(b"abc"), b"abc")
        # %a will give the equivalent of
        # repr(some_obj).encode('ascii', 'backslashreplace')
        testcommon(b"%a", 3.14, b"3.14")
        testcommon(b"%a", b"ghi", b"b'ghi'")
        testcommon(b"%a", "jkl", b"'jkl'")
        testcommon(b"%a", "\u0544", b"'\\u0544'")
        # %r ni an alias kila %a
        testcommon(b"%r", 3.14, b"3.14")
        testcommon(b"%r", b"ghi", b"b'ghi'")
        testcommon(b"%r", "jkl", b"'jkl'")
        testcommon(b"%r", "\u0544", b"'\\u0544'")

        # Test exception kila unknown format characters, etc.
        ikiwa verbose:
            andika('Testing exceptions')
        test_exc(b'%g', '1', TypeError, "float argument required, sio str")
        test_exc(b'%g', b'1', TypeError, "float argument required, sio bytes")
        test_exc(b'no format', 7, TypeError,
                 "not all arguments converted during bytes formatting")
        test_exc(b'no format', b'1', TypeError,
                 "not all arguments converted during bytes formatting")
        test_exc(b'no format', bytearray(b'1'), TypeError,
                 "not all arguments converted during bytes formatting")
        test_exc(b"%c", -1, OverflowError,
                "%c arg haiko kwenye range(256)")
        test_exc(b"%c", 256, OverflowError,
                "%c arg haiko kwenye range(256)")
        test_exc(b"%c", 2**128, OverflowError,
                "%c arg haiko kwenye range(256)")
        test_exc(b"%c", b"Za", TypeError,
                "%c requires an integer kwenye range(256) ama a single byte")
        test_exc(b"%c", "Y", TypeError,
                "%c requires an integer kwenye range(256) ama a single byte")
        test_exc(b"%c", 3.14, TypeError,
                "%c requires an integer kwenye range(256) ama a single byte")
        test_exc(b"%b", "Xc", TypeError,
                "%b requires a bytes-like object, "
                 "or an object that implements __bytes__, sio 'str'")
        test_exc(b"%s", "Wd", TypeError,
                "%b requires a bytes-like object, "
                 "or an object that implements __bytes__, sio 'str'")

        ikiwa maxsize == 2**31-1:
            # crashes 2.2.1 na earlier:
            jaribu:
                "%*d"%(maxsize, -127)
            tatizo MemoryError:
                pita
            isipokua:
                ashiria TestFailed('"%*d"%(maxsize, -127) should fail')

    eleza test_nul(self):
        # test the null character
        testcommon("a\0b", (), 'a\0b')
        testcommon("a%cb", (0,), 'a\0b')
        testformat("a%sb", ('c\0d',), 'ac\0db')
        testcommon(b"a%sb", (b'c\0d',), b'ac\0db')

    eleza test_non_ascii(self):
        testformat("\u20ac=%f", (1.0,), "\u20ac=1.000000")

        self.assertEqual(format("abc", "\u2007<5"), "abc\u2007\u2007")
        self.assertEqual(format(123, "\u2007<5"), "123\u2007\u2007")
        self.assertEqual(format(12.3, "\u2007<6"), "12.3\u2007\u2007")
        self.assertEqual(format(0j, "\u2007<4"), "0j\u2007\u2007")
        self.assertEqual(format(1+2j, "\u2007<8"), "(1+2j)\u2007\u2007")

        self.assertEqual(format("abc", "\u2007>5"), "\u2007\u2007abc")
        self.assertEqual(format(123, "\u2007>5"), "\u2007\u2007123")
        self.assertEqual(format(12.3, "\u2007>6"), "\u2007\u200712.3")
        self.assertEqual(format(1+2j, "\u2007>8"), "\u2007\u2007(1+2j)")
        self.assertEqual(format(0j, "\u2007>4"), "\u2007\u20070j")

        self.assertEqual(format("abc", "\u2007^5"), "\u2007abc\u2007")
        self.assertEqual(format(123, "\u2007^5"), "\u2007123\u2007")
        self.assertEqual(format(12.3, "\u2007^6"), "\u200712.3\u2007")
        self.assertEqual(format(1+2j, "\u2007^8"), "\u2007(1+2j)\u2007")
        self.assertEqual(format(0j, "\u2007^4"), "\u20070j\u2007")

    eleza test_locale(self):
        jaribu:
            oldloc = locale.setlocale(locale.LC_ALL)
            locale.setlocale(locale.LC_ALL, '')
        tatizo locale.Error kama err:
            self.skipTest("Cannot set locale: {}".format(err))
        jaribu:
            localeconv = locale.localeconv()
            sep = localeconv['thousands_sep']
            point = localeconv['decimal_point']

            text = format(123456789, "n")
            self.assertIn(sep, text)
            self.assertEqual(text.replace(sep, ''), '123456789')

            text = format(1234.5, "n")
            self.assertIn(sep, text)
            self.assertIn(point, text)
            self.assertEqual(text.replace(sep, ''), '1234' + point + '5')
        mwishowe:
            locale.setlocale(locale.LC_ALL, oldloc)

    @support.cpython_only
    eleza test_optimisations(self):
        text = "abcde" # 5 characters

        self.assertIs("%s" % text, text)
        self.assertIs("%.5s" % text, text)
        self.assertIs("%.10s" % text, text)
        self.assertIs("%1s" % text, text)
        self.assertIs("%5s" % text, text)

        self.assertIs("{0}".format(text), text)
        self.assertIs("{0:s}".format(text), text)
        self.assertIs("{0:.5s}".format(text), text)
        self.assertIs("{0:.10s}".format(text), text)
        self.assertIs("{0:1s}".format(text), text)
        self.assertIs("{0:5s}".format(text), text)

        self.assertIs(text % (), text)
        self.assertIs(text.format(), text)

    eleza test_precision(self):
        f = 1.2
        self.assertEqual(format(f, ".0f"), "1")
        self.assertEqual(format(f, ".3f"), "1.200")
        ukijumuisha self.assertRaises(ValueError) kama cm:
            format(f, ".%sf" % (sys.maxsize + 1))

        c = complex(f)
        self.assertEqual(format(c, ".0f"), "1+0j")
        self.assertEqual(format(c, ".3f"), "1.200+0.000j")
        ukijumuisha self.assertRaises(ValueError) kama cm:
            format(c, ".%sf" % (sys.maxsize + 1))

    @support.cpython_only
    eleza test_precision_c_limits(self):
        kutoka _testcapi agiza INT_MAX

        f = 1.2
        ukijumuisha self.assertRaises(ValueError) kama cm:
            format(f, ".%sf" % (INT_MAX + 1))

        c = complex(f)
        ukijumuisha self.assertRaises(ValueError) kama cm:
            format(c, ".%sf" % (INT_MAX + 1))


ikiwa __name__ == "__main__":
    unittest.main()
