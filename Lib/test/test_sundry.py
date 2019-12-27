"""Do a minimal test of all the modules that aren't otherwise tested."""
agiza importlib
agiza platform
agiza sys
kutoka test agiza support
agiza unittest

kundi TestUntestedModules(unittest.TestCase):
    eleza test_untested_modules_can_be_imported(self):
        untested = ('encodings', 'formatter')
        with support.check_warnings(quiet=True):
            for name in untested:
                try:
                    support.import_module('test.test_{}'.format(name))
                except unittest.SkipTest:
                    importlib.import_module(name)
                else:
                    self.fail('{} has tests even though test_sundry claims '
                              'otherwise'.format(name))

            agiza distutils.bcppcompiler
            agiza distutils.ccompiler
            agiza distutils.cygwinccompiler
            agiza distutils.filelist
            agiza distutils.text_file
            agiza distutils.unixccompiler

            agiza distutils.command.bdist_dumb
            ikiwa sys.platform.startswith('win') and not platform.win32_is_iot():
                agiza distutils.command.bdist_msi
            agiza distutils.command.bdist
            agiza distutils.command.bdist_rpm
            agiza distutils.command.bdist_wininst
            agiza distutils.command.build_clib
            agiza distutils.command.build_ext
            agiza distutils.command.build
            agiza distutils.command.clean
            agiza distutils.command.config
            agiza distutils.command.install_data
            agiza distutils.command.install_egg_info
            agiza distutils.command.install_headers
            agiza distutils.command.install_lib
            agiza distutils.command.register
            agiza distutils.command.sdist
            agiza distutils.command.upload

            agiza html.entities

            try:
                agiza tty  # Not available on Windows
            except ImportError:
                ikiwa support.verbose:
                    andika("skipping tty")


ikiwa __name__ == "__main__":
    unittest.main()
