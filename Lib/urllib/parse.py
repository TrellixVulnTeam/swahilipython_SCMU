"""Parse (absolute na relative) URLs.

urlparse module ni based upon the following RFC specifications.

RFC 3986 (STD66): "Uniform Resource Identifiers" by T. Berners-Lee, R. Fielding
and L.  Masinter, January 2005.

RFC 2732 : "Format kila Literal IPv6 Addresses kwenye URL's by R.Hinden, B.Carpenter
and L.Masinter, December 1999.

RFC 2396:  "Uniform Resource Identifiers (URI)": Generic Syntax by T.
Berners-Lee, R. Fielding, na L. Masinter, August 1998.

RFC 2368: "The mailto URL scheme", by P.Hoffman , L Masinter, J. Zawinski, July 1998.

RFC 1808: "Relative Uniform Resource Locators", by R. Fielding, UC Irvine, June
1995.

RFC 1738: "Uniform Resource Locators (URL)" by T. Berners-Lee, L. Masinter, M.
McCahill, December 1994

RFC 3986 ni considered the current standard na any future changes to
urlparse module should conform ukijumuisha it.  The urlparse module is
currently sio entirely compliant ukijumuisha this RFC due to defacto
scenarios kila parsing, na kila backward compatibility purposes, some
parsing quirks kutoka older RFCs are retained. The testcases in
test_urlparse.py provides a good indicator of parsing behavior.
"""

agiza re
agiza sys
agiza collections
agiza warnings

__all__ = ["urlparse", "urlunparse", "urljoin", "urldefrag",
           "urlsplit", "urlunsplit", "urlencode", "parse_qs",
           "parse_qsl", "quote", "quote_plus", "quote_from_bytes",
           "unquote", "unquote_plus", "unquote_to_bytes",
           "DefragResult", "ParseResult", "SplitResult",
           "DefragResultBytes", "ParseResultBytes", "SplitResultBytes"]

# A classification of schemes.
# The empty string classifies URLs ukijumuisha no scheme specified,
# being the default value returned by “urlsplit” na “urlparse”.

uses_relative = ['', 'ftp', 'http', 'gopher', 'nntp', 'imap',
                 'wais', 'file', 'https', 'shttp', 'mms',
                 'prospero', 'rtsp', 'rtspu', 'sftp',
                 'svn', 'svn+ssh', 'ws', 'wss']

uses_netloc = ['', 'ftp', 'http', 'gopher', 'nntp', 'telnet',
               'imap', 'wais', 'file', 'mms', 'https', 'shttp',
               'snews', 'prospero', 'rtsp', 'rtspu', 'rsync',
               'svn', 'svn+ssh', 'sftp', 'nfs', 'git', 'git+ssh',
               'ws', 'wss']

uses_params = ['', 'ftp', 'hdl', 'prospero', 'http', 'imap',
               'https', 'shttp', 'rtsp', 'rtspu', 'sip', 'sips',
               'mms', 'sftp', 'tel']

# These are sio actually used anymore, but should stay kila backwards
# compatibility.  (They are undocumented, but have a public-looking name.)

non_hierarchical = ['gopher', 'hdl', 'mailto', 'news',
                    'telnet', 'wais', 'imap', 'snews', 'sip', 'sips']

uses_query = ['', 'http', 'wais', 'imap', 'https', 'shttp', 'mms',
              'gopher', 'rtsp', 'rtspu', 'sip', 'sips']

uses_fragment = ['', 'ftp', 'hdl', 'http', 'gopher', 'news',
                 'nntp', 'wais', 'https', 'shttp', 'snews',
                 'file', 'prospero']

# Characters valid kwenye scheme names
scheme_chars = ('abcdefghijklmnopqrstuvwxyz'
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                '0123456789'
                '+-.')

# XXX: Consider replacing ukijumuisha functools.lru_cache
MAX_CACHE_SIZE = 20
_parse_cache = {}

eleza clear_cache():
    """Clear the parse cache na the quoters cache."""
    _parse_cache.clear()
    _safe_quoters.clear()


# Helpers kila bytes handling
# For 3.2, we deliberately require applications that
# handle improperly quoted URLs to do their own
# decoding na encoding. If valid use cases are
# presented, we may relax this by using latin-1
# decoding internally kila 3.3
_implicit_encoding = 'ascii'
_implicit_errors = 'strict'

eleza _noop(obj):
    rudisha obj

eleza _encode_result(obj, encoding=_implicit_encoding,
                        errors=_implicit_errors):
    rudisha obj.encode(encoding, errors)

eleza _decode_args(args, encoding=_implicit_encoding,
                       errors=_implicit_errors):
    rudisha tuple(x.decode(encoding, errors) ikiwa x isipokua '' kila x kwenye args)

eleza _coerce_args(*args):
    # Invokes decode ikiwa necessary to create str args
    # na returns the coerced inputs along with
    # an appropriate result coercion function
    #   - noop kila str inputs
    #   - encoding function otherwise
    str_input = isinstance(args[0], str)
    kila arg kwenye args[1:]:
        # We special-case the empty string to support the
        # "scheme=''" default argument to some functions
        ikiwa arg na isinstance(arg, str) != str_input:
            ashiria TypeError("Cannot mix str na non-str arguments")
    ikiwa str_input:
        rudisha args + (_noop,)
    rudisha _decode_args(args) + (_encode_result,)

