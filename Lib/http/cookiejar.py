r"""HTTP cookie handling kila web clients.

This module has (now fairly distant) origins kwenye Gisle Aas' Perl module
HTTP::Cookies, kutoka the libwww-perl library.

Docstrings, comments na debug strings kwenye this code refer to the
attributes of the HTTP cookie system as cookie-attributes, to distinguish
them clearly kutoka Python attributes.

Class diagram (note that BSDDBCookieJar na the MSIE* classes are not
distributed ukijumuisha the Python standard library, but are available from
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
agiza http.client  # only kila the default HTTP port
kutoka calendar agiza timegm

debug = Uongo   # set to Kweli to enable debugging via the logging module
logger = Tupu

eleza _debug(*args):
    ikiwa sio debug:
        return
    global logger
    ikiwa sio logger:
        agiza logging
        logger = logging.getLogger("http.cookiejar")
    rudisha logger.debug(*args)


DEFAULT_HTTP_PORT = str(http.client.HTTP_PORT)
MISSING_FILENAME_TEXT = ("a filename was sio supplied (nor was the CookieJar "
                         "instance initialised ukijumuisha one)")

eleza _warn_unhandled_exception():
    # There are a few catch-all tatizo: statements kwenye this module, for
    # catching input that's bad kwenye unexpected ways.  Warn ikiwa any
    # exceptions are caught there.
    agiza io, warnings, traceback
    f = io.StringIO()
    traceback.print_exc(Tupu, f)
    msg = f.getvalue()
    warnings.warn("http.cookiejar bug!\n%s" % msg, stacklevel=2)


# Date/time conversion
# -----------------------------------------------------------------------------

EPOCH_YEAR = 1970
eleza _timegm(tt):
    year, month, mday, hour, min, sec = tt[:6]
    ikiwa ((year >= EPOCH_YEAR) na (1 <= month <= 12) na (1 <= mday <= 31) and
        (0 <= hour <= 24) na (0 <= min <= 59) na (0 <= sec <= 61)):
        rudisha timegm(tt)
    isipokua:
        rudisha Tupu

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS_LOWER = []
kila month kwenye MONTHS: MONTHS_LOWER.append(month.lower())

eleza time2isoz(t=Tupu):
    """Return a string representing time kwenye seconds since epoch, t.

    If the function ni called without an argument, it will use the current
    time.

    The format of the returned string ni like "YYYY-MM-DD hh:mm:ssZ",
    representing Universal Time (UTC, aka GMT).  An example of this format is:

    1994-11-24 08:49:37Z

    """
    ikiwa t ni Tupu:
        dt = datetime.datetime.utcnow()
    isipokua:
        dt = datetime.datetime.utcfromtimestamp(t)
    rudisha "%04d-%02d-%02d %02d:%02d:%02dZ" % (
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

eleza time2netscape(t=Tupu):
    """Return a string representing time kwenye seconds since epoch, t.

    If the function ni called without an argument, it will use the current
    time.

    The format of the returned string ni like this:

    Wed, DD-Mon-YYYY HH:MM:SS GMT

    """
    ikiwa t ni Tupu:
        dt = datetime.datetime.utcnow()
    isipokua:
        dt = datetime.datetime.utcfromtimestamp(t)
    rudisha "%s, %02d-%s-%04d %02d:%02d:%02d GMT" % (
        DAYS[dt.weekday()], dt.day, MONTHS[dt.month-1],
        dt.year, dt.hour, dt.minute, dt.second)


UTC_ZONES = {"GMT": Tupu, "UTC": Tupu, "UT": Tupu, "Z": Tupu}

TIMEZONE_RE = re.compile(r"^([-+])?(\d\d?):?(\d\d)?$", re.ASCII)
eleza offset_from_tz_string(tz):
    offset = Tupu
    ikiwa tz kwenye UTC_ZONES:
        offset = 0
    isipokua:
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
        rudisha Tupu

    # translate month name to number
    # month numbers start ukijumuisha 1 (January)
    jaribu:
        mon = MONTHS_LOWER.index(mon.lower())+1
    except ValueError:
        # maybe it's already a number
        jaribu:
            imon = int(mon)
        except ValueError:
            rudisha Tupu
        ikiwa 1 <= imon <= 12:
            mon = imon
        isipokua:
            rudisha Tupu

    # make sure clock elements are defined
    ikiwa hr ni Tupu: hr = 0
    ikiwa min ni Tupu: min = 0
    ikiwa sec ni Tupu: sec = 0

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
            isipokua: yr = yr - 100

    # convert UTC time tuple to seconds since epoch (not timezone-adjusted)
    t = _timegm((yr, mon, day, hr, min, sec, tz))

    ikiwa t ni sio Tupu:
        # adjust time using timezone string, to get absolute time since epoch
        ikiwa tz ni Tupu:
            tz = "UTC"
        tz = tz.upper()
        offset = offset_from_tz_string(tz)
        ikiwa offset ni Tupu:
            rudisha Tupu
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
    (?:\(\w+\))?       # ASCII representation of timezone kwenye parens.
       \s*$""", re.X | re.ASCII)
