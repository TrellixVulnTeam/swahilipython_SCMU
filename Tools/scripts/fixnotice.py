#! /usr/bin/env python3

"""(Ostensibly) fix copyright notices kwenye files.

Actually, this script will simply replace a block of text kwenye a file kutoka one
string to another.  It will only do this once though, i.e. sio globally
throughout the file.  It writes a backup file na then does an os.rename()
dance kila atomicity.

Usage: fixnotices.py [options] [filenames]
Options:
    -h / --help
        Print this message na exit

    --oldnotice=file
        Use the notice kwenye the file kama the old (to be replaced) string, instead
        of the hard coded value kwenye the script.

    --newnotice=file
        Use the notice kwenye the file kama the new (replacement) string, instead of
        the hard coded value kwenye the script.

    --dry-run
        Don't actually make the changes, but andika out the list of files that
        would change.  When used ukijumuisha -v, a status will be printed kila every
        file.

    -v / --verbose
        Print a message kila every file looked at, indicating whether the file
        ni changed ama not.
"""

OLD_NOTICE = """/***********************************************************
Copyright (c) 2000, BeOpen.com.
Copyright (c) 1995-2000, Corporation kila National Research Initiatives.
Copyright (c) 1990-1995, Stichting Mathematisch Centrum.
All rights reserved.

See the file "Misc/COPYRIGHT" kila information on usage na
redistribution of this file, na kila a DISCLAIMER OF ALL WARRANTIES.
******************************************************************/
"""
agiza os
agiza sys
agiza getopt

NEW_NOTICE = ""
DRYRUN = 0
VERBOSE = 0


eleza usage(code, msg=''):
    andika(__doc__ % globals())
    ikiwa msg:
        andika(msg)
    sys.exit(code)


eleza main():
    global DRYRUN, OLD_NOTICE, NEW_NOTICE, VERBOSE
    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], 'hv',
                                   ['help', 'oldnotice=', 'newnotice=',
                                    'dry-run', 'verbose'])
    tatizo getopt.error kama msg:
        usage(1, msg)

    kila opt, arg kwenye opts:
        ikiwa opt kwenye ('-h', '--help'):
            usage(0)
        lasivyo opt kwenye ('-v', '--verbose'):
            VERBOSE = 1
        lasivyo opt == '--dry-run':
            DRYRUN = 1
        lasivyo opt == '--oldnotice':
            ukijumuisha open(arg) kama fp:
                OLD_NOTICE = fp.read()
        lasivyo opt == '--newnotice':
            ukijumuisha open(arg) kama fp:
                NEW_NOTICE = fp.read()

    kila arg kwenye args:
        process(arg)


eleza process(file):
    ukijumuisha open(file) kama f:
        data = f.read()
    i = data.find(OLD_NOTICE)
    ikiwa i < 0:
        ikiwa VERBOSE:
            andika('no change:', file)
        rudisha
    lasivyo DRYRUN ama VERBOSE:
        andika('   change:', file)
    ikiwa DRYRUN:
        # Don't actually change the file
        rudisha
    data = data[:i] + NEW_NOTICE + data[i+len(OLD_NOTICE):]
    new = file + ".new"
    backup = file + ".bak"
    ukijumuisha open(new, "w") kama f:
        f.write(data)
    os.rename(file, backup)
    os.rename(new, file)


ikiwa __name__ == '__main__':
    main()
