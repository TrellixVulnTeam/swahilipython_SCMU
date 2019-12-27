# -*- Mode: Python -*-
#   Id: asyncore.py,v 2.51 2000/09/07 22:29:26 rushing Exp
#   Author: Sam Rushing <rushing@nightmare.com>

# ======================================================================
# Copyright 1996 by Sam Rushing
#
#                         All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby
# granted, provided that the above copyright notice appear in all
# copies and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of Sam
# Rushing not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission.
#
# SAM RUSHING DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
# NO EVENT SHALL SAM RUSHING BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# ======================================================================

"""Basic infrastructure for asynchronous socket service clients and servers.

There are only two ways to have a program on a single processor do "more
than one thing at a time".  Multi-threaded programming is the simplest and
most popular way to do it, but there is another very different technique,
that lets you have nearly all the advantages of multi-threading, without
actually using multiple threads. it's really only practical ikiwa your program
is largely I/O bound. If your program is CPU bound, then pre-emptive
scheduled threads are probably what you really need. Network servers are
rarely CPU-bound, however.

If your operating system supports the select() system call in its I/O
library (and nearly all do), then you can use it to juggle multiple
communication channels at once; doing other work while your I/O is taking
place in the "background."  Although this strategy can seem strange and
complex, especially at first, it is in many ways easier to understand and
control than multi-threaded programming. The module documented here solves
many of the difficult problems for you, making the task of building
sophisticated high-performance network servers and clients a snap.
"""

agiza select
agiza socket
agiza sys
agiza time
agiza warnings

agiza os
kutoka errno agiza EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, EINVAL, \
     ENOTCONN, ESHUTDOWN, EISCONN, EBADF, ECONNABORTED, EPIPE, EAGAIN, \
     errorcode

_DISCONNECTED = frozenset({ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED, EPIPE,
                           EBADF})

try:
    socket_map
except NameError:
    socket_map = {}

eleza _strerror(err):
    try:
        rudisha os.strerror(err)
    except (ValueError, OverflowError, NameError):
        ikiwa err in errorcode:
            rudisha errorcode[err]
        rudisha "Unknown error %s" %err

kundi ExitNow(Exception):
    pass

_reraised_exceptions = (ExitNow, KeyboardInterrupt, SystemExit)

eleza read(obj):
    try:
        obj.handle_read_event()
    except _reraised_exceptions:
        raise
    except:
        obj.handle_error()

eleza write(obj):
    try:
        obj.handle_write_event()
    except _reraised_exceptions:
        raise
    except:
        obj.handle_error()

eleza _exception(obj):
    try:
        obj.handle_expt_event()
    except _reraised_exceptions:
        raise
    except:
        obj.handle_error()

eleza readwrite(obj, flags):
    try:
        ikiwa flags & select.POLLIN:
            obj.handle_read_event()
        ikiwa flags & select.POLLOUT:
            obj.handle_write_event()
        ikiwa flags & select.POLLPRI:
            obj.handle_expt_event()
        ikiwa flags & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
            obj.handle_close()
    except OSError as e:
        ikiwa e.args[0] not in _DISCONNECTED:
            obj.handle_error()
        else:
            obj.handle_close()
    except _reraised_exceptions:
        raise
    except:
        obj.handle_error()

eleza poll(timeout=0.0, map=None):
    ikiwa map is None:
        map = socket_map
    ikiwa map:
        r = []; w = []; e = []
        for fd, obj in list(map.items()):
            is_r = obj.readable()
            is_w = obj.writable()
            ikiwa is_r:
                r.append(fd)
            # accepting sockets should not be writable
            ikiwa is_w and not obj.accepting:
                w.append(fd)
            ikiwa is_r or is_w:
                e.append(fd)
        ikiwa [] == r == w == e:
            time.sleep(timeout)
            return

        r, w, e = select.select(r, w, e, timeout)

        for fd in r:
            obj = map.get(fd)
            ikiwa obj is None:
                continue
            read(obj)

        for fd in w:
            obj = map.get(fd)
            ikiwa obj is None:
                continue
            write(obj)

        for fd in e:
            obj = map.get(fd)
            ikiwa obj is None:
                continue
            _exception(obj)

