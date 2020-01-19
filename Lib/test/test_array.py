"""Test the arraymodule.
   Roger E. Masse
"""

agiza unittest
kutoka test agiza support
kutoka test.support agiza _2G
agiza weakref
agiza pickle
agiza operator
agiza struct
agiza sys
agiza warnings

agiza array
kutoka array agiza _array_reconstructor kama array_reconstructor

sizeof_wchar = array.array('u').itemsize


kundi ArraySubclass(array.array):
    pita

kundi ArraySubclassWithKwargs(array.array):
    eleza __init__(self, typecode, newarg=Tupu):
        array.array.__init__(self)

typecodes = 'ubBhHiIlLfdqQ'

kundi MiscTest(unittest.TestCase):

    eleza test_bad_constructor(self):
        self.assertRaises(TypeError, array.array)
        self.assertRaises(TypeError, array.array, spam=42)
        self.assertRaises(TypeError, array.array, 'xx')
        self.assertRaises(ValueError, array.array, 'x')

    eleza test_empty(self):
        # Exercise code kila handling zero-length arrays
        a = array.array('B')
        a[:] = a
        self.assertEqual(len(a), 0)
        self.assertEqual(len(a + a), 0)
        self.assertEqual(len(a * 3), 0)
        a += a
        self.assertEqual(len(a), 0)


# Machine format codes.
#
# Search kila "enum machine_format_code" kwenye Modules/arraymodule.c to get the
# authoritative values.
UNKNOWN_FORMAT = -1
UNSIGNED_INT8 = 0
SIGNED_INT8 = 1
UNSIGNED_INT16_LE = 2
UNSIGNED_INT16_BE = 3
SIGNED_INT16_LE = 4
SIGNED_INT16_BE = 5
UNSIGNED_INT32_LE = 6
UNSIGNED_INT32_BE = 7
SIGNED_INT32_LE = 8
SIGNED_INT32_BE = 9
UNSIGNED_INT64_LE = 10
UNSIGNED_INT64_BE = 11
SIGNED_INT64_LE = 12
SIGNED_INT64_BE = 13
IEEE_754_FLOAT_LE = 14
IEEE_754_FLOAT_BE = 15
IEEE_754_DOUBLE_LE = 16
IEEE_754_DOUBLE_BE = 17
UTF16_LE = 18
UTF16_BE = 19
UTF32_LE = 20
UTF32_BE = 21

kundi ArrayReconstructorTest(unittest.TestCase):

    eleza test_error(self):
        self.assertRaises(TypeError, array_reconstructor,
                          "", "b", 0, b"")
        self.assertRaises(TypeError, array_reconstructor,
                          str, "b", 0, b"")
        self.assertRaises(TypeError, array_reconstructor,
                          array.array, "b", '', b"")
        self.assertRaises(TypeError, array_reconstructor,
                          array.array, "b", 0, "")
        self.assertRaises(ValueError, array_reconstructor,
                          array.array, "?", 0, b"")
        self.assertRaises(ValueError, array_reconstructor,
                          array.array, "b", UNKNOWN_FORMAT, b"")
        self.assertRaises(ValueError, array_reconstructor,
                          array.array, "b", 22, b"")
        self.assertRaises(ValueError, array_reconstructor,
                          array.array, "d", 16, b"a")

    eleza test_numbers(self):
        testcases = (
            (['B', 'H', 'I', 'L'], UNSIGNED_INT8, '=BBBB',
             [0x80, 0x7f, 0, 0xff]),
            (['b', 'h', 'i', 'l'], SIGNED_INT8, '=bbb',
             [-0x80, 0x7f, 0]),
            (['H', 'I', 'L'], UNSIGNED_INT16_LE, '<HHHH',
             [0x8000, 0x7fff, 0, 0xffff]),
            (['H', 'I', 'L'], UNSIGNED_INT16_BE, '>HHHH',
             [0x8000, 0x7fff, 0, 0xffff]),
            (['h', 'i', 'l'], SIGNED_INT16_LE, '<hhh',
             [-0x8000, 0x7fff, 0]),
            (['h', 'i', 'l'], SIGNED_INT16_BE, '>hhh',
             [-0x8000, 0x7fff, 0]),
            (['I', 'L'], UNSIGNED_INT32_LE, '<IIII',
             [1<<31, (1<<31)-1, 0, (1<<32)-1]),
            (['I', 'L'], UNSIGNED_INT32_BE, '>IIII',
             [1<<31, (1<<31)-1, 0, (1<<32)-1]),
            (['i', 'l'], SIGNED_INT32_LE, '<iii',
             [-1<<31, (1<<31)-1, 0]),
            (['i', 'l'], SIGNED_INT32_BE, '>iii',
             [-1<<31, (1<<31)-1, 0]),
            (['L'], UNSIGNED_INT64_LE, '<QQQQ',
             [1<<31, (1<<31)-1, 0, (1<<32)-1]),
            (['L'], UNSIGNED_INT64_BE, '>QQQQ',
             [1<<31, (1<<31)-1, 0, (1<<32)-1]),
            (['l'], SIGNED_INT64_LE, '<qqq',
             [-1<<31, (1<<31)-1, 0]),
            (['l'], SIGNED_INT64_BE, '>qqq',
             [-1<<31, (1<<31)-1, 0]),
            # The following tests kila INT64 will ashiria an OverflowError
            # when run on a 32-bit machine. The tests are simply skipped
            # kwenye that case.
            (['L'], UNSIGNED_INT64_LE, '<QQQQ',
             [1<<63, (1<<63)-1, 0, (1<<64)-1]),
            (['L'], UNSIGNED_INT64_BE, '>QQQQ',
             [1<<63, (1<<63)-1, 0, (1<<64)-1]),
            (['l'], SIGNED_INT64_LE, '<qqq',
             [-1<<63, (1<<63)-1, 0]),
            (['l'], SIGNED_INT64_BE, '>qqq',
             [-1<<63, (1<<63)-1, 0]),
            (['f'], IEEE_754_FLOAT_LE, '<ffff',
             [16711938.0, float('inf'), float('-inf'), -0.0]),
            (['f'], IEEE_754_FLOAT_BE, '>ffff',
             [16711938.0, float('inf'), float('-inf'), -0.0]),
            (['d'], IEEE_754_DOUBLE_LE, '<dddd',
             [9006104071832581.0, float('inf'), float('-inf'), -0.0]),
            (['d'], IEEE_754_DOUBLE_BE, '>dddd',
             [9006104071832581.0, float('inf'), float('-inf'), -0.0])
        )
        kila testcase kwenye testcases:
            valid_typecodes, mformat_code, struct_fmt, values = testcase
            arraystr = struct.pack(struct_fmt, *values)
            kila typecode kwenye valid_typecodes:
                jaribu:
                    a = array.array(typecode, values)
                tatizo OverflowError:
                    endelea  # Skip this test case.
                b = array_reconstructor(
                    array.array, typecode, mformat_code, arraystr)
                self.assertEqual(a, b,
                    msg="{0!r} != {1!r}; testcase={2!r}".format(a, b, testcase))

    eleza test_unicode(self):
        teststr = "Bonne Journ\xe9e \U0002030a\U00020347"
        testcases = (
            (UTF16_LE, "UTF-16-LE"),
            (UTF16_BE, "UTF-16-BE"),
            (UTF32_LE, "UTF-32-LE"),
            (UTF32_BE, "UTF-32-BE")
        )
        kila testcase kwenye testcases:
            mformat_code, encoding = testcase
            a = array.array('u', teststr)
            b = array_reconstructor(
                array.array, 'u', mformat_code, teststr.encode(encoding))
            self.assertEqual(a, b,
                msg="{0!r} != {1!r}; testcase={2!r}".format(a, b, testcase))


