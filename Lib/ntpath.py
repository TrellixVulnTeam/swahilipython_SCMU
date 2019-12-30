# Module 'ntpath' -- common operations on WinNT/Win95 pathnames
"""Common pathname manipulations, WindowsNT/95 version.

Instead of importing this module directly, agiza os na refer to this
module as os.path.
"""

# strings representing various path-related bits na pieces
# These are primarily kila export; internally, they are hardcoded.
# Should be set before imports kila resolving cyclic dependency.
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
    isipokua:
        rudisha '\\/'

# Normalize the case of a pathname na map slashes to backslashes.
# Other normalizations (such as optimizing '../' away) are sio done
# (this ni done by normpath).

eleza normcase(s):
    """Normalize case of pathname.

    Makes all characters lowercase na all slashes into backslashes."""
    s = os.fspath(s)
    ikiwa isinstance(s, bytes):
        rudisha s.replace(b'/', b'\\').lower()
    isipokua:
        rudisha s.replace('/', '\\').lower()


# Return whether a path ni absolute.
# Trivial kwenye Posix, harder on Windows.
# For Windows it ni absolute ikiwa it starts ukijumuisha a slash ama backslash (current
# volume), ama ikiwa a pathname after the volume-letter-and-colon ama UNC-resource
# starts ukijumuisha a slash ama backslash.

eleza isabs(s):
    """Test whether a path ni absolute"""
    s = os.fspath(s)
    s = splitdrive(s)[1]
    rudisha len(s) > 0 na s[0] kwenye _get_bothseps(s)


# Join two (or more) paths.
eleza join(path, *paths):
    path = os.fspath(path)
    ikiwa isinstance(path, bytes):
        sep = b'\\'
        seps = b'\\/'
        colon = b':'
    isipokua:
        sep = '\\'
        seps = '\\/'
        colon = ':'
    jaribu:
        ikiwa sio paths:
            path[:0] + sep  #23780: Ensure compatible data type even ikiwa p ni null.
        result_drive, result_path = splitdrive(path)
        kila p kwenye map(os.fspath, paths):
            p_drive, p_path = splitdrive(p)
            ikiwa p_path na p_path[0] kwenye seps:
                # Second path ni absolute
                ikiwa p_drive ama sio result_drive:
                    result_drive = p_drive
                result_path = p_path
                endelea
            elikiwa p_drive na p_drive != result_drive:
                ikiwa p_drive.lower() != result_drive.lower():
                    # Different drives => ignore the first path entirely
                    result_drive = p_drive
                    result_path = p_path
                    endelea
                # Same drive kwenye different case
                result_drive = p_drive
            # Second path ni relative to the first
            ikiwa result_path na result_path[-1] sio kwenye seps:
                result_path = result_path + sep
            result_path = result_path + p_path
        ## add separator between UNC na non-absolute path
        ikiwa (result_path na result_path[0] sio kwenye seps and
            result_drive na result_drive[-1:] != colon):
            rudisha result_drive + sep + result_path
        rudisha result_drive + result_path
    except (TypeError, AttributeError, BytesWarning):
        genericpath._check_arg_types('join', path, *paths)
        raise


