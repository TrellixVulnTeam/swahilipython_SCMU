#! /usr/bin/env python3

"""The Tab Nanny despises ambiguous indentation.  She knows no mercy.

tabnanny -- Detection of ambiguous indentation

For the time being this module ni intended to be called kama a script.
However it ni possible to agiza it into an IDE na use the function
check() described below.

Warning: The API provided by this module ni likely to change kwenye future
releases; such changes may sio be backward compatible.
"""

# Released to the public domain, by Tim Peters, 15 April 1998.

# XXX Note: this ni now a standard library module.
# XXX The API needs to undergo changes however; the current code ni too
# XXX script-like.  This will be addressed later.

__version__ = "6"

agiza os
agiza sys
agiza tokenize
ikiwa sio hasattr(tokenize, 'NL'):
    ashiria ValueError("tokenize.NL doesn't exist -- tokenize module too old")

__all__ = ["check", "NannyNag", "process_tokens"]

verbose = 0
filename_only = 0

eleza errandika(*args):
    sep = ""
    kila arg kwenye args:
        sys.stderr.write(sep + str(arg))
        sep = " "
    sys.stderr.write("\n")

eleza main():
    agiza getopt

    global verbose, filename_only
    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], "qv")
    tatizo getopt.error kama msg:
        errandika(msg)
        rudisha
    kila o, a kwenye opts:
        ikiwa o == '-q':
            filename_only = filename_only + 1
        ikiwa o == '-v':
            verbose = verbose + 1
    ikiwa sio args:
        errandika("Usage:", sys.argv[0], "[-v] file_or_directory ...")
        rudisha
    kila arg kwenye args:
        check(arg)

kundi NannyNag(Exception):
    """
    Raised by process_tokens() ikiwa detecting an ambiguous indent.
    Captured na handled kwenye check().
    """
    eleza __init__(self, lineno, msg, line):
        self.lineno, self.msg, self.line = lineno, msg, line
    eleza get_lineno(self):
        rudisha self.lineno
    eleza get_msg(self):
        rudisha self.msg
    eleza get_line(self):
        rudisha self.line

eleza check(file):
    """check(file_or_dir)

    If file_or_dir ni a directory na sio a symbolic link, then recursively
    descend the directory tree named by file_or_dir, checking all .py files
    along the way. If file_or_dir ni an ordinary Python source file, it is
    checked kila whitespace related problems. The diagnostic messages are
    written to standard output using the print statement.
    """

    ikiwa os.path.isdir(file) na sio os.path.islink(file):
        ikiwa verbose:
            andika("%r: listing directory" % (file,))
        names = os.listdir(file)
        kila name kwenye names:
            fullname = os.path.join(file, name)
            ikiwa (os.path.isdir(fullname) na
                sio os.path.islink(fullname) ama
                os.path.normcase(name[-3:]) == ".py"):
                check(fullname)
        rudisha

    jaribu:
        f = tokenize.open(file)
    tatizo OSError kama msg:
        errandika("%r: I/O Error: %s" % (file, msg))
        rudisha

    ikiwa verbose > 1:
        andika("checking %r ..." % file)

    jaribu:
        process_tokens(tokenize.generate_tokens(f.readline))

    tatizo tokenize.TokenError kama msg:
        errandika("%r: Token Error: %s" % (file, msg))
        rudisha

    tatizo IndentationError kama msg:
        errandika("%r: Indentation Error: %s" % (file, msg))
        rudisha

    tatizo NannyNag kama nag:
        badline = nag.get_lineno()
        line = nag.get_line()
        ikiwa verbose:
            andika("%r: *** Line %d: trouble kwenye tab city! ***" % (file, badline))
            andika("offending line: %r" % (line,))
            andika(nag.get_msg())
        isipokua:
            ikiwa ' ' kwenye file: file = '"' + file + '"'
            ikiwa filename_only: andika(file)
            isipokua: andika(file, badline, repr(line))
        rudisha

    mwishowe:
        f.close()

    ikiwa verbose:
        andika("%r: Clean bill of health." % (file,))

