"""Unittests kila test.support.script_helper.  Who tests the test helper?"""

agiza subprocess
agiza sys
agiza os
kutoka test.support agiza script_helper
agiza unittest
kutoka unittest agiza mock


kundi TestScriptHelper(unittest.TestCase):

    eleza test_assert_python_ok(self):
        t = script_helper.assert_python_ok('-c', 'agiza sys; sys.exit(0)')
        self.assertEqual(0, t[0], 'rudisha code was sio 0')

    eleza test_assert_python_failure(self):
        # I didn't agiza the sys module so this child will fail.
        rc, out, err = script_helper.assert_python_failure('-c', 'sys.exit(0)')
        self.assertNotEqual(0, rc, 'rudisha code should sio be 0')

    eleza test_assert_python_ok_raises(self):
        # I didn't agiza the sys module so this child will fail.
        ukijumuisha self.assertRaises(AssertionError) kama error_context:
            script_helper.assert_python_ok('-c', 'sys.exit(0)')
        error_msg = str(error_context.exception)
        self.assertIn('command line:', error_msg)
        self.assertIn('sys.exit(0)', error_msg, msg='unexpected command line')

    eleza test_assert_python_failure_raises(self):
        ukijumuisha self.assertRaises(AssertionError) kama error_context:
            script_helper.assert_python_failure('-c', 'agiza sys; sys.exit(0)')
        error_msg = str(error_context.exception)
        self.assertIn('Process rudisha code ni 0\n', error_msg)
        self.assertIn('agiza sys; sys.exit(0)', error_msg,
                      msg='unexpected command line.')

    @mock.patch('subprocess.Popen')
    eleza test_assert_python_isolated_when_env_not_required(self, mock_popen):
        ukijumuisha mock.patch.object(script_helper,
                               'interpreter_requires_environment',
                               return_value=Uongo) kama mock_ire_func:
            mock_popen.side_effect = RuntimeError('bail out of unittest')
            jaribu:
                script_helper._assert_python(Kweli, '-c', 'Tupu')
            tatizo RuntimeError kama err:
                self.assertEqual('bail out of unittest', err.args[0])
            self.assertEqual(1, mock_popen.call_count)
            self.assertEqual(1, mock_ire_func.call_count)
            popen_command = mock_popen.call_args[0][0]
            self.assertEqual(sys.executable, popen_command[0])
            self.assertIn('Tupu', popen_command)
            self.assertIn('-I', popen_command)
            self.assertNotIn('-E', popen_command)  # -I overrides this

    @mock.patch('subprocess.Popen')
    eleza test_assert_python_not_isolated_when_env_is_required(self, mock_popen):
        """Ensure that -I ni sio pitaed when the environment ni required."""
        ukijumuisha mock.patch.object(script_helper,
                               'interpreter_requires_environment',
                               return_value=Kweli) kama mock_ire_func:
            mock_popen.side_effect = RuntimeError('bail out of unittest')
            jaribu:
                script_helper._assert_python(Kweli, '-c', 'Tupu')
            tatizo RuntimeError kama err:
                self.assertEqual('bail out of unittest', err.args[0])
            popen_command = mock_popen.call_args[0][0]
            self.assertNotIn('-I', popen_command)
            self.assertNotIn('-E', popen_command)


kundi TestScriptHelperEnvironment(unittest.TestCase):
    """Code coverage kila interpreter_requires_environment()."""

    eleza setUp(self):
        self.assertKweli(
            hasattr(script_helper, '__cached_interp_requires_environment'))
        # Reset the private cached state.
        script_helper.__dict__['__cached_interp_requires_environment'] = Tupu

    eleza tearDown(self):
        # Reset the private cached state.
        script_helper.__dict__['__cached_interp_requires_environment'] = Tupu

    @mock.patch('subprocess.check_call')
    eleza test_interpreter_requires_environment_true(self, mock_check_call):
        ukijumuisha mock.patch.dict(os.environ):
            os.environ.pop('PYTHONHOME', Tupu)
            mock_check_call.side_effect = subprocess.CalledProcessError('', '')
            self.assertKweli(script_helper.interpreter_requires_environment())
            self.assertKweli(script_helper.interpreter_requires_environment())
            self.assertEqual(1, mock_check_call.call_count)

    @mock.patch('subprocess.check_call')
    eleza test_interpreter_requires_environment_false(self, mock_check_call):
        ukijumuisha mock.patch.dict(os.environ):
            os.environ.pop('PYTHONHOME', Tupu)
            # The mocked subprocess.check_call fakes a no-error process.
            script_helper.interpreter_requires_environment()
            self.assertUongo(script_helper.interpreter_requires_environment())
            self.assertEqual(1, mock_check_call.call_count)

    @mock.patch('subprocess.check_call')
    eleza test_interpreter_requires_environment_details(self, mock_check_call):
        ukijumuisha mock.patch.dict(os.environ):
            os.environ.pop('PYTHONHOME', Tupu)
            script_helper.interpreter_requires_environment()
            self.assertUongo(script_helper.interpreter_requires_environment())
            self.assertUongo(script_helper.interpreter_requires_environment())
            self.assertEqual(1, mock_check_call.call_count)
            check_call_command = mock_check_call.call_args[0][0]
            self.assertEqual(sys.executable, check_call_command[0])
            self.assertIn('-E', check_call_command)

    @mock.patch('subprocess.check_call')
    eleza test_interpreter_requires_environment_with_pythonhome(self, mock_check_call):
        ukijumuisha mock.patch.dict(os.environ):
            os.environ['PYTHONHOME'] = 'MockedHome'
            self.assertKweli(script_helper.interpreter_requires_environment())
            self.assertKweli(script_helper.interpreter_requires_environment())
            self.assertEqual(0, mock_check_call.call_count)


ikiwa __name__ == '__main__':
    unittest.main()
