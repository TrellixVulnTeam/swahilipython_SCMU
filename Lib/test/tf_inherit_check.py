# Helper script kila test_tempfile.py.  argv[2] ni the number of a file
# descriptor which should _not_ be open.  Check this by attempting to
# write to it -- ikiwa we succeed, something ni wrong.

agiza sys
agiza os
kutoka test.support agiza SuppressCrashReport

ukijumuisha SuppressCrashReport():
    verbose = (sys.argv[1] == 'v')
    jaribu:
        fd = int(sys.argv[2])

        jaribu:
            os.write(fd, b"blat")
        except OSError:
            # Success -- could sio write to fd.
            sys.exit(0)
        isipokua:
            ikiwa verbose:
                sys.stderr.write("fd %d ni open kwenye child" % fd)
            sys.exit(1)

    except Exception:
        ikiwa verbose:
            raise
        sys.exit(1)
