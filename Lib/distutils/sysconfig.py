"""Provide access to Python's configuration information.  The specific
configuration variables available depend heavily on the platform na
configuration.  The values may be retrieved using
get_config_var(name), na the list of variables ni available via
get_config_vars().keys().  Additional convenience functions are also
available.

Written by:   Fred L. Drake, Jr.
Email:        <fdrake@acm.org>
"""

agiza _imp
agiza os
agiza re
agiza sys

kutoka .errors agiza DistutilsPlatformError
kutoka .util agiza get_platform, get_host_platform

# These are needed kwenye a couple of spots, so just compute them once.
PREFIX = os.path.normpath(sys.prefix)
EXEC_PREFIX = os.path.normpath(sys.exec_prefix)
BASE_PREFIX = os.path.normpath(sys.base_prefix)
BASE_EXEC_PREFIX = os.path.normpath(sys.base_exec_prefix)

# Path to the base directory of the project. On Windows the binary may
# live kwenye project/PCbuild/win32 ama project/PCbuild/amd64.
# set kila cross builds
ikiwa "_PYTHON_PROJECT_BASE" kwenye os.environ:
    project_base = os.path.abspath(os.environ["_PYTHON_PROJECT_BASE"])
isipokua:
    ikiwa sys.executable:
        project_base = os.path.dirname(os.path.abspath(sys.executable))
    isipokua:
        # sys.executable can be empty ikiwa argv[0] has been changed na Python is
        # unable to retrieve the real program name
        project_base = os.getcwd()


# python_build: (Boolean) ikiwa true, we're either building Python ama
# building an extension ukijumuisha an un-installed Python, so we use
# different (hard-wired) directories.
eleza _is_python_source_dir(d):
    kila fn kwenye ("Setup", "Setup.local"):
        ikiwa os.path.isfile(os.path.join(d, "Modules", fn)):
            rudisha Kweli
    rudisha Uongo

_sys_home = getattr(sys, '_home', Tupu)

ikiwa os.name == 'nt':
    eleza _fix_pcbuild(d):
        ikiwa d na os.path.normcase(d).startswith(
                os.path.normcase(os.path.join(PREFIX, "PCbuild"))):
            rudisha PREFIX
        rudisha d
    project_base = _fix_pcbuild(project_base)
    _sys_home = _fix_pcbuild(_sys_home)

eleza _python_build():
    ikiwa _sys_home:
        rudisha _is_python_source_dir(_sys_home)
    rudisha _is_python_source_dir(project_base)

python_build = _python_build()


# Calculate the build qualifier flags ikiwa they are defined.  Adding the flags
# to the include na lib directories only makes sense kila an installation, sio
# an in-source build.
build_flags = ''
jaribu:
    ikiwa sio python_build:
        build_flags = sys.abiflags
tatizo AttributeError:
    # It's sio a configure-based build, so the sys module doesn't have
    # this attribute, which ni fine.
    pita

eleza get_python_version():
    """Return a string containing the major na minor Python version,
    leaving off the patchlevel.  Sample rudisha values could be '1.5'
    ama '2.2'.
    """
    rudisha '%d.%d' % sys.version_info[:2]


eleza get_python_inc(plat_specific=0, prefix=Tupu):
    """Return the directory containing installed Python header files.

    If 'plat_specific' ni false (the default), this ni the path to the
    non-platform-specific header files, i.e. Python.h na so on;
    otherwise, this ni the path to platform-specific header files
    (namely pyconfig.h).

    If 'prefix' ni supplied, use it instead of sys.base_prefix ama
    sys.base_exec_prefix -- i.e., ignore 'plat_specific'.
    """
    ikiwa prefix ni Tupu:
        prefix = plat_specific na BASE_EXEC_PREFIX ama BASE_PREFIX
    ikiwa os.name == "posix":
        ikiwa python_build:
            # Assume the executable ni kwenye the build directory.  The
            # pyconfig.h file should be kwenye the same directory.  Since
            # the build directory may sio be the source directory, we
            # must use "srcdir" kutoka the makefile to find the "Include"
            # directory.
            ikiwa plat_specific:
                rudisha _sys_home ama project_base
            isipokua:
                incdir = os.path.join(get_config_var('srcdir'), 'Include')
                rudisha os.path.normpath(incdir)
        python_dir = 'python' + get_python_version() + build_flags
        rudisha os.path.join(prefix, "include", python_dir)
    lasivyo os.name == "nt":
        ikiwa python_build:
            # Include both the include na PC dir to ensure we can find
            # pyconfig.h
            rudisha (os.path.join(prefix, "include") + os.path.pathsep +
                    os.path.join(prefix, "PC"))
        rudisha os.path.join(prefix, "include")
    isipokua:
        ashiria DistutilsPlatformError(
            "I don't know where Python installs its C header files "
            "on platform '%s'" % os.name)


