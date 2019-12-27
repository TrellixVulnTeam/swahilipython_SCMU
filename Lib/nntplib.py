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

Here 'resp' is the server response line.
Error responses are turned into exceptions.

To post an article kutoka a file:
>>> f = open(filename, 'rb') # file containing article, including header
>>> resp = s.post(f)
>>>

For descriptions of all methods, read the comments in the code below.
Note that all arguments and rudisha values representing article numbers
are strings, not numbers, since they are rarely used for calculations.
"""

# RFC 977 by Brian Kantor and Phil Lapsley.
# xover, xgtitle, xpath, date methods by Kevan Heydon

# Incompatible changes kutoka the 2.x nntplib:
# - all commands are encoded as UTF-8 data (using the "surrogateescape"
#   error handler), except for raw message data (POST, IHAVE)
# - all responses are decoded as UTF-8 data (using the "surrogateescape"
#   error handler), except for raw message data (ARTICLE, HEAD, BODY)
# - the `file` argument to various methods is keyword-only
#
# - NNTP.date() returns a datetime object
# - NNTP.newgroups() and NNTP.newnews() take a datetime (or date) object,
#   rather than a pair of (date, time) strings.
# - NNTP.newgroups() and NNTP.list() rudisha a list of GroupInfo named tuples
# - NNTP.descriptions() returns a dict mapping group names to descriptions
# - NNTP.xover() returns a list of dicts mapping field names (header or metadata)
#   to field values; each dict representing a message overview.
# - NNTP.article(), NNTP.head() and NNTP.body() rudisha a (response, ArticleInfo)
#   tuple.
# - the "internal" methods have been marked private (they now start with
#   an underscore)

# Other changes kutoka the 2.x/3.1 nntplib:
# - automatic querying of capabilities at connect
# - New method NNTP.getcapabilities()
# - New method NNTP.over()
# - New helper function decode_header()
# - NNTP.post() and NNTP.ihave() accept file objects, bytes-like objects and
#   arbitrary iterables yielding lines.
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

try:
    agiza ssl
except ImportError:
    _have_ssl = False
else:
    _have_ssl = True

kutoka email.header agiza decode_header as _email_decode_header
kutoka socket agiza _GLOBAL_DEFAULT_TIMEOUT

__all__ = ["NNTP",
           "NNTPError", "NNTPReplyError", "NNTPTemporaryError",
           "NNTPPermanentError", "NNTPProtocolError", "NNTPDataError",
           "decode_header",
           ]

# maximal line length when calling readline(). This is to prevent
# reading arbitrary length lines. RFC 3977 limits NNTP line length to
# 512 characters, including CRLF. We have selected 2048 just to be on
# the safe side.
_MAXLINE = 2048


# Exceptions raised when an error or invalid response is received
kundi NNTPError(Exception):
    """Base kundi for all nntplib exceptions"""
    eleza __init__(self, *args):
        Exception.__init__(self, *args)
        try:
            self.response = args[0]
        except IndexError:
            self.response = 'No response given'

kundi NNTPReplyError(NNTPError):
    """Unexpected [123]xx reply"""
    pass

kundi NNTPTemporaryError(NNTPError):
    """4xx errors"""
    pass

kundi NNTPPermanentError(NNTPError):
    """5xx errors"""
    pass

kundi NNTPProtocolError(NNTPError):
    """Response does not begin with [1-5]"""
    pass

kundi NNTPDataError(NNTPError):
    """Error in response data"""
    pass


# Standard port used by NNTP servers
NNTP_PORT = 119
NNTP_SSL_PORT = 563

# Response numbers that are followed by additional text (e.g. article)
_LONGRESP = {
    '100',   # HELP
    '101',   # CAPABILITIES
    '211',   # LISTGROUP   (also not multi-line with GROUP)
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

# Default decoded value for LIST OVERVIEW.FMT ikiwa not supported
_DEFAULT_OVERVIEW_FMT = [
    "subject", "kutoka", "date", "message-id", "references", ":bytes", ":lines"]

# Alternative names allowed in LIST OVERVIEW.FMT response
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
    and decodes it as a (possibly non-ASCII) readable value."""
    parts = []
    for v, enc in _email_decode_header(header_str):
        ikiwa isinstance(v, bytes):
            parts.append(v.decode(enc or 'ascii'))
        else:
            parts.append(v)
    rudisha ''.join(parts)