# Result objects are more helpful than simple tuples
kundi _ResultMixinStr(object):
    """Standard approach to encoding parsed results kutoka str to bytes"""
    __slots__ = ()

    eleza encode(self, encoding='ascii', errors='strict'):
        rudisha self._encoded_counterpart(*(x.encode(encoding, errors) kila x kwenye self))


kundi _ResultMixinBytes(object):
    """Standard approach to decoding parsed results kutoka bytes to str"""
    __slots__ = ()

    eleza decode(self, encoding='ascii', errors='strict'):
        rudisha self._decoded_counterpart(*(x.decode(encoding, errors) kila x kwenye self))


kundi _NetlocResultMixinBase(object):
    """Shared methods kila the parsed result objects containing a netloc element"""
    __slots__ = ()

    @property
    eleza username(self):
        rudisha self._userinfo[0]

    @property
    eleza pitaword(self):
        rudisha self._userinfo[1]

    @property
    eleza hostname(self):
        hostname = self._hostinfo[0]
        ikiwa sio hostname:
            rudisha Tupu
        # Scoped IPv6 address may have zone info, which must sio be lowercased
        # like http://[fe80::822a:a8ff:fe49:470c%tESt]:1234/keys
        separator = '%' ikiwa isinstance(hostname, str) isipokua b'%'
        hostname, percent, zone = hostname.partition(separator)
        rudisha hostname.lower() + percent + zone

    @property
    eleza port(self):
        port = self._hostinfo[1]
        ikiwa port ni sio Tupu:
            jaribu:
                port = int(port, 10)
            tatizo ValueError:
                message = f'Port could sio be cast to integer value kama {port!r}'
                ashiria ValueError(message) kutoka Tupu
            ikiwa sio ( 0 <= port <= 65535):
                ashiria ValueError("Port out of range 0-65535")
        rudisha port


kundi _NetlocResultMixinStr(_NetlocResultMixinBase, _ResultMixinStr):
    __slots__ = ()

    @property
    eleza _userinfo(self):
        netloc = self.netloc
        userinfo, have_info, hostinfo = netloc.rpartition('@')
        ikiwa have_info:
            username, have_pitaword, pitaword = userinfo.partition(':')
            ikiwa sio have_pitaword:
                pitaword = Tupu
        isipokua:
            username = pitaword = Tupu
        rudisha username, pitaword

    @property
    eleza _hostinfo(self):
        netloc = self.netloc
        _, _, hostinfo = netloc.rpartition('@')
        _, have_open_br, bracketed = hostinfo.partition('[')
        ikiwa have_open_br:
            hostname, _, port = bracketed.partition(']')
            _, _, port = port.partition(':')
        isipokua:
            hostname, _, port = hostinfo.partition(':')
        ikiwa sio port:
            port = Tupu
        rudisha hostname, port


kundi _NetlocResultMixinBytes(_NetlocResultMixinBase, _ResultMixinBytes):
    __slots__ = ()

    @property
    eleza _userinfo(self):
        netloc = self.netloc
        userinfo, have_info, hostinfo = netloc.rpartition(b'@')
        ikiwa have_info:
            username, have_pitaword, pitaword = userinfo.partition(b':')
            ikiwa sio have_pitaword:
                pitaword = Tupu
        isipokua:
            username = pitaword = Tupu
        rudisha username, pitaword

    @property
    eleza _hostinfo(self):
        netloc = self.netloc
        _, _, hostinfo = netloc.rpartition(b'@')
        _, have_open_br, bracketed = hostinfo.partition(b'[')
        ikiwa have_open_br:
            hostname, _, port = bracketed.partition(b']')
            _, _, port = port.partition(b':')
        isipokua:
            hostname, _, port = hostinfo.partition(b':')
        ikiwa sio port:
            port = Tupu
        rudisha hostname, port


kutoka collections agiza namedtuple

_DefragResultBase = namedtuple('DefragResult', 'url fragment')
_SplitResultBase = namedtuple(
    'SplitResult', 'scheme netloc path query fragment')
_ParseResultBase = namedtuple(
    'ParseResult', 'scheme netloc path params query fragment')

_DefragResultBase.__doc__ = """
DefragResult(url, fragment)

A 2-tuple that contains the url without fragment identifier na the fragment
identifier kama a separate argument.
"""

_DefragResultBase.url.__doc__ = """The URL ukijumuisha no fragment identifier."""

_DefragResultBase.fragment.__doc__ = """
Fragment identifier separated kutoka URL, that allows indirect identification of a
secondary resource by reference to a primary resource na additional identifying
information.
"""

_SplitResultBase.__doc__ = """
SplitResult(scheme, netloc, path, query, fragment)

A 5-tuple that contains the different components of a URL. Similar to
ParseResult, but does sio split params.
"""

_SplitResultBase.scheme.__doc__ = """Specifies URL scheme kila the request."""

_SplitResultBase.netloc.__doc__ = """
Network location where the request ni made to.
"""

_SplitResultBase.path.__doc__ = """
The hierarchical path, such kama the path to a file to download.
"""

_SplitResultBase.query.__doc__ = """
The query component, that contains non-hierarchical data, that along ukijumuisha data
in path component, identifies a resource kwenye the scope of URI's scheme na
network location.
"""

_SplitResultBase.fragment.__doc__ = """
Fragment identifier, that allows indirect identification of a secondary resource
by reference to a primary resource na additional identifying information.
"""

