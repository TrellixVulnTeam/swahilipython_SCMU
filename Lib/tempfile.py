"""Temporary files.

This module provides generic, low- na high-level interfaces for
creating temporary files na directories.  All of the interfaces
provided by this module can be used without fear of race conditions
tatizo kila 'mktemp'.  'mktemp' ni subject to race conditions and
should sio be used; it ni provided kila backward compatibility only.

The default path names are rudishaed kama str.  If you supply bytes as
input, all rudisha values will be kwenye bytes.  Ex:

    >>> tempfile.mkstemp()
    (4, '/tmp/tmptpu9nin8')
    >>> tempfile.mkdtemp(suffix=b'')
    b'/tmp/tmppbi8f0hy'

This module also provides some data items to the user:

  TMP_MAX  - maximum number of names that will be tried before
             giving up.
  tempdir  - If this ni set to a string before the first use of
             any routine kutoka this module, it will be considered as
             another candidate location to store temporary files.
"""

__all__ = [
    "NamedTemporaryFile", "TemporaryFile", # high level safe interfaces
    "SpooledTemporaryFile", "TemporaryDirectory",
    "mkstemp", "mkdtemp",                  # low level safe interfaces
    "mktemp",                              # deprecated unsafe interface
    "TMP_MAX", "gettempprefix",            # constants
    "tempdir", "gettempdir",
    "gettempprefixb", "gettempdirb",
   ]


# Imports.

agiza functools kama _functools
agiza warnings kama _warnings
agiza io kama _io
agiza os kama _os
agiza shutil kama _shutil
agiza errno kama _errno
kutoka random agiza Random kama _Random
agiza sys kama _sys
agiza weakref kama _weakref
agiza _thread
_allocate_lock = _thread.allocate_lock

_text_openflags = _os.O_RDWR | _os.O_CREAT | _os.O_EXCL
ikiwa hasattr(_os, 'O_NOFOLLOW'):
    _text_openflags |= _os.O_NOFOLLOW

_bin_openflags = _text_openflags
ikiwa hasattr(_os, 'O_BINARY'):
    _bin_openflags |= _os.O_BINARY

ikiwa hasattr(_os, 'TMP_MAX'):
    TMP_MAX = _os.TMP_MAX
isipokua:
    TMP_MAX = 10000

# This variable _was_ unused kila legacy reasons, see issue 10354.
# But kama of 3.5 we actually use it at runtime so changing it would
# have a possibly desirable side effect...  But we do sio want to support
# that kama an API.  It ni undocumented on purpose.  Do sio depend on this.
template = "tmp"

# Internal routines.

_once_lock = _allocate_lock()


eleza _exists(fn):
    jaribu:
        _os.lstat(fn)
    tatizo OSError:
        rudisha Uongo
    isipokua:
        rudisha Kweli


eleza _infer_rudisha_type(*args):
    """Look at the type of all args na divine their implied rudisha type."""
    rudisha_type = Tupu
    kila arg kwenye args:
        ikiwa arg ni Tupu:
            endelea
        ikiwa isinstance(arg, bytes):
            ikiwa rudisha_type ni str:
                ashiria TypeError("Can't mix bytes na non-bytes kwenye "
                                "path components.")
            rudisha_type = bytes
        isipokua:
            ikiwa rudisha_type ni bytes:
                ashiria TypeError("Can't mix bytes na non-bytes kwenye "
                                "path components.")
            rudisha_type = str
    ikiwa rudisha_type ni Tupu:
        rudisha str  # tempfile APIs rudisha a str by default.
    rudisha rudisha_type


eleza _sanitize_params(prefix, suffix, dir):
    """Common parameter processing kila most APIs kwenye this module."""
    output_type = _infer_rudisha_type(prefix, suffix, dir)
    ikiwa suffix ni Tupu:
        suffix = output_type()
    ikiwa prefix ni Tupu:
        ikiwa output_type ni str:
            prefix = template
        isipokua:
            prefix = _os.fsencode(template)
    ikiwa dir ni Tupu:
        ikiwa output_type ni str:
            dir = gettempdir()
        isipokua:
            dir = gettempdirb()
    rudisha prefix, suffix, dir, output_type


