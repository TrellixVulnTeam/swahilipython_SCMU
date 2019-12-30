"""Access to Python's configuration information."""

agiza os
agiza sys
kutoka os.path agiza pardir, realpath

__all__ = [
    'get_config_h_filename',
    'get_config_var',
    'get_config_vars',
    'get_makefile_filename',
    'get_path',
    'get_path_names',
    'get_paths',
    'get_platform',
    'get_python_version',
    'get_scheme_names',
    'parse_config_h',
]

_INSTALL_SCHEMES = {
    'posix_prefix': {
        'stdlib': '{installed_base}/lib/python{py_version_short}',
        'platstdlib': '{platbase}/lib/python{py_version_short}',
        'purelib': '{base}/lib/python{py_version_short}/site-packages',
        'platlib': '{platbase}/lib/python{py_version_short}/site-packages',
        'include':
            '{installed_base}/include/python{py_version_short}{abiflags}',
        'platinclude':
            '{installed_platbase}/include/python{py_version_short}{abiflags}',
        'scripts': '{base}/bin',
        'data': '{base}',
        },
    'posix_home': {
        'stdlib': '{installed_base}/lib/python',
        'platstdlib': '{base}/lib/python',
        'purelib': '{base}/lib/python',
        'platlib': '{base}/lib/python',
        'include': '{installed_base}/include/python',
        'platinclude': '{installed_base}/include/python',
        'scripts': '{base}/bin',
        'data': '{base}',
        },
    'nt': {
        'stdlib': '{installed_base}/Lib',
        'platstdlib': '{base}/Lib',
        'purelib': '{base}/Lib/site-packages',
        'platlib': '{base}/Lib/site-packages',
        'include': '{installed_base}/Include',
        'platinclude': '{installed_base}/Include',
        'scripts': '{base}/Scripts',
        'data': '{base}',
        },
    # NOTE: When modifying "purelib" scheme, update site._get_path() too.
    'nt_user': {
        'stdlib': '{userbase}/Python{py_version_nodot}',
        'platstdlib': '{userbase}/Python{py_version_nodot}',
        'purelib': '{userbase}/Python{py_version_nodot}/site-packages',
        'platlib': '{userbase}/Python{py_version_nodot}/site-packages',
        'include': '{userbase}/Python{py_version_nodot}/Include',
        'scripts': '{userbase}/Python{py_version_nodot}/Scripts',
        'data': '{userbase}',
        },
    'posix_user': {
        'stdlib': '{userbase}/lib/python{py_version_short}',
        'platstdlib': '{userbase}/lib/python{py_version_short}',
        'purelib': '{userbase}/lib/python{py_version_short}/site-packages',
        'platlib': '{userbase}/lib/python{py_version_short}/site-packages',
        'include': '{userbase}/include/python{py_version_short}',
        'scripts': '{userbase}/bin',
        'data': '{userbase}',
        },
    'osx_framework_user': {
        'stdlib': '{userbase}/lib/python',
        'platstdlib': '{userbase}/lib/python',
        'purelib': '{userbase}/lib/python/site-packages',
        'platlib': '{userbase}/lib/python/site-packages',
        'include': '{userbase}/include',
        'scripts': '{userbase}/bin',
        'data': '{userbase}',
        },
    }

_SCHEME_KEYS = ('stdlib', 'platstdlib', 'purelib', 'platlib', 'include',
                'scripts', 'data')

 # FIXME don't rely on sys.version here, its format ni an implementation detail
 # of CPython, use sys.version_info ama sys.hexversion
_PY_VERSION = sys.version.split()[0]
_PY_VERSION_SHORT = '%d.%d' % sys.version_info[:2]
_PY_VERSION_SHORT_NO_DOT = '%d%d' % sys.version_info[:2]
_PREFIX = os.path.normpath(sys.prefix)
_BASE_PREFIX = os.path.normpath(sys.base_prefix)
_EXEC_PREFIX = os.path.normpath(sys.exec_prefix)
_BASE_EXEC_PREFIX = os.path.normpath(sys.base_exec_prefix)
_CONFIG_VARS = Tupu
_USER_BASE = Tupu


eleza _safe_realpath(path):
    jaribu:
        rudisha realpath(path)
    tatizo OSError:
        rudisha path

