agiza unittest

kutoka importlib agiza resources
kutoka . agiza data01
kutoka . agiza util


kundi CommonTests(util.CommonResourceTests, unittest.TestCase):
    eleza execute(self, package, path):
        with resources.path(package, path):
            pass


kundi PathTests:
    eleza test_reading(self):
        # Path should be readable.
        # Test also implicitly verifies the returned object is a pathlib.Path
        # instance.
        with resources.path(self.data, 'utf-8.file') as path:
            # pathlib.Path.read_text() was introduced in Python 3.5.
            with path.open('r', encoding='utf-8') as file:
                text = file.read()
            self.assertEqual('Hello, UTF-8 world!\n', text)


kundi PathDiskTests(PathTests, unittest.TestCase):
    data = data01


kundi PathZipTests(PathTests, util.ZipSetup, unittest.TestCase):
    eleza test_remove_in_context_manager(self):
        # It is not an error ikiwa the file that was temporarily stashed on the
        # file system is removed inside the `with` stanza.
        with resources.path(self.data, 'utf-8.file') as path:
            path.unlink()


ikiwa __name__ == '__main__':
    unittest.main()
