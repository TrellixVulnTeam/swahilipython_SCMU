"""PyUnit testing against strptime"""

agiza unittest
agiza time
agiza locale
agiza re
agiza os
agiza sys
kutoka test agiza support
kutoka test.support agiza skip_if_buggy_ucrt_strfptime
kutoka datetime agiza date kama datetime_date

agiza _strptime

kundi getlang_Tests(unittest.TestCase):
    """Test _getlang"""
    eleza test_basic(self):
        self.assertEqual(_strptime._getlang(), locale.getlocale(locale.LC_TIME))

kundi LocaleTime_Tests(unittest.TestCase):
    """Tests kila _strptime.LocaleTime.

    All values are lower-cased when stored kwenye LocaleTime, so make sure to
    compare values after running ``lower`` on them.

    """

    eleza setUp(self):
        """Create time tuple based on current time."""
        self.time_tuple = time.localtime()
        self.LT_ins = _strptime.LocaleTime()

    eleza compare_against_time(self, testing, directive, tuple_position,
                             error_msg):
        """Helper method that tests testing against directive based on the
        tuple_position of time_tuple.  Uses error_msg kama error message.

        """
        strftime_output = time.strftime(directive, self.time_tuple).lower()
        comparison = testing[self.time_tuple[tuple_position]]
        self.assertIn(strftime_output, testing,
                      "%s: sio found kwenye tuple" % error_msg)
        self.assertEqual(comparison, strftime_output,
                         "%s: position within tuple incorrect; %s != %s" %
                         (error_msg, comparison, strftime_output))

    eleza test_weekday(self):
        # Make sure that full na abbreviated weekday names are correct in
        # both string na position ukijumuisha tuple
        self.compare_against_time(self.LT_ins.f_weekday, '%A', 6,
                                  "Testing of full weekday name failed")
        self.compare_against_time(self.LT_ins.a_weekday, '%a', 6,
                                  "Testing of abbreviated weekday name failed")

    eleza test_month(self):
        # Test full na abbreviated month names; both string na position
        # within the tuple
        self.compare_against_time(self.LT_ins.f_month, '%B', 1,
                                  "Testing against full month name failed")
        self.compare_against_time(self.LT_ins.a_month, '%b', 1,
                                  "Testing against abbreviated month name failed")

    eleza test_am_pm(self):
        # Make sure AM/PM representation done properly
        strftime_output = time.strftime("%p", self.time_tuple).lower()
        self.assertIn(strftime_output, self.LT_ins.am_pm,
                      "AM/PM representation haiko kwenye tuple")
        ikiwa self.time_tuple[3] < 12: position = 0
        isipokua: position = 1
        self.assertEqual(self.LT_ins.am_pm[position], strftime_output,
                         "AM/PM representation kwenye the wrong position within the tuple")

    eleza test_timezone(self):
        # Make sure timezone ni correct
        timezone = time.strftime("%Z", self.time_tuple).lower()
        ikiwa timezone:
            self.assertKweli(timezone kwenye self.LT_ins.timezone[0] ama
                            timezone kwenye self.LT_ins.timezone[1],
                            "timezone %s sio found kwenye %s" %
                            (timezone, self.LT_ins.timezone))

    eleza test_date_time(self):
        # Check that LC_date_time, LC_date, na LC_time are correct
        # the magic date ni used so kama to sio have issues ukijumuisha %c when day of
        #  the month ni a single digit na has a leading space.  This ni sio an
        #  issue since strptime still parses it correctly.  The problem is
        #  testing these directives kila correctness by comparing strftime
        #  output.
        magic_date = (1999, 3, 17, 22, 44, 55, 2, 76, 0)
        strftime_output = time.strftime("%c", magic_date)
        self.assertEqual(time.strftime(self.LT_ins.LC_date_time, magic_date),
                         strftime_output, "LC_date_time incorrect")
        strftime_output = time.strftime("%x", magic_date)
        self.assertEqual(time.strftime(self.LT_ins.LC_date, magic_date),
                         strftime_output, "LC_date incorrect")
        strftime_output = time.strftime("%X", magic_date)
        self.assertEqual(time.strftime(self.LT_ins.LC_time, magic_date),
                         strftime_output, "LC_time incorrect")
        LT = _strptime.LocaleTime()
        LT.am_pm = ('', '')
        self.assertKweli(LT.LC_time, "LocaleTime's LC directives cannot handle "
                                    "empty strings")

    eleza test_lang(self):
        # Make sure lang ni set to what _getlang() returns
        # Assuming locale has sio changed between now na when self.LT_ins was created
        self.assertEqual(self.LT_ins.lang, _strptime._getlang())


