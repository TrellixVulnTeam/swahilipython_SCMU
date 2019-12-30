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
    ikiwa text ni Tupu:
        rudisha Tupu
    text = str(text)
    text = re.sub(r'\s+', ' ', text)
    rudisha text.strip()


kundi PythonInfo:
    eleza __init__(self):
        self.info = {}

    eleza add(self, key, value):
        ikiwa key kwenye self.info:
            ashiria ValueError("duplicate key: %r" % key)

        ikiwa value ni Tupu:
            return

        ikiwa sio isinstance(value, int):
            ikiwa sio isinstance(value, str):
                # convert other objects like sys.flags to string
                value = str(value)

            value = value.strip()
            ikiwa sio value:
                return

        self.info[key] = value

    eleza get_infos(self):
        """
        Get information kama a key:value dictionary where values are strings.
        """
        rudisha {key: str(value) kila key, value kwenye self.info.items()}


eleza copy_attributes(info_add, obj, name_fmt, attributes, *, formatter=Tupu):
    kila attr kwenye attributes:
        value = getattr(obj, attr, Tupu)
        ikiwa value ni Tupu:
            endelea
        name = name_fmt % attr
        ikiwa formatter ni sio Tupu:
            value = formatter(attr, value)
        info_add(name, value)


eleza copy_attr(info_add, name, mod, attr_name):
    jaribu:
        value = getattr(mod, attr_name)
    tatizo AttributeError:
        return
    info_add(name, value)


eleza call_func(info_add, name, mod, func_name, *, formatter=Tupu):
    jaribu:
        func = getattr(mod, func_name)
    tatizo AttributeError:
        return
    value = func()
    ikiwa formatter ni sio Tupu:
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

    kila name kwenye ('stdin', 'stdout', 'stderr'):
        stream = getattr(sys, name)
        ikiwa stream ni Tupu:
            endelea
        encoding = getattr(stream, 'encoding', Tupu)
        ikiwa sio encoding:
            endelea
        errors = getattr(stream, 'errors', Tupu)
        ikiwa errors:
            encoding = '%s/%s' % (encoding, errors)
        info_add('sys.%s.encoding' % name, encoding)

    # Were we compiled --with-pydebug ama ukijumuisha #define Py_DEBUG?
    Py_DEBUG = hasattr(sys, 'gettotalrefcount')
    ikiwa Py_DEBUG:
        text = 'Yes (sys.gettotalrefcount() present)'
    isipokua:
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
             platform.platform(aliased=Kweli))

    libc_ver = ('%s %s' % platform.libc_ver()).strip()
    ikiwa libc_ver:
        info_add('platform.libc_ver', libc_ver)


eleza collect_locale(info_add):
    agiza locale

    info_add('locale.encoding', locale.getpreferredencoding(Uongo))


eleza collect_builtins(info_add):
    info_add('builtins.float.float_format', float.__getformat__("float"))
    info_add('builtins.float.double_format', float.__getformat__("double"))


eleza collect_urandom(info_add):
    agiza os

    ikiwa hasattr(os, 'getrandom'):
        # PEP 524: Check ikiwa system urandom ni initialized
        jaribu:
            jaribu:
                os.getrandom(1, os.GRND_NONBLOCK)
                state = 'ready (initialized)'
            tatizo BlockingIOError kama exc:
                state = 'not seeded yet (%s)' % exc
            info_add('os.getrandom', state)
        tatizo OSError kama exc:
            # Python was compiled on a more recent Linux version
            # than the current Linux kernel: ignore OSError(ENOSYS)
            ikiwa exc.errno != errno.ENOSYS:
                raise


