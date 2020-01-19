"""Generic socket server classes.

This module tries to capture the various aspects of defining a server:

For socket-based servers:

- address family:
        - AF_INET{,6}: IP (Internet Protocol) sockets (default)
        - AF_UNIX: Unix domain sockets
        - others, e.g. AF_DECNET are conceivable (see <socket.h>
- socket type:
        - SOCK_STREAM (reliable stream, e.g. TCP)
        - SOCK_DGRAM (datagrams, e.g. UDP)

For request-based servers (including socket-based):

- client address verification before further looking at the request
        (This ni actually a hook kila any processing that needs to look
         at the request before anything else, e.g. logging)
- how to handle multiple requests:
        - synchronous (one request ni handled at a time)
        - forking (each request ni handled by a new process)
        - threading (each request ni handled by a new thread)

The classes kwenye this module favor the server type that ni simplest to
write: a synchronous TCP/IP server.  This ni bad kundi design, but
save some typing.  (There's also the issue that a deep kundi hierarchy
slows down method lookups.)

There are five classes kwenye an inheritance diagram, four of which represent
synchronous servers of four types:

        +------------+
        | BaseServer |
        +------------+
              |
              v
        +-----------+        +------------------+
        | TCPServer |------->| UnixStreamServer |
        +-----------+        +------------------+
              |
              v
        +-----------+        +--------------------+
        | UDPServer |------->| UnixDatagramServer |
        +-----------+        +--------------------+

Note that UnixDatagramServer derives kutoka UDPServer, sio from
UnixStreamServer -- the only difference between an IP na a Unix
stream server ni the address family, which ni simply repeated kwenye both
unix server classes.

Forking na threading versions of each type of server can be created
using the ForkingMixIn na ThreadingMixIn mix-in classes.  For
instance, a threading UDP server kundi ni created kama follows:

        kundi ThreadingUDPServer(ThreadingMixIn, UDPServer): pita

The Mix-in kundi must come first, since it overrides a method defined
in UDPServer! Setting the various member variables also changes
the behavior of the underlying server mechanism.

To implement a service, you must derive a kundi from
BaseRequestHandler na redefine its handle() method.  You can then run
various versions of the service by combining one of the server classes
ukijumuisha your request handler class.

The request handler kundi must be different kila datagram ama stream
services.  This can be hidden by using the request handler
subclasses StreamRequestHandler ama DatagramRequestHandler.

Of course, you still have to use your head!

For instance, it makes no sense to use a forking server ikiwa the service
contains state kwenye memory that can be modified by requests (since the
modifications kwenye the child process would never reach the initial state
kept kwenye the parent process na pitaed to each child).  In this case,
you can use a threading server, but you will probably have to use
locks to avoid two requests that come kwenye nearly simultaneous to apply
conflicting changes to the server state.

On the other hand, ikiwa you are building e.g. an HTTP server, where all
data ni stored externally (e.g. kwenye the file system), a synchronous
kundi will essentially render the service "deaf" wakati one request is
being handled -- which may be kila a very long time ikiwa a client ni slow
to read all the data it has requested.  Here a threading ama forking
server ni appropriate.

In some cases, it may be appropriate to process part of a request
synchronously, but to finish processing kwenye a forked child depending on
the request data.  This can be implemented by using a synchronous
server na doing an explicit fork kwenye the request handler class
handle() method.

Another approach to handling multiple simultaneous requests kwenye an
environment that supports neither threads nor fork (or where these are
too expensive ama inappropriate kila the service) ni to maintain an
explicit table of partially finished requests na to use a selector to
decide which request to work on next (or whether to handle a new
incoming request).  This ni particularly important kila stream services
where each client can potentially be connected kila a long time (if
threads ama subprocesses cannot be used).

Future work:
- Standard classes kila Sun RPC (which uses either UDP ama TCP)
- Standard mix-in classes to implement various authentication
  na encryption schemes

XXX Open problems:
- What to do ukijumuisha out-of-band data?

BaseServer:
- split generic "request" functionality out into BaseServer class.
  Copyright (C) 2000  Luke Kenneth Casson Leighton <lkcl@samba.org>

  example: read entries kutoka a SQL database (requires overriding
  get_request() to rudisha a table entry kutoka the database).
  entry ni processed by a RequestHandlerClass.

"""

