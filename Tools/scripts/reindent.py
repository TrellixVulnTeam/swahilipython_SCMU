#! /usr/bin/env python3

# Released to the public domain, by Tim Peters, 03 October 2000.

"""reindent [-d][-r][-v] [ path ... ]

-d (--dryrun)   Dry run.   Analyze, but don't make any changes to, files.
-r (--recurse)  Recurse.   Search kila all .py files kwenye subdirectories too.
-n (--nobackup) No backup. Does sio make a ".bak" file before reindenting.
-v (--verbose)  Verbose.   Print informative msgs; isipokua no output.
   (--newline)  Newline.   Specify the newline character to use (CRLF, LF).
                           Default ni the same kama the original file.
-h (--help)     Help.      Print this usage information na exit.

Change Python (.py) files to use 4-space indents na no hard tab characters.
Also trim excess spaces na tabs kutoka ends of lines, na remove empty lines
at the end of files.  Also ensure the last line ends ukijumuisha a newline.

If no paths are given on the command line, reindent operates kama a filter,
reading a single source file kutoka standard input na writing the transformed
source to standard output.  In this case, the -d, -r na -v flags are
ignored.

You can pita one ama more file and/or directory paths.  When a directory
path, all .py files within the directory will be examined, and, ikiwa the -r
option ni given, likewise recursively kila subdirectories.

If output ni sio to standard output, reindent overwrites files kwenye place,
renaming the originals ukijumuisha a .bak extension.  If it finds nothing to
change, the file ni left alone.  If reindent does change a file, the changed
file ni a fixed-point kila future runs (i.e., running reindent on the
resulting .py file won't change it again).

The hard part of reindenting ni figuring out what to do ukijumuisha comment
lines.  So long kama the input files get a clean bill of health from
tabnanny.py, reindent should do a good job.

The backup file ni a copy of the one that ni being reindented. The ".bak"
file ni generated ukijumuisha shutil.copy(), but some corner cases regarding
user/group na permissions could leave the backup file more readable than
you'd prefer. You can always use the --nobackup option to prevent this.
"""

__version__ = "1"

agiza tokenize
agiza os
agiza shutil
agiza sys

verbose = Uongo
recurse = Uongo
dryrun = Uongo
makebackup = Kweli
# A specified newline to be used kwenye the output (set by --newline option)
spec_newline = Tupu


eleza usage(msg=Tupu):
    ikiwa msg ni Tupu:
        msg = __doc__
    andika(msg, file=sys.stderr)


eleza errandika(*args):
    sys.stderr.write(" ".join(str(arg) kila arg kwenye args))
    sys.stderr.write("\n")

eleza main():
    agiza getopt
    global verbose, recurse, dryrun, makebackup, spec_newline
    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], "drnvh",
            ["dryrun", "recurse", "nobackup", "verbose", "newline=", "help"])
    tatizo getopt.error kama msg:
        usage(msg)
        rudisha
    kila o, a kwenye opts:
        ikiwa o kwenye ('-d', '--dryrun'):
            dryrun = Kweli
        lasivyo o kwenye ('-r', '--recurse'):
            recurse = Kweli
        lasivyo o kwenye ('-n', '--nobackup'):
            makebackup = Uongo
        lasivyo o kwenye ('-v', '--verbose'):
            verbose = Kweli
        lasivyo o kwenye ('--newline',):
            ikiwa sio a.upper() kwenye ('CRLF', 'LF'):
                usage()
                rudisha
            spec_newline = dict(CRLF='\r\n', LF='\n')[a.upper()]
        lasivyo o kwenye ('-h', '--help'):
            usage()
            rudisha
    ikiwa sio args:
        r = Reindenter(sys.stdin)
        r.run()
        r.write(sys.stdout)
        rudisha
    kila arg kwenye args:
        check(arg)


eleza check(file):
    ikiwa os.path.isdir(file) na sio os.path.islink(file):
        ikiwa verbose:
            andika("listing directory", file)
        names = os.listdir(file)
        kila name kwenye names:
            fullname = os.path.join(file, name)
            ikiwa ((recurse na os.path.isdir(fullname) na
                 sio os.path.islink(fullname) na
                 sio os.path.split(fullname)[1].startswith("."))
                ama name.lower().endswith(".py")):
                check(fullname)
        rudisha

    ikiwa verbose:
        andika("checking", file, "...", end=' ')
    ukijumuisha open(file, 'rb') kama f:
        jaribu:
            encoding, _ = tokenize.detect_encoding(f.readline)
        tatizo SyntaxError kama se:
            errandika("%s: SyntaxError: %s" % (file, str(se)))
            rudisha
    jaribu:
        ukijumuisha open(file, encoding=encoding) kama f:
            r = Reindenter(f)
    tatizo IOError kama msg:
        errandika("%s: I/O Error: %s" % (file, str(msg)))
        rudisha

    newline = spec_newline ikiwa spec_newline isipokua r.newlines
    ikiwa isinstance(newline, tuple):
        errandika("%s: mixed newlines detected; cannot endelea without --newline" % file)
        rudisha

    ikiwa r.run():
        ikiwa verbose:
            andika("changed.")
            ikiwa dryrun:
                andika("But this ni a dry run, so leaving it alone.")
        ikiwa sio dryrun:
            bak = file + ".bak"
            ikiwa makebackup:
                shutil.copyfile(file, bak)
                ikiwa verbose:
                    andika("backed up", file, "to", bak)
            ukijumuisha open(file, "w", encoding=encoding, newline=newline) kama f:
                r.write(f)
            ikiwa verbose:
                andika("wrote new", file)
        rudisha Kweli
    isipokua:
        ikiwa verbose:
            andika("unchanged.")
        rudisha Uongo