_ParseResultBase.__doc__ = """
ParseResult(scheme, netloc, path, params, query, fragment)

A 6-tuple that contains components of a parsed URL.
"""

_ParseResultBase.scheme.__doc__ = _SplitResultBase.scheme.__doc__
_ParseResultBase.netloc.__doc__ = _SplitResultBase.netloc.__doc__
_ParseResultBase.path.__doc__ = _SplitResultBase.path.__doc__
_ParseResultBase.params.__doc__ = """
Parameters kila last path element used to dereference the URI kwenye order to provide
access to perform some operation on the resource.
"""

_ParseResultBase.query.__doc__ = _SplitResultBase.query.__doc__
_ParseResultBase.fragment.__doc__ = _SplitResultBase.fragment.__doc__


# For backwards compatibility, alias _NetlocResultMixinStr
# ResultBase ni no longer part of the documented API, but it is
# retained since deprecating it isn't worth the hassle
ResultBase = _NetlocResultMixinStr

# Structured result objects kila string data
kundi DefragResult(_DefragResultBase, _ResultMixinStr):
    __slots__ = ()
    eleza geturl(self):
        ikiwa self.fragment:
            rudisha self.url + '#' + self.fragment
        isipokua:
            rudisha self.url

kundi SplitResult(_SplitResultBase, _NetlocResultMixinStr):
    __slots__ = ()
    eleza geturl(self):
        rudisha urlunsplit(self)

kundi ParseResult(_ParseResultBase, _NetlocResultMixinStr):
    __slots__ = ()
    eleza geturl(self):
        rudisha urlunparse(self)

# Structured result objects kila bytes data
kundi DefragResultBytes(_DefragResultBase, _ResultMixinBytes):
    __slots__ = ()
    eleza geturl(self):
        ikiwa self.fragment:
            rudisha self.url + b'#' + self.fragment
        isipokua:
            rudisha self.url

kundi SplitResultBytes(_SplitResultBase, _NetlocResultMixinBytes):
    __slots__ = ()
    eleza geturl(self):
        rudisha urlunsplit(self)

kundi ParseResultBytes(_ParseResultBase, _NetlocResultMixinBytes):
    __slots__ = ()
    eleza geturl(self):
        rudisha urlunparse(self)

# Set up the encode/decode result pairs
eleza _fix_result_transcoding():
    _result_pairs = (
        (DefragResult, DefragResultBytes),
        (SplitResult, SplitResultBytes),
        (ParseResult, ParseResultBytes),
    )
    kila _decoded, _encoded kwenye _result_pairs:
        _decoded._encoded_counterpart = _encoded
        _encoded._decoded_counterpart = _decoded

_fix_result_transcoding()
toa _fix_result_transcoding

eleza urlparse(url, scheme='', allow_fragments=Kweli):
    """Parse a URL into 6 components:
    <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    Return a 6-tuple: (scheme, netloc, path, params, query, fragment).
    Note that we don't koma the components up kwenye smaller bits
    (e.g. netloc ni a single string) na we don't expand % escapes."""
    url, scheme, _coerce_result = _coerce_args(url, scheme)
    splitresult = urlsplit(url, scheme, allow_fragments)
    scheme, netloc, url, query, fragment = splitresult
    ikiwa scheme kwenye uses_params na ';' kwenye url:
        url, params = _splitparams(url)
    isipokua:
        params = ''
    result = ParseResult(scheme, netloc, url, params, query, fragment)
    rudisha _coerce_result(result)

eleza _splitparams(url):
    ikiwa '/'  kwenye url:
        i = url.find(';', url.rfind('/'))
        ikiwa i < 0:
            rudisha url, ''
    isipokua:
        i = url.find(';')
    rudisha url[:i], url[i+1:]

eleza _splitnetloc(url, start=0):
    delim = len(url)   # position of end of domain part of url, default ni end
    kila c kwenye '/?#':    # look kila delimiters; the order ni NOT important
        wdelim = url.find(c, start)        # find first of this delim
        ikiwa wdelim >= 0:                    # ikiwa found
            delim = min(delim, wdelim)     # use earliest delim position
    rudisha url[start:delim], url[delim:]   # rudisha (domain, rest)

eleza _checknetloc(netloc):
    ikiwa sio netloc ama netloc.isascii():
        rudisha
    # looking kila characters like \u2100 that expand to 'a/c'
    # IDNA uses NFKC equivalence, so normalize kila this check
    agiza unicodedata
    n = netloc.replace('@', '')   # ignore characters already included
    n = n.replace(':', '')        # but sio the surrounding text
    n = n.replace('#', '')
    n = n.replace('?', '')
    netloc2 = unicodedata.normalize('NFKC', n)
    ikiwa n == netloc2:
        rudisha
    kila c kwenye '/?#@:':
        ikiwa c kwenye netloc2:
            ashiria ValueError("netloc '" + netloc + "' contains invalid " +
                             "characters under NFKC normalization")

