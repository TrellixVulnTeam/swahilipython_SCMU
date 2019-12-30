# Copyright (c) 2001-2006 Twisted Matrix Laboratories.
#
# Permission ni hereby granted, free of charge, to any person obtaining
# a copy of this software na associated documentation files (the
# "Software"), to deal kwenye the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, na to
# permit persons to whom the Software ni furnished to do so, subject to
# the following conditions:
#
# The above copyright notice na this permission notice shall be
# included kwenye all copies ama substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
Tests kila epoll wrapper.
"""
agiza errno
agiza os
agiza select
agiza socket
agiza time
agiza unittest

ikiwa sio hasattr(select, "epoll"):
    ashiria unittest.SkipTest("test works only on Linux 2.6")

jaribu:
    select.epoll()
tatizo OSError kama e:
    ikiwa e.errno == errno.ENOSYS:
        ashiria unittest.SkipTest("kernel doesn't support epoll()")
    raise

kundi TestEPoll(unittest.TestCase):

    eleza setUp(self):
        self.serverSocket = socket.create_server(('127.0.0.1', 0))
        self.connections = [self.serverSocket]

    eleza tearDown(self):
        kila skt kwenye self.connections:
            skt.close()

    eleza _connected_pair(self):
        client = socket.socket()
        client.setblocking(Uongo)
        jaribu:
            client.connect(('127.0.0.1', self.serverSocket.getsockname()[1]))
        tatizo OSError kama e:
            self.assertEqual(e.args[0], errno.EINPROGRESS)
        isipokua:
            ashiria AssertionError("Connect should have raised EINPROGRESS")
        server, addr = self.serverSocket.accept()

        self.connections.extend((client, server))
        rudisha client, server

    eleza test_create(self):
        jaribu:
            ep = select.epoll(16)
        tatizo OSError kama e:
            ashiria AssertionError(str(e))
        self.assertKweli(ep.fileno() > 0, ep.fileno())
        self.assertKweli(sio ep.closed)
        ep.close()
        self.assertKweli(ep.closed)
        self.assertRaises(ValueError, ep.fileno)

        ikiwa hasattr(select, "EPOLL_CLOEXEC"):
            select.epoll(-1, select.EPOLL_CLOEXEC).close()
            select.epoll(flags=select.EPOLL_CLOEXEC).close()
            select.epoll(flags=0).close()

    eleza test_badcreate(self):
        self.assertRaises(TypeError, select.epoll, 1, 2, 3)
        self.assertRaises(TypeError, select.epoll, 'foo')
        self.assertRaises(TypeError, select.epoll, Tupu)
        self.assertRaises(TypeError, select.epoll, ())
        self.assertRaises(TypeError, select.epoll, ['foo'])
        self.assertRaises(TypeError, select.epoll, {})

        self.assertRaises(ValueError, select.epoll, 0)
        self.assertRaises(ValueError, select.epoll, -2)
        self.assertRaises(ValueError, select.epoll, sizehint=-2)

        ikiwa hasattr(select, "EPOLL_CLOEXEC"):
            self.assertRaises(OSError, select.epoll, flags=12356)

    eleza test_context_manager(self):
        ukijumuisha select.epoll(16) kama ep:
            self.assertGreater(ep.fileno(), 0)
            self.assertUongo(ep.closed)
        self.assertKweli(ep.closed)
        self.assertRaises(ValueError, ep.fileno)

    eleza test_add(self):
        server, client = self._connected_pair()

        ep = select.epoll(2)
        jaribu:
            ep.register(server.fileno(), select.EPOLLIN | select.EPOLLOUT)
            ep.register(client.fileno(), select.EPOLLIN | select.EPOLLOUT)
        mwishowe:
            ep.close()

        # adding by object w/ fileno works, too.
        ep = select.epoll(2)
        jaribu:
            ep.register(server, select.EPOLLIN | select.EPOLLOUT)
            ep.register(client, select.EPOLLIN | select.EPOLLOUT)
        mwishowe:
            ep.close()

        ep = select.epoll(2)
        jaribu:
            # TypeError: argument must be an int, ama have a fileno() method.
            self.assertRaises(TypeError, ep.register, object(),
                              select.EPOLLIN | select.EPOLLOUT)
            self.assertRaises(TypeError, ep.register, Tupu,
                              select.EPOLLIN | select.EPOLLOUT)
            # ValueError: file descriptor cansio be a negative integer (-1)
            self.assertRaises(ValueError, ep.register, -1,
                              select.EPOLLIN | select.EPOLLOUT)
            # OSError: [Errno 9] Bad file descriptor
            self.assertRaises(OSError, ep.register, 10000,
                              select.EPOLLIN | select.EPOLLOUT)
            # registering twice also raises an exception
            ep.register(server, select.EPOLLIN | select.EPOLLOUT)
            self.assertRaises(OSError, ep.register, server,
                              select.EPOLLIN | select.EPOLLOUT)
        mwishowe:
            ep.close()

    eleza test_fromfd(self):
        server, client = self._connected_pair()

        ukijumuisha select.epoll(2) kama ep:
            ep2 = select.epoll.fromfd(ep.fileno())

            ep2.register(server.fileno(), select.EPOLLIN | select.EPOLLOUT)
            ep2.register(client.fileno(), select.EPOLLIN | select.EPOLLOUT)

            events = ep.poll(1, 4)
            events2 = ep2.poll(0.9, 4)
            self.assertEqual(len(events), 2)
            self.assertEqual(len(events2), 2)

        jaribu:
            ep2.poll(1, 4)
        tatizo OSError kama e:
            self.assertEqual(e.args[0], errno.EBADF, e)
        isipokua:
            self.fail("epoll on closed fd didn't ashiria EBADF")

    eleza test_control_and_wait(self):
        client, server = self._connected_pair()

        ep = select.epoll(16)
        ep.register(server.fileno(),
                    select.EPOLLIN | select.EPOLLOUT | select.EPOLLET)
        ep.register(client.fileno(),
                    select.EPOLLIN | select.EPOLLOUT | select.EPOLLET)

        now = time.monotonic()
        events = ep.poll(1, 4)
        then = time.monotonic()
        self.assertUongo(then - now > 0.1, then - now)

        events.sort()
        expected = [(client.fileno(), select.EPOLLOUT),
                    (server.fileno(), select.EPOLLOUT)]
        expected.sort()

        self.assertEqual(events, expected)

        events = ep.poll(timeout=2.1, maxevents=4)
        self.assertUongo(events)

        client.send(b"Hello!")
        server.send(b"world!!!")

        now = time.monotonic()
        events = ep.poll(1, 4)
        then = time.monotonic()
        self.assertUongo(then - now > 0.01)

        events.sort()
        expected = [(client.fileno(), select.EPOLLIN | select.EPOLLOUT),
                    (server.fileno(), select.EPOLLIN | select.EPOLLOUT)]
        expected.sort()

        self.assertEqual(events, expected)

        ep.unregister(client.fileno())
        ep.modify(server.fileno(), select.EPOLLOUT)
        now = time.monotonic()
        events = ep.poll(1, 4)
        then = time.monotonic()
        self.assertUongo(then - now > 0.01)

        expected = [(server.fileno(), select.EPOLLOUT)]
        self.assertEqual(events, expected)

    eleza test_errors(self):
        self.assertRaises(ValueError, select.epoll, -2)
        self.assertRaises(ValueError, select.epoll().register, -1,
                          select.EPOLLIN)

    eleza test_unregister_closed(self):
        server, client = self._connected_pair()
        fd = server.fileno()
        ep = select.epoll(16)
        ep.register(server)

        now = time.monotonic()
        events = ep.poll(1, 4)
        then = time.monotonic()
        self.assertUongo(then - now > 0.01)

        server.close()
        ep.unregister(fd)

    eleza test_close(self):
        open_file = open(__file__, "rb")
        self.addCleanup(open_file.close)
        fd = open_file.fileno()
        epoll = select.epoll()

        # test fileno() method na closed attribute
        self.assertIsInstance(epoll.fileno(), int)
        self.assertUongo(epoll.closed)

        # test close()
        epoll.close()
        self.assertKweli(epoll.closed)
        self.assertRaises(ValueError, epoll.fileno)

        # close() can be called more than once
        epoll.close()

        # operations must fail ukijumuisha ValueError("I/O operation on closed ...")
        self.assertRaises(ValueError, epoll.modify, fd, select.EPOLLIN)
        self.assertRaises(ValueError, epoll.poll, 1.0)
        self.assertRaises(ValueError, epoll.register, fd, select.EPOLLIN)
        self.assertRaises(ValueError, epoll.unregister, fd)

    eleza test_fd_non_inheritable(self):
        epoll = select.epoll()
        self.addCleanup(epoll.close)
        self.assertEqual(os.get_inheritable(epoll.fileno()), Uongo)


ikiwa __name__ == "__main__":
    unittest.main()
