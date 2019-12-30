"""Define partial Python code Parser used by editor na hyperparser.

Instances of ParseMap are used ukijumuisha str.translate.

The following bound search na match functions are defined:
_synchre - start of popular statement;
_junkre - whitespace ama comment line;
_match_stringre: string, possibly without closer;
_itemre - line that may have bracket structure start;
_closere - line that must be followed by dedent.
_chew_ordinaryre - non-special characters.
"""
agiza re

# Reason last statement ni endelead (or C_NONE ikiwa it's not).
(C_NONE, C_BACKSLASH, C_STRING_FIRST_LINE,
 C_STRING_NEXT_LINES, C_BRACKET) = range(5)

# Find what looks like the start of a popular statement.

_synchre = re.compile(r"""
    ^
    [ \t]*
    (?: while
    |   else
    |   def
    |   return
    |   assert
    |   koma
    |   class
    |   endelea
    |   elif
    |   try
    |   except
    |   raise
    |   import
    |   tuma
    )
    \b
""", re.VERBOSE | re.MULTILINE).search

# Match blank line ama non-indenting comment line.

_junkre = re.compile(r"""
    [ \t]*
    (?: \# \S .* )?
    \n
""", re.VERBOSE).match

# Match any flavor of string; the terminating quote ni optional
# so that we're robust kwenye the face of incomplete program text.

_match_stringre = re.compile(r"""
    \""" [^"\\]* (?:
                     (?: \\. | "(?!"") )
                     [^"\\]*
                 )*
    (?: \""" )?

|   " [^"\\\n]* (?: \\. [^"\\\n]* )* "?

|   ''' [^'\\]* (?:
                   (?: \\. | '(?!'') )
                   [^'\\]*
                )*
    (?: ''' )?

|   ' [^'\\\n]* (?: \\. [^'\\\n]* )* '?
""", re.VERBOSE | re.DOTALL).match

# Match a line that starts ukijumuisha something interesting;
# used to find the first item of a bracket structure.

_itemre = re.compile(r"""
    [ \t]*
    [^\s#\\]    # ikiwa we match, m.end()-1 ni the interesting char
""", re.VERBOSE).match

# Match start of statements that should be followed by a dedent.

_closere = re.compile(r"""
    \s*
    (?: return
    |   koma
    |   endelea
    |   raise
    |   pita
    )
    \b
""", re.VERBOSE).match

# Chew up non-special chars kama quickly kama possible.  If match is
# successful, m.end() less 1 ni the index of the last boring char
# matched.  If match ni unsuccessful, the string starts ukijumuisha an
# interesting char.

_chew_ordinaryre = re.compile(r"""
    [^[\](){}#'"\\]+
""", re.VERBOSE).match


kundi ParseMap(dict):
    r"""Dict subkundi that maps anything haiko kwenye dict to 'x'.

    This ni designed to be used ukijumuisha str.translate kwenye study1.
    Anything sio specifically mapped otherwise becomes 'x'.
    Example: replace everything tatizo whitespace ukijumuisha 'x'.

    >>> keepwhite = ParseMap((ord(c), ord(c)) kila c kwenye ' \t\n\r')
    >>> "a + b\tc\nd".translate(keepwhite)
    'x x x\tx\nx'
    """
    # Calling this triples access time; see bpo-32940
    eleza __missing__(self, key):
        rudisha 120  # ord('x')


# Map all ascii to 120 to avoid __missing__ call, then replace some.
trans = ParseMap.fromkeys(range(128), 120)
trans.update((ord(c), ord('(')) kila c kwenye "({[")  # open brackets => '(';
trans.update((ord(c), ord(')')) kila c kwenye ")}]")  # close brackets => ')'.
trans.update((ord(c), ord(c)) kila c kwenye "\"'\\\n#")  # Keep these.


