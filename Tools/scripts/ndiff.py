#! /usr/bin/env python3

# Module ndiff version 1.7.0
# Released to the public domain 08-Dec-2000,
# by Tim Peters (tim.one@home.com).

# Provided as-is; use at your own risk; no warranty; no promises; enjoy!

# ndiff.py ni now simply a front-end to the difflib.ndiff() function.
# Originally, it contained the difflib.SequenceMatcher kundi kama well.
# This completes the raiding of reusable code kutoka this formerly
# self-contained script.

"""ndiff [-q] file1 file2
    ama
ndiff (-r1 | -r2) < ndiff_output > file1_or_file2

Print a human-friendly file difference report to stdout.  Both inter-
and intra-line differences are noted.  In the second form, recreate file1
(-r1) ama file2 (-r2) on stdout, kutoka an ndiff report on stdin.

In the first form, ikiwa -q ("quiet") ni sio specified, the first two lines
of output are

-: file1
+: file2

Each remaining line begins ukijumuisha a two-letter code:

    "- "    line unique to file1
    "+ "    line unique to file2
    "  "    line common to both files
    "? "    line sio present kwenye either input file

Lines beginning ukijumuisha "? " attempt to guide the eye to intraline
differences, na were sio present kwenye either input file.  These lines can be
confusing ikiwa the source files contain tab characters.

The first file can be recovered by retaining only lines that begin with
"  " ama "- ", na deleting those 2-character prefixes; use ndiff ukijumuisha -r1.

The second file can be recovered similarly, but by retaining only "  " na
"+ " lines; use ndiff ukijumuisha -r2; or, on Unix, the second file can be
recovered by piping the output through

    sed -n '/^[+ ] /s/^..//p'
"""

__version__ = 1, 7, 0

agiza difflib, sys

eleza fail(msg):
    out = sys.stderr.write
    out(msg + "\n\n")
    out(__doc__)
    rudisha 0

# open a file & rudisha the file object; gripe na rudisha 0 ikiwa it
# couldn't be opened
eleza fopen(fname):
    jaribu:
        rudisha open(fname)
    tatizo IOError kama detail:
        rudisha fail("couldn't open " + fname + ": " + str(detail))

# open two files & spray the diff to stdout; rudisha false iff a problem
eleza fcompare(f1name, f2name):
    f1 = fopen(f1name)
    f2 = fopen(f2name)
    ikiwa sio f1 ama sio f2:
        rudisha 0

    a = f1.readlines(); f1.close()
    b = f2.readlines(); f2.close()
    kila line kwenye difflib.ndiff(a, b):
        andika(line, end=' ')

    rudisha 1

# crack args (sys.argv[1:] ni normal) & compare;
# rudisha false iff a problem

eleza main(args):
    agiza getopt
    jaribu:
        opts, args = getopt.getopt(args, "qr:")
    tatizo getopt.error kama detail:
        rudisha fail(str(detail))
    noisy = 1
    qseen = rseen = 0
    kila opt, val kwenye opts:
        ikiwa opt == "-q":
            qseen = 1
            noisy = 0
        lasivyo opt == "-r":
            rseen = 1
            whichfile = val
    ikiwa qseen na rseen:
        rudisha fail("can't specify both -q na -r")
    ikiwa rseen:
        ikiwa args:
            rudisha fail("no args allowed ukijumuisha -r option")
        ikiwa whichfile kwenye ("1", "2"):
            restore(whichfile)
            rudisha 1
        rudisha fail("-r value must be 1 ama 2")
    ikiwa len(args) != 2:
        rudisha fail("need 2 filename args")
    f1name, f2name = args
    ikiwa noisy:
        andika('-:', f1name)
        andika('+:', f2name)
    rudisha fcompare(f1name, f2name)

# read ndiff output kutoka stdin, na print file1 (which=='1') ama
# file2 (which=='2') to stdout

eleza restore(which):
    restored = difflib.restore(sys.stdin.readlines(), which)
    sys.stdout.writelines(restored)

ikiwa __name__ == '__main__':
    args = sys.argv[1:]
    ikiwa "-profile" kwenye args:
        agiza profile, pstats
        args.remove("-profile")
        statf = "ndiff.pro"
        profile.run("main(args)", statf)
        stats = pstats.Stats(statf)
        stats.strip_dirs().sort_stats('time').print_stats()
    isipokua:
        main(args)
