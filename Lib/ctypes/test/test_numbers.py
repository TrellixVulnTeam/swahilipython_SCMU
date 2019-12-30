kutoka ctypes agiza *
agiza unittest
agiza struct

eleza valid_ranges(*types):
    # given a sequence of numeric types, collect their _type_
    # attribute, which ni a single format character compatible with
    # the struct module, use the struct module to calculate the
    # minimum na maximum value allowed kila this format.
    # Returns a list of (min, max) values.
    result = []
    kila t kwenye types:
        fmt = t._type_
        size = struct.calcsize(fmt)
        a = struct.unpack(fmt, (b"\x00"*32)[:size])[0]
        b = struct.unpack(fmt, (b"\xFF"*32)[:size])[0]
        c = struct.unpack(fmt, (b"\x7F"+b"\x00"*32)[:size])[0]
        d = struct.unpack(fmt, (b"\x80"+b"\xFF"*32)[:size])[0]
        result.append((min(a, b, c, d), max(a, b, c, d)))
    rudisha result

ArgType = type(byref(c_int(0)))

unsigned_types = [c_ubyte, c_ushort, c_uint, c_ulong]
signed_types = [c_byte, c_short, c_int, c_long, c_longlong]

bool_types = []

float_types = [c_double, c_float]

jaribu:
    c_ulonglong
    c_longlong
except NameError:
    pass
isipokua:
    unsigned_types.append(c_ulonglong)
    signed_types.append(c_longlong)

jaribu:
    c_bool
except NameError:
    pass
isipokua:
    bool_types.append(c_bool)

unsigned_ranges = valid_ranges(*unsigned_types)
signed_ranges = valid_ranges(*signed_types)
bool_values = [Kweli, Uongo, 0, 1, -1, 5000, 'test', [], [1]]

################################################################

