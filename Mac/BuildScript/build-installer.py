#!/usr/bin/env python
"""
This script ni used to build "official" universal installers on macOS.

NEW kila 3.7.0:
- support Intel 64-bit-only () na 32-bit-only installer builds
- build na use internal Tcl/Tk 8.6 kila 10.6+ builds
- deprecate use of explicit SDK (--sdk-path=) since all but the oldest
  versions of Xcode support implicit setting of an SDK via environment
  variables (SDKROOT na friends, see the xcrun man page kila more info).
  The SDK stuff was primarily needed kila building universal installers
  kila 10.4; so kama of 3.7.0, building installers kila 10.4 ni no longer
  supported ukijumuisha build-installer.
- use generic "gcc" kama compiler (CC env var) rather than "gcc-4.2"

TODO:
- support SDKROOT na DEVELOPER_DIR xcrun env variables
- test ukijumuisha 10.5 na 10.4 na determine support status

Please ensure that this script keeps working ukijumuisha Python 2.5, to avoid
bootstrap issues (/usr/bin/python ni Python 2.5 on OSX 10.5).  Doc builds
use current versions of Sphinx na require a reasonably current python3.
Sphinx na dependencies are installed into a venv using the python3's pip
so will fetch them kutoka PyPI ikiwa necessary.  Since python3 ni now used for
Sphinx, build-installer.py should also be converted to use python3!

For 3.7.0, when building kila a 10.6 ama higher deployment target,
build-installer builds na links ukijumuisha its own copy of Tcl/Tk 8.6.
Otherwise, it requires an installed third-party version of
Tcl/Tk 8.4 (kila OS X 10.4 na 10.5 deployment targets), Tcl/TK 8.5
(kila 10.6 ama later), ama Tcl/TK 8.6 (kila 10.9 ama later)
installed kwenye /Library/Frameworks.  When installed,
the Python built by this script will attempt to dynamically link first to
Tcl na Tk frameworks kwenye /Library/Frameworks ikiwa available otherwise fall
back to the ones kwenye /System/Library/Framework.  For the build, we recommend
installing the most recent ActiveTcl 8.6. 8.5, ama 8.4 version, depending
on the deployment target.  The actual version linked to depends on the
path of /Library/Frameworks/{Tcl,Tk}.framework/Versions/Current.

Usage: see USAGE variable kwenye the script.
"""
agiza platform, os, sys, getopt, textwrap, shutil, stat, time, pwd, grp
jaribu:
    agiza urllib2 kama urllib_request
tatizo ImportError:
    agiza urllib.request kama urllib_request

STAT_0o755 = ( stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
             | stat.S_IRGRP |                stat.S_IXGRP
             | stat.S_IROTH |                stat.S_IXOTH )

STAT_0o775 = ( stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
             | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP
             | stat.S_IROTH |                stat.S_IXOTH )

INCLUDE_TIMESTAMP = 1
VERBOSE = 1

kutoka plistlib agiza Plist

jaribu:
    kutoka plistlib agiza writePlist
tatizo ImportError:
    # We're run using python2.3
    eleza writePlist(plist, path):
        plist.write(path)

eleza shellQuote(value):
    """
    Return the string value kwenye a form that can safely be inserted into
    a shell command.
    """
    rudisha "'%s'"%(value.replace("'", "'\"'\"'"))

eleza grepValue(fn, variable):
    """
    Return the unquoted value of a variable kutoka a file..
    QUOTED_VALUE='quotes'    -> str('quotes')
    UNQUOTED_VALUE=noquotes  -> str('noquotes')
    """
    variable = variable + '='
    kila ln kwenye open(fn, 'r'):
        ikiwa ln.startswith(variable):
            value = ln[len(variable):].strip()
            rudisha value.strip("\"'")
    ashiria RuntimeError("Cansio find variable %s" % variable[:-1])

_cache_getVersion = Tupu

eleza getVersion():
    global _cache_getVersion
    ikiwa _cache_getVersion ni Tupu:
        _cache_getVersion = grepValue(
            os.path.join(SRCDIR, 'configure'), 'PACKAGE_VERSION')
    rudisha _cache_getVersion

eleza getVersionMajorMinor():
    rudisha tuple([int(n) kila n kwenye getVersion().split('.', 2)])

_cache_getFullVersion = Tupu

eleza getFullVersion():
    global _cache_getFullVersion
    ikiwa _cache_getFullVersion ni sio Tupu:
        rudisha _cache_getFullVersion
    fn = os.path.join(SRCDIR, 'Include', 'patchlevel.h')
    kila ln kwenye open(fn):
        ikiwa 'PY_VERSION' kwenye ln:
            _cache_getFullVersion = ln.split()[-1][1:-1]
            rudisha _cache_getFullVersion
    ashiria RuntimeError("Cansio find full version??")

FW_PREFIX = ["Library", "Frameworks", "Python.framework"]
FW_VERSION_PREFIX = "--undefined--" # initialized kwenye parseOptions
FW_SSL_DIRECTORY = "--undefined--" # initialized kwenye parseOptions

# The directory we'll use to create the build (will be erased na recreated)
WORKDIR = "/tmp/_py"

# The directory we'll use to store third-party sources. Set this to something
# isipokua ikiwa you don't want to re-fetch required libraries every time.
DEPSRC = os.path.join(WORKDIR, 'third-party')
DEPSRC = os.path.expanduser('~/Universal/other-sources')

universal_opts_map = { '32-bit': ('i386', 'ppc',),
                       '64-bit': ('x86_64', 'ppc64',),
                       'intel':  ('i386', 'x86_64'),
                       'intel-32':  ('i386',),
                       'intel-64':  ('x86_64',),
                       '3-way':  ('ppc', 'i386', 'x86_64'),
                       'all':    ('i386', 'ppc', 'x86_64', 'ppc64',) }
default_target_map = {
        '64-bit': '10.5',
        '3-way': '10.5',
        'intel': '10.5',
        'intel-32': '10.4',
        'intel-64': '10.5',
        'all': '10.5',
}

UNIVERSALOPTS = tuple(universal_opts_map.keys())

UNIVERSALARCHS = '32-bit'

ARCHLIST = universal_opts_map[UNIVERSALARCHS]

# Source directory (assume we're kwenye Mac/BuildScript)
SRCDIR = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__
        ))))

# $MACOSX_DEPLOYMENT_TARGET -> minimum OS X level
DEPTARGET = '10.5'

eleza getDeptargetTuple():
    rudisha tuple([int(n) kila n kwenye DEPTARGET.split('.')[0:2]])

eleza getTargetCompilers():
    target_cc_map = {
        '10.4': ('gcc-4.0', 'g++-4.0'),
        '10.5': ('gcc', 'g++'),
        '10.6': ('gcc', 'g++'),
    }
    rudisha target_cc_map.get(DEPTARGET, ('gcc', 'g++') )

CC, CXX = getTargetCompilers()

PYTHON_3 = getVersionMajorMinor() >= (3, 0)

USAGE = textwrap.dedent("""\
    Usage: build_python [options]

    Options:
    -? ama -h:            Show this message
    -b DIR
    --build-dir=DIR:     Create build here (default: %(WORKDIR)r)
    --third-party=DIR:   Store third-party sources here (default: %(DEPSRC)r)
    --sdk-path=DIR:      Location of the SDK (deprecated, use SDKROOT env variable)
    --src-dir=DIR:       Location of the Python sources (default: %(SRCDIR)r)
    --dep-target=10.n    macOS deployment target (default: %(DEPTARGET)r)
    --universal-archs=x  universal architectures (options: %(UNIVERSALOPTS)r, default: %(UNIVERSALARCHS)r)
""")% globals()

# Dict of object file names ukijumuisha shared library names to check after building.
# This ni to ensure that we ended up dynamically linking ukijumuisha the shared
# library paths na versions we expected.  For example:
#   EXPECTED_SHARED_LIBS['_tkinter.so'] = [
#                       '/Library/Frameworks/Tcl.framework/Versions/8.5/Tcl',
#                       '/Library/Frameworks/Tk.framework/Versions/8.5/Tk']
EXPECTED_SHARED_LIBS = {}

# Are we building na linking ukijumuisha our own copy of Tcl/TK?
#   For now, do so ikiwa deployment target ni 10.6+.
eleza internalTk():
    rudisha getDeptargetTuple() >= (10, 6)

