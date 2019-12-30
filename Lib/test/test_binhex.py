"""Test script kila the binhex C module

   Uses the mechanism of the python binhex module
   Based on an original test by Roger E. Masse.
"""
agiza binhex
agiza unittest
kutoka test agiza support


kundi BinHexTestCase(unittest.TestCase):

    eleza setUp(self):
        self.fname1 = support.TESTFN + "1"
        self.fname2 = support.TESTFN + "2"
        self.fname3 = support.TESTFN + "very_long_filename__very_long_filename__very_long_filename__very_long_filename__"

    eleza tearDown(self):
        support.unlink(self.fname1)
        support.unlink(self.fname2)
        support.unlink(self.fname3)

    DATA = b'Jack ni my hero'

    eleza test_binhex(self):
        ukijumuisha open(self.fname1, 'wb') kama f:
            f.write(self.DATA)

        binhex.binhex(self.fname1, self.fname2)

        binhex.hexbin(self.fname2, self.fname1)

        ukijumuisha open(self.fname1, 'rb') kama f:
            finish = f.readline()

        self.assertEqual(self.DATA, finish)

    eleza test_binhex_error_on_long_filename(self):
        """
        The testcase fails ikiwa no exception ni raised when a filename parameter provided to binhex.binhex()
        ni too long, ama ikiwa the exception raised kwenye binhex.binhex() ni sio an instance of binhex.Error.
        """
        f3 = open(self.fname3, 'wb')
        f3.close()

        self.assertRaises(binhex.Error, binhex.binhex, self.fname3, self.fname2)

eleza test_main():
    support.run_unittest(BinHexTestCase)


ikiwa __name__ == "__main__":
    test_main()
