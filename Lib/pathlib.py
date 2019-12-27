agiza fnmatch
agiza functools
agiza io
agiza ntpath
agiza os
agiza posixpath
agiza re
agiza sys
kutoka _collections_abc agiza Sequence
kutoka errno agiza EINVAL, ENOENT, ENOTDIR, EBADF, ELOOP
kutoka operator agiza attrgetter
kutoka stat agiza S_ISDIR, S_ISLNK, S_ISREG, S_ISSOCK, S_ISBLK, S_ISCHR, S_ISFIFO
kutoka urllib.parse agiza quote_kutoka_bytes as urlquote_kutoka_bytes


supports_symlinks = True
ikiwa os.name == 'nt':
    agiza nt
    ikiwa sys.getwindowsversion()[:2] >= (6, 0):
        kutoka nt agiza _getfinalpathname
    else:
        supports_symlinks = False
        _getfinalpathname = None
else:
    nt = None


__all__ = [
    "PurePath", "PurePosixPath", "PureWindowsPath",
    "Path", "PosixPath", "WindowsPath",
    ]

#
# Internals
#

# EBADF - guard against macOS `stat` throwing EBADF
_IGNORED_ERROS = (ENOENT, ENOTDIR, EBADF, ELOOP)

_IGNORED_WINERRORS = (
    21,  # ERROR_NOT_READY - drive exists but is not accessible
    1921,  # ERROR_CANT_RESOLVE_FILENAME - fix for broken symlink pointing to itself
)

eleza _ignore_error(exception):
    rudisha (getattr(exception, 'errno', None) in _IGNORED_ERROS or
            getattr(exception, 'winerror', None) in _IGNORED_WINERRORS)


eleza _is_wildcard_pattern(pat):
    # Whether this pattern needs actual matching using fnmatch, or can
    # be looked up directly as a file.
    rudisha "*" in pat or "?" in pat or "[" in pat


kundi _Flavour(object):
    """A flavour implements a particular (platform-specific) set of path
    semantics."""

    eleza __init__(self):
        self.join = self.sep.join

    eleza parse_parts(self, parts):
        parsed = []
        sep = self.sep
        altsep = self.altsep
        drv = root = ''
        it = reversed(parts)
        for part in it:
            ikiwa not part:
                continue
            ikiwa altsep:
                part = part.replace(altsep, sep)
            drv, root, rel = self.splitroot(part)
            ikiwa sep in rel:
                for x in reversed(rel.split(sep)):
                    ikiwa x and x != '.':
                        parsed.append(sys.intern(x))
            else:
                ikiwa rel and rel != '.':
                    parsed.append(sys.intern(rel))
            ikiwa drv or root:
                ikiwa not drv:
                    # If no drive is present, try to find one in the previous
                    # parts. This makes the result of parsing e.g.
                    # ("C:", "/", "a") reasonably intuitive.
                    for part in it:
                        ikiwa not part:
                            continue
                        ikiwa altsep:
                            part = part.replace(altsep, sep)
                        drv = self.splitroot(part)[0]
                        ikiwa drv:
                            break
                break
        ikiwa drv or root:
            parsed.append(drv + root)
        parsed.reverse()
        rudisha drv, root, parsed

    eleza join_parsed_parts(self, drv, root, parts, drv2, root2, parts2):
        """
        Join the two paths represented by the respective
        (drive, root, parts) tuples.  Return a new (drive, root, parts) tuple.
        """
        ikiwa root2:
            ikiwa not drv2 and drv:
                rudisha drv, root2, [drv + root2] + parts2[1:]
        elikiwa drv2:
            ikiwa drv2 == drv or self.casefold(drv2) == self.casefold(drv):
                # Same drive => second path is relative to the first
                rudisha drv, root, parts + parts2[1:]
        else:
            # Second path is non-anchored (common case)
            rudisha drv, root, parts + parts2
        rudisha drv2, root2, parts2