kundi BaseTest:
    # Required kundi attributes (provided by subclasses
    # typecode: the typecode to test
    # example: an initializer usable kwenye the constructor kila this type
    # smallerexample: the same length kama example, but smaller
    # biggerexample: the same length kama example, but bigger
    # outside: An entry that ni haiko kwenye example
    # minitemsize: the minimum guaranteed itemsize

    eleza assertEntryEqual(self, entry1, entry2):
        self.assertEqual(entry1, entry2)

    eleza badtypecode(self):
        # Return a typecode that ni different kutoka our own
        rudisha typecodes[(typecodes.index(self.typecode)+1) % len(typecodes)]

    eleza test_constructor(self):
        a = array.array(self.typecode)
        self.assertEqual(a.typecode, self.typecode)
        self.assertGreaterEqual(a.itemsize, self.minitemsize)
        self.assertRaises(TypeError, array.array, self.typecode, Tupu)

    eleza test_len(self):
        a = array.array(self.typecode)
        a.append(self.example[0])
        self.assertEqual(len(a), 1)

        a = array.array(self.typecode, self.example)
        self.assertEqual(len(a), len(self.example))

    eleza test_buffer_info(self):
        a = array.array(self.typecode, self.example)
        self.assertRaises(TypeError, a.buffer_info, 42)
        bi = a.buffer_info()
        self.assertIsInstance(bi, tuple)
        self.assertEqual(len(bi), 2)
        self.assertIsInstance(bi[0], int)
        self.assertIsInstance(bi[1], int)
        self.assertEqual(bi[1], len(a))

    eleza test_byteswap(self):
        ikiwa self.typecode == 'u':
            example = '\U00100100'
        isipokua:
            example = self.example
        a = array.array(self.typecode, example)
        self.assertRaises(TypeError, a.byteswap, 42)
        ikiwa a.itemsize kwenye (1, 2, 4, 8):
            b = array.array(self.typecode, example)
            b.byteswap()
            ikiwa a.itemsize==1:
                self.assertEqual(a, b)
            isipokua:
                self.assertNotEqual(a, b)
            b.byteswap()
            self.assertEqual(a, b)

    eleza test_copy(self):
        agiza copy
        a = array.array(self.typecode, self.example)
        b = copy.copy(a)
        self.assertNotEqual(id(a), id(b))
        self.assertEqual(a, b)

    eleza test_deepcopy(self):
        agiza copy
        a = array.array(self.typecode, self.example)
        b = copy.deepcopy(a)
        self.assertNotEqual(id(a), id(b))
        self.assertEqual(a, b)

    eleza test_reduce_ex(self):
        a = array.array(self.typecode, self.example)
        kila protocol kwenye range(3):
            self.assertIs(a.__reduce_ex__(protocol)[0], array.array)
        kila protocol kwenye range(3, pickle.HIGHEST_PROTOCOL + 1):
            self.assertIs(a.__reduce_ex__(protocol)[0], array_reconstructor)

    eleza test_pickle(self):
        kila protocol kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            a = array.array(self.typecode, self.example)
            b = pickle.loads(pickle.dumps(a, protocol))
            self.assertNotEqual(id(a), id(b))
            self.assertEqual(a, b)

            a = ArraySubclass(self.typecode, self.example)
            a.x = 10
            b = pickle.loads(pickle.dumps(a, protocol))
            self.assertNotEqual(id(a), id(b))
            self.assertEqual(a, b)
            self.assertEqual(a.x, b.x)
            self.assertEqual(type(a), type(b))

    eleza test_pickle_for_empty_array(self):
        kila protocol kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            a = array.array(self.typecode)
            b = pickle.loads(pickle.dumps(a, protocol))
            self.assertNotEqual(id(a), id(b))
            self.assertEqual(a, b)

            a = ArraySubclass(self.typecode)
            a.x = 10
            b = pickle.loads(pickle.dumps(a, protocol))
            self.assertNotEqual(id(a), id(b))
            self.assertEqual(a, b)
            self.assertEqual(a.x, b.x)
            self.assertEqual(type(a), type(b))

    eleza test_iterator_pickle(self):
        orig = array.array(self.typecode, self.example)
        data = list(orig)
        data2 = data[::-1]
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            # initial iterator
            itorig = iter(orig)
            d = pickle.dumps((itorig, orig), proto)
            it, a = pickle.loads(d)
            a.fromlist(data2)
            self.assertEqual(type(it), type(itorig))
            self.assertEqual(list(it), data + data2)

            # running iterator
            next(itorig)
            d = pickle.dumps((itorig, orig), proto)
            it, a = pickle.loads(d)
            a.fromlist(data2)
            self.assertEqual(type(it), type(itorig))
            self.assertEqual(list(it), data[1:] + data2)

            # empty iterator
            kila i kwenye range(1, len(data)):
                next(itorig)
            d = pickle.dumps((itorig, orig), proto)
            it, a = pickle.loads(d)
            a.fromlist(data2)
            self.assertEqual(type(it), type(itorig))
            self.assertEqual(list(it), data2)

            # exhausted iterator
            self.assertRaises(StopIteration, next, itorig)
            d = pickle.dumps((itorig, orig), proto)
            it, a = pickle.loads(d)
            a.fromlist(data2)
            self.assertEqual(list(it), [])

    eleza test_exhausted_iterator(self):
        a = array.array(self.typecode, self.example)
        self.assertEqual(list(a), list(self.example))
        exhit = iter(a)
        empit = iter(a)
        kila x kwenye exhit:  # exhaust the iterator
            next(empit)  # sio exhausted
        a.append(self.outside)
        self.assertEqual(list(exhit), [])
        self.assertEqual(list(empit), [self.outside])
        self.assertEqual(list(a), list(self.example) + [self.outside])

    eleza test_insert(self):
        a = array.array(self.typecode, self.example)
        a.insert(0, self.example[0])
        self.assertEqual(len(a), 1+len(self.example))
        self.assertEqual(a[0], a[1])
        self.assertRaises(TypeError, a.insert)
        self.assertRaises(TypeError, a.insert, Tupu)
        self.assertRaises(TypeError, a.insert, 0, Tupu)

        a = array.array(self.typecode, self.example)
        a.insert(-1, self.example[0])
        self.assertEqual(
            a,
            array.array(
                self.typecode,
                self.example[:-1] + self.example[:1] + self.example[-1:]
            )
        )

        a = array.array(self.typecode, self.example)
        a.insert(-1000, self.example[0])
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[:1] + self.example)
        )

        a = array.array(self.typecode, self.example)
        a.insert(1000, self.example[0])
        self.assertEqual(
            a,
            array.array(self.typecode, self.example + self.example[:1])
        )

    eleza test_tofromfile(self):
        a = array.array(self.typecode, 2*self.example)
        self.assertRaises(TypeError, a.tofile)
        support.unlink(support.TESTFN)
        f = open(support.TESTFN, 'wb')
        jaribu:
            a.tofile(f)
            f.close()
            b = array.array(self.typecode)
            f = open(support.TESTFN, 'rb')
            self.assertRaises(TypeError, b.fromfile)
            b.fromfile(f, len(self.example))
            self.assertEqual(b, array.array(self.typecode, self.example))
            self.assertNotEqual(a, b)
            self.assertRaises(EOFError, b.fromfile, f, len(self.example)+1)
            self.assertEqual(a, b)
            f.close()
        mwishowe:
            ikiwa sio f.closed:
                f.close()
            support.unlink(support.TESTFN)

    eleza test_fromfile_ioerror(self):
        # Issue #5395: Check ikiwa fromfile raises a proper OSError
        # instead of EOFError.
        a = array.array(self.typecode)
        f = open(support.TESTFN, 'wb')
        jaribu:
            self.assertRaises(OSError, a.fromfile, f, len(self.example))
        mwishowe:
            f.close()
            support.unlink(support.TESTFN)

    eleza test_filewrite(self):
        a = array.array(self.typecode, 2*self.example)
        f = open(support.TESTFN, 'wb')
        jaribu:
            f.write(a)
            f.close()
            b = array.array(self.typecode)
            f = open(support.TESTFN, 'rb')
            b.fromfile(f, len(self.example))
            self.assertEqual(b, array.array(self.typecode, self.example))
            self.assertNotEqual(a, b)
            b.fromfile(f, len(self.example))
            self.assertEqual(a, b)
            f.close()
        mwishowe:
            ikiwa sio f.closed:
                f.close()
            support.unlink(support.TESTFN)

    eleza test_tofromlist(self):
        a = array.array(self.typecode, 2*self.example)
        b = array.array(self.typecode)
        self.assertRaises(TypeError, a.tolist, 42)
        self.assertRaises(TypeError, b.fromlist)
        self.assertRaises(TypeError, b.fromlist, 42)
        self.assertRaises(TypeError, b.fromlist, [Tupu])
        b.fromlist(a.tolist())
        self.assertEqual(a, b)

    eleza test_tofromstring(self):
        # Warnings sio raised when arguments are incorrect kama Argument Clinic
        # handles that before the warning can be raised.
        nb_warnings = 2
        ukijumuisha warnings.catch_warnings(record=Kweli) kama r:
            warnings.filterwarnings("always",
                                    message=r"(to|from)string\(\) ni deprecated",
                                    category=DeprecationWarning)
            a = array.array(self.typecode, 2*self.example)
            b = array.array(self.typecode)
            self.assertRaises(TypeError, a.tostring, 42)
            self.assertRaises(TypeError, b.fromstring)
            self.assertRaises(TypeError, b.fromstring, 42)
            b.fromstring(a.tostring())
            self.assertEqual(a, b)
            ikiwa a.itemsize>1:
                self.assertRaises(ValueError, b.fromstring, "x")
                nb_warnings += 1
        self.assertEqual(len(r), nb_warnings)

    eleza test_tofrombytes(self):
        a = array.array(self.typecode, 2*self.example)
        b = array.array(self.typecode)
        self.assertRaises(TypeError, a.tobytes, 42)
        self.assertRaises(TypeError, b.frombytes)
        self.assertRaises(TypeError, b.frombytes, 42)
        b.frombytes(a.tobytes())
        c = array.array(self.typecode, bytearray(a.tobytes()))
        self.assertEqual(a, b)
        self.assertEqual(a, c)
        ikiwa a.itemsize>1:
            self.assertRaises(ValueError, b.frombytes, b"x")

    eleza test_fromarray(self):
        a = array.array(self.typecode, self.example)
        b = array.array(self.typecode, a)
        self.assertEqual(a, b)

    eleza test_repr(self):
        a = array.array(self.typecode, 2*self.example)
        self.assertEqual(a, eval(repr(a), {"array": array.array}))

        a = array.array(self.typecode)
        self.assertEqual(repr(a), "array('%s')" % self.typecode)

    eleza test_str(self):
        a = array.array(self.typecode, 2*self.example)
        str(a)

    eleza test_cmp(self):
        a = array.array(self.typecode, self.example)
        self.assertIs(a == 42, Uongo)
        self.assertIs(a != 42, Kweli)

        self.assertIs(a == a, Kweli)
        self.assertIs(a != a, Uongo)
        self.assertIs(a < a, Uongo)
        self.assertIs(a <= a, Kweli)
        self.assertIs(a > a, Uongo)
        self.assertIs(a >= a, Kweli)

        al = array.array(self.typecode, self.smallerexample)
        ab = array.array(self.typecode, self.biggerexample)

        self.assertIs(a == 2*a, Uongo)
        self.assertIs(a != 2*a, Kweli)
        self.assertIs(a < 2*a, Kweli)
        self.assertIs(a <= 2*a, Kweli)
        self.assertIs(a > 2*a, Uongo)
        self.assertIs(a >= 2*a, Uongo)

        self.assertIs(a == al, Uongo)
        self.assertIs(a != al, Kweli)
        self.assertIs(a < al, Uongo)
        self.assertIs(a <= al, Uongo)
        self.assertIs(a > al, Kweli)
        self.assertIs(a >= al, Kweli)

        self.assertIs(a == ab, Uongo)
        self.assertIs(a != ab, Kweli)
        self.assertIs(a < ab, Kweli)
        self.assertIs(a <= ab, Kweli)
        self.assertIs(a > ab, Uongo)
        self.assertIs(a >= ab, Uongo)

    eleza test_add(self):
        a = array.array(self.typecode, self.example) \
            + array.array(self.typecode, self.example[::-1])
        self.assertEqual(
            a,
            array.array(self.typecode, self.example + self.example[::-1])
        )

        b = array.array(self.badtypecode())
        self.assertRaises(TypeError, a.__add__, b)

        self.assertRaises(TypeError, a.__add__, "bad")

    eleza test_iadd(self):
        a = array.array(self.typecode, self.example[::-1])
        b = a
        a += array.array(self.typecode, 2*self.example)
        self.assertIs(a, b)
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[::-1]+2*self.example)
        )
        a = array.array(self.typecode, self.example)
        a += a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example + self.example)
        )

        b = array.array(self.badtypecode())
        self.assertRaises(TypeError, a.__add__, b)

        self.assertRaises(TypeError, a.__iadd__, "bad")

    eleza test_mul(self):
        a = 5*array.array(self.typecode, self.example)
        self.assertEqual(
            a,
            array.array(self.typecode, 5*self.example)
        )

        a = array.array(self.typecode, self.example)*5
        self.assertEqual(
            a,
            array.array(self.typecode, self.example*5)
        )

        a = 0*array.array(self.typecode, self.example)
        self.assertEqual(
            a,
            array.array(self.typecode)
        )

        a = (-1)*array.array(self.typecode, self.example)
        self.assertEqual(
            a,
            array.array(self.typecode)
        )

        a = 5 * array.array(self.typecode, self.example[:1])
        self.assertEqual(
            a,
            array.array(self.typecode, [a[0]] * 5)
        )

        self.assertRaises(TypeError, a.__mul__, "bad")

    eleza test_imul(self):
        a = array.array(self.typecode, self.example)
        b = a

        a *= 5
        self.assertIs(a, b)
        self.assertEqual(
            a,
            array.array(self.typecode, 5*self.example)
        )

        a *= 0
        self.assertIs(a, b)
        self.assertEqual(a, array.array(self.typecode))

        a *= 1000
        self.assertIs(a, b)
        self.assertEqual(a, array.array(self.typecode))

        a *= -1
        self.assertIs(a, b)
        self.assertEqual(a, array.array(self.typecode))

        a = array.array(self.typecode, self.example)
        a *= -1
        self.assertEqual(a, array.array(self.typecode))

        self.assertRaises(TypeError, a.__imul__, "bad")

    eleza test_getitem(self):
        a = array.array(self.typecode, self.example)
        self.assertEntryEqual(a[0], self.example[0])
        self.assertEntryEqual(a[0], self.example[0])
        self.assertEntryEqual(a[-1], self.example[-1])
        self.assertEntryEqual(a[-1], self.example[-1])
        self.assertEntryEqual(a[len(self.example)-1], self.example[-1])
        self.assertEntryEqual(a[-len(self.example)], self.example[0])
        self.assertRaises(TypeError, a.__getitem__)
        self.assertRaises(IndexError, a.__getitem__, len(self.example))
        self.assertRaises(IndexError, a.__getitem__, -len(self.example)-1)

    eleza test_setitem(self):
        a = array.array(self.typecode, self.example)
        a[0] = a[-1]
        self.assertEntryEqual(a[0], a[-1])

        a = array.array(self.typecode, self.example)
        a[0] = a[-1]
        self.assertEntryEqual(a[0], a[-1])

        a = array.array(self.typecode, self.example)
        a[-1] = a[0]
        self.assertEntryEqual(a[0], a[-1])

        a = array.array(self.typecode, self.example)
        a[-1] = a[0]
        self.assertEntryEqual(a[0], a[-1])

        a = array.array(self.typecode, self.example)
        a[len(self.example)-1] = a[0]
        self.assertEntryEqual(a[0], a[-1])

        a = array.array(self.typecode, self.example)
        a[-len(self.example)] = a[-1]
        self.assertEntryEqual(a[0], a[-1])

        self.assertRaises(TypeError, a.__setitem__)
        self.assertRaises(TypeError, a.__setitem__, Tupu)
        self.assertRaises(TypeError, a.__setitem__, 0, Tupu)
        self.assertRaises(
            IndexError,
            a.__setitem__,
            len(self.example), self.example[0]
        )
        self.assertRaises(
            IndexError,
            a.__setitem__,
            -len(self.example)-1, self.example[0]
        )

    eleza test_delitem(self):
        a = array.array(self.typecode, self.example)
        toa a[0]
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[1:])
        )

        a = array.array(self.typecode, self.example)
        toa a[-1]
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[:-1])
        )

        a = array.array(self.typecode, self.example)
        toa a[len(self.example)-1]
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[:-1])
        )

        a = array.array(self.typecode, self.example)
        toa a[-len(self.example)]
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[1:])
        )

        self.assertRaises(TypeError, a.__delitem__)
        self.assertRaises(TypeError, a.__delitem__, Tupu)
        self.assertRaises(IndexError, a.__delitem__, len(self.example))
        self.assertRaises(IndexError, a.__delitem__, -len(self.example)-1)

    eleza test_getslice(self):
        a = array.array(self.typecode, self.example)
        self.assertEqual(a[:], a)

        self.assertEqual(
            a[1:],
            array.array(self.typecode, self.example[1:])
        )

        self.assertEqual(
            a[:1],
            array.array(self.typecode, self.example[:1])
        )

        self.assertEqual(
            a[:-1],
            array.array(self.typecode, self.example[:-1])
        )

        self.assertEqual(
            a[-1:],
            array.array(self.typecode, self.example[-1:])
        )

        self.assertEqual(
            a[-1:-1],
            array.array(self.typecode)
        )

        self.assertEqual(
            a[2:1],
            array.array(self.typecode)
        )

        self.assertEqual(
            a[1000:],
            array.array(self.typecode)
        )
        self.assertEqual(a[-1000:], a)
        self.assertEqual(a[:1000], a)
        self.assertEqual(
            a[:-1000],
            array.array(self.typecode)
        )
        self.assertEqual(a[-1000:1000], a)
        self.assertEqual(
            a[2000:1000],
            array.array(self.typecode)
        )

    eleza test_extended_getslice(self):
        # Test extended slicing by comparing ukijumuisha list slicing
        # (Assumes list conversion works correctly, too)
        a = array.array(self.typecode, self.example)
        indices = (0, Tupu, 1, 3, 19, 100, sys.maxsize, -1, -2, -31, -100)
        kila start kwenye indices:
            kila stop kwenye indices:
                # Everything tatizo the initial 0 (invalid step)
                kila step kwenye indices[1:]:
                    self.assertEqual(list(a[start:stop:step]),
                                     list(a)[start:stop:step])

    eleza test_setslice(self):
        a = array.array(self.typecode, self.example)
        a[:1] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example + self.example[1:])
        )

        a = array.array(self.typecode, self.example)
        a[:-1] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example + self.example[-1:])
        )

        a = array.array(self.typecode, self.example)
        a[-1:] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[:-1] + self.example)
        )

        a = array.array(self.typecode, self.example)
        a[1:] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[:1] + self.example)
        )

        a = array.array(self.typecode, self.example)
        a[1:-1] = a
        self.assertEqual(
            a,
            array.array(
                self.typecode,
                self.example[:1] + self.example + self.example[-1:]
            )
        )

        a = array.array(self.typecode, self.example)
        a[1000:] = a
        self.assertEqual(
            a,
            array.array(self.typecode, 2*self.example)
        )

        a = array.array(self.typecode, self.example)
        a[-1000:] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example)
        )

        a = array.array(self.typecode, self.example)
        a[:1000] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example)
        )

        a = array.array(self.typecode, self.example)
        a[:-1000] = a
        self.assertEqual(
            a,
            array.array(self.typecode, 2*self.example)
        )

        a = array.array(self.typecode, self.example)
        a[1:0] = a
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[:1] + self.example + self.example[1:])
        )

        a = array.array(self.typecode, self.example)
        a[2000:1000] = a
        self.assertEqual(
            a,
            array.array(self.typecode, 2*self.example)
        )

        a = array.array(self.typecode, self.example)
        self.assertRaises(TypeError, a.__setitem__, slice(0, 0), Tupu)
        self.assertRaises(TypeError, a.__setitem__, slice(0, 1), Tupu)

        b = array.array(self.badtypecode())
        self.assertRaises(TypeError, a.__setitem__, slice(0, 0), b)
        self.assertRaises(TypeError, a.__setitem__, slice(0, 1), b)

    eleza test_extended_set_del_slice(self):
        indices = (0, Tupu, 1, 3, 19, 100, sys.maxsize, -1, -2, -31, -100)
        kila start kwenye indices:
            kila stop kwenye indices:
                # Everything tatizo the initial 0 (invalid step)
                kila step kwenye indices[1:]:
                    a = array.array(self.typecode, self.example)
                    L = list(a)
                    # Make sure we have a slice of exactly the right length,
                    # but ukijumuisha (hopefully) different data.
                    data = L[start:stop:step]
                    data.reverse()
                    L[start:stop:step] = data
                    a[start:stop:step] = array.array(self.typecode, data)
                    self.assertEqual(a, array.array(self.typecode, L))

                    toa L[start:stop:step]
                    toa a[start:stop:step]
                    self.assertEqual(a, array.array(self.typecode, L))

    eleza test_index(self):
        example = 2*self.example
        a = array.array(self.typecode, example)
        self.assertRaises(TypeError, a.index)
        kila x kwenye example:
            self.assertEqual(a.index(x), example.index(x))
        self.assertRaises(ValueError, a.index, Tupu)
        self.assertRaises(ValueError, a.index, self.outside)

    eleza test_count(self):
        example = 2*self.example
        a = array.array(self.typecode, example)
        self.assertRaises(TypeError, a.count)
        kila x kwenye example:
            self.assertEqual(a.count(x), example.count(x))
        self.assertEqual(a.count(self.outside), 0)
        self.assertEqual(a.count(Tupu), 0)

    eleza test_remove(self):
        kila x kwenye self.example:
            example = 2*self.example
            a = array.array(self.typecode, example)
            pos = example.index(x)
            example2 = example[:pos] + example[pos+1:]
            a.remove(x)
            self.assertEqual(a, array.array(self.typecode, example2))

        a = array.array(self.typecode, self.example)
        self.assertRaises(ValueError, a.remove, self.outside)

        self.assertRaises(ValueError, a.remove, Tupu)

    eleza test_pop(self):
        a = array.array(self.typecode)
        self.assertRaises(IndexError, a.pop)

        a = array.array(self.typecode, 2*self.example)
        self.assertRaises(TypeError, a.pop, 42, 42)
        self.assertRaises(TypeError, a.pop, Tupu)
        self.assertRaises(IndexError, a.pop, len(a))
        self.assertRaises(IndexError, a.pop, -len(a)-1)

        self.assertEntryEqual(a.pop(0), self.example[0])
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[1:]+self.example)
        )
        self.assertEntryEqual(a.pop(1), self.example[2])
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[1:2]+self.example[3:]+self.example)
        )
        self.assertEntryEqual(a.pop(0), self.example[1])
        self.assertEntryEqual(a.pop(), self.example[-1])
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[3:]+self.example[:-1])
        )

    eleza test_reverse(self):
        a = array.array(self.typecode, self.example)
        self.assertRaises(TypeError, a.reverse, 42)
        a.reverse()
        self.assertEqual(
            a,
            array.array(self.typecode, self.example[::-1])
        )

    eleza test_extend(self):
        a = array.array(self.typecode, self.example)
        self.assertRaises(TypeError, a.extend)
        a.extend(array.array(self.typecode, self.example[::-1]))
        self.assertEqual(
            a,
            array.array(self.typecode, self.example+self.example[::-1])
        )

        a = array.array(self.typecode, self.example)
        a.extend(a)
        self.assertEqual(
            a,
            array.array(self.typecode, self.example+self.example)
        )

        b = array.array(self.badtypecode())
        self.assertRaises(TypeError, a.extend, b)

        a = array.array(self.typecode, self.example)
        a.extend(self.example[::-1])
        self.assertEqual(
            a,
            array.array(self.typecode, self.example+self.example[::-1])
        )

    eleza test_constructor_with_iterable_argument(self):
        a = array.array(self.typecode, iter(self.example))
        b = array.array(self.typecode, self.example)
        self.assertEqual(a, b)

        # non-iterable argument
        self.assertRaises(TypeError, array.array, self.typecode, 10)

        # pita through errors raised kwenye __iter__
        kundi A:
            eleza __iter__(self):
                ashiria UnicodeError
        self.assertRaises(UnicodeError, array.array, self.typecode, A())

        # pita through errors raised kwenye next()
        eleza B():
            ashiria UnicodeError
            tuma Tupu
        self.assertRaises(UnicodeError, array.array, self.typecode, B())

    eleza test_coveritertraverse(self):
        jaribu:
            agiza gc
        tatizo ImportError:
            self.skipTest('gc module sio available')
        a = array.array(self.typecode)
        l = [iter(a)]
        l.append(l)
        gc.collect()

    eleza test_buffer(self):
        a = array.array(self.typecode, self.example)
        m = memoryview(a)
        expected = m.tobytes()
        self.assertEqual(a.tobytes(), expected)
        self.assertEqual(a.tobytes()[0], expected[0])
        # Resizing ni forbidden when there are buffer exports.
        # For issue 4509, we also check after each error that
        # the array was sio modified.
        self.assertRaises(BufferError, a.append, a[0])
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, a.extend, a[0:1])
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, a.remove, a[0])
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, a.pop, 0)
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, a.fromlist, a.tolist())
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, a.frombytes, a.tobytes())
        self.assertEqual(m.tobytes(), expected)
        ikiwa self.typecode == 'u':
            self.assertRaises(BufferError, a.fromunicode, a.tounicode())
            self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, operator.imul, a, 2)
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, operator.imul, a, 0)
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, operator.setitem, a, slice(0, 0), a)
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, operator.delitem, a, 0)
        self.assertEqual(m.tobytes(), expected)
        self.assertRaises(BufferError, operator.delitem, a, slice(0, 1))
        self.assertEqual(m.tobytes(), expected)

    eleza test_weakref(self):
        s = array.array(self.typecode, self.example)
        p = weakref.proxy(s)
        self.assertEqual(p.tobytes(), s.tobytes())
        s = Tupu
        self.assertRaises(ReferenceError, len, p)

    @unittest.skipUnless(hasattr(sys, 'getrefcount'),
                         'test needs sys.getrefcount()')
    eleza test_bug_782369(self):
        kila i kwenye range(10):
            b = array.array('B', range(64))
        rc = sys.getrefcount(10)
        kila i kwenye range(10):
            b = array.array('B', range(64))
        self.assertEqual(rc, sys.getrefcount(10))

    eleza test_subclass_with_kwargs(self):
        # SF bug #1486663 -- this used to erroneously ashiria a TypeError
        ArraySubclassWithKwargs('b', newarg=1)

    eleza test_create_from_bytes(self):
        # XXX This test probably needs to be moved kwenye a subkundi ama
        # generalized to use self.typecode.
        a = array.array('H', b"1234")
        self.assertEqual(len(a) * a.itemsize, 4)

    @support.cpython_only
    eleza test_sizeof_with_buffer(self):
        a = array.array(self.typecode, self.example)
        basesize = support.calcvobjsize('Pn2Pi')
        buffer_size = a.buffer_info()[1] * a.itemsize
        support.check_sizeof(self, a, basesize + buffer_size)

    @support.cpython_only
    eleza test_sizeof_without_buffer(self):
        a = array.array(self.typecode)
        basesize = support.calcvobjsize('Pn2Pi')
        support.check_sizeof(self, a, basesize)

    eleza test_initialize_with_unicode(self):
        ikiwa self.typecode != 'u':
            ukijumuisha self.assertRaises(TypeError) kama cm:
                a = array.array(self.typecode, 'foo')
            self.assertIn("cannot use a str", str(cm.exception))
            ukijumuisha self.assertRaises(TypeError) kama cm:
                a = array.array(self.typecode, array.array('u', 'foo'))
            self.assertIn("cannot use a unicode array", str(cm.exception))
        isipokua:
            a = array.array(self.typecode, "foo")
            a = array.array(self.typecode, array.array('u', 'foo'))

    @support.cpython_only
    eleza test_obsolete_write_lock(self):
        kutoka _testcapi agiza getbuffer_with_null_view
        a = array.array('B', b"")
        self.assertRaises(BufferError, getbuffer_with_null_view, a)

    eleza test_free_after_iterating(self):
        support.check_free_after_iterating(self, iter, array.array,
                                           (self.typecode,))
        support.check_free_after_iterating(self, reversed, array.array,
                                           (self.typecode,))

