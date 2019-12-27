# Module 'ntpath' -- common operations on WinNT/Win95 pathnames
"""Common pathname manipulations, WindowsNT/95 version.

Instead of agizaing this module directly, agiza os and refer to this
module as os.path.
"""

# strings representing various path-related bits and pieces
# These are primarily for export; internally, they are hardcoded.
# Should be set before agizas for resolving cyclic dependency.
curdir = '.'
pardir = '..'
extsep = '.'
sep = '\\'
pathsep = ';'
altsep = '/'
defpath = '.;C:\\bin'
devnull = 'nul'

agiza os
agiza sys
agiza stat
agiza genericpath
kutoka genericpath agiza *

__all__ = ["normcase","isabs","join","splitdrive","split","splitext",
           "basename","dirname","commonprefix","getsize","getmtime",
           "getatime","getctime", "islink","exists","lexists","isdir","isfile",
           "ismount", "expanduser","expandvars","normpath","abspath",
           "curdir","pardir","sep","pathsep","defpath","altsep",
           "extsep","devnull","realpath","supports_unicode_filenames","relpath",
           "samefile", "sameopenfile", "samestat", "commonpath"]

eleza _get_bothseps(path):
    ikiwa isinstance(path, bytes):
        rudisha b'\\/'
    else:
        rudisha '\\/'

# Normalize the case of a pathname and map slashes to backslashes.
# Other normalizations (such as optimizing '../' away) are not done
# (this is done by normpath).

eleza normcase(s):
    """Normalize case of pathname.

    Makes all characters lowercase and all slashes into backslashes."""
    s = os.fspath(s)
    ikiwa isinstance(s, bytes):
        rudisha s.replace(b'/', b'\\').lower()
    else:
        rudisha s.replace('/', '\\').lower()


# Return whether a path is absolute.
# Trivial in Posix, harder on Windows.
# For Windows it is absolute ikiwa it starts with a slash or backslash (current
# volume), or ikiwa a pathname after the volume-letter-and-colon or UNC-resource
# starts with a slash or backslash.

eleza isabs(s):
    """Test whether a path is absolute"""
    s = os.fspath(s)
    s = splitdrive(s)[1]
    rudisha len(s) > 0 and s[0] in _get_bothseps(s)


# Join two (or more) paths.
eleza join(path, *paths):
    path = os.fspath(path)
    ikiwa isinstance(path, bytes):
        sep = b'\\'
        seps = b'\\/'
        colon = b':'
    else:
        sep = '\\'
        seps = '\\/'
        colon = ':'
    try:
        ikiwa not paths:
            path[:0] + sep  #23780: Ensure compatible data type even ikiwa p is null.
        result_drive, result_path = splitdrive(path)
        for p in map(os.fspath, paths):
            p_drive, p_path = splitdrive(p)
            ikiwa p_path and p_path[0] in seps:
                # Second path is absolute
                ikiwa p_drive or not result_drive:
                    result_drive = p_drive
                result_path = p_path
                continue
            elikiwa p_drive and p_drive != result_drive:
                ikiwa p_drive.lower() != result_drive.lower():
                    # Different drives => ignore the first path entirely
                    result_drive = p_drive
                    result_path = p_path
                    continue
                # Same drive in different case
                result_drive = p_drive
            # Second path is relative to the first
            ikiwa result_path and result_path[-1] not in seps:
                result_path = result_path + sep
            result_path = result_path + p_path
        ## add separator between UNC and non-absolute path
        ikiwa (result_path and result_path[0] not in seps and
            result_drive and result_drive[-1:] != colon):
            rudisha result_drive + sep + result_path
        rudisha result_drive + result_path
    except (TypeError, AttributeError, BytesWarning):
        genericpath._check_arg_types('join', path, *paths)
        raise