kundi _WindowsFlavour(_Flavour):
    # Reference for Windows paths can be found at
    # http://msdn.microsoft.com/en-us/library/aa365247%28v=vs.85%29.aspx

    sep = '\\'
    altsep = '/'
    has_drv = True
    pathmod = ntpath

    is_supported = (os.name == 'nt')

    drive_letters = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    ext_namespace_prefix = '\\\\?\\'

    reserved_names = (
        {'CON', 'PRN', 'AUX', 'NUL'} |
        {'COM%d' % i for i in range(1, 10)} |
        {'LPT%d' % i for i in range(1, 10)}
        )

    # Interesting findings about extended paths:
    # - '\\?\c:\a', '//?/c:\a' and '//?/c:/a' are all supported
    #   but '\\?\c:/a' is not
    # - extended paths are always absolute; "relative" extended paths will
    #   fail.

    eleza splitroot(self, part, sep=sep):
        first = part[0:1]
        second = part[1:2]
        ikiwa (second == sep and first == sep):
            # XXX extended paths should also disable the collapsing of "."
            # components (according to MSDN docs).
            prefix, part = self._split_extended_path(part)
            first = part[0:1]
            second = part[1:2]
        else:
            prefix = ''
        third = part[2:3]
        ikiwa (second == sep and first == sep and third != sep):
            # is a UNC path:
            # vvvvvvvvvvvvvvvvvvvvv root
            # \\machine\mountpoint\directory\etc\...
            #            directory ^^^^^^^^^^^^^^
            index = part.find(sep, 2)
            ikiwa index != -1:
                index2 = part.find(sep, index + 1)
                # a UNC path can't have two slashes in a row
                # (after the initial two)
                ikiwa index2 != index + 1:
                    ikiwa index2 == -1:
                        index2 = len(part)
                    ikiwa prefix:
                        rudisha prefix + part[1:index2], sep, part[index2+1:]
                    else:
                        rudisha part[:index2], sep, part[index2+1:]
        drv = root = ''
        ikiwa second == ':' and first in self.drive_letters:
            drv = part[:2]
            part = part[2:]
            first = third
        ikiwa first == sep:
            root = first
            part = part.lstrip(sep)
        rudisha prefix + drv, root, part

    eleza casefold(self, s):
        rudisha s.lower()

    eleza casefold_parts(self, parts):
        rudisha [p.lower() for p in parts]

    eleza resolve(self, path, strict=False):
        s = str(path)
        ikiwa not s:
            rudisha os.getcwd()
        previous_s = None
        ikiwa _getfinalpathname is not None:
            ikiwa strict:
                rudisha self._ext_to_normal(_getfinalpathname(s))
            else:
                tail_parts = []  # End of the path after the first one not found
                while True:
                    try:
                        s = self._ext_to_normal(_getfinalpathname(s))
                    except FileNotFoundError:
                        previous_s = s
                        s, tail = os.path.split(s)
                        tail_parts.append(tail)
                        ikiwa previous_s == s:
                            rudisha path
                    else:
                        rudisha os.path.join(s, *reversed(tail_parts))
        # Means fallback on absolute
        rudisha None

    eleza _split_extended_path(self, s, ext_prefix=ext_namespace_prefix):
        prefix = ''
        ikiwa s.startswith(ext_prefix):
            prefix = s[:4]
            s = s[4:]
            ikiwa s.startswith('UNC\\'):
                prefix += s[:3]
                s = '\\' + s[3:]
        rudisha prefix, s

    eleza _ext_to_normal(self, s):
        # Turn back an extended path into a normal DOS-like path
        rudisha self._split_extended_path(s)[1]

    eleza is_reserved(self, parts):
        # NOTE: the rules for reserved names seem somewhat complicated
        # (e.g. r"..\NUL" is reserved but not r"foo\NUL").
        # We err on the side of caution and rudisha True for paths which are
        # not considered reserved by Windows.
        ikiwa not parts:
            rudisha False
        ikiwa parts[0].startswith('\\\\'):
            # UNC paths are never reserved
            rudisha False
        rudisha parts[-1].partition('.')[0].upper() in self.reserved_names

    eleza make_uri(self, path):
        # Under Windows, file URIs use the UTF-8 encoding.
        drive = path.drive
        ikiwa len(drive) == 2 and drive[1] == ':':
            # It's a path on a local drive => 'file:///c:/a/b'
            rest = path.as_posix()[2:].lstrip('/')
            rudisha 'file:///%s/%s' % (
                drive, urlquote_kutoka_bytes(rest.encode('utf-8')))
        else:
            # It's a path on a network drive => 'file://host/share/a/b'
            rudisha 'file:' + urlquote_kutoka_bytes(path.as_posix().encode('utf-8'))

    eleza gethomedir(self, username):
        ikiwa 'HOME' in os.environ:
            userhome = os.environ['HOME']
        elikiwa 'USERPROFILE' in os.environ:
            userhome = os.environ['USERPROFILE']
        elikiwa 'HOMEPATH' in os.environ:
            try:
                drv = os.environ['HOMEDRIVE']
            except KeyError:
                drv = ''
            userhome = drv + os.environ['HOMEPATH']
        else:
            raise RuntimeError("Can't determine home directory")

        ikiwa username:
            # Try to guess user home directory.  By default all users
            # directories are located in the same place and are named by
            # corresponding usernames.  If current user home directory points
            # to nonstandard place, this guess is likely wrong.
            ikiwa os.environ['USERNAME'] != username:
                drv, root, parts = self.parse_parts((userhome,))
                ikiwa parts[-1] != os.environ['USERNAME']:
                    raise RuntimeError("Can't determine home directory "
                                       "for %r" % username)
                parts[-1] = username
                ikiwa drv or root:
                    userhome = drv + root + self.join(parts[1:])
                else:
                    userhome = self.join(parts)
        rudisha userhome

kundi _PosixFlavour(_Flavour):
    sep = '/'
    altsep = ''
    has_drv = False
    pathmod = posixpath

    is_supported = (os.name != 'nt')

    eleza splitroot(self, part, sep=sep):
        ikiwa part and part[0] == sep:
            stripped_part = part.lstrip(sep)
            # According to POSIX path resolution:
            # http://pubs.opengroup.org/onlinepubs/009695399/basedefs/xbd_chap04.html#tag_04_11
            # "A pathname that begins with two successive slashes may be
            # interpreted in an implementation-defined manner, although more
            # than two leading slashes shall be treated as a single slash".
            ikiwa len(part) - len(stripped_part) == 2:
                rudisha '', sep * 2, stripped_part
            else:
                rudisha '', sep, stripped_part
        else:
            rudisha '', '', part

    eleza casefold(self, s):
        rudisha s

    eleza casefold_parts(self, parts):
        rudisha parts

    eleza resolve(self, path, strict=False):
        sep = self.sep
        accessor = path._accessor
        seen = {}
        eleza _resolve(path, rest):
            ikiwa rest.startswith(sep):
                path = ''

            for name in rest.split(sep):
                ikiwa not name or name == '.':
                    # current dir
                    continue
                ikiwa name == '..':
                    # parent dir
                    path, _, _ = path.rpartition(sep)
                    continue
                newpath = path + sep + name
                ikiwa newpath in seen:
                    # Already seen this path
                    path = seen[newpath]
                    ikiwa path is not None:
                        # use cached value
                        continue
                    # The symlink is not resolved, so we must have a symlink loop.
                    raise RuntimeError("Symlink loop kutoka %r" % newpath)
                # Resolve the symbolic link
                try:
                    target = accessor.readlink(newpath)
                except OSError as e:
                    ikiwa e.errno != EINVAL and strict:
                        raise
                    # Not a symlink, or non-strict mode. We just leave the path
                    # untouched.
                    path = newpath
                else:
                    seen[newpath] = None # not resolved symlink
                    path = _resolve(path, target)
                    seen[newpath] = path # resolved symlink

            rudisha path
        # NOTE: according to POSIX, getcwd() cannot contain path components
        # which are symlinks.
        base = '' ikiwa path.is_absolute() else os.getcwd()
        rudisha _resolve(base, str(path)) or sep

    eleza is_reserved(self, parts):
        rudisha False

    eleza make_uri(self, path):
        # We represent the path using the local filesystem encoding,
        # for portability to other applications.
        bpath = bytes(path)
        rudisha 'file://' + urlquote_kutoka_bytes(bpath)

    eleza gethomedir(self, username):
        ikiwa not username:
            try:
                rudisha os.environ['HOME']
            except KeyError:
                agiza pwd
                rudisha pwd.getpwuid(os.getuid()).pw_dir
        else:
            agiza pwd
            try:
                rudisha pwd.getpwnam(username).pw_dir
            except KeyError:
                raise RuntimeError("Can't determine home directory "
                                   "for %r" % username)


