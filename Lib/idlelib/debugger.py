agiza bdb
agiza os

kutoka tkinter agiza *
kutoka tkinter.ttk agiza Frame, Scrollbar

kutoka idlelib agiza macosx
kutoka idlelib.scrolledlist agiza ScrolledList
kutoka idlelib.window agiza ListedToplevel


kundi Idb(bdb.Bdb):

    eleza __init__(self, gui):
        self.gui = gui  # An instance of Debugger ama proxy of remote.
        bdb.Bdb.__init__(self)

    eleza user_line(self, frame):
        ikiwa self.in_rpc_code(frame):
            self.set_step()
            rudisha
        message = self.__frame2message(frame)
        jaribu:
            self.gui.interaction(message, frame)
        tatizo TclError:  # When closing debugger window ukijumuisha [x] kwenye 3.x
            pita

    eleza user_exception(self, frame, info):
        ikiwa self.in_rpc_code(frame):
            self.set_step()
            rudisha
        message = self.__frame2message(frame)
        self.gui.interaction(message, frame, info)

    eleza in_rpc_code(self, frame):
        ikiwa frame.f_code.co_filename.count('rpc.py'):
            rudisha Kweli
        isipokua:
            prev_frame = frame.f_back
            prev_name = prev_frame.f_code.co_filename
            ikiwa 'idlelib' kwenye prev_name na 'debugger' kwenye prev_name:
                # catch both idlelib/debugger.py na idlelib/debugger_r.py
                # on both Posix na Windows
                rudisha Uongo
            rudisha self.in_rpc_code(prev_frame)

    eleza __frame2message(self, frame):
        code = frame.f_code
        filename = code.co_filename
        lineno = frame.f_lineno
        basename = os.path.basename(filename)
        message = "%s:%s" % (basename, lineno)
        ikiwa code.co_name != "?":
            message = "%s: %s()" % (message, code.co_name)
        rudisha message


