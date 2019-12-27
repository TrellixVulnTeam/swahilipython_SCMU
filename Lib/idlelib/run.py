""" idlelib.run

Simplified, pyshell.ModifiedInterpreter spawns a subprocess with
f'''{sys.executable} -c "__import__('idlelib.run').run.main()"'''
'.run' is needed because __import__ returns idlelib, not idlelib.run.
"""
agiza functools
agiza io
agiza linecache
agiza queue
agiza sys
agiza textwrap
agiza time
agiza traceback
agiza _thread as thread
agiza threading
agiza warnings

kutoka idlelib agiza autocomplete  # AutoComplete, fetch_encodings
kutoka idlelib agiza calltip  # Calltip
kutoka idlelib agiza debugger_r  # start_debugger
kutoka idlelib agiza debugobj_r  # remote_object_tree_item
kutoka idlelib agiza iomenu  # encoding
kutoka idlelib agiza rpc  # multiple objects
kutoka idlelib agiza stackviewer  # StackTreeItem
agiza __main__

agiza tkinter  # Use tcl and, ikiwa startup fails, messagebox.
ikiwa not hasattr(sys.modules['idlelib.run'], 'firstrun'):
    # Undo modifications of tkinter by idlelib agizas; see bpo-25507.
    for mod in ('simpledialog', 'messagebox', 'font',
                'dialog', 'filedialog', 'commondialog',
                'ttk'):
        delattr(tkinter, mod)
        del sys.modules['tkinter.' + mod]
    # Avoid AttributeError ikiwa run again; see bpo-37038.
    sys.modules['idlelib.run'].firstrun = False

LOCALHOST = '127.0.0.1'


eleza idle_formatwarning(message, category, filename, lineno, line=None):
    """Format warnings the IDLE way."""

    s = "\nWarning (kutoka warnings module):\n"
    s += '  File \"%s\", line %s\n' % (filename, lineno)
    ikiwa line is None:
        line = linecache.getline(filename, lineno)
    line = line.strip()
    ikiwa line:
        s += "    %s\n" % line
    s += "%s: %s\n" % (category.__name__, message)
    rudisha s

eleza idle_showwarning_subproc(
        message, category, filename, lineno, file=None, line=None):
    """Show Idle-format warning after replacing warnings.showwarning.

    The only difference is the formatter called.
    """
    ikiwa file is None:
        file = sys.stderr
    try:
        file.write(idle_formatwarning(
                message, category, filename, lineno, line))
    except OSError:
        pass # the file (probably stderr) is invalid - this warning gets lost.

_warnings_showwarning = None

eleza capture_warnings(capture):
    "Replace warning.showwarning with idle_showwarning_subproc, or reverse."

    global _warnings_showwarning
    ikiwa capture:
        ikiwa _warnings_showwarning is None:
            _warnings_showwarning = warnings.showwarning
            warnings.showwarning = idle_showwarning_subproc
    else:
        ikiwa _warnings_showwarning is not None:
            warnings.showwarning = _warnings_showwarning
            _warnings_showwarning = None

capture_warnings(True)
tcl = tkinter.Tcl()

eleza handle_tk_events(tcl=tcl):
    """Process any tk events that are ready to be dispatched ikiwa tkinter
    has been imported, a tcl interpreter has been created and tk has been
    loaded."""
    tcl.eval("update")

# Thread shared globals: Establish a queue between a subthread (which handles
# the socket) and the main thread (which runs user code), plus global
# completion, exit and interruptable (the main thread) flags:

exit_now = False
quitting = False
interruptable = False