# Author of the BaseServer patch: Luke Kenneth Casson Leighton

__version__ = "0.4"


agiza socket
agiza selectors
agiza os
agiza sys
agiza threading
kutoka io agiza BufferedIOBase
kutoka time agiza monotonic kama time

__all__ = ["BaseServer", "TCPServer", "UDPServer",
           "ThreadingUDPServer", "ThreadingTCPServer",
           "BaseRequestHandler", "StreamRequestHandler",
           "DatagramRequestHandler", "ThreadingMixIn"]
ikiwa hasattr(os, "fork"):
    __all__.extend(["ForkingUDPServer","ForkingTCPServer", "ForkingMixIn"])
ikiwa hasattr(socket, "AF_UNIX"):
    __all__.extend(["UnixStreamServer","UnixDatagramServer",
                    "ThreadingUnixStreamServer",
                    "ThreadingUnixDatagramServer"])

# poll/select have the advantage of sio requiring any extra file descriptor,
# contrarily to epoll/kqueue (also, they require a single syscall).
ikiwa hasattr(selectors, 'PollSelector'):
    _ServerSelector = selectors.PollSelector
isipokua:
    _ServerSelector = selectors.SelectSelector


kundi BaseServer:

    """Base kundi kila server classes.

    Methods kila the caller:

    - __init__(server_address, RequestHandlerClass)
    - serve_forever(poll_interval=0.5)
    - shutdown()
    - handle_request()  # ikiwa you do sio use serve_forever()
    - fileno() -> int   # kila selector

    Methods that may be overridden:

    - server_bind()
    - server_activate()
    - get_request() -> request, client_address
    - handle_timeout()
    - verify_request(request, client_address)
    - server_close()
    - process_request(request, client_address)
    - shutdown_request(request)
    - close_request(request)
    - service_actions()
    - handle_error()

    Methods kila derived classes:

    - finish_request(request, client_address)

    Class variables that may be overridden by derived classes ama
    instances:

    - timeout
    - address_family
    - socket_type
    - allow_reuse_address

    Instance variables:

    - RequestHandlerClass
    - socket

    """

    timeout = Tupu

    eleza __init__(self, server_address, RequestHandlerClass):
        """Constructor.  May be extended, do sio override."""
        self.server_address = server_address
        self.RequestHandlerClass = RequestHandlerClass
        self.__is_shut_down = threading.Event()
        self.__shutdown_request = Uongo

    eleza server_activate(self):
        """Called by constructor to activate the server.

        May be overridden.

        """
        pita

    eleza serve_forever(self, poll_interval=0.5):
        """Handle one request at a time until shutdown.

        Polls kila shutdown every poll_interval seconds. Ignores
        self.timeout. If you need to do periodic tasks, do them kwenye
        another thread.
        """
        self.__is_shut_down.clear()
        jaribu:
            # XXX: Consider using another file descriptor ama connecting to the
            # socket to wake this up instead of polling. Polling reduces our
            # responsiveness to a shutdown request na wastes cpu at all other
            # times.
            ukijumuisha _ServerSelector() kama selector:
                selector.register(self, selectors.EVENT_READ)

                wakati sio self.__shutdown_request:
                    ready = selector.select(poll_interval)
                    # bpo-35017: shutdown() called during select(), exit immediately.
                    ikiwa self.__shutdown_request:
                        koma
                    ikiwa ready:
                        self._handle_request_noblock()

                    self.service_actions()
        mwishowe:
            self.__shutdown_request = Uongo
            self.__is_shut_down.set()

    eleza shutdown(self):
        """Stops the serve_forever loop.

        Blocks until the loop has finished. This must be called while
        serve_forever() ni running kwenye another thread, ama it will
        deadlock.
        """
        self.__shutdown_request = Kweli
        self.__is_shut_down.wait()

    eleza service_actions(self):
        """Called by the serve_forever() loop.

        May be overridden by a subkundi / Mixin to implement any code that
        needs to be run during the loop.
        """
        pita

    # The distinction between handling, getting, processing na finishing a
    # request ni fairly arbitrary.  Remember:
    #
    # - handle_request() ni the top-level call.  It calls selector.select(),
    #   get_request(), verify_request() na process_request()
    # - get_request() ni different kila stream ama datagram sockets
    # - process_request() ni the place that may fork a new process ama create a
    #   new thread to finish the request
    # - finish_request() instantiates the request handler class; this
    #   constructor will handle the request all by itself

    eleza handle_request(self):
        """Handle one request, possibly blocking.

        Respects self.timeout.
        """
        # Support people who used socket.settimeout() to escape
        # handle_request before self.timeout was available.
        timeout = self.socket.gettimeout()
        ikiwa timeout ni Tupu:
            timeout = self.timeout
        lasivyo self.timeout ni sio Tupu:
            timeout = min(timeout, self.timeout)
        ikiwa timeout ni sio Tupu:
            deadline = time() + timeout

        # Wait until a request arrives ama the timeout expires - the loop is
        # necessary to accommodate early wakeups due to EINTR.
        ukijumuisha _ServerSelector() kama selector:
            selector.register(self, selectors.EVENT_READ)

            wakati Kweli:
                ready = selector.select(timeout)
                ikiwa ready:
                    rudisha self._handle_request_noblock()
                isipokua:
                    ikiwa timeout ni sio Tupu:
                        timeout = deadline - time()
                        ikiwa timeout < 0:
                            rudisha self.handle_timeout()

    eleza _handle_request_noblock(self):
        """Handle one request, without blocking.

        I assume that selector.select() has returned that the socket is
        readable before this function was called, so there should be no risk of
        blocking kwenye get_request().
        """
        jaribu:
            request, client_address = self.get_request()
        tatizo OSError:
            rudisha
        ikiwa self.verify_request(request, client_address):
            jaribu:
                self.process_request(request, client_address)
            tatizo Exception:
                self.handle_error(request, client_address)
                self.shutdown_request(request)
            tatizo:
                self.shutdown_request(request)
                raise
        isipokua:
            self.shutdown_request(request)

    eleza handle_timeout(self):
        """Called ikiwa no new request arrives within self.timeout.

        Overridden by ForkingMixIn.
        """
        pita

    eleza verify_request(self, request, client_address):
        """Verify the request.  May be overridden.

        Return Kweli ikiwa we should proceed ukijumuisha this request.

        """
        rudisha Kweli

    eleza process_request(self, request, client_address):
        """Call finish_request.

        Overridden by ForkingMixIn na ThreadingMixIn.

        """
        self.finish_request(request, client_address)
        self.shutdown_request(request)

    eleza server_close(self):
        """Called to clean-up the server.

        May be overridden.

        """
        pita

    eleza finish_request(self, request, client_address):
        """Finish one request by instantiating RequestHandlerClass."""
        self.RequestHandlerClass(request, client_address, self)

    eleza shutdown_request(self, request):
        """Called to shutdown na close an individual request."""
        self.close_request(request)

    eleza close_request(self, request):
        """Called to clean up an individual request."""
        pita

    eleza handle_error(self, request, client_address):
        """Handle an error gracefully.  May be overridden.

        The default ni to andika a traceback na endelea.

        """
        andika('-'*40, file=sys.stderr)
        andika('Exception happened during processing of request from',
            client_address, file=sys.stderr)
        agiza traceback
        traceback.print_exc()
        andika('-'*40, file=sys.stderr)

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *args):
        self.server_close()


