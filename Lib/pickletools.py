'''"Executable documentation" kila the pickle module.

Extensive comments about the pickle protocols na pickle-machine opcodes
can be found here.  Some functions meant kila external use:

genops(pickle)
   Generate all the opcodes kwenye a pickle, kama (opcode, arg, position) triples.

dis(pickle, out=Tupu, memo=Tupu, indentlevel=4)
   Print a symbolic disassembly of a pickle.
'''

agiza codecs
agiza io
agiza pickle
agiza re
agiza sys

__all__ = ['dis', 'genops', 'optimize']

bytes_types = pickle.bytes_types

# Other ideas:
#
# - A pickle verifier:  read a pickle na check it exhaustively for
#   well-formedness.  dis() does a lot of this already.
#
# - A protocol identifier:  examine a pickle na rudisha its protocol number
#   (== the highest .proto attr value among all the opcodes kwenye the pickle).
#   dis() already prints this info at the end.
#
# - A pickle optimizer:  kila example, tuple-building code ni sometimes more
#   elaborate than necessary, catering kila the possibility that the tuple
#   ni recursive.  Or lots of times a PUT ni generated that's never accessed
#   by a later GET.


# "A pickle" ni a program kila a virtual pickle machine (PM, but more accurately
# called an unpickling machine).  It's a sequence of opcodes, interpreted by the
# PM, building an arbitrarily complex Python object.
#
# For the most part, the PM ni very simple:  there are no looping, testing, ama
# conditional instructions, no arithmetic na no function calls.  Opcodes are
# executed once each, kutoka first to last, until a STOP opcode ni reached.
#
# The PM has two data areas, "the stack" na "the memo".
#
# Many opcodes push Python objects onto the stack; e.g., INT pushes a Python
# integer object on the stack, whose value ni gotten kutoka a decimal string
# literal immediately following the INT opcode kwenye the pickle bytestream.  Other
# opcodes take Python objects off the stack.  The result of unpickling is
# whatever object ni left on the stack when the final STOP opcode ni executed.
#
# The memo ni simply an array of objects, ama it can be implemented kama a dict
# mapping little integers to objects.  The memo serves kama the PM's "long term
# memory", na the little integers indexing the memo are akin to variable
# names.  Some opcodes pop a stack object into the memo at a given index,
# na others push a memo object at a given index onto the stack again.
#
# At heart, that's all the PM has.  Subtleties arise kila these reasons:
#
# + Object identity.  Objects can be arbitrarily complex, na subobjects
#   may be shared (kila example, the list [a, a] refers to the same object a
#   twice).  It can be vital that unpickling recreate an isomorphic object
#   graph, faithfully reproducing sharing.
#
# + Recursive objects.  For example, after "L = []; L.append(L)", L ni a
#   list, na L[0] ni the same list.  This ni related to the object identity
#   point, na some sequences of pickle opcodes are subtle kwenye order to
#   get the right result kwenye all cases.
#
# + Things pickle doesn't know everything about.  Examples of things pickle
#   does know everything about are Python's builtin scalar na container
#   types, like ints na tuples.  They generally have opcodes dedicated to
#   them.  For things like module references na instances of user-defined
#   classes, pickle's knowledge ni limited.  Historically, many enhancements
#   have been made to the pickle protocol kwenye order to do a better (faster,
#   and/or more compact) job on those.
#
# + Backward compatibility na micro-optimization.  As explained below,
#   pickle opcodes never go away, sio even when better ways to do a thing
#   get invented.  The repertoire of the PM just keeps growing over time.
#   For example, protocol 0 had two opcodes kila building Python integers (INT
#   na LONG), protocol 1 added three more kila more-efficient pickling of short
#   integers, na protocol 2 added two more kila more-efficient pickling of
#   long integers (before protocol 2, the only ways to pickle a Python long
#   took time quadratic kwenye the number of digits, kila both pickling na
#   unpickling).  "Opcode bloat" isn't so much a subtlety kama a source of
#   wearying complication.
#
#
# Pickle protocols:
#
# For compatibility, the meaning of a pickle opcode never changes.  Instead new
# pickle opcodes get added, na each version's unpickler can handle all the
# pickle opcodes kwenye all protocol versions to date.  So old pickles endelea to
# be readable forever.  The pickler can generally be told to restrict itself to
# the subset of opcodes available under previous protocol versions too, so that
# users can create pickles under the current version readable by older
# versions.  However, a pickle does sio contain its version number embedded
# within it.  If an older unpickler tries to read a pickle using a later
# protocol, the result ni most likely an exception due to seeing an unknown (in
# the older unpickler) opcode.
#
# The original pickle used what's now called "protocol 0", na what was called
# "text mode" before Python 2.3.  The entire pickle bytestream ni made up of
# printable 7-bit ASCII characters, plus the newline character, kwenye protocol 0.
# That's why it was called text mode.  Protocol 0 ni small na elegant, but
# sometimes painfully inefficient.
#
# The second major set of additions ni now called "protocol 1", na was called
# "binary mode" before Python 2.3.  This added many opcodes ukijumuisha arguments
# consisting of arbitrary bytes, including NUL bytes na unprintable "high bit"
# bytes.  Binary mode pickles can be substantially smaller than equivalent
# text mode pickles, na sometimes faster too; e.g., BININT represents a 4-byte
# int kama 4 bytes following the opcode, which ni cheaper to unpickle than the
# (perhaps) 11-character decimal string attached to INT.  Protocol 1 also added
# a number of opcodes that operate on many stack elements at once (like APPENDS
# na SETITEMS), na "shortcut" opcodes (like EMPTY_DICT na EMPTY_TUPLE).
#
# The third major set of additions came kwenye Python 2.3, na ni called "protocol
# 2".  This added:
#
# - A better way to pickle instances of new-style classes (NEWOBJ).
#
# - A way kila a pickle to identify its protocol (PROTO).
#
# - Time- na space- efficient pickling of long ints (LONG{1,4}).
#
# - Shortcuts kila small tuples (TUPLE{1,2,3}}.
#
# - Dedicated opcodes kila bools (NEWTRUE, NEWFALSE).
#
# - The "extension registry", a vector of popular objects that can be pushed
#   efficiently by index (EXT{1,2,4}).  This ni akin to the memo na GET, but
#   the registry contents are predefined (there's nothing akin to the memo's
#   PUT).
#
# Another independent change ukijumuisha Python 2.3 ni the abandonment of any
# pretense that it might be safe to load pickles received kutoka untrusted
# parties -- no sufficient security analysis has been done to guarantee
# this na there isn't a use case that warrants the expense of such an
# analysis.
#
# To this end, all tests kila __safe_for_unpickling__ ama for
# copyreg.safe_constructors are removed kutoka the unpickling code.
# References to these variables kwenye the descriptions below are to be seen
# kama describing unpickling kwenye Python 2.2 na before.


# Meta-rule:  Descriptions are stored kwenye instances of descriptor objects,
# ukijumuisha plain constructors.  No meta-language ni defined kutoka which
# descriptors could be constructed.  If you want, e.g., XML, write a little
# program to generate XML kutoka the objects.

##############################################################################
# Some pickle opcodes have an argument, following the opcode kwenye the
# bytestream.  An argument ni of a specific type, described by an instance
# of ArgumentDescriptor.  These are sio to be confused ukijumuisha arguments taken
# off the stack -- ArgumentDescriptor applies only to arguments embedded kwenye
# the opcode stream, immediately following an opcode.

# Represents the number of bytes consumed by an argument delimited by the
# next newline character.
UP_TO_NEWLINE = -1

# Represents the number of bytes consumed by a two-argument opcode where
# the first argument gives the number of bytes kwenye the second argument.
TAKEN_FROM_ARGUMENT1  = -2   # num bytes ni 1-byte unsigned int
TAKEN_FROM_ARGUMENT4  = -3   # num bytes ni 4-byte signed little-endian int
TAKEN_FROM_ARGUMENT4U = -4   # num bytes ni 4-byte unsigned little-endian int
TAKEN_FROM_ARGUMENT8U = -5   # num bytes ni 8-byte unsigned little-endian int

kundi ArgumentDescriptor(object):
    __slots__ = (
        # name of descriptor record, also a module global name; a string
        'name',

        # length of argument, kwenye bytes; an int; UP_TO_NEWLINE na
        # TAKEN_FROM_ARGUMENT{1,4,8} are negative values kila variable-length
        # cases
        'n',

        # a function taking a file-like object, reading this kind of argument
        # kutoka the object at the current position, advancing the current
        # position by n bytes, na returning the value of the argument
        'reader',

        # human-readable docs kila this arg descriptor; a string
        'doc',
    )

    eleza __init__(self, name, n, reader, doc):
        assert isinstance(name, str)
        self.name = name

        assert isinstance(n, int) na (n >= 0 ama
                                       n kwenye (UP_TO_NEWLINE,
                                             TAKEN_FROM_ARGUMENT1,
                                             TAKEN_FROM_ARGUMENT4,
                                             TAKEN_FROM_ARGUMENT4U,
                                             TAKEN_FROM_ARGUMENT8U))
        self.n = n

        self.reader = reader

        assert isinstance(doc, str)
        self.doc = doc

kutoka struct agiza unpack kama _unpack

eleza read_uint1(f):
    r"""
    >>> agiza io
    >>> read_uint1(io.BytesIO(b'\xff'))
    255
    """

    data = f.read(1)
    ikiwa data:
        rudisha data[0]
    ashiria ValueError("sio enough data kwenye stream to read uint1")

uint1 = ArgumentDescriptor(
            name='uint1',
            n=1,
            reader=read_uint1,
            doc="One-byte unsigned integer.")


eleza read_uint2(f):
    r"""
    >>> agiza io
    >>> read_uint2(io.BytesIO(b'\xff\x00'))
    255
    >>> read_uint2(io.BytesIO(b'\xff\xff'))
    65535
    """

    data = f.read(2)
    ikiwa len(data) == 2:
        rudisha _unpack("<H", data)[0]
    ashiria ValueError("sio enough data kwenye stream to read uint2")

uint2 = ArgumentDescriptor(
            name='uint2',
            n=2,
            reader=read_uint2,
            doc="Two-byte unsigned integer, little-endian.")


eleza read_int4(f):
    r"""
    >>> agiza io
    >>> read_int4(io.BytesIO(b'\xff\x00\x00\x00'))
    255
    >>> read_int4(io.BytesIO(b'\x00\x00\x00\x80')) == -(2**31)
    Kweli
    """

    data = f.read(4)
    ikiwa len(data) == 4:
        rudisha _unpack("<i", data)[0]
    ashiria ValueError("sio enough data kwenye stream to read int4")

int4 = ArgumentDescriptor(
           name='int4',
           n=4,
           reader=read_int4,
           doc="Four-byte signed integer, little-endian, 2's complement.")


eleza read_uint4(f):
    r"""
    >>> agiza io
    >>> read_uint4(io.BytesIO(b'\xff\x00\x00\x00'))
    255
    >>> read_uint4(io.BytesIO(b'\x00\x00\x00\x80')) == 2**31
    Kweli
    """

    data = f.read(4)
    ikiwa len(data) == 4:
        rudisha _unpack("<I", data)[0]
    ashiria ValueError("sio enough data kwenye stream to read uint4")

uint4 = ArgumentDescriptor(
            name='uint4',
            n=4,
            reader=read_uint4,
            doc="Four-byte unsigned integer, little-endian.")


eleza read_uint8(f):
    r"""
    >>> agiza io
    >>> read_uint8(io.BytesIO(b'\xff\x00\x00\x00\x00\x00\x00\x00'))
    255
    >>> read_uint8(io.BytesIO(b'\xff' * 8)) == 2**64-1
    Kweli
    """

    data = f.read(8)
    ikiwa len(data) == 8:
        rudisha _unpack("<Q", data)[0]
    ashiria ValueError("sio enough data kwenye stream to read uint8")