kundi StringTest(BaseTest):

    eleza test_setitem(self):
        super().test_setitem()
        a = array.array(self.typecode, self.example)
        self.assertRaises(TypeError, a.__setitem__, 0, self.example[:2])

kundi UnicodeTest(StringTest, unittest.TestCase):
    typecode = 'u'
    example = '\x01\u263a\x00\ufeff'
    smallerexample = '\x01\u263a\x00\ufefe'
    biggerexample = '\x01\u263a\x01\ufeff'
    outside = str('\x33')
    minitemsize = 2

    eleza test_unicode(self):
        self.assertRaises(TypeError, array.array, 'b', 'foo')

        a = array.array('u', '\xa0\xc2\u1234')
        a.fromunicode(' ')
        a.fromunicode('')
        a.fromunicode('')
        a.fromunicode('\x11abc\xff\u1234')
        s = a.tounicode()
        self.assertEqual(s, '\xa0\xc2\u1234 \x11abc\xff\u1234')
        self.assertEqual(a.itemsize, sizeof_wchar)

        s = '\x00="\'a\\b\x80\xff\u0000\u0001\u1234'
        a = array.array('u', s)
        self.assertEqual(
            repr(a),
            "array('u', '\\x00=\"\\'a\\\\b\\x80\xff\\x00\\x01\u1234')")

        self.assertRaises(TypeError, a.fromunicode)

    eleza test_issue17223(self):
        # this used to crash
        ikiwa sizeof_wchar == 4:
            # U+FFFFFFFF ni an invalid code point kwenye Unicode 6.0
            invalid_str = b'\xff\xff\xff\xff'
        isipokua:
            # PyUnicode_FromUnicode() cannot fail ukijumuisha 16-bit wchar_t
            self.skipTest("specific to 32-bit wchar_t")
        a = array.array('u', invalid_str)
        self.assertRaises(ValueError, a.tounicode)
        self.assertRaises(ValueError, str, a)

