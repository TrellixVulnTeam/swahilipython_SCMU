kutoka test agiza support
kutoka tokenize agiza (tokenize, _tokenize, untokenize, NUMBER, NAME, OP,
                     STRING, ENDMARKER, ENCODING, tok_name, detect_encoding,
                     open kama tokenize_open, Untokenizer, generate_tokens,
                     NEWLINE)
kutoka io agiza BytesIO, StringIO
agiza unittest
kutoka unittest agiza TestCase, mock
kutoka test.test_grammar agiza (VALID_UNDERSCORE_LITERALS,
                               INVALID_UNDERSCORE_LITERALS)
agiza os
agiza token


# Converts a source string into a list of textual representation
# of the tokens such as:
# `    NAME       'if'          (1, 0) (1, 2)`
# to make writing tests easier.
eleza stringify_tokens_from_source(token_generator, source_string):
    result = []
    num_lines = len(source_string.splitlines())
    missing_trailing_nl = source_string[-1] haiko kwenye '\r\n'

    kila type, token, start, end, line kwenye token_generator:
        ikiwa type == ENDMARKER:
            koma
        # Ignore the new line on the last line ikiwa the input lacks one
        ikiwa missing_trailing_nl na type == NEWLINE na end[0] == num_lines:
            endelea
        type = tok_name[type]
        result.append(f"    {type:10} {token!r:13} {start} {end}")

    rudisha result

