"""Implementation of JSONEncoder
"""
agiza re

try:
    kutoka _json agiza encode_basestring_ascii as c_encode_basestring_ascii
except ImportError:
    c_encode_basestring_ascii = None
try:
    kutoka _json agiza encode_basestring as c_encode_basestring
except ImportError:
    c_encode_basestring = None
try:
    kutoka _json agiza make_encoder as c_make_encoder
except ImportError:
    c_make_encoder = None

ESCAPE = re.compile(r'[\x00-\x1f\\"\b\f\n\r\t]')
ESCAPE_ASCII = re.compile(r'([\\"]|[^\ -~])')
HAS_UTF8 = re.compile(b'[\x80-\xff]')
ESCAPE_DCT = {
    '\\': '\\\\',
    '"': '\\"',
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
}
for i in range(0x20):
    ESCAPE_DCT.setdefault(chr(i), '\\u{0:04x}'.format(i))
    #ESCAPE_DCT.setdefault(chr(i), '\\u%04x' % (i,))

INFINITY = float('inf')

eleza py_encode_basestring(s):
    """Return a JSON representation of a Python string

    """
    eleza replace(match):
        rudisha ESCAPE_DCT[match.group(0)]
    rudisha '"' + ESCAPE.sub(replace, s) + '"'


encode_basestring = (c_encode_basestring or py_encode_basestring)


eleza py_encode_basestring_ascii(s):
    """Return an ASCII-only JSON representation of a Python string

    """
    eleza replace(match):
        s = match.group(0)
        try:
            rudisha ESCAPE_DCT[s]
        except KeyError:
            n = ord(s)
            ikiwa n < 0x10000:
                rudisha '\\u{0:04x}'.format(n)
                #rudisha '\\u%04x' % (n,)
            else:
                # surrogate pair
                n -= 0x10000
                s1 = 0xd800 | ((n >> 10) & 0x3ff)
                s2 = 0xdc00 | (n & 0x3ff)
                rudisha '\\u{0:04x}\\u{1:04x}'.format(s1, s2)
    rudisha '"' + ESCAPE_ASCII.sub(replace, s) + '"'


encode_basestring_ascii = (
    c_encode_basestring_ascii or py_encode_basestring_ascii)

