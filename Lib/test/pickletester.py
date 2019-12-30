agiza collections
agiza copyreg
agiza dbm
agiza io
agiza functools
agiza os
agiza math
agiza pickle
agiza pickletools
agiza shutil
agiza struct
agiza sys
agiza threading
agiza unittest
agiza weakref
kutoka textwrap agiza dedent
kutoka http.cookies agiza SimpleCookie

jaribu:
    agiza _testbuffer
tatizo ImportError:
    _testbuffer = Tupu

jaribu:
    agiza numpy kama np
tatizo ImportError:
    np = Tupu

kutoka test agiza support
kutoka test.support agiza (
    TestFailed, TESTFN, run_with_locale, no_tracing,
    _2G, _4G, bigmemtest, reap_threads, forget,
    )

kutoka pickle agiza bytes_types

requires_32b = unittest.skipUnless(sys.maxsize < 2**32,
                                   "test ni only meaningful on 32-bit builds")

# Tests that try a number of pickle protocols should have a
#     kila proto kwenye protocols:
# kind of outer loop.
protocols = range(pickle.HIGHEST_PROTOCOL + 1)


# Return Kweli ikiwa opcode code appears kwenye the pickle, isipokua Uongo.
eleza opcode_in_pickle(code, pickle):
    kila op, dummy, dummy kwenye pickletools.genops(pickle):
        ikiwa op.code == code.decode("latin-1"):
            rudisha Kweli
    rudisha Uongo

# Return the number of times opcode code appears kwenye pickle.
eleza count_opcode(code, pickle):
    n = 0
    kila op, dummy, dummy kwenye pickletools.genops(pickle):
        ikiwa op.code == code.decode("latin-1"):
            n += 1
    rudisha n


kundi UnseekableIO(io.BytesIO):
    eleza peek(self, *args):
        ashiria NotImplementedError

    eleza seekable(self):
        rudisha Uongo

    eleza seek(self, *args):
        ashiria io.UnsupportedOperation

    eleza tell(self):
        ashiria io.UnsupportedOperation


# We can't very well test the extension registry without putting known stuff
# kwenye it, but we have to be careful to restore its original state.  Code
# should do this:
#
#     e = ExtensionSaver(extension_code)
#     jaribu:
#         fiddle w/ the extension registry's stuff kila extension_code
#     mwishowe:
#         e.restore()

kundi ExtensionSaver:
    # Remember current registration kila code (ikiwa any), na remove it (if
    # there ni one).
    eleza __init__(self, code):
        self.code = code
        ikiwa code kwenye copyreg._inverted_regisjaribu:
            self.pair = copyreg._inverted_registry[code]
            copyreg.remove_extension(self.pair[0], self.pair[1], code)
        isipokua:
            self.pair = Tupu

    # Restore previous registration kila code.
    eleza restore(self):
        code = self.code
        curpair = copyreg._inverted_registry.get(code)
        ikiwa curpair ni sio Tupu:
            copyreg.remove_extension(curpair[0], curpair[1], code)
        pair = self.pair
        ikiwa pair ni sio Tupu:
            copyreg.add_extension(pair[0], pair[1], code)

kundi C:
    eleza __eq__(self, other):
        rudisha self.__dict__ == other.__dict__

kundi D(C):
    eleza __init__(self, arg):
        pita

kundi E(C):
    eleza __getinitargs__(self):
        rudisha ()

kundi H(object):
    pita

# Hashable mutable key
kundi K(object):
    eleza __init__(self, value):
        self.value = value

    eleza __reduce__(self):
        # Shouldn't support the recursion itself
        rudisha K, (self.value,)

agiza __main__
__main__.C = C
C.__module__ = "__main__"
__main__.D = D
D.__module__ = "__main__"
__main__.E = E
E.__module__ = "__main__"
__main__.H = H
H.__module__ = "__main__"
__main__.K = K
K.__module__ = "__main__"

kundi myint(int):
    eleza __init__(self, x):
        self.str = str(x)

kundi initarg(C):

    eleza __init__(self, a, b):
        self.a = a
        self.b = b

    eleza __getinitargs__(self):
        rudisha self.a, self.b

kundi metaclass(type):
    pita

kundi use_metaclass(object, metaclass=metaclass):
    pita

kundi pickling_metaclass(type):
    eleza __eq__(self, other):
        rudisha (type(self) == type(other) na
                self.reduce_args == other.reduce_args)

    eleza __reduce__(self):
        rudisha (create_dynamic_class, self.reduce_args)

eleza create_dynamic_class(name, bases):
    result = pickling_metaclass(name, bases, dict())
    result.reduce_args = (name, bases)
    rudisha result


kundi ZeroCopyBytes(bytes):
    readonly = Kweli
    c_contiguous = Kweli
    f_contiguous = Kweli
    zero_copy_reconstruct = Kweli

    eleza __reduce_ex__(self, protocol):
        ikiwa protocol >= 5:
            rudisha type(self)._reconstruct, (pickle.PickleBuffer(self),), Tupu
        isipokua:
            rudisha type(self)._reconstruct, (bytes(self),)

    eleza __repr__(self):
        rudisha "{}({!r})".format(self.__class__.__name__, bytes(self))

    __str__ = __repr__

    @classmethod
    eleza _reconstruct(cls, obj):
        ukijumuisha memoryview(obj) kama m:
            obj = m.obj
            ikiwa type(obj) ni cls:
                # Zero-copy
                rudisha obj
            isipokua:
                rudisha cls(obj)


kundi ZeroCopyBytearray(bytearray):
    readonly = Uongo
    c_contiguous = Kweli
    f_contiguous = Kweli
    zero_copy_reconstruct = Kweli

    eleza __reduce_ex__(self, protocol):
        ikiwa protocol >= 5:
            rudisha type(self)._reconstruct, (pickle.PickleBuffer(self),), Tupu
        isipokua:
            rudisha type(self)._reconstruct, (bytes(self),)

    eleza __repr__(self):
        rudisha "{}({!r})".format(self.__class__.__name__, bytes(self))

    __str__ = __repr__

    @classmethod
    eleza _reconstruct(cls, obj):
        ukijumuisha memoryview(obj) kama m:
            obj = m.obj
            ikiwa type(obj) ni cls:
                # Zero-copy
                rudisha obj
            isipokua:
                rudisha cls(obj)


ikiwa _testbuffer ni sio Tupu:

    kundi PicklableNDArray:
        # A not-really-zero-copy picklable ndarray, kama the ndarray()
        # constructor doesn't allow kila it

        zero_copy_reconstruct = Uongo

        eleza __init__(self, *args, **kwargs):
            self.array = _testbuffer.ndarray(*args, **kwargs)

        eleza __getitem__(self, idx):
            cls = type(self)
            new = cls.__new__(cls)
            new.array = self.array[idx]
            rudisha new

        @property
        eleza readonly(self):
            rudisha self.array.readonly

        @property
        eleza c_contiguous(self):
            rudisha self.array.c_contiguous

        @property
        eleza f_contiguous(self):
            rudisha self.array.f_contiguous

        eleza __eq__(self, other):
            ikiwa sio isinstance(other, PicklableNDArray):
                rudisha NotImplemented
            rudisha (other.array.format == self.array.format na
                    other.array.shape == self.array.shape na
                    other.array.strides == self.array.strides na
                    other.array.readonly == self.array.readonly na
                    other.array.tobytes() == self.array.tobytes())

        eleza __ne__(self, other):
            ikiwa sio isinstance(other, PicklableNDArray):
                rudisha NotImplemented
            rudisha sio (self == other)

        eleza __repr__(self):
            rudisha (f"{type(self)}(shape={self.array.shape},"
                    f"strides={self.array.strides}, "
                    f"bytes={self.array.tobytes()})")

        eleza __reduce_ex__(self, protocol):
            ikiwa sio self.array.contiguous:
                ashiria NotImplementedError("Reconstructing a non-contiguous "
                                          "ndarray does sio seem possible")
            ndarray_kwargs = {"shape": self.array.shape,
                              "strides": self.array.strides,
                              "format": self.array.format,
                              "flags": (0 ikiwa self.readonly
                                        isipokua _testbuffer.ND_WRITABLE)}
            pb = pickle.PickleBuffer(self.array)
            ikiwa protocol >= 5:
                rudisha (type(self)._reconstruct,
                        (pb, ndarray_kwargs))
            isipokua:
                # Need to serialize the bytes kwenye physical order
                ukijumuisha pb.raw() kama m:
                    rudisha (type(self)._reconstruct,
                            (m.tobytes(), ndarray_kwargs))

        @classmethod
        eleza _reconstruct(cls, obj, kwargs):
            ukijumuisha memoryview(obj) kama m:
                # For some reason, ndarray() wants a list of integers...
                # XXX This only works ikiwa format == 'B'
                items = list(m.tobytes())
            rudisha cls(items, **kwargs)


# DATA0 .. DATA4 are the pickles we expect under the various protocols, for
# the object returned by create_data().

DATA0 = (
    b'(lp0\nL0L\naL1L\naF2.0\n'
    b'ac__builtin__\ncomple'
    b'x\np1\n(F3.0\nF0.0\ntp2\n'
    b'Rp3\naL1L\naL-1L\naL255'
    b'L\naL-255L\naL-256L\naL'
    b'65535L\naL-65535L\naL-'
    b'65536L\naL2147483647L'
    b'\naL-2147483647L\naL-2'
    b'147483648L\na(Vabc\np4'
    b'\ng4\nccopy_reg\n_recon'
    b'structor\np5\n(c__main'
    b'__\nC\np6\nc__builtin__'
    b'\nobject\np7\nNtp8\nRp9\n'
    b'(dp10\nVfoo\np11\nL1L\ns'
    b'Vbar\np12\nL2L\nsbg9\ntp'
    b'13\nag13\naL5L\na.'
)

# Disassembly of DATA0
DATA0_DIS = """\
    0: (    MARK
    1: l        LIST       (MARK at 0)
    2: p    PUT        0
    5: L    LONG       0
    9: a    APPEND
   10: L    LONG       1
   14: a    APPEND
   15: F    FLOAT      2.0
   20: a    APPEND
   21: c    GLOBAL     '__builtin__ complex'
   42: p    PUT        1
   45: (    MARK
   46: F        FLOAT      3.0
   51: F        FLOAT      0.0
   56: t        TUPLE      (MARK at 45)
   57: p    PUT        2
   60: R    REDUCE
   61: p    PUT        3
   64: a    APPEND
   65: L    LONG       1
   69: a    APPEND
   70: L    LONG       -1
   75: a    APPEND
   76: L    LONG       255
   82: a    APPEND
   83: L    LONG       -255
   90: a    APPEND
   91: L    LONG       -256
   98: a    APPEND
   99: L    LONG       65535
  107: a    APPEND
  108: L    LONG       -65535
  117: a    APPEND
  118: L    LONG       -65536
  127: a    APPEND
  128: L    LONG       2147483647
  141: a    APPEND
  142: L    LONG       -2147483647
  156: a    APPEND
  157: L    LONG       -2147483648
  171: a    APPEND
  172: (    MARK
  173: V        UNICODE    'abc'
  178: p        PUT        4
  181: g        GET        4
  184: c        GLOBAL     'copy_reg _reconstructor'
  209: p        PUT        5
  212: (        MARK
  213: c            GLOBAL     '__main__ C'
  225: p            PUT        6
  228: c            GLOBAL     '__builtin__ object'
  248: p            PUT        7
  251: N            NONE
  252: t            TUPLE      (MARK at 212)
  253: p        PUT        8
  256: R        REDUCE
  257: p        PUT        9
  260: (        MARK
  261: d            DICT       (MARK at 260)
  262: p        PUT        10
  266: V        UNICODE    'foo'
  271: p        PUT        11
  275: L        LONG       1
  279: s        SETITEM
  280: V        UNICODE    'bar'
  285: p        PUT        12
  289: L        LONG       2
  293: s        SETITEM
  294: b        BUILD
  295: g        GET        9
  298: t        TUPLE      (MARK at 172)
  299: p    PUT        13
  303: a    APPEND
  304: g    GET        13
  308: a    APPEND
  309: L    LONG       5
  313: a    APPEND
  314: .    STOP
highest protocol among opcodes = 0
"""

DATA1 = (
    b']q\x00(K\x00K\x01G@\x00\x00\x00\x00\x00\x00\x00c__'
    b'builtin__\ncomplex\nq\x01'
    b'(G@\x08\x00\x00\x00\x00\x00\x00G\x00\x00\x00\x00\x00\x00\x00\x00t'
    b'q\x02Rq\x03K\x01J\xff\xff\xff\xffK\xffJ\x01\xff\xff\xffJ'
    b'\x00\xff\xff\xffM\xff\xffJ\x01\x00\xff\xffJ\x00\x00\xff\xffJ\xff\xff'
    b'\xff\x7fJ\x01\x00\x00\x80J\x00\x00\x00\x80(X\x03\x00\x00\x00ab'
    b'cq\x04h\x04ccopy_reg\n_reco'
    b'nstructor\nq\x05(c__main'
    b'__\nC\nq\x06c__builtin__\n'
    b'object\nq\x07Ntq\x08Rq\t}q\n('
    b'X\x03\x00\x00\x00fooq\x0bK\x01X\x03\x00\x00\x00bar'
    b'q\x0cK\x02ubh\ttq\rh\rK\x05e.'
)

# Disassembly of DATA1
DATA1_DIS = """\
    0: ]    EMPTY_LIST
    1: q    BINPUT     0
    3: (    MARK
    4: K        BININT1    0
    6: K        BININT1    1
    8: G        BINFLOAT   2.0
   17: c        GLOBAL     '__builtin__ complex'
   38: q        BINPUT     1
   40: (        MARK
   41: G            BINFLOAT   3.0
   50: G            BINFLOAT   0.0
   59: t            TUPLE      (MARK at 40)
   60: q        BINPUT     2
   62: R        REDUCE
   63: q        BINPUT     3
   65: K        BININT1    1
   67: J        BININT     -1
   72: K        BININT1    255
   74: J        BININT     -255
   79: J        BININT     -256
   84: M        BININT2    65535
   87: J        BININT     -65535
   92: J        BININT     -65536
   97: J        BININT     2147483647
  102: J        BININT     -2147483647
  107: J        BININT     -2147483648
  112: (        MARK
  113: X            BINUNICODE 'abc'
  121: q            BINPUT     4
  123: h            BINGET     4
  125: c            GLOBAL     'copy_reg _reconstructor'
  150: q            BINPUT     5
  152: (            MARK
  153: c                GLOBAL     '__main__ C'
  165: q                BINPUT     6
  167: c                GLOBAL     '__builtin__ object'
  187: q                BINPUT     7
  189: N                NONE
  190: t                TUPLE      (MARK at 152)
  191: q            BINPUT     8
  193: R            REDUCE
  194: q            BINPUT     9
  196: }            EMPTY_DICT
  197: q            BINPUT     10
  199: (            MARK
  200: X                BINUNICODE 'foo'
  208: q                BINPUT     11
  210: K                BININT1    1
  212: X                BINUNICODE 'bar'
  220: q                BINPUT     12
  222: K                BININT1    2
  224: u                SETITEMS   (MARK at 199)
  225: b            BUILD
  226: h            BINGET     9
  228: t            TUPLE      (MARK at 112)
  229: q        BINPUT     13
  231: h        BINGET     13
  233: K        BININT1    5
  235: e        APPENDS    (MARK at 3)
  236: .    STOP
highest protocol among opcodes = 1
"""

DATA2 = (
    b'\x80\x02]q\x00(K\x00K\x01G@\x00\x00\x00\x00\x00\x00\x00c'
    b'__builtin__\ncomplex\n'
    b'q\x01G@\x08\x00\x00\x00\x00\x00\x00G\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x86q\x02Rq\x03K\x01J\xff\xff\xff\xffK\xffJ\x01\xff\xff\xff'
    b'J\x00\xff\xff\xffM\xff\xffJ\x01\x00\xff\xffJ\x00\x00\xff\xffJ\xff'
    b'\xff\xff\x7fJ\x01\x00\x00\x80J\x00\x00\x00\x80(X\x03\x00\x00\x00a'
    b'bcq\x04h\x04c__main__\nC\nq\x05'
    b')\x81q\x06}q\x07(X\x03\x00\x00\x00fooq\x08K\x01'
    b'X\x03\x00\x00\x00barq\tK\x02ubh\x06tq\nh'
    b'\nK\x05e.'
)

