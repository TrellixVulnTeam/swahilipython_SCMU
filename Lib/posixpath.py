"""Common operations on Posix pathnames.

Instead of agizaing this module directly, agiza os and refer to
this module as os.path.  The "os.path" name is an alias for this
module on Posix systems; on other systems (e.g. Windows),
os.path provides the same operations in a manner specific to that
platform, and is an alias to another module (e.g. ntpath).

Some of this can actually be useful on non-Posix systems too, e.g.
for manipulation of the pathname component of URLs.
"""

# Strings representing various path-related bits and pieces.
# These are primarily for export; internally, they are hardcoded.
# Should be set before agizas for resolving cyclic dependency.
curdir = '.'
pardir = '..'
extsep = '.'
sep = '/'
pathsep = ':'
defpath = '/bin:/usr/bin'
altsep = None
devnull = '/dev/null'

agiza os
agiza sys
agiza stat
agiza genericpath
kutoka genericpath agiza *

__all__ = ["normcase","isabs","join","splitdrive","split","splitext",
           "basename","dirname","commonprefix","getsize","getmtime",
           "getatime","getctime","islink","exists","lexists","isdir","isfile",
           "ismount", "expanduser","expandvars","normpath","abspath",
           "samefile","sameopenfile","samestat",
           "curdir","pardir","sep","pathsep","defpath","altsep","extsep",
           "devnull","realpath","supports_unicode_filenames","relpath",
           "commonpath"]


eleza _get_sep(path):
    ikiwa isinstance(path, bytes):
        rudisha b'/'
    else:
        rudisha '/'

# Normalize the case of a pathname.  Trivial in Posix, string.lower on Mac.
# On MS-DOS this may also turn slashes into backslashes; however, other
# normalizations (such as optimizing '../' away) are not allowed
# (another function should be defined to do that).

eleza normcase(s):
    """Normalize case of pathname.  Has no effect under Posix"""
    rudisha os.fspath(s)


# Return whether a path is absolute.
# Trivial in Posix, harder on the Mac or MS-DOS.

eleza isabs(s):
    """Test whether a path is absolute"""
    s = os.fspath(s)
    sep = _get_sep(s)
    rudisha s.startswith(sep)


# Join pathnames.
# Ignore the previous parts ikiwa a part is absolute.
# Insert a '/' unless the first part is empty or already ends in '/'.

eleza join(a, *p):
    """Join two or more pathname components, inserting '/' as needed.
    If any component is an absolute path, all previous path components
    will be discarded.  An empty last part will result in a path that
    ends with a separator."""
    a = os.fspath(a)
    sep = _get_sep(a)
    path = a
    try:
        ikiwa not p:
            path[:0] + sep  #23780: Ensure compatible data type even ikiwa p is null.
        for b in map(os.fspath, p):
            ikiwa b.startswith(sep):
                path = b
            elikiwa not path or path.endswith(sep):
                path += b
            else:
                path += sep + b
    except (TypeError, AttributeError, BytesWarning):
        genericpath._check_arg_types('join', a, *p)
        raise
    rudisha path


# Split a path in head (everything up to the last '/') and tail (the
# rest).  If the path ends in '/', tail will be empty.  If there is no
# '/' in the path, head  will be empty.
# Trailing '/'es are stripped kutoka head unless it is the root.

eleza split(p):
    """Split a pathname.  Returns tuple "(head, tail)" where "tail" is
    everything after the final slash.  Either part may be empty."""
    p = os.fspath(p)
    sep = _get_sep(p)
    i = p.rfind(sep) + 1
    head, tail = p[:i], p[i:]
    ikiwa head and head != sep*len(head):
        head = head.rstrip(sep)
    rudisha head, tail


# Split a path in root and extension.
# The extension is everything starting at the last dot in the last
# pathname component; the root is everything before that.
# It is always true that root + ext == p.

eleza splitext(p):
    p = os.fspath(p)
    ikiwa isinstance(p, bytes):
        sep = b'/'
        extsep = b'.'
    else:
        sep = '/'
        extsep = '.'
    rudisha genericpath._splitext(p, sep, None, extsep)
splitext.__doc__ = genericpath._splitext.__doc__

# Split a pathname into a drive specification and the rest of the
# path.  Useful on DOS/Windows/NT; on Unix, the drive is always empty.

eleza splitdrive(p):
    """Split a pathname into drive and path. On Posix, drive is always
    empty."""
    p = os.fspath(p)
    rudisha p[:0], p


# Return the tail (basename) part of a path, same as split(path)[1].

eleza basename(p):
    """Returns the final component of a pathname"""
    p = os.fspath(p)
    sep = _get_sep(p)
    i = p.rfind(sep) + 1
    rudisha p[i:]


# Return the head (dirname) part of a path, same as split(path)[0].

eleza dirname(p):
    """Returns the directory component of a pathname"""
    p = os.fspath(p)
    sep = _get_sep(p)
    i = p.rfind(sep) + 1
    head = p[:i]
    ikiwa head and head != sep*len(head):
        head = head.rstrip(sep)
    rudisha head


