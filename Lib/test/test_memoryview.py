"""Unit tests kila the memoryview

   Some tests are kwenye test_bytes. Many tests that require _testbuffer.ndarray
   are kwenye test_buffer.
"""

agiza unittest
agiza test.support
agiza sys
agiza gc
agiza weakref
agiza array
agiza io
agiza copy
agiza pickle


kundi AbstractMemoryTests:
    source_bytes = b"abcdef"

    @property
    eleza _source(self):
        rudisha self.source_bytes

    @property
    eleza _types(self):
        rudisha filter(Tupu, [self.ro_type, self.rw_type])

    eleza check_getitem_with_type(self, tp):
        b = tp(self._source)
        oldrefcount = sys.getrefcount(b)
        m = self._view(b)
        self.assertEqual(m[0], ord(b"a"))
        self.assertIsInstance(m[0], int)
        self.assertEqual(m[5], ord(b"f"))
        self.assertEqual(m[-1], ord(b"f"))
        self.assertEqual(m[-6], ord(b"a"))
        # Bounds checking
        self.assertRaises(IndexError, lambda: m[6])
        self.assertRaises(IndexError, lambda: m[-7])
        self.assertRaises(IndexError, lambda: m[sys.maxsize])
        self.assertRaises(IndexError, lambda: m[-sys.maxsize])
        # Type checking
        self.assertRaises(TypeError, lambda: m[Tupu])
        self.assertRaises(TypeError, lambda: m[0.0])
        self.assertRaises(TypeError, lambda: m["a"])
        m = Tupu
        self.assertEqual(sys.getrefcount(b), oldrefcount)

    eleza test_getitem(self):
        kila tp kwenye self._types:
            self.check_getitem_with_type(tp)

    eleza test_iter(self):
        kila tp kwenye self._types:
            b = tp(self._source)
            m = self._view(b)
            self.assertEqual(list(m), [m[i] kila i kwenye range(len(m))])

    eleza test_setitem_readonly(self):
        ikiwa sio self.ro_type:
            self.skipTest("no read-only type to test")
        b = self.ro_type(self._source)
        oldrefcount = sys.getrefcount(b)
        m = self._view(b)
        eleza setitem(value):
            m[0] = value
        self.assertRaises(TypeError, setitem, b"a")
        self.assertRaises(TypeError, setitem, 65)
        self.assertRaises(TypeError, setitem, memoryview(b"a"))
        m = Tupu
        self.assertEqual(sys.getrefcount(b), oldrefcount)

    eleza test_setitem_writable(self):
        ikiwa sio self.rw_type:
            self.skipTest("no writable type to test")
        tp = self.rw_type
        b = self.rw_type(self._source)
        oldrefcount = sys.getrefcount(b)
        m = self._view(b)
        m[0] = ord(b'1')
        self._check_contents(tp, b, b"1bcdef")
        m[0:1] = tp(b"0")
        self._check_contents(tp, b, b"0bcdef")
        m[1:3] = tp(b"12")
        self._check_contents(tp, b, b"012def")
        m[1:1] = tp(b"")
        self._check_contents(tp, b, b"012def")
        m[:] = tp(b"abcdef")
        self._check_contents(tp, b, b"abcdef")

        # Overlapping copies of a view into itself
        m[0:3] = m[2:5]
        self._check_contents(tp, b, b"cdedef")
        m[:] = tp(b"abcdef")
        m[2:5] = m[0:3]
        self._check_contents(tp, b, b"ababcf")

        eleza setitem(key, value):
            m[key] = tp(value)
        # Bounds checking
        self.assertRaises(IndexError, setitem, 6, b"a")
        self.assertRaises(IndexError, setitem, -7, b"a")
        self.assertRaises(IndexError, setitem, sys.maxsize, b"a")
        self.assertRaises(IndexError, setitem, -sys.maxsize, b"a")
        # Wrong index/slice types
        self.assertRaises(TypeError, setitem, 0.0, b"a")
        self.assertRaises(TypeError, setitem, (0,), b"a")
        self.assertRaises(TypeError, setitem, (slice(0,1,1), 0), b"a")
        self.assertRaises(TypeError, setitem, (0, slice(0,1,1)), b"a")
        self.assertRaises(TypeError, setitem, (0,), b"a")
        self.assertRaises(TypeError, setitem, "a", b"a")
        # Not implemented: multidimensional slices
        slices = (slice(0,1,1), slice(0,1,2))
        self.assertRaises(NotImplementedError, setitem, slices, b"a")
        # Trying to resize the memory object
        exc = ValueError ikiwa m.format == 'c' isipokua TypeError
        self.assertRaises(exc, setitem, 0, b"")
        self.assertRaises(exc, setitem, 0, b"ab")
        self.assertRaises(ValueError, setitem, slice(1,1), b"a")
        self.assertRaises(ValueError, setitem, slice(0,2), b"a")

        m = Tupu
        self.assertEqual(sys.getrefcount(b), oldrefcount)

    eleza test_delitem(self):
        kila tp kwenye self._types:
            b = tp(self._source)
            m = self._view(b)
            ukijumuisha self.assertRaises(TypeError):
                toa m[1]
            ukijumuisha self.assertRaises(TypeError):
                toa m[1:4]

    eleza test_tobytes(self):
        kila tp kwenye self._types:
            m = self._view(tp(self._source))
            b = m.tobytes()
            # This calls self.getitem_type() on each separate byte of b"abcdef"
            expected = b"".join(
                self.getitem_type(bytes([c])) kila c kwenye b"abcdef")
            self.assertEqual(b, expected)
            self.assertIsInstance(b, bytes)

    eleza test_tolist(self):
        kila tp kwenye self._types:
            m = self._view(tp(self._source))
            l = m.tolist()
            self.assertEqual(l, list(b"abcdef"))

    eleza test_compare(self):
        # memoryviews can compare kila equality ukijumuisha other objects
        # having the buffer interface.
        kila tp kwenye self._types:
            m = self._view(tp(self._source))
            kila tp_comp kwenye self._types:
                self.assertKweli(m == tp_comp(b"abcdef"))
                self.assertUongo(m != tp_comp(b"abcdef"))
                self.assertUongo(m == tp_comp(b"abcde"))
                self.assertKweli(m != tp_comp(b"abcde"))
                self.assertUongo(m == tp_comp(b"abcde1"))
                self.assertKweli(m != tp_comp(b"abcde1"))
            self.assertKweli(m == m)
            self.assertKweli(m == m[:])
            self.assertKweli(m[0:6] == m[:])
            self.assertUongo(m[0:5] == m)

            # Comparison ukijumuisha objects which don't support the buffer API
            self.assertUongo(m == "abcdef")
            self.assertKweli(m != "abcdef")
            self.assertUongo("abcdef" == m)
            self.assertKweli("abcdef" != m)

            # Unordered comparisons
            kila c kwenye (m, b"abcdef"):
                self.assertRaises(TypeError, lambda: m < c)
                self.assertRaises(TypeError, lambda: c <= m)
                self.assertRaises(TypeError, lambda: m >= c)
                self.assertRaises(TypeError, lambda: c > m)

    eleza check_attributes_with_type(self, tp):
        m = self._view(tp(self._source))
        self.assertEqual(m.format, self.format)
        self.assertEqual(m.itemsize, self.itemsize)
        self.assertEqual(m.ndim, 1)
        self.assertEqual(m.shape, (6,))
        self.assertEqual(len(m), 6)
        self.assertEqual(m.strides, (self.itemsize,))
        self.assertEqual(m.suboffsets, ())
        rudisha m

    eleza test_attributes_readonly(self):
        ikiwa sio self.ro_type:
            self.skipTest("no read-only type to test")
        m = self.check_attributes_with_type(self.ro_type)
        self.assertEqual(m.readonly, Kweli)

    eleza test_attributes_writable(self):
        ikiwa sio self.rw_type:
            self.skipTest("no writable type to test")
        m = self.check_attributes_with_type(self.rw_type)
        self.assertEqual(m.readonly, Uongo)

    eleza test_getbuffer(self):
        # Test PyObject_GetBuffer() on a memoryview object.
        kila tp kwenye self._types:
            b = tp(self._source)
            oldrefcount = sys.getrefcount(b)
            m = self._view(b)
            oldviewrefcount = sys.getrefcount(m)
            s = str(m, "utf-8")
            self._check_contents(tp, b, s.encode("utf-8"))
            self.assertEqual(sys.getrefcount(m), oldviewrefcount)
            m = Tupu
            self.assertEqual(sys.getrefcount(b), oldrefcount)

    eleza test_gc(self):
        kila tp kwenye self._types:
            ikiwa sio isinstance(tp, type):
                # If tp ni a factory rather than a plain type, skip
                endelea

            kundi MyView():
                eleza __init__(self, base):
                    self.m = memoryview(base)
            kundi MySource(tp):
                pass
            kundi MyObject:
                pass

            # Create a reference cycle through a memoryview object.
            # This exercises mbuf_clear().
            b = MySource(tp(b'abc'))
            m = self._view(b)
            o = MyObject()
            b.m = m
            b.o = o
            wr = weakref.ref(o)
            b = m = o = Tupu
            # The cycle must be broken
            gc.collect()
            self.assertKweli(wr() ni Tupu, wr())

            # This exercises memory_clear().
            m = MyView(tp(b'abc'))
            o = MyObject()
            m.x = m
            m.o = o
            wr = weakref.ref(o)
            m = o = Tupu
            # The cycle must be broken
            gc.collect()
            self.assertKweli(wr() ni Tupu, wr())

    eleza _check_released(self, m, tp):
        check = self.assertRaisesRegex(ValueError, "released")
        ukijumuisha check: bytes(m)
        ukijumuisha check: m.tobytes()
        ukijumuisha check: m.tolist()
        ukijumuisha check: m[0]
        ukijumuisha check: m[0] = b'x'
        ukijumuisha check: len(m)
        ukijumuisha check: m.format
        ukijumuisha check: m.itemsize
        ukijumuisha check: m.ndim
        ukijumuisha check: m.readonly
        ukijumuisha check: m.shape
        ukijumuisha check: m.strides
        ukijumuisha check:
            ukijumuisha m:
                pass
        # str() na repr() still function
        self.assertIn("released memory", str(m))
        self.assertIn("released memory", repr(m))
        self.assertEqual(m, m)
        self.assertNotEqual(m, memoryview(tp(self._source)))
        self.assertNotEqual(m, tp(self._source))

    eleza test_contextmanager(self):
        kila tp kwenye self._types:
            b = tp(self._source)
            m = self._view(b)
            ukijumuisha m as cm:
                self.assertIs(cm, m)
            self._check_released(m, tp)
            m = self._view(b)
            # Can release explicitly inside the context manager
            ukijumuisha m:
                m.release()

    eleza test_release(self):
        kila tp kwenye self._types:
            b = tp(self._source)
            m = self._view(b)
            m.release()
            self._check_released(m, tp)
            # Can be called a second time (it's a no-op)
            m.release()
            self._check_released(m, tp)

    eleza test_writable_readonly(self):
        # Issue #10451: memoryview incorrectly exposes a readonly
        # buffer as writable causing a segfault ikiwa using mmap
        tp = self.ro_type
        ikiwa tp ni Tupu:
            self.skipTest("no read-only type to test")
        b = tp(self._source)
        m = self._view(b)
        i = io.BytesIO(b'ZZZZ')
        self.assertRaises(TypeError, i.readinto, m)

    eleza test_getbuf_fail(self):
        self.assertRaises(TypeError, self._view, {})

    eleza test_hash(self):
        # Memoryviews of readonly (hashable) types are hashable, na they
        # hash as hash(obj.tobytes()).
        tp = self.ro_type
        ikiwa tp ni Tupu:
            self.skipTest("no read-only type to test")
        b = tp(self._source)
        m = self._view(b)
        self.assertEqual(hash(m), hash(b"abcdef"))
        # Releasing the memoryview keeps the stored hash value (as ukijumuisha weakrefs)
        m.release()
        self.assertEqual(hash(m), hash(b"abcdef"))
        # Hashing a memoryview kila the first time after it ni released
        # results kwenye an error (as ukijumuisha weakrefs).
        m = self._view(b)
        m.release()
        self.assertRaises(ValueError, hash, m)

    eleza test_hash_writable(self):
        # Memoryviews of writable types are unhashable
        tp = self.rw_type
        ikiwa tp ni Tupu:
            self.skipTest("no writable type to test")
        b = tp(self._source)
        m = self._view(b)
        self.assertRaises(ValueError, hash, m)

    eleza test_weakref(self):
        # Check memoryviews are weakrefable
        kila tp kwenye self._types:
            b = tp(self._source)
            m = self._view(b)
            L = []
            eleza callback(wr, b=b):
                L.append(b)
            wr = weakref.ref(m, callback)
            self.assertIs(wr(), m)
            toa m
            test.support.gc_collect()
            self.assertIs(wr(), Tupu)
            self.assertIs(L[0], b)

    eleza test_reversed(self):
        kila tp kwenye self._types:
            b = tp(self._source)
            m = self._view(b)
            aslist = list(reversed(m.tolist()))
            self.assertEqual(list(reversed(m)), aslist)
            self.assertEqual(list(reversed(m)), list(m[::-1]))

    eleza test_toreadonly(self):
        kila tp kwenye self._types:
            b = tp(self._source)
            m = self._view(b)
            mm = m.toreadonly()
            self.assertKweli(mm.readonly)
            self.assertKweli(memoryview(mm).readonly)
            self.assertEqual(mm.tolist(), m.tolist())
            mm.release()
            m.tolist()

    eleza test_issue22668(self):
        a = array.array('H', [256, 256, 256, 256])
        x = memoryview(a)
        m = x.cast('B')
        b = m.cast('H')
        c = b[0:2]
        d = memoryview(b)

        toa b

        self.assertEqual(c[0], 256)
        self.assertEqual(d[0], 256)
        self.assertEqual(c.format, "H")
        self.assertEqual(d.format, "H")

        _ = m.cast('I')
        self.assertEqual(c[0], 256)
        self.assertEqual(d[0], 256)
        self.assertEqual(c.format, "H")
        self.assertEqual(d.format, "H")