eleza main(del_exitfunc=False):
    """Start the Python execution server in a subprocess

    In the Python subprocess, RPCServer is instantiated with handlerclass
    MyHandler, which inherits register/unregister methods kutoka RPCHandler via
    the mix-in kundi SocketIO.

    When the RPCServer 'server' is instantiated, the TCPServer initialization
    creates an instance of run.MyHandler and calls its handle() method.
    handle() instantiates a run.Executive object, passing it a reference to the
    MyHandler object.  That reference is saved as attribute rpchandler of the
    Executive instance.  The Executive methods have access to the reference and
    can pass it on to entities that they command
    (e.g. debugger_r.Debugger.start_debugger()).  The latter, in turn, can
    call MyHandler(SocketIO) register/unregister methods via the reference to
    register and unregister themselves.

    """
    global exit_now
    global quitting
    global no_exitfunc
    no_exitfunc = del_exitfunc
    #time.sleep(15) # test subprocess not responding
    try:
        assert(len(sys.argv) > 1)
        port = int(sys.argv[-1])
    except:
        andika("IDLE Subprocess: no IP port passed in sys.argv.",
              file=sys.__stderr__)
        return

    capture_warnings(True)
    sys.argv[:] = [""]
    sockthread = threading.Thread(target=manage_socket,
                                  name='SockThread',
                                  args=((LOCALHOST, port),))
    sockthread.daemon = True
    sockthread.start()
    while 1:
        try:
            ikiwa exit_now:
                try:
                    exit()
                except KeyboardInterrupt:
                    # exiting but got an extra KBI? Try again!
                    continue
            try:
                request = rpc.request_queue.get(block=True, timeout=0.05)
            except queue.Empty:
                request = None
                # Issue 32207: calling handle_tk_events here adds spurious
                # queue.Empty traceback to event handling exceptions.
            ikiwa request:
                seq, (method, args, kwargs) = request
                ret = method(*args, **kwargs)
                rpc.response_queue.put((seq, ret))
            else:
                handle_tk_events()
        except KeyboardInterrupt:
            ikiwa quitting:
                exit_now = True
            continue
        except SystemExit:
            capture_warnings(False)
            raise
        except:
            type, value, tb = sys.exc_info()
            try:
                print_exception()
                rpc.response_queue.put((seq, None))
            except:
                # Link didn't work, print same exception to __stderr__
                traceback.print_exception(type, value, tb, file=sys.__stderr__)
                exit()
            else:
                continue

eleza manage_socket(address):
    for i in range(3):
        time.sleep(i)
        try:
            server = MyRPCServer(address, MyHandler)
            break
        except OSError as err:
            andika("IDLE Subprocess: OSError: " + err.args[1] +
                  ", retrying....", file=sys.__stderr__)
            socket_error = err
    else:
        andika("IDLE Subprocess: Connection to "
              "IDLE GUI failed, exiting.", file=sys.__stderr__)
        show_socket_error(socket_error, address)
        global exit_now
        exit_now = True
        return
    server.handle_request() # A single request only

eleza show_socket_error(err, address):
    "Display socket error kutoka manage_socket."
    agiza tkinter
    kutoka tkinter.messagebox agiza showerror
    root = tkinter.Tk()
    fix_scaling(root)
    root.withdraw()
    showerror(
            "Subprocess Connection Error",
            f"IDLE's subprocess can't connect to {address[0]}:{address[1]}.\n"
            f"Fatal OSError #{err.errno}: {err.strerror}.\n"
            "See the 'Startup failure' section of the IDLE doc, online at\n"
            "https://docs.python.org/3/library/idle.html#startup-failure",
            parent=root)
    root.destroy()

