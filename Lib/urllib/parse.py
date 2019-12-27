"""Parse (absolute and relative) URLs.

urlparse module is based upon the following RFC specifications.

RFC 3986 (STD66): "Uniform Resource Identifiers" by T. Berners-Lee, R. Fielding
and L.  Masinter, January 2005.

RFC 2732 : "Format for Literal IPv6 Addresses in URL's by R.Hinden, B.Carpenter
and L.Masinter, December 1999.

RFC 2396:  "Uniform Resource Identifiers (URI)": Generic Syntax by T.
Berners-Lee, R. Fielding, and L. Masinter, August 1998.

RFC 2368: "The mailto URL scheme", by P.Hoffman , L Masinter, J. Zawinski, July 1998.

RFC 1808: "Relative Uniform Resource Locators", by R. Fielding, UC Irvine, June
1995.

RFC 1738: "Uniform Resource Locators (URL)" by T. Berners-Lee, L. Masinter, M.
McCahill, December 1994

RFC 3986 is considered the current standard and any future changes to
urlparse module should conform with it.  The urlparse module is
currently not entirely compliant with this RFC due to defacto
scenarios for parsing, and for backward compatibility purposes, some
parsing quirks kutoka older RFCs are retained. The testcases in
test_urlparse.py provides a good indicator of parsing behavior.
"""

agiza re
agiza sys
agiza collections
agiza warnings

__all__ = ["urlparse", "urlunparse", "urljoin", "urldefrag",
           "urlsplit", "urlunsplit", "urlencode", "parse_qs",
           "parse_qsl", "quote", "quote_plus", "quote_kutoka_bytes",
           "unquote", "unquote_plus", "unquote_to_bytes",
           "DefragResult", "ParseResult", "SplitResult",
           "DefragResultBytes", "ParseResultBytes", "SplitResultBytes"]

# A classification of schemes.
# The empty string classifies URLs with no scheme specified,
# being the default value returned by “urlsplit” and “urlparse”.

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

# These are not actually used anymore, but should stay for backwards
# compatibility.  (They are undocumented, but have a public-looking name.)

non_hierarchical = ['gopher', 'hdl', 'mailto', 'news',
                    'telnet', 'wais', 'imap', 'snews', 'sip', 'sips']

uses_query = ['', 'http', 'wais', 'imap', 'https', 'shttp', 'mms',
              'gopher', 'rtsp', 'rtspu', 'sip', 'sips']

uses_fragment = ['', 'ftp', 'hdl', 'http', 'gopher', 'news',
                 'nntp', 'wais', 'https', 'shttp', 'snews',
                 'file', 'prospero']

# Characters valid in scheme names
scheme_chars = ('abcdefghijklmnopqrstuvwxyz'
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                '0123456789'
                '+-.')

# XXX: Consider replacing with functools.lru_cache
MAX_CACHE_SIZE = 20
_parse_cache = {}

eleza clear_cache():
    """Clear the parse cache and the quoters cache."""
    _parse_cache.clear()
    _safe_quoters.clear()


# Helpers for bytes handling
# For 3.2, we deliberately require applications that
# handle improperly quoted URLs to do their own
# decoding and encoding. If valid use cases are
# presented, we may relax this by using latin-1
# decoding internally for 3.3
_implicit_encoding = 'ascii'
_implicit_errors = 'strict'

eleza _noop(obj):
    rudisha obj

eleza _encode_result(obj, encoding=_implicit_encoding,
                        errors=_implicit_errors):
    rudisha obj.encode(encoding, errors)

eleza _decode_args(args, encoding=_implicit_encoding,
                       errors=_implicit_errors):
    rudisha tuple(x.decode(encoding, errors) ikiwa x else '' for x in args)

eleza _coerce_args(*args):
    # Invokes decode ikiwa necessary to create str args
    # and returns the coerced inputs along with
    # an appropriate result coercion function
    #   - noop for str inputs
    #   - encoding function otherwise
    str_input = isinstance(args[0], str)
    for arg in args[1:]:
        # We special-case the empty string to support the
        # "scheme=''" default argument to some functions
        ikiwa arg and isinstance(arg, str) != str_input:
            raise TypeError("Cannot mix str and non-str arguments")
    ikiwa str_input:
        rudisha args + (_noop,)
    rudisha _decode_args(args) + (_encode_result,)

# Result objects are more helpful than simple tuples
kundi _ResultMixinStr(object):
    """Standard approach to encoding parsed results kutoka str to bytes"""
    __slots__ = ()

    eleza encode(self, encoding='ascii', errors='strict'):
        rudisha self._encoded_counterpart(*(x.encode(encoding, errors) for x in self))


