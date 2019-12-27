"""Filename globbing utility."""

agiza os
agiza re
agiza fnmatch
agiza sys

__all__ = ["glob", "iglob", "escape"]

eleza glob(pathname, *, recursive=False):
    """Return a list of paths matching a pathname pattern.

    The pattern may contain simple shell-style wildcards a la
    fnmatch. However, unlike fnmatch, filenames starting with a
    dot are special cases that are not matched by '*' and '?'
    patterns.

    If recursive is true, the pattern '**' will match any files and
    zero or more directories and subdirectories.
    """
    rudisha list(iglob(pathname, recursive=recursive))

eleza iglob(pathname, *, recursive=False):
    """Return an iterator which yields the paths matching a pathname pattern.

    The pattern may contain simple shell-style wildcards a la
    fnmatch. However, unlike fnmatch, filenames starting with a
    dot are special cases that are not matched by '*' and '?'
    patterns.

    If recursive is true, the pattern '**' will match any files and
    zero or more directories and subdirectories.
    """
    it = _iglob(pathname, recursive, False)
    ikiwa recursive and _isrecursive(pathname):
        s = next(it)  # skip empty string
        assert not s
    rudisha it

eleza _iglob(pathname, recursive, dironly):
    sys.audit("glob.glob", pathname, recursive)
    dirname, basename = os.path.split(pathname)
    ikiwa not has_magic(pathname):
        assert not dironly
        ikiwa basename:
            ikiwa os.path.lexists(pathname):
                yield pathname
        else:
            # Patterns ending with a slash should match only directories
            ikiwa os.path.isdir(dirname):
                yield pathname
        return
    ikiwa not dirname:
        ikiwa recursive and _isrecursive(basename):
            yield kutoka _glob2(dirname, basename, dironly)
        else:
            yield kutoka _glob1(dirname, basename, dironly)
        return
    # `os.path.split()` returns the argument itself as a dirname ikiwa it is a
    # drive or UNC path.  Prevent an infinite recursion ikiwa a drive or UNC path
    # contains magic characters (i.e. r'\\?\C:').
    ikiwa dirname != pathname and has_magic(dirname):
        dirs = _iglob(dirname, recursive, True)
    else:
        dirs = [dirname]
    ikiwa has_magic(basename):
        ikiwa recursive and _isrecursive(basename):
            glob_in_dir = _glob2
        else:
            glob_in_dir = _glob1
    else:
        glob_in_dir = _glob0
    for dirname in dirs:
        for name in glob_in_dir(dirname, basename, dironly):
            yield os.path.join(dirname, name)

# These 2 helper functions non-recursively glob inside a literal directory.
# They rudisha a list of basenames.  _glob1 accepts a pattern while _glob0
# takes a literal basename (so it only has to check for its existence).

eleza _glob1(dirname, pattern, dironly):
    names = list(_iterdir(dirname, dironly))
    ikiwa not _ishidden(pattern):
        names = (x for x in names ikiwa not _ishidden(x))
    rudisha fnmatch.filter(names, pattern)

eleza _glob0(dirname, basename, dironly):
    ikiwa not basename:
        # `os.path.split()` returns an empty basename for paths ending with a
        # directory separator.  'q*x/' should match only directories.
        ikiwa os.path.isdir(dirname):
            rudisha [basename]
    else:
        ikiwa os.path.lexists(os.path.join(dirname, basename)):
            rudisha [basename]
    rudisha []

# Following functions are not public but can be used by third-party code.

eleza glob0(dirname, pattern):
    rudisha _glob0(dirname, pattern, False)

eleza glob1(dirname, pattern):
    rudisha _glob1(dirname, pattern, False)

# This helper function recursively yields relative pathnames inside a literal
# directory.

eleza _glob2(dirname, pattern, dironly):
    assert _isrecursive(pattern)
    yield pattern[:0]
    yield kutoka _rlistdir(dirname, dironly)

# If dironly is false, yields all file names inside a directory.
# If dironly is true, yields only directory names.
eleza _iterdir(dirname, dironly):
    ikiwa not dirname:
        ikiwa isinstance(dirname, bytes):
            dirname = bytes(os.curdir, 'ASCII')
        else:
            dirname = os.curdir
    try:
        with os.scandir(dirname) as it:
            for entry in it:
                try:
                    ikiwa not dironly or entry.is_dir():
                        yield entry.name
                except OSError:
                    pass
    except OSError:
        return

# Recursively yields relative pathnames inside a literal directory.
eleza _rlistdir(dirname, dironly):
    names = list(_iterdir(dirname, dironly))
    for x in names:
        ikiwa not _ishidden(x):
            yield x
            path = os.path.join(dirname, x) ikiwa dirname else x
            for y in _rlistdir(path, dironly):
                yield os.path.join(x, y)


magic_check = re.compile('([*?[])')
magic_check_bytes = re.compile(b'([*?[])')

eleza has_magic(s):
    ikiwa isinstance(s, bytes):
        match = magic_check_bytes.search(s)
    else:
        match = magic_check.search(s)
    rudisha match is not None

eleza _ishidden(path):
    rudisha path[0] in ('.', b'.'[0])

eleza _isrecursive(pattern):
    ikiwa isinstance(pattern, bytes):
        rudisha pattern == b'**'
    else:
        rudisha pattern == '**'

eleza escape(pathname):
    """Escape all special characters.
    """
    # Escaping is done by wrapping any of "*?[" between square brackets.
    # Metacharacters do not work in the drive part and shouldn't be escaped.
    drive, pathname = os.path.splitdrive(pathname)
    ikiwa isinstance(pathname, bytes):
        pathname = magic_check_bytes.sub(br'[\1]', pathname)
    else:
        pathname = magic_check.sub(r'[\1]', pathname)
    rudisha drive + pathname