eleza _parse_overview_fmt(lines):
    """Parse a list of string representing the response to LIST OVERVIEW.FMT
    and rudisha a list of header/metadata names.
    Raises NNTPDataError ikiwa the response is not compliant
    (cf. RFC 3977, section 8.4)."""
    fmt = []
    for line in lines:
        ikiwa line[0] == ':':
            # Metadata name (e.g. ":bytes")
            name, _, suffix = line[1:].partition(':')
            name = ':' + name
        else:
            # Header name (e.g. "Subject:" or "Xref:full")
            name, _, suffix = line.partition(':')
        name = name.lower()
        name = _OVERVIEW_FMT_ALTERNATIVES.get(name, name)
        # Should we do something with the suffix?
        fmt.append(name)
    defaults = _DEFAULT_OVERVIEW_FMT
    ikiwa len(fmt) < len(defaults):
        raise NNTPDataError("LIST OVERVIEW.FMT response too short")
    ikiwa fmt[:len(defaults)] != defaults:
        raise NNTPDataError("LIST OVERVIEW.FMT redefines default fields")
    rudisha fmt

eleza _parse_overview(lines, fmt, data_process_func=None):
    """Parse the response to an OVER or XOVER command according to the
    overview format `fmt`."""
    n_defaults = len(_DEFAULT_OVERVIEW_FMT)
    overview = []
    for line in lines:
        fields = {}
        article_number, *tokens = line.split('\t')
        article_number = int(article_number)
        for i, token in enumerate(tokens):
            ikiwa i >= len(fmt):
                # XXX should we raise an error? Some servers might not
                # support LIST OVERVIEW.FMT and still rudisha additional
                # headers.
                continue
            field_name = fmt[i]
            is_metadata = field_name.startswith(':')
            ikiwa i >= n_defaults and not is_metadata:
                # Non-default header names are included in full in the response
                # (unless the field is totally empty)
                h = field_name + ": "
                ikiwa token and token[:len(h)].lower() != h:
                    raise NNTPDataError("OVER/XOVER response doesn't include "
                                        "names of additional headers")
                token = token[len(h):] ikiwa token else None
            fields[fmt[i]] = token
        overview.append((article_number, fields))
    rudisha overview

eleza _parse_datetime(date_str, time_str=None):
    """Parse a pair of (date, time) strings, and rudisha a datetime object.
    If only the date is given, it is assumed to be date and time
    concatenated together (e.g. response to the DATE command).
    """
    ikiwa time_str is None:
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
    elikiwa year < 100:
        year += 1900
    rudisha datetime.datetime(year, month, day, hours, minutes, seconds)

eleza _unparse_datetime(dt, legacy=False):
    """Format a date or datetime object as a pair of (date, time) strings
    in the format required by the NEWNEWS and NEWGROUPS commands.  If a
    date object is passed, the time is assumed to be midnight (00h00).

    The returned representation depends on the legacy flag:
    * ikiwa legacy is False (the default):
      date has the YYYYMMDD format and time the HHMMSS format
    * ikiwa legacy is True:
      date has the YYMMDD format and time the HHMMSS format.
    RFC 3977 compliant servers should understand both formats; therefore,
    legacy is only needed when talking to old servers.
    """
    ikiwa not isinstance(dt, datetime.datetime):
        time_str = "000000"
    else:
        time_str = "{0.hour:02d}{0.minute:02d}{0.second:02d}".format(dt)
    y = dt.year
    ikiwa legacy:
        y = y % 100
        date_str = "{0:02d}{1.month:02d}{1.day:02d}".format(y, dt)
    else:
        date_str = "{0:04d}{1.month:02d}{1.day:02d}".format(y, dt)
    rudisha date_str, time_str


ikiwa _have_ssl:

    eleza _encrypt_on(sock, context, hostname):
        """Wrap a socket in SSL/TLS. Arguments:
        - sock: Socket to wrap
        - context: SSL context to use for the encrypted connection
        Returns:
        - sock: New, encrypted socket.
        """
        # Generate a default SSL context ikiwa none was passed.
        ikiwa context is None:
            context = ssl._create_stdlib_context()
        rudisha context.wrap_socket(sock, server_hostname=hostname)


