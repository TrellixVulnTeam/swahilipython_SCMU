# Helper script for test_tempfile.py.  argv[2] is the number of a file
# descriptor which should _not_ be open.  Check this by attempting to
# write to it -- ikiwa we succeed, something is wrong.

agiza sys
agiza os
kutoka test.support agiza SuppressCrashReport

with SuppressCrashReport():
    verbose = (sys.argv[1] == 'v')
    try:
        fd = int(sys.argv[2])

        try:
            os.write(fd, b"blat")
        except OSError:
            # Success -- could not write to fd.
            sys.exit(0)
        else:
            ikiwa verbose:
                sys.stderr.write("fd %d is open in child" % fd)
            sys.exit(1)

    except Exception:
        ikiwa verbose:
            raise
        sys.exit(1)