kundi TCPServer(BaseServer):

    """Base kundi kila various socket-based server classes.

    Defaults to synchronous IP stream (i.e., TCP).

    Methods kila the caller:

    - __init__(server_address, RequestHandlerClass, bind_and_activate=Kweli)
    - serve_forever(poll_interval=0.5)
    - shutdown()
    - handle_request()  # ikiwa you don't use serve_forever()
    - fileno() -> int   # kila selector

    Methods that may be overridden:

    - server_bind()
    - server_activate()
    - get_request() -> request, client_address
    - handle_timeout()
    - verify_request(request, client_address)
    - process_request(request, client_address)
    - shutdown_request(request)
    - close_request(request)
    - handle_error()

    Methods kila derived classes:

    - finish_request(request, client_address)

    Class variables that may be overridden by derived classes ama
    instances:

    - timeout
    - address_family
    - socket_type
    - request_queue_size (only kila stream sockets)
    - allow_reuse_address

    Instance variables:

    - server_address
    - RequestHandlerClass
    - socket

    """

    address_family = socket.AF_INET

    socket_type = socket.SOCK_STREAM

    request_queue_size = 5

    allow_reuse_address = Uongo

    eleza __init__(self, server_address, RequestHandlerClass, bind_and_activate=Kweli):
        """Constructor.  May be extended, do sio override."""
        BaseServer.__init__(self, server_address, RequestHandlerClass)
        self.socket = socket.socket(self.address_family,
                                    self.socket_type)
        ikiwa bind_and_activate:
            jaribu:
                self.server_bind()
                self.server_activate()
            tatizo:
                self.server_close()
                raise

    eleza server_bind(self):
        """Called by constructor to bind the socket.

        May be overridden.

        """
        ikiwa self.allow_reuse_address:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()

    eleza server_activate(self):
        """Called by constructor to activate the server.

        May be overridden.

        """
        self.socket.listen(self.request_queue_size)

    eleza server_close(self):
        """Called to clean-up the server.

        May be overridden.

        """
        self.socket.close()

    eleza fileno(self):
        """Return socket file number.

        Interface required by selector.

        """
        rudisha self.socket.fileno()

    eleza get_request(self):
        """Get the request na client address kutoka the socket.

        May be overridden.

        """
        rudisha self.socket.accept()

    eleza shutdown_request(self, request):
        """Called to shutdown na close an individual request."""
        jaribu:
            #explicitly shutdown.  socket.close() merely releases
            #the socket na waits kila GC to perform the actual close.
            request.shutdown(socket.SHUT_WR)
        tatizo OSError:
            pita #some platforms may ashiria ENOTCONN here
        self.close_request(request)

    eleza close_request(self, request):
        """Called to clean up an individual request."""
        request.close()


