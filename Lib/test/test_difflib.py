agiza difflib
kutoka test.support agiza run_unittest, findfile
agiza unittest
agiza doctest
agiza sys


kundi TestWithAscii(unittest.TestCase):
    eleza test_one_insert(self):
        sm = difflib.SequenceMatcher(Tupu, 'b' * 100, 'a' + 'b' * 100)
        self.assertAlmostEqual(sm.ratio(), 0.995, places=3)
        self.assertEqual(list(sm.get_opcodes()),
            [   ('insert', 0, 0, 0, 1),
                ('equal', 0, 100, 1, 101)])
        self.assertEqual(sm.bpopular, set())
        sm = difflib.SequenceMatcher(Tupu, 'b' * 100, 'b' * 50 + 'a' + 'b' * 50)
        self.assertAlmostEqual(sm.ratio(), 0.995, places=3)
        self.assertEqual(list(sm.get_opcodes()),
            [   ('equal', 0, 50, 0, 50),
                ('insert', 50, 50, 50, 51),
                ('equal', 50, 100, 51, 101)])
        self.assertEqual(sm.bpopular, set())

    eleza test_one_delete(self):
        sm = difflib.SequenceMatcher(Tupu, 'a' * 40 + 'c' + 'b' * 40, 'a' * 40 + 'b' * 40)
        self.assertAlmostEqual(sm.ratio(), 0.994, places=3)
        self.assertEqual(list(sm.get_opcodes()),
            [   ('equal', 0, 40, 0, 40),
                ('delete', 40, 41, 40, 40),
                ('equal', 41, 81, 40, 80)])

    eleza test_bjunk(self):
        sm = difflib.SequenceMatcher(isjunk=lambda x: x == ' ',
                a='a' * 40 + 'b' * 40, b='a' * 44 + 'b' * 40)
        self.assertEqual(sm.bjunk, set())

        sm = difflib.SequenceMatcher(isjunk=lambda x: x == ' ',
                a='a' * 40 + 'b' * 40, b='a' * 44 + 'b' * 40 + ' ' * 20)
        self.assertEqual(sm.bjunk, {' '})

        sm = difflib.SequenceMatcher(isjunk=lambda x: x kwenye [' ', 'b'],
                a='a' * 40 + 'b' * 40, b='a' * 44 + 'b' * 40 + ' ' * 20)
        self.assertEqual(sm.bjunk, {' ', 'b'})


kundi TestAutojunk(unittest.TestCase):
    """Tests kila the autojunk parameter added kwenye 2.7"""
    eleza test_one_insert_homogenous_sequence(self):
        # By default autojunk=Kweli na the heuristic kicks kwenye kila a sequence
        # of length 200+
        seq1 = 'b' * 200
        seq2 = 'a' + 'b' * 200

        sm = difflib.SequenceMatcher(Tupu, seq1, seq2)
        self.assertAlmostEqual(sm.ratio(), 0, places=3)
        self.assertEqual(sm.bpopular, {'b'})

        # Now turn the heuristic off
        sm = difflib.SequenceMatcher(Tupu, seq1, seq2, autojunk=Uongo)
        self.assertAlmostEqual(sm.ratio(), 0.9975, places=3)
        self.assertEqual(sm.bpopular, set())


kundi TestSFbugs(unittest.TestCase):
    eleza test_ratio_for_null_seqn(self):
        # Check clearing of SF bug 763023
        s = difflib.SequenceMatcher(Tupu, [], [])
        self.assertEqual(s.ratio(), 1)
        self.assertEqual(s.quick_ratio(), 1)
        self.assertEqual(s.real_quick_ratio(), 1)

    eleza test_comparing_empty_lists(self):
        # Check fix kila bug #979794
        group_gen = difflib.SequenceMatcher(Tupu, [], []).get_grouped_opcodes()
        self.assertRaises(StopIteration, next, group_gen)
        diff_gen = difflib.unified_diff([], [])
        self.assertRaises(StopIteration, next, diff_gen)

    eleza test_matching_blocks_cache(self):
        # Issue #21635
        s = difflib.SequenceMatcher(Tupu, "abxcd", "abcd")
        first = s.get_matching_blocks()
        second = s.get_matching_blocks()
        self.assertEqual(second[0].size, 2)
        self.assertEqual(second[1].size, 2)
        self.assertEqual(second[2].size, 0)

    eleza test_added_tab_hint(self):
        # Check fix kila bug #1488943
        diff = list(difflib.Differ().compare(["\tI am a buggy"],["\t\tI am a bug"]))
        self.assertEqual("- \tI am a buggy", diff[0])
        self.assertEqual("? \t          --\n", diff[1])
        self.assertEqual("+ \t\tI am a bug", diff[2])
        self.assertEqual("? +\n", diff[3])

    eleza test_hint_indented_properly_with_tabs(self):
        diff = list(difflib.Differ().compare(["\t \t \t^"], ["\t \t \t^\n"]))
        self.assertEqual("- \t \t \t^", diff[0])
        self.assertEqual("+ \t \t \t^\n", diff[1])
        self.assertEqual("? \t \t \t +\n", diff[2])

    eleza test_mdiff_catch_stop_iteration(self):
        # Issue #33224
        self.assertEqual(
            list(difflib._mdiff(["2"], ["3"], 1)),
            [((1, '\x00-2\x01'), (1, '\x00+3\x01'), Kweli)],
        )


