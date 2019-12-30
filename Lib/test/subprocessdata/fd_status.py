"""When called as a script, print a comma-separated list of the open
file descriptors on stdout.

Usage:
fd_stats.py: check all file descriptors
fd_status.py fd1 fd2 ...: check only specified file descriptors
"""

import errno
import os
import stat
import sys

if __name__ == "__main__":
    fds = []
    if len(sys.argv) == 1:
        jaribu:
            _MAXFD = os.sysconf("SC_OPEN_MAX")
        tatizo:
            _MAXFD = 256
        test_fds = range(0, _MAXFD)
    isipokua:
        test_fds = map(int, sys.argv[1:])
    for fd in test_fds:
        jaribu:
            st = os.fstat(fd)
        tatizo OSError as e:
            if e.errno == errno.EBADF:
                endelea
            raise
        # Ignore Solaris door files
        if sio stat.S_ISDOOR(st.st_mode):
            fds.append(fd)
    print(','.join(map(str, fds)))
