"""Implementation of JSONEncoder
"""
agiza re

jaribu:
    kutoka _json agiza encode_basestring_ascii kama c_encode_basestring_ascii
tatizo ImportError:
    c_encode_basestring_ascii = Tupu
jaribu:
    kutoka _json agiza encode_basestring kama c_encode_basestring
tatizo ImportError:
    c_encode_basestring = Tupu
jaribu:
    kutoka _json agiza make_encoder kama c_make_encoder
tatizo ImportError:
    c_make_encoder = Tupu

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
kila i kwenye range(0x20):
    ESCAPE_DCT.setdefault(chr(i), '\\u{0:04x}'.format(i))
    #ESCAPE_DCT.setdefault(chr(i), '\\u%04x' % (i,))

INFINITY = float('inf')

eleza py_encode_basestring(s):
    """Return a JSON representation of a Python string

    """
    eleza replace(match):
        rudisha ESCAPE_DCT[match.group(0)]
    rudisha '"' + ESCAPE.sub(replace, s) + '"'


encode_basestring = (c_encode_basestring ama py_encode_basestring)


eleza py_encode_basestring_ascii(s):
    """Return an ASCII-only JSON representation of a Python string

    """
    eleza replace(match):
        s = match.group(0)
        jaribu:
            rudisha ESCAPE_DCT[s]
        tatizo KeyError:
            n = ord(s)
            ikiwa n < 0x10000:
                rudisha '\\u{0:04x}'.format(n)
                #rudisha '\\u%04x' % (n,)
            isipokua:
                # surrogate pair
                n -= 0x10000
                s1 = 0xd800 | ((n >> 10) & 0x3ff)
                s2 = 0xdc00 | (n & 0x3ff)
                rudisha '\\u{0:04x}\\u{1:04x}'.format(s1, s2)
    rudisha '"' + ESCAPE_ASCII.sub(replace, s) + '"'


encode_basestring_ascii = (
    c_encode_basestring_ascii ama py_encode_basestring_ascii)