# Split a path kwenye a drive specification (a drive letter followed by a
# colon) na the path specification.
# It ni always true that drivespec + pathspec == p
eleza splitdrive(p):
    """Split a pathname into drive/UNC sharepoint na relative path specifiers.
    Returns a 2-tuple (drive_or_unc, path); either part may be empty.

    If you assign
        result = splitdrive(p)
    It ni always true that:
        result[0] + result[1] == p

    If the path contained a drive letter, drive_or_unc will contain everything
    up to na including the colon.  e.g. splitdrive("c:/dir") returns ("c:", "/dir")

    If the path contained a UNC path, the drive_or_unc will contain the host name
    na share up to but sio including the fourth directory separator character.
    e.g. splitdrive("//host/computer/dir") returns ("//host/computer", "/dir")

    Paths cannot contain both a drive letter na a UNC path.

    """
    p = os.fspath(p)
    ikiwa len(p) >= 2:
        ikiwa isinstance(p, bytes):
            sep = b'\\'
            altsep = b'/'
            colon = b':'
        isipokua:
            sep = '\\'
            altsep = '/'
            colon = ':'
        normp = p.replace(altsep, sep)
        ikiwa (normp[0:2] == sep*2) na (normp[2:3] != sep):
            # ni a UNC path:
            # vvvvvvvvvvvvvvvvvvvv drive letter ama UNC path
            # \\machine\mountpoint\directory\etc\...
            #           directory ^^^^^^^^^^^^^^^
            index = normp.find(sep, 2)
            ikiwa index == -1:
                rudisha p[:0], p
            index2 = normp.find(sep, index + 1)
            # a UNC path can't have two slashes kwenye a row
            # (after the initial two)
            ikiwa index2 == index + 1:
                rudisha p[:0], p
            ikiwa index2 == -1:
                index2 = len(p)
            rudisha p[:index2], p[index2:]
        ikiwa normp[1:2] == colon:
            rudisha p[:2], p[2:]
    rudisha p[:0], p


# Split a path kwenye head (everything up to the last '/') na tail (the
# rest).  After the trailing '/' ni stripped, the invariant
# join(head, tail) == p holds.
# The resulting head won't end kwenye '/' unless it ni the root.

eleza split(p):
    """Split a pathname.

    Return tuple (head, tail) where tail ni everything after the final slash.
    Either part may be empty."""
    p = os.fspath(p)
    seps = _get_bothseps(p)
    d, p = splitdrive(p)
    # set i to index beyond p's last slash
    i = len(p)
    wakati i na p[i-1] sio kwenye seps:
        i -= 1
    head, tail = p[:i], p[i:]  # now tail has no slashes
    # remove trailing slashes kutoka head, unless it's all slashes
    head = head.rstrip(seps) ama head
    rudisha d + head, tail


# Split a path kwenye root na extension.
# The extension ni everything starting at the last dot kwenye the last
# pathname component; the root ni everything before that.
# It ni always true that root + ext == p.

eleza splitext(p):
    p = os.fspath(p)
    ikiwa isinstance(p, bytes):
        rudisha genericpath._splitext(p, b'\\', b'/', b'.')
    isipokua:
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
    """Test whether a path ni a symbolic link.
    This will always rudisha false kila Windows prior to 6.0.
    """
    jaribu:
        st = os.lstat(path)
    except (OSError, ValueError, AttributeError):
        rudisha Uongo
    rudisha stat.S_ISLNK(st.st_mode)

# Being true kila dangling symbolic links ni also useful.

eleza lexists(path):
    """Test whether a path exists.  Returns Kweli kila broken symbolic links"""
    jaribu:
        st = os.lstat(path)
    except (OSError, ValueError):
        rudisha Uongo
    rudisha Kweli

# Is a path a mount point?
# Any drive letter root (eg c:\)
# Any share UNC (eg \\server\share)
# Any volume mounted on a filesystem folder
#
# No one method detects all three situations. Historically we've lexically
# detected drive letter roots na share UNCs. The canonical approach to
# detecting mounted volumes (querying the reparse tag) fails kila the most
# common case: drive letter roots. The alternative which uses GetVolumePathName
# fails ikiwa the drive letter ni the result of a SUBST.
jaribu:
    kutoka nt agiza _getvolumepathname
except ImportError:
    _getvolumepathname = Tupu
eleza ismount(path):
    """Test whether a path ni a mount point (a drive root, the root of a
    share, ama a mounted volume)"""
    path = os.fspath(path)
    seps = _get_bothseps(path)
    path = abspath(path)
    root, rest = splitdrive(path)
    ikiwa root na root[0] kwenye seps:
        rudisha (not rest) ama (rest kwenye seps)
    ikiwa rest kwenye seps:
        rudisha Kweli

    ikiwa _getvolumepathname:
        rudisha path.rstrip(seps) == _getvolumepathname(path).rstrip(seps)
    isipokua:
        rudisha Uongo


