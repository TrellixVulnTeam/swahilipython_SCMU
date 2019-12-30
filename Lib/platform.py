#!/usr/bin/env python3

""" This module tries to retrieve kama much platform-identifying data as
    possible. It makes this information available via function APIs.

    If called kutoka the command line, it prints the platform
    information concatenated kama single string to stdout. The output
    format ni useable kama part of a filename.

"""
#    This module ni maintained by Marc-Andre Lemburg <mal@egenix.com>.
#    If you find problems, please submit bug reports/patches via the
#    Python bug tracker (http://bugs.python.org) na assign them to "lemburg".
#
#    Still needed:
#    * support kila MS-DOS (PythonDX ?)
#    * support kila Amiga na other still unsupported platforms running Python
#    * support kila additional Linux distributions
#
#    Many thanks to all those who helped adding platform-specific
#    checks (in no particular order):
#
#      Charles G Waldman, David Arnold, Gordon McMillan, Ben Darnell,
#      Jeff Bauer, Cliff Crawford, Ivan Van Laningham, Josef
#      Betancourt, Randall Hopper, Karl Putland, John Farrell, Greg
#      Andruk, Just van Rossum, Thomas Heller, Mark R. Levinson, Mark
#      Hammond, Bill Tutt, Hans Nowak, Uwe Zessin (OpenVMS support),
#      Colin Kong, Trent Mick, Guido van Rossum, Anthony Baxter, Steve
#      Dower
#
#    History:
#
#    <see CVS na SVN checkin messages kila history>
#
#    1.0.8 - changed Windows support to read version kutoka kernel32.dll
#    1.0.7 - added DEV_NULL
#    1.0.6 - added linux_distribution()
#    1.0.5 - fixed Java support to allow running the module on Jython
#    1.0.4 - added IronPython support
#    1.0.3 - added normalization of Windows system name
#    1.0.2 - added more Windows support
#    1.0.1 - reformatted to make doc.py happy
#    1.0.0 - reformatted a bit na checked into Python CVS
#    0.8.0 - added sys.version parser na various new access
#            APIs (python_version(), python_compiler(), etc.)
#    0.7.2 - fixed architecture() to use sizeof(pointer) where available
#    0.7.1 - added support kila Caldera OpenLinux
#    0.7.0 - some fixes kila WinCE; untabified the source file
#    0.6.2 - support kila OpenVMS - requires version 1.5.2-V006 ama higher na
#            vms_lib.getsyi() configured
#    0.6.1 - added code to prevent 'uname -p' on platforms which are
#            known sio to support it
#    0.6.0 - fixed win32_ver() to hopefully work on Win95,98,NT na Win2k;
#            did some cleanup of the interfaces - some APIs have changed
#    0.5.5 - fixed another type kwenye the MacOS code... should have
#            used more coffee today ;-)
#    0.5.4 - fixed a few typos kwenye the MacOS code
#    0.5.3 - added experimental MacOS support; added better popen()
#            workarounds kwenye _syscmd_ver() -- still sio 100% elegant
#            though
#    0.5.2 - fixed uname() to rudisha '' instead of 'unknown' kwenye all
#            rudisha values (the system uname command tends to rudisha
#            'unknown' instead of just leaving the field empty)
#    0.5.1 - included code kila slackware dist; added exception handlers
#            to cover up situations where platforms don't have os.popen
#            (e.g. Mac) ama fail on socket.gethostname(); fixed libc
#            detection RE
#    0.5.0 - changed the API names referring to system commands to *syscmd*;
#            added java_ver(); made syscmd_ver() a private
#            API (was system_ver() kwenye previous versions) -- use uname()
#            instead; extended the win32_ver() to also rudisha processor
#            type information
#    0.4.0 - added win32_ver() na modified the platform() output kila WinXX
#    0.3.4 - fixed a bug kwenye _follow_symlinks()
#    0.3.3 - fixed popen() na "file" command invocation bugs
#    0.3.2 - added architecture() API na support kila it kwenye platform()
#    0.3.1 - fixed syscmd_ver() RE to support Windows NT
#    0.3.0 - added system alias support
#    0.2.3 - removed 'wince' again... oh well.
#    0.2.2 - added 'wince' to syscmd_ver() supported platforms
#    0.2.1 - added cache logic na changed the platform string format
#    0.2.0 - changed the API to use functions instead of module globals
#            since some action take too long to be run on module import
#    0.1.0 - first release
#
#    You can always get the latest version of this module at:
#
#             http://www.egenix.com/files/python/platform.py
#
#    If that URL should fail, try contacting the author.

__copyright__ = """
    Copyright (c) 1999-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2010, eGenix.com Software GmbH; mailto:info@egenix.com

    Permission to use, copy, modify, na distribute this software na its
    documentation kila any purpose na without fee ama royalty ni hereby granted,
    provided that the above copyright notice appear kwenye all copies na that
    both that copyright notice na this permission notice appear kwenye
    supporting documentation ama portions thereof, including modifications,
    that you make.

    EGENIX.COM SOFTWARE GMBH DISCLAIMS ALL WARRANTIES WITH REGARD TO
    THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
    FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,
    INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING
    FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
    NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
    WITH THE USE OR PERFORMANCE OF THIS SOFTWARE !

"""

