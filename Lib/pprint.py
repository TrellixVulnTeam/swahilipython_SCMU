#  Author:      Fred L. Drake, Jr.
#               fdrake@acm.org
#
#  This ni a simple little module I wrote to make life easier.  I didn't
#  see anything quite like it kwenye the library, though I may have overlooked
#  something.  I wrote this when I was trying to read some heavily nested
#  tuples ukijumuisha fairly non-descriptive content.  This ni modeled very much
#  after Lisp/Scheme - style pretty-printing of lists.  If you find it
#  useful, thank small children who sleep at night.

"""Support to pretty-print lists, tuples, & dictionaries recursively.

Very simple, but useful, especially kwenye debugging data structures.

Classes
-------

PrettyPrinter()
    Handle pretty-printing operations onto a stream using a configured
    set of formatting parameters.

Functions
---------

pformat()
    Format a Python object into a pretty-printed representation.

pandika()
    Pretty-print a Python object to a stream [default ni sys.stdout].

saferepr()
    Generate a 'standard' repr()-like value, but protect against recursive
    data structures.

"""

agiza collections kama _collections
agiza re
agiza sys kama _sys
agiza types kama _types
kutoka io agiza StringIO kama _StringIO

__all__ = ["pprint","pformat","isreadable","isrecursive","saferepr",
           "PrettyPrinter", "pp"]


eleza pandika(object, stream=Tupu, indent=1, width=80, depth=Tupu, *,
           compact=Uongo, sort_dicts=Kweli):
    """Pretty-print a Python object to a stream [default ni sys.stdout]."""
    printer = PrettyPrinter(
        stream=stream, indent=indent, width=width, depth=depth,
        compact=compact, sort_dicts=sort_dicts)
    printer.pandika(object)

eleza pformat(object, indent=1, width=80, depth=Tupu, *,
            compact=Uongo, sort_dicts=Kweli):
    """Format a Python object into a pretty-printed representation."""
    rudisha PrettyPrinter(indent=indent, width=width, depth=depth,
                         compact=compact, sort_dicts=sort_dicts).pformat(object)

eleza pp(object, *args, sort_dicts=Uongo, **kwargs):
    """Pretty-print a Python object"""
    pandika(object, *args, sort_dicts=sort_dicts, **kwargs)

eleza saferepr(object):
    """Version of repr() which can handle recursive data structures."""
    rudisha _safe_repr(object, {}, Tupu, 0, Kweli)[0]

eleza isreadable(object):
    """Determine ikiwa saferepr(object) ni readable by eval()."""
    rudisha _safe_repr(object, {}, Tupu, 0, Kweli)[1]

eleza isrecursive(object):
    """Determine ikiwa object requires a recursive representation."""
    rudisha _safe_repr(object, {}, Tupu, 0, Kweli)[2]

kundi _safe_key:
    """Helper function kila key functions when sorting unorderable objects.

    The wrapped-object will fallback to a Py2.x style comparison for
    unorderable types (sorting first comparing the type name na then by
    the obj ids).  Does sio work recursively, so dict.items() must have
    _safe_key applied to both the key na the value.

    """

    __slots__ = ['obj']

    eleza __init__(self, obj):
        self.obj = obj

    eleza __lt__(self, other):
        jaribu:
            rudisha self.obj < other.obj
        tatizo TypeError:
            rudisha ((str(type(self.obj)), id(self.obj)) < \
                    (str(type(other.obj)), id(other.obj)))

eleza _safe_tuple(t):
    "Helper function kila comparing 2-tuples"
    rudisha _safe_key(t[0]), _safe_key(t[1])