kundi NumberTest(BaseTest):

    eleza test_extslice(self):
        a = array.array(self.typecode, range(5))
        self.assertEqual(a[::], a)
        self.assertEqual(a[::2], array.array(self.typecode, [0,2,4]))
        self.assertEqual(a[1::2], array.array(self.typecode, [1,3]))
        self.assertEqual(a[::-1], array.array(self.typecode, [4,3,2,1,0]))
        self.assertEqual(a[::-2], array.array(self.typecode, [4,2,0]))
        self.assertEqual(a[3::-2], array.array(self.typecode, [3,1]))
        self.assertEqual(a[-100:100:], a)
        self.assertEqual(a[100:-100:-1], a[::-1])
        self.assertEqual(a[-100:100:2], array.array(self.typecode, [0,2,4]))
        self.assertEqual(a[1000:2000:2], array.array(self.typecode, []))
        self.assertEqual(a[-1000:-2000:-2], array.array(self.typecode, []))

    eleza test_delslice(self):
        a = array.array(self.typecode, range(5))
        toa a[::2]
        self.assertEqual(a, array.array(self.typecode, [1,3]))
        a = array.array(self.typecode, range(5))
        toa a[1::2]
        self.assertEqual(a, array.array(self.typecode, [0,2,4]))
        a = array.array(self.typecode, range(5))
        toa a[1::-2]
        self.assertEqual(a, array.array(self.typecode, [0,2,3,4]))
        a = array.array(self.typecode, range(10))
        toa a[::1000]
        self.assertEqual(a, array.array(self.typecode, [1,2,3,4,5,6,7,8,9]))
        # test issue7788
        a = array.array(self.typecode, range(10))
        toa a[9::1<<333]

    eleza test_assignment(self):
        a = array.array(self.typecode, range(10))
        a[::2] = array.array(self.typecode, [42]*5)
        self.assertEqual(a, array.array(self.typecode, [42, 1, 42, 3, 42, 5, 42, 7, 42, 9]))
        a = array.array(self.typecode, range(10))
        a[::-4] = array.array(self.typecode, [10]*3)
        self.assertEqual(a, array.array(self.typecode, [0, 10, 2, 3, 4, 10, 6, 7, 8 ,10]))
        a = array.array(self.typecode, range(4))
        a[::-1] = a
        self.assertEqual(a, array.array(self.typecode, [3, 2, 1, 0]))
        a = array.array(self.typecode, range(10))
        b = a[:]
        c = a[:]
        ins = array.array(self.typecode, range(2))
        a[2:3] = ins
        b[slice(2,3)] = ins
        c[2:3:] = ins

    eleza test_iterationcontains(self):
        a = array.array(self.typecode, range(10))
        self.assertEqual(list(a), list(range(10)))
        b = array.array(self.typecode, [20])
        self.assertEqual(a[-1] kwenye a, Kweli)
        self.assertEqual(b[0] haiko kwenye a, Kweli)

    eleza check_overflow(self, lower, upper):
        # method to be used by subclasses

        # should sio overflow assigning lower limit
        a = array.array(self.typecode, [lower])
        a[0] = lower
        # should overflow assigning less than lower limit
        self.assertRaises(OverflowError, array.array, self.typecode, [lower-1])
        self.assertRaises(OverflowError, a.__setitem__, 0, lower-1)
        # should sio overflow assigning upper limit
        a = array.array(self.typecode, [upper])
        a[0] = upper
        # should overflow assigning more than upper limit
        self.assertRaises(OverflowError, array.array, self.typecode, [upper+1])
        self.assertRaises(OverflowError, a.__setitem__, 0, upper+1)

    eleza test_subclassing(self):
        typecode = self.typecode
        kundi ExaggeratingArray(array.array):
            __slots__ = ['offset']

            eleza __new__(cls, typecode, data, offset):
                rudisha array.array.__new__(cls, typecode, data)

            eleza __init__(self, typecode, data, offset):
                self.offset = offset

            eleza __getitem__(self, i):
                rudisha array.array.__getitem__(self, i) + self.offset

        a = ExaggeratingArray(self.typecode, [3, 6, 7, 11], 4)
        self.assertEntryEqual(a[0], 7)

        self.assertRaises(AttributeError, setattr, a, "color", "blue")

    eleza test_frombytearray(self):
        a = array.array('b', range(10))
        b = array.array(self.typecode, a)
        self.assertEqual(a, b)

