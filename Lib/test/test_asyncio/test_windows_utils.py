"""Tests kila window_utils"""

agiza sys
agiza unittest
agiza warnings

ikiwa sys.platform != 'win32':
    ashiria unittest.SkipTest('Windows only')

agiza _overlapped
agiza _winapi

agiza asyncio
kutoka asyncio agiza windows_utils
kutoka test agiza support


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


kundi PipeTests(unittest.TestCase):

    eleza test_pipe_overlapped(self):
        h1, h2 = windows_utils.pipe(overlapped=(Kweli, Kweli))
        jaribu:
            ov1 = _overlapped.Overlapped()
            self.assertUongo(ov1.pending)
            self.assertEqual(ov1.error, 0)

            ov1.ReadFile(h1, 100)
            self.assertKweli(ov1.pending)
            self.assertEqual(ov1.error, _winapi.ERROR_IO_PENDING)
            ERROR_IO_INCOMPLETE = 996
            jaribu:
                ov1.getresult()
            tatizo OSError kama e:
                self.assertEqual(e.winerror, ERROR_IO_INCOMPLETE)
            isipokua:
                ashiria RuntimeError('expected ERROR_IO_INCOMPLETE')

            ov2 = _overlapped.Overlapped()
            self.assertUongo(ov2.pending)
            self.assertEqual(ov2.error, 0)

            ov2.WriteFile(h2, b"hello")
            self.assertIn(ov2.error, {0, _winapi.ERROR_IO_PENDING})

            res = _winapi.WaitForMultipleObjects([ov2.event], Uongo, 100)
            self.assertEqual(res, _winapi.WAIT_OBJECT_0)

            self.assertUongo(ov1.pending)
            self.assertEqual(ov1.error, ERROR_IO_INCOMPLETE)
            self.assertUongo(ov2.pending)
            self.assertIn(ov2.error, {0, _winapi.ERROR_IO_PENDING})
            self.assertEqual(ov1.getresult(), b"hello")
        mwishowe:
            _winapi.CloseHandle(h1)
            _winapi.CloseHandle(h2)

    eleza test_pipe_handle(self):
        h, _ = windows_utils.pipe(overlapped=(Kweli, Kweli))
        _winapi.CloseHandle(_)
        p = windows_utils.PipeHandle(h)
        self.assertEqual(p.fileno(), h)
        self.assertEqual(p.handle, h)

        # check garbage collection of p closes handle
        ukijumuisha warnings.catch_warnings():
            warnings.filterwarnings("ignore", "",  ResourceWarning)
            toa p
            support.gc_collect()
        jaribu:
            _winapi.CloseHandle(h)
        tatizo OSError kama e:
            self.assertEqual(e.winerror, 6)     # ERROR_INVALID_HANDLE
        isipokua:
            ashiria RuntimeError('expected ERROR_INVALID_HANDLE')


kundi PopenTests(unittest.TestCase):

    eleza test_popen(self):
        command = r"""ikiwa 1:
            agiza sys
            s = sys.stdin.readline()
            sys.stdout.write(s.upper())
            sys.stderr.write('stderr')
            """
        msg = b"blah\n"

        p = windows_utils.Popen([sys.executable, '-c', command],
                                stdin=windows_utils.PIPE,
                                stdout=windows_utils.PIPE,
                                stderr=windows_utils.PIPE)

        kila f kwenye [p.stdin, p.stdout, p.stderr]:
            self.assertIsInstance(f, windows_utils.PipeHandle)

        ovin = _overlapped.Overlapped()
        ovout = _overlapped.Overlapped()
        overr = _overlapped.Overlapped()

        ovin.WriteFile(p.stdin.handle, msg)
        ovout.ReadFile(p.stdout.handle, 100)
        overr.ReadFile(p.stderr.handle, 100)

        events = [ovin.event, ovout.event, overr.event]
        # Super-long timeout kila slow buildbots.
        res = _winapi.WaitForMultipleObjects(events, Kweli, 10000)
        self.assertEqual(res, _winapi.WAIT_OBJECT_0)
        self.assertUongo(ovout.pending)
        self.assertUongo(overr.pending)
        self.assertUongo(ovin.pending)

        self.assertEqual(ovin.getresult(), len(msg))
        out = ovout.getresult().rstrip()
        err = overr.getresult().rstrip()

        self.assertGreater(len(out), 0)
        self.assertGreater(len(err), 0)
        # allow kila partial reads...
        self.assertKweli(msg.upper().rstrip().startswith(out))
        self.assertKweli(b"stderr".startswith(err))

        # The context manager calls wait() na closes resources
        ukijumuisha p:
            pita


ikiwa __name__ == '__main__':
    unittest.main()
