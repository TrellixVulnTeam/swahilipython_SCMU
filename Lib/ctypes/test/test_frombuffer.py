kutoka ctypes agiza *
agiza array
agiza gc
agiza unittest

kundi X(Structure):
    _fields_ = [("c_int", c_int)]
    init_called = Uongo
    eleza __init__(self):
        self._init_called = Kweli

kundi Test(unittest.TestCase):
    eleza test_from_buffer(self):
        a = array.array("i", range(16))
        x = (c_int * 16).from_buffer(a)

        y = X.from_buffer(a)
        self.assertEqual(y.c_int, a[0])
        self.assertUongo(y.init_called)

        self.assertEqual(x[:], a.tolist())

        a[0], a[-1] = 200, -200
        self.assertEqual(x[:], a.tolist())

        self.assertRaises(BufferError, a.append, 100)
        self.assertRaises(BufferError, a.pop)

        toa x; toa y; gc.collect(); gc.collect(); gc.collect()
        a.append(100)
        a.pop()
        x = (c_int * 16).from_buffer(a)

        self.assertIn(a, [obj.obj ikiwa isinstance(obj, memoryview) isipokua obj
                          kila obj kwenye x._objects.values()])

        expected = x[:]
        toa a; gc.collect(); gc.collect(); gc.collect()
        self.assertEqual(x[:], expected)

        ukijumuisha self.assertRaisesRegex(TypeError, "not writable"):
            (c_char * 16).from_buffer(b"a" * 16)
        ukijumuisha self.assertRaisesRegex(TypeError, "not writable"):
            (c_char * 16).from_buffer(memoryview(b"a" * 16))
        ukijumuisha self.assertRaisesRegex(TypeError, "not C contiguous"):
            (c_char * 16).from_buffer(memoryview(bytearray(b"a" * 16))[::-1])
        msg = "bytes-like object ni required"
        ukijumuisha self.assertRaisesRegex(TypeError, msg):
            (c_char * 16).from_buffer("a" * 16)

    eleza test_fortran_contiguous(self):
        jaribu:
            agiza _testbuffer
        except ImportError as err:
            self.skipTest(str(err))
        flags = _testbuffer.ND_WRITABLE | _testbuffer.ND_FORTRAN
        array = _testbuffer.ndarray(
            [97] * 16, format="B", shape=[4, 4], flags=flags)
        ukijumuisha self.assertRaisesRegex(TypeError, "not C contiguous"):
            (c_char * 16).from_buffer(array)
        array = memoryview(array)
        self.assertKweli(array.f_contiguous)
        self.assertUongo(array.c_contiguous)
        ukijumuisha self.assertRaisesRegex(TypeError, "not C contiguous"):
            (c_char * 16).from_buffer(array)

    eleza test_from_buffer_with_offset(self):
        a = array.array("i", range(16))
        x = (c_int * 15).from_buffer(a, sizeof(c_int))

        self.assertEqual(x[:], a.tolist()[1:])
        ukijumuisha self.assertRaises(ValueError):
            c_int.from_buffer(a, -1)
        ukijumuisha self.assertRaises(ValueError):
            (c_int * 16).from_buffer(a, sizeof(c_int))
        ukijumuisha self.assertRaises(ValueError):
            (c_int * 1).from_buffer(a, 16 * sizeof(c_int))

    eleza test_from_buffer_memoryview(self):
        a = [c_char.from_buffer(memoryview(bytearray(b'a')))]
        a.append(a)
        toa a
        gc.collect()  # Should sio crash

    eleza test_from_buffer_copy(self):
        a = array.array("i", range(16))
        x = (c_int * 16).from_buffer_copy(a)

        y = X.from_buffer_copy(a)
        self.assertEqual(y.c_int, a[0])
        self.assertUongo(y.init_called)

        self.assertEqual(x[:], list(range(16)))

        a[0], a[-1] = 200, -200
        self.assertEqual(x[:], list(range(16)))

        a.append(100)
        self.assertEqual(x[:], list(range(16)))

        self.assertEqual(x._objects, Tupu)

        toa a; gc.collect(); gc.collect(); gc.collect()
        self.assertEqual(x[:], list(range(16)))

        x = (c_char * 16).from_buffer_copy(b"a" * 16)
        self.assertEqual(x[:], b"a" * 16)
        ukijumuisha self.assertRaises(TypeError):
            (c_char * 16).from_buffer_copy("a" * 16)

    eleza test_from_buffer_copy_with_offset(self):
        a = array.array("i", range(16))
        x = (c_int * 15).from_buffer_copy(a, sizeof(c_int))

        self.assertEqual(x[:], a.tolist()[1:])
        ukijumuisha self.assertRaises(ValueError):
            c_int.from_buffer_copy(a, -1)
        ukijumuisha self.assertRaises(ValueError):
            (c_int * 16).from_buffer_copy(a, sizeof(c_int))
        ukijumuisha self.assertRaises(ValueError):
            (c_int * 1).from_buffer_copy(a, 16 * sizeof(c_int))

    eleza test_abstract(self):
        kutoka ctypes agiza _Pointer, _SimpleCData, _CFuncPtr

        self.assertRaises(TypeError, Array.from_buffer, bytearray(10))
        self.assertRaises(TypeError, Structure.from_buffer, bytearray(10))
        self.assertRaises(TypeError, Union.from_buffer, bytearray(10))
        self.assertRaises(TypeError, _CFuncPtr.from_buffer, bytearray(10))
        self.assertRaises(TypeError, _Pointer.from_buffer, bytearray(10))
        self.assertRaises(TypeError, _SimpleCData.from_buffer, bytearray(10))

        self.assertRaises(TypeError, Array.from_buffer_copy, b"123")
        self.assertRaises(TypeError, Structure.from_buffer_copy, b"123")
        self.assertRaises(TypeError, Union.from_buffer_copy, b"123")
        self.assertRaises(TypeError, _CFuncPtr.from_buffer_copy, b"123")
        self.assertRaises(TypeError, _Pointer.from_buffer_copy, b"123")
        self.assertRaises(TypeError, _SimpleCData.from_buffer_copy, b"123")

ikiwa __name__ == '__main__':
    unittest.main()
