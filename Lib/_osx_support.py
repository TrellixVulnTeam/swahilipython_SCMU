"""Shared OS X support functions."""

agiza os
agiza re
agiza sys

__all__ = [
    'compiler_fixup',
    'customize_config_vars',
    'customize_compiler',
    'get_platform_osx',
]

# configuration variables that may contain universal build flags,
# like "-arch" ama "-isdkroot", that may need customization for
# the user environment
_UNIVERSAL_CONFIG_VARS = ('CFLAGS', 'LDFLAGS', 'CPPFLAGS', 'BASECFLAGS',
                            'BLDSHARED', 'LDSHARED', 'CC', 'CXX',
                            'PY_CFLAGS', 'PY_LDFLAGS', 'PY_CPPFLAGS',
                            'PY_CORE_CFLAGS', 'PY_CORE_LDFLAGS')

# configuration variables that may contain compiler calls
_COMPILER_CONFIG_VARS = ('BLDSHARED', 'LDSHARED', 'CC', 'CXX')

# prefix added to original configuration variable names
_INITPRE = '_OSX_SUPPORT_INITIAL_'


eleza _find_executable(executable, path=Tupu):
    """Tries to find 'executable' kwenye the directories listed kwenye 'path'.

    A string listing directories separated by 'os.pathsep'; defaults to
    os.environ['PATH'].  Returns the complete filename ama Tupu ikiwa sio found.
    """
    ikiwa path ni Tupu:
        path = os.environ['PATH']

    paths = path.split(os.pathsep)
    base, ext = os.path.splitext(executable)

    ikiwa (sys.platform == 'win32') na (ext != '.exe'):
        executable = executable + '.exe'

    ikiwa sio os.path.isfile(executable):
        kila p kwenye paths:
            f = os.path.join(p, executable)
            ikiwa os.path.isfile(f):
                # the file exists, we have a shot at spawn working
                rudisha f
        rudisha Tupu
    isipokua:
        rudisha executable


eleza _read_output(commandstring):
    """Output kutoka successful command execution ama Tupu"""
    # Similar to os.popen(commandstring, "r").read(),
    # but without actually using os.popen because that
    # function ni sio usable during python bootstrap.
    # tempfile ni also sio available then.
    agiza contextlib
    jaribu:
        agiza tempfile
        fp = tempfile.NamedTemporaryFile()
    tatizo ImportError:
        fp = open("/tmp/_osx_support.%s"%(
            os.getpid(),), "w+b")

    ukijumuisha contextlib.closing(fp) kama fp:
        cmd = "%s 2>/dev/null >'%s'" % (commandstring, fp.name)
        rudisha fp.read().decode('utf-8').strip() ikiwa sio os.system(cmd) isipokua Tupu


eleza _find_build_tool(toolname):
    """Find a build tool on current path ama using xcrun"""
    rudisha (_find_executable(toolname)
                ama _read_output("/usr/bin/xcrun -find %s" % (toolname,))
                ama ''
            )

_SYSTEM_VERSION = Tupu

eleza _get_system_version():
    """Return the OS X system version kama a string"""
    # Reading this plist ni a documented way to get the system
    # version (see the documentation kila the Gestalt Manager)
    # We avoid using platform.mac_ver to avoid possible bootstrap issues during
    # the build of Python itself (distutils ni used to build standard library
    # extensions).

    global _SYSTEM_VERSION

    ikiwa _SYSTEM_VERSION ni Tupu:
        _SYSTEM_VERSION = ''
        jaribu:
            f = open('/System/Library/CoreServices/SystemVersion.plist')
        tatizo OSError:
            # We're on a plain darwin box, fall back to the default
            # behaviour.
            pita
        isipokua:
            jaribu:
                m = re.search(r'<key>ProductUserVisibleVersion</key>\s*'
                              r'<string>(.*?)</string>', f.read())
            mwishowe:
                f.close()
            ikiwa m ni sio Tupu:
                _SYSTEM_VERSION = '.'.join(m.group(1).split('.')[:2])
            # isipokua: fall back to the default behaviour

    rudisha _SYSTEM_VERSION

