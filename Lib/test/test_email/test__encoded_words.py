agiza unittest
kutoka email agiza _encoded_words kama _ew
kutoka email agiza errors
kutoka test.test_email agiza TestEmailBase


kundi TestDecodeQ(TestEmailBase):

    eleza _test(self, source, ex_result, ex_defects=[]):
        result, defects = _ew.decode_q(source)
        self.assertEqual(result, ex_result)
        self.assertDefectsEqual(defects, ex_defects)

    eleza test_no_encoded(self):
        self._test(b'foobar', b'foobar')

    eleza test_spaces(self):
        self._test(b'foo=20bar=20', b'foo bar ')
        self._test(b'foo_bar_', b'foo bar ')

    eleza test_run_of_encoded(self):
        self._test(b'foo=20=20=21=2Cbar', b'foo  !,bar')


kundi TestDecodeB(TestEmailBase):

    eleza _test(self, source, ex_result, ex_defects=[]):
        result, defects = _ew.decode_b(source)
        self.assertEqual(result, ex_result)
        self.assertDefectsEqual(defects, ex_defects)

    eleza test_simple(self):
        self._test(b'Zm9v', b'foo')

    eleza test_missing_padding(self):
        # 1 missing padding character
        self._test(b'dmk', b'vi', [errors.InvalidBase64PaddingDefect])
        # 2 missing padding characters
        self._test(b'dg', b'v', [errors.InvalidBase64PaddingDefect])

    eleza test_invalid_character(self):
        self._test(b'dm\x01k===', b'vi', [errors.InvalidBase64CharactersDefect])

    eleza test_invalid_character_and_bad_padding(self):
        self._test(b'dm\x01k', b'vi', [errors.InvalidBase64CharactersDefect,
                                       errors.InvalidBase64PaddingDefect])

    eleza test_invalid_length(self):
        self._test(b'abcde', b'abcde', [errors.InvalidBase64LengthDefect])


kundi TestDecode(TestEmailBase):

    eleza test_wrong_format_input_ashirias(self):
        ukijumuisha self.assertRaises(ValueError):
            _ew.decode('=?badone?=')
        ukijumuisha self.assertRaises(ValueError):
            _ew.decode('=?')
        ukijumuisha self.assertRaises(ValueError):
            _ew.decode('')
        ukijumuisha self.assertRaises(KeyError):
            _ew.decode('=?utf-8?X?somevalue?=')

    eleza _test(self, source, result, charset='us-ascii', lang='', defects=[]):
        res, char, l, d = _ew.decode(source)
        self.assertEqual(res, result)
        self.assertEqual(char, charset)
        self.assertEqual(l, lang)
        self.assertDefectsEqual(d, defects)

    eleza test_simple_q(self):
        self._test('=?us-ascii?q?foo?=', 'foo')

    eleza test_simple_b(self):
        self._test('=?us-ascii?b?dmk=?=', 'vi')

    eleza test_q_case_ignored(self):
        self._test('=?us-ascii?Q?foo?=', 'foo')

    eleza test_b_case_ignored(self):
        self._test('=?us-ascii?B?dmk=?=', 'vi')

    eleza test_non_trivial_q(self):
        self._test('=?latin-1?q?=20F=fcr=20Elise=20?=', ' Für Elise ', 'latin-1')

    eleza test_q_escaped_bytes_preserved(self):
        self._test(b'=?us-ascii?q?=20\xACfoo?='.decode('us-ascii',
                                                       'surrogateescape'),
                   ' \uDCACfoo',
                   defects = [errors.UndecodableBytesDefect])

    eleza test_b_undecodable_bytes_ignored_with_defect(self):
        self._test(b'=?us-ascii?b?dm\xACk?='.decode('us-ascii',
                                                   'surrogateescape'),
                   'vi',
                   defects = [
                    errors.InvalidBase64CharactersDefect,
                    errors.InvalidBase64PaddingDefect])

    eleza test_b_invalid_bytes_ignored_with_defect(self):
        self._test('=?us-ascii?b?dm\x01k===?=',
                   'vi',
                   defects = [errors.InvalidBase64CharactersDefect])

    eleza test_b_invalid_bytes_incorrect_padding(self):
        self._test('=?us-ascii?b?dm\x01k?=',
                   'vi',
                   defects = [
                    errors.InvalidBase64CharactersDefect,
                    errors.InvalidBase64PaddingDefect])

    eleza test_b_padding_defect(self):
        self._test('=?us-ascii?b?dmk?=',
                   'vi',
                    defects = [errors.InvalidBase64PaddingDefect])

    eleza test_nonnull_lang(self):
        self._test('=?us-ascii*jive?q?test?=', 'test', lang='jive')

    eleza test_unknown_8bit_charset(self):
        self._test('=?unknown-8bit?q?foo=ACbar?=',
                   b'foo\xacbar'.decode('ascii', 'surrogateescape'),
                   charset = 'unknown-8bit',
                   defects = [])

    eleza test_unknown_charset(self):
        self._test('=?foobar?q?foo=ACbar?=',
                   b'foo\xacbar'.decode('ascii', 'surrogateescape'),
                   charset = 'foobar',
                   # XXX Should this be a new Defect instead?
                   defects = [errors.CharsetError])

    eleza test_q_nonascii(self):
        self._test('=?utf-8?q?=C3=89ric?=',
                   'Éric',
                   charset='utf-8')