# Is a path a symbolic link?
# This will always rudisha false on systems where os.lstat doesn't exist.

eleza islink(path):
    """Test whether a path is a symbolic link"""
    try:
        st = os.lstat(path)
    except (OSError, ValueError, AttributeError):
        rudisha False
    rudisha stat.S_ISLNK(st.st_mode)

# Being true for dangling symbolic links is also useful.

eleza lexists(path):
    """Test whether a path exists.  Returns True for broken symbolic links"""
    try:
        os.lstat(path)
    except (OSError, ValueError):
        rudisha False
    rudisha True


# Is a path a mount point?
# (Does this work for all UNIXes?  Is it even guaranteed to work by Posix?)

eleza ismount(path):
    """Test whether a path is a mount point"""
    try:
        s1 = os.lstat(path)
    except (OSError, ValueError):
        # It doesn't exist -- so not a mount point. :-)
        rudisha False
    else:
        # A symlink can never be a mount point
        ikiwa stat.S_ISLNK(s1.st_mode):
            rudisha False

    ikiwa isinstance(path, bytes):
        parent = join(path, b'..')
    else:
        parent = join(path, '..')
    parent = realpath(parent)
    try:
        s2 = os.lstat(parent)
    except (OSError, ValueError):
        rudisha False

    dev1 = s1.st_dev
    dev2 = s2.st_dev
    ikiwa dev1 != dev2:
        rudisha True     # path/.. on a different device as path
    ino1 = s1.st_ino
    ino2 = s2.st_ino
    ikiwa ino1 == ino2:
        rudisha True     # path/.. is the same i-node as path
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
    """Expand ~ and ~user constructions.  If user or $HOME is unknown,
    do nothing."""
    path = os.fspath(path)
    ikiwa isinstance(path, bytes):
        tilde = b'~'
    else:
        tilde = '~'
    ikiwa not path.startswith(tilde):
        rudisha path
    sep = _get_sep(path)
    i = path.find(sep, 1)
    ikiwa i < 0:
        i = len(path)
    ikiwa i == 1:
        ikiwa 'HOME' not in os.environ:
            agiza pwd
            try:
                userhome = pwd.getpwuid(os.getuid()).pw_dir
            except KeyError:
                # bpo-10496: ikiwa the current user identifier doesn't exist in the
                # password database, rudisha the path unchanged
                rudisha path
        else:
            userhome = os.environ['HOME']
    else:
        agiza pwd
        name = path[1:i]
        ikiwa isinstance(name, bytes):
            name = str(name, 'ASCII')
        try:
            pwent = pwd.getpwnam(name)
        except KeyError:
            # bpo-10496: ikiwa the user name kutoka the path doesn't exist in the
            # password database, rudisha the path unchanged
            rudisha path
        userhome = pwent.pw_dir
    ikiwa isinstance(path, bytes):
        userhome = os.fsencode(userhome)
        root = b'/'
    else:
        root = '/'
    userhome = userhome.rstrip(root)
    rudisha (userhome + path[i:]) or root


# Expand paths containing shell variable substitutions.
# This expands the forms $variable and ${variable} only.
# Non-existent variables are left unchanged.

_varprog = None
_varprogb = None

eleza expandvars(path):
    """Expand shell variables of form $var and ${var}.  Unknown variables
    are left unchanged."""
    path = os.fspath(path)
    global _varprog, _varprogb
    ikiwa isinstance(path, bytes):
        ikiwa b'$' not in path:
            rudisha path
        ikiwa not _varprogb:
            agiza re
            _varprogb = re.compile(br'\$(\w+|\{[^}]*\})', re.ASCII)
        search = _varprogb.search
        start = b'{'
        end = b'}'
        environ = getattr(os, 'environb', None)
    else:
        ikiwa '$' not in path:
            rudisha path
        ikiwa not _varprog:
            agiza re
            _varprog = re.compile(r'\$(\w+|\{[^}]*\})', re.ASCII)
        search = _varprog.search
        start = '{'
        end = '}'
        environ = os.environ
    i = 0
    while True:
        m = search(path, i)
        ikiwa not m:
            break
        i, j = m.span(0)
        name = m.group(1)
        ikiwa name.startswith(start) and name.endswith(end):
            name = name[1:-1]
        try:
            ikiwa environ is None:
                value = os.fsencode(os.environ[os.fsdecode(name)])
            else:
                value = environ[name]
        except KeyError:
            i = j
        else:
            tail = path[j:]
            path = path[:i] + value
            i = len(path)
            path += tail
    rudisha path


# Normalize a path, e.g. A//B, A/./B and A/foo/../B all become A/B.
# It should be understood that this may change the meaning of the path
# ikiwa it contains symbolic links!