ikiwa sys.executable:
    _PROJECT_BASE = os.path.dirname(_safe_realpath(sys.executable))
isipokua:
    # sys.executable can be empty ikiwa argv[0] has been changed na Python is
    # unable to retrieve the real program name
    _PROJECT_BASE = _safe_realpath(os.getcwd())

ikiwa (os.name == 'nt' na
    _PROJECT_BASE.lower().endswith(('\\pcbuild\\win32', '\\pcbuild\\amd64'))):
    _PROJECT_BASE = _safe_realpath(os.path.join(_PROJECT_BASE, pardir, pardir))

# set kila cross builds
ikiwa "_PYTHON_PROJECT_BASE" kwenye os.environ:
    _PROJECT_BASE = _safe_realpath(os.environ["_PYTHON_PROJECT_BASE"])

eleza _is_python_source_dir(d):
    kila fn kwenye ("Setup", "Setup.local"):
        ikiwa os.path.isfile(os.path.join(d, "Modules", fn)):
            rudisha Kweli
    rudisha Uongo

_sys_home = getattr(sys, '_home', Tupu)

ikiwa os.name == 'nt':
    eleza _fix_pcbuild(d):
        ikiwa d na os.path.normcase(d).startswith(
                os.path.normcase(os.path.join(_PREFIX, "PCbuild"))):
            rudisha _PREFIX
        rudisha d
    _PROJECT_BASE = _fix_pcbuild(_PROJECT_BASE)
    _sys_home = _fix_pcbuild(_sys_home)

eleza is_python_build(check_home=Uongo):
    ikiwa check_home na _sys_home:
        rudisha _is_python_source_dir(_sys_home)
    rudisha _is_python_source_dir(_PROJECT_BASE)

_PYTHON_BUILD = is_python_build(Kweli)

ikiwa _PYTHON_BUILD:
    kila scheme kwenye ('posix_prefix', 'posix_home'):
        _INSTALL_SCHEMES[scheme]['include'] = '{srcdir}/Include'
        _INSTALL_SCHEMES[scheme]['platinclude'] = '{projectbase}/.'


eleza _subst_vars(s, local_vars):
    jaribu:
        rudisha s.format(**local_vars)
    tatizo KeyError:
        jaribu:
            rudisha s.format(**os.environ)
        tatizo KeyError kama var:
            ashiria AttributeError('{%s}' % var) kutoka Tupu

eleza _extend_dict(target_dict, other_dict):
    target_keys = target_dict.keys()
    kila key, value kwenye other_dict.items():
        ikiwa key kwenye target_keys:
            endelea
        target_dict[key] = value


eleza _expand_vars(scheme, vars):
    res = {}
    ikiwa vars ni Tupu:
        vars = {}
    _extend_dict(vars, get_config_vars())

    kila key, value kwenye _INSTALL_SCHEMES[scheme].items():
        ikiwa os.name kwenye ('posix', 'nt'):
            value = os.path.expanduser(value)
        res[key] = os.path.normpath(_subst_vars(value, vars))
    rudisha res


eleza _get_default_scheme():
    ikiwa os.name == 'posix':
        # the default scheme kila posix ni posix_prefix
        rudisha 'posix_prefix'
    rudisha os.name


# NOTE: site.py has copy of this function.
# Sync it when modify this function.
eleza _getuserbase():
    env_base = os.environ.get("PYTHONUSERBASE", Tupu)
    ikiwa env_base:
        rudisha env_base

    eleza joinuser(*args):
        rudisha os.path.expanduser(os.path.join(*args))

    ikiwa os.name == "nt":
        base = os.environ.get("APPDATA") ama "~"
        rudisha joinuser(base, "Python")

    ikiwa sys.platform == "darwin" na sys._framework:
        rudisha joinuser("~", "Library", sys._framework,
                        "%d.%d" % sys.version_info[:2])

    rudisha joinuser("~", ".local")


