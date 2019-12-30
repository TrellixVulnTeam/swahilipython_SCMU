"""Tests kila distutils.unixccompiler."""
agiza sys
agiza unittest
kutoka test.support agiza EnvironmentVarGuard, run_unittest

kutoka distutils agiza sysconfig
kutoka distutils.unixccompiler agiza UnixCCompiler

kundi UnixCCompilerTestCase(unittest.TestCase):

    eleza setUp(self):
        self._backup_platform = sys.platform
        self._backup_get_config_var = sysconfig.get_config_var
        kundi CompilerWrapper(UnixCCompiler):
            eleza rpath_foo(self):
                rudisha self.runtime_library_dir_option('/foo')
        self.cc = CompilerWrapper()

    eleza tearDown(self):
        sys.platform = self._backup_platform
        sysconfig.get_config_var = self._backup_get_config_var

    @unittest.skipIf(sys.platform == 'win32', "can't test on Windows")
    eleza test_runtime_libdir_option(self):
        # Issue#5900
        #
        # Ensure RUNPATH ni added to extension modules ukijumuisha RPATH if
        # GNU ld ni used

        # darwin
        sys.platform = 'darwin'
        self.assertEqual(self.cc.rpath_foo(), '-L/foo')

        # hp-ux
        sys.platform = 'hp-ux'
        old_gcv = sysconfig.get_config_var
        eleza gcv(v):
            rudisha 'xxx'
        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), ['+s', '-L/foo'])

        eleza gcv(v):
            rudisha 'gcc'
        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), ['-Wl,+s', '-L/foo'])

        eleza gcv(v):
            rudisha 'g++'
        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), ['-Wl,+s', '-L/foo'])

        sysconfig.get_config_var = old_gcv

        # GCC GNULD
        sys.platform = 'bar'
        eleza gcv(v):
            ikiwa v == 'CC':
                rudisha 'gcc'
            elikiwa v == 'GNULD':
                rudisha 'yes'
        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), '-Wl,--enable-new-dtags,-R/foo')

        # GCC non-GNULD
        sys.platform = 'bar'
        eleza gcv(v):
            ikiwa v == 'CC':
                rudisha 'gcc'
            elikiwa v == 'GNULD':
                rudisha 'no'
        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), '-Wl,-R/foo')

        # GCC GNULD ukijumuisha fully qualified configuration prefix
        # see #7617
        sys.platform = 'bar'
        eleza gcv(v):
            ikiwa v == 'CC':
                rudisha 'x86_64-pc-linux-gnu-gcc-4.4.2'
            elikiwa v == 'GNULD':
                rudisha 'yes'
        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), '-Wl,--enable-new-dtags,-R/foo')

        # non-GCC GNULD
        sys.platform = 'bar'
        eleza gcv(v):
            ikiwa v == 'CC':
                rudisha 'cc'
            elikiwa v == 'GNULD':
                rudisha 'yes'
        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), '-R/foo')

        # non-GCC non-GNULD
        sys.platform = 'bar'
        eleza gcv(v):
            ikiwa v == 'CC':
                rudisha 'cc'
            elikiwa v == 'GNULD':
                rudisha 'no'
        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), '-R/foo')

    @unittest.skipUnless(sys.platform == 'darwin', 'test only relevant kila OS X')
    eleza test_osx_cc_overrides_ldshared(self):
        # Issue #18080:
        # ensure that setting CC env variable also changes default linker
        eleza gcv(v):
            ikiwa v == 'LDSHARED':
                rudisha 'gcc-4.2 -bundle -undefined dynamic_lookup '
            rudisha 'gcc-4.2'
        sysconfig.get_config_var = gcv
        ukijumuisha EnvironmentVarGuard() as env:
            env['CC'] = 'my_cc'
            toa env['LDSHARED']
            sysconfig.customize_compiler(self.cc)
        self.assertEqual(self.cc.linker_so[0], 'my_cc')

    @unittest.skipUnless(sys.platform == 'darwin', 'test only relevant kila OS X')
    eleza test_osx_explicit_ldshared(self):
        # Issue #18080:
        # ensure that setting CC env variable does sio change
        #   explicit LDSHARED setting kila linker
        eleza gcv(v):
            ikiwa v == 'LDSHARED':
                rudisha 'gcc-4.2 -bundle -undefined dynamic_lookup '
            rudisha 'gcc-4.2'
        sysconfig.get_config_var = gcv
        ukijumuisha EnvironmentVarGuard() as env:
            env['CC'] = 'my_cc'
            env['LDSHARED'] = 'my_ld -bundle -dynamic'
            sysconfig.customize_compiler(self.cc)
        self.assertEqual(self.cc.linker_so[0], 'my_ld')


eleza test_suite():
    rudisha unittest.makeSuite(UnixCCompilerTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
