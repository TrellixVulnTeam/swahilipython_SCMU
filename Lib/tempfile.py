"""Temporary files.

This module provides generic, low- and high-level interfaces for
creating temporary files and directories.  All of the interfaces
provided by this module can be used without fear of race conditions
except for 'mktemp'.  'mktemp' is subject to race conditions and
should not be used; it is provided for backward compatibility only.

The default path names are returned as str.  If you supply bytes as
input, all rudisha values will be in bytes.  Ex:

    >>> tempfile.mkstemp()
    (4, '/tmp/tmptpu9nin8')
    >>> tempfile.mkdtemp(suffix=b'')
    b'/tmp/tmppbi8f0hy'

This module also provides some data items to the user:

  TMP_MAX  - maximum number of names that will be tried before
             giving up.
  tempdir  - If this is set to a string before the first use of
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

agiza functools as _functools
agiza warnings as _warnings
agiza io as _io
agiza os as _os
agiza shutil as _shutil
agiza errno as _errno
kutoka random agiza Random as _Random
agiza sys as _sys
agiza weakref as _weakref
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
else:
    TMP_MAX = 10000

# This variable _was_ unused for legacy reasons, see issue 10354.
# But as of 3.5 we actually use it at runtime so changing it would
# have a possibly desirable side effect...  But we do not want to support
# that as an API.  It is undocumented on purpose.  Do not depend on this.
template = "tmp"

# Internal routines.

_once_lock = _allocate_lock()


eleza _exists(fn):
    try:
        _os.lstat(fn)
    except OSError:
        rudisha False
    else:
        rudisha True


eleza _infer_return_type(*args):
    """Look at the type of all args and divine their implied rudisha type."""
    return_type = None
    for arg in args:
        ikiwa arg is None:
            continue
        ikiwa isinstance(arg, bytes):
            ikiwa return_type is str:
                raise TypeError("Can't mix bytes and non-bytes in "
                                "path components.")
            return_type = bytes
        else:
            ikiwa return_type is bytes:
                raise TypeError("Can't mix bytes and non-bytes in "
                                "path components.")
            return_type = str
    ikiwa return_type is None:
        rudisha str  # tempfile APIs rudisha a str by default.
    rudisha return_type


eleza _sanitize_params(prefix, suffix, dir):
    """Common parameter processing for most APIs in this module."""
    output_type = _infer_return_type(prefix, suffix, dir)
    ikiwa suffix is None:
        suffix = output_type()
    ikiwa prefix is None:
        ikiwa output_type is str:
            prefix = template
        else:
            prefix = _os.fsencode(template)
    ikiwa dir is None:
        ikiwa output_type is str:
            dir = gettempdir()
        else:
            dir = gettempdirb()
    rudisha prefix, suffix, dir, output_type


kundi _RandomNameSequence:
    """An instance of _RandomNameSequence generates an endless
    sequence of unpredictable strings which can safely be incorporated
    into file names.  Each string is eight characters long.  Multiple
    threads can safely use the same instance at the same time.

    _RandomNameSequence is an iterator."""

    characters = "abcdefghijklmnopqrstuvwxyz0123456789_"

    @property
    eleza rng(self):
        cur_pid = _os.getpid()
        ikiwa cur_pid != getattr(self, '_rng_pid', None):
            self._rng = _Random()
            self._rng_pid = cur_pid
        rudisha self._rng

    eleza __iter__(self):
        rudisha self

    eleza __next__(self):
        c = self.characters
        choose = self.rng.choice
        letters = [choose(c) for dummy in range(8)]
        rudisha ''.join(letters)

eleza _candidate_tempdir_list():
    """Generate a list of candidate temporary directories which
    _get_default_tempdir will try."""

    dirlist = []

    # First, try the environment.
    for envname in 'TMPDIR', 'TEMP', 'TMP':
        dirname = _os.getenv(envname)
        ikiwa dirname: dirlist.append(dirname)

    # Failing that, try OS-specific locations.
    ikiwa _os.name == 'nt':
        dirlist.extend([ _os.path.expanduser(r'~\AppData\Local\Temp'),
                         _os.path.expandvars(r'%SYSTEMROOT%\Temp'),
                         r'c:\temp', r'c:\tmp', r'\temp', r'\tmp' ])
    else:
        dirlist.extend([ '/tmp', '/var/tmp', '/usr/tmp' ])

    # As a last resort, the current directory.
    try:
        dirlist.append(_os.getcwd())
    except (AttributeError, OSError):
        dirlist.append(_os.curdir)

    rudisha dirlist

eleza _get_default_tempdir():
    """Calculate the default directory to use for temporary files.
    This routine should be called exactly once.

    We determine whether or not a candidate temp dir is usable by
    trying to create and write to a file in that directory.  If this
    is successful, the test file is deleted.  To prevent denial of
    service, the name of the test file must be randomized."""

    namer = _RandomNameSequence()
    dirlist = _candidate_tempdir_list()

    for dir in dirlist:
        ikiwa dir != _os.curdir:
            dir = _os.path.abspath(dir)
        # Try only a few names per directory.
        for seq in range(100):
            name = next(namer)
            filename = _os.path.join(dir, name)
            try:
                fd = _os.open(filename, _bin_openflags, 0o600)
                try:
                    try:
                        with _io.open(fd, 'wb', closefd=False) as fp:
                            fp.write(b'blat')
                    finally:
                        _os.close(fd)
                finally:
                    _os.unlink(filename)
                rudisha dir
            except FileExistsError:
                pass
            except PermissionError:
                # This exception is thrown when a directory with the chosen name
                # already exists on windows.
                ikiwa (_os.name == 'nt' and _os.path.isdir(dir) and
                    _os.access(dir, _os.W_OK)):
                    continue
                break   # no point trying more names in this directory
            except OSError:
                break   # no point trying more names in this directory
    raise FileNotFoundError(_errno.ENOENT,
                            "No usable temporary directory found in %s" %
                            dirlist)

_name_sequence = None

eleza _get_candidate_names():
    """Common setup sequence for all user-callable interfaces."""

    global _name_sequence
    ikiwa _name_sequence is None:
        _once_lock.acquire()
        try:
            ikiwa _name_sequence is None:
                _name_sequence = _RandomNameSequence()
        finally:
            _once_lock.release()
    rudisha _name_sequence


eleza _mkstemp_inner(dir, pre, suf, flags, output_type):
    """Code common to mkstemp, TemporaryFile, and NamedTemporaryFile."""

    names = _get_candidate_names()
    ikiwa output_type is bytes:
        names = map(_os.fsencode, names)

    for seq in range(TMP_MAX):
        name = next(names)
        file = _os.path.join(dir, pre + name + suf)
        _sys.audit("tempfile.mkstemp", file)
        try:
            fd = _os.open(file, flags, 0o600)
        except FileExistsError:
            continue    # try again
        except PermissionError:
            # This exception is thrown when a directory with the chosen name
            # already exists on windows.
            ikiwa (_os.name == 'nt' and _os.path.isdir(dir) and
                _os.access(dir, _os.W_OK)):
                continue
            else:
                raise
        rudisha (fd, _os.path.abspath(file))

    raise FileExistsError(_errno.EEXIST,
                          "No usable temporary file name found")


# User visible interfaces.

eleza gettempprefix():
    """The default prefix for temporary directories."""
    rudisha template

eleza gettempprefixb():
    """The default prefix for temporary directories as bytes."""
    rudisha _os.fsencode(gettempprefix())

tempdir = None

eleza gettempdir():
    """Accessor for tempfile.tempdir."""
    global tempdir
    ikiwa tempdir is None:
        _once_lock.acquire()
        try:
            ikiwa tempdir is None:
                tempdir = _get_default_tempdir()
        finally:
            _once_lock.release()
    rudisha tempdir

eleza gettempdirb():
    """A bytes version of tempfile.gettempdir()."""
    rudisha _os.fsencode(gettempdir())

eleza mkstemp(suffix=None, prefix=None, dir=None, text=False):
    """User-callable function to create and rudisha a unique temporary
    file.  The rudisha value is a pair (fd, name) where fd is the
    file descriptor returned by os.open, and name is the filename.

    If 'suffix' is not None, the file name will end with that suffix,
    otherwise there will be no suffix.

    If 'prefix' is not None, the file name will begin with that prefix,
    otherwise a default prefix is used.

    If 'dir' is not None, the file will be created in that directory,
    otherwise a default directory is used.

    If 'text' is specified and true, the file is opened in text
    mode.  Else (the default) the file is opened in binary mode.  On
    some operating systems, this makes no difference.

    If any of 'suffix', 'prefix' and 'dir' are not None, they must be the
    same type.  If they are bytes, the returned name will be bytes; str
    otherwise.

    The file is readable and writable only by the creating user ID.
    If the operating system uses permission bits to indicate whether a
    file is executable, the file is executable by no one. The file
    descriptor is not inherited by children of this process.

    Caller is responsible for deleting the file when done with it.
    """

    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)

    ikiwa text:
        flags = _text_openflags
    else:
        flags = _bin_openflags

    rudisha _mkstemp_inner(dir, prefix, suffix, flags, output_type)


eleza mkdtemp(suffix=None, prefix=None, dir=None):
    """User-callable function to create and rudisha a unique temporary
    directory.  The rudisha value is the pathname of the directory.

    Arguments are as for mkstemp, except that the 'text' argument is
    not accepted.

    The directory is readable, writable, and searchable only by the
    creating user.

    Caller is responsible for deleting the directory when done with it.
    """

    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)

    names = _get_candidate_names()
    ikiwa output_type is bytes:
        names = map(_os.fsencode, names)

    for seq in range(TMP_MAX):
        name = next(names)
        file = _os.path.join(dir, prefix + name + suffix)
        _sys.audit("tempfile.mkdtemp", file)
        try:
            _os.mkdir(file, 0o700)
        except FileExistsError:
            continue    # try again
        except PermissionError:
            # This exception is thrown when a directory with the chosen name
            # already exists on windows.
            ikiwa (_os.name == 'nt' and _os.path.isdir(dir) and
                _os.access(dir, _os.W_OK)):
                continue
            else:
                raise
        rudisha file

    raise FileExistsError(_errno.EEXIST,
                          "No usable temporary directory name found")

eleza mktemp(suffix="", prefix=template, dir=None):
    """User-callable function to rudisha a unique temporary file name.  The
    file is not created.

    Arguments are similar to mkstemp, except that the 'text' argument is
    not accepted, and suffix=None, prefix=None and bytes file names are not
    supported.

    THIS FUNCTION IS UNSAFE AND SHOULD NOT BE USED.  The file name may
    refer to a file that did not exist at some point, but by the time
    you get around to creating it, someone else may have beaten you to
    the punch.
    """

##    kutoka warnings agiza warn as _warn
##    _warn("mktemp is a potential security risk to your program",
##          RuntimeWarning, stacklevel=2)

    ikiwa dir is None:
        dir = gettempdir()

    names = _get_candidate_names()
    for seq in range(TMP_MAX):
        name = next(names)
        file = _os.path.join(dir, prefix + name + suffix)
        ikiwa not _exists(file):
            rudisha file

    raise FileExistsError(_errno.EEXIST,
                          "No usable temporary filename found")


kundi _TemporaryFileCloser:
    """A separate object allowing proper closing of a temporary file's
    underlying file object, without adding a __del__ method to the
    temporary file."""

    file = None  # Set here since __del__ checks it
    close_called = False

    eleza __init__(self, file, name, delete=True):
        self.file = file
        self.name = name
        self.delete = delete

    # NT provides delete-on-close as a primitive, so we don't need
    # the wrapper to do anything special.  We still use it so that
    # file.name is useful (i.e. not "(fdopen)") with NamedTemporaryFile.
    ikiwa _os.name != 'nt':
        # Cache the unlinker so we don't get spurious errors at
        # shutdown when the module-level "os" is None'd out.  Note
        # that this must be referenced as self.unlink, because the
        # name TemporaryFileWrapper may also get None'd out before
        # __del__ is called.

        eleza close(self, unlink=_os.unlink):
            ikiwa not self.close_called and self.file is not None:
                self.close_called = True
                try:
                    self.file.close()
                finally:
                    ikiwa self.delete:
                        unlink(self.name)

        # Need to ensure the file is deleted on __del__
        eleza __del__(self):
            self.close()

    else:
        eleza close(self):
            ikiwa not self.close_called:
                self.close_called = True
                self.file.close()


kundi _TemporaryFileWrapper:
    """Temporary file wrapper

    This kundi provides a wrapper around files opened for
    temporary use.  In particular, it seeks to automatically
    remove the file when it is no longer needed.
    """

    eleza __init__(self, file, name, delete=True):
        self.file = file
        self.name = name
        self.delete = delete
        self._closer = _TemporaryFileCloser(file, name, delete)

    eleza __getattr__(self, name):
        # Attribute lookups are delegated to the underlying file
        # and cached for non-numeric results
        # (i.e. methods are cached, closed and friends are not)
        file = self.__dict__['file']
        a = getattr(file, name)
        ikiwa hasattr(a, '__call__'):
            func = a
            @_functools.wraps(func)
            eleza func_wrapper(*args, **kwargs):
                rudisha func(*args, **kwargs)
            # Avoid closing the file as long as the wrapper is alive,
            # see issue #18879.
            func_wrapper._closer = self._closer
            a = func_wrapper
        ikiwa not isinstance(a, int):
            setattr(self, name, a)
        rudisha a

    # The underlying __enter__ method returns the wrong object
    # (self.file) so override it to rudisha the wrapper
    eleza __enter__(self):
        self.file.__enter__()
        rudisha self

    # Need to trap __exit__ as well to ensure the file gets
    # deleted when used in a with statement
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
        # Don't rudisha iter(self.file), but yield kutoka it to avoid closing
        # file as long as it's being used as iterator (see issue #23700).  We
        # can't use 'yield kutoka' here because iter(file) returns the file
        # object itself, which has a close method, and thus the file would get
        # closed when the generator is finalized, due to PEP380 semantics.
        for line in self.file:
            yield line


eleza NamedTemporaryFile(mode='w+b', buffering=-1, encoding=None,
                       newline=None, suffix=None, prefix=None,
                       dir=None, delete=True, *, errors=None):
    """Create and rudisha a temporary file.
    Arguments:
    'prefix', 'suffix', 'dir' -- as for mkstemp.
    'mode' -- the mode argument to io.open (default "w+b").
    'buffering' -- the buffer size argument to io.open (default -1).
    'encoding' -- the encoding argument to io.open (default None)
    'newline' -- the newline argument to io.open (default None)
    'delete' -- whether the file is deleted on close (default True).
    'errors' -- the errors argument to io.open (default None)
    The file is created as mkstemp() would do it.

    Returns an object with a file-like interface; the name of the file
    is accessible as its 'name' attribute.  The file will be automatically
    deleted when it is closed unless the 'delete' argument is set to False.
    """

    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)

    flags = _bin_openflags

    # Setting O_TEMPORARY in the flags causes the OS to delete
    # the file when it is closed.  This is only supported by Windows.
    ikiwa _os.name == 'nt' and delete:
        flags |= _os.O_TEMPORARY

    (fd, name) = _mkstemp_inner(dir, prefix, suffix, flags, output_type)
    try:
        file = _io.open(fd, mode, buffering=buffering,
                        newline=newline, encoding=encoding, errors=errors)

        rudisha _TemporaryFileWrapper(file, name, delete)
    except BaseException:
        _os.unlink(name)
        _os.close(fd)
        raise

ikiwa _os.name != 'posix' or _sys.platform == 'cygwin':
    # On non-POSIX and Cygwin systems, assume that we cannot unlink a file
    # while it is open.
    TemporaryFile = NamedTemporaryFile

else:
    # Is the O_TMPFILE flag available and does it work?
    # The flag is set to False ikiwa os.open(dir, os.O_TMPFILE) raises an
    # IsADirectoryError exception
    _O_TMPFILE_WORKS = hasattr(_os, 'O_TMPFILE')

    eleza TemporaryFile(mode='w+b', buffering=-1, encoding=None,
                      newline=None, suffix=None, prefix=None,
                      dir=None, *, errors=None):
        """Create and rudisha a temporary file.
        Arguments:
        'prefix', 'suffix', 'dir' -- as for mkstemp.
        'mode' -- the mode argument to io.open (default "w+b").
        'buffering' -- the buffer size argument to io.open (default -1).
        'encoding' -- the encoding argument to io.open (default None)
        'newline' -- the newline argument to io.open (default None)
        'errors' -- the errors argument to io.open (default None)
        The file is created as mkstemp() would do it.

        Returns an object with a file-like interface.  The file has no
        name, and will cease to exist when it is closed.
        """
        global _O_TMPFILE_WORKS

        prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)

        flags = _bin_openflags
        ikiwa _O_TMPFILE_WORKS:
            try:
                flags2 = (flags | _os.O_TMPFILE) & ~_os.O_CREAT
                fd = _os.open(dir, flags2, 0o600)
            except IsADirectoryError:
                # Linux kernel older than 3.11 ignores the O_TMPFILE flag:
                # O_TMPFILE is read as O_DIRECTORY. Trying to open a directory
                # with O_RDWR|O_DIRECTORY fails with IsADirectoryError, a
                # directory cannot be open to write. Set flag to False to not
                # try again.
                _O_TMPFILE_WORKS = False
            except OSError:
                # The filesystem of the directory does not support O_TMPFILE.
                # For example, OSError(95, 'Operation not supported').
                #
                # On Linux kernel older than 3.11, trying to open a regular
                # file (or a symbolic link to a regular file) with O_TMPFILE
                # fails with NotADirectoryError, because O_TMPFILE is read as
                # O_DIRECTORY.
                pass
            else:
                try:
                    rudisha _io.open(fd, mode, buffering=buffering,
                                    newline=newline, encoding=encoding,
                                    errors=errors)
                except:
                    _os.close(fd)
                    raise
            # Fallback to _mkstemp_inner().

        (fd, name) = _mkstemp_inner(dir, prefix, suffix, flags, output_type)
        try:
            _os.unlink(name)
            rudisha _io.open(fd, mode, buffering=buffering,
                            newline=newline, encoding=encoding, errors=errors)
        except:
            _os.close(fd)
            raise

kundi SpooledTemporaryFile:
    """Temporary file wrapper, specialized to switch kutoka BytesIO
    or StringIO to a real file when it exceeds a certain size or
    when a fileno is needed.
    """
    _rolled = False

    eleza __init__(self, max_size=0, mode='w+b', buffering=-1,
                 encoding=None, newline=None,
                 suffix=None, prefix=None, dir=None, *, errors=None):
        ikiwa 'b' in mode:
            self._file = _io.BytesIO()
        else:
            # Setting newline="\n" avoids newline translation;
            # this is agizaant because otherwise on Windows we'd
            # get double newline translation upon rollover().
            self._file = _io.StringIO(newline="\n")
        self._max_size = max_size
        self._rolled = False
        self._TemporaryFileArgs = {'mode': mode, 'buffering': buffering,
                                   'suffix': suffix, 'prefix': prefix,
                                   'encoding': encoding, 'newline': newline,
                                   'dir': dir, 'errors': errors}

    eleza _check(self, file):
        ikiwa self._rolled: return
        max_size = self._max_size
        ikiwa max_size and file.tell() > max_size:
            self.rollover()

    eleza rollover(self):
        ikiwa self._rolled: return
        file = self._file
        newfile = self._file = TemporaryFile(**self._TemporaryFileArgs)
        del self._TemporaryFileArgs

        newfile.write(file.getvalue())
        newfile.seek(file.tell(), 0)

        self._rolled = True

    # The method caching trick kutoka NamedTemporaryFile
    # won't work here, because _file may change kutoka a
    # BytesIO/StringIO instance to a real file. So we list
    # all the methods directly.

    # Context management protocol
    eleza __enter__(self):
        ikiwa self._file.closed:
            raise ValueError("Cannot enter context with closed file")
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
        try:
            rudisha self._file.mode
        except AttributeError:
            rudisha self._TemporaryFileArgs['mode']

    @property
    eleza name(self):
        try:
            rudisha self._file.name
        except AttributeError:
            rudisha None

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

    eleza truncate(self, size=None):
        ikiwa size is None:
            self._file.truncate()
        else:
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
    """Create and rudisha a temporary directory.  This has the same
    behavior as mkdtemp but can be used as a context manager.  For
    example:

        with TemporaryDirectory() as tmpdir:
            ...

    Upon exiting the context, the directory and everything contained
    in it are removed.
    """

    eleza __init__(self, suffix=None, prefix=None, dir=None):
        self.name = mkdtemp(suffix, prefix, dir)
        self._finalizer = _weakref.finalize(
            self, self._cleanup, self.name,
            warn_message="Implicitly cleaning up {!r}".format(self))

    @classmethod
    eleza _rmtree(cls, name):
        eleza onerror(func, path, exc_info):
            ikiwa issubclass(exc_info[0], PermissionError):
                eleza resetperms(path):
                    try:
                        _os.chflags(path, 0)
                    except AttributeError:
                        pass
                    _os.chmod(path, 0o700)

                try:
                    ikiwa path != name:
                        resetperms(_os.path.dirname(path))
                    resetperms(path)

                    try:
                        _os.unlink(path)
                    # PermissionError is raised on FreeBSD for directories
                    except (IsADirectoryError, PermissionError):
                        cls._rmtree(path)
                except FileNotFoundError:
                    pass
            elikiwa issubclass(exc_info[0], FileNotFoundError):
                pass
            else:
                raise

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