kundi IntegerNumberTest(NumberTest):
    eleza test_type_error(self):
        a = array.array(self.typecode)
        a.append(42)
        ukijumuisha self.assertRaises(TypeError):
            a.append(42.0)
        ukijumuisha self.assertRaises(TypeError):
            a[0] = 42.0

kundi Intable:
    eleza __init__(self, num):
        self._num = num
    eleza __index__(self):
        rudisha self._num
    eleza __int__(self):
        rudisha self._num
    eleza __sub__(self, other):
        rudisha Intable(int(self) - int(other))
    eleza __add__(self, other):
        rudisha Intable(int(self) + int(other))

kundi SignedNumberTest(IntegerNumberTest):
    example = [-1, 0, 1, 42, 0x7f]
    smallerexample = [-1, 0, 1, 42, 0x7e]
    biggerexample = [-1, 0, 1, 43, 0x7f]
    outside = 23

    eleza test_overflow(self):
        a = array.array(self.typecode)
        lower = -1 * int(pow(2, a.itemsize * 8 - 1))
        upper = int(pow(2, a.itemsize * 8 - 1)) - 1
        self.check_overflow(lower, upper)
        self.check_overflow(Intable(lower), Intable(upper))

kundi UnsignedNumberTest(IntegerNumberTest):
    example = [0, 1, 17, 23, 42, 0xff]
    smallerexample = [0, 1, 17, 23, 42, 0xfe]
    biggerexample = [0, 1, 17, 23, 43, 0xff]
    outside = 0xaa

    eleza test_overflow(self):
        a = array.array(self.typecode)
        lower = 0
        upper = int(pow(2, a.itemsize * 8)) - 1
        self.check_overflow(lower, upper)
        self.check_overflow(Intable(lower), Intable(upper))

    eleza test_bytes_extend(self):
        s = bytes(self.example)

        a = array.array(self.typecode, self.example)
        a.extend(s)
        self.assertEqual(
            a,
            array.array(self.typecode, self.example+self.example)
        )

        a = array.array(self.typecode, self.example)
        a.extend(bytearray(reversed(s)))
        self.assertEqual(
            a,
            array.array(self.typecode, self.example+self.example[::-1])
        )


