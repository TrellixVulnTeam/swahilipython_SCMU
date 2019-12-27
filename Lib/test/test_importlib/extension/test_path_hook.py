kutoka .. agiza util

machinery = util.import_importlib('importlib.machinery')

agiza unittest


kundi PathHookTests:

    """Test the path hook for extension modules."""
    # XXX Should it only succeed for pre-existing directories?
    # XXX Should it only work for directories containing an extension module?

    eleza hook(self, entry):
        rudisha self.machinery.FileFinder.path_hook(
                (self.machinery.ExtensionFileLoader,
                 self.machinery.EXTENSION_SUFFIXES))(entry)

    eleza test_success(self):
        # Path hook should handle a directory where a known extension module
        # exists.
        self.assertTrue(hasattr(self.hook(util.EXTENSIONS.path), 'find_module'))


(Frozen_PathHooksTests,
 Source_PathHooksTests
 ) = util.test_both(PathHookTests, machinery=machinery)


ikiwa __name__ == '__main__':
    unittest.main()
