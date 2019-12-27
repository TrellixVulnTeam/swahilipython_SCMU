"""Utility functions for copying and archiving files and directory trees.

XXX The functions here don't copy the resource fork or other metadata on Mac.

"""

agiza os
agiza sys
agiza stat
agiza fnmatch
agiza collections
agiza errno

try:
    agiza zlib
    del zlib
    _ZLIB_SUPPORTED = True
except ImportError:
    _ZLIB_SUPPORTED = False

try:
    agiza bz2
    del bz2
    _BZ2_SUPPORTED = True
except ImportError:
    _BZ2_SUPPORTED = False

try:
    agiza lzma
    del lzma
    _LZMA_SUPPORTED = True
except ImportError:
    _LZMA_SUPPORTED = False

try:
    kutoka pwd agiza getpwnam
except ImportError:
    getpwnam = None

try:
    kutoka grp agiza getgrnam
except ImportError:
    getgrnam = None

_WINDOWS = os.name == 'nt'
posix = nt = None
ikiwa os.name == 'posix':
    agiza posix
elikiwa _WINDOWS:
    agiza nt

COPY_BUFSIZE = 1024 * 1024 ikiwa _WINDOWS else 64 * 1024
_USE_CP_SENDFILE = hasattr(os, "sendfile") and sys.platform.startswith("linux")
_HAS_FCOPYFILE = posix and hasattr(posix, "_fcopyfile")  # macOS

__all__ = ["copyfileobj", "copyfile", "copymode", "copystat", "copy", "copy2",
           "copytree", "move", "rmtree", "Error", "SpecialFileError",
           "ExecError", "make_archive", "get_archive_formats",
           "register_archive_format", "unregister_archive_format",
           "get_unpack_formats", "register_unpack_format",
           "unregister_unpack_format", "unpack_archive",
           "ignore_patterns", "chown", "which", "get_terminal_size",
           "SameFileError"]
           # disk_usage is added later, ikiwa available on the platform

kundi Error(OSError):
    pass

kundi SameFileError(Error):
    """Raised when source and destination are the same file."""

kundi SpecialFileError(OSError):
    """Raised when trying to do a kind of operation (e.g. copying) which is
    not supported on a special file (e.g. a named pipe)"""

kundi ExecError(OSError):
    """Raised when a command could not be executed"""

kundi ReadError(OSError):
    """Raised when an archive cannot be read"""

kundi RegistryError(Exception):
    """Raised when a registry operation with the archiving
    and unpacking registries fails"""

kundi _GiveupOnFastCopy(Exception):
    """Raised as a signal to fallback on using raw read()/write()
    file copy when fast-copy functions fail to do so.
    """

eleza _fastcopy_fcopyfile(fsrc, fdst, flags):
    """Copy a regular file content or metadata by using high-performance
    fcopyfile(3) syscall (macOS).
    """
    try:
        infd = fsrc.fileno()
        outfd = fdst.fileno()
    except Exception as err:
        raise _GiveupOnFastCopy(err)  # not a regular file

    try:
        posix._fcopyfile(infd, outfd, flags)
    except OSError as err:
        err.filename = fsrc.name
        err.filename2 = fdst.name
        ikiwa err.errno in {errno.EINVAL, errno.ENOTSUP}:
            raise _GiveupOnFastCopy(err)
        else:
            raise err kutoka None

eleza _fastcopy_sendfile(fsrc, fdst):
    """Copy data kutoka one regular mmap-like fd to another by using
    high-performance sendfile(2) syscall.
    This should work on Linux >= 2.6.33 only.
    """
    # Note: copyfileobj() is left alone in order to not introduce any
    # unexpected breakage. Possible risks by using zero-copy calls
    # in copyfileobj() are:
    # - fdst cannot be open in "a"(ppend) mode
    # - fsrc and fdst may be open in "t"(ext) mode
    # - fsrc may be a BufferedReader (which hides unread data in a buffer),
    #   GzipFile (which decompresses data), HTTPResponse (which decodes
    #   chunks).
    # - possibly others (e.g. encrypted fs/partition?)
    global _USE_CP_SENDFILE
    try:
        infd = fsrc.fileno()
        outfd = fdst.fileno()
    except Exception as err:
        raise _GiveupOnFastCopy(err)  # not a regular file

    # Hopefully the whole file will be copied in a single call.
    # sendfile() is called in a loop 'till EOF is reached (0 return)
    # so a bufsize smaller or bigger than the actual file size
    # should not make any difference, also in case the file content
    # changes while being copied.
    try:
        blocksize = max(os.fstat(infd).st_size, 2 ** 23)  # min 8MiB
    except OSError:
        blocksize = 2 ** 27  # 128MiB
    # On 32-bit architectures truncate to 1GiB to avoid OverflowError,
    # see bpo-38319.
    ikiwa sys.maxsize < 2 ** 32:
        blocksize = min(blocksize, 2 ** 30)

    offset = 0
    while True:
        try:
            sent = os.sendfile(outfd, infd, offset, blocksize)
        except OSError as err:
            # ...in oder to have a more informative exception.
            err.filename = fsrc.name
            err.filename2 = fdst.name

            ikiwa err.errno == errno.ENOTSOCK:
                # sendfile() on this platform (probably Linux < 2.6.33)
                # does not support copies between regular files (only
                # sockets).
                _USE_CP_SENDFILE = False
                raise _GiveupOnFastCopy(err)

            ikiwa err.errno == errno.ENOSPC:  # filesystem is full
                raise err kutoka None

            # Give up on first call and ikiwa no data was copied.
            ikiwa offset == 0 and os.lseek(outfd, 0, os.SEEK_CUR) == 0:
                raise _GiveupOnFastCopy(err)

            raise err
        else:
            ikiwa sent == 0:
                break  # EOF
            offset += sent