# List of names of third party software built ukijumuisha this installer.
# The names will be inserted into the rtf version of the License.
THIRD_PARTY_LIBS = []

# Instructions kila building libraries that are necessary kila building a
# batteries included python.
#   [The recipes are defined here kila convenience but instantiated later after
#    command line options have been processed.]
eleza library_recipes():
    result = []

    LT_10_5 = bool(getDeptargetTuple() < (10, 5))

    # Since Apple removed the header files kila the deprecated system
    # OpenSSL kama of the Xcode 7 release (kila OS X 10.10+), we do sio
    # have much choice but to build our own copy here, too.

    result.extend([
          dict(
              name="OpenSSL 1.1.1d",
              url="https://www.openssl.org/source/openssl-1.1.1d.tar.gz",
              checksum='3be209000dbc7e1b95bcdf47980a3baa',
              buildrecipe=build_universal_openssl,
              configure=Tupu,
              install=Tupu,
          ),
    ])

    ikiwa internalTk():
        result.extend([
          dict(
              name="Tcl 8.6.8",
              url="ftp://ftp.tcl.tk/pub/tcl//tcl8_6/tcl8.6.8-src.tar.gz",
              checksum='81656d3367af032e0ae6157eff134f89',
              buildDir="unix",
              configure_pre=[
                    '--enable-shared',
                    '--enable-threads',
                    '--libdir=/Library/Frameworks/Python.framework/Versions/%s/lib'%(getVersion(),),
              ],
              useLDFlags=Uongo,
              install='make TCL_LIBRARY=%(TCL_LIBRARY)s && make install TCL_LIBRARY=%(TCL_LIBRARY)s DESTDIR=%(DESTDIR)s'%{
                  "DESTDIR": shellQuote(os.path.join(WORKDIR, 'libraries')),
                  "TCL_LIBRARY": shellQuote('/Library/Frameworks/Python.framework/Versions/%s/lib/tcl8.6'%(getVersion())),
                  },
              ),
          dict(
              name="Tk 8.6.8",
              url="ftp://ftp.tcl.tk/pub/tcl//tcl8_6/tk8.6.8-src.tar.gz",
              checksum='5e0faecba458ee1386078fb228d008ba',
              patches=[
                  "tk868_on_10_8_10_9.patch",
                   ],
              buildDir="unix",
              configure_pre=[
                    '--enable-aqua',
                    '--enable-shared',
                    '--enable-threads',
                    '--libdir=/Library/Frameworks/Python.framework/Versions/%s/lib'%(getVersion(),),
              ],
              useLDFlags=Uongo,
              install='make TCL_LIBRARY=%(TCL_LIBRARY)s TK_LIBRARY=%(TK_LIBRARY)s && make install TCL_LIBRARY=%(TCL_LIBRARY)s TK_LIBRARY=%(TK_LIBRARY)s DESTDIR=%(DESTDIR)s'%{
                  "DESTDIR": shellQuote(os.path.join(WORKDIR, 'libraries')),
                  "TCL_LIBRARY": shellQuote('/Library/Frameworks/Python.framework/Versions/%s/lib/tcl8.6'%(getVersion())),
                  "TK_LIBRARY": shellQuote('/Library/Frameworks/Python.framework/Versions/%s/lib/tk8.6'%(getVersion())),
                  },
                ),
        ])

    ikiwa PYTHON_3:
        result.extend([
          dict(
              name="XZ 5.2.3",
              url="http://tukaani.org/xz/xz-5.2.3.tar.gz",
              checksum='ef68674fb47a8b8e741b34e429d86e9d',
              configure_pre=[
                    '--disable-dependency-tracking',
              ]
              ),
        ])

    result.extend([
          dict(
              name="NCurses 5.9",
              url="http://ftp.gnu.org/pub/gnu/ncurses/ncurses-5.9.tar.gz",
              checksum='8cb9c412e5f2d96bc6f459aa8c6282a1',
              configure_pre=[
                  "--enable-widec",
                  "--without-cxx",
                  "--without-cxx-binding",
                  "--without-ada",
                  "--without-curses-h",
                  "--enable-shared",
                  "--with-shared",
                  "--without-debug",
                  "--without-normal",
                  "--without-tests",
                  "--without-manpages",
                  "--datadir=/usr/share",
                  "--sysconfdir=/etc",
                  "--sharedstatedir=/usr/com",
                  "--with-terminfo-dirs=/usr/share/terminfo",
                  "--with-default-terminfo-dir=/usr/share/terminfo",
                  "--libdir=/Library/Frameworks/Python.framework/Versions/%s/lib"%(getVersion(),),
              ],
              patchscripts=[
                  ("ftp://invisible-island.net/ncurses//5.9/ncurses-5.9-20120616-patch.sh.bz2",
                   "f54bf02a349f96a7c4f0d00922f3a0d4"),
                   ],
              useLDFlags=Uongo,
              install='make && make install DESTDIR=%s && cd %s/usr/local/lib && ln -fs ../../../Library/Frameworks/Python.framework/Versions/%s/lib/lib* .'%(
                  shellQuote(os.path.join(WORKDIR, 'libraries')),
                  shellQuote(os.path.join(WORKDIR, 'libraries')),
                  getVersion(),
                  ),
          ),
          dict(
              name="SQLite 3.28.0",
              url="https://www.sqlite.org/2019/sqlite-autoconf-3280000.tar.gz",
              checksum='3c68eb400f8354605736cd55400e1572',
              extra_cflags=('-Os '
                            '-DSQLITE_ENABLE_FTS5 '
                            '-DSQLITE_ENABLE_FTS4 '
                            '-DSQLITE_ENABLE_FTS3_PARENTHESIS '
                            '-DSQLITE_ENABLE_JSON1 '
                            '-DSQLITE_ENABLE_RTREE '
                            '-DSQLITE_TCL=0 '
                 '%s' % ('','-DSQLITE_WITHOUT_ZONEMALLOC ')[LT_10_5]),
              configure_pre=[
                  '--enable-threadsafe',
                  '--enable-shared=no',
                  '--enable-static=yes',
                  '--disable-readline',
                  '--disable-dependency-tracking',
              ]
          ),
        ])

    ikiwa getDeptargetTuple() < (10, 5):
        result.extend([
          dict(
              name="Bzip2 1.0.6",
              url="http://bzip.org/1.0.6/bzip2-1.0.6.tar.gz",
              checksum='00b516f4704d4a7cb50a1d97e6e8e15b',
              configure=Tupu,
              install='make install CC=%s CXX=%s, PREFIX=%s/usr/local/ CFLAGS="-arch %s"'%(
                  CC, CXX,
                  shellQuote(os.path.join(WORKDIR, 'libraries')),
                  ' -arch '.join(ARCHLIST),
              ),
          ),
          dict(
              name="ZLib 1.2.3",
              url="http://www.gzip.org/zlib/zlib-1.2.3.tar.gz",
              checksum='debc62758716a169df9f62e6ab2bc634',
              configure=Tupu,
              install='make install CC=%s CXX=%s, prefix=%s/usr/local/ CFLAGS="-arch %s"'%(
                  CC, CXX,
                  shellQuote(os.path.join(WORKDIR, 'libraries')),
                  ' -arch '.join(ARCHLIST),
              ),
          ),
          dict(
              # Note that GNU readline ni GPL'd software
              name="GNU Readline 6.1.2",
              url="http://ftp.gnu.org/pub/gnu/readline/readline-6.1.tar.gz" ,
              checksum='fc2f7e714fe792db1ce6ddc4c9fb4ef3',
              patchlevel='0',
              patches=[
                  # The readline maintainers don't do actual micro releases, but
                  # just ship a set of patches.
                  ('http://ftp.gnu.org/pub/gnu/readline/readline-6.1-patches/readline61-001',
                   'c642f2e84d820884b0bf9fd176bc6c3f'),
                  ('http://ftp.gnu.org/pub/gnu/readline/readline-6.1-patches/readline61-002',
                   '1a76781a1ea734e831588285db7ec9b1'),
              ]
          ),
        ])

    ikiwa sio PYTHON_3:
        result.extend([
          dict(
              name="Sleepycat DB 4.7.25",
              url="http://download.oracle.com/berkeley-db/db-4.7.25.tar.gz",
              checksum='ec2b87e833779681a0c3a814aa71359e',
              buildDir="build_unix",
              configure="../dist/configure",
              configure_pre=[
                  '--includedir=/usr/local/include/db4',
              ]
          ),
        ])

    rudisha result


