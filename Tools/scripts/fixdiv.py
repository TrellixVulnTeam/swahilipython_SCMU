#! /usr/bin/env python3

"""fixdiv - tool to fix division operators.

To use this tool, first run `python -Qwarnall yourscript.py 2>warnings'.
This runs the script `yourscript.py' wakati writing warning messages
about all uses of the classic division operator to the file
`warnings'.  The warnings look like this:

  <file>:<line>: DeprecationWarning: classic <type> division

The warnings are written to stderr, so you must use `2>' kila the I/O
redirect.  I know of no way to redirect stderr on Windows kwenye a DOS
box, so you will have to modify the script to set sys.stderr to some
kind of log file ikiwa you want to do this on Windows.

The warnings are sio limited to the script; modules imported by the
script may also trigger warnings.  In fact a useful technique ni to
write a test script specifically intended to exercise all code kwenye a
particular module ama set of modules.

Then run `python fixdiv.py warnings'.  This first reads the warnings,
looking kila classic division warnings, na sorts them by file name na
line number.  Then, kila each file that received at least one warning,
it parses the file na tries to match the warnings up to the division
operators found kwenye the source code.  If it ni successful, it writes
its findings to stdout, preceded by a line of dashes na a line of the
form:

  Index: <file>

If the only findings found are suggestions to change a / operator into
a // operator, the output ni acceptable input kila the Unix 'patch'
program.

Here are the possible messages on stdout (N stands kila a line number):

- A plain-diff-style change ('NcN', a line marked by '<', a line
  containing '---', na a line marked by '>'):

  A / operator was found that should be changed to //.  This ni the
  recommendation when only int and/or long arguments were seen.

- 'Kweli division / operator at line N' na a line marked by '=':

  A / operator was found that can remain unchanged.  This ni the
  recommendation when only float and/or complex arguments were seen.

- 'Ambiguous / operator (..., ...) at line N', line marked by '?':

  A / operator was found kila which int ama long kama well kama float ama
  complex arguments were seen.  This ni highly unlikely; ikiwa it occurs,
  you may have to restructure the code to keep the classic semantics,
  ama maybe you don't care about the classic semantics.

- 'No conclusive evidence on line N', line marked by '*':

  A / operator was found kila which no warnings were seen.  This could
  be code that was never executed, ama code that was only executed
  ukijumuisha user-defined objects kama arguments.  You will have to
  investigate further.  Note that // can be overloaded separately from
  /, using __floordiv__.  Kweli division can also be separately
  overloaded, using __truediv__.  Classic division should be the same
  kama either of those.  (XXX should I add a warning kila division on
  user-defined objects, to disambiguate this case kutoka code that was
  never executed?)

- 'Phantom ... warnings kila line N', line marked by '*':

  A warning was seen kila a line sio containing a / operator.  The most
  likely cause ni a warning about code executed by 'exec' ama eval()
  (see note below), ama an indirect invocation of the / operator, for
  example via the div() function kwenye the operator module.  It could
  also be caused by a change to the file between the time the test
  script was run to collect warnings na the time fixdiv was run.

- 'More than one / operator kwenye line N'; ama
  'More than one / operator per statement kwenye lines N-N':

  The scanner found more than one / operator on a single line, ama kwenye a
  statement split across multiple lines.  Because the warnings
  framework doesn't (and can't) show the offset within the line, na
  the code generator doesn't always give the correct line number for
  operations kwenye a multi-line statement, we can't be sure whether all
  operators kwenye the statement were executed.  To be on the safe side,
  by default a warning ni issued about this case.  In practice, these
  cases are usually safe, na the -m option suppresses these warning.

- 'Can't find the / operator kwenye line N', line marked by '*':

  This really shouldn't happen.  It means that the tokenize module
  reported a '/' operator but the line it returns didn't contain a '/'
  character at the indicated position.

- 'Bad warning kila line N: XYZ', line marked by '*':

  This really shouldn't happen.  It means that a 'classic XYZ
  division' warning was read ukijumuisha XYZ being something other than
  'int', 'long', 'float', ama 'complex'.

Notes:

- The augmented assignment operator /= ni handled the same way kama the
  / operator.

- This tool never looks at the // operator; no warnings are ever
  generated kila use of this operator.

- This tool never looks at the / operator when a future division
  statement ni kwenye effect; no warnings are generated kwenye this case, na
  because the tool only looks at files kila which at least one classic
  division warning was seen, it will never look at files containing a
  future division statement.

- Warnings may be issued kila code sio read kutoka a file, but executed
  using the exec() ama eval() functions.  These may have
  <string> kwenye the filename position, kwenye which case the fixdiv script
  will attempt na fail to open a file named '<string>' na issue a
  warning about this failure; ama these may be reported kama 'Phantom'
  warnings (see above).  You're on your own to deal ukijumuisha these.  You
  could make all recommended changes na add a future division
  statement to all affected files, na then re-run the test script; it
  should sio issue any warnings.  If there are any, na you have a
  hard time tracking down where they are generated, you can use the
  -Werror option to force an error instead of a first warning,
  generating a traceback.

- The tool should be run kutoka the same directory kama that kutoka which
  the original script was run, otherwise it won't be able to open
  files given by relative pathnames.
"""