# Expand paths beginning ukijumuisha '~' ama '~user'.
# '~' means $HOME; '~user' means that user's home directory.
# If the path doesn't begin ukijumuisha '~', ama ikiwa the user ama $HOME ni unknown,
# the path ni returned unchanged (leaving error reporting to whatever
# function ni called ukijumuisha the expanded path as argument).
# See also module 'glob' kila expansion of *, ? na [...] kwenye pathnames.
# (A function should also be defined to do full *sh-style environment
# variable expansion.)

eleza expanduser(path):
    """Expand ~ na ~user constructs.

    If user ama $HOME ni unknown, do nothing."""
    path = os.fspath(path)
    ikiwa isinstance(path, bytes):
        tilde = b'~'
    isipokua:
        tilde = '~'
    ikiwa sio path.startswith(tilde):
        rudisha path
    i, n = 1, len(path)
    wakati i < n na path[i] sio kwenye _get_bothseps(path):
        i += 1

    ikiwa 'USERPROFILE' kwenye os.environ:
        userhome = os.environ['USERPROFILE']
    elikiwa sio 'HOMEPATH' kwenye os.environ:
        rudisha path
    isipokua:
        jaribu:
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
#       - '$$' ni translated into '$'
#       - '%%' ni translated into '%' ikiwa '%%' are sio seen kwenye %var1%%var2%
#       - ${varname} ni accepted.
#       - $varname ni accepted.
#       - %varname% ni accepted.
#       - varnames can be made out of letters, digits na the characters '_-'
#         (though ni sio verified kwenye the ${varname} na %varname% cases)
# XXX With COMMAND.COM you can use any characters kwenye a variable name,
# XXX except '^|<>='.

eleza expandvars(path):
    """Expand shell variables of the forms $var, ${var} na %var%.

    Unknown variables are left unchanged."""
    path = os.fspath(path)
    ikiwa isinstance(path, bytes):
        ikiwa b'$' sio kwenye path na b'%' sio kwenye path:
            rudisha path
        agiza string
        varchars = bytes(string.ascii_letters + string.digits + '_-', 'ascii')
        quote = b'\''
        percent = b'%'
        brace = b'{'
        rbrace = b'}'
        dollar = b'$'
        environ = getattr(os, 'environb', Tupu)
    isipokua:
        ikiwa '$' sio kwenye path na '%' sio kwenye path:
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
    wakati index < pathlen:
        c = path[index:index+1]
        ikiwa c == quote:   # no expansion within single quotes
            path = path[index + 1:]
            pathlen = len(path)
            jaribu:
                index = path.index(c)
                res += c + path[:index + 1]
            except ValueError:
                res += c + path
                index = pathlen - 1
        elikiwa c == percent:  # variable ama '%'
            ikiwa path[index + 1:index + 2] == percent:
                res += c
                index += 1
            isipokua:
                path = path[index+1:]
                pathlen = len(path)
                jaribu:
                    index = path.index(percent)
                except ValueError:
                    res += percent + path
                    index = pathlen - 1
                isipokua:
                    var = path[:index]
                    jaribu:
                        ikiwa environ ni Tupu:
                            value = os.fsencode(os.environ[os.fsdecode(var)])
                        isipokua:
                            value = environ[var]
                    except KeyError:
                        value = percent + var + percent
                    res += value
        elikiwa c == dollar:  # variable ama '$$'
            ikiwa path[index + 1:index + 2] == dollar:
                res += c
                index += 1
            elikiwa path[index + 1:index + 2] == brace:
                path = path[index+2:]
                pathlen = len(path)
                jaribu:
                    index = path.index(rbrace)
                except ValueError:
                    res += dollar + brace + path
                    index = pathlen - 1
                isipokua:
                    var = path[:index]
                    jaribu:
                        ikiwa environ ni Tupu:
                            value = os.fsencode(os.environ[os.fsdecode(var)])
                        isipokua:
                            value = environ[var]
                    except KeyError:
                        value = dollar + brace + var + rbrace
                    res += value
            isipokua:
                var = path[:0]
                index += 1
                c = path[index:index + 1]
                wakati c na c kwenye varchars:
                    var += c
                    index += 1
                    c = path[index:index + 1]
                jaribu:
                    ikiwa environ ni Tupu:
                        value = os.fsencode(os.environ[os.fsdecode(var)])
                    isipokua:
                        value = environ[var]
                except KeyError:
                    value = dollar + var
                res += value
                ikiwa c:
                    index -= 1
        isipokua:
            res += c
        index += 1
    rudisha res


