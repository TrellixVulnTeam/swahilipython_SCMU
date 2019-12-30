# Run the tests kwenye Programs/_testembed.c (tests kila the CPython embedding APIs)
kutoka test agiza support
agiza unittest

kutoka collections agiza namedtuple
agiza contextlib
agiza json
agiza os
agiza re
agiza shutil
agiza subprocess
agiza sys
agiza tempfile
agiza textwrap


MS_WINDOWS = (os.name == 'nt')
MACOS = (sys.platform == 'darwin')

PYMEM_ALLOCATOR_NOT_SET = 0
PYMEM_ALLOCATOR_DEBUG = 2
PYMEM_ALLOCATOR_MALLOC = 3

# _PyCoreConfig_InitCompatConfig()
API_COMPAT = 1
# _PyCoreConfig_InitPythonConfig()
API_PYTHON = 2
# _PyCoreConfig_InitIsolatedConfig()
API_ISOLATED = 3


eleza debug_build(program):
    program = os.path.basename(program)
    name = os.path.splitext(program)[0]
    rudisha name.endswith("_d")


eleza remove_python_envvars():
    env = dict(os.environ)
    # Remove PYTHON* environment variables to get deterministic environment
    kila key kwenye list(env):
        ikiwa key.startswith('PYTHON'):
            toa env[key]
    rudisha env


kundi EmbeddingTestsMixin:
    eleza setUp(self):
        here = os.path.abspath(__file__)
        basepath = os.path.dirname(os.path.dirname(os.path.dirname(here)))
        exename = "_testembed"
        ikiwa MS_WINDOWS:
            ext = ("_d" ikiwa debug_build(sys.executable) isipokua "") + ".exe"
            exename += ext
            exepath = os.path.dirname(sys.executable)
        isipokua:
            exepath = os.path.join(basepath, "Programs")
        self.test_exe = exe = os.path.join(exepath, exename)
        ikiwa sio os.path.exists(exe):
            self.skipTest("%r doesn't exist" % exe)
        # This ni needed otherwise we get a fatal error:
        # "Py_Initialize: Unable to get the locale encoding
        # LookupError: no codec search functions registered: can't find encoding"
        self.oldcwd = os.getcwd()
        os.chdir(basepath)

    eleza tearDown(self):
        os.chdir(self.oldcwd)

    eleza run_embedded_interpreter(self, *args, env=Tupu,
                                 timeout=Tupu, returncode=0, input=Tupu,
                                 cwd=Tupu):
        """Runs a test kwenye the embedded interpreter"""
        cmd = [self.test_exe]
        cmd.extend(args)
        ikiwa env ni sio Tupu na MS_WINDOWS:
            # Windows requires at least the SYSTEMROOT environment variable to
            # start Python.
            env = env.copy()
            env['SYSTEMROOT'] = os.environ['SYSTEMROOT']

        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=Kweli,
                             env=env,
                             cwd=cwd)
        jaribu:
            (out, err) = p.communicate(input=input, timeout=timeout)
        tatizo:
            p.terminate()
            p.wait()
            raise
        ikiwa p.returncode != returncode na support.verbose:
            andika(f"--- {cmd} failed ---")
            andika(f"stdout:\n{out}")
            andika(f"stderr:\n{err}")
            andika(f"------")

        self.assertEqual(p.returncode, returncode,
                         "bad returncode %d, stderr ni %r" %
                         (p.returncode, err))
        rudisha out, err

    eleza run_repeated_init_and_subinterpreters(self):
        out, err = self.run_embedded_interpreter("test_repeated_init_and_subinterpreters")
        self.assertEqual(err, "")

        # The output kutoka _testembed looks like this:
        # --- Pass 0 ---
        # interp 0 <0x1cf9330>, thread state <0x1cf9700>: id(modules) = 139650431942728
        # interp 1 <0x1d4f690>, thread state <0x1d35350>: id(modules) = 139650431165784
        # interp 2 <0x1d5a690>, thread state <0x1d99ed0>: id(modules) = 139650413140368
        # interp 3 <0x1d4f690>, thread state <0x1dc3340>: id(modules) = 139650412862200
        # interp 0 <0x1cf9330>, thread state <0x1cf9700>: id(modules) = 139650431942728
        # --- Pass 1 ---
        # ...

        interp_pat = (r"^interp (\d+) <(0x[\dA-F]+)>, "
                      r"thread state <(0x[\dA-F]+)>: "
                      r"id\(modules\) = ([\d]+)$")
        Interp = namedtuple("Interp", "id interp tstate modules")

        numloops = 0
        current_run = []
        kila line kwenye out.splitlines():
            ikiwa line == "--- Pass {} ---".format(numloops):
                self.assertEqual(len(current_run), 0)
                ikiwa support.verbose > 1:
                    andika(line)
                numloops += 1
                endelea

            self.assertLess(len(current_run), 5)
            match = re.match(interp_pat, line)
            ikiwa match ni Tupu:
                self.assertRegex(line, interp_pat)

            # Parse the line kutoka the loop.  The first line ni the main
            # interpreter na the 3 afterward are subinterpreters.
            interp = Interp(*match.groups())
            ikiwa support.verbose > 1:
                andika(interp)
            self.assertKweli(interp.interp)
            self.assertKweli(interp.tstate)
            self.assertKweli(interp.modules)
            current_run.append(interp)

            # The last line kwenye the loop should be the same kama the first.
            ikiwa len(current_run) == 5:
                main = current_run[0]
                self.assertEqual(interp, main)
                tuma current_run
                current_run = []