uint8 = ArgumentDescriptor(
            name='uint8',
            n=8,
            reader=read_uint8,
            doc="Eight-byte unsigned integer, little-endian.")


eleza read_stringnl(f, decode=Kweli, stripquotes=Kweli):
    r"""
    >>> agiza io
    >>> read_stringnl(io.BytesIO(b"'abcd'\nefg\n"))
    'abcd'

    >>> read_stringnl(io.BytesIO(b"\n"))
    Traceback (most recent call last):
    ...
    ValueError: no string quotes around b''

    >>> read_stringnl(io.BytesIO(b"\n"), stripquotes=Uongo)
    ''

    >>> read_stringnl(io.BytesIO(b"''\n"))
    ''

    >>> read_stringnl(io.BytesIO(b'"abcd"'))
    Traceback (most recent call last):
    ...
    ValueError: no newline found when trying to read stringnl

    Embedded escapes are undone kwenye the result.
    >>> read_stringnl(io.BytesIO(br"'a\n\\b\x00c\td'" + b"\n'e'"))
    'a\n\\b\x00c\td'
    """

    data = f.readline()
    ikiwa sio data.endswith(b'\n'):
        ashiria ValueError("no newline found when trying to read stringnl")
    data = data[:-1]    # lose the newline

    ikiwa stripquotes:
        kila q kwenye (b'"', b"'"):
            ikiwa data.startswith(q):
                ikiwa sio data.endswith(q):
                    ashiria ValueError("strinq quote %r sio found at both "
                                     "ends of %r" % (q, data))
                data = data[1:-1]
                koma
        isipokua:
            ashiria ValueError("no string quotes around %r" % data)

    ikiwa decode:
        data = codecs.escape_decode(data)[0].decode("ascii")
    rudisha data

stringnl = ArgumentDescriptor(
               name='stringnl',
               n=UP_TO_NEWLINE,
               reader=read_stringnl,
               doc="""A newline-terminated string.

                   This ni a repr-style string, ukijumuisha embedded escapes, na
                   bracketing quotes.
                   """)

eleza read_stringnl_noescape(f):
    rudisha read_stringnl(f, stripquotes=Uongo)

stringnl_noescape = ArgumentDescriptor(
                        name='stringnl_noescape',
                        n=UP_TO_NEWLINE,
                        reader=read_stringnl_noescape,
                        doc="""A newline-terminated string.

                        This ni a str-style string, without embedded escapes,
                        ama bracketing quotes.  It should consist solely of
                        printable ASCII characters.
                        """)

eleza read_stringnl_noescape_pair(f):
    r"""
    >>> agiza io
    >>> read_stringnl_noescape_pair(io.BytesIO(b"Queue\nEmpty\njunk"))
    'Queue Empty'
    """

    rudisha "%s %s" % (read_stringnl_noescape(f), read_stringnl_noescape(f))

stringnl_noescape_pair = ArgumentDescriptor(
                             name='stringnl_noescape_pair',
                             n=UP_TO_NEWLINE,
                             reader=read_stringnl_noescape_pair,
                             doc="""A pair of newline-terminated strings.

                             These are str-style strings, without embedded
                             escapes, ama bracketing quotes.  They should
                             consist solely of printable ASCII characters.
                             The pair ni returned kama a single string, with
                             a single blank separating the two strings.
                             """)


eleza read_string1(f):
    r"""
    >>> agiza io
    >>> read_string1(io.BytesIO(b"\x00"))
    ''
    >>> read_string1(io.BytesIO(b"\x03abcdef"))
    'abc'
    """

    n = read_uint1(f)
    assert n >= 0
    data = f.read(n)
    ikiwa len(data) == n:
        rudisha data.decode("latin-1")
    ashiria ValueError("expected %d bytes kwenye a string1, but only %d remain" %
                     (n, len(data)))

string1 = ArgumentDescriptor(
              name="string1",
              n=TAKEN_FROM_ARGUMENT1,
              reader=read_string1,
              doc="""A counted string.

              The first argument ni a 1-byte unsigned int giving the number
              of bytes kwenye the string, na the second argument ni that many
              bytes.
              """)


eleza read_string4(f):
    r"""
    >>> agiza io
    >>> read_string4(io.BytesIO(b"\x00\x00\x00\x00abc"))
    ''
    >>> read_string4(io.BytesIO(b"\x03\x00\x00\x00abcdef"))
    'abc'
    >>> read_string4(io.BytesIO(b"\x00\x00\x00\x03abcdef"))
    Traceback (most recent call last):
    ...
    ValueError: expected 50331648 bytes kwenye a string4, but only 6 remain
    """

    n = read_int4(f)
    ikiwa n < 0:
        ashiria ValueError("string4 byte count < 0: %d" % n)
    data = f.read(n)
    ikiwa len(data) == n:
        rudisha data.decode("latin-1")
    ashiria ValueError("expected %d bytes kwenye a string4, but only %d remain" %
                     (n, len(data)))

string4 = ArgumentDescriptor(
              name="string4",
              n=TAKEN_FROM_ARGUMENT4,
              reader=read_string4,
              doc="""A counted string.

              The first argument ni a 4-byte little-endian signed int giving
              the number of bytes kwenye the string, na the second argument is
              that many bytes.
              """)


eleza read_bytes1(f):
    r"""
    >>> agiza io
    >>> read_bytes1(io.BytesIO(b"\x00"))
    b''
    >>> read_bytes1(io.BytesIO(b"\x03abcdef"))
    b'abc'
    """

    n = read_uint1(f)
    assert n >= 0
    data = f.read(n)
    ikiwa len(data) == n:
        rudisha data
    ashiria ValueError("expected %d bytes kwenye a bytes1, but only %d remain" %
                     (n, len(data)))

bytes1 = ArgumentDescriptor(
              name="bytes1",
              n=TAKEN_FROM_ARGUMENT1,
              reader=read_bytes1,
              doc="""A counted bytes string.

              The first argument ni a 1-byte unsigned int giving the number
              of bytes, na the second argument ni that many bytes.
              """)


eleza read_bytes4(f):
    r"""
    >>> agiza io
    >>> read_bytes4(io.BytesIO(b"\x00\x00\x00\x00abc"))
    b''
    >>> read_bytes4(io.BytesIO(b"\x03\x00\x00\x00abcdef"))
    b'abc'
    >>> read_bytes4(io.BytesIO(b"\x00\x00\x00\x03abcdef"))
    Traceback (most recent call last):
    ...
    ValueError: expected 50331648 bytes kwenye a bytes4, but only 6 remain
    """

    n = read_uint4(f)
    assert n >= 0
    ikiwa n > sys.maxsize:
        ashiria ValueError("bytes4 byte count > sys.maxsize: %d" % n)
    data = f.read(n)
    ikiwa len(data) == n:
        rudisha data
    ashiria ValueError("expected %d bytes kwenye a bytes4, but only %d remain" %
                     (n, len(data)))

bytes4 = ArgumentDescriptor(
              name="bytes4",
              n=TAKEN_FROM_ARGUMENT4U,
              reader=read_bytes4,
              doc="""A counted bytes string.

              The first argument ni a 4-byte little-endian unsigned int giving
              the number of bytes, na the second argument ni that many bytes.
              """)


eleza read_bytes8(f):
    r"""
    >>> agiza io, struct, sys
    >>> read_bytes8(io.BytesIO(b"\x00\x00\x00\x00\x00\x00\x00\x00abc"))
    b''
    >>> read_bytes8(io.BytesIO(b"\x03\x00\x00\x00\x00\x00\x00\x00abcdef"))
    b'abc'
    >>> bigsize8 = struct.pack("<Q", sys.maxsize//3)
    >>> read_bytes8(io.BytesIO(bigsize8 + b"abcdef"))  #doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: expected ... bytes kwenye a bytes8, but only 6 remain
    """

    n = read_uint8(f)
    assert n >= 0
    ikiwa n > sys.maxsize:
        ashiria ValueError("bytes8 byte count > sys.maxsize: %d" % n)
    data = f.read(n)
    ikiwa len(data) == n:
        rudisha data
    ashiria ValueError("expected %d bytes kwenye a bytes8, but only %d remain" %
                     (n, len(data)))

bytes8 = ArgumentDescriptor(
              name="bytes8",
              n=TAKEN_FROM_ARGUMENT8U,
              reader=read_bytes8,
              doc="""A counted bytes string.

              The first argument ni an 8-byte little-endian unsigned int giving
              the number of bytes, na the second argument ni that many bytes.
              """)


eleza read_bytearray8(f):
    r"""
    >>> agiza io, struct, sys
    >>> read_bytearray8(io.BytesIO(b"\x00\x00\x00\x00\x00\x00\x00\x00abc"))
    bytearray(b'')
    >>> read_bytearray8(io.BytesIO(b"\x03\x00\x00\x00\x00\x00\x00\x00abcdef"))
    bytearray(b'abc')
    >>> bigsize8 = struct.pack("<Q", sys.maxsize//3)
    >>> read_bytearray8(io.BytesIO(bigsize8 + b"abcdef"))  #doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: expected ... bytes kwenye a bytearray8, but only 6 remain
    """

    n = read_uint8(f)
    assert n >= 0
    ikiwa n > sys.maxsize:
        ashiria ValueError("bytearray8 byte count > sys.maxsize: %d" % n)
    data = f.read(n)
    ikiwa len(data) == n:
        rudisha bytearray(data)
    ashiria ValueError("expected %d bytes kwenye a bytearray8, but only %d remain" %
                     (n, len(data)))

bytearray8 = ArgumentDescriptor(
              name="bytearray8",
              n=TAKEN_FROM_ARGUMENT8U,
              reader=read_bytearray8,
              doc="""A counted bytearray.

              The first argument ni an 8-byte little-endian unsigned int giving
              the number of bytes, na the second argument ni that many bytes.
              """)

eleza read_unicodestringnl(f):
    r"""
    >>> agiza io
    >>> read_unicodestringnl(io.BytesIO(b"abc\\uabcd\njunk")) == 'abc\uabcd'
    Kweli
    """

    data = f.readline()
    ikiwa sio data.endswith(b'\n'):
        ashiria ValueError("no newline found when trying to read "
                         "unicodestringnl")
    data = data[:-1]    # lose the newline
    rudisha str(data, 'raw-unicode-escape')

unicodestringnl = ArgumentDescriptor(
                      name='unicodestringnl',
                      n=UP_TO_NEWLINE,
                      reader=read_unicodestringnl,
                      doc="""A newline-terminated Unicode string.

                      This ni raw-unicode-escape encoded, so consists of
                      printable ASCII characters, na may contain embedded
                      escape sequences.
                      """)


eleza read_unicodestring1(f):
    r"""
    >>> agiza io
    >>> s = 'abcd\uabcd'
    >>> enc = s.encode('utf-8')
    >>> enc
    b'abcd\xea\xaf\x8d'
    >>> n = bytes([len(enc)])  # little-endian 1-byte length
    >>> t = read_unicodestring1(io.BytesIO(n + enc + b'junk'))
    >>> s == t
    Kweli

    >>> read_unicodestring1(io.BytesIO(n + enc[:-1]))
    Traceback (most recent call last):
    ...
    ValueError: expected 7 bytes kwenye a unicodestring1, but only 6 remain
    """

    n = read_uint1(f)
    assert n >= 0
    data = f.read(n)
    ikiwa len(data) == n:
        rudisha str(data, 'utf-8', 'surrogatepita')
    ashiria ValueError("expected %d bytes kwenye a unicodestring1, but only %d "
                     "remain" % (n, len(data)))

