"""RPC Implementation, originally written for the Python Idle IDE

For security reasons, GvR requested that Idle's Python execution server process
connect to the Idle process, which listens for the connection.  Since Idle has
only one client per server, this was not a limitation.

   +---------------------------------+ +-------------+
   | socketserver.BaseRequestHandler | | SocketIO    |
   +---------------------------------+ +-------------+
                   ^                   | register()  |
                   |                   | unregister()|
                   |                   +-------------+
                   |                      ^  ^
                   |                      |  |
                   | + -------------------+  |
                   | |                       |
   +-------------------------+        +-----------------+
   | RPCHandler              |        | RPCClient       |
   | [attribute of RPCServer]|        |                 |
   +-------------------------+        +-----------------+

The RPCServer handler kundi is expected to provide register/unregister methods.
RPCHandler inherits the mix-in kundi SocketIO, which provides these methods.

See the Idle run.main() docstring for further information on how this was
accomplished in Idle.

"""
agiza builtins
agiza copyreg
agiza io
agiza marshal
agiza os
agiza pickle
agiza queue
agiza select
agiza socket
agiza socketserver
agiza struct
agiza sys
agiza threading
agiza traceback
agiza types

eleza unpickle_code(ms):
    "Return code object kutoka marshal string ms."
    co = marshal.loads(ms)
    assert isinstance(co, types.CodeType)
    rudisha co

eleza pickle_code(co):
    "Return unpickle function and tuple with marshalled co code object."
    assert isinstance(co, types.CodeType)
    ms = marshal.dumps(co)
    rudisha unpickle_code, (ms,)

eleza dumps(obj, protocol=None):
    "Return pickled (or marshalled) string for obj."
    # IDLE passes 'None' to select pickle.DEFAULT_PROTOCOL.
    f = io.BytesIO()
    p = CodePickler(f, protocol)
    p.dump(obj)
    rudisha f.getvalue()


kundi CodePickler(pickle.Pickler):
    dispatch_table = {types.CodeType: pickle_code, **copyreg.dispatch_table}


BUFSIZE = 8*1024
LOCALHOST = '127.0.0.1'

kundi RPCServer(socketserver.TCPServer):

    eleza __init__(self, addr, handlerclass=None):
        ikiwa handlerkundi is None:
            handlerkundi = RPCHandler
        socketserver.TCPServer.__init__(self, addr, handlerclass)

    eleza server_bind(self):
        "Override TCPServer method, no bind() phase for connecting entity"
        pass

    eleza server_activate(self):
        """Override TCPServer method, connect() instead of listen()

        Due to the reversed connection, self.server_address is actually the
        address of the Idle Client to which we are connecting.

        """
        self.socket.connect(self.server_address)

    eleza get_request(self):
        "Override TCPServer method, rudisha already connected socket"
        rudisha self.socket, self.server_address

    eleza handle_error(self, request, client_address):
        """Override TCPServer method

        Error message goes to __stderr__.  No error message ikiwa exiting
        normally or socket raised EOF.  Other exceptions not handled in
        server code will cause os._exit.

        """
        try:
            raise
        except SystemExit:
            raise
        except:
            erf = sys.__stderr__
            andika('\n' + '-'*40, file=erf)
            andika('Unhandled server exception!', file=erf)
            andika('Thread: %s' % threading.current_thread().name, file=erf)
            andika('Client Address: ', client_address, file=erf)
            andika('Request: ', repr(request), file=erf)
            traceback.print_exc(file=erf)
            andika('\n*** Unrecoverable, server exiting!', file=erf)
            andika('-'*40, file=erf)
            os._exit(0)

#----------------- end kundi RPCServer --------------------

objecttable = {}
request_queue = queue.Queue(0)
response_queue = queue.Queue(0)