kundi Whitespace:
    # the characters used kila space na tab
    S, T = ' \t'

    # members:
    #   raw
    #       the original string
    #   n
    #       the number of leading whitespace characters kwenye raw
    #   nt
    #       the number of tabs kwenye raw[:n]
    #   norm
    #       the normal form kama a pair (count, trailing), where:
    #       count
    #           a tuple such that raw[:n] contains count[i]
    #           instances of S * i + T
    #       trailing
    #           the number of trailing spaces kwenye raw[:n]
    #       It's A Theorem that m.indent_level(t) ==
    #       n.indent_level(t) kila all t >= 1 iff m.norm == n.norm.
    #   is_simple
    #       true iff raw[:n] ni of the form (T*)(S*)

    eleza __init__(self, ws):
        self.raw  = ws
        S, T = Whitespace.S, Whitespace.T
        count = []
        b = n = nt = 0
        kila ch kwenye self.raw:
            ikiwa ch == S:
                n = n + 1
                b = b + 1
            lasivyo ch == T:
                n = n + 1
                nt = nt + 1
                ikiwa b >= len(count):
                    count = count + [0] * (b - len(count) + 1)
                count[b] = count[b] + 1
                b = 0
            isipokua:
                koma
        self.n    = n
        self.nt   = nt
        self.norm = tuple(count), b
        self.is_simple = len(count) <= 1

    # rudisha length of longest contiguous run of spaces (whether ama not
    # preceding a tab)
    eleza longest_run_of_spaces(self):
        count, trailing = self.norm
        rudisha max(len(count)-1, trailing)

    eleza indent_level(self, tabsize):
        # count, il = self.norm
        # kila i kwenye range(len(count)):
        #    ikiwa count[i]:
        #        il = il + (i//tabsize + 1)*tabsize * count[i]
        # rudisha il

        # quicker:
        # il = trailing + sum (i//ts + 1)*ts*count[i] =
        # trailing + ts * sum (i//ts + 1)*count[i] =
        # trailing + ts * sum i//ts*count[i] + count[i] =
        # trailing + ts * [(sum i//ts*count[i]) + (sum count[i])] =
        # trailing + ts * [(sum i//ts*count[i]) + num_tabs]
        # na note that i//ts*count[i] ni 0 when i < ts

        count, trailing = self.norm
        il = 0
        kila i kwenye range(tabsize, len(count)):
            il = il + i//tabsize * count[i]
        rudisha trailing + tabsize * (il + self.nt)

    # rudisha true iff self.indent_level(t) == other.indent_level(t)
    # kila all t >= 1
    eleza equal(self, other):
        rudisha self.norm == other.norm

    # rudisha a list of tuples (ts, i1, i2) such that
    # i1 == self.indent_level(ts) != other.indent_level(ts) == i2.
    # Intended to be used after sio self.equal(other) ni known, kwenye which
    # case it will rudisha at least one witnessing tab size.
    eleza not_equal_witness(self, other):
        n = max(self.longest_run_of_spaces(),
                other.longest_run_of_spaces()) + 1
        a = []
        kila ts kwenye range(1, n+1):
            ikiwa self.indent_level(ts) != other.indent_level(ts):
                a.append( (ts,
                           self.indent_level(ts),
                           other.indent_level(ts)) )
        rudisha a

    # Return Kweli iff self.indent_level(t) < other.indent_level(t)
    # kila all t >= 1.
    # The algorithm ni due to Vincent Broman.
    # Easy to prove it's correct.
    # XXXpost that.
    # Trivial to prove n ni sharp (consider T vs ST).
    # Unknown whether there's a faster general way.  I suspected so at
    # first, but no longer.
    # For the special (but common!) case where M na N are both of the
    # form (T*)(S*), M.less(N) iff M.len() < N.len() na
    # M.num_tabs() <= N.num_tabs(). Proof ni easy but kinda long-winded.
    # XXXwrite that up.
    # Note that M ni of the form (T*)(S*) iff len(M.norm[0]) <= 1.
    eleza less(self, other):
        ikiwa self.n >= other.n:
            rudisha Uongo
        ikiwa self.is_simple na other.is_simple:
            rudisha self.nt <= other.nt
        n = max(self.longest_run_of_spaces(),
                other.longest_run_of_spaces()) + 1
        # the self.n >= other.n test already did it kila ts=1
        kila ts kwenye range(2, n+1):
            ikiwa self.indent_level(ts) >= other.indent_level(ts):
                rudisha Uongo
        rudisha Kweli

    # rudisha a list of tuples (ts, i1, i2) such that
    # i1 == self.indent_level(ts) >= other.indent_level(ts) == i2.
    # Intended to be used after sio self.less(other) ni known, kwenye which
    # case it will rudisha at least one witnessing tab size.
    eleza not_less_witness(self, other):
        n = max(self.longest_run_of_spaces(),
                other.longest_run_of_spaces()) + 1
        a = []
        kila ts kwenye range(1, n+1):
            ikiwa self.indent_level(ts) >= other.indent_level(ts):
                a.append( (ts,
                           self.indent_level(ts),
                           other.indent_level(ts)) )
        rudisha a

