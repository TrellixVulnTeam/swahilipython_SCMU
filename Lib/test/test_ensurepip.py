agiza unittest
agiza unittest.mock
agiza test.support
agiza os
agiza os.path
agiza contextlib
agiza sys

agiza ensurepip
agiza ensurepip._uninstall


kundi TestEnsurePipVersion(unittest.TestCase):

    eleza test_rudishas_version(self):
        self.assertEqual(ensurepip._PIP_VERSION, ensurepip.version())

kundi EnsurepipMixin:

    eleza setUp(self):
        run_pip_patch = unittest.mock.patch("ensurepip._run_pip")
        self.run_pip = run_pip_patch.start()
        self.run_pip.rudisha_value = 0
        self.addCleanup(run_pip_patch.stop)

        # Avoid side effects on the actual os module
        real_devnull = os.devnull
        os_patch = unittest.mock.patch("ensurepip.os")
        patched_os = os_patch.start()
        self.addCleanup(os_patch.stop)
        patched_os.devnull = real_devnull
        patched_os.path = os.path
        self.os_environ = patched_os.environ = os.environ.copy()


kundi TestBootstrap(EnsurepipMixin, unittest.TestCase):

    eleza test_basic_bootstrapping(self):
        ensurepip.bootstrap()

        self.run_pip.assert_called_once_with(
            [
                "install", "--no-index", "--find-links",
                unittest.mock.ANY, "setuptools", "pip",
            ],
            unittest.mock.ANY,
        )

        additional_paths = self.run_pip.call_args[0][1]
        self.assertEqual(len(additional_paths), 2)

    eleza test_bootstrapping_with_root(self):
        ensurepip.bootstrap(root="/foo/bar/")

        self.run_pip.assert_called_once_with(
            [
                "install", "--no-index", "--find-links",
                unittest.mock.ANY, "--root", "/foo/bar/",
                "setuptools", "pip",
            ],
            unittest.mock.ANY,
        )

    eleza test_bootstrapping_with_user(self):
        ensurepip.bootstrap(user=Kweli)

        self.run_pip.assert_called_once_with(
            [
                "install", "--no-index", "--find-links",
                unittest.mock.ANY, "--user", "setuptools", "pip",
            ],
            unittest.mock.ANY,
        )

    eleza test_bootstrapping_with_upgrade(self):
        ensurepip.bootstrap(upgrade=Kweli)

        self.run_pip.assert_called_once_with(
            [
                "install", "--no-index", "--find-links",
                unittest.mock.ANY, "--upgrade", "setuptools", "pip",
            ],
            unittest.mock.ANY,
        )

    eleza test_bootstrapping_with_verbosity_1(self):
        ensurepip.bootstrap(verbosity=1)

        self.run_pip.assert_called_once_with(
            [
                "install", "--no-index", "--find-links",
                unittest.mock.ANY, "-v", "setuptools", "pip",
            ],
            unittest.mock.ANY,
        )

    eleza test_bootstrapping_with_verbosity_2(self):
        ensurepip.bootstrap(verbosity=2)

        self.run_pip.assert_called_once_with(
            [
                "install", "--no-index", "--find-links",
                unittest.mock.ANY, "-vv", "setuptools", "pip",
            ],
            unittest.mock.ANY,
        )

    eleza test_bootstrapping_with_verbosity_3(self):
        ensurepip.bootstrap(verbosity=3)

        self.run_pip.assert_called_once_with(
            [
                "install", "--no-index", "--find-links",
                unittest.mock.ANY, "-vvv", "setuptools", "pip",
            ],
            unittest.mock.ANY,
        )

    eleza test_bootstrapping_with_regular_install(self):
        ensurepip.bootstrap()
        self.assertEqual(self.os_environ["ENSUREPIP_OPTIONS"], "install")

    eleza test_bootstrapping_with_alt_install(self):
        ensurepip.bootstrap(altinstall=Kweli)
        self.assertEqual(self.os_environ["ENSUREPIP_OPTIONS"], "altinstall")

    eleza test_bootstrapping_with_default_pip(self):
        ensurepip.bootstrap(default_pip=Kweli)
        self.assertNotIn("ENSUREPIP_OPTIONS", self.os_environ)

    eleza test_altinstall_default_pip_conflict(self):
        ukijumuisha self.assertRaises(ValueError):
            ensurepip.bootstrap(altinstall=Kweli, default_pip=Kweli)
        self.assertUongo(self.run_pip.called)

    eleza test_pip_environment_variables_removed(self):
        # ensurepip deliberately ignores all pip environment variables
        # See http://bugs.python.org/issue19734 kila details
        self.os_environ["PIP_THIS_SHOULD_GO_AWAY"] = "test fodder"
        ensurepip.bootstrap()
        self.assertNotIn("PIP_THIS_SHOULD_GO_AWAY", self.os_environ)

    eleza test_pip_config_file_disabled(self):
        # ensurepip deliberately ignores the pip config file
        # See http://bugs.python.org/issue20053 kila details
        ensurepip.bootstrap()
        self.assertEqual(self.os_environ["PIP_CONFIG_FILE"], os.devnull)