eleza get_python_lib(plat_specific=0, standard_lib=0, prefix=Tupu):
    """Return the directory containing the Python library (standard ama
    site additions).

    If 'plat_specific' ni true, rudisha the directory containing
    platform-specific modules, i.e. any module kutoka a non-pure-Python
    module distribution; otherwise, rudisha the platform-shared library
    directory.  If 'standard_lib' ni true, rudisha the directory
    containing standard Python library modules; otherwise, rudisha the
    directory kila site-specific modules.

    If 'prefix' ni supplied, use it instead of sys.base_prefix ama
    sys.base_exec_prefix -- i.e., ignore 'plat_specific'.
    """
    ikiwa prefix ni Tupu:
        ikiwa standard_lib:
            prefix = plat_specific na BASE_EXEC_PREFIX ama BASE_PREFIX
        isipokua:
            prefix = plat_specific na EXEC_PREFIX ama PREFIX

    ikiwa os.name == "posix":
        libpython = os.path.join(prefix,
                                 "lib", "python" + get_python_version())
        ikiwa standard_lib:
            rudisha libpython
        isipokua:
            rudisha os.path.join(libpython, "site-packages")
    lasivyo os.name == "nt":
        ikiwa standard_lib:
            rudisha os.path.join(prefix, "Lib")
        isipokua:
            rudisha os.path.join(prefix, "Lib", "site-packages")
    isipokua:
        ashiria DistutilsPlatformError(
            "I don't know where Python installs its library "
            "on platform '%s'" % os.name)



eleza customize_compiler(compiler):
    """Do any platform-specific customization of a CCompiler instance.

    Mainly needed on Unix, so we can plug kwenye the information that
    varies across Unices na ni stored kwenye Python's Makefile.
    """
    ikiwa compiler.compiler_type == "unix":
        ikiwa sys.platform == "darwin":
            # Perform first-time customization of compiler-related
            # config vars on OS X now that we know we need a compiler.
            # This ni primarily to support Pythons kutoka binary
            # installers.  The kind na paths to build tools on
            # the user system may vary significantly kutoka the system
            # that Python itself was built on.  Also the user OS
            # version na build tools may sio support the same set
            # of CPU architectures kila universal builds.
            global _config_vars
            # Use get_config_var() to ensure _config_vars ni initialized.
            ikiwa sio get_config_var('CUSTOMIZED_OSX_COMPILER'):
                agiza _osx_support
                _osx_support.customize_compiler(_config_vars)
                _config_vars['CUSTOMIZED_OSX_COMPILER'] = 'Kweli'

        (cc, cxx, cflags, ccshared, ldshared, shlib_suffix, ar, ar_flags) = \
            get_config_vars('CC', 'CXX', 'CFLAGS',
                            'CCSHARED', 'LDSHARED', 'SHLIB_SUFFIX', 'AR', 'ARFLAGS')

        ikiwa 'CC' kwenye os.environ:
            newcc = os.environ['CC']
            ikiwa (sys.platform == 'darwin'
                    na 'LDSHARED' haiko kwenye os.environ
                    na ldshared.startswith(cc)):
                # On OS X, ikiwa CC ni overridden, use that kama the default
                #       command kila LDSHARED kama well
                ldshared = newcc + ldshared[len(cc):]
            cc = newcc
        ikiwa 'CXX' kwenye os.environ:
            cxx = os.environ['CXX']
        ikiwa 'LDSHARED' kwenye os.environ:
            ldshared = os.environ['LDSHARED']
        ikiwa 'CPP' kwenye os.environ:
            cpp = os.environ['CPP']
        isipokua:
            cpp = cc + " -E"           # sio always
        ikiwa 'LDFLAGS' kwenye os.environ:
            ldshared = ldshared + ' ' + os.environ['LDFLAGS']
        ikiwa 'CFLAGS' kwenye os.environ:
            cflags = cflags + ' ' + os.environ['CFLAGS']
            ldshared = ldshared + ' ' + os.environ['CFLAGS']
        ikiwa 'CPPFLAGS' kwenye os.environ:
            cpp = cpp + ' ' + os.environ['CPPFLAGS']
            cflags = cflags + ' ' + os.environ['CPPFLAGS']
            ldshared = ldshared + ' ' + os.environ['CPPFLAGS']
        ikiwa 'AR' kwenye os.environ:
            ar = os.environ['AR']
        ikiwa 'ARFLAGS' kwenye os.environ:
            archiver = ar + ' ' + os.environ['ARFLAGS']
        isipokua:
            archiver = ar + ' ' + ar_flags

        cc_cmd = cc + ' ' + cflags
        compiler.set_executables(
            preprocessor=cpp,
            compiler=cc_cmd,
            compiler_so=cc_cmd + ' ' + ccshared,
            compiler_cxx=cxx,
            linker_so=ldshared,
            linker_exe=cc,
            archiver=archiver)

        compiler.shared_lib_extension = shlib_suffix


