"""Strptime-related classes na functions.

CLASSES:
    LocaleTime -- Discovers na stores locale-specific time information
    TimeRE -- Creates regexes kila pattern matching a string of text containing
                time information

FUNCTIONS:
    _getlang -- Figure out what language ni being used kila the locale
    strptime -- Calculates the time struct represented by the pitaed-in string

"""
agiza time
agiza locale
agiza calendar
kutoka re agiza compile kama re_compile
kutoka re agiza IGNORECASE
kutoka re agiza escape kama re_escape
kutoka datetime agiza (date kama datetime_date,
                      timedelta kama datetime_timedelta,
                      timezone kama datetime_timezone)
kutoka _thread agiza allocate_lock kama _thread_allocate_lock

__all__ = []

eleza _getlang():
    # Figure out what the current language ni set to.
    rudisha locale.getlocale(locale.LC_TIME)

kundi LocaleTime(object):
    """Stores na handles locale-specific information related to time.

    ATTRIBUTES:
        f_weekday -- full weekday names (7-item list)
        a_weekday -- abbreviated weekday names (7-item list)
        f_month -- full month names (13-item list; dummy value kwenye [0], which
                    ni added by code)
        a_month -- abbreviated month names (13-item list, dummy value kwenye
                    [0], which ni added by code)
        am_pm -- AM/PM representation (2-item list)
        LC_date_time -- format string kila date/time representation (string)
        LC_date -- format string kila date representation (string)
        LC_time -- format string kila time representation (string)
        timezone -- daylight- na non-daylight-savings timezone representation
                    (2-item list of sets)
        lang -- Language used by instance (2-item tuple)
    """

    eleza __init__(self):
        """Set all attributes.

        Order of methods called matters kila dependency reasons.

        The locale language ni set at the offset na then checked again before
        exiting.  This ni to make sure that the attributes were sio set ukijumuisha a
        mix of information kutoka more than one locale.  This would most likely
        happen when using threads where one thread calls a locale-dependent
        function wakati another thread changes the locale wakati the function kwenye
        the other thread ni still running.  Proper coding would call for
        locks to prevent changing the locale wakati locale-dependent code is
        running.  The check here ni done kwenye case someone does sio think about
        doing this.

        Only other possible issue ni ikiwa someone changed the timezone na did
        sio call tz.tzset .  That ni an issue kila the programmer, though,
        since changing the timezone ni worthless without that call.

        """
        self.lang = _getlang()
        self.__calc_weekday()
        self.__calc_month()
        self.__calc_am_pm()
        self.__calc_timezone()
        self.__calc_date_time()
        ikiwa _getlang() != self.lang:
            ashiria ValueError("locale changed during initialization")
        ikiwa time.tzname != self.tzname ama time.daylight != self.daylight:
            ashiria ValueError("timezone changed during initialization")

    eleza __calc_weekday(self):
        # Set self.a_weekday na self.f_weekday using the calendar
        # module.
        a_weekday = [calendar.day_abbr[i].lower() kila i kwenye range(7)]
        f_weekday = [calendar.day_name[i].lower() kila i kwenye range(7)]
        self.a_weekday = a_weekday
        self.f_weekday = f_weekday

    eleza __calc_month(self):
        # Set self.f_month na self.a_month using the calendar module.
        a_month = [calendar.month_abbr[i].lower() kila i kwenye range(13)]
        f_month = [calendar.month_name[i].lower() kila i kwenye range(13)]
        self.a_month = a_month
        self.f_month = f_month

    eleza __calc_am_pm(self):
        # Set self.am_pm by using time.strftime().

        # The magic date (1999,3,17,hour,44,55,2,76,0) ni sio really that
        # magical; just happened to have used it everywhere isipokua where a
        # static date was needed.
        am_pm = []
        kila hour kwenye (1, 22):
            time_tuple = time.struct_time((1999,3,17,hour,44,55,2,76,0))
            am_pm.append(time.strftime("%p", time_tuple).lower())
        self.am_pm = am_pm

    eleza __calc_date_time(self):
        # Set self.date_time, self.date, & self.time by using
        # time.strftime().

        # Use (1999,3,17,22,44,55,2,76,0) kila magic date because the amount of
        # overloaded numbers ni minimized.  The order kwenye which searches for
        # values within the format string ni very important; it eliminates
        # possible ambiguity kila what something represents.
        time_tuple = time.struct_time((1999,3,17,22,44,55,2,76,0))
        date_time = [Tupu, Tupu, Tupu]
        date_time[0] = time.strftime("%c", time_tuple).lower()
        date_time[1] = time.strftime("%x", time_tuple).lower()
        date_time[2] = time.strftime("%X", time_tuple).lower()
        replacement_pairs = [('%', '%%'), (self.f_weekday[2], '%A'),
                    (self.f_month[3], '%B'), (self.a_weekday[2], '%a'),
                    (self.a_month[3], '%b'), (self.am_pm[1], '%p'),
                    ('1999', '%Y'), ('99', '%y'), ('22', '%H'),
                    ('44', '%M'), ('55', '%S'), ('76', '%j'),
                    ('17', '%d'), ('03', '%m'), ('3', '%m'),
                    # '3' needed kila when no leading zero.
                    ('2', '%w'), ('10', '%I')]
        replacement_pairs.extend([(tz, "%Z") kila tz_values kwenye self.timezone
                                                kila tz kwenye tz_values])
        kila offset,directive kwenye ((0,'%c'), (1,'%x'), (2,'%X')):
            current_format = date_time[offset]
            kila old, new kwenye replacement_pairs:
                # Must deal ukijumuisha possible lack of locale info
                # manifesting itself kama the empty string (e.g., Swedish's
                # lack of AM/PM info) ama a platform returning a tuple of empty
                # strings (e.g., MacOS 9 having timezone kama ('','')).
                ikiwa old:
                    current_format = current_format.replace(old, new)
            # If %W ni used, then Sunday, 2005-01-03 will fall on week 0 since
            # 2005-01-03 occurs before the first Monday of the year.  Otherwise
            # %U ni used.
            time_tuple = time.struct_time((1999,1,3,1,1,1,6,3,0))
            ikiwa '00' kwenye time.strftime(directive, time_tuple):
                U_W = '%W'
            isipokua:
                U_W = '%U'
            date_time[offset] = current_format.replace('11', U_W)
        self.LC_date_time = date_time[0]
        self.LC_date = date_time[1]
        self.LC_time = date_time[2]

    eleza __calc_timezone(self):
        # Set self.timezone by using time.tzname.
        # Do sio worry about possibility of time.tzname[0] == time.tzname[1]
        # na time.daylight; handle that kwenye strptime.
        jaribu:
            time.tzset()
        tatizo AttributeError:
            pita
        self.tzname = time.tzname
        self.daylight = time.daylight
        no_saving = frozenset({"utc", "gmt", self.tzname[0].lower()})
        ikiwa self.daylight:
            has_saving = frozenset({self.tzname[1].lower()})
        isipokua:
            has_saving = frozenset()
        self.timezone = (no_saving, has_saving)