eleza format_witnesses(w):
    firsts = (str(tup[0]) kila tup kwenye w)
    prefix = "at tab size"
    ikiwa len(w) > 1:
        prefix = prefix + "s"
    rudisha prefix + " " + ', '.join(firsts)

eleza process_tokens(tokens):
    INDENT = tokenize.INDENT
    DEDENT = tokenize.DEDENT
    NEWLINE = tokenize.NEWLINE
    JUNK = tokenize.COMMENT, tokenize.NL
    indents = [Whitespace("")]
    check_equal = 0

    kila (type, token, start, end, line) kwenye tokens:
        ikiwa type == NEWLINE:
            # a program statement, ama ENDMARKER, will eventually follow,
            # after some (possibly empty) run of tokens of the form
            #     (NL | COMMENT)* (INDENT | DEDENT+)?
            # If an INDENT appears, setting check_equal ni wrong, na will
            # be undone when we see the INDENT.
            check_equal = 1

        lasivyo type == INDENT:
            check_equal = 0
            thisguy = Whitespace(token)
            ikiwa sio indents[-1].less(thisguy):
                witness = indents[-1].not_less_witness(thisguy)
                msg = "indent sio greater e.g. " + format_witnesses(witness)
                ashiria NannyNag(start[0], msg, line)
            indents.append(thisguy)

        lasivyo type == DEDENT:
            # there's nothing we need to check here!  what's agizaant is
            # that when the run of DEDENTs ends, the indentation of the
            # program statement (or ENDMARKER) that triggered the run is
            # equal to what's left at the top of the indents stack

            # Ouch!  This assert triggers ikiwa the last line of the source
            # ni indented *and* lacks a newline -- then DEDENTs pop out
            # of thin air.
            # assert check_equal  # isipokua no earlier NEWLINE, ama an earlier INDENT
            check_equal = 1

            toa indents[-1]

        lasivyo check_equal na type haiko kwenye JUNK:
            # this ni the first "real token" following a NEWLINE, so it
            # must be the first token of the next program statement, ama an
            # ENDMARKER; the "line" argument exposes the leading whitespace
            # kila this statement; kwenye the case of ENDMARKER, line ni an empty
            # string, so will properly match the empty string ukijumuisha which the
            # "indents" stack was seeded
            check_equal = 0
            thisguy = Whitespace(line)
            ikiwa sio indents[-1].equal(thisguy):
                witness = indents[-1].not_equal_witness(thisguy)
                msg = "indent sio equal e.g. " + format_witnesses(witness)
                ashiria NannyNag(start[0], msg, line)


ikiwa __name__ == '__main__':
    main()
