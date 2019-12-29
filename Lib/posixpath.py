"""Common operations on Posix pathnames.

Instead of agizaing this module directly, agiza os na refer to
this module kama os.path.  The "os.path" name ni an alias kila this
module on Posix systems; on other systems (e.g. Windows),
os.path provides the same operations kwenye a manner specific to that
platform, na ni an alias to another module (e.g. ntpath).

Some of this can actually be useful on non-Posix systems too, e.g.
kila manipulation of the pathname component of URLs.
"""

# Strings representing various path-related bits na pieces.
# These are primarily kila export; internally, they are hardcoded.
# Should be set before agizas kila resolving cyclic dependency.
curdir = '.'
pardir = '..'
extsep = '.'
sep = '/'
pathsep = ':'
defpath = '/bin:/usr/bin'
altsep = Tupu
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
    isipokua:
        rudisha '/'

# Normalize the case of a pathname.  Trivial kwenye Posix, string.lower on Mac.
# On MS-DOS this may also turn slashes into backslashes; however, other
# normalizations (such kama optimizing '../' away) are sio allowed
# (another function should be defined to do that).

eleza normcase(s):
    """Normalize case of pathname.  Has no effect under Posix"""
    rudisha os.fspath(s)


# Return whether a path ni absolute.
# Trivial kwenye Posix, harder on the Mac ama MS-DOS.

eleza isabs(s):
    """Test whether a path ni absolute"""
    s = os.fspath(s)
    sep = _get_sep(s)
    rudisha s.startswith(sep)


# Join pathnames.
# Ignore the previous parts ikiwa a part ni absolute.
# Insert a '/' unless the first part ni empty ama already ends kwenye '/'.

eleza join(a, *p):
    """Join two ama more pathname components, inserting '/' kama needed.
    If any component ni an absolute path, all previous path components
    will be discarded.  An empty last part will result kwenye a path that
    ends with a separator."""
    a = os.fspath(a)
    sep = _get_sep(a)
    path = a
    jaribu:
        ikiwa sio p:
            path[:0] + sep  #23780: Ensure compatible data type even ikiwa p ni null.
        kila b kwenye map(os.fspath, p):
            ikiwa b.startswith(sep):
                path = b
            elikiwa sio path ama path.endswith(sep):
                path += b
            isipokua:
                path += sep + b
    tatizo (TypeError, AttributeError, BytesWarning):
        genericpath._check_arg_types('join', a, *p)
        ashiria
    rudisha path


# Split a path kwenye head (everything up to the last '/') na tail (the
# rest).  If the path ends kwenye '/', tail will be empty.  If there ni no
# '/' kwenye the path, head  will be empty.
# Trailing '/'es are stripped kutoka head unless it ni the root.

eleza split(p):
    """Split a pathname.  Returns tuple "(head, tail)" where "tail" is
    everything after the final slash.  Either part may be empty."""
    p = os.fspath(p)
    sep = _get_sep(p)
    i = p.rfind(sep) + 1
    head, tail = p[:i], p[i:]
    ikiwa head na head != sep*len(head):
        head = head.rstrip(sep)
    rudisha head, tail


# Split a path kwenye root na extension.
# The extension ni everything starting at the last dot kwenye the last
# pathname component; the root ni everything before that.
# It ni always true that root + ext == p.

eleza splitext(p):
    p = os.fspath(p)
    ikiwa isinstance(p, bytes):
        sep = b'/'
        extsep = b'.'
    isipokua:
        sep = '/'
        extsep = '.'
    rudisha genericpath._splitext(p, sep, Tupu, extsep)
splitext.__doc__ = genericpath._splitext.__doc__

# Split a pathname into a drive specification na the rest of the
# path.  Useful on DOS/Windows/NT; on Unix, the drive ni always empty.

eleza splitdrive(p):
    """Split a pathname into drive na path. On Posix, drive ni always
    empty."""
    p = os.fspath(p)
    rudisha p[:0], p