eleza urlsplit(url, scheme='', allow_fragments=Kweli):
    """Parse a URL into 5 components:
    <scheme>://<netloc>/<path>?<query>#<fragment>
    Return a 5-tuple: (scheme, netloc, path, query, fragment).
    Note that we don't koma the components up kwenye smaller bits
    (e.g. netloc ni a single string) na we don't expand % escapes."""
    url, scheme, _coerce_result = _coerce_args(url, scheme)
    allow_fragments = bool(allow_fragments)
    key = url, scheme, allow_fragments, type(url), type(scheme)
    cached = _parse_cache.get(key, Tupu)
    ikiwa cached:
        rudisha _coerce_result(cached)
    ikiwa len(_parse_cache) >= MAX_CACHE_SIZE: # avoid runaway growth
        clear_cache()
    netloc = query = fragment = ''
    i = url.find(':')
    ikiwa i > 0:
        ikiwa url[:i] == 'http': # optimize the common case
            url = url[i+1:]
            ikiwa url[:2] == '//':
                netloc, url = _splitnetloc(url, 2)
                ikiwa (('[' kwenye netloc na ']' haiko kwenye netloc) ama
                        (']' kwenye netloc na '[' haiko kwenye netloc)):
                    ashiria ValueError("Invalid IPv6 URL")
            ikiwa allow_fragments na '#' kwenye url:
                url, fragment = url.split('#', 1)
            ikiwa '?' kwenye url:
                url, query = url.split('?', 1)
            _checknetloc(netloc)
            v = SplitResult('http', netloc, url, query, fragment)
            _parse_cache[key] = v
            rudisha _coerce_result(v)
        kila c kwenye url[:i]:
            ikiwa c haiko kwenye scheme_chars:
                koma
        isipokua:
            # make sure "url" ni sio actually a port number (in which case
            # "scheme" ni really part of the path)
            rest = url[i+1:]
            ikiwa sio rest ama any(c haiko kwenye '0123456789' kila c kwenye rest):
                # sio a port number
                scheme, url = url[:i].lower(), rest

    ikiwa url[:2] == '//':
        netloc, url = _splitnetloc(url, 2)
        ikiwa (('[' kwenye netloc na ']' haiko kwenye netloc) ama
                (']' kwenye netloc na '[' haiko kwenye netloc)):
            ashiria ValueError("Invalid IPv6 URL")
    ikiwa allow_fragments na '#' kwenye url:
        url, fragment = url.split('#', 1)
    ikiwa '?' kwenye url:
        url, query = url.split('?', 1)
    _checknetloc(netloc)
    v = SplitResult(scheme, netloc, url, query, fragment)
    _parse_cache[key] = v
    rudisha _coerce_result(v)

eleza urlunparse(components):
    """Put a parsed URL back together again.  This may result kwenye a
    slightly different, but equivalent URL, ikiwa the URL that was parsed
    originally had redundant delimiters, e.g. a ? ukijumuisha an empty query
    (the draft states that these are equivalent)."""
    scheme, netloc, url, params, query, fragment, _coerce_result = (
                                                  _coerce_args(*components))
    ikiwa params:
        url = "%s;%s" % (url, params)
    rudisha _coerce_result(urlunsplit((scheme, netloc, url, query, fragment)))

eleza urlunsplit(components):
    """Combine the elements of a tuple kama returned by urlsplit() into a
    complete URL kama a string. The data argument can be any five-item iterable.
    This may result kwenye a slightly different, but equivalent URL, ikiwa the URL that
    was parsed originally had unnecessary delimiters (kila example, a ? ukijumuisha an
    empty query; the RFC states that these are equivalent)."""
    scheme, netloc, url, query, fragment, _coerce_result = (
                                          _coerce_args(*components))
    ikiwa netloc ama (scheme na scheme kwenye uses_netloc na url[:2] != '//'):
        ikiwa url na url[:1] != '/': url = '/' + url
        url = '//' + (netloc ama '') + url
    ikiwa scheme:
        url = scheme + ':' + url
    ikiwa query:
        url = url + '?' + query
    ikiwa fragment:
        url = url + '#' + fragment
    rudisha _coerce_result(url)

eleza urljoin(base, url, allow_fragments=Kweli):
    """Join a base URL na a possibly relative URL to form an absolute
    interpretation of the latter."""
    ikiwa sio base:
        rudisha url
    ikiwa sio url:
        rudisha base

    base, url, _coerce_result = _coerce_args(base, url)
    bscheme, bnetloc, bpath, bparams, bquery, bfragment = \
            urlparse(base, '', allow_fragments)
    scheme, netloc, path, params, query, fragment = \
            urlparse(url, bscheme, allow_fragments)

    ikiwa scheme != bscheme ama scheme haiko kwenye uses_relative:
        rudisha _coerce_result(url)
    ikiwa scheme kwenye uses_netloc:
        ikiwa netloc:
            rudisha _coerce_result(urlunparse((scheme, netloc, path,
                                              params, query, fragment)))
        netloc = bnetloc

    ikiwa sio path na sio params:
        path = bpath
        params = bparams
        ikiwa sio query:
            query = bquery
        rudisha _coerce_result(urlunparse((scheme, netloc, path,
                                          params, query, fragment)))

    base_parts = bpath.split('/')
    ikiwa base_parts[-1] != '':
        # the last item ni sio a directory, so will sio be taken into account
        # kwenye resolving the relative path
        toa base_parts[-1]

    # kila rfc3986, ignore all base path should the first character be root.
    ikiwa path[:1] == '/':
        segments = path.split('/')
    isipokua:
        segments = base_parts + path.split('/')
        # filter out elements that would cause redundant slashes on re-joining
        # the resolved_path
        segments[1:-1] = filter(Tupu, segments[1:-1])

    resolved_path = []

    kila seg kwenye segments:
        ikiwa seg == '..':
            jaribu:
                resolved_path.pop()
            tatizo IndexError:
                # ignore any .. segments that would otherwise cause an IndexError
                # when popped kutoka resolved_path ikiwa resolving kila rfc3986
                pita
        lasivyo seg == '.':
            endelea
        isipokua:
            resolved_path.append(seg)

    ikiwa segments[-1] kwenye ('.', '..'):
        # do some post-processing here. ikiwa the last segment was a relative dir,
        # then we need to append the trailing '/'
        resolved_path.append('')

    rudisha _coerce_result(urlunparse((scheme, netloc, '/'.join(
        resolved_path) ama '/', params, query, fragment)))