eleza _copyfileobj_readinto(fsrc, fdst, length=COPY_BUFSIZE):
    """readinto()/memoryview() based variant of copyfileobj().
    *fsrc* must support readinto() method and both files must be
    open in binary mode.
    """
    # Localize variable access to minimize overhead.
    fsrc_readinto = fsrc.readinto
    fdst_write = fdst.write
    with memoryview(bytearray(length)) as mv:
        while True:
            n = fsrc_readinto(mv)
            ikiwa not n:
                break
            elikiwa n < length:
                with mv[:n] as smv:
                    fdst.write(smv)
            else:
                fdst_write(mv)

eleza copyfileobj(fsrc, fdst, length=0):
    """copy data kutoka file-like object fsrc to file-like object fdst"""
    # Localize variable access to minimize overhead.
    ikiwa not length:
        length = COPY_BUFSIZE
    fsrc_read = fsrc.read
    fdst_write = fdst.write
    while True:
        buf = fsrc_read(length)
        ikiwa not buf:
            break
        fdst_write(buf)

eleza _samefile(src, dst):
    # Macintosh, Unix.
    ikiwa isinstance(src, os.DirEntry) and hasattr(os.path, 'samestat'):
        try:
            rudisha os.path.samestat(src.stat(), os.stat(dst))
        except OSError:
            rudisha False

    ikiwa hasattr(os.path, 'samefile'):
        try:
            rudisha os.path.samefile(src, dst)
        except OSError:
            rudisha False

    # All other platforms: check for same pathname.
    rudisha (os.path.normcase(os.path.abspath(src)) ==
            os.path.normcase(os.path.abspath(dst)))

eleza _stat(fn):
    rudisha fn.stat() ikiwa isinstance(fn, os.DirEntry) else os.stat(fn)

eleza _islink(fn):
    rudisha fn.is_symlink() ikiwa isinstance(fn, os.DirEntry) else os.path.islink(fn)

eleza copyfile(src, dst, *, follow_symlinks=True):
    """Copy data kutoka src to dst in the most efficient way possible.

    If follow_symlinks is not set and src is a symbolic link, a new
    symlink will be created instead of copying the file it points to.

    """
    ikiwa _samefile(src, dst):
        raise SameFileError("{!r} and {!r} are the same file".format(src, dst))

    file_size = 0
    for i, fn in enumerate([src, dst]):
        try:
            st = _stat(fn)
        except OSError:
            # File most likely does not exist
            pass
        else:
            # XXX What about other special files? (sockets, devices...)
            ikiwa stat.S_ISFIFO(st.st_mode):
                fn = fn.path ikiwa isinstance(fn, os.DirEntry) else fn
                raise SpecialFileError("`%s` is a named pipe" % fn)
            ikiwa _WINDOWS and i == 0:
                file_size = st.st_size

    ikiwa not follow_symlinks and _islink(src):
        os.symlink(os.readlink(src), dst)
    else:
        with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
            # macOS
            ikiwa _HAS_FCOPYFILE:
                try:
                    _fastcopy_fcopyfile(fsrc, fdst, posix._COPYFILE_DATA)
                    rudisha dst
                except _GiveupOnFastCopy:
                    pass
            # Linux
            elikiwa _USE_CP_SENDFILE:
                try:
                    _fastcopy_sendfile(fsrc, fdst)
                    rudisha dst
                except _GiveupOnFastCopy:
                    pass
            # Windows, see:
            # https://github.com/python/cpython/pull/7160#discussion_r195405230
            elikiwa _WINDOWS and file_size > 0:
                _copyfileobj_readinto(fsrc, fdst, min(file_size, COPY_BUFSIZE))
                rudisha dst

            copyfileobj(fsrc, fdst)

    rudisha dst

eleza copymode(src, dst, *, follow_symlinks=True):
    """Copy mode bits kutoka src to dst.

    If follow_symlinks is not set, symlinks aren't followed ikiwa and only
    ikiwa both `src` and `dst` are symlinks.  If `lchmod` isn't available
    (e.g. Linux) this method does nothing.

    """
    ikiwa not follow_symlinks and _islink(src) and os.path.islink(dst):
        ikiwa hasattr(os, 'lchmod'):
            stat_func, chmod_func = os.lstat, os.lchmod
        else:
            return
    else:
        stat_func, chmod_func = _stat, os.chmod

    st = stat_func(src)
    chmod_func(dst, stat.S_IMODE(st.st_mode))

ikiwa hasattr(os, 'listxattr'):
    eleza _copyxattr(src, dst, *, follow_symlinks=True):
        """Copy extended filesystem attributes kutoka `src` to `dst`.

        Overwrite existing attributes.

        If `follow_symlinks` is false, symlinks won't be followed.

        """

        try:
            names = os.listxattr(src, follow_symlinks=follow_symlinks)
        except OSError as e:
            ikiwa e.errno not in (errno.ENOTSUP, errno.ENODATA, errno.EINVAL):
                raise
            return
        for name in names:
            try:
                value = os.getxattr(src, name, follow_symlinks=follow_symlinks)
                os.setxattr(dst, name, value, follow_symlinks=follow_symlinks)
            except OSError as e:
                ikiwa e.errno not in (errno.EPERM, errno.ENOTSUP, errno.ENODATA,
                                   errno.EINVAL):
                    raise
else:
    eleza _copyxattr(*args, **kwargs):
        pass

