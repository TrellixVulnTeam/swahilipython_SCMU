#! /usr/bin/env python3

agiza sys
ikiwa __name__ == "__main__":
    sys.modules['idlelib.pyshell'] = sys.modules['__main__']

jaribu:
    kutoka tkinter agiza *
tatizo ImportError:
    andika("** IDLE can't agiza Tkinter.\n"
          "Your Python may sio be configured kila Tk. **", file=sys.__stderr__)
    ashiria SystemExit(1)

# Valid arguments kila the ...Awareness call below are defined kwenye the following.
# https://msdn.microsoft.com/en-us/library/windows/desktop/dn280512(v=vs.85).aspx
ikiwa sys.platform == 'win32':
    jaribu:
        agiza ctypes
        PROCESS_SYSTEM_DPI_AWARE = 1
        ctypes.OleDLL('shcore').SetProcessDpiAwareness(PROCESS_SYSTEM_DPI_AWARE)
    tatizo (ImportError, AttributeError, OSError):
        pita

agiza tkinter.messagebox kama tkMessageBox
ikiwa TkVersion < 8.5:
    root = Tk()  # otherwise create root kwenye main
    root.withdraw()
    kutoka idlelib.run agiza fix_scaling
    fix_scaling(root)
    tkMessageBox.showerror("Idle Cannot Start",
            "Idle requires tcl/tk 8.5+, sio %s." % TkVersion,
            parent=root)
    ashiria SystemExit(1)

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
kutoka idlelib.editor agiza EditorWindow, fixwordkomas
kutoka idlelib.filelist agiza FileList
kutoka idlelib.outwin agiza OutputWindow
kutoka idlelib agiza rpc
kutoka idlelib.run agiza idle_formatwarning, StdInputFile, StdOutputFile
kutoka idlelib.undo agiza UndoDelegator

HOST = '127.0.0.1' # python execution server on localhost loopback
PORT = 0  # someday pita kwenye host, port kila remote debug capability

# Override warnings module to write to warning_stream.  Initialize to send IDLE
# internal warnings to the console.  ScriptBinding.check_syntax() will
# temporarily redirect the stream to the shell window to display warnings when
# checking user's code.
warning_stream = sys.__stderr__  # Tupu, at least on Windows, ikiwa no console.

eleza idle_showwarning(
        message, category, filename, lineno, file=Tupu, line=Tupu):
    """Show Idle-format warning (after replacing warnings.showwarning).

    The differences are the formatter called, the file=Tupu replacement,
    which can be Tupu, the capture of the consequence AttributeError,
    na the output of a hard-coded prompt.
    """
    ikiwa file ni Tupu:
        file = warning_stream
    jaribu:
        file.write(idle_formatwarning(
                message, category, filename, lineno, line=line))
        file.write(">>> ")
    tatizo (AttributeError, OSError):
        pita  # ikiwa file (probably __stderr__) ni invalid, skip warning.

_warnings_showwarning = Tupu

eleza capture_warnings(capture):
    "Replace warning.showwarning ukijumuisha idle_showwarning, ama reverse."

    global _warnings_showwarning
    ikiwa capture:
        ikiwa _warnings_showwarning ni Tupu:
            _warnings_showwarning = warnings.showwarning
            warnings.showwarning = idle_showwarning
    isipokua:
        ikiwa _warnings_showwarning ni sio Tupu:
            warnings.showwarning = _warnings_showwarning
            _warnings_showwarning = Tupu

capture_warnings(Kweli)

eleza extended_linecache_checkcache(filename=Tupu,
                                  orig_checkcache=linecache.checkcache):
    """Extend linecache.checkcache to preserve the <pyshell#...> entries

    Rather than repeating the linecache code, patch it to save the
    <pyshell#...> entries, call the original linecache.checkcache()
    (skipping them), na then restore the saved entries.

    orig_checkcache ni bound at definition time to the original
    method, allowing it to be patched.
    """
    cache = linecache.cache
    save = {}
    kila key kwenye list(cache):
        ikiwa key[:1] + key[-1:] == '<>':
            save[key] = cache.pop(key)
    orig_checkcache(filename)
    cache.update(save)

# Patch linecache.checkcache():
linecache.checkcache = extended_linecache_checkcache


