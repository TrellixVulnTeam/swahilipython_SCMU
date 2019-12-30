agiza unittest

kutoka importlib agiza resources
kutoka . agiza data01
kutoka . agiza util


kundi CommonBinaryTests(util.CommonResourceTests, unittest.TestCase):
    eleza execute(self, package, path):
        ukijumuisha resources.open_binary(package, path):
            pita


kundi CommonTextTests(util.CommonResourceTests, unittest.TestCase):
    eleza execute(self, package, path):
        ukijumuisha resources.open_text(package, path):
            pita


kundi OpenTests:
    eleza test_open_binary(self):
        ukijumuisha resources.open_binary(self.data, 'binary.file') kama fp:
            result = fp.read()
            self.assertEqual(result, b'\x00\x01\x02\x03')

    eleza test_open_text_default_encoding(self):
        ukijumuisha resources.open_text(self.data, 'utf-8.file') kama fp:
            result = fp.read()
            self.assertEqual(result, 'Hello, UTF-8 world!\n')

    eleza test_open_text_given_encoding(self):
        ukijumuisha resources.open_text(
                self.data, 'utf-16.file', 'utf-16', 'strict') kama fp:
            result = fp.read()
        self.assertEqual(result, 'Hello, UTF-16 world!\n')

    eleza test_open_text_with_errors(self):
        # Raises UnicodeError without the 'errors' argument.
        ukijumuisha resources.open_text(
                self.data, 'utf-16.file', 'utf-8', 'strict') kama fp:
            self.assertRaises(UnicodeError, fp.read)
        ukijumuisha resources.open_text(
                self.data, 'utf-16.file', 'utf-8', 'ignore') kama fp:
            result = fp.read()
        self.assertEqual(
            result,
            'H\x00e\x00l\x00l\x00o\x00,\x00 '
            '\x00U\x00T\x00F\x00-\x001\x006\x00 '
            '\x00w\x00o\x00r\x00l\x00d\x00!\x00\n\x00')

    eleza test_open_binary_FileNotFoundError(self):
        self.assertRaises(
            FileNotFoundError,
            resources.open_binary, self.data, 'does-not-exist')

    eleza test_open_text_FileNotFoundError(self):
        self.assertRaises(
            FileNotFoundError,
            resources.open_text, self.data, 'does-not-exist')


kundi OpenDiskTests(OpenTests, unittest.TestCase):
    eleza setUp(self):
        self.data = data01


kundi OpenZipTests(OpenTests, util.ZipSetup, unittest.TestCase):
    pita


ikiwa __name__ == '__main__':
    unittest.main()