eleza copystat(src, dst, *, follow_symlinks=True):
    """Copy file metadata

    Copy the permission bits, last access time, last modification time, and
    flags kutoka `src` to `dst`. On Linux, copystat() also copies the "extended
    attributes" where possible. The file contents, owner, and group are
    unaffected. `src` and `dst` are path-like objects or path names given as
    strings.

    If the optional flag `follow_symlinks` is not set, symlinks aren't
    followed ikiwa and only ikiwa both `src` and `dst` are symlinks.
    """
    eleza _nop(*args, ns=None, follow_symlinks=None):
        pass

    # follow symlinks (aka don't not follow symlinks)
    follow = follow_symlinks or not (_islink(src) and os.path.islink(dst))
    ikiwa follow:
        # use the real function ikiwa it exists
        eleza lookup(name):
            rudisha getattr(os, name, _nop)
    else:
        # use the real function only ikiwa it exists
        # *and* it supports follow_symlinks
        eleza lookup(name):
            fn = getattr(os, name, _nop)
            ikiwa fn in os.supports_follow_symlinks:
                rudisha fn
            rudisha _nop

    ikiwa isinstance(src, os.DirEntry):
        st = src.stat(follow_symlinks=follow)
    else:
        st = lookup("stat")(src, follow_symlinks=follow)
    mode = stat.S_IMODE(st.st_mode)
    lookup("utime")(dst, ns=(st.st_atime_ns, st.st_mtime_ns),
        follow_symlinks=follow)
    # We must copy extended attributes before the file is (potentially)
    # chmod()'ed read-only, otherwise setxattr() will error with -EACCES.
    _copyxattr(src, dst, follow_symlinks=follow)
    try:
        lookup("chmod")(dst, mode, follow_symlinks=follow)
    except NotImplementedError:
        # ikiwa we got a NotImplementedError, it's because
        #   * follow_symlinks=False,
        #   * lchown() is unavailable, and
        #   * either
        #       * fchownat() is unavailable or
        #       * fchownat() doesn't implement AT_SYMLINK_NOFOLLOW.
        #         (it returned ENOSUP.)
        # therefore we're out of options--we simply cannot chown the
        # symlink.  give up, suppress the error.
        # (which is what shutil always did in this circumstance.)
        pass
    ikiwa hasattr(st, 'st_flags'):
        try:
            lookup("chflags")(dst, st.st_flags, follow_symlinks=follow)
        except OSError as why:
            for err in 'EOPNOTSUPP', 'ENOTSUP':
                ikiwa hasattr(errno, err) and why.errno == getattr(errno, err):
                    break
            else:
                raise

eleza copy(src, dst, *, follow_symlinks=True):
    """Copy data and mode bits ("cp src dst"). Return the file's destination.

    The destination may be a directory.

    If follow_symlinks is false, symlinks won't be followed. This
    resembles GNU's "cp -P src dst".

    If source and destination are the same file, a SameFileError will be
    raised.

    """
    ikiwa os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    copyfile(src, dst, follow_symlinks=follow_symlinks)
    copymode(src, dst, follow_symlinks=follow_symlinks)
    rudisha dst

eleza copy2(src, dst, *, follow_symlinks=True):
    """Copy data and metadata. Return the file's destination.

    Metadata is copied with copystat(). Please see the copystat function
    for more information.

    The destination may be a directory.

    If follow_symlinks is false, symlinks won't be followed. This
    resembles GNU's "cp -P src dst".
    """
    ikiwa os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    copyfile(src, dst, follow_symlinks=follow_symlinks)
    copystat(src, dst, follow_symlinks=follow_symlinks)
    rudisha dst

eleza ignore_patterns(*patterns):
    """Function that can be used as copytree() ignore parameter.

    Patterns is a sequence of glob-style patterns
    that are used to exclude files"""
    eleza _ignore_patterns(path, names):
        ignored_names = []
        for pattern in patterns:
            ignored_names.extend(fnmatch.filter(names, pattern))
        rudisha set(ignored_names)
    rudisha _ignore_patterns

