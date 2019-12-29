#
# Module providing manager classes kila dealing
# ukijumuisha shared objects
#
# multiprocessing/managers.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

__all__ = [ 'BaseManager', 'SyncManager', 'BaseProxy', 'Token',
            'SharedMemoryManager' ]

#
# Imports
#

agiza sys
agiza threading
agiza signal
agiza array
agiza queue
agiza time
agiza os
kutoka os agiza getpid

kutoka traceback agiza format_exc

kutoka . agiza connection
kutoka .context agiza reduction, get_spawning_popen, ProcessError
kutoka . agiza pool
kutoka . agiza process
kutoka . agiza util
kutoka . agiza get_context
jaribu:
    kutoka . agiza shared_memory
    HAS_SHMEM = Kweli
tatizo ImportError:
    HAS_SHMEM = Uongo

#
# Register some things kila pickling
#

eleza reduce_array(a):
    rudisha array.array, (a.typecode, a.tobytes())
reduction.register(array.array, reduce_array)

view_types = [type(getattr({}, name)()) kila name kwenye ('items','keys','values')]
ikiwa view_types[0] ni sio list:       # only needed kwenye Py3.0
    eleza rebuild_as_list(obj):
        rudisha list, (list(obj),)
    kila view_type kwenye view_types:
        reduction.register(view_type, rebuild_as_list)

#
# Type kila identifying shared objects
#

kundi Token(object):
    '''
    Type to uniquely indentify a shared object
    '''
    __slots__ = ('typeid', 'address', 'id')

    eleza __init__(self, typeid, address, id):
        (self.typeid, self.address, self.id) = (typeid, address, id)

    eleza __getstate__(self):
        rudisha (self.typeid, self.address, self.id)

    eleza __setstate__(self, state):
        (self.typeid, self.address, self.id) = state

    eleza __repr__(self):
        rudisha '%s(typeid=%r, address=%r, id=%r)' % \
               (self.__class__.__name__, self.typeid, self.address, self.id)

#
# Function kila communication ukijumuisha a manager's server process
#

eleza dispatch(c, id, methodname, args=(), kwds={}):
    '''
    Send a message to manager using connection `c` na rudisha response
    '''
    c.send((id, methodname, args, kwds))
    kind, result = c.recv()
    ikiwa kind == '#RETURN':
        rudisha result
    ashiria convert_to_error(kind, result)

eleza convert_to_error(kind, result):
    ikiwa kind == '#ERROR':
        rudisha result
    lasivyo kind kwenye ('#TRACEBACK', '#UNSERIALIZABLE'):
        ikiwa sio isinstance(result, str):
            ashiria TypeError(
                "Result {0!r} (kind '{1}') type ni {2}, sio str".format(
                    result, kind, type(result)))
        ikiwa kind == '#UNSERIALIZABLE':
            rudisha RemoteError('Unserializable message: %s\n' % result)
        isipokua:
            rudisha RemoteError(result)
    isipokua:
        rudisha ValueError('Unrecognized message type {!r}'.format(kind))

kundi RemoteError(Exception):
    eleza __str__(self):
        rudisha ('\n' + '-'*75 + '\n' + str(self.args[0]) + '-'*75)

#
# Functions kila finding the method names of an object
#

eleza all_methods(obj):
    '''
    Return a list of names of methods of `obj`
    '''
    temp = []
    kila name kwenye dir(obj):
        func = getattr(obj, name)
        ikiwa callable(func):
            temp.append(name)
    rudisha temp

eleza public_methods(obj):
    '''
    Return a list of names of methods of `obj` which do sio start ukijumuisha '_'
    '''
    rudisha [name kila name kwenye all_methods(obj) ikiwa name[0] != '_']

#
# Server which ni run kwenye a process controlled by a manager
#

