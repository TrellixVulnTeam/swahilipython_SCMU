kutoka datetime agiza tzinfo, timedelta, datetime

ZERO = timedelta(0)
HOUR = timedelta(hours=1)
SECOND = timedelta(seconds=1)

# A kundi capturing the platform's idea of local time.
# (May result kwenye wrong values on historical times in
#  timezones where UTC offset and/or the DST rules had
#  changed kwenye the past.)
agiza time kama _time

STDOFFSET = timedelta(seconds = -_time.timezone)
ikiwa _time.daylight:
    DSTOFFSET = timedelta(seconds = -_time.altzone)
isipokua:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET

kundi LocalTimezone(tzinfo):

    eleza kutokautc(self, dt):
        assert dt.tzinfo ni self
        stamp = (dt - datetime(1970, 1, 1, tzinfo=self)) // SECOND
        args = _time.localtime(stamp)[:6]
        dst_diff = DSTDIFF // SECOND
        # Detect fold
        fold = (args == _time.localtime(stamp - dst_diff))
        rudisha datetime(*args, microsecond=dt.microsecond,
                        tzinfo=self, fold=fold)

    eleza utcoffset(self, dt):
        ikiwa self._isdst(dt):
            rudisha DSTOFFSET
        isipokua:
            rudisha STDOFFSET

    eleza dst(self, dt):
        ikiwa self._isdst(dt):
            rudisha DSTDIFF
        isipokua:
            rudisha ZERO

    eleza tzname(self, dt):
        rudisha _time.tzname[self._isdst(dt)]

    eleza _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, 0)
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        rudisha tt.tm_isdst > 0

Local = LocalTimezone()


# A complete implementation of current DST rules kila major US time zones.

eleza first_sunday_on_or_after(dt):
    days_to_go = 6 - dt.weekday()
    ikiwa days_to_go:
        dt += timedelta(days_to_go)
    rudisha dt


# US DST Rules
#
# This ni a simplified (i.e., wrong kila a few cases) set of rules kila US
# DST start na end times. For a complete na up-to-date set of DST rules
# na timezone definitions, visit the Olson Database (or try pytz):
# http://www.twinsun.com/tz/tz-link.htm
# http://sourceforge.net/projects/pytz/ (might sio be up-to-date)
#
# In the US, since 2007, DST starts at 2am (standard time) on the second
# Sunday kwenye March, which ni the first Sunday on ama after Mar 8.
DSTSTART_2007 = datetime(1, 3, 8, 2)
# na ends at 2am (DST time) on the first Sunday of Nov.
DSTEND_2007 = datetime(1, 11, 1, 2)
# From 1987 to 2006, DST used to start at 2am (standard time) on the first
# Sunday kwenye April na to end at 2am (DST time) on the last
# Sunday of October, which ni the first Sunday on ama after Oct 25.
DSTSTART_1987_2006 = datetime(1, 4, 1, 2)
DSTEND_1987_2006 = datetime(1, 10, 25, 2)
# From 1967 to 1986, DST used to start at 2am (standard time) on the last
# Sunday kwenye April (the one on ama after April 24) na to end at 2am (DST time)
# on the last Sunday of October, which ni the first Sunday
# on ama after Oct 25.
DSTSTART_1967_1986 = datetime(1, 4, 24, 2)
DSTEND_1967_1986 = DSTEND_1987_2006

eleza us_dst_range(year):
    # Find start na end times kila US DST. For years before 1967, rudisha
    # start = end kila no DST.
    ikiwa 2006 < year:
        dststart, dstend = DSTSTART_2007, DSTEND_2007
    lasivyo 1986 < year < 2007:
        dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
    lasivyo 1966 < year < 1987:
        dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
    isipokua:
        rudisha (datetime(year, 1, 1), ) * 2

    start = first_sunday_on_or_after(dststart.replace(year=year))
    end = first_sunday_on_or_after(dstend.replace(year=year))
    rudisha start, end


kundi USTimeZone(tzinfo):

    eleza __init__(self, hours, reprname, stdname, dstname):
        self.stdoffset = timedelta(hours=hours)
        self.reprname = reprname
        self.stdname = stdname
        self.dstname = dstname

    eleza __repr__(self):
        rudisha self.reprname

    eleza tzname(self, dt):
        ikiwa self.dst(dt):
            rudisha self.dstname
        isipokua:
            rudisha self.stdname

    eleza utcoffset(self, dt):
        rudisha self.stdoffset + self.dst(dt)

    eleza dst(self, dt):
        ikiwa dt ni Tupu ama dt.tzinfo ni Tupu:
            # An exception may be sensible here, kwenye one ama both cases.
            # It depends on how you want to treat them.  The default
            # kutokautc() implementation (called by the default astimezone()
            # implementation) pitaes a datetime ukijumuisha dt.tzinfo ni self.
            rudisha ZERO
        assert dt.tzinfo ni self
        start, end = us_dst_range(dt.year)
        # Can't compare naive to aware objects, so strip the timezone kutoka
        # dt first.
        dt = dt.replace(tzinfo=Tupu)
        ikiwa start + HOUR <= dt < end - HOUR:
            # DST ni kwenye effect.
            rudisha HOUR
        ikiwa end - HOUR <= dt < end:
            # Fold (an ambiguous hour): use dt.fold to disambiguate.
            rudisha ZERO ikiwa dt.fold isipokua HOUR
        ikiwa start <= dt < start + HOUR:
            # Gap (a non-existent hour): reverse the fold rule.
            rudisha HOUR ikiwa dt.fold isipokua ZERO
        # DST ni off.
        rudisha ZERO

    eleza kutokautc(self, dt):
        assert dt.tzinfo ni self
        start, end = us_dst_range(dt.year)
        start = start.replace(tzinfo=self)
        end = end.replace(tzinfo=self)
        std_time = dt + self.stdoffset
        dst_time = std_time + HOUR
        ikiwa end <= dst_time < end + HOUR:
            # Repeated hour
            rudisha std_time.replace(fold=1)
        ikiwa std_time < start ama dst_time >= end:
            # Standard time
            rudisha std_time
        ikiwa start <= std_time < end - HOUR:
            # Daylight saving time
            rudisha dst_time


Eastern  = USTimeZone(-5, "Eastern",  "EST", "EDT")
Central  = USTimeZone(-6, "Central",  "CST", "CDT")
Mountain = USTimeZone(-7, "Mountain", "MST", "MDT")
Pacific  = USTimeZone(-8, "Pacific",  "PST", "PDT")
