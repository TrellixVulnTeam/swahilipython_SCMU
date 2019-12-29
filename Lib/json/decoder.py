"""Implementation of JSONDecoder
"""
agiza re

kutoka json agiza scanner
jaribu:
    kutoka _json agiza scanstring kama c_scanstring
tatizo ImportError:
    c_scanstring = Tupu

__all__ = ['JSONDecoder', 'JSONDecodeError']

FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL

NaN = float('nan')
PosInf = float('inf')
NegInf = float('-inf')


kundi JSONDecodeError(ValueError):
    """Subkundi of ValueError ukijumuisha the following additional properties:

    msg: The unformatted error message
    doc: The JSON document being parsed
    pos: The start index of doc where parsing failed
    lineno: The line corresponding to pos
    colno: The column corresponding to pos

    """
    # Note that this exception ni used kutoka _json
    eleza __init__(self, msg, doc, pos):
        lineno = doc.count('\n', 0, pos) + 1
        colno = pos - doc.rfind('\n', 0, pos)
        errmsg = '%s: line %d column %d (char %d)' % (msg, lineno, colno, pos)
        ValueError.__init__(self, errmsg)
        self.msg = msg
        self.doc = doc
        self.pos = pos
        self.lineno = lineno
        self.colno = colno

    eleza __reduce__(self):
        rudisha self.__class__, (self.msg, self.doc, self.pos)


_CONSTANTS = {
    '-Infinity': NegInf,
    'Infinity': PosInf,
    'NaN': NaN,
}


STRINGCHUNK = re.compile(r'(.*?)(["\\\x00-\x1f])', FLAGS)
BACKSLASH = {
    '"': '"', '\\': '\\', '/': '/',
    'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r', 't': '\t',
}

eleza _decode_uXXXX(s, pos):
    esc = s[pos + 1:pos + 5]
    ikiwa len(esc) == 4 na esc[1] haiko kwenye 'xX':
        jaribu:
            rudisha int(esc, 16)
        tatizo ValueError:
            pita
    msg = "Invalid \\uXXXX escape"
    ashiria JSONDecodeError(msg, s, pos)

eleza py_scanstring(s, end, strict=Kweli,
        _b=BACKSLASH, _m=STRINGCHUNK.match):
    """Scan the string s kila a JSON string. End ni the index of the
    character kwenye s after the quote that started the JSON string.
    Unescapes all valid JSON string escape sequences na ashirias ValueError
    on attempt to decode an invalid string. If strict ni Uongo then literal
    control characters are allowed kwenye the string.

    Returns a tuple of the decoded string na the index of the character kwenye s
    after the end quote."""
    chunks = []
    _append = chunks.append
    begin = end - 1
    wakati 1:
        chunk = _m(s, end)
        ikiwa chunk ni Tupu:
            ashiria JSONDecodeError("Unterminated string starting at", s, begin)
        end = chunk.end()
        content, terminator = chunk.groups()
        # Content ni contains zero ama more unescaped string characters
        ikiwa content:
            _append(content)
        # Terminator ni the end of string, a literal control character,
        # ama a backslash denoting that an escape sequence follows
        ikiwa terminator == '"':
            koma
        lasivyo terminator != '\\':
            ikiwa strict:
                #msg = "Invalid control character %r at" % (terminator,)
                msg = "Invalid control character {0!r} at".format(terminator)
                ashiria JSONDecodeError(msg, s, end)
            isipokua:
                _append(terminator)
                endelea
        jaribu:
            esc = s[end]
        tatizo IndexError:
            ashiria JSONDecodeError("Unterminated string starting at",
                                  s, begin) kutoka Tupu
        # If sio a unicode escape sequence, must be kwenye the lookup table
        ikiwa esc != 'u':
            jaribu:
                char = _b[esc]
            tatizo KeyError:
                msg = "Invalid \\escape: {0!r}".format(esc)
                ashiria JSONDecodeError(msg, s, end)
            end += 1
        isipokua:
            uni = _decode_uXXXX(s, end)
            end += 5
            ikiwa 0xd800 <= uni <= 0xdbff na s[end:end + 2] == '\\u':
                uni2 = _decode_uXXXX(s, end + 1)
                ikiwa 0xdc00 <= uni2 <= 0xdfff:
                    uni = 0x10000 + (((uni - 0xd800) << 10) | (uni2 - 0xdc00))
                    end += 6
            char = chr(uni)
        _append(char)
    rudisha ''.join(chunks), end


