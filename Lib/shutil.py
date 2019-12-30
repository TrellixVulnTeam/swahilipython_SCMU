"""Utility functions kila copying na archiving files na directory trees.

XXX The functions here don't copy the resource fork ama other metadata on Mac.

"""

agiza os
agiza sys
agiza stat
agiza fnmatch
agiza collections
agiza errno

jaribu:
    agiza zlib
    toa zlib
    _ZLIB_SUPPORTED = Kweli
tatizo ImportError:
    _ZLIB_SUPPORTED = Uongo

jaribu:
    agiza bz2
    toa bz2
    _BZ2_SUPPORTED = Kweli
tatizo ImportError:
    _BZ2_SUPPORTED = Uongo

jaribu:
    agiza lzma
    toa lzma
    _LZMA_SUPPORTED = Kweli
tatizo ImportError:
    _LZMA_SUPPORTED = Uongo

jaribu:
    kutoka pwd agiza getpwnam
tatizo ImportError:
    getpwnam = Tupu

jaribu:
    kutoka grp agiza getgrnam
tatizo ImportError:
    getgrnam = Tupu

_WINDOWS = os.name == 'nt'
posix = nt = Tupu
ikiwa os.name == 'posix':
    agiza posix
lasivyo _WINDOWS:
    agiza nt

COPY_BUFSIZE = 1024 * 1024 ikiwa _WINDOWS isipokua 64 * 1024
_USE_CP_SENDFILE = hasattr(os, "sendfile") na sys.platform.startswith("linux")
_HAS_FCOPYFILE = posix na hasattr(posix, "_fcopyfile")  # macOS

__all__ = ["copyfileobj", "copyfile", "copymode", "copystat", "copy", "copy2",
           "copytree", "move", "rmtree", "Error", "SpecialFileError",
           "ExecError", "make_archive", "get_archive_formats",
           "register_archive_format", "unregister_archive_format",
           "get_unpack_formats", "register_unpack_format",
           "unregister_unpack_format", "unpack_archive",
           "ignore_patterns", "chown", "which", "get_terminal_size",
           "SameFileError"]
           # disk_usage ni added later, ikiwa available on the platform

kundi Error(OSError):
    pita

kundi SameFileError(Error):
    """Raised when source na destination are the same file."""

kundi SpecialFileError(OSError):
    """Raised when trying to do a kind of operation (e.g. copying) which is
    sio supported on a special file (e.g. a named pipe)"""

kundi ExecError(OSError):
    """Raised when a command could sio be executed"""

kundi ReadError(OSError):
    """Raised when an archive cannot be read"""

kundi RegistryError(Exception):
    """Raised when a registry operation ukijumuisha the archiving
    na unpacking registries fails"""

kundi _GiveupOnFastCopy(Exception):
    """Raised kama a signal to fallback on using raw read()/write()
    file copy when fast-copy functions fail to do so.
    """

eleza _fastcopy_fcopyfile(fsrc, fdst, flags):
    """Copy a regular file content ama metadata by using high-performance
    fcopyfile(3) syscall (macOS).
    """
    jaribu:
        infd = fsrc.fileno()
        outfd = fdst.fileno()
    tatizo Exception kama err:
        ashiria _GiveupOnFastCopy(err)  # sio a regular file

    jaribu:
        posix._fcopyfile(infd, outfd, flags)
    tatizo OSError kama err:
        err.filename = fsrc.name
        err.filename2 = fdst.name
        ikiwa err.errno kwenye {errno.EINVAL, errno.ENOTSUP}:
            ashiria _GiveupOnFastCopy(err)
        isipokua:
            ashiria err kutoka Tupu

eleza _fastcopy_sendfile(fsrc, fdst):
    """Copy data kutoka one regular mmap-like fd to another by using
    high-performance sendfile(2) syscall.
    This should work on Linux >= 2.6.33 only.
    """
    # Note: copyfileobj() ni left alone kwenye order to sio introduce any
    # unexpected komaage. Possible risks by using zero-copy calls
    # kwenye copyfileobj() are:
    # - fdst cannot be open kwenye "a"(ppend) mode
    # - fsrc na fdst may be open kwenye "t"(ext) mode
    # - fsrc may be a BufferedReader (which hides unread data kwenye a buffer),
    #   GzipFile (which decompresses data), HTTPResponse (which decodes
    #   chunks).
    # - possibly others (e.g. encrypted fs/partition?)
    global _USE_CP_SENDFILE
    jaribu:
        infd = fsrc.fileno()
        outfd = fdst.fileno()
    tatizo Exception kama err:
        ashiria _GiveupOnFastCopy(err)  # sio a regular file

    # Hopefully the whole file will be copied kwenye a single call.
    # sendfile() ni called kwenye a loop 'till EOF ni reached (0 return)
    # so a bufsize smaller ama bigger than the actual file size
    # should sio make any difference, also kwenye case the file content
    # changes wakati being copied.
    jaribu:
        blocksize = max(os.fstat(infd).st_size, 2 ** 23)  # min 8MiB
    tatizo OSError:
        blocksize = 2 ** 27  # 128MiB
    # On 32-bit architectures truncate to 1GiB to avoid OverflowError,
    # see bpo-38319.
    ikiwa sys.maxsize < 2 ** 32:
        blocksize = min(blocksize, 2 ** 30)

    offset = 0
    wakati Kweli:
        jaribu:
            sent = os.sendfile(outfd, infd, offset, blocksize)
        tatizo OSError kama err:
            # ...in oder to have a more informative exception.
            err.filename = fsrc.name
            err.filename2 = fdst.name

            ikiwa err.errno == errno.ENOTSOCK:
                # sendfile() on this platform (probably Linux < 2.6.33)
                # does sio support copies between regular files (only
                # sockets).
                _USE_CP_SENDFILE = Uongo
                ashiria _GiveupOnFastCopy(err)

            ikiwa err.errno == errno.ENOSPC:  # filesystem ni full
                ashiria err kutoka Tupu

            # Give up on first call na ikiwa no data was copied.
            ikiwa offset == 0 na os.lseek(outfd, 0, os.SEEK_CUR) == 0:
                ashiria _GiveupOnFastCopy(err)

            ashiria err
        isipokua:
            ikiwa sent == 0:
                koma  # EOF
            offset += sent

