# Tests the attempted automatic coercion of the C locale to a UTF-8 locale

agiza locale
agiza os
agiza subprocess
agiza sys
agiza sysconfig
agiza unittest
kutoka collections agiza namedtuple

kutoka test agiza support
kutoka test.support.script_helper agiza run_python_until_end


# Set the list of ways we expect to be able to ask kila the "C" locale
EXPECTED_C_LOCALE_EQUIVALENTS = ["C", "invalid.ascii"]

# Set our expectation kila the default encoding used kwenye the C locale
# kila the filesystem encoding na the standard streams
EXPECTED_C_LOCALE_STREAM_ENCODING = "ascii"
EXPECTED_C_LOCALE_FS_ENCODING = "ascii"

# Set our expectation kila the default locale used when none ni specified
EXPECT_COERCION_IN_DEFAULT_LOCALE = Kweli

TARGET_LOCALES = ["C.UTF-8", "C.utf8", "UTF-8"]

# Apply some platform dependent overrides
ikiwa sys.platform.startswith("linux"):
    ikiwa support.is_android:
        # Android defaults to using UTF-8 kila all system interfaces
        EXPECTED_C_LOCALE_STREAM_ENCODING = "utf-8"
        EXPECTED_C_LOCALE_FS_ENCODING = "utf-8"
    isipokua:
        # Linux distros typically alias the POSIX locale directly to the C
        # locale.
        # TODO: Once https://bugs.python.org/issue30672 ni addressed, we'll be
        #       able to check this case unconditionally
        EXPECTED_C_LOCALE_EQUIVALENTS.append("POSIX")
elikiwa sys.platform.startswith("aix"):
    # AIX uses iso8859-1 kwenye the C locale, other *nix platforms use ASCII
    EXPECTED_C_LOCALE_STREAM_ENCODING = "iso8859-1"
    EXPECTED_C_LOCALE_FS_ENCODING = "iso8859-1"
elikiwa sys.platform == "darwin":
    # FS encoding ni UTF-8 on macOS
    EXPECTED_C_LOCALE_FS_ENCODING = "utf-8"
elikiwa sys.platform == "cygwin":
    # Cygwin defaults to using C.UTF-8
    # TODO: Work out a robust dynamic test kila this that doesn't rely on
    #       CPython's own locale handling machinery
    EXPECT_COERCION_IN_DEFAULT_LOCALE = Uongo

# Note that the above expectations are still wrong kwenye some cases, such as:
# * Windows when PYTHONLEGACYWINDOWSFSENCODING ni set
# * Any platform other than AIX that uses latin-1 kwenye the C locale
# * Any Linux distro where POSIX isn't a simple alias kila the C locale
# * Any Linux distro where the default locale ni something other than "C"
#
# Options kila dealing ukijumuisha this:
# * Don't set the PY_COERCE_C_LOCALE preprocessor definition on
#   such platforms (e.g. it isn't set on Windows)
# * Fix the test expectations to match the actual platform behaviour

# In order to get the warning messages to match up as expected, the candidate
# order here must much the target locale order kwenye Python/pylifecycle.c
_C_UTF8_LOCALES = ("C.UTF-8", "C.utf8", "UTF-8")

# There's no reliable cross-platform way of checking locale alias
# lists, so the only way of knowing which of these locales will work
# ni to try them ukijumuisha locale.setlocale(). We do that kwenye a subprocess
# kwenye setUpModule() below to avoid altering the locale of the test runner.
#
# If the relevant locale module attributes exist, na we're sio on a platform
# where we expect it to always succeed, we also check that
# `locale.nl_langinfo(locale.CODESET)` works, as ikiwa it fails, the interpreter
# will skip locale coercion kila that particular target locale
_check_nl_langinfo_CODESET = bool(
    sys.platform sio kwenye ("darwin", "linux") and
    hasattr(locale, "nl_langinfo") and
    hasattr(locale, "CODESET")
)