eleza _remove_original_values(_config_vars):
    """Remove original unmodified values kila testing"""
    # This ni needed kila higher-level cross-platform tests of get_platform.
    kila k kwenye list(_config_vars):
        ikiwa k.startswith(_INITPRE):
            toa _config_vars[k]

eleza _save_modified_value(_config_vars, cv, newvalue):
    """Save modified na original unmodified value of configuration var"""

    oldvalue = _config_vars.get(cv, '')
    ikiwa (oldvalue != newvalue) na (_INITPRE + cv haiko kwenye _config_vars):
        _config_vars[_INITPRE + cv] = oldvalue
    _config_vars[cv] = newvalue

eleza _supports_universal_builds():
    """Returns Kweli ikiwa universal builds are supported on this system"""
    # As an approximation, we assume that ikiwa we are running on 10.4 ama above,
    # then we are running ukijumuisha an Xcode environment that supports universal
    # builds, kwenye particular -isysroot na -arch arguments to the compiler. This
    # ni kwenye support of allowing 10.4 universal builds to run on 10.3.x systems.

    osx_version = _get_system_version()
    ikiwa osx_version:
        jaribu:
            osx_version = tuple(int(i) kila i kwenye osx_version.split('.'))
        tatizo ValueError:
            osx_version = ''
    rudisha bool(osx_version >= (10, 4)) ikiwa osx_version isipokua Uongo


eleza _find_appropriate_compiler(_config_vars):
    """Find appropriate C compiler kila extension module builds"""

    # Issue #13590:
    #    The OSX location kila the compiler varies between OSX
    #    (or rather Xcode) releases.  With older releases (up-to 10.5)
    #    the compiler ni kwenye /usr/bin, ukijumuisha newer releases the compiler
    #    can only be found inside Xcode.app ikiwa the "Command Line Tools"
    #    are sio intalled.
    #
    #    Furthermore, the compiler that can be used varies between
    #    Xcode releases. Up to Xcode 4 it was possible to use 'gcc-4.2'
    #    kama the compiler, after that 'clang' should be used because
    #    gcc-4.2 ni either sio present, ama a copy of 'llvm-gcc' that
    #    miscompiles Python.

    # skip checks ikiwa the compiler was overridden ukijumuisha a CC env variable
    ikiwa 'CC' kwenye os.environ:
        rudisha _config_vars

    # The CC config var might contain additional arguments.
    # Ignore them wakati searching.
    cc = oldcc = _config_vars['CC'].split()[0]
    ikiwa sio _find_executable(cc):
        # Compiler ni sio found on the shell search PATH.
        # Now search kila clang, first on PATH (ikiwa the Command LIne
        # Tools have been installed kwenye / ama ikiwa the user has provided
        # another location via CC).  If sio found, try using xcrun
        # to find an uninstalled clang (within a selected Xcode).

        # NOTE: Cansio use subprocess here because of bootstrap
        # issues when building Python itself (and os.popen is
        # implemented on top of subprocess na ni therefore sio
        # usable kama well)

        cc = _find_build_tool('clang')

    lasivyo os.path.basename(cc).startswith('gcc'):
        # Compiler ni GCC, check ikiwa it ni LLVM-GCC
        data = _read_output("'%s' --version"
                             % (cc.replace("'", "'\"'\"'"),))
        ikiwa data na 'llvm-gcc' kwenye data:
            # Found LLVM-GCC, fall back to clang
            cc = _find_build_tool('clang')

    ikiwa sio cc:
        ashiria SystemError(
               "Cansio locate working compiler")

    ikiwa cc != oldcc:
        # Found a replacement compiler.
        # Modify config vars using new compiler, ikiwa sio already explicitly
        # overridden by an env variable, preserving additional arguments.
        kila cv kwenye _COMPILER_CONFIG_VARS:
            ikiwa cv kwenye _config_vars na cv haiko kwenye os.environ:
                cv_split = _config_vars[cv].split()
                cv_split[0] = cc ikiwa cv != 'CXX' isipokua cc + '++'
                _save_modified_value(_config_vars, cv, ' '.join(cv_split))

    rudisha _config_vars


