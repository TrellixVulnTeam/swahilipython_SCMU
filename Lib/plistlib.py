r"""plistlib.py -- a tool to generate na parse MacOSX .plist files.

The property list (.plist) file format ni a simple XML pickle supporting
basic object types, like dictionaries, lists, numbers na strings.
Usually the top level object ni a dictionary.

To write out a plist file, use the dump(value, file)
function. 'value' ni the top level object, 'file' is
a (writable) file object.

To parse a plist kutoka a file, use the load(file) function,
ukijumuisha a (readable) file object kama the only argument. It
returns the top level object (again, usually a dictionary).

To work ukijumuisha plist data kwenye bytes objects, you can use loads()
and dumps().

Values can be strings, integers, floats, booleans, tuples, lists,
dictionaries (but only ukijumuisha string keys), Data, bytes, bytearray, ama
datetime.datetime objects.

Generate Plist example:

    pl = dict(
        aString = "Doodah",
        aList = ["A", "B", 12, 32.1, [1, 2, 3]],
        aFloat = 0.1,
        anInt = 728,
        aDict = dict(
            anotherString = "<hello & hi there!>",
            aUnicodeValue = "M\xe4ssig, Ma\xdf",
            aKweliValue = Kweli,
            aUongoValue = Uongo,
        ),
        someData = b"<binary gunk>",
        someMoreData = b"<lots of binary gunk>" * 10,
        aDate = datetime.datetime.fromtimestamp(time.mktime(time.gmtime())),
    )
    ukijumuisha open(fileName, 'wb') kama fp:
        dump(pl, fp)

Parse Plist example:

    ukijumuisha open(fileName, 'rb') kama fp:
        pl = load(fp)
    andika(pl["aKey"])
"""
__all__ = [
    "readPlist", "writePlist", "readPlistFromBytes", "writePlistToBytes",
    "Data", "InvalidFileException", "FMT_XML", "FMT_BINARY",
    "load", "dump", "loads", "dumps", "UID"
]

agiza binascii
agiza codecs
agiza contextlib
agiza datetime
agiza enum
kutoka io agiza BytesIO
agiza itertools
agiza os
agiza re
agiza struct
kutoka warnings agiza warn
kutoka xml.parsers.expat agiza ParserCreate


PlistFormat = enum.Enum('PlistFormat', 'FMT_XML FMT_BINARY', module=__name__)
globals().update(PlistFormat.__members__)


#
#
# Deprecated functionality
#
#


@contextlib.contextmanager
eleza _maybe_open(pathOrFile, mode):
    ikiwa isinstance(pathOrFile, str):
        ukijumuisha open(pathOrFile, mode) kama fp:
            tuma fp

    isipokua:
        tuma pathOrFile


eleza readPlist(pathOrFile):
    """
    Read a .plist kutoka a path ama file. pathOrFile should either
    be a file name, ama a readable binary file object.

    This function ni deprecated, use load instead.
    """
    warn("The readPlist function ni deprecated, use load() instead",
        DeprecationWarning, 2)

    ukijumuisha _maybe_open(pathOrFile, 'rb') kama fp:
        rudisha load(fp, fmt=Tupu, use_builtin_types=Uongo)

eleza writePlist(value, pathOrFile):
    """
    Write 'value' to a .plist file. 'pathOrFile' may either be a
    file name ama a (writable) file object.

    This function ni deprecated, use dump instead.
    """
    warn("The writePlist function ni deprecated, use dump() instead",
        DeprecationWarning, 2)
    ukijumuisha _maybe_open(pathOrFile, 'wb') kama fp:
        dump(value, fp, fmt=FMT_XML, sort_keys=Kweli, skipkeys=Uongo)


eleza readPlistFromBytes(data):
    """
    Read a plist data kutoka a bytes object. Return the root object.

    This function ni deprecated, use loads instead.
    """
    warn("The readPlistFromBytes function ni deprecated, use loads() instead",
        DeprecationWarning, 2)
    rudisha load(BytesIO(data), fmt=Tupu, use_builtin_types=Uongo)


