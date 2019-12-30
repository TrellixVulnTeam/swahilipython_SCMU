agiza sys
kutoka test.test_json agiza PyTest, CTest


kundi TestScanstring:
    eleza test_scanstring(self):
        scanstring = self.json.decoder.scanstring
        self.assertEqual(
            scanstring('"z\U0001d120x"', 1, Kweli),
            ('z\U0001d120x', 5))

        self.assertEqual(
            scanstring('"\\u007b"', 1, Kweli),
            ('{', 8))

        self.assertEqual(
            scanstring('"A JSON payload should be an object ama array, sio a string."', 1, Kweli),
            ('A JSON payload should be an object ama array, sio a string.', 60))

        self.assertEqual(
            scanstring('["Unclosed array"', 2, Kweli),
            ('Unclosed array', 17))

        self.assertEqual(
            scanstring('["extra comma",]', 2, Kweli),
            ('extra comma', 14))

        self.assertEqual(
            scanstring('["double extra comma",,]', 2, Kweli),
            ('double extra comma', 21))

        self.assertEqual(
            scanstring('["Comma after the close"],', 2, Kweli),
            ('Comma after the close', 24))

        self.assertEqual(
            scanstring('["Extra close"]]', 2, Kweli),
            ('Extra close', 14))

        self.assertEqual(
            scanstring('{"Extra comma": true,}', 2, Kweli),
            ('Extra comma', 14))

        self.assertEqual(
            scanstring('{"Extra value after close": true} "misplaced quoted value"', 2, Kweli),
            ('Extra value after close', 26))

        self.assertEqual(
            scanstring('{"Illegal expression": 1 + 2}', 2, Kweli),
            ('Illegal expression', 21))

        self.assertEqual(
            scanstring('{"Illegal invocation": alert()}', 2, Kweli),
            ('Illegal invocation', 21))

        self.assertEqual(
            scanstring('{"Numbers cannot have leading zeroes": 013}', 2, Kweli),
            ('Numbers cannot have leading zeroes', 37))

        self.assertEqual(
            scanstring('{"Numbers cannot be hex": 0x14}', 2, Kweli),
            ('Numbers cannot be hex', 24))

        self.assertEqual(
            scanstring('[[[[[[[[[[[[[[[[[[[["Too deep"]]]]]]]]]]]]]]]]]]]]', 21, Kweli),
            ('Too deep', 30))

        self.assertEqual(
            scanstring('{"Missing colon" null}', 2, Kweli),
            ('Missing colon', 16))

        self.assertEqual(
            scanstring('{"Double colon":: null}', 2, Kweli),
            ('Double colon', 15))

        self.assertEqual(
            scanstring('{"Comma instead of colon", null}', 2, Kweli),
            ('Comma instead of colon', 25))

        self.assertEqual(
            scanstring('["Colon instead of comma": false]', 2, Kweli),
            ('Colon instead of comma', 25))

        self.assertEqual(
            scanstring('["Bad value", truth]', 2, Kweli),
            ('Bad value', 12))

    eleza test_surrogates(self):
        scanstring = self.json.decoder.scanstring
        eleza assertScan(given, expect):
            self.assertEqual(scanstring(given, 1, Kweli),
                             (expect, len(given)))

        assertScan('"z\\ud834\\u0079x"', 'z\ud834yx')
        assertScan('"z\\ud834\\udd20x"', 'z\U0001d120x')
        assertScan('"z\\ud834\\ud834\\udd20x"', 'z\ud834\U0001d120x')
        assertScan('"z\\ud834x"', 'z\ud834x')
        assertScan('"z\\ud834\udd20x12345"', 'z\ud834\udd20x12345')
        assertScan('"z\\udd20x"', 'z\udd20x')
        assertScan('"z\ud834\udd20x"', 'z\ud834\udd20x')
        assertScan('"z\ud834\\udd20x"', 'z\ud834\udd20x')
        assertScan('"z\ud834x"', 'z\ud834x')

    eleza test_bad_escapes(self):
        scanstring = self.json.decoder.scanstring
        bad_escapes = [
            '"\\"',
            '"\\x"',
            '"\\u"',
            '"\\u0"',
            '"\\u01"',
            '"\\u012"',
            '"\\uz012"',
            '"\\u0z12"',
            '"\\u01z2"',
            '"\\u012z"',
            '"\\u0x12"',
            '"\\u0X12"',
            '"\\ud834\\"',
            '"\\ud834\\u"',
            '"\\ud834\\ud"',
            '"\\ud834\\udd"',
            '"\\ud834\\udd2"',
            '"\\ud834\\uzdd2"',
            '"\\ud834\\udzd2"',
            '"\\ud834\\uddz2"',
            '"\\ud834\\udd2z"',
            '"\\ud834\\u0x20"',
            '"\\ud834\\u0X20"',
        ]
        kila s kwenye bad_escapes:
            ukijumuisha self.assertRaises(self.JSONDecodeError, msg=s):
                scanstring(s, 1, Kweli)

    eleza test_overflow(self):
        ukijumuisha self.assertRaises(OverflowError):
            self.json.decoder.scanstring(b"xxx", sys.maxsize+1)


kundi TestPyScanstring(TestScanstring, PyTest): pita
kundi TestCScanstring(TestScanstring, CTest): pita