eleza get_config_h_filename():
    """Return full pathname of installed pyconfig.h file."""
    ikiwa python_build:
        ikiwa os.name == "nt":
            inc_dir = os.path.join(_sys_home ama project_base, "PC")
        isipokua:
            inc_dir = _sys_home ama project_base
    isipokua:
        inc_dir = get_python_inc(plat_specific=1)

    rudisha os.path.join(inc_dir, 'pyconfig.h')


eleza get_makefile_filename():
    """Return full pathname of installed Makefile kutoka the Python build."""
    ikiwa python_build:
        rudisha os.path.join(_sys_home ama project_base, "Makefile")
    lib_dir = get_python_lib(plat_specific=0, standard_lib=1)
    config_file = 'config-{}{}'.format(get_python_version(), build_flags)
    ikiwa hasattr(sys.implementation, '_multiarch'):
        config_file += '-%s' % sys.implementation._multiarch
    rudisha os.path.join(lib_dir, config_file, 'Makefile')


eleza parse_config_h(fp, g=Tupu):
    """Parse a config.h-style file.

    A dictionary containing name/value pairs ni returned.  If an
    optional dictionary ni pitaed kwenye kama the second argument, it is
    used instead of a new dictionary.
    """
    ikiwa g ni Tupu:
        g = {}
    define_rx = re.compile("#define ([A-Z][A-Za-z0-9_]+) (.*)\n")
    undef_rx = re.compile("/[*] #uneleza ([A-Z][A-Za-z0-9_]+) [*]/\n")
    #
    wakati Kweli:
        line = fp.readline()
        ikiwa sio line:
            koma
        m = define_rx.match(line)
        ikiwa m:
            n, v = m.group(1, 2)
            jaribu: v = int(v)
            tatizo ValueError: pita
            g[n] = v
        isipokua:
            m = undef_rx.match(line)
            ikiwa m:
                g[m.group(1)] = 0
    rudisha g


# Regexes needed kila parsing Makefile (and similar syntaxes,
# like old-style Setup files).
_variable_rx = re.compile(r"([a-zA-Z][a-zA-Z0-9_]+)\s*=\s*(.*)")
_findvar1_rx = re.compile(r"\$\(([A-Za-z][A-Za-z0-9_]*)\)")
_findvar2_rx = re.compile(r"\${([A-Za-z][A-Za-z0-9_]*)}")