eleza http2time(text):
    """Returns time kwenye seconds since epoch of time represented by a string.

    Return value ni an integer.

    Tupu ni returned ikiwa the format of str ni unrecognized, the time ni outside
    the representable range, ama the timezone string ni sio recognized.  If the
    string contains no timezone, UTC ni assumed.

    The timezone kwenye the string may be numerical (like "-0800" ama "+0100") ama a
    string timezone (like "UTC", "GMT", "BST" ama "EST").  Currently, only the
    timezone strings equivalent to UTC (zero offset) are known to the function.

    The function loosely parses the following formats:

    Wed, 09 Feb 1994 22:23:32 GMT       -- HTTP format
    Tuesday, 08-Feb-94 14:15:29 GMT     -- old rfc850 HTTP format
    Tuesday, 08-Feb-1994 14:15:29 GMT   -- broken rfc850 HTTP format
    09 Feb 1994 22:23:32 GMT            -- HTTP format (no weekday)
    08-Feb-94 14:15:29 GMT              -- rfc850 format (no weekday)
    08-Feb-1994 14:15:29 GMT            -- broken rfc850 format (no weekday)

    The parser ignores leading na trailing whitespace.  The time may be
    absent.

    If the year ni given ukijumuisha only 2 digits, the function will select the
    century that makes the year closest to the current date.

    """
    # fast exit kila strictly conforming string
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

    # tz ni time zone specifier string
    day, mon, yr, hr, min, sec, tz = [Tupu]*7

    # loose regexp parse
    m = LOOSE_HTTP_DATE_RE.search(text)
    ikiwa m ni sio Tupu:
        day, mon, yr, hr, min, sec, tz = m.groups()
    isipokua:
        rudisha Tupu  # bad format

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
    |Z|z)?               # timezone  (Z ni "zero meridian", i.e. GMT)
      \s*$""", re.X | re. ASCII)
eleza iso2time(text):
    """
    As kila http2time, but parses the ISO 8601 formats:

    1994-02-03 14:15:29 -0100    -- ISO 8601 format
    1994-02-03 14:15:29          -- zone ni optional
    1994-02-03                   -- only date
    1994-02-03T14:15:29          -- Use T as separator
    19940203T141529Z             -- ISO 8601 compact format
    19940203                     -- only date

    """
    # clean up
    text = text.lstrip()

    # tz ni time zone specifier string
    day, mon, yr, hr, min, sec, tz = [Tupu]*7

    # loose regexp parse
    m = ISO_DATE_RE.search(text)
    ikiwa m ni sio Tupu:
        # XXX there's an extra bit of the timezone I'm ignoring here: is
        #   this the right thing to do?
        yr, mon, day, hr, min, sec, tz, _ = m.groups()
    isipokua:
        rudisha Tupu  # bad format

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

    The function knows how to deal ukijumuisha ",", ";" na "=" as well as quoted
    values after "=".  A list of space separated tokens are parsed as ikiwa they
    were separated by ";".

    If the header_values passed as argument contains multiple values, then they
    are treated as ikiwa they were a single value separated by comma ",".

    This means that this function ni useful kila parsing header fields that
    follow this syntax (BNF as kutoka the HTTP/1.1 specification, but we relax
    the requirement kila tokens).

      headers           = #header
      header            = (token | parameter) *( [";"] (token | parameter))

      token             = 1*<any CHAR except CTLs ama separators>
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

    Each header ni represented by a list of key/value pairs.  The value kila a
    simple token (not part of a parameter) ni Tupu.  Syntactically incorrect
    headers will sio necessarily be parsed as you would want.

    This ni easier to describe ukijumuisha some examples:

    >>> split_header_words(['foo="bar"; port="80,81"; discard, bar=baz'])
    [[('foo', 'bar'), ('port', '80,81'), ('discard', Tupu)], [('bar', 'baz')]]
    >>> split_header_words(['text/html; charset="iso-8859-1"'])
    [[('text/html', Tupu), ('charset', 'iso-8859-1')]]
    >>> split_header_words([r'Basic realm="\"foo\bar\""'])
    [[('Basic', Tupu), ('realm', '"foobar"')]]

    """
    assert sio isinstance(header_values, str)
    result = []
    kila text kwenye header_values:
        orig_text = text
        pairs = []
        wakati text:
            m = HEADER_TOKEN_RE.search(text)
            ikiwa m:
                text = unmatched(m)
                name = m.group(1)
                m = HEADER_QUOTED_VALUE_RE.search(text)
                ikiwa m:  # quoted value
                    text = unmatched(m)
                    value = m.group(1)
                    value = HEADER_ESCAPE_RE.sub(r"\1", value)
                isipokua:
                    m = HEADER_VALUE_RE.search(text)
                    ikiwa m:  # unquoted value
                        text = unmatched(m)
                        value = m.group(1)
                        value = value.rstrip()
                    isipokua:
                        # no value, a lone token
                        value = Tupu
                pairs.append((name, value))
            elikiwa text.lstrip().startswith(","):
                # concatenated headers, as per RFC 2616 section 4.2
                text = text.lstrip()[1:]
                ikiwa pairs: result.append(pairs)
                pairs = []
            isipokua:
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

    Takes a list of lists of (key, value) pairs na produces a single header
    value.  Attribute values are quoted ikiwa needed.

    >>> join_header_words([[("text/plain", Tupu), ("charset", "iso-8859-1")]])
    'text/plain; charset="iso-8859-1"'
    >>> join_header_words([[("text/plain", Tupu)], [("charset", "iso-8859-1")]])
    'text/plain, charset="iso-8859-1"'

    """
    headers = []
    kila pairs kwenye lists:
        attr = []
        kila k, v kwenye pairs:
            ikiwa v ni sio Tupu:
                ikiwa sio re.search(r"^\w+$", v):
                    v = HEADER_JOIN_ESCAPE_RE.sub(r"\\\1", v)  # escape " na \
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
    """Ad-hoc parser kila Netscape protocol cookie-attributes.

    The old Netscape cookie format kila Set-Cookie can kila instance contain
    an unquoted "," kwenye the expires field, so we have to use this ad-hoc
    parser instead of split_header_words.

    XXX This may sio make the best possible effort to parse all the crap
    that Netscape Cookie headers contain.  Ronald Tschalar's HTTPClient
    parser ni probably better, so could do worse than following that if
    this ever gives any trouble.

    Currently, this ni also used kila parsing RFC 2109 cookies.

    """
    known_attrs = ("expires", "domain", "path", "secure",
                   # RFC 2109 attrs (may turn up kwenye Netscape cookies, too)
                   "version", "port", "max-age")

    result = []
    kila ns_header kwenye ns_headers:
        pairs = []
        version_set = Uongo

        # XXX: The following does sio strictly adhere to RFCs kwenye that empty
        # names na values are legal (the former will only appear once na will
        # be overwritten ikiwa multiple occurrences are present). This is
        # mostly to deal ukijumuisha backwards compatibility.
        kila ii, param kwenye enumerate(ns_header.split(';')):
            param = param.strip()

            key, sep, val = param.partition('=')
            key = key.strip()

            ikiwa sio key:
                ikiwa ii == 0:
                    koma
                isipokua:
                    endelea

            # allow kila a distinction between present na empty na missing
            # altogether
            val = val.strip() ikiwa sep isipokua Tupu

            ikiwa ii != 0:
                lc = key.lower()
                ikiwa lc kwenye known_attrs:
                    key = lc

                ikiwa key == "version":
                    # This ni an RFC 2109 cookie.
                    ikiwa val ni sio Tupu:
                        val = strip_quotes(val)
                    version_set = Kweli
                elikiwa key == "expires":
                    # convert expires date to seconds since epoch
                    ikiwa val ni sio Tupu:
                        val = http2time(strip_quotes(val))  # Tupu ikiwa invalid
            pairs.append((key, val))

        ikiwa pairs:
            ikiwa sio version_set:
                pairs.append(("version", "0"))
            result.append(pairs)

    rudisha result


IPV4_RE = re.compile(r"\.\d+$", re.ASCII)
eleza is_HDN(text):
    """Return Kweli ikiwa text ni a host domain name."""
    # XXX
    # This may well be wrong.  Which RFC ni HDN defined in, ikiwa any (for
    #  the purposes of RFC 2965)?
    # For the current implementation, what about IPv6?  Remember to look
    #  at other uses of IPV4_RE also, ikiwa change this.
    ikiwa IPV4_RE.search(text):
        rudisha Uongo
    ikiwa text == "":
        rudisha Uongo
    ikiwa text[0] == "." ama text[-1] == ".":
        rudisha Uongo
    rudisha Kweli

eleza domain_match(A, B):
    """Return Kweli ikiwa domain A domain-matches domain B, according to RFC 2965.

    A na B may be host domain names ama IP addresses.

    RFC 2965, section 1:

    Host names can be specified either as an IP address ama a HDN string.
    Sometimes we compare one host name ukijumuisha another.  (Such comparisons SHALL
    be case-insensitive.)  Host A's name domain-matches host B's if

         *  their host name strings string-compare equal; or

         * A ni a HDN string na has the form NB, where N ni a non-empty
            name string, B has the form .B', na B' ni a HDN string.  (So,
            x.y.com domain-matches .Y.com but sio Y.com.)

    Note that domain-match ni sio a commutative operation: a.b.c.com
    domain-matches .c.com, but sio the reverse.

    """
    # Note that, ikiwa A ama B are IP addresses, the only relevant part of the
    # definition of the domain-match algorithm ni the direct string-compare.
    A = A.lower()
    B = B.lower()
    ikiwa A == B:
        rudisha Kweli
    ikiwa sio is_HDN(A):
        rudisha Uongo
    i = A.rfind(B)
    ikiwa i == -1 ama i == 0:
        # A does sio have form NB, ama N ni the empty string
        rudisha Uongo
    ikiwa sio B.startswith("."):
        rudisha Uongo
    ikiwa sio is_HDN(B[1:]):
        rudisha Uongo
    rudisha Kweli

eleza liberal_is_HDN(text):
    """Return Kweli ikiwa text ni a sort-of-like a host domain name.

    For accepting/blocking domains.

    """
    ikiwa IPV4_RE.search(text):
        rudisha Uongo
    rudisha Kweli

eleza user_domain_match(A, B):
    """For blocking/accepting domains.

    A na B may be host domain names ama IP addresses.

    """
    A = A.lower()
    B = B.lower()
    ikiwa sio (liberal_is_HDN(A) na liberal_is_HDN(B)):
        ikiwa A == B:
            # equal IP addresses
            rudisha Kweli
        rudisha Uongo
    initial_dot = B.startswith(".")
    ikiwa initial_dot na A.endswith(B):
        rudisha Kweli
    ikiwa sio initial_dot na A == B:
        rudisha Kweli
    rudisha Uongo

cut_port_re = re.compile(r":\d+$", re.ASCII)
eleza request_host(request):
    """Return request-host, as defined by RFC 2965.

    Variation kutoka RFC: returned value ni lowercased, kila convenient
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
    ikiwa req_host.find(".") == -1 na sio IPV4_RE.search(req_host):
        erhn = req_host + ".local"
    rudisha req_host, erhn

eleza request_path(request):
    """Path component of request-URI, as defined by RFC 2965."""
    url = request.get_full_url()
    parts = urllib.parse.urlsplit(url)
    path = escape_path(parts.path)
    ikiwa sio path.startswith("/"):
        # fix bad RFC 2396 absoluteURI
        path = "/" + path
    rudisha path