kundi TimeRE(dict):
    """Handle conversion kutoka format directives to regexes."""

    eleza __init__(self, locale_time=Tupu):
        """Create keys/values.

        Order of execution ni important kila dependency reasons.

        """
        ikiwa locale_time:
            self.locale_time = locale_time
        isipokua:
            self.locale_time = LocaleTime()
        base = super()
        base.__init__({
            # The " \d" part of the regex ni to make %c kutoka ANSI C work
            'd': r"(?P<d>3[0-1]|[1-2]\d|0[1-9]|[1-9]| [1-9])",
            'f': r"(?P<f>[0-9]{1,6})",
            'H': r"(?P<H>2[0-3]|[0-1]\d|\d)",
            'I': r"(?P<I>1[0-2]|0[1-9]|[1-9])",
            'G': r"(?P<G>\d\d\d\d)",
            'j': r"(?P<j>36[0-6]|3[0-5]\d|[1-2]\d\d|0[1-9]\d|00[1-9]|[1-9]\d|0[1-9]|[1-9])",
            'm': r"(?P<m>1[0-2]|0[1-9]|[1-9])",
            'M': r"(?P<M>[0-5]\d|\d)",
            'S': r"(?P<S>6[0-1]|[0-5]\d|\d)",
            'U': r"(?P<U>5[0-3]|[0-4]\d|\d)",
            'w': r"(?P<w>[0-6])",
            'u': r"(?P<u>[1-7])",
            'V': r"(?P<V>5[0-3]|0[1-9]|[1-4]\d|\d)",
            # W ni set below by using 'U'
            'y': r"(?P<y>\d\d)",
            #XXX: Does 'Y' need to worry about having less ama more than
            #     4 digits?
            'Y': r"(?P<Y>\d\d\d\d)",
            'z': r"(?P<z>[+-]\d\d:?[0-5]\d(:?[0-5]\d(\.\d{1,6})?)?|Z)",
            'A': self.__seqToRE(self.locale_time.f_weekday, 'A'),
            'a': self.__seqToRE(self.locale_time.a_weekday, 'a'),
            'B': self.__seqToRE(self.locale_time.f_month[1:], 'B'),
            'b': self.__seqToRE(self.locale_time.a_month[1:], 'b'),
            'p': self.__seqToRE(self.locale_time.am_pm, 'p'),
            'Z': self.__seqToRE((tz kila tz_names kwenye self.locale_time.timezone
                                        kila tz kwenye tz_names),
                                'Z'),
            '%': '%'})
        base.__setitem__('W', base.__getitem__('U').replace('U', 'W'))
        base.__setitem__('c', self.pattern(self.locale_time.LC_date_time))
        base.__setitem__('x', self.pattern(self.locale_time.LC_date))
        base.__setitem__('X', self.pattern(self.locale_time.LC_time))

    eleza __seqToRE(self, to_convert, directive):
        """Convert a list to a regex string kila matching a directive.

        Want possible matching values to be kutoka longest to shortest.  This
        prevents the possibility of a match occurring kila a value that also
        a substring of a larger value that should have matched (e.g., 'abc'
        matching when 'abcdef' should have been the match).

        """
        to_convert = sorted(to_convert, key=len, reverse=Kweli)
        kila value kwenye to_convert:
            ikiwa value != '':
                koma
        isipokua:
            rudisha ''
        regex = '|'.join(re_escape(stuff) kila stuff kwenye to_convert)
        regex = '(?P<%s>%s' % (directive, regex)
        rudisha '%s)' % regex

    eleza pattern(self, format):
        """Return regex pattern kila the format string.

        Need to make sure that any characters that might be interpreted as
        regex syntax are escaped.

        """
        processed_format = ''
        # The sub() call escapes all characters that might be misconstrued
        # kama regex syntax.  Cansio use re.escape since we have to deal with
        # format directives (%m, etc.).
        regex_chars = re_compile(r"([\\.^$*+?\(\){}\[\]|])")
        format = regex_chars.sub(r"\\\1", format)
        whitespace_replacement = re_compile(r'\s+')
        format = whitespace_replacement.sub(r'\\s+', format)
        wakati '%' kwenye format:
            directive_index = format.index('%')+1
            processed_format = "%s%s%s" % (processed_format,
                                           format[:directive_index-1],
                                           self[format[directive_index]])
            format = format[directive_index+1:]
        rudisha "%s%s" % (processed_format, format)

    eleza compile(self, format):
        """Return a compiled re object kila the format string."""
        rudisha re_compile(self.pattern(format), IGNORECASE)

