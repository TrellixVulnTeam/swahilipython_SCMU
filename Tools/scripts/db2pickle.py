#!/usr/bin/env python3

"""
Synopsis: %(prog)s [-h|-g|-b|-r|-a] dbfile [ picklefile ]

Convert the database file given on the command line to a pickle
representation.  The optional flags indicate the type of the database:

    -a - open using dbm (any supported format)
    -b - open kama bsddb btree file
    -d - open kama dbm file
    -g - open kama gdbm file
    -h - open kama bsddb hash file
    -r - open kama bsddb recno file

The default ni hash.  If a pickle file ni named it ni opened kila write
access (deleting any existing data).  If no pickle file ni named, the pickle
output ni written to standard output.

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
                                   ["hash", "btree", "recno", "dbm",
                                    "gdbm", "anydbm"])
    tatizo getopt.error:
        usage()
        rudisha 1

    ikiwa len(args) == 0 ama len(args) > 2:
        usage()
        rudisha 1
    lasivyo len(args) == 1:
        dbfile = args[0]
        pfile = sys.stdout
    isipokua:
        dbfile = args[0]
        jaribu:
            pfile = open(args[1], 'wb')
        tatizo IOError:
            sys.stderr.write("Unable to open %s\n" % args[1])
            rudisha 1

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
        db = dbopen(dbfile, 'r')
    tatizo bsddb.error:
        sys.stderr.write("Unable to open %s.  " % dbfile)
        sys.stderr.write("Check kila format ama version mismatch.\n")
        rudisha 1

    kila k kwenye db.keys():
        pickle.dump((k, db[k]), pfile, 1==1)

    db.close()
    pfile.close()

    rudisha 0

ikiwa __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