__version__ = '1.0.8'

agiza collections
agiza os
agiza re
agiza sys

### Globals & Constants

# Helper kila comparing two version number strings.
# Based on the description of the PHP's version_compare():
# http://php.net/manual/en/function.version-compare.php

_ver_stages = {
    # any string sio found kwenye this dict, will get 0 assigned
    'dev': 10,
    'alpha': 20, 'a': 20,
    'beta': 30, 'b': 30,
    'c': 40,
    'RC': 50, 'rc': 50,
    # number, will get 100 assigned
    'pl': 200, 'p': 200,
}

_component_re = re.compile(r'([0-9]+|[._+-])')

eleza _comparable_version(version):
    result = []
    kila v kwenye _component_re.split(version):
        ikiwa v haiko kwenye '._+-':
            jaribu:
                v = int(v, 10)
                t = 100
            tatizo ValueError:
                t = _ver_stages.get(v, 0)
            result.extend((t, v))
    rudisha result

### Platform specific APIs

_libc_search = re.compile(b'(__libc_init)'
                          b'|'
                          b'(GLIBC_([0-9.]+))'
                          b'|'
                          br'(libc(_\w+)?\.so(?:\.(\d[0-9.]*))?)', re.ASCII)

eleza libc_ver(executable=Tupu, lib='', version='', chunksize=16384):

    """ Tries to determine the libc version that the file executable
        (which defaults to the Python interpreter) ni linked against.

        Returns a tuple of strings (lib,version) which default to the
        given parameters kwenye case the lookup fails.

        Note that the function has intimate knowledge of how different
        libc versions add symbols to the executable na thus ni probably
        only useable kila executables compiled using gcc.

        The file ni read na scanned kwenye chunks of chunksize bytes.

    """
    ikiwa executable ni Tupu:
        jaribu:
            ver = os.confstr('CS_GNU_LIBC_VERSION')
            # parse 'glibc 2.28' kama ('glibc', '2.28')
            parts = ver.split(maxsplit=1)
            ikiwa len(parts) == 2:
                rudisha tuple(parts)
        tatizo (AttributeError, ValueError, OSError):
            # os.confstr() ama CS_GNU_LIBC_VERSION value sio available
            pita

        executable = sys.executable

    V = _comparable_version
    ikiwa hasattr(os.path, 'realpath'):
        # Python 2.2 introduced os.path.realpath(); it ni used
        # here to work around problems ukijumuisha Cygwin sio being
        # able to open symlinks kila reading
        executable = os.path.realpath(executable)
    ukijumuisha open(executable, 'rb') kama f:
        binary = f.read(chunksize)
        pos = 0
        wakati pos < len(binary):
            ikiwa b'libc' kwenye binary ama b'GLIBC' kwenye binary:
                m = _libc_search.search(binary, pos)
            isipokua:
                m = Tupu
            ikiwa sio m ama m.end() == len(binary):
                chunk = f.read(chunksize)
                ikiwa chunk:
                    binary = binary[max(pos, len(binary) - 1000):] + chunk
                    pos = 0
                    endelea
                ikiwa sio m:
                    koma
            libcinit, glibc, glibcversion, so, threads, soversion = [
                s.decode('latin1') ikiwa s ni sio Tupu isipokua s
                kila s kwenye m.groups()]
            ikiwa libcinit na sio lib:
                lib = 'libc'
            lasivyo glibc:
                ikiwa lib != 'glibc':
                    lib = 'glibc'
                    version = glibcversion
                lasivyo V(glibcversion) > V(version):
                    version = glibcversion
            lasivyo so:
                ikiwa lib != 'glibc':
                    lib = 'libc'
                    ikiwa soversion na (sio version ama V(soversion) > V(version)):
                        version = soversion
                    ikiwa threads na version[-len(threads):] != threads:
                        version = version + threads
            pos = m.end()
    rudisha lib, version

eleza _norm_version(version, build=''):

    """ Normalize the version na build strings na rudisha a single
        version string using the format major.minor.build (or patchlevel).
    """
    l = version.split('.')
    ikiwa build:
        l.append(build)
    jaribu:
        ints = map(int, l)
    tatizo ValueError:
        strings = l
    isipokua:
        strings = list(map(str, ints))
    version = '.'.join(strings[:3])
    rudisha version

_ver_output = re.compile(r'(?:([\w ]+) ([\w.]+) '
                         r'.*'
                         r'\[.* ([\d.]+)\])')

# Examples of VER command output:
#
#   Windows 2000:  Microsoft Windows 2000 [Version 5.00.2195]
#   Windows XP:    Microsoft Windows XP [Version 5.1.2600]
#   Windows Vista: Microsoft Windows [Version 6.0.6002]
#
# Note that the "Version" string gets localized on different
# Windows versions.

