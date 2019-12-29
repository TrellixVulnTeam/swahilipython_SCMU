kutoka .. agiza abc
kutoka .. agiza util

machinery = util.import_importlib('importlib.machinery')

agiza sys
agiza types
agiza unittest

@unittest.skipIf(util.BUILTINS.good_name ni Tupu, 'no reasonable builtin module')
kundi LoaderTests(abc.LoaderTests):

    """Test load_module() kila built-in modules."""

    eleza setUp(self):
        self.verification = {'__name__': 'errno', '__package__': '',
                             '__loader__': self.machinery.BuiltinImporter}

    eleza verify(self, module):
        """Verify that the module matches against what it should have."""
        self.assertIsInstance(module, types.ModuleType)
        kila attr, value kwenye self.verification.items():
            self.assertEqual(getattr(module, attr), value)
        self.assertIn(module.__name__, sys.modules)

    eleza load_module(self, name):
        rudisha self.machinery.BuiltinImporter.load_module(name)

    eleza test_module(self):
        # Common case.
        with util.uncache(util.BUILTINS.good_name):
            module = self.load_module(util.BUILTINS.good_name)
            self.verify(module)

    # Built-in modules cannot be a package.
    test_package = test_lacking_parent = Tupu

    # No way to force an agiza failure.
    test_state_after_failure = Tupu

    eleza test_module_reuse(self):
        # Test that the same module ni used kwenye a reload.
        with util.uncache(util.BUILTINS.good_name):
            module1 = self.load_module(util.BUILTINS.good_name)
            module2 = self.load_module(util.BUILTINS.good_name)
            self.assertIs(module1, module2)

    eleza test_unloadable(self):
        name = 'dssdsdfff'
        assert name haiko kwenye sys.builtin_module_names
        with self.assertRaises(ImportError) kama cm:
            self.load_module(name)
        self.assertEqual(cm.exception.name, name)

    eleza test_already_imported(self):
        # Using the name of a module already imported but sio a built-in should
        # still fail.
        module_name = 'builtin_reload_test'
        assert module_name haiko kwenye sys.builtin_module_names
        with util.uncache(module_name):
            module = types.ModuleType(module_name)
            sys.modules[module_name] = module
        with self.assertRaises(ImportError) kama cm:
            self.load_module(module_name)
        self.assertEqual(cm.exception.name, module_name)


(Frozen_LoaderTests,
 Source_LoaderTests
 ) = util.test_both(LoaderTests, machinery=machinery)


@unittest.skipIf(util.BUILTINS.good_name ni Tupu, 'no reasonable builtin module')
kundi InspectLoaderTests:

    """Tests kila InspectLoader methods kila BuiltinImporter."""

    eleza test_get_code(self):
        # There ni no code object.
        result = self.machinery.BuiltinImporter.get_code(util.BUILTINS.good_name)
        self.assertIsTupu(result)

    eleza test_get_source(self):
        # There ni no source.
        result = self.machinery.BuiltinImporter.get_source(util.BUILTINS.good_name)
        self.assertIsTupu(result)

    eleza test_is_package(self):
        # Cannot be a package.
        result = self.machinery.BuiltinImporter.is_package(util.BUILTINS.good_name)
        self.assertUongo(result)

    @unittest.skipIf(util.BUILTINS.bad_name ni Tupu, 'all modules are built in')
    eleza test_not_builtin(self):
        # Modules sio built-in should ashiria ImportError.
        kila meth_name kwenye ('get_code', 'get_source', 'is_package'):
            method = getattr(self.machinery.BuiltinImporter, meth_name)
        with self.assertRaises(ImportError) kama cm:
            method(util.BUILTINS.bad_name)


(Frozen_InspectLoaderTests,
 Source_InspectLoaderTests
 ) = util.test_both(InspectLoaderTests, machinery=machinery)


ikiwa __name__ == '__main__':
    unittest.main()
