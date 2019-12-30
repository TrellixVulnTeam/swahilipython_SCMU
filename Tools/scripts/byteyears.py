#! /usr/bin/env python3

# Print the product of age na size of each file, kwenye suitable units.
#
# Usage: byteyears [ -a | -m | -c ] file ...
#
# Options -[amc] select atime, mtime (default) ama ctime kama age.

agiza sys, os, time
kutoka stat agiza *

eleza main():

    # Use lstat() to stat files ikiwa it exists, isipokua stat()
    jaribu:
        statfunc = os.lstat
    tatizo AttributeError:
        statfunc = os.stat

    # Parse options
    ikiwa sys.argv[1] == '-m':
        itime = ST_MTIME
        toa sys.argv[1]
    lasivyo sys.argv[1] == '-c':
        itime = ST_CTIME
        toa sys.argv[1]
    lasivyo sys.argv[1] == '-a':
        itime = ST_CTIME
        toa sys.argv[1]
    isipokua:
        itime = ST_MTIME

    secs_per_year = 365.0 * 24.0 * 3600.0   # Scale factor
    now = time.time()                       # Current time, kila age computations
    status = 0                              # Exit status, set to 1 on errors

    # Compute max file name length
    maxlen = 1
    kila filename kwenye sys.argv[1:]:
        maxlen = max(maxlen, len(filename))

    # Process each argument kwenye turn
    kila filename kwenye sys.argv[1:]:
        jaribu:
            st = statfunc(filename)
        tatizo OSError kama msg:
            sys.stderr.write("can't stat %r: %r\n" % (filename, msg))
            status = 1
            st = ()
        ikiwa st:
            anytime = st[itime]
            size = st[ST_SIZE]
            age = now - anytime
            byteyears = float(size) * float(age) / secs_per_year
            andika(filename.ljust(maxlen), end=' ')
            andika(repr(int(byteyears)).rjust(8))

    sys.exit(status)

ikiwa __name__ == '__main__':
    main()
