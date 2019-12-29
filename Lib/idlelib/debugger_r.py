"""Support kila remote Python debugging.

Some ASCII art to describe the structure:

       IN PYTHON SUBPROCESS          #             IN IDLE PROCESS
                                     #
                                     #        oid='gui_adapter'
                 +----------+        #       +------------+          +-----+
                 | GUIProxy |--remote#call-->| GUIAdapter |--calls-->| GUI |
+-----+--calls-->+----------+        #       +------------+          +-----+
| Idb |                               #                             /
+-----+<-calls--+------------+         #      +----------+<--calls-/
                | IdbAdapter |<--remote#call--| IdbProxy |
                +------------+         #      +----------+
                oid='idb_adapter'      #

The purpose of the Proxy na Adapter classes ni to translate certain
arguments na rudisha values that cannot be transported through the RPC
barrier, kwenye particular frame na traceback objects.

"""

agiza types
kutoka idlelib agiza debugger

debugging = 0

idb_adap_oid = "idb_adapter"
gui_adap_oid = "gui_adapter"

#=======================================
#
# In the PYTHON subprocess:

frametable = {}
dicttable = {}
codetable = {}
tracebacktable = {}

eleza wrap_frame(frame):
    fid = id(frame)
    frametable[fid] = frame
    rudisha fid

eleza wrap_info(info):
    "replace info[2], a traceback instance, by its ID"
    ikiwa info ni Tupu:
        rudisha Tupu
    isipokua:
        traceback = info[2]
        assert isinstance(traceback, types.TracebackType)
        traceback_id = id(traceback)
        tracebacktable[traceback_id] = traceback
        modified_info = (info[0], info[1], traceback_id)
        rudisha modified_info

kundi GUIProxy:

    eleza __init__(self, conn, gui_adap_oid):
        self.conn = conn
        self.oid = gui_adap_oid

    eleza interaction(self, message, frame, info=Tupu):
        # calls rpc.SocketIO.remotecall() via run.MyHandler instance
        # pita frame na traceback object IDs instead of the objects themselves
        self.conn.remotecall(self.oid, "interaction",
                             (message, wrap_frame(frame), wrap_info(info)),
                             {})

kundi IdbAdapter:

    eleza __init__(self, idb):
        self.idb = idb

    #----------called by an IdbProxy----------

    eleza set_step(self):
        self.idb.set_step()

    eleza set_quit(self):
        self.idb.set_quit()

    eleza set_endelea(self):
        self.idb.set_endelea()

    eleza set_next(self, fid):
        frame = frametable[fid]
        self.idb.set_next(frame)

    eleza set_rudisha(self, fid):
        frame = frametable[fid]
        self.idb.set_rudisha(frame)

    eleza get_stack(self, fid, tbid):
        frame = frametable[fid]
        ikiwa tbid ni Tupu:
            tb = Tupu
        isipokua:
            tb = tracebacktable[tbid]
        stack, i = self.idb.get_stack(frame, tb)
        stack = [(wrap_frame(frame2), k) kila frame2, k kwenye stack]
        rudisha stack, i

    eleza run(self, cmd):
        agiza __main__
        self.idb.run(cmd, __main__.__dict__)

    eleza set_koma(self, filename, lineno):
        msg = self.idb.set_koma(filename, lineno)
        rudisha msg

    eleza clear_koma(self, filename, lineno):
        msg = self.idb.clear_koma(filename, lineno)
        rudisha msg

    eleza clear_all_file_komas(self, filename):
        msg = self.idb.clear_all_file_komas(filename)
        rudisha msg

    #----------called by a FrameProxy----------

    eleza frame_attr(self, fid, name):
        frame = frametable[fid]
        rudisha getattr(frame, name)

    eleza frame_globals(self, fid):
        frame = frametable[fid]
        dict = frame.f_globals
        did = id(dict)
        dicttable[did] = dict
        rudisha did

    eleza frame_locals(self, fid):
        frame = frametable[fid]
        dict = frame.f_locals
        did = id(dict)
        dicttable[did] = dict
        rudisha did

    eleza frame_code(self, fid):
        frame = frametable[fid]
        code = frame.f_code
        cid = id(code)
        codetable[cid] = code
        rudisha cid

    #----------called by a CodeProxy----------

    eleza code_name(self, cid):
        code = codetable[cid]
        rudisha code.co_name

    eleza code_filename(self, cid):
        code = codetable[cid]
        rudisha code.co_filename

    #----------called by a DictProxy----------

    eleza dict_keys(self, did):
        ashiria NotImplementedError("dict_keys sio public ama pickleable")