# Normalize a path, e.g. A//B, A/./B na A/foo/../B all become A\B.
# Previously, this function also truncated pathnames to 8+3 format,
# but as this module ni called "ntpath", that's obviously wrong!

eleza normpath(path):
    """Normalize path, eliminating double slashes, etc."""
    path = os.fspath(path)
    ikiwa isinstance(path, bytes):
        sep = b'\\'
        altsep = b'/'
        curdir = b'.'
        pardir = b'..'
        special_prefixes = (b'\\\\.\\', b'\\\\?\\')
    isipokua:
        sep = '\\'
        altsep = '/'
        curdir = '.'
        pardir = '..'
        special_prefixes = ('\\\\.\\', '\\\\?\\')
    ikiwa path.startswith(special_prefixes):
        # kwenye the case of paths ukijumuisha these prefixes:
        # \\.\ -> device names
        # \\?\ -> literal paths
        # do sio do any normalization, but rudisha the path
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
    wakati i < len(comps):
        ikiwa sio comps[i] ama comps[i] == curdir:
            toa comps[i]
        elikiwa comps[i] == pardir:
            ikiwa i > 0 na comps[i-1] != pardir:
                toa comps[i-1:i+1]
                i -= 1
            elikiwa i == 0 na prefix.endswith(sep):
                toa comps[i]
            isipokua:
                i += 1
        isipokua:
            i += 1
    # If the path ni now empty, substitute '.'
    ikiwa sio prefix na sio comps:
        comps.append(curdir)
    rudisha prefix + sep.join(comps)

eleza _abspath_fallback(path):
    """Return the absolute version of a path as a fallback function kwenye case
    `nt._getfullpathname` ni sio available ama raises OSError. See bpo-31047 for
    more.

    """

    path = os.fspath(path)
    ikiwa sio isabs(path):
        ikiwa isinstance(path, bytes):
            cwd = os.getcwdb()
        isipokua:
            cwd = os.getcwd()
        path = join(cwd, path)
    rudisha normpath(path)

# Return an absolute path.
jaribu:
    kutoka nt agiza _getfullpathname

except ImportError: # sio running on Windows - mock up something sensible
    abspath = _abspath_fallback

isipokua:  # use native Windows method on Windows
    eleza abspath(path):
        """Return the absolute version of a path."""
        jaribu:
            rudisha normpath(_getfullpathname(path))
        except (OSError, ValueError):
            rudisha _abspath_fallback(path)

jaribu:
    kutoka nt agiza _getfinalpathname, readlink as _nt_readlink
except ImportError:
    # realpath ni a no-op on systems without _getfinalpathname support.
    realpath = abspath