# Variations on source objects kila the buffer: bytes-like objects, then arrays
# ukijumuisha itemsize > 1.
# NOTE: support kila multi-dimensional objects ni unimplemented.

kundi BaseBytesMemoryTests(AbstractMemoryTests):
    ro_type = bytes
    rw_type = bytearray
    getitem_type = bytes
    itemsize = 1
    format = 'B'

kundi BaseArrayMemoryTests(AbstractMemoryTests):
    ro_type = Tupu
    rw_type = lambda self, b: array.array('i', list(b))
    getitem_type = lambda self, b: array.array('i', list(b)).tobytes()
    itemsize = array.array('i').itemsize
    format = 'i'

    @unittest.skip('XXX test should be adapted kila non-byte buffers')
    eleza test_getbuffer(self):
        pass

    @unittest.skip('XXX NotImplementedError: tolist() only supports byte views')
    eleza test_tolist(self):
        pass


# Variations on indirection levels: memoryview, slice of memoryview,
# slice of slice of memoryview.
# This ni important to test allocation subtleties.

kundi BaseMemoryviewTests:
    eleza _view(self, obj):
        rudisha memoryview(obj)

    eleza _check_contents(self, tp, obj, contents):
        self.assertEqual(obj, tp(contents))

kundi BaseMemorySliceTests:
    source_bytes = b"XabcdefY"

    eleza _view(self, obj):
        m = memoryview(obj)
        rudisha m[1:7]

    eleza _check_contents(self, tp, obj, contents):
        self.assertEqual(obj[1:7], tp(contents))

    eleza test_refs(self):
        kila tp kwenye self._types:
            m = memoryview(tp(self._source))
            oldrefcount = sys.getrefcount(m)
            m[1:2]
            self.assertEqual(sys.getrefcount(m), oldrefcount)