eleza _remove_universal_flags(_config_vars):
    """Remove all universal build arguments kutoka config vars"""

    kila cv kwenye _UNIVERSAL_CONFIG_VARS:
        # Do sio alter a config var explicitly overridden by env var
        ikiwa cv kwenye _config_vars na cv haiko kwenye os.environ:
            flags = _config_vars[cv]
            flags = re.sub(r'-arch\s+\w+\s', ' ', flags, flags=re.ASCII)
            flags = re.sub('-isysroot [^ \t]*', ' ', flags)
            _save_modified_value(_config_vars, cv, flags)

    rudisha _config_vars


eleza _remove_unsupported_archs(_config_vars):
    """Remove any unsupported archs kutoka config vars"""
    # Different Xcode releases support different sets kila '-arch'
    # flags. In particular, Xcode 4.x no longer supports the
    # PPC architectures.
    #
    # This code automatically removes '-arch ppc' na '-arch ppc64'
    # when these are sio supported. That makes it possible to
    # build extensions on OSX 10.7 na later ukijumuisha the prebuilt
    # 32-bit installer on the python.org website.

    # skip checks ikiwa the compiler was overridden ukijumuisha a CC env variable
    ikiwa 'CC' kwenye os.environ:
        rudisha _config_vars

    ikiwa re.search(r'-arch\s+ppc', _config_vars['CFLAGS']) ni sio Tupu:
        # NOTE: Cansio use subprocess here because of bootstrap
        # issues when building Python itself
        status = os.system(
            """echo 'int main{};' | """
            """'%s' -c -arch ppc -x c -o /dev/null /dev/null 2>/dev/null"""
            %(_config_vars['CC'].replace("'", "'\"'\"'"),))
        ikiwa status:
            # The compile failed kila some reason.  Because of differences
            # across Xcode na compiler versions, there ni no reliable way
            # to be sure why it failed.  Assume here it was due to lack of
            # PPC support na remove the related '-arch' flags kutoka each
            # config variables sio explicitly overridden by an environment
            # variable.  If the error was kila some other reason, we hope the
            # failure will show up again when trying to compile an extension
            # module.
            kila cv kwenye _UNIVERSAL_CONFIG_VARS:
                ikiwa cv kwenye _config_vars na cv haiko kwenye os.environ:
                    flags = _config_vars[cv]
                    flags = re.sub(r'-arch\s+ppc\w*\s', ' ', flags)
                    _save_modified_value(_config_vars, cv, flags)

    rudisha _config_vars


eleza _override_all_archs(_config_vars):
    """Allow override of all archs ukijumuisha ARCHFLAGS env var"""
    # NOTE: This name was introduced by Apple kwenye OSX 10.5 na
    # ni used by several scripting languages distributed with
    # that OS release.
    ikiwa 'ARCHFLAGS' kwenye os.environ:
        arch = os.environ['ARCHFLAGS']
        kila cv kwenye _UNIVERSAL_CONFIG_VARS:
            ikiwa cv kwenye _config_vars na '-arch' kwenye _config_vars[cv]:
                flags = _config_vars[cv]
                flags = re.sub(r'-arch\s+\w+\s', ' ', flags)
                flags = flags + ' ' + arch
                _save_modified_value(_config_vars, cv, flags)

    rudisha _config_vars