kundi _ResultMixinBytes(object):
    """Standard approach to decoding parsed results kutoka bytes to str"""
    __slots__ = ()

    eleza decode(self, encoding='ascii', errors='strict'):
        rudisha self._decoded_counterpart(*(x.decode(encoding, errors) for x in self))


kundi _NetlocResultMixinBase(object):
    """Shared methods for the parsed result objects containing a netloc element"""
    __slots__ = ()

    @property
    eleza username(self):
        rudisha self._userinfo[0]

    @property
    eleza password(self):
        rudisha self._userinfo[1]

    @property
    eleza hostname(self):
        hostname = self._hostinfo[0]
        ikiwa not hostname:
            rudisha None
        # Scoped IPv6 address may have zone info, which must not be lowercased
        # like http://[fe80::822a:a8ff:fe49:470c%tESt]:1234/keys
        separator = '%' ikiwa isinstance(hostname, str) else b'%'
        hostname, percent, zone = hostname.partition(separator)
        rudisha hostname.lower() + percent + zone

    @property
    eleza port(self):
        port = self._hostinfo[1]
        ikiwa port is not None:
            try:
                port = int(port, 10)
            except ValueError:
                message = f'Port could not be cast to integer value as {port!r}'
                raise ValueError(message) kutoka None
            ikiwa not ( 0 <= port <= 65535):
                raise ValueError("Port out of range 0-65535")
        rudisha port


kundi _NetlocResultMixinStr(_NetlocResultMixinBase, _ResultMixinStr):
    __slots__ = ()

    @property
    eleza _userinfo(self):
        netloc = self.netloc
        userinfo, have_info, hostinfo = netloc.rpartition('@')
        ikiwa have_info:
            username, have_password, password = userinfo.partition(':')
            ikiwa not have_password:
                password = None
        else:
            username = password = None
        rudisha username, password

    @property
    eleza _hostinfo(self):
        netloc = self.netloc
        _, _, hostinfo = netloc.rpartition('@')
        _, have_open_br, bracketed = hostinfo.partition('[')
        ikiwa have_open_br:
            hostname, _, port = bracketed.partition(']')
            _, _, port = port.partition(':')
        else:
            hostname, _, port = hostinfo.partition(':')
        ikiwa not port:
            port = None
        rudisha hostname, port


kundi _NetlocResultMixinBytes(_NetlocResultMixinBase, _ResultMixinBytes):
    __slots__ = ()

    @property
    eleza _userinfo(self):
        netloc = self.netloc
        userinfo, have_info, hostinfo = netloc.rpartition(b'@')
        ikiwa have_info:
            username, have_password, password = userinfo.partition(b':')
            ikiwa not have_password:
                password = None
        else:
            username = password = None
        rudisha username, password

    @property
    eleza _hostinfo(self):
        netloc = self.netloc
        _, _, hostinfo = netloc.rpartition(b'@')
        _, have_open_br, bracketed = hostinfo.partition(b'[')
        ikiwa have_open_br:
            hostname, _, port = bracketed.partition(b']')
            _, _, port = port.partition(b':')
        else:
            hostname, _, port = hostinfo.partition(b':')
        ikiwa not port:
            port = None
        rudisha hostname, port


kutoka collections agiza namedtuple

_DefragResultBase = namedtuple('DefragResult', 'url fragment')
_SplitResultBase = namedtuple(
    'SplitResult', 'scheme netloc path query fragment')
_ParseResultBase = namedtuple(
    'ParseResult', 'scheme netloc path params query fragment')

_DefragResultBase.__doc__ = """
DefragResult(url, fragment)

A 2-tuple that contains the url without fragment identifier and the fragment
identifier as a separate argument.
"""

_DefragResultBase.url.__doc__ = """The URL with no fragment identifier."""

_DefragResultBase.fragment.__doc__ = """
Fragment identifier separated kutoka URL, that allows indirect identification of a
secondary resource by reference to a primary resource and additional identifying
information.
"""

_SplitResultBase.__doc__ = """
SplitResult(scheme, netloc, path, query, fragment)

A 5-tuple that contains the different components of a URL. Similar to
ParseResult, but does not split params.
"""

_SplitResultBase.scheme.__doc__ = """Specifies URL scheme for the request."""

_SplitResultBase.netloc.__doc__ = """
Network location where the request is made to.
"""

_SplitResultBase.path.__doc__ = """
The hierarchical path, such as the path to a file to download.
"""

_SplitResultBase.query.__doc__ = """
The query component, that contains non-hierarchical data, that along with data
in path component, identifies a resource in the scope of URI's scheme and
network location.
"""

_SplitResultBase.fragment.__doc__ = """
Fragment identifier, that allows indirect identification of a secondary resource
by reference to a primary resource and additional identifying information.
"""

_ParseResultBase.__doc__ = """
ParseResult(scheme, netloc, path, params, query, fragment)

A 6-tuple that contains components of a parsed URL.
"""

