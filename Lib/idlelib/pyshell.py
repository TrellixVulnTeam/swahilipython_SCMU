#! /usr/bin/env python3

agiza sys
ikiwa __name__ == "__main__":
    sys.modules['idlelib.pyshell'] = sys.modules['__main__']

try:
    kutoka tkinter agiza *
except ImportError:
    andika("** IDLE can't agiza Tkinter.\n"
          "Your Python may not be configured for Tk. **", file=sys.__stderr__)
    raise SystemExit(1)

# Valid arguments for the ...Awareness call below are defined in the following.
# https://msdn.microsoft.com/en-us/library/windows/desktop/dn280512(v=vs.85).aspx
ikiwa sys.platform == 'win32':
    try:
        agiza ctypes
        PROCESS_SYSTEM_DPI_AWARE = 1
        ctypes.OleDLL('shcore').SetProcessDpiAwareness(PROCESS_SYSTEM_DPI_AWARE)
    except (ImportError, AttributeError, OSError):
        pass

agiza tkinter.messagebox as tkMessageBox
ikiwa TkVersion < 8.5:
    root = Tk()  # otherwise create root in main
    root.withdraw()
    kutoka idlelib.run agiza fix_scaling
    fix_scaling(root)
    tkMessageBox.showerror("Idle Cannot Start",
            "Idle requires tcl/tk 8.5+, not %s." % TkVersion,
            parent=root)
    raise SystemExit(1)

kutoka code agiza InteractiveInterpreter
agiza linecache
agiza os
agiza os.path
kutoka platform agiza python_version
agiza re
agiza socket
agiza subprocess
kutoka textwrap agiza TextWrapper
agiza threading
agiza time
agiza tokenize
agiza warnings

kutoka idlelib.colorizer agiza ColorDelegator
kutoka idlelib.config agiza idleConf
kutoka idlelib agiza debugger
kutoka idlelib agiza debugger_r
kutoka idlelib.editor agiza EditorWindow, fixwordbreaks
kutoka idlelib.filelist agiza FileList
kutoka idlelib.outwin agiza OutputWindow
kutoka idlelib agiza rpc
kutoka idlelib.run agiza idle_formatwarning, StdInputFile, StdOutputFile
kutoka idlelib.undo agiza UndoDelegator

HOST = '127.0.0.1' # python execution server on localhost loopback
PORT = 0  # someday pass in host, port for remote debug capability

# Override warnings module to write to warning_stream.  Initialize to send IDLE
# internal warnings to the console.  ScriptBinding.check_syntax() will
# temporarily redirect the stream to the shell window to display warnings when
# checking user's code.
warning_stream = sys.__stderr__  # None, at least on Windows, ikiwa no console.

eleza idle_showwarning(
        message, category, filename, lineno, file=None, line=None):
    """Show Idle-format warning (after replacing warnings.showwarning).

    The differences are the formatter called, the file=None replacement,
    which can be None, the capture of the consequence AttributeError,
    and the output of a hard-coded prompt.
    """
    ikiwa file is None:
        file = warning_stream
    try:
        file.write(idle_formatwarning(
                message, category, filename, lineno, line=line))
        file.write(">>> ")
    except (AttributeError, OSError):
        pass  # ikiwa file (probably __stderr__) is invalid, skip warning.

_warnings_showwarning = None

eleza capture_warnings(capture):
    "Replace warning.showwarning with idle_showwarning, or reverse."

    global _warnings_showwarning
    ikiwa capture:
        ikiwa _warnings_showwarning is None:
            _warnings_showwarning = warnings.showwarning
            warnings.showwarning = idle_showwarning
    else:
        ikiwa _warnings_showwarning is not None:
            warnings.showwarning = _warnings_showwarning
            _warnings_showwarning = None

capture_warnings(True)

eleza extended_linecache_checkcache(filename=None,
                                  orig_checkcache=linecache.checkcache):
    """Extend linecache.checkcache to preserve the <pyshell#...> entries

    Rather than repeating the linecache code, patch it to save the
    <pyshell#...> entries, call the original linecache.checkcache()
    (skipping them), and then restore the saved entries.

    orig_checkcache is bound at definition time to the original
    method, allowing it to be patched.
    """
    cache = linecache.cache
    save = {}
    for key in list(cache):
        ikiwa key[:1] + key[-1:] == '<>':
            save[key] = cache.pop(key)
    orig_checkcache(filename)
    cache.update(save)

# Patch linecache.checkcache():
linecache.checkcache = extended_linecache_checkcache


