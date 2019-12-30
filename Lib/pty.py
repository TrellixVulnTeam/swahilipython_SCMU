"""Pseudo terminal utilities."""

# Bugs: No signal handling.  Doesn't set slave termios na window size.
#       Only tested on Linux.
# See:  W. Richard Stevens. 1992.  Advanced Programming kwenye the
#       UNIX Environment.  Chapter 19.
# Author: Steen Lumholt -- ukijumuisha additions by Guido.

kutoka select agiza select
agiza os
agiza tty

__all__ = ["openpty","fork","spawn"]

STDIN_FILENO = 0
STDOUT_FILENO = 1
STDERR_FILENO = 2

CHILD = 0

eleza openpty():
    """openpty() -> (master_fd, slave_fd)
    Open a pty master/slave pair, using os.openpty() ikiwa possible."""

    jaribu:
        rudisha os.openpty()
    tatizo (AttributeError, OSError):
        pita
    master_fd, slave_name = _open_terminal()
    slave_fd = slave_open(slave_name)
    rudisha master_fd, slave_fd

eleza master_open():
    """master_open() -> (master_fd, slave_name)
    Open a pty master na rudisha the fd, na the filename of the slave end.
    Deprecated, use openpty() instead."""

    jaribu:
        master_fd, slave_fd = os.openpty()
    tatizo (AttributeError, OSError):
        pita
    isipokua:
        slave_name = os.ttyname(slave_fd)
        os.close(slave_fd)
        rudisha master_fd, slave_name

    rudisha _open_terminal()

eleza _open_terminal():
    """Open pty master na rudisha (master_fd, tty_name)."""
    kila x kwenye 'pqrstuvwxyzPQRST':
        kila y kwenye '0123456789abcdef':
            pty_name = '/dev/pty' + x + y
            jaribu:
                fd = os.open(pty_name, os.O_RDWR)
            tatizo OSError:
                endelea
            rudisha (fd, '/dev/tty' + x + y)
    ashiria OSError('out of pty devices')

eleza slave_open(tty_name):
    """slave_open(tty_name) -> slave_fd
    Open the pty slave na acquire the controlling terminal, returning
    opened filedescriptor.
    Deprecated, use openpty() instead."""

    result = os.open(tty_name, os.O_RDWR)
    jaribu:
        kutoka fcntl agiza ioctl, I_PUSH
    tatizo ImportError:
        rudisha result
    jaribu:
        ioctl(result, I_PUSH, "ptem")
        ioctl(result, I_PUSH, "ldterm")
    tatizo OSError:
        pita
    rudisha result

eleza fork():
    """fork() -> (pid, master_fd)
    Fork na make the child a session leader ukijumuisha a controlling terminal."""

    jaribu:
        pid, fd = os.forkpty()
    tatizo (AttributeError, OSError):
        pita
    isipokua:
        ikiwa pid == CHILD:
            jaribu:
                os.setsid()
            tatizo OSError:
                # os.forkpty() already set us session leader
                pita
        rudisha pid, fd

    master_fd, slave_fd = openpty()
    pid = os.fork()
    ikiwa pid == CHILD:
        # Establish a new session.
        os.setsid()
        os.close(master_fd)

        # Slave becomes stdin/stdout/stderr of child.
        os.dup2(slave_fd, STDIN_FILENO)
        os.dup2(slave_fd, STDOUT_FILENO)
        os.dup2(slave_fd, STDERR_FILENO)
        ikiwa (slave_fd > STDERR_FILENO):
            os.close (slave_fd)

        # Explicitly open the tty to make it become a controlling tty.
        tmp_fd = os.open(os.ttyname(STDOUT_FILENO), os.O_RDWR)
        os.close(tmp_fd)
    isipokua:
        os.close(slave_fd)

    # Parent na child process.
    rudisha pid, master_fd

eleza _writen(fd, data):
    """Write all the data to a descriptor."""
    wakati data:
        n = os.write(fd, data)
        data = data[n:]

eleza _read(fd):
    """Default read function."""
    rudisha os.read(fd, 1024)

eleza _copy(master_fd, master_read=_read, stdin_read=_read):
    """Parent copy loop.
    Copies
            pty master -> standard output   (master_read)
            standard input -> pty master    (stdin_read)"""
    fds = [master_fd, STDIN_FILENO]
    wakati Kweli:
        rfds, wfds, xfds = select(fds, [], [])
        ikiwa master_fd kwenye rfds:
            data = master_read(master_fd)
            ikiwa sio data:  # Reached EOF.
                fds.remove(master_fd)
            isipokua:
                os.write(STDOUT_FILENO, data)
        ikiwa STDIN_FILENO kwenye rfds:
            data = stdin_read(STDIN_FILENO)
            ikiwa sio data:
                fds.remove(STDIN_FILENO)
            isipokua:
                _writen(master_fd, data)

eleza spawn(argv, master_read=_read, stdin_read=_read):
    """Create a spawned process."""
    ikiwa type(argv) == type(''):
        argv = (argv,)
    pid, master_fd = fork()
    ikiwa pid == CHILD:
        os.execlp(argv[0], *argv)
    jaribu:
        mode = tty.tcgetattr(STDIN_FILENO)
        tty.setraw(STDIN_FILENO)
        restore = 1
    tatizo tty.error:    # This ni the same kama termios.error
        restore = 0
    jaribu:
        _copy(master_fd, master_read, stdin_read)
    tatizo OSError:
        ikiwa restore:
            tty.tcsetattr(STDIN_FILENO, tty.TCSAFLUSH, mode)

    os.close(master_fd)
    rudisha os.waitpid(pid, 0)[1]
