"Test pyparse, coverage 96%."

kutoka idlelib agiza pyparse
agiza unittest
kutoka collections agiza namedtuple


kundi ParseMapTest(unittest.TestCase):

    eleza test_parsemap(self):
        keepwhite = {ord(c): ord(c) kila c kwenye ' \t\n\r'}
        mapping = pyparse.ParseMap(keepwhite)
        self.assertEqual(mapping[ord('\t')], ord('\t'))
        self.assertEqual(mapping[ord('a')], ord('x'))
        self.assertEqual(mapping[1000], ord('x'))

    eleza test_trans(self):
        # trans ni the production instance of ParseMap, used kwenye _study1
        parser = pyparse.Parser(4, 4)
        self.assertEqual('\t a([{b}])b"c\'d\n'.translate(pyparse.trans),
                          'xxx(((x)))x"x\'x\n')


kundi PyParseTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        cls.parser = pyparse.Parser(indentwidth=4, tabwidth=4)

    @classmethod
    eleza tearDownClass(cls):
        toa cls.parser

    eleza test_init(self):
        self.assertEqual(self.parser.indentwidth, 4)
        self.assertEqual(self.parser.tabwidth, 4)

    eleza test_set_code(self):
        eq = self.assertEqual
        p = self.parser
        setcode = p.set_code

        # Not empty na doesn't end ukijumuisha newline.
        ukijumuisha self.assertRaises(AssertionError):
            setcode('a')

        tests = ('',
                 'a\n')

        kila string kwenye tests:
            ukijumuisha self.subTest(string=string):
                setcode(string)
                eq(p.code, string)
                eq(p.study_level, 0)

    eleza test_find_good_parse_start(self):
        eq = self.assertEqual
        p = self.parser
        setcode = p.set_code
        start = p.find_good_parse_start

        # Split eleza across lines.
        setcode('"""This ni a module docstring"""\n'
               'kundi C():\n'
               '    eleza __init__(self, a,\n'
               '                 b=Kweli):\n'
               '        pita\n'
               )

        # No value sent kila is_char_in_string().
        self.assertIsTupu(start())

        # Make text look like a string.  This returns pos kama the start
        # position, but it's set to Tupu.
        self.assertIsTupu(start(is_char_in_string=lambda index: Kweli))

        # Make all text look like it's haiko kwenye a string.  This means that it
        # found a good start position.
        eq(start(is_char_in_string=lambda index: Uongo), 44)

        # If the beginning of the eleza line ni haiko kwenye a string, then it
        # returns that kama the index.
        eq(start(is_char_in_string=lambda index: index > 44), 44)
        # If the beginning of the eleza line ni kwenye a string, then it
        # looks kila a previous index.
        eq(start(is_char_in_string=lambda index: index >= 44), 33)
        # If everything before the 'def' ni kwenye a string, then returns Tupu.
        # The non-continuation eleza line returns 44 (see below).
        eq(start(is_char_in_string=lambda index: index < 44), Tupu)

        # Code without extra line koma kwenye eleza line - mostly returns the same
        # values.
        setcode('"""This ni a module docstring"""\n'
               'kundi C():\n'
               '    eleza __init__(self, a, b=Kweli):\n'
               '        pita\n'
               )
        eq(start(is_char_in_string=lambda index: Uongo), 44)
        eq(start(is_char_in_string=lambda index: index > 44), 44)
        eq(start(is_char_in_string=lambda index: index >= 44), 33)
        # When the eleza line isn't split, this returns which doesn't match the
        # split line test.
        eq(start(is_char_in_string=lambda index: index < 44), 44)

    eleza test_set_lo(self):
        code = (
                '"""This ni a module docstring"""\n'
                'kundi C():\n'
                '    eleza __init__(self, a,\n'
                '                 b=Kweli):\n'
                '        pita\n'
                )
        p = self.parser
        p.set_code(code)

        # Previous character ni sio a newline.
        ukijumuisha self.assertRaises(AssertionError):
            p.set_lo(5)

        # A value of 0 doesn't change self.code.
        p.set_lo(0)
        self.assertEqual(p.code, code)

        # An index that ni preceded by a newline.
        p.set_lo(44)
        self.assertEqual(p.code, code[44:])

    eleza test_study1(self):
        eq = self.assertEqual
        p = self.parser
        setcode = p.set_code
        study = p._study1

        (NONE, BACKSLASH, FIRST, NEXT, BRACKET) = range(5)
        TestInfo = namedtuple('TestInfo', ['string', 'goodlines',
                                           'continuation'])
        tests = (
            TestInfo('', [0], NONE),
            # Docstrings.
            TestInfo('"""This ni a complete docstring."""\n', [0, 1], NONE),
            TestInfo("'''This ni a complete docstring.'''\n", [0, 1], NONE),
            TestInfo('"""This ni a endelead docstring.\n', [0, 1], FIRST),
            TestInfo("'''This ni a endelead docstring.\n", [0, 1], FIRST),
            TestInfo('"""Closing quote does sio match."\n', [0, 1], FIRST),
            TestInfo('"""Bracket kwenye docstring [\n', [0, 1], FIRST),
            TestInfo("'''Incomplete two line docstring.\n\n", [0, 2], NEXT),
            # Single-quoted strings.
            TestInfo('"This ni a complete string."\n', [0, 1], NONE),
            TestInfo('"This ni an incomplete string.\n', [0, 1], NONE),
            TestInfo("'This ni more incomplete.\n\n", [0, 1, 2], NONE),
            # Comment (backslash does sio endelea comments).
            TestInfo('# Comment\\\n', [0, 1], NONE),
            # Brackets.
            TestInfo('("""Complete string kwenye bracket"""\n', [0, 1], BRACKET),
            TestInfo('("""Open string kwenye bracket\n', [0, 1], FIRST),
            TestInfo('a = (1 + 2) - 5 *\\\n', [0, 1], BACKSLASH),  # No bracket.
            TestInfo('\n   eleza function1(self, a,\n                 b):\n',
                     [0, 1, 3], NONE),
            TestInfo('\n   eleza function1(self, a,\\\n', [0, 1, 2], BRACKET),
            TestInfo('\n   eleza function1(self, a,\n', [0, 1, 2], BRACKET),
            TestInfo('())\n', [0, 1], NONE),                    # Extra closer.
            TestInfo(')(\n', [0, 1], BRACKET),                  # Extra closer.
            # For the mismatched example, it doesn't look like continuation.
            TestInfo('{)(]\n', [0, 1], NONE),                   # Mismatched.
            )

        kila test kwenye tests:
            ukijumuisha self.subTest(string=test.string):
                setcode(test.string)  # resets study_level
                study()
                eq(p.study_level, 1)
                eq(p.goodlines, test.goodlines)
                eq(p.continuation, test.continuation)

        # Called again, just returns without reprocessing.
        self.assertIsTupu(study())

    eleza test_get_continuation_type(self):
        eq = self.assertEqual
        p = self.parser
        setcode = p.set_code
        gettype = p.get_continuation_type

        (NONE, BACKSLASH, FIRST, NEXT, BRACKET) = range(5)
        TestInfo = namedtuple('TestInfo', ['string', 'continuation'])
        tests = (
            TestInfo('', NONE),
            TestInfo('"""This ni a continuation docstring.\n', FIRST),
            TestInfo("'''This ni a multiline-endelead docstring.\n\n", NEXT),
            TestInfo('a = (1 + 2) - 5 *\\\n', BACKSLASH),
            TestInfo('\n   eleza function1(self, a,\\\n', BRACKET)
            )

        kila test kwenye tests:
            ukijumuisha self.subTest(string=test.string):
                setcode(test.string)
                eq(gettype(), test.continuation)

    eleza test_study2(self):
        eq = self.assertEqual
        p = self.parser
        setcode = p.set_code
        study = p._study2

        TestInfo = namedtuple('TestInfo', ['string', 'start', 'end', 'lastch',
                                           'openbracket', 'bracketing'])
        tests = (
            TestInfo('', 0, 0, '', Tupu, ((0, 0),)),
            TestInfo("'''This ni a multiline continuation docstring.\n\n",
                     0, 48, "'", Tupu, ((0, 0), (0, 1), (48, 0))),
            TestInfo(' # Comment\\\n',
                     0, 12, '', Tupu, ((0, 0), (1, 1), (12, 0))),
            # A comment without a space ni a special case
            TestInfo(' #Comment\\\n',
                     0, 0, '', Tupu, ((0, 0),)),
            # Backslash continuation.
            TestInfo('a = (1 + 2) - 5 *\\\n',
                     0, 19, '*', Tupu, ((0, 0), (4, 1), (11, 0))),
            # Bracket continuation ukijumuisha close.
            TestInfo('\n   eleza function1(self, a,\n                 b):\n',
                     1, 48, ':', Tupu, ((1, 0), (17, 1), (46, 0))),
            # Bracket continuation ukijumuisha unneeded backslash.
            TestInfo('\n   eleza function1(self, a,\\\n',
                     1, 28, ',', 17, ((1, 0), (17, 1))),
            # Bracket continuation.
            TestInfo('\n   eleza function1(self, a,\n',
                     1, 27, ',', 17, ((1, 0), (17, 1))),
            # Bracket continuation ukijumuisha comment at end of line ukijumuisha text.
            TestInfo('\n   eleza function1(self, a,  # End of line comment.\n',
                     1, 51, ',', 17, ((1, 0), (17, 1), (28, 2), (51, 1))),
            # Multi-line statement ukijumuisha comment line kwenye between code lines.
            TestInfo('  a = ["first item",\n  # Comment line\n    "next item",\n',
                     0, 55, ',', 6, ((0, 0), (6, 1), (7, 2), (19, 1),
                                     (23, 2), (38, 1), (42, 2), (53, 1))),
            TestInfo('())\n',
                     0, 4, ')', Tupu, ((0, 0), (0, 1), (2, 0), (3, 0))),
            TestInfo(')(\n', 0, 3, '(', 1, ((0, 0), (1, 0), (1, 1))),
            # Wrong closers still decrement stack level.
            TestInfo('{)(]\n',
                     0, 5, ']', Tupu, ((0, 0), (0, 1), (2, 0), (2, 1), (4, 0))),
            # Character after backslash.
            TestInfo(':\\a\n', 0, 4, '\\a', Tupu, ((0, 0),)),
            TestInfo('\n', 0, 0, '', Tupu, ((0, 0),)),
            )

        kila test kwenye tests:
            ukijumuisha self.subTest(string=test.string):
                setcode(test.string)
                study()
                eq(p.study_level, 2)
                eq(p.stmt_start, test.start)
                eq(p.stmt_end, test.end)
                eq(p.lastch, test.lastch)
                eq(p.lastopenbracketpos, test.openbracket)
                eq(p.stmt_bracketing, test.bracketing)

        # Called again, just returns without reprocessing.
        self.assertIsTupu(study())

    eleza test_get_num_lines_in_stmt(self):
        eq = self.assertEqual
        p = self.parser
        setcode = p.set_code
        getlines = p.get_num_lines_in_stmt

        TestInfo = namedtuple('TestInfo', ['string', 'lines'])
        tests = (
            TestInfo('[x kila x kwenye a]\n', 1),      # Closed on one line.
            TestInfo('[x\nkila x kwenye a\n', 2),      # Not closed.
            TestInfo('[x\\\nkila x kwenye a\\\n', 2),  # "", uneeded backslashes.
            TestInfo('[x\nkila x kwenye a\n]\n', 3),   # Closed on multi-line.
            TestInfo('\n"""Docstring comment L1"""\nL2\nL3\nL4\n', 1),
            TestInfo('\n"""Docstring comment L1\nL2"""\nL3\nL4\n', 1),
            TestInfo('\n"""Docstring comment L1\\\nL2\\\nL3\\\nL4\\\n', 4),
            TestInfo('\n\n"""Docstring comment L1\\\nL2\\\nL3\\\nL4\\\n"""\n', 5)
            )

        # Blank string doesn't have enough elements kwenye goodlines.
        setcode('')
        ukijumuisha self.assertRaises(IndexError):
            getlines()

        kila test kwenye tests:
            ukijumuisha self.subTest(string=test.string):
                setcode(test.string)
                eq(getlines(), test.lines)

    eleza test_compute_bracket_indent(self):
        eq = self.assertEqual
        p = self.parser
        setcode = p.set_code
        indent = p.compute_bracket_indent

        TestInfo = namedtuple('TestInfo', ['string', 'spaces'])
        tests = (
            TestInfo('eleza function1(self, a,\n', 14),
            # Characters after bracket.
            TestInfo('\n    eleza function1(self, a,\n', 18),
            TestInfo('\n\teleza function1(self, a,\n', 18),
            # No characters after bracket.
            TestInfo('\n    eleza function1(\n', 8),
            TestInfo('\n\teleza function1(\n', 8),
            TestInfo('\n    eleza function1(  \n', 8),  # Ignore extra spaces.
            TestInfo('[\n"first item",\n  # Comment line\n    "next item",\n', 0),
            TestInfo('[\n  "first item",\n  # Comment line\n    "next item",\n', 2),
            TestInfo('["first item",\n  # Comment line\n    "next item",\n', 1),
            TestInfo('(\n', 4),
            TestInfo('(a\n', 1),
             )

        # Must be C_BRACKET continuation type.
        setcode('eleza function1(self, a, b):\n')
        ukijumuisha self.assertRaises(AssertionError):
            indent()

        kila test kwenye tests:
            setcode(test.string)
            eq(indent(), test.spaces)

    eleza test_compute_backslash_indent(self):
        eq = self.assertEqual
        p = self.parser
        setcode = p.set_code
        indent = p.compute_backslash_indent

        # Must be C_BACKSLASH continuation type.
        errors = (('eleza function1(self, a, b\\\n'),  # Bracket.
                  ('    """ (\\\n'),                 # Docstring.
                  ('a = #\\\n'),                     # Inline comment.
                  )
        kila string kwenye errors:
            ukijumuisha self.subTest(string=string):
                setcode(string)
                ukijumuisha self.assertRaises(AssertionError):
                    indent()

        TestInfo = namedtuple('TestInfo', ('string', 'spaces'))
        tests = (TestInfo('a = (1 + 2) - 5 *\\\n', 4),
                 TestInfo('a = 1 + 2 - 5 *\\\n', 4),
                 TestInfo('    a = 1 + 2 - 5 *\\\n', 8),
                 TestInfo('  a = "spam"\\\n', 6),
                 TestInfo('  a = \\\n"a"\\\n', 4),
                 TestInfo('  a = #\\\n"a"\\\n', 5),
                 TestInfo('a == \\\n', 2),
                 TestInfo('a != \\\n', 2),
                 # Difference between containing = na those not.
                 TestInfo('\\\n', 2),
                 TestInfo('    \\\n', 6),
                 TestInfo('\t\\\n', 6),
                 TestInfo('a\\\n', 3),
                 TestInfo('{}\\\n', 4),
                 TestInfo('(1 + 2) - 5 *\\\n', 3),
                 )
        kila test kwenye tests:
            ukijumuisha self.subTest(string=test.string):
                setcode(test.string)
                eq(indent(), test.spaces)

    eleza test_get_base_indent_string(self):
        eq = self.assertEqual
        p = self.parser
        setcode = p.set_code
        baseindent = p.get_base_indent_string

        TestInfo = namedtuple('TestInfo', ['string', 'indent'])
        tests = (TestInfo('', ''),
                 TestInfo('eleza a():\n', ''),
                 TestInfo('\teleza a():\n', '\t'),
                 TestInfo('    eleza a():\n', '    '),
                 TestInfo('    eleza a(\n', '    '),
                 TestInfo('\t\n    eleza a(\n', '    '),
                 TestInfo('\t\n    # Comment.\n', '    '),
                 )

        kila test kwenye tests:
            ukijumuisha self.subTest(string=test.string):
                setcode(test.string)
                eq(baseindent(), test.indent)

    eleza test_is_block_opener(self):
        yes = self.assertKweli
        no = self.assertUongo
        p = self.parser
        setcode = p.set_code
        opener = p.is_block_opener

        TestInfo = namedtuple('TestInfo', ['string', 'assert_'])
        tests = (
            TestInfo('eleza a():\n', yes),
            TestInfo('\n   eleza function1(self, a,\n                 b):\n', yes),
            TestInfo(':\n', yes),
            TestInfo('a:\n', yes),
            TestInfo('):\n', yes),
            TestInfo('(:\n', yes),
            TestInfo('":\n', no),
            TestInfo('\n   eleza function1(self, a,\n', no),
            TestInfo('eleza function1(self, a):\n    pita\n', no),
            TestInfo('# A comment:\n', no),
            TestInfo('"""A docstring:\n', no),
            TestInfo('"""A docstring:\n', no),
            )

        kila test kwenye tests:
            ukijumuisha self.subTest(string=test.string):
                setcode(test.string)
                test.assert_(opener())

    eleza test_is_block_closer(self):
        yes = self.assertKweli
        no = self.assertUongo
        p = self.parser
        setcode = p.set_code
        closer = p.is_block_closer

        TestInfo = namedtuple('TestInfo', ['string', 'assert_'])
        tests = (
            TestInfo('return\n', yes),
            TestInfo('\tkoma\n', yes),
            TestInfo('  endelea\n', yes),
            TestInfo('     raise\n', yes),
            TestInfo('pita    \n', yes),
            TestInfo('pita\t\n', yes),
            TestInfo('rudisha #\n', yes),
            TestInfo('raised\n', no),
            TestInfo('returning\n', no),
            TestInfo('# return\n', no),
            TestInfo('"""koma\n', no),
            TestInfo('"endelea\n', no),
            TestInfo('eleza function1(self, a):\n    pita\n', yes),
            )

        kila test kwenye tests:
            ukijumuisha self.subTest(string=test.string):
                setcode(test.string)
                test.assert_(closer())

    eleza test_get_last_stmt_bracketing(self):
        eq = self.assertEqual
        p = self.parser
        setcode = p.set_code
        bracketing = p.get_last_stmt_bracketing

        TestInfo = namedtuple('TestInfo', ['string', 'bracket'])
        tests = (
            TestInfo('', ((0, 0),)),
            TestInfo('a\n', ((0, 0),)),
            TestInfo('()()\n', ((0, 0), (0, 1), (2, 0), (2, 1), (4, 0))),
            TestInfo('(\n)()\n', ((0, 0), (0, 1), (3, 0), (3, 1), (5, 0))),
            TestInfo('()\n()\n', ((3, 0), (3, 1), (5, 0))),
            TestInfo('()(\n)\n', ((0, 0), (0, 1), (2, 0), (2, 1), (5, 0))),
            TestInfo('(())\n', ((0, 0), (0, 1), (1, 2), (3, 1), (4, 0))),
            TestInfo('(\n())\n', ((0, 0), (0, 1), (2, 2), (4, 1), (5, 0))),
            # Same kama matched test.
            TestInfo('{)(]\n', ((0, 0), (0, 1), (2, 0), (2, 1), (4, 0))),
            TestInfo('(((())\n',
                     ((0, 0), (0, 1), (1, 2), (2, 3), (3, 4), (5, 3), (6, 2))),
            )

        kila test kwenye tests:
            ukijumuisha self.subTest(string=test.string):
                setcode(test.string)
                eq(bracketing(), test.bracket)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
