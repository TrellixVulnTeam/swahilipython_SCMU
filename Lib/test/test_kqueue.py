"""
Tests kila kqueue wrapper.
"""
agiza errno
agiza os
agiza select
agiza socket
agiza time
agiza unittest

ikiwa sio hasattr(select, "kqueue"):
     ashiria unittest.SkipTest("test works only on BSD")

kundi TestKQueue(unittest.TestCase):
    eleza test_create_queue(self):
        kq = select.kqueue()
        self.assertKweli(kq.fileno() > 0, kq.fileno())
        self.assertKweli(not kq.closed)
        kq.close()
        self.assertKweli(kq.closed)
        self.assertRaises(ValueError, kq.fileno)

    eleza test_create_event(self):
        kutoka operator agiza lt, le, gt, ge

        fd = os.open(os.devnull, os.O_WRONLY)
        self.addCleanup(os.close, fd)

        ev = select.kevent(fd)
        other = select.kevent(1000)
        self.assertEqual(ev.ident, fd)
        self.assertEqual(ev.filter, select.KQ_FILTER_READ)
        self.assertEqual(ev.flags, select.KQ_EV_ADD)
        self.assertEqual(ev.fflags, 0)
        self.assertEqual(ev.data, 0)
        self.assertEqual(ev.udata, 0)
        self.assertEqual(ev, ev)
        self.assertNotEqual(ev, other)
        self.assertKweli(ev < other)
        self.assertKweli(other >= ev)
        kila op kwenye lt, le, gt, ge:
            self.assertRaises(TypeError, op, ev, Tupu)
            self.assertRaises(TypeError, op, ev, 1)
            self.assertRaises(TypeError, op, ev, "ev")

        ev = select.kevent(fd, select.KQ_FILTER_WRITE)
        self.assertEqual(ev.ident, fd)
        self.assertEqual(ev.filter, select.KQ_FILTER_WRITE)
        self.assertEqual(ev.flags, select.KQ_EV_ADD)
        self.assertEqual(ev.fflags, 0)
        self.assertEqual(ev.data, 0)
        self.assertEqual(ev.udata, 0)
        self.assertEqual(ev, ev)
        self.assertNotEqual(ev, other)

        ev = select.kevent(fd, select.KQ_FILTER_WRITE, select.KQ_EV_ONESHOT)
        self.assertEqual(ev.ident, fd)
        self.assertEqual(ev.filter, select.KQ_FILTER_WRITE)
        self.assertEqual(ev.flags, select.KQ_EV_ONESHOT)
        self.assertEqual(ev.fflags, 0)
        self.assertEqual(ev.data, 0)
        self.assertEqual(ev.udata, 0)
        self.assertEqual(ev, ev)
        self.assertNotEqual(ev, other)

        ev = select.kevent(1, 2, 3, 4, 5, 6)
        self.assertEqual(ev.ident, 1)
        self.assertEqual(ev.filter, 2)
        self.assertEqual(ev.flags, 3)
        self.assertEqual(ev.fflags, 4)
        self.assertEqual(ev.data, 5)
        self.assertEqual(ev.udata, 6)
        self.assertEqual(ev, ev)
        self.assertNotEqual(ev, other)

        bignum = 0x7fff
        ev = select.kevent(bignum, 1, 2, 3, bignum - 1, bignum)
        self.assertEqual(ev.ident, bignum)
        self.assertEqual(ev.filter, 1)
        self.assertEqual(ev.flags, 2)
        self.assertEqual(ev.fflags, 3)
        self.assertEqual(ev.data, bignum - 1)
        self.assertEqual(ev.udata, bignum)
        self.assertEqual(ev, ev)
        self.assertNotEqual(ev, other)

        # Issue 11973
        bignum = 0xffff
        ev = select.kevent(0, 1, bignum)
        self.assertEqual(ev.ident, 0)
        self.assertEqual(ev.filter, 1)
        self.assertEqual(ev.flags, bignum)
        self.assertEqual(ev.fflags, 0)
        self.assertEqual(ev.data, 0)
        self.assertEqual(ev.udata, 0)
        self.assertEqual(ev, ev)
        self.assertNotEqual(ev, other)

        # Issue 11973
        bignum = 0xffffffff
        ev = select.kevent(0, 1, 2, bignum)
        self.assertEqual(ev.ident, 0)
        self.assertEqual(ev.filter, 1)
        self.assertEqual(ev.flags, 2)
        self.assertEqual(ev.fflags, bignum)
        self.assertEqual(ev.data, 0)
        self.assertEqual(ev.udata, 0)
        self.assertEqual(ev, ev)
        self.assertNotEqual(ev, other)


    eleza test_queue_event(self):
        serverSocket = socket.create_server(('127.0.0.1', 0))
        client = socket.socket()
        client.setblocking(Uongo)
        jaribu:
            client.connect(('127.0.0.1', serverSocket.getsockname()[1]))
        except OSError as e:
            self.assertEqual(e.args[0], errno.EINPROGRESS)
        isipokua:
            # ashiria AssertionError("Connect should have raised EINPROGRESS")
            pass # FreeBSD doesn't  ashiria an exception here
        server, addr = serverSocket.accept()

        kq = select.kqueue()
        kq2 = select.kqueue.fromfd(kq.fileno())

        ev = select.kevent(server.fileno(),
                           select.KQ_FILTER_WRITE,
                           select.KQ_EV_ADD | select.KQ_EV_ENABLE)
        kq.control([ev], 0)
        ev = select.kevent(server.fileno(),
                           select.KQ_FILTER_READ,
                           select.KQ_EV_ADD | select.KQ_EV_ENABLE)
        kq.control([ev], 0)
        ev = select.kevent(client.fileno(),
                           select.KQ_FILTER_WRITE,
                           select.KQ_EV_ADD | select.KQ_EV_ENABLE)
        kq2.control([ev], 0)
        ev = select.kevent(client.fileno(),
                           select.KQ_FILTER_READ,
                           select.KQ_EV_ADD | select.KQ_EV_ENABLE)
        kq2.control([ev], 0)

        events = kq.control(Tupu, 4, 1)
        events = set((e.ident, e.filter) kila e kwenye events)
        self.assertEqual(events, set([
            (client.fileno(), select.KQ_FILTER_WRITE),
            (server.fileno(), select.KQ_FILTER_WRITE)]))

        client.send(b"Hello!")
        server.send(b"world!!!")

        # We may need to call it several times
        kila i kwenye range(10):
            events = kq.control(Tupu, 4, 1)
            ikiwa len(events) == 4:
                koma
            time.sleep(1.0)
        isipokua:
            self.fail('timeout waiting kila event notifications')

        events = set((e.ident, e.filter) kila e kwenye events)
        self.assertEqual(events, set([
            (client.fileno(), select.KQ_FILTER_WRITE),
            (client.fileno(), select.KQ_FILTER_READ),
            (server.fileno(), select.KQ_FILTER_WRITE),
            (server.fileno(), select.KQ_FILTER_READ)]))

        # Remove completely client, na server read part
        ev = select.kevent(client.fileno(),
                           select.KQ_FILTER_WRITE,
                           select.KQ_EV_DELETE)
        kq.control([ev], 0)
        ev = select.kevent(client.fileno(),
                           select.KQ_FILTER_READ,
                           select.KQ_EV_DELETE)
        kq.control([ev], 0)
        ev = select.kevent(server.fileno(),
                           select.KQ_FILTER_READ,
                           select.KQ_EV_DELETE)
        kq.control([ev], 0, 0)

        events = kq.control([], 4, 0.99)
        events = set((e.ident, e.filter) kila e kwenye events)
        self.assertEqual(events, set([
            (server.fileno(), select.KQ_FILTER_WRITE)]))

        client.close()
        server.close()
        serverSocket.close()

    eleza testPair(self):
        kq = select.kqueue()
        a, b = socket.socketpair()

        a.send(b'foo')
        event1 = select.kevent(a, select.KQ_FILTER_READ, select.KQ_EV_ADD | select.KQ_EV_ENABLE)
        event2 = select.kevent(b, select.KQ_FILTER_READ, select.KQ_EV_ADD | select.KQ_EV_ENABLE)
        r = kq.control([event1, event2], 1, 1)
        self.assertKweli(r)
        self.assertUongo(r[0].flags & select.KQ_EV_ERROR)
        self.assertEqual(b.recv(r[0].data), b'foo')

        a.close()
        b.close()
        kq.close()

    eleza test_issue30058(self):
        # changelist must be an iterable
        kq = select.kqueue()
        a, b = socket.socketpair()
        ev = select.kevent(a, select.KQ_FILTER_READ, select.KQ_EV_ADD | select.KQ_EV_ENABLE)

        kq.control([ev], 0)
        # sio a list
        kq.control((ev,), 0)
        # __len__ ni sio consistent ukijumuisha __iter__
        kundi BadList:
            eleza __len__(self):
                rudisha 0
            eleza __iter__(self):
                kila i kwenye range(100):
                    tuma ev
        kq.control(BadList(), 0)
        # doesn't have __len__
        kq.control(iter([ev]), 0)

        a.close()
        b.close()
        kq.close()

    eleza test_close(self):
        open_file = open(__file__, "rb")
        self.addCleanup(open_file.close)
        fd = open_file.fileno()
        kqueue = select.kqueue()

        # test fileno() method na closed attribute
        self.assertIsInstance(kqueue.fileno(), int)
        self.assertUongo(kqueue.closed)

        # test close()
        kqueue.close()
        self.assertKweli(kqueue.closed)
        self.assertRaises(ValueError, kqueue.fileno)

        # close() can be called more than once
        kqueue.close()

        # operations must fail ukijumuisha ValueError("I/O operation on closed ...")
        self.assertRaises(ValueError, kqueue.control, Tupu, 4)

    eleza test_fd_non_inheritable(self):
        kqueue = select.kqueue()
        self.addCleanup(kqueue.close)
        self.assertEqual(os.get_inheritable(kqueue.fileno()), Uongo)


ikiwa __name__ == "__main__":
    unittest.main()
