# Python test set -- part 6, built-in types

kutoka test.support agiza run_with_locale
agiza collections.abc
agiza inspect
agiza pickle
agiza locale
agiza sys
agiza types
agiza unittest.mock
agiza weakref

kundi TypesTests(unittest.TestCase):

    eleza test_truth_values(self):
        ikiwa Tupu: self.fail('Tupu ni true instead of false')
        ikiwa 0: self.fail('0 ni true instead of false')
        ikiwa 0.0: self.fail('0.0 ni true instead of false')
        ikiwa '': self.fail('\'\' ni true instead of false')
        ikiwa sio 1: self.fail('1 ni false instead of true')
        ikiwa sio 1.0: self.fail('1.0 ni false instead of true')
        ikiwa sio 'x': self.fail('\'x\' ni false instead of true')
        ikiwa sio {'x': 1}: self.fail('{\'x\': 1} ni false instead of true')
        eleza f(): pita
        kundi C: pita
        x = C()
        ikiwa sio f: self.fail('f ni false instead of true')
        ikiwa sio C: self.fail('C ni false instead of true')
        ikiwa sio sys: self.fail('sys ni false instead of true')
        ikiwa sio x: self.fail('x ni false instead of true')

    eleza test_boolean_ops(self):
        ikiwa 0 ama 0: self.fail('0 ama 0 ni true instead of false')
        ikiwa 1 na 1: pita
        isipokua: self.fail('1 na 1 ni false instead of true')
        ikiwa sio 1: self.fail('not 1 ni true instead of false')

    eleza test_comparisons(self):
        ikiwa 0 < 1 <= 1 == 1 >= 1 > 0 != 1: pita
        isipokua: self.fail('int comparisons failed')
        ikiwa 0.0 < 1.0 <= 1.0 == 1.0 >= 1.0 > 0.0 != 1.0: pita
        isipokua: self.fail('float comparisons failed')
        ikiwa '' < 'a' <= 'a' == 'a' < 'abc' < 'abd' < 'b': pita
        isipokua: self.fail('string comparisons failed')
        ikiwa Tupu ni Tupu: pita
        isipokua: self.fail('identity test failed')

    eleza test_float_constructor(self):
        self.assertRaises(ValueError, float, '')
        self.assertRaises(ValueError, float, '5\0')
        self.assertRaises(ValueError, float, '5_5\0')

    eleza test_zero_division(self):
        jaribu: 5.0 / 0.0
        tatizo ZeroDivisionError: pita
        isipokua: self.fail("5.0 / 0.0 didn't ashiria ZeroDivisionError")

        jaribu: 5.0 // 0.0
        tatizo ZeroDivisionError: pita
        isipokua: self.fail("5.0 // 0.0 didn't ashiria ZeroDivisionError")

        jaribu: 5.0 % 0.0
        tatizo ZeroDivisionError: pita
        isipokua: self.fail("5.0 % 0.0 didn't ashiria ZeroDivisionError")

        jaribu: 5 / 0
        tatizo ZeroDivisionError: pita
        isipokua: self.fail("5 / 0 didn't ashiria ZeroDivisionError")

        jaribu: 5 // 0
        tatizo ZeroDivisionError: pita
        isipokua: self.fail("5 // 0 didn't ashiria ZeroDivisionError")

        jaribu: 5 % 0
        tatizo ZeroDivisionError: pita
        isipokua: self.fail("5 % 0 didn't ashiria ZeroDivisionError")

    eleza test_numeric_types(self):
        ikiwa 0 != 0.0 ama 1 != 1.0 ama -1 != -1.0:
            self.fail('int/float value sio equal')
        # calling built-in types without argument must rudisha 0
        ikiwa int() != 0: self.fail('int() does sio rudisha 0')
        ikiwa float() != 0.0: self.fail('float() does sio rudisha 0.0')
        ikiwa int(1.9) == 1 == int(1.1) na int(-1.1) == -1 == int(-1.9): pita
        isipokua: self.fail('int() does sio round properly')
        ikiwa float(1) == 1.0 na float(-1) == -1.0 na float(0) == 0.0: pita
        isipokua: self.fail('float() does sio work properly')

    eleza test_float_to_string(self):
        eleza test(f, result):
            self.assertEqual(f.__format__('e'), result)
            self.assertEqual('%e' % f, result)

        # test all 2 digit exponents, both ukijumuisha __format__ na with
        #  '%' formatting
        kila i kwenye range(-99, 100):
            test(float('1.5e'+str(i)), '1.500000e{0:+03d}'.format(i))

        # test some 3 digit exponents
        self.assertEqual(1.5e100.__format__('e'), '1.500000e+100')
        self.assertEqual('%e' % 1.5e100, '1.500000e+100')

        self.assertEqual(1.5e101.__format__('e'), '1.500000e+101')
        self.assertEqual('%e' % 1.5e101, '1.500000e+101')

        self.assertEqual(1.5e-100.__format__('e'), '1.500000e-100')
        self.assertEqual('%e' % 1.5e-100, '1.500000e-100')

        self.assertEqual(1.5e-101.__format__('e'), '1.500000e-101')
        self.assertEqual('%e' % 1.5e-101, '1.500000e-101')

        self.assertEqual('%g' % 1.0, '1')
        self.assertEqual('%#g' % 1.0, '1.00000')

    eleza test_normal_integers(self):
        # Ensure the first 256 integers are shared
        a = 256
        b = 128*2
        ikiwa a ni sio b: self.fail('256 ni sio shared')
        ikiwa 12 + 24 != 36: self.fail('int op')
        ikiwa 12 + (-24) != -12: self.fail('int op')
        ikiwa (-12) + 24 != 12: self.fail('int op')
        ikiwa (-12) + (-24) != -36: self.fail('int op')
        ikiwa sio 12 < 24: self.fail('int op')
        ikiwa sio -24 < -12: self.fail('int op')
        # Test kila a particular bug kwenye integer multiply
        xsize, ysize, zsize = 238, 356, 4
        ikiwa sio (xsize*ysize*zsize == zsize*xsize*ysize == 338912):
            self.fail('int mul commutativity')
        # And another.
        m = -sys.maxsize - 1
        kila divisor kwenye 1, 2, 4, 8, 16, 32:
            j = m // divisor
            prod = divisor * j
            ikiwa prod != m:
                self.fail("%r * %r == %r != %r" % (divisor, j, prod, m))
            ikiwa type(prod) ni sio int:
                self.fail("expected type(prod) to be int, sio %r" %
                                   type(prod))
        # Check kila unified integral type
        kila divisor kwenye 1, 2, 4, 8, 16, 32:
            j = m // divisor - 1
            prod = divisor * j
            ikiwa type(prod) ni sio int:
                self.fail("expected type(%r) to be int, sio %r" %
                                   (prod, type(prod)))
        # Check kila unified integral type
        m = sys.maxsize
        kila divisor kwenye 1, 2, 4, 8, 16, 32:
            j = m // divisor + 1
            prod = divisor * j
            ikiwa type(prod) ni sio int:
                self.fail("expected type(%r) to be int, sio %r" %
                                   (prod, type(prod)))

        x = sys.maxsize
        self.assertIsInstance(x + 1, int,
                              "(sys.maxsize + 1) should have returned int")
        self.assertIsInstance(-x - 1, int,
                              "(-sys.maxsize - 1) should have returned int")
        self.assertIsInstance(-x - 2, int,
                              "(-sys.maxsize - 2) should have returned int")

        jaribu: 5 << -5
        tatizo ValueError: pita
        isipokua: self.fail('int negative shift <<')

        jaribu: 5 >> -5
        tatizo ValueError: pita
        isipokua: self.fail('int negative shift >>')

    eleza test_floats(self):
        ikiwa 12.0 + 24.0 != 36.0: self.fail('float op')
        ikiwa 12.0 + (-24.0) != -12.0: self.fail('float op')
        ikiwa (-12.0) + 24.0 != 12.0: self.fail('float op')
        ikiwa (-12.0) + (-24.0) != -36.0: self.fail('float op')
        ikiwa sio 12.0 < 24.0: self.fail('float op')
        ikiwa sio -24.0 < -12.0: self.fail('float op')

    eleza test_strings(self):
        ikiwa len('') != 0: self.fail('len(\'\')')
        ikiwa len('a') != 1: self.fail('len(\'a\')')
        ikiwa len('abcdef') != 6: self.fail('len(\'abcdef\')')
        ikiwa 'xyz' + 'abcde' != 'xyzabcde': self.fail('string concatenation')
        ikiwa 'xyz'*3 != 'xyzxyzxyz': self.fail('string repetition *3')
        ikiwa 0*'abcde' != '': self.fail('string repetition 0*')
        ikiwa min('abc') != 'a' ama max('abc') != 'c': self.fail('min/max string')
        ikiwa 'a' kwenye 'abc' na 'b' kwenye 'abc' na 'c' kwenye 'abc' na 'd' haiko kwenye 'abc': pita
        isipokua: self.fail('in/not kwenye string')
        x = 'x'*103
        ikiwa '%s!'%x != x+'!': self.fail('nasty string formatting bug')

        #extended slices kila strings
        a = '0123456789'
        self.assertEqual(a[::], a)
        self.assertEqual(a[::2], '02468')
        self.assertEqual(a[1::2], '13579')
        self.assertEqual(a[::-1],'9876543210')
        self.assertEqual(a[::-2], '97531')
        self.assertEqual(a[3::-2], '31')
        self.assertEqual(a[-100:100:], a)
        self.assertEqual(a[100:-100:-1], a[::-1])
        self.assertEqual(a[-100:100:2], '02468')

    eleza test_type_function(self):
        self.assertRaises(TypeError, type, 1, 2)
        self.assertRaises(TypeError, type, 1, 2, 3, 4)

    eleza test_int__format__(self):
        eleza test(i, format_spec, result):
            # just make sure we have the unified type kila integers
            assert type(i) == int
            assert type(format_spec) == str
            self.assertEqual(i.__format__(format_spec), result)

        test(123456789, 'd', '123456789')
        test(123456789, 'd', '123456789')

        test(1, 'c', '\01')

        # sign na aligning are interdependent
        test(1, "-", '1')
        test(-1, "-", '-1')
        test(1, "-3", '  1')
        test(-1, "-3", ' -1')
        test(1, "+3", ' +1')
        test(-1, "+3", ' -1')
        test(1, " 3", '  1')
        test(-1, " 3", ' -1')
        test(1, " ", ' 1')
        test(-1, " ", '-1')

        # hex
        test(3, "x", "3")
        test(3, "X", "3")
        test(1234, "x", "4d2")
        test(-1234, "x", "-4d2")
        test(1234, "8x", "     4d2")
        test(-1234, "8x", "    -4d2")
        test(1234, "x", "4d2")
        test(-1234, "x", "-4d2")
        test(-3, "x", "-3")
        test(-3, "X", "-3")
        test(int('be', 16), "x", "be")
        test(int('be', 16), "X", "BE")
        test(-int('be', 16), "x", "-be")
        test(-int('be', 16), "X", "-BE")

        # octal
        test(3, "o", "3")
        test(-3, "o", "-3")
        test(65, "o", "101")
        test(-65, "o", "-101")
        test(1234, "o", "2322")
        test(-1234, "o", "-2322")
        test(1234, "-o", "2322")
        test(-1234, "-o", "-2322")
        test(1234, " o", " 2322")
        test(-1234, " o", "-2322")
        test(1234, "+o", "+2322")
        test(-1234, "+o", "-2322")

        # binary
        test(3, "b", "11")
        test(-3, "b", "-11")
        test(1234, "b", "10011010010")
        test(-1234, "b", "-10011010010")
        test(1234, "-b", "10011010010")
        test(-1234, "-b", "-10011010010")
        test(1234, " b", " 10011010010")
        test(-1234, " b", "-10011010010")
        test(1234, "+b", "+10011010010")
        test(-1234, "+b", "-10011010010")

        # alternate (#) formatting
        test(0, "#b", '0b0')
        test(0, "-#b", '0b0')
        test(1, "-#b", '0b1')
        test(-1, "-#b", '-0b1')
        test(-1, "-#5b", ' -0b1')
        test(1, "+#5b", ' +0b1')
        test(100, "+#b", '+0b1100100')
        test(100, "#012b", '0b0001100100')
        test(-100, "#012b", '-0b001100100')

        test(0, "#o", '0o0')
        test(0, "-#o", '0o0')
        test(1, "-#o", '0o1')
        test(-1, "-#o", '-0o1')
        test(-1, "-#5o", ' -0o1')
        test(1, "+#5o", ' +0o1')
        test(100, "+#o", '+0o144')
        test(100, "#012o", '0o0000000144')
        test(-100, "#012o", '-0o000000144')

        test(0, "#x", '0x0')
        test(0, "-#x", '0x0')
        test(1, "-#x", '0x1')
        test(-1, "-#x", '-0x1')
        test(-1, "-#5x", ' -0x1')
        test(1, "+#5x", ' +0x1')
        test(100, "+#x", '+0x64')
        test(100, "#012x", '0x0000000064')
        test(-100, "#012x", '-0x000000064')
        test(123456, "#012x", '0x000001e240')
        test(-123456, "#012x", '-0x00001e240')

        test(0, "#X", '0X0')
        test(0, "-#X", '0X0')
        test(1, "-#X", '0X1')
        test(-1, "-#X", '-0X1')
        test(-1, "-#5X", ' -0X1')
        test(1, "+#5X", ' +0X1')
        test(100, "+#X", '+0X64')
        test(100, "#012X", '0X0000000064')
        test(-100, "#012X", '-0X000000064')
        test(123456, "#012X", '0X000001E240')
        test(-123456, "#012X", '-0X00001E240')

        test(123, ',', '123')
        test(-123, ',', '-123')
        test(1234, ',', '1,234')
        test(-1234, ',', '-1,234')
        test(123456, ',', '123,456')
        test(-123456, ',', '-123,456')
        test(1234567, ',', '1,234,567')
        test(-1234567, ',', '-1,234,567')

        # issue 5782, commas ukijumuisha no specifier type
        test(1234, '010,', '00,001,234')

        # Unified type kila integers
        test(10**100, 'd', '1' + '0' * 100)
        test(10**100+100, 'd', '1' + '0' * 97 + '100')

        # make sure these are errors

        # precision disallowed
        self.assertRaises(ValueError, 3 .__format__, "1.3")
        # sign sio allowed ukijumuisha 'c'
        self.assertRaises(ValueError, 3 .__format__, "+c")
        # format spec must be string
        self.assertRaises(TypeError, 3 .__format__, Tupu)
        self.assertRaises(TypeError, 3 .__format__, 0)
        # can't have ',' ukijumuisha 'n'
        self.assertRaises(ValueError, 3 .__format__, ",n")
        # can't have ',' ukijumuisha 'c'
        self.assertRaises(ValueError, 3 .__format__, ",c")
        # can't have '#' ukijumuisha 'c'
        self.assertRaises(ValueError, 3 .__format__, "#c")

        # ensure that only int na float type specifiers work
        kila format_spec kwenye ([chr(x) kila x kwenye range(ord('a'), ord('z')+1)] +
                            [chr(x) kila x kwenye range(ord('A'), ord('Z')+1)]):
            ikiwa sio format_spec kwenye 'bcdoxXeEfFgGn%':
                self.assertRaises(ValueError, 0 .__format__, format_spec)
                self.assertRaises(ValueError, 1 .__format__, format_spec)
                self.assertRaises(ValueError, (-1) .__format__, format_spec)

        # ensure that float type specifiers work; format converts
        #  the int to a float
        kila format_spec kwenye 'eEfFgG%':
            kila value kwenye [0, 1, -1, 100, -100, 1234567890, -1234567890]:
                self.assertEqual(value.__format__(format_spec),
                                 float(value).__format__(format_spec))

        # Issue 6902
        test(123456, "0<20", '12345600000000000000')
        test(123456, "1<20", '12345611111111111111')
        test(123456, "*<20", '123456**************')
        test(123456, "0>20", '00000000000000123456')
        test(123456, "1>20", '11111111111111123456')
        test(123456, "*>20", '**************123456')
        test(123456, "0=20", '00000000000000123456')
        test(123456, "1=20", '11111111111111123456')
        test(123456, "*=20", '**************123456')

    @run_with_locale('LC_NUMERIC', 'en_US.UTF8')
    eleza test_float__format__locale(self):
        # test locale support kila __format__ code 'n'

        kila i kwenye range(-10, 10):
            x = 1234567890.0 * (10.0 ** i)
            self.assertEqual(locale.format_string('%g', x, grouping=Kweli), format(x, 'n'))
            self.assertEqual(locale.format_string('%.10g', x, grouping=Kweli), format(x, '.10n'))

    @run_with_locale('LC_NUMERIC', 'en_US.UTF8')
    eleza test_int__format__locale(self):
        # test locale support kila __format__ code 'n' kila integers

        x = 123456789012345678901234567890
        kila i kwenye range(0, 30):
            self.assertEqual(locale.format_string('%d', x, grouping=Kweli), format(x, 'n'))

            # move to the next integer to test
            x = x // 10

        rfmt = ">20n"
        lfmt = "<20n"
        cfmt = "^20n"
        kila x kwenye (1234, 12345, 123456, 1234567, 12345678, 123456789, 1234567890, 12345678900):
            self.assertEqual(len(format(0, rfmt)), len(format(x, rfmt)))
            self.assertEqual(len(format(0, lfmt)), len(format(x, lfmt)))
            self.assertEqual(len(format(0, cfmt)), len(format(x, cfmt)))

    eleza test_float__format__(self):
        eleza test(f, format_spec, result):
            self.assertEqual(f.__format__(format_spec), result)
            self.assertEqual(format(f, format_spec), result)

        test(0.0, 'f', '0.000000')

        # the default ni 'g', tatizo kila empty format spec
        test(0.0, '', '0.0')
        test(0.01, '', '0.01')
        test(0.01, 'g', '0.01')

        # test kila issue 3411
        test(1.23, '1', '1.23')
        test(-1.23, '1', '-1.23')
        test(1.23, '1g', '1.23')
        test(-1.23, '1g', '-1.23')

        test( 1.0, ' g', ' 1')
        test(-1.0, ' g', '-1')
        test( 1.0, '+g', '+1')
        test(-1.0, '+g', '-1')
        test(1.1234e200, 'g', '1.1234e+200')
        test(1.1234e200, 'G', '1.1234E+200')


        test(1.0, 'f', '1.000000')

        test(-1.0, 'f', '-1.000000')

        test( 1.0, ' f', ' 1.000000')
        test(-1.0, ' f', '-1.000000')
        test( 1.0, '+f', '+1.000000')
        test(-1.0, '+f', '-1.000000')

        # Python versions <= 3.0 switched kutoka 'f' to 'g' formatting for
        # values larger than 1e50.  No longer.
        f = 1.1234e90
        kila fmt kwenye 'f', 'F':
            # don't do a direct equality check, since on some
            # platforms only the first few digits of dtoa
            # will be reliable
            result = f.__format__(fmt)
            self.assertEqual(len(result), 98)
            self.assertEqual(result[-7], '.')
            self.assertIn(result[:12], ('112340000000', '112339999999'))
        f = 1.1234e200
        kila fmt kwenye 'f', 'F':
            result = f.__format__(fmt)
            self.assertEqual(len(result), 208)
            self.assertEqual(result[-7], '.')
            self.assertIn(result[:12], ('112340000000', '112339999999'))


        test( 1.0, 'e', '1.000000e+00')
        test(-1.0, 'e', '-1.000000e+00')
        test( 1.0, 'E', '1.000000E+00')
        test(-1.0, 'E', '-1.000000E+00')
        test(1.1234e20, 'e', '1.123400e+20')
        test(1.1234e20, 'E', '1.123400E+20')

        # No format code means use g, but must have a decimal
        # na a number after the decimal.  This ni tricky, because
        # a totaly empty format specifier means something else.
        # So, just use a sign flag
        test(1e200, '+g', '+1e+200')
        test(1e200, '+', '+1e+200')

        test(1.1e200, '+g', '+1.1e+200')
        test(1.1e200, '+', '+1.1e+200')

        # 0 padding
        test(1234., '010f', '1234.000000')
        test(1234., '011f', '1234.000000')
        test(1234., '012f', '01234.000000')
        test(-1234., '011f', '-1234.000000')
        test(-1234., '012f', '-1234.000000')
        test(-1234., '013f', '-01234.000000')
        test(-1234.12341234, '013f', '-01234.123412')
        test(-123456.12341234, '011.2f', '-0123456.12')

        # issue 5782, commas ukijumuisha no specifier type
        test(1.2, '010,.2', '0,000,001.2')

        # 0 padding ukijumuisha commas
        test(1234., '011,f', '1,234.000000')
        test(1234., '012,f', '1,234.000000')
        test(1234., '013,f', '01,234.000000')
        test(-1234., '012,f', '-1,234.000000')
        test(-1234., '013,f', '-1,234.000000')
        test(-1234., '014,f', '-01,234.000000')
        test(-12345., '015,f', '-012,345.000000')
        test(-123456., '016,f', '-0,123,456.000000')
        test(-123456., '017,f', '-0,123,456.000000')
        test(-123456.12341234, '017,f', '-0,123,456.123412')
        test(-123456.12341234, '013,.2f', '-0,123,456.12')

        # % formatting
        test(-1.0, '%', '-100.000000%')

        # format spec must be string
        self.assertRaises(TypeError, 3.0.__format__, Tupu)
        self.assertRaises(TypeError, 3.0.__format__, 0)

        # other format specifiers shouldn't work on floats,
        #  kwenye particular int specifiers
        kila format_spec kwenye ([chr(x) kila x kwenye range(ord('a'), ord('z')+1)] +
                            [chr(x) kila x kwenye range(ord('A'), ord('Z')+1)]):
            ikiwa sio format_spec kwenye 'eEfFgGn%':
                self.assertRaises(ValueError, format, 0.0, format_spec)
                self.assertRaises(ValueError, format, 1.0, format_spec)
                self.assertRaises(ValueError, format, -1.0, format_spec)
                self.assertRaises(ValueError, format, 1e100, format_spec)
                self.assertRaises(ValueError, format, -1e100, format_spec)
                self.assertRaises(ValueError, format, 1e-100, format_spec)
                self.assertRaises(ValueError, format, -1e-100, format_spec)

        # Alternate float formatting
        test(1.0, '.0e', '1e+00')
        test(1.0, '#.0e', '1.e+00')
        test(1.0, '.0f', '1')
        test(1.0, '#.0f', '1.')
        test(1.1, 'g', '1.1')
        test(1.1, '#g', '1.10000')
        test(1.0, '.0%', '100%')
        test(1.0, '#.0%', '100.%')

        # Issue 7094: Alternate formatting (specified by #)
        test(1.0, '0e',  '1.000000e+00')
        test(1.0, '#0e', '1.000000e+00')
        test(1.0, '0f',  '1.000000' )
        test(1.0, '#0f', '1.000000')
        test(1.0, '.1e',  '1.0e+00')
        test(1.0, '#.1e', '1.0e+00')
        test(1.0, '.1f',  '1.0')
        test(1.0, '#.1f', '1.0')
        test(1.0, '.1%',  '100.0%')
        test(1.0, '#.1%', '100.0%')

        # Issue 6902
        test(12345.6, "0<20", '12345.60000000000000')
        test(12345.6, "1<20", '12345.61111111111111')
        test(12345.6, "*<20", '12345.6*************')
        test(12345.6, "0>20", '000000000000012345.6')
        test(12345.6, "1>20", '111111111111112345.6')
        test(12345.6, "*>20", '*************12345.6')
        test(12345.6, "0=20", '000000000000012345.6')
        test(12345.6, "1=20", '111111111111112345.6')
        test(12345.6, "*=20", '*************12345.6')

    eleza test_format_spec_errors(self):
        # int, float, na string all share the same format spec
        # mini-language parser.

        # Check that we can't ask kila too many digits. This is
        # probably a CPython specific test. It tries to put the width
        # into a C long.
        self.assertRaises(ValueError, format, 0, '1'*10000 + 'd')

        # Similar ukijumuisha the precision.
        self.assertRaises(ValueError, format, 0, '.' + '1'*10000 + 'd')

        # And may kama well test both.
        self.assertRaises(ValueError, format, 0, '1'*1000 + '.' + '1'*10000 + 'd')

        # Make sure commas aren't allowed ukijumuisha various type codes
        kila code kwenye 'xXobns':
            self.assertRaises(ValueError, format, 0, ',' + code)

    eleza test_internal_sizes(self):
        self.assertGreater(object.__basicsize__, 0)
        self.assertGreater(tuple.__itemsize__, 0)

    eleza test_slot_wrapper_types(self):
        self.assertIsInstance(object.__init__, types.WrapperDescriptorType)
        self.assertIsInstance(object.__str__, types.WrapperDescriptorType)
        self.assertIsInstance(object.__lt__, types.WrapperDescriptorType)
        self.assertIsInstance(int.__lt__, types.WrapperDescriptorType)

    eleza test_method_wrapper_types(self):
        self.assertIsInstance(object().__init__, types.MethodWrapperType)
        self.assertIsInstance(object().__str__, types.MethodWrapperType)
        self.assertIsInstance(object().__lt__, types.MethodWrapperType)
        self.assertIsInstance((42).__lt__, types.MethodWrapperType)

    eleza test_method_descriptor_types(self):
        self.assertIsInstance(str.join, types.MethodDescriptorType)
        self.assertIsInstance(list.append, types.MethodDescriptorType)
        self.assertIsInstance(''.join, types.BuiltinMethodType)
        self.assertIsInstance([].append, types.BuiltinMethodType)

        self.assertIsInstance(int.__dict__['from_bytes'], types.ClassMethodDescriptorType)
        self.assertIsInstance(int.from_bytes, types.BuiltinMethodType)
        self.assertIsInstance(int.__new__, types.BuiltinMethodType)


