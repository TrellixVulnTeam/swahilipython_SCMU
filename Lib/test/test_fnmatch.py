"""Test cases kila the fnmatch module."""

agiza unittest
agiza os
agiza warnings

kutoka fnmatch agiza fnmatch, fnmatchcase, translate, filter

kundi FnmatchTestCase(unittest.TestCase):

    eleza check_match(self, filename, pattern, should_match=Kweli, fn=fnmatch):
        ikiwa should_match:
            self.assertKweli(fn(filename, pattern),
                         "expected %r to match pattern %r"
                         % (filename, pattern))
        isipokua:
            self.assertUongo(fn(filename, pattern),
                         "expected %r sio to match pattern %r"
                         % (filename, pattern))

    eleza test_fnmatch(self):
        check = self.check_match
        check('abc', 'abc')
        check('abc', '?*?')
        check('abc', '???*')
        check('abc', '*???')
        check('abc', '???')
        check('abc', '*')
        check('abc', 'ab[cd]')
        check('abc', 'ab[!de]')
        check('abc', 'ab[de]', Uongo)
        check('a', '??', Uongo)
        check('a', 'b', Uongo)

        # these test that '\' ni handled correctly kwenye character sets;
        # see SF bug #409651
        check('\\', r'[\]')
        check('a', r'[!\]')
        check('\\', r'[!\]', Uongo)

        # test that filenames with newlines kwenye them are handled correctly.
        # http://bugs.python.org/issue6665
        check('foo\nbar', 'foo*')
        check('foo\nbar\n', 'foo*')
        check('\nfoo', 'foo*', Uongo)
        check('\n', '*')

    eleza test_mix_bytes_str(self):
        self.assertRaises(TypeError, fnmatch, 'test', b'*')
        self.assertRaises(TypeError, fnmatch, b'test', '*')
        self.assertRaises(TypeError, fnmatchcase, 'test', b'*')
        self.assertRaises(TypeError, fnmatchcase, b'test', '*')

    eleza test_fnmatchcase(self):
        check = self.check_match
        check('abc', 'abc', Kweli, fnmatchcase)
        check('AbC', 'abc', Uongo, fnmatchcase)
        check('abc', 'AbC', Uongo, fnmatchcase)
        check('AbC', 'AbC', Kweli, fnmatchcase)

        check('usr/bin', 'usr/bin', Kweli, fnmatchcase)
        check('usr\\bin', 'usr/bin', Uongo, fnmatchcase)
        check('usr/bin', 'usr\\bin', Uongo, fnmatchcase)
        check('usr\\bin', 'usr\\bin', Kweli, fnmatchcase)

    eleza test_bytes(self):
        self.check_match(b'test', b'te*')
        self.check_match(b'test\xff', b'te*\xff')
        self.check_match(b'foo\nbar', b'foo*')

    eleza test_case(self):
        ignorecase = os.path.normcase('ABC') == os.path.normcase('abc')
        check = self.check_match
        check('abc', 'abc')
        check('AbC', 'abc', ignorecase)
        check('abc', 'AbC', ignorecase)
        check('AbC', 'AbC')

    eleza test_sep(self):
        normsep = os.path.normcase('\\') == os.path.normcase('/')
        check = self.check_match
        check('usr/bin', 'usr/bin')
        check('usr\\bin', 'usr/bin', normsep)
        check('usr/bin', 'usr\\bin', normsep)
        check('usr\\bin', 'usr\\bin')

    eleza test_warnings(self):
        with warnings.catch_warnings():
            warnings.simplefilter('error', Warning)
            check = self.check_match
            check('[', '[[]')
            check('&', '[a&&b]')
            check('|', '[a||b]')
            check('~', '[a~~b]')
            check(',', '[a-z+--A-Z]')
            check('.', '[a-z--/A-Z]')


kundi TranslateTestCase(unittest.TestCase):

    eleza test_translate(self):
        self.assertEqual(translate('*'), r'(?s:.*)\Z')
        self.assertEqual(translate('?'), r'(?s:.)\Z')
        self.assertEqual(translate('a?b*'), r'(?s:a.b.*)\Z')
        self.assertEqual(translate('[abc]'), r'(?s:[abc])\Z')
        self.assertEqual(translate('[]]'), r'(?s:[]])\Z')
        self.assertEqual(translate('[!x]'), r'(?s:[^x])\Z')
        self.assertEqual(translate('[^x]'), r'(?s:[\^x])\Z')
        self.assertEqual(translate('[x'), r'(?s:\[x)\Z')


kundi FilterTestCase(unittest.TestCase):

    eleza test_filter(self):
        self.assertEqual(filter(['Python', 'Ruby', 'Perl', 'Tcl'], 'P*'),
                         ['Python', 'Perl'])
        self.assertEqual(filter([b'Python', b'Ruby', b'Perl', b'Tcl'], b'P*'),
                         [b'Python', b'Perl'])

    eleza test_mix_bytes_str(self):
        self.assertRaises(TypeError, filter, ['test'], b'*')
        self.assertRaises(TypeError, filter, [b'test'], '*')

    eleza test_case(self):
        ignorecase = os.path.normcase('P') == os.path.normcase('p')
        self.assertEqual(filter(['Test.py', 'Test.rb', 'Test.PL'], '*.p*'),
                         ['Test.py', 'Test.PL'] ikiwa ignorecase else ['Test.py'])
        self.assertEqual(filter(['Test.py', 'Test.rb', 'Test.PL'], '*.P*'),
                         ['Test.py', 'Test.PL'] ikiwa ignorecase else ['Test.PL'])

    eleza test_sep(self):
        normsep = os.path.normcase('\\') == os.path.normcase('/')
        self.assertEqual(filter(['usr/bin', 'usr', 'usr\\lib'], 'usr/*'),
                         ['usr/bin', 'usr\\lib'] ikiwa normsep else ['usr/bin'])
        self.assertEqual(filter(['usr/bin', 'usr', 'usr\\lib'], 'usr\\*'),
                         ['usr/bin', 'usr\\lib'] ikiwa normsep else ['usr\\lib'])


ikiwa __name__ == "__main__":
    unittest.main()