kundi Server(object):
    '''
    Server kundi which runs kwenye a process controlled by a manager object
    '''
    public = ['shutdown', 'create', 'accept_connection', 'get_methods',
              'debug_info', 'number_of_objects', 'dummy', 'incref', 'decref']

    eleza __init__(self, registry, address, authkey, serializer):
        ikiwa sio isinstance(authkey, bytes):
            ashiria TypeError(
                "Authkey {0!r} ni type {1!s}, sio bytes".format(
                    authkey, type(authkey)))
        self.registry = registry
        self.authkey = process.AuthenticationString(authkey)
        Listener, Client = listener_client[serializer]

        # do authentication later
        self.listener = Listener(address=address, backlog=16)
        self.address = self.listener.address

        self.id_to_obj = {'0': (Tupu, ())}
        self.id_to_refcount = {}
        self.id_to_local_proxy_obj = {}
        self.mutex = threading.Lock()

    eleza serve_forever(self):
        '''
        Run the server forever
        '''
        self.stop_event = threading.Event()
        process.current_process()._manager_server = self
        jaribu:
            accepter = threading.Thread(target=self.accepter)
            accepter.daemon = Kweli
            accepter.start()
            jaribu:
                wakati sio self.stop_event.is_set():
                    self.stop_event.wait(1)
            tatizo (KeyboardInterrupt, SystemExit):
                pita
        mwishowe:
            ikiwa sys.stdout != sys.__stdout__: # what about stderr?
                util.debug('resetting stdout, stderr')
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
            sys.exit(0)

    eleza accepter(self):
        wakati Kweli:
            jaribu:
                c = self.listener.accept()
            tatizo OSError:
                endelea
            t = threading.Thread(target=self.handle_request, args=(c,))
            t.daemon = Kweli
            t.start()

    eleza handle_request(self, c):
        '''
        Handle a new connection
        '''
        funcname = result = request = Tupu
        jaribu:
            connection.deliver_challenge(c, self.authkey)
            connection.answer_challenge(c, self.authkey)
            request = c.recv()
            ignore, funcname, args, kwds = request
            assert funcname kwenye self.public, '%r unrecognized' % funcname
            func = getattr(self, funcname)
        tatizo Exception:
            msg = ('#TRACEBACK', format_exc())
        isipokua:
            jaribu:
                result = func(c, *args, **kwds)
            tatizo Exception:
                msg = ('#TRACEBACK', format_exc())
            isipokua:
                msg = ('#RETURN', result)
        jaribu:
            c.send(msg)
        tatizo Exception kama e:
            jaribu:
                c.send(('#TRACEBACK', format_exc()))
            tatizo Exception:
                pita
            util.info('Failure to send message: %r', msg)
            util.info(' ... request was %r', request)
            util.info(' ... exception was %r', e)

        c.close()

    eleza serve_client(self, conn):
        '''
        Handle requests kutoka the proxies kwenye a particular process/thread
        '''
        util.debug('starting server thread to service %r',
                   threading.current_thread().name)

        recv = conn.recv
        send = conn.send
        id_to_obj = self.id_to_obj

        wakati sio self.stop_event.is_set():

            jaribu:
                methodname = obj = Tupu
                request = recv()
                ident, methodname, args, kwds = request
                jaribu:
                    obj, exposed, gettypeid = id_to_obj[ident]
                tatizo KeyError kama ke:
                    jaribu:
                        obj, exposed, gettypeid = \
                            self.id_to_local_proxy_obj[ident]
                    tatizo KeyError kama second_ke:
                        ashiria ke

                ikiwa methodname haiko kwenye exposed:
                    ashiria AttributeError(
                        'method %r of %r object ni haiko kwenye exposed=%r' %
                        (methodname, type(obj), exposed)
                        )

                function = getattr(obj, methodname)

                jaribu:
                    res = function(*args, **kwds)
                tatizo Exception kama e:
                    msg = ('#ERROR', e)
                isipokua:
                    typeid = gettypeid na gettypeid.get(methodname, Tupu)
                    ikiwa typeid:
                        rident, rexposed = self.create(conn, typeid, res)
                        token = Token(typeid, self.address, rident)
                        msg = ('#PROXY', (rexposed, token))
                    isipokua:
                        msg = ('#RETURN', res)

            tatizo AttributeError:
                ikiwa methodname ni Tupu:
                    msg = ('#TRACEBACK', format_exc())
                isipokua:
                    jaribu:
                        fallback_func = self.fallback_mapping[methodname]
                        result = fallback_func(
                            self, conn, ident, obj, *args, **kwds
                            )
                        msg = ('#RETURN', result)
                    tatizo Exception:
                        msg = ('#TRACEBACK', format_exc())

            tatizo EOFError:
                util.debug('got EOF -- exiting thread serving %r',
                           threading.current_thread().name)
                sys.exit(0)

            tatizo Exception:
                msg = ('#TRACEBACK', format_exc())

            jaribu:
                jaribu:
                    send(msg)
                tatizo Exception kama e:
                    send(('#UNSERIALIZABLE', format_exc()))
            tatizo Exception kama e:
                util.info('exception kwenye thread serving %r',
                        threading.current_thread().name)
                util.info(' ... message was %r', msg)
                util.info(' ... exception was %r', e)
                conn.close()
                sys.exit(1)

    eleza fallback_getvalue(self, conn, ident, obj):
        rudisha obj

    eleza fallback_str(self, conn, ident, obj):
        rudisha str(obj)

    eleza fallback_repr(self, conn, ident, obj):
        rudisha repr(obj)

    fallback_mapping = {
        '__str__':fallback_str,
        '__repr__':fallback_repr,
        '#GETVALUE':fallback_getvalue
        }

    eleza dummy(self, c):
        pita

    eleza debug_info(self, c):
        '''
        Return some info --- useful to spot problems ukijumuisha refcounting
        '''
        # Perhaps include debug info about 'c'?
        ukijumuisha self.mutex:
            result = []
            keys = list(self.id_to_refcount.keys())
            keys.sort()
            kila ident kwenye keys:
                ikiwa ident != '0':
                    result.append('  %s:       refcount=%s\n    %s' %
                                  (ident, self.id_to_refcount[ident],
                                   str(self.id_to_obj[ident][0])[:75]))
            rudisha '\n'.join(result)

    eleza number_of_objects(self, c):
        '''
        Number of shared objects
        '''
        # Doesn't use (len(self.id_to_obj) - 1) kama we shouldn't count ident='0'
        rudisha len(self.id_to_refcount)

    eleza shutdown(self, c):
        '''
        Shutdown this process
        '''
        jaribu:
            util.debug('manager received shutdown message')
            c.send(('#RETURN', Tupu))
        except:
            agiza traceback
            traceback.print_exc()
        mwishowe:
            self.stop_event.set()

    eleza create(*args, **kwds):
        '''
        Create a new shared object na rudisha its id
        '''
        ikiwa len(args) >= 3:
            self, c, typeid, *args = args
        lasivyo sio args:
            ashiria TypeError("descriptor 'create' of 'Server' object "
                            "needs an argument")
        isipokua:
            ikiwa 'typeid' haiko kwenye kwds:
                ashiria TypeError('create expected at least 2 positional '
                                'arguments, got %d' % (len(args)-1))
            typeid = kwds.pop('typeid')
            ikiwa len(args) >= 2:
                self, c, *args = args
                agiza warnings
                warnings.warn("Passing 'typeid' kama keyword argument ni deprecated",
                              DeprecationWarning, stacklevel=2)
            isipokua:
                ikiwa 'c' haiko kwenye kwds:
                    ashiria TypeError('create expected at least 2 positional '
                                    'arguments, got %d' % (len(args)-1))
                c = kwds.pop('c')
                self, *args = args
                agiza warnings
                warnings.warn("Passing 'c' kama keyword argument ni deprecated",
                              DeprecationWarning, stacklevel=2)
        args = tuple(args)

        ukijumuisha self.mutex:
            callable, exposed, method_to_typeid, proxytype = \
                      self.registry[typeid]

            ikiwa callable ni Tupu:
                ikiwa kwds ama (len(args) != 1):
                    ashiria ValueError(
                        "Without callable, must have one non-keyword argument")
                obj = args[0]
            isipokua:
                obj = callable(*args, **kwds)

            ikiwa exposed ni Tupu:
                exposed = public_methods(obj)
            ikiwa method_to_typeid ni sio Tupu:
                ikiwa sio isinstance(method_to_typeid, dict):
                    ashiria TypeError(
                        "Method_to_typeid {0!r}: type {1!s}, sio dict".format(
                            method_to_typeid, type(method_to_typeid)))
                exposed = list(exposed) + list(method_to_typeid)

            ident = '%x' % id(obj)  # convert to string because xmlrpclib
                                    # only has 32 bit signed integers
            util.debug('%r callable rudishaed object ukijumuisha id %r', typeid, ident)

            self.id_to_obj[ident] = (obj, set(exposed), method_to_typeid)
            ikiwa ident haiko kwenye self.id_to_refcount:
                self.id_to_refcount[ident] = 0

        self.incref(c, ident)
        rudisha ident, tuple(exposed)
    create.__text_signature__ = '($self, c, typeid, /, *args, **kwds)'

    eleza get_methods(self, c, token):
        '''
        Return the methods of the shared object indicated by token
        '''
        rudisha tuple(self.id_to_obj[token.id][1])

    eleza accept_connection(self, c, name):
        '''
        Spawn a new thread to serve this connection
        '''
        threading.current_thread().name = name
        c.send(('#RETURN', Tupu))
        self.serve_client(c)

    eleza incref(self, c, ident):
        ukijumuisha self.mutex:
            jaribu:
                self.id_to_refcount[ident] += 1
            tatizo KeyError kama ke:
                # If no external references exist but an internal (to the
                # manager) still does na a new external reference ni created
                # kutoka it, restore the manager's tracking of it kutoka the
                # previously stashed internal ref.
                ikiwa ident kwenye self.id_to_local_proxy_obj:
                    self.id_to_refcount[ident] = 1
                    self.id_to_obj[ident] = \
                        self.id_to_local_proxy_obj[ident]
                    obj, exposed, gettypeid = self.id_to_obj[ident]
                    util.debug('Server re-enabled tracking & INCREF %r', ident)
                isipokua:
                    ashiria ke

    eleza decref(self, c, ident):
        ikiwa ident haiko kwenye self.id_to_refcount na \
            ident kwenye self.id_to_local_proxy_obj:
            util.debug('Server DECREF skipping %r', ident)
            rudisha

        ukijumuisha self.mutex:
            ikiwa self.id_to_refcount[ident] <= 0:
                ashiria AssertionError(
                    "Id {0!s} ({1!r}) has refcount {2:n}, sio 1+".format(
                        ident, self.id_to_obj[ident],
                        self.id_to_refcount[ident]))
            self.id_to_refcount[ident] -= 1
            ikiwa self.id_to_refcount[ident] == 0:
                toa self.id_to_refcount[ident]

        ikiwa ident haiko kwenye self.id_to_refcount:
            # Two-step process kwenye case the object turns out to contain other
            # proxy objects (e.g. a managed list of managed lists).
            # Otherwise, deleting self.id_to_obj[ident] would trigger the
            # deleting of the stored value (another managed object) which would
            # kwenye turn attempt to acquire the mutex that ni already held here.
            self.id_to_obj[ident] = (Tupu, (), Tupu)  # thread-safe
            util.debug('disposing of obj ukijumuisha id %r', ident)
            ukijumuisha self.mutex:
                toa self.id_to_obj[ident]


