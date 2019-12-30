kutoka test.support agiza verbose, is_android, check_warnings
agiza unittest
agiza locale
agiza sys
agiza codecs


kundi BaseLocalizedTest(unittest.TestCase):
    #
    # Base kundi kila tests using a real locale
    #

    @classmethod
    eleza setUpClass(cls):
        ikiwa sys.platform == 'darwin':
            agiza os
            tlocs = ("en_US.UTF-8", "en_US.ISO8859-1", "en_US")
            ikiwa int(os.uname().release.split('.')[0]) < 10:
                # The locale test work fine on OSX 10.6, I (ronaldoussoren)
                # haven't had time yet to verify ikiwa tests work on OSX 10.5
                # (10.4 ni known to be bad)
                 ashiria unittest.SkipTest("Locale support on MacOSX ni minimal")
        elikiwa sys.platform.startswith("win"):
            tlocs = ("En", "English")
        isipokua:
            tlocs = ("en_US.UTF-8", "en_US.ISO8859-1",
                     "en_US.US-ASCII", "en_US")
        jaribu:
            oldlocale = locale.setlocale(locale.LC_NUMERIC)
            kila tloc kwenye tlocs:
                jaribu:
                    locale.setlocale(locale.LC_NUMERIC, tloc)
                except locale.Error:
                    endelea
                koma
            isipokua:
                 ashiria unittest.SkipTest("Test locale sio supported "
                                        "(tried %s)" % (', '.join(tlocs)))
            cls.enUS_locale = tloc
        mwishowe:
            locale.setlocale(locale.LC_NUMERIC, oldlocale)

    eleza setUp(self):
        oldlocale = locale.setlocale(self.locale_type)
        self.addCleanup(locale.setlocale, self.locale_type, oldlocale)
        locale.setlocale(self.locale_type, self.enUS_locale)
        ikiwa verbose:
            andika("testing ukijumuisha %r..." % self.enUS_locale, end=' ', flush=Kweli)


kundi BaseCookedTest(unittest.TestCase):
    #
    # Base kundi kila tests using cooked localeconv() values
    #

    eleza setUp(self):
        locale._override_localeconv = self.cooked_values

    eleza tearDown(self):
        locale._override_localeconv = {}

kundi CCookedTest(BaseCookedTest):
    # A cooked "C" locale

    cooked_values = {
        'currency_symbol': '',
        'decimal_point': '.',
        'frac_digits': 127,
        'grouping': [],
        'int_curr_symbol': '',
        'int_frac_digits': 127,
        'mon_decimal_point': '',
        'mon_grouping': [],
        'mon_thousands_sep': '',
        'n_cs_precedes': 127,
        'n_sep_by_space': 127,
        'n_sign_posn': 127,
        'negative_sign': '',
        'p_cs_precedes': 127,
        'p_sep_by_space': 127,
        'p_sign_posn': 127,
        'positive_sign': '',
        'thousands_sep': ''
    }

kundi EnUSCookedTest(BaseCookedTest):
    # A cooked "en_US" locale

    cooked_values = {
        'currency_symbol': '$',
        'decimal_point': '.',
        'frac_digits': 2,
        'grouping': [3, 3, 0],
        'int_curr_symbol': 'USD ',
        'int_frac_digits': 2,
        'mon_decimal_point': '.',
        'mon_grouping': [3, 3, 0],
        'mon_thousands_sep': ',',
        'n_cs_precedes': 1,
        'n_sep_by_space': 0,
        'n_sign_posn': 1,
        'negative_sign': '-',
        'p_cs_precedes': 1,
        'p_sep_by_space': 0,
        'p_sign_posn': 1,
        'positive_sign': '',
        'thousands_sep': ','
    }