kundi PyShellEditorWindow(EditorWindow):
    "Regular text edit window in IDLE, supports breakpoints"

    eleza __init__(self, *args):
        self.breakpoints = []
        EditorWindow.__init__(self, *args)
        self.text.bind("<<set-breakpoint-here>>", self.set_breakpoint_here)
        self.text.bind("<<clear-breakpoint-here>>", self.clear_breakpoint_here)
        self.text.bind("<<open-python-shell>>", self.flist.open_shell)

        #TODO: don't read/write this kutoka/to .idlerc when testing
        self.breakpointPath = os.path.join(
                idleConf.userdir, 'breakpoints.lst')
        # whenever a file is changed, restore breakpoints
        eleza filename_changed_hook(old_hook=self.io.filename_change_hook,
                                  self=self):
            self.restore_file_breaks()
            old_hook()
        self.io.set_filename_change_hook(filename_changed_hook)
        ikiwa self.io.filename:
            self.restore_file_breaks()
        self.color_breakpoint_text()

    rmenu_specs = [
        ("Cut", "<<cut>>", "rmenu_check_cut"),
        ("Copy", "<<copy>>", "rmenu_check_copy"),
        ("Paste", "<<paste>>", "rmenu_check_paste"),
        (None, None, None),
        ("Set Breakpoint", "<<set-breakpoint-here>>", None),
        ("Clear Breakpoint", "<<clear-breakpoint-here>>", None)
    ]

    eleza color_breakpoint_text(self, color=True):
        "Turn colorizing of breakpoint text on or off"
        ikiwa self.io is None:
            # possible due to update in restore_file_breaks
            return
        ikiwa color:
            theme = idleConf.CurrentTheme()
            cfg = idleConf.GetHighlight(theme, "break")
        else:
            cfg = {'foreground': '', 'background': ''}
        self.text.tag_config('BREAK', cfg)

    eleza set_breakpoint(self, lineno):
        text = self.text
        filename = self.io.filename
        text.tag_add("BREAK", "%d.0" % lineno, "%d.0" % (lineno+1))
        try:
            self.breakpoints.index(lineno)
        except ValueError:  # only add ikiwa missing, i.e. do once
            self.breakpoints.append(lineno)
        try:    # update the subprocess debugger
            debug = self.flist.pyshell.interp.debugger
            debug.set_breakpoint_here(filename, lineno)
        except: # but debugger may not be active right now....
            pass

    eleza set_breakpoint_here(self, event=None):
        text = self.text
        filename = self.io.filename
        ikiwa not filename:
            text.bell()
            return
        lineno = int(float(text.index("insert")))
        self.set_breakpoint(lineno)

    eleza clear_breakpoint_here(self, event=None):
        text = self.text
        filename = self.io.filename
        ikiwa not filename:
            text.bell()
            return
        lineno = int(float(text.index("insert")))
        try:
            self.breakpoints.remove(lineno)
        except:
            pass
        text.tag_remove("BREAK", "insert linestart",\
                        "insert lineend +1char")
        try:
            debug = self.flist.pyshell.interp.debugger
            debug.clear_breakpoint_here(filename, lineno)
        except:
            pass

    eleza clear_file_breaks(self):
        ikiwa self.breakpoints:
            text = self.text
            filename = self.io.filename
            ikiwa not filename:
                text.bell()
                return
            self.breakpoints = []
            text.tag_remove("BREAK", "1.0", END)
            try:
                debug = self.flist.pyshell.interp.debugger
                debug.clear_file_breaks(filename)
            except:
                pass

    eleza store_file_breaks(self):
        "Save breakpoints when file is saved"
        # XXX 13 Dec 2002 KBK Currently the file must be saved before it can
        #     be run.  The breaks are saved at that time.  If we introduce
        #     a temporary file save feature the save breaks functionality
        #     needs to be re-verified, since the breaks at the time the
        #     temp file is created may differ kutoka the breaks at the last
        #     permanent save of the file.  Currently, a break introduced
        #     after a save will be effective, but not persistent.
        #     This is necessary to keep the saved breaks synched with the
        #     saved file.
        #
        #     Breakpoints are set as tagged ranges in the text.
        #     Since a modified file has to be saved before it is
        #     run, and since self.breakpoints (kutoka which the subprocess
        #     debugger is loaded) is updated during the save, the visible
        #     breaks stay synched with the subprocess even ikiwa one of these
        #     unexpected breakpoint deletions occurs.
        breaks = self.breakpoints
        filename = self.io.filename
        try:
            with open(self.breakpointPath, "r") as fp:
                lines = fp.readlines()
        except OSError:
            lines = []
        try:
            with open(self.breakpointPath, "w") as new_file:
                for line in lines:
                    ikiwa not line.startswith(filename + '='):
                        new_file.write(line)
                self.update_breakpoints()
                breaks = self.breakpoints
                ikiwa breaks:
                    new_file.write(filename + '=' + str(breaks) + '\n')
        except OSError as err:
            ikiwa not getattr(self.root, "breakpoint_error_displayed", False):
                self.root.breakpoint_error_displayed = True
                tkMessageBox.showerror(title='IDLE Error',
                    message='Unable to update breakpoint list:\n%s'
                        % str(err),
                    parent=self.text)

    eleza restore_file_breaks(self):
        self.text.update()   # this enables setting "BREAK" tags to be visible
        ikiwa self.io is None:
            # can happen ikiwa IDLE closes due to the .update() call
            return
        filename = self.io.filename
        ikiwa filename is None:
            return
        ikiwa os.path.isfile(self.breakpointPath):
            with open(self.breakpointPath, "r") as fp:
                lines = fp.readlines()
            for line in lines:
                ikiwa line.startswith(filename + '='):
                    breakpoint_linenumbers = eval(line[len(filename)+1:])
                    for breakpoint_linenumber in breakpoint_linenumbers:
                        self.set_breakpoint(breakpoint_linenumber)

    eleza update_breakpoints(self):
        "Retrieves all the breakpoints in the current window"
        text = self.text
        ranges = text.tag_ranges("BREAK")
        linenumber_list = self.ranges_to_linenumbers(ranges)
        self.breakpoints = linenumber_list

    eleza ranges_to_linenumbers(self, ranges):
        lines = []
        for index in range(0, len(ranges), 2):
            lineno = int(float(ranges[index].string))
            end = int(float(ranges[index+1].string))
            while lineno < end:
                lines.append(lineno)
                lineno += 1
        rudisha lines

# XXX 13 Dec 2002 KBK Not used currently
#    eleza saved_change_hook(self):
#        "Extend base method - clear breaks ikiwa module is modified"
#        ikiwa not self.get_saved():
#            self.clear_file_breaks()
#        EditorWindow.saved_change_hook(self)

    eleza _close(self):
        "Extend base method - clear breaks when module is closed"
        self.clear_file_breaks()
        EditorWindow._close(self)


kundi PyShellFileList(FileList):
    "Extend base class: IDLE supports a shell and breakpoints"

    # override FileList's kundi variable, instances rudisha PyShellEditorWindow
    # instead of EditorWindow when new edit windows are created.
    EditorWindow = PyShellEditorWindow

    pyshell = None

    eleza open_shell(self, event=None):
        ikiwa self.pyshell:
            self.pyshell.top.wakeup()
        else:
            self.pyshell = PyShell(self)
            ikiwa self.pyshell:
                ikiwa not self.pyshell.begin():
                    rudisha None
        rudisha self.pyshell


kundi ModifiedColorDelegator(ColorDelegator):
    "Extend base class: colorizer for the shell window itself"

    eleza __init__(self):
        ColorDelegator.__init__(self)
        self.LoadTagDefs()

    eleza recolorize_main(self):
        self.tag_remove("TODO", "1.0", "iomark")
        self.tag_add("SYNC", "1.0", "iomark")
        ColorDelegator.recolorize_main(self)

    eleza LoadTagDefs(self):
        ColorDelegator.LoadTagDefs(self)
        theme = idleConf.CurrentTheme()
        self.tagdefs.update({
            "stdin": {'background':None,'foreground':None},
            "stdout": idleConf.GetHighlight(theme, "stdout"),
            "stderr": idleConf.GetHighlight(theme, "stderr"),
            "console": idleConf.GetHighlight(theme, "console"),
        })

    eleza removecolors(self):
        # Don't remove shell color tags before "iomark"
        for tag in self.tagdefs:
            self.tag_remove(tag, "iomark", "end")

kundi ModifiedUndoDelegator(UndoDelegator):
    "Extend base class: forbid insert/delete before the I/O mark"

    eleza insert(self, index, chars, tags=None):
        try:
            ikiwa self.delegate.compare(index, "<", "iomark"):
                self.delegate.bell()
                return
        except TclError:
            pass
        UndoDelegator.insert(self, index, chars, tags)

    eleza delete(self, index1, index2=None):
        try:
            ikiwa self.delegate.compare(index1, "<", "iomark"):
                self.delegate.bell()
                return
        except TclError:
            pass
        UndoDelegator.delete(self, index1, index2)


kundi MyRPCClient(rpc.RPCClient):

    eleza handle_EOF(self):
        "Override the base kundi - just re-raise EOFError"
        raise EOFError