kundi TestEncodeQ(TestEmailBase):

    eleza _test(self, src, expected):
        self.assertEqual(_ew.encode_q(src), expected)

    eleza test_all_safe(self):
        self._test(b'foobar', 'foobar')

    eleza test_spaces(self):
        self._test(b'foo bar ', 'foo_bar_')

    eleza test_run_of_encodables(self):
        self._test(b'foo  ,,bar', 'foo__=2C=2Cbar')


kundi TestEncodeB(TestEmailBase):

    eleza test_simple(self):
        self.assertEqual(_ew.encode_b(b'foo'), 'Zm9v')

    eleza test_padding(self):
        self.assertEqual(_ew.encode_b(b'vi'), 'dmk=')


kundi TestEncode(TestEmailBase):

    eleza test_q(self):
        self.assertEqual(_ew.encode('foo', 'utf-8', 'q'), '=?utf-8?q?foo?=')

    eleza test_b(self):
        self.assertEqual(_ew.encode('foo', 'utf-8', 'b'), '=?utf-8?b?Zm9v?=')

    eleza test_auto_q(self):
        self.assertEqual(_ew.encode('foo', 'utf-8'), '=?utf-8?q?foo?=')

    eleza test_auto_q_if_short_mostly_safe(self):
        self.assertEqual(_ew.encode('vi.', 'utf-8'), '=?utf-8?q?vi=2E?=')

    eleza test_auto_b_if_enough_unsafe(self):
        self.assertEqual(_ew.encode('.....', 'utf-8'), '=?utf-8?b?Li4uLi4=?=')

    eleza test_auto_b_if_long_unsafe(self):
        self.assertEqual(_ew.encode('vi.vi.vi.vi.vi.', 'utf-8'),
                         '=?utf-8?b?dmkudmkudmkudmkudmku?=')

    eleza test_auto_q_if_long_mostly_safe(self):
        self.assertEqual(_ew.encode('vi vi vi.vi ', 'utf-8'),
                         '=?utf-8?q?vi_vi_vi=2Evi_?=')

    eleza test_utf8_default(self):
        self.assertEqual(_ew.encode('foo'), '=?utf-8?q?foo?=')

    eleza test_lang(self):
        self.assertEqual(_ew.encode('foo', lang='jive'), '=?utf-8*jive?q?foo?=')

    eleza test_unknown_8bit(self):
        self.assertEqual(_ew.encode('foo\uDCACbar', charset='unknown-8bit'),
                         '=?unknown-8bit?q?foo=ACbar?=')


ikiwa __name__ == '__main__':
    unittest.main()