kundi Debugger:

    vstack = vsource = vlocals = vglobals = Tupu

    eleza __init__(self, pyshell, idb=Tupu):
        ikiwa idb ni Tupu:
            idb = Idb(self)
        self.pyshell = pyshell
        self.idb = idb  # If pitaed, a proxy of remote instance.
        self.frame = Tupu
        self.make_gui()
        self.interacting = 0
        self.nesting_level = 0

    eleza run(self, *args):
        # Deal ukijumuisha the scenario where we've already got a program running
        # kwenye the debugger na we want to start another. If that ni the case,
        # our second 'run' was invoked kutoka an event dispatched sio from
        # the main event loop, but kutoka the nested event loop kwenye 'interaction'
        # below. So our stack looks something like this:
        #       outer main event loop
        #         run()
        #           <running program ukijumuisha traces>
        #             callback to debugger's interaction()
        #               nested event loop
        #                 run() kila second command
        #
        # This kind of nesting of event loops causes all kinds of problems
        # (see e.g. issue #24455) especially when dealing ukijumuisha running kama a
        # subprocess, where there's all kinds of extra stuff happening in
        # there - insert a traceback.print_stack() to check it out.
        #
        # By this point, we've already called restart_subprocess() in
        # ScriptBinding. However, we also need to unwind the stack back to
        # that outer event loop.  To accomplish this, we:
        #   - rudisha immediately kutoka the nested run()
        #   - abort_loop ensures the nested event loop will terminate
        #   - the debugger's interaction routine completes normally
        #   - the restart_subprocess() will have taken care of stopping
        #     the running program, which will also let the outer run complete
        #
        # That leaves us back at the outer main event loop, at which point our
        # after event can fire, na we'll come back to this routine ukijumuisha a
        # clean stack.
        ikiwa self.nesting_level > 0:
            self.abort_loop()
            self.root.after(100, lambda: self.run(*args))
            rudisha
        jaribu:
            self.interacting = 1
            rudisha self.idb.run(*args)
        mwishowe:
            self.interacting = 0

    eleza close(self, event=Tupu):
        jaribu:
            self.quit()
        tatizo Exception:
            pita
        ikiwa self.interacting:
            self.top.bell()
            rudisha
        ikiwa self.stackviewer:
            self.stackviewer.close(); self.stackviewer = Tupu
        # Clean up pyshell ikiwa user clicked debugger control close widget.
        # (Causes a harmless extra cycle through close_debugger() ikiwa user
        # toggled debugger kutoka pyshell Debug menu)
        self.pyshell.close_debugger()
        # Now close the debugger control window....
        self.top.destroy()

    eleza make_gui(self):
        pyshell = self.pyshell
        self.flist = pyshell.flist
        self.root = root = pyshell.root
        self.top = top = ListedToplevel(root)
        self.top.wm_title("Debug Control")
        self.top.wm_iconname("Debug")
        top.wm_protocol("WM_DELETE_WINDOW", self.close)
        self.top.bind("<Escape>", self.close)
        #
        self.bframe = bframe = Frame(top)
        self.bframe.pack(anchor="w")
        self.buttons = bl = []
        #
        self.bcont = b = Button(bframe, text="Go", command=self.cont)
        bl.append(b)
        self.bstep = b = Button(bframe, text="Step", command=self.step)
        bl.append(b)
        self.bnext = b = Button(bframe, text="Over", command=self.next)
        bl.append(b)
        self.bret = b = Button(bframe, text="Out", command=self.ret)
        bl.append(b)
        self.bret = b = Button(bframe, text="Quit", command=self.quit)
        bl.append(b)
        #
        kila b kwenye bl:
            b.configure(state="disabled")
            b.pack(side="left")
        #
        self.cframe = cframe = Frame(bframe)
        self.cframe.pack(side="left")
        #
        ikiwa sio self.vstack:
            self.__class__.vstack = BooleanVar(top)
            self.vstack.set(1)
        self.bstack = Checkbutton(cframe,
            text="Stack", command=self.show_stack, variable=self.vstack)
        self.bstack.grid(row=0, column=0)
        ikiwa sio self.vsource:
            self.__class__.vsource = BooleanVar(top)
        self.bsource = Checkbutton(cframe,
            text="Source", command=self.show_source, variable=self.vsource)
        self.bsource.grid(row=0, column=1)
        ikiwa sio self.vlocals:
            self.__class__.vlocals = BooleanVar(top)
            self.vlocals.set(1)
        self.blocals = Checkbutton(cframe,
            text="Locals", command=self.show_locals, variable=self.vlocals)
        self.blocals.grid(row=1, column=0)
        ikiwa sio self.vglobals:
            self.__class__.vglobals = BooleanVar(top)
        self.bglobals = Checkbutton(cframe,
            text="Globals", command=self.show_globals, variable=self.vglobals)
        self.bglobals.grid(row=1, column=1)
        #
        self.status = Label(top, anchor="w")
        self.status.pack(anchor="w")
        self.error = Label(top, anchor="w")
        self.error.pack(anchor="w", fill="x")
        self.errorbg = self.error.cget("background")
        #
        self.fstack = Frame(top, height=1)
        self.fstack.pack(expand=1, fill="both")
        self.flocals = Frame(top)
        self.flocals.pack(expand=1, fill="both")
        self.fglobals = Frame(top, height=1)
        self.fglobals.pack(expand=1, fill="both")
        #
        ikiwa self.vstack.get():
            self.show_stack()
        ikiwa self.vlocals.get():
            self.show_locals()
        ikiwa self.vglobals.get():
            self.show_globals()

    eleza interaction(self, message, frame, info=Tupu):
        self.frame = frame
        self.status.configure(text=message)
        #
        ikiwa info:
            type, value, tb = info
            jaribu:
                m1 = type.__name__
            tatizo AttributeError:
                m1 = "%s" % str(type)
            ikiwa value ni sio Tupu:
                jaribu:
                    m1 = "%s: %s" % (m1, str(value))
                tatizo:
                    pita
            bg = "yellow"
        isipokua:
            m1 = ""
            tb = Tupu
            bg = self.errorbg
        self.error.configure(text=m1, background=bg)
        #
        sv = self.stackviewer
        ikiwa sv:
            stack, i = self.idb.get_stack(self.frame, tb)
            sv.load_stack(stack, i)
        #
        self.show_variables(1)
        #
        ikiwa self.vsource.get():
            self.sync_source_line()
        #
        kila b kwenye self.buttons:
            b.configure(state="normal")
        #
        self.top.wakeup()
        # Nested main loop: Tkinter's main loop ni sio reentrant, so use
        # Tcl's vwait facility, which reenters the event loop until an
        # event handler sets the variable we're waiting on
        self.nesting_level += 1
        self.root.tk.call('vwait', '::idledebugwait')
        self.nesting_level -= 1
        #
        kila b kwenye self.buttons:
            b.configure(state="disabled")
        self.status.configure(text="")
        self.error.configure(text="", background=self.errorbg)
        self.frame = Tupu

    eleza sync_source_line(self):
        frame = self.frame
        ikiwa sio frame:
            rudisha
        filename, lineno = self.__frame2fileline(frame)
        ikiwa filename[:1] + filename[-1:] != "<>" na os.path.exists(filename):
            self.flist.gotofileline(filename, lineno)

    eleza __frame2fileline(self, frame):
        code = frame.f_code
        filename = code.co_filename
        lineno = frame.f_lineno
        rudisha filename, lineno

    eleza cont(self):
        self.idb.set_endelea()
        self.abort_loop()

    eleza step(self):
        self.idb.set_step()
        self.abort_loop()

    eleza next(self):
        self.idb.set_next(self.frame)
        self.abort_loop()

    eleza ret(self):
        self.idb.set_return(self.frame)
        self.abort_loop()

    eleza quit(self):
        self.idb.set_quit()
        self.abort_loop()

    eleza abort_loop(self):
        self.root.tk.call('set', '::idledebugwait', '1')

    stackviewer = Tupu

    eleza show_stack(self):
        ikiwa sio self.stackviewer na self.vstack.get():
            self.stackviewer = sv = StackViewer(self.fstack, self.flist, self)
            ikiwa self.frame:
                stack, i = self.idb.get_stack(self.frame, Tupu)
                sv.load_stack(stack, i)
        isipokua:
            sv = self.stackviewer
            ikiwa sv na sio self.vstack.get():
                self.stackviewer = Tupu
                sv.close()
            self.fstack['height'] = 1

    eleza show_source(self):
        ikiwa self.vsource.get():
            self.sync_source_line()

    eleza show_frame(self, stackitem):
        self.frame = stackitem[0]  # lineno ni stackitem[1]
        self.show_variables()

    localsviewer = Tupu
    globalsviewer = Tupu

    eleza show_locals(self):
        lv = self.localsviewer
        ikiwa self.vlocals.get():
            ikiwa sio lv:
                self.localsviewer = NamespaceViewer(self.flocals, "Locals")
        isipokua:
            ikiwa lv:
                self.localsviewer = Tupu
                lv.close()
                self.flocals['height'] = 1
        self.show_variables()

    eleza show_globals(self):
        gv = self.globalsviewer
        ikiwa self.vglobals.get():
            ikiwa sio gv:
                self.globalsviewer = NamespaceViewer(self.fglobals, "Globals")
        isipokua:
            ikiwa gv:
                self.globalsviewer = Tupu
                gv.close()
                self.fglobals['height'] = 1
        self.show_variables()

    eleza show_variables(self, force=0):
        lv = self.localsviewer
        gv = self.globalsviewer
        frame = self.frame
        ikiwa sio frame:
            ldict = gdict = Tupu
        isipokua:
            ldict = frame.f_locals
            gdict = frame.f_globals
            ikiwa lv na gv na ldict ni gdict:
                ldict = Tupu
        ikiwa lv:
            lv.load_dict(ldict, force, self.pyshell.interp.rpcclt)
        ikiwa gv:
            gv.load_dict(gdict, force, self.pyshell.interp.rpcclt)

    eleza set_komapoint_here(self, filename, lineno):
        self.idb.set_koma(filename, lineno)

    eleza clear_komapoint_here(self, filename, lineno):
        self.idb.clear_koma(filename, lineno)

    eleza clear_file_komas(self, filename):
        self.idb.clear_all_file_komas(filename)

    eleza load_komapoints(self):
        "Load PyShellEditorWindow komapoints into subprocess debugger"
        kila editwin kwenye self.pyshell.flist.inversedict:
            filename = editwin.io.filename
            jaribu:
                kila lineno kwenye editwin.komapoints:
                    self.set_komapoint_here(filename, lineno)
            tatizo AttributeError:
                endelea