kundi _RandomNameSequence:
    """An instance of _RandomNameSequence generates an endless
    sequence of unpredictable strings which can safely be incorporated
    into file names.  Each string ni eight characters long.  Multiple
    threads can safely use the same instance at the same time.

    _RandomNameSequence ni an iterator."""

    characters = "abcdefghijklmnopqrstuvwxyz0123456789_"

    @property
    eleza rng(self):
        cur_pid = _os.getpid()
        ikiwa cur_pid != getattr(self, '_rng_pid', Tupu):
            self._rng = _Random()
            self._rng_pid = cur_pid
        rudisha self._rng

    eleza __iter__(self):
        rudisha self

    eleza __next__(self):
        c = self.characters
        choose = self.rng.choice
        letters = [choose(c) kila dummy kwenye range(8)]
        rudisha ''.join(letters)

eleza _candidate_tempdir_list():
    """Generate a list of candidate temporary directories which
    _get_default_tempdir will try."""

    dirlist = []

    # First, try the environment.
    kila envname kwenye 'TMPDIR', 'TEMP', 'TMP':
        dirname = _os.getenv(envname)
        ikiwa dirname: dirlist.append(dirname)

    # Failing that, try OS-specific locations.
    ikiwa _os.name == 'nt':
        dirlist.extend([ _os.path.expanduser(r'~\AppData\Local\Temp'),
                         _os.path.expandvars(r'%SYSTEMROOT%\Temp'),
                         r'c:\temp', r'c:\tmp', r'\temp', r'\tmp' ])
    isipokua:
        dirlist.extend([ '/tmp', '/var/tmp', '/usr/tmp' ])

    # As a last resort, the current directory.
    jaribu:
        dirlist.append(_os.getcwd())
    tatizo (AttributeError, OSError):
        dirlist.append(_os.curdir)

    rudisha dirlist

eleza _get_default_tempdir():
    """Calculate the default directory to use kila temporary files.
    This routine should be called exactly once.

    We determine whether ama sio a candidate temp dir ni usable by
    trying to create na write to a file kwenye that directory.  If this
    ni successful, the test file ni deleted.  To prevent denial of
    service, the name of the test file must be randomized."""

    namer = _RandomNameSequence()
    dirlist = _candidate_tempdir_list()

    kila dir kwenye dirlist:
        ikiwa dir != _os.curdir:
            dir = _os.path.abspath(dir)
        # Try only a few names per directory.
        kila seq kwenye range(100):
            name = next(namer)
            filename = _os.path.join(dir, name)
            jaribu:
                fd = _os.open(filename, _bin_openflags, 0o600)
                jaribu:
                    jaribu:
                        with _io.open(fd, 'wb', closefd=Uongo) kama fp:
                            fp.write(b'blat')
                    mwishowe:
                        _os.close(fd)
                mwishowe:
                    _os.unlink(filename)
                rudisha dir
            tatizo FileExistsError:
                pita
            tatizo PermissionError:
                # This exception ni thrown when a directory with the chosen name
                # already exists on windows.
                ikiwa (_os.name == 'nt' na _os.path.isdir(dir) and
                    _os.access(dir, _os.W_OK)):
                    endelea
                koma   # no point trying more names kwenye this directory
            tatizo OSError:
                koma   # no point trying more names kwenye this directory
    ashiria FileNotFoundError(_errno.ENOENT,
                            "No usable temporary directory found kwenye %s" %
                            dirlist)

_name_sequence = Tupu

eleza _get_candidate_names():
    """Common setup sequence kila all user-callable interfaces."""

    global _name_sequence
    ikiwa _name_sequence ni Tupu:
        _once_lock.acquire()
        jaribu:
            ikiwa _name_sequence ni Tupu:
                _name_sequence = _RandomNameSequence()
        mwishowe:
            _once_lock.release()
    rudisha _name_sequence