# The classes themselves
kundi _NNTPBase:
    # UTF-8 is the character set for all NNTP commands and responses: they
    # are automatically encoded (when sending) and decoded (and receiving)
    # by this class.
    # However, some multi-line data blocks can contain arbitrary bytes (for
    # example, latin-1 or utf-16 data in the body of a message). Commands
    # taking (POST, IHAVE) or returning (HEAD, BODY, ARTICLE) raw message
    # data will therefore only accept and produce bytes objects.
    # Furthermore, since there could be non-compliant servers out there,
    # we use 'surrogateescape' as the error handler for fault tolerance
    # and easy round-tripping. This could be useful for some applications
    # (e.g. NNTP gateways).

    encoding = 'utf-8'
    errors = 'surrogateescape'

    eleza __init__(self, file, host,
                 readermode=None, timeout=_GLOBAL_DEFAULT_TIMEOUT):
        """Initialize an instance.  Arguments:
        - file: file-like object (open for read/write in binary mode)
        - host: hostname of the server
        - readermode: ikiwa true, send 'mode reader' command after
                      connecting.
        - timeout: timeout (in seconds) used for socket connections

        readermode is sometimes necessary ikiwa you are connecting to an
        NNTP server on the local machine and intend to call
        reader-specific commands, such as `group'.  If you get
        unexpected NNTPPermanentErrors, you might need to set
        readermode.
        """
        self.host = host
        self.file = file
        self.debugging = 0
        self.welcome = self._getresp()

        # Inquire about capabilities (RFC 3977).
        self._caps = None
        self.getcapabilities()

        # 'MODE READER' is sometimes necessary to enable 'reader' mode.
        # However, the order in which 'MODE READER' and 'AUTHINFO' need to
        # arrive differs between some NNTP servers. If _setreadermode() fails
        # with an authorization failed error, it will set this to True;
        # the login() routine will interpret that as a request to try again
        # after performing its normal function.
        # Enable only ikiwa we're not already in READER mode anyway.
        self.readermode_afterauth = False
        ikiwa readermode and 'READER' not in self._caps:
            self._setreadermode()
            ikiwa not self.readermode_afterauth:
                # Capabilities might have changed after MODE READER
                self._caps = None
                self.getcapabilities()

        # RFC 4642 2.2.2: Both the client and the server MUST know ikiwa there is
        # a TLS session active.  A client MUST NOT attempt to start a TLS
        # session ikiwa a TLS session is already active.
        self.tls_on = False

        # Log in and encryption setup order is left to subclasses.
        self.authenticated = False

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *args):
        is_connected = lambda: hasattr(self, "file")
        ikiwa is_connected():
            try:
                self.quit()
            except (OSError, EOFError):
                pass
            finally:
                ikiwa is_connected():
                    self._close()

    eleza getwelcome(self):
        """Get the welcome message kutoka the server
        (this is read and squirreled away by __init__()).
        If the response code is 200, posting is allowed;
        ikiwa it 201, posting is not allowed."""

        ikiwa self.debugging: andika('*welcome*', repr(self.welcome))
        rudisha self.welcome

    eleza getcapabilities(self):
        """Get the server capabilities, as read by __init__().
        If the CAPABILITIES command is not supported, an empty dict is
        returned."""
        ikiwa self._caps is None:
            self.nntp_version = 1
            self.nntp_implementation = None
            try:
                resp, caps = self.capabilities()
            except (NNTPPermanentError, NNTPTemporaryError):
                # Server doesn't support capabilities
                self._caps = {}
            else:
                self._caps = caps
                ikiwa 'VERSION' in caps:
                    # The server can advertise several supported versions,
                    # choose the highest.
                    self.nntp_version = max(map(int, caps['VERSION']))
                ikiwa 'IMPLEMENTATION' in caps:
                    self.nntp_implementation = ' '.join(caps['IMPLEMENTATION'])
        rudisha self._caps

    eleza set_debuglevel(self, level):
        """Set the debugging level.  Argument 'level' means:
        0: no debugging output (default)
        1: print commands and responses but not body text etc.
        2: also print raw lines read and sent before stripping CR/LF"""

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

    eleza _getline(self, strip_crlf=True):
        """Internal: rudisha one line kutoka the server, stripping _CRLF.
        Raise EOFError ikiwa the connection is closed.
        Returns a bytes object."""
        line = self.file.readline(_MAXLINE +1)
        ikiwa len(line) > _MAXLINE:
            raise NNTPDataError('line too long')
        ikiwa self.debugging > 1:
            andika('*get*', repr(line))
        ikiwa not line: raise EOFError
        ikiwa strip_crlf:
            ikiwa line[-2:] == _CRLF:
                line = line[:-2]
            elikiwa line[-1:] in _CRLF:
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
            raise NNTPTemporaryError(resp)
        ikiwa c == '5':
            raise NNTPPermanentError(resp)
        ikiwa c not in '123':
            raise NNTPProtocolError(resp)
        rudisha resp

    eleza _getlongresp(self, file=None):
        """Internal: get a response plus following text kutoka the server.
        Raise various errors ikiwa the response indicates an error.

        Returns a (response, lines) tuple where `response` is a unicode
        string and `lines` is a list of bytes objects.
        If `file` is a file-like object, it must be open in binary mode.
        """

        openedFile = None
        try:
            # If a string was passed then open a file with that name
            ikiwa isinstance(file, (str, bytes)):
                openedFile = file = open(file, "wb")

            resp = self._getresp()
            ikiwa resp[:3] not in _LONGRESP:
                raise NNTPReplyError(resp)

            lines = []
            ikiwa file is not None:
                # XXX lines = None instead?
                terminators = (b'.' + _CRLF, b'.\n')
                while 1:
                    line = self._getline(False)
                    ikiwa line in terminators:
                        break
                    ikiwa line.startswith(b'..'):
                        line = line[1:]
                    file.write(line)
            else:
                terminator = b'.'
                while 1:
                    line = self._getline()
                    ikiwa line == terminator:
                        break
                    ikiwa line.startswith(b'..'):
                        line = line[1:]
                    lines.append(line)
        finally:
            # If this method created the file, then it must close it
            ikiwa openedFile:
                openedFile.close()

        rudisha resp, lines

    eleza _shortcmd(self, line):
        """Internal: send a command and get the response.
        Same rudisha value as _getresp()."""
        self._putcmd(line)
        rudisha self._getresp()

    eleza _longcmd(self, line, file=None):
        """Internal: send a command and get the response plus following text.
        Same rudisha value as _getlongresp()."""
        self._putcmd(line)
        rudisha self._getlongresp(file)

    eleza _longcmdstring(self, line, file=None):
        """Internal: send a command and get the response plus following text.
        Same as _longcmd() and _getlongresp(), except that the returned `lines`
        are unicode strings rather than bytes objects.
        """
        self._putcmd(line)
        resp, list = self._getlongresp(file)
        rudisha resp, [line.decode(self.encoding, self.errors)
                      for line in list]

    eleza _getoverviewfmt(self):
        """Internal: get the overview format. Queries the server ikiwa not
        already done, else returns the cached value."""
        try:
            rudisha self._cachedoverviewfmt
        except AttributeError:
            pass
        try:
            resp, lines = self._longcmdstring("LIST OVERVIEW.FMT")
        except NNTPPermanentError:
            # Not supported by server?
            fmt = _DEFAULT_OVERVIEW_FMT[:]
        else:
            fmt = _parse_overview_fmt(lines)
        self._cachedoverviewfmt = fmt
        rudisha fmt

    eleza _grouplist(self, lines):
        # Parse lines into "group last first flag"
        rudisha [GroupInfo(*line.split()) for line in lines]

    eleza capabilities(self):
        """Process a CAPABILITIES command.  Not supported by all servers.
        Return:
        - resp: server response ikiwa successful
        - caps: a dictionary mapping capability names to lists of tokens
        (for example {'VERSION': ['2'], 'OVER': [], LIST: ['ACTIVE', 'HEADERS'] })
        """
        caps = {}
        resp, lines = self._longcmdstring("CAPABILITIES")
        for line in lines:
            name, *tokens = line.split()
            caps[name] = tokens
        rudisha resp, caps

    eleza newgroups(self, date, *, file=None):
        """Process a NEWGROUPS command.  Arguments:
        - date: a date or datetime object
        Return:
        - resp: server response ikiwa successful
        - list: list of newsgroup names
        """
        ikiwa not isinstance(date, (datetime.date, datetime.date)):
            raise TypeError(
                "the date parameter must be a date or datetime object, "
                "not '{:40}'".format(date.__class__.__name__))
        date_str, time_str = _unparse_datetime(date, self.nntp_version < 2)
        cmd = 'NEWGROUPS {0} {1}'.format(date_str, time_str)
        resp, lines = self._longcmdstring(cmd, file)
        rudisha resp, self._grouplist(lines)

    eleza newnews(self, group, date, *, file=None):
        """Process a NEWNEWS command.  Arguments:
        - group: group name or '*'
        - date: a date or datetime object
        Return:
        - resp: server response ikiwa successful
        - list: list of message ids
        """
        ikiwa not isinstance(date, (datetime.date, datetime.date)):
            raise TypeError(
                "the date parameter must be a date or datetime object, "
                "not '{:40}'".format(date.__class__.__name__))
        date_str, time_str = _unparse_datetime(date, self.nntp_version < 2)
        cmd = 'NEWNEWS {0} {1} {2}'.format(group, date_str, time_str)
        rudisha self._longcmdstring(cmd, file)

    eleza list(self, group_pattern=None, *, file=None):
        """Process a LIST or LIST ACTIVE command. Arguments:
        - group_pattern: a pattern indicating which groups to query
        - file: Filename string or file object to store the result in
        Returns:
        - resp: server response ikiwa successful
        - list: list of (group, last, first, flag) (strings)
        """
        ikiwa group_pattern is not None:
            command = 'LIST ACTIVE ' + group_pattern
        else:
            command = 'LIST'
        resp, lines = self._longcmdstring(command, file)
        rudisha resp, self._grouplist(lines)

    eleza _getdescriptions(self, group_pattern, return_all):
        line_pat = re.compile('^(?P<group>[^ \t]+)[ \t]+(.*)$')
        # Try the more std (acc. to RFC2980) LIST NEWSGROUPS first
        resp, lines = self._longcmdstring('LIST NEWSGROUPS ' + group_pattern)
        ikiwa not resp.startswith('215'):
            # Now the deprecated XGTITLE.  This either raises an error
            # or succeeds with the same output structure as LIST
            # NEWSGROUPS.
            resp, lines = self._longcmdstring('XGTITLE ' + group_pattern)
        groups = {}
        for raw_line in lines:
            match = line_pat.search(raw_line.strip())
            ikiwa match:
                name, desc = match.group(1, 2)
                ikiwa not return_all:
                    rudisha desc
                groups[name] = desc
        ikiwa return_all:
            rudisha resp, groups
        else:
            # Nothing found
            rudisha ''

    eleza description(self, group):
        """Get a description for a single group.  If more than one
        group matches ('group' is a pattern), rudisha the first.  If no
        group matches, rudisha an empty string.

        This elides the response code kutoka the server, since it can
        only be '215' or '285' (for xgtitle) anyway.  If the response
        code is needed, use the 'descriptions' method.

        NOTE: This neither checks for a wildcard in 'group' nor does
        it check whether the group actually exists."""
        rudisha self._getdescriptions(group, False)

    eleza descriptions(self, group_pattern):
        """Get descriptions for a range of groups."""
        rudisha self._getdescriptions(group_pattern, True)

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
        ikiwa not resp.startswith('211'):
            raise NNTPReplyError(resp)
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

    eleza help(self, *, file=None):
        """Process a HELP command. Argument:
        - file: Filename string or file object to store the result in
        Returns:
        - resp: server response ikiwa successful
        - list: list of strings returned by the server in response to the
                HELP command
        """
        rudisha self._longcmdstring('HELP', file)

    eleza _statparse(self, resp):
        """Internal: parse the response line of a STAT, NEXT, LAST,
        ARTICLE, HEAD or BODY command."""
        ikiwa not resp.startswith('22'):
            raise NNTPReplyError(resp)
        words = resp.split()
        art_num = int(words[1])
        message_id = words[2]
        rudisha resp, art_num, message_id

    eleza _statcmd(self, line):
        """Internal: process a STAT, NEXT or LAST command."""
        resp = self._shortcmd(line)
        rudisha self._statparse(resp)

    eleza stat(self, message_spec=None):
        """Process a STAT command.  Argument:
        - message_spec: article number or message id (ikiwa not specified,
          the current article is selected)
        Returns:
        - resp: server response ikiwa successful
        - art_num: the article number
        - message_id: the message id
        """
        ikiwa message_spec:
            rudisha self._statcmd('STAT {0}'.format(message_spec))
        else:
            rudisha self._statcmd('STAT')

    eleza next(self):
        """Process a NEXT command.  No arguments.  Return as for STAT."""
        rudisha self._statcmd('NEXT')

    eleza last(self):
        """Process a LAST command.  No arguments.  Return as for STAT."""
        rudisha self._statcmd('LAST')

    eleza _artcmd(self, line, file=None):
        """Internal: process a HEAD, BODY or ARTICLE command."""
        resp, lines = self._longcmd(line, file)
        resp, art_num, message_id = self._statparse(resp)
        rudisha resp, ArticleInfo(art_num, message_id, lines)

    eleza head(self, message_spec=None, *, file=None):
        """Process a HEAD command.  Argument:
        - message_spec: article number or message id
        - file: filename string or file object to store the headers in
        Returns:
        - resp: server response ikiwa successful
        - ArticleInfo: (article number, message id, list of header lines)
        """
        ikiwa message_spec is not None:
            cmd = 'HEAD {0}'.format(message_spec)
        else:
            cmd = 'HEAD'
        rudisha self._artcmd(cmd, file)

    eleza body(self, message_spec=None, *, file=None):
        """Process a BODY command.  Argument:
        - message_spec: article number or message id
        - file: filename string or file object to store the body in
        Returns:
        - resp: server response ikiwa successful
        - ArticleInfo: (article number, message id, list of body lines)
        """
        ikiwa message_spec is not None:
            cmd = 'BODY {0}'.format(message_spec)
        else:
            cmd = 'BODY'
        rudisha self._artcmd(cmd, file)

    eleza article(self, message_spec=None, *, file=None):
        """Process an ARTICLE command.  Argument:
        - message_spec: article number or message id
        - file: filename string or file object to store the article in
        Returns:
        - resp: server response ikiwa successful
        - ArticleInfo: (article number, message id, list of article lines)
        """
        ikiwa message_spec is not None:
            cmd = 'ARTICLE {0}'.format(message_spec)
        else:
            cmd = 'ARTICLE'
        rudisha self._artcmd(cmd, file)

    eleza slave(self):
        """Process a SLAVE command.  Returns:
        - resp: server response ikiwa successful
        """
        rudisha self._shortcmd('SLAVE')

    eleza xhdr(self, hdr, str, *, file=None):
        """Process an XHDR command (optional server extension).  Arguments:
        - hdr: the header type (e.g. 'subject')
        - str: an article nr, a message id, or a range nr1-nr2
        - file: Filename string or file object to store the result in
        Returns:
        - resp: server response ikiwa successful
        - list: list of (nr, value) strings
        """
        pat = re.compile('^([0-9]+) ?(.*)\n?')
        resp, lines = self._longcmdstring('XHDR {0} {1}'.format(hdr, str), file)
        eleza remove_number(line):
            m = pat.match(line)
            rudisha m.group(1, 2) ikiwa m else line
        rudisha resp, [remove_number(line) for line in lines]

    eleza xover(self, start, end, *, file=None):
        """Process an XOVER command (optional server extension) Arguments:
        - start: start of range
        - end: end of range
        - file: Filename string or file object to store the result in
        Returns:
        - resp: server response ikiwa successful
        - list: list of dicts containing the response fields
        """
        resp, lines = self._longcmdstring('XOVER {0}-{1}'.format(start, end),
                                          file)
        fmt = self._getoverviewfmt()
        rudisha resp, _parse_overview(lines, fmt)

    eleza over(self, message_spec, *, file=None):
        """Process an OVER command.  If the command isn't supported, fall
        back to XOVER. Arguments:
        - message_spec:
            - either a message id, indicating the article to fetch
              information about
            - or a (start, end) tuple, indicating a range of article numbers;
              ikiwa end is None, information up to the newest message will be
              retrieved
            - or None, indicating the current article number must be used
        - file: Filename string or file object to store the result in
        Returns:
        - resp: server response ikiwa successful
        - list: list of dicts containing the response fields

        NOTE: the "message id" form isn't supported by XOVER
        """
        cmd = 'OVER' ikiwa 'OVER' in self._caps else 'XOVER'
        ikiwa isinstance(message_spec, (tuple, list)):
            start, end = message_spec
            cmd += ' {0}-{1}'.format(start, end or '')
        elikiwa message_spec is not None:
            cmd = cmd + ' ' + message_spec
        resp, lines = self._longcmdstring(cmd, file)
        fmt = self._getoverviewfmt()
        rudisha resp, _parse_overview(lines, fmt)

    eleza xgtitle(self, group, *, file=None):
        """Process an XGTITLE command (optional server extension) Arguments:
        - group: group name wildcard (i.e. news.*)
        Returns:
        - resp: server response ikiwa successful
        - list: list of (name,title) strings"""
        warnings.warn("The XGTITLE extension is not actively used, "
                      "use descriptions() instead",
                      DeprecationWarning, 2)
        line_pat = re.compile('^([^ \t]+)[ \t]+(.*)$')
        resp, raw_lines = self._longcmdstring('XGTITLE ' + group, file)
        lines = []
        for raw_line in raw_lines:
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
        warnings.warn("The XPATH extension is not actively used",
                      DeprecationWarning, 2)

        resp = self._shortcmd('XPATH {0}'.format(id))
        ikiwa not resp.startswith('223'):
            raise NNTPReplyError(resp)
        try:
            [resp_num, path] = resp.split()
        except ValueError:
            raise NNTPReplyError(resp) kutoka None
        else:
            rudisha resp, path

    eleza date(self):
        """Process the DATE command.
        Returns:
        - resp: server response ikiwa successful
        - date: datetime object
        """
        resp = self._shortcmd("DATE")
        ikiwa not resp.startswith('111'):
            raise NNTPReplyError(resp)
        elem = resp.split()
        ikiwa len(elem) != 2:
            raise NNTPDataError(resp)
        date = elem[1]
        ikiwa len(date) != 14:
            raise NNTPDataError(resp)
        rudisha resp, _parse_datetime(date, None)

    eleza _post(self, command, f):
        resp = self._shortcmd(command)
        # Raises a specific exception ikiwa posting is not allowed
        ikiwa not resp.startswith('3'):
            raise NNTPReplyError(resp)
        ikiwa isinstance(f, (bytes, bytearray)):
            f = f.splitlines()
        # We don't use _putline() because:
        # - we don't want additional CRLF ikiwa the file or iterable is already
        #   in the right format
        # - we don't want a spurious flush() after each line is written
        for line in f:
            ikiwa not line.endswith(_CRLF):
                line = line.rstrip(b"\r\n") + _CRLF
            ikiwa line.startswith(b'.'):
                line = b'.' + line
            self.file.write(line)
        self.file.write(b".\r\n")
        self.file.flush()
        rudisha self._getresp()

    eleza post(self, data):
        """Process a POST command.  Arguments:
        - data: bytes object, iterable or file containing the article
        Returns:
        - resp: server response ikiwa successful"""
        rudisha self._post('POST', data)

    eleza ihave(self, message_id, data):
        """Process an IHAVE command.  Arguments:
        - message_id: message-id of the article
        - data: file containing the article
        Returns:
        - resp: server response ikiwa successful
        Note that ikiwa the server refuses the article an exception is raised."""
        rudisha self._post('IHAVE {0}'.format(message_id), data)

    eleza _close(self):
        self.file.close()
        del self.file

    eleza quit(self):
        """Process a QUIT command and close the socket.  Returns:
        - resp: server response ikiwa successful"""
        try:
            resp = self._shortcmd('QUIT')
        finally:
            self._close()
        rudisha resp

    eleza login(self, user=None, password=None, usenetrc=True):
        ikiwa self.authenticated:
            raise ValueError("Already logged in.")
        ikiwa not user and not usenetrc:
            raise ValueError(
                "At least one of `user` and `usenetrc` must be specified")
        # If no login/password was specified but netrc was requested,
        # try to get them kutoka ~/.netrc
        # Presume that ikiwa .netrc has an entry, NNRP authentication is required.
        try:
            ikiwa usenetrc and not user:
                agiza netrc
                credentials = netrc.netrc()
                auth = credentials.authenticators(self.host)
                ikiwa auth:
                    user = auth[0]
                    password = auth[2]
        except OSError:
            pass
        # Perform NNTP authentication ikiwa needed.
        ikiwa not user:
            return
        resp = self._shortcmd('authinfo user ' + user)
        ikiwa resp.startswith('381'):
            ikiwa not password:
                raise NNTPReplyError(resp)
            else:
                resp = self._shortcmd('authinfo pass ' + password)
                ikiwa not resp.startswith('281'):
                    raise NNTPPermanentError(resp)
        # Capabilities might have changed after login
        self._caps = None
        self.getcapabilities()
        # Attempt to send mode reader ikiwa it was requested after login.
        # Only do so ikiwa we're not in reader mode already.
        ikiwa self.readermode_afterauth and 'READER' not in self._caps:
            self._setreadermode()
            # Capabilities might have changed after MODE READER
            self._caps = None
            self.getcapabilities()

    eleza _setreadermode(self):
        try:
            self.welcome = self._shortcmd('mode reader')
        except NNTPPermanentError:
            # Error 5xx, probably 'not implemented'
            pass
        except NNTPTemporaryError as e:
            ikiwa e.response.startswith('480'):
                # Need authorization before 'mode reader'
                self.readermode_afterauth = True
            else:
                raise

    ikiwa _have_ssl:
        eleza starttls(self, context=None):
            """Process a STARTTLS command. Arguments:
            - context: SSL context to use for the encrypted connection
            """
            # Per RFC 4642, STARTTLS MUST NOT be sent after authentication or if
            # a TLS session already exists.
            ikiwa self.tls_on:
                raise ValueError("TLS is already enabled.")
            ikiwa self.authenticated:
                raise ValueError("TLS cannot be started after authentication.")
            resp = self._shortcmd('STARTTLS')
            ikiwa resp.startswith('382'):
                self.file.close()
                self.sock = _encrypt_on(self.sock, context, self.host)
                self.file = self.sock.makefile("rwb")
                self.tls_on = True
                # Capabilities may change after TLS starts up, so ask for them
                # again.
                self._caps = None
                self.getcapabilities()
            else:
                raise NNTPError("TLS failed to start.")