# Split a path in a drive specification (a drive letter followed by a
# colon) and the path specification.
# It is always true that drivespec + pathspec == p
eleza splitdrive(p):
    """Split a pathname into drive/UNC sharepoint and relative path specifiers.
    Returns a 2-tuple (drive_or_unc, path); either part may be empty.

    If you assign
        result = splitdrive(p)
    It is always true that:
        result[0] + result[1] == p

    If the path contained a drive letter, drive_or_unc will contain everything
    up to and including the colon.  e.g. splitdrive("c:/dir") returns ("c:", "/dir")

    If the path contained a UNC path, the drive_or_unc will contain the host name
    and share up to but not including the fourth directory separator character.
    e.g. splitdrive("//host/computer/dir") returns ("//host/computer", "/dir")

    Paths cannot contain both a drive letter and a UNC path.

    """
    p = os.fspath(p)
    ikiwa len(p) >= 2:
        ikiwa isinstance(p, bytes):
            sep = b'\\'
            altsep = b'/'
            colon = b':'
        else:
            sep = '\\'
            altsep = '/'
            colon = ':'
        normp = p.replace(altsep, sep)
        ikiwa (normp[0:2] == sep*2) and (normp[2:3] != sep):
            # is a UNC path:
            # vvvvvvvvvvvvvvvvvvvv drive letter or UNC path
            # \\machine\mountpoint\directory\etc\...
            #           directory ^^^^^^^^^^^^^^^
            index = normp.find(sep, 2)
            ikiwa index == -1:
                rudisha p[:0], p
            index2 = normp.find(sep, index + 1)
            # a UNC path can't have two slashes in a row
            # (after the initial two)
            ikiwa index2 == index + 1:
                rudisha p[:0], p
            ikiwa index2 == -1:
                index2 = len(p)
            rudisha p[:index2], p[index2:]
        ikiwa normp[1:2] == colon:
            rudisha p[:2], p[2:]
    rudisha p[:0], p


# Split a path in head (everything up to the last '/') and tail (the
# rest).  After the trailing '/' is stripped, the invariant
# join(head, tail) == p holds.
# The resulting head won't end in '/' unless it is the root.

eleza split(p):
    """Split a pathname.

    Return tuple (head, tail) where tail is everything after the final slash.
    Either part may be empty."""
    p = os.fspath(p)
    seps = _get_bothseps(p)
    d, p = splitdrive(p)
    # set i to index beyond p's last slash
    i = len(p)
    while i and p[i-1] not in seps:
        i -= 1
    head, tail = p[:i], p[i:]  # now tail has no slashes
    # remove trailing slashes kutoka head, unless it's all slashes
    head = head.rstrip(seps) or head
    rudisha d + head, tail


# Split a path in root and extension.
# The extension is everything starting at the last dot in the last
# pathname component; the root is everything before that.
# It is always true that root + ext == p.

eleza splitext(p):
    p = os.fspath(p)
    ikiwa isinstance(p, bytes):
        rudisha genericpath._splitext(p, b'\\', b'/', b'.')
    else:
        rudisha genericpath._splitext(p, '\\', '/', '.')
splitext.__doc__ = genericpath._splitext.__doc__


# Return the tail (basename) part of a path.

eleza basename(p):
    """Returns the final component of a pathname"""
    rudisha split(p)[1]


# Return the head (dirname) part of a path.

eleza dirname(p):
    """Returns the directory component of a pathname"""
    rudisha split(p)[0]

# Is a path a symbolic link?
# This will always rudisha false on systems where os.lstat doesn't exist.

eleza islink(path):
    """Test whether a path is a symbolic link.
    This will always rudisha false for Windows prior to 6.0.
    """
    try:
        st = os.lstat(path)
    except (OSError, ValueError, AttributeError):
        rudisha False
    rudisha stat.S_ISLNK(st.st_mode)

# Being true for dangling symbolic links is also useful.

eleza lexists(path):
    """Test whether a path exists.  Returns True for broken symbolic links"""
    try:
        st = os.lstat(path)
    except (OSError, ValueError):
        rudisha False
    rudisha True

# Is a path a mount point?
# Any drive letter root (eg c:\)
# Any share UNC (eg \\server\share)
# Any volume mounted on a filesystem folder
#
# No one method detects all three situations. Historically we've lexically
# detected drive letter roots and share UNCs. The canonical approach to
# detecting mounted volumes (querying the reparse tag) fails for the most
# common case: drive letter roots. The alternative which uses GetVolumePathName
# fails ikiwa the drive letter is the result of a SUBST.
try:
    kutoka nt agiza _getvolumepathname
except ImportError:
    _getvolumepathname = None
