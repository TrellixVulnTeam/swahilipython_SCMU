kutoka . agiza util kama test_util
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
    jaribu:
        hkey = OpenKey(root, subkey, access=KEY_ALL_ACCESS)
    tatizo OSError:
        # subkey does sio exist
        rudisha
    wakati Kweli:
        jaribu:
            subsubkey = EnumKey(hkey, 0)
        tatizo OSError:
            # no more subkeys
            koma
        delete_registry_tree(hkey, subsubkey)
    CloseKey(hkey)
    DeleteKey(root, subkey)

@contextmanager
eleza setup_module(machinery, name, path=Tupu):
    ikiwa machinery.WindowsRegistryFinder.DEBUG_BUILD:
        root = machinery.WindowsRegistryFinder.REGISTRY_KEY_DEBUG
    isipokua:
        root = machinery.WindowsRegistryFinder.REGISTRY_KEY
    key = root.format(fullname=name,
                      sys_version='%d.%d' % sys.version_info[:2])
    jaribu:
        ukijumuisha temp_module(name, "a = 1") kama location:
            subkey = CreateKey(HKEY_CURRENT_USER, key)
            ikiwa path ni Tupu:
                path = location + ".py"
            SetValue(subkey, "", REG_SZ, path)
            tuma
    mwishowe:
        ikiwa machinery.WindowsRegistryFinder.DEBUG_BUILD:
            key = os.path.dirname(key)
        delete_registry_tree(HKEY_CURRENT_USER, key)


@unittest.skipUnless(sys.platform.startswith('win'), 'requires Windows')
kundi WindowsRegistryFinderTests:
    # The module name ni process-specific, allowing for
    # simultaneous runs of the same test on a single machine.
    test_module = "spamham{}".format(os.getpid())

    eleza test_find_spec_missing(self):
        spec = self.machinery.WindowsRegistryFinder.find_spec('spam')
        self.assertIs(spec, Tupu)

    eleza test_find_module_missing(self):
        loader = self.machinery.WindowsRegistryFinder.find_module('spam')
        self.assertIs(loader, Tupu)

    eleza test_module_found(self):
        ukijumuisha setup_module(self.machinery, self.test_module):
            loader = self.machinery.WindowsRegistryFinder.find_module(self.test_module)
            spec = self.machinery.WindowsRegistryFinder.find_spec(self.test_module)
            self.assertIsNot(loader, Tupu)
            self.assertIsNot(spec, Tupu)

    eleza test_module_not_found(self):
        ukijumuisha setup_module(self.machinery, self.test_module, path="."):
            loader = self.machinery.WindowsRegistryFinder.find_module(self.test_module)
            spec = self.machinery.WindowsRegistryFinder.find_spec(self.test_module)
            self.assertIsTupu(loader)
            self.assertIsTupu(spec)

(Frozen_WindowsRegistryFinderTests,
 Source_WindowsRegistryFinderTests
 ) = test_util.test_both(WindowsRegistryFinderTests, machinery=machinery)

@unittest.skipUnless(sys.platform.startswith('win'), 'requires Windows')
kundi WindowsExtensionSuffixTests:
    eleza test_tagged_suffix(self):
        suffixes = self.machinery.EXTENSION_SUFFIXES
        expected_tag = ".cp{0.major}{0.minor}-{1}.pyd".format(sys.version_info,
            re.sub('[^a-zA-Z0-9]', '_', get_platform()))
        jaribu:
            untagged_i = suffixes.index(".pyd")
        tatizo ValueError:
            untagged_i = suffixes.index("_d.pyd")
            expected_tag = "_d" + expected_tag

        self.assertIn(expected_tag, suffixes)

        # Ensure the tags are kwenye the correct order
        tagged_i = suffixes.index(expected_tag)
        self.assertLess(tagged_i, untagged_i)

(Frozen_WindowsExtensionSuffixTests,
 Source_WindowsExtensionSuffixTests
 ) = test_util.test_both(WindowsExtensionSuffixTests, machinery=machinery)