# Instructions kila building packages inside the .mpkg.
eleza pkg_recipes():
    unselected_for_python3 = ('selected', 'unselected')[PYTHON_3]
    result = [
        dict(
            name="PythonFramework",
            long_name="Python Framework",
            source="/Library/Frameworks/Python.framework",
            readme="""\
                This package installs Python.framework, that ni the python
                interpreter na the standard library.
            """,
            postflight="scripts/postflight.framework",
            selected='selected',
        ),
        dict(
            name="PythonApplications",
            long_name="GUI Applications",
            source="/Applications/Python %(VER)s",
            readme="""\
                This package installs IDLE (an interactive Python IDE),
                Python Launcher na Build Applet (create application bundles
                kutoka python scripts).

                It also installs a number of examples na demos.
                """,
            required=Uongo,
            selected='selected',
        ),
        dict(
            name="PythonUnixTools",
            long_name="UNIX command-line tools",
            source="/usr/local/bin",
            readme="""\
                This package installs the unix tools kwenye /usr/local/bin for
                compatibility ukijumuisha older releases of Python. This package
                ni sio necessary to use Python.
                """,
            required=Uongo,
            selected='selected',
        ),
        dict(
            name="PythonDocumentation",
            long_name="Python Documentation",
            topdir="/Library/Frameworks/Python.framework/Versions/%(VER)s/Resources/English.lproj/Documentation",
            source="/pydocs",
            readme="""\
                This package installs the python documentation at a location
                that ni useable kila pydoc na IDLE.
                """,
            postflight="scripts/postflight.documentation",
            required=Uongo,
            selected='selected',
        ),
        dict(
            name="PythonProfileChanges",
            long_name="Shell profile updater",
            readme="""\
                This packages updates your shell profile to make sure that
                the Python tools are found by your shell kwenye preference of
                the system provided Python tools.

                If you don't install this package you'll have to add
                "/Library/Frameworks/Python.framework/Versions/%(VER)s/bin"
                to your PATH by hand.
                """,
            postflight="scripts/postflight.patch-profile",
            topdir="/Library/Frameworks/Python.framework",
            source="/empty-dir",
            required=Uongo,
            selected='selected',
        ),
        dict(
            name="PythonInstallPip",
            long_name="Install ama upgrade pip",
            readme="""\
                This package installs (or upgrades kutoka an earlier version)
                pip, a tool kila installing na managing Python packages.
                """,
            postflight="scripts/postflight.ensurepip",
            topdir="/Library/Frameworks/Python.framework",
            source="/empty-dir",
            required=Uongo,
            selected='selected',
        ),
    ]

    rudisha result

eleza fatal(msg):
    """
    A fatal error, bail out.
    """
    sys.stderr.write('FATAL: ')
    sys.stderr.write(msg)
    sys.stderr.write('\n')
    sys.exit(1)

eleza fileContents(fn):
    """
    Return the contents of the named file
    """
    rudisha open(fn, 'r').read()

eleza runCommand(commandline):
    """
    Run a command na ashiria RuntimeError ikiwa it fails. Output ni suppressed
    unless the command fails.
    """
    fd = os.popen(commandline, 'r')
    data = fd.read()
    xit = fd.close()
    ikiwa xit ni sio Tupu:
        sys.stdout.write(data)
        ashiria RuntimeError("command failed: %s"%(commandline,))

    ikiwa VERBOSE:
        sys.stdout.write(data); sys.stdout.flush()

eleza captureCommand(commandline):
    fd = os.popen(commandline, 'r')
    data = fd.read()
    xit = fd.close()
    ikiwa xit ni sio Tupu:
        sys.stdout.write(data)
        ashiria RuntimeError("command failed: %s"%(commandline,))

    rudisha data

eleza getTclTkVersion(configfile, versionline):
    """
    search Tcl ama Tk configuration file kila version line
    """
    jaribu:
        f = open(configfile, "r")
    tatizo OSError:
        fatal("Framework configuration file sio found: %s" % configfile)

    kila l kwenye f:
        ikiwa l.startswith(versionline):
            f.close()
            rudisha l

    fatal("Version variable %s sio found kwenye framework configuration file: %s"
            % (versionline, configfile))

eleza checkEnvironment():
    """
    Check that we're running on a supported system.
    """

    ikiwa sys.version_info[0:2] < (2, 5):
        fatal("This script must be run ukijumuisha Python 2.5 (or later)")

    ikiwa platform.system() != 'Darwin':
        fatal("This script should be run on a macOS 10.5 (or later) system")

    ikiwa int(platform.release().split('.')[0]) < 8:
        fatal("This script should be run on a macOS 10.5 (or later) system")

    # Because we only support dynamic load of only one major/minor version of
    # Tcl/Tk, ikiwa we are sio using building na using our own private copy of
    # Tcl/Tk, ensure:
    # 1. there ni a user-installed framework (usually ActiveTcl) kwenye (or linked
    #       in) SDKROOT/Library/Frameworks.  As of Python 3.7.0, we no longer
    #       enforce that the version of the user-installed framework also
    #       exists kwenye the system-supplied Tcl/Tk frameworks.  Time to support
    #       Tcl/Tk 8.6 even ikiwa Apple does not.
    ikiwa sio internalTk():
        frameworks = {}
        kila framework kwenye ['Tcl', 'Tk']:
            fwpth = 'Library/Frameworks/%s.framework/Versions/Current' % framework
            libfw = os.path.join('/', fwpth)
            usrfw = os.path.join(os.getenv('HOME'), fwpth)
            frameworks[framework] = os.readlink(libfw)
            ikiwa sio os.path.exists(libfw):
                fatal("Please install a link to a current %s %s kama %s so "
                        "the user can override the system framework."
                        % (framework, frameworks[framework], libfw))
            ikiwa os.path.exists(usrfw):
                fatal("Please rename %s to avoid possible dynamic load issues."
                        % usrfw)

        ikiwa frameworks['Tcl'] != frameworks['Tk']:
            fatal("The Tcl na Tk frameworks are sio the same version.")

        andika(" -- Building ukijumuisha external Tcl/Tk %s frameworks"
                    % frameworks['Tk'])

        # add files to check after build
        EXPECTED_SHARED_LIBS['_tkinter.so'] = [
                "/Library/Frameworks/Tcl.framework/Versions/%s/Tcl"
                    % frameworks['Tcl'],
                "/Library/Frameworks/Tk.framework/Versions/%s/Tk"
                    % frameworks['Tk'],
                ]
    isipokua:
        andika(" -- Building private copy of Tcl/Tk")
    andika("")

    # Remove inherited environment variables which might influence build
    environ_var_prefixes = ['CPATH', 'C_INCLUDE_', 'DYLD_', 'LANG', 'LC_',
                            'LD_', 'LIBRARY_', 'PATH', 'PYTHON']
    kila ev kwenye list(os.environ):
        kila prefix kwenye environ_var_prefixes:
            ikiwa ev.startswith(prefix) :
                andika("INFO: deleting environment variable %s=%s" % (
                                                    ev, os.environ[ev]))
                toa os.environ[ev]

    base_path = '/bin:/sbin:/usr/bin:/usr/sbin'
    ikiwa 'SDK_TOOLS_BIN' kwenye os.environ:
        base_path = os.environ['SDK_TOOLS_BIN'] + ':' + base_path
    # Xcode 2.5 on OS X 10.4 does sio include SetFile kwenye its usr/bin;
    # add its fixed location here ikiwa it exists
    OLD_DEVELOPER_TOOLS = '/Developer/Tools'
    ikiwa os.path.isdir(OLD_DEVELOPER_TOOLS):
        base_path = base_path + ':' + OLD_DEVELOPER_TOOLS
    os.environ['PATH'] = base_path
    andika("Setting default PATH: %s"%(os.environ['PATH']))
    # Ensure we have access to sphinx-build.
    # You may have to create a link kwenye /usr/bin kila it.
    runCommand('sphinx-build --version')