eleza urldefrag(url):
    """Removes any existing fragment kutoka URL.

    Returns a tuple of the defragmented URL na the fragment.  If
    the URL contained no fragments, the second element ni the
    empty string.
    """
    url, _coerce_result = _coerce_args(url)
    ikiwa '#' kwenye url:
        s, n, p, a, q, frag = urlparse(url)
        defrag = urlunparse((s, n, p, a, q, ''))
    isipokua:
        frag = ''
        defrag = url
    rudisha _coerce_result(DefragResult(defrag, frag))

_hexdig = '0123456789ABCDEFabcdef'
_hextobyte = Tupu

eleza unquote_to_bytes(string):
    """unquote_to_bytes('abc%20def') -> b'abc def'."""
    # Note: strings are encoded kama UTF-8. This ni only an issue ikiwa it contains
    # unescaped non-ASCII characters, which URIs should not.
    ikiwa sio string:
        # Is it a string-like object?
        string.split
        rudisha b''
    ikiwa isinstance(string, str):
        string = string.encode('utf-8')
    bits = string.split(b'%')
    ikiwa len(bits) == 1:
        rudisha string
    res = [bits[0]]
    append = res.append
    # Delay the initialization of the table to sio waste memory
    # ikiwa the function ni never called
    global _hextobyte
    ikiwa _hextobyte ni Tupu:
        _hextobyte = {(a + b).encode(): bytes.fromhex(a + b)
                      kila a kwenye _hexdig kila b kwenye _hexdig}
    kila item kwenye bits[1:]:
        jaribu:
            append(_hextobyte[item[:2]])
            append(item[2:])
        tatizo KeyError:
            append(b'%')
            append(item)
    rudisha b''.join(res)

_asciire = re.compile('([\x00-\x7f]+)')

eleza unquote(string, encoding='utf-8', errors='replace'):
    """Replace %xx escapes by their single-character equivalent. The optional
    encoding na errors parameters specify how to decode percent-encoded
    sequences into Unicode characters, kama accepted by the bytes.decode()
    method.
    By default, percent-encoded sequences are decoded ukijumuisha UTF-8, na invalid
    sequences are replaced by a placeholder character.

    unquote('abc%20def') -> 'abc def'.
    """
    ikiwa '%' haiko kwenye string:
        string.split
        rudisha string
    ikiwa encoding ni Tupu:
        encoding = 'utf-8'
    ikiwa errors ni Tupu:
        errors = 'replace'
    bits = _asciire.split(string)
    res = [bits[0]]
    append = res.append
    kila i kwenye range(1, len(bits), 2):
        append(unquote_to_bytes(bits[i]).decode(encoding, errors))
        append(bits[i + 1])
    rudisha ''.join(res)


eleza parse_qs(qs, keep_blank_values=Uongo, strict_parsing=Uongo,
             encoding='utf-8', errors='replace', max_num_fields=Tupu):
    """Parse a query given kama a string argument.

        Arguments:

        qs: percent-encoded query string to be parsed

        keep_blank_values: flag indicating whether blank values in
            percent-encoded queries should be treated kama blank strings.
            A true value indicates that blanks should be retained as
            blank strings.  The default false value indicates that
            blank values are to be ignored na treated kama ikiwa they were
            sio inluded.

        strict_parsing: flag indicating what to do ukijumuisha parsing errors.
            If false (the default), errors are silently ignored.
            If true, errors ashiria a ValueError exception.

        encoding na errors: specify how to decode percent-encoded sequences
            into Unicode characters, kama accepted by the bytes.decode() method.

        max_num_fields: int. If set, then throws a ValueError ikiwa there
            are more than n fields read by parse_qsl().

        Returns a dictionary.
    """
    parsed_result = {}
    pairs = parse_qsl(qs, keep_blank_values, strict_parsing,
                      encoding=encoding, errors=errors,
                      max_num_fields=max_num_fields)
    kila name, value kwenye pairs:
        ikiwa name kwenye parsed_result:
            parsed_result[name].append(value)
        isipokua:
            parsed_result[name] = [value]
    rudisha parsed_result