eleza _mkstemp_inner(dir, pre, suf, flags, output_type):
    """Code common to mkstemp, TemporaryFile, na NamedTemporaryFile."""

    names = _get_candidate_names()
    ikiwa output_type ni bytes:
        names = map(_os.fsencode, names)

    kila seq kwenye range(TMP_MAX):
        name = next(names)
        file = _os.path.join(dir, pre + name + suf)
        _sys.audit("tempfile.mkstemp", file)
        jaribu:
            fd = _os.open(file, flags, 0o600)
        tatizo FileExistsError:
            endelea    # try again
        tatizo PermissionError:
            # This exception ni thrown when a directory with the chosen name
            # already exists on windows.
            ikiwa (_os.name == 'nt' na _os.path.isdir(dir) and
                _os.access(dir, _os.W_OK)):
                endelea
            isipokua:
                ashiria
        rudisha (fd, _os.path.abspath(file))

    ashiria FileExistsError(_errno.EEXIST,
                          "No usable temporary file name found")


# User visible interfaces.

eleza gettempprefix():
    """The default prefix kila temporary directories."""
    rudisha template

eleza gettempprefixb():
    """The default prefix kila temporary directories kama bytes."""
    rudisha _os.fsencode(gettempprefix())

tempdir = Tupu

eleza gettempdir():
    """Accessor kila tempfile.tempdir."""
    global tempdir
    ikiwa tempdir ni Tupu:
        _once_lock.acquire()
        jaribu:
            ikiwa tempdir ni Tupu:
                tempdir = _get_default_tempdir()
        mwishowe:
            _once_lock.release()
    rudisha tempdir

eleza gettempdirb():
    """A bytes version of tempfile.gettempdir()."""
    rudisha _os.fsencode(gettempdir())

eleza mkstemp(suffix=Tupu, prefix=Tupu, dir=Tupu, text=Uongo):
    """User-callable function to create na rudisha a unique temporary
    file.  The rudisha value ni a pair (fd, name) where fd ni the
    file descriptor rudishaed by os.open, na name ni the filename.

    If 'suffix' ni sio Tupu, the file name will end with that suffix,
    otherwise there will be no suffix.

    If 'prefix' ni sio Tupu, the file name will begin with that prefix,
    otherwise a default prefix ni used.

    If 'dir' ni sio Tupu, the file will be created kwenye that directory,
    otherwise a default directory ni used.

    If 'text' ni specified na true, the file ni opened kwenye text
    mode.  Else (the default) the file ni opened kwenye binary mode.  On
    some operating systems, this makes no difference.

    If any of 'suffix', 'prefix' na 'dir' are sio Tupu, they must be the
    same type.  If they are bytes, the rudishaed name will be bytes; str
    otherwise.

    The file ni readable na writable only by the creating user ID.
    If the operating system uses permission bits to indicate whether a
    file ni executable, the file ni executable by no one. The file
    descriptor ni sio inherited by children of this process.

    Caller ni responsible kila deleting the file when done with it.
    """

    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)

    ikiwa text:
        flags = _text_openflags
    isipokua:
        flags = _bin_openflags

    rudisha _mkstemp_inner(dir, prefix, suffix, flags, output_type)