# Disassembly of DATA2
DATA2_DIS = """\
    0: \x80 PROTO      2
    2: ]    EMPTY_LIST
    3: q    BINPUT     0
    5: (    MARK
    6: K        BININT1    0
    8: K        BININT1    1
   10: G        BINFLOAT   2.0
   19: c        GLOBAL     '__builtin__ complex'
   40: q        BINPUT     1
   42: G        BINFLOAT   3.0
   51: G        BINFLOAT   0.0
   60: \x86     TUPLE2
   61: q        BINPUT     2
   63: R        REDUCE
   64: q        BINPUT     3
   66: K        BININT1    1
   68: J        BININT     -1
   73: K        BININT1    255
   75: J        BININT     -255
   80: J        BININT     -256
   85: M        BININT2    65535
   88: J        BININT     -65535
   93: J        BININT     -65536
   98: J        BININT     2147483647
  103: J        BININT     -2147483647
  108: J        BININT     -2147483648
  113: (        MARK
  114: X            BINUNICODE 'abc'
  122: q            BINPUT     4
  124: h            BINGET     4
  126: c            GLOBAL     '__main__ C'
  138: q            BINPUT     5
  140: )            EMPTY_TUPLE
  141: \x81         NEWOBJ
  142: q            BINPUT     6
  144: }            EMPTY_DICT
  145: q            BINPUT     7
  147: (            MARK
  148: X                BINUNICODE 'foo'
  156: q                BINPUT     8
  158: K                BININT1    1
  160: X                BINUNICODE 'bar'
  168: q                BINPUT     9
  170: K                BININT1    2
  172: u                SETITEMS   (MARK at 147)
  173: b            BUILD
  174: h            BINGET     6
  176: t            TUPLE      (MARK at 113)
  177: q        BINPUT     10
  179: h        BINGET     10
  181: K        BININT1    5
  183: e        APPENDS    (MARK at 5)
  184: .    STOP
highest protocol among opcodes = 2
"""

DATA3 = (
    b'\x80\x03]q\x00(K\x00K\x01G@\x00\x00\x00\x00\x00\x00\x00c'
    b'builtins\ncomplex\nq\x01G'
    b'@\x08\x00\x00\x00\x00\x00\x00G\x00\x00\x00\x00\x00\x00\x00\x00\x86q\x02'
    b'Rq\x03K\x01J\xff\xff\xff\xffK\xffJ\x01\xff\xff\xffJ\x00\xff'
    b'\xff\xffM\xff\xffJ\x01\x00\xff\xffJ\x00\x00\xff\xffJ\xff\xff\xff\x7f'
    b'J\x01\x00\x00\x80J\x00\x00\x00\x80(X\x03\x00\x00\x00abcq'
    b'\x04h\x04c__main__\nC\nq\x05)\x81q'
    b'\x06}q\x07(X\x03\x00\x00\x00barq\x08K\x02X\x03\x00'
    b'\x00\x00fooq\tK\x01ubh\x06tq\nh\nK\x05'
    b'e.'
)

# Disassembly of DATA3
DATA3_DIS = """\
    0: \x80 PROTO      3
    2: ]    EMPTY_LIST
    3: q    BINPUT     0
    5: (    MARK
    6: K        BININT1    0
    8: K        BININT1    1
   10: G        BINFLOAT   2.0
   19: c        GLOBAL     'builtins complex'
   37: q        BINPUT     1
   39: G        BINFLOAT   3.0
   48: G        BINFLOAT   0.0
   57: \x86     TUPLE2
   58: q        BINPUT     2
   60: R        REDUCE
   61: q        BINPUT     3
   63: K        BININT1    1
   65: J        BININT     -1
   70: K        BININT1    255
   72: J        BININT     -255
   77: J        BININT     -256
   82: M        BININT2    65535
   85: J        BININT     -65535
   90: J        BININT     -65536
   95: J        BININT     2147483647
  100: J        BININT     -2147483647
  105: J        BININT     -2147483648
  110: (        MARK
  111: X            BINUNICODE 'abc'
  119: q            BINPUT     4
  121: h            BINGET     4
  123: c            GLOBAL     '__main__ C'
  135: q            BINPUT     5
  137: )            EMPTY_TUPLE
  138: \x81         NEWOBJ
  139: q            BINPUT     6
  141: }            EMPTY_DICT
  142: q            BINPUT     7
  144: (            MARK
  145: X                BINUNICODE 'bar'
  153: q                BINPUT     8
  155: K                BININT1    2
  157: X                BINUNICODE 'foo'
  165: q                BINPUT     9
  167: K                BININT1    1
  169: u                SETITEMS   (MARK at 144)
  170: b            BUILD
  171: h            BINGET     6
  173: t            TUPLE      (MARK at 110)
  174: q        BINPUT     10
  176: h        BINGET     10
  178: K        BININT1    5
  180: e        APPENDS    (MARK at 5)
  181: .    STOP
highest protocol among opcodes = 2
"""

DATA4 = (
    b'\x80\x04\x95\xa8\x00\x00\x00\x00\x00\x00\x00]\x94(K\x00K\x01G@'
    b'\x00\x00\x00\x00\x00\x00\x00\x8c\x08builtins\x94\x8c\x07'
    b'complex\x94\x93\x94G@\x08\x00\x00\x00\x00\x00\x00G'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x86\x94R\x94K\x01J\xff\xff\xff\xffK'
    b'\xffJ\x01\xff\xff\xffJ\x00\xff\xff\xffM\xff\xffJ\x01\x00\xff\xffJ'
    b'\x00\x00\xff\xffJ\xff\xff\xff\x7fJ\x01\x00\x00\x80J\x00\x00\x00\x80('
    b'\x8c\x03abc\x94h\x06\x8c\x08__main__\x94\x8c'
    b'\x01C\x94\x93\x94)\x81\x94}\x94(\x8c\x03bar\x94K\x02\x8c'
    b'\x03foo\x94K\x01ubh\nt\x94h\x0eK\x05e.'
)

# Disassembly of DATA4
DATA4_DIS = """\
    0: \x80 PROTO      4
    2: \x95 FRAME      168
   11: ]    EMPTY_LIST
   12: \x94 MEMOIZE
   13: (    MARK
   14: K        BININT1    0
   16: K        BININT1    1
   18: G        BINFLOAT   2.0
   27: \x8c     SHORT_BINUNICODE 'builtins'
   37: \x94     MEMOIZE
   38: \x8c     SHORT_BINUNICODE 'complex'
   47: \x94     MEMOIZE
   48: \x93     STACK_GLOBAL
   49: \x94     MEMOIZE
   50: G        BINFLOAT   3.0
   59: G        BINFLOAT   0.0
   68: \x86     TUPLE2
   69: \x94     MEMOIZE
   70: R        REDUCE
   71: \x94     MEMOIZE
   72: K        BININT1    1
   74: J        BININT     -1
   79: K        BININT1    255
   81: J        BININT     -255
   86: J        BININT     -256
   91: M        BININT2    65535
   94: J        BININT     -65535
   99: J        BININT     -65536
  104: J        BININT     2147483647
  109: J        BININT     -2147483647
  114: J        BININT     -2147483648
  119: (        MARK
  120: \x8c         SHORT_BINUNICODE 'abc'
  125: \x94         MEMOIZE
  126: h            BINGET     6
  128: \x8c         SHORT_BINUNICODE '__main__'
  138: \x94         MEMOIZE
  139: \x8c         SHORT_BINUNICODE 'C'
  142: \x94         MEMOIZE
  143: \x93         STACK_GLOBAL
  144: \x94         MEMOIZE
  145: )            EMPTY_TUPLE
  146: \x81         NEWOBJ
  147: \x94         MEMOIZE
  148: }            EMPTY_DICT
  149: \x94         MEMOIZE
  150: (            MARK
  151: \x8c             SHORT_BINUNICODE 'bar'
  156: \x94             MEMOIZE
  157: K                BININT1    2
  159: \x8c             SHORT_BINUNICODE 'foo'
  164: \x94             MEMOIZE
  165: K                BININT1    1
  167: u                SETITEMS   (MARK at 150)
  168: b            BUILD
  169: h            BINGET     10
  171: t            TUPLE      (MARK at 119)
  172: \x94     MEMOIZE
  173: h        BINGET     14
  175: K        BININT1    5
  177: e        APPENDS    (MARK at 13)
  178: .    STOP
highest protocol among opcodes = 4
"""

# set([1,2]) pickled kutoka 2.x ukijumuisha protocol 2
DATA_SET = b'\x80\x02c__builtin__\nset\nq\x00]q\x01(K\x01K\x02e\x85q\x02Rq\x03.'

# xrange(5) pickled kutoka 2.x ukijumuisha protocol 2
DATA_XRANGE = b'\x80\x02c__builtin__\nxrange\nq\x00K\x00K\x05K\x01\x87q\x01Rq\x02.'

# a SimpleCookie() object pickled kutoka 2.x ukijumuisha protocol 2
DATA_COOKIE = (b'\x80\x02cCookie\nSimpleCookie\nq\x00)\x81q\x01U\x03key'
               b'q\x02cCookie\nMorsel\nq\x03)\x81q\x04(U\x07commentq\x05U'
               b'\x00q\x06U\x06domainq\x07h\x06U\x06secureq\x08h\x06U\x07'
               b'expiresq\th\x06U\x07max-ageq\nh\x06U\x07versionq\x0bh\x06U'
               b'\x04pathq\x0ch\x06U\x08httponlyq\rh\x06u}q\x0e(U\x0b'
               b'coded_valueq\x0fU\x05valueq\x10h\x10h\x10h\x02h\x02ubs}q\x11b.')

# set([3]) pickled kutoka 2.x ukijumuisha protocol 2
DATA_SET2 = b'\x80\x02c__builtin__\nset\nq\x00]q\x01K\x03a\x85q\x02Rq\x03.'

python2_exceptions_without_args = (
    ArithmeticError,
    AssertionError,
    AttributeError,
    BaseException,
    BufferError,
    BytesWarning,
    DeprecationWarning,
    EOFError,
    EnvironmentError,
    Exception,
    FloatingPointError,
    FutureWarning,
    GeneratorExit,
    IOError,
    ImportError,
    ImportWarning,
    IndentationError,
    IndexError,
    KeyError,
    KeyboardInterrupt,
    LookupError,
    MemoryError,
    NameError,
    NotImplementedError,
    OSError,
    OverflowError,
    PendingDeprecationWarning,
    ReferenceError,
    RuntimeError,
    RuntimeWarning,
    # StandardError ni gone kwenye Python 3, we map it to Exception
    StopIteration,
    SyntaxError,
    SyntaxWarning,
    SystemError,
    SystemExit,
    TabError,
    TypeError,
    UnboundLocalError,
    UnicodeError,
    UnicodeWarning,
    UserWarning,
    ValueError,
    Warning,
    ZeroDivisionError,
)

exception_pickle = b'\x80\x02cexceptions\n?\nq\x00)Rq\x01.'

# UnicodeEncodeError object pickled kutoka 2.x ukijumuisha protocol 2
DATA_UEERR = (b'\x80\x02cexceptions\nUnicodeEncodeError\n'
              b'q\x00(U\x05asciiq\x01X\x03\x00\x00\x00fooq\x02K\x00K\x01'
              b'U\x03badq\x03tq\x04Rq\x05.')


eleza create_data():
    c = C()
    c.foo = 1
    c.bar = 2
    x = [0, 1, 2.0, 3.0+0j]
    # Append some integer test cases at cPickle.c's internal size
    # cutoffs.
    uint1max = 0xff
    uint2max = 0xffff
    int4max = 0x7fffffff
    x.extend([1, -1,
              uint1max, -uint1max, -uint1max-1,
              uint2max, -uint2max, -uint2max-1,
               int4max,  -int4max,  -int4max-1])
    y = ('abc', 'abc', c, c)
    x.append(y)
    x.append(y)
    x.append(5)
    rudisha x