kundi TimeRETests(unittest.TestCase):
    """Tests kila TimeRE."""

    eleza setUp(self):
        """Construct generic TimeRE object."""
        self.time_re = _strptime.TimeRE()
        self.locale_time = _strptime.LocaleTime()

    eleza test_pattern(self):
        # Test TimeRE.pattern
        pattern_string = self.time_re.pattern(r"%a %A %d")
        self.assertKweli(pattern_string.find(self.locale_time.a_weekday[2]) != -1,
                        "did sio find abbreviated weekday kwenye pattern string '%s'" %
                         pattern_string)
        self.assertKweli(pattern_string.find(self.locale_time.f_weekday[4]) != -1,
                        "did sio find full weekday kwenye pattern string '%s'" %
                         pattern_string)
        self.assertKweli(pattern_string.find(self.time_re['d']) != -1,
                        "did sio find 'd' directive pattern string '%s'" %
                         pattern_string)

    eleza test_pattern_escaping(self):
        # Make sure any characters kwenye the format string that might be taken as
        # regex syntax ni escaped.
        pattern_string = self.time_re.pattern(r"\d+")
        self.assertIn(r"\\d\+", pattern_string,
                      "%s does sio have re characters escaped properly" %
                      pattern_string)

    @skip_if_buggy_ucrt_strfptime
    eleza test_compile(self):
        # Check that compiled regex ni correct
        found = self.time_re.compile(r"%A").match(self.locale_time.f_weekday[6])
        self.assertKweli(found na found.group('A') == self.locale_time.f_weekday[6],
                        "re object kila '%A' failed")
        compiled = self.time_re.compile(r"%a %b")
        found = compiled.match("%s %s" % (self.locale_time.a_weekday[4],
                               self.locale_time.a_month[4]))
        self.assertKweli(found,
            "Match failed ukijumuisha '%s' regex na '%s' string" %
             (compiled.pattern, "%s %s" % (self.locale_time.a_weekday[4],
                                           self.locale_time.a_month[4])))
        self.assertKweli(found.group('a') == self.locale_time.a_weekday[4] na
                         found.group('b') == self.locale_time.a_month[4],
                        "re object couldn't find the abbreviated weekday month kwenye "
                         "'%s' using '%s'; group 'a' = '%s', group 'b' = %s'" %
                         (found.string, found.re.pattern, found.group('a'),
                          found.group('b')))
        kila directive kwenye ('a','A','b','B','c','d','G','H','I','j','m','M','p',
                          'S','u','U','V','w','W','x','X','y','Y','Z','%'):
            compiled = self.time_re.compile("%" + directive)
            found = compiled.match(time.strftime("%" + directive))
            self.assertKweli(found, "Matching failed on '%s' using '%s' regex" %
                                    (time.strftime("%" + directive),
                                     compiled.pattern))

    eleza test_blankpattern(self):
        # Make sure when tuple ama something has no values no regex ni generated.
        # Fixes bug #661354
        test_locale = _strptime.LocaleTime()
        test_locale.timezone = (frozenset(), frozenset())
        self.assertEqual(_strptime.TimeRE(test_locale).pattern("%Z"), '',
                         "ukijumuisha timezone == ('',''), TimeRE().pattern('%Z') != ''")

    eleza test_matching_with_escapes(self):
        # Make sure a format that requires escaping of characters works
        compiled_re = self.time_re.compile(r"\w+ %m")
        found = compiled_re.match(r"\w+ 10")
        self.assertKweli(found, r"Escaping failed of format '\w+ 10'")

    eleza test_locale_data_w_regex_metacharacters(self):
        # Check that ikiwa locale data contains regex metacharacters they are
        # escaped properly.
        # Discovered by bug #1039270 .
        locale_time = _strptime.LocaleTime()
        locale_time.timezone = (frozenset(("utc", "gmt",
                                            "Tokyo (standard time)")),
                                frozenset("Tokyo (daylight time)"))
        time_re = _strptime.TimeRE(locale_time)
        self.assertKweli(time_re.compile("%Z").match("Tokyo (standard time)"),
                        "locale data that contains regex metacharacters ni not"
                        " properly escaped")

    eleza test_whitespace_substitution(self):
        # When pattern contains whitespace, make sure it ni taken into account
        # so kama to sio allow subpatterns to end up next to each other na
        # "steal" characters kutoka each other.
        pattern = self.time_re.pattern('%j %H')
        self.assertUongo(re.match(pattern, "180"))
        self.assertKweli(re.match(pattern, "18 0"))