kundi BaseMemorySliceSliceTests:
    source_bytes = b"XabcdefY"

    eleza _view(self, obj):
        m = memoryview(obj)
        rudisha m[:7][1:]

    eleza _check_contents(self, tp, obj, contents):
        self.assertEqual(obj[1:7], tp(contents))


# Concrete test classes

kundi BytesMemoryviewTest(unittest.TestCase,
    BaseMemoryviewTests, BaseBytesMemoryTests):

    eleza test_constructor(self):
        kila tp kwenye self._types:
            ob = tp(self._source)
            self.assertKweli(memoryview(ob))
            self.assertKweli(memoryview(object=ob))
            self.assertRaises(TypeError, memoryview)
            self.assertRaises(TypeError, memoryview, ob, ob)
            self.assertRaises(TypeError, memoryview, argument=ob)
            self.assertRaises(TypeError, memoryview, ob, argument=Kweli)

kundi ArrayMemoryviewTest(unittest.TestCase,
    BaseMemoryviewTests, BaseArrayMemoryTests):

    eleza test_array_assign(self):
        # Issue #4569: segfault when mutating a memoryview ukijumuisha itemsize != 1
        a = array.array('i', range(10))
        m = memoryview(a)
        new_a = array.array('i', range(9, -1, -1))
        m[:] = new_a
        self.assertEqual(a, new_a)