eleza writePlistToBytes(value):
    """
    Return 'value' kama a plist-formatted bytes object.

    This function ni deprecated, use dumps instead.
    """
    warn("The writePlistToBytes function ni deprecated, use dumps() instead",
        DeprecationWarning, 2)
    f = BytesIO()
    dump(value, f, fmt=FMT_XML, sort_keys=Kweli, skipkeys=Uongo)
    rudisha f.getvalue()


kundi Data:
    """
    Wrapper kila binary data.

    This kundi ni deprecated, use a bytes object instead.
    """

    eleza __init__(self, data):
        ikiwa sio isinstance(data, bytes):
            ashiria TypeError("data must be kama bytes")
        self.data = data

    @classmethod
    eleza fromBase64(cls, data):
        # base64.decodebytes just calls binascii.a2b_base64;
        # it seems overkill to use both base64 na binascii.
        rudisha cls(_decode_base64(data))

    eleza asBase64(self, maxlinelength=76):
        rudisha _encode_base64(self.data, maxlinelength)

    eleza __eq__(self, other):
        ikiwa isinstance(other, self.__class__):
            rudisha self.data == other.data
        lasivyo isinstance(other, bytes):
            rudisha self.data == other
        isipokua:
            rudisha NotImplemented

    eleza __repr__(self):
        rudisha "%s(%s)" % (self.__class__.__name__, repr(self.data))

#
#
# End of deprecated functionality
#
#


kundi UID:
    eleza __init__(self, data):
        ikiwa sio isinstance(data, int):
            ashiria TypeError("data must be an int")
        ikiwa data >= 1 << 64:
            ashiria ValueError("UIDs cannot be >= 2**64")
        ikiwa data < 0:
            ashiria ValueError("UIDs must be positive")
        self.data = data

    eleza __index__(self):
        rudisha self.data

    eleza __repr__(self):
        rudisha "%s(%s)" % (self.__class__.__name__, repr(self.data))

    eleza __reduce__(self):
        rudisha self.__class__, (self.data,)

    eleza __eq__(self, other):
        ikiwa sio isinstance(other, UID):
            rudisha NotImplemented
        rudisha self.data == other.data

    eleza __hash__(self):
        rudisha hash(self.data)


#
# XML support
#


# XML 'header'
PLISTHEADER = b"""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
"""


# Regex to find any control chars, tatizo kila \t \n na \r
_controlCharPat = re.compile(
    r"[\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f"
    r"\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f]")