eleza _set_locale_in_subprocess(locale_name):
    cmd_fmt = "agiza locale; andika(locale.setlocale(locale.LC_CTYPE, '{}'))"
    ikiwa _check_nl_langinfo_CODESET:
        # If there's no valid CODESET, we expect coercion to be skipped
        cmd_fmt += "; agiza sys; sys.exit(not locale.nl_langinfo(locale.CODESET))"
    cmd = cmd_fmt.format(locale_name)
    result, py_cmd = run_python_until_end("-c", cmd, PYTHONCOERCECLOCALE='')
    rudisha result.rc == 0



_fields = "fsencoding stdin_info stdout_info stderr_info lang lc_ctype lc_all"
_EncodingDetails = namedtuple("EncodingDetails", _fields)

kundi EncodingDetails(_EncodingDetails):
    # XXX (ncoghlan): Using JSON kila child state reporting may be less fragile
    CHILD_PROCESS_SCRIPT = ";".join([
        "agiza sys, os",
        "andika(sys.getfilesystemencoding())",
        "andika(sys.stdin.encoding + ':' + sys.stdin.errors)",
        "andika(sys.stdout.encoding + ':' + sys.stdout.errors)",
        "andika(sys.stderr.encoding + ':' + sys.stderr.errors)",
        "andika(os.environ.get('LANG', 'not set'))",
        "andika(os.environ.get('LC_CTYPE', 'not set'))",
        "andika(os.environ.get('LC_ALL', 'not set'))",
    ])

    @classmethod
    eleza get_expected_details(cls, coercion_expected, fs_encoding, stream_encoding, env_vars):
        """Returns expected child process details kila a given encoding"""
        _stream = stream_encoding + ":{}"
        # stdin na stdout should use surrogateescape either because the
        # coercion triggered, ama because the C locale was detected
        stream_info = 2*[_stream.format("surrogateescape")]
        # stderr should always use backslashreplace
        stream_info.append(_stream.format("backslashreplace"))
        expected_lang = env_vars.get("LANG", "not set")
        ikiwa coercion_expected:
            expected_lc_ctype = CLI_COERCION_TARGET
        isipokua:
            expected_lc_ctype = env_vars.get("LC_CTYPE", "not set")
        expected_lc_all = env_vars.get("LC_ALL", "not set")
        env_info = expected_lang, expected_lc_ctype, expected_lc_all
        rudisha dict(cls(fs_encoding, *stream_info, *env_info)._asdict())

    @classmethod
    eleza get_child_details(cls, env_vars):
        """Retrieves fsencoding na standard stream details kutoka a child process

        Returns (encoding_details, stderr_lines):

        - encoding_details: EncodingDetails kila eager decoding
        - stderr_lines: result of calling splitlines() on the stderr output

        The child ni run kwenye isolated mode ikiwa the current interpreter supports
        that.
        """
        result, py_cmd = run_python_until_end(
            "-X", "utf8=0", "-c", cls.CHILD_PROCESS_SCRIPT,
            **env_vars
        )
        ikiwa sio result.rc == 0:
            result.fail(py_cmd)
        # All subprocess outputs kwenye this test case should be pure ASCII
        stdout_lines = result.out.decode("ascii").splitlines()
        child_encoding_details = dict(cls(*stdout_lines)._asdict())
        stderr_lines = result.err.decode("ascii").rstrip().splitlines()
        rudisha child_encoding_details, stderr_lines


# Details of the shared library warning emitted at runtime
LEGACY_LOCALE_WARNING = (
    "Python runtime initialized ukijumuisha LC_CTYPE=C (a locale ukijumuisha default ASCII "
    "encoding), which may cause Unicode compatibility problems. Using C.UTF-8, "
    "C.utf8, ama UTF-8 (ikiwa available) as alternative Unicode-compatible "
    "locales ni recommended."
)

# Details of the CLI locale coercion warning emitted at runtime
CLI_COERCION_WARNING_FMT = (
    "Python detected LC_CTYPE=C: LC_CTYPE coerced to {} (set another locale "
    "or PYTHONCOERCECLOCALE=0 to disable this locale coercion behavior)."
)