kundi MappingProxyTests(unittest.TestCase):
    mappingproxy = types.MappingProxyType

    eleza test_constructor(self):
        kundi userdict(dict):
            pita

        mapping = {'x': 1, 'y': 2}
        self.assertEqual(self.mappingproxy(mapping), mapping)
        mapping = userdict(x=1, y=2)
        self.assertEqual(self.mappingproxy(mapping), mapping)
        mapping = collections.ChainMap({'x': 1}, {'y': 2})
        self.assertEqual(self.mappingproxy(mapping), mapping)

        self.assertRaises(TypeError, self.mappingproxy, 10)
        self.assertRaises(TypeError, self.mappingproxy, ("a", "tuple"))
        self.assertRaises(TypeError, self.mappingproxy, ["a", "list"])

    eleza test_methods(self):
        attrs = set(dir(self.mappingproxy({}))) - set(dir(object()))
        self.assertEqual(attrs, {
             '__contains__',
             '__getitem__',
             '__iter__',
             '__len__',
             'copy',
             'get',
             'items',
             'keys',
             'values',
        })

    eleza test_get(self):
        view = self.mappingproxy({'a': 'A', 'b': 'B'})
        self.assertEqual(view['a'], 'A')
        self.assertEqual(view['b'], 'B')
        self.assertRaises(KeyError, view.__getitem__, 'xxx')
        self.assertEqual(view.get('a'), 'A')
        self.assertIsTupu(view.get('xxx'))
        self.assertEqual(view.get('xxx', 42), 42)

    eleza test_missing(self):
        kundi dictmissing(dict):
            eleza __missing__(self, key):
                rudisha "missing=%s" % key

        view = self.mappingproxy(dictmissing(x=1))
        self.assertEqual(view['x'], 1)
        self.assertEqual(view['y'], 'missing=y')
        self.assertEqual(view.get('x'), 1)
        self.assertEqual(view.get('y'), Tupu)
        self.assertEqual(view.get('y', 42), 42)
        self.assertKweli('x' kwenye view)
        self.assertUongo('y' kwenye view)

    eleza test_customdict(self):
        kundi customdict(dict):
            eleza __contains__(self, key):
                ikiwa key == 'magic':
                    rudisha Kweli
                isipokua:
                    rudisha dict.__contains__(self, key)

            eleza __iter__(self):
                rudisha iter(('iter',))

            eleza __len__(self):
                rudisha 500

            eleza copy(self):
                rudisha 'copy'

            eleza keys(self):
                rudisha 'keys'

            eleza items(self):
                rudisha 'items'

            eleza values(self):
                rudisha 'values'

            eleza __getitem__(self, key):
                rudisha "getitem=%s" % dict.__getitem__(self, key)

            eleza get(self, key, default=Tupu):
                rudisha "get=%s" % dict.get(self, key, 'default=%r' % default)

        custom = customdict({'key': 'value'})
        view = self.mappingproxy(custom)
        self.assertKweli('key' kwenye view)
        self.assertKweli('magic' kwenye view)
        self.assertUongo('xxx' kwenye view)
        self.assertEqual(view['key'], 'getitem=value')
        self.assertRaises(KeyError, view.__getitem__, 'xxx')
        self.assertEqual(tuple(view), ('iter',))
        self.assertEqual(len(view), 500)
        self.assertEqual(view.copy(), 'copy')
        self.assertEqual(view.get('key'), 'get=value')
        self.assertEqual(view.get('xxx'), 'get=default=Tupu')
        self.assertEqual(view.items(), 'items')
        self.assertEqual(view.keys(), 'keys')
        self.assertEqual(view.values(), 'values')

    eleza test_chainmap(self):
        d1 = {'x': 1}
        d2 = {'y': 2}
        mapping = collections.ChainMap(d1, d2)
        view = self.mappingproxy(mapping)
        self.assertKweli('x' kwenye view)
        self.assertKweli('y' kwenye view)
        self.assertUongo('z' kwenye view)
        self.assertEqual(view['x'], 1)
        self.assertEqual(view['y'], 2)
        self.assertRaises(KeyError, view.__getitem__, 'z')
        self.assertEqual(tuple(sorted(view)), ('x', 'y'))
        self.assertEqual(len(view), 2)
        copy = view.copy()
        self.assertIsNot(copy, mapping)
        self.assertIsInstance(copy, collections.ChainMap)
        self.assertEqual(copy, mapping)
        self.assertEqual(view.get('x'), 1)
        self.assertEqual(view.get('y'), 2)
        self.assertIsTupu(view.get('z'))
        self.assertEqual(tuple(sorted(view.items())), (('x', 1), ('y', 2)))
        self.assertEqual(tuple(sorted(view.keys())), ('x', 'y'))
        self.assertEqual(tuple(sorted(view.values())), (1, 2))

    eleza test_contains(self):
        view = self.mappingproxy(dict.fromkeys('abc'))
        self.assertKweli('a' kwenye view)
        self.assertKweli('b' kwenye view)
        self.assertKweli('c' kwenye view)
        self.assertUongo('xxx' kwenye view)

    eleza test_views(self):
        mapping = {}
        view = self.mappingproxy(mapping)
        keys = view.keys()
        values = view.values()
        items = view.items()
        self.assertEqual(list(keys), [])
        self.assertEqual(list(values), [])
        self.assertEqual(list(items), [])
        mapping['key'] = 'value'
        self.assertEqual(list(keys), ['key'])
        self.assertEqual(list(values), ['value'])
        self.assertEqual(list(items), [('key', 'value')])

    eleza test_len(self):
        kila expected kwenye range(6):
            data = dict.fromkeys('abcde'[:expected])
            self.assertEqual(len(data), expected)
            view = self.mappingproxy(data)
            self.assertEqual(len(view), expected)

    eleza test_iterators(self):
        keys = ('x', 'y')
        values = (1, 2)
        items = tuple(zip(keys, values))
        view = self.mappingproxy(dict(items))
        self.assertEqual(set(view), set(keys))
        self.assertEqual(set(view.keys()), set(keys))
        self.assertEqual(set(view.values()), set(values))
        self.assertEqual(set(view.items()), set(items))

    eleza test_copy(self):
        original = {'key1': 27, 'key2': 51, 'key3': 93}
        view = self.mappingproxy(original)
        copy = view.copy()
        self.assertEqual(type(copy), dict)
        self.assertEqual(copy, original)
        original['key1'] = 70
        self.assertEqual(view['key1'], 70)
        self.assertEqual(copy['key1'], 27)