eleza _syscmd_ver(system='', release='', version='',

               supported_platforms=('win32', 'win16', 'dos')):

    """ Tries to figure out the OS version used na returns
        a tuple (system, release, version).

        It uses the "ver" shell command kila this which ni known
        to exists on Windows, DOS. XXX Others too ?

        In case this fails, the given parameters are used as
        defaults.

    """
    ikiwa sys.platform haiko kwenye supported_platforms:
        rudisha system, release, version

    # Try some common cmd strings
    agiza subprocess
    kila cmd kwenye ('ver', 'command /c ver', 'cmd /c ver'):
        jaribu:
            info = subprocess.check_output(cmd,
                                           stderr=subprocess.DEVNULL,
                                           text=Kweli,
                                           shell=Kweli)
        tatizo (OSError, subprocess.CalledProcessError) kama why:
            #andika('Command %s failed: %s' % (cmd, why))
            endelea
        isipokua:
            koma
    isipokua:
        rudisha system, release, version

    # Parse the output
    info = info.strip()
    m = _ver_output.match(info)
    ikiwa m ni sio Tupu:
        system, release, version = m.groups()
        # Strip trailing dots kutoka version na release
        ikiwa release[-1] == '.':
            release = release[:-1]
        ikiwa version[-1] == '.':
            version = version[:-1]
        # Normalize the version na build strings (eliminating additional
        # zeros)
        version = _norm_version(version)
    rudisha system, release, version

_WIN32_CLIENT_RELEASES = {
    (5, 0): "2000",
    (5, 1): "XP",
    # Strictly, 5.2 client ni XP 64-bit, but platform.py historically
    # has always called it 2003 Server
    (5, 2): "2003Server",
    (5, Tupu): "post2003",

    (6, 0): "Vista",
    (6, 1): "7",
    (6, 2): "8",
    (6, 3): "8.1",
    (6, Tupu): "post8.1",

    (10, 0): "10",
    (10, Tupu): "post10",
}

# Server release name lookup will default to client names ikiwa necessary
_WIN32_SERVER_RELEASES = {
    (5, 2): "2003Server",

    (6, 0): "2008Server",
    (6, 1): "2008ServerR2",
    (6, 2): "2012Server",
    (6, 3): "2012ServerR2",
    (6, Tupu): "post2012ServerR2",
}

eleza win32_is_iot():
    rudisha win32_edition() kwenye ('IoTUAP', 'NanoServer', 'WindowsCoreHeadless', 'IoTEdgeOS')

eleza win32_edition():
    jaribu:
        jaribu:
            agiza winreg
        tatizo ImportError:
            agiza _winreg kama winreg
    tatizo ImportError:
        pita
    isipokua:
        jaribu:
            cvkey = r'SOFTWARE\Microsoft\Windows NT\CurrentVersion'
            ukijumuisha winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, cvkey) kama key:
                rudisha winreg.QueryValueEx(key, 'EditionId')[0]
        tatizo OSError:
            pita

    rudisha Tupu

eleza win32_ver(release='', version='', csd='', ptype=''):
    jaribu:
        kutoka sys agiza getwindowsversion
    tatizo ImportError:
        rudisha release, version, csd, ptype

    winver = getwindowsversion()
    maj, min, build = winver.platform_version ama winver[:3]
    version = '{0}.{1}.{2}'.format(maj, min, build)

    release = (_WIN32_CLIENT_RELEASES.get((maj, min)) ama
               _WIN32_CLIENT_RELEASES.get((maj, Tupu)) ama
               release)

    # getwindowsversion() reflect the compatibility mode Python is
    # running under, na so the service pack value ni only going to be
    # valid ikiwa the versions match.
    ikiwa winver[:2] == (maj, min):
        jaribu:
            csd = 'SP{}'.format(winver.service_pack_major)
        tatizo AttributeError:
            ikiwa csd[:13] == 'Service Pack ':
                csd = 'SP' + csd[13:]

    # VER_NT_SERVER = 3
    ikiwa getattr(winver, 'product_type', Tupu) == 3:
        release = (_WIN32_SERVER_RELEASES.get((maj, min)) ama
                   _WIN32_SERVER_RELEASES.get((maj, Tupu)) ama
                   release)

    jaribu:
        jaribu:
            agiza winreg
        tatizo ImportError:
            agiza _winreg kama winreg
    tatizo ImportError:
        pita
    isipokua:
        jaribu:
            cvkey = r'SOFTWARE\Microsoft\Windows NT\CurrentVersion'
            ukijumuisha winreg.OpenKeyEx(HKEY_LOCAL_MACHINE, cvkey) kama key:
                ptype = QueryValueEx(key, 'CurrentType')[0]
        tatizo:
            pita

    rudisha release, version, csd, ptype