# Return the tail (basename) part of a path, same kama split(path)[1].

eleza basename(p):
    """Returns the final component of a pathname"""
    p = os.fspath(p)
    sep = _get_sep(p)
    i = p.rfind(sep) + 1
    rudisha p[i:]


# Return the head (dirname) part of a path, same kama split(path)[0].

eleza dirname(p):
    """Returns the directory component of a pathname"""
    p = os.fspath(p)
    sep = _get_sep(p)
    i = p.rfind(sep) + 1
    head = p[:i]
    ikiwa head na head != sep*len(head):
        head = head.rstrip(sep)
    rudisha head


# Is a path a symbolic link?
# This will always rudisha false on systems where os.lstat doesn't exist.

eleza islink(path):
    """Test whether a path ni a symbolic link"""
    jaribu:
        st = os.lstat(path)
    tatizo (OSError, ValueError, AttributeError):
        rudisha Uongo
    rudisha stat.S_ISLNK(st.st_mode)

# Being true kila dangling symbolic links ni also useful.

eleza lexists(path):
    """Test whether a path exists.  Returns Kweli kila broken symbolic links"""
    jaribu:
        os.lstat(path)
    tatizo (OSError, ValueError):
        rudisha Uongo
    rudisha Kweli


# Is a path a mount point?
# (Does this work kila all UNIXes?  Is it even guaranteed to work by Posix?)

eleza ismount(path):
    """Test whether a path ni a mount point"""
    jaribu:
        s1 = os.lstat(path)
    tatizo (OSError, ValueError):
        # It doesn't exist -- so sio a mount point. :-)
        rudisha Uongo
    isipokua:
        # A symlink can never be a mount point
        ikiwa stat.S_ISLNK(s1.st_mode):
            rudisha Uongo

    ikiwa isinstance(path, bytes):
        parent = join(path, b'..')
    isipokua:
        parent = join(path, '..')
    parent = realpath(parent)
    jaribu:
        s2 = os.lstat(parent)
    tatizo (OSError, ValueError):
        rudisha Uongo

    dev1 = s1.st_dev
    dev2 = s2.st_dev
    ikiwa dev1 != dev2:
        rudisha Kweli     # path/.. on a different device kama path
    ino1 = s1.st_ino
    ino2 = s2.st_ino
    ikiwa ino1 == ino2:
        rudisha Kweli     # path/.. ni the same i-node kama path
    rudisha Uongo


# Expand paths beginning with '~' ama '~user'.
# '~' means $HOME; '~user' means that user's home directory.
# If the path doesn't begin with '~', ama ikiwa the user ama $HOME ni unknown,
# the path ni rudishaed unchanged (leaving error reporting to whatever
# function ni called with the expanded path kama argument).
# See also module 'glob' kila expansion of *, ? na [...] kwenye pathnames.
# (A function should also be defined to do full *sh-style environment
# variable expansion.)

eleza expanduser(path):
    """Expand ~ na ~user constructions.  If user ama $HOME ni unknown,
    do nothing."""
    path = os.fspath(path)
    ikiwa isinstance(path, bytes):
        tilde = b'~'
    isipokua:
        tilde = '~'
    ikiwa sio path.startswith(tilde):
        rudisha path
    sep = _get_sep(path)
    i = path.find(sep, 1)
    ikiwa i < 0:
        i = len(path)
    ikiwa i == 1:
        ikiwa 'HOME' haiko kwenye os.environ:
            agiza pwd
            jaribu:
                userhome = pwd.getpwuid(os.getuid()).pw_dir
            tatizo KeyError:
                # bpo-10496: ikiwa the current user identifier doesn't exist kwenye the
                # pitaword database, rudisha the path unchanged
                rudisha path
        isipokua:
            userhome = os.environ['HOME']
    isipokua:
        agiza pwd
        name = path[1:i]
        ikiwa isinstance(name, bytes):
            name = str(name, 'ASCII')
        jaribu:
            pwent = pwd.getpwnam(name)
        tatizo KeyError:
            # bpo-10496: ikiwa the user name kutoka the path doesn't exist kwenye the
            # pitaword database, rudisha the path unchanged
            rudisha path
        userhome = pwent.pw_dir
    ikiwa isinstance(path, bytes):
        userhome = os.fsencode(userhome)
        root = b'/'
    isipokua:
        root = '/'
    userhome = userhome.rstrip(root)
    rudisha (userhome + path[i:]) ama root


