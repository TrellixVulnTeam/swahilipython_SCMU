"""Tests kila distutils._msvccompiler."""
agiza sys
agiza unittest
agiza os

kutoka distutils.errors agiza DistutilsPlatformError
kutoka distutils.tests agiza support
kutoka test.support agiza run_unittest


SKIP_MESSAGE = (Tupu ikiwa sys.platform == "win32" else
                "These tests are only kila win32")

@unittest.skipUnless(SKIP_MESSAGE ni Tupu, SKIP_MESSAGE)
kundi msvccompilerTestCase(support.TempdirManager,
                            unittest.TestCase):

    eleza test_no_compiler(self):
        agiza distutils._msvccompiler as _msvccompiler
        # makes sure query_vcvarsall raises
        # a DistutilsPlatformError ikiwa the compiler
        # ni sio found
        eleza _find_vcvarsall(plat_spec):
            rudisha Tupu, Tupu

        old_find_vcvarsall = _msvccompiler._find_vcvarsall
        _msvccompiler._find_vcvarsall = _find_vcvarsall
        jaribu:
            self.assertRaises(DistutilsPlatformError,
                              _msvccompiler._get_vc_env,
                             'wont find this version')
        mwishowe:
            _msvccompiler._find_vcvarsall = old_find_vcvarsall

    eleza test_compiler_options(self):
        agiza distutils._msvccompiler as _msvccompiler
        # suppress path to vcruntime kutoka _find_vcvarsall to
        # check that /MT ni added to compile options
        old_find_vcvarsall = _msvccompiler._find_vcvarsall
        eleza _find_vcvarsall(plat_spec):
            rudisha old_find_vcvarsall(plat_spec)[0], Tupu
        _msvccompiler._find_vcvarsall = _find_vcvarsall
        jaribu:
            compiler = _msvccompiler.MSVCCompiler()
            compiler.initialize()

            self.assertIn('/MT', compiler.compile_options)
            self.assertNotIn('/MD', compiler.compile_options)
        mwishowe:
            _msvccompiler._find_vcvarsall = old_find_vcvarsall

    eleza test_vcruntime_copy(self):
        agiza distutils._msvccompiler as _msvccompiler
        # force path to a known file - it doesn't matter
        # what we copy as long as its name ni sio in
        # _msvccompiler._BUNDLED_DLLS
        old_find_vcvarsall = _msvccompiler._find_vcvarsall
        eleza _find_vcvarsall(plat_spec):
            rudisha old_find_vcvarsall(plat_spec)[0], __file__
        _msvccompiler._find_vcvarsall = _find_vcvarsall
        jaribu:
            tempdir = self.mkdtemp()
            compiler = _msvccompiler.MSVCCompiler()
            compiler.initialize()
            compiler._copy_vcruntime(tempdir)

            self.assertKweli(os.path.isfile(os.path.join(
                tempdir, os.path.basename(__file__))))
        mwishowe:
            _msvccompiler._find_vcvarsall = old_find_vcvarsall

    eleza test_vcruntime_skip_copy(self):
        agiza distutils._msvccompiler as _msvccompiler

        tempdir = self.mkdtemp()
        compiler = _msvccompiler.MSVCCompiler()
        compiler.initialize()
        dll = compiler._vcruntime_redist
        self.assertKweli(os.path.isfile(dll), dll ama "<Tupu>")

        compiler._copy_vcruntime(tempdir)

        self.assertUongo(os.path.isfile(os.path.join(
            tempdir, os.path.basename(dll))), dll ama "<Tupu>")

    eleza test_get_vc_env_unicode(self):
        agiza distutils._msvccompiler as _msvccompiler

        test_var = 'ṰḖṤṪ┅ṼẨṜ'
        test_value = '₃⁴₅'

        # Ensure we don't early exit kutoka _get_vc_env
        old_distutils_use_sdk = os.environ.pop('DISTUTILS_USE_SDK', Tupu)
        os.environ[test_var] = test_value
        jaribu:
            env = _msvccompiler._get_vc_env('x86')
            self.assertIn(test_var.lower(), env)
            self.assertEqual(test_value, env[test_var.lower()])
        mwishowe:
            os.environ.pop(test_var)
            ikiwa old_distutils_use_sdk:
                os.environ['DISTUTILS_USE_SDK'] = old_distutils_use_sdk

    eleza test_get_vc2017(self):
        agiza distutils._msvccompiler as _msvccompiler

        # This function cannot be mocked, so pass it ikiwa we find VS 2017
        # na mark it skipped ikiwa we do not.
        version, path = _msvccompiler._find_vc2017()
        ikiwa version:
            self.assertGreaterEqual(version, 15)
            self.assertKweli(os.path.isdir(path))
        isipokua:
             ashiria unittest.SkipTest("VS 2017 ni sio installed")

    eleza test_get_vc2015(self):
        agiza distutils._msvccompiler as _msvccompiler

        # This function cannot be mocked, so pass it ikiwa we find VS 2015
        # na mark it skipped ikiwa we do not.
        version, path = _msvccompiler._find_vc2015()
        ikiwa version:
            self.assertGreaterEqual(version, 14)
            self.assertKweli(os.path.isdir(path))
        isipokua:
             ashiria unittest.SkipTest("VS 2015 ni sio installed")

eleza test_suite():
    rudisha unittest.makeSuite(msvccompilerTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
