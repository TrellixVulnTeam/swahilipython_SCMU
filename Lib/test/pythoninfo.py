"""
Collect various information about Python to help debugging test failures.
"""
kutoka __future__ agiza print_function
agiza errno
agiza re
agiza sys
agiza traceback
agiza warnings


eleza normalize_text(text):
    ikiwa text is None:
        rudisha None
    text = str(text)
    text = re.sub(r'\s+', ' ', text)
    rudisha text.strip()


kundi PythonInfo:
    eleza __init__(self):
        self.info = {}

    eleza add(self, key, value):
        ikiwa key in self.info:
            raise ValueError("duplicate key: %r" % key)

        ikiwa value is None:
            return

        ikiwa not isinstance(value, int):
            ikiwa not isinstance(value, str):
                # convert other objects like sys.flags to string
                value = str(value)

            value = value.strip()
            ikiwa not value:
                return

        self.info[key] = value

    eleza get_infos(self):
        """
        Get information as a key:value dictionary where values are strings.
        """
        rudisha {key: str(value) for key, value in self.info.items()}


eleza copy_attributes(info_add, obj, name_fmt, attributes, *, formatter=None):
    for attr in attributes:
        value = getattr(obj, attr, None)
        ikiwa value is None:
            continue
        name = name_fmt % attr
        ikiwa formatter is not None:
            value = formatter(attr, value)
        info_add(name, value)


eleza copy_attr(info_add, name, mod, attr_name):
    try:
        value = getattr(mod, attr_name)
    except AttributeError:
        return
    info_add(name, value)


eleza call_func(info_add, name, mod, func_name, *, formatter=None):
    try:
        func = getattr(mod, func_name)
    except AttributeError:
        return
    value = func()
    ikiwa formatter is not None:
        value = formatter(value)
    info_add(name, value)


eleza collect_sys(info_add):
    attributes = (
        '_framework',
        'abiflags',
        'api_version',
        'builtin_module_names',
        'byteorder',
        'dont_write_bytecode',
        'executable',
        'flags',
        'float_info',
        'float_repr_style',
        'hash_info',
        'hexversion',
        'implementation',
        'int_info',
        'maxsize',
        'maxunicode',
        'path',
        'platform',
        'prefix',
        'thread_info',
        'version',
        'version_info',
        'winver',
    )
    copy_attributes(info_add, sys, 'sys.%s', attributes)

    call_func(info_add, 'sys.androidapilevel', sys, 'getandroidapilevel')
    call_func(info_add, 'sys.windowsversion', sys, 'getwindowsversion')

    encoding = sys.getfilesystemencoding()
    ikiwa hasattr(sys, 'getfilesystemencodeerrors'):
        encoding = '%s/%s' % (encoding, sys.getfilesystemencodeerrors())
    info_add('sys.filesystem_encoding', encoding)

    for name in ('stdin', 'stdout', 'stderr'):
        stream = getattr(sys, name)
        ikiwa stream is None:
            continue
        encoding = getattr(stream, 'encoding', None)
        ikiwa not encoding:
            continue
        errors = getattr(stream, 'errors', None)
        ikiwa errors:
            encoding = '%s/%s' % (encoding, errors)
        info_add('sys.%s.encoding' % name, encoding)

    # Were we compiled --with-pydebug or with #define Py_DEBUG?
    Py_DEBUG = hasattr(sys, 'gettotalrefcount')
    ikiwa Py_DEBUG:
        text = 'Yes (sys.gettotalrefcount() present)'
    else:
        text = 'No (sys.gettotalrefcount() missing)'
    info_add('Py_DEBUG', text)


eleza collect_platform(info_add):
    agiza platform

    arch = platform.architecture()
    arch = ' '.join(filter(bool, arch))
    info_add('platform.architecture', arch)

    info_add('platform.python_implementation',
             platform.python_implementation())
    info_add('platform.platform',
             platform.platform(aliased=True))

    libc_ver = ('%s %s' % platform.libc_ver()).strip()
    ikiwa libc_ver:
        info_add('platform.libc_ver', libc_ver)


eleza collect_locale(info_add):
    agiza locale

    info_add('locale.encoding', locale.getpreferredencoding(False))


eleza collect_builtins(info_add):
    info_add('builtins.float.float_format', float.__getformat__("float"))
    info_add('builtins.float.double_format', float.__getformat__("double"))


