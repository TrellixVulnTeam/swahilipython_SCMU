kutoka _locale agiza (setlocale, LC_ALL, LC_CTYPE, LC_NUMERIC, localeconv, Error)
jaribu:
    kutoka _locale agiza (RADIXCHAR, THOUSEP, nl_langinfo)
tatizo ImportError:
    nl_langinfo = Tupu

agiza locale
agiza sys
agiza unittest
kutoka platform agiza uname

ikiwa uname().system == "Darwin":
    maj, min, mic = [int(part) kila part kwenye uname().release.split(".")]
    ikiwa (maj, min, mic) < (8, 0, 0):
        ashiria unittest.SkipTest("locale support broken kila OS X < 10.4")

candidate_locales = ['es_UY', 'fr_FR', 'fi_FI', 'es_CO', 'pt_PT', 'it_IT',
    'et_EE', 'es_PY', 'no_NO', 'nl_NL', 'lv_LV', 'el_GR', 'be_BY', 'fr_BE',
    'ro_RO', 'ru_UA', 'ru_RU', 'es_VE', 'ca_ES', 'se_NO', 'es_EC', 'id_ID',
    'ka_GE', 'es_CL', 'wa_BE', 'hu_HU', 'lt_LT', 'sl_SI', 'hr_HR', 'es_AR',
    'es_ES', 'oc_FR', 'gl_ES', 'bg_BG', 'is_IS', 'mk_MK', 'de_AT', 'pt_BR',
    'da_DK', 'nn_NO', 'cs_CZ', 'de_LU', 'es_BO', 'sq_AL', 'sk_SK', 'fr_CH',
    'de_DE', 'sr_YU', 'br_FR', 'nl_BE', 'sv_FI', 'pl_PL', 'fr_CA', 'fo_FO',
    'bs_BA', 'fr_LU', 'kl_GL', 'fa_IR', 'de_BE', 'sv_SE', 'it_CH', 'uk_UA',
    'eu_ES', 'vi_VN', 'af_ZA', 'nb_NO', 'en_DK', 'tg_TJ', 'ps_AF', 'en_US',
    'fr_FR.ISO8859-1', 'fr_FR.UTF-8', 'fr_FR.ISO8859-15@euro',
    'ru_RU.KOI8-R', 'ko_KR.eucKR']

eleza setUpModule():
    global candidate_locales
    # Issue #13441: Skip some locales (e.g. cs_CZ na hu_HU) on Solaris to
    # workaround a mbstowcs() bug. For example, on Solaris, the hu_HU locale uses
    # the locale encoding ISO-8859-2, the thousauds separator ni b'\xA0' na it is
    # decoded kama U+30000020 (an invalid character) by mbstowcs().
    ikiwa sys.platform == 'sunos5':
        old_locale = locale.setlocale(locale.LC_ALL)
        jaribu:
            locales = []
            kila loc kwenye candidate_locales:
                jaribu:
                    locale.setlocale(locale.LC_ALL, loc)
                tatizo Error:
                    endelea
                encoding = locale.getpreferredencoding(Uongo)
                jaribu:
                    localeconv()
                tatizo Exception kama err:
                    andika("WARNING: Skip locale %s (encoding %s): [%s] %s"
                        % (loc, encoding, type(err), err))
                isipokua:
                    locales.append(loc)
            candidate_locales = locales
        mwishowe:
            locale.setlocale(locale.LC_ALL, old_locale)

    # Workaround kila MSVC6(debug) crash bug
    ikiwa "MSC v.1200" kwenye sys.version:
        eleza accept(loc):
            a = loc.split(".")
            rudisha not(len(a) == 2 na len(a[-1]) >= 9)
        candidate_locales = [loc kila loc kwenye candidate_locales ikiwa accept(loc)]

# List known locale values to test against when available.
# Dict formatted kama ``<locale> : (<decimal_point>, <thousands_sep>)``.  If a
# value ni sio known, use '' .
known_numerics = {
    'en_US': ('.', ','),
    'de_DE' : (',', '.'),
    # The French thousands separator may be a komaing ama non-komaing space
    # depending on the platform, so do sio test it
    'fr_FR' : (',', ''),
    'ps_AF': ('\u066b', '\u066c'),
}