eleza restart_line(width, filename):  # See bpo-38141.
    """Return width long restart line formatted with filename.

    Fill line with balanced '='s, with any extras and at least one at
    the beginning.  Do not end with a trailing space.
    """
    tag = f"= RESTART: {filename or 'Shell'} ="
    ikiwa width >= len(tag):
        div, mod = divmod((width -len(tag)), 2)
        rudisha f"{(div+mod)*'='}{tag}{div*'='}"
    else:
        rudisha tag[:-2]  # Remove ' ='.


kundi ModifiedInterpreter(InteractiveInterpreter):

    eleza __init__(self, tkconsole):
        self.tkconsole = tkconsole
        locals = sys.modules['__main__'].__dict__
        InteractiveInterpreter.__init__(self, locals=locals)
        self.restarting = False
        self.subprocess_arglist = None
        self.port = PORT
        self.original_compiler_flags = self.compile.compiler.flags

    _afterid = None
    rpcclt = None
    rpcsubproc = None

    eleza spawn_subprocess(self):
        ikiwa self.subprocess_arglist is None:
            self.subprocess_arglist = self.build_subprocess_arglist()
        self.rpcsubproc = subprocess.Popen(self.subprocess_arglist)

    eleza build_subprocess_arglist(self):
        assert (self.port!=0), (
            "Socket should have been assigned a port number.")
        w = ['-W' + s for s in sys.warnoptions]
        # Maybe IDLE is installed and is being accessed via sys.path,
        # or maybe it's not installed and the idle.py script is being
        # run kutoka the IDLE source directory.
        del_exitf = idleConf.GetOption('main', 'General', 'delete-exitfunc',
                                       default=False, type='bool')
        command = "__import__('idlelib.run').run.main(%r)" % (del_exitf,)
        rudisha [sys.executable] + w + ["-c", command, str(self.port)]

    eleza start_subprocess(self):
        addr = (HOST, self.port)
        # GUI makes several attempts to acquire socket, listens for connection
        for i in range(3):
            time.sleep(i)
            try:
                self.rpcclt = MyRPCClient(addr)
                break
            except OSError:
                pass
        else:
            self.display_port_binding_error()
            rudisha None
        # ikiwa PORT was 0, system will assign an 'ephemeral' port. Find it out:
        self.port = self.rpcclt.listening_sock.getsockname()[1]
        # ikiwa PORT was not 0, probably working with a remote execution server
        ikiwa PORT != 0:
            # To allow reconnection within the 2MSL wait (cf. Stevens TCP
            # V1, 18.6),  set SO_REUSEADDR.  Note that this can be problematic
            # on Windows since the implementation allows two active sockets on
            # the same address!
            self.rpcclt.listening_sock.setsockopt(socket.SOL_SOCKET,
                                           socket.SO_REUSEADDR, 1)
        self.spawn_subprocess()
        #time.sleep(20) # test to simulate GUI not accepting connection
        # Accept the connection kutoka the Python execution server
        self.rpcclt.listening_sock.settimeout(10)
        try:
            self.rpcclt.accept()
        except socket.timeout:
            self.display_no_subprocess_error()
            rudisha None
        self.rpcclt.register("console", self.tkconsole)
        self.rpcclt.register("stdin", self.tkconsole.stdin)
        self.rpcclt.register("stdout", self.tkconsole.stdout)
        self.rpcclt.register("stderr", self.tkconsole.stderr)
        self.rpcclt.register("flist", self.tkconsole.flist)
        self.rpcclt.register("linecache", linecache)
        self.rpcclt.register("interp", self)
        self.transfer_path(with_cwd=True)
        self.poll_subprocess()
        rudisha self.rpcclt

    eleza restart_subprocess(self, with_cwd=False, filename=''):
        ikiwa self.restarting:
            rudisha self.rpcclt
        self.restarting = True
        # close only the subprocess debugger
        debug = self.getdebugger()
        ikiwa debug:
            try:
                # Only close subprocess debugger, don't unregister gui_adap!
                debugger_r.close_subprocess_debugger(self.rpcclt)
            except:
                pass
        # Kill subprocess, spawn a new one, accept connection.
        self.rpcclt.close()
        self.terminate_subprocess()
        console = self.tkconsole
        was_executing = console.executing
        console.executing = False
        self.spawn_subprocess()
        try:
            self.rpcclt.accept()
        except socket.timeout:
            self.display_no_subprocess_error()
            rudisha None
        self.transfer_path(with_cwd=with_cwd)
        console.stop_readline()
        # annotate restart in shell window and mark it
        console.text.delete("iomark", "end-1c")
        console.write('\n')
        console.write(restart_line(console.width, filename))
        console.text.mark_set("restart", "end-1c")
        console.text.mark_gravity("restart", "left")
        ikiwa not filename:
            console.showprompt()
        # restart subprocess debugger
        ikiwa debug:
            # Restarted debugger connects to current instance of debug GUI
            debugger_r.restart_subprocess_debugger(self.rpcclt)
            # reload remote debugger breakpoints for all PyShellEditWindows
            debug.load_breakpoints()
        self.compile.compiler.flags = self.original_compiler_flags
        self.restarting = False
        rudisha self.rpcclt

    eleza __request_interrupt(self):
        self.rpcclt.remotecall("exec", "interrupt_the_server", (), {})

    eleza interrupt_subprocess(self):
        threading.Thread(target=self.__request_interrupt).start()

    eleza kill_subprocess(self):
        ikiwa self._afterid is not None:
            self.tkconsole.text.after_cancel(self._afterid)
        try:
            self.rpcclt.listening_sock.close()
        except AttributeError:  # no socket
            pass
        try:
            self.rpcclt.close()
        except AttributeError:  # no socket
            pass
        self.terminate_subprocess()
        self.tkconsole.executing = False
        self.rpcclt = None

    eleza terminate_subprocess(self):
        "Make sure subprocess is terminated"
        try:
            self.rpcsubproc.kill()
        except OSError:
            # process already terminated
            return
        else:
            try:
                self.rpcsubproc.wait()
            except OSError:
                return

    eleza transfer_path(self, with_cwd=False):
        ikiwa with_cwd:        # Issue 13506
            path = ['']     # include Current Working Directory
            path.extend(sys.path)
        else:
            path = sys.path

        self.runcommand("""ikiwa 1:
        agiza sys as _sys
        _sys.path = %r
        del _sys
        \n""" % (path,))

    active_seq = None

    eleza poll_subprocess(self):
        clt = self.rpcclt
        ikiwa clt is None:
            return
        try:
            response = clt.pollresponse(self.active_seq, wait=0.05)
        except (EOFError, OSError, KeyboardInterrupt):
            # lost connection or subprocess terminated itself, restart
            # [the KBI is kutoka rpc.SocketIO.handle_EOF()]
            ikiwa self.tkconsole.closing:
                return
            response = None
            self.restart_subprocess()
        ikiwa response:
            self.tkconsole.resetoutput()
            self.active_seq = None
            how, what = response
            console = self.tkconsole.console
            ikiwa how == "OK":
                ikiwa what is not None:
                    andika(repr(what), file=console)
            elikiwa how == "EXCEPTION":
                ikiwa self.tkconsole.getvar("<<toggle-jit-stack-viewer>>"):
                    self.remote_stack_viewer()
            elikiwa how == "ERROR":
                errmsg = "pyshell.ModifiedInterpreter: Subprocess ERROR:\n"
                andika(errmsg, what, file=sys.__stderr__)
                andika(errmsg, what, file=console)
            # we received a response to the currently active seq number:
            try:
                self.tkconsole.endexecuting()
            except AttributeError:  # shell may have closed
                pass
        # Reschedule myself
        ikiwa not self.tkconsole.closing:
            self._afterid = self.tkconsole.text.after(
                self.tkconsole.pollinterval, self.poll_subprocess)

    debugger = None

    eleza setdebugger(self, debugger):
        self.debugger = debugger

    eleza getdebugger(self):
        rudisha self.debugger

    eleza open_remote_stack_viewer(self):
        """Initiate the remote stack viewer kutoka a separate thread.

        This method is called kutoka the subprocess, and by returning kutoka this
        method we allow the subprocess to unblock.  After a bit the shell
        requests the subprocess to open the remote stack viewer which returns a
        static object looking at the last exception.  It is queried through
        the RPC mechanism.

        """
        self.tkconsole.text.after(300, self.remote_stack_viewer)
        return

    eleza remote_stack_viewer(self):
        kutoka idlelib agiza debugobj_r
        oid = self.rpcclt.remotequeue("exec", "stackviewer", ("flist",), {})
        ikiwa oid is None:
            self.tkconsole.root.bell()
            return
        item = debugobj_r.StubObjectTreeItem(self.rpcclt, oid)
        kutoka idlelib.tree agiza ScrolledCanvas, TreeNode
        top = Toplevel(self.tkconsole.root)
        theme = idleConf.CurrentTheme()
        background = idleConf.GetHighlight(theme, 'normal')['background']
        sc = ScrolledCanvas(top, bg=background, highlightthickness=0)
        sc.frame.pack(expand=1, fill="both")
        node = TreeNode(sc.canvas, None, item)
        node.expand()
        # XXX Should GC the remote tree when closing the window

    gid = 0

    eleza execsource(self, source):
        "Like runsource() but assumes complete exec source"
        filename = self.stuffsource(source)
        self.execfile(filename, source)

    eleza execfile(self, filename, source=None):
        "Execute an existing file"
        ikiwa source is None:
            with tokenize.open(filename) as fp:
                source = fp.read()
                ikiwa use_subprocess:
                    source = (f"__file__ = r'''{os.path.abspath(filename)}'''\n"
                              + source + "\ndel __file__")
        try:
            code = compile(source, filename, "exec")
        except (OverflowError, SyntaxError):
            self.tkconsole.resetoutput()
            andika('*** Error in script or command!\n'
                 'Traceback (most recent call last):',
                  file=self.tkconsole.stderr)
            InteractiveInterpreter.showsyntaxerror(self, filename)
            self.tkconsole.showprompt()
        else:
            self.runcode(code)

    eleza runsource(self, source):
        "Extend base kundi method: Stuff the source in the line cache first"
        filename = self.stuffsource(source)
        self.more = 0
        # at the moment, InteractiveInterpreter expects str
        assert isinstance(source, str)
        # InteractiveInterpreter.runsource() calls its runcode() method,
        # which is overridden (see below)
        rudisha InteractiveInterpreter.runsource(self, source, filename)

    eleza stuffsource(self, source):
        "Stuff source in the filename cache"
        filename = "<pyshell#%d>" % self.gid
        self.gid = self.gid + 1
        lines = source.split("\n")
        linecache.cache[filename] = len(source)+1, 0, lines, filename
        rudisha filename

    eleza prepend_syspath(self, filename):
        "Prepend sys.path with file's directory ikiwa not already included"
        self.runcommand("""ikiwa 1:
            _filename = %r
            agiza sys as _sys
            kutoka os.path agiza dirname as _dirname
            _dir = _dirname(_filename)
            ikiwa not _dir in _sys.path:
                _sys.path.insert(0, _dir)
            del _filename, _sys, _dirname, _dir
            \n""" % (filename,))

    eleza showsyntaxerror(self, filename=None):
        """Override Interactive Interpreter method: Use Colorizing

        Color the offending position instead of printing it and pointing at it
        with a caret.

        """
        tkconsole = self.tkconsole
        text = tkconsole.text
        text.tag_remove("ERROR", "1.0", "end")
        type, value, tb = sys.exc_info()
        msg = getattr(value, 'msg', '') or value or "<no detail available>"
        lineno = getattr(value, 'lineno', '') or 1
        offset = getattr(value, 'offset', '') or 0
        ikiwa offset == 0:
            lineno += 1 #mark end of offending line
        ikiwa lineno == 1:
            pos = "iomark + %d chars" % (offset-1)
        else:
            pos = "iomark linestart + %d lines + %d chars" % \
                  (lineno-1, offset-1)
        tkconsole.colorize_syntax_error(text, pos)
        tkconsole.resetoutput()
        self.write("SyntaxError: %s\n" % msg)
        tkconsole.showprompt()

    eleza showtraceback(self):
        "Extend base kundi method to reset output properly"
        self.tkconsole.resetoutput()
        self.checklinecache()
        InteractiveInterpreter.showtraceback(self)
        ikiwa self.tkconsole.getvar("<<toggle-jit-stack-viewer>>"):
            self.tkconsole.open_stack_viewer()

    eleza checklinecache(self):
        c = linecache.cache
        for key in list(c.keys()):
            ikiwa key[:1] + key[-1:] != "<>":
                del c[key]

    eleza runcommand(self, code):
        "Run the code without invoking the debugger"
        # The code better not raise an exception!
        ikiwa self.tkconsole.executing:
            self.display_executing_dialog()
            rudisha 0
        ikiwa self.rpcclt:
            self.rpcclt.remotequeue("exec", "runcode", (code,), {})
        else:
            exec(code, self.locals)
        rudisha 1

    eleza runcode(self, code):
        "Override base kundi method"
        ikiwa self.tkconsole.executing:
            self.interp.restart_subprocess()
        self.checklinecache()
        debugger = self.debugger
        try:
            self.tkconsole.beginexecuting()
            ikiwa not debugger and self.rpcclt is not None:
                self.active_seq = self.rpcclt.asyncqueue("exec", "runcode",
                                                        (code,), {})
            elikiwa debugger:
                debugger.run(code, self.locals)
            else:
                exec(code, self.locals)
        except SystemExit:
            ikiwa not self.tkconsole.closing:
                ikiwa tkMessageBox.askyesno(
                    "Exit?",
                    "Do you want to exit altogether?",
                    default="yes",
                    parent=self.tkconsole.text):
                    raise
                else:
                    self.showtraceback()
            else:
                raise
        except:
            ikiwa use_subprocess:
                andika("IDLE internal error in runcode()",
                      file=self.tkconsole.stderr)
                self.showtraceback()
                self.tkconsole.endexecuting()
            else:
                ikiwa self.tkconsole.canceled:
                    self.tkconsole.canceled = False
                    andika("KeyboardInterrupt", file=self.tkconsole.stderr)
                else:
                    self.showtraceback()
        finally:
            ikiwa not use_subprocess:
                try:
                    self.tkconsole.endexecuting()
                except AttributeError:  # shell may have closed
                    pass

    eleza write(self, s):
        "Override base kundi method"
        rudisha self.tkconsole.stderr.write(s)

    eleza display_port_binding_error(self):
        tkMessageBox.showerror(
            "Port Binding Error",
            "IDLE can't bind to a TCP/IP port, which is necessary to "
            "communicate with its Python execution server.  This might be "
            "because no networking is installed on this computer.  "
            "Run IDLE with the -n command line switch to start without a "
            "subprocess and refer to Help/IDLE Help 'Running without a "
            "subprocess' for further details.",
            parent=self.tkconsole.text)

    eleza display_no_subprocess_error(self):
        tkMessageBox.showerror(
            "Subprocess Connection Error",
            "IDLE's subprocess didn't make connection.\n"
            "See the 'Startup failure' section of the IDLE doc, online at\n"
            "https://docs.python.org/3/library/idle.html#startup-failure",
            parent=self.tkconsole.text)

    eleza display_executing_dialog(self):
        tkMessageBox.showerror(
            "Already executing",
            "The Python Shell window is already executing a command; "
            "please wait until it is finished.",
            parent=self.tkconsole.text)


