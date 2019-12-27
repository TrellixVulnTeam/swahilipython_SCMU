agiza os
agiza signal
agiza subprocess
agiza sys
agiza time
agiza unittest


kundi SIGUSR1Exception(Exception):
    pass


kundi InterProcessSignalTests(unittest.TestCase):
    eleza setUp(self):
        self.got_signals = {'SIGHUP': 0, 'SIGUSR1': 0, 'SIGALRM': 0}

    eleza sighup_handler(self, signum, frame):
        self.got_signals['SIGHUP'] += 1

    eleza sigusr1_handler(self, signum, frame):
        self.got_signals['SIGUSR1'] += 1
        raise SIGUSR1Exception

    eleza wait_signal(self, child, signame):
        ikiwa child is not None:
            # This wait should be interrupted by exc_class
            # (ikiwa set)
            child.wait()

        timeout = 10.0
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            ikiwa self.got_signals[signame]:
                return
            signal.pause()

        self.fail('signal %s not received after %s seconds'
                  % (signame, timeout))

    eleza subprocess_send_signal(self, pid, signame):
        code = 'agiza os, signal; os.kill(%s, signal.%s)' % (pid, signame)
        args = [sys.executable, '-I', '-c', code]
        rudisha subprocess.Popen(args)

    eleza test_interprocess_signal(self):
        # Install handlers. This function runs in a sub-process, so we
        # don't worry about re-setting the default handlers.
        signal.signal(signal.SIGHUP, self.sighup_handler)
        signal.signal(signal.SIGUSR1, self.sigusr1_handler)
        signal.signal(signal.SIGUSR2, signal.SIG_IGN)
        signal.signal(signal.SIGALRM, signal.default_int_handler)

        # Let the sub-processes know who to send signals to.
        pid = str(os.getpid())

        with self.subprocess_send_signal(pid, "SIGHUP") as child:
            self.wait_signal(child, 'SIGHUP')
        self.assertEqual(self.got_signals, {'SIGHUP': 1, 'SIGUSR1': 0,
                                            'SIGALRM': 0})

        with self.assertRaises(SIGUSR1Exception):
            with self.subprocess_send_signal(pid, "SIGUSR1") as child:
                self.wait_signal(child, 'SIGUSR1')
        self.assertEqual(self.got_signals, {'SIGHUP': 1, 'SIGUSR1': 1,
                                            'SIGALRM': 0})

        with self.subprocess_send_signal(pid, "SIGUSR2") as child:
            # Nothing should happen: SIGUSR2 is ignored
            child.wait()

        try:
            with self.assertRaises(KeyboardInterrupt):
                signal.alarm(1)
                self.wait_signal(None, 'SIGALRM')
            self.assertEqual(self.got_signals, {'SIGHUP': 1, 'SIGUSR1': 1,
                                                'SIGALRM': 0})
        finally:
            signal.alarm(0)


ikiwa __name__ == "__main__":
    unittest.main()