kundi ByteTest(SignedNumberTest, unittest.TestCase):
    typecode = 'b'
    minitemsize = 1

kundi UnsignedByteTest(UnsignedNumberTest, unittest.TestCase):
    typecode = 'B'
    minitemsize = 1

kundi ShortTest(SignedNumberTest, unittest.TestCase):
    typecode = 'h'
    minitemsize = 2

kundi UnsignedShortTest(UnsignedNumberTest, unittest.TestCase):
    typecode = 'H'
    minitemsize = 2

kundi IntTest(SignedNumberTest, unittest.TestCase):
    typecode = 'i'
    minitemsize = 2

kundi UnsignedIntTest(UnsignedNumberTest, unittest.TestCase):
    typecode = 'I'
    minitemsize = 2

kundi LongTest(SignedNumberTest, unittest.TestCase):
    typecode = 'l'
    minitemsize = 4

kundi UnsignedLongTest(UnsignedNumberTest, unittest.TestCase):
    typecode = 'L'
    minitemsize = 4

kundi LongLongTest(SignedNumberTest, unittest.TestCase):
    typecode = 'q'
    minitemsize = 8

kundi UnsignedLongLongTest(UnsignedNumberTest, unittest.TestCase):
    typecode = 'Q'
    minitemsize = 8