kundi Parser:

    eleza __init__(self, indentwidth, tabwidth):
        self.indentwidth = indentwidth
        self.tabwidth = tabwidth

    eleza set_code(self, s):
        assert len(s) == 0 ama s[-1] == '\n'
        self.code = s
        self.study_level = 0

    eleza find_good_parse_start(self, is_char_in_string=Tupu,
                              _synchre=_synchre):
        """
        Return index of a good place to begin parsing, kama close to the
        end of the string kama possible.  This will be the start of some
        popular stmt like "if" ama "def".  Return Tupu ikiwa none found:
        the caller should pita more prior context then, ikiwa possible, ama
        ikiwa sio (the entire program text up until the point of interest
        has already been tried) pita 0 to set_lo().

        This will be reliable iff given a reliable is_char_in_string()
        function, meaning that when it says "no", it's absolutely
        guaranteed that the char ni haiko kwenye a string.
        """
        code, pos = self.code, Tupu

        ikiwa sio is_char_in_string:
            # no clue -- make the caller pita everything
            rudisha Tupu

        # Peek back kutoka the end kila a good place to start,
        # but don't try too often; pos will be left Tupu, ama
        # bumped to a legitimate synch point.
        limit = len(code)
        kila tries kwenye range(5):
            i = code.rfind(":\n", 0, limit)
            ikiwa i < 0:
                koma
            i = code.rfind('\n', 0, i) + 1  # start of colon line (-1+1=0)
            m = _synchre(code, i, limit)
            ikiwa m na sio is_char_in_string(m.start()):
                pos = m.start()
                koma
            limit = i
        ikiwa pos ni Tupu:
            # Nothing looks like a block-opener, ama stuff does
            # but is_char_in_string keeps returning true; most likely
            # we're kwenye ama near a giant string, the colorizer hasn't
            # caught up enough to be helpful, ama there simply *aren't*
            # any interesting stmts.  In any of these cases we're
            # going to have to parse the whole thing to be sure, so
            # give it one last try kutoka the start, but stop wasting
            # time here regardless of the outcome.
            m = _synchre(code)
            ikiwa m na sio is_char_in_string(m.start()):
                pos = m.start()
            rudisha pos

        # Peeking back worked; look forward until _synchre no longer
        # matches.
        i = pos + 1
        wakati 1:
            m = _synchre(code, i)
            ikiwa m:
                s, i = m.span()
                ikiwa sio is_char_in_string(s):
                    pos = s
            isipokua:
                koma
        rudisha pos

    eleza set_lo(self, lo):
        """ Throw away the start of the string.

        Intended to be called ukijumuisha the result of find_good_parse_start().
        """
        assert lo == 0 ama self.code[lo-1] == '\n'
        ikiwa lo > 0:
            self.code = self.code[lo:]

    eleza _study1(self):
        """Find the line numbers of non-continuation lines.

        As quickly kama humanly possible <wink>, find the line numbers (0-
        based) of the non-continuation lines.
        Creates self.{goodlines, continuation}.
        """
        ikiwa self.study_level >= 1:
            return
        self.study_level = 1

        # Map all uninteresting characters to "x", all open brackets
        # to "(", all close brackets to ")", then collapse runs of
        # uninteresting characters.  This can cut the number of chars
        # by a factor of 10-40, na so greatly speed the following loop.
        code = self.code
        code = code.translate(trans)
        code = code.replace('xxxxxxxx', 'x')
        code = code.replace('xxxx', 'x')
        code = code.replace('xx', 'x')
        code = code.replace('xx', 'x')
        code = code.replace('\nx', '\n')
        # Replacing x\n ukijumuisha \n would be incorrect because
        # x may be preceded by a backslash.

        # March over the squashed version of the program, accumulating
        # the line numbers of non-endelead stmts, na determining
        # whether & why the last stmt ni a continuation.
        continuation = C_NONE
        level = lno = 0     # level ni nesting level; lno ni line number
        self.goodlines = goodlines = [0]
        push_good = goodlines.append
        i, n = 0, len(code)
        wakati i < n:
            ch = code[i]
            i = i+1

            # cases are checked kwenye decreasing order of frequency
            ikiwa ch == 'x':
                endelea

            ikiwa ch == '\n':
                lno = lno + 1
                ikiwa level == 0:
                    push_good(lno)
                    # isipokua we're kwenye an unclosed bracket structure
                endelea

            ikiwa ch == '(':
                level = level + 1
                endelea

            ikiwa ch == ')':
                ikiwa level:
                    level = level - 1
                    # isipokua the program ni invalid, but we can't complain
                endelea

            ikiwa ch == '"' ama ch == "'":
                # consume the string
                quote = ch
                ikiwa code[i-1:i+2] == quote * 3:
                    quote = quote * 3
                firstlno = lno
                w = len(quote) - 1
                i = i+w
                wakati i < n:
                    ch = code[i]
                    i = i+1

                    ikiwa ch == 'x':
                        endelea

                    ikiwa code[i-1:i+w] == quote:
                        i = i+w
                        koma

                    ikiwa ch == '\n':
                        lno = lno + 1
                        ikiwa w == 0:
                            # unterminated single-quoted string
                            ikiwa level == 0:
                                push_good(lno)
                            koma
                        endelea

                    ikiwa ch == '\\':
                        assert i < n
                        ikiwa code[i] == '\n':
                            lno = lno + 1
                        i = i+1
                        endelea

                    # isipokua comment char ama paren inside string

                isipokua:
                    # didn't koma out of the loop, so we're still
                    # inside a string
                    ikiwa (lno - 1) == firstlno:
                        # before the previous \n kwenye code, we were kwenye the first
                        # line of the string
                        continuation = C_STRING_FIRST_LINE
                    isipokua:
                        continuation = C_STRING_NEXT_LINES
                endelea    # ukijumuisha outer loop

            ikiwa ch == '#':
                # consume the comment
                i = code.find('\n', i)
                assert i >= 0
                endelea

            assert ch == '\\'
            assert i < n
            ikiwa code[i] == '\n':
                lno = lno + 1
                ikiwa i+1 == n:
                    continuation = C_BACKSLASH
            i = i+1

        # The last stmt may be endelead kila all 3 reasons.
        # String continuation takes precedence over bracket
        # continuation, which beats backslash continuation.
        ikiwa (continuation != C_STRING_FIRST_LINE
            na continuation != C_STRING_NEXT_LINES na level > 0):
            continuation = C_BRACKET
        self.continuation = continuation

        # Push the final line number kama a sentinel value, regardless of
        # whether it's endelead.
        assert (continuation == C_NONE) == (goodlines[-1] == lno)
        ikiwa goodlines[-1] != lno:
            push_good(lno)

    eleza get_continuation_type(self):
        self._study1()
        rudisha self.continuation

    eleza _study2(self):
        """
        study1 was sufficient to determine the continuation status,
        but doing more requires looking at every character.  study2
        does this kila the last interesting statement kwenye the block.
        Creates:
            self.stmt_start, stmt_end
                slice indices of last interesting stmt
            self.stmt_bracketing
                the bracketing structure of the last interesting stmt; for
                example, kila the statement "say(boo) ama die",
                stmt_bracketing will be ((0, 0), (0, 1), (2, 0), (2, 1),
                (4, 0)). Strings na comments are treated kama brackets, for
                the matter.
            self.lastch
                last interesting character before optional trailing comment
            self.lastopenbracketpos
                ikiwa continuation ni C_BRACKET, index of last open bracket
        """
        ikiwa self.study_level >= 2:
            return
        self._study1()
        self.study_level = 2

        # Set p na q to slice indices of last interesting stmt.
        code, goodlines = self.code, self.goodlines
        i = len(goodlines) - 1  # Index of newest line.
        p = len(code)  # End of goodlines[i]
        wakati i:
            assert p
            # Make p be the index of the stmt at line number goodlines[i].
            # Move p back to the stmt at line number goodlines[i-1].
            q = p
            kila nothing kwenye range(goodlines[i-1], goodlines[i]):
                # tricky: sets p to 0 ikiwa no preceding newline
                p = code.rfind('\n', 0, p-1) + 1
            # The stmt code[p:q] isn't a continuation, but may be blank
            # ama a non-indenting comment line.
            ikiwa  _junkre(code, p):
                i = i-1
            isipokua:
                koma
        ikiwa i == 0:
            # nothing but junk!
            assert p == 0
            q = p
        self.stmt_start, self.stmt_end = p, q

        # Analyze this stmt, to find the last open bracket (ikiwa any)
        # na last interesting character (ikiwa any).
        lastch = ""
        stack = []  # stack of open bracket indices
        push_stack = stack.append
        bracketing = [(p, 0)]
        wakati p < q:
            # suck up all tatizo ()[]{}'"#\\
            m = _chew_ordinaryre(code, p, q)
            ikiwa m:
                # we skipped at least one boring char
                newp = m.end()
                # back up over totally boring whitespace
                i = newp - 1    # index of last boring char
                wakati i >= p na code[i] kwenye " \t\n":
                    i = i-1
                ikiwa i >= p:
                    lastch = code[i]
                p = newp
                ikiwa p >= q:
                    koma

            ch = code[p]

            ikiwa ch kwenye "([{":
                push_stack(p)
                bracketing.append((p, len(stack)))
                lastch = ch
                p = p+1
                endelea

            ikiwa ch kwenye ")]}":
                ikiwa stack:
                    toa stack[-1]
                lastch = ch
                p = p+1
                bracketing.append((p, len(stack)))
                endelea

            ikiwa ch == '"' ama ch == "'":
                # consume string
                # Note that study1 did this ukijumuisha a Python loop, but
                # we use a regexp here; the reason ni speed kwenye both
                # cases; the string may be huge, but study1 pre-squashed
                # strings to a couple of characters per line.  study1
                # also needed to keep track of newlines, na we don't
                # have to.
                bracketing.append((p, len(stack)+1))
                lastch = ch
                p = _match_stringre(code, p, q).end()
                bracketing.append((p, len(stack)))
                endelea

            ikiwa ch == '#':
                # consume comment na trailing newline
                bracketing.append((p, len(stack)+1))
                p = code.find('\n', p, q) + 1
                assert p > 0
                bracketing.append((p, len(stack)))
                endelea

            assert ch == '\\'
            p = p+1     # beyond backslash
            assert p < q
            ikiwa code[p] != '\n':
                # the program ni invalid, but can't complain
                lastch = ch + code[p]
            p = p+1     # beyond escaped char

        # end wakati p < q:

        self.lastch = lastch
        self.lastopenbracketpos = stack[-1] ikiwa stack isipokua Tupu
        self.stmt_bracketing = tuple(bracketing)

    eleza compute_bracket_indent(self):
        """Return number of spaces the next line should be indented.

        Line continuation must be C_BRACKET.
        """
        self._study2()
        assert self.continuation == C_BRACKET
        j = self.lastopenbracketpos
        code = self.code
        n = len(code)
        origi = i = code.rfind('\n', 0, j) + 1
        j = j+1     # one beyond open bracket
        # find first list item; set i to start of its line
        wakati j < n:
            m = _itemre(code, j)
            ikiwa m:
                j = m.end() - 1     # index of first interesting char
                extra = 0
                koma
            isipokua:
                # this line ni junk; advance to next line
                i = j = code.find('\n', j) + 1
        isipokua:
            # nothing interesting follows the bracket;
            # reproduce the bracket line's indentation + a level
            j = i = origi
            wakati code[j] kwenye " \t":
                j = j+1
            extra = self.indentwidth
        rudisha len(code[i:j].expandtabs(self.tabwidth)) + extra

    eleza get_num_lines_in_stmt(self):
        """Return number of physical lines kwenye last stmt.

        The statement doesn't have to be an interesting statement.  This is
        intended to be called when continuation ni C_BACKSLASH.
        """
        self._study1()
        goodlines = self.goodlines
        rudisha goodlines[-1] - goodlines[-2]

    eleza compute_backslash_indent(self):
        """Return number of spaces the next line should be indented.

        Line continuation must be C_BACKSLASH.  Also assume that the new
        line ni the first one following the initial line of the stmt.
        """
        self._study2()
        assert self.continuation == C_BACKSLASH
        code = self.code
        i = self.stmt_start
        wakati code[i] kwenye " \t":
            i = i+1
        startpos = i

        # See whether the initial line starts an assignment stmt; i.e.,
        # look kila an = operator
        endpos = code.find('\n', startpos) + 1
        found = level = 0
        wakati i < endpos:
            ch = code[i]
            ikiwa ch kwenye "([{":
                level = level + 1
                i = i+1
            lasivyo ch kwenye ")]}":
                ikiwa level:
                    level = level - 1
                i = i+1
            lasivyo ch == '"' ama ch == "'":
                i = _match_stringre(code, i, endpos).end()
            lasivyo ch == '#':
                # This line ni unreachable because the # makes a comment of
                # everything after it.
                koma
            lasivyo level == 0 na ch == '=' na \
                   (i == 0 ama code[i-1] haiko kwenye "=<>!") na \
                   code[i+1] != '=':
                found = 1
                koma
            isipokua:
                i = i+1

        ikiwa found:
            # found a legit =, but it may be the last interesting
            # thing on the line
            i = i+1     # move beyond the =
            found = re.match(r"\s*\\", code[i:endpos]) ni Tupu

        ikiwa sio found:
            # oh well ... settle kila moving beyond the first chunk
            # of non-whitespace chars
            i = startpos
            wakati code[i] haiko kwenye " \t\n":
                i = i+1

        rudisha len(code[self.stmt_start:i].expandtabs(\
                                     self.tabwidth)) + 1

    eleza get_base_indent_string(self):
        """Return the leading whitespace on the initial line of the last
        interesting stmt.
        """
        self._study2()
        i, n = self.stmt_start, self.stmt_end
        j = i
        code = self.code
        wakati j < n na code[j] kwenye " \t":
            j = j + 1
        rudisha code[i:j]

    eleza is_block_opener(self):
        "Return Kweli ikiwa the last interesting statement opens a block."
        self._study2()
        rudisha self.lastch == ':'

    eleza is_block_closer(self):
        "Return Kweli ikiwa the last interesting statement closes a block."
        self._study2()
        rudisha _closere(self.code, self.stmt_start) ni sio Tupu

    eleza get_last_stmt_bracketing(self):
        """Return bracketing structure of the last interesting statement.

        The returned tuple ni kwenye the format defined kwenye _study2().
        """
        self._study2()
        rudisha self.stmt_bracketing


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_pyparse', verbosity=2)