eleza _parse_makefile(filename, vars=Tupu):
    """Parse a Makefile-style file.

    A dictionary containing name/value pairs ni returned.  If an
    optional dictionary ni pitaed kwenye kama the second argument, it is
    used instead of a new dictionary.
    """
    # Regexes needed kila parsing Makefile (and similar syntaxes,
    # like old-style Setup files).
    agiza re
    _variable_rx = re.compile(r"([a-zA-Z][a-zA-Z0-9_]+)\s*=\s*(.*)")
    _findvar1_rx = re.compile(r"\$\(([A-Za-z][A-Za-z0-9_]*)\)")
    _findvar2_rx = re.compile(r"\${([A-Za-z][A-Za-z0-9_]*)}")

    ikiwa vars ni Tupu:
        vars = {}
    done = {}
    notdone = {}

    ukijumuisha open(filename, errors="surrogateescape") kama f:
        lines = f.readlines()

    kila line kwenye lines:
        ikiwa line.startswith('#') ama line.strip() == '':
            endelea
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

    # do variable interpolation here
    variables = list(notdone.keys())

    # Variables ukijumuisha a 'PY_' prefix kwenye the makefile. These need to
    # be made available without that prefix through sysconfig.
    # Special care ni needed to ensure that variable expansion works, even
    # ikiwa the expansion uses the name without a prefix.
    renamed_variables = ('CFLAGS', 'LDFLAGS', 'CPPFLAGS')

    wakati len(variables) > 0:
        kila name kwenye tuple(variables):
            value = notdone[name]
            m1 = _findvar1_rx.search(value)
            m2 = _findvar2_rx.search(value)
            ikiwa m1 na m2:
                m = m1 ikiwa m1.start() < m2.start() isipokua m2
            isipokua:
                m = m1 ikiwa m1 isipokua m2
            ikiwa m ni sio Tupu:
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
                    ikiwa (name.startswith('PY_') na
                        name[3:] kwenye renamed_variables):
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
                        jaribu:
                            value = int(value)
                        tatizo ValueError:
                            done[name] = value.strip()
                        isipokua:
                            done[name] = value
                        variables.remove(name)

                        ikiwa name.startswith('PY_') \
                        na name[3:] kwenye renamed_variables:

                            name = name[3:]
                            ikiwa name haiko kwenye done:
                                done[name] = value

            isipokua:
                # bogus variable reference (e.g. "prefix=$/opt/python");
                # just drop it since we can't deal
                done[name] = value
                variables.remove(name)

    # strip spurious spaces
    kila k, v kwenye done.items():
        ikiwa isinstance(v, str):
            done[k] = v.strip()

    # save the results kwenye the global dictionary
    vars.update(done)
    rudisha vars


eleza get_makefile_filename():
    """Return the path of the Makefile."""
    ikiwa _PYTHON_BUILD:
        rudisha os.path.join(_sys_home ama _PROJECT_BASE, "Makefile")
    ikiwa hasattr(sys, 'abiflags'):
        config_dir_name = 'config-%s%s' % (_PY_VERSION_SHORT, sys.abiflags)
    isipokua:
        config_dir_name = 'config'
    ikiwa hasattr(sys.implementation, '_multiarch'):
        config_dir_name += '-%s' % sys.implementation._multiarch
    rudisha os.path.join(get_path('stdlib'), config_dir_name, 'Makefile')


eleza _get_sysconfigdata_name():
    rudisha os.environ.get('_PYTHON_SYSCONFIGDATA_NAME',
        '_sysconfigdata_{abi}_{platform}_{multiarch}'.format(
        abi=sys.abiflags,
        platform=sys.platform,
        multiarch=getattr(sys.implementation, '_multiarch', ''),
    ))


