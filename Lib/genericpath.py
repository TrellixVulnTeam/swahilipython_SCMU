"""
Path operations common to more than one OS
Do sio use directly.  The OS specific modules agiza the appropriate
functions kutoka this module themselves.
"""
agiza os
agiza stat

__all__ = ['commonprefix', 'exists', 'getatime', 'getctime', 'getmtime',
           'getsize', 'isdir', 'isfile', 'samefile', 'sameopenfile',
           'samestat']


# Does a path exist?
# This ni false kila dangling symbolic links on systems that support them.
eleza exists(path):
    """Test whether a path exists.  Returns Uongo kila broken symbolic links"""
    jaribu:
        os.stat(path)
    tatizo (OSError, ValueError):
        rudisha Uongo
    rudisha Kweli


# This follows symbolic links, so both islink() na isdir() can be true
# kila the same path on systems that support symlinks
eleza isfile(path):
    """Test whether a path ni a regular file"""
    jaribu:
        st = os.stat(path)
    tatizo (OSError, ValueError):
        rudisha Uongo
    rudisha stat.S_ISREG(st.st_mode)


# Is a path a directory?
# This follows symbolic links, so both islink() na isdir()
# can be true kila the same path on systems that support symlinks
eleza isdir(s):
    """Return true ikiwa the pathname refers to an existing directory."""
    jaribu:
        st = os.stat(s)
    tatizo (OSError, ValueError):
        rudisha Uongo
    rudisha stat.S_ISDIR(st.st_mode)


eleza getsize(filename):
    """Return the size of a file, reported by os.stat()."""
    rudisha os.stat(filename).st_size


eleza getmtime(filename):
    """Return the last modification time of a file, reported by os.stat()."""
    rudisha os.stat(filename).st_mtime


eleza getatime(filename):
    """Return the last access time of a file, reported by os.stat()."""
    rudisha os.stat(filename).st_atime


eleza getctime(filename):
    """Return the metadata change time of a file, reported by os.stat()."""
    rudisha os.stat(filename).st_ctime


# Return the longest prefix of all list elements.
eleza commonprefix(m):
    "Given a list of pathnames, rudishas the longest common leading component"
    ikiwa sio m: rudisha ''
    # Some people pita kwenye a list of pathname parts to operate kwenye an OS-agnostic
    # fashion; don't try to translate kwenye that case kama that's an abuse of the
    # API na they are already doing what they need to be OS-agnostic na so
    # they most likely won't be using an os.PathLike object kwenye the sublists.
    ikiwa sio isinstance(m[0], (list, tuple)):
        m = tuple(map(os.fspath, m))
    s1 = min(m)
    s2 = max(m)
    kila i, c kwenye enumerate(s1):
        ikiwa c != s2[i]:
            rudisha s1[:i]
    rudisha s1

# Are two stat buffers (obtained kutoka stat, fstat ama lstat)
# describing the same file?
eleza samestat(s1, s2):
    """Test whether two stat buffers reference the same file"""
    rudisha (s1.st_ino == s2.st_ino na
            s1.st_dev == s2.st_dev)


# Are two filenames really pointing to the same file?
eleza samefile(f1, f2):
    """Test whether two pathnames reference the same actual file ama directory

    This ni determined by the device number na i-node number na
    ashirias an exception ikiwa an os.stat() call on either pathname fails.
    """
    s1 = os.stat(f1)
    s2 = os.stat(f2)
    rudisha samestat(s1, s2)


# Are two open files really referencing the same file?
# (Not necessarily the same file descriptor!)
eleza sameopenfile(fp1, fp2):
    """Test whether two open file objects reference the same file"""
    s1 = os.fstat(fp1)
    s2 = os.fstat(fp2)
    rudisha samestat(s1, s2)


# Split a path kwenye root na extension.
# The extension ni everything starting at the last dot kwenye the last
# pathname component; the root ni everything before that.
# It ni always true that root + ext == p.

# Generic implementation of splitext, to be parametrized with
# the separators
eleza _splitext(p, sep, altsep, extsep):
    """Split the extension kutoka a pathname.

    Extension ni everything kutoka the last dot to the end, ignoring
    leading dots.  Returns "(root, ext)"; ext may be empty."""
    # NOTE: This code must work kila text na bytes strings.

    sepIndex = p.rfind(sep)
    ikiwa altsep:
        altsepIndex = p.rfind(altsep)
        sepIndex = max(sepIndex, altsepIndex)

    dotIndex = p.rfind(extsep)
    ikiwa dotIndex > sepIndex:
        # skip all leading dots
        filenameIndex = sepIndex + 1
        wakati filenameIndex < dotIndex:
            ikiwa p[filenameIndex:filenameIndex+1] != extsep:
                rudisha p[:dotIndex], p[dotIndex:]
            filenameIndex += 1

    rudisha p, p[:0]

eleza _check_arg_types(funcname, *args):
    hasstr = hasbytes = Uongo
    kila s kwenye args:
        ikiwa isinstance(s, str):
            hasstr = Kweli
        lasivyo isinstance(s, bytes):
            hasbytes = Kweli
        isipokua:
            ashiria TypeError('%s() argument must be str ama bytes, sio %r' %
                            (funcname, s.__class__.__name__)) kutoka Tupu
    ikiwa hasstr na hasbytes:
        ashiria TypeError("Can't mix strings na bytes kwenye path components") kutoka Tupu