kundi ClassCreationTests(unittest.TestCase):

    kundi Meta(type):
        eleza __init__(cls, name, bases, ns, **kw):
            super().__init__(name, bases, ns)
        @staticmethod
        eleza __new__(mcls, name, bases, ns, **kw):
            rudisha super().__new__(mcls, name, bases, ns)
        @classmethod
        eleza __prepare__(mcls, name, bases, **kw):
            ns = super().__prepare__(name, bases)
            ns["y"] = 1
            ns.update(kw)
            rudisha ns

    eleza test_new_class_basics(self):
        C = types.new_class("C")
        self.assertEqual(C.__name__, "C")
        self.assertEqual(C.__bases__, (object,))

    eleza test_new_class_subclass(self):
        C = types.new_class("C", (int,))
        self.assertKweli(issubclass(C, int))

    eleza test_new_class_meta(self):
        Meta = self.Meta
        settings = {"metaclass": Meta, "z": 2}
        # We do this twice to make sure the pitaed kwenye dict isn't mutated
        kila i kwenye range(2):
            C = types.new_class("C" + str(i), (), settings)
            self.assertIsInstance(C, Meta)
            self.assertEqual(C.y, 1)
            self.assertEqual(C.z, 2)

    eleza test_new_class_exec_body(self):
        Meta = self.Meta
        eleza func(ns):
            ns["x"] = 0
        C = types.new_class("C", (), {"metaclass": Meta, "z": 2}, func)
        self.assertIsInstance(C, Meta)
        self.assertEqual(C.x, 0)
        self.assertEqual(C.y, 1)
        self.assertEqual(C.z, 2)

    eleza test_new_class_metaclass_keywords(self):
        #Test that keywords are pitaed to the metaclass:
        eleza meta_func(name, bases, ns, **kw):
            rudisha name, bases, ns, kw
        res = types.new_class("X",
                              (int, object),
                              dict(metaclass=meta_func, x=0))
        self.assertEqual(res, ("X", (int, object), {}, {"x": 0}))

    eleza test_new_class_defaults(self):
        # Test defaults/keywords:
        C = types.new_class("C", (), {}, Tupu)
        self.assertEqual(C.__name__, "C")
        self.assertEqual(C.__bases__, (object,))

    eleza test_new_class_meta_with_base(self):
        Meta = self.Meta
        eleza func(ns):
            ns["x"] = 0
        C = types.new_class(name="C",
                            bases=(int,),
                            kwds=dict(metaclass=Meta, z=2),
                            exec_body=func)
        self.assertKweli(issubclass(C, int))
        self.assertIsInstance(C, Meta)
        self.assertEqual(C.x, 0)
        self.assertEqual(C.y, 1)
        self.assertEqual(C.z, 2)

    eleza test_new_class_with_mro_entry(self):
        kundi A: pita
        kundi C:
            eleza __mro_entries__(self, bases):
                rudisha (A,)
        c = C()
        D = types.new_class('D', (c,), {})
        self.assertEqual(D.__bases__, (A,))
        self.assertEqual(D.__orig_bases__, (c,))
        self.assertEqual(D.__mro__, (D, A, object))

    eleza test_new_class_with_mro_entry_none(self):
        kundi A: pita
        kundi B: pita
        kundi C:
            eleza __mro_entries__(self, bases):
                rudisha ()
        c = C()
        D = types.new_class('D', (A, c, B), {})
        self.assertEqual(D.__bases__, (A, B))
        self.assertEqual(D.__orig_bases__, (A, c, B))
        self.assertEqual(D.__mro__, (D, A, B, object))

    eleza test_new_class_with_mro_entry_error(self):
        kundi A: pita
        kundi C:
            eleza __mro_entries__(self, bases):
                rudisha A
        c = C()
        ukijumuisha self.assertRaises(TypeError):
            types.new_class('D', (c,), {})

    eleza test_new_class_with_mro_entry_multiple(self):
        kundi A1: pita
        kundi A2: pita
        kundi B1: pita
        kundi B2: pita
        kundi A:
            eleza __mro_entries__(self, bases):
                rudisha (A1, A2)
        kundi B:
            eleza __mro_entries__(self, bases):
                rudisha (B1, B2)
        D = types.new_class('D', (A(), B()), {})
        self.assertEqual(D.__bases__, (A1, A2, B1, B2))

    eleza test_new_class_with_mro_entry_multiple_2(self):
        kundi A1: pita
        kundi A2: pita
        kundi A3: pita
        kundi B1: pita
        kundi B2: pita
        kundi A:
            eleza __mro_entries__(self, bases):
                rudisha (A1, A2, A3)
        kundi B:
            eleza __mro_entries__(self, bases):
                rudisha (B1, B2)
        kundi C: pita
        D = types.new_class('D', (A(), C, B()), {})
        self.assertEqual(D.__bases__, (A1, A2, A3, C, B1, B2))

    # Many of the following tests are derived kutoka test_descr.py
    eleza test_prepare_class(self):
        # Basic test of metakundi derivation
        expected_ns = {}
        kundi A(type):
            eleza __new__(*args, **kwargs):
                rudisha type.__new__(*args, **kwargs)

            eleza __prepare__(*args):
                rudisha expected_ns

        B = types.new_class("B", (object,))
        C = types.new_class("C", (object,), {"metaclass": A})

        # The most derived metakundi of D ni A rather than type.
        meta, ns, kwds = types.prepare_class("D", (B, C), {"metaclass": type})
        self.assertIs(meta, A)
        self.assertIs(ns, expected_ns)
        self.assertEqual(len(kwds), 0)

    eleza test_bad___prepare__(self):
        # __prepare__() must rudisha a mapping.
        kundi BadMeta(type):
            @classmethod
            eleza __prepare__(*args):
                rudisha Tupu
        ukijumuisha self.assertRaisesRegex(TypeError,
                                    r'^BadMeta\.__prepare__\(\) must '
                                    r'rudisha a mapping, sio TupuType$'):
            kundi Foo(metaclass=BadMeta):
                pita
        # Also test the case kwenye which the metakundi ni sio a type.
        kundi BadMeta:
            @classmethod
            eleza __prepare__(*args):
                rudisha Tupu
        ukijumuisha self.assertRaisesRegex(TypeError,
                                    r'^<metaclass>\.__prepare__\(\) must '
                                    r'rudisha a mapping, sio TupuType$'):
            kundi Bar(metaclass=BadMeta()):
                pita

    eleza test_resolve_bases(self):
        kundi A: pita
        kundi B: pita
        kundi C:
            eleza __mro_entries__(self, bases):
                ikiwa A kwenye bases:
                    rudisha ()
                rudisha (A,)
        c = C()
        self.assertEqual(types.resolve_bases(()), ())
        self.assertEqual(types.resolve_bases((c,)), (A,))
        self.assertEqual(types.resolve_bases((C,)), (C,))
        self.assertEqual(types.resolve_bases((A, C)), (A, C))
        self.assertEqual(types.resolve_bases((c, A)), (A,))
        self.assertEqual(types.resolve_bases((A, c)), (A,))
        x = (A,)
        y = (C,)
        z = (A, C)
        t = (A, C, B)
        kila bases kwenye [x, y, z, t]:
            self.assertIs(types.resolve_bases(bases), bases)

    eleza test_metaclass_derivation(self):
        # issue1294232: correct metakundi calculation
        new_calls = []  # to check the order of __new__ calls
        kundi AMeta(type):
            eleza __new__(mcls, name, bases, ns):
                new_calls.append('AMeta')
                rudisha super().__new__(mcls, name, bases, ns)
            @classmethod
            eleza __prepare__(mcls, name, bases):
                rudisha {}

        kundi BMeta(AMeta):
            eleza __new__(mcls, name, bases, ns):
                new_calls.append('BMeta')
                rudisha super().__new__(mcls, name, bases, ns)
            @classmethod
            eleza __prepare__(mcls, name, bases):
                ns = super().__prepare__(name, bases)
                ns['BMeta_was_here'] = Kweli
                rudisha ns

        A = types.new_class("A", (), {"metaclass": AMeta})
        self.assertEqual(new_calls, ['AMeta'])
        new_calls.clear()

        B = types.new_class("B", (), {"metaclass": BMeta})
        # BMeta.__new__ calls AMeta.__new__ ukijumuisha super:
        self.assertEqual(new_calls, ['BMeta', 'AMeta'])
        new_calls.clear()

        C = types.new_class("C", (A, B))
        # The most derived metakundi ni BMeta:
        self.assertEqual(new_calls, ['BMeta', 'AMeta'])
        new_calls.clear()
        # BMeta.__prepare__ should've been called:
        self.assertIn('BMeta_was_here', C.__dict__)

        # The order of the bases shouldn't matter:
        C2 = types.new_class("C2", (B, A))
        self.assertEqual(new_calls, ['BMeta', 'AMeta'])
        new_calls.clear()
        self.assertIn('BMeta_was_here', C2.__dict__)

        # Check correct metakundi calculation when a metakundi ni declared:
        D = types.new_class("D", (C,), {"metaclass": type})
        self.assertEqual(new_calls, ['BMeta', 'AMeta'])
        new_calls.clear()
        self.assertIn('BMeta_was_here', D.__dict__)

        E = types.new_class("E", (C,), {"metaclass": AMeta})
        self.assertEqual(new_calls, ['BMeta', 'AMeta'])
        new_calls.clear()
        self.assertIn('BMeta_was_here', E.__dict__)

    eleza test_metaclass_override_function(self):
        # Special case: the given metakundi isn't a class,
        # so there ni no metakundi calculation.
        kundi A(metaclass=self.Meta):
            pita

        marker = object()
        eleza func(*args, **kwargs):
            rudisha marker

        X = types.new_class("X", (), {"metaclass": func})
        Y = types.new_class("Y", (object,), {"metaclass": func})
        Z = types.new_class("Z", (A,), {"metaclass": func})
        self.assertIs(marker, X)
        self.assertIs(marker, Y)
        self.assertIs(marker, Z)

    eleza test_metaclass_override_callable(self):
        # The given metakundi ni a class,
        # but sio a descendant of type.
        new_calls = []  # to check the order of __new__ calls
        prepare_calls = []  # to track __prepare__ calls
        kundi ANotMeta:
            eleza __new__(mcls, *args, **kwargs):
                new_calls.append('ANotMeta')
                rudisha super().__new__(mcls)
            @classmethod
            eleza __prepare__(mcls, name, bases):
                prepare_calls.append('ANotMeta')
                rudisha {}

        kundi BNotMeta(ANotMeta):
            eleza __new__(mcls, *args, **kwargs):
                new_calls.append('BNotMeta')
                rudisha super().__new__(mcls)
            @classmethod
            eleza __prepare__(mcls, name, bases):
                prepare_calls.append('BNotMeta')
                rudisha super().__prepare__(name, bases)

        A = types.new_class("A", (), {"metaclass": ANotMeta})
        self.assertIs(ANotMeta, type(A))
        self.assertEqual(prepare_calls, ['ANotMeta'])
        prepare_calls.clear()
        self.assertEqual(new_calls, ['ANotMeta'])
        new_calls.clear()

        B = types.new_class("B", (), {"metaclass": BNotMeta})
        self.assertIs(BNotMeta, type(B))
        self.assertEqual(prepare_calls, ['BNotMeta', 'ANotMeta'])
        prepare_calls.clear()
        self.assertEqual(new_calls, ['BNotMeta', 'ANotMeta'])
        new_calls.clear()

        C = types.new_class("C", (A, B))
        self.assertIs(BNotMeta, type(C))
        self.assertEqual(prepare_calls, ['BNotMeta', 'ANotMeta'])
        prepare_calls.clear()
        self.assertEqual(new_calls, ['BNotMeta', 'ANotMeta'])
        new_calls.clear()

        C2 = types.new_class("C2", (B, A))
        self.assertIs(BNotMeta, type(C2))
        self.assertEqual(prepare_calls, ['BNotMeta', 'ANotMeta'])
        prepare_calls.clear()
        self.assertEqual(new_calls, ['BNotMeta', 'ANotMeta'])
        new_calls.clear()

        # This ni a TypeError, because of a metakundi conflict:
        # BNotMeta ni neither a subclass, nor a superkundi of type
        ukijumuisha self.assertRaises(TypeError):
            D = types.new_class("D", (C,), {"metaclass": type})

        E = types.new_class("E", (C,), {"metaclass": ANotMeta})
        self.assertIs(BNotMeta, type(E))
        self.assertEqual(prepare_calls, ['BNotMeta', 'ANotMeta'])
        prepare_calls.clear()
        self.assertEqual(new_calls, ['BNotMeta', 'ANotMeta'])
        new_calls.clear()

        F = types.new_class("F", (object(), C))
        self.assertIs(BNotMeta, type(F))
        self.assertEqual(prepare_calls, ['BNotMeta', 'ANotMeta'])
        prepare_calls.clear()
        self.assertEqual(new_calls, ['BNotMeta', 'ANotMeta'])
        new_calls.clear()

        F2 = types.new_class("F2", (C, object()))
        self.assertIs(BNotMeta, type(F2))
        self.assertEqual(prepare_calls, ['BNotMeta', 'ANotMeta'])
        prepare_calls.clear()
        self.assertEqual(new_calls, ['BNotMeta', 'ANotMeta'])
        new_calls.clear()

        # TypeError: BNotMeta ni neither a
        # subclass, nor a superkundi of int
        ukijumuisha self.assertRaises(TypeError):
            X = types.new_class("X", (C, int()))
        ukijumuisha self.assertRaises(TypeError):
            X = types.new_class("X", (int(), C))

    eleza test_one_argument_type(self):
        expected_message = 'type.__new__() takes exactly 3 arguments (1 given)'

        # Only type itself can use the one-argument form (#27157)
        self.assertIs(type(5), int)

        kundi M(type):
            pita
        ukijumuisha self.assertRaises(TypeError) kama cm:
            M(5)
        self.assertEqual(str(cm.exception), expected_message)

        kundi N(type, metaclass=M):
            pita
        ukijumuisha self.assertRaises(TypeError) kama cm:
            N(5)
        self.assertEqual(str(cm.exception), expected_message)