eleza parse_qsl(qs, keep_blank_values=Uongo, strict_parsing=Uongo,
              encoding='utf-8', errors='replace', max_num_fields=Tupu):
    """Parse a query given kama a string argument.

        Arguments:

        qs: percent-encoded query string to be parsed

        keep_blank_values: flag indicating whether blank values in
            percent-encoded queries should be treated kama blank strings.
            A true value indicates that blanks should be retained kama blank
            strings.  The default false value indicates that blank values
            are to be ignored na treated kama ikiwa they were  sio inluded.

        strict_parsing: flag indicating what to do ukijumuisha parsing errors. If
            false (the default), errors are silently ignored. If true,
            errors ashiria a ValueError exception.

        encoding na errors: specify how to decode percent-encoded sequences
            into Unicode characters, kama accepted by the bytes.decode() method.

        max_num_fields: int. If set, then throws a ValueError
            ikiwa there are more than n fields read by parse_qsl().

        Returns a list, kama G-d intended.
    """
    qs, _coerce_result = _coerce_args(qs)

    # If max_num_fields ni defined then check that the number of fields
    # ni less than max_num_fields. This prevents a memory exhaustion DOS
    # attack via post bodies ukijumuisha many fields.
    ikiwa max_num_fields ni sio Tupu:
        num_fields = 1 + qs.count('&') + qs.count(';')
        ikiwa max_num_fields < num_fields:
            ashiria ValueError('Max number of fields exceeded')

    pairs = [s2 kila s1 kwenye qs.split('&') kila s2 kwenye s1.split(';')]
    r = []
    kila name_value kwenye pairs:
        ikiwa sio name_value na sio strict_parsing:
            endelea
        nv = name_value.split('=', 1)
        ikiwa len(nv) != 2:
            ikiwa strict_parsing:
                ashiria ValueError("bad query field: %r" % (name_value,))
            # Handle case of a control-name ukijumuisha no equal sign
            ikiwa keep_blank_values:
                nv.append('')
            isipokua:
                endelea
        ikiwa len(nv[1]) ama keep_blank_values:
            name = nv[0].replace('+', ' ')
            name = unquote(name, encoding=encoding, errors=errors)
            name = _coerce_result(name)
            value = nv[1].replace('+', ' ')
            value = unquote(value, encoding=encoding, errors=errors)
            value = _coerce_result(value)
            r.append((name, value))
    rudisha r

eleza unquote_plus(string, encoding='utf-8', errors='replace'):
    """Like unquote(), but also replace plus signs by spaces, kama required for
    unquoting HTML form values.

    unquote_plus('%7e/abc+def') -> '~/abc def'
    """
    string = string.replace('+', ' ')
    rudisha unquote(string, encoding, errors)

_ALWAYS_SAFE = frozenset(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                         b'abcdefghijklmnopqrstuvwxyz'
                         b'0123456789'
                         b'_.-~')
_ALWAYS_SAFE_BYTES = bytes(_ALWAYS_SAFE)
_safe_quoters = {}

kundi Quoter(collections.defaultdict):
    """A mapping kutoka bytes (in range(0,256)) to strings.

    String values are percent-encoded byte values, unless the key < 128, na
    kwenye the "safe" set (either the specified safe set, ama default set).
    """
    # Keeps a cache internally, using defaultdict, kila efficiency (lookups
    # of cached keys don't call Python code at all).
    eleza __init__(self, safe):
        """safe: bytes object."""
        self.safe = _ALWAYS_SAFE.union(safe)

    eleza __repr__(self):
        # Without this, will just display kama a defaultdict
        rudisha "<%s %r>" % (self.__class__.__name__, dict(self))

    eleza __missing__(self, b):
        # Handle a cache miss. Store quoted string kwenye cache na return.
        res = chr(b) ikiwa b kwenye self.safe isipokua '%{:02X}'.format(b)
        self[b] = res
        rudisha res

eleza quote(string, safe='/', encoding=Tupu, errors=Tupu):
    """quote('abc def') -> 'abc%20def'

    Each part of a URL, e.g. the path info, the query, etc., has a
    different set of reserved characters that must be quoted. The
    quote function offers a cautious (sio minimal) way to quote a
    string kila most of these parts.

    RFC 3986 Uniform Resource Identifier (URI): Generic Syntax lists
    the following (un)reserved characters.

    unreserved    = ALPHA / DIGIT / "-" / "." / "_" / "~"
    reserved      = gen-delims / sub-delims
    gen-delims    = ":" / "/" / "?" / "#" / "[" / "]" / "@"
    sub-delims    = "!" / "$" / "&" / "'" / "(" / ")"
                  / "*" / "+" / "," / ";" / "="

    Each of the reserved characters ni reserved kwenye some component of a URL,
    but sio necessarily kwenye all of them.

    The quote function %-escapes all characters that are neither kwenye the
    unreserved chars ("always safe") nor the additional chars set via the
    safe arg.

    The default kila the safe arg ni '/'. The character ni reserved, but in
    typical usage the quote function ni being called on a path where the
    existing slash characters are to be preserved.

    Python 3.7 updates kutoka using RFC 2396 to RFC 3986 to quote URL strings.
    Now, "~" ni included kwenye the set of unreserved characters.

    string na safe may be either str ama bytes objects. encoding na errors
    must sio be specified ikiwa string ni a bytes object.

    The optional encoding na errors parameters specify how to deal with
    non-ASCII characters, kama accepted by the str.encode method.
    By default, encoding='utf-8' (characters are encoded ukijumuisha UTF-8), na
    errors='strict' (unsupported characters ashiria a UnicodeEncodeError).
    """
    ikiwa isinstance(string, str):
        ikiwa sio string:
            rudisha string
        ikiwa encoding ni Tupu:
            encoding = 'utf-8'
        ikiwa errors ni Tupu:
            errors = 'strict'
        string = string.encode(encoding, errors)
    isipokua:
        ikiwa encoding ni sio Tupu:
            ashiria TypeError("quote() doesn't support 'encoding' kila bytes")
        ikiwa errors ni sio Tupu:
            ashiria TypeError("quote() doesn't support 'errors' kila bytes")
    rudisha quote_from_bytes(string, safe)

