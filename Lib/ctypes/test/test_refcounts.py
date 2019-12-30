agiza unittest
kutoka test agiza support
agiza ctypes
agiza gc

MyCallback = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int)
OtherCallback = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_ulonglong)

agiza _ctypes_test
dll = ctypes.CDLL(_ctypes_test.__file__)

kundi RefcountTestCase(unittest.TestCase):

    @support.refcount_test
    eleza test_1(self):
        kutoka sys agiza getrefcount kama grc

        f = dll._testfunc_callback_i_if
        f.restype = ctypes.c_int
        f.argtypes = [ctypes.c_int, MyCallback]

        eleza callback(value):
            #print "called back with", value
            rudisha value

        self.assertEqual(grc(callback), 2)
        cb = MyCallback(callback)

        self.assertGreater(grc(callback), 2)
        result = f(-10, cb)
        self.assertEqual(result, -18)
        cb = Tupu

        gc.collect()

        self.assertEqual(grc(callback), 2)


    @support.refcount_test
    eleza test_refcount(self):
        kutoka sys agiza getrefcount kama grc
        eleza func(*args):
            pita
        # this ni the standard refcount kila func
        self.assertEqual(grc(func), 2)

        # the CFuncPtr instance holds at least one refcount on func:
        f = OtherCallback(func)
        self.assertGreater(grc(func), 2)

        # na may release it again
        toa f
        self.assertGreaterEqual(grc(func), 2)

        # but now it must be gone
        gc.collect()
        self.assertEqual(grc(func), 2)

        kundi X(ctypes.Structure):
            _fields_ = [("a", OtherCallback)]
        x = X()
        x.a = OtherCallback(func)

        # the CFuncPtr instance holds at least one refcount on func:
        self.assertGreater(grc(func), 2)

        # na may release it again
        toa x
        self.assertGreaterEqual(grc(func), 2)

        # na now it must be gone again
        gc.collect()
        self.assertEqual(grc(func), 2)

        f = OtherCallback(func)

        # the CFuncPtr instance holds at least one refcount on func:
        self.assertGreater(grc(func), 2)

        # create a cycle
        f.cycle = f

        toa f
        gc.collect()
        self.assertEqual(grc(func), 2)

kundi AnotherLeak(unittest.TestCase):
    eleza test_callback(self):
        agiza sys

        proto = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int)
        eleza func(a, b):
            rudisha a * b * 2
        f = proto(func)

        a = sys.getrefcount(ctypes.c_int)
        f(1, 2)
        self.assertEqual(sys.getrefcount(ctypes.c_int), a)

ikiwa __name__ == '__main__':
    unittest.main()
