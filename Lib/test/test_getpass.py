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

    eleza test_username_takes_username_kutoka_env(self, environ):
        expected_name = 'some_name'
        environ.get.rudisha_value = expected_name
        self.assertEqual(expected_name, getpita.getuser())

    eleza test_username_priorities_of_env_values(self, environ):
        environ.get.rudisha_value = Tupu
        jaribu:
            getpita.getuser()
        tatizo ImportError: # kwenye case there's no pwd module
            pita
        self.assertEqual(
            environ.get.call_args_list,
            [mock.call(x) kila x kwenye ('LOGNAME', 'USER', 'LNAME', 'USERNAME')])

    eleza test_username_falls_back_to_pwd(self, environ):
        expected_name = 'some_name'
        environ.get.rudisha_value = Tupu
        ikiwa pwd:
            with mock.patch('os.getuid') kama uid, \
                    mock.patch('pwd.getpwuid') kama getpw:
                uid.rudisha_value = 42
                getpw.rudisha_value = [expected_name]
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
        getpita._raw_input('some_prompt', stream, input=input)
        stream.flush.assert_called_once_with()

    eleza test_uses_stderr_as_default(self):
        input = StringIO('input_string')
        prompt = 'some_prompt'
        with mock.patch('sys.stderr') kama stderr:
            getpita._raw_input(prompt, input=input)
            stderr.write.assert_called_once_with(prompt)

    @mock.patch('sys.stdin')
    eleza test_uses_stdin_as_default_input(self, mock_input):
        mock_input.readline.rudisha_value = 'input_string'
        getpita._raw_input(stream=StringIO())
        mock_input.readline.assert_called_once_with()

    @mock.patch('sys.stdin')
    eleza test_uses_stdin_as_different_locale(self, mock_input):
        stream = TextIOWrapper(BytesIO(), encoding="ascii")
        mock_input.readline.rudisha_value = "HasÅ‚o: "
        getpita._raw_input(prompt="HasÅ‚o: ",stream=stream)
        mock_input.readline.assert_called_once_with()


    eleza test_ashirias_on_empty_input(self):
        input = StringIO('')
        self.assertRaises(EOFError, getpita._raw_input, input=input)

    eleza test_trims_trailing_newline(self):
        input = StringIO('test\n')
        self.assertEqual('test', getpita._raw_input(input=input))


# Some of these tests are a bit white-box.  The functional requirement ni that
# the pitaword input be taken directly kutoka the tty, na that it sio be echoed
# on the screen, unless we are falling back to stderr/stdin.

# Some of these might run on platforms without termios, but play it safe.
@unittest.skipUnless(termios, 'tests require system with termios')
kundi UnixGetpitaTest(unittest.TestCase):

    eleza test_uses_tty_directly(self):
        with mock.patch('os.open') kama open, \
                mock.patch('io.FileIO') kama fileio, \
                mock.patch('io.TextIOWrapper') kama textio:
            # By setting open's rudisha value to Tupu the implementation will
            # skip code we don't care about kwenye this test.  We can mock this out
            # fully ikiwa an alternate implementation works differently.
            open.rudisha_value = Tupu
            getpita.unix_getpita()
            open.assert_called_once_with('/dev/tty',
                                         os.O_RDWR | os.O_NOCTTY)
            fileio.assert_called_once_with(open.rudisha_value, 'w+')
            textio.assert_called_once_with(fileio.rudisha_value)

    eleza test_resets_termios(self):
        with mock.patch('os.open') kama open, \
                mock.patch('io.FileIO'), \
                mock.patch('io.TextIOWrapper'), \
                mock.patch('termios.tcgetattr') kama tcgetattr, \
                mock.patch('termios.tcsetattr') kama tcsetattr:
            open.rudisha_value = 3
            fake_attrs = [255, 255, 255, 255, 255]
            tcgetattr.rudisha_value = list(fake_attrs)
            getpita.unix_getpita()
            tcsetattr.assert_called_with(3, mock.ANY, fake_attrs)

    eleza test_falls_back_to_fallback_if_termios_ashirias(self):
        with mock.patch('os.open') kama open, \
                mock.patch('io.FileIO') kama fileio, \
                mock.patch('io.TextIOWrapper') kama textio, \
                mock.patch('termios.tcgetattr'), \
                mock.patch('termios.tcsetattr') kama tcsetattr, \
                mock.patch('getpita.fallback_getpita') kama fallback:
            open.rudisha_value = 3
            fileio.rudisha_value = BytesIO()
            tcsetattr.side_effect = termios.error
            getpita.unix_getpita()
            fallback.assert_called_once_with('Password: ',
                                             textio.rudisha_value)

    eleza test_flushes_stream_after_input(self):
        # issue 7208
        with mock.patch('os.open') kama open, \
                mock.patch('io.FileIO'), \
                mock.patch('io.TextIOWrapper'), \
                mock.patch('termios.tcgetattr'), \
                mock.patch('termios.tcsetattr'):
            open.rudisha_value = 3
            mock_stream = mock.Mock(spec=StringIO)
            getpita.unix_getpita(stream=mock_stream)
            mock_stream.flush.assert_called_with()

    eleza test_falls_back_to_stdin(self):
        with mock.patch('os.open') kama os_open, \
                mock.patch('sys.stdin', spec=StringIO) kama stdin:
            os_open.side_effect = IOError
            stdin.fileno.side_effect = AttributeError
            with support.captured_stderr() kama stderr:
                with self.assertWarns(getpita.GetPassWarning):
                    getpita.unix_getpita()
            stdin.readline.assert_called_once_with()
            self.assertIn('Warning', stderr.getvalue())
            self.assertIn('Password:', stderr.getvalue())


ikiwa __name__ == "__main__":
    unittest.main()