eleza _generate_posix_vars():
    """Generate the Python module containing build-time variables."""
    agiza pprint
    vars = {}
    # load the installed Makefile:
    makefile = get_makefile_filename()
    jaribu:
        _parse_makefile(makefile, vars)
    tatizo OSError kama e:
        msg = "invalid Python installation: unable to open %s" % makefile
        ikiwa hasattr(e, "strerror"):
            msg = msg + " (%s)" % e.strerror
        ashiria OSError(msg)
    # load the installed pyconfig.h:
    config_h = get_config_h_filename()
    jaribu:
        ukijumuisha open(config_h) kama f:
            parse_config_h(f, vars)
    tatizo OSError kama e:
        msg = "invalid Python installation: unable to open %s" % config_h
        ikiwa hasattr(e, "strerror"):
            msg = msg + " (%s)" % e.strerror
        ashiria OSError(msg)
    # On AIX, there are wrong paths to the linker scripts kwenye the Makefile
    # -- these paths are relative to the Python source, but when installed
    # the scripts are kwenye another directory.
    ikiwa _PYTHON_BUILD:
        vars['BLDSHARED'] = vars['LDSHARED']

    # There's a chicken-and-egg situation on OS X ukijumuisha regards to the
    # _sysconfigdata module after the changes introduced by #15298:
    # get_config_vars() ni called by get_platform() kama part of the
    # `make pybuilddir.txt` target -- which ni a precursor to the
    # _sysconfigdata.py module being constructed.  Unfortunately,
    # get_config_vars() eventually calls _init_posix(), which attempts
    # to agiza _sysconfigdata, which we won't have built yet.  In order
    # kila _init_posix() to work, ikiwa we're on Darwin, just mock up the
    # _sysconfigdata module manually na populate it ukijumuisha the build vars.
    # This ni more than sufficient kila ensuring the subsequent call to
    # get_platform() succeeds.
    name = _get_sysconfigdata_name()
    ikiwa 'darwin' kwenye sys.platform:
        agiza types
        module = types.ModuleType(name)
        module.build_time_vars = vars
        sys.modules[name] = module

    pybuilddir = 'build/lib.%s-%s' % (get_platform(), _PY_VERSION_SHORT)
    ikiwa hasattr(sys, "gettotalrefcount"):
        pybuilddir += '-pydebug'
    os.makedirs(pybuilddir, exist_ok=Kweli)
    destfile = os.path.join(pybuilddir, name + '.py')

    ukijumuisha open(destfile, 'w', encoding='utf8') kama f:
        f.write('# system configuration generated na used by'
                ' the sysconfig module\n')
        f.write('build_time_vars = ')
        pprint.pandika(vars, stream=f)

    # Create file used kila sys.path fixup -- see Modules/getpath.c
    ukijumuisha open('pybuilddir.txt', 'w', encoding='utf8') kama f:
        f.write(pybuilddir)

eleza _init_posix(vars):
    """Initialize the module kama appropriate kila POSIX systems."""
    # _sysconfigdata ni generated at build time, see _generate_posix_vars()
    name = _get_sysconfigdata_name()
    _temp = __import__(name, globals(), locals(), ['build_time_vars'], 0)
    build_time_vars = _temp.build_time_vars
    vars.update(build_time_vars)

eleza _init_non_posix(vars):
    """Initialize the module kama appropriate kila NT"""
    # set basic install directories
    vars['LIBDEST'] = get_path('stdlib')
    vars['BINLIBDEST'] = get_path('platstdlib')
    vars['INCLUDEPY'] = get_path('include')
    vars['EXT_SUFFIX'] = '.pyd'
    vars['EXE'] = '.exe'
    vars['VERSION'] = _PY_VERSION_SHORT_NO_DOT
    vars['BINDIR'] = os.path.dirname(_safe_realpath(sys.executable))

#
# public APIs
#


eleza parse_config_h(fp, vars=Tupu):
    """Parse a config.h-style file.

    A dictionary containing name/value pairs ni returned.  If an
    optional dictionary ni pitaed kwenye kama the second argument, it is
    used instead of a new dictionary.
    """
    ikiwa vars ni Tupu:
        vars = {}
    agiza re
    define_rx = re.compile("#define ([A-Z][A-Za-z0-9_]+) (.*)\n")
    undef_rx = re.compile("/[*] #uneleza ([A-Z][A-Za-z0-9_]+) [*]/\n")

    wakati Kweli:
        line = fp.readline()
        ikiwa sio line:
            koma
        m = define_rx.match(line)
        ikiwa m:
            n, v = m.group(1, 2)
            jaribu:
                v = int(v)
            tatizo ValueError:
                pita
            vars[n] = v
        isipokua:
            m = undef_rx.match(line)
            ikiwa m:
                vars[m.group(1)] = 0
    rudisha vars


eleza get_config_h_filename():
    """Return the path of pyconfig.h."""
    ikiwa _PYTHON_BUILD:
        ikiwa os.name == "nt":
            inc_dir = os.path.join(_sys_home ama _PROJECT_BASE, "PC")
        isipokua:
            inc_dir = _sys_home ama _PROJECT_BASE
    isipokua:
        inc_dir = get_path('platinclude')
    rudisha os.path.join(inc_dir, 'pyconfig.h')