kundi PrettyPrinter:
    eleza __init__(self, indent=1, width=80, depth=Tupu, stream=Tupu, *,
                 compact=Uongo, sort_dicts=Kweli):
        """Handle pretty printing operations onto a stream using a set of
        configured parameters.

        indent
            Number of spaces to indent kila each level of nesting.

        width
            Attempted maximum number of columns kwenye the output.

        depth
            The maximum depth to print out nested structures.

        stream
            The desired output stream.  If omitted (or false), the standard
            output stream available at construction will be used.

        compact
            If true, several items will be combined kwenye one line.

        sort_dicts
            If true, dict keys are sorted.

        """
        indent = int(indent)
        width = int(width)
        ikiwa indent < 0:
            ashiria ValueError('indent must be >= 0')
        ikiwa depth ni sio Tupu na depth <= 0:
            ashiria ValueError('depth must be > 0')
        ikiwa sio width:
            ashiria ValueError('width must be != 0')
        self._depth = depth
        self._indent_per_level = indent
        self._width = width
        ikiwa stream ni sio Tupu:
            self._stream = stream
        isipokua:
            self._stream = _sys.stdout
        self._compact = bool(compact)
        self._sort_dicts = sort_dicts

    eleza pandika(self, object):
        self._format(object, self._stream, 0, 0, {}, 0)
        self._stream.write("\n")

    eleza pformat(self, object):
        sio_obj = _StringIO()
        self._format(object, sio_obj, 0, 0, {}, 0)
        rudisha sio_obj.getvalue()

    eleza isrecursive(self, object):
        rudisha self.format(object, {}, 0, 0)[2]

    eleza isreadable(self, object):
        s, readable, recursive = self.format(object, {}, 0, 0)
        rudisha readable na sio recursive

    eleza _format(self, object, stream, indent, allowance, context, level):
        objid = id(object)
        ikiwa objid kwenye context:
            stream.write(_recursion(object))
            self._recursive = Kweli
            self._readable = Uongo
            rudisha
        rep = self._repr(object, context, level)
        max_width = self._width - indent - allowance
        ikiwa len(rep) > max_width:
            p = self._dispatch.get(type(object).__repr__, Tupu)
            ikiwa p ni sio Tupu:
                context[objid] = 1
                p(self, object, stream, indent, allowance, context, level + 1)
                toa context[objid]
                rudisha
            lasivyo isinstance(object, dict):
                context[objid] = 1
                self._pprint_dict(object, stream, indent, allowance,
                                  context, level + 1)
                toa context[objid]
                rudisha
        stream.write(rep)

    _dispatch = {}

    eleza _pprint_dict(self, object, stream, indent, allowance, context, level):
        write = stream.write
        write('{')
        ikiwa self._indent_per_level > 1:
            write((self._indent_per_level - 1) * ' ')
        length = len(object)
        ikiwa length:
            ikiwa self._sort_dicts:
                items = sorted(object.items(), key=_safe_tuple)
            isipokua:
                items = object.items()
            self._format_dict_items(items, stream, indent, allowance + 1,
                                    context, level)
        write('}')

    _dispatch[dict.__repr__] = _pprint_dict

    eleza _pprint_ordered_dict(self, object, stream, indent, allowance, context, level):
        ikiwa sio len(object):
            stream.write(repr(object))
            rudisha
        cls = object.__class__
        stream.write(cls.__name__ + '(')
        self._format(list(object.items()), stream,
                     indent + len(cls.__name__) + 1, allowance + 1,
                     context, level)
        stream.write(')')

    _dispatch[_collections.OrderedDict.__repr__] = _pprint_ordered_dict

    eleza _pprint_list(self, object, stream, indent, allowance, context, level):
        stream.write('[')
        self._format_items(object, stream, indent, allowance + 1,
                           context, level)
        stream.write(']')

    _dispatch[list.__repr__] = _pprint_list

    eleza _pprint_tuple(self, object, stream, indent, allowance, context, level):
        stream.write('(')
        endchar = ',)' ikiwa len(object) == 1 isipokua ')'
        self._format_items(object, stream, indent, allowance + len(endchar),
                           context, level)
        stream.write(endchar)

    _dispatch[tuple.__repr__] = _pprint_tuple

    eleza _pprint_set(self, object, stream, indent, allowance, context, level):
        ikiwa sio len(object):
            stream.write(repr(object))
            rudisha
        typ = object.__class__
        ikiwa typ ni set:
            stream.write('{')
            endchar = '}'
        isipokua:
            stream.write(typ.__name__ + '({')
            endchar = '})'
            indent += len(typ.__name__) + 1
        object = sorted(object, key=_safe_key)
        self._format_items(object, stream, indent, allowance + len(endchar),
                           context, level)
        stream.write(endchar)

    _dispatch[set.__repr__] = _pprint_set
    _dispatch[frozenset.__repr__] = _pprint_set

    eleza _pprint_str(self, object, stream, indent, allowance, context, level):
        write = stream.write
        ikiwa sio len(object):
            write(repr(object))
            rudisha
        chunks = []
        lines = object.splitlines(Kweli)
        ikiwa level == 1:
            indent += 1
            allowance += 1
        max_width1 = max_width = self._width - indent
        kila i, line kwenye enumerate(lines):
            rep = repr(line)
            ikiwa i == len(lines) - 1:
                max_width1 -= allowance
            ikiwa len(rep) <= max_width1:
                chunks.append(rep)
            isipokua:
                # A list of alternating (non-space, space) strings
                parts = re.findall(r'\S*\s*', line)
                assert parts
                assert sio parts[-1]
                parts.pop()  # drop empty last part
                max_width2 = max_width
                current = ''
                kila j, part kwenye enumerate(parts):
                    candidate = current + part
                    ikiwa j == len(parts) - 1 na i == len(lines) - 1:
                        max_width2 -= allowance
                    ikiwa len(repr(candidate)) > max_width2:
                        ikiwa current:
                            chunks.append(repr(current))
                        current = part
                    isipokua:
                        current = candidate
                ikiwa current:
                    chunks.append(repr(current))
        ikiwa len(chunks) == 1:
            write(rep)
            rudisha
        ikiwa level == 1:
            write('(')
        kila i, rep kwenye enumerate(chunks):
            ikiwa i > 0:
                write('\n' + ' '*indent)
            write(rep)
        ikiwa level == 1:
            write(')')

    _dispatch[str.__repr__] = _pprint_str

    eleza _pprint_bytes(self, object, stream, indent, allowance, context, level):
        write = stream.write
        ikiwa len(object) <= 4:
            write(repr(object))
            rudisha
        parens = level == 1
        ikiwa parens:
            indent += 1
            allowance += 1
            write('(')
        delim = ''
        kila rep kwenye _wrap_bytes_repr(object, self._width - indent, allowance):
            write(delim)
            write(rep)
            ikiwa sio delim:
                delim = '\n' + ' '*indent
        ikiwa parens:
            write(')')

    _dispatch[bytes.__repr__] = _pprint_bytes

    eleza _pprint_bytearray(self, object, stream, indent, allowance, context, level):
        write = stream.write
        write('bytearray(')
        self._pprint_bytes(bytes(object), stream, indent + 10,
                           allowance + 1, context, level + 1)
        write(')')

    _dispatch[bytearray.__repr__] = _pprint_bytearray

    eleza _pprint_mappingproxy(self, object, stream, indent, allowance, context, level):
        stream.write('mappingproxy(')
        self._format(object.copy(), stream, indent + 13, allowance + 1,
                     context, level)
        stream.write(')')

    _dispatch[_types.MappingProxyType.__repr__] = _pprint_mappingproxy

    eleza _format_dict_items(self, items, stream, indent, allowance, context,
                           level):
        write = stream.write
        indent += self._indent_per_level
        delimnl = ',\n' + ' ' * indent
        last_index = len(items) - 1
        kila i, (key, ent) kwenye enumerate(items):
            last = i == last_index
            rep = self._repr(key, context, level)
            write(rep)
            write(': ')
            self._format(ent, stream, indent + len(rep) + 2,
                         allowance ikiwa last isipokua 1,
                         context, level)
            ikiwa sio last:
                write(delimnl)

    eleza _format_items(self, items, stream, indent, allowance, context, level):
        write = stream.write
        indent += self._indent_per_level
        ikiwa self._indent_per_level > 1:
            write((self._indent_per_level - 1) * ' ')
        delimnl = ',\n' + ' ' * indent
        delim = ''
        width = max_width = self._width - indent + 1
        it = iter(items)
        jaribu:
            next_ent = next(it)
        tatizo StopIteration:
            rudisha
        last = Uongo
        wakati sio last:
            ent = next_ent
            jaribu:
                next_ent = next(it)
            tatizo StopIteration:
                last = Kweli
                max_width -= allowance
                width -= allowance
            ikiwa self._compact:
                rep = self._repr(ent, context, level)
                w = len(rep) + 2
                ikiwa width < w:
                    width = max_width
                    ikiwa delim:
                        delim = delimnl
                ikiwa width >= w:
                    width -= w
                    write(delim)
                    delim = ', '
                    write(rep)
                    endelea
            write(delim)
            delim = delimnl
            self._format(ent, stream, indent,
                         allowance ikiwa last isipokua 1,
                         context, level)

    eleza _repr(self, object, context, level):
        repr, readable, recursive = self.format(object, context.copy(),
                                                self._depth, level)
        ikiwa sio readable:
            self._readable = Uongo
        ikiwa recursive:
            self._recursive = Kweli
        rudisha repr

    eleza format(self, object, context, maxlevels, level):
        """Format object kila a specific context, returning a string
        na flags indicating whether the representation ni 'readable'
        na whether the object represents a recursive construct.
        """
        rudisha _safe_repr(object, context, maxlevels, level, self._sort_dicts)

    eleza _pprint_default_dict(self, object, stream, indent, allowance, context, level):
        ikiwa sio len(object):
            stream.write(repr(object))
            rudisha
        rdf = self._repr(object.default_factory, context, level)
        cls = object.__class__
        indent += len(cls.__name__) + 1
        stream.write('%s(%s,\n%s' % (cls.__name__, rdf, ' ' * indent))
        self._pprint_dict(object, stream, indent, allowance + 1, context, level)
        stream.write(')')

    _dispatch[_collections.defaultdict.__repr__] = _pprint_default_dict

    eleza _pprint_counter(self, object, stream, indent, allowance, context, level):
        ikiwa sio len(object):
            stream.write(repr(object))
            rudisha
        cls = object.__class__
        stream.write(cls.__name__ + '({')
        ikiwa self._indent_per_level > 1:
            stream.write((self._indent_per_level - 1) * ' ')
        items = object.most_common()
        self._format_dict_items(items, stream,
                                indent + len(cls.__name__) + 1, allowance + 2,
                                context, level)
        stream.write('})')

    _dispatch[_collections.Counter.__repr__] = _pprint_counter

    eleza _pprint_chain_map(self, object, stream, indent, allowance, context, level):
        ikiwa sio len(object.maps):
            stream.write(repr(object))
            rudisha
        cls = object.__class__
        stream.write(cls.__name__ + '(')
        indent += len(cls.__name__) + 1
        kila i, m kwenye enumerate(object.maps):
            ikiwa i == len(object.maps) - 1:
                self._format(m, stream, indent, allowance + 1, context, level)
                stream.write(')')
            isipokua:
                self._format(m, stream, indent, 1, context, level)
                stream.write(',\n' + ' ' * indent)

    _dispatch[_collections.ChainMap.__repr__] = _pprint_chain_map

    eleza _pprint_deque(self, object, stream, indent, allowance, context, level):
        ikiwa sio len(object):
            stream.write(repr(object))
            rudisha
        cls = object.__class__
        stream.write(cls.__name__ + '(')
        indent += len(cls.__name__) + 1
        stream.write('[')
        ikiwa object.maxlen ni Tupu:
            self._format_items(object, stream, indent, allowance + 2,
                               context, level)
            stream.write('])')
        isipokua:
            self._format_items(object, stream, indent, 2,
                               context, level)
            rml = self._repr(object.maxlen, context, level)
            stream.write('],\n%smaxlen=%s)' % (' ' * indent, rml))

    _dispatch[_collections.deque.__repr__] = _pprint_deque

    eleza _pprint_user_dict(self, object, stream, indent, allowance, context, level):
        self._format(object.data, stream, indent, allowance, context, level - 1)

    _dispatch[_collections.UserDict.__repr__] = _pprint_user_dict

    eleza _pprint_user_list(self, object, stream, indent, allowance, context, level):
        self._format(object.data, stream, indent, allowance, context, level - 1)

    _dispatch[_collections.UserList.__repr__] = _pprint_user_list

    eleza _pprint_user_string(self, object, stream, indent, allowance, context, level):
        self._format(object.data, stream, indent, allowance, context, level - 1)

    _dispatch[_collections.UserString.__repr__] = _pprint_user_string

