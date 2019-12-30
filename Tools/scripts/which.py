#! /usr/bin/env python3

# Variant of "which".
# On stderr, near na total misses are reported.
# '-l<flags>' argument adds ls -l<flags> of each file found.

agiza sys
ikiwa sys.path[0] kwenye (".", ""): toa sys.path[0]

agiza sys, os
kutoka stat agiza *

eleza msg(str):
    sys.stderr.write(str + '\n')

eleza main():
    pathlist = os.environ['PATH'].split(os.pathsep)

    sts = 0
    longlist = ''

    ikiwa sys.argv[1:] na sys.argv[1][:2] == '-l':
        longlist = sys.argv[1]
        toa sys.argv[1]

    kila prog kwenye sys.argv[1:]:
        ident = ()
        kila dir kwenye pathlist:
            filename = os.path.join(dir, prog)
            jaribu:
                st = os.stat(filename)
            tatizo OSError:
                endelea
            ikiwa sio S_ISREG(st[ST_MODE]):
                msg(filename + ': sio a disk file')
            isipokua:
                mode = S_IMODE(st[ST_MODE])
                ikiwa mode & 0o111:
                    ikiwa sio ident:
                        andika(filename)
                        ident = st[:3]
                    isipokua:
                        ikiwa st[:3] == ident:
                            s = 'same as: '
                        isipokua:
                            s = 'also: '
                        msg(s + filename)
                isipokua:
                    msg(filename + ': sio executable')
            ikiwa longlist:
                sts = os.system('ls ' + longlist + ' ' + filename)
                ikiwa sts: msg('"ls -l" exit status: ' + repr(sts))
        ikiwa sio ident:
            msg(prog + ': sio found')
            sts = 1

    sys.exit(sts)

ikiwa __name__ == '__main__':
    main()