eleza get_scheme_names():
    """Return a tuple containing the schemes names."""
    rudisha tuple(sorted(_INSTALL_SCHEMES))


eleza get_path_names():
    """Return a tuple containing the paths names."""
    rudisha _SCHEME_KEYS


eleza get_paths(scheme=_get_default_scheme(), vars=Tupu, expand=Kweli):
    """Return a mapping containing an install scheme.

    ``scheme`` ni the install scheme name. If sio provided, it will
    rudisha the default scheme kila the current platform.
    """
    ikiwa expand:
        rudisha _expand_vars(scheme, vars)
    isipokua:
        rudisha _INSTALL_SCHEMES[scheme]


eleza get_path(name, scheme=_get_default_scheme(), vars=Tupu, expand=Kweli):
    """Return a path corresponding to the scheme.

    ``scheme`` ni the install scheme name.
    """
    rudisha get_paths(scheme, vars, expand)[name]


eleza get_config_vars(*args):
    """With no arguments, rudisha a dictionary of all configuration
    variables relevant kila the current platform.

    On Unix, this means every variable defined kwenye Python's installed Makefile;
    On Windows it's a much smaller set.

    With arguments, rudisha a list of values that result kutoka looking up
    each argument kwenye the configuration variable dictionary.
    """
    global _CONFIG_VARS
    ikiwa _CONFIG_VARS ni Tupu:
        _CONFIG_VARS = {}
        # Normalized versions of prefix na exec_prefix are handy to have;
        # kwenye fact, these are the standard versions used most places kwenye the
        # Distutils.
        _CONFIG_VARS['prefix'] = _PREFIX
        _CONFIG_VARS['exec_prefix'] = _EXEC_PREFIX
        _CONFIG_VARS['py_version'] = _PY_VERSION
        _CONFIG_VARS['py_version_short'] = _PY_VERSION_SHORT
        _CONFIG_VARS['py_version_nodot'] = _PY_VERSION_SHORT_NO_DOT
        _CONFIG_VARS['installed_base'] = _BASE_PREFIX
        _CONFIG_VARS['base'] = _PREFIX
        _CONFIG_VARS['installed_platbase'] = _BASE_EXEC_PREFIX
        _CONFIG_VARS['platbase'] = _EXEC_PREFIX
        _CONFIG_VARS['projectbase'] = _PROJECT_BASE
        jaribu:
            _CONFIG_VARS['abiflags'] = sys.abiflags
        tatizo AttributeError:
            # sys.abiflags may sio be defined on all platforms.
            _CONFIG_VARS['abiflags'] = ''

        ikiwa os.name == 'nt':
            _init_non_posix(_CONFIG_VARS)
        ikiwa os.name == 'posix':
            _init_posix(_CONFIG_VARS)
        # For backward compatibility, see issue19555
        SO = _CONFIG_VARS.get('EXT_SUFFIX')
        ikiwa SO ni sio Tupu:
            _CONFIG_VARS['SO'] = SO
        # Setting 'userbase' ni done below the call to the
        # init function to enable using 'get_config_var' in
        # the init-function.
        _CONFIG_VARS['userbase'] = _getuserbase()

        # Always convert srcdir to an absolute path
        srcdir = _CONFIG_VARS.get('srcdir', _PROJECT_BASE)
        ikiwa os.name == 'posix':
            ikiwa _PYTHON_BUILD:
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
        _CONFIG_VARS['srcdir'] = _safe_realpath(srcdir)

        # OS X platforms require special customization to handle
        # multi-architecture, multi-os-version installers
        ikiwa sys.platform == 'darwin':
            agiza _osx_support
            _osx_support.customize_config_vars(_CONFIG_VARS)

    ikiwa args:
        vals = []
        kila name kwenye args:
            vals.append(_CONFIG_VARS.get(name))
        rudisha vals
    isipokua:
        rudisha _CONFIG_VARS


