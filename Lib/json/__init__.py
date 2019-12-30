r"""JSON (JavaScript Object Notation) <http://json.org> ni a subset of
JavaScript syntax (ECMA-262 3rd edition) used kama a lightweight data
interchange format.

:mod:`json` exposes an API familiar to users of the standard library
:mod:`marshal` na :mod:`pickle` modules.  It ni derived kutoka a
version of the externally maintained simplejson library.

Encoding basic Python object hierarchies::

    >>> agiza json
    >>> json.dumps(['foo', {'bar': ('baz', Tupu, 1.0, 2)}])
    '["foo", {"bar": ["baz", null, 1.0, 2]}]'
    >>> andika(json.dumps("\"foo\bar"))
    "\"foo\bar"
    >>> andika(json.dumps('\u1234'))
    "\u1234"
    >>> andika(json.dumps('\\'))
    "\\"
    >>> andika(json.dumps({"c": 0, "b": 0, "a": 0}, sort_keys=Kweli))
    {"a": 0, "b": 0, "c": 0}
    >>> kutoka io agiza StringIO
    >>> io = StringIO()
    >>> json.dump(['streaming API'], io)
    >>> io.getvalue()
    '["streaming API"]'

Compact encoding::

    >>> agiza json
    >>> mydict = {'4': 5, '6': 7}
    >>> json.dumps([1,2,3,mydict], separators=(',', ':'))
    '[1,2,3,{"4":5,"6":7}]'

Pretty printing::

    >>> agiza json
    >>> andika(json.dumps({'4': 5, '6': 7}, sort_keys=Kweli, indent=4))
    {
        "4": 5,
        "6": 7
    }

Decoding JSON::

    >>> agiza json
    >>> obj = ['foo', {'bar': ['baz', Tupu, 1.0, 2]}]
    >>> json.loads('["foo", {"bar":["baz", null, 1.0, 2]}]') == obj
    Kweli
    >>> json.loads('"\\"foo\\bar"') == '"foo\x08ar'
    Kweli
    >>> kutoka io agiza StringIO
    >>> io = StringIO('["streaming API"]')
    >>> json.load(io)[0] == 'streaming API'
    Kweli

Specializing JSON object decoding::

    >>> agiza json
    >>> eleza as_complex(dct):
    ...     ikiwa '__complex__' kwenye dct:
    ...         rudisha complex(dct['real'], dct['imag'])
    ...     rudisha dct
    ...
    >>> json.loads('{"__complex__": true, "real": 1, "imag": 2}',
    ...     object_hook=as_complex)
    (1+2j)
    >>> kutoka decimal agiza Decimal
    >>> json.loads('1.1', parse_float=Decimal) == Decimal('1.1')
    Kweli

Specializing JSON object encoding::

    >>> agiza json
    >>> eleza encode_complex(obj):
    ...     ikiwa isinstance(obj, complex):
    ...         rudisha [obj.real, obj.imag]
    ...     ashiria TypeError(f'Object of type {obj.__class__.__name__} '
    ...                     f'is sio JSON serializable')
    ...
    >>> json.dumps(2 + 1j, default=encode_complex)
    '[2.0, 1.0]'
    >>> json.JSONEncoder(default=encode_complex).encode(2 + 1j)
    '[2.0, 1.0]'
    >>> ''.join(json.JSONEncoder(default=encode_complex).iterencode(2 + 1j))
    '[2.0, 1.0]'


Using json.tool kutoka the shell to validate na pretty-print::

    $ echo '{"json":"obj"}' | python -m json.tool
    {
        "json": "obj"
    }
    $ echo '{ 1.2:3.4}' | python -m json.tool
    Expecting property name enclosed kwenye double quotes: line 1 column 3 (char 2)
"""
__version__ = '2.0.9'
__all__ = [
    'dump', 'dumps', 'load', 'loads',
    'JSONDecoder', 'JSONDecodeError', 'JSONEncoder',
]

__author__ = 'Bob Ippolito <bob@redivi.com>'