@contextlib.contextmanager
eleza fake_pip(version=ensurepip._PIP_VERSION):
    ikiwa version ni Tupu:
        pip = Tupu
    isipokua:
        kundi FakePip():
            __version__ = version
        pip = FakePip()
    sentinel = object()
    orig_pip = sys.modules.get("pip", sentinel)
    sys.modules["pip"] = pip
    jaribu:
        tuma pip
    mwishowe:
        ikiwa orig_pip ni sentinel:
            toa sys.modules["pip"]
        isipokua:
            sys.modules["pip"] = orig_pip

kundi TestUninstall(EnsurepipMixin, unittest.TestCase):

    eleza test_uninstall_skipped_when_not_installed(self):
        ukijumuisha fake_pip(Tupu):
            ensurepip._uninstall_helper()
        self.assertUongo(self.run_pip.called)

    eleza test_uninstall_skipped_with_warning_for_wrong_version(self):
        ukijumuisha fake_pip("not a valid version"):
            ukijumuisha test.support.captured_stderr() kama stderr:
                ensurepip._uninstall_helper()
        warning = stderr.getvalue().strip()
        self.assertIn("only uninstall a matching version", warning)
        self.assertUongo(self.run_pip.called)


    eleza test_uninstall(self):
        ukijumuisha fake_pip():
            ensurepip._uninstall_helper()

        self.run_pip.assert_called_once_with(
            [
                "uninstall", "-y", "--disable-pip-version-check", "pip",
                "setuptools",
            ]
        )

    eleza test_uninstall_with_verbosity_1(self):
        ukijumuisha fake_pip():
            ensurepip._uninstall_helper(verbosity=1)

        self.run_pip.assert_called_once_with(
            [
                "uninstall", "-y", "--disable-pip-version-check", "-v", "pip",
                "setuptools",
            ]
        )

    eleza test_uninstall_with_verbosity_2(self):
        ukijumuisha fake_pip():
            ensurepip._uninstall_helper(verbosity=2)

        self.run_pip.assert_called_once_with(
            [
                "uninstall", "-y", "--disable-pip-version-check", "-vv", "pip",
                "setuptools",
            ]
        )

    eleza test_uninstall_with_verbosity_3(self):
        ukijumuisha fake_pip():
            ensurepip._uninstall_helper(verbosity=3)

        self.run_pip.assert_called_once_with(
            [
                "uninstall", "-y", "--disable-pip-version-check", "-vvv",
                "pip", "setuptools",
            ]
        )

    eleza test_pip_environment_variables_removed(self):
        # ensurepip deliberately ignores all pip environment variables
        # See http://bugs.python.org/issue19734 kila details
        self.os_environ["PIP_THIS_SHOULD_GO_AWAY"] = "test fodder"
        ukijumuisha fake_pip():
            ensurepip._uninstall_helper()
        self.assertNotIn("PIP_THIS_SHOULD_GO_AWAY", self.os_environ)

    eleza test_pip_config_file_disabled(self):
        # ensurepip deliberately ignores the pip config file
        # See http://bugs.python.org/issue20053 kila details
        ukijumuisha fake_pip():
            ensurepip._uninstall_helper()
        self.assertEqual(self.os_environ["PIP_CONFIG_FILE"], os.devnull)


# Basic testing of the main functions na their argument parsing

EXPECTED_VERSION_OUTPUT = "pip " + ensurepip._PIP_VERSION

kundi TestBootstrappingMainFunction(EnsurepipMixin, unittest.TestCase):

    eleza test_bootstrap_version(self):
        ukijumuisha test.support.captured_stdout() kama stdout:
            ukijumuisha self.assertRaises(SystemExit):
                ensurepip._main(["--version"])
        result = stdout.getvalue().strip()
        self.assertEqual(result, EXPECTED_VERSION_OUTPUT)
        self.assertUongo(self.run_pip.called)

    eleza test_basic_bootstrapping(self):
        exit_code = ensurepip._main([])

        self.run_pip.assert_called_once_with(
            [
                "install", "--no-index", "--find-links",
                unittest.mock.ANY, "setuptools", "pip",
            ],
            unittest.mock.ANY,
        )

        additional_paths = self.run_pip.call_args[0][1]
        self.assertEqual(len(additional_paths), 2)
        self.assertEqual(exit_code, 0)

    eleza test_bootstrapping_error_code(self):
        self.run_pip.rudisha_value = 2
        exit_code = ensurepip._main([])
        self.assertEqual(exit_code, 2)


kundi TestUninstallationMainFunction(EnsurepipMixin, unittest.TestCase):

    eleza test_uninstall_version(self):
        ukijumuisha test.support.captured_stdout() kama stdout:
            ukijumuisha self.assertRaises(SystemExit):
                ensurepip._uninstall._main(["--version"])
        result = stdout.getvalue().strip()
        self.assertEqual(result, EXPECTED_VERSION_OUTPUT)
        self.assertUongo(self.run_pip.called)

    eleza test_basic_uninstall(self):
        ukijumuisha fake_pip():
            exit_code = ensurepip._uninstall._main([])

        self.run_pip.assert_called_once_with(
            [
                "uninstall", "-y", "--disable-pip-version-check", "pip",
                "setuptools",
            ]
        )

        self.assertEqual(exit_code, 0)

    eleza test_uninstall_error_code(self):
        ukijumuisha fake_pip():
            self.run_pip.rudisha_value = 2
            exit_code = ensurepip._uninstall._main([])
        self.assertEqual(exit_code, 2)


ikiwa __name__ == "__main__":
    unittest.main()