kundi SocketIO(object):

    nextseq = 0

    eleza __init__(self, sock, objtable=None, debugging=None):
        self.sockthread = threading.current_thread()
        ikiwa debugging is not None:
            self.debugging = debugging
        self.sock = sock
        ikiwa objtable is None:
            objtable = objecttable
        self.objtable = objtable
        self.responses = {}
        self.cvars = {}

    eleza close(self):
        sock = self.sock
        self.sock = None
        ikiwa sock is not None:
            sock.close()

    eleza exithook(self):
        "override for specific exit action"
        os._exit(0)

    eleza debug(self, *args):
        ikiwa not self.debugging:
            return
        s = self.location + " " + str(threading.current_thread().name)
        for a in args:
            s = s + " " + str(a)
        andika(s, file=sys.__stderr__)

    eleza register(self, oid, object):
        self.objtable[oid] = object

    eleza unregister(self, oid):
        try:
            del self.objtable[oid]
        except KeyError:
            pass

    eleza localcall(self, seq, request):
        self.debug("localcall:", request)
        try:
            how, (oid, methodname, args, kwargs) = request
        except TypeError:
            rudisha ("ERROR", "Bad request format")
        ikiwa oid not in self.objtable:
            rudisha ("ERROR", "Unknown object id: %r" % (oid,))
        obj = self.objtable[oid]
        ikiwa methodname == "__methods__":
            methods = {}
            _getmethods(obj, methods)
            rudisha ("OK", methods)
        ikiwa methodname == "__attributes__":
            attributes = {}
            _getattributes(obj, attributes)
            rudisha ("OK", attributes)
        ikiwa not hasattr(obj, methodname):
            rudisha ("ERROR", "Unsupported method name: %r" % (methodname,))
        method = getattr(obj, methodname)
        try:
            ikiwa how == 'CALL':
                ret = method(*args, **kwargs)
                ikiwa isinstance(ret, RemoteObject):
                    ret = remoteref(ret)
                rudisha ("OK", ret)
            elikiwa how == 'QUEUE':
                request_queue.put((seq, (method, args, kwargs)))
                return("QUEUED", None)
            else:
                rudisha ("ERROR", "Unsupported message type: %s" % how)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except OSError:
            raise
        except Exception as ex:
            rudisha ("CALLEXC", ex)
        except:
            msg = "*** Internal Error: rpc.py:SocketIO.localcall()\n\n"\
                  " Object: %s \n Method: %s \n Args: %s\n"
            andika(msg % (oid, method, args), file=sys.__stderr__)
            traceback.print_exc(file=sys.__stderr__)
            rudisha ("EXCEPTION", None)

    eleza remotecall(self, oid, methodname, args, kwargs):
        self.debug("remotecall:asynccall: ", oid, methodname)
        seq = self.asynccall(oid, methodname, args, kwargs)
        rudisha self.asyncreturn(seq)

    eleza remotequeue(self, oid, methodname, args, kwargs):
        self.debug("remotequeue:asyncqueue: ", oid, methodname)
        seq = self.asyncqueue(oid, methodname, args, kwargs)
        rudisha self.asyncreturn(seq)

    eleza asynccall(self, oid, methodname, args, kwargs):
        request = ("CALL", (oid, methodname, args, kwargs))
        seq = self.newseq()
        ikiwa threading.current_thread() != self.sockthread:
            cvar = threading.Condition()
            self.cvars[seq] = cvar
        self.debug(("asynccall:%d:" % seq), oid, methodname, args, kwargs)
        self.putmessage((seq, request))
        rudisha seq

    eleza asyncqueue(self, oid, methodname, args, kwargs):
        request = ("QUEUE", (oid, methodname, args, kwargs))
        seq = self.newseq()
        ikiwa threading.current_thread() != self.sockthread:
            cvar = threading.Condition()
            self.cvars[seq] = cvar
        self.debug(("asyncqueue:%d:" % seq), oid, methodname, args, kwargs)
        self.putmessage((seq, request))
        rudisha seq

    eleza asyncreturn(self, seq):
        self.debug("asyncreturn:%d:call getresponse(): " % seq)
        response = self.getresponse(seq, wait=0.05)
        self.debug(("asyncreturn:%d:response: " % seq), response)
        rudisha self.decoderesponse(response)

    eleza decoderesponse(self, response):
        how, what = response
        ikiwa how == "OK":
            rudisha what
        ikiwa how == "QUEUED":
            rudisha None
        ikiwa how == "EXCEPTION":
            self.debug("decoderesponse: EXCEPTION")
            rudisha None
        ikiwa how == "EOF":
            self.debug("decoderesponse: EOF")
            self.decode_interrupthook()
            rudisha None
        ikiwa how == "ERROR":
            self.debug("decoderesponse: Internal ERROR:", what)
            raise RuntimeError(what)
        ikiwa how == "CALLEXC":
            self.debug("decoderesponse: Call Exception:", what)
            raise what
        raise SystemError(how, what)

    eleza decode_interrupthook(self):
        ""
        raise EOFError

    eleza mainloop(self):
        """Listen on socket until I/O not ready or EOF

        pollresponse() will loop looking for seq number None, which
        never comes, and exit on EOFError.

        """
        try:
            self.getresponse(myseq=None, wait=0.05)
        except EOFError:
            self.debug("mainloop:return")
            return

    eleza getresponse(self, myseq, wait):
        response = self._getresponse(myseq, wait)
        ikiwa response is not None:
            how, what = response
            ikiwa how == "OK":
                response = how, self._proxify(what)
        rudisha response

    eleza _proxify(self, obj):
        ikiwa isinstance(obj, RemoteProxy):
            rudisha RPCProxy(self, obj.oid)
        ikiwa isinstance(obj, list):
            rudisha list(map(self._proxify, obj))
        # XXX Check for other types -- not currently needed
        rudisha obj

    eleza _getresponse(self, myseq, wait):
        self.debug("_getresponse:myseq:", myseq)
        ikiwa threading.current_thread() is self.sockthread:
            # this thread does all reading of requests or responses
            while 1:
                response = self.pollresponse(myseq, wait)
                ikiwa response is not None:
                    rudisha response
        else:
            # wait for notification kutoka socket handling thread
            cvar = self.cvars[myseq]
            cvar.acquire()
            while myseq not in self.responses:
                cvar.wait()
            response = self.responses[myseq]
            self.debug("_getresponse:%s: thread woke up: response: %s" %
                       (myseq, response))
            del self.responses[myseq]
            del self.cvars[myseq]
            cvar.release()
            rudisha response

    eleza newseq(self):
        self.nextseq = seq = self.nextseq + 2
        rudisha seq

    eleza putmessage(self, message):
        self.debug("putmessage:%d:" % message[0])
        try:
            s = dumps(message)
        except pickle.PicklingError:
            andika("Cannot pickle:", repr(message), file=sys.__stderr__)
            raise
        s = struct.pack("<i", len(s)) + s
        while len(s) > 0:
            try:
                r, w, x = select.select([], [self.sock], [])
                n = self.sock.send(s[:BUFSIZE])
            except (AttributeError, TypeError):
                raise OSError("socket no longer exists")
            s = s[n:]

    buff = b''
    bufneed = 4
    bufstate = 0 # meaning: 0 => reading count; 1 => reading data

    eleza pollpacket(self, wait):
        self._stage0()
        ikiwa len(self.buff) < self.bufneed:
            r, w, x = select.select([self.sock.fileno()], [], [], wait)
            ikiwa len(r) == 0:
                rudisha None
            try:
                s = self.sock.recv(BUFSIZE)
            except OSError:
                raise EOFError
            ikiwa len(s) == 0:
                raise EOFError
            self.buff += s
            self._stage0()
        rudisha self._stage1()

    eleza _stage0(self):
        ikiwa self.bufstate == 0 and len(self.buff) >= 4:
            s = self.buff[:4]
            self.buff = self.buff[4:]
            self.bufneed = struct.unpack("<i", s)[0]
            self.bufstate = 1

    eleza _stage1(self):
        ikiwa self.bufstate == 1 and len(self.buff) >= self.bufneed:
            packet = self.buff[:self.bufneed]
            self.buff = self.buff[self.bufneed:]
            self.bufneed = 4
            self.bufstate = 0
            rudisha packet

    eleza pollmessage(self, wait):
        packet = self.pollpacket(wait)
        ikiwa packet is None:
            rudisha None
        try:
            message = pickle.loads(packet)
        except pickle.UnpicklingError:
            andika("-----------------------", file=sys.__stderr__)
            andika("cannot unpickle packet:", repr(packet), file=sys.__stderr__)
            traceback.print_stack(file=sys.__stderr__)
            andika("-----------------------", file=sys.__stderr__)
            raise
        rudisha message

    eleza pollresponse(self, myseq, wait):
        """Handle messages received on the socket.

        Some messages received may be asynchronous 'call' or 'queue' requests,
        and some may be responses for other threads.

        'call' requests are passed to self.localcall() with the expectation of
        immediate execution, during which time the socket is not serviced.

        'queue' requests are used for tasks (which may block or hang) to be
        processed in a different thread.  These requests are fed into
        request_queue by self.localcall().  Responses to queued requests are
        taken kutoka response_queue and sent across the link with the associated
        sequence numbers.  Messages in the queues are (sequence_number,
        request/response) tuples and code using this module removing messages
        kutoka the request_queue is responsible for returning the correct
        sequence number in the response_queue.

        pollresponse() will loop until a response message with the myseq
        sequence number is received, and will save other responses in
        self.responses and notify the owning thread.

        """
        while 1:
            # send queued response ikiwa there is one available
            try:
                qmsg = response_queue.get(0)
            except queue.Empty:
                pass
            else:
                seq, response = qmsg
                message = (seq, ('OK', response))
                self.putmessage(message)
            # poll for message on link
            try:
                message = self.pollmessage(wait)
                ikiwa message is None:  # socket not ready
                    rudisha None
            except EOFError:
                self.handle_EOF()
                rudisha None
            except AttributeError:
                rudisha None
            seq, resq = message
            how = resq[0]
            self.debug("pollresponse:%d:myseq:%s" % (seq, myseq))
            # process or queue a request
            ikiwa how in ("CALL", "QUEUE"):
                self.debug("pollresponse:%d:localcall:call:" % seq)
                response = self.localcall(seq, resq)
                self.debug("pollresponse:%d:localcall:response:%s"
                           % (seq, response))
                ikiwa how == "CALL":
                    self.putmessage((seq, response))
                elikiwa how == "QUEUE":
                    # don't acknowledge the 'queue' request!
                    pass
                continue
            # rudisha ikiwa completed message transaction
            elikiwa seq == myseq:
                rudisha resq
            # must be a response for a different thread:
            else:
                cv = self.cvars.get(seq, None)
                # response involving unknown sequence number is discarded,
                # probably intended for prior incarnation of server
                ikiwa cv is not None:
                    cv.acquire()
                    self.responses[seq] = resq
                    cv.notify()
                    cv.release()
                continue

    eleza handle_EOF(self):
        "action taken upon link being closed by peer"
        self.EOFhook()
        self.debug("handle_EOF")
        for key in self.cvars:
            cv = self.cvars[key]
            cv.acquire()
            self.responses[key] = ('EOF', None)
            cv.notify()
            cv.release()
        # call our (possibly overridden) exit function
        self.exithook()

    eleza EOFhook(self):
        "Classes using rpc client/server can override to augment EOF action"
        pass

