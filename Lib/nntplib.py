"""An NNTP client kundi based on:
- RFC 977: Network News Transfer Protocol
- RFC 2980: Common NNTP Extensions
- RFC 3977: Network News Transfer Protocol (version 2)

Example:

>>> kutoka nntplib agiza NNTP
>>> s = NNTP('news')
>>> resp, count, first, last, name = s.group('comp.lang.python')
>>> andika('Group', name, 'has', count, 'articles, range', first, 'to', last)
Group comp.lang.python has 51 articles, range 5770 to 5821
>>> resp, subs = s.xhdr('subject', '{0}-{1}'.format(first, last))
>>> resp = s.quit()
>>>

Here 'resp' ni the server response line.
Error responses are turned into exceptions.

To post an article kutoka a file:
>>> f = open(filename, 'rb') # file containing article, including header
>>> resp = s.post(f)
>>>

For descriptions of all methods, read the comments kwenye the code below.
Note that all arguments na rudisha values representing article numbers
are strings, sio numbers, since they are rarely used kila calculations.
"""

# RFC 977 by Brian Kantor na Phil Lapsley.
# xover, xgtitle, xpath, date methods by Kevan Heydon

# Incompatible changes kutoka the 2.x nntplib:
# - all commands are encoded kama UTF-8 data (using the "surrogateescape"
#   error handler), tatizo kila raw message data (POST, IHAVE)
# - all responses are decoded kama UTF-8 data (using the "surrogateescape"
#   error handler), tatizo kila raw message data (ARTICLE, HEAD, BODY)
# - the `file` argument to various methods ni keyword-only
#
# - NNTP.date() rudishas a datetime object
# - NNTP.newgroups() na NNTP.newnews() take a datetime (or date) object,
#   rather than a pair of (date, time) strings.
# - NNTP.newgroups() na NNTP.list() rudisha a list of GroupInfo named tuples
# - NNTP.descriptions() rudishas a dict mapping group names to descriptions
# - NNTP.xover() rudishas a list of dicts mapping field names (header ama metadata)
#   to field values; each dict representing a message overview.
# - NNTP.article(), NNTP.head() na NNTP.body() rudisha a (response, ArticleInfo)
#   tuple.
# - the "internal" methods have been marked private (they now start with
#   an underscore)

# Other changes kutoka the 2.x/3.1 nntplib:
# - automatic querying of capabilities at connect
# - New method NNTP.getcapabilities()
# - New method NNTP.over()
# - New helper function decode_header()
# - NNTP.post() na NNTP.ihave() accept file objects, bytes-like objects and
#   arbitrary iterables tumaing lines.
# - An extensive test suite :-)

# TODO:
# - rudisha structured data (GroupInfo etc.) everywhere
# - support HDR

# Imports
agiza re
agiza socket
agiza collections
agiza datetime
agiza warnings
agiza sys

jaribu:
    agiza ssl
tatizo ImportError:
    _have_ssl = Uongo
isipokua:
    _have_ssl = Kweli

kutoka email.header agiza decode_header kama _email_decode_header
kutoka socket agiza _GLOBAL_DEFAULT_TIMEOUT

__all__ = ["NNTP",
           "NNTPError", "NNTPReplyError", "NNTPTemporaryError",
           "NNTPPermanentError", "NNTPProtocolError", "NNTPDataError",
           "decode_header",
           ]

# maximal line length when calling readline(). This ni to prevent
# reading arbitrary length lines. RFC 3977 limits NNTP line length to
# 512 characters, including CRLF. We have selected 2048 just to be on
# the safe side.
_MAXLINE = 2048


# Exceptions ashiriad when an error ama invalid response ni received
kundi NNTPError(Exception):
    """Base kundi kila all nntplib exceptions"""
    eleza __init__(self, *args):
        Exception.__init__(self, *args)
        jaribu:
            self.response = args[0]
        tatizo IndexError:
            self.response = 'No response given'

kundi NNTPReplyError(NNTPError):
    """Unexpected [123]xx reply"""
    pita

kundi NNTPTemporaryError(NNTPError):
    """4xx errors"""
    pita

kundi NNTPPermanentError(NNTPError):
    """5xx errors"""
    pita

kundi NNTPProtocolError(NNTPError):
    """Response does sio begin ukijumuisha [1-5]"""
    pita

kundi NNTPDataError(NNTPError):
    """Error kwenye response data"""
    pita


# Standard port used by NNTP servers
NNTP_PORT = 119
NNTP_SSL_PORT = 563

# Response numbers that are followed by additional text (e.g. article)
_LONGRESP = {
    '100',   # HELP
    '101',   # CAPABILITIES
    '211',   # LISTGROUP   (also sio multi-line ukijumuisha GROUP)
    '215',   # LIST
    '220',   # ARTICLE
    '221',   # HEAD, XHDR
    '222',   # BODY
    '224',   # OVER, XOVER
    '225',   # HDR
    '230',   # NEWNEWS
    '231',   # NEWGROUPS
    '282',   # XGTITLE
}

# Default decoded value kila LIST OVERVIEW.FMT ikiwa sio supported
_DEFAULT_OVERVIEW_FMT = [
    "subject", "kutoka", "date", "message-id", "references", ":bytes", ":lines"]

# Alternative names allowed kwenye LIST OVERVIEW.FMT response
_OVERVIEW_FMT_ALTERNATIVES = {
    'bytes': ':bytes',
    'lines': ':lines',
}