_ParseResultBase.scheme.__doc__ = _SplitResultBase.scheme.__doc__
_ParseResultBase.netloc.__doc__ = _SplitResultBase.netloc.__doc__
_ParseResultBase.path.__doc__ = _SplitResultBase.path.__doc__
_ParseResultBase.params.__doc__ = """
Parameters for last path element used to dereference the URI in order to provide
access to perform some operation on the resource.
"""

_ParseResultBase.query.__doc__ = _SplitResultBase.query.__doc__
_ParseResultBase.fragment.__doc__ = _SplitResultBase.fragment.__doc__


# For backwards compatibility, alias _NetlocResultMixinStr
# ResultBase is no longer part of the documented API, but it is
# retained since deprecating it isn't worth the hassle
ResultBase = _NetlocResultMixinStr

# Structured result objects for string data
kundi DefragResult(_DefragResultBase, _ResultMixinStr):
    __slots__ = ()
    eleza geturl(self):
        ikiwa self.fragment:
            rudisha self.url + '#' + self.fragment
        else:
            rudisha self.url

kundi SplitResult(_SplitResultBase, _NetlocResultMixinStr):
    __slots__ = ()
    eleza geturl(self):
        rudisha urlunsplit(self)

kundi ParseResult(_ParseResultBase, _NetlocResultMixinStr):
    __slots__ = ()
    eleza geturl(self):
        rudisha urlunparse(self)

# Structured result objects for bytes data
kundi DefragResultBytes(_DefragResultBase, _ResultMixinBytes):
    __slots__ = ()
    eleza geturl(self):
        ikiwa self.fragment:
            rudisha self.url + b'#' + self.fragment
        else:
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
    for _decoded, _encoded in _result_pairs:
        _decoded._encoded_counterpart = _encoded
        _encoded._decoded_counterpart = _decoded

_fix_result_transcoding()
del _fix_result_transcoding

eleza urlparse(url, scheme='', allow_fragments=True):
    """Parse a URL into 6 components:
    <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    Return a 6-tuple: (scheme, netloc, path, params, query, fragment).
    Note that we don't break the components up in smaller bits
    (e.g. netloc is a single string) and we don't expand % escapes."""
    url, scheme, _coerce_result = _coerce_args(url, scheme)
    splitresult = urlsplit(url, scheme, allow_fragments)
    scheme, netloc, url, query, fragment = splitresult
    ikiwa scheme in uses_params and ';' in url:
        url, params = _splitparams(url)
    else:
        params = ''
    result = ParseResult(scheme, netloc, url, params, query, fragment)
    rudisha _coerce_result(result)

eleza _splitparams(url):
    ikiwa '/'  in url:
        i = url.find(';', url.rfind('/'))
        ikiwa i < 0:
            rudisha url, ''
    else:
        i = url.find(';')
    rudisha url[:i], url[i+1:]

eleza _splitnetloc(url, start=0):
    delim = len(url)   # position of end of domain part of url, default is end
    for c in '/?#':    # look for delimiters; the order is NOT agizaant
        wdelim = url.find(c, start)        # find first of this delim
        ikiwa wdelim >= 0:                    # ikiwa found
            delim = min(delim, wdelim)     # use earliest delim position
    rudisha url[start:delim], url[delim:]   # rudisha (domain, rest)

eleza _checknetloc(netloc):
    ikiwa not netloc or netloc.isascii():
        return
    # looking for characters like \u2100 that expand to 'a/c'
    # IDNA uses NFKC equivalence, so normalize for this check
    agiza unicodedata
    n = netloc.replace('@', '')   # ignore characters already included
    n = n.replace(':', '')        # but not the surrounding text
    n = n.replace('#', '')
    n = n.replace('?', '')
    netloc2 = unicodedata.normalize('NFKC', n)
    ikiwa n == netloc2:
        return
    for c in '/?#@:':
        ikiwa c in netloc2:
            raise ValueError("netloc '" + netloc + "' contains invalid " +
                             "characters under NFKC normalization")