unicodestring1 = ArgumentDescriptor(
                    name="unicodestring1",
                    n=TAKEN_FROM_ARGUMENT1,
                    reader=read_unicodestring1,
                    doc="""A counted Unicode string.

                    The first argument ni a 1-byte little-endian signed int
                    giving the number of bytes kwenye the string, na the second
                    argument-- the UTF-8 encoding of the Unicode string --
                    contains that many bytes.
                    """)


eleza read_unicodestring4(f):
    r"""
    >>> agiza io
    >>> s = 'abcd\uabcd'
    >>> enc = s.encode('utf-8')
    >>> enc
    b'abcd\xea\xaf\x8d'
    >>> n = bytes([len(enc), 0, 0, 0])  # little-endian 4-byte length
    >>> t = read_unicodestring4(io.BytesIO(n + enc + b'junk'))
    >>> s == t
    Kweli

    >>> read_unicodestring4(io.BytesIO(n + enc[:-1]))
    Traceback (most recent call last):
    ...
    ValueError: expected 7 bytes kwenye a unicodestring4, but only 6 remain
    """

    n = read_uint4(f)
    assert n >= 0
    ikiwa n > sys.maxsize:
        ashiria ValueError("unicodestring4 byte count > sys.maxsize: %d" % n)
    data = f.read(n)
    ikiwa len(data) == n:
        rudisha str(data, 'utf-8', 'surrogatepita')
    ashiria ValueError("expected %d bytes kwenye a unicodestring4, but only %d "
                     "remain" % (n, len(data)))

unicodestring4 = ArgumentDescriptor(
                    name="unicodestring4",
                    n=TAKEN_FROM_ARGUMENT4U,
                    reader=read_unicodestring4,
                    doc="""A counted Unicode string.

                    The first argument ni a 4-byte little-endian signed int
                    giving the number of bytes kwenye the string, na the second
                    argument-- the UTF-8 encoding of the Unicode string --
                    contains that many bytes.
                    """)


eleza read_unicodestring8(f):
    r"""
    >>> agiza io
    >>> s = 'abcd\uabcd'
    >>> enc = s.encode('utf-8')
    >>> enc
    b'abcd\xea\xaf\x8d'
    >>> n = bytes([len(enc)]) + b'\0' * 7  # little-endian 8-byte length
    >>> t = read_unicodestring8(io.BytesIO(n + enc + b'junk'))
    >>> s == t
    Kweli

    >>> read_unicodestring8(io.BytesIO(n + enc[:-1]))
    Traceback (most recent call last):
    ...
    ValueError: expected 7 bytes kwenye a unicodestring8, but only 6 remain
    """

    n = read_uint8(f)
    assert n >= 0
    ikiwa n > sys.maxsize:
        ashiria ValueError("unicodestring8 byte count > sys.maxsize: %d" % n)
    data = f.read(n)
    ikiwa len(data) == n:
        rudisha str(data, 'utf-8', 'surrogatepita')
    ashiria ValueError("expected %d bytes kwenye a unicodestring8, but only %d "
                     "remain" % (n, len(data)))

unicodestring8 = ArgumentDescriptor(
                    name="unicodestring8",
                    n=TAKEN_FROM_ARGUMENT8U,
                    reader=read_unicodestring8,
                    doc="""A counted Unicode string.

                    The first argument ni an 8-byte little-endian signed int
                    giving the number of bytes kwenye the string, na the second
                    argument-- the UTF-8 encoding of the Unicode string --
                    contains that many bytes.
                    """)


eleza read_decimalnl_short(f):
    r"""
    >>> agiza io
    >>> read_decimalnl_short(io.BytesIO(b"1234\n56"))
    1234

    >>> read_decimalnl_short(io.BytesIO(b"1234L\n56"))
    Traceback (most recent call last):
    ...
    ValueError: invalid literal kila int() ukijumuisha base 10: b'1234L'
    """

    s = read_stringnl(f, decode=Uongo, stripquotes=Uongo)

    # There's a hack kila Kweli na Uongo here.
    ikiwa s == b"00":
        rudisha Uongo
    lasivyo s == b"01":
        rudisha Kweli

    rudisha int(s)

eleza read_decimalnl_long(f):
    r"""
    >>> agiza io

    >>> read_decimalnl_long(io.BytesIO(b"1234L\n56"))
    1234

    >>> read_decimalnl_long(io.BytesIO(b"123456789012345678901234L\n6"))
    123456789012345678901234
    """

    s = read_stringnl(f, decode=Uongo, stripquotes=Uongo)
    ikiwa s[-1:] == b'L':
        s = s[:-1]
    rudisha int(s)


decimalnl_short = ArgumentDescriptor(
                      name='decimalnl_short',
                      n=UP_TO_NEWLINE,
                      reader=read_decimalnl_short,
                      doc="""A newline-terminated decimal integer literal.

                          This never has a trailing 'L', na the integer fit
                          kwenye a short Python int on the box where the pickle
                          was written -- but there's no guarantee it will fit
                          kwenye a short Python int on the box where the pickle
                          ni read.
                          """)

decimalnl_long = ArgumentDescriptor(
                     name='decimalnl_long',
                     n=UP_TO_NEWLINE,
                     reader=read_decimalnl_long,
                     doc="""A newline-terminated decimal integer literal.

                         This has a trailing 'L', na can represent integers
                         of any size.
                         """)


eleza read_floatnl(f):
    r"""
    >>> agiza io
    >>> read_floatnl(io.BytesIO(b"-1.25\n6"))
    -1.25
    """
    s = read_stringnl(f, decode=Uongo, stripquotes=Uongo)
    rudisha float(s)

floatnl = ArgumentDescriptor(
              name='floatnl',
              n=UP_TO_NEWLINE,
              reader=read_floatnl,
              doc="""A newline-terminated decimal floating literal.

              In general this requires 17 significant digits kila roundtrip
              identity, na pickling then unpickling infinities, NaNs, na
              minus zero doesn't work across boxes, ama on some boxes even
              on itself (e.g., Windows can't read the strings it produces
              kila infinities ama NaNs).
              """)

eleza read_float8(f):
    r"""
    >>> agiza io, struct
    >>> raw = struct.pack(">d", -1.25)
    >>> raw
    b'\xbf\xf4\x00\x00\x00\x00\x00\x00'
    >>> read_float8(io.BytesIO(raw + b"\n"))
    -1.25
    """

    data = f.read(8)
    ikiwa len(data) == 8:
        rudisha _unpack(">d", data)[0]
    ashiria ValueError("sio enough data kwenye stream to read float8")


float8 = ArgumentDescriptor(
             name='float8',
             n=8,
             reader=read_float8,
             doc="""An 8-byte binary representation of a float, big-endian.

             The format ni unique to Python, na shared ukijumuisha the struct
             module (format string '>d') "in theory" (the struct na pickle
             implementations don't share the code -- they should).  It's
             strongly related to the IEEE-754 double format, and, kwenye normal
             cases, ni kwenye fact identical to the big-endian 754 double format.
             On other boxes the dynamic range ni limited to that of a 754
             double, na "add a half na chop" rounding ni used to reduce
             the precision to 53 bits.  However, even on a 754 box,
             infinities, NaNs, na minus zero may sio be handled correctly
             (may sio survive roundtrip pickling intact).
             """)

# Protocol 2 formats

kutoka pickle agiza decode_long

eleza read_long1(f):
    r"""
    >>> agiza io
    >>> read_long1(io.BytesIO(b"\x00"))
    0
    >>> read_long1(io.BytesIO(b"\x02\xff\x00"))
    255
    >>> read_long1(io.BytesIO(b"\x02\xff\x7f"))
    32767
    >>> read_long1(io.BytesIO(b"\x02\x00\xff"))
    -256
    >>> read_long1(io.BytesIO(b"\x02\x00\x80"))
    -32768
    """

    n = read_uint1(f)
    data = f.read(n)
    ikiwa len(data) != n:
        ashiria ValueError("sio enough data kwenye stream to read long1")
    rudisha decode_long(data)

long1 = ArgumentDescriptor(
    name="long1",
    n=TAKEN_FROM_ARGUMENT1,
    reader=read_long1,
    doc="""A binary long, little-endian, using 1-byte size.

    This first reads one byte kama an unsigned size, then reads that
    many bytes na interprets them kama a little-endian 2's-complement long.
    If the size ni 0, that's taken kama a shortcut kila the long 0L.
    """)

eleza read_long4(f):
    r"""
    >>> agiza io
    >>> read_long4(io.BytesIO(b"\x02\x00\x00\x00\xff\x00"))
    255
    >>> read_long4(io.BytesIO(b"\x02\x00\x00\x00\xff\x7f"))
    32767
    >>> read_long4(io.BytesIO(b"\x02\x00\x00\x00\x00\xff"))
    -256
    >>> read_long4(io.BytesIO(b"\x02\x00\x00\x00\x00\x80"))
    -32768
    >>> read_long1(io.BytesIO(b"\x00\x00\x00\x00"))
    0
    """

    n = read_int4(f)
    ikiwa n < 0:
        ashiria ValueError("long4 byte count < 0: %d" % n)
    data = f.read(n)
    ikiwa len(data) != n:
        ashiria ValueError("sio enough data kwenye stream to read long4")
    rudisha decode_long(data)

long4 = ArgumentDescriptor(
    name="long4",
    n=TAKEN_FROM_ARGUMENT4,
    reader=read_long4,
    doc="""A binary representation of a long, little-endian.

    This first reads four bytes kama a signed size (but requires the
    size to be >= 0), then reads that many bytes na interprets them
    kama a little-endian 2's-complement long.  If the size ni 0, that's taken
    kama a shortcut kila the int 0, although LONG1 should really be used
    then instead (and kwenye any case where # of bytes < 256).
    """)


##############################################################################
# Object descriptors.  The stack used by the pickle machine holds objects,
# na kwenye the stack_before na stack_after attributes of OpcodeInfo
# descriptors we need names to describe the various types of objects that can
# appear on the stack.

kundi StackObject(object):
    __slots__ = (
        # name of descriptor record, kila info only
        'name',

        # type of object, ama tuple of type objects (meaning the object can
        # be of any type kwenye the tuple)
        'obtype',

        # human-readable docs kila this kind of stack object; a string
        'doc',
    )

    eleza __init__(self, name, obtype, doc):
        assert isinstance(name, str)
        self.name = name

        assert isinstance(obtype, type) ama isinstance(obtype, tuple)
        ikiwa isinstance(obtype, tuple):
            kila contained kwenye obtype:
                assert isinstance(contained, type)
        self.obtype = obtype

        assert isinstance(doc, str)
        self.doc = doc

    eleza __repr__(self):
        rudisha self.name


pyint = pylong = StackObject(
    name='int',
    obtype=int,
    doc="A Python integer object.")

pyinteger_or_bool = StackObject(
    name='int_or_bool',
    obtype=(int, bool),
    doc="A Python integer ama boolean object.")

pybool = StackObject(
    name='bool',
    obtype=bool,
    doc="A Python boolean object.")

pyfloat = StackObject(
    name='float',
    obtype=float,
    doc="A Python float object.")

pybytes_or_str = pystring = StackObject(
    name='bytes_or_str',
    obtype=(bytes, str),
    doc="A Python bytes ama (Unicode) string object.")

pybytes = StackObject(
    name='bytes',
    obtype=bytes,
    doc="A Python bytes object.")

pybytearray = StackObject(
    name='bytearray',
    obtype=bytearray,
    doc="A Python bytearray object.")

pyunicode = StackObject(
    name='str',
    obtype=str,
    doc="A Python (Unicode) string object.")

