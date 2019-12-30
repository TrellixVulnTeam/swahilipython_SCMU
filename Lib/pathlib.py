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
kutoka urllib.parse agiza quote_from_bytes kama urlquote_from_bytes


supports_symlinks = Kweli
ikiwa os.name == 'nt':
    agiza nt
    ikiwa sys.getwindowsversion()[:2] >= (6, 0):
        kutoka nt agiza _getfinalpathname
    isipokua:
        supports_symlinks = Uongo
        _getfinalpathname = Tupu
isipokua:
    nt = Tupu


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
    21,  # ERROR_NOT_READY - drive exists but ni sio accessible
    1921,  # ERROR_CANT_RESOLVE_FILENAME - fix kila broken symlink pointing to itself
)

eleza _ignore_error(exception):
    rudisha (getattr(exception, 'errno', Tupu) kwenye _IGNORED_ERROS ama
            getattr(exception, 'winerror', Tupu) kwenye _IGNORED_WINERRORS)


eleza _is_wildcard_pattern(pat):
    # Whether this pattern needs actual matching using fnmatch, ama can
    # be looked up directly kama a file.
    rudisha "*" kwenye pat ama "?" kwenye pat ama "[" kwenye pat


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
        kila part kwenye it:
            ikiwa sio part:
                endelea
            ikiwa altsep:
                part = part.replace(altsep, sep)
            drv, root, rel = self.splitroot(part)
            ikiwa sep kwenye rel:
                kila x kwenye reversed(rel.split(sep)):
                    ikiwa x na x != '.':
                        parsed.append(sys.intern(x))
            isipokua:
                ikiwa rel na rel != '.':
                    parsed.append(sys.intern(rel))
            ikiwa drv ama root:
                ikiwa sio drv:
                    # If no drive ni present, try to find one kwenye the previous
                    # parts. This makes the result of parsing e.g.
                    # ("C:", "/", "a") reasonably intuitive.
                    kila part kwenye it:
                        ikiwa sio part:
                            endelea
                        ikiwa altsep:
                            part = part.replace(altsep, sep)
                        drv = self.splitroot(part)[0]
                        ikiwa drv:
                            koma
                koma
        ikiwa drv ama root:
            parsed.append(drv + root)
        parsed.reverse()
        rudisha drv, root, parsed

    eleza join_parsed_parts(self, drv, root, parts, drv2, root2, parts2):
        """
        Join the two paths represented by the respective
        (drive, root, parts) tuples.  Return a new (drive, root, parts) tuple.
        """
        ikiwa root2:
            ikiwa sio drv2 na drv:
                rudisha drv, root2, [drv + root2] + parts2[1:]
        lasivyo drv2:
            ikiwa drv2 == drv ama self.casefold(drv2) == self.casefold(drv):
                # Same drive => second path ni relative to the first
                rudisha drv, root, parts + parts2[1:]
        isipokua:
            # Second path ni non-anchored (common case)
            rudisha drv, root, parts + parts2
        rudisha drv2, root2, parts2


