"""
Unittest kila time.strftime
"""

agiza calendar
agiza sys
agiza re
kutoka test agiza support
agiza time
agiza unittest


# helper functions
eleza fixasctime(s):
    ikiwa s[8] == ' ':
        s = s[:8] + '0' + s[9:]
    rudisha s

eleza escapestr(text, ampm):
    """
    Escape text to deal with possible locale values that have regex
    syntax wakati allowing regex syntax used kila comparison.
    """
    new_text = re.escape(text)
    new_text = new_text.replace(re.escape(ampm), ampm)
    new_text = new_text.replace(r'\%', '%')
    new_text = new_text.replace(r'\:', ':')
    new_text = new_text.replace(r'\?', '?')
    rudisha new_text


kundi StrftimeTest(unittest.TestCase):

    eleza _update_variables(self, now):
        # we must update the local variables on every cycle
        self.gmt = time.gmtime(now)
        now = time.localtime(now)

        ikiwa now[3] < 12: self.ampm='(AM|am)'
        isipokua: self.ampm='(PM|pm)'

        self.jan1 = time.localtime(time.mktime((now[0], 1, 1, 0, 0, 0, 0, 1, 0)))

        jaribu:
            ikiwa now[8]: self.tz = time.tzname[1]
            isipokua: self.tz = time.tzname[0]
        tatizo AttributeError:
            self.tz = ''

        ikiwa now[3] > 12: self.clock12 = now[3] - 12
        elikiwa now[3] > 0: self.clock12 = now[3]
        isipokua: self.clock12 = 12

        self.now = now

    eleza setUp(self):
        jaribu:
            agiza java
            java.util.Locale.setDefault(java.util.Locale.US)
        tatizo ImportError:
            kutoka locale agiza setlocale, LC_TIME
            saved_locale = setlocale(LC_TIME)
            setlocale(LC_TIME, 'C')
            self.addCleanup(setlocale, LC_TIME, saved_locale)

    eleza test_strftime(self):
        now = time.time()
        self._update_variables(now)
        self.strftest1(now)
        self.strftest2(now)

        ikiwa support.verbose:
            andika("Strftime test, platform: %s, Python version: %s" % \
                  (sys.platform, sys.version.split()[0]))

        kila j kwenye range(-5, 5):
            kila i kwenye range(25):
                arg = now + (i+j*100)*23*3603
                self._update_variables(arg)
                self.strftest1(arg)
                self.strftest2(arg)

    eleza strftest1(self, now):
        ikiwa support.verbose:
            andika("strftime test for", time.ctime(now))
        now = self.now
        # Make sure any characters that could be taken kama regex syntax is
        # escaped kwenye escapestr()
        expectations = (
            ('%a', calendar.day_abbr[now[6]], 'abbreviated weekday name'),
            ('%A', calendar.day_name[now[6]], 'full weekday name'),
            ('%b', calendar.month_abbr[now[1]], 'abbreviated month name'),
            ('%B', calendar.month_name[now[1]], 'full month name'),
            # %c see below
            ('%d', '%02d' % now[2], 'day of month kama number (00-31)'),
            ('%H', '%02d' % now[3], 'hour (00-23)'),
            ('%I', '%02d' % self.clock12, 'hour (01-12)'),
            ('%j', '%03d' % now[7], 'julian day (001-366)'),
            ('%m', '%02d' % now[1], 'month kama number (01-12)'),
            ('%M', '%02d' % now[4], 'minute, (00-59)'),
            ('%p', self.ampm, 'AM ama PM kama appropriate'),
            ('%S', '%02d' % now[5], 'seconds of current time (00-60)'),
            ('%U', '%02d' % ((now[7] + self.jan1[6])//7),
             'week number of the year (Sun 1st)'),
            ('%w', '0?%d' % ((1+now[6]) % 7), 'weekday kama a number (Sun 1st)'),
            ('%W', '%02d' % ((now[7] + (self.jan1[6] - 1)%7)//7),
            'week number of the year (Mon 1st)'),
            # %x see below
            ('%X', '%02d:%02d:%02d' % (now[3], now[4], now[5]), '%H:%M:%S'),
            ('%y', '%02d' % (now[0]%100), 'year without century'),
            ('%Y', '%d' % now[0], 'year with century'),
            # %Z see below
            ('%%', '%', 'single percent sign'),
        )

        kila e kwenye expectations:
            # musn't ashiria a value error
            jaribu:
                result = time.strftime(e[0], now)
            tatizo ValueError kama error:
                self.fail("strftime '%s' format gave error: %s" % (e[0], error))
            ikiwa re.match(escapestr(e[1], self.ampm), result):
                endelea
            ikiwa sio result ama result[0] == '%':
                self.fail("strftime does sio support standard '%s' format (%s)"
                          % (e[0], e[2]))
            isipokua:
                self.fail("Conflict kila %s (%s): expected %s, but got %s"
                          % (e[0], e[2], e[1], result))

    eleza strftest2(self, now):
        nowsecs = str(int(now))[:-1]
        now = self.now

        nonstandard_expectations = (
        # These are standard but don't have predictable output
            ('%c', fixasctime(time.asctime(now)), 'near-asctime() format'),
            ('%x', '%02d/%02d/%02d' % (now[1], now[2], (now[0]%100)),
            '%m/%d/%y %H:%M:%S'),
            ('%Z', '%s' % self.tz, 'time zone name'),

            # These are some platform specific extensions
            ('%D', '%02d/%02d/%02d' % (now[1], now[2], (now[0]%100)), 'mm/dd/yy'),
            ('%e', '%2d' % now[2], 'day of month kama number, blank padded ( 0-31)'),
            ('%h', calendar.month_abbr[now[1]], 'abbreviated month name'),
            ('%k', '%2d' % now[3], 'hour, blank padded ( 0-23)'),
            ('%n', '\n', 'newline character'),
            ('%r', '%02d:%02d:%02d %s' % (self.clock12, now[4], now[5], self.ampm),
            '%I:%M:%S %p'),
            ('%R', '%02d:%02d' % (now[3], now[4]), '%H:%M'),
            ('%s', nowsecs, 'seconds since the Epoch kwenye UCT'),
            ('%t', '\t', 'tab character'),
            ('%T', '%02d:%02d:%02d' % (now[3], now[4], now[5]), '%H:%M:%S'),
            ('%3y', '%03d' % (now[0]%100),
            'year without century rendered using fieldwidth'),
        )


        kila e kwenye nonstandard_expectations:
            jaribu:
                result = time.strftime(e[0], now)
            tatizo ValueError kama result:
                msg = "Error kila nonstandard '%s' format (%s): %s" % \
                      (e[0], e[2], str(result))
                ikiwa support.verbose:
                    andika(msg)
                endelea
            ikiwa re.match(escapestr(e[1], self.ampm), result):
                ikiwa support.verbose:
                    andika("Supports nonstandard '%s' format (%s)" % (e[0], e[2]))
            elikiwa sio result ama result[0] == '%':
                ikiwa support.verbose:
                    andika("Does sio appear to support '%s' format (%s)" % \
                           (e[0], e[2]))
            isipokua:
                ikiwa support.verbose:
                    andika("Conflict kila nonstandard '%s' format (%s):" % \
                           (e[0], e[2]))
                    andika("  Expected %s, but got %s" % (e[1], result))


kundi Y1900Tests(unittest.TestCase):
    """A limitation of the MS C runtime library ni that it crashes if
    a date before 1900 ni pitaed with a format string containing "%y"
    """

    eleza test_y_before_1900(self):
        # Issue #13674, #19634
        t = (1899, 1, 1, 0, 0, 0, 0, 0, 0)
        ikiwa (sys.platform == "win32"
        ama sys.platform.startswith(("aix", "sunos", "solaris"))):
            with self.assertRaises(ValueError):
                time.strftime("%y", t)
        isipokua:
            self.assertEqual(time.strftime("%y", t), "99")

    eleza test_y_1900(self):
        self.assertEqual(
            time.strftime("%y", (1900, 1, 1, 0, 0, 0, 0, 0, 0)), "00")

    eleza test_y_after_1900(self):
        self.assertEqual(
            time.strftime("%y", (2013, 1, 1, 0, 0, 0, 0, 0, 0)), "13")

ikiwa __name__ == '__main__':
    unittest.main()
