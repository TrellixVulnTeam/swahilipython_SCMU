agiza re
agiza sys

eleza negate(condition):
    """
    Returns a CPP conditional that ni the opposite of the conditional pitaed in.
    """
    ikiwa condition.startswith('!'):
        rudisha condition[1:]
    rudisha "!" + condition

kundi Monitor:
    """
    A simple C preprocessor that scans C source na computes, line by line,
    what the current C preprocessor #ikiwa state is.

    Doesn't handle everything--kila example, ikiwa you have /* inside a C string,
    without a matching */ (also inside a C string), ama ukijumuisha a */ inside a C
    string but on another line na ukijumuisha preprocessor macros kwenye between...
    the parser will get lost.

    Anyway this implementation seems to work well enough kila the CPython sources.
    """

    is_a_simple_defined = re.compile(r'^defined\s*\(\s*[A-Za-z0-9_]+\s*\)$').match

    eleza __init__(self, filename=Tupu, *, verbose=Uongo):
        self.stack = []
        self.in_comment = Uongo
        self.continuation = Tupu
        self.line_number = 0
        self.filename = filename
        self.verbose = verbose

    eleza __repr__(self):
        rudisha ''.join((
            '<Monitor ',
            str(id(self)),
            " line=", str(self.line_number),
            " condition=", repr(self.condition()),
            ">"))

    eleza status(self):
        rudisha str(self.line_number).rjust(4) + ": " + self.condition()

    eleza condition(self):
        """
        Returns the current preprocessor state, kama a single #ikiwa condition.
        """
        rudisha " && ".join(condition kila token, condition kwenye self.stack)

    eleza fail(self, *a):
        ikiwa self.filename:
            filename = " " + self.filename
        isipokua:
            filename = ''
        andika("Error at" + filename, "line", self.line_number, ":")
        andika("   ", ' '.join(str(x) kila x kwenye a))
        sys.exit(-1)

    eleza close(self):
        ikiwa self.stack:
            self.fail("Ended file wakati still kwenye a preprocessor conditional block!")

    eleza write(self, s):
        kila line kwenye s.split("\n"):
            self.writeline(line)

    eleza writeline(self, line):
        self.line_number += 1
        line = line.strip()

        eleza pop_stack():
            ikiwa sio self.stack:
                self.fail("#" + token + " without matching #ikiwa / #ifeleza / #ifndef!")
            rudisha self.stack.pop()

        ikiwa self.continuation:
            line = self.continuation + line
            self.continuation = Tupu

        ikiwa sio line:
            rudisha

        ikiwa line.endswith('\\'):
            self.continuation = line[:-1].rstrip() + " "
            rudisha

        # we have to ignore preprocessor commands inside comments
        #
        # we also have to handle this:
        #     /* start
        #     ...
        #     */   /*    <-- tricky!
        #     ...
        #     */
        # na this:
        #     /* start
        #     ...
        #     */   /* also tricky! */
        ikiwa self.in_comment:
            ikiwa '*/' kwenye line:
                # snip out the comment na endelea
                #
                # GCC allows
                #    /* comment
                #    */ #include <stdio.h>
                # maybe other compilers too?
                _, _, line = line.partition('*/')
                self.in_comment = Uongo

        wakati Kweli:
            ikiwa '/*' kwenye line:
                ikiwa self.in_comment:
                    self.fail("Nested block comment!")

                before, _, remainder = line.partition('/*')
                comment, comment_ends, after = remainder.partition('*/')
                ikiwa comment_ends:
                    # snip out the comment
                    line = before.rstrip() + ' ' + after.lstrip()
                    endelea
                # comment endeleas to eol
                self.in_comment = Kweli
                line = before.rstrip()
            koma

        # we actually have some // comments
        # (but block comments take precedence)
        before, line_comment, comment = line.partition('//')
        ikiwa line_comment:
            line = before.rstrip()

        ikiwa sio line.startswith('#'):
            rudisha

        line = line[1:].lstrip()
        assert line

        fields = line.split()
        token = fields[0].lower()
        condition = ' '.join(fields[1:]).strip()

        if_tokens = {'if', 'ifdef', 'ifndef'}
        all_tokens = if_tokens | {'elif', 'else', 'endif'}

        ikiwa token haiko kwenye all_tokens:
            rudisha

        # cheat a little here, to reuse the implementation of if
        ikiwa token == 'elif':
            pop_stack()
            token = 'if'

        ikiwa token kwenye if_tokens:
            ikiwa sio condition:
                self.fail("Invalid format kila #" + token + " line: no argument!")
            ikiwa token == 'if':
                ikiwa sio self.is_a_simple_defined(condition):
                    condition = "(" + condition + ")"
            isipokua:
                fields = condition.split()
                ikiwa len(fields) != 1:
                    self.fail("Invalid format kila #" + token + " line: should be exactly one argument!")
                symbol = fields[0]
                condition = 'defined(' + symbol + ')'
                ikiwa token == 'ifndef':
                    condition = '!' + condition

            self.stack.append(("if", condition))
            ikiwa self.verbose:
                andika(self.status())
            rudisha

        previous_token, previous_condition = pop_stack()

        ikiwa token == 'else':
            self.stack.append(('else', negate(previous_condition)))
        lasivyo token == 'endif':
            pita
        ikiwa self.verbose:
            andika(self.status())

ikiwa __name__ == '__main__':
    kila filename kwenye sys.argv[1:]:
        ukijumuisha open(filename, "rt") kama f:
            cpp = Monitor(filename, verbose=Kweli)
            andika()
            andika(filename)
            kila line_number, line kwenye enumerate(f.read().split('\n'), 1):
                cpp.writeline(line)
