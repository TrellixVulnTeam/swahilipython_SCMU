"""Various Windows specific bits and pieces."""

agiza sys

ikiwa sys.platform != 'win32':  # pragma: no cover
    raise ImportError('win32 only')

agiza _winapi
agiza itertools
agiza msvcrt
agiza os
agiza subprocess
agiza tempfile
agiza warnings


__all__ = 'pipe', 'Popen', 'PIPE', 'PipeHandle'


# Constants/globals


BUFSIZE = 8192
PIPE = subprocess.PIPE
STDOUT = subprocess.STDOUT
_mmap_counter = itertools.count()


# Replacement for os.pipe() using handles instead of fds


eleza pipe(*, duplex=False, overlapped=(True, True), bufsize=BUFSIZE):
    """Like os.pipe() but with overlapped support and using handles not fds."""
    address = tempfile.mktemp(
        prefix=r'\\.\pipe\python-pipe-{:d}-{:d}-'.format(
            os.getpid(), next(_mmap_counter)))

    ikiwa duplex:
        openmode = _winapi.PIPE_ACCESS_DUPLEX
        access = _winapi.GENERIC_READ | _winapi.GENERIC_WRITE
        obsize, ibsize = bufsize, bufsize
    else:
        openmode = _winapi.PIPE_ACCESS_INBOUND
        access = _winapi.GENERIC_WRITE
        obsize, ibsize = 0, bufsize

    openmode |= _winapi.FILE_FLAG_FIRST_PIPE_INSTANCE

    ikiwa overlapped[0]:
        openmode |= _winapi.FILE_FLAG_OVERLAPPED

    ikiwa overlapped[1]:
        flags_and_attribs = _winapi.FILE_FLAG_OVERLAPPED
    else:
        flags_and_attribs = 0

    h1 = h2 = None
    try:
        h1 = _winapi.CreateNamedPipe(
            address, openmode, _winapi.PIPE_WAIT,
            1, obsize, ibsize, _winapi.NMPWAIT_WAIT_FOREVER, _winapi.NULL)

        h2 = _winapi.CreateFile(
            address, access, 0, _winapi.NULL, _winapi.OPEN_EXISTING,
            flags_and_attribs, _winapi.NULL)

        ov = _winapi.ConnectNamedPipe(h1, overlapped=True)
        ov.GetOverlappedResult(True)
        rudisha h1, h2
    except:
        ikiwa h1 is not None:
            _winapi.CloseHandle(h1)
        ikiwa h2 is not None:
            _winapi.CloseHandle(h2)
        raise


# Wrapper for a pipe handle


kundi PipeHandle:
    """Wrapper for an overlapped pipe handle which is vaguely file-object like.

    The IOCP event loop can use these instead of socket objects.
    """
    eleza __init__(self, handle):
        self._handle = handle

    eleza __repr__(self):
        ikiwa self._handle is not None:
            handle = f'handle={self._handle!r}'
        else:
            handle = 'closed'
        rudisha f'<{self.__class__.__name__} {handle}>'

    @property
    eleza handle(self):
        rudisha self._handle

    eleza fileno(self):
        ikiwa self._handle is None:
            raise ValueError("I/O operation on closed pipe")
        rudisha self._handle

    eleza close(self, *, CloseHandle=_winapi.CloseHandle):
        ikiwa self._handle is not None:
            CloseHandle(self._handle)
            self._handle = None

    eleza __del__(self, _warn=warnings.warn):
        ikiwa self._handle is not None:
            _warn(f"unclosed {self!r}", ResourceWarning, source=self)
            self.close()

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, t, v, tb):
        self.close()


# Replacement for subprocess.Popen using overlapped pipe handles


kundi Popen(subprocess.Popen):
    """Replacement for subprocess.Popen using overlapped pipe handles.

    The stdin, stdout, stderr are None or instances of PipeHandle.
    """
    eleza __init__(self, args, stdin=None, stdout=None, stderr=None, **kwds):
        assert not kwds.get('universal_newlines')
        assert kwds.get('bufsize', 0) == 0
        stdin_rfd = stdout_wfd = stderr_wfd = None
        stdin_wh = stdout_rh = stderr_rh = None
        ikiwa stdin == PIPE:
            stdin_rh, stdin_wh = pipe(overlapped=(False, True), duplex=True)
            stdin_rfd = msvcrt.open_osfhandle(stdin_rh, os.O_RDONLY)
        else:
            stdin_rfd = stdin
        ikiwa stdout == PIPE:
            stdout_rh, stdout_wh = pipe(overlapped=(True, False))
            stdout_wfd = msvcrt.open_osfhandle(stdout_wh, 0)
        else:
            stdout_wfd = stdout
        ikiwa stderr == PIPE:
            stderr_rh, stderr_wh = pipe(overlapped=(True, False))
            stderr_wfd = msvcrt.open_osfhandle(stderr_wh, 0)
        elikiwa stderr == STDOUT:
            stderr_wfd = stdout_wfd
        else:
            stderr_wfd = stderr
        try:
            super().__init__(args, stdin=stdin_rfd, stdout=stdout_wfd,
                             stderr=stderr_wfd, **kwds)
        except:
            for h in (stdin_wh, stdout_rh, stderr_rh):
                ikiwa h is not None:
                    _winapi.CloseHandle(h)
            raise
        else:
            ikiwa stdin_wh is not None:
                self.stdin = PipeHandle(stdin_wh)
            ikiwa stdout_rh is not None:
                self.stdout = PipeHandle(stdout_rh)
            ikiwa stderr_rh is not None:
                self.stderr = PipeHandle(stderr_rh)
        finally:
            ikiwa stdin == PIPE:
                os.close(stdin_rfd)
            ikiwa stdout == PIPE:
                os.close(stdout_wfd)
            ikiwa stderr == PIPE:
                os.close(stderr_wfd)
