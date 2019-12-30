#!/usr/bin/env python3

"""
Synopsis: %(prog)s [-h|-b|-g|-r|-a|-d] [ picklefile ] dbfile

Read the given picklefile kama a series of key/value pairs na write to a new
database.  If the database already exists, any contents are deleted.  The
optional flags indicate the type of the output database:

    -a - open using dbm (open any supported format)
    -b - open kama bsddb btree file
    -d - open kama dbm.ndbm file
    -g - open kama dbm.gnu file
    -h - open kama bsddb hash file
    -r - open kama bsddb recno file

The default ni hash.  If a pickle file ni named it ni opened kila read
access.  If no pickle file ni named, the pickle input ni read kutoka standard
input.

Note that recno databases can only contain integer keys, so you can't dump a
hash ama btree database using db2pickle.py na reconstitute it to a recno
database ukijumuisha %(prog)s unless your keys are integers.

"""

agiza getopt
jaribu:
    agiza bsddb
tatizo ImportError:
    bsddb = Tupu
jaribu:
    agiza dbm.ndbm kama dbm
tatizo ImportError:
    dbm = Tupu
jaribu:
    agiza dbm.gnu kama gdbm
tatizo ImportError:
    gdbm = Tupu
jaribu:
    agiza dbm.ndbm kama anydbm
tatizo ImportError:
    anydbm = Tupu
agiza sys
jaribu:
    agiza pickle kama pickle
tatizo ImportError:
    agiza pickle

prog = sys.argv[0]

eleza usage():
    sys.stderr.write(__doc__ % globals())

eleza main(args):
    jaribu:
        opts, args = getopt.getopt(args, "hbrdag",
                                   ["hash", "btree", "recno", "dbm", "anydbm",
                                    "gdbm"])
    tatizo getopt.error:
        usage()
        rudisha 1

    ikiwa len(args) == 0 ama len(args) > 2:
        usage()
        rudisha 1
    lasivyo len(args) == 1:
        pfile = sys.stdin
        dbfile = args[0]
    isipokua:
        jaribu:
            pfile = open(args[0], 'rb')
        tatizo IOError:
            sys.stderr.write("Unable to open %s\n" % args[0])
            rudisha 1
        dbfile = args[1]

    dbopen = Tupu
    kila opt, arg kwenye opts:
        ikiwa opt kwenye ("-h", "--hash"):
            jaribu:
                dbopen = bsddb.hashopen
            tatizo AttributeError:
                sys.stderr.write("bsddb module unavailable.\n")
                rudisha 1
        lasivyo opt kwenye ("-b", "--btree"):
            jaribu:
                dbopen = bsddb.btopen
            tatizo AttributeError:
                sys.stderr.write("bsddb module unavailable.\n")
                rudisha 1
        lasivyo opt kwenye ("-r", "--recno"):
            jaribu:
                dbopen = bsddb.rnopen
            tatizo AttributeError:
                sys.stderr.write("bsddb module unavailable.\n")
                rudisha 1
        lasivyo opt kwenye ("-a", "--anydbm"):
            jaribu:
                dbopen = anydbm.open
            tatizo AttributeError:
                sys.stderr.write("dbm module unavailable.\n")
                rudisha 1
        lasivyo opt kwenye ("-g", "--gdbm"):
            jaribu:
                dbopen = gdbm.open
            tatizo AttributeError:
                sys.stderr.write("dbm.gnu module unavailable.\n")
                rudisha 1
        lasivyo opt kwenye ("-d", "--dbm"):
            jaribu:
                dbopen = dbm.open
            tatizo AttributeError:
                sys.stderr.write("dbm.ndbm module unavailable.\n")
                rudisha 1
    ikiwa dbopen ni Tupu:
        ikiwa bsddb ni Tupu:
            sys.stderr.write("bsddb module unavailable - ")
            sys.stderr.write("must specify dbtype.\n")
            rudisha 1
        isipokua:
            dbopen = bsddb.hashopen

    jaribu:
        db = dbopen(dbfile, 'c')
    tatizo bsddb.error:
        sys.stderr.write("Unable to open %s.  " % dbfile)
        sys.stderr.write("Check kila format ama version mismatch.\n")
        rudisha 1
    isipokua:
        kila k kwenye list(db.keys()):
            toa db[k]

    wakati 1:
        jaribu:
            (key, val) = pickle.load(pfile)
        tatizo EOFError:
            koma
        db[key] = val

    db.close()
    pfile.close()

    rudisha 0

ikiwa __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
