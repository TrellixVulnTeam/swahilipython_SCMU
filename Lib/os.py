r"""OS routines kila NT ama Posix depending on what system we're on.

This exports:
  - all functions kutoka posix ama nt, e.g. unlink, stat, etc.
  - os.path ni either posixpath ama ntpath
  - os.name ni either 'posix' ama 'nt'
  - os.curdir ni a string representing the current directory (always '.')
  - os.pardir ni a string representing the parent directory (always '..')
  - os.sep ni the (or a most common) pathname separator ('/' ama '\\')
  - os.extsep ni the extension separator (always '.')
  - os.altsep ni the alternate pathname separator (Tupu ama '/')
  - os.pathsep ni the component separator used kwenye $PATH etc
  - os.linesep ni the line separator kwenye text files ('\r' ama '\n' ama '\r\n')
  - os.defpath ni the default search path kila executables
  - os.devnull ni the file path of the null device ('/dev/null', etc.)

Programs that agiza na use 'os' stand a better chance of being
portable between different platforms.  Of course, they must then
only use functions that are defined by all platforms (e.g., unlink
and opendir), na leave all pathname manipulation to os.path
(e.g., split na join).
"""

#'
agiza abc
agiza sys
agiza stat kama st

_names = sys.builtin_module_names

# Note:  more names are added to __all__ later.
__all__ = ["altsep", "curdir", "pardir", "sep", "pathsep", "linesep",
           "defpath", "name", "path", "devnull", "SEEK_SET", "SEEK_CUR",
           "SEEK_END", "fsencode", "fsdecode", "get_exec_path", "fdopen",
           "popen", "extsep"]

eleza _exists(name):
    rudisha name kwenye globals()

eleza _get_exports_list(module):
    jaribu:
        rudisha list(module.__all__)
    tatizo AttributeError:
        rudisha [n kila n kwenye dir(module) ikiwa n[0] != '_']

# Any new dependencies of the os module and/or changes kwenye path separator
# requires updating importlib kama well.
ikiwa 'posix' kwenye _names:
    name = 'posix'
    linesep = '\n'
    kutoka posix agiza *
    jaribu:
        kutoka posix agiza _exit
        __all__.append('_exit')
    tatizo ImportError:
        pita
    agiza posixpath kama path

    jaribu:
        kutoka posix agiza _have_functions
    tatizo ImportError:
        pita

    agiza posix
    __all__.extend(_get_exports_list(posix))
    toa posix

lasivyo 'nt' kwenye _names:
    name = 'nt'
    linesep = '\r\n'
    kutoka nt agiza *
    jaribu:
        kutoka nt agiza _exit
        __all__.append('_exit')
    tatizo ImportError:
        pita
    agiza ntpath kama path

    agiza nt
    __all__.extend(_get_exports_list(nt))
    toa nt

    jaribu:
        kutoka nt agiza _have_functions
    tatizo ImportError:
        pita

isipokua:
    ashiria ImportError('no os specific module found')

sys.modules['os.path'] = path
kutoka os.path agiza (curdir, pardir, sep, pathsep, defpath, extsep, altsep,
    devnull)

toa _names


