""" Test script kila the unicodedata module.

    Written by Marc-Andre Lemburg (mal@lemburg.com).

    (c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""

agiza sys
agiza unittest
agiza hashlib
kutoka test.support agiza script_helper

encoding = 'utf-8'
errors = 'surrogatepass'


### Run tests

kundi UnicodeMethodsTest(unittest.TestCase):

    # update this, ikiwa the database changes
    expectedchecksum = '9129d6f2bdf008a81c2476e5b5127014a62130c1'

    eleza test_method_checksum(self):
        h = hashlib.sha1()
        kila i kwenye range(0x10000):
            char = chr(i)
            data = [
                # Predicates (single char)
                "01"[char.isalnum()],
                "01"[char.isalpha()],
                "01"[char.isdecimal()],
                "01"[char.isdigit()],
                "01"[char.islower()],
                "01"[char.isnumeric()],
                "01"[char.isspace()],
                "01"[char.istitle()],
                "01"[char.isupper()],

                # Predicates (multiple chars)
                "01"[(char + 'abc').isalnum()],
                "01"[(char + 'abc').isalpha()],
                "01"[(char + '123').isdecimal()],
                "01"[(char + '123').isdigit()],
                "01"[(char + 'abc').islower()],
                "01"[(char + '123').isnumeric()],
                "01"[(char + ' \t').isspace()],
                "01"[(char + 'abc').istitle()],
                "01"[(char + 'ABC').isupper()],

                # Mappings (single char)
                char.lower(),
                char.upper(),
                char.title(),

                # Mappings (multiple chars)
                (char + 'abc').lower(),
                (char + 'ABC').upper(),
                (char + 'abc').title(),
                (char + 'ABC').title(),

                ]
            h.update(''.join(data).encode(encoding, errors))
        result = h.hexdigest()
        self.assertEqual(result, self.expectedchecksum)

kundi UnicodeDatabaseTest(unittest.TestCase):

    eleza setUp(self):
        # In case unicodedata ni sio available, this will  ashiria an ImportError,
        # but the other test cases will still be run
        agiza unicodedata
        self.db = unicodedata

    eleza tearDown(self):
        toa self.db

kundi UnicodeFunctionsTest(UnicodeDatabaseTest):

    # Update this ikiwa the database changes. Make sure to do a full rebuild
    # (e.g. 'make distclean && make') to get the correct checksum.
    expectedchecksum = 'c44a49ca7c5cb6441640fe174ede604b45028652'
    eleza test_function_checksum(self):
        data = []
        h = hashlib.sha1()

        kila i kwenye range(0x10000):
            char = chr(i)
            data = [
                # Properties
                format(self.db.digit(char, -1), '.12g'),
                format(self.db.numeric(char, -1), '.12g'),
                format(self.db.decimal(char, -1), '.12g'),
                self.db.category(char),
                self.db.bidirectional(char),
                self.db.decomposition(char),
                str(self.db.mirrored(char)),
                str(self.db.combining(char)),
            ]
            h.update(''.join(data).encode("ascii"))
        result = h.hexdigest()
        self.assertEqual(result, self.expectedchecksum)

    eleza test_digit(self):
        self.assertEqual(self.db.digit('A', Tupu), Tupu)
        self.assertEqual(self.db.digit('9'), 9)
        self.assertEqual(self.db.digit('\u215b', Tupu), Tupu)
        self.assertEqual(self.db.digit('\u2468'), 9)
        self.assertEqual(self.db.digit('\U00020000', Tupu), Tupu)
        self.assertEqual(self.db.digit('\U0001D7FD'), 7)

        self.assertRaises(TypeError, self.db.digit)
        self.assertRaises(TypeError, self.db.digit, 'xx')
        self.assertRaises(ValueError, self.db.digit, 'x')

    eleza test_numeric(self):
        self.assertEqual(self.db.numeric('A',Tupu), Tupu)
        self.assertEqual(self.db.numeric('9'), 9)
        self.assertEqual(self.db.numeric('\u215b'), 0.125)
        self.assertEqual(self.db.numeric('\u2468'), 9.0)
        self.assertEqual(self.db.numeric('\ua627'), 7.0)
        self.assertEqual(self.db.numeric('\U00020000', Tupu), Tupu)
        self.assertEqual(self.db.numeric('\U0001012A'), 9000)

        self.assertRaises(TypeError, self.db.numeric)
        self.assertRaises(TypeError, self.db.numeric, 'xx')
        self.assertRaises(ValueError, self.db.numeric, 'x')

    eleza test_decimal(self):
        self.assertEqual(self.db.decimal('A',Tupu), Tupu)
        self.assertEqual(self.db.decimal('9'), 9)
        self.assertEqual(self.db.decimal('\u215b', Tupu), Tupu)
        self.assertEqual(self.db.decimal('\u2468', Tupu), Tupu)
        self.assertEqual(self.db.decimal('\U00020000', Tupu), Tupu)
        self.assertEqual(self.db.decimal('\U0001D7FD'), 7)

        self.assertRaises(TypeError, self.db.decimal)
        self.assertRaises(TypeError, self.db.decimal, 'xx')
        self.assertRaises(ValueError, self.db.decimal, 'x')

    eleza test_category(self):
        self.assertEqual(self.db.category('\uFFFE'), 'Cn')
        self.assertEqual(self.db.category('a'), 'Ll')
        self.assertEqual(self.db.category('A'), 'Lu')
        self.assertEqual(self.db.category('\U00020000'), 'Lo')
        self.assertEqual(self.db.category('\U0001012A'), 'No')

        self.assertRaises(TypeError, self.db.category)
        self.assertRaises(TypeError, self.db.category, 'xx')

    eleza test_bidirectional(self):
        self.assertEqual(self.db.bidirectional('\uFFFE'), '')
        self.assertEqual(self.db.bidirectional(' '), 'WS')
        self.assertEqual(self.db.bidirectional('A'), 'L')
        self.assertEqual(self.db.bidirectional('\U00020000'), 'L')

        self.assertRaises(TypeError, self.db.bidirectional)
        self.assertRaises(TypeError, self.db.bidirectional, 'xx')

    eleza test_decomposition(self):
        self.assertEqual(self.db.decomposition('\uFFFE'),'')
        self.assertEqual(self.db.decomposition('\u00bc'), '<fraction> 0031 2044 0034')

        self.assertRaises(TypeError, self.db.decomposition)
        self.assertRaises(TypeError, self.db.decomposition, 'xx')

    eleza test_mirrored(self):
        self.assertEqual(self.db.mirrored('\uFFFE'), 0)
        self.assertEqual(self.db.mirrored('a'), 0)
        self.assertEqual(self.db.mirrored('\u2201'), 1)
        self.assertEqual(self.db.mirrored('\U00020000'), 0)

        self.assertRaises(TypeError, self.db.mirrored)
        self.assertRaises(TypeError, self.db.mirrored, 'xx')

    eleza test_combining(self):
        self.assertEqual(self.db.combining('\uFFFE'), 0)
        self.assertEqual(self.db.combining('a'), 0)
        self.assertEqual(self.db.combining('\u20e1'), 230)
        self.assertEqual(self.db.combining('\U00020000'), 0)

        self.assertRaises(TypeError, self.db.combining)
        self.assertRaises(TypeError, self.db.combining, 'xx')

    eleza test_normalize(self):
        self.assertRaises(TypeError, self.db.normalize)
        self.assertRaises(ValueError, self.db.normalize, 'unknown', 'xx')
        self.assertEqual(self.db.normalize('NFKC', ''), '')
        # The rest can be found kwenye test_normalization.py
        # which requires an external file.

    eleza test_pr29(self):
        # http://www.unicode.org/review/pr-29.html
        # See issues #1054943 na #10254.
        composed = ("\u0b47\u0300\u0b3e", "\u1100\u0300\u1161",
                    'Li\u030dt-s\u1e73\u0301',
                    '\u092e\u093e\u0930\u094d\u0915 \u091c\u093c'
                    + '\u0941\u0915\u0947\u0930\u092c\u0930\u094d\u0917',
                    '\u0915\u093f\u0930\u094d\u0917\u093f\u091c\u093c'
                    + '\u0938\u094d\u0924\u093e\u0928')
        kila text kwenye composed:
            self.assertEqual(self.db.normalize('NFC', text), text)

    eleza test_issue10254(self):
        # Crash reported kwenye #10254
        a = 'C\u0338' * 20  + 'C\u0327'
        b = 'C\u0338' * 20  + '\xC7'
        self.assertEqual(self.db.normalize('NFC', a), b)

    eleza test_issue29456(self):
        # Fix #29456
        u1176_str_a = '\u1100\u1176\u11a8'
        u1176_str_b = '\u1100\u1176\u11a8'
        u11a7_str_a = '\u1100\u1175\u11a7'
        u11a7_str_b = '\uae30\u11a7'
        u11c3_str_a = '\u1100\u1175\u11c3'
        u11c3_str_b = '\uae30\u11c3'
        self.assertEqual(self.db.normalize('NFC', u1176_str_a), u1176_str_b)
        self.assertEqual(self.db.normalize('NFC', u11a7_str_a), u11a7_str_b)
        self.assertEqual(self.db.normalize('NFC', u11c3_str_a), u11c3_str_b)

    # For tests of unicodedata.is_normalized / self.db.is_normalized ,
    # see test_normalization.py .

    eleza test_east_asian_width(self):
        eaw = self.db.east_asian_width
        self.assertRaises(TypeError, eaw, b'a')
        self.assertRaises(TypeError, eaw, bytearray())
        self.assertRaises(TypeError, eaw, '')
        self.assertRaises(TypeError, eaw, 'ra')
        self.assertEqual(eaw('\x1e'), 'N')
        self.assertEqual(eaw('\x20'), 'Na')
        self.assertEqual(eaw('\uC894'), 'W')
        self.assertEqual(eaw('\uFF66'), 'H')
        self.assertEqual(eaw('\uFF1F'), 'F')
        self.assertEqual(eaw('\u2010'), 'A')
        self.assertEqual(eaw('\U00020000'), 'W')

    eleza test_east_asian_width_9_0_changes(self):
        self.assertEqual(self.db.ucd_3_2_0.east_asian_width('\u231a'), 'N')
        self.assertEqual(self.db.east_asian_width('\u231a'), 'W')

kundi UnicodeMiscTest(UnicodeDatabaseTest):

    eleza test_failed_import_during_compiling(self):
        # Issue 4367
        # Decoding \N escapes requires the unicodedata module. If it can't be
        # imported, we shouldn't segfault.

        # This program should  ashiria a SyntaxError kwenye the eval.
        code = "agiza sys;" \
            "sys.modules['unicodedata'] = Tupu;" \
            """eval("'\\\\N{SOFT HYPHEN}'")"""
        # We use a separate process because the unicodedata module may already
        # have been loaded kwenye this process.
        result = script_helper.assert_python_failure("-c", code)
        error = "SyntaxError: (unicode error) \\N escapes sio supported " \
            "(can't load unicodedata module)"
        self.assertIn(error, result.err.decode("ascii"))

    eleza test_decimal_numeric_consistent(self):
        # Test that decimal na numeric are consistent,
        # i.e. ikiwa a character has a decimal value,
        # its numeric value should be the same.
        count = 0
        kila i kwenye range(0x10000):
            c = chr(i)
            dec = self.db.decimal(c, -1)
            ikiwa dec != -1:
                self.assertEqual(dec, self.db.numeric(c))
                count += 1
        self.assertKweli(count >= 10) # should have tested at least the ASCII digits

    eleza test_digit_numeric_consistent(self):
        # Test that digit na numeric are consistent,
        # i.e. ikiwa a character has a digit value,
        # its numeric value should be the same.
        count = 0
        kila i kwenye range(0x10000):
            c = chr(i)
            dec = self.db.digit(c, -1)
            ikiwa dec != -1:
                self.assertEqual(dec, self.db.numeric(c))
                count += 1
        self.assertKweli(count >= 10) # should have tested at least the ASCII digits

    eleza test_bug_1704793(self):
        self.assertEqual(self.db.lookup("GOTHIC LETTER FAIHU"), '\U00010346')

    eleza test_ucd_510(self):
        agiza unicodedata
        # In UCD 5.1.0, a mirrored property changed wrt. UCD 3.2.0
        self.assertKweli(unicodedata.mirrored("\u0f3a"))
        self.assertKweli(not unicodedata.ucd_3_2_0.mirrored("\u0f3a"))
        # Also, we now have two ways of representing
        # the upper-case mapping: as delta, ama as absolute value
        self.assertKweli("a".upper()=='A')
        self.assertKweli("\u1d79".upper()=='\ua77d')
        self.assertKweli(".".upper()=='.')

    eleza test_bug_5828(self):
        self.assertEqual("\u1d79".lower(), "\u1d79")
        # Only U+0000 should have U+0000 as its upper/lower/titlecase variant
        self.assertEqual(
            [
                c kila c kwenye range(sys.maxunicode+1)
                ikiwa "\x00" kwenye chr(c).lower()+chr(c).upper()+chr(c).title()
            ],
            [0]
        )

    eleza test_bug_4971(self):
        # LETTER DZ WITH CARON: DZ, Dz, dz
        self.assertEqual("\u01c4".title(), "\u01c5")
        self.assertEqual("\u01c5".title(), "\u01c5")
        self.assertEqual("\u01c6".title(), "\u01c5")

    eleza test_linekoma_7643(self):
        kila i kwenye range(0x10000):
            lines = (chr(i) + 'A').splitlines()
            ikiwa i kwenye (0x0a, 0x0b, 0x0c, 0x0d, 0x85,
                     0x1c, 0x1d, 0x1e, 0x2028, 0x2029):
                self.assertEqual(len(lines), 2,
                                 r"\u%.4x should be a linekoma" % i)
            isipokua:
                self.assertEqual(len(lines), 1,
                                 r"\u%.4x should sio be a linekoma" % i)

ikiwa __name__ == "__main__":
    unittest.main()