eleza request_port(request):
    host = request.host
    i = host.find(':')
    ikiwa i >= 0:
        port = host[i+1:]
        jaribu:
            int(port)
        except ValueError:
            _debug("nonnumeric port: '%s'", port)
            rudisha Tupu
    isipokua:
        port = DEFAULT_HTTP_PORT
    rudisha port

# Characters kwenye addition to A-Z, a-z, 0-9, '_', '.', na '-' that don't
# need to be escaped to form a valid HTTP URL (RFCs 2396 na 1738).
HTTP_PATH_SAFE = "%/;:@&=+$,!~*'()"
ESCAPED_CHAR_RE = re.compile(r"%([0-9a-fA-F][0-9a-fA-F])")
eleza uppercase_escaped_char(match):
    rudisha "%%%s" % match.group(1).upper()
eleza escape_path(path):
    """Escape any invalid characters kwenye HTTP URL, na uppercase all escapes."""
    # There's no knowing what character encoding was used to create URLs
    # containing %-escapes, but since we have to pick one to escape invalid
    # path characters, we pick UTF-8, as recommended kwenye the HTML 4.0
    # specification:
    # http://www.w3.org/TR/REC-html40/appendix/notes.html#h-B.2.1
    # And here, kind of: draft-fielding-uri-rfc2396bis-03
    # (And kwenye draft IRI specification: draft-duerst-iri-05)
    # (And here, kila new URI schemes: RFC 2718)
    path = urllib.parse.quote(path, HTTP_PATH_SAFE)
    path = ESCAPED_CHAR_RE.sub(uppercase_escaped_char, path)
    rudisha path

eleza reach(h):
    """Return reach of host h, as defined by RFC 2965, section 1.

    The reach R of a host name H ni defined as follows:

       *  If

          -  H ni the host domain name of a host; and,

          -  H has the form A.B; and

          -  A has no embedded (that is, interior) dots; and

          -  B has at least one embedded dot, ama B ni the string "local".
             then the reach of H ni .B.

       *  Otherwise, the reach of H ni H.

    >>> reach("www.acme.com")
    '.acme.com'
    >>> reach("acme.com")
    'acme.com'
    >>> reach("acme.local")
    '.local'

    """
    i = h.find(".")
    ikiwa i >= 0:
        #a = h[:i]  # this line ni only here to show what a is
        b = h[i+1:]
        i = b.find(".")
        ikiwa is_HDN(h) na (i >= 0 ama b == "local"):
            rudisha "."+b
    rudisha h

eleza is_third_party(request):
    """

    RFC 2965, section 3.3.6:

        An unverifiable transaction ni to a third-party host ikiwa its request-
        host U does sio domain-match the reach R of the request-host O kwenye the
        origin transaction.

    """
    req_host = request_host(request)
    ikiwa sio domain_match(req_host, reach(request.origin_req_host)):
        rudisha Kweli
    isipokua:
        rudisha Uongo