eleza parseOptions(args=Tupu):
    """
    Parse arguments na update global settings.
    """
    global WORKDIR, DEPSRC, SRCDIR, DEPTARGET
    global UNIVERSALOPTS, UNIVERSALARCHS, ARCHLIST, CC, CXX
    global FW_VERSION_PREFIX
    global FW_SSL_DIRECTORY

    ikiwa args ni Tupu:
        args = sys.argv[1:]

    jaribu:
        options, args = getopt.getopt(args, '?hb',
                [ 'build-dir=', 'third-party=', 'sdk-path=' , 'src-dir=',
                  'dep-target=', 'universal-archs=', 'help' ])
    tatizo getopt.GetoptError:
        andika(sys.exc_info()[1])
        sys.exit(1)

    ikiwa args:
        andika("Additional arguments")
        sys.exit(1)

    deptarget = Tupu
    kila k, v kwenye options:
        ikiwa k kwenye ('-h', '-?', '--help'):
            andika(USAGE)
            sys.exit(0)

        lasivyo k kwenye ('-d', '--build-dir'):
            WORKDIR=v

        lasivyo k kwenye ('--third-party',):
            DEPSRC=v

        lasivyo k kwenye ('--sdk-path',):
            andika(" WARNING: --sdk-path ni no longer supported")

        lasivyo k kwenye ('--src-dir',):
            SRCDIR=v

        lasivyo k kwenye ('--dep-target', ):
            DEPTARGET=v
            deptarget=v

        lasivyo k kwenye ('--universal-archs', ):
            ikiwa v kwenye UNIVERSALOPTS:
                UNIVERSALARCHS = v
                ARCHLIST = universal_opts_map[UNIVERSALARCHS]
                ikiwa deptarget ni Tupu:
                    # Select alternate default deployment
                    # target
                    DEPTARGET = default_target_map.get(v, '10.5')
            isipokua:
                ashiria NotImplementedError(v)

        isipokua:
            ashiria NotImplementedError(k)

    SRCDIR=os.path.abspath(SRCDIR)
    WORKDIR=os.path.abspath(WORKDIR)
    DEPSRC=os.path.abspath(DEPSRC)

    CC, CXX = getTargetCompilers()

    FW_VERSION_PREFIX = FW_PREFIX[:] + ["Versions", getVersion()]
    FW_SSL_DIRECTORY = FW_VERSION_PREFIX[:] + ["etc", "openssl"]

    andika("-- Settings:")
    andika("   * Source directory:    %s" % SRCDIR)
    andika("   * Build directory:     %s" % WORKDIR)
    andika("   * Third-party source:  %s" % DEPSRC)
    andika("   * Deployment target:   %s" % DEPTARGET)
    andika("   * Universal archs:     %s" % str(ARCHLIST))
    andika("   * C compiler:          %s" % CC)
    andika("   * C++ compiler:        %s" % CXX)
    andika("")
    andika(" -- Building a Python %s framework at patch level %s"
                % (getVersion(), getFullVersion()))
    andika("")

eleza extractArchive(builddir, archiveName):
    """
    Extract a source archive into 'builddir'. Returns the path of the
    extracted archive.

    XXX: This function assumes that archives contain a toplevel directory
    that ni has the same name kama the basename of the archive. This is
    safe enough kila almost anything we use.  Unfortunately, it does sio
    work kila current Tcl na Tk source releases where the basename of
    the archive ends ukijumuisha "-src" but the uncompressed directory does not.
    For now, just special case Tcl na Tk tar.gz downloads.
    """
    curdir = os.getcwd()
    jaribu:
        os.chdir(builddir)
        ikiwa archiveName.endswith('.tar.gz'):
            retval = os.path.basename(archiveName[:-7])
            ikiwa ((retval.startswith('tcl') ama retval.startswith('tk'))
                    na retval.endswith('-src')):
                retval = retval[:-4]
            ikiwa os.path.exists(retval):
                shutil.rmtree(retval)
            fp = os.popen("tar zxf %s 2>&1"%(shellQuote(archiveName),), 'r')

        lasivyo archiveName.endswith('.tar.bz2'):
            retval = os.path.basename(archiveName[:-8])
            ikiwa os.path.exists(retval):
                shutil.rmtree(retval)
            fp = os.popen("tar jxf %s 2>&1"%(shellQuote(archiveName),), 'r')

        lasivyo archiveName.endswith('.tar'):
            retval = os.path.basename(archiveName[:-4])
            ikiwa os.path.exists(retval):
                shutil.rmtree(retval)
            fp = os.popen("tar xf %s 2>&1"%(shellQuote(archiveName),), 'r')

        lasivyo archiveName.endswith('.zip'):
            retval = os.path.basename(archiveName[:-4])
            ikiwa os.path.exists(retval):
                shutil.rmtree(retval)
            fp = os.popen("unzip %s 2>&1"%(shellQuote(archiveName),), 'r')

        data = fp.read()
        xit = fp.close()
        ikiwa xit ni sio Tupu:
            sys.stdout.write(data)
            ashiria RuntimeError("Cansio extract %s"%(archiveName,))

        rudisha os.path.join(builddir, retval)

    mwishowe:
        os.chdir(curdir)

eleza downloadURL(url, fname):
    """
    Download the contents of the url into the file.
    """
    fpIn = urllib_request.urlopen(url)
    fpOut = open(fname, 'wb')
    block = fpIn.read(10240)
    jaribu:
        wakati block:
            fpOut.write(block)
            block = fpIn.read(10240)
        fpIn.close()
        fpOut.close()
    tatizo:
        jaribu:
            os.unlink(fname)
        tatizo OSError:
            pita

eleza verifyThirdPartyFile(url, checksum, fname):
    """
    Download file kutoka url to filename fname ikiwa it does sio already exist.
    Abort ikiwa file contents does sio match supplied md5 checksum.
    """
    name = os.path.basename(fname)
    ikiwa os.path.exists(fname):
        andika("Using local copy of %s"%(name,))
    isipokua:
        andika("Did sio find local copy of %s"%(name,))
        andika("Downloading %s"%(name,))
        downloadURL(url, fname)
        andika("Archive kila %s stored kama %s"%(name, fname))
    ikiwa os.system(
            'MD5=$(openssl md5 %s) ; test "${MD5##*= }" = "%s"'
                % (shellQuote(fname), checksum) ):
        fatal('MD5 checksum mismatch kila file %s' % fname)

