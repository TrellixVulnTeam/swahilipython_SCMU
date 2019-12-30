# Copyright (C) 2002-2007 Python Software Foundation
# Contact: email-sig@python.org

"""Email address parsing code.

Lifted directly kutoka rfc822.py.  This should eventually be rewritten.
"""

__all__ = [
    'mktime_tz',
    'parsedate',
    'parsedate_tz',
    'quote',
    ]

agiza time, calendar

SPACE = ' '
EMPTYSTRING = ''
COMMASPACE = ', '

# Parse a date field
_monthnames = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul',
               'aug', 'sep', 'oct', 'nov', 'dec',
               'january', 'february', 'march', 'april', 'may', 'june', 'july',
               'august', 'september', 'october', 'november', 'december']

_daynames = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

# The timezone table does sio include the military time zones defined
# kwenye RFC822, other than Z.  According to RFC1123, the description in
# RFC822 gets the signs wrong, so we can't rely on any such time
# zones.  RFC1123 recommends that numeric timezone indicators be used
# instead of timezone names.

_timezones = {'UT':0, 'UTC':0, 'GMT':0, 'Z':0,
              'AST': -400, 'ADT': -300,  # Atlantic (used kwenye Canada)
              'EST': -500, 'EDT': -400,  # Eastern
              'CST': -600, 'CDT': -500,  # Central
              'MST': -700, 'MDT': -600,  # Mountain
              'PST': -800, 'PDT': -700   # Pacific
              }


eleza parsedate_tz(data):
    """Convert a date string to a time tuple.

    Accounts kila military timezones.
    """
    res = _parsedate_tz(data)
    ikiwa sio res:
        return
    ikiwa res[9] ni Tupu:
        res[9] = 0
    rudisha tuple(res)