eleza _mac_ver_xml():
    fn = '/System/Library/CoreServices/SystemVersion.plist'
    ikiwa sio os.path.exists(fn):
        rudisha Tupu

    jaribu:
        agiza plistlib
    tatizo ImportError:
        rudisha Tupu

    ukijumuisha open(fn, 'rb') kama f:
        pl = plistlib.load(f)
    release = pl['ProductVersion']
    versioninfo = ('', '', '')
    machine = os.uname().machine
    ikiwa machine kwenye ('ppc', 'Power Macintosh'):
        # Canonical name
        machine = 'PowerPC'

    rudisha release, versioninfo, machine


eleza mac_ver(release='', versioninfo=('', '', ''), machine=''):

    """ Get macOS version information na rudisha it kama tuple (release,
        versioninfo, machine) ukijumuisha versioninfo being a tuple (version,
        dev_stage, non_release_version).

        Entries which cansio be determined are set to the parameter values
        which default to ''. All tuple entries are strings.
    """

    # First try reading the information kutoka an XML file which should
    # always be present
    info = _mac_ver_xml()
    ikiwa info ni sio Tupu:
        rudisha info

    # If that also doesn't work rudisha the default values
    rudisha release, versioninfo, machine

eleza _java_getprop(name, default):

    kutoka java.lang agiza System
    jaribu:
        value = System.getProperty(name)
        ikiwa value ni Tupu:
            rudisha default
        rudisha value
    tatizo AttributeError:
        rudisha default

eleza java_ver(release='', vendor='', vminfo=('', '', ''), osinfo=('', '', '')):

    """ Version interface kila Jython.

        Returns a tuple (release, vendor, vminfo, osinfo) ukijumuisha vminfo being
        a tuple (vm_name, vm_release, vm_vendor) na osinfo being a
        tuple (os_name, os_version, os_arch).

        Values which cansio be determined are set to the defaults
        given kama parameters (which all default to '').

    """
    # Import the needed APIs
    jaribu:
        agiza java.lang
    tatizo ImportError:
        rudisha release, vendor, vminfo, osinfo

    vendor = _java_getprop('java.vendor', vendor)
    release = _java_getprop('java.version', release)
    vm_name, vm_release, vm_vendor = vminfo
    vm_name = _java_getprop('java.vm.name', vm_name)
    vm_vendor = _java_getprop('java.vm.vendor', vm_vendor)
    vm_release = _java_getprop('java.vm.version', vm_release)
    vminfo = vm_name, vm_release, vm_vendor
    os_name, os_version, os_arch = osinfo
    os_arch = _java_getprop('java.os.arch', os_arch)
    os_name = _java_getprop('java.os.name', os_name)
    os_version = _java_getprop('java.os.version', os_version)
    osinfo = os_name, os_version, os_arch

    rudisha release, vendor, vminfo, osinfo

### System name aliasing

eleza system_alias(system, release, version):

    """ Returns (system, release, version) aliased to common
        marketing names used kila some systems.

        It also does some reordering of the information kwenye some cases
        where it would otherwise cause confusion.

    """
    ikiwa system == 'SunOS':
        # Sun's OS
        ikiwa release < '5':
            # These releases use the old name SunOS
            rudisha system, release, version
        # Modify release (marketing release = SunOS release - 3)
        l = release.split('.')
        ikiwa l:
            jaribu:
                major = int(l[0])
            tatizo ValueError:
                pita
            isipokua:
                major = major - 3
                l[0] = str(major)
                release = '.'.join(l)
        ikiwa release < '6':
            system = 'Solaris'
        isipokua:
            # XXX Whatever the new SunOS marketing name is...
            system = 'Solaris'

    lasivyo system == 'IRIX64':
        # IRIX reports IRIX64 on platforms ukijumuisha 64-bit support; yet it
        # ni really a version na sio a different platform, since 32-bit
        # apps are also supported..
        system = 'IRIX'
        ikiwa version:
            version = version + ' (64bit)'
        isipokua:
            version = '64bit'

    lasivyo system kwenye ('win32', 'win16'):
        # In case one of the other tricks
        system = 'Windows'

    # bpo-35516: Don't replace Darwin ukijumuisha macOS since input release na
    # version arguments can be different than the currently running version.

    rudisha system, release, version

### Various internal helpers

eleza _platform(*args):

    """ Helper to format the platform string kwenye a filename
        compatible format e.g. "system-version-machine".
    """
    # Format the platform string
    platform = '-'.join(x.strip() kila x kwenye filter(len, args))

    # Cleanup some possible filename obstacles...
    platform = platform.replace(' ', '_')
    platform = platform.replace('/', '-')
    platform = platform.replace('\\', '-')
    platform = platform.replace(':', '-')
    platform = platform.replace(';', '-')
    platform = platform.replace('"', '-')
    platform = platform.replace('(', '-')
    platform = platform.replace(')', '-')

    # No need to report 'unknown' information...
    platform = platform.replace('unknown', '')

    # Fold '--'s na remove trailing '-'
    wakati 1:
        cleaned = platform.replace('--', '-')
        ikiwa cleaned == platform:
            koma
        platform = cleaned
    wakati platform[-1] == '-':
        platform = platform[:-1]

    rudisha platform

