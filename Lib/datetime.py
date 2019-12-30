"""Concrete date/time na related types.

See http://www.iana.org/time-zones/repository/tz-link.html for
time zone na DST data sources.
"""

agiza time kama _time
agiza math kama _math
agiza sys

eleza _cmp(x, y):
    rudisha 0 ikiwa x == y isipokua 1 ikiwa x > y isipokua -1

MINYEAR = 1
MAXYEAR = 9999
_MAXORDINAL = 3652059  # date.max.toordinal()

# Utility functions, adapted kutoka Python's Demo/classes/Dates.py, which
# also assumes the current Gregorian calendar indefinitely extended in
# both directions.  Difference:  Dates.py calls January 1 of year 0 day
# number 1.  The code here calls January 1 of year 1 day number 1.  This is
# to match the definition of the "proleptic Gregorian" calendar kwenye Dershowitz
# na Reingold's "Calendrical Calculations", where it's the base calendar
# kila all computations.  See the book kila algorithms kila converting between
# proleptic Gregorian ordinals na many other calendar systems.

# -1 ni a placeholder kila indexing purposes.
_DAYS_IN_MONTH = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

_DAYS_BEFORE_MONTH = [-1]  # -1 ni a placeholder kila indexing purposes.
dbm = 0
kila dim kwenye _DAYS_IN_MONTH[1:]:
    _DAYS_BEFORE_MONTH.append(dbm)
    dbm += dim
toa dbm, dim

eleza _is_leap(year):
    "year -> 1 ikiwa leap year, isipokua 0."
    rudisha year % 4 == 0 na (year % 100 != 0 ama year % 400 == 0)

eleza _days_before_year(year):
    "year -> number of days before January 1st of year."
    y = year - 1
    rudisha y*365 + y//4 - y//100 + y//400

eleza _days_in_month(year, month):
    "year, month -> number of days kwenye that month kwenye that year."
    assert 1 <= month <= 12, month
    ikiwa month == 2 na _is_leap(year):
        rudisha 29
    rudisha _DAYS_IN_MONTH[month]

eleza _days_before_month(year, month):
    "year, month -> number of days kwenye year preceding first day of month."
    assert 1 <= month <= 12, 'month must be kwenye 1..12'
    rudisha _DAYS_BEFORE_MONTH[month] + (month > 2 na _is_leap(year))

eleza _ymd2ord(year, month, day):
    "year, month, day -> ordinal, considering 01-Jan-0001 kama day 1."
    assert 1 <= month <= 12, 'month must be kwenye 1..12'
    dim = _days_in_month(year, month)
    assert 1 <= day <= dim, ('day must be kwenye 1..%d' % dim)
    rudisha (_days_before_year(year) +
            _days_before_month(year, month) +
            day)

_DI400Y = _days_before_year(401)    # number of days kwenye 400 years
_DI100Y = _days_before_year(101)    #    "    "   "   " 100   "
_DI4Y   = _days_before_year(5)      #    "    "   "   "   4   "

# A 4-year cycle has an extra leap day over what we'd get kutoka pasting
# together 4 single years.
assert _DI4Y == 4 * 365 + 1

# Similarly, a 400-year cycle has an extra leap day over what we'd get from
# pasting together 4 100-year cycles.
assert _DI400Y == 4 * _DI100Y + 1

# OTOH, a 100-year cycle has one fewer leap day than we'd get from
# pasting together 25 4-year cycles.
assert _DI100Y == 25 * _DI4Y - 1

eleza _ord2ymd(n):
    "ordinal -> (year, month, day), considering 01-Jan-0001 kama day 1."

    # n ni a 1-based index, starting at 1-Jan-1.  The pattern of leap years
    # repeats exactly every 400 years.  The basic strategy ni to find the
    # closest 400-year boundary at ama before n, then work ukijumuisha the offset
    # kutoka that boundary to n.  Life ni much clearer ikiwa we subtract 1 from
    # n first -- then the values of n at 400-year boundaries are exactly
    # those divisible by _DI400Y:
    #
    #     D  M   Y            n              n-1
    #     -- --- ----        ----------     ----------------
    #     31 Dec -400        -_DI400Y       -_DI400Y -1
    #      1 Jan -399         -_DI400Y +1   -_DI400Y      400-year boundary
    #     ...
    #     30 Dec  000        -1             -2
    #     31 Dec  000         0             -1
    #      1 Jan  001         1              0            400-year boundary
    #      2 Jan  001         2              1
    #      3 Jan  001         3              2
    #     ...
    #     31 Dec  400         _DI400Y        _DI400Y -1
    #      1 Jan  401         _DI400Y +1     _DI400Y      400-year boundary
    n -= 1
    n400, n = divmod(n, _DI400Y)
    year = n400 * 400 + 1   # ..., -399, 1, 401, ...

    # Now n ni the (non-negative) offset, kwenye days, kutoka January 1 of year, to
    # the desired date.  Now compute how many 100-year cycles precede n.
    # Note that it's possible kila n100 to equal 4!  In that case 4 full
    # 100-year cycles precede the desired day, which implies the desired
    # day ni December 31 at the end of a 400-year cycle.
    n100, n = divmod(n, _DI100Y)

    # Now compute how many 4-year cycles precede it.
    n4, n = divmod(n, _DI4Y)

    # And now how many single years.  Again n1 can be 4, na again meaning
    # that the desired day ni December 31 at the end of the 4-year cycle.
    n1, n = divmod(n, 365)

    year += n100 * 100 + n4 * 4 + n1
    ikiwa n1 == 4 ama n100 == 4:
        assert n == 0
        rudisha year-1, 12, 31

    # Now the year ni correct, na n ni the offset kutoka January 1.  We find
    # the month via an estimate that's either exact ama one too large.
    leapyear = n1 == 3 na (n4 != 24 ama n100 == 3)
    assert leapyear == _is_leap(year)
    month = (n + 50) >> 5
    preceding = _DAYS_BEFORE_MONTH[month] + (month > 2 na leapyear)
    ikiwa preceding > n:  # estimate ni too large
        month -= 1
        preceding -= _DAYS_IN_MONTH[month] + (month == 2 na leapyear)
    n -= preceding
    assert 0 <= n < _days_in_month(year, month)

    # Now the year na month are correct, na n ni the offset kutoka the
    # start of that month:  we're done!
    rudisha year, month, n+1