eleza ismount(path):
    """Test whether a path is a mount point (a drive root, the root of a
    share, or a mounted volume)"""
    path = os.fspath(path)
    seps = _get_bothseps(path)
    path = abspath(path)
    root, rest = splitdrive(path)
    ikiwa root and root[0] in seps:
        rudisha (not rest) or (rest in seps)
    ikiwa rest in seps:
        rudisha True

    ikiwa _getvolumepathname:
        rudisha path.rstrip(seps) == _getvolumepathname(path).rstrip(seps)
    else:
        rudisha False


# Expand paths beginning with '~' or '~user'.
# '~' means $HOME; '~user' means that user's home directory.
# If the path doesn't begin with '~', or ikiwa the user or $HOME is unknown,
# the path is returned unchanged (leaving error reporting to whatever
# function is called with the expanded path as argument).
# See also module 'glob' for expansion of *, ? and [...] in pathnames.
# (A function should also be defined to do full *sh-style environment
# variable expansion.)

eleza expanduser(path):
    """Expand ~ and ~user constructs.

    If user or $HOME is unknown, do nothing."""
    path = os.fspath(path)
    ikiwa isinstance(path, bytes):
        tilde = b'~'
    else:
        tilde = '~'
    ikiwa not path.startswith(tilde):
        rudisha path
    i, n = 1, len(path)
    while i < n and path[i] not in _get_bothseps(path):
        i += 1

    ikiwa 'USERPROFILE' in os.environ:
        userhome = os.environ['USERPROFILE']
    elikiwa not 'HOMEPATH' in os.environ:
        rudisha path
    else:
        try:
            drive = os.environ['HOMEDRIVE']
        except KeyError:
            drive = ''
        userhome = join(drive, os.environ['HOMEPATH'])

    ikiwa isinstance(path, bytes):
        userhome = os.fsencode(userhome)

    ikiwa i != 1: #~user
        userhome = join(dirname(userhome), path[1:i])

    rudisha userhome + path[i:]


# Expand paths containing shell variable substitutions.
# The following rules apply:
#       - no expansion within single quotes
#       - '$$' is translated into '$'
#       - '%%' is translated into '%' ikiwa '%%' are not seen in %var1%%var2%
#       - ${varname} is accepted.
#       - $varname is accepted.
#       - %varname% is accepted.
#       - varnames can be made out of letters, digits and the characters '_-'
#         (though is not verified in the ${varname} and %varname% cases)
# XXX With COMMAND.COM you can use any characters in a variable name,
# XXX except '^|<>='.

eleza expandvars(path):
    """Expand shell variables of the forms $var, ${var} and %var%.

    Unknown variables are left unchanged."""
    path = os.fspath(path)
    ikiwa isinstance(path, bytes):
        ikiwa b'$' not in path and b'%' not in path:
            rudisha path
        agiza string
        varchars = bytes(string.ascii_letters + string.digits + '_-', 'ascii')
        quote = b'\''
        percent = b'%'
        brace = b'{'
        rbrace = b'}'
        dollar = b'$'
        environ = getattr(os, 'environb', None)
    else:
        ikiwa '$' not in path and '%' not in path:
            rudisha path
        agiza string
        varchars = string.ascii_letters + string.digits + '_-'
        quote = '\''
        percent = '%'
        brace = '{'
        rbrace = '}'
        dollar = '$'
        environ = os.environ
    res = path[:0]
    index = 0
    pathlen = len(path)
    while index < pathlen:
        c = path[index:index+1]
        ikiwa c == quote:   # no expansion within single quotes
            path = path[index + 1:]
            pathlen = len(path)
            try:
                index = path.index(c)
                res += c + path[:index + 1]
            except ValueError:
                res += c + path
                index = pathlen - 1
        elikiwa c == percent:  # variable or '%'
            ikiwa path[index + 1:index + 2] == percent:
                res += c
                index += 1
            else:
                path = path[index+1:]
                pathlen = len(path)
                try:
                    index = path.index(percent)
                except ValueError:
                    res += percent + path
                    index = pathlen - 1
                else:
                    var = path[:index]
                    try:
                        ikiwa environ is None:
                            value = os.fsencode(os.environ[os.fsdecode(var)])
                        else:
                            value = environ[var]
                    except KeyError:
                        value = percent + var + percent
                    res += value
        elikiwa c == dollar:  # variable or '$$'
            ikiwa path[index + 1:index + 2] == dollar:
                res += c
                index += 1
            elikiwa path[index + 1:index + 2] == brace:
                path = path[index+2:]
                pathlen = len(path)
                try:
                    index = path.index(rbrace)
                except ValueError:
                    res += dollar + brace + path
                    index = pathlen - 1
                else:
                    var = path[:index]
                    try:
                        ikiwa environ is None:
                            value = os.fsencode(os.environ[os.fsdecode(var)])
                        else:
                            value = environ[var]
                    except KeyError:
                        value = dollar + brace + var + rbrace
                    res += value
            else:
                var = path[:0]
                index += 1
                c = path[index:index + 1]
                while c and c in varchars:
                    var += c
                    index += 1
                    c = path[index:index + 1]
                try:
                    ikiwa environ is None:
                        value = os.fsencode(os.environ[os.fsdecode(var)])
                    else:
                        value = environ[var]
                except KeyError:
                    value = dollar + var
                res += value
                ikiwa c:
                    index -= 1
        else:
            res += c
        index += 1
    rudisha res