kundi JSONEncoder(object):
    """Extensible JSON <http://json.org> encoder kila Python data structures.

    Supports the following objects na types by default:

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
    | Kweli              | true          |
    +-------------------+---------------+
    | Uongo             | false         |
    +-------------------+---------------+
    | Tupu              | null          |
    +-------------------+---------------+

    To extend this to recognize other objects, subkundi na implement a
    ``.default()`` method ukijumuisha another method that rudishas a serializable
    object kila ``o`` ikiwa possible, otherwise it should call the superclass
    implementation (to ashiria ``TypeError``).

    """
    item_separator = ', '
    key_separator = ': '
    eleza __init__(self, *, skipkeys=Uongo, ensure_ascii=Kweli,
            check_circular=Kweli, allow_nan=Kweli, sort_keys=Uongo,
            indent=Tupu, separators=Tupu, default=Tupu):
        """Constructor kila JSONEncoder, ukijumuisha sensible defaults.

        If skipkeys ni false, then it ni a TypeError to attempt
        encoding of keys that are sio str, int, float ama Tupu.  If
        skipkeys ni Kweli, such items are simply skipped.

        If ensure_ascii ni true, the output ni guaranteed to be str
        objects ukijumuisha all incoming non-ASCII characters escaped.  If
        ensure_ascii ni false, the output can contain non-ASCII characters.

        If check_circular ni true, then lists, dicts, na custom encoded
        objects will be checked kila circular references during encoding to
        prevent an infinite recursion (which would cause an OverflowError).
        Otherwise, no such check takes place.

        If allow_nan ni true, then NaN, Infinity, na -Infinity will be
        encoded kama such.  This behavior ni sio JSON specification compliant,
        but ni consistent ukijumuisha most JavaScript based encoders na decoders.
        Otherwise, it will be a ValueError to encode such floats.

        If sort_keys ni true, then the output of dictionaries will be
        sorted by key; this ni useful kila regression tests to ensure
        that JSON serializations can be compared on a day-to-day basis.

        If indent ni a non-negative integer, then JSON array
        elements na object members will be pretty-printed ukijumuisha that
        indent level.  An indent level of 0 will only insert newlines.
        Tupu ni the most compact representation.

        If specified, separators should be an (item_separator, key_separator)
        tuple.  The default ni (', ', ': ') ikiwa *indent* ni ``Tupu`` na
        (',', ': ') otherwise.  To get the most compact JSON representation,
        you should specify (',', ':') to eliminate whitespace.

        If specified, default ni a function that gets called kila objects
        that can't otherwise be serialized.  It should rudisha a JSON encodable
        version of the object ama ashiria a ``TypeError``.

        """

        self.skipkeys = skipkeys
        self.ensure_ascii = ensure_ascii
        self.check_circular = check_circular
        self.allow_nan = allow_nan
        self.sort_keys = sort_keys
        self.indent = indent
        ikiwa separators ni sio Tupu:
            self.item_separator, self.key_separator = separators
        lasivyo indent ni sio Tupu:
            self.item_separator = ','
        ikiwa default ni sio Tupu:
            self.default = default

    eleza default(self, o):
        """Implement this method kwenye a subkundi such that it rudishas
        a serializable object kila ``o``, ama calls the base implementation
        (to ashiria a ``TypeError``).

        For example, to support arbitrary iterators, you could
        implement default like this::

            eleza default(self, o):
                jaribu:
                    iterable = iter(o)
                tatizo TypeError:
                    pita
                isipokua:
                    rudisha list(iterable)
                # Let the base kundi default method ashiria the TypeError
                rudisha JSONEncoder.default(self, o)

        """
        ashiria TypeError(f'Object of type {o.__class__.__name__} '
                        f'is sio JSON serializable')

    eleza encode(self, o):
        """Return a JSON string representation of a Python data structure.

        >>> kutoka json.encoder agiza JSONEncoder
        >>> JSONEncoder().encode({"foo": ["bar", "baz"]})
        '{"foo": ["bar", "baz"]}'

        """
        # This ni kila extremely simple cases na benchmarks.
        ikiwa isinstance(o, str):
            ikiwa self.ensure_ascii:
                rudisha encode_basestring_ascii(o)
            isipokua:
                rudisha encode_basestring(o)
        # This doesn't pita the iterator directly to ''.join() because the
        # exceptions aren't kama detailed.  The list call should be roughly
        # equivalent to the PySequence_Fast that ''.join() would do.
        chunks = self.iterencode(o, _one_shot=Kweli)
        ikiwa sio isinstance(chunks, (list, tuple)):
            chunks = list(chunks)
        rudisha ''.join(chunks)

    eleza iterencode(self, o, _one_shot=Uongo):
        """Encode the given object na tuma each string
        representation kama available.

        For example::

            kila chunk kwenye JSONEncoder().iterencode(bigobject):
                mysocket.write(chunk)

        """
        ikiwa self.check_circular:
            markers = {}
        isipokua:
            markers = Tupu
        ikiwa self.ensure_ascii:
            _encoder = encode_basestring_ascii
        isipokua:
            _encoder = encode_basestring

        eleza floatstr(o, allow_nan=self.allow_nan,
                _repr=float.__repr__, _inf=INFINITY, _neginf=-INFINITY):
            # Check kila specials.  Note that this type of test ni processor
            # and/or platform-specific, so do tests which don't depend on the
            # internals.

            ikiwa o != o:
                text = 'NaN'
            lasivyo o == _inf:
                text = 'Infinity'
            lasivyo o == _neginf:
                text = '-Infinity'
            isipokua:
                rudisha _repr(o)

            ikiwa sio allow_nan:
                ashiria ValueError(
                    "Out of range float values are sio JSON compliant: " +
                    repr(o))

            rudisha text


        ikiwa (_one_shot na c_make_encoder ni sio Tupu
                na self.indent ni Tupu):
            _iterencode = c_make_encoder(
                markers, self.default, _encoder, self.indent,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, self.allow_nan)
        isipokua:
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

    ikiwa _indent ni sio Tupu na sio isinstance(_indent, str):
        _indent = ' ' * _indent

    eleza _iterencode_list(lst, _current_indent_level):
        ikiwa sio lst:
            tuma '[]'
            rudisha
        ikiwa markers ni sio Tupu:
            markerid = id(lst)
            ikiwa markerid kwenye markers:
                ashiria ValueError("Circular reference detected")
            markers[markerid] = lst
        buf = '['
        ikiwa _indent ni sio Tupu:
            _current_indent_level += 1
            newline_indent = '\n' + _indent * _current_indent_level
            separator = _item_separator + newline_indent
            buf += newline_indent
        isipokua:
            newline_indent = Tupu
            separator = _item_separator
        first = Kweli
        kila value kwenye lst:
            ikiwa first:
                first = Uongo
            isipokua:
                buf = separator
            ikiwa isinstance(value, str):
                tuma buf + _encoder(value)
            lasivyo value ni Tupu:
                tuma buf + 'null'
            lasivyo value ni Kweli:
                tuma buf + 'true'
            lasivyo value ni Uongo:
                tuma buf + 'false'
            lasivyo isinstance(value, int):
                # Subclasses of int/float may override __repr__, but we still
                # want to encode them kama integers/floats kwenye JSON. One example
                # within the standard library ni IntEnum.
                tuma buf + _intstr(value)
            lasivyo isinstance(value, float):
                # see comment above kila int
                tuma buf + _floatstr(value)
            isipokua:
                tuma buf
                ikiwa isinstance(value, (list, tuple)):
                    chunks = _iterencode_list(value, _current_indent_level)
                lasivyo isinstance(value, dict):
                    chunks = _iterencode_dict(value, _current_indent_level)
                isipokua:
                    chunks = _iterencode(value, _current_indent_level)
                tuma kutoka chunks
        ikiwa newline_indent ni sio Tupu:
            _current_indent_level -= 1
            tuma '\n' + _indent * _current_indent_level
        tuma ']'
        ikiwa markers ni sio Tupu:
            toa markers[markerid]

    eleza _iterencode_dict(dct, _current_indent_level):
        ikiwa sio dct:
            tuma '{}'
            rudisha
        ikiwa markers ni sio Tupu:
            markerid = id(dct)
            ikiwa markerid kwenye markers:
                ashiria ValueError("Circular reference detected")
            markers[markerid] = dct
        tuma '{'
        ikiwa _indent ni sio Tupu:
            _current_indent_level += 1
            newline_indent = '\n' + _indent * _current_indent_level
            item_separator = _item_separator + newline_indent
            tuma newline_indent
        isipokua:
            newline_indent = Tupu
            item_separator = _item_separator
        first = Kweli
        ikiwa _sort_keys:
            items = sorted(dct.items())
        isipokua:
            items = dct.items()
        kila key, value kwenye items:
            ikiwa isinstance(key, str):
                pita
            # JavaScript ni weakly typed kila these, so it makes sense to
            # also allow them.  Many encoders seem to do something like this.
            lasivyo isinstance(key, float):
                # see comment kila int/float kwenye _make_iterencode
                key = _floatstr(key)
            lasivyo key ni Kweli:
                key = 'true'
            lasivyo key ni Uongo:
                key = 'false'
            lasivyo key ni Tupu:
                key = 'null'
            lasivyo isinstance(key, int):
                # see comment kila int/float kwenye _make_iterencode
                key = _intstr(key)
            lasivyo _skipkeys:
                endelea
            isipokua:
                ashiria TypeError(f'keys must be str, int, float, bool ama Tupu, '
                                f'not {key.__class__.__name__}')
            ikiwa first:
                first = Uongo
            isipokua:
                tuma item_separator
            tuma _encoder(key)
            tuma _key_separator
            ikiwa isinstance(value, str):
                tuma _encoder(value)
            lasivyo value ni Tupu:
                tuma 'null'
            lasivyo value ni Kweli:
                tuma 'true'
            lasivyo value ni Uongo:
                tuma 'false'
            lasivyo isinstance(value, int):
                # see comment kila int/float kwenye _make_iterencode
                tuma _intstr(value)
            lasivyo isinstance(value, float):
                # see comment kila int/float kwenye _make_iterencode
                tuma _floatstr(value)
            isipokua:
                ikiwa isinstance(value, (list, tuple)):
                    chunks = _iterencode_list(value, _current_indent_level)
                lasivyo isinstance(value, dict):
                    chunks = _iterencode_dict(value, _current_indent_level)
                isipokua:
                    chunks = _iterencode(value, _current_indent_level)
                tuma kutoka chunks
        ikiwa newline_indent ni sio Tupu:
            _current_indent_level -= 1
            tuma '\n' + _indent * _current_indent_level
        tuma '}'
        ikiwa markers ni sio Tupu:
            toa markers[markerid]

    eleza _iterencode(o, _current_indent_level):
        ikiwa isinstance(o, str):
            tuma _encoder(o)
        lasivyo o ni Tupu:
            tuma 'null'
        lasivyo o ni Kweli:
            tuma 'true'
        lasivyo o ni Uongo:
            tuma 'false'
        lasivyo isinstance(o, int):
            # see comment kila int/float kwenye _make_iterencode
            tuma _intstr(o)
        lasivyo isinstance(o, float):
            # see comment kila int/float kwenye _make_iterencode
            tuma _floatstr(o)
        lasivyo isinstance(o, (list, tuple)):
            tuma kutoka _iterencode_list(o, _current_indent_level)
        lasivyo isinstance(o, dict):
            tuma kutoka _iterencode_dict(o, _current_indent_level)
        isipokua:
            ikiwa markers ni sio Tupu:
                markerid = id(o)
                ikiwa markerid kwenye markers:
                    ashiria ValueError("Circular reference detected")
                markers[markerid] = o
            o = _default(o)
            tuma kutoka _iterencode(o, _current_indent_level)
            ikiwa markers ni sio Tupu:
                toa markers[markerid]
    rudisha _iterencode