eleza _copytree(entries, src, dst, symlinks, ignore, copy_function,
              ignore_dangling_symlinks, dirs_exist_ok=False):
    ikiwa ignore is not None:
        ignored_names = ignore(src, set(os.listdir(src)))
    else:
        ignored_names = set()

    os.makedirs(dst, exist_ok=dirs_exist_ok)
    errors = []
    use_srcentry = copy_function is copy2 or copy_function is copy

    for srcentry in entries:
        ikiwa srcentry.name in ignored_names:
            continue
        srcname = os.path.join(src, srcentry.name)
        dstname = os.path.join(dst, srcentry.name)
        srcobj = srcentry ikiwa use_srcentry else srcname
        try:
            is_symlink = srcentry.is_symlink()
            ikiwa is_symlink and os.name == 'nt':
                # Special check for directory junctions, which appear as
                # symlinks but we want to recurse.
                lstat = srcentry.stat(follow_symlinks=False)
                ikiwa lstat.st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT:
                    is_symlink = False
            ikiwa is_symlink:
                linkto = os.readlink(srcname)
                ikiwa symlinks:
                    # We can't just leave it to `copy_function` because legacy
                    # code with a custom `copy_function` may rely on copytree
                    # doing the right thing.
                    os.symlink(linkto, dstname)
                    copystat(srcobj, dstname, follow_symlinks=not symlinks)
                else:
                    # ignore dangling symlink ikiwa the flag is on
                    ikiwa not os.path.exists(linkto) and ignore_dangling_symlinks:
                        continue
                    # otherwise let the copy occur. copy2 will raise an error
                    ikiwa srcentry.is_dir():
                        copytree(srcobj, dstname, symlinks, ignore,
                                 copy_function, dirs_exist_ok=dirs_exist_ok)
                    else:
                        copy_function(srcobj, dstname)
            elikiwa srcentry.is_dir():
                copytree(srcobj, dstname, symlinks, ignore, copy_function,
                         dirs_exist_ok=dirs_exist_ok)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy_function(srcobj, dstname)
        # catch the Error kutoka the recursive copytree so that we can
        # continue with other files
        except Error as err:
            errors.extend(err.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        # Copying file access times may fail on Windows
        ikiwa getattr(why, 'winerror', None) is None:
            errors.append((src, dst, str(why)))
    ikiwa errors:
        raise Error(errors)
    rudisha dst

eleza copytree(src, dst, symlinks=False, ignore=None, copy_function=copy2,
             ignore_dangling_symlinks=False, dirs_exist_ok=False):
    """Recursively copy a directory tree and rudisha the destination directory.

    dirs_exist_ok dictates whether to raise an exception in case dst or any
    missing parent directory already exists.

    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied. If the file pointed by the symlink doesn't
    exist, an exception will be added in the list of errors raised in
    an Error exception at the end of the copy process.

    You can set the optional ignore_dangling_symlinks flag to true ikiwa you
    want to silence this exception. Notice that this has no effect on
    platforms that don't support os.symlink.

    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() is called recursively, the callable will be
    called once for each directory that is copied. It returns a
    list of names relative to the `src` directory that should
    not be copied.

    The optional copy_function argument is a callable that will be used
    to copy each file. It will be called with the source path and the
    destination path as arguments. By default, copy2() is used, but any
    function that supports the same signature (like copy()) can be used.

    """
    sys.audit("shutil.copytree", src, dst)
    with os.scandir(src) as entries:
        rudisha _copytree(entries=entries, src=src, dst=dst, symlinks=symlinks,
                         ignore=ignore, copy_function=copy_function,
                         ignore_dangling_symlinks=ignore_dangling_symlinks,
                         dirs_exist_ok=dirs_exist_ok)

ikiwa hasattr(os.stat_result, 'st_file_attributes'):
    # Special handling for directory junctions to make them behave like
    # symlinks for shutil.rmtree, since in general they do not appear as
    # regular links.
    eleza _rmtree_isdir(entry):
        try:
            st = entry.stat(follow_symlinks=False)
            rudisha (stat.S_ISDIR(st.st_mode) and not
                (st.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
                 and st.st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT))
        except OSError:
            rudisha False

    eleza _rmtree_islink(path):
        try:
            st = os.lstat(path)
            rudisha (stat.S_ISLNK(st.st_mode) or
                (st.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
                 and st.st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT))
        except OSError:
            rudisha False
else:
    eleza _rmtree_isdir(entry):
        try:
            rudisha entry.is_dir(follow_symlinks=False)
        except OSError:
            rudisha False

    eleza _rmtree_islink(path):
        rudisha os.path.islink(path)

# version vulnerable to race conditions
eleza _rmtree_unsafe(path, onerror):
    try:
        with os.scandir(path) as scandir_it:
            entries = list(scandir_it)
    except OSError:
        onerror(os.scandir, path, sys.exc_info())
        entries = []
    for entry in entries:
        fullname = entry.path
        ikiwa _rmtree_isdir(entry):
            try:
                ikiwa entry.is_symlink():
                    # This can only happen ikiwa someone replaces
                    # a directory with a symlink after the call to
                    # os.scandir or entry.is_dir above.
                    raise OSError("Cannot call rmtree on a symbolic link")
            except OSError:
                onerror(os.path.islink, fullname, sys.exc_info())
                continue
            _rmtree_unsafe(fullname, onerror)
        else:
            try:
                os.unlink(fullname)
            except OSError:
                onerror(os.unlink, fullname, sys.exc_info())
    try:
        os.rmdir(path)
    except OSError:
        onerror(os.rmdir, path, sys.exc_info())

# Version using fd-based APIs to protect against races
eleza _rmtree_safe_fd(topfd, path, onerror):
    try:
        with os.scandir(topfd) as scandir_it:
            entries = list(scandir_it)
    except OSError as err:
        err.filename = path
        onerror(os.scandir, path, sys.exc_info())
        return
    for entry in entries:
        fullname = os.path.join(path, entry.name)
        try:
            is_dir = entry.is_dir(follow_symlinks=False)
        except OSError:
            is_dir = False
        else:
            ikiwa is_dir:
                try:
                    orig_st = entry.stat(follow_symlinks=False)
                    is_dir = stat.S_ISDIR(orig_st.st_mode)
                except OSError:
                    onerror(os.lstat, fullname, sys.exc_info())
                    continue
        ikiwa is_dir:
            try:
                dirfd = os.open(entry.name, os.O_RDONLY, dir_fd=topfd)
            except OSError:
                onerror(os.open, fullname, sys.exc_info())
            else:
                try:
                    ikiwa os.path.samestat(orig_st, os.fstat(dirfd)):
                        _rmtree_safe_fd(dirfd, fullname, onerror)
                        try:
                            os.rmdir(entry.name, dir_fd=topfd)
                        except OSError:
                            onerror(os.rmdir, fullname, sys.exc_info())
                    else:
                        try:
                            # This can only happen ikiwa someone replaces
                            # a directory with a symlink after the call to
                            # os.scandir or stat.S_ISDIR above.
                            raise OSError("Cannot call rmtree on a symbolic "
                                          "link")
                        except OSError:
                            onerror(os.path.islink, fullname, sys.exc_info())
                finally:
                    os.close(dirfd)
        else:
            try:
                os.unlink(entry.name, dir_fd=topfd)
            except OSError:
                onerror(os.unlink, fullname, sys.exc_info())

_use_fd_functions = ({os.open, os.stat, os.unlink, os.rmdir} <=
                     os.supports_dir_fd and
                     os.scandir in os.supports_fd and
                     os.stat in os.supports_follow_symlinks)

eleza rmtree(path, ignore_errors=False, onerror=None):
    """Recursively delete a directory tree.

    If ignore_errors is set, errors are ignored; otherwise, ikiwa onerror
    is set, it is called to handle the error with arguments (func,
    path, exc_info) where func is platform and implementation dependent;
    path is the argument to that function that caused it to fail; and
    exc_info is a tuple returned by sys.exc_info().  If ignore_errors
    is false and onerror is None, an exception is raised.

    """
    sys.audit("shutil.rmtree", path)
    ikiwa ignore_errors:
        eleza onerror(*args):
            pass
    elikiwa onerror is None:
        eleza onerror(*args):
            raise
    ikiwa _use_fd_functions:
        # While the unsafe rmtree works fine on bytes, the fd based does not.
        ikiwa isinstance(path, bytes):
            path = os.fsdecode(path)
        # Note: To guard against symlink races, we use the standard
        # lstat()/open()/fstat() trick.
        try:
            orig_st = os.lstat(path)
        except Exception:
            onerror(os.lstat, path, sys.exc_info())
            return
        try:
            fd = os.open(path, os.O_RDONLY)
        except Exception:
            onerror(os.lstat, path, sys.exc_info())
            return
        try:
            ikiwa os.path.samestat(orig_st, os.fstat(fd)):
                _rmtree_safe_fd(fd, path, onerror)
                try:
                    os.rmdir(path)
                except OSError:
                    onerror(os.rmdir, path, sys.exc_info())
            else:
                try:
                    # symlinks to directories are forbidden, see bug #1669
                    raise OSError("Cannot call rmtree on a symbolic link")
                except OSError:
                    onerror(os.path.islink, path, sys.exc_info())
        finally:
            os.close(fd)
    else:
        try:
            ikiwa _rmtree_islink(path):
                # symlinks to directories are forbidden, see bug #1669
                raise OSError("Cannot call rmtree on a symbolic link")
        except OSError:
            onerror(os.path.islink, path, sys.exc_info())
            # can't continue even ikiwa onerror hook returns
            return
        rudisha _rmtree_unsafe(path, onerror)

# Allow introspection of whether or not the hardening against symlink
# attacks is supported on the current platform
rmtree.avoids_symlink_attacks = _use_fd_functions

eleza _basename(path):
    # A basename() variant which first strips the trailing slash, ikiwa present.
    # Thus we always get the last component of the path, even for directories.
    sep = os.path.sep + (os.path.altsep or '')
    rudisha os.path.basename(path.rstrip(sep))

eleza move(src, dst, copy_function=copy2):
    """Recursively move a file or directory to another location. This is
    similar to the Unix "mv" command. Return the file or directory's
    destination.

    If the destination is a directory or a symlink to a directory, the source
    is moved inside the directory. The destination path must not already
    exist.

    If the destination already exists but is not a directory, it may be
    overwritten depending on os.rename() semantics.

    If the destination is on our current filesystem, then rename() is used.
    Otherwise, src is copied to the destination and then removed. Symlinks are
    recreated under the new name ikiwa os.rename() fails because of cross
    filesystem renames.

    The optional `copy_function` argument is a callable that will be used
    to copy the source or it will be delegated to `copytree`.
    By default, copy2() is used, but any function that supports the same
    signature (like copy()) can be used.

    A lot more could be done here...  A look at a mv.c shows a lot of
    the issues this implementation glosses over.

    """
    real_dst = dst
    ikiwa os.path.isdir(dst):
        ikiwa _samefile(src, dst):
            # We might be on a case insensitive filesystem,
            # perform the rename anyway.
            os.rename(src, dst)
            return

        real_dst = os.path.join(dst, _basename(src))
        ikiwa os.path.exists(real_dst):
            raise Error("Destination path '%s' already exists" % real_dst)
    try:
        os.rename(src, real_dst)
    except OSError:
        ikiwa os.path.islink(src):
            linkto = os.readlink(src)
            os.symlink(linkto, real_dst)
            os.unlink(src)
        elikiwa os.path.isdir(src):
            ikiwa _destinsrc(src, dst):
                raise Error("Cannot move a directory '%s' into itself"
                            " '%s'." % (src, dst))
            copytree(src, real_dst, copy_function=copy_function,
                     symlinks=True)
            rmtree(src)
        else:
            copy_function(src, real_dst)
            os.unlink(src)
    rudisha real_dst

eleza _destinsrc(src, dst):
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)
    ikiwa not src.endswith(os.path.sep):
        src += os.path.sep
    ikiwa not dst.endswith(os.path.sep):
        dst += os.path.sep
    rudisha dst.startswith(src)