# Line terminators (we always output CRLF, but accept any of CRLF, CR, LF)
_CRLF = b'\r\n'

GroupInfo = collections.namedtuple('GroupInfo',
                                   ['group', 'last', 'first', 'flag'])

ArticleInfo = collections.namedtuple('ArticleInfo',
                                     ['number', 'message_id', 'lines'])


# Helper function(s)
eleza decode_header(header_str):
    """Takes a unicode string representing a munged header value
    na decodes it kama a (possibly non-ASCII) readable value."""
    parts = []
    kila v, enc kwenye _email_decode_header(header_str):
        ikiwa isinstance(v, bytes):
            parts.append(v.decode(enc ama 'ascii'))
        isipokua:
            parts.append(v)
    rudisha ''.join(parts)

eleza _parse_overview_fmt(lines):
    """Parse a list of string representing the response to LIST OVERVIEW.FMT
    na rudisha a list of header/metadata names.
    Raises NNTPDataError ikiwa the response ni sio compliant
    (cf. RFC 3977, section 8.4)."""
    fmt = []
    kila line kwenye lines:
        ikiwa line[0] == ':':
            # Metadata name (e.g. ":bytes")
            name, _, suffix = line[1:].partition(':')
            name = ':' + name
        isipokua:
            # Header name (e.g. "Subject:" ama "Xref:full")
            name, _, suffix = line.partition(':')
        name = name.lower()
        name = _OVERVIEW_FMT_ALTERNATIVES.get(name, name)
        # Should we do something ukijumuisha the suffix?
        fmt.append(name)
    defaults = _DEFAULT_OVERVIEW_FMT
    ikiwa len(fmt) < len(defaults):
        ashiria NNTPDataError("LIST OVERVIEW.FMT response too short")
    ikiwa fmt[:len(defaults)] != defaults:
        ashiria NNTPDataError("LIST OVERVIEW.FMT redefines default fields")
    rudisha fmt

eleza _parse_overview(lines, fmt, data_process_func=Tupu):
    """Parse the response to an OVER ama XOVER command according to the
    overview format `fmt`."""
    n_defaults = len(_DEFAULT_OVERVIEW_FMT)
    overview = []
    kila line kwenye lines:
        fields = {}
        article_number, *tokens = line.split('\t')
        article_number = int(article_number)
        kila i, token kwenye enumerate(tokens):
            ikiwa i >= len(fmt):
                # XXX should we ashiria an error? Some servers might not
                # support LIST OVERVIEW.FMT na still rudisha additional
                # headers.
                endelea
            field_name = fmt[i]
            is_metadata = field_name.startswith(':')
            ikiwa i >= n_defaults na sio is_metadata:
                # Non-default header names are included kwenye full kwenye the response
                # (unless the field ni totally empty)
                h = field_name + ": "
                ikiwa token na token[:len(h)].lower() != h:
                    ashiria NNTPDataError("OVER/XOVER response doesn't include "
                                        "names of additional headers")
                token = token[len(h):] ikiwa token isipokua Tupu
            fields[fmt[i]] = token
        overview.append((article_number, fields))
    rudisha overview

eleza _parse_datetime(date_str, time_str=Tupu):
    """Parse a pair of (date, time) strings, na rudisha a datetime object.
    If only the date ni given, it ni assumed to be date na time
    concatenated together (e.g. response to the DATE command).
    """
    ikiwa time_str ni Tupu:
        time_str = date_str[-6:]
        date_str = date_str[:-6]
    hours = int(time_str[:2])
    minutes = int(time_str[2:4])
    seconds = int(time_str[4:])
    year = int(date_str[:-4])
    month = int(date_str[-4:-2])
    day = int(date_str[-2:])
    # RFC 3977 doesn't say how to interpret 2-char years.  Assume that
    # there are no dates before 1970 on Usenet.
    ikiwa year < 70:
        year += 2000
    lasivyo year < 100:
        year += 1900
    rudisha datetime.datetime(year, month, day, hours, minutes, seconds)

eleza _unparse_datetime(dt, legacy=Uongo):
    """Format a date ama datetime object kama a pair of (date, time) strings
    kwenye the format required by the NEWNEWS na NEWGROUPS commands.  If a
    date object ni pitaed, the time ni assumed to be midnight (00h00).

    The rudishaed representation depends on the legacy flag:
    * ikiwa legacy ni Uongo (the default):
      date has the YYYYMMDD format na time the HHMMSS format
    * ikiwa legacy ni Kweli:
      date has the YYMMDD format na time the HHMMSS format.
    RFC 3977 compliant servers should understand both formats; therefore,
    legacy ni only needed when talking to old servers.
    """
    ikiwa sio isinstance(dt, datetime.datetime):
        time_str = "000000"
    isipokua:
        time_str = "{0.hour:02d}{0.minute:02d}{0.second:02d}".format(dt)
    y = dt.year
    ikiwa legacy:
        y = y % 100
        date_str = "{0:02d}{1.month:02d}{1.day:02d}".format(y, dt)
    isipokua:
        date_str = "{0:04d}{1.month:02d}{1.day:02d}".format(y, dt)
    rudisha date_str, time_str