kundi TokenizeTest(TestCase):
    # Tests kila the tokenize module.

    # The tests can be really simple. Given a small fragment of source
    # code, andika out a table ukijumuisha tokens. The ENDMARKER, ENCODING na
    # final NEWLINE are omitted kila brevity.

    eleza check_tokenize(self, s, expected):
        # Format the tokens kwenye s kwenye a table format.
        # The ENDMARKER na final NEWLINE are omitted.
        f = BytesIO(s.encode('utf-8'))
        result = stringify_tokens_from_source(tokenize(f.readline), s)

        self.assertEqual(result,
                         ["    ENCODING   'utf-8'       (0, 0) (0, 0)"] +
                         expected.rstrip().splitlines())

    eleza test_implicit_newline(self):
        # Make sure that the tokenizer puts kwenye an implicit NEWLINE
        # when the input lacks a trailing new line.
        f = BytesIO("x".encode('utf-8'))
        tokens = list(tokenize(f.readline))
        self.assertEqual(tokens[-2].type, NEWLINE)
        self.assertEqual(tokens[-1].type, ENDMARKER)

    eleza test_basic(self):
        self.check_tokenize("1 + 1", """\
    NUMBER     '1'           (1, 0) (1, 1)
    OP         '+'           (1, 2) (1, 3)
    NUMBER     '1'           (1, 4) (1, 5)
    """)
        self.check_tokenize("ikiwa Uongo:\n"
                            "    # NL\n"
                            "    \n"
                            "    Kweli = Uongo # NEWLINE\n", """\
    NAME       'if'          (1, 0) (1, 2)
    NAME       'Uongo'       (1, 3) (1, 8)
    OP         ':'           (1, 8) (1, 9)
    NEWLINE    '\\n'          (1, 9) (1, 10)
    COMMENT    '# NL'        (2, 4) (2, 8)
    NL         '\\n'          (2, 8) (2, 9)
    NL         '\\n'          (3, 4) (3, 5)
    INDENT     '    '        (4, 0) (4, 4)
    NAME       'Kweli'        (4, 4) (4, 8)
    OP         '='           (4, 9) (4, 10)
    NAME       'Uongo'       (4, 11) (4, 16)
    COMMENT    '# NEWLINE'   (4, 17) (4, 26)
    NEWLINE    '\\n'          (4, 26) (4, 27)
    DEDENT     ''            (5, 0) (5, 0)
    """)
        indent_error_file = b"""\
eleza k(x):
    x += 2
  x += 5
"""
        readline = BytesIO(indent_error_file).readline
        ukijumuisha self.assertRaisesRegex(IndentationError,
                                    "unindent does sio match any "
                                    "outer indentation level"):
            kila tok kwenye tokenize(readline):
                pita

    eleza test_int(self):
        # Ordinary integers na binary operators
        self.check_tokenize("0xff <= 255", """\
    NUMBER     '0xff'        (1, 0) (1, 4)
    OP         '<='          (1, 5) (1, 7)
    NUMBER     '255'         (1, 8) (1, 11)
    """)
        self.check_tokenize("0b10 <= 255", """\
    NUMBER     '0b10'        (1, 0) (1, 4)
    OP         '<='          (1, 5) (1, 7)
    NUMBER     '255'         (1, 8) (1, 11)
    """)
        self.check_tokenize("0o123 <= 0O123", """\
    NUMBER     '0o123'       (1, 0) (1, 5)
    OP         '<='          (1, 6) (1, 8)
    NUMBER     '0O123'       (1, 9) (1, 14)
    """)
        self.check_tokenize("1234567 > ~0x15", """\
    NUMBER     '1234567'     (1, 0) (1, 7)
    OP         '>'           (1, 8) (1, 9)
    OP         '~'           (1, 10) (1, 11)
    NUMBER     '0x15'        (1, 11) (1, 15)
    """)
        self.check_tokenize("2134568 != 1231515", """\
    NUMBER     '2134568'     (1, 0) (1, 7)
    OP         '!='          (1, 8) (1, 10)
    NUMBER     '1231515'     (1, 11) (1, 18)
    """)
        self.check_tokenize("(-124561-1) & 200000000", """\
    OP         '('           (1, 0) (1, 1)
    OP         '-'           (1, 1) (1, 2)
    NUMBER     '124561'      (1, 2) (1, 8)
    OP         '-'           (1, 8) (1, 9)
    NUMBER     '1'           (1, 9) (1, 10)
    OP         ')'           (1, 10) (1, 11)
    OP         '&'           (1, 12) (1, 13)
    NUMBER     '200000000'   (1, 14) (1, 23)
    """)
        self.check_tokenize("0xdeadbeef != -1", """\
    NUMBER     '0xdeadbeef'  (1, 0) (1, 10)
    OP         '!='          (1, 11) (1, 13)
    OP         '-'           (1, 14) (1, 15)
    NUMBER     '1'           (1, 15) (1, 16)
    """)
        self.check_tokenize("0xdeadc0de & 12345", """\
    NUMBER     '0xdeadc0de'  (1, 0) (1, 10)
    OP         '&'           (1, 11) (1, 12)
    NUMBER     '12345'       (1, 13) (1, 18)
    """)
        self.check_tokenize("0xFF & 0x15 | 1234", """\
    NUMBER     '0xFF'        (1, 0) (1, 4)
    OP         '&'           (1, 5) (1, 6)
    NUMBER     '0x15'        (1, 7) (1, 11)
    OP         '|'           (1, 12) (1, 13)
    NUMBER     '1234'        (1, 14) (1, 18)
    """)

    eleza test_long(self):
        # Long integers
        self.check_tokenize("x = 0", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    NUMBER     '0'           (1, 4) (1, 5)
    """)
        self.check_tokenize("x = 0xfffffffffff", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    NUMBER     '0xfffffffffff' (1, 4) (1, 17)
    """)
        self.check_tokenize("x = 123141242151251616110", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    NUMBER     '123141242151251616110' (1, 4) (1, 25)
    """)
        self.check_tokenize("x = -15921590215012591", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    OP         '-'           (1, 4) (1, 5)
    NUMBER     '15921590215012591' (1, 5) (1, 22)
    """)

    eleza test_float(self):
        # Floating point numbers
        self.check_tokenize("x = 3.14159", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    NUMBER     '3.14159'     (1, 4) (1, 11)
    """)
        self.check_tokenize("x = 314159.", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    NUMBER     '314159.'     (1, 4) (1, 11)
    """)
        self.check_tokenize("x = .314159", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    NUMBER     '.314159'     (1, 4) (1, 11)
    """)
        self.check_tokenize("x = 3e14159", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    NUMBER     '3e14159'     (1, 4) (1, 11)
    """)
        self.check_tokenize("x = 3E123", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    NUMBER     '3E123'       (1, 4) (1, 9)
    """)
        self.check_tokenize("x+y = 3e-1230", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '+'           (1, 1) (1, 2)
    NAME       'y'           (1, 2) (1, 3)
    OP         '='           (1, 4) (1, 5)
    NUMBER     '3e-1230'     (1, 6) (1, 13)
    """)
        self.check_tokenize("x = 3.14e159", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    NUMBER     '3.14e159'    (1, 4) (1, 12)
    """)

    eleza test_underscore_literals(self):
        eleza number_token(s):
            f = BytesIO(s.encode('utf-8'))
            kila toktype, token, start, end, line kwenye tokenize(f.readline):
                ikiwa toktype == NUMBER:
                    rudisha token
            rudisha 'invalid token'
        kila lit kwenye VALID_UNDERSCORE_LITERALS:
            ikiwa '(' kwenye lit:
                # this won't work ukijumuisha compound complex inputs
                endelea
            self.assertEqual(number_token(lit), lit)
        kila lit kwenye INVALID_UNDERSCORE_LITERALS:
            self.assertNotEqual(number_token(lit), lit)

    eleza test_string(self):
        # String literals
        self.check_tokenize("x = ''; y = \"\"", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    STRING     "''"          (1, 4) (1, 6)
    OP         ';'           (1, 6) (1, 7)
    NAME       'y'           (1, 8) (1, 9)
    OP         '='           (1, 10) (1, 11)
    STRING     '""'          (1, 12) (1, 14)
    """)
        self.check_tokenize("x = '\"'; y = \"'\"", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    STRING     '\\'"\\''       (1, 4) (1, 7)
    OP         ';'           (1, 7) (1, 8)
    NAME       'y'           (1, 9) (1, 10)
    OP         '='           (1, 11) (1, 12)
    STRING     '"\\'"'        (1, 13) (1, 16)
    """)
        self.check_tokenize("x = \"doesn't \"shrink\", does it\"", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    STRING     '"doesn\\'t "' (1, 4) (1, 14)
    NAME       'shrink'      (1, 14) (1, 20)
    STRING     '", does it"' (1, 20) (1, 31)
    """)
        self.check_tokenize("x = 'abc' + 'ABC'", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    STRING     "'abc'"       (1, 4) (1, 9)
    OP         '+'           (1, 10) (1, 11)
    STRING     "'ABC'"       (1, 12) (1, 17)
    """)
        self.check_tokenize('y = "ABC" + "ABC"', """\
    NAME       'y'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    STRING     '"ABC"'       (1, 4) (1, 9)
    OP         '+'           (1, 10) (1, 11)
    STRING     '"ABC"'       (1, 12) (1, 17)
    """)
        self.check_tokenize("x = r'abc' + r'ABC' + R'ABC' + R'ABC'", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    STRING     "r'abc'"      (1, 4) (1, 10)
    OP         '+'           (1, 11) (1, 12)
    STRING     "r'ABC'"      (1, 13) (1, 19)
    OP         '+'           (1, 20) (1, 21)
    STRING     "R'ABC'"      (1, 22) (1, 28)
    OP         '+'           (1, 29) (1, 30)
    STRING     "R'ABC'"      (1, 31) (1, 37)
    """)
        self.check_tokenize('y = r"abc" + r"ABC" + R"ABC" + R"ABC"', """\
    NAME       'y'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    STRING     'r"abc"'      (1, 4) (1, 10)
    OP         '+'           (1, 11) (1, 12)
    STRING     'r"ABC"'      (1, 13) (1, 19)
    OP         '+'           (1, 20) (1, 21)
    STRING     'R"ABC"'      (1, 22) (1, 28)
    OP         '+'           (1, 29) (1, 30)
    STRING     'R"ABC"'      (1, 31) (1, 37)
    """)

        self.check_tokenize("u'abc' + U'abc'", """\
    STRING     "u'abc'"      (1, 0) (1, 6)
    OP         '+'           (1, 7) (1, 8)
    STRING     "U'abc'"      (1, 9) (1, 15)
    """)
        self.check_tokenize('u"abc" + U"abc"', """\
    STRING     'u"abc"'      (1, 0) (1, 6)
    OP         '+'           (1, 7) (1, 8)
    STRING     'U"abc"'      (1, 9) (1, 15)
    """)

        self.check_tokenize("b'abc' + B'abc'", """\
    STRING     "b'abc'"      (1, 0) (1, 6)
    OP         '+'           (1, 7) (1, 8)
    STRING     "B'abc'"      (1, 9) (1, 15)
    """)
        self.check_tokenize('b"abc" + B"abc"', """\
    STRING     'b"abc"'      (1, 0) (1, 6)
    OP         '+'           (1, 7) (1, 8)
    STRING     'B"abc"'      (1, 9) (1, 15)
    """)
        self.check_tokenize("br'abc' + bR'abc' + Br'abc' + BR'abc'", """\
    STRING     "br'abc'"     (1, 0) (1, 7)
    OP         '+'           (1, 8) (1, 9)
    STRING     "bR'abc'"     (1, 10) (1, 17)
    OP         '+'           (1, 18) (1, 19)
    STRING     "Br'abc'"     (1, 20) (1, 27)
    OP         '+'           (1, 28) (1, 29)
    STRING     "BR'abc'"     (1, 30) (1, 37)
    """)
        self.check_tokenize('br"abc" + bR"abc" + Br"abc" + BR"abc"', """\
    STRING     'br"abc"'     (1, 0) (1, 7)
    OP         '+'           (1, 8) (1, 9)
    STRING     'bR"abc"'     (1, 10) (1, 17)
    OP         '+'           (1, 18) (1, 19)
    STRING     'Br"abc"'     (1, 20) (1, 27)
    OP         '+'           (1, 28) (1, 29)
    STRING     'BR"abc"'     (1, 30) (1, 37)
    """)
        self.check_tokenize("rb'abc' + rB'abc' + Rb'abc' + RB'abc'", """\
    STRING     "rb'abc'"     (1, 0) (1, 7)
    OP         '+'           (1, 8) (1, 9)
    STRING     "rB'abc'"     (1, 10) (1, 17)
    OP         '+'           (1, 18) (1, 19)
    STRING     "Rb'abc'"     (1, 20) (1, 27)
    OP         '+'           (1, 28) (1, 29)
    STRING     "RB'abc'"     (1, 30) (1, 37)
    """)
        self.check_tokenize('rb"abc" + rB"abc" + Rb"abc" + RB"abc"', """\
    STRING     'rb"abc"'     (1, 0) (1, 7)
    OP         '+'           (1, 8) (1, 9)
    STRING     'rB"abc"'     (1, 10) (1, 17)
    OP         '+'           (1, 18) (1, 19)
    STRING     'Rb"abc"'     (1, 20) (1, 27)
    OP         '+'           (1, 28) (1, 29)
    STRING     'RB"abc"'     (1, 30) (1, 37)
    """)
        # Check 0, 1, na 2 character string prefixes.
        self.check_tokenize(r'"a\
de\
fg"', """\
    STRING     '"a\\\\\\nde\\\\\\nfg"\' (1, 0) (3, 3)
    """)
        self.check_tokenize(r'u"a\
de"', """\
    STRING     'u"a\\\\\\nde"\'  (1, 0) (2, 3)
    """)
        self.check_tokenize(r'rb"a\
d"', """\
    STRING     'rb"a\\\\\\nd"\'  (1, 0) (2, 2)
    """)
        self.check_tokenize(r'"""a\
b"""', """\
    STRING     '\"\""a\\\\\\nb\"\""' (1, 0) (2, 4)
    """)
        self.check_tokenize(r'u"""a\
b"""', """\
    STRING     'u\"\""a\\\\\\nb\"\""' (1, 0) (2, 4)
    """)
        self.check_tokenize(r'rb"""a\
b\
c"""', """\
    STRING     'rb"\""a\\\\\\nb\\\\\\nc"\""' (1, 0) (3, 4)
    """)
        self.check_tokenize('f"abc"', """\
    STRING     'f"abc"'      (1, 0) (1, 6)
    """)
        self.check_tokenize('fR"a{b}c"', """\
    STRING     'fR"a{b}c"'   (1, 0) (1, 9)
    """)
        self.check_tokenize('f"""abc"""', """\
    STRING     'f\"\"\"abc\"\"\"'  (1, 0) (1, 10)
    """)
        self.check_tokenize(r'f"abc\
def"', """\
    STRING     'f"abc\\\\\\ndef"' (1, 0) (2, 4)
    """)
        self.check_tokenize(r'Rf"abc\
def"', """\
    STRING     'Rf"abc\\\\\\ndef"' (1, 0) (2, 4)
    """)

    eleza test_function(self):
        self.check_tokenize("eleza d22(a, b, c=2, d=2, *k): pita", """\
    NAME       'def'         (1, 0) (1, 3)
    NAME       'd22'         (1, 4) (1, 7)
    OP         '('           (1, 7) (1, 8)
    NAME       'a'           (1, 8) (1, 9)
    OP         ','           (1, 9) (1, 10)
    NAME       'b'           (1, 11) (1, 12)
    OP         ','           (1, 12) (1, 13)
    NAME       'c'           (1, 14) (1, 15)
    OP         '='           (1, 15) (1, 16)
    NUMBER     '2'           (1, 16) (1, 17)
    OP         ','           (1, 17) (1, 18)
    NAME       'd'           (1, 19) (1, 20)
    OP         '='           (1, 20) (1, 21)
    NUMBER     '2'           (1, 21) (1, 22)
    OP         ','           (1, 22) (1, 23)
    OP         '*'           (1, 24) (1, 25)
    NAME       'k'           (1, 25) (1, 26)
    OP         ')'           (1, 26) (1, 27)
    OP         ':'           (1, 27) (1, 28)
    NAME       'pita'        (1, 29) (1, 33)
    """)
        self.check_tokenize("eleza d01v_(a=1, *k, **w): pita", """\
    NAME       'def'         (1, 0) (1, 3)
    NAME       'd01v_'       (1, 4) (1, 9)
    OP         '('           (1, 9) (1, 10)
    NAME       'a'           (1, 10) (1, 11)
    OP         '='           (1, 11) (1, 12)
    NUMBER     '1'           (1, 12) (1, 13)
    OP         ','           (1, 13) (1, 14)
    OP         '*'           (1, 15) (1, 16)
    NAME       'k'           (1, 16) (1, 17)
    OP         ','           (1, 17) (1, 18)
    OP         '**'          (1, 19) (1, 21)
    NAME       'w'           (1, 21) (1, 22)
    OP         ')'           (1, 22) (1, 23)
    OP         ':'           (1, 23) (1, 24)
    NAME       'pita'        (1, 25) (1, 29)
    """)
        self.check_tokenize("eleza d23(a: str, b: int=3) -> int: pita", """\
    NAME       'def'         (1, 0) (1, 3)
    NAME       'd23'         (1, 4) (1, 7)
    OP         '('           (1, 7) (1, 8)
    NAME       'a'           (1, 8) (1, 9)
    OP         ':'           (1, 9) (1, 10)
    NAME       'str'         (1, 11) (1, 14)
    OP         ','           (1, 14) (1, 15)
    NAME       'b'           (1, 16) (1, 17)
    OP         ':'           (1, 17) (1, 18)
    NAME       'int'         (1, 19) (1, 22)
    OP         '='           (1, 22) (1, 23)
    NUMBER     '3'           (1, 23) (1, 24)
    OP         ')'           (1, 24) (1, 25)
    OP         '->'          (1, 26) (1, 28)
    NAME       'int'         (1, 29) (1, 32)
    OP         ':'           (1, 32) (1, 33)
    NAME       'pita'        (1, 34) (1, 38)
    """)

    eleza test_comparison(self):
        # Comparison
        self.check_tokenize("ikiwa 1 < 1 > 1 == 1 >= 5 <= 0x15 <= 0x12 != "
                            "1 na 5 kwenye 1 haiko kwenye 1 ni 1 ama 5 ni sio 1: pita", """\
    NAME       'if'          (1, 0) (1, 2)
    NUMBER     '1'           (1, 3) (1, 4)
    OP         '<'           (1, 5) (1, 6)
    NUMBER     '1'           (1, 7) (1, 8)
    OP         '>'           (1, 9) (1, 10)
    NUMBER     '1'           (1, 11) (1, 12)
    OP         '=='          (1, 13) (1, 15)
    NUMBER     '1'           (1, 16) (1, 17)
    OP         '>='          (1, 18) (1, 20)
    NUMBER     '5'           (1, 21) (1, 22)
    OP         '<='          (1, 23) (1, 25)
    NUMBER     '0x15'        (1, 26) (1, 30)
    OP         '<='          (1, 31) (1, 33)
    NUMBER     '0x12'        (1, 34) (1, 38)
    OP         '!='          (1, 39) (1, 41)
    NUMBER     '1'           (1, 42) (1, 43)
    NAME       'and'         (1, 44) (1, 47)
    NUMBER     '5'           (1, 48) (1, 49)
    NAME       'in'          (1, 50) (1, 52)
    NUMBER     '1'           (1, 53) (1, 54)
    NAME       'not'         (1, 55) (1, 58)
    NAME       'in'          (1, 59) (1, 61)
    NUMBER     '1'           (1, 62) (1, 63)
    NAME       'is'          (1, 64) (1, 66)
    NUMBER     '1'           (1, 67) (1, 68)
    NAME       'or'          (1, 69) (1, 71)
    NUMBER     '5'           (1, 72) (1, 73)
    NAME       'is'          (1, 74) (1, 76)
    NAME       'not'         (1, 77) (1, 80)
    NUMBER     '1'           (1, 81) (1, 82)
    OP         ':'           (1, 82) (1, 83)
    NAME       'pita'        (1, 84) (1, 88)
    """)

    eleza test_shift(self):
        # Shift
        self.check_tokenize("x = 1 << 1 >> 5", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    NUMBER     '1'           (1, 4) (1, 5)
    OP         '<<'          (1, 6) (1, 8)
    NUMBER     '1'           (1, 9) (1, 10)
    OP         '>>'          (1, 11) (1, 13)
    NUMBER     '5'           (1, 14) (1, 15)
    """)

    eleza test_additive(self):
        # Additive
        self.check_tokenize("x = 1 - y + 15 - 1 + 0x124 + z + a[5]", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    NUMBER     '1'           (1, 4) (1, 5)
    OP         '-'           (1, 6) (1, 7)
    NAME       'y'           (1, 8) (1, 9)
    OP         '+'           (1, 10) (1, 11)
    NUMBER     '15'          (1, 12) (1, 14)
    OP         '-'           (1, 15) (1, 16)
    NUMBER     '1'           (1, 17) (1, 18)
    OP         '+'           (1, 19) (1, 20)
    NUMBER     '0x124'       (1, 21) (1, 26)
    OP         '+'           (1, 27) (1, 28)
    NAME       'z'           (1, 29) (1, 30)
    OP         '+'           (1, 31) (1, 32)
    NAME       'a'           (1, 33) (1, 34)
    OP         '['           (1, 34) (1, 35)
    NUMBER     '5'           (1, 35) (1, 36)
    OP         ']'           (1, 36) (1, 37)
    """)

    eleza test_multiplicative(self):
        # Multiplicative
        self.check_tokenize("x = 1//1*1/5*12%0x12@42", """\
    NAME       'x'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    NUMBER     '1'           (1, 4) (1, 5)
    OP         '//'          (1, 5) (1, 7)
    NUMBER     '1'           (1, 7) (1, 8)
    OP         '*'           (1, 8) (1, 9)
    NUMBER     '1'           (1, 9) (1, 10)
    OP         '/'           (1, 10) (1, 11)
    NUMBER     '5'           (1, 11) (1, 12)
    OP         '*'           (1, 12) (1, 13)
    NUMBER     '12'          (1, 13) (1, 15)
    OP         '%'           (1, 15) (1, 16)
    NUMBER     '0x12'        (1, 16) (1, 20)
    OP         '@'           (1, 20) (1, 21)
    NUMBER     '42'          (1, 21) (1, 23)
    """)

    eleza test_unary(self):
        # Unary
        self.check_tokenize("~1 ^ 1 & 1 |1 ^ -1", """\
    OP         '~'           (1, 0) (1, 1)
    NUMBER     '1'           (1, 1) (1, 2)
    OP         '^'           (1, 3) (1, 4)
    NUMBER     '1'           (1, 5) (1, 6)
    OP         '&'           (1, 7) (1, 8)
    NUMBER     '1'           (1, 9) (1, 10)
    OP         '|'           (1, 11) (1, 12)
    NUMBER     '1'           (1, 12) (1, 13)
    OP         '^'           (1, 14) (1, 15)
    OP         '-'           (1, 16) (1, 17)
    NUMBER     '1'           (1, 17) (1, 18)
    """)
        self.check_tokenize("-1*1/1+1*1//1 - ---1**1", """\
    OP         '-'           (1, 0) (1, 1)
    NUMBER     '1'           (1, 1) (1, 2)
    OP         '*'           (1, 2) (1, 3)
    NUMBER     '1'           (1, 3) (1, 4)
    OP         '/'           (1, 4) (1, 5)
    NUMBER     '1'           (1, 5) (1, 6)
    OP         '+'           (1, 6) (1, 7)
    NUMBER     '1'           (1, 7) (1, 8)
    OP         '*'           (1, 8) (1, 9)
    NUMBER     '1'           (1, 9) (1, 10)
    OP         '//'          (1, 10) (1, 12)
    NUMBER     '1'           (1, 12) (1, 13)
    OP         '-'           (1, 14) (1, 15)
    OP         '-'           (1, 16) (1, 17)
    OP         '-'           (1, 17) (1, 18)
    OP         '-'           (1, 18) (1, 19)
    NUMBER     '1'           (1, 19) (1, 20)
    OP         '**'          (1, 20) (1, 22)
    NUMBER     '1'           (1, 22) (1, 23)
    """)

    eleza test_selector(self):
        # Selector
        self.check_tokenize("agiza sys, time\nx = sys.modules['time'].time()", """\
    NAME       'import'      (1, 0) (1, 6)
    NAME       'sys'         (1, 7) (1, 10)
    OP         ','           (1, 10) (1, 11)
    NAME       'time'        (1, 12) (1, 16)
    NEWLINE    '\\n'          (1, 16) (1, 17)
    NAME       'x'           (2, 0) (2, 1)
    OP         '='           (2, 2) (2, 3)
    NAME       'sys'         (2, 4) (2, 7)
    OP         '.'           (2, 7) (2, 8)
    NAME       'modules'     (2, 8) (2, 15)
    OP         '['           (2, 15) (2, 16)
    STRING     "'time'"      (2, 16) (2, 22)
    OP         ']'           (2, 22) (2, 23)
    OP         '.'           (2, 23) (2, 24)
    NAME       'time'        (2, 24) (2, 28)
    OP         '('           (2, 28) (2, 29)
    OP         ')'           (2, 29) (2, 30)
    """)

    eleza test_method(self):
        # Methods
        self.check_tokenize("@staticmethod\neleza foo(x,y): pita", """\
    OP         '@'           (1, 0) (1, 1)
    NAME       'staticmethod' (1, 1) (1, 13)
    NEWLINE    '\\n'          (1, 13) (1, 14)
    NAME       'def'         (2, 0) (2, 3)
    NAME       'foo'         (2, 4) (2, 7)
    OP         '('           (2, 7) (2, 8)
    NAME       'x'           (2, 8) (2, 9)
    OP         ','           (2, 9) (2, 10)
    NAME       'y'           (2, 10) (2, 11)
    OP         ')'           (2, 11) (2, 12)
    OP         ':'           (2, 12) (2, 13)
    NAME       'pita'        (2, 14) (2, 18)
    """)

    eleza test_tabs(self):
        # Evil tabs
        self.check_tokenize("eleza f():\n"
                            "\tikiwa x\n"
                            "        \tpita", """\
    NAME       'def'         (1, 0) (1, 3)
    NAME       'f'           (1, 4) (1, 5)
    OP         '('           (1, 5) (1, 6)
    OP         ')'           (1, 6) (1, 7)
    OP         ':'           (1, 7) (1, 8)
    NEWLINE    '\\n'          (1, 8) (1, 9)
    INDENT     '\\t'          (2, 0) (2, 1)
    NAME       'if'          (2, 1) (2, 3)
    NAME       'x'           (2, 4) (2, 5)
    NEWLINE    '\\n'          (2, 5) (2, 6)
    INDENT     '        \\t'  (3, 0) (3, 9)
    NAME       'pita'        (3, 9) (3, 13)
    DEDENT     ''            (4, 0) (4, 0)
    DEDENT     ''            (4, 0) (4, 0)
    """)

    eleza test_non_ascii_identifiers(self):
        # Non-ascii identifiers
        self.check_tokenize("Örter = 'places'\ngrün = 'green'", """\
    NAME       'Örter'       (1, 0) (1, 5)
    OP         '='           (1, 6) (1, 7)
    STRING     "'places'"    (1, 8) (1, 16)
    NEWLINE    '\\n'          (1, 16) (1, 17)
    NAME       'grün'        (2, 0) (2, 4)
    OP         '='           (2, 5) (2, 6)
    STRING     "'green'"     (2, 7) (2, 14)
    """)

    eleza test_unicode(self):
        # Legacy unicode literals:
        self.check_tokenize("Örter = u'places'\ngrün = U'green'", """\
    NAME       'Örter'       (1, 0) (1, 5)
    OP         '='           (1, 6) (1, 7)
    STRING     "u'places'"   (1, 8) (1, 17)
    NEWLINE    '\\n'          (1, 17) (1, 18)
    NAME       'grün'        (2, 0) (2, 4)
    OP         '='           (2, 5) (2, 6)
    STRING     "U'green'"    (2, 7) (2, 15)
    """)

    eleza test_async(self):
        # Async/await extension:
        self.check_tokenize("async = 1", """\
    NAME       'async'       (1, 0) (1, 5)
    OP         '='           (1, 6) (1, 7)
    NUMBER     '1'           (1, 8) (1, 9)
    """)

        self.check_tokenize("a = (async = 1)", """\
    NAME       'a'           (1, 0) (1, 1)
    OP         '='           (1, 2) (1, 3)
    OP         '('           (1, 4) (1, 5)
    NAME       'async'       (1, 5) (1, 10)
    OP         '='           (1, 11) (1, 12)
    NUMBER     '1'           (1, 13) (1, 14)
    OP         ')'           (1, 14) (1, 15)
    """)

        self.check_tokenize("async()", """\
    NAME       'async'       (1, 0) (1, 5)
    OP         '('           (1, 5) (1, 6)
    OP         ')'           (1, 6) (1, 7)
    """)

        self.check_tokenize("kundi async(Bar):pita", """\
    NAME       'class'       (1, 0) (1, 5)
    NAME       'async'       (1, 6) (1, 11)
    OP         '('           (1, 11) (1, 12)
    NAME       'Bar'         (1, 12) (1, 15)
    OP         ')'           (1, 15) (1, 16)
    OP         ':'           (1, 16) (1, 17)
    NAME       'pita'        (1, 17) (1, 21)
    """)

        self.check_tokenize("kundi async:pita", """\
    NAME       'class'       (1, 0) (1, 5)
    NAME       'async'       (1, 6) (1, 11)
    OP         ':'           (1, 11) (1, 12)
    NAME       'pita'        (1, 12) (1, 16)
    """)

        self.check_tokenize("await = 1", """\
    NAME       'await'       (1, 0) (1, 5)
    OP         '='           (1, 6) (1, 7)
    NUMBER     '1'           (1, 8) (1, 9)
    """)

        self.check_tokenize("foo.async", """\
    NAME       'foo'         (1, 0) (1, 3)
    OP         '.'           (1, 3) (1, 4)
    NAME       'async'       (1, 4) (1, 9)
    """)

        self.check_tokenize("async kila a kwenye b: pita", """\
    NAME       'async'       (1, 0) (1, 5)
    NAME       'for'         (1, 6) (1, 9)
    NAME       'a'           (1, 10) (1, 11)
    NAME       'in'          (1, 12) (1, 14)
    NAME       'b'           (1, 15) (1, 16)
    OP         ':'           (1, 16) (1, 17)
    NAME       'pita'        (1, 18) (1, 22)
    """)

        self.check_tokenize("async ukijumuisha a kama b: pita", """\
    NAME       'async'       (1, 0) (1, 5)
    NAME       'with'        (1, 6) (1, 10)
    NAME       'a'           (1, 11) (1, 12)
    NAME       'as'          (1, 13) (1, 15)
    NAME       'b'           (1, 16) (1, 17)
    OP         ':'           (1, 17) (1, 18)
    NAME       'pita'        (1, 19) (1, 23)
    """)

        self.check_tokenize("async.foo", """\
    NAME       'async'       (1, 0) (1, 5)
    OP         '.'           (1, 5) (1, 6)
    NAME       'foo'         (1, 6) (1, 9)
    """)

        self.check_tokenize("async", """\
    NAME       'async'       (1, 0) (1, 5)
    """)

        self.check_tokenize("async\n#comment\nawait", """\
    NAME       'async'       (1, 0) (1, 5)
    NEWLINE    '\\n'          (1, 5) (1, 6)
    COMMENT    '#comment'    (2, 0) (2, 8)
    NL         '\\n'          (2, 8) (2, 9)
    NAME       'await'       (3, 0) (3, 5)
    """)

        self.check_tokenize("async\n...\nawait", """\
    NAME       'async'       (1, 0) (1, 5)
    NEWLINE    '\\n'          (1, 5) (1, 6)
    OP         '...'         (2, 0) (2, 3)
    NEWLINE    '\\n'          (2, 3) (2, 4)
    NAME       'await'       (3, 0) (3, 5)
    """)

        self.check_tokenize("async\nawait", """\
    NAME       'async'       (1, 0) (1, 5)
    NEWLINE    '\\n'          (1, 5) (1, 6)
    NAME       'await'       (2, 0) (2, 5)
    """)

        self.check_tokenize("foo.async + 1", """\
    NAME       'foo'         (1, 0) (1, 3)
    OP         '.'           (1, 3) (1, 4)
    NAME       'async'       (1, 4) (1, 9)
    OP         '+'           (1, 10) (1, 11)
    NUMBER     '1'           (1, 12) (1, 13)
    """)

        self.check_tokenize("async eleza foo(): pita", """\
    NAME       'async'       (1, 0) (1, 5)
    NAME       'def'         (1, 6) (1, 9)
    NAME       'foo'         (1, 10) (1, 13)
    OP         '('           (1, 13) (1, 14)
    OP         ')'           (1, 14) (1, 15)
    OP         ':'           (1, 15) (1, 16)
    NAME       'pita'        (1, 17) (1, 21)
    """)

        self.check_tokenize('''\
async eleza foo():
  eleza foo(await):
    await = 1
  ikiwa 1:
    await
async += 1
''', """\
    NAME       'async'       (1, 0) (1, 5)
    NAME       'def'         (1, 6) (1, 9)
    NAME       'foo'         (1, 10) (1, 13)
    OP         '('           (1, 13) (1, 14)
    OP         ')'           (1, 14) (1, 15)
    OP         ':'           (1, 15) (1, 16)
    NEWLINE    '\\n'          (1, 16) (1, 17)
    INDENT     '  '          (2, 0) (2, 2)
    NAME       'def'         (2, 2) (2, 5)
    NAME       'foo'         (2, 6) (2, 9)
    OP         '('           (2, 9) (2, 10)
    NAME       'await'       (2, 10) (2, 15)
    OP         ')'           (2, 15) (2, 16)
    OP         ':'           (2, 16) (2, 17)
    NEWLINE    '\\n'          (2, 17) (2, 18)
    INDENT     '    '        (3, 0) (3, 4)
    NAME       'await'       (3, 4) (3, 9)
    OP         '='           (3, 10) (3, 11)
    NUMBER     '1'           (3, 12) (3, 13)
    NEWLINE    '\\n'          (3, 13) (3, 14)
    DEDENT     ''            (4, 2) (4, 2)
    NAME       'if'          (4, 2) (4, 4)
    NUMBER     '1'           (4, 5) (4, 6)
    OP         ':'           (4, 6) (4, 7)
    NEWLINE    '\\n'          (4, 7) (4, 8)
    INDENT     '    '        (5, 0) (5, 4)
    NAME       'await'       (5, 4) (5, 9)
    NEWLINE    '\\n'          (5, 9) (5, 10)
    DEDENT     ''            (6, 0) (6, 0)
    DEDENT     ''            (6, 0) (6, 0)
    NAME       'async'       (6, 0) (6, 5)
    OP         '+='          (6, 6) (6, 8)
    NUMBER     '1'           (6, 9) (6, 10)
    NEWLINE    '\\n'          (6, 10) (6, 11)
    """)

        self.check_tokenize('''\
async eleza foo():
  async kila i kwenye 1: pita''', """\
    NAME       'async'       (1, 0) (1, 5)
    NAME       'def'         (1, 6) (1, 9)
    NAME       'foo'         (1, 10) (1, 13)
    OP         '('           (1, 13) (1, 14)
    OP         ')'           (1, 14) (1, 15)
    OP         ':'           (1, 15) (1, 16)
    NEWLINE    '\\n'          (1, 16) (1, 17)
    INDENT     '  '          (2, 0) (2, 2)
    NAME       'async'       (2, 2) (2, 7)
    NAME       'for'         (2, 8) (2, 11)
    NAME       'i'           (2, 12) (2, 13)
    NAME       'in'          (2, 14) (2, 16)
    NUMBER     '1'           (2, 17) (2, 18)
    OP         ':'           (2, 18) (2, 19)
    NAME       'pita'        (2, 20) (2, 24)
    DEDENT     ''            (3, 0) (3, 0)
    """)

        self.check_tokenize('''async eleza foo(async): await''', """\
    NAME       'async'       (1, 0) (1, 5)
    NAME       'def'         (1, 6) (1, 9)
    NAME       'foo'         (1, 10) (1, 13)
    OP         '('           (1, 13) (1, 14)
    NAME       'async'       (1, 14) (1, 19)
    OP         ')'           (1, 19) (1, 20)
    OP         ':'           (1, 20) (1, 21)
    NAME       'await'       (1, 22) (1, 27)
    """)

        self.check_tokenize('''\
eleza f():

  eleza baz(): pita
  async eleza bar(): pita

  await = 2''', """\
    NAME       'def'         (1, 0) (1, 3)
    NAME       'f'           (1, 4) (1, 5)
    OP         '('           (1, 5) (1, 6)
    OP         ')'           (1, 6) (1, 7)
    OP         ':'           (1, 7) (1, 8)
    NEWLINE    '\\n'          (1, 8) (1, 9)
    NL         '\\n'          (2, 0) (2, 1)
    INDENT     '  '          (3, 0) (3, 2)
    NAME       'def'         (3, 2) (3, 5)
    NAME       'baz'         (3, 6) (3, 9)
    OP         '('           (3, 9) (3, 10)
    OP         ')'           (3, 10) (3, 11)
    OP         ':'           (3, 11) (3, 12)
    NAME       'pita'        (3, 13) (3, 17)
    NEWLINE    '\\n'          (3, 17) (3, 18)
    NAME       'async'       (4, 2) (4, 7)
    NAME       'def'         (4, 8) (4, 11)
    NAME       'bar'         (4, 12) (4, 15)
    OP         '('           (4, 15) (4, 16)
    OP         ')'           (4, 16) (4, 17)
    OP         ':'           (4, 17) (4, 18)
    NAME       'pita'        (4, 19) (4, 23)
    NEWLINE    '\\n'          (4, 23) (4, 24)
    NL         '\\n'          (5, 0) (5, 1)
    NAME       'await'       (6, 2) (6, 7)
    OP         '='           (6, 8) (6, 9)
    NUMBER     '2'           (6, 10) (6, 11)
    DEDENT     ''            (7, 0) (7, 0)
    """)

        self.check_tokenize('''\
async eleza f():

  eleza baz(): pita
  async eleza bar(): pita

  await = 2''', """\
    NAME       'async'       (1, 0) (1, 5)
    NAME       'def'         (1, 6) (1, 9)
    NAME       'f'           (1, 10) (1, 11)
    OP         '('           (1, 11) (1, 12)
    OP         ')'           (1, 12) (1, 13)
    OP         ':'           (1, 13) (1, 14)
    NEWLINE    '\\n'          (1, 14) (1, 15)
    NL         '\\n'          (2, 0) (2, 1)
    INDENT     '  '          (3, 0) (3, 2)
    NAME       'def'         (3, 2) (3, 5)
    NAME       'baz'         (3, 6) (3, 9)
    OP         '('           (3, 9) (3, 10)
    OP         ')'           (3, 10) (3, 11)
    OP         ':'           (3, 11) (3, 12)
    NAME       'pita'        (3, 13) (3, 17)
    NEWLINE    '\\n'          (3, 17) (3, 18)
    NAME       'async'       (4, 2) (4, 7)
    NAME       'def'         (4, 8) (4, 11)
    NAME       'bar'         (4, 12) (4, 15)
    OP         '('           (4, 15) (4, 16)
    OP         ')'           (4, 16) (4, 17)
    OP         ':'           (4, 17) (4, 18)
    NAME       'pita'        (4, 19) (4, 23)
    NEWLINE    '\\n'          (4, 23) (4, 24)
    NL         '\\n'          (5, 0) (5, 1)
    NAME       'await'       (6, 2) (6, 7)
    OP         '='           (6, 8) (6, 9)
    NUMBER     '2'           (6, 10) (6, 11)
    DEDENT     ''            (7, 0) (7, 0)
    """)

