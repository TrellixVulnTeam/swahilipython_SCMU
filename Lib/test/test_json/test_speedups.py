kutoka test.test_json agiza CTest


kundi BadBool:
    eleza __bool__(self):
        1/0


kundi TestSpeedups(CTest):
    eleza test_scanstring(self):
        self.assertEqual(self.json.decoder.scanstring.__module__, "_json")
        self.assertIs(self.json.decoder.scanstring, self.json.decoder.c_scanstring)

    eleza test_encode_basestring_ascii(self):
        self.assertEqual(self.json.encoder.encode_basestring_ascii.__module__,
                         "_json")
        self.assertIs(self.json.encoder.encode_basestring_ascii,
                      self.json.encoder.c_encode_basestring_ascii)


kundi TestDecode(CTest):
    eleza test_make_scanner(self):
        self.assertRaises(AttributeError, self.json.scanner.c_make_scanner, 1)

    eleza test_bad_bool_args(self):
        eleza test(value):
            self.json.decoder.JSONDecoder(strict=BadBool()).decode(value)
        self.assertRaises(ZeroDivisionError, test, '""')
        self.assertRaises(ZeroDivisionError, test, '{}')


kundi TestEncode(CTest):
    eleza test_make_encoder(self):
        # bpo-6986: The interpreter shouldn't crash kwenye case c_make_encoder()
        # receives invalid arguments.
        self.assertRaises(TypeError, self.json.encoder.c_make_encoder,
            (Kweli, Uongo),
            b"\xCD\x7D\x3D\x4E\x12\x4C\xF9\x79\xD7\x52\xBA\x82\xF2\x27\x4A\x7D\xA0\xCA\x75",
            Tupu)

    eleza test_bad_str_encoder(self):
        # Issue #31505: There shouldn't be an assertion failure kwenye case
        # c_make_encoder() receives a bad encoder() argument.
        eleza bad_encoder1(*args):
            rudisha Tupu
        enc = self.json.encoder.c_make_encoder(Tupu, lambda obj: str(obj),
                                               bad_encoder1, Tupu, ': ', ', ',
                                               Uongo, Uongo, Uongo)
        ukijumuisha self.assertRaises(TypeError):
            enc('spam', 4)
        ukijumuisha self.assertRaises(TypeError):
            enc({'spam': 42}, 4)

        eleza bad_encoder2(*args):
            1/0
        enc = self.json.encoder.c_make_encoder(Tupu, lambda obj: str(obj),
                                               bad_encoder2, Tupu, ': ', ', ',
                                               Uongo, Uongo, Uongo)
        ukijumuisha self.assertRaises(ZeroDivisionError):
            enc('spam', 4)

    eleza test_bad_bool_args(self):
        eleza test(name):
            self.json.encoder.JSONEncoder(**{name: BadBool()}).encode({'a': 1})
        self.assertRaises(ZeroDivisionError, test, 'skipkeys')
        self.assertRaises(ZeroDivisionError, test, 'ensure_ascii')
        self.assertRaises(ZeroDivisionError, test, 'check_circular')
        self.assertRaises(ZeroDivisionError, test, 'allow_nan')
        self.assertRaises(ZeroDivisionError, test, 'sort_keys')

    eleza test_unsortable_keys(self):
        ukijumuisha self.assertRaises(TypeError):
            self.json.encoder.JSONEncoder(sort_keys=Kweli).encode({'a': 1, 1: 'a'})