_windows_flavour = _WindowsFlavour()
_posix_flavour = _PosixFlavour()


kundi _Accessor:
    """An accessor implements a particular (system-specific or not) way of
    accessing paths on the filesystem."""


kundi _NormalAccessor(_Accessor):

    stat = os.stat

    lstat = os.lstat

    open = os.open

    listdir = os.listdir

    scandir = os.scandir

    chmod = os.chmod

    ikiwa hasattr(os, "lchmod"):
        lchmod = os.lchmod
    else:
        eleza lchmod(self, pathobj, mode):
            raise NotImplementedError("lchmod() not available on this system")

    mkdir = os.mkdir

    unlink = os.unlink

    link_to = os.link

    rmdir = os.rmdir

    rename = os.rename

    replace = os.replace

    ikiwa nt:
        ikiwa supports_symlinks:
            symlink = os.symlink
        else:
            eleza symlink(a, b, target_is_directory):
                raise NotImplementedError("symlink() not available on this system")
    else:
        # Under POSIX, os.symlink() takes two args
        @staticmethod
        eleza symlink(a, b, target_is_directory):
            rudisha os.symlink(a, b)

    utime = os.utime

    # Helper for resolve()
    eleza readlink(self, path):
        rudisha os.readlink(path)


_normal_accessor = _NormalAccessor()


#
# Globbing helpers
#

eleza _make_selector(pattern_parts):
    pat = pattern_parts[0]
    child_parts = pattern_parts[1:]
    ikiwa pat == '**':
        cls = _RecursiveWildcardSelector
    elikiwa '**' in pat:
        raise ValueError("Invalid pattern: '**' can only be an entire path component")
    elikiwa _is_wildcard_pattern(pat):
        cls = _WildcardSelector
    else:
        cls = _PreciseSelector
    rudisha cls(pat, child_parts)

ikiwa hasattr(functools, "lru_cache"):
    _make_selector = functools.lru_cache()(_make_selector)


kundi _Selector:
    """A selector matches a specific glob pattern part against the children
    of a given path."""

    eleza __init__(self, child_parts):
        self.child_parts = child_parts
        ikiwa child_parts:
            self.successor = _make_selector(child_parts)
            self.dironly = True
        else:
            self.successor = _TerminatingSelector()
            self.dironly = False

    eleza select_kutoka(self, parent_path):
        """Iterate over all child paths of `parent_path` matched by this
        selector.  This can contain parent_path itself."""
        path_cls = type(parent_path)
        is_dir = path_cls.is_dir
        exists = path_cls.exists
        scandir = parent_path._accessor.scandir
        ikiwa not is_dir(parent_path):
            rudisha iter([])
        rudisha self._select_kutoka(parent_path, is_dir, exists, scandir)


kundi _TerminatingSelector:

    eleza _select_kutoka(self, parent_path, is_dir, exists, scandir):
        yield parent_path


kundi _PreciseSelector(_Selector):

    eleza __init__(self, name, child_parts):
        self.name = name
        _Selector.__init__(self, child_parts)

    eleza _select_kutoka(self, parent_path, is_dir, exists, scandir):
        try:
            path = parent_path._make_child_relpath(self.name)
            ikiwa (is_dir ikiwa self.dironly else exists)(path):
                for p in self.successor._select_kutoka(path, is_dir, exists, scandir):
                    yield p
        except PermissionError:
            return


kundi _WildcardSelector(_Selector):

    eleza __init__(self, pat, child_parts):
        self.pat = re.compile(fnmatch.translate(pat))
        _Selector.__init__(self, child_parts)

    eleza _select_kutoka(self, parent_path, is_dir, exists, scandir):
        try:
            cf = parent_path._flavour.casefold
            entries = list(scandir(parent_path))
            for entry in entries:
                entry_is_dir = False
                try:
                    entry_is_dir = entry.is_dir()
                except OSError as e:
                    ikiwa not _ignore_error(e):
                        raise
                ikiwa not self.dironly or entry_is_dir:
                    name = entry.name
                    casefolded = cf(name)
                    ikiwa self.pat.match(casefolded):
                        path = parent_path._make_child_relpath(name)
                        for p in self.successor._select_kutoka(path, is_dir, exists, scandir):
                            yield p
        except PermissionError:
            return