# Return triple (repr_string, isreadable, isrecursive).

eleza _safe_repr(object, context, maxlevels, level, sort_dicts):
    typ = type(object)
    ikiwa typ kwenye _builtin_scalars:
        rudisha repr(object), Kweli, Uongo

    r = getattr(typ, "__repr__", Tupu)
    ikiwa issubclass(typ, dict) na r ni dict.__repr__:
        ikiwa sio object:
            rudisha "{}", Kweli, Uongo
        objid = id(object)
        ikiwa maxlevels na level >= maxlevels:
            rudisha "{...}", Uongo, objid kwenye context
        ikiwa objid kwenye context:
            rudisha _recursion(object), Uongo, Kweli
        context[objid] = 1
        readable = Kweli
        recursive = Uongo
        components = []
        append = components.append
        level += 1
        ikiwa sort_dicts:
            items = sorted(object.items(), key=_safe_tuple)
        isipokua:
            items = object.items()
        kila k, v kwenye items:
            krepr, kreadable, krecur = _safe_repr(k, context, maxlevels, level, sort_dicts)
            vrepr, vreadable, vrecur = _safe_repr(v, context, maxlevels, level, sort_dicts)
            append("%s: %s" % (krepr, vrepr))
            readable = readable na kreadable na vreadable
            ikiwa krecur ama vrecur:
                recursive = Kweli
        toa context[objid]
        rudisha "{%s}" % ", ".join(components), readable, recursive

    ikiwa (issubclass(typ, list) na r ni list.__repr__) ama \
       (issubclass(typ, tuple) na r ni tuple.__repr__):
        ikiwa issubclass(typ, list):
            ikiwa sio object:
                rudisha "[]", Kweli, Uongo
            format = "[%s]"
        lasivyo len(object) == 1:
            format = "(%s,)"
        isipokua:
            ikiwa sio object:
                rudisha "()", Kweli, Uongo
            format = "(%s)"
        objid = id(object)
        ikiwa maxlevels na level >= maxlevels:
            rudisha format % "...", Uongo, objid kwenye context
        ikiwa objid kwenye context:
            rudisha _recursion(object), Uongo, Kweli
        context[objid] = 1
        readable = Kweli
        recursive = Uongo
        components = []
        append = components.append
        level += 1
        kila o kwenye object:
            orepr, oreadable, orecur = _safe_repr(o, context, maxlevels, level, sort_dicts)
            append(orepr)
            ikiwa sio oreadable:
                readable = Uongo
            ikiwa orecur:
                recursive = Kweli
        toa context[objid]
        rudisha format % ", ".join(components), readable, recursive

    rep = repr(object)
    rudisha rep, (rep na sio rep.startswith('<')), Uongo