ikiwa _have_ssl:

    eleza _encrypt_on(sock, context, hostname):
        """Wrap a socket kwenye SSL/TLS. Arguments:
        - sock: Socket to wrap
        - context: SSL context to use kila the encrypted connection
        Returns:
        - sock: New, encrypted socket.
        """
        # Generate a default SSL context ikiwa none was pitaed.
        ikiwa context ni Tupu:
            context = ssl._create_stdlib_context()
        rudisha context.wrap_socket(sock, server_hostname=hostname)


# The classes themselves
kundi _NNTPBase:
    # UTF-8 ni the character set kila all NNTP commands na responses: they
    # are automatically encoded (when sending) na decoded (and receiving)
    # by this class.
    # However, some multi-line data blocks can contain arbitrary bytes (for
    # example, latin-1 ama utf-16 data kwenye the body of a message). Commands
    # taking (POST, IHAVE) ama rudishaing (HEAD, BODY, ARTICLE) raw message
    # data will therefore only accept na produce bytes objects.
    # Furthermore, since there could be non-compliant servers out there,
    # we use 'surrogateescape' kama the error handler kila fault tolerance
    # na easy round-tripping. This could be useful kila some applications
    # (e.g. NNTP gateways).

    encoding = 'utf-8'
    errors = 'surrogateescape'

    eleza __init__(self, file, host,
                 readermode=Tupu, timeout=_GLOBAL_DEFAULT_TIMEOUT):
        """Initialize an instance.  Arguments:
        - file: file-like object (open kila read/write kwenye binary mode)
        - host: hostname of the server
        - readermode: ikiwa true, send 'mode reader' command after
                      connecting.
        - timeout: timeout (in seconds) used kila socket connections

        readermode ni sometimes necessary ikiwa you are connecting to an
        NNTP server on the local machine na intend to call
        reader-specific commands, such kama `group'.  If you get
        unexpected NNTPPermanentErrors, you might need to set
        readermode.
        """
        self.host = host
        self.file = file
        self.debugging = 0
        self.welcome = self._getresp()

        # Inquire about capabilities (RFC 3977).
        self._caps = Tupu
        self.getcapabilities()

        # 'MODE READER' ni sometimes necessary to enable 'reader' mode.
        # However, the order kwenye which 'MODE READER' na 'AUTHINFO' need to
        # arrive differs between some NNTP servers. If _setreadermode() fails
        # ukijumuisha an authorization failed error, it will set this to Kweli;
        # the login() routine will interpret that kama a request to try again
        # after performing its normal function.
        # Enable only ikiwa we're sio already kwenye READER mode anyway.
        self.readermode_afterauth = Uongo
        ikiwa readermode na 'READER' haiko kwenye self._caps:
            self._setreadermode()
            ikiwa sio self.readermode_afterauth:
                # Capabilities might have changed after MODE READER
                self._caps = Tupu
                self.getcapabilities()

        # RFC 4642 2.2.2: Both the client na the server MUST know ikiwa there is
        # a TLS session active.  A client MUST NOT attempt to start a TLS
        # session ikiwa a TLS session ni already active.
        self.tls_on = Uongo

        # Log kwenye na encryption setup order ni left to subclasses.
        self.authenticated = Uongo

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *args):
        is_connected = lambda: hasattr(self, "file")
        ikiwa is_connected():
            jaribu:
                self.quit()
            tatizo (OSError, EOFError):
                pita
            mwishowe:
                ikiwa is_connected():
                    self._close()

    eleza getwelcome(self):
        """Get the welcome message kutoka the server
        (this ni read na squirreled away by __init__()).
        If the response code ni 200, posting ni allowed;
        ikiwa it 201, posting ni sio allowed."""

        ikiwa self.debugging: andika('*welcome*', repr(self.welcome))
        rudisha self.welcome

    eleza getcapabilities(self):
        """Get the server capabilities, kama read by __init__().
        If the CAPABILITIES command ni sio supported, an empty dict is
        rudishaed."""
        ikiwa self._caps ni Tupu:
            self.nntp_version = 1
            self.nntp_implementation = Tupu
            jaribu:
                resp, caps = self.capabilities()
            tatizo (NNTPPermanentError, NNTPTemporaryError):
                # Server doesn't support capabilities
                self._caps = {}
            isipokua:
                self._caps = caps
                ikiwa 'VERSION' kwenye caps:
                    # The server can advertise several supported versions,
                    # choose the highest.
                    self.nntp_version = max(map(int, caps['VERSION']))
                ikiwa 'IMPLEMENTATION' kwenye caps:
                    self.nntp_implementation = ' '.join(caps['IMPLEMENTATION'])
        rudisha self._caps

    eleza set_debuglevel(self, level):
        """Set the debugging level.  Argument 'level' means:
        0: no debugging output (default)
        1: print commands na responses but sio body text etc.
        2: also print raw lines read na sent before stripping CR/LF"""

        self.debugging = level
    debug = set_debuglevel

    eleza _putline(self, line):
        """Internal: send one line to the server, appending CRLF.
        The `line` must be a bytes-like object."""
        sys.audit("nntplib.putline", self, line)
        line = line + _CRLF
        ikiwa self.debugging > 1: andika('*put*', repr(line))
        self.file.write(line)
        self.file.flush()

    eleza _putcmd(self, line):
        """Internal: send one command to the server (through _putline()).
        The `line` must be a unicode string."""
        ikiwa self.debugging: andika('*cmd*', repr(line))
        line = line.encode(self.encoding, self.errors)
        self._putline(line)

    eleza _getline(self, strip_crlf=Kweli):
        """Internal: rudisha one line kutoka the server, stripping _CRLF.
        Raise EOFError ikiwa the connection ni closed.
        Returns a bytes object."""
        line = self.file.readline(_MAXLINE +1)
        ikiwa len(line) > _MAXLINE:
            ashiria NNTPDataError('line too long')
        ikiwa self.debugging > 1:
            andika('*get*', repr(line))
        ikiwa sio line: ashiria EOFError
        ikiwa strip_crlf:
            ikiwa line[-2:] == _CRLF:
                line = line[:-2]
            lasivyo line[-1:] kwenye _CRLF:
                line = line[:-1]
        rudisha line

    eleza _getresp(self):
        """Internal: get a response kutoka the server.
        Raise various errors ikiwa the response indicates an error.
        Returns a unicode string."""
        resp = self._getline()
        ikiwa self.debugging: andika('*resp*', repr(resp))
        resp = resp.decode(self.encoding, self.errors)
        c = resp[:1]
        ikiwa c == '4':
            ashiria NNTPTemporaryError(resp)
        ikiwa c == '5':
            ashiria NNTPPermanentError(resp)
        ikiwa c haiko kwenye '123':
            ashiria NNTPProtocolError(resp)
        rudisha resp

    eleza _getlongresp(self, file=Tupu):
        """Internal: get a response plus following text kutoka the server.
        Raise various errors ikiwa the response indicates an error.

        Returns a (response, lines) tuple where `response` ni a unicode
        string na `lines` ni a list of bytes objects.
        If `file` ni a file-like object, it must be open kwenye binary mode.
        """

        openedFile = Tupu
        jaribu:
            # If a string was pitaed then open a file ukijumuisha that name
            ikiwa isinstance(file, (str, bytes)):
                openedFile = file = open(file, "wb")

            resp = self._getresp()
            ikiwa resp[:3] haiko kwenye _LONGRESP:
                ashiria NNTPReplyError(resp)

            lines = []
            ikiwa file ni sio Tupu:
                # XXX lines = Tupu instead?
                terminators = (b'.' + _CRLF, b'.\n')
                wakati 1:
                    line = self._getline(Uongo)
                    ikiwa line kwenye terminators:
                        koma
                    ikiwa line.startswith(b'..'):
                        line = line[1:]
                    file.write(line)
            isipokua:
                terminator = b'.'
                wakati 1:
                    line = self._getline()
                    ikiwa line == terminator:
                        koma
                    ikiwa line.startswith(b'..'):
                        line = line[1:]
                    lines.append(line)
        mwishowe:
            # If this method created the file, then it must close it
            ikiwa openedFile:
                openedFile.close()

        rudisha resp, lines

    eleza _shortcmd(self, line):
        """Internal: send a command na get the response.
        Same rudisha value kama _getresp()."""
        self._putcmd(line)
        rudisha self._getresp()

    eleza _longcmd(self, line, file=Tupu):
        """Internal: send a command na get the response plus following text.
        Same rudisha value kama _getlongresp()."""
        self._putcmd(line)
        rudisha self._getlongresp(file)

    eleza _longcmdstring(self, line, file=Tupu):
        """Internal: send a command na get the response plus following text.
        Same kama _longcmd() na _getlongresp(), tatizo that the rudishaed `lines`
        are unicode strings rather than bytes objects.
        """
        self._putcmd(line)
        resp, list = self._getlongresp(file)
        rudisha resp, [line.decode(self.encoding, self.errors)
                      kila line kwenye list]

    eleza _getoverviewfmt(self):
        """Internal: get the overview format. Queries the server ikiwa not
        already done, isipokua rudishas the cached value."""
        jaribu:
            rudisha self._cachedoverviewfmt
        tatizo AttributeError:
            pita
        jaribu:
            resp, lines = self._longcmdstring("LIST OVERVIEW.FMT")
        tatizo NNTPPermanentError:
            # Not supported by server?
            fmt = _DEFAULT_OVERVIEW_FMT[:]
        isipokua:
            fmt = _parse_overview_fmt(lines)
        self._cachedoverviewfmt = fmt
        rudisha fmt

    eleza _grouplist(self, lines):
        # Parse lines into "group last first flag"
        rudisha [GroupInfo(*line.split()) kila line kwenye lines]

    eleza capabilities(self):
        """Process a CAPABILITIES command.  Not supported by all servers.
        Return:
        - resp: server response ikiwa successful
        - caps: a dictionary mapping capability names to lists of tokens
        (kila example {'VERSION': ['2'], 'OVER': [], LIST: ['ACTIVE', 'HEADERS'] })
        """
        caps = {}
        resp, lines = self._longcmdstring("CAPABILITIES")
        kila line kwenye lines:
            name, *tokens = line.split()
            caps[name] = tokens
        rudisha resp, caps

    eleza newgroups(self, date, *, file=Tupu):
        """Process a NEWGROUPS command.  Arguments:
        - date: a date ama datetime object
        Return:
        - resp: server response ikiwa successful
        - list: list of newsgroup names
        """
        ikiwa sio isinstance(date, (datetime.date, datetime.date)):
            ashiria TypeError(
                "the date parameter must be a date ama datetime object, "
                "not '{:40}'".format(date.__class__.__name__))
        date_str, time_str = _unparse_datetime(date, self.nntp_version < 2)
        cmd = 'NEWGROUPS {0} {1}'.format(date_str, time_str)
        resp, lines = self._longcmdstring(cmd, file)
        rudisha resp, self._grouplist(lines)

    eleza newnews(self, group, date, *, file=Tupu):
        """Process a NEWNEWS command.  Arguments:
        - group: group name ama '*'
        - date: a date ama datetime object
        Return:
        - resp: server response ikiwa successful
        - list: list of message ids
        """
        ikiwa sio isinstance(date, (datetime.date, datetime.date)):
            ashiria TypeError(
                "the date parameter must be a date ama datetime object, "
                "not '{:40}'".format(date.__class__.__name__))
        date_str, time_str = _unparse_datetime(date, self.nntp_version < 2)
        cmd = 'NEWNEWS {0} {1} {2}'.format(group, date_str, time_str)
        rudisha self._longcmdstring(cmd, file)

    eleza list(self, group_pattern=Tupu, *, file=Tupu):
        """Process a LIST ama LIST ACTIVE command. Arguments:
        - group_pattern: a pattern indicating which groups to query
        - file: Filename string ama file object to store the result in
        Returns:
        - resp: server response ikiwa successful
        - list: list of (group, last, first, flag) (strings)
        """
        ikiwa group_pattern ni sio Tupu:
            command = 'LIST ACTIVE ' + group_pattern
        isipokua:
            command = 'LIST'
        resp, lines = self._longcmdstring(command, file)
        rudisha resp, self._grouplist(lines)

    eleza _getdescriptions(self, group_pattern, rudisha_all):
        line_pat = re.compile('^(?P<group>[^ \t]+)[ \t]+(.*)$')
        # Try the more std (acc. to RFC2980) LIST NEWSGROUPS first
        resp, lines = self._longcmdstring('LIST NEWSGROUPS ' + group_pattern)
        ikiwa sio resp.startswith('215'):
            # Now the deprecated XGTITLE.  This either ashirias an error
            # ama succeeds ukijumuisha the same output structure kama LIST
            # NEWSGROUPS.
            resp, lines = self._longcmdstring('XGTITLE ' + group_pattern)
        groups = {}
        kila raw_line kwenye lines:
            match = line_pat.search(raw_line.strip())
            ikiwa match:
                name, desc = match.group(1, 2)
                ikiwa sio rudisha_all:
                    rudisha desc
                groups[name] = desc
        ikiwa rudisha_all:
            rudisha resp, groups
        isipokua:
            # Nothing found
            rudisha ''

    eleza description(self, group):
        """Get a description kila a single group.  If more than one
        group matches ('group' ni a pattern), rudisha the first.  If no
        group matches, rudisha an empty string.

        This elides the response code kutoka the server, since it can
        only be '215' ama '285' (kila xgtitle) anyway.  If the response
        code ni needed, use the 'descriptions' method.

        NOTE: This neither checks kila a wildcard kwenye 'group' nor does
        it check whether the group actually exists."""
        rudisha self._getdescriptions(group, Uongo)

    eleza descriptions(self, group_pattern):
        """Get descriptions kila a range of groups."""
        rudisha self._getdescriptions(group_pattern, Kweli)

    eleza group(self, name):
        """Process a GROUP command.  Argument:
        - group: the group name
        Returns:
        - resp: server response ikiwa successful
        - count: number of articles
        - first: first article number
        - last: last article number
        - name: the group name
        """
        resp = self._shortcmd('GROUP ' + name)
        ikiwa sio resp.startswith('211'):
            ashiria NNTPReplyError(resp)
        words = resp.split()
        count = first = last = 0
        n = len(words)
        ikiwa n > 1:
            count = words[1]
            ikiwa n > 2:
                first = words[2]
                ikiwa n > 3:
                    last = words[3]
                    ikiwa n > 4:
                        name = words[4].lower()
        rudisha resp, int(count), int(first), int(last), name

    eleza help(self, *, file=Tupu):
        """Process a HELP command. Argument:
        - file: Filename string ama file object to store the result in
        Returns:
        - resp: server response ikiwa successful
        - list: list of strings rudishaed by the server kwenye response to the
                HELP command
        """
        rudisha self._longcmdstring('HELP', file)

    eleza _statparse(self, resp):
        """Internal: parse the response line of a STAT, NEXT, LAST,
        ARTICLE, HEAD ama BODY command."""
        ikiwa sio resp.startswith('22'):
            ashiria NNTPReplyError(resp)
        words = resp.split()
        art_num = int(words[1])
        message_id = words[2]
        rudisha resp, art_num, message_id

    eleza _statcmd(self, line):
        """Internal: process a STAT, NEXT ama LAST command."""
        resp = self._shortcmd(line)
        rudisha self._statparse(resp)

    eleza stat(self, message_spec=Tupu):
        """Process a STAT command.  Argument:
        - message_spec: article number ama message id (ikiwa sio specified,
          the current article ni selected)
        Returns:
        - resp: server response ikiwa successful
        - art_num: the article number
        - message_id: the message id
        """
        ikiwa message_spec:
            rudisha self._statcmd('STAT {0}'.format(message_spec))
        isipokua:
            rudisha self._statcmd('STAT')

    eleza next(self):
        """Process a NEXT command.  No arguments.  Return kama kila STAT."""
        rudisha self._statcmd('NEXT')

    eleza last(self):
        """Process a LAST command.  No arguments.  Return kama kila STAT."""
        rudisha self._statcmd('LAST')

    eleza _artcmd(self, line, file=Tupu):
        """Internal: process a HEAD, BODY ama ARTICLE command."""
        resp, lines = self._longcmd(line, file)
        resp, art_num, message_id = self._statparse(resp)
        rudisha resp, ArticleInfo(art_num, message_id, lines)

    eleza head(self, message_spec=Tupu, *, file=Tupu):
        """Process a HEAD command.  Argument:
        - message_spec: article number ama message id
        - file: filename string ama file object to store the headers in
        Returns:
        - resp: server response ikiwa successful
        - ArticleInfo: (article number, message id, list of header lines)
        """
        ikiwa message_spec ni sio Tupu:
            cmd = 'HEAD {0}'.format(message_spec)
        isipokua:
            cmd = 'HEAD'
        rudisha self._artcmd(cmd, file)

    eleza body(self, message_spec=Tupu, *, file=Tupu):
        """Process a BODY command.  Argument:
        - message_spec: article number ama message id
        - file: filename string ama file object to store the body in
        Returns:
        - resp: server response ikiwa successful
        - ArticleInfo: (article number, message id, list of body lines)
        """
        ikiwa message_spec ni sio Tupu:
            cmd = 'BODY {0}'.format(message_spec)
        isipokua:
            cmd = 'BODY'
        rudisha self._artcmd(cmd, file)

    eleza article(self, message_spec=Tupu, *, file=Tupu):
        """Process an ARTICLE command.  Argument:
        - message_spec: article number ama message id
        - file: filename string ama file object to store the article in
        Returns:
        - resp: server response ikiwa successful
        - ArticleInfo: (article number, message id, list of article lines)
        """
        ikiwa message_spec ni sio Tupu:
            cmd = 'ARTICLE {0}'.format(message_spec)
        isipokua:
            cmd = 'ARTICLE'
        rudisha self._artcmd(cmd, file)

    eleza slave(self):
        """Process a SLAVE command.  Returns:
        - resp: server response ikiwa successful
        """
        rudisha self._shortcmd('SLAVE')

    eleza xhdr(self, hdr, str, *, file=Tupu):
        """Process an XHDR command (optional server extension).  Arguments:
        - hdr: the header type (e.g. 'subject')
        - str: an article nr, a message id, ama a range nr1-nr2
        - file: Filename string ama file object to store the result in
        Returns:
        - resp: server response ikiwa successful
        - list: list of (nr, value) strings
        """
        pat = re.compile('^([0-9]+) ?(.*)\n?')
        resp, lines = self._longcmdstring('XHDR {0} {1}'.format(hdr, str), file)
        eleza remove_number(line):
            m = pat.match(line)
            rudisha m.group(1, 2) ikiwa m isipokua line
        rudisha resp, [remove_number(line) kila line kwenye lines]

    eleza xover(self, start, end, *, file=Tupu):
        """Process an XOVER command (optional server extension) Arguments:
        - start: start of range
        - end: end of range
        - file: Filename string ama file object to store the result in
        Returns:
        - resp: server response ikiwa successful
        - list: list of dicts containing the response fields
        """
        resp, lines = self._longcmdstring('XOVER {0}-{1}'.format(start, end),
                                          file)
        fmt = self._getoverviewfmt()
        rudisha resp, _parse_overview(lines, fmt)

    eleza over(self, message_spec, *, file=Tupu):
        """Process an OVER command.  If the command isn't supported, fall
        back to XOVER. Arguments:
        - message_spec:
            - either a message id, indicating the article to fetch
              information about
            - ama a (start, end) tuple, indicating a range of article numbers;
              ikiwa end ni Tupu, information up to the newest message will be
              retrieved
            - ama Tupu, indicating the current article number must be used
        - file: Filename string ama file object to store the result in
        Returns:
        - resp: server response ikiwa successful
        - list: list of dicts containing the response fields

        NOTE: the "message id" form isn't supported by XOVER
        """
        cmd = 'OVER' ikiwa 'OVER' kwenye self._caps isipokua 'XOVER'
        ikiwa isinstance(message_spec, (tuple, list)):
            start, end = message_spec
            cmd += ' {0}-{1}'.format(start, end ama '')
        lasivyo message_spec ni sio Tupu:
            cmd = cmd + ' ' + message_spec
        resp, lines = self._longcmdstring(cmd, file)
        fmt = self._getoverviewfmt()
        rudisha resp, _parse_overview(lines, fmt)

    eleza xgtitle(self, group, *, file=Tupu):
        """Process an XGTITLE command (optional server extension) Arguments:
        - group: group name wildcard (i.e. news.*)
        Returns:
        - resp: server response ikiwa successful
        - list: list of (name,title) strings"""
        warnings.warn("The XGTITLE extension ni sio actively used, "
                      "use descriptions() instead",
                      DeprecationWarning, 2)
        line_pat = re.compile('^([^ \t]+)[ \t]+(.*)$')
        resp, raw_lines = self._longcmdstring('XGTITLE ' + group, file)
        lines = []
        kila raw_line kwenye raw_lines:
            match = line_pat.search(raw_line.strip())
            ikiwa match:
                lines.append(match.group(1, 2))
        rudisha resp, lines

    eleza xpath(self, id):
        """Process an XPATH command (optional server extension) Arguments:
        - id: Message id of article
        Returns:
        resp: server response ikiwa successful
        path: directory path to article
        """
        warnings.warn("The XPATH extension ni sio actively used",
                      DeprecationWarning, 2)

        resp = self._shortcmd('XPATH {0}'.format(id))
        ikiwa sio resp.startswith('223'):
            ashiria NNTPReplyError(resp)
        jaribu:
            [resp_num, path] = resp.split()
        tatizo ValueError:
            ashiria NNTPReplyError(resp) kutoka Tupu
        isipokua:
            rudisha resp, path

    eleza date(self):
        """Process the DATE command.
        Returns:
        - resp: server response ikiwa successful
        - date: datetime object
        """
        resp = self._shortcmd("DATE")
        ikiwa sio resp.startswith('111'):
            ashiria NNTPReplyError(resp)
        elem = resp.split()
        ikiwa len(elem) != 2:
            ashiria NNTPDataError(resp)
        date = elem[1]
        ikiwa len(date) != 14:
            ashiria NNTPDataError(resp)
        rudisha resp, _parse_datetime(date, Tupu)

    eleza _post(self, command, f):
        resp = self._shortcmd(command)
        # Raises a specific exception ikiwa posting ni sio allowed
        ikiwa sio resp.startswith('3'):
            ashiria NNTPReplyError(resp)
        ikiwa isinstance(f, (bytes, bytearray)):
            f = f.splitlines()
        # We don't use _putline() because:
        # - we don't want additional CRLF ikiwa the file ama iterable ni already
        #   kwenye the right format
        # - we don't want a spurious flush() after each line ni written
        kila line kwenye f:
            ikiwa sio line.endswith(_CRLF):
                line = line.rstrip(b"\r\n") + _CRLF
            ikiwa line.startswith(b'.'):
                line = b'.' + line
            self.file.write(line)
        self.file.write(b".\r\n")
        self.file.flush()
        rudisha self._getresp()

    eleza post(self, data):
        """Process a POST command.  Arguments:
        - data: bytes object, iterable ama file containing the article
        Returns:
        - resp: server response ikiwa successful"""
        rudisha self._post('POST', data)

    eleza ihave(self, message_id, data):
        """Process an IHAVE command.  Arguments:
        - message_id: message-id of the article
        - data: file containing the article
        Returns:
        - resp: server response ikiwa successful
        Note that ikiwa the server refuses the article an exception ni ashiriad."""
        rudisha self._post('IHAVE {0}'.format(message_id), data)

    eleza _close(self):
        self.file.close()
        toa self.file

    eleza quit(self):
        """Process a QUIT command na close the socket.  Returns:
        - resp: server response ikiwa successful"""
        jaribu:
            resp = self._shortcmd('QUIT')
        mwishowe:
            self._close()
        rudisha resp

    eleza login(self, user=Tupu, pitaword=Tupu, usenetrc=Kweli):
        ikiwa self.authenticated:
            ashiria ValueError("Already logged in.")
        ikiwa sio user na sio usenetrc:
            ashiria ValueError(
                "At least one of `user` na `usenetrc` must be specified")
        # If no login/pitaword was specified but netrc was requested,
        # try to get them kutoka ~/.netrc
        # Presume that ikiwa .netrc has an entry, NNRP authentication ni required.
        jaribu:
            ikiwa usenetrc na sio user:
                agiza netrc
                credentials = netrc.netrc()
                auth = credentials.authenticators(self.host)
                ikiwa auth:
                    user = auth[0]
                    pitaword = auth[2]
        tatizo OSError:
            pita
        # Perform NNTP authentication ikiwa needed.
        ikiwa sio user:
            rudisha
        resp = self._shortcmd('authinfo user ' + user)
        ikiwa resp.startswith('381'):
            ikiwa sio pitaword:
                ashiria NNTPReplyError(resp)
            isipokua:
                resp = self._shortcmd('authinfo pita ' + pitaword)
                ikiwa sio resp.startswith('281'):
                    ashiria NNTPPermanentError(resp)
        # Capabilities might have changed after login
        self._caps = Tupu
        self.getcapabilities()
        # Attempt to send mode reader ikiwa it was requested after login.
        # Only do so ikiwa we're haiko kwenye reader mode already.
        ikiwa self.readermode_afterauth na 'READER' haiko kwenye self._caps:
            self._setreadermode()
            # Capabilities might have changed after MODE READER
            self._caps = Tupu
            self.getcapabilities()

    eleza _setreadermode(self):
        jaribu:
            self.welcome = self._shortcmd('mode reader')
        tatizo NNTPPermanentError:
            # Error 5xx, probably 'not implemented'
            pita
        tatizo NNTPTemporaryError kama e:
            ikiwa e.response.startswith('480'):
                # Need authorization before 'mode reader'
                self.readermode_afterauth = Kweli
            isipokua:
                ashiria

    ikiwa _have_ssl:
        eleza starttls(self, context=Tupu):
            """Process a STARTTLS command. Arguments:
            - context: SSL context to use kila the encrypted connection
            """
            # Per RFC 4642, STARTTLS MUST NOT be sent after authentication ama if
            # a TLS session already exists.
            ikiwa self.tls_on:
                ashiria ValueError("TLS ni already enabled.")
            ikiwa self.authenticated:
                ashiria ValueError("TLS cannot be started after authentication.")
            resp = self._shortcmd('STARTTLS')
            ikiwa resp.startswith('382'):
                self.file.close()
                self.sock = _encrypt_on(self.sock, context, self.host)
                self.file = self.sock.makefile("rwb")
                self.tls_on = Kweli
                # Capabilities may change after TLS starts up, so ask kila them
                # again.
                self._caps = Tupu
                self.getcapabilities()
            isipokua:
                ashiria NNTPError("TLS failed to start.")