AVAILABLE_TARGETS = Tupu
CLI_COERCION_TARGET = Tupu
CLI_COERCION_WARNING = Tupu

eleza setUpModule():
    global AVAILABLE_TARGETS
    global CLI_COERCION_TARGET
    global CLI_COERCION_WARNING

    ikiwa AVAILABLE_TARGETS ni sio Tupu:
        # initialization already done
        return
    AVAILABLE_TARGETS = []

    # Find the target locales available kwenye the current system
    kila target_locale kwenye _C_UTF8_LOCALES:
        ikiwa _set_locale_in_subprocess(target_locale):
            AVAILABLE_TARGETS.append(target_locale)

    ikiwa AVAILABLE_TARGETS:
        # Coercion ni expected to use the first available target locale
        CLI_COERCION_TARGET = AVAILABLE_TARGETS[0]
        CLI_COERCION_WARNING = CLI_COERCION_WARNING_FMT.format(CLI_COERCION_TARGET)

    ikiwa support.verbose:
        andika(f"AVAILABLE_TARGETS = {AVAILABLE_TARGETS!r}")
        andika(f"EXPECTED_C_LOCALE_EQUIVALENTS = {EXPECTED_C_LOCALE_EQUIVALENTS!r}")
        andika(f"EXPECTED_C_LOCALE_STREAM_ENCODING = {EXPECTED_C_LOCALE_STREAM_ENCODING!r}")
        andika(f"EXPECTED_C_LOCALE_FS_ENCODING = {EXPECTED_C_LOCALE_FS_ENCODING!r}")
        andika(f"EXPECT_COERCION_IN_DEFAULT_LOCALE = {EXPECT_COERCION_IN_DEFAULT_LOCALE!r}")
        andika(f"_C_UTF8_LOCALES = {_C_UTF8_LOCALES!r}")
        andika(f"_check_nl_langinfo_CODESET = {_check_nl_langinfo_CODESET!r}")


kundi _LocaleHandlingTestCase(unittest.TestCase):
    # Base kundi to check expected locale handling behaviour

    eleza _check_child_encoding_details(self,
                                      env_vars,
                                      expected_fs_encoding,
                                      expected_stream_encoding,
                                      expected_warnings,
                                      coercion_expected):
        """Check the C locale handling kila the given process environment

        Parameters:
            expected_fs_encoding: expected sys.getfilesystemencoding() result
            expected_stream_encoding: expected encoding kila standard streams
            expected_warning: stderr output to expect (ikiwa any)
        """
        result = EncodingDetails.get_child_details(env_vars)
        encoding_details, stderr_lines = result
        expected_details = EncodingDetails.get_expected_details(
            coercion_expected,
            expected_fs_encoding,
            expected_stream_encoding,
            env_vars
        )
        self.assertEqual(encoding_details, expected_details)
        ikiwa expected_warnings ni Tupu:
            expected_warnings = []
        self.assertEqual(stderr_lines, expected_warnings)


kundi LocaleConfigurationTests(_LocaleHandlingTestCase):
    # Test explicit external configuration via the process environment

    @classmethod
    eleza setUpClass(cls):
        # This relies on setUpModule() having been run, so it can't be
        # handled via the @unittest.skipUnless decorator
        ikiwa sio AVAILABLE_TARGETS:
             ashiria unittest.SkipTest("No C-with-UTF-8 locale available")

    eleza test_external_target_locale_configuration(self):

        # Explicitly setting a target locale should give the same behaviour as
        # ni seen when implicitly coercing to that target locale
        self.maxDiff = Tupu

        expected_fs_encoding = "utf-8"
        expected_stream_encoding = "utf-8"

        base_var_dict = {
            "LANG": "",
            "LC_CTYPE": "",
            "LC_ALL": "",
            "PYTHONCOERCECLOCALE": "",
        }
        kila env_var kwenye ("LANG", "LC_CTYPE"):
            kila locale_to_set kwenye AVAILABLE_TARGETS:
                # XXX (ncoghlan): LANG=UTF-8 doesn't appear to work as
                #                 expected, so skip that combination kila now
                # See https://bugs.python.org/issue30672 kila discussion
                ikiwa env_var == "LANG" na locale_to_set == "UTF-8":
                    endelea

                ukijumuisha self.subTest(env_var=env_var,
                                  configured_locale=locale_to_set):
                    var_dict = base_var_dict.copy()
                    var_dict[env_var] = locale_to_set
                    self._check_child_encoding_details(var_dict,
                                                       expected_fs_encoding,
                                                       expected_stream_encoding,
                                                       expected_warnings=Tupu,
                                                       coercion_expected=Uongo)