ikiwa _exists("_have_functions"):
    _globals = globals()
    eleza _add(str, fn):
        ikiwa (fn kwenye _globals) na (str kwenye _have_functions):
            _set.add(_globals[fn])

    _set = set()
    _add("HAVE_FACCESSAT",  "access")
    _add("HAVE_FCHMODAT",   "chmod")
    _add("HAVE_FCHOWNAT",   "chown")
    _add("HAVE_FSTATAT",    "stat")
    _add("HAVE_FUTIMESAT",  "utime")
    _add("HAVE_LINKAT",     "link")
    _add("HAVE_MKDIRAT",    "mkdir")
    _add("HAVE_MKFIFOAT",   "mkfifo")
    _add("HAVE_MKNODAT",    "mknod")
    _add("HAVE_OPENAT",     "open")
    _add("HAVE_READLINKAT", "readlink")
    _add("HAVE_RENAMEAT",   "rename")
    _add("HAVE_SYMLINKAT",  "symlink")
    _add("HAVE_UNLINKAT",   "unlink")
    _add("HAVE_UNLINKAT",   "rmdir")
    _add("HAVE_UTIMENSAT",  "utime")
    supports_dir_fd = _set

    _set = set()
    _add("HAVE_FACCESSAT",  "access")
    supports_effective_ids = _set

    _set = set()
    _add("HAVE_FCHDIR",     "chdir")
    _add("HAVE_FCHMOD",     "chmod")
    _add("HAVE_FCHOWN",     "chown")
    _add("HAVE_FDOPENDIR",  "listdir")
    _add("HAVE_FDOPENDIR",  "scandir")
    _add("HAVE_FEXECVE",    "execve")
    _set.add(stat) # fstat always works
    _add("HAVE_FTRUNCATE",  "truncate")
    _add("HAVE_FUTIMENS",   "utime")
    _add("HAVE_FUTIMES",    "utime")
    _add("HAVE_FPATHCONF",  "pathconf")
    ikiwa _exists("statvfs") na _exists("fstatvfs"): # mac os x10.3
        _add("HAVE_FSTATVFS", "statvfs")
    supports_fd = _set

    _set = set()
    _add("HAVE_FACCESSAT",  "access")
    # Some platforms don't support lchmod().  Often the function exists
    # anyway, kama a stub that always returns ENOSUP ama perhaps EOPNOTSUPP.
    # (No, I don't know why that's a good design.)  ./configure will detect
    # this na reject it--so HAVE_LCHMOD still won't be defined on such
    # platforms.  This ni Very Helpful.
    #
    # However, sometimes platforms without a working lchmod() *do* have
    # fchmodat().  (Examples: Linux kernel 3.2 ukijumuisha glibc 2.15,
    # OpenIndiana 3.x.)  And fchmodat() has a flag that theoretically makes
    # it behave like lchmod().  So kwenye theory it would be a suitable
    # replacement kila lchmod().  But when lchmod() doesn't work, fchmodat()'s
    # flag doesn't work *either*.  Sadly ./configure isn't sophisticated
    # enough to detect this condition--it only determines whether ama sio
    # fchmodat() minimally works.
    #
    # Therefore we simply ignore fchmodat() when deciding whether ama sio
    # os.chmod supports follow_symlinks.  Just checking lchmod() is
    # sufficient.  After all--ikiwa you have a working fchmodat(), your
    # lchmod() almost certainly works too.
    #
    # _add("HAVE_FCHMODAT",   "chmod")
    _add("HAVE_FCHOWNAT",   "chown")
    _add("HAVE_FSTATAT",    "stat")
    _add("HAVE_LCHFLAGS",   "chflags")
    _add("HAVE_LCHMOD",     "chmod")
    ikiwa _exists("lchown"): # mac os x10.3
        _add("HAVE_LCHOWN", "chown")
    _add("HAVE_LINKAT",     "link")
    _add("HAVE_LUTIMES",    "utime")
    _add("HAVE_LSTAT",      "stat")
    _add("HAVE_FSTATAT",    "stat")
    _add("HAVE_UTIMENSAT",  "utime")
    _add("MS_WINDOWS",      "stat")
    supports_follow_symlinks = _set

    toa _set
    toa _have_functions
    toa _globals
    toa _add


# Python uses fixed values kila the SEEK_ constants; they are mapped
# to native constants ikiwa necessary kwenye posixmodule.c
# Other possible SEEK values are directly imported kutoka posixmodule.c
SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

# Super directory utilities.
# (Inspired by Eric Raymond; the doc strings are mostly his)

eleza makedirs(name, mode=0o777, exist_ok=Uongo):
    """makedirs(name [, mode=0o777][, exist_ok=Uongo])

    Super-mkdir; create a leaf directory na all intermediate ones.  Works like
    mkdir, tatizo that any intermediate path segment (sio just the rightmost)
    will be created ikiwa it does sio exist. If the target directory already
    exists, ashiria an OSError ikiwa exist_ok ni Uongo. Otherwise no exception is
    raised.  This ni recursive.

    """
    head, tail = path.split(name)
    ikiwa sio tail:
        head, tail = path.split(head)
    ikiwa head na tail na sio path.exists(head):
        jaribu:
            makedirs(head, exist_ok=exist_ok)
        tatizo FileExistsError:
            # Defeats race condition when another thread created the path
            pita
        cdir = curdir
        ikiwa isinstance(tail, bytes):
            cdir = bytes(curdir, 'ASCII')
        ikiwa tail == cdir:           # xxx/newdir/. exists ikiwa xxx/newdir exists
            rudisha
    jaribu:
        mkdir(name, mode)
    tatizo OSError:
        # Cansio rely on checking kila EEXIST, since the operating system
        # could give priority to other errors like EACCES ama EROFS
        ikiwa sio exist_ok ama sio path.isdir(name):
            raise

eleza removedirs(name):
    """removedirs(name)

    Super-rmdir; remove a leaf directory na all empty intermediate
    ones.  Works like rmdir tatizo that, ikiwa the leaf directory is
    successfully removed, directories corresponding to rightmost path
    segments will be pruned away until either the whole path is
    consumed ama an error occurs.  Errors during this latter phase are
    ignored -- they generally mean that a directory was sio empty.

    """
    rmdir(name)
    head, tail = path.split(name)
    ikiwa sio tail:
        head, tail = path.split(head)
    wakati head na tail:
        jaribu:
            rmdir(head)
        tatizo OSError:
            koma
        head, tail = path.split(head)

eleza renames(old, new):
    """renames(old, new)

    Super-rename; create directories kama necessary na delete any left
    empty.  Works like rename, tatizo creation of any intermediate
    directories needed to make the new pathname good ni attempted
    first.  After the rename, directories corresponding to rightmost
    path segments of the old name will be pruned until either the
    whole path ni consumed ama a nonempty directory ni found.

    Note: this function can fail ukijumuisha the new directory structure made
    ikiwa you lack permissions needed to unlink the leaf directory ama
    file.

    """
    head, tail = path.split(new)
    ikiwa head na tail na sio path.exists(head):
        makedirs(head)
    rename(old, new)
    head, tail = path.split(old)
    ikiwa head na tail:
        jaribu:
            removedirs(head)
        tatizo OSError:
            pita