kundi NNTP(_NNTPBase):

    eleza __init__(self, host, port=NNTP_PORT, user=Tupu, pitaword=Tupu,
                 readermode=Tupu, usenetrc=Uongo,
                 timeout=_GLOBAL_DEFAULT_TIMEOUT):
        """Initialize an instance.  Arguments:
        - host: hostname to connect to
        - port: port to connect to (default the standard NNTP port)
        - user: username to authenticate with
        - pitaword: pitaword to use ukijumuisha username
        - readermode: ikiwa true, send 'mode reader' command after
                      connecting.
        - usenetrc: allow loading username na pitaword kutoka ~/.netrc file
                    ikiwa sio specified explicitly
        - timeout: timeout (in seconds) used kila socket connections

        readermode ni sometimes necessary ikiwa you are connecting to an
        NNTP server on the local machine na intend to call
        reader-specific commands, such kama `group'.  If you get
        unexpected NNTPPermanentErrors, you might need to set
        readermode.
        """
        self.host = host
        self.port = port
        sys.audit("nntplib.connect", self, host, port)
        self.sock = socket.create_connection((host, port), timeout)
        file = Tupu
        jaribu:
            file = self.sock.makefile("rwb")
            _NNTPBase.__init__(self, file, host,
                               readermode, timeout)
            ikiwa user ama usenetrc:
                self.login(user, pitaword, usenetrc)
        except:
            ikiwa file:
                file.close()
            self.sock.close()
            ashiria

    eleza _close(self):
        jaribu:
            _NNTPBase._close(self)
        mwishowe:
            self.sock.close()