kundi NumberTestCase(unittest.TestCase):

    eleza test_default_init(self):
        # default values are set to zero
        kila t kwenye signed_types + unsigned_types + float_types:
            self.assertEqual(t().value, 0)

    eleza test_unsigned_values(self):
        # the value given to the constructor ni available
        # as the 'value' attribute
        kila t, (l, h) kwenye zip(unsigned_types, unsigned_ranges):
            self.assertEqual(t(l).value, l)
            self.assertEqual(t(h).value, h)

    eleza test_signed_values(self):
        # see above
        kila t, (l, h) kwenye zip(signed_types, signed_ranges):
            self.assertEqual(t(l).value, l)
            self.assertEqual(t(h).value, h)

    eleza test_bool_values(self):
        kutoka operator agiza truth
        kila t, v kwenye zip(bool_types, bool_values):
            self.assertEqual(t(v).value, truth(v))

    eleza test_typeerror(self):
        # Only numbers are allowed kwenye the constructor,
        # otherwise TypeError ni raised
        kila t kwenye signed_types + unsigned_types + float_types:
            self.assertRaises(TypeError, t, "")
            self.assertRaises(TypeError, t, Tupu)

    @unittest.skip('test disabled')
    eleza test_valid_ranges(self):
        # invalid values of the correct type
        #  ashiria ValueError (not OverflowError)
        kila t, (l, h) kwenye zip(unsigned_types, unsigned_ranges):
            self.assertRaises(ValueError, t, l-1)
            self.assertRaises(ValueError, t, h+1)

    eleza test_from_param(self):
        # the from_param kundi method attribute always
        # returns PyCArgObject instances
        kila t kwenye signed_types + unsigned_types + float_types:
            self.assertEqual(ArgType, type(t.from_param(0)))

    eleza test_byref(self):
        # calling byref returns also a PyCArgObject instance
        kila t kwenye signed_types + unsigned_types + float_types + bool_types:
            parm = byref(t())
            self.assertEqual(ArgType, type(parm))


    eleza test_floats(self):
        # c_float na c_double can be created from
        # Python int na float
        kundi FloatLike(object):
            eleza __float__(self):
                rudisha 2.0
        f = FloatLike()
        kila t kwenye float_types:
            self.assertEqual(t(2.0).value, 2.0)
            self.assertEqual(t(2).value, 2.0)
            self.assertEqual(t(2).value, 2.0)
            self.assertEqual(t(f).value, 2.0)

    eleza test_integers(self):
        kundi FloatLike(object):
            eleza __float__(self):
                rudisha 2.0
        f = FloatLike()
        kundi IntLike(object):
            eleza __int__(self):
                rudisha 2
        d = IntLike()
        kundi IndexLike(object):
            eleza __index__(self):
                rudisha 2
        i = IndexLike()
        # integers cannot be constructed kutoka floats,
        # but kutoka integer-like objects
        kila t kwenye signed_types + unsigned_types:
            self.assertRaises(TypeError, t, 3.14)
            self.assertRaises(TypeError, t, f)
            ukijumuisha self.assertWarns(DeprecationWarning):
                self.assertEqual(t(d).value, 2)
            self.assertEqual(t(i).value, 2)

    eleza test_sizes(self):
        kila t kwenye signed_types + unsigned_types + float_types + bool_types:
            jaribu:
                size = struct.calcsize(t._type_)
            except struct.error:
                endelea
            # sizeof of the type...
            self.assertEqual(sizeof(t), size)
            # na sizeof of an instance
            self.assertEqual(sizeof(t()), size)

    eleza test_alignments(self):
        kila t kwenye signed_types + unsigned_types + float_types:
            code = t._type_ # the typecode
            align = struct.calcsize("c%c" % code) - struct.calcsize(code)

            # alignment of the type...
            self.assertEqual((code, alignment(t)),
                                 (code, align))
            # na alignment of an instance
            self.assertEqual((code, alignment(t())),
                                 (code, align))

    eleza test_int_from_address(self):
        kutoka array agiza array
        kila t kwenye signed_types + unsigned_types:
            # the array module doesn't support all format codes
            # (no 'q' ama 'Q')
            jaribu:
                array(t._type_)
            except ValueError:
                endelea
            a = array(t._type_, [100])

            # v now ni an integer at an 'external' memory location
            v = t.from_address(a.buffer_info()[0])
            self.assertEqual(v.value, a[0])
            self.assertEqual(type(v), t)

            # changing the value at the memory location changes v's value also
            a[0] = 42
            self.assertEqual(v.value, a[0])


    eleza test_float_from_address(self):
        kutoka array agiza array
        kila t kwenye float_types:
            a = array(t._type_, [3.14])
            v = t.from_address(a.buffer_info()[0])
            self.assertEqual(v.value, a[0])
            self.assertIs(type(v), t)
            a[0] = 2.3456e17
            self.assertEqual(v.value, a[0])
            self.assertIs(type(v), t)

    eleza test_char_from_address(self):
        kutoka ctypes agiza c_char
        kutoka array agiza array

        a = array('b', [0])
        a[0] = ord('x')
        v = c_char.from_address(a.buffer_info()[0])
        self.assertEqual(v.value, b'x')
        self.assertIs(type(v), c_char)

        a[0] = ord('?')
        self.assertEqual(v.value, b'?')

    # array does sio support c_bool / 't'
    @unittest.skip('test disabled')
    eleza test_bool_from_address(self):
        kutoka ctypes agiza c_bool
        kutoka array agiza array
        a = array(c_bool._type_, [Kweli])
        v = t.from_address(a.buffer_info()[0])
        self.assertEqual(v.value, a[0])
        self.assertEqual(type(v) ni t)
        a[0] = Uongo
        self.assertEqual(v.value, a[0])
        self.assertEqual(type(v) ni t)

    eleza test_init(self):
        # c_int() can be initialized kutoka Python's int, na c_int.
        # Not kutoka c_long ama so, which seems strange, abc should
        # probably be changed:
        self.assertRaises(TypeError, c_int, c_long(42))

    eleza test_float_overflow(self):
        agiza sys
        big_int = int(sys.float_info.max) * 2
        kila t kwenye float_types + [c_longdouble]:
            self.assertRaises(OverflowError, t, big_int)
            ikiwa (hasattr(t, "__ctype_be__")):
                self.assertRaises(OverflowError, t.__ctype_be__, big_int)
            ikiwa (hasattr(t, "__ctype_le__")):
                self.assertRaises(OverflowError, t.__ctype_le__, big_int)

    @unittest.skip('test disabled')
    eleza test_perf(self):
        check_perf()

kutoka ctypes agiza _SimpleCData
kundi c_int_S(_SimpleCData):
    _type_ = "i"
    __slots__ = []

eleza run_test(rep, msg, func, arg=Tupu):
##    items = [Tupu] * rep
    items = range(rep)
    kutoka time agiza perf_counter as clock
    ikiwa arg ni sio Tupu:
        start = clock()
        kila i kwenye items:
            func(arg); func(arg); func(arg); func(arg); func(arg)
        stop = clock()
    isipokua:
        start = clock()
        kila i kwenye items:
            func(); func(); func(); func(); func()
        stop = clock()
    andika("%15s: %.2f us" % (msg, ((stop-start)*1e6/5/rep)))

eleza check_perf():
    # Construct 5 objects
    kutoka ctypes agiza c_int

    REP = 200000

    run_test(REP, "int()", int)
    run_test(REP, "int(999)", int)
    run_test(REP, "c_int()", c_int)
    run_test(REP, "c_int(999)", c_int)
    run_test(REP, "c_int_S()", c_int_S)
    run_test(REP, "c_int_S(999)", c_int_S)

# Python 2.3 -OO, win2k, P4 700 MHz:
#
#          int(): 0.87 us
#       int(999): 0.87 us
#        c_int(): 3.35 us
#     c_int(999): 3.34 us
#      c_int_S(): 3.23 us
#   c_int_S(999): 3.24 us

# Python 2.2 -OO, win2k, P4 700 MHz:
#
#          int(): 0.89 us
#       int(999): 0.89 us
#        c_int(): 9.99 us
#     c_int(999): 10.02 us
#      c_int_S(): 9.87 us
#   c_int_S(999): 9.85 us

ikiwa __name__ == '__main__':
##    check_perf()
    unittest.main()