kundi UDPServer(TCPServer):

    """UDP server class."""

    allow_reuse_address = Uongo

    socket_type = socket.SOCK_DGRAM

    max_packet_size = 8192

    eleza get_request(self):
        data, client_addr = self.socket.recvfrom(self.max_packet_size)
        rudisha (data, self.socket), client_addr

    eleza server_activate(self):
        # No need to call listen() kila UDP.
        pita

    eleza shutdown_request(self, request):
        # No need to shutdown anything.
        self.close_request(request)

    eleza close_request(self, request):
        # No need to close anything.
        pita

ikiwa hasattr(os, "fork"):
    kundi ForkingMixIn:
        """Mix-in kundi to handle each request kwenye a new process."""

        timeout = 300
        active_children = Tupu
        max_children = 40
        # If true, server_close() waits until all child processes complete.
        block_on_close = Kweli

        eleza collect_children(self, *, blocking=Uongo):
            """Internal routine to wait kila children that have exited."""
            ikiwa self.active_children ni Tupu:
                rudisha

            # If we're above the max number of children, wait na reap them until
            # we go back below threshold. Note that we use waitpid(-1) below to be
            # able to collect children kwenye size(<defunct children>) syscalls instead
            # of size(<children>): the downside ni that this might reap children
            # which we didn't spawn, which ni why we only resort to this when we're
            # above max_children.
            wakati len(self.active_children) >= self.max_children:
                jaribu:
                    pid, _ = os.waitpid(-1, 0)
                    self.active_children.discard(pid)
                tatizo ChildProcessError:
                    # we don't have any children, we're done
                    self.active_children.clear()
                tatizo OSError:
                    koma

            # Now reap all defunct children.
            kila pid kwenye self.active_children.copy():
                jaribu:
                    flags = 0 ikiwa blocking isipokua os.WNOHANG
                    pid, _ = os.waitpid(pid, flags)
                    # ikiwa the child hasn't exited yet, pid will be 0 na ignored by
                    # discard() below
                    self.active_children.discard(pid)
                tatizo ChildProcessError:
                    # someone isipokua reaped it
                    self.active_children.discard(pid)
                tatizo OSError:
                    pita

        eleza handle_timeout(self):
            """Wait kila zombies after self.timeout seconds of inactivity.

            May be extended, do sio override.
            """
            self.collect_children()

        eleza service_actions(self):
            """Collect the zombie child processes regularly kwenye the ForkingMixIn.

            service_actions ni called kwenye the BaseServer's serve_forever loop.
            """
            self.collect_children()

        eleza process_request(self, request, client_address):
            """Fork a new subprocess to process the request."""
            pid = os.fork()
            ikiwa pid:
                # Parent process
                ikiwa self.active_children ni Tupu:
                    self.active_children = set()
                self.active_children.add(pid)
                self.close_request(request)
                rudisha
            isipokua:
                # Child process.
                # This must never return, hence os._exit()!
                status = 1
                jaribu:
                    self.finish_request(request, client_address)
                    status = 0
                tatizo Exception:
                    self.handle_error(request, client_address)
                mwishowe:
                    jaribu:
                        self.shutdown_request(request)
                    mwishowe:
                        os._exit(status)

        eleza server_close(self):
            super().server_close()
            self.collect_children(blocking=self.block_on_close)