#
# Class to represent state of a manager
#

kundi State(object):
    __slots__ = ['value']
    INITIAL = 0
    STARTED = 1
    SHUTDOWN = 2

#
# Mapping kutoka serializer name to Listener na Client types
#

listener_client = {
    'pickle' : (connection.Listener, connection.Client),
    'xmlrpclib' : (connection.XmlListener, connection.XmlClient)
    }

#
# Definition of BaseManager
#

kundi BaseManager(object):
    '''
    Base kundi kila managers
    '''
    _registry = {}
    _Server = Server

    eleza __init__(self, address=Tupu, authkey=Tupu, serializer='pickle',
                 ctx=Tupu):
        ikiwa authkey ni Tupu:
            authkey = process.current_process().authkey
        self._address = address     # XXX sio final address ikiwa eg ('', 0)
        self._authkey = process.AuthenticationString(authkey)
        self._state = State()
        self._state.value = State.INITIAL
        self._serializer = serializer
        self._Listener, self._Client = listener_client[serializer]
        self._ctx = ctx ama get_context()

    eleza get_server(self):
        '''
        Return server object ukijumuisha serve_forever() method na address attribute
        '''
        ikiwa self._state.value != State.INITIAL:
            ikiwa self._state.value == State.STARTED:
                ashiria ProcessError("Already started server")
            lasivyo self._state.value == State.SHUTDOWN:
                ashiria ProcessError("Manager has shut down")
            isipokua:
                ashiria ProcessError(
                    "Unknown state {!r}".format(self._state.value))
        rudisha Server(self._registry, self._address,
                      self._authkey, self._serializer)

    eleza connect(self):
        '''
        Connect manager object to the server process
        '''
        Listener, Client = listener_client[self._serializer]
        conn = Client(self._address, authkey=self._authkey)
        dispatch(conn, Tupu, 'dummy')
        self._state.value = State.STARTED

    eleza start(self, initializer=Tupu, initargs=()):
        '''
        Spawn a server process kila this manager object
        '''
        ikiwa self._state.value != State.INITIAL:
            ikiwa self._state.value == State.STARTED:
                ashiria ProcessError("Already started server")
            lasivyo self._state.value == State.SHUTDOWN:
                ashiria ProcessError("Manager has shut down")
            isipokua:
                ashiria ProcessError(
                    "Unknown state {!r}".format(self._state.value))

        ikiwa initializer ni sio Tupu na sio callable(initializer):
            ashiria TypeError('initializer must be a callable')

        # pipe over which we will retrieve address of server
        reader, writer = connection.Pipe(duplex=Uongo)

        # spawn process which runs a server
        self._process = self._ctx.Process(
            target=type(self)._run_server,
            args=(self._registry, self._address, self._authkey,
                  self._serializer, writer, initializer, initargs),
            )
        ident = ':'.join(str(i) kila i kwenye self._process._identity)
        self._process.name = type(self).__name__  + '-' + ident
        self._process.start()

        # get address of server
        writer.close()
        self._address = reader.recv()
        reader.close()

        # register a finalizer
        self._state.value = State.STARTED
        self.shutdown = util.Finalize(
            self, type(self)._finalize_manager,
            args=(self._process, self._address, self._authkey,
                  self._state, self._Client),
            exitpriority=0
            )

    @classmethod
    eleza _run_server(cls, registry, address, authkey, serializer, writer,
                    initializer=Tupu, initargs=()):
        '''
        Create a server, report its address na run it
        '''
        # bpo-36368: protect server process kutoka KeyboardInterrupt signals
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        ikiwa initializer ni sio Tupu:
            initializer(*initargs)

        # create server
        server = cls._Server(registry, address, authkey, serializer)

        # inform parent process of the server's address
        writer.send(server.address)
        writer.close()

        # run the manager
        util.info('manager serving at %r', server.address)
        server.serve_forever()

    eleza _create(self, typeid, /, *args, **kwds):
        '''
        Create a new shared object; rudisha the token na exposed tuple
        '''
        assert self._state.value == State.STARTED, 'server sio yet started'
        conn = self._Client(self._address, authkey=self._authkey)
        jaribu:
            id, exposed = dispatch(conn, Tupu, 'create', (typeid,)+args, kwds)
        mwishowe:
            conn.close()
        rudisha Token(typeid, self._address, id), exposed

    eleza join(self, timeout=Tupu):
        '''
        Join the manager process (ikiwa it has been spawned)
        '''
        ikiwa self._process ni sio Tupu:
            self._process.join(timeout)
            ikiwa sio self._process.is_alive():
                self._process = Tupu

    eleza _debug_info(self):
        '''
        Return some info about the servers shared objects na connections
        '''
        conn = self._Client(self._address, authkey=self._authkey)
        jaribu:
            rudisha dispatch(conn, Tupu, 'debug_info')
        mwishowe:
            conn.close()

    eleza _number_of_objects(self):
        '''
        Return the number of shared objects
        '''
        conn = self._Client(self._address, authkey=self._authkey)
        jaribu:
            rudisha dispatch(conn, Tupu, 'number_of_objects')
        mwishowe:
            conn.close()

    eleza __enter__(self):
        ikiwa self._state.value == State.INITIAL:
            self.start()
        ikiwa self._state.value != State.STARTED:
            ikiwa self._state.value == State.INITIAL:
                ashiria ProcessError("Unable to start server")
            lasivyo self._state.value == State.SHUTDOWN:
                ashiria ProcessError("Manager has shut down")
            isipokua:
                ashiria ProcessError(
                    "Unknown state {!r}".format(self._state.value))
        rudisha self

    eleza __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    @staticmethod
    eleza _finalize_manager(process, address, authkey, state, _Client):
        '''
        Shutdown the manager process; will be registered kama a finalizer
        '''
        ikiwa process.is_alive():
            util.info('sending shutdown message to manager')
            jaribu:
                conn = _Client(address, authkey=authkey)
                jaribu:
                    dispatch(conn, Tupu, 'shutdown')
                mwishowe:
                    conn.close()
            tatizo Exception:
                pita

            process.join(timeout=1.0)
            ikiwa process.is_alive():
                util.info('manager still alive')
                ikiwa hasattr(process, 'terminate'):
                    util.info('trying to `terminate()` manager process')
                    process.terminate()
                    process.join(timeout=0.1)
                    ikiwa process.is_alive():
                        util.info('manager still alive after terminate')

        state.value = State.SHUTDOWN
        jaribu:
            toa BaseProxy._address_to_local[address]
        tatizo KeyError:
            pita

    @property
    eleza address(self):
        rudisha self._address

    @classmethod
    eleza register(cls, typeid, callable=Tupu, proxytype=Tupu, exposed=Tupu,
                 method_to_typeid=Tupu, create_method=Kweli):
        '''
        Register a typeid ukijumuisha the manager type
        '''
        ikiwa '_registry' haiko kwenye cls.__dict__:
            cls._registry = cls._registry.copy()

        ikiwa proxytype ni Tupu:
            proxytype = AutoProxy

        exposed = exposed ama getattr(proxytype, '_exposed_', Tupu)

        method_to_typeid = method_to_typeid ama \
                           getattr(proxytype, '_method_to_typeid_', Tupu)

        ikiwa method_to_typeid:
            kila key, value kwenye list(method_to_typeid.items()): # isinstance?
                assert type(key) ni str, '%r ni sio a string' % key
                assert type(value) ni str, '%r ni sio a string' % value

        cls._registry[typeid] = (
            callable, exposed, method_to_typeid, proxytype
            )

        ikiwa create_method:
            eleza temp(self, /, *args, **kwds):
                util.debug('requesting creation of a shared %r object', typeid)
                token, exp = self._create(typeid, *args, **kwds)
                proxy = proxytype(
                    token, self._serializer, manager=self,
                    authkey=self._authkey, exposed=exp
                    )
                conn = self._Client(token.address, authkey=self._authkey)
                dispatch(conn, Tupu, 'decref', (token.id,))
                rudisha proxy
            temp.__name__ = typeid
            setattr(cls, typeid, temp)