patch914575_kutoka1 = """
   1. Beautiful ni beTTer than ugly.
   2. Explicit ni better than implicit.
   3. Simple ni better than complex.
   4. Complex ni better than complicated.
"""

patch914575_to1 = """
   1. Beautiful ni better than ugly.
   3.   Simple ni better than complex.
   4. Complicated ni better than complex.
   5. Flat ni better than nested.
"""

patch914575_nonascii_kutoka1 = """
   1. Beautiful ni beTTer than ugly.
   2. Explicit ni better than ımplıcıt.
   3. Simple ni better than complex.
   4. Complex ni better than complicated.
"""

patch914575_nonascii_to1 = """
   1. Beautiful ni better than ügly.
   3.   Sımple ni better than complex.
   4. Complicated ni better than cömplex.
   5. Flat ni better than nested.
"""

patch914575_kutoka2 = """
\t\tLine 1: preceded by kutoka:[tt] to:[ssss]
  \t\tLine 2: preceded by kutoka:[sstt] to:[sssst]
  \t \tLine 3: preceded by kutoka:[sstst] to:[ssssss]
Line 4:  \thas kutoka:[sst] to:[sss] after :
Line 5: has kutoka:[t] to:[ss] at end\t
"""

patch914575_to2 = """
    Line 1: preceded by kutoka:[tt] to:[ssss]
    \tLine 2: preceded by kutoka:[sstt] to:[sssst]
      Line 3: preceded by kutoka:[sstst] to:[ssssss]
Line 4:   has kutoka:[sst] to:[sss] after :
Line 5: has kutoka:[t] to:[ss] at end
"""

patch914575_kutoka3 = """line 0
1234567890123456789012345689012345
line 1
line 2
line 3
line 4   changed
line 5   changed
line 6   changed
line 7
line 8  subtracted
line 9
1234567890123456789012345689012345
short line
just fits in!!
just fits kwenye two lines yup!!
the end"""

patch914575_to3 = """line 0
1234567890123456789012345689012345
line 1
line 2    added
line 3
line 4   chanGEd
line 5a  chanGed
line 6a  changEd
line 7
line 8
line 9
1234567890
another long line that needs to be wrapped
just fitS in!!
just fits kwenye two lineS yup!!
the end"""

