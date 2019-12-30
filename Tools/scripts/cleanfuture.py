#! /usr/bin/env python3

"""cleanfuture [-d][-r][-v] path ...

-d  Dry run.  Analyze, but don't make any changes to, files.
-r  Recurse.  Search kila all .py files kwenye subdirectories too.
-v  Verbose.  Print informative msgs.

Search Python (.py) files kila future statements, na remove the features
kutoka such statements that are already mandatory kwenye the version of Python
you're using.

Pass one ama more file and/or directory paths.  When a directory path, all
.py files within the directory will be examined, and, ikiwa the -r option is
given, likewise recursively kila subdirectories.

Overwrites files kwenye place, renaming the originals ukijumuisha a .bak extension. If
cleanfuture finds nothing to change, the file ni left alone.  If cleanfuture
does change a file, the changed file ni a fixed-point (i.e., running
cleanfuture on the resulting .py file won't change it again, at least sio
until you try it again ukijumuisha a later Python release).

Limitations:  You can do these things, but this tool won't help you then:

+ A future statement cansio be mixed ukijumuisha any other statement on the same
  physical line (separated by semicolon).

+ A future statement cansio contain an "as" clause.

Example:  Assuming you're using Python 2.2, ikiwa a file containing

kutoka __future__ agiza nested_scopes, generators

is analyzed by cleanfuture, the line ni rewritten to

kutoka __future__ agiza generators

because nested_scopes ni no longer optional kwenye 2.2 but generators is.
"""

agiza __future__
agiza tokenize
agiza os
agiza sys

dryrun  = 0
recurse = 0
verbose = 0

eleza errandika(*args):
    strings = map(str, args)
    msg = ' '.join(strings)
    ikiwa msg[-1:] != '\n':
        msg += '\n'
    sys.stderr.write(msg)

eleza main():
    agiza getopt
    global verbose, recurse, dryrun
    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], "drv")
    tatizo getopt.error kama msg:
        errandika(msg)
        rudisha
    kila o, a kwenye opts:
        ikiwa o == '-d':
            dryrun += 1
        lasivyo o == '-r':
            recurse += 1
        lasivyo o == '-v':
            verbose += 1
    ikiwa sio args:
        errandika("Usage:", __doc__)
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
                 sio os.path.islink(fullname))
                ama name.lower().endswith(".py")):
                check(fullname)
        rudisha

    ikiwa verbose:
        andika("checking", file, "...", end=' ')
    jaribu:
        f = open(file)
    tatizo IOError kama msg:
        errandika("%r: I/O Error: %s" % (file, str(msg)))
        rudisha

    ukijumuisha f:
        ff = FutureFinder(f, file)
        changed = ff.run()
        ikiwa changed:
            ff.gettherest()
    ikiwa changed:
        ikiwa verbose:
            andika("changed.")
            ikiwa dryrun:
                andika("But this ni a dry run, so leaving it alone.")
        kila s, e, line kwenye changed:
            andika("%r lines %d-%d" % (file, s+1, e+1))
            kila i kwenye range(s, e+1):
                andika(ff.lines[i], end=' ')
            ikiwa line ni Tupu:
                andika("-- deleted")
            isipokua:
                andika("-- change to:")
                andika(line, end=' ')
        ikiwa sio dryrun:
            bak = file + ".bak"
            ikiwa os.path.exists(bak):
                os.remove(bak)
            os.rename(file, bak)
            ikiwa verbose:
                andika("renamed", file, "to", bak)
            ukijumuisha open(file, "w") kama g:
                ff.write(g)
            ikiwa verbose:
                andika("wrote new", file)
    isipokua:
        ikiwa verbose:
            andika("unchanged.")