kundi _WindowsFlavour(_Flavour):
    # Reference kila Windows paths can be found at
    # http://msdn.microsoft.com/en-us/library/aa365247%28v=vs.85%29.aspx

    sep = '\\'
    altsep = '/'
    has_drv = Kweli
    pathmod = ntpath

    is_supported = (os.name == 'nt')

    drive_letters = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    ext_namespace_prefix = '\\\\?\\'

    reserved_names = (
        {'CON', 'PRN', 'AUX', 'NUL'} |
        {'COM%d' % i kila i kwenye range(1, 10)} |
        {'LPT%d' % i kila i kwenye range(1, 10)}
        )

    # Interesting findings about extended paths:
    # - '\\?\c:\a', '//?/c:\a' na '//?/c:/a' are all supported
    #   but '\\?\c:/a' ni not
    # - extended paths are always absolute; "relative" extended paths will
    #   fail.

    eleza splitroot(self, part, sep=sep):
        first = part[0:1]
        second = part[1:2]
        ikiwa (second == sep na first == sep):
            # XXX extended paths should also disable the collapsing of "."
            # components (according to MSDN docs).
            prefix, part = self._split_extended_path(part)
            first = part[0:1]
            second = part[1:2]
        isipokua:
            prefix = ''
        third = part[2:3]
        ikiwa (second == sep na first == sep na third != sep):
            # ni a UNC path:
            # vvvvvvvvvvvvvvvvvvvvv root
            # \\machine\mountpoint\directory\etc\...
            #            directory ^^^^^^^^^^^^^^
            index = part.find(sep, 2)
            ikiwa index != -1:
                index2 = part.find(sep, index + 1)
                # a UNC path can't have two slashes kwenye a row
                # (after the initial two)
                ikiwa index2 != index + 1:
                    ikiwa index2 == -1:
                        index2 = len(part)
                    ikiwa prefix:
                        rudisha prefix + part[1:index2], sep, part[index2+1:]
                    isipokua:
                        rudisha part[:index2], sep, part[index2+1:]
        drv = root = ''
        ikiwa second == ':' na first kwenye self.drive_letters:
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
        rudisha [p.lower() kila p kwenye parts]

    eleza resolve(self, path, strict=Uongo):
        s = str(path)
        ikiwa sio s:
            rudisha os.getcwd()
        previous_s = Tupu
        ikiwa _getfinalpathname ni sio Tupu:
            ikiwa strict:
                rudisha self._ext_to_normal(_getfinalpathname(s))
            isipokua:
                tail_parts = []  # End of the path after the first one sio found
                wakati Kweli:
                    jaribu:
                        s = self._ext_to_normal(_getfinalpathname(s))
                    tatizo FileNotFoundError:
                        previous_s = s
                        s, tail = os.path.split(s)
                        tail_parts.append(tail)
                        ikiwa previous_s == s:
                            rudisha path
                    isipokua:
                        rudisha os.path.join(s, *reversed(tail_parts))
        # Means fallback on absolute
        rudisha Tupu

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
        # NOTE: the rules kila reserved names seem somewhat complicated
        # (e.g. r"..\NUL" ni reserved but sio r"foo\NUL").
        # We err on the side of caution na rudisha Kweli kila paths which are
        # sio considered reserved by Windows.
        ikiwa sio parts:
            rudisha Uongo
        ikiwa parts[0].startswith('\\\\'):
            # UNC paths are never reserved
            rudisha Uongo
        rudisha parts[-1].partition('.')[0].upper() kwenye self.reserved_names

    eleza make_uri(self, path):
        # Under Windows, file URIs use the UTF-8 encoding.
        drive = path.drive
        ikiwa len(drive) == 2 na drive[1] == ':':
            # It's a path on a local drive => 'file:///c:/a/b'
            rest = path.as_posix()[2:].lstrip('/')
            rudisha 'file:///%s/%s' % (
                drive, urlquote_from_bytes(rest.encode('utf-8')))
        isipokua:
            # It's a path on a network drive => 'file://host/share/a/b'
            rudisha 'file:' + urlquote_from_bytes(path.as_posix().encode('utf-8'))

    eleza gethomedir(self, username):
        ikiwa 'HOME' kwenye os.environ:
            userhome = os.environ['HOME']
        lasivyo 'USERPROFILE' kwenye os.environ:
            userhome = os.environ['USERPROFILE']
        lasivyo 'HOMEPATH' kwenye os.environ:
            jaribu:
                drv = os.environ['HOMEDRIVE']
            tatizo KeyError:
                drv = ''
            userhome = drv + os.environ['HOMEPATH']
        isipokua:
            ashiria RuntimeError("Can't determine home directory")

        ikiwa username:
            # Try to guess user home directory.  By default all users
            # directories are located kwenye the same place na are named by
            # corresponding usernames.  If current user home directory points
            # to nonstandard place, this guess ni likely wrong.
            ikiwa os.environ['USERNAME'] != username:
                drv, root, parts = self.parse_parts((userhome,))
                ikiwa parts[-1] != os.environ['USERNAME']:
                    ashiria RuntimeError("Can't determine home directory "
                                       "kila %r" % username)
                parts[-1] = username
                ikiwa drv ama root:
                    userhome = drv + root + self.join(parts[1:])
                isipokua:
                    userhome = self.join(parts)
        rudisha userhome

kundi _PosixFlavour(_Flavour):
    sep = '/'
    altsep = ''
    has_drv = Uongo
    pathmod = posixpath

    is_supported = (os.name != 'nt')

    eleza splitroot(self, part, sep=sep):
        ikiwa part na part[0] == sep:
            stripped_part = part.lstrip(sep)
            # According to POSIX path resolution:
            # http://pubs.opengroup.org/onlinepubs/009695399/basedefs/xbd_chap04.html#tag_04_11
            # "A pathname that begins ukijumuisha two successive slashes may be
            # interpreted kwenye an implementation-defined manner, although more
            # than two leading slashes shall be treated kama a single slash".
            ikiwa len(part) - len(stripped_part) == 2:
                rudisha '', sep * 2, stripped_part
            isipokua:
                rudisha '', sep, stripped_part
        isipokua:
            rudisha '', '', part

    eleza casefold(self, s):
        rudisha s

    eleza casefold_parts(self, parts):
        rudisha parts

    eleza resolve(self, path, strict=Uongo):
        sep = self.sep
        accessor = path._accessor
        seen = {}
        eleza _resolve(path, rest):
            ikiwa rest.startswith(sep):
                path = ''

            kila name kwenye rest.split(sep):
                ikiwa sio name ama name == '.':
                    # current dir
                    endelea
                ikiwa name == '..':
                    # parent dir
                    path, _, _ = path.rpartition(sep)
                    endelea
                newpath = path + sep + name
                ikiwa newpath kwenye seen:
                    # Already seen this path
                    path = seen[newpath]
                    ikiwa path ni sio Tupu:
                        # use cached value
                        endelea
                    # The symlink ni sio resolved, so we must have a symlink loop.
                    ashiria RuntimeError("Symlink loop kutoka %r" % newpath)
                # Resolve the symbolic link
                jaribu:
                    target = accessor.readlink(newpath)
                tatizo OSError kama e:
                    ikiwa e.errno != EINVAL na strict:
                        raise
                    # Not a symlink, ama non-strict mode. We just leave the path
                    # untouched.
                    path = newpath
                isipokua:
                    seen[newpath] = Tupu # sio resolved symlink
                    path = _resolve(path, target)
                    seen[newpath] = path # resolved symlink

            rudisha path
        # NOTE: according to POSIX, getcwd() cannot contain path components
        # which are symlinks.
        base = '' ikiwa path.is_absolute() isipokua os.getcwd()
        rudisha _resolve(base, str(path)) ama sep

    eleza is_reserved(self, parts):
        rudisha Uongo

    eleza make_uri(self, path):
        # We represent the path using the local filesystem encoding,
        # kila portability to other applications.
        bpath = bytes(path)
        rudisha 'file://' + urlquote_from_bytes(bpath)

    eleza gethomedir(self, username):
        ikiwa sio username:
            jaribu:
                rudisha os.environ['HOME']
            tatizo KeyError:
                agiza pwd
                rudisha pwd.getpwuid(os.getuid()).pw_dir
        isipokua:
            agiza pwd
            jaribu:
                rudisha pwd.getpwnam(username).pw_dir
            tatizo KeyError:
                ashiria RuntimeError("Can't determine home directory "
                                   "kila %r" % username)


