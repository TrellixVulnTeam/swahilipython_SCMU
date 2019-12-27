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

    eleza test_returns_version(self):
        self.assertEqual(ensurepip._PIP_VERSION, ensurepip.version())

kundi EnsurepipMixin:

    eleza setUp(self):
        run_pip_patch = unittest.mock.patch("ensurepip._run_pip")
        self.run_pip = run_pip_patch.start()
        self.run_pip.return_value = 0
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
        ensurepip.bootstrap(user=True)

        self.run_pip.assert_called_once_with(
            [
                "install", "--no-index", "--find-links",
                unittest.mock.ANY, "--user", "setuptools", "pip",
            ],
            unittest.mock.ANY,
        )

    eleza test_bootstrapping_with_upgrade(self):
        ensurepip.bootstrap(upgrade=True)

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
        ensurepip.bootstrap(altinstall=True)
        self.assertEqual(self.os_environ["ENSUREPIP_OPTIONS"], "altinstall")

    eleza test_bootstrapping_with_default_pip(self):
        ensurepip.bootstrap(default_pip=True)
        self.assertNotIn("ENSUREPIP_OPTIONS", self.os_environ)

    eleza test_altinstall_default_pip_conflict(self):
        with self.assertRaises(ValueError):
            ensurepip.bootstrap(altinstall=True, default_pip=True)
        self.assertFalse(self.run_pip.called)

    eleza test_pip_environment_variables_removed(self):
        # ensurepip deliberately ignores all pip environment variables
        # See http://bugs.python.org/issue19734 for details
        self.os_environ["PIP_THIS_SHOULD_GO_AWAY"] = "test fodder"
        ensurepip.bootstrap()
        self.assertNotIn("PIP_THIS_SHOULD_GO_AWAY", self.os_environ)

    eleza test_pip_config_file_disabled(self):
        # ensurepip deliberately ignores the pip config file
        # See http://bugs.python.org/issue20053 for details
        ensurepip.bootstrap()
        self.assertEqual(self.os_environ["PIP_CONFIG_FILE"], os.devnull)

@contextlib.contextmanager
eleza fake_pip(version=ensurepip._PIP_VERSION):
    ikiwa version is None:
        pip = None
    else:
        kundi FakePip():
            __version__ = version
        pip = FakePip()
    sentinel = object()
    orig_pip = sys.modules.get("pip", sentinel)
    sys.modules["pip"] = pip
    try:
        yield pip
    finally:
        ikiwa orig_pip is sentinel:
            del sys.modules["pip"]
        else:
            sys.modules["pip"] = orig_pip

kundi TestUninstall(EnsurepipMixin, unittest.TestCase):

    eleza test_uninstall_skipped_when_not_installed(self):
        with fake_pip(None):
            ensurepip._uninstall_helper()
        self.assertFalse(self.run_pip.called)

    eleza test_uninstall_skipped_with_warning_for_wrong_version(self):
        with fake_pip("not a valid version"):
            with test.support.captured_stderr() as stderr:
                ensurepip._uninstall_helper()
        warning = stderr.getvalue().strip()
        self.assertIn("only uninstall a matching version", warning)
        self.assertFalse(self.run_pip.called)


    eleza test_uninstall(self):
        with fake_pip():
            ensurepip._uninstall_helper()

        self.run_pip.assert_called_once_with(
            [
                "uninstall", "-y", "--disable-pip-version-check", "pip",
                "setuptools",
            ]
        )

    eleza test_uninstall_with_verbosity_1(self):
        with fake_pip():
            ensurepip._uninstall_helper(verbosity=1)

        self.run_pip.assert_called_once_with(
            [
                "uninstall", "-y", "--disable-pip-version-check", "-v", "pip",
                "setuptools",
            ]
        )

    eleza test_uninstall_with_verbosity_2(self):
        with fake_pip():
            ensurepip._uninstall_helper(verbosity=2)

        self.run_pip.assert_called_once_with(
            [
                "uninstall", "-y", "--disable-pip-version-check", "-vv", "pip",
                "setuptools",
            ]
        )

    eleza test_uninstall_with_verbosity_3(self):
        with fake_pip():
            ensurepip._uninstall_helper(verbosity=3)

        self.run_pip.assert_called_once_with(
            [
                "uninstall", "-y", "--disable-pip-version-check", "-vvv",
                "pip", "setuptools",
            ]
        )

    eleza test_pip_environment_variables_removed(self):
        # ensurepip deliberately ignores all pip environment variables
        # See http://bugs.python.org/issue19734 for details
        self.os_environ["PIP_THIS_SHOULD_GO_AWAY"] = "test fodder"
        with fake_pip():
            ensurepip._uninstall_helper()
        self.assertNotIn("PIP_THIS_SHOULD_GO_AWAY", self.os_environ)

    eleza test_pip_config_file_disabled(self):
        # ensurepip deliberately ignores the pip config file
        # See http://bugs.python.org/issue20053 for details
        with fake_pip():
            ensurepip._uninstall_helper()
        self.assertEqual(self.os_environ["PIP_CONFIG_FILE"], os.devnull)


# Basic testing of the main functions and their argument parsing

EXPECTED_VERSION_OUTPUT = "pip " + ensurepip._PIP_VERSION

kundi TestBootstrappingMainFunction(EnsurepipMixin, unittest.TestCase):

    eleza test_bootstrap_version(self):
        with test.support.captured_stdout() as stdout:
            with self.assertRaises(SystemExit):
                ensurepip._main(["--version"])
        result = stdout.getvalue().strip()
        self.assertEqual(result, EXPECTED_VERSION_OUTPUT)
        self.assertFalse(self.run_pip.called)

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
        self.run_pip.return_value = 2
        exit_code = ensurepip._main([])
        self.assertEqual(exit_code, 2)


kundi TestUninstallationMainFunction(EnsurepipMixin, unittest.TestCase):

    eleza test_uninstall_version(self):
        with test.support.captured_stdout() as stdout:
            with self.assertRaises(SystemExit):
                ensurepip._uninstall._main(["--version"])
        result = stdout.getvalue().strip()
        self.assertEqual(result, EXPECTED_VERSION_OUTPUT)
        self.assertFalse(self.run_pip.called)

    eleza test_basic_uninstall(self):
        with fake_pip():
            exit_code = ensurepip._uninstall._main([])

        self.run_pip.assert_called_once_with(
            [
                "uninstall", "-y", "--disable-pip-version-check", "pip",
                "setuptools",
            ]
        )

        self.assertEqual(exit_code, 0)

    eleza test_uninstall_error_code(self):
        with fake_pip():
            self.run_pip.return_value = 2
            exit_code = ensurepip._uninstall._main([])
        self.assertEqual(exit_code, 2)


ikiwa __name__ == "__main__":
    unittest.main()