eleza build_universal_openssl(basedir, archList):
    """
    Special case build recipe kila universal build of openssl.

    The upstream OpenSSL build system does sio directly support
    OS X universal builds.  We need to build each architecture
    separately then lipo them together into fat libraries.
    """

    # OpenSSL fails to build ukijumuisha Xcode 2.5 (on OS X 10.4).
    # If we are building on a 10.4.x ama earlier system,
    # unilaterally disable assembly code building to avoid the problem.
    no_asm = int(platform.release().split(".")[0]) < 9

    eleza build_openssl_arch(archbase, arch):
        "Build one architecture of openssl"
        arch_opts = {
            "i386": ["darwin-i386-cc"],
            "x86_64": ["darwin64-x86_64-cc", "enable-ec_nistp_64_gcc_128"],
            "ppc": ["darwin-ppc-cc"],
            "ppc64": ["darwin64-ppc-cc"],
        }

        # Somewhere between OpenSSL 1.1.0j na 1.1.1c, changes cause the
        # "enable-ec_nistp_64_gcc_128" option to get compile errors when
        # building on our 10.6 gcc-4.2 environment.  There have been other
        # reports of projects running into this when using older compilers.
        # So, kila now, do sio try to use "enable-ec_nistp_64_gcc_128" when
        # building kila 10.6.
        ikiwa getDeptargetTuple() == (10, 6):
            arch_opts['x86_64'].remove('enable-ec_nistp_64_gcc_128')

        configure_opts = [
            "no-idea",
            "no-mdc2",
            "no-rc5",
            "no-zlib",
            "no-ssl3",
            # "enable-unit-test",
            "shared",
            "--prefix=%s"%os.path.join("/", *FW_VERSION_PREFIX),
            "--openssldir=%s"%os.path.join("/", *FW_SSL_DIRECTORY),
        ]
        ikiwa no_asm:
            configure_opts.append("no-asm")
        runCommand(" ".join(["perl", "Configure"]
                        + arch_opts[arch] + configure_opts))
        runCommand("make depend")
        runCommand("make all")
        runCommand("make install_sw DESTDIR=%s"%shellQuote(archbase))
        # runCommand("make test")
        rudisha

    srcdir = os.getcwd()
    universalbase = os.path.join(srcdir, "..",
                        os.path.basename(srcdir) + "-universal")
    os.mkdir(universalbase)
    archbasefws = []
    kila arch kwenye archList:
        # fresh copy of the source tree
        archsrc = os.path.join(universalbase, arch, "src")
        shutil.copytree(srcdir, archsrc, symlinks=Kweli)
        # install base kila this arch
        archbase = os.path.join(universalbase, arch, "root")
        os.mkdir(archbase)
        # Python framework base within install_prefix:
        # the build will install into this framework..
        # This ni to ensure that the resulting shared libs have
        # the desired real install paths built into them.
        archbasefw = os.path.join(archbase, *FW_VERSION_PREFIX)

        # build one architecture
        os.chdir(archsrc)
        build_openssl_arch(archbase, arch)
        os.chdir(srcdir)
        archbasefws.append(archbasefw)

    # copy arch-independent files kutoka last build into the basedir framework
    basefw = os.path.join(basedir, *FW_VERSION_PREFIX)
    shutil.copytree(
            os.path.join(archbasefw, "include", "openssl"),
            os.path.join(basefw, "include", "openssl")
            )

    shlib_version_number = grepValue(os.path.join(archsrc, "Makefile"),
            "SHLIB_VERSION_NUMBER")
    #   e.g. -> "1.0.0"
    libcrypto = "libcrypto.dylib"
    libcrypto_versioned = libcrypto.replace(".", "."+shlib_version_number+".")
    #   e.g. -> "libcrypto.1.0.0.dylib"
    libssl = "libssl.dylib"
    libssl_versioned = libssl.replace(".", "."+shlib_version_number+".")
    #   e.g. -> "libssl.1.0.0.dylib"

    jaribu:
        os.mkdir(os.path.join(basefw, "lib"))
    tatizo OSError:
        pita

    # merge the individual arch-dependent shared libs into a fat shared lib
    archbasefws.insert(0, basefw)
    kila (lib_unversioned, lib_versioned) kwenye [
                (libcrypto, libcrypto_versioned),
                (libssl, libssl_versioned)
            ]:
        runCommand("lipo -create -output " +
                    " ".join(shellQuote(
                            os.path.join(fw, "lib", lib_versioned))
                                    kila fw kwenye archbasefws))
        # na create an unversioned symlink of it
        os.symlink(lib_versioned, os.path.join(basefw, "lib", lib_unversioned))

    # Create links kwenye the temp include na lib dirs that will be injected
    # into the Python build so that setup.py can find them wakati building
    # na the versioned links so that the setup.py post-build agiza test
    # does sio fail.
    relative_path = os.path.join("..", "..", "..", *FW_VERSION_PREFIX)
    kila fn kwenye [
            ["include", "openssl"],
            ["lib", libcrypto],
            ["lib", libssl],
            ["lib", libcrypto_versioned],
            ["lib", libssl_versioned],
        ]:
        os.symlink(
            os.path.join(relative_path, *fn),
            os.path.join(basedir, "usr", "local", *fn)
        )

    rudisha

eleza buildRecipe(recipe, basedir, archList):
    """
    Build software using a recipe. This function does the
    'configure;make;make install' dance kila C software, ukijumuisha a possibility
    to customize this process, basically a poor-mans DarwinPorts.
    """
    curdir = os.getcwd()

    name = recipe['name']
    THIRD_PARTY_LIBS.append(name)
    url = recipe['url']
    configure = recipe.get('configure', './configure')
    buildrecipe = recipe.get('buildrecipe', Tupu)
    install = recipe.get('install', 'make && make install DESTDIR=%s'%(
        shellQuote(basedir)))

    archiveName = os.path.split(url)[-1]
    sourceArchive = os.path.join(DEPSRC, archiveName)

    ikiwa sio os.path.exists(DEPSRC):
        os.mkdir(DEPSRC)

    verifyThirdPartyFile(url, recipe['checksum'], sourceArchive)
    andika("Extracting archive kila %s"%(name,))
    buildDir=os.path.join(WORKDIR, '_bld')
    ikiwa sio os.path.exists(buildDir):
        os.mkdir(buildDir)

    workDir = extractArchive(buildDir, sourceArchive)
    os.chdir(workDir)

    kila patch kwenye recipe.get('patches', ()):
        ikiwa isinstance(patch, tuple):
            url, checksum = patch
            fn = os.path.join(DEPSRC, os.path.basename(url))
            verifyThirdPartyFile(url, checksum, fn)
        isipokua:
            # patch ni a file kwenye the source directory
            fn = os.path.join(curdir, patch)
        runCommand('patch -p%s < %s'%(recipe.get('patchlevel', 1),
            shellQuote(fn),))

    kila patchscript kwenye recipe.get('patchscripts', ()):
        ikiwa isinstance(patchscript, tuple):
            url, checksum = patchscript
            fn = os.path.join(DEPSRC, os.path.basename(url))
            verifyThirdPartyFile(url, checksum, fn)
        isipokua:
            # patch ni a file kwenye the source directory
            fn = os.path.join(curdir, patchscript)
        ikiwa fn.endswith('.bz2'):
            runCommand('bunzip2 -fk %s' % shellQuote(fn))
            fn = fn[:-4]
        runCommand('sh %s' % shellQuote(fn))
        os.unlink(fn)

    ikiwa 'buildDir' kwenye recipe:
        os.chdir(recipe['buildDir'])

    ikiwa configure ni sio Tupu:
        configure_args = [
            "--prefix=/usr/local",
            "--enable-static",
            "--disable-shared",
            #"CPP=gcc -arch %s -E"%(' -arch '.join(archList,),),
        ]

        ikiwa 'configure_pre' kwenye recipe:
            args = list(recipe['configure_pre'])
            ikiwa '--disable-static' kwenye args:
                configure_args.remove('--enable-static')
            ikiwa '--enable-shared' kwenye args:
                configure_args.remove('--disable-shared')
            configure_args.extend(args)

        ikiwa recipe.get('useLDFlags', 1):
            configure_args.extend([
                "CFLAGS=%s-mmacosx-version-min=%s -arch %s "
                            "-I%s/usr/local/include"%(
                        recipe.get('extra_cflags', ''),
                        DEPTARGET,
                        ' -arch '.join(archList),
                        shellQuote(basedir)[1:-1],),
                "LDFLAGS=-mmacosx-version-min=%s -L%s/usr/local/lib -arch %s"%(
                    DEPTARGET,
                    shellQuote(basedir)[1:-1],
                    ' -arch '.join(archList)),
            ])
        isipokua:
            configure_args.extend([
                "CFLAGS=%s-mmacosx-version-min=%s -arch %s "
                            "-I%s/usr/local/include"%(
                        recipe.get('extra_cflags', ''),
                        DEPTARGET,
                        ' -arch '.join(archList),
                        shellQuote(basedir)[1:-1],),
            ])

        ikiwa 'configure_post' kwenye recipe:
            configure_args = configure_args + list(recipe['configure_post'])

        configure_args.insert(0, configure)
        configure_args = [ shellQuote(a) kila a kwenye configure_args ]

        andika("Running configure kila %s"%(name,))
        runCommand(' '.join(configure_args) + ' 2>&1')

    ikiwa buildrecipe ni sio Tupu:
        # call special-case build recipe, e.g. kila openssl
        buildrecipe(basedir, archList)

    ikiwa install ni sio Tupu:
        andika("Running install kila %s"%(name,))
        runCommand('{ ' + install + ' ;} 2>&1')

    andika("Done %s"%(name,))
    andika("")

    os.chdir(curdir)

eleza buildLibraries():
    """
    Build our dependencies into $WORKDIR/libraries/usr/local
    """
    andika("")
    andika("Building required libraries")
    andika("")
    universal = os.path.join(WORKDIR, 'libraries')
    os.mkdir(universal)
    os.makedirs(os.path.join(universal, 'usr', 'local', 'lib'))
    os.makedirs(os.path.join(universal, 'usr', 'local', 'include'))

    kila recipe kwenye library_recipes():
        buildRecipe(recipe, universal, ARCHLIST)