eleza _get_gid(name):
    """Returns a gid, given a group name."""
    ikiwa getgrnam is None or name is None:
        rudisha None
    try:
        result = getgrnam(name)
    except KeyError:
        result = None
    ikiwa result is not None:
        rudisha result[2]
    rudisha None

eleza _get_uid(name):
    """Returns an uid, given a user name."""
    ikiwa getpwnam is None or name is None:
        rudisha None
    try:
        result = getpwnam(name)
    except KeyError:
        result = None
    ikiwa result is not None:
        rudisha result[2]
    rudisha None

eleza _make_tarball(base_name, base_dir, compress="gzip", verbose=0, dry_run=0,
                  owner=None, group=None, logger=None):
    """Create a (possibly compressed) tar file kutoka all the files under
    'base_dir'.

    'compress' must be "gzip" (the default), "bzip2", "xz", or None.

    'owner' and 'group' can be used to define an owner and a group for the
    archive that is being built. If not provided, the current owner and group
    will be used.

    The output tar file will be named 'base_name' +  ".tar", possibly plus
    the appropriate compression extension (".gz", ".bz2", or ".xz").

    Returns the output filename.
    """
    ikiwa compress is None:
        tar_compression = ''
    elikiwa _ZLIB_SUPPORTED and compress == 'gzip':
        tar_compression = 'gz'
    elikiwa _BZ2_SUPPORTED and compress == 'bzip2':
        tar_compression = 'bz2'
    elikiwa _LZMA_SUPPORTED and compress == 'xz':
        tar_compression = 'xz'
    else:
        raise ValueError("bad value for 'compress', or compression format not "
                         "supported : {0}".format(compress))

    agiza tarfile  # late agiza for breaking circular dependency

    compress_ext = '.' + tar_compression ikiwa compress else ''
    archive_name = base_name + '.tar' + compress_ext
    archive_dir = os.path.dirname(archive_name)

    ikiwa archive_dir and not os.path.exists(archive_dir):
        ikiwa logger is not None:
            logger.info("creating %s", archive_dir)
        ikiwa not dry_run:
            os.makedirs(archive_dir)

    # creating the tarball
    ikiwa logger is not None:
        logger.info('Creating tar archive')

    uid = _get_uid(owner)
    gid = _get_gid(group)

    eleza _set_uid_gid(tarinfo):
        ikiwa gid is not None:
            tarinfo.gid = gid
            tarinfo.gname = group
        ikiwa uid is not None:
            tarinfo.uid = uid
            tarinfo.uname = owner
        rudisha tarinfo

    ikiwa not dry_run:
        tar = tarfile.open(archive_name, 'w|%s' % tar_compression)
        try:
            tar.add(base_dir, filter=_set_uid_gid)
        finally:
            tar.close()

    rudisha archive_name

