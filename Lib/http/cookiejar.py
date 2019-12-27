r"""HTTP cookie handling for web clients.

This module has (now fairly distant) origins in Gisle Aas' Perl module
HTTP::Cookies, kutoka the libwww-perl library.

Docstrings, comments and debug strings in this code refer to the
attributes of the HTTP cookie system as cookie-attributes, to distinguish
them clearly kutoka Python attributes.

Class diagram (note that BSDDBCookieJar and the MSIE* classes are not
distributed with the Python standard library, but are available kutoka
http://wwwsearch.sf.net/):

                        CookieJar____
                        /     \      \
            FileCookieJar      \      \
             /    |   \         \      \
 MozillaCookieJar | LWPCookieJar \      \
                  |               |      \
                  |   ---MSIEBase |       \
                  |  /      |     |        \
                  | /   MSIEDBCookieJar BSDDBCookieJar
                  |/
               MSIECookieJar

"""

__all__ = ['Cookie', 'CookieJar', 'CookiePolicy', 'DefaultCookiePolicy',
           'FileCookieJar', 'LWPCookieJar', 'LoadError', 'MozillaCookieJar']

agiza os
agiza copy
agiza datetime
agiza re
agiza time
agiza urllib.parse, urllib.request
agiza threading as _threading
agiza http.client  # only for the default HTTP port
kutoka calendar agiza timegm

debug = False   # set to True to enable debugging via the logging module
logger = None

eleza _debug(*args):
    ikiwa not debug:
        return
    global logger
    ikiwa not logger:
        agiza logging
        logger = logging.getLogger("http.cookiejar")
    rudisha logger.debug(*args)


DEFAULT_HTTP_PORT = str(http.client.HTTP_PORT)
MISSING_FILENAME_TEXT = ("a filename was not supplied (nor was the CookieJar "
                         "instance initialised with one)")

eleza _warn_unhandled_exception():
    # There are a few catch-all except: statements in this module, for
    # catching input that's bad in unexpected ways.  Warn ikiwa any
    # exceptions are caught there.
    agiza io, warnings, traceback
    f = io.StringIO()
    traceback.print_exc(None, f)
    msg = f.getvalue()
    warnings.warn("http.cookiejar bug!\n%s" % msg, stacklevel=2)


# Date/time conversion
# -----------------------------------------------------------------------------

EPOCH_YEAR = 1970
eleza _timegm(tt):
    year, month, mday, hour, min, sec = tt[:6]
    ikiwa ((year >= EPOCH_YEAR) and (1 <= month <= 12) and (1 <= mday <= 31) and
        (0 <= hour <= 24) and (0 <= min <= 59) and (0 <= sec <= 61)):
        rudisha timegm(tt)
    else:
        rudisha None

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS_LOWER = []
for month in MONTHS: MONTHS_LOWER.append(month.lower())