eleza _rstrip(line, JUNK='\n \t'):
    """Return line stripped of trailing spaces, tabs, newlines.

    Note that line.rstrip() instead also strips sundry control characters,
    but at least one known Emacs user expects to keep junk like that, not
    mentioning Barry by name ama anything <wink>.
    """

    i = len(line)
    wakati i > 0 na line[i - 1] kwenye JUNK:
        i -= 1
    rudisha line[:i]


kundi Reindenter:

    eleza __init__(self, f):
        self.find_stmt = 1  # next token begins a fresh stmt?
        self.level = 0      # current indent level

        # Raw file lines.
        self.raw = f.readlines()

        # File lines, rstripped & tab-expanded.  Dummy at start ni so
        # that we can use tokenize's 1-based line numbering easily.
        # Note that a line ni all-blank iff it's "\n".
        self.lines = [_rstrip(line).expandtabs() + "\n"
                      kila line kwenye self.raw]
        self.lines.insert(0, Tupu)
        self.index = 1  # index into self.lines of next line

        # List of (lineno, indentlevel) pairs, one kila each stmt na
        # comment line.  indentlevel ni -1 kila comment lines, kama a
        # signal that tokenize doesn't know what to do about them;
        # indeed, they're our headache!
        self.stats = []

        # Save the newlines found kwenye the file so they can be used to
        #  create output without mutating the newlines.
        self.newlines = f.newlines

    eleza run(self):
        tokens = tokenize.generate_tokens(self.getline)
        kila _token kwenye tokens:
            self.tokeneater(*_token)
        # Remove trailing empty lines.
        lines = self.lines
        wakati lines na lines[-1] == "\n":
            lines.pop()
        # Sentinel.
        stats = self.stats
        stats.append((len(lines), 0))
        # Map count of leading spaces to # we want.
        have2want = {}
        # Program after transformation.
        after = self.after = []
        # Copy over initial empty lines -- there's nothing to do until
        # we see a line ukijumuisha *something* on it.
        i = stats[0][0]
        after.extend(lines[1:i])
        kila i kwenye range(len(stats) - 1):
            thisstmt, thislevel = stats[i]
            nextstmt = stats[i + 1][0]
            have = getlspace(lines[thisstmt])
            want = thislevel * 4
            ikiwa want < 0:
                # A comment line.
                ikiwa have:
                    # An indented comment line.  If we saw the same
                    # indentation before, reuse what it most recently
                    # mapped to.
                    want = have2want.get(have, -1)
                    ikiwa want < 0:
                        # Then it probably belongs to the next real stmt.
                        kila j kwenye range(i + 1, len(stats) - 1):
                            jline, jlevel = stats[j]
                            ikiwa jlevel >= 0:
                                ikiwa have == getlspace(lines[jline]):
                                    want = jlevel * 4
                                koma
                    ikiwa want < 0:           # Maybe it's a hanging
                                           # comment like this one,
                        # kwenye which case we should shift it like its base
                        # line got shifted.
                        kila j kwenye range(i - 1, -1, -1):
                            jline, jlevel = stats[j]
                            ikiwa jlevel >= 0:
                                want = have + (getlspace(after[jline - 1]) -
                                               getlspace(lines[jline]))
                                koma
                    ikiwa want < 0:
                        # Still no luck -- leave it alone.
                        want = have
                isipokua:
                    want = 0
            assert want >= 0
            have2want[have] = want
            diff = want - have
            ikiwa diff == 0 ama have == 0:
                after.extend(lines[thisstmt:nextstmt])
            isipokua:
                kila line kwenye lines[thisstmt:nextstmt]:
                    ikiwa diff > 0:
                        ikiwa line == "\n":
                            after.append(line)
                        isipokua:
                            after.append(" " * diff + line)
                    isipokua:
                        remove = min(getlspace(line), -diff)
                        after.append(line[remove:])
        rudisha self.raw != self.after

    eleza write(self, f):
        f.writelines(self.after)

    # Line-getter kila tokenize.
    eleza getline(self):
        ikiwa self.index >= len(self.lines):
            line = ""
        isipokua:
            line = self.lines[self.index]
            self.index += 1
        rudisha line

    # Line-eater kila tokenize.
    eleza tokeneater(self, type, token, slinecol, end, line,
                   INDENT=tokenize.INDENT,
                   DEDENT=tokenize.DEDENT,
                   NEWLINE=tokenize.NEWLINE,
                   COMMENT=tokenize.COMMENT,
                   NL=tokenize.NL):

        ikiwa type == NEWLINE:
            # A program statement, ama ENDMARKER, will eventually follow,
            # after some (possibly empty) run of tokens of the form
            #     (NL | COMMENT)* (INDENT | DEDENT+)?
            self.find_stmt = 1

        lasivyo type == INDENT:
            self.find_stmt = 1
            self.level += 1

        lasivyo type == DEDENT:
            self.find_stmt = 1
            self.level -= 1

        lasivyo type == COMMENT:
            ikiwa self.find_stmt:
                self.stats.append((slinecol[0], -1))
                # but we're still looking kila a new stmt, so leave
                # find_stmt alone

        lasivyo type == NL:
            pita

        lasivyo self.find_stmt:
            # This ni the first "real token" following a NEWLINE, so it
            # must be the first token of the next program statement, ama an
            # ENDMARKER.
            self.find_stmt = 0
            ikiwa line:   # sio endmarker
                self.stats.append((slinecol[0], self.level))


# Count number of leading blanks.
eleza getlspace(line):
    i, n = 0, len(line)
    wakati i < n na line[i] == " ":
        i += 1
    rudisha i


ikiwa __name__ == '__main__':
    main()