# Normalize a path, e.g. A//B, A/./B and A/foo/../B all become A\B.
# Previously, this function also truncated pathnames to 8+3 format,
# but as this module is called "ntpath", that's obviously wrong!

eleza normpath(path):
    """Normalize path, eliminating double slashes, etc."""
    path = os.fspath(path)
    ikiwa isinstance(path, bytes):
        sep = b'\\'
        altsep = b'/'
        curdir = b'.'
        pardir = b'..'
        special_prefixes = (b'\\\\.\\', b'\\\\?\\')
    else:
        sep = '\\'
        altsep = '/'
        curdir = '.'
        pardir = '..'
        special_prefixes = ('\\\\.\\', '\\\\?\\')
    ikiwa path.startswith(special_prefixes):
        # in the case of paths with these prefixes:
        # \\.\ -> device names
        # \\?\ -> literal paths
        # do not do any normalization, but rudisha the path
        # unchanged apart kutoka the call to os.fspath()
        rudisha path
    path = path.replace(altsep, sep)
    prefix, path = splitdrive(path)

    # collapse initial backslashes
    ikiwa path.startswith(sep):
        prefix += sep
        path = path.lstrip(sep)

    comps = path.split(sep)
    i = 0
    while i < len(comps):
        ikiwa not comps[i] or comps[i] == curdir:
            del comps[i]
        elikiwa comps[i] == pardir:
            ikiwa i > 0 and comps[i-1] != pardir:
                del comps[i-1:i+1]
                i -= 1
            elikiwa i == 0 and prefix.endswith(sep):
                del comps[i]
            else:
                i += 1
        else:
            i += 1
    # If the path is now empty, substitute '.'
    ikiwa not prefix and not comps:
        comps.append(curdir)
    rudisha prefix + sep.join(comps)

eleza _abspath_fallback(path):
    """Return the absolute version of a path as a fallback function in case
    `nt._getfullpathname` is not available or raises OSError. See bpo-31047 for
    more.

    """

    path = os.fspath(path)
    ikiwa not isabs(path):
        ikiwa isinstance(path, bytes):
            cwd = os.getcwdb()
        else:
            cwd = os.getcwd()
        path = join(cwd, path)
    rudisha normpath(path)

# Return an absolute path.
try:
    kutoka nt agiza _getfullpathname

except ImportError: # not running on Windows - mock up something sensible
    abspath = _abspath_fallback

else:  # use native Windows method on Windows
    eleza abspath(path):
        """Return the absolute version of a path."""
        try:
            rudisha normpath(_getfullpathname(path))
        except (OSError, ValueError):
            rudisha _abspath_fallback(path)

try:
    kutoka nt agiza _getfinalpathname, readlink as _nt_readlink
except ImportError:
    # realpath is a no-op on systems without _getfinalpathname support.
    realpath = abspath