kundi FPTest(NumberTest):
    example = [-42.0, 0, 42, 1e5, -1e10]
    smallerexample = [-42.0, 0, 42, 1e5, -2e10]
    biggerexample = [-42.0, 0, 42, 1e5, 1e10]
    outside = 23

    eleza assertEntryEqual(self, entry1, entry2):
        self.assertAlmostEqual(entry1, entry2)

    eleza test_nan(self):
        a = array.array(self.typecode, [float('nan')])
        b = array.array(self.typecode, [float('nan')])
        self.assertIs(a != b, Kweli)
        self.assertIs(a == b, Uongo)
        self.assertIs(a > b, Uongo)
        self.assertIs(a >= b, Uongo)
        self.assertIs(a < b, Uongo)
        self.assertIs(a <= b, Uongo)

    eleza test_byteswap(self):
        a = array.array(self.typecode, self.example)
        self.assertRaises(TypeError, a.byteswap, 42)
        ikiwa a.itemsize kwenye (1, 2, 4, 8):
            b = array.array(self.typecode, self.example)
            b.byteswap()
            ikiwa a.itemsize==1:
                self.assertEqual(a, b)
            isipokua:
                # On alphas treating the byte swapped bit patters as
                # floats/doubles results kwenye floating point exceptions
                # => compare the 8bit string values instead
                self.assertNotEqual(a.tobytes(), b.tobytes())
            b.byteswap()
            self.assertEqual(a, b)