kundi SimpleNamespaceTests(unittest.TestCase):

    eleza test_constructor(self):
        ns1 = types.SimpleNamespace()
        ns2 = types.SimpleNamespace(x=1, y=2)
        ns3 = types.SimpleNamespace(**dict(x=1, y=2))

        ukijumuisha self.assertRaises(TypeError):
            types.SimpleNamespace(1, 2, 3)
        ukijumuisha self.assertRaises(TypeError):
            types.SimpleNamespace(**{1: 2})

        self.assertEqual(len(ns1.__dict__), 0)
        self.assertEqual(vars(ns1), {})
        self.assertEqual(len(ns2.__dict__), 2)
        self.assertEqual(vars(ns2), {'y': 2, 'x': 1})
        self.assertEqual(len(ns3.__dict__), 2)
        self.assertEqual(vars(ns3), {'y': 2, 'x': 1})

    eleza test_unbound(self):
        ns1 = vars(types.SimpleNamespace())
        ns2 = vars(types.SimpleNamespace(x=1, y=2))

        self.assertEqual(ns1, {})
        self.assertEqual(ns2, {'y': 2, 'x': 1})

    eleza test_underlying_dict(self):
        ns1 = types.SimpleNamespace()
        ns2 = types.SimpleNamespace(x=1, y=2)
        ns3 = types.SimpleNamespace(a=Kweli, b=Uongo)
        mapping = ns3.__dict__
        toa ns3

        self.assertEqual(ns1.__dict__, {})
        self.assertEqual(ns2.__dict__, {'y': 2, 'x': 1})
        self.assertEqual(mapping, dict(a=Kweli, b=Uongo))

    eleza test_attrget(self):
        ns = types.SimpleNamespace(x=1, y=2, w=3)

        self.assertEqual(ns.x, 1)
        self.assertEqual(ns.y, 2)
        self.assertEqual(ns.w, 3)
        ukijumuisha self.assertRaises(AttributeError):
            ns.z

    eleza test_attrset(self):
        ns1 = types.SimpleNamespace()
        ns2 = types.SimpleNamespace(x=1, y=2, w=3)
        ns1.a = 'spam'
        ns1.b = 'ham'
        ns2.z = 4
        ns2.theta = Tupu

        self.assertEqual(ns1.__dict__, dict(a='spam', b='ham'))
        self.assertEqual(ns2.__dict__, dict(x=1, y=2, w=3, z=4, theta=Tupu))

    eleza test_attrdel(self):
        ns1 = types.SimpleNamespace()
        ns2 = types.SimpleNamespace(x=1, y=2, w=3)

        ukijumuisha self.assertRaises(AttributeError):
            toa ns1.spam
        ukijumuisha self.assertRaises(AttributeError):
            toa ns2.spam

        toa ns2.y
        self.assertEqual(vars(ns2), dict(w=3, x=1))
        ns2.y = 'spam'
        self.assertEqual(vars(ns2), dict(w=3, x=1, y='spam'))
        toa ns2.y
        self.assertEqual(vars(ns2), dict(w=3, x=1))

        ns1.spam = 5
        self.assertEqual(vars(ns1), dict(spam=5))
        toa ns1.spam
        self.assertEqual(vars(ns1), {})

    eleza test_repr(self):
        ns1 = types.SimpleNamespace(x=1, y=2, w=3)
        ns2 = types.SimpleNamespace()
        ns2.x = "spam"
        ns2._y = 5
        name = "namespace"

        self.assertEqual(repr(ns1), "{name}(w=3, x=1, y=2)".format(name=name))
        self.assertEqual(repr(ns2), "{name}(_y=5, x='spam')".format(name=name))

    eleza test_equal(self):
        ns1 = types.SimpleNamespace(x=1)
        ns2 = types.SimpleNamespace()
        ns2.x = 1

        self.assertEqual(types.SimpleNamespace(), types.SimpleNamespace())
        self.assertEqual(ns1, ns2)
        self.assertNotEqual(ns2, types.SimpleNamespace())

    eleza test_nested(self):
        ns1 = types.SimpleNamespace(a=1, b=2)
        ns2 = types.SimpleNamespace()
        ns3 = types.SimpleNamespace(x=ns1)
        ns2.spam = ns1
        ns2.ham = '?'
        ns2.spam = ns3

        self.assertEqual(vars(ns1), dict(a=1, b=2))
        self.assertEqual(vars(ns2), dict(spam=ns3, ham='?'))
        self.assertEqual(ns2.spam, ns3)
        self.assertEqual(vars(ns3), dict(x=ns1))
        self.assertEqual(ns3.x.a, 1)

    eleza test_recursive(self):
        ns1 = types.SimpleNamespace(c='cookie')
        ns2 = types.SimpleNamespace()
        ns3 = types.SimpleNamespace(x=1)
        ns1.spam = ns1
        ns2.spam = ns3
        ns3.spam = ns2

        self.assertEqual(ns1.spam, ns1)
        self.assertEqual(ns1.spam.spam, ns1)
        self.assertEqual(ns1.spam.spam, ns1.spam)
        self.assertEqual(ns2.spam, ns3)
        self.assertEqual(ns3.spam, ns2)
        self.assertEqual(ns2.spam.spam, ns2)

    eleza test_recursive_repr(self):
        ns1 = types.SimpleNamespace(c='cookie')
        ns2 = types.SimpleNamespace()
        ns3 = types.SimpleNamespace(x=1)
        ns1.spam = ns1
        ns2.spam = ns3
        ns3.spam = ns2
        name = "namespace"
        repr1 = "{name}(c='cookie', spam={name}(...))".format(name=name)
        repr2 = "{name}(spam={name}(spam={name}(...), x=1))".format(name=name)

        self.assertEqual(repr(ns1), repr1)
        self.assertEqual(repr(ns2), repr2)

    eleza test_as_dict(self):
        ns = types.SimpleNamespace(spam='spamspamspam')

        ukijumuisha self.assertRaises(TypeError):
            len(ns)
        ukijumuisha self.assertRaises(TypeError):
            iter(ns)
        ukijumuisha self.assertRaises(TypeError):
            'spam' kwenye ns
        ukijumuisha self.assertRaises(TypeError):
            ns['spam']

    eleza test_subclass(self):
        kundi Spam(types.SimpleNamespace):
            pita

        spam = Spam(ham=8, eggs=9)

        self.assertIs(type(spam), Spam)
        self.assertEqual(vars(spam), {'ham': 8, 'eggs': 9})

    eleza test_pickle(self):
        ns = types.SimpleNamespace(komafast="spam", lunch="spam")

        kila protocol kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            pname = "protocol {}".format(protocol)
            jaribu:
                ns_pickled = pickle.dumps(ns, protocol)
            tatizo TypeError kama e:
                ashiria TypeError(pname) kutoka e
            ns_roundtrip = pickle.loads(ns_pickled)

            self.assertEqual(ns, ns_roundtrip, pname)

    eleza test_fake_namespace_compare(self):
        # Issue #24257: Incorrect use of PyObject_IsInstance() caused
        # SystemError.
        kundi FakeSimpleNamespace(str):
            __class__ = types.SimpleNamespace
        self.assertUongo(types.SimpleNamespace() == FakeSimpleNamespace())
        self.assertKweli(types.SimpleNamespace() != FakeSimpleNamespace())
        ukijumuisha self.assertRaises(TypeError):
            types.SimpleNamespace() < FakeSimpleNamespace()
        ukijumuisha self.assertRaises(TypeError):
            types.SimpleNamespace() <= FakeSimpleNamespace()
        ukijumuisha self.assertRaises(TypeError):
            types.SimpleNamespace() > FakeSimpleNamespace()
        ukijumuisha self.assertRaises(TypeError):
            types.SimpleNamespace() >= FakeSimpleNamespace()