kundi PyShellEditorWindow(EditorWindow):
    "Regular text edit window kwenye IDLE, supports komapoints"

    eleza __init__(self, *args):
        self.komapoints = []
        EditorWindow.__init__(self, *args)
        self.text.bind("<<set-komapoint-here>>", self.set_komapoint_here)
        self.text.bind("<<clear-komapoint-here>>", self.clear_komapoint_here)
        self.text.bind("<<open-python-shell>>", self.flist.open_shell)

        #TODO: don't read/write this from/to .idlerc when testing
        self.komapointPath = os.path.join(
                idleConf.userdir, 'komapoints.lst')
        # whenever a file ni changed, restore komapoints
        eleza filename_changed_hook(old_hook=self.io.filename_change_hook,
                                  self=self):
            self.restore_file_komas()
            old_hook()
        self.io.set_filename_change_hook(filename_changed_hook)
        ikiwa self.io.filename:
            self.restore_file_komas()
        self.color_komapoint_text()

    rmenu_specs = [
        ("Cut", "<<cut>>", "rmenu_check_cut"),
        ("Copy", "<<copy>>", "rmenu_check_copy"),
        ("Paste", "<<paste>>", "rmenu_check_paste"),
        (Tupu, Tupu, Tupu),
        ("Set Breakpoint", "<<set-komapoint-here>>", Tupu),
        ("Clear Breakpoint", "<<clear-komapoint-here>>", Tupu)
    ]

    eleza color_komapoint_text(self, color=Kweli):
        "Turn colorizing of komapoint text on ama off"
        ikiwa self.io ni Tupu:
            # possible due to update kwenye restore_file_komas
            rudisha
        ikiwa color:
            theme = idleConf.CurrentTheme()
            cfg = idleConf.GetHighlight(theme, "koma")
        isipokua:
            cfg = {'foreground': '', 'background': ''}
        self.text.tag_config('BREAK', cfg)

    eleza set_komapoint(self, lineno):
        text = self.text
        filename = self.io.filename
        text.tag_add("BREAK", "%d.0" % lineno, "%d.0" % (lineno+1))
        jaribu:
            self.komapoints.index(lineno)
        tatizo ValueError:  # only add ikiwa missing, i.e. do once
            self.komapoints.append(lineno)
        jaribu:    # update the subprocess debugger
            debug = self.flist.pyshell.interp.debugger
            debug.set_komapoint_here(filename, lineno)
        tatizo: # but debugger may sio be active right now....
            pita

    eleza set_komapoint_here(self, event=Tupu):
        text = self.text
        filename = self.io.filename
        ikiwa sio filename:
            text.bell()
            rudisha
        lineno = int(float(text.index("insert")))
        self.set_komapoint(lineno)

    eleza clear_komapoint_here(self, event=Tupu):
        text = self.text
        filename = self.io.filename
        ikiwa sio filename:
            text.bell()
            rudisha
        lineno = int(float(text.index("insert")))
        jaribu:
            self.komapoints.remove(lineno)
        tatizo:
            pita
        text.tag_remove("BREAK", "insert linestart",\
                        "insert lineend +1char")
        jaribu:
            debug = self.flist.pyshell.interp.debugger
            debug.clear_komapoint_here(filename, lineno)
        tatizo:
            pita

    eleza clear_file_komas(self):
        ikiwa self.komapoints:
            text = self.text
            filename = self.io.filename
            ikiwa sio filename:
                text.bell()
                rudisha
            self.komapoints = []
            text.tag_remove("BREAK", "1.0", END)
            jaribu:
                debug = self.flist.pyshell.interp.debugger
                debug.clear_file_komas(filename)
            tatizo:
                pita

    eleza store_file_komas(self):
        "Save komapoints when file ni saved"
        # XXX 13 Dec 2002 KBK Currently the file must be saved before it can
        #     be run.  The komas are saved at that time.  If we introduce
        #     a temporary file save feature the save komas functionality
        #     needs to be re-verified, since the komas at the time the
        #     temp file ni created may differ kutoka the komas at the last
        #     permanent save of the file.  Currently, a koma introduced
        #     after a save will be effective, but sio persistent.
        #     This ni necessary to keep the saved komas synched ukijumuisha the
        #     saved file.
        #
        #     Breakpoints are set kama tagged ranges kwenye the text.
        #     Since a modified file has to be saved before it is
        #     run, na since self.komapoints (kutoka which the subprocess
        #     debugger ni loaded) ni updated during the save, the visible
        #     komas stay synched ukijumuisha the subprocess even ikiwa one of these
        #     unexpected komapoint deletions occurs.
        komas = self.komapoints
        filename = self.io.filename
        jaribu:
            ukijumuisha open(self.komapointPath, "r") kama fp:
                lines = fp.readlines()
        tatizo OSError:
            lines = []
        jaribu:
            ukijumuisha open(self.komapointPath, "w") kama new_file:
                kila line kwenye lines:
                    ikiwa sio line.startswith(filename + '='):
                        new_file.write(line)
                self.update_komapoints()
                komas = self.komapoints
                ikiwa komas:
                    new_file.write(filename + '=' + str(komas) + '\n')
        tatizo OSError kama err:
            ikiwa sio getattr(self.root, "komapoint_error_displayed", Uongo):
                self.root.komapoint_error_displayed = Kweli
                tkMessageBox.showerror(title='IDLE Error',
                    message='Unable to update komapoint list:\n%s'
                        % str(err),
                    parent=self.text)

    eleza restore_file_komas(self):
        self.text.update()   # this enables setting "BREAK" tags to be visible
        ikiwa self.io ni Tupu:
            # can happen ikiwa IDLE closes due to the .update() call
            rudisha
        filename = self.io.filename
        ikiwa filename ni Tupu:
            rudisha
        ikiwa os.path.isfile(self.komapointPath):
            ukijumuisha open(self.komapointPath, "r") kama fp:
                lines = fp.readlines()
            kila line kwenye lines:
                ikiwa line.startswith(filename + '='):
                    komapoint_linenumbers = eval(line[len(filename)+1:])
                    kila komapoint_linenumber kwenye komapoint_linenumbers:
                        self.set_komapoint(komapoint_linenumber)

    eleza update_komapoints(self):
        "Retrieves all the komapoints kwenye the current window"
        text = self.text
        ranges = text.tag_ranges("BREAK")
        linenumber_list = self.ranges_to_linenumbers(ranges)
        self.komapoints = linenumber_list

    eleza ranges_to_linenumbers(self, ranges):
        lines = []
        kila index kwenye range(0, len(ranges), 2):
            lineno = int(float(ranges[index].string))
            end = int(float(ranges[index+1].string))
            wakati lineno < end:
                lines.append(lineno)
                lineno += 1
        rudisha lines

# XXX 13 Dec 2002 KBK Not used currently
#    eleza saved_change_hook(self):
#        "Extend base method - clear komas ikiwa module ni modified"
#        ikiwa sio self.get_saved():
#            self.clear_file_komas()
#        EditorWindow.saved_change_hook(self)

    eleza _close(self):
        "Extend base method - clear komas when module ni closed"
        self.clear_file_komas()
        EditorWindow._close(self)


kundi PyShellFileList(FileList):
    "Extend base class: IDLE supports a shell na komapoints"

    # override FileList's kundi variable, instances rudisha PyShellEditorWindow
    # instead of EditorWindow when new edit windows are created.
    EditorWindow = PyShellEditorWindow

    pyshell = Tupu

    eleza open_shell(self, event=Tupu):
        ikiwa self.pyshell:
            self.pyshell.top.wakeup()
        isipokua:
            self.pyshell = PyShell(self)
            ikiwa self.pyshell:
                ikiwa sio self.pyshell.begin():
                    rudisha Tupu
        rudisha self.pyshell


kundi ModifiedColorDelegator(ColorDelegator):
    "Extend base class: colorizer kila the shell window itself"

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
            "stdin": {'background':Tupu,'foreground':Tupu},
            "stdout": idleConf.GetHighlight(theme, "stdout"),
            "stderr": idleConf.GetHighlight(theme, "stderr"),
            "console": idleConf.GetHighlight(theme, "console"),
        })

    eleza removecolors(self):
        # Don't remove shell color tags before "iomark"
        kila tag kwenye self.tagdefs:
            self.tag_remove(tag, "iomark", "end")