eleza _make_zipfile(base_name, base_dir, verbose=0, dry_run=0, logger=None):
    """Create a zip file kutoka all the files under 'base_dir'.

    The output zip file will be named 'base_name' + ".zip".  Returns the
    name of the output zip file.
    """
    agiza zipfile  # late agiza for breaking circular dependency

    zip_filename = base_name + ".zip"
    archive_dir = os.path.dirname(base_name)

    ikiwa archive_dir and not os.path.exists(archive_dir):
        ikiwa logger is not None:
            logger.info("creating %s", archive_dir)
        ikiwa not dry_run:
            os.makedirs(archive_dir)

    ikiwa logger is not None:
        logger.info("creating '%s' and adding '%s' to it",
                    zip_filename, base_dir)

    ikiwa not dry_run:
        with zipfile.ZipFile(zip_filename, "w",
                             compression=zipfile.ZIP_DEFLATED) as zf:
            path = os.path.normpath(base_dir)
            ikiwa path != os.curdir:
                zf.write(path, path)
                ikiwa logger is not None:
                    logger.info("adding '%s'", path)
            for dirpath, dirnames, filenames in os.walk(base_dir):
                for name in sorted(dirnames):
                    path = os.path.normpath(os.path.join(dirpath, name))
                    zf.write(path, path)
                    ikiwa logger is not None:
                        logger.info("adding '%s'", path)
                for name in filenames:
                    path = os.path.normpath(os.path.join(dirpath, name))
                    ikiwa os.path.isfile(path):
                        zf.write(path, path)
                        ikiwa logger is not None:
                            logger.info("adding '%s'", path)

    rudisha zip_filename

_ARCHIVE_FORMATS = {
    'tar':   (_make_tarball, [('compress', None)], "uncompressed tar file"),
}

ikiwa _ZLIB_SUPPORTED:
    _ARCHIVE_FORMATS['gztar'] = (_make_tarball, [('compress', 'gzip')],
                                "gzip'ed tar-file")
    _ARCHIVE_FORMATS['zip'] = (_make_zipfile, [], "ZIP file")

ikiwa _BZ2_SUPPORTED:
    _ARCHIVE_FORMATS['bztar'] = (_make_tarball, [('compress', 'bzip2')],
                                "bzip2'ed tar-file")

ikiwa _LZMA_SUPPORTED:
    _ARCHIVE_FORMATS['xztar'] = (_make_tarball, [('compress', 'xz')],
                                "xz'ed tar-file")

eleza get_archive_formats():
    """Returns a list of supported formats for archiving and unarchiving.

    Each element of the returned sequence is a tuple (name, description)
    """
    formats = [(name, registry[2]) for name, registry in
               _ARCHIVE_FORMATS.items()]
    formats.sort()
    rudisha formats

eleza register_archive_format(name, function, extra_args=None, description=''):
    """Registers an archive format.

    name is the name of the format. function is the callable that will be
    used to create archives. If provided, extra_args is a sequence of
    (name, value) tuples that will be passed as arguments to the callable.
    description can be provided to describe the format, and will be returned
    by the get_archive_formats() function.
    """
    ikiwa extra_args is None:
        extra_args = []
    ikiwa not callable(function):
        raise TypeError('The %s object is not callable' % function)
    ikiwa not isinstance(extra_args, (tuple, list)):
        raise TypeError('extra_args needs to be a sequence')
    for element in extra_args:
        ikiwa not isinstance(element, (tuple, list)) or len(element) !=2:
            raise TypeError('extra_args elements are : (arg_name, value)')

    _ARCHIVE_FORMATS[name] = (function, extra_args, description)

eleza unregister_archive_format(name):
    del _ARCHIVE_FORMATS[name]

eleza make_archive(base_name, format, root_dir=None, base_dir=None, verbose=0,
                 dry_run=0, owner=None, group=None, logger=None):
    """Create an archive file (eg. zip or tar).

    'base_name' is the name of the file to create, minus any format-specific
    extension; 'format' is the archive format: one of "zip", "tar", "gztar",
    "bztar", or "xztar".  Or any other registered format.

    'root_dir' is a directory that will be the root directory of the
    archive; ie. we typically chdir into 'root_dir' before creating the
    archive.  'base_dir' is the directory where we start archiving kutoka;
    ie. 'base_dir' will be the common prefix of all files and
    directories in the archive.  'root_dir' and 'base_dir' both default
    to the current directory.  Returns the name of the archive file.

    'owner' and 'group' are used when creating a tar archive. By default,
    uses the current owner and group.
    """
    sys.audit("shutil.make_archive", base_name, format, root_dir, base_dir)
    save_cwd = os.getcwd()
    ikiwa root_dir is not None:
        ikiwa logger is not None:
            logger.debug("changing into '%s'", root_dir)
        base_name = os.path.abspath(base_name)
        ikiwa not dry_run:
            os.chdir(root_dir)

    ikiwa base_dir is None:
        base_dir = os.curdir

    kwargs = {'dry_run': dry_run, 'logger': logger}

    try:
        format_info = _ARCHIVE_FORMATS[format]
    except KeyError:
        raise ValueError("unknown archive format '%s'" % format) kutoka None

    func = format_info[0]
    for arg, val in format_info[1]:
        kwargs[arg] = val

    ikiwa format != 'zip':
        kwargs['owner'] = owner
        kwargs['group'] = group

    try:
        filename = func(base_name, base_dir, **kwargs)
    finally:
        ikiwa root_dir is not None:
            ikiwa logger is not None:
                logger.debug("changing back to '%s'", save_cwd)
            os.chdir(save_cwd)

    rudisha filename


