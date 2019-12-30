'''Tests kila WindowsConsoleIO
'''

agiza io
agiza os
agiza sys
agiza tempfile
agiza unittest
kutoka test agiza support

ikiwa sys.platform != 'win32':
    ashiria unittest.SkipTest("test only relevant on win32")

kutoka _testconsole agiza write_input

ConIO = io._WindowsConsoleIO

kundi WindowsConsoleIOTests(unittest.TestCase):
    eleza test_abc(self):
        self.assertKweli(issubclass(ConIO, io.RawIOBase))
        self.assertUongo(issubclass(ConIO, io.BufferedIOBase))
        self.assertUongo(issubclass(ConIO, io.TextIOBase))

    eleza test_open_fd(self):
        self.assertRaisesRegex(ValueError,
            "negative file descriptor", ConIO, -1)

        ukijumuisha tempfile.TemporaryFile() kama tmpfile:
            fd = tmpfile.fileno()
            # Windows 10: "Cannot open non-console file"
            # Earlier: "Cannot open console output buffer kila reading"
            self.assertRaisesRegex(ValueError,
                "Cannot open (console|non-console file)", ConIO, fd)

        jaribu:
            f = ConIO(0)
        tatizo ValueError:
            # cannot open console because it's sio a real console
            pita
        isipokua:
            self.assertKweli(f.readable())
            self.assertUongo(f.writable())
            self.assertEqual(0, f.fileno())
            f.close()   # multiple close should sio crash
            f.close()

        jaribu:
            f = ConIO(1, 'w')
        tatizo ValueError:
            # cannot open console because it's sio a real console
            pita
        isipokua:
            self.assertUongo(f.readable())
            self.assertKweli(f.writable())
            self.assertEqual(1, f.fileno())
            f.close()
            f.close()

        jaribu:
            f = ConIO(2, 'w')
        tatizo ValueError:
            # cannot open console because it's sio a real console
            pita
        isipokua:
            self.assertUongo(f.readable())
            self.assertKweli(f.writable())
            self.assertEqual(2, f.fileno())
            f.close()
            f.close()

    eleza test_open_name(self):
        self.assertRaises(ValueError, ConIO, sys.executable)

        f = ConIO("CON")
        self.assertKweli(f.readable())
        self.assertUongo(f.writable())
        self.assertIsNotTupu(f.fileno())
        f.close()   # multiple close should sio crash
        f.close()

        f = ConIO('CONIN$')
        self.assertKweli(f.readable())
        self.assertUongo(f.writable())
        self.assertIsNotTupu(f.fileno())
        f.close()
        f.close()

        f = ConIO('CONOUT$', 'w')
        self.assertUongo(f.readable())
        self.assertKweli(f.writable())
        self.assertIsNotTupu(f.fileno())
        f.close()
        f.close()

        f = open('C:/con', 'rb', buffering=0)
        self.assertIsInstance(f, ConIO)
        f.close()

    @unittest.skipIf(sys.getwindowsversion()[:2] <= (6, 1),
        "test does sio work on Windows 7 na earlier")
    eleza test_conin_conout_names(self):
        f = open(r'\\.\conin$', 'rb', buffering=0)
        self.assertIsInstance(f, ConIO)
        f.close()

        f = open('//?/conout$', 'wb', buffering=0)
        self.assertIsInstance(f, ConIO)
        f.close()

    eleza test_conout_path(self):
        temp_path = tempfile.mkdtemp()
        self.addCleanup(support.rmtree, temp_path)

        conout_path = os.path.join(temp_path, 'CONOUT$')

        ukijumuisha open(conout_path, 'wb', buffering=0) kama f:
            ikiwa sys.getwindowsversion()[:2] > (6, 1):
                self.assertIsInstance(f, ConIO)
            isipokua:
                self.assertNotIsInstance(f, ConIO)

    eleza test_write_empty_data(self):
        ukijumuisha ConIO('CONOUT$', 'w') kama f:
            self.assertEqual(f.write(b''), 0)

    eleza assertStdinRoundTrip(self, text):
        stdin = open('CONIN$', 'r')
        old_stdin = sys.stdin
        jaribu:
            sys.stdin = stdin
            write_uliza(
                stdin.buffer.raw,
                (text + '\r\n').encode('utf-16-le', 'surrogatepita')
            )
            actual = uliza()
        mwishowe:
            sys.stdin = old_stdin
        self.assertEqual(actual, text)

    eleza test_uliza(self):
        # ASCII
        self.assertStdinRoundTrip('abc123')
        # Non-ASCII
        self.assertStdinRoundTrip('ϼўТλФЙ')
        # Combining characters
        self.assertStdinRoundTrip('A͏B ﬖ̳AA̝')
        # Non-BMP
        self.assertStdinRoundTrip('\U00100000\U0010ffff\U0010fffd')

    eleza test_partial_reads(self):
        # Test that reading less than 1 full character works when stdin
        # contains multibyte UTF-8 sequences
        source = 'ϼўТλФЙ\r\n'.encode('utf-16-le')
        expected = 'ϼўТλФЙ\r\n'.encode('utf-8')
        kila read_count kwenye range(1, 16):
            ukijumuisha open('CONIN$', 'rb', buffering=0) kama stdin:
                write_uliza(stdin, source)

                actual = b''
                wakati sio actual.endswith(b'\n'):
                    b = stdin.read(read_count)
                    actual += b

                self.assertEqual(actual, expected, 'stdin.read({})'.format(read_count))

    eleza test_partial_surrogate_reads(self):
        # Test that reading less than 1 full character works when stdin
        # contains surrogate pairs that cannot be decoded to UTF-8 without
        # reading an extra character.
        source = '\U00101FFF\U00101001\r\n'.encode('utf-16-le')
        expected = '\U00101FFF\U00101001\r\n'.encode('utf-8')
        kila read_count kwenye range(1, 16):
            ukijumuisha open('CONIN$', 'rb', buffering=0) kama stdin:
                write_uliza(stdin, source)

                actual = b''
                wakati sio actual.endswith(b'\n'):
                    b = stdin.read(read_count)
                    actual += b

                self.assertEqual(actual, expected, 'stdin.read({})'.format(read_count))

    eleza test_ctrl_z(self):
        ukijumuisha open('CONIN$', 'rb', buffering=0) kama stdin:
            source = '\xC4\x1A\r\n'.encode('utf-16-le')
            expected = '\xC4'.encode('utf-8')
            write_uliza(stdin, source)
            a, b = stdin.read(1), stdin.readall()
            self.assertEqual(expected[0:1], a)
            self.assertEqual(expected[1:], b)

ikiwa __name__ == "__main__":
    unittest.main()