##         dict = dicttable[did]
##         rudisha dict.keys()

    ### Needed until dict_keys ni type ni finished na pickealable.
    ### Will probably need to extend rpc.py:SocketIO._proxify at that time.
    eleza dict_keys_list(self, did):
        dict = dicttable[did]
        rudisha list(dict.keys())

    eleza dict_item(self, did, key):
        dict = dicttable[did]
        value = dict[key]
        value = repr(value) ### can't pickle module 'builtins'
        rudisha value

#----------end kundi IdbAdapter----------


eleza start_debugger(rpchandler, gui_adap_oid):
    """Start the debugger na its RPC link kwenye the Python subprocess

    Start the subprocess side of the split debugger na set up that side of the
    RPC link by instantiating the GUIProxy, Idb debugger, na IdbAdapter
    objects na linking them together.  Register the IdbAdapter ukijumuisha the
    RPCServer to handle RPC requests kutoka the split debugger GUI via the
    IdbProxy.

    """
    gui_proxy = GUIProxy(rpchandler, gui_adap_oid)
    idb = debugger.Idb(gui_proxy)
    idb_adap = IdbAdapter(idb)
    rpchandler.register(idb_adap_oid, idb_adap)
    rudisha idb_adap_oid


#=======================================
#
# In the IDLE process:


kundi FrameProxy:

    eleza __init__(self, conn, fid):
        self._conn = conn
        self._fid = fid
        self._oid = "idb_adapter"
        self._dictcache = {}

    eleza __getattr__(self, name):
        ikiwa name[:1] == "_":
            ashiria AttributeError(name)
        ikiwa name == "f_code":
            rudisha self._get_f_code()
        ikiwa name == "f_globals":
            rudisha self._get_f_globals()
        ikiwa name == "f_locals":
            rudisha self._get_f_locals()
        rudisha self._conn.remotecall(self._oid, "frame_attr",
                                     (self._fid, name), {})

    eleza _get_f_code(self):
        cid = self._conn.remotecall(self._oid, "frame_code", (self._fid,), {})
        rudisha CodeProxy(self._conn, self._oid, cid)

    eleza _get_f_globals(self):
        did = self._conn.remotecall(self._oid, "frame_globals",
                                    (self._fid,), {})
        rudisha self._get_dict_proxy(did)

    eleza _get_f_locals(self):
        did = self._conn.remotecall(self._oid, "frame_locals",
                                    (self._fid,), {})
        rudisha self._get_dict_proxy(did)

    eleza _get_dict_proxy(self, did):
        ikiwa did kwenye self._dictcache:
            rudisha self._dictcache[did]
        dp = DictProxy(self._conn, self._oid, did)
        self._dictcache[did] = dp
        rudisha dp


kundi CodeProxy:

    eleza __init__(self, conn, oid, cid):
        self._conn = conn
        self._oid = oid
        self._cid = cid

    eleza __getattr__(self, name):
        ikiwa name == "co_name":
            rudisha self._conn.remotecall(self._oid, "code_name",
                                         (self._cid,), {})
        ikiwa name == "co_filename":
            rudisha self._conn.remotecall(self._oid, "code_filename",
                                         (self._cid,), {})


kundi DictProxy:

    eleza __init__(self, conn, oid, did):
        self._conn = conn
        self._oid = oid
        self._did = did

##    eleza keys(self):
##        rudisha self._conn.remotecall(self._oid, "dict_keys", (self._did,), {})

    # 'temporary' until dict_keys ni a pickleable built-in type
    eleza keys(self):
        rudisha self._conn.remotecall(self._oid,
                                     "dict_keys_list", (self._did,), {})

    eleza __getitem__(self, key):
        rudisha self._conn.remotecall(self._oid, "dict_item",
                                     (self._did, key), {})

    eleza __getattr__(self, name):
        ##andika("*** Failed DictProxy.__getattr__:", name)
        ashiria AttributeError(name)