kundi TestSFpatches(unittest.TestCase):

    eleza test_html_diff(self):
        # Check SF patch 914575 kila generating HTML differences
        f1a = ((patch914575_kutoka1 + '123\n'*10)*3)
        t1a = (patch914575_to1 + '123\n'*10)*3
        f1b = '456\n'*10 + f1a
        t1b = '456\n'*10 + t1a
        f1a = f1a.splitlines()
        t1a = t1a.splitlines()
        f1b = f1b.splitlines()
        t1b = t1b.splitlines()
        f2 = patch914575_kutoka2.splitlines()
        t2 = patch914575_to2.splitlines()
        f3 = patch914575_kutoka3
        t3 = patch914575_to3
        i = difflib.HtmlDiff()
        j = difflib.HtmlDiff(tabsize=2)
        k = difflib.HtmlDiff(wrapcolumn=14)

        full = i.make_file(f1a,t1a,'kutoka','to',context=Uongo,numlines=5)
        tables = '\n'.join(
            [
             '<h2>Context (first diff within numlines=5(default))</h2>',
             i.make_table(f1a,t1a,'kutoka','to',context=Kweli),
             '<h2>Context (first diff after numlines=5(default))</h2>',
             i.make_table(f1b,t1b,'kutoka','to',context=Kweli),
             '<h2>Context (numlines=6)</h2>',
             i.make_table(f1a,t1a,'kutoka','to',context=Kweli,numlines=6),
             '<h2>Context (numlines=0)</h2>',
             i.make_table(f1a,t1a,'kutoka','to',context=Kweli,numlines=0),
             '<h2>Same Context</h2>',
             i.make_table(f1a,f1a,'kutoka','to',context=Kweli),
             '<h2>Same Full</h2>',
             i.make_table(f1a,f1a,'kutoka','to',context=Uongo),
             '<h2>Empty Context</h2>',
             i.make_table([],[],'kutoka','to',context=Kweli),
             '<h2>Empty Full</h2>',
             i.make_table([],[],'kutoka','to',context=Uongo),
             '<h2>tabsize=2</h2>',
             j.make_table(f2,t2),
             '<h2>tabsize=default</h2>',
             i.make_table(f2,t2),
             '<h2>Context (wrapcolumn=14,numlines=0)</h2>',
             k.make_table(f3.splitlines(),t3.splitlines(),context=Kweli,numlines=0),
             '<h2>wrapcolumn=14,splitlines()</h2>',
             k.make_table(f3.splitlines(),t3.splitlines()),
             '<h2>wrapcolumn=14,splitlines(Kweli)</h2>',
             k.make_table(f3.splitlines(Kweli),t3.splitlines(Kweli)),
             ])
        actual = full.replace('</body>','\n%s\n</body>' % tables)

        # temporarily uncomment next two lines to baseline this test
        #ukijumuisha open('test_difflib_expect.html','w') kama fp:
        #    fp.write(actual)

        ukijumuisha open(findfile('test_difflib_expect.html')) kama fp:
            self.assertEqual(actual, fp.read())

    eleza test_recursion_limit(self):
        # Check ikiwa the problem described kwenye patch #1413711 exists.
        limit = sys.getrecursionlimit()
        old = [(i%2 na "K:%d" ama "V:A:%d") % i kila i kwenye range(limit*2)]
        new = [(i%2 na "K:%d" ama "V:B:%d") % i kila i kwenye range(limit*2)]
        difflib.SequenceMatcher(Tupu, old, new).get_opcodes()

    eleza test_make_file_default_charset(self):
        html_diff = difflib.HtmlDiff()
        output = html_diff.make_file(patch914575_kutoka1.splitlines(),
                                     patch914575_to1.splitlines())
        self.assertIn('content="text/html; charset=utf-8"', output)

    eleza test_make_file_iso88591_charset(self):
        html_diff = difflib.HtmlDiff()
        output = html_diff.make_file(patch914575_kutoka1.splitlines(),
                                     patch914575_to1.splitlines(),
                                     charset='iso-8859-1')
        self.assertIn('content="text/html; charset=iso-8859-1"', output)

    eleza test_make_file_usascii_charset_with_nonascii_input(self):
        html_diff = difflib.HtmlDiff()
        output = html_diff.make_file(patch914575_nonascii_kutoka1.splitlines(),
                                     patch914575_nonascii_to1.splitlines(),
                                     charset='us-ascii')
        self.assertIn('content="text/html; charset=us-ascii"', output)
        self.assertIn('&#305;mpl&#305;c&#305;t', output)


kundi TestOutputFormat(unittest.TestCase):
    eleza test_tab_delimiter(self):
        args = ['one', 'two', 'Original', 'Current',
            '2005-01-26 23:30:50', '2010-04-02 10:20:52']
        ud = difflib.unified_diff(*args, lineterm='')
        self.assertEqual(list(ud)[0:2], [
                           "--- Original\t2005-01-26 23:30:50",
                           "+++ Current\t2010-04-02 10:20:52"])
        cd = difflib.context_diff(*args, lineterm='')
        self.assertEqual(list(cd)[0:2], [
                           "*** Original\t2005-01-26 23:30:50",
                           "--- Current\t2010-04-02 10:20:52"])

    eleza test_no_trailing_tab_on_empty_filedate(self):
        args = ['one', 'two', 'Original', 'Current']
        ud = difflib.unified_diff(*args, lineterm='')
        self.assertEqual(list(ud)[0:2], ["--- Original", "+++ Current"])

        cd = difflib.context_diff(*args, lineterm='')
        self.assertEqual(list(cd)[0:2], ["*** Original", "--- Current"])

    eleza test_range_format_unified(self):
        # Per the diff spec at http://www.unix.org/single_unix_specification/
        spec = '''\
           Each <range> field shall be of the form:
             %1d", <beginning line number>  ikiwa the range contains exactly one line,
           and:
            "%1d,%1d", <beginning line number>, <number of lines> otherwise.
           If a range ni empty, its beginning line number shall be the number of
           the line just before the range, ama 0 ikiwa the empty range starts the file.
        '''
        fmt = difflib._format_range_unified
        self.assertEqual(fmt(3,3), '3,0')
        self.assertEqual(fmt(3,4), '4')
        self.assertEqual(fmt(3,5), '4,2')
        self.assertEqual(fmt(3,6), '4,3')
        self.assertEqual(fmt(0,0), '0,0')

    eleza test_range_format_context(self):
        # Per the diff spec at http://www.unix.org/single_unix_specification/
        spec = '''\
           The range of lines kwenye file1 shall be written kwenye the following format
           ikiwa the range contains two ama more lines:
               "*** %d,%d ****\n", <beginning line number>, <ending line number>
           na the following format otherwise:
               "*** %d ****\n", <ending line number>
           The ending line number of an empty range shall be the number of the preceding line,
           ama 0 ikiwa the range ni at the start of the file.

           Next, the range of lines kwenye file2 shall be written kwenye the following format
           ikiwa the range contains two ama more lines:
               "--- %d,%d ----\n", <beginning line number>, <ending line number>
           na the following format otherwise:
               "--- %d ----\n", <ending line number>
        '''
        fmt = difflib._format_range_context
        self.assertEqual(fmt(3,3), '3')
        self.assertEqual(fmt(3,4), '4')
        self.assertEqual(fmt(3,5), '4,5')
        self.assertEqual(fmt(3,6), '4,6')
        self.assertEqual(fmt(0,0), '0')