kundi _RecursiveWildcardSelector(_Selector):

    eleza __init__(self, pat, child_parts):
        _Selector.__init__(self, child_parts)

    eleza _iterate_directories(self, parent_path, is_dir, scandir):
        yield parent_path
        try:
            entries = list(scandir(parent_path))
            for entry in entries:
                entry_is_dir = False
                try:
                    entry_is_dir = entry.is_dir()
                except OSError as e:
                    ikiwa not _ignore_error(e):
                        raise
                ikiwa entry_is_dir and not entry.is_symlink():
                    path = parent_path._make_child_relpath(entry.name)
                    for p in self._iterate_directories(path, is_dir, scandir):
                        yield p
        except PermissionError:
            return

    eleza _select_kutoka(self, parent_path, is_dir, exists, scandir):
        try:
            yielded = set()
            try:
                successor_select = self.successor._select_kutoka
                for starting_point in self._iterate_directories(parent_path, is_dir, scandir):
                    for p in successor_select(starting_point, is_dir, exists, scandir):
                        ikiwa p not in yielded:
                            yield p
                            yielded.add(p)
            finally:
                yielded.clear()
        except PermissionError:
            return


#
# Public API
#

kundi _PathParents(Sequence):
    """This object provides sequence-like access to the logical ancestors
    of a path.  Don't try to construct it yourself."""
    __slots__ = ('_pathcls', '_drv', '_root', '_parts')

    eleza __init__(self, path):
        # We don't store the instance to avoid reference cycles
        self._pathcls = type(path)
        self._drv = path._drv
        self._root = path._root
        self._parts = path._parts

    eleza __len__(self):
        ikiwa self._drv or self._root:
            rudisha len(self._parts) - 1
        else:
            rudisha len(self._parts)

    eleza __getitem__(self, idx):
        ikiwa idx < 0 or idx >= len(self):
            raise IndexError(idx)
        rudisha self._pathcls._kutoka_parsed_parts(self._drv, self._root,
                                                self._parts[:-idx - 1])

    eleza __repr__(self):
        rudisha "<{}.parents>".format(self._pathcls.__name__)


