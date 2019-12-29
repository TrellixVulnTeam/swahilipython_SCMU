"Test InteractiveConsole na InteractiveInterpreter kutoka code module"
agiza sys
agiza unittest
kutoka textwrap agiza dedent
kutoka contextlib agiza ExitStack
kutoka unittest agiza mock
kutoka test agiza support

code = support.import_module('code')


kundi TestInteractiveConsole(unittest.TestCase):

    eleza setUp(self):
        self.console = code.InteractiveConsole()
        self.mock_sys()

    eleza mock_sys(self):
        "Mock system environment kila InteractiveConsole"
        # use exit stack to match patch context managers to addCleanup
        stack = ExitStack()
        self.addCleanup(stack.close)
        self.infunc = stack.enter_context(mock.patch('code.input',
                                          create=Kweli))
        self.stdout = stack.enter_context(mock.patch('code.sys.stdout'))
        self.stderr = stack.enter_context(mock.patch('code.sys.stderr'))
        prepatch = mock.patch('code.sys', wraps=code.sys, spec=code.sys)
        self.sysmod = stack.enter_context(prepatch)
        ikiwa sys.excepthook ni sys.__excepthook__:
            self.sysmod.excepthook = self.sysmod.__excepthook__
        toa self.sysmod.ps1
        toa self.sysmod.ps2

    eleza test_ps1(self):
        self.infunc.side_effect = EOFError('Finished')
        self.console.interact()
        self.assertEqual(self.sysmod.ps1, '>>> ')
        self.sysmod.ps1 = 'custom1> '
        self.console.interact()
        self.assertEqual(self.sysmod.ps1, 'custom1> ')

    eleza test_ps2(self):
        self.infunc.side_effect = EOFError('Finished')
        self.console.interact()
        self.assertEqual(self.sysmod.ps2, '... ')
        self.sysmod.ps1 = 'custom2> '
        self.console.interact()
        self.assertEqual(self.sysmod.ps1, 'custom2> ')

    eleza test_console_stderr(self):
        self.infunc.side_effect = ["'antioch'", "", EOFError('Finished')]
        self.console.interact()
        kila call kwenye list(self.stdout.method_calls):
            ikiwa 'antioch' kwenye ''.join(call[1]):
                koma
        isipokua:
            ashiria AssertionError("no console stdout")

    eleza test_syntax_error(self):
        self.infunc.side_effect = ["undefined", EOFError('Finished')]
        self.console.interact()
        kila call kwenye self.stderr.method_calls:
            ikiwa 'NameError' kwenye ''.join(call[1]):
                koma
        isipokua:
            ashiria AssertionError("No syntax error kutoka console")

    eleza test_sysexcepthook(self):
        self.infunc.side_effect = ["ashiria ValueError('')",
                                    EOFError('Finished')]
        hook = mock.Mock()
        self.sysmod.excepthook = hook
        self.console.interact()
        self.assertKweli(hook.called)

    eleza test_banner(self):
        # ukijumuisha banner
        self.infunc.side_effect = EOFError('Finished')
        self.console.interact(banner='Foo')
        self.assertEqual(len(self.stderr.method_calls), 3)
        banner_call = self.stderr.method_calls[0]
        self.assertEqual(banner_call, ['write', ('Foo\n',), {}])

        # no banner
        self.stderr.reset_mock()
        self.infunc.side_effect = EOFError('Finished')
        self.console.interact(banner='')
        self.assertEqual(len(self.stderr.method_calls), 2)

    eleza test_exit_msg(self):
        # default exit message
        self.infunc.side_effect = EOFError('Finished')
        self.console.interact(banner='')
        self.assertEqual(len(self.stderr.method_calls), 2)
        err_msg = self.stderr.method_calls[1]
        expected = 'now exiting InteractiveConsole...\n'
        self.assertEqual(err_msg, ['write', (expected,), {}])

        # no exit message
        self.stderr.reset_mock()
        self.infunc.side_effect = EOFError('Finished')
        self.console.interact(banner='', exitmsg='')
        self.assertEqual(len(self.stderr.method_calls), 1)

        # custom exit message
        self.stderr.reset_mock()
        message = (
            'bye! \N{GREEK SMALL LETTER ZETA}\N{CYRILLIC SMALL LETTER ZHE}'
            )
        self.infunc.side_effect = EOFError('Finished')
        self.console.interact(banner='', exitmsg=message)
        self.assertEqual(len(self.stderr.method_calls), 2)
        err_msg = self.stderr.method_calls[1]
        expected = message + '\n'
        self.assertEqual(err_msg, ['write', (expected,), {}])


    eleza test_cause_tb(self):
        self.infunc.side_effect = ["ashiria ValueError('') kutoka AttributeError",
                                    EOFError('Finished')]
        self.console.interact()
        output = ''.join(''.join(call[1]) kila call kwenye self.stderr.method_calls)
        expected = dedent("""
        AttributeError

        The above exception was the direct cause of the following exception:

        Traceback (most recent call last):
          File "<console>", line 1, kwenye <module>
        ValueError
        """)
        self.assertIn(expected, output)

    eleza test_context_tb(self):
        self.infunc.side_effect = ["jaribu: ham\nexcept: eggs\n",
                                    EOFError('Finished')]
        self.console.interact()
        output = ''.join(''.join(call[1]) kila call kwenye self.stderr.method_calls)
        expected = dedent("""
        Traceback (most recent call last):
          File "<console>", line 1, kwenye <module>
        NameError: name 'ham' ni sio defined

        During handling of the above exception, another exception occurred:

        Traceback (most recent call last):
          File "<console>", line 2, kwenye <module>
        NameError: name 'eggs' ni sio defined
        """)
        self.assertIn(expected, output)


ikiwa __name__ == "__main__":
    unittest.main()
