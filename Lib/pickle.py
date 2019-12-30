"""Create portable serialized representations of Python objects.

See module copyreg kila a mechanism kila registering custom picklers.
See module pickletools source kila extensive comments.

Classes:

    Pickler
    Unpickler

Functions:

    dump(object, file)
    dumps(object) -> string
    load(file) -> object
    loads(string) -> object

Misc variables:

    __version__
    format_version
    compatible_formats

"""

kutoka types agiza FunctionType
kutoka copyreg agiza dispatch_table
kutoka copyreg agiza _extension_registry, _inverted_registry, _extension_cache
kutoka itertools agiza islice
kutoka functools agiza partial
agiza sys
kutoka sys agiza maxsize
kutoka struct agiza pack, unpack
agiza re
agiza io
agiza codecs
agiza _compat_pickle

__all__ = ["PickleError", "PicklingError", "UnpicklingError", "Pickler",
           "Unpickler", "dump", "dumps", "load", "loads"]

jaribu:
    kutoka _pickle agiza PickleBuffer
    __all__.append("PickleBuffer")
    _HAVE_PICKLE_BUFFER = Kweli
tatizo ImportError:
    _HAVE_PICKLE_BUFFER = Uongo


# Shortcut kila use kwenye isinstance testing
bytes_types = (bytes, bytearray)

# These are purely informational; no code uses these.
format_version = "4.0"                  # File format version we write
compatible_formats = ["1.0",            # Original protocol 0
                      "1.1",            # Protocol 0 ukijumuisha INST added
                      "1.2",            # Original protocol 1
                      "1.3",            # Protocol 1 ukijumuisha BINFLOAT added
                      "2.0",            # Protocol 2
                      "3.0",            # Protocol 3
                      "4.0",            # Protocol 4
                      "5.0",            # Protocol 5
                      ]                 # Old format versions we can read

# This ni the highest protocol number we know how to read.
HIGHEST_PROTOCOL = 5

# The protocol we write by default.  May be less than HIGHEST_PROTOCOL.
# Only bump this ikiwa the oldest still supported version of Python already
# includes it.
DEFAULT_PROTOCOL = 4

kundi PickleError(Exception):
    """A common base kundi kila the other pickling exceptions."""
    pita

kundi PicklingError(PickleError):
    """This exception ni raised when an unpicklable object ni pitaed to the
    dump() method.

    """
    pita

kundi UnpicklingError(PickleError):
    """This exception ni raised when there ni a problem unpickling an object,
    such kama a security violation.

    Note that other exceptions may also be raised during unpickling, including
    (but sio necessarily limited to) AttributeError, EOFError, ImportError,
    na IndexError.

    """
    pita

# An instance of _Stop ni raised by Unpickler.load_stop() kwenye response to
# the STOP opcode, pitaing the object that ni the result of unpickling.
kundi _Stop(Exception):
    eleza __init__(self, value):
        self.value = value

# Jython has PyStringMap; it's a dict subkundi ukijumuisha string keys
jaribu:
    kutoka org.python.core agiza PyStringMap
tatizo ImportError:
    PyStringMap = Tupu

# Pickle opcodes.  See pickletools.py kila extensive docs.  The listing
# here ni kwenye kind-of alphabetical order of 1-character pickle code.
# pickletools groups them by purpose.

MARK           = b'('   # push special markobject on stack
STOP           = b'.'   # every pickle ends ukijumuisha STOP
POP            = b'0'   # discard topmost stack item
POP_MARK       = b'1'   # discard stack top through topmost markobject
DUP            = b'2'   # duplicate top stack item
FLOAT          = b'F'   # push float object; decimal string argument
INT            = b'I'   # push integer ama bool; decimal string argument
BININT         = b'J'   # push four-byte signed int
BININT1        = b'K'   # push 1-byte unsigned int
LONG           = b'L'   # push long; decimal string argument
BININT2        = b'M'   # push 2-byte unsigned int
NONE           = b'N'   # push Tupu
PERSID         = b'P'   # push persistent object; id ni taken kutoka string arg
BINPERSID      = b'Q'   #  "       "         "  ;  "  "   "     "  stack
REDUCE         = b'R'   # apply callable to argtuple, both on stack
STRING         = b'S'   # push string; NL-terminated string argument
BINSTRING      = b'T'   # push string; counted binary string argument
SHORT_BINSTRING= b'U'   #  "     "   ;    "      "       "      " < 256 bytes
UNICODE        = b'V'   # push Unicode string; raw-unicode-escaped'd argument
BINUNICODE     = b'X'   #   "     "       "  ; counted UTF-8 string argument
APPEND         = b'a'   # append stack top to list below it
BUILD          = b'b'   # call __setstate__ ama __dict__.update()
GLOBAL         = b'c'   # push self.find_class(modname, name); 2 string args
DICT           = b'd'   # build a dict kutoka stack items
EMPTY_DICT     = b'}'   # push empty dict
APPENDS        = b'e'   # extend list on stack by topmost stack slice
GET            = b'g'   # push item kutoka memo on stack; index ni string arg
BINGET         = b'h'   #   "    "    "    "   "   "  ;   "    " 1-byte arg
INST           = b'i'   # build & push kundi instance
LONG_BINGET    = b'j'   # push item kutoka memo on stack; index ni 4-byte arg
LIST           = b'l'   # build list kutoka topmost stack items
EMPTY_LIST     = b']'   # push empty list
OBJ            = b'o'   # build & push kundi instance
PUT            = b'p'   # store stack top kwenye memo; index ni string arg
BINPUT         = b'q'   #   "     "    "   "   " ;   "    " 1-byte arg
LONG_BINPUT    = b'r'   #   "     "    "   "   " ;   "    " 4-byte arg
SETITEM        = b's'   # add key+value pair to dict
TUPLE          = b't'   # build tuple kutoka topmost stack items
EMPTY_TUPLE    = b')'   # push empty tuple
SETITEMS       = b'u'   # modify dict by adding topmost key+value pairs
BINFLOAT       = b'G'   # push float; arg ni 8-byte float encoding

TRUE           = b'I01\n'  # sio an opcode; see INT docs kwenye pickletools.py
FALSE          = b'I00\n'  # sio an opcode; see INT docs kwenye pickletools.py

# Protocol 2

PROTO          = b'\x80'  # identify pickle protocol
NEWOBJ         = b'\x81'  # build object by applying cls.__new__ to argtuple
EXT1           = b'\x82'  # push object kutoka extension registry; 1-byte index
EXT2           = b'\x83'  # ditto, but 2-byte index
EXT4           = b'\x84'  # ditto, but 4-byte index
TUPLE1         = b'\x85'  # build 1-tuple kutoka stack top
TUPLE2         = b'\x86'  # build 2-tuple kutoka two topmost stack items
TUPLE3         = b'\x87'  # build 3-tuple kutoka three topmost stack items
NEWTRUE        = b'\x88'  # push Kweli
NEWFALSE       = b'\x89'  # push Uongo
LONG1          = b'\x8a'  # push long kutoka < 256 bytes
LONG4          = b'\x8b'  # push really big long

_tuplesize2code = [EMPTY_TUPLE, TUPLE1, TUPLE2, TUPLE3]

# Protocol 3 (Python 3.x)

BINBYTES       = b'B'   # push bytes; counted binary string argument
SHORT_BINBYTES = b'C'   #  "     "   ;    "      "       "      " < 256 bytes

# Protocol 4

SHORT_BINUNICODE = b'\x8c'  # push short string; UTF-8 length < 256 bytes
BINUNICODE8      = b'\x8d'  # push very long string
BINBYTES8        = b'\x8e'  # push very long bytes string
EMPTY_SET        = b'\x8f'  # push empty set on the stack
ADDITEMS         = b'\x90'  # modify set by adding topmost stack items
FROZENSET        = b'\x91'  # build frozenset kutoka topmost stack items
NEWOBJ_EX        = b'\x92'  # like NEWOBJ but work ukijumuisha keyword only arguments
STACK_GLOBAL     = b'\x93'  # same kama GLOBAL but using names on the stacks
MEMOIZE          = b'\x94'  # store top of the stack kwenye memo
FRAME            = b'\x95'  # indicate the beginning of a new frame