eleza parse_makefile(fn, g=Tupu):
    """Parse a Makefile-style file.

    A dictionary containing name/value pairs ni returned.  If an
    optional dictionary ni pitaed kwenye kama the second argument, it is
    used instead of a new dictionary.
    """
    kutoka distutils.text_file agiza TextFile
    fp = TextFile(fn, strip_comments=1, skip_blanks=1, join_lines=1, errors="surrogateescape")

    ikiwa g ni Tupu:
        g = {}
    done = {}
    notdone = {}

    wakati Kweli:
        line = fp.readline()
        ikiwa line ni Tupu: # eof
            koma
        m = _variable_rx.match(line)
        ikiwa m:
            n, v = m.group(1, 2)
            v = v.strip()
            # `$$' ni a literal `$' kwenye make
            tmpv = v.replace('$$', '')

            ikiwa "$" kwenye tmpv:
                notdone[n] = v
            isipokua:
                jaribu:
                    v = int(v)
                tatizo ValueError:
                    # insert literal `$'
                    done[n] = v.replace('$$', '$')
                isipokua:
                    done[n] = v

    # Variables ukijumuisha a 'PY_' prefix kwenye the makefile. These need to
    # be made available without that prefix through sysconfig.
    # Special care ni needed to ensure that variable expansion works, even
    # ikiwa the expansion uses the name without a prefix.
    renamed_variables = ('CFLAGS', 'LDFLAGS', 'CPPFLAGS')

    # do variable interpolation here
    wakati notdone:
        kila name kwenye list(notdone):
            value = notdone[name]
            m = _findvar1_rx.search(value) ama _findvar2_rx.search(value)
            ikiwa m:
                n = m.group(1)
                found = Kweli
                ikiwa n kwenye done:
                    item = str(done[n])
                lasivyo n kwenye notdone:
                    # get it on a subsequent round
                    found = Uongo
                lasivyo n kwenye os.environ:
                    # do it like make: fall back to environment
                    item = os.environ[n]

                lasivyo n kwenye renamed_variables:
                    ikiwa name.startswith('PY_') na name[3:] kwenye renamed_variables:
                        item = ""

                    lasivyo 'PY_' + n kwenye notdone:
                        found = Uongo

                    isipokua:
                        item = str(done['PY_' + n])
                isipokua:
                    done[n] = item = ""
                ikiwa found:
                    after = value[m.end():]
                    value = value[:m.start()] + item + after
                    ikiwa "$" kwenye after:
                        notdone[name] = value
                    isipokua:
                        jaribu: value = int(value)
                        tatizo ValueError:
                            done[name] = value.strip()
                        isipokua:
                            done[name] = value
                        toa notdone[name]

                        ikiwa name.startswith('PY_') \
                            na name[3:] kwenye renamed_variables:

                            name = name[3:]
                            ikiwa name haiko kwenye done:
                                done[name] = value
            isipokua:
                # bogus variable reference; just drop it since we can't deal
                toa notdone[name]

    fp.close()

    # strip spurious spaces
    kila k, v kwenye done.items():
        ikiwa isinstance(v, str):
            done[k] = v.strip()

    # save the results kwenye the global dictionary
    g.update(done)
    rudisha g


eleza expand_makefile_vars(s, vars):
    """Expand Makefile-style variables -- "${foo}" ama "$(foo)" -- kwenye
    'string' according to 'vars' (a dictionary mapping variable names to
    values).  Variables sio present kwenye 'vars' are silently expanded to the
    empty string.  The variable values kwenye 'vars' should sio contain further
    variable expansions; ikiwa 'vars' ni the output of 'parse_makefile()',
    you're fine.  Returns a variable-expanded version of 's'.
    """

    # This algorithm does multiple expansion, so ikiwa vars['foo'] contains
    # "${bar}", it will expand ${foo} to ${bar}, na then expand
    # ${bar}... na so forth.  This ni fine kama long kama 'vars' comes from
    # 'parse_makefile()', which takes care of such expansions eagerly,
    # according to make's variable expansion semantics.

    wakati Kweli:
        m = _findvar1_rx.search(s) ama _findvar2_rx.search(s)
        ikiwa m:
            (beg, end) = m.span()
            s = s[0:beg] + vars.get(m.group(1)) + s[end:]
        isipokua:
            koma
    rudisha s


_config_vars = Tupu

eleza _init_posix():
    """Initialize the module kama appropriate kila POSIX systems."""
    # _sysconfigdata ni generated at build time, see the sysconfig module
    name = os.environ.get('_PYTHON_SYSCONFIGDATA_NAME',
        '_sysconfigdata_{abi}_{platform}_{multiarch}'.format(
        abi=sys.abiflags,
        platform=sys.platform,
        multiarch=getattr(sys.implementation, '_multiarch', ''),
    ))
    _temp = __import__(name, globals(), locals(), ['build_time_vars'], 0)
    build_time_vars = _temp.build_time_vars
    global _config_vars
    _config_vars = {}
    _config_vars.update(build_time_vars)