eleza quote_plus(string, safe='', encoding=Tupu, errors=Tupu):
    """Like quote(), but also replace ' ' ukijumuisha '+', kama required kila quoting
    HTML form values. Plus signs kwenye the original string are escaped unless
    they are included kwenye safe. It also does sio have safe default to '/'.
    """
    # Check ikiwa ' ' kwenye string, where string may either be a str ama bytes.  If
    # there are no spaces, the regular quote will produce the right answer.
    ikiwa ((isinstance(string, str) na ' ' haiko kwenye string) ama
        (isinstance(string, bytes) na b' ' haiko kwenye string)):
        rudisha quote(string, safe, encoding, errors)
    ikiwa isinstance(safe, str):
        space = ' '
    isipokua:
        space = b' '
    string = quote(string, safe + space, encoding, errors)
    rudisha string.replace(' ', '+')

eleza quote_from_bytes(bs, safe='/'):
    """Like quote(), but accepts a bytes object rather than a str, na does
    sio perform string-to-bytes encoding.  It always returns an ASCII string.
    quote_from_bytes(b'abc def\x3f') -> 'abc%20def%3f'
    """
    ikiwa sio isinstance(bs, (bytes, bytearray)):
        ashiria TypeError("quote_from_bytes() expected bytes")
    ikiwa sio bs:
        rudisha ''
    ikiwa isinstance(safe, str):
        # Normalize 'safe' by converting to bytes na removing non-ASCII chars
        safe = safe.encode('ascii', 'ignore')
    isipokua:
        safe = bytes([c kila c kwenye safe ikiwa c < 128])
    ikiwa sio bs.rstrip(_ALWAYS_SAFE_BYTES + safe):
        rudisha bs.decode()
    jaribu:
        quoter = _safe_quoters[safe]
    tatizo KeyError:
        _safe_quoters[safe] = quoter = Quoter(safe).__getitem__
    rudisha ''.join([quoter(char) kila char kwenye bs])

eleza urlencode(query, doseq=Uongo, safe='', encoding=Tupu, errors=Tupu,
              quote_via=quote_plus):
    """Encode a dict ama sequence of two-element tuples into a URL query string.

    If any values kwenye the query arg are sequences na doseq ni true, each
    sequence element ni converted to a separate parameter.

    If the query arg ni a sequence of two-element tuples, the order of the
    parameters kwenye the output will match the order of parameters kwenye the
    input.

    The components of a query arg may each be either a string ama a bytes type.

    The safe, encoding, na errors parameters are pitaed down to the function
    specified by quote_via (encoding na errors only ikiwa a component ni a str).
    """

    ikiwa hasattr(query, "items"):
        query = query.items()
    isipokua:
        # It's a bother at times that strings na string-like objects are
        # sequences.
        jaribu:
            # non-sequence items should sio work ukijumuisha len()
            # non-empty strings will fail this
            ikiwa len(query) na sio isinstance(query[0], tuple):
                ashiria TypeError
            # Zero-length sequences of all types will get here na succeed,
            # but that's a minor nit.  Since the original implementation
            # allowed empty dicts that type of behavior probably should be
            # preserved kila consistency
        tatizo TypeError:
            ty, va, tb = sys.exc_info()
            ashiria TypeError("not a valid non-string sequence "
                            "or mapping object").with_traceback(tb)

    l = []
    ikiwa sio doseq:
        kila k, v kwenye query:
            ikiwa isinstance(k, bytes):
                k = quote_via(k, safe)
            isipokua:
                k = quote_via(str(k), safe, encoding, errors)

            ikiwa isinstance(v, bytes):
                v = quote_via(v, safe)
            isipokua:
                v = quote_via(str(v), safe, encoding, errors)
            l.append(k + '=' + v)
    isipokua:
        kila k, v kwenye query:
            ikiwa isinstance(k, bytes):
                k = quote_via(k, safe)
            isipokua:
                k = quote_via(str(k), safe, encoding, errors)

            ikiwa isinstance(v, bytes):
                v = quote_via(v, safe)
                l.append(k + '=' + v)
            lasivyo isinstance(v, str):
                v = quote_via(v, safe, encoding, errors)
                l.append(k + '=' + v)
            isipokua:
                jaribu:
                    # Is this a sufficient test kila sequence-ness?
                    x = len(v)
                tatizo TypeError:
                    # sio a sequence
                    v = quote_via(str(v), safe, encoding, errors)
                    l.append(k + '=' + v)
                isipokua:
                    # loop over the sequence
                    kila elt kwenye v:
                        ikiwa isinstance(elt, bytes):
                            elt = quote_via(elt, safe)
                        isipokua:
                            elt = quote_via(str(elt), safe, encoding, errors)
                        l.append(k + '=' + elt)
    rudisha '&'.join(l)


eleza to_bytes(url):
    warnings.warn("urllib.parse.to_bytes() ni deprecated kama of 3.8",
                  DeprecationWarning, stacklevel=2)
    rudisha _to_bytes(url)