kundi FloatTest(FPTest, unittest.TestCase):
    typecode = 'f'
    minitemsize = 4

kundi DoubleTest(FPTest, unittest.TestCase):
    typecode = 'd'
    minitemsize = 8

    eleza test_alloc_overflow(self):
        kutoka sys agiza maxsize
        a = array.array('d', [-1]*65536)
        jaribu:
            a *= maxsize//65536 + 1
        tatizo MemoryError:
            pita
        isipokua:
            self.fail("Array of size > maxsize created - MemoryError expected")
        b = array.array('d', [ 2.71828183, 3.14159265, -1])
        jaribu:
            b * (maxsize//3 + 1)
        tatizo MemoryError:
            pita
        isipokua:
            self.fail("Array of size > maxsize created - MemoryError expected")


kundi LargeArrayTest(unittest.TestCase):
    typecode = 'b'

    eleza example(self, size):
        # We assess a base memuse of <=2.125 kila constructing this array
        base = array.array(self.typecode, [0, 1, 2, 3, 4, 5, 6, 7]) * (size // 8)
        base += array.array(self.typecode, [99]*(size % 8) + [8, 9, 10, 11])
        rudisha base

    @support.bigmemtest(_2G, memuse=2.125)
    eleza test_example_data(self, size):
        example = self.example(size)
        self.assertEqual(len(example), size+4)

    @support.bigmemtest(_2G, memuse=2.125)
    eleza test_access(self, size):
        example = self.example(size)
        self.assertEqual(example[0], 0)
        self.assertEqual(example[-(size+4)], 0)
        self.assertEqual(example[size], 8)
        self.assertEqual(example[-4], 8)
        self.assertEqual(example[size+3], 11)
        self.assertEqual(example[-1], 11)

    @support.bigmemtest(_2G, memuse=2.125+1)
    eleza test_slice(self, size):
        example = self.example(size)
        self.assertEqual(list(example[:4]), [0, 1, 2, 3])
        self.assertEqual(list(example[-4:]), [8, 9, 10, 11])
        part = example[1:-1]
        self.assertEqual(len(part), size+2)
        self.assertEqual(part[0], 1)
        self.assertEqual(part[-1], 10)
        toa part
        part = example[::2]
        self.assertEqual(len(part), (size+5)//2)
        self.assertEqual(list(part[:4]), [0, 2, 4, 6])
        ikiwa size % 2:
            self.assertEqual(list(part[-2:]), [9, 11])
        isipokua:
            self.assertEqual(list(part[-2:]), [8, 10])

    @support.bigmemtest(_2G, memuse=2.125)
    eleza test_count(self, size):
        example = self.example(size)
        self.assertEqual(example.count(0), size//8)
        self.assertEqual(example.count(11), 1)

    @support.bigmemtest(_2G, memuse=2.125)
    eleza test_append(self, size):
        example = self.example(size)
        example.append(12)
        self.assertEqual(example[-1], 12)

    @support.bigmemtest(_2G, memuse=2.125)
    eleza test_extend(self, size):
        example = self.example(size)
        example.extend(iter([12, 13, 14, 15]))
        self.assertEqual(len(example), size+8)
        self.assertEqual(list(example[-8:]), [8, 9, 10, 11, 12, 13, 14, 15])

    @support.bigmemtest(_2G, memuse=2.125)
    eleza test_frombytes(self, size):
        example = self.example(size)
        example.frombytes(b'abcd')
        self.assertEqual(len(example), size+8)
        self.assertEqual(list(example[-8:]), [8, 9, 10, 11] + list(b'abcd'))

    @support.bigmemtest(_2G, memuse=2.125)
    eleza test_fromlist(self, size):
        example = self.example(size)
        example.fromlist([12, 13, 14, 15])
        self.assertEqual(len(example), size+8)
        self.assertEqual(list(example[-8:]), [8, 9, 10, 11, 12, 13, 14, 15])

    @support.bigmemtest(_2G, memuse=2.125)
    eleza test_index(self, size):
        example = self.example(size)
        self.assertEqual(example.index(0), 0)
        self.assertEqual(example.index(1), 1)
        self.assertEqual(example.index(7), 7)
        self.assertEqual(example.index(11), size+3)

    @support.bigmemtest(_2G, memuse=2.125)
    eleza test_insert(self, size):
        example = self.example(size)
        example.insert(0, 12)
        example.insert(10, 13)
        example.insert(size+1, 14)
        self.assertEqual(len(example), size+7)
        self.assertEqual(example[0], 12)
        self.assertEqual(example[10], 13)
        self.assertEqual(example[size+1], 14)

    @support.bigmemtest(_2G, memuse=2.125)
    eleza test_pop(self, size):
        example = self.example(size)
        self.assertEqual(example.pop(0), 0)
        self.assertEqual(example[0], 1)
        self.assertEqual(example.pop(size+1), 10)
        self.assertEqual(example[size+1], 11)
        self.assertEqual(example.pop(1), 2)
        self.assertEqual(example[1], 3)
        self.assertEqual(len(example), size+1)
        self.assertEqual(example.pop(), 11)
        self.assertEqual(len(example), size)

    @support.bigmemtest(_2G, memuse=2.125)
    eleza test_remove(self, size):
        example = self.example(size)
        example.remove(0)
        self.assertEqual(len(example), size+3)
        self.assertEqual(example[0], 1)
        example.remove(10)
        self.assertEqual(len(example), size+2)
        self.assertEqual(example[size], 9)
        self.assertEqual(example[size+1], 11)

    @support.bigmemtest(_2G, memuse=2.125)
    eleza test_reverse(self, size):
        example = self.example(size)
        example.reverse()
        self.assertEqual(len(example), size+4)
        self.assertEqual(example[0], 11)
        self.assertEqual(example[3], 8)
        self.assertEqual(example[-1], 0)
        example.reverse()
        self.assertEqual(len(example), size+4)
        self.assertEqual(list(example[:4]), [0, 1, 2, 3])
        self.assertEqual(list(example[-4:]), [8, 9, 10, 11])

    # list takes about 9 bytes per element
    @support.bigmemtest(_2G, memuse=2.125+9)
    eleza test_tolist(self, size):
        example = self.example(size)
        ls = example.tolist()
        self.assertEqual(len(ls), len(example))
        self.assertEqual(ls[:8], list(example[:8]))
        self.assertEqual(ls[-8:], list(example[-8:]))

ikiwa __name__ == "__main__":
    unittest.main()