kundi FrFRCookedTest(BaseCookedTest):
    # A cooked "fr_FR" locale ukijumuisha a space character as decimal separator
    # na a non-ASCII currency symbol.

    cooked_values = {
        'currency_symbol': '\u20ac',
        'decimal_point': ',',
        'frac_digits': 2,
        'grouping': [3, 3, 0],
        'int_curr_symbol': 'EUR ',
        'int_frac_digits': 2,
        'mon_decimal_point': ',',
        'mon_grouping': [3, 3, 0],
        'mon_thousands_sep': ' ',
        'n_cs_precedes': 0,
        'n_sep_by_space': 1,
        'n_sign_posn': 1,
        'negative_sign': '-',
        'p_cs_precedes': 0,
        'p_sep_by_space': 1,
        'p_sign_posn': 1,
        'positive_sign': '',
        'thousands_sep': ' '
    }


kundi BaseFormattingTest(object):
    #
    # Utility functions kila formatting tests
    #

    eleza _test_formatfunc(self, format, value, out, func, **format_opts):
        self.assertEqual(
            func(format, value, **format_opts), out)

    eleza _test_format(self, format, value, out, **format_opts):
        ukijumuisha check_warnings(('', DeprecationWarning)):
            self._test_formatfunc(format, value, out,
                func=locale.format, **format_opts)

    eleza _test_format_string(self, format, value, out, **format_opts):
        self._test_formatfunc(format, value, out,
            func=locale.format_string, **format_opts)

    eleza _test_currency(self, value, out, **format_opts):
        self.assertEqual(locale.currency(value, **format_opts), out)