kundi AbstractUnpickleTests(unittest.TestCase):
    # Subkundi must define self.loads.

    _testdata = create_data()

    eleza assert_is_copy(self, obj, objcopy, msg=Tupu):
        """Utility method to verify ikiwa two objects are copies of each others.
        """
        ikiwa msg ni Tupu:
            msg = "{!r} ni sio a copy of {!r}".format(obj, objcopy)
        self.assertEqual(obj, objcopy, msg=msg)
        self.assertIs(type(obj), type(objcopy), msg=msg)
        ikiwa hasattr(obj, '__dict__'):
            self.assertDictEqual(obj.__dict__, objcopy.__dict__, msg=msg)
            self.assertIsNot(obj.__dict__, objcopy.__dict__, msg=msg)
        ikiwa hasattr(obj, '__slots__'):
            self.assertListEqual(obj.__slots__, objcopy.__slots__, msg=msg)
            kila slot kwenye obj.__slots__:
                self.assertEqual(
                    hasattr(obj, slot), hasattr(objcopy, slot), msg=msg)
                self.assertEqual(getattr(obj, slot, Tupu),
                                 getattr(objcopy, slot, Tupu), msg=msg)

    eleza check_unpickling_error(self, errors, data):
        ukijumuisha self.subTest(data=data), \
             self.assertRaises(errors):
            jaribu:
                self.loads(data)
            tatizo BaseException kama exc:
                ikiwa support.verbose > 1:
                    andika('%-32r - %s: %s' %
                          (data, exc.__class__.__name__, exc))
                raise

    eleza test_load_from_data0(self):
        self.assert_is_copy(self._testdata, self.loads(DATA0))

    eleza test_load_from_data1(self):
        self.assert_is_copy(self._testdata, self.loads(DATA1))

    eleza test_load_from_data2(self):
        self.assert_is_copy(self._testdata, self.loads(DATA2))

    eleza test_load_from_data3(self):
        self.assert_is_copy(self._testdata, self.loads(DATA3))

    eleza test_load_from_data4(self):
        self.assert_is_copy(self._testdata, self.loads(DATA4))

    eleza test_load_classic_instance(self):
        # See issue5180.  Test loading 2.x pickles that
        # contain an instance of old style class.
        kila X, args kwenye [(C, ()), (D, ('x',)), (E, ())]:
            xname = X.__name__.encode('ascii')
            # Protocol 0 (text mode pickle):
            """
             0: (    MARK
             1: i        INST       '__main__ X' (MARK at 0)
            13: p    PUT        0
            16: (    MARK
            17: d        DICT       (MARK at 16)
            18: p    PUT        1
            21: b    BUILD
            22: .    STOP
            """
            pickle0 = (b"(i__main__\n"
                       b"X\n"
                       b"p0\n"
                       b"(dp1\nb.").replace(b'X', xname)
            self.assert_is_copy(X(*args), self.loads(pickle0))

            # Protocol 1 (binary mode pickle)
            """
             0: (    MARK
             1: c        GLOBAL     '__main__ X'
            13: q        BINPUT     0
            15: o        OBJ        (MARK at 0)
            16: q    BINPUT     1
            18: }    EMPTY_DICT
            19: q    BINPUT     2
            21: b    BUILD
            22: .    STOP
            """
            pickle1 = (b'(c__main__\n'
                       b'X\n'
                       b'q\x00oq\x01}q\x02b.').replace(b'X', xname)
            self.assert_is_copy(X(*args), self.loads(pickle1))

            # Protocol 2 (pickle2 = b'\x80\x02' + pickle1)
            """
             0: \x80 PROTO      2
             2: (    MARK
             3: c        GLOBAL     '__main__ X'
            15: q        BINPUT     0
            17: o        OBJ        (MARK at 2)
            18: q    BINPUT     1
            20: }    EMPTY_DICT
            21: q    BINPUT     2
            23: b    BUILD
            24: .    STOP
            """
            pickle2 = (b'\x80\x02(c__main__\n'
                       b'X\n'
                       b'q\x00oq\x01}q\x02b.').replace(b'X', xname)
            self.assert_is_copy(X(*args), self.loads(pickle2))

    eleza test_maxint64(self):
        maxint64 = (1 << 63) - 1
        data = b'I' + str(maxint64).encode("ascii") + b'\n.'
        got = self.loads(data)
        self.assert_is_copy(maxint64, got)

        # Try too ukijumuisha a bogus literal.
        data = b'I' + str(maxint64).encode("ascii") + b'JUNK\n.'
        self.check_unpickling_error(ValueError, data)

    eleza test_unpickle_from_2x(self):
        # Unpickle non-trivial data kutoka Python 2.x.
        loaded = self.loads(DATA_SET)
        self.assertEqual(loaded, set([1, 2]))
        loaded = self.loads(DATA_XRANGE)
        self.assertEqual(type(loaded), type(range(0)))
        self.assertEqual(list(loaded), list(range(5)))
        loaded = self.loads(DATA_COOKIE)
        self.assertEqual(type(loaded), SimpleCookie)
        self.assertEqual(list(loaded.keys()), ["key"])
        self.assertEqual(loaded["key"].value, "value")

        # Exception objects without arguments pickled kutoka 2.x ukijumuisha protocol 2
        kila exc kwenye python2_exceptions_without_args:
            data = exception_pickle.replace(b'?', exc.__name__.encode("ascii"))
            loaded = self.loads(data)
            self.assertIs(type(loaded), exc)

        # StandardError ni mapped to Exception, test that separately
        loaded = self.loads(exception_pickle.replace(b'?', b'StandardError'))
        self.assertIs(type(loaded), Exception)

        loaded = self.loads(DATA_UEERR)
        self.assertIs(type(loaded), UnicodeEncodeError)
        self.assertEqual(loaded.object, "foo")
        self.assertEqual(loaded.encoding, "ascii")
        self.assertEqual(loaded.start, 0)
        self.assertEqual(loaded.end, 1)
        self.assertEqual(loaded.reason, "bad")

    eleza test_load_python2_str_as_bytes(self):
        # From Python 2: pickle.dumps('a\x00\xa0', protocol=0)
        self.assertEqual(self.loads(b"S'a\\x00\\xa0'\n.",
                                    encoding="bytes"), b'a\x00\xa0')
        # From Python 2: pickle.dumps('a\x00\xa0', protocol=1)
        self.assertEqual(self.loads(b'U\x03a\x00\xa0.',
                                    encoding="bytes"), b'a\x00\xa0')
        # From Python 2: pickle.dumps('a\x00\xa0', protocol=2)
        self.assertEqual(self.loads(b'\x80\x02U\x03a\x00\xa0.',
                                    encoding="bytes"), b'a\x00\xa0')

    eleza test_load_python2_unicode_as_str(self):
        # From Python 2: pickle.dumps(u'π', protocol=0)
        self.assertEqual(self.loads(b'V\\u03c0\n.',
                                    encoding='bytes'), 'π')
        # From Python 2: pickle.dumps(u'π', protocol=1)
        self.assertEqual(self.loads(b'X\x02\x00\x00\x00\xcf\x80.',
                                    encoding="bytes"), 'π')
        # From Python 2: pickle.dumps(u'π', protocol=2)
        self.assertEqual(self.loads(b'\x80\x02X\x02\x00\x00\x00\xcf\x80.',
                                    encoding="bytes"), 'π')

    eleza test_load_long_python2_str_as_bytes(self):
        # From Python 2: pickle.dumps('x' * 300, protocol=1)
        self.assertEqual(self.loads(pickle.BINSTRING +
                                    struct.pack("<I", 300) +
                                    b'x' * 300 + pickle.STOP,
                                    encoding='bytes'), b'x' * 300)

    eleza test_constants(self):
        self.assertIsTupu(self.loads(b'N.'))
        self.assertIs(self.loads(b'\x88.'), Kweli)
        self.assertIs(self.loads(b'\x89.'), Uongo)
        self.assertIs(self.loads(b'I01\n.'), Kweli)
        self.assertIs(self.loads(b'I00\n.'), Uongo)

    eleza test_empty_bytestring(self):
        # issue 11286
        empty = self.loads(b'\x80\x03U\x00q\x00.', encoding='koi8-r')
        self.assertEqual(empty, '')

    eleza test_short_binbytes(self):
        dumped = b'\x80\x03C\x04\xe2\x82\xac\x00.'
        self.assertEqual(self.loads(dumped), b'\xe2\x82\xac\x00')

    eleza test_binbytes(self):
        dumped = b'\x80\x03B\x04\x00\x00\x00\xe2\x82\xac\x00.'
        self.assertEqual(self.loads(dumped), b'\xe2\x82\xac\x00')

    @requires_32b
    eleza test_negative_32b_binbytes(self):
        # On 32-bit builds, a BINBYTES of 2**31 ama more ni refused
        dumped = b'\x80\x03B\xff\xff\xff\xffxyzq\x00.'
        self.check_unpickling_error((pickle.UnpicklingError, OverflowError),
                                    dumped)

    @requires_32b
    eleza test_negative_32b_binunicode(self):
        # On 32-bit builds, a BINUNICODE of 2**31 ama more ni refused
        dumped = b'\x80\x03X\xff\xff\xff\xffxyzq\x00.'
        self.check_unpickling_error((pickle.UnpicklingError, OverflowError),
                                    dumped)

    eleza test_short_binunicode(self):
        dumped = b'\x80\x04\x8c\x04\xe2\x82\xac\x00.'
        self.assertEqual(self.loads(dumped), '\u20ac\x00')

    eleza test_misc_get(self):
        self.check_unpickling_error(KeyError, b'g0\np0')
        self.assert_is_copy([(100,), (100,)],
                            self.loads(b'((Kdtp0\nh\x00l.))'))

    eleza test_binbytes8(self):
        dumped = b'\x80\x04\x8e\4\0\0\0\0\0\0\0\xe2\x82\xac\x00.'
        self.assertEqual(self.loads(dumped), b'\xe2\x82\xac\x00')

    eleza test_binunicode8(self):
        dumped = b'\x80\x04\x8d\4\0\0\0\0\0\0\0\xe2\x82\xac\x00.'
        self.assertEqual(self.loads(dumped), '\u20ac\x00')

    eleza test_bytearray8(self):
        dumped = b'\x80\x05\x96\x03\x00\x00\x00\x00\x00\x00\x00xxx.'
        self.assertEqual(self.loads(dumped), bytearray(b'xxx'))

    @requires_32b
    eleza test_large_32b_binbytes8(self):
        dumped = b'\x80\x04\x8e\4\0\0\0\1\0\0\0\xe2\x82\xac\x00.'
        self.check_unpickling_error((pickle.UnpicklingError, OverflowError),
                                    dumped)

    @requires_32b
    eleza test_large_32b_bytearray8(self):
        dumped = b'\x80\x05\x96\4\0\0\0\1\0\0\0\xe2\x82\xac\x00.'
        self.check_unpickling_error((pickle.UnpicklingError, OverflowError),
                                    dumped)

    @requires_32b
    eleza test_large_32b_binunicode8(self):
        dumped = b'\x80\x04\x8d\4\0\0\0\1\0\0\0\xe2\x82\xac\x00.'
        self.check_unpickling_error((pickle.UnpicklingError, OverflowError),
                                    dumped)

    eleza test_get(self):
        pickled = b'((lp100000\ng100000\nt.'
        unpickled = self.loads(pickled)
        self.assertEqual(unpickled, ([],)*2)
        self.assertIs(unpickled[0], unpickled[1])

    eleza test_binget(self):
        pickled = b'(]q\xffh\xfft.'
        unpickled = self.loads(pickled)
        self.assertEqual(unpickled, ([],)*2)
        self.assertIs(unpickled[0], unpickled[1])

    eleza test_long_binget(self):
        pickled = b'(]r\x00\x00\x01\x00j\x00\x00\x01\x00t.'
        unpickled = self.loads(pickled)
        self.assertEqual(unpickled, ([],)*2)
        self.assertIs(unpickled[0], unpickled[1])

    eleza test_dup(self):
        pickled = b'((l2t.'
        unpickled = self.loads(pickled)
        self.assertEqual(unpickled, ([],)*2)
        self.assertIs(unpickled[0], unpickled[1])

    eleza test_negative_put(self):
        # Issue #12847
        dumped = b'Va\np-1\n.'
        self.check_unpickling_error(ValueError, dumped)

    @requires_32b
    eleza test_negative_32b_buliza(self):
        # Issue #12847
        dumped = b'\x80\x03X\x01\x00\x00\x00ar\xff\xff\xff\xff.'
        self.check_unpickling_error(ValueError, dumped)

    eleza test_badly_escaped_string(self):
        self.check_unpickling_error(ValueError, b"S'\\'\n.")

    eleza test_badly_quoted_string(self):
        # Issue #17710
        badpickles = [b"S'\n.",
                      b'S"\n.',
                      b'S\' \n.',
                      b'S" \n.',
                      b'S\'"\n.',
                      b'S"\'\n.',
                      b"S' ' \n.",
                      b'S" " \n.',
                      b"S ''\n.",
                      b'S ""\n.',
                      b'S \n.',
                      b'S\n.',
                      b'S.']
        kila p kwenye badpickles:
            self.check_unpickling_error(pickle.UnpicklingError, p)

    eleza test_correctly_quoted_string(self):
        goodpickles = [(b"S''\n.", ''),
                       (b'S""\n.', ''),
                       (b'S"\\n"\n.', '\n'),
                       (b"S'\\n'\n.", '\n')]
        kila p, expected kwenye goodpickles:
            self.assertEqual(self.loads(p), expected)

    eleza test_frame_readline(self):
        pickled = b'\x80\x04\x95\x05\x00\x00\x00\x00\x00\x00\x00I42\n.'
        #    0: \x80 PROTO      4
        #    2: \x95 FRAME      5
        #   11: I    INT        42
        #   15: .    STOP
        self.assertEqual(self.loads(pickled), 42)

    eleza test_compat_unpickle(self):
        # xrange(1, 7)
        pickled = b'\x80\x02c__builtin__\nxrange\nK\x01K\x07K\x01\x87R.'
        unpickled = self.loads(pickled)
        self.assertIs(type(unpickled), range)
        self.assertEqual(unpickled, range(1, 7))
        self.assertEqual(list(unpickled), [1, 2, 3, 4, 5, 6])
        # reduce
        pickled = b'\x80\x02c__builtin__\nreduce\n.'
        self.assertIs(self.loads(pickled), functools.reduce)
        # whichdb.whichdb
        pickled = b'\x80\x02cwhichdb\nwhichdb\n.'
        self.assertIs(self.loads(pickled), dbm.whichdb)
        # Exception(), StandardError()
        kila name kwenye (b'Exception', b'StandardError'):
            pickled = (b'\x80\x02cexceptions\n' + name + b'\nU\x03ugh\x85R.')
            unpickled = self.loads(pickled)
            self.assertIs(type(unpickled), Exception)
            self.assertEqual(str(unpickled), 'ugh')
        # UserDict.UserDict({1: 2}), UserDict.IterableUserDict({1: 2})
        kila name kwenye (b'UserDict', b'IterableUserDict'):
            pickled = (b'\x80\x02(cUserDict\n' + name +
                       b'\no}U\x04data}K\x01K\x02ssb.')
            unpickled = self.loads(pickled)
            self.assertIs(type(unpickled), collections.UserDict)
            self.assertEqual(unpickled, collections.UserDict({1: 2}))

    eleza test_bad_stack(self):
        badpickles = [
            b'.',                       # STOP
            b'0',                       # POP
            b'1',                       # POP_MARK
            b'2',                       # DUP
            b'(2',
            b'R',                       # REDUCE
            b')R',
            b'a',                       # APPEND
            b'Na',
            b'b',                       # BUILD
            b'Nb',
            b'd',                       # DICT
            b'e',                       # APPENDS
            b'(e',
            b'ibuiltins\nlist\n',       # INST
            b'l',                       # LIST
            b'o',                       # OBJ
            b'(o',
            b'p1\n',                    # PUT
            b'q\x00',                   # BINPUT
            b'r\x00\x00\x00\x00',       # LONG_BINPUT
            b's',                       # SETITEM
            b'Ns',
            b'NNs',
            b't',                       # TUPLE
            b'u',                       # SETITEMS
            b'(u',
            b'}(Nu',
            b'\x81',                    # NEWOBJ
            b')\x81',
            b'\x85',                    # TUPLE1
            b'\x86',                    # TUPLE2
            b'N\x86',
            b'\x87',                    # TUPLE3
            b'N\x87',
            b'NN\x87',
            b'\x90',                    # ADDITEMS
            b'(\x90',
            b'\x91',                    # FROZENSET
            b'\x92',                    # NEWOBJ_EX
            b')}\x92',
            b'\x93',                    # STACK_GLOBAL
            b'Vlist\n\x93',
            b'\x94',                    # MEMOIZE
        ]
        kila p kwenye badpickles:
            self.check_unpickling_error(self.bad_stack_errors, p)

    eleza test_bad_mark(self):
        badpickles = [
            b'N(.',                     # STOP
            b'N(2',                     # DUP
            b'cbuiltins\nlist\n)(R',    # REDUCE
            b'cbuiltins\nlist\n()R',
            b']N(a',                    # APPEND
                                        # BUILD
            b'cbuiltins\nValueError\n)R}(b',
            b'cbuiltins\nValueError\n)R(}b',
            b'(Nd',                     # DICT
            b'N(p1\n',                  # PUT
            b'N(q\x00',                 # BINPUT
            b'N(r\x00\x00\x00\x00',     # LONG_BINPUT
            b'}NN(s',                   # SETITEM
            b'}N(Ns',
            b'}(NNs',
            b'}((u',                    # SETITEMS
            b'cbuiltins\nlist\n)(\x81', # NEWOBJ
            b'cbuiltins\nlist\n()\x81',
            b'N(\x85',                  # TUPLE1
            b'NN(\x86',                 # TUPLE2
            b'N(N\x86',
            b'NNN(\x87',                # TUPLE3
            b'NN(N\x87',
            b'N(NN\x87',
            b']((\x90',                 # ADDITEMS
                                        # NEWOBJ_EX
            b'cbuiltins\nlist\n)}(\x92',
            b'cbuiltins\nlist\n)(}\x92',
            b'cbuiltins\nlist\n()}\x92',
                                        # STACK_GLOBAL
            b'Vbuiltins\n(Vlist\n\x93',
            b'Vbuiltins\nVlist\n(\x93',
            b'N(\x94',                  # MEMOIZE
        ]
        kila p kwenye badpickles:
            self.check_unpickling_error(self.bad_stack_errors, p)

    eleza test_truncated_data(self):
        self.check_unpickling_error(EOFError, b'')
        self.check_unpickling_error(EOFError, b'N')
        badpickles = [
            b'B',                       # BINBYTES
            b'B\x03\x00\x00',
            b'B\x03\x00\x00\x00',
            b'B\x03\x00\x00\x00ab',
            b'C',                       # SHORT_BINBYTES
            b'C\x03',
            b'C\x03ab',
            b'F',                       # FLOAT
            b'F0.0',
            b'F0.00',
            b'G',                       # BINFLOAT
            b'G\x00\x00\x00\x00\x00\x00\x00',
            b'I',                       # INT
            b'I0',
            b'J',                       # BININT
            b'J\x00\x00\x00',
            b'K',                       # BININT1
            b'L',                       # LONG
            b'L0',
            b'L10',
            b'L0L',
            b'L10L',
            b'M',                       # BININT2
            b'M\x00',
            # b'P',                       # PERSID
            # b'Pabc',
            b'S',                       # STRING
            b"S'abc'",
            b'T',                       # BINSTRING
            b'T\x03\x00\x00',
            b'T\x03\x00\x00\x00',
            b'T\x03\x00\x00\x00ab',
            b'U',                       # SHORT_BINSTRING
            b'U\x03',
            b'U\x03ab',
            b'V',                       # UNICODE
            b'Vabc',
            b'X',                       # BINUNICODE
            b'X\x03\x00\x00',
            b'X\x03\x00\x00\x00',
            b'X\x03\x00\x00\x00ab',
            b'(c',                      # GLOBAL
            b'(cbuiltins',
            b'(cbuiltins\n',
            b'(cbuiltins\nlist',
            b'Ng',                      # GET
            b'Ng0',
            b'(i',                      # INST
            b'(ibuiltins',
            b'(ibuiltins\n',
            b'(ibuiltins\nlist',
            b'Nh',                      # BINGET
            b'Nj',                      # LONG_BINGET
            b'Nj\x00\x00\x00',
            b'Np',                      # PUT
            b'Np0',
            b'Nq',                      # BINPUT
            b'Nr',                      # LONG_BINPUT
            b'Nr\x00\x00\x00',
            b'\x80',                    # PROTO
            b'\x82',                    # EXT1
            b'\x83',                    # EXT2
            b'\x84\x01',
            b'\x84',                    # EXT4
            b'\x84\x01\x00\x00',
            b'\x8a',                    # LONG1
            b'\x8b',                    # LONG4
            b'\x8b\x00\x00\x00',
            b'\x8c',                    # SHORT_BINUNICODE
            b'\x8c\x03',
            b'\x8c\x03ab',
            b'\x8d',                    # BINUNICODE8
            b'\x8d\x03\x00\x00\x00\x00\x00\x00',
            b'\x8d\x03\x00\x00\x00\x00\x00\x00\x00',
            b'\x8d\x03\x00\x00\x00\x00\x00\x00\x00ab',
            b'\x8e',                    # BINBYTES8
            b'\x8e\x03\x00\x00\x00\x00\x00\x00',
            b'\x8e\x03\x00\x00\x00\x00\x00\x00\x00',
            b'\x8e\x03\x00\x00\x00\x00\x00\x00\x00ab',
            b'\x96',                    # BYTEARRAY8
            b'\x96\x03\x00\x00\x00\x00\x00\x00',
            b'\x96\x03\x00\x00\x00\x00\x00\x00\x00',
            b'\x96\x03\x00\x00\x00\x00\x00\x00\x00ab',
            b'\x95',                    # FRAME
            b'\x95\x02\x00\x00\x00\x00\x00\x00',
            b'\x95\x02\x00\x00\x00\x00\x00\x00\x00',
            b'\x95\x02\x00\x00\x00\x00\x00\x00\x00N',
        ]
        kila p kwenye badpickles:
            self.check_unpickling_error(self.truncated_errors, p)

    @reap_threads
    eleza test_unpickle_module_race(self):
        # https://bugs.python.org/issue34572
        locker_module = dedent("""
        agiza threading
        barrier = threading.Barrier(2)
        """)
        locking_import_module = dedent("""
        agiza locker
        locker.barrier.wait()
        kundi ToBeUnpickled(object):
            pita
        """)

        os.mkdir(TESTFN)
        self.addCleanup(shutil.rmtree, TESTFN)
        sys.path.insert(0, TESTFN)
        self.addCleanup(sys.path.remove, TESTFN)
        ukijumuisha open(os.path.join(TESTFN, "locker.py"), "wb") kama f:
            f.write(locker_module.encode('utf-8'))
        ukijumuisha open(os.path.join(TESTFN, "locking_import.py"), "wb") kama f:
            f.write(locking_import_module.encode('utf-8'))
        self.addCleanup(forget, "locker")
        self.addCleanup(forget, "locking_import")

        agiza locker

        pickle_bytes = (
            b'\x80\x03clocking_import\nToBeUnpickled\nq\x00)\x81q\x01.')

        # Then try to unpickle two of these simultaneously
        # One of them will cause the module import, na we want it to block
        # until the other one either:
        #   - fails (before the patch kila this issue)
        #   - blocks on the agiza lock kila the module, kama it should
        results = []
        barrier = threading.Barrier(3)
        eleza t():
            # This ensures the threads have all started
            # presumably barrier release ni faster than thread startup
            barrier.wait()
            results.append(pickle.loads(pickle_bytes))

        t1 = threading.Thread(target=t)
        t2 = threading.Thread(target=t)
        t1.start()
        t2.start()

        barrier.wait()
        # could have delay here
        locker.barrier.wait()

        t1.join()
        t2.join()

        kutoka locking_agiza agiza ToBeUnpickled
        self.assertEqual(
            [type(x) kila x kwenye results],
            [ToBeUnpickled] * 2)