_windows_flavour = _WindowsFlavour()
_posix_flavour = _PosixFlavour()


kundi _Accessor:
    """An accessor implements a particular (system-specific ama not) way of
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
    isipokua:
        eleza lchmod(self, pathobj, mode):
            ashiria NotImplementedError("lchmod() sio available on this system")

    mkdir = os.mkdir

    unlink = os.unlink

    link_to = os.link

    rmdir = os.rmdir

    rename = os.rename

    replace = os.replace

    ikiwa nt:
        ikiwa supports_symlinks:
            symlink = os.symlink
        isipokua:
            eleza symlink(a, b, target_is_directory):
                ashiria NotImplementedError("symlink() sio available on this system")
    isipokua:
        # Under POSIX, os.symlink() takes two args
        @staticmethod
        eleza symlink(a, b, target_is_directory):
            rudisha os.symlink(a, b)

    utime = os.utime

    # Helper kila resolve()
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
    lasivyo '**' kwenye pat:
        ashiria ValueError("Invalid pattern: '**' can only be an entire path component")
    lasivyo _is_wildcard_pattern(pat):
        cls = _WildcardSelector
    isipokua:
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
            self.dironly = Kweli
        isipokua:
            self.successor = _TerminatingSelector()
            self.dironly = Uongo

    eleza select_from(self, parent_path):
        """Iterate over all child paths of `parent_path` matched by this
        selector.  This can contain parent_path itself."""
        path_cls = type(parent_path)
        is_dir = path_cls.is_dir
        exists = path_cls.exists
        scandir = parent_path._accessor.scandir
        ikiwa sio is_dir(parent_path):
            rudisha iter([])
        rudisha self._select_from(parent_path, is_dir, exists, scandir)


kundi _TerminatingSelector:

    eleza _select_from(self, parent_path, is_dir, exists, scandir):
        tuma parent_path


kundi _PreciseSelector(_Selector):

    eleza __init__(self, name, child_parts):
        self.name = name
        _Selector.__init__(self, child_parts)

    eleza _select_from(self, parent_path, is_dir, exists, scandir):
        jaribu:
            path = parent_path._make_child_relpath(self.name)
            ikiwa (is_dir ikiwa self.dironly isipokua exists)(path):
                kila p kwenye self.successor._select_from(path, is_dir, exists, scandir):
                    tuma p
        tatizo PermissionError:
            return


kundi _WildcardSelector(_Selector):

    eleza __init__(self, pat, child_parts):
        self.pat = re.compile(fnmatch.translate(pat))
        _Selector.__init__(self, child_parts)

    eleza _select_from(self, parent_path, is_dir, exists, scandir):
        jaribu:
            cf = parent_path._flavour.casefold
            entries = list(scandir(parent_path))
            kila entry kwenye entries:
                entry_is_dir = Uongo
                jaribu:
                    entry_is_dir = entry.is_dir()
                tatizo OSError kama e:
                    ikiwa sio _ignore_error(e):
                        raise
                ikiwa sio self.dironly ama entry_is_dir:
                    name = entry.name
                    casefolded = cf(name)
                    ikiwa self.pat.match(casefolded):
                        path = parent_path._make_child_relpath(name)
                        kila p kwenye self.successor._select_from(path, is_dir, exists, scandir):
                            tuma p
        tatizo PermissionError:
            return



kundi _RecursiveWildcardSelector(_Selector):

    eleza __init__(self, pat, child_parts):
        _Selector.__init__(self, child_parts)

    eleza _iterate_directories(self, parent_path, is_dir, scandir):
        tuma parent_path
        jaribu:
            entries = list(scandir(parent_path))
            kila entry kwenye entries:
                entry_is_dir = Uongo
                jaribu:
                    entry_is_dir = entry.is_dir()
                tatizo OSError kama e:
                    ikiwa sio _ignore_error(e):
                        raise
                ikiwa entry_is_dir na sio entry.is_symlink():
                    path = parent_path._make_child_relpath(entry.name)
                    kila p kwenye self._iterate_directories(path, is_dir, scandir):
                        tuma p
        tatizo PermissionError:
            return

    eleza _select_from(self, parent_path, is_dir, exists, scandir):
        jaribu:
            tumaed = set()
            jaribu:
                successor_select = self.successor._select_from
                kila starting_point kwenye self._iterate_directories(parent_path, is_dir, scandir):
                    kila p kwenye successor_select(starting_point, is_dir, exists, scandir):
                        ikiwa p haiko kwenye tumaed:
                            tuma p
                            tumaed.add(p)
            mwishowe:
                tumaed.clear()
        tatizo PermissionError:
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
        ikiwa self._drv ama self._root:
            rudisha len(self._parts) - 1
        isipokua:
            rudisha len(self._parts)

    eleza __getitem__(self, idx):
        ikiwa idx < 0 ama idx >= len(self):
            ashiria IndexError(idx)
        rudisha self._pathcls._from_parsed_parts(self._drv, self._root,
                                                self._parts[:-idx - 1])

    eleza __repr__(self):
        rudisha "<{}.parents>".format(self._pathcls.__name__)


kundi PurePath(object):
    """Base kundi kila manipulating paths without I/O.

    PurePath represents a filesystem path na offers operations which
    don't imply any actual filesystem I/O.  Depending on your system,
    instantiating a PurePath will rudisha either a PurePosixPath ama a
    PureWindowsPath object.  You can also instantiate either of these classes
    directly, regardless of your system.
    """
    __slots__ = (
        '_drv', '_root', '_parts',
        '_str', '_hash', '_pparts', '_cached_cparts',
    )

    eleza __new__(cls, *args):
        """Construct a PurePath kutoka one ama several strings na ama existing
        PurePath objects.  The strings na path objects are combined so as
        to tuma a canonicalized path, which ni incorporated into the
        new PurePath object.
        """
        ikiwa cls ni PurePath:
            cls = PureWindowsPath ikiwa os.name == 'nt' isipokua PurePosixPath
        rudisha cls._from_parts(args)

    eleza __reduce__(self):
        # Using the parts tuple helps share interned path parts
        # when pickling related paths.
        rudisha (self.__class__, tuple(self._parts))

    @classmethod
    eleza _parse_args(cls, args):
        # This ni useful when you don't want to create an instance, just
        # canonicalize some constructor arguments.
        parts = []
        kila a kwenye args:
            ikiwa isinstance(a, PurePath):
                parts += a._parts
            isipokua:
                a = os.fspath(a)
                ikiwa isinstance(a, str):
                    # Force-cast str subclasses to str (issue #21127)
                    parts.append(str(a))
                isipokua:
                    ashiria TypeError(
                        "argument should be a str object ama an os.PathLike "
                        "object returning str, sio %r"
                        % type(a))
        rudisha cls._flavour.parse_parts(parts)

    @classmethod
    eleza _from_parts(cls, args, init=Kweli):
        # We need to call _parse_args on the instance, so kama to get the
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
    eleza _from_parsed_parts(cls, drv, root, parts, init=Kweli):
        self = object.__new__(cls)
        self._drv = drv
        self._root = root
        self._parts = parts
        ikiwa init:
            self._init()
        rudisha self

    @classmethod
    eleza _format_parsed_parts(cls, drv, root, parts):
        ikiwa drv ama root:
            rudisha drv + root + cls._flavour.join(parts[1:])
        isipokua:
            rudisha cls._flavour.join(parts)

    eleza _init(self):
        # Overridden kwenye concrete Path
        pita

    eleza _make_child(self, args):
        drv, root, parts = self._parse_args(args)
        drv, root, parts = self._flavour.join_parsed_parts(
            self._drv, self._root, self._parts, drv, root, parts)
        rudisha self._from_parsed_parts(drv, root, parts)

    eleza __str__(self):
        """Return the string representation of the path, suitable for
        pitaing to system calls."""
        jaribu:
            rudisha self._str
        tatizo AttributeError:
            self._str = self._format_parsed_parts(self._drv, self._root,
                                                  self._parts) ama '.'
            rudisha self._str

    eleza __fspath__(self):
        rudisha str(self)

    eleza as_posix(self):
        """Return the string representation of the path ukijumuisha forward (/)
        slashes."""
        f = self._flavour
        rudisha str(self).replace(f.sep, '/')

    eleza __bytes__(self):
        """Return the bytes representation of the path.  This ni only
        recommended to use under Unix."""
        rudisha os.fsencode(self)

    eleza __repr__(self):
        rudisha "{}({!r})".format(self.__class__.__name__, self.as_posix())

    eleza as_uri(self):
        """Return the path kama a 'file' URI."""
        ikiwa sio self.is_absolute():
            ashiria ValueError("relative path can't be expressed kama a file URI")
        rudisha self._flavour.make_uri(self)

    @property
    eleza _cparts(self):
        # Cached casefolded parts, kila hashing na comparison
        jaribu:
            rudisha self._cached_cparts
        tatizo AttributeError:
            self._cached_cparts = self._flavour.casefold_parts(self._parts)
            rudisha self._cached_cparts

    eleza __eq__(self, other):
        ikiwa sio isinstance(other, PurePath):
            rudisha NotImplemented
        rudisha self._cparts == other._cparts na self._flavour ni other._flavour

    eleza __hash__(self):
        jaribu:
            rudisha self._hash
        tatizo AttributeError:
            self._hash = hash(tuple(self._cparts))
            rudisha self._hash

    eleza __lt__(self, other):
        ikiwa sio isinstance(other, PurePath) ama self._flavour ni sio other._flavour:
            rudisha NotImplemented
        rudisha self._cparts < other._cparts

    eleza __le__(self, other):
        ikiwa sio isinstance(other, PurePath) ama self._flavour ni sio other._flavour:
            rudisha NotImplemented
        rudisha self._cparts <= other._cparts

    eleza __gt__(self, other):
        ikiwa sio isinstance(other, PurePath) ama self._flavour ni sio other._flavour:
            rudisha NotImplemented
        rudisha self._cparts > other._cparts

    eleza __ge__(self, other):
        ikiwa sio isinstance(other, PurePath) ama self._flavour ni sio other._flavour:
            rudisha NotImplemented
        rudisha self._cparts >= other._cparts

    drive = property(attrgetter('_drv'),
                     doc="""The drive prefix (letter ama UNC path), ikiwa any.""")

    root = property(attrgetter('_root'),
                    doc="""The root of the path, ikiwa any.""")

    @property
    eleza anchor(self):
        """The concatenation of the drive na root, ama ''."""
        anchor = self._drv + self._root
        rudisha anchor

    @property
    eleza name(self):
        """The final path component, ikiwa any."""
        parts = self._parts
        ikiwa len(parts) == (1 ikiwa (self._drv ama self._root) isipokua 0):
            rudisha ''
        rudisha parts[-1]

    @property
    eleza suffix(self):
        """The final component's last suffix, ikiwa any."""
        name = self.name
        i = name.rfind('.')
        ikiwa 0 < i < len(name) - 1:
            rudisha name[i:]
        isipokua:
            rudisha ''

    @property
    eleza suffixes(self):
        """A list of the final component's suffixes, ikiwa any."""
        name = self.name
        ikiwa name.endswith('.'):
            rudisha []
        name = name.lstrip('.')
        rudisha ['.' + suffix kila suffix kwenye name.split('.')[1:]]

    @property
    eleza stem(self):
        """The final path component, minus its last suffix."""
        name = self.name
        i = name.rfind('.')
        ikiwa 0 < i < len(name) - 1:
            rudisha name[:i]
        isipokua:
            rudisha name

    eleza with_name(self, name):
        """Return a new path ukijumuisha the file name changed."""
        ikiwa sio self.name:
            ashiria ValueError("%r has an empty name" % (self,))
        drv, root, parts = self._flavour.parse_parts((name,))
        ikiwa (sio name ama name[-1] kwenye [self._flavour.sep, self._flavour.altsep]
            ama drv ama root ama len(parts) != 1):
            ashiria ValueError("Invalid name %r" % (name))
        rudisha self._from_parsed_parts(self._drv, self._root,
                                       self._parts[:-1] + [name])

    eleza with_suffix(self, suffix):
        """Return a new path ukijumuisha the file suffix changed.  If the path
        has no suffix, add given suffix.  If the given suffix ni an empty
        string, remove the suffix kutoka the path.
        """
        f = self._flavour
        ikiwa f.sep kwenye suffix ama f.altsep na f.altsep kwenye suffix:
            ashiria ValueError("Invalid suffix %r" % (suffix,))
        ikiwa suffix na sio suffix.startswith('.') ama suffix == '.':
            ashiria ValueError("Invalid suffix %r" % (suffix))
        name = self.name
        ikiwa sio name:
            ashiria ValueError("%r has an empty name" % (self,))
        old_suffix = self.suffix
        ikiwa sio old_suffix:
            name = name + suffix
        isipokua:
            name = name[:-len(old_suffix)] + suffix
        rudisha self._from_parsed_parts(self._drv, self._root,
                                       self._parts[:-1] + [name])

    eleza relative_to(self, *other):
        """Return the relative path to another path identified by the pitaed
        arguments.  If the operation ni sio possible (because this ni not
        a subpath of the other path), ashiria ValueError.
        """
        # For the purpose of this method, drive na root are considered
        # separate parts, i.e.:
        #   Path('c:/').relative_to('c:')  gives Path('/')
        #   Path('c:/').relative_to('/')   ashiria ValueError
        ikiwa sio other:
            ashiria TypeError("need at least one argument")
        parts = self._parts
        drv = self._drv
        root = self._root
        ikiwa root:
            abs_parts = [drv, root] + parts[1:]
        isipokua:
            abs_parts = parts
        to_drv, to_root, to_parts = self._parse_args(other)
        ikiwa to_root:
            to_abs_parts = [to_drv, to_root] + to_parts[1:]
        isipokua:
            to_abs_parts = to_parts
        n = len(to_abs_parts)
        cf = self._flavour.casefold_parts
        ikiwa (root ama drv) ikiwa n == 0 isipokua cf(abs_parts[:n]) != cf(to_abs_parts):
            formatted = self._format_parsed_parts(to_drv, to_root, to_parts)
            ashiria ValueError("{!r} does sio start ukijumuisha {!r}"
                             .format(str(self), str(formatted)))
        rudisha self._from_parsed_parts('', root ikiwa n == 1 isipokua '',
                                       abs_parts[n:])

    @property
    eleza parts(self):
        """An object providing sequence-like access to the
        components kwenye the filesystem path."""
        # We cache the tuple to avoid building a new one each time .parts
        # ni accessed.  XXX ni this necessary?
        jaribu:
            rudisha self._pparts
        tatizo AttributeError:
            self._pparts = tuple(self._parts)
            rudisha self._pparts

    eleza joinpath(self, *args):
        """Combine this path ukijumuisha one ama several arguments, na rudisha a
        new path representing either a subpath (ikiwa all arguments are relative
        paths) ama a totally different path (ikiwa one of the arguments is
        anchored).
        """
        rudisha self._make_child(args)

    eleza __truediv__(self, key):
        jaribu:
            rudisha self._make_child((key,))
        tatizo TypeError:
            rudisha NotImplemented

    eleza __rtruediv__(self, key):
        jaribu:
            rudisha self._from_parts([key] + self._parts)
        tatizo TypeError:
            rudisha NotImplemented

    @property
    eleza parent(self):
        """The logical parent of the path."""
        drv = self._drv
        root = self._root
        parts = self._parts
        ikiwa len(parts) == 1 na (drv ama root):
            rudisha self
        rudisha self._from_parsed_parts(drv, root, parts[:-1])

    @property
    eleza parents(self):
        """A sequence of this path's logical parents."""
        rudisha _PathParents(self)

    eleza is_absolute(self):
        """Kweli ikiwa the path ni absolute (has both a root and, ikiwa applicable,
        a drive)."""
        ikiwa sio self._root:
            rudisha Uongo
        rudisha sio self._flavour.has_drv ama bool(self._drv)

    eleza is_reserved(self):
        """Return Kweli ikiwa the path contains one of the special names reserved
        by the system, ikiwa any."""
        rudisha self._flavour.is_reserved(self._parts)

    eleza match(self, path_pattern):
        """
        Return Kweli ikiwa this path matches the given pattern.
        """
        cf = self._flavour.casefold
        path_pattern = cf(path_pattern)
        drv, root, pat_parts = self._flavour.parse_parts((path_pattern,))
        ikiwa sio pat_parts:
            ashiria ValueError("empty pattern")
        ikiwa drv na drv != cf(self._drv):
            rudisha Uongo
        ikiwa root na root != cf(self._root):
            rudisha Uongo
        parts = self._cparts
        ikiwa drv ama root:
            ikiwa len(pat_parts) != len(parts):
                rudisha Uongo
            pat_parts = pat_parts[1:]
        lasivyo len(pat_parts) > len(parts):
            rudisha Uongo
        kila part, pat kwenye zip(reversed(parts), reversed(pat_parts)):
            ikiwa sio fnmatch.fnmatchcase(part, pat):
                rudisha Uongo
        rudisha Kweli