kundi PyShell(OutputWindow):

    shell_title = "Python " + python_version() + " Shell"

    # Override classes
    ColorDelegator = ModifiedColorDelegator
    UndoDelegator = ModifiedUndoDelegator

    # Override menus
    menu_specs = [
        ("file", "_File"),
        ("edit", "_Edit"),
        ("debug", "_Debug"),
        ("options", "_Options"),
        ("window", "_Window"),
        ("help", "_Help"),
    ]

    # Extend right-click context menu
    rmenu_specs = OutputWindow.rmenu_specs + [
        ("Squeeze", "<<squeeze-current-text>>"),
    ]

    allow_line_numbers = False

    # New classes
    kutoka idlelib.history agiza History

    eleza __init__(self, flist=None):
        ikiwa use_subprocess:
            ms = self.menu_specs
            ikiwa ms[2][0] != "shell":
                ms.insert(2, ("shell", "She_ll"))
        self.interp = ModifiedInterpreter(self)
        ikiwa flist is None:
            root = Tk()
            fixwordbreaks(root)
            root.withdraw()
            flist = PyShellFileList(root)

        OutputWindow.__init__(self, flist, None, None)

        self.usetabs = True
        # indentwidth must be 8 when using tabs.  See note in EditorWindow:
        self.indentwidth = 8

        self.sys_ps1 = sys.ps1 ikiwa hasattr(sys, 'ps1') else '>>> '
        self.prompt_last_line = self.sys_ps1.split('\n')[-1]
        self.prompt = self.sys_ps1  # Changes when debug active

        text = self.text
        text.configure(wrap="char")
        text.bind("<<newline-and-indent>>", self.enter_callback)
        text.bind("<<plain-newline-and-indent>>", self.linefeed_callback)
        text.bind("<<interrupt-execution>>", self.cancel_callback)
        text.bind("<<end-of-file>>", self.eof_callback)
        text.bind("<<open-stack-viewer>>", self.open_stack_viewer)
        text.bind("<<toggle-debugger>>", self.toggle_debugger)
        text.bind("<<toggle-jit-stack-viewer>>", self.toggle_jit_stack_viewer)
        ikiwa use_subprocess:
            text.bind("<<view-restart>>", self.view_restart_mark)
            text.bind("<<restart-shell>>", self.restart_shell)
        squeezer = self.Squeezer(self)
        text.bind("<<squeeze-current-text>>",
                  squeezer.squeeze_current_text_event)

        self.save_stdout = sys.stdout
        self.save_stderr = sys.stderr
        self.save_stdin = sys.stdin
        kutoka idlelib agiza iomenu
        self.stdin = StdInputFile(self, "stdin",
                                  iomenu.encoding, iomenu.errors)
        self.stdout = StdOutputFile(self, "stdout",
                                    iomenu.encoding, iomenu.errors)
        self.stderr = StdOutputFile(self, "stderr",
                                    iomenu.encoding, "backslashreplace")
        self.console = StdOutputFile(self, "console",
                                     iomenu.encoding, iomenu.errors)
        ikiwa not use_subprocess:
            sys.stdout = self.stdout
            sys.stderr = self.stderr
            sys.stdin = self.stdin
        try:
            # page help() text to shell.
            agiza pydoc # agiza must be done here to capture i/o rebinding.
            # XXX KBK 27Dec07 use text viewer someday, but must work w/o subproc
            pydoc.pager = pydoc.plainpager
        except:
            sys.stderr = sys.__stderr__
            raise
        #
        self.history = self.History(self.text)
        #
        self.pollinterval = 50  # millisec

    eleza get_standard_extension_names(self):
        rudisha idleConf.GetExtensions(shell_only=True)

    reading = False
    executing = False
    canceled = False
    endoffile = False
    closing = False
    _stop_readline_flag = False

    eleza set_warning_stream(self, stream):
        global warning_stream
        warning_stream = stream

    eleza get_warning_stream(self):
        rudisha warning_stream

    eleza toggle_debugger(self, event=None):
        ikiwa self.executing:
            tkMessageBox.showerror("Don't debug now",
                "You can only toggle the debugger when idle",
                parent=self.text)
            self.set_debugger_indicator()
            rudisha "break"
        else:
            db = self.interp.getdebugger()
            ikiwa db:
                self.close_debugger()
            else:
                self.open_debugger()

    eleza set_debugger_indicator(self):
        db = self.interp.getdebugger()
        self.setvar("<<toggle-debugger>>", not not db)

    eleza toggle_jit_stack_viewer(self, event=None):
        pass # All we need is the variable

    eleza close_debugger(self):
        db = self.interp.getdebugger()
        ikiwa db:
            self.interp.setdebugger(None)
            db.close()
            ikiwa self.interp.rpcclt:
                debugger_r.close_remote_debugger(self.interp.rpcclt)
            self.resetoutput()
            self.console.write("[DEBUG OFF]\n")
            self.prompt = self.sys_ps1
            self.showprompt()
        self.set_debugger_indicator()

    eleza open_debugger(self):
        ikiwa self.interp.rpcclt:
            dbg_gui = debugger_r.start_remote_debugger(self.interp.rpcclt,
                                                           self)
        else:
            dbg_gui = debugger.Debugger(self)
        self.interp.setdebugger(dbg_gui)
        dbg_gui.load_breakpoints()
        self.prompt = "[DEBUG ON]\n" + self.sys_ps1
        self.showprompt()
        self.set_debugger_indicator()

    eleza beginexecuting(self):
        "Helper for ModifiedInterpreter"
        self.resetoutput()
        self.executing = 1

    eleza endexecuting(self):
        "Helper for ModifiedInterpreter"
        self.executing = 0
        self.canceled = 0
        self.showprompt()

    eleza close(self):
        "Extend EditorWindow.close()"
        ikiwa self.executing:
            response = tkMessageBox.askokcancel(
                "Kill?",
                "Your program is still running!\n Do you want to kill it?",
                default="ok",
                parent=self.text)
            ikiwa response is False:
                rudisha "cancel"
        self.stop_readline()
        self.canceled = True
        self.closing = True
        rudisha EditorWindow.close(self)

    eleza _close(self):
        "Extend EditorWindow._close(), shut down debugger and execution server"
        self.close_debugger()
        ikiwa use_subprocess:
            self.interp.kill_subprocess()
        # Restore std streams
        sys.stdout = self.save_stdout
        sys.stderr = self.save_stderr
        sys.stdin = self.save_stdin
        # Break cycles
        self.interp = None
        self.console = None
        self.flist.pyshell = None
        self.history = None
        EditorWindow._close(self)

    eleza ispythonsource(self, filename):
        "Override EditorWindow method: never remove the colorizer"
        rudisha True

    eleza short_title(self):
        rudisha self.shell_title

    COPYRIGHT = \
          'Type "help", "copyright", "credits" or "license()" for more information.'

    eleza begin(self):
        self.text.mark_set("iomark", "insert")
        self.resetoutput()
        ikiwa use_subprocess:
            nosub = ''
            client = self.interp.start_subprocess()
            ikiwa not client:
                self.close()
                rudisha False
        else:
            nosub = ("==== No Subprocess ====\n\n" +
                    "WARNING: Running IDLE without a Subprocess is deprecated\n" +
                    "and will be removed in a later version. See Help/IDLE Help\n" +
                    "for details.\n\n")
            sys.displayhook = rpc.displayhook

        self.write("Python %s on %s\n%s\n%s" %
                   (sys.version, sys.platform, self.COPYRIGHT, nosub))
        self.text.focus_force()
        self.showprompt()
        agiza tkinter
        tkinter._default_root = None # 03Jan04 KBK What's this?
        rudisha True

    eleza stop_readline(self):
        ikiwa not self.reading:  # no nested mainloop to exit.
            return
        self._stop_readline_flag = True
        self.top.quit()

    eleza readline(self):
        save = self.reading
        try:
            self.reading = 1
            self.top.mainloop()  # nested mainloop()
        finally:
            self.reading = save
        ikiwa self._stop_readline_flag:
            self._stop_readline_flag = False
            rudisha ""
        line = self.text.get("iomark", "end-1c")
        ikiwa len(line) == 0:  # may be EOF ikiwa we quit our mainloop with Ctrl-C
            line = "\n"
        self.resetoutput()
        ikiwa self.canceled:
            self.canceled = 0
            ikiwa not use_subprocess:
                raise KeyboardInterrupt
        ikiwa self.endoffile:
            self.endoffile = 0
            line = ""
        rudisha line

    eleza isatty(self):
        rudisha True

    eleza cancel_callback(self, event=None):
        try:
            ikiwa self.text.compare("sel.first", "!=", "sel.last"):
                rudisha # Active selection -- always use default binding
        except:
            pass
        ikiwa not (self.executing or self.reading):
            self.resetoutput()
            self.interp.write("KeyboardInterrupt\n")
            self.showprompt()
            rudisha "break"
        self.endoffile = 0
        self.canceled = 1
        ikiwa (self.executing and self.interp.rpcclt):
            ikiwa self.interp.getdebugger():
                self.interp.restart_subprocess()
            else:
                self.interp.interrupt_subprocess()
        ikiwa self.reading:
            self.top.quit()  # exit the nested mainloop() in readline()
        rudisha "break"

    eleza eof_callback(self, event):
        ikiwa self.executing and not self.reading:
            rudisha # Let the default binding (delete next char) take over
        ikiwa not (self.text.compare("iomark", "==", "insert") and
                self.text.compare("insert", "==", "end-1c")):
            rudisha # Let the default binding (delete next char) take over
        ikiwa not self.executing:
            self.resetoutput()
            self.close()
        else:
            self.canceled = 0
            self.endoffile = 1
            self.top.quit()
        rudisha "break"

    eleza linefeed_callback(self, event):
        # Insert a linefeed without entering anything (still autoindented)
        ikiwa self.reading:
            self.text.insert("insert", "\n")
            self.text.see("insert")
        else:
            self.newline_and_indent_event(event)
        rudisha "break"

    eleza enter_callback(self, event):
        ikiwa self.executing and not self.reading:
            rudisha # Let the default binding (insert '\n') take over
        # If some text is selected, recall the selection
        # (but only ikiwa this before the I/O mark)
        try:
            sel = self.text.get("sel.first", "sel.last")
            ikiwa sel:
                ikiwa self.text.compare("sel.last", "<=", "iomark"):
                    self.recall(sel, event)
                    rudisha "break"
        except:
            pass
        # If we're strictly before the line containing iomark, recall
        # the current line, less a leading prompt, less leading or
        # trailing whitespace
        ikiwa self.text.compare("insert", "<", "iomark linestart"):
            # Check ikiwa there's a relevant stdin range -- ikiwa so, use it
            prev = self.text.tag_prevrange("stdin", "insert")
            ikiwa prev and self.text.compare("insert", "<", prev[1]):
                self.recall(self.text.get(prev[0], prev[1]), event)
                rudisha "break"
            next = self.text.tag_nextrange("stdin", "insert")
            ikiwa next and self.text.compare("insert lineend", ">=", next[0]):
                self.recall(self.text.get(next[0], next[1]), event)
                rudisha "break"
            # No stdin mark -- just get the current line, less any prompt
            indices = self.text.tag_nextrange("console", "insert linestart")
            ikiwa indices and \
               self.text.compare(indices[0], "<=", "insert linestart"):
                self.recall(self.text.get(indices[1], "insert lineend"), event)
            else:
                self.recall(self.text.get("insert linestart", "insert lineend"), event)
            rudisha "break"
        # If we're between the beginning of the line and the iomark, i.e.
        # in the prompt area, move to the end of the prompt
        ikiwa self.text.compare("insert", "<", "iomark"):
            self.text.mark_set("insert", "iomark")
        # If we're in the current input and there's only whitespace
        # beyond the cursor, erase that whitespace first
        s = self.text.get("insert", "end-1c")
        ikiwa s and not s.strip():
            self.text.delete("insert", "end-1c")
        # If we're in the current input before its last line,
        # insert a newline right at the insert point
        ikiwa self.text.compare("insert", "<", "end-1c linestart"):
            self.newline_and_indent_event(event)
            rudisha "break"
        # We're in the last line; append a newline and submit it
        self.text.mark_set("insert", "end-1c")
        ikiwa self.reading:
            self.text.insert("insert", "\n")
            self.text.see("insert")
        else:
            self.newline_and_indent_event(event)
        self.text.tag_add("stdin", "iomark", "end-1c")
        self.text.update_idletasks()
        ikiwa self.reading:
            self.top.quit() # Break out of recursive mainloop()
        else:
            self.runit()
        rudisha "break"

    eleza recall(self, s, event):
        # remove leading and trailing empty or whitespace lines
        s = re.sub(r'^\s*\n', '' , s)
        s = re.sub(r'\n\s*$', '', s)
        lines = s.split('\n')
        self.text.undo_block_start()
        try:
            self.text.tag_remove("sel", "1.0", "end")
            self.text.mark_set("insert", "end-1c")
            prefix = self.text.get("insert linestart", "insert")
            ikiwa prefix.rstrip().endswith(':'):
                self.newline_and_indent_event(event)
                prefix = self.text.get("insert linestart", "insert")
            self.text.insert("insert", lines[0].strip())
            ikiwa len(lines) > 1:
                orig_base_indent = re.search(r'^([ \t]*)', lines[0]).group(0)
                new_base_indent  = re.search(r'^([ \t]*)', prefix).group(0)
                for line in lines[1:]:
                    ikiwa line.startswith(orig_base_indent):
                        # replace orig base indentation with new indentation
                        line = new_base_indent + line[len(orig_base_indent):]
                    self.text.insert('insert', '\n'+line.rstrip())
        finally:
            self.text.see("insert")
            self.text.undo_block_stop()

    eleza runit(self):
        line = self.text.get("iomark", "end-1c")
        # Strip off last newline and surrounding whitespace.
        # (To allow you to hit rudisha twice to end a statement.)
        i = len(line)
        while i > 0 and line[i-1] in " \t":
            i = i-1
        ikiwa i > 0 and line[i-1] == "\n":
            i = i-1
        while i > 0 and line[i-1] in " \t":
            i = i-1
        line = line[:i]
        self.interp.runsource(line)

    eleza open_stack_viewer(self, event=None):
        ikiwa self.interp.rpcclt:
            rudisha self.interp.remote_stack_viewer()
        try:
            sys.last_traceback
        except:
            tkMessageBox.showerror("No stack trace",
                "There is no stack trace yet.\n"
                "(sys.last_traceback is not defined)",
                parent=self.text)
            return
        kutoka idlelib.stackviewer agiza StackBrowser
        StackBrowser(self.root, self.flist)

    eleza view_restart_mark(self, event=None):
        self.text.see("iomark")
        self.text.see("restart")

    eleza restart_shell(self, event=None):
        "Callback for Run/Restart Shell Cntl-F6"
        self.interp.restart_subprocess(with_cwd=True)

    eleza showprompt(self):
        self.resetoutput()
        self.console.write(self.prompt)
        self.text.mark_set("insert", "end-1c")
        self.set_line_and_column()
        self.io.reset_undo()

    eleza show_warning(self, msg):
        width = self.interp.tkconsole.width
        wrapper = TextWrapper(width=width, tabsize=8, expand_tabs=True)
        wrapped_msg = '\n'.join(wrapper.wrap(msg))
        ikiwa not wrapped_msg.endswith('\n'):
            wrapped_msg += '\n'
        self.per.bottom.insert("iomark linestart", wrapped_msg, "stderr")

    eleza resetoutput(self):
        source = self.text.get("iomark", "end-1c")
        ikiwa self.history:
            self.history.store(source)
        ikiwa self.text.get("end-2c") != "\n":
            self.text.insert("end-1c", "\n")
        self.text.mark_set("iomark", "end-1c")
        self.set_line_and_column()

    eleza write(self, s, tags=()):
        try:
            self.text.mark_gravity("iomark", "right")
            count = OutputWindow.write(self, s, tags, "iomark")
            self.text.mark_gravity("iomark", "left")
        except:
            raise ###pass  # ### 11Aug07 KBK ikiwa we are expecting exceptions
                           # let's find out what they are and be specific.
        ikiwa self.canceled:
            self.canceled = 0
            ikiwa not use_subprocess:
                raise KeyboardInterrupt
        rudisha count

    eleza rmenu_check_cut(self):
        try:
            ikiwa self.text.compare('sel.first', '<', 'iomark'):
                rudisha 'disabled'
        except TclError: # no selection, so the index 'sel.first' doesn't exist
            rudisha 'disabled'
        rudisha super().rmenu_check_cut()

    eleza rmenu_check_paste(self):
        ikiwa self.text.compare('insert','<','iomark'):
            rudisha 'disabled'
        rudisha super().rmenu_check_paste()