eleza time2isoz(t=None):
    """Return a string representing time in seconds since epoch, t.

    If the function is called without an argument, it will use the current
    time.

    The format of the returned string is like "YYYY-MM-DD hh:mm:ssZ",
    representing Universal Time (UTC, aka GMT).  An example of this format is:

    1994-11-24 08:49:37Z

    """
    ikiwa t is None:
        dt = datetime.datetime.utcnow()
    else:
        dt = datetime.datetime.utckutokatimestamp(t)
    rudisha "%04d-%02d-%02d %02d:%02d:%02dZ" % (
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

eleza time2netscape(t=None):
    """Return a string representing time in seconds since epoch, t.

    If the function is called without an argument, it will use the current
    time.

    The format of the returned string is like this:

    Wed, DD-Mon-YYYY HH:MM:SS GMT

    """
    ikiwa t is None:
        dt = datetime.datetime.utcnow()
    else:
        dt = datetime.datetime.utckutokatimestamp(t)
    rudisha "%s, %02d-%s-%04d %02d:%02d:%02d GMT" % (
        DAYS[dt.weekday()], dt.day, MONTHS[dt.month-1],
        dt.year, dt.hour, dt.minute, dt.second)


UTC_ZONES = {"GMT": None, "UTC": None, "UT": None, "Z": None}

TIMEZONE_RE = re.compile(r"^([-+])?(\d\d?):?(\d\d)?$", re.ASCII)
eleza offset_kutoka_tz_string(tz):
    offset = None
    ikiwa tz in UTC_ZONES:
        offset = 0
    else:
        m = TIMEZONE_RE.search(tz)
        ikiwa m:
            offset = 3600 * int(m.group(2))
            ikiwa m.group(3):
                offset = offset + 60 * int(m.group(3))
            ikiwa m.group(1) == '-':
                offset = -offset
    rudisha offset

eleza _str2time(day, mon, yr, hr, min, sec, tz):
    yr = int(yr)
    ikiwa yr > datetime.MAXYEAR:
        rudisha None

    # translate month name to number
    # month numbers start with 1 (January)
    try:
        mon = MONTHS_LOWER.index(mon.lower())+1
    except ValueError:
        # maybe it's already a number
        try:
            imon = int(mon)
        except ValueError:
            rudisha None
        ikiwa 1 <= imon <= 12:
            mon = imon
        else:
            rudisha None

    # make sure clock elements are defined
    ikiwa hr is None: hr = 0
    ikiwa min is None: min = 0
    ikiwa sec is None: sec = 0

    day = int(day)
    hr = int(hr)
    min = int(min)
    sec = int(sec)

    ikiwa yr < 1000:
        # find "obvious" year
        cur_yr = time.localtime(time.time())[0]
        m = cur_yr % 100
        tmp = yr
        yr = yr + cur_yr - m
        m = m - tmp
        ikiwa abs(m) > 50:
            ikiwa m > 0: yr = yr + 100
            else: yr = yr - 100

    # convert UTC time tuple to seconds since epoch (not timezone-adjusted)
    t = _timegm((yr, mon, day, hr, min, sec, tz))

    ikiwa t is not None:
        # adjust time using timezone string, to get absolute time since epoch
        ikiwa tz is None:
            tz = "UTC"
        tz = tz.upper()
        offset = offset_kutoka_tz_string(tz)
        ikiwa offset is None:
            rudisha None
        t = t - offset

    rudisha t

STRICT_DATE_RE = re.compile(
    r"^[SMTWF][a-z][a-z], (\d\d) ([JFMASOND][a-z][a-z]) "
    r"(\d\d\d\d) (\d\d):(\d\d):(\d\d) GMT$", re.ASCII)
WEEKDAY_RE = re.compile(
    r"^(?:Sun|Mon|Tue|Wed|Thu|Fri|Sat)[a-z]*,?\s*", re.I | re.ASCII)
LOOSE_HTTP_DATE_RE = re.compile(
    r"""^
    (\d\d?)            # day
       (?:\s+|[-\/])
    (\w+)              # month
        (?:\s+|[-\/])
    (\d+)              # year
    (?:
          (?:\s+|:)    # separator before clock
       (\d\d?):(\d\d)  # hour:min
       (?::(\d\d))?    # optional seconds
    )?                 # optional clock
       \s*
    ([-+]?\d{2,4}|(?![APap][Mm]\b)[A-Za-z]+)? # timezone
       \s*
    (?:\(\w+\))?       # ASCII representation of timezone in parens.
       \s*$""", re.X | re.ASCII)
eleza http2time(text):
    """Returns time in seconds since epoch of time represented by a string.

    Return value is an integer.

    None is returned ikiwa the format of str is unrecognized, the time is outside
    the representable range, or the timezone string is not recognized.  If the
    string contains no timezone, UTC is assumed.

    The timezone in the string may be numerical (like "-0800" or "+0100") or a
    string timezone (like "UTC", "GMT", "BST" or "EST").  Currently, only the
    timezone strings equivalent to UTC (zero offset) are known to the function.

    The function loosely parses the following formats:

    Wed, 09 Feb 1994 22:23:32 GMT       -- HTTP format
    Tuesday, 08-Feb-94 14:15:29 GMT     -- old rfc850 HTTP format
    Tuesday, 08-Feb-1994 14:15:29 GMT   -- broken rfc850 HTTP format
    09 Feb 1994 22:23:32 GMT            -- HTTP format (no weekday)
    08-Feb-94 14:15:29 GMT              -- rfc850 format (no weekday)
    08-Feb-1994 14:15:29 GMT            -- broken rfc850 format (no weekday)

    The parser ignores leading and trailing whitespace.  The time may be
    absent.

    If the year is given with only 2 digits, the function will select the
    century that makes the year closest to the current date.

    """
    # fast exit for strictly conforming string
    m = STRICT_DATE_RE.search(text)
    ikiwa m:
        g = m.groups()
        mon = MONTHS_LOWER.index(g[1].lower()) + 1
        tt = (int(g[2]), mon, int(g[0]),
              int(g[3]), int(g[4]), float(g[5]))
        rudisha _timegm(tt)

    # No, we need some messy parsing...

    # clean up
    text = text.lstrip()
    text = WEEKDAY_RE.sub("", text, 1)  # Useless weekday

    # tz is time zone specifier string
    day, mon, yr, hr, min, sec, tz = [None]*7

    # loose regexp parse
    m = LOOSE_HTTP_DATE_RE.search(text)
    ikiwa m is not None:
        day, mon, yr, hr, min, sec, tz = m.groups()
    else:
        rudisha None  # bad format

    rudisha _str2time(day, mon, yr, hr, min, sec, tz)

ISO_DATE_RE = re.compile(
    r"""^
    (\d{4})              # year
       [-\/]?
    (\d\d?)              # numerical month
       [-\/]?
    (\d\d?)              # day
   (?:
         (?:\s+|[-:Tt])  # separator before clock
      (\d\d?):?(\d\d)    # hour:min
      (?::?(\d\d(?:\.\d*)?))?  # optional seconds (and fractional)
   )?                    # optional clock
      \s*
   ([-+]?\d\d?:?(:?\d\d)?
    |Z|z)?               # timezone  (Z is "zero meridian", i.e. GMT)
      \s*$""", re.X | re. ASCII)
eleza iso2time(text):
    """
    As for http2time, but parses the ISO 8601 formats:

    1994-02-03 14:15:29 -0100    -- ISO 8601 format
    1994-02-03 14:15:29          -- zone is optional
    1994-02-03                   -- only date
    1994-02-03T14:15:29          -- Use T as separator
    19940203T141529Z             -- ISO 8601 compact format
    19940203                     -- only date

    """
    # clean up
    text = text.lstrip()

    # tz is time zone specifier string
    day, mon, yr, hr, min, sec, tz = [None]*7

    # loose regexp parse
    m = ISO_DATE_RE.search(text)
    ikiwa m is not None:
        # XXX there's an extra bit of the timezone I'm ignoring here: is
        #   this the right thing to do?
        yr, mon, day, hr, min, sec, tz, _ = m.groups()
    else:
        rudisha None  # bad format

    rudisha _str2time(day, mon, yr, hr, min, sec, tz)


# Header parsing
# -----------------------------------------------------------------------------

eleza unmatched(match):
    """Return unmatched part of re.Match object."""
    start, end = match.span(0)
    rudisha match.string[:start]+match.string[end:]

HEADER_TOKEN_RE =        re.compile(r"^\s*([^=\s;,]+)")
HEADER_QUOTED_VALUE_RE = re.compile(r"^\s*=\s*\"([^\"\\]*(?:\\.[^\"\\]*)*)\"")
HEADER_VALUE_RE =        re.compile(r"^\s*=\s*([^\s;,]*)")
HEADER_ESCAPE_RE = re.compile(r"\\(.)")
eleza split_header_words(header_values):
    r"""Parse header values into a list of lists containing key,value pairs.

    The function knows how to deal with ",", ";" and "=" as well as quoted
    values after "=".  A list of space separated tokens are parsed as ikiwa they
    were separated by ";".

    If the header_values passed as argument contains multiple values, then they
    are treated as ikiwa they were a single value separated by comma ",".

    This means that this function is useful for parsing header fields that
    follow this syntax (BNF as kutoka the HTTP/1.1 specification, but we relax
    the requirement for tokens).

      headers           = #header
      header            = (token | parameter) *( [";"] (token | parameter))

      token             = 1*<any CHAR except CTLs or separators>
      separators        = "(" | ")" | "<" | ">" | "@"
                        | "," | ";" | ":" | "\" | <">
                        | "/" | "[" | "]" | "?" | "="
                        | "{" | "}" | SP | HT

      quoted-string     = ( <"> *(qdtext | quoted-pair ) <"> )
      qdtext            = <any TEXT except <">>
      quoted-pair       = "\" CHAR

      parameter         = attribute "=" value
      attribute         = token
      value             = token | quoted-string

    Each header is represented by a list of key/value pairs.  The value for a
    simple token (not part of a parameter) is None.  Syntactically incorrect
    headers will not necessarily be parsed as you would want.

    This is easier to describe with some examples:

    >>> split_header_words(['foo="bar"; port="80,81"; discard, bar=baz'])
    [[('foo', 'bar'), ('port', '80,81'), ('discard', None)], [('bar', 'baz')]]
    >>> split_header_words(['text/html; charset="iso-8859-1"'])
    [[('text/html', None), ('charset', 'iso-8859-1')]]
    >>> split_header_words([r'Basic realm="\"foo\bar\""'])
    [[('Basic', None), ('realm', '"foobar"')]]

    """
    assert not isinstance(header_values, str)
    result = []
    for text in header_values:
        orig_text = text
        pairs = []
        while text:
            m = HEADER_TOKEN_RE.search(text)
            ikiwa m:
                text = unmatched(m)
                name = m.group(1)
                m = HEADER_QUOTED_VALUE_RE.search(text)
                ikiwa m:  # quoted value
                    text = unmatched(m)
                    value = m.group(1)
                    value = HEADER_ESCAPE_RE.sub(r"\1", value)
                else:
                    m = HEADER_VALUE_RE.search(text)
                    ikiwa m:  # unquoted value
                        text = unmatched(m)
                        value = m.group(1)
                        value = value.rstrip()
                    else:
                        # no value, a lone token
                        value = None
                pairs.append((name, value))
            elikiwa text.lstrip().startswith(","):
                # concatenated headers, as per RFC 2616 section 4.2
                text = text.lstrip()[1:]
                ikiwa pairs: result.append(pairs)
                pairs = []
            else:
                # skip junk
                non_junk, nr_junk_chars = re.subn(r"^[=\s;]*", "", text)
                assert nr_junk_chars > 0, (
                    "split_header_words bug: '%s', '%s', %s" %
                    (orig_text, text, pairs))
                text = non_junk
        ikiwa pairs: result.append(pairs)
    rudisha result

HEADER_JOIN_ESCAPE_RE = re.compile(r"([\"\\])")
eleza join_header_words(lists):
    """Do the inverse (almost) of the conversion done by split_header_words.

    Takes a list of lists of (key, value) pairs and produces a single header
    value.  Attribute values are quoted ikiwa needed.

    >>> join_header_words([[("text/plain", None), ("charset", "iso-8859-1")]])
    'text/plain; charset="iso-8859-1"'
    >>> join_header_words([[("text/plain", None)], [("charset", "iso-8859-1")]])
    'text/plain, charset="iso-8859-1"'

    """
    headers = []
    for pairs in lists:
        attr = []
        for k, v in pairs:
            ikiwa v is not None:
                ikiwa not re.search(r"^\w+$", v):
                    v = HEADER_JOIN_ESCAPE_RE.sub(r"\\\1", v)  # escape " and \
                    v = '"%s"' % v
                k = "%s=%s" % (k, v)
            attr.append(k)
        ikiwa attr: headers.append("; ".join(attr))
    rudisha ", ".join(headers)

eleza strip_quotes(text):
    ikiwa text.startswith('"'):
        text = text[1:]
    ikiwa text.endswith('"'):
        text = text[:-1]
    rudisha text

eleza parse_ns_headers(ns_headers):
    """Ad-hoc parser for Netscape protocol cookie-attributes.

    The old Netscape cookie format for Set-Cookie can for instance contain
    an unquoted "," in the expires field, so we have to use this ad-hoc
    parser instead of split_header_words.

    XXX This may not make the best possible effort to parse all the crap
    that Netscape Cookie headers contain.  Ronald Tschalar's HTTPClient
    parser is probably better, so could do worse than following that if
    this ever gives any trouble.

    Currently, this is also used for parsing RFC 2109 cookies.

    """
    known_attrs = ("expires", "domain", "path", "secure",
                   # RFC 2109 attrs (may turn up in Netscape cookies, too)
                   "version", "port", "max-age")

    result = []
    for ns_header in ns_headers:
        pairs = []
        version_set = False

        # XXX: The following does not strictly adhere to RFCs in that empty
        # names and values are legal (the former will only appear once and will
        # be overwritten ikiwa multiple occurrences are present). This is
        # mostly to deal with backwards compatibility.
        for ii, param in enumerate(ns_header.split(';')):
            param = param.strip()

            key, sep, val = param.partition('=')
            key = key.strip()

            ikiwa not key:
                ikiwa ii == 0:
                    break
                else:
                    continue

            # allow for a distinction between present and empty and missing
            # altogether
            val = val.strip() ikiwa sep else None

            ikiwa ii != 0:
                lc = key.lower()
                ikiwa lc in known_attrs:
                    key = lc

                ikiwa key == "version":
                    # This is an RFC 2109 cookie.
                    ikiwa val is not None:
                        val = strip_quotes(val)
                    version_set = True
                elikiwa key == "expires":
                    # convert expires date to seconds since epoch
                    ikiwa val is not None:
                        val = http2time(strip_quotes(val))  # None ikiwa invalid
            pairs.append((key, val))

        ikiwa pairs:
            ikiwa not version_set:
                pairs.append(("version", "0"))
            result.append(pairs)

    rudisha result


IPV4_RE = re.compile(r"\.\d+$", re.ASCII)
eleza is_HDN(text):
    """Return True ikiwa text is a host domain name."""
    # XXX
    # This may well be wrong.  Which RFC is HDN defined in, ikiwa any (for
    #  the purposes of RFC 2965)?
    # For the current implementation, what about IPv6?  Remember to look
    #  at other uses of IPV4_RE also, ikiwa change this.
    ikiwa IPV4_RE.search(text):
        rudisha False
    ikiwa text == "":
        rudisha False
    ikiwa text[0] == "." or text[-1] == ".":
        rudisha False
    rudisha True

eleza domain_match(A, B):
    """Return True ikiwa domain A domain-matches domain B, according to RFC 2965.

    A and B may be host domain names or IP addresses.

    RFC 2965, section 1:

    Host names can be specified either as an IP address or a HDN string.
    Sometimes we compare one host name with another.  (Such comparisons SHALL
    be case-insensitive.)  Host A's name domain-matches host B's if

         *  their host name strings string-compare equal; or

         * A is a HDN string and has the form NB, where N is a non-empty
            name string, B has the form .B', and B' is a HDN string.  (So,
            x.y.com domain-matches .Y.com but not Y.com.)

    Note that domain-match is not a commutative operation: a.b.c.com
    domain-matches .c.com, but not the reverse.

    """
    # Note that, ikiwa A or B are IP addresses, the only relevant part of the
    # definition of the domain-match algorithm is the direct string-compare.
    A = A.lower()
    B = B.lower()
    ikiwa A == B:
        rudisha True
    ikiwa not is_HDN(A):
        rudisha False
    i = A.rfind(B)
    ikiwa i == -1 or i == 0:
        # A does not have form NB, or N is the empty string
        rudisha False
    ikiwa not B.startswith("."):
        rudisha False
    ikiwa not is_HDN(B[1:]):
        rudisha False
    rudisha True

eleza liberal_is_HDN(text):
    """Return True ikiwa text is a sort-of-like a host domain name.

    For accepting/blocking domains.

    """
    ikiwa IPV4_RE.search(text):
        rudisha False
    rudisha True

eleza user_domain_match(A, B):
    """For blocking/accepting domains.

    A and B may be host domain names or IP addresses.

    """
    A = A.lower()
    B = B.lower()
    ikiwa not (liberal_is_HDN(A) and liberal_is_HDN(B)):
        ikiwa A == B:
            # equal IP addresses
            rudisha True
        rudisha False
    initial_dot = B.startswith(".")
    ikiwa initial_dot and A.endswith(B):
        rudisha True
    ikiwa not initial_dot and A == B:
        rudisha True
    rudisha False

cut_port_re = re.compile(r":\d+$", re.ASCII)
eleza request_host(request):
    """Return request-host, as defined by RFC 2965.

    Variation kutoka RFC: returned value is lowercased, for convenient
    comparison.

    """
    url = request.get_full_url()
    host = urllib.parse.urlparse(url)[1]
    ikiwa host == "":
        host = request.get_header("Host", "")

    # remove port, ikiwa present
    host = cut_port_re.sub("", host, 1)
    rudisha host.lower()

eleza eff_request_host(request):
    """Return a tuple (request-host, effective request-host name).

    As defined by RFC 2965, except both are lowercased.

    """
    erhn = req_host = request_host(request)
    ikiwa req_host.find(".") == -1 and not IPV4_RE.search(req_host):
        erhn = req_host + ".local"
    rudisha req_host, erhn

eleza request_path(request):
    """Path component of request-URI, as defined by RFC 2965."""
    url = request.get_full_url()
    parts = urllib.parse.urlsplit(url)
    path = escape_path(parts.path)
    ikiwa not path.startswith("/"):
        # fix bad RFC 2396 absoluteURI
        path = "/" + path
    rudisha path

eleza request_port(request):
    host = request.host
    i = host.find(':')
    ikiwa i >= 0:
        port = host[i+1:]
        try:
            int(port)
        except ValueError:
            _debug("nonnumeric port: '%s'", port)
            rudisha None
    else:
        port = DEFAULT_HTTP_PORT
    rudisha port

# Characters in addition to A-Z, a-z, 0-9, '_', '.', and '-' that don't
# need to be escaped to form a valid HTTP URL (RFCs 2396 and 1738).
HTTP_PATH_SAFE = "%/;:@&=+$,!~*'()"
ESCAPED_CHAR_RE = re.compile(r"%([0-9a-fA-F][0-9a-fA-F])")
eleza uppercase_escaped_char(match):
    rudisha "%%%s" % match.group(1).upper()
eleza escape_path(path):
    """Escape any invalid characters in HTTP URL, and uppercase all escapes."""
    # There's no knowing what character encoding was used to create URLs
    # containing %-escapes, but since we have to pick one to escape invalid
    # path characters, we pick UTF-8, as recommended in the HTML 4.0
    # specification:
    # http://www.w3.org/TR/REC-html40/appendix/notes.html#h-B.2.1
    # And here, kind of: draft-fielding-uri-rfc2396bis-03
    # (And in draft IRI specification: draft-duerst-iri-05)
    # (And here, for new URI schemes: RFC 2718)
    path = urllib.parse.quote(path, HTTP_PATH_SAFE)
    path = ESCAPED_CHAR_RE.sub(uppercase_escaped_char, path)
    rudisha path

eleza reach(h):
    """Return reach of host h, as defined by RFC 2965, section 1.

    The reach R of a host name H is defined as follows:

       *  If

          -  H is the host domain name of a host; and,

          -  H has the form A.B; and

          -  A has no embedded (that is, interior) dots; and

          -  B has at least one embedded dot, or B is the string "local".
             then the reach of H is .B.

       *  Otherwise, the reach of H is H.

    >>> reach("www.acme.com")
    '.acme.com'
    >>> reach("acme.com")
    'acme.com'
    >>> reach("acme.local")
    '.local'

    """
    i = h.find(".")
    ikiwa i >= 0:
        #a = h[:i]  # this line is only here to show what a is
        b = h[i+1:]
        i = b.find(".")
        ikiwa is_HDN(h) and (i >= 0 or b == "local"):
            rudisha "."+b
    rudisha h

eleza is_third_party(request):
    """

    RFC 2965, section 3.3.6:

        An unverifiable transaction is to a third-party host ikiwa its request-
        host U does not domain-match the reach R of the request-host O in the
        origin transaction.

    """
    req_host = request_host(request)
    ikiwa not domain_match(req_host, reach(request.origin_req_host)):
        rudisha True
    else:
        rudisha False


kundi Cookie:
    """HTTP Cookie.

    This kundi represents both Netscape and RFC 2965 cookies.

    This is deliberately a very simple class.  It just holds attributes.  It's
    possible to construct Cookie instances that don't comply with the cookie
    standards.  CookieJar.make_cookies is the factory function for Cookie
    objects -- it deals with cookie parsing, supplying defaults, and
    normalising to the representation used in this class.  CookiePolicy is
    responsible for checking them to see whether they should be accepted kutoka
    and returned to the server.

    Note that the port may be present in the headers, but unspecified ("Port"
    rather than"Port=80", for example); ikiwa this is the case, port is None.

    """

    eleza __init__(self, version, name, value,
                 port, port_specified,
                 domain, domain_specified, domain_initial_dot,
                 path, path_specified,
                 secure,
                 expires,
                 discard,
                 comment,
                 comment_url,
                 rest,
                 rfc2109=False,
                 ):

        ikiwa version is not None: version = int(version)
        ikiwa expires is not None: expires = int(float(expires))
        ikiwa port is None and port_specified is True:
            raise ValueError("ikiwa port is None, port_specified must be false")

        self.version = version
        self.name = name
        self.value = value
        self.port = port
        self.port_specified = port_specified
        # normalise case, as per RFC 2965 section 3.3.3
        self.domain = domain.lower()
        self.domain_specified = domain_specified
        # Sigh.  We need to know whether the domain given in the
        # cookie-attribute had an initial dot, in order to follow RFC 2965
        # (as clarified in draft errata).  Needed for the returned $Domain
        # value.
        self.domain_initial_dot = domain_initial_dot
        self.path = path
        self.path_specified = path_specified
        self.secure = secure
        self.expires = expires
        self.discard = discard
        self.comment = comment
        self.comment_url = comment_url
        self.rfc2109 = rfc2109

        self._rest = copy.copy(rest)

    eleza has_nonstandard_attr(self, name):
        rudisha name in self._rest
    eleza get_nonstandard_attr(self, name, default=None):
        rudisha self._rest.get(name, default)
    eleza set_nonstandard_attr(self, name, value):
        self._rest[name] = value

    eleza is_expired(self, now=None):
        ikiwa now is None: now = time.time()
        ikiwa (self.expires is not None) and (self.expires <= now):
            rudisha True
        rudisha False

    eleza __str__(self):
        ikiwa self.port is None: p = ""
        else: p = ":"+self.port
        limit = self.domain + p + self.path
        ikiwa self.value is not None:
            namevalue = "%s=%s" % (self.name, self.value)
        else:
            namevalue = self.name
        rudisha "<Cookie %s for %s>" % (namevalue, limit)

    eleza __repr__(self):
        args = []
        for name in ("version", "name", "value",
                     "port", "port_specified",
                     "domain", "domain_specified", "domain_initial_dot",
                     "path", "path_specified",
                     "secure", "expires", "discard", "comment", "comment_url",
                     ):
            attr = getattr(self, name)
            args.append("%s=%s" % (name, repr(attr)))
        args.append("rest=%s" % repr(self._rest))
        args.append("rfc2109=%s" % repr(self.rfc2109))
        rudisha "%s(%s)" % (self.__class__.__name__, ", ".join(args))


kundi CookiePolicy:
    """Defines which cookies get accepted kutoka and returned to server.

    May also modify cookies, though this is probably a bad idea.

    The subkundi DefaultCookiePolicy defines the standard rules for Netscape
    and RFC 2965 cookies -- override that ikiwa you want a customized policy.

    """
    eleza set_ok(self, cookie, request):
        """Return true ikiwa (and only if) cookie should be accepted kutoka server.

        Currently, pre-expired cookies never get this far -- the CookieJar
        kundi deletes such cookies itself.

        """
        raise NotImplementedError()

    eleza return_ok(self, cookie, request):
        """Return true ikiwa (and only if) cookie should be returned to server."""
        raise NotImplementedError()

    eleza domain_return_ok(self, domain, request):
        """Return false ikiwa cookies should not be returned, given cookie domain.
        """
        rudisha True

    eleza path_return_ok(self, path, request):
        """Return false ikiwa cookies should not be returned, given cookie path.
        """
        rudisha True


kundi DefaultCookiePolicy(CookiePolicy):
    """Implements the standard rules for accepting and returning cookies."""

    DomainStrictNoDots = 1
    DomainStrictNonDomain = 2
    DomainRFC2965Match = 4

    DomainLiberal = 0
    DomainStrict = DomainStrictNoDots|DomainStrictNonDomain

    eleza __init__(self,
                 blocked_domains=None, allowed_domains=None,
                 netscape=True, rfc2965=False,
                 rfc2109_as_netscape=None,
                 hide_cookie2=False,
                 strict_domain=False,
                 strict_rfc2965_unverifiable=True,
                 strict_ns_unverifiable=False,
                 strict_ns_domain=DomainLiberal,
                 strict_ns_set_initial_dollar=False,
                 strict_ns_set_path=False,
                 secure_protocols=("https", "wss")
                 ):
        """Constructor arguments should be passed as keyword arguments only."""
        self.netscape = netscape
        self.rfc2965 = rfc2965
        self.rfc2109_as_netscape = rfc2109_as_netscape
        self.hide_cookie2 = hide_cookie2
        self.strict_domain = strict_domain
        self.strict_rfc2965_unverifiable = strict_rfc2965_unverifiable
        self.strict_ns_unverifiable = strict_ns_unverifiable
        self.strict_ns_domain = strict_ns_domain
        self.strict_ns_set_initial_dollar = strict_ns_set_initial_dollar
        self.strict_ns_set_path = strict_ns_set_path
        self.secure_protocols = secure_protocols

        ikiwa blocked_domains is not None:
            self._blocked_domains = tuple(blocked_domains)
        else:
            self._blocked_domains = ()

        ikiwa allowed_domains is not None:
            allowed_domains = tuple(allowed_domains)
        self._allowed_domains = allowed_domains

    eleza blocked_domains(self):
        """Return the sequence of blocked domains (as a tuple)."""
        rudisha self._blocked_domains
    eleza set_blocked_domains(self, blocked_domains):
        """Set the sequence of blocked domains."""
        self._blocked_domains = tuple(blocked_domains)

    eleza is_blocked(self, domain):
        for blocked_domain in self._blocked_domains:
            ikiwa user_domain_match(domain, blocked_domain):
                rudisha True
        rudisha False

    eleza allowed_domains(self):
        """Return None, or the sequence of allowed domains (as a tuple)."""
        rudisha self._allowed_domains
    eleza set_allowed_domains(self, allowed_domains):
        """Set the sequence of allowed domains, or None."""
        ikiwa allowed_domains is not None:
            allowed_domains = tuple(allowed_domains)
        self._allowed_domains = allowed_domains

    eleza is_not_allowed(self, domain):
        ikiwa self._allowed_domains is None:
            rudisha False
        for allowed_domain in self._allowed_domains:
            ikiwa user_domain_match(domain, allowed_domain):
                rudisha False
        rudisha True

    eleza set_ok(self, cookie, request):
        """
        If you override .set_ok(), be sure to call this method.  If it returns
        false, so should your subkundi (assuming your subkundi wants to be more
        strict about which cookies to accept).

        """
        _debug(" - checking cookie %s=%s", cookie.name, cookie.value)

        assert cookie.name is not None

        for n in "version", "verifiability", "name", "path", "domain", "port":
            fn_name = "set_ok_"+n
            fn = getattr(self, fn_name)
            ikiwa not fn(cookie, request):
                rudisha False

        rudisha True

    eleza set_ok_version(self, cookie, request):
        ikiwa cookie.version is None:
            # Version is always set to 0 by parse_ns_headers ikiwa it's a Netscape
            # cookie, so this must be an invalid RFC 2965 cookie.
            _debug("   Set-Cookie2 without version attribute (%s=%s)",
                   cookie.name, cookie.value)
            rudisha False
        ikiwa cookie.version > 0 and not self.rfc2965:
            _debug("   RFC 2965 cookies are switched off")
            rudisha False
        elikiwa cookie.version == 0 and not self.netscape:
            _debug("   Netscape cookies are switched off")
            rudisha False
        rudisha True

    eleza set_ok_verifiability(self, cookie, request):
        ikiwa request.unverifiable and is_third_party(request):
            ikiwa cookie.version > 0 and self.strict_rfc2965_unverifiable:
                _debug("   third-party RFC 2965 cookie during "
                             "unverifiable transaction")
                rudisha False
            elikiwa cookie.version == 0 and self.strict_ns_unverifiable:
                _debug("   third-party Netscape cookie during "
                             "unverifiable transaction")
                rudisha False
        rudisha True

    eleza set_ok_name(self, cookie, request):
        # Try and stop servers setting V0 cookies designed to hack other
        # servers that know both V0 and V1 protocols.
        ikiwa (cookie.version == 0 and self.strict_ns_set_initial_dollar and
            cookie.name.startswith("$")):
            _debug("   illegal name (starts with '$'): '%s'", cookie.name)
            rudisha False
        rudisha True

    eleza set_ok_path(self, cookie, request):
        ikiwa cookie.path_specified:
            req_path = request_path(request)
            ikiwa ((cookie.version > 0 or
                 (cookie.version == 0 and self.strict_ns_set_path)) and
                not self.path_return_ok(cookie.path, request)):
                _debug("   path attribute %s is not a prefix of request "
                       "path %s", cookie.path, req_path)
                rudisha False
        rudisha True

    eleza set_ok_domain(self, cookie, request):
        ikiwa self.is_blocked(cookie.domain):
            _debug("   domain %s is in user block-list", cookie.domain)
            rudisha False
        ikiwa self.is_not_allowed(cookie.domain):
            _debug("   domain %s is not in user allow-list", cookie.domain)
            rudisha False
        ikiwa cookie.domain_specified:
            req_host, erhn = eff_request_host(request)
            domain = cookie.domain
            ikiwa self.strict_domain and (domain.count(".") >= 2):
                # XXX This should probably be compared with the Konqueror
                # (kcookiejar.cpp) and Mozilla implementations, but it's a
                # losing battle.
                i = domain.rfind(".")
                j = domain.rfind(".", 0, i)
                ikiwa j == 0:  # domain like .foo.bar
                    tld = domain[i+1:]
                    sld = domain[j+1:i]
                    ikiwa sld.lower() in ("co", "ac", "com", "edu", "org", "net",
                       "gov", "mil", "int", "aero", "biz", "cat", "coop",
                       "info", "jobs", "mobi", "museum", "name", "pro",
                       "travel", "eu") and len(tld) == 2:
                        # domain like .co.uk
                        _debug("   country-code second level domain %s", domain)
                        rudisha False
            ikiwa domain.startswith("."):
                undotted_domain = domain[1:]
            else:
                undotted_domain = domain
            embedded_dots = (undotted_domain.find(".") >= 0)
            ikiwa not embedded_dots and domain != ".local":
                _debug("   non-local domain %s contains no embedded dot",
                       domain)
                rudisha False
            ikiwa cookie.version == 0:
                ikiwa (not erhn.endswith(domain) and
                    (not erhn.startswith(".") and
                     not ("."+erhn).endswith(domain))):
                    _debug("   effective request-host %s (even with added "
                           "initial dot) does not end with %s",
                           erhn, domain)
                    rudisha False
            ikiwa (cookie.version > 0 or
                (self.strict_ns_domain & self.DomainRFC2965Match)):
                ikiwa not domain_match(erhn, domain):
                    _debug("   effective request-host %s does not domain-match "
                           "%s", erhn, domain)
                    rudisha False
            ikiwa (cookie.version > 0 or
                (self.strict_ns_domain & self.DomainStrictNoDots)):
                host_prefix = req_host[:-len(domain)]
                ikiwa (host_prefix.find(".") >= 0 and
                    not IPV4_RE.search(req_host)):
                    _debug("   host prefix %s for domain %s contains a dot",
                           host_prefix, domain)
                    rudisha False
        rudisha True

    eleza set_ok_port(self, cookie, request):
        ikiwa cookie.port_specified:
            req_port = request_port(request)
            ikiwa req_port is None:
                req_port = "80"
            else:
                req_port = str(req_port)
            for p in cookie.port.split(","):
                try:
                    int(p)
                except ValueError:
                    _debug("   bad port %s (not numeric)", p)
                    rudisha False
                ikiwa p == req_port:
                    break
            else:
                _debug("   request port (%s) not found in %s",
                       req_port, cookie.port)
                rudisha False
        rudisha True

    eleza return_ok(self, cookie, request):
        """
        If you override .return_ok(), be sure to call this method.  If it
        returns false, so should your subkundi (assuming your subkundi wants to
        be more strict about which cookies to return).

        """
        # Path has already been checked by .path_return_ok(), and domain
        # blocking done by .domain_return_ok().
        _debug(" - checking cookie %s=%s", cookie.name, cookie.value)

        for n in "version", "verifiability", "secure", "expires", "port", "domain":
            fn_name = "return_ok_"+n
            fn = getattr(self, fn_name)
            ikiwa not fn(cookie, request):
                rudisha False
        rudisha True

    eleza return_ok_version(self, cookie, request):
        ikiwa cookie.version > 0 and not self.rfc2965:
            _debug("   RFC 2965 cookies are switched off")
            rudisha False
        elikiwa cookie.version == 0 and not self.netscape:
            _debug("   Netscape cookies are switched off")
            rudisha False
        rudisha True

    eleza return_ok_verifiability(self, cookie, request):
        ikiwa request.unverifiable and is_third_party(request):
            ikiwa cookie.version > 0 and self.strict_rfc2965_unverifiable:
                _debug("   third-party RFC 2965 cookie during unverifiable "
                       "transaction")
                rudisha False
            elikiwa cookie.version == 0 and self.strict_ns_unverifiable:
                _debug("   third-party Netscape cookie during unverifiable "
                       "transaction")
                rudisha False
        rudisha True

    eleza return_ok_secure(self, cookie, request):
        ikiwa cookie.secure and request.type not in self.secure_protocols:
            _debug("   secure cookie with non-secure request")
            rudisha False
        rudisha True

    eleza return_ok_expires(self, cookie, request):
        ikiwa cookie.is_expired(self._now):
            _debug("   cookie expired")
            rudisha False
        rudisha True

    eleza return_ok_port(self, cookie, request):
        ikiwa cookie.port:
            req_port = request_port(request)
            ikiwa req_port is None:
                req_port = "80"
            for p in cookie.port.split(","):
                ikiwa p == req_port:
                    break
            else:
                _debug("   request port %s does not match cookie port %s",
                       req_port, cookie.port)
                rudisha False
        rudisha True

    eleza return_ok_domain(self, cookie, request):
        req_host, erhn = eff_request_host(request)
        domain = cookie.domain

        ikiwa domain and not domain.startswith("."):
            dotdomain = "." + domain
        else:
            dotdomain = domain

        # strict check of non-domain cookies: Mozilla does this, MSIE5 doesn't
        ikiwa (cookie.version == 0 and
            (self.strict_ns_domain & self.DomainStrictNonDomain) and
            not cookie.domain_specified and domain != erhn):
            _debug("   cookie with unspecified domain does not string-compare "
                   "equal to request domain")
            rudisha False

        ikiwa cookie.version > 0 and not domain_match(erhn, domain):
            _debug("   effective request-host name %s does not domain-match "
                   "RFC 2965 cookie domain %s", erhn, domain)
            rudisha False
        ikiwa cookie.version == 0 and not ("."+erhn).endswith(dotdomain):
            _debug("   request-host %s does not match Netscape cookie domain "
                   "%s", req_host, domain)
            rudisha False
        rudisha True

    eleza domain_return_ok(self, domain, request):
        # Liberal check of.  This is here as an optimization to avoid
        # having to load lots of MSIE cookie files unless necessary.
        req_host, erhn = eff_request_host(request)
        ikiwa not req_host.startswith("."):
            req_host = "."+req_host
        ikiwa not erhn.startswith("."):
            erhn = "."+erhn
        ikiwa domain and not domain.startswith("."):
            dotdomain = "." + domain
        else:
            dotdomain = domain
        ikiwa not (req_host.endswith(dotdomain) or erhn.endswith(dotdomain)):
            #_debug("   request domain %s does not match cookie domain %s",
            #       req_host, domain)
            rudisha False

        ikiwa self.is_blocked(domain):
            _debug("   domain %s is in user block-list", domain)
            rudisha False
        ikiwa self.is_not_allowed(domain):
            _debug("   domain %s is not in user allow-list", domain)
            rudisha False

        rudisha True

    eleza path_return_ok(self, path, request):
        _debug("- checking cookie path=%s", path)
        req_path = request_path(request)
        pathlen = len(path)
        ikiwa req_path == path:
            rudisha True
        elikiwa (req_path.startswith(path) and
              (path.endswith("/") or req_path[pathlen:pathlen+1] == "/")):
            rudisha True

        _debug("  %s does not path-match %s", req_path, path)
        rudisha False

eleza vals_sorted_by_key(adict):
    keys = sorted(adict.keys())
    rudisha map(adict.get, keys)

eleza deepvalues(mapping):
    """Iterates over nested mapping, depth-first, in sorted order by key."""
    values = vals_sorted_by_key(mapping)
    for obj in values:
        mapping = False
        try:
            obj.items
        except AttributeError:
            pass
        else:
            mapping = True
            yield kutoka deepvalues(obj)
        ikiwa not mapping:
            yield obj


# Used as second parameter to dict.get() method, to distinguish absent
# dict key kutoka one with a None value.
kundi Absent: pass

kundi CookieJar:
    """Collection of HTTP cookies.

    You may not need to know about this class: try
    urllib.request.build_opener(HTTPCookieProcessor).open(url).
    """

    non_word_re = re.compile(r"\W")
    quote_re = re.compile(r"([\"\\])")
    strict_domain_re = re.compile(r"\.?[^.]*")
    domain_re = re.compile(r"[^.]*")
    dots_re = re.compile(r"^\.+")

    magic_re = re.compile(r"^\#LWP-Cookies-(\d+\.\d+)", re.ASCII)

    eleza __init__(self, policy=None):
        ikiwa policy is None:
            policy = DefaultCookiePolicy()
        self._policy = policy

        self._cookies_lock = _threading.RLock()
        self._cookies = {}

    eleza set_policy(self, policy):
        self._policy = policy

    eleza _cookies_for_domain(self, domain, request):
        cookies = []
        ikiwa not self._policy.domain_return_ok(domain, request):
            rudisha []
        _debug("Checking %s for cookies to return", domain)
        cookies_by_path = self._cookies[domain]
        for path in cookies_by_path.keys():
            ikiwa not self._policy.path_return_ok(path, request):
                continue
            cookies_by_name = cookies_by_path[path]
            for cookie in cookies_by_name.values():
                ikiwa not self._policy.return_ok(cookie, request):
                    _debug("   not returning cookie")
                    continue
                _debug("   it's a match")
                cookies.append(cookie)
        rudisha cookies

    eleza _cookies_for_request(self, request):
        """Return a list of cookies to be returned to server."""
        cookies = []
        for domain in self._cookies.keys():
            cookies.extend(self._cookies_for_domain(domain, request))
        rudisha cookies

    eleza _cookie_attrs(self, cookies):
        """Return a list of cookie-attributes to be returned to server.

        like ['foo="bar"; $Path="/"', ...]

        The $Version attribute is also added when appropriate (currently only
        once per request).

        """
        # add cookies in order of most specific (ie. longest) path first
        cookies.sort(key=lambda a: len(a.path), reverse=True)

        version_set = False

        attrs = []
        for cookie in cookies:
            # set version of Cookie header
            # XXX
            # What should it be ikiwa multiple matching Set-Cookie headers have
            #  different versions themselves?
            # Answer: there is no answer; was supposed to be settled by
            #  RFC 2965 errata, but that may never appear...
            version = cookie.version
            ikiwa not version_set:
                version_set = True
                ikiwa version > 0:
                    attrs.append("$Version=%s" % version)

            # quote cookie value ikiwa necessary
            # (not for Netscape protocol, which already has any quotes
            #  intact, due to the poorly-specified Netscape Cookie: syntax)
            ikiwa ((cookie.value is not None) and
                self.non_word_re.search(cookie.value) and version > 0):
                value = self.quote_re.sub(r"\\\1", cookie.value)
            else:
                value = cookie.value

            # add cookie-attributes to be returned in Cookie header
            ikiwa cookie.value is None:
                attrs.append(cookie.name)
            else:
                attrs.append("%s=%s" % (cookie.name, value))
            ikiwa version > 0:
                ikiwa cookie.path_specified:
                    attrs.append('$Path="%s"' % cookie.path)
                ikiwa cookie.domain.startswith("."):
                    domain = cookie.domain
                    ikiwa (not cookie.domain_initial_dot and
                        domain.startswith(".")):
                        domain = domain[1:]
                    attrs.append('$Domain="%s"' % domain)
                ikiwa cookie.port is not None:
                    p = "$Port"
                    ikiwa cookie.port_specified:
                        p = p + ('="%s"' % cookie.port)
                    attrs.append(p)

        rudisha attrs

    eleza add_cookie_header(self, request):
        """Add correct Cookie: header to request (urllib.request.Request object).

        The Cookie2 header is also added unless policy.hide_cookie2 is true.

        """
        _debug("add_cookie_header")
        self._cookies_lock.acquire()
        try:

            self._policy._now = self._now = int(time.time())

            cookies = self._cookies_for_request(request)

            attrs = self._cookie_attrs(cookies)
            ikiwa attrs:
                ikiwa not request.has_header("Cookie"):
                    request.add_unredirected_header(
                        "Cookie", "; ".join(attrs))

            # ikiwa necessary, advertise that we know RFC 2965
            ikiwa (self._policy.rfc2965 and not self._policy.hide_cookie2 and
                not request.has_header("Cookie2")):
                for cookie in cookies:
                    ikiwa cookie.version != 1:
                        request.add_unredirected_header("Cookie2", '$Version="1"')
                        break

        finally:
            self._cookies_lock.release()

        self.clear_expired_cookies()

    eleza _normalized_cookie_tuples(self, attrs_set):
        """Return list of tuples containing normalised cookie information.

        attrs_set is the list of lists of key,value pairs extracted kutoka
        the Set-Cookie or Set-Cookie2 headers.

        Tuples are name, value, standard, rest, where name and value are the
        cookie name and value, standard is a dictionary containing the standard
        cookie-attributes (discard, secure, version, expires or max-age,
        domain, path and port) and rest is a dictionary containing the rest of
        the cookie-attributes.

        """
        cookie_tuples = []

        boolean_attrs = "discard", "secure"
        value_attrs = ("version",
                       "expires", "max-age",
                       "domain", "path", "port",
                       "comment", "commenturl")

        for cookie_attrs in attrs_set:
            name, value = cookie_attrs[0]

            # Build dictionary of standard cookie-attributes (standard) and
            # dictionary of other cookie-attributes (rest).

            # Note: expiry time is normalised to seconds since epoch.  V0
            # cookies should have the Expires cookie-attribute, and V1 cookies
            # should have Max-Age, but since V1 includes RFC 2109 cookies (and
            # since V0 cookies may be a mish-mash of Netscape and RFC 2109), we
            # accept either (but prefer Max-Age).
            max_age_set = False

            bad_cookie = False

            standard = {}
            rest = {}
            for k, v in cookie_attrs[1:]:
                lc = k.lower()
                # don't lose case distinction for unknown fields
                ikiwa lc in value_attrs or lc in boolean_attrs:
                    k = lc
                ikiwa k in boolean_attrs and v is None:
                    # boolean cookie-attribute is present, but has no value
                    # (like "discard", rather than "port=80")
                    v = True
                ikiwa k in standard:
                    # only first value is significant
                    continue
                ikiwa k == "domain":
                    ikiwa v is None:
                        _debug("   missing value for domain attribute")
                        bad_cookie = True
                        break
                    # RFC 2965 section 3.3.3
                    v = v.lower()
                ikiwa k == "expires":
                    ikiwa max_age_set:
                        # Prefer max-age to expires (like Mozilla)
                        continue
                    ikiwa v is None:
                        _debug("   missing or invalid value for expires "
                              "attribute: treating as session cookie")
                        continue
                ikiwa k == "max-age":
                    max_age_set = True
                    try:
                        v = int(v)
                    except ValueError:
                        _debug("   missing or invalid (non-numeric) value for "
                              "max-age attribute")
                        bad_cookie = True
                        break
                    # convert RFC 2965 Max-Age to seconds since epoch
                    # XXX Strictly you're supposed to follow RFC 2616
                    #   age-calculation rules.  Remember that zero Max-Age
                    #   is a request to discard (old and new) cookie, though.
                    k = "expires"
                    v = self._now + v
                ikiwa (k in value_attrs) or (k in boolean_attrs):
                    ikiwa (v is None and
                        k not in ("port", "comment", "commenturl")):
                        _debug("   missing value for %s attribute" % k)
                        bad_cookie = True
                        break
                    standard[k] = v
                else:
                    rest[k] = v

            ikiwa bad_cookie:
                continue

            cookie_tuples.append((name, value, standard, rest))

        rudisha cookie_tuples

    eleza _cookie_kutoka_cookie_tuple(self, tup, request):
        # standard is dict of standard cookie-attributes, rest is dict of the
        # rest of them
        name, value, standard, rest = tup

        domain = standard.get("domain", Absent)
        path = standard.get("path", Absent)
        port = standard.get("port", Absent)
        expires = standard.get("expires", Absent)

        # set the easy defaults
        version = standard.get("version", None)
        ikiwa version is not None:
            try:
                version = int(version)
            except ValueError:
                rudisha None  # invalid version, ignore cookie
        secure = standard.get("secure", False)
        # (discard is also set ikiwa expires is Absent)
        discard = standard.get("discard", False)
        comment = standard.get("comment", None)
        comment_url = standard.get("commenturl", None)

        # set default path
        ikiwa path is not Absent and path != "":
            path_specified = True
            path = escape_path(path)
        else:
            path_specified = False
            path = request_path(request)
            i = path.rfind("/")
            ikiwa i != -1:
                ikiwa version == 0:
                    # Netscape spec parts company kutoka reality here
                    path = path[:i]
                else:
                    path = path[:i+1]
            ikiwa len(path) == 0: path = "/"

        # set default domain
        domain_specified = domain is not Absent
        # but first we have to remember whether it starts with a dot
        domain_initial_dot = False
        ikiwa domain_specified:
            domain_initial_dot = bool(domain.startswith("."))
        ikiwa domain is Absent:
            req_host, erhn = eff_request_host(request)
            domain = erhn
        elikiwa not domain.startswith("."):
            domain = "."+domain

        # set default port
        port_specified = False
        ikiwa port is not Absent:
            ikiwa port is None:
                # Port attr present, but has no value: default to request port.
                # Cookie should then only be sent back on that port.
                port = request_port(request)
            else:
                port_specified = True
                port = re.sub(r"\s+", "", port)
        else:
            # No port attr present.  Cookie can be sent back on any port.
            port = None

        # set default expires and discard
        ikiwa expires is Absent:
            expires = None
            discard = True
        elikiwa expires <= self._now:
            # Expiry date in past is request to delete cookie.  This can't be
            # in DefaultCookiePolicy, because can't delete cookies there.
            try:
                self.clear(domain, path, name)
            except KeyError:
                pass
            _debug("Expiring cookie, domain='%s', path='%s', name='%s'",
                   domain, path, name)
            rudisha None

        rudisha Cookie(version,
                      name, value,
                      port, port_specified,
                      domain, domain_specified, domain_initial_dot,
                      path, path_specified,
                      secure,
                      expires,
                      discard,
                      comment,
                      comment_url,
                      rest)

    eleza _cookies_kutoka_attrs_set(self, attrs_set, request):
        cookie_tuples = self._normalized_cookie_tuples(attrs_set)

        cookies = []
        for tup in cookie_tuples:
            cookie = self._cookie_kutoka_cookie_tuple(tup, request)
            ikiwa cookie: cookies.append(cookie)
        rudisha cookies

    eleza _process_rfc2109_cookies(self, cookies):
        rfc2109_as_ns = getattr(self._policy, 'rfc2109_as_netscape', None)
        ikiwa rfc2109_as_ns is None:
            rfc2109_as_ns = not self._policy.rfc2965
        for cookie in cookies:
            ikiwa cookie.version == 1:
                cookie.rfc2109 = True
                ikiwa rfc2109_as_ns:
                    # treat 2109 cookies as Netscape cookies rather than
                    # as RFC2965 cookies
                    cookie.version = 0

    eleza make_cookies(self, response, request):
        """Return sequence of Cookie objects extracted kutoka response object."""
        # get cookie-attributes for RFC 2965 and Netscape protocols
        headers = response.info()
        rfc2965_hdrs = headers.get_all("Set-Cookie2", [])
        ns_hdrs = headers.get_all("Set-Cookie", [])
        self._policy._now = self._now = int(time.time())

        rfc2965 = self._policy.rfc2965
        netscape = self._policy.netscape

        ikiwa ((not rfc2965_hdrs and not ns_hdrs) or
            (not ns_hdrs and not rfc2965) or
            (not rfc2965_hdrs and not netscape) or
            (not netscape and not rfc2965)):
            rudisha []  # no relevant cookie headers: quick exit

        try:
            cookies = self._cookies_kutoka_attrs_set(
                split_header_words(rfc2965_hdrs), request)
        except Exception:
            _warn_unhandled_exception()
            cookies = []

        ikiwa ns_hdrs and netscape:
            try:
                # RFC 2109 and Netscape cookies
                ns_cookies = self._cookies_kutoka_attrs_set(
                    parse_ns_headers(ns_hdrs), request)
            except Exception:
                _warn_unhandled_exception()
                ns_cookies = []
            self._process_rfc2109_cookies(ns_cookies)

            # Look for Netscape cookies (kutoka Set-Cookie headers) that match
            # corresponding RFC 2965 cookies (kutoka Set-Cookie2 headers).
            # For each match, keep the RFC 2965 cookie and ignore the Netscape
            # cookie (RFC 2965 section 9.1).  Actually, RFC 2109 cookies are
            # bundled in with the Netscape cookies for this purpose, which is
            # reasonable behaviour.
            ikiwa rfc2965:
                lookup = {}
                for cookie in cookies:
                    lookup[(cookie.domain, cookie.path, cookie.name)] = None

                eleza no_matching_rfc2965(ns_cookie, lookup=lookup):
                    key = ns_cookie.domain, ns_cookie.path, ns_cookie.name
                    rudisha key not in lookup
                ns_cookies = filter(no_matching_rfc2965, ns_cookies)

            ikiwa ns_cookies:
                cookies.extend(ns_cookies)

        rudisha cookies

    eleza set_cookie_if_ok(self, cookie, request):
        """Set a cookie ikiwa policy says it's OK to do so."""
        self._cookies_lock.acquire()
        try:
            self._policy._now = self._now = int(time.time())

            ikiwa self._policy.set_ok(cookie, request):
                self.set_cookie(cookie)


        finally:
            self._cookies_lock.release()

    eleza set_cookie(self, cookie):
        """Set a cookie, without checking whether or not it should be set."""
        c = self._cookies
        self._cookies_lock.acquire()
        try:
            ikiwa cookie.domain not in c: c[cookie.domain] = {}
            c2 = c[cookie.domain]
            ikiwa cookie.path not in c2: c2[cookie.path] = {}
            c3 = c2[cookie.path]
            c3[cookie.name] = cookie
        finally:
            self._cookies_lock.release()

    eleza extract_cookies(self, response, request):
        """Extract cookies kutoka response, where allowable given the request."""
        _debug("extract_cookies: %s", response.info())
        self._cookies_lock.acquire()
        try:
            for cookie in self.make_cookies(response, request):
                ikiwa self._policy.set_ok(cookie, request):
                    _debug(" setting cookie: %s", cookie)
                    self.set_cookie(cookie)
        finally:
            self._cookies_lock.release()

    eleza clear(self, domain=None, path=None, name=None):
        """Clear some cookies.

        Invoking this method without arguments will clear all cookies.  If
        given a single argument, only cookies belonging to that domain will be
        removed.  If given two arguments, cookies belonging to the specified
        path within that domain are removed.  If given three arguments, then
        the cookie with the specified name, path and domain is removed.

        Raises KeyError ikiwa no matching cookie exists.

        """
        ikiwa name is not None:
            ikiwa (domain is None) or (path is None):
                raise ValueError(
                    "domain and path must be given to remove a cookie by name")
            del self._cookies[domain][path][name]
        elikiwa path is not None:
            ikiwa domain is None:
                raise ValueError(
                    "domain must be given to remove cookies by path")
            del self._cookies[domain][path]
        elikiwa domain is not None:
            del self._cookies[domain]
        else:
            self._cookies = {}

    eleza clear_session_cookies(self):
        """Discard all session cookies.

        Note that the .save() method won't save session cookies anyway, unless
        you ask otherwise by passing a true ignore_discard argument.

        """
        self._cookies_lock.acquire()
        try:
            for cookie in self:
                ikiwa cookie.discard:
                    self.clear(cookie.domain, cookie.path, cookie.name)
        finally:
            self._cookies_lock.release()

    eleza clear_expired_cookies(self):
        """Discard all expired cookies.

        You probably don't need to call this method: expired cookies are never
        sent back to the server (provided you're using DefaultCookiePolicy),
        this method is called by CookieJar itself every so often, and the
        .save() method won't save expired cookies anyway (unless you ask
        otherwise by passing a true ignore_expires argument).

        """
        self._cookies_lock.acquire()
        try:
            now = time.time()
            for cookie in self:
                ikiwa cookie.is_expired(now):
                    self.clear(cookie.domain, cookie.path, cookie.name)
        finally:
            self._cookies_lock.release()

    eleza __iter__(self):
        rudisha deepvalues(self._cookies)

    eleza __len__(self):
        """Return number of contained cookies."""
        i = 0
        for cookie in self: i = i + 1
        rudisha i

    eleza __repr__(self):
        r = []
        for cookie in self: r.append(repr(cookie))
        rudisha "<%s[%s]>" % (self.__class__.__name__, ", ".join(r))

    eleza __str__(self):
        r = []
        for cookie in self: r.append(str(cookie))
        rudisha "<%s[%s]>" % (self.__class__.__name__, ", ".join(r))


# derives kutoka OSError for backwards-compatibility with Python 2.4.0
kundi LoadError(OSError): pass

kundi FileCookieJar(CookieJar):
    """CookieJar that can be loaded kutoka and saved to a file."""

    eleza __init__(self, filename=None, delayload=False, policy=None):
        """
        Cookies are NOT loaded kutoka the named file until either the .load() or
        .revert() method is called.

        """
        CookieJar.__init__(self, policy)
        ikiwa filename is not None:
            filename = os.fspath(filename)
        self.filename = filename
        self.delayload = bool(delayload)

    eleza save(self, filename=None, ignore_discard=False, ignore_expires=False):
        """Save cookies to a file."""
        raise NotImplementedError()

    eleza load(self, filename=None, ignore_discard=False, ignore_expires=False):
        """Load cookies kutoka a file."""
        ikiwa filename is None:
            ikiwa self.filename is not None: filename = self.filename
            else: raise ValueError(MISSING_FILENAME_TEXT)

        with open(filename) as f:
            self._really_load(f, filename, ignore_discard, ignore_expires)

    eleza revert(self, filename=None,
               ignore_discard=False, ignore_expires=False):
        """Clear all cookies and reload cookies kutoka a saved file.

        Raises LoadError (or OSError) ikiwa reversion is not successful; the
        object's state will not be altered ikiwa this happens.

        """
        ikiwa filename is None:
            ikiwa self.filename is not None: filename = self.filename
            else: raise ValueError(MISSING_FILENAME_TEXT)

        self._cookies_lock.acquire()
        try:

            old_state = copy.deepcopy(self._cookies)
            self._cookies = {}
            try:
                self.load(filename, ignore_discard, ignore_expires)
            except OSError:
                self._cookies = old_state
                raise

        finally:
            self._cookies_lock.release()


eleza lwp_cookie_str(cookie):
    """Return string representation of Cookie in the LWP cookie file format.

    Actually, the format is extended a bit -- see module docstring.

    """
    h = [(cookie.name, cookie.value),
         ("path", cookie.path),
         ("domain", cookie.domain)]
    ikiwa cookie.port is not None: h.append(("port", cookie.port))
    ikiwa cookie.path_specified: h.append(("path_spec", None))
    ikiwa cookie.port_specified: h.append(("port_spec", None))
    ikiwa cookie.domain_initial_dot: h.append(("domain_dot", None))
    ikiwa cookie.secure: h.append(("secure", None))
    ikiwa cookie.expires: h.append(("expires",
                               time2isoz(float(cookie.expires))))
    ikiwa cookie.discard: h.append(("discard", None))
    ikiwa cookie.comment: h.append(("comment", cookie.comment))
    ikiwa cookie.comment_url: h.append(("commenturl", cookie.comment_url))

    keys = sorted(cookie._rest.keys())
    for k in keys:
        h.append((k, str(cookie._rest[k])))

    h.append(("version", str(cookie.version)))

    rudisha join_header_words([h])

kundi LWPCookieJar(FileCookieJar):
    """
    The LWPCookieJar saves a sequence of "Set-Cookie3" lines.
    "Set-Cookie3" is the format used by the libwww-perl library, not known
    to be compatible with any browser, but which is easy to read and
    doesn't lose information about RFC 2965 cookies.

    Additional methods

    as_lwp_str(ignore_discard=True, ignore_expired=True)

    """

    eleza as_lwp_str(self, ignore_discard=True, ignore_expires=True):
        """Return cookies as a string of "\\n"-separated "Set-Cookie3" headers.

        ignore_discard and ignore_expires: see docstring for FileCookieJar.save

        """
        now = time.time()
        r = []
        for cookie in self:
            ikiwa not ignore_discard and cookie.discard:
                continue
            ikiwa not ignore_expires and cookie.is_expired(now):
                continue
            r.append("Set-Cookie3: %s" % lwp_cookie_str(cookie))
        rudisha "\n".join(r+[""])

    eleza save(self, filename=None, ignore_discard=False, ignore_expires=False):
        ikiwa filename is None:
            ikiwa self.filename is not None: filename = self.filename
            else: raise ValueError(MISSING_FILENAME_TEXT)

        with open(filename, "w") as f:
            # There really isn't an LWP Cookies 2.0 format, but this indicates
            # that there is extra information in here (domain_dot and
            # port_spec) while still being compatible with libwww-perl, I hope.
            f.write("#LWP-Cookies-2.0\n")
            f.write(self.as_lwp_str(ignore_discard, ignore_expires))

    eleza _really_load(self, f, filename, ignore_discard, ignore_expires):
        magic = f.readline()
        ikiwa not self.magic_re.search(magic):
            msg = ("%r does not look like a Set-Cookie3 (LWP) format "
                   "file" % filename)
            raise LoadError(msg)

        now = time.time()

        header = "Set-Cookie3:"
        boolean_attrs = ("port_spec", "path_spec", "domain_dot",
                         "secure", "discard")
        value_attrs = ("version",
                       "port", "path", "domain",
                       "expires",
                       "comment", "commenturl")

        try:
            while 1:
                line = f.readline()
                ikiwa line == "": break
                ikiwa not line.startswith(header):
                    continue
                line = line[len(header):].strip()

                for data in split_header_words([line]):
                    name, value = data[0]
                    standard = {}
                    rest = {}
                    for k in boolean_attrs:
                        standard[k] = False
                    for k, v in data[1:]:
                        ikiwa k is not None:
                            lc = k.lower()
                        else:
                            lc = None
                        # don't lose case distinction for unknown fields
                        ikiwa (lc in value_attrs) or (lc in boolean_attrs):
                            k = lc
                        ikiwa k in boolean_attrs:
                            ikiwa v is None: v = True
                            standard[k] = v
                        elikiwa k in value_attrs:
                            standard[k] = v
                        else:
                            rest[k] = v

                    h = standard.get
                    expires = h("expires")
                    discard = h("discard")
                    ikiwa expires is not None:
                        expires = iso2time(expires)
                    ikiwa expires is None:
                        discard = True
                    domain = h("domain")
                    domain_specified = domain.startswith(".")
                    c = Cookie(h("version"), name, value,
                               h("port"), h("port_spec"),
                               domain, domain_specified, h("domain_dot"),
                               h("path"), h("path_spec"),
                               h("secure"),
                               expires,
                               discard,
                               h("comment"),
                               h("commenturl"),
                               rest)
                    ikiwa not ignore_discard and c.discard:
                        continue
                    ikiwa not ignore_expires and c.is_expired(now):
                        continue
                    self.set_cookie(c)
        except OSError:
            raise
        except Exception:
            _warn_unhandled_exception()
            raise LoadError("invalid Set-Cookie3 format file %r: %r" %
                            (filename, line))


kundi MozillaCookieJar(FileCookieJar):
    """

    WARNING: you may want to backup your browser's cookies file ikiwa you use
    this kundi to save cookies.  I *think* it works, but there have been
    bugs in the past!

    This kundi differs kutoka CookieJar only in the format it uses to save and
    load cookies to and kutoka a file.  This kundi uses the Mozilla/Netscape
    `cookies.txt' format.  lynx uses this file format, too.

    Don't expect cookies saved while the browser is running to be noticed by
    the browser (in fact, Mozilla on unix will overwrite your saved cookies if
    you change them on disk while it's running; on Windows, you probably can't
    save at all while the browser is running).

    Note that the Mozilla/Netscape format will downgrade RFC2965 cookies to
    Netscape cookies on saving.

    In particular, the cookie version and port number information is lost,
    together with information about whether or not Path, Port and Discard were
    specified by the Set-Cookie2 (or Set-Cookie) header, and whether or not the
    domain as set in the HTTP header started with a dot (yes, I'm aware some
    domains in Netscape files start with a dot and some don't -- trust me, you
    really don't want to know any more about this).

    Note that though Mozilla and Netscape use the same format, they use
    slightly different headers.  The kundi saves cookies using the Netscape
    header by default (Mozilla can cope with that).

    """
    magic_re = re.compile("#( Netscape)? HTTP Cookie File")
    header = """\
# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

"""

    eleza _really_load(self, f, filename, ignore_discard, ignore_expires):
        now = time.time()

        magic = f.readline()
        ikiwa not self.magic_re.search(magic):
            raise LoadError(
                "%r does not look like a Netscape format cookies file" %
                filename)

        try:
            while 1:
                line = f.readline()
                ikiwa line == "": break

                # last field may be absent, so keep any trailing tab
                ikiwa line.endswith("\n"): line = line[:-1]

                # skip comments and blank lines XXX what is $ for?
                ikiwa (line.strip().startswith(("#", "$")) or
                    line.strip() == ""):
                    continue

                domain, domain_specified, path, secure, expires, name, value = \
                        line.split("\t")
                secure = (secure == "TRUE")
                domain_specified = (domain_specified == "TRUE")
                ikiwa name == "":
                    # cookies.txt regards 'Set-Cookie: foo' as a cookie
                    # with no name, whereas http.cookiejar regards it as a
                    # cookie with no value.
                    name = value
                    value = None

                initial_dot = domain.startswith(".")
                assert domain_specified == initial_dot

                discard = False
                ikiwa expires == "":
                    expires = None
                    discard = True

                # assume path_specified is false
                c = Cookie(0, name, value,
                           None, False,
                           domain, domain_specified, initial_dot,
                           path, False,
                           secure,
                           expires,
                           discard,
                           None,
                           None,
                           {})
                ikiwa not ignore_discard and c.discard:
                    continue
                ikiwa not ignore_expires and c.is_expired(now):
                    continue
                self.set_cookie(c)

        except OSError:
            raise
        except Exception:
            _warn_unhandled_exception()
            raise LoadError("invalid Netscape format cookies file %r: %r" %
                            (filename, line))

    eleza save(self, filename=None, ignore_discard=False, ignore_expires=False):
        ikiwa filename is None:
            ikiwa self.filename is not None: filename = self.filename
            else: raise ValueError(MISSING_FILENAME_TEXT)

        with open(filename, "w") as f:
            f.write(self.header)
            now = time.time()
            for cookie in self:
                ikiwa not ignore_discard and cookie.discard:
                    continue
                ikiwa not ignore_expires and cookie.is_expired(now):
                    continue
                ikiwa cookie.secure: secure = "TRUE"
                else: secure = "FALSE"
                ikiwa cookie.domain.startswith("."): initial_dot = "TRUE"
                else: initial_dot = "FALSE"
                ikiwa cookie.expires is not None:
                    expires = str(cookie.expires)
                else:
                    expires = ""
                ikiwa cookie.value is None:
                    # cookies.txt regards 'Set-Cookie: foo' as a cookie
                    # with no name, whereas http.cookiejar regards it as a
                    # cookie with no value.
                    name = ""
                    value = cookie.name
                else:
                    name = cookie.name
                    value = cookie.value
                f.write(
                    "\t".join([cookie.domain, initial_dot, cookie.path,
                               secure, expires, name, value])+
                    "\n")
