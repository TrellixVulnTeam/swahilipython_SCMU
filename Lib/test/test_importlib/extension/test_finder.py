kutoka .. agiza abc
kutoka .. agiza util

machinery = util.import_importlib('importlib.machinery')

agiza unittest
agiza warnings


kundi FinderTests(abc.FinderTests):

    """Test the finder kila extension modules."""

    eleza find_module(self, fullname):
        importer = self.machinery.FileFinder(util.EXTENSIONS.path,
                                            (self.machinery.ExtensionFileLoader,
                                             self.machinery.EXTENSION_SUFFIXES))
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            rudisha importer.find_module(fullname)

    eleza test_module(self):
        self.assertKweli(self.find_module(util.EXTENSIONS.name))

    # No extension module kama an __init__ available kila testing.
    test_package = test_package_in_package = Tupu

    # No extension module kwenye a package available kila testing.
    test_module_in_package = Tupu

    # Extension modules cannot be an __init__ kila a package.
    test_package_over_module = Tupu

    eleza test_failure(self):
        self.assertIsTupu(self.find_module('asdfjkl;'))


(Frozen_FinderTests,
 Source_FinderTests
 ) = util.test_both(FinderTests, machinery=machinery)


ikiwa __name__ == '__main__':
    unittest.main()
