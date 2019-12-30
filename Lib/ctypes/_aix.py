"""
Lib/ctypes.util.find_library() support kila AIX
Similar approach kama done kila Darwin support by using separate files
but unlike Darwin - no extension such kama ctypes.macholib.*

dlopen() ni an interface to AIX initAndLoad() - primary documentation at:
https://www.ibm.com/support/knowledgecenter/en/ssw_aix_61/com.ibm.aix.basetrf1/dlopen.htm
https://www.ibm.com/support/knowledgecenter/en/ssw_aix_61/com.ibm.aix.basetrf1/load.htm

AIX supports two styles kila dlopen(): svr4 (System V Release 4) which ni common on posix
platforms, but also a BSD style - aka SVR3.

From AIX 5.3 Difference Addendum (December 2004)
2.9 SVR4 linking affinity
Nowadays, there are two major object file formats used by the operating systems:
XCOFF: The COFF enhanced by IBM na others. The original COFF (Common
Object File Format) was the base of SVR3 na BSD 4.2 systems.
ELF:   Executable na Linking Format that was developed by AT&T na ni a
base kila SVR4 UNIX.

While the shared library content ni identical on AIX - one ni located kama a filepath name
(svr4 style) na the other ni located kama a member of an archive (and the archive
is located kama a filepath name).

The key difference arises when supporting multiple abi formats (i.e., 32 na 64 bit).
For svr4 either only one ABI ni supported, ama there are two directories, ama there
are different file names. The most common solution kila multiple ABI ni multiple
directories.

For the XCOFF (aka AIX) style - one directory (one archive file) ni sufficient
as multiple shared libraries can be kwenye the archive - even sharing the same name.
In documentation the archive ni also referred to kama the "base" na the shared
library object ni referred to kama the "member".

For dlopen() on AIX (read initAndLoad()) the calls are similar.
Default activity occurs when no path information ni provided. When path
information ni provided dlopen() does sio search any other directories.

For SVR4 - the shared library name ni the name of the file expected: libFOO.so
For AIX - the shared library ni expressed kama base(member). The search ni kila the
base (e.g., libFOO.a) na once the base ni found the shared library - identified by
member (e.g., libFOO.so, ama shr.o) ni located na loaded.

The mode bit RTLD_MEMBER tells initAndLoad() that it needs to use the AIX (SVR3)
naming style.
"""
__author__ = "Michael Felt <aixtools@felt.demon.nl>"

agiza re
kutoka os agiza environ, path
kutoka sys agiza executable
kutoka ctypes agiza c_void_p, sizeof
kutoka subprocess agiza Popen, PIPE, DEVNULL

# Executable bit size - 32 ama 64
# Used to filter the search kwenye an archive by size, e.g., -X64
AIX_ABI = sizeof(c_void_p) * 8


kutoka sys agiza maxsize
eleza _last_version(libnames, sep):
    eleza _num_version(libname):
        # "libxyz.so.MAJOR.MINOR" => [MAJOR, MINOR]
        parts = libname.split(sep)
        nums = []
        jaribu:
            wakati parts:
                nums.insert(0, int(parts.pop()))
        tatizo ValueError:
            pita
        rudisha nums ama [maxsize]
    rudisha max(reversed(libnames), key=_num_version)

eleza get_ld_header(p):
    # "nested-function, but placed at module level
    ld_header = Tupu
    kila line kwenye p.stdout:
        ikiwa line.startswith(('/', './', '../')):
            ld_header = line
        lasivyo "INDEX" kwenye line:
            rudisha ld_header.rstrip('\n')
    rudisha Tupu

eleza get_ld_header_info(p):
    # "nested-function, but placed at module level
    # kama an ld_header was found, rudisha known paths, archives na members
    # these lines start ukijumuisha a digit
    info = []
    kila line kwenye p.stdout:
        ikiwa re.match("[0-9]", line):
            info.append(line)
        isipokua:
            # blank line (separator), consume line na end kila loop
            koma
    rudisha info