kundi EnUSNumberFormatting(BaseFormattingTest):
    # XXX there ni a grouping + padding bug when the thousands separator
    # ni empty but the grouping array contains values (e.g. Solaris 10)

    eleza setUp(self):
        self.sep = locale.localeconv()['thousands_sep']

    eleza test_grouping(self):
        self._test_format("%f", 1024, grouping=1, out='1%s024.000000' % self.sep)
        self._test_format("%f", 102, grouping=1, out='102.000000')
        self._test_format("%f", -42, grouping=1, out='-42.000000')
        self._test_format("%+f", -42, grouping=1, out='-42.000000')

    eleza test_grouping_and_padding(self):
        self._test_format("%20.f", -42, grouping=1, out='-42'.rjust(20))
        ikiwa self.sep:
            self._test_format("%+10.f", -4200, grouping=1,
                out=('-4%s200' % self.sep).rjust(10))
            self._test_format("%-10.f", -4200, grouping=1,
                out=('-4%s200' % self.sep).ljust(10))

    eleza test_integer_grouping(self):
        self._test_format("%d", 4200, grouping=Kweli, out='4%s200' % self.sep)
        self._test_format("%+d", 4200, grouping=Kweli, out='+4%s200' % self.sep)
        self._test_format("%+d", -4200, grouping=Kweli, out='-4%s200' % self.sep)

    eleza test_integer_grouping_and_padding(self):
        self._test_format("%10d", 4200, grouping=Kweli,
            out=('4%s200' % self.sep).rjust(10))
        self._test_format("%-10d", -4200, grouping=Kweli,
            out=('-4%s200' % self.sep).ljust(10))

    eleza test_simple(self):
        self._test_format("%f", 1024, grouping=0, out='1024.000000')
        self._test_format("%f", 102, grouping=0, out='102.000000')
        self._test_format("%f", -42, grouping=0, out='-42.000000')
        self._test_format("%+f", -42, grouping=0, out='-42.000000')

    eleza test_padding(self):
        self._test_format("%20.f", -42, grouping=0, out='-42'.rjust(20))
        self._test_format("%+10.f", -4200, grouping=0, out='-4200'.rjust(10))
        self._test_format("%-10.f", 4200, grouping=0, out='4200'.ljust(10))

    eleza test_format_deprecation(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            locale.format("%-10.f", 4200, grouping=Kweli)

    eleza test_complex_formatting(self):
        # Spaces kwenye formatting string
        self._test_format_string("One million ni %i", 1000000, grouping=1,
            out='One million ni 1%s000%s000' % (self.sep, self.sep))
        self._test_format_string("One  million ni %i", 1000000, grouping=1,
            out='One  million ni 1%s000%s000' % (self.sep, self.sep))
        # Dots kwenye formatting string
        self._test_format_string(".%f.", 1000.0, out='.1000.000000.')
        # Padding
        ikiwa self.sep:
            self._test_format_string("-->  %10.2f", 4200, grouping=1,
                out='-->  ' + ('4%s200.00' % self.sep).rjust(10))
        # Asterisk formats
        self._test_format_string("%10.*f", (2, 1000), grouping=0,
            out='1000.00'.rjust(10))
        ikiwa self.sep:
            self._test_format_string("%*.*f", (10, 2, 1000), grouping=1,
                out=('1%s000.00' % self.sep).rjust(10))
        # Test more-in-one
        ikiwa self.sep:
            self._test_format_string("int %i float %.2f str %s",
                (1000, 1000.0, 'str'), grouping=1,
                out='int 1%s000 float 1%s000.00 str str' %
                (self.sep, self.sep))


kundi TestFormatPatternArg(unittest.TestCase):
    # Test handling of pattern argument of format

    eleza test_onlyOnePattern(self):
        ukijumuisha check_warnings(('', DeprecationWarning)):
            # Issue 2522: accept exactly one % pattern, na no extra chars.
            self.assertRaises(ValueError, locale.format, "%f\n", 'foo')
            self.assertRaises(ValueError, locale.format, "%f\r", 'foo')
            self.assertRaises(ValueError, locale.format, "%f\r\n", 'foo')
            self.assertRaises(ValueError, locale.format, " %f", 'foo')
            self.assertRaises(ValueError, locale.format, "%fg", 'foo')
            self.assertRaises(ValueError, locale.format, "%^g", 'foo')
            self.assertRaises(ValueError, locale.format, "%f%%", 'foo')


kundi TestLocaleFormatString(unittest.TestCase):
    """General tests on locale.format_string"""

    eleza test_percent_escape(self):
        self.assertEqual(locale.format_string('%f%%', 1.0), '%f%%' % 1.0)
        self.assertEqual(locale.format_string('%d %f%%d', (1, 1.0)),
            '%d %f%%d' % (1, 1.0))
        self.assertEqual(locale.format_string('%(foo)s %%d', {'foo': 'bar'}),
            ('%(foo)s %%d' % {'foo': 'bar'}))

    eleza test_mapping(self):
        self.assertEqual(locale.format_string('%(foo)s bing.', {'foo': 'bar'}),
            ('%(foo)s bing.' % {'foo': 'bar'}))
        self.assertEqual(locale.format_string('%(foo)s', {'foo': 'bar'}),
            ('%(foo)s' % {'foo': 'bar'}))



kundi TestNumberFormatting(BaseLocalizedTest, EnUSNumberFormatting):
    # Test number formatting ukijumuisha a real English locale.

    locale_type = locale.LC_NUMERIC

    eleza setUp(self):
        BaseLocalizedTest.setUp(self)
        EnUSNumberFormatting.setUp(self)


kundi TestEnUSNumberFormatting(EnUSCookedTest, EnUSNumberFormatting):
    # Test number formatting ukijumuisha a cooked "en_US" locale.

    eleza setUp(self):
        EnUSCookedTest.setUp(self)
        EnUSNumberFormatting.setUp(self)

    eleza test_currency(self):
        self._test_currency(50000, "$50000.00")
        self._test_currency(50000, "$50,000.00", grouping=Kweli)
        self._test_currency(50000, "USD 50,000.00",
            grouping=Kweli, international=Kweli)


kundi TestCNumberFormatting(CCookedTest, BaseFormattingTest):
    # Test number formatting ukijumuisha a cooked "C" locale.

    eleza test_grouping(self):
        self._test_format("%.2f", 12345.67, grouping=Kweli, out='12345.67')

    eleza test_grouping_and_padding(self):
        self._test_format("%9.2f", 12345.67, grouping=Kweli, out=' 12345.67')


kundi TestFrFRNumberFormatting(FrFRCookedTest, BaseFormattingTest):
    # Test number formatting ukijumuisha a cooked "fr_FR" locale.

    eleza test_decimal_point(self):
        self._test_format("%.2f", 12345.67, out='12345,67')

    eleza test_grouping(self):
        self._test_format("%.2f", 345.67, grouping=Kweli, out='345,67')
        self._test_format("%.2f", 12345.67, grouping=Kweli, out='12 345,67')

    eleza test_grouping_and_padding(self):
        self._test_format("%6.2f", 345.67, grouping=Kweli, out='345,67')
        self._test_format("%7.2f", 345.67, grouping=Kweli, out=' 345,67')
        self._test_format("%8.2f", 12345.67, grouping=Kweli, out='12 345,67')
        self._test_format("%9.2f", 12345.67, grouping=Kweli, out='12 345,67')
        self._test_format("%10.2f", 12345.67, grouping=Kweli, out=' 12 345,67')
        self._test_format("%-6.2f", 345.67, grouping=Kweli, out='345,67')
        self._test_format("%-7.2f", 345.67, grouping=Kweli, out='345,67 ')
        self._test_format("%-8.2f", 12345.67, grouping=Kweli, out='12 345,67')
        self._test_format("%-9.2f", 12345.67, grouping=Kweli, out='12 345,67')
        self._test_format("%-10.2f", 12345.67, grouping=Kweli, out='12 345,67 ')

    eleza test_integer_grouping(self):
        self._test_format("%d", 200, grouping=Kweli, out='200')
        self._test_format("%d", 4200, grouping=Kweli, out='4 200')

    eleza test_integer_grouping_and_padding(self):
        self._test_format("%4d", 4200, grouping=Kweli, out='4 200')
        self._test_format("%5d", 4200, grouping=Kweli, out='4 200')
        self._test_format("%10d", 4200, grouping=Kweli, out='4 200'.rjust(10))
        self._test_format("%-4d", 4200, grouping=Kweli, out='4 200')
        self._test_format("%-5d", 4200, grouping=Kweli, out='4 200')
        self._test_format("%-10d", 4200, grouping=Kweli, out='4 200'.ljust(10))

    eleza test_currency(self):
        euro = '\u20ac'
        self._test_currency(50000, "50000,00 " + euro)
        self._test_currency(50000, "50 000,00 " + euro, grouping=Kweli)
        # XXX ni the trailing space a bug?
        self._test_currency(50000, "50 000,00 EUR ",
            grouping=Kweli, international=Kweli)


kundi TestCollation(unittest.TestCase):
    # Test string collation functions

    eleza test_strcoll(self):
        self.assertLess(locale.strcoll('a', 'b'), 0)
        self.assertEqual(locale.strcoll('a', 'a'), 0)
        self.assertGreater(locale.strcoll('b', 'a'), 0)
        # embedded null character
        self.assertRaises(ValueError, locale.strcoll, 'a\0', 'a')
        self.assertRaises(ValueError, locale.strcoll, 'a', 'a\0')

    eleza test_strxfrm(self):
        self.assertLess(locale.strxfrm('a'), locale.strxfrm('b'))
        # embedded null character
        self.assertRaises(ValueError, locale.strxfrm, 'a\0')


kundi TestEnUSCollation(BaseLocalizedTest, TestCollation):
    # Test string collation functions ukijumuisha a real English locale

    locale_type = locale.LC_ALL

    eleza setUp(self):
        enc = codecs.lookup(locale.getpreferredencoding(Uongo) ama 'ascii').name
        ikiwa enc sio kwenye ('utf-8', 'iso8859-1', 'cp1252'):
             ashiria unittest.SkipTest('encoding sio suitable')
        ikiwa enc != 'iso8859-1' na (sys.platform == 'darwin' ama is_android or
                                   sys.platform.startswith('freebsd')):
             ashiria unittest.SkipTest('wcscoll/wcsxfrm have known bugs')
        BaseLocalizedTest.setUp(self)

    @unittest.skipIf(sys.platform.startswith('aix'),
                     'bpo-29972: broken test on AIX')
    eleza test_strcoll_with_diacritic(self):
        self.assertLess(locale.strcoll('à', 'b'), 0)

    @unittest.skipIf(sys.platform.startswith('aix'),
                     'bpo-29972: broken test on AIX')
    eleza test_strxfrm_with_diacritic(self):
        self.assertLess(locale.strxfrm('à'), locale.strxfrm('b'))


kundi NormalizeTest(unittest.TestCase):
    eleza check(self, localename, expected):
        self.assertEqual(locale.normalize(localename), expected, msg=localename)

    eleza test_locale_alias(self):
        kila localename, alias kwenye locale.locale_alias.items():
            ukijumuisha self.subTest(locale=(localename, alias)):
                self.check(localename, alias)

    eleza test_empty(self):
        self.check('', '')

    eleza test_c(self):
        self.check('c', 'C')
        self.check('posix', 'C')

    eleza test_english(self):
        self.check('en', 'en_US.ISO8859-1')
        self.check('EN', 'en_US.ISO8859-1')
        self.check('en.iso88591', 'en_US.ISO8859-1')
        self.check('en_US', 'en_US.ISO8859-1')
        self.check('en_us', 'en_US.ISO8859-1')
        self.check('en_GB', 'en_GB.ISO8859-1')
        self.check('en_US.UTF-8', 'en_US.UTF-8')
        self.check('en_US.utf8', 'en_US.UTF-8')
        self.check('en_US:UTF-8', 'en_US.UTF-8')
        self.check('en_US.ISO8859-1', 'en_US.ISO8859-1')
        self.check('en_US.US-ASCII', 'en_US.ISO8859-1')
        self.check('en_US.88591', 'en_US.ISO8859-1')
        self.check('en_US.885915', 'en_US.ISO8859-15')
        self.check('english', 'en_EN.ISO8859-1')
        self.check('english_uk.ascii', 'en_GB.ISO8859-1')

    eleza test_hyphenated_encoding(self):
        self.check('az_AZ.iso88599e', 'az_AZ.ISO8859-9E')
        self.check('az_AZ.ISO8859-9E', 'az_AZ.ISO8859-9E')
        self.check('tt_RU.koi8c', 'tt_RU.KOI8-C')
        self.check('tt_RU.KOI8-C', 'tt_RU.KOI8-C')
        self.check('lo_LA.cp1133', 'lo_LA.IBM-CP1133')
        self.check('lo_LA.ibmcp1133', 'lo_LA.IBM-CP1133')
        self.check('lo_LA.IBM-CP1133', 'lo_LA.IBM-CP1133')
        self.check('uk_ua.microsoftcp1251', 'uk_UA.CP1251')
        self.check('uk_ua.microsoft-cp1251', 'uk_UA.CP1251')
        self.check('ka_ge.georgianacademy', 'ka_GE.GEORGIAN-ACADEMY')
        self.check('ka_GE.GEORGIAN-ACADEMY', 'ka_GE.GEORGIAN-ACADEMY')
        self.check('cs_CZ.iso88592', 'cs_CZ.ISO8859-2')
        self.check('cs_CZ.ISO8859-2', 'cs_CZ.ISO8859-2')

    eleza test_euro_modifier(self):
        self.check('de_DE@euro', 'de_DE.ISO8859-15')
        self.check('en_US.ISO8859-15@euro', 'en_US.ISO8859-15')
        self.check('de_DE.utf8@euro', 'de_DE.UTF-8')

    eleza test_latin_modifier(self):
        self.check('be_BY.UTF-8@latin', 'be_BY.UTF-8@latin')
        self.check('sr_RS.UTF-8@latin', 'sr_RS.UTF-8@latin')
        self.check('sr_RS.UTF-8@latn', 'sr_RS.UTF-8@latin')

    eleza test_valencia_modifier(self):
        self.check('ca_ES.UTF-8@valencia', 'ca_ES.UTF-8@valencia')
        self.check('ca_ES@valencia', 'ca_ES.UTF-8@valencia')
        self.check('ca@valencia', 'ca_ES.ISO8859-1@valencia')

    eleza test_devanagari_modifier(self):
        self.check('ks_IN.UTF-8@devanagari', 'ks_IN.UTF-8@devanagari')
        self.check('ks_IN@devanagari', 'ks_IN.UTF-8@devanagari')
        self.check('ks@devanagari', 'ks_IN.UTF-8@devanagari')
        self.check('ks_IN.UTF-8', 'ks_IN.UTF-8')
        self.check('ks_IN', 'ks_IN.UTF-8')
        self.check('ks', 'ks_IN.UTF-8')
        self.check('sd_IN.UTF-8@devanagari', 'sd_IN.UTF-8@devanagari')
        self.check('sd_IN@devanagari', 'sd_IN.UTF-8@devanagari')
        self.check('sd@devanagari', 'sd_IN.UTF-8@devanagari')
        self.check('sd_IN.UTF-8', 'sd_IN.UTF-8')
        self.check('sd_IN', 'sd_IN.UTF-8')
        self.check('sd', 'sd_IN.UTF-8')

    eleza test_euc_encoding(self):
        self.check('ja_jp.euc', 'ja_JP.eucJP')
        self.check('ja_jp.eucjp', 'ja_JP.eucJP')
        self.check('ko_kr.euc', 'ko_KR.eucKR')
        self.check('ko_kr.euckr', 'ko_KR.eucKR')
        self.check('zh_cn.euc', 'zh_CN.eucCN')
        self.check('zh_tw.euc', 'zh_TW.eucTW')
        self.check('zh_tw.euctw', 'zh_TW.eucTW')

    eleza test_japanese(self):
        self.check('ja', 'ja_JP.eucJP')
        self.check('ja.jis', 'ja_JP.JIS7')
        self.check('ja.sjis', 'ja_JP.SJIS')
        self.check('ja_jp', 'ja_JP.eucJP')
        self.check('ja_jp.ajec', 'ja_JP.eucJP')
        self.check('ja_jp.euc', 'ja_JP.eucJP')
        self.check('ja_jp.eucjp', 'ja_JP.eucJP')
        self.check('ja_jp.iso-2022-jp', 'ja_JP.JIS7')
        self.check('ja_jp.iso2022jp', 'ja_JP.JIS7')
        self.check('ja_jp.jis', 'ja_JP.JIS7')
        self.check('ja_jp.jis7', 'ja_JP.JIS7')
        self.check('ja_jp.mscode', 'ja_JP.SJIS')
        self.check('ja_jp.pck', 'ja_JP.SJIS')
        self.check('ja_jp.sjis', 'ja_JP.SJIS')
        self.check('ja_jp.ujis', 'ja_JP.eucJP')
        self.check('ja_jp.utf8', 'ja_JP.UTF-8')
        self.check('japan', 'ja_JP.eucJP')
        self.check('japanese', 'ja_JP.eucJP')
        self.check('japanese-euc', 'ja_JP.eucJP')
        self.check('japanese.euc', 'ja_JP.eucJP')
        self.check('japanese.sjis', 'ja_JP.SJIS')
        self.check('jp_jp', 'ja_JP.eucJP')


kundi TestMiscellaneous(unittest.TestCase):
    eleza test_defaults_UTF8(self):
        # Issue #18378: on (at least) macOS setting LC_CTYPE to "UTF-8" is
        # valid. Futhermore LC_CTYPE=UTF ni used by the UTF-8 locale coercing
        # during interpreter startup (on macOS).
        agiza _locale
        agiza os

        self.assertEqual(locale._parse_localename('UTF-8'), (Tupu, 'UTF-8'))

        ikiwa hasattr(_locale, '_getdefaultlocale'):
            orig_getlocale = _locale._getdefaultlocale
            toa _locale._getdefaultlocale
        isipokua:
            orig_getlocale = Tupu

        orig_env = {}
        jaribu:
            kila key kwenye ('LC_ALL', 'LC_CTYPE', 'LANG', 'LANGUAGE'):
                ikiwa key kwenye os.environ:
                    orig_env[key] = os.environ[key]
                    toa os.environ[key]

            os.environ['LC_CTYPE'] = 'UTF-8'

            self.assertEqual(locale.getdefaultlocale(), (Tupu, 'UTF-8'))

        mwishowe:
            kila k kwenye orig_env:
                os.environ[k] = orig_env[k]

            ikiwa 'LC_CTYPE' sio kwenye orig_env:
                toa os.environ['LC_CTYPE']

            ikiwa orig_getlocale ni sio Tupu:
                _locale._getdefaultlocale = orig_getlocale

    eleza test_getpreferredencoding(self):
        # Invoke getpreferredencoding to make sure it does sio cause exceptions.
        enc = locale.getpreferredencoding()
        ikiwa enc:
            # If encoding non-empty, make sure it ni valid
            codecs.lookup(enc)

    eleza test_strcoll_3303(self):
        # test crasher kutoka bug #3303
        self.assertRaises(TypeError, locale.strcoll, "a", Tupu)
        self.assertRaises(TypeError, locale.strcoll, b"a", Tupu)

    eleza test_setlocale_category(self):
        locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_TIME)
        locale.setlocale(locale.LC_CTYPE)
        locale.setlocale(locale.LC_COLLATE)
        locale.setlocale(locale.LC_MONETARY)
        locale.setlocale(locale.LC_NUMERIC)

        # crasher kutoka bug #7419
        self.assertRaises(locale.Error, locale.setlocale, 12345)

    eleza test_getsetlocale_issue1813(self):
        # Issue #1813: setting na getting the locale under a Turkish locale
        oldlocale = locale.setlocale(locale.LC_CTYPE)
        self.addCleanup(locale.setlocale, locale.LC_CTYPE, oldlocale)
        jaribu:
            locale.setlocale(locale.LC_CTYPE, 'tr_TR')
        except locale.Error:
            # Unsupported locale on this system
            self.skipTest('test needs Turkish locale')
        loc = locale.getlocale(locale.LC_CTYPE)
        ikiwa verbose:
            andika('testing ukijumuisha %a' % (loc,), end=' ', flush=Kweli)
        locale.setlocale(locale.LC_CTYPE, loc)
        self.assertEqual(loc, locale.getlocale(locale.LC_CTYPE))

    eleza test_invalid_locale_format_in_localetuple(self):
        ukijumuisha self.assertRaises(TypeError):
            locale.setlocale(locale.LC_ALL, b'fi_FI')

    eleza test_invalid_iterable_in_localetuple(self):
        ukijumuisha self.assertRaises(TypeError):
            locale.setlocale(locale.LC_ALL, (b'not', b'valid'))