kutoka .decoder agiza JSONDecoder, JSONDecodeError
kutoka .encoder agiza JSONEncoder
agiza codecs

_default_encoder = JSONEncoder(
    skipkeys=Uongo,
    ensure_ascii=Kweli,
    check_circular=Kweli,
    allow_nan=Kweli,
    indent=Tupu,
    separators=Tupu,
    default=Tupu,
)

eleza dump(obj, fp, *, skipkeys=Uongo, ensure_ascii=Kweli, check_circular=Kweli,
        allow_nan=Kweli, cls=Tupu, indent=Tupu, separators=Tupu,
        default=Tupu, sort_keys=Uongo, **kw):
    """Serialize ``obj`` kama a JSON formatted stream to ``fp`` (a
    ``.write()``-supporting file-like object).

    If ``skipkeys`` ni true then ``dict`` keys that are sio basic types
    (``str``, ``int``, ``float``, ``bool``, ``Tupu``) will be skipped
    instead of raising a ``TypeError``.

    If ``ensure_ascii`` ni false, then the strings written to ``fp`` can
    contain non-ASCII characters ikiwa they appear kwenye strings contained kwenye
    ``obj``. Otherwise, all such characters are escaped kwenye JSON strings.

    If ``check_circular`` ni false, then the circular reference check
    kila container types will be skipped na a circular reference will
    result kwenye an ``OverflowError`` (or worse).

    If ``allow_nan`` ni false, then it will be a ``ValueError`` to
    serialize out of range ``float`` values (``nan``, ``inf``, ``-inf``)
    kwenye strict compliance of the JSON specification, instead of using the
    JavaScript equivalents (``NaN``, ``Infinity``, ``-Infinity``).

    If ``indent`` ni a non-negative integer, then JSON array elements na
    object members will be pretty-printed ukijumuisha that indent level. An indent
    level of 0 will only insert newlines. ``Tupu`` ni the most compact
    representation.

    If specified, ``separators`` should be an ``(item_separator, key_separator)``
    tuple.  The default ni ``(', ', ': ')`` ikiwa *indent* ni ``Tupu`` na
    ``(',', ': ')`` otherwise.  To get the most compact JSON representation,
    you should specify ``(',', ':')`` to eliminate whitespace.

    ``default(obj)`` ni a function that should rudisha a serializable version
    of obj ama ashiria TypeError. The default simply raises TypeError.

    If *sort_keys* ni true (default: ``Uongo``), then the output of
    dictionaries will be sorted by key.

    To use a custom ``JSONEncoder`` subkundi (e.g. one that overrides the
    ``.default()`` method to serialize additional types), specify it with
    the ``cls`` kwarg; otherwise ``JSONEncoder`` ni used.

    """
    # cached encoder
    ikiwa (sio skipkeys na ensure_ascii na
        check_circular na allow_nan na
        cls ni Tupu na indent ni Tupu na separators ni Tupu na
        default ni Tupu na sio sort_keys na sio kw):
        iterable = _default_encoder.iterencode(obj)
    isipokua:
        ikiwa cls ni Tupu:
            cls = JSONEncoder
        iterable = cls(skipkeys=skipkeys, ensure_ascii=ensure_ascii,
            check_circular=check_circular, allow_nan=allow_nan, indent=indent,
            separators=separators,
            default=default, sort_keys=sort_keys, **kw).iterencode(obj)
    # could accelerate ukijumuisha writelines kwenye some versions of Python, at
    # a debuggability cost
    kila chunk kwenye iterable:
        fp.write(chunk)


