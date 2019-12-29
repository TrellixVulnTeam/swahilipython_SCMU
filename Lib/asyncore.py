# -*- Mode: Python -*-
#   Id: asyncore.py,v 2.51 2000/09/07 22:29:26 rushing Exp
#   Author: Sam Rushing <rushing@nightmare.com>

# ======================================================================
# Copyright 1996 by Sam Rushing
#
#                         All Rights Reserved
#
# Permission to use, copy, modify, na distribute this software and
# its documentation kila any purpose na without fee ni hereby
# granted, provided that the above copyright notice appear kwenye all
# copies na that both that copyright notice na this permission
# notice appear kwenye supporting documentation, na that the name of Sam
# Rushing sio be used kwenye advertising ama publicity pertaining to
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

"""Basic infrastructure kila asynchronous socket service clients na servers.

There are only two ways to have a program on a single processor do "more
than one thing at a time".  Multi-threaded programming ni the simplest and
most popular way to do it, but there ni another very different technique,
that lets you have nearly all the advantages of multi-threading, without
actually using multiple threads. it's really only practical ikiwa your program
is largely I/O bound. If your program ni CPU bound, then pre-emptive
scheduled threads are probably what you really need. Network servers are
rarely CPU-bound, however.

If your operating system supports the select() system call kwenye its I/O
library (and nearly all do), then you can use it to juggle multiple
communication channels at once; doing other work wakati your I/O ni taking
place kwenye the "background."  Although this strategy can seem strange and
complex, especially at first, it ni kwenye many ways easier to understand and
control than multi-threaded programming. The module documented here solves
many of the difficult problems kila you, making the task of building
sophisticated high-performance network servers na clients a snap.
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

jaribu:
    socket_map
tatizo NameError:
    socket_map = {}

eleza _strerror(err):
    jaribu:
        rudisha os.strerror(err)
    tatizo (ValueError, OverflowError, NameError):
        ikiwa err kwenye errorcode:
            rudisha errorcode[err]
        rudisha "Unknown error %s" %err

kundi ExitNow(Exception):
    pita

_reashiriad_exceptions = (ExitNow, KeyboardInterrupt, SystemExit)

eleza read(obj):
    jaribu:
        obj.handle_read_event()
    tatizo _reashiriad_exceptions:
        ashiria
    except:
        obj.handle_error()

eleza write(obj):
    jaribu:
        obj.handle_write_event()
    tatizo _reashiriad_exceptions:
        ashiria
    except:
        obj.handle_error()

eleza _exception(obj):
    jaribu:
        obj.handle_expt_event()
    tatizo _reashiriad_exceptions:
        ashiria
    except:
        obj.handle_error()

eleza readwrite(obj, flags):
    jaribu:
        ikiwa flags & select.POLLIN:
            obj.handle_read_event()
        ikiwa flags & select.POLLOUT:
            obj.handle_write_event()
        ikiwa flags & select.POLLPRI:
            obj.handle_expt_event()
        ikiwa flags & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
            obj.handle_close()
    tatizo OSError kama e:
        ikiwa e.args[0] haiko kwenye _DISCONNECTED:
            obj.handle_error()
        isipokua:
            obj.handle_close()
    tatizo _reashiriad_exceptions:
        ashiria
    except:
        obj.handle_error()

eleza poll(timeout=0.0, map=Tupu):
    ikiwa map ni Tupu:
        map = socket_map
    ikiwa map:
        r = []; w = []; e = []
        kila fd, obj kwenye list(map.items()):
            is_r = obj.readable()
            is_w = obj.writable()
            ikiwa is_r:
                r.append(fd)
            # accepting sockets should sio be writable
            ikiwa is_w na sio obj.accepting:
                w.append(fd)
            ikiwa is_r ama is_w:
                e.append(fd)
        ikiwa [] == r == w == e:
            time.sleep(timeout)
            rudisha

        r, w, e = select.select(r, w, e, timeout)

        kila fd kwenye r:
            obj = map.get(fd)
            ikiwa obj ni Tupu:
                endelea
            read(obj)

        kila fd kwenye w:
            obj = map.get(fd)
            ikiwa obj ni Tupu:
                endelea
            write(obj)

        kila fd kwenye e:
            obj = map.get(fd)
            ikiwa obj ni Tupu:
                endelea
            _exception(obj)

eleza poll2(timeout=0.0, map=Tupu):
    # Use the poll() support added to the select module kwenye Python 2.0
    ikiwa map ni Tupu:
        map = socket_map
    ikiwa timeout ni sio Tupu:
        # timeout ni kwenye milliseconds
        timeout = int(timeout*1000)
    pollster = select.poll()
    ikiwa map:
        kila fd, obj kwenye list(map.items()):
            flags = 0
            ikiwa obj.readable():
                flags |= select.POLLIN | select.POLLPRI
            # accepting sockets should sio be writable
            ikiwa obj.writable() na sio obj.accepting:
                flags |= select.POLLOUT
            ikiwa flags:
                pollster.register(fd, flags)

        r = pollster.poll(timeout)
        kila fd, flags kwenye r:
            obj = map.get(fd)
            ikiwa obj ni Tupu:
                endelea
            readwrite(obj, flags)

poll3 = poll2                           # Alias kila backward compatibility

eleza loop(timeout=30.0, use_poll=Uongo, map=Tupu, count=Tupu):
    ikiwa map ni Tupu:
        map = socket_map

    ikiwa use_poll na hasattr(select, 'poll'):
        poll_fun = poll2
    isipokua:
        poll_fun = poll

    ikiwa count ni Tupu:
        wakati map:
            poll_fun(timeout, map)

    isipokua:
        wakati map na count > 0:
            poll_fun(timeout, map)
            count = count - 1

kundi dispatcher:

    debug = Uongo
    connected = Uongo
    accepting = Uongo
    connecting = Uongo
    closing = Uongo
    addr = Tupu
    ignore_log_types = frozenset({'warning'})

    eleza __init__(self, sock=Tupu, map=Tupu):
        ikiwa map ni Tupu:
            self._map = socket_map
        isipokua:
            self._map = map

        self._fileno = Tupu

        ikiwa sock:
            # Set to nonblocking just to make sure kila cases where we
            # get a socket kutoka a blocking source.
            sock.setblocking(0)
            self.set_socket(sock, map)
            self.connected = Kweli
            # The constructor no longer requires that the socket
            # pitaed be connected.
            jaribu:
                self.addr = sock.getpeername()
            tatizo OSError kama err:
                ikiwa err.args[0] kwenye (ENOTCONN, EINVAL):
                    # To handle the case where we got an unconnected
                    # socket.
                    self.connected = Uongo
                isipokua:
                    # The socket ni broken kwenye some unknown way, alert
                    # the user na remove it kutoka the map (to prevent
                    # polling of broken sockets).
                    self.del_channel(map)
                    ashiria
        isipokua:
            self.socket = Tupu

    eleza __repr__(self):
        status = [self.__class__.__module__+"."+self.__class__.__qualname__]
        ikiwa self.accepting na self.addr:
            status.append('listening')
        lasivyo self.connected:
            status.append('connected')
        ikiwa self.addr ni sio Tupu:
            jaribu:
                status.append('%s:%d' % self.addr)
            tatizo TypeError:
                status.append(repr(self.addr))
        rudisha '<%s at %#x>' % (' '.join(status), id(self))

    eleza add_channel(self, map=Tupu):
        #self.log_info('adding channel %s' % self)
        ikiwa map ni Tupu:
            map = self._map
        map[self._fileno] = self

    eleza del_channel(self, map=Tupu):
        fd = self._fileno
        ikiwa map ni Tupu:
            map = self._map
        ikiwa fd kwenye map:
            #self.log_info('closing channel %d:%s' % (fd, self))
            toa map[fd]
        self._fileno = Tupu

    eleza create_socket(self, family=socket.AF_INET, type=socket.SOCK_STREAM):
        self.family_and_type = family, type
        sock = socket.socket(family, type)
        sock.setblocking(0)
        self.set_socket(sock)

    eleza set_socket(self, sock, map=Tupu):
        self.socket = sock
        self._fileno = sock.fileno()
        self.add_channel(map)

    eleza set_reuse_addr(self):
        # try to re-use a server port ikiwa possible
        jaribu:
            self.socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR,
                self.socket.getsockopt(socket.SOL_SOCKET,
                                       socket.SO_REUSEADDR) | 1
                )
        tatizo OSError:
            pita

    # ==================================================
    # predicates kila select()
    # these are used kama filters kila the lists of sockets
    # to pita to select().
    # ==================================================

    eleza readable(self):
        rudisha Kweli

    eleza writable(self):
        rudisha Kweli

    # ==================================================
    # socket object methods.
    # ==================================================

    eleza listen(self, num):
        self.accepting = Kweli
        ikiwa os.name == 'nt' na num > 5:
            num = 5
        rudisha self.socket.listen(num)

    eleza bind(self, addr):
        self.addr = addr
        rudisha self.socket.bind(addr)

    eleza connect(self, address):
        self.connected = Uongo
        self.connecting = Kweli
        err = self.socket.connect_ex(address)
        ikiwa err kwenye (EINPROGRESS, EALREADY, EWOULDBLOCK) \
        ama err == EINVAL na os.name == 'nt':
            self.addr = address
            rudisha
        ikiwa err kwenye (0, EISCONN):
            self.addr = address
            self.handle_connect_event()
        isipokua:
            ashiria OSError(err, errorcode[err])

    eleza accept(self):
        # XXX can rudisha either an address pair ama Tupu
        jaribu:
            conn, addr = self.socket.accept()
        tatizo TypeError:
            rudisha Tupu
        tatizo OSError kama why:
            ikiwa why.args[0] kwenye (EWOULDBLOCK, ECONNABORTED, EAGAIN):
                rudisha Tupu
            isipokua:
                ashiria
        isipokua:
            rudisha conn, addr

    eleza send(self, data):
        jaribu:
            result = self.socket.send(data)
            rudisha result
        tatizo OSError kama why:
            ikiwa why.args[0] == EWOULDBLOCK:
                rudisha 0
            lasivyo why.args[0] kwenye _DISCONNECTED:
                self.handle_close()
                rudisha 0
            isipokua:
                ashiria

    eleza recv(self, buffer_size):
        jaribu:
            data = self.socket.recv(buffer_size)
            ikiwa sio data:
                # a closed connection ni indicated by signaling
                # a read condition, na having recv() rudisha 0.
                self.handle_close()
                rudisha b''
            isipokua:
                rudisha data
        tatizo OSError kama why:
            # winsock sometimes ashirias ENOTCONN
            ikiwa why.args[0] kwenye _DISCONNECTED:
                self.handle_close()
                rudisha b''
            isipokua:
                ashiria

    eleza close(self):
        self.connected = Uongo
        self.accepting = Uongo
        self.connecting = Uongo
        self.del_channel()
        ikiwa self.socket ni sio Tupu:
            jaribu:
                self.socket.close()
            tatizo OSError kama why:
                ikiwa why.args[0] haiko kwenye (ENOTCONN, EBADF):
                    ashiria

    # log na log_info may be overridden to provide more sophisticated
    # logging na warning methods. In general, log ni kila 'hit' logging
    # na 'log_info' ni kila informational, warning na error logging.

    eleza log(self, message):
        sys.stderr.write('log: %s\n' % str(message))

    eleza log_info(self, message, type='info'):
        ikiwa type haiko kwenye self.ignore_log_types:
            andika('%s: %s' % (type, message))

    eleza handle_read_event(self):
        ikiwa self.accepting:
            # accepting sockets are never connected, they "spawn" new
            # sockets that are connected
            self.handle_accept()
        lasivyo sio self.connected:
            ikiwa self.connecting:
                self.handle_connect_event()
            self.handle_read()
        isipokua:
            self.handle_read()

    eleza handle_connect_event(self):
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        ikiwa err != 0:
            ashiria OSError(err, _strerror(err))
        self.handle_connect()
        self.connected = Kweli
        self.connecting = Uongo

    eleza handle_write_event(self):
        ikiwa self.accepting:
            # Accepting sockets shouldn't get a write event.
            # We will pretend it didn't happen.
            rudisha

        ikiwa sio self.connected:
            ikiwa self.connecting:
                self.handle_connect_event()
        self.handle_write()

    eleza handle_expt_event(self):
        # handle_expt_event() ni called ikiwa there might be an error on the
        # socket, ama ikiwa there ni OOB data
        # check kila the error condition first
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        ikiwa err != 0:
            # we can get here when select.select() says that there ni an
            # exceptional condition on the socket
            # since there ni an error, we'll go ahead na close the socket
            # like we would kwenye a subclassed handle_read() that received no
            # data
            self.handle_close()
        isipokua:
            self.handle_expt()

    eleza handle_error(self):
        nil, t, v, tbinfo = compact_traceback()

        # sometimes a user repr method will crash.
        jaribu:
            self_repr = repr(self)
        except:
            self_repr = '<__repr__(self) failed kila object at %0x>' % id(self)

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
        ikiwa pair ni sio Tupu:
            self.handle_accepted(*pair)

    eleza handle_accepted(self, sock, addr):
        sock.close()
        self.log_info('unhandled accepted event', 'warning')

    eleza handle_close(self):
        self.log_info('unhandled close event', 'warning')
        self.close()

# ---------------------------------------------------------------------------
# adds simple buffered output capability, useful kila simple clients.
# [kila more sophisticated usage use asynchat.async_chat]
# ---------------------------------------------------------------------------

kundi dispatcher_with_send(dispatcher):

    eleza __init__(self, sock=Tupu, map=Tupu):
        dispatcher.__init__(self, sock, map)
        self.out_buffer = b''

    eleza initiate_send(self):
        num_sent = 0
        num_sent = dispatcher.send(self, self.out_buffer[:65536])
        self.out_buffer = self.out_buffer[num_sent:]

    eleza handle_write(self):
        self.initiate_send()

    eleza writable(self):
        rudisha (not self.connected) ama len(self.out_buffer)

    eleza send(self, data):
        ikiwa self.debug:
            self.log_info('sending %s' % repr(data))
        self.out_buffer = self.out_buffer + data
        self.initiate_send()

# ---------------------------------------------------------------------------
# used kila debugging.
# ---------------------------------------------------------------------------

eleza compact_traceback():
    t, v, tb = sys.exc_info()
    tbinfo = []
    ikiwa sio tb: # Must have a traceback
        ashiria AssertionError("traceback does sio exist")
    wakati tb:
        tbinfo.append((
            tb.tb_frame.f_code.co_filename,
            tb.tb_frame.f_code.co_name,
            str(tb.tb_lineno)
            ))
        tb = tb.tb_next

    # just to be safe
    toa tb

    file, function, line = tbinfo[-1]
    info = ' '.join(['[%s|%s|%s]' % x kila x kwenye tbinfo])
    rudisha (file, function, line), t, v, info

eleza close_all(map=Tupu, ignore_all=Uongo):
    ikiwa map ni Tupu:
        map = socket_map
    kila x kwenye list(map.values()):
        jaribu:
            x.close()
        tatizo OSError kama x:
            ikiwa x.args[0] == EBADF:
                pita
            lasivyo sio ignore_all:
                ashiria
        tatizo _reashiriad_exceptions:
            ashiria
        except:
            ikiwa sio ignore_all:
                ashiria
    map.clear()

# Asynchronous File I/O:
#
# After a little research (reading man pages on various unixen, and
# digging through the linux kernel), I've determined that select()
# isn't meant kila doing asynchronous file i/o.
# Heartening, though - reading linux/mm/filemap.c shows that linux
# supports asynchronous read-ahead.  So _MOST_ of the time, the data
# will be sitting kwenye memory kila us already when we go to read it.
#
# What other OS's (besides NT) support async file i/o?  [VMS?]
#
# Regardless, this ni useful kila pipes, na stdin/stdout...

ikiwa os.name == 'posix':
    kundi file_wrapper:
        # Here we override just enough to make a file
        # look like a socket kila the purposes of asyncore.
        # The pitaed fd ni automatically os.dup()'d

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

        eleza getsockopt(self, level, optname, buflen=Tupu):
            ikiwa (level == socket.SOL_SOCKET and
                optname == socket.SO_ERROR and
                sio buflen):
                rudisha 0
            ashiria NotImplementedError("Only asyncore specific behaviour "
                                      "implemented.")

        read = recv
        write = send

        eleza close(self):
            ikiwa self.fd < 0:
                rudisha
            fd = self.fd
            self.fd = -1
            os.close(fd)

        eleza fileno(self):
            rudisha self.fd

    kundi file_dispatcher(dispatcher):

        eleza __init__(self, fd, map=Tupu):
            dispatcher.__init__(self, Tupu, map)
            self.connected = Kweli
            jaribu:
                fd = fd.fileno()
            tatizo AttributeError:
                pita
            self.set_file(fd)
            # set it to non-blocking mode
            os.set_blocking(fd, Uongo)

        eleza set_file(self, fd):
            self.socket = file_wrapper(fd)
            self._fileno = self.socket.fileno()
            self.add_channel()