kundi GenerateTokensTest(TokenizeTest):
    eleza check_tokenize(self, s, expected):
        # Format the tokens kwenye s kwenye a table format.
        # The ENDMARKER na final NEWLINE are omitted.
        f = StringIO(s)
        result = stringify_tokens_from_source(generate_tokens(f.readline), s)
        self.assertEqual(result, expected.rstrip().splitlines())


eleza decistmt(s):
    result = []
    g = tokenize(BytesIO(s.encode('utf-8')).readline)   # tokenize the string
    kila toknum, tokval, _, _, _  kwenye g:
        ikiwa toknum == NUMBER na '.' kwenye tokval:  # replace NUMBER tokens
            result.extend([
                (NAME, 'Decimal'),
                (OP, '('),
                (STRING, repr(tokval)),
                (OP, ')')
            ])
        isipokua:
            result.append((toknum, tokval))
    rudisha untokenize(result).decode('utf-8')

kundi TestMisc(TestCase):

    eleza test_decistmt(self):
        # Substitute Decimals kila floats kwenye a string of statements.
        # This ni an example kutoka the docs.

        kutoka decimal agiza Decimal
        s = '+21.3e-5*-.1234/81.7'
        self.assertEqual(decistmt(s),
                         "+Decimal ('21.3e-5')*-Decimal ('.1234')/Decimal ('81.7')")

        # The format of the exponent ni inherited kutoka the platform C library.
        # Known cases are "e-007" (Windows) na "e-07" (sio Windows).  Since
        # we're only showing 11 digits, na the 12th isn't close to 5, the
        # rest of the output should be platform-independent.
        self.assertRegex(repr(eval(s)), '-3.2171603427[0-9]*e-0+7')

        # Output kutoka calculations ukijumuisha Decimal should be identical across all
        # platforms.
        self.assertEqual(eval(decistmt(s)),
                         Decimal('-3.217160342717258261933904529E-7'))