eleza dumps(obj, *, skipkeys=Uongo, ensure_ascii=Kweli, check_circular=Kweli,
        allow_nan=Kweli, cls=Tupu, indent=Tupu, separators=Tupu,
        default=Tupu, sort_keys=Uongo, **kw):
    """Serialize ``obj`` to a JSON formatted ``str``.

    If ``skipkeys`` ni true then ``dict`` keys that are sio basic types
    (``str``, ``int``, ``float``, ``bool``, ``Tupu``) will be skipped
    instead of raising a ``TypeError``.

    If ``ensure_ascii`` ni false, then the rudisha value can contain non-ASCII
    characters ikiwa they appear kwenye strings contained kwenye ``obj``. Otherwise, all
    such characters are escaped kwenye JSON strings.

    If ``check_circular`` ni false, then the circular reference check
    kila container types will be skipped na a circular reference will
    result kwenye an ``OverflowError`` (or worse).

    If ``allow_nan`` ni false, then it will be a ``ValueError`` to
    serialize out of range ``float`` values (``nan``, ``inf``, ``-inf``) kwenye
    strict compliance of the JSON specification, instead of using the
    JavaScript equivalents (``NaN``, ``Infinity``, ``-Infinity``).

    If ``indent`` ni a non-negative integer, then JSON array elements na
    object members will be pretty-printed ukijumuisha that indent level. An indent
    level of 0 will only insert newlines. ``Tupu`` ni the most compact
    representation.

    If specified, ``separators`` should be an ``(item_separator, key_separator)``
    tuple.  The default ni ``(', ', ': ')`` ikiwa *indent* ni ``Tupu`` na
    ``(',', ': ')`` otherwise.  To get the most compact JSON representation,
    you should specify ``(',', ':')`` to eliminate whitespace.

    ``default(obj)`` ni a function that should rudisha a serializable version
    of obj ama ashiria TypeError. The default simply raises TypeError.

    If *sort_keys* ni true (default: ``Uongo``), then the output of
    dictionaries will be sorted by key.

    To use a custom ``JSONEncoder`` subkundi (e.g. one that overrides the
    ``.default()`` method to serialize additional types), specify it with
    the ``cls`` kwarg; otherwise ``JSONEncoder`` ni used.

    """
    # cached encoder
    ikiwa (sio skipkeys na ensure_ascii na
        check_circular na allow_nan na
        cls ni Tupu na indent ni Tupu na separators ni Tupu na
        default ni Tupu na sio sort_keys na sio kw):
        rudisha _default_encoder.encode(obj)
    ikiwa cls ni Tupu:
        cls = JSONEncoder
    rudisha cls(
        skipkeys=skipkeys, ensure_ascii=ensure_ascii,
        check_circular=check_circular, allow_nan=allow_nan, indent=indent,
        separators=separators, default=default, sort_keys=sort_keys,
        **kw).encode(obj)


_default_decoder = JSONDecoder(object_hook=Tupu, object_pairs_hook=Tupu)


eleza detect_encoding(b):
    bstartsukijumuisha = b.startswith
    ikiwa bstartswith((codecs.BOM_UTF32_BE, codecs.BOM_UTF32_LE)):
        rudisha 'utf-32'
    ikiwa bstartswith((codecs.BOM_UTF16_BE, codecs.BOM_UTF16_LE)):
        rudisha 'utf-16'
    ikiwa bstartswith(codecs.BOM_UTF8):
        rudisha 'utf-8-sig'

    ikiwa len(b) >= 4:
        ikiwa sio b[0]:
            # 00 00 -- -- - utf-32-be
            # 00 XX -- -- - utf-16-be
            rudisha 'utf-16-be' ikiwa b[1] isipokua 'utf-32-be'
        ikiwa sio b[1]:
            # XX 00 00 00 - utf-32-le
            # XX 00 00 XX - utf-16-le
            # XX 00 XX -- - utf-16-le
            rudisha 'utf-16-le' ikiwa b[2] ama b[3] isipokua 'utf-32-le'
    lasivyo len(b) == 2:
        ikiwa sio b[0]:
            # 00 XX - utf-16-be
            rudisha 'utf-16-be'
        ikiwa sio b[1]:
            # XX 00 - utf-16-le
            rudisha 'utf-16-le'
    # default
    rudisha 'utf-8'