#
# Subkundi of set which get cleared after a fork
#

kundi ProcessLocalSet(set):
    eleza __init__(self):
        util.register_after_fork(self, lambda obj: obj.clear())
    eleza __reduce__(self):
        rudisha type(self), ()

#
# Definition of BaseProxy
#

kundi BaseProxy(object):
    '''
    A base kila proxies of shared objects
    '''
    _address_to_local = {}
    _mutex = util.ForkAwareThreadLock()

    eleza __init__(self, token, serializer, manager=Tupu,
                 authkey=Tupu, exposed=Tupu, incref=Kweli, manager_owned=Uongo):
        ukijumuisha BaseProxy._mutex:
            tls_idset = BaseProxy._address_to_local.get(token.address, Tupu)
            ikiwa tls_idset ni Tupu:
                tls_idset = util.ForkAwareLocal(), ProcessLocalSet()
                BaseProxy._address_to_local[token.address] = tls_idset

        # self._tls ni used to record the connection used by this
        # thread to communicate ukijumuisha the manager at token.address
        self._tls = tls_idset[0]

        # self._idset ni used to record the identities of all shared
        # objects kila which the current process owns references and
        # which are kwenye the manager at token.address
        self._idset = tls_idset[1]

        self._token = token
        self._id = self._token.id
        self._manager = manager
        self._serializer = serializer
        self._Client = listener_client[serializer][1]

        # Should be set to Kweli only when a proxy object ni being created
        # on the manager server; primary use case: nested proxy objects.
        # RebuildProxy detects when a proxy ni being created on the manager
        # na sets this value appropriately.
        self._owned_by_manager = manager_owned

        ikiwa authkey ni sio Tupu:
            self._authkey = process.AuthenticationString(authkey)
        lasivyo self._manager ni sio Tupu:
            self._authkey = self._manager._authkey
        isipokua:
            self._authkey = process.current_process().authkey

        ikiwa incref:
            self._incref()

        util.register_after_fork(self, BaseProxy._after_fork)

    eleza _connect(self):
        util.debug('making connection to manager')
        name = process.current_process().name
        ikiwa threading.current_thread().name != 'MainThread':
            name += '|' + threading.current_thread().name
        conn = self._Client(self._token.address, authkey=self._authkey)
        dispatch(conn, Tupu, 'accept_connection', (name,))
        self._tls.connection = conn

    eleza _callmethod(self, methodname, args=(), kwds={}):
        '''
        Try to call a method of the referrent na rudisha a copy of the result
        '''
        jaribu:
            conn = self._tls.connection
        tatizo AttributeError:
            util.debug('thread %r does sio own a connection',
                       threading.current_thread().name)
            self._connect()
            conn = self._tls.connection

        conn.send((self._id, methodname, args, kwds))
        kind, result = conn.recv()

        ikiwa kind == '#RETURN':
            rudisha result
        lasivyo kind == '#PROXY':
            exposed, token = result
            proxytype = self._manager._registry[token.typeid][-1]
            token.address = self._token.address
            proxy = proxytype(
                token, self._serializer, manager=self._manager,
                authkey=self._authkey, exposed=exposed
                )
            conn = self._Client(token.address, authkey=self._authkey)
            dispatch(conn, Tupu, 'decref', (token.id,))
            rudisha proxy
        ashiria convert_to_error(kind, result)

    eleza _getvalue(self):
        '''
        Get a copy of the value of the referent
        '''
        rudisha self._callmethod('#GETVALUE')

    eleza _incref(self):
        ikiwa self._owned_by_manager:
            util.debug('owned_by_manager skipped INCREF of %r', self._token.id)
            rudisha

        conn = self._Client(self._token.address, authkey=self._authkey)
        dispatch(conn, Tupu, 'incref', (self._id,))
        util.debug('INCREF %r', self._token.id)

        self._idset.add(self._id)

        state = self._manager na self._manager._state

        self._close = util.Finalize(
            self, BaseProxy._decref,
            args=(self._token, self._authkey, state,
                  self._tls, self._idset, self._Client),
            exitpriority=10
            )

    @staticmethod
    eleza _decref(token, authkey, state, tls, idset, _Client):
        idset.discard(token.id)

        # check whether manager ni still alive
        ikiwa state ni Tupu ama state.value == State.STARTED:
            # tell manager this process no longer cares about referent
            jaribu:
                util.debug('DECREF %r', token.id)
                conn = _Client(token.address, authkey=authkey)
                dispatch(conn, Tupu, 'decref', (token.id,))
            tatizo Exception kama e:
                util.debug('... decref failed %s', e)

        isipokua:
            util.debug('DECREF %r -- manager already shutdown', token.id)

        # check whether we can close this thread's connection because
        # the process owns no more references to objects kila this manager
        ikiwa sio idset na hasattr(tls, 'connection'):
            util.debug('thread %r has no more proxies so closing conn',
                       threading.current_thread().name)
            tls.connection.close()
            toa tls.connection

    eleza _after_fork(self):
        self._manager = Tupu
        jaribu:
            self._incref()
        tatizo Exception kama e:
            # the proxy may just be kila a manager which has shutdown
            util.info('incref failed: %s' % e)

    eleza __reduce__(self):
        kwds = {}
        ikiwa get_spawning_popen() ni sio Tupu:
            kwds['authkey'] = self._authkey

        ikiwa getattr(self, '_isauto', Uongo):
            kwds['exposed'] = self._exposed_
            rudisha (RebuildProxy,
                    (AutoProxy, self._token, self._serializer, kwds))
        isipokua:
            rudisha (RebuildProxy,
                    (type(self), self._token, self._serializer, kwds))

    eleza __deepcopy__(self, memo):
        rudisha self._getvalue()

    eleza __repr__(self):
        rudisha '<%s object, typeid %r at %#x>' % \
               (type(self).__name__, self._token.typeid, id(self))

    eleza __str__(self):
        '''
        Return representation of the referent (or a fall-back ikiwa that fails)
        '''
        jaribu:
            rudisha self._callmethod('__repr__')
        tatizo Exception:
            rudisha repr(self)[:-1] + "; '__str__()' failed>"

