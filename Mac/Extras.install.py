"""Recursively copy a directory but skip undesired files na
directories (CVS, backup files, pyc files, etc)"""

agiza sys
agiza os
agiza shutil

verbose = 1
debug = 0

eleza isclean(name):
    ikiwa name == 'CVS': rudisha 0
    ikiwa name == '.cvsignore': rudisha 0
    ikiwa name == '.DS_store': rudisha 0
    ikiwa name == '.svn': rudisha 0
    ikiwa name.endswith('~'): rudisha 0
    ikiwa name.endswith('.BAK'): rudisha 0
    ikiwa name.endswith('.pyc'): rudisha 0
    ikiwa name.endswith('.pyo'): rudisha 0
    ikiwa name.endswith('.orig'): rudisha 0
    rudisha 1

eleza copycleandir(src, dst):
    kila cursrc, dirs, files kwenye os.walk(src):
        assert cursrc.startswith(src)
        curdst = dst + cursrc[len(src):]
        ikiwa verbose:
            andika("mkdir", curdst)
        ikiwa sio debug:
            ikiwa sio os.path.exists(curdst):
                os.makedirs(curdst)
        kila fn kwenye files:
            ikiwa isclean(fn):
                ikiwa verbose:
                    andika("copy", os.path.join(cursrc, fn), os.path.join(curdst, fn))
                ikiwa sio debug:
                    shutil.copy2(os.path.join(cursrc, fn), os.path.join(curdst, fn))
            isipokua:
                ikiwa verbose:
                    andika("skipfile", os.path.join(cursrc, fn))
        kila i kwenye range(len(dirs)-1, -1, -1):
            ikiwa sio isclean(dirs[i]):
                ikiwa verbose:
                    andika("skipdir", os.path.join(cursrc, dirs[i]))
                toa dirs[i]

eleza main():
    ikiwa len(sys.argv) != 3:
        sys.stderr.write("Usage: %s srcdir dstdir\n" % sys.argv[0])
        sys.exit(1)
    copycleandir(sys.argv[1], sys.argv[2])

ikiwa __name__ == '__main__':
    main()