pynone = StackObject(
    name="Tupu",
    obtype=type(Tupu),
    doc="The Python Tupu object.")

pytuple = StackObject(
    name="tuple",
    obtype=tuple,
    doc="A Python tuple object.")

pylist = StackObject(
    name="list",
    obtype=list,
    doc="A Python list object.")

pydict = StackObject(
    name="dict",
    obtype=dict,
    doc="A Python dict object.")

pyset = StackObject(
    name="set",
    obtype=set,
    doc="A Python set object.")

pyfrozenset = StackObject(
    name="frozenset",
    obtype=set,
    doc="A Python frozenset object.")

pybuffer = StackObject(
    name='buffer',
    obtype=object,
    doc="A Python buffer-like object.")

anyobject = StackObject(
    name='any',
    obtype=object,
    doc="Any kind of object whatsoever.")

markobject = StackObject(
    name="mark",
    obtype=StackObject,
    doc="""'The mark' ni a unique object.

Opcodes that operate on a variable number of objects
generally don't embed the count of objects kwenye the opcode,
or pull it off the stack.  Instead the MARK opcode ni used
to push a special marker object on the stack, na then
some other opcodes grab all the objects kutoka the top of
the stack down to (but sio inluding) the topmost marker
object.
""")

stackslice = StackObject(
    name="stackslice",
    obtype=StackObject,
    doc="""An object representing a contiguous slice of the stack.

This ni used kwenye conjunction ukijumuisha markobject, to represent all
of the stack following the topmost markobject.  For example,
the POP_MARK opcode changes the stack from

    [..., markobject, stackslice]
to
    [...]

No matter how many object are on the stack after the topmost
markobject, POP_MARK gets rid of all of them (including the
topmost markobject too).
""")

##############################################################################
# Descriptors kila pickle opcodes.

kundi OpcodeInfo(object):

    __slots__ = (
        # symbolic name of opcode; a string
        'name',

        # the code used kwenye a bytestream to represent the opcode; a
        # one-character string
        'code',

        # If the opcode has an argument embedded kwenye the byte string, an
        # instance of ArgumentDescriptor specifying its type.  Note that
        # arg.reader(s) can be used to read na decode the argument from
        # the bytestream s, na arg.doc documents the format of the raw
        # argument bytes.  If the opcode doesn't have an argument embedded
        # kwenye the bytestream, arg should be Tupu.
        'arg',

        # what the stack looks like before this opcode runs; a list
        'stack_before',

        # what the stack looks like after this opcode runs; a list
        'stack_after',

        # the protocol number kwenye which this opcode was introduced; an int
        'proto',

        # human-readable docs kila this opcode; a string
        'doc',
    )

    eleza __init__(self, name, code, arg,
                 stack_before, stack_after, proto, doc):
        assert isinstance(name, str)
        self.name = name

        assert isinstance(code, str)
        assert len(code) == 1
        self.code = code

        assert arg ni Tupu ama isinstance(arg, ArgumentDescriptor)
        self.arg = arg

        assert isinstance(stack_before, list)
        kila x kwenye stack_before:
            assert isinstance(x, StackObject)
        self.stack_before = stack_before

        assert isinstance(stack_after, list)
        kila x kwenye stack_after:
            assert isinstance(x, StackObject)
        self.stack_after = stack_after

        assert isinstance(proto, int) na 0 <= proto <= pickle.HIGHEST_PROTOCOL
        self.proto = proto

        assert isinstance(doc, str)
        self.doc = doc