eleza urlsplit(url, scheme='', allow_fragments=True):
    """Parse a URL into 5 components:
    <scheme>://<netloc>/<path>?<query>#<fragment>
    Return a 5-tuple: (scheme, netloc, path, query, fragment).
    Note that we don't break the components up in smaller bits
    (e.g. netloc is a single string) and we don't expand % escapes."""
    url, scheme, _coerce_result = _coerce_args(url, scheme)
    allow_fragments = bool(allow_fragments)
    key = url, scheme, allow_fragments, type(url), type(scheme)
    cached = _parse_cache.get(key, None)
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
                ikiwa (('[' in netloc and ']' not in netloc) or
                        (']' in netloc and '[' not in netloc)):
                    raise ValueError("Invalid IPv6 URL")
            ikiwa allow_fragments and '#' in url:
                url, fragment = url.split('#', 1)
            ikiwa '?' in url:
                url, query = url.split('?', 1)
            _checknetloc(netloc)
            v = SplitResult('http', netloc, url, query, fragment)
            _parse_cache[key] = v
            rudisha _coerce_result(v)
        for c in url[:i]:
            ikiwa c not in scheme_chars:
                break
        else:
            # make sure "url" is not actually a port number (in which case
            # "scheme" is really part of the path)
            rest = url[i+1:]
            ikiwa not rest or any(c not in '0123456789' for c in rest):
                # not a port number
                scheme, url = url[:i].lower(), rest

    ikiwa url[:2] == '//':
        netloc, url = _splitnetloc(url, 2)
        ikiwa (('[' in netloc and ']' not in netloc) or
                (']' in netloc and '[' not in netloc)):
            raise ValueError("Invalid IPv6 URL")
    ikiwa allow_fragments and '#' in url:
        url, fragment = url.split('#', 1)
    ikiwa '?' in url:
        url, query = url.split('?', 1)
    _checknetloc(netloc)
    v = SplitResult(scheme, netloc, url, query, fragment)
    _parse_cache[key] = v
    rudisha _coerce_result(v)

eleza urlunparse(components):
    """Put a parsed URL back together again.  This may result in a
    slightly different, but equivalent URL, ikiwa the URL that was parsed
    originally had redundant delimiters, e.g. a ? with an empty query
    (the draft states that these are equivalent)."""
    scheme, netloc, url, params, query, fragment, _coerce_result = (
                                                  _coerce_args(*components))
    ikiwa params:
        url = "%s;%s" % (url, params)
    rudisha _coerce_result(urlunsplit((scheme, netloc, url, query, fragment)))

eleza urlunsplit(components):
    """Combine the elements of a tuple as returned by urlsplit() into a
    complete URL as a string. The data argument can be any five-item iterable.
    This may result in a slightly different, but equivalent URL, ikiwa the URL that
    was parsed originally had unnecessary delimiters (for example, a ? with an
    empty query; the RFC states that these are equivalent)."""
    scheme, netloc, url, query, fragment, _coerce_result = (
                                          _coerce_args(*components))
    ikiwa netloc or (scheme and scheme in uses_netloc and url[:2] != '//'):
        ikiwa url and url[:1] != '/': url = '/' + url
        url = '//' + (netloc or '') + url
    ikiwa scheme:
        url = scheme + ':' + url
    ikiwa query:
        url = url + '?' + query
    ikiwa fragment:
        url = url + '#' + fragment
    rudisha _coerce_result(url)

eleza urljoin(base, url, allow_fragments=True):
    """Join a base URL and a possibly relative URL to form an absolute
    interpretation of the latter."""
    ikiwa not base:
        rudisha url
    ikiwa not url:
        rudisha base

    base, url, _coerce_result = _coerce_args(base, url)
    bscheme, bnetloc, bpath, bparams, bquery, bfragment = \
            urlparse(base, '', allow_fragments)
    scheme, netloc, path, params, query, fragment = \
            urlparse(url, bscheme, allow_fragments)

    ikiwa scheme != bscheme or scheme not in uses_relative:
        rudisha _coerce_result(url)
    ikiwa scheme in uses_netloc:
        ikiwa netloc:
            rudisha _coerce_result(urlunparse((scheme, netloc, path,
                                              params, query, fragment)))
        netloc = bnetloc

    ikiwa not path and not params:
        path = bpath
        params = bparams
        ikiwa not query:
            query = bquery
        rudisha _coerce_result(urlunparse((scheme, netloc, path,
                                          params, query, fragment)))

    base_parts = bpath.split('/')
    ikiwa base_parts[-1] != '':
        # the last item is not a directory, so will not be taken into account
        # in resolving the relative path
        del base_parts[-1]

    # for rfc3986, ignore all base path should the first character be root.
    ikiwa path[:1] == '/':
        segments = path.split('/')
    else:
        segments = base_parts + path.split('/')
        # filter out elements that would cause redundant slashes on re-joining
        # the resolved_path
        segments[1:-1] = filter(None, segments[1:-1])

    resolved_path = []

    for seg in segments:
        ikiwa seg == '..':
            try:
                resolved_path.pop()
            except IndexError:
                # ignore any .. segments that would otherwise cause an IndexError
                # when popped kutoka resolved_path ikiwa resolving for rfc3986
                pass
        elikiwa seg == '.':
            continue
        else:
            resolved_path.append(seg)

    ikiwa segments[-1] in ('.', '..'):
        # do some post-processing here. ikiwa the last segment was a relative dir,
        # then we need to append the trailing '/'
        resolved_path.append('')

    rudisha _coerce_result(urlunparse((scheme, netloc, '/'.join(
        resolved_path) or '/', params, query, fragment)))