eleza poll2(timeout=0.0, map=None):
    # Use the poll() support added to the select module in Python 2.0
    ikiwa map is None:
        map = socket_map
    ikiwa timeout is not None:
        # timeout is in milliseconds
        timeout = int(timeout*1000)
    pollster = select.poll()
    ikiwa map:
        for fd, obj in list(map.items()):
            flags = 0
            ikiwa obj.readable():
                flags |= select.POLLIN | select.POLLPRI
            # accepting sockets should not be writable
            ikiwa obj.writable() and not obj.accepting:
                flags |= select.POLLOUT
            ikiwa flags:
                pollster.register(fd, flags)

        r = pollster.poll(timeout)
        for fd, flags in r:
            obj = map.get(fd)
            ikiwa obj is None:
                continue
            readwrite(obj, flags)

poll3 = poll2                           # Alias for backward compatibility

eleza loop(timeout=30.0, use_poll=False, map=None, count=None):
    ikiwa map is None:
        map = socket_map

    ikiwa use_poll and hasattr(select, 'poll'):
        poll_fun = poll2
    else:
        poll_fun = poll

    ikiwa count is None:
        while map:
            poll_fun(timeout, map)

    else:
        while map and count > 0:
            poll_fun(timeout, map)
            count = count - 1

kundi dispatcher:

    debug = False
    connected = False
    accepting = False
    connecting = False
    closing = False
    addr = None
    ignore_log_types = frozenset({'warning'})

    eleza __init__(self, sock=None, map=None):
        ikiwa map is None:
            self._map = socket_map
        else:
            self._map = map

        self._fileno = None

        ikiwa sock:
            # Set to nonblocking just to make sure for cases where we
            # get a socket kutoka a blocking source.
            sock.setblocking(0)
            self.set_socket(sock, map)
            self.connected = True
            # The constructor no longer requires that the socket
            # passed be connected.
            try:
                self.addr = sock.getpeername()
            except OSError as err:
                ikiwa err.args[0] in (ENOTCONN, EINVAL):
                    # To handle the case where we got an unconnected
                    # socket.
                    self.connected = False
                else:
                    # The socket is broken in some unknown way, alert
                    # the user and remove it kutoka the map (to prevent
                    # polling of broken sockets).
                    self.del_channel(map)
                    raise
        else:
            self.socket = None

    eleza __repr__(self):
        status = [self.__class__.__module__+"."+self.__class__.__qualname__]
        ikiwa self.accepting and self.addr:
            status.append('listening')
        elikiwa self.connected:
            status.append('connected')
        ikiwa self.addr is not None:
            try:
                status.append('%s:%d' % self.addr)
            except TypeError:
                status.append(repr(self.addr))
        rudisha '<%s at %#x>' % (' '.join(status), id(self))

    eleza add_channel(self, map=None):
        #self.log_info('adding channel %s' % self)
        ikiwa map is None:
            map = self._map
        map[self._fileno] = self

    eleza del_channel(self, map=None):
        fd = self._fileno
        ikiwa map is None:
            map = self._map
        ikiwa fd in map:
            #self.log_info('closing channel %d:%s' % (fd, self))
            del map[fd]
        self._fileno = None

    eleza create_socket(self, family=socket.AF_INET, type=socket.SOCK_STREAM):
        self.family_and_type = family, type
        sock = socket.socket(family, type)
        sock.setblocking(0)
        self.set_socket(sock)

    eleza set_socket(self, sock, map=None):
        self.socket = sock
        self._fileno = sock.fileno()
        self.add_channel(map)

    eleza set_reuse_addr(self):
        # try to re-use a server port ikiwa possible
        try:
            self.socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR,
                self.socket.getsockopt(socket.SOL_SOCKET,
                                       socket.SO_REUSEADDR) | 1
                )
        except OSError:
            pass

    # ==================================================
    # predicates for select()
    # these are used as filters for the lists of sockets
    # to pass to select().
    # ==================================================

    eleza readable(self):
        rudisha True

    eleza writable(self):
        rudisha True

    # ==================================================
    # socket object methods.
    # ==================================================

    eleza listen(self, num):
        self.accepting = True
        ikiwa os.name == 'nt' and num > 5:
            num = 5
        rudisha self.socket.listen(num)

    eleza bind(self, addr):
        self.addr = addr
        rudisha self.socket.bind(addr)

    eleza connect(self, address):
        self.connected = False
        self.connecting = True
        err = self.socket.connect_ex(address)
        ikiwa err in (EINPROGRESS, EALREADY, EWOULDBLOCK) \
        or err == EINVAL and os.name == 'nt':
            self.addr = address
            return
        ikiwa err in (0, EISCONN):
            self.addr = address
            self.handle_connect_event()
        else:
            raise OSError(err, errorcode[err])

    eleza accept(self):
        # XXX can rudisha either an address pair or None
        try:
            conn, addr = self.socket.accept()
        except TypeError:
            rudisha None
        except OSError as why:
            ikiwa why.args[0] in (EWOULDBLOCK, ECONNABORTED, EAGAIN):
                rudisha None
            else:
                raise
        else:
            rudisha conn, addr

    eleza send(self, data):
        try:
            result = self.socket.send(data)
            rudisha result
        except OSError as why:
            ikiwa why.args[0] == EWOULDBLOCK:
                rudisha 0
            elikiwa why.args[0] in _DISCONNECTED:
                self.handle_close()
                rudisha 0
            else:
                raise

    eleza recv(self, buffer_size):
        try:
            data = self.socket.recv(buffer_size)
            ikiwa not data:
                # a closed connection is indicated by signaling
                # a read condition, and having recv() rudisha 0.
                self.handle_close()
                rudisha b''
            else:
                rudisha data
        except OSError as why:
            # winsock sometimes raises ENOTCONN
            ikiwa why.args[0] in _DISCONNECTED:
                self.handle_close()
                rudisha b''
            else:
                raise

    eleza close(self):
        self.connected = False
        self.accepting = False
        self.connecting = False
        self.del_channel()
        ikiwa self.socket is not None:
            try:
                self.socket.close()
            except OSError as why:
                ikiwa why.args[0] not in (ENOTCONN, EBADF):
                    raise

    # log and log_info may be overridden to provide more sophisticated
    # logging and warning methods. In general, log is for 'hit' logging
    # and 'log_info' is for informational, warning and error logging.

    eleza log(self, message):
        sys.stderr.write('log: %s\n' % str(message))

    eleza log_info(self, message, type='info'):
        ikiwa type not in self.ignore_log_types:
            andika('%s: %s' % (type, message))

    eleza handle_read_event(self):
        ikiwa self.accepting:
            # accepting sockets are never connected, they "spawn" new
            # sockets that are connected
            self.handle_accept()
        elikiwa not self.connected:
            ikiwa self.connecting:
                self.handle_connect_event()
            self.handle_read()
        else:
            self.handle_read()

    eleza handle_connect_event(self):
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        ikiwa err != 0:
            raise OSError(err, _strerror(err))
        self.handle_connect()
        self.connected = True
        self.connecting = False

    eleza handle_write_event(self):
        ikiwa self.accepting:
            # Accepting sockets shouldn't get a write event.
            # We will pretend it didn't happen.
            return

        ikiwa not self.connected:
            ikiwa self.connecting:
                self.handle_connect_event()
        self.handle_write()

    eleza handle_expt_event(self):
        # handle_expt_event() is called ikiwa there might be an error on the
        # socket, or ikiwa there is OOB data
        # check for the error condition first
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        ikiwa err != 0:
            # we can get here when select.select() says that there is an
            # exceptional condition on the socket
            # since there is an error, we'll go ahead and close the socket
            # like we would in a subclassed handle_read() that received no
            # data
            self.handle_close()
        else:
            self.handle_expt()

    eleza handle_error(self):
        nil, t, v, tbinfo = compact_traceback()

        # sometimes a user repr method will crash.
        try:
            self_repr = repr(self)
        except:
            self_repr = '<__repr__(self) failed for object at %0x>' % id(self)

        self.log_info(
            'uncaptured python exception, closing channel %s (%s:%s %s)' % (
                self_repr,
                t,
                v,
                tbinfo
                ),
            'error'
            )
        self.handle_close()

    eleza handle_expt(self):
        self.log_info('unhandled incoming priority event', 'warning')

    eleza handle_read(self):
        self.log_info('unhandled read event', 'warning')

    eleza handle_write(self):
        self.log_info('unhandled write event', 'warning')

    eleza handle_connect(self):
        self.log_info('unhandled connect event', 'warning')

    eleza handle_accept(self):
        pair = self.accept()
        ikiwa pair is not None:
            self.handle_accepted(*pair)

    eleza handle_accepted(self, sock, addr):
        sock.close()
        self.log_info('unhandled accepted event', 'warning')

    eleza handle_close(self):
        self.log_info('unhandled close event', 'warning')
        self.close()