kundi Cookie:
    """HTTP Cookie.

    This kundi represents both Netscape na RFC 2965 cookies.

    This ni deliberately a very simple class.  It just holds attributes.  It's
    possible to construct Cookie instances that don't comply ukijumuisha the cookie
    standards.  CookieJar.make_cookies ni the factory function kila Cookie
    objects -- it deals ukijumuisha cookie parsing, supplying defaults, and
    normalising to the representation used kwenye this class.  CookiePolicy is
    responsible kila checking them to see whether they should be accepted from
    na returned to the server.

    Note that the port may be present kwenye the headers, but unspecified ("Port"
    rather than"Port=80", kila example); ikiwa this ni the case, port ni Tupu.

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
                 rfc2109=Uongo,
                 ):

        ikiwa version ni sio Tupu: version = int(version)
        ikiwa expires ni sio Tupu: expires = int(float(expires))
        ikiwa port ni Tupu na port_specified ni Kweli:
             ashiria ValueError("ikiwa port ni Tupu, port_specified must be false")

        self.version = version
        self.name = name
        self.value = value
        self.port = port
        self.port_specified = port_specified
        # normalise case, as per RFC 2965 section 3.3.3
        self.domain = domain.lower()
        self.domain_specified = domain_specified
        # Sigh.  We need to know whether the domain given kwenye the
        # cookie-attribute had an initial dot, kwenye order to follow RFC 2965
        # (as clarified kwenye draft errata).  Needed kila the returned $Domain
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
        rudisha name kwenye self._rest
    eleza get_nonstandard_attr(self, name, default=Tupu):
        rudisha self._rest.get(name, default)
    eleza set_nonstandard_attr(self, name, value):
        self._rest[name] = value

    eleza is_expired(self, now=Tupu):
        ikiwa now ni Tupu: now = time.time()
        ikiwa (self.expires ni sio Tupu) na (self.expires <= now):
            rudisha Kweli
        rudisha Uongo

    eleza __str__(self):
        ikiwa self.port ni Tupu: p = ""
        isipokua: p = ":"+self.port
        limit = self.domain + p + self.path
        ikiwa self.value ni sio Tupu:
            namevalue = "%s=%s" % (self.name, self.value)
        isipokua:
            namevalue = self.name
        rudisha "<Cookie %s kila %s>" % (namevalue, limit)

    eleza __repr__(self):
        args = []
        kila name kwenye ("version", "name", "value",
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
    """Defines which cookies get accepted kutoka na returned to server.

    May also modify cookies, though this ni probably a bad idea.

    The subkundi DefaultCookiePolicy defines the standard rules kila Netscape
    na RFC 2965 cookies -- override that ikiwa you want a customized policy.

    """
    eleza set_ok(self, cookie, request):
        """Return true ikiwa (and only if) cookie should be accepted kutoka server.

        Currently, pre-expired cookies never get this far -- the CookieJar
        kundi deletes such cookies itself.

        """
         ashiria NotImplementedError()

    eleza return_ok(self, cookie, request):
        """Return true ikiwa (and only if) cookie should be returned to server."""
         ashiria NotImplementedError()

    eleza domain_return_ok(self, domain, request):
        """Return false ikiwa cookies should sio be returned, given cookie domain.
        """
        rudisha Kweli

    eleza path_return_ok(self, path, request):
        """Return false ikiwa cookies should sio be returned, given cookie path.
        """
        rudisha Kweli


kundi DefaultCookiePolicy(CookiePolicy):
    """Implements the standard rules kila accepting na returning cookies."""

    DomainStrictNoDots = 1
    DomainStrictNonDomain = 2
    DomainRFC2965Match = 4

    DomainLiberal = 0
    DomainStrict = DomainStrictNoDots|DomainStrictNonDomain

    eleza __init__(self,
                 blocked_domains=Tupu, allowed_domains=Tupu,
                 netscape=Kweli, rfc2965=Uongo,
                 rfc2109_as_netscape=Tupu,
                 hide_cookie2=Uongo,
                 strict_domain=Uongo,
                 strict_rfc2965_unverifiable=Kweli,
                 strict_ns_unverifiable=Uongo,
                 strict_ns_domain=DomainLiberal,
                 strict_ns_set_initial_dollar=Uongo,
                 strict_ns_set_path=Uongo,
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

        ikiwa blocked_domains ni sio Tupu:
            self._blocked_domains = tuple(blocked_domains)
        isipokua:
            self._blocked_domains = ()

        ikiwa allowed_domains ni sio Tupu:
            allowed_domains = tuple(allowed_domains)
        self._allowed_domains = allowed_domains

    eleza blocked_domains(self):
        """Return the sequence of blocked domains (as a tuple)."""
        rudisha self._blocked_domains
    eleza set_blocked_domains(self, blocked_domains):
        """Set the sequence of blocked domains."""
        self._blocked_domains = tuple(blocked_domains)

    eleza is_blocked(self, domain):
        kila blocked_domain kwenye self._blocked_domains:
            ikiwa user_domain_match(domain, blocked_domain):
                rudisha Kweli
        rudisha Uongo

    eleza allowed_domains(self):
        """Return Tupu, ama the sequence of allowed domains (as a tuple)."""
        rudisha self._allowed_domains
    eleza set_allowed_domains(self, allowed_domains):
        """Set the sequence of allowed domains, ama Tupu."""
        ikiwa allowed_domains ni sio Tupu:
            allowed_domains = tuple(allowed_domains)
        self._allowed_domains = allowed_domains

    eleza is_not_allowed(self, domain):
        ikiwa self._allowed_domains ni Tupu:
            rudisha Uongo
        kila allowed_domain kwenye self._allowed_domains:
            ikiwa user_domain_match(domain, allowed_domain):
                rudisha Uongo
        rudisha Kweli

    eleza set_ok(self, cookie, request):
        """
        If you override .set_ok(), be sure to call this method.  If it returns
        false, so should your subkundi (assuming your subkundi wants to be more
        strict about which cookies to accept).

        """
        _debug(" - checking cookie %s=%s", cookie.name, cookie.value)

        assert cookie.name ni sio Tupu

        kila n kwenye "version", "verifiability", "name", "path", "domain", "port":
            fn_name = "set_ok_"+n
            fn = getattr(self, fn_name)
            ikiwa sio fn(cookie, request):
                rudisha Uongo

        rudisha Kweli

    eleza set_ok_version(self, cookie, request):
        ikiwa cookie.version ni Tupu:
            # Version ni always set to 0 by parse_ns_headers ikiwa it's a Netscape
            # cookie, so this must be an invalid RFC 2965 cookie.
            _debug("   Set-Cookie2 without version attribute (%s=%s)",
                   cookie.name, cookie.value)
            rudisha Uongo
        ikiwa cookie.version > 0 na sio self.rfc2965:
            _debug("   RFC 2965 cookies are switched off")
            rudisha Uongo
        elikiwa cookie.version == 0 na sio self.netscape:
            _debug("   Netscape cookies are switched off")
            rudisha Uongo
        rudisha Kweli

    eleza set_ok_verifiability(self, cookie, request):
        ikiwa request.unverifiable na is_third_party(request):
            ikiwa cookie.version > 0 na self.strict_rfc2965_unverifiable:
                _debug("   third-party RFC 2965 cookie during "
                             "unverifiable transaction")
                rudisha Uongo
            elikiwa cookie.version == 0 na self.strict_ns_unverifiable:
                _debug("   third-party Netscape cookie during "
                             "unverifiable transaction")
                rudisha Uongo
        rudisha Kweli

    eleza set_ok_name(self, cookie, request):
        # Try na stop servers setting V0 cookies designed to hack other
        # servers that know both V0 na V1 protocols.
        ikiwa (cookie.version == 0 na self.strict_ns_set_initial_dollar and
            cookie.name.startswith("$")):
            _debug("   illegal name (starts ukijumuisha '$'): '%s'", cookie.name)
            rudisha Uongo
        rudisha Kweli

    eleza set_ok_path(self, cookie, request):
        ikiwa cookie.path_specified:
            req_path = request_path(request)
            ikiwa ((cookie.version > 0 or
                 (cookie.version == 0 na self.strict_ns_set_path)) and
                sio self.path_return_ok(cookie.path, request)):
                _debug("   path attribute %s ni sio a prefix of request "
                       "path %s", cookie.path, req_path)
                rudisha Uongo
        rudisha Kweli

    eleza set_ok_domain(self, cookie, request):
        ikiwa self.is_blocked(cookie.domain):
            _debug("   domain %s ni kwenye user block-list", cookie.domain)
            rudisha Uongo
        ikiwa self.is_not_allowed(cookie.domain):
            _debug("   domain %s ni sio kwenye user allow-list", cookie.domain)
            rudisha Uongo
        ikiwa cookie.domain_specified:
            req_host, erhn = eff_request_host(request)
            domain = cookie.domain
            ikiwa self.strict_domain na (domain.count(".") >= 2):
                # XXX This should probably be compared ukijumuisha the Konqueror
                # (kcookiejar.cpp) na Mozilla implementations, but it's a
                # losing battle.
                i = domain.rfind(".")
                j = domain.rfind(".", 0, i)
                ikiwa j == 0:  # domain like .foo.bar
                    tld = domain[i+1:]
                    sld = domain[j+1:i]
                    ikiwa sld.lower() kwenye ("co", "ac", "com", "edu", "org", "net",
                       "gov", "mil", "int", "aero", "biz", "cat", "coop",
                       "info", "jobs", "mobi", "museum", "name", "pro",
                       "travel", "eu") na len(tld) == 2:
                        # domain like .co.uk
                        _debug("   country-code second level domain %s", domain)
                        rudisha Uongo
            ikiwa domain.startswith("."):
                undotted_domain = domain[1:]
            isipokua:
                undotted_domain = domain
            embedded_dots = (undotted_domain.find(".") >= 0)
            ikiwa sio embedded_dots na domain != ".local":
                _debug("   non-local domain %s contains no embedded dot",
                       domain)
                rudisha Uongo
            ikiwa cookie.version == 0:
                ikiwa (not erhn.endswith(domain) and
                    (not erhn.startswith(".") and
                     sio ("."+erhn).endswith(domain))):
                    _debug("   effective request-host %s (even ukijumuisha added "
                           "initial dot) does sio end ukijumuisha %s",
                           erhn, domain)
                    rudisha Uongo
            ikiwa (cookie.version > 0 or
                (self.strict_ns_domain & self.DomainRFC2965Match)):
                ikiwa sio domain_match(erhn, domain):
                    _debug("   effective request-host %s does sio domain-match "
                           "%s", erhn, domain)
                    rudisha Uongo
            ikiwa (cookie.version > 0 or
                (self.strict_ns_domain & self.DomainStrictNoDots)):
                host_prefix = req_host[:-len(domain)]
                ikiwa (host_prefix.find(".") >= 0 and
                    sio IPV4_RE.search(req_host)):
                    _debug("   host prefix %s kila domain %s contains a dot",
                           host_prefix, domain)
                    rudisha Uongo
        rudisha Kweli

    eleza set_ok_port(self, cookie, request):
        ikiwa cookie.port_specified:
            req_port = request_port(request)
            ikiwa req_port ni Tupu:
                req_port = "80"
            isipokua:
                req_port = str(req_port)
            kila p kwenye cookie.port.split(","):
                jaribu:
                    int(p)
                except ValueError:
                    _debug("   bad port %s (not numeric)", p)
                    rudisha Uongo
                ikiwa p == req_port:
                    koma
            isipokua:
                _debug("   request port (%s) sio found kwenye %s",
                       req_port, cookie.port)
                rudisha Uongo
        rudisha Kweli

    eleza return_ok(self, cookie, request):
        """
        If you override .return_ok(), be sure to call this method.  If it
        returns false, so should your subkundi (assuming your subkundi wants to
        be more strict about which cookies to return).

        """
        # Path has already been checked by .path_return_ok(), na domain
        # blocking done by .domain_return_ok().
        _debug(" - checking cookie %s=%s", cookie.name, cookie.value)

        kila n kwenye "version", "verifiability", "secure", "expires", "port", "domain":
            fn_name = "return_ok_"+n
            fn = getattr(self, fn_name)
            ikiwa sio fn(cookie, request):
                rudisha Uongo
        rudisha Kweli

    eleza return_ok_version(self, cookie, request):
        ikiwa cookie.version > 0 na sio self.rfc2965:
            _debug("   RFC 2965 cookies are switched off")
            rudisha Uongo
        elikiwa cookie.version == 0 na sio self.netscape:
            _debug("   Netscape cookies are switched off")
            rudisha Uongo
        rudisha Kweli

    eleza return_ok_verifiability(self, cookie, request):
        ikiwa request.unverifiable na is_third_party(request):
            ikiwa cookie.version > 0 na self.strict_rfc2965_unverifiable:
                _debug("   third-party RFC 2965 cookie during unverifiable "
                       "transaction")
                rudisha Uongo
            elikiwa cookie.version == 0 na self.strict_ns_unverifiable:
                _debug("   third-party Netscape cookie during unverifiable "
                       "transaction")
                rudisha Uongo
        rudisha Kweli

    eleza return_ok_secure(self, cookie, request):
        ikiwa cookie.secure na request.type sio kwenye self.secure_protocols:
            _debug("   secure cookie ukijumuisha non-secure request")
            rudisha Uongo
        rudisha Kweli

    eleza return_ok_expires(self, cookie, request):
        ikiwa cookie.is_expired(self._now):
            _debug("   cookie expired")
            rudisha Uongo
        rudisha Kweli

    eleza return_ok_port(self, cookie, request):
        ikiwa cookie.port:
            req_port = request_port(request)
            ikiwa req_port ni Tupu:
                req_port = "80"
            kila p kwenye cookie.port.split(","):
                ikiwa p == req_port:
                    koma
            isipokua:
                _debug("   request port %s does sio match cookie port %s",
                       req_port, cookie.port)
                rudisha Uongo
        rudisha Kweli

    eleza return_ok_domain(self, cookie, request):
        req_host, erhn = eff_request_host(request)
        domain = cookie.domain

        ikiwa domain na sio domain.startswith("."):
            dotdomain = "." + domain
        isipokua:
            dotdomain = domain

        # strict check of non-domain cookies: Mozilla does this, MSIE5 doesn't
        ikiwa (cookie.version == 0 and
            (self.strict_ns_domain & self.DomainStrictNonDomain) and
            sio cookie.domain_specified na domain != erhn):
            _debug("   cookie ukijumuisha unspecified domain does sio string-compare "
                   "equal to request domain")
            rudisha Uongo

        ikiwa cookie.version > 0 na sio domain_match(erhn, domain):
            _debug("   effective request-host name %s does sio domain-match "
                   "RFC 2965 cookie domain %s", erhn, domain)
            rudisha Uongo
        ikiwa cookie.version == 0 na sio ("."+erhn).endswith(dotdomain):
            _debug("   request-host %s does sio match Netscape cookie domain "
                   "%s", req_host, domain)
            rudisha Uongo
        rudisha Kweli

    eleza domain_return_ok(self, domain, request):
        # Liberal check of.  This ni here as an optimization to avoid
        # having to load lots of MSIE cookie files unless necessary.
        req_host, erhn = eff_request_host(request)
        ikiwa sio req_host.startswith("."):
            req_host = "."+req_host
        ikiwa sio erhn.startswith("."):
            erhn = "."+erhn
        ikiwa domain na sio domain.startswith("."):
            dotdomain = "." + domain
        isipokua:
            dotdomain = domain
        ikiwa sio (req_host.endswith(dotdomain) ama erhn.endswith(dotdomain)):
            #_debug("   request domain %s does sio match cookie domain %s",
            #       req_host, domain)
            rudisha Uongo

        ikiwa self.is_blocked(domain):
            _debug("   domain %s ni kwenye user block-list", domain)
            rudisha Uongo
        ikiwa self.is_not_allowed(domain):
            _debug("   domain %s ni sio kwenye user allow-list", domain)
            rudisha Uongo

        rudisha Kweli

    eleza path_return_ok(self, path, request):
        _debug("- checking cookie path=%s", path)
        req_path = request_path(request)
        pathlen = len(path)
        ikiwa req_path == path:
            rudisha Kweli
        elikiwa (req_path.startswith(path) and
              (path.endswith("/") ama req_path[pathlen:pathlen+1] == "/")):
            rudisha Kweli

        _debug("  %s does sio path-match %s", req_path, path)
        rudisha Uongo

eleza vals_sorted_by_key(adict):
    keys = sorted(adict.keys())
    rudisha map(adict.get, keys)

eleza deepvalues(mapping):
    """Iterates over nested mapping, depth-first, kwenye sorted order by key."""
    values = vals_sorted_by_key(mapping)
    kila obj kwenye values:
        mapping = Uongo
        jaribu:
            obj.items
        except AttributeError:
            pass
        isipokua:
            mapping = Kweli
            tuma kutoka deepvalues(obj)
        ikiwa sio mapping:
            tuma obj


# Used as second parameter to dict.get() method, to distinguish absent
# dict key kutoka one ukijumuisha a Tupu value.
kundi Absent: pass

kundi CookieJar:
    """Collection of HTTP cookies.

    You may sio need to know about this class: try
    urllib.request.build_opener(HTTPCookieProcessor).open(url).
    """

    non_word_re = re.compile(r"\W")
    quote_re = re.compile(r"([\"\\])")
    strict_domain_re = re.compile(r"\.?[^.]*")
    domain_re = re.compile(r"[^.]*")
    dots_re = re.compile(r"^\.+")

    magic_re = re.compile(r"^\#LWP-Cookies-(\d+\.\d+)", re.ASCII)

    eleza __init__(self, policy=Tupu):
        ikiwa policy ni Tupu:
            policy = DefaultCookiePolicy()
        self._policy = policy

        self._cookies_lock = _threading.RLock()
        self._cookies = {}

    eleza set_policy(self, policy):
        self._policy = policy

    eleza _cookies_for_domain(self, domain, request):
        cookies = []
        ikiwa sio self._policy.domain_return_ok(domain, request):
            rudisha []
        _debug("Checking %s kila cookies to return", domain)
        cookies_by_path = self._cookies[domain]
        kila path kwenye cookies_by_path.keys():
            ikiwa sio self._policy.path_return_ok(path, request):
                endelea
            cookies_by_name = cookies_by_path[path]
            kila cookie kwenye cookies_by_name.values():
                ikiwa sio self._policy.return_ok(cookie, request):
                    _debug("   sio returning cookie")
                    endelea
                _debug("   it's a match")
                cookies.append(cookie)
        rudisha cookies

    eleza _cookies_for_request(self, request):
        """Return a list of cookies to be returned to server."""
        cookies = []
        kila domain kwenye self._cookies.keys():
            cookies.extend(self._cookies_for_domain(domain, request))
        rudisha cookies

    eleza _cookie_attrs(self, cookies):
        """Return a list of cookie-attributes to be returned to server.

        like ['foo="bar"; $Path="/"', ...]

        The $Version attribute ni also added when appropriate (currently only
        once per request).

        """
        # add cookies kwenye order of most specific (ie. longest) path first
        cookies.sort(key=lambda a: len(a.path), reverse=Kweli)

        version_set = Uongo

        attrs = []
        kila cookie kwenye cookies:
            # set version of Cookie header
            # XXX
            # What should it be ikiwa multiple matching Set-Cookie headers have
            #  different versions themselves?
            # Answer: there ni no answer; was supposed to be settled by
            #  RFC 2965 errata, but that may never appear...
            version = cookie.version
            ikiwa sio version_set:
                version_set = Kweli
                ikiwa version > 0:
                    attrs.append("$Version=%s" % version)

            # quote cookie value ikiwa necessary
            # (not kila Netscape protocol, which already has any quotes
            #  intact, due to the poorly-specified Netscape Cookie: syntax)
            ikiwa ((cookie.value ni sio Tupu) and
                self.non_word_re.search(cookie.value) na version > 0):
                value = self.quote_re.sub(r"\\\1", cookie.value)
            isipokua:
                value = cookie.value

            # add cookie-attributes to be returned kwenye Cookie header
            ikiwa cookie.value ni Tupu:
                attrs.append(cookie.name)
            isipokua:
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
                ikiwa cookie.port ni sio Tupu:
                    p = "$Port"
                    ikiwa cookie.port_specified:
                        p = p + ('="%s"' % cookie.port)
                    attrs.append(p)

        rudisha attrs

    eleza add_cookie_header(self, request):
        """Add correct Cookie: header to request (urllib.request.Request object).

        The Cookie2 header ni also added unless policy.hide_cookie2 ni true.

        """
        _debug("add_cookie_header")
        self._cookies_lock.acquire()
        jaribu:

            self._policy._now = self._now = int(time.time())

            cookies = self._cookies_for_request(request)

            attrs = self._cookie_attrs(cookies)
            ikiwa attrs:
                ikiwa sio request.has_header("Cookie"):
                    request.add_unredirected_header(
                        "Cookie", "; ".join(attrs))

            # ikiwa necessary, advertise that we know RFC 2965
            ikiwa (self._policy.rfc2965 na sio self._policy.hide_cookie2 and
                sio request.has_header("Cookie2")):
                kila cookie kwenye cookies:
                    ikiwa cookie.version != 1:
                        request.add_unredirected_header("Cookie2", '$Version="1"')
                        koma

        mwishowe:
            self._cookies_lock.release()

        self.clear_expired_cookies()

    eleza _normalized_cookie_tuples(self, attrs_set):
        """Return list of tuples containing normalised cookie information.

        attrs_set ni the list of lists of key,value pairs extracted from
        the Set-Cookie ama Set-Cookie2 headers.

        Tuples are name, value, standard, rest, where name na value are the
        cookie name na value, standard ni a dictionary containing the standard
        cookie-attributes (discard, secure, version, expires ama max-age,
        domain, path na port) na rest ni a dictionary containing the rest of
        the cookie-attributes.

        """
        cookie_tuples = []

        boolean_attrs = "discard", "secure"
        value_attrs = ("version",
                       "expires", "max-age",
                       "domain", "path", "port",
                       "comment", "commenturl")

        kila cookie_attrs kwenye attrs_set:
            name, value = cookie_attrs[0]

            # Build dictionary of standard cookie-attributes (standard) and
            # dictionary of other cookie-attributes (rest).

            # Note: expiry time ni normalised to seconds since epoch.  V0
            # cookies should have the Expires cookie-attribute, na V1 cookies
            # should have Max-Age, but since V1 includes RFC 2109 cookies (and
            # since V0 cookies may be a mish-mash of Netscape na RFC 2109), we
            # accept either (but prefer Max-Age).
            max_age_set = Uongo

            bad_cookie = Uongo

            standard = {}
            rest = {}
            kila k, v kwenye cookie_attrs[1:]:
                lc = k.lower()
                # don't lose case distinction kila unknown fields
                ikiwa lc kwenye value_attrs ama lc kwenye boolean_attrs:
                    k = lc
                ikiwa k kwenye boolean_attrs na v ni Tupu:
                    # boolean cookie-attribute ni present, but has no value
                    # (like "discard", rather than "port=80")
                    v = Kweli
                ikiwa k kwenye standard:
                    # only first value ni significant
                    endelea
                ikiwa k == "domain":
                    ikiwa v ni Tupu:
                        _debug("   missing value kila domain attribute")
                        bad_cookie = Kweli
                        koma
                    # RFC 2965 section 3.3.3
                    v = v.lower()
                ikiwa k == "expires":
                    ikiwa max_age_set:
                        # Prefer max-age to expires (like Mozilla)
                        endelea
                    ikiwa v ni Tupu:
                        _debug("   missing ama invalid value kila expires "
                              "attribute: treating as session cookie")
                        endelea
                ikiwa k == "max-age":
                    max_age_set = Kweli
                    jaribu:
                        v = int(v)
                    except ValueError:
                        _debug("   missing ama invalid (non-numeric) value kila "
                              "max-age attribute")
                        bad_cookie = Kweli
                        koma
                    # convert RFC 2965 Max-Age to seconds since epoch
                    # XXX Strictly you're supposed to follow RFC 2616
                    #   age-calculation rules.  Remember that zero Max-Age
                    #   ni a request to discard (old na new) cookie, though.
                    k = "expires"
                    v = self._now + v
                ikiwa (k kwenye value_attrs) ama (k kwenye boolean_attrs):
                    ikiwa (v ni Tupu and
                        k sio kwenye ("port", "comment", "commenturl")):
                        _debug("   missing value kila %s attribute" % k)
                        bad_cookie = Kweli
                        koma
                    standard[k] = v
                isipokua:
                    rest[k] = v

            ikiwa bad_cookie:
                endelea

            cookie_tuples.append((name, value, standard, rest))

        rudisha cookie_tuples

    eleza _cookie_from_cookie_tuple(self, tup, request):
        # standard ni dict of standard cookie-attributes, rest ni dict of the
        # rest of them
        name, value, standard, rest = tup

        domain = standard.get("domain", Absent)
        path = standard.get("path", Absent)
        port = standard.get("port", Absent)
        expires = standard.get("expires", Absent)

        # set the easy defaults
        version = standard.get("version", Tupu)
        ikiwa version ni sio Tupu:
            jaribu:
                version = int(version)
            except ValueError:
                rudisha Tupu  # invalid version, ignore cookie
        secure = standard.get("secure", Uongo)
        # (discard ni also set ikiwa expires ni Absent)
        discard = standard.get("discard", Uongo)
        comment = standard.get("comment", Tupu)
        comment_url = standard.get("commenturl", Tupu)

        # set default path
        ikiwa path ni sio Absent na path != "":
            path_specified = Kweli
            path = escape_path(path)
        isipokua:
            path_specified = Uongo
            path = request_path(request)
            i = path.rfind("/")
            ikiwa i != -1:
                ikiwa version == 0:
                    # Netscape spec parts company kutoka reality here
                    path = path[:i]
                isipokua:
                    path = path[:i+1]
            ikiwa len(path) == 0: path = "/"

        # set default domain
        domain_specified = domain ni sio Absent
        # but first we have to remember whether it starts ukijumuisha a dot
        domain_initial_dot = Uongo
        ikiwa domain_specified:
            domain_initial_dot = bool(domain.startswith("."))
        ikiwa domain ni Absent:
            req_host, erhn = eff_request_host(request)
            domain = erhn
        elikiwa sio domain.startswith("."):
            domain = "."+domain

        # set default port
        port_specified = Uongo
        ikiwa port ni sio Absent:
            ikiwa port ni Tupu:
                # Port attr present, but has no value: default to request port.
                # Cookie should then only be sent back on that port.
                port = request_port(request)
            isipokua:
                port_specified = Kweli
                port = re.sub(r"\s+", "", port)
        isipokua:
            # No port attr present.  Cookie can be sent back on any port.
            port = Tupu

        # set default expires na discard
        ikiwa expires ni Absent:
            expires = Tupu
            discard = Kweli
        elikiwa expires <= self._now:
            # Expiry date kwenye past ni request to delete cookie.  This can't be
            # kwenye DefaultCookiePolicy, because can't delete cookies there.
            jaribu:
                self.clear(domain, path, name)
            except KeyError:
                pass
            _debug("Expiring cookie, domain='%s', path='%s', name='%s'",
                   domain, path, name)
            rudisha Tupu

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

    eleza _cookies_from_attrs_set(self, attrs_set, request):
        cookie_tuples = self._normalized_cookie_tuples(attrs_set)

        cookies = []
        kila tup kwenye cookie_tuples:
            cookie = self._cookie_from_cookie_tuple(tup, request)
            ikiwa cookie: cookies.append(cookie)
        rudisha cookies

    eleza _process_rfc2109_cookies(self, cookies):
        rfc2109_as_ns = getattr(self._policy, 'rfc2109_as_netscape', Tupu)
        ikiwa rfc2109_as_ns ni Tupu:
            rfc2109_as_ns = sio self._policy.rfc2965
        kila cookie kwenye cookies:
            ikiwa cookie.version == 1:
                cookie.rfc2109 = Kweli
                ikiwa rfc2109_as_ns:
                    # treat 2109 cookies as Netscape cookies rather than
                    # as RFC2965 cookies
                    cookie.version = 0

    eleza make_cookies(self, response, request):
        """Return sequence of Cookie objects extracted kutoka response object."""
        # get cookie-attributes kila RFC 2965 na Netscape protocols
        headers = response.info()
        rfc2965_hdrs = headers.get_all("Set-Cookie2", [])
        ns_hdrs = headers.get_all("Set-Cookie", [])
        self._policy._now = self._now = int(time.time())

        rfc2965 = self._policy.rfc2965
        netscape = self._policy.netscape

        ikiwa ((not rfc2965_hdrs na sio ns_hdrs) or
            (not ns_hdrs na sio rfc2965) or
            (not rfc2965_hdrs na sio netscape) or
            (not netscape na sio rfc2965)):
            rudisha []  # no relevant cookie headers: quick exit

        jaribu:
            cookies = self._cookies_from_attrs_set(
                split_header_words(rfc2965_hdrs), request)
        except Exception:
            _warn_unhandled_exception()
            cookies = []

        ikiwa ns_hdrs na netscape:
            jaribu:
                # RFC 2109 na Netscape cookies
                ns_cookies = self._cookies_from_attrs_set(
                    parse_ns_headers(ns_hdrs), request)
            except Exception:
                _warn_unhandled_exception()
                ns_cookies = []
            self._process_rfc2109_cookies(ns_cookies)

            # Look kila Netscape cookies (kutoka Set-Cookie headers) that match
            # corresponding RFC 2965 cookies (kutoka Set-Cookie2 headers).
            # For each match, keep the RFC 2965 cookie na ignore the Netscape
            # cookie (RFC 2965 section 9.1).  Actually, RFC 2109 cookies are
            # bundled kwenye ukijumuisha the Netscape cookies kila this purpose, which is
            # reasonable behaviour.
            ikiwa rfc2965:
                lookup = {}
                kila cookie kwenye cookies:
                    lookup[(cookie.domain, cookie.path, cookie.name)] = Tupu

                eleza no_matching_rfc2965(ns_cookie, lookup=lookup):
                    key = ns_cookie.domain, ns_cookie.path, ns_cookie.name
                    rudisha key sio kwenye lookup
                ns_cookies = filter(no_matching_rfc2965, ns_cookies)

            ikiwa ns_cookies:
                cookies.extend(ns_cookies)

        rudisha cookies

    eleza set_cookie_if_ok(self, cookie, request):
        """Set a cookie ikiwa policy says it's OK to do so."""
        self._cookies_lock.acquire()
        jaribu:
            self._policy._now = self._now = int(time.time())

            ikiwa self._policy.set_ok(cookie, request):
                self.set_cookie(cookie)


        mwishowe:
            self._cookies_lock.release()

    eleza set_cookie(self, cookie):
        """Set a cookie, without checking whether ama sio it should be set."""
        c = self._cookies
        self._cookies_lock.acquire()
        jaribu:
            ikiwa cookie.domain sio kwenye c: c[cookie.domain] = {}
            c2 = c[cookie.domain]
            ikiwa cookie.path sio kwenye c2: c2[cookie.path] = {}
            c3 = c2[cookie.path]
            c3[cookie.name] = cookie
        mwishowe:
            self._cookies_lock.release()

    eleza extract_cookies(self, response, request):
        """Extract cookies kutoka response, where allowable given the request."""
        _debug("extract_cookies: %s", response.info())
        self._cookies_lock.acquire()
        jaribu:
            kila cookie kwenye self.make_cookies(response, request):
                ikiwa self._policy.set_ok(cookie, request):
                    _debug(" setting cookie: %s", cookie)
                    self.set_cookie(cookie)
        mwishowe:
            self._cookies_lock.release()

    eleza clear(self, domain=Tupu, path=Tupu, name=Tupu):
        """Clear some cookies.

        Invoking this method without arguments will clear all cookies.  If
        given a single argument, only cookies belonging to that domain will be
        removed.  If given two arguments, cookies belonging to the specified
        path within that domain are removed.  If given three arguments, then
        the cookie ukijumuisha the specified name, path na domain ni removed.

        Raises KeyError ikiwa no matching cookie exists.

        """
        ikiwa name ni sio Tupu:
            ikiwa (domain ni Tupu) ama (path ni Tupu):
                 ashiria ValueError(
                    "domain na path must be given to remove a cookie by name")
            toa self._cookies[domain][path][name]
        elikiwa path ni sio Tupu:
            ikiwa domain ni Tupu:
                 ashiria ValueError(
                    "domain must be given to remove cookies by path")
            toa self._cookies[domain][path]
        elikiwa domain ni sio Tupu:
            toa self._cookies[domain]
        isipokua:
            self._cookies = {}

    eleza clear_session_cookies(self):
        """Discard all session cookies.

        Note that the .save() method won't save session cookies anyway, unless
        you ask otherwise by passing a true ignore_discard argument.

        """
        self._cookies_lock.acquire()
        jaribu:
            kila cookie kwenye self:
                ikiwa cookie.discard:
                    self.clear(cookie.domain, cookie.path, cookie.name)
        mwishowe:
            self._cookies_lock.release()

    eleza clear_expired_cookies(self):
        """Discard all expired cookies.

        You probably don't need to call this method: expired cookies are never
        sent back to the server (provided you're using DefaultCookiePolicy),
        this method ni called by CookieJar itself every so often, na the
        .save() method won't save expired cookies anyway (unless you ask
        otherwise by passing a true ignore_expires argument).

        """
        self._cookies_lock.acquire()
        jaribu:
            now = time.time()
            kila cookie kwenye self:
                ikiwa cookie.is_expired(now):
                    self.clear(cookie.domain, cookie.path, cookie.name)
        mwishowe:
            self._cookies_lock.release()

    eleza __iter__(self):
        rudisha deepvalues(self._cookies)

    eleza __len__(self):
        """Return number of contained cookies."""
        i = 0
        kila cookie kwenye self: i = i + 1
        rudisha i

    eleza __repr__(self):
        r = []
        kila cookie kwenye self: r.append(repr(cookie))
        rudisha "<%s[%s]>" % (self.__class__.__name__, ", ".join(r))

    eleza __str__(self):
        r = []
        kila cookie kwenye self: r.append(str(cookie))
        rudisha "<%s[%s]>" % (self.__class__.__name__, ", ".join(r))