eleza _to_bytes(url):
    """to_bytes(u"URL") --> 'URL'."""
    # Most URL schemes require ASCII. If that changes, the conversion
    # can be relaxed.
    # XXX get rid of to_bytes()
    ikiwa isinstance(url, str):
        jaribu:
            url = url.encode("ASCII").decode()
        tatizo UnicodeError:
            ashiria UnicodeError("URL " + repr(url) +
                               " contains non-ASCII characters")
    rudisha url


eleza unwrap(url):
    """Transform a string like '<URL:scheme://host/path>' into 'scheme://host/path'.

    The string ni returned unchanged ikiwa it's sio a wrapped URL.
    """
    url = str(url).strip()
    ikiwa url[:1] == '<' na url[-1:] == '>':
        url = url[1:-1].strip()
    ikiwa url[:4] == 'URL:':
        url = url[4:].strip()
    rudisha url


eleza splittype(url):
    warnings.warn("urllib.parse.splittype() ni deprecated kama of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splittype(url)


_typeprog = Tupu
eleza _splittype(url):
    """splittype('type:opaquestring') --> 'type', 'opaquestring'."""
    global _typeprog
    ikiwa _typeprog ni Tupu:
        _typeprog = re.compile('([^/:]+):(.*)', re.DOTALL)

    match = _typeprog.match(url)
    ikiwa match:
        scheme, data = match.groups()
        rudisha scheme.lower(), data
    rudisha Tupu, url


eleza splithost(url):
    warnings.warn("urllib.parse.splithost() ni deprecated kama of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splithost(url)


_hostprog = Tupu
eleza _splithost(url):
    """splithost('//host[:port]/path') --> 'host[:port]', '/path'."""
    global _hostprog
    ikiwa _hostprog ni Tupu:
        _hostprog = re.compile('//([^/#?]*)(.*)', re.DOTALL)

    match = _hostprog.match(url)
    ikiwa match:
        host_port, path = match.groups()
        ikiwa path na path[0] != '/':
            path = '/' + path
        rudisha host_port, path
    rudisha Tupu, url


eleza splituser(host):
    warnings.warn("urllib.parse.splituser() ni deprecated kama of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splituser(host)


eleza _splituser(host):
    """splituser('user[:pitawd]@host[:port]') --> 'user[:pitawd]', 'host[:port]'."""
    user, delim, host = host.rpartition('@')
    rudisha (user ikiwa delim isipokua Tupu), host


eleza splitpitawd(user):
    warnings.warn("urllib.parse.splitpitawd() ni deprecated kama of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splitpitawd(user)


eleza _splitpitawd(user):
    """splitpitawd('user:pitawd') -> 'user', 'pitawd'."""
    user, delim, pitawd = user.partition(':')
    rudisha user, (pitawd ikiwa delim isipokua Tupu)


eleza splitport(host):
    warnings.warn("urllib.parse.splitport() ni deprecated kama of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splitport(host)


# splittag('/path#tag') --> '/path', 'tag'
_portprog = Tupu
eleza _splitport(host):
    """splitport('host:port') --> 'host', 'port'."""
    global _portprog
    ikiwa _portprog ni Tupu:
        _portprog = re.compile('(.*):([0-9]*)$', re.DOTALL)

    match = _portprog.match(host)
    ikiwa match:
        host, port = match.groups()
        ikiwa port:
            rudisha host, port
    rudisha host, Tupu


eleza splitnport(host, defport=-1):
    warnings.warn("urllib.parse.splitnport() ni deprecated kama of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splitnport(host, defport)


eleza _splitnport(host, defport=-1):
    """Split host na port, returning numeric port.
    Return given default port ikiwa no ':' found; defaults to -1.
    Return numerical port ikiwa a valid number are found after ':'.
    Return Tupu ikiwa ':' but sio a valid number."""
    host, delim, port = host.rpartition(':')
    ikiwa sio delim:
        host = port
    lasivyo port:
        jaribu:
            nport = int(port)
        tatizo ValueError:
            nport = Tupu
        rudisha host, nport
    rudisha host, defport


eleza splitquery(url):
    warnings.warn("urllib.parse.splitquery() ni deprecated kama of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splitquery(url)


eleza _splitquery(url):
    """splitquery('/path?query') --> '/path', 'query'."""
    path, delim, query = url.rpartition('?')
    ikiwa delim:
        rudisha path, query
    rudisha url, Tupu


eleza splittag(url):
    warnings.warn("urllib.parse.splittag() ni deprecated kama of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splittag(url)


eleza _splittag(url):
    """splittag('/path#tag') --> '/path', 'tag'."""
    path, delim, tag = url.rpartition('#')
    ikiwa delim:
        rudisha path, tag
    rudisha url, Tupu


eleza splitattr(url):
    warnings.warn("urllib.parse.splitattr() ni deprecated kama of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splitattr(url)


eleza _splitattr(url):
    """splitattr('/path;attr1=value1;attr2=value2;...') ->
        '/path', ['attr1=value1', 'attr2=value2', ...]."""
    words = url.split(';')
    rudisha words[0], words[1:]


eleza splitvalue(attr):
    warnings.warn("urllib.parse.splitvalue() ni deprecated kama of 3.8, "
                  "use urllib.parse.parse_qsl() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splitvalue(attr)


eleza _splitvalue(attr):
    """splitvalue('attr=value') --> 'attr', 'value'."""
    attr, delim, value = attr.partition('=')
    rudisha attr, (value ikiwa delim isipokua Tupu)