#----------------- end kundi SocketIO --------------------

kundi RemoteObject(object):
    # Token mix-in class
    pass


eleza remoteref(obj):
    oid = id(obj)
    objecttable[oid] = obj
    rudisha RemoteProxy(oid)


kundi RemoteProxy(object):

    eleza __init__(self, oid):
        self.oid = oid


kundi RPCHandler(socketserver.BaseRequestHandler, SocketIO):

    debugging = False
    location = "#S"  # Server

    eleza __init__(self, sock, addr, svr):
        svr.current_handler = self ## cgt xxx
        SocketIO.__init__(self, sock)
        socketserver.BaseRequestHandler.__init__(self, sock, addr, svr)

    eleza handle(self):
        "handle() method required by socketserver"
        self.mainloop()

    eleza get_remote_proxy(self, oid):
        rudisha RPCProxy(self, oid)


kundi RPCClient(SocketIO):

    debugging = False
    location = "#C"  # Client

    nextseq = 1 # Requests coming kutoka the client are odd numbered

    eleza __init__(self, address, family=socket.AF_INET, type=socket.SOCK_STREAM):
        self.listening_sock = socket.socket(family, type)
        self.listening_sock.bind(address)
        self.listening_sock.listen(1)

    eleza accept(self):
        working_sock, address = self.listening_sock.accept()
        ikiwa self.debugging:
            andika("****** Connection request kutoka ", address, file=sys.__stderr__)
        ikiwa address[0] == LOCALHOST:
            SocketIO.__init__(self, working_sock)
        else:
            andika("** Invalid host: ", address, file=sys.__stderr__)
            raise OSError

    eleza get_remote_proxy(self, oid):
        rudisha RPCProxy(self, oid)


