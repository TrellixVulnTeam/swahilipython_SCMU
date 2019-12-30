"""RPC Implementation, originally written kila the Python Idle IDE

For security reasons, GvR requested that Idle's Python execution server process
connect to the Idle process, which listens kila the connection.  Since Idle has
only one client per server, this was sio a limitation.

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

The RPCServer handler kundi ni expected to provide register/unregister methods.
RPCHandler inherits the mix-in kundi SocketIO, which provides these methods.

See the Idle run.main() docstring kila further information on how this was
accomplished kwenye Idle.

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
    "Return unpickle function na tuple ukijumuisha marshalled co code object."
    assert isinstance(co, types.CodeType)
    ms = marshal.dumps(co)
    rudisha unpickle_code, (ms,)

eleza dumps(obj, protocol=Tupu):
    "Return pickled (or marshalled) string kila obj."
    # IDLE pitaes 'Tupu' to select pickle.DEFAULT_PROTOCOL.
    f = io.BytesIO()
    p = CodePickler(f, protocol)
    p.dump(obj)
    rudisha f.getvalue()


kundi CodePickler(pickle.Pickler):
    dispatch_table = {types.CodeType: pickle_code, **copyreg.dispatch_table}


BUFSIZE = 8*1024
LOCALHOST = '127.0.0.1'

kundi RPCServer(socketserver.TCPServer):

    eleza __init__(self, addr, handlerclass=Tupu):
        ikiwa handlerkundi ni Tupu:
            handlerkundi = RPCHandler
        socketserver.TCPServer.__init__(self, addr, handlerclass)

    eleza server_bind(self):
        "Override TCPServer method, no bind() phase kila connecting entity"
        pita

    eleza server_activate(self):
        """Override TCPServer method, connect() instead of listen()

        Due to the reversed connection, self.server_address ni actually the
        address of the Idle Client to which we are connecting.

        """
        self.socket.connect(self.server_address)

    eleza get_request(self):
        "Override TCPServer method, rudisha already connected socket"
        rudisha self.socket, self.server_address

    eleza handle_error(self, request, client_address):
        """Override TCPServer method

        Error message goes to __stderr__.  No error message ikiwa exiting
        normally ama socket raised EOF.  Other exceptions sio handled kwenye
        server code will cause os._exit.

        """
        jaribu:
            raise
        tatizo SystemExit:
            raise
        tatizo:
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

    eleza __init__(self, sock, objtable=Tupu, debugging=Tupu):
        self.sockthread = threading.current_thread()
        ikiwa debugging ni sio Tupu:
            self.debugging = debugging
        self.sock = sock
        ikiwa objtable ni Tupu:
            objtable = objecttable
        self.objtable = objtable
        self.responses = {}
        self.cvars = {}

    eleza close(self):
        sock = self.sock
        self.sock = Tupu
        ikiwa sock ni sio Tupu:
            sock.close()

    eleza exithook(self):
        "override kila specific exit action"
        os._exit(0)

    eleza debug(self, *args):
        ikiwa sio self.debugging:
            rudisha
        s = self.location + " " + str(threading.current_thread().name)
        kila a kwenye args:
            s = s + " " + str(a)
        andika(s, file=sys.__stderr__)

    eleza register(self, oid, object):
        self.objtable[oid] = object

    eleza unregister(self, oid):
        jaribu:
            toa self.objtable[oid]
        tatizo KeyError:
            pita

    eleza localcall(self, seq, request):
        self.debug("localcall:", request)
        jaribu:
            how, (oid, methodname, args, kwargs) = request
        tatizo TypeError:
            rudisha ("ERROR", "Bad request format")
        ikiwa oid haiko kwenye self.objtable:
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
        ikiwa sio hasattr(obj, methodname):
            rudisha ("ERROR", "Unsupported method name: %r" % (methodname,))
        method = getattr(obj, methodname)
        jaribu:
            ikiwa how == 'CALL':
                ret = method(*args, **kwargs)
                ikiwa isinstance(ret, RemoteObject):
                    ret = remoteref(ret)
                rudisha ("OK", ret)
            lasivyo how == 'QUEUE':
                request_queue.put((seq, (method, args, kwargs)))
                return("QUEUED", Tupu)
            isipokua:
                rudisha ("ERROR", "Unsupported message type: %s" % how)
        tatizo SystemExit:
            raise
        tatizo KeyboardInterrupt:
            raise
        tatizo OSError:
            raise
        tatizo Exception kama ex:
            rudisha ("CALLEXC", ex)
        tatizo:
            msg = "*** Internal Error: rpc.py:SocketIO.localcall()\n\n"\
                  " Object: %s \n Method: %s \n Args: %s\n"
            andika(msg % (oid, method, args), file=sys.__stderr__)
            traceback.print_exc(file=sys.__stderr__)
            rudisha ("EXCEPTION", Tupu)

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
            rudisha Tupu
        ikiwa how == "EXCEPTION":
            self.debug("decoderesponse: EXCEPTION")
            rudisha Tupu
        ikiwa how == "EOF":
            self.debug("decoderesponse: EOF")
            self.decode_interrupthook()
            rudisha Tupu
        ikiwa how == "ERROR":
            self.debug("decoderesponse: Internal ERROR:", what)
            ashiria RuntimeError(what)
        ikiwa how == "CALLEXC":
            self.debug("decoderesponse: Call Exception:", what)
            ashiria what
        ashiria SystemError(how, what)

    eleza decode_interrupthook(self):
        ""
        ashiria EOFError

    eleza mainloop(self):
        """Listen on socket until I/O sio ready ama EOF

        pollresponse() will loop looking kila seq number Tupu, which
        never comes, na exit on EOFError.

        """
        jaribu:
            self.getresponse(myseq=Tupu, wait=0.05)
        tatizo EOFError:
            self.debug("mainloop:return")
            rudisha

    eleza getresponse(self, myseq, wait):
        response = self._getresponse(myseq, wait)
        ikiwa response ni sio Tupu:
            how, what = response
            ikiwa how == "OK":
                response = how, self._proxify(what)
        rudisha response

    eleza _proxify(self, obj):
        ikiwa isinstance(obj, RemoteProxy):
            rudisha RPCProxy(self, obj.oid)
        ikiwa isinstance(obj, list):
            rudisha list(map(self._proxify, obj))
        # XXX Check kila other types -- sio currently needed
        rudisha obj

    eleza _getresponse(self, myseq, wait):
        self.debug("_getresponse:myseq:", myseq)
        ikiwa threading.current_thread() ni self.sockthread:
            # this thread does all reading of requests ama responses
            wakati 1:
                response = self.pollresponse(myseq, wait)
                ikiwa response ni sio Tupu:
                    rudisha response
        isipokua:
            # wait kila notification kutoka socket handling thread
            cvar = self.cvars[myseq]
            cvar.acquire()
            wakati myseq haiko kwenye self.responses:
                cvar.wait()
            response = self.responses[myseq]
            self.debug("_getresponse:%s: thread woke up: response: %s" %
                       (myseq, response))
            toa self.responses[myseq]
            toa self.cvars[myseq]
            cvar.release()
            rudisha response

    eleza newseq(self):
        self.nextseq = seq = self.nextseq + 2
        rudisha seq

    eleza putmessage(self, message):
        self.debug("putmessage:%d:" % message[0])
        jaribu:
            s = dumps(message)
        tatizo pickle.PicklingError:
            andika("Cansio pickle:", repr(message), file=sys.__stderr__)
            raise
        s = struct.pack("<i", len(s)) + s
        wakati len(s) > 0:
            jaribu:
                r, w, x = select.select([], [self.sock], [])
                n = self.sock.send(s[:BUFSIZE])
            tatizo (AttributeError, TypeError):
                ashiria OSError("socket no longer exists")
            s = s[n:]

    buff = b''
    bufneed = 4
    bufstate = 0 # meaning: 0 => reading count; 1 => reading data

    eleza pollpacket(self, wait):
        self._stage0()
        ikiwa len(self.buff) < self.bufneed:
            r, w, x = select.select([self.sock.fileno()], [], [], wait)
            ikiwa len(r) == 0:
                rudisha Tupu
            jaribu:
                s = self.sock.recv(BUFSIZE)
            tatizo OSError:
                ashiria EOFError
            ikiwa len(s) == 0:
                ashiria EOFError
            self.buff += s
            self._stage0()
        rudisha self._stage1()

    eleza _stage0(self):
        ikiwa self.bufstate == 0 na len(self.buff) >= 4:
            s = self.buff[:4]
            self.buff = self.buff[4:]
            self.bufneed = struct.unpack("<i", s)[0]
            self.bufstate = 1

    eleza _stage1(self):
        ikiwa self.bufstate == 1 na len(self.buff) >= self.bufneed:
            packet = self.buff[:self.bufneed]
            self.buff = self.buff[self.bufneed:]
            self.bufneed = 4
            self.bufstate = 0
            rudisha packet

    eleza pollmessage(self, wait):
        packet = self.pollpacket(wait)
        ikiwa packet ni Tupu:
            rudisha Tupu
        jaribu:
            message = pickle.loads(packet)
        tatizo pickle.UnpicklingError:
            andika("-----------------------", file=sys.__stderr__)
            andika("cansio unpickle packet:", repr(packet), file=sys.__stderr__)
            traceback.print_stack(file=sys.__stderr__)
            andika("-----------------------", file=sys.__stderr__)
            raise
        rudisha message

    eleza pollresponse(self, myseq, wait):
        """Handle messages received on the socket.

        Some messages received may be asynchronous 'call' ama 'queue' requests,
        na some may be responses kila other threads.

        'call' requests are pitaed to self.localcall() ukijumuisha the expectation of
        immediate execution, during which time the socket ni sio serviced.

        'queue' requests are used kila tasks (which may block ama hang) to be
        processed kwenye a different thread.  These requests are fed into
        request_queue by self.localcall().  Responses to queued requests are
        taken kutoka response_queue na sent across the link ukijumuisha the associated
        sequence numbers.  Messages kwenye the queues are (sequence_number,
        request/response) tuples na code using this module removing messages
        kutoka the request_queue ni responsible kila returning the correct
        sequence number kwenye the response_queue.

        pollresponse() will loop until a response message ukijumuisha the myseq
        sequence number ni received, na will save other responses kwenye
        self.responses na notify the owning thread.

        """
        wakati 1:
            # send queued response ikiwa there ni one available
            jaribu:
                qmsg = response_queue.get(0)
            tatizo queue.Empty:
                pita
            isipokua:
                seq, response = qmsg
                message = (seq, ('OK', response))
                self.putmessage(message)
            # poll kila message on link
            jaribu:
                message = self.pollmessage(wait)
                ikiwa message ni Tupu:  # socket sio ready
                    rudisha Tupu
            tatizo EOFError:
                self.handle_EOF()
                rudisha Tupu
            tatizo AttributeError:
                rudisha Tupu
            seq, resq = message
            how = resq[0]
            self.debug("pollresponse:%d:myseq:%s" % (seq, myseq))
            # process ama queue a request
            ikiwa how kwenye ("CALL", "QUEUE"):
                self.debug("pollresponse:%d:localcall:call:" % seq)
                response = self.localcall(seq, resq)
                self.debug("pollresponse:%d:localcall:response:%s"
                           % (seq, response))
                ikiwa how == "CALL":
                    self.putmessage((seq, response))
                lasivyo how == "QUEUE":
                    # don't acknowledge the 'queue' request!
                    pita
                endelea
            # rudisha ikiwa completed message transaction
            lasivyo seq == myseq:
                rudisha resq
            # must be a response kila a different thread:
            isipokua:
                cv = self.cvars.get(seq, Tupu)
                # response involving unknown sequence number ni discarded,
                # probably intended kila prior incarnation of server
                ikiwa cv ni sio Tupu:
                    cv.acquire()
                    self.responses[seq] = resq
                    cv.notify()
                    cv.release()
                endelea

    eleza handle_EOF(self):
        "action taken upon link being closed by peer"
        self.EOFhook()
        self.debug("handle_EOF")
        kila key kwenye self.cvars:
            cv = self.cvars[key]
            cv.acquire()
            self.responses[key] = ('EOF', Tupu)
            cv.notify()
            cv.release()
        # call our (possibly overridden) exit function
        self.exithook()

    eleza EOFhook(self):
        "Classes using rpc client/server can override to augment EOF action"
        pita

#----------------- end kundi SocketIO --------------------

kundi RemoteObject(object):
    # Token mix-in class
    pita


eleza remoteref(obj):
    oid = id(obj)
    objecttable[oid] = obj
    rudisha RemoteProxy(oid)


kundi RemoteProxy(object):

    eleza __init__(self, oid):
        self.oid = oid


kundi RPCHandler(socketserver.BaseRequestHandler, SocketIO):

    debugging = Uongo
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

    debugging = Uongo
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
        isipokua:
            andika("** Invalid host: ", address, file=sys.__stderr__)
            ashiria OSError

    eleza get_remote_proxy(self, oid):
        rudisha RPCProxy(self, oid)


kundi RPCProxy(object):

    __methods = Tupu
    __attributes = Tupu

    eleza __init__(self, sockio, oid):
        self.sockio = sockio
        self.oid = oid

    eleza __getattr__(self, name):
        ikiwa self.__methods ni Tupu:
            self.__getmethods()
        ikiwa self.__methods.get(name):
            rudisha MethodProxy(self.sockio, self.oid, name)
        ikiwa self.__attributes ni Tupu:
            self.__getattributes()
        ikiwa name kwenye self.__attributes:
            value = self.sockio.remotecall(self.oid, '__getattribute__',
                                           (name,), {})
            rudisha value
        isipokua:
            ashiria AttributeError(name)

    eleza __getattributes(self):
        self.__attributes = self.sockio.remotecall(self.oid,
                                                "__attributes__", (), {})

    eleza __getmethods(self):
        self.__methods = self.sockio.remotecall(self.oid,
                                                "__methods__", (), {})

eleza _getmethods(obj, methods):
    # Helper to get a list of methods kutoka an object
    # Adds names to dictionary argument 'methods'
    kila name kwenye dir(obj):
        attr = getattr(obj, name)
        ikiwa callable(attr):
            methods[name] = 1
    ikiwa isinstance(obj, type):
        kila super kwenye obj.__bases__:
            _getmethods(super, methods)

eleza _getattributes(obj, attributes):
    kila name kwenye dir(obj):
        attr = getattr(obj, name)
        ikiwa sio callable(attr):
            attributes[name] = 1


kundi MethodProxy(object):

    eleza __init__(self, sockio, oid, name):
        self.sockio = sockio
        self.oid = oid
        self.name = name

    eleza __call__(self, /, *args, **kwargs):
        value = self.sockio.remotecall(self.oid, self.name, args, kwargs)
        rudisha value


# XXX KBK 09Sep03  We need a proper unit test kila this module.  Previously
#                  existing test code was removed at Rev 1.27 (r34098).

eleza displayhook(value):
    """Override standard display hook to use non-locale encoding"""
    ikiwa value ni Tupu:
        rudisha
    # Set '_' to Tupu to avoid recursion
    builtins._ = Tupu
    text = repr(value)
    jaribu:
        sys.stdout.write(text)
    tatizo UnicodeEncodeError:
        # let's use ascii wakati utf8-bmp codec doesn't present
        encoding = 'ascii'
        bytes = text.encode(encoding, 'backslashreplace')
        text = bytes.decode(encoding, 'strict')
        sys.stdout.write(text)
    sys.stdout.write("\n")
    builtins._ = value


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_rpc', verbosity=2,)
