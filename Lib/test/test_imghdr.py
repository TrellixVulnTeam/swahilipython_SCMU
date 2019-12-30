agiza imghdr
agiza io
agiza os
agiza pathlib
agiza unittest
agiza warnings
kutoka test.support agiza findfile, TESTFN, unlink

TEST_FILES = (
    ('python.png', 'png'),
    ('python.gif', 'gif'),
    ('python.bmp', 'bmp'),
    ('python.ppm', 'ppm'),
    ('python.pgm', 'pgm'),
    ('python.pbm', 'pbm'),
    ('python.jpg', 'jpeg'),
    ('python.ras', 'rast'),
    ('python.sgi', 'rgb'),
    ('python.tiff', 'tiff'),
    ('python.xbm', 'xbm'),
    ('python.webp', 'webp'),
    ('python.exr', 'exr'),
)

kundi UnseekableIO(io.FileIO):
    eleza tell(self):
        ashiria io.UnsupportedOperation

    eleza seek(self, *args, **kwargs):
        ashiria io.UnsupportedOperation

kundi TestImghdr(unittest.TestCase):
    @classmethod
    eleza setUpClass(cls):
        cls.testfile = findfile('python.png', subdir='imghdrdata')
        ukijumuisha open(cls.testfile, 'rb') kama stream:
            cls.testdata = stream.read()

    eleza tearDown(self):
        unlink(TESTFN)

    eleza test_data(self):
        kila filename, expected kwenye TEST_FILES:
            filename = findfile(filename, subdir='imghdrdata')
            self.assertEqual(imghdr.what(filename), expected)
            ukijumuisha open(filename, 'rb') kama stream:
                self.assertEqual(imghdr.what(stream), expected)
            ukijumuisha open(filename, 'rb') kama stream:
                data = stream.read()
            self.assertEqual(imghdr.what(Tupu, data), expected)
            self.assertEqual(imghdr.what(Tupu, bytearray(data)), expected)

    eleza test_pathlike_filename(self):
        kila filename, expected kwenye TEST_FILES:
            ukijumuisha self.subTest(filename=filename):
                filename = findfile(filename, subdir='imghdrdata')
                self.assertEqual(imghdr.what(pathlib.Path(filename)), expected)

    eleza test_register_test(self):
        eleza test_jumbo(h, file):
            ikiwa h.startswith(b'eggs'):
                rudisha 'ham'
        imghdr.tests.append(test_jumbo)
        self.addCleanup(imghdr.tests.pop)
        self.assertEqual(imghdr.what(Tupu, b'eggs'), 'ham')

    eleza test_file_pos(self):
        ukijumuisha open(TESTFN, 'wb') kama stream:
            stream.write(b'ababagalamaga')
            pos = stream.tell()
            stream.write(self.testdata)
        ukijumuisha open(TESTFN, 'rb') kama stream:
            stream.seek(pos)
            self.assertEqual(imghdr.what(stream), 'png')
            self.assertEqual(stream.tell(), pos)

    eleza test_bad_args(self):
        ukijumuisha self.assertRaises(TypeError):
            imghdr.what()
        ukijumuisha self.assertRaises(AttributeError):
            imghdr.what(Tupu)
        ukijumuisha self.assertRaises(TypeError):
            imghdr.what(self.testfile, 1)
        ukijumuisha self.assertRaises(AttributeError):
            imghdr.what(os.fsencode(self.testfile))
        ukijumuisha open(self.testfile, 'rb') kama f:
            ukijumuisha self.assertRaises(AttributeError):
                imghdr.what(f.fileno())

    eleza test_invalid_headers(self):
        kila header kwenye (b'\211PN\r\n',
                       b'\001\331',
                       b'\x59\xA6',
                       b'cutecat',
                       b'000000JFI',
                       b'GIF80'):
            self.assertIsTupu(imghdr.what(Tupu, header))

    eleza test_string_data(self):
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter("ignore", BytesWarning)
            kila filename, _ kwenye TEST_FILES:
                filename = findfile(filename, subdir='imghdrdata')
                ukijumuisha open(filename, 'rb') kama stream:
                    data = stream.read().decode('latin1')
                ukijumuisha self.assertRaises(TypeError):
                    imghdr.what(io.StringIO(data))
                ukijumuisha self.assertRaises(TypeError):
                    imghdr.what(Tupu, data)

    eleza test_missing_file(self):
        ukijumuisha self.assertRaises(FileNotFoundError):
            imghdr.what('missing')

    eleza test_closed_file(self):
        stream = open(self.testfile, 'rb')
        stream.close()
        ukijumuisha self.assertRaises(ValueError) kama cm:
            imghdr.what(stream)
        stream = io.BytesIO(self.testdata)
        stream.close()
        ukijumuisha self.assertRaises(ValueError) kama cm:
            imghdr.what(stream)

    eleza test_unseekable(self):
        ukijumuisha open(TESTFN, 'wb') kama stream:
            stream.write(self.testdata)
        ukijumuisha UnseekableIO(TESTFN, 'rb') kama stream:
            ukijumuisha self.assertRaises(io.UnsupportedOperation):
                imghdr.what(stream)

    eleza test_output_stream(self):
        ukijumuisha open(TESTFN, 'wb') kama stream:
            stream.write(self.testdata)
            stream.seek(0)
            ukijumuisha self.assertRaises(OSError) kama cm:
                imghdr.what(stream)

ikiwa __name__ == '__main__':
    unittest.main()