kundi NNTP(_NNTPBase):

    eleza __init__(self, host, port=NNTP_PORT, user=None, password=None,
                 readermode=None, usenetrc=False,
                 timeout=_GLOBAL_DEFAULT_TIMEOUT):
        """Initialize an instance.  Arguments:
        - host: hostname to connect to
        - port: port to connect to (default the standard NNTP port)
        - user: username to authenticate with
        - password: password to use with username
        - readermode: ikiwa true, send 'mode reader' command after
                      connecting.
        - usenetrc: allow loading username and password kutoka ~/.netrc file
                    ikiwa not specified explicitly
        - timeout: timeout (in seconds) used for socket connections

        readermode is sometimes necessary ikiwa you are connecting to an
        NNTP server on the local machine and intend to call
        reader-specific commands, such as `group'.  If you get
        unexpected NNTPPermanentErrors, you might need to set
        readermode.
        """
        self.host = host
        self.port = port
        sys.audit("nntplib.connect", self, host, port)
        self.sock = socket.create_connection((host, port), timeout)
        file = None
        try:
            file = self.sock.makefile("rwb")
            _NNTPBase.__init__(self, file, host,
                               readermode, timeout)
            ikiwa user or usenetrc:
                self.login(user, password, usenetrc)
        except:
            ikiwa file:
                file.close()
            self.sock.close()
            raise

    eleza _close(self):
        try:
            _NNTPBase._close(self)
        finally:
            self.sock.close()