# derives kutoka OSError kila backwards-compatibility ukijumuisha Python 2.4.0
kundi LoadError(OSError): pass

kundi FileCookieJar(CookieJar):
    """CookieJar that can be loaded kutoka na saved to a file."""

    eleza __init__(self, filename=Tupu, delayload=Uongo, policy=Tupu):
        """
        Cookies are NOT loaded kutoka the named file until either the .load() or
        .revert() method ni called.

        """
        CookieJar.__init__(self, policy)
        ikiwa filename ni sio Tupu:
            filename = os.fspath(filename)
        self.filename = filename
        self.delayload = bool(delayload)

    eleza save(self, filename=Tupu, ignore_discard=Uongo, ignore_expires=Uongo):
        """Save cookies to a file."""
         ashiria NotImplementedError()

    eleza load(self, filename=Tupu, ignore_discard=Uongo, ignore_expires=Uongo):
        """Load cookies kutoka a file."""
        ikiwa filename ni Tupu:
            ikiwa self.filename ni sio Tupu: filename = self.filename
            isipokua:  ashiria ValueError(MISSING_FILENAME_TEXT)

        ukijumuisha open(filename) as f:
            self._really_load(f, filename, ignore_discard, ignore_expires)

    eleza revert(self, filename=Tupu,
               ignore_discard=Uongo, ignore_expires=Uongo):
        """Clear all cookies na reload cookies kutoka a saved file.

        Raises LoadError (or OSError) ikiwa reversion ni sio successful; the
        object's state will sio be altered ikiwa this happens.

        """
        ikiwa filename ni Tupu:
            ikiwa self.filename ni sio Tupu: filename = self.filename
            isipokua:  ashiria ValueError(MISSING_FILENAME_TEXT)

        self._cookies_lock.acquire()
        jaribu:

            old_state = copy.deepcopy(self._cookies)
            self._cookies = {}
            jaribu:
                self.load(filename, ignore_discard, ignore_expires)
            except OSError:
                self._cookies = old_state
                raise

        mwishowe:
            self._cookies_lock.release()


