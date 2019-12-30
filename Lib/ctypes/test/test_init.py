kutoka ctypes agiza *
agiza unittest

kundi X(Structure):
    _fields_ = [("a", c_int),
                ("b", c_int)]
    new_was_called = Uongo

    eleza __new__(cls):
        result = super().__new__(cls)
        result.new_was_called = Kweli
        rudisha result

    eleza __init__(self):
        self.a = 9
        self.b = 12

kundi Y(Structure):
    _fields_ = [("x", X)]


kundi InitTest(unittest.TestCase):
    eleza test_get(self):
        # make sure the only accessing a nested structure
        # doesn't call the structure's __new__ na __init__
        y = Y()
        self.assertEqual((y.x.a, y.x.b), (0, 0))
        self.assertEqual(y.x.new_was_called, Uongo)

        # But explicitly creating an X structure calls __new__ na __init__, of course.
        x = X()
        self.assertEqual((x.a, x.b), (9, 12))
        self.assertEqual(x.new_was_called, Kweli)

        y.x = x
        self.assertEqual((y.x.a, y.x.b), (9, 12))
        self.assertEqual(y.x.new_was_called, Uongo)

ikiwa __name__ == "__main__":
    unittest.main()