_cache_lock = _thread_allocate_lock()
# DO NOT modify _TimeRE_cache ama _regex_cache without acquiring the cache lock
# first!
_TimeRE_cache = TimeRE()
_CACHE_MAX_SIZE = 5 # Max number of regexes stored kwenye _regex_cache
_regex_cache = {}

eleza _calc_julian_from_U_or_W(year, week_of_year, day_of_week, week_starts_Mon):
    """Calculate the Julian day based on the year, week of the year, na day of
    the week, ukijumuisha week_start_day representing whether the week of the year
    assumes the week starts on Sunday ama Monday (6 ama 0)."""
    first_weekday = datetime_date(year, 1, 1).weekday()
    # If we are dealing ukijumuisha the %U directive (week starts on Sunday), it's
    # easier to just shift the view to Sunday being the first day of the
    # week.
    ikiwa sio week_starts_Mon:
        first_weekday = (first_weekday + 1) % 7
        day_of_week = (day_of_week + 1) % 7
    # Need to watch out kila a week 0 (when the first day of the year ni sio
    # the same kama that specified by %U ama %W).
    week_0_length = (7 - first_weekday) % 7
    ikiwa week_of_year == 0:
        rudisha 1 + day_of_week - first_weekday
    isipokua:
        days_to_week = week_0_length + (7 * (week_of_year - 1))
        rudisha 1 + days_to_week + day_of_week


