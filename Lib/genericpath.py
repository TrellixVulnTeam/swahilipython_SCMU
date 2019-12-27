"""
Path operations common to more than one OS
Do not use directly.  The OS specific modules agiza the appropriate
functions kutoka this module themselves.
"""
agiza os
agiza stat

__all__ = ['commonprefix', 'exists', 'getatime', 'getctime', 'getmtime',
           'getsize', 'isdir', 'isfile', 'samefile', 'sameopenfile',
           'samestat']


# Does a path exist?
# This is false for dangling symbolic links on systems that support them.
eleza exists(path):
    """Test whether a path exists.  Returns False for broken symbolic links"""
    try:
        os.stat(path)
    except (OSError, ValueError):
        rudisha False
    rudisha True


# This follows symbolic links, so both islink() and isdir() can be true
# for the same path on systems that support symlinks
eleza isfile(path):
    """Test whether a path is a regular file"""
    try:
        st = os.stat(path)
    except (OSError, ValueError):
        rudisha False
    rudisha stat.S_ISREG(st.st_mode)


# Is a path a directory?
# This follows symbolic links, so both islink() and isdir()
# can be true for the same path on systems that support symlinks
eleza isdir(s):
    """Return true ikiwa the pathname refers to an existing directory."""
    try:
        st = os.stat(s)
    except (OSError, ValueError):
        rudisha False
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
    "Given a list of pathnames, returns the longest common leading component"
    ikiwa not m: rudisha ''
    # Some people pass in a list of pathname parts to operate in an OS-agnostic
    # fashion; don't try to translate in that case as that's an abuse of the
    # API and they are already doing what they need to be OS-agnostic and so
    # they most likely won't be using an os.PathLike object in the sublists.
    ikiwa not isinstance(m[0], (list, tuple)):
        m = tuple(map(os.fspath, m))
    s1 = min(m)
    s2 = max(m)
    for i, c in enumerate(s1):
        ikiwa c != s2[i]:
            rudisha s1[:i]
    rudisha s1

# Are two stat buffers (obtained kutoka stat, fstat or lstat)
# describing the same file?
eleza samestat(s1, s2):
    """Test whether two stat buffers reference the same file"""
    rudisha (s1.st_ino == s2.st_ino and
            s1.st_dev == s2.st_dev)


# Are two filenames really pointing to the same file?
eleza samefile(f1, f2):
    """Test whether two pathnames reference the same actual file or directory

    This is determined by the device number and i-node number and
    raises an exception ikiwa an os.stat() call on either pathname fails.
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


# Split a path in root and extension.
# The extension is everything starting at the last dot in the last
# pathname component; the root is everything before that.
# It is always true that root + ext == p.

# Generic implementation of splitext, to be parametrized with
# the separators
eleza _splitext(p, sep, altsep, extsep):
    """Split the extension kutoka a pathname.

    Extension is everything kutoka the last dot to the end, ignoring
    leading dots.  Returns "(root, ext)"; ext may be empty."""
    # NOTE: This code must work for text and bytes strings.

    sepIndex = p.rfind(sep)
    ikiwa altsep:
        altsepIndex = p.rfind(altsep)
        sepIndex = max(sepIndex, altsepIndex)

    dotIndex = p.rfind(extsep)
    ikiwa dotIndex > sepIndex:
        # skip all leading dots
        filenameIndex = sepIndex + 1
        while filenameIndex < dotIndex:
            ikiwa p[filenameIndex:filenameIndex+1] != extsep:
                rudisha p[:dotIndex], p[dotIndex:]
            filenameIndex += 1

    rudisha p, p[:0]

eleza _check_arg_types(funcname, *args):
    hasstr = hasbytes = False
    for s in args:
        ikiwa isinstance(s, str):
            hasstr = True
        elikiwa isinstance(s, bytes):
            hasbytes = True
        else:
            raise TypeError('%s() argument must be str or bytes, not %r' %
                            (funcname, s.__class__.__name__)) kutoka None
    ikiwa hasstr and hasbytes:
        raise TypeError("Can't mix strings and bytes in path components") kutoka None