kundi PurePath(object):
    """Base kundi for manipulating paths without I/O.

    PurePath represents a filesystem path and offers operations which
    don't imply any actual filesystem I/O.  Depending on your system,
    instantiating a PurePath will rudisha either a PurePosixPath or a
    PureWindowsPath object.  You can also instantiate either of these classes
    directly, regardless of your system.
    """
    __slots__ = (
        '_drv', '_root', '_parts',
        '_str', '_hash', '_pparts', '_cached_cparts',
    )

    eleza __new__(cls, *args):
        """Construct a PurePath kutoka one or several strings and or existing
        PurePath objects.  The strings and path objects are combined so as
        to yield a canonicalized path, which is incorporated into the
        new PurePath object.
        """
        ikiwa cls is PurePath:
            cls = PureWindowsPath ikiwa os.name == 'nt' else PurePosixPath
        rudisha cls._kutoka_parts(args)

    eleza __reduce__(self):
        # Using the parts tuple helps share interned path parts
        # when pickling related paths.
        rudisha (self.__class__, tuple(self._parts))

    @classmethod
    eleza _parse_args(cls, args):
        # This is useful when you don't want to create an instance, just
        # canonicalize some constructor arguments.
        parts = []
        for a in args:
            ikiwa isinstance(a, PurePath):
                parts += a._parts
            else:
                a = os.fspath(a)
                ikiwa isinstance(a, str):
                    # Force-cast str subclasses to str (issue #21127)
                    parts.append(str(a))
                else:
                    raise TypeError(
                        "argument should be a str object or an os.PathLike "
                        "object returning str, not %r"
                        % type(a))
        rudisha cls._flavour.parse_parts(parts)

    @classmethod
    eleza _kutoka_parts(cls, args, init=True):
        # We need to call _parse_args on the instance, so as to get the
        # right flavour.
        self = object.__new__(cls)
        drv, root, parts = self._parse_args(args)
        self._drv = drv
        self._root = root
        self._parts = parts
        ikiwa init:
            self._init()
        rudisha self

    @classmethod
    eleza _kutoka_parsed_parts(cls, drv, root, parts, init=True):
        self = object.__new__(cls)
        self._drv = drv
        self._root = root
        self._parts = parts
        ikiwa init:
            self._init()
        rudisha self

    @classmethod
    eleza _format_parsed_parts(cls, drv, root, parts):
        ikiwa drv or root:
            rudisha drv + root + cls._flavour.join(parts[1:])
        else:
            rudisha cls._flavour.join(parts)

    eleza _init(self):
        # Overridden in concrete Path
        pass

    eleza _make_child(self, args):
        drv, root, parts = self._parse_args(args)
        drv, root, parts = self._flavour.join_parsed_parts(
            self._drv, self._root, self._parts, drv, root, parts)
        rudisha self._kutoka_parsed_parts(drv, root, parts)

    eleza __str__(self):
        """Return the string representation of the path, suitable for
        passing to system calls."""
        try:
            rudisha self._str
        except AttributeError:
            self._str = self._format_parsed_parts(self._drv, self._root,
                                                  self._parts) or '.'
            rudisha self._str

    eleza __fspath__(self):
        rudisha str(self)

    eleza as_posix(self):
        """Return the string representation of the path with forward (/)
        slashes."""
        f = self._flavour
        rudisha str(self).replace(f.sep, '/')

    eleza __bytes__(self):
        """Return the bytes representation of the path.  This is only
        recommended to use under Unix."""
        rudisha os.fsencode(self)

    eleza __repr__(self):
        rudisha "{}({!r})".format(self.__class__.__name__, self.as_posix())

    eleza as_uri(self):
        """Return the path as a 'file' URI."""
        ikiwa not self.is_absolute():
            raise ValueError("relative path can't be expressed as a file URI")
        rudisha self._flavour.make_uri(self)

    @property
    eleza _cparts(self):
        # Cached casefolded parts, for hashing and comparison
        try:
            rudisha self._cached_cparts
        except AttributeError:
            self._cached_cparts = self._flavour.casefold_parts(self._parts)
            rudisha self._cached_cparts

    eleza __eq__(self, other):
        ikiwa not isinstance(other, PurePath):
            rudisha NotImplemented
        rudisha self._cparts == other._cparts and self._flavour is other._flavour

    eleza __hash__(self):
        try:
            rudisha self._hash
        except AttributeError:
            self._hash = hash(tuple(self._cparts))
            rudisha self._hash

    eleza __lt__(self, other):
        ikiwa not isinstance(other, PurePath) or self._flavour is not other._flavour:
            rudisha NotImplemented
        rudisha self._cparts < other._cparts

    eleza __le__(self, other):
        ikiwa not isinstance(other, PurePath) or self._flavour is not other._flavour:
            rudisha NotImplemented
        rudisha self._cparts <= other._cparts

    eleza __gt__(self, other):
        ikiwa not isinstance(other, PurePath) or self._flavour is not other._flavour:
            rudisha NotImplemented
        rudisha self._cparts > other._cparts

    eleza __ge__(self, other):
        ikiwa not isinstance(other, PurePath) or self._flavour is not other._flavour:
            rudisha NotImplemented
        rudisha self._cparts >= other._cparts

    drive = property(attrgetter('_drv'),
                     doc="""The drive prefix (letter or UNC path), ikiwa any.""")

    root = property(attrgetter('_root'),
                    doc="""The root of the path, ikiwa any.""")

    @property
    eleza anchor(self):
        """The concatenation of the drive and root, or ''."""
        anchor = self._drv + self._root
        rudisha anchor

    @property
    eleza name(self):
        """The final path component, ikiwa any."""
        parts = self._parts
        ikiwa len(parts) == (1 ikiwa (self._drv or self._root) else 0):
            rudisha ''
        rudisha parts[-1]

    @property
    eleza suffix(self):
        """The final component's last suffix, ikiwa any."""
        name = self.name
        i = name.rfind('.')
        ikiwa 0 < i < len(name) - 1:
            rudisha name[i:]
        else:
            rudisha ''

    @property
    eleza suffixes(self):
        """A list of the final component's suffixes, ikiwa any."""
        name = self.name
        ikiwa name.endswith('.'):
            rudisha []
        name = name.lstrip('.')
        rudisha ['.' + suffix for suffix in name.split('.')[1:]]

    @property
    eleza stem(self):
        """The final path component, minus its last suffix."""
        name = self.name
        i = name.rfind('.')
        ikiwa 0 < i < len(name) - 1:
            rudisha name[:i]
        else:
            rudisha name

    eleza with_name(self, name):
        """Return a new path with the file name changed."""
        ikiwa not self.name:
            raise ValueError("%r has an empty name" % (self,))
        drv, root, parts = self._flavour.parse_parts((name,))
        ikiwa (not name or name[-1] in [self._flavour.sep, self._flavour.altsep]
            or drv or root or len(parts) != 1):
            raise ValueError("Invalid name %r" % (name))
        rudisha self._kutoka_parsed_parts(self._drv, self._root,
                                       self._parts[:-1] + [name])

    eleza with_suffix(self, suffix):
        """Return a new path with the file suffix changed.  If the path
        has no suffix, add given suffix.  If the given suffix is an empty
        string, remove the suffix kutoka the path.
        """
        f = self._flavour
        ikiwa f.sep in suffix or f.altsep and f.altsep in suffix:
            raise ValueError("Invalid suffix %r" % (suffix,))
        ikiwa suffix and not suffix.startswith('.') or suffix == '.':
            raise ValueError("Invalid suffix %r" % (suffix))
        name = self.name
        ikiwa not name:
            raise ValueError("%r has an empty name" % (self,))
        old_suffix = self.suffix
        ikiwa not old_suffix:
            name = name + suffix
        else:
            name = name[:-len(old_suffix)] + suffix
        rudisha self._kutoka_parsed_parts(self._drv, self._root,
                                       self._parts[:-1] + [name])

    eleza relative_to(self, *other):
        """Return the relative path to another path identified by the passed
        arguments.  If the operation is not possible (because this is not
        a subpath of the other path), raise ValueError.
        """
        # For the purpose of this method, drive and root are considered
        # separate parts, i.e.:
        #   Path('c:/').relative_to('c:')  gives Path('/')
        #   Path('c:/').relative_to('/')   raise ValueError
        ikiwa not other:
            raise TypeError("need at least one argument")
        parts = self._parts
        drv = self._drv
        root = self._root
        ikiwa root:
            abs_parts = [drv, root] + parts[1:]
        else:
            abs_parts = parts
        to_drv, to_root, to_parts = self._parse_args(other)
        ikiwa to_root:
            to_abs_parts = [to_drv, to_root] + to_parts[1:]
        else:
            to_abs_parts = to_parts
        n = len(to_abs_parts)
        cf = self._flavour.casefold_parts
        ikiwa (root or drv) ikiwa n == 0 else cf(abs_parts[:n]) != cf(to_abs_parts):
            formatted = self._format_parsed_parts(to_drv, to_root, to_parts)
            raise ValueError("{!r} does not start with {!r}"
                             .format(str(self), str(formatted)))
        rudisha self._kutoka_parsed_parts('', root ikiwa n == 1 else '',
                                       abs_parts[n:])

    @property
    eleza parts(self):
        """An object providing sequence-like access to the
        components in the filesystem path."""
        # We cache the tuple to avoid building a new one each time .parts
        # is accessed.  XXX is this necessary?
        try:
            rudisha self._pparts
        except AttributeError:
            self._pparts = tuple(self._parts)
            rudisha self._pparts

    eleza joinpath(self, *args):
        """Combine this path with one or several arguments, and rudisha a
        new path representing either a subpath (ikiwa all arguments are relative
        paths) or a totally different path (ikiwa one of the arguments is
        anchored).
        """
        rudisha self._make_child(args)

    eleza __truediv__(self, key):
        try:
            rudisha self._make_child((key,))
        except TypeError:
            rudisha NotImplemented

    eleza __rtruediv__(self, key):
        try:
            rudisha self._kutoka_parts([key] + self._parts)
        except TypeError:
            rudisha NotImplemented

    @property
    eleza parent(self):
        """The logical parent of the path."""
        drv = self._drv
        root = self._root
        parts = self._parts
        ikiwa len(parts) == 1 and (drv or root):
            rudisha self
        rudisha self._kutoka_parsed_parts(drv, root, parts[:-1])

    @property
    eleza parents(self):
        """A sequence of this path's logical parents."""
        rudisha _PathParents(self)

    eleza is_absolute(self):
        """True ikiwa the path is absolute (has both a root and, ikiwa applicable,
        a drive)."""
        ikiwa not self._root:
            rudisha False
        rudisha not self._flavour.has_drv or bool(self._drv)

    eleza is_reserved(self):
        """Return True ikiwa the path contains one of the special names reserved
        by the system, ikiwa any."""
        rudisha self._flavour.is_reserved(self._parts)

    eleza match(self, path_pattern):
        """
        Return True ikiwa this path matches the given pattern.
        """
        cf = self._flavour.casefold
        path_pattern = cf(path_pattern)
        drv, root, pat_parts = self._flavour.parse_parts((path_pattern,))
        ikiwa not pat_parts:
            raise ValueError("empty pattern")
        ikiwa drv and drv != cf(self._drv):
            rudisha False
        ikiwa root and root != cf(self._root):
            rudisha False
        parts = self._cparts
        ikiwa drv or root:
            ikiwa len(pat_parts) != len(parts):
                rudisha False
            pat_parts = pat_parts[1:]
        elikiwa len(pat_parts) > len(parts):
            rudisha False
        for part, pat in zip(reversed(parts), reversed(pat_parts)):
            ikiwa not fnmatch.fnmatchcase(part, pat):
                rudisha False
        rudisha True