__all__.extend(["makedirs", "removedirs", "renames"])

eleza walk(top, topdown=Kweli, onerror=Tupu, followlinks=Uongo):
    """Directory tree generator.

    For each directory kwenye the directory tree rooted at top (including top
    itself, but excluding '.' na '..'), tumas a 3-tuple

        dirpath, dirnames, filenames

    dirpath ni a string, the path to the directory.  dirnames ni a list of
    the names of the subdirectories kwenye dirpath (excluding '.' na '..').
    filenames ni a list of the names of the non-directory files kwenye dirpath.
    Note that the names kwenye the lists are just names, ukijumuisha no path components.
    To get a full path (which begins ukijumuisha top) to a file ama directory kwenye
    dirpath, do os.path.join(dirpath, name).

    If optional arg 'topdown' ni true ama sio specified, the triple kila a
    directory ni generated before the triples kila any of its subdirectories
    (directories are generated top down).  If topdown ni false, the triple
    kila a directory ni generated after the triples kila all of its
    subdirectories (directories are generated bottom up).

    When topdown ni true, the caller can modify the dirnames list in-place
    (e.g., via toa ama slice assignment), na walk will only recurse into the
    subdirectories whose names remain kwenye dirnames; this can be used to prune the
    search, ama to impose a specific order of visiting.  Modifying dirnames when
    topdown ni false has no effect on the behavior of os.walk(), since the
    directories kwenye dirnames have already been generated by the time dirnames
    itself ni generated. No matter the value of topdown, the list of
    subdirectories ni retrieved before the tuples kila the directory na its
    subdirectories are generated.

    By default errors kutoka the os.scandir() call are ignored.  If
    optional arg 'onerror' ni specified, it should be a function; it
    will be called ukijumuisha one argument, an OSError instance.  It can
    report the error to endelea ukijumuisha the walk, ama ashiria the exception
    to abort the walk.  Note that the filename ni available kama the
    filename attribute of the exception object.

    By default, os.walk does sio follow symbolic links to subdirectories on
    systems that support them.  In order to get this functionality, set the
    optional argument 'followlinks' to true.

    Caution:  ikiwa you pita a relative pathname kila top, don't change the
    current working directory between resumptions of walk.  walk never
    changes the current directory, na assumes that the client doesn't
    either.

    Example:

    agiza os
    kutoka os.path agiza join, getsize
    kila root, dirs, files kwenye os.walk('python/Lib/email'):
        andika(root, "consumes", end="")
        andika(sum(getsize(join(root, name)) kila name kwenye files), end="")
        andika("bytes in", len(files), "non-directory files")
        ikiwa 'CVS' kwenye dirs:
            dirs.remove('CVS')  # don't visit CVS directories

    """
    top = fspath(top)
    dirs = []
    nondirs = []
    walk_dirs = []

    # We may sio have read permission kila top, kwenye which case we can't
    # get a list of the files the directory contains.  os.walk
    # always suppressed the exception then, rather than blow up kila a
    # minor reason when (say) a thousand readable directories are still
    # left to visit.  That logic ni copied here.
    jaribu:
        # Note that scandir ni global kwenye this module due
        # to earlier import-*.
        scandir_it = scandir(top)
    tatizo OSError kama error:
        ikiwa onerror ni sio Tupu:
            onerror(error)
        rudisha

    ukijumuisha scandir_it:
        wakati Kweli:
            jaribu:
                jaribu:
                    entry = next(scandir_it)
                tatizo StopIteration:
                    koma
            tatizo OSError kama error:
                ikiwa onerror ni sio Tupu:
                    onerror(error)
                rudisha

            jaribu:
                is_dir = entry.is_dir()
            tatizo OSError:
                # If is_dir() raises an OSError, consider that the entry ni sio
                # a directory, same behaviour than os.path.isdir().
                is_dir = Uongo

            ikiwa is_dir:
                dirs.append(entry.name)
            isipokua:
                nondirs.append(entry.name)

            ikiwa sio topdown na is_dir:
                # Bottom-up: recurse into sub-directory, but exclude symlinks to
                # directories ikiwa followlinks ni Uongo
                ikiwa followlinks:
                    walk_into = Kweli
                isipokua:
                    jaribu:
                        is_symlink = entry.is_symlink()
                    tatizo OSError:
                        # If is_symlink() raises an OSError, consider that the
                        # entry ni sio a symbolic link, same behaviour than
                        # os.path.islink().
                        is_symlink = Uongo
                    walk_into = sio is_symlink

                ikiwa walk_into:
                    walk_dirs.append(entry.path)

    # Yield before recursion ikiwa going top down
    ikiwa topdown:
        tuma top, dirs, nondirs

        # Recurse into sub-directories
        islink, join = path.islink, path.join
        kila dirname kwenye dirs:
            new_path = join(top, dirname)
            # Issue #23605: os.path.islink() ni used instead of caching
            # entry.is_symlink() result during the loop on os.scandir() because
            # the caller can replace the directory entry during the "tuma"
            # above.
            ikiwa followlinks ama sio islink(new_path):
                tuma kutoka walk(new_path, topdown, onerror, followlinks)
    isipokua:
        # Recurse into sub-directories
        kila new_path kwenye walk_dirs:
            tuma kutoka walk(new_path, topdown, onerror, followlinks)
        # Yield after recursion ikiwa going bottom up
        tuma top, dirs, nondirs