eleza _encode_base64(s, maxlinelength=76):
    # copied kutoka base64.encodebytes(), ukijumuisha added maxlinelength argument
    maxbinsize = (maxlinelength//4)*3
    pieces = []
    kila i kwenye range(0, len(s), maxbinsize):
        chunk = s[i : i + maxbinsize]
        pieces.append(binascii.b2a_base64(chunk))
    rudisha b''.join(pieces)

eleza _decode_base64(s):
    ikiwa isinstance(s, str):
        rudisha binascii.a2b_base64(s.encode("utf-8"))

    isipokua:
        rudisha binascii.a2b_base64(s)

# Contents should conform to a subset of ISO 8601
# (in particular, YYYY '-' MM '-' DD 'T' HH ':' MM ':' SS 'Z'.  Smaller units
# may be omitted ukijumuisha #  a loss of precision)
_dateParser = re.compile(r"(?P<year>\d\d\d\d)(?:-(?P<month>\d\d)(?:-(?P<day>\d\d)(?:T(?P<hour>\d\d)(?::(?P<minute>\d\d)(?::(?P<second>\d\d))?)?)?)?)?Z", re.ASCII)


eleza _date_from_string(s):
    order = ('year', 'month', 'day', 'hour', 'minute', 'second')
    gd = _dateParser.match(s).groupdict()
    lst = []
    kila key kwenye order:
        val = gd[key]
        ikiwa val ni Tupu:
            koma
        lst.append(int(val))
    rudisha datetime.datetime(*lst)


eleza _date_to_string(d):
    rudisha '%04d-%02d-%02dT%02d:%02d:%02dZ' % (
        d.year, d.month, d.day,
        d.hour, d.minute, d.second
    )

eleza _escape(text):
    m = _controlCharPat.search(text)
    ikiwa m ni sio Tupu:
        ashiria ValueError("strings can't contains control characters; "
                         "use bytes instead")
    text = text.replace("\r\n", "\n")       # convert DOS line endings
    text = text.replace("\r", "\n")         # convert Mac line endings
    text = text.replace("&", "&amp;")       # escape '&'
    text = text.replace("<", "&lt;")        # escape '<'
    text = text.replace(">", "&gt;")        # escape '>'
    rudisha text

kundi _PlistParser:
    eleza __init__(self, use_builtin_types, dict_type):
        self.stack = []
        self.current_key = Tupu
        self.root = Tupu
        self._use_builtin_types = use_builtin_types
        self._dict_type = dict_type

    eleza parse(self, fileobj):
        self.parser = ParserCreate()
        self.parser.StartElementHandler = self.handle_begin_element
        self.parser.EndElementHandler = self.handle_end_element
        self.parser.CharacterDataHandler = self.handle_data
        self.parser.ParseFile(fileobj)
        rudisha self.root

    eleza handle_begin_element(self, element, attrs):
        self.data = []
        handler = getattr(self, "begin_" + element, Tupu)
        ikiwa handler ni sio Tupu:
            handler(attrs)

    eleza handle_end_element(self, element):
        handler = getattr(self, "end_" + element, Tupu)
        ikiwa handler ni sio Tupu:
            handler()

    eleza handle_data(self, data):
        self.data.append(data)

    eleza add_object(self, value):
        ikiwa self.current_key ni sio Tupu:
            ikiwa sio isinstance(self.stack[-1], type({})):
                ashiria ValueError("unexpected element at line %d" %
                                 self.parser.CurrentLineNumber)
            self.stack[-1][self.current_key] = value
            self.current_key = Tupu
        lasivyo sio self.stack:
            # this ni the root object
            self.root = value
        isipokua:
            ikiwa sio isinstance(self.stack[-1], type([])):
                ashiria ValueError("unexpected element at line %d" %
                                 self.parser.CurrentLineNumber)
            self.stack[-1].append(value)

    eleza get_data(self):
        data = ''.join(self.data)
        self.data = []
        rudisha data

    # element handlers

    eleza begin_dict(self, attrs):
        d = self._dict_type()
        self.add_object(d)
        self.stack.append(d)

    eleza end_dict(self):
        ikiwa self.current_key:
            ashiria ValueError("missing value kila key '%s' at line %d" %
                             (self.current_key,self.parser.CurrentLineNumber))
        self.stack.pop()

    eleza end_key(self):
        ikiwa self.current_key ama sio isinstance(self.stack[-1], type({})):
            ashiria ValueError("unexpected key at line %d" %
                             self.parser.CurrentLineNumber)
        self.current_key = self.get_data()

    eleza begin_array(self, attrs):
        a = []
        self.add_object(a)
        self.stack.append(a)

    eleza end_array(self):
        self.stack.pop()

    eleza end_true(self):
        self.add_object(Kweli)

    eleza end_false(self):
        self.add_object(Uongo)

    eleza end_integer(self):
        self.add_object(int(self.get_data()))

    eleza end_real(self):
        self.add_object(float(self.get_data()))

    eleza end_string(self):
        self.add_object(self.get_data())

    eleza end_data(self):
        ikiwa self._use_builtin_types:
            self.add_object(_decode_base64(self.get_data()))

        isipokua:
            self.add_object(Data.fromBase64(self.get_data()))

    eleza end_date(self):
        self.add_object(_date_from_string(self.get_data()))


kundi _DumbXMLWriter:
    eleza __init__(self, file, indent_level=0, indent="\t"):
        self.file = file
        self.stack = []
        self._indent_level = indent_level
        self.indent = indent

    eleza begin_element(self, element):
        self.stack.append(element)
        self.writeln("<%s>" % element)
        self._indent_level += 1

    eleza end_element(self, element):
        assert self._indent_level > 0
        assert self.stack.pop() == element
        self._indent_level -= 1
        self.writeln("</%s>" % element)

    eleza simple_element(self, element, value=Tupu):
        ikiwa value ni sio Tupu:
            value = _escape(value)
            self.writeln("<%s>%s</%s>" % (element, value, element))

        isipokua:
            self.writeln("<%s/>" % element)

    eleza writeln(self, line):
        ikiwa line:
            # plist has fixed encoding of utf-8

            # XXX: ni this test needed?
            ikiwa isinstance(line, str):
                line = line.encode('utf-8')
            self.file.write(self._indent_level * self.indent)
            self.file.write(line)
        self.file.write(b'\n')


kundi _PlistWriter(_DumbXMLWriter):
    eleza __init__(
            self, file, indent_level=0, indent=b"\t", writeHeader=1,
            sort_keys=Kweli, skipkeys=Uongo):

        ikiwa writeHeader:
            file.write(PLISTHEADER)
        _DumbXMLWriter.__init__(self, file, indent_level, indent)
        self._sort_keys = sort_keys
        self._skipkeys = skipkeys

    eleza write(self, value):
        self.writeln("<plist version=\"1.0\">")
        self.write_value(value)
        self.writeln("</plist>")

    eleza write_value(self, value):
        ikiwa isinstance(value, str):
            self.simple_element("string", value)

        lasivyo value ni Kweli:
            self.simple_element("true")

        lasivyo value ni Uongo:
            self.simple_element("false")

        lasivyo isinstance(value, int):
            ikiwa -1 << 63 <= value < 1 << 64:
                self.simple_element("integer", "%d" % value)
            isipokua:
                ashiria OverflowError(value)

        lasivyo isinstance(value, float):
            self.simple_element("real", repr(value))

        lasivyo isinstance(value, dict):
            self.write_dict(value)

        lasivyo isinstance(value, Data):
            self.write_data(value)

        lasivyo isinstance(value, (bytes, bytearray)):
            self.write_bytes(value)

        lasivyo isinstance(value, datetime.datetime):
            self.simple_element("date", _date_to_string(value))

        lasivyo isinstance(value, (tuple, list)):
            self.write_array(value)

        isipokua:
            ashiria TypeError("unsupported type: %s" % type(value))

    eleza write_data(self, data):
        self.write_bytes(data.data)

    eleza write_bytes(self, data):
        self.begin_element("data")
        self._indent_level -= 1
        maxlinelength = max(
            16,
            76 - len(self.indent.replace(b"\t", b" " * 8) * self._indent_level))

        kila line kwenye _encode_base64(data, maxlinelength).split(b"\n"):
            ikiwa line:
                self.writeln(line)
        self._indent_level += 1
        self.end_element("data")

    eleza write_dict(self, d):
        ikiwa d:
            self.begin_element("dict")
            ikiwa self._sort_keys:
                items = sorted(d.items())
            isipokua:
                items = d.items()

            kila key, value kwenye items:
                ikiwa sio isinstance(key, str):
                    ikiwa self._skipkeys:
                        endelea
                    ashiria TypeError("keys must be strings")
                self.simple_element("key", key)
                self.write_value(value)
            self.end_element("dict")

        isipokua:
            self.simple_element("dict")

    eleza write_array(self, array):
        ikiwa array:
            self.begin_element("array")
            kila value kwenye array:
                self.write_value(value)
            self.end_element("array")

        isipokua:
            self.simple_element("array")


eleza _is_fmt_xml(header):
    prefixes = (b'<?xml', b'<plist')

    kila pfx kwenye prefixes:
        ikiwa header.startswith(pfx):
            rudisha Kweli

    # Also check kila alternative XML encodings, this ni slightly
    # overkill because the Apple tools (and plistlib) will sio
    # generate files ukijumuisha these encodings.
    kila bom, encoding kwenye (
                (codecs.BOM_UTF8, "utf-8"),
                (codecs.BOM_UTF16_BE, "utf-16-be"),
                (codecs.BOM_UTF16_LE, "utf-16-le"),
                # expat does sio support utf-32
                #(codecs.BOM_UTF32_BE, "utf-32-be"),
                #(codecs.BOM_UTF32_LE, "utf-32-le"),
            ):
        ikiwa sio header.startswith(bom):
            endelea

        kila start kwenye prefixes:
            prefix = bom + start.decode('ascii').encode(encoding)
            ikiwa header[:len(prefix)] == prefix:
                rudisha Kweli

    rudisha Uongo

#
# Binary Plist
#


kundi InvalidFileException (ValueError):
    eleza __init__(self, message="Invalid file"):
        ValueError.__init__(self, message)

_BINARY_FORMAT = {1: 'B', 2: 'H', 4: 'L', 8: 'Q'}

_undefined = object()

kundi _BinaryPlistParser:
    """
    Read ama write a binary plist file, following the description of the binary
    format.  Raise InvalidFileException kwenye case of error, otherwise rudisha the
    root object.

    see also: http://opensource.apple.com/source/CF/CF-744.18/CFBinaryPList.c
    """
    eleza __init__(self, use_builtin_types, dict_type):
        self._use_builtin_types = use_builtin_types
        self._dict_type = dict_type

    eleza parse(self, fp):
        jaribu:
            # The basic file format:
            # HEADER
            # object...
            # refid->offset...
            # TRAILER
            self._fp = fp
            self._fp.seek(-32, os.SEEK_END)
            trailer = self._fp.read(32)
            ikiwa len(trailer) != 32:
                ashiria InvalidFileException()
            (
                offset_size, self._ref_size, num_objects, top_object,
                offset_table_offset
            ) = struct.unpack('>6xBBQQQ', trailer)
            self._fp.seek(offset_table_offset)
            self._object_offsets = self._read_ints(num_objects, offset_size)
            self._objects = [_undefined] * num_objects
            rudisha self._read_object(top_object)

        tatizo (OSError, IndexError, struct.error, OverflowError,
                UnicodeDecodeError):
            ashiria InvalidFileException()

    eleza _get_size(self, tokenL):
        """ rudisha the size of the next object."""
        ikiwa tokenL == 0xF:
            m = self._fp.read(1)[0] & 0x3
            s = 1 << m
            f = '>' + _BINARY_FORMAT[s]
            rudisha struct.unpack(f, self._fp.read(s))[0]

        rudisha tokenL

    eleza _read_ints(self, n, size):
        data = self._fp.read(size * n)
        ikiwa size kwenye _BINARY_FORMAT:
            rudisha struct.unpack('>' + _BINARY_FORMAT[size] * n, data)
        isipokua:
            ikiwa sio size ama len(data) != size * n:
                ashiria InvalidFileException()
            rudisha tuple(int.from_bytes(data[i: i + size], 'big')
                         kila i kwenye range(0, size * n, size))

    eleza _read_refs(self, n):
        rudisha self._read_ints(n, self._ref_size)

    eleza _read_object(self, ref):
        """
        read the object by reference.

        May recursively read sub-objects (content of an array/dict/set)
        """
        result = self._objects[ref]
        ikiwa result ni sio _undefined:
            rudisha result

        offset = self._object_offsets[ref]
        self._fp.seek(offset)
        token = self._fp.read(1)[0]
        tokenH, tokenL = token & 0xF0, token & 0x0F

        ikiwa token == 0x00:
            result = Tupu

        lasivyo token == 0x08:
            result = Uongo

        lasivyo token == 0x09:
            result = Kweli

        # The referenced source code also mentions URL (0x0c, 0x0d) na
        # UUID (0x0e), but neither can be generated using the Cocoa libraries.

        lasivyo token == 0x0f:
            result = b''

        lasivyo tokenH == 0x10:  # int
            result = int.from_bytes(self._fp.read(1 << tokenL),
                                    'big', signed=tokenL >= 3)

        lasivyo token == 0x22: # real
            result = struct.unpack('>f', self._fp.read(4))[0]

        lasivyo token == 0x23: # real
            result = struct.unpack('>d', self._fp.read(8))[0]

        lasivyo token == 0x33:  # date
            f = struct.unpack('>d', self._fp.read(8))[0]
            # timestamp 0 of binary plists corresponds to 1/1/2001
            # (year of Mac OS X 10.0), instead of 1/1/1970.
            result = (datetime.datetime(2001, 1, 1) +
                      datetime.timedelta(seconds=f))

        lasivyo tokenH == 0x40:  # data
            s = self._get_size(tokenL)
            ikiwa self._use_builtin_types:
                result = self._fp.read(s)
            isipokua:
                result = Data(self._fp.read(s))

        lasivyo tokenH == 0x50:  # ascii string
            s = self._get_size(tokenL)
            result =  self._fp.read(s).decode('ascii')

        lasivyo tokenH == 0x60:  # unicode string
            s = self._get_size(tokenL)
            result = self._fp.read(s * 2).decode('utf-16be')

        lasivyo tokenH == 0x80:  # UID
            # used by Key-Archiver plist files
            result = UID(int.from_bytes(self._fp.read(1 + tokenL), 'big'))

        lasivyo tokenH == 0xA0:  # array
            s = self._get_size(tokenL)
            obj_refs = self._read_refs(s)
            result = []
            self._objects[ref] = result
            result.extend(self._read_object(x) kila x kwenye obj_refs)

        # tokenH == 0xB0 ni documented kama 'ordset', but ni sio actually
        # implemented kwenye the Apple reference code.

        # tokenH == 0xC0 ni documented kama 'set', but sets cannot be used kwenye
        # plists.

        lasivyo tokenH == 0xD0:  # dict
            s = self._get_size(tokenL)
            key_refs = self._read_refs(s)
            obj_refs = self._read_refs(s)
            result = self._dict_type()
            self._objects[ref] = result
            kila k, o kwenye zip(key_refs, obj_refs):
                result[self._read_object(k)] = self._read_object(o)

        isipokua:
            ashiria InvalidFileException()

        self._objects[ref] = result
        rudisha result

eleza _count_to_size(count):
    ikiwa count < 1 << 8:
        rudisha 1

    lasivyo count < 1 << 16:
        rudisha 2

    lasivyo count << 1 << 32:
        rudisha 4

    isipokua:
        rudisha 8

_scalars = (str, int, float, datetime.datetime, bytes)

kundi _BinaryPlistWriter (object):
    eleza __init__(self, fp, sort_keys, skipkeys):
        self._fp = fp
        self._sort_keys = sort_keys
        self._skipkeys = skipkeys

    eleza write(self, value):

        # Flattened object list:
        self._objlist = []

        # Mappings kutoka object->objectid
        # First dict has (type(object), object) kama the key,
        # second dict ni used when object ni sio hashable na
        # has id(object) kama the key.
        self._objtable = {}
        self._objidtable = {}

        # Create list of all objects kwenye the plist
        self._flatten(value)

        # Size of object references kwenye serialized containers
        # depends on the number of objects kwenye the plist.
        num_objects = len(self._objlist)
        self._object_offsets = [0]*num_objects
        self._ref_size = _count_to_size(num_objects)

        self._ref_format = _BINARY_FORMAT[self._ref_size]

        # Write file header
        self._fp.write(b'bplist00')

        # Write object list
        kila obj kwenye self._objlist:
            self._write_object(obj)

        # Write refnum->object offset table
        top_object = self._getrefnum(value)
        offset_table_offset = self._fp.tell()
        offset_size = _count_to_size(offset_table_offset)
        offset_format = '>' + _BINARY_FORMAT[offset_size] * num_objects
        self._fp.write(struct.pack(offset_format, *self._object_offsets))

        # Write trailer
        sort_version = 0
        trailer = (
            sort_version, offset_size, self._ref_size, num_objects,
            top_object, offset_table_offset
        )
        self._fp.write(struct.pack('>5xBBBQQQ', *trailer))

    eleza _flatten(self, value):
        # First check ikiwa the object ni kwenye the object table, sio used for
        # containers to ensure that two subcontainers ukijumuisha the same contents
        # will be serialized kama distinct values.
        ikiwa isinstance(value, _scalars):
            ikiwa (type(value), value) kwenye self._objtable:
                rudisha

        lasivyo isinstance(value, Data):
            ikiwa (type(value.data), value.data) kwenye self._objtable:
                rudisha

        lasivyo id(value) kwenye self._objidtable:
            rudisha

        # Add to objectreference map
        refnum = len(self._objlist)
        self._objlist.append(value)
        ikiwa isinstance(value, _scalars):
            self._objtable[(type(value), value)] = refnum
        lasivyo isinstance(value, Data):
            self._objtable[(type(value.data), value.data)] = refnum
        isipokua:
            self._objidtable[id(value)] = refnum

        # And finally recurse into containers
        ikiwa isinstance(value, dict):
            keys = []
            values = []
            items = value.items()
            ikiwa self._sort_keys:
                items = sorted(items)

            kila k, v kwenye items:
                ikiwa sio isinstance(k, str):
                    ikiwa self._skipkeys:
                        endelea
                    ashiria TypeError("keys must be strings")
                keys.append(k)
                values.append(v)

            kila o kwenye itertools.chain(keys, values):
                self._flatten(o)

        lasivyo isinstance(value, (list, tuple)):
            kila o kwenye value:
                self._flatten(o)

    eleza _getrefnum(self, value):
        ikiwa isinstance(value, _scalars):
            rudisha self._objtable[(type(value), value)]
        lasivyo isinstance(value, Data):
            rudisha self._objtable[(type(value.data), value.data)]
        isipokua:
            rudisha self._objidtable[id(value)]

    eleza _write_size(self, token, size):
        ikiwa size < 15:
            self._fp.write(struct.pack('>B', token | size))

        lasivyo size < 1 << 8:
            self._fp.write(struct.pack('>BBB', token | 0xF, 0x10, size))

        lasivyo size < 1 << 16:
            self._fp.write(struct.pack('>BBH', token | 0xF, 0x11, size))

        lasivyo size < 1 << 32:
            self._fp.write(struct.pack('>BBL', token | 0xF, 0x12, size))

        isipokua:
            self._fp.write(struct.pack('>BBQ', token | 0xF, 0x13, size))

    eleza _write_object(self, value):
        ref = self._getrefnum(value)
        self._object_offsets[ref] = self._fp.tell()
        ikiwa value ni Tupu:
            self._fp.write(b'\x00')

        lasivyo value ni Uongo:
            self._fp.write(b'\x08')

        lasivyo value ni Kweli:
            self._fp.write(b'\x09')

        lasivyo isinstance(value, int):
            ikiwa value < 0:
                jaribu:
                    self._fp.write(struct.pack('>Bq', 0x13, value))
                tatizo struct.error:
                    ashiria OverflowError(value) kutoka Tupu
            lasivyo value < 1 << 8:
                self._fp.write(struct.pack('>BB', 0x10, value))
            lasivyo value < 1 << 16:
                self._fp.write(struct.pack('>BH', 0x11, value))
            lasivyo value < 1 << 32:
                self._fp.write(struct.pack('>BL', 0x12, value))
            lasivyo value < 1 << 63:
                self._fp.write(struct.pack('>BQ', 0x13, value))
            lasivyo value < 1 << 64:
                self._fp.write(b'\x14' + value.to_bytes(16, 'big', signed=Kweli))
            isipokua:
                ashiria OverflowError(value)

        lasivyo isinstance(value, float):
            self._fp.write(struct.pack('>Bd', 0x23, value))

        lasivyo isinstance(value, datetime.datetime):
            f = (value - datetime.datetime(2001, 1, 1)).total_seconds()
            self._fp.write(struct.pack('>Bd', 0x33, f))

        lasivyo isinstance(value, Data):
            self._write_size(0x40, len(value.data))
            self._fp.write(value.data)

        lasivyo isinstance(value, (bytes, bytearray)):
            self._write_size(0x40, len(value))
            self._fp.write(value)

        lasivyo isinstance(value, str):
            jaribu:
                t = value.encode('ascii')
                self._write_size(0x50, len(value))
            tatizo UnicodeEncodeError:
                t = value.encode('utf-16be')
                self._write_size(0x60, len(t) // 2)

            self._fp.write(t)

        lasivyo isinstance(value, UID):
            ikiwa value.data < 0:
                ashiria ValueError("UIDs must be positive")
            lasivyo value.data < 1 << 8:
                self._fp.write(struct.pack('>BB', 0x80, value))
            lasivyo value.data < 1 << 16:
                self._fp.write(struct.pack('>BH', 0x81, value))
            lasivyo value.data < 1 << 32:
                self._fp.write(struct.pack('>BL', 0x83, value))
            lasivyo value.data < 1 << 64:
                self._fp.write(struct.pack('>BQ', 0x87, value))
            isipokua:
                ashiria OverflowError(value)

        lasivyo isinstance(value, (list, tuple)):
            refs = [self._getrefnum(o) kila o kwenye value]
            s = len(refs)
            self._write_size(0xA0, s)
            self._fp.write(struct.pack('>' + self._ref_format * s, *refs))

        lasivyo isinstance(value, dict):
            keyRefs, valRefs = [], []

            ikiwa self._sort_keys:
                rootItems = sorted(value.items())
            isipokua:
                rootItems = value.items()

            kila k, v kwenye rootItems:
                ikiwa sio isinstance(k, str):
                    ikiwa self._skipkeys:
                        endelea
                    ashiria TypeError("keys must be strings")
                keyRefs.append(self._getrefnum(k))
                valRefs.append(self._getrefnum(v))

            s = len(keyRefs)
            self._write_size(0xD0, s)
            self._fp.write(struct.pack('>' + self._ref_format * s, *keyRefs))
            self._fp.write(struct.pack('>' + self._ref_format * s, *valRefs))

        isipokua:
            ashiria TypeError(value)


eleza _is_fmt_binary(header):
    rudisha header[:8] == b'bplist00'


#
# Generic bits
#

_FORMATS={
    FMT_XML: dict(
        detect=_is_fmt_xml,
        parser=_PlistParser,
        writer=_PlistWriter,
    ),
    FMT_BINARY: dict(
        detect=_is_fmt_binary,
        parser=_BinaryPlistParser,
        writer=_BinaryPlistWriter,
    )
}


eleza load(fp, *, fmt=Tupu, use_builtin_types=Kweli, dict_type=dict):
    """Read a .plist file. 'fp' should be a readable na binary file object.
    Return the unpacked root object (which usually ni a dictionary).
    """
    ikiwa fmt ni Tupu:
        header = fp.read(32)
        fp.seek(0)
        kila info kwenye _FORMATS.values():
            ikiwa info['detect'](header):
                P = info['parser']
                koma

        isipokua:
            ashiria InvalidFileException()

    isipokua:
        P = _FORMATS[fmt]['parser']

    p = P(use_builtin_types=use_builtin_types, dict_type=dict_type)
    rudisha p.parse(fp)


eleza loads(value, *, fmt=Tupu, use_builtin_types=Kweli, dict_type=dict):
    """Read a .plist file kutoka a bytes object.
    Return the unpacked root object (which usually ni a dictionary).
    """
    fp = BytesIO(value)
    rudisha load(
        fp, fmt=fmt, use_builtin_types=use_builtin_types, dict_type=dict_type)


eleza dump(value, fp, *, fmt=FMT_XML, sort_keys=Kweli, skipkeys=Uongo):
    """Write 'value' to a .plist file. 'fp' should be a writable,
    binary file object.
    """
    ikiwa fmt haiko kwenye _FORMATS:
        ashiria ValueError("Unsupported format: %r"%(fmt,))

    writer = _FORMATS[fmt]["writer"](fp, sort_keys=sort_keys, skipkeys=skipkeys)
    writer.write(value)


eleza dumps(value, *, fmt=FMT_XML, skipkeys=Uongo, sort_keys=Kweli):
    """Return a bytes object ukijumuisha the contents kila a .plist file.
    """
    fp = BytesIO()
    dump(value, fp, fmt=fmt, skipkeys=skipkeys, sort_keys=sort_keys)
    rudisha fp.getvalue()
