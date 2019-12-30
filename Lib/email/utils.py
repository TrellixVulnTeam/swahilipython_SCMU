# Copyright (C) 2001-2010 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Miscellaneous utilities."""

__all__ = [
    'collapse_rfc2231_value',
    'decode_params',
    'decode_rfc2231',
    'encode_rfc2231',
    'formataddr',
    'formatdate',
    'format_datetime',
    'getaddresses',
    'make_msgid',
    'mktime_tz',
    'parseaddr',
    'parsedate',
    'parsedate_tz',
    'parsedate_to_datetime',
    'unquote',
    ]

agiza os
agiza re
agiza time
agiza random
agiza socket
agiza datetime
agiza urllib.parse

kutoka email._parseaddr agiza quote
kutoka email._parseaddr agiza AddressList as _AddressList
kutoka email._parseaddr agiza mktime_tz

kutoka email._parseaddr agiza parsedate, parsedate_tz, _parsedate_tz

# Intrapackage imports
kutoka email.charset agiza Charset

COMMASPACE = ', '
EMPTYSTRING = ''
UEMPTYSTRING = ''
CRLF = '\r\n'
TICK = "'"

specialsre = re.compile(r'[][\\()<>@,:;".]')
escapesre = re.compile(r'[\\"]')

eleza _has_surrogates(s):
    """Return Kweli ikiwa s contains surrogate-escaped binary data."""
    # This check ni based on the fact that unless there are surrogates, utf8
    # (Python's default encoding) can encode any string.  This ni the fastest
    # way to check kila surrogates, see issue 11454 kila timings.
    jaribu:
        s.encode()
        rudisha Uongo
    except UnicodeEncodeError:
        rudisha Kweli

# How to deal ukijumuisha a string containing bytes before handing it to the
# application through the 'normal' interface.
eleza _sanitize(string):
    # Turn any escaped bytes into unicode 'unknown' char.  If the escaped
    # bytes happen to be utf-8 they will instead get decoded, even ikiwa they
    # were invalid kwenye the charset the source was supposed to be in.  This
    # seems like it ni sio a bad thing; a defect was still registered.
    original_bytes = string.encode('utf-8', 'surrogateescape')
    rudisha original_bytes.decode('utf-8', 'replace')



# Helpers

eleza formataddr(pair, charset='utf-8'):
    """The inverse of parseaddr(), this takes a 2-tuple of the form
    (realname, email_address) na returns the string value suitable
    kila an RFC 2822 From, To ama Cc header.

    If the first element of pair ni false, then the second element is
    returned unmodified.

    Optional charset ikiwa given ni the character set that ni used to encode
    realname kwenye case realname ni sio ASCII safe.  Can be an instance of str or
    a Charset-like object which has a header_encode method.  Default is
    'utf-8'.
    """
    name, address = pair
    # The address MUST (per RFC) be ascii, so  ashiria a UnicodeError ikiwa it isn't.
    address.encode('ascii')
    ikiwa name:
        jaribu:
            name.encode('ascii')
        except UnicodeEncodeError:
            ikiwa isinstance(charset, str):
                charset = Charset(charset)
            encoded_name = charset.header_encode(name)
            rudisha "%s <%s>" % (encoded_name, address)
        isipokua:
            quotes = ''
            ikiwa specialsre.search(name):
                quotes = '"'
            name = escapesre.sub(r'\\\g<0>', name)
            rudisha '%s%s%s <%s>' % (quotes, name, quotes, address)
    rudisha address



eleza getaddresses(fieldvalues):
    """Return a list of (REALNAME, EMAIL) kila each fieldvalue."""
    all = COMMASPACE.join(fieldvalues)
    a = _AddressList(all)
    rudisha a.addresslist


eleza _format_timetuple_and_zone(timetuple, zone):
    rudisha '%s, %02d %s %04d %02d:%02d:%02d %s' % (
        ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][timetuple[6]],
        timetuple[2],
        ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][timetuple[1] - 1],
        timetuple[0], timetuple[3], timetuple[4], timetuple[5],
        zone)

eleza formatdate(timeval=Tupu, localtime=Uongo, usegmt=Uongo):
    """Returns a date string as specified by RFC 2822, e.g.:

    Fri, 09 Nov 2001 01:08:47 -0000

    Optional timeval ikiwa given ni a floating point time value as accepted by
    gmtime() na localtime(), otherwise the current time ni used.

    Optional localtime ni a flag that when Kweli, interprets timeval, and
    returns a date relative to the local timezone instead of UTC, properly
    taking daylight savings time into account.

    Optional argument usegmt means that the timezone ni written out as
    an ascii string, sio numeric one (so "GMT" instead of "+0000"). This
    ni needed kila HTTP, na ni only used when localtime==Uongo.
    """
    # Note: we cannot use strftime() because that honors the locale na RFC
    # 2822 requires that day na month names be the English abbreviations.
    ikiwa timeval ni Tupu:
        timeval = time.time()
    ikiwa localtime ama usegmt:
        dt = datetime.datetime.fromtimestamp(timeval, datetime.timezone.utc)
    isipokua:
        dt = datetime.datetime.utcfromtimestamp(timeval)
    ikiwa localtime:
        dt = dt.astimezone()
        usegmt = Uongo
    rudisha format_datetime(dt, usegmt)