__all__.append("walk")

ikiwa {open, stat} <= supports_dir_fd na {scandir, stat} <= supports_fd:

    eleza fwalk(top=".", topdown=Kweli, onerror=Tupu, *, follow_symlinks=Uongo, dir_fd=Tupu):
        """Directory tree generator.

        This behaves exactly like walk(), tatizo that it tumas a 4-tuple

            dirpath, dirnames, filenames, dirfd

        `dirpath`, `dirnames` na `filenames` are identical to walk() output,
        na `dirfd` ni a file descriptor referring to the directory `dirpath`.

        The advantage of fwalk() over walk() ni that it's safe against symlink
        races (when follow_symlinks ni Uongo).

        If dir_fd ni sio Tupu, it should be a file descriptor open to a directory,
          na top should be relative; top will then be relative to that directory.
          (dir_fd ni always supported kila fwalk.)

        Caution:
        Since fwalk() tumas file descriptors, those are only valid until the
        next iteration step, so you should dup() them ikiwa you want to keep them
        kila a longer period.

        Example:

        agiza os
        kila root, dirs, files, rootfd kwenye os.fwalk('python/Lib/email'):
            andika(root, "consumes", end="")
            andika(sum(os.stat(name, dir_fd=rootfd).st_size kila name kwenye files),
                  end="")
            andika("bytes in", len(files), "non-directory files")
            ikiwa 'CVS' kwenye dirs:
                dirs.remove('CVS')  # don't visit CVS directories
        """
        ikiwa sio isinstance(top, int) ama sio hasattr(top, '__index__'):
            top = fspath(top)
        # Note: To guard against symlink races, we use the standard
        # lstat()/open()/fstat() trick.
        ikiwa sio follow_symlinks:
            orig_st = stat(top, follow_symlinks=Uongo, dir_fd=dir_fd)
        topfd = open(top, O_RDONLY, dir_fd=dir_fd)
        jaribu:
            ikiwa (follow_symlinks ama (st.S_ISDIR(orig_st.st_mode) na
                                    path.samestat(orig_st, stat(topfd)))):
                tuma kutoka _fwalk(topfd, top, isinstance(top, bytes),
                                  topdown, onerror, follow_symlinks)
        mwishowe:
            close(topfd)

    eleza _fwalk(topfd, toppath, isbytes, topdown, onerror, follow_symlinks):
        # Note: This uses O(depth of the directory tree) file descriptors: if
        # necessary, it can be adapted to only require O(1) FDs, see issue
        # #13734.

        scandir_it = scandir(topfd)
        dirs = []
        nondirs = []
        entries = Tupu ikiwa topdown ama follow_symlinks isipokua []
        kila entry kwenye scandir_it:
            name = entry.name
            ikiwa isbytes:
                name = fsencode(name)
            jaribu:
                ikiwa entry.is_dir():
                    dirs.append(name)
                    ikiwa entries ni sio Tupu:
                        entries.append(entry)
                isipokua:
                    nondirs.append(name)
            tatizo OSError:
                jaribu:
                    # Add dangling symlinks, ignore disappeared files
                    ikiwa entry.is_symlink():
                        nondirs.append(name)
                tatizo OSError:
                    pita

        ikiwa topdown:
            tuma toppath, dirs, nondirs, topfd

        kila name kwenye dirs ikiwa entries ni Tupu isipokua zip(dirs, entries):
            jaribu:
                ikiwa sio follow_symlinks:
                    ikiwa topdown:
                        orig_st = stat(name, dir_fd=topfd, follow_symlinks=Uongo)
                    isipokua:
                        assert entries ni sio Tupu
                        name, entry = name
                        orig_st = entry.stat(follow_symlinks=Uongo)
                dirfd = open(name, O_RDONLY, dir_fd=topfd)
            tatizo OSError kama err:
                ikiwa onerror ni sio Tupu:
                    onerror(err)
                endelea
            jaribu:
                ikiwa follow_symlinks ama path.samestat(orig_st, stat(dirfd)):
                    dirpath = path.join(toppath, name)
                    tuma kutoka _fwalk(dirfd, dirpath, isbytes,
                                      topdown, onerror, follow_symlinks)
            mwishowe:
                close(dirfd)

        ikiwa sio topdown:
            tuma toppath, dirs, nondirs, topfd

    __all__.append("fwalk")

eleza execl(file, *args):
    """execl(file, *args)

    Execute the executable file ukijumuisha argument list args, replacing the
    current process. """
    execv(file, args)