eleza _init_nt():
    """Initialize the module kama appropriate kila NT"""
    g = {}
    # set basic install directories
    g['LIBDEST'] = get_python_lib(plat_specific=0, standard_lib=1)
    g['BINLIBDEST'] = get_python_lib(plat_specific=1, standard_lib=1)

    # XXX hmmm.. a normal install puts include files here
    g['INCLUDEPY'] = get_python_inc(plat_specific=0)

    g['EXT_SUFFIX'] = _imp.extension_suffixes()[0]
    g['EXE'] = ".exe"
    g['VERSION'] = get_python_version().replace(".", "")
    g['BINDIR'] = os.path.dirname(os.path.abspath(sys.executable))

    global _config_vars
    _config_vars = g


eleza get_config_vars(*args):
    """With no arguments, rudisha a dictionary of all configuration
    variables relevant kila the current platform.  Generally this includes
    everything needed to build extensions na install both pure modules na
    extensions.  On Unix, this means every variable defined kwenye Python's
    installed Makefile; on Windows it's a much smaller set.

    With arguments, rudisha a list of values that result kutoka looking up
    each argument kwenye the configuration variable dictionary.
    """
    global _config_vars
    ikiwa _config_vars ni Tupu:
        func = globals().get("_init_" + os.name)
        ikiwa func:
            func()
        isipokua:
            _config_vars = {}

        # Normalized versions of prefix na exec_prefix are handy to have;
        # kwenye fact, these are the standard versions used most places kwenye the
        # Distutils.
        _config_vars['prefix'] = PREFIX
        _config_vars['exec_prefix'] = EXEC_PREFIX

        # For backward compatibility, see issue19555
        SO = _config_vars.get('EXT_SUFFIX')
        ikiwa SO ni sio Tupu:
            _config_vars['SO'] = SO

        # Always convert srcdir to an absolute path
        srcdir = _config_vars.get('srcdir', project_base)
        ikiwa os.name == 'posix':
            ikiwa python_build:
                # If srcdir ni a relative path (typically '.' ama '..')
                # then it should be interpreted relative to the directory
                # containing Makefile.
                base = os.path.dirname(get_makefile_filename())
                srcdir = os.path.join(base, srcdir)
            isipokua:
                # srcdir ni sio meaningful since the installation is
                # spread about the filesystem.  We choose the
                # directory containing the Makefile since we know it
                # exists.
                srcdir = os.path.dirname(get_makefile_filename())
        _config_vars['srcdir'] = os.path.abspath(os.path.normpath(srcdir))

        # Convert srcdir into an absolute path ikiwa it appears necessary.
        # Normally it ni relative to the build directory.  However, during
        # testing, kila example, we might be running a non-installed python
        # kutoka a different directory.
        ikiwa python_build na os.name == "posix":
            base = project_base
            ikiwa (sio os.path.isabs(_config_vars['srcdir']) na
                base != os.getcwd()):
                # srcdir ni relative na we are haiko kwenye the same directory
                # kama the executable. Assume executable ni kwenye the build
                # directory na make srcdir absolute.
                srcdir = os.path.join(base, _config_vars['srcdir'])
                _config_vars['srcdir'] = os.path.normpath(srcdir)

        # OS X platforms require special customization to handle
        # multi-architecture, multi-os-version installers
        ikiwa sys.platform == 'darwin':
            agiza _osx_support
            _osx_support.customize_config_vars(_config_vars)

    ikiwa args:
        vals = []
        kila name kwenye args:
            vals.append(_config_vars.get(name))
        rudisha vals
    isipokua:
        rudisha _config_vars

eleza get_config_var(name):
    """Return the value of a single variable using the dictionary
    returned by 'get_config_vars()'.  Equivalent to
    get_config_vars().get(name)
    """
    ikiwa name == 'SO':
        agiza warnings
        warnings.warn('SO ni deprecated, use EXT_SUFFIX', DeprecationWarning, 2)
    rudisha get_config_vars().get(name)