# Expand paths containing shell variable substitutions.
# This expands the forms $variable na ${variable} only.
# Non-existent variables are left unchanged.

_varprog = Tupu
_varprogb = Tupu

eleza expandvars(path):
    """Expand shell variables of form $var na ${var}.  Unknown variables
    are left unchanged."""
    path = os.fspath(path)
    global _varprog, _varprogb
    ikiwa isinstance(path, bytes):
        ikiwa b'$' haiko kwenye path:
            rudisha path
        ikiwa sio _varprogb:
            agiza re
            _varprogb = re.compile(br'\$(\w+|\{[^}]*\})', re.ASCII)
        search = _varprogb.search
        start = b'{'
        end = b'}'
        environ = getattr(os, 'environb', Tupu)
    isipokua:
        ikiwa '$' haiko kwenye path:
            rudisha path
        ikiwa sio _varprog:
            agiza re
            _varprog = re.compile(r'\$(\w+|\{[^}]*\})', re.ASCII)
        search = _varprog.search
        start = '{'
        end = '}'
        environ = os.environ
    i = 0
    wakati Kweli:
        m = search(path, i)
        ikiwa sio m:
            koma
        i, j = m.span(0)
        name = m.group(1)
        ikiwa name.startswith(start) na name.endswith(end):
            name = name[1:-1]
        jaribu:
            ikiwa environ ni Tupu:
                value = os.fsencode(os.environ[os.fsdecode(name)])
            isipokua:
                value = environ[name]
        tatizo KeyError:
            i = j
        isipokua:
            tail = path[j:]
            path = path[:i] + value
            i = len(path)
            path += tail
    rudisha path


# Normalize a path, e.g. A//B, A/./B na A/foo/../B all become A/B.
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
    isipokua:
        sep = '/'
        empty = ''
        dot = '.'
        dotdot = '..'
    ikiwa path == empty:
        rudisha dot
    initial_slashes = path.startswith(sep)
    # POSIX allows one ama two initial slashes, but treats three ama more
    # kama single slash.
    ikiwa (initial_slashes and
        path.startswith(sep*2) na sio path.startswith(sep*3)):
        initial_slashes = 2
    comps = path.split(sep)
    new_comps = []
    kila comp kwenye comps:
        ikiwa comp kwenye (empty, dot):
            endelea
        ikiwa (comp != dotdot ama (not initial_slashes na sio new_comps) or
             (new_comps na new_comps[-1] == dotdot)):
            new_comps.append(comp)
        elikiwa new_comps:
            new_comps.pop()
    comps = new_comps
    path = sep.join(comps)
    ikiwa initial_slashes:
        path = sep*initial_slashes + path
    rudisha path ama dot


eleza abspath(path):
    """Return an absolute path."""
    path = os.fspath(path)
    ikiwa sio isabs(path):
        ikiwa isinstance(path, bytes):
            cwd = os.getcwdb()
        isipokua:
            cwd = os.getcwd()
        path = join(cwd, path)
    rudisha normpath(path)


# Return a canonical path (i.e. the absolute location of a file on the
# filesystem).

eleza realpath(filename):
    """Return the canonical path of the specified filename, eliminating any
symbolic links encountered kwenye the path."""
    filename = os.fspath(filename)
    path, ok = _joinrealpath(filename[:0], filename, {})
    rudisha abspath(path)