eleza buildPythonDocs():
    # This stores the documentation kama Resources/English.lproj/Documentation
    # inside the framework. pydoc na IDLE will pick it up there.
    andika("Install python documentation")
    rootDir = os.path.join(WORKDIR, '_root')
    buildDir = os.path.join('../../Doc')
    docdir = os.path.join(rootDir, 'pydocs')
    curDir = os.getcwd()
    os.chdir(buildDir)
    runCommand('make clean')
    # Create virtual environment kila docs builds ukijumuisha blurb na sphinx
    runCommand('make venv')
    runCommand('venv/bin/python3 -m pip install -U Sphinx==2.0.1')
    runCommand('make html PYTHON=venv/bin/python')
    os.chdir(curDir)
    ikiwa sio os.path.exists(docdir):
        os.mkdir(docdir)
    os.rename(os.path.join(buildDir, 'build', 'html'), docdir)


eleza buildPython():
    andika("Building a universal python kila %s architectures" % UNIVERSALARCHS)

    buildDir = os.path.join(WORKDIR, '_bld', 'python')
    rootDir = os.path.join(WORKDIR, '_root')

    ikiwa os.path.exists(buildDir):
        shutil.rmtree(buildDir)
    ikiwa os.path.exists(rootDir):
        shutil.rmtree(rootDir)
    os.makedirs(buildDir)
    os.makedirs(rootDir)
    os.makedirs(os.path.join(rootDir, 'empty-dir'))
    curdir = os.getcwd()
    os.chdir(buildDir)

    # Extract the version kutoka the configure file, needed to calculate
    # several paths.
    version = getVersion()

    # Since the extra libs are haiko kwenye their installed framework location
    # during the build, augment the library path so that the interpreter
    # will find them during its extension agiza sanity checks.
    os.environ['DYLD_LIBRARY_PATH'] = os.path.join(WORKDIR,
                                        'libraries', 'usr', 'local', 'lib')
    andika("Running configure...")
    runCommand("%s -C --enable-framework --enable-universalsdk=/ "
               "--with-universal-archs=%s "
               "%s "
               "%s "
               "%s "
               "%s "
               "LDFLAGS='-g -L%s/libraries/usr/local/lib' "
               "CFLAGS='-g -I%s/libraries/usr/local/include' 2>&1"%(
        shellQuote(os.path.join(SRCDIR, 'configure')),
        UNIVERSALARCHS,
        (' ', '--with-computed-gotos ')[PYTHON_3],
        (' ', '--without-ensurepip ')[PYTHON_3],
        (' ', "--with-tcltk-includes='-I%s/libraries/usr/local/include'"%(
                            shellQuote(WORKDIR)[1:-1],))[internalTk()],
        (' ', "--with-tcltk-libs='-L%s/libraries/usr/local/lib -ltcl8.6 -ltk8.6'"%(
                            shellQuote(WORKDIR)[1:-1],))[internalTk()],
        shellQuote(WORKDIR)[1:-1],
        shellQuote(WORKDIR)[1:-1]))

    # Look kila environment value BUILDINSTALLER_BUILDPYTHON_MAKE_EXTRAS
    # and, ikiwa defined, append its value to the make command.  This allows
    # us to pita kwenye version control tags, like GITTAG, to a build kutoka a
    # tarball rather than kutoka a vcs checkout, thus eliminating the need
    # to have a working copy of the vcs program on the build machine.
    #
    # A typical use might be:
    #      export BUILDINSTALLER_BUILDPYTHON_MAKE_EXTRAS=" \
    #                         GITVERSION='echo 123456789a' \
    #                         GITTAG='echo v3.6.0' \
    #                         GITBRANCH='echo 3.6'"

    make_extras = os.getenv("BUILDINSTALLER_BUILDPYTHON_MAKE_EXTRAS")
    ikiwa make_extras:
        make_cmd = "make " + make_extras
    isipokua:
        make_cmd = "make"
    andika("Running " + make_cmd)
    runCommand(make_cmd)

    andika("Running make install")
    runCommand("make install DESTDIR=%s"%(
        shellQuote(rootDir)))

    andika("Running make frameworkinstallextras")
    runCommand("make frameworkinstallextras DESTDIR=%s"%(
        shellQuote(rootDir)))

    toa os.environ['DYLD_LIBRARY_PATH']
    andika("Copying required shared libraries")
    ikiwa os.path.exists(os.path.join(WORKDIR, 'libraries', 'Library')):
        build_lib_dir = os.path.join(
                WORKDIR, 'libraries', 'Library', 'Frameworks',
                'Python.framework', 'Versions', getVersion(), 'lib')
        fw_lib_dir = os.path.join(
                WORKDIR, '_root', 'Library', 'Frameworks',
                'Python.framework', 'Versions', getVersion(), 'lib')
        ikiwa internalTk():
            # move Tcl na Tk pkgconfig files
            runCommand("mv %s/pkgconfig/* %s/pkgconfig"%(
                        shellQuote(build_lib_dir),
                        shellQuote(fw_lib_dir) ))
            runCommand("rm -r %s/pkgconfig"%(
                        shellQuote(build_lib_dir), ))
        runCommand("mv %s/* %s"%(
                    shellQuote(build_lib_dir),
                    shellQuote(fw_lib_dir) ))

    frmDir = os.path.join(rootDir, 'Library', 'Frameworks', 'Python.framework')
    frmDirVersioned = os.path.join(frmDir, 'Versions', version)
    path_to_lib = os.path.join(frmDirVersioned, 'lib', 'python%s'%(version,))
    # create directory kila OpenSSL certificates
    sslDir = os.path.join(frmDirVersioned, 'etc', 'openssl')
    os.makedirs(sslDir)

    andika("Fix file modes")
    gid = grp.getgrnam('admin').gr_gid

    shared_lib_error = Uongo
    kila dirpath, dirnames, filenames kwenye os.walk(frmDir):
        kila dn kwenye dirnames:
            os.chmod(os.path.join(dirpath, dn), STAT_0o775)
            os.chown(os.path.join(dirpath, dn), -1, gid)

        kila fn kwenye filenames:
            ikiwa os.path.islink(fn):
                endelea

            # "chmod g+w $fn"
            p = os.path.join(dirpath, fn)
            st = os.stat(p)
            os.chmod(p, stat.S_IMODE(st.st_mode) | stat.S_IWGRP)
            os.chown(p, -1, gid)

            ikiwa fn kwenye EXPECTED_SHARED_LIBS:
                # check to see that this file was linked ukijumuisha the
                # expected library path na version
                data = captureCommand("otool -L %s" % shellQuote(p))
                kila sl kwenye EXPECTED_SHARED_LIBS[fn]:
                    ikiwa ("\t%s " % sl) haiko kwenye data:
                        andika("Expected shared lib %s was sio linked ukijumuisha %s"
                                % (sl, p))
                        shared_lib_error = Kweli

    ikiwa shared_lib_error:
        fatal("Unexpected shared library errors.")

    ikiwa PYTHON_3:
        LDVERSION=Tupu
        VERSION=Tupu
        ABIFLAGS=Tupu

        fp = open(os.path.join(buildDir, 'Makefile'), 'r')
        kila ln kwenye fp:
            ikiwa ln.startswith('VERSION='):
                VERSION=ln.split()[1]
            ikiwa ln.startswith('ABIFLAGS='):
                ABIFLAGS=ln.split()
                ABIFLAGS=ABIFLAGS[1] ikiwa len(ABIFLAGS) > 1 isipokua ''
            ikiwa ln.startswith('LDVERSION='):
                LDVERSION=ln.split()[1]
        fp.close()

        LDVERSION = LDVERSION.replace('$(VERSION)', VERSION)
        LDVERSION = LDVERSION.replace('$(ABIFLAGS)', ABIFLAGS)
        config_suffix = '-' + LDVERSION
        ikiwa getVersionMajorMinor() >= (3, 6):
            config_suffix = config_suffix + '-darwin'
    isipokua:
        config_suffix = ''      # Python 2.x

    # We added some directories to the search path during the configure
    # phase. Remove those because those directories won't be there on
    # the end-users system. Also remove the directories kutoka _sysconfigdata.py
    # (added kwenye 3.3) ikiwa it exists.

    include_path = '-I%s/libraries/usr/local/include' % (WORKDIR,)
    lib_path = '-L%s/libraries/usr/local/lib' % (WORKDIR,)

    # fix Makefile
    path = os.path.join(path_to_lib, 'config' + config_suffix, 'Makefile')
    fp = open(path, 'r')
    data = fp.read()
    fp.close()

    kila p kwenye (include_path, lib_path):
        data = data.replace(" " + p, '')
        data = data.replace(p + " ", '')

    fp = open(path, 'w')
    fp.write(data)
    fp.close()

    # fix _sysconfigdata
    #
    # TODO: make this more robust!  test_sysconfig_module of
    # distutils.tests.test_sysconfig.SysconfigTestCase tests that
    # the output kutoka get_config_var kwenye both sysconfig na
    # distutils.sysconfig ni exactly the same kila both CFLAGS na
    # LDFLAGS.  The fixing up ni now complicated by the pretty
    # printing kwenye _sysconfigdata.py.  Also, we are using the
    # pprint kutoka the Python running the installer build which
    # may sio cosmetically format the same kama the pprint kwenye the Python
    # being built (and which ni used to originally generate
    # _sysconfigdata.py).

    agiza pprint
    ikiwa getVersionMajorMinor() >= (3, 6):
        # XXX this ni extra-fragile
        path = os.path.join(path_to_lib,
            '_sysconfigdata_%s_darwin_darwin.py' % (ABIFLAGS,))
    isipokua:
        path = os.path.join(path_to_lib, '_sysconfigdata.py')
    fp = open(path, 'r')
    data = fp.read()
    fp.close()
    # create build_time_vars dict
    exec(data)
    vars = {}
    kila k, v kwenye build_time_vars.items():
        ikiwa type(v) == type(''):
            kila p kwenye (include_path, lib_path):
                v = v.replace(' ' + p, '')
                v = v.replace(p + ' ', '')
        vars[k] = v

    fp = open(path, 'w')
    # duplicated kutoka sysconfig._generate_posix_vars()
    fp.write('# system configuration generated na used by'
                ' the sysconfig module\n')
    fp.write('build_time_vars = ')
    pprint.pandika(vars, stream=fp)
    fp.close()

    # Add symlinks kwenye /usr/local/bin, using relative links
    usr_local_bin = os.path.join(rootDir, 'usr', 'local', 'bin')
    to_framework = os.path.join('..', '..', '..', 'Library', 'Frameworks',
            'Python.framework', 'Versions', version, 'bin')
    ikiwa os.path.exists(usr_local_bin):
        shutil.rmtree(usr_local_bin)
    os.makedirs(usr_local_bin)
    kila fn kwenye os.listdir(
                os.path.join(frmDir, 'Versions', version, 'bin')):
        os.symlink(os.path.join(to_framework, fn),
                   os.path.join(usr_local_bin, fn))

    os.chdir(curdir)

    ikiwa PYTHON_3:
        # Remove the 'Current' link, that way we don't accidentally mess
        # ukijumuisha an already installed version of python 2
        os.unlink(os.path.join(rootDir, 'Library', 'Frameworks',
                            'Python.framework', 'Versions', 'Current'))

