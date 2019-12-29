"""Calendar printing functions

Note when comparing these calendars to the ones printed by cal(1): By
default, these calendars have Monday kama the first day of the week, and
Sunday kama the last (the European convention). Use setfirstweekday() to
set the first day of the week (0=Monday, 6=Sunday)."""

agiza sys
agiza datetime
agiza locale kama _locale
kutoka itertools agiza repeat

__all__ = ["IllegalMonthError", "IllegalWeekdayError", "setfirstweekday",
           "firstweekday", "isleap", "leapdays", "weekday", "monthrange",
           "monthcalendar", "prmonth", "month", "prcal", "calendar",
           "timegm", "month_name", "month_abbr", "day_name", "day_abbr",
           "Calendar", "TextCalendar", "HTMLCalendar", "LocaleTextCalendar",
           "LocaleHTMLCalendar", "weekheader"]

# Exception ashiriad kila bad input (ukijumuisha string parameter kila details)
error = ValueError

# Exceptions ashiriad kila bad input
kundi IllegalMonthError(ValueError):
    eleza __init__(self, month):
        self.month = month
    eleza __str__(self):
        rudisha "bad month number %r; must be 1-12" % self.month


kundi IllegalWeekdayError(ValueError):
    eleza __init__(self, weekday):
        self.weekday = weekday
    eleza __str__(self):
        rudisha "bad weekday number %r; must be 0 (Monday) to 6 (Sunday)" % self.weekday


# Constants kila months referenced later
January = 1
February = 2

# Number of days per month (tatizo kila February kwenye leap years)
mdays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

# This module used to have hard-coded lists of day na month names, as
# English strings.  The classes following emulate a read-only version of
# that, but supply localized names.  Note that the values are computed
# fresh on each call, kwenye case the user changes locale between calls.

kundi _localized_month:

    _months = [datetime.date(2001, i+1, 1).strftime kila i kwenye range(12)]
    _months.insert(0, lambda x: "")

    eleza __init__(self, format):
        self.format = format

    eleza __getitem__(self, i):
        funcs = self._months[i]
        ikiwa isinstance(i, slice):
            rudisha [f(self.format) kila f kwenye funcs]
        isipokua:
            rudisha funcs(self.format)

    eleza __len__(self):
        rudisha 13


kundi _localized_day:

    # January 1, 2001, was a Monday.
    _days = [datetime.date(2001, 1, i+1).strftime kila i kwenye range(7)]

    eleza __init__(self, format):
        self.format = format

    eleza __getitem__(self, i):
        funcs = self._days[i]
        ikiwa isinstance(i, slice):
            rudisha [f(self.format) kila f kwenye funcs]
        isipokua:
            rudisha funcs(self.format)

    eleza __len__(self):
        rudisha 7


# Full na abbreviated names of weekdays
day_name = _localized_day('%A')
day_abbr = _localized_day('%a')

# Full na abbreviated names of months (1-based arrays!!!)
month_name = _localized_month('%B')
month_abbr = _localized_month('%b')

# Constants kila weekdays
(MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY) = range(7)


eleza isleap(year):
    """Return Kweli kila leap years, Uongo kila non-leap years."""
    rudisha year % 4 == 0 na (year % 100 != 0 ama year % 400 == 0)


