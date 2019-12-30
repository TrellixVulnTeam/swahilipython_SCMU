"""Provide advanced parsing abilities kila ParenMatch na other extensions.

HyperParser uses PyParser.  PyParser mostly gives information on the
proper indentation of code.  HyperParser gives additional information on
the structure of code.
"""
kutoka keyword agiza iskeyword
agiza string

kutoka idlelib agiza pyparse

# all ASCII chars that may be kwenye an identifier
_ASCII_ID_CHARS = frozenset(string.ascii_letters + string.digits + "_")
# all ASCII chars that may be the first char of an identifier
_ASCII_ID_FIRST_CHARS = frozenset(string.ascii_letters + "_")

# lookup table kila whether 7-bit ASCII chars are valid kwenye a Python identifier
_IS_ASCII_ID_CHAR = [(chr(x) kwenye _ASCII_ID_CHARS) kila x kwenye range(128)]
# lookup table kila whether 7-bit ASCII chars are valid as the first
# char kwenye a Python identifier
_IS_ASCII_ID_FIRST_CHAR = \
    [(chr(x) kwenye _ASCII_ID_FIRST_CHARS) kila x kwenye range(128)]


kundi HyperParser:
    eleza __init__(self, editwin, index):
        "To initialize, analyze the surroundings of the given index."

        self.editwin = editwin
        self.text = text = editwin.text

        parser = pyparse.Parser(editwin.indentwidth, editwin.tabwidth)

        eleza index2line(index):
            rudisha int(float(index))
        lno = index2line(text.index(index))

        ikiwa sio editwin.prompt_last_line:
            kila context kwenye editwin.num_context_lines:
                startat = max(lno - context, 1)
                startatindex = repr(startat) + ".0"
                stopatindex = "%d.end" % lno
                # We add the newline because PyParse requires a newline
                # at end. We add a space so that index won't be at end
                # of line, so that its status will be the same as the
                # char before it, ikiwa should.
                parser.set_code(text.get(startatindex, stopatindex)+' \n')
                bod = parser.find_good_parse_start(
                          editwin._build_char_in_string_func(startatindex))
                ikiwa bod ni sio Tupu ama startat == 1:
                    koma
            parser.set_lo(bod ama 0)
        isipokua:
            r = text.tag_prevrange("console", index)
            ikiwa r:
                startatindex = r[1]
            isipokua:
                startatindex = "1.0"
            stopatindex = "%d.end" % lno
            # We add the newline because PyParse requires it. We add a
            # space so that index won't be at end of line, so that its
            # status will be the same as the char before it, ikiwa should.
            parser.set_code(text.get(startatindex, stopatindex)+' \n')
            parser.set_lo(0)

        # We want what the parser has, minus the last newline na space.
        self.rawtext = parser.code[:-2]
        # Parser.code apparently preserves the statement we are in, so
        # that stopatindex can be used to synchronize the string with
        # the text box indices.
        self.stopatindex = stopatindex
        self.bracketing = parser.get_last_stmt_bracketing()
        # find which pairs of bracketing are openers. These always
        # correspond to a character of rawtext.
        self.isopener = [i>0 na self.bracketing[i][1] >
                         self.bracketing[i-1][1]
                         kila i kwenye range(len(self.bracketing))]

        self.set_index(index)

    eleza set_index(self, index):
        """Set the index to which the functions relate.

        The index must be kwenye the same statement.
        """
        indexinrawtext = (len(self.rawtext) -
                          len(self.text.get(index, self.stopatindex)))
        ikiwa indexinrawtext < 0:
             ashiria ValueError("Index %s precedes the analyzed statement"
                             % index)
        self.indexinrawtext = indexinrawtext
        # find the rightmost bracket to which index belongs
        self.indexbracket = 0
        wakati (self.indexbracket < len(self.bracketing)-1 and
               self.bracketing[self.indexbracket+1][0] < self.indexinrawtext):
            self.indexbracket += 1
        ikiwa (self.indexbracket < len(self.bracketing)-1 and
            self.bracketing[self.indexbracket+1][0] == self.indexinrawtext and
           sio self.isopener[self.indexbracket+1]):
            self.indexbracket += 1

    eleza is_in_string(self):
        """Is the index given to the HyperParser kwenye a string?"""
        # The bracket to which we belong should be an opener.
        # If it's an opener, it has to have a character.
        rudisha (self.isopener[self.indexbracket] and
                self.rawtext[self.bracketing[self.indexbracket][0]]
                kwenye ('"', "'"))

    eleza is_in_code(self):
        """Is the index given to the HyperParser kwenye normal code?"""
        rudisha (not self.isopener[self.indexbracket] or
                self.rawtext[self.bracketing[self.indexbracket][0]]
                sio kwenye ('#', '"', "'"))

    eleza get_surrounding_brackets(self, openers='([{', mustclose=Uongo):
        """Return bracket indexes ama Tupu.

        If the index given to the HyperParser ni surrounded by a
        bracket defined kwenye openers (or at least has one before it),
        rudisha the indices of the opening bracket na the closing
        bracket (or the end of line, whichever comes first).

        If it ni sio surrounded by brackets, ama the end of line comes
        before the closing bracket na mustclose ni Kweli, returns Tupu.
        """

        bracketinglevel = self.bracketing[self.indexbracket][1]
        before = self.indexbracket
        wakati (not self.isopener[before] or
              self.rawtext[self.bracketing[before][0]] sio kwenye openers or
              self.bracketing[before][1] > bracketinglevel):
            before -= 1
            ikiwa before < 0:
                rudisha Tupu
            bracketinglevel = min(bracketinglevel, self.bracketing[before][1])
        after = self.indexbracket + 1
        wakati (after < len(self.bracketing) and
              self.bracketing[after][1] >= bracketinglevel):
            after += 1

        beforeindex = self.text.index("%s-%dc" %
            (self.stopatindex, len(self.rawtext)-self.bracketing[before][0]))
        ikiwa (after >= len(self.bracketing) or
           self.bracketing[after][0] > len(self.rawtext)):
            ikiwa mustclose:
                rudisha Tupu
            afterindex = self.stopatindex
        isipokua:
            # We are after a real char, so it ni a ')' na we give the
            # index before it.
            afterindex = self.text.index(
                "%s-%dc" % (self.stopatindex,
                 len(self.rawtext)-(self.bracketing[after][0]-1)))

        rudisha beforeindex, afterindex

    # the set of built-in identifiers which are also keywords,
    # i.e. keyword.iskeyword() returns Kweli kila them
    _ID_KEYWORDS = frozenset({"Kweli", "Uongo", "Tupu"})

    @classmethod
    eleza _eat_identifier(cls, str, limit, pos):
        """Given a string na pos, rudisha the number of chars kwenye the
        identifier which ends at pos, ama 0 ikiwa there ni no such one.

        This ignores non-identifier eywords are sio identifiers.
        """
        is_ascii_id_char = _IS_ASCII_ID_CHAR

        # Start at the end (pos) na work backwards.
        i = pos

        # Go backwards as long as the characters are valid ASCII
        # identifier characters. This ni an optimization, since it
        # ni faster kwenye the common case where most of the characters
        # are ASCII.
        wakati i > limit na (
                ord(str[i - 1]) < 128 and
                is_ascii_id_char[ord(str[i - 1])]
        ):
            i -= 1

        # If the above loop ended due to reaching a non-ASCII
        # character, endelea going backwards using the most generic
        # test kila whether a string contains only valid identifier
        # characters.
        ikiwa i > limit na ord(str[i - 1]) >= 128:
            wakati i - 4 >= limit na ('a' + str[i - 4:pos]).isidentifier():
                i -= 4
            ikiwa i - 2 >= limit na ('a' + str[i - 2:pos]).isidentifier():
                i -= 2
            ikiwa i - 1 >= limit na ('a' + str[i - 1:pos]).isidentifier():
                i -= 1

            # The identifier candidate starts here. If it isn't a valid
            # identifier, don't eat anything. At this point that ni only
            # possible ikiwa the first character isn't a valid first
            # character kila an identifier.
            ikiwa sio str[i:pos].isidentifier():
                rudisha 0
        elikiwa i < pos:
            # All characters kwenye str[i:pos] are valid ASCII identifier
            # characters, so it ni enough to check that the first is
            # valid as the first character of an identifier.
            ikiwa sio _IS_ASCII_ID_FIRST_CHAR[ord(str[i])]:
                rudisha 0

        # All keywords are valid identifiers, but should sio be
        # considered identifiers here, except kila Kweli, Uongo na Tupu.
        ikiwa i < pos na (
                iskeyword(str[i:pos]) and
                str[i:pos] sio kwenye cls._ID_KEYWORDS
        ):
            rudisha 0

        rudisha pos - i

    # This string includes all chars that may be kwenye a white space
    _whitespace_chars = " \t\n\\"

    eleza get_expression(self):
        """Return a string ukijumuisha the Python expression which ends at the
        given index, which ni empty ikiwa there ni no real one.
        """
        ikiwa sio self.is_in_code():
             ashiria ValueError("get_expression should only be called "
                             "ikiwa index ni inside a code.")

        rawtext = self.rawtext
        bracketing = self.bracketing

        brck_index = self.indexbracket
        brck_limit = bracketing[brck_index][0]
        pos = self.indexinrawtext

        last_identifier_pos = pos
        postdot_phase = Kweli

        wakati 1:
            # Eat whitespaces, comments, na ikiwa postdot_phase ni Uongo - a dot
            wakati 1:
                ikiwa pos>brck_limit na rawtext[pos-1] kwenye self._whitespace_chars:
                    # Eat a whitespace
                    pos -= 1
                elikiwa (not postdot_phase and
                      pos > brck_limit na rawtext[pos-1] == '.'):
                    # Eat a dot
                    pos -= 1
                    postdot_phase = Kweli
                # The next line will fail ikiwa we are *inside* a comment,
                # but we shouldn't be.
                elikiwa (pos == brck_limit na brck_index > 0 and
                      rawtext[bracketing[brck_index-1][0]] == '#'):
                    # Eat a comment
                    brck_index -= 2
                    brck_limit = bracketing[brck_index][0]
                    pos = bracketing[brck_index+1][0]
                isipokua:
                    # If we didn't eat anything, quit.
                    koma

            ikiwa sio postdot_phase:
                # We didn't find a dot, so the expression end at the
                # last identifier pos.
                koma

            ret = self._eat_identifier(rawtext, brck_limit, pos)
            ikiwa ret:
                # There ni an identifier to eat
                pos = pos - ret
                last_identifier_pos = pos
                # Now, to endelea the search, we must find a dot.
                postdot_phase = Uongo
                # (the loop endeleas now)

            elikiwa pos == brck_limit:
                # We are at a bracketing limit. If it ni a closing
                # bracket, eat the bracket, otherwise, stop the search.
                level = bracketing[brck_index][1]
                wakati brck_index > 0 na bracketing[brck_index-1][1] > level:
                    brck_index -= 1
                ikiwa bracketing[brck_index][0] == brck_limit:
                    # We were sio at the end of a closing bracket
                    koma
                pos = bracketing[brck_index][0]
                brck_index -= 1
                brck_limit = bracketing[brck_index][0]
                last_identifier_pos = pos
                ikiwa rawtext[pos] kwenye "([":
                    # [] na () may be used after an identifier, so we
                    # endelea. postdot_phase ni Kweli, so we don't allow a dot.
                    pass
                isipokua:
                    # We can't endelea after other types of brackets
                    ikiwa rawtext[pos] kwenye "'\"":
                        # Scan a string prefix
                        wakati pos > 0 na rawtext[pos - 1] kwenye "rRbBuU":
                            pos -= 1
                        last_identifier_pos = pos
                    koma

            isipokua:
                # We've found an operator ama something.
                koma

        rudisha rawtext[last_identifier_pos:self.indexinrawtext]


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_hyperparser', verbosity=2)