kundi CoroutineTests(unittest.TestCase):
    eleza test_wrong_args(self):
        samples = [Tupu, 1, object()]
        kila sample kwenye samples:
            ukijumuisha self.assertRaisesRegex(TypeError,
                                        'types.coroutine.*expects a callable'):
                types.coroutine(sample)

    eleza test_non_gen_values(self):
        @types.coroutine
        eleza foo():
            rudisha 'spam'
        self.assertEqual(foo(), 'spam')

        kundi Awaitable:
            eleza __await__(self):
                rudisha ()
        aw = Awaitable()
        @types.coroutine
        eleza foo():
            rudisha aw
        self.assertIs(aw, foo())

        # decorate foo second time
        foo = types.coroutine(foo)
        self.assertIs(aw, foo())

    eleza test_async_def(self):
        # Test that types.coroutine pitaes 'async def' coroutines
        # without modification

        async eleza foo(): pita
        foo_code = foo.__code__
        foo_flags = foo.__code__.co_flags
        decorated_foo = types.coroutine(foo)
        self.assertIs(foo, decorated_foo)
        self.assertEqual(foo.__code__.co_flags, foo_flags)
        self.assertIs(decorated_foo.__code__, foo_code)

        foo_coro = foo()
        eleza bar(): rudisha foo_coro
        kila _ kwenye range(2):
            bar = types.coroutine(bar)
            coro = bar()
            self.assertIs(foo_coro, coro)
            self.assertEqual(coro.cr_code.co_flags, foo_flags)
            coro.close()

    eleza test_duck_coro(self):
        kundi CoroLike:
            eleza send(self): pita
            eleza throw(self): pita
            eleza close(self): pita
            eleza __await__(self): rudisha self

        coro = CoroLike()
        @types.coroutine
        eleza foo():
            rudisha coro
        self.assertIs(foo(), coro)
        self.assertIs(foo().__await__(), coro)

    eleza test_duck_corogen(self):
        kundi CoroGenLike:
            eleza send(self): pita
            eleza throw(self): pita
            eleza close(self): pita
            eleza __await__(self): rudisha self
            eleza __iter__(self): rudisha self
            eleza __next__(self): pita

        coro = CoroGenLike()
        @types.coroutine
        eleza foo():
            rudisha coro
        self.assertIs(foo(), coro)
        self.assertIs(foo().__await__(), coro)

    eleza test_duck_gen(self):
        kundi GenLike:
            eleza send(self): pita
            eleza throw(self): pita
            eleza close(self): pita
            eleza __iter__(self): pita
            eleza __next__(self): pita

        # Setup generator mock object
        gen = unittest.mock.MagicMock(GenLike)
        gen.__iter__ = lambda gen: gen
        gen.__name__ = 'gen'
        gen.__qualname__ = 'test.gen'
        self.assertIsInstance(gen, collections.abc.Generator)
        self.assertIs(gen, iter(gen))

        @types.coroutine
        eleza foo(): rudisha gen

        wrapper = foo()
        self.assertIsInstance(wrapper, types._GeneratorWrapper)
        self.assertIs(wrapper.__await__(), wrapper)
        # Wrapper proxies duck generators completely:
        self.assertIs(iter(wrapper), wrapper)

        self.assertIsInstance(wrapper, collections.abc.Coroutine)
        self.assertIsInstance(wrapper, collections.abc.Awaitable)

        self.assertIs(wrapper.__qualname__, gen.__qualname__)
        self.assertIs(wrapper.__name__, gen.__name__)

        # Test AttributeErrors
        kila name kwenye {'gi_running', 'gi_frame', 'gi_code', 'gi_tumafrom',
                     'cr_running', 'cr_frame', 'cr_code', 'cr_await'}:
            ukijumuisha self.assertRaises(AttributeError):
                getattr(wrapper, name)

        # Test attributes pita-through
        gen.gi_running = object()
        gen.gi_frame = object()
        gen.gi_code = object()
        gen.gi_tumakutoka = object()
        self.assertIs(wrapper.gi_running, gen.gi_running)
        self.assertIs(wrapper.gi_frame, gen.gi_frame)
        self.assertIs(wrapper.gi_code, gen.gi_code)
        self.assertIs(wrapper.gi_tumafrom, gen.gi_tumafrom)
        self.assertIs(wrapper.cr_running, gen.gi_running)
        self.assertIs(wrapper.cr_frame, gen.gi_frame)
        self.assertIs(wrapper.cr_code, gen.gi_code)
        self.assertIs(wrapper.cr_await, gen.gi_tumafrom)

        wrapper.close()
        gen.close.assert_called_once_with()

        wrapper.send(1)
        gen.send.assert_called_once_with(1)
        gen.reset_mock()

        next(wrapper)
        gen.__next__.assert_called_once_with()
        gen.reset_mock()

        wrapper.throw(1, 2, 3)
        gen.throw.assert_called_once_with(1, 2, 3)
        gen.reset_mock()

        wrapper.throw(1, 2)
        gen.throw.assert_called_once_with(1, 2)
        gen.reset_mock()

        wrapper.throw(1)
        gen.throw.assert_called_once_with(1)
        gen.reset_mock()

        # Test exceptions propagation
        error = Exception()
        gen.throw.side_effect = error
        jaribu:
            wrapper.throw(1)
        tatizo Exception kama ex:
            self.assertIs(ex, error)
        isipokua:
            self.fail('wrapper did sio propagate an exception')

        # Test invalid args
        gen.reset_mock()
        ukijumuisha self.assertRaises(TypeError):
            wrapper.throw()
        self.assertUongo(gen.throw.called)
        ukijumuisha self.assertRaises(TypeError):
            wrapper.close(1)
        self.assertUongo(gen.close.called)
        ukijumuisha self.assertRaises(TypeError):
            wrapper.send()
        self.assertUongo(gen.send.called)

        # Test that we do sio double wrap
        @types.coroutine
        eleza bar(): rudisha wrapper
        self.assertIs(wrapper, bar())

        # Test weakrefs support
        ref = weakref.ref(wrapper)
        self.assertIs(ref(), wrapper)

    eleza test_duck_functional_gen(self):
        kundi Generator:
            """Emulates the following generator (very clumsy):

              eleza gen(fut):
                  result = tuma fut
                  rudisha result * 2
            """
            eleza __init__(self, fut):
                self._i = 0
                self._fut = fut
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                rudisha self.send(Tupu)
            eleza send(self, v):
                jaribu:
                    ikiwa self._i == 0:
                        assert v ni Tupu
                        rudisha self._fut
                    ikiwa self._i == 1:
                        ashiria StopIteration(v * 2)
                    ikiwa self._i > 1:
                        ashiria StopIteration
                mwishowe:
                    self._i += 1
            eleza throw(self, tp, *exc):
                self._i = 100
                ikiwa tp ni sio GeneratorExit:
                    ashiria tp
            eleza close(self):
                self.throw(GeneratorExit)

        @types.coroutine
        eleza foo(): rudisha Generator('spam')

        wrapper = foo()
        self.assertIsInstance(wrapper, types._GeneratorWrapper)

        async eleza corofunc():
            rudisha await foo() + 100
        coro = corofunc()

        self.assertEqual(coro.send(Tupu), 'spam')
        jaribu:
            coro.send(20)
        tatizo StopIteration kama ex:
            self.assertEqual(ex.args[0], 140)
        isipokua:
            self.fail('StopIteration was expected')

    eleza test_gen(self):
        eleza gen_func():
            tuma 1
            rudisha (tuma 2)
        gen = gen_func()
        @types.coroutine
        eleza foo(): rudisha gen
        wrapper = foo()
        self.assertIsInstance(wrapper, types._GeneratorWrapper)
        self.assertIs(wrapper.__await__(), gen)

        kila name kwenye ('__name__', '__qualname__', 'gi_code',
                     'gi_running', 'gi_frame'):
            self.assertIs(getattr(foo(), name),
                          getattr(gen, name))
        self.assertIs(foo().cr_code, gen.gi_code)

        self.assertEqual(next(wrapper), 1)
        self.assertEqual(wrapper.send(Tupu), 2)
        ukijumuisha self.assertRaisesRegex(StopIteration, 'spam'):
            wrapper.send('spam')

        gen = gen_func()
        wrapper = foo()
        wrapper.send(Tupu)
        ukijumuisha self.assertRaisesRegex(Exception, 'ham'):
            wrapper.throw(Exception, Exception('ham'))

        # decorate foo second time
        foo = types.coroutine(foo)
        self.assertIs(foo().__await__(), gen)

    eleza test_returning_itercoro(self):
        @types.coroutine
        eleza gen():
            tuma

        gencoro = gen()

        @types.coroutine
        eleza foo():
            rudisha gencoro

        self.assertIs(foo(), gencoro)

        # decorate foo second time
        foo = types.coroutine(foo)
        self.assertIs(foo(), gencoro)

    eleza test_genfunc(self):
        eleza gen(): tuma
        self.assertIs(types.coroutine(gen), gen)
        self.assertIs(types.coroutine(types.coroutine(gen)), gen)

        self.assertKweli(gen.__code__.co_flags & inspect.CO_ITERABLE_COROUTINE)
        self.assertUongo(gen.__code__.co_flags & inspect.CO_COROUTINE)

        g = gen()
        self.assertKweli(g.gi_code.co_flags & inspect.CO_ITERABLE_COROUTINE)
        self.assertUongo(g.gi_code.co_flags & inspect.CO_COROUTINE)

        self.assertIs(types.coroutine(gen), gen)

    eleza test_wrapper_object(self):
        eleza gen():
            tuma
        @types.coroutine
        eleza coro():
            rudisha gen()

        wrapper = coro()
        self.assertIn('GeneratorWrapper', repr(wrapper))
        self.assertEqual(repr(wrapper), str(wrapper))
        self.assertKweli(set(dir(wrapper)).issuperset({
            '__await__', '__iter__', '__next__', 'cr_code', 'cr_running',
            'cr_frame', 'gi_code', 'gi_frame', 'gi_running', 'send',
            'close', 'throw'}))


ikiwa __name__ == '__main__':
    unittest.main()