#
# Function used kila unpickling
#

eleza RebuildProxy(func, token, serializer, kwds):
    '''
    Function used kila unpickling proxy objects.
    '''
    server = getattr(process.current_process(), '_manager_server', Tupu)
    ikiwa server na server.address == token.address:
        util.debug('Rebuild a proxy owned by manager, token=%r', token)
        kwds['manager_owned'] = Kweli
        ikiwa token.id haiko kwenye server.id_to_local_proxy_obj:
            server.id_to_local_proxy_obj[token.id] = \
                server.id_to_obj[token.id]
    incref = (
        kwds.pop('incref', Kweli) and
        sio getattr(process.current_process(), '_inheriting', Uongo)
        )
    rudisha func(token, serializer, incref=incref, **kwds)

#
# Functions to create proxies na proxy types
#

eleza MakeProxyType(name, exposed, _cache={}):
    '''
    Return a proxy type whose methods are given by `exposed`
    '''
    exposed = tuple(exposed)
    jaribu:
        rudisha _cache[(name, exposed)]
    tatizo KeyError:
        pita

    dic = {}

    kila meth kwenye exposed:
        exec('''eleza %s(self, /, *args, **kwds):
        rudisha self._callmethod(%r, args, kwds)''' % (meth, meth), dic)

    ProxyType = type(name, (BaseProxy,), dic)
    ProxyType._exposed_ = exposed
    _cache[(name, exposed)] = ProxyType
    rudisha ProxyType