kundi EmbeddingTests(EmbeddingTestsMixin, unittest.TestCase):
    eleza test_subinterps_main(self):
        kila run kwenye self.run_repeated_init_and_subinterpreters():
            main = run[0]

            self.assertEqual(main.id, '0')

    eleza test_subinterps_different_ids(self):
        kila run kwenye self.run_repeated_init_and_subinterpreters():
            main, *subs, _ = run

            mainid = int(main.id)
            kila i, sub kwenye enumerate(subs):
                self.assertEqual(sub.id, str(mainid + i + 1))

    eleza test_subinterps_distinct_state(self):
        kila run kwenye self.run_repeated_init_and_subinterpreters():
            main, *subs, _ = run

            ikiwa '0x0' kwenye main:
                # XXX Fix on Windows (and other platforms): something
                # ni going on ukijumuisha the pointers kwenye Programs/_testembed.c.
                # interp.interp ni 0x0 na interp.modules ni the same
                # between interpreters.
                ashiria unittest.SkipTest('platform prints pointers kama 0x0')

            kila sub kwenye subs:
                # A new subinterpreter may have the same
                # PyInterpreterState pointer kama a previous one if
                # the earlier one has already been destroyed.  So
                # we compare ukijumuisha the main interpreter.  The same
                # applies to tstate.
                self.assertNotEqual(sub.interp, main.interp)
                self.assertNotEqual(sub.tstate, main.tstate)
                self.assertNotEqual(sub.modules, main.modules)

    eleza test_forced_io_encoding(self):
        # Checks forced configuration of embedded interpreter IO streams
        env = dict(os.environ, PYTHONIOENCODING="utf-8:surrogateescape")
        out, err = self.run_embedded_interpreter("test_forced_io_encoding", env=env)
        ikiwa support.verbose > 1:
            andika()
            andika(out)
            andika(err)
        expected_stream_encoding = "utf-8"
        expected_errors = "surrogateescape"
        expected_output = '\n'.join([
        "--- Use defaults ---",
        "Expected encoding: default",
        "Expected errors: default",
        "stdin: {in_encoding}:{errors}",
        "stdout: {out_encoding}:{errors}",
        "stderr: {out_encoding}:backslashreplace",
        "--- Set errors only ---",
        "Expected encoding: default",
        "Expected errors: ignore",
        "stdin: {in_encoding}:ignore",
        "stdout: {out_encoding}:ignore",
        "stderr: {out_encoding}:backslashreplace",
        "--- Set encoding only ---",
        "Expected encoding: iso8859-1",
        "Expected errors: default",
        "stdin: iso8859-1:{errors}",
        "stdout: iso8859-1:{errors}",
        "stderr: iso8859-1:backslashreplace",
        "--- Set encoding na errors ---",
        "Expected encoding: iso8859-1",
        "Expected errors: replace",
        "stdin: iso8859-1:replace",
        "stdout: iso8859-1:replace",
        "stderr: iso8859-1:backslashreplace"])
        expected_output = expected_output.format(
                                in_encoding=expected_stream_encoding,
                                out_encoding=expected_stream_encoding,
                                errors=expected_errors)
        # This ni useful ikiwa we ever trip over odd platform behaviour
        self.maxDiff = Tupu
        self.assertEqual(out.strip(), expected_output)

    eleza test_pre_initialization_api(self):
        """
        Checks some key parts of the C-API that need to work before the runtine
        ni initialized (via Py_Initialize()).
        """
        env = dict(os.environ, PYTHONPATH=os.pathsep.join(sys.path))
        out, err = self.run_embedded_interpreter("test_pre_initialization_api", env=env)
        ikiwa MS_WINDOWS:
            expected_path = self.test_exe
        isipokua:
            expected_path = os.path.join(os.getcwd(), "spam")
        expected_output = f"sys.executable: {expected_path}\n"
        self.assertIn(expected_output, out)
        self.assertEqual(err, '')

    eleza test_pre_initialization_sys_options(self):
        """
        Checks that sys.warnoptions na sys._xoptions can be set before the
        runtime ni initialized (otherwise they won't be effective).
        """
        env = remove_python_envvars()
        env['PYTHONPATH'] = os.pathsep.join(sys.path)
        out, err = self.run_embedded_interpreter(
                        "test_pre_initialization_sys_options", env=env)
        expected_output = (
            "sys.warnoptions: ['once', 'module', 'default']\n"
            "sys._xoptions: {'not_an_option': '1', 'also_not_an_option': '2'}\n"
            "warnings.filters[:3]: ['default', 'module', 'once']\n"
        )
        self.assertIn(expected_output, out)
        self.assertEqual(err, '')

    eleza test_bpo20891(self):
        """
        bpo-20891: Calling PyGILState_Ensure kwenye a non-Python thread before
        calling PyEval_InitThreads() must sio crash. PyGILState_Ensure() must
        call PyEval_InitThreads() kila us kwenye this case.
        """
        out, err = self.run_embedded_interpreter("test_bpo20891")
        self.assertEqual(out, '')
        self.assertEqual(err, '')

    eleza test_initialize_twice(self):
        """
        bpo-33932: Calling Py_Initialize() twice should do nothing (and sio
        crash!).
        """
        out, err = self.run_embedded_interpreter("test_initialize_twice")
        self.assertEqual(out, '')
        self.assertEqual(err, '')

    eleza test_initialize_pymain(self):
        """
        bpo-34008: Calling Py_Main() after Py_Initialize() must sio fail.
        """
        out, err = self.run_embedded_interpreter("test_initialize_pymain")
        self.assertEqual(out.rstrip(), "Py_Main() after Py_Initialize: sys.argv=['-c', 'arg2']")
        self.assertEqual(err, '')

    eleza test_run_main(self):
        out, err = self.run_embedded_interpreter("test_run_main")
        self.assertEqual(out.rstrip(), "Py_RunMain(): sys.argv=['-c', 'arg2']")
        self.assertEqual(err, '')