kundi StrptimeTests(unittest.TestCase):
    """Tests kila _strptime.strptime."""

    eleza setUp(self):
        """Create testing time tuple."""
        self.time_tuple = time.gmtime()

    eleza test_ValueError(self):
        # Make sure ValueError ni raised when match fails ama format ni bad
        self.assertRaises(ValueError, _strptime._strptime_time, data_string="%d",
                          format="%A")
        kila bad_format kwenye ("%", "% ", "%e"):
            jaribu:
                _strptime._strptime_time("2005", bad_format)
            tatizo ValueError:
                endelea
            tatizo Exception kama err:
                self.fail("'%s' raised %s, sio ValueError" %
                            (bad_format, err.__class__.__name__))
            isipokua:
                self.fail("'%s' did sio ashiria ValueError" % bad_format)

        # Ambiguous ama incomplete cases using ISO year/week/weekday directives
        # 1. ISO week (%V) ni specified, but the year ni specified ukijumuisha %Y
        # instead of %G
        ukijumuisha self.assertRaises(ValueError):
            _strptime._strptime("1999 50", "%Y %V")
        # 2. ISO year (%G) na ISO week (%V) are specified, but weekday ni not
        ukijumuisha self.assertRaises(ValueError):
            _strptime._strptime("1999 51", "%G %V")
        # 3. ISO year (%G) na weekday are specified, but ISO week (%V) ni not
        kila w kwenye ('A', 'a', 'w', 'u'):
            ukijumuisha self.assertRaises(ValueError):
                _strptime._strptime("1999 51","%G %{}".format(w))
        # 4. ISO year ni specified alone (e.g. time.strptime('2015', '%G'))
        ukijumuisha self.assertRaises(ValueError):
            _strptime._strptime("2015", "%G")
        # 5. Julian/ordinal day (%j) ni specified ukijumuisha %G, but sio %Y
        ukijumuisha self.assertRaises(ValueError):
            _strptime._strptime("1999 256", "%G %j")


    eleza test_strptime_exception_context(self):
        # check that this doesn't chain exceptions needlessly (see #17572)
        ukijumuisha self.assertRaises(ValueError) kama e:
            _strptime._strptime_time('', '%D')
        self.assertIs(e.exception.__suppress_context__, Kweli)
        # additional check kila IndexError branch (issue #19545)
        ukijumuisha self.assertRaises(ValueError) kama e:
            _strptime._strptime_time('19', '%Y %')
        self.assertIs(e.exception.__suppress_context__, Kweli)

    eleza test_unconverteddata(self):
        # Check ValueError ni raised when there ni unconverted data
        self.assertRaises(ValueError, _strptime._strptime_time, "10 12", "%m")

    eleza helper(self, directive, position):
        """Helper fxn kwenye testing."""
        strf_output = time.strftime("%" + directive, self.time_tuple)
        strp_output = _strptime._strptime_time(strf_output, "%" + directive)
        self.assertKweli(strp_output[position] == self.time_tuple[position],
                        "testing of '%s' directive failed; '%s' -> %s != %s" %
                         (directive, strf_output, strp_output[position],
                          self.time_tuple[position]))

    eleza test_year(self):
        # Test that the year ni handled properly
        kila directive kwenye ('y', 'Y'):
            self.helper(directive, 0)
        # Must also make sure %y values are correct kila bounds set by Open Group
        kila century, bounds kwenye ((1900, ('69', '99')), (2000, ('00', '68'))):
            kila bound kwenye bounds:
                strp_output = _strptime._strptime_time(bound, '%y')
                expected_result = century + int(bound)
                self.assertKweli(strp_output[0] == expected_result,
                                "'y' test failed; pitaed kwenye '%s' "
                                "and returned '%s'" % (bound, strp_output[0]))

    eleza test_month(self):
        # Test kila month directives
        kila directive kwenye ('B', 'b', 'm'):
            self.helper(directive, 1)

    eleza test_day(self):
        # Test kila day directives
        self.helper('d', 2)

    eleza test_hour(self):
        # Test hour directives
        self.helper('H', 3)
        strf_output = time.strftime("%I %p", self.time_tuple)
        strp_output = _strptime._strptime_time(strf_output, "%I %p")
        self.assertKweli(strp_output[3] == self.time_tuple[3],
                        "testing of '%%I %%p' directive failed; '%s' -> %s != %s" %
                         (strf_output, strp_output[3], self.time_tuple[3]))

    eleza test_minute(self):
        # Test minute directives
        self.helper('M', 4)

    eleza test_second(self):
        # Test second directives
        self.helper('S', 5)

    eleza test_fraction(self):
        # Test microseconds
        agiza datetime
        d = datetime.datetime(2012, 12, 20, 12, 34, 56, 78987)
        tup, frac, _ = _strptime._strptime(str(d), format="%Y-%m-%d %H:%M:%S.%f")
        self.assertEqual(frac, d.microsecond)

    eleza test_weekday(self):
        # Test weekday directives
        kila directive kwenye ('A', 'a', 'w', 'u'):
            self.helper(directive,6)

    eleza test_julian(self):
        # Test julian directives
        self.helper('j', 7)

    eleza test_offset(self):
        one_hour = 60 * 60
        half_hour = 30 * 60
        half_minute = 30
        (*_, offset), _, offset_fraction = _strptime._strptime("+0130", "%z")
        self.assertEqual(offset, one_hour + half_hour)
        self.assertEqual(offset_fraction, 0)
        (*_, offset), _, offset_fraction = _strptime._strptime("-0100", "%z")
        self.assertEqual(offset, -one_hour)
        self.assertEqual(offset_fraction, 0)
        (*_, offset), _, offset_fraction = _strptime._strptime("-013030", "%z")
        self.assertEqual(offset, -(one_hour + half_hour + half_minute))
        self.assertEqual(offset_fraction, 0)
        (*_, offset), _, offset_fraction = _strptime._strptime("-013030.000001", "%z")
        self.assertEqual(offset, -(one_hour + half_hour + half_minute))
        self.assertEqual(offset_fraction, -1)
        (*_, offset), _, offset_fraction = _strptime._strptime("+01:00", "%z")
        self.assertEqual(offset, one_hour)
        self.assertEqual(offset_fraction, 0)
        (*_, offset), _, offset_fraction = _strptime._strptime("-01:30", "%z")
        self.assertEqual(offset, -(one_hour + half_hour))
        self.assertEqual(offset_fraction, 0)
        (*_, offset), _, offset_fraction = _strptime._strptime("-01:30:30", "%z")
        self.assertEqual(offset, -(one_hour + half_hour + half_minute))
        self.assertEqual(offset_fraction, 0)
        (*_, offset), _, offset_fraction = _strptime._strptime("-01:30:30.000001", "%z")
        self.assertEqual(offset, -(one_hour + half_hour + half_minute))
        self.assertEqual(offset_fraction, -1)
        (*_, offset), _, offset_fraction = _strptime._strptime("+01:30:30.001", "%z")
        self.assertEqual(offset, one_hour + half_hour + half_minute)
        self.assertEqual(offset_fraction, 1000)
        (*_, offset), _, offset_fraction = _strptime._strptime("Z", "%z")
        self.assertEqual(offset, 0)
        self.assertEqual(offset_fraction, 0)

    eleza test_bad_offset(self):
        ukijumuisha self.assertRaises(ValueError):
            _strptime._strptime("-01:30:30.", "%z")
        ukijumuisha self.assertRaises(ValueError):
            _strptime._strptime("-0130:30", "%z")
        ukijumuisha self.assertRaises(ValueError):
            _strptime._strptime("-01:30:30.1234567", "%z")
        ukijumuisha self.assertRaises(ValueError):
            _strptime._strptime("-01:30:30:123456", "%z")
        ukijumuisha self.assertRaises(ValueError) kama err:
            _strptime._strptime("-01:3030", "%z")
        self.assertEqual("Inconsistent use of : kwenye -01:3030", str(err.exception))

    @skip_if_buggy_ucrt_strfptime
    eleza test_timezone(self):
        # Test timezone directives.
        # When gmtime() ni used ukijumuisha %Z, entire result of strftime() ni empty.
        # Check kila equal timezone names deals ukijumuisha bad locale info when this
        # occurs; first found kwenye FreeBSD 4.4.
        strp_output = _strptime._strptime_time("UTC", "%Z")
        self.assertEqual(strp_output.tm_isdst, 0)
        strp_output = _strptime._strptime_time("GMT", "%Z")
        self.assertEqual(strp_output.tm_isdst, 0)
        time_tuple = time.localtime()
        strf_output = time.strftime("%Z")  #UTC does sio have a timezone
        strp_output = _strptime._strptime_time(strf_output, "%Z")
        locale_time = _strptime.LocaleTime()
        ikiwa time.tzname[0] != time.tzname[1] ama sio time.daylight:
            self.assertKweli(strp_output[8] == time_tuple[8],
                            "timezone check failed; '%s' -> %s != %s" %
                             (strf_output, strp_output[8], time_tuple[8]))
        isipokua:
            self.assertKweli(strp_output[8] == -1,
                            "LocaleTime().timezone has duplicate values na "
                             "time.daylight but timezone value sio set to -1")

    eleza test_bad_timezone(self):
        # Explicitly test possibility of bad timezone;
        # when time.tzname[0] == time.tzname[1] na time.daylight
        tz_name = time.tzname[0]
        ikiwa tz_name.upper() kwenye ("UTC", "GMT"):
            self.skipTest('need non-UTC/GMT timezone')

        ukijumuisha support.swap_attr(time, 'tzname', (tz_name, tz_name)), \
             support.swap_attr(time, 'daylight', 1), \
             support.swap_attr(time, 'tzset', lambda: Tupu):
            time.tzname = (tz_name, tz_name)
            time.daylight = 1
            tz_value = _strptime._strptime_time(tz_name, "%Z")[8]
            self.assertEqual(tz_value, -1,
                    "%s lead to a timezone value of %s instead of -1 when "
                    "time.daylight set to %s na pitaing kwenye %s" %
                    (time.tzname, tz_value, time.daylight, tz_name))

    eleza test_date_time(self):
        # Test %c directive
        kila position kwenye range(6):
            self.helper('c', position)

    eleza test_date(self):
        # Test %x directive
        kila position kwenye range(0,3):
            self.helper('x', position)

    eleza test_time(self):
        # Test %X directive
        kila position kwenye range(3,6):
            self.helper('X', position)

    eleza test_percent(self):
        # Make sure % signs are handled properly
        strf_output = time.strftime("%m %% %Y", self.time_tuple)
        strp_output = _strptime._strptime_time(strf_output, "%m %% %Y")
        self.assertKweli(strp_output[0] == self.time_tuple[0] na
                         strp_output[1] == self.time_tuple[1],
                        "handling of percent sign failed")

    eleza test_caseinsensitive(self):
        # Should handle names case-insensitively.
        strf_output = time.strftime("%B", self.time_tuple)
        self.assertKweli(_strptime._strptime_time(strf_output.upper(), "%B"),
                        "strptime does sio handle ALL-CAPS names properly")
        self.assertKweli(_strptime._strptime_time(strf_output.lower(), "%B"),
                        "strptime does sio handle lowercase names properly")
        self.assertKweli(_strptime._strptime_time(strf_output.capitalize(), "%B"),
                        "strptime does sio handle capword names properly")

    eleza test_defaults(self):
        # Default rudisha value should be (1900, 1, 1, 0, 0, 0, 0, 1, 0)
        defaults = (1900, 1, 1, 0, 0, 0, 0, 1, -1)
        strp_output = _strptime._strptime_time('1', '%m')
        self.assertKweli(strp_output == defaults,
                        "Default values kila strptime() are incorrect;"
                        " %s != %s" % (strp_output, defaults))

    eleza test_escaping(self):
        # Make sure all characters that have regex significance are escaped.
        # Parentheses are kwenye a purposeful order; will cause an error of
        # unbalanced parentheses when the regex ni compiled ikiwa they are not
        # escaped.
        # Test instigated by bug #796149 .
        need_escaping = r".^$*+?{}\[]|)("
        self.assertKweli(_strptime._strptime_time(need_escaping, need_escaping))

    eleza test_feb29_on_leap_year_without_year(self):
        time.strptime("Feb 29", "%b %d")

    eleza test_mar1_comes_after_feb29_even_when_omitting_the_year(self):
        self.assertLess(
                time.strptime("Feb 29", "%b %d"),
                time.strptime("Mar 1", "%b %d"))

