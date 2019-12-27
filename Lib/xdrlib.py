"""Implements (a subset of) Sun XDR -- eXternal Data Representation.

See: RFC 1014

"""

agiza struct
kutoka io agiza BytesIO
kutoka functools agiza wraps

__all__ = ["Error", "Packer", "Unpacker", "ConversionError"]

# exceptions
kundi Error(Exception):
    """Exception kundi for this module. Use:

    except xdrlib.Error as var:
        # var has the Error instance for the exception

    Public ivars:
        msg -- contains the message

    """
    eleza __init__(self, msg):
        self.msg = msg
    eleza __repr__(self):
        rudisha repr(self.msg)
    eleza __str__(self):
        rudisha str(self.msg)


kundi ConversionError(Error):
    pass

eleza raise_conversion_error(function):
    """ Wrap any raised struct.errors in a ConversionError. """

    @wraps(function)
    eleza result(self, value):
        try:
            rudisha function(self, value)
        except struct.error as e:
            raise ConversionError(e.args[0]) kutoka None
    rudisha result


kundi Packer:
    """Pack various data representations into a buffer."""

    eleza __init__(self):
        self.reset()

    eleza reset(self):
        self.__buf = BytesIO()

    eleza get_buffer(self):
        rudisha self.__buf.getvalue()
    # backwards compatibility
    get_buf = get_buffer

    @raise_conversion_error
    eleza pack_uint(self, x):
        self.__buf.write(struct.pack('>L', x))

    @raise_conversion_error
    eleza pack_int(self, x):
        self.__buf.write(struct.pack('>l', x))

    pack_enum = pack_int

    eleza pack_bool(self, x):
        ikiwa x: self.__buf.write(b'\0\0\0\1')
        else: self.__buf.write(b'\0\0\0\0')

    eleza pack_uhyper(self, x):
        try:
            self.pack_uint(x>>32 & 0xffffffff)
        except (TypeError, struct.error) as e:
            raise ConversionError(e.args[0]) kutoka None
        try:
            self.pack_uint(x & 0xffffffff)
        except (TypeError, struct.error) as e:
            raise ConversionError(e.args[0]) kutoka None

    pack_hyper = pack_uhyper

    @raise_conversion_error
    eleza pack_float(self, x):
        self.__buf.write(struct.pack('>f', x))

    @raise_conversion_error
    eleza pack_double(self, x):
        self.__buf.write(struct.pack('>d', x))

    eleza pack_fstring(self, n, s):
        ikiwa n < 0:
            raise ValueError('fstring size must be nonnegative')
        data = s[:n]
        n = ((n+3)//4)*4
        data = data + (n - len(data)) * b'\0'
        self.__buf.write(data)

    pack_fopaque = pack_fstring

    eleza pack_string(self, s):
        n = len(s)
        self.pack_uint(n)
        self.pack_fstring(n, s)

    pack_opaque = pack_string
    pack_bytes = pack_string

    eleza pack_list(self, list, pack_item):
        for item in list:
            self.pack_uint(1)
            pack_item(item)
        self.pack_uint(0)

    eleza pack_farray(self, n, list, pack_item):
        ikiwa len(list) != n:
            raise ValueError('wrong array size')
        for item in list:
            pack_item(item)

    eleza pack_array(self, list, pack_item):
        n = len(list)
        self.pack_uint(n)
        self.pack_farray(n, list, pack_item)



kundi Unpacker:
    """Unpacks various data representations kutoka the given buffer."""

    eleza __init__(self, data):
        self.reset(data)

    eleza reset(self, data):
        self.__buf = data
        self.__pos = 0

    eleza get_position(self):
        rudisha self.__pos

    eleza set_position(self, position):
        self.__pos = position

    eleza get_buffer(self):
        rudisha self.__buf

    eleza done(self):
        ikiwa self.__pos < len(self.__buf):
            raise Error('unextracted data remains')

    eleza unpack_uint(self):
        i = self.__pos
        self.__pos = j = i+4
        data = self.__buf[i:j]
        ikiwa len(data) < 4:
            raise EOFError
        rudisha struct.unpack('>L', data)[0]

    eleza unpack_int(self):
        i = self.__pos
        self.__pos = j = i+4
        data = self.__buf[i:j]
        ikiwa len(data) < 4:
            raise EOFError
        rudisha struct.unpack('>l', data)[0]

    unpack_enum = unpack_int

    eleza unpack_bool(self):
        rudisha bool(self.unpack_int())

    eleza unpack_uhyper(self):
        hi = self.unpack_uint()
        lo = self.unpack_uint()
        rudisha int(hi)<<32 | lo

    eleza unpack_hyper(self):
        x = self.unpack_uhyper()
        ikiwa x >= 0x8000000000000000:
            x = x - 0x10000000000000000
        rudisha x

    eleza unpack_float(self):
        i = self.__pos
        self.__pos = j = i+4
        data = self.__buf[i:j]
        ikiwa len(data) < 4:
            raise EOFError
        rudisha struct.unpack('>f', data)[0]

    eleza unpack_double(self):
        i = self.__pos
        self.__pos = j = i+8
        data = self.__buf[i:j]
        ikiwa len(data) < 8:
            raise EOFError
        rudisha struct.unpack('>d', data)[0]

    eleza unpack_fstring(self, n):
        ikiwa n < 0:
            raise ValueError('fstring size must be nonnegative')
        i = self.__pos
        j = i + (n+3)//4*4
        ikiwa j > len(self.__buf):
            raise EOFError
        self.__pos = j
        rudisha self.__buf[i:i+n]

    unpack_fopaque = unpack_fstring

    eleza unpack_string(self):
        n = self.unpack_uint()
        rudisha self.unpack_fstring(n)

    unpack_opaque = unpack_string
    unpack_bytes = unpack_string

    eleza unpack_list(self, unpack_item):
        list = []
        while 1:
            x = self.unpack_uint()
            ikiwa x == 0: break
            ikiwa x != 1:
                raise ConversionError('0 or 1 expected, got %r' % (x,))
            item = unpack_item()
            list.append(item)
        rudisha list

    eleza unpack_farray(self, n, unpack_item):
        list = []
        for i in range(n):
            list.append(unpack_item())
        rudisha list

    eleza unpack_array(self, unpack_item):
        n = self.unpack_uint()
        rudisha self.unpack_farray(n, unpack_item)