kundi ModifiedUndoDelegator(UndoDelegator):
    "Extend base class: forbid insert/delete before the I/O mark"

    eleza insert(self, index, chars, tags=Tupu):
        jaribu:
            ikiwa self.delegate.compare(index, "<", "iomark"):
                self.delegate.bell()
                rudisha
        tatizo TclError:
            pita
        UndoDelegator.insert(self, index, chars, tags)

    eleza delete(self, index1, index2=Tupu):
        jaribu:
            ikiwa self.delegate.compare(index1, "<", "iomark"):
                self.delegate.bell()
                rudisha
        tatizo TclError:
            pita
        UndoDelegator.delete(self, index1, index2)


kundi MyRPCClient(rpc.RPCClient):

    eleza handle_EOF(self):
        "Override the base kundi - just re-ashiria EOFError"
        ashiria EOFError

eleza restart_line(width, filename):  # See bpo-38141.
    """Return width long restart line formatted ukijumuisha filename.

    Fill line ukijumuisha balanced '='s, ukijumuisha any extras na at least one at
    the beginning.  Do sio end ukijumuisha a trailing space.
    """
    tag = f"= RESTART: {filename ama 'Shell'} ="
    ikiwa width >= len(tag):
        div, mod = divmod((width -len(tag)), 2)
        rudisha f"{(div+mod)*'='}{tag}{div*'='}"
    isipokua:
        rudisha tag[:-2]  # Remove ' ='.