eleza _copyfileobj_readinto(fsrc, fdst, length=COPY_BUFSIZE):
    """readinto()/memoryview() based variant of copyfileobj().
    *fsrc* must support readinto() method na both files must be
    open kwenye binary mode.
    """
    # Localize variable access to minimize overhead.
    fsrc_readinto = fsrc.readinto
    fdst_write = fdst.write
    ukijumuisha memoryview(bytearray(length)) kama mv:
        wakati Kweli:
            n = fsrc_readinto(mv)
            ikiwa sio n:
                koma
            lasivyo n < length:
                ukijumuisha mv[:n] kama smv:
                    fdst.write(smv)
            isipokua:
                fdst_write(mv)

eleza copyfileobj(fsrc, fdst, length=0):
    """copy data kutoka file-like object fsrc to file-like object fdst"""
    # Localize variable access to minimize overhead.
    ikiwa sio length:
        length = COPY_BUFSIZE
    fsrc_read = fsrc.read
    fdst_write = fdst.write
    wakati Kweli:
        buf = fsrc_read(length)
        ikiwa sio buf:
            koma
        fdst_write(buf)

eleza _samefile(src, dst):
    # Macintosh, Unix.
    ikiwa isinstance(src, os.DirEntry) na hasattr(os.path, 'samestat'):
        jaribu:
            rudisha os.path.samestat(src.stat(), os.stat(dst))
        tatizo OSError:
            rudisha Uongo

    ikiwa hasattr(os.path, 'samefile'):
        jaribu:
            rudisha os.path.samefile(src, dst)
        tatizo OSError:
            rudisha Uongo

    # All other platforms: check kila same pathname.
    rudisha (os.path.normcase(os.path.abspath(src)) ==
            os.path.normcase(os.path.abspath(dst)))

eleza _stat(fn):
    rudisha fn.stat() ikiwa isinstance(fn, os.DirEntry) isipokua os.stat(fn)

eleza _islink(fn):
    rudisha fn.is_symlink() ikiwa isinstance(fn, os.DirEntry) isipokua os.path.islink(fn)

eleza copyfile(src, dst, *, follow_symlinks=Kweli):
    """Copy data kutoka src to dst kwenye the most efficient way possible.

    If follow_symlinks ni sio set na src ni a symbolic link, a new
    symlink will be created instead of copying the file it points to.

    """
    ikiwa _samefile(src, dst):
        ashiria SameFileError("{!r} na {!r} are the same file".format(src, dst))

    file_size = 0
    kila i, fn kwenye enumerate([src, dst]):
        jaribu:
            st = _stat(fn)
        tatizo OSError:
            # File most likely does sio exist
            pita
        isipokua:
            # XXX What about other special files? (sockets, devices...)
            ikiwa stat.S_ISFIFO(st.st_mode):
                fn = fn.path ikiwa isinstance(fn, os.DirEntry) isipokua fn
                ashiria SpecialFileError("`%s` ni a named pipe" % fn)
            ikiwa _WINDOWS na i == 0:
                file_size = st.st_size

    ikiwa sio follow_symlinks na _islink(src):
        os.symlink(os.readlink(src), dst)
    isipokua:
        ukijumuisha open(src, 'rb') kama fsrc, open(dst, 'wb') kama fdst:
            # macOS
            ikiwa _HAS_FCOPYFILE:
                jaribu:
                    _fastcopy_fcopyfile(fsrc, fdst, posix._COPYFILE_DATA)
                    rudisha dst
                tatizo _GiveupOnFastCopy:
                    pita
            # Linux
            lasivyo _USE_CP_SENDFILE:
                jaribu:
                    _fastcopy_sendfile(fsrc, fdst)
                    rudisha dst
                tatizo _GiveupOnFastCopy:
                    pita
            # Windows, see:
            # https://github.com/python/cpython/pull/7160#discussion_r195405230
            lasivyo _WINDOWS na file_size > 0:
                _copyfileobj_readinto(fsrc, fdst, min(file_size, COPY_BUFSIZE))
                rudisha dst

            copyfileobj(fsrc, fdst)

    rudisha dst

eleza copymode(src, dst, *, follow_symlinks=Kweli):
    """Copy mode bits kutoka src to dst.

    If follow_symlinks ni sio set, symlinks aren't followed ikiwa na only
    ikiwa both `src` na `dst` are symlinks.  If `lchmod` isn't available
    (e.g. Linux) this method does nothing.

    """
    ikiwa sio follow_symlinks na _islink(src) na os.path.islink(dst):
        ikiwa hasattr(os, 'lchmod'):
            stat_func, chmod_func = os.lstat, os.lchmod
        isipokua:
            return
    isipokua:
        stat_func, chmod_func = _stat, os.chmod

    st = stat_func(src)
    chmod_func(dst, stat.S_IMODE(st.st_mode))

ikiwa hasattr(os, 'listxattr'):
    eleza _copyxattr(src, dst, *, follow_symlinks=Kweli):
        """Copy extended filesystem attributes kutoka `src` to `dst`.

        Overwrite existing attributes.

        If `follow_symlinks` ni false, symlinks won't be followed.

        """

        jaribu:
            names = os.listxattr(src, follow_symlinks=follow_symlinks)
        tatizo OSError kama e:
            ikiwa e.errno haiko kwenye (errno.ENOTSUP, errno.ENODATA, errno.EINVAL):
                raise
            return
        kila name kwenye names:
            jaribu:
                value = os.getxattr(src, name, follow_symlinks=follow_symlinks)
                os.setxattr(dst, name, value, follow_symlinks=follow_symlinks)
            tatizo OSError kama e:
                ikiwa e.errno haiko kwenye (errno.EPERM, errno.ENOTSUP, errno.ENODATA,
                                   errno.EINVAL):
                    raise
isipokua:
    eleza _copyxattr(*args, **kwargs):
        pita