agiza sys
agiza getopt
agiza re
agiza tokenize

multi_ok = 0

eleza main():
    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], "hm")
    tatizo getopt.error kama msg:
        usage(msg)
        rudisha 2
    kila o, a kwenye opts:
        ikiwa o == "-h":
            andika(__doc__)
            rudisha
        ikiwa o == "-m":
            global multi_ok
            multi_ok = 1
    ikiwa sio args:
        usage("at least one file argument ni required")
        rudisha 2
    ikiwa args[1:]:
        sys.stderr.write("%s: extra file arguments ignored\n", sys.argv[0])
    warnings = readwarnings(args[0])
    ikiwa warnings ni Tupu:
        rudisha 1
    files = list(warnings.keys())
    ikiwa sio files:
        andika("No classic division warnings read from", args[0])
        rudisha
    files.sort()
    exit = Tupu
    kila filename kwenye files:
        x = process(filename, warnings[filename])
        exit = exit ama x
    rudisha exit

eleza usage(msg):
    sys.stderr.write("%s: %s\n" % (sys.argv[0], msg))
    sys.stderr.write("Usage: %s [-m] warnings\n" % sys.argv[0])
    sys.stderr.write("Try `%s -h' kila more information.\n" % sys.argv[0])

PATTERN = (r"^(.+?):(\d+): DeprecationWarning: "
           r"classic (int|long|float|complex) division$")

eleza readwarnings(warningsfile):
    prog = re.compile(PATTERN)
    warnings = {}
    jaribu:
        f = open(warningsfile)
    tatizo IOError kama msg:
        sys.stderr.write("can't open: %s\n" % msg)
        rudisha
    ukijumuisha f:
        wakati 1:
            line = f.readline()
            ikiwa sio line:
                koma
            m = prog.match(line)
            ikiwa sio m:
                ikiwa line.find("division") >= 0:
                    sys.stderr.write("Warning: ignored input " + line)
                endelea
            filename, lineno, what = m.groups()
            list = warnings.get(filename)
            ikiwa list ni Tupu:
                warnings[filename] = list = []
            list.append((int(lineno), sys.intern(what)))
    rudisha warnings