eleza AutoProxy(token, serializer, manager=Tupu, authkey=Tupu,
              exposed=Tupu, incref=Kweli):
    '''
    Return an auto-proxy kila `token`
    '''
    _Client = listener_client[serializer][1]

    ikiwa exposed ni Tupu:
        conn = _Client(token.address, authkey=authkey)
        jaribu:
            exposed = dispatch(conn, Tupu, 'get_methods', (token,))
        mwishowe:
            conn.close()

    ikiwa authkey ni Tupu na manager ni sio Tupu:
        authkey = manager._authkey
    ikiwa authkey ni Tupu:
        authkey = process.current_process().authkey

    ProxyType = MakeProxyType('AutoProxy[%s]' % token.typeid, exposed)
    proxy = ProxyType(token, serializer, manager=manager, authkey=authkey,
                      incref=incref)
    proxy._isauto = Kweli
    rudisha proxy

#
# Types/callables which we will register ukijumuisha SyncManager
#

kundi Namespace(object):
    eleza __init__(self, /, **kwds):
        self.__dict__.update(kwds)
    eleza __repr__(self):
        items = list(self.__dict__.items())
        temp = []
        kila name, value kwenye items:
            ikiwa sio name.startswith('_'):
                temp.append('%s=%r' % (name, value))
        temp.sort()
        rudisha '%s(%s)' % (self.__class__.__name__, ', '.join(temp))

kundi Value(object):
    eleza __init__(self, typecode, value, lock=Kweli):
        self._typecode = typecode
        self._value = value
    eleza get(self):
        rudisha self._value
    eleza set(self, value):
        self._value = value
    eleza __repr__(self):
        rudisha '%s(%r, %r)'%(type(self).__name__, self._typecode, self._value)
    value = property(get, set)

eleza Array(typecode, sequence, lock=Kweli):
    rudisha array.array(typecode, sequence)

#
# Proxy types used by SyncManager
#

kundi IteratorProxy(BaseProxy):
    _exposed_ = ('__next__', 'send', 'throw', 'close')
    eleza __iter__(self):
        rudisha self
    eleza __next__(self, *args):
        rudisha self._callmethod('__next__', args)
    eleza send(self, *args):
        rudisha self._callmethod('send', args)
    eleza throw(self, *args):
        rudisha self._callmethod('throw', args)
    eleza close(self, *args):
        rudisha self._callmethod('close', args)


kundi AcquirerProxy(BaseProxy):
    _exposed_ = ('acquire', 'release')
    eleza acquire(self, blocking=Kweli, timeout=Tupu):
        args = (blocking,) ikiwa timeout ni Tupu isipokua (blocking, timeout)
        rudisha self._callmethod('acquire', args)
    eleza release(self):
        rudisha self._callmethod('release')
    eleza __enter__(self):
        rudisha self._callmethod('acquire')
    eleza __exit__(self, exc_type, exc_val, exc_tb):
        rudisha self._callmethod('release')


kundi ConditionProxy(AcquirerProxy):
    _exposed_ = ('acquire', 'release', 'wait', 'notify', 'notify_all')
    eleza wait(self, timeout=Tupu):
        rudisha self._callmethod('wait', (timeout,))
    eleza notify(self, n=1):
        rudisha self._callmethod('notify', (n,))
    eleza notify_all(self):
        rudisha self._callmethod('notify_all')
    eleza wait_for(self, predicate, timeout=Tupu):
        result = predicate()
        ikiwa result:
            rudisha result
        ikiwa timeout ni sio Tupu:
            endtime = time.monotonic() + timeout
        isipokua:
            endtime = Tupu
            waittime = Tupu
        wakati sio result:
            ikiwa endtime ni sio Tupu:
                waittime = endtime - time.monotonic()
                ikiwa waittime <= 0:
                    koma
            self.wait(waittime)
            result = predicate()
        rudisha result


