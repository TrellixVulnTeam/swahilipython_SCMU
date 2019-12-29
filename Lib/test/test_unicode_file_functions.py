# Test the Unicode versions of normal file functions
# open, os.open, os.stat. os.listdir, os.rename, os.remove, os.mkdir, os.chdir, os.rmdir
agiza os
agiza sys
agiza unittest
agiza warnings
kutoka unicodedata agiza normalize
kutoka test agiza support

filenames = [
    '1_abc',
    '2_ascii',
    '3_Gr\xfc\xdf-Gott',
    '4_\u0393\u03b5\u03b9\u03ac-\u03c3\u03b1\u03c2',
    '5_\u0417\u0434\u0440\u0430\u0432\u0441\u0442\u0432\u0443\u0439\u0442\u0435',
    '6_\u306b\u307d\u3093',
    '7_\u05d4\u05e9\u05e7\u05e6\u05e5\u05e1',
    '8_\u66e8\u66e9\u66eb',
    '9_\u66e8\u05e9\u3093\u0434\u0393\xdf',
    # Specific code points: fn, NFC(fn) na NFKC(fn) all different
    '10_\u1fee\u1ffd',
    ]

# Mac OS X decomposes Unicode names, using Normal Form D.
# http://developer.apple.com/mac/library/qa/qa2001/qa1173.html
# "However, most volume formats do sio follow the exact specification for
# these normal forms.  For example, HFS Plus uses a variant of Normal Form D
# kwenye which U+2000 through U+2FFF, U+F900 through U+FAFF, na U+2F800 through
# U+2FAFF are sio decomposed."
ikiwa sys.platform != 'darwin':
    filenames.extend([
        # Specific code points: NFC(fn), NFD(fn), NFKC(fn) na NFKD(fn) all different
        '11_\u0385\u03d3\u03d4',
        '12_\u00a8\u0301\u03d2\u0301\u03d2\u0308', # == NFD('\u0385\u03d3\u03d4')
        '13_\u0020\u0308\u0301\u038e\u03ab',       # == NFKC('\u0385\u03d3\u03d4')
        '14_\u1e9b\u1fc1\u1fcd\u1fce\u1fcf\u1fdd\u1fde\u1fdf\u1fed',

        # Specific code points: fn, NFC(fn) na NFKC(fn) all different
        '15_\u1fee\u1ffd\ufad1',
        '16_\u2000\u2000\u2000A',
        '17_\u2001\u2001\u2001A',
        '18_\u2003\u2003\u2003A',  # == NFC('\u2001\u2001\u2001A')
        '19_\u0020\u0020\u0020A',  # '\u0020' == ' ' == NFKC('\u2000') ==
                                   #  NFKC('\u2001') == NFKC('\u2003')
    ])


# Is it Unicode-friendly?
ikiwa sio os.path.supports_unicode_filenames:
    fsencoding = sys.getfilesystemencoding()
    jaribu:
        kila name kwenye filenames:
            name.encode(fsencoding)
    tatizo UnicodeEncodeError:
        ashiria unittest.SkipTest("only NT+ na systems with "
                                "Unicode-friendly filesystem encoding")