eleza get_unpack_formats():
    """Returns a list of supported formats for unpacking.

    Each element of the returned sequence is a tuple
    (name, extensions, description)
    """
    formats = [(name, info[0], info[3]) for name, info in
               _UNPACK_FORMATS.items()]
    formats.sort()
    rudisha formats

eleza _check_unpack_options(extensions, function, extra_args):
    """Checks what gets registered as an unpacker."""
    # first make sure no other unpacker is registered for this extension
    existing_extensions = {}
    for name, info in _UNPACK_FORMATS.items():
        for ext in info[0]:
            existing_extensions[ext] = name

    for extension in extensions:
        ikiwa extension in existing_extensions:
            msg = '%s is already registered for "%s"'
            raise RegistryError(msg % (extension,
                                       existing_extensions[extension]))

    ikiwa not callable(function):
        raise TypeError('The registered function must be a callable')


eleza register_unpack_format(name, extensions, function, extra_args=None,
                           description=''):
    """Registers an unpack format.

    `name` is the name of the format. `extensions` is a list of extensions
    corresponding to the format.

    `function` is the callable that will be
    used to unpack archives. The callable will receive archives to unpack.
    If it's unable to handle an archive, it needs to raise a ReadError
    exception.

    If provided, `extra_args` is a sequence of
    (name, value) tuples that will be passed as arguments to the callable.
    description can be provided to describe the format, and will be returned
    by the get_unpack_formats() function.
    """
    ikiwa extra_args is None:
        extra_args = []
    _check_unpack_options(extensions, function, extra_args)
    _UNPACK_FORMATS[name] = extensions, function, extra_args, description

eleza unregister_unpack_format(name):
    """Removes the pack format kutoka the registry."""
    del _UNPACK_FORMATS[name]

eleza _ensure_directory(path):
    """Ensure that the parent directory of `path` exists"""
    dirname = os.path.dirname(path)
    ikiwa not os.path.isdir(dirname):
        os.makedirs(dirname)

eleza _unpack_zipfile(filename, extract_dir):
    """Unpack zip `filename` to `extract_dir`
    """
    agiza zipfile  # late agiza for breaking circular dependency

    ikiwa not zipfile.is_zipfile(filename):
        raise ReadError("%s is not a zip file" % filename)

    zip = zipfile.ZipFile(filename)
    try:
        for info in zip.infolist():
            name = info.filename

            # don't extract absolute paths or ones with .. in them
            ikiwa name.startswith('/') or '..' in name:
                continue

            target = os.path.join(extract_dir, *name.split('/'))
            ikiwa not target:
                continue

            _ensure_directory(target)
            ikiwa not name.endswith('/'):
                # file
                data = zip.read(info.filename)
                f = open(target, 'wb')
                try:
                    f.write(data)
                finally:
                    f.close()
                    del data
    finally:
        zip.close()

eleza _unpack_tarfile(filename, extract_dir):
    """Unpack tar/tar.gz/tar.bz2/tar.xz `filename` to `extract_dir`
    """
    agiza tarfile  # late agiza for breaking circular dependency
    try:
        tarobj = tarfile.open(filename)
    except tarfile.TarError:
        raise ReadError(
            "%s is not a compressed or uncompressed tar file" % filename)
    try:
        tarobj.extractall(extract_dir)
    finally:
        tarobj.close()

_UNPACK_FORMATS = {
    'tar':   (['.tar'], _unpack_tarfile, [], "uncompressed tar file"),
    'zip':   (['.zip'], _unpack_zipfile, [], "ZIP file"),
}

ikiwa _ZLIB_SUPPORTED:
    _UNPACK_FORMATS['gztar'] = (['.tar.gz', '.tgz'], _unpack_tarfile, [],
                                "gzip'ed tar-file")

ikiwa _BZ2_SUPPORTED:
    _UNPACK_FORMATS['bztar'] = (['.tar.bz2', '.tbz2'], _unpack_tarfile, [],
                                "bzip2'ed tar-file")

ikiwa _LZMA_SUPPORTED:
    _UNPACK_FORMATS['xztar'] = (['.tar.xz', '.txz'], _unpack_tarfile, [],
                                "xz'ed tar-file")

eleza _find_unpack_format(filename):
    for name, info in _UNPACK_FORMATS.items():
        for extension in info[0]:
            ikiwa filename.endswith(extension):
                rudisha name
    rudisha None

eleza unpack_archive(filename, extract_dir=None, format=None):
    """Unpack an archive.

    `filename` is the name of the archive.

    `extract_dir` is the name of the target directory, where the archive
    is unpacked. If not provided, the current working directory is used.

    `format` is the archive format: one of "zip", "tar", "gztar", "bztar",
    or "xztar".  Or any other registered format.  If not provided,
    unpack_archive will use the filename extension and see ikiwa an unpacker
    was registered for that extension.

    In case none is found, a ValueError is raised.
    """
    ikiwa extract_dir is None:
        extract_dir = os.getcwd()

    extract_dir = os.fspath(extract_dir)
    filename = os.fspath(filename)

    ikiwa format is not None:
        try:
            format_info = _UNPACK_FORMATS[format]
        except KeyError:
            raise ValueError("Unknown unpack format '{0}'".format(format)) kutoka None

        func = format_info[1]
        func(filename, extract_dir, **dict(format_info[2]))
    else:
        # we need to look at the registered unpackers supported extensions
        format = _find_unpack_format(filename)
        ikiwa format is None:
            raise ReadError("Unknown archive format '{0}'".format(filename))

        func = _UNPACK_FORMATS[format][1]
        kwargs = dict(_UNPACK_FORMATS[format][2])
        func(filename, extract_dir, **kwargs)


ikiwa hasattr(os, 'statvfs'):

    __all__.append('disk_usage')
    _ntuple_diskusage = collections.namedtuple('usage', 'total used free')
    _ntuple_diskusage.total.__doc__ = 'Total space in bytes'
    _ntuple_diskusage.used.__doc__ = 'Used space in bytes'
    _ntuple_diskusage.free.__doc__ = 'Free space in bytes'

    eleza disk_usage(path):
        """Return disk usage statistics about the given path.

        Returned value is a named tuple with attributes 'total', 'used' and
        'free', which are the amount of total, used and free space, in bytes.
        """
        st = os.statvfs(path)
        free = st.f_bavail * st.f_frsize
        total = st.f_blocks * st.f_frsize
        used = (st.f_blocks - st.f_bfree) * st.f_frsize
        rudisha _ntuple_diskusage(total, used, free)