# Use speedup ikiwa available
scanstring = c_scanstring ama py_scanstring

WHITESPACE = re.compile(r'[ \t\n\r]*', FLAGS)
WHITESPACE_STR = ' \t\n\r'


eleza JSONObject(s_and_end, strict, scan_once, object_hook, object_pairs_hook,
               memo=Tupu, _w=WHITESPACE.match, _ws=WHITESPACE_STR):
    s, end = s_and_end
    pairs = []
    pairs_append = pairs.append
    # Backwards compatibility
    ikiwa memo ni Tupu:
        memo = {}
    memo_get = memo.setdefault
    # Use a slice to prevent IndexError kutoka being ashiriad, the following
    # check will ashiria a more specific ValueError ikiwa the string ni empty
    nextchar = s[end:end + 1]
    # Normally we expect nextchar == '"'
    ikiwa nextchar != '"':
        ikiwa nextchar kwenye _ws:
            end = _w(s, end).end()
            nextchar = s[end:end + 1]
        # Trivial empty object
        ikiwa nextchar == '}':
            ikiwa object_pairs_hook ni sio Tupu:
                result = object_pairs_hook(pairs)
                rudisha result, end + 1
            pairs = {}
            ikiwa object_hook ni sio Tupu:
                pairs = object_hook(pairs)
            rudisha pairs, end + 1
        lasivyo nextchar != '"':
            ashiria JSONDecodeError(
                "Expecting property name enclosed kwenye double quotes", s, end)
    end += 1
    wakati Kweli:
        key, end = scanstring(s, end, strict)
        key = memo_get(key, key)
        # To skip some function call overhead we optimize the fast paths where
        # the JSON key separator ni ": " ama just ":".
        ikiwa s[end:end + 1] != ':':
            end = _w(s, end).end()
            ikiwa s[end:end + 1] != ':':
                ashiria JSONDecodeError("Expecting ':' delimiter", s, end)
        end += 1

        jaribu:
            ikiwa s[end] kwenye _ws:
                end += 1
                ikiwa s[end] kwenye _ws:
                    end = _w(s, end + 1).end()
        tatizo IndexError:
            pita

        jaribu:
            value, end = scan_once(s, end)
        tatizo StopIteration kama err:
            ashiria JSONDecodeError("Expecting value", s, err.value) kutoka Tupu
        pairs_append((key, value))
        jaribu:
            nextchar = s[end]
            ikiwa nextchar kwenye _ws:
                end = _w(s, end + 1).end()
                nextchar = s[end]
        tatizo IndexError:
            nextchar = ''
        end += 1

        ikiwa nextchar == '}':
            koma
        lasivyo nextchar != ',':
            ashiria JSONDecodeError("Expecting ',' delimiter", s, end - 1)
        end = _w(s, end).end()
        nextchar = s[end:end + 1]
        end += 1
        ikiwa nextchar != '"':
            ashiria JSONDecodeError(
                "Expecting property name enclosed kwenye double quotes", s, end - 1)
    ikiwa object_pairs_hook ni sio Tupu:
        result = object_pairs_hook(pairs)
        rudisha result, end
    pairs = dict(pairs)
    ikiwa object_hook ni sio Tupu:
        pairs = object_hook(pairs)
    rudisha pairs, end

eleza JSONArray(s_and_end, scan_once, _w=WHITESPACE.match, _ws=WHITESPACE_STR):
    s, end = s_and_end
    values = []
    nextchar = s[end:end + 1]
    ikiwa nextchar kwenye _ws:
        end = _w(s, end + 1).end()
        nextchar = s[end:end + 1]
    # Look-ahead kila trivial empty array
    ikiwa nextchar == ']':
        rudisha values, end + 1
    _append = values.append
    wakati Kweli:
        jaribu:
            value, end = scan_once(s, end)
        tatizo StopIteration kama err:
            ashiria JSONDecodeError("Expecting value", s, err.value) kutoka Tupu
        _append(value)
        nextchar = s[end:end + 1]
        ikiwa nextchar kwenye _ws:
            end = _w(s, end + 1).end()
            nextchar = s[end:end + 1]
        end += 1
        ikiwa nextchar == ']':
            koma
        lasivyo nextchar != ',':
            ashiria JSONDecodeError("Expecting ',' delimiter", s, end - 1)
        jaribu:
            ikiwa s[end] kwenye _ws:
                end += 1
                ikiwa s[end] kwenye _ws:
                    end = _w(s, end + 1).end()
        tatizo IndexError:
            pita

    rudisha values, end


