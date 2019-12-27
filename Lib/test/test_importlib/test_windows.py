kutoka . agiza util as test_util
machinery = test_util.import_importlib('importlib.machinery')

agiza os
agiza re
agiza sys
agiza unittest
kutoka test agiza support
kutoka distutils.util agiza get_platform
kutoka contextlib agiza contextmanager
kutoka .util agiza temp_module

support.import_module('winreg', required_on=['win'])
kutoka winreg agiza (
    CreateKey, HKEY_CURRENT_USER,
    SetValue, REG_SZ, KEY_ALL_ACCESS,
    EnumKey, CloseKey, DeleteKey, OpenKey
)

eleza delete_registry_tree(root, subkey):
    try:
        hkey = OpenKey(root, subkey, access=KEY_ALL_ACCESS)
    except OSError:
        # subkey does not exist
        return
    while True:
        try:
            subsubkey = EnumKey(hkey, 0)
        except OSError:
            # no more subkeys
            break
        delete_registry_tree(hkey, subsubkey)
    CloseKey(hkey)
    DeleteKey(root, subkey)

@contextmanager
eleza setup_module(machinery, name, path=None):
    ikiwa machinery.WindowsRegistryFinder.DEBUG_BUILD:
        root = machinery.WindowsRegistryFinder.REGISTRY_KEY_DEBUG
    else:
        root = machinery.WindowsRegistryFinder.REGISTRY_KEY
    key = root.format(fullname=name,
                      sys_version='%d.%d' % sys.version_info[:2])
    try:
        with temp_module(name, "a = 1") as location:
            subkey = CreateKey(HKEY_CURRENT_USER, key)
            ikiwa path is None:
                path = location + ".py"
            SetValue(subkey, "", REG_SZ, path)
            yield
    finally:
        ikiwa machinery.WindowsRegistryFinder.DEBUG_BUILD:
            key = os.path.dirname(key)
        delete_registry_tree(HKEY_CURRENT_USER, key)


@unittest.skipUnless(sys.platform.startswith('win'), 'requires Windows')
kundi WindowsRegistryFinderTests:
    # The module name is process-specific, allowing for
    # simultaneous runs of the same test on a single machine.
    test_module = "spamham{}".format(os.getpid())

    eleza test_find_spec_missing(self):
        spec = self.machinery.WindowsRegistryFinder.find_spec('spam')
        self.assertIs(spec, None)

    eleza test_find_module_missing(self):
        loader = self.machinery.WindowsRegistryFinder.find_module('spam')
        self.assertIs(loader, None)

    eleza test_module_found(self):
        with setup_module(self.machinery, self.test_module):
            loader = self.machinery.WindowsRegistryFinder.find_module(self.test_module)
            spec = self.machinery.WindowsRegistryFinder.find_spec(self.test_module)
            self.assertIsNot(loader, None)
            self.assertIsNot(spec, None)

    eleza test_module_not_found(self):
        with setup_module(self.machinery, self.test_module, path="."):
            loader = self.machinery.WindowsRegistryFinder.find_module(self.test_module)
            spec = self.machinery.WindowsRegistryFinder.find_spec(self.test_module)
            self.assertIsNone(loader)
            self.assertIsNone(spec)

(Frozen_WindowsRegistryFinderTests,
 Source_WindowsRegistryFinderTests
 ) = test_util.test_both(WindowsRegistryFinderTests, machinery=machinery)

@unittest.skipUnless(sys.platform.startswith('win'), 'requires Windows')
kundi WindowsExtensionSuffixTests:
    eleza test_tagged_suffix(self):
        suffixes = self.machinery.EXTENSION_SUFFIXES
        expected_tag = ".cp{0.major}{0.minor}-{1}.pyd".format(sys.version_info,
            re.sub('[^a-zA-Z0-9]', '_', get_platform()))
        try:
            untagged_i = suffixes.index(".pyd")
        except ValueError:
            untagged_i = suffixes.index("_d.pyd")
            expected_tag = "_d" + expected_tag

        self.assertIn(expected_tag, suffixes)

        # Ensure the tags are in the correct order
        tagged_i = suffixes.index(expected_tag)
        self.assertLess(tagged_i, untagged_i)

(Frozen_WindowsExtensionSuffixTests,
 Source_WindowsExtensionSuffixTests
 ) = test_util.test_both(WindowsExtensionSuffixTests, machinery=machinery)