kundi TestTokenizerAdheresToPep0263(TestCase):
    """
    Test that tokenizer adheres to the coding behaviour stipulated kwenye PEP 0263.
    """

    eleza _testFile(self, filename):
        path = os.path.join(os.path.dirname(__file__), filename)
        TestRoundtrip.check_roundtrip(self, open(path, 'rb'))

    eleza test_utf8_coding_cookie_and_no_utf8_bom(self):
        f = 'tokenize_tests-utf8-coding-cookie-and-no-utf8-bom-sig.txt'
        self._testFile(f)

    eleza test_latin1_coding_cookie_and_utf8_bom(self):
        """
        As per PEP 0263, ikiwa a file starts ukijumuisha a utf-8 BOM signature, the only
        allowed encoding kila the comment ni 'utf-8'.  The text file used kwenye
        this test starts ukijumuisha a BOM signature, but specifies latin1 kama the
        coding, so verify that a SyntaxError ni raised, which matches the
        behaviour of the interpreter when it encounters a similar condition.
        """
        f = 'tokenize_tests-latin1-coding-cookie-and-utf8-bom-sig.txt'
        self.assertRaises(SyntaxError, self._testFile, f)

    eleza test_no_coding_cookie_and_utf8_bom(self):
        f = 'tokenize_tests-no-coding-cookie-and-utf8-bom-sig-only.txt'
        self._testFile(f)

    eleza test_utf8_coding_cookie_and_utf8_bom(self):
        f = 'tokenize_tests-utf8-coding-cookie-and-utf8-bom-sig.txt'
        self._testFile(f)

    eleza test_bad_coding_cookie(self):
        self.assertRaises(SyntaxError, self._testFile, 'bad_coding.py')
        self.assertRaises(SyntaxError, self._testFile, 'bad_coding2.py')