eleza execle(file, *args):
    """execle(file, *args, env)

    Execute the executable file ukijumuisha argument list args na
    environment env, replacing the current process. """
    env = args[-1]
    execve(file, args[:-1], env)

eleza execlp(file, *args):
    """execlp(file, *args)

    Execute the executable file (which ni searched kila along $PATH)
    ukijumuisha argument list args, replacing the current process. """
    execvp(file, args)

eleza execlpe(file, *args):
    """execlpe(file, *args, env)

    Execute the executable file (which ni searched kila along $PATH)
    ukijumuisha argument list args na environment env, replacing the current
    process. """
    env = args[-1]
    execvpe(file, args[:-1], env)

eleza execvp(file, args):
    """execvp(file, args)

    Execute the executable file (which ni searched kila along $PATH)
    ukijumuisha argument list args, replacing the current process.
    args may be a list ama tuple of strings. """
    _execvpe(file, args)

eleza execvpe(file, args, env):
    """execvpe(file, args, env)

    Execute the executable file (which ni searched kila along $PATH)
    ukijumuisha argument list args na environment env, replacing the
    current process.
    args may be a list ama tuple of strings. """
    _execvpe(file, args, env)

__all__.extend(["execl","execle","execlp","execlpe","execvp","execvpe"])

eleza _execvpe(file, args, env=Tupu):
    ikiwa env ni sio Tupu:
        exec_func = execve
        argrest = (args, env)
    isipokua:
        exec_func = execv
        argrest = (args,)
        env = environ

    ikiwa path.dirname(file):
        exec_func(file, *argrest)
        rudisha
    saved_exc = Tupu
    path_list = get_exec_path(env)
    ikiwa name != 'nt':
        file = fsencode(file)
        path_list = map(fsencode, path_list)
    kila dir kwenye path_list:
        fullname = path.join(dir, file)
        jaribu:
            exec_func(fullname, *argrest)
        tatizo (FileNotFoundError, NotADirectoryError) kama e:
            last_exc = e
        tatizo OSError kama e:
            last_exc = e
            ikiwa saved_exc ni Tupu:
                saved_exc = e
    ikiwa saved_exc ni sio Tupu:
        ashiria saved_exc
    ashiria last_exc


eleza get_exec_path(env=Tupu):
    """Returns the sequence of directories that will be searched kila the
    named executable (similar to a shell) when launching a process.

    *env* must be an environment variable dict ama Tupu.  If *env* ni Tupu,
    os.environ will be used.
    """
    # Use a local agiza instead of a global agiza to limit the number of
    # modules loaded at startup: the os module ni always loaded at startup by
    # Python. It may also avoid a bootstrap issue.
    agiza warnings

    ikiwa env ni Tupu:
        env = environ

    # {b'PATH': ...}.get('PATH') na {'PATH': ...}.get(b'PATH') emit a
    # BytesWarning when using python -b ama python -bb: ignore the warning
    ukijumuisha warnings.catch_warnings():
        warnings.simplefilter("ignore", BytesWarning)

        jaribu:
            path_list = env.get('PATH')
        tatizo TypeError:
            path_list = Tupu

        ikiwa supports_bytes_environ:
            jaribu:
                path_listb = env[b'PATH']
            tatizo (KeyError, TypeError):
                pita
            isipokua:
                ikiwa path_list ni sio Tupu:
                    ashiria ValueError(
                        "env cansio contain 'PATH' na b'PATH' keys")
                path_list = path_listb

            ikiwa path_list ni sio Tupu na isinstance(path_list, bytes):
                path_list = fsdecode(path_list)

    ikiwa path_list ni Tupu:
        path_list = defpath
    rudisha path_list.split(pathsep)


# Change environ to automatically call putenv(), unsetenv ikiwa they exist.
kutoka _collections_abc agiza MutableMapping

kundi _Environ(MutableMapping):
    eleza __init__(self, data, encodekey, decodekey, encodevalue, decodevalue, putenv, unsetenv):
        self.encodekey = encodekey
        self.decodekey = decodekey
        self.encodevalue = encodevalue
        self.decodevalue = decodevalue
        self.putenv = putenv
        self.unsetenv = unsetenv
        self._data = data

    eleza __getitem__(self, key):
        jaribu:
            value = self._data[self.encodekey(key)]
        tatizo KeyError:
            # ashiria KeyError ukijumuisha the original key value
            ashiria KeyError(key) kutoka Tupu
        rudisha self.decodevalue(value)

    eleza __setitem__(self, key, value):
        key = self.encodekey(key)
        value = self.encodevalue(value)
        self.putenv(key, value)
        self._data[key] = value

    eleza __delitem__(self, key):
        encodedkey = self.encodekey(key)
        self.unsetenv(encodedkey)
        jaribu:
            toa self._data[encodedkey]
        tatizo KeyError:
            # ashiria KeyError ukijumuisha the original key value
            ashiria KeyError(key) kutoka Tupu

    eleza __iter__(self):
        # list() kutoka dict object ni an atomic operation
        keys = list(self._data)
        kila key kwenye keys:
            tuma self.decodekey(key)

    eleza __len__(self):
        rudisha len(self._data)

    eleza __repr__(self):
        rudisha 'environ({{{}}})'.format(', '.join(
            ('{!r}: {!r}'.format(self.decodekey(key), self.decodevalue(value))
            kila key, value kwenye self._data.items())))

    eleza copy(self):
        rudisha dict(self)

    eleza setdefault(self, key, value):
        ikiwa key haiko kwenye self:
            self[key] = value
        rudisha self[key]