eleza urldefrag(url):
    """Removes any existing fragment kutoka URL.

    Returns a tuple of the defragmented URL and the fragment.  If
    the URL contained no fragments, the second element is the
    empty string.
    """
    url, _coerce_result = _coerce_args(url)
    ikiwa '#' in url:
        s, n, p, a, q, frag = urlparse(url)
        defrag = urlunparse((s, n, p, a, q, ''))
    else:
        frag = ''
        defrag = url
    rudisha _coerce_result(DefragResult(defrag, frag))

_hexdig = '0123456789ABCDEFabcdef'
_hextobyte = None

eleza unquote_to_bytes(string):
    """unquote_to_bytes('abc%20def') -> b'abc def'."""
    # Note: strings are encoded as UTF-8. This is only an issue ikiwa it contains
    # unescaped non-ASCII characters, which URIs should not.
    ikiwa not string:
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
    # Delay the initialization of the table to not waste memory
    # ikiwa the function is never called
    global _hextobyte
    ikiwa _hextobyte is None:
        _hextobyte = {(a + b).encode(): bytes.kutokahex(a + b)
                      for a in _hexdig for b in _hexdig}
    for item in bits[1:]:
        try:
            append(_hextobyte[item[:2]])
            append(item[2:])
        except KeyError:
            append(b'%')
            append(item)
    rudisha b''.join(res)

_asciire = re.compile('([\x00-\x7f]+)')

eleza unquote(string, encoding='utf-8', errors='replace'):
    """Replace %xx escapes by their single-character equivalent. The optional
    encoding and errors parameters specify how to decode percent-encoded
    sequences into Unicode characters, as accepted by the bytes.decode()
    method.
    By default, percent-encoded sequences are decoded with UTF-8, and invalid
    sequences are replaced by a placeholder character.

    unquote('abc%20def') -> 'abc def'.
    """
    ikiwa '%' not in string:
        string.split
        rudisha string
    ikiwa encoding is None:
        encoding = 'utf-8'
    ikiwa errors is None:
        errors = 'replace'
    bits = _asciire.split(string)
    res = [bits[0]]
    append = res.append
    for i in range(1, len(bits), 2):
        append(unquote_to_bytes(bits[i]).decode(encoding, errors))
        append(bits[i + 1])
    rudisha ''.join(res)


eleza parse_qs(qs, keep_blank_values=False, strict_parsing=False,
             encoding='utf-8', errors='replace', max_num_fields=None):
    """Parse a query given as a string argument.

        Arguments:

        qs: percent-encoded query string to be parsed

        keep_blank_values: flag indicating whether blank values in
            percent-encoded queries should be treated as blank strings.
            A true value indicates that blanks should be retained as
            blank strings.  The default false value indicates that
            blank values are to be ignored and treated as ikiwa they were
            not included.

        strict_parsing: flag indicating what to do with parsing errors.
            If false (the default), errors are silently ignored.
            If true, errors raise a ValueError exception.

        encoding and errors: specify how to decode percent-encoded sequences
            into Unicode characters, as accepted by the bytes.decode() method.

        max_num_fields: int. If set, then throws a ValueError ikiwa there
            are more than n fields read by parse_qsl().

        Returns a dictionary.
    """
    parsed_result = {}
    pairs = parse_qsl(qs, keep_blank_values, strict_parsing,
                      encoding=encoding, errors=errors,
                      max_num_fields=max_num_fields)
    for name, value in pairs:
        ikiwa name in parsed_result:
            parsed_result[name].append(value)
        else:
            parsed_result[name] = [value]
    rudisha parsed_result