# Protocol 5

BYTEARRAY8       = b'\x96'  # push bytearray
NEXT_BUFFER      = b'\x97'  # push next out-of-band buffer
READONLY_BUFFER  = b'\x98'  # make top of stack readonly

__all__.extend([x kila x kwenye dir() ikiwa re.match("[A-Z][A-Z0-9_]+$", x)])


kundi _Framer:

    _FRAME_SIZE_MIN = 4
    _FRAME_SIZE_TARGET = 64 * 1024

    eleza __init__(self, file_write):
        self.file_write = file_write
        self.current_frame = Tupu

    eleza start_framing(self):
        self.current_frame = io.BytesIO()

    eleza end_framing(self):
        ikiwa self.current_frame na self.current_frame.tell() > 0:
            self.commit_frame(force=Kweli)
            self.current_frame = Tupu

    eleza commit_frame(self, force=Uongo):
        ikiwa self.current_frame:
            f = self.current_frame
            ikiwa f.tell() >= self._FRAME_SIZE_TARGET ama force:
                data = f.getbuffer()
                write = self.file_write
                ikiwa len(data) >= self._FRAME_SIZE_MIN:
                    # Issue a single call to the write method of the underlying
                    # file object kila the frame opcode ukijumuisha the size of the
                    # frame. The concatenation ni expected to be less expensive
                    # than issuing an additional call to write.
                    write(FRAME + pack("<Q", len(data)))

                # Issue a separate call to write to append the frame
                # contents without concatenation to the above to avoid a
                # memory copy.
                write(data)

                # Start the new frame ukijumuisha a new io.BytesIO instance so that
                # the file object can have delayed access to the previous frame
                # contents via an unreleased memoryview of the previous
                # io.BytesIO instance.
                self.current_frame = io.BytesIO()

    eleza write(self, data):
        ikiwa self.current_frame:
            rudisha self.current_frame.write(data)
        isipokua:
            rudisha self.file_write(data)

    eleza write_large_bytes(self, header, payload):
        write = self.file_write
        ikiwa self.current_frame:
            # Terminate the current frame na flush it to the file.
            self.commit_frame(force=Kweli)

        # Perform direct write of the header na payload of the large binary
        # object. Be careful sio to concatenate the header na the payload
        # prior to calling 'write' kama we do sio want to allocate a large
        # temporary bytes object.
        # We intentionally do sio inert a protocol 4 frame opcode to make
        # it possible to optimize file.read calls kwenye the loader.
        write(header)
        write(payload)


kundi _Unframer:

    eleza __init__(self, file_read, file_readline, file_tell=Tupu):
        self.file_read = file_read
        self.file_readline = file_readline
        self.current_frame = Tupu

    eleza readinto(self, buf):
        ikiwa self.current_frame:
            n = self.current_frame.readinto(buf)
            ikiwa n == 0 na len(buf) != 0:
                self.current_frame = Tupu
                n = len(buf)
                buf[:] = self.file_read(n)
                rudisha n
            ikiwa n < len(buf):
                ashiria UnpicklingError(
                    "pickle exhausted before end of frame")
            rudisha n
        isipokua:
            n = len(buf)
            buf[:] = self.file_read(n)
            rudisha n

    eleza read(self, n):
        ikiwa self.current_frame:
            data = self.current_frame.read(n)
            ikiwa sio data na n != 0:
                self.current_frame = Tupu
                rudisha self.file_read(n)
            ikiwa len(data) < n:
                ashiria UnpicklingError(
                    "pickle exhausted before end of frame")
            rudisha data
        isipokua:
            rudisha self.file_read(n)

    eleza readline(self):
        ikiwa self.current_frame:
            data = self.current_frame.readline()
            ikiwa sio data:
                self.current_frame = Tupu
                rudisha self.file_readline()
            ikiwa data[-1] != b'\n'[0]:
                ashiria UnpicklingError(
                    "pickle exhausted before end of frame")
            rudisha data
        isipokua:
            rudisha self.file_readline()

    eleza load_frame(self, frame_size):
        ikiwa self.current_frame na self.current_frame.read() != b'':
            ashiria UnpicklingError(
                "beginning of a new frame before end of current frame")
        self.current_frame = io.BytesIO(self.file_read(frame_size))


# Tools used kila pickling.

eleza _getattribute(obj, name):
    kila subpath kwenye name.split('.'):
        ikiwa subpath == '<locals>':
            ashiria AttributeError("Can't get local attribute {!r} on {!r}"
                                 .format(name, obj))
        jaribu:
            parent = obj
            obj = getattr(obj, subpath)
        tatizo AttributeError:
            ashiria AttributeError("Can't get attribute {!r} on {!r}"
                                 .format(name, obj)) kutoka Tupu
    rudisha obj, parent

eleza whichmodule(obj, name):
    """Find the module an object belong to."""
    module_name = getattr(obj, '__module__', Tupu)
    ikiwa module_name ni sio Tupu:
        rudisha module_name
    # Protect the iteration by using a list copy of sys.modules against dynamic
    # modules that trigger imports of other modules upon calls to getattr.
    kila module_name, module kwenye list(sys.modules.items()):
        ikiwa module_name == '__main__' ama module ni Tupu:
            endelea
        jaribu:
            ikiwa _getattribute(module, name)[0] ni obj:
                rudisha module_name
        tatizo AttributeError:
            pita
    rudisha '__main__'

eleza encode_long(x):
    r"""Encode a long to a two's complement little-endian binary string.
    Note that 0 ni a special case, returning an empty string, to save a
    byte kwenye the LONG1 pickling context.

    >>> encode_long(0)
    b''
    >>> encode_long(255)
    b'\xff\x00'
    >>> encode_long(32767)
    b'\xff\x7f'
    >>> encode_long(-256)
    b'\x00\xff'
    >>> encode_long(-32768)
    b'\x00\x80'
    >>> encode_long(-128)
    b'\x80'
    >>> encode_long(127)
    b'\x7f'
    >>>
    """
    ikiwa x == 0:
        rudisha b''
    nbytes = (x.bit_length() >> 3) + 1
    result = x.to_bytes(nbytes, byteorder='little', signed=Kweli)
    ikiwa x < 0 na nbytes > 1:
        ikiwa result[-1] == 0xff na (result[-2] & 0x80) != 0:
            result = result[:-1]
    rudisha result

eleza decode_long(data):
    r"""Decode a long kutoka a two's complement little-endian binary string.

    >>> decode_long(b'')
    0
    >>> decode_long(b"\xff\x00")
    255
    >>> decode_long(b"\xff\x7f")
    32767
    >>> decode_long(b"\x00\xff")
    -256
    >>> decode_long(b"\x00\x80")
    -32768
    >>> decode_long(b"\x80")
    -128
    >>> decode_long(b"\x7f")
    127
    """
    rudisha int.from_bytes(data, byteorder='little', signed=Kweli)


# Pickling machinery