kundi Test_Tokenize(TestCase):

    eleza test__tokenize_decodes_with_specified_encoding(self):
        literal = '"ЉЊЈЁЂ"'
        line = literal.encode('utf-8')
        first = Uongo
        eleza readline():
            nonlocal first
            ikiwa sio first:
                first = Kweli
                rudisha line
            isipokua:
                rudisha b''

        # skip the initial encoding token na the end tokens
        tokens = list(_tokenize(readline, encoding='utf-8'))[1:-2]
        expected_tokens = [(3, '"ЉЊЈЁЂ"', (1, 0), (1, 7), '"ЉЊЈЁЂ"')]
        self.assertEqual(tokens, expected_tokens,
                         "bytes sio decoded ukijumuisha encoding")

    eleza test__tokenize_does_not_decode_with_encoding_none(self):
        literal = '"ЉЊЈЁЂ"'
        first = Uongo
        eleza readline():
            nonlocal first
            ikiwa sio first:
                first = Kweli
                rudisha literal
            isipokua:
                rudisha b''

        # skip the end tokens
        tokens = list(_tokenize(readline, encoding=Tupu))[:-2]
        expected_tokens = [(3, '"ЉЊЈЁЂ"', (1, 0), (1, 7), '"ЉЊЈЁЂ"')]
        self.assertEqual(tokens, expected_tokens,
                         "string sio tokenized when encoding ni Tupu")