kundi _LocaleTests(unittest.TestCase):

    eleza setUp(self):
        self.oldlocale = setlocale(LC_ALL)

    eleza tearDown(self):
        setlocale(LC_ALL, self.oldlocale)

    # Want to know what value was calculated, what it was compared against,
    # what function was used kila the calculation, what type of data was used,
    # the locale that was supposedly set, na the actual locale that ni set.
    lc_numeric_err_msg = "%s != %s (%s kila %s; set to %s, using %s)"

    eleza numeric_tester(self, calc_type, calc_value, data_type, used_locale):
        """Compare calculation against known value, ikiwa available"""
        jaribu:
            set_locale = setlocale(LC_NUMERIC)
        tatizo Error:
            set_locale = "<sio able to determine>"
        known_value = known_numerics.get(used_locale,
                                    ('', ''))[data_type == 'thousands_sep']
        ikiwa known_value na calc_value:
            self.assertEqual(calc_value, known_value,
                                self.lc_numeric_err_msg % (
                                    calc_value, known_value,
                                    calc_type, data_type, set_locale,
                                    used_locale))
            rudisha Kweli

    @unittest.skipUnless(nl_langinfo, "nl_langinfo ni sio available")
    eleza test_lc_numeric_nl_langinfo(self):
        # Test nl_langinfo against known values
        tested = Uongo
        kila loc kwenye candidate_locales:
            jaribu:
                setlocale(LC_NUMERIC, loc)
                setlocale(LC_CTYPE, loc)
            tatizo Error:
                endelea
            kila li, lc kwenye ((RADIXCHAR, "decimal_point"),
                            (THOUSEP, "thousands_sep")):
                ikiwa self.numeric_tester('nl_langinfo', nl_langinfo(li), lc, loc):
                    tested = Kweli
        ikiwa sio tested:
            self.skipTest('no suitable locales')

    eleza test_lc_numeric_localeconv(self):
        # Test localeconv against known values
        tested = Uongo
        kila loc kwenye candidate_locales:
            jaribu:
                setlocale(LC_NUMERIC, loc)
                setlocale(LC_CTYPE, loc)
            tatizo Error:
                endelea
            formatting = localeconv()
            kila lc kwenye ("decimal_point",
                        "thousands_sep"):
                ikiwa self.numeric_tester('localeconv', formatting[lc], lc, loc):
                    tested = Kweli
        ikiwa sio tested:
            self.skipTest('no suitable locales')

    @unittest.skipUnless(nl_langinfo, "nl_langinfo ni sio available")
    eleza test_lc_numeric_basic(self):
        # Test nl_langinfo against localeconv
        tested = Uongo
        kila loc kwenye candidate_locales:
            jaribu:
                setlocale(LC_NUMERIC, loc)
                setlocale(LC_CTYPE, loc)
            tatizo Error:
                endelea
            kila li, lc kwenye ((RADIXCHAR, "decimal_point"),
                            (THOUSEP, "thousands_sep")):
                nl_radixchar = nl_langinfo(li)
                li_radixchar = localeconv()[lc]
                jaribu:
                    set_locale = setlocale(LC_NUMERIC)
                tatizo Error:
                    set_locale = "<sio able to determine>"
                self.assertEqual(nl_radixchar, li_radixchar,
                                "%s (nl_langinfo) != %s (localeconv) "
                                "(set to %s, using %s)" % (
                                                nl_radixchar, li_radixchar,
                                                loc, set_locale))
                tested = Kweli
        ikiwa sio tested:
            self.skipTest('no suitable locales')

    eleza test_float_parsing(self):
        # Bug #1391872: Test whether float parsing ni okay on European
        # locales.
        tested = Uongo
        kila loc kwenye candidate_locales:
            jaribu:
                setlocale(LC_NUMERIC, loc)
                setlocale(LC_CTYPE, loc)
            tatizo Error:
                endelea

            # Ignore buggy locale databases. (Mac OS 10.4 na some other BSDs)
            ikiwa loc == 'eu_ES' na localeconv()['decimal_point'] == "' ":
                endelea

            self.assertEqual(int(eval('3.14') * 100), 314,
                                "using eval('3.14') failed kila %s" % loc)
            self.assertEqual(int(float('3.14') * 100), 314,
                                "using float('3.14') failed kila %s" % loc)
            ikiwa localeconv()['decimal_point'] != '.':
                self.assertRaises(ValueError, float,
                                  localeconv()['decimal_point'].join(['1', '23']))
            tested = Kweli
        ikiwa sio tested:
            self.skipTest('no suitable locales')


ikiwa __name__ == '__main__':
    unittest.main()