# ---------------------------------------------------------------------------
# adds simple buffered output capability, useful for simple clients.
# [for more sophisticated usage use asynchat.async_chat]
# ---------------------------------------------------------------------------

kundi dispatcher_with_send(dispatcher):

    eleza __init__(self, sock=None, map=None):
        dispatcher.__init__(self, sock, map)
        self.out_buffer = b''

    eleza initiate_send(self):
        num_sent = 0
        num_sent = dispatcher.send(self, self.out_buffer[:65536])
        self.out_buffer = self.out_buffer[num_sent:]

    eleza handle_write(self):
        self.initiate_send()

    eleza writable(self):
        rudisha (not self.connected) or len(self.out_buffer)

    eleza send(self, data):
        ikiwa self.debug:
            self.log_info('sending %s' % repr(data))
        self.out_buffer = self.out_buffer + data
        self.initiate_send()

# ---------------------------------------------------------------------------
# used for debugging.
# ---------------------------------------------------------------------------

eleza compact_traceback():
    t, v, tb = sys.exc_info()
    tbinfo = []
    ikiwa not tb: # Must have a traceback
        raise AssertionError("traceback does not exist")
    while tb:
        tbinfo.append((
            tb.tb_frame.f_code.co_filename,
            tb.tb_frame.f_code.co_name,
            str(tb.tb_lineno)
            ))
        tb = tb.tb_next

    # just to be safe
    del tb

    file, function, line = tbinfo[-1]
    info = ' '.join(['[%s|%s|%s]' % x for x in tbinfo])
    rudisha (file, function, line), t, v, info