eleza parse_qsl(qs, keep_blank_values=False, strict_parsing=False,
              encoding='utf-8', errors='replace', max_num_fields=None):
    """Parse a query given as a string argument.

        Arguments:

        qs: percent-encoded query string to be parsed

        keep_blank_values: flag indicating whether blank values in
            percent-encoded queries should be treated as blank strings.
            A true value indicates that blanks should be retained as blank
            strings.  The default false value indicates that blank values
            are to be ignored and treated as ikiwa they were  not included.

        strict_parsing: flag indicating what to do with parsing errors. If
            false (the default), errors are silently ignored. If true,
            errors raise a ValueError exception.

        encoding and errors: specify how to decode percent-encoded sequences
            into Unicode characters, as accepted by the bytes.decode() method.

        max_num_fields: int. If set, then throws a ValueError
            ikiwa there are more than n fields read by parse_qsl().

        Returns a list, as G-d intended.
    """
    qs, _coerce_result = _coerce_args(qs)

    # If max_num_fields is defined then check that the number of fields
    # is less than max_num_fields. This prevents a memory exhaustion DOS
    # attack via post bodies with many fields.
    ikiwa max_num_fields is not None:
        num_fields = 1 + qs.count('&') + qs.count(';')
        ikiwa max_num_fields < num_fields:
            raise ValueError('Max number of fields exceeded')

    pairs = [s2 for s1 in qs.split('&') for s2 in s1.split(';')]
    r = []
    for name_value in pairs:
        ikiwa not name_value and not strict_parsing:
            continue
        nv = name_value.split('=', 1)
        ikiwa len(nv) != 2:
            ikiwa strict_parsing:
                raise ValueError("bad query field: %r" % (name_value,))
            # Handle case of a control-name with no equal sign
            ikiwa keep_blank_values:
                nv.append('')
            else:
                continue
        ikiwa len(nv[1]) or keep_blank_values:
            name = nv[0].replace('+', ' ')
            name = unquote(name, encoding=encoding, errors=errors)
            name = _coerce_result(name)
            value = nv[1].replace('+', ' ')
            value = unquote(value, encoding=encoding, errors=errors)
            value = _coerce_result(value)
            r.append((name, value))
    rudisha r

eleza unquote_plus(string, encoding='utf-8', errors='replace'):
    """Like unquote(), but also replace plus signs by spaces, as required for
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

    String values are percent-encoded byte values, unless the key < 128, and
    in the "safe" set (either the specified safe set, or default set).
    """
    # Keeps a cache internally, using defaultdict, for efficiency (lookups
    # of cached keys don't call Python code at all).
    eleza __init__(self, safe):
        """safe: bytes object."""
        self.safe = _ALWAYS_SAFE.union(safe)

    eleza __repr__(self):
        # Without this, will just display as a defaultdict
        rudisha "<%s %r>" % (self.__class__.__name__, dict(self))

    eleza __missing__(self, b):
        # Handle a cache miss. Store quoted string in cache and return.
        res = chr(b) ikiwa b in self.safe else '%{:02X}'.format(b)
        self[b] = res
        rudisha res

eleza quote(string, safe='/', encoding=None, errors=None):
    """quote('abc def') -> 'abc%20def'

    Each part of a URL, e.g. the path info, the query, etc., has a
    different set of reserved characters that must be quoted. The
    quote function offers a cautious (not minimal) way to quote a
    string for most of these parts.

    RFC 3986 Uniform Resource Identifier (URI): Generic Syntax lists
    the following (un)reserved characters.

    unreserved    = ALPHA / DIGIT / "-" / "." / "_" / "~"
    reserved      = gen-delims / sub-delims
    gen-delims    = ":" / "/" / "?" / "#" / "[" / "]" / "@"
    sub-delims    = "!" / "$" / "&" / "'" / "(" / ")"
                  / "*" / "+" / "," / ";" / "="

    Each of the reserved characters is reserved in some component of a URL,
    but not necessarily in all of them.

    The quote function %-escapes all characters that are neither in the
    unreserved chars ("always safe") nor the additional chars set via the
    safe arg.

    The default for the safe arg is '/'. The character is reserved, but in
    typical usage the quote function is being called on a path where the
    existing slash characters are to be preserved.

    Python 3.7 updates kutoka using RFC 2396 to RFC 3986 to quote URL strings.
    Now, "~" is included in the set of unreserved characters.

    string and safe may be either str or bytes objects. encoding and errors
    must not be specified ikiwa string is a bytes object.

    The optional encoding and errors parameters specify how to deal with
    non-ASCII characters, as accepted by the str.encode method.
    By default, encoding='utf-8' (characters are encoded with UTF-8), and
    errors='strict' (unsupported characters raise a UnicodeEncodeError).
    """
    ikiwa isinstance(string, str):
        ikiwa not string:
            rudisha string
        ikiwa encoding is None:
            encoding = 'utf-8'
        ikiwa errors is None:
            errors = 'strict'
        string = string.encode(encoding, errors)
    else:
        ikiwa encoding is not None:
            raise TypeError("quote() doesn't support 'encoding' for bytes")
        ikiwa errors is not None:
            raise TypeError("quote() doesn't support 'errors' for bytes")
    rudisha quote_kutoka_bytes(string, safe)

eleza quote_plus(string, safe='', encoding=None, errors=None):
    """Like quote(), but also replace ' ' with '+', as required for quoting
    HTML form values. Plus signs in the original string are escaped unless
    they are included in safe. It also does not have safe default to '/'.
    """
    # Check ikiwa ' ' in string, where string may either be a str or bytes.  If
    # there are no spaces, the regular quote will produce the right answer.
    ikiwa ((isinstance(string, str) and ' ' not in string) or
        (isinstance(string, bytes) and b' ' not in string)):
        rudisha quote(string, safe, encoding, errors)
    ikiwa isinstance(safe, str):
        space = ' '
    else:
        space = b' '
    string = quote(string, safe + space, encoding, errors)
    rudisha string.replace(' ', '+')

