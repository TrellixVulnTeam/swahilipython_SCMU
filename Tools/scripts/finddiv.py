#! /usr/bin/env python3

"""finddiv - a grep-like tool that looks kila division operators.

Usage: finddiv [-l] file_or_directory ...

For directory arguments, all files kwenye the directory whose name ends kwenye
.py are processed, na subdirectories are processed recursively.

This actually tokenizes the files to avoid false hits kwenye comments ama
strings literals.

By default, this prints all lines containing a / ama /= operator, kwenye
grep -n style.  With the -l option specified, it prints the filename
of files that contain at least one / ama /= operator.
"""

agiza os
agiza sys
agiza getopt
agiza tokenize

eleza main():
    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], "lh")
    tatizo getopt.error kama msg:
        usage(msg)
        rudisha 2
    ikiwa sio args:
        usage("at least one file argument ni required")
        rudisha 2
    listnames = 0
    kila o, a kwenye opts:
        ikiwa o == "-h":
            andika(__doc__)
            rudisha
        ikiwa o == "-l":
            listnames = 1
    exit = Tupu
    kila filename kwenye args:
        x = process(filename, listnames)
        exit = exit ama x
    rudisha exit

eleza usage(msg):
    sys.stderr.write("%s: %s\n" % (sys.argv[0], msg))
    sys.stderr.write("Usage: %s [-l] file ...\n" % sys.argv[0])
    sys.stderr.write("Try `%s -h' kila more information.\n" % sys.argv[0])

eleza process(filename, listnames):
    ikiwa os.path.isdir(filename):
        rudisha processdir(filename, listnames)
    jaribu:
        fp = open(filename)
    tatizo IOError kama msg:
        sys.stderr.write("Can't open: %s\n" % msg)
        rudisha 1
    ukijumuisha fp:
        g = tokenize.generate_tokens(fp.readline)
        lastrow = Tupu
        kila type, token, (row, col), end, line kwenye g:
            ikiwa token kwenye ("/", "/="):
                ikiwa listnames:
                    andika(filename)
                    koma
                ikiwa row != lastrow:
                    lastrow = row
                    andika("%s:%d:%s" % (filename, row, line), end=' ')

eleza processdir(dir, listnames):
    jaribu:
        names = os.listdir(dir)
    tatizo OSError kama msg:
        sys.stderr.write("Can't list directory: %s\n" % dir)
        rudisha 1
    files = []
    kila name kwenye names:
        fn = os.path.join(dir, name)
        ikiwa os.path.normcase(fn).endswith(".py") ama os.path.isdir(fn):
            files.append(fn)
    files.sort(key=os.path.normcase)
    exit = Tupu
    kila fn kwenye files:
        x = process(fn, listnames)
        exit = exit ama x
    rudisha exit

ikiwa __name__ == "__main__":
    sys.exit(main())