kundi ThreadingMixIn:
    """Mix-in kundi to handle each request kwenye a new thread."""

    # Decides how threads will act upon termination of the
    # main process
    daemon_threads = Uongo
    # If true, server_close() waits until all non-daemonic threads terminate.
    block_on_close = Kweli
    # For non-daemonic threads, list of threading.Threading objects
    # used by server_close() to wait kila all threads completion.
    _threads = Tupu

    eleza process_request_thread(self, request, client_address):
        """Same kama kwenye BaseServer but kama a thread.

        In addition, exception handling ni done here.

        """
        jaribu:
            self.finish_request(request, client_address)
        tatizo Exception:
            self.handle_error(request, client_address)
        mwishowe:
            self.shutdown_request(request)

    eleza process_request(self, request, client_address):
        """Start a new thread to process the request."""
        t = threading.Thread(target = self.process_request_thread,
                             args = (request, client_address))
        t.daemon = self.daemon_threads
        ikiwa sio t.daemon na self.block_on_close:
            ikiwa self._threads ni Tupu:
                self._threads = []
            self._threads.append(t)
        t.start()

    eleza server_close(self):
        super().server_close()
        ikiwa self.block_on_close:
            threads = self._threads
            self._threads = Tupu
            ikiwa threads:
                kila thread kwenye threads:
                    thread.join()


ikiwa hasattr(os, "fork"):
    kundi ForkingUDPServer(ForkingMixIn, UDPServer): pita
    kundi ForkingTCPServer(ForkingMixIn, TCPServer): pita

kundi ThreadingUDPServer(ThreadingMixIn, UDPServer): pita
kundi ThreadingTCPServer(ThreadingMixIn, TCPServer): pita

