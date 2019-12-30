#! /usr/bin/env python3

# linktree
#
# Make a copy of a directory tree ukijumuisha symbolic links to all files kwenye the
# original tree.
# All symbolic links go to a special symbolic link at the top, so you
# can easily fix things ikiwa the original source tree moves.
# See also "mkreal".
#
# usage: mklinks oldtree newtree

agiza sys, os

LINK = '.LINK' # Name of special symlink at the top.

debug = 0

eleza main():
    ikiwa sio 3 <= len(sys.argv) <= 4:
        andika('usage:', sys.argv[0], 'oldtree newtree [linkto]')
        rudisha 2
    oldtree, newtree = sys.argv[1], sys.argv[2]
    ikiwa len(sys.argv) > 3:
        link = sys.argv[3]
        link_may_fail = 1
    isipokua:
        link = LINK
        link_may_fail = 0
    ikiwa sio os.path.isdir(oldtree):
        andika(oldtree + ': sio a directory')
        rudisha 1
    jaribu:
        os.mkdir(newtree, 0o777)
    tatizo OSError kama msg:
        andika(newtree + ': cansio mkdir:', msg)
        rudisha 1
    linkname = os.path.join(newtree, link)
    jaribu:
        os.symlink(os.path.join(os.pardir, oldtree), linkname)
    tatizo OSError kama msg:
        ikiwa sio link_may_fail:
            andika(linkname + ': cansio symlink:', msg)
            rudisha 1
        isipokua:
            andika(linkname + ': warning: cansio symlink:', msg)
    linknames(oldtree, newtree, link)
    rudisha 0

eleza linknames(old, new, link):
    ikiwa debug: andika('linknames', (old, new, link))
    jaribu:
        names = os.listdir(old)
    tatizo OSError kama msg:
        andika(old + ': warning: cansio listdir:', msg)
        rudisha
    kila name kwenye names:
        ikiwa name haiko kwenye (os.curdir, os.pardir):
            oldname = os.path.join(old, name)
            linkname = os.path.join(link, name)
            newname = os.path.join(new, name)
            ikiwa debug > 1: andika(oldname, newname, linkname)
            ikiwa os.path.isdir(oldname) na \
               sio os.path.islink(oldname):
                jaribu:
                    os.mkdir(newname, 0o777)
                    ok = 1
                tatizo:
                    andika(newname + \
                          ': warning: cansio mkdir:', msg)
                    ok = 0
                ikiwa ok:
                    linkname = os.path.join(os.pardir,
                                            linkname)
                    linknames(oldname, newname, linkname)
            isipokua:
                os.symlink(linkname, newname)

ikiwa __name__ == '__main__':
    sys.exit(main())