kundi TestDetectEncoding(TestCase):

    eleza get_readline(self, lines):
        index = 0
        eleza readline():
            nonlocal index
            ikiwa index == len(lines):
                ashiria StopIteration
            line = lines[index]
            index += 1
            rudisha line
        rudisha readline

    eleza test_no_bom_no_encoding_cookie(self):
        lines = (
            b'# something\n',
            b'andika(something)\n',
            b'do_something(else)\n'
        )
        encoding, consumed_lines = detect_encoding(self.get_readline(lines))
        self.assertEqual(encoding, 'utf-8')
        self.assertEqual(consumed_lines, list(lines[:2]))

    eleza test_bom_no_cookie(self):
        lines = (
            b'\xef\xbb\xbf# something\n',
            b'andika(something)\n',
            b'do_something(else)\n'
        )
        encoding, consumed_lines = detect_encoding(self.get_readline(lines))
        self.assertEqual(encoding, 'utf-8-sig')
        self.assertEqual(consumed_lines,
                         [b'# something\n', b'andika(something)\n'])

    eleza test_cookie_first_line_no_bom(self):
        lines = (
            b'# -*- coding: latin-1 -*-\n',
            b'andika(something)\n',
            b'do_something(else)\n'
        )
        encoding, consumed_lines = detect_encoding(self.get_readline(lines))
        self.assertEqual(encoding, 'iso-8859-1')
        self.assertEqual(consumed_lines, [b'# -*- coding: latin-1 -*-\n'])

    eleza test_matched_bom_and_cookie_first_line(self):
        lines = (
            b'\xef\xbb\xbf# coding=utf-8\n',
            b'andika(something)\n',
            b'do_something(else)\n'
        )
        encoding, consumed_lines = detect_encoding(self.get_readline(lines))
        self.assertEqual(encoding, 'utf-8-sig')
        self.assertEqual(consumed_lines, [b'# coding=utf-8\n'])

    eleza test_mismatched_bom_and_cookie_first_line_raises_syntaxerror(self):
        lines = (
            b'\xef\xbb\xbf# vim: set fileencoding=ascii :\n',
            b'andika(something)\n',
            b'do_something(else)\n'
        )
        readline = self.get_readline(lines)
        self.assertRaises(SyntaxError, detect_encoding, readline)

    eleza test_cookie_second_line_no_bom(self):
        lines = (
            b'#! something\n',
            b'# vim: set fileencoding=ascii :\n',
            b'andika(something)\n',
            b'do_something(else)\n'
        )
        encoding, consumed_lines = detect_encoding(self.get_readline(lines))
        self.assertEqual(encoding, 'ascii')
        expected = [b'#! something\n', b'# vim: set fileencoding=ascii :\n']
        self.assertEqual(consumed_lines, expected)

    eleza test_matched_bom_and_cookie_second_line(self):
        lines = (
            b'\xef\xbb\xbf#! something\n',
            b'f# coding=utf-8\n',
            b'andika(something)\n',
            b'do_something(else)\n'
        )
        encoding, consumed_lines = detect_encoding(self.get_readline(lines))
        self.assertEqual(encoding, 'utf-8-sig')
        self.assertEqual(consumed_lines,
                         [b'#! something\n', b'f# coding=utf-8\n'])

    eleza test_mismatched_bom_and_cookie_second_line_raises_syntaxerror(self):
        lines = (
            b'\xef\xbb\xbf#! something\n',
            b'# vim: set fileencoding=ascii :\n',
            b'andika(something)\n',
            b'do_something(else)\n'
        )
        readline = self.get_readline(lines)
        self.assertRaises(SyntaxError, detect_encoding, readline)

    eleza test_cookie_second_line_noncommented_first_line(self):
        lines = (
            b"andika('\xc2\xa3')\n",
            b'# vim: set fileencoding=iso8859-15 :\n',
            b"andika('\xe2\x82\xac')\n"
        )
        encoding, consumed_lines = detect_encoding(self.get_readline(lines))
        self.assertEqual(encoding, 'utf-8')
        expected = [b"andika('\xc2\xa3')\n"]
        self.assertEqual(consumed_lines, expected)

    eleza test_cookie_second_line_commented_first_line(self):
        lines = (
            b"#andika('\xc2\xa3')\n",
            b'# vim: set fileencoding=iso8859-15 :\n',
            b"andika('\xe2\x82\xac')\n"
        )
        encoding, consumed_lines = detect_encoding(self.get_readline(lines))
        self.assertEqual(encoding, 'iso8859-15')
        expected = [b"#andika('\xc2\xa3')\n", b'# vim: set fileencoding=iso8859-15 :\n']
        self.assertEqual(consumed_lines, expected)

    eleza test_cookie_second_line_empty_first_line(self):
        lines = (
            b'\n',
            b'# vim: set fileencoding=iso8859-15 :\n',
            b"andika('\xe2\x82\xac')\n"
        )
        encoding, consumed_lines = detect_encoding(self.get_readline(lines))
        self.assertEqual(encoding, 'iso8859-15')
        expected = [b'\n', b'# vim: set fileencoding=iso8859-15 :\n']
        self.assertEqual(consumed_lines, expected)

    eleza test_latin1_normalization(self):
        # See get_normal_name() kwenye tokenizer.c.
        encodings = ("latin-1", "iso-8859-1", "iso-latin-1", "latin-1-unix",
                     "iso-8859-1-unix", "iso-latin-1-mac")
        kila encoding kwenye encodings:
            kila rep kwenye ("-", "_"):
                enc = encoding.replace("-", rep)
                lines = (b"#!/usr/bin/python\n",
                         b"# coding: " + enc.encode("ascii") + b"\n",
                         b"andika(things)\n",
                         b"do_something += 4\n")
                rl = self.get_readline(lines)
                found, consumed_lines = detect_encoding(rl)
                self.assertEqual(found, "iso-8859-1")

    eleza test_syntaxerror_latin1(self):
        # Issue 14629: need to ashiria SyntaxError ikiwa the first
        # line(s) have non-UTF-8 characters
        lines = (
            b'andika("\xdf")', # Latin-1: LATIN SMALL LETTER SHARP S
            )
        readline = self.get_readline(lines)
        self.assertRaises(SyntaxError, detect_encoding, readline)


    eleza test_utf8_normalization(self):
        # See get_normal_name() kwenye tokenizer.c.
        encodings = ("utf-8", "utf-8-mac", "utf-8-unix")
        kila encoding kwenye encodings:
            kila rep kwenye ("-", "_"):
                enc = encoding.replace("-", rep)
                lines = (b"#!/usr/bin/python\n",
                         b"# coding: " + enc.encode("ascii") + b"\n",
                         b"1 + 3\n")
                rl = self.get_readline(lines)
                found, consumed_lines = detect_encoding(rl)
                self.assertEqual(found, "utf-8")

    eleza test_short_files(self):
        readline = self.get_readline((b'andika(something)\n',))
        encoding, consumed_lines = detect_encoding(readline)
        self.assertEqual(encoding, 'utf-8')
        self.assertEqual(consumed_lines, [b'andika(something)\n'])

        encoding, consumed_lines = detect_encoding(self.get_readline(()))
        self.assertEqual(encoding, 'utf-8')
        self.assertEqual(consumed_lines, [])

        readline = self.get_readline((b'\xef\xbb\xbfandika(something)\n',))
        encoding, consumed_lines = detect_encoding(readline)
        self.assertEqual(encoding, 'utf-8-sig')
        self.assertEqual(consumed_lines, [b'andika(something)\n'])

        readline = self.get_readline((b'\xef\xbb\xbf',))
        encoding, consumed_lines = detect_encoding(readline)
        self.assertEqual(encoding, 'utf-8-sig')
        self.assertEqual(consumed_lines, [])

        readline = self.get_readline((b'# coding: bad\n',))
        self.assertRaises(SyntaxError, detect_encoding, readline)

    eleza test_false_encoding(self):
        # Issue 18873: "Encoding" detected kwenye non-comment lines
        readline = self.get_readline((b'andika("#coding=fake")',))
        encoding, consumed_lines = detect_encoding(readline)
        self.assertEqual(encoding, 'utf-8')
        self.assertEqual(consumed_lines, [b'andika("#coding=fake")'])

    eleza test_open(self):
        filename = support.TESTFN + '.py'
        self.addCleanup(support.unlink, filename)

        # test coding cookie
        kila encoding kwenye ('iso-8859-15', 'utf-8'):
            ukijumuisha open(filename, 'w', encoding=encoding) kama fp:
                andika("# coding: %s" % encoding, file=fp)
                andika("andika('euro:\u20ac')", file=fp)
            ukijumuisha tokenize_open(filename) kama fp:
                self.assertEqual(fp.encoding, encoding)
                self.assertEqual(fp.mode, 'r')

        # test BOM (no coding cookie)
        ukijumuisha open(filename, 'w', encoding='utf-8-sig') kama fp:
            andika("andika('euro:\u20ac')", file=fp)
        ukijumuisha tokenize_open(filename) kama fp:
            self.assertEqual(fp.encoding, 'utf-8-sig')
            self.assertEqual(fp.mode, 'r')

    eleza test_filename_in_exception(self):
        # When possible, include the file name kwenye the exception.
        path = 'some_file_path'
        lines = (
            b'andika("\xdf")', # Latin-1: LATIN SMALL LETTER SHARP S
            )
        kundi Bunk:
            eleza __init__(self, lines, path):
                self.name = path
                self._lines = lines
                self._index = 0

            eleza readline(self):
                ikiwa self._index == len(lines):
                    ashiria StopIteration
                line = lines[self._index]
                self._index += 1
                rudisha line

        ukijumuisha self.assertRaises(SyntaxError):
            ins = Bunk(lines, path)
            # Make sure lacking a name isn't an issue.
            toa ins.name
            detect_encoding(ins.readline)
        ukijumuisha self.assertRaisesRegex(SyntaxError, '.*{}'.format(path)):
            ins = Bunk(lines, path)
            detect_encoding(ins.readline)

    eleza test_open_error(self):
        # Issue #23840: open() must close the binary file on error
        m = BytesIO(b'#coding:xxx')
        ukijumuisha mock.patch('tokenize._builtin_open', return_value=m):
            self.assertRaises(SyntaxError, tokenize_open, 'foobar')
        self.assertKweli(m.closed)


