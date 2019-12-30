#! /usr/bin/env python3

# Find symbolic links na show where they point to.
# Arguments are directories to search; default ni current directory.
# No recursion.
# (This ni a totally different program kutoka "findsymlinks.py"!)

agiza sys, os

eleza lll(dirname):
    kila name kwenye os.listdir(dirname):
        ikiwa name haiko kwenye (os.curdir, os.pardir):
            full = os.path.join(dirname, name)
            ikiwa os.path.islink(full):
                andika(name, '->', os.readlink(full))
eleza main(args):
    ikiwa sio args: args = [os.curdir]
    first = 1
    kila arg kwenye args:
        ikiwa len(args) > 1:
            ikiwa sio first: andika()
            first = 0
            andika(arg + ':')
        lll(arg)

ikiwa __name__ == '__main__':
    main(sys.argv[1:])
