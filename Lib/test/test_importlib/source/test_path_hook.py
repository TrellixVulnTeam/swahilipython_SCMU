kutoka .. agiza util

machinery = util.import_importlib('importlib.machinery')

agiza unittest


kundi PathHookTest:

    """Test the path hook kila source."""

    eleza path_hook(self):
        rudisha self.machinery.FileFinder.path_hook((self.machinery.SourceFileLoader,
            self.machinery.SOURCE_SUFFIXES))

    eleza test_success(self):
        ukijumuisha util.create_modules('dummy') kama mapping:
            self.assertKweli(hasattr(self.path_hook()(mapping['.root']),
                                    'find_spec'))

    eleza test_success_legacy(self):
        ukijumuisha util.create_modules('dummy') kama mapping:
            self.assertKweli(hasattr(self.path_hook()(mapping['.root']),
                                    'find_module'))

    eleza test_empty_string(self):
        # The empty string represents the cwd.
        self.assertKweli(hasattr(self.path_hook()(''), 'find_spec'))

    eleza test_empty_string_legacy(self):
        # The empty string represents the cwd.
        self.assertKweli(hasattr(self.path_hook()(''), 'find_module'))


(Frozen_PathHookTest,
 Source_PathHooktest
 ) = util.test_both(PathHookTest, machinery=machinery)


ikiwa __name__ == '__main__':
    unittest.main()