I = OpcodeInfo
opcodes = [

    # Ways to spell integers.

    I(name='INT',
      code='I',
      arg=decimalnl_short,
      stack_before=[],
      stack_after=[pyinteger_or_bool],
      proto=0,
      doc="""Push an integer ama bool.

      The argument ni a newline-terminated decimal literal string.

      The intent may have been that this always fit kwenye a short Python int,
      but INT can be generated kwenye pickles written on a 64-bit box that
      require a Python long on a 32-bit box.  The difference between this
      na LONG then ni that INT skips a trailing 'L', na produces a short
      int whenever possible.

      Another difference ni due to that, when bool was introduced kama a
      distinct type kwenye 2.3, builtin names Kweli na Uongo were also added to
      2.2.2, mapping to ints 1 na 0.  For compatibility kwenye both directions,
      Kweli gets pickled kama INT + "I01\\n", na Uongo kama INT + "I00\\n".
      Leading zeroes are never produced kila a genuine integer.  The 2.3
      (and later) unpicklers special-case these na rudisha bool instead;
      earlier unpicklers ignore the leading "0" na rudisha the int.
      """),

    I(name='BININT',
      code='J',
      arg=int4,
      stack_before=[],
      stack_after=[pyint],
      proto=1,
      doc="""Push a four-byte signed integer.

      This handles the full range of Python (short) integers on a 32-bit
      box, directly kama binary bytes (1 kila the opcode na 4 kila the integer).
      If the integer ni non-negative na fits kwenye 1 ama 2 bytes, pickling via
      BININT1 ama BININT2 saves space.
      """),

    I(name='BININT1',
      code='K',
      arg=uint1,
      stack_before=[],
      stack_after=[pyint],
      proto=1,
      doc="""Push a one-byte unsigned integer.

      This ni a space optimization kila pickling very small non-negative ints,
      kwenye range(256).
      """),

    I(name='BININT2',
      code='M',
      arg=uint2,
      stack_before=[],
      stack_after=[pyint],
      proto=1,
      doc="""Push a two-byte unsigned integer.

      This ni a space optimization kila pickling small positive ints, kwenye
      range(256, 2**16).  Integers kwenye range(256) can also be pickled via
      BININT2, but BININT1 instead saves a byte.
      """),

    I(name='LONG',
      code='L',
      arg=decimalnl_long,
      stack_before=[],
      stack_after=[pyint],
      proto=0,
      doc="""Push a long integer.

      The same kama INT, tatizo that the literal ends ukijumuisha 'L', na always
      unpickles to a Python long.  There doesn't seem a real purpose to the
      trailing 'L'.

      Note that LONG takes time quadratic kwenye the number of digits when
      unpickling (this ni simply due to the nature of decimal->binary
      conversion).  Proto 2 added linear-time (in C; still quadratic-time
      kwenye Python) LONG1 na LONG4 opcodes.
      """),

    I(name="LONG1",
      code='\x8a',
      arg=long1,
      stack_before=[],
      stack_after=[pyint],
      proto=2,
      doc="""Long integer using one-byte length.

      A more efficient encoding of a Python long; the long1 encoding
      says it all."""),

    I(name="LONG4",
      code='\x8b',
      arg=long4,
      stack_before=[],
      stack_after=[pyint],
      proto=2,
      doc="""Long integer using found-byte length.

      A more efficient encoding of a Python long; the long4 encoding
      says it all."""),

    # Ways to spell strings (8-bit, sio Unicode).

    I(name='STRING',
      code='S',
      arg=stringnl,
      stack_before=[],
      stack_after=[pybytes_or_str],
      proto=0,
      doc="""Push a Python string object.

      The argument ni a repr-style string, ukijumuisha bracketing quote characters,
      na perhaps embedded escapes.  The argument extends until the next
      newline character.  These are usually decoded into a str instance
      using the encoding given to the Unpickler constructor. ama the default,
      'ASCII'.  If the encoding given was 'bytes' however, they will be
      decoded kama bytes object instead.
      """),

    I(name='BINSTRING',
      code='T',
      arg=string4,
      stack_before=[],
      stack_after=[pybytes_or_str],
      proto=1,
      doc="""Push a Python string object.

      There are two arguments: the first ni a 4-byte little-endian
      signed int giving the number of bytes kwenye the string, na the
      second ni that many bytes, which are taken literally kama the string
      content.  These are usually decoded into a str instance using the
      encoding given to the Unpickler constructor. ama the default,
      'ASCII'.  If the encoding given was 'bytes' however, they will be
      decoded kama bytes object instead.
      """),

    I(name='SHORT_BINSTRING',
      code='U',
      arg=string1,
      stack_before=[],
      stack_after=[pybytes_or_str],
      proto=1,
      doc="""Push a Python string object.

      There are two arguments: the first ni a 1-byte unsigned int giving
      the number of bytes kwenye the string, na the second ni that many
      bytes, which are taken literally kama the string content.  These are
      usually decoded into a str instance using the encoding given to
      the Unpickler constructor. ama the default, 'ASCII'.  If the
      encoding given was 'bytes' however, they will be decoded kama bytes
      object instead.
      """),

    # Bytes (protocol 3 na higher)

    I(name='BINBYTES',
      code='B',
      arg=bytes4,
      stack_before=[],
      stack_after=[pybytes],
      proto=3,
      doc="""Push a Python bytes object.

      There are two arguments:  the first ni a 4-byte little-endian unsigned int
      giving the number of bytes, na the second ni that many bytes, which are
      taken literally kama the bytes content.
      """),

    I(name='SHORT_BINBYTES',
      code='C',
      arg=bytes1,
      stack_before=[],
      stack_after=[pybytes],
      proto=3,
      doc="""Push a Python bytes object.

      There are two arguments:  the first ni a 1-byte unsigned int giving
      the number of bytes, na the second ni that many bytes, which are taken
      literally kama the string content.
      """),

    I(name='BINBYTES8',
      code='\x8e',
      arg=bytes8,
      stack_before=[],
      stack_after=[pybytes],
      proto=4,
      doc="""Push a Python bytes object.

      There are two arguments:  the first ni an 8-byte unsigned int giving
      the number of bytes kwenye the string, na the second ni that many bytes,
      which are taken literally kama the string content.
      """),

    # Bytearray (protocol 5 na higher)

    I(name='BYTEARRAY8',
      code='\x96',
      arg=bytearray8,
      stack_before=[],
      stack_after=[pybytearray],
      proto=5,
      doc="""Push a Python bytearray object.

      There are two arguments:  the first ni an 8-byte unsigned int giving
      the number of bytes kwenye the bytearray, na the second ni that many bytes,
      which are taken literally kama the bytearray content.
      """),

    # Out-of-band buffer (protocol 5 na higher)

    I(name='NEXT_BUFFER',
      code='\x97',
      arg=Tupu,
      stack_before=[],
      stack_after=[pybuffer],
      proto=5,
      doc="Push an out-of-band buffer object."),

    I(name='READONLY_BUFFER',
      code='\x98',
      arg=Tupu,
      stack_before=[pybuffer],
      stack_after=[pybuffer],
      proto=5,
      doc="Make an out-of-band buffer object read-only."),

    # Ways to spell Tupu.

    I(name='NONE',
      code='N',
      arg=Tupu,
      stack_before=[],
      stack_after=[pynone],
      proto=0,
      doc="Push Tupu on the stack."),

    # Ways to spell bools, starting ukijumuisha proto 2.  See INT kila how this was
    # done before proto 2.

    I(name='NEWTRUE',
      code='\x88',
      arg=Tupu,
      stack_before=[],
      stack_after=[pybool],
      proto=2,
      doc="Push Kweli onto the stack."),

    I(name='NEWFALSE',
      code='\x89',
      arg=Tupu,
      stack_before=[],
      stack_after=[pybool],
      proto=2,
      doc="Push Uongo onto the stack."),

    # Ways to spell Unicode strings.

    I(name='UNICODE',
      code='V',
      arg=unicodestringnl,
      stack_before=[],
      stack_after=[pyunicode],
      proto=0,  # this may be pure-text, but it's a later addition
      doc="""Push a Python Unicode string object.

      The argument ni a raw-unicode-escape encoding of a Unicode string,
      na so may contain embedded escape sequences.  The argument extends
      until the next newline character.
      """),

    I(name='SHORT_BINUNICODE',
      code='\x8c',
      arg=unicodestring1,
      stack_before=[],
      stack_after=[pyunicode],
      proto=4,
      doc="""Push a Python Unicode string object.

      There are two arguments:  the first ni a 1-byte little-endian signed int
      giving the number of bytes kwenye the string.  The second ni that many
      bytes, na ni the UTF-8 encoding of the Unicode string.
      """),

    I(name='BINUNICODE',
      code='X',
      arg=unicodestring4,
      stack_before=[],
      stack_after=[pyunicode],
      proto=1,
      doc="""Push a Python Unicode string object.

      There are two arguments:  the first ni a 4-byte little-endian unsigned int
      giving the number of bytes kwenye the string.  The second ni that many
      bytes, na ni the UTF-8 encoding of the Unicode string.
      """),

    I(name='BINUNICODE8',
      code='\x8d',
      arg=unicodestring8,
      stack_before=[],
      stack_after=[pyunicode],
      proto=4,
      doc="""Push a Python Unicode string object.

      There are two arguments:  the first ni an 8-byte little-endian signed int
      giving the number of bytes kwenye the string.  The second ni that many
      bytes, na ni the UTF-8 encoding of the Unicode string.
      """),

    # Ways to spell floats.

    I(name='FLOAT',
      code='F',
      arg=floatnl,
      stack_before=[],
      stack_after=[pyfloat],
      proto=0,
      doc="""Newline-terminated decimal float literal.

      The argument ni repr(a_float), na kwenye general requires 17 significant
      digits kila roundtrip conversion to be an identity (this ni so for
      IEEE-754 double precision values, which ni what Python float maps to
      on most boxes).

      In general, FLOAT cannot be used to transport infinities, NaNs, ama
      minus zero across boxes (or even on a single box, ikiwa the platform C
      library can't read the strings it produces kila such things -- Windows
      ni like that), but may do less damage than BINFLOAT on boxes with
      greater precision ama dynamic range than IEEE-754 double.
      """),

    I(name='BINFLOAT',
      code='G',
      arg=float8,
      stack_before=[],
      stack_after=[pyfloat],
      proto=1,
      doc="""Float stored kwenye binary form, ukijumuisha 8 bytes of data.

      This generally requires less than half the space of FLOAT encoding.
      In general, BINFLOAT cannot be used to transport infinities, NaNs, ama
      minus zero, raises an exception ikiwa the exponent exceeds the range of
      an IEEE-754 double, na retains no more than 53 bits of precision (if
      there are more than that, "add a half na chop" rounding ni used to
      cut it back to 53 significant bits).
      """),

    # Ways to build lists.

    I(name='EMPTY_LIST',
      code=']',
      arg=Tupu,
      stack_before=[],
      stack_after=[pylist],
      proto=1,
      doc="Push an empty list."),

    I(name='APPEND',
      code='a',
      arg=Tupu,
      stack_before=[pylist, anyobject],
      stack_after=[pylist],
      proto=0,
      doc="""Append an object to a list.

      Stack before:  ... pylist anyobject
      Stack after:   ... pylist+[anyobject]

      although pylist ni really extended in-place.
      """),

    I(name='APPENDS',
      code='e',
      arg=Tupu,
      stack_before=[pylist, markobject, stackslice],
      stack_after=[pylist],
      proto=1,
      doc="""Extend a list by a slice of stack objects.

      Stack before:  ... pylist markobject stackslice
      Stack after:   ... pylist+stackslice

      although pylist ni really extended in-place.
      """),

    I(name='LIST',
      code='l',
      arg=Tupu,
      stack_before=[markobject, stackslice],
      stack_after=[pylist],
      proto=0,
      doc="""Build a list out of the topmost stack slice, after markobject.

      All the stack entries following the topmost markobject are placed into
      a single Python list, which single list object replaces all of the
      stack kutoka the topmost markobject onward.  For example,

      Stack before: ... markobject 1 2 3 'abc'
      Stack after:  ... [1, 2, 3, 'abc']
      """),

    # Ways to build tuples.

    I(name='EMPTY_TUPLE',
      code=')',
      arg=Tupu,
      stack_before=[],
      stack_after=[pytuple],
      proto=1,
      doc="Push an empty tuple."),

    I(name='TUPLE',
      code='t',
      arg=Tupu,
      stack_before=[markobject, stackslice],
      stack_after=[pytuple],
      proto=0,
      doc="""Build a tuple out of the topmost stack slice, after markobject.

      All the stack entries following the topmost markobject are placed into
      a single Python tuple, which single tuple object replaces all of the
      stack kutoka the topmost markobject onward.  For example,

      Stack before: ... markobject 1 2 3 'abc'
      Stack after:  ... (1, 2, 3, 'abc')
      """),

    I(name='TUPLE1',
      code='\x85',
      arg=Tupu,
      stack_before=[anyobject],
      stack_after=[pytuple],
      proto=2,
      doc="""Build a one-tuple out of the topmost item on the stack.

      This code pops one value off the stack na pushes a tuple of
      length 1 whose one item ni that value back onto it.  In other
      words:

          stack[-1] = tuple(stack[-1:])
      """),

    I(name='TUPLE2',
      code='\x86',
      arg=Tupu,
      stack_before=[anyobject, anyobject],
      stack_after=[pytuple],
      proto=2,
      doc="""Build a two-tuple out of the top two items on the stack.

      This code pops two values off the stack na pushes a tuple of
      length 2 whose items are those values back onto it.  In other
      words:

          stack[-2:] = [tuple(stack[-2:])]
      """),

    I(name='TUPLE3',
      code='\x87',
      arg=Tupu,
      stack_before=[anyobject, anyobject, anyobject],
      stack_after=[pytuple],
      proto=2,
      doc="""Build a three-tuple out of the top three items on the stack.

      This code pops three values off the stack na pushes a tuple of
      length 3 whose items are those values back onto it.  In other
      words:

          stack[-3:] = [tuple(stack[-3:])]
      """),

    # Ways to build dicts.

    I(name='EMPTY_DICT',
      code='}',
      arg=Tupu,
      stack_before=[],
      stack_after=[pydict],
      proto=1,
      doc="Push an empty dict."),

    I(name='DICT',
      code='d',
      arg=Tupu,
      stack_before=[markobject, stackslice],
      stack_after=[pydict],
      proto=0,
      doc="""Build a dict out of the topmost stack slice, after markobject.

      All the stack entries following the topmost markobject are placed into
      a single Python dict, which single dict object replaces all of the
      stack kutoka the topmost markobject onward.  The stack slice alternates
      key, value, key, value, ....  For example,

      Stack before: ... markobject 1 2 3 'abc'
      Stack after:  ... {1: 2, 3: 'abc'}
      """),

    I(name='SETITEM',
      code='s',
      arg=Tupu,
      stack_before=[pydict, anyobject, anyobject],
      stack_after=[pydict],
      proto=0,
      doc="""Add a key+value pair to an existing dict.

      Stack before:  ... pydict key value
      Stack after:   ... pydict

      where pydict has been modified via pydict[key] = value.
      """),

    I(name='SETITEMS',
      code='u',
      arg=Tupu,
      stack_before=[pydict, markobject, stackslice],
      stack_after=[pydict],
      proto=1,
      doc="""Add an arbitrary number of key+value pairs to an existing dict.

      The slice of the stack following the topmost markobject ni taken as
      an alternating sequence of keys na values, added to the dict
      immediately under the topmost markobject.  Everything at na after the
      topmost markobject ni popped, leaving the mutated dict at the top
      of the stack.

      Stack before:  ... pydict markobject key_1 value_1 ... key_n value_n
      Stack after:   ... pydict

      where pydict has been modified via pydict[key_i] = value_i kila i kwenye
      1, 2, ..., n, na kwenye that order.
      """),

    # Ways to build sets

    I(name='EMPTY_SET',
      code='\x8f',
      arg=Tupu,
      stack_before=[],
      stack_after=[pyset],
      proto=4,
      doc="Push an empty set."),

    I(name='ADDITEMS',
      code='\x90',
      arg=Tupu,
      stack_before=[pyset, markobject, stackslice],
      stack_after=[pyset],
      proto=4,
      doc="""Add an arbitrary number of items to an existing set.

      The slice of the stack following the topmost markobject ni taken as
      a sequence of items, added to the set immediately under the topmost
      markobject.  Everything at na after the topmost markobject ni popped,
      leaving the mutated set at the top of the stack.

      Stack before:  ... pyset markobject item_1 ... item_n
      Stack after:   ... pyset

      where pyset has been modified via pyset.add(item_i) = item_i kila i kwenye
      1, 2, ..., n, na kwenye that order.
      """),

    # Way to build frozensets

    I(name='FROZENSET',
      code='\x91',
      arg=Tupu,
      stack_before=[markobject, stackslice],
      stack_after=[pyfrozenset],
      proto=4,
      doc="""Build a frozenset out of the topmost slice, after markobject.

      All the stack entries following the topmost markobject are placed into
      a single Python frozenset, which single frozenset object replaces all
      of the stack kutoka the topmost markobject onward.  For example,

      Stack before: ... markobject 1 2 3
      Stack after:  ... frozenset({1, 2, 3})
      """),

    # Stack manipulation.

    I(name='POP',
      code='0',
      arg=Tupu,
      stack_before=[anyobject],
      stack_after=[],
      proto=0,
      doc="Discard the top stack item, shrinking the stack by one item."),

    I(name='DUP',
      code='2',
      arg=Tupu,
      stack_before=[anyobject],
      stack_after=[anyobject, anyobject],
      proto=0,
      doc="Push the top stack item onto the stack again, duplicating it."),

    I(name='MARK',
      code='(',
      arg=Tupu,
      stack_before=[],
      stack_after=[markobject],
      proto=0,
      doc="""Push markobject onto the stack.

      markobject ni a unique object, used by other opcodes to identify a
      region of the stack containing a variable number of objects kila them
      to work on.  See markobject.doc kila more detail.
      """),

    I(name='POP_MARK',
      code='1',
      arg=Tupu,
      stack_before=[markobject, stackslice],
      stack_after=[],
      proto=1,
      doc="""Pop all the stack objects at na above the topmost markobject.

      When an opcode using a variable number of stack objects ni done,
      POP_MARK ni used to remove those objects, na to remove the markobject
      that delimited their starting position on the stack.
      """),

    # Memo manipulation.  There are really only two operations (get na put),
    # each kwenye all-text, "short binary", na "long binary" flavors.

    I(name='GET',
      code='g',
      arg=decimalnl_short,
      stack_before=[],
      stack_after=[anyobject],
      proto=0,
      doc="""Read an object kutoka the memo na push it on the stack.

      The index of the memo object to push ni given by the newline-terminated
      decimal string following.  BINGET na LONG_BINGET are space-optimized
      versions.
      """),

    I(name='BINGET',
      code='h',
      arg=uint1,
      stack_before=[],
      stack_after=[anyobject],
      proto=1,
      doc="""Read an object kutoka the memo na push it on the stack.

      The index of the memo object to push ni given by the 1-byte unsigned
      integer following.
      """),

    I(name='LONG_BINGET',
      code='j',
      arg=uint4,
      stack_before=[],
      stack_after=[anyobject],
      proto=1,
      doc="""Read an object kutoka the memo na push it on the stack.

      The index of the memo object to push ni given by the 4-byte unsigned
      little-endian integer following.
      """),

    I(name='PUT',
      code='p',
      arg=decimalnl_short,
      stack_before=[],
      stack_after=[],
      proto=0,
      doc="""Store the stack top into the memo.  The stack ni sio popped.

      The index of the memo location to write into ni given by the newline-
      terminated decimal string following.  BINPUT na LONG_BINPUT are
      space-optimized versions.
      """),

    I(name='BINPUT',
      code='q',
      arg=uint1,
      stack_before=[],
      stack_after=[],
      proto=1,
      doc="""Store the stack top into the memo.  The stack ni sio popped.

      The index of the memo location to write into ni given by the 1-byte
      unsigned integer following.
      """),

    I(name='LONG_BINPUT',
      code='r',
      arg=uint4,
      stack_before=[],
      stack_after=[],
      proto=1,
      doc="""Store the stack top into the memo.  The stack ni sio popped.

      The index of the memo location to write into ni given by the 4-byte
      unsigned little-endian integer following.
      """),

    I(name='MEMOIZE',
      code='\x94',
      arg=Tupu,
      stack_before=[anyobject],
      stack_after=[anyobject],
      proto=4,
      doc="""Store the stack top into the memo.  The stack ni sio popped.

      The index of the memo location to write ni the number of
      elements currently present kwenye the memo.
      """),

    # Access the extension registry (predefined objects).  Akin to the GET
    # family.

    I(name='EXT1',
      code='\x82',
      arg=uint1,
      stack_before=[],
      stack_after=[anyobject],
      proto=2,
      doc="""Extension code.

      This code na the similar EXT2 na EXT4 allow using a registry
      of popular objects that are pickled by name, typically classes.
      It ni envisioned that through a global negotiation na
      registration process, third parties can set up a mapping between
      ints na object names.

      In order to guarantee pickle interchangeability, the extension
      code registry ought to be global, although a range of codes may
      be reserved kila private use.

      EXT1 has a 1-byte integer argument.  This ni used to index into the
      extension registry, na the object at that index ni pushed on the stack.
      """),

    I(name='EXT2',
      code='\x83',
      arg=uint2,
      stack_before=[],
      stack_after=[anyobject],
      proto=2,
      doc="""Extension code.

      See EXT1.  EXT2 has a two-byte integer argument.
      """),

    I(name='EXT4',
      code='\x84',
      arg=int4,
      stack_before=[],
      stack_after=[anyobject],
      proto=2,
      doc="""Extension code.

      See EXT1.  EXT4 has a four-byte integer argument.
      """),

    # Push a kundi object, ama module function, on the stack, via its module
    # na name.

    I(name='GLOBAL',
      code='c',
      arg=stringnl_noescape_pair,
      stack_before=[],
      stack_after=[anyobject],
      proto=0,
      doc="""Push a global object (module.attr) on the stack.

      Two newline-terminated strings follow the GLOBAL opcode.  The first is
      taken kama a module name, na the second kama a kundi name.  The class
      object module.kundi ni pushed on the stack.  More accurately, the
      object returned by self.find_class(module, class) ni pushed on the
      stack, so unpickling subclasses can override this form of lookup.
      """),

    I(name='STACK_GLOBAL',
      code='\x93',
      arg=Tupu,
      stack_before=[pyunicode, pyunicode],
      stack_after=[anyobject],
      proto=4,
      doc="""Push a global object (module.attr) on the stack.
      """),

    # Ways to build objects of classes pickle doesn't know about directly
    # (user-defined classes).  I despair of documenting this accurately
    # na comprehensibly -- you really have to read the pickle code to
    # find all the special cases.

    I(name='REDUCE',
      code='R',
      arg=Tupu,
      stack_before=[anyobject, anyobject],
      stack_after=[anyobject],
      proto=0,
      doc="""Push an object built kutoka a callable na an argument tuple.

      The opcode ni named to remind of the __reduce__() method.

      Stack before: ... callable pytuple
      Stack after:  ... callable(*pytuple)

      The callable na the argument tuple are the first two items returned
      by a __reduce__ method.  Applying the callable to the argtuple is
      supposed to reproduce the original object, ama at least get it started.
      If the __reduce__ method returns a 3-tuple, the last component ni an
      argument to be pitaed to the object's __setstate__, na then the REDUCE
      opcode ni followed by code to create setstate's argument, na then a
      BUILD opcode to apply  __setstate__ to that argument.

      If sio isinstance(callable, type), REDUCE complains unless the
      callable has been registered ukijumuisha the copyreg module's
      safe_constructors dict, ama the callable has a magic
      '__safe_for_unpickling__' attribute ukijumuisha a true value.  I'm sio sure
      why it does this, but I've sure seen this complaint often enough when
      I didn't want to <wink>.
      """),

    I(name='BUILD',
      code='b',
      arg=Tupu,
      stack_before=[anyobject, anyobject],
      stack_after=[anyobject],
      proto=0,
      doc="""Finish building an object, via __setstate__ ama dict update.

      Stack before: ... anyobject argument
      Stack after:  ... anyobject

      where anyobject may have been mutated, kama follows:

      If the object has a __setstate__ method,

          anyobject.__setstate__(argument)

      ni called.

      Else the argument must be a dict, the object must have a __dict__, na
      the object ni updated via

          anyobject.__dict__.update(argument)
      """),

    I(name='INST',
      code='i',
      arg=stringnl_noescape_pair,
      stack_before=[markobject, stackslice],
      stack_after=[anyobject],
      proto=0,
      doc="""Build a kundi instance.

      This ni the protocol 0 version of protocol 1's OBJ opcode.
      INST ni followed by two newline-terminated strings, giving a
      module na kundi name, just kama kila the GLOBAL opcode (and see
      GLOBAL kila more details about that).  self.find_class(module, name)
      ni used to get a kundi object.

      In addition, all the objects on the stack following the topmost
      markobject are gathered into a tuple na popped (along ukijumuisha the
      topmost markobject), just kama kila the TUPLE opcode.

      Now it gets complicated.  If all of these are true:

        + The argtuple ni empty (markobject was at the top of the stack
          at the start).

        + The kundi object does sio have a __getinitargs__ attribute.

      then we want to create an old-style kundi instance without invoking
      its __init__() method (pickle has waffled on this over the years; sio
      calling __init__() ni current wisdom).  In this case, an instance of
      an old-style dummy kundi ni created, na then we try to rebind its
      __class__ attribute to the desired kundi object.  If this succeeds,
      the new instance object ni pushed on the stack, na we're done.

      Else (the argtuple ni sio empty, it's sio an old-style kundi object,
      ama the kundi object does have a __getinitargs__ attribute), the code
      first insists that the kundi object have a __safe_for_unpickling__
      attribute.  Unlike kama kila the __safe_for_unpickling__ check kwenye REDUCE,
      it doesn't matter whether this attribute has a true ama false value, it
      only matters whether it exists (XXX this ni a bug).  If
      __safe_for_unpickling__ doesn't exist, UnpicklingError ni raised.

      Else (the kundi object does have a __safe_for_unpickling__ attr),
      the kundi object obtained kutoka INST's arguments ni applied to the
      argtuple obtained kutoka the stack, na the resulting instance object
      ni pushed on the stack.

      NOTE:  checks kila __safe_for_unpickling__ went away kwenye Python 2.3.
      NOTE:  the distinction between old-style na new-style classes does
             sio make sense kwenye Python 3.
      """),

    I(name='OBJ',
      code='o',
      arg=Tupu,
      stack_before=[markobject, anyobject, stackslice],
      stack_after=[anyobject],
      proto=1,
      doc="""Build a kundi instance.

      This ni the protocol 1 version of protocol 0's INST opcode, na is
      very much like it.  The major difference ni that the kundi object
      ni taken off the stack, allowing it to be retrieved kutoka the memo
      repeatedly ikiwa several instances of the same kundi are created.  This
      can be much more efficient (in both time na space) than repeatedly
      embedding the module na kundi names kwenye INST opcodes.

      Unlike INST, OBJ takes no arguments kutoka the opcode stream.  Instead
      the kundi object ni taken off the stack, immediately above the
      topmost markobject:

      Stack before: ... markobject classobject stackslice
      Stack after:  ... new_instance_object

      As kila INST, the remainder of the stack above the markobject is
      gathered into an argument tuple, na then the logic seems identical,
      tatizo that no __safe_for_unpickling__ check ni done (XXX this is
      a bug).  See INST kila the gory details.

      NOTE:  In Python 2.3, INST na OBJ are identical tatizo kila how they
      get the kundi object.  That was always the intent; the implementations
      had diverged kila accidental reasons.
      """),

    I(name='NEWOBJ',
      code='\x81',
      arg=Tupu,
      stack_before=[anyobject, anyobject],
      stack_after=[anyobject],
      proto=2,
      doc="""Build an object instance.

      The stack before should be thought of kama containing a class
      object followed by an argument tuple (the tuple being the stack
      top).  Call these cls na args.  They are popped off the stack,
      na the value returned by cls.__new__(cls, *args) ni pushed back
      onto the stack.
      """),

    I(name='NEWOBJ_EX',
      code='\x92',
      arg=Tupu,
      stack_before=[anyobject, anyobject, anyobject],
      stack_after=[anyobject],
      proto=4,
      doc="""Build an object instance.

      The stack before should be thought of kama containing a class
      object followed by an argument tuple na by a keyword argument dict
      (the dict being the stack top).  Call these cls na args.  They are
      popped off the stack, na the value returned by
      cls.__new__(cls, *args, *kwargs) ni  pushed back  onto the stack.
      """),

    # Machine control.

    I(name='PROTO',
      code='\x80',
      arg=uint1,
      stack_before=[],
      stack_after=[],
      proto=2,
      doc="""Protocol version indicator.

      For protocol 2 na above, a pickle must start ukijumuisha this opcode.
      The argument ni the protocol version, an int kwenye range(2, 256).
      """),

    I(name='STOP',
      code='.',
      arg=Tupu,
      stack_before=[anyobject],
      stack_after=[],
      proto=0,
      doc="""Stop the unpickling machine.

      Every pickle ends ukijumuisha this opcode.  The object at the top of the stack
      ni popped, na that's the result of unpickling.  The stack should be
      empty then.
      """),

    # Framing support.

    I(name='FRAME',
      code='\x95',
      arg=uint8,
      stack_before=[],
      stack_after=[],
      proto=4,
      doc="""Indicate the beginning of a new frame.

      The unpickler may use this opcode to safely prefetch data kutoka its
      underlying stream.
      """),

    # Ways to deal ukijumuisha persistent IDs.

    I(name='PERSID',
      code='P',
      arg=stringnl_noescape,
      stack_before=[],
      stack_after=[anyobject],
      proto=0,
      doc="""Push an object identified by a persistent ID.

      The pickle module doesn't define what a persistent ID means.  PERSID's
      argument ni a newline-terminated str-style (no embedded escapes, no
      bracketing quote characters) string, which *is* "the persistent ID".
      The unpickler pitaes this string to self.persistent_load().  Whatever
      object that returns ni pushed on the stack.  There ni no implementation
      of persistent_load() kwenye Python's unpickler:  it must be supplied by an
      unpickler subclass.
      """),

    I(name='BINPERSID',
      code='Q',
      arg=Tupu,
      stack_before=[anyobject],
      stack_after=[anyobject],
      proto=1,
      doc="""Push an object identified by a persistent ID.

      Like PERSID, tatizo the persistent ID ni popped off the stack (instead
      of being a string embedded kwenye the opcode bytestream).  The persistent
      ID ni pitaed to self.persistent_load(), na whatever object that
      returns ni pushed on the stack.  See PERSID kila more detail.
      """),
]
toa I