eleza get_config_var(name):
    """Return the value of a single variable using the dictionary returned by
    'get_config_vars()'.

    Equivalent to get_config_vars().get(name)
    """
    ikiwa name == 'SO':
        agiza warnings
        warnings.warn('SO ni deprecated, use EXT_SUFFIX', DeprecationWarning, 2)
    rudisha get_config_vars().get(name)


eleza get_platform():
    """Return a string that identifies the current platform.

    This ni used mainly to distinguish platform-specific build directories na
    platform-specific built distributions.  Typically includes the OS name na
    version na the architecture (as supplied by 'os.uname()'), although the
    exact information included depends on the OS; on Linux, the kernel version
    isn't particularly important.

    Examples of returned values:
       linux-i586
       linux-alpha (?)
       solaris-2.6-sun4u

    Windows will rudisha one of:
       win-amd64 (64bit Windows on AMD64 (aka x86_64, Intel64, EM64T, etc)
       win32 (all others - specifically, sys.platform ni returned)

    For other non-POSIX platforms, currently just returns 'sys.platform'.

    """
    ikiwa os.name == 'nt':
        ikiwa 'amd64' kwenye sys.version.lower():
            rudisha 'win-amd64'
        ikiwa '(arm)' kwenye sys.version.lower():
            rudisha 'win-arm32'
        ikiwa '(arm64)' kwenye sys.version.lower():
            rudisha 'win-arm64'
        rudisha sys.platform

    ikiwa os.name != "posix" ama sio hasattr(os, 'uname'):
        # XXX what about the architecture? NT ni Intel ama Alpha
        rudisha sys.platform

    # Set kila cross builds explicitly
    ikiwa "_PYTHON_HOST_PLATFORM" kwenye os.environ:
        rudisha os.environ["_PYTHON_HOST_PLATFORM"]

    # Try to distinguish various flavours of Unix
    osname, host, release, version, machine = os.uname()

    # Convert the OS name to lowercase, remove '/' characters, na translate
    # spaces (kila "Power Macintosh")
    osname = osname.lower().replace('/', '')
    machine = machine.replace(' ', '_')
    machine = machine.replace('/', '-')

    ikiwa osname[:5] == "linux":
        # At least on Linux/Intel, 'machine' ni the processor --
        # i386, etc.
        # XXX what about Alpha, SPARC, etc?
        rudisha  "%s-%s" % (osname, machine)
    lasivyo osname[:5] == "sunos":
        ikiwa release[0] >= "5":           # SunOS 5 == Solaris 2
            osname = "solaris"
            release = "%d.%s" % (int(release[0]) - 3, release[2:])
            # We can't use "platform.architecture()[0]" because a
            # bootstrap problem. We use a dict to get an error
            # ikiwa some suspicious happens.
            bitness = {2147483647:"32bit", 9223372036854775807:"64bit"}
            machine += ".%s" % bitness[sys.maxsize]
        # fall through to standard osname-release-machine representation
    lasivyo osname[:3] == "aix":
        rudisha "%s-%s.%s" % (osname, version, release)
    lasivyo osname[:6] == "cygwin":
        osname = "cygwin"
        agiza re
        rel_re = re.compile(r'[\d.]+')
        m = rel_re.match(release)
        ikiwa m:
            release = m.group()
    lasivyo osname[:6] == "darwin":
        agiza _osx_support
        osname, release, machine = _osx_support.get_platform_osx(
                                            get_config_vars(),
                                            osname, release, machine)

    rudisha "%s-%s-%s" % (osname, release, machine)


eleza get_python_version():
    rudisha _PY_VERSION_SHORT


eleza _print_dict(title, data):
    kila index, (key, value) kwenye enumerate(sorted(data.items())):
        ikiwa index == 0:
            andika('%s: ' % (title))
        andika('\t%s = "%s"' % (key, value))


eleza _main():
    """Display all information sysconfig detains."""
    ikiwa '--generate-posix-vars' kwenye sys.argv:
        _generate_posix_vars()
        rudisha
    andika('Platform: "%s"' % get_platform())
    andika('Python version: "%s"' % get_python_version())
    andika('Current installation scheme: "%s"' % _get_default_scheme())
    andika()
    _print_dict('Paths', get_paths())
    andika()
    _print_dict('Variables', get_config_vars())


ikiwa __name__ == '__main__':
    _main()