eleza fix_x11_paste(root):
    "Make paste replace selection on x11.  See issue #5124."
    ikiwa root._windowingsystem == 'x11':
        for cls in 'Text', 'Entry', 'Spinbox':
            root.bind_class(
                cls,
                '<<Paste>>',
                'catch {%W delete sel.first sel.last}\n' +
                        root.bind_class(cls, '<<Paste>>'))


usage_msg = """\

USAGE: idle  [-deins] [-t title] [file]*
       idle  [-dns] [-t title] (-c cmd | -r file) [arg]*
       idle  [-dns] [-t title] - [arg]*

  -h         print this help message and exit
  -n         run IDLE without a subprocess (DEPRECATED,
             see Help/IDLE Help for details)

The following options will override the IDLE 'settings' configuration:

  -e         open an edit window
  -i         open a shell window

The following options imply -i and will open a shell:

  -c cmd     run the command in a shell, or
  -r file    run script kutoka file

  -d         enable the debugger
  -s         run $IDLESTARTUP or $PYTHONSTARTUP before anything else
  -t title   set title of shell window

A default edit window will be bypassed when -c, -r, or - are used.

[arg]* are passed to the command (-c) or script (-r) in sys.argv[1:].

Examples:

idle
        Open an edit window or shell depending on IDLE's configuration.

idle foo.py foobar.py
        Edit the files, also open a shell ikiwa configured to start with shell.

idle -est "Baz" foo.py
        Run $IDLESTARTUP or $PYTHONSTARTUP, edit foo.py, and open a shell
        window with the title "Baz".

idle -c "agiza sys; andika(sys.argv)" "foo"
        Open a shell window and run the command, passing "-c" in sys.argv[0]
        and "foo" in sys.argv[1].

idle -d -s -r foo.py "Hello World"
        Open a shell window, run a startup script, enable the debugger, and
        run foo.py, passing "foo.py" in sys.argv[0] and "Hello World" in
        sys.argv[1].

echo "agiza sys; andika(sys.argv)" | idle - "foobar"
        Open a shell window, run the script piped in, passing '' in sys.argv[0]
        and "foobar" in sys.argv[1].
"""