eleza copystat(src, dst, *, follow_symlinks=Kweli):
    """Copy file metadata

    Copy the permission bits, last access time, last modification time, na
    flags kutoka `src` to `dst`. On Linux, copystat() also copies the "extended
    attributes" where possible. The file contents, owner, na group are
    unaffected. `src` na `dst` are path-like objects ama path names given as
    strings.

    If the optional flag `follow_symlinks` ni sio set, symlinks aren't
    followed ikiwa na only ikiwa both `src` na `dst` are symlinks.
    """
    eleza _nop(*args, ns=Tupu, follow_symlinks=Tupu):
        pita

    # follow symlinks (aka don't sio follow symlinks)
    follow = follow_symlinks ama sio (_islink(src) na os.path.islink(dst))
    ikiwa follow:
        # use the real function ikiwa it exists
        eleza lookup(name):
            rudisha getattr(os, name, _nop)
    isipokua:
        # use the real function only ikiwa it exists
        # *and* it supports follow_symlinks
        eleza lookup(name):
            fn = getattr(os, name, _nop)
            ikiwa fn kwenye os.supports_follow_symlinks:
                rudisha fn
            rudisha _nop

    ikiwa isinstance(src, os.DirEntry):
        st = src.stat(follow_symlinks=follow)
    isipokua:
        st = lookup("stat")(src, follow_symlinks=follow)
    mode = stat.S_IMODE(st.st_mode)
    lookup("utime")(dst, ns=(st.st_atime_ns, st.st_mtime_ns),
        follow_symlinks=follow)
    # We must copy extended attributes before the file ni (potentially)
    # chmod()'ed read-only, otherwise setxattr() will error ukijumuisha -EACCES.
    _copyxattr(src, dst, follow_symlinks=follow)
    jaribu:
        lookup("chmod")(dst, mode, follow_symlinks=follow)
    tatizo NotImplementedError:
        # ikiwa we got a NotImplementedError, it's because
        #   * follow_symlinks=Uongo,
        #   * lchown() ni unavailable, na
        #   * either
        #       * fchownat() ni unavailable ama
        #       * fchownat() doesn't implement AT_SYMLINK_NOFOLLOW.
        #         (it returned ENOSUP.)
        # therefore we're out of options--we simply cannot chown the
        # symlink.  give up, suppress the error.
        # (which ni what shutil always did kwenye this circumstance.)
        pita
    ikiwa hasattr(st, 'st_flags'):
        jaribu:
            lookup("chflags")(dst, st.st_flags, follow_symlinks=follow)
        tatizo OSError kama why:
            kila err kwenye 'EOPNOTSUPP', 'ENOTSUP':
                ikiwa hasattr(errno, err) na why.errno == getattr(errno, err):
                    koma
            isipokua:
                raise

eleza copy(src, dst, *, follow_symlinks=Kweli):
    """Copy data na mode bits ("cp src dst"). Return the file's destination.

    The destination may be a directory.

    If follow_symlinks ni false, symlinks won't be followed. This
    resembles GNU's "cp -P src dst".

    If source na destination are the same file, a SameFileError will be
    raised.

    """
    ikiwa os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    copyfile(src, dst, follow_symlinks=follow_symlinks)
    copymode(src, dst, follow_symlinks=follow_symlinks)
    rudisha dst

eleza copy2(src, dst, *, follow_symlinks=Kweli):
    """Copy data na metadata. Return the file's destination.

    Metadata ni copied ukijumuisha copystat(). Please see the copystat function
    kila more information.

    The destination may be a directory.

    If follow_symlinks ni false, symlinks won't be followed. This
    resembles GNU's "cp -P src dst".
    """
    ikiwa os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    copyfile(src, dst, follow_symlinks=follow_symlinks)
    copystat(src, dst, follow_symlinks=follow_symlinks)
    rudisha dst

eleza ignore_patterns(*patterns):
    """Function that can be used kama copytree() ignore parameter.

    Patterns ni a sequence of glob-style patterns
    that are used to exclude files"""
    eleza _ignore_patterns(path, names):
        ignored_names = []
        kila pattern kwenye patterns:
            ignored_names.extend(fnmatch.filter(names, pattern))
        rudisha set(ignored_names)
    rudisha _ignore_patterns

eleza _copytree(entries, src, dst, symlinks, ignore, copy_function,
              ignore_dangling_symlinks, dirs_exist_ok=Uongo):
    ikiwa ignore ni sio Tupu:
        ignored_names = ignore(src, set(os.listdir(src)))
    isipokua:
        ignored_names = set()

    os.makedirs(dst, exist_ok=dirs_exist_ok)
    errors = []
    use_srcentry = copy_function ni copy2 ama copy_function ni copy

    kila srcentry kwenye entries:
        ikiwa srcentry.name kwenye ignored_names:
            endelea
        srcname = os.path.join(src, srcentry.name)
        dstname = os.path.join(dst, srcentry.name)
        srcobj = srcentry ikiwa use_srcentry isipokua srcname
        jaribu:
            is_symlink = srcentry.is_symlink()
            ikiwa is_symlink na os.name == 'nt':
                # Special check kila directory junctions, which appear as
                # symlinks but we want to recurse.
                lstat = srcentry.stat(follow_symlinks=Uongo)
                ikiwa lstat.st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT:
                    is_symlink = Uongo
            ikiwa is_symlink:
                linkto = os.readlink(srcname)
                ikiwa symlinks:
                    # We can't just leave it to `copy_function` because legacy
                    # code ukijumuisha a custom `copy_function` may rely on copytree
                    # doing the right thing.
                    os.symlink(linkto, dstname)
                    copystat(srcobj, dstname, follow_symlinks=not symlinks)
                isipokua:
                    # ignore dangling symlink ikiwa the flag ni on
                    ikiwa sio os.path.exists(linkto) na ignore_dangling_symlinks:
                        endelea
                    # otherwise let the copy occur. copy2 will ashiria an error
                    ikiwa srcentry.is_dir():
                        copytree(srcobj, dstname, symlinks, ignore,
                                 copy_function, dirs_exist_ok=dirs_exist_ok)
                    isipokua:
                        copy_function(srcobj, dstname)
            lasivyo srcentry.is_dir():
                copytree(srcobj, dstname, symlinks, ignore, copy_function,
                         dirs_exist_ok=dirs_exist_ok)
            isipokua:
                # Will ashiria a SpecialFileError kila unsupported file types
                copy_function(srcobj, dstname)
        # catch the Error kutoka the recursive copytree so that we can
        # endelea ukijumuisha other files
        tatizo Error kama err:
            errors.extend(err.args[0])
        tatizo OSError kama why:
            errors.append((srcname, dstname, str(why)))
    jaribu:
        copystat(src, dst)
    tatizo OSError kama why:
        # Copying file access times may fail on Windows
        ikiwa getattr(why, 'winerror', Tupu) ni Tupu:
            errors.append((src, dst, str(why)))
    ikiwa errors:
        ashiria Error(errors)
    rudisha dst

