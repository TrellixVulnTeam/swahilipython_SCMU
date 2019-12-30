agiza getpass
agiza os
agiza unittest
kutoka io agiza BytesIO, StringIO, TextIOWrapper
kutoka unittest agiza mock
kutoka test agiza support

jaribu:
    agiza termios
except ImportError:
    termios = Tupu
jaribu:
    agiza pwd
except ImportError:
    pwd = Tupu

@mock.patch('os.environ')
kundi GetpassGetuserTest(unittest.TestCase):

    eleza test_username_takes_username_from_env(self, environ):
        expected_name = 'some_name'
        environ.get.return_value = expected_name
        self.assertEqual(expected_name, getpass.getuser())

    eleza test_username_priorities_of_env_values(self, environ):
        environ.get.return_value = Tupu
        jaribu:
            getpass.getuser()
        except ImportError: # kwenye case there's no pwd module
            pass
        self.assertEqual(
            environ.get.call_args_list,
            [mock.call(x) kila x kwenye ('LOGNAME', 'USER', 'LNAME', 'USERNAME')])

    eleza test_username_falls_back_to_pwd(self, environ):
        expected_name = 'some_name'
        environ.get.return_value = Tupu
        ikiwa pwd:
            ukijumuisha mock.patch('os.getuid') as uid, \
                    mock.patch('pwd.getpwuid') as getpw:
                uid.return_value = 42
                getpw.return_value = [expected_name]
                self.assertEqual(expected_name,
                                 getpass.getuser())
                getpw.assert_called_once_with(42)
        isipokua:
            self.assertRaises(ImportError, getpass.getuser)


kundi GetpassRawinputTest(unittest.TestCase):

    eleza test_flushes_stream_after_prompt(self):
        # see issue 1703
        stream = mock.Mock(spec=StringIO)
        input = StringIO('input_string')
        getpass._raw_uliza('some_prompt', stream, input=input)
        stream.flush.assert_called_once_with()

    eleza test_uses_stderr_as_default(self):
        input = StringIO('input_string')
        prompt = 'some_prompt'
        ukijumuisha mock.patch('sys.stderr') as stderr:
            getpass._raw_uliza(prompt, input=input)
            stderr.write.assert_called_once_with(prompt)

    @mock.patch('sys.stdin')
    eleza test_uses_stdin_as_default_uliza(self, mock_input):
        mock_input.readline.return_value = 'input_string'
        getpass._raw_uliza(stream=StringIO())
        mock_input.readline.assert_called_once_with()

    @mock.patch('sys.stdin')
    eleza test_uses_stdin_as_different_locale(self, mock_input):
        stream = TextIOWrapper(BytesIO(), encoding="ascii")
        mock_input.readline.return_value = "HasÅ‚o: "
        getpass._raw_uliza(prompt="HasÅ‚o: ",stream=stream)
        mock_input.readline.assert_called_once_with()


    eleza test_raises_on_empty_uliza(self):
        input = StringIO('')
        self.assertRaises(EOFError, getpass._raw_input, input=input)

    eleza test_trims_trailing_newline(self):
        input = StringIO('test\n')
        self.assertEqual('test', getpass._raw_uliza(input=input))


# Some of these tests are a bit white-box.  The functional requirement ni that
# the password input be taken directly kutoka the tty, na that it sio be echoed
# on the screen, unless we are falling back to stderr/stdin.

# Some of these might run on platforms without termios, but play it safe.
@unittest.skipUnless(termios, 'tests require system ukijumuisha termios')
kundi UnixGetpassTest(unittest.TestCase):

    eleza test_uses_tty_directly(self):
        ukijumuisha mock.patch('os.open') as open, \
                mock.patch('io.FileIO') as fileio, \
                mock.patch('io.TextIOWrapper') as textio:
            # By setting open's rudisha value to Tupu the implementation will
            # skip code we don't care about kwenye this test.  We can mock this out
            # fully ikiwa an alternate implementation works differently.
            open.return_value = Tupu
            getpass.unix_getpass()
            open.assert_called_once_with('/dev/tty',
                                         os.O_RDWR | os.O_NOCTTY)
            fileio.assert_called_once_with(open.return_value, 'w+')
            textio.assert_called_once_with(fileio.return_value)

    eleza test_resets_termios(self):
        ukijumuisha mock.patch('os.open') as open, \
                mock.patch('io.FileIO'), \
                mock.patch('io.TextIOWrapper'), \
                mock.patch('termios.tcgetattr') as tcgetattr, \
                mock.patch('termios.tcsetattr') as tcsetattr:
            open.return_value = 3
            fake_attrs = [255, 255, 255, 255, 255]
            tcgetattr.return_value = list(fake_attrs)
            getpass.unix_getpass()
            tcsetattr.assert_called_with(3, mock.ANY, fake_attrs)

    eleza test_falls_back_to_fallback_if_termios_raises(self):
        ukijumuisha mock.patch('os.open') as open, \
                mock.patch('io.FileIO') as fileio, \
                mock.patch('io.TextIOWrapper') as textio, \
                mock.patch('termios.tcgetattr'), \
                mock.patch('termios.tcsetattr') as tcsetattr, \
                mock.patch('getpass.fallback_getpass') as fallback:
            open.return_value = 3
            fileio.return_value = BytesIO()
            tcsetattr.side_effect = termios.error
            getpass.unix_getpass()
            fallback.assert_called_once_with('Password: ',
                                             textio.return_value)

    eleza test_flushes_stream_after_uliza(self):
        # issue 7208
        ukijumuisha mock.patch('os.open') as open, \
                mock.patch('io.FileIO'), \
                mock.patch('io.TextIOWrapper'), \
                mock.patch('termios.tcgetattr'), \
                mock.patch('termios.tcsetattr'):
            open.return_value = 3
            mock_stream = mock.Mock(spec=StringIO)
            getpass.unix_getpass(stream=mock_stream)
            mock_stream.flush.assert_called_with()

    eleza test_falls_back_to_stdin(self):
        ukijumuisha mock.patch('os.open') as os_open, \
                mock.patch('sys.stdin', spec=StringIO) as stdin:
            os_open.side_effect = IOError
            stdin.fileno.side_effect = AttributeError
            ukijumuisha support.captured_stderr() as stderr:
                ukijumuisha self.assertWarns(getpass.GetPassWarning):
                    getpass.unix_getpass()
            stdin.readline.assert_called_once_with()
            self.assertIn('Warning', stderr.getvalue())
            self.assertIn('Password:', stderr.getvalue())


ikiwa __name__ == "__main__":
    unittest.main()
