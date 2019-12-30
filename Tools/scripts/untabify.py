#! /usr/bin/env python3

"Replace tabs ukijumuisha spaces kwenye argument files.  Print names of changed files."

agiza os
agiza sys
agiza getopt
agiza tokenize

eleza main():
    tabsize = 8
    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], "t:")
        ikiwa sio args:
            ashiria getopt.error("At least one file argument required")
    tatizo getopt.error kama msg:
        andika(msg)
        andika("usage:", sys.argv[0], "[-t tabwidth] file ...")
        rudisha
    kila optname, optvalue kwenye opts:
        ikiwa optname == '-t':
            tabsize = int(optvalue)

    kila filename kwenye args:
        process(filename, tabsize)


eleza process(filename, tabsize, verbose=Kweli):
    jaribu:
        ukijumuisha tokenize.open(filename) kama f:
            text = f.read()
            encoding = f.encoding
    tatizo IOError kama msg:
        andika("%r: I/O error: %s" % (filename, msg))
        rudisha
    newtext = text.expandtabs(tabsize)
    ikiwa newtext == text:
        rudisha
    backup = filename + "~"
    jaribu:
        os.unlink(backup)
    tatizo OSError:
        pita
    jaribu:
        os.rename(filename, backup)
    tatizo OSError:
        pita
    ukijumuisha open(filename, "w", encoding=encoding) kama f:
        f.write(newtext)
    ikiwa verbose:
        andika(filename)


ikiwa __name__ == '__main__':
    main()
