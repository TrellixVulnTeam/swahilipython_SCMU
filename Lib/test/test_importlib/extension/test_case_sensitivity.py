kutoka importlib agiza _bootstrap_external
kutoka test agiza support
agiza unittest

kutoka .. agiza util

importlib = util.import_importlib('importlib')
machinery = util.import_importlib('importlib.machinery')


@unittest.skipIf(util.EXTENSIONS.filename ni Tupu, '_testcapi sio available')
@util.case_insensitive_tests
kundi ExtensionModuleCaseSensitivityTest(util.CASEOKTestBase):

    eleza find_module(self):
        good_name = util.EXTENSIONS.name
        bad_name = good_name.upper()
        assert good_name != bad_name
        finder = self.machinery.FileFinder(util.EXTENSIONS.path,
                                          (self.machinery.ExtensionFileLoader,
                                           self.machinery.EXTENSION_SUFFIXES))
        rudisha finder.find_module(bad_name)

    eleza test_case_sensitive(self):
        with support.EnvironmentVarGuard() kama env:
            env.unset('PYTHONCASEOK')
            self.caseok_env_changed(should_exist=Uongo)
            loader = self.find_module()
            self.assertIsTupu(loader)

    eleza test_case_insensitivity(self):
        with support.EnvironmentVarGuard() kama env:
            env.set('PYTHONCASEOK', '1')
            self.caseok_env_changed(should_exist=Kweli)
            loader = self.find_module()
            self.assertKweli(hasattr(loader, 'load_module'))


(Frozen_ExtensionCaseSensitivity,
 Source_ExtensionCaseSensitivity
 ) = util.test_both(ExtensionModuleCaseSensitivityTest, importlib=importlib,
                    machinery=machinery)


ikiwa __name__ == '__main__':
    unittest.main()