kundi ModifiedInterpreter(InteractiveInterpreter):

    eleza __init__(self, tkconsole):
        self.tkconsole = tkconsole
        locals = sys.modules['__main__'].__dict__
        InteractiveInterpreter.__init__(self, locals=locals)
        self.restarting = Uongo
        self.subprocess_arglist = Tupu
        self.port = PORT
        self.original_compiler_flags = self.compile.compiler.flags

    _afterid = Tupu
    rpcclt = Tupu
    rpcsubproc = Tupu

    eleza spawn_subprocess(self):
        ikiwa self.subprocess_arglist ni Tupu:
            self.subprocess_arglist = self.build_subprocess_arglist()
        self.rpcsubproc = subprocess.Popen(self.subprocess_arglist)

    eleza build_subprocess_arglist(self):
        assert (self.port!=0), (
            "Socket should have been assigned a port number.")
        w = ['-W' + s kila s kwenye sys.warnoptions]
        # Maybe IDLE ni installed na ni being accessed via sys.path,
        # ama maybe it's sio intalled na the idle.py script ni being
        # run kutoka the IDLE source directory.
        del_exitf = idleConf.GetOption('main', 'General', 'delete-exitfunc',
                                       default=Uongo, type='bool')
        command = "__import__('idlelib.run').run.main(%r)" % (del_exitf,)
        rudisha [sys.executable] + w + ["-c", command, str(self.port)]

    eleza start_subprocess(self):
        addr = (HOST, self.port)
        # GUI makes several attempts to acquire socket, listens kila connection
        kila i kwenye range(3):
            time.sleep(i)
            jaribu:
                self.rpcclt = MyRPCClient(addr)
                koma
            tatizo OSError:
                pita
        isipokua:
            self.display_port_binding_error()
            rudisha Tupu
        # ikiwa PORT was 0, system will assign an 'ephemeral' port. Find it out:
        self.port = self.rpcclt.listening_sock.getsockname()[1]
        # ikiwa PORT was sio 0, probably working ukijumuisha a remote execution server
        ikiwa PORT != 0:
            # To allow reconnection within the 2MSL wait (cf. Stevens TCP
            # V1, 18.6),  set SO_REUSEADDR.  Note that this can be problematic
            # on Windows since the implementation allows two active sockets on
            # the same address!
            self.rpcclt.listening_sock.setsockopt(socket.SOL_SOCKET,
                                           socket.SO_REUSEADDR, 1)
        self.spawn_subprocess()
        #time.sleep(20) # test to simulate GUI sio accepting connection
        # Accept the connection kutoka the Python execution server
        self.rpcclt.listening_sock.settimeout(10)
        jaribu:
            self.rpcclt.accept()
        tatizo socket.timeout:
            self.display_no_subprocess_error()
            rudisha Tupu
        self.rpcclt.register("console", self.tkconsole)
        self.rpcclt.register("stdin", self.tkconsole.stdin)
        self.rpcclt.register("stdout", self.tkconsole.stdout)
        self.rpcclt.register("stderr", self.tkconsole.stderr)
        self.rpcclt.register("flist", self.tkconsole.flist)
        self.rpcclt.register("linecache", linecache)
        self.rpcclt.register("interp", self)
        self.transfer_path(with_cwd=Kweli)
        self.poll_subprocess()
        rudisha self.rpcclt

    eleza restart_subprocess(self, with_cwd=Uongo, filename=''):
        ikiwa self.restarting:
            rudisha self.rpcclt
        self.restarting = Kweli
        # close only the subprocess debugger
        debug = self.getdebugger()
        ikiwa debug:
            jaribu:
                # Only close subprocess debugger, don't unregister gui_adap!
                debugger_r.close_subprocess_debugger(self.rpcclt)
            tatizo:
                pita
        # Kill subprocess, spawn a new one, accept connection.
        self.rpcclt.close()
        self.terminate_subprocess()
        console = self.tkconsole
        was_executing = console.executing
        console.executing = Uongo
        self.spawn_subprocess()
        jaribu:
            self.rpcclt.accept()
        tatizo socket.timeout:
            self.display_no_subprocess_error()
            rudisha Tupu
        self.transfer_path(with_cwd=with_cwd)
        console.stop_readline()
        # annotate restart kwenye shell window na mark it
        console.text.delete("iomark", "end-1c")
        console.write('\n')
        console.write(restart_line(console.width, filename))
        console.text.mark_set("restart", "end-1c")
        console.text.mark_gravity("restart", "left")
        ikiwa sio filename:
            console.showprompt()
        # restart subprocess debugger
        ikiwa debug:
            # Restarted debugger connects to current instance of debug GUI
            debugger_r.restart_subprocess_debugger(self.rpcclt)
            # reload remote debugger komapoints kila all PyShellEditWindows
            debug.load_komapoints()
        self.compile.compiler.flags = self.original_compiler_flags
        self.restarting = Uongo
        rudisha self.rpcclt

    eleza __request_interrupt(self):
        self.rpcclt.remotecall("exec", "interrupt_the_server", (), {})

    eleza interrupt_subprocess(self):
        threading.Thread(target=self.__request_interrupt).start()

    eleza kill_subprocess(self):
        ikiwa self._afterid ni sio Tupu:
            self.tkconsole.text.after_cancel(self._afterid)
        jaribu:
            self.rpcclt.listening_sock.close()
        tatizo AttributeError:  # no socket
            pita
        jaribu:
            self.rpcclt.close()
        tatizo AttributeError:  # no socket
            pita
        self.terminate_subprocess()
        self.tkconsole.executing = Uongo
        self.rpcclt = Tupu

    eleza terminate_subprocess(self):
        "Make sure subprocess ni terminated"
        jaribu:
            self.rpcsubproc.kill()
        tatizo OSError:
            # process already terminated
            rudisha
        isipokua:
            jaribu:
                self.rpcsubproc.wait()
            tatizo OSError:
                rudisha

    eleza transfer_path(self, with_cwd=Uongo):
        ikiwa with_cwd:        # Issue 13506
            path = ['']     # include Current Working Directory
            path.extend(sys.path)
        isipokua:
            path = sys.path

        self.runcommand("""ikiwa 1:
        agiza sys kama _sys
        _sys.path = %r
        toa _sys
        \n""" % (path,))

    active_seq = Tupu

    eleza poll_subprocess(self):
        clt = self.rpcclt
        ikiwa clt ni Tupu:
            rudisha
        jaribu:
            response = clt.pollresponse(self.active_seq, wait=0.05)
        tatizo (EOFError, OSError, KeyboardInterrupt):
            # lost connection ama subprocess terminated itself, restart
            # [the KBI ni kutoka rpc.SocketIO.handle_EOF()]
            ikiwa self.tkconsole.closing:
                rudisha
            response = Tupu
            self.restart_subprocess()
        ikiwa response:
            self.tkconsole.resetoutput()
            self.active_seq = Tupu
            how, what = response
            console = self.tkconsole.console
            ikiwa how == "OK":
                ikiwa what ni sio Tupu:
                    andika(repr(what), file=console)
            lasivyo how == "EXCEPTION":
                ikiwa self.tkconsole.getvar("<<toggle-jit-stack-viewer>>"):
                    self.remote_stack_viewer()
            lasivyo how == "ERROR":
                errmsg = "pyshell.ModifiedInterpreter: Subprocess ERROR:\n"
                andika(errmsg, what, file=sys.__stderr__)
                andika(errmsg, what, file=console)
            # we received a response to the currently active seq number:
            jaribu:
                self.tkconsole.endexecuting()
            tatizo AttributeError:  # shell may have closed
                pita
        # Reschedule myself
        ikiwa sio self.tkconsole.closing:
            self._afterid = self.tkconsole.text.after(
                self.tkconsole.pollinterval, self.poll_subprocess)

    debugger = Tupu

    eleza setdebugger(self, debugger):
        self.debugger = debugger

    eleza getdebugger(self):
        rudisha self.debugger

    eleza open_remote_stack_viewer(self):
        """Initiate the remote stack viewer kutoka a separate thread.

        This method ni called kutoka the subprocess, na by returning kutoka this
        method we allow the subprocess to unblock.  After a bit the shell
        requests the subprocess to open the remote stack viewer which returns a
        static object looking at the last exception.  It ni queried through
        the RPC mechanism.

        """
        self.tkconsole.text.after(300, self.remote_stack_viewer)
        rudisha

    eleza remote_stack_viewer(self):
        kutoka idlelib agiza debugobj_r
        oid = self.rpcclt.remotequeue("exec", "stackviewer", ("flist",), {})
        ikiwa oid ni Tupu:
            self.tkconsole.root.bell()
            rudisha
        item = debugobj_r.StubObjectTreeItem(self.rpcclt, oid)
        kutoka idlelib.tree agiza ScrolledCanvas, TreeNode
        top = Toplevel(self.tkconsole.root)
        theme = idleConf.CurrentTheme()
        background = idleConf.GetHighlight(theme, 'normal')['background']
        sc = ScrolledCanvas(top, bg=background, highlightthickness=0)
        sc.frame.pack(expand=1, fill="both")
        node = TreeNode(sc.canvas, Tupu, item)
        node.expand()
        # XXX Should GC the remote tree when closing the window

    gid = 0

    eleza execsource(self, source):
        "Like runsource() but assumes complete exec source"
        filename = self.stuffsource(source)
        self.execfile(filename, source)

    eleza execfile(self, filename, source=Tupu):
        "Execute an existing file"
        ikiwa source ni Tupu:
            ukijumuisha tokenize.open(filename) kama fp:
                source = fp.read()
                ikiwa use_subprocess:
                    source = (f"__file__ = r'''{os.path.abspath(filename)}'''\n"
                              + source + "\ntoa __file__")
        jaribu:
            code = compile(source, filename, "exec")
        tatizo (OverflowError, SyntaxError):
            self.tkconsole.resetoutput()
            andika('*** Error kwenye script ama command!\n'
                 'Traceback (most recent call last):',
                  file=self.tkconsole.stderr)
            InteractiveInterpreter.showsyntaxerror(self, filename)
            self.tkconsole.showprompt()
        isipokua:
            self.runcode(code)

    eleza runsource(self, source):
        "Extend base kundi method: Stuff the source kwenye the line cache first"
        filename = self.stuffsource(source)
        self.more = 0
        # at the moment, InteractiveInterpreter expects str
        assert isinstance(source, str)
        # InteractiveInterpreter.runsource() calls its runcode() method,
        # which ni overridden (see below)
        rudisha InteractiveInterpreter.runsource(self, source, filename)

    eleza stuffsource(self, source):
        "Stuff source kwenye the filename cache"
        filename = "<pyshell#%d>" % self.gid
        self.gid = self.gid + 1
        lines = source.split("\n")
        linecache.cache[filename] = len(source)+1, 0, lines, filename
        rudisha filename

    eleza prepend_syspath(self, filename):
        "Prepend sys.path ukijumuisha file's directory ikiwa sio already included"
        self.runcommand("""ikiwa 1:
            _filename = %r
            agiza sys kama _sys
            kutoka os.path agiza dirname kama _dirname
            _dir = _dirname(_filename)
            ikiwa sio _dir kwenye _sys.path:
                _sys.path.insert(0, _dir)
            toa _filename, _sys, _dirname, _dir
            \n""" % (filename,))

    eleza showsyntaxerror(self, filename=Tupu):
        """Override Interactive Interpreter method: Use Colorizing

        Color the offending position instead of printing it na pointing at it
        ukijumuisha a caret.

        """
        tkconsole = self.tkconsole
        text = tkconsole.text
        text.tag_remove("ERROR", "1.0", "end")
        type, value, tb = sys.exc_info()
        msg = getattr(value, 'msg', '') ama value ama "<no detail available>"
        lineno = getattr(value, 'lineno', '') ama 1
        offset = getattr(value, 'offset', '') ama 0
        ikiwa offset == 0:
            lineno += 1 #mark end of offending line
        ikiwa lineno == 1:
            pos = "iomark + %d chars" % (offset-1)
        isipokua:
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
        kila key kwenye list(c.keys()):
            ikiwa key[:1] + key[-1:] != "<>":
                toa c[key]

    eleza runcommand(self, code):
        "Run the code without invoking the debugger"
        # The code better sio ashiria an exception!
        ikiwa self.tkconsole.executing:
            self.display_executing_dialog()
            rudisha 0
        ikiwa self.rpcclt:
            self.rpcclt.remotequeue("exec", "runcode", (code,), {})
        isipokua:
            exec(code, self.locals)
        rudisha 1

    eleza runcode(self, code):
        "Override base kundi method"
        ikiwa self.tkconsole.executing:
            self.interp.restart_subprocess()
        self.checklinecache()
        debugger = self.debugger
        jaribu:
            self.tkconsole.beginexecuting()
            ikiwa sio debugger na self.rpcclt ni sio Tupu:
                self.active_seq = self.rpcclt.asyncqueue("exec", "runcode",
                                                        (code,), {})
            lasivyo debugger:
                debugger.run(code, self.locals)
            isipokua:
                exec(code, self.locals)
        tatizo SystemExit:
            ikiwa sio self.tkconsole.closing:
                ikiwa tkMessageBox.askyesno(
                    "Exit?",
                    "Do you want to exit altogether?",
                    default="yes",
                    parent=self.tkconsole.text):
                    raise
                isipokua:
                    self.showtraceback()
            isipokua:
                raise
        tatizo:
            ikiwa use_subprocess:
                andika("IDLE internal error kwenye runcode()",
                      file=self.tkconsole.stderr)
                self.showtraceback()
                self.tkconsole.endexecuting()
            isipokua:
                ikiwa self.tkconsole.canceled:
                    self.tkconsole.canceled = Uongo
                    andika("KeyboardInterrupt", file=self.tkconsole.stderr)
                isipokua:
                    self.showtraceback()
        mwishowe:
            ikiwa sio use_subprocess:
                jaribu:
                    self.tkconsole.endexecuting()
                tatizo AttributeError:  # shell may have closed
                    pita

    eleza write(self, s):
        "Override base kundi method"
        rudisha self.tkconsole.stderr.write(s)

    eleza display_port_binding_error(self):
        tkMessageBox.showerror(
            "Port Binding Error",
            "IDLE can't bind to a TCP/IP port, which ni necessary to "
            "communicate ukijumuisha its Python execution server.  This might be "
            "because no networking ni installed on this computer.  "
            "Run IDLE ukijumuisha the -n command line switch to start without a "
            "subprocess na refer to Help/IDLE Help 'Running without a "
            "subprocess' kila further details.",
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
            "The Python Shell window ni already executing a command; "
            "please wait until it ni finished.",
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

    allow_line_numbers = Uongo

    # New classes
    kutoka idlelib.history agiza History

    eleza __init__(self, flist=Tupu):
        ikiwa use_subprocess:
            ms = self.menu_specs
            ikiwa ms[2][0] != "shell":
                ms.insert(2, ("shell", "She_ll"))
        self.interp = ModifiedInterpreter(self)
        ikiwa flist ni Tupu:
            root = Tk()
            fixwordkomas(root)
            root.withdraw()
            flist = PyShellFileList(root)

        OutputWindow.__init__(self, flist, Tupu, Tupu)

        self.usetabs = Kweli
        # indentwidth must be 8 when using tabs.  See note kwenye EditorWindow:
        self.indentwidth = 8

        self.sys_ps1 = sys.ps1 ikiwa hasattr(sys, 'ps1') isipokua '>>> '
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
        ikiwa sio use_subprocess:
            sys.stdout = self.stdout
            sys.stderr = self.stderr
            sys.stdin = self.stdin
        jaribu:
            # page help() text to shell.
            agiza pydoc # agiza must be done here to capture i/o rebinding.
            # XXX KBK 27Dec07 use text viewer someday, but must work w/o subproc
            pydoc.pager = pydoc.plainpager
        tatizo:
            sys.stderr = sys.__stderr__
            raise
        #
        self.history = self.History(self.text)
        #
        self.pollinterval = 50  # millisec

    eleza get_standard_extension_names(self):
        rudisha idleConf.GetExtensions(shell_only=Kweli)

    reading = Uongo
    executing = Uongo
    canceled = Uongo
    endoffile = Uongo
    closing = Uongo
    _stop_readline_flag = Uongo

    eleza set_warning_stream(self, stream):
        global warning_stream
        warning_stream = stream

    eleza get_warning_stream(self):
        rudisha warning_stream

    eleza toggle_debugger(self, event=Tupu):
        ikiwa self.executing:
            tkMessageBox.showerror("Don't debug now",
                "You can only toggle the debugger when idle",
                parent=self.text)
            self.set_debugger_indicator()
            rudisha "koma"
        isipokua:
            db = self.interp.getdebugger()
            ikiwa db:
                self.close_debugger()
            isipokua:
                self.open_debugger()

    eleza set_debugger_indicator(self):
        db = self.interp.getdebugger()
        self.setvar("<<toggle-debugger>>", sio sio db)

    eleza toggle_jit_stack_viewer(self, event=Tupu):
        pita # All we need ni the variable

    eleza close_debugger(self):
        db = self.interp.getdebugger()
        ikiwa db:
            self.interp.setdebugger(Tupu)
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
        isipokua:
            dbg_gui = debugger.Debugger(self)
        self.interp.setdebugger(dbg_gui)
        dbg_gui.load_komapoints()
        self.prompt = "[DEBUG ON]\n" + self.sys_ps1
        self.showprompt()
        self.set_debugger_indicator()

    eleza beginexecuting(self):
        "Helper kila ModifiedInterpreter"
        self.resetoutput()
        self.executing = 1

    eleza endexecuting(self):
        "Helper kila ModifiedInterpreter"
        self.executing = 0
        self.canceled = 0
        self.showprompt()

    eleza close(self):
        "Extend EditorWindow.close()"
        ikiwa self.executing:
            response = tkMessageBox.askokcancel(
                "Kill?",
                "Your program ni still running!\n Do you want to kill it?",
                default="ok",
                parent=self.text)
            ikiwa response ni Uongo:
                rudisha "cancel"
        self.stop_readline()
        self.canceled = Kweli
        self.closing = Kweli
        rudisha EditorWindow.close(self)

    eleza _close(self):
        "Extend EditorWindow._close(), shut down debugger na execution server"
        self.close_debugger()
        ikiwa use_subprocess:
            self.interp.kill_subprocess()
        # Restore std streams
        sys.stdout = self.save_stdout
        sys.stderr = self.save_stderr
        sys.stdin = self.save_stdin
        # Break cycles
        self.interp = Tupu
        self.console = Tupu
        self.flist.pyshell = Tupu
        self.history = Tupu
        EditorWindow._close(self)

    eleza ispythonsource(self, filename):
        "Override EditorWindow method: never remove the colorizer"
        rudisha Kweli

    eleza short_title(self):
        rudisha self.shell_title

    COPYRIGHT = \
          'Type "help", "copyright", "credits" ama "license()" kila more information.'

    eleza begin(self):
        self.text.mark_set("iomark", "insert")
        self.resetoutput()
        ikiwa use_subprocess:
            nosub = ''
            client = self.interp.start_subprocess()
            ikiwa sio client:
                self.close()
                rudisha Uongo
        isipokua:
            nosub = ("==== No Subprocess ====\n\n" +
                    "WARNING: Running IDLE without a Subprocess ni deprecated\n" +
                    "and will be removed kwenye a later version. See Help/IDLE Help\n" +
                    "kila details.\n\n")
            sys.displayhook = rpc.displayhook

        self.write("Python %s on %s\n%s\n%s" %
                   (sys.version, sys.platform, self.COPYRIGHT, nosub))
        self.text.focus_force()
        self.showprompt()
        agiza tkinter
        tkinter._default_root = Tupu # 03Jan04 KBK What's this?
        rudisha Kweli

    eleza stop_readline(self):
        ikiwa sio self.reading:  # no nested mainloop to exit.
            rudisha
        self._stop_readline_flag = Kweli
        self.top.quit()

    eleza readline(self):
        save = self.reading
        jaribu:
            self.reading = 1
            self.top.mainloop()  # nested mainloop()
        mwishowe:
            self.reading = save
        ikiwa self._stop_readline_flag:
            self._stop_readline_flag = Uongo
            rudisha ""
        line = self.text.get("iomark", "end-1c")
        ikiwa len(line) == 0:  # may be EOF ikiwa we quit our mainloop ukijumuisha Ctrl-C
            line = "\n"
        self.resetoutput()
        ikiwa self.canceled:
            self.canceled = 0
            ikiwa sio use_subprocess:
                ashiria KeyboardInterrupt
        ikiwa self.endoffile:
            self.endoffile = 0
            line = ""
        rudisha line

    eleza isatty(self):
        rudisha Kweli

    eleza cancel_callback(self, event=Tupu):
        jaribu:
            ikiwa self.text.compare("sel.first", "!=", "sel.last"):
                rudisha # Active selection -- always use default binding
        tatizo:
            pita
        ikiwa sio (self.executing ama self.reading):
            self.resetoutput()
            self.interp.write("KeyboardInterrupt\n")
            self.showprompt()
            rudisha "koma"
        self.endoffile = 0
        self.canceled = 1
        ikiwa (self.executing na self.interp.rpcclt):
            ikiwa self.interp.getdebugger():
                self.interp.restart_subprocess()
            isipokua:
                self.interp.interrupt_subprocess()
        ikiwa self.reading:
            self.top.quit()  # exit the nested mainloop() kwenye readline()
        rudisha "koma"

    eleza eof_callback(self, event):
        ikiwa self.executing na sio self.reading:
            rudisha # Let the default binding (delete next char) take over
        ikiwa sio (self.text.compare("iomark", "==", "insert") na
                self.text.compare("insert", "==", "end-1c")):
            rudisha # Let the default binding (delete next char) take over
        ikiwa sio self.executing:
            self.resetoutput()
            self.close()
        isipokua:
            self.canceled = 0
            self.endoffile = 1
            self.top.quit()
        rudisha "koma"

    eleza linefeed_callback(self, event):
        # Insert a linefeed without entering anything (still autoindented)
        ikiwa self.reading:
            self.text.insert("insert", "\n")
            self.text.see("insert")
        isipokua:
            self.newline_and_indent_event(event)
        rudisha "koma"

    eleza enter_callback(self, event):
        ikiwa self.executing na sio self.reading:
            rudisha # Let the default binding (insert '\n') take over
        # If some text ni selected, recall the selection
        # (but only ikiwa this before the I/O mark)
        jaribu:
            sel = self.text.get("sel.first", "sel.last")
            ikiwa sel:
                ikiwa self.text.compare("sel.last", "<=", "iomark"):
                    self.recall(sel, event)
                    rudisha "koma"
        tatizo:
            pita
        # If we're strictly before the line containing iomark, recall
        # the current line, less a leading prompt, less leading ama
        # trailing whitespace
        ikiwa self.text.compare("insert", "<", "iomark linestart"):
            # Check ikiwa there's a relevant stdin range -- ikiwa so, use it
            prev = self.text.tag_prevrange("stdin", "insert")
            ikiwa prev na self.text.compare("insert", "<", prev[1]):
                self.recall(self.text.get(prev[0], prev[1]), event)
                rudisha "koma"
            next = self.text.tag_nextrange("stdin", "insert")
            ikiwa next na self.text.compare("insert lineend", ">=", next[0]):
                self.recall(self.text.get(next[0], next[1]), event)
                rudisha "koma"
            # No stdin mark -- just get the current line, less any prompt
            indices = self.text.tag_nextrange("console", "insert linestart")
            ikiwa indices na \
               self.text.compare(indices[0], "<=", "insert linestart"):
                self.recall(self.text.get(indices[1], "insert lineend"), event)
            isipokua:
                self.recall(self.text.get("insert linestart", "insert lineend"), event)
            rudisha "koma"
        # If we're between the beginning of the line na the iomark, i.e.
        # kwenye the prompt area, move to the end of the prompt
        ikiwa self.text.compare("insert", "<", "iomark"):
            self.text.mark_set("insert", "iomark")
        # If we're kwenye the current input na there's only whitespace
        # beyond the cursor, erase that whitespace first
        s = self.text.get("insert", "end-1c")
        ikiwa s na sio s.strip():
            self.text.delete("insert", "end-1c")
        # If we're kwenye the current input before its last line,
        # insert a newline right at the insert point
        ikiwa self.text.compare("insert", "<", "end-1c linestart"):
            self.newline_and_indent_event(event)
            rudisha "koma"
        # We're kwenye the last line; append a newline na submit it
        self.text.mark_set("insert", "end-1c")
        ikiwa self.reading:
            self.text.insert("insert", "\n")
            self.text.see("insert")
        isipokua:
            self.newline_and_indent_event(event)
        self.text.tag_add("stdin", "iomark", "end-1c")
        self.text.update_idletasks()
        ikiwa self.reading:
            self.top.quit() # Break out of recursive mainloop()
        isipokua:
            self.runit()
        rudisha "koma"

    eleza recall(self, s, event):
        # remove leading na trailing empty ama whitespace lines
        s = re.sub(r'^\s*\n', '' , s)
        s = re.sub(r'\n\s*$', '', s)
        lines = s.split('\n')
        self.text.undo_block_start()
        jaribu:
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
                kila line kwenye lines[1:]:
                    ikiwa line.startswith(orig_base_indent):
                        # replace orig base indentation ukijumuisha new indentation
                        line = new_base_indent + line[len(orig_base_indent):]
                    self.text.insert('insert', '\n'+line.rstrip())
        mwishowe:
            self.text.see("insert")
            self.text.undo_block_stop()

    eleza runit(self):
        line = self.text.get("iomark", "end-1c")
        # Strip off last newline na surrounding whitespace.
        # (To allow you to hit rudisha twice to end a statement.)
        i = len(line)
        wakati i > 0 na line[i-1] kwenye " \t":
            i = i-1
        ikiwa i > 0 na line[i-1] == "\n":
            i = i-1
        wakati i > 0 na line[i-1] kwenye " \t":
            i = i-1
        line = line[:i]
        self.interp.runsource(line)

    eleza open_stack_viewer(self, event=Tupu):
        ikiwa self.interp.rpcclt:
            rudisha self.interp.remote_stack_viewer()
        jaribu:
            sys.last_traceback
        tatizo:
            tkMessageBox.showerror("No stack trace",
                "There ni no stack trace yet.\n"
                "(sys.last_traceback ni sio defined)",
                parent=self.text)
            rudisha
        kutoka idlelib.stackviewer agiza StackBrowser
        StackBrowser(self.root, self.flist)

    eleza view_restart_mark(self, event=Tupu):
        self.text.see("iomark")
        self.text.see("restart")

    eleza restart_shell(self, event=Tupu):
        "Callback kila Run/Restart Shell Cntl-F6"
        self.interp.restart_subprocess(with_cwd=Kweli)

    eleza showprompt(self):
        self.resetoutput()
        self.console.write(self.prompt)
        self.text.mark_set("insert", "end-1c")
        self.set_line_and_column()
        self.io.reset_undo()

    eleza show_warning(self, msg):
        width = self.interp.tkconsole.width
        wrapper = TextWrapper(width=width, tabsize=8, expand_tabs=Kweli)
        wrapped_msg = '\n'.join(wrapper.wrap(msg))
        ikiwa sio wrapped_msg.endswith('\n'):
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
        jaribu:
            self.text.mark_gravity("iomark", "right")
            count = OutputWindow.write(self, s, tags, "iomark")
            self.text.mark_gravity("iomark", "left")
        tatizo:
            ashiria ###pita  # ### 11Aug07 KBK ikiwa we are expecting exceptions
                           # let's find out what they are na be specific.
        ikiwa self.canceled:
            self.canceled = 0
            ikiwa sio use_subprocess:
                ashiria KeyboardInterrupt
        rudisha count

    eleza rmenu_check_cut(self):
        jaribu:
            ikiwa self.text.compare('sel.first', '<', 'iomark'):
                rudisha 'disabled'
        tatizo TclError: # no selection, so the index 'sel.first' doesn't exist
            rudisha 'disabled'
        rudisha super().rmenu_check_cut()

    eleza rmenu_check_paste(self):
        ikiwa self.text.compare('insert','<','iomark'):
            rudisha 'disabled'
        rudisha super().rmenu_check_paste()


eleza fix_x11_paste(root):
    "Make paste replace selection on x11.  See issue #5124."
    ikiwa root._windowingsystem == 'x11':
        kila cls kwenye 'Text', 'Entry', 'Spinbox':
            root.bind_class(
                cls,
                '<<Paste>>',
                'catch {%W delete sel.first sel.last}\n' +
                        root.bind_class(cls, '<<Paste>>'))


usage_msg = """\

USAGE: idle  [-deins] [-t title] [file]*
       idle  [-dns] [-t title] (-c cmd | -r file) [arg]*
       idle  [-dns] [-t title] - [arg]*

  -h         print this help message na exit
  -n         run IDLE without a subprocess (DEPRECATED,
             see Help/IDLE Help kila details)

The following options will override the IDLE 'settings' configuration:

  -e         open an edit window
  -i         open a shell window

The following options imply -i na will open a shell:

  -c cmd     run the command kwenye a shell, ama
  -r file    run script kutoka file

  -d         enable the debugger
  -s         run $IDLESTARTUP ama $PYTHONSTARTUP before anything isipokua
  -t title   set title of shell window

A default edit window will be bypitaed when -c, -r, ama - are used.

[arg]* are pitaed to the command (-c) ama script (-r) kwenye sys.argv[1:].

Examples:

idle
        Open an edit window ama shell depending on IDLE's configuration.

idle foo.py foobar.py
        Edit the files, also open a shell ikiwa configured to start ukijumuisha shell.

idle -est "Baz" foo.py
        Run $IDLESTARTUP ama $PYTHONSTARTUP, edit foo.py, na open a shell
        window ukijumuisha the title "Baz".

idle -c "agiza sys; andika(sys.argv)" "foo"
        Open a shell window na run the command, pitaing "-c" kwenye sys.argv[0]
        na "foo" kwenye sys.argv[1].

idle -d -s -r foo.py "Hello World"
        Open a shell window, run a startup script, enable the debugger, na
        run foo.py, pitaing "foo.py" kwenye sys.argv[0] na "Hello World" in
        sys.argv[1].

echo "agiza sys; andika(sys.argv)" | idle - "foobar"
        Open a shell window, run the script piped in, pitaing '' kwenye sys.argv[0]
        na "foobar" kwenye sys.argv[1].
"""

eleza main():
    agiza getopt
    kutoka platform agiza system
    kutoka idlelib agiza testing  # bool value
    kutoka idlelib agiza macosx

    global flist, root, use_subprocess

    capture_warnings(Kweli)
    use_subprocess = Kweli
    enable_shell = Uongo
    enable_edit = Uongo
    debug = Uongo
    cmd = Tupu
    script = Tupu
    startup = Uongo
    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], "c:deihnr:st:")
    tatizo getopt.error kama msg:
        andika("Error: %s\n%s" % (msg, usage_msg), file=sys.stderr)
        sys.exit(2)
    kila o, a kwenye opts:
        ikiwa o == '-c':
            cmd = a
            enable_shell = Kweli
        ikiwa o == '-d':
            debug = Kweli
            enable_shell = Kweli
        ikiwa o == '-e':
            enable_edit = Kweli
        ikiwa o == '-h':
            sys.stdout.write(usage_msg)
            sys.exit()
        ikiwa o == '-i':
            enable_shell = Kweli
        ikiwa o == '-n':
            andika(" Warning: running IDLE without a subprocess ni deprecated.",
                  file=sys.stderr)
            use_subprocess = Uongo
        ikiwa o == '-r':
            script = a
            ikiwa os.path.isfile(script):
                pita
            isipokua:
                andika("No script file: ", script)
                sys.exit()
            enable_shell = Kweli
        ikiwa o == '-s':
            startup = Kweli
            enable_shell = Kweli
        ikiwa o == '-t':
            PyShell.shell_title = a
            enable_shell = Kweli
    ikiwa args na args[0] == '-':
        cmd = sys.stdin.read()
        enable_shell = Kweli
    # process sys.argv na sys.path:
    kila i kwenye range(len(sys.path)):
        sys.path[i] = os.path.abspath(sys.path[i])
    ikiwa args na args[0] == '-':
        sys.argv = [''] + args[1:]
    lasivyo cmd:
        sys.argv = ['-c'] + args
    lasivyo script:
        sys.argv = [script] + args
    lasivyo args:
        enable_edit = Kweli
        pathx = []
        kila filename kwenye args:
            pathx.append(os.path.dirname(filename))
        kila dir kwenye pathx:
            dir = os.path.abspath(dir)
            ikiwa sio dir kwenye sys.path:
                sys.path.insert(0, dir)
    isipokua:
        dir = os.getcwd()
        ikiwa dir haiko kwenye sys.path:
            sys.path.insert(0, dir)
    # check the IDLE settings configuration (but command line overrides)
    edit_start = idleConf.GetOption('main', 'General',
                                    'editor-on-startup', type='bool')
    enable_edit = enable_edit ama edit_start
    enable_shell = enable_shell ama sio enable_edit

    # Setup root.  Don't koma user code run kwenye IDLE process.
    # Don't change environment when testing.
    ikiwa use_subprocess na sio testing:
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
    lasivyo sio macosx.isAquaTk():
        ext = '.png' ikiwa TkVersion >= 8.6 isipokua '.gif'
        iconfiles = [os.path.join(icondir, 'idle_%d%s' % (size, ext))
                     kila size kwenye (16, 32, 48)]
        icons = [PhotoImage(master=root, file=iconfile)
                 kila iconfile kwenye iconfiles]
        root.wm_iconphoto(Kweli, *icons)

    # start editor and/or shell windows:
    fixwordkomas(root)
    fix_x11_paste(root)
    flist = PyShellFileList(root)
    macosx.setupApp(root, flist)

    ikiwa enable_edit:
        ikiwa sio (cmd ama script):
            kila filename kwenye args[:]:
                ikiwa flist.open(filename) ni Tupu:
                    # filename ni a directory actually, disconsider it
                    args.remove(filename)
            ikiwa sio args:
                flist.new()

    ikiwa enable_shell:
        shell = flist.open_shell()
        ikiwa sio shell:
            rudisha # couldn't open shell
        ikiwa macosx.isAquaTk() na flist.dict:
            # On OSX: when the user has double-clicked on a file that causes
            # IDLE to be launched the shell window will open just kwenye front of
            # the file she wants to see. Lower the interpreter window when
            # there are open files.
            shell.top.lower()
    isipokua:
        shell = flist.pyshell

    # Handle remaining options. If any of these are set, enable_shell
    # was set also, so shell must be true to reach here.
    ikiwa debug:
        shell.open_debugger()
    ikiwa startup:
        filename = os.environ.get("IDLESTARTUP") ama \
                   os.environ.get("PYTHONSTARTUP")
        ikiwa filename na os.path.isfile(filename):
            shell.interp.execfile(filename)
    ikiwa cmd ama script:
        shell.interp.runcommand("""ikiwa 1:
            agiza sys kama _sys
            _sys.argv = %r
            toa _sys
            \n""" % (sys.argv,))
        ikiwa cmd:
            shell.interp.execsource(cmd)
        lasivyo script:
            shell.interp.prepend_syspath(script)
            shell.interp.execfile(script)
    lasivyo shell:
        # If there ni a shell window na no cmd ama script kwenye progress,
        # check kila problematic issues na print warning message(s) in
        # the IDLE shell window; this ni less intrusive than always
        # opening a separate window.

        # Warn ikiwa using a problematic OS X Tk version.
        tkversionwarning = macosx.tkVersionWarning(root)
        ikiwa tkversionwarning:
            shell.show_warning(tkversionwarning)

        # Warn ikiwa the "Prefer tabs when opening documents" system
        # preference ni set to "Always".
        prefer_tabs_preference_warning = macosx.preferTabsPreferenceWarning()
        ikiwa prefer_tabs_preference_warning:
            shell.show_warning(prefer_tabs_preference_warning)

    wakati flist.inversedict:  # keep IDLE running wakati files are open.
        root.mainloop()
    root.destroy()
    capture_warnings(Uongo)

ikiwa __name__ == "__main__":
    main()

capture_warnings(Uongo)  # Make sure turned off; see issue 18081