eleza normpath(path):
    """Normalize path, eliminating double slashes, etc."""
    path = os.fspath(path)
    ikiwa isinstance(path, bytes):
        sep = b'/'
        empty = b''
        dot = b'.'
        dotdot = b'..'
    else:
        sep = '/'
        empty = ''
        dot = '.'
        dotdot = '..'
    ikiwa path == empty:
        rudisha dot
    initial_slashes = path.startswith(sep)
    # POSIX allows one or two initial slashes, but treats three or more
    # as single slash.
    ikiwa (initial_slashes and
        path.startswith(sep*2) and not path.startswith(sep*3)):
        initial_slashes = 2
    comps = path.split(sep)
    new_comps = []
    for comp in comps:
        ikiwa comp in (empty, dot):
            continue
        ikiwa (comp != dotdot or (not initial_slashes and not new_comps) or
             (new_comps and new_comps[-1] == dotdot)):
            new_comps.append(comp)
        elikiwa new_comps:
            new_comps.pop()
    comps = new_comps
    path = sep.join(comps)
    ikiwa initial_slashes:
        path = sep*initial_slashes + path
    rudisha path or dot


eleza abspath(path):
    """Return an absolute path."""
    path = os.fspath(path)
    ikiwa not isabs(path):
        ikiwa isinstance(path, bytes):
            cwd = os.getcwdb()
        else:
            cwd = os.getcwd()
        path = join(cwd, path)
    rudisha normpath(path)


# Return a canonical path (i.e. the absolute location of a file on the
# filesystem).

eleza realpath(filename):
    """Return the canonical path of the specified filename, eliminating any
symbolic links encountered in the path."""
    filename = os.fspath(filename)
    path, ok = _joinrealpath(filename[:0], filename, {})
    rudisha abspath(path)

# Join two paths, normalizing and eliminating any symbolic links
# encountered in the second path.
eleza _joinrealpath(path, rest, seen):
    ikiwa isinstance(path, bytes):
        sep = b'/'
        curdir = b'.'
        pardir = b'..'
    else:
        sep = '/'
        curdir = '.'
        pardir = '..'

    ikiwa isabs(rest):
        rest = rest[1:]
        path = sep

    while rest:
        name, _, rest = rest.partition(sep)
        ikiwa not name or name == curdir:
            # current dir
            continue
        ikiwa name == pardir:
            # parent dir
            ikiwa path:
                path, name = split(path)
                ikiwa name == pardir:
                    path = join(path, pardir, pardir)
            else:
                path = pardir
            continue
        newpath = join(path, name)
        ikiwa not islink(newpath):
            path = newpath
            continue
        # Resolve the symbolic link
        ikiwa newpath in seen:
            # Already seen this path
            path = seen[newpath]
            ikiwa path is not None:
                # use cached value
                continue
            # The symlink is not resolved, so we must have a symlink loop.
            # Return already resolved part + rest of the path unchanged.
            rudisha join(newpath, rest), False
        seen[newpath] = None # not resolved symlink
        path, ok = _joinrealpath(path, os.readlink(newpath), seen)
        ikiwa not ok:
            rudisha join(path, rest), False
        seen[newpath] = path # resolved symlink

    rudisha path, True


supports_unicode_filenames = (sys.platform == 'darwin')

eleza relpath(path, start=None):
    """Return a relative version of a path"""

    ikiwa not path:
        raise ValueError("no path specified")

    path = os.fspath(path)
    ikiwa isinstance(path, bytes):
        curdir = b'.'
        sep = b'/'
        pardir = b'..'
    else:
        curdir = '.'
        sep = '/'
        pardir = '..'

    ikiwa start is None:
        start = curdir
    else:
        start = os.fspath(start)

    try:
        start_list = [x for x in abspath(start).split(sep) ikiwa x]
        path_list = [x for x in abspath(path).split(sep) ikiwa x]
        # Work out how much of the filepath is shared by start and path.
        i = len(commonprefix([start_list, path_list]))

        rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
        ikiwa not rel_list:
            rudisha curdir
        rudisha join(*rel_list)
    except (TypeError, AttributeError, BytesWarning, DeprecationWarning):
        genericpath._check_arg_types('relpath', path, start)
        raise


# Return the longest common sub-path of the sequence of paths given as input.
# The paths are not normalized before comparing them (this is the
# responsibility of the caller). Any trailing separator is stripped kutoka the
# returned path.

eleza commonpath(paths):
    """Given a sequence of path names, returns the longest common sub-path."""

    ikiwa not paths:
        raise ValueError('commonpath() arg is an empty sequence')

    paths = tuple(map(os.fspath, paths))
    ikiwa isinstance(paths[0], bytes):
        sep = b'/'
        curdir = b'.'
    else:
        sep = '/'
        curdir = '.'

    try:
        split_paths = [path.split(sep) for path in paths]

        try:
            isabs, = set(p[:1] == sep for p in paths)
        except ValueError:
            raise ValueError("Can't mix absolute and relative paths") kutoka None

        split_paths = [[c for c in s ikiwa c and c != curdir] for s in split_paths]
        s1 = min(split_paths)
        s2 = max(split_paths)
        common = s1
        for i, c in enumerate(s1):
            ikiwa c != s2[i]:
                common = s1[:i]
                break

        prefix = sep ikiwa isabs else sep[:0]
        rudisha prefix + sep.join(common)
    except (TypeError, AttributeError):
        genericpath._check_arg_types('commonpath', *paths)
        raise
