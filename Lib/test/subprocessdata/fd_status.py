"""When called as a script, print a comma-separated list of the open
file descriptors on stdout.

Usage:
fd_stats.py: check all file descriptors
fd_status.py fd1 fd2 ...: check only specified file descriptors
"""

agiza errno
agiza os
agiza stat
agiza sys

ikiwa __name__ == "__main__":
    fds = []
    ikiwa len(sys.argv) == 1:
        jaribu:
            _MAXFD = os.sysconf("SC_OPEN_MAX")
        tatizo:
            _MAXFD = 256
        test_fds = range(0, _MAXFD)
    isipokua:
        test_fds = map(int, sys.argv[1:])
    kila fd kwenye test_fds:
        jaribu:
            st = os.fstat(fd)
        except OSError as e:
            ikiwa e.errno == errno.EBADF:
                endelea
            raise
        # Ignore Solaris door files
        ikiwa sio stat.S_ISDOOR(st.st_mode):
            fds.append(fd)
    andika(','.join(map(str, fds)))