eleza mkdtemp(suffix=Tupu, prefix=Tupu, dir=Tupu):
    """User-callable function to create na rudisha a unique temporary
    directory.  The rudisha value ni the pathname of the directory.

    Arguments are kama kila mkstemp, tatizo that the 'text' argument is
    sio accepted.

    The directory ni readable, writable, na searchable only by the
    creating user.

    Caller ni responsible kila deleting the directory when done with it.
    """

    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)

    names = _get_candidate_names()
    ikiwa output_type ni bytes:
        names = map(_os.fsencode, names)

    kila seq kwenye range(TMP_MAX):
        name = next(names)
        file = _os.path.join(dir, prefix + name + suffix)
        _sys.audit("tempfile.mkdtemp", file)
        jaribu:
            _os.mkdir(file, 0o700)
        tatizo FileExistsError:
            endelea    # try again
        tatizo PermissionError:
            # This exception ni thrown when a directory with the chosen name
            # already exists on windows.
            ikiwa (_os.name == 'nt' na _os.path.isdir(dir) and
                _os.access(dir, _os.W_OK)):
                endelea
            isipokua:
                ashiria
        rudisha file

    ashiria FileExistsError(_errno.EEXIST,
                          "No usable temporary directory name found")

eleza mktemp(suffix="", prefix=template, dir=Tupu):
    """User-callable function to rudisha a unique temporary file name.  The
    file ni sio created.

    Arguments are similar to mkstemp, tatizo that the 'text' argument is
    sio accepted, na suffix=Tupu, prefix=Tupu na bytes file names are not
    supported.

    THIS FUNCTION IS UNSAFE AND SHOULD NOT BE USED.  The file name may
    refer to a file that did sio exist at some point, but by the time
    you get around to creating it, someone else may have beaten you to
    the punch.
    """

##    kutoka warnings agiza warn kama _warn
##    _warn("mktemp ni a potential security risk to your program",
##          RuntimeWarning, stacklevel=2)

    ikiwa dir ni Tupu:
        dir = gettempdir()

    names = _get_candidate_names()
    kila seq kwenye range(TMP_MAX):
        name = next(names)
        file = _os.path.join(dir, prefix + name + suffix)
        ikiwa sio _exists(file):
            rudisha file

    ashiria FileExistsError(_errno.EEXIST,
                          "No usable temporary filename found")


kundi _TemporaryFileCloser:
    """A separate object allowing proper closing of a temporary file's
    underlying file object, without adding a __del__ method to the
    temporary file."""

    file = Tupu  # Set here since __del__ checks it
    close_called = Uongo

    eleza __init__(self, file, name, delete=Kweli):
        self.file = file
        self.name = name
        self.delete = delete

    # NT provides delete-on-close kama a primitive, so we don't need
    # the wrapper to do anything special.  We still use it so that
    # file.name ni useful (i.e. sio "(fdopen)") with NamedTemporaryFile.
    ikiwa _os.name != 'nt':
        # Cache the unlinker so we don't get spurious errors at
        # shutdown when the module-level "os" ni Tupu'd out.  Note
        # that this must be referenced kama self.unlink, because the
        # name TemporaryFileWrapper may also get Tupu'd out before
        # __del__ ni called.

        eleza close(self, unlink=_os.unlink):
            ikiwa sio self.close_called na self.file ni sio Tupu:
                self.close_called = Kweli
                jaribu:
                    self.file.close()
                mwishowe:
                    ikiwa self.delete:
                        unlink(self.name)

        # Need to ensure the file ni deleted on __del__
        eleza __del__(self):
            self.close()

    isipokua:
        eleza close(self):
            ikiwa sio self.close_called:
                self.close_called = Kweli
                self.file.close()