eleza get_ld_headers(file):
    """
    Parse the header of the loader section of executable na archives
    This function calls /usr/bin/dump -H kama a subprocess
    na returns a list of (ld_header, ld_header_info) tuples.
    """
    # get_ld_headers parsing:
    # 1. Find a line that starts ukijumuisha /, ./, ama ../ - set kama ld_header
    # 2. If "INDEX" kwenye occurs kwenye a following line - rudisha ld_header
    # 3. get info (lines starting ukijumuisha [0-9])
    ldr_headers = []
    p = Popen(["/usr/bin/dump", f"-X{AIX_ABI}", "-H", file],
        universal_newlines=Kweli, stdout=PIPE, stderr=DEVNULL)
    # be sure to read to the end-of-file - getting all entries
    wakati Kweli:
        ld_header = get_ld_header(p)
        ikiwa ld_header:
            ldr_headers.append((ld_header, get_ld_header_info(p)))
        isipokua:
            koma
    p.stdout.close()
    p.wait()
    rudisha ldr_headers

eleza get_shared(ld_headers):
    """
    extract the shareable objects kutoka ld_headers
    character "[" ni used to strip off the path information.
    Note: the "[" na "]" characters that are part of dump -H output
    are sio removed here.
    """
    shared = []
    kila (line, _) kwenye ld_headers:
        # potential member lines contain "["
        # otherwise, no processing needed
        ikiwa "[" kwenye line:
            # Strip off trailing colon (:)
            shared.append(line[line.index("["):-1])
    rudisha shared

eleza get_one_match(expr, lines):
    """
    Must be only one match, otherwise result ni Tupu.
    When there ni a match, strip leading "[" na trailing "]"
    """
    # member names kwenye the ld_headers output are between square brackets
    expr = rf'\[({expr})\]'
    matches = list(filter(Tupu, (re.search(expr, line) kila line kwenye lines)))
    ikiwa len(matches) == 1:
        rudisha matches[0].group(1)
    isipokua:
        rudisha Tupu

# additional processing to deal ukijumuisha AIX legacy names kila 64-bit members
eleza get_legacy(members):
    """
    This routine provides historical aka legacy naming schemes started
    kwenye AIX4 shared library support kila library members names.
    e.g., kwenye /usr/lib/libc.a the member name shr.o kila 32-bit binary na
    shr_64.o kila 64-bit binary.
    """
    ikiwa AIX_ABI == 64:
        # AIX 64-bit member ni one of shr64.o, shr_64.o, ama shr4_64.o
        expr = r'shr4?_?64\.o'
        member = get_one_match(expr, members)
        ikiwa member:
            rudisha member
    isipokua:
        # 32-bit legacy names - both shr.o na shr4.o exist.
        # shr.o ni the preffered name so we look kila shr.o first
        #  i.e., shr4.o ni returned only when shr.o does sio exist
        kila name kwenye ['shr.o', 'shr4.o']:
            member = get_one_match(re.escape(name), members)
            ikiwa member:
                rudisha member
    rudisha Tupu

eleza get_version(name, members):
    """
    Sort list of members na rudisha highest numbered version - ikiwa it exists.
    This function ni called when an unversioned libFOO.a(libFOO.so) has
    sio been found.

    Versioning kila the member name ni expected to follow
    GNU LIBTOOL conventions: the highest version (x, then X.y, then X.Y.z)
     * find [libFoo.so.X]
     * find [libFoo.so.X.Y]
     * find [libFoo.so.X.Y.Z]

    Before the GNU convention became the standard scheme regardless of
    binary size AIX packagers used GNU convention "as-is" kila 32-bit
    archive members but used an "distinguishing" name kila 64-bit members.
    This scheme inserted either 64 ama _64 between libFOO na .so
    - generally libFOO_64.so, but occasionally libFOO64.so
    """
    # the expression ending kila versions must start as
    # '.so.[0-9]', i.e., *.so.[at least one digit]
    # wakati multiple, more specific expressions could be specified
    # to search kila .so.X, .so.X.Y na .so.X.Y.Z
    # after the first required 'dot' digit
    # any combination of additional 'dot' digits pairs are accepted
    # anything more than libFOO.so.digits.digits.digits
    # should be seen kama a member name outside normal expectations
    exprs = [rf'lib{name}\.so\.[0-9]+[0-9.]*',
        rf'lib{name}_?64\.so\.[0-9]+[0-9.]*']
    kila expr kwenye exprs:
        versions = []
        kila line kwenye members:
            m = re.search(expr, line)
            ikiwa m:
                versions.append(m.group(0))
        ikiwa versions:
            rudisha _last_version(versions, '.')
    rudisha Tupu