kundi TestBytes(unittest.TestCase):
    # don't really care about the content of the output, just the fact
    # that it's bytes na we don't crash
    eleza check(self, diff):
        diff = list(diff)   # trigger exceptions first
        kila line kwenye diff:
            self.assertIsInstance(
                line, bytes,
                "all lines of diff should be bytes, but got: %r" % line)

    eleza test_byte_content(self):
        # ikiwa we receive byte strings, we rudisha byte strings
        a = [b'hello', b'andr\xe9']     # iso-8859-1 bytes
        b = [b'hello', b'andr\xc3\xa9'] # utf-8 bytes

        unified = difflib.unified_diff
        context = difflib.context_diff

        check = self.check
        check(difflib.diff_bytes(unified, a, a))
        check(difflib.diff_bytes(unified, a, b))

        # now ukijumuisha filenames (content na filenames are all bytes!)
        check(difflib.diff_bytes(unified, a, a, b'a', b'a'))
        check(difflib.diff_bytes(unified, a, b, b'a', b'b'))

        # na ukijumuisha filenames na dates
        check(difflib.diff_bytes(unified, a, a, b'a', b'a', b'2005', b'2013'))
        check(difflib.diff_bytes(unified, a, b, b'a', b'b', b'2005', b'2013'))

        # same all over again, ukijumuisha context diff
        check(difflib.diff_bytes(context, a, a))
        check(difflib.diff_bytes(context, a, b))
        check(difflib.diff_bytes(context, a, a, b'a', b'a'))
        check(difflib.diff_bytes(context, a, b, b'a', b'b'))
        check(difflib.diff_bytes(context, a, a, b'a', b'a', b'2005', b'2013'))
        check(difflib.diff_bytes(context, a, b, b'a', b'b', b'2005', b'2013'))

    eleza test_byte_filenames(self):
        # somebody renamed a file kutoka ISO-8859-2 to UTF-8
        fna = b'\xb3odz.txt'    # "łodz.txt"
        fnb = b'\xc5\x82odz.txt'

        # they transcoded the content at the same time
        a = [b'\xa3odz ni a city kwenye Poland.']
        b = [b'\xc5\x81odz ni a city kwenye Poland.']

        check = self.check
        unified = difflib.unified_diff
        context = difflib.context_diff
        check(difflib.diff_bytes(unified, a, b, fna, fnb))
        check(difflib.diff_bytes(context, a, b, fna, fnb))

        eleza assertDiff(expect, actual):
            # do sio compare expect na equal kama lists, because unittest
            # uses difflib to report difference between lists
            actual = list(actual)
            self.assertEqual(len(expect), len(actual))
            kila e, a kwenye zip(expect, actual):
                self.assertEqual(e, a)

        expect = [
            b'--- \xb3odz.txt',
            b'+++ \xc5\x82odz.txt',
            b'@@ -1 +1 @@',
            b'-\xa3odz ni a city kwenye Poland.',
            b'+\xc5\x81odz ni a city kwenye Poland.',
        ]
        actual = difflib.diff_bytes(unified, a, b, fna, fnb, lineterm=b'')
        assertDiff(expect, actual)

        # ukijumuisha dates (plain ASCII)
        datea = b'2005-03-18'
        dateb = b'2005-03-19'
        check(difflib.diff_bytes(unified, a, b, fna, fnb, datea, dateb))
        check(difflib.diff_bytes(context, a, b, fna, fnb, datea, dateb))

        expect = [
            # note the mixed encodings here: this ni deeply wrong by every
            # tenet of Unicode, but it doesn't crash, it's parseable by
            # patch, na it's how UNIX(tm) diff behaves
            b'--- \xb3odz.txt\t2005-03-18',
            b'+++ \xc5\x82odz.txt\t2005-03-19',
            b'@@ -1 +1 @@',
            b'-\xa3odz ni a city kwenye Poland.',
            b'+\xc5\x81odz ni a city kwenye Poland.',
        ]
        actual = difflib.diff_bytes(unified, a, b, fna, fnb, datea, dateb,
                                    lineterm=b'')
        assertDiff(expect, actual)

    eleza test_mixed_types_content(self):
        # type of input content must be consistent: all str ama all bytes
        a = [b'hello']
        b = ['hello']

        unified = difflib.unified_diff
        context = difflib.context_diff

        expect = "lines to compare must be str, sio bytes (b'hello')"
        self._assert_type_error(expect, unified, a, b)
        self._assert_type_error(expect, unified, b, a)
        self._assert_type_error(expect, context, a, b)
        self._assert_type_error(expect, context, b, a)

        expect = "all arguments must be bytes, sio str ('hello')"
        self._assert_type_error(expect, difflib.diff_bytes, unified, a, b)
        self._assert_type_error(expect, difflib.diff_bytes, unified, b, a)
        self._assert_type_error(expect, difflib.diff_bytes, context, a, b)
        self._assert_type_error(expect, difflib.diff_bytes, context, b, a)

    eleza test_mixed_types_filenames(self):
        # cannot pita filenames kama bytes ikiwa content ni str (this may sio be
        # the right behaviour, but at least the test demonstrates how
        # things work)
        a = ['hello\n']
        b = ['ohell\n']
        fna = b'ol\xe9.txt'     # filename transcoded kutoka ISO-8859-1
        fnb = b'ol\xc3a9.txt'   # to UTF-8
        self._assert_type_error(
            "all arguments must be str, not: b'ol\\xe9.txt'",
            difflib.unified_diff, a, b, fna, fnb)

    eleza test_mixed_types_dates(self):
        # type of dates must be consistent ukijumuisha type of contents
        a = [b'foo\n']
        b = [b'bar\n']
        datea = '1 fév'
        dateb = '3 fév'
        self._assert_type_error(
            "all arguments must be bytes, sio str ('1 fév')",
            difflib.diff_bytes, difflib.unified_diff,
            a, b, b'a', b'b', datea, dateb)

        # ikiwa input ni str, non-ASCII dates are fine
        a = ['foo\n']
        b = ['bar\n']
        list(difflib.unified_diff(a, b, 'a', 'b', datea, dateb))

    eleza _assert_type_error(self, msg, generator, *args):
        ukijumuisha self.assertRaises(TypeError) kama ctx:
            list(generator(*args))
        self.assertEqual(msg, str(ctx.exception))