eleza print_exception():
    agiza linecache
    linecache.checkcache()
    flush_stdout()
    efile = sys.stderr
    typ, val, tb = excinfo = sys.exc_info()
    sys.last_type, sys.last_value, sys.last_traceback = excinfo
    seen = set()

    eleza print_exc(typ, exc, tb):
        seen.add(id(exc))
        context = exc.__context__
        cause = exc.__cause__
        ikiwa cause is not None and id(cause) not in seen:
            print_exc(type(cause), cause, cause.__traceback__)
            andika("\nThe above exception was the direct cause "
                  "of the following exception:\n", file=efile)
        elikiwa (context is not None and
              not exc.__suppress_context__ and
              id(context) not in seen):
            print_exc(type(context), context, context.__traceback__)
            andika("\nDuring handling of the above exception, "
                  "another exception occurred:\n", file=efile)
        ikiwa tb:
            tbe = traceback.extract_tb(tb)
            andika('Traceback (most recent call last):', file=efile)
            exclude = ("run.py", "rpc.py", "threading.py", "queue.py",
                       "debugger_r.py", "bdb.py")
            cleanup_traceback(tbe, exclude)
            traceback.print_list(tbe, file=efile)
        lines = traceback.format_exception_only(typ, exc)
        for line in lines:
            andika(line, end='', file=efile)

    print_exc(typ, val, tb)

eleza cleanup_traceback(tb, exclude):
    "Remove excluded traces kutoka beginning/end of tb; get cached lines"
    orig_tb = tb[:]
    while tb:
        for rpcfile in exclude:
            ikiwa tb[0][0].count(rpcfile):
                break    # found an exclude, break for: and delete tb[0]
        else:
            break        # no excludes, have left RPC code, break while:
        del tb[0]
    while tb:
        for rpcfile in exclude:
            ikiwa tb[-1][0].count(rpcfile):
                break
        else:
            break
        del tb[-1]
    ikiwa len(tb) == 0:
        # exception was in IDLE internals, don't prune!
        tb[:] = orig_tb[:]
        andika("** IDLE Internal Exception: ", file=sys.stderr)
    rpchandler = rpc.objecttable['exec'].rpchandler
    for i in range(len(tb)):
        fn, ln, nm, line = tb[i]
        ikiwa nm == '?':
            nm = "-toplevel-"
        ikiwa not line and fn.startswith("<pyshell#"):
            line = rpchandler.remotecall('linecache', 'getline',
                                              (fn, ln), {})
        tb[i] = fn, ln, nm, line

eleza flush_stdout():
    """XXX How to do this now?"""

eleza exit():
    """Exit subprocess, possibly after first clearing exit functions.

    If config-main.cfg/.eleza 'General' 'delete-exitfunc' is True, then any
    functions registered with atexit will be removed before exiting.
    (VPython support)

    """
    ikiwa no_exitfunc:
        agiza atexit
        atexit._clear()
    capture_warnings(False)
    sys.exit(0)


eleza fix_scaling(root):
    """Scale fonts on HiDPI displays."""
    agiza tkinter.font
    scaling = float(root.tk.call('tk', 'scaling'))
    ikiwa scaling > 1.4:
        for name in tkinter.font.names(root):
            font = tkinter.font.Font(root=root, name=name, exists=True)
            size = int(font['size'])
            ikiwa size < 0:
                font['size'] = round(-0.75*size)


eleza fixdoc(fun, text):
    tem = (fun.__doc__ + '\n\n') ikiwa fun.__doc__ is not None else ''
    fun.__doc__ = tem + textwrap.fill(textwrap.dedent(text))

RECURSIONLIMIT_DELTA = 30

eleza install_recursionlimit_wrappers():
    """Install wrappers to always add 30 to the recursion limit."""
    # see: bpo-26806

    @functools.wraps(sys.setrecursionlimit)
    eleza setrecursionlimit(*args, **kwargs):
        # mimic the original sys.setrecursionlimit()'s input handling
        ikiwa kwargs:
            raise TypeError(
                "setrecursionlimit() takes no keyword arguments")
        try:
            limit, = args
        except ValueError:
            raise TypeError(f"setrecursionlimit() takes exactly one "
                            f"argument ({len(args)} given)")
        ikiwa not limit > 0:
            raise ValueError(
                "recursion limit must be greater or equal than 1")

        rudisha setrecursionlimit.__wrapped__(limit + RECURSIONLIMIT_DELTA)

    fixdoc(setrecursionlimit, f"""\
            This IDLE wrapper adds {RECURSIONLIMIT_DELTA} to prevent possible
            uninterruptible loops.""")

    @functools.wraps(sys.getrecursionlimit)
    eleza getrecursionlimit():
        rudisha getrecursionlimit.__wrapped__() - RECURSIONLIMIT_DELTA

    fixdoc(getrecursionlimit, f"""\
            This IDLE wrapper subtracts {RECURSIONLIMIT_DELTA} to compensate
            for the {RECURSIONLIMIT_DELTA} IDLE adds when setting the limit.""")

    # add the delta to the default recursion limit, to compensate
    sys.setrecursionlimit(sys.getrecursionlimit() + RECURSIONLIMIT_DELTA)

    sys.setrecursionlimit = setrecursionlimit
    sys.getrecursionlimit = getrecursionlimit