elikiwa _WINDOWS:

    __all__.append('disk_usage')
    _ntuple_diskusage = collections.namedtuple('usage', 'total used free')

    eleza disk_usage(path):
        """Return disk usage statistics about the given path.

        Returned values is a named tuple with attributes 'total', 'used' and
        'free', which are the amount of total, used and free space, in bytes.
        """
        total, free = nt._getdiskusage(path)
        used = total - free
        rudisha _ntuple_diskusage(total, used, free)


eleza chown(path, user=None, group=None):
    """Change owner user and group of the given path.

    user and group can be the uid/gid or the user/group names, and in that case,
    they are converted to their respective uid/gid.
    """

    ikiwa user is None and group is None:
        raise ValueError("user and/or group must be set")

    _user = user
    _group = group

    # -1 means don't change it
    ikiwa user is None:
        _user = -1
    # user can either be an int (the uid) or a string (the system username)
    elikiwa isinstance(user, str):
        _user = _get_uid(user)
        ikiwa _user is None:
            raise LookupError("no such user: {!r}".format(user))

    ikiwa group is None:
        _group = -1
    elikiwa not isinstance(group, int):
        _group = _get_gid(group)
        ikiwa _group is None:
            raise LookupError("no such group: {!r}".format(group))

    os.chown(path, _user, _group)

eleza get_terminal_size(fallback=(80, 24)):
    """Get the size of the terminal window.

    For each of the two dimensions, the environment variable, COLUMNS
    and LINES respectively, is checked. If the variable is defined and
    the value is a positive integer, it is used.

    When COLUMNS or LINES is not defined, which is the common case,
    the terminal connected to sys.__stdout__ is queried
    by invoking os.get_terminal_size.

    If the terminal size cannot be successfully queried, either because
    the system doesn't support querying, or because we are not
    connected to a terminal, the value given in fallback parameter
    is used. Fallback defaults to (80, 24) which is the default
    size used by many terminal emulators.

    The value returned is a named tuple of type os.terminal_size.
    """
    # columns, lines are the working values
    try:
        columns = int(os.environ['COLUMNS'])
    except (KeyError, ValueError):
        columns = 0

    try:
        lines = int(os.environ['LINES'])
    except (KeyError, ValueError):
        lines = 0

    # only query ikiwa necessary
    ikiwa columns <= 0 or lines <= 0:
        try:
            size = os.get_terminal_size(sys.__stdout__.fileno())
        except (AttributeError, ValueError, OSError):
            # stdout is None, closed, detached, or not a terminal, or
            # os.get_terminal_size() is unsupported
            size = os.terminal_size(fallback)
        ikiwa columns <= 0:
            columns = size.columns
        ikiwa lines <= 0:
            lines = size.lines

    rudisha os.terminal_size((columns, lines))


# Check that a given file can be accessed with the correct mode.
# Additionally check that `file` is not a directory, as on Windows
# directories pass the os.access check.
eleza _access_check(fn, mode):
    rudisha (os.path.exists(fn) and os.access(fn, mode)
            and not os.path.isdir(fn))


eleza which(cmd, mode=os.F_OK | os.X_OK, path=None):
    """Given a command, mode, and a PATH string, rudisha the path which
    conforms to the given mode on the PATH, or None ikiwa there is no such
    file.

    `mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
    of os.environ.get("PATH"), or can be overridden with a custom search
    path.

    """
    # If we're given a path with a directory part, look it up directly rather
    # than referring to PATH directories. This includes checking relative to the
    # current directory, e.g. ./script
    ikiwa os.path.dirname(cmd):
        ikiwa _access_check(cmd, mode):
            rudisha cmd
        rudisha None

    use_bytes = isinstance(cmd, bytes)

    ikiwa path is None:
        path = os.environ.get("PATH", None)
        ikiwa path is None:
            try:
                path = os.confstr("CS_PATH")
            except (AttributeError, ValueError):
                # os.confstr() or CS_PATH is not available
                path = os.defpath
        # bpo-35755: Don't use os.defpath ikiwa the PATH environment variable is
        # set to an empty string

    # PATH='' doesn't match, whereas PATH=':' looks in the current directory
    ikiwa not path:
        rudisha None

    ikiwa use_bytes:
        path = os.fsencode(path)
        path = path.split(os.fsencode(os.pathsep))
    else:
        path = os.fsdecode(path)
        path = path.split(os.pathsep)

    ikiwa sys.platform == "win32":
        # The current directory takes precedence on Windows.
        curdir = os.curdir
        ikiwa use_bytes:
            curdir = os.fsencode(curdir)
        ikiwa curdir not in path:
            path.insert(0, curdir)

        # PATHEXT is necessary to check on Windows.
        pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
        ikiwa use_bytes:
            pathext = [os.fsencode(ext) for ext in pathext]
        # See ikiwa the given file matches any of the expected path extensions.
        # This will allow us to short circuit when given "python.exe".
        # If it does match, only test that one, otherwise we have to try
        # others.
        ikiwa any(cmd.lower().endswith(ext.lower()) for ext in pathext):
            files = [cmd]
        else:
            files = [cmd + ext for ext in pathext]
    else:
        # On other platforms you don't have things like PATHEXT to tell you
        # what file suffixes are executable, so just pass on cmd as-is.
        files = [cmd]

    seen = set()
    for dir in path:
        normdir = os.path.normcase(dir)
        ikiwa not normdir in seen:
            seen.add(normdir)
            for thefile in files:
                name = os.path.join(dir, thefile)
                ikiwa _access_check(name, mode):
                    rudisha name
    rudisha None
