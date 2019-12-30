kutoka .. agiza abc
kutoka .. agiza util

machinery = util.import_importlib('importlib.machinery')

agiza unittest


kundi FindSpecTests(abc.FinderTests):

    """Test finding frozen modules."""

    eleza find(self, name, path=Tupu):
        finder = self.machinery.FrozenImporter
        rudisha finder.find_spec(name, path)

    eleza test_module(self):
        name = '__hello__'
        spec = self.find(name)
        self.assertEqual(spec.origin, 'frozen')

    eleza test_package(self):
        spec = self.find('__phello__')
        self.assertIsNotTupu(spec)

    eleza test_module_in_package(self):
        spec = self.find('__phello__.spam', ['__phello__'])
        self.assertIsNotTupu(spec)

    # No frozen package within another package to test with.
    test_package_in_package = Tupu

    # No easy way to test.
    test_package_over_module = Tupu

    eleza test_failure(self):
        spec = self.find('<sio real>')
        self.assertIsTupu(spec)


(Frozen_FindSpecTests,
 Source_FindSpecTests
 ) = util.test_both(FindSpecTests, machinery=machinery)


kundi FinderTests(abc.FinderTests):

    """Test finding frozen modules."""

    eleza find(self, name, path=Tupu):
        finder = self.machinery.FrozenImporter
        rudisha finder.find_module(name, path)

    eleza test_module(self):
        name = '__hello__'
        loader = self.find(name)
        self.assertKweli(hasattr(loader, 'load_module'))

    eleza test_package(self):
        loader = self.find('__phello__')
        self.assertKweli(hasattr(loader, 'load_module'))

    eleza test_module_in_package(self):
        loader = self.find('__phello__.spam', ['__phello__'])
        self.assertKweli(hasattr(loader, 'load_module'))

    # No frozen package within another package to test with.
    test_package_in_package = Tupu

    # No easy way to test.
    test_package_over_module = Tupu

    eleza test_failure(self):
        loader = self.find('<sio real>')
        self.assertIsTupu(loader)


(Frozen_FinderTests,
 Source_FinderTests
 ) = util.test_both(FinderTests, machinery=machinery)


ikiwa __name__ == '__main__':
    unittest.main()