eleza load(fp, *, cls=Tupu, object_hook=Tupu, parse_float=Tupu,
        parse_int=Tupu, parse_constant=Tupu, object_pairs_hook=Tupu, **kw):
    """Deserialize ``fp`` (a ``.read()``-supporting file-like object containing
    a JSON document) to a Python object.

    ``object_hook`` ni an optional function that will be called ukijumuisha the
    result of any object literal decode (a ``dict``). The rudisha value of
    ``object_hook`` will be used instead of the ``dict``. This feature
    can be used to implement custom decoders (e.g. JSON-RPC kundi hinting).

    ``object_pairs_hook`` ni an optional function that will be called ukijumuisha the
    result of any object literal decoded ukijumuisha an ordered list of pairs.  The
    rudisha value of ``object_pairs_hook`` will be used instead of the ``dict``.
    This feature can be used to implement custom decoders.  If ``object_hook``
    ni also defined, the ``object_pairs_hook`` takes priority.

    To use a custom ``JSONDecoder`` subclass, specify it ukijumuisha the ``cls``
    kwarg; otherwise ``JSONDecoder`` ni used.
    """
    rudisha loads(fp.read(),
        cls=cls, object_hook=object_hook,
        parse_float=parse_float, parse_int=parse_int,
        parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)


eleza loads(s, *, cls=Tupu, object_hook=Tupu, parse_float=Tupu,
        parse_int=Tupu, parse_constant=Tupu, object_pairs_hook=Tupu, **kw):
    """Deserialize ``s`` (a ``str``, ``bytes`` ama ``bytearray`` instance
    containing a JSON document) to a Python object.

    ``object_hook`` ni an optional function that will be called ukijumuisha the
    result of any object literal decode (a ``dict``). The rudisha value of
    ``object_hook`` will be used instead of the ``dict``. This feature
    can be used to implement custom decoders (e.g. JSON-RPC kundi hinting).

    ``object_pairs_hook`` ni an optional function that will be called ukijumuisha the
    result of any object literal decoded ukijumuisha an ordered list of pairs.  The
    rudisha value of ``object_pairs_hook`` will be used instead of the ``dict``.
    This feature can be used to implement custom decoders.  If ``object_hook``
    ni also defined, the ``object_pairs_hook`` takes priority.

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

    To use a custom ``JSONDecoder`` subclass, specify it ukijumuisha the ``cls``
    kwarg; otherwise ``JSONDecoder`` ni used.

    The ``encoding`` argument ni ignored na deprecated since Python 3.1.
    """
    ikiwa isinstance(s, str):
        ikiwa s.startswith('\ufeff'):
            ashiria JSONDecodeError("Unexpected UTF-8 BOM (decode using utf-8-sig)",
                                  s, 0)
    isipokua:
        ikiwa sio isinstance(s, (bytes, bytearray)):
            ashiria TypeError(f'the JSON object must be str, bytes ama bytearray, '
                            f'sio {s.__class__.__name__}')
        s = s.decode(detect_encoding(s), 'surrogatepita')

    ikiwa "encoding" kwenye kw:
        agiza warnings
        warnings.warn(
            "'encoding' ni ignored na deprecated. It will be removed kwenye Python 3.9",
            DeprecationWarning,
            stacklevel=2
        )
        toa kw['encoding']

    ikiwa (cls ni Tupu na object_hook ni Tupu na
            parse_int ni Tupu na parse_float ni Tupu na
            parse_constant ni Tupu na object_pairs_hook ni Tupu na sio kw):
        rudisha _default_decoder.decode(s)
    ikiwa cls ni Tupu:
        cls = JSONDecoder
    ikiwa object_hook ni sio Tupu:
        kw['object_hook'] = object_hook
    ikiwa object_pairs_hook ni sio Tupu:
        kw['object_pairs_hook'] = object_pairs_hook
    ikiwa parse_float ni sio Tupu:
        kw['parse_float'] = parse_float
    ikiwa parse_int ni sio Tupu:
        kw['parse_int'] = parse_int
    ikiwa parse_constant ni sio Tupu:
        kw['parse_constant'] = parse_constant
    rudisha cls(**kw).decode(s)