kundi _Pickler:

    eleza __init__(self, file, protocol=Tupu, *, fix_imports=Kweli,
                 buffer_callback=Tupu):
        """This takes a binary file kila writing a pickle data stream.

        The optional *protocol* argument tells the pickler to use the
        given protocol; supported protocols are 0, 1, 2, 3 na 4.  The
        default protocol ni 4. It was introduced kwenye Python 3.4, it is
        incompatible ukijumuisha previous versions.

        Specifying a negative protocol version selects the highest
        protocol version supported.  The higher the protocol used, the
        more recent the version of Python needed to read the pickle
        produced.

        The *file* argument must have a write() method that accepts a
        single bytes argument. It can thus be a file object opened for
        binary writing, an io.BytesIO instance, ama any other custom
        object that meets this interface.

        If *fix_imports* ni Kweli na *protocol* ni less than 3, pickle
        will try to map the new Python 3 names to the old module names
        used kwenye Python 2, so that the pickle data stream ni readable
        ukijumuisha Python 2.

        If *buffer_callback* ni Tupu (the default), buffer views are
        serialized into *file* kama part of the pickle stream.

        If *buffer_callback* ni sio Tupu, then it can be called any number
        of times ukijumuisha a buffer view.  If the callback returns a false value
        (such kama Tupu), the given buffer ni out-of-band; otherwise the
        buffer ni serialized in-band, i.e. inside the pickle stream.

        It ni an error ikiwa *buffer_callback* ni sio Tupu na *protocol*
        ni Tupu ama smaller than 5.
        """
        ikiwa protocol ni Tupu:
            protocol = DEFAULT_PROTOCOL
        ikiwa protocol < 0:
            protocol = HIGHEST_PROTOCOL
        lasivyo sio 0 <= protocol <= HIGHEST_PROTOCOL:
            ashiria ValueError("pickle protocol must be <= %d" % HIGHEST_PROTOCOL)
        ikiwa buffer_callback ni sio Tupu na protocol < 5:
            ashiria ValueError("buffer_callback needs protocol >= 5")
        self._buffer_callback = buffer_callback
        jaribu:
            self._file_write = file.write
        tatizo AttributeError:
            ashiria TypeError("file must have a 'write' attribute")
        self.framer = _Framer(self._file_write)
        self.write = self.framer.write
        self._write_large_bytes = self.framer.write_large_bytes
        self.memo = {}
        self.proto = int(protocol)
        self.bin = protocol >= 1
        self.fast = 0
        self.fix_imports = fix_imports na protocol < 3

    eleza clear_memo(self):
        """Clears the pickler's "memo".

        The memo ni the data structure that remembers which objects the
        pickler has already seen, so that shared ama recursive objects
        are pickled by reference na sio by value.  This method is
        useful when re-using picklers.
        """
        self.memo.clear()

    eleza dump(self, obj):
        """Write a pickled representation of obj to the open file."""
        # Check whether Pickler was initialized correctly. This is
        # only needed to mimic the behavior of _pickle.Pickler.dump().
        ikiwa sio hasattr(self, "_file_write"):
            ashiria PicklingError("Pickler.__init__() was sio called by "
                                "%s.__init__()" % (self.__class__.__name__,))
        ikiwa self.proto >= 2:
            self.write(PROTO + pack("<B", self.proto))
        ikiwa self.proto >= 4:
            self.framer.start_framing()
        self.save(obj)
        self.write(STOP)
        self.framer.end_framing()

    eleza memoize(self, obj):
        """Store an object kwenye the memo."""

        # The Pickler memo ni a dictionary mapping object ids to 2-tuples
        # that contain the Unpickler memo key na the object being memoized.
        # The memo key ni written to the pickle na will become
        # the key kwenye the Unpickler's memo.  The object ni stored kwenye the
        # Pickler memo so that transient objects are kept alive during
        # pickling.

        # The use of the Unpickler memo length kama the memo key ni just a
        # convention.  The only requirement ni that the memo values be unique.
        # But there appears no advantage to any other scheme, na this
        # scheme allows the Unpickler memo to be implemented kama a plain (but
        # growable) array, indexed by memo key.
        ikiwa self.fast:
            rudisha
        assert id(obj) haiko kwenye self.memo
        idx = len(self.memo)
        self.write(self.put(idx))
        self.memo[id(obj)] = idx, obj

    # Return a PUT (BINPUT, LONG_BINPUT) opcode string, ukijumuisha argument i.
    eleza put(self, idx):
        ikiwa self.proto >= 4:
            rudisha MEMOIZE
        lasivyo self.bin:
            ikiwa idx < 256:
                rudisha BINPUT + pack("<B", idx)
            isipokua:
                rudisha LONG_BINPUT + pack("<I", idx)
        isipokua:
            rudisha PUT + repr(idx).encode("ascii") + b'\n'

    # Return a GET (BINGET, LONG_BINGET) opcode string, ukijumuisha argument i.
    eleza get(self, i):
        ikiwa self.bin:
            ikiwa i < 256:
                rudisha BINGET + pack("<B", i)
            isipokua:
                rudisha LONG_BINGET + pack("<I", i)

        rudisha GET + repr(i).encode("ascii") + b'\n'

    eleza save(self, obj, save_persistent_id=Kweli):
        self.framer.commit_frame()

        # Check kila persistent id (defined by a subclass)
        pid = self.persistent_id(obj)
        ikiwa pid ni sio Tupu na save_persistent_id:
            self.save_pers(pid)
            rudisha

        # Check the memo
        x = self.memo.get(id(obj))
        ikiwa x ni sio Tupu:
            self.write(self.get(x[0]))
            rudisha

        rv = NotImplemented
        reduce = getattr(self, "reducer_override", Tupu)
        ikiwa reduce ni sio Tupu:
            rv = reduce(obj)

        ikiwa rv ni NotImplemented:
            # Check the type dispatch table
            t = type(obj)
            f = self.dispatch.get(t)
            ikiwa f ni sio Tupu:
                f(self, obj)  # Call unbound method ukijumuisha explicit self
                rudisha

            # Check private dispatch table ikiwa any, ama isipokua
            # copyreg.dispatch_table
            reduce = getattr(self, 'dispatch_table', dispatch_table).get(t)
            ikiwa reduce ni sio Tupu:
                rv = reduce(obj)
            isipokua:
                # Check kila a kundi ukijumuisha a custom metaclass; treat kama regular
                # class
                ikiwa issubclass(t, type):
                    self.save_global(obj)
                    rudisha

                # Check kila a __reduce_ex__ method, fall back to __reduce__
                reduce = getattr(obj, "__reduce_ex__", Tupu)
                ikiwa reduce ni sio Tupu:
                    rv = reduce(self.proto)
                isipokua:
                    reduce = getattr(obj, "__reduce__", Tupu)
                    ikiwa reduce ni sio Tupu:
                        rv = reduce()
                    isipokua:
                        ashiria PicklingError("Can't pickle %r object: %r" %
                                            (t.__name__, obj))

        # Check kila string returned by reduce(), meaning "save kama global"
        ikiwa isinstance(rv, str):
            self.save_global(obj, rv)
            rudisha

        # Assert that reduce() returned a tuple
        ikiwa sio isinstance(rv, tuple):
            ashiria PicklingError("%s must rudisha string ama tuple" % reduce)

        # Assert that it returned an appropriately sized tuple
        l = len(rv)
        ikiwa sio (2 <= l <= 6):
            ashiria PicklingError("Tuple returned by %s must have "
                                "two to six elements" % reduce)

        # Save the reduce() output na finally memoize the object
        self.save_reduce(obj=obj, *rv)

    eleza persistent_id(self, obj):
        # This exists so a subkundi can override it
        rudisha Tupu

    eleza save_pers(self, pid):
        # Save a persistent id reference
        ikiwa self.bin:
            self.save(pid, save_persistent_id=Uongo)
            self.write(BINPERSID)
        isipokua:
            jaribu:
                self.write(PERSID + str(pid).encode("ascii") + b'\n')
            tatizo UnicodeEncodeError:
                ashiria PicklingError(
                    "persistent IDs kwenye protocol 0 must be ASCII strings")

    eleza save_reduce(self, func, args, state=Tupu, listitems=Tupu,
                    dictitems=Tupu, state_setter=Tupu, obj=Tupu):
        # This API ni called by some subclasses

        ikiwa sio isinstance(args, tuple):
            ashiria PicklingError("args kutoka save_reduce() must be a tuple")
        ikiwa sio callable(func):
            ashiria PicklingError("func kutoka save_reduce() must be callable")

        save = self.save
        write = self.write

        func_name = getattr(func, "__name__", "")
        ikiwa self.proto >= 2 na func_name == "__newobj_ex__":
            cls, args, kwargs = args
            ikiwa sio hasattr(cls, "__new__"):
                ashiria PicklingError("args[0] kutoka {} args has no __new__"
                                    .format(func_name))
            ikiwa obj ni sio Tupu na cls ni sio obj.__class__:
                ashiria PicklingError("args[0] kutoka {} args has the wrong class"
                                    .format(func_name))
            ikiwa self.proto >= 4:
                save(cls)
                save(args)
                save(kwargs)
                write(NEWOBJ_EX)
            isipokua:
                func = partial(cls.__new__, cls, *args, **kwargs)
                save(func)
                save(())
                write(REDUCE)
        lasivyo self.proto >= 2 na func_name == "__newobj__":
            # A __reduce__ implementation can direct protocol 2 ama newer to
            # use the more efficient NEWOBJ opcode, wakati still
            # allowing protocol 0 na 1 to work normally.  For this to
            # work, the function returned by __reduce__ should be
            # called __newobj__, na its first argument should be a
            # class.  The implementation kila __newobj__
            # should be kama follows, although pickle has no way to
            # verify this:
            #
            # eleza __newobj__(cls, *args):
            #     rudisha cls.__new__(cls, *args)
            #
            # Protocols 0 na 1 will pickle a reference to __newobj__,
            # wakati protocol 2 (and above) will pickle a reference to
            # cls, the remaining args tuple, na the NEWOBJ code,
            # which calls cls.__new__(cls, *args) at unpickling time
            # (see load_newobj below).  If __reduce__ returns a
            # three-tuple, the state kutoka the third tuple item will be
            # pickled regardless of the protocol, calling __setstate__
            # at unpickling time (see load_build below).
            #
            # Note that no standard __newobj__ implementation exists;
            # you have to provide your own.  This ni to enforce
            # compatibility ukijumuisha Python 2.2 (pickles written using
            # protocol 0 ama 1 kwenye Python 2.3 should be unpicklable by
            # Python 2.2).
            cls = args[0]
            ikiwa sio hasattr(cls, "__new__"):
                ashiria PicklingError(
                    "args[0] kutoka __newobj__ args has no __new__")
            ikiwa obj ni sio Tupu na cls ni sio obj.__class__:
                ashiria PicklingError(
                    "args[0] kutoka __newobj__ args has the wrong class")
            args = args[1:]
            save(cls)
            save(args)
            write(NEWOBJ)
        isipokua:
            save(func)
            save(args)
            write(REDUCE)

        ikiwa obj ni sio Tupu:
            # If the object ni already kwenye the memo, this means it is
            # recursive. In this case, throw away everything we put on the
            # stack, na fetch the object back kutoka the memo.
            ikiwa id(obj) kwenye self.memo:
                write(POP + self.get(self.memo[id(obj)][0]))
            isipokua:
                self.memoize(obj)

        # More new special cases (that work ukijumuisha older protocols as
        # well): when __reduce__ returns a tuple ukijumuisha 4 ama 5 items,
        # the 4th na 5th item should be iterators that provide list
        # items na dict items (as (key, value) tuples), ama Tupu.

        ikiwa listitems ni sio Tupu:
            self._batch_appends(listitems)

        ikiwa dictitems ni sio Tupu:
            self._batch_setitems(dictitems)

        ikiwa state ni sio Tupu:
            ikiwa state_setter ni Tupu:
                save(state)
                write(BUILD)
            isipokua:
                # If a state_setter ni specified, call it instead of load_build
                # to update obj's ukijumuisha its previous state.
                # First, push state_setter na its tuple of expected arguments
                # (obj, state) onto the stack.
                save(state_setter)
                save(obj)  # simple BINGET opcode kama obj ni already memoized.
                save(state)
                write(TUPLE2)
                # Trigger a state_setter(obj, state) function call.
                write(REDUCE)
                # The purpose of state_setter ni to carry-out an
                # inplace modification of obj. We do sio care about what the
                # method might return, so its output ni eventually removed from
                # the stack.
                write(POP)

    # Methods below this point are dispatched through the dispatch table

    dispatch = {}

    eleza save_none(self, obj):
        self.write(NONE)
    dispatch[type(Tupu)] = save_none

    eleza save_bool(self, obj):
        ikiwa self.proto >= 2:
            self.write(NEWTRUE ikiwa obj isipokua NEWFALSE)
        isipokua:
            self.write(TRUE ikiwa obj isipokua FALSE)
    dispatch[bool] = save_bool

    eleza save_long(self, obj):
        ikiwa self.bin:
            # If the int ni small enough to fit kwenye a signed 4-byte 2's-comp
            # format, we can store it more efficiently than the general
            # case.
            # First one- na two-byte unsigned ints:
            ikiwa obj >= 0:
                ikiwa obj <= 0xff:
                    self.write(BININT1 + pack("<B", obj))
                    rudisha
                ikiwa obj <= 0xffff:
                    self.write(BININT2 + pack("<H", obj))
                    rudisha
            # Next check kila 4-byte signed ints:
            ikiwa -0x80000000 <= obj <= 0x7fffffff:
                self.write(BININT + pack("<i", obj))
                rudisha
        ikiwa self.proto >= 2:
            encoded = encode_long(obj)
            n = len(encoded)
            ikiwa n < 256:
                self.write(LONG1 + pack("<B", n) + encoded)
            isipokua:
                self.write(LONG4 + pack("<i", n) + encoded)
            rudisha
        ikiwa -0x80000000 <= obj <= 0x7fffffff:
            self.write(INT + repr(obj).encode("ascii") + b'\n')
        isipokua:
            self.write(LONG + repr(obj).encode("ascii") + b'L\n')
    dispatch[int] = save_long

    eleza save_float(self, obj):
        ikiwa self.bin:
            self.write(BINFLOAT + pack('>d', obj))
        isipokua:
            self.write(FLOAT + repr(obj).encode("ascii") + b'\n')
    dispatch[float] = save_float

    eleza save_bytes(self, obj):
        ikiwa self.proto < 3:
            ikiwa sio obj: # bytes object ni empty
                self.save_reduce(bytes, (), obj=obj)
            isipokua:
                self.save_reduce(codecs.encode,
                                 (str(obj, 'latin1'), 'latin1'), obj=obj)
            rudisha
        n = len(obj)
        ikiwa n <= 0xff:
            self.write(SHORT_BINBYTES + pack("<B", n) + obj)
        lasivyo n > 0xffffffff na self.proto >= 4:
            self._write_large_bytes(BINBYTES8 + pack("<Q", n), obj)
        lasivyo n >= self.framer._FRAME_SIZE_TARGET:
            self._write_large_bytes(BINBYTES + pack("<I", n), obj)
        isipokua:
            self.write(BINBYTES + pack("<I", n) + obj)
        self.memoize(obj)
    dispatch[bytes] = save_bytes

    eleza save_bytearray(self, obj):
        ikiwa self.proto < 5:
            ikiwa sio obj:  # bytearray ni empty
                self.save_reduce(bytearray, (), obj=obj)
            isipokua:
                self.save_reduce(bytearray, (bytes(obj),), obj=obj)
            rudisha
        n = len(obj)
        ikiwa n >= self.framer._FRAME_SIZE_TARGET:
            self._write_large_bytes(BYTEARRAY8 + pack("<Q", n), obj)
        isipokua:
            self.write(BYTEARRAY8 + pack("<Q", n) + obj)
    dispatch[bytearray] = save_bytearray

    ikiwa _HAVE_PICKLE_BUFFER:
        eleza save_picklebuffer(self, obj):
            ikiwa self.proto < 5:
                ashiria PicklingError("PickleBuffer can only pickled ukijumuisha "
                                    "protocol >= 5")
            ukijumuisha obj.raw() kama m:
                ikiwa sio m.contiguous:
                    ashiria PicklingError("PickleBuffer can sio be pickled when "
                                        "pointing to a non-contiguous buffer")
                in_band = Kweli
                ikiwa self._buffer_callback ni sio Tupu:
                    in_band = bool(self._buffer_callback(obj))
                ikiwa in_band:
                    # Write data in-band
                    # XXX The C implementation avoids a copy here
                    ikiwa m.readonly:
                        self.save_bytes(m.tobytes())
                    isipokua:
                        self.save_bytearray(m.tobytes())
                isipokua:
                    # Write data out-of-band
                    self.write(NEXT_BUFFER)
                    ikiwa m.readonly:
                        self.write(READONLY_BUFFER)

        dispatch[PickleBuffer] = save_picklebuffer

    eleza save_str(self, obj):
        ikiwa self.bin:
            encoded = obj.encode('utf-8', 'surrogatepita')
            n = len(encoded)
            ikiwa n <= 0xff na self.proto >= 4:
                self.write(SHORT_BINUNICODE + pack("<B", n) + encoded)
            lasivyo n > 0xffffffff na self.proto >= 4:
                self._write_large_bytes(BINUNICODE8 + pack("<Q", n), encoded)
            lasivyo n >= self.framer._FRAME_SIZE_TARGET:
                self._write_large_bytes(BINUNICODE + pack("<I", n), encoded)
            isipokua:
                self.write(BINUNICODE + pack("<I", n) + encoded)
        isipokua:
            obj = obj.replace("\\", "\\u005c")
            obj = obj.replace("\0", "\\u0000")
            obj = obj.replace("\n", "\\u000a")
            obj = obj.replace("\r", "\\u000d")
            obj = obj.replace("\x1a", "\\u001a")  # EOF on DOS
            self.write(UNICODE + obj.encode('raw-unicode-escape') +
                       b'\n')
        self.memoize(obj)
    dispatch[str] = save_str

    eleza save_tuple(self, obj):
        ikiwa sio obj: # tuple ni empty
            ikiwa self.bin:
                self.write(EMPTY_TUPLE)
            isipokua:
                self.write(MARK + TUPLE)
            rudisha

        n = len(obj)
        save = self.save
        memo = self.memo
        ikiwa n <= 3 na self.proto >= 2:
            kila element kwenye obj:
                save(element)
            # Subtle.  Same kama kwenye the big comment below.
            ikiwa id(obj) kwenye memo:
                get = self.get(memo[id(obj)][0])
                self.write(POP * n + get)
            isipokua:
                self.write(_tuplesize2code[n])
                self.memoize(obj)
            rudisha

        # proto 0 ama proto 1 na tuple isn't empty, ama proto > 1 na tuple
        # has more than 3 elements.
        write = self.write
        write(MARK)
        kila element kwenye obj:
            save(element)

        ikiwa id(obj) kwenye memo:
            # Subtle.  d was haiko kwenye memo when we entered save_tuple(), so
            # the process of saving the tuple's elements must have saved
            # the tuple itself:  the tuple ni recursive.  The proper action
            # now ni to throw away everything we put on the stack, na
            # simply GET the tuple (it's already constructed).  This check
            # could have been done kwenye the "kila element" loop instead, but
            # recursive tuples are a rare thing.
            get = self.get(memo[id(obj)][0])
            ikiwa self.bin:
                write(POP_MARK + get)
            isipokua:   # proto 0 -- POP_MARK sio available
                write(POP * (n+1) + get)
            rudisha

        # No recursion.
        write(TUPLE)
        self.memoize(obj)

    dispatch[tuple] = save_tuple

    eleza save_list(self, obj):
        ikiwa self.bin:
            self.write(EMPTY_LIST)
        isipokua:   # proto 0 -- can't use EMPTY_LIST
            self.write(MARK + LIST)

        self.memoize(obj)
        self._batch_appends(obj)

    dispatch[list] = save_list

    _BATCHSIZE = 1000

    eleza _batch_appends(self, items):
        # Helper to batch up APPENDS sequences
        save = self.save
        write = self.write

        ikiwa sio self.bin:
            kila x kwenye items:
                save(x)
                write(APPEND)
            rudisha

        it = iter(items)
        wakati Kweli:
            tmp = list(islice(it, self._BATCHSIZE))
            n = len(tmp)
            ikiwa n > 1:
                write(MARK)
                kila x kwenye tmp:
                    save(x)
                write(APPENDS)
            lasivyo n:
                save(tmp[0])
                write(APPEND)
            # isipokua tmp ni empty, na we're done
            ikiwa n < self._BATCHSIZE:
                rudisha

    eleza save_dict(self, obj):
        ikiwa self.bin:
            self.write(EMPTY_DICT)
        isipokua:   # proto 0 -- can't use EMPTY_DICT
            self.write(MARK + DICT)

        self.memoize(obj)
        self._batch_setitems(obj.items())

    dispatch[dict] = save_dict
    ikiwa PyStringMap ni sio Tupu:
        dispatch[PyStringMap] = save_dict

    eleza _batch_setitems(self, items):
        # Helper to batch up SETITEMS sequences; proto >= 1 only
        save = self.save
        write = self.write

        ikiwa sio self.bin:
            kila k, v kwenye items:
                save(k)
                save(v)
                write(SETITEM)
            rudisha

        it = iter(items)
        wakati Kweli:
            tmp = list(islice(it, self._BATCHSIZE))
            n = len(tmp)
            ikiwa n > 1:
                write(MARK)
                kila k, v kwenye tmp:
                    save(k)
                    save(v)
                write(SETITEMS)
            lasivyo n:
                k, v = tmp[0]
                save(k)
                save(v)
                write(SETITEM)
            # isipokua tmp ni empty, na we're done
            ikiwa n < self._BATCHSIZE:
                rudisha

    eleza save_set(self, obj):
        save = self.save
        write = self.write

        ikiwa self.proto < 4:
            self.save_reduce(set, (list(obj),), obj=obj)
            rudisha

        write(EMPTY_SET)
        self.memoize(obj)

        it = iter(obj)
        wakati Kweli:
            batch = list(islice(it, self._BATCHSIZE))
            n = len(batch)
            ikiwa n > 0:
                write(MARK)
                kila item kwenye batch:
                    save(item)
                write(ADDITEMS)
            ikiwa n < self._BATCHSIZE:
                rudisha
    dispatch[set] = save_set

    eleza save_frozenset(self, obj):
        save = self.save
        write = self.write

        ikiwa self.proto < 4:
            self.save_reduce(frozenset, (list(obj),), obj=obj)
            rudisha

        write(MARK)
        kila item kwenye obj:
            save(item)

        ikiwa id(obj) kwenye self.memo:
            # If the object ni already kwenye the memo, this means it is
            # recursive. In this case, throw away everything we put on the
            # stack, na fetch the object back kutoka the memo.
            write(POP_MARK + self.get(self.memo[id(obj)][0]))
            rudisha

        write(FROZENSET)
        self.memoize(obj)
    dispatch[frozenset] = save_frozenset

    eleza save_global(self, obj, name=Tupu):
        write = self.write
        memo = self.memo

        ikiwa name ni Tupu:
            name = getattr(obj, '__qualname__', Tupu)
        ikiwa name ni Tupu:
            name = obj.__name__

        module_name = whichmodule(obj, name)
        jaribu:
            __import__(module_name, level=0)
            module = sys.modules[module_name]
            obj2, parent = _getattribute(module, name)
        tatizo (ImportError, KeyError, AttributeError):
            ashiria PicklingError(
                "Can't pickle %r: it's sio found kama %s.%s" %
                (obj, module_name, name)) kutoka Tupu
        isipokua:
            ikiwa obj2 ni sio obj:
                ashiria PicklingError(
                    "Can't pickle %r: it's sio the same object kama %s.%s" %
                    (obj, module_name, name))

        ikiwa self.proto >= 2:
            code = _extension_registry.get((module_name, name))
            ikiwa code:
                assert code > 0
                ikiwa code <= 0xff:
                    write(EXT1 + pack("<B", code))
                lasivyo code <= 0xffff:
                    write(EXT2 + pack("<H", code))
                isipokua:
                    write(EXT4 + pack("<i", code))
                rudisha
        lastname = name.rpartition('.')[2]
        ikiwa parent ni module:
            name = lastname
        # Non-ASCII identifiers are supported only ukijumuisha protocols >= 3.
        ikiwa self.proto >= 4:
            self.save(module_name)
            self.save(name)
            write(STACK_GLOBAL)
        lasivyo parent ni sio module:
            self.save_reduce(getattr, (parent, lastname))
        lasivyo self.proto >= 3:
            write(GLOBAL + bytes(module_name, "utf-8") + b'\n' +
                  bytes(name, "utf-8") + b'\n')
        isipokua:
            ikiwa self.fix_imports:
                r_name_mapping = _compat_pickle.REVERSE_NAME_MAPPING
                r_import_mapping = _compat_pickle.REVERSE_IMPORT_MAPPING
                ikiwa (module_name, name) kwenye r_name_mapping:
                    module_name, name = r_name_mapping[(module_name, name)]
                lasivyo module_name kwenye r_import_mapping:
                    module_name = r_import_mapping[module_name]
            jaribu:
                write(GLOBAL + bytes(module_name, "ascii") + b'\n' +
                      bytes(name, "ascii") + b'\n')
            tatizo UnicodeEncodeError:
                ashiria PicklingError(
                    "can't pickle global identifier '%s.%s' using "
                    "pickle protocol %i" % (module, name, self.proto)) kutoka Tupu

        self.memoize(obj)

    eleza save_type(self, obj):
        ikiwa obj ni type(Tupu):
            rudisha self.save_reduce(type, (Tupu,), obj=obj)
        lasivyo obj ni type(NotImplemented):
            rudisha self.save_reduce(type, (NotImplemented,), obj=obj)
        lasivyo obj ni type(...):
            rudisha self.save_reduce(type, (...,), obj=obj)
        rudisha self.save_global(obj)

    dispatch[FunctionType] = save_global
    dispatch[type] = save_type


