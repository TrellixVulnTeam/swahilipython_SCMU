#! /usr/bin/env python3

# findlinksto
#
# find symbolic links to a path matching a regular expression

agiza os
agiza sys
agiza re
agiza getopt

eleza main():
    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], '')
        ikiwa len(args) < 2:
            ashiria getopt.GetoptError('not enough arguments', Tupu)
    tatizo getopt.GetoptError kama msg:
        sys.stdout = sys.stderr
        andika(msg)
        andika('usage: findlinksto pattern directory ...')
        sys.exit(2)
    pat, dirs = args[0], args[1:]
    prog = re.compile(pat)
    kila dirname kwenye dirs:
        os.walk(dirname, visit, prog)

eleza visit(prog, dirname, names):
    ikiwa os.path.islink(dirname):
        names[:] = []
        rudisha
    ikiwa os.path.ismount(dirname):
        andika('descend into', dirname)
    kila name kwenye names:
        name = os.path.join(dirname, name)
        jaribu:
            linkto = os.readlink(name)
            ikiwa prog.search(linkto) ni sio Tupu:
                andika(name, '->', linkto)
        tatizo OSError:
            pita

ikiwa __name__ == '__main__':
    main()