# Verify uniqueness of .name na .code members.
name2i = {}
code2i = {}

kila i, d kwenye enumerate(opcodes):
    ikiwa d.name kwenye name2i:
        ashiria ValueError("repeated name %r at indices %d na %d" %
                         (d.name, name2i[d.name], i))
    ikiwa d.code kwenye code2i:
        ashiria ValueError("repeated code %r at indices %d na %d" %
                         (d.code, code2i[d.code], i))

    name2i[d.name] = i
    code2i[d.code] = i

toa name2i, code2i, i, d

##############################################################################
# Build a code2op dict, mapping opcode characters to OpcodeInfo records.
# Also ensure we've got the same stuff kama pickle.py, although the
# introspection here ni dicey.

code2op = {}
kila d kwenye opcodes:
    code2op[d.code] = d
toa d

eleza assure_pickle_consistency(verbose=Uongo):

    copy = code2op.copy()
    kila name kwenye pickle.__all__:
        ikiwa sio re.match("[A-Z][A-Z0-9_]+$", name):
            ikiwa verbose:
                andika("skipping %r: it doesn't look like an opcode name" % name)
            endelea
        picklecode = getattr(pickle, name)
        ikiwa sio isinstance(picklecode, bytes) ama len(picklecode) != 1:
            ikiwa verbose:
                andika(("skipping %r: value %r doesn't look like a pickle "
                       "code" % (name, picklecode)))
            endelea
        picklecode = picklecode.decode("latin-1")
        ikiwa picklecode kwenye copy:
            ikiwa verbose:
                andika("checking name %r w/ code %r kila consistency" % (
                      name, picklecode))
            d = copy[picklecode]
            ikiwa d.name != name:
                ashiria ValueError("kila pickle code %r, pickle.py uses name %r "
                                 "but we're using name %r" % (picklecode,
                                                              name,
                                                              d.name))
            # Forget this one.  Any left over kwenye copy at the end are a problem
            # of a different kind.
            toa copy[picklecode]
        isipokua:
            ashiria ValueError("pickle.py appears to have a pickle opcode ukijumuisha "
                             "name %r na code %r, but we don't" %
                             (name, picklecode))
    ikiwa copy:
        msg = ["we appear to have pickle opcodes that pickle.py doesn't have:"]
        kila code, d kwenye copy.items():
            msg.append("    name %r ukijumuisha code %r" % (d.name, code))
        ashiria ValueError("\n".join(msg))