eleza quote_kutoka_bytes(bs, safe='/'):
    """Like quote(), but accepts a bytes object rather than a str, and does
    not perform string-to-bytes encoding.  It always returns an ASCII string.
    quote_kutoka_bytes(b'abc def\x3f') -> 'abc%20def%3f'
    """
    ikiwa not isinstance(bs, (bytes, bytearray)):
        raise TypeError("quote_kutoka_bytes() expected bytes")
    ikiwa not bs:
        rudisha ''
    ikiwa isinstance(safe, str):
        # Normalize 'safe' by converting to bytes and removing non-ASCII chars
        safe = safe.encode('ascii', 'ignore')
    else:
        safe = bytes([c for c in safe ikiwa c < 128])
    ikiwa not bs.rstrip(_ALWAYS_SAFE_BYTES + safe):
        rudisha bs.decode()
    try:
        quoter = _safe_quoters[safe]
    except KeyError:
        _safe_quoters[safe] = quoter = Quoter(safe).__getitem__
    rudisha ''.join([quoter(char) for char in bs])

eleza urlencode(query, doseq=False, safe='', encoding=None, errors=None,
              quote_via=quote_plus):
    """Encode a dict or sequence of two-element tuples into a URL query string.

    If any values in the query arg are sequences and doseq is true, each
    sequence element is converted to a separate parameter.

    If the query arg is a sequence of two-element tuples, the order of the
    parameters in the output will match the order of parameters in the
    input.

    The components of a query arg may each be either a string or a bytes type.

    The safe, encoding, and errors parameters are passed down to the function
    specified by quote_via (encoding and errors only ikiwa a component is a str).
    """

    ikiwa hasattr(query, "items"):
        query = query.items()
    else:
        # It's a bother at times that strings and string-like objects are
        # sequences.
        try:
            # non-sequence items should not work with len()
            # non-empty strings will fail this
            ikiwa len(query) and not isinstance(query[0], tuple):
                raise TypeError
            # Zero-length sequences of all types will get here and succeed,
            # but that's a minor nit.  Since the original implementation
            # allowed empty dicts that type of behavior probably should be
            # preserved for consistency
        except TypeError:
            ty, va, tb = sys.exc_info()
            raise TypeError("not a valid non-string sequence "
                            "or mapping object").with_traceback(tb)

    l = []
    ikiwa not doseq:
        for k, v in query:
            ikiwa isinstance(k, bytes):
                k = quote_via(k, safe)
            else:
                k = quote_via(str(k), safe, encoding, errors)

            ikiwa isinstance(v, bytes):
                v = quote_via(v, safe)
            else:
                v = quote_via(str(v), safe, encoding, errors)
            l.append(k + '=' + v)
    else:
        for k, v in query:
            ikiwa isinstance(k, bytes):
                k = quote_via(k, safe)
            else:
                k = quote_via(str(k), safe, encoding, errors)

            ikiwa isinstance(v, bytes):
                v = quote_via(v, safe)
                l.append(k + '=' + v)
            elikiwa isinstance(v, str):
                v = quote_via(v, safe, encoding, errors)
                l.append(k + '=' + v)
            else:
                try:
                    # Is this a sufficient test for sequence-ness?
                    x = len(v)
                except TypeError:
                    # not a sequence
                    v = quote_via(str(v), safe, encoding, errors)
                    l.append(k + '=' + v)
                else:
                    # loop over the sequence
                    for elt in v:
                        ikiwa isinstance(elt, bytes):
                            elt = quote_via(elt, safe)
                        else:
                            elt = quote_via(str(elt), safe, encoding, errors)
                        l.append(k + '=' + elt)
    rudisha '&'.join(l)


eleza to_bytes(url):
    warnings.warn("urllib.parse.to_bytes() is deprecated as of 3.8",
                  DeprecationWarning, stacklevel=2)
    rudisha _to_bytes(url)


eleza _to_bytes(url):
    """to_bytes(u"URL") --> 'URL'."""
    # Most URL schemes require ASCII. If that changes, the conversion
    # can be relaxed.
    # XXX get rid of to_bytes()
    ikiwa isinstance(url, str):
        try:
            url = url.encode("ASCII").decode()
        except UnicodeError:
            raise UnicodeError("URL " + repr(url) +
                               " contains non-ASCII characters")
    rudisha url