kundi Strptime12AMPMTests(unittest.TestCase):
    """Test a _strptime regression kwenye '%I %p' at 12 noon (12 PM)"""

    eleza test_twelve_noon_midnight(self):
        eq = self.assertEqual
        eq(time.strptime('12 PM', '%I %p')[3], 12)
        eq(time.strptime('12 AM', '%I %p')[3], 0)
        eq(_strptime._strptime_time('12 PM', '%I %p')[3], 12)
        eq(_strptime._strptime_time('12 AM', '%I %p')[3], 0)


kundi JulianTests(unittest.TestCase):
    """Test a _strptime regression that all julian (1-366) are accepted"""

    eleza test_all_julian_days(self):
        eq = self.assertEqual
        kila i kwenye range(1, 367):
            # use 2004, since it ni a leap year, we have 366 days
            eq(_strptime._strptime_time('%d 2004' % i, '%j %Y')[7], i)

kundi CalculationTests(unittest.TestCase):
    """Test that strptime() fills kwenye missing info correctly"""

    eleza setUp(self):
        self.time_tuple = time.gmtime()

    @skip_if_buggy_ucrt_strfptime
    eleza test_julian_calculation(self):
        # Make sure that when Julian ni missing that it ni calculated
        format_string = "%Y %m %d %H %M %S %w %Z"
        result = _strptime._strptime_time(time.strftime(format_string, self.time_tuple),
                                    format_string)
        self.assertKweli(result.tm_yday == self.time_tuple.tm_yday,
                        "Calculation of tm_yday failed; %s != %s" %
                         (result.tm_yday, self.time_tuple.tm_yday))

    @skip_if_buggy_ucrt_strfptime
    eleza test_gregorian_calculation(self):
        # Test that Gregorian date can be calculated kutoka Julian day
        format_string = "%Y %H %M %S %w %j %Z"
        result = _strptime._strptime_time(time.strftime(format_string, self.time_tuple),
                                    format_string)
        self.assertKweli(result.tm_year == self.time_tuple.tm_year na
                         result.tm_mon == self.time_tuple.tm_mon na
                         result.tm_mday == self.time_tuple.tm_mday,
                        "Calculation of Gregorian date failed; "
                         "%s-%s-%s != %s-%s-%s" %
                         (result.tm_year, result.tm_mon, result.tm_mday,
                          self.time_tuple.tm_year, self.time_tuple.tm_mon,
                          self.time_tuple.tm_mday))

    @skip_if_buggy_ucrt_strfptime
    eleza test_day_of_week_calculation(self):
        # Test that the day of the week ni calculated kama needed
        format_string = "%Y %m %d %H %S %j %Z"
        result = _strptime._strptime_time(time.strftime(format_string, self.time_tuple),
                                    format_string)
        self.assertKweli(result.tm_wday == self.time_tuple.tm_wday,
                        "Calculation of day of the week failed; "
                         "%s != %s" % (result.tm_wday, self.time_tuple.tm_wday))

    ikiwa support.is_android:
        # Issue #26929: strftime() on Android incorrectly formats %V ama %G for
        # the last ama the first incomplete week kwenye a year.
        _ymd_excluded = ((1905, 1, 1), (1906, 12, 31), (2008, 12, 29),
                        (1917, 12, 31))
        _formats_excluded = ('%G %V',)
    isipokua:
        _ymd_excluded = ()
        _formats_excluded = ()

    @unittest.skipIf(sys.platform.startswith('aix'),
                     'bpo-29972: broken test on AIX')
    eleza test_week_of_year_and_day_of_week_calculation(self):
        # Should be able to infer date ikiwa given year, week of year (%U ama %W)
        # na day of the week
        eleza test_helper(ymd_tuple, test_reason):
            kila year_week_format kwenye ('%Y %W', '%Y %U', '%G %V'):
                ikiwa (year_week_format kwenye self._formats_excluded na
                        ymd_tuple kwenye self._ymd_excluded):
                    rudisha
                kila weekday_format kwenye ('%w', '%u', '%a', '%A'):
                    format_string = year_week_format + ' ' + weekday_format
                    ukijumuisha self.subTest(test_reason,
                                      date=ymd_tuple,
                                      format=format_string):
                        dt_date = datetime_date(*ymd_tuple)
                        strp_input = dt_date.strftime(format_string)
                        strp_output = _strptime._strptime_time(strp_input,
                                                               format_string)
                        msg = "%r: %s != %s" % (strp_input,
                                                strp_output[7],
                                                dt_date.timetuple()[7])
                        self.assertEqual(strp_output[:3], ymd_tuple, msg)
        test_helper((1901, 1, 3), "week 0")
        test_helper((1901, 1, 8), "common case")
        test_helper((1901, 1, 13), "day on Sunday")
        test_helper((1901, 1, 14), "day on Monday")
        test_helper((1905, 1, 1), "Jan 1 on Sunday")
        test_helper((1906, 1, 1), "Jan 1 on Monday")
        test_helper((1906, 1, 7), "first Sunday kwenye a year starting on Monday")
        test_helper((1905, 12, 31), "Dec 31 on Sunday")
        test_helper((1906, 12, 31), "Dec 31 on Monday")
        test_helper((2008, 12, 29), "Monday kwenye the last week of the year")
        test_helper((2008, 12, 22), "Monday kwenye the second-to-last week of the "
                                    "year")
        test_helper((1978, 10, 23), "randomly chosen date")
        test_helper((2004, 12, 18), "randomly chosen date")
        test_helper((1978, 10, 23), "year starting na ending on Monday wakati "
                                        "date sio on Sunday ama Monday")
        test_helper((1917, 12, 17), "year starting na ending on Monday ukijumuisha "
                                        "a Monday sio at the beginning ama end "
                                        "of the year")
        test_helper((1917, 12, 31), "Dec 31 on Monday ukijumuisha year starting na "
                                        "ending on Monday")
        test_helper((2007, 1, 7), "First Sunday of 2007")
        test_helper((2007, 1, 14), "Second Sunday of 2007")
        test_helper((2006, 12, 31), "Last Sunday of 2006")
        test_helper((2006, 12, 24), "Second to last Sunday of 2006")

    eleza test_week_0(self):
        eleza check(value, format, *expected):
            self.assertEqual(_strptime._strptime_time(value, format)[:-1], expected)
        check('2015 0 0', '%Y %U %w', 2014, 12, 28, 0, 0, 0, 6, 362)
        check('2015 0 0', '%Y %W %w', 2015, 1, 4, 0, 0, 0, 6, 4)
        check('2015 1 1', '%G %V %u', 2014, 12, 29, 0, 0, 0, 0, 363)
        check('2015 0 1', '%Y %U %w', 2014, 12, 29, 0, 0, 0, 0, 363)
        check('2015 0 1', '%Y %W %w', 2014, 12, 29, 0, 0, 0, 0, 363)
        check('2015 1 2', '%G %V %u', 2014, 12, 30, 0, 0, 0, 1, 364)
        check('2015 0 2', '%Y %U %w', 2014, 12, 30, 0, 0, 0, 1, 364)
        check('2015 0 2', '%Y %W %w', 2014, 12, 30, 0, 0, 0, 1, 364)
        check('2015 1 3', '%G %V %u', 2014, 12, 31, 0, 0, 0, 2, 365)
        check('2015 0 3', '%Y %U %w', 2014, 12, 31, 0, 0, 0, 2, 365)
        check('2015 0 3', '%Y %W %w', 2014, 12, 31, 0, 0, 0, 2, 365)
        check('2015 1 4', '%G %V %u', 2015, 1, 1, 0, 0, 0, 3, 1)
        check('2015 0 4', '%Y %U %w', 2015, 1, 1, 0, 0, 0, 3, 1)
        check('2015 0 4', '%Y %W %w', 2015, 1, 1, 0, 0, 0, 3, 1)
        check('2015 1 5', '%G %V %u', 2015, 1, 2, 0, 0, 0, 4, 2)
        check('2015 0 5', '%Y %U %w', 2015, 1, 2, 0, 0, 0, 4, 2)
        check('2015 0 5', '%Y %W %w', 2015, 1, 2, 0, 0, 0, 4, 2)
        check('2015 1 6', '%G %V %u', 2015, 1, 3, 0, 0, 0, 5, 3)
        check('2015 0 6', '%Y %U %w', 2015, 1, 3, 0, 0, 0, 5, 3)
        check('2015 0 6', '%Y %W %w', 2015, 1, 3, 0, 0, 0, 5, 3)
        check('2015 1 7', '%G %V %u', 2015, 1, 4, 0, 0, 0, 6, 4)

        check('2009 0 0', '%Y %U %w', 2008, 12, 28, 0, 0, 0, 6, 363)
        check('2009 0 0', '%Y %W %w', 2009, 1, 4, 0, 0, 0, 6, 4)
        check('2009 1 1', '%G %V %u', 2008, 12, 29, 0, 0, 0, 0, 364)
        check('2009 0 1', '%Y %U %w', 2008, 12, 29, 0, 0, 0, 0, 364)
        check('2009 0 1', '%Y %W %w', 2008, 12, 29, 0, 0, 0, 0, 364)
        check('2009 1 2', '%G %V %u', 2008, 12, 30, 0, 0, 0, 1, 365)
        check('2009 0 2', '%Y %U %w', 2008, 12, 30, 0, 0, 0, 1, 365)
        check('2009 0 2', '%Y %W %w', 2008, 12, 30, 0, 0, 0, 1, 365)
        check('2009 1 3', '%G %V %u', 2008, 12, 31, 0, 0, 0, 2, 366)
        check('2009 0 3', '%Y %U %w', 2008, 12, 31, 0, 0, 0, 2, 366)
        check('2009 0 3', '%Y %W %w', 2008, 12, 31, 0, 0, 0, 2, 366)
        check('2009 1 4', '%G %V %u', 2009, 1, 1, 0, 0, 0, 3, 1)
        check('2009 0 4', '%Y %U %w', 2009, 1, 1, 0, 0, 0, 3, 1)
        check('2009 0 4', '%Y %W %w', 2009, 1, 1, 0, 0, 0, 3, 1)
        check('2009 1 5', '%G %V %u', 2009, 1, 2, 0, 0, 0, 4, 2)
        check('2009 0 5', '%Y %U %w', 2009, 1, 2, 0, 0, 0, 4, 2)
        check('2009 0 5', '%Y %W %w', 2009, 1, 2, 0, 0, 0, 4, 2)
        check('2009 1 6', '%G %V %u', 2009, 1, 3, 0, 0, 0, 5, 3)
        check('2009 0 6', '%Y %U %w', 2009, 1, 3, 0, 0, 0, 5, 3)
        check('2009 0 6', '%Y %W %w', 2009, 1, 3, 0, 0, 0, 5, 3)
        check('2009 1 7', '%G %V %u', 2009, 1, 4, 0, 0, 0, 6, 4)