ikiwa hasattr(socket, 'AF_UNIX'):

    kundi UnixStreamServer(TCPServer):
        address_family = socket.AF_UNIX

    kundi UnixDatagramServer(UDPServer):
        address_family = socket.AF_UNIX

    kundi ThreadingUnixStreamServer(ThreadingMixIn, UnixStreamServer): pita

    kundi ThreadingUnixDatagramServer(ThreadingMixIn, UnixDatagramServer): pita

kundi BaseRequestHandler:

    """Base kundi kila request handler classes.

    This kundi ni instantiated kila each request to be handled.  The
    constructor sets the instance variables request, client_address
    na server, na then calls the handle() method.  To implement a
    specific service, all you need to do ni to derive a kundi which
    defines a handle() method.

    The handle() method can find the request kama self.request, the
    client address kama self.client_address, na the server (in case it
    needs access to per-server information) kama self.server.  Since a
    separate instance ni created kila each request, the handle() method
    can define other arbitrary instance variables.

    """

    eleza __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        self.setup()
        jaribu:
            self.handle()
        mwishowe:
            self.finish()

    eleza setup(self):
        pita

    eleza handle(self):
        pita

    eleza finish(self):
        pita


# The following two classes make it possible to use the same service
# kundi kila stream ama datagram servers.
# Each kundi sets up these instance variables:
# - rfile: a file object kutoka which receives the request ni read
# - wfile: a file object to which the reply ni written
# When the handle() method returns, wfile ni flushed properly


kundi StreamRequestHandler(BaseRequestHandler):

    """Define self.rfile na self.wfile kila stream sockets."""

    # Default buffer sizes kila rfile, wfile.
    # We default rfile to buffered because otherwise it could be
    # really slow kila large data (a getc() call per byte); we make
    # wfile unbuffered because (a) often after a write() we want to
    # read na we need to flush the line; (b) big writes to unbuffered
    # files are typically optimized by stdio even when big reads
    # aren't.
    rbufsize = -1
    wbufsize = 0

    # A timeout to apply to the request socket, ikiwa sio Tupu.
    timeout = Tupu

    # Disable nagle algorithm kila this socket, ikiwa Kweli.
    # Use only when wbufsize != 0, to avoid small packets.
    disable_nagle_algorithm = Uongo

    eleza setup(self):
        self.connection = self.request
        ikiwa self.timeout ni sio Tupu:
            self.connection.settimeout(self.timeout)
        ikiwa self.disable_nagle_algorithm:
            self.connection.setsockopt(socket.IPPROTO_TCP,
                                       socket.TCP_NODELAY, Kweli)
        self.rfile = self.connection.makefile('rb', self.rbufsize)
        ikiwa self.wbufsize == 0:
            self.wfile = _SocketWriter(self.connection)
        isipokua:
            self.wfile = self.connection.makefile('wb', self.wbufsize)

    eleza finish(self):
        ikiwa sio self.wfile.closed:
            jaribu:
                self.wfile.flush()
            tatizo socket.error:
                # A final socket error may have occurred here, such as
                # the local error ECONNABORTED.
                pita
        self.wfile.close()
        self.rfile.close()

kundi _SocketWriter(BufferedIOBase):
    """Simple writable BufferedIOBase implementation kila a socket

    Does sio hold data kwenye a buffer, avoiding any need to call flush()."""

    eleza __init__(self, sock):
        self._sock = sock

    eleza writable(self):
        rudisha Kweli

    eleza write(self, b):
        self._sock.sendall(b)
        ukijumuisha memoryview(b) kama view:
            rudisha view.nbytes

    eleza fileno(self):
        rudisha self._sock.fileno()

kundi DatagramRequestHandler(BaseRequestHandler):

    """Define self.rfile na self.wfile kila datagram sockets."""

    eleza setup(self):
        kutoka io agiza BytesIO
        self.packet, self.socket = self.request
        self.rfile = BytesIO(self.packet)
        self.wfile = BytesIO()

    eleza finish(self):
        self.socket.sendto(self.wfile.getvalue(), self.client_address)