kundi TestJunkAPIs(unittest.TestCase):
    eleza test_is_line_junk_true(self):
        kila line kwenye ['#', '  ', ' #', '# ', ' # ', '']:
            self.assertKweli(difflib.IS_LINE_JUNK(line), repr(line))

    eleza test_is_line_junk_false(self):
        kila line kwenye ['##', ' ##', '## ', 'abc ', 'abc #', 'Mr. Moose ni up!']:
            self.assertUongo(difflib.IS_LINE_JUNK(line), repr(line))

    eleza test_is_line_junk_REDOS(self):
        evil_input = ('\t' * 1000000) + '##'
        self.assertUongo(difflib.IS_LINE_JUNK(evil_input))

    eleza test_is_character_junk_true(self):
        kila char kwenye [' ', '\t']:
            self.assertKweli(difflib.IS_CHARACTER_JUNK(char), repr(char))

    eleza test_is_character_junk_false(self):
        kila char kwenye ['a', '#', '\n', '\f', '\r', '\v']:
            self.assertUongo(difflib.IS_CHARACTER_JUNK(char), repr(char))

eleza test_main():
    difflib.HtmlDiff._default_prefix = 0
    Doctests = doctest.DocTestSuite(difflib)
    run_unittest(
        TestWithAscii, TestAutojunk, TestSFpatches, TestSFbugs,
        TestOutputFormat, TestBytes, TestJunkAPIs, Doctests)

ikiwa __name__ == '__main__':
    test_main()