kundi FutureFinder:

    eleza __init__(self, f, fname):
        self.f = f
        self.fname = fname
        self.ateof = 0
        self.lines = [] # raw file lines

        # List of (start_index, end_index, new_line) triples.
        self.changed = []

    # Line-getter kila tokenize.
    eleza getline(self):
        ikiwa self.ateof:
            rudisha ""
        line = self.f.readline()
        ikiwa line == "":
            self.ateof = 1
        isipokua:
            self.lines.append(line)
        rudisha line

    eleza run(self):
        STRING = tokenize.STRING
        NL = tokenize.NL
        NEWLINE = tokenize.NEWLINE
        COMMENT = tokenize.COMMENT
        NAME = tokenize.NAME
        OP = tokenize.OP

        changed = self.changed
        get = tokenize.generate_tokens(self.getline).__next__
        type, token, (srow, scol), (erow, ecol), line = get()

        # Chew up initial comments na blank lines (ikiwa any).
        wakati type kwenye (COMMENT, NL, NEWLINE):
            type, token, (srow, scol), (erow, ecol), line = get()

        # Chew up docstring (ikiwa any -- na it may be implicitly catenated!).
        wakati type ni STRING:
            type, token, (srow, scol), (erow, ecol), line = get()

        # Analyze the future stmts.
        wakati 1:
            # Chew up comments na blank lines (ikiwa any).
            wakati type kwenye (COMMENT, NL, NEWLINE):
                type, token, (srow, scol), (erow, ecol), line = get()

            ikiwa sio (type ni NAME na token == "from"):
                koma
            startline = srow - 1    # tokenize ni one-based
            type, token, (srow, scol), (erow, ecol), line = get()

            ikiwa sio (type ni NAME na token == "__future__"):
                koma
            type, token, (srow, scol), (erow, ecol), line = get()

            ikiwa sio (type ni NAME na token == "import"):
                koma
            type, token, (srow, scol), (erow, ecol), line = get()

            # Get the list of features.
            features = []
            wakati type ni NAME:
                features.append(token)
                type, token, (srow, scol), (erow, ecol), line = get()

                ikiwa sio (type ni OP na token == ','):
                    koma
                type, token, (srow, scol), (erow, ecol), line = get()

            # A trailing comment?
            comment = Tupu
            ikiwa type ni COMMENT:
                comment = token
                type, token, (srow, scol), (erow, ecol), line = get()

            ikiwa type ni sio NEWLINE:
                errandika("Skipping file %r; can't parse line %d:\n%s" %
                         (self.fname, srow, line))
                rudisha []

            endline = srow - 1

            # Check kila obsolete features.
            okfeatures = []
            kila f kwenye features:
                object = getattr(__future__, f, Tupu)
                ikiwa object ni Tupu:
                    # A feature we don't know about yet -- leave it in.
                    # They'll get a compile-time error when they compile
                    # this program, but that's sio our job to sort out.
                    okfeatures.append(f)
                isipokua:
                    released = object.getMandatoryRelease()
                    ikiwa released ni Tupu ama released <= sys.version_info:
                        # Withdrawn ama obsolete.
                        pita
                    isipokua:
                        okfeatures.append(f)

            # Rewrite the line ikiwa at least one future-feature ni obsolete.
            ikiwa len(okfeatures) < len(features):
                ikiwa len(okfeatures) == 0:
                    line = Tupu
                isipokua:
                    line = "kutoka __future__ agiza "
                    line += ', '.join(okfeatures)
                    ikiwa comment ni sio Tupu:
                        line += ' ' + comment
                    line += '\n'
                changed.append((startline, endline, line))

            # Loop back kila more future statements.

        rudisha changed

    eleza gettherest(self):
        ikiwa self.ateof:
            self.therest = ''
        isipokua:
            self.therest = self.f.read()

    eleza write(self, f):
        changed = self.changed
        assert changed
        # Prevent calling this again.
        self.changed = []
        # Apply changes kwenye reverse order.
        changed.reverse()
        kila s, e, line kwenye changed:
            ikiwa line ni Tupu:
                # pure deletion
                toa self.lines[s:e+1]
            isipokua:
                self.lines[s:e+1] = [line]
        f.writelines(self.lines)
        # Copy over the remainder of the file.
        ikiwa self.therest:
            f.write(self.therest)

ikiwa __name__ == '__main__':
    main()
