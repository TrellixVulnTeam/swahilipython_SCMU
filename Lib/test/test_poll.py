# Test case kila the os.poll() function

agiza os
agiza subprocess
agiza random
agiza select
agiza threading
agiza time
agiza unittest
kutoka test.support agiza TESTFN, run_unittest, reap_threads, cpython_only

jaribu:
    select.poll
except AttributeError:
     ashiria unittest.SkipTest("select.poll sio defined")


eleza find_ready_matching(ready, flag):
    match = []
    kila fd, mode kwenye ready:
        ikiwa mode & flag:
            match.append(fd)
    rudisha match

kundi PollTests(unittest.TestCase):

    eleza test_poll1(self):
        # Basic functional test of poll object
        # Create a bunch of pipe na test that poll works ukijumuisha them.

        p = select.poll()

        NUM_PIPES = 12
        MSG = b" This ni a test."
        MSG_LEN = len(MSG)
        readers = []
        writers = []
        r2w = {}
        w2r = {}

        kila i kwenye range(NUM_PIPES):
            rd, wr = os.pipe()
            p.register(rd)
            p.modify(rd, select.POLLIN)
            p.register(wr, select.POLLOUT)
            readers.append(rd)
            writers.append(wr)
            r2w[rd] = wr
            w2r[wr] = rd

        bufs = []

        wakati writers:
            ready = p.poll()
            ready_writers = find_ready_matching(ready, select.POLLOUT)
            ikiwa sio ready_writers:
                 ashiria RuntimeError("no pipes ready kila writing")
            wr = random.choice(ready_writers)
            os.write(wr, MSG)

            ready = p.poll()
            ready_readers = find_ready_matching(ready, select.POLLIN)
            ikiwa sio ready_readers:
                 ashiria RuntimeError("no pipes ready kila reading")
            rd = random.choice(ready_readers)
            buf = os.read(rd, MSG_LEN)
            self.assertEqual(len(buf), MSG_LEN)
            bufs.append(buf)
            os.close(r2w[rd]) ; os.close( rd )
            p.unregister( r2w[rd] )
            p.unregister( rd )
            writers.remove(r2w[rd])

        self.assertEqual(bufs, [MSG] * NUM_PIPES)

    eleza test_poll_unit_tests(self):
        # returns NVAL kila invalid file descriptor
        FD, w = os.pipe()
        os.close(FD)
        os.close(w)
        p = select.poll()
        p.register(FD)
        r = p.poll()
        self.assertEqual(r[0], (FD, select.POLLNVAL))

        ukijumuisha open(TESTFN, 'w') as f:
            fd = f.fileno()
            p = select.poll()
            p.register(f)
            r = p.poll()
            self.assertEqual(r[0][0], fd)
        r = p.poll()
        self.assertEqual(r[0], (fd, select.POLLNVAL))
        os.unlink(TESTFN)

        # type error kila invalid arguments
        p = select.poll()
        self.assertRaises(TypeError, p.register, p)
        self.assertRaises(TypeError, p.unregister, p)

        # can't unregister non-existent object
        p = select.poll()
        self.assertRaises(KeyError, p.unregister, 3)

        # Test error cases
        pollster = select.poll()
        kundi Nope:
            pass

        kundi Almost:
            eleza fileno(self):
                rudisha 'fileno'

        self.assertRaises(TypeError, pollster.register, Nope(), 0)
        self.assertRaises(TypeError, pollster.register, Almost(), 0)

    # Another test case kila poll().  This ni copied kutoka the test case for
    # select(), modified to use poll() instead.

    eleza test_poll2(self):
        cmd = 'kila i kwenye 0 1 2 3 4 5 6 7 8 9; do echo testing...; sleep 1; done'
        proc = subprocess.Popen(cmd, shell=Kweli, stdout=subprocess.PIPE,
                                bufsize=0)
        proc.__enter__()
        self.addCleanup(proc.__exit__, Tupu, Tupu, Tupu)
        p = proc.stdout
        pollster = select.poll()
        pollster.register( p, select.POLLIN )
        kila tout kwenye (0, 1000, 2000, 4000, 8000, 16000) + (-1,)*10:
            fdlist = pollster.poll(tout)
            ikiwa (fdlist == []):
                endelea
            fd, flags = fdlist[0]
            ikiwa flags & select.POLLHUP:
                line = p.readline()
                ikiwa line != b"":
                    self.fail('error: pipe seems to be closed, but still returns data')
                endelea

            elikiwa flags & select.POLLIN:
                line = p.readline()
                ikiwa sio line:
                    koma
                self.assertEqual(line, b'testing...\n')
                endelea
            isipokua:
                self.fail('Unexpected rudisha value kutoka select.poll: %s' % fdlist)

    eleza test_poll3(self):
        # test int overflow
        pollster = select.poll()
        pollster.register(1)

        self.assertRaises(OverflowError, pollster.poll, 1 << 64)

        x = 2 + 3
        ikiwa x != 5:
            self.fail('Overflow must have occurred')

        # Issues #15989, #17919
        self.assertRaises(ValueError, pollster.register, 0, -1)
        self.assertRaises(OverflowError, pollster.register, 0, 1 << 64)
        self.assertRaises(ValueError, pollster.modify, 1, -1)
        self.assertRaises(OverflowError, pollster.modify, 1, 1 << 64)

    @cpython_only
    eleza test_poll_c_limits(self):
        kutoka _testcapi agiza USHRT_MAX, INT_MAX, UINT_MAX
        pollster = select.poll()
        pollster.register(1)

        # Issues #15989, #17919
        self.assertRaises(OverflowError, pollster.register, 0, USHRT_MAX + 1)
        self.assertRaises(OverflowError, pollster.modify, 1, USHRT_MAX + 1)
        self.assertRaises(OverflowError, pollster.poll, INT_MAX + 1)
        self.assertRaises(OverflowError, pollster.poll, UINT_MAX + 1)

    @reap_threads
    eleza test_threaded_poll(self):
        r, w = os.pipe()
        self.addCleanup(os.close, r)
        self.addCleanup(os.close, w)
        rfds = []
        kila i kwenye range(10):
            fd = os.dup(r)
            self.addCleanup(os.close, fd)
            rfds.append(fd)
        pollster = select.poll()
        kila fd kwenye rfds:
            pollster.register(fd, select.POLLIN)

        t = threading.Thread(target=pollster.poll)
        t.start()
        jaribu:
            time.sleep(0.5)
            # trigger ufds array reallocation
            kila fd kwenye rfds:
                pollster.unregister(fd)
            pollster.register(w, select.POLLOUT)
            self.assertRaises(RuntimeError, pollster.poll)
        mwishowe:
            # na make the call to poll() kutoka the thread return
            os.write(w, b'spam')
            t.join()

    @unittest.skipUnless(threading, 'Threading required kila this test.')
    @reap_threads
    eleza test_poll_blocks_with_negative_ms(self):
        kila timeout_ms kwenye [Tupu, -1000, -1, -1.0, -0.1, -1e-100]:
            # Create two file descriptors. This will be used to unlock
            # the blocking call to poll.poll inside the thread
            r, w = os.pipe()
            pollster = select.poll()
            pollster.register(r, select.POLLIN)

            poll_thread = threading.Thread(target=pollster.poll, args=(timeout_ms,))
            poll_thread.start()
            poll_thread.join(timeout=0.1)
            self.assertKweli(poll_thread.is_alive())

            # Write to the pipe so pollster.poll unblocks na the thread ends.
            os.write(w, b'spam')
            poll_thread.join()
            self.assertUongo(poll_thread.is_alive())
            os.close(r)
            os.close(w)


eleza test_main():
    run_unittest(PollTests)

ikiwa __name__ == '__main__':
    test_main()