eleza unwrap(url):
    """Transform a string like '<URL:scheme://host/path>' into 'scheme://host/path'.

    The string is returned unchanged ikiwa it's not a wrapped URL.
    """
    url = str(url).strip()
    ikiwa url[:1] == '<' and url[-1:] == '>':
        url = url[1:-1].strip()
    ikiwa url[:4] == 'URL:':
        url = url[4:].strip()
    rudisha url


eleza splittype(url):
    warnings.warn("urllib.parse.splittype() is deprecated as of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splittype(url)


_typeprog = None
eleza _splittype(url):
    """splittype('type:opaquestring') --> 'type', 'opaquestring'."""
    global _typeprog
    ikiwa _typeprog is None:
        _typeprog = re.compile('([^/:]+):(.*)', re.DOTALL)

    match = _typeprog.match(url)
    ikiwa match:
        scheme, data = match.groups()
        rudisha scheme.lower(), data
    rudisha None, url


eleza splithost(url):
    warnings.warn("urllib.parse.splithost() is deprecated as of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splithost(url)


_hostprog = None
eleza _splithost(url):
    """splithost('//host[:port]/path') --> 'host[:port]', '/path'."""
    global _hostprog
    ikiwa _hostprog is None:
        _hostprog = re.compile('//([^/#?]*)(.*)', re.DOTALL)

    match = _hostprog.match(url)
    ikiwa match:
        host_port, path = match.groups()
        ikiwa path and path[0] != '/':
            path = '/' + path
        rudisha host_port, path
    rudisha None, url


eleza splituser(host):
    warnings.warn("urllib.parse.splituser() is deprecated as of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splituser(host)


eleza _splituser(host):
    """splituser('user[:passwd]@host[:port]') --> 'user[:passwd]', 'host[:port]'."""
    user, delim, host = host.rpartition('@')
    rudisha (user ikiwa delim else None), host


eleza splitpasswd(user):
    warnings.warn("urllib.parse.splitpasswd() is deprecated as of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splitpasswd(user)


eleza _splitpasswd(user):
    """splitpasswd('user:passwd') -> 'user', 'passwd'."""
    user, delim, passwd = user.partition(':')
    rudisha user, (passwd ikiwa delim else None)


eleza splitport(host):
    warnings.warn("urllib.parse.splitport() is deprecated as of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splitport(host)


# splittag('/path#tag') --> '/path', 'tag'
_portprog = None
eleza _splitport(host):
    """splitport('host:port') --> 'host', 'port'."""
    global _portprog
    ikiwa _portprog is None:
        _portprog = re.compile('(.*):([0-9]*)$', re.DOTALL)

    match = _portprog.match(host)
    ikiwa match:
        host, port = match.groups()
        ikiwa port:
            rudisha host, port
    rudisha host, None


eleza splitnport(host, defport=-1):
    warnings.warn("urllib.parse.splitnport() is deprecated as of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splitnport(host, defport)


eleza _splitnport(host, defport=-1):
    """Split host and port, returning numeric port.
    Return given default port ikiwa no ':' found; defaults to -1.
    Return numerical port ikiwa a valid number are found after ':'.
    Return None ikiwa ':' but not a valid number."""
    host, delim, port = host.rpartition(':')
    ikiwa not delim:
        host = port
    elikiwa port:
        try:
            nport = int(port)
        except ValueError:
            nport = None
        rudisha host, nport
    rudisha host, defport


eleza splitquery(url):
    warnings.warn("urllib.parse.splitquery() is deprecated as of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splitquery(url)


eleza _splitquery(url):
    """splitquery('/path?query') --> '/path', 'query'."""
    path, delim, query = url.rpartition('?')
    ikiwa delim:
        rudisha path, query
    rudisha url, None


eleza splittag(url):
    warnings.warn("urllib.parse.splittag() is deprecated as of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splittag(url)


eleza _splittag(url):
    """splittag('/path#tag') --> '/path', 'tag'."""
    path, delim, tag = url.rpartition('#')
    ikiwa delim:
        rudisha path, tag
    rudisha url, None


eleza splitattr(url):
    warnings.warn("urllib.parse.splitattr() is deprecated as of 3.8, "
                  "use urllib.parse.urlparse() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splitattr(url)


eleza _splitattr(url):
    """splitattr('/path;attr1=value1;attr2=value2;...') ->
        '/path', ['attr1=value1', 'attr2=value2', ...]."""
    words = url.split(';')
    rudisha words[0], words[1:]


eleza splitvalue(attr):
    warnings.warn("urllib.parse.splitvalue() is deprecated as of 3.8, "
                  "use urllib.parse.parse_qsl() instead",
                  DeprecationWarning, stacklevel=2)
    rudisha _splitvalue(attr)


eleza _splitvalue(attr):
    """splitvalue('attr=value') --> 'attr', 'value'."""
    attr, delim, value = attr.partition('=')
    rudisha attr, (value ikiwa delim else None)