# Join two paths, normalizing na eliminating any symbolic links
# encountered kwenye the second path.
eleza _joinrealpath(path, rest, seen):
    ikiwa isinstance(path, bytes):
        sep = b'/'
        curdir = b'.'
        pardir = b'..'
    isipokua:
        sep = '/'
        curdir = '.'
        pardir = '..'

    ikiwa isabs(rest):
        rest = rest[1:]
        path = sep

    wakati rest:
        name, _, rest = rest.partition(sep)
        ikiwa sio name ama name == curdir:
            # current dir
            endelea
        ikiwa name == pardir:
            # parent dir
            ikiwa path:
                path, name = split(path)
                ikiwa name == pardir:
                    path = join(path, pardir, pardir)
            isipokua:
                path = pardir
            endelea
        newpath = join(path, name)
        ikiwa sio islink(newpath):
            path = newpath
            endelea
        # Resolve the symbolic link
        ikiwa newpath kwenye seen:
            # Already seen this path
            path = seen[newpath]
            ikiwa path ni sio Tupu:
                # use cached value
                endelea
            # The symlink ni sio resolved, so we must have a symlink loop.
            # Return already resolved part + rest of the path unchanged.
            rudisha join(newpath, rest), Uongo
        seen[newpath] = Tupu # sio resolved symlink
        path, ok = _joinrealpath(path, os.readlink(newpath), seen)
        ikiwa sio ok:
            rudisha join(path, rest), Uongo
        seen[newpath] = path # resolved symlink

    rudisha path, Kweli


supports_unicode_filenames = (sys.platform == 'darwin')

eleza relpath(path, start=Tupu):
    """Return a relative version of a path"""

    ikiwa sio path:
        ashiria ValueError("no path specified")

    path = os.fspath(path)
    ikiwa isinstance(path, bytes):
        curdir = b'.'
        sep = b'/'
        pardir = b'..'
    isipokua:
        curdir = '.'
        sep = '/'
        pardir = '..'

    ikiwa start ni Tupu:
        start = curdir
    isipokua:
        start = os.fspath(start)

    jaribu:
        start_list = [x kila x kwenye abspath(start).split(sep) ikiwa x]
        path_list = [x kila x kwenye abspath(path).split(sep) ikiwa x]
        # Work out how much of the filepath ni shared by start na path.
        i = len(commonprefix([start_list, path_list]))

        rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
        ikiwa sio rel_list:
            rudisha curdir
        rudisha join(*rel_list)
    tatizo (TypeError, AttributeError, BytesWarning, DeprecationWarning):
        genericpath._check_arg_types('relpath', path, start)
        ashiria


# Return the longest common sub-path of the sequence of paths given kama input.
# The paths are sio normalized before comparing them (this ni the
# responsibility of the caller). Any trailing separator ni stripped kutoka the
# rudishaed path.

eleza commonpath(paths):
    """Given a sequence of path names, rudishas the longest common sub-path."""

    ikiwa sio paths:
        ashiria ValueError('commonpath() arg ni an empty sequence')

    paths = tuple(map(os.fspath, paths))
    ikiwa isinstance(paths[0], bytes):
        sep = b'/'
        curdir = b'.'
    isipokua:
        sep = '/'
        curdir = '.'

    jaribu:
        split_paths = [path.split(sep) kila path kwenye paths]

        jaribu:
            isabs, = set(p[:1] == sep kila p kwenye paths)
        tatizo ValueError:
            ashiria ValueError("Can't mix absolute na relative paths") kutoka Tupu

        split_paths = [[c kila c kwenye s ikiwa c na c != curdir] kila s kwenye split_paths]
        s1 = min(split_paths)
        s2 = max(split_paths)
        common = s1
        kila i, c kwenye enumerate(s1):
            ikiwa c != s2[i]:
                common = s1[:i]
                koma

        prefix = sep ikiwa isabs else sep[:0]
        rudisha prefix + sep.join(common)
    tatizo (TypeError, AttributeError):
        genericpath._check_arg_types('commonpath', *paths)
        ashiria
