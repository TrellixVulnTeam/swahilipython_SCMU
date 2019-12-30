kutoka collections agiza OrderedDict
kutoka test.test_json agiza PyTest, CTest
kutoka test.support agiza bigaddrspacetest


CASES = [
    ('/\\"\ucafe\ubabe\uab98\ufcde\ubcda\uef4a\x08\x0c\n\r\t`1~!@#$%^&*()_+-=[]{}|;:\',./<>?', '"/\\\\\\"\\ucafe\\ubabe\\uab98\\ufcde\\ubcda\\uef4a\\b\\f\\n\\r\\t`1~!@#$%^&*()_+-=[]{}|;:\',./<>?"'),
    ('\u0123\u4567\u89ab\ucdef\uabcd\uef4a', '"\\u0123\\u4567\\u89ab\\ucdef\\uabcd\\uef4a"'),
    ('controls', '"controls"'),
    ('\x08\x0c\n\r\t', '"\\b\\f\\n\\r\\t"'),
    ('{"object ukijumuisha 1 member":["array ukijumuisha 1 element"]}', '"{\\"object ukijumuisha 1 member\\":[\\"array ukijumuisha 1 element\\"]}"'),
    (' s p a c e d ', '" s p a c e d "'),
    ('\U0001d120', '"\\ud834\\udd20"'),
    ('\u03b1\u03a9', '"\\u03b1\\u03a9"'),
    ("`1~!@#$%^&*()_+-={':[,]}|;.</>?", '"`1~!@#$%^&*()_+-={\':[,]}|;.</>?"'),
    ('\x08\x0c\n\r\t', '"\\b\\f\\n\\r\\t"'),
    ('\u0123\u4567\u89ab\ucdef\uabcd\uef4a', '"\\u0123\\u4567\\u89ab\\ucdef\\uabcd\\uef4a"'),
]

kundi TestEncodeBasestringAscii:
    eleza test_encode_basestring_ascii(self):
        fname = self.json.encoder.encode_basestring_ascii.__name__
        kila input_string, expect kwenye CASES:
            result = self.json.encoder.encode_basestring_ascii(input_string)
            self.assertEqual(result, expect,
                '{0!r} != {1!r} kila {2}({3!r})'.format(
                    result, expect, fname, input_string))

    eleza test_ordered_dict(self):
        # See issue 6105
        items = [('one', 1), ('two', 2), ('three', 3), ('four', 4), ('five', 5)]
        s = self.dumps(OrderedDict(items))
        self.assertEqual(s, '{"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}')

    eleza test_sorted_dict(self):
        items = [('one', 1), ('two', 2), ('three', 3), ('four', 4), ('five', 5)]
        s = self.dumps(dict(items), sort_keys=Kweli)
        self.assertEqual(s, '{"five": 5, "four": 4, "one": 1, "three": 3, "two": 2}')


kundi TestPyEncodeBasestringAscii(TestEncodeBasestringAscii, PyTest): pass
kundi TestCEncodeBasestringAscii(TestEncodeBasestringAscii, CTest):
    @bigaddrspacetest
    eleza test_overflow(self):
        size = (2**32)//6 + 1
        s = "\x00"*size
        ukijumuisha self.assertRaises(OverflowError):
            self.json.encoder.encode_basestring_ascii(s)