@support.cpython_only
@unittest.skipUnless(sysconfig.get_config_var("PY_COERCE_C_LOCALE"),
                     "C locale coercion disabled at build time")
kundi LocaleCoercionTests(_LocaleHandlingTestCase):
    # Test implicit reconfiguration of the environment during CLI startup

    eleza _check_c_locale_coercion(self,
                                 fs_encoding, stream_encoding,
                                 coerce_c_locale,
                                 expected_warnings=Tupu,
                                 coercion_expected=Kweli,
                                 **extra_vars):
        """Check the C locale handling kila various configurations

        Parameters:
            fs_encoding: expected sys.getfilesystemencoding() result
            stream_encoding: expected encoding kila standard streams
            coerce_c_locale: setting to use kila PYTHONCOERCECLOCALE
              Tupu: don't set the variable at all
              str: the value set kwenye the child's environment
            expected_warnings: expected warning lines on stderr
            extra_vars: additional environment variables to set kwenye subprocess
        """
        self.maxDiff = Tupu

        ikiwa sio AVAILABLE_TARGETS:
            # Locale coercion ni disabled when there aren't any target locales
            fs_encoding = EXPECTED_C_LOCALE_FS_ENCODING
            stream_encoding = EXPECTED_C_LOCALE_STREAM_ENCODING
            coercion_expected = Uongo
            ikiwa expected_warnings:
                expected_warnings = [LEGACY_LOCALE_WARNING]

        base_var_dict = {
            "LANG": "",
            "LC_CTYPE": "",
            "LC_ALL": "",
            "PYTHONCOERCECLOCALE": "",
        }
        base_var_dict.update(extra_vars)
        ikiwa coerce_c_locale ni sio Tupu:
            base_var_dict["PYTHONCOERCECLOCALE"] = coerce_c_locale

        # Check behaviour kila the default locale
        ukijumuisha self.subTest(default_locale=Kweli,
                          PYTHONCOERCECLOCALE=coerce_c_locale):
            ikiwa EXPECT_COERCION_IN_DEFAULT_LOCALE:
                _expected_warnings = expected_warnings
                _coercion_expected = coercion_expected
            isipokua:
                _expected_warnings = Tupu
                _coercion_expected = Uongo
            # On Android CLI_COERCION_WARNING ni sio printed when all the
            # locale environment variables are undefined ama empty. When
            # this code path ni run ukijumuisha environ['LC_ALL'] == 'C', then
            # LEGACY_LOCALE_WARNING ni printed.
            ikiwa (support.is_android and
                    _expected_warnings == [CLI_COERCION_WARNING]):
                _expected_warnings = Tupu
            self._check_child_encoding_details(base_var_dict,
                                               fs_encoding,
                                               stream_encoding,
                                               _expected_warnings,
                                               _coercion_expected)

        # Check behaviour kila explicitly configured locales
        kila locale_to_set kwenye EXPECTED_C_LOCALE_EQUIVALENTS:
            kila env_var kwenye ("LANG", "LC_CTYPE"):
                ukijumuisha self.subTest(env_var=env_var,
                                  nominal_locale=locale_to_set,
                                  PYTHONCOERCECLOCALE=coerce_c_locale):
                    var_dict = base_var_dict.copy()
                    var_dict[env_var] = locale_to_set
                    # Check behaviour on successful coercion
                    self._check_child_encoding_details(var_dict,
                                                       fs_encoding,
                                                       stream_encoding,
                                                       expected_warnings,
                                                       coercion_expected)

    eleza test_PYTHONCOERCECLOCALE_not_set(self):
        # This should coerce to the first available target locale by default
        self._check_c_locale_coercion("utf-8", "utf-8", coerce_c_locale=Tupu)

    eleza test_PYTHONCOERCECLOCALE_not_zero(self):
        # *Any* string other than "0" ni considered "set" kila our purposes
        # na hence should result kwenye the locale coercion being enabled
        kila setting kwenye ("", "1", "true", "false"):
            self._check_c_locale_coercion("utf-8", "utf-8", coerce_c_locale=setting)

    eleza test_PYTHONCOERCECLOCALE_set_to_warn(self):
        # PYTHONCOERCECLOCALE=warn enables runtime warnings kila legacy locales
        self._check_c_locale_coercion("utf-8", "utf-8",
                                      coerce_c_locale="warn",
                                      expected_warnings=[CLI_COERCION_WARNING])


    eleza test_PYTHONCOERCECLOCALE_set_to_zero(self):
        # The setting "0" should result kwenye the locale coercion being disabled
        self._check_c_locale_coercion(EXPECTED_C_LOCALE_FS_ENCODING,
                                      EXPECTED_C_LOCALE_STREAM_ENCODING,
                                      coerce_c_locale="0",
                                      coercion_expected=Uongo)
        # Setting LC_ALL=C shouldn't make any difference to the behaviour
        self._check_c_locale_coercion(EXPECTED_C_LOCALE_FS_ENCODING,
                                      EXPECTED_C_LOCALE_STREAM_ENCODING,
                                      coerce_c_locale="0",
                                      LC_ALL="C",
                                      coercion_expected=Uongo)

    eleza test_LC_ALL_set_to_C(self):
        # Setting LC_ALL should render the locale coercion ineffective
        self._check_c_locale_coercion(EXPECTED_C_LOCALE_FS_ENCODING,
                                      EXPECTED_C_LOCALE_STREAM_ENCODING,
                                      coerce_c_locale=Tupu,
                                      LC_ALL="C",
                                      coercion_expected=Uongo)
        # And result kwenye a warning about a lack of locale compatibility
        self._check_c_locale_coercion(EXPECTED_C_LOCALE_FS_ENCODING,
                                      EXPECTED_C_LOCALE_STREAM_ENCODING,
                                      coerce_c_locale="warn",
                                      LC_ALL="C",
                                      expected_warnings=[LEGACY_LOCALE_WARNING],
                                      coercion_expected=Uongo)

    eleza test_PYTHONCOERCECLOCALE_set_to_one(self):
        # skip the test ikiwa the LC_CTYPE locale ni C ama coerced
        old_loc = locale.setlocale(locale.LC_CTYPE, Tupu)
        self.addCleanup(locale.setlocale, locale.LC_CTYPE, old_loc)
        loc = locale.setlocale(locale.LC_CTYPE, "")
        ikiwa loc == "C":
            self.skipTest("test requires LC_CTYPE locale different than C")
        ikiwa loc kwenye TARGET_LOCALES :
            self.skipTest("coerced LC_CTYPE locale: %s" % loc)

        # bpo-35336: PYTHONCOERCECLOCALE=1 must sio coerce the LC_CTYPE locale
        # ikiwa it's sio equal to "C"
        code = 'agiza locale; andika(locale.setlocale(locale.LC_CTYPE, Tupu))'
        env = dict(os.environ, PYTHONCOERCECLOCALE='1')
        cmd = subprocess.run([sys.executable, '-c', code],
                             stdout=subprocess.PIPE,
                             env=env,
                             text=Kweli)
        self.assertEqual(cmd.stdout.rstrip(), loc)


eleza test_main():
    support.run_unittest(
        LocaleConfigurationTests,
        LocaleCoercionTests
    )
    support.reap_children()

ikiwa __name__ == "__main__":
    test_main()