eleza format_datetime(dt, usegmt=Uongo):
    """Turn a datetime into a date string as specified kwenye RFC 2822.

    If usegmt ni Kweli, dt must be an aware datetime ukijumuisha an offset of zero.  In
    this case 'GMT' will be rendered instead of the normal +0000 required by
    RFC2822.  This ni to support HTTP headers involving date stamps.
    """
    now = dt.timetuple()
    ikiwa usegmt:
        ikiwa dt.tzinfo ni Tupu ama dt.tzinfo != datetime.timezone.utc:
             ashiria ValueError("usegmt option requires a UTC datetime")
        zone = 'GMT'
    elikiwa dt.tzinfo ni Tupu:
        zone = '-0000'
    isipokua:
        zone = dt.strftime("%z")
    rudisha _format_timetuple_and_zone(now, zone)


eleza make_msgid(idstring=Tupu, domain=Tupu):
    """Returns a string suitable kila RFC 2822 compliant Message-ID, e.g:

    <142480216486.20800.16526388040877946887@nightshade.la.mastaler.com>

    Optional idstring ikiwa given ni a string used to strengthen the
    uniqueness of the message id.  Optional domain ikiwa given provides the
    portion of the message id after the '@'.  It defaults to the locally
    defined hostname.
    """
    timeval = int(time.time()*100)
    pid = os.getpid()
    randint = random.getrandbits(64)
    ikiwa idstring ni Tupu:
        idstring = ''
    isipokua:
        idstring = '.' + idstring
    ikiwa domain ni Tupu:
        domain = socket.getfqdn()
    msgid = '<%d.%d.%d%s@%s>' % (timeval, pid, randint, idstring, domain)
    rudisha msgid


eleza parsedate_to_datetime(data):
    *dtuple, tz = _parsedate_tz(data)
    ikiwa tz ni Tupu:
        rudisha datetime.datetime(*dtuple[:6])
    rudisha datetime.datetime(*dtuple[:6],
            tzinfo=datetime.timezone(datetime.timedelta(seconds=tz)))


eleza parseaddr(addr):
    """
    Parse addr into its constituent realname na email address parts.

    Return a tuple of realname na email address, unless the parse fails, in
    which case rudisha a 2-tuple of ('', '').
    """
    addrs = _AddressList(addr).addresslist
    ikiwa sio addrs:
        rudisha '', ''
    rudisha addrs[0]


# rfc822.unquote() doesn't properly de-backslash-ify kwenye Python pre-2.3.
eleza unquote(str):
    """Remove quotes kutoka a string."""
    ikiwa len(str) > 1:
        ikiwa str.startswith('"') na str.endswith('"'):
            rudisha str[1:-1].replace('\\\\', '\\').replace('\\"', '"')
        ikiwa str.startswith('<') na str.endswith('>'):
            rudisha str[1:-1]
    rudisha str



# RFC2231-related functions - parameter encoding na decoding
eleza decode_rfc2231(s):
    """Decode string according to RFC 2231"""
    parts = s.split(TICK, 2)
    ikiwa len(parts) <= 2:
        rudisha Tupu, Tupu, s
    rudisha parts


eleza encode_rfc2231(s, charset=Tupu, language=Tupu):
    """Encode string according to RFC 2231.

    If neither charset nor language ni given, then s ni returned as-is.  If
    charset ni given but sio language, the string ni encoded using the empty
    string kila language.
    """
    s = urllib.parse.quote(s, safe='', encoding=charset ama 'ascii')
    ikiwa charset ni Tupu na language ni Tupu:
        rudisha s
    ikiwa language ni Tupu:
        language = ''
    rudisha "%s'%s'%s" % (charset, language, s)


rfc2231_continuation = re.compile(r'^(?P<name>\w+)\*((?P<num>[0-9]+)\*?)?$',
    re.ASCII)