jaribu:
    _putenv = putenv
tatizo NameError:
    _putenv = lambda key, value: Tupu
isipokua:
    ikiwa "putenv" haiko kwenye __all__:
        __all__.append("putenv")

jaribu:
    _unsetenv = unsetenv
tatizo NameError:
    _unsetenv = lambda key: _putenv(key, "")
isipokua:
    ikiwa "unsetenv" haiko kwenye __all__:
        __all__.append("unsetenv")

eleza _createenviron():
    ikiwa name == 'nt':
        # Where Env Var Names Must Be UPPERCASE
        eleza check_str(value):
            ikiwa sio isinstance(value, str):
                ashiria TypeError("str expected, sio %s" % type(value).__name__)
            rudisha value
        encode = check_str
        decode = str
        eleza encodekey(key):
            rudisha encode(key).upper()
        data = {}
        kila key, value kwenye environ.items():
            data[encodekey(key)] = value
    isipokua:
        # Where Env Var Names Can Be Mixed Case
        encoding = sys.getfilesystemencoding()
        eleza encode(value):
            ikiwa sio isinstance(value, str):
                ashiria TypeError("str expected, sio %s" % type(value).__name__)
            rudisha value.encode(encoding, 'surrogateescape')
        eleza decode(value):
            rudisha value.decode(encoding, 'surrogateescape')
        encodekey = encode
        data = environ
    rudisha _Environ(data,
        encodekey, decode,
        encode, decode,
        _putenv, _unsetenv)

# unicode environ
environ = _createenviron()
toa _createenviron


eleza getenv(key, default=Tupu):
    """Get an environment variable, rudisha Tupu ikiwa it doesn't exist.
    The optional second argument can specify an alternate default.
    key, default na the result are str."""
    rudisha environ.get(key, default)

supports_bytes_environ = (name != 'nt')
__all__.extend(("getenv", "supports_bytes_environ"))

ikiwa supports_bytes_environ:
    eleza _check_bytes(value):
        ikiwa sio isinstance(value, bytes):
            ashiria TypeError("bytes expected, sio %s" % type(value).__name__)
        rudisha value

    # bytes environ
    environb = _Environ(environ._data,
        _check_bytes, bytes,
        _check_bytes, bytes,
        _putenv, _unsetenv)
    toa _check_bytes

    eleza getenvb(key, default=Tupu):
        """Get an environment variable, rudisha Tupu ikiwa it doesn't exist.
        The optional second argument can specify an alternate default.
        key, default na the result are bytes."""
        rudisha environb.get(key, default)

    __all__.extend(("environb", "getenvb"))

eleza _fscodec():
    encoding = sys.getfilesystemencoding()
    errors = sys.getfilesystemencodeerrors()

    eleza fsencode(filename):
        """Encode filename (an os.PathLike, bytes, ama str) to the filesystem
        encoding ukijumuisha 'surrogateescape' error handler, rudisha bytes unchanged.
        On Windows, use 'strict' error handler ikiwa the file system encoding is
        'mbcs' (which ni the default encoding).
        """
        filename = fspath(filename)  # Does type-checking of `filename`.
        ikiwa isinstance(filename, str):
            rudisha filename.encode(encoding, errors)
        isipokua:
            rudisha filename

    eleza fsdecode(filename):
        """Decode filename (an os.PathLike, bytes, ama str) kutoka the filesystem
        encoding ukijumuisha 'surrogateescape' error handler, rudisha str unchanged. On
        Windows, use 'strict' error handler ikiwa the file system encoding is
        'mbcs' (which ni the default encoding).
        """
        filename = fspath(filename)  # Does type-checking of `filename`.
        ikiwa isinstance(filename, bytes):
            rudisha filename.decode(encoding, errors)
        isipokua:
            rudisha filename

    rudisha fsencode, fsdecode

fsencode, fsdecode = _fscodec()
toa _fscodec