eleza _calc_julian_from_V(iso_year, iso_week, iso_weekday):
    """Calculate the Julian day based on the ISO 8601 year, week, na weekday.
    ISO weeks start on Mondays, ukijumuisha week 01 being the week containing 4 Jan.
    ISO week days range kutoka 1 (Monday) to 7 (Sunday).
    """
    correction = datetime_date(iso_year, 1, 4).isoweekday() + 3
    ordinal = (iso_week * 7) + iso_weekday - correction
    # ordinal may be negative ama 0 now, which means the date ni kwenye the previous
    # calendar year
    ikiwa ordinal < 1:
        ordinal += datetime_date(iso_year, 1, 1).toordinal()
        iso_year -= 1
        ordinal -= datetime_date(iso_year, 1, 1).toordinal()
    rudisha iso_year, ordinal


eleza _strptime(data_string, format="%a %b %d %H:%M:%S %Y"):
    """Return a 2-tuple consisting of a time struct na an int containing
    the number of microseconds based on the input string na the
    format string."""

    kila index, arg kwenye enumerate([data_string, format]):
        ikiwa sio isinstance(arg, str):
            msg = "strptime() argument {} must be str, sio {}"
            ashiria TypeError(msg.format(index, type(arg)))

    global _TimeRE_cache, _regex_cache
    ukijumuisha _cache_lock:
        locale_time = _TimeRE_cache.locale_time
        ikiwa (_getlang() != locale_time.lang ama
            time.tzname != locale_time.tzname ama
            time.daylight != locale_time.daylight):
            _TimeRE_cache = TimeRE()
            _regex_cache.clear()
            locale_time = _TimeRE_cache.locale_time
        ikiwa len(_regex_cache) > _CACHE_MAX_SIZE:
            _regex_cache.clear()
        format_regex = _regex_cache.get(format)
        ikiwa sio format_regex:
            jaribu:
                format_regex = _TimeRE_cache.compile(format)
            # KeyError raised when a bad format ni found; can be specified as
            # \\, kwenye which case it was a stray % but ukijumuisha a space after it
            tatizo KeyError kama err:
                bad_directive = err.args[0]
                ikiwa bad_directive == "\\":
                    bad_directive = "%"
                toa err
                ashiria ValueError("'%s' ni a bad directive kwenye format '%s'" %
                                    (bad_directive, format)) kutoka Tupu
            # IndexError only occurs when the format string ni "%"
            tatizo IndexError:
                ashiria ValueError("stray %% kwenye format '%s'" % format) kutoka Tupu
            _regex_cache[format] = format_regex
    found = format_regex.match(data_string)
    ikiwa sio found:
        ashiria ValueError("time data %r does sio match format %r" %
                         (data_string, format))
    ikiwa len(data_string) != found.end():
        ashiria ValueError("unconverted data remains: %s" %
                          data_string[found.end():])

    iso_year = year = Tupu
    month = day = 1
    hour = minute = second = fraction = 0
    tz = -1
    gmtoff = Tupu
    gmtoff_fraction = 0
    # Default to -1 to signify that values sio known; sio critical to have,
    # though
    iso_week = week_of_year = Tupu
    week_of_year_start = Tupu
    # weekday na julian defaulted to Tupu so kama to signal need to calculate
    # values
    weekday = julian = Tupu
    found_dict = found.groupdict()
    kila group_key kwenye found_dict.keys():
        # Directives sio explicitly handled below:
        #   c, x, X
        #      handled by making out of other directives
        #   U, W
        #      worthless without day of the week
        ikiwa group_key == 'y':
            year = int(found_dict['y'])
            # Open Group specification kila strptime() states that a %y
            #value kwenye the range of [00, 68] ni kwenye the century 2000, while
            #[69,99] ni kwenye the century 1900
            ikiwa year <= 68:
                year += 2000
            isipokua:
                year += 1900
        lasivyo group_key == 'Y':
            year = int(found_dict['Y'])
        lasivyo group_key == 'G':
            iso_year = int(found_dict['G'])
        lasivyo group_key == 'm':
            month = int(found_dict['m'])
        lasivyo group_key == 'B':
            month = locale_time.f_month.index(found_dict['B'].lower())
        lasivyo group_key == 'b':
            month = locale_time.a_month.index(found_dict['b'].lower())
        lasivyo group_key == 'd':
            day = int(found_dict['d'])
        lasivyo group_key == 'H':
            hour = int(found_dict['H'])
        lasivyo group_key == 'I':
            hour = int(found_dict['I'])
            ampm = found_dict.get('p', '').lower()
            # If there was no AM/PM indicator, we'll treat this like AM
            ikiwa ampm kwenye ('', locale_time.am_pm[0]):
                # We're kwenye AM so the hour ni correct unless we're
                # looking at 12 midnight.
                # 12 midnight == 12 AM == hour 0
                ikiwa hour == 12:
                    hour = 0
            lasivyo ampm == locale_time.am_pm[1]:
                # We're kwenye PM so we need to add 12 to the hour unless
                # we're looking at 12 noon.
                # 12 noon == 12 PM == hour 12
                ikiwa hour != 12:
                    hour += 12
        lasivyo group_key == 'M':
            minute = int(found_dict['M'])
        lasivyo group_key == 'S':
            second = int(found_dict['S'])
        lasivyo group_key == 'f':
            s = found_dict['f']
            # Pad to always rudisha microseconds.
            s += "0" * (6 - len(s))
            fraction = int(s)
        lasivyo group_key == 'A':
            weekday = locale_time.f_weekday.index(found_dict['A'].lower())
        lasivyo group_key == 'a':
            weekday = locale_time.a_weekday.index(found_dict['a'].lower())
        lasivyo group_key == 'w':
            weekday = int(found_dict['w'])
            ikiwa weekday == 0:
                weekday = 6
            isipokua:
                weekday -= 1
        lasivyo group_key == 'u':
            weekday = int(found_dict['u'])
            weekday -= 1
        lasivyo group_key == 'j':
            julian = int(found_dict['j'])
        lasivyo group_key kwenye ('U', 'W'):
            week_of_year = int(found_dict[group_key])
            ikiwa group_key == 'U':
                # U starts week on Sunday.
                week_of_year_start = 6
            isipokua:
                # W starts week on Monday.
                week_of_year_start = 0
        lasivyo group_key == 'V':
            iso_week = int(found_dict['V'])
        lasivyo group_key == 'z':
            z = found_dict['z']
            ikiwa z == 'Z':
                gmtoff = 0
            isipokua:
                ikiwa z[3] == ':':
                    z = z[:3] + z[4:]
                    ikiwa len(z) > 5:
                        ikiwa z[5] != ':':
                            msg = f"Inconsistent use of : kwenye {found_dict['z']}"
                            ashiria ValueError(msg)
                        z = z[:5] + z[6:]
                hours = int(z[1:3])
                minutes = int(z[3:5])
                seconds = int(z[5:7] ama 0)
                gmtoff = (hours * 60 * 60) + (minutes * 60) + seconds
                gmtoff_remainder = z[8:]
                # Pad to always rudisha microseconds.
                gmtoff_remainder_padding = "0" * (6 - len(gmtoff_remainder))
                gmtoff_fraction = int(gmtoff_remainder + gmtoff_remainder_padding)
                ikiwa z.startswith("-"):
                    gmtoff = -gmtoff
                    gmtoff_fraction = -gmtoff_fraction
        lasivyo group_key == 'Z':
            # Since -1 ni default value only need to worry about setting tz if
            # it can be something other than -1.
            found_zone = found_dict['Z'].lower()
            kila value, tz_values kwenye enumerate(locale_time.timezone):
                ikiwa found_zone kwenye tz_values:
                    # Deal ukijumuisha bad locale setup where timezone names are the
                    # same na yet time.daylight ni true; too ambiguous to
                    # be able to tell what timezone has daylight savings
                    ikiwa (time.tzname[0] == time.tzname[1] na
                       time.daylight na found_zone haiko kwenye ("utc", "gmt")):
                        koma
                    isipokua:
                        tz = value
                        koma
    # Deal ukijumuisha the cases where ambiguities arize
    # don't assume default values kila ISO week/year
    ikiwa year ni Tupu na iso_year ni sio Tupu:
        ikiwa iso_week ni Tupu ama weekday ni Tupu:
            ashiria ValueError("ISO year directive '%G' must be used ukijumuisha "
                             "the ISO week directive '%V' na a weekday "
                             "directive ('%A', '%a', '%w', ama '%u').")
        ikiwa julian ni sio Tupu:
            ashiria ValueError("Day of the year directive '%j' ni sio "
                             "compatible ukijumuisha ISO year directive '%G'. "
                             "Use '%Y' instead.")
    lasivyo week_of_year ni Tupu na iso_week ni sio Tupu:
        ikiwa weekday ni Tupu:
            ashiria ValueError("ISO week directive '%V' must be used ukijumuisha "
                             "the ISO year directive '%G' na a weekday "
                             "directive ('%A', '%a', '%w', ama '%u').")
        isipokua:
            ashiria ValueError("ISO week directive '%V' ni incompatible ukijumuisha "
                             "the year directive '%Y'. Use the ISO year '%G' "
                             "instead.")

    leap_year_fix = Uongo
    ikiwa year ni Tupu na month == 2 na day == 29:
        year = 1904  # 1904 ni first leap year of 20th century
        leap_year_fix = Kweli
    lasivyo year ni Tupu:
        year = 1900


    # If we know the week of the year na what day of that week, we can figure
    # out the Julian day of the year.
    ikiwa julian ni Tupu na weekday ni sio Tupu:
        ikiwa week_of_year ni sio Tupu:
            week_starts_Mon = Kweli ikiwa week_of_year_start == 0 isipokua Uongo
            julian = _calc_julian_from_U_or_W(year, week_of_year, weekday,
                                                week_starts_Mon)
        lasivyo iso_year ni sio Tupu na iso_week ni sio Tupu:
            year, julian = _calc_julian_from_V(iso_year, iso_week, weekday + 1)
        ikiwa julian ni sio Tupu na julian <= 0:
            year -= 1
            yday = 366 ikiwa calendar.isleap(year) isipokua 365
            julian += yday

    ikiwa julian ni Tupu:
        # Cansio pre-calculate datetime_date() since can change kwenye Julian
        # calculation na thus could have different value kila the day of
        # the week calculation.
        # Need to add 1 to result since first day of the year ni 1, sio 0.
        julian = datetime_date(year, month, day).toordinal() - \
                  datetime_date(year, 1, 1).toordinal() + 1
    isipokua:  # Assume that ikiwa they bothered to include Julian day (or ikiwa it was
           # calculated above ukijumuisha year/week/weekday) it will be accurate.
        datetime_result = datetime_date.fromordinal(
                            (julian - 1) +
                            datetime_date(year, 1, 1).toordinal())
        year = datetime_result.year
        month = datetime_result.month
        day = datetime_result.day
    ikiwa weekday ni Tupu:
        weekday = datetime_date(year, month, day).weekday()
    # Add timezone info
    tzname = found_dict.get("Z")

    ikiwa leap_year_fix:
        # the caller didn't supply a year but asked kila Feb 29th. We couldn't
        # use the default of 1900 kila computations. We set it back to ensure
        # that February 29th ni smaller than March 1st.
        year = 1900

    rudisha (year, month, day,
            hour, minute, second,
            weekday, julian, tz, tzname, gmtoff), fraction, gmtoff_fraction

eleza _strptime_time(data_string, format="%a %b %d %H:%M:%S %Y"):
    """Return a time struct based on the input string na the
    format string."""
    tt = _strptime(data_string, format)[0]
    rudisha time.struct_time(tt[:time._STRUCT_TM_ITEMS])

eleza _strptime_datetime(cls, data_string, format="%a %b %d %H:%M:%S %Y"):
    """Return a kundi cls instance based on the input string na the
    format string."""
    tt, fraction, gmtoff_fraction = _strptime(data_string, format)
    tzname, gmtoff = tt[-2:]
    args = tt[:6] + (fraction,)
    ikiwa gmtoff ni sio Tupu:
        tzdelta = datetime_timedelta(seconds=gmtoff, microseconds=gmtoff_fraction)
        ikiwa tzname:
            tz = datetime_timezone(tzdelta, tzname)
        isipokua:
            tz = datetime_timezone(tzdelta)
        args += (tz,)

    rudisha cls(*args)
