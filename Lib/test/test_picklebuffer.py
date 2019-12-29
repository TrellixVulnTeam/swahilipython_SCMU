"""Unit tests kila the PickleBuffer object.

Pickling tests themselves are kwenye pickletester.py.
"""

agiza gc
kutoka pickle agiza PickleBuffer
agiza weakref
agiza unittest

kutoka test agiza support


kundi B(bytes):
    pita


kundi PickleBufferTest(unittest.TestCase):

    eleza check_memoryview(self, pb, equiv):
        with memoryview(pb) kama m:
            with memoryview(equiv) kama expected:
                self.assertEqual(m.nbytes, expected.nbytes)
                self.assertEqual(m.readonly, expected.readonly)
                self.assertEqual(m.itemsize, expected.itemsize)
                self.assertEqual(m.shape, expected.shape)
                self.assertEqual(m.strides, expected.strides)
                self.assertEqual(m.c_contiguous, expected.c_contiguous)
                self.assertEqual(m.f_contiguous, expected.f_contiguous)
                self.assertEqual(m.format, expected.format)
                self.assertEqual(m.tobytes(), expected.tobytes())

    eleza test_constructor_failure(self):
        with self.assertRaises(TypeError):
            PickleBuffer()
        with self.assertRaises(TypeError):
            PickleBuffer("foo")
        # Released memoryview fails taking a buffer
        m = memoryview(b"foo")
        m.release()
        with self.assertRaises(ValueError):
            PickleBuffer(m)

    eleza test_basics(self):
        pb = PickleBuffer(b"foo")
        self.assertEqual(b"foo", bytes(pb))
        with memoryview(pb) kama m:
            self.assertKweli(m.readonly)

        pb = PickleBuffer(bytearray(b"foo"))
        self.assertEqual(b"foo", bytes(pb))
        with memoryview(pb) kama m:
            self.assertUongo(m.readonly)
            m[0] = 48
        self.assertEqual(b"0oo", bytes(pb))

    eleza test_release(self):
        pb = PickleBuffer(b"foo")
        pb.release()
        with self.assertRaises(ValueError) kama ashirias:
            memoryview(pb)
        self.assertIn("operation forbidden on released PickleBuffer object",
                      str(ashirias.exception))
        # Idempotency
        pb.release()

    eleza test_cycle(self):
        b = B(b"foo")
        pb = PickleBuffer(b)
        b.cycle = pb
        wpb = weakref.ref(pb)
        toa b, pb
        gc.collect()
        self.assertIsTupu(wpb())

    eleza test_ndarray_2d(self):
        # C-contiguous
        ndarray = support.import_module("_testbuffer").ndarray
        arr = ndarray(list(range(12)), shape=(4, 3), format='<i')
        self.assertKweli(arr.c_contiguous)
        self.assertUongo(arr.f_contiguous)
        pb = PickleBuffer(arr)
        self.check_memoryview(pb, arr)
        # Non-contiguous
        arr = arr[::2]
        self.assertUongo(arr.c_contiguous)
        self.assertUongo(arr.f_contiguous)
        pb = PickleBuffer(arr)
        self.check_memoryview(pb, arr)
        # F-contiguous
        arr = ndarray(list(range(12)), shape=(3, 4), strides=(4, 12), format='<i')
        self.assertKweli(arr.f_contiguous)
        self.assertUongo(arr.c_contiguous)
        pb = PickleBuffer(arr)
        self.check_memoryview(pb, arr)

    # Tests kila PickleBuffer.raw()

    eleza check_raw(self, obj, equiv):
        pb = PickleBuffer(obj)
        with pb.raw() kama m:
            self.assertIsInstance(m, memoryview)
            self.check_memoryview(m, equiv)

    eleza test_raw(self):
        kila obj kwenye (b"foo", bytearray(b"foo")):
            with self.subTest(obj=obj):
                self.check_raw(obj, obj)

    eleza test_raw_ndarray(self):
        # 1-D, contiguous
        ndarray = support.import_module("_testbuffer").ndarray
        arr = ndarray(list(range(3)), shape=(3,), format='<h')
        equiv = b"\x00\x00\x01\x00\x02\x00"
        self.check_raw(arr, equiv)
        # 2-D, C-contiguous
        arr = ndarray(list(range(6)), shape=(2, 3), format='<h')
        equiv = b"\x00\x00\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00"
        self.check_raw(arr, equiv)
        # 2-D, F-contiguous
        arr = ndarray(list(range(6)), shape=(2, 3), strides=(2, 4),
                      format='<h')
        # Note this ni different kutoka arr.tobytes()
        equiv = b"\x00\x00\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00"
        self.check_raw(arr, equiv)
        # 0-D
        arr = ndarray(456, shape=(), format='<i')
        equiv = b'\xc8\x01\x00\x00'
        self.check_raw(arr, equiv)

    eleza check_raw_non_contiguous(self, obj):
        pb = PickleBuffer(obj)
        with self.assertRaisesRegex(BufferError, "non-contiguous"):
            pb.raw()

    eleza test_raw_non_contiguous(self):
        # 1-D
        ndarray = support.import_module("_testbuffer").ndarray
        arr = ndarray(list(range(6)), shape=(6,), format='<i')[::2]
        self.check_raw_non_contiguous(arr)
        # 2-D
        arr = ndarray(list(range(12)), shape=(4, 3), format='<i')[::2]
        self.check_raw_non_contiguous(arr)

    eleza test_raw_released(self):
        pb = PickleBuffer(b"foo")
        pb.release()
        with self.assertRaises(ValueError) kama ashirias:
            pb.raw()


ikiwa __name__ == "__main__":
    unittest.main()