eleza close_all(map=None, ignore_all=False):
    ikiwa map is None:
        map = socket_map
    for x in list(map.values()):
        try:
            x.close()
        except OSError as x:
            ikiwa x.args[0] == EBADF:
                pass
            elikiwa not ignore_all:
                raise
        except _reraised_exceptions:
            raise
        except:
            ikiwa not ignore_all:
                raise
    map.clear()

# Asynchronous File I/O:
#
# After a little research (reading man pages on various unixen, and
# digging through the linux kernel), I've determined that select()
# isn't meant for doing asynchronous file i/o.
# Heartening, though - reading linux/mm/filemap.c shows that linux
# supports asynchronous read-ahead.  So _MOST_ of the time, the data
# will be sitting in memory for us already when we go to read it.
#
# What other OS's (besides NT) support async file i/o?  [VMS?]
#
# Regardless, this is useful for pipes, and stdin/stdout...

ikiwa os.name == 'posix':
    kundi file_wrapper:
        # Here we override just enough to make a file
        # look like a socket for the purposes of asyncore.
        # The passed fd is automatically os.dup()'d

        eleza __init__(self, fd):
            self.fd = os.dup(fd)

        eleza __del__(self):
            ikiwa self.fd >= 0:
                warnings.warn("unclosed file %r" % self, ResourceWarning,
                              source=self)
            self.close()

        eleza recv(self, *args):
            rudisha os.read(self.fd, *args)

        eleza send(self, *args):
            rudisha os.write(self.fd, *args)

        eleza getsockopt(self, level, optname, buflen=None):
            ikiwa (level == socket.SOL_SOCKET and
                optname == socket.SO_ERROR and
                not buflen):
                rudisha 0
            raise NotImplementedError("Only asyncore specific behaviour "
                                      "implemented.")

        read = recv
        write = send

        eleza close(self):
            ikiwa self.fd < 0:
                return
            fd = self.fd
            self.fd = -1
            os.close(fd)

        eleza fileno(self):
            rudisha self.fd

    kundi file_dispatcher(dispatcher):

        eleza __init__(self, fd, map=None):
            dispatcher.__init__(self, None, map)
            self.connected = True
            try:
                fd = fd.fileno()
            except AttributeError:
                pass
            self.set_file(fd)
            # set it to non-blocking mode
            os.set_blocking(fd, False)

        eleza set_file(self, fd):
            self.socket = file_wrapper(fd)
            self._fileno = self.socket.fileno()
            self.add_channel()