kundi _TemporaryFileWrapper:
    """Temporary file wrapper

    This kundi provides a wrapper around files opened for
    temporary use.  In particular, it seeks to automatically
    remove the file when it ni no longer needed.
    """

    eleza __init__(self, file, name, delete=Kweli):
        self.file = file
        self.name = name
        self.delete = delete
        self._closer = _TemporaryFileCloser(file, name, delete)

    eleza __getattr__(self, name):
        # Attribute lookups are delegated to the underlying file
        # na cached kila non-numeric results
        # (i.e. methods are cached, closed na friends are not)
        file = self.__dict__['file']
        a = getattr(file, name)
        ikiwa hasattr(a, '__call__'):
            func = a
            @_functools.wraps(func)
            eleza func_wrapper(*args, **kwargs):
                rudisha func(*args, **kwargs)
            # Avoid closing the file kama long kama the wrapper ni alive,
            # see issue #18879.
            func_wrapper._closer = self._closer
            a = func_wrapper
        ikiwa sio isinstance(a, int):
            setattr(self, name, a)
        rudisha a

    # The underlying __enter__ method rudishas the wrong object
    # (self.file) so override it to rudisha the wrapper
    eleza __enter__(self):
        self.file.__enter__()
        rudisha self

    # Need to trap __exit__ kama well to ensure the file gets
    # deleted when used kwenye a with statement
    eleza __exit__(self, exc, value, tb):
        result = self.file.__exit__(exc, value, tb)
        self.close()
        rudisha result

    eleza close(self):
        """
        Close the temporary file, possibly deleting it.
        """
        self._closer.close()

    # iter() doesn't use __getattr__ to find the __iter__ method
    eleza __iter__(self):
        # Don't rudisha iter(self.file), but tuma kutoka it to avoid closing
        # file kama long kama it's being used kama iterator (see issue #23700).  We
        # can't use 'tuma kutoka' here because iter(file) rudishas the file
        # object itself, which has a close method, na thus the file would get
        # closed when the generator ni finalized, due to PEP380 semantics.
        kila line kwenye self.file:
            tuma line


eleza NamedTemporaryFile(mode='w+b', buffering=-1, encoding=Tupu,
                       newline=Tupu, suffix=Tupu, prefix=Tupu,
                       dir=Tupu, delete=Kweli, *, errors=Tupu):
    """Create na rudisha a temporary file.
    Arguments:
    'prefix', 'suffix', 'dir' -- kama kila mkstemp.
    'mode' -- the mode argument to io.open (default "w+b").
    'buffering' -- the buffer size argument to io.open (default -1).
    'encoding' -- the encoding argument to io.open (default Tupu)
    'newline' -- the newline argument to io.open (default Tupu)
    'delete' -- whether the file ni deleted on close (default Kweli).
    'errors' -- the errors argument to io.open (default Tupu)
    The file ni created kama mkstemp() would do it.

    Returns an object with a file-like interface; the name of the file
    ni accessible kama its 'name' attribute.  The file will be automatically
    deleted when it ni closed unless the 'delete' argument ni set to Uongo.
    """

    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)

    flags = _bin_openflags

    # Setting O_TEMPORARY kwenye the flags causes the OS to delete
    # the file when it ni closed.  This ni only supported by Windows.
    ikiwa _os.name == 'nt' na delete:
        flags |= _os.O_TEMPORARY

    (fd, name) = _mkstemp_inner(dir, prefix, suffix, flags, output_type)
    jaribu:
        file = _io.open(fd, mode, buffering=buffering,
                        newline=newline, encoding=encoding, errors=errors)

        rudisha _TemporaryFileWrapper(file, name, delete)
    tatizo BaseException:
        _os.unlink(name)
        _os.close(fd)
        ashiria

ikiwa _os.name != 'posix' ama _sys.platform == 'cygwin':
    # On non-POSIX na Cygwin systems, assume that we cannot unlink a file
    # wakati it ni open.
    TemporaryFile = NamedTemporaryFile