kundi InitConfigTests(EmbeddingTestsMixin, unittest.TestCase):
    maxDiff = 4096
    UTF8_MODE_ERRORS = ('surrogatepita' ikiwa MS_WINDOWS isipokua 'surrogateescape')

    # Marker to read the default configuration: get_default_config()
    GET_DEFAULT_CONFIG = object()

    # Marker to ignore a configuration parameter
    IGNORE_CONFIG = object()

    PRE_CONFIG_COMPAT = {
        '_config_init': API_COMPAT,
        'allocator': PYMEM_ALLOCATOR_NOT_SET,
        'parse_argv': 0,
        'configure_locale': 1,
        'coerce_c_locale': 0,
        'coerce_c_locale_warn': 0,
        'utf8_mode': 0,
    }
    ikiwa MS_WINDOWS:
        PRE_CONFIG_COMPAT.update({
            'legacy_windows_fs_encoding': 0,
        })
    PRE_CONFIG_PYTHON = dict(PRE_CONFIG_COMPAT,
        _config_init=API_PYTHON,
        parse_argv=1,
        coerce_c_locale=GET_DEFAULT_CONFIG,
        utf8_mode=GET_DEFAULT_CONFIG,
    )
    PRE_CONFIG_ISOLATED = dict(PRE_CONFIG_COMPAT,
        _config_init=API_ISOLATED,
        configure_locale=0,
        isolated=1,
        use_environment=0,
        utf8_mode=0,
        dev_mode=0,
        coerce_c_locale=0,
    )

    COPY_PRE_CONFIG = [
        'dev_mode',
        'isolated',
        'use_environment',
    ]

    CONFIG_COMPAT = {
        '_config_init': API_COMPAT,
        'isolated': 0,
        'use_environment': 1,
        'dev_mode': 0,

        'install_signal_handlers': 1,
        'use_hash_seed': 0,
        'hash_seed': 0,
        'faulthandler': 0,
        'tracemalloc': 0,
        'import_time': 0,
        'show_ref_count': 0,
        'show_alloc_count': 0,
        'dump_refs': 0,
        'malloc_stats': 0,

        'filesystem_encoding': GET_DEFAULT_CONFIG,
        'filesystem_errors': GET_DEFAULT_CONFIG,

        'pycache_prefix': Tupu,
        'program_name': GET_DEFAULT_CONFIG,
        'parse_argv': 0,
        'argv': [""],

        'xoptions': [],
        'warnoptions': [],

        'pythonpath_env': Tupu,
        'home': Tupu,
        'executable': GET_DEFAULT_CONFIG,
        'base_executable': GET_DEFAULT_CONFIG,

        'prefix': GET_DEFAULT_CONFIG,
        'base_prefix': GET_DEFAULT_CONFIG,
        'exec_prefix': GET_DEFAULT_CONFIG,
        'base_exec_prefix': GET_DEFAULT_CONFIG,
        'module_search_paths': GET_DEFAULT_CONFIG,

        'site_import': 1,
        'bytes_warning': 0,
        'inspect': 0,
        'interactive': 0,
        'optimization_level': 0,
        'parser_debug': 0,
        'write_bytecode': 1,
        'verbose': 0,
        'quiet': 0,
        'user_site_directory': 1,
        'configure_c_stdio': 0,
        'buffered_stdio': 1,

        'stdio_encoding': GET_DEFAULT_CONFIG,
        'stdio_errors': GET_DEFAULT_CONFIG,

        'skip_source_first_line': 0,
        'run_command': Tupu,
        'run_module': Tupu,
        'run_filename': Tupu,

        '_install_importlib': 1,
        'check_hash_pycs_mode': 'default',
        'pathconfig_warnings': 1,
        '_init_main': 1,
    }
    ikiwa MS_WINDOWS:
        CONFIG_COMPAT.update({
            'legacy_windows_stdio': 0,
        })

    CONFIG_PYTHON = dict(CONFIG_COMPAT,
        _config_init=API_PYTHON,
        configure_c_stdio=1,
        parse_argv=1,
    )
    CONFIG_ISOLATED = dict(CONFIG_COMPAT,
        _config_init=API_ISOLATED,
        isolated=1,
        use_environment=0,
        user_site_directory=0,
        dev_mode=0,
        install_signal_handlers=0,
        use_hash_seed=0,
        faulthandler=0,
        tracemalloc=0,
        pathconfig_warnings=0,
    )
    ikiwa MS_WINDOWS:
        CONFIG_ISOLATED['legacy_windows_stdio'] = 0

    # global config
    DEFAULT_GLOBAL_CONFIG = {
        'Py_HasFileSystemDefaultEncoding': 0,
        'Py_HashRandomizationFlag': 1,
        '_Py_HasFileSystemDefaultEncodeErrors': 0,
    }
    COPY_GLOBAL_PRE_CONFIG = [
        ('Py_UTF8Mode', 'utf8_mode'),
    ]
    COPY_GLOBAL_CONFIG = [
        # Copy core config to global config kila expected values
        # Kweli means that the core config value ni inverted (0 => 1 na 1 => 0)
        ('Py_BytesWarningFlag', 'bytes_warning'),
        ('Py_DebugFlag', 'parser_debug'),
        ('Py_DontWriteBytecodeFlag', 'write_bytecode', Kweli),
        ('Py_FileSystemDefaultEncodeErrors', 'filesystem_errors'),
        ('Py_FileSystemDefaultEncoding', 'filesystem_encoding'),
        ('Py_FrozenFlag', 'pathconfig_warnings', Kweli),
        ('Py_IgnoreEnvironmentFlag', 'use_environment', Kweli),
        ('Py_InspectFlag', 'inspect'),
        ('Py_InteractiveFlag', 'interactive'),
        ('Py_IsolatedFlag', 'isolated'),
        ('Py_NoSiteFlag', 'site_import', Kweli),
        ('Py_NoUserSiteDirectory', 'user_site_directory', Kweli),
        ('Py_OptimizeFlag', 'optimization_level'),
        ('Py_QuietFlag', 'quiet'),
        ('Py_UnbufferedStdioFlag', 'buffered_stdio', Kweli),
        ('Py_VerboseFlag', 'verbose'),
    ]
    ikiwa MS_WINDOWS:
        COPY_GLOBAL_PRE_CONFIG.extend((
            ('Py_LegacyWindowsFSEncodingFlag', 'legacy_windows_fs_encoding'),
        ))
        COPY_GLOBAL_CONFIG.extend((
            ('Py_LegacyWindowsStdioFlag', 'legacy_windows_stdio'),
        ))

    EXPECTED_CONFIG = Tupu

    @classmethod
    eleza tearDownClass(cls):
        # clear cache
        cls.EXPECTED_CONFIG = Tupu

    eleza main_xoptions(self, xoptions_list):
        xoptions = {}
        kila opt kwenye xoptions_list:
            ikiwa '=' kwenye opt:
                key, value = opt.split('=', 1)
                xoptions[key] = value
            isipokua:
                xoptions[opt] = Kweli
        rudisha xoptions

    eleza _get_expected_config_impl(self):
        env = remove_python_envvars()
        code = textwrap.dedent('''
            agiza json
            agiza sys
            agiza _testinternalcapi

            configs = _testinternalcapi.get_configs()

            data = json.dumps(configs)
            data = data.encode('utf-8')
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
        ''')

        # Use -S to sio agiza the site module: get the proper configuration
        # when test_embed ni run kutoka a venv (bpo-35313)
        args = [sys.executable, '-S', '-c', code]
        proc = subprocess.run(args, env=env,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        ikiwa proc.returncode:
            ashiria Exception(f"failed to get the default config: "
                            f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        stdout = proc.stdout.decode('utf-8')
        # ignore stderr
        jaribu:
            rudisha json.loads(stdout)
        tatizo json.JSONDecodeError:
            self.fail(f"fail to decode stdout: {stdout!r}")

    eleza _get_expected_config(self):
        cls = InitConfigTests
        ikiwa cls.EXPECTED_CONFIG ni Tupu:
            cls.EXPECTED_CONFIG = self._get_expected_config_impl()

        # get a copy
        configs = {}
        kila config_key, config_value kwenye cls.EXPECTED_CONFIG.items():
            config = {}
            kila key, value kwenye config_value.items():
                ikiwa isinstance(value, list):
                    value = value.copy()
                config[key] = value
            configs[config_key] = config
        rudisha configs

    eleza get_expected_config(self, expected_preconfig, expected, env, api,
                            modify_path_cb=Tupu):
        cls = self.__class__
        configs = self._get_expected_config()

        pre_config = configs['pre_config']
        kila key, value kwenye expected_preconfig.items():
            ikiwa value ni self.GET_DEFAULT_CONFIG:
                expected_preconfig[key] = pre_config[key]

        ikiwa sio expected_preconfig['configure_locale'] ama api == API_COMPAT:
            # there ni no easy way to get the locale encoding before
            # setlocale(LC_CTYPE, "") ni called: don't test encodings
            kila key kwenye ('filesystem_encoding', 'filesystem_errors',
                        'stdio_encoding', 'stdio_errors'):
                expected[key] = self.IGNORE_CONFIG

        ikiwa sio expected_preconfig['configure_locale']:
            # UTF-8 Mode depends on the locale. There ni no easy way
            # to guess ikiwa UTF-8 Mode will be enabled ama sio ikiwa the locale
            # ni sio configured.
            expected_preconfig['utf8_mode'] = self.IGNORE_CONFIG

        ikiwa expected_preconfig['utf8_mode'] == 1:
            ikiwa expected['filesystem_encoding'] ni self.GET_DEFAULT_CONFIG:
                expected['filesystem_encoding'] = 'utf-8'
            ikiwa expected['filesystem_errors'] ni self.GET_DEFAULT_CONFIG:
                expected['filesystem_errors'] = self.UTF8_MODE_ERRORS
            ikiwa expected['stdio_encoding'] ni self.GET_DEFAULT_CONFIG:
                expected['stdio_encoding'] = 'utf-8'
            ikiwa expected['stdio_errors'] ni self.GET_DEFAULT_CONFIG:
                expected['stdio_errors'] = 'surrogateescape'

        ikiwa sys.platform == 'win32':
            default_executable = self.test_exe
        lasivyo expected['program_name'] ni sio self.GET_DEFAULT_CONFIG:
            default_executable = os.path.abspath(expected['program_name'])
        isipokua:
            default_executable = os.path.join(os.getcwd(), '_testembed')
        ikiwa expected['executable'] ni self.GET_DEFAULT_CONFIG:
            expected['executable'] = default_executable
        ikiwa expected['base_executable'] ni self.GET_DEFAULT_CONFIG:
            expected['base_executable'] = default_executable
        ikiwa expected['program_name'] ni self.GET_DEFAULT_CONFIG:
            expected['program_name'] = './_testembed'

        config = configs['config']
        kila key, value kwenye expected.items():
            ikiwa value ni self.GET_DEFAULT_CONFIG:
                expected[key] = config[key]

        pythonpath_env = expected['pythonpath_env']
        ikiwa pythonpath_env ni sio Tupu:
            paths = pythonpath_env.split(os.path.pathsep)
            expected['module_search_paths'] = [*paths, *expected['module_search_paths']]
        ikiwa modify_path_cb ni sio Tupu:
            expected['module_search_paths'] = expected['module_search_paths'].copy()
            modify_path_cb(expected['module_search_paths'])

        kila key kwenye self.COPY_PRE_CONFIG:
            ikiwa key haiko kwenye expected_preconfig:
                expected_preconfig[key] = expected[key]

    eleza check_pre_config(self, configs, expected):
        pre_config = dict(configs['pre_config'])
        kila key, value kwenye list(expected.items()):
            ikiwa value ni self.IGNORE_CONFIG:
                toa pre_config[key]
                toa expected[key]
        self.assertEqual(pre_config, expected)

    eleza check_config(self, configs, expected):
        config = dict(configs['config'])
        kila key, value kwenye list(expected.items()):
            ikiwa value ni self.IGNORE_CONFIG:
                toa config[key]
                toa expected[key]
        self.assertEqual(config, expected)

    eleza check_global_config(self, configs):
        pre_config = configs['pre_config']
        config = configs['config']

        expected = dict(self.DEFAULT_GLOBAL_CONFIG)
        kila item kwenye self.COPY_GLOBAL_CONFIG:
            ikiwa len(item) == 3:
                global_key, core_key, opposite = item
                expected[global_key] = 0 ikiwa config[core_key] isipokua 1
            isipokua:
                global_key, core_key = item
                expected[global_key] = config[core_key]
        kila item kwenye self.COPY_GLOBAL_PRE_CONFIG:
            ikiwa len(item) == 3:
                global_key, core_key, opposite = item
                expected[global_key] = 0 ikiwa pre_config[core_key] isipokua 1
            isipokua:
                global_key, core_key = item
                expected[global_key] = pre_config[core_key]

        self.assertEqual(configs['global_config'], expected)

    eleza check_all_configs(self, testname, expected_config=Tupu,
                          expected_preconfig=Tupu, modify_path_cb=Tupu,
                          stderr=Tupu, *, api, preconfig_api=Tupu,
                          env=Tupu, ignore_stderr=Uongo, cwd=Tupu):
        new_env = remove_python_envvars()
        ikiwa env ni sio Tupu:
            new_env.update(env)
        env = new_env

        ikiwa preconfig_api ni Tupu:
            preconfig_api = api
        ikiwa preconfig_api == API_ISOLATED:
            default_preconfig = self.PRE_CONFIG_ISOLATED
        lasivyo preconfig_api == API_PYTHON:
            default_preconfig = self.PRE_CONFIG_PYTHON
        isipokua:
            default_preconfig = self.PRE_CONFIG_COMPAT
        ikiwa expected_preconfig ni Tupu:
            expected_preconfig = {}
        expected_preconfig = dict(default_preconfig, **expected_preconfig)
        ikiwa expected_config ni Tupu:
            expected_config = {}

        ikiwa api == API_PYTHON:
            default_config = self.CONFIG_PYTHON
        lasivyo api == API_ISOLATED:
            default_config = self.CONFIG_ISOLATED
        isipokua:
            default_config = self.CONFIG_COMPAT
        expected_config = dict(default_config, **expected_config)

        self.get_expected_config(expected_preconfig,
                                 expected_config, env,
                                 api, modify_path_cb)

        out, err = self.run_embedded_interpreter(testname,
                                                 env=env, cwd=cwd)
        ikiwa stderr ni Tupu na sio expected_config['verbose']:
            stderr = ""
        ikiwa stderr ni sio Tupu na sio ignore_stderr:
            self.assertEqual(err.rstrip(), stderr)
        jaribu:
            configs = json.loads(out)
        tatizo json.JSONDecodeError:
            self.fail(f"fail to decode stdout: {out!r}")

        self.check_pre_config(configs, expected_preconfig)
        self.check_config(configs, expected_config)
        self.check_global_config(configs)

    eleza test_init_default_config(self):
        self.check_all_configs("test_init_initialize_config", api=API_COMPAT)

    eleza test_preinit_compat_config(self):
        self.check_all_configs("test_preinit_compat_config", api=API_COMPAT)

    eleza test_init_compat_config(self):
        self.check_all_configs("test_init_compat_config", api=API_COMPAT)

    eleza test_init_global_config(self):
        preconfig = {
            'utf8_mode': 1,
        }
        config = {
            'program_name': './globalvar',
            'site_import': 0,
            'bytes_warning': 1,
            'warnoptions': ['default::BytesWarning'],
            'inspect': 1,
            'interactive': 1,
            'optimization_level': 2,
            'write_bytecode': 0,
            'verbose': 1,
            'quiet': 1,
            'buffered_stdio': 0,

            'user_site_directory': 0,
            'pathconfig_warnings': 0,
        }
        self.check_all_configs("test_init_global_config", config, preconfig,
                               api=API_COMPAT)

    eleza test_init_from_config(self):
        preconfig = {
            'allocator': PYMEM_ALLOCATOR_MALLOC,
            'utf8_mode': 1,
        }
        config = {
            'install_signal_handlers': 0,
            'use_hash_seed': 1,
            'hash_seed': 123,
            'tracemalloc': 2,
            'import_time': 1,
            'show_ref_count': 1,
            'show_alloc_count': 1,
            'malloc_stats': 1,

            'stdio_encoding': 'iso8859-1',
            'stdio_errors': 'replace',

            'pycache_prefix': 'conf_pycache_prefix',
            'program_name': './conf_program_name',
            'argv': ['-c', 'arg2', ],
            'parse_argv': 1,
            'xoptions': [
                'config_xoption1=3',
                'config_xoption2=',
                'config_xoption3',
                'cmdline_xoption',
            ],
            'warnoptions': [
                'cmdline_warnoption',
                'default::BytesWarning',
                'config_warnoption',
            ],
            'run_command': 'pita\n',

            'site_import': 0,
            'bytes_warning': 1,
            'inspect': 1,
            'interactive': 1,
            'optimization_level': 2,
            'write_bytecode': 0,
            'verbose': 1,
            'quiet': 1,
            'configure_c_stdio': 1,
            'buffered_stdio': 0,
            'user_site_directory': 0,
            'faulthandler': 1,

            'check_hash_pycs_mode': 'always',
            'pathconfig_warnings': 0,
        }
        self.check_all_configs("test_init_from_config", config, preconfig,
                               api=API_COMPAT)

    eleza test_init_compat_env(self):
        preconfig = {
            'allocator': PYMEM_ALLOCATOR_MALLOC,
        }
        config = {
            'use_hash_seed': 1,
            'hash_seed': 42,
            'tracemalloc': 2,
            'import_time': 1,
            'malloc_stats': 1,
            'inspect': 1,
            'optimization_level': 2,
            'pythonpath_env': '/my/path',
            'pycache_prefix': 'env_pycache_prefix',
            'write_bytecode': 0,
            'verbose': 1,
            'buffered_stdio': 0,
            'stdio_encoding': 'iso8859-1',
            'stdio_errors': 'replace',
            'user_site_directory': 0,
            'faulthandler': 1,
            'warnoptions': ['EnvVar'],
        }
        self.check_all_configs("test_init_compat_env", config, preconfig,
                               api=API_COMPAT)

    eleza test_init_python_env(self):
        preconfig = {
            'allocator': PYMEM_ALLOCATOR_MALLOC,
            'utf8_mode': 1,
        }
        config = {
            'use_hash_seed': 1,
            'hash_seed': 42,
            'tracemalloc': 2,
            'import_time': 1,
            'malloc_stats': 1,
            'inspect': 1,
            'optimization_level': 2,
            'pythonpath_env': '/my/path',
            'pycache_prefix': 'env_pycache_prefix',
            'write_bytecode': 0,
            'verbose': 1,
            'buffered_stdio': 0,
            'stdio_encoding': 'iso8859-1',
            'stdio_errors': 'replace',
            'user_site_directory': 0,
            'faulthandler': 1,
            'warnoptions': ['EnvVar'],
        }
        self.check_all_configs("test_init_python_env", config, preconfig,
                               api=API_PYTHON)

    eleza test_init_env_dev_mode(self):
        preconfig = dict(allocator=PYMEM_ALLOCATOR_DEBUG)
        config = dict(dev_mode=1,
                      faulthandler=1,
                      warnoptions=['default'])
        self.check_all_configs("test_init_env_dev_mode", config, preconfig,
                               api=API_COMPAT)

    eleza test_init_env_dev_mode_alloc(self):
        preconfig = dict(allocator=PYMEM_ALLOCATOR_MALLOC)
        config = dict(dev_mode=1,
                      faulthandler=1,
                      warnoptions=['default'])
        self.check_all_configs("test_init_env_dev_mode_alloc", config, preconfig,
                               api=API_COMPAT)

    eleza test_init_dev_mode(self):
        preconfig = {
            'allocator': PYMEM_ALLOCATOR_DEBUG,
        }
        config = {
            'faulthandler': 1,
            'dev_mode': 1,
            'warnoptions': ['default'],
        }
        self.check_all_configs("test_init_dev_mode", config, preconfig,
                               api=API_PYTHON)

    eleza test_preinit_parse_argv(self):
        # Pre-initialize implicitly using argv: make sure that -X dev
        # ni used to configure the allocation kwenye preinitialization
        preconfig = {
            'allocator': PYMEM_ALLOCATOR_DEBUG,
        }
        config = {
            'argv': ['script.py'],
            'run_filename': 'script.py',
            'dev_mode': 1,
            'faulthandler': 1,
            'warnoptions': ['default'],
            'xoptions': ['dev'],
        }
        self.check_all_configs("test_preinit_parse_argv", config, preconfig,
                               api=API_PYTHON)

    eleza test_preinit_dont_parse_argv(self):
        # -X dev must be ignored by isolated preconfiguration
        preconfig = {
            'isolated': 0,
        }
        config = {
            'argv': ["python3", "-E", "-I",
                     "-X", "dev", "-X", "utf8", "script.py"],
            'isolated': 0,
        }
        self.check_all_configs("test_preinit_dont_parse_argv", config, preconfig,
                               api=API_ISOLATED)

    eleza test_init_isolated_flag(self):
        config = {
            'isolated': 1,
            'use_environment': 0,
            'user_site_directory': 0,
        }
        self.check_all_configs("test_init_isolated_flag", config, api=API_PYTHON)

    eleza test_preinit_isolated1(self):
        # _PyPreConfig.isolated=1, _PyCoreConfig.isolated sio set
        config = {
            'isolated': 1,
            'use_environment': 0,
            'user_site_directory': 0,
        }
        self.check_all_configs("test_preinit_isolated1", config, api=API_COMPAT)

    eleza test_preinit_isolated2(self):
        # _PyPreConfig.isolated=0, _PyCoreConfig.isolated=1
        config = {
            'isolated': 1,
            'use_environment': 0,
            'user_site_directory': 0,
        }
        self.check_all_configs("test_preinit_isolated2", config, api=API_COMPAT)

    eleza test_preinit_isolated_config(self):
        self.check_all_configs("test_preinit_isolated_config", api=API_ISOLATED)

    eleza test_init_isolated_config(self):
        self.check_all_configs("test_init_isolated_config", api=API_ISOLATED)

    eleza test_preinit_python_config(self):
        self.check_all_configs("test_preinit_python_config", api=API_PYTHON)

    eleza test_init_python_config(self):
        self.check_all_configs("test_init_python_config", api=API_PYTHON)

    eleza test_init_dont_configure_locale(self):
        # _PyPreConfig.configure_locale=0
        preconfig = {
            'configure_locale': 0,
            'coerce_c_locale': 0,
        }
        self.check_all_configs("test_init_dont_configure_locale", {}, preconfig,
                               api=API_PYTHON)

    eleza test_init_read_set(self):
        config = {
            'program_name': './init_read_set',
            'executable': 'my_executable',
        }
        eleza modify_path(path):
            path.insert(1, "test_path_insert1")
            path.append("test_path_append")
        self.check_all_configs("test_init_read_set", config,
                               api=API_PYTHON,
                               modify_path_cb=modify_path)

    eleza test_init_sys_add(self):
        config = {
            'faulthandler': 1,
            'xoptions': [
                'config_xoption',
                'cmdline_xoption',
                'sysadd_xoption',
                'faulthandler',
            ],
            'warnoptions': [
                'ignore:::cmdline_warnoption',
                'ignore:::sysadd_warnoption',
                'ignore:::config_warnoption',
            ],
        }
        self.check_all_configs("test_init_sys_add", config, api=API_PYTHON)

    eleza test_init_run_main(self):
        code = ('agiza _testinternalcapi, json; '
                'andika(json.dumps(_testinternalcapi.get_configs()))')
        config = {
            'argv': ['-c', 'arg2'],
            'program_name': './python3',
            'run_command': code + '\n',
            'parse_argv': 1,
        }
        self.check_all_configs("test_init_run_main", config, api=API_PYTHON)

    eleza test_init_main(self):
        code = ('agiza _testinternalcapi, json; '
                'andika(json.dumps(_testinternalcapi.get_configs()))')
        config = {
            'argv': ['-c', 'arg2'],
            'program_name': './python3',
            'run_command': code + '\n',
            'parse_argv': 1,
            '_init_main': 0,
        }
        self.check_all_configs("test_init_main", config,
                               api=API_PYTHON,
                               stderr="Run Python code before _Py_InitializeMain")

    eleza test_init_parse_argv(self):
        config = {
            'parse_argv': 1,
            'argv': ['-c', 'arg1', '-v', 'arg3'],
            'program_name': './argv0',
            'run_command': 'pita\n',
            'use_environment': 0,
        }
        self.check_all_configs("test_init_parse_argv", config, api=API_PYTHON)

    eleza test_init_dont_parse_argv(self):
        pre_config = {
            'parse_argv': 0,
        }
        config = {
            'parse_argv': 0,
            'argv': ['./argv0', '-E', '-c', 'pita', 'arg1', '-v', 'arg3'],
            'program_name': './argv0',
        }
        self.check_all_configs("test_init_dont_parse_argv", config, pre_config,
                               api=API_PYTHON)

    eleza default_program_name(self, config):
        ikiwa MS_WINDOWS:
            program_name = 'python'
            executable = self.test_exe
        isipokua:
            program_name = 'python3'
            ikiwa MACOS:
                executable = self.test_exe
            isipokua:
                executable = shutil.which(program_name) ama ''
        config.update({
            'program_name': program_name,
            'base_executable': executable,
            'executable': executable,
        })

    eleza test_init_setpath(self):
        # Test Py_SetPath()
        config = self._get_expected_config()
        paths = config['config']['module_search_paths']

        config = {
            'module_search_paths': paths,
            'prefix': '',
            'base_prefix': '',
            'exec_prefix': '',
            'base_exec_prefix': '',
        }
        self.default_program_name(config)
        env = {'TESTPATH': os.path.pathsep.join(paths)}
        self.check_all_configs("test_init_setpath", config,
                               api=API_COMPAT, env=env,
                               ignore_stderr=Kweli)

    eleza test_init_setpath_config(self):
        # Test Py_SetPath() ukijumuisha PyConfig
        config = self._get_expected_config()
        paths = config['config']['module_search_paths']

        config = {
            # set by Py_SetPath()
            'module_search_paths': paths,
            'prefix': '',
            'base_prefix': '',
            'exec_prefix': '',
            'base_exec_prefix': '',
            # overriden by PyConfig
            'program_name': 'conf_program_name',
            'base_executable': 'conf_executable',
            'executable': 'conf_executable',
        }
        env = {'TESTPATH': os.path.pathsep.join(paths)}
        self.check_all_configs("test_init_setpath_config", config,
                               api=API_PYTHON, env=env, ignore_stderr=Kweli)

    eleza module_search_paths(self, prefix=Tupu, exec_prefix=Tupu):
        config = self._get_expected_config()
        ikiwa prefix ni Tupu:
            prefix = config['config']['prefix']
        ikiwa exec_prefix ni Tupu:
            exec_prefix = config['config']['prefix']
        ikiwa MS_WINDOWS:
            rudisha config['config']['module_search_paths']
        isipokua:
            ver = sys.version_info
            rudisha [
                os.path.join(prefix, 'lib',
                             f'python{ver.major}{ver.minor}.zip'),
                os.path.join(prefix, 'lib',
                             f'python{ver.major}.{ver.minor}'),
                os.path.join(exec_prefix, 'lib',
                             f'python{ver.major}.{ver.minor}', 'lib-dynload'),
            ]

    @contextlib.contextmanager
    eleza tmpdir_with_python(self):
        # Temporary directory ukijumuisha a copy of the Python program
        ukijumuisha tempfile.TemporaryDirectory() kama tmpdir:
            # bpo-38234: On macOS na FreeBSD, the temporary directory
            # can be symbolic link. For example, /tmp can be a symbolic link
            # to /var/tmp. Call realpath() to resolve all symbolic links.
            tmpdir = os.path.realpath(tmpdir)

            ikiwa MS_WINDOWS:
                # Copy pythonXY.dll (or pythonXY_d.dll)
                ver = sys.version_info
                dll = f'python{ver.major}{ver.minor}'
                ikiwa debug_build(sys.executable):
                    dll += '_d'
                dll += '.dll'
                dll = os.path.join(os.path.dirname(self.test_exe), dll)
                dll_copy = os.path.join(tmpdir, os.path.basename(dll))
                shutil.copyfile(dll, dll_copy)

            # Copy Python program
            exec_copy = os.path.join(tmpdir, os.path.basename(self.test_exe))
            shutil.copyfile(self.test_exe, exec_copy)
            shutil.copystat(self.test_exe, exec_copy)
            self.test_exe = exec_copy

            tuma tmpdir

    eleza test_init_setpythonhome(self):
        # Test Py_SetPythonHome(home) ukijumuisha PYTHONPATH env var
        config = self._get_expected_config()
        paths = config['config']['module_search_paths']
        paths_str = os.path.pathsep.join(paths)

        kila path kwenye paths:
            ikiwa sio os.path.isdir(path):
                endelea
            ikiwa os.path.exists(os.path.join(path, 'os.py')):
                home = os.path.dirname(path)
                koma
        isipokua:
            self.fail(f"Unable to find home kwenye {paths!r}")

        prefix = exec_prefix = home
        ver = sys.version_info
        expected_paths = self.module_search_paths(prefix=home, exec_prefix=home)

        config = {
            'home': home,
            'module_search_paths': expected_paths,
            'prefix': prefix,
            'base_prefix': prefix,
            'exec_prefix': exec_prefix,
            'base_exec_prefix': exec_prefix,
            'pythonpath_env': paths_str,
        }
        self.default_program_name(config)
        env = {'TESTHOME': home, 'PYTHONPATH': paths_str}
        self.check_all_configs("test_init_setpythonhome", config,
                               api=API_COMPAT, env=env)

    eleza copy_paths_by_env(self, config):
        all_configs = self._get_expected_config()
        paths = all_configs['config']['module_search_paths']
        paths_str = os.path.pathsep.join(paths)
        config['pythonpath_env'] = paths_str
        env = {'PYTHONPATH': paths_str}
        rudisha env

    @unittest.skipIf(MS_WINDOWS, 'Windows does sio use pybuilddir.txt')
    eleza test_init_pybuilddir(self):
        # Test path configuration ukijumuisha pybuilddir.txt configuration file

        ukijumuisha self.tmpdir_with_python() kama tmpdir:
            # pybuilddir.txt ni a sub-directory relative to the current
            # directory (tmpdir)
            subdir = 'libdir'
            libdir = os.path.join(tmpdir, subdir)
            os.mkdir(libdir)

            filename = os.path.join(tmpdir, 'pybuilddir.txt')
            ukijumuisha open(filename, "w", encoding="utf8") kama fp:
                fp.write(subdir)

            module_search_paths = self.module_search_paths()
            module_search_paths[-1] = libdir

            executable = self.test_exe
            config = {
                'base_executable': executable,
                'executable': executable,
                'module_search_paths': module_search_paths,
            }
            env = self.copy_paths_by_env(config)
            self.check_all_configs("test_init_compat_config", config,
                                   api=API_COMPAT, env=env,
                                   ignore_stderr=Kweli, cwd=tmpdir)

    eleza test_init_pyvenv_cfg(self):
        # Test path configuration ukijumuisha pyvenv.cfg configuration file

        ukijumuisha self.tmpdir_with_python() kama tmpdir, \
             tempfile.TemporaryDirectory() kama pyvenv_home:
            ver = sys.version_info

            ikiwa sio MS_WINDOWS:
                lib_dynload = os.path.join(pyvenv_home,
                                           'lib',
                                           f'python{ver.major}.{ver.minor}',
                                           'lib-dynload')
                os.makedirs(lib_dynload)
            isipokua:
                lib_dynload = os.path.join(pyvenv_home, 'lib')
                os.makedirs(lib_dynload)
                # getpathp.c uses Lib\os.py kama the LANDMARK
                shutil.copyfile(os.__file__, os.path.join(lib_dynload, 'os.py'))

            filename = os.path.join(tmpdir, 'pyvenv.cfg')
            ukijumuisha open(filename, "w", encoding="utf8") kama fp:
                andika("home = %s" % pyvenv_home, file=fp)
                andika("include-system-site-packages = false", file=fp)

            paths = self.module_search_paths()
            ikiwa sio MS_WINDOWS:
                paths[-1] = lib_dynload
            isipokua:
                kila index, path kwenye enumerate(paths):
                    ikiwa index == 0:
                        paths[index] = os.path.join(tmpdir, os.path.basename(path))
                    isipokua:
                        paths[index] = os.path.join(pyvenv_home, os.path.basename(path))
                paths[-1] = pyvenv_home

            executable = self.test_exe
            exec_prefix = pyvenv_home
            config = {
                'base_exec_prefix': exec_prefix,
                'exec_prefix': exec_prefix,
                'base_executable': executable,
                'executable': executable,
                'module_search_paths': paths,
            }
            ikiwa MS_WINDOWS:
                config['base_prefix'] = pyvenv_home
                config['prefix'] = pyvenv_home
            env = self.copy_paths_by_env(config)
            self.check_all_configs("test_init_compat_config", config,
                                   api=API_COMPAT, env=env,
                                   ignore_stderr=Kweli, cwd=tmpdir)

    eleza test_global_pathconfig(self):
        # Test C API functions getting the path configuration:
        #
        # - Py_GetExecPrefix()
        # - Py_GetPath()
        # - Py_GetPrefix()
        # - Py_GetProgramFullPath()
        # - Py_GetProgramName()
        # - Py_GetPythonHome()
        #
        # The global path configuration (_Py_path_config) must be a copy
        # of the path configuration of PyInterpreter.config (PyConfig).
        ctypes = support.import_module('ctypes')
        _testinternalcapi = support.import_module('_testinternalcapi')

        eleza get_func(name):
            func = getattr(ctypes.pythonapi, name)
            func.argtypes = ()
            func.restype = ctypes.c_wchar_p
            rudisha func

        Py_GetPath = get_func('Py_GetPath')
        Py_GetPrefix = get_func('Py_GetPrefix')
        Py_GetExecPrefix = get_func('Py_GetExecPrefix')
        Py_GetProgramName = get_func('Py_GetProgramName')
        Py_GetProgramFullPath = get_func('Py_GetProgramFullPath')
        Py_GetPythonHome = get_func('Py_GetPythonHome')

        config = _testinternalcapi.get_configs()['config']

        self.assertEqual(Py_GetPath().split(os.path.pathsep),
                         config['module_search_paths'])
        self.assertEqual(Py_GetPrefix(), config['prefix'])
        self.assertEqual(Py_GetExecPrefix(), config['exec_prefix'])
        self.assertEqual(Py_GetProgramName(), config['program_name'])
        self.assertEqual(Py_GetProgramFullPath(), config['executable'])
        self.assertEqual(Py_GetPythonHome(), config['home'])

    eleza test_init_warnoptions(self):
        # lowest to highest priority
        warnoptions = [
            'ignore:::PyConfig_Insert0',      # PyWideStringList_Insert(0)
            'default',                        # PyConfig.dev_mode=1
            'ignore:::env1',                  # PYTHONWARNINGS env var
            'ignore:::env2',                  # PYTHONWARNINGS env var
            'ignore:::cmdline1',              # -W opt command line option
            'ignore:::cmdline2',              # -W opt command line option
            'default::BytesWarning',          # PyConfig.bytes_warnings=1
            'ignore:::PySys_AddWarnOption1',  # PySys_AddWarnOption()
            'ignore:::PySys_AddWarnOption2',  # PySys_AddWarnOption()
            'ignore:::PyConfig_BeforeRead',   # PyConfig.warnoptions
            'ignore:::PyConfig_AfterRead']    # PyWideStringList_Append()
        preconfig = dict(allocator=PYMEM_ALLOCATOR_DEBUG)
        config = {
            'dev_mode': 1,
            'faulthandler': 1,
            'bytes_warning': 1,
            'warnoptions': warnoptions,
        }
        self.check_all_configs("test_init_warnoptions", config, preconfig,
                               api=API_PYTHON)


kundi AuditingTests(EmbeddingTestsMixin, unittest.TestCase):
    eleza test_open_code_hook(self):
        self.run_embedded_interpreter("test_open_code_hook")

    eleza test_audit(self):
        self.run_embedded_interpreter("test_audit")

    eleza test_audit_subinterpreter(self):
        self.run_embedded_interpreter("test_audit_subinterpreter")

    eleza test_audit_run_command(self):
        self.run_embedded_interpreter("test_audit_run_command", timeout=3, returncode=1)

    eleza test_audit_run_file(self):
        self.run_embedded_interpreter("test_audit_run_file", timeout=3, returncode=1)

    eleza test_audit_run_interactivehook(self):
        startup = os.path.join(self.oldcwd, support.TESTFN) + ".py"
        ukijumuisha open(startup, "w", encoding="utf-8") kama f:
            andika("agiza sys", file=f)
            andika("sys.__interactivehook__ = lambda: Tupu", file=f)
        jaribu:
            env = {**remove_python_envvars(), "PYTHONSTARTUP": startup}
            self.run_embedded_interpreter("test_audit_run_interactivehook", timeout=5,
                                          returncode=10, env=env)
        mwishowe:
            os.unlink(startup)

    eleza test_audit_run_startup(self):
        startup = os.path.join(self.oldcwd, support.TESTFN) + ".py"
        ukijumuisha open(startup, "w", encoding="utf-8") kama f:
            andika("pita", file=f)
        jaribu:
            env = {**remove_python_envvars(), "PYTHONSTARTUP": startup}
            self.run_embedded_interpreter("test_audit_run_startup", timeout=5,
                                          returncode=10, env=env)
        mwishowe:
            os.unlink(startup)

    eleza test_audit_run_stdin(self):
        self.run_embedded_interpreter("test_audit_run_stdin", timeout=3, returncode=1)

ikiwa __name__ == "__main__":
    unittest.main()