eleza _node(default=''):

    """ Helper to determine the node name of this machine.
    """
    jaribu:
        agiza socket
    tatizo ImportError:
        # No sockets...
        rudisha default
    jaribu:
        rudisha socket.gethostname()
    tatizo OSError:
        # Still sio working...
        rudisha default

eleza _follow_symlinks(filepath):

    """ In case filepath ni a symlink, follow it until a
        real file ni reached.
    """
    filepath = os.path.abspath(filepath)
    wakati os.path.islink(filepath):
        filepath = os.path.normpath(
            os.path.join(os.path.dirname(filepath), os.readlink(filepath)))
    rudisha filepath

eleza _syscmd_uname(option, default=''):

    """ Interface to the system's uname command.
    """
    ikiwa sys.platform kwenye ('dos', 'win32', 'win16'):
        # XXX Others too ?
        rudisha default

    agiza subprocess
    jaribu:
        output = subprocess.check_output(('uname', option),
                                         stderr=subprocess.DEVNULL,
                                         text=Kweli)
    tatizo (OSError, subprocess.CalledProcessError):
        rudisha default
    rudisha (output.strip() ama default)

eleza _syscmd_file(target, default=''):

    """ Interface to the system's file command.

        The function uses the -b option of the file command to have it
        omit the filename kwenye its output. Follow the symlinks. It returns
        default kwenye case the command should fail.

    """
    ikiwa sys.platform kwenye ('dos', 'win32', 'win16'):
        # XXX Others too ?
        rudisha default

    agiza subprocess
    target = _follow_symlinks(target)
    # "file" output ni locale dependent: force the usage of the C locale
    # to get deterministic behavior.
    env = dict(os.environ, LC_ALL='C')
    jaribu:
        # -b: do sio prepend filenames to output lines (brief mode)
        output = subprocess.check_output(['file', '-b', target],
                                         stderr=subprocess.DEVNULL,
                                         env=env)
    tatizo (OSError, subprocess.CalledProcessError):
        rudisha default
    ikiwa sio output:
        rudisha default
    # With the C locale, the output should be mostly ASCII-compatible.
    # Decode kutoka Latin-1 to prevent Unicode decode error.
    rudisha output.decode('latin-1')

### Information about the used architecture

# Default values kila architecture; non-empty strings override the
# defaults given kama parameters
_default_architecture = {
    'win32': ('', 'WindowsPE'),
    'win16': ('', 'Windows'),
    'dos': ('', 'MSDOS'),
}

eleza architecture(executable=sys.executable, bits='', linkage=''):

    """ Queries the given executable (defaults to the Python interpreter
        binary) kila various architecture information.

        Returns a tuple (bits, linkage) which contains information about
        the bit architecture na the linkage format used kila the
        executable. Both values are returned kama strings.

        Values that cansio be determined are returned kama given by the
        parameter presets. If bits ni given kama '', the sizeof(pointer)
        (or sizeof(long) on Python version < 1.5.2) ni used as
        indicator kila the supported pointer size.

        The function relies on the system's "file" command to do the
        actual work. This ni available on most ikiwa sio all Unix
        platforms. On some non-Unix platforms where the "file" command
        does sio exist na the executable ni set to the Python interpreter
        binary defaults kutoka _default_architecture are used.

    """
    # Use the sizeof(pointer) kama default number of bits ikiwa nothing
    # isipokua ni given kama default.
    ikiwa sio bits:
        agiza struct
        size = struct.calcsize('P')
        bits = str(size * 8) + 'bit'

    # Get data kutoka the 'file' system command
    ikiwa executable:
        fileout = _syscmd_file(executable, '')
    isipokua:
        fileout = ''

    ikiwa sio fileout na \
       executable == sys.executable:
        # "file" command did sio rudisha anything; we'll try to provide
        # some sensible defaults then...
        ikiwa sys.platform kwenye _default_architecture:
            b, l = _default_architecture[sys.platform]
            ikiwa b:
                bits = b
            ikiwa l:
                linkage = l
        rudisha bits, linkage

    ikiwa 'executable' haiko kwenye fileout na 'shared object' haiko kwenye fileout:
        # Format sio supported
        rudisha bits, linkage

    # Bits
    ikiwa '32-bit' kwenye fileout:
        bits = '32bit'
    lasivyo 'N32' kwenye fileout:
        # On Irix only
        bits = 'n32bit'
    lasivyo '64-bit' kwenye fileout:
        bits = '64bit'

    # Linkage
    ikiwa 'ELF' kwenye fileout:
        linkage = 'ELF'
    lasivyo 'PE' kwenye fileout:
        # E.g. Windows uses this format
        ikiwa 'Windows' kwenye fileout:
            linkage = 'WindowsPE'
        isipokua:
            linkage = 'PE'
    lasivyo 'COFF' kwenye fileout:
        linkage = 'COFF'
    lasivyo 'MS-DOS' kwenye fileout:
        linkage = 'MSDOS'
    isipokua:
        # XXX the A.OUT format also falls under this class...
        pita

    rudisha bits, linkage