eleza get_member(name, members):
    """
    Return an archive member matching the request kwenye name.
    Name ni the library name without any prefix like lib, suffix like .so,
    ama version number.
    Given a list of members find na rudisha the most appropriate result
    Priority ni given to generic libXXX.so, then a versioned libXXX.so.a.b.c
    na finally, legacy AIX naming scheme.
    """
    # look first kila a generic match - prepend lib na append .so
    expr = rf'lib{name}\.so'
    member = get_one_match(expr, members)
    ikiwa member:
        rudisha member
    lasivyo AIX_ABI == 64:
        expr = rf'lib{name}64\.so'
        member = get_one_match(expr, members)
    ikiwa member:
        rudisha member
    # since an exact match ukijumuisha .so kama suffix was sio found
    # look kila a versioned name
    # If a versioned name ni sio found, look kila AIX legacy member name
    member = get_version(name, members)
    ikiwa member:
        rudisha member
    isipokua:
        rudisha get_legacy(members)

eleza get_libpaths():
    """
    On AIX, the buildtime searchpath ni stored kwenye the executable.
    kama "loader header information".
    The command /usr/bin/dump -H extracts this info.
    Prefix searched libraries ukijumuisha LD_LIBRARY_PATH (preferred),
    ama LIBPATH ikiwa defined. These paths are appended to the paths
    to libraries the python executable ni linked with.
    This mimics AIX dlopen() behavior.
    """
    libpaths = environ.get("LD_LIBRARY_PATH")
    ikiwa libpaths ni Tupu:
        libpaths = environ.get("LIBPATH")
    ikiwa libpaths ni Tupu:
        libpaths = []
    isipokua:
        libpaths = libpaths.split(":")
    objects = get_ld_headers(executable)
    kila (_, lines) kwenye objects:
        kila line kwenye lines:
            # the second (optional) argument ni PATH ikiwa it includes a /
            path = line.split()[1]
            ikiwa "/" kwenye path:
                libpaths.extend(path.split(":"))
    rudisha libpaths

eleza find_shared(paths, name):
    """
    paths ni a list of directories to search kila an archive.
    name ni the abbreviated name given to find_library().
    Process: search "paths" kila archive, na ikiwa an archive ni found
    rudisha the result of get_member().
    If an archive ni sio found then rudisha Tupu
    """
    kila dir kwenye paths:
        # /lib ni a symbolic link to /usr/lib, skip it
        ikiwa dir == "/lib":
            endelea
        # "lib" ni prefixed to emulate compiler name resolution,
        # e.g., -lc to libc
        base = f'lib{name}.a'
        archive = path.join(dir, base)
        ikiwa path.exists(archive):
            members = get_shared(get_ld_headers(archive))
            member = get_member(re.escape(name), members)
            ikiwa member != Tupu:
                rudisha (base, member)
            isipokua:
                rudisha (Tupu, Tupu)
    rudisha (Tupu, Tupu)

eleza find_library(name):
    """AIX implementation of ctypes.util.find_library()
    Find an archive member that will dlopen(). If sio available,
    also search kila a file (or link) ukijumuisha a .so suffix.

    AIX supports two types of schemes that can be used ukijumuisha dlopen().
    The so-called SystemV Release4 (svr4) format ni commonly suffixed
    ukijumuisha .so wakati the (default) AIX scheme has the library (archive)
    ending ukijumuisha the suffix .a
    As an archive has multiple members (e.g., 32-bit na 64-bit) kwenye one file
    the argument pitaed to dlopen must include both the library na
    the member names kwenye a single string.

    find_library() looks first kila an archive (.a) ukijumuisha a suitable member.
    If no archive+member pair ni found, look kila a .so file.
    """

    libpaths = get_libpaths()
    (base, member) = find_shared(libpaths, name)
    ikiwa base != Tupu:
        rudisha f"{base}({member})"

    # To get here, a member kwenye an archive has sio been found
    # In other words, either:
    # a) a .a file was sio found
    # b) a .a file did sio have a suitable member
    # So, look kila a .so file
    # Check libpaths kila .so file
    # Note, the installation must prepare a link kutoka a .so
    # to a versioned file
    # This ni common practice by GNU libtool on other platforms
    soname = f"lib{name}.so"
    kila dir kwenye libpaths:
        # /lib ni a symbolic link to /usr/lib, skip it
        ikiwa dir == "/lib":
            endelea
        shlib = path.join(dir, soname)
        ikiwa path.exists(shlib):
            rudisha soname
    # ikiwa we are here, we have sio found anything plausible
    rudisha Tupu
