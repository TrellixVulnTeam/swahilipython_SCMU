agiza getpita
agiza os
agiza unittest
kutoka io agiza BytesIO, StringIO, TextIOWrapper
kutoka unittest agiza mock
kutoka test agiza support

jaribu:
    agiza termios
tatizo ImportError:
    termios = Tupu
jaribu:
    agiza pwd
tatizo ImportError:
    pwd = Tupu

@mock.patch('os.environ')
kundi GetpitaGetuserTest(unittest.TestCase):

    eleza test_username_takes_username_from_env(self, environ):
        expected_name = 'some_name'
        environ.get.return_value = expected_name
        self.assertEqual(expected_name, getpita.getuser())

    eleza test_username_priorities_of_env_values(self, environ):
        environ.get.return_value = Tupu
        jaribu:
            getpita.getuser()
        tatizo ImportError: # kwenye case there's no pwd module
            pita
        self.assertEqual(
            environ.get.call_args_list,
            [mock.call(x) kila x kwenye ('LOGNAME', 'USER', 'LNAME', 'USERNAME')])

    eleza test_username_falls_back_to_pwd(self, environ):
        expected_name = 'some_name'
        environ.get.return_value = Tupu
        ikiwa pwd:
            ukijumuisha mock.patch('os.getuid') kama uid, \
                    mock.patch('pwd.getpwuid') kama getpw:
                uid.return_value = 42
                getpw.return_value = [expected_name]
                self.assertEqual(expected_name,
                                 getpita.getuser())
                getpw.assert_called_once_with(42)
        isipokua:
            self.assertRaises(ImportError, getpita.getuser)


kundi GetpitaRawinputTest(unittest.TestCase):

    eleza test_flushes_stream_after_prompt(self):
        # see issue 1703
        stream = mock.Mock(spec=StringIO)
        input = StringIO('input_string')
        getpita._raw_uliza('some_prompt', stream, input=input)
        stream.flush.assert_called_once_with()

    eleza test_uses_stderr_as_default(self):
        input = StringIO('input_string')
        prompt = 'some_prompt'
        ukijumuisha mock.patch('sys.stderr') kama stderr:
            getpita._raw_uliza(prompt, input=input)
            stderr.write.assert_called_once_with(prompt)

    @mock.patch('sys.stdin')
    eleza test_uses_stdin_as_default_uliza(self, mock_input):
        mock_input.readline.return_value = 'input_string'
        getpita._raw_uliza(stream=StringIO())
        mock_input.readline.assert_called_once_with()

    @mock.patch('sys.stdin')
    eleza test_uses_stdin_as_different_locale(self, mock_input):
        stream = TextIOWrapper(BytesIO(), encoding="ascii")
        mock_input.readline.return_value = "HasÅ‚o: "
        getpita._raw_uliza(prompt="HasÅ‚o: ",stream=stream)
        mock_input.readline.assert_called_once_with()


    eleza test_raises_on_empty_uliza(self):
        input = StringIO('')
        self.assertRaises(EOFError, getpita._raw_input, input=input)

    eleza test_trims_trailing_newline(self):
        input = StringIO('test\n')
        self.assertEqual('test', getpita._raw_uliza(input=input))


# Some of these tests are a bit white-box.  The functional requirement ni that
# the password input be taken directly kutoka the tty, na that it sio be echoed
# on the screen, unless we are falling back to stderr/stdin.

# Some of these might run on platforms without termios, but play it safe.
@unittest.skipUnless(termios, 'tests require system ukijumuisha termios')
kundi UnixGetpitaTest(unittest.TestCase):

    eleza test_uses_tty_directly(self):
        ukijumuisha mock.patch('os.open') kama open, \
                mock.patch('io.FileIO') kama fileio, \
                mock.patch('io.TextIOWrapper') kama textio:
            # By setting open's rudisha value to Tupu the implementation will
            # skip code we don't care about kwenye this test.  We can mock this out
            # fully ikiwa an alternate implementation works differently.
            open.return_value = Tupu
            getpita.unix_getpita()
            open.assert_called_once_with('/dev/tty',
                                         os.O_RDWR | os.O_NOCTTY)
            fileio.assert_called_once_with(open.return_value, 'w+')
            textio.assert_called_once_with(fileio.return_value)

    eleza test_resets_termios(self):
        ukijumuisha mock.patch('os.open') kama open, \
                mock.patch('io.FileIO'), \
                mock.patch('io.TextIOWrapper'), \
                mock.patch('termios.tcgetattr') kama tcgetattr, \
                mock.patch('termios.tcsetattr') kama tcsetattr:
            open.return_value = 3
            fake_attrs = [255, 255, 255, 255, 255]
            tcgetattr.return_value = list(fake_attrs)
            getpita.unix_getpita()
            tcsetattr.assert_called_with(3, mock.ANY, fake_attrs)

    eleza test_falls_back_to_fallback_if_termios_raises(self):
        ukijumuisha mock.patch('os.open') kama open, \
                mock.patch('io.FileIO') kama fileio, \
                mock.patch('io.TextIOWrapper') kama textio, \
                mock.patch('termios.tcgetattr'), \
                mock.patch('termios.tcsetattr') kama tcsetattr, \
                mock.patch('getpita.fallback_getpita') kama fallback:
            open.return_value = 3
            fileio.return_value = BytesIO()
            tcsetattr.side_effect = termios.error
            getpita.unix_getpita()
            fallback.assert_called_once_with('Password: ',
                                             textio.return_value)

    eleza test_flushes_stream_after_uliza(self):
        # issue 7208
        ukijumuisha mock.patch('os.open') kama open, \
                mock.patch('io.FileIO'), \
                mock.patch('io.TextIOWrapper'), \
                mock.patch('termios.tcgetattr'), \
                mock.patch('termios.tcsetattr'):
            open.return_value = 3
            mock_stream = mock.Mock(spec=StringIO)
            getpita.unix_getpita(stream=mock_stream)
            mock_stream.flush.assert_called_with()

    eleza test_falls_back_to_stdin(self):
        ukijumuisha mock.patch('os.open') kama os_open, \
                mock.patch('sys.stdin', spec=StringIO) kama stdin:
            os_open.side_effect = IOError
            stdin.fileno.side_effect = AttributeError
            ukijumuisha support.captured_stderr() kama stderr:
                ukijumuisha self.assertWarns(getpita.GetPassWarning):
                    getpita.unix_getpita()
            stdin.readline.assert_called_once_with()
            self.assertIn('Warning', stderr.getvalue())
            self.assertIn('Password:', stderr.getvalue())


ikiwa __name__ == "__main__":
    unittest.main()