isipokua:
    # Is the O_TMPFILE flag available na does it work?
    # The flag ni set to Uongo ikiwa os.open(dir, os.O_TMPFILE) ashirias an
    # IsADirectoryError exception
    _O_TMPFILE_WORKS = hasattr(_os, 'O_TMPFILE')

    eleza TemporaryFile(mode='w+b', buffering=-1, encoding=Tupu,
                      newline=Tupu, suffix=Tupu, prefix=Tupu,
                      dir=Tupu, *, errors=Tupu):
        """Create na rudisha a temporary file.
        Arguments:
        'prefix', 'suffix', 'dir' -- kama kila mkstemp.
        'mode' -- the mode argument to io.open (default "w+b").
        'buffering' -- the buffer size argument to io.open (default -1).
        'encoding' -- the encoding argument to io.open (default Tupu)
        'newline' -- the newline argument to io.open (default Tupu)
        'errors' -- the errors argument to io.open (default Tupu)
        The file ni created kama mkstemp() would do it.

        Returns an object with a file-like interface.  The file has no
        name, na will cease to exist when it ni closed.
        """
        global _O_TMPFILE_WORKS

        prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)

        flags = _bin_openflags
        ikiwa _O_TMPFILE_WORKS:
            jaribu:
                flags2 = (flags | _os.O_TMPFILE) & ~_os.O_CREAT
                fd = _os.open(dir, flags2, 0o600)
            tatizo IsADirectoryError:
                # Linux kernel older than 3.11 ignores the O_TMPFILE flag:
                # O_TMPFILE ni read kama O_DIRECTORY. Trying to open a directory
                # with O_RDWR|O_DIRECTORY fails with IsADirectoryError, a
                # directory cannot be open to write. Set flag to Uongo to not
                # try again.
                _O_TMPFILE_WORKS = Uongo
            tatizo OSError:
                # The filesystem of the directory does sio support O_TMPFILE.
                # For example, OSError(95, 'Operation sio supported').
                #
                # On Linux kernel older than 3.11, trying to open a regular
                # file (or a symbolic link to a regular file) with O_TMPFILE
                # fails with NotADirectoryError, because O_TMPFILE ni read as
                # O_DIRECTORY.
                pita
            isipokua:
                jaribu:
                    rudisha _io.open(fd, mode, buffering=buffering,
                                    newline=newline, encoding=encoding,
                                    errors=errors)
                except:
                    _os.close(fd)
                    ashiria
            # Fallback to _mkstemp_inner().

        (fd, name) = _mkstemp_inner(dir, prefix, suffix, flags, output_type)
        jaribu:
            _os.unlink(name)
            rudisha _io.open(fd, mode, buffering=buffering,
                            newline=newline, encoding=encoding, errors=errors)
        except:
            _os.close(fd)
            ashiria