kundi TestTokenize(TestCase):

    eleza test_tokenize(self):
        agiza tokenize kama tokenize_module
        encoding = object()
        encoding_used = Tupu
        eleza mock_detect_encoding(readline):
            rudisha encoding, [b'first', b'second']

        eleza mock__tokenize(readline, encoding):
            nonlocal encoding_used
            encoding_used = encoding
            out = []
            wakati Kweli:
                next_line = readline()
                ikiwa next_line:
                    out.append(next_line)
                    endelea
                rudisha out

        counter = 0
        eleza mock_readline():
            nonlocal counter
            counter += 1
            ikiwa counter == 5:
                rudisha b''
            rudisha str(counter).encode()

        orig_detect_encoding = tokenize_module.detect_encoding
        orig__tokenize = tokenize_module._tokenize
        tokenize_module.detect_encoding = mock_detect_encoding
        tokenize_module._tokenize = mock__tokenize
        jaribu:
            results = tokenize(mock_readline)
            self.assertEqual(list(results),
                             [b'first', b'second', b'1', b'2', b'3', b'4'])
        mwishowe:
            tokenize_module.detect_encoding = orig_detect_encoding
            tokenize_module._tokenize = orig__tokenize

        self.assertEqual(encoding_used, encoding)

    eleza test_oneline_defs(self):
        buf = []
        kila i kwenye range(500):
            buf.append('eleza i{i}(): rudisha {i}'.format(i=i))
        buf.append('OK')
        buf = '\n'.join(buf)

        # Test that 500 consequent, one-line defs ni OK
        toks = list(tokenize(BytesIO(buf.encode('utf-8')).readline))
        self.assertEqual(toks[-3].string, 'OK') # [-1] ni always ENDMARKER
                                                # [-2] ni always NEWLINE

    eleza assertExactTypeEqual(self, opstr, *optypes):
        tokens = list(tokenize(BytesIO(opstr.encode('utf-8')).readline))
        num_optypes = len(optypes)
        self.assertEqual(len(tokens), 3 + num_optypes)
        self.assertEqual(tok_name[tokens[0].exact_type],
                         tok_name[ENCODING])
        kila i kwenye range(num_optypes):
            self.assertEqual(tok_name[tokens[i + 1].exact_type],
                             tok_name[optypes[i]])
        self.assertEqual(tok_name[tokens[1 + num_optypes].exact_type],
                         tok_name[token.NEWLINE])
        self.assertEqual(tok_name[tokens[2 + num_optypes].exact_type],
                         tok_name[token.ENDMARKER])

    eleza test_exact_type(self):
        self.assertExactTypeEqual('()', token.LPAR, token.RPAR)
        self.assertExactTypeEqual('[]', token.LSQB, token.RSQB)
        self.assertExactTypeEqual(':', token.COLON)
        self.assertExactTypeEqual(',', token.COMMA)
        self.assertExactTypeEqual(';', token.SEMI)
        self.assertExactTypeEqual('+', token.PLUS)
        self.assertExactTypeEqual('-', token.MINUS)
        self.assertExactTypeEqual('*', token.STAR)
        self.assertExactTypeEqual('/', token.SLASH)
        self.assertExactTypeEqual('|', token.VBAR)
        self.assertExactTypeEqual('&', token.AMPER)
        self.assertExactTypeEqual('<', token.LESS)
        self.assertExactTypeEqual('>', token.GREATER)
        self.assertExactTypeEqual('=', token.EQUAL)
        self.assertExactTypeEqual('.', token.DOT)
        self.assertExactTypeEqual('%', token.PERCENT)
        self.assertExactTypeEqual('{}', token.LBRACE, token.RBRACE)
        self.assertExactTypeEqual('==', token.EQEQUAL)
        self.assertExactTypeEqual('!=', token.NOTEQUAL)
        self.assertExactTypeEqual('<=', token.LESSEQUAL)
        self.assertExactTypeEqual('>=', token.GREATEREQUAL)
        self.assertExactTypeEqual('~', token.TILDE)
        self.assertExactTypeEqual('^', token.CIRCUMFLEX)
        self.assertExactTypeEqual('<<', token.LEFTSHIFT)
        self.assertExactTypeEqual('>>', token.RIGHTSHIFT)
        self.assertExactTypeEqual('**', token.DOUBLESTAR)
        self.assertExactTypeEqual('+=', token.PLUSEQUAL)
        self.assertExactTypeEqual('-=', token.MINEQUAL)
        self.assertExactTypeEqual('*=', token.STAREQUAL)
        self.assertExactTypeEqual('/=', token.SLASHEQUAL)
        self.assertExactTypeEqual('%=', token.PERCENTEQUAL)
        self.assertExactTypeEqual('&=', token.AMPEREQUAL)
        self.assertExactTypeEqual('|=', token.VBAREQUAL)
        self.assertExactTypeEqual('^=', token.CIRCUMFLEXEQUAL)
        self.assertExactTypeEqual('^=', token.CIRCUMFLEXEQUAL)
        self.assertExactTypeEqual('<<=', token.LEFTSHIFTEQUAL)
        self.assertExactTypeEqual('>>=', token.RIGHTSHIFTEQUAL)
        self.assertExactTypeEqual('**=', token.DOUBLESTAREQUAL)
        self.assertExactTypeEqual('//', token.DOUBLESLASH)
        self.assertExactTypeEqual('//=', token.DOUBLESLASHEQUAL)
        self.assertExactTypeEqual(':=', token.COLONEQUAL)
        self.assertExactTypeEqual('...', token.ELLIPSIS)
        self.assertExactTypeEqual('->', token.RARROW)
        self.assertExactTypeEqual('@', token.AT)
        self.assertExactTypeEqual('@=', token.ATEQUAL)

        self.assertExactTypeEqual('a**2+b**2==c**2',
                                  NAME, token.DOUBLESTAR, NUMBER,
                                  token.PLUS,
                                  NAME, token.DOUBLESTAR, NUMBER,
                                  token.EQEQUAL,
                                  NAME, token.DOUBLESTAR, NUMBER)
        self.assertExactTypeEqual('{1, 2, 3}',
                                  token.LBRACE,
                                  token.NUMBER, token.COMMA,
                                  token.NUMBER, token.COMMA,
                                  token.NUMBER,
                                  token.RBRACE)
        self.assertExactTypeEqual('^(x & 0x1)',
                                  token.CIRCUMFLEX,
                                  token.LPAR,
                                  token.NAME, token.AMPER, token.NUMBER,
                                  token.RPAR)

    eleza test_pathological_trailing_whitespace(self):
        # See http://bugs.python.org/issue16152
        self.assertExactTypeEqual('@          ', token.AT)