eleza collect_urandom(info_add):
    agiza os

    ikiwa hasattr(os, 'getrandom'):
        # PEP 524: Check ikiwa system urandom is initialized
        try:
            try:
                os.getrandom(1, os.GRND_NONBLOCK)
                state = 'ready (initialized)'
            except BlockingIOError as exc:
                state = 'not seeded yet (%s)' % exc
            info_add('os.getrandom', state)
        except OSError as exc:
            # Python was compiled on a more recent Linux version
            # than the current Linux kernel: ignore OSError(ENOSYS)
            ikiwa exc.errno != errno.ENOSYS:
                raise


eleza collect_os(info_add):
    agiza os

    eleza format_attr(attr, value):
        ikiwa attr in ('supports_follow_symlinks', 'supports_fd',
                    'supports_effective_ids'):
            rudisha str(sorted(func.__name__ for func in value))
        else:
            rudisha value

    attributes = (
        'name',
        'supports_bytes_environ',
        'supports_effective_ids',
        'supports_fd',
        'supports_follow_symlinks',
    )
    copy_attributes(info_add, os, 'os.%s', attributes, formatter=format_attr)

    call_func(info_add, 'os.getcwd', os, 'getcwd')

    call_func(info_add, 'os.getuid', os, 'getuid')
    call_func(info_add, 'os.getgid', os, 'getgid')
    call_func(info_add, 'os.uname', os, 'uname')

    eleza format_groups(groups):
        rudisha ', '.join(map(str, groups))

    call_func(info_add, 'os.getgroups', os, 'getgroups', formatter=format_groups)

    ikiwa hasattr(os, 'getlogin'):
        try:
            login = os.getlogin()
        except OSError:
            # getlogin() fails with "OSError: [Errno 25] Inappropriate ioctl
            # for device" on Travis CI
            pass
        else:
            info_add("os.login", login)

    call_func(info_add, 'os.cpu_count', os, 'cpu_count')
    call_func(info_add, 'os.getloadavg', os, 'getloadavg')

    # Environment variables used by the stdlib and tests. Don't log the full
    # environment: filter to list to not leak sensitive information.
    #
    # HTTP_PROXY is not logged because it can contain a password.
    ENV_VARS = frozenset((
        "APPDATA",
        "AR",
        "ARCHFLAGS",
        "ARFLAGS",
        "AUDIODEV",
        "CC",
        "CFLAGS",
        "COLUMNS",
        "COMPUTERNAME",
        "COMSPEC",
        "CPP",
        "CPPFLAGS",
        "DISPLAY",
        "DISTUTILS_DEBUG",
        "DISTUTILS_USE_SDK",
        "DYLD_LIBRARY_PATH",
        "ENSUREPIP_OPTIONS",
        "HISTORY_FILE",
        "HOME",
        "HOMEDRIVE",
        "HOMEPATH",
        "IDLESTARTUP",
        "LANG",
        "LDFLAGS",
        "LDSHARED",
        "LD_LIBRARY_PATH",
        "LINES",
        "MACOSX_DEPLOYMENT_TARGET",
        "MAILCAPS",
        "MAKEFLAGS",
        "MIXERDEV",
        "MSSDK",
        "PATH",
        "PATHEXT",
        "PIP_CONFIG_FILE",
        "PLAT",
        "POSIXLY_CORRECT",
        "PY_SAX_PARSER",
        "ProgramFiles",
        "ProgramFiles(x86)",
        "RUNNING_ON_VALGRIND",
        "SDK_TOOLS_BIN",
        "SERVER_SOFTWARE",
        "SHELL",
        "SOURCE_DATE_EPOCH",
        "SYSTEMROOT",
        "TEMP",
        "TERM",
        "TILE_LIBRARY",
        "TIX_LIBRARY",
        "TMP",
        "TMPDIR",
        "TRAVIS",
        "TZ",
        "USERPROFILE",
        "VIRTUAL_ENV",
        "WAYLAND_DISPLAY",
        "WINDIR",
        "_PYTHON_HOST_PLATFORM",
        "_PYTHON_PROJECT_BASE",
        "_PYTHON_SYSCONFIGDATA_NAME",
        "__PYVENV_LAUNCHER__",
    ))
    for name, value in os.environ.items():
        uname = name.upper()
        ikiwa (uname in ENV_VARS
           # Copy PYTHON* and LC_* variables
           or uname.startswith(("PYTHON", "LC_"))
           # Visual Studio: VS140COMNTOOLS
           or (uname.startswith("VS") and uname.endswith("COMNTOOLS"))):
            info_add('os.environ[%s]' % name, value)

    ikiwa hasattr(os, 'umask'):
        mask = os.umask(0)
        os.umask(mask)
        info_add("os.umask", '%03o' % mask)