eleza lwp_cookie_str(cookie):
    """Return string representation of Cookie kwenye the LWP cookie file format.

    Actually, the format ni extended a bit -- see module docstring.

    """
    h = [(cookie.name, cookie.value),
         ("path", cookie.path),
         ("domain", cookie.domain)]
    ikiwa cookie.port ni sio Tupu: h.append(("port", cookie.port))
    ikiwa cookie.path_specified: h.append(("path_spec", Tupu))
    ikiwa cookie.port_specified: h.append(("port_spec", Tupu))
    ikiwa cookie.domain_initial_dot: h.append(("domain_dot", Tupu))
    ikiwa cookie.secure: h.append(("secure", Tupu))
    ikiwa cookie.expires: h.append(("expires",
                               time2isoz(float(cookie.expires))))
    ikiwa cookie.discard: h.append(("discard", Tupu))
    ikiwa cookie.comment: h.append(("comment", cookie.comment))
    ikiwa cookie.comment_url: h.append(("commenturl", cookie.comment_url))

    keys = sorted(cookie._rest.keys())
    kila k kwenye keys:
        h.append((k, str(cookie._rest[k])))

    h.append(("version", str(cookie.version)))

    rudisha join_header_words([h])

kundi LWPCookieJar(FileCookieJar):
    """
    The LWPCookieJar saves a sequence of "Set-Cookie3" lines.
    "Set-Cookie3" ni the format used by the libwww-perl library, sio known
    to be compatible ukijumuisha any browser, but which ni easy to read and
    doesn't lose information about RFC 2965 cookies.

    Additional methods

    as_lwp_str(ignore_discard=Kweli, ignore_expired=Kweli)

    """

    eleza as_lwp_str(self, ignore_discard=Kweli, ignore_expires=Kweli):
        """Return cookies as a string of "\\n"-separated "Set-Cookie3" headers.

        ignore_discard na ignore_expires: see docstring kila FileCookieJar.save

        """
        now = time.time()
        r = []
        kila cookie kwenye self:
            ikiwa sio ignore_discard na cookie.discard:
                endelea
            ikiwa sio ignore_expires na cookie.is_expired(now):
                endelea
            r.append("Set-Cookie3: %s" % lwp_cookie_str(cookie))
        rudisha "\n".join(r+[""])

    eleza save(self, filename=Tupu, ignore_discard=Uongo, ignore_expires=Uongo):
        ikiwa filename ni Tupu:
            ikiwa self.filename ni sio Tupu: filename = self.filename
            isipokua:  ashiria ValueError(MISSING_FILENAME_TEXT)

        ukijumuisha open(filename, "w") as f:
            # There really isn't an LWP Cookies 2.0 format, but this indicates
            # that there ni extra information kwenye here (domain_dot and
            # port_spec) wakati still being compatible ukijumuisha libwww-perl, I hope.
            f.write("#LWP-Cookies-2.0\n")
            f.write(self.as_lwp_str(ignore_discard, ignore_expires))

    eleza _really_load(self, f, filename, ignore_discard, ignore_expires):
        magic = f.readline()
        ikiwa sio self.magic_re.search(magic):
            msg = ("%r does sio look like a Set-Cookie3 (LWP) format "
                   "file" % filename)
             ashiria LoadError(msg)

        now = time.time()

        header = "Set-Cookie3:"
        boolean_attrs = ("port_spec", "path_spec", "domain_dot",
                         "secure", "discard")
        value_attrs = ("version",
                       "port", "path", "domain",
                       "expires",
                       "comment", "commenturl")

        jaribu:
            wakati 1:
                line = f.readline()
                ikiwa line == "": koma
                ikiwa sio line.startswith(header):
                    endelea
                line = line[len(header):].strip()

                kila data kwenye split_header_words([line]):
                    name, value = data[0]
                    standard = {}
                    rest = {}
                    kila k kwenye boolean_attrs:
                        standard[k] = Uongo
                    kila k, v kwenye data[1:]:
                        ikiwa k ni sio Tupu:
                            lc = k.lower()
                        isipokua:
                            lc = Tupu
                        # don't lose case distinction kila unknown fields
                        ikiwa (lc kwenye value_attrs) ama (lc kwenye boolean_attrs):
                            k = lc
                        ikiwa k kwenye boolean_attrs:
                            ikiwa v ni Tupu: v = Kweli
                            standard[k] = v
                        elikiwa k kwenye value_attrs:
                            standard[k] = v
                        isipokua:
                            rest[k] = v

                    h = standard.get
                    expires = h("expires")
                    discard = h("discard")
                    ikiwa expires ni sio Tupu:
                        expires = iso2time(expires)
                    ikiwa expires ni Tupu:
                        discard = Kweli
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
                    ikiwa sio ignore_discard na c.discard:
                        endelea
                    ikiwa sio ignore_expires na c.is_expired(now):
                        endelea
                    self.set_cookie(c)
        except OSError:
            raise
        except Exception:
            _warn_unhandled_exception()
             ashiria LoadError("invalid Set-Cookie3 format file %r: %r" %
                            (filename, line))


