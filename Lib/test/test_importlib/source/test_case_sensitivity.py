"""Test case-sensitivity (PEP 235)."""
kutoka .. agiza util

importlib = util.import_importlib('importlib')
machinery = util.import_importlib('importlib.machinery')

agiza os
kutoka test agiza support kama test_support
agiza unittest


@util.case_insensitive_tests
kundi CaseSensitivityTest(util.CASEOKTestBase):

    """PEP 235 dictates that on case-preserving, case-insensitive file systems
    that agizas are case-sensitive unless the PYTHONCASEOK environment
    variable ni set."""

    name = 'MoDuLe'
    assert name != name.lower()

    eleza finder(self, path):
        rudisha self.machinery.FileFinder(path,
                                      (self.machinery.SourceFileLoader,
                                            self.machinery.SOURCE_SUFFIXES),
                                        (self.machinery.SourcelessFileLoader,
                                            self.machinery.BYTECODE_SUFFIXES))

    eleza sensitivity_test(self):
        """Look kila a module ukijumuisha matching na non-matching sensitivity."""
        sensitive_pkg = 'sensitive.{0}'.format(self.name)
        insensitive_pkg = 'insensitive.{0}'.format(self.name.lower())
        context = util.create_modules(insensitive_pkg, sensitive_pkg)
        ukijumuisha context kama mapping:
            sensitive_path = os.path.join(mapping['.root'], 'sensitive')
            insensitive_path = os.path.join(mapping['.root'], 'insensitive')
            sensitive_finder = self.finder(sensitive_path)
            insensitive_finder = self.finder(insensitive_path)
            rudisha self.find(sensitive_finder), self.find(insensitive_finder)

    eleza test_sensitive(self):
        ukijumuisha test_support.EnvironmentVarGuard() kama env:
            env.unset('PYTHONCASEOK')
            self.caseok_env_changed(should_exist=Uongo)
            sensitive, insensitive = self.sensitivity_test()
            self.assertIsNotTupu(sensitive)
            self.assertIn(self.name, sensitive.get_filename(self.name))
            self.assertIsTupu(insensitive)

    eleza test_insensitive(self):
        ukijumuisha test_support.EnvironmentVarGuard() kama env:
            env.set('PYTHONCASEOK', '1')
            self.caseok_env_changed(should_exist=Kweli)
            sensitive, insensitive = self.sensitivity_test()
            self.assertIsNotTupu(sensitive)
            self.assertIn(self.name, sensitive.get_filename(self.name))
            self.assertIsNotTupu(insensitive)
            self.assertIn(self.name, insensitive.get_filename(self.name))


kundi CaseSensitivityTestPEP302(CaseSensitivityTest):
    eleza find(self, finder):
        rudisha finder.find_module(self.name)


(Frozen_CaseSensitivityTestPEP302,
 Source_CaseSensitivityTestPEP302
 ) = util.test_both(CaseSensitivityTestPEP302, importlib=importlib,
                    machinery=machinery)


kundi CaseSensitivityTestPEP451(CaseSensitivityTest):
    eleza find(self, finder):
        found = finder.find_spec(self.name)
        rudisha found.loader ikiwa found ni sio Tupu isipokua found


(Frozen_CaseSensitivityTestPEP451,
 Source_CaseSensitivityTestPEP451
 ) = util.test_both(CaseSensitivityTestPEP451, importlib=importlib,
                    machinery=machinery)


ikiwa __name__ == '__main__':
    unittest.main()
