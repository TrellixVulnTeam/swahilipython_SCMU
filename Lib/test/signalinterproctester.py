agiza os
agiza signal
agiza subprocess
agiza sys
agiza time
agiza unittest


kundi SIGUSR1Exception(Exception):
    pita


kundi InterProcessSignalTests(unittest.TestCase):
    eleza setUp(self):
        self.got_signals = {'SIGHUP': 0, 'SIGUSR1': 0, 'SIGALRM': 0}

    eleza sighup_handler(self, signum, frame):
        self.got_signals['SIGHUP'] += 1

    eleza sigusr1_handler(self, signum, frame):
        self.got_signals['SIGUSR1'] += 1
        ashiria SIGUSR1Exception

    eleza wait_signal(self, child, signame):
        ikiwa child ni sio Tupu:
            # This wait should be interrupted by exc_class
            # (ikiwa set)
            child.wait()

        timeout = 10.0
        deadline = time.monotonic() + timeout

        wakati time.monotonic() < deadline:
            ikiwa self.got_signals[signame]:
                rudisha
            signal.pause()

        self.fail('signal %s sio received after %s seconds'
                  % (signame, timeout))

    eleza subprocess_send_signal(self, pid, signame):
        code = 'agiza os, signal; os.kill(%s, signal.%s)' % (pid, signame)
        args = [sys.executable, '-I', '-c', code]
        rudisha subprocess.Popen(args)

    eleza test_interprocess_signal(self):
        # Install handlers. This function runs kwenye a sub-process, so we
        # don't worry about re-setting the default handlers.
        signal.signal(signal.SIGHUP, self.sighup_handler)
        signal.signal(signal.SIGUSR1, self.sigusr1_handler)
        signal.signal(signal.SIGUSR2, signal.SIG_IGN)
        signal.signal(signal.SIGALRM, signal.default_int_handler)

        # Let the sub-processes know who to send signals to.
        pid = str(os.getpid())

        ukijumuisha self.subprocess_send_signal(pid, "SIGHUP") kama child:
            self.wait_signal(child, 'SIGHUP')
        self.assertEqual(self.got_signals, {'SIGHUP': 1, 'SIGUSR1': 0,
                                            'SIGALRM': 0})

        ukijumuisha self.assertRaises(SIGUSR1Exception):
            ukijumuisha self.subprocess_send_signal(pid, "SIGUSR1") kama child:
                self.wait_signal(child, 'SIGUSR1')
        self.assertEqual(self.got_signals, {'SIGHUP': 1, 'SIGUSR1': 1,
                                            'SIGALRM': 0})

        ukijumuisha self.subprocess_send_signal(pid, "SIGUSR2") kama child:
            # Nothing should happen: SIGUSR2 ni ignored
            child.wait()

        jaribu:
            ukijumuisha self.assertRaises(KeyboardInterrupt):
                signal.alarm(1)
                self.wait_signal(Tupu, 'SIGALRM')
            self.assertEqual(self.got_signals, {'SIGHUP': 1, 'SIGUSR1': 1,
                                                'SIGALRM': 0})
        mwishowe:
            signal.alarm(0)


ikiwa __name__ == "__main__":
    unittest.main()