kundi BytesMemorySliceTest(unittest.TestCase,
    BaseMemorySliceTests, BaseBytesMemoryTests):
    pass

kundi ArrayMemorySliceTest(unittest.TestCase,
    BaseMemorySliceTests, BaseArrayMemoryTests):
    pass

kundi BytesMemorySliceSliceTest(unittest.TestCase,
    BaseMemorySliceSliceTests, BaseBytesMemoryTests):
    pass

kundi ArrayMemorySliceSliceTest(unittest.TestCase,
    BaseMemorySliceSliceTests, BaseArrayMemoryTests):
    pass


kundi OtherTest(unittest.TestCase):
    eleza test_ctypes_cast(self):
        # Issue 15944: Allow all source formats when casting to bytes.
        ctypes = test.support.import_module("ctypes")
        p6 = bytes(ctypes.c_double(0.6))

        d = ctypes.c_double()
        m = memoryview(d).cast("B")
        m[:2] = p6[:2]
        m[2:] = p6[2:]
        self.assertEqual(d.value, 0.6)

        kila format kwenye "Bbc":
            ukijumuisha self.subTest(format):
                d = ctypes.c_double()
                m = memoryview(d).cast(format)
                m[:2] = memoryview(p6).cast(format)[:2]
                m[2:] = memoryview(p6).cast(format)[2:]
                self.assertEqual(d.value, 0.6)

    eleza test_memoryview_hex(self):
        # Issue #9951: memoryview.hex() segfaults ukijumuisha non-contiguous buffers.
        x = b'0' * 200000
        m1 = memoryview(x)
        m2 = m1[::-1]
        self.assertEqual(m2.hex(), '30' * 200000)

    eleza test_copy(self):
        m = memoryview(b'abc')
        ukijumuisha self.assertRaises(TypeError):
            copy.copy(m)

    eleza test_pickle(self):
        m = memoryview(b'abc')
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.assertRaises(TypeError):
                pickle.dumps(m, proto)


ikiwa __name__ == "__main__":
    unittest.main()