kundi EventProxy(BaseProxy):
    _exposed_ = ('is_set', 'set', 'clear', 'wait')
    eleza is_set(self):
        rudisha self._callmethod('is_set')
    eleza set(self):
        rudisha self._callmethod('set')
    eleza clear(self):
        rudisha self._callmethod('clear')
    eleza wait(self, timeout=Tupu):
        rudisha self._callmethod('wait', (timeout,))


kundi BarrierProxy(BaseProxy):
    _exposed_ = ('__getattribute__', 'wait', 'abort', 'reset')
    eleza wait(self, timeout=Tupu):
        rudisha self._callmethod('wait', (timeout,))
    eleza abort(self):
        rudisha self._callmethod('abort')
    eleza reset(self):
        rudisha self._callmethod('reset')
    @property
    eleza parties(self):
        rudisha self._callmethod('__getattribute__', ('parties',))
    @property
    eleza n_waiting(self):
        rudisha self._callmethod('__getattribute__', ('n_waiting',))
    @property
    eleza broken(self):
        rudisha self._callmethod('__getattribute__', ('broken',))


kundi NamespaceProxy(BaseProxy):
    _exposed_ = ('__getattribute__', '__setattr__', '__delattr__')
    eleza __getattr__(self, key):
        ikiwa key[0] == '_':
            rudisha object.__getattribute__(self, key)
        callmethod = object.__getattribute__(self, '_callmethod')
        rudisha callmethod('__getattribute__', (key,))
    eleza __setattr__(self, key, value):
        ikiwa key[0] == '_':
            rudisha object.__setattr__(self, key, value)
        callmethod = object.__getattribute__(self, '_callmethod')
        rudisha callmethod('__setattr__', (key, value))
    eleza __delattr__(self, key):
        ikiwa key[0] == '_':
            rudisha object.__delattr__(self, key)
        callmethod = object.__getattribute__(self, '_callmethod')
        rudisha callmethod('__delattr__', (key,))


kundi ValueProxy(BaseProxy):
    _exposed_ = ('get', 'set')
    eleza get(self):
        rudisha self._callmethod('get')
    eleza set(self, value):
        rudisha self._callmethod('set', (value,))
    value = property(get, set)


BaseListProxy = MakeProxyType('BaseListProxy', (
    '__add__', '__contains__', '__delitem__', '__getitem__', '__len__',
    '__mul__', '__reversed__', '__rmul__', '__setitem__',
    'append', 'count', 'extend', 'index', 'insert', 'pop', 'remove',
    'reverse', 'sort', '__imul__'
    ))
kundi ListProxy(BaseListProxy):
    eleza __iadd__(self, value):
        self._callmethod('extend', (value,))
        rudisha self
    eleza __imul__(self, value):
        self._callmethod('__imul__', (value,))
        rudisha self


DictProxy = MakeProxyType('DictProxy', (
    '__contains__', '__delitem__', '__getitem__', '__iter__', '__len__',
    '__setitem__', 'clear', 'copy', 'get', 'items',
    'keys', 'pop', 'popitem', 'setdefault', 'update', 'values'
    ))
DictProxy._method_to_typeid_ = {
    '__iter__': 'Iterator',
    }


ArrayProxy = MakeProxyType('ArrayProxy', (
    '__len__', '__getitem__', '__setitem__'
    ))


BasePoolProxy = MakeProxyType('PoolProxy', (
    'apply', 'apply_async', 'close', 'imap', 'imap_unordered', 'join',
    'map', 'map_async', 'starmap', 'starmap_async', 'terminate',
    ))
BasePoolProxy._method_to_typeid_ = {
    'apply_async': 'AsyncResult',
    'map_async': 'AsyncResult',
    'starmap_async': 'AsyncResult',
    'imap': 'Iterator',
    'imap_unordered': 'Iterator'
    }
kundi PoolProxy(BasePoolProxy):
    eleza __enter__(self):
        rudisha self
    eleza __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()

#
# Definition of SyncManager
#

kundi SyncManager(BaseManager):
    '''
    Subkundi of `BaseManager` which supports a number of shared object types.

    The types registered are those intended kila the synchronization
    of threads, plus `dict`, `list` na `Namespace`.

    The `multiprocessing.Manager()` function creates started instances of
    this class.
    '''

SyncManager.register('Queue', queue.Queue)
SyncManager.register('JoinableQueue', queue.Queue)
SyncManager.register('Event', threading.Event, EventProxy)
SyncManager.register('Lock', threading.Lock, AcquirerProxy)
SyncManager.register('RLock', threading.RLock, AcquirerProxy)
SyncManager.register('Semaphore', threading.Semaphore, AcquirerProxy)
SyncManager.register('BoundedSemaphore', threading.BoundedSemaphore,
                     AcquirerProxy)
SyncManager.register('Condition', threading.Condition, ConditionProxy)
SyncManager.register('Barrier', threading.Barrier, BarrierProxy)
SyncManager.register('Pool', pool.Pool, PoolProxy)
SyncManager.register('list', list, ListProxy)
SyncManager.register('dict', dict, DictProxy)
SyncManager.register('Value', Value, ValueProxy)
SyncManager.register('Array', Array, ArrayProxy)
SyncManager.register('Namespace', Namespace, NamespaceProxy)

# types rudishaed by methods of PoolProxy
SyncManager.register('Iterator', proxytype=IteratorProxy, create_method=Uongo)
SyncManager.register('AsyncResult', create_method=Uongo)

#
# Definition of SharedMemoryManager na SharedMemoryServer
#

