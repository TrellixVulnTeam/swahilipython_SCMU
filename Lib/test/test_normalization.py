kutoka test.support agiza open_urlresource
agiza unittest

kutoka http.client agiza HTTPException
agiza sys
kutoka unicodedata agiza normalize, is_normalized, unidata_version

TESTDATAFILE = "NormalizationTest.txt"
TESTDATAURL = "http://www.pythontest.net/unicode/" + unidata_version + "/" + TESTDATAFILE

eleza check_version(testfile):
    hdr = testfile.readline()
    rudisha unidata_version kwenye hdr

kundi RangeError(Exception):
    pita

eleza NFC(str):
    rudisha normalize("NFC", str)

eleza NFKC(str):
    rudisha normalize("NFKC", str)

eleza NFD(str):
    rudisha normalize("NFD", str)

eleza NFKD(str):
    rudisha normalize("NFKD", str)

eleza unistr(data):
    data = [int(x, 16) kila x kwenye data.split(" ")]
    kila x kwenye data:
        ikiwa x > sys.maxunicode:
            ashiria RangeError
    rudisha "".join([chr(x) kila x kwenye data])

kundi NormalizationTest(unittest.TestCase):
    eleza test_main(self):
        # Hit the exception early
        jaribu:
            testdata = open_urlresource(TESTDATAURL, encoding="utf-8",
                                        check=check_version)
        tatizo PermissionError:
            self.skipTest(f"Permission error when downloading {TESTDATAURL} "
                          f"into the test data directory")
        tatizo (OSError, HTTPException):
            self.fail(f"Could sio retrieve {TESTDATAURL}")

        with testdata:
            self.run_normalization_tests(testdata)

    eleza run_normalization_tests(self, testdata):
        part = Tupu
        part1_data = {}

        kila line kwenye testdata:
            ikiwa '#' kwenye line:
                line = line.split('#')[0]
            line = line.strip()
            ikiwa sio line:
                endelea
            ikiwa line.startswith("@Part"):
                part = line.split()[0]
                endelea
            jaribu:
                c1,c2,c3,c4,c5 = [unistr(x) kila x kwenye line.split(';')[:-1]]
            tatizo RangeError:
                # Skip unsupported characters;
                # try at least adding c1 ikiwa we are kwenye part1
                ikiwa part == "@Part1":
                    jaribu:
                        c1 = unistr(line.split(';')[0])
                    tatizo RangeError:
                        pita
                    isipokua:
                        part1_data[c1] = 1
                endelea

            # Perform tests
            self.assertKweli(c2 ==  NFC(c1) ==  NFC(c2) ==  NFC(c3), line)
            self.assertKweli(c4 ==  NFC(c4) ==  NFC(c5), line)
            self.assertKweli(c3 ==  NFD(c1) ==  NFD(c2) ==  NFD(c3), line)
            self.assertKweli(c5 ==  NFD(c4) ==  NFD(c5), line)
            self.assertKweli(c4 == NFKC(c1) == NFKC(c2) == \
                            NFKC(c3) == NFKC(c4) == NFKC(c5),
                            line)
            self.assertKweli(c5 == NFKD(c1) == NFKD(c2) == \
                            NFKD(c3) == NFKD(c4) == NFKD(c5),
                            line)

            self.assertKweli(is_normalized("NFC", c2))
            self.assertKweli(is_normalized("NFC", c4))

            self.assertKweli(is_normalized("NFD", c3))
            self.assertKweli(is_normalized("NFD", c5))

            self.assertKweli(is_normalized("NFKC", c4))
            self.assertKweli(is_normalized("NFKD", c5))

            # Record part 1 data
            ikiwa part == "@Part1":
                part1_data[c1] = 1

        # Perform tests kila all other data
        kila c kwenye range(sys.maxunicode+1):
            X = chr(c)
            ikiwa X kwenye part1_data:
                endelea
            self.assertKweli(X == NFC(X) == NFD(X) == NFKC(X) == NFKD(X), c)

    eleza test_bug_834676(self):
        # Check kila bug 834676
        normalize('NFC', '\ud55c\uae00')


ikiwa __name__ == "__main__":
    unittest.main()