kundi MozillaCookieJar(FileCookieJar):
    """

    WARNING: you may want to backup your browser's cookies file ikiwa you use
    this kundi to save cookies.  I *think* it works, but there have been
    bugs kwenye the past!

    This kundi differs kutoka CookieJar only kwenye the format it uses to save and
    load cookies to na kutoka a file.  This kundi uses the Mozilla/Netscape
    `cookies.txt' format.  lynx uses this file format, too.

    Don't expect cookies saved wakati the browser ni running to be noticed by
    the browser (in fact, Mozilla on unix will overwrite your saved cookies if
    you change them on disk wakati it's running; on Windows, you probably can't
    save at all wakati the browser ni running).

    Note that the Mozilla/Netscape format will downgrade RFC2965 cookies to
    Netscape cookies on saving.

    In particular, the cookie version na port number information ni lost,
    together ukijumuisha information about whether ama sio Path, Port na Discard were
    specified by the Set-Cookie2 (or Set-Cookie) header, na whether ama sio the
    domain as set kwenye the HTTP header started ukijumuisha a dot (yes, I'm aware some
    domains kwenye Netscape files start ukijumuisha a dot na some don't -- trust me, you
    really don't want to know any more about this).

    Note that though Mozilla na Netscape use the same format, they use
    slightly different headers.  The kundi saves cookies using the Netscape
    header by default (Mozilla can cope ukijumuisha that).

    """
    magic_re = re.compile("#( Netscape)? HTTP Cookie File")
    header = """\
# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This ni a generated file!  Do sio edit.

"""

    eleza _really_load(self, f, filename, ignore_discard, ignore_expires):
        now = time.time()

        magic = f.readline()
        ikiwa sio self.magic_re.search(magic):
             ashiria LoadError(
                "%r does sio look like a Netscape format cookies file" %
                filename)

        jaribu:
            wakati 1:
                line = f.readline()
                ikiwa line == "": koma

                # last field may be absent, so keep any trailing tab
                ikiwa line.endswith("\n"): line = line[:-1]

                # skip comments na blank lines XXX what ni $ for?
                ikiwa (line.strip().startswith(("#", "$")) or
                    line.strip() == ""):
                    endelea

                domain, domain_specified, path, secure, expires, name, value = \
                        line.split("\t")
                secure = (secure == "TRUE")
                domain_specified = (domain_specified == "TRUE")
                ikiwa name == "":
                    # cookies.txt regards 'Set-Cookie: foo' as a cookie
                    # ukijumuisha no name, whereas http.cookiejar regards it as a
                    # cookie ukijumuisha no value.
                    name = value
                    value = Tupu

                initial_dot = domain.startswith(".")
                assert domain_specified == initial_dot

                discard = Uongo
                ikiwa expires == "":
                    expires = Tupu
                    discard = Kweli

                # assume path_specified ni false
                c = Cookie(0, name, value,
                           Tupu, Uongo,
                           domain, domain_specified, initial_dot,
                           path, Uongo,
                           secure,
                           expires,
                           discard,
                           Tupu,
                           Tupu,
                           {})
                ikiwa sio ignore_discard na c.discard:
                    endelea
                ikiwa sio ignore_expires na c.is_expired(now):
                    endelea
                self.set_cookie(c)

        except OSError:
            raise
        except Exception:
            _warn_unhandled_exception()
             ashiria LoadError("invalid Netscape format cookies file %r: %r" %
                            (filename, line))

    eleza save(self, filename=Tupu, ignore_discard=Uongo, ignore_expires=Uongo):
        ikiwa filename ni Tupu:
            ikiwa self.filename ni sio Tupu: filename = self.filename
            isipokua:  ashiria ValueError(MISSING_FILENAME_TEXT)

        ukijumuisha open(filename, "w") as f:
            f.write(self.header)
            now = time.time()
            kila cookie kwenye self:
                ikiwa sio ignore_discard na cookie.discard:
                    endelea
                ikiwa sio ignore_expires na cookie.is_expired(now):
                    endelea
                ikiwa cookie.secure: secure = "TRUE"
                isipokua: secure = "FALSE"
                ikiwa cookie.domain.startswith("."): initial_dot = "TRUE"
                isipokua: initial_dot = "FALSE"
                ikiwa cookie.expires ni sio Tupu:
                    expires = str(cookie.expires)
                isipokua:
                    expires = ""
                ikiwa cookie.value ni Tupu:
                    # cookies.txt regards 'Set-Cookie: foo' as a cookie
                    # ukijumuisha no name, whereas http.cookiejar regards it as a
                    # cookie ukijumuisha no value.
                    name = ""
                    value = cookie.name
                isipokua:
                    name = cookie.name
                    value = cookie.value
                f.write(
                    "\t".join([cookie.domain, initial_dot, cookie.path,
                               secure, expires, name, value])+
                    "\n")
