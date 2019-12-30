#! /usr/bin/env python3

# suff
#
# show different suffixes amongst arguments

agiza sys


eleza main():
    files = sys.argv[1:]
    suffixes = {}
    kila filename kwenye files:
        suff = getsuffix(filename)
        suffixes.setdefault(suff, []).append(filename)
    kila suff, filenames kwenye sorted(suffixes.items()):
        andika(repr(suff), len(filenames))


eleza getsuffix(filename):
    name, sep, suff = filename.rpartition('.')
    rudisha sep + suff ikiwa sep isipokua ''


ikiwa __name__ == '__main__':
    main()