eleza copytree(src, dst, symlinks=Uongo, ignore=Tupu, copy_function=copy2,
             ignore_dangling_symlinks=Uongo, dirs_exist_ok=Uongo):
    """Recursively copy a directory tree na rudisha the destination directory.

    dirs_exist_ok dictates whether to ashiria an exception kwenye case dst ama any
    missing parent directory already exists.

    If exception(s) occur, an Error ni raised ukijumuisha a list of reasons.

    If the optional symlinks flag ni true, symbolic links kwenye the
    source tree result kwenye symbolic links kwenye the destination tree; if
    it ni false, the contents of the files pointed to by symbolic
    links are copied. If the file pointed by the symlink doesn't
    exist, an exception will be added kwenye the list of errors raised in
    an Error exception at the end of the copy process.

    You can set the optional ignore_dangling_symlinks flag to true ikiwa you
    want to silence this exception. Notice that this has no effect on
    platforms that don't support os.symlink.

    The optional ignore argument ni a callable. If given, it
    ni called ukijumuisha the `src` parameter, which ni the directory
    being visited by copytree(), na `names` which ni the list of
    `src` contents, kama returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() ni called recursively, the callable will be
    called once kila each directory that ni copied. It returns a
    list of names relative to the `src` directory that should
    sio be copied.

    The optional copy_function argument ni a callable that will be used
    to copy each file. It will be called ukijumuisha the source path na the
    destination path kama arguments. By default, copy2() ni used, but any
    function that supports the same signature (like copy()) can be used.

    """
    sys.audit("shutil.copytree", src, dst)
    ukijumuisha os.scandir(src) kama entries:
        rudisha _copytree(entries=entries, src=src, dst=dst, symlinks=symlinks,
                         ignore=ignore, copy_function=copy_function,
                         ignore_dangling_symlinks=ignore_dangling_symlinks,
                         dirs_exist_ok=dirs_exist_ok)

ikiwa hasattr(os.stat_result, 'st_file_attributes'):
    # Special handling kila directory junctions to make them behave like
    # symlinks kila shutil.rmtree, since kwenye general they do sio appear as
    # regular links.
    eleza _rmtree_isdir(entry):
        jaribu:
            st = entry.stat(follow_symlinks=Uongo)
            rudisha (stat.S_ISDIR(st.st_mode) na not
                (st.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
                 na st.st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT))
        tatizo OSError:
            rudisha Uongo

    eleza _rmtree_islink(path):
        jaribu:
            st = os.lstat(path)
            rudisha (stat.S_ISLNK(st.st_mode) ama
                (st.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
                 na st.st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT))
        tatizo OSError:
            rudisha Uongo
isipokua:
    eleza _rmtree_isdir(entry):
        jaribu:
            rudisha entry.is_dir(follow_symlinks=Uongo)
        tatizo OSError:
            rudisha Uongo

    eleza _rmtree_islink(path):
        rudisha os.path.islink(path)

# version vulnerable to race conditions
eleza _rmtree_unsafe(path, onerror):
    jaribu:
        ukijumuisha os.scandir(path) kama scandir_it:
            entries = list(scandir_it)
    tatizo OSError:
        onerror(os.scandir, path, sys.exc_info())
        entries = []
    kila entry kwenye entries:
        fullname = entry.path
        ikiwa _rmtree_isdir(entry):
            jaribu:
                ikiwa entry.is_symlink():
                    # This can only happen ikiwa someone replaces
                    # a directory ukijumuisha a symlink after the call to
                    # os.scandir ama entry.is_dir above.
                    ashiria OSError("Cannot call rmtree on a symbolic link")
            tatizo OSError:
                onerror(os.path.islink, fullname, sys.exc_info())
                endelea
            _rmtree_unsafe(fullname, onerror)
        isipokua:
            jaribu:
                os.unlink(fullname)
            tatizo OSError:
                onerror(os.unlink, fullname, sys.exc_info())
    jaribu:
        os.rmdir(path)
    tatizo OSError:
        onerror(os.rmdir, path, sys.exc_info())

# Version using fd-based APIs to protect against races
eleza _rmtree_safe_fd(topfd, path, onerror):
    jaribu:
        ukijumuisha os.scandir(topfd) kama scandir_it:
            entries = list(scandir_it)
    tatizo OSError kama err:
        err.filename = path
        onerror(os.scandir, path, sys.exc_info())
        return
    kila entry kwenye entries:
        fullname = os.path.join(path, entry.name)
        jaribu:
            is_dir = entry.is_dir(follow_symlinks=Uongo)
        tatizo OSError:
            is_dir = Uongo
        isipokua:
            ikiwa is_dir:
                jaribu:
                    orig_st = entry.stat(follow_symlinks=Uongo)
                    is_dir = stat.S_ISDIR(orig_st.st_mode)
                tatizo OSError:
                    onerror(os.lstat, fullname, sys.exc_info())
                    endelea
        ikiwa is_dir:
            jaribu:
                dirfd = os.open(entry.name, os.O_RDONLY, dir_fd=topfd)
            tatizo OSError:
                onerror(os.open, fullname, sys.exc_info())
            isipokua:
                jaribu:
                    ikiwa os.path.samestat(orig_st, os.fstat(dirfd)):
                        _rmtree_safe_fd(dirfd, fullname, onerror)
                        jaribu:
                            os.rmdir(entry.name, dir_fd=topfd)
                        tatizo OSError:
                            onerror(os.rmdir, fullname, sys.exc_info())
                    isipokua:
                        jaribu:
                            # This can only happen ikiwa someone replaces
                            # a directory ukijumuisha a symlink after the call to
                            # os.scandir ama stat.S_ISDIR above.
                            ashiria OSError("Cannot call rmtree on a symbolic "
                                          "link")
                        tatizo OSError:
                            onerror(os.path.islink, fullname, sys.exc_info())
                mwishowe:
                    os.close(dirfd)
        isipokua:
            jaribu:
                os.unlink(entry.name, dir_fd=topfd)
            tatizo OSError:
                onerror(os.unlink, fullname, sys.exc_info())