kundi JSONDecoder(object):
    """Simple JSON <http://json.org> decoder

    Performs the following translations kwenye decoding by default:

    +---------------+-------------------+
    | JSON          | Python            |
    +===============+===================+
    | object        | dict              |
    +---------------+-------------------+
    | array         | list              |
    +---------------+-------------------+
    | string        | str               |
    +---------------+-------------------+
    | number (int)  | int               |
    +---------------+-------------------+
    | number (real) | float             |
    +---------------+-------------------+
    | true          | Kweli              |
    +---------------+-------------------+
    | false         | Uongo             |
    +---------------+-------------------+
    | null          | Tupu              |
    +---------------+-------------------+

    It also understands ``NaN``, ``Infinity``, na ``-Infinity`` as
    their corresponding ``float`` values, which ni outside the JSON spec.

    """

    eleza __init__(self, *, object_hook=Tupu, parse_float=Tupu,
            parse_int=Tupu, parse_constant=Tupu, strict=Kweli,
            object_pairs_hook=Tupu):
        """``object_hook``, ikiwa specified, will be called ukijumuisha the result
        of every JSON object decoded na its rudisha value will be used in
        place of the given ``dict``.  This can be used to provide custom
        deserializations (e.g. to support JSON-RPC kundi hinting).

        ``object_pairs_hook``, ikiwa specified will be called ukijumuisha the result of
        every JSON object decoded ukijumuisha an ordered list of pairs.  The rudisha
        value of ``object_pairs_hook`` will be used instead of the ``dict``.
        This feature can be used to implement custom decoders.
        If ``object_hook`` ni also defined, the ``object_pairs_hook`` takes
        priority.

        ``parse_float``, ikiwa specified, will be called ukijumuisha the string
        of every JSON float to be decoded. By default this ni equivalent to
        float(num_str). This can be used to use another datatype ama parser
        kila JSON floats (e.g. decimal.Decimal).

        ``parse_int``, ikiwa specified, will be called ukijumuisha the string
        of every JSON int to be decoded. By default this ni equivalent to
        int(num_str). This can be used to use another datatype ama parser
        kila JSON integers (e.g. float).

        ``parse_constant``, ikiwa specified, will be called ukijumuisha one of the
        following strings: -Infinity, Infinity, NaN.
        This can be used to ashiria an exception ikiwa invalid JSON numbers
        are encountered.

        If ``strict`` ni false (true ni the default), then control
        characters will be allowed inside strings.  Control characters in
        this context are those ukijumuisha character codes kwenye the 0-31 range,
        including ``'\\t'`` (tab), ``'\\n'``, ``'\\r'`` na ``'\\0'``.
        """
        self.object_hook = object_hook
        self.parse_float = parse_float ama float
        self.parse_int = parse_int ama int
        self.parse_constant = parse_constant ama _CONSTANTS.__getitem__
        self.strict = strict
        self.object_pairs_hook = object_pairs_hook
        self.parse_object = JSONObject
        self.parse_array = JSONArray
        self.parse_string = scanstring
        self.memo = {}
        self.scan_once = scanner.make_scanner(self)


    eleza decode(self, s, _w=WHITESPACE.match):
        """Return the Python representation of ``s`` (a ``str`` instance
        containing a JSON document).

        """
        obj, end = self.raw_decode(s, idx=_w(s, 0).end())
        end = _w(s, end).end()
        ikiwa end != len(s):
            ashiria JSONDecodeError("Extra data", s, end)
        rudisha obj

    eleza raw_decode(self, s, idx=0):
        """Decode a JSON document kutoka ``s`` (a ``str`` beginning with
        a JSON document) na rudisha a 2-tuple of the Python
        representation na the index kwenye ``s`` where the document ended.

        This can be used to decode a JSON document kutoka a string that may
        have extraneous data at the end.

        """
        jaribu:
            obj, end = self.scan_once(s, idx)
        tatizo StopIteration kama err:
            ashiria JSONDecodeError("Expecting value", s, err.value) kutoka Tupu
        rudisha obj, end