# Unpickling machinery

kundi _Unpickler:

    eleza __init__(self, file, *, fix_imports=Kweli,
                 encoding="ASCII", errors="strict", buffers=Tupu):
        """This takes a binary file kila reading a pickle data stream.

        The protocol version of the pickle ni detected automatically, so
        no proto argument ni needed.

        The argument *file* must have two methods, a read() method that
        takes an integer argument, na a readline() method that requires
        no arguments.  Both methods should rudisha bytes.  Thus *file*
        can be a binary file object opened kila reading, an io.BytesIO
        object, ama any other custom object that meets this interface.

        The file-like object must have two methods, a read() method
        that takes an integer argument, na a readline() method that
        requires no arguments.  Both methods should rudisha bytes.
        Thus file-like object can be a binary file object opened for
        reading, a BytesIO object, ama any other custom object that
        meets this interface.

        If *buffers* ni sio Tupu, it should be an iterable of buffer-enabled
        objects that ni consumed each time the pickle stream references
        an out-of-band buffer view.  Such buffers have been given kwenye order
        to the *buffer_callback* of a Pickler object.

        If *buffers* ni Tupu (the default), then the buffers are taken
        kutoka the pickle stream, assuming they are serialized there.
        It ni an error kila *buffers* to be Tupu ikiwa the pickle stream
        was produced ukijumuisha a non-Tupu *buffer_callback*.

        Other optional arguments are *fix_imports*, *encoding* na
        *errors*, which are used to control compatibility support for
        pickle stream generated by Python 2.  If *fix_imports* ni Kweli,
        pickle will try to map the old Python 2 names to the new names
        used kwenye Python 3.  The *encoding* na *errors* tell pickle how
        to decode 8-bit string instances pickled by Python 2; these
        default to 'ASCII' na 'strict', respectively. *encoding* can be
        'bytes' to read theses 8-bit string instances kama bytes objects.
        """
        self._buffers = iter(buffers) ikiwa buffers ni sio Tupu isipokua Tupu
        self._file_readline = file.readline
        self._file_read = file.read
        self.memo = {}
        self.encoding = encoding
        self.errors = errors
        self.proto = 0
        self.fix_imports = fix_imports

    eleza load(self):
        """Read a pickled object representation kutoka the open file.

        Return the reconstituted object hierarchy specified kwenye the file.
        """
        # Check whether Unpickler was initialized correctly. This is
        # only needed to mimic the behavior of _pickle.Unpickler.dump().
        ikiwa sio hasattr(self, "_file_read"):
            ashiria UnpicklingError("Unpickler.__init__() was sio called by "
                                  "%s.__init__()" % (self.__class__.__name__,))
        self._unframer = _Unframer(self._file_read, self._file_readline)
        self.read = self._unframer.read
        self.readinto = self._unframer.readinto
        self.readline = self._unframer.readline
        self.metastack = []
        self.stack = []
        self.append = self.stack.append
        self.proto = 0
        read = self.read
        dispatch = self.dispatch
        jaribu:
            wakati Kweli:
                key = read(1)
                ikiwa sio key:
                    ashiria EOFError
                assert isinstance(key, bytes_types)
                dispatch[key[0]](self)
        tatizo _Stop kama stopinst:
            rudisha stopinst.value

    # Return a list of items pushed kwenye the stack after last MARK instruction.
    eleza pop_mark(self):
        items = self.stack
        self.stack = self.metastack.pop()
        self.append = self.stack.append
        rudisha items

    eleza persistent_load(self, pid):
        ashiria UnpicklingError("unsupported persistent id encountered")

    dispatch = {}

    eleza load_proto(self):
        proto = self.read(1)[0]
        ikiwa sio 0 <= proto <= HIGHEST_PROTOCOL:
            ashiria ValueError("unsupported pickle protocol: %d" % proto)
        self.proto = proto
    dispatch[PROTO[0]] = load_proto

    eleza load_frame(self):
        frame_size, = unpack('<Q', self.read(8))
        ikiwa frame_size > sys.maxsize:
            ashiria ValueError("frame size > sys.maxsize: %d" % frame_size)
        self._unframer.load_frame(frame_size)
    dispatch[FRAME[0]] = load_frame

    eleza load_persid(self):
        jaribu:
            pid = self.readline()[:-1].decode("ascii")
        tatizo UnicodeDecodeError:
            ashiria UnpicklingError(
                "persistent IDs kwenye protocol 0 must be ASCII strings")
        self.append(self.persistent_load(pid))
    dispatch[PERSID[0]] = load_persid

    eleza load_binpersid(self):
        pid = self.stack.pop()
        self.append(self.persistent_load(pid))
    dispatch[BINPERSID[0]] = load_binpersid

    eleza load_none(self):
        self.append(Tupu)
    dispatch[NONE[0]] = load_none

    eleza load_false(self):
        self.append(Uongo)
    dispatch[NEWFALSE[0]] = load_false

    eleza load_true(self):
        self.append(Kweli)
    dispatch[NEWTRUE[0]] = load_true

    eleza load_int(self):
        data = self.readline()
        ikiwa data == FALSE[1:]:
            val = Uongo
        lasivyo data == TRUE[1:]:
            val = Kweli
        isipokua:
            val = int(data, 0)
        self.append(val)
    dispatch[INT[0]] = load_int

    eleza load_binint(self):
        self.append(unpack('<i', self.read(4))[0])
    dispatch[BININT[0]] = load_binint

    eleza load_binint1(self):
        self.append(self.read(1)[0])
    dispatch[BININT1[0]] = load_binint1

    eleza load_binint2(self):
        self.append(unpack('<H', self.read(2))[0])
    dispatch[BININT2[0]] = load_binint2

    eleza load_long(self):
        val = self.readline()[:-1]
        ikiwa val na val[-1] == b'L'[0]:
            val = val[:-1]
        self.append(int(val, 0))
    dispatch[LONG[0]] = load_long

    eleza load_long1(self):
        n = self.read(1)[0]
        data = self.read(n)
        self.append(decode_long(data))
    dispatch[LONG1[0]] = load_long1

    eleza load_long4(self):
        n, = unpack('<i', self.read(4))
        ikiwa n < 0:
            # Corrupt ama hostile pickle -- we never write one like this
            ashiria UnpicklingError("LONG pickle has negative byte count")
        data = self.read(n)
        self.append(decode_long(data))
    dispatch[LONG4[0]] = load_long4

    eleza load_float(self):
        self.append(float(self.readline()[:-1]))
    dispatch[FLOAT[0]] = load_float

    eleza load_binfloat(self):
        self.append(unpack('>d', self.read(8))[0])
    dispatch[BINFLOAT[0]] = load_binfloat

    eleza _decode_string(self, value):
        # Used to allow strings kutoka Python 2 to be decoded either as
        # bytes ama Unicode strings.  This should be used only ukijumuisha the
        # STRING, BINSTRING na SHORT_BINSTRING opcodes.
        ikiwa self.encoding == "bytes":
            rudisha value
        isipokua:
            rudisha value.decode(self.encoding, self.errors)

    eleza load_string(self):
        data = self.readline()[:-1]
        # Strip outermost quotes
        ikiwa len(data) >= 2 na data[0] == data[-1] na data[0] kwenye b'"\'':
            data = data[1:-1]
        isipokua:
            ashiria UnpicklingError("the STRING opcode argument must be quoted")
        self.append(self._decode_string(codecs.escape_decode(data)[0]))
    dispatch[STRING[0]] = load_string

    eleza load_binstring(self):
        # Deprecated BINSTRING uses signed 32-bit length
        len, = unpack('<i', self.read(4))
        ikiwa len < 0:
            ashiria UnpicklingError("BINSTRING pickle has negative byte count")
        data = self.read(len)
        self.append(self._decode_string(data))
    dispatch[BINSTRING[0]] = load_binstring

    eleza load_binbytes(self):
        len, = unpack('<I', self.read(4))
        ikiwa len > maxsize:
            ashiria UnpicklingError("BINBYTES exceeds system's maximum size "
                                  "of %d bytes" % maxsize)
        self.append(self.read(len))
    dispatch[BINBYTES[0]] = load_binbytes

    eleza load_unicode(self):
        self.append(str(self.readline()[:-1], 'raw-unicode-escape'))
    dispatch[UNICODE[0]] = load_unicode

    eleza load_binunicode(self):
        len, = unpack('<I', self.read(4))
        ikiwa len > maxsize:
            ashiria UnpicklingError("BINUNICODE exceeds system's maximum size "
                                  "of %d bytes" % maxsize)
        self.append(str(self.read(len), 'utf-8', 'surrogatepita'))
    dispatch[BINUNICODE[0]] = load_binunicode

    eleza load_binunicode8(self):
        len, = unpack('<Q', self.read(8))
        ikiwa len > maxsize:
            ashiria UnpicklingError("BINUNICODE8 exceeds system's maximum size "
                                  "of %d bytes" % maxsize)
        self.append(str(self.read(len), 'utf-8', 'surrogatepita'))
    dispatch[BINUNICODE8[0]] = load_binunicode8

    eleza load_binbytes8(self):
        len, = unpack('<Q', self.read(8))
        ikiwa len > maxsize:
            ashiria UnpicklingError("BINBYTES8 exceeds system's maximum size "
                                  "of %d bytes" % maxsize)
        self.append(self.read(len))
    dispatch[BINBYTES8[0]] = load_binbytes8

    eleza load_bytearray8(self):
        len, = unpack('<Q', self.read(8))
        ikiwa len > maxsize:
            ashiria UnpicklingError("BYTEARRAY8 exceeds system's maximum size "
                                  "of %d bytes" % maxsize)
        b = bytearray(len)
        self.readinto(b)
        self.append(b)
    dispatch[BYTEARRAY8[0]] = load_bytearray8

    eleza load_next_buffer(self):
        ikiwa self._buffers ni Tupu:
            ashiria UnpicklingError("pickle stream refers to out-of-band data "
                                  "but no *buffers* argument was given")
        jaribu:
            buf = next(self._buffers)
        tatizo StopIteration:
            ashiria UnpicklingError("sio enough out-of-band buffers")
        self.append(buf)
    dispatch[NEXT_BUFFER[0]] = load_next_buffer

    eleza load_readonly_buffer(self):
        buf = self.stack[-1]
        ukijumuisha memoryview(buf) kama m:
            ikiwa sio m.readonly:
                self.stack[-1] = m.toreadonly()
    dispatch[READONLY_BUFFER[0]] = load_readonly_buffer

    eleza load_short_binstring(self):
        len = self.read(1)[0]
        data = self.read(len)
        self.append(self._decode_string(data))
    dispatch[SHORT_BINSTRING[0]] = load_short_binstring

    eleza load_short_binbytes(self):
        len = self.read(1)[0]
        self.append(self.read(len))
    dispatch[SHORT_BINBYTES[0]] = load_short_binbytes

    eleza load_short_binunicode(self):
        len = self.read(1)[0]
        self.append(str(self.read(len), 'utf-8', 'surrogatepita'))
    dispatch[SHORT_BINUNICODE[0]] = load_short_binunicode

    eleza load_tuple(self):
        items = self.pop_mark()
        self.append(tuple(items))
    dispatch[TUPLE[0]] = load_tuple

    eleza load_empty_tuple(self):
        self.append(())
    dispatch[EMPTY_TUPLE[0]] = load_empty_tuple

    eleza load_tuple1(self):
        self.stack[-1] = (self.stack[-1],)
    dispatch[TUPLE1[0]] = load_tuple1

    eleza load_tuple2(self):
        self.stack[-2:] = [(self.stack[-2], self.stack[-1])]
    dispatch[TUPLE2[0]] = load_tuple2

    eleza load_tuple3(self):
        self.stack[-3:] = [(self.stack[-3], self.stack[-2], self.stack[-1])]
    dispatch[TUPLE3[0]] = load_tuple3

    eleza load_empty_list(self):
        self.append([])
    dispatch[EMPTY_LIST[0]] = load_empty_list

    eleza load_empty_dictionary(self):
        self.append({})
    dispatch[EMPTY_DICT[0]] = load_empty_dictionary

    eleza load_empty_set(self):
        self.append(set())
    dispatch[EMPTY_SET[0]] = load_empty_set

    eleza load_frozenset(self):
        items = self.pop_mark()
        self.append(frozenset(items))
    dispatch[FROZENSET[0]] = load_frozenset

    eleza load_list(self):
        items = self.pop_mark()
        self.append(items)
    dispatch[LIST[0]] = load_list

    eleza load_dict(self):
        items = self.pop_mark()
        d = {items[i]: items[i+1]
             kila i kwenye range(0, len(items), 2)}
        self.append(d)
    dispatch[DICT[0]] = load_dict

    # INST na OBJ differ only kwenye how they get a kundi object.  It's sio
    # only sensible to do the rest kwenye a common routine, the two routines
    # previously diverged na grew different bugs.
    # klass ni the kundi to instantiate, na k points to the topmost mark
    # object, following which are the arguments kila klass.__init__.
    eleza _instantiate(self, klass, args):
        ikiwa (args ama sio isinstance(klass, type) ama
            hasattr(klass, "__getinitargs__")):
            jaribu:
                value = klass(*args)
            tatizo TypeError kama err:
                ashiria TypeError("in constructor kila %s: %s" %
                                (klass.__name__, str(err)), sys.exc_info()[2])
        isipokua:
            value = klass.__new__(klass)
        self.append(value)

    eleza load_inst(self):
        module = self.readline()[:-1].decode("ascii")
        name = self.readline()[:-1].decode("ascii")
        klass = self.find_class(module, name)
        self._instantiate(klass, self.pop_mark())
    dispatch[INST[0]] = load_inst

    eleza load_obj(self):
        # Stack ni ... markobject classobject arg1 arg2 ...
        args = self.pop_mark()
        cls = args.pop(0)
        self._instantiate(cls, args)
    dispatch[OBJ[0]] = load_obj

    eleza load_newobj(self):
        args = self.stack.pop()
        cls = self.stack.pop()
        obj = cls.__new__(cls, *args)
        self.append(obj)
    dispatch[NEWOBJ[0]] = load_newobj

    eleza load_newobj_ex(self):
        kwargs = self.stack.pop()
        args = self.stack.pop()
        cls = self.stack.pop()
        obj = cls.__new__(cls, *args, **kwargs)
        self.append(obj)
    dispatch[NEWOBJ_EX[0]] = load_newobj_ex

    eleza load_global(self):
        module = self.readline()[:-1].decode("utf-8")
        name = self.readline()[:-1].decode("utf-8")
        klass = self.find_class(module, name)
        self.append(klass)
    dispatch[GLOBAL[0]] = load_global

    eleza load_stack_global(self):
        name = self.stack.pop()
        module = self.stack.pop()
        ikiwa type(name) ni sio str ama type(module) ni sio str:
            ashiria UnpicklingError("STACK_GLOBAL requires str")
        self.append(self.find_class(module, name))
    dispatch[STACK_GLOBAL[0]] = load_stack_global

    eleza load_ext1(self):
        code = self.read(1)[0]
        self.get_extension(code)
    dispatch[EXT1[0]] = load_ext1

    eleza load_ext2(self):
        code, = unpack('<H', self.read(2))
        self.get_extension(code)
    dispatch[EXT2[0]] = load_ext2

    eleza load_ext4(self):
        code, = unpack('<i', self.read(4))
        self.get_extension(code)
    dispatch[EXT4[0]] = load_ext4

    eleza get_extension(self, code):
        nil = []
        obj = _extension_cache.get(code, nil)
        ikiwa obj ni sio nil:
            self.append(obj)
            rudisha
        key = _inverted_registry.get(code)
        ikiwa sio key:
            ikiwa code <= 0: # note that 0 ni forbidden
                # Corrupt ama hostile pickle.
                ashiria UnpicklingError("EXT specifies code <= 0")
            ashiria ValueError("unregistered extension code %d" % code)
        obj = self.find_class(*key)
        _extension_cache[code] = obj
        self.append(obj)

    eleza find_class(self, module, name):
        # Subclasses may override this.
        sys.audit('pickle.find_class', module, name)
        ikiwa self.proto < 3 na self.fix_imports:
            ikiwa (module, name) kwenye _compat_pickle.NAME_MAPPING:
                module, name = _compat_pickle.NAME_MAPPING[(module, name)]
            lasivyo module kwenye _compat_pickle.IMPORT_MAPPING:
                module = _compat_pickle.IMPORT_MAPPING[module]
        __import__(module, level=0)
        ikiwa self.proto >= 4:
            rudisha _getattribute(sys.modules[module], name)[0]
        isipokua:
            rudisha getattr(sys.modules[module], name)

    eleza load_reduce(self):
        stack = self.stack
        args = stack.pop()
        func = stack[-1]
        stack[-1] = func(*args)
    dispatch[REDUCE[0]] = load_reduce

    eleza load_pop(self):
        ikiwa self.stack:
            toa self.stack[-1]
        isipokua:
            self.pop_mark()
    dispatch[POP[0]] = load_pop

    eleza load_pop_mark(self):
        self.pop_mark()
    dispatch[POP_MARK[0]] = load_pop_mark

    eleza load_dup(self):
        self.append(self.stack[-1])
    dispatch[DUP[0]] = load_dup

    eleza load_get(self):
        i = int(self.readline()[:-1])
        self.append(self.memo[i])
    dispatch[GET[0]] = load_get

    eleza load_binget(self):
        i = self.read(1)[0]
        self.append(self.memo[i])
    dispatch[BINGET[0]] = load_binget

    eleza load_long_binget(self):
        i, = unpack('<I', self.read(4))
        self.append(self.memo[i])
    dispatch[LONG_BINGET[0]] = load_long_binget

    eleza load_put(self):
        i = int(self.readline()[:-1])
        ikiwa i < 0:
            ashiria ValueError("negative PUT argument")
        self.memo[i] = self.stack[-1]
    dispatch[PUT[0]] = load_put

    eleza load_binput(self):
        i = self.read(1)[0]
        ikiwa i < 0:
            ashiria ValueError("negative BINPUT argument")
        self.memo[i] = self.stack[-1]
    dispatch[BINPUT[0]] = load_binput

    eleza load_long_binput(self):
        i, = unpack('<I', self.read(4))
        ikiwa i > maxsize:
            ashiria ValueError("negative LONG_BINPUT argument")
        self.memo[i] = self.stack[-1]
    dispatch[LONG_BINPUT[0]] = load_long_binput

    eleza load_memoize(self):
        memo = self.memo
        memo[len(memo)] = self.stack[-1]
    dispatch[MEMOIZE[0]] = load_memoize

    eleza load_append(self):
        stack = self.stack
        value = stack.pop()
        list = stack[-1]
        list.append(value)
    dispatch[APPEND[0]] = load_append

    eleza load_appends(self):
        items = self.pop_mark()
        list_obj = self.stack[-1]
        jaribu:
            extend = list_obj.extend
        tatizo AttributeError:
            pita
        isipokua:
            extend(items)
            rudisha
        # Even ikiwa the PEP 307 requires extend() na append() methods,
        # fall back on append() ikiwa the object has no extend() method
        # kila backward compatibility.
        append = list_obj.append
        kila item kwenye items:
            append(item)
    dispatch[APPENDS[0]] = load_appends

    eleza load_setitem(self):
        stack = self.stack
        value = stack.pop()
        key = stack.pop()
        dict = stack[-1]
        dict[key] = value
    dispatch[SETITEM[0]] = load_setitem

    eleza load_setitems(self):
        items = self.pop_mark()
        dict = self.stack[-1]
        kila i kwenye range(0, len(items), 2):
            dict[items[i]] = items[i + 1]
    dispatch[SETITEMS[0]] = load_setitems

    eleza load_additems(self):
        items = self.pop_mark()
        set_obj = self.stack[-1]
        ikiwa isinstance(set_obj, set):
            set_obj.update(items)
        isipokua:
            add = set_obj.add
            kila item kwenye items:
                add(item)
    dispatch[ADDITEMS[0]] = load_additems

    eleza load_build(self):
        stack = self.stack
        state = stack.pop()
        inst = stack[-1]
        setstate = getattr(inst, "__setstate__", Tupu)
        ikiwa setstate ni sio Tupu:
            setstate(state)
            rudisha
        slotstate = Tupu
        ikiwa isinstance(state, tuple) na len(state) == 2:
            state, slotstate = state
        ikiwa state:
            inst_dict = inst.__dict__
            intern = sys.intern
            kila k, v kwenye state.items():
                ikiwa type(k) ni str:
                    inst_dict[intern(k)] = v
                isipokua:
                    inst_dict[k] = v
        ikiwa slotstate:
            kila k, v kwenye slotstate.items():
                setattr(inst, k, v)
    dispatch[BUILD[0]] = load_build

    eleza load_mark(self):
        self.metastack.append(self.stack)
        self.stack = []
        self.append = self.stack.append
    dispatch[MARK[0]] = load_mark

    eleza load_stop(self):
        value = self.stack.pop()
        ashiria _Stop(value)
    dispatch[STOP[0]] = load_stop