kundi GUIAdapter:

    eleza __init__(self, conn, gui):
        self.conn = conn
        self.gui = gui

    eleza interaction(self, message, fid, modified_info):
        ##andika("*** Interaction: (%s, %s, %s)" % (message, fid, modified_info))
        frame = FrameProxy(self.conn, fid)
        self.gui.interaction(message, frame, modified_info)


kundi IdbProxy:

    eleza __init__(self, conn, shell, oid):
        self.oid = oid
        self.conn = conn
        self.shell = shell

    eleza call(self, methodname, /, *args, **kwargs):
        ##andika("*** IdbProxy.call %s %s %s" % (methodname, args, kwargs))
        value = self.conn.remotecall(self.oid, methodname, args, kwargs)
        ##andika("*** IdbProxy.call %s rudishas %r" % (methodname, value))
        rudisha value

    eleza run(self, cmd, locals):
        # Ignores locals on purpose!
        seq = self.conn.asyncqueue(self.oid, "run", (cmd,), {})
        self.shell.interp.active_seq = seq

    eleza get_stack(self, frame, tbid):
        # pitaing frame na traceback IDs, sio the objects themselves
        stack, i = self.call("get_stack", frame._fid, tbid)
        stack = [(FrameProxy(self.conn, fid), k) kila fid, k kwenye stack]
        rudisha stack, i

    eleza set_endelea(self):
        self.call("set_endelea")

    eleza set_step(self):
        self.call("set_step")

    eleza set_next(self, frame):
        self.call("set_next", frame._fid)

    eleza set_rudisha(self, frame):
        self.call("set_rudisha", frame._fid)

    eleza set_quit(self):
        self.call("set_quit")

    eleza set_koma(self, filename, lineno):
        msg = self.call("set_koma", filename, lineno)
        rudisha msg

    eleza clear_koma(self, filename, lineno):
        msg = self.call("clear_koma", filename, lineno)
        rudisha msg

    eleza clear_all_file_komas(self, filename):
        msg = self.call("clear_all_file_komas", filename)
        rudisha msg

eleza start_remote_debugger(rpcclt, pyshell):
    """Start the subprocess debugger, initialize the debugger GUI na RPC link

    Request the RPCServer start the Python subprocess debugger na link.  Set
    up the Idle side of the split debugger by instantiating the IdbProxy,
    debugger GUI, na debugger GUIAdapter objects na linking them together.

    Register the GUIAdapter ukijumuisha the RPCClient to handle debugger GUI
    interaction requests coming kutoka the subprocess debugger via the GUIProxy.

    The IdbAdapter will pita execution na environment requests coming kutoka the
    Idle debugger GUI to the subprocess debugger via the IdbProxy.

    """
    global idb_adap_oid

    idb_adap_oid = rpcclt.remotecall("exec", "start_the_debugger",\
                                   (gui_adap_oid,), {})
    idb_proxy = IdbProxy(rpcclt, pyshell, idb_adap_oid)
    gui = debugger.Debugger(pyshell, idb_proxy)
    gui_adap = GUIAdapter(rpcclt, gui)
    rpcclt.register(gui_adap_oid, gui_adap)
    rudisha gui

eleza close_remote_debugger(rpcclt):
    """Shut down subprocess debugger na Idle side of debugger RPC link

    Request that the RPCServer shut down the subprocess debugger na link.
    Unregister the GUIAdapter, which will cause a GC on the Idle process
    debugger na RPC link objects.  (The second reference to the debugger GUI
    ni deleted kwenye pyshell.close_remote_debugger().)

    """
    close_subprocess_debugger(rpcclt)
    rpcclt.unregister(gui_adap_oid)

eleza close_subprocess_debugger(rpcclt):
    rpcclt.remotecall("exec", "stop_the_debugger", (idb_adap_oid,), {})

eleza restart_subprocess_debugger(rpcclt):
    idb_adap_oid_ret = rpcclt.remotecall("exec", "start_the_debugger",\
                                         (gui_adap_oid,), {})
    assert idb_adap_oid_ret == idb_adap_oid, 'Idb restarted ukijumuisha different oid'


ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_debugger', verbosity=2, exit=Uongo)