eleza collect_pwd(info_add):
    try:
        agiza pwd
    except ImportError:
        return
    agiza os

    uid = os.getuid()
    try:
        entry = pwd.getpwuid(uid)
    except KeyError:
        entry = None

    info_add('pwd.getpwuid(%s)'% uid,
             entry ikiwa entry is not None else '<KeyError>')

    ikiwa entry is None:
        # there is nothing interesting to read ikiwa the current user identifier
        # is not the password database
        return

    ikiwa hasattr(os, 'getgrouplist'):
        groups = os.getgrouplist(entry.pw_name, entry.pw_gid)
        groups = ', '.join(map(str, groups))
        info_add('os.getgrouplist', groups)


eleza collect_readline(info_add):
    try:
        agiza readline
    except ImportError:
        return

    eleza format_attr(attr, value):
        ikiwa isinstance(value, int):
            rudisha "%#x" % value
        else:
            rudisha value

    attributes = (
        "_READLINE_VERSION",
        "_READLINE_RUNTIME_VERSION",
        "_READLINE_LIBRARY_VERSION",
    )
    copy_attributes(info_add, readline, 'readline.%s', attributes,
                    formatter=format_attr)

    ikiwa not hasattr(readline, "_READLINE_LIBRARY_VERSION"):
        # _READLINE_LIBRARY_VERSION has been added to CPython 3.7
        doc = getattr(readline, '__doc__', '')
        ikiwa 'libedit readline' in doc:
            info_add('readline.library', 'libedit readline')
        elikiwa 'GNU readline' in doc:
            info_add('readline.library', 'GNU readline')