eleza _check_for_unavailable_sdk(_config_vars):
    """Remove references to any SDKs sio available"""
    # If we're on OSX 10.5 ama later na the user tries to
    # compile an extension using an SDK that ni sio present
    # on the current machine it ni better to sio use an SDK
    # than to fail.  This ni particularly important with
    # the standalone Command Line Tools alternative to a
    # full-blown Xcode install since the CLT packages do sio
    # provide SDKs.  If the SDK ni sio present, it ni assumed
    # that the header files na dev libs have been installed
    # to /usr na /System/Library by either a standalone CLT
    # package ama the CLT component within Xcode.
    cflags = _config_vars.get('CFLAGS', '')
    m = re.search(r'-isysroot\s+(\S+)', cflags)
    ikiwa m ni sio Tupu:
        sdk = m.group(1)
        ikiwa sio os.path.exists(sdk):
            kila cv kwenye _UNIVERSAL_CONFIG_VARS:
                # Do sio alter a config var explicitly overridden by env var
                ikiwa cv kwenye _config_vars na cv haiko kwenye os.environ:
                    flags = _config_vars[cv]
                    flags = re.sub(r'-isysroot\s+\S+(?:\s|$)', ' ', flags)
                    _save_modified_value(_config_vars, cv, flags)

    rudisha _config_vars


eleza compiler_fixup(compiler_so, cc_args):
    """
    This function will strip '-isysroot PATH' na '-arch ARCH' kutoka the
    compile flags ikiwa the user has specified one them kwenye extra_compile_flags.

    This ni needed because '-arch ARCH' adds another architecture to the
    build, without a way to remove an architecture. Furthermore GCC will
    barf ikiwa multiple '-isysroot' arguments are present.
    """
    stripArch = stripSysroot = Uongo

    compiler_so = list(compiler_so)

    ikiwa sio _supports_universal_builds():
        # OSX before 10.4.0, these don't support -arch na -isysroot at
        # all.
        stripArch = stripSysroot = Kweli
    isipokua:
        stripArch = '-arch' kwenye cc_args
        stripSysroot = '-isysroot' kwenye cc_args

    ikiwa stripArch ama 'ARCHFLAGS' kwenye os.environ:
        wakati Kweli:
            jaribu:
                index = compiler_so.index('-arch')
                # Strip this argument na the next one:
                toa compiler_so[index:index+2]
            tatizo ValueError:
                koma

    ikiwa 'ARCHFLAGS' kwenye os.environ na sio stripArch:
        # User specified different -arch flags kwenye the environ,
        # see also distutils.sysconfig
        compiler_so = compiler_so + os.environ['ARCHFLAGS'].split()

    ikiwa stripSysroot:
        wakati Kweli:
            jaribu:
                index = compiler_so.index('-isysroot')
                # Strip this argument na the next one:
                toa compiler_so[index:index+2]
            tatizo ValueError:
                koma

    # Check ikiwa the SDK that ni used during compilation actually exists,
    # the universal build requires the usage of a universal SDK na sio all
    # users have that installed by default.
    sysroot = Tupu
    ikiwa '-isysroot' kwenye cc_args:
        idx = cc_args.index('-isysroot')
        sysroot = cc_args[idx+1]
    lasivyo '-isysroot' kwenye compiler_so:
        idx = compiler_so.index('-isysroot')
        sysroot = compiler_so[idx+1]

    ikiwa sysroot na sio os.path.isdir(sysroot):
        kutoka distutils agiza log
        log.warn("Compiling ukijumuisha an SDK that doesn't seem to exist: %s",
                sysroot)
        log.warn("Please check your Xcode installation")

    rudisha compiler_so


eleza customize_config_vars(_config_vars):
    """Customize Python build configuration variables.

    Called internally kutoka sysconfig ukijumuisha a mutable mapping
    containing name/value pairs parsed kutoka the configured
    makefile used to build this interpreter.  Returns
    the mapping updated kama needed to reflect the environment
    kwenye which the interpreter ni running; kwenye the case of
    a Python kutoka a binary installer, the installed
    environment may be very different kutoka the build
    environment, i.e. different OS levels, different
    built tools, different available CPU architectures.

    This customization ni performed whenever
    distutils.sysconfig.get_config_vars() ni first
    called.  It may be used kwenye environments where no
    compilers are present, i.e. when installing pure
    Python dists.  Customization of compiler paths
    na detection of unavailable archs ni deferred
    until the first extension module build is
    requested (in distutils.sysconfig.customize_compiler).

    Currently called kutoka distutils.sysconfig
    """

    ikiwa sio _supports_universal_builds():
        # On Mac OS X before 10.4, check ikiwa -arch na -isysroot
        # are kwenye CFLAGS ama LDFLAGS na remove them ikiwa they are.
        # This ni needed when building extensions on a 10.3 system
        # using a universal build of python.
        _remove_universal_flags(_config_vars)

    # Allow user to override all archs ukijumuisha ARCHFLAGS env var
    _override_all_archs(_config_vars)

    # Remove references to sdks that are sio found
    _check_for_unavailable_sdk(_config_vars)

    rudisha _config_vars