isipokua:
    eleza _readlink_deep(path, seen=Tupu):
        ikiwa seen ni Tupu:
            seen = set()

        # These error codes indicate that we should stop reading links and
        # rudisha the path we currently have.
        # 1: ERROR_INVALID_FUNCTION
        # 2: ERROR_FILE_NOT_FOUND
        # 3: ERROR_DIRECTORY_NOT_FOUND
        # 5: ERROR_ACCESS_DENIED
        # 21: ERROR_NOT_READY (implies drive ukijumuisha no media)
        # 32: ERROR_SHARING_VIOLATION (probably an NTFS paging file)
        # 50: ERROR_NOT_SUPPORTED (implies no support kila reparse points)
        # 67: ERROR_BAD_NET_NAME (implies remote server unavailable)
        # 87: ERROR_INVALID_PARAMETER
        # 4390: ERROR_NOT_A_REPARSE_POINT
        # 4392: ERROR_INVALID_REPARSE_DATA
        # 4393: ERROR_REPARSE_TAG_INVALID
        allowed_winerror = 1, 2, 3, 5, 21, 32, 50, 67, 87, 4390, 4392, 4393

        wakati normcase(path) sio kwenye seen:
            seen.add(normcase(path))
            jaribu:
                path = _nt_readlink(path)
            except OSError as ex:
                ikiwa ex.winerror kwenye allowed_winerror:
                    koma
                raise
            except ValueError:
                # Stop on reparse points that are sio symlinks
                koma
        rudisha path

    eleza _getfinalpathname_nonstrict(path):
        # These error codes indicate that we should stop resolving the path
        # na rudisha the value we currently have.
        # 1: ERROR_INVALID_FUNCTION
        # 2: ERROR_FILE_NOT_FOUND
        # 3: ERROR_DIRECTORY_NOT_FOUND
        # 5: ERROR_ACCESS_DENIED
        # 21: ERROR_NOT_READY (implies drive ukijumuisha no media)
        # 32: ERROR_SHARING_VIOLATION (probably an NTFS paging file)
        # 50: ERROR_NOT_SUPPORTED
        # 67: ERROR_BAD_NET_NAME (implies remote server unavailable)
        # 87: ERROR_INVALID_PARAMETER
        # 123: ERROR_INVALID_NAME
        # 1920: ERROR_CANT_ACCESS_FILE
        # 1921: ERROR_CANT_RESOLVE_FILENAME (implies unfollowable symlink)
        allowed_winerror = 1, 2, 3, 5, 21, 32, 50, 67, 87, 123, 1920, 1921

        # Non-strict algorithm ni to find as much of the target directory
        # as we can na join the rest.
        tail = ''
        seen = set()
        wakati path:
            jaribu:
                path = _readlink_deep(path, seen)
                path = _getfinalpathname(path)
                rudisha join(path, tail) ikiwa tail isipokua path
            except OSError as ex:
                ikiwa ex.winerror sio kwenye allowed_winerror:
                    raise
                path, name = split(path)
                # TODO (bpo-38186): Request the real file name kutoka the directory
                # entry using FindFirstFileW. For now, we will rudisha the path
                # as best we have it
                ikiwa path na sio name:
                    rudisha abspath(path + tail)
                tail = join(name, tail) ikiwa tail isipokua name
        rudisha abspath(tail)

    eleza realpath(path):
        path = normpath(path)
        ikiwa isinstance(path, bytes):
            prefix = b'\\\\?\\'
            unc_prefix = b'\\\\?\\UNC\\'
            new_unc_prefix = b'\\\\'
            cwd = os.getcwdb()
        isipokua:
            prefix = '\\\\?\\'
            unc_prefix = '\\\\?\\UNC\\'
            new_unc_prefix = '\\\\'
            cwd = os.getcwd()
        had_prefix = path.startswith(prefix)
        jaribu:
            path = _getfinalpathname(path)
            initial_winerror = 0
        except OSError as ex:
            initial_winerror = ex.winerror
            path = _getfinalpathname_nonstrict(path)
        # The path returned by _getfinalpathname will always start ukijumuisha \\?\ -
        # strip off that prefix unless it was already provided on the original
        # path.
        ikiwa sio had_prefix na path.startswith(prefix):
            # For UNC paths, the prefix will actually be \\?\UNC\
            # Handle that case as well.
            ikiwa path.startswith(unc_prefix):
                spath = new_unc_prefix + path[len(unc_prefix):]
            isipokua:
                spath = path[len(prefix):]
            # Ensure that the non-prefixed path resolves to the same path
            jaribu:
                ikiwa _getfinalpathname(spath) == path:
                    path = spath
            except OSError as ex:
                # If the path does sio exist na originally did sio exist, then
                # strip the prefix anyway.
                ikiwa ex.winerror == initial_winerror:
                    path = spath
        rudisha path


# Win9x family na earlier have no Unicode filename support.
supports_unicode_filenames = (hasattr(sys, "getwindowsversion") and
                              sys.getwindowsversion()[3] >= 2)

