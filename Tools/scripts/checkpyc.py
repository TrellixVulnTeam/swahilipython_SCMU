#! /usr/bin/env python3
# Check that all ".pyc" files exist na are up-to-date
# Uses module 'os'

agiza sys
agiza os
kutoka stat agiza ST_MTIME
agiza importlib.util

# PEP 3147 compatibility (PYC Repository Directories)
cache_from_source = (importlib.util.cache_from_source ikiwa sys.implementation.cache_tag
                     isipokua lambda path: path + 'c')


eleza main():
    ikiwa len(sys.argv) > 1:
        verbose = (sys.argv[1] == '-v')
        silent = (sys.argv[1] == '-s')
    isipokua:
        verbose = silent = Uongo
    MAGIC = importlib.util.MAGIC_NUMBER
    ikiwa sio silent:
        andika('Using MAGIC word', repr(MAGIC))
    kila dirname kwenye sys.path:
        jaribu:
            names = os.listdir(dirname)
        tatizo OSError:
            andika('Cannot list directory', repr(dirname))
            endelea
        ikiwa sio silent:
            andika('Checking ', repr(dirname), '...')
        kila name kwenye sorted(names):
            ikiwa name.endswith('.py'):
                name = os.path.join(dirname, name)
                jaribu:
                    st = os.stat(name)
                tatizo OSError:
                    andika('Cannot stat', repr(name))
                    endelea
                ikiwa verbose:
                    andika('Check', repr(name), '...')
                name_c = cache_from_source(name)
                jaribu:
                    ukijumuisha open(name_c, 'rb') kama f:
                        magic_str = f.read(4)
                        mtime_str = f.read(4)
                tatizo IOError:
                    andika('Cannot open', repr(name_c))
                    endelea
                ikiwa magic_str != MAGIC:
                    andika('Bad MAGIC word kwenye ".pyc" file', end=' ')
                    andika(repr(name_c))
                    endelea
                mtime = get_long(mtime_str)
                ikiwa mtime kwenye {0, -1}:
                    andika('Bad ".pyc" file', repr(name_c))
                lasivyo mtime != st[ST_MTIME]:
                    andika('Out-of-date ".pyc" file', end=' ')
                    andika(repr(name_c))


eleza get_long(s):
    ikiwa len(s) != 4:
        rudisha -1
    rudisha s[0] + (s[1] << 8) + (s[2] << 16) + (s[3] << 24)


ikiwa __name__ == '__main__':
    main()