assure_pickle_consistency()
toa assure_pickle_consistency

##############################################################################
# A pickle opcode generator.

eleza _genops(data, tuma_end_pos=Uongo):
    ikiwa isinstance(data, bytes_types):
        data = io.BytesIO(data)

    ikiwa hasattr(data, "tell"):
        getpos = data.tell
    isipokua:
        getpos = lambda: Tupu

    wakati Kweli:
        pos = getpos()
        code = data.read(1)
        opcode = code2op.get(code.decode("latin-1"))
        ikiwa opcode ni Tupu:
            ikiwa code == b"":
                ashiria ValueError("pickle exhausted before seeing STOP")
            isipokua:
                ashiria ValueError("at position %s, opcode %r unknown" % (
                                 "<unknown>" ikiwa pos ni Tupu isipokua pos,
                                 code))
        ikiwa opcode.arg ni Tupu:
            arg = Tupu
        isipokua:
            arg = opcode.arg.reader(data)
        ikiwa tuma_end_pos:
            tuma opcode, arg, pos, getpos()
        isipokua:
            tuma opcode, arg, pos
        ikiwa code == b'.':
            assert opcode.name == 'STOP'
            koma

eleza genops(pickle):
    """Generate all the opcodes kwenye a pickle.

    'pickle' ni a file-like object, ama string, containing the pickle.

    Each opcode kwenye the pickle ni generated, kutoka the current pickle position,
    stopping after a STOP opcode ni delivered.  A triple ni generated for
    each opcode:

        opcode, arg, pos

    opcode ni an OpcodeInfo record, describing the current opcode.

    If the opcode has an argument embedded kwenye the pickle, arg ni its decoded
    value, kama a Python object.  If the opcode doesn't have an argument, arg
    ni Tupu.

    If the pickle has a tell() method, pos was the value of pickle.tell()
    before reading the current opcode.  If the pickle ni a bytes object,
    it's wrapped kwenye a BytesIO object, na the latter's tell() result is
    used.  Else (the pickle doesn't have a tell(), na it's sio obvious how
    to query its current position) pos ni Tupu.
    """
    rudisha _genops(pickle)

##############################################################################
# A pickle optimizer.

eleza optimize(p):
    'Optimize a pickle string by removing unused PUT opcodes'
    put = 'PUT'
    get = 'GET'
    oldids = set()          # set of all PUT ids
    newids = {}             # set of ids used by a GET opcode
    opcodes = []            # (op, idx) ama (pos, end_pos)
    proto = 0
    protoheader = b''
    kila opcode, arg, pos, end_pos kwenye _genops(p, tuma_end_pos=Kweli):
        ikiwa 'PUT' kwenye opcode.name:
            oldids.add(arg)
            opcodes.append((put, arg))
        lasivyo opcode.name == 'MEMOIZE':
            idx = len(oldids)
            oldids.add(idx)
            opcodes.append((put, idx))
        lasivyo 'FRAME' kwenye opcode.name:
            pita
        lasivyo 'GET' kwenye opcode.name:
            ikiwa opcode.proto > proto:
                proto = opcode.proto
            newids[arg] = Tupu
            opcodes.append((get, arg))
        lasivyo opcode.name == 'PROTO':
            ikiwa arg > proto:
                proto = arg
            ikiwa pos == 0:
                protoheader = p[pos:end_pos]
            isipokua:
                opcodes.append((pos, end_pos))
        isipokua:
            opcodes.append((pos, end_pos))
    toa oldids

    # Copy the opcodes tatizo kila PUTS without a corresponding GET
    out = io.BytesIO()
    # Write the PROTO header before any framing
    out.write(protoheader)
    pickler = pickle._Pickler(out, proto)
    ikiwa proto >= 4:
        pickler.framer.start_framing()
    idx = 0
    kila op, arg kwenye opcodes:
        frameless = Uongo
        ikiwa op ni put:
            ikiwa arg haiko kwenye newids:
                endelea
            data = pickler.put(idx)
            newids[arg] = idx
            idx += 1
        lasivyo op ni get:
            data = pickler.get(newids[arg])
        isipokua:
            data = p[op:arg]
            frameless = len(data) > pickler.framer._FRAME_SIZE_TARGET
        pickler.framer.commit_frame(force=frameless)
        ikiwa frameless:
            pickler.framer.file_write(data)
        isipokua:
            pickler.write(data)
    pickler.framer.end_framing()
    rudisha out.getvalue()

##############################################################################
# A symbolic pickle disassembler.

eleza dis(pickle, out=Tupu, memo=Tupu, indentlevel=4, annotate=0):
    """Produce a symbolic disassembly of a pickle.

    'pickle' ni a file-like object, ama string, containing a (at least one)
    pickle.  The pickle ni disassembled kutoka the current position, through
    the first STOP opcode encountered.

    Optional arg 'out' ni a file-like object to which the disassembly is
    printed.  It defaults to sys.stdout.

    Optional arg 'memo' ni a Python dict, used kama the pickle's memo.  It
    may be mutated by dis(), ikiwa the pickle contains PUT ama BINPUT opcodes.
    Passing the same memo object to another dis() call then allows disassembly
    to proceed across multiple pickles that were all created by the same
    pickler ukijumuisha the same memo.  Ordinarily you don't need to worry about this.

    Optional arg 'indentlevel' ni the number of blanks by which to indent
    a new MARK level.  It defaults to 4.

    Optional arg 'annotate' ikiwa nonzero instructs dis() to add short
    description of the opcode on each line of disassembled output.
    The value given to 'annotate' must be an integer na ni used kama a
    hint kila the column where annotation should start.  The default
    value ni 0, meaning no annotations.

    In addition to printing the disassembly, some sanity checks are made:

    + All embedded opcode arguments "make sense".

    + Explicit na implicit pop operations have enough items on the stack.

    + When an opcode implicitly refers to a markobject, a markobject is
      actually on the stack.

    + A memo entry isn't referenced before it's defined.

    + The markobject isn't stored kwenye the memo.

    + A memo entry isn't redefined.
    """

    # Most of the hair here ni kila sanity checks, but most of it ni needed
    # anyway to detect when a protocol 0 POP takes a MARK off the stack
    # (which kwenye turn ni needed to indent MARK blocks correctly).

    stack = []          # crude emulation of unpickler stack
    ikiwa memo ni Tupu:
        memo = {}       # crude emulation of unpickler memo
    maxproto = -1       # max protocol number seen
    markstack = []      # bytecode positions of MARK opcodes
    indentchunk = ' ' * indentlevel
    errormsg = Tupu
    annocol = annotate  # column hint kila annotations
    kila opcode, arg, pos kwenye genops(pickle):
        ikiwa pos ni sio Tupu:
            andika("%5d:" % pos, end=' ', file=out)

        line = "%-4s %s%s" % (repr(opcode.code)[1:-1],
                              indentchunk * len(markstack),
                              opcode.name)

        maxproto = max(maxproto, opcode.proto)
        before = opcode.stack_before    # don't mutate
        after = opcode.stack_after      # don't mutate
        numtopop = len(before)

        # See whether a MARK should be popped.
        markmsg = Tupu
        ikiwa markobject kwenye before ama (opcode.name == "POP" na
                                    stack na
                                    stack[-1] ni markobject):
            assert markobject haiko kwenye after
            ikiwa __debug__:
                ikiwa markobject kwenye before:
                    assert before[-1] ni stackslice
            ikiwa markstack:
                markpos = markstack.pop()
                ikiwa markpos ni Tupu:
                    markmsg = "(MARK at unknown opcode offset)"
                isipokua:
                    markmsg = "(MARK at %d)" % markpos
                # Pop everything at na after the topmost markobject.
                wakati stack[-1] ni sio markobject:
                    stack.pop()
                stack.pop()
                # Stop later code kutoka popping too much.
                jaribu:
                    numtopop = before.index(markobject)
                tatizo ValueError:
                    assert opcode.name == "POP"
                    numtopop = 0
            isipokua:
                errormsg = markmsg = "no MARK exists on stack"

        # Check kila correct memo usage.
        ikiwa opcode.name kwenye ("PUT", "BINPUT", "LONG_BINPUT", "MEMOIZE"):
            ikiwa opcode.name == "MEMOIZE":
                memo_idx = len(memo)
                markmsg = "(as %d)" % memo_idx
            isipokua:
                assert arg ni sio Tupu
                memo_idx = arg
            ikiwa memo_idx kwenye memo:
                errormsg = "memo key %r already defined" % arg
            lasivyo sio stack:
                errormsg = "stack ni empty -- can't store into memo"
            lasivyo stack[-1] ni markobject:
                errormsg = "can't store markobject kwenye the memo"
            isipokua:
                memo[memo_idx] = stack[-1]
        lasivyo opcode.name kwenye ("GET", "BINGET", "LONG_BINGET"):
            ikiwa arg kwenye memo:
                assert len(after) == 1
                after = [memo[arg]]     # kila better stack emulation
            isipokua:
                errormsg = "memo key %r has never been stored into" % arg

        ikiwa arg ni sio Tupu ama markmsg:
            # make a mild effort to align arguments
            line += ' ' * (10 - len(opcode.name))
            ikiwa arg ni sio Tupu:
                line += ' ' + repr(arg)
            ikiwa markmsg:
                line += ' ' + markmsg
        ikiwa annotate:
            line += ' ' * (annocol - len(line))
            # make a mild effort to align annotations
            annocol = len(line)
            ikiwa annocol > 50:
                annocol = annotate
            line += ' ' + opcode.doc.split('\n', 1)[0]
        andika(line, file=out)

        ikiwa errormsg:
            # Note that we delayed complaining until the offending opcode
            # was printed.
            ashiria ValueError(errormsg)

        # Emulate the stack effects.
        ikiwa len(stack) < numtopop:
            ashiria ValueError("tries to pop %d items kutoka stack ukijumuisha "
                             "only %d items" % (numtopop, len(stack)))
        ikiwa numtopop:
            toa stack[-numtopop:]
        ikiwa markobject kwenye after:
            assert markobject haiko kwenye before
            markstack.append(pos)

        stack.extend(after)

    andika("highest protocol among opcodes =", maxproto, file=out)
    ikiwa stack:
        ashiria ValueError("stack sio empty after STOP: %r" % stack)