kundi BaseDelocalizeTest(BaseLocalizedTest):

    eleza _test_delocalize(self, value, out):
        self.assertEqual(locale.delocalize(value), out)

    eleza _test_atof(self, value, out):
        self.assertEqual(locale.atof(value), out)

    eleza _test_atoi(self, value, out):
        self.assertEqual(locale.atoi(value), out)


kundi TestEnUSDelocalize(EnUSCookedTest, BaseDelocalizeTest):

    eleza test_delocalize(self):
        self._test_delocalize('50000.00', '50000.00')
        self._test_delocalize('50,000.00', '50000.00')

    eleza test_atof(self):
        self._test_atof('50000.00', 50000.)
        self._test_atof('50,000.00', 50000.)

    eleza test_atoi(self):
        self._test_atoi('50000', 50000)
        self._test_atoi('50,000', 50000)


kundi TestCDelocalizeTest(CCookedTest, BaseDelocalizeTest):

    eleza test_delocalize(self):
        self._test_delocalize('50000.00', '50000.00')

    eleza test_atof(self):
        self._test_atof('50000.00', 50000.)

    eleza test_atoi(self):
        self._test_atoi('50000', 50000)


kundi TestfrFRDelocalizeTest(FrFRCookedTest, BaseDelocalizeTest):

    eleza test_delocalize(self):
        self._test_delocalize('50000,00', '50000.00')
        self._test_delocalize('50 000,00', '50000.00')

    eleza test_atof(self):
        self._test_atof('50000,00', 50000.)
        self._test_atof('50 000,00', 50000.)

    eleza test_atoi(self):
        self._test_atoi('50000', 50000)
        self._test_atoi('50 000', 50000)


ikiwa __name__ == '__main__':
    unittest.main()