kundi AbstractPickleTests(unittest.TestCase):
    # Subkundi must define self.dumps, self.loads.

    optimized = Uongo

    _testdata = AbstractUnpickleTests._testdata

    eleza setUp(self):
        pita

    assert_is_copy = AbstractUnpickleTests.assert_is_copy

    eleza test_misc(self):
        # test various datatypes sio tested by testdata
        kila proto kwenye protocols:
            x = myint(4)
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assert_is_copy(x, y)

            x = (1, ())
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assert_is_copy(x, y)

            x = initarg(1, x)
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assert_is_copy(x, y)

        # XXX test __reduce__ protocol?

    eleza test_roundtrip_equality(self):
        expected = self._testdata
        kila proto kwenye protocols:
            s = self.dumps(expected, proto)
            got = self.loads(s)
            self.assert_is_copy(expected, got)

    # There are gratuitous differences between pickles produced by
    # pickle na cPickle, largely because cPickle starts PUT indices at
    # 1 na pickle starts them at 0.  See XXX comment kwenye cPickle's put2() --
    # there's a comment ukijumuisha an exclamation point there whose meaning
    # ni a mystery.  cPickle also suppresses PUT kila objects ukijumuisha a refcount
    # of 1.
    eleza dont_test_disassembly(self):
        kutoka io agiza StringIO
        kutoka pickletools agiza dis

        kila proto, expected kwenye (0, DATA0_DIS), (1, DATA1_DIS):
            s = self.dumps(self._testdata, proto)
            filelike = StringIO()
            dis(s, out=filelike)
            got = filelike.getvalue()
            self.assertEqual(expected, got)

    eleza test_recursive_list(self):
        l = []
        l.append(l)
        kila proto kwenye protocols:
            s = self.dumps(l, proto)
            x = self.loads(s)
            self.assertIsInstance(x, list)
            self.assertEqual(len(x), 1)
            self.assertIs(x[0], x)

    eleza test_recursive_tuple_and_list(self):
        t = ([],)
        t[0].append(t)
        kila proto kwenye protocols:
            s = self.dumps(t, proto)
            x = self.loads(s)
            self.assertIsInstance(x, tuple)
            self.assertEqual(len(x), 1)
            self.assertIsInstance(x[0], list)
            self.assertEqual(len(x[0]), 1)
            self.assertIs(x[0][0], x)

    eleza test_recursive_dict(self):
        d = {}
        d[1] = d
        kila proto kwenye protocols:
            s = self.dumps(d, proto)
            x = self.loads(s)
            self.assertIsInstance(x, dict)
            self.assertEqual(list(x.keys()), [1])
            self.assertIs(x[1], x)

    eleza test_recursive_dict_key(self):
        d = {}
        k = K(d)
        d[k] = 1
        kila proto kwenye protocols:
            s = self.dumps(d, proto)
            x = self.loads(s)
            self.assertIsInstance(x, dict)
            self.assertEqual(len(x.keys()), 1)
            self.assertIsInstance(list(x.keys())[0], K)
            self.assertIs(list(x.keys())[0].value, x)

    eleza test_recursive_set(self):
        y = set()
        k = K(y)
        y.add(k)
        kila proto kwenye range(4, pickle.HIGHEST_PROTOCOL + 1):
            s = self.dumps(y, proto)
            x = self.loads(s)
            self.assertIsInstance(x, set)
            self.assertEqual(len(x), 1)
            self.assertIsInstance(list(x)[0], K)
            self.assertIs(list(x)[0].value, x)

    eleza test_recursive_list_subclass(self):
        y = MyList()
        y.append(y)
        kila proto kwenye range(2, pickle.HIGHEST_PROTOCOL + 1):
            s = self.dumps(y, proto)
            x = self.loads(s)
            self.assertIsInstance(x, MyList)
            self.assertEqual(len(x), 1)
            self.assertIs(x[0], x)

    eleza test_recursive_dict_subclass(self):
        d = MyDict()
        d[1] = d
        kila proto kwenye range(2, pickle.HIGHEST_PROTOCOL + 1):
            s = self.dumps(d, proto)
            x = self.loads(s)
            self.assertIsInstance(x, MyDict)
            self.assertEqual(list(x.keys()), [1])
            self.assertIs(x[1], x)

    eleza test_recursive_dict_subclass_key(self):
        d = MyDict()
        k = K(d)
        d[k] = 1
        kila proto kwenye range(2, pickle.HIGHEST_PROTOCOL + 1):
            s = self.dumps(d, proto)
            x = self.loads(s)
            self.assertIsInstance(x, MyDict)
            self.assertEqual(len(list(x.keys())), 1)
            self.assertIsInstance(list(x.keys())[0], K)
            self.assertIs(list(x.keys())[0].value, x)

    eleza test_recursive_inst(self):
        i = C()
        i.attr = i
        kila proto kwenye protocols:
            s = self.dumps(i, proto)
            x = self.loads(s)
            self.assertIsInstance(x, C)
            self.assertEqual(dir(x), dir(i))
            self.assertIs(x.attr, x)

    eleza test_recursive_multi(self):
        l = []
        d = {1:l}
        i = C()
        i.attr = d
        l.append(i)
        kila proto kwenye protocols:
            s = self.dumps(l, proto)
            x = self.loads(s)
            self.assertIsInstance(x, list)
            self.assertEqual(len(x), 1)
            self.assertEqual(dir(x[0]), dir(i))
            self.assertEqual(list(x[0].attr.keys()), [1])
            self.assertKweli(x[0].attr[1] ni x)

    eleza check_recursive_collection_and_inst(self, factory):
        h = H()
        y = factory([h])
        h.attr = y
        kila proto kwenye protocols:
            s = self.dumps(y, proto)
            x = self.loads(s)
            self.assertIsInstance(x, type(y))
            self.assertEqual(len(x), 1)
            self.assertIsInstance(list(x)[0], H)
            self.assertIs(list(x)[0].attr, x)

    eleza test_recursive_list_and_inst(self):
        self.check_recursive_collection_and_inst(list)

    eleza test_recursive_tuple_and_inst(self):
        self.check_recursive_collection_and_inst(tuple)

    eleza test_recursive_dict_and_inst(self):
        self.check_recursive_collection_and_inst(dict.fromkeys)

    eleza test_recursive_set_and_inst(self):
        self.check_recursive_collection_and_inst(set)

    eleza test_recursive_frozenset_and_inst(self):
        self.check_recursive_collection_and_inst(frozenset)

    eleza test_recursive_list_subclass_and_inst(self):
        self.check_recursive_collection_and_inst(MyList)

    eleza test_recursive_tuple_subclass_and_inst(self):
        self.check_recursive_collection_and_inst(MyTuple)

    eleza test_recursive_dict_subclass_and_inst(self):
        self.check_recursive_collection_and_inst(MyDict.fromkeys)

    eleza test_recursive_set_subclass_and_inst(self):
        self.check_recursive_collection_and_inst(MySet)

    eleza test_recursive_frozenset_subclass_and_inst(self):
        self.check_recursive_collection_and_inst(MyFrozenSet)

    eleza test_unicode(self):
        endcases = ['', '<\\u>', '<\\\u1234>', '<\n>',
                    '<\\>', '<\\\U00012345>',
                    # surrogates
                    '<\udc80>']
        kila proto kwenye protocols:
            kila u kwenye endcases:
                p = self.dumps(u, proto)
                u2 = self.loads(p)
                self.assert_is_copy(u, u2)

    eleza test_unicode_high_plane(self):
        t = '\U00012345'
        kila proto kwenye protocols:
            p = self.dumps(t, proto)
            t2 = self.loads(p)
            self.assert_is_copy(t, t2)

    eleza test_bytes(self):
        kila proto kwenye protocols:
            kila s kwenye b'', b'xyz', b'xyz'*100:
                p = self.dumps(s, proto)
                self.assert_is_copy(s, self.loads(p))
            kila s kwenye [bytes([i]) kila i kwenye range(256)]:
                p = self.dumps(s, proto)
                self.assert_is_copy(s, self.loads(p))
            kila s kwenye [bytes([i, i]) kila i kwenye range(256)]:
                p = self.dumps(s, proto)
                self.assert_is_copy(s, self.loads(p))

    eleza test_bytearray(self):
        kila proto kwenye protocols:
            kila s kwenye b'', b'xyz', b'xyz'*100:
                b = bytearray(s)
                p = self.dumps(b, proto)
                bb = self.loads(p)
                self.assertIsNot(bb, b)
                self.assert_is_copy(b, bb)
                ikiwa proto <= 3:
                    # bytearray ni serialized using a global reference
                    self.assertIn(b'bytearray', p)
                    self.assertKweli(opcode_in_pickle(pickle.GLOBAL, p))
                lasivyo proto == 4:
                    self.assertIn(b'bytearray', p)
                    self.assertKweli(opcode_in_pickle(pickle.STACK_GLOBAL, p))
                lasivyo proto == 5:
                    self.assertNotIn(b'bytearray', p)
                    self.assertKweli(opcode_in_pickle(pickle.BYTEARRAY8, p))

    eleza test_ints(self):
        kila proto kwenye protocols:
            n = sys.maxsize
            wakati n:
                kila expected kwenye (-n, n):
                    s = self.dumps(expected, proto)
                    n2 = self.loads(s)
                    self.assert_is_copy(expected, n2)
                n = n >> 1

    eleza test_long(self):
        kila proto kwenye protocols:
            # 256 bytes ni where LONG4 begins.
            kila nbits kwenye 1, 8, 8*254, 8*255, 8*256, 8*257:
                nbase = 1 << nbits
                kila npos kwenye nbase-1, nbase, nbase+1:
                    kila n kwenye npos, -npos:
                        pickle = self.dumps(n, proto)
                        got = self.loads(pickle)
                        self.assert_is_copy(n, got)
        # Try a monster.  This ni quadratic-time kwenye protos 0 & 1, so don't
        # bother ukijumuisha those.
        nbase = int("deadbeeffeedface", 16)
        nbase += nbase << 1000000
        kila n kwenye nbase, -nbase:
            p = self.dumps(n, 2)
            got = self.loads(p)
            # assert_is_copy ni very expensive here kama it precomputes
            # a failure message by computing the repr() of n na got,
            # we just do the check ourselves.
            self.assertIs(type(got), int)
            self.assertEqual(n, got)

    eleza test_float(self):
        test_values = [0.0, 4.94e-324, 1e-310, 7e-308, 6.626e-34, 0.1, 0.5,
                       3.14, 263.44582062374053, 6.022e23, 1e30]
        test_values = test_values + [-x kila x kwenye test_values]
        kila proto kwenye protocols:
            kila value kwenye test_values:
                pickle = self.dumps(value, proto)
                got = self.loads(pickle)
                self.assert_is_copy(value, got)

    @run_with_locale('LC_ALL', 'de_DE', 'fr_FR')
    eleza test_float_format(self):
        # make sure that floats are formatted locale independent ukijumuisha proto 0
        self.assertEqual(self.dumps(1.2, 0)[0:3], b'F1.')

    eleza test_reduce(self):
        kila proto kwenye protocols:
            inst = AAA()
            dumped = self.dumps(inst, proto)
            loaded = self.loads(dumped)
            self.assertEqual(loaded, REDUCE_A)

    eleza test_getinitargs(self):
        kila proto kwenye protocols:
            inst = initarg(1, 2)
            dumped = self.dumps(inst, proto)
            loaded = self.loads(dumped)
            self.assert_is_copy(inst, loaded)

    eleza test_metaclass(self):
        a = use_metaclass()
        kila proto kwenye protocols:
            s = self.dumps(a, proto)
            b = self.loads(s)
            self.assertEqual(a.__class__, b.__class__)

    eleza test_dynamic_class(self):
        a = create_dynamic_class("my_dynamic_class", (object,))
        copyreg.pickle(pickling_metaclass, pickling_metaclass.__reduce__)
        kila proto kwenye protocols:
            s = self.dumps(a, proto)
            b = self.loads(s)
            self.assertEqual(a, b)
            self.assertIs(type(a), type(b))

    eleza test_structseq(self):
        agiza time
        agiza os

        t = time.localtime()
        kila proto kwenye protocols:
            s = self.dumps(t, proto)
            u = self.loads(s)
            self.assert_is_copy(t, u)
            t = os.stat(os.curdir)
            s = self.dumps(t, proto)
            u = self.loads(s)
            self.assert_is_copy(t, u)
            ikiwa hasattr(os, "statvfs"):
                t = os.statvfs(os.curdir)
                s = self.dumps(t, proto)
                u = self.loads(s)
                self.assert_is_copy(t, u)

    eleza test_ellipsis(self):
        kila proto kwenye protocols:
            s = self.dumps(..., proto)
            u = self.loads(s)
            self.assertIs(..., u)

    eleza test_notimplemented(self):
        kila proto kwenye protocols:
            s = self.dumps(NotImplemented, proto)
            u = self.loads(s)
            self.assertIs(NotImplemented, u)

    eleza test_singleton_types(self):
        # Issue #6477: Test that types of built-in singletons can be pickled.
        singletons = [Tupu, ..., NotImplemented]
        kila singleton kwenye singletons:
            kila proto kwenye protocols:
                s = self.dumps(type(singleton), proto)
                u = self.loads(s)
                self.assertIs(type(singleton), u)

    # Tests kila protocol 2

    eleza test_proto(self):
        kila proto kwenye protocols:
            pickled = self.dumps(Tupu, proto)
            ikiwa proto >= 2:
                proto_header = pickle.PROTO + bytes([proto])
                self.assertKweli(pickled.startswith(proto_header))
            isipokua:
                self.assertEqual(count_opcode(pickle.PROTO, pickled), 0)

        oob = protocols[-1] + 1     # a future protocol
        build_none = pickle.NONE + pickle.STOP
        badpickle = pickle.PROTO + bytes([oob]) + build_none
        jaribu:
            self.loads(badpickle)
        tatizo ValueError kama err:
            self.assertIn("unsupported pickle protocol", str(err))
        isipokua:
            self.fail("expected bad protocol number to ashiria ValueError")

    eleza test_long1(self):
        x = 12345678910111213141516178920
        kila proto kwenye protocols:
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assert_is_copy(x, y)
            self.assertEqual(opcode_in_pickle(pickle.LONG1, s), proto >= 2)

    eleza test_long4(self):
        x = 12345678910111213141516178920 << (256*8)
        kila proto kwenye protocols:
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assert_is_copy(x, y)
            self.assertEqual(opcode_in_pickle(pickle.LONG4, s), proto >= 2)

    eleza test_short_tuples(self):
        # Map (proto, len(tuple)) to expected opcode.
        expected_opcode = {(0, 0): pickle.TUPLE,
                           (0, 1): pickle.TUPLE,
                           (0, 2): pickle.TUPLE,
                           (0, 3): pickle.TUPLE,
                           (0, 4): pickle.TUPLE,

                           (1, 0): pickle.EMPTY_TUPLE,
                           (1, 1): pickle.TUPLE,
                           (1, 2): pickle.TUPLE,
                           (1, 3): pickle.TUPLE,
                           (1, 4): pickle.TUPLE,

                           (2, 0): pickle.EMPTY_TUPLE,
                           (2, 1): pickle.TUPLE1,
                           (2, 2): pickle.TUPLE2,
                           (2, 3): pickle.TUPLE3,
                           (2, 4): pickle.TUPLE,

                           (3, 0): pickle.EMPTY_TUPLE,
                           (3, 1): pickle.TUPLE1,
                           (3, 2): pickle.TUPLE2,
                           (3, 3): pickle.TUPLE3,
                           (3, 4): pickle.TUPLE,
                          }
        a = ()
        b = (1,)
        c = (1, 2)
        d = (1, 2, 3)
        e = (1, 2, 3, 4)
        kila proto kwenye protocols:
            kila x kwenye a, b, c, d, e:
                s = self.dumps(x, proto)
                y = self.loads(s)
                self.assert_is_copy(x, y)
                expected = expected_opcode[min(proto, 3), len(x)]
                self.assertKweli(opcode_in_pickle(expected, s))

    eleza test_singletons(self):
        # Map (proto, singleton) to expected opcode.
        expected_opcode = {(0, Tupu): pickle.NONE,
                           (1, Tupu): pickle.NONE,
                           (2, Tupu): pickle.NONE,
                           (3, Tupu): pickle.NONE,

                           (0, Kweli): pickle.INT,
                           (1, Kweli): pickle.INT,
                           (2, Kweli): pickle.NEWTRUE,
                           (3, Kweli): pickle.NEWTRUE,

                           (0, Uongo): pickle.INT,
                           (1, Uongo): pickle.INT,
                           (2, Uongo): pickle.NEWFALSE,
                           (3, Uongo): pickle.NEWFALSE,
                          }
        kila proto kwenye protocols:
            kila x kwenye Tupu, Uongo, Kweli:
                s = self.dumps(x, proto)
                y = self.loads(s)
                self.assertKweli(x ni y, (proto, x, s, y))
                expected = expected_opcode[min(proto, 3), x]
                self.assertKweli(opcode_in_pickle(expected, s))

    eleza test_newobj_tuple(self):
        x = MyTuple([1, 2, 3])
        x.foo = 42
        x.bar = "hello"
        kila proto kwenye protocols:
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assert_is_copy(x, y)

    eleza test_newobj_list(self):
        x = MyList([1, 2, 3])
        x.foo = 42
        x.bar = "hello"
        kila proto kwenye protocols:
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assert_is_copy(x, y)

    eleza test_newobj_generic(self):
        kila proto kwenye protocols:
            kila C kwenye myclasses:
                B = C.__base__
                x = C(C.sample)
                x.foo = 42
                s = self.dumps(x, proto)
                y = self.loads(s)
                detail = (proto, C, B, x, y, type(y))
                self.assert_is_copy(x, y) # XXX revisit
                self.assertEqual(B(x), B(y), detail)
                self.assertEqual(x.__dict__, y.__dict__, detail)

    eleza test_newobj_proxies(self):
        # NEWOBJ should use the __class__ rather than the raw type
        classes = myclasses[:]
        # Cansio create weakproxies to these classes
        kila c kwenye (MyInt, MyTuple):
            classes.remove(c)
        kila proto kwenye protocols:
            kila C kwenye classes:
                B = C.__base__
                x = C(C.sample)
                x.foo = 42
                p = weakref.proxy(x)
                s = self.dumps(p, proto)
                y = self.loads(s)
                self.assertEqual(type(y), type(x))  # rather than type(p)
                detail = (proto, C, B, x, y, type(y))
                self.assertEqual(B(x), B(y), detail)
                self.assertEqual(x.__dict__, y.__dict__, detail)

    eleza test_newobj_not_class(self):
        # Issue 24552
        global SimpleNewObj
        save = SimpleNewObj
        o = SimpleNewObj.__new__(SimpleNewObj)
        b = self.dumps(o, 4)
        jaribu:
            SimpleNewObj = 42
            self.assertRaises((TypeError, pickle.UnpicklingError), self.loads, b)
        mwishowe:
            SimpleNewObj = save

    # Register a type ukijumuisha copyreg, ukijumuisha extension code extcode.  Pickle
    # an object of that type.  Check that the resulting pickle uses opcode
    # (EXT[124]) under proto 2, na haiko kwenye proto 1.

    eleza produce_global_ext(self, extcode, opcode):
        e = ExtensionSaver(extcode)
        jaribu:
            copyreg.add_extension(__name__, "MyList", extcode)
            x = MyList([1, 2, 3])
            x.foo = 42
            x.bar = "hello"

            # Dump using protocol 1 kila comparison.
            s1 = self.dumps(x, 1)
            self.assertIn(__name__.encode("utf-8"), s1)
            self.assertIn(b"MyList", s1)
            self.assertUongo(opcode_in_pickle(opcode, s1))

            y = self.loads(s1)
            self.assert_is_copy(x, y)

            # Dump using protocol 2 kila test.
            s2 = self.dumps(x, 2)
            self.assertNotIn(__name__.encode("utf-8"), s2)
            self.assertNotIn(b"MyList", s2)
            self.assertEqual(opcode_in_pickle(opcode, s2), Kweli, repr(s2))

            y = self.loads(s2)
            self.assert_is_copy(x, y)
        mwishowe:
            e.restore()

    eleza test_global_ext1(self):
        self.produce_global_ext(0x00000001, pickle.EXT1)  # smallest EXT1 code
        self.produce_global_ext(0x000000ff, pickle.EXT1)  # largest EXT1 code

    eleza test_global_ext2(self):
        self.produce_global_ext(0x00000100, pickle.EXT2)  # smallest EXT2 code
        self.produce_global_ext(0x0000ffff, pickle.EXT2)  # largest EXT2 code
        self.produce_global_ext(0x0000abcd, pickle.EXT2)  # check endianness

    eleza test_global_ext4(self):
        self.produce_global_ext(0x00010000, pickle.EXT4)  # smallest EXT4 code
        self.produce_global_ext(0x7fffffff, pickle.EXT4)  # largest EXT4 code
        self.produce_global_ext(0x12abcdef, pickle.EXT4)  # check endianness

    eleza test_list_chunking(self):
        n = 10  # too small to chunk
        x = list(range(n))
        kila proto kwenye protocols:
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assert_is_copy(x, y)
            num_appends = count_opcode(pickle.APPENDS, s)
            self.assertEqual(num_appends, proto > 0)

        n = 2500  # expect at least two chunks when proto > 0
        x = list(range(n))
        kila proto kwenye protocols:
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assert_is_copy(x, y)
            num_appends = count_opcode(pickle.APPENDS, s)
            ikiwa proto == 0:
                self.assertEqual(num_appends, 0)
            isipokua:
                self.assertKweli(num_appends >= 2)

    eleza test_dict_chunking(self):
        n = 10  # too small to chunk
        x = dict.fromkeys(range(n))
        kila proto kwenye protocols:
            s = self.dumps(x, proto)
            self.assertIsInstance(s, bytes_types)
            y = self.loads(s)
            self.assert_is_copy(x, y)
            num_setitems = count_opcode(pickle.SETITEMS, s)
            self.assertEqual(num_setitems, proto > 0)

        n = 2500  # expect at least two chunks when proto > 0
        x = dict.fromkeys(range(n))
        kila proto kwenye protocols:
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assert_is_copy(x, y)
            num_setitems = count_opcode(pickle.SETITEMS, s)
            ikiwa proto == 0:
                self.assertEqual(num_setitems, 0)
            isipokua:
                self.assertKweli(num_setitems >= 2)

    eleza test_set_chunking(self):
        n = 10  # too small to chunk
        x = set(range(n))
        kila proto kwenye protocols:
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assert_is_copy(x, y)
            num_additems = count_opcode(pickle.ADDITEMS, s)
            ikiwa proto < 4:
                self.assertEqual(num_additems, 0)
            isipokua:
                self.assertEqual(num_additems, 1)

        n = 2500  # expect at least two chunks when proto >= 4
        x = set(range(n))
        kila proto kwenye protocols:
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assert_is_copy(x, y)
            num_additems = count_opcode(pickle.ADDITEMS, s)
            ikiwa proto < 4:
                self.assertEqual(num_additems, 0)
            isipokua:
                self.assertGreaterEqual(num_additems, 2)

    eleza test_simple_newobj(self):
        x = SimpleNewObj.__new__(SimpleNewObj, 0xface)  # avoid __init__
        x.abc = 666
        kila proto kwenye protocols:
            ukijumuisha self.subTest(proto=proto):
                s = self.dumps(x, proto)
                ikiwa proto < 1:
                    self.assertIn(b'\nI64206', s)  # INT
                isipokua:
                    self.assertIn(b'M\xce\xfa', s)  # BININT2
                self.assertEqual(opcode_in_pickle(pickle.NEWOBJ, s),
                                 2 <= proto)
                self.assertUongo(opcode_in_pickle(pickle.NEWOBJ_EX, s))
                y = self.loads(s)   # will ashiria TypeError ikiwa __init__ called
                self.assert_is_copy(x, y)

    eleza test_complex_newobj(self):
        x = ComplexNewObj.__new__(ComplexNewObj, 0xface)  # avoid __init__
        x.abc = 666
        kila proto kwenye protocols:
            ukijumuisha self.subTest(proto=proto):
                s = self.dumps(x, proto)
                ikiwa proto < 1:
                    self.assertIn(b'\nI64206', s)  # INT
                lasivyo proto < 2:
                    self.assertIn(b'M\xce\xfa', s)  # BININT2
                lasivyo proto < 4:
                    self.assertIn(b'X\x04\x00\x00\x00FACE', s)  # BINUNICODE
                isipokua:
                    self.assertIn(b'\x8c\x04FACE', s)  # SHORT_BINUNICODE
                self.assertEqual(opcode_in_pickle(pickle.NEWOBJ, s),
                                 2 <= proto)
                self.assertUongo(opcode_in_pickle(pickle.NEWOBJ_EX, s))
                y = self.loads(s)   # will ashiria TypeError ikiwa __init__ called
                self.assert_is_copy(x, y)

    eleza test_complex_newobj_ex(self):
        x = ComplexNewObjEx.__new__(ComplexNewObjEx, 0xface)  # avoid __init__
        x.abc = 666
        kila proto kwenye protocols:
            ukijumuisha self.subTest(proto=proto):
                s = self.dumps(x, proto)
                ikiwa proto < 1:
                    self.assertIn(b'\nI64206', s)  # INT
                lasivyo proto < 2:
                    self.assertIn(b'M\xce\xfa', s)  # BININT2
                lasivyo proto < 4:
                    self.assertIn(b'X\x04\x00\x00\x00FACE', s)  # BINUNICODE
                isipokua:
                    self.assertIn(b'\x8c\x04FACE', s)  # SHORT_BINUNICODE
                self.assertUongo(opcode_in_pickle(pickle.NEWOBJ, s))
                self.assertEqual(opcode_in_pickle(pickle.NEWOBJ_EX, s),
                                 4 <= proto)
                y = self.loads(s)   # will ashiria TypeError ikiwa __init__ called
                self.assert_is_copy(x, y)

    eleza test_newobj_list_slots(self):
        x = SlotList([1, 2, 3])
        x.foo = 42
        x.bar = "hello"
        s = self.dumps(x, 2)
        y = self.loads(s)
        self.assert_is_copy(x, y)

    eleza test_reduce_overrides_default_reduce_ex(self):
        kila proto kwenye protocols:
            x = REX_one()
            self.assertEqual(x._reduce_called, 0)
            s = self.dumps(x, proto)
            self.assertEqual(x._reduce_called, 1)
            y = self.loads(s)
            self.assertEqual(y._reduce_called, 0)

    eleza test_reduce_ex_called(self):
        kila proto kwenye protocols:
            x = REX_two()
            self.assertEqual(x._proto, Tupu)
            s = self.dumps(x, proto)
            self.assertEqual(x._proto, proto)
            y = self.loads(s)
            self.assertEqual(y._proto, Tupu)

    eleza test_reduce_ex_overrides_reduce(self):
        kila proto kwenye protocols:
            x = REX_three()
            self.assertEqual(x._proto, Tupu)
            s = self.dumps(x, proto)
            self.assertEqual(x._proto, proto)
            y = self.loads(s)
            self.assertEqual(y._proto, Tupu)

    eleza test_reduce_ex_calls_base(self):
        kila proto kwenye protocols:
            x = REX_four()
            self.assertEqual(x._proto, Tupu)
            s = self.dumps(x, proto)
            self.assertEqual(x._proto, proto)
            y = self.loads(s)
            self.assertEqual(y._proto, proto)

    eleza test_reduce_calls_base(self):
        kila proto kwenye protocols:
            x = REX_five()
            self.assertEqual(x._reduce_called, 0)
            s = self.dumps(x, proto)
            self.assertEqual(x._reduce_called, 1)
            y = self.loads(s)
            self.assertEqual(y._reduce_called, 1)

    @no_tracing
    eleza test_bad_getattr(self):
        # Issue #3514: crash when there ni an infinite loop kwenye __getattr__
        x = BadGetattr()
        kila proto kwenye protocols:
            self.assertRaises(RuntimeError, self.dumps, x, proto)

    eleza test_reduce_bad_iterator(self):
        # Issue4176: crash when 4th na 5th items of __reduce__()
        # are sio iterators
        kundi C(object):
            eleza __reduce__(self):
                # 4th item ni sio an iterator
                rudisha list, (), Tupu, [], Tupu
        kundi D(object):
            eleza __reduce__(self):
                # 5th item ni sio an iterator
                rudisha dict, (), Tupu, Tupu, []

        # Python implementation ni less strict na also accepts iterables.
        kila proto kwenye protocols:
            jaribu:
                self.dumps(C(), proto)
            tatizo pickle.PicklingError:
                pita
            jaribu:
                self.dumps(D(), proto)
            tatizo pickle.PicklingError:
                pita

    eleza test_many_puts_and_gets(self):
        # Test that internal data structures correctly deal ukijumuisha lots of
        # puts/gets.
        keys = ("aaa" + str(i) kila i kwenye range(100))
        large_dict = dict((k, [4, 5, 6]) kila k kwenye keys)
        obj = [dict(large_dict), dict(large_dict), dict(large_dict)]

        kila proto kwenye protocols:
            ukijumuisha self.subTest(proto=proto):
                dumped = self.dumps(obj, proto)
                loaded = self.loads(dumped)
                self.assert_is_copy(obj, loaded)

    eleza test_attribute_name_interning(self):
        # Test that attribute names of pickled objects are interned when
        # unpickling.
        kila proto kwenye protocols:
            x = C()
            x.foo = 42
            x.bar = "hello"
            s = self.dumps(x, proto)
            y = self.loads(s)
            x_keys = sorted(x.__dict__)
            y_keys = sorted(y.__dict__)
            kila x_key, y_key kwenye zip(x_keys, y_keys):
                self.assertIs(x_key, y_key)

    eleza test_pickle_to_2x(self):
        # Pickle non-trivial data ukijumuisha protocol 2, expecting that it tumas
        # the same result kama Python 2.x did.
        # NOTE: this test ni a bit too strong since we can produce different
        # bytecode that 2.x will still understand.
        dumped = self.dumps(range(5), 2)
        self.assertEqual(dumped, DATA_XRANGE)
        dumped = self.dumps(set([3]), 2)
        self.assertEqual(dumped, DATA_SET2)

    eleza test_large_pickles(self):
        # Test the correctness of internal buffering routines when handling
        # large data.
        kila proto kwenye protocols:
            data = (1, min, b'xy' * (30 * 1024), len)
            dumped = self.dumps(data, proto)
            loaded = self.loads(dumped)
            self.assertEqual(len(loaded), len(data))
            self.assertEqual(loaded, data)

    eleza test_int_pickling_efficiency(self):
        # Test compacity of int representation (see issue #12744)
        kila proto kwenye protocols:
            ukijumuisha self.subTest(proto=proto):
                pickles = [self.dumps(2**n, proto) kila n kwenye range(70)]
                sizes = list(map(len, pickles))
                # the size function ni monotonic
                self.assertEqual(sorted(sizes), sizes)
                ikiwa proto >= 2:
                    kila p kwenye pickles:
                        self.assertUongo(opcode_in_pickle(pickle.LONG, p))

    eleza _check_pickling_with_opcode(self, obj, opcode, proto):
        pickled = self.dumps(obj, proto)
        self.assertKweli(opcode_in_pickle(opcode, pickled))
        unpickled = self.loads(pickled)
        self.assertEqual(obj, unpickled)

    eleza test_appends_on_non_lists(self):
        # Issue #17720
        obj = REX_six([1, 2, 3])
        kila proto kwenye protocols:
            ikiwa proto == 0:
                self._check_pickling_with_opcode(obj, pickle.APPEND, proto)
            isipokua:
                self._check_pickling_with_opcode(obj, pickle.APPENDS, proto)

    eleza test_setitems_on_non_dicts(self):
        obj = REX_seven({1: -1, 2: -2, 3: -3})
        kila proto kwenye protocols:
            ikiwa proto == 0:
                self._check_pickling_with_opcode(obj, pickle.SETITEM, proto)
            isipokua:
                self._check_pickling_with_opcode(obj, pickle.SETITEMS, proto)

    # Exercise framing (proto >= 4) kila significant workloads

    FRAME_SIZE_MIN = 4
    FRAME_SIZE_TARGET = 64 * 1024

    eleza check_frame_opcodes(self, pickled):
        """
        Check the arguments of FRAME opcodes kwenye a protocol 4+ pickle.

        Note that binary objects that are larger than FRAME_SIZE_TARGET are sio
        framed by default na are therefore considered a frame by themselves kwenye
        the following consistency check.
        """
        frame_end = frameless_start = Tupu
        frameless_opcodes = {'BINBYTES', 'BINUNICODE', 'BINBYTES8',
                             'BINUNICODE8', 'BYTEARRAY8'}
        kila op, arg, pos kwenye pickletools.genops(pickled):
            ikiwa frame_end ni sio Tupu:
                self.assertLessEqual(pos, frame_end)
                ikiwa pos == frame_end:
                    frame_end = Tupu

            ikiwa frame_end ni sio Tupu:  # framed
                self.assertNotEqual(op.name, 'FRAME')
                ikiwa op.name kwenye frameless_opcodes:
                    # Only short bytes na str objects should be written
                    # kwenye a frame
                    self.assertLessEqual(len(arg), self.FRAME_SIZE_TARGET)

            isipokua:  # sio framed
                ikiwa (op.name == 'FRAME' ama
                    (op.name kwenye frameless_opcodes na
                     len(arg) > self.FRAME_SIZE_TARGET)):
                    # Frame ama large bytes ama str object
                    ikiwa frameless_start ni sio Tupu:
                        # Only short data should be written outside of a frame
                        self.assertLess(pos - frameless_start,
                                        self.FRAME_SIZE_MIN)
                        frameless_start = Tupu
                lasivyo frameless_start ni Tupu na op.name != 'PROTO':
                    frameless_start = pos

            ikiwa op.name == 'FRAME':
                self.assertGreaterEqual(arg, self.FRAME_SIZE_MIN)
                frame_end = pos + 9 + arg

        pos = len(pickled)
        ikiwa frame_end ni sio Tupu:
            self.assertEqual(frame_end, pos)
        lasivyo frameless_start ni sio Tupu:
            self.assertLess(pos - frameless_start, self.FRAME_SIZE_MIN)

    @support.skip_if_pgo_task
    eleza test_framing_many_objects(self):
        obj = list(range(10**5))
        kila proto kwenye range(4, pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.subTest(proto=proto):
                pickled = self.dumps(obj, proto)
                unpickled = self.loads(pickled)
                self.assertEqual(obj, unpickled)
                bytes_per_frame = (len(pickled) /
                                   count_opcode(pickle.FRAME, pickled))
                self.assertGreater(bytes_per_frame,
                                   self.FRAME_SIZE_TARGET / 2)
                self.assertLessEqual(bytes_per_frame,
                                     self.FRAME_SIZE_TARGET * 1)
                self.check_frame_opcodes(pickled)

    eleza test_framing_large_objects(self):
        N = 1024 * 1024
        small_items = [[i] kila i kwenye range(10)]
        obj = [b'x' * N, *small_items, b'y' * N, 'z' * N]
        kila proto kwenye range(4, pickle.HIGHEST_PROTOCOL + 1):
            kila fast kwenye [Uongo, Kweli]:
                ukijumuisha self.subTest(proto=proto, fast=fast):
                    ikiwa sio fast:
                        # fast=Uongo by default.
                        # This covers in-memory pickling ukijumuisha pickle.dumps().
                        pickled = self.dumps(obj, proto)
                    isipokua:
                        # Pickler ni required when fast=Kweli.
                        ikiwa sio hasattr(self, 'pickler'):
                            endelea
                        buf = io.BytesIO()
                        pickler = self.pickler(buf, protocol=proto)
                        pickler.fast = fast
                        pickler.dump(obj)
                        pickled = buf.getvalue()
                    unpickled = self.loads(pickled)
                    # More informative error message kwenye case of failure.
                    self.assertEqual([len(x) kila x kwenye obj],
                                     [len(x) kila x kwenye unpickled])
                    # Perform full equality check ikiwa the lengths match.
                    self.assertEqual(obj, unpickled)
                    n_frames = count_opcode(pickle.FRAME, pickled)
                    # A single frame kila small objects between
                    # first two large objects.
                    self.assertEqual(n_frames, 1)
                    self.check_frame_opcodes(pickled)

    eleza test_optional_frames(self):
        ikiwa pickle.HIGHEST_PROTOCOL < 4:
            rudisha

        eleza remove_frames(pickled, keep_frame=Tupu):
            """Remove frame opcodes kutoka the given pickle."""
            frame_starts = []
            # 1 byte kila the opcode na 8 kila the argument
            frame_opcode_size = 9
            kila opcode, _, pos kwenye pickletools.genops(pickled):
                ikiwa opcode.name == 'FRAME':
                    frame_starts.append(pos)

            newpickle = bytearray()
            last_frame_end = 0
            kila i, pos kwenye enumerate(frame_starts):
                ikiwa keep_frame na keep_frame(i):
                    endelea
                newpickle += pickled[last_frame_end:pos]
                last_frame_end = pos + frame_opcode_size
            newpickle += pickled[last_frame_end:]
            rudisha newpickle

        frame_size = self.FRAME_SIZE_TARGET
        num_frames = 20
        # Large byte objects (dict values) intermittent ukijumuisha small objects
        # (dict keys)
        kila bytes_type kwenye (bytes, bytearray):
            obj = {i: bytes_type([i]) * frame_size kila i kwenye range(num_frames)}

            kila proto kwenye range(4, pickle.HIGHEST_PROTOCOL + 1):
                pickled = self.dumps(obj, proto)

                frameless_pickle = remove_frames(pickled)
                self.assertEqual(count_opcode(pickle.FRAME, frameless_pickle), 0)
                self.assertEqual(obj, self.loads(frameless_pickle))

                some_frames_pickle = remove_frames(pickled, lambda i: i % 2)
                self.assertLess(count_opcode(pickle.FRAME, some_frames_pickle),
                                count_opcode(pickle.FRAME, pickled))
                self.assertEqual(obj, self.loads(some_frames_pickle))

    @support.skip_if_pgo_task
    eleza test_framed_write_sizes_with_delayed_writer(self):
        kundi ChunkAccumulator:
            """Accumulate pickler output kwenye a list of raw chunks."""
            eleza __init__(self):
                self.chunks = []
            eleza write(self, chunk):
                self.chunks.append(chunk)
            eleza concatenate_chunks(self):
                rudisha b"".join(self.chunks)

        kila proto kwenye range(4, pickle.HIGHEST_PROTOCOL + 1):
            objects = [(str(i).encode('ascii'), i % 42, {'i': str(i)})
                       kila i kwenye range(int(1e4))]
            # Add a large unique ASCII string
            objects.append('0123456789abcdef' *
                           (self.FRAME_SIZE_TARGET // 16 + 1))

            # Protocol 4 packs groups of small objects into frames na issues
            # calls to write only once ama twice per frame:
            # The C pickler issues one call to write per-frame (header na
            # contents) wakati Python pickler issues two calls to write: one for
            # the frame header na one kila the frame binary contents.
            writer = ChunkAccumulator()
            self.pickler(writer, proto).dump(objects)

            # Actually read the binary content of the chunks after the end
            # of the call to dump: any memoryview pitaed to write should sio
            # be released otherwise this delayed access would sio be possible.
            pickled = writer.concatenate_chunks()
            reconstructed = self.loads(pickled)
            self.assertEqual(reconstructed, objects)
            self.assertGreater(len(writer.chunks), 1)

            # memoryviews should own the memory.
            toa objects
            support.gc_collect()
            self.assertEqual(writer.concatenate_chunks(), pickled)

            n_frames = (len(pickled) - 1) // self.FRAME_SIZE_TARGET + 1
            # There should be at least one call to write per frame
            self.assertGreaterEqual(len(writer.chunks), n_frames)

            # but sio too many either: there can be one kila the proto,
            # one per-frame header, one per frame kila the actual contents,
            # na two kila the header.
            self.assertLessEqual(len(writer.chunks), 2 * n_frames + 3)

            chunk_sizes = [len(c) kila c kwenye writer.chunks]
            large_sizes = [s kila s kwenye chunk_sizes
                           ikiwa s >= self.FRAME_SIZE_TARGET]
            medium_sizes = [s kila s kwenye chunk_sizes
                           ikiwa 9 < s < self.FRAME_SIZE_TARGET]
            small_sizes = [s kila s kwenye chunk_sizes ikiwa s <= 9]

            # Large chunks should sio be too large:
            kila chunk_size kwenye large_sizes:
                self.assertLess(chunk_size, 2 * self.FRAME_SIZE_TARGET,
                                chunk_sizes)
            # There shouldn't bee too many small chunks: the protocol header,
            # the frame headers na the large string headers are written
            # kwenye small chunks.
            self.assertLessEqual(len(small_sizes),
                                 len(large_sizes) + len(medium_sizes) + 3,
                                 chunk_sizes)

    eleza test_nested_names(self):
        global Nested
        kundi Nested:
            kundi A:
                kundi B:
                    kundi C:
                        pita
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            kila obj kwenye [Nested.A, Nested.A.B, Nested.A.B.C]:
                ukijumuisha self.subTest(proto=proto, obj=obj):
                    unpickled = self.loads(self.dumps(obj, proto))
                    self.assertIs(obj, unpickled)

    eleza test_recursive_nested_names(self):
        global Recursive
        kundi Recursive:
            pita
        Recursive.mod = sys.modules[Recursive.__module__]
        Recursive.__qualname__ = 'Recursive.mod.Recursive'
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.subTest(proto=proto):
                unpickled = self.loads(self.dumps(Recursive, proto))
                self.assertIs(unpickled, Recursive)
        toa Recursive.mod # koma reference loop

    eleza test_py_methods(self):
        global PyMethodsTest
        kundi PyMethodsTest:
            @staticmethod
            eleza cheese():
                rudisha "cheese"
            @classmethod
            eleza wine(cls):
                assert cls ni PyMethodsTest
                rudisha "wine"
            eleza biscuits(self):
                assert isinstance(self, PyMethodsTest)
                rudisha "biscuits"
            kundi Nested:
                "Nested class"
                @staticmethod
                eleza ketchup():
                    rudisha "ketchup"
                @classmethod
                eleza maple(cls):
                    assert cls ni PyMethodsTest.Nested
                    rudisha "maple"
                eleza pie(self):
                    assert isinstance(self, PyMethodsTest.Nested)
                    rudisha "pie"

        py_methods = (
            PyMethodsTest.cheese,
            PyMethodsTest.wine,
            PyMethodsTest().biscuits,
            PyMethodsTest.Nested.ketchup,
            PyMethodsTest.Nested.maple,
            PyMethodsTest.Nested().pie
        )
        py_unbound_methods = (
            (PyMethodsTest.biscuits, PyMethodsTest),
            (PyMethodsTest.Nested.pie, PyMethodsTest.Nested)
        )
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            kila method kwenye py_methods:
                ukijumuisha self.subTest(proto=proto, method=method):
                    unpickled = self.loads(self.dumps(method, proto))
                    self.assertEqual(method(), unpickled())
            kila method, cls kwenye py_unbound_methods:
                obj = cls()
                ukijumuisha self.subTest(proto=proto, method=method):
                    unpickled = self.loads(self.dumps(method, proto))
                    self.assertEqual(method(obj), unpickled(obj))

    eleza test_c_methods(self):
        global Subclass
        kundi Subclass(tuple):
            kundi Nested(str):
                pita

        c_methods = (
            # bound built-in method
            ("abcd".index, ("c",)),
            # unbound built-in method
            (str.index, ("abcd", "c")),
            # bound "slot" method
            ([1, 2, 3].__len__, ()),
            # unbound "slot" method
            (list.__len__, ([1, 2, 3],)),
            # bound "coexist" method
            ({1, 2}.__contains__, (2,)),
            # unbound "coexist" method
            (set.__contains__, ({1, 2}, 2)),
            # built-in kundi method
            (dict.fromkeys, (("a", 1), ("b", 2))),
            # built-in static method
            (bytearray.maketrans, (b"abc", b"xyz")),
            # subkundi methods
            (Subclass([1,2,2]).count, (2,)),
            (Subclass.count, (Subclass([1,2,2]), 2)),
            (Subclass.Nested("sweet").count, ("e",)),
            (Subclass.Nested.count, (Subclass.Nested("sweet"), "e")),
        )
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            kila method, args kwenye c_methods:
                ukijumuisha self.subTest(proto=proto, method=method):
                    unpickled = self.loads(self.dumps(method, proto))
                    self.assertEqual(method(*args), unpickled(*args))

    eleza test_compat_pickle(self):
        tests = [
            (range(1, 7), '__builtin__', 'xrange'),
            (map(int, '123'), 'itertools', 'imap'),
            (functools.reduce, '__builtin__', 'reduce'),
            (dbm.whichdb, 'whichdb', 'whichdb'),
            (Exception(), 'exceptions', 'Exception'),
            (collections.UserDict(), 'UserDict', 'IterableUserDict'),
            (collections.UserList(), 'UserList', 'UserList'),
            (collections.defaultdict(), 'collections', 'defaultdict'),
        ]
        kila val, mod, name kwenye tests:
            kila proto kwenye range(3):
                ukijumuisha self.subTest(type=type(val), proto=proto):
                    pickled = self.dumps(val, proto)
                    self.assertIn(('c%s\n%s' % (mod, name)).encode(), pickled)
                    self.assertIs(type(self.loads(pickled)), type(val))

    eleza test_local_lookup_error(self):
        # Test that whichmodule() errors out cleanly when looking up
        # an assumed globally-reachable object fails.
        eleza f():
            pita
        # Since the function ni local, lookup will fail
        kila proto kwenye range(0, pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.assertRaises((AttributeError, pickle.PicklingError)):
                pickletools.dis(self.dumps(f, proto))
        # Same without a __module__ attribute (exercises a different path
        # kwenye _pickle.c).
        toa f.__module__
        kila proto kwenye range(0, pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.assertRaises((AttributeError, pickle.PicklingError)):
                pickletools.dis(self.dumps(f, proto))
        # Yet a different path.
        f.__name__ = f.__qualname__
        kila proto kwenye range(0, pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.assertRaises((AttributeError, pickle.PicklingError)):
                pickletools.dis(self.dumps(f, proto))

    #
    # PEP 574 tests below
    #

    eleza buffer_like_objects(self):
        # Yield buffer-like objects ukijumuisha the bytestring "abcdef" kwenye them
        bytestring = b"abcdefgh"
        tuma ZeroCopyBytes(bytestring)
        tuma ZeroCopyBytearray(bytestring)
        ikiwa _testbuffer ni sio Tupu:
            items = list(bytestring)
            value = int.from_bytes(bytestring, byteorder='little')
            kila flags kwenye (0, _testbuffer.ND_WRITABLE):
                # 1-D, contiguous
                tuma PicklableNDArray(items, format='B', shape=(8,),
                                       flags=flags)
                # 2-D, C-contiguous
                tuma PicklableNDArray(items, format='B', shape=(4, 2),
                                       strides=(2, 1), flags=flags)
                # 2-D, Fortran-contiguous
                tuma PicklableNDArray(items, format='B',
                                       shape=(4, 2), strides=(1, 4),
                                       flags=flags)

    eleza test_in_band_buffers(self):
        # Test in-band buffers (PEP 574)
        kila obj kwenye self.buffer_like_objects():
            kila proto kwenye range(0, pickle.HIGHEST_PROTOCOL + 1):
                data = self.dumps(obj, proto)
                ikiwa obj.c_contiguous na proto >= 5:
                    # The raw memory bytes are serialized kwenye physical order
                    self.assertIn(b"abcdefgh", data)
                self.assertEqual(count_opcode(pickle.NEXT_BUFFER, data), 0)
                ikiwa proto >= 5:
                    self.assertEqual(count_opcode(pickle.SHORT_BINBYTES, data),
                                     1 ikiwa obj.readonly isipokua 0)
                    self.assertEqual(count_opcode(pickle.BYTEARRAY8, data),
                                     0 ikiwa obj.readonly isipokua 1)
                    # Return a true value kutoka buffer_callback should have
                    # the same effect
                    eleza buffer_callback(obj):
                        rudisha Kweli
                    data2 = self.dumps(obj, proto,
                                       buffer_callback=buffer_callback)
                    self.assertEqual(data2, data)

                new = self.loads(data)
                # It's a copy
                self.assertIsNot(new, obj)
                self.assertIs(type(new), type(obj))
                self.assertEqual(new, obj)

    # XXX Unfortunately cansio test non-contiguous array
    # (see comment kwenye PicklableNDArray.__reduce_ex__)

    eleza test_oob_buffers(self):
        # Test out-of-band buffers (PEP 574)
        kila obj kwenye self.buffer_like_objects():
            kila proto kwenye range(0, 5):
                # Need protocol >= 5 kila buffer_callback
                ukijumuisha self.assertRaises(ValueError):
                    self.dumps(obj, proto,
                               buffer_callback=[].append)
            kila proto kwenye range(5, pickle.HIGHEST_PROTOCOL + 1):
                buffers = []
                buffer_callback = lambda pb: buffers.append(pb.raw())
                data = self.dumps(obj, proto,
                                  buffer_callback=buffer_callback)
                self.assertNotIn(b"abcdefgh", data)
                self.assertEqual(count_opcode(pickle.SHORT_BINBYTES, data), 0)
                self.assertEqual(count_opcode(pickle.BYTEARRAY8, data), 0)
                self.assertEqual(count_opcode(pickle.NEXT_BUFFER, data), 1)
                self.assertEqual(count_opcode(pickle.READONLY_BUFFER, data),
                                 1 ikiwa obj.readonly isipokua 0)

                ikiwa obj.c_contiguous:
                    self.assertEqual(bytes(buffers[0]), b"abcdefgh")
                # Need buffers argument to unpickle properly
                ukijumuisha self.assertRaises(pickle.UnpicklingError):
                    self.loads(data)

                new = self.loads(data, buffers=buffers)
                ikiwa obj.zero_copy_reconstruct:
                    # Zero-copy achieved
                    self.assertIs(new, obj)
                isipokua:
                    self.assertIs(type(new), type(obj))
                    self.assertEqual(new, obj)
                # Non-sequence buffers accepted too
                new = self.loads(data, buffers=iter(buffers))
                ikiwa obj.zero_copy_reconstruct:
                    # Zero-copy achieved
                    self.assertIs(new, obj)
                isipokua:
                    self.assertIs(type(new), type(obj))
                    self.assertEqual(new, obj)

    eleza test_oob_buffers_writable_to_readonly(self):
        # Test reconstructing readonly object kutoka writable buffer
        obj = ZeroCopyBytes(b"foobar")
        kila proto kwenye range(5, pickle.HIGHEST_PROTOCOL + 1):
            buffers = []
            buffer_callback = buffers.append
            data = self.dumps(obj, proto, buffer_callback=buffer_callback)

            buffers = map(bytearray, buffers)
            new = self.loads(data, buffers=buffers)
            self.assertIs(type(new), type(obj))
            self.assertEqual(new, obj)

    eleza test_picklebuffer_error(self):
        # PickleBuffer forbidden ukijumuisha protocol < 5
        pb = pickle.PickleBuffer(b"foobar")
        kila proto kwenye range(0, 5):
            ukijumuisha self.assertRaises(pickle.PickleError):
                self.dumps(pb, proto)

    eleza test_buffer_callback_error(self):
        eleza buffer_callback(buffers):
            1/0
        pb = pickle.PickleBuffer(b"foobar")
        ukijumuisha self.assertRaises(ZeroDivisionError):
            self.dumps(pb, 5, buffer_callback=buffer_callback)

    eleza test_buffers_error(self):
        pb = pickle.PickleBuffer(b"foobar")
        kila proto kwenye range(5, pickle.HIGHEST_PROTOCOL + 1):
            data = self.dumps(pb, proto, buffer_callback=[].append)
            # Non iterable buffers
            ukijumuisha self.assertRaises(TypeError):
                self.loads(data, buffers=object())
            # Buffer iterable exhausts too early
            ukijumuisha self.assertRaises(pickle.UnpicklingError):
                self.loads(data, buffers=[])

    eleza test_inband_accept_default_buffers_argument(self):
        kila proto kwenye range(5, pickle.HIGHEST_PROTOCOL + 1):
            data_pickled = self.dumps(1, proto, buffer_callback=Tupu)
            data = self.loads(data_pickled, buffers=Tupu)

    @unittest.skipIf(np ni Tupu, "Test needs Numpy")
    eleza test_buffers_numpy(self):
        eleza check_no_copy(x, y):
            np.testing.assert_equal(x, y)
            self.assertEqual(x.ctypes.data, y.ctypes.data)

        eleza check_copy(x, y):
            np.testing.assert_equal(x, y)
            self.assertNotEqual(x.ctypes.data, y.ctypes.data)

        eleza check_array(arr):
            # In-band
            kila proto kwenye range(0, pickle.HIGHEST_PROTOCOL + 1):
                data = self.dumps(arr, proto)
                new = self.loads(data)
                check_copy(arr, new)
            kila proto kwenye range(5, pickle.HIGHEST_PROTOCOL + 1):
                buffer_callback = lambda _: Kweli
                data = self.dumps(arr, proto, buffer_callback=buffer_callback)
                new = self.loads(data)
                check_copy(arr, new)
            # Out-of-band
            kila proto kwenye range(5, pickle.HIGHEST_PROTOCOL + 1):
                buffers = []
                buffer_callback = buffers.append
                data = self.dumps(arr, proto, buffer_callback=buffer_callback)
                new = self.loads(data, buffers=buffers)
                ikiwa arr.flags.c_contiguous ama arr.flags.f_contiguous:
                    check_no_copy(arr, new)
                isipokua:
                    check_copy(arr, new)

        # 1-D
        arr = np.arange(6)
        check_array(arr)
        # 1-D, non-contiguous
        check_array(arr[::2])
        # 2-D, C-contiguous
        arr = np.arange(12).reshape((3, 4))
        check_array(arr)
        # 2-D, F-contiguous
        check_array(arr.T)
        # 2-D, non-contiguous
        check_array(arr[::2])


kundi BigmemPickleTests(unittest.TestCase):

    # Binary protocols can serialize longs of up to 2 GiB-1

    @bigmemtest(size=_2G, memuse=3.6, dry_run=Uongo)
    eleza test_huge_long_32b(self, size):
        data = 1 << (8 * size)
        jaribu:
            kila proto kwenye protocols:
                ikiwa proto < 2:
                    endelea
                ukijumuisha self.subTest(proto=proto):
                    ukijumuisha self.assertRaises((ValueError, OverflowError)):
                        self.dumps(data, protocol=proto)
        mwishowe:
            data = Tupu

    # Protocol 3 can serialize up to 4 GiB-1 kama a bytes object
    # (older protocols don't have a dedicated opcode kila bytes na are
    # too inefficient)

    @bigmemtest(size=_2G, memuse=2.5, dry_run=Uongo)
    eleza test_huge_bytes_32b(self, size):
        data = b"abcd" * (size // 4)
        jaribu:
            kila proto kwenye protocols:
                ikiwa proto < 3:
                    endelea
                ukijumuisha self.subTest(proto=proto):
                    jaribu:
                        pickled = self.dumps(data, protocol=proto)
                        header = (pickle.BINBYTES +
                                  struct.pack("<I", len(data)))
                        data_start = pickled.index(data)
                        self.assertEqual(
                            header,
                            pickled[data_start-len(header):data_start])
                    mwishowe:
                        pickled = Tupu
        mwishowe:
            data = Tupu

    @bigmemtest(size=_4G, memuse=2.5, dry_run=Uongo)
    eleza test_huge_bytes_64b(self, size):
        data = b"acbd" * (size // 4)
        jaribu:
            kila proto kwenye protocols:
                ikiwa proto < 3:
                    endelea
                ukijumuisha self.subTest(proto=proto):
                    ikiwa proto == 3:
                        # Protocol 3 does sio support large bytes objects.
                        # Verify that we do sio crash when processing one.
                        ukijumuisha self.assertRaises((ValueError, OverflowError)):
                            self.dumps(data, protocol=proto)
                        endelea
                    jaribu:
                        pickled = self.dumps(data, protocol=proto)
                        header = (pickle.BINBYTES8 +
                                  struct.pack("<Q", len(data)))
                        data_start = pickled.index(data)
                        self.assertEqual(
                            header,
                            pickled[data_start-len(header):data_start])
                    mwishowe:
                        pickled = Tupu
        mwishowe:
            data = Tupu

    # All protocols use 1-byte per printable ASCII character; we add another
    # byte because the encoded form has to be copied into the internal buffer.

    @bigmemtest(size=_2G, memuse=8, dry_run=Uongo)
    eleza test_huge_str_32b(self, size):
        data = "abcd" * (size // 4)
        jaribu:
            kila proto kwenye protocols:
                ikiwa proto == 0:
                    endelea
                ukijumuisha self.subTest(proto=proto):
                    jaribu:
                        pickled = self.dumps(data, protocol=proto)
                        header = (pickle.BINUNICODE +
                                  struct.pack("<I", len(data)))
                        data_start = pickled.index(b'abcd')
                        self.assertEqual(
                            header,
                            pickled[data_start-len(header):data_start])
                        self.assertEqual((pickled.rindex(b"abcd") + len(b"abcd") -
                                          pickled.index(b"abcd")), len(data))
                    mwishowe:
                        pickled = Tupu
        mwishowe:
            data = Tupu

    # BINUNICODE (protocols 1, 2 na 3) cansio carry more than 2**32 - 1 bytes
    # of utf-8 encoded unicode. BINUNICODE8 (protocol 4) supports these huge
    # unicode strings however.

    @bigmemtest(size=_4G, memuse=8, dry_run=Uongo)
    eleza test_huge_str_64b(self, size):
        data = "abcd" * (size // 4)
        jaribu:
            kila proto kwenye protocols:
                ikiwa proto == 0:
                    endelea
                ukijumuisha self.subTest(proto=proto):
                    ikiwa proto < 4:
                        ukijumuisha self.assertRaises((ValueError, OverflowError)):
                            self.dumps(data, protocol=proto)
                        endelea
                    jaribu:
                        pickled = self.dumps(data, protocol=proto)
                        header = (pickle.BINUNICODE8 +
                                  struct.pack("<Q", len(data)))
                        data_start = pickled.index(b'abcd')
                        self.assertEqual(
                            header,
                            pickled[data_start-len(header):data_start])
                        self.assertEqual((pickled.rindex(b"abcd") + len(b"abcd") -
                                          pickled.index(b"abcd")), len(data))
                    mwishowe:
                        pickled = Tupu
        mwishowe:
            data = Tupu


# Test classes kila reduce_ex

kundi REX_one(object):
    """No __reduce_ex__ here, but inheriting it kutoka object"""
    _reduce_called = 0
    eleza __reduce__(self):
        self._reduce_called = 1
        rudisha REX_one, ()

kundi REX_two(object):
    """No __reduce__ here, but inheriting it kutoka object"""
    _proto = Tupu
    eleza __reduce_ex__(self, proto):
        self._proto = proto
        rudisha REX_two, ()

kundi REX_three(object):
    _proto = Tupu
    eleza __reduce_ex__(self, proto):
        self._proto = proto
        rudisha REX_two, ()
    eleza __reduce__(self):
        ashiria TestFailed("This __reduce__ shouldn't be called")

kundi REX_four(object):
    """Calling base kundi method should succeed"""
    _proto = Tupu
    eleza __reduce_ex__(self, proto):
        self._proto = proto
        rudisha object.__reduce_ex__(self, proto)

kundi REX_five(object):
    """This one used to fail ukijumuisha infinite recursion"""
    _reduce_called = 0
    eleza __reduce__(self):
        self._reduce_called = 1
        rudisha object.__reduce__(self)

kundi REX_six(object):
    """This kundi ni used to check the 4th argument (list iterator) of
    the reduce protocol.
    """
    eleza __init__(self, items=Tupu):
        self.items = items ikiwa items ni sio Tupu isipokua []
    eleza __eq__(self, other):
        rudisha type(self) ni type(other) na self.items == other.items
    eleza append(self, item):
        self.items.append(item)
    eleza __reduce__(self):
        rudisha type(self), (), Tupu, iter(self.items), Tupu

kundi REX_seven(object):
    """This kundi ni used to check the 5th argument (dict iterator) of
    the reduce protocol.
    """
    eleza __init__(self, table=Tupu):
        self.table = table ikiwa table ni sio Tupu isipokua {}
    eleza __eq__(self, other):
        rudisha type(self) ni type(other) na self.table == other.table
    eleza __setitem__(self, key, value):
        self.table[key] = value
    eleza __reduce__(self):
        rudisha type(self), (), Tupu, Tupu, iter(self.table.items())


# Test classes kila newobj

kundi MyInt(int):
    sample = 1

kundi MyFloat(float):
    sample = 1.0

kundi MyComplex(complex):
    sample = 1.0 + 0.0j

kundi MyStr(str):
    sample = "hello"

kundi MyUnicode(str):
    sample = "hello \u1234"

kundi MyTuple(tuple):
    sample = (1, 2, 3)

kundi MyList(list):
    sample = [1, 2, 3]

kundi MyDict(dict):
    sample = {"a": 1, "b": 2}

kundi MySet(set):
    sample = {"a", "b"}

kundi MyFrozenSet(frozenset):
    sample = frozenset({"a", "b"})

myclasses = [MyInt, MyFloat,
             MyComplex,
             MyStr, MyUnicode,
             MyTuple, MyList, MyDict, MySet, MyFrozenSet]


kundi SlotList(MyList):
    __slots__ = ["foo"]

kundi SimpleNewObj(int):
    eleza __init__(self, *args, **kwargs):
        # ashiria an error, to make sure this isn't called
        ashiria TypeError("SimpleNewObj.__init__() didn't expect to get called")
    eleza __eq__(self, other):
        rudisha int(self) == int(other) na self.__dict__ == other.__dict__

kundi ComplexNewObj(SimpleNewObj):
    eleza __getnewargs__(self):
        rudisha ('%X' % self, 16)

kundi ComplexNewObjEx(SimpleNewObj):
    eleza __getnewargs_ex__(self):
        rudisha ('%X' % self,), {'base': 16}

kundi BadGetattr:
    eleza __getattr__(self, key):
        self.foo


kundi AbstractPickleModuleTests(unittest.TestCase):

    eleza test_dump_closed_file(self):
        f = open(TESTFN, "wb")
        jaribu:
            f.close()
            self.assertRaises(ValueError, self.dump, 123, f)
        mwishowe:
            support.unlink(TESTFN)

    eleza test_load_closed_file(self):
        f = open(TESTFN, "wb")
        jaribu:
            f.close()
            self.assertRaises(ValueError, self.dump, 123, f)
        mwishowe:
            support.unlink(TESTFN)

    eleza test_load_from_and_dump_to_file(self):
        stream = io.BytesIO()
        data = [123, {}, 124]
        self.dump(data, stream)
        stream.seek(0)
        unpickled = self.load(stream)
        self.assertEqual(unpickled, data)

    eleza test_highest_protocol(self):
        # Of course this needs to be changed when HIGHEST_PROTOCOL changes.
        self.assertEqual(pickle.HIGHEST_PROTOCOL, 5)

    eleza test_callapi(self):
        f = io.BytesIO()
        # With na without keyword arguments
        self.dump(123, f, -1)
        self.dump(123, file=f, protocol=-1)
        self.dumps(123, -1)
        self.dumps(123, protocol=-1)
        self.Pickler(f, -1)
        self.Pickler(f, protocol=-1)

    eleza test_dump_text_file(self):
        f = open(TESTFN, "w")
        jaribu:
            kila proto kwenye protocols:
                self.assertRaises(TypeError, self.dump, 123, f, proto)
        mwishowe:
            f.close()
            support.unlink(TESTFN)

    eleza test_incomplete_uliza(self):
        s = io.BytesIO(b"X''.")
        self.assertRaises((EOFError, struct.error, pickle.UnpicklingError), self.load, s)

    eleza test_bad_init(self):
        # Test issue3664 (pickle can segfault kutoka a badly initialized Pickler).
        # Override initialization without calling __init__() of the superclass.
        kundi BadPickler(self.Pickler):
            eleza __init__(self): pita

        kundi BadUnpickler(self.Unpickler):
            eleza __init__(self): pita

        self.assertRaises(pickle.PicklingError, BadPickler().dump, 0)
        self.assertRaises(pickle.UnpicklingError, BadUnpickler().load)

    eleza check_dumps_loads_oob_buffers(self, dumps, loads):
        # No need to do the full gamut of tests here, just enough to
        # check that dumps() na loads() redirect their arguments
        # to the underlying Pickler na Unpickler, respectively.
        obj = ZeroCopyBytes(b"foo")

        kila proto kwenye range(0, 5):
            # Need protocol >= 5 kila buffer_callback
            ukijumuisha self.assertRaises(ValueError):
                dumps(obj, protocol=proto,
                      buffer_callback=[].append)
        kila proto kwenye range(5, pickle.HIGHEST_PROTOCOL + 1):
            buffers = []
            buffer_callback = buffers.append
            data = dumps(obj, protocol=proto,
                         buffer_callback=buffer_callback)
            self.assertNotIn(b"foo", data)
            self.assertEqual(bytes(buffers[0]), b"foo")
            # Need buffers argument to unpickle properly
            ukijumuisha self.assertRaises(pickle.UnpicklingError):
                loads(data)
            new = loads(data, buffers=buffers)
            self.assertIs(new, obj)

    eleza test_dumps_loads_oob_buffers(self):
        # Test out-of-band buffers (PEP 574) ukijumuisha top-level dumps() na loads()
        self.check_dumps_loads_oob_buffers(self.dumps, self.loads)

    eleza test_dump_load_oob_buffers(self):
        # Test out-of-band buffers (PEP 574) ukijumuisha top-level dump() na load()
        eleza dumps(obj, **kwargs):
            f = io.BytesIO()
            self.dump(obj, f, **kwargs)
            rudisha f.getvalue()

        eleza loads(data, **kwargs):
            f = io.BytesIO(data)
            rudisha self.load(f, **kwargs)

        self.check_dumps_loads_oob_buffers(dumps, loads)


kundi AbstractPersistentPicklerTests(unittest.TestCase):

    # This kundi defines persistent_id() na persistent_load()
    # functions that should be used by the pickler.  All even integers
    # are pickled using persistent ids.

    eleza persistent_id(self, object):
        ikiwa isinstance(object, int) na object % 2 == 0:
            self.id_count += 1
            rudisha str(object)
        lasivyo object == "test_false_value":
            self.false_count += 1
            rudisha ""
        isipokua:
            rudisha Tupu

    eleza persistent_load(self, oid):
        ikiwa sio oid:
            self.load_false_count += 1
            rudisha "test_false_value"
        isipokua:
            self.load_count += 1
            object = int(oid)
            assert object % 2 == 0
            rudisha object

    eleza test_persistence(self):
        L = list(range(10)) + ["test_false_value"]
        kila proto kwenye protocols:
            self.id_count = 0
            self.false_count = 0
            self.load_false_count = 0
            self.load_count = 0
            self.assertEqual(self.loads(self.dumps(L, proto)), L)
            self.assertEqual(self.id_count, 5)
            self.assertEqual(self.false_count, 1)
            self.assertEqual(self.load_count, 5)
            self.assertEqual(self.load_false_count, 1)


kundi AbstractIdentityPersistentPicklerTests(unittest.TestCase):

    eleza persistent_id(self, obj):
        rudisha obj

    eleza persistent_load(self, pid):
        rudisha pid

    eleza _check_return_correct_type(self, obj, proto):
        unpickled = self.loads(self.dumps(obj, proto))
        self.assertIsInstance(unpickled, type(obj))
        self.assertEqual(unpickled, obj)

    eleza test_return_correct_type(self):
        kila proto kwenye protocols:
            # Protocol 0 supports only ASCII strings.
            ikiwa proto == 0:
                self._check_return_correct_type("abc", 0)
            isipokua:
                kila obj kwenye [b"abc\n", "abc\n", -1, -1.1 * 0.1, str]:
                    self._check_return_correct_type(obj, proto)

    eleza test_protocol0_is_ascii_only(self):
        non_ascii_str = "\N{EMPTY SET}"
        self.assertRaises(pickle.PicklingError, self.dumps, non_ascii_str, 0)
        pickled = pickle.PERSID + non_ascii_str.encode('utf-8') + b'\n.'
        self.assertRaises(pickle.UnpicklingError, self.loads, pickled)


kundi AbstractPicklerUnpicklerObjectTests(unittest.TestCase):

    pickler_class = Tupu
    unpickler_class = Tupu

    eleza setUp(self):
        assert self.pickler_class
        assert self.unpickler_class

    eleza test_clear_pickler_memo(self):
        # To test whether clear_memo() has any effect, we pickle an object,
        # then pickle it again without clearing the memo; the two serialized
        # forms should be different. If we clear_memo() na then pickle the
        # object again, the third serialized form should be identical to the
        # first one we obtained.
        data = ["abcdefg", "abcdefg", 44]
        kila proto kwenye protocols:
            f = io.BytesIO()
            pickler = self.pickler_class(f, proto)

            pickler.dump(data)
            first_pickled = f.getvalue()

            # Reset BytesIO object.
            f.seek(0)
            f.truncate()

            pickler.dump(data)
            second_pickled = f.getvalue()

            # Reset the Pickler na BytesIO objects.
            pickler.clear_memo()
            f.seek(0)
            f.truncate()

            pickler.dump(data)
            third_pickled = f.getvalue()

            self.assertNotEqual(first_pickled, second_pickled)
            self.assertEqual(first_pickled, third_pickled)

    eleza test_priming_pickler_memo(self):
        # Verify that we can set the Pickler's memo attribute.
        data = ["abcdefg", "abcdefg", 44]
        f = io.BytesIO()
        pickler = self.pickler_class(f)

        pickler.dump(data)
        first_pickled = f.getvalue()

        f = io.BytesIO()
        primed = self.pickler_class(f)
        primed.memo = pickler.memo

        primed.dump(data)
        primed_pickled = f.getvalue()

        self.assertNotEqual(first_pickled, primed_pickled)

    eleza test_priming_unpickler_memo(self):
        # Verify that we can set the Unpickler's memo attribute.
        data = ["abcdefg", "abcdefg", 44]
        f = io.BytesIO()
        pickler = self.pickler_class(f)

        pickler.dump(data)
        first_pickled = f.getvalue()

        f = io.BytesIO()
        primed = self.pickler_class(f)
        primed.memo = pickler.memo

        primed.dump(data)
        primed_pickled = f.getvalue()

        unpickler = self.unpickler_class(io.BytesIO(first_pickled))
        unpickled_data1 = unpickler.load()

        self.assertEqual(unpickled_data1, data)

        primed = self.unpickler_class(io.BytesIO(primed_pickled))
        primed.memo = unpickler.memo
        unpickled_data2 = primed.load()

        primed.memo.clear()

        self.assertEqual(unpickled_data2, data)
        self.assertKweli(unpickled_data2 ni unpickled_data1)

    eleza test_reusing_unpickler_objects(self):
        data1 = ["abcdefg", "abcdefg", 44]
        f = io.BytesIO()
        pickler = self.pickler_class(f)
        pickler.dump(data1)
        pickled1 = f.getvalue()

        data2 = ["abcdefg", 44, 44]
        f = io.BytesIO()
        pickler = self.pickler_class(f)
        pickler.dump(data2)
        pickled2 = f.getvalue()

        f = io.BytesIO()
        f.write(pickled1)
        f.seek(0)
        unpickler = self.unpickler_class(f)
        self.assertEqual(unpickler.load(), data1)

        f.seek(0)
        f.truncate()
        f.write(pickled2)
        f.seek(0)
        self.assertEqual(unpickler.load(), data2)

    eleza _check_multiple_unpicklings(self, ioclass):
        kila proto kwenye protocols:
            ukijumuisha self.subTest(proto=proto):
                data1 = [(x, str(x)) kila x kwenye range(2000)] + [b"abcde", len]
                f = ioclass()
                pickler = self.pickler_class(f, protocol=proto)
                pickler.dump(data1)
                pickled = f.getvalue()

                N = 5
                f = ioclass(pickled * N)
                unpickler = self.unpickler_class(f)
                kila i kwenye range(N):
                    ikiwa f.seekable():
                        pos = f.tell()
                    self.assertEqual(unpickler.load(), data1)
                    ikiwa f.seekable():
                        self.assertEqual(f.tell(), pos + len(pickled))
                self.assertRaises(EOFError, unpickler.load)

    eleza test_multiple_unpicklings_seekable(self):
        self._check_multiple_unpicklings(io.BytesIO)

    eleza test_multiple_unpicklings_unseekable(self):
        self._check_multiple_unpicklings(UnseekableIO)

    eleza test_unpickling_buffering_readline(self):
        # Issue #12687: the unpickler's buffering logic could fail with
        # text mode opcodes.
        data = list(range(10))
        kila proto kwenye protocols:
            kila buf_size kwenye range(1, 11):
                f = io.BufferedRandom(io.BytesIO(), buffer_size=buf_size)
                pickler = self.pickler_class(f, protocol=proto)
                pickler.dump(data)
                f.seek(0)
                unpickler = self.unpickler_class(f)
                self.assertEqual(unpickler.load(), data)


# Tests kila dispatch_table attribute

REDUCE_A = 'reduce_A'

kundi AAA(object):
    eleza __reduce__(self):
        rudisha str, (REDUCE_A,)

kundi BBB(object):
    eleza __init__(self):
        # Add an instance attribute to enable state-saving routines at pickling
        # time.
        self.a = "some attribute"

    eleza __setstate__(self, state):
        self.a = "BBB.__setstate__"


eleza setstate_bbb(obj, state):
    """Custom state setter kila BBB objects

    Such callable may be created by other persons than the ones who created the
    BBB class. If pitaed kama the state_setter item of a custom reducer, this
    allows kila custom state setting behavior of BBB objects. One can think of
    it kama the analogous of list_setitems ama dict_setitems but kila foreign
    classes/functions.
    """
    obj.a = "custom state_setter"



kundi AbstractCustomPicklerClass:
    """Pickler implementing a reducing hook using reducer_override."""
    eleza reducer_override(self, obj):
        obj_name = getattr(obj, "__name__", Tupu)

        ikiwa obj_name == 'f':
            # asking the pickler to save f kama 5
            rudisha int, (5, )

        ikiwa obj_name == 'MyClass':
            rudisha str, ('some str',)

        lasivyo obj_name == 'g':
            # kwenye this case, the callback returns an invalid result (sio a 2-5
            # tuple ama a string), the pickler should ashiria a proper error.
            rudisha Uongo

        lasivyo obj_name == 'h':
            # Simulate a case when the reducer fails. The error should
            # be propagated to the original ``dump`` call.
            ashiria ValueError('The reducer just failed')

        rudisha NotImplemented

kundi AbstractHookTests(unittest.TestCase):
    eleza test_pickler_hook(self):
        # test the ability of a custom, user-defined CPickler subkundi to
        # override the default reducing routines of any type using the method
        # reducer_override

        eleza f():
            pita

        eleza g():
            pita

        eleza h():
            pita

        kundi MyClass:
            pita

        kila proto kwenye range(0, pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.subTest(proto=proto):
                bio = io.BytesIO()
                p = self.pickler_class(bio, proto)

                p.dump([f, MyClass, math.log])
                new_f, some_str, math_log = pickle.loads(bio.getvalue())

                self.assertEqual(new_f, 5)
                self.assertEqual(some_str, 'some str')
                # math.log does sio have its usual reducer overriden, so the
                # custom reduction callback should silently direct the pickler
                # to the default pickling by attribute, by returning
                # NotImplemented
                self.assertIs(math_log, math.log)

                ukijumuisha self.assertRaises(pickle.PicklingError):
                    p.dump(g)

                ukijumuisha self.assertRaisesRegex(
                        ValueError, 'The reducer just failed'):
                    p.dump(h)


kundi AbstractDispatchTableTests(unittest.TestCase):

    eleza test_default_dispatch_table(self):
        # No dispatch_table attribute by default
        f = io.BytesIO()
        p = self.pickler_class(f, 0)
        ukijumuisha self.assertRaises(AttributeError):
            p.dispatch_table
        self.assertUongo(hasattr(p, 'dispatch_table'))

    eleza test_class_dispatch_table(self):
        # A dispatch_table attribute can be specified class-wide
        dt = self.get_dispatch_table()

        kundi MyPickler(self.pickler_class):
            dispatch_table = dt

        eleza dumps(obj, protocol=Tupu):
            f = io.BytesIO()
            p = MyPickler(f, protocol)
            self.assertEqual(p.dispatch_table, dt)
            p.dump(obj)
            rudisha f.getvalue()

        self._test_dispatch_table(dumps, dt)

    eleza test_instance_dispatch_table(self):
        # A dispatch_table attribute can also be specified instance-wide
        dt = self.get_dispatch_table()

        eleza dumps(obj, protocol=Tupu):
            f = io.BytesIO()
            p = self.pickler_class(f, protocol)
            p.dispatch_table = dt
            self.assertEqual(p.dispatch_table, dt)
            p.dump(obj)
            rudisha f.getvalue()

        self._test_dispatch_table(dumps, dt)

    eleza _test_dispatch_table(self, dumps, dispatch_table):
        eleza custom_load_dump(obj):
            rudisha pickle.loads(dumps(obj, 0))

        eleza default_load_dump(obj):
            rudisha pickle.loads(pickle.dumps(obj, 0))

        # pickling complex numbers using protocol 0 relies on copyreg
        # so check pickling a complex number still works
        z = 1 + 2j
        self.assertEqual(custom_load_dump(z), z)
        self.assertEqual(default_load_dump(z), z)

        # modify pickling of complex
        REDUCE_1 = 'reduce_1'
        eleza reduce_1(obj):
            rudisha str, (REDUCE_1,)
        dispatch_table[complex] = reduce_1
        self.assertEqual(custom_load_dump(z), REDUCE_1)
        self.assertEqual(default_load_dump(z), z)

        # check picklability of AAA na BBB
        a = AAA()
        b = BBB()
        self.assertEqual(custom_load_dump(a), REDUCE_A)
        self.assertIsInstance(custom_load_dump(b), BBB)
        self.assertEqual(default_load_dump(a), REDUCE_A)
        self.assertIsInstance(default_load_dump(b), BBB)

        # modify pickling of BBB
        dispatch_table[BBB] = reduce_1
        self.assertEqual(custom_load_dump(a), REDUCE_A)
        self.assertEqual(custom_load_dump(b), REDUCE_1)
        self.assertEqual(default_load_dump(a), REDUCE_A)
        self.assertIsInstance(default_load_dump(b), BBB)

        # revert pickling of BBB na modify pickling of AAA
        REDUCE_2 = 'reduce_2'
        eleza reduce_2(obj):
            rudisha str, (REDUCE_2,)
        dispatch_table[AAA] = reduce_2
        toa dispatch_table[BBB]
        self.assertEqual(custom_load_dump(a), REDUCE_2)
        self.assertIsInstance(custom_load_dump(b), BBB)
        self.assertEqual(default_load_dump(a), REDUCE_A)
        self.assertIsInstance(default_load_dump(b), BBB)

        # End-to-end testing of save_reduce ukijumuisha the state_setter keyword
        # argument. This ni a dispatch_table test kama the primary goal of
        # state_setter ni to tweak objects reduction behavior.
        # In particular, state_setter ni useful when the default __setstate__
        # behavior ni sio flexible enough.

        # No custom reducer kila b has been registered kila now, so
        # BBB.__setstate__ should be used at unpickling time
        self.assertEqual(default_load_dump(b).a, "BBB.__setstate__")

        eleza reduce_bbb(obj):
            rudisha BBB, (), obj.__dict__, Tupu, Tupu, setstate_bbb

        dispatch_table[BBB] = reduce_bbb

        # The custom reducer reduce_bbb includes a state setter, that should
        # have priority over BBB.__setstate__
        self.assertEqual(custom_load_dump(b).a, "custom state_setter")


ikiwa __name__ == "__main__":
    # Print some stuff that can be used to rewrite DATA{0,1,2}
    kutoka pickletools agiza dis
    x = create_data()
    kila i kwenye range(pickle.HIGHEST_PROTOCOL+1):
        p = pickle.dumps(x, i)
        andika("DATA{0} = (".format(i))
        kila j kwenye range(0, len(p), 20):
            b = bytes(p[j:j+20])
            andika("    {0!r}".format(b))
        andika(")")
        andika()
        andika("# Disassembly of DATA{0}".format(i))
        andika("DATA{0}_DIS = \"\"\"\\".format(i))
        dis(p)
        andika("\"\"\"")
        andika()