eleza uninstall_recursionlimit_wrappers():
    """Uninstall the recursion limit wrappers kutoka the sys module.

    IDLE only uses this for tests. Users can agiza run and call
    this to remove the wrapping.
    """
    ikiwa (
            getattr(sys.setrecursionlimit, '__wrapped__', None) and
            getattr(sys.getrecursionlimit, '__wrapped__', None)
    ):
        sys.setrecursionlimit = sys.setrecursionlimit.__wrapped__
        sys.getrecursionlimit = sys.getrecursionlimit.__wrapped__
        sys.setrecursionlimit(sys.getrecursionlimit() - RECURSIONLIMIT_DELTA)


kundi MyRPCServer(rpc.RPCServer):

    eleza handle_error(self, request, client_address):
        """Override RPCServer method for IDLE

        Interrupt the MainThread and exit server ikiwa link is dropped.

        """
        global quitting
        try:
            raise
        except SystemExit:
            raise
        except EOFError:
            global exit_now
            exit_now = True
            thread.interrupt_main()
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
            quitting = True
            thread.interrupt_main()


# Pseudofiles for shell-remote communication (also used in pyshell)

kundi StdioFile(io.TextIOBase):

    eleza __init__(self, shell, tags, encoding='utf-8', errors='strict'):
        self.shell = shell
        self.tags = tags
        self._encoding = encoding
        self._errors = errors

    @property
    eleza encoding(self):
        rudisha self._encoding

    @property
    eleza errors(self):
        rudisha self._errors

    @property
    eleza name(self):
        rudisha '<%s>' % self.tags

    eleza isatty(self):
        rudisha True


kundi StdOutputFile(StdioFile):

    eleza writable(self):
        rudisha True

    eleza write(self, s):
        ikiwa self.closed:
            raise ValueError("write to closed file")
        s = str.encode(s, self.encoding, self.errors).decode(self.encoding, self.errors)
        rudisha self.shell.write(s, self.tags)


kundi StdInputFile(StdioFile):
    _line_buffer = ''

    eleza readable(self):
        rudisha True

    eleza read(self, size=-1):
        ikiwa self.closed:
            raise ValueError("read kutoka closed file")
        ikiwa size is None:
            size = -1
        elikiwa not isinstance(size, int):
            raise TypeError('must be int, not ' + type(size).__name__)
        result = self._line_buffer
        self._line_buffer = ''
        ikiwa size < 0:
            while True:
                line = self.shell.readline()
                ikiwa not line: break
                result += line
        else:
            while len(result) < size:
                line = self.shell.readline()
                ikiwa not line: break
                result += line
            self._line_buffer = result[size:]
            result = result[:size]
        rudisha result

    eleza readline(self, size=-1):
        ikiwa self.closed:
            raise ValueError("read kutoka closed file")
        ikiwa size is None:
            size = -1
        elikiwa not isinstance(size, int):
            raise TypeError('must be int, not ' + type(size).__name__)
        line = self._line_buffer or self.shell.readline()
        ikiwa size < 0:
            size = len(line)
        eol = line.find('\n', 0, size)
        ikiwa eol >= 0:
            size = eol + 1
        self._line_buffer = line[size:]
        rudisha line[:size]

    eleza close(self):
        self.shell.close()