kundi UntokenizeTest(TestCase):

    eleza test_bad_input_order(self):
        # ashiria ikiwa previous row
        u = Untokenizer()
        u.prev_row = 2
        u.prev_col = 2
        ukijumuisha self.assertRaises(ValueError) kama cm:
            u.add_whitespace((1,3))
        self.assertEqual(cm.exception.args[0],
                'start (1,3) precedes previous end (2,2)')
        # ashiria ikiwa previous column kwenye row
        self.assertRaises(ValueError, u.add_whitespace, (2,1))

    eleza test_backslash_continuation(self):
        # The problem ni that <whitespace>\<newline> leaves no token
        u = Untokenizer()
        u.prev_row = 1
        u.prev_col =  1
        u.tokens = []
        u.add_whitespace((2, 0))
        self.assertEqual(u.tokens, ['\\\n'])
        u.prev_row = 2
        u.add_whitespace((4, 4))
        self.assertEqual(u.tokens, ['\\\n', '\\\n\\\n', '    '])
        TestRoundtrip.check_roundtrip(self, 'a\n  b\n    c\n  \\\n  c\n')

    eleza test_iter_compat(self):
        u = Untokenizer()
        token = (NAME, 'Hello')
        tokens = [(ENCODING, 'utf-8'), token]
        u.compat(token, iter([]))
        self.assertEqual(u.tokens, ["Hello "])
        u = Untokenizer()
        self.assertEqual(u.untokenize(iter([token])), 'Hello ')
        u = Untokenizer()
        self.assertEqual(u.untokenize(iter(tokens)), 'Hello ')
        self.assertEqual(u.encoding, 'utf-8')
        self.assertEqual(untokenize(iter(tokens)), b'Hello ')


kundi TestRoundtrip(TestCase):

    eleza check_roundtrip(self, f):
        """
        Test roundtrip kila `untokenize`. `f` ni an open file ama a string.
        The source code kwenye f ni tokenized to both 5- na 2-tuples.
        Both sequences are converted back to source code via
        tokenize.untokenize(), na the latter tokenized again to 2-tuples.
        The test fails ikiwa the 3 pair tokenizations do sio match.

        When untokenize bugs are fixed, untokenize ukijumuisha 5-tuples should
        reproduce code that does sio contain a backslash continuation
        following spaces.  A proper test should test this.
        """
        # Get source code na original tokenizations
        ikiwa isinstance(f, str):
            code = f.encode('utf-8')
        isipokua:
            code = f.read()
            f.close()
        readline = iter(code.splitlines(keepends=Kweli)).__next__
        tokens5 = list(tokenize(readline))
        tokens2 = [tok[:2] kila tok kwenye tokens5]
        # Reproduce tokens2 kutoka pairs
        bytes_from2 = untokenize(tokens2)
        readline2 = iter(bytes_from2.splitlines(keepends=Kweli)).__next__
        tokens2_from2 = [tok[:2] kila tok kwenye tokenize(readline2)]
        self.assertEqual(tokens2_from2, tokens2)
        # Reproduce tokens2 kutoka 5-tuples
        bytes_from5 = untokenize(tokens5)
        readline5 = iter(bytes_from5.splitlines(keepends=Kweli)).__next__
        tokens2_from5 = [tok[:2] kila tok kwenye tokenize(readline5)]
        self.assertEqual(tokens2_from5, tokens2)

    eleza test_roundtrip(self):
        # There are some standard formatting practices that are easy to get right.

        self.check_roundtrip("ikiwa x == 1:\n"
                             "    andika(x)\n")
        self.check_roundtrip("# This ni a comment\n"
                             "# This also\n")

        # Some people use different formatting conventions, which makes
        # untokenize a little trickier. Note that this test involves trailing
        # whitespace after the colon. Note that we use hex escapes to make the
        # two trailing blanks apparent kwenye the expected output.

        self.check_roundtrip("ikiwa x == 1 : \n"
                             "  andika(x)\n")
        fn = support.findfile("tokenize_tests.txt")
        ukijumuisha open(fn, 'rb') kama f:
            self.check_roundtrip(f)
        self.check_roundtrip("ikiwa x == 1:\n"
                             "    # A comment by itself.\n"
                             "    andika(x) # Comment here, too.\n"
                             "    # Another comment.\n"
                             "after_ikiwa = Kweli\n")
        self.check_roundtrip("ikiwa (x # The comments need to go kwenye the right place\n"
                             "    == 1):\n"
                             "    andika('x==1')\n")
        self.check_roundtrip("kundi Test: # A comment here\n"
                             "  # A comment ukijumuisha weird indent\n"
                             "  after_com = 5\n"
                             "  eleza x(m): rudisha m*5 # a one liner\n"
                             "  eleza y(m): # A whitespace after the colon\n"
                             "     rudisha y*4 # 3-space indent\n")

        # Some error-handling code
        self.check_roundtrip("jaribu: agiza somemodule\n"
                             "tatizo ImportError: # comment\n"
                             "    andika('Can sio import' # comment2\n)"
                             "isipokua:   andika('Loaded')\n")

    eleza test_continuation(self):
        # Balancing continuation
        self.check_roundtrip("a = (3,4, \n"
                             "5,6)\n"
                             "y = [3, 4,\n"
                             "5]\n"
                             "z = {'a': 5,\n"
                             "'b':15, 'c':Kweli}\n"
                             "x = len(y) + 5 - a[\n"
                             "3] - a[2]\n"
                             "+ len(z) - z[\n"
                             "'b']\n")

    eleza test_backslash_continuation(self):
        # Backslash means line continuation, tatizo kila comments
        self.check_roundtrip("x=1+\\\n"
                             "1\n"
                             "# This ni a comment\\\n"
                             "# This also\n")
        self.check_roundtrip("# Comment \\\n"
                             "x = 0")

    eleza test_string_concatenation(self):
        # Two string literals on the same line
        self.check_roundtrip("'' ''")

    eleza test_random_files(self):
        # Test roundtrip on random python modules.
        # pita the '-ucpu' option to process the full directory.

        agiza glob, random
        fn = support.findfile("tokenize_tests.txt")
        tempdir = os.path.dirname(fn) ama os.curdir
        testfiles = glob.glob(os.path.join(tempdir, "test*.py"))

        # Tokenize ni broken on test_pep3131.py because regular expressions are
        # broken on the obscure unicode identifiers kwenye it. *sigh*
        # With roundtrip extended to test the 5-tuple mode of untokenize,
        # 7 more testfiles fail.  Remove them also until the failure ni diagnosed.

        testfiles.remove(os.path.join(tempdir, "test_unicode_identifiers.py"))
        kila f kwenye ('buffer', 'builtin', 'fileio', 'inspect', 'os', 'platform', 'sys'):
            testfiles.remove(os.path.join(tempdir, "test_%s.py") % f)

        ikiwa sio support.is_resource_enabled("cpu"):
            testfiles = random.sample(testfiles, 10)

        kila testfile kwenye testfiles:
            ikiwa support.verbose >= 2:
                andika('tokenize', testfile)
            ukijumuisha open(testfile, 'rb') kama f:
                ukijumuisha self.subTest(file=testfile):
                    self.check_roundtrip(f)


    eleza roundtrip(self, code):
        ikiwa isinstance(code, str):
            code = code.encode('utf-8')
        rudisha untokenize(tokenize(BytesIO(code).readline)).decode('utf-8')

    eleza test_indentation_semantics_retained(self):
        """
        Ensure that although whitespace might be mutated kwenye a roundtrip,
        the semantic meaning of the indentation remains consistent.
        """
        code = "ikiwa Uongo:\n\tx=3\n\tx=3\n"
        codelines = self.roundtrip(code).split('\n')
        self.assertEqual(codelines[1], codelines[2])
        self.check_roundtrip(code)


ikiwa __name__ == "__main__":
    unittest.main()