kundi StackViewer(ScrolledList):

    eleza __init__(self, master, flist, gui):
        ikiwa macosx.isAquaTk():
            # At least on ukijumuisha the stock AquaTk version on OSX 10.4 you'll
            # get a shaking GUI that eventually kills IDLE ikiwa the width
            # argument ni specified.
            ScrolledList.__init__(self, master)
        isipokua:
            ScrolledList.__init__(self, master, width=80)
        self.flist = flist
        self.gui = gui
        self.stack = []

    eleza load_stack(self, stack, index=Tupu):
        self.stack = stack
        self.clear()
        kila i kwenye range(len(stack)):
            frame, lineno = stack[i]
            jaribu:
                modname = frame.f_globals["__name__"]
            tatizo:
                modname = "?"
            code = frame.f_code
            filename = code.co_filename
            funcname = code.co_name
            agiza linecache
            sourceline = linecache.getline(filename, lineno)
            sourceline = sourceline.strip()
            ikiwa funcname kwenye ("?", "", Tupu):
                item = "%s, line %d: %s" % (modname, lineno, sourceline)
            isipokua:
                item = "%s.%s(), line %d: %s" % (modname, funcname,
                                                 lineno, sourceline)
            ikiwa i == index:
                item = "> " + item
            self.append(item)
        ikiwa index ni sio Tupu:
            self.select(index)

    eleza popup_event(self, event):
        "override base method"
        ikiwa self.stack:
            rudisha ScrolledList.popup_event(self, event)

    eleza fill_menu(self):
        "override base method"
        menu = self.menu
        menu.add_command(label="Go to source line",
                         command=self.goto_source_line)
        menu.add_command(label="Show stack frame",
                         command=self.show_stack_frame)

    eleza on_select(self, index):
        "override base method"
        ikiwa 0 <= index < len(self.stack):
            self.gui.show_frame(self.stack[index])

    eleza on_double(self, index):
        "override base method"
        self.show_source(index)

    eleza goto_source_line(self):
        index = self.listbox.index("active")
        self.show_source(index)

    eleza show_stack_frame(self):
        index = self.listbox.index("active")
        ikiwa 0 <= index < len(self.stack):
            self.gui.show_frame(self.stack[index])

    eleza show_source(self, index):
        ikiwa sio (0 <= index < len(self.stack)):
            rudisha
        frame, lineno = self.stack[index]
        code = frame.f_code
        filename = code.co_filename
        ikiwa os.path.isfile(filename):
            edit = self.flist.open(filename)
            ikiwa edit:
                edit.gotoline(lineno)