eleza collect_os(info_add):
    agiza os

    eleza format_attr(attr, value):
        ikiwa attr kwenye ('supports_follow_symlinks', 'supports_fd',
                    'supports_effective_ids'):
            rudisha str(sorted(func.__name__ kila func kwenye value))
        isipokua:
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
        jaribu:
            login = os.getlogin()
        tatizo OSError:
            # getlogin() fails ukijumuisha "OSError: [Errno 25] Inappropriate ioctl
            # kila device" on Travis CI
            pita
        isipokua:
            info_add("os.login", login)

    call_func(info_add, 'os.cpu_count', os, 'cpu_count')
    call_func(info_add, 'os.getloadavg', os, 'getloadavg')

    # Environment variables used by the stdlib na tests. Don't log the full
    # environment: filter to list to sio leak sensitive information.
    #
    # HTTP_PROXY ni sio logged because it can contain a pitaword.
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
    kila name, value kwenye os.environ.items():
        uname = name.upper()
        ikiwa (uname kwenye ENV_VARS
           # Copy PYTHON* na LC_* variables
           ama uname.startswith(("PYTHON", "LC_"))
           # Visual Studio: VS140COMNTOOLS
           ama (uname.startswith("VS") na uname.endswith("COMNTOOLS"))):
            info_add('os.environ[%s]' % name, value)

    ikiwa hasattr(os, 'umask'):
        mask = os.umask(0)
        os.umask(mask)
        info_add("os.umask", '%03o' % mask)


eleza collect_pwd(info_add):
    jaribu:
        agiza pwd
    tatizo ImportError:
        return
    agiza os

    uid = os.getuid()
    jaribu:
        entry = pwd.getpwuid(uid)
    tatizo KeyError:
        entry = Tupu

    info_add('pwd.getpwuid(%s)'% uid,
             entry ikiwa entry ni sio Tupu isipokua '<KeyError>')

    ikiwa entry ni Tupu:
        # there ni nothing interesting to read ikiwa the current user identifier
        # ni sio the pitaword database
        return

    ikiwa hasattr(os, 'getgrouplist'):
        groups = os.getgrouplist(entry.pw_name, entry.pw_gid)
        groups = ', '.join(map(str, groups))
        info_add('os.getgrouplist', groups)


eleza collect_readline(info_add):
    jaribu:
        agiza readline
    tatizo ImportError:
        return

    eleza format_attr(attr, value):
        ikiwa isinstance(value, int):
            rudisha "%#x" % value
        isipokua:
            rudisha value

    attributes = (
        "_READLINE_VERSION",
        "_READLINE_RUNTIME_VERSION",
        "_READLINE_LIBRARY_VERSION",
    )
    copy_attributes(info_add, readline, 'readline.%s', attributes,
                    formatter=format_attr)

    ikiwa sio hasattr(readline, "_READLINE_LIBRARY_VERSION"):
        # _READLINE_LIBRARY_VERSION has been added to CPython 3.7
        doc = getattr(readline, '__doc__', '')
        ikiwa 'libedit readline' kwenye doc:
            info_add('readline.library', 'libedit readline')
        lasivyo 'GNU readline' kwenye doc:
            info_add('readline.library', 'GNU readline')