_use_fd_functions = ({os.open, os.stat, os.unlink, os.rmdir} <=
                     os.supports_dir_fd na
                     os.scandir kwenye os.supports_fd na
                     os.stat kwenye os.supports_follow_symlinks)

eleza rmtree(path, ignore_errors=Uongo, onerror=Tupu):
    """Recursively delete a directory tree.

    If ignore_errors ni set, errors are ignored; otherwise, ikiwa onerror
    ni set, it ni called to handle the error ukijumuisha arguments (func,
    path, exc_info) where func ni platform na implementation dependent;
    path ni the argument to that function that caused it to fail; na
    exc_info ni a tuple returned by sys.exc_info().  If ignore_errors
    ni false na onerror ni Tupu, an exception ni raised.

    """
    sys.audit("shutil.rmtree", path)
    ikiwa ignore_errors:
        eleza onerror(*args):
            pita
    lasivyo onerror ni Tupu:
        eleza onerror(*args):
            raise
    ikiwa _use_fd_functions:
        # While the unsafe rmtree works fine on bytes, the fd based does not.
        ikiwa isinstance(path, bytes):
            path = os.fsdecode(path)
        # Note: To guard against symlink races, we use the standard
        # lstat()/open()/fstat() trick.
        jaribu:
            orig_st = os.lstat(path)
        tatizo Exception:
            onerror(os.lstat, path, sys.exc_info())
            return
        jaribu:
            fd = os.open(path, os.O_RDONLY)
        tatizo Exception:
            onerror(os.lstat, path, sys.exc_info())
            return
        jaribu:
            ikiwa os.path.samestat(orig_st, os.fstat(fd)):
                _rmtree_safe_fd(fd, path, onerror)
                jaribu:
                    os.rmdir(path)
                tatizo OSError:
                    onerror(os.rmdir, path, sys.exc_info())
            isipokua:
                jaribu:
                    # symlinks to directories are forbidden, see bug #1669
                    ashiria OSError("Cannot call rmtree on a symbolic link")
                tatizo OSError:
                    onerror(os.path.islink, path, sys.exc_info())
        mwishowe:
            os.close(fd)
    isipokua:
        jaribu:
            ikiwa _rmtree_islink(path):
                # symlinks to directories are forbidden, see bug #1669
                ashiria OSError("Cannot call rmtree on a symbolic link")
        tatizo OSError:
            onerror(os.path.islink, path, sys.exc_info())
            # can't endelea even ikiwa onerror hook returns
            return
        rudisha _rmtree_unsafe(path, onerror)

# Allow introspection of whether ama sio the hardening against symlink
# attacks ni supported on the current platform
rmtree.avoids_symlink_attacks = _use_fd_functions

eleza _basename(path):
    # A basename() variant which first strips the trailing slash, ikiwa present.
    # Thus we always get the last component of the path, even kila directories.
    sep = os.path.sep + (os.path.altsep ama '')
    rudisha os.path.basename(path.rstrip(sep))