eleza leapdays(y1, y2):
    """Return number of leap years kwenye range [y1, y2).
       Assume y1 <= y2."""
    y1 -= 1
    y2 -= 1
    rudisha (y2//4 - y1//4) - (y2//100 - y1//100) + (y2//400 - y1//400)


eleza weekday(year, month, day):
    """Return weekday (0-6 ~ Mon-Sun) kila year, month (1-12), day (1-31)."""
    ikiwa sio datetime.MINYEAR <= year <= datetime.MAXYEAR:
        year = 2000 + year % 400
    rudisha datetime.date(year, month, day).weekday()


eleza monthrange(year, month):
    """Return weekday (0-6 ~ Mon-Sun) na number of days (28-31) for
       year, month."""
    ikiwa sio 1 <= month <= 12:
        ashiria IllegalMonthError(month)
    day1 = weekday(year, month, 1)
    ndays = mdays[month] + (month == February na isleap(year))
    rudisha day1, ndays


eleza _monthlen(year, month):
    rudisha mdays[month] + (month == February na isleap(year))


eleza _prevmonth(year, month):
    ikiwa month == 1:
        rudisha year-1, 12
    isipokua:
        rudisha year, month-1


eleza _nextmonth(year, month):
    ikiwa month == 12:
        rudisha year+1, 1
    isipokua:
        rudisha year, month+1


kundi Calendar(object):
    """
    Base calendar class. This kundi doesn't do any formatting. It simply
    provides data to subclasses.
    """

    eleza __init__(self, firstweekday=0):
        self.firstweekday = firstweekday # 0 = Monday, 6 = Sunday

    eleza getfirstweekday(self):
        rudisha self._firstweekday % 7

    eleza setfirstweekday(self, firstweekday):
        self._firstweekday = firstweekday

    firstweekday = property(getfirstweekday, setfirstweekday)

    eleza iterweekdays(self):
        """
        Return an iterator kila one week of weekday numbers starting ukijumuisha the
        configured first one.
        """
        kila i kwenye range(self.firstweekday, self.firstweekday + 7):
            tuma i%7

    eleza itermonthdates(self, year, month):
        """
        Return an iterator kila one month. The iterator will tuma datetime.date
        values na will always iterate through complete weeks, so it will tuma
        dates outside the specified month.
        """
        kila y, m, d kwenye self.itermonthdays3(year, month):
            tuma datetime.date(y, m, d)

    eleza itermonthdays(self, year, month):
        """
        Like itermonthdates(), but will tuma day numbers. For days outside
        the specified month the day number ni 0.
        """
        day1, ndays = monthrange(year, month)
        days_before = (day1 - self.firstweekday) % 7
        tuma kutoka repeat(0, days_before)
        tuma kutoka range(1, ndays + 1)
        days_after = (self.firstweekday - day1 - ndays) % 7
        tuma kutoka repeat(0, days_after)

    eleza itermonthdays2(self, year, month):
        """
        Like itermonthdates(), but will tuma (day number, weekday number)
        tuples. For days outside the specified month the day number ni 0.
        """
        kila i, d kwenye enumerate(self.itermonthdays(year, month), self.firstweekday):
            tuma d, i % 7

    eleza itermonthdays3(self, year, month):
        """
        Like itermonthdates(), but will tuma (year, month, day) tuples.  Can be
        used kila dates outside of datetime.date range.
        """
        day1, ndays = monthrange(year, month)
        days_before = (day1 - self.firstweekday) % 7
        days_after = (self.firstweekday - day1 - ndays) % 7
        y, m = _prevmonth(year, month)
        end = _monthlen(y, m) + 1
        kila d kwenye range(end-days_before, end):
            tuma y, m, d
        kila d kwenye range(1, ndays + 1):
            tuma year, month, d
        y, m = _nextmonth(year, month)
        kila d kwenye range(1, days_after + 1):
            tuma y, m, d

    eleza itermonthdays4(self, year, month):
        """
        Like itermonthdates(), but will tuma (year, month, day, day_of_week) tuples.
        Can be used kila dates outside of datetime.date range.
        """
        kila i, (y, m, d) kwenye enumerate(self.itermonthdays3(year, month)):
            tuma y, m, d, (self.firstweekday + i) % 7

    eleza monthdatescalendar(self, year, month):
        """
        Return a matrix (list of lists) representing a month's calendar.
        Each row represents a week; week entries are datetime.date values.
        """
        dates = list(self.itermonthdates(year, month))
        rudisha [ dates[i:i+7] kila i kwenye range(0, len(dates), 7) ]

    eleza monthdays2calendar(self, year, month):
        """
        Return a matrix representing a month's calendar.
        Each row represents a week; week entries are
        (day number, weekday number) tuples. Day numbers outside this month
        are zero.
        """
        days = list(self.itermonthdays2(year, month))
        rudisha [ days[i:i+7] kila i kwenye range(0, len(days), 7) ]

    eleza monthdayscalendar(self, year, month):
        """
        Return a matrix representing a month's calendar.
        Each row represents a week; days outside this month are zero.
        """
        days = list(self.itermonthdays(year, month))
        rudisha [ days[i:i+7] kila i kwenye range(0, len(days), 7) ]

    eleza yeardatescalendar(self, year, width=3):
        """
        Return the data kila the specified year ready kila formatting. The rudisha
        value ni a list of month rows. Each month row contains up to width months.
        Each month contains between 4 na 6 weeks na each week contains 1-7
        days. Days are datetime.date objects.
        """
        months = [
            self.monthdatescalendar(year, i)
            kila i kwenye range(January, January+12)
        ]
        rudisha [months[i:i+width] kila i kwenye range(0, len(months), width) ]

    eleza yeardays2calendar(self, year, width=3):
        """
        Return the data kila the specified year ready kila formatting (similar to
        yeardatescalendar()). Entries kwenye the week lists are
        (day number, weekday number) tuples. Day numbers outside this month are
        zero.
        """
        months = [
            self.monthdays2calendar(year, i)
            kila i kwenye range(January, January+12)
        ]
        rudisha [months[i:i+width] kila i kwenye range(0, len(months), width) ]

    eleza yeardayscalendar(self, year, width=3):
        """
        Return the data kila the specified year ready kila formatting (similar to
        yeardatescalendar()). Entries kwenye the week lists are day numbers.
        Day numbers outside this month are zero.
        """
        months = [
            self.monthdayscalendar(year, i)
            kila i kwenye range(January, January+12)
        ]
        rudisha [months[i:i+width] kila i kwenye range(0, len(months), width) ]


kundi TextCalendar(Calendar):
    """
    Subkundi of Calendar that outputs a calendar kama a simple plain text
    similar to the UNIX program cal.
    """

    eleza prweek(self, theweek, width):
        """
        Print a single week (no newline).
        """
        andika(self.formatweek(theweek, width), end='')

    eleza formatday(self, day, weekday, width):
        """
        Returns a formatted day.
        """
        ikiwa day == 0:
            s = ''
        isipokua:
            s = '%2i' % day             # right-align single-digit days
        rudisha s.center(width)

    eleza formatweek(self, theweek, width):
        """
        Returns a single week kwenye a string (no newline).
        """
        rudisha ' '.join(self.formatday(d, wd, width) kila (d, wd) kwenye theweek)

    eleza formatweekday(self, day, width):
        """
        Returns a formatted week day name.
        """
        ikiwa width >= 9:
            names = day_name
        isipokua:
            names = day_abbr
        rudisha names[day][:width].center(width)

    eleza formatweekheader(self, width):
        """
        Return a header kila a week.
        """
        rudisha ' '.join(self.formatweekday(i, width) kila i kwenye self.iterweekdays())

    eleza formatmonthname(self, theyear, themonth, width, withyear=Kweli):
        """
        Return a formatted month name.
        """
        s = month_name[themonth]
        ikiwa withyear:
            s = "%s %r" % (s, theyear)
        rudisha s.center(width)

    eleza prmonth(self, theyear, themonth, w=0, l=0):
        """
        Print a month's calendar.
        """
        andika(self.formatmonth(theyear, themonth, w, l), end='')

    eleza formatmonth(self, theyear, themonth, w=0, l=0):
        """
        Return a month's calendar string (multi-line).
        """
        w = max(2, w)
        l = max(1, l)
        s = self.formatmonthname(theyear, themonth, 7 * (w + 1) - 1)
        s = s.rstrip()
        s += '\n' * l
        s += self.formatweekheader(w).rstrip()
        s += '\n' * l
        kila week kwenye self.monthdays2calendar(theyear, themonth):
            s += self.formatweek(week, w).rstrip()
            s += '\n' * l
        rudisha s

    eleza formatyear(self, theyear, w=2, l=1, c=6, m=3):
        """
        Returns a year's calendar kama a multi-line string.
        """
        w = max(2, w)
        l = max(1, l)
        c = max(2, c)
        colwidth = (w + 1) * 7 - 1
        v = []
        a = v.append
        a(repr(theyear).center(colwidth*m+c*(m-1)).rstrip())
        a('\n'*l)
        header = self.formatweekheader(w)
        kila (i, row) kwenye enumerate(self.yeardays2calendar(theyear, m)):
            # months kwenye this row
            months = range(m*i+1, min(m*(i+1)+1, 13))
            a('\n'*l)
            names = (self.formatmonthname(theyear, k, colwidth, Uongo)
                     kila k kwenye months)
            a(formatstring(names, colwidth, c).rstrip())
            a('\n'*l)
            headers = (header kila k kwenye months)
            a(formatstring(headers, colwidth, c).rstrip())
            a('\n'*l)
            # max number of weeks kila this row
            height = max(len(cal) kila cal kwenye row)
            kila j kwenye range(height):
                weeks = []
                kila cal kwenye row:
                    ikiwa j >= len(cal):
                        weeks.append('')
                    isipokua:
                        weeks.append(self.formatweek(cal[j], w))
                a(formatstring(weeks, colwidth, c).rstrip())
                a('\n' * l)
        rudisha ''.join(v)

    eleza pryear(self, theyear, w=0, l=0, c=6, m=3):
        """Print a year's calendar."""
        andika(self.formatyear(theyear, w, l, c, m), end='')


kundi HTMLCalendar(Calendar):
    """
    This calendar rudishas complete HTML pages.
    """

    # CSS classes kila the day <td>s
    cssclasses = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    # CSS classes kila the day <th>s
    cssclasses_weekday_head = cssclasses

    # CSS kundi kila the days before na after current month
    cssclass_noday = "noday"

    # CSS kundi kila the month's head
    cssclass_month_head = "month"

    # CSS kundi kila the month
    cssclass_month = "month"

    # CSS kundi kila the year's table head
    cssclass_year_head = "year"

    # CSS kundi kila the whole year table
    cssclass_year = "year"

    eleza formatday(self, day, weekday):
        """
        Return a day kama a table cell.
        """
        ikiwa day == 0:
            # day outside month
            rudisha '<td class="%s">&nbsp;</td>' % self.cssclass_noday
        isipokua:
            rudisha '<td class="%s">%d</td>' % (self.cssclasses[weekday], day)

    eleza formatweek(self, theweek):
        """
        Return a complete week kama a table row.
        """
        s = ''.join(self.formatday(d, wd) kila (d, wd) kwenye theweek)
        rudisha '<tr>%s</tr>' % s

    eleza formatweekday(self, day):
        """
        Return a weekday name kama a table header.
        """
        rudisha '<th class="%s">%s</th>' % (
            self.cssclasses_weekday_head[day], day_abbr[day])

    eleza formatweekheader(self):
        """
        Return a header kila a week kama a table row.
        """
        s = ''.join(self.formatweekday(i) kila i kwenye self.iterweekdays())
        rudisha '<tr>%s</tr>' % s

    eleza formatmonthname(self, theyear, themonth, withyear=Kweli):
        """
        Return a month name kama a table row.
        """
        ikiwa withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        isipokua:
            s = '%s' % month_name[themonth]
        rudisha '<tr><th colspan="7" class="%s">%s</th></tr>' % (
            self.cssclass_month_head, s)

    eleza formatmonth(self, theyear, themonth, withyear=Kweli):
        """
        Return a formatted month kama a table.
        """
        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="%s">' % (
            self.cssclass_month))
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        kila week kwenye self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</table>')
        a('\n')
        rudisha ''.join(v)

    eleza formatyear(self, theyear, width=3):
        """
        Return a formatted year kama a table of tables.
        """
        v = []
        a = v.append
        width = max(width, 1)
        a('<table border="0" cellpadding="0" cellspacing="0" class="%s">' %
          self.cssclass_year)
        a('\n')
        a('<tr><th colspan="%d" class="%s">%s</th></tr>' % (
            width, self.cssclass_year_head, theyear))
        kila i kwenye range(January, January+12, width):
            # months kwenye this row
            months = range(i, min(i+width, 13))
            a('<tr>')
            kila m kwenye months:
                a('<td>')
                a(self.formatmonth(theyear, m, withyear=Uongo))
                a('</td>')
            a('</tr>')
        a('</table>')
        rudisha ''.join(v)

    eleza formatyearpage(self, theyear, width=3, css='calendar.css', encoding=Tupu):
        """
        Return a formatted year kama a complete HTML page.
        """
        ikiwa encoding ni Tupu:
            encoding = sys.getdefaultencoding()
        v = []
        a = v.append
        a('<?xml version="1.0" encoding="%s"?>\n' % encoding)
        a('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        a('<html>\n')
        a('<head>\n')
        a('<meta http-equiv="Content-Type" content="text/html; charset=%s" />\n' % encoding)
        ikiwa css ni sio Tupu:
            a('<link rel="stylesheet" type="text/css" href="%s" />\n' % css)
        a('<title>Calendar kila %d</title>\n' % theyear)
        a('</head>\n')
        a('<body>\n')
        a(self.formatyear(theyear, width))
        a('</body>\n')
        a('</html>\n')
        rudisha ''.join(v).encode(encoding, "xmlcharrefreplace")


kundi different_locale:
    eleza __init__(self, locale):
        self.locale = locale

    eleza __enter__(self):
        self.oldlocale = _locale.getlocale(_locale.LC_TIME)
        _locale.setlocale(_locale.LC_TIME, self.locale)

    eleza __exit__(self, *args):
        _locale.setlocale(_locale.LC_TIME, self.oldlocale)


kundi LocaleTextCalendar(TextCalendar):
    """
    This kundi can be pitaed a locale name kwenye the constructor na will rudisha
    month na weekday names kwenye the specified locale. If this locale includes
    an encoding all strings containing month na weekday names will be rudishaed
    kama unicode.
    """

    eleza __init__(self, firstweekday=0, locale=Tupu):
        TextCalendar.__init__(self, firstweekday)
        ikiwa locale ni Tupu:
            locale = _locale.getdefaultlocale()
        self.locale = locale

    eleza formatweekday(self, day, width):
        ukijumuisha different_locale(self.locale):
            ikiwa width >= 9:
                names = day_name
            isipokua:
                names = day_abbr
            name = names[day]
            rudisha name[:width].center(width)

    eleza formatmonthname(self, theyear, themonth, width, withyear=Kweli):
        ukijumuisha different_locale(self.locale):
            s = month_name[themonth]
            ikiwa withyear:
                s = "%s %r" % (s, theyear)
            rudisha s.center(width)


kundi LocaleHTMLCalendar(HTMLCalendar):
    """
    This kundi can be pitaed a locale name kwenye the constructor na will rudisha
    month na weekday names kwenye the specified locale. If this locale includes
    an encoding all strings containing month na weekday names will be rudishaed
    kama unicode.
    """
    eleza __init__(self, firstweekday=0, locale=Tupu):
        HTMLCalendar.__init__(self, firstweekday)
        ikiwa locale ni Tupu:
            locale = _locale.getdefaultlocale()
        self.locale = locale

    eleza formatweekday(self, day):
        ukijumuisha different_locale(self.locale):
            s = day_abbr[day]
            rudisha '<th class="%s">%s</th>' % (self.cssclasses[day], s)

    eleza formatmonthname(self, theyear, themonth, withyear=Kweli):
        ukijumuisha different_locale(self.locale):
            s = month_name[themonth]
            ikiwa withyear:
                s = '%s %s' % (s, theyear)
            rudisha '<tr><th colspan="7" class="month">%s</th></tr>' % s


# Support kila old module level interface
c = TextCalendar()

firstweekday = c.getfirstweekday

eleza setfirstweekday(firstweekday):
    ikiwa sio MONDAY <= firstweekday <= SUNDAY:
        ashiria IllegalWeekdayError(firstweekday)
    c.firstweekday = firstweekday

monthcalendar = c.monthdayscalendar
prweek = c.prweek
week = c.formatweek
weekheader = c.formatweekheader
prmonth = c.prmonth
month = c.formatmonth
calendar = c.formatyear
prcal = c.pryear


# Spacing of month columns kila multi-column year calendar
_colwidth = 7*3 - 1         # Amount printed by prweek()
_spacing = 6                # Number of spaces between columns


eleza format(cols, colwidth=_colwidth, spacing=_spacing):
    """Prints multi-column formatting kila year calendars"""
    andika(formatstring(cols, colwidth, spacing))


eleza formatstring(cols, colwidth=_colwidth, spacing=_spacing):
    """Returns a string formatted kutoka n strings, centered within n columns."""
    spacing *= ' '
    rudisha spacing.join(c.center(colwidth) kila c kwenye cols)


EPOCH = 1970
_EPOCH_ORD = datetime.date(EPOCH, 1, 1).toordinal()


eleza timegm(tuple):
    """Unrelated but handy function to calculate Unix timestamp kutoka GMT."""
    year, month, day, hour, minute, second = tuple[:6]
    days = datetime.date(year, month, 1).toordinal() - _EPOCH_ORD + day - 1
    hours = days*24 + hour
    minutes = hours*60 + minute
    seconds = minutes*60 + second
    rudisha seconds


eleza main(args):
    agiza argparse
    parser = argparse.ArgumentParser()
    textgroup = parser.add_argument_group('text only arguments')
    htmlgroup = parser.add_argument_group('html only arguments')
    textgroup.add_argument(
        "-w", "--width",
        type=int, default=2,
        help="width of date column (default 2)"
    )
    textgroup.add_argument(
        "-l", "--lines",
        type=int, default=1,
        help="number of lines kila each week (default 1)"
    )
    textgroup.add_argument(
        "-s", "--spacing",
        type=int, default=6,
        help="spacing between months (default 6)"
    )
    textgroup.add_argument(
        "-m", "--months",
        type=int, default=3,
        help="months per row (default 3)"
    )
    htmlgroup.add_argument(
        "-c", "--css",
        default="calendar.css",
        help="CSS to use kila page"
    )
    parser.add_argument(
        "-L", "--locale",
        default=Tupu,
        help="locale to be used kutoka month na weekday names"
    )
    parser.add_argument(
        "-e", "--encoding",
        default=Tupu,
        help="encoding to use kila output"
    )
    parser.add_argument(
        "-t", "--type",
        default="text",
        choices=("text", "html"),
        help="output type (text ama html)"
    )
    parser.add_argument(
        "year",
        nargs='?', type=int,
        help="year number (1-9999)"
    )
    parser.add_argument(
        "month",
        nargs='?', type=int,
        help="month number (1-12, text only)"
    )

    options = parser.parse_args(args[1:])

    ikiwa options.locale na sio options.encoding:
        parser.error("ikiwa --locale ni specified --encoding ni required")
        sys.exit(1)

    locale = options.locale, options.encoding

    ikiwa options.type == "html":
        ikiwa options.locale:
            cal = LocaleHTMLCalendar(locale=locale)
        isipokua:
            cal = HTMLCalendar()
        encoding = options.encoding
        ikiwa encoding ni Tupu:
            encoding = sys.getdefaultencoding()
        optdict = dict(encoding=encoding, css=options.css)
        write = sys.stdout.buffer.write
        ikiwa options.year ni Tupu:
            write(cal.formatyearpage(datetime.date.today().year, **optdict))
        lasivyo options.month ni Tupu:
            write(cal.formatyearpage(options.year, **optdict))
        isipokua:
            parser.error("incorrect number of arguments")
            sys.exit(1)
    isipokua:
        ikiwa options.locale:
            cal = LocaleTextCalendar(locale=locale)
        isipokua:
            cal = TextCalendar()
        optdict = dict(w=options.width, l=options.lines)
        ikiwa options.month ni Tupu:
            optdict["c"] = options.spacing
            optdict["m"] = options.months
        ikiwa options.year ni Tupu:
            result = cal.formatyear(datetime.date.today().year, **optdict)
        lasivyo options.month ni Tupu:
            result = cal.formatyear(options.year, **optdict)
        isipokua:
            result = cal.formatmonth(options.year, options.month, **optdict)
        write = sys.stdout.write
        ikiwa options.encoding:
            result = result.encode(options.encoding)
            write = sys.stdout.buffer.write
        write(result)


ikiwa __name__ == "__main__":
    main(sys.argv)