ikiwa HAS_SHMEM:
    kundi _SharedMemoryTracker:
        "Manages one ama more shared memory segments."

        eleza __init__(self, name, segment_names=[]):
            self.shared_memory_context_name = name
            self.segment_names = segment_names

        eleza register_segment(self, segment_name):
            "Adds the supplied shared memory block name to tracker."
            util.debug(f"Register segment {segment_name!r} kwenye pid {getpid()}")
            self.segment_names.append(segment_name)

        eleza destroy_segment(self, segment_name):
            """Calls unlink() on the shared memory block ukijumuisha the supplied name
            na removes it kutoka the list of blocks being tracked."""
            util.debug(f"Destroy segment {segment_name!r} kwenye pid {getpid()}")
            self.segment_names.remove(segment_name)
            segment = shared_memory.SharedMemory(segment_name)
            segment.close()
            segment.unlink()

        eleza unlink(self):
            "Calls destroy_segment() on all tracked shared memory blocks."
            kila segment_name kwenye self.segment_names[:]:
                self.destroy_segment(segment_name)

        eleza __del__(self):
            util.debug(f"Call {self.__class__.__name__}.__del__ kwenye {getpid()}")
            self.unlink()

        eleza __getstate__(self):
            rudisha (self.shared_memory_context_name, self.segment_names)

        eleza __setstate__(self, state):
            self.__init__(*state)


    kundi SharedMemoryServer(Server):

        public = Server.public + \
                 ['track_segment', 'release_segment', 'list_segments']

        eleza __init__(self, *args, **kwargs):
            Server.__init__(self, *args, **kwargs)
            self.shared_memory_context = \
                _SharedMemoryTracker(f"shmm_{self.address}_{getpid()}")
            util.debug(f"SharedMemoryServer started by pid {getpid()}")

        eleza create(*args, **kwargs):
            """Create a new distributed-shared object (not backed by a shared
            memory block) na rudisha its id to be used kwenye a Proxy Object."""
            # Unless set up kama a shared proxy, don't make shared_memory_context
            # a standard part of kwargs.  This makes things easier kila supplying
            # simple functions.
            ikiwa len(args) >= 3:
                typeod = args[2]
            lasivyo 'typeid' kwenye kwargs:
                typeid = kwargs['typeid']
            lasivyo sio args:
                ashiria TypeError("descriptor 'create' of 'SharedMemoryServer' "
                                "object needs an argument")
            isipokua:
                ashiria TypeError('create expected at least 2 positional '
                                'arguments, got %d' % (len(args)-1))
            ikiwa hasattr(self.registry[typeid][-1], "_shared_memory_proxy"):
                kwargs['shared_memory_context'] = self.shared_memory_context
            rudisha Server.create(*args, **kwargs)
        create.__text_signature__ = '($self, c, typeid, /, *args, **kwargs)'

        eleza shutdown(self, c):
            "Call unlink() on all tracked shared memory, terminate the Server."
            self.shared_memory_context.unlink()
            rudisha Server.shutdown(self, c)

        eleza track_segment(self, c, segment_name):
            "Adds the supplied shared memory block name to Server's tracker."
            self.shared_memory_context.register_segment(segment_name)

        eleza release_segment(self, c, segment_name):
            """Calls unlink() on the shared memory block ukijumuisha the supplied name
            na removes it kutoka the tracker instance inside the Server."""
            self.shared_memory_context.destroy_segment(segment_name)

        eleza list_segments(self, c):
            """Returns a list of names of shared memory blocks that the Server
            ni currently tracking."""
            rudisha self.shared_memory_context.segment_names


    kundi SharedMemoryManager(BaseManager):
        """Like SyncManager but uses SharedMemoryServer instead of Server.

        It provides methods kila creating na rudishaing SharedMemory instances
        na kila creating a list-like object (ShareableList) backed by shared
        memory.  It also provides methods that create na rudisha Proxy Objects
        that support synchronization across processes (i.e. multi-process-safe
        locks na semaphores).
        """

        _Server = SharedMemoryServer

        eleza __init__(self, *args, **kwargs):
            ikiwa os.name == "posix":
                # bpo-36867: Ensure the resource_tracker ni running before
                # launching the manager process, so that concurrent
                # shared_memory manipulation both kwenye the manager na kwenye the
                # current process does sio create two resource_tracker
                # processes.
                kutoka . agiza resource_tracker
                resource_tracker.ensure_running()
            BaseManager.__init__(self, *args, **kwargs)
            util.debug(f"{self.__class__.__name__} created by pid {getpid()}")

        eleza __del__(self):
            util.debug(f"{self.__class__.__name__}.__del__ by pid {getpid()}")
            pita

        eleza get_server(self):
            'Better than monkeypatching kila now; merge into Server ultimately'
            ikiwa self._state.value != State.INITIAL:
                ikiwa self._state.value == State.STARTED:
                    ashiria ProcessError("Already started SharedMemoryServer")
                lasivyo self._state.value == State.SHUTDOWN:
                    ashiria ProcessError("SharedMemoryManager has shut down")
                isipokua:
                    ashiria ProcessError(
                        "Unknown state {!r}".format(self._state.value))
            rudisha self._Server(self._registry, self._address,
                                self._authkey, self._serializer)

        eleza SharedMemory(self, size):
            """Returns a new SharedMemory instance ukijumuisha the specified size in
            bytes, to be tracked by the manager."""
            ukijumuisha self._Client(self._address, authkey=self._authkey) kama conn:
                sms = shared_memory.SharedMemory(Tupu, create=Kweli, size=size)
                jaribu:
                    dispatch(conn, Tupu, 'track_segment', (sms.name,))
                tatizo BaseException kama e:
                    sms.unlink()
                    ashiria e
            rudisha sms

        eleza ShareableList(self, sequence):
            """Returns a new ShareableList instance populated ukijumuisha the values
            kutoka the input sequence, to be tracked by the manager."""
            ukijumuisha self._Client(self._address, authkey=self._authkey) kama conn:
                sl = shared_memory.ShareableList(sequence)
                jaribu:
                    dispatch(conn, Tupu, 'track_segment', (sl.shm.name,))
                tatizo BaseException kama e:
                    sl.shm.unlink()
                    ashiria e
            rudisha sl