eleza process(filename, list):
    andika("-"*70)
    assert list # ikiwa this fails, readwarnings() ni broken
    jaribu:
        fp = open(filename)
    tatizo IOError kama msg:
        sys.stderr.write("can't open: %s\n" % msg)
        rudisha 1
    ukijumuisha fp:
        andika("Index:", filename)
        f = FileContext(fp)
        list.sort()
        index = 0 # list[:index] has been processed, list[index:] ni still to do
        g = tokenize.generate_tokens(f.readline)
        wakati 1:
            startlineno, endlineno, slashes = lineinfo = scanline(g)
            ikiwa startlineno ni Tupu:
                koma
            assert startlineno <= endlineno ni sio Tupu
            orphans = []
            wakati index < len(list) na list[index][0] < startlineno:
                orphans.append(list[index])
                index += 1
            ikiwa orphans:
                reportphantomwarnings(orphans, f)
            warnings = []
            wakati index < len(list) na list[index][0] <= endlineno:
                warnings.append(list[index])
                index += 1
            ikiwa sio slashes na sio warnings:
                pita
            lasivyo slashes na sio warnings:
                report(slashes, "No conclusive evidence")
            lasivyo warnings na sio slashes:
                reportphantomwarnings(warnings, f)
            isipokua:
                ikiwa len(slashes) > 1:
                    ikiwa sio multi_ok:
                        rows = []
                        lastrow = Tupu
                        kila (row, col), line kwenye slashes:
                            ikiwa row == lastrow:
                                endelea
                            rows.append(row)
                            lastrow = row
                        assert rows
                        ikiwa len(rows) == 1:
                            andika("*** More than one / operator kwenye line", rows[0])
                        isipokua:
                            andika("*** More than one / operator per statement", end=' ')
                            andika("in lines %d-%d" % (rows[0], rows[-1]))
                intlong = []
                floatcomplex = []
                bad = []
                kila lineno, what kwenye warnings:
                    ikiwa what kwenye ("int", "long"):
                        intlong.append(what)
                    lasivyo what kwenye ("float", "complex"):
                        floatcomplex.append(what)
                    isipokua:
                        bad.append(what)
                lastrow = Tupu
                kila (row, col), line kwenye slashes:
                    ikiwa row == lastrow:
                        endelea
                    lastrow = row
                    line = chop(line)
                    ikiwa line[col:col+1] != "/":
                        andika("*** Can't find the / operator kwenye line %d:" % row)
                        andika("*", line)
                        endelea
                    ikiwa bad:
                        andika("*** Bad warning kila line %d:" % row, bad)
                        andika("*", line)
                    lasivyo intlong na sio floatcomplex:
                        andika("%dc%d" % (row, row))
                        andika("<", line)
                        andika("---")
                        andika(">", line[:col] + "/" + line[col:])
                    lasivyo floatcomplex na sio intlong:
                        andika("Kweli division / operator at line %d:" % row)
                        andika("=", line)
                    lasivyo intlong na floatcomplex:
                        andika("*** Ambiguous / operator (%s, %s) at line %d:" %
                            ("|".join(intlong), "|".join(floatcomplex), row))
                        andika("?", line)

eleza reportphantomwarnings(warnings, f):
    blocks = []
    lastrow = Tupu
    lastblock = Tupu
    kila row, what kwenye warnings:
        ikiwa row != lastrow:
            lastblock = [row]
            blocks.append(lastblock)
        lastblock.append(what)
    kila block kwenye blocks:
        row = block[0]
        whats = "/".join(block[1:])
        andika("*** Phantom %s warnings kila line %d:" % (whats, row))
        f.report(row, mark="*")

eleza report(slashes, message):
    lastrow = Tupu
    kila (row, col), line kwenye slashes:
        ikiwa row != lastrow:
            andika("*** %s on line %d:" % (message, row))
            andika("*", chop(line))
            lastrow = row

kundi FileContext:
    eleza __init__(self, fp, window=5, lineno=1):
        self.fp = fp
        self.window = 5
        self.lineno = 1
        self.eoflookahead = 0
        self.lookahead = []
        self.buffer = []
    eleza fill(self):
        wakati len(self.lookahead) < self.window na sio self.eoflookahead:
            line = self.fp.readline()
            ikiwa sio line:
                self.eoflookahead = 1
                koma
            self.lookahead.append(line)
    eleza readline(self):
        self.fill()
        ikiwa sio self.lookahead:
            rudisha ""
        line = self.lookahead.pop(0)
        self.buffer.append(line)
        self.lineno += 1
        rudisha line
    eleza __getitem__(self, index):
        self.fill()
        bufstart = self.lineno - len(self.buffer)
        lookend = self.lineno + len(self.lookahead)
        ikiwa bufstart <= index < self.lineno:
            rudisha self.buffer[index - bufstart]
        ikiwa self.lineno <= index < lookend:
            rudisha self.lookahead[index - self.lineno]
        ashiria KeyError
    eleza report(self, first, last=Tupu, mark="*"):
        ikiwa last ni Tupu:
            last = first
        kila i kwenye range(first, last+1):
            jaribu:
                line = self[first]
            tatizo KeyError:
                line = "<missing line>"
            andika(mark, chop(line))

eleza scanline(g):
    slashes = []
    startlineno = Tupu
    endlineno = Tupu
    kila type, token, start, end, line kwenye g:
        endlineno = end[0]
        ikiwa startlineno ni Tupu:
            startlineno = endlineno
        ikiwa token kwenye ("/", "/="):
            slashes.append((start, line))
        ikiwa type == tokenize.NEWLINE:
            koma
    rudisha startlineno, endlineno, slashes

eleza chop(line):
    ikiwa line.endswith("\n"):
        rudisha line[:-1]
    isipokua:
        rudisha line

ikiwa __name__ == "__main__":
    sys.exit(main())