# Can't subkundi os.PathLike kutoka PurePath and keep the constructor
# optimizations in PurePath._parse_args().
os.PathLike.register(PurePath)


kundi PurePosixPath(PurePath):
    """PurePath subkundi for non-Windows systems.

    On a POSIX system, instantiating a PurePath should rudisha this object.
    However, you can also instantiate it directly on any system.
    """
    _flavour = _posix_flavour
    __slots__ = ()


kundi PureWindowsPath(PurePath):
    """PurePath subkundi for Windows systems.

    On a Windows system, instantiating a PurePath should rudisha this object.
    However, you can also instantiate it directly on any system.
    """
    _flavour = _windows_flavour
    __slots__ = ()


# Filesystem-accessing classes


kundi Path(PurePath):
    """PurePath subkundi that can make system calls.

    Path represents a filesystem path but unlike PurePath, also offers
    methods to do system calls on path objects. Depending on your system,
    instantiating a Path will rudisha either a PosixPath or a WindowsPath
    object. You can also instantiate a PosixPath or WindowsPath directly,
    but cannot instantiate a WindowsPath on a POSIX system or vice versa.
    """
    __slots__ = (
        '_accessor',
        '_closed',
    )

    eleza __new__(cls, *args, **kwargs):
        ikiwa cls is Path:
            cls = WindowsPath ikiwa os.name == 'nt' else PosixPath
        self = cls._kutoka_parts(args, init=False)
        ikiwa not self._flavour.is_supported:
            raise NotImplementedError("cannot instantiate %r on your system"
                                      % (cls.__name__,))
        self._init()
        rudisha self

    eleza _init(self,
              # Private non-constructor arguments
              template=None,
              ):
        self._closed = False
        ikiwa template is not None:
            self._accessor = template._accessor
        else:
            self._accessor = _normal_accessor

    eleza _make_child_relpath(self, part):
        # This is an optimization used for dir walking.  `part` must be
        # a single part relative to this path.
        parts = self._parts + [part]
        rudisha self._kutoka_parsed_parts(self._drv, self._root, parts)

    eleza __enter__(self):
        ikiwa self._closed:
            self._raise_closed()
        rudisha self

    eleza __exit__(self, t, v, tb):
        self._closed = True

    eleza _raise_closed(self):
        raise ValueError("I/O operation on closed path")

    eleza _opener(self, name, flags, mode=0o666):
        # A stub for the opener argument to built-in open()
        rudisha self._accessor.open(self, flags, mode)

    eleza _raw_open(self, flags, mode=0o777):
        """
        Open the file pointed by this path and rudisha a file descriptor,
        as os.open() does.
        """
        ikiwa self._closed:
            self._raise_closed()
        rudisha self._accessor.open(self, flags, mode)

    # Public API

    @classmethod
    eleza cwd(cls):
        """Return a new path pointing to the current working directory
        (as returned by os.getcwd()).
        """
        rudisha cls(os.getcwd())

    @classmethod
    eleza home(cls):
        """Return a new path pointing to the user's home directory (as
        returned by os.path.expanduser('~')).
        """
        rudisha cls(cls()._flavour.gethomedir(None))

    eleza samefile(self, other_path):
        """Return whether other_path is the same or not as this file
        (as returned by os.path.samefile()).
        """
        st = self.stat()
        try:
            other_st = other_path.stat()
        except AttributeError:
            other_st = os.stat(other_path)
        rudisha os.path.samestat(st, other_st)

    eleza iterdir(self):
        """Iterate over the files in this directory.  Does not yield any
        result for the special paths '.' and '..'.
        """
        ikiwa self._closed:
            self._raise_closed()
        for name in self._accessor.listdir(self):
            ikiwa name in {'.', '..'}:
                # Yielding a path object for these makes little sense
                continue
            yield self._make_child_relpath(name)
            ikiwa self._closed:
                self._raise_closed()

    eleza glob(self, pattern):
        """Iterate over this subtree and yield all existing files (of any
        kind, including directories) matching the given relative pattern.
        """
        ikiwa not pattern:
            raise ValueError("Unacceptable pattern: {!r}".format(pattern))
        pattern = self._flavour.casefold(pattern)
        drv, root, pattern_parts = self._flavour.parse_parts((pattern,))
        ikiwa drv or root:
            raise NotImplementedError("Non-relative patterns are unsupported")
        selector = _make_selector(tuple(pattern_parts))
        for p in selector.select_kutoka(self):
            yield p

    eleza rglob(self, pattern):
        """Recursively yield all existing files (of any kind, including
        directories) matching the given relative pattern, anywhere in
        this subtree.
        """
        pattern = self._flavour.casefold(pattern)
        drv, root, pattern_parts = self._flavour.parse_parts((pattern,))
        ikiwa drv or root:
            raise NotImplementedError("Non-relative patterns are unsupported")
        selector = _make_selector(("**",) + tuple(pattern_parts))
        for p in selector.select_kutoka(self):
            yield p

    eleza absolute(self):
        """Return an absolute version of this path.  This function works
        even ikiwa the path doesn't point to anything.

        No normalization is done, i.e. all '.' and '..' will be kept along.
        Use resolve() to get the canonical path to a file.
        """
        # XXX untested yet!
        ikiwa self._closed:
            self._raise_closed()
        ikiwa self.is_absolute():
            rudisha self
        # FIXME this must defer to the specific flavour (and, under Windows,
        # use nt._getfullpathname())
        obj = self._kutoka_parts([os.getcwd()] + self._parts, init=False)
        obj._init(template=self)
        rudisha obj

    eleza resolve(self, strict=False):
        """
        Make the path absolute, resolving all symlinks on the way and also
        normalizing it (for example turning slashes into backslashes under
        Windows).
        """
        ikiwa self._closed:
            self._raise_closed()
        s = self._flavour.resolve(self, strict=strict)
        ikiwa s is None:
            # No symlink resolution => for consistency, raise an error if
            # the path doesn't exist or is forbidden
            self.stat()
            s = str(self.absolute())
        # Now we have no symlinks in the path, it's safe to normalize it.
        normed = self._flavour.pathmod.normpath(s)
        obj = self._kutoka_parts((normed,), init=False)
        obj._init(template=self)
        rudisha obj

    eleza stat(self):
        """
        Return the result of the stat() system call on this path, like
        os.stat() does.
        """
        rudisha self._accessor.stat(self)

    eleza owner(self):
        """
        Return the login name of the file owner.
        """
        agiza pwd
        rudisha pwd.getpwuid(self.stat().st_uid).pw_name

    eleza group(self):
        """
        Return the group name of the file gid.
        """
        agiza grp
        rudisha grp.getgrgid(self.stat().st_gid).gr_name

    eleza open(self, mode='r', buffering=-1, encoding=None,
             errors=None, newline=None):
        """
        Open the file pointed by this path and rudisha a file object, as
        the built-in open() function does.
        """
        ikiwa self._closed:
            self._raise_closed()
        rudisha io.open(self, mode, buffering, encoding, errors, newline,
                       opener=self._opener)

    eleza read_bytes(self):
        """
        Open the file in bytes mode, read it, and close the file.
        """
        with self.open(mode='rb') as f:
            rudisha f.read()

    eleza read_text(self, encoding=None, errors=None):
        """
        Open the file in text mode, read it, and close the file.
        """
        with self.open(mode='r', encoding=encoding, errors=errors) as f:
            rudisha f.read()

    eleza write_bytes(self, data):
        """
        Open the file in bytes mode, write to it, and close the file.
        """
        # type-check for the buffer interface before truncating the file
        view = memoryview(data)
        with self.open(mode='wb') as f:
            rudisha f.write(view)

    eleza write_text(self, data, encoding=None, errors=None):
        """
        Open the file in text mode, write to it, and close the file.
        """
        ikiwa not isinstance(data, str):
            raise TypeError('data must be str, not %s' %
                            data.__class__.__name__)
        with self.open(mode='w', encoding=encoding, errors=errors) as f:
            rudisha f.write(data)

    eleza touch(self, mode=0o666, exist_ok=True):
        """
        Create this file with the given access mode, ikiwa it doesn't exist.
        """
        ikiwa self._closed:
            self._raise_closed()
        ikiwa exist_ok:
            # First try to bump modification time
            # Implementation note: GNU touch uses the UTIME_NOW option of
            # the utimensat() / futimens() functions.
            try:
                self._accessor.utime(self, None)
            except OSError:
                # Avoid exception chaining
                pass
            else:
                return
        flags = os.O_CREAT | os.O_WRONLY
        ikiwa not exist_ok:
            flags |= os.O_EXCL
        fd = self._raw_open(flags, mode)
        os.close(fd)

    eleza mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.
        """
        ikiwa self._closed:
            self._raise_closed()
        try:
            self._accessor.mkdir(self, mode)
        except FileNotFoundError:
            ikiwa not parents or self.parent == self:
                raise
            self.parent.mkdir(parents=True, exist_ok=True)
            self.mkdir(mode, parents=False, exist_ok=exist_ok)
        except OSError:
            # Cannot rely on checking for EEXIST, since the operating system
            # could give priority to other errors like EACCES or EROFS
            ikiwa not exist_ok or not self.is_dir():
                raise

    eleza chmod(self, mode):
        """
        Change the permissions of the path, like os.chmod().
        """
        ikiwa self._closed:
            self._raise_closed()
        self._accessor.chmod(self, mode)

    eleza lchmod(self, mode):
        """
        Like chmod(), except ikiwa the path points to a symlink, the symlink's
        permissions are changed, rather than its target's.
        """
        ikiwa self._closed:
            self._raise_closed()
        self._accessor.lchmod(self, mode)

    eleza unlink(self, missing_ok=False):
        """
        Remove this file or link.
        If the path is a directory, use rmdir() instead.
        """
        ikiwa self._closed:
            self._raise_closed()
        try:
            self._accessor.unlink(self)
        except FileNotFoundError:
            ikiwa not missing_ok:
                raise

    eleza rmdir(self):
        """
        Remove this directory.  The directory must be empty.
        """
        ikiwa self._closed:
            self._raise_closed()
        self._accessor.rmdir(self)

    eleza lstat(self):
        """
        Like stat(), except ikiwa the path points to a symlink, the symlink's
        status information is returned, rather than its target's.
        """
        ikiwa self._closed:
            self._raise_closed()
        rudisha self._accessor.lstat(self)

    eleza link_to(self, target):
        """
        Create a hard link pointing to a path named target.
        """
        ikiwa self._closed:
            self._raise_closed()
        self._accessor.link_to(self, target)

    eleza rename(self, target):
        """
        Rename this path to the given path,
        and rudisha a new Path instance pointing to the given path.
        """
        ikiwa self._closed:
            self._raise_closed()
        self._accessor.rename(self, target)
        rudisha self.__class__(target)

    eleza replace(self, target):
        """
        Rename this path to the given path, clobbering the existing
        destination ikiwa it exists, and rudisha a new Path instance
        pointing to the given path.
        """
        ikiwa self._closed:
            self._raise_closed()
        self._accessor.replace(self, target)
        rudisha self.__class__(target)

    eleza symlink_to(self, target, target_is_directory=False):
        """
        Make this path a symlink pointing to the given path.
        Note the order of arguments (self, target) is the reverse of os.symlink's.
        """
        ikiwa self._closed:
            self._raise_closed()
        self._accessor.symlink(target, self, target_is_directory)

    # Convenience functions for querying the stat results

    eleza exists(self):
        """
        Whether this path exists.
        """
        try:
            self.stat()
        except OSError as e:
            ikiwa not _ignore_error(e):
                raise
            rudisha False
        except ValueError:
            # Non-encodable path
            rudisha False
        rudisha True

    eleza is_dir(self):
        """
        Whether this path is a directory.
        """
        try:
            rudisha S_ISDIR(self.stat().st_mode)
        except OSError as e:
            ikiwa not _ignore_error(e):
                raise
            # Path doesn't exist or is a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            rudisha False
        except ValueError:
            # Non-encodable path
            rudisha False

    eleza is_file(self):
        """
        Whether this path is a regular file (also True for symlinks pointing
        to regular files).
        """
        try:
            rudisha S_ISREG(self.stat().st_mode)
        except OSError as e:
            ikiwa not _ignore_error(e):
                raise
            # Path doesn't exist or is a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            rudisha False
        except ValueError:
            # Non-encodable path
            rudisha False

    eleza is_mount(self):
        """
        Check ikiwa this path is a POSIX mount point
        """
        # Need to exist and be a dir
        ikiwa not self.exists() or not self.is_dir():
            rudisha False

        parent = Path(self.parent)
        try:
            parent_dev = parent.stat().st_dev
        except OSError:
            rudisha False

        dev = self.stat().st_dev
        ikiwa dev != parent_dev:
            rudisha True
        ino = self.stat().st_ino
        parent_ino = parent.stat().st_ino
        rudisha ino == parent_ino

    eleza is_symlink(self):
        """
        Whether this path is a symbolic link.
        """
        try:
            rudisha S_ISLNK(self.lstat().st_mode)
        except OSError as e:
            ikiwa not _ignore_error(e):
                raise
            # Path doesn't exist
            rudisha False
        except ValueError:
            # Non-encodable path
            rudisha False

    eleza is_block_device(self):
        """
        Whether this path is a block device.
        """
        try:
            rudisha S_ISBLK(self.stat().st_mode)
        except OSError as e:
            ikiwa not _ignore_error(e):
                raise
            # Path doesn't exist or is a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            rudisha False
        except ValueError:
            # Non-encodable path
            rudisha False

    eleza is_char_device(self):
        """
        Whether this path is a character device.
        """
        try:
            rudisha S_ISCHR(self.stat().st_mode)
        except OSError as e:
            ikiwa not _ignore_error(e):
                raise
            # Path doesn't exist or is a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            rudisha False
        except ValueError:
            # Non-encodable path
            rudisha False

    eleza is_fifo(self):
        """
        Whether this path is a FIFO.
        """
        try:
            rudisha S_ISFIFO(self.stat().st_mode)
        except OSError as e:
            ikiwa not _ignore_error(e):
                raise
            # Path doesn't exist or is a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            rudisha False
        except ValueError:
            # Non-encodable path
            rudisha False

    eleza is_socket(self):
        """
        Whether this path is a socket.
        """
        try:
            rudisha S_ISSOCK(self.stat().st_mode)
        except OSError as e:
            ikiwa not _ignore_error(e):
                raise
            # Path doesn't exist or is a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            rudisha False
        except ValueError:
            # Non-encodable path
            rudisha False

    eleza expanduser(self):
        """ Return a new path with expanded ~ and ~user constructs
        (as returned by os.path.expanduser)
        """
        ikiwa (not (self._drv or self._root) and
            self._parts and self._parts[0][:1] == '~'):
            homedir = self._flavour.gethomedir(self._parts[0][1:])
            rudisha self._kutoka_parts([homedir] + self._parts[1:])

        rudisha self


kundi PosixPath(Path, PurePosixPath):
    """Path subkundi for non-Windows systems.

    On a POSIX system, instantiating a Path should rudisha this object.
    """
    __slots__ = ()

kundi WindowsPath(Path, PureWindowsPath):
    """Path subkundi for Windows systems.

    On a Windows system, instantiating a Path should rudisha this object.
    """
    __slots__ = ()

    eleza owner(self):
        raise NotImplementedError("Path.owner() is unsupported on this system")

    eleza group(self):
        raise NotImplementedError("Path.group() is unsupported on this system")

    eleza is_mount(self):
        raise NotImplementedError("Path.is_mount() is unsupported on this system")