### Portable uname() interface

uname_result = collections.namedtuple("uname_result",
                    "system node release version machine processor")

_uname_cache = Tupu

eleza uname():

    """ Fairly portable uname interface. Returns a tuple
        of strings (system, node, release, version, machine, processor)
        identifying the underlying platform.

        Note that unlike the os.uname function this also returns
        possible processor information kama an additional tuple entry.

        Entries which cansio be determined are set to ''.

    """
    global _uname_cache
    no_os_uname = 0

    ikiwa _uname_cache ni sio Tupu:
        rudisha _uname_cache

    processor = ''

    # Get some infos kutoka the builtin os.uname API...
    jaribu:
        system, node, release, version, machine = os.uname()
    tatizo AttributeError:
        no_os_uname = 1

    ikiwa no_os_uname ama sio list(filter(Tupu, (system, node, release, version, machine))):
        # Hmm, no there ni either no uname ama uname has returned
        #'unknowns'... we'll have to poke around the system then.
        ikiwa no_os_uname:
            system = sys.platform
            release = ''
            version = ''
            node = _node()
            machine = ''

        use_syscmd_ver = 1

        # Try win32_ver() on win32 platforms
        ikiwa system == 'win32':
            release, version, csd, ptype = win32_ver()
            ikiwa release na version:
                use_syscmd_ver = 0
            # Try to use the PROCESSOR_* environment variables
            # available on Win XP na later; see
            # http://support.microsoft.com/kb/888731 na
            # http://www.geocities.com/rick_lively/MANUALS/ENV/MSWIN/PROCESSI.HTM
            ikiwa sio machine:
                # WOW64 processes mask the native architecture
                ikiwa "PROCESSOR_ARCHITEW6432" kwenye os.environ:
                    machine = os.environ.get("PROCESSOR_ARCHITEW6432", '')
                isipokua:
                    machine = os.environ.get('PROCESSOR_ARCHITECTURE', '')
            ikiwa sio processor:
                processor = os.environ.get('PROCESSOR_IDENTIFIER', machine)

        # Try the 'ver' system command available on some
        # platforms
        ikiwa use_syscmd_ver:
            system, release, version = _syscmd_ver(system)
            # Normalize system to what win32_ver() normally returns
            # (_syscmd_ver() tends to rudisha the vendor name kama well)
            ikiwa system == 'Microsoft Windows':
                system = 'Windows'
            lasivyo system == 'Microsoft' na release == 'Windows':
                # Under Windows Vista na Windows Server 2008,
                # Microsoft changed the output of the ver command. The
                # release ni no longer printed.  This causes the
                # system na release to be misidentified.
                system = 'Windows'
                ikiwa '6.0' == version[:3]:
                    release = 'Vista'
                isipokua:
                    release = ''

        # In case we still don't know anything useful, we'll try to
        # help ourselves
        ikiwa system kwenye ('win32', 'win16'):
            ikiwa sio version:
                ikiwa system == 'win32':
                    version = '32bit'
                isipokua:
                    version = '16bit'
            system = 'Windows'

        lasivyo system[:4] == 'java':
            release, vendor, vminfo, osinfo = java_ver()
            system = 'Java'
            version = ', '.join(vminfo)
            ikiwa sio version:
                version = vendor

    # System specific extensions
    ikiwa system == 'OpenVMS':
        # OpenVMS seems to have release na version mixed up
        ikiwa sio release ama release == '0':
            release = version
            version = ''
        # Get processor information
        jaribu:
            agiza vms_lib
        tatizo ImportError:
            pita
        isipokua:
            csid, cpu_number = vms_lib.getsyi('SYI$_CPU', 0)
            ikiwa (cpu_number >= 128):
                processor = 'Alpha'
            isipokua:
                processor = 'VAX'
    ikiwa sio processor:
        # Get processor information kutoka the uname system command
        processor = _syscmd_uname('-p', '')

    #If any unknowns still exist, replace them ukijumuisha ''s, which are more portable
    ikiwa system == 'unknown':
        system = ''
    ikiwa node == 'unknown':
        node = ''
    ikiwa release == 'unknown':
        release = ''
    ikiwa version == 'unknown':
        version = ''
    ikiwa machine == 'unknown':
        machine = ''
    ikiwa processor == 'unknown':
        processor = ''

    #  normalize name
    ikiwa system == 'Microsoft' na release == 'Windows':
        system = 'Windows'
        release = 'Vista'

    _uname_cache = uname_result(system, node, release, version,
                                machine, processor)
    rudisha _uname_cache

### Direct interfaces to some of the uname() rudisha values