eleza collect_gdb(info_add):
    agiza subprocess

    jaribu:
        proc = subprocess.Popen(["gdb", "-nx", "--version"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=Kweli)
        version = proc.communicate()[0]
    tatizo OSError:
        return

    # Only keep the first line
    version = version.splitlines()[0]
    info_add('gdb_version', version)


eleza collect_tkinter(info_add):
    jaribu:
        agiza _tkinter
    tatizo ImportError:
        pita
    isipokua:
        attributes = ('TK_VERSION', 'TCL_VERSION')
        copy_attributes(info_add, _tkinter, 'tkinter.%s', attributes)

    jaribu:
        agiza tkinter
    tatizo ImportError:
        pita
    isipokua:
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
        kila clock kwenye ('clock', 'monotonic', 'perf_counter',
                      'process_time', 'thread_time', 'time'):
            jaribu:
                # prevent DeprecatingWarning on get_clock_info('clock')
                ukijumuisha warnings.catch_warnings(record=Kweli):
                    clock_info = time.get_clock_info(clock)
            tatizo ValueError:
                # missing clock like time.thread_time()
                pita
            isipokua:
                info_add('time.get_clock_info(%s)' % clock, clock_info)


eleza collect_datetime(info_add):
    jaribu:
        agiza datetime
    tatizo ImportError:
        return

    info_add('datetime.datetime.now', datetime.datetime.now())


eleza collect_sysconfig(info_add):
    agiza sysconfig

    kila name kwenye (
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
        ikiwa name == 'ANDROID_API_LEVEL' na sio value:
            # skip ANDROID_API_LEVEL=0
            endelea
        value = normalize_text(value)
        info_add('sysconfig[%s]' % name, value)


eleza collect_ssl(info_add):
    agiza os
    jaribu:
        agiza ssl
    tatizo ImportError:
        return
    jaribu:
        agiza _ssl
    tatizo ImportError:
        _ssl = Tupu

    eleza format_attr(attr, value):
        ikiwa attr.startswith('OP_'):
            rudisha '%#8x' % value
        isipokua:
            rudisha value

    attributes = (
        'OPENSSL_VERSION',
        'OPENSSL_VERSION_INFO',
        'HAS_SNI',
        'OP_ALL',
        'OP_NO_TLSv1_1',
    )
    copy_attributes(info_add, ssl, 'ssl.%s', attributes, formatter=format_attr)

    kila name, ctx kwenye (
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
    ikiwa _ssl ni sio Tupu na hasattr(_ssl, 'get_default_verify_paths'):
        parts = _ssl.get_default_verify_paths()
        env_names.extend((parts[0], parts[2]))

    kila name kwenye env_names:
        jaribu:
            value = os.environ[name]
        tatizo KeyError:
            endelea
        info_add('ssl.environ[%s]' % name, value)


eleza collect_socket(info_add):
    agiza socket

    hostname = socket.gethostname()
    info_add('socket.hostname', hostname)


eleza collect_sqlite(info_add):
    jaribu:
        agiza sqlite3
    tatizo ImportError:
        return

    attributes = ('version', 'sqlite_version')
    copy_attributes(info_add, sqlite3, 'sqlite3.%s', attributes)


eleza collect_zlib(info_add):
    jaribu:
        agiza zlib
    tatizo ImportError:
        return

    attributes = ('ZLIB_VERSION', 'ZLIB_RUNTIME_VERSION')
    copy_attributes(info_add, zlib, 'zlib.%s', attributes)


eleza collect_expat(info_add):
    jaribu:
        kutoka xml.parsers agiza expat
    tatizo ImportError:
        return

    attributes = ('EXPAT_VERSION',)
    copy_attributes(info_add, expat, 'expat.%s', attributes)


eleza collect_decimal(info_add):
    jaribu:
        agiza _decimal
    tatizo ImportError:
        return

    attributes = ('__libmpdec_version__',)
    copy_attributes(info_add, _decimal, '_decimal.%s', attributes)


eleza collect_testcapi(info_add):
    jaribu:
        agiza _testcapi
    tatizo ImportError:
        return

    call_func(info_add, 'pymem.allocator', _testcapi, 'pymem_getallocatorsname')
    copy_attr(info_add, 'pymem.with_pymalloc', _testcapi, 'WITH_PYMALLOC')


eleza collect_resource(info_add):
    jaribu:
        agiza resource
    tatizo ImportError:
        return

    limits = [attr kila attr kwenye dir(resource) ikiwa attr.startswith('RLIMIT_')]
    kila name kwenye limits:
        key = getattr(resource, name)
        value = resource.getrlimit(key)
        info_add('resource.%s' % name, value)

    call_func(info_add, 'resource.pagesize', resource, 'getpagesize')


eleza collect_test_socket(info_add):
    jaribu:
        kutoka test agiza test_socket
    tatizo ImportError:
        return

    # all check attributes like HAVE_SOCKET_CAN
    attributes = [name kila name kwenye dir(test_socket)
                  ikiwa name.startswith('HAVE_')]
    copy_attributes(info_add, test_socket, 'test_socket.%s', attributes)


eleza collect_test_support(info_add):
    jaribu:
        kutoka test agiza support
    tatizo ImportError:
        return

    attributes = ('IPV6_ENABLED',)
    copy_attributes(info_add, support, 'test_support.%s', attributes)

    call_func(info_add, 'test_support._is_gui_available', support, '_is_gui_available')
    call_func(info_add, 'test_support.python_is_optimized', support, 'python_is_optimized')


eleza collect_cc(info_add):
    agiza subprocess
    agiza sysconfig

    CC = sysconfig.get_config_var('CC')
    ikiwa sio CC:
        return

    jaribu:
        agiza shlex
        args = shlex.split(CC)
    tatizo ImportError:
        args = CC.split()
    args.append('--version')
    jaribu:
        proc = subprocess.Popen(args,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=Kweli)
    tatizo OSError:
        # Cannot run the compiler, kila example when Python has been
        # cross-compiled na installed on the target platform where the
        # compiler ni missing.
        return

    stdout = proc.communicate()[0]
    ikiwa proc.returncode:
        # CC --version failed: ignore error
        return

    text = stdout.splitlines()[0]
    text = normalize_text(text)
    info_add('CC.version', text)


eleza collect_gdbm(info_add):
    jaribu:
        kutoka _gdbm agiza _GDBM_VERSION
    tatizo ImportError:
        return

    info_add('gdbm.GDBM_VERSION', '.'.join(map(str, _GDBM_VERSION)))


eleza collect_get_config(info_add):
    # Get global configuration variables, _PyPreConfig na _PyCoreConfig
    jaribu:
        kutoka _testinternalcapi agiza get_configs
    tatizo ImportError:
        return

    all_configs = get_configs()
    kila config_type kwenye sorted(all_configs):
        config = all_configs[config_type]
        kila key kwenye sorted(config):
            info_add('%s[%s]' % (config_type, key), repr(config[key]))


eleza collect_subprocess(info_add):
    agiza subprocess
    copy_attributes(info_add, subprocess, 'subprocess.%s', ('_USE_POSIX_SPAWN',))


eleza collect_windows(info_add):
    jaribu:
        agiza ctypes
    tatizo ImportError:
        return

    ikiwa sio hasattr(ctypes, 'WinDLL'):
        return

    ntdll = ctypes.WinDLL('ntdll')
    BOOLEAN = ctypes.c_ubyte

    jaribu:
        RtlAreLongPathsEnabled = ntdll.RtlAreLongPathsEnabled
    tatizo AttributeError:
        res = '<function sio available>'
    isipokua:
        RtlAreLongPathsEnabled.restype = BOOLEAN
        RtlAreLongPathsEnabled.argtypes = ()
        res = bool(RtlAreLongPathsEnabled())
    info_add('windows.RtlAreLongPathsEnabled', res)

    jaribu:
        agiza _winapi
        dll_path = _winapi.GetModuleFileName(sys.dllhandle)
        info_add('windows.dll_path', dll_path)
    tatizo (ImportError, AttributeError):
        pita


eleza collect_info(info):
    error = Uongo
    info_add = info.add

    kila collect_func kwenye (
        # collect_urandom() must be the first, to check the getrandom() status.
        # Other functions may block on os.urandom() indirectly na so change
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

        # Collecting kutoka tests should be last kama they have side effects.
        collect_test_socket,
        collect_test_support,
    ):
        jaribu:
            collect_func(info_add)
        tatizo Exception kama exc:
            error = Kweli
            andika("ERROR: %s() failed" % (collect_func.__name__),
                  file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            andika(file=sys.stderr)
            sys.stderr.flush()

    rudisha error


eleza dump_info(info, file=Tupu):
    title = "Python debug information"
    andika(title)
    andika("=" * len(title))
    andika()

    infos = info.get_infos()
    infos = sorted(infos.items())
    kila key, value kwenye infos:
        value = value.replace("\n", " ")
        andika("%s: %s" % (key, value))
    andika()


eleza main():
    info = PythonInfo()
    error = collect_info(info)
    dump_info(info)

    ikiwa error:
        andika("Collection failed: exit ukijumuisha error", file=sys.stderr)
        sys.exit(1)


ikiwa __name__ == "__main__":
    main()