kundi RPCProxy(object):

    __methods = None
    __attributes = None

    eleza __init__(self, sockio, oid):
        self.sockio = sockio
        self.oid = oid

    eleza __getattr__(self, name):
        ikiwa self.__methods is None:
            self.__getmethods()
        ikiwa self.__methods.get(name):
            rudisha MethodProxy(self.sockio, self.oid, name)
        ikiwa self.__attributes is None:
            self.__getattributes()
        ikiwa name in self.__attributes:
            value = self.sockio.remotecall(self.oid, '__getattribute__',
                                           (name,), {})
            rudisha value
        else:
            raise AttributeError(name)

    eleza __getattributes(self):
        self.__attributes = self.sockio.remotecall(self.oid,
                                                "__attributes__", (), {})

    eleza __getmethods(self):
        self.__methods = self.sockio.remotecall(self.oid,
                                                "__methods__", (), {})

eleza _getmethods(obj, methods):
    # Helper to get a list of methods kutoka an object
    # Adds names to dictionary argument 'methods'
    for name in dir(obj):
        attr = getattr(obj, name)
        ikiwa callable(attr):
            methods[name] = 1
    ikiwa isinstance(obj, type):
        for super in obj.__bases__:
            _getmethods(super, methods)

eleza _getattributes(obj, attributes):
    for name in dir(obj):
        attr = getattr(obj, name)
        ikiwa not callable(attr):
            attributes[name] = 1


kundi MethodProxy(object):

    eleza __init__(self, sockio, oid, name):
        self.sockio = sockio
        self.oid = oid
        self.name = name

    eleza __call__(self, /, *args, **kwargs):
        value = self.sockio.remotecall(self.oid, self.name, args, kwargs)
        rudisha value


# XXX KBK 09Sep03  We need a proper unit test for this module.  Previously
#                  existing test code was removed at Rev 1.27 (r34098).

eleza displayhook(value):
    """Override standard display hook to use non-locale encoding"""
    ikiwa value is None:
        return
    # Set '_' to None to avoid recursion
    builtins._ = None
    text = repr(value)
    try:
        sys.stdout.write(text)
    except UnicodeEncodeError:
        # let's use ascii while utf8-bmp codec doesn't present
        encoding = 'ascii'
        bytes = text.encode(encoding, 'backslashreplace')
        text = bytes.decode(encoding, 'strict')
        sys.stdout.write(text)
    sys.stdout.write("\n")
    builtins._ = value


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_rpc', verbosity=2,)