ikiwa _have_ssl:
    kundi NNTP_SSL(_NNTPBase):

        eleza __init__(self, host, port=NNTP_SSL_PORT,
                    user=None, password=None, ssl_context=None,
                    readermode=None, usenetrc=False,
                    timeout=_GLOBAL_DEFAULT_TIMEOUT):
            """This works identically to NNTP.__init__, except for the change
            in default port and the `ssl_context` argument for SSL connections.
            """
            sys.audit("nntplib.connect", self, host, port)
            self.sock = socket.create_connection((host, port), timeout)
            file = None
            try:
                self.sock = _encrypt_on(self.sock, ssl_context, host)
                file = self.sock.makefile("rwb")
                _NNTPBase.__init__(self, file, host,
                                   readermode=readermode, timeout=timeout)
                ikiwa user or usenetrc:
                    self.login(user, password, usenetrc)
            except:
                ikiwa file:
                    file.close()
                self.sock.close()
                raise

        eleza _close(self):
            try:
                _NNTPBase._close(self)
            finally:
                self.sock.close()

    __all__.append("NNTP_SSL")


# Test retrieval when run as a script.
ikiwa __name__ == '__main__':
    agiza argparse

    parser = argparse.ArgumentParser(description="""\
        nntplib built-in demo - display the latest articles in a newsgroup""")
    parser.add_argument('-g', '--group', default='gmane.comp.python.general',
                        help='group to fetch messages kutoka (default: %(default)s)')
    parser.add_argument('-s', '--server', default='news.gmane.org',
                        help='NNTP server hostname (default: %(default)s)')
    parser.add_argument('-p', '--port', default=-1, type=int,
                        help='NNTP port number (default: %s / %s)' % (NNTP_PORT, NNTP_SSL_PORT))
    parser.add_argument('-n', '--nb-articles', default=10, type=int,
                        help='number of articles to fetch (default: %(default)s)')
    parser.add_argument('-S', '--ssl', action='store_true', default=False,
                        help='use NNTP over SSL')
    args = parser.parse_args()

    port = args.port
    ikiwa not args.ssl:
        ikiwa port == -1:
            port = NNTP_PORT
        s = NNTP(host=args.server, port=port)
    else:
        ikiwa port == -1:
            port = NNTP_SSL_PORT
        s = NNTP_SSL(host=args.server, port=port)

    caps = s.getcapabilities()
    ikiwa 'STARTTLS' in caps:
        s.starttls()
    resp, count, first, last, name = s.group(args.group)
    andika('Group', name, 'has', count, 'articles, range', first, 'to', last)

    eleza cut(s, lim):
        ikiwa len(s) > lim:
            s = s[:lim - 4] + "..."
        rudisha s

    first = str(int(last) - args.nb_articles + 1)
    resp, overviews = s.xover(first, last)
    for artnum, over in overviews:
        author = decode_header(over['kutoka']).split('<', 1)[0]
        subject = decode_header(over['subject'])
        lines = int(over[':lines'])
        andika("{:7} {:20} {:42} ({})".format(
              artnum, cut(author, 20), cut(subject, 42), lines)
              )

    s.quit()