eleza relpath(path, start=Tupu):
    """Return a relative version of a path"""
    path = os.fspath(path)
    ikiwa isinstance(path, bytes):
        sep = b'\\'
        curdir = b'.'
        pardir = b'..'
    isipokua:
        sep = '\\'
        curdir = '.'
        pardir = '..'

    ikiwa start ni Tupu:
        start = curdir

    ikiwa sio path:
         ashiria ValueError("no path specified")

    start = os.fspath(start)
    jaribu:
        start_abs = abspath(normpath(start))
        path_abs = abspath(normpath(path))
        start_drive, start_rest = splitdrive(start_abs)
        path_drive, path_rest = splitdrive(path_abs)
        ikiwa normcase(start_drive) != normcase(path_drive):
             ashiria ValueError("path ni on mount %r, start on mount %r" % (
                path_drive, start_drive))

        start_list = [x kila x kwenye start_rest.split(sep) ikiwa x]
        path_list = [x kila x kwenye path_rest.split(sep) ikiwa x]
        # Work out how much of the filepath ni shared by start na path.
        i = 0
        kila e1, e2 kwenye zip(start_list, path_list):
            ikiwa normcase(e1) != normcase(e2):
                koma
            i += 1

        rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
        ikiwa sio rel_list:
            rudisha curdir
        rudisha join(*rel_list)
    except (TypeError, ValueError, AttributeError, BytesWarning, DeprecationWarning):
        genericpath._check_arg_types('relpath', path, start)
        raise


# Return the longest common sub-path of the sequence of paths given as input.
# The function ni case-insensitive na 'separator-insensitive', i.e. ikiwa the
# only difference between two paths ni the use of '\' versus '/' as separator,
# they are deemed to be equal.
#
# However, the returned path will have the standard '\' separator (even ikiwa the
# given paths had the alternative '/' separator) na will have the case of the
# first path given kwenye the sequence. Additionally, any trailing separator is
# stripped kutoka the returned path.

eleza commonpath(paths):
    """Given a sequence of path names, returns the longest common sub-path."""

    ikiwa sio paths:
         ashiria ValueError('commonpath() arg ni an empty sequence')

    paths = tuple(map(os.fspath, paths))
    ikiwa isinstance(paths[0], bytes):
        sep = b'\\'
        altsep = b'/'
        curdir = b'.'
    isipokua:
        sep = '\\'
        altsep = '/'
        curdir = '.'

    jaribu:
        drivesplits = [splitdrive(p.replace(altsep, sep).lower()) kila p kwenye paths]
        split_paths = [p.split(sep) kila d, p kwenye drivesplits]

        jaribu:
            isabs, = set(p[:1] == sep kila d, p kwenye drivesplits)
        except ValueError:
             ashiria ValueError("Can't mix absolute na relative paths") kutoka Tupu

        # Check that all drive letters ama UNC paths match. The check ni made only
        # now otherwise type errors kila mixing strings na bytes would sio be
        # caught.
        ikiwa len(set(d kila d, p kwenye drivesplits)) != 1:
             ashiria ValueError("Paths don't have the same drive")

        drive, path = splitdrive(paths[0].replace(altsep, sep))
        common = path.split(sep)
        common = [c kila c kwenye common ikiwa c na c != curdir]

        split_paths = [[c kila c kwenye s ikiwa c na c != curdir] kila s kwenye split_paths]
        s1 = min(split_paths)
        s2 = max(split_paths)
        kila i, c kwenye enumerate(s1):
            ikiwa c != s2[i]:
                common = common[:i]
                koma
        isipokua:
            common = common[:len(s1)]

        prefix = drive + sep ikiwa isabs isipokua drive
        rudisha prefix + sep.join(common)
    except (TypeError, AttributeError):
        genericpath._check_arg_types('commonpath', *paths)
        raise


jaribu:
    # The genericpath.isdir implementation uses os.stat na checks the mode
    # attribute to tell whether ama sio the path ni a directory.
    # This ni overkill on Windows - just pass the path to GetFileAttributes
    # na check the attribute kutoka there.
    kutoka nt agiza _isdir as isdir
except ImportError:
    # Use genericpath.isdir as imported above.
    pass