kundi JSONEncoder(object):
    """Extensible JSON <http://json.org> encoder for Python data structures.

    Supports the following objects and types by default:

    +-------------------+---------------+
    | Python            | JSON          |
    +===================+===============+
    | dict              | object        |
    +-------------------+---------------+
    | list, tuple       | array         |
    +-------------------+---------------+
    | str               | string        |
    +-------------------+---------------+
    | int, float        | number        |
    +-------------------+---------------+
    | True              | true          |
    +-------------------+---------------+
    | False             | false         |
    +-------------------+---------------+
    | None              | null          |
    +-------------------+---------------+

    To extend this to recognize other objects, subkundi and implement a
    ``.default()`` method with another method that returns a serializable
    object for ``o`` ikiwa possible, otherwise it should call the superclass
    implementation (to raise ``TypeError``).

    """
    item_separator = ', '
    key_separator = ': '
    eleza __init__(self, *, skipkeys=False, ensure_ascii=True,
            check_circular=True, allow_nan=True, sort_keys=False,
            indent=None, separators=None, default=None):
        """Constructor for JSONEncoder, with sensible defaults.

        If skipkeys is false, then it is a TypeError to attempt
        encoding of keys that are not str, int, float or None.  If
        skipkeys is True, such items are simply skipped.

        If ensure_ascii is true, the output is guaranteed to be str
        objects with all incoming non-ASCII characters escaped.  If
        ensure_ascii is false, the output can contain non-ASCII characters.

        If check_circular is true, then lists, dicts, and custom encoded
        objects will be checked for circular references during encoding to
        prevent an infinite recursion (which would cause an OverflowError).
        Otherwise, no such check takes place.

        If allow_nan is true, then NaN, Infinity, and -Infinity will be
        encoded as such.  This behavior is not JSON specification compliant,
        but is consistent with most JavaScript based encoders and decoders.
        Otherwise, it will be a ValueError to encode such floats.

        If sort_keys is true, then the output of dictionaries will be
        sorted by key; this is useful for regression tests to ensure
        that JSON serializations can be compared on a day-to-day basis.

        If indent is a non-negative integer, then JSON array
        elements and object members will be pretty-printed with that
        indent level.  An indent level of 0 will only insert newlines.
        None is the most compact representation.

        If specified, separators should be an (item_separator, key_separator)
        tuple.  The default is (', ', ': ') ikiwa *indent* is ``None`` and
        (',', ': ') otherwise.  To get the most compact JSON representation,
        you should specify (',', ':') to eliminate whitespace.

        If specified, default is a function that gets called for objects
        that can't otherwise be serialized.  It should rudisha a JSON encodable
        version of the object or raise a ``TypeError``.

        """

        self.skipkeys = skipkeys
        self.ensure_ascii = ensure_ascii
        self.check_circular = check_circular
        self.allow_nan = allow_nan
        self.sort_keys = sort_keys
        self.indent = indent
        ikiwa separators is not None:
            self.item_separator, self.key_separator = separators
        elikiwa indent is not None:
            self.item_separator = ','
        ikiwa default is not None:
            self.default = default

    eleza default(self, o):
        """Implement this method in a subkundi such that it returns
        a serializable object for ``o``, or calls the base implementation
        (to raise a ``TypeError``).

        For example, to support arbitrary iterators, you could
        implement default like this::

            eleza default(self, o):
                try:
                    iterable = iter(o)
                except TypeError:
                    pass
                else:
                    rudisha list(iterable)
                # Let the base kundi default method raise the TypeError
                rudisha JSONEncoder.default(self, o)

        """
        raise TypeError(f'Object of type {o.__class__.__name__} '
                        f'is not JSON serializable')

    eleza encode(self, o):
        """Return a JSON string representation of a Python data structure.

        >>> kutoka json.encoder agiza JSONEncoder
        >>> JSONEncoder().encode({"foo": ["bar", "baz"]})
        '{"foo": ["bar", "baz"]}'

        """
        # This is for extremely simple cases and benchmarks.
        ikiwa isinstance(o, str):
            ikiwa self.ensure_ascii:
                rudisha encode_basestring_ascii(o)
            else:
                rudisha encode_basestring(o)
        # This doesn't pass the iterator directly to ''.join() because the
        # exceptions aren't as detailed.  The list call should be roughly
        # equivalent to the PySequence_Fast that ''.join() would do.
        chunks = self.iterencode(o, _one_shot=True)
        ikiwa not isinstance(chunks, (list, tuple)):
            chunks = list(chunks)
        rudisha ''.join(chunks)

    eleza iterencode(self, o, _one_shot=False):
        """Encode the given object and yield each string
        representation as available.

        For example::

            for chunk in JSONEncoder().iterencode(bigobject):
                mysocket.write(chunk)

        """
        ikiwa self.check_circular:
            markers = {}
        else:
            markers = None
        ikiwa self.ensure_ascii:
            _encoder = encode_basestring_ascii
        else:
            _encoder = encode_basestring

        eleza floatstr(o, allow_nan=self.allow_nan,
                _repr=float.__repr__, _inf=INFINITY, _neginf=-INFINITY):
            # Check for specials.  Note that this type of test is processor
            # and/or platform-specific, so do tests which don't depend on the
            # internals.

            ikiwa o != o:
                text = 'NaN'
            elikiwa o == _inf:
                text = 'Infinity'
            elikiwa o == _neginf:
                text = '-Infinity'
            else:
                rudisha _repr(o)

            ikiwa not allow_nan:
                raise ValueError(
                    "Out of range float values are not JSON compliant: " +
                    repr(o))

            rudisha text


        ikiwa (_one_shot and c_make_encoder is not None
                and self.indent is None):
            _iterencode = c_make_encoder(
                markers, self.default, _encoder, self.indent,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, self.allow_nan)
        else:
            _iterencode = _make_iterencode(
                markers, self.default, _encoder, self.indent, floatstr,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, _one_shot)
        rudisha _iterencode(o, 0)