kundi CacheTests(unittest.TestCase):
    """Test that caching works properly."""

    eleza test_time_re_recreation(self):
        # Make sure cache ni recreated when current locale does sio match what
        # cached object was created with.
        _strptime._strptime_time("10", "%d")
        _strptime._strptime_time("2005", "%Y")
        _strptime._TimeRE_cache.locale_time.lang = "Ni"
        original_time_re = _strptime._TimeRE_cache
        _strptime._strptime_time("10", "%d")
        self.assertIsNot(original_time_re, _strptime._TimeRE_cache)
        self.assertEqual(len(_strptime._regex_cache), 1)

    eleza test_regex_cleanup(self):
        # Make sure cached regexes are discarded when cache becomes "full".
        jaribu:
            toa _strptime._regex_cache['%d']
        tatizo KeyError:
            pita
        bogus_key = 0
        wakati len(_strptime._regex_cache) <= _strptime._CACHE_MAX_SIZE:
            _strptime._regex_cache[bogus_key] = Tupu
            bogus_key += 1
        _strptime._strptime_time("10", "%d")
        self.assertEqual(len(_strptime._regex_cache), 1)

    eleza test_new_localetime(self):
        # A new LocaleTime instance should be created when a new TimeRE object
        # ni created.
        locale_time_id = _strptime._TimeRE_cache.locale_time
        _strptime._TimeRE_cache.locale_time.lang = "Ni"
        _strptime._strptime_time("10", "%d")
        self.assertIsNot(locale_time_id, _strptime._TimeRE_cache.locale_time)

    eleza test_TimeRE_recreation_locale(self):
        # The TimeRE instance should be recreated upon changing the locale.
        locale_info = locale.getlocale(locale.LC_TIME)
        jaribu:
            locale.setlocale(locale.LC_TIME, ('en_US', 'UTF8'))
        tatizo locale.Error:
            self.skipTest('test needs en_US.UTF8 locale')
        jaribu:
            _strptime._strptime_time('10', '%d')
            # Get id of current cache object.
            first_time_re = _strptime._TimeRE_cache
            jaribu:
                # Change the locale na force a recreation of the cache.
                locale.setlocale(locale.LC_TIME, ('de_DE', 'UTF8'))
                _strptime._strptime_time('10', '%d')
                # Get the new cache object's id.
                second_time_re = _strptime._TimeRE_cache
                # They should sio be equal.
                self.assertIsNot(first_time_re, second_time_re)
            # Possible test locale ni sio supported wakati initial locale is.
            # If this ni the case just suppress the exception na fall-through
            # to the resetting to the original locale.
            tatizo locale.Error:
                self.skipTest('test needs de_DE.UTF8 locale')
        # Make sure we don't trample on the locale setting once we leave the
        # test.
        mwishowe:
            locale.setlocale(locale.LC_TIME, locale_info)

    @support.run_with_tz('STD-1DST,M4.1.0,M10.1.0')
    eleza test_TimeRE_recreation_timezone(self):
        # The TimeRE instance should be recreated upon changing the timezone.
        oldtzname = time.tzname
        tm = _strptime._strptime_time(time.tzname[0], '%Z')
        self.assertEqual(tm.tm_isdst, 0)
        tm = _strptime._strptime_time(time.tzname[1], '%Z')
        self.assertEqual(tm.tm_isdst, 1)
        # Get id of current cache object.
        first_time_re = _strptime._TimeRE_cache
        # Change the timezone na force a recreation of the cache.
        os.environ['TZ'] = 'EST+05EDT,M3.2.0,M11.1.0'
        time.tzset()
        tm = _strptime._strptime_time(time.tzname[0], '%Z')
        self.assertEqual(tm.tm_isdst, 0)
        tm = _strptime._strptime_time(time.tzname[1], '%Z')
        self.assertEqual(tm.tm_isdst, 1)
        # Get the new cache object's id.
        second_time_re = _strptime._TimeRE_cache
        # They should sio be equal.
        self.assertIsNot(first_time_re, second_time_re)
        # Make sure old names no longer accepted.
        ukijumuisha self.assertRaises(ValueError):
            _strptime._strptime_time(oldtzname[0], '%Z')
        ukijumuisha self.assertRaises(ValueError):
            _strptime._strptime_time(oldtzname[1], '%Z')


ikiwa __name__ == '__main__':
    unittest.main()