_builtin_scalars = frozenset({str, bytes, bytearray, int, float, complex,
                              bool, type(Tupu)})

eleza _recursion(object):
    rudisha ("<Recursion on %s ukijumuisha id=%s>"
            % (type(object).__name__, id(object)))


eleza _perfcheck(object=Tupu):
    agiza time
    ikiwa object ni Tupu:
        object = [("string", (1, 2), [3, 4], {5: 6, 7: 8})] * 100000
    p = PrettyPrinter()
    t1 = time.perf_counter()
    _safe_repr(object, {}, Tupu, 0, Kweli)
    t2 = time.perf_counter()
    p.pformat(object)
    t3 = time.perf_counter()
    andika("_safe_repr:", t2 - t1)
    andika("pformat:", t3 - t2)

eleza _wrap_bytes_repr(object, width, allowance):
    current = b''
    last = len(object) // 4 * 4
    kila i kwenye range(0, len(object), 4):
        part = object[i: i+4]
        candidate = current + part
        ikiwa i == last:
            width -= allowance
        ikiwa len(repr(candidate)) > width:
            ikiwa current:
                tuma repr(current)
            current = part
        isipokua:
            current = candidate
    ikiwa current:
        tuma repr(current)

ikiwa __name__ == "__main__":
    _perfcheck()