eleza _parsedate_tz(data):
    """Convert date to extended time tuple.

    The last (additional) element ni the time zone offset kwenye seconds, tatizo if
    the timezone was specified kama -0000.  In that case the last element is
    Tupu.  This indicates a UTC timestamp that explicitly declaims knowledge of
    the source timezone, kama opposed to a +0000 timestamp that indicates the
    source timezone really was UTC.

    """
    ikiwa sio data:
        return
    data = data.split()
    # The FWS after the comma after the day-of-week ni optional, so search na
    # adjust kila this.
    ikiwa data[0].endswith(',') ama data[0].lower() kwenye _daynames:
        # There's a dayname here. Skip it
        toa data[0]
    isipokua:
        i = data[0].rfind(',')
        ikiwa i >= 0:
            data[0] = data[0][i+1:]
    ikiwa len(data) == 3: # RFC 850 date, deprecated
        stuff = data[0].split('-')
        ikiwa len(stuff) == 3:
            data = stuff + data[1:]
    ikiwa len(data) == 4:
        s = data[3]
        i = s.find('+')
        ikiwa i == -1:
            i = s.find('-')
        ikiwa i > 0:
            data[3:] = [s[:i], s[i:]]
        isipokua:
            data.append('') # Dummy tz
    ikiwa len(data) < 5:
        rudisha Tupu
    data = data[:5]
    [dd, mm, yy, tm, tz] = data
    mm = mm.lower()
    ikiwa mm haiko kwenye _monthnames:
        dd, mm = mm, dd.lower()
        ikiwa mm haiko kwenye _monthnames:
            rudisha Tupu
    mm = _monthnames.index(mm) + 1
    ikiwa mm > 12:
        mm -= 12
    ikiwa dd[-1] == ',':
        dd = dd[:-1]
    i = yy.find(':')
    ikiwa i > 0:
        yy, tm = tm, yy
    ikiwa yy[-1] == ',':
        yy = yy[:-1]
    ikiwa sio yy[0].isdigit():
        yy, tz = tz, yy
    ikiwa tm[-1] == ',':
        tm = tm[:-1]
    tm = tm.split(':')
    ikiwa len(tm) == 2:
        [thh, tmm] = tm
        tss = '0'
    lasivyo len(tm) == 3:
        [thh, tmm, tss] = tm
    lasivyo len(tm) == 1 na '.' kwenye tm[0]:
        # Some non-compliant MUAs use '.' to separate time elements.
        tm = tm[0].split('.')
        ikiwa len(tm) == 2:
            [thh, tmm] = tm
            tss = 0
        lasivyo len(tm) == 3:
            [thh, tmm, tss] = tm
    isipokua:
        rudisha Tupu
    jaribu:
        yy = int(yy)
        dd = int(dd)
        thh = int(thh)
        tmm = int(tmm)
        tss = int(tss)
    tatizo ValueError:
        rudisha Tupu
    # Check kila a yy specified kwenye two-digit format, then convert it to the
    # appropriate four-digit format, according to the POSIX standard. RFC 822
    # calls kila a two-digit yy, but RFC 2822 (which obsoletes RFC 822)
    # mandates a 4-digit yy. For more information, see the documentation for
    # the time module.
    ikiwa yy < 100:
        # The year ni between 1969 na 1999 (inclusive).
        ikiwa yy > 68:
            yy += 1900
        # The year ni between 2000 na 2068 (inclusive).
        isipokua:
            yy += 2000
    tzoffset = Tupu
    tz = tz.upper()
    ikiwa tz kwenye _timezones:
        tzoffset = _timezones[tz]
    isipokua:
        jaribu:
            tzoffset = int(tz)
        tatizo ValueError:
            pita
        ikiwa tzoffset==0 na tz.startswith('-'):
            tzoffset = Tupu
    # Convert a timezone offset into seconds ; -0500 -> -18000
    ikiwa tzoffset:
        ikiwa tzoffset < 0:
            tzsign = -1
            tzoffset = -tzoffset
        isipokua:
            tzsign = 1
        tzoffset = tzsign * ( (tzoffset//100)*3600 + (tzoffset % 100)*60)
    # Daylight Saving Time flag ni set to -1, since DST ni unknown.
    rudisha [yy, mm, dd, thh, tmm, tss, 0, 1, -1, tzoffset]


eleza parsedate(data):
    """Convert a time string to a time tuple."""
    t = parsedate_tz(data)
    ikiwa isinstance(t, tuple):
        rudisha t[:9]
    isipokua:
        rudisha t


eleza mktime_tz(data):
    """Turn a 10-tuple kama returned by parsedate_tz() into a POSIX timestamp."""
    ikiwa data[9] ni Tupu:
        # No zone info, so localtime ni better assumption than GMT
        rudisha time.mktime(data[:8] + (-1,))
    isipokua:
        t = calendar.timegm(data)
        rudisha t - data[9]


eleza quote(str):
    """Prepare string to be used kwenye a quoted string.

    Turns backslash na double quote characters into quoted pairs.  These
    are the only characters that need to be quoted inside a quoted string.
    Does sio add the surrounding double quotes.
    """
    rudisha str.replace('\\', '\\\\').replace('"', '\\"')


kundi AddrlistClass:
    """Address parser kundi by Ben Escoto.

    To understand what this kundi does, it helps to have a copy of RFC 2822 in
    front of you.

    Note: this kundi interface ni deprecated na may be removed kwenye the future.
    Use email.utils.AddressList instead.
    """

    eleza __init__(self, field):
        """Initialize a new instance.

        `field' ni an unparsed address header field, containing
        one ama more addresses.
        """
        self.specials = '()<>@,:;.\"[]'
        self.pos = 0
        self.LWS = ' \t'
        self.CR = '\r\n'
        self.FWS = self.LWS + self.CR
        self.atomends = self.specials + self.LWS + self.CR
        # Note that RFC 2822 now specifies `.' kama obs-phrase, meaning that it
        # ni obsolete syntax.  RFC 2822 requires that we recognize obsolete
        # syntax, so allow dots kwenye phrases.
        self.phraseends = self.atomends.replace('.', '')
        self.field = field
        self.commentlist = []

    eleza gotonext(self):
        """Skip white space na extract comments."""
        wslist = []
        wakati self.pos < len(self.field):
            ikiwa self.field[self.pos] kwenye self.LWS + '\n\r':
                ikiwa self.field[self.pos] haiko kwenye '\n\r':
                    wslist.append(self.field[self.pos])
                self.pos += 1
            lasivyo self.field[self.pos] == '(':
                self.commentlist.append(self.getcomment())
            isipokua:
                koma
        rudisha EMPTYSTRING.join(wslist)

    eleza getaddrlist(self):
        """Parse all addresses.

        Returns a list containing all of the addresses.
        """
        result = []
        wakati self.pos < len(self.field):
            ad = self.getaddress()
            ikiwa ad:
                result += ad
            isipokua:
                result.append(('', ''))
        rudisha result

    eleza getaddress(self):
        """Parse the next address."""
        self.commentlist = []
        self.gotonext()

        oldpos = self.pos
        oldcl = self.commentlist
        plist = self.getphraselist()

        self.gotonext()
        returnlist = []

        ikiwa self.pos >= len(self.field):
            # Bad email address technically, no domain.
            ikiwa plist:
                returnlist = [(SPACE.join(self.commentlist), plist[0])]

        lasivyo self.field[self.pos] kwenye '.@':
            # email address ni just an addrspec
            # this isn't very efficient since we start over
            self.pos = oldpos
            self.commentlist = oldcl
            addrspec = self.getaddrspec()
            returnlist = [(SPACE.join(self.commentlist), addrspec)]

        lasivyo self.field[self.pos] == ':':
            # address ni a group
            returnlist = []

            fieldlen = len(self.field)
            self.pos += 1
            wakati self.pos < len(self.field):
                self.gotonext()
                ikiwa self.pos < fieldlen na self.field[self.pos] == ';':
                    self.pos += 1
                    koma
                returnlist = returnlist + self.getaddress()

        lasivyo self.field[self.pos] == '<':
            # Address ni a phrase then a route addr
            routeaddr = self.getrouteaddr()

            ikiwa self.commentlist:
                returnlist = [(SPACE.join(plist) + ' (' +
                               ' '.join(self.commentlist) + ')', routeaddr)]
            isipokua:
                returnlist = [(SPACE.join(plist), routeaddr)]

        isipokua:
            ikiwa plist:
                returnlist = [(SPACE.join(self.commentlist), plist[0])]
            lasivyo self.field[self.pos] kwenye self.specials:
                self.pos += 1

        self.gotonext()
        ikiwa self.pos < len(self.field) na self.field[self.pos] == ',':
            self.pos += 1
        rudisha returnlist

    eleza getrouteaddr(self):
        """Parse a route address (Return-path value).

        This method just skips all the route stuff na returns the addrspec.
        """
        ikiwa self.field[self.pos] != '<':
            return

        expectroute = Uongo
        self.pos += 1
        self.gotonext()
        adlist = ''
        wakati self.pos < len(self.field):
            ikiwa expectroute:
                self.getdomain()
                expectroute = Uongo
            lasivyo self.field[self.pos] == '>':
                self.pos += 1
                koma
            lasivyo self.field[self.pos] == '@':
                self.pos += 1
                expectroute = Kweli
            lasivyo self.field[self.pos] == ':':
                self.pos += 1
            isipokua:
                adlist = self.getaddrspec()
                self.pos += 1
                koma
            self.gotonext()

        rudisha adlist

    eleza getaddrspec(self):
        """Parse an RFC 2822 addr-spec."""
        aslist = []

        self.gotonext()
        wakati self.pos < len(self.field):
            preserve_ws = Kweli
            ikiwa self.field[self.pos] == '.':
                ikiwa aslist na sio aslist[-1].strip():
                    aslist.pop()
                aslist.append('.')
                self.pos += 1
                preserve_ws = Uongo
            lasivyo self.field[self.pos] == '"':
                aslist.append('"%s"' % quote(self.getquote()))
            lasivyo self.field[self.pos] kwenye self.atomends:
                ikiwa aslist na sio aslist[-1].strip():
                    aslist.pop()
                koma
            isipokua:
                aslist.append(self.getatom())
            ws = self.gotonext()
            ikiwa preserve_ws na ws:
                aslist.append(ws)

        ikiwa self.pos >= len(self.field) ama self.field[self.pos] != '@':
            rudisha EMPTYSTRING.join(aslist)

        aslist.append('@')
        self.pos += 1
        self.gotonext()
        domain = self.getdomain()
        ikiwa sio domain:
            # Invalid domain, rudisha an empty address instead of returning a
            # local part to denote failed parsing.
            rudisha EMPTYSTRING
        rudisha EMPTYSTRING.join(aslist) + domain

    eleza getdomain(self):
        """Get the complete domain name kutoka an address."""
        sdlist = []
        wakati self.pos < len(self.field):
            ikiwa self.field[self.pos] kwenye self.LWS:
                self.pos += 1
            lasivyo self.field[self.pos] == '(':
                self.commentlist.append(self.getcomment())
            lasivyo self.field[self.pos] == '[':
                sdlist.append(self.getdomainliteral())
            lasivyo self.field[self.pos] == '.':
                self.pos += 1
                sdlist.append('.')
            lasivyo self.field[self.pos] == '@':
                # bpo-34155: Don't parse domains ukijumuisha two `@` like
                # `a@malicious.org@important.com`.
                rudisha EMPTYSTRING
            lasivyo self.field[self.pos] kwenye self.atomends:
                koma
            isipokua:
                sdlist.append(self.getatom())
        rudisha EMPTYSTRING.join(sdlist)

    eleza getdelimited(self, beginchar, endchars, allowcomments=Kweli):
        """Parse a header fragment delimited by special characters.

        `beginchar' ni the start character kila the fragment.
        If self ni sio looking at an instance of `beginchar' then
        getdelimited returns the empty string.

        `endchars' ni a sequence of allowable end-delimiting characters.
        Parsing stops when one of these ni encountered.

        If `allowcomments' ni non-zero, embedded RFC 2822 comments are allowed
        within the parsed fragment.
        """
        ikiwa self.field[self.pos] != beginchar:
            rudisha ''

        slist = ['']
        quote = Uongo
        self.pos += 1
        wakati self.pos < len(self.field):
            ikiwa quote:
                slist.append(self.field[self.pos])
                quote = Uongo
            lasivyo self.field[self.pos] kwenye endchars:
                self.pos += 1
                koma
            lasivyo allowcomments na self.field[self.pos] == '(':
                slist.append(self.getcomment())
                endelea        # have already advanced pos kutoka getcomment
            lasivyo self.field[self.pos] == '\\':
                quote = Kweli
            isipokua:
                slist.append(self.field[self.pos])
            self.pos += 1

        rudisha EMPTYSTRING.join(slist)

    eleza getquote(self):
        """Get a quote-delimited fragment kutoka self's field."""
        rudisha self.getdelimited('"', '"\r', Uongo)

    eleza getcomment(self):
        """Get a parenthesis-delimited fragment kutoka self's field."""
        rudisha self.getdelimited('(', ')\r', Kweli)

    eleza getdomainliteral(self):
        """Parse an RFC 2822 domain-literal."""
        rudisha '[%s]' % self.getdelimited('[', ']\r', Uongo)

    eleza getatom(self, atomends=Tupu):
        """Parse an RFC 2822 atom.

        Optional atomends specifies a different set of end token delimiters
        (the default ni to use self.atomends).  This ni used e.g. in
        getphraselist() since phrase endings must sio include the `.' (which
        ni legal kwenye phrases)."""
        atomlist = ['']
        ikiwa atomends ni Tupu:
            atomends = self.atomends

        wakati self.pos < len(self.field):
            ikiwa self.field[self.pos] kwenye atomends:
                koma
            isipokua:
                atomlist.append(self.field[self.pos])
            self.pos += 1

        rudisha EMPTYSTRING.join(atomlist)

    eleza getphraselist(self):
        """Parse a sequence of RFC 2822 phrases.

        A phrase ni a sequence of words, which are kwenye turn either RFC 2822
        atoms ama quoted-strings.  Phrases are canonicalized by squeezing all
        runs of continuous whitespace into one space.
        """
        plist = []

        wakati self.pos < len(self.field):
            ikiwa self.field[self.pos] kwenye self.FWS:
                self.pos += 1
            lasivyo self.field[self.pos] == '"':
                plist.append(self.getquote())
            lasivyo self.field[self.pos] == '(':
                self.commentlist.append(self.getcomment())
            lasivyo self.field[self.pos] kwenye self.phraseends:
                koma
            isipokua:
                plist.append(self.getatom(self.phraseends))

        rudisha plist

kundi AddressList(AddrlistClass):
    """An AddressList encapsulates a list of parsed RFC 2822 addresses."""
    eleza __init__(self, field):
        AddrlistClass.__init__(self, field)
        ikiwa field:
            self.addresslist = self.getaddrlist()
        isipokua:
            self.addresslist = []

    eleza __len__(self):
        rudisha len(self.addresslist)

    eleza __add__(self, other):
        # Set union
        newaddr = AddressList(Tupu)
        newaddr.addresslist = self.addresslist[:]
        kila x kwenye other.addresslist:
            ikiwa sio x kwenye self.addresslist:
                newaddr.addresslist.append(x)
        rudisha newaddr

    eleza __iadd__(self, other):
        # Set union, in-place
        kila x kwenye other.addresslist:
            ikiwa sio x kwenye self.addresslist:
                self.addresslist.append(x)
        rudisha self

    eleza __sub__(self, other):
        # Set difference
        newaddr = AddressList(Tupu)
        kila x kwenye self.addresslist:
            ikiwa sio x kwenye other.addresslist:
                newaddr.addresslist.append(x)
        rudisha newaddr

    eleza __isub__(self, other):
        # Set difference, in-place
        kila x kwenye other.addresslist:
            ikiwa x kwenye self.addresslist:
                self.addresslist.remove(x)
        rudisha self

    eleza __getitem__(self, index):
        # Make indexing, slices, na 'in' work
        rudisha self.addresslist[index]