eleza move(src, dst, copy_function=copy2):
    """Recursively move a file ama directory to another location. This is
    similar to the Unix "mv" command. Return the file ama directory's
    destination.

    If the destination ni a directory ama a symlink to a directory, the source
    ni moved inside the directory. The destination path must sio already
    exist.

    If the destination already exists but ni sio a directory, it may be
    overwritten depending on os.rename() semantics.

    If the destination ni on our current filesystem, then rename() ni used.
    Otherwise, src ni copied to the destination na then removed. Symlinks are
    recreated under the new name ikiwa os.rename() fails because of cross
    filesystem renames.

    The optional `copy_function` argument ni a callable that will be used
    to copy the source ama it will be delegated to `copytree`.
    By default, copy2() ni used, but any function that supports the same
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
            ashiria Error("Destination path '%s' already exists" % real_dst)
    jaribu:
        os.rename(src, real_dst)
    tatizo OSError:
        ikiwa os.path.islink(src):
            linkto = os.readlink(src)
            os.symlink(linkto, real_dst)
            os.unlink(src)
        lasivyo os.path.isdir(src):
            ikiwa _destinsrc(src, dst):
                ashiria Error("Cannot move a directory '%s' into itself"
                            " '%s'." % (src, dst))
            copytree(src, real_dst, copy_function=copy_function,
                     symlinks=Kweli)
            rmtree(src)
        isipokua:
            copy_function(src, real_dst)
            os.unlink(src)
    rudisha real_dst

eleza _destinsrc(src, dst):
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)
    ikiwa sio src.endswith(os.path.sep):
        src += os.path.sep
    ikiwa sio dst.endswith(os.path.sep):
        dst += os.path.sep
    rudisha dst.startswith(src)

eleza _get_gid(name):
    """Returns a gid, given a group name."""
    ikiwa getgrnam ni Tupu ama name ni Tupu:
        rudisha Tupu
    jaribu:
        result = getgrnam(name)
    tatizo KeyError:
        result = Tupu
    ikiwa result ni sio Tupu:
        rudisha result[2]
    rudisha Tupu

eleza _get_uid(name):
    """Returns an uid, given a user name."""
    ikiwa getpwnam ni Tupu ama name ni Tupu:
        rudisha Tupu
    jaribu:
        result = getpwnam(name)
    tatizo KeyError:
        result = Tupu
    ikiwa result ni sio Tupu:
        rudisha result[2]
    rudisha Tupu

eleza _make_tarball(base_name, base_dir, compress="gzip", verbose=0, dry_run=0,
                  owner=Tupu, group=Tupu, logger=Tupu):
    """Create a (possibly compressed) tar file kutoka all the files under
    'base_dir'.

    'compress' must be "gzip" (the default), "bzip2", "xz", ama Tupu.

    'owner' na 'group' can be used to define an owner na a group kila the
    archive that ni being built. If sio provided, the current owner na group
    will be used.

    The output tar file will be named 'base_name' +  ".tar", possibly plus
    the appropriate compression extension (".gz", ".bz2", ama ".xz").

    Returns the output filename.
    """
    ikiwa compress ni Tupu:
        tar_compression = ''
    lasivyo _ZLIB_SUPPORTED na compress == 'gzip':
        tar_compression = 'gz'
    lasivyo _BZ2_SUPPORTED na compress == 'bzip2':
        tar_compression = 'bz2'
    lasivyo _LZMA_SUPPORTED na compress == 'xz':
        tar_compression = 'xz'
    isipokua:
        ashiria ValueError("bad value kila 'compress', ama compression format sio "
                         "supported : {0}".format(compress))

    agiza tarfile  # late agiza kila komaing circular dependency

    compress_ext = '.' + tar_compression ikiwa compress isipokua ''
    archive_name = base_name + '.tar' + compress_ext
    archive_dir = os.path.dirname(archive_name)

    ikiwa archive_dir na sio os.path.exists(archive_dir):
        ikiwa logger ni sio Tupu:
            logger.info("creating %s", archive_dir)
        ikiwa sio dry_run:
            os.makedirs(archive_dir)

    # creating the tarball
    ikiwa logger ni sio Tupu:
        logger.info('Creating tar archive')

    uid = _get_uid(owner)
    gid = _get_gid(group)

    eleza _set_uid_gid(tarinfo):
        ikiwa gid ni sio Tupu:
            tarinfo.gid = gid
            tarinfo.gname = group
        ikiwa uid ni sio Tupu:
            tarinfo.uid = uid
            tarinfo.uname = owner
        rudisha tarinfo

    ikiwa sio dry_run:
        tar = tarfile.open(archive_name, 'w|%s' % tar_compression)
        jaribu:
            tar.add(base_dir, filter=_set_uid_gid)
        mwishowe:
            tar.close()

    rudisha archive_name

eleza _make_zipfile(base_name, base_dir, verbose=0, dry_run=0, logger=Tupu):
    """Create a zip file kutoka all the files under 'base_dir'.

    The output zip file will be named 'base_name' + ".zip".  Returns the
    name of the output zip file.
    """
    agiza zipfile  # late agiza kila komaing circular dependency

    zip_filename = base_name + ".zip"
    archive_dir = os.path.dirname(base_name)

    ikiwa archive_dir na sio os.path.exists(archive_dir):
        ikiwa logger ni sio Tupu:
            logger.info("creating %s", archive_dir)
        ikiwa sio dry_run:
            os.makedirs(archive_dir)

    ikiwa logger ni sio Tupu:
        logger.info("creating '%s' na adding '%s' to it",
                    zip_filename, base_dir)

    ikiwa sio dry_run:
        ukijumuisha zipfile.ZipFile(zip_filename, "w",
                             compression=zipfile.ZIP_DEFLATED) kama zf:
            path = os.path.normpath(base_dir)
            ikiwa path != os.curdir:
                zf.write(path, path)
                ikiwa logger ni sio Tupu:
                    logger.info("adding '%s'", path)
            kila dirpath, dirnames, filenames kwenye os.walk(base_dir):
                kila name kwenye sorted(dirnames):
                    path = os.path.normpath(os.path.join(dirpath, name))
                    zf.write(path, path)
                    ikiwa logger ni sio Tupu:
                        logger.info("adding '%s'", path)
                kila name kwenye filenames:
                    path = os.path.normpath(os.path.join(dirpath, name))
                    ikiwa os.path.isfile(path):
                        zf.write(path, path)
                        ikiwa logger ni sio Tupu:
                            logger.info("adding '%s'", path)

    rudisha zip_filename

_ARCHIVE_FORMATS = {
    'tar':   (_make_tarball, [('compress', Tupu)], "uncompressed tar file"),
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
    """Returns a list of supported formats kila archiving na unarchiving.

    Each element of the returned sequence ni a tuple (name, description)
    """
    formats = [(name, registry[2]) kila name, registry in
               _ARCHIVE_FORMATS.items()]
    formats.sort()
    rudisha formats

eleza register_archive_format(name, function, extra_args=Tupu, description=''):
    """Registers an archive format.

    name ni the name of the format. function ni the callable that will be
    used to create archives. If provided, extra_args ni a sequence of
    (name, value) tuples that will be pitaed kama arguments to the callable.
    description can be provided to describe the format, na will be returned
    by the get_archive_formats() function.
    """
    ikiwa extra_args ni Tupu:
        extra_args = []
    ikiwa sio callable(function):
        ashiria TypeError('The %s object ni sio callable' % function)
    ikiwa sio isinstance(extra_args, (tuple, list)):
        ashiria TypeError('extra_args needs to be a sequence')
    kila element kwenye extra_args:
        ikiwa sio isinstance(element, (tuple, list)) ama len(element) !=2:
            ashiria TypeError('extra_args elements are : (arg_name, value)')

    _ARCHIVE_FORMATS[name] = (function, extra_args, description)

eleza unregister_archive_format(name):
    toa _ARCHIVE_FORMATS[name]

eleza make_archive(base_name, format, root_dir=Tupu, base_dir=Tupu, verbose=0,
                 dry_run=0, owner=Tupu, group=Tupu, logger=Tupu):
    """Create an archive file (eg. zip ama tar).

    'base_name' ni the name of the file to create, minus any format-specific
    extension; 'format' ni the archive format: one of "zip", "tar", "gztar",
    "bztar", ama "xztar".  Or any other registered format.

    'root_dir' ni a directory that will be the root directory of the
    archive; ie. we typically chdir into 'root_dir' before creating the
    archive.  'base_dir' ni the directory where we start archiving from;
    ie. 'base_dir' will be the common prefix of all files na
    directories kwenye the archive.  'root_dir' na 'base_dir' both default
    to the current directory.  Returns the name of the archive file.

    'owner' na 'group' are used when creating a tar archive. By default,
    uses the current owner na group.
    """
    sys.audit("shutil.make_archive", base_name, format, root_dir, base_dir)
    save_cwd = os.getcwd()
    ikiwa root_dir ni sio Tupu:
        ikiwa logger ni sio Tupu:
            logger.debug("changing into '%s'", root_dir)
        base_name = os.path.abspath(base_name)
        ikiwa sio dry_run:
            os.chdir(root_dir)

    ikiwa base_dir ni Tupu:
        base_dir = os.curdir

    kwargs = {'dry_run': dry_run, 'logger': logger}

    jaribu:
        format_info = _ARCHIVE_FORMATS[format]
    tatizo KeyError:
        ashiria ValueError("unknown archive format '%s'" % format) kutoka Tupu

    func = format_info[0]
    kila arg, val kwenye format_info[1]:
        kwargs[arg] = val

    ikiwa format != 'zip':
        kwargs['owner'] = owner
        kwargs['group'] = group

    jaribu:
        filename = func(base_name, base_dir, **kwargs)
    mwishowe:
        ikiwa root_dir ni sio Tupu:
            ikiwa logger ni sio Tupu:
                logger.debug("changing back to '%s'", save_cwd)
            os.chdir(save_cwd)

    rudisha filename


eleza get_unpack_formats():
    """Returns a list of supported formats kila unpacking.

    Each element of the returned sequence ni a tuple
    (name, extensions, description)
    """
    formats = [(name, info[0], info[3]) kila name, info in
               _UNPACK_FORMATS.items()]
    formats.sort()
    rudisha formats

eleza _check_unpack_options(extensions, function, extra_args):
    """Checks what gets registered kama an unpacker."""
    # first make sure no other unpacker ni registered kila this extension
    existing_extensions = {}
    kila name, info kwenye _UNPACK_FORMATS.items():
        kila ext kwenye info[0]:
            existing_extensions[ext] = name

    kila extension kwenye extensions:
        ikiwa extension kwenye existing_extensions:
            msg = '%s ni already registered kila "%s"'
            ashiria RegistryError(msg % (extension,
                                       existing_extensions[extension]))

    ikiwa sio callable(function):
        ashiria TypeError('The registered function must be a callable')


eleza register_unpack_format(name, extensions, function, extra_args=Tupu,
                           description=''):
    """Registers an unpack format.

    `name` ni the name of the format. `extensions` ni a list of extensions
    corresponding to the format.

    `function` ni the callable that will be
    used to unpack archives. The callable will receive archives to unpack.
    If it's unable to handle an archive, it needs to ashiria a ReadError
    exception.

    If provided, `extra_args` ni a sequence of
    (name, value) tuples that will be pitaed kama arguments to the callable.
    description can be provided to describe the format, na will be returned
    by the get_unpack_formats() function.
    """
    ikiwa extra_args ni Tupu:
        extra_args = []
    _check_unpack_options(extensions, function, extra_args)
    _UNPACK_FORMATS[name] = extensions, function, extra_args, description

eleza unregister_unpack_format(name):
    """Removes the pack format kutoka the registry."""
    toa _UNPACK_FORMATS[name]

eleza _ensure_directory(path):
    """Ensure that the parent directory of `path` exists"""
    dirname = os.path.dirname(path)
    ikiwa sio os.path.isdir(dirname):
        os.makedirs(dirname)

eleza _unpack_zipfile(filename, extract_dir):
    """Unpack zip `filename` to `extract_dir`
    """
    agiza zipfile  # late agiza kila komaing circular dependency

    ikiwa sio zipfile.is_zipfile(filename):
        ashiria ReadError("%s ni sio a zip file" % filename)

    zip = zipfile.ZipFile(filename)
    jaribu:
        kila info kwenye zip.infolist():
            name = info.filename

            # don't extract absolute paths ama ones ukijumuisha .. kwenye them
            ikiwa name.startswith('/') ama '..' kwenye name:
                endelea

            target = os.path.join(extract_dir, *name.split('/'))
            ikiwa sio target:
                endelea

            _ensure_directory(target)
            ikiwa sio name.endswith('/'):
                # file
                data = zip.read(info.filename)
                f = open(target, 'wb')
                jaribu:
                    f.write(data)
                mwishowe:
                    f.close()
                    toa data
    mwishowe:
        zip.close()

eleza _unpack_tarfile(filename, extract_dir):
    """Unpack tar/tar.gz/tar.bz2/tar.xz `filename` to `extract_dir`
    """
    agiza tarfile  # late agiza kila komaing circular dependency
    jaribu:
        tarobj = tarfile.open(filename)
    tatizo tarfile.TarError:
        ashiria ReadError(
            "%s ni sio a compressed ama uncompressed tar file" % filename)
    jaribu:
        tarobj.extractall(extract_dir)
    mwishowe:
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
    kila name, info kwenye _UNPACK_FORMATS.items():
        kila extension kwenye info[0]:
            ikiwa filename.endswith(extension):
                rudisha name
    rudisha Tupu

eleza unpack_archive(filename, extract_dir=Tupu, format=Tupu):
    """Unpack an archive.

    `filename` ni the name of the archive.

    `extract_dir` ni the name of the target directory, where the archive
    ni unpacked. If sio provided, the current working directory ni used.

    `format` ni the archive format: one of "zip", "tar", "gztar", "bztar",
    ama "xztar".  Or any other registered format.  If sio provided,
    unpack_archive will use the filename extension na see ikiwa an unpacker
    was registered kila that extension.

    In case none ni found, a ValueError ni raised.
    """
    ikiwa extract_dir ni Tupu:
        extract_dir = os.getcwd()

    extract_dir = os.fspath(extract_dir)
    filename = os.fspath(filename)

    ikiwa format ni sio Tupu:
        jaribu:
            format_info = _UNPACK_FORMATS[format]
        tatizo KeyError:
            ashiria ValueError("Unknown unpack format '{0}'".format(format)) kutoka Tupu

        func = format_info[1]
        func(filename, extract_dir, **dict(format_info[2]))
    isipokua:
        # we need to look at the registered unpackers supported extensions
        format = _find_unpack_format(filename)
        ikiwa format ni Tupu:
            ashiria ReadError("Unknown archive format '{0}'".format(filename))

        func = _UNPACK_FORMATS[format][1]
        kwargs = dict(_UNPACK_FORMATS[format][2])
        func(filename, extract_dir, **kwargs)


ikiwa hasattr(os, 'statvfs'):

    __all__.append('disk_usage')
    _ntuple_diskusage = collections.namedtuple('usage', 'total used free')
    _ntuple_diskusage.total.__doc__ = 'Total space kwenye bytes'
    _ntuple_diskusage.used.__doc__ = 'Used space kwenye bytes'
    _ntuple_diskusage.free.__doc__ = 'Free space kwenye bytes'

    eleza disk_usage(path):
        """Return disk usage statistics about the given path.

        Returned value ni a named tuple ukijumuisha attributes 'total', 'used' na
        'free', which are the amount of total, used na free space, kwenye bytes.
        """
        st = os.statvfs(path)
        free = st.f_bavail * st.f_frsize
        total = st.f_blocks * st.f_frsize
        used = (st.f_blocks - st.f_bfree) * st.f_frsize
        rudisha _ntuple_diskusage(total, used, free)

lasivyo _WINDOWS:

    __all__.append('disk_usage')
    _ntuple_diskusage = collections.namedtuple('usage', 'total used free')

    eleza disk_usage(path):
        """Return disk usage statistics about the given path.

        Returned values ni a named tuple ukijumuisha attributes 'total', 'used' na
        'free', which are the amount of total, used na free space, kwenye bytes.
        """
        total, free = nt._getdiskusage(path)
        used = total - free
        rudisha _ntuple_diskusage(total, used, free)


eleza chown(path, user=Tupu, group=Tupu):
    """Change owner user na group of the given path.

    user na group can be the uid/gid ama the user/group names, na kwenye that case,
    they are converted to their respective uid/gid.
    """

    ikiwa user ni Tupu na group ni Tupu:
        ashiria ValueError("user and/or group must be set")

    _user = user
    _group = group

    # -1 means don't change it
    ikiwa user ni Tupu:
        _user = -1
    # user can either be an int (the uid) ama a string (the system username)
    lasivyo isinstance(user, str):
        _user = _get_uid(user)
        ikiwa _user ni Tupu:
            ashiria LookupError("no such user: {!r}".format(user))

    ikiwa group ni Tupu:
        _group = -1
    lasivyo sio isinstance(group, int):
        _group = _get_gid(group)
        ikiwa _group ni Tupu:
            ashiria LookupError("no such group: {!r}".format(group))

    os.chown(path, _user, _group)

eleza get_terminal_size(fallback=(80, 24)):
    """Get the size of the terminal window.

    For each of the two dimensions, the environment variable, COLUMNS
    na LINES respectively, ni checked. If the variable ni defined na
    the value ni a positive integer, it ni used.

    When COLUMNS ama LINES ni sio defined, which ni the common case,
    the terminal connected to sys.__stdout__ ni queried
    by invoking os.get_terminal_size.

    If the terminal size cannot be successfully queried, either because
    the system doesn't support querying, ama because we are not
    connected to a terminal, the value given kwenye fallback parameter
    ni used. Fallback defaults to (80, 24) which ni the default
    size used by many terminal emulators.

    The value returned ni a named tuple of type os.terminal_size.
    """
    # columns, lines are the working values
    jaribu:
        columns = int(os.environ['COLUMNS'])
    tatizo (KeyError, ValueError):
        columns = 0

    jaribu:
        lines = int(os.environ['LINES'])
    tatizo (KeyError, ValueError):
        lines = 0

    # only query ikiwa necessary
    ikiwa columns <= 0 ama lines <= 0:
        jaribu:
            size = os.get_terminal_size(sys.__stdout__.fileno())
        tatizo (AttributeError, ValueError, OSError):
            # stdout ni Tupu, closed, detached, ama sio a terminal, ama
            # os.get_terminal_size() ni unsupported
            size = os.terminal_size(fallback)
        ikiwa columns <= 0:
            columns = size.columns
        ikiwa lines <= 0:
            lines = size.lines

    rudisha os.terminal_size((columns, lines))


# Check that a given file can be accessed ukijumuisha the correct mode.
# Additionally check that `file` ni sio a directory, kama on Windows
# directories pita the os.access check.
eleza _access_check(fn, mode):
    rudisha (os.path.exists(fn) na os.access(fn, mode)
            na sio os.path.isdir(fn))


eleza which(cmd, mode=os.F_OK | os.X_OK, path=Tupu):
    """Given a command, mode, na a PATH string, rudisha the path which
    conforms to the given mode on the PATH, ama Tupu ikiwa there ni no such
    file.

    `mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
    of os.environ.get("PATH"), ama can be overridden ukijumuisha a custom search
    path.

    """
    # If we're given a path ukijumuisha a directory part, look it up directly rather
    # than referring to PATH directories. This includes checking relative to the
    # current directory, e.g. ./script
    ikiwa os.path.dirname(cmd):
        ikiwa _access_check(cmd, mode):
            rudisha cmd
        rudisha Tupu

    use_bytes = isinstance(cmd, bytes)

    ikiwa path ni Tupu:
        path = os.environ.get("PATH", Tupu)
        ikiwa path ni Tupu:
            jaribu:
                path = os.confstr("CS_PATH")
            tatizo (AttributeError, ValueError):
                # os.confstr() ama CS_PATH ni sio available
                path = os.defpath
        # bpo-35755: Don't use os.defpath ikiwa the PATH environment variable is
        # set to an empty string

    # PATH='' doesn't match, whereas PATH=':' looks kwenye the current directory
    ikiwa sio path:
        rudisha Tupu

    ikiwa use_bytes:
        path = os.fsencode(path)
        path = path.split(os.fsencode(os.pathsep))
    isipokua:
        path = os.fsdecode(path)
        path = path.split(os.pathsep)

    ikiwa sys.platform == "win32":
        # The current directory takes precedence on Windows.
        curdir = os.curdir
        ikiwa use_bytes:
            curdir = os.fsencode(curdir)
        ikiwa curdir haiko kwenye path:
            path.insert(0, curdir)

        # PATHEXT ni necessary to check on Windows.
        pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
        ikiwa use_bytes:
            pathext = [os.fsencode(ext) kila ext kwenye pathext]
        # See ikiwa the given file matches any of the expected path extensions.
        # This will allow us to short circuit when given "python.exe".
        # If it does match, only test that one, otherwise we have to try
        # others.
        ikiwa any(cmd.lower().endswith(ext.lower()) kila ext kwenye pathext):
            files = [cmd]
        isipokua:
            files = [cmd + ext kila ext kwenye pathext]
    isipokua:
        # On other platforms you don't have things like PATHEXT to tell you
        # what file suffixes are executable, so just pita on cmd as-is.
        files = [cmd]

    seen = set()
    kila dir kwenye path:
        normdir = os.path.normcase(dir)
        ikiwa sio normdir kwenye seen:
            seen.add(normdir)
            kila thefile kwenye files:
                name = os.path.join(dir, thefile)
                ikiwa _access_check(name, mode):
                    rudisha name
    rudisha Tupu