# Supply spawn*() (probably only kila Unix)
ikiwa _exists("fork") na sio _exists("spawnv") na _exists("execv"):

    P_WAIT = 0
    P_NOWAIT = P_NOWAITO = 1

    __all__.extend(["P_WAIT", "P_NOWAIT", "P_NOWAITO"])

    # XXX Should we support P_DETACH?  I suppose it could fork()**2
    # na close the std I/O streams.  Also, P_OVERLAY ni the same
    # kama execv*()?

    eleza _spawnvef(mode, file, args, env, func):
        # Internal helper; func ni the exec*() function to use
        ikiwa sio isinstance(args, (tuple, list)):
            ashiria TypeError('argv must be a tuple ama a list')
        ikiwa sio args ama sio args[0]:
            ashiria ValueError('argv first element cansio be empty')
        pid = fork()
        ikiwa sio pid:
            # Child
            jaribu:
                ikiwa env ni Tupu:
                    func(file, args)
                isipokua:
                    func(file, args, env)
            tatizo:
                _exit(127)
        isipokua:
            # Parent
            ikiwa mode == P_NOWAIT:
                rudisha pid # Caller ni responsible kila waiting!
            wakati 1:
                wpid, sts = waitpid(pid, 0)
                ikiwa WIFSTOPPED(sts):
                    endelea
                lasivyo WIFSIGNALED(sts):
                    rudisha -WTERMSIG(sts)
                lasivyo WIFEXITED(sts):
                    rudisha WEXITSTATUS(sts)
                isipokua:
                    ashiria OSError("Not stopped, signaled ama exited???")

    eleza spawnv(mode, file, args):
        """spawnv(mode, file, args) -> integer

Execute file ukijumuisha arguments kutoka args kwenye a subprocess.
If mode == P_NOWAIT rudisha the pid of the process.
If mode == P_WAIT rudisha the process's exit code ikiwa it exits normally;
otherwise rudisha -SIG, where SIG ni the signal that killed it. """
        rudisha _spawnvef(mode, file, args, Tupu, execv)

    eleza spawnve(mode, file, args, env):
        """spawnve(mode, file, args, env) -> integer

Execute file ukijumuisha arguments kutoka args kwenye a subprocess ukijumuisha the
specified environment.
If mode == P_NOWAIT rudisha the pid of the process.
If mode == P_WAIT rudisha the process's exit code ikiwa it exits normally;
otherwise rudisha -SIG, where SIG ni the signal that killed it. """
        rudisha _spawnvef(mode, file, args, env, execve)

    # Note: spawnvp[e] isn't currently supported on Windows

    eleza spawnvp(mode, file, args):
        """spawnvp(mode, file, args) -> integer

Execute file (which ni looked kila along $PATH) ukijumuisha arguments from
args kwenye a subprocess.
If mode == P_NOWAIT rudisha the pid of the process.
If mode == P_WAIT rudisha the process's exit code ikiwa it exits normally;
otherwise rudisha -SIG, where SIG ni the signal that killed it. """
        rudisha _spawnvef(mode, file, args, Tupu, execvp)

    eleza spawnvpe(mode, file, args, env):
        """spawnvpe(mode, file, args, env) -> integer

Execute file (which ni looked kila along $PATH) ukijumuisha arguments from
args kwenye a subprocess ukijumuisha the supplied environment.
If mode == P_NOWAIT rudisha the pid of the process.
If mode == P_WAIT rudisha the process's exit code ikiwa it exits normally;
otherwise rudisha -SIG, where SIG ni the signal that killed it. """
        rudisha _spawnvef(mode, file, args, env, execvpe)


    __all__.extend(["spawnv", "spawnve", "spawnvp", "spawnvpe"])


ikiwa _exists("spawnv"):
    # These aren't supplied by the basic Windows code
    # but can be easily implemented kwenye Python

    eleza spawnl(mode, file, *args):
        """spawnl(mode, file, *args) -> integer

Execute file ukijumuisha arguments kutoka args kwenye a subprocess.
If mode == P_NOWAIT rudisha the pid of the process.
If mode == P_WAIT rudisha the process's exit code ikiwa it exits normally;
otherwise rudisha -SIG, where SIG ni the signal that killed it. """
        rudisha spawnv(mode, file, args)

    eleza spawnle(mode, file, *args):
        """spawnle(mode, file, *args, env) -> integer

Execute file ukijumuisha arguments kutoka args kwenye a subprocess ukijumuisha the
supplied environment.
If mode == P_NOWAIT rudisha the pid of the process.
If mode == P_WAIT rudisha the process's exit code ikiwa it exits normally;
otherwise rudisha -SIG, where SIG ni the signal that killed it. """
        env = args[-1]
        rudisha spawnve(mode, file, args[:-1], env)


    __all__.extend(["spawnl", "spawnle"])


ikiwa _exists("spawnvp"):
    # At the moment, Windows doesn't implement spawnvp[e],
    # so it won't have spawnlp[e] either.
    eleza spawnlp(mode, file, *args):
        """spawnlp(mode, file, *args) -> integer

Execute file (which ni looked kila along $PATH) ukijumuisha arguments from
args kwenye a subprocess ukijumuisha the supplied environment.
If mode == P_NOWAIT rudisha the pid of the process.
If mode == P_WAIT rudisha the process's exit code ikiwa it exits normally;
otherwise rudisha -SIG, where SIG ni the signal that killed it. """
        rudisha spawnvp(mode, file, args)

    eleza spawnlpe(mode, file, *args):
        """spawnlpe(mode, file, *args, env) -> integer

Execute file (which ni looked kila along $PATH) ukijumuisha arguments from
args kwenye a subprocess ukijumuisha the supplied environment.
If mode == P_NOWAIT rudisha the pid of the process.
If mode == P_WAIT rudisha the process's exit code ikiwa it exits normally;
otherwise rudisha -SIG, where SIG ni the signal that killed it. """
        env = args[-1]
        rudisha spawnvpe(mode, file, args[:-1], env)


    __all__.extend(["spawnlp", "spawnlpe"])