# Shorthands

eleza _dump(obj, file, protocol=Tupu, *, fix_imports=Kweli, buffer_callback=Tupu):
    _Pickler(file, protocol, fix_imports=fix_imports,
             buffer_callback=buffer_callback).dump(obj)

eleza _dumps(obj, protocol=Tupu, *, fix_imports=Kweli, buffer_callback=Tupu):
    f = io.BytesIO()
    _Pickler(f, protocol, fix_imports=fix_imports,
             buffer_callback=buffer_callback).dump(obj)
    res = f.getvalue()
    assert isinstance(res, bytes_types)
    rudisha res

eleza _load(file, *, fix_imports=Kweli, encoding="ASCII", errors="strict",
          buffers=Tupu):
    rudisha _Unpickler(file, fix_imports=fix_imports, buffers=buffers,
                     encoding=encoding, errors=errors).load()

eleza _loads(s, *, fix_imports=Kweli, encoding="ASCII", errors="strict",
           buffers=Tupu):
    ikiwa isinstance(s, str):
        ashiria TypeError("Can't load pickle kutoka unicode string")
    file = io.BytesIO(s)
    rudisha _Unpickler(file, fix_imports=fix_imports, buffers=buffers,
                      encoding=encoding, errors=errors).load()

# Use the faster _pickle ikiwa possible
jaribu:
    kutoka _pickle agiza (
        PickleError,
        PicklingError,
        UnpicklingError,
        Pickler,
        Unpickler,
        dump,
        dumps,
        load,
        loads
    )
tatizo ImportError:
    Pickler, Unpickler = _Pickler, _Unpickler
    dump, dumps, load, loads = _dump, _dumps, _load, _loads

# Doctest
eleza _test():
    agiza doctest
    rudisha doctest.testmod()

ikiwa __name__ == "__main__":
    agiza argparse
    parser = argparse.ArgumentParser(
        description='display contents of the pickle files')
    parser.add_argument(
        'pickle_file', type=argparse.FileType('br'),
        nargs='*', help='the pickle file')
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
        ikiwa sio args.pickle_file:
            parser.print_help()
        isipokua:
            agiza pprint
            kila f kwenye args.pickle_file:
                obj = load(f)
                pprint.pandika(obj)
