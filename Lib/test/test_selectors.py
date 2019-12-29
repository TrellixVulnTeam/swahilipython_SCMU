agiza errno
agiza os
agiza random
agiza selectors
agiza signal
agiza socket
agiza sys
kutoka test agiza support
kutoka time agiza sleep
agiza unittest
agiza unittest.mock
agiza tempfile
kutoka time agiza monotonic kama time
jaribu:
    agiza resource
tatizo ImportError:
    resource = Tupu


ikiwa hasattr(socket, 'socketpair'):
    socketpair = socket.socketpair
isipokua:
    eleza socketpair(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0):
        ukijumuisha socket.socket(family, type, proto) kama l:
            l.bind((support.HOST, 0))
            l.listen()
            c = socket.socket(family, type, proto)
            jaribu:
                c.connect(l.getsockname())
                caddr = c.getsockname()
                wakati Kweli:
                    a, addr = l.accept()
                    # check that we've got the correct client
                    ikiwa addr == caddr:
                        rudisha c, a
                    a.close()
            tatizo OSError:
                c.close()
                ashiria


eleza find_ready_matching(ready, flag):
    match = []
    kila key, events kwenye ready:
        ikiwa events & flag:
            match.append(key.fileobj)
    rudisha match


kundi BaseSelectorTestCase(unittest.TestCase):

    eleza make_socketpair(self):
        rd, wr = socketpair()
        self.addCleanup(rd.close)
        self.addCleanup(wr.close)
        rudisha rd, wr

    eleza test_register(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        key = s.register(rd, selectors.EVENT_READ, "data")
        self.assertIsInstance(key, selectors.SelectorKey)
        self.assertEqual(key.fileobj, rd)
        self.assertEqual(key.fd, rd.fileno())
        self.assertEqual(key.events, selectors.EVENT_READ)
        self.assertEqual(key.data, "data")

        # register an unknown event
        self.assertRaises(ValueError, s.register, 0, 999999)

        # register an invalid FD
        self.assertRaises(ValueError, s.register, -10, selectors.EVENT_READ)

        # register twice
        self.assertRaises(KeyError, s.register, rd, selectors.EVENT_READ)

        # register the same FD, but ukijumuisha a different object
        self.assertRaises(KeyError, s.register, rd.fileno(),
                          selectors.EVENT_READ)

    eleza test_unregister(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        s.register(rd, selectors.EVENT_READ)
        s.unregister(rd)

        # unregister an unknown file obj
        self.assertRaises(KeyError, s.unregister, 999999)

        # unregister twice
        self.assertRaises(KeyError, s.unregister, rd)

    eleza test_unregister_after_fd_close(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)
        rd, wr = self.make_socketpair()
        r, w = rd.fileno(), wr.fileno()
        s.register(r, selectors.EVENT_READ)
        s.register(w, selectors.EVENT_WRITE)
        rd.close()
        wr.close()
        s.unregister(r)
        s.unregister(w)

    @unittest.skipUnless(os.name == 'posix', "requires posix")
    eleza test_unregister_after_fd_close_and_reuse(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)
        rd, wr = self.make_socketpair()
        r, w = rd.fileno(), wr.fileno()
        s.register(r, selectors.EVENT_READ)
        s.register(w, selectors.EVENT_WRITE)
        rd2, wr2 = self.make_socketpair()
        rd.close()
        wr.close()
        os.dup2(rd2.fileno(), r)
        os.dup2(wr2.fileno(), w)
        self.addCleanup(os.close, r)
        self.addCleanup(os.close, w)
        s.unregister(r)
        s.unregister(w)

    eleza test_unregister_after_socket_close(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)
        rd, wr = self.make_socketpair()
        s.register(rd, selectors.EVENT_READ)
        s.register(wr, selectors.EVENT_WRITE)
        rd.close()
        wr.close()
        s.unregister(rd)
        s.unregister(wr)

    eleza test_modify(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        key = s.register(rd, selectors.EVENT_READ)

        # modify events
        key2 = s.modify(rd, selectors.EVENT_WRITE)
        self.assertNotEqual(key.events, key2.events)
        self.assertEqual(key2, s.get_key(rd))

        s.unregister(rd)

        # modify data
        d1 = object()
        d2 = object()

        key = s.register(rd, selectors.EVENT_READ, d1)
        key2 = s.modify(rd, selectors.EVENT_READ, d2)
        self.assertEqual(key.events, key2.events)
        self.assertNotEqual(key.data, key2.data)
        self.assertEqual(key2, s.get_key(rd))
        self.assertEqual(key2.data, d2)

        # modify unknown file obj
        self.assertRaises(KeyError, s.modify, 999999, selectors.EVENT_READ)

        # modify use a shortcut
        d3 = object()
        s.register = unittest.mock.Mock()
        s.unregister = unittest.mock.Mock()

        s.modify(rd, selectors.EVENT_READ, d3)
        self.assertUongo(s.register.called)
        self.assertUongo(s.unregister.called)

    eleza test_modify_unregister(self):
        # Make sure the fd ni unregister()ed kwenye case of error on
        # modify(): http://bugs.python.org/issue30014
        ikiwa self.SELECTOR.__name__ == 'EpollSelector':
            patch = unittest.mock.patch(
                'selectors.EpollSelector._selector_cls')
        lasivyo self.SELECTOR.__name__ == 'PollSelector':
            patch = unittest.mock.patch(
                'selectors.PollSelector._selector_cls')
        lasivyo self.SELECTOR.__name__ == 'DevpollSelector':
            patch = unittest.mock.patch(
                'selectors.DevpollSelector._selector_cls')
        isipokua:
            ashiria self.skipTest("")

        ukijumuisha patch kama m:
            m.rudisha_value.modify = unittest.mock.Mock(
                side_effect=ZeroDivisionError)
            s = self.SELECTOR()
            self.addCleanup(s.close)
            rd, wr = self.make_socketpair()
            s.register(rd, selectors.EVENT_READ)
            self.assertEqual(len(s._map), 1)
            ukijumuisha self.assertRaises(ZeroDivisionError):
                s.modify(rd, selectors.EVENT_WRITE)
            self.assertEqual(len(s._map), 0)

    eleza test_close(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        mapping = s.get_map()
        rd, wr = self.make_socketpair()

        s.register(rd, selectors.EVENT_READ)
        s.register(wr, selectors.EVENT_WRITE)

        s.close()
        self.assertRaises(RuntimeError, s.get_key, rd)
        self.assertRaises(RuntimeError, s.get_key, wr)
        self.assertRaises(KeyError, mapping.__getitem__, rd)
        self.assertRaises(KeyError, mapping.__getitem__, wr)

    eleza test_get_key(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        key = s.register(rd, selectors.EVENT_READ, "data")
        self.assertEqual(key, s.get_key(rd))

        # unknown file obj
        self.assertRaises(KeyError, s.get_key, 999999)

    eleza test_get_map(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        keys = s.get_map()
        self.assertUongo(keys)
        self.assertEqual(len(keys), 0)
        self.assertEqual(list(keys), [])
        key = s.register(rd, selectors.EVENT_READ, "data")
        self.assertIn(rd, keys)
        self.assertEqual(key, keys[rd])
        self.assertEqual(len(keys), 1)
        self.assertEqual(list(keys), [rd.fileno()])
        self.assertEqual(list(keys.values()), [key])

        # unknown file obj
        ukijumuisha self.assertRaises(KeyError):
            keys[999999]

        # Read-only mapping
        ukijumuisha self.assertRaises(TypeError):
            toa keys[rd]

    eleza test_select(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        s.register(rd, selectors.EVENT_READ)
        wr_key = s.register(wr, selectors.EVENT_WRITE)

        result = s.select()
        kila key, events kwenye result:
            self.assertKweli(isinstance(key, selectors.SelectorKey))
            self.assertKweli(events)
            self.assertUongo(events & ~(selectors.EVENT_READ |
                                        selectors.EVENT_WRITE))

        self.assertEqual([(wr_key, selectors.EVENT_WRITE)], result)

    eleza test_context_manager(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        ukijumuisha s kama sel:
            sel.register(rd, selectors.EVENT_READ)
            sel.register(wr, selectors.EVENT_WRITE)

        self.assertRaises(RuntimeError, s.get_key, rd)
        self.assertRaises(RuntimeError, s.get_key, wr)

    eleza test_fileno(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        ikiwa hasattr(s, 'fileno'):
            fd = s.fileno()
            self.assertKweli(isinstance(fd, int))
            self.assertGreaterEqual(fd, 0)

    eleza test_selector(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        NUM_SOCKETS = 12
        MSG = b" This ni a test."
        MSG_LEN = len(MSG)
        readers = []
        writers = []
        r2w = {}
        w2r = {}

        kila i kwenye range(NUM_SOCKETS):
            rd, wr = self.make_socketpair()
            s.register(rd, selectors.EVENT_READ)
            s.register(wr, selectors.EVENT_WRITE)
            readers.append(rd)
            writers.append(wr)
            r2w[rd] = wr
            w2r[wr] = rd

        bufs = []

        wakati writers:
            ready = s.select()
            ready_writers = find_ready_matching(ready, selectors.EVENT_WRITE)
            ikiwa sio ready_writers:
                self.fail("no sockets ready kila writing")
            wr = random.choice(ready_writers)
            wr.send(MSG)

            kila i kwenye range(10):
                ready = s.select()
                ready_readers = find_ready_matching(ready,
                                                    selectors.EVENT_READ)
                ikiwa ready_readers:
                    koma
                # there might be a delay between the write to the write end and
                # the read end ni reported ready
                sleep(0.1)
            isipokua:
                self.fail("no sockets ready kila reading")
            self.assertEqual([w2r[wr]], ready_readers)
            rd = ready_readers[0]
            buf = rd.recv(MSG_LEN)
            self.assertEqual(len(buf), MSG_LEN)
            bufs.append(buf)
            s.unregister(r2w[rd])
            s.unregister(rd)
            writers.remove(r2w[rd])

        self.assertEqual(bufs, [MSG] * NUM_SOCKETS)

    @unittest.skipIf(sys.platform == 'win32',
                     'select.select() cannot be used ukijumuisha empty fd sets')
    eleza test_empty_select(self):
        # Issue #23009: Make sure EpollSelector.select() works when no FD is
        # registered.
        s = self.SELECTOR()
        self.addCleanup(s.close)
        self.assertEqual(s.select(timeout=0), [])

    eleza test_timeout(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        s.register(wr, selectors.EVENT_WRITE)
        t = time()
        self.assertEqual(1, len(s.select(0)))
        self.assertEqual(1, len(s.select(-1)))
        self.assertLess(time() - t, 0.5)

        s.unregister(wr)
        s.register(rd, selectors.EVENT_READ)
        t = time()
        self.assertUongo(s.select(0))
        self.assertUongo(s.select(-1))
        self.assertLess(time() - t, 0.5)

        t0 = time()
        self.assertUongo(s.select(1))
        t1 = time()
        dt = t1 - t0
        # Tolerate 2.0 seconds kila very slow buildbots
        self.assertKweli(0.8 <= dt <= 2.0, dt)

    @unittest.skipUnless(hasattr(signal, "alarm"),
                         "signal.alarm() required kila this test")
    eleza test_select_interrupt_exc(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        kundi InterruptSelect(Exception):
            pita

        eleza handler(*args):
            ashiria InterruptSelect

        orig_alrm_handler = signal.signal(signal.SIGALRM, handler)
        self.addCleanup(signal.signal, signal.SIGALRM, orig_alrm_handler)

        jaribu:
            signal.alarm(1)

            s.register(rd, selectors.EVENT_READ)
            t = time()
            # select() ni interrupted by a signal which ashirias an exception
            ukijumuisha self.assertRaises(InterruptSelect):
                s.select(30)
            # select() was interrupted before the timeout of 30 seconds
            self.assertLess(time() - t, 5.0)
        mwishowe:
            signal.alarm(0)

    @unittest.skipUnless(hasattr(signal, "alarm"),
                         "signal.alarm() required kila this test")
    eleza test_select_interrupt_noashiria(self):
        s = self.SELECTOR()
        self.addCleanup(s.close)

        rd, wr = self.make_socketpair()

        orig_alrm_handler = signal.signal(signal.SIGALRM, lambda *args: Tupu)
        self.addCleanup(signal.signal, signal.SIGALRM, orig_alrm_handler)

        jaribu:
            signal.alarm(1)

            s.register(rd, selectors.EVENT_READ)
            t = time()
            # select() ni interrupted by a signal, but the signal handler doesn't
            # ashiria an exception, so select() should by retries ukijumuisha a recomputed
            # timeout
            self.assertUongo(s.select(1.5))
            self.assertGreaterEqual(time() - t, 1.0)
        mwishowe:
            signal.alarm(0)


kundi ScalableSelectorMixIn:

    # see issue #18963 kila why it's skipped on older OS X versions
    @support.requires_mac_ver(10, 5)
    @unittest.skipUnless(resource, "Test needs resource module")
    eleza test_above_fd_setsize(self):
        # A scalable implementation should have no problem ukijumuisha more than
        # FD_SETSIZE file descriptors. Since we don't know the value, we just
        # try to set the soft RLIMIT_NOFILE to the hard RLIMIT_NOFILE ceiling.
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        jaribu:
            resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))
            self.addCleanup(resource.setrlimit, resource.RLIMIT_NOFILE,
                            (soft, hard))
            NUM_FDS = min(hard, 2**16)
        tatizo (OSError, ValueError):
            NUM_FDS = soft

        # guard kila already allocated FDs (stdin, stdout...)
        NUM_FDS -= 32

        s = self.SELECTOR()
        self.addCleanup(s.close)

        kila i kwenye range(NUM_FDS // 2):
            jaribu:
                rd, wr = self.make_socketpair()
            tatizo OSError:
                # too many FDs, skip - note that we should only catch EMFILE
                # here, but apparently *BSD na Solaris can fail upon connect()
                # ama bind() ukijumuisha EADDRNOTAVAIL, so let's be safe
                self.skipTest("FD limit reached")

            jaribu:
                s.register(rd, selectors.EVENT_READ)
                s.register(wr, selectors.EVENT_WRITE)
            tatizo OSError kama e:
                ikiwa e.errno == errno.ENOSPC:
                    # this can be ashiriad by epoll ikiwa we go over
                    # fs.epoll.max_user_watches sysctl
                    self.skipTest("FD limit reached")
                ashiria

        jaribu:
            fds = s.select()
        tatizo OSError kama e:
            ikiwa e.errno == errno.EINVAL na sys.platform == 'darwin':
                # unexplainable errors on macOS don't need to fail the test
                self.skipTest("Invalid argument error calling poll()")
            ashiria
        self.assertEqual(NUM_FDS // 2, len(fds))


kundi DefaultSelectorTestCase(BaseSelectorTestCase):

    SELECTOR = selectors.DefaultSelector


kundi SelectSelectorTestCase(BaseSelectorTestCase):

    SELECTOR = selectors.SelectSelector


@unittest.skipUnless(hasattr(selectors, 'PollSelector'),
                     "Test needs selectors.PollSelector")
kundi PollSelectorTestCase(BaseSelectorTestCase, ScalableSelectorMixIn):

    SELECTOR = getattr(selectors, 'PollSelector', Tupu)


@unittest.skipUnless(hasattr(selectors, 'EpollSelector'),
                     "Test needs selectors.EpollSelector")
kundi EpollSelectorTestCase(BaseSelectorTestCase, ScalableSelectorMixIn):

    SELECTOR = getattr(selectors, 'EpollSelector', Tupu)

    eleza test_register_file(self):
        # epoll(7) rudishas EPERM when given a file to watch
        s = self.SELECTOR()
        ukijumuisha tempfile.NamedTemporaryFile() kama f:
            ukijumuisha self.assertRaises(IOError):
                s.register(f, selectors.EVENT_READ)
            # the SelectorKey has been removed
            ukijumuisha self.assertRaises(KeyError):
                s.get_key(f)


@unittest.skipUnless(hasattr(selectors, 'KqueueSelector'),
                     "Test needs selectors.KqueueSelector)")
kundi KqueueSelectorTestCase(BaseSelectorTestCase, ScalableSelectorMixIn):

    SELECTOR = getattr(selectors, 'KqueueSelector', Tupu)

    eleza test_register_bad_fd(self):
        # a file descriptor that's been closed should ashiria an OSError
        # ukijumuisha EBADF
        s = self.SELECTOR()
        bad_f = support.make_bad_fd()
        ukijumuisha self.assertRaises(OSError) kama cm:
            s.register(bad_f, selectors.EVENT_READ)
        self.assertEqual(cm.exception.errno, errno.EBADF)
        # the SelectorKey has been removed
        ukijumuisha self.assertRaises(KeyError):
            s.get_key(bad_f)


@unittest.skipUnless(hasattr(selectors, 'DevpollSelector'),
                     "Test needs selectors.DevpollSelector")
kundi DevpollSelectorTestCase(BaseSelectorTestCase, ScalableSelectorMixIn):

    SELECTOR = getattr(selectors, 'DevpollSelector', Tupu)



eleza test_main():
    tests = [DefaultSelectorTestCase, SelectSelectorTestCase,
             PollSelectorTestCase, EpollSelectorTestCase,
             KqueueSelectorTestCase, DevpollSelectorTestCase]
    support.run_unittest(*tests)
    support.reap_children()


ikiwa __name__ == "__main__":
    test_main()