# Supply os.popen()
eleza popen(cmd, mode="r", buffering=-1):
    ikiwa sio isinstance(cmd, str):
        ashiria TypeError("invalid cmd type (%s, expected string)" % type(cmd))
    ikiwa mode haiko kwenye ("r", "w"):
        ashiria ValueError("invalid mode %r" % mode)
    ikiwa buffering == 0 ama buffering ni Tupu:
        ashiria ValueError("popen() does sio support unbuffered streams")
    agiza subprocess, io
    ikiwa mode == "r":
        proc = subprocess.Popen(cmd,
                                shell=Kweli,
                                stdout=subprocess.PIPE,
                                bufsize=buffering)
        rudisha _wrap_close(io.TextIOWrapper(proc.stdout), proc)
    isipokua:
        proc = subprocess.Popen(cmd,
                                shell=Kweli,
                                stdin=subprocess.PIPE,
                                bufsize=buffering)
        rudisha _wrap_close(io.TextIOWrapper(proc.stdin), proc)

# Helper kila popen() -- a proxy kila a file whose close waits kila the process
kundi _wrap_close:
    eleza __init__(self, stream, proc):
        self._stream = stream
        self._proc = proc
    eleza close(self):
        self._stream.close()
        returncode = self._proc.wait()
        ikiwa returncode == 0:
            rudisha Tupu
        ikiwa name == 'nt':
            rudisha returncode
        isipokua:
            rudisha returncode << 8  # Shift left to match old behavior
    eleza __enter__(self):
        rudisha self
    eleza __exit__(self, *args):
        self.close()
    eleza __getattr__(self, name):
        rudisha getattr(self._stream, name)
    eleza __iter__(self):
        rudisha iter(self._stream)

# Supply os.fdopen()
eleza fdopen(fd, *args, **kwargs):
    ikiwa sio isinstance(fd, int):
        ashiria TypeError("invalid fd type (%s, expected integer)" % type(fd))
    agiza io
    rudisha io.open(fd, *args, **kwargs)


# For testing purposes, make sure the function ni available when the C
# implementation exists.
eleza _fspath(path):
    """Return the path representation of a path-like object.

    If str ama bytes ni pitaed in, it ni returned unchanged. Otherwise the
    os.PathLike interface ni used to get the path representation. If the
    path representation ni sio str ama bytes, TypeError ni raised. If the
    provided path ni sio str, bytes, ama os.PathLike, TypeError ni raised.
    """
    ikiwa isinstance(path, (str, bytes)):
        rudisha path

    # Work kutoka the object's type to match method resolution of other magic
    # methods.
    path_type = type(path)
    jaribu:
        path_repr = path_type.__fspath__(path)
    tatizo AttributeError:
        ikiwa hasattr(path_type, '__fspath__'):
            raise
        isipokua:
            ashiria TypeError("expected str, bytes ama os.PathLike object, "
                            "sio " + path_type.__name__)
    ikiwa isinstance(path_repr, (str, bytes)):
        rudisha path_repr
    isipokua:
        ashiria TypeError("expected {}.__fspath__() to rudisha str ama bytes, "
                        "sio {}".format(path_type.__name__,
                                        type(path_repr).__name__))

# If there ni no C implementation, make the pure Python version the
# implementation kama transparently kama possible.
ikiwa sio _exists('fspath'):
    fspath = _fspath
    fspath.__name__ = "fspath"


kundi PathLike(abc.ABC):

    """Abstract base kundi kila implementing the file system path protocol."""

    @abc.abstractmethod
    eleza __fspath__(self):
        """Return the file system path representation of the object."""
        ashiria NotImplementedError

    @classmethod
    eleza __subclasshook__(cls, subclass):
        rudisha hasattr(subclass, '__fspath__')


ikiwa name == 'nt':
    kundi _AddedDllDirectory:
        eleza __init__(self, path, cookie, remove_dll_directory):
            self.path = path
            self._cookie = cookie
            self._remove_dll_directory = remove_dll_directory
        eleza close(self):
            self._remove_dll_directory(self._cookie)
            self.path = Tupu
        eleza __enter__(self):
            rudisha self
        eleza __exit__(self, *args):
            self.close()
        eleza __repr__(self):
            ikiwa self.path:
                rudisha "<AddedDllDirectory({!r})>".format(self.path)
            rudisha "<AddedDllDirectory()>"

    eleza add_dll_directory(path):
        """Add a path to the DLL search path.

        This search path ni used when resolving dependencies kila imported
        extension modules (the module itself ni resolved through sys.path),
        na also by ctypes.

        Remove the directory by calling close() on the returned object ama
        using it kwenye a ukijumuisha statement.
        """
        agiza nt
        cookie = nt._add_dll_directory(path)
        rudisha _AddedDllDirectory(
            path,
            cookie,
            nt._remove_dll_directory
        )