# Can't subkundi os.PathLike kutoka PurePath na keep the constructor
# optimizations kwenye PurePath._parse_args().
os.PathLike.register(PurePath)


kundi PurePosixPath(PurePath):
    """PurePath subkundi kila non-Windows systems.

    On a POSIX system, instantiating a PurePath should rudisha this object.
    However, you can also instantiate it directly on any system.
    """
    _flavour = _posix_flavour
    __slots__ = ()


kundi PureWindowsPath(PurePath):
    """PurePath subkundi kila Windows systems.

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
    instantiating a Path will rudisha either a PosixPath ama a WindowsPath
    object. You can also instantiate a PosixPath ama WindowsPath directly,
    but cannot instantiate a WindowsPath on a POSIX system ama vice versa.
    """
    __slots__ = (
        '_accessor',
        '_closed',
    )

    eleza __new__(cls, *args, **kwargs):
        ikiwa cls ni Path:
            cls = WindowsPath ikiwa os.name == 'nt' isipokua PosixPath
        self = cls._from_parts(args, init=Uongo)
        ikiwa sio self._flavour.is_supported:
            ashiria NotImplementedError("cannot instantiate %r on your system"
                                      % (cls.__name__,))
        self._init()
        rudisha self

    eleza _init(self,
              # Private non-constructor arguments
              template=Tupu,
              ):
        self._closed = Uongo
        ikiwa template ni sio Tupu:
            self._accessor = template._accessor
        isipokua:
            self._accessor = _normal_accessor

    eleza _make_child_relpath(self, part):
        # This ni an optimization used kila dir walking.  `part` must be
        # a single part relative to this path.
        parts = self._parts + [part]
        rudisha self._from_parsed_parts(self._drv, self._root, parts)

    eleza __enter__(self):
        ikiwa self._closed:
            self._raise_closed()
        rudisha self

    eleza __exit__(self, t, v, tb):
        self._closed = Kweli

    eleza _raise_closed(self):
        ashiria ValueError("I/O operation on closed path")

    eleza _opener(self, name, flags, mode=0o666):
        # A stub kila the opener argument to built-in open()
        rudisha self._accessor.open(self, flags, mode)

    eleza _raw_open(self, flags, mode=0o777):
        """
        Open the file pointed by this path na rudisha a file descriptor,
        kama os.open() does.
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
        rudisha cls(cls()._flavour.gethomedir(Tupu))

    eleza samefile(self, other_path):
        """Return whether other_path ni the same ama sio kama this file
        (as returned by os.path.samefile()).
        """
        st = self.stat()
        jaribu:
            other_st = other_path.stat()
        tatizo AttributeError:
            other_st = os.stat(other_path)
        rudisha os.path.samestat(st, other_st)

    eleza iterdir(self):
        """Iterate over the files kwenye this directory.  Does sio tuma any
        result kila the special paths '.' na '..'.
        """
        ikiwa self._closed:
            self._raise_closed()
        kila name kwenye self._accessor.listdir(self):
            ikiwa name kwenye {'.', '..'}:
                # Yielding a path object kila these makes little sense
                endelea
            tuma self._make_child_relpath(name)
            ikiwa self._closed:
                self._raise_closed()

    eleza glob(self, pattern):
        """Iterate over this subtree na tuma all existing files (of any
        kind, including directories) matching the given relative pattern.
        """
        ikiwa sio pattern:
            ashiria ValueError("Unacceptable pattern: {!r}".format(pattern))
        pattern = self._flavour.casefold(pattern)
        drv, root, pattern_parts = self._flavour.parse_parts((pattern,))
        ikiwa drv ama root:
            ashiria NotImplementedError("Non-relative patterns are unsupported")
        selector = _make_selector(tuple(pattern_parts))
        kila p kwenye selector.select_from(self):
            tuma p

    eleza rglob(self, pattern):
        """Recursively tuma all existing files (of any kind, including
        directories) matching the given relative pattern, anywhere in
        this subtree.
        """
        pattern = self._flavour.casefold(pattern)
        drv, root, pattern_parts = self._flavour.parse_parts((pattern,))
        ikiwa drv ama root:
            ashiria NotImplementedError("Non-relative patterns are unsupported")
        selector = _make_selector(("**",) + tuple(pattern_parts))
        kila p kwenye selector.select_from(self):
            tuma p

    eleza absolute(self):
        """Return an absolute version of this path.  This function works
        even ikiwa the path doesn't point to anything.

        No normalization ni done, i.e. all '.' na '..' will be kept along.
        Use resolve() to get the canonical path to a file.
        """
        # XXX untested yet!
        ikiwa self._closed:
            self._raise_closed()
        ikiwa self.is_absolute():
            rudisha self
        # FIXME this must defer to the specific flavour (and, under Windows,
        # use nt._getfullpathname())
        obj = self._from_parts([os.getcwd()] + self._parts, init=Uongo)
        obj._init(template=self)
        rudisha obj

    eleza resolve(self, strict=Uongo):
        """
        Make the path absolute, resolving all symlinks on the way na also
        normalizing it (kila example turning slashes into backslashes under
        Windows).
        """
        ikiwa self._closed:
            self._raise_closed()
        s = self._flavour.resolve(self, strict=strict)
        ikiwa s ni Tupu:
            # No symlink resolution => kila consistency, ashiria an error if
            # the path doesn't exist ama ni forbidden
            self.stat()
            s = str(self.absolute())
        # Now we have no symlinks kwenye the path, it's safe to normalize it.
        normed = self._flavour.pathmod.normpath(s)
        obj = self._from_parts((normed,), init=Uongo)
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

    eleza open(self, mode='r', buffering=-1, encoding=Tupu,
             errors=Tupu, newline=Tupu):
        """
        Open the file pointed by this path na rudisha a file object, as
        the built-in open() function does.
        """
        ikiwa self._closed:
            self._raise_closed()
        rudisha io.open(self, mode, buffering, encoding, errors, newline,
                       opener=self._opener)

    eleza read_bytes(self):
        """
        Open the file kwenye bytes mode, read it, na close the file.
        """
        ukijumuisha self.open(mode='rb') kama f:
            rudisha f.read()

    eleza read_text(self, encoding=Tupu, errors=Tupu):
        """
        Open the file kwenye text mode, read it, na close the file.
        """
        ukijumuisha self.open(mode='r', encoding=encoding, errors=errors) kama f:
            rudisha f.read()

    eleza write_bytes(self, data):
        """
        Open the file kwenye bytes mode, write to it, na close the file.
        """
        # type-check kila the buffer interface before truncating the file
        view = memoryview(data)
        ukijumuisha self.open(mode='wb') kama f:
            rudisha f.write(view)

    eleza write_text(self, data, encoding=Tupu, errors=Tupu):
        """
        Open the file kwenye text mode, write to it, na close the file.
        """
        ikiwa sio isinstance(data, str):
            ashiria TypeError('data must be str, sio %s' %
                            data.__class__.__name__)
        ukijumuisha self.open(mode='w', encoding=encoding, errors=errors) kama f:
            rudisha f.write(data)

    eleza touch(self, mode=0o666, exist_ok=Kweli):
        """
        Create this file ukijumuisha the given access mode, ikiwa it doesn't exist.
        """
        ikiwa self._closed:
            self._raise_closed()
        ikiwa exist_ok:
            # First try to bump modification time
            # Implementation note: GNU touch uses the UTIME_NOW option of
            # the utimensat() / futimens() functions.
            jaribu:
                self._accessor.utime(self, Tupu)
            tatizo OSError:
                # Avoid exception chaining
                pita
            isipokua:
                return
        flags = os.O_CREAT | os.O_WRONLY
        ikiwa sio exist_ok:
            flags |= os.O_EXCL
        fd = self._raw_open(flags, mode)
        os.close(fd)

    eleza mkdir(self, mode=0o777, parents=Uongo, exist_ok=Uongo):
        """
        Create a new directory at this given path.
        """
        ikiwa self._closed:
            self._raise_closed()
        jaribu:
            self._accessor.mkdir(self, mode)
        tatizo FileNotFoundError:
            ikiwa sio parents ama self.parent == self:
                raise
            self.parent.mkdir(parents=Kweli, exist_ok=Kweli)
            self.mkdir(mode, parents=Uongo, exist_ok=exist_ok)
        tatizo OSError:
            # Cannot rely on checking kila EEXIST, since the operating system
            # could give priority to other errors like EACCES ama EROFS
            ikiwa sio exist_ok ama sio self.is_dir():
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
        Like chmod(), tatizo ikiwa the path points to a symlink, the symlink's
        permissions are changed, rather than its target's.
        """
        ikiwa self._closed:
            self._raise_closed()
        self._accessor.lchmod(self, mode)

    eleza unlink(self, missing_ok=Uongo):
        """
        Remove this file ama link.
        If the path ni a directory, use rmdir() instead.
        """
        ikiwa self._closed:
            self._raise_closed()
        jaribu:
            self._accessor.unlink(self)
        tatizo FileNotFoundError:
            ikiwa sio missing_ok:
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
        Like stat(), tatizo ikiwa the path points to a symlink, the symlink's
        status information ni returned, rather than its target's.
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
        na rudisha a new Path instance pointing to the given path.
        """
        ikiwa self._closed:
            self._raise_closed()
        self._accessor.rename(self, target)
        rudisha self.__class__(target)

    eleza replace(self, target):
        """
        Rename this path to the given path, clobbering the existing
        destination ikiwa it exists, na rudisha a new Path instance
        pointing to the given path.
        """
        ikiwa self._closed:
            self._raise_closed()
        self._accessor.replace(self, target)
        rudisha self.__class__(target)

    eleza symlink_to(self, target, target_is_directory=Uongo):
        """
        Make this path a symlink pointing to the given path.
        Note the order of arguments (self, target) ni the reverse of os.symlink's.
        """
        ikiwa self._closed:
            self._raise_closed()
        self._accessor.symlink(target, self, target_is_directory)

    # Convenience functions kila querying the stat results

    eleza exists(self):
        """
        Whether this path exists.
        """
        jaribu:
            self.stat()
        tatizo OSError kama e:
            ikiwa sio _ignore_error(e):
                raise
            rudisha Uongo
        tatizo ValueError:
            # Non-encodable path
            rudisha Uongo
        rudisha Kweli

    eleza is_dir(self):
        """
        Whether this path ni a directory.
        """
        jaribu:
            rudisha S_ISDIR(self.stat().st_mode)
        tatizo OSError kama e:
            ikiwa sio _ignore_error(e):
                raise
            # Path doesn't exist ama ni a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            rudisha Uongo
        tatizo ValueError:
            # Non-encodable path
            rudisha Uongo

    eleza is_file(self):
        """
        Whether this path ni a regular file (also Kweli kila symlinks pointing
        to regular files).
        """
        jaribu:
            rudisha S_ISREG(self.stat().st_mode)
        tatizo OSError kama e:
            ikiwa sio _ignore_error(e):
                raise
            # Path doesn't exist ama ni a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            rudisha Uongo
        tatizo ValueError:
            # Non-encodable path
            rudisha Uongo

    eleza is_mount(self):
        """
        Check ikiwa this path ni a POSIX mount point
        """
        # Need to exist na be a dir
        ikiwa sio self.exists() ama sio self.is_dir():
            rudisha Uongo

        parent = Path(self.parent)
        jaribu:
            parent_dev = parent.stat().st_dev
        tatizo OSError:
            rudisha Uongo

        dev = self.stat().st_dev
        ikiwa dev != parent_dev:
            rudisha Kweli
        ino = self.stat().st_ino
        parent_ino = parent.stat().st_ino
        rudisha ino == parent_ino

    eleza is_symlink(self):
        """
        Whether this path ni a symbolic link.
        """
        jaribu:
            rudisha S_ISLNK(self.lstat().st_mode)
        tatizo OSError kama e:
            ikiwa sio _ignore_error(e):
                raise
            # Path doesn't exist
            rudisha Uongo
        tatizo ValueError:
            # Non-encodable path
            rudisha Uongo

    eleza is_block_device(self):
        """
        Whether this path ni a block device.
        """
        jaribu:
            rudisha S_ISBLK(self.stat().st_mode)
        tatizo OSError kama e:
            ikiwa sio _ignore_error(e):
                raise
            # Path doesn't exist ama ni a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            rudisha Uongo
        tatizo ValueError:
            # Non-encodable path
            rudisha Uongo

    eleza is_char_device(self):
        """
        Whether this path ni a character device.
        """
        jaribu:
            rudisha S_ISCHR(self.stat().st_mode)
        tatizo OSError kama e:
            ikiwa sio _ignore_error(e):
                raise
            # Path doesn't exist ama ni a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            rudisha Uongo
        tatizo ValueError:
            # Non-encodable path
            rudisha Uongo

    eleza is_fifo(self):
        """
        Whether this path ni a FIFO.
        """
        jaribu:
            rudisha S_ISFIFO(self.stat().st_mode)
        tatizo OSError kama e:
            ikiwa sio _ignore_error(e):
                raise
            # Path doesn't exist ama ni a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            rudisha Uongo
        tatizo ValueError:
            # Non-encodable path
            rudisha Uongo

    eleza is_socket(self):
        """
        Whether this path ni a socket.
        """
        jaribu:
            rudisha S_ISSOCK(self.stat().st_mode)
        tatizo OSError kama e:
            ikiwa sio _ignore_error(e):
                raise
            # Path doesn't exist ama ni a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            rudisha Uongo
        tatizo ValueError:
            # Non-encodable path
            rudisha Uongo

    eleza expanduser(self):
        """ Return a new path ukijumuisha expanded ~ na ~user constructs
        (as returned by os.path.expanduser)
        """
        ikiwa (sio (self._drv ama self._root) na
            self._parts na self._parts[0][:1] == '~'):
            homedir = self._flavour.gethomedir(self._parts[0][1:])
            rudisha self._from_parts([homedir] + self._parts[1:])

        rudisha self


kundi PosixPath(Path, PurePosixPath):
    """Path subkundi kila non-Windows systems.

    On a POSIX system, instantiating a Path should rudisha this object.
    """
    __slots__ = ()

kundi WindowsPath(Path, PureWindowsPath):
    """Path subkundi kila Windows systems.

    On a Windows system, instantiating a Path should rudisha this object.
    """
    __slots__ = ()

    eleza owner(self):
        ashiria NotImplementedError("Path.owner() ni unsupported on this system")

    eleza group(self):
        ashiria NotImplementedError("Path.group() ni unsupported on this system")

    eleza is_mount(self):
        ashiria NotImplementedError("Path.is_mount() ni unsupported on this system")
