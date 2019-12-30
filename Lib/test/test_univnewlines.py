# Tests universal newline support kila both reading na parsing files.
agiza io
agiza _pyio as pyio
agiza unittest
agiza os
agiza sys
kutoka test agiza support

ikiwa sio hasattr(sys.stdin, 'newlines'):
     ashiria unittest.SkipTest(
        "This Python does sio have universal newline support")

FATX = 'x' * (2**14)

DATA_TEMPLATE = [
    "line1=1",
    "line2='this ni a very long line designed to go past any default " +
        "buffer limits that exist kwenye io.py but we also want to test " +
        "the uncommon case, naturally.'",
    "eleza line3():pass",
    "line4 = '%s'" % FATX,
    ]

DATA_LF = "\n".join(DATA_TEMPLATE) + "\n"
DATA_CR = "\r".join(DATA_TEMPLATE) + "\r"
DATA_CRLF = "\r\n".join(DATA_TEMPLATE) + "\r\n"

# Note that DATA_MIXED also tests the ability to recognize a lone \r
# before end-of-file.
DATA_MIXED = "\n".join(DATA_TEMPLATE) + "\r"
DATA_SPLIT = [x + "\n" kila x kwenye DATA_TEMPLATE]

kundi CTest:
    open = io.open

kundi PyTest:
    open = staticmethod(pyio.open)

kundi TestGenericUnivNewlines:
    # use a kundi variable DATA to define the data to write to the file
    # na a kundi variable NEWLINE to set the expected newlines value
    READMODE = 'r'
    WRITEMODE = 'wb'

    eleza setUp(self):
        data = self.DATA
        ikiwa "b" kwenye self.WRITEMODE:
            data = data.encode("ascii")
        ukijumuisha self.open(support.TESTFN, self.WRITEMODE) as fp:
            fp.write(data)

    eleza tearDown(self):
        jaribu:
            os.unlink(support.TESTFN)
        tatizo:
            pass

    eleza test_read(self):
        ukijumuisha self.open(support.TESTFN, self.READMODE) as fp:
            data = fp.read()
        self.assertEqual(data, DATA_LF)
        self.assertEqual(repr(fp.newlines), repr(self.NEWLINE))

    eleza test_readlines(self):
        ukijumuisha self.open(support.TESTFN, self.READMODE) as fp:
            data = fp.readlines()
        self.assertEqual(data, DATA_SPLIT)
        self.assertEqual(repr(fp.newlines), repr(self.NEWLINE))

    eleza test_readline(self):
        ukijumuisha self.open(support.TESTFN, self.READMODE) as fp:
            data = []
            d = fp.readline()
            wakati d:
                data.append(d)
                d = fp.readline()
        self.assertEqual(data, DATA_SPLIT)
        self.assertEqual(repr(fp.newlines), repr(self.NEWLINE))

    eleza test_seek(self):
        ukijumuisha self.open(support.TESTFN, self.READMODE) as fp:
            fp.readline()
            pos = fp.tell()
            data = fp.readlines()
            self.assertEqual(data, DATA_SPLIT[1:])
            fp.seek(pos)
            data = fp.readlines()
        self.assertEqual(data, DATA_SPLIT[1:])


kundi TestCRNewlines(TestGenericUnivNewlines):
    NEWLINE = '\r'
    DATA = DATA_CR
kundi CTestCRNewlines(CTest, TestCRNewlines, unittest.TestCase): pass
kundi PyTestCRNewlines(PyTest, TestCRNewlines, unittest.TestCase): pass

kundi TestLFNewlines(TestGenericUnivNewlines):
    NEWLINE = '\n'
    DATA = DATA_LF
kundi CTestLFNewlines(CTest, TestLFNewlines, unittest.TestCase): pass
kundi PyTestLFNewlines(PyTest, TestLFNewlines, unittest.TestCase): pass

kundi TestCRLFNewlines(TestGenericUnivNewlines):
    NEWLINE = '\r\n'
    DATA = DATA_CRLF

    eleza test_tell(self):
        ukijumuisha self.open(support.TESTFN, self.READMODE) as fp:
            self.assertEqual(repr(fp.newlines), repr(Tupu))
            data = fp.readline()
            pos = fp.tell()
        self.assertEqual(repr(fp.newlines), repr(self.NEWLINE))
kundi CTestCRLFNewlines(CTest, TestCRLFNewlines, unittest.TestCase): pass
kundi PyTestCRLFNewlines(PyTest, TestCRLFNewlines, unittest.TestCase): pass

kundi TestMixedNewlines(TestGenericUnivNewlines):
    NEWLINE = ('\r', '\n')
    DATA = DATA_MIXED
kundi CTestMixedNewlines(CTest, TestMixedNewlines, unittest.TestCase): pass
kundi PyTestMixedNewlines(PyTest, TestMixedNewlines, unittest.TestCase): pass

ikiwa __name__ == '__main__':
    unittest.main()
