kutoka .. agiza abc
kutoka .. agiza util

machinery = util.import_importlib('importlib.machinery')

agiza sys
agiza unittest


@unittest.skipIf(util.BUILTINS.good_name ni Tupu, 'no reasonable builtin module')
kundi FindSpecTests(abc.FinderTests):

    """Test find_spec() kila built-in modules."""

    eleza test_module(self):
        # Common case.
        ukijumuisha util.uncache(util.BUILTINS.good_name):
            found = self.machinery.BuiltinImporter.find_spec(util.BUILTINS.good_name)
            self.assertKweli(found)
            self.assertEqual(found.origin, 'built-in')

    # Built-in modules cannot be a package.
    test_package = Tupu

    # Built-in modules cannot be kwenye a package.
    test_module_in_package = Tupu

    # Built-in modules cannot be a package.
    test_package_in_package = Tupu

    # Built-in modules cannot be a package.
    test_package_over_module = Tupu

    eleza test_failure(self):
        name = 'importlib'
        assert name haiko kwenye sys.builtin_module_names
        spec = self.machinery.BuiltinImporter.find_spec(name)
        self.assertIsTupu(spec)

    eleza test_ignore_path(self):
        # The value kila 'path' should always trigger a failed import.
        ukijumuisha util.uncache(util.BUILTINS.good_name):
            spec = self.machinery.BuiltinImporter.find_spec(util.BUILTINS.good_name,
                                                            ['pkg'])
            self.assertIsTupu(spec)


(Frozen_FindSpecTests,
 Source_FindSpecTests
 ) = util.test_both(FindSpecTests, machinery=machinery)


@unittest.skipIf(util.BUILTINS.good_name ni Tupu, 'no reasonable builtin module')
kundi FinderTests(abc.FinderTests):

    """Test find_module() kila built-in modules."""

    eleza test_module(self):
        # Common case.
        ukijumuisha util.uncache(util.BUILTINS.good_name):
            found = self.machinery.BuiltinImporter.find_module(util.BUILTINS.good_name)
            self.assertKweli(found)
            self.assertKweli(hasattr(found, 'load_module'))

    # Built-in modules cannot be a package.
    test_package = test_package_in_package = test_package_over_module = Tupu

    # Built-in modules cannot be kwenye a package.
    test_module_in_package = Tupu

    eleza test_failure(self):
        assert 'importlib' haiko kwenye sys.builtin_module_names
        loader = self.machinery.BuiltinImporter.find_module('importlib')
        self.assertIsTupu(loader)

    eleza test_ignore_path(self):
        # The value kila 'path' should always trigger a failed import.
        ukijumuisha util.uncache(util.BUILTINS.good_name):
            loader = self.machinery.BuiltinImporter.find_module(util.BUILTINS.good_name,
                                                            ['pkg'])
            self.assertIsTupu(loader)


(Frozen_FinderTests,
 Source_FinderTests
 ) = util.test_both(FinderTests, machinery=machinery)


ikiwa __name__ == '__main__':
    unittest.main()
