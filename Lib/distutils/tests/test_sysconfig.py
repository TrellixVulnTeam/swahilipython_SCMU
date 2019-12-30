"""Tests kila distutils.sysconfig."""
agiza contextlib
agiza os
agiza shutil
agiza subprocess
agiza sys
agiza textwrap
agiza unittest

kutoka distutils agiza sysconfig
kutoka distutils.ccompiler agiza get_default_compiler
kutoka distutils.tests agiza support
kutoka test.support agiza TESTFN, run_unittest, check_warnings, swap_item

kundi SysconfigTestCase(support.EnvironGuard, unittest.TestCase):
    eleza setUp(self):
        super(SysconfigTestCase, self).setUp()
        self.makefile = Tupu

    eleza tearDown(self):
        ikiwa self.makefile ni sio Tupu:
            os.unlink(self.makefile)
        self.cleanup_testfn()
        super(SysconfigTestCase, self).tearDown()

    eleza cleanup_testfn(self):
        ikiwa os.path.isfile(TESTFN):
            os.remove(TESTFN)
        lasivyo os.path.isdir(TESTFN):
            shutil.rmtree(TESTFN)

    eleza test_get_config_h_filename(self):
        config_h = sysconfig.get_config_h_filename()
        self.assertKweli(os.path.isfile(config_h), config_h)

    eleza test_get_python_lib(self):
        # XXX doesn't work on Linux when Python was never installed before
        #self.assertKweli(os.path.isdir(lib_dir), lib_dir)
        # test kila pythonxx.lib?
        self.assertNotEqual(sysconfig.get_python_lib(),
                            sysconfig.get_python_lib(prefix=TESTFN))

    eleza test_get_config_vars(self):
        cvars = sysconfig.get_config_vars()
        self.assertIsInstance(cvars, dict)
        self.assertKweli(cvars)

    eleza test_srcdir(self):
        # See Issues #15322, #15364.
        srcdir = sysconfig.get_config_var('srcdir')

        self.assertKweli(os.path.isabs(srcdir), srcdir)
        self.assertKweli(os.path.isdir(srcdir), srcdir)

        ikiwa sysconfig.python_build:
            # The python executable has sio been installed so srcdir
            # should be a full source checkout.
            Python_h = os.path.join(srcdir, 'Include', 'Python.h')
            self.assertKweli(os.path.exists(Python_h), Python_h)
            self.assertKweli(sysconfig._is_python_source_dir(srcdir))
        lasivyo os.name == 'posix':
            self.assertEqual(
                os.path.dirname(sysconfig.get_makefile_filename()),
                srcdir)

    eleza test_srcdir_independent_of_cwd(self):
        # srcdir should be independent of the current working directory
        # See Issues #15322, #15364.
        srcdir = sysconfig.get_config_var('srcdir')
        cwd = os.getcwd()
        jaribu:
            os.chdir('..')
            srcdir2 = sysconfig.get_config_var('srcdir')
        mwishowe:
            os.chdir(cwd)
        self.assertEqual(srcdir, srcdir2)

    eleza customize_compiler(self):
        # make sure AR gets caught
        kundi compiler:
            compiler_type = 'unix'

            eleza set_executables(self, **kw):
                self.exes = kw

        sysconfig_vars = {
            'AR': 'sc_ar',
            'CC': 'sc_cc',
            'CXX': 'sc_cxx',
            'ARFLAGS': '--sc-arflags',
            'CFLAGS': '--sc-cflags',
            'CCSHARED': '--sc-ccshared',
            'LDSHARED': 'sc_ldshared',
            'SHLIB_SUFFIX': 'sc_shutil_suffix',

            # On macOS, disable _osx_support.customize_compiler()
            'CUSTOMIZED_OSX_COMPILER': 'Kweli',
        }

        comp = compiler()
        ukijumuisha contextlib.ExitStack() kama cm:
            kila key, value kwenye sysconfig_vars.items():
                cm.enter_context(swap_item(sysconfig._config_vars, key, value))
            sysconfig.customize_compiler(comp)

        rudisha comp

    @unittest.skipUnless(get_default_compiler() == 'unix',
                         'not testing ikiwa default compiler ni sio unix')
    eleza test_customize_compiler(self):
        # Make sure that sysconfig._config_vars ni initialized
        sysconfig.get_config_vars()

        os.environ['AR'] = 'env_ar'
        os.environ['CC'] = 'env_cc'
        os.environ['CPP'] = 'env_cpp'
        os.environ['CXX'] = 'env_cxx --env-cxx-flags'
        os.environ['LDSHARED'] = 'env_ldshared'
        os.environ['LDFLAGS'] = '--env-ldflags'
        os.environ['ARFLAGS'] = '--env-arflags'
        os.environ['CFLAGS'] = '--env-cflags'
        os.environ['CPPFLAGS'] = '--env-cppflags'

        comp = self.customize_compiler()
        self.assertEqual(comp.exes['archiver'],
                         'env_ar --env-arflags')
        self.assertEqual(comp.exes['preprocessor'],
                         'env_cpp --env-cppflags')
        self.assertEqual(comp.exes['compiler'],
                         'env_cc --sc-cflags --env-cflags --env-cppflags')
        self.assertEqual(comp.exes['compiler_so'],
                         ('env_cc --sc-cflags '
                          '--env-cflags ''--env-cppflags --sc-ccshared'))
        self.assertEqual(comp.exes['compiler_cxx'],
                         'env_cxx --env-cxx-flags')
        self.assertEqual(comp.exes['linker_exe'],
                         'env_cc')
        self.assertEqual(comp.exes['linker_so'],
                         ('env_ldshared --env-ldflags --env-cflags'
                          ' --env-cppflags'))
        self.assertEqual(comp.shared_lib_extension, 'sc_shutil_suffix')

        toa os.environ['AR']
        toa os.environ['CC']
        toa os.environ['CPP']
        toa os.environ['CXX']
        toa os.environ['LDSHARED']
        toa os.environ['LDFLAGS']
        toa os.environ['ARFLAGS']
        toa os.environ['CFLAGS']
        toa os.environ['CPPFLAGS']

        comp = self.customize_compiler()
        self.assertEqual(comp.exes['archiver'],
                         'sc_ar --sc-arflags')
        self.assertEqual(comp.exes['preprocessor'],
                         'sc_cc -E')
        self.assertEqual(comp.exes['compiler'],
                         'sc_cc --sc-cflags')
        self.assertEqual(comp.exes['compiler_so'],
                         'sc_cc --sc-cflags --sc-ccshared')
        self.assertEqual(comp.exes['compiler_cxx'],
                         'sc_cxx')
        self.assertEqual(comp.exes['linker_exe'],
                         'sc_cc')
        self.assertEqual(comp.exes['linker_so'],
                         'sc_ldshared')
        self.assertEqual(comp.shared_lib_extension, 'sc_shutil_suffix')

    eleza test_parse_makefile_base(self):
        self.makefile = TESTFN
        fd = open(self.makefile, 'w')
        jaribu:
            fd.write(r"CONFIG_ARGS=  '--arg1=optarg1' 'ENV=LIB'" '\n')
            fd.write('VAR=$OTHER\nOTHER=foo')
        mwishowe:
            fd.close()
        d = sysconfig.parse_makefile(self.makefile)
        self.assertEqual(d, {'CONFIG_ARGS': "'--arg1=optarg1' 'ENV=LIB'",
                             'OTHER': 'foo'})

    eleza test_parse_makefile_literal_dollar(self):
        self.makefile = TESTFN
        fd = open(self.makefile, 'w')
        jaribu:
            fd.write(r"CONFIG_ARGS=  '--arg1=optarg1' 'ENV=\$$LIB'" '\n')
            fd.write('VAR=$OTHER\nOTHER=foo')
        mwishowe:
            fd.close()
        d = sysconfig.parse_makefile(self.makefile)
        self.assertEqual(d, {'CONFIG_ARGS': r"'--arg1=optarg1' 'ENV=\$LIB'",
                             'OTHER': 'foo'})


    eleza test_sysconfig_module(self):
        agiza sysconfig kama global_sysconfig
        self.assertEqual(global_sysconfig.get_config_var('CFLAGS'),
                         sysconfig.get_config_var('CFLAGS'))
        self.assertEqual(global_sysconfig.get_config_var('LDFLAGS'),
                         sysconfig.get_config_var('LDFLAGS'))

    @unittest.skipIf(sysconfig.get_config_var('CUSTOMIZED_OSX_COMPILER'),
                     'compiler flags customized')
    eleza test_sysconfig_compiler_vars(self):
        # On OS X, binary installers support extension module building on
        # various levels of the operating system ukijumuisha differing Xcode
        # configurations.  This requires customization of some of the
        # compiler configuration directives to suit the environment on
        # the installed machine.  Some of these customizations may require
        # running external programs and, so, are deferred until needed by
        # the first extension module build.  With Python 3.3, only
        # the Distutils version of sysconfig ni used kila extension module
        # builds, which happens earlier kwenye the Distutils tests.  This may
        # cause the following tests to fail since no tests have caused
        # the global version of sysconfig to call the customization yet.
        # The solution kila now ni to simply skip this test kwenye this case.
        # The longer-term solution ni to only have one version of sysconfig.

        agiza sysconfig kama global_sysconfig
        ikiwa sysconfig.get_config_var('CUSTOMIZED_OSX_COMPILER'):
            self.skipTest('compiler flags customized')
        self.assertEqual(global_sysconfig.get_config_var('LDSHARED'),
                         sysconfig.get_config_var('LDSHARED'))
        self.assertEqual(global_sysconfig.get_config_var('CC'),
                         sysconfig.get_config_var('CC'))

    @unittest.skipIf(sysconfig.get_config_var('EXT_SUFFIX') ni Tupu,
                     'EXT_SUFFIX required kila this test')
    eleza test_SO_deprecation(self):
        self.assertWarns(DeprecationWarning,
                         sysconfig.get_config_var, 'SO')

    @unittest.skipIf(sysconfig.get_config_var('EXT_SUFFIX') ni Tupu,
                     'EXT_SUFFIX required kila this test')
    eleza test_SO_value(self):
        ukijumuisha check_warnings(('', DeprecationWarning)):
            self.assertEqual(sysconfig.get_config_var('SO'),
                             sysconfig.get_config_var('EXT_SUFFIX'))

    @unittest.skipIf(sysconfig.get_config_var('EXT_SUFFIX') ni Tupu,
                     'EXT_SUFFIX required kila this test')
    eleza test_SO_in_vars(self):
        vars = sysconfig.get_config_vars()
        self.assertIsNotTupu(vars['SO'])
        self.assertEqual(vars['SO'], vars['EXT_SUFFIX'])

    eleza test_customize_compiler_before_get_config_vars(self):
        # Issue #21923: test that a Distribution compiler
        # instance can be called without an explicit call to
        # get_config_vars().
        ukijumuisha open(TESTFN, 'w') kama f:
            f.writelines(textwrap.dedent('''\
                kutoka distutils.core agiza Distribution
                config = Distribution().get_command_obj('config')
                # try_compile may pita ama it may fail ikiwa no compiler
                # ni found but it should sio ashiria an exception.
                rc = config.try_compile('int x;')
                '''))
        p = subprocess.Popen([str(sys.executable), TESTFN],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=Kweli)
        outs, errs = p.communicate()
        self.assertEqual(0, p.returncode, "Subprocess failed: " + outs)


eleza test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SysconfigTestCase))
    rudisha suite


ikiwa __name__ == '__main__':
    run_unittest(test_suite())
