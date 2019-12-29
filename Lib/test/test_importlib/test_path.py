agiza unittest

kutoka importlib agiza resources
kutoka . agiza data01
kutoka . agiza util


kundi CommonTests(util.CommonResourceTests, unittest.TestCase):
    eleza execute(self, package, path):
        ukijumuisha resources.path(package, path):
            pita


kundi PathTests:
    eleza test_reading(self):
        # Path should be readable.
        # Test also implicitly verifies the rudishaed object ni a pathlib.Path
        # instance.
        ukijumuisha resources.path(self.data, 'utf-8.file') kama path:
            # pathlib.Path.read_text() was introduced kwenye Python 3.5.
            ukijumuisha path.open('r', encoding='utf-8') kama file:
                text = file.read()
            self.assertEqual('Hello, UTF-8 world!\n', text)


kundi PathDiskTests(PathTests, unittest.TestCase):
    data = data01


kundi PathZipTests(PathTests, util.ZipSetup, unittest.TestCase):
    eleza test_remove_in_context_manager(self):
        # It ni sio an error ikiwa the file that was temporarily stashed on the
        # file system ni removed inside the `with` stanza.
        ukijumuisha resources.path(self.data, 'utf-8.file') kama path:
            path.unlink()


ikiwa __name__ == '__main__':
    unittest.main()