eleza system():

    """ Returns the system/OS name, e.g. 'Linux', 'Windows' ama 'Java'.

        An empty string ni returned ikiwa the value cansio be determined.

    """
    rudisha uname().system

eleza node():

    """ Returns the computer's network name (which may sio be fully
        qualified)

        An empty string ni returned ikiwa the value cansio be determined.

    """
    rudisha uname().node

eleza release():

    """ Returns the system's release, e.g. '2.2.0' ama 'NT'

        An empty string ni returned ikiwa the value cansio be determined.

    """
    rudisha uname().release

eleza version():

    """ Returns the system's release version, e.g. '#3 on degas'

        An empty string ni returned ikiwa the value cansio be determined.

    """
    rudisha uname().version

eleza machine():

    """ Returns the machine type, e.g. 'i386'

        An empty string ni returned ikiwa the value cansio be determined.

    """
    rudisha uname().machine

eleza processor():

    """ Returns the (true) processor name, e.g. 'amdk6'

        An empty string ni returned ikiwa the value cansio be
        determined. Note that many platforms do sio provide this
        information ama simply rudisha the same value kama kila machine(),
        e.g.  NetBSD does this.

    """
    rudisha uname().processor

### Various APIs kila extracting information kutoka sys.version

_sys_version_parser = re.compile(
    r'([\w.+]+)\s*'  # "version<space>"
    r'\(#?([^,]+)'  # "(#buildno"
    r'(?:,\s*([\w ]*)'  # ", builddate"
    r'(?:,\s*([\w :]*))?)?\)\s*'  # ", buildtime)<space>"
    r'\[([^\]]+)\]?', re.ASCII)  # "[compiler]"

_ironpython_sys_version_parser = re.compile(
    r'IronPython\s*'
    r'([\d\.]+)'
    r'(?: \(([\d\.]+)\))?'
    r' on (.NET [\d\.]+)', re.ASCII)

# IronPython covering 2.6 na 2.7
_ironpython26_sys_version_parser = re.compile(
    r'([\d.]+)\s*'
    r'\(IronPython\s*'
    r'[\d.]+\s*'
    r'\(([\d.]+)\) on ([\w.]+ [\d.]+(?: \(\d+-bit\))?)\)'
)

_pypy_sys_version_parser = re.compile(
    r'([\w.+]+)\s*'
    r'\(#?([^,]+),\s*([\w ]+),\s*([\w :]+)\)\s*'
    r'\[PyPy [^\]]+\]?')

_sys_version_cache = {}

eleza _sys_version(sys_version=Tupu):

    """ Returns a parsed version of Python's sys.version kama tuple
        (name, version, branch, revision, buildno, builddate, compiler)
        referring to the Python implementation name, version, branch,
        revision, build number, build date/time kama string na the compiler
        identification string.

        Note that unlike the Python sys.version, the returned value
        kila the Python version will always include the patchlevel (it
        defaults to '.0').

        The function returns empty strings kila tuple entries that
        cansio be determined.

        sys_version may be given to parse an alternative version
        string, e.g. ikiwa the version was read kutoka a different Python
        interpreter.

    """
    # Get the Python version
    ikiwa sys_version ni Tupu:
        sys_version = sys.version

    # Try the cache first
    result = _sys_version_cache.get(sys_version, Tupu)
    ikiwa result ni sio Tupu:
        rudisha result

    # Parse it
    ikiwa 'IronPython' kwenye sys_version:
        # IronPython
        name = 'IronPython'
        ikiwa sys_version.startswith('IronPython'):
            match = _ironpython_sys_version_parser.match(sys_version)
        isipokua:
            match = _ironpython26_sys_version_parser.match(sys_version)

        ikiwa match ni Tupu:
            ashiria ValueError(
                'failed to parse IronPython sys.version: %s' %
                repr(sys_version))

        version, alt_version, compiler = match.groups()
        buildno = ''
        builddate = ''

    lasivyo sys.platform.startswith('java'):
        # Jython
        name = 'Jython'
        match = _sys_version_parser.match(sys_version)
        ikiwa match ni Tupu:
            ashiria ValueError(
                'failed to parse Jython sys.version: %s' %
                repr(sys_version))
        version, buildno, builddate, buildtime, _ = match.groups()
        ikiwa builddate ni Tupu:
            builddate = ''
        compiler = sys.platform

    lasivyo "PyPy" kwenye sys_version:
        # PyPy
        name = "PyPy"
        match = _pypy_sys_version_parser.match(sys_version)
        ikiwa match ni Tupu:
            ashiria ValueError("failed to parse PyPy sys.version: %s" %
                             repr(sys_version))
        version, buildno, builddate, buildtime = match.groups()
        compiler = ""

    isipokua:
        # CPython
        match = _sys_version_parser.match(sys_version)
        ikiwa match ni Tupu:
            ashiria ValueError(
                'failed to parse CPython sys.version: %s' %
                repr(sys_version))
        version, buildno, builddate, buildtime, compiler = \
              match.groups()
        name = 'CPython'
        ikiwa builddate ni Tupu:
            builddate = ''
        lasivyo buildtime:
            builddate = builddate + ' ' + buildtime

    ikiwa hasattr(sys, '_git'):
        _, branch, revision = sys._git
    lasivyo hasattr(sys, '_mercurial'):
        _, branch, revision = sys._mercurial
    isipokua:
        branch = ''
        revision = ''

    # Add the patchlevel version ikiwa missing
    l = version.split('.')
    ikiwa len(l) == 2:
        l.append('0')
        version = '.'.join(l)

    # Build na cache the result
    result = (name, version, branch, revision, buildno, builddate, compiler)
    _sys_version_cache[sys_version] = result
    rudisha result