eleza patchFile(inPath, outPath):
    data = fileContents(inPath)
    data = data.replace('$FULL_VERSION', getFullVersion())
    data = data.replace('$VERSION', getVersion())
    data = data.replace('$MACOSX_DEPLOYMENT_TARGET', ''.join((DEPTARGET, ' ama later')))
    data = data.replace('$ARCHITECTURES', ", ".join(universal_opts_map[UNIVERSALARCHS]))
    data = data.replace('$INSTALL_SIZE', installSize())
    data = data.replace('$THIRD_PARTY_LIBS', "\\\n".join(THIRD_PARTY_LIBS))

    # This one ni sio handy kama a template variable
    data = data.replace('$PYTHONFRAMEWORKINSTALLDIR', '/Library/Frameworks/Python.framework')
    fp = open(outPath, 'w')
    fp.write(data)
    fp.close()

eleza patchScript(inPath, outPath):
    major, minor = getVersionMajorMinor()
    data = fileContents(inPath)
    data = data.replace('@PYMAJOR@', str(major))
    data = data.replace('@PYVER@', getVersion())
    fp = open(outPath, 'w')
    fp.write(data)
    fp.close()
    os.chmod(outPath, STAT_0o755)



eleza packageFromRecipe(targetDir, recipe):
    curdir = os.getcwd()
    jaribu:
        # The major version (such kama 2.5) ni included kwenye the package name
        # because having two version of python installed at the same time is
        # common.
        pkgname = '%s-%s'%(recipe['name'], getVersion())
        srcdir  = recipe.get('source')
        pkgroot = recipe.get('topdir', srcdir)
        postflight = recipe.get('postflight')
        readme = textwrap.dedent(recipe['readme'])
        isRequired = recipe.get('required', Kweli)

        andika("- building package %s"%(pkgname,))

        # Substitute some variables
        textvars = dict(
            VER=getVersion(),
            FULLVER=getFullVersion(),
        )
        readme = readme % textvars

        ikiwa pkgroot ni sio Tupu:
            pkgroot = pkgroot % textvars
        isipokua:
            pkgroot = '/'

        ikiwa srcdir ni sio Tupu:
            srcdir = os.path.join(WORKDIR, '_root', srcdir[1:])
            srcdir = srcdir % textvars

        ikiwa postflight ni sio Tupu:
            postflight = os.path.abspath(postflight)

        packageContents = os.path.join(targetDir, pkgname + '.pkg', 'Contents')
        os.makedirs(packageContents)

        ikiwa srcdir ni sio Tupu:
            os.chdir(srcdir)
            runCommand("pax -wf %s . 2>&1"%(shellQuote(os.path.join(packageContents, 'Archive.pax')),))
            runCommand("gzip -9 %s 2>&1"%(shellQuote(os.path.join(packageContents, 'Archive.pax')),))
            runCommand("mkbom . %s 2>&1"%(shellQuote(os.path.join(packageContents, 'Archive.bom')),))

        fn = os.path.join(packageContents, 'PkgInfo')
        fp = open(fn, 'w')
        fp.write('pmkrpkg1')
        fp.close()

        rsrcDir = os.path.join(packageContents, "Resources")
        os.mkdir(rsrcDir)
        fp = open(os.path.join(rsrcDir, 'ReadMe.txt'), 'w')
        fp.write(readme)
        fp.close()

        ikiwa postflight ni sio Tupu:
            patchScript(postflight, os.path.join(rsrcDir, 'postflight'))

        vers = getFullVersion()
        major, minor = getVersionMajorMinor()
        pl = Plist(
                CFBundleGetInfoString="Python.%s %s"%(pkgname, vers,),
                CFBundleIdentifier='org.python.Python.%s'%(pkgname,),
                CFBundleName='Python.%s'%(pkgname,),
                CFBundleShortVersionString=vers,
                IFMajorVersion=major,
                IFMinorVersion=minor,
                IFPkgFormatVersion=0.10000000149011612,
                IFPkgFlagAllowBackRev=Uongo,
                IFPkgFlagAuthorizationAction="RootAuthorization",
                IFPkgFlagDefaultLocation=pkgroot,
                IFPkgFlagFollowLinks=Kweli,
                IFPkgFlagInstallFat=Kweli,
                IFPkgFlagIsRequired=isRequired,
                IFPkgFlagOverwritePermissions=Uongo,
                IFPkgFlagRelocatable=Uongo,
                IFPkgFlagRestartAction="NoRestart",
                IFPkgFlagRootVolumeOnly=Kweli,
                IFPkgFlagUpdateInstalledLangauges=Uongo,
            )
        writePlist(pl, os.path.join(packageContents, 'Info.plist'))

        pl = Plist(
                    IFPkgDescriptionDescription=readme,
                    IFPkgDescriptionTitle=recipe.get('long_name', "Python.%s"%(pkgname,)),
                    IFPkgDescriptionVersion=vers,
                )
        writePlist(pl, os.path.join(packageContents, 'Resources', 'Description.plist'))

    mwishowe:
        os.chdir(curdir)


eleza makeMpkgPlist(path):

    vers = getFullVersion()
    major, minor = getVersionMajorMinor()

    pl = Plist(
            CFBundleGetInfoString="Python %s"%(vers,),
            CFBundleIdentifier='org.python.Python',
            CFBundleName='Python',
            CFBundleShortVersionString=vers,
            IFMajorVersion=major,
            IFMinorVersion=minor,
            IFPkgFlagComponentDirectory="Contents/Packages",
            IFPkgFlagPackageList=[
                dict(
                    IFPkgFlagPackageLocation='%s-%s.pkg'%(item['name'], getVersion()),
                    IFPkgFlagPackageSelection=item.get('selected', 'selected'),
                )
                kila item kwenye pkg_recipes()
            ],
            IFPkgFormatVersion=0.10000000149011612,
            IFPkgFlagBackgroundScaling="proportional",
            IFPkgFlagBackgroundAlignment="left",
            IFPkgFlagAuthorizationAction="RootAuthorization",
        )

    writePlist(pl, path)