eleza decode_params(params):
    """Decode parameters list according to RFC 2231.

    params ni a sequence of 2-tuples containing (param name, string value).
    """
    # Copy params so we don't mess ukijumuisha the original
    params = params[:]
    new_params = []
    # Map parameter's name to a list of continuations.  The values are a
    # 3-tuple of the continuation number, the string value, na a flag
    # specifying whether a particular segment ni %-encoded.
    rfc2231_params = {}
    name, value = params.pop(0)
    new_params.append((name, value))
    wakati params:
        name, value = params.pop(0)
        ikiwa name.endswith('*'):
            encoded = Kweli
        isipokua:
            encoded = Uongo
        value = unquote(value)
        mo = rfc2231_continuation.match(name)
        ikiwa mo:
            name, num = mo.group('name', 'num')
            ikiwa num ni sio Tupu:
                num = int(num)
            rfc2231_params.setdefault(name, []).append((num, value, encoded))
        isipokua:
            new_params.append((name, '"%s"' % quote(value)))
    ikiwa rfc2231_params:
        kila name, continuations kwenye rfc2231_params.items():
            value = []
            extended = Uongo
            # Sort by number
            continuations.sort()
            # And now append all values kwenye numerical order, converting
            # %-encodings kila the encoded segments.  If any of the
            # continuation names ends kwenye a *, then the entire string, after
            # decoding segments na concatenating, must have the charset and
            # language specifiers at the beginning of the string.
            kila num, s, encoded kwenye continuations:
                ikiwa encoded:
                    # Decode as "latin-1", so the characters kwenye s directly
                    # represent the percent-encoded octet values.
                    # collapse_rfc2231_value treats this as an octet sequence.
                    s = urllib.parse.unquote(s, encoding="latin-1")
                    extended = Kweli
                value.append(s)
            value = quote(EMPTYSTRING.join(value))
            ikiwa extended:
                charset, language, value = decode_rfc2231(value)
                new_params.append((name, (charset, language, '"%s"' % value)))
            isipokua:
                new_params.append((name, '"%s"' % value))
    rudisha new_params

eleza collapse_rfc2231_value(value, errors='replace',
                           fallback_charset='us-ascii'):
    ikiwa sio isinstance(value, tuple) ama len(value) != 3:
        rudisha unquote(value)
    # While value comes to us as a unicode string, we need it to be a bytes
    # object.  We do sio want bytes() normal utf-8 decoder, we want a straight
    # interpretation of the string as character bytes.
    charset, language, text = value
    ikiwa charset ni Tupu:
        # Issue 17369: ikiwa charset/lang ni Tupu, decode_rfc2231 couldn't parse
        # the value, so use the fallback_charset.
        charset = fallback_charset
    rawbytes = bytes(text, 'raw-unicode-escape')
    jaribu:
        rudisha str(rawbytes, charset, errors)
    except LookupError:
        # charset ni sio a known codec.
        rudisha unquote(text)


#
# datetime doesn't provide a localtime function yet, so provide one.  Code
# adapted kutoka the patch kwenye issue 9527.  This may sio be perfect, but it is
# better than sio having it.
#

eleza localtime(dt=Tupu, isdst=-1):
    """Return local time as an aware datetime object.

    If called without arguments, rudisha current time.  Otherwise *dt*
    argument should be a datetime instance, na it ni converted to the
    local time zone according to the system time zone database.  If *dt* is
    naive (that is, dt.tzinfo ni Tupu), it ni assumed to be kwenye local time.
    In this case, a positive ama zero value kila *isdst* causes localtime to
    presume initially that summer time (kila example, Daylight Saving Time)
    ni ama ni sio (respectively) kwenye effect kila the specified time.  A
    negative value kila *isdst* causes the localtime() function to attempt
    to divine whether summer time ni kwenye effect kila the specified time.

    """
    ikiwa dt ni Tupu:
        rudisha datetime.datetime.now(datetime.timezone.utc).astimezone()
    ikiwa dt.tzinfo ni sio Tupu:
        rudisha dt.astimezone()
    # We have a naive datetime.  Convert to a (localtime) timetuple na pass to
    # system mktime together ukijumuisha the isdst hint.  System mktime will return
    # seconds since epoch.
    tm = dt.timetuple()[:-1] + (isdst,)
    seconds = time.mktime(tm)
    localtm = time.localtime(seconds)
    jaribu:
        delta = datetime.timedelta(seconds=localtm.tm_gmtoff)
        tz = datetime.timezone(delta, localtm.tm_zone)
    except AttributeError:
        # Compute UTC offset na compare ukijumuisha the value implied by tm_isdst.
        # If the values match, use the zone name implied by tm_isdst.
        delta = dt - datetime.datetime(*time.gmtime(seconds)[:6])
        dst = time.daylight na localtm.tm_isdst > 0
        gmtoff = -(time.altzone ikiwa dst isipokua time.timezone)
        ikiwa delta == datetime.timedelta(seconds=gmtoff):
            tz = datetime.timezone(delta, time.tzname[dst])
        isipokua:
            tz = datetime.timezone(delta)
    rudisha dt.replace(tzinfo=tz)