kundi MyHandler(rpc.RPCHandler):

    eleza handle(self):
        """Override base method"""
        executive = Executive(self)
        self.register("exec", executive)
        self.console = self.get_remote_proxy("console")
        sys.stdin = StdInputFile(self.console, "stdin",
                                 iomenu.encoding, iomenu.errors)
        sys.stdout = StdOutputFile(self.console, "stdout",
                                   iomenu.encoding, iomenu.errors)
        sys.stderr = StdOutputFile(self.console, "stderr",
                                   iomenu.encoding, "backslashreplace")

        sys.displayhook = rpc.displayhook
        # page help() text to shell.
        agiza pydoc # agiza must be done here to capture i/o binding
        pydoc.pager = pydoc.plainpager

        # Keep a reference to stdin so that it won't try to exit IDLE if
        # sys.stdin gets changed kutoka within IDLE's shell. See issue17838.
        self._keep_stdin = sys.stdin

        install_recursionlimit_wrappers()

        self.interp = self.get_remote_proxy("interp")
        rpc.RPCHandler.getresponse(self, myseq=None, wait=0.05)

    eleza exithook(self):
        "override SocketIO method - wait for MainThread to shut us down"
        time.sleep(10)

    eleza EOFhook(self):
        "Override SocketIO method - terminate wait on callback and exit thread"
        global quitting
        quitting = True
        thread.interrupt_main()

    eleza decode_interrupthook(self):
        "interrupt awakened thread"
        global quitting
        quitting = True
        thread.interrupt_main()


kundi Executive(object):

    eleza __init__(self, rpchandler):
        self.rpchandler = rpchandler
        self.locals = __main__.__dict__
        self.calltip = calltip.Calltip()
        self.autocomplete = autocomplete.AutoComplete()

    eleza runcode(self, code):
        global interruptable
        try:
            self.usr_exc_info = None
            interruptable = True
            try:
                exec(code, self.locals)
            finally:
                interruptable = False
        except SystemExit as e:
            ikiwa e.args:  # SystemExit called with an argument.
                ob = e.args[0]
                ikiwa not isinstance(ob, (type(None), int)):
                    andika('SystemExit: ' + str(ob), file=sys.stderr)
            # Return to the interactive prompt.
        except:
            self.usr_exc_info = sys.exc_info()
            ikiwa quitting:
                exit()
            print_exception()
            jit = self.rpchandler.console.getvar("<<toggle-jit-stack-viewer>>")
            ikiwa jit:
                self.rpchandler.interp.open_remote_stack_viewer()
        else:
            flush_stdout()

    eleza interrupt_the_server(self):
        ikiwa interruptable:
            thread.interrupt_main()

    eleza start_the_debugger(self, gui_adap_oid):
        rudisha debugger_r.start_debugger(self.rpchandler, gui_adap_oid)

    eleza stop_the_debugger(self, idb_adap_oid):
        "Unregister the Idb Adapter.  Link objects and Idb then subject to GC"
        self.rpchandler.unregister(idb_adap_oid)

    eleza get_the_calltip(self, name):
        rudisha self.calltip.fetch_tip(name)

    eleza get_the_completion_list(self, what, mode):
        rudisha self.autocomplete.fetch_completions(what, mode)

    eleza stackviewer(self, flist_oid=None):
        ikiwa self.usr_exc_info:
            typ, val, tb = self.usr_exc_info
        else:
            rudisha None
        flist = None
        ikiwa flist_oid is not None:
            flist = self.rpchandler.get_remote_proxy(flist_oid)
        while tb and tb.tb_frame.f_globals["__name__"] in ["rpc", "run"]:
            tb = tb.tb_next
        sys.last_type = typ
        sys.last_value = val
        item = stackviewer.StackTreeItem(flist, tb)
        rudisha debugobj_r.remote_object_tree_item(item)


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_run', verbosity=2)

capture_warnings(False)  # Make sure turned off; see bpo-18081.