else:
    eleza _readlink_deep(path, seen=None):
        ikiwa seen is None:
            seen = set()

        # These error codes indicate that we should stop reading links and
        # rudisha the path we currently have.
        # 1: ERROR_INVALID_FUNCTION
        # 2: ERROR_FILE_NOT_FOUND
        # 3: ERROR_DIRECTORY_NOT_FOUND
        # 5: ERROR_ACCESS_DENIED
        # 21: ERROR_NOT_READY (implies drive with no media)
        # 32: ERROR_SHARING_VIOLATION (probably an NTFS paging file)
        # 50: ERROR_NOT_SUPPORTED (implies no support for reparse points)
        # 67: ERROR_BAD_NET_NAME (implies remote server unavailable)
        # 87: ERROR_INVALID_PARAMETER
        # 4390: ERROR_NOT_A_REPARSE_POINT
        # 4392: ERROR_INVALID_REPARSE_DATA
        # 4393: ERROR_REPARSE_TAG_INVALID
        allowed_winerror = 1, 2, 3, 5, 21, 32, 50, 67, 87, 4390, 4392, 4393

        while normcase(path) not in seen:
            seen.add(normcase(path))
            try:
                path = _nt_readlink(path)
            except OSError as ex:
                ikiwa ex.winerror in allowed_winerror:
                    break
                raise
            except ValueError:
                # Stop on reparse points that are not symlinks
                break
        rudisha path

    eleza _getfinalpathname_nonstrict(path):
        # These error codes indicate that we should stop resolving the path
        # and rudisha the value we currently have.
        # 1: ERROR_INVALID_FUNCTION
        # 2: ERROR_FILE_NOT_FOUND
        # 3: ERROR_DIRECTORY_NOT_FOUND
        # 5: ERROR_ACCESS_DENIED
        # 21: ERROR_NOT_READY (implies drive with no media)
        # 32: ERROR_SHARING_VIOLATION (probably an NTFS paging file)
        # 50: ERROR_NOT_SUPPORTED
        # 67: ERROR_BAD_NET_NAME (implies remote server unavailable)
        # 87: ERROR_INVALID_PARAMETER
        # 123: ERROR_INVALID_NAME
        # 1920: ERROR_CANT_ACCESS_FILE
        # 1921: ERROR_CANT_RESOLVE_FILENAME (implies unfollowable symlink)
        allowed_winerror = 1, 2, 3, 5, 21, 32, 50, 67, 87, 123, 1920, 1921

        # Non-strict algorithm is to find as much of the target directory
        # as we can and join the rest.
        tail = ''
        seen = set()
        while path:
            try:
                path = _readlink_deep(path, seen)
                path = _getfinalpathname(path)
                rudisha join(path, tail) ikiwa tail else path
            except OSError as ex:
                ikiwa ex.winerror not in allowed_winerror:
                    raise
                path, name = split(path)
                # TODO (bpo-38186): Request the real file name kutoka the directory
                # entry using FindFirstFileW. For now, we will rudisha the path
                # as best we have it
                ikiwa path and not name:
                    rudisha abspath(path + tail)
                tail = join(name, tail) ikiwa tail else name
        rudisha abspath(tail)

    eleza realpath(path):
        path = normpath(path)
        ikiwa isinstance(path, bytes):
            prefix = b'\\\\?\\'
            unc_prefix = b'\\\\?\\UNC\\'
            new_unc_prefix = b'\\\\'
            cwd = os.getcwdb()
        else:
            prefix = '\\\\?\\'
            unc_prefix = '\\\\?\\UNC\\'
            new_unc_prefix = '\\\\'
            cwd = os.getcwd()
        had_prefix = path.startswith(prefix)
        try:
            path = _getfinalpathname(path)
            initial_winerror = 0
        except OSError as ex:
            initial_winerror = ex.winerror
            path = _getfinalpathname_nonstrict(path)
        # The path returned by _getfinalpathname will always start with \\?\ -
        # strip off that prefix unless it was already provided on the original
        # path.
        ikiwa not had_prefix and path.startswith(prefix):
            # For UNC paths, the prefix will actually be \\?\UNC\
            # Handle that case as well.
            ikiwa path.startswith(unc_prefix):
                spath = new_unc_prefix + path[len(unc_prefix):]
            else:
                spath = path[len(prefix):]
            # Ensure that the non-prefixed path resolves to the same path
            try:
                ikiwa _getfinalpathname(spath) == path:
                    path = spath
            except OSError as ex:
                # If the path does not exist and originally did not exist, then
                # strip the prefix anyway.
                ikiwa ex.winerror == initial_winerror:
                    path = spath
        rudisha path


