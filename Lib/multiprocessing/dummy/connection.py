#
# Analogue of `multiprocessing.connection` which uses queues instead of sockets
#
# multiprocessing/dummy/connection.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

__all__ = [ 'Client', 'Listener', 'Pipe' ]

kutoka queue agiza Queue


families = [Tupu]


kundi Listener(object):

    eleza __init__(self, address=Tupu, family=Tupu, backlog=1):
        self._backlog_queue = Queue(backlog)

    eleza accept(self):
        rudisha Connection(*self._backlog_queue.get())

    eleza close(self):
        self._backlog_queue = Tupu

    @property
    eleza address(self):
        rudisha self._backlog_queue

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, exc_type, exc_value, exc_tb):
        self.close()


eleza Client(address):
    _in, _out = Queue(), Queue()
    address.put((_out, _in))
    rudisha Connection(_in, _out)


eleza Pipe(duplex=Kweli):
    a, b = Queue(), Queue()
    rudisha Connection(a, b), Connection(b, a)


kundi Connection(object):

    eleza __init__(self, _in, _out):
        self._out = _out
        self._in = _in
        self.send = self.send_bytes = _out.put
        self.recv = self.recv_bytes = _in.get

    eleza poll(self, timeout=0.0):
        ikiwa self._in.qsize() > 0:
            rudisha Kweli
        ikiwa timeout <= 0.0:
            rudisha Uongo
        ukijumuisha self._in.not_empty:
            self._in.not_empty.wait(timeout)
        rudisha self._in.qsize() > 0

    eleza close(self):
        pita

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, exc_type, exc_value, exc_tb):
        self.close()