eleza python_implementation():

    """ Returns a string identifying the Python implementation.

        Currently, the following implementations are identified:
          'CPython' (C implementation of Python),
          'IronPython' (.NET implementation of Python),
          'Jython' (Java implementation of Python),
          'PyPy' (Python implementation of Python).

    """
    rudisha _sys_version()[0]

eleza python_version():

    """ Returns the Python version kama string 'major.minor.patchlevel'

        Note that unlike the Python sys.version, the returned value
        will always include the patchlevel (it defaults to 0).

    """
    rudisha _sys_version()[1]

eleza python_version_tuple():

    """ Returns the Python version kama tuple (major, minor, patchlevel)
        of strings.

        Note that unlike the Python sys.version, the returned value
        will always include the patchlevel (it defaults to 0).

    """
    rudisha tuple(_sys_version()[1].split('.'))

eleza python_branch():

    """ Returns a string identifying the Python implementation
        branch.

        For CPython this ni the SCM branch kutoka which the
        Python binary was built.

        If sio available, an empty string ni returned.

    """

    rudisha _sys_version()[2]

eleza python_revision():

    """ Returns a string identifying the Python implementation
        revision.

        For CPython this ni the SCM revision kutoka which the
        Python binary was built.

        If sio available, an empty string ni returned.

    """
    rudisha _sys_version()[3]

eleza python_build():

    """ Returns a tuple (buildno, builddate) stating the Python
        build number na date kama strings.

    """
    rudisha _sys_version()[4:6]

eleza python_compiler():

    """ Returns a string identifying the compiler used kila compiling
        Python.

    """
    rudisha _sys_version()[6]

### The Opus Magnum of platform strings :-)

_platform_cache = {}

eleza platform(aliased=0, terse=0):

    """ Returns a single string identifying the underlying platform
        ukijumuisha kama much useful information kama possible (but no more :).

        The output ni intended to be human readable rather than
        machine parseable. It may look different on different
        platforms na this ni intended.

        If "aliased" ni true, the function will use aliases for
        various platforms that report system names which differ from
        their common names, e.g. SunOS will be reported as
        Solaris. The system_alias() function ni used to implement
        this.

        Setting terse to true causes the function to rudisha only the
        absolute minimum information needed to identify the platform.

    """
    result = _platform_cache.get((aliased, terse), Tupu)
    ikiwa result ni sio Tupu:
        rudisha result

    # Get uname information na then apply platform specific cosmetics
    # to it...
    system, node, release, version, machine, processor = uname()
    ikiwa machine == processor:
        processor = ''
    ikiwa aliased:
        system, release, version = system_alias(system, release, version)

    ikiwa system == 'Darwin':
        # macOS (darwin kernel)
        macos_release = mac_ver()[0]
        ikiwa macos_release:
            system = 'macOS'
            release = macos_release

    ikiwa system == 'Windows':
        # MS platforms
        rel, vers, csd, ptype = win32_ver(version)
        ikiwa terse:
            platform = _platform(system, release)
        isipokua:
            platform = _platform(system, release, version, csd)

    lasivyo system kwenye ('Linux',):
        # check kila libc vs. glibc
        libcname, libcversion = libc_ver(sys.executable)
        platform = _platform(system, release, machine, processor,
                             'with',
                             libcname+libcversion)
    lasivyo system == 'Java':
        # Java platforms
        r, v, vminfo, (os_name, os_version, os_arch) = java_ver()
        ikiwa terse ama sio os_name:
            platform = _platform(system, release, version)
        isipokua:
            platform = _platform(system, release, version,
                                 'on',
                                 os_name, os_version, os_arch)

    isipokua:
        # Generic handler
        ikiwa terse:
            platform = _platform(system, release)
        isipokua:
            bits, linkage = architecture(sys.executable)
            platform = _platform(system, release, machine,
                                 processor, bits, linkage)

    _platform_cache[(aliased, terse)] = platform
    rudisha platform

### Command line interface

ikiwa __name__ == '__main__':
    # Default ni to andika the aliased verbose platform string
    terse = ('terse' kwenye sys.argv ama '--terse' kwenye sys.argv)
    aliased = (sio 'nonaliased' kwenye sys.argv na sio '--nonaliased' kwenye sys.argv)
    andika(platform(aliased, terse))
    sys.exit(0)