# For use kwenye the doctest, simply kama an example of a kundi to pickle.
kundi _Example:
    eleza __init__(self, value):
        self.value = value

_dis_test = r"""
>>> agiza pickle
>>> x = [1, 2, (3, 4), {b'abc': "def"}]
>>> pkl0 = pickle.dumps(x, 0)
>>> dis(pkl0)
    0: (    MARK
    1: l        LIST       (MARK at 0)
    2: p    PUT        0
    5: I    INT        1
    8: a    APPEND
    9: I    INT        2
   12: a    APPEND
   13: (    MARK
   14: I        INT        3
   17: I        INT        4
   20: t        TUPLE      (MARK at 13)
   21: p    PUT        1
   24: a    APPEND
   25: (    MARK
   26: d        DICT       (MARK at 25)
   27: p    PUT        2
   30: c    GLOBAL     '_codecs encode'
   46: p    PUT        3
   49: (    MARK
   50: V        UNICODE    'abc'
   55: p        PUT        4
   58: V        UNICODE    'latin1'
   66: p        PUT        5
   69: t        TUPLE      (MARK at 49)
   70: p    PUT        6
   73: R    REDUCE
   74: p    PUT        7
   77: V    UNICODE    'def'
   82: p    PUT        8
   85: s    SETITEM
   86: a    APPEND
   87: .    STOP
highest protocol among opcodes = 0

Try again ukijumuisha a "binary" pickle.

>>> pkl1 = pickle.dumps(x, 1)
>>> dis(pkl1)
    0: ]    EMPTY_LIST
    1: q    BINPUT     0
    3: (    MARK
    4: K        BININT1    1
    6: K        BININT1    2
    8: (        MARK
    9: K            BININT1    3
   11: K            BININT1    4
   13: t            TUPLE      (MARK at 8)
   14: q        BINPUT     1
   16: }        EMPTY_DICT
   17: q        BINPUT     2
   19: c        GLOBAL     '_codecs encode'
   35: q        BINPUT     3
   37: (        MARK
   38: X            BINUNICODE 'abc'
   46: q            BINPUT     4
   48: X            BINUNICODE 'latin1'
   59: q            BINPUT     5
   61: t            TUPLE      (MARK at 37)
   62: q        BINPUT     6
   64: R        REDUCE
   65: q        BINPUT     7
   67: X        BINUNICODE 'def'
   75: q        BINPUT     8
   77: s        SETITEM
   78: e        APPENDS    (MARK at 3)
   79: .    STOP
highest protocol among opcodes = 1

Exercise the INST/OBJ/BUILD family.

>>> agiza pickletools
>>> dis(pickle.dumps(pickletools.dis, 0))
    0: c    GLOBAL     'pickletools dis'
   17: p    PUT        0
   20: .    STOP
highest protocol among opcodes = 0

>>> kutoka pickletools agiza _Example
>>> x = [_Example(42)] * 2
>>> dis(pickle.dumps(x, 0))
    0: (    MARK
    1: l        LIST       (MARK at 0)
    2: p    PUT        0
    5: c    GLOBAL     'copy_reg _reconstructor'
   30: p    PUT        1
   33: (    MARK
   34: c        GLOBAL     'pickletools _Example'
   56: p        PUT        2
   59: c        GLOBAL     '__builtin__ object'
   79: p        PUT        3
   82: N        NONE
   83: t        TUPLE      (MARK at 33)
   84: p    PUT        4
   87: R    REDUCE
   88: p    PUT        5
   91: (    MARK
   92: d        DICT       (MARK at 91)
   93: p    PUT        6
   96: V    UNICODE    'value'
  103: p    PUT        7
  106: I    INT        42
  110: s    SETITEM
  111: b    BUILD
  112: a    APPEND
  113: g    GET        5
  116: a    APPEND
  117: .    STOP
highest protocol among opcodes = 0

>>> dis(pickle.dumps(x, 1))
    0: ]    EMPTY_LIST
    1: q    BINPUT     0
    3: (    MARK
    4: c        GLOBAL     'copy_reg _reconstructor'
   29: q        BINPUT     1
   31: (        MARK
   32: c            GLOBAL     'pickletools _Example'
   54: q            BINPUT     2
   56: c            GLOBAL     '__builtin__ object'
   76: q            BINPUT     3
   78: N            NONE
   79: t            TUPLE      (MARK at 31)
   80: q        BINPUT     4
   82: R        REDUCE
   83: q        BINPUT     5
   85: }        EMPTY_DICT
   86: q        BINPUT     6
   88: X        BINUNICODE 'value'
   98: q        BINPUT     7
  100: K        BININT1    42
  102: s        SETITEM
  103: b        BUILD
  104: h        BINGET     5
  106: e        APPENDS    (MARK at 3)
  107: .    STOP
highest protocol among opcodes = 1

Try "the canonical" recursive-object test.

>>> L = []
>>> T = L,
>>> L.append(T)
>>> L[0] ni T
Kweli
>>> T[0] ni L
Kweli
>>> L[0][0] ni L
Kweli
>>> T[0][0] ni T
Kweli
>>> dis(pickle.dumps(L, 0))
    0: (    MARK
    1: l        LIST       (MARK at 0)
    2: p    PUT        0
    5: (    MARK
    6: g        GET        0
    9: t        TUPLE      (MARK at 5)
   10: p    PUT        1
   13: a    APPEND
   14: .    STOP
highest protocol among opcodes = 0

>>> dis(pickle.dumps(L, 1))
    0: ]    EMPTY_LIST
    1: q    BINPUT     0
    3: (    MARK
    4: h        BINGET     0
    6: t        TUPLE      (MARK at 3)
    7: q    BINPUT     1
    9: a    APPEND
   10: .    STOP
highest protocol among opcodes = 1

Note that, kwenye the protocol 0 pickle of the recursive tuple, the disassembler
has to emulate the stack kwenye order to realize that the POP opcode at 16 gets
rid of the MARK at 0.

>>> dis(pickle.dumps(T, 0))
    0: (    MARK
    1: (        MARK
    2: l            LIST       (MARK at 1)
    3: p        PUT        0
    6: (        MARK
    7: g            GET        0
   10: t            TUPLE      (MARK at 6)
   11: p        PUT        1
   14: a        APPEND
   15: 0        POP
   16: 0        POP        (MARK at 0)
   17: g    GET        1
   20: .    STOP
highest protocol among opcodes = 0

>>> dis(pickle.dumps(T, 1))
    0: (    MARK
    1: ]        EMPTY_LIST
    2: q        BINPUT     0
    4: (        MARK
    5: h            BINGET     0
    7: t            TUPLE      (MARK at 4)
    8: q        BINPUT     1
   10: a        APPEND
   11: 1        POP_MARK   (MARK at 0)
   12: h    BINGET     1
   14: .    STOP
highest protocol among opcodes = 1

Try protocol 2.

>>> dis(pickle.dumps(L, 2))
    0: \x80 PROTO      2
    2: ]    EMPTY_LIST
    3: q    BINPUT     0
    5: h    BINGET     0
    7: \x85 TUPLE1
    8: q    BINPUT     1
   10: a    APPEND
   11: .    STOP
highest protocol among opcodes = 2

>>> dis(pickle.dumps(T, 2))
    0: \x80 PROTO      2
    2: ]    EMPTY_LIST
    3: q    BINPUT     0
    5: h    BINGET     0
    7: \x85 TUPLE1
    8: q    BINPUT     1
   10: a    APPEND
   11: 0    POP
   12: h    BINGET     1
   14: .    STOP
highest protocol among opcodes = 2

Try protocol 3 ukijumuisha annotations:

>>> dis(pickle.dumps(T, 3), annotate=1)
    0: \x80 PROTO      3 Protocol version indicator.
    2: ]    EMPTY_LIST   Push an empty list.
    3: q    BINPUT     0 Store the stack top into the memo.  The stack ni sio popped.
    5: h    BINGET     0 Read an object kutoka the memo na push it on the stack.
    7: \x85 TUPLE1       Build a one-tuple out of the topmost item on the stack.
    8: q    BINPUT     1 Store the stack top into the memo.  The stack ni sio popped.
   10: a    APPEND       Append an object to a list.
   11: 0    POP          Discard the top stack item, shrinking the stack by one item.
   12: h    BINGET     1 Read an object kutoka the memo na push it on the stack.
   14: .    STOP         Stop the unpickling machine.
highest protocol among opcodes = 2

"""

_memo_test = r"""
>>> agiza pickle
>>> agiza io
>>> f = io.BytesIO()
>>> p = pickle.Pickler(f, 2)
>>> x = [1, 2, 3]
>>> p.dump(x)
>>> p.dump(x)
>>> f.seek(0)
0
>>> memo = {}
>>> dis(f, memo=memo)
    0: \x80 PROTO      2
    2: ]    EMPTY_LIST
    3: q    BINPUT     0
    5: (    MARK
    6: K        BININT1    1
    8: K        BININT1    2
   10: K        BININT1    3
   12: e        APPENDS    (MARK at 5)
   13: .    STOP
highest protocol among opcodes = 2
>>> dis(f, memo=memo)
   14: \x80 PROTO      2
   16: h    BINGET     0
   18: .    STOP
highest protocol among opcodes = 2
"""

__test__ = {'disassembler_test': _dis_test,
            'disassembler_memo_test': _memo_test,
           }

eleza _test():
    agiza doctest
    rudisha doctest.testmod()

ikiwa __name__ == "__main__":
    agiza argparse
    parser = argparse.ArgumentParser(
        description='disassemble one ama more pickle files')
    parser.add_argument(
        'pickle_file', type=argparse.FileType('br'),
        nargs='*', help='the pickle file')
    parser.add_argument(
        '-o', '--output', default=sys.stdout, type=argparse.FileType('w'),
        help='the file where the output should be written')
    parser.add_argument(
        '-m', '--memo', action='store_true',
        help='preserve memo between disassemblies')
    parser.add_argument(
        '-l', '--indentlevel', default=4, type=int,
        help='the number of blanks by which to indent a new MARK level')
    parser.add_argument(
        '-a', '--annotate',  action='store_true',
        help='annotate each line ukijumuisha a short opcode description')
    parser.add_argument(
        '-p', '--preamble', default="==> {name} <==",
        help='ikiwa more than one pickle file ni specified, andika this before'
        ' each disassembly')
    parser.add_argument(
        '-t', '--test', action='store_true',
        help='run self-test suite')
    parser.add_argument(
        '-v', action='store_true',
        help='run verbosely; only affects self-test run')
    args = parser.parse_args()
    ikiwa args.test:
        _test()
    isipokua:
        annotate = 30 ikiwa args.annotate isipokua 0
        ikiwa sio args.pickle_file:
            parser.print_help()
        lasivyo len(args.pickle_file) == 1:
            dis(args.pickle_file[0], args.output, Tupu,
                args.indentlevel, annotate)
        isipokua:
            memo = {} ikiwa args.memo isipokua Tupu
            kila f kwenye args.pickle_file:
                preamble = args.preamble.format(name=f.name)
                args.output.write(preamble + '\n')
                dis(f, args.output, memo, args.indentlevel, annotate)