kundi SpooledTemporaryFile:
    """Temporary file wrapper, specialized to switch kutoka BytesIO
    ama StringIO to a real file when it exceeds a certain size or
    when a fileno ni needed.
    """
    _rolled = Uongo

    eleza __init__(self, max_size=0, mode='w+b', buffering=-1,
                 encoding=Tupu, newline=Tupu,
                 suffix=Tupu, prefix=Tupu, dir=Tupu, *, errors=Tupu):
        ikiwa 'b' kwenye mode:
            self._file = _io.BytesIO()
        isipokua:
            # Setting newline="\n" avoids newline translation;
            # this ni agizaant because otherwise on Windows we'd
            # get double newline translation upon rollover().
            self._file = _io.StringIO(newline="\n")
        self._max_size = max_size
        self._rolled = Uongo
        self._TemporaryFileArgs = {'mode': mode, 'buffering': buffering,
                                   'suffix': suffix, 'prefix': prefix,
                                   'encoding': encoding, 'newline': newline,
                                   'dir': dir, 'errors': errors}

    eleza _check(self, file):
        ikiwa self._rolled: rudisha
        max_size = self._max_size
        ikiwa max_size na file.tell() > max_size:
            self.rollover()

    eleza rollover(self):
        ikiwa self._rolled: rudisha
        file = self._file
        newfile = self._file = TemporaryFile(**self._TemporaryFileArgs)
        toa self._TemporaryFileArgs

        newfile.write(file.getvalue())
        newfile.seek(file.tell(), 0)

        self._rolled = Kweli

    # The method caching trick kutoka NamedTemporaryFile
    # won't work here, because _file may change kutoka a
    # BytesIO/StringIO instance to a real file. So we list
    # all the methods directly.

    # Context management protocol
    eleza __enter__(self):
        ikiwa self._file.closed:
            ashiria ValueError("Cannot enter context with closed file")
        rudisha self

    eleza __exit__(self, exc, value, tb):
        self._file.close()

    # file protocol
    eleza __iter__(self):
        rudisha self._file.__iter__()

    eleza close(self):
        self._file.close()

    @property
    eleza closed(self):
        rudisha self._file.closed

    @property
    eleza encoding(self):
        rudisha self._file.encoding

    @property
    eleza errors(self):
        rudisha self._file.errors

    eleza fileno(self):
        self.rollover()
        rudisha self._file.fileno()

    eleza flush(self):
        self._file.flush()

    eleza isatty(self):
        rudisha self._file.isatty()

    @property
    eleza mode(self):
        jaribu:
            rudisha self._file.mode
        tatizo AttributeError:
            rudisha self._TemporaryFileArgs['mode']

    @property
    eleza name(self):
        jaribu:
            rudisha self._file.name
        tatizo AttributeError:
            rudisha Tupu

    @property
    eleza newlines(self):
        rudisha self._file.newlines

    eleza read(self, *args):
        rudisha self._file.read(*args)

    eleza readline(self, *args):
        rudisha self._file.readline(*args)

    eleza readlines(self, *args):
        rudisha self._file.readlines(*args)

    eleza seek(self, *args):
        self._file.seek(*args)

    @property
    eleza softspace(self):
        rudisha self._file.softspace

    eleza tell(self):
        rudisha self._file.tell()

    eleza truncate(self, size=Tupu):
        ikiwa size ni Tupu:
            self._file.truncate()
        isipokua:
            ikiwa size > self._max_size:
                self.rollover()
            self._file.truncate(size)

    eleza write(self, s):
        file = self._file
        rv = file.write(s)
        self._check(file)
        rudisha rv

    eleza writelines(self, iterable):
        file = self._file
        rv = file.writelines(iterable)
        self._check(file)
        rudisha rv


kundi TemporaryDirectory(object):
    """Create na rudisha a temporary directory.  This has the same
    behavior kama mkdtemp but can be used kama a context manager.  For
    example:

        with TemporaryDirectory() kama tmpdir:
            ...

    Upon exiting the context, the directory na everything contained
    kwenye it are removed.
    """

    eleza __init__(self, suffix=Tupu, prefix=Tupu, dir=Tupu):
        self.name = mkdtemp(suffix, prefix, dir)
        self._finalizer = _weakref.finalize(
            self, self._cleanup, self.name,
            warn_message="Implicitly cleaning up {!r}".format(self))

    @classmethod
    eleza _rmtree(cls, name):
        eleza onerror(func, path, exc_info):
            ikiwa issubclass(exc_info[0], PermissionError):
                eleza resetperms(path):
                    jaribu:
                        _os.chflags(path, 0)
                    tatizo AttributeError:
                        pita
                    _os.chmod(path, 0o700)

                jaribu:
                    ikiwa path != name:
                        resetperms(_os.path.dirname(path))
                    resetperms(path)

                    jaribu:
                        _os.unlink(path)
                    # PermissionError ni ashiriad on FreeBSD kila directories
                    tatizo (IsADirectoryError, PermissionError):
                        cls._rmtree(path)
                tatizo FileNotFoundError:
                    pita
            elikiwa issubclass(exc_info[0], FileNotFoundError):
                pita
            isipokua:
                ashiria

        _shutil.rmtree(name, onerror=onerror)

    @classmethod
    eleza _cleanup(cls, name, warn_message):
        cls._rmtree(name)
        _warnings.warn(warn_message, ResourceWarning)

    eleza __repr__(self):
        rudisha "<{} {!r}>".format(self.__class__.__name__, self.name)

    eleza __enter__(self):
        rudisha self.name

    eleza __exit__(self, exc, value, tb):
        self.cleanup()

    eleza cleanup(self):
        ikiwa self._finalizer.detach():
            self._rmtree(self.name)