eleza collect_gdb(info_add):
    agiza subprocess

    try:
        proc = subprocess.Popen(["gdb", "-nx", "--version"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True)
        version = proc.communicate()[0]
    except OSError:
        return

    # Only keep the first line
    version = version.splitlines()[0]
    info_add('gdb_version', version)


eleza collect_tkinter(info_add):
    try:
        agiza _tkinter
    except ImportError:
        pass
    else:
        attributes = ('TK_VERSION', 'TCL_VERSION')
        copy_attributes(info_add, _tkinter, 'tkinter.%s', attributes)

    try:
        agiza tkinter
    except ImportError:
        pass
    else:
        tcl = tkinter.Tcl()
        patchlevel = tcl.call('info', 'patchlevel')
        info_add('tkinter.info_patchlevel', patchlevel)


eleza collect_time(info_add):
    agiza time

    info_add('time.time', time.time())

    attributes = (
        'altzone',
        'daylight',
        'timezone',
        'tzname',
    )
    copy_attributes(info_add, time, 'time.%s', attributes)

    ikiwa hasattr(time, 'get_clock_info'):
        for clock in ('clock', 'monotonic', 'perf_counter',
                      'process_time', 'thread_time', 'time'):
            try:
                # prevent DeprecatingWarning on get_clock_info('clock')
                with warnings.catch_warnings(record=True):
                    clock_info = time.get_clock_info(clock)
            except ValueError:
                # missing clock like time.thread_time()
                pass
            else:
                info_add('time.get_clock_info(%s)' % clock, clock_info)


eleza collect_datetime(info_add):
    try:
        agiza datetime
    except ImportError:
        return

    info_add('datetime.datetime.now', datetime.datetime.now())


eleza collect_sysconfig(info_add):
    agiza sysconfig

    for name in (
        'ABIFLAGS',
        'ANDROID_API_LEVEL',
        'CC',
        'CCSHARED',
        'CFLAGS',
        'CFLAGSFORSHARED',
        'CONFIG_ARGS',
        'HOST_GNU_TYPE',
        'MACHDEP',
        'MULTIARCH',
        'OPT',
        'PY_CFLAGS',
        'PY_CFLAGS_NODIST',
        'PY_CORE_LDFLAGS',
        'PY_LDFLAGS',
        'PY_LDFLAGS_NODIST',
        'PY_STDMODULE_CFLAGS',
        'Py_DEBUG',
        'Py_ENABLE_SHARED',
        'SHELL',
        'SOABI',
        'prefix',
    ):
        value = sysconfig.get_config_var(name)
        ikiwa name == 'ANDROID_API_LEVEL' and not value:
            # skip ANDROID_API_LEVEL=0
            continue
        value = normalize_text(value)
        info_add('sysconfig[%s]' % name, value)


eleza collect_ssl(info_add):
    agiza os
    try:
        agiza ssl
    except ImportError:
        return
    try:
        agiza _ssl
    except ImportError:
        _ssl = None

    eleza format_attr(attr, value):
        ikiwa attr.startswith('OP_'):
            rudisha '%#8x' % value
        else:
            rudisha value

    attributes = (
        'OPENSSL_VERSION',
        'OPENSSL_VERSION_INFO',
        'HAS_SNI',
        'OP_ALL',
        'OP_NO_TLSv1_1',
    )
    copy_attributes(info_add, ssl, 'ssl.%s', attributes, formatter=format_attr)

    for name, ctx in (
        ('SSLContext', ssl.SSLContext()),
        ('default_https_context', ssl._create_default_https_context()),
        ('stdlib_context', ssl._create_stdlib_context()),
    ):
        attributes = (
            'minimum_version',
            'maximum_version',
            'protocol',
            'options',
            'verify_mode',
        )
        copy_attributes(info_add, ctx, f'ssl.{name}.%s', attributes)

    env_names = ["OPENSSL_CONF", "SSLKEYLOGFILE"]
    ikiwa _ssl is not None and hasattr(_ssl, 'get_default_verify_paths'):
        parts = _ssl.get_default_verify_paths()
        env_names.extend((parts[0], parts[2]))

    for name in env_names:
        try:
            value = os.environ[name]
        except KeyError:
            continue
        info_add('ssl.environ[%s]' % name, value)


eleza collect_socket(info_add):
    agiza socket

    hostname = socket.gethostname()
    info_add('socket.hostname', hostname)


eleza collect_sqlite(info_add):
    try:
        agiza sqlite3
    except ImportError:
        return

    attributes = ('version', 'sqlite_version')
    copy_attributes(info_add, sqlite3, 'sqlite3.%s', attributes)


eleza collect_zlib(info_add):
    try:
        agiza zlib
    except ImportError:
        return

    attributes = ('ZLIB_VERSION', 'ZLIB_RUNTIME_VERSION')
    copy_attributes(info_add, zlib, 'zlib.%s', attributes)


eleza collect_expat(info_add):
    try:
        kutoka xml.parsers agiza expat
    except ImportError:
        return

    attributes = ('EXPAT_VERSION',)
    copy_attributes(info_add, expat, 'expat.%s', attributes)


eleza collect_decimal(info_add):
    try:
        agiza _decimal
    except ImportError:
        return

    attributes = ('__libmpdec_version__',)
    copy_attributes(info_add, _decimal, '_decimal.%s', attributes)


eleza collect_testcapi(info_add):
    try:
        agiza _testcapi
    except ImportError:
        return

    call_func(info_add, 'pymem.allocator', _testcapi, 'pymem_getallocatorsname')
    copy_attr(info_add, 'pymem.with_pymalloc', _testcapi, 'WITH_PYMALLOC')


eleza collect_resource(info_add):
    try:
        agiza resource
    except ImportError:
        return

    limits = [attr for attr in dir(resource) ikiwa attr.startswith('RLIMIT_')]
    for name in limits:
        key = getattr(resource, name)
        value = resource.getrlimit(key)
        info_add('resource.%s' % name, value)

    call_func(info_add, 'resource.pagesize', resource, 'getpagesize')


eleza collect_test_socket(info_add):
    try:
        kutoka test agiza test_socket
    except ImportError:
        return

    # all check attributes like HAVE_SOCKET_CAN
    attributes = [name for name in dir(test_socket)
                  ikiwa name.startswith('HAVE_')]
    copy_attributes(info_add, test_socket, 'test_socket.%s', attributes)


eleza collect_test_support(info_add):
    try:
        kutoka test agiza support
    except ImportError:
        return

    attributes = ('IPV6_ENABLED',)
    copy_attributes(info_add, support, 'test_support.%s', attributes)

    call_func(info_add, 'test_support._is_gui_available', support, '_is_gui_available')
    call_func(info_add, 'test_support.python_is_optimized', support, 'python_is_optimized')


eleza collect_cc(info_add):
    agiza subprocess
    agiza sysconfig

    CC = sysconfig.get_config_var('CC')
    ikiwa not CC:
        return

    try:
        agiza shlex
        args = shlex.split(CC)
    except ImportError:
        args = CC.split()
    args.append('--version')
    try:
        proc = subprocess.Popen(args,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True)
    except OSError:
        # Cannot run the compiler, for example when Python has been
        # cross-compiled and installed on the target platform where the
        # compiler is missing.
        return

    stdout = proc.communicate()[0]
    ikiwa proc.returncode:
        # CC --version failed: ignore error
        return

    text = stdout.splitlines()[0]
    text = normalize_text(text)
    info_add('CC.version', text)


eleza collect_gdbm(info_add):
    try:
        kutoka _gdbm agiza _GDBM_VERSION
    except ImportError:
        return

    info_add('gdbm.GDBM_VERSION', '.'.join(map(str, _GDBM_VERSION)))


eleza collect_get_config(info_add):
    # Get global configuration variables, _PyPreConfig and _PyCoreConfig
    try:
        kutoka _testinternalcapi agiza get_configs
    except ImportError:
        return

    all_configs = get_configs()
    for config_type in sorted(all_configs):
        config = all_configs[config_type]
        for key in sorted(config):
            info_add('%s[%s]' % (config_type, key), repr(config[key]))


eleza collect_subprocess(info_add):
    agiza subprocess
    copy_attributes(info_add, subprocess, 'subprocess.%s', ('_USE_POSIX_SPAWN',))


eleza collect_windows(info_add):
    try:
        agiza ctypes
    except ImportError:
        return

    ikiwa not hasattr(ctypes, 'WinDLL'):
        return

    ntdll = ctypes.WinDLL('ntdll')
    BOOLEAN = ctypes.c_ubyte

    try:
        RtlAreLongPathsEnabled = ntdll.RtlAreLongPathsEnabled
    except AttributeError:
        res = '<function not available>'
    else:
        RtlAreLongPathsEnabled.restype = BOOLEAN
        RtlAreLongPathsEnabled.argtypes = ()
        res = bool(RtlAreLongPathsEnabled())
    info_add('windows.RtlAreLongPathsEnabled', res)

    try:
        agiza _winapi
        dll_path = _winapi.GetModuleFileName(sys.dllhandle)
        info_add('windows.dll_path', dll_path)
    except (ImportError, AttributeError):
        pass


eleza collect_info(info):
    error = False
    info_add = info.add

    for collect_func in (
        # collect_urandom() must be the first, to check the getrandom() status.
        # Other functions may block on os.urandom() indirectly and so change
        # its state.
        collect_urandom,

        collect_builtins,
        collect_cc,
        collect_datetime,
        collect_decimal,
        collect_expat,
        collect_gdb,
        collect_gdbm,
        collect_get_config,
        collect_locale,
        collect_os,
        collect_platform,
        collect_pwd,
        collect_readline,
        collect_resource,
        collect_socket,
        collect_sqlite,
        collect_ssl,
        collect_subprocess,
        collect_sys,
        collect_sysconfig,
        collect_testcapi,
        collect_time,
        collect_tkinter,
        collect_windows,
        collect_zlib,

        # Collecting kutoka tests should be last as they have side effects.
        collect_test_socket,
        collect_test_support,
    ):
        try:
            collect_func(info_add)
        except Exception as exc:
            error = True
            andika("ERROR: %s() failed" % (collect_func.__name__),
                  file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            andika(file=sys.stderr)
            sys.stderr.flush()

    rudisha error


eleza dump_info(info, file=None):
    title = "Python debug information"
    andika(title)
    andika("=" * len(title))
    andika()

    infos = info.get_infos()
    infos = sorted(infos.items())
    for key, value in infos:
        value = value.replace("\n", " ")
        andika("%s: %s" % (key, value))
    andika()


eleza main():
    info = PythonInfo()
    error = collect_info(info)
    dump_info(info)

    ikiwa error:
        andika("Collection failed: exit with error", file=sys.stderr)
        sys.exit(1)


ikiwa __name__ == "__main__":
    main()