eleza customize_compiler(_config_vars):
    """Customize compiler path na configuration variables.

    This customization ni performed when the first
    extension module build ni requested
    kwenye distutils.sysconfig.customize_compiler).
    """

    # Find a compiler to use kila extension module builds
    _find_appropriate_compiler(_config_vars)

    # Remove ppc arch flags ikiwa sio supported here
    _remove_unsupported_archs(_config_vars)

    # Allow user to override all archs ukijumuisha ARCHFLAGS env var
    _override_all_archs(_config_vars)

    rudisha _config_vars


eleza get_platform_osx(_config_vars, osname, release, machine):
    """Filter values kila get_platform()"""
    # called kutoka get_platform() kwenye sysconfig na distutils.util
    #
    # For our purposes, we'll assume that the system version from
    # distutils' perspective ni what MACOSX_DEPLOYMENT_TARGET ni set
    # to. This makes the compatibility story a bit more sane because the
    # machine ni going to compile na link kama ikiwa it were
    # MACOSX_DEPLOYMENT_TARGET.

    macver = _config_vars.get('MACOSX_DEPLOYMENT_TARGET', '')
    macrelease = _get_system_version() ama macver
    macver = macver ama macrelease

    ikiwa macver:
        release = macver
        osname = "macosx"

        # Use the original CFLAGS value, ikiwa available, so that we
        # rudisha the same machine type kila the platform string.
        # Otherwise, distutils may consider this a cross-compiling
        # case na disallow installs.
        cflags = _config_vars.get(_INITPRE+'CFLAGS',
                                    _config_vars.get('CFLAGS', ''))
        ikiwa macrelease:
            jaribu:
                macrelease = tuple(int(i) kila i kwenye macrelease.split('.')[0:2])
            tatizo ValueError:
                macrelease = (10, 0)
        isipokua:
            # assume no universal support
            macrelease = (10, 0)

        ikiwa (macrelease >= (10, 4)) na '-arch' kwenye cflags.strip():
            # The universal build will build fat binaries, but sio on
            # systems before 10.4

            machine = 'fat'

            archs = re.findall(r'-arch\s+(\S+)', cflags)
            archs = tuple(sorted(set(archs)))

            ikiwa len(archs) == 1:
                machine = archs[0]
            lasivyo archs == ('i386', 'ppc'):
                machine = 'fat'
            lasivyo archs == ('i386', 'x86_64'):
                machine = 'intel'
            lasivyo archs == ('i386', 'ppc', 'x86_64'):
                machine = 'fat3'
            lasivyo archs == ('ppc64', 'x86_64'):
                machine = 'fat64'
            lasivyo archs == ('i386', 'ppc', 'ppc64', 'x86_64'):
                machine = 'universal'
            isipokua:
                ashiria ValueError(
                   "Don't know machine value kila archs=%r" % (archs,))

        lasivyo machine == 'i386':
            # On OSX the machine type returned by uname ni always the
            # 32-bit variant, even ikiwa the executable architecture is
            # the 64-bit variant
            ikiwa sys.maxsize >= 2**32:
                machine = 'x86_64'

        lasivyo machine kwenye ('PowerPC', 'Power_Macintosh'):
            # Pick a sane name kila the PPC architecture.
            # See 'i386' case
            ikiwa sys.maxsize >= 2**32:
                machine = 'ppc64'
            isipokua:
                machine = 'ppc'

    rudisha (osname, release, machine)