ikiwa _have_ssl:
    kundi NNTP_SSL(_NNTPBase):

        eleza __init__(self, host, port=NNTP_SSL_PORT,
                    user=Tupu, pitaword=Tupu, ssl_context=Tupu,
                    readermode=Tupu, usenetrc=Uongo,
                    timeout=_GLOBAL_DEFAULT_TIMEOUT):
            """This works identically to NNTP.__init__, tatizo kila the change
            kwenye default port na the `ssl_context` argument kila SSL connections.
            """
            sys.audit("nntplib.connect", self, host, port)
            self.sock = socket.create_connection((host, port), timeout)
            file = Tupu
            jaribu:
                self.sock = _encrypt_on(self.sock, ssl_context, host)
                file = self.sock.makefile("rwb")
                _NNTPBase.__init__(self, file, host,
                                   readermode=readermode, timeout=timeout)
                ikiwa user ama usenetrc:
                    self.login(user, pitaword, usenetrc)
            except:
                ikiwa file:
                    file.close()
                self.sock.close()
                ashiria

        eleza _close(self):
            jaribu:
                _NNTPBase._close(self)
            mwishowe:
                self.sock.close()

    __all__.append("NNTP_SSL")


# Test retrieval when run kama a script.
ikiwa __name__ == '__main__':
    agiza argparse

    parser = argparse.ArgumentParser(description="""\
        nntplib built-in demo - display the latest articles kwenye a newsgroup""")
    parser.add_argument('-g', '--group', default='gmane.comp.python.general',
                        help='group to fetch messages kutoka (default: %(default)s)')
    parser.add_argument('-s', '--server', default='news.gmane.org',
                        help='NNTP server hostname (default: %(default)s)')
    parser.add_argument('-p', '--port', default=-1, type=int,
                        help='NNTP port number (default: %s / %s)' % (NNTP_PORT, NNTP_SSL_PORT))
    parser.add_argument('-n', '--nb-articles', default=10, type=int,
                        help='number of articles to fetch (default: %(default)s)')
    parser.add_argument('-S', '--ssl', action='store_true', default=Uongo,
                        help='use NNTP over SSL')
    args = parser.parse_args()

    port = args.port
    ikiwa sio args.ssl:
        ikiwa port == -1:
            port = NNTP_PORT
        s = NNTP(host=args.server, port=port)
    isipokua:
        ikiwa port == -1:
            port = NNTP_SSL_PORT
        s = NNTP_SSL(host=args.server, port=port)

    caps = s.getcapabilities()
    ikiwa 'STARTTLS' kwenye caps:
        s.starttls()
    resp, count, first, last, name = s.group(args.group)
    andika('Group', name, 'has', count, 'articles, range', first, 'to', last)

    eleza cut(s, lim):
        ikiwa len(s) > lim:
            s = s[:lim - 4] + "..."
        rudisha s

    first = str(int(last) - args.nb_articles + 1)
    resp, overviews = s.xover(first, last)
    kila artnum, over kwenye overviews:
        author = decode_header(over['kutoka']).split('<', 1)[0]
        subject = decode_header(over['subject'])
        lines = int(over[':lines'])
        andika("{:7} {:20} {:42} ({})".format(
              artnum, cut(author, 20), cut(subject, 42), lines)
              )

    s.quit()