eleza main():
    agiza getopt
    kutoka platform agiza system
    kutoka idlelib agiza testing  # bool value
    kutoka idlelib agiza macosx

    global flist, root, use_subprocess

    capture_warnings(True)
    use_subprocess = True
    enable_shell = False
    enable_edit = False
    debug = False
    cmd = None
    script = None
    startup = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:deihnr:st:")
    except getopt.error as msg:
        andika("Error: %s\n%s" % (msg, usage_msg), file=sys.stderr)
        sys.exit(2)
    for o, a in opts:
        ikiwa o == '-c':
            cmd = a
            enable_shell = True
        ikiwa o == '-d':
            debug = True
            enable_shell = True
        ikiwa o == '-e':
            enable_edit = True
        ikiwa o == '-h':
            sys.stdout.write(usage_msg)
            sys.exit()
        ikiwa o == '-i':
            enable_shell = True
        ikiwa o == '-n':
            andika(" Warning: running IDLE without a subprocess is deprecated.",
                  file=sys.stderr)
            use_subprocess = False
        ikiwa o == '-r':
            script = a
            ikiwa os.path.isfile(script):
                pass
            else:
                andika("No script file: ", script)
                sys.exit()
            enable_shell = True
        ikiwa o == '-s':
            startup = True
            enable_shell = True
        ikiwa o == '-t':
            PyShell.shell_title = a
            enable_shell = True
    ikiwa args and args[0] == '-':
        cmd = sys.stdin.read()
        enable_shell = True
    # process sys.argv and sys.path:
    for i in range(len(sys.path)):
        sys.path[i] = os.path.abspath(sys.path[i])
    ikiwa args and args[0] == '-':
        sys.argv = [''] + args[1:]
    elikiwa cmd:
        sys.argv = ['-c'] + args
    elikiwa script:
        sys.argv = [script] + args
    elikiwa args:
        enable_edit = True
        pathx = []
        for filename in args:
            pathx.append(os.path.dirname(filename))
        for dir in pathx:
            dir = os.path.abspath(dir)
            ikiwa not dir in sys.path:
                sys.path.insert(0, dir)
    else:
        dir = os.getcwd()
        ikiwa dir not in sys.path:
            sys.path.insert(0, dir)
    # check the IDLE settings configuration (but command line overrides)
    edit_start = idleConf.GetOption('main', 'General',
                                    'editor-on-startup', type='bool')
    enable_edit = enable_edit or edit_start
    enable_shell = enable_shell or not enable_edit

    # Setup root.  Don't break user code run in IDLE process.
    # Don't change environment when testing.
    ikiwa use_subprocess and not testing:
        NoDefaultRoot()
    root = Tk(className="Idle")
    root.withdraw()
    kutoka idlelib.run agiza fix_scaling
    fix_scaling(root)

    # set application icon
    icondir = os.path.join(os.path.dirname(__file__), 'Icons')
    ikiwa system() == 'Windows':
        iconfile = os.path.join(icondir, 'idle.ico')
        root.wm_iconbitmap(default=iconfile)
    elikiwa not macosx.isAquaTk():
        ext = '.png' ikiwa TkVersion >= 8.6 else '.gif'
        iconfiles = [os.path.join(icondir, 'idle_%d%s' % (size, ext))
                     for size in (16, 32, 48)]
        icons = [PhotoImage(master=root, file=iconfile)
                 for iconfile in iconfiles]
        root.wm_iconphoto(True, *icons)

    # start editor and/or shell windows:
    fixwordbreaks(root)
    fix_x11_paste(root)
    flist = PyShellFileList(root)
    macosx.setupApp(root, flist)

    ikiwa enable_edit:
        ikiwa not (cmd or script):
            for filename in args[:]:
                ikiwa flist.open(filename) is None:
                    # filename is a directory actually, disconsider it
                    args.remove(filename)
            ikiwa not args:
                flist.new()

    ikiwa enable_shell:
        shell = flist.open_shell()
        ikiwa not shell:
            rudisha # couldn't open shell
        ikiwa macosx.isAquaTk() and flist.dict:
            # On OSX: when the user has double-clicked on a file that causes
            # IDLE to be launched the shell window will open just in front of
            # the file she wants to see. Lower the interpreter window when
            # there are open files.
            shell.top.lower()
    else:
        shell = flist.pyshell

    # Handle remaining options. If any of these are set, enable_shell
    # was set also, so shell must be true to reach here.
    ikiwa debug:
        shell.open_debugger()
    ikiwa startup:
        filename = os.environ.get("IDLESTARTUP") or \
                   os.environ.get("PYTHONSTARTUP")
        ikiwa filename and os.path.isfile(filename):
            shell.interp.execfile(filename)
    ikiwa cmd or script:
        shell.interp.runcommand("""ikiwa 1:
            agiza sys as _sys
            _sys.argv = %r
            del _sys
            \n""" % (sys.argv,))
        ikiwa cmd:
            shell.interp.execsource(cmd)
        elikiwa script:
            shell.interp.prepend_syspath(script)
            shell.interp.execfile(script)
    elikiwa shell:
        # If there is a shell window and no cmd or script in progress,
        # check for problematic issues and print warning message(s) in
        # the IDLE shell window; this is less intrusive than always
        # opening a separate window.

        # Warn ikiwa using a problematic OS X Tk version.
        tkversionwarning = macosx.tkVersionWarning(root)
        ikiwa tkversionwarning:
            shell.show_warning(tkversionwarning)

        # Warn ikiwa the "Prefer tabs when opening documents" system
        # preference is set to "Always".
        prefer_tabs_preference_warning = macosx.preferTabsPreferenceWarning()
        ikiwa prefer_tabs_preference_warning:
            shell.show_warning(prefer_tabs_preference_warning)

    while flist.inversedict:  # keep IDLE running while files are open.
        root.mainloop()
    root.destroy()
    capture_warnings(False)

ikiwa __name__ == "__main__":
    main()

capture_warnings(False)  # Make sure turned off; see issue 18081