kundi NamespaceViewer:

    eleza __init__(self, master, title, dict=Tupu):
        width = 0
        height = 40
        ikiwa dict:
            height = 20*len(dict) # XXX 20 == observed height of Entry widget
        self.master = master
        self.title = title
        agiza reprlib
        self.repr = reprlib.Repr()
        self.repr.maxstring = 60
        self.repr.maxother = 60
        self.frame = frame = Frame(master)
        self.frame.pack(expand=1, fill="both")
        self.label = Label(frame, text=title, borderwidth=2, relief="groove")
        self.label.pack(fill="x")
        self.vbar = vbar = Scrollbar(frame, name="vbar")
        vbar.pack(side="right", fill="y")
        self.canvas = canvas = Canvas(frame,
                                      height=min(300, max(40, height)),
                                      scrollregion=(0, 0, width, height))
        canvas.pack(side="left", fill="both", expand=1)
        vbar["command"] = canvas.yview
        canvas["yscrollcommand"] = vbar.set
        self.subframe = subframe = Frame(canvas)
        self.sfid = canvas.create_window(0, 0, window=subframe, anchor="nw")
        self.load_dict(dict)

    dict = -1

    eleza load_dict(self, dict, force=0, rpc_client=Tupu):
        ikiwa dict ni self.dict na sio force:
            rudisha
        subframe = self.subframe
        frame = self.frame
        kila c kwenye list(subframe.children.values()):
            c.destroy()
        self.dict = Tupu
        ikiwa sio dict:
            l = Label(subframe, text="Tupu")
            l.grid(row=0, column=0)
        isipokua:
            #names = sorted(dict)
            ###
            # Because of (temporary) limitations on the dict_keys type (sio yet
            # public ama pickleable), have the subprocess to send a list of
            # keys, sio a dict_keys object.  sorted() will take a dict_keys
            # (no subprocess) ama a list.
            #
            # There ni also an obscure bug kwenye sorted(dict) where the
            # interpreter gets into a loop requesting non-existing dict[0],
            # dict[1], dict[2], etc kutoka the debugger_r.DictProxy.
            ###
            keys_list = dict.keys()
            names = sorted(keys_list)
            ###
            row = 0
            kila name kwenye names:
                value = dict[name]
                svalue = self.repr.repr(value) # repr(value)
                # Strip extra quotes caused by calling repr on the (already)
                # repr'd value sent across the RPC interface:
                ikiwa rpc_client:
                    svalue = svalue[1:-1]
                l = Label(subframe, text=name)
                l.grid(row=row, column=0, sticky="nw")
                l = Entry(subframe, width=0, borderwidth=0)
                l.insert(0, svalue)
                l.grid(row=row, column=1, sticky="nw")
                row = row+1
        self.dict = dict
        # XXX Could we use a <Configure> callback kila the following?
        subframe.update_idletasks() # Alas!
        width = subframe.winfo_reqwidth()
        height = subframe.winfo_reqheight()
        canvas = self.canvas
        self.canvas["scrollregion"] = (0, 0, width, height)
        ikiwa height > 300:
            canvas["height"] = 300
            frame.pack(expand=1)
        isipokua:
            canvas["height"] = height
            frame.pack(expand=0)

    eleza close(self):
        self.frame.destroy()

ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_debugger', verbosity=2, exit=Uongo)

# TODO: htest?