# Month na day names.  For localized versions, see the calendar module.
_MONTHNAMES = [Tupu, "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
_DAYNAMES = [Tupu, "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


eleza _build_struct_time(y, m, d, hh, mm, ss, dstflag):
    wday = (_ymd2ord(y, m, d) + 6) % 7
    dnum = _days_before_month(y, m) + d
    rudisha _time.struct_time((y, m, d, hh, mm, ss, wday, dnum, dstflag))

eleza _format_time(hh, mm, ss, us, timespec='auto'):
    specs = {
        'hours': '{:02d}',
        'minutes': '{:02d}:{:02d}',
        'seconds': '{:02d}:{:02d}:{:02d}',
        'milliseconds': '{:02d}:{:02d}:{:02d}.{:03d}',
        'microseconds': '{:02d}:{:02d}:{:02d}.{:06d}'
    }

    ikiwa timespec == 'auto':
        # Skip trailing microseconds when us==0.
        timespec = 'microseconds' ikiwa us isipokua 'seconds'
    lasivyo timespec == 'milliseconds':
        us //= 1000
    jaribu:
        fmt = specs[timespec]
    tatizo KeyError:
        ashiria ValueError('Unknown timespec value')
    isipokua:
        rudisha fmt.format(hh, mm, ss, us)

eleza _format_offset(off):
    s = ''
    ikiwa off ni sio Tupu:
        ikiwa off.days < 0:
            sign = "-"
            off = -off
        isipokua:
            sign = "+"
        hh, mm = divmod(off, timedelta(hours=1))
        mm, ss = divmod(mm, timedelta(minutes=1))
        s += "%s%02d:%02d" % (sign, hh, mm)
        ikiwa ss ama ss.microseconds:
            s += ":%02d" % ss.seconds

            ikiwa ss.microseconds:
                s += '.%06d' % ss.microseconds
    rudisha s

# Correctly substitute kila %z na %Z escapes kwenye strftime formats.
eleza _wrap_strftime(object, format, timetuple):
    # Don't call utcoffset() ama tzname() unless actually needed.
    freplace = Tupu  # the string to use kila %f
    zreplace = Tupu  # the string to use kila %z
    Zreplace = Tupu  # the string to use kila %Z

    # Scan format kila %z na %Z escapes, replacing kama needed.
    newformat = []
    push = newformat.append
    i, n = 0, len(format)
    wakati i < n:
        ch = format[i]
        i += 1
        ikiwa ch == '%':
            ikiwa i < n:
                ch = format[i]
                i += 1
                ikiwa ch == 'f':
                    ikiwa freplace ni Tupu:
                        freplace = '%06d' % getattr(object,
                                                    'microsecond', 0)
                    newformat.append(freplace)
                lasivyo ch == 'z':
                    ikiwa zreplace ni Tupu:
                        zreplace = ""
                        ikiwa hasattr(object, "utcoffset"):
                            offset = object.utcoffset()
                            ikiwa offset ni sio Tupu:
                                sign = '+'
                                ikiwa offset.days < 0:
                                    offset = -offset
                                    sign = '-'
                                h, rest = divmod(offset, timedelta(hours=1))
                                m, rest = divmod(rest, timedelta(minutes=1))
                                s = rest.seconds
                                u = offset.microseconds
                                ikiwa u:
                                    zreplace = '%c%02d%02d%02d.%06d' % (sign, h, m, s, u)
                                lasivyo s:
                                    zreplace = '%c%02d%02d%02d' % (sign, h, m, s)
                                isipokua:
                                    zreplace = '%c%02d%02d' % (sign, h, m)
                    assert '%' haiko kwenye zreplace
                    newformat.append(zreplace)
                lasivyo ch == 'Z':
                    ikiwa Zreplace ni Tupu:
                        Zreplace = ""
                        ikiwa hasattr(object, "tzname"):
                            s = object.tzname()
                            ikiwa s ni sio Tupu:
                                # strftime ni going to have at this: escape %
                                Zreplace = s.replace('%', '%%')
                    newformat.append(Zreplace)
                isipokua:
                    push('%')
                    push(ch)
            isipokua:
                push('%')
        isipokua:
            push(ch)
    newformat = "".join(newformat)
    rudisha _time.strftime(newformat, timetuple)

# Helpers kila parsing the result of isoformat()
eleza _parse_isoformat_date(dtstr):
    # It ni assumed that this function will only be called ukijumuisha a
    # string of length exactly 10, na (though this ni sio used) ASCII-only
    year = int(dtstr[0:4])
    ikiwa dtstr[4] != '-':
        ashiria ValueError('Invalid date separator: %s' % dtstr[4])

    month = int(dtstr[5:7])

    ikiwa dtstr[7] != '-':
        ashiria ValueError('Invalid date separator')

    day = int(dtstr[8:10])

    rudisha [year, month, day]

eleza _parse_hh_mm_ss_ff(tstr):
    # Parses things of the form HH[:MM[:SS[.fff[fff]]]]
    len_str = len(tstr)

    time_comps = [0, 0, 0, 0]
    pos = 0
    kila comp kwenye range(0, 3):
        ikiwa (len_str - pos) < 2:
            ashiria ValueError('Incomplete time component')

        time_comps[comp] = int(tstr[pos:pos+2])

        pos += 2
        next_char = tstr[pos:pos+1]

        ikiwa sio next_char ama comp >= 2:
            koma

        ikiwa next_char != ':':
            ashiria ValueError('Invalid time separator: %c' % next_char)

        pos += 1

    ikiwa pos < len_str:
        ikiwa tstr[pos] != '.':
            ashiria ValueError('Invalid microsecond component')
        isipokua:
            pos += 1

            len_remainder = len_str - pos
            ikiwa len_remainder haiko kwenye (3, 6):
                ashiria ValueError('Invalid microsecond component')

            time_comps[3] = int(tstr[pos:])
            ikiwa len_remainder == 3:
                time_comps[3] *= 1000

    rudisha time_comps

eleza _parse_isoformat_time(tstr):
    # Format supported ni HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]]
    len_str = len(tstr)
    ikiwa len_str < 2:
        ashiria ValueError('Isoformat time too short')

    # This ni equivalent to re.search('[+-]', tstr), but faster
    tz_pos = (tstr.find('-') + 1 ama tstr.find('+') + 1)
    timestr = tstr[:tz_pos-1] ikiwa tz_pos > 0 isipokua tstr

    time_comps = _parse_hh_mm_ss_ff(timestr)

    tzi = Tupu
    ikiwa tz_pos > 0:
        tzstr = tstr[tz_pos:]

        # Valid time zone strings are:
        # HH:MM               len: 5
        # HH:MM:SS            len: 8
        # HH:MM:SS.ffffff     len: 15

        ikiwa len(tzstr) haiko kwenye (5, 8, 15):
            ashiria ValueError('Malformed time zone string')

        tz_comps = _parse_hh_mm_ss_ff(tzstr)
        ikiwa all(x == 0 kila x kwenye tz_comps):
            tzi = timezone.utc
        isipokua:
            tzsign = -1 ikiwa tstr[tz_pos - 1] == '-' isipokua 1

            td = timedelta(hours=tz_comps[0], minutes=tz_comps[1],
                           seconds=tz_comps[2], microseconds=tz_comps[3])

            tzi = timezone(tzsign * td)

    time_comps.append(tzi)

    rudisha time_comps


# Just ashiria TypeError ikiwa the arg isn't Tupu ama a string.
eleza _check_tzname(name):
    ikiwa name ni sio Tupu na sio isinstance(name, str):
        ashiria TypeError("tzinfo.tzname() must rudisha Tupu ama string, "
                        "not '%s'" % type(name))

# name ni the offset-producing method, "utcoffset" ama "dst".
# offset ni what it returned.
# If offset isn't Tupu ama timedelta, raises TypeError.
# If offset ni Tupu, returns Tupu.
# Else offset ni checked kila being kwenye range.
# If it is, its integer value ni returned.  Else ValueError ni raised.
eleza _check_utc_offset(name, offset):
    assert name kwenye ("utcoffset", "dst")
    ikiwa offset ni Tupu:
        return
    ikiwa sio isinstance(offset, timedelta):
        ashiria TypeError("tzinfo.%s() must rudisha Tupu "
                        "or timedelta, sio '%s'" % (name, type(offset)))
    ikiwa sio -timedelta(1) < offset < timedelta(1):
        ashiria ValueError("%s()=%s, must be strictly between "
                         "-timedelta(hours=24) na timedelta(hours=24)" %
                         (name, offset))

eleza _check_int_field(value):
    ikiwa isinstance(value, int):
        rudisha value
    ikiwa isinstance(value, float):
        ashiria TypeError('integer argument expected, got float')
    jaribu:
        value = value.__index__()
    tatizo AttributeError:
        pita
    isipokua:
        ikiwa sio isinstance(value, int):
            ashiria TypeError('__index__ returned non-int (type %s)' %
                            type(value).__name__)
        rudisha value
    orig = value
    jaribu:
        value = value.__int__()
    tatizo AttributeError:
        pita
    isipokua:
        ikiwa sio isinstance(value, int):
            ashiria TypeError('__int__ returned non-int (type %s)' %
                            type(value).__name__)
        agiza warnings
        warnings.warn("an integer ni required (got type %s)"  %
                      type(orig).__name__,
                      DeprecationWarning,
                      stacklevel=2)
        rudisha value
    ashiria TypeError('an integer ni required (got type %s)' %
                    type(value).__name__)

eleza _check_date_fields(year, month, day):
    year = _check_int_field(year)
    month = _check_int_field(month)
    day = _check_int_field(day)
    ikiwa sio MINYEAR <= year <= MAXYEAR:
        ashiria ValueError('year must be kwenye %d..%d' % (MINYEAR, MAXYEAR), year)
    ikiwa sio 1 <= month <= 12:
        ashiria ValueError('month must be kwenye 1..12', month)
    dim = _days_in_month(year, month)
    ikiwa sio 1 <= day <= dim:
        ashiria ValueError('day must be kwenye 1..%d' % dim, day)
    rudisha year, month, day

eleza _check_time_fields(hour, minute, second, microsecond, fold):
    hour = _check_int_field(hour)
    minute = _check_int_field(minute)
    second = _check_int_field(second)
    microsecond = _check_int_field(microsecond)
    ikiwa sio 0 <= hour <= 23:
        ashiria ValueError('hour must be kwenye 0..23', hour)
    ikiwa sio 0 <= minute <= 59:
        ashiria ValueError('minute must be kwenye 0..59', minute)
    ikiwa sio 0 <= second <= 59:
        ashiria ValueError('second must be kwenye 0..59', second)
    ikiwa sio 0 <= microsecond <= 999999:
        ashiria ValueError('microsecond must be kwenye 0..999999', microsecond)
    ikiwa fold haiko kwenye (0, 1):
        ashiria ValueError('fold must be either 0 ama 1', fold)
    rudisha hour, minute, second, microsecond, fold

eleza _check_tzinfo_arg(tz):
    ikiwa tz ni sio Tupu na sio isinstance(tz, tzinfo):
        ashiria TypeError("tzinfo argument must be Tupu ama of a tzinfo subclass")

eleza _cmperror(x, y):
    ashiria TypeError("can't compare '%s' to '%s'" % (
                    type(x).__name__, type(y).__name__))

eleza _divide_and_round(a, b):
    """divide a by b na round result to the nearest integer

    When the ratio ni exactly half-way between two integers,
    the even integer ni returned.
    """
    # Based on the reference implementation kila divmod_near
    # kwenye Objects/longobject.c.
    q, r = divmod(a, b)
    # round up ikiwa either r / b > 0.5, ama r / b == 0.5 na q ni odd.
    # The expression r / b > 0.5 ni equivalent to 2 * r > b ikiwa b is
    # positive, 2 * r < b ikiwa b negative.
    r *= 2
    greater_than_half = r > b ikiwa b > 0 isipokua r < b
    ikiwa greater_than_half ama r == b na q % 2 == 1:
        q += 1

    rudisha q


kundi timedelta:
    """Represent the difference between two datetime objects.

    Supported operators:

    - add, subtract timedelta
    - unary plus, minus, abs
    - compare to timedelta
    - multiply, divide by int

    In addition, datetime supports subtraction of two datetime objects
    returning a timedelta, na addition ama subtraction of a datetime
    na a timedelta giving a datetime.

    Representation: (days, seconds, microseconds).  Why?  Because I
    felt like it.
    """
    __slots__ = '_days', '_seconds', '_microseconds', '_hashcode'

    eleza __new__(cls, days=0, seconds=0, microseconds=0,
                milliseconds=0, minutes=0, hours=0, weeks=0):
        # Doing this efficiently na accurately kwenye C ni going to be difficult
        # na error-prone, due to ubiquitous overflow possibilities, na that
        # C double doesn't have enough bits of precision to represent
        # microseconds over 10K years faithfully.  The code here tries to make
        # explicit where go-fast assumptions can be relied on, kwenye order to
        # guide the C implementation; it's way more convoluted than speed-
        # ignoring auto-overflow-to-long idiomatic Python could be.

        # XXX Check that all inputs are ints ama floats.

        # Final values, all integer.
        # s na us fit kwenye 32-bit signed ints; d isn't bounded.
        d = s = us = 0

        # Normalize everything to days, seconds, microseconds.
        days += weeks*7
        seconds += minutes*60 + hours*3600
        microseconds += milliseconds*1000

        # Get rid of all fractions, na normalize s na us.
        # Take a deep breath <wink>.
        ikiwa isinstance(days, float):
            dayfrac, days = _math.modf(days)
            daysecondsfrac, daysecondswhole = _math.modf(dayfrac * (24.*3600.))
            assert daysecondswhole == int(daysecondswhole)  # can't overflow
            s = int(daysecondswhole)
            assert days == int(days)
            d = int(days)
        isipokua:
            daysecondsfrac = 0.0
            d = days
        assert isinstance(daysecondsfrac, float)
        assert abs(daysecondsfrac) <= 1.0
        assert isinstance(d, int)
        assert abs(s) <= 24 * 3600
        # days isn't referenced again before redefinition

        ikiwa isinstance(seconds, float):
            secondsfrac, seconds = _math.modf(seconds)
            assert seconds == int(seconds)
            seconds = int(seconds)
            secondsfrac += daysecondsfrac
            assert abs(secondsfrac) <= 2.0
        isipokua:
            secondsfrac = daysecondsfrac
        # daysecondsfrac isn't referenced again
        assert isinstance(secondsfrac, float)
        assert abs(secondsfrac) <= 2.0

        assert isinstance(seconds, int)
        days, seconds = divmod(seconds, 24*3600)
        d += days
        s += int(seconds)    # can't overflow
        assert isinstance(s, int)
        assert abs(s) <= 2 * 24 * 3600
        # seconds isn't referenced again before redefinition

        usdouble = secondsfrac * 1e6
        assert abs(usdouble) < 2.1e6    # exact value sio critical
        # secondsfrac isn't referenced again

        ikiwa isinstance(microseconds, float):
            microseconds = round(microseconds + usdouble)
            seconds, microseconds = divmod(microseconds, 1000000)
            days, seconds = divmod(seconds, 24*3600)
            d += days
            s += seconds
        isipokua:
            microseconds = int(microseconds)
            seconds, microseconds = divmod(microseconds, 1000000)
            days, seconds = divmod(seconds, 24*3600)
            d += days
            s += seconds
            microseconds = round(microseconds + usdouble)
        assert isinstance(s, int)
        assert isinstance(microseconds, int)
        assert abs(s) <= 3 * 24 * 3600
        assert abs(microseconds) < 3.1e6

        # Just a little bit of carrying possible kila microseconds na seconds.
        seconds, us = divmod(microseconds, 1000000)
        s += seconds
        days, s = divmod(s, 24*3600)
        d += days

        assert isinstance(d, int)
        assert isinstance(s, int) na 0 <= s < 24*3600
        assert isinstance(us, int) na 0 <= us < 1000000

        ikiwa abs(d) > 999999999:
            ashiria OverflowError("timedelta # of days ni too large: %d" % d)

        self = object.__new__(cls)
        self._days = d
        self._seconds = s
        self._microseconds = us
        self._hashcode = -1
        rudisha self

    eleza __repr__(self):
        args = []
        ikiwa self._days:
            args.append("days=%d" % self._days)
        ikiwa self._seconds:
            args.append("seconds=%d" % self._seconds)
        ikiwa self._microseconds:
            args.append("microseconds=%d" % self._microseconds)
        ikiwa sio args:
            args.append('0')
        rudisha "%s.%s(%s)" % (self.__class__.__module__,
                              self.__class__.__qualname__,
                              ', '.join(args))

    eleza __str__(self):
        mm, ss = divmod(self._seconds, 60)
        hh, mm = divmod(mm, 60)
        s = "%d:%02d:%02d" % (hh, mm, ss)
        ikiwa self._days:
            eleza plural(n):
                rudisha n, abs(n) != 1 na "s" ama ""
            s = ("%d day%s, " % plural(self._days)) + s
        ikiwa self._microseconds:
            s = s + ".%06d" % self._microseconds
        rudisha s

    eleza total_seconds(self):
        """Total seconds kwenye the duration."""
        rudisha ((self.days * 86400 + self.seconds) * 10**6 +
                self.microseconds) / 10**6

    # Read-only field accessors
    @property
    eleza days(self):
        """days"""
        rudisha self._days

    @property
    eleza seconds(self):
        """seconds"""
        rudisha self._seconds

    @property
    eleza microseconds(self):
        """microseconds"""
        rudisha self._microseconds

    eleza __add__(self, other):
        ikiwa isinstance(other, timedelta):
            # kila CPython compatibility, we cannot use
            # our __class__ here, but need a real timedelta
            rudisha timedelta(self._days + other._days,
                             self._seconds + other._seconds,
                             self._microseconds + other._microseconds)
        rudisha NotImplemented

    __radd__ = __add__

    eleza __sub__(self, other):
        ikiwa isinstance(other, timedelta):
            # kila CPython compatibility, we cannot use
            # our __class__ here, but need a real timedelta
            rudisha timedelta(self._days - other._days,
                             self._seconds - other._seconds,
                             self._microseconds - other._microseconds)
        rudisha NotImplemented

    eleza __rsub__(self, other):
        ikiwa isinstance(other, timedelta):
            rudisha -self + other
        rudisha NotImplemented

    eleza __neg__(self):
        # kila CPython compatibility, we cannot use
        # our __class__ here, but need a real timedelta
        rudisha timedelta(-self._days,
                         -self._seconds,
                         -self._microseconds)

    eleza __pos__(self):
        rudisha self

    eleza __abs__(self):
        ikiwa self._days < 0:
            rudisha -self
        isipokua:
            rudisha self

    eleza __mul__(self, other):
        ikiwa isinstance(other, int):
            # kila CPython compatibility, we cannot use
            # our __class__ here, but need a real timedelta
            rudisha timedelta(self._days * other,
                             self._seconds * other,
                             self._microseconds * other)
        ikiwa isinstance(other, float):
            usec = self._to_microseconds()
            a, b = other.as_integer_ratio()
            rudisha timedelta(0, 0, _divide_and_round(usec * a, b))
        rudisha NotImplemented

    __rmul__ = __mul__

    eleza _to_microseconds(self):
        rudisha ((self._days * (24*3600) + self._seconds) * 1000000 +
                self._microseconds)

    eleza __floordiv__(self, other):
        ikiwa sio isinstance(other, (int, timedelta)):
            rudisha NotImplemented
        usec = self._to_microseconds()
        ikiwa isinstance(other, timedelta):
            rudisha usec // other._to_microseconds()
        ikiwa isinstance(other, int):
            rudisha timedelta(0, 0, usec // other)

    eleza __truediv__(self, other):
        ikiwa sio isinstance(other, (int, float, timedelta)):
            rudisha NotImplemented
        usec = self._to_microseconds()
        ikiwa isinstance(other, timedelta):
            rudisha usec / other._to_microseconds()
        ikiwa isinstance(other, int):
            rudisha timedelta(0, 0, _divide_and_round(usec, other))
        ikiwa isinstance(other, float):
            a, b = other.as_integer_ratio()
            rudisha timedelta(0, 0, _divide_and_round(b * usec, a))

    eleza __mod__(self, other):
        ikiwa isinstance(other, timedelta):
            r = self._to_microseconds() % other._to_microseconds()
            rudisha timedelta(0, 0, r)
        rudisha NotImplemented

    eleza __divmod__(self, other):
        ikiwa isinstance(other, timedelta):
            q, r = divmod(self._to_microseconds(),
                          other._to_microseconds())
            rudisha q, timedelta(0, 0, r)
        rudisha NotImplemented

    # Comparisons of timedelta objects ukijumuisha other.

    eleza __eq__(self, other):
        ikiwa isinstance(other, timedelta):
            rudisha self._cmp(other) == 0
        isipokua:
            rudisha NotImplemented

    eleza __le__(self, other):
        ikiwa isinstance(other, timedelta):
            rudisha self._cmp(other) <= 0
        isipokua:
            rudisha NotImplemented

    eleza __lt__(self, other):
        ikiwa isinstance(other, timedelta):
            rudisha self._cmp(other) < 0
        isipokua:
            rudisha NotImplemented

    eleza __ge__(self, other):
        ikiwa isinstance(other, timedelta):
            rudisha self._cmp(other) >= 0
        isipokua:
            rudisha NotImplemented

    eleza __gt__(self, other):
        ikiwa isinstance(other, timedelta):
            rudisha self._cmp(other) > 0
        isipokua:
            rudisha NotImplemented

    eleza _cmp(self, other):
        assert isinstance(other, timedelta)
        rudisha _cmp(self._getstate(), other._getstate())

    eleza __hash__(self):
        ikiwa self._hashcode == -1:
            self._hashcode = hash(self._getstate())
        rudisha self._hashcode

    eleza __bool__(self):
        rudisha (self._days != 0 ama
                self._seconds != 0 ama
                self._microseconds != 0)

    # Pickle support.

    eleza _getstate(self):
        rudisha (self._days, self._seconds, self._microseconds)

    eleza __reduce__(self):
        rudisha (self.__class__, self._getstate())

timedelta.min = timedelta(-999999999)
timedelta.max = timedelta(days=999999999, hours=23, minutes=59, seconds=59,
                          microseconds=999999)
timedelta.resolution = timedelta(microseconds=1)

kundi date:
    """Concrete date type.

    Constructors:

    __new__()
    fromtimestamp()
    today()
    fromordinal()

    Operators:

    __repr__, __str__
    __eq__, __le__, __lt__, __ge__, __gt__, __hash__
    __add__, __radd__, __sub__ (add/radd only ukijumuisha timedelta arg)

    Methods:

    timetuple()
    toordinal()
    weekday()
    isoweekday(), isocalendar(), isoformat()
    ctime()
    strftime()

    Properties (readonly):
    year, month, day
    """
    __slots__ = '_year', '_month', '_day', '_hashcode'

    eleza __new__(cls, year, month=Tupu, day=Tupu):
        """Constructor.

        Arguments:

        year, month, day (required, base 1)
        """
        ikiwa (month ni Tupu na
            isinstance(year, (bytes, str)) na len(year) == 4 na
            1 <= ord(year[2:3]) <= 12):
            # Pickle support
            ikiwa isinstance(year, str):
                jaribu:
                    year = year.encode('latin1')
                tatizo UnicodeEncodeError:
                    # More informative error message.
                    ashiria ValueError(
                        "Failed to encode latin1 string when unpickling "
                        "a date object. "
                        "pickle.load(data, encoding='latin1') ni assumed.")
            self = object.__new__(cls)
            self.__setstate(year)
            self._hashcode = -1
            rudisha self
        year, month, day = _check_date_fields(year, month, day)
        self = object.__new__(cls)
        self._year = year
        self._month = month
        self._day = day
        self._hashcode = -1
        rudisha self

    # Additional constructors

    @classmethod
    eleza fromtimestamp(cls, t):
        "Construct a date kutoka a POSIX timestamp (like time.time())."
        y, m, d, hh, mm, ss, weekday, jday, dst = _time.localtime(t)
        rudisha cls(y, m, d)

    @classmethod
    eleza today(cls):
        "Construct a date kutoka time.time()."
        t = _time.time()
        rudisha cls.fromtimestamp(t)

    @classmethod
    eleza fromordinal(cls, n):
        """Construct a date kutoka a proleptic Gregorian ordinal.

        January 1 of year 1 ni day 1.  Only the year, month na day are
        non-zero kwenye the result.
        """
        y, m, d = _ord2ymd(n)
        rudisha cls(y, m, d)

    @classmethod
    eleza fromisoformat(cls, date_string):
        """Construct a date kutoka the output of date.isoformat()."""
        ikiwa sio isinstance(date_string, str):
            ashiria TypeError('fromisoformat: argument must be str')

        jaribu:
            assert len(date_string) == 10
            rudisha cls(*_parse_isoformat_date(date_string))
        tatizo Exception:
            ashiria ValueError(f'Invalid isoformat string: {date_string!r}')

    @classmethod
    eleza fromisocalendar(cls, year, week, day):
        """Construct a date kutoka the ISO year, week number na weekday.

        This ni the inverse of the date.isocalendar() function"""
        # Year ni bounded this way because 9999-12-31 ni (9999, 52, 5)
        ikiwa sio MINYEAR <= year <= MAXYEAR:
            ashiria ValueError(f"Year ni out of range: {year}")

        ikiwa sio 0 < week < 53:
            out_of_range = Kweli

            ikiwa week == 53:
                # ISO years have 53 weeks kwenye them on years starting ukijumuisha a
                # Thursday na leap years starting on a Wednesday
                first_weekday = _ymd2ord(year, 1, 1) % 7
                ikiwa (first_weekday == 4 ama (first_weekday == 3 na
                                           _is_leap(year))):
                    out_of_range = Uongo

            ikiwa out_of_range:
                ashiria ValueError(f"Invalid week: {week}")

        ikiwa sio 0 < day < 8:
            ashiria ValueError(f"Invalid weekday: {day} (range ni [1, 7])")

        # Now compute the offset kutoka (Y, 1, 1) kwenye days:
        day_offset = (week - 1) * 7 + (day - 1)

        # Calculate the ordinal day kila monday, week 1
        day_1 = _isoweek1monday(year)
        ord_day = day_1 + day_offset

        rudisha cls(*_ord2ymd(ord_day))

    # Conversions to string

    eleza __repr__(self):
        """Convert to formal string, kila repr().

        >>> dt = datetime(2010, 1, 1)
        >>> repr(dt)
        'datetime.datetime(2010, 1, 1, 0, 0)'

        >>> dt = datetime(2010, 1, 1, tzinfo=timezone.utc)
        >>> repr(dt)
        'datetime.datetime(2010, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)'
        """
        rudisha "%s.%s(%d, %d, %d)" % (self.__class__.__module__,
                                      self.__class__.__qualname__,
                                      self._year,
                                      self._month,
                                      self._day)
    # XXX These shouldn't depend on time.localtime(), because that
    # clips the usable dates to [1970 .. 2038).  At least ctime() is
    # easily done without using strftime() -- that's better too because
    # strftime("%c", ...) ni locale specific.


    eleza ctime(self):
        "Return ctime() style string."
        weekday = self.toordinal() % 7 ama 7
        rudisha "%s %s %2d 00:00:00 %04d" % (
            _DAYNAMES[weekday],
            _MONTHNAMES[self._month],
            self._day, self._year)

    eleza strftime(self, fmt):
        "Format using strftime()."
        rudisha _wrap_strftime(self, fmt, self.timetuple())

    eleza __format__(self, fmt):
        ikiwa sio isinstance(fmt, str):
            ashiria TypeError("must be str, sio %s" % type(fmt).__name__)
        ikiwa len(fmt) != 0:
            rudisha self.strftime(fmt)
        rudisha str(self)

    eleza isoformat(self):
        """Return the date formatted according to ISO.

        This ni 'YYYY-MM-DD'.

        References:
        - http://www.w3.org/TR/NOTE-datetime
        - http://www.cl.cam.ac.uk/~mgk25/iso-time.html
        """
        rudisha "%04d-%02d-%02d" % (self._year, self._month, self._day)

    __str__ = isoformat

    # Read-only field accessors
    @property
    eleza year(self):
        """year (1-9999)"""
        rudisha self._year

    @property
    eleza month(self):
        """month (1-12)"""
        rudisha self._month

    @property
    eleza day(self):
        """day (1-31)"""
        rudisha self._day

    # Standard conversions, __eq__, __le__, __lt__, __ge__, __gt__,
    # __hash__ (and helpers)

    eleza timetuple(self):
        "Return local time tuple compatible ukijumuisha time.localtime()."
        rudisha _build_struct_time(self._year, self._month, self._day,
                                  0, 0, 0, -1)

    eleza toordinal(self):
        """Return proleptic Gregorian ordinal kila the year, month na day.

        January 1 of year 1 ni day 1.  Only the year, month na day values
        contribute to the result.
        """
        rudisha _ymd2ord(self._year, self._month, self._day)

    eleza replace(self, year=Tupu, month=Tupu, day=Tupu):
        """Return a new date ukijumuisha new values kila the specified fields."""
        ikiwa year ni Tupu:
            year = self._year
        ikiwa month ni Tupu:
            month = self._month
        ikiwa day ni Tupu:
            day = self._day
        rudisha type(self)(year, month, day)

    # Comparisons of date objects ukijumuisha other.

    eleza __eq__(self, other):
        ikiwa isinstance(other, date):
            rudisha self._cmp(other) == 0
        rudisha NotImplemented

    eleza __le__(self, other):
        ikiwa isinstance(other, date):
            rudisha self._cmp(other) <= 0
        rudisha NotImplemented

    eleza __lt__(self, other):
        ikiwa isinstance(other, date):
            rudisha self._cmp(other) < 0
        rudisha NotImplemented

    eleza __ge__(self, other):
        ikiwa isinstance(other, date):
            rudisha self._cmp(other) >= 0
        rudisha NotImplemented

    eleza __gt__(self, other):
        ikiwa isinstance(other, date):
            rudisha self._cmp(other) > 0
        rudisha NotImplemented

    eleza _cmp(self, other):
        assert isinstance(other, date)
        y, m, d = self._year, self._month, self._day
        y2, m2, d2 = other._year, other._month, other._day
        rudisha _cmp((y, m, d), (y2, m2, d2))

    eleza __hash__(self):
        "Hash."
        ikiwa self._hashcode == -1:
            self._hashcode = hash(self._getstate())
        rudisha self._hashcode

    # Computations

    eleza __add__(self, other):
        "Add a date to a timedelta."
        ikiwa isinstance(other, timedelta):
            o = self.toordinal() + other.days
            ikiwa 0 < o <= _MAXORDINAL:
                rudisha type(self).fromordinal(o)
            ashiria OverflowError("result out of range")
        rudisha NotImplemented

    __radd__ = __add__

    eleza __sub__(self, other):
        """Subtract two dates, ama a date na a timedelta."""
        ikiwa isinstance(other, timedelta):
            rudisha self + timedelta(-other.days)
        ikiwa isinstance(other, date):
            days1 = self.toordinal()
            days2 = other.toordinal()
            rudisha timedelta(days1 - days2)
        rudisha NotImplemented

    eleza weekday(self):
        "Return day of the week, where Monday == 0 ... Sunday == 6."
        rudisha (self.toordinal() + 6) % 7

    # Day-of-the-week na week-of-the-year, according to ISO

    eleza isoweekday(self):
        "Return day of the week, where Monday == 1 ... Sunday == 7."
        # 1-Jan-0001 ni a Monday
        rudisha self.toordinal() % 7 ama 7

    eleza isocalendar(self):
        """Return a 3-tuple containing ISO year, week number, na weekday.

        The first ISO week of the year ni the (Mon-Sun) week
        containing the year's first Thursday; everything isipokua derives
        kutoka that.

        The first week ni 1; Monday ni 1 ... Sunday ni 7.

        ISO calendar algorithm taken from
        http://www.phys.uu.nl/~vgent/calendar/isocalendar.htm
        (used ukijumuisha permission)
        """
        year = self._year
        week1monday = _isoweek1monday(year)
        today = _ymd2ord(self._year, self._month, self._day)
        # Internally, week na day have origin 0
        week, day = divmod(today - week1monday, 7)
        ikiwa week < 0:
            year -= 1
            week1monday = _isoweek1monday(year)
            week, day = divmod(today - week1monday, 7)
        lasivyo week >= 52:
            ikiwa today >= _isoweek1monday(year+1):
                year += 1
                week = 0
        rudisha year, week+1, day+1

    # Pickle support.

    eleza _getstate(self):
        yhi, ylo = divmod(self._year, 256)
        rudisha bytes([yhi, ylo, self._month, self._day]),

    eleza __setstate(self, string):
        yhi, ylo, self._month, self._day = string
        self._year = yhi * 256 + ylo

    eleza __reduce__(self):
        rudisha (self.__class__, self._getstate())

_date_kundi = date  # so functions w/ args named "date" can get at the class

date.min = date(1, 1, 1)
date.max = date(9999, 12, 31)
date.resolution = timedelta(days=1)


kundi tzinfo:
    """Abstract base kundi kila time zone info classes.

    Subclasses must override the name(), utcoffset() na dst() methods.
    """
    __slots__ = ()

    eleza tzname(self, dt):
        "datetime -> string name of time zone."
        ashiria NotImplementedError("tzinfo subkundi must override tzname()")

    eleza utcoffset(self, dt):
        "datetime -> timedelta, positive kila east of UTC, negative kila west of UTC"
        ashiria NotImplementedError("tzinfo subkundi must override utcoffset()")

    eleza dst(self, dt):
        """datetime -> DST offset kama timedelta, positive kila east of UTC.

        Return 0 ikiwa DST haiko kwenye effect.  utcoffset() must include the DST
        offset.
        """
        ashiria NotImplementedError("tzinfo subkundi must override dst()")

    eleza fromutc(self, dt):
        "datetime kwenye UTC -> datetime kwenye local time."

        ikiwa sio isinstance(dt, datetime):
            ashiria TypeError("fromutc() requires a datetime argument")
        ikiwa dt.tzinfo ni sio self:
            ashiria ValueError("dt.tzinfo ni sio self")

        dtoff = dt.utcoffset()
        ikiwa dtoff ni Tupu:
            ashiria ValueError("fromutc() requires a non-Tupu utcoffset() "
                             "result")

        # See the long comment block at the end of this file kila an
        # explanation of this algorithm.
        dtdst = dt.dst()
        ikiwa dtdst ni Tupu:
            ashiria ValueError("fromutc() requires a non-Tupu dst() result")
        delta = dtoff - dtdst
        ikiwa delta:
            dt += delta
            dtdst = dt.dst()
            ikiwa dtdst ni Tupu:
                ashiria ValueError("fromutc(): dt.dst gave inconsistent "
                                 "results; cannot convert")
        rudisha dt + dtdst

    # Pickle support.

    eleza __reduce__(self):
        getinitargs = getattr(self, "__getinitargs__", Tupu)
        ikiwa getinitargs:
            args = getinitargs()
        isipokua:
            args = ()
        getstate = getattr(self, "__getstate__", Tupu)
        ikiwa getstate:
            state = getstate()
        isipokua:
            state = getattr(self, "__dict__", Tupu) ama Tupu
        ikiwa state ni Tupu:
            rudisha (self.__class__, args)
        isipokua:
            rudisha (self.__class__, args, state)

_tzinfo_kundi = tzinfo

kundi time:
    """Time ukijumuisha time zone.

    Constructors:

    __new__()

    Operators:

    __repr__, __str__
    __eq__, __le__, __lt__, __ge__, __gt__, __hash__

    Methods:

    strftime()
    isoformat()
    utcoffset()
    tzname()
    dst()

    Properties (readonly):
    hour, minute, second, microsecond, tzinfo, fold
    """
    __slots__ = '_hour', '_minute', '_second', '_microsecond', '_tzinfo', '_hashcode', '_fold'

    eleza __new__(cls, hour=0, minute=0, second=0, microsecond=0, tzinfo=Tupu, *, fold=0):
        """Constructor.

        Arguments:

        hour, minute (required)
        second, microsecond (default to zero)
        tzinfo (default to Tupu)
        fold (keyword only, default to zero)
        """
        ikiwa (isinstance(hour, (bytes, str)) na len(hour) == 6 na
            ord(hour[0:1])&0x7F < 24):
            # Pickle support
            ikiwa isinstance(hour, str):
                jaribu:
                    hour = hour.encode('latin1')
                tatizo UnicodeEncodeError:
                    # More informative error message.
                    ashiria ValueError(
                        "Failed to encode latin1 string when unpickling "
                        "a time object. "
                        "pickle.load(data, encoding='latin1') ni assumed.")
            self = object.__new__(cls)
            self.__setstate(hour, minute ama Tupu)
            self._hashcode = -1
            rudisha self
        hour, minute, second, microsecond, fold = _check_time_fields(
            hour, minute, second, microsecond, fold)
        _check_tzinfo_arg(tzinfo)
        self = object.__new__(cls)
        self._hour = hour
        self._minute = minute
        self._second = second
        self._microsecond = microsecond
        self._tzinfo = tzinfo
        self._hashcode = -1
        self._fold = fold
        rudisha self

    # Read-only field accessors
    @property
    eleza hour(self):
        """hour (0-23)"""
        rudisha self._hour

    @property
    eleza minute(self):
        """minute (0-59)"""
        rudisha self._minute

    @property
    eleza second(self):
        """second (0-59)"""
        rudisha self._second

    @property
    eleza microsecond(self):
        """microsecond (0-999999)"""
        rudisha self._microsecond

    @property
    eleza tzinfo(self):
        """timezone info object"""
        rudisha self._tzinfo

    @property
    eleza fold(self):
        rudisha self._fold

    # Standard conversions, __hash__ (and helpers)

    # Comparisons of time objects ukijumuisha other.

    eleza __eq__(self, other):
        ikiwa isinstance(other, time):
            rudisha self._cmp(other, allow_mixed=Kweli) == 0
        isipokua:
            rudisha NotImplemented

    eleza __le__(self, other):
        ikiwa isinstance(other, time):
            rudisha self._cmp(other) <= 0
        isipokua:
            rudisha NotImplemented

    eleza __lt__(self, other):
        ikiwa isinstance(other, time):
            rudisha self._cmp(other) < 0
        isipokua:
            rudisha NotImplemented

    eleza __ge__(self, other):
        ikiwa isinstance(other, time):
            rudisha self._cmp(other) >= 0
        isipokua:
            rudisha NotImplemented

    eleza __gt__(self, other):
        ikiwa isinstance(other, time):
            rudisha self._cmp(other) > 0
        isipokua:
            rudisha NotImplemented

    eleza _cmp(self, other, allow_mixed=Uongo):
        assert isinstance(other, time)
        mytz = self._tzinfo
        ottz = other._tzinfo
        myoff = otoff = Tupu

        ikiwa mytz ni ottz:
            base_compare = Kweli
        isipokua:
            myoff = self.utcoffset()
            otoff = other.utcoffset()
            base_compare = myoff == otoff

        ikiwa base_compare:
            rudisha _cmp((self._hour, self._minute, self._second,
                         self._microsecond),
                        (other._hour, other._minute, other._second,
                         other._microsecond))
        ikiwa myoff ni Tupu ama otoff ni Tupu:
            ikiwa allow_mixed:
                rudisha 2 # arbitrary non-zero value
            isipokua:
                ashiria TypeError("cannot compare naive na aware times")
        myhhmm = self._hour * 60 + self._minute - myoff//timedelta(minutes=1)
        othhmm = other._hour * 60 + other._minute - otoff//timedelta(minutes=1)
        rudisha _cmp((myhhmm, self._second, self._microsecond),
                    (othhmm, other._second, other._microsecond))

    eleza __hash__(self):
        """Hash."""
        ikiwa self._hashcode == -1:
            ikiwa self.fold:
                t = self.replace(fold=0)
            isipokua:
                t = self
            tzoff = t.utcoffset()
            ikiwa sio tzoff:  # zero ama Tupu
                self._hashcode = hash(t._getstate()[0])
            isipokua:
                h, m = divmod(timedelta(hours=self.hour, minutes=self.minute) - tzoff,
                              timedelta(hours=1))
                assert sio m % timedelta(minutes=1), "whole minute"
                m //= timedelta(minutes=1)
                ikiwa 0 <= h < 24:
                    self._hashcode = hash(time(h, m, self.second, self.microsecond))
                isipokua:
                    self._hashcode = hash((h, m, self.second, self.microsecond))
        rudisha self._hashcode

    # Conversion to string

    eleza _tzstr(self):
        """Return formatted timezone offset (+xx:xx) ama an empty string."""
        off = self.utcoffset()
        rudisha _format_offset(off)

    eleza __repr__(self):
        """Convert to formal string, kila repr()."""
        ikiwa self._microsecond != 0:
            s = ", %d, %d" % (self._second, self._microsecond)
        lasivyo self._second != 0:
            s = ", %d" % self._second
        isipokua:
            s = ""
        s= "%s.%s(%d, %d%s)" % (self.__class__.__module__,
                                self.__class__.__qualname__,
                                self._hour, self._minute, s)
        ikiwa self._tzinfo ni sio Tupu:
            assert s[-1:] == ")"
            s = s[:-1] + ", tzinfo=%r" % self._tzinfo + ")"
        ikiwa self._fold:
            assert s[-1:] == ")"
            s = s[:-1] + ", fold=1)"
        rudisha s

    eleza isoformat(self, timespec='auto'):
        """Return the time formatted according to ISO.

        The full format ni 'HH:MM:SS.mmmmmm+zz:zz'. By default, the fractional
        part ni omitted ikiwa self.microsecond == 0.

        The optional argument timespec specifies the number of additional
        terms of the time to include.
        """
        s = _format_time(self._hour, self._minute, self._second,
                          self._microsecond, timespec)
        tz = self._tzstr()
        ikiwa tz:
            s += tz
        rudisha s

    __str__ = isoformat

    @classmethod
    eleza fromisoformat(cls, time_string):
        """Construct a time kutoka the output of isoformat()."""
        ikiwa sio isinstance(time_string, str):
            ashiria TypeError('fromisoformat: argument must be str')

        jaribu:
            rudisha cls(*_parse_isoformat_time(time_string))
        tatizo Exception:
            ashiria ValueError(f'Invalid isoformat string: {time_string!r}')


    eleza strftime(self, fmt):
        """Format using strftime().  The date part of the timestamp pitaed
        to underlying strftime should sio be used.
        """
        # The year must be >= 1000 isipokua Python's strftime implementation
        # can ashiria a bogus exception.
        timetuple = (1900, 1, 1,
                     self._hour, self._minute, self._second,
                     0, 1, -1)
        rudisha _wrap_strftime(self, fmt, timetuple)

    eleza __format__(self, fmt):
        ikiwa sio isinstance(fmt, str):
            ashiria TypeError("must be str, sio %s" % type(fmt).__name__)
        ikiwa len(fmt) != 0:
            rudisha self.strftime(fmt)
        rudisha str(self)

    # Timezone functions

    eleza utcoffset(self):
        """Return the timezone offset kama timedelta, positive east of UTC
         (negative west of UTC)."""
        ikiwa self._tzinfo ni Tupu:
            rudisha Tupu
        offset = self._tzinfo.utcoffset(Tupu)
        _check_utc_offset("utcoffset", offset)
        rudisha offset

    eleza tzname(self):
        """Return the timezone name.

        Note that the name ni 100% informational -- there's no requirement that
        it mean anything kwenye particular. For example, "GMT", "UTC", "-500",
        "-5:00", "EDT", "US/Eastern", "America/New York" are all valid replies.
        """
        ikiwa self._tzinfo ni Tupu:
            rudisha Tupu
        name = self._tzinfo.tzname(Tupu)
        _check_tzname(name)
        rudisha name

    eleza dst(self):
        """Return 0 ikiwa DST ni haiko kwenye effect, ama the DST offset (as timedelta
        positive eastward) ikiwa DST ni kwenye effect.

        This ni purely informational; the DST offset has already been added to
        the UTC offset returned by utcoffset() ikiwa applicable, so there's no
        need to consult dst() unless you're interested kwenye displaying the DST
        info.
        """
        ikiwa self._tzinfo ni Tupu:
            rudisha Tupu
        offset = self._tzinfo.dst(Tupu)
        _check_utc_offset("dst", offset)
        rudisha offset

    eleza replace(self, hour=Tupu, minute=Tupu, second=Tupu, microsecond=Tupu,
                tzinfo=Kweli, *, fold=Tupu):
        """Return a new time ukijumuisha new values kila the specified fields."""
        ikiwa hour ni Tupu:
            hour = self.hour
        ikiwa minute ni Tupu:
            minute = self.minute
        ikiwa second ni Tupu:
            second = self.second
        ikiwa microsecond ni Tupu:
            microsecond = self.microsecond
        ikiwa tzinfo ni Kweli:
            tzinfo = self.tzinfo
        ikiwa fold ni Tupu:
            fold = self._fold
        rudisha type(self)(hour, minute, second, microsecond, tzinfo, fold=fold)

    # Pickle support.

    eleza _getstate(self, protocol=3):
        us2, us3 = divmod(self._microsecond, 256)
        us1, us2 = divmod(us2, 256)
        h = self._hour
        ikiwa self._fold na protocol > 3:
            h += 128
        basestate = bytes([h, self._minute, self._second,
                           us1, us2, us3])
        ikiwa self._tzinfo ni Tupu:
            rudisha (basestate,)
        isipokua:
            rudisha (basestate, self._tzinfo)

    eleza __setstate(self, string, tzinfo):
        ikiwa tzinfo ni sio Tupu na sio isinstance(tzinfo, _tzinfo_class):
            ashiria TypeError("bad tzinfo state arg")
        h, self._minute, self._second, us1, us2, us3 = string
        ikiwa h > 127:
            self._fold = 1
            self._hour = h - 128
        isipokua:
            self._fold = 0
            self._hour = h
        self._microsecond = (((us1 << 8) | us2) << 8) | us3
        self._tzinfo = tzinfo

    eleza __reduce_ex__(self, protocol):
        rudisha (time, self._getstate(protocol))

    eleza __reduce__(self):
        rudisha self.__reduce_ex__(2)

_time_kundi = time  # so functions w/ args named "time" can get at the class

time.min = time(0, 0, 0)
time.max = time(23, 59, 59, 999999)
time.resolution = timedelta(microseconds=1)

kundi datetime(date):
    """datetime(year, month, day[, hour[, minute[, second[, microsecond[,tzinfo]]]]])

    The year, month na day arguments are required. tzinfo may be Tupu, ama an
    instance of a tzinfo subclass. The remaining arguments may be ints.
    """
    __slots__ = date.__slots__ + time.__slots__

    eleza __new__(cls, year, month=Tupu, day=Tupu, hour=0, minute=0, second=0,
                microsecond=0, tzinfo=Tupu, *, fold=0):
        ikiwa (isinstance(year, (bytes, str)) na len(year) == 10 na
            1 <= ord(year[2:3])&0x7F <= 12):
            # Pickle support
            ikiwa isinstance(year, str):
                jaribu:
                    year = bytes(year, 'latin1')
                tatizo UnicodeEncodeError:
                    # More informative error message.
                    ashiria ValueError(
                        "Failed to encode latin1 string when unpickling "
                        "a datetime object. "
                        "pickle.load(data, encoding='latin1') ni assumed.")
            self = object.__new__(cls)
            self.__setstate(year, month)
            self._hashcode = -1
            rudisha self
        year, month, day = _check_date_fields(year, month, day)
        hour, minute, second, microsecond, fold = _check_time_fields(
            hour, minute, second, microsecond, fold)
        _check_tzinfo_arg(tzinfo)
        self = object.__new__(cls)
        self._year = year
        self._month = month
        self._day = day
        self._hour = hour
        self._minute = minute
        self._second = second
        self._microsecond = microsecond
        self._tzinfo = tzinfo
        self._hashcode = -1
        self._fold = fold
        rudisha self

    # Read-only field accessors
    @property
    eleza hour(self):
        """hour (0-23)"""
        rudisha self._hour

    @property
    eleza minute(self):
        """minute (0-59)"""
        rudisha self._minute

    @property
    eleza second(self):
        """second (0-59)"""
        rudisha self._second

    @property
    eleza microsecond(self):
        """microsecond (0-999999)"""
        rudisha self._microsecond

    @property
    eleza tzinfo(self):
        """timezone info object"""
        rudisha self._tzinfo

    @property
    eleza fold(self):
        rudisha self._fold

    @classmethod
    eleza _fromtimestamp(cls, t, utc, tz):
        """Construct a datetime kutoka a POSIX timestamp (like time.time()).

        A timezone info object may be pitaed kwenye kama well.
        """
        frac, t = _math.modf(t)
        us = round(frac * 1e6)
        ikiwa us >= 1000000:
            t += 1
            us -= 1000000
        lasivyo us < 0:
            t -= 1
            us += 1000000

        converter = _time.gmtime ikiwa utc isipokua _time.localtime
        y, m, d, hh, mm, ss, weekday, jday, dst = converter(t)
        ss = min(ss, 59)    # clamp out leap seconds ikiwa the platform has them
        result = cls(y, m, d, hh, mm, ss, us, tz)
        ikiwa tz ni Tupu:
            # As of version 2015f max fold kwenye IANA database is
            # 23 hours at 1969-09-30 13:00:00 kwenye Kwajalein.
            # Let's probe 24 hours kwenye the past to detect a transition:
            max_fold_seconds = 24 * 3600

            # On Windows localtime_s throws an OSError kila negative values,
            # thus we can't perform fold detection kila values of time less
            # than the max time fold. See comments kwenye _datetimemodule's
            # version of this method kila more details.
            ikiwa t < max_fold_seconds na sys.platform.startswith("win"):
                rudisha result

            y, m, d, hh, mm, ss = converter(t - max_fold_seconds)[:6]
            probe1 = cls(y, m, d, hh, mm, ss, us, tz)
            trans = result - probe1 - timedelta(0, max_fold_seconds)
            ikiwa trans.days < 0:
                y, m, d, hh, mm, ss = converter(t + trans // timedelta(0, 1))[:6]
                probe2 = cls(y, m, d, hh, mm, ss, us, tz)
                ikiwa probe2 == result:
                    result._fold = 1
        isipokua:
            result = tz.fromutc(result)
        rudisha result

    @classmethod
    eleza fromtimestamp(cls, t, tz=Tupu):
        """Construct a datetime kutoka a POSIX timestamp (like time.time()).

        A timezone info object may be pitaed kwenye kama well.
        """
        _check_tzinfo_arg(tz)

        rudisha cls._fromtimestamp(t, tz ni sio Tupu, tz)

    @classmethod
    eleza utcfromtimestamp(cls, t):
        """Construct a naive UTC datetime kutoka a POSIX timestamp."""
        rudisha cls._fromtimestamp(t, Kweli, Tupu)

    @classmethod
    eleza now(cls, tz=Tupu):
        "Construct a datetime kutoka time.time() na optional time zone info."
        t = _time.time()
        rudisha cls.fromtimestamp(t, tz)

    @classmethod
    eleza utcnow(cls):
        "Construct a UTC datetime kutoka time.time()."
        t = _time.time()
        rudisha cls.utcfromtimestamp(t)

    @classmethod
    eleza combine(cls, date, time, tzinfo=Kweli):
        "Construct a datetime kutoka a given date na a given time."
        ikiwa sio isinstance(date, _date_class):
            ashiria TypeError("date argument must be a date instance")
        ikiwa sio isinstance(time, _time_class):
            ashiria TypeError("time argument must be a time instance")
        ikiwa tzinfo ni Kweli:
            tzinfo = time.tzinfo
        rudisha cls(date.year, date.month, date.day,
                   time.hour, time.minute, time.second, time.microsecond,
                   tzinfo, fold=time.fold)

    @classmethod
    eleza fromisoformat(cls, date_string):
        """Construct a datetime kutoka the output of datetime.isoformat()."""
        ikiwa sio isinstance(date_string, str):
            ashiria TypeError('fromisoformat: argument must be str')

        # Split this at the separator
        dstr = date_string[0:10]
        tstr = date_string[11:]

        jaribu:
            date_components = _parse_isoformat_date(dstr)
        tatizo ValueError:
            ashiria ValueError(f'Invalid isoformat string: {date_string!r}')

        ikiwa tstr:
            jaribu:
                time_components = _parse_isoformat_time(tstr)
            tatizo ValueError:
                ashiria ValueError(f'Invalid isoformat string: {date_string!r}')
        isipokua:
            time_components = [0, 0, 0, 0, Tupu]

        rudisha cls(*(date_components + time_components))

    eleza timetuple(self):
        "Return local time tuple compatible ukijumuisha time.localtime()."
        dst = self.dst()
        ikiwa dst ni Tupu:
            dst = -1
        lasivyo dst:
            dst = 1
        isipokua:
            dst = 0
        rudisha _build_struct_time(self.year, self.month, self.day,
                                  self.hour, self.minute, self.second,
                                  dst)

    eleza _mktime(self):
        """Return integer POSIX timestamp."""
        epoch = datetime(1970, 1, 1)
        max_fold_seconds = 24 * 3600
        t = (self - epoch) // timedelta(0, 1)
        eleza local(u):
            y, m, d, hh, mm, ss = _time.localtime(u)[:6]
            rudisha (datetime(y, m, d, hh, mm, ss) - epoch) // timedelta(0, 1)

        # Our goal ni to solve t = local(u) kila u.
        a = local(t) - t
        u1 = t - a
        t1 = local(u1)
        ikiwa t1 == t:
            # We found one solution, but it may sio be the one we need.
            # Look kila an earlier solution (ikiwa `fold` ni 0), ama a
            # later one (ikiwa `fold` ni 1).
            u2 = u1 + (-max_fold_seconds, max_fold_seconds)[self.fold]
            b = local(u2) - u2
            ikiwa a == b:
                rudisha u1
        isipokua:
            b = t1 - u1
            assert a != b
        u2 = t - b
        t2 = local(u2)
        ikiwa t2 == t:
            rudisha u2
        ikiwa t1 == t:
            rudisha u1
        # We have found both offsets a na b, but neither t - a nor t - b is
        # a solution.  This means t ni kwenye the gap.
        rudisha (max, min)[self.fold](u1, u2)


    eleza timestamp(self):
        "Return POSIX timestamp kama float"
        ikiwa self._tzinfo ni Tupu:
            s = self._mktime()
            rudisha s + self.microsecond / 1e6
        isipokua:
            rudisha (self - _EPOCH).total_seconds()

    eleza utctimetuple(self):
        "Return UTC time tuple compatible ukijumuisha time.gmtime()."
        offset = self.utcoffset()
        ikiwa offset:
            self -= offset
        y, m, d = self.year, self.month, self.day
        hh, mm, ss = self.hour, self.minute, self.second
        rudisha _build_struct_time(y, m, d, hh, mm, ss, 0)

    eleza date(self):
        "Return the date part."
        rudisha date(self._year, self._month, self._day)

    eleza time(self):
        "Return the time part, ukijumuisha tzinfo Tupu."
        rudisha time(self.hour, self.minute, self.second, self.microsecond, fold=self.fold)

    eleza timetz(self):
        "Return the time part, ukijumuisha same tzinfo."
        rudisha time(self.hour, self.minute, self.second, self.microsecond,
                    self._tzinfo, fold=self.fold)

    eleza replace(self, year=Tupu, month=Tupu, day=Tupu, hour=Tupu,
                minute=Tupu, second=Tupu, microsecond=Tupu, tzinfo=Kweli,
                *, fold=Tupu):
        """Return a new datetime ukijumuisha new values kila the specified fields."""
        ikiwa year ni Tupu:
            year = self.year
        ikiwa month ni Tupu:
            month = self.month
        ikiwa day ni Tupu:
            day = self.day
        ikiwa hour ni Tupu:
            hour = self.hour
        ikiwa minute ni Tupu:
            minute = self.minute
        ikiwa second ni Tupu:
            second = self.second
        ikiwa microsecond ni Tupu:
            microsecond = self.microsecond
        ikiwa tzinfo ni Kweli:
            tzinfo = self.tzinfo
        ikiwa fold ni Tupu:
            fold = self.fold
        rudisha type(self)(year, month, day, hour, minute, second,
                          microsecond, tzinfo, fold=fold)

    eleza _local_timezone(self):
        ikiwa self.tzinfo ni Tupu:
            ts = self._mktime()
        isipokua:
            ts = (self - _EPOCH) // timedelta(seconds=1)
        localtm = _time.localtime(ts)
        local = datetime(*localtm[:6])
        # Extract TZ data
        gmtoff = localtm.tm_gmtoff
        zone = localtm.tm_zone
        rudisha timezone(timedelta(seconds=gmtoff), zone)

    eleza astimezone(self, tz=Tupu):
        ikiwa tz ni Tupu:
            tz = self._local_timezone()
        lasivyo sio isinstance(tz, tzinfo):
            ashiria TypeError("tz argument must be an instance of tzinfo")

        mytz = self.tzinfo
        ikiwa mytz ni Tupu:
            mytz = self._local_timezone()
            myoffset = mytz.utcoffset(self)
        isipokua:
            myoffset = mytz.utcoffset(self)
            ikiwa myoffset ni Tupu:
                mytz = self.replace(tzinfo=Tupu)._local_timezone()
                myoffset = mytz.utcoffset(self)

        ikiwa tz ni mytz:
            rudisha self

        # Convert self to UTC, na attach the new time zone object.
        utc = (self - myoffset).replace(tzinfo=tz)

        # Convert kutoka UTC to tz's local time.
        rudisha tz.fromutc(utc)

    # Ways to produce a string.

    eleza ctime(self):
        "Return ctime() style string."
        weekday = self.toordinal() % 7 ama 7
        rudisha "%s %s %2d %02d:%02d:%02d %04d" % (
            _DAYNAMES[weekday],
            _MONTHNAMES[self._month],
            self._day,
            self._hour, self._minute, self._second,
            self._year)

    eleza isoformat(self, sep='T', timespec='auto'):
        """Return the time formatted according to ISO.

        The full format looks like 'YYYY-MM-DD HH:MM:SS.mmmmmm'.
        By default, the fractional part ni omitted ikiwa self.microsecond == 0.

        If self.tzinfo ni sio Tupu, the UTC offset ni also attached, giving
        giving a full format of 'YYYY-MM-DD HH:MM:SS.mmmmmm+HH:MM'.

        Optional argument sep specifies the separator between date na
        time, default 'T'.

        The optional argument timespec specifies the number of additional
        terms of the time to include.
        """
        s = ("%04d-%02d-%02d%c" % (self._year, self._month, self._day, sep) +
             _format_time(self._hour, self._minute, self._second,
                          self._microsecond, timespec))

        off = self.utcoffset()
        tz = _format_offset(off)
        ikiwa tz:
            s += tz

        rudisha s

    eleza __repr__(self):
        """Convert to formal string, kila repr()."""
        L = [self._year, self._month, self._day,  # These are never zero
             self._hour, self._minute, self._second, self._microsecond]
        ikiwa L[-1] == 0:
            toa L[-1]
        ikiwa L[-1] == 0:
            toa L[-1]
        s = "%s.%s(%s)" % (self.__class__.__module__,
                           self.__class__.__qualname__,
                           ", ".join(map(str, L)))
        ikiwa self._tzinfo ni sio Tupu:
            assert s[-1:] == ")"
            s = s[:-1] + ", tzinfo=%r" % self._tzinfo + ")"
        ikiwa self._fold:
            assert s[-1:] == ")"
            s = s[:-1] + ", fold=1)"
        rudisha s

    eleza __str__(self):
        "Convert to string, kila str()."
        rudisha self.isoformat(sep=' ')

    @classmethod
    eleza strptime(cls, date_string, format):
        'string, format -> new datetime parsed kutoka a string (like time.strptime()).'
        agiza _strptime
        rudisha _strptime._strptime_datetime(cls, date_string, format)

    eleza utcoffset(self):
        """Return the timezone offset kama timedelta positive east of UTC (negative west of
        UTC)."""
        ikiwa self._tzinfo ni Tupu:
            rudisha Tupu
        offset = self._tzinfo.utcoffset(self)
        _check_utc_offset("utcoffset", offset)
        rudisha offset

    eleza tzname(self):
        """Return the timezone name.

        Note that the name ni 100% informational -- there's no requirement that
        it mean anything kwenye particular. For example, "GMT", "UTC", "-500",
        "-5:00", "EDT", "US/Eastern", "America/New York" are all valid replies.
        """
        ikiwa self._tzinfo ni Tupu:
            rudisha Tupu
        name = self._tzinfo.tzname(self)
        _check_tzname(name)
        rudisha name

    eleza dst(self):
        """Return 0 ikiwa DST ni haiko kwenye effect, ama the DST offset (as timedelta
        positive eastward) ikiwa DST ni kwenye effect.

        This ni purely informational; the DST offset has already been added to
        the UTC offset returned by utcoffset() ikiwa applicable, so there's no
        need to consult dst() unless you're interested kwenye displaying the DST
        info.
        """
        ikiwa self._tzinfo ni Tupu:
            rudisha Tupu
        offset = self._tzinfo.dst(self)
        _check_utc_offset("dst", offset)
        rudisha offset

    # Comparisons of datetime objects ukijumuisha other.

    eleza __eq__(self, other):
        ikiwa isinstance(other, datetime):
            rudisha self._cmp(other, allow_mixed=Kweli) == 0
        lasivyo sio isinstance(other, date):
            rudisha NotImplemented
        isipokua:
            rudisha Uongo

    eleza __le__(self, other):
        ikiwa isinstance(other, datetime):
            rudisha self._cmp(other) <= 0
        lasivyo sio isinstance(other, date):
            rudisha NotImplemented
        isipokua:
            _cmperror(self, other)

    eleza __lt__(self, other):
        ikiwa isinstance(other, datetime):
            rudisha self._cmp(other) < 0
        lasivyo sio isinstance(other, date):
            rudisha NotImplemented
        isipokua:
            _cmperror(self, other)

    eleza __ge__(self, other):
        ikiwa isinstance(other, datetime):
            rudisha self._cmp(other) >= 0
        lasivyo sio isinstance(other, date):
            rudisha NotImplemented
        isipokua:
            _cmperror(self, other)

    eleza __gt__(self, other):
        ikiwa isinstance(other, datetime):
            rudisha self._cmp(other) > 0
        lasivyo sio isinstance(other, date):
            rudisha NotImplemented
        isipokua:
            _cmperror(self, other)

    eleza _cmp(self, other, allow_mixed=Uongo):
        assert isinstance(other, datetime)
        mytz = self._tzinfo
        ottz = other._tzinfo
        myoff = otoff = Tupu

        ikiwa mytz ni ottz:
            base_compare = Kweli
        isipokua:
            myoff = self.utcoffset()
            otoff = other.utcoffset()
            # Assume that allow_mixed means that we are called kutoka __eq__
            ikiwa allow_mixed:
                ikiwa myoff != self.replace(fold=not self.fold).utcoffset():
                    rudisha 2
                ikiwa otoff != other.replace(fold=not other.fold).utcoffset():
                    rudisha 2
            base_compare = myoff == otoff

        ikiwa base_compare:
            rudisha _cmp((self._year, self._month, self._day,
                         self._hour, self._minute, self._second,
                         self._microsecond),
                        (other._year, other._month, other._day,
                         other._hour, other._minute, other._second,
                         other._microsecond))
        ikiwa myoff ni Tupu ama otoff ni Tupu:
            ikiwa allow_mixed:
                rudisha 2 # arbitrary non-zero value
            isipokua:
                ashiria TypeError("cannot compare naive na aware datetimes")
        # XXX What follows could be done more efficiently...
        diff = self - other     # this will take offsets into account
        ikiwa diff.days < 0:
            rudisha -1
        rudisha diff na 1 ama 0

    eleza __add__(self, other):
        "Add a datetime na a timedelta."
        ikiwa sio isinstance(other, timedelta):
            rudisha NotImplemented
        delta = timedelta(self.toordinal(),
                          hours=self._hour,
                          minutes=self._minute,
                          seconds=self._second,
                          microseconds=self._microsecond)
        delta += other
        hour, rem = divmod(delta.seconds, 3600)
        minute, second = divmod(rem, 60)
        ikiwa 0 < delta.days <= _MAXORDINAL:
            rudisha type(self).combine(date.fromordinal(delta.days),
                                      time(hour, minute, second,
                                           delta.microseconds,
                                           tzinfo=self._tzinfo))
        ashiria OverflowError("result out of range")

    __radd__ = __add__

    eleza __sub__(self, other):
        "Subtract two datetimes, ama a datetime na a timedelta."
        ikiwa sio isinstance(other, datetime):
            ikiwa isinstance(other, timedelta):
                rudisha self + -other
            rudisha NotImplemented

        days1 = self.toordinal()
        days2 = other.toordinal()
        secs1 = self._second + self._minute * 60 + self._hour * 3600
        secs2 = other._second + other._minute * 60 + other._hour * 3600
        base = timedelta(days1 - days2,
                         secs1 - secs2,
                         self._microsecond - other._microsecond)
        ikiwa self._tzinfo ni other._tzinfo:
            rudisha base
        myoff = self.utcoffset()
        otoff = other.utcoffset()
        ikiwa myoff == otoff:
            rudisha base
        ikiwa myoff ni Tupu ama otoff ni Tupu:
            ashiria TypeError("cannot mix naive na timezone-aware time")
        rudisha base + otoff - myoff

    eleza __hash__(self):
        ikiwa self._hashcode == -1:
            ikiwa self.fold:
                t = self.replace(fold=0)
            isipokua:
                t = self
            tzoff = t.utcoffset()
            ikiwa tzoff ni Tupu:
                self._hashcode = hash(t._getstate()[0])
            isipokua:
                days = _ymd2ord(self.year, self.month, self.day)
                seconds = self.hour * 3600 + self.minute * 60 + self.second
                self._hashcode = hash(timedelta(days, seconds, self.microsecond) - tzoff)
        rudisha self._hashcode

    # Pickle support.

    eleza _getstate(self, protocol=3):
        yhi, ylo = divmod(self._year, 256)
        us2, us3 = divmod(self._microsecond, 256)
        us1, us2 = divmod(us2, 256)
        m = self._month
        ikiwa self._fold na protocol > 3:
            m += 128
        basestate = bytes([yhi, ylo, m, self._day,
                           self._hour, self._minute, self._second,
                           us1, us2, us3])
        ikiwa self._tzinfo ni Tupu:
            rudisha (basestate,)
        isipokua:
            rudisha (basestate, self._tzinfo)

    eleza __setstate(self, string, tzinfo):
        ikiwa tzinfo ni sio Tupu na sio isinstance(tzinfo, _tzinfo_class):
            ashiria TypeError("bad tzinfo state arg")
        (yhi, ylo, m, self._day, self._hour,
         self._minute, self._second, us1, us2, us3) = string
        ikiwa m > 127:
            self._fold = 1
            self._month = m - 128
        isipokua:
            self._fold = 0
            self._month = m
        self._year = yhi * 256 + ylo
        self._microsecond = (((us1 << 8) | us2) << 8) | us3
        self._tzinfo = tzinfo

    eleza __reduce_ex__(self, protocol):
        rudisha (self.__class__, self._getstate(protocol))

    eleza __reduce__(self):
        rudisha self.__reduce_ex__(2)


datetime.min = datetime(1, 1, 1)
datetime.max = datetime(9999, 12, 31, 23, 59, 59, 999999)
datetime.resolution = timedelta(microseconds=1)


eleza _isoweek1monday(year):
    # Helper to calculate the day number of the Monday starting week 1
    # XXX This could be done more efficiently
    THURSDAY = 3
    firstday = _ymd2ord(year, 1, 1)
    firstweekday = (firstday + 6) % 7  # See weekday() above
    week1monday = firstday - firstweekday
    ikiwa firstweekday > THURSDAY:
        week1monday += 7
    rudisha week1monday


kundi timezone(tzinfo):
    __slots__ = '_offset', '_name'

    # Sentinel value to disallow Tupu
    _Omitted = object()
    eleza __new__(cls, offset, name=_Omitted):
        ikiwa sio isinstance(offset, timedelta):
            ashiria TypeError("offset must be a timedelta")
        ikiwa name ni cls._Omitted:
            ikiwa sio offset:
                rudisha cls.utc
            name = Tupu
        lasivyo sio isinstance(name, str):
            ashiria TypeError("name must be a string")
        ikiwa sio cls._minoffset <= offset <= cls._maxoffset:
            ashiria ValueError("offset must be a timedelta "
                             "strictly between -timedelta(hours=24) na "
                             "timedelta(hours=24).")
        rudisha cls._create(offset, name)

    @classmethod
    eleza _create(cls, offset, name=Tupu):
        self = tzinfo.__new__(cls)
        self._offset = offset
        self._name = name
        rudisha self

    eleza __getinitargs__(self):
        """pickle support"""
        ikiwa self._name ni Tupu:
            rudisha (self._offset,)
        rudisha (self._offset, self._name)

    eleza __eq__(self, other):
        ikiwa isinstance(other, timezone):
            rudisha self._offset == other._offset
        rudisha NotImplemented

    eleza __hash__(self):
        rudisha hash(self._offset)

    eleza __repr__(self):
        """Convert to formal string, kila repr().

        >>> tz = timezone.utc
        >>> repr(tz)
        'datetime.timezone.utc'
        >>> tz = timezone(timedelta(hours=-5), 'EST')
        >>> repr(tz)
        "datetime.timezone(datetime.timedelta(-1, 68400), 'EST')"
        """
        ikiwa self ni self.utc:
            rudisha 'datetime.timezone.utc'
        ikiwa self._name ni Tupu:
            rudisha "%s.%s(%r)" % (self.__class__.__module__,
                                  self.__class__.__qualname__,
                                  self._offset)
        rudisha "%s.%s(%r, %r)" % (self.__class__.__module__,
                                  self.__class__.__qualname__,
                                  self._offset, self._name)

    eleza __str__(self):
        rudisha self.tzname(Tupu)

    eleza utcoffset(self, dt):
        ikiwa isinstance(dt, datetime) ama dt ni Tupu:
            rudisha self._offset
        ashiria TypeError("utcoffset() argument must be a datetime instance"
                        " ama Tupu")

    eleza tzname(self, dt):
        ikiwa isinstance(dt, datetime) ama dt ni Tupu:
            ikiwa self._name ni Tupu:
                rudisha self._name_from_offset(self._offset)
            rudisha self._name
        ashiria TypeError("tzname() argument must be a datetime instance"
                        " ama Tupu")

    eleza dst(self, dt):
        ikiwa isinstance(dt, datetime) ama dt ni Tupu:
            rudisha Tupu
        ashiria TypeError("dst() argument must be a datetime instance"
                        " ama Tupu")

    eleza fromutc(self, dt):
        ikiwa isinstance(dt, datetime):
            ikiwa dt.tzinfo ni sio self:
                ashiria ValueError("fromutc: dt.tzinfo "
                                 "is sio self")
            rudisha dt + self._offset
        ashiria TypeError("fromutc() argument must be a datetime instance"
                        " ama Tupu")

    _maxoffset = timedelta(hours=24, microseconds=-1)
    _minoffset = -_maxoffset

    @staticmethod
    eleza _name_from_offset(delta):
        ikiwa sio delta:
            rudisha 'UTC'
        ikiwa delta < timedelta(0):
            sign = '-'
            delta = -delta
        isipokua:
            sign = '+'
        hours, rest = divmod(delta, timedelta(hours=1))
        minutes, rest = divmod(rest, timedelta(minutes=1))
        seconds = rest.seconds
        microseconds = rest.microseconds
        ikiwa microseconds:
            rudisha (f'UTC{sign}{hours:02d}:{minutes:02d}:{seconds:02d}'
                    f'.{microseconds:06d}')
        ikiwa seconds:
            rudisha f'UTC{sign}{hours:02d}:{minutes:02d}:{seconds:02d}'
        rudisha f'UTC{sign}{hours:02d}:{minutes:02d}'

timezone.utc = timezone._create(timedelta(0))
# bpo-37642: These attributes are rounded to the nearest minute kila backwards
# compatibility, even though the constructor will accept a wider range of
# values. This may change kwenye the future.
timezone.min = timezone._create(-timedelta(hours=23, minutes=59))
timezone.max = timezone._create(timedelta(hours=23, minutes=59))
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

# Some time zone algebra.  For a datetime x, let
#     x.n = x stripped of its timezone -- its naive time.
#     x.o = x.utcoffset(), na assuming that doesn't ashiria an exception ama
#           rudisha Tupu
#     x.d = x.dst(), na assuming that doesn't ashiria an exception ama
#           rudisha Tupu
#     x.s = x's standard offset, x.o - x.d
#
# Now some derived rules, where k ni a duration (timedelta).
#
# 1. x.o = x.s + x.d
#    This follows kutoka the definition of x.s.
#
# 2. If x na y have the same tzinfo member, x.s = y.s.
#    This ni actually a requirement, an assumption we need to make about
#    sane tzinfo classes.
#
# 3. The naive UTC time corresponding to x ni x.n - x.o.
#    This ni again a requirement kila a sane tzinfo class.
#
# 4. (x+k).s = x.s
#    This follows kutoka #2, na that datimetimetz+timedelta preserves tzinfo.
#
# 5. (x+k).n = x.n + k
#    Again follows kutoka how arithmetic ni defined.
#
# Now we can explain tz.fromutc(x).  Let's assume it's an interesting case
# (meaning that the various tzinfo methods exist, na don't blow up ama return
# Tupu when called).
#
# The function wants to rudisha a datetime y ukijumuisha timezone tz, equivalent to x.
# x ni already kwenye UTC.
#
# By #3, we want
#
#     y.n - y.o = x.n                             [1]
#
# The algorithm starts by attaching tz to x.n, na calling that y.  So
# x.n = y.n at the start.  Then it wants to add a duration k to y, so that [1]
# becomes true; kwenye effect, we want to solve [2] kila k:
#
#    (y+k).n - (y+k).o = x.n                      [2]
#
# By #1, this ni the same as
#
#    (y+k).n - ((y+k).s + (y+k).d) = x.n          [3]
#
# By #5, (y+k).n = y.n + k, which equals x.n + k because x.n=y.n at the start.
# Substituting that into [3],
#
#    x.n + k - (y+k).s - (y+k).d = x.n; the x.n terms cancel, leaving
#    k - (y+k).s - (y+k).d = 0; rearranging,
#    k = (y+k).s - (y+k).d; by #4, (y+k).s == y.s, so
#    k = y.s - (y+k).d
#
# On the RHS, (y+k).d can't be computed directly, but y.s can be, na we
# approximate k by ignoring the (y+k).d term at first.  Note that k can't be
# very large, since all offset-returning methods rudisha a duration of magnitude
# less than 24 hours.  For that reason, ikiwa y ni firmly kwenye std time, (y+k).d must
# be 0, so ignoring it has no consequence then.
#
# In any case, the new value is
#
#     z = y + y.s                                 [4]
#
# It's helpful to step back at look at [4] kutoka a higher level:  it's simply
# mapping kutoka UTC to tz's standard time.
#
# At this point, if
#
#     z.n - z.o = x.n                             [5]
#
# we have an equivalent time, na are almost done.  The insecurity here is
# at the start of daylight time.  Picture US Eastern kila concreteness.  The wall
# time jumps kutoka 1:59 to 3:00, na wall hours of the form 2:MM don't make good
# sense then.  The docs ask that an Eastern tzinfo kundi consider such a time to
# be EDT (because it's "after 2"), which ni a redundant spelling of 1:MM EST
# on the day DST starts.  We want to rudisha the 1:MM EST spelling because that's
# the only spelling that makes sense on the local wall clock.
#
# In fact, ikiwa [5] holds at this point, we do have the standard-time spelling,
# but that takes a bit of proof.  We first prove a stronger result.  What's the
# difference between the LHS na RHS of [5]?  Let
#
#     diff = x.n - (z.n - z.o)                    [6]
#
# Now
#     z.n =                       by [4]
#     (y + y.s).n =               by #5
#     y.n + y.s =                 since y.n = x.n
#     x.n + y.s =                 since z na y are have the same tzinfo member,
#                                     y.s = z.s by #2
#     x.n + z.s
#
# Plugging that back into [6] gives
#
#     diff =
#     x.n - ((x.n + z.s) - z.o) =     expanding
#     x.n - x.n - z.s + z.o =         cancelling
#     - z.s + z.o =                   by #2
#     z.d
#
# So diff = z.d.
#
# If [5] ni true now, diff = 0, so z.d = 0 too, na we have the standard-time
# spelling we wanted kwenye the endcase described above.  We're done.  Contrarily,
# ikiwa z.d = 0, then we have a UTC equivalent, na are also done.
#
# If [5] ni sio true now, diff = z.d != 0, na z.d ni the offset we need to
# add to z (in effect, z ni kwenye tz's standard time, na we need to shift the
# local clock into tz's daylight time).
#
# Let
#
#     z' = z + z.d = z + diff                     [7]
#
# na we can again ask whether
#
#     z'.n - z'.o = x.n                           [8]
#
# If so, we're done.  If not, the tzinfo kundi ni insane, according to the
# assumptions we've made.  This also requires a bit of proof.  As before, let's
# compute the difference between the LHS na RHS of [8] (and skipping some of
# the justifications kila the kinds of substitutions we've done several times
# already):
#
#     diff' = x.n - (z'.n - z'.o) =           replacing z'.n via [7]
#             x.n  - (z.n + diff - z'.o) =    replacing diff via [6]
#             x.n - (z.n + x.n - (z.n - z.o) - z'.o) =
#             x.n - z.n - x.n + z.n - z.o + z'.o =    cancel x.n
#             - z.n + z.n - z.o + z'.o =              cancel z.n
#             - z.o + z'.o =                      #1 twice
#             -z.s - z.d + z'.s + z'.d =          z na z' have same tzinfo
#             z'.d - z.d
#
# So z' ni UTC-equivalent to x iff z'.d = z.d at this point.  If they are equal,
# we've found the UTC-equivalent so are done.  In fact, we stop ukijumuisha [7] na
# rudisha z', sio bothering to compute z'.d.
#
# How could z.d na z'd differ?  z' = z + z.d [7], so merely moving z' by
# a dst() offset, na starting *from* a time already kwenye DST (we know z.d != 0),
# would have to change the result dst() returns:  we start kwenye DST, na moving
# a little further into it takes us out of DST.
#
# There isn't a sane case where this can happen.  The closest it gets ni at
# the end of DST, where there's an hour kwenye UTC ukijumuisha no spelling kwenye a hybrid
# tzinfo class.  In US Eastern, that's 5:MM UTC = 0:MM EST = 1:MM EDT.  During
# that hour, on an Eastern clock 1:MM ni taken kama being kwenye standard time (6:MM
# UTC) because the docs insist on that, but 0:MM ni taken kama being kwenye daylight
# time (4:MM UTC).  There ni no local time mapping to 5:MM UTC.  The local
# clock jumps kutoka 1:59 back to 1:00 again, na repeats the 1:MM hour in
# standard time.  Since that's what the local clock *does*, we want to map both
# UTC hours 5:MM na 6:MM to 1:MM Eastern.  The result ni ambiguous
# kwenye local time, but so it goes -- it's the way the local clock works.
#
# When x = 5:MM UTC ni the input to this algorithm, x.o=0, y.o=-5 na y.d=0,
# so z=0:MM.  z.d=60 (minutes) then, so [5] doesn't hold na we keep going.
# z' = z + z.d = 1:MM then, na z'.d=0, na z'.d - z.d = -60 != 0 so [8]
# (correctly) concludes that z' ni sio UTC-equivalent to x.
#
# Because we know z.d said z was kwenye daylight time (else [5] would have held na
# we would have stopped then), na we know z.d != z'.d (else [8] would have held
# na we have stopped then), na there are only 2 possible values dst() can
# rudisha kwenye Eastern, it follows that z'.d must be 0 (which it ni kwenye the example,
# but the reasoning doesn't depend on the example -- it depends on there being
# two possible dst() outcomes, one zero na the other non-zero).  Therefore
# z' must be kwenye standard time, na ni the spelling we want kwenye this case.
#
# Note again that z' ni sio UTC-equivalent kama far kama the hybrid tzinfo kundi is
# concerned (because it takes z' kama being kwenye standard time rather than the
# daylight time we intend here), but returning it gives the real-life "local
# clock repeats an hour" behavior when mapping the "unspellable" UTC hour into
# tz.
#
# When the input ni 6:MM, z=1:MM na z.d=0, na we stop at once, again with
# the 1:MM standard time spelling we want.
#
# So how can this koma?  One of the assumptions must be violated.  Two
# possibilities:
#
# 1) [2] effectively says that y.s ni invariant across all y belong to a given
#    time zone.  This isn't true if, kila political reasons ama continental drift,
#    a region decides to change its base offset kutoka UTC.
#
# 2) There may be versions of "double daylight" time where the tail end of
#    the analysis gives up a step too early.  I haven't thought about that
#    enough to say.
#
# In any case, it's clear that the default fromutc() ni strong enough to handle
# "almost all" time zones:  so long kama the standard offset ni invariant, it
# doesn't matter ikiwa daylight time transition points change kutoka year to year, ama
# ikiwa daylight time ni skipped kwenye some years; it doesn't matter how large ama
# small dst() may get within its bounds; na it doesn't even matter ikiwa some
# perverse time zone returns a negative dst()).  So a komaing case must be
# pretty bizarre, na a tzinfo subkundi can override fromutc() ikiwa it is.

jaribu:
    kutoka _datetime agiza *
tatizo ImportError:
    pita
isipokua:
    # Clean up unused names
    toa (_DAYNAMES, _DAYS_BEFORE_MONTH, _DAYS_IN_MONTH, _DI100Y, _DI400Y,
         _DI4Y, _EPOCH, _MAXORDINAL, _MONTHNAMES, _build_struct_time,
         _check_date_fields, _check_int_field, _check_time_fields,
         _check_tzinfo_arg, _check_tzname, _check_utc_offset, _cmp, _cmperror,
         _date_class, _days_before_month, _days_before_year, _days_in_month,
         _format_time, _format_offset, _is_leap, _isoweek1monday, _math,
         _ord2ymd, _time, _time_class, _tzinfo_class, _wrap_strftime, _ymd2ord,
         _divide_and_round, _parse_isoformat_date, _parse_isoformat_time,
         _parse_hh_mm_ss_ff)
    # XXX Since agiza * above excludes names that start ukijumuisha _,
    # docstring does sio get overwritten. In the future, it may be
    # appropriate to maintain a single module level docstring na
    # remove the following line.
    kutoka _datetime agiza __doc__
