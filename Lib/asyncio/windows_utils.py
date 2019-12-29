"""Various Windows specific bits na pieces."""

agiza sys

ikiwa sys.platform != 'win32':  # pragma: no cover
    ashiria ImportError('win32 only')

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


# Replacement kila os.pipe() using handles instead of fds


eleza pipe(*, duplex=Uongo, overlapped=(Kweli, Kweli), bufsize=BUFSIZE):
    """Like os.pipe() but with overlapped support na using handles sio fds."""
    address = tempfile.mktemp(
        prefix=r'\\.\pipe\python-pipe-{:d}-{:d}-'.format(
            os.getpid(), next(_mmap_counter)))

    ikiwa duplex:
        openmode = _winapi.PIPE_ACCESS_DUPLEX
        access = _winapi.GENERIC_READ | _winapi.GENERIC_WRITE
        obsize, ibsize = bufsize, bufsize
    isipokua:
        openmode = _winapi.PIPE_ACCESS_INBOUND
        access = _winapi.GENERIC_WRITE
        obsize, ibsize = 0, bufsize

    openmode |= _winapi.FILE_FLAG_FIRST_PIPE_INSTANCE

    ikiwa overlapped[0]:
        openmode |= _winapi.FILE_FLAG_OVERLAPPED

    ikiwa overlapped[1]:
        flags_and_attribs = _winapi.FILE_FLAG_OVERLAPPED
    isipokua:
        flags_and_attribs = 0

    h1 = h2 = Tupu
    jaribu:
        h1 = _winapi.CreateNamedPipe(
            address, openmode, _winapi.PIPE_WAIT,
            1, obsize, ibsize, _winapi.NMPWAIT_WAIT_FOREVER, _winapi.NULL)

        h2 = _winapi.CreateFile(
            address, access, 0, _winapi.NULL, _winapi.OPEN_EXISTING,
            flags_and_attribs, _winapi.NULL)

        ov = _winapi.ConnectNamedPipe(h1, overlapped=Kweli)
        ov.GetOverlappedResult(Kweli)
        rudisha h1, h2
    except:
        ikiwa h1 ni sio Tupu:
            _winapi.CloseHandle(h1)
        ikiwa h2 ni sio Tupu:
            _winapi.CloseHandle(h2)
        ashiria


# Wrapper kila a pipe handle


kundi PipeHandle:
    """Wrapper kila an overlapped pipe handle which ni vaguely file-object like.

    The IOCP event loop can use these instead of socket objects.
    """
    eleza __init__(self, handle):
        self._handle = handle

    eleza __repr__(self):
        ikiwa self._handle ni sio Tupu:
            handle = f'handle={self._handle!r}'
        isipokua:
            handle = 'closed'
        rudisha f'<{self.__class__.__name__} {handle}>'

    @property
    eleza handle(self):
        rudisha self._handle

    eleza fileno(self):
        ikiwa self._handle ni Tupu:
            ashiria ValueError("I/O operation on closed pipe")
        rudisha self._handle

    eleza close(self, *, CloseHandle=_winapi.CloseHandle):
        ikiwa self._handle ni sio Tupu:
            CloseHandle(self._handle)
            self._handle = Tupu

    eleza __del__(self, _warn=warnings.warn):
        ikiwa self._handle ni sio Tupu:
            _warn(f"unclosed {self!r}", ResourceWarning, source=self)
            self.close()

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, t, v, tb):
        self.close()


# Replacement kila subprocess.Popen using overlapped pipe handles


kundi Popen(subprocess.Popen):
    """Replacement kila subprocess.Popen using overlapped pipe handles.

    The stdin, stdout, stderr are Tupu ama instances of PipeHandle.
    """
    eleza __init__(self, args, stdin=Tupu, stdout=Tupu, stderr=Tupu, **kwds):
        assert sio kwds.get('universal_newlines')
        assert kwds.get('bufsize', 0) == 0
        stdin_rfd = stdout_wfd = stderr_wfd = Tupu
        stdin_wh = stdout_rh = stderr_rh = Tupu
        ikiwa stdin == PIPE:
            stdin_rh, stdin_wh = pipe(overlapped=(Uongo, Kweli), duplex=Kweli)
            stdin_rfd = msvcrt.open_osfhandle(stdin_rh, os.O_RDONLY)
        isipokua:
            stdin_rfd = stdin
        ikiwa stdout == PIPE:
            stdout_rh, stdout_wh = pipe(overlapped=(Kweli, Uongo))
            stdout_wfd = msvcrt.open_osfhandle(stdout_wh, 0)
        isipokua:
            stdout_wfd = stdout
        ikiwa stderr == PIPE:
            stderr_rh, stderr_wh = pipe(overlapped=(Kweli, Uongo))
            stderr_wfd = msvcrt.open_osfhandle(stderr_wh, 0)
        elikiwa stderr == STDOUT:
            stderr_wfd = stdout_wfd
        isipokua:
            stderr_wfd = stderr
        jaribu:
            super().__init__(args, stdin=stdin_rfd, stdout=stdout_wfd,
                             stderr=stderr_wfd, **kwds)
        except:
            kila h kwenye (stdin_wh, stdout_rh, stderr_rh):
                ikiwa h ni sio Tupu:
                    _winapi.CloseHandle(h)
            ashiria
        isipokua:
            ikiwa stdin_wh ni sio Tupu:
                self.stdin = PipeHandle(stdin_wh)
            ikiwa stdout_rh ni sio Tupu:
                self.stdout = PipeHandle(stdout_rh)
            ikiwa stderr_rh ni sio Tupu:
                self.stderr = PipeHandle(stderr_rh)
        mwishowe:
            ikiwa stdin == PIPE:
                os.close(stdin_rfd)
            ikiwa stdout == PIPE:
                os.close(stdout_wfd)
            ikiwa stderr == PIPE:
                os.close(stderr_wfd)
