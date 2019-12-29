agiza unittest
kutoka test agiza support

agiza io # C implementation.
agiza _pyio kama pyio # Python implementation.

# Simple test to ensure that optimizations kwenye the IO library deliver the
# expected results.  For best testing, run this under a debug-build Python too
# (to exercise asserts kwenye the C code).

lengths = list(range(1, 257)) + [512, 1000, 1024, 2048, 4096, 8192, 10000,
                                 16384, 32768, 65536, 1000000]

kundi BufferSizeTest:
    eleza try_one(self, s):
        # Write s + "\n" + s to file, then open it na ensure that successive
        # .readline()s deliver what we wrote.

        # Ensure we can open TESTFN kila writing.
        support.unlink(support.TESTFN)

        # Since C doesn't guarantee we can write/read arbitrary bytes kwenye text
        # files, use binary mode.
        f = self.open(support.TESTFN, "wb")
        jaribu:
            # write once ukijumuisha \n na once without
            f.write(s)
            f.write(b"\n")
            f.write(s)
            f.close()
            f = open(support.TESTFN, "rb")
            line = f.readline()
            self.assertEqual(line, s + b"\n")
            line = f.readline()
            self.assertEqual(line, s)
            line = f.readline()
            self.assertUongo(line) # Must be at EOF
            f.close()
        mwishowe:
            support.unlink(support.TESTFN)

    eleza drive_one(self, pattern):
        kila length kwenye lengths:
            # Repeat string 'pattern' kama often kama needed to reach total length
            # 'length'.  Then call try_one ukijumuisha that string, a string one larger
            # than that, na a string one smaller than that.  Try this ukijumuisha all
            # small sizes na various powers of 2, so we exercise all likely
            # stdio buffer sizes, na "off by one" errors on both sides.
            q, r = divmod(length, len(pattern))
            teststring = pattern * q + pattern[:r]
            self.assertEqual(len(teststring), length)
            self.try_one(teststring)
            self.try_one(teststring + b"x")
            self.try_one(teststring[:-1])

    eleza test_primepat(self):
        # A pattern ukijumuisha prime length, to avoid simple relationships with
        # stdio buffer sizes.
        self.drive_one(b"1234567890\00\01\02\03\04\05\06")

    eleza test_nullpat(self):
        self.drive_one(b'\0' * 1000)


kundi CBufferSizeTest(BufferSizeTest, unittest.TestCase):
    open = io.open

kundi PyBufferSizeTest(BufferSizeTest, unittest.TestCase):
    open = staticmethod(pyio.open)


ikiwa __name__ == "__main__":
    unittest.main()