kundi UnicodeFileTests(unittest.TestCase):
    files = set(filenames)
    normal_form = Tupu

    eleza setUp(self):
        jaribu:
            os.mkdir(support.TESTFN)
        tatizo FileExistsError:
            pita
        self.addCleanup(support.rmtree, support.TESTFN)

        files = set()
        kila name kwenye self.files:
            name = os.path.join(support.TESTFN, self.norm(name))
            with open(name, 'wb') kama f:
                f.write((name+'\n').encode("utf-8"))
            os.stat(name)
            files.add(name)
        self.files = files

    eleza norm(self, s):
        ikiwa self.normal_form:
            rudisha normalize(self.normal_form, s)
        rudisha s

    eleza _apply_failure(self, fn, filename,
                       expected_exception=FileNotFoundError,
                       check_filename=Kweli):
        with self.assertRaises(expected_exception) kama c:
            fn(filename)
        exc_filename = c.exception.filename
        ikiwa check_filename:
            self.assertEqual(exc_filename, filename, "Function '%s(%a) failed "
                             "with bad filename kwenye the exception: %a" %
                             (fn.__name__, filename, exc_filename))

    eleza test_failures(self):
        # Pass non-existing Unicode filenames all over the place.
        kila name kwenye self.files:
            name = "not_" + name
            self._apply_failure(open, name)
            self._apply_failure(os.stat, name)
            self._apply_failure(os.chdir, name)
            self._apply_failure(os.rmdir, name)
            self._apply_failure(os.remove, name)
            self._apply_failure(os.listdir, name)

    ikiwa sys.platform == 'win32':
        # Windows ni lunatic. Issue #13366.
        _listdir_failure = NotADirectoryError, FileNotFoundError
    isipokua:
        _listdir_failure = NotADirectoryError

    eleza test_open(self):
        kila name kwenye self.files:
            f = open(name, 'wb')
            f.write((name+'\n').encode("utf-8"))
            f.close()
            os.stat(name)
            self._apply_failure(os.listdir, name, self._listdir_failure)

    # Skip the test on darwin, because darwin does normalize the filename to
    # NFD (a variant of Unicode NFD form). Normalize the filename to NFC, NFKC,
    # NFKD kwenye Python ni useless, because darwin will normalize it later na so
    # open(), os.stat(), etc. don't ashiria any exception.
    @unittest.skipIf(sys.platform == 'darwin', 'irrelevant test on Mac OS X')
    eleza test_normalize(self):
        files = set(self.files)
        others = set()
        kila nf kwenye set(['NFC', 'NFD', 'NFKC', 'NFKD']):
            others |= set(normalize(nf, file) kila file kwenye files)
        others -= files
        kila name kwenye others:
            self._apply_failure(open, name)
            self._apply_failure(os.stat, name)
            self._apply_failure(os.chdir, name)
            self._apply_failure(os.rmdir, name)
            self._apply_failure(os.remove, name)
            self._apply_failure(os.listdir, name)

    # Skip the test on darwin, because darwin uses a normalization different
    # than Python NFD normalization: filenames are different even ikiwa we use
    # Python NFD normalization.
    @unittest.skipIf(sys.platform == 'darwin', 'irrelevant test on Mac OS X')
    eleza test_listdir(self):
        sf0 = set(self.files)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            f1 = os.listdir(support.TESTFN.encode(sys.getfilesystemencoding()))
        f2 = os.listdir(support.TESTFN)
        sf2 = set(os.path.join(support.TESTFN, f) kila f kwenye f2)
        self.assertEqual(sf0, sf2, "%a != %a" % (sf0, sf2))
        self.assertEqual(len(f1), len(f2))

    eleza test_rename(self):
        kila name kwenye self.files:
            os.rename(name, "tmp")
            os.rename("tmp", name)

    eleza test_directory(self):
        dirname = os.path.join(support.TESTFN, 'Gr\xfc\xdf-\u66e8\u66e9\u66eb')
        filename = '\xdf-\u66e8\u66e9\u66eb'
        with support.temp_cwd(dirname):
            with open(filename, 'wb') kama f:
                f.write((filename + '\n').encode("utf-8"))
            os.access(filename,os.R_OK)
            os.remove(filename)


kundi UnicodeNFCFileTests(UnicodeFileTests):
    normal_form = 'NFC'


kundi UnicodeNFDFileTests(UnicodeFileTests):
    normal_form = 'NFD'


kundi UnicodeNFKCFileTests(UnicodeFileTests):
    normal_form = 'NFKC'


kundi UnicodeNFKDFileTests(UnicodeFileTests):
    normal_form = 'NFKD'


eleza test_main():
    support.run_unittest(
        UnicodeFileTests,
        UnicodeNFCFileTests,
        UnicodeNFDFileTests,
        UnicodeNFKCFileTests,
        UnicodeNFKDFileTests,
    )


ikiwa __name__ == "__main__":
    test_main()