# Win9x family and earlier have no Unicode filename support.
supports_unicode_filenames = (hasattr(sys, "getwindowsversion") and
                              sys.getwindowsversion()[3] >= 2)

eleza relpath(path, start=None):
    """Return a relative version of a path"""
    path = os.fspath(path)
    ikiwa isinstance(path, bytes):
        sep = b'\\'
        curdir = b'.'
        pardir = b'..'
    else:
        sep = '\\'
        curdir = '.'
        pardir = '..'

    ikiwa start is None:
        start = curdir

    ikiwa not path:
        raise ValueError("no path specified")

    start = os.fspath(start)
    try:
        start_abs = abspath(normpath(start))
        path_abs = abspath(normpath(path))
        start_drive, start_rest = splitdrive(start_abs)
        path_drive, path_rest = splitdrive(path_abs)
        ikiwa normcase(start_drive) != normcase(path_drive):
            raise ValueError("path is on mount %r, start on mount %r" % (
                path_drive, start_drive))

        start_list = [x for x in start_rest.split(sep) ikiwa x]
        path_list = [x for x in path_rest.split(sep) ikiwa x]
        # Work out how much of the filepath is shared by start and path.
        i = 0
        for e1, e2 in zip(start_list, path_list):
            ikiwa normcase(e1) != normcase(e2):
                break
            i += 1

        rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
        ikiwa not rel_list:
            rudisha curdir
        rudisha join(*rel_list)
    except (TypeError, ValueError, AttributeError, BytesWarning, DeprecationWarning):
        genericpath._check_arg_types('relpath', path, start)
        raise


# Return the longest common sub-path of the sequence of paths given as input.
# The function is case-insensitive and 'separator-insensitive', i.e. ikiwa the
# only difference between two paths is the use of '\' versus '/' as separator,
# they are deemed to be equal.
#
# However, the returned path will have the standard '\' separator (even ikiwa the
# given paths had the alternative '/' separator) and will have the case of the
# first path given in the sequence. Additionally, any trailing separator is
# stripped kutoka the returned path.

eleza commonpath(paths):
    """Given a sequence of path names, returns the longest common sub-path."""

    ikiwa not paths:
        raise ValueError('commonpath() arg is an empty sequence')

    paths = tuple(map(os.fspath, paths))
    ikiwa isinstance(paths[0], bytes):
        sep = b'\\'
        altsep = b'/'
        curdir = b'.'
    else:
        sep = '\\'
        altsep = '/'
        curdir = '.'

    try:
        drivesplits = [splitdrive(p.replace(altsep, sep).lower()) for p in paths]
        split_paths = [p.split(sep) for d, p in drivesplits]

        try:
            isabs, = set(p[:1] == sep for d, p in drivesplits)
        except ValueError:
            raise ValueError("Can't mix absolute and relative paths") kutoka None

        # Check that all drive letters or UNC paths match. The check is made only
        # now otherwise type errors for mixing strings and bytes would not be
        # caught.
        ikiwa len(set(d for d, p in drivesplits)) != 1:
            raise ValueError("Paths don't have the same drive")

        drive, path = splitdrive(paths[0].replace(altsep, sep))
        common = path.split(sep)
        common = [c for c in common ikiwa c and c != curdir]

        split_paths = [[c for c in s ikiwa c and c != curdir] for s in split_paths]
        s1 = min(split_paths)
        s2 = max(split_paths)
        for i, c in enumerate(s1):
            ikiwa c != s2[i]:
                common = common[:i]
                break
        else:
            common = common[:len(s1)]

        prefix = drive + sep ikiwa isabs else drive
        rudisha prefix + sep.join(common)
    except (TypeError, AttributeError):
        genericpath._check_arg_types('commonpath', *paths)
        raise


try:
    # The genericpath.isdir implementation uses os.stat and checks the mode
    # attribute to tell whether or not the path is a directory.
    # This is overkill on Windows - just pass the path to GetFileAttributes
    # and check the attribute kutoka there.
    kutoka nt agiza _isdir as isdir
except ImportError:
    # Use genericpath.isdir as imported above.
    pass