eleza buildInstaller():

    # Zap all compiled files
    kila dirpath, _, filenames kwenye os.walk(os.path.join(WORKDIR, '_root')):
        kila fn kwenye filenames:
            ikiwa fn.endswith('.pyc') ama fn.endswith('.pyo'):
                os.unlink(os.path.join(dirpath, fn))

    outdir = os.path.join(WORKDIR, 'installer')
    ikiwa os.path.exists(outdir):
        shutil.rmtree(outdir)
    os.mkdir(outdir)

    pkgroot = os.path.join(outdir, 'Python.mpkg', 'Contents')
    pkgcontents = os.path.join(pkgroot, 'Packages')
    os.makedirs(pkgcontents)
    kila recipe kwenye pkg_recipes():
        packageFromRecipe(pkgcontents, recipe)

    rsrcDir = os.path.join(pkgroot, 'Resources')

    fn = os.path.join(pkgroot, 'PkgInfo')
    fp = open(fn, 'w')
    fp.write('pmkrpkg1')
    fp.close()

    os.mkdir(rsrcDir)

    makeMpkgPlist(os.path.join(pkgroot, 'Info.plist'))
    pl = Plist(
                IFPkgDescriptionTitle="Python",
                IFPkgDescriptionVersion=getVersion(),
            )

    writePlist(pl, os.path.join(pkgroot, 'Resources', 'Description.plist'))
    kila fn kwenye os.listdir('resources'):
        ikiwa fn == '.svn': endelea
        ikiwa fn.endswith('.jpg'):
            shutil.copy(os.path.join('resources', fn), os.path.join(rsrcDir, fn))
        isipokua:
            patchFile(os.path.join('resources', fn), os.path.join(rsrcDir, fn))


eleza installSize(clear=Uongo, _saved=[]):
    ikiwa clear:
        toa _saved[:]
    ikiwa sio _saved:
        data = captureCommand("du -ks %s"%(
                    shellQuote(os.path.join(WORKDIR, '_root'))))
        _saved.append("%d"%((0.5 + (int(data.split()[0]) / 1024.0)),))
    rudisha _saved[0]


eleza buildDMG():
    """
    Create DMG containing the rootDir.
    """
    outdir = os.path.join(WORKDIR, 'diskimage')
    ikiwa os.path.exists(outdir):
        shutil.rmtree(outdir)

    imagepath = os.path.join(outdir,
                    'python-%s-macosx%s'%(getFullVersion(),DEPTARGET))
    ikiwa INCLUDE_TIMESTAMP:
        imagepath = imagepath + '-%04d-%02d-%02d'%(time.localtime()[:3])
    imagepath = imagepath + '.dmg'

    os.mkdir(outdir)

    # Try to mitigate race condition kwenye certain versions of macOS, e.g. 10.9,
    # when hdiutil create fails ukijumuisha  "Resource busy".  For now, just retry
    # the create a few times na hope that it eventually works.

    volname='Python %s'%(getFullVersion())
    cmd = ("hdiutil create -format UDRW -volname %s -srcfolder %s -size 100m %s"%(
            shellQuote(volname),
            shellQuote(os.path.join(WORKDIR, 'installer')),
            shellQuote(imagepath + ".tmp.dmg" )))
    kila i kwenye range(5):
        fd = os.popen(cmd, 'r')
        data = fd.read()
        xit = fd.close()
        ikiwa sio xit:
            koma
        sys.stdout.write(data)
        andika(" -- retrying hdiutil create")
        time.sleep(5)
    isipokua:
        ashiria RuntimeError("command failed: %s"%(cmd,))

    ikiwa sio os.path.exists(os.path.join(WORKDIR, "mnt")):
        os.mkdir(os.path.join(WORKDIR, "mnt"))
    runCommand("hdiutil attach %s -mountroot %s"%(
        shellQuote(imagepath + ".tmp.dmg"), shellQuote(os.path.join(WORKDIR, "mnt"))))

    # Custom icon kila the DMG, shown when the DMG ni mounted.
    shutil.copy("../Icons/Disk Image.icns",
            os.path.join(WORKDIR, "mnt", volname, ".VolumeIcon.icns"))
    runCommand("SetFile -a C %s/"%(
            shellQuote(os.path.join(WORKDIR, "mnt", volname)),))

    runCommand("hdiutil detach %s"%(shellQuote(os.path.join(WORKDIR, "mnt", volname))))

    setIcon(imagepath + ".tmp.dmg", "../Icons/Disk Image.icns")
    runCommand("hdiutil convert %s -format UDZO -o %s"%(
            shellQuote(imagepath + ".tmp.dmg"), shellQuote(imagepath)))
    setIcon(imagepath, "../Icons/Disk Image.icns")

    os.unlink(imagepath + ".tmp.dmg")

    rudisha imagepath


eleza setIcon(filePath, icnsPath):
    """
    Set the custom icon kila the specified file ama directory.
    """

    dirPath = os.path.normpath(os.path.dirname(__file__))
    toolPath = os.path.join(dirPath, "seticon.app/Contents/MacOS/seticon")
    ikiwa sio os.path.exists(toolPath) ama os.stat(toolPath).st_mtime < os.stat(dirPath + '/seticon.m').st_mtime:
        # NOTE: The tool ni created inside an .app bundle, otherwise it won't work due
        # to connections to the window server.
        appPath = os.path.join(dirPath, "seticon.app/Contents/MacOS")
        ikiwa sio os.path.exists(appPath):
            os.makedirs(appPath)
        runCommand("cc -o %s %s/seticon.m -framework Cocoa"%(
            shellQuote(toolPath), shellQuote(dirPath)))

    runCommand("%s %s %s"%(shellQuote(os.path.abspath(toolPath)), shellQuote(icnsPath),
        shellQuote(filePath)))

eleza main():
    # First parse options na check ikiwa we can perform our work
    parseOptions()
    checkEnvironment()

    os.environ['MACOSX_DEPLOYMENT_TARGET'] = DEPTARGET
    os.environ['CC'] = CC
    os.environ['CXX'] = CXX

    ikiwa os.path.exists(WORKDIR):
        shutil.rmtree(WORKDIR)
    os.mkdir(WORKDIR)

    os.environ['LC_ALL'] = 'C'

    # Then build third-party libraries such kama sleepycat DB4.
    buildLibraries()

    # Now build python itself
    buildPython()

    # And then build the documentation
    # Remove the Deployment Target kutoka the shell
    # environment, it's no longer needed na
    # an unexpected build target can cause problems
    # when Sphinx na its dependencies need to
    # be (re-)installed.
    toa os.environ['MACOSX_DEPLOYMENT_TARGET']
    buildPythonDocs()


    # Prepare the applications folder
    folder = os.path.join(WORKDIR, "_root", "Applications", "Python %s"%(
        getVersion(),))
    fn = os.path.join(folder, "License.rtf")
    patchFile("resources/License.rtf",  fn)
    fn = os.path.join(folder, "ReadMe.rtf")
    patchFile("resources/ReadMe.rtf",  fn)
    fn = os.path.join(folder, "Update Shell Profile.command")
    patchScript("scripts/postflight.patch-profile",  fn)
    fn = os.path.join(folder, "Install Certificates.command")
    patchScript("resources/install_certificates.command",  fn)
    os.chmod(folder, STAT_0o755)
    setIcon(folder, "../Icons/Python Folder.icns")

    # Create the installer
    buildInstaller()

    # And copy the readme into the directory containing the installer
    patchFile('resources/ReadMe.rtf',
                os.path.join(WORKDIR, 'installer', 'ReadMe.rtf'))

    # Ditto kila the license file.
    patchFile('resources/License.rtf',
                os.path.join(WORKDIR, 'installer', 'License.rtf'))

    fp = open(os.path.join(WORKDIR, 'installer', 'Build.txt'), 'w')
    fp.write("# BUILD INFO\n")
    fp.write("# Date: %s\n" % time.ctime())
    fp.write("# By: %s\n" % pwd.getpwuid(os.getuid()).pw_gecos)
    fp.close()

    # And copy it to a DMG
    buildDMG()

ikiwa __name__ == "__main__":
    main()