eleza _make_iterencode(markers, _default, _encoder, _indent, _floatstr,
        _key_separator, _item_separator, _sort_keys, _skipkeys, _one_shot,
        ## HACK: hand-optimized bytecode; turn globals into locals
        ValueError=ValueError,
        dict=dict,
        float=float,
        id=id,
        int=int,
        isinstance=isinstance,
        list=list,
        str=str,
        tuple=tuple,
        _intstr=int.__repr__,
    ):

    ikiwa _indent is not None and not isinstance(_indent, str):
        _indent = ' ' * _indent

    eleza _iterencode_list(lst, _current_indent_level):
        ikiwa not lst:
            yield '[]'
            return
        ikiwa markers is not None:
            markerid = id(lst)
            ikiwa markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = lst
        buf = '['
        ikiwa _indent is not None:
            _current_indent_level += 1
            newline_indent = '\n' + _indent * _current_indent_level
            separator = _item_separator + newline_indent
            buf += newline_indent
        else:
            newline_indent = None
            separator = _item_separator
        first = True
        for value in lst:
            ikiwa first:
                first = False
            else:
                buf = separator
            ikiwa isinstance(value, str):
                yield buf + _encoder(value)
            elikiwa value is None:
                yield buf + 'null'
            elikiwa value is True:
                yield buf + 'true'
            elikiwa value is False:
                yield buf + 'false'
            elikiwa isinstance(value, int):
                # Subclasses of int/float may override __repr__, but we still
                # want to encode them as integers/floats in JSON. One example
                # within the standard library is IntEnum.
                yield buf + _intstr(value)
            elikiwa isinstance(value, float):
                # see comment above for int
                yield buf + _floatstr(value)
            else:
                yield buf
                ikiwa isinstance(value, (list, tuple)):
                    chunks = _iterencode_list(value, _current_indent_level)
                elikiwa isinstance(value, dict):
                    chunks = _iterencode_dict(value, _current_indent_level)
                else:
                    chunks = _iterencode(value, _current_indent_level)
                yield kutoka chunks
        ikiwa newline_indent is not None:
            _current_indent_level -= 1
            yield '\n' + _indent * _current_indent_level
        yield ']'
        ikiwa markers is not None:
            del markers[markerid]

    eleza _iterencode_dict(dct, _current_indent_level):
        ikiwa not dct:
            yield '{}'
            return
        ikiwa markers is not None:
            markerid = id(dct)
            ikiwa markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = dct
        yield '{'
        ikiwa _indent is not None:
            _current_indent_level += 1
            newline_indent = '\n' + _indent * _current_indent_level
            item_separator = _item_separator + newline_indent
            yield newline_indent
        else:
            newline_indent = None
            item_separator = _item_separator
        first = True
        ikiwa _sort_keys:
            items = sorted(dct.items())
        else:
            items = dct.items()
        for key, value in items:
            ikiwa isinstance(key, str):
                pass
            # JavaScript is weakly typed for these, so it makes sense to
            # also allow them.  Many encoders seem to do something like this.
            elikiwa isinstance(key, float):
                # see comment for int/float in _make_iterencode
                key = _floatstr(key)
            elikiwa key is True:
                key = 'true'
            elikiwa key is False:
                key = 'false'
            elikiwa key is None:
                key = 'null'
            elikiwa isinstance(key, int):
                # see comment for int/float in _make_iterencode
                key = _intstr(key)
            elikiwa _skipkeys:
                continue
            else:
                raise TypeError(f'keys must be str, int, float, bool or None, '
                                f'not {key.__class__.__name__}')
            ikiwa first:
                first = False
            else:
                yield item_separator
            yield _encoder(key)
            yield _key_separator
            ikiwa isinstance(value, str):
                yield _encoder(value)
            elikiwa value is None:
                yield 'null'
            elikiwa value is True:
                yield 'true'
            elikiwa value is False:
                yield 'false'
            elikiwa isinstance(value, int):
                # see comment for int/float in _make_iterencode
                yield _intstr(value)
            elikiwa isinstance(value, float):
                # see comment for int/float in _make_iterencode
                yield _floatstr(value)
            else:
                ikiwa isinstance(value, (list, tuple)):
                    chunks = _iterencode_list(value, _current_indent_level)
                elikiwa isinstance(value, dict):
                    chunks = _iterencode_dict(value, _current_indent_level)
                else:
                    chunks = _iterencode(value, _current_indent_level)
                yield kutoka chunks
        ikiwa newline_indent is not None:
            _current_indent_level -= 1
            yield '\n' + _indent * _current_indent_level
        yield '}'
        ikiwa markers is not None:
            del markers[markerid]

    eleza _iterencode(o, _current_indent_level):
        ikiwa isinstance(o, str):
            yield _encoder(o)
        elikiwa o is None:
            yield 'null'
        elikiwa o is True:
            yield 'true'
        elikiwa o is False:
            yield 'false'
        elikiwa isinstance(o, int):
            # see comment for int/float in _make_iterencode
            yield _intstr(o)
        elikiwa isinstance(o, float):
            # see comment for int/float in _make_iterencode
            yield _floatstr(o)
        elikiwa isinstance(o, (list, tuple)):
            yield kutoka _iterencode_list(o, _current_indent_level)
        elikiwa isinstance(o, dict):
            yield kutoka _iterencode_dict(o, _current_indent_level)
        else:
            ikiwa markers is not None:
                markerid = id(o)
                ikiwa markerid in markers:
                    raise ValueError("Circular reference detected")
                markers[markerid] = o
            o = _default(o)
            yield kutoka _iterencode(o, _current_indent_level)
            ikiwa markers is not None:
                del markers[markerid]
    rudisha _iterencode
